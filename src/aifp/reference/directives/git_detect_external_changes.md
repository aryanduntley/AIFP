# Directive: git_detect_external_changes

**Type**: Git
**Level**: 2
**Parent Directive**: aifp_status
**Priority**: HIGH - Critical for session synchronization

---

## Purpose

The `git_detect_external_changes` directive detects code modifications made **outside of AIFP sessions** by comparing the current Git HEAD commit hash with the `project.last_known_git_hash` stored in the database. This enables AIFP to:

- **Detect manual edits**: User edited files directly (outside AI session)
- **Detect other tool changes**: IDE refactorings, linters, formatters
- **Detect team collaboration**: Other developers pushed changes
- **Synchronize project state**: Update database to reflect external changes
- **Provide impact analysis**: Show which themes, flows, and functions affected

This directive is **essential for reliable AI assistance** because:
- AI needs to know current code state before making suggestions
- Database (`project.db`) must stay synchronized with actual files
- Theme and flow organization may need updates after external changes
- Function metadata (purity, dependencies) may be outdated

The detection workflow:
1. **Compare Git hashes** - Current HEAD vs stored hash
2. **If different**: Analyze changes with `git diff`
3. **Build impact report** - Which files, themes, flows, functions affected
4. **Present to user** - Show what changed with recommendations
5. **Update database** - Sync hash and timestamp

**Important**: This directive is automatically called by `aifp_status` at session start to ensure AI has current context.

---

## When to Apply

This directive applies when:
- **Called by `aifp_status`** - At start of every AI session
- **Session boot** - AI needs to sync with current code state
- **User says "continue" or "resume"** - Resuming previous work
- **Manual sync requested** - User asks "check for external changes"
- **After Git operations** - Pull, fetch, checkout, merge from external source

---

## Workflow

### Trunk: get_last_known_hash_from_project_table

Retrieves the last known Git commit hash from `project.db`.

**Steps**:
1. **Query database** - `SELECT last_known_git_hash FROM project WHERE id=1`
2. **Get current Git hash** - Run `git rev-parse HEAD`
3. **Compare hashes** - Are they the same?
4. **Route to appropriate action** - Based on comparison result

### Branches

**Branch 1: If no_last_hash**
- **Then**: `store_current_hash`
- **Details**: First run, no previous hash stored
  - Action: This is first run or hash was never initialized
  - Update: `project.last_known_git_hash = current_hash`
  - Update: `project.last_git_sync = CURRENT_TIMESTAMP`
  - Message: "Git hash initialized, no external changes to detect"
- **Result**: Hash stored for future comparisons

**Branch 2: If hash_matches**
- **Then**: `return_no_changes`
- **Details**: No external changes detected
  - Message: "No external changes detected"
  - Update: `project.last_git_sync = CURRENT_TIMESTAMP` (refresh sync time)
  - Return: No action needed
- **Result**: Session can proceed with current state

**Branch 3: If hash_differs**
- **Then**: `analyze_changes`
- **Details**: External changes detected, analyze impact
  - Actions:
    1. **git diff --name-only**: Get list of changed files
       ```bash
       git diff --name-only {last_hash}..HEAD
       ```
    2. **Query file themes**: For each changed file, query database
       ```sql
       SELECT t.name, f.name FROM themes t
       JOIN flow_themes ft ON t.id = ft.theme_id
       JOIN file_flows ff ON ft.flow_id = ff.flow_id
       JOIN files f ON ff.file_id = f.id
       WHERE f.path IN (changed_files)
       ```
    3. **Query file functions**: Get affected functions
       ```sql
       SELECT name, purpose, purity_level FROM functions
       WHERE file_id IN (SELECT id FROM files WHERE path IN (changed_files))
       ```
    4. **Build impact report**: Structure the analysis
       ```python
       {
         "changed_files": ["src/calc.py", "src/utils.py"],
         "affected_themes": ["Math Operations", "Utility Functions"],
         "affected_functions": [
           {"name": "calculate", "file": "src/calc.py", "purity": "pure"},
           {"name": "format", "file": "src/utils.py", "purity": "pure"}
         ],
         "commit_range": "abc123..def456",
         "commits_behind": 5
       }
       ```
- **Result**: Detailed change analysis ready

**Branch 4: If changes_analyzed**
- **Then**: `present_to_user`
- **Details**: Show changes to user with context
  - Show:
    - List of changed files
    - Affected themes and flows
    - Functions that changed
    - Commit range (how many commits behind)
    - Git log summary if helpful
  - Format as clear, actionable report
- **Result**: User informed of external changes

**Branch 5: If user_acknowledged**
- **Then**: `update_project_table`
- **Details**: Update database with new hash
  - Update: `project.last_known_git_hash = current_hash`
  - Update: `project.last_git_sync = CURRENT_TIMESTAMP`
  - Log to notes table if significant changes
- **Result**: Database synchronized with Git

**Branch 6: If organizational_impact**
- **Then**: `suggest_reconciliation`
- **Details**: Suggest updating themes/flows if affected
  - Actions:
    - **update_themes**: If themes structure changed
    - **update_flows**: If flow dependencies changed
  - Suggest: "Run `project_update_db` to refresh function metadata"
- **Result**: Recommendations provided for sync

**Fallback**: `log_warning`
- **Details**: Detection failed but non-critical
  - Message: "External changes detected but analysis failed"
  - Fallback: Show changed files only (no impact analysis)
  - Log warning to notes table
  - Continue with best-effort synchronization
- **Result**: Graceful degradation

---

## Examples

### ✅ Compliant Usage

**External Changes Detected (Manual Edit):**
```bash
# User manually edited src/calc.py outside AIFP
# Next AI session starts...

# Workflow:
# 1. Query: SELECT last_known_git_hash FROM project → "abc123"
# 2. Run: git rev-parse HEAD → "def456"
# 3. Hashes differ! Analyze changes
# 4. Run: git diff --name-only abc123..HEAD
#    → src/calc.py
# 5. Query: SELECT themes FROM ... WHERE file='src/calc.py'
#    → Theme: "Math Operations"
# 6. Query: SELECT functions FROM ... WHERE file='src/calc.py'
#    → Functions: calculate_total, format_result
# 7. Run: git log --oneline abc123..HEAD
#    → def456 Fixed calculation bug
#      ghi789 Added error handling
#
# Present to user:
# ⚠️  External changes detected:
#
# Changed files (2 commits behind):
#   • src/calc.py
#
# Affected themes:
#   • Math Operations
#
# Affected functions:
#   • calculate_total (pure)
#   • format_result (pure)
#
# Commits:
#   def456 - Fixed calculation bug
#   ghi789 - Added error handling
#
# Recommendations:
#   • Review function metadata for accuracy
#
# 8. UPDATE project SET last_known_git_hash='def456', last_git_sync=now
```

---

**No External Changes:**
```bash
# AI session starts, no changes made externally

# Workflow:
# 1. Query: SELECT last_known_git_hash FROM project → "abc123"
# 2. Run: git rev-parse HEAD → "abc123"
# 3. Hashes match! No changes
# 4. UPDATE project SET last_git_sync=CURRENT_TIMESTAMP
#
# Result:
# ✅ No external changes detected
# Session proceeds normally
```

---

### ❌ Non-Compliant Usage

**Not Checking on Session Start:**
```python
# ❌ AI starts making suggestions without checking
# User manually changed code
# AI suggestions based on outdated state
```

**Why Non-Compliant**:
- AI operates on stale state
- Suggestions may conflict with manual changes
- Database out of sync

**Corrected:**
```python
# ✅ Always check first
if aifp_status_called:
    git_detect_external_changes()  # Called automatically
    # Now safe to proceed with current state
```

---

**Ignoring Impact Analysis:**
```python
# ❌ Just updating hash without analyzing
project.last_known_git_hash = current_hash
# No impact analysis, user unaware of changes
```

**Why Non-Compliant**:
- User not informed of what changed
- Can't assess impact on themes/flows
- Misses opportunity to update metadata

**Corrected:**
```python
# ✅ Full analysis
if hash_differs:
    impact = analyze_changes(last_hash, current_hash)
    present_to_user(impact)
    update_hash()
```

---

## Edge Cases

### Edge Case 1: Many Commits Behind (Large Divergence)

**Issue**: Stored hash is many commits behind HEAD

**Handling**:
```python
# Count commits
commits_behind = run_command("git rev-list --count {last_hash}..HEAD")

if commits_behind > 20:
    # Too many changes to show individually
    return {
        "message": f"Repository is {commits_behind} commits ahead",
        "suggestion": "Large divergence detected. Consider:",
        "options": [
            "Review git log manually",
            "Accept changes and continue",
            "Run full project rescan"
        ]
    }
```

**Directive Action**: Present summary, don't overwhelm with details.

---

### Edge Case 2: Git History Rewritten (Force Push)

**Issue**: Stored hash doesn't exist in current history

**Handling**:
```bash
# Try to find stored hash
if ! git cat-file -e "$LAST_HASH" 2>/dev/null; then
    # Hash doesn't exist (history rewritten)
    echo "Git history rewritten or rebased"

    # Options:
    # 1. Re-initialize with current hash
    # 2. Warn user about potential data loss
    # 3. Suggest reviewing changes manually
fi
```

**Directive Action**: Re-initialize hash, warn user, suggest manual review.

---

### Edge Case 3: Detached HEAD State

**Issue**: Not on a branch, HEAD is detached

**Handling**:
```bash
# Check if HEAD is detached
BRANCH=$(git symbolic-ref -q HEAD)
if [ -z "$BRANCH" ]; then
    # Detached HEAD
    echo "Detached HEAD state detected"
    echo "Current commit: $(git rev-parse HEAD)"

    # Still track changes, but warn user
fi
```

**Directive Action**: Proceed with detection, warn about detached state.

---

### Edge Case 4: Database Query Fails (Theme Impact Unknown)

**Issue**: Can't query themes/functions for impact analysis

**Handling**:
```python
try:
    themes = query_themes_for_files(changed_files)
    functions = query_functions_for_files(changed_files)
except DatabaseError:
    # Database query failed
    # Fallback: Just show changed files
    return {
        "changed_files": changed_files,
        "affected_themes": "Unknown (database query failed)",
        "affected_functions": "Unknown",
        "recommendation": "Run project_update_db to refresh metadata"
    }
```

**Directive Action**: Graceful degradation, show what's available.

---

## Related Directives

- **Called By**:
  - `aifp_status` - At session start for synchronization
  - `git_sync_state` - When hash mismatch detected
- **Calls**:
  - Git CLI commands via helpers
  - Database query helpers for impact analysis
- **Triggers**:
  - `project_update_db` - If metadata needs refresh
- **Related**:
  - `git_init` - Initializes hash tracking
  - `git_merge_branch` - Creates commits that trigger detection

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`project`**: Updates `last_known_git_hash` and `last_git_sync` after detection
- **`notes`**: Logs significant external changes with `note_type = 'external_change'`

**Note**: This directive primarily **reads** from files, functions, themes, flows tables for impact analysis.

---

## Testing

How to verify this directive is working:

1. **No changes** → Reports clean
   ```python
   result = git_detect_external_changes("/path/to/project")
   assert result["changes_detected"] == False
   ```

2. **Manual edit** → Detects change
   ```bash
   # Edit file manually
   echo "# comment" >> src/calc.py
   git add src/calc.py && git commit -m "Manual edit"

   result = git_detect_external_changes("/path/to/project")
   assert result["changes_detected"] == True
   assert "src/calc.py" in result["changed_files"]
   ```

3. **Impact analysis** → Shows affected themes
   ```python
   result = git_detect_external_changes("/path/to/project")
   assert len(result["affected_themes"]) > 0
   assert len(result["affected_functions"]) > 0
   ```

---

## Common Mistakes

- ❌ **Not calling at session start** - AI operates on stale state
- ❌ **Ignoring impact analysis** - User unaware of change scope
- ❌ **Not updating hash after detection** - Same changes detected repeatedly
- ❌ **Assuming Git always available** - Handle Git command failures
- ❌ **Not handling large divergence** - Overwhelming user with too many changes

---

## Roadblocks and Resolutions

### Roadblock 1: git_hash_corrupted
**Issue**: Stored hash is invalid or doesn't exist in history
**Resolution**: Re-initialize `project.last_known_git_hash` from current Git HEAD

### Roadblock 2: too_many_changes
**Issue**: Repository is many commits ahead (large divergence)
**Resolution**: Present summary instead of full diff, offer detailed analysis option

### Roadblock 3: theme_analysis_fails
**Issue**: Database queries fail or incomplete
**Resolution**: Skip theme impact, just show changed files, suggest running `project_update_db`

---

## References

None
---

*Part of AIFP v1.0 - Git integration directive for external change detection*

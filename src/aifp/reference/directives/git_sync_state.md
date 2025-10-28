# Directive: git_sync_state

**Type**: Git
**Level**: 2
**Parent Directive**: aifp_status
**Priority**: HIGH - Critical for change detection

---

## Purpose

The `git_sync_state` directive **synchronizes the current Git commit hash** with the `project.last_known_git_hash` field in the database, enabling AIFP to detect when code has been modified outside of AIFP sessions. This directive is the **synchronization checkpoint** that maintains the connection between Git's version control and AIFP's database-tracked project state.

This directive is **essential for external change detection** because:
- **Baseline tracking**: Stores current Git state for future comparison
- **Enables git_detect_external_changes**: Without synced hash, change detection doesn't work
- **Session synchronization**: Called at session boot to establish current state
- **Post-operation updates**: Updates hash after commits, merges, and branch operations
- **Lightweight**: Fast operation (~1-2ms) using simple Git commands

The sync workflow is intentionally **simple and focused**:
1. **Get current Git hash** - Query `git rev-parse HEAD`
2. **Query stored hash** - Read `project.last_known_git_hash` from database
3. **Compare hashes** - Are they the same or different?
4. **If different** - Trigger `git_detect_external_changes` for analysis
5. **Update database** - Store current hash and sync timestamp

**Design Decision**: AIFP does **NOT duplicate Git state** in the database (e.g., no separate `git_state` table tracking current branch). Current Git state is always queried directly from Git using fast commands like:
- Current branch: `git branch --show-current` (~1ms)
- Current hash: `git rev-parse HEAD` (~1ms)
- Git status: `git status --porcelain` (~5ms)

This avoids data duplication and potential inconsistencies. Only the **last known hash** is stored for external change detection.

---

## When to Apply

This directive applies when:
- **Called by `aifp_status`** - At session boot/initialization
- **After Git commits** - When AIFP creates commits
- **After branch operations** - After checkout, merge, rebase
- **After pull/fetch** - When remote changes are integrated
- **Manual sync requested** - User asks to refresh Git state
- **Periodic health check** - Automated sync during long sessions

---

## Workflow

### Trunk: get_current_git_hash

Retrieves the current Git HEAD commit hash.

**Steps**:
1. **Run git rev-parse HEAD** - Get current commit hash
2. **Handle Git errors** - Repository not initialized, detached HEAD, etc.
3. **Query database** - Get stored `last_known_git_hash`
4. **Route based on comparison** - Hash differs or matches

### Branches

**Branch 1: If git_hash_retrieved**
- **Then**: `query_project_last_known_hash`
- **Details**: Get stored hash from database
  - Query:
    ```sql
    SELECT last_known_git_hash, last_git_sync
    FROM project
    WHERE id = 1
    ```
  - Store both hash and timestamp
  - If no hash found → First run (initialize)
- **Result**: Stored hash retrieved

**Branch 2: If no_last_hash**
- **Then**: `initialize_hash`
- **Details**: First run, no hash stored yet
  - This is initial project setup
  - Update database:
    ```sql
    UPDATE project
    SET last_known_git_hash = ?,
        last_git_sync = CURRENT_TIMESTAMP
    WHERE id = 1
    ```
  - Message: "Git state initialized - tracking enabled"
  - No external changes to detect (baseline established)
- **Result**: Hash initialized, sync complete

**Branch 3: If hash_exists**
- **Then**: `compare_hashes`
- **Details**: Compare stored hash with current Git HEAD
  - Comparison:
    ```python
    if stored_hash == current_hash:
        # No changes - repository state unchanged
        route_to: update_sync_timestamp
    else:
        # Hash differs - external changes detected
        route_to: trigger_external_change_detection
    ```
  - Decision point for next action
- **Result**: Hashes compared, route determined

**Branch 4: If hash_differs**
- **Then**: `trigger_external_change_detection`
- **Details**: Git state changed since last sync
  - Call: `git_detect_external_changes` directive
    - This directive analyzes what changed:
      - Which files modified
      - Which themes/flows affected
      - Which functions changed
      - Impact analysis
  - Wait for analysis to complete
  - User will be informed of changes
  - After analysis, update hash
- **Result**: External changes analyzed and reported

**Branch 5: If hash_same**
- **Then**: `update_sync_timestamp`
- **Details**: No changes detected, refresh timestamp
  - Update:
    ```sql
    UPDATE project
    SET last_git_sync = CURRENT_TIMESTAMP
    WHERE id = 1
    ```
  - This records last successful sync
  - Useful for tracking "last checked" time
  - No other action needed
- **Result**: Timestamp refreshed

**Branch 6: If sync_complete**
- **Then**: `return_success`
- **Details**: Sync operation successful
  - Show:
    - Current branch: `git branch --show-current`
    - Current commit hash: First 8 characters (e.g., "abc123de")
    - Sync status: "Up to date" or "External changes detected"
    - Last sync time: Timestamp
  - Example output:
    ```
    ✅ Git State Synchronized

    Branch: main
    Commit: abc123de (latest)
    Status: Up to date
    Last sync: 2024-10-27 14:32:15
    ```
- **Result**: User informed of Git status

**Fallback**: `log_warning`
- **Details**: Git sync failed (non-critical)
  - Message: "Git sync failed - external change detection may be affected"
  - Common causes:
    - Git not available (not installed)
    - Not a Git repository (no .git folder)
    - Database locked (concurrent access)
    - Git command error
  - Action: Log warning to notes table
  - Continue: Session proceeds with cached hash (if available)
- **Result**: Warning logged, graceful degradation

---

## Examples

### ✅ Compliant Usage

**Session Boot (No Changes):**
```bash
# User starts new AIFP session
# AI calls: git_sync_state() [called by aifp_status]

# Workflow:
# 1. Run: git rev-parse HEAD → "abc123def456..."
# 2. Query: SELECT last_known_git_hash FROM project → "abc123def456..."
# 3. Compare: stored == current (no changes)
# 4. Update: project.last_git_sync = CURRENT_TIMESTAMP
# 5. Return:
#    ✅ Git State Synchronized
#    Branch: main
#    Commit: abc123de
#    Status: Up to date
#    Last sync: 2024-10-27 14:30:00
```

---

**Session Boot (External Changes Detected):**
```bash
# User manually edited src/calc.py and committed outside AIFP
# AI calls: git_sync_state() [called by aifp_status]

# Workflow:
# 1. Run: git rev-parse HEAD → "def456ghi789..." (new hash)
# 2. Query: SELECT last_known_git_hash FROM project → "abc123def456..." (old hash)
# 3. Compare: stored != current (changes detected!)
# 4. Trigger: git_detect_external_changes directive
#    → Analyzes: src/calc.py changed, theme "Math Operations" affected
#    → Reports to user: "External changes detected in src/calc.py"
# 5. Update: project.last_known_git_hash = "def456ghi789..."
#           project.last_git_sync = CURRENT_TIMESTAMP
# 6. Return:
#    ⚠️  External changes detected
#
#    Changed files:
#    • src/calc.py
#
#    Affected themes:
#    • Math Operations
#
#    Commits:
#    def456 - Fixed calculation bug (manual edit)
#
#    Recommendations:
#    • Review changes for FP compliance
#    • Update function metadata if needed
```

---

**After AIFP Commit:**
```python
# AIFP creates commit after file write
# AI calls: git_sync_state() [after commit operation]

# Workflow:
# 1. AIFP created commit: "ghi789jkl012..."
# 2. Run: git rev-parse HEAD → "ghi789jkl012..."
# 3. Query: SELECT last_known_git_hash FROM project → "def456ghi789..." (previous)
# 4. Compare: stored != current (expected - we just committed)
# 5. Update: project.last_known_git_hash = "ghi789jkl012..."
#           project.last_git_sync = CURRENT_TIMESTAMP
#    (No external change detection needed - we know what changed)
# 6. Return:
#    ✅ Git State Synchronized
#    Branch: main
#    Commit: ghi789jk (AIFP commit)
#    Status: Up to date
```

---

**First Run (Initialize):**
```bash
# User just initialized AIFP project with Git
# AI calls: git_sync_state() [first time]

# Workflow:
# 1. Run: git rev-parse HEAD → "abc123def456..."
# 2. Query: SELECT last_known_git_hash FROM project → NULL (no hash yet)
# 3. initialize_hash:
#    UPDATE project SET last_known_git_hash = "abc123def456...",
#                       last_git_sync = CURRENT_TIMESTAMP
# 4. Return:
#    ✅ Git state initialized
#    Tracking enabled for external change detection
#    Branch: main
#    Commit: abc123de
```

---

### ❌ Non-Compliant Usage

**Not Syncing After Commits:**
```python
# ❌ Creating commit without syncing
subprocess.run(['git', 'commit', '-m', 'Update code'])
# Forgot to sync - git_detect_external_changes will trigger unnecessarily
```

**Why Non-Compliant**:
- Next session will detect "external changes" (but they were AIFP changes)
- Unnecessary analysis overhead
- Confusing to user

**Corrected:**
```python
# ✅ Always sync after commits
subprocess.run(['git', 'commit', '-m', 'Update code'])
git_sync_state()  # Update stored hash
```

---

**Duplicating Git State in Database:**
```sql
-- ❌ Creating separate git_state table
CREATE TABLE git_state (
    current_branch TEXT,
    current_commit TEXT,
    dirty_working_tree BOOLEAN
);
-- This duplicates Git's state, can get out of sync
```

**Why Non-Compliant**:
- Duplicates data Git already tracks
- Can become inconsistent
- Slower than querying Git directly

**Corrected:**
```python
# ✅ Query Git directly, only store last_known_hash
current_branch = subprocess.run(['git', 'branch', '--show-current'], capture_output=True).stdout.strip()
current_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True).stdout.strip()
# Fast (~1ms each), always accurate
```

---

## Edge Cases

### Edge Case 1: Git Not Available

**Issue**: `git` command not found or not installed

**Handling**:
```python
try:
    result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                          capture_output=True, text=True, check=True)
    current_hash = result.stdout.strip()
except FileNotFoundError:
    # Git not installed
    log_warning("Git not available - sync skipped")
    return SyncResult(
        success=False,
        error="Git not installed",
        fallback="Using cached hash (external change detection disabled)"
    )
except subprocess.CalledProcessError:
    # Git command failed (not a git repo, etc.)
    log_warning("Git command failed - not a git repository?")
    return SyncResult(success=False, error="Not a Git repository")
```

**Directive Action**: Log warning, continue with cached hash if available.

---

### Edge Case 2: Database Locked

**Issue**: Can't update project table (concurrent access)

**Handling**:
```python
import time

max_retries = 3
for attempt in range(max_retries):
    try:
        conn.execute("""
            UPDATE project
            SET last_known_git_hash = ?, last_git_sync = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (current_hash,))
        conn.commit()
        break  # Success
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            if attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
            else:
                log_warning("Database locked - sync failed after retries")
                return SyncResult(success=False, error="Database locked")
        else:
            raise
```

**Directive Action**: Retry with exponential backoff, fail gracefully if still locked.

---

### Edge Case 3: Detached HEAD State

**Issue**: HEAD is detached (not on a branch)

**Handling**:
```bash
# Check if HEAD is detached
BRANCH=$(git symbolic-ref -q HEAD)

if [ -z "$BRANCH" ]; then
    # Detached HEAD
    COMMIT=$(git rev-parse HEAD)
    echo "⚠️  Detached HEAD state"
    echo "Current commit: $COMMIT"
    echo "Not on any branch"

    # Still sync hash (change detection works)
    # Just warn user about detached state
fi
```

**Directive Action**: Sync hash as normal, warn user about detached HEAD.

---

### Edge Case 4: Hash Corrupted in Database

**Issue**: Stored hash is invalid (not a valid Git object)

**Handling**:
```bash
# Verify stored hash exists in Git history
if ! git cat-file -e "$STORED_HASH" 2>/dev/null; then
    # Hash doesn't exist (history rewritten?)
    echo "⚠️  Stored hash invalid or history rewritten"
    echo "Re-initializing from current HEAD"

    # Re-initialize with current hash
    UPDATE project SET last_known_git_hash = current_hash
fi
```

**Directive Action**: Re-initialize hash if corrupted, warn user.

---

## Related Directives

- **Called By**:
  - `aifp_status` - At session boot for synchronization
  - `project_file_write` - After commits
  - `git_merge_branch` - After merge operations
- **Calls**:
  - `git_detect_external_changes` - If hash differs
  - Git CLI commands for hash retrieval
- **Enables**:
  - External change detection workflow
- **Related**:
  - `git_init` - Initializes Git integration, sets up for syncing

---

## Helper Functions Used

- `get_current_git_hash() -> str` - Runs `git rev-parse HEAD`
- `get_stored_git_hash(conn) -> str | None` - Queries database for last_known_git_hash
- `update_git_hash(conn, hash: str) -> None` - Updates project table with new hash
- `get_current_branch() -> str` - Runs `git branch --show-current`
- `check_git_available() -> bool` - Verifies Git is installed

---

## Database Operations

This directive updates the following tables:

- **`project`**: Updates `last_known_git_hash` and `last_git_sync` fields
- **`notes`**: Logs warnings if sync fails (optional)

**Note**: This directive primarily **reads** from Git and **writes** to project table only.

---

## Testing

How to verify this directive is working:

1. **Initial sync** → Hash stored
   ```python
   git_sync_state()
   hash = query_db("SELECT last_known_git_hash FROM project WHERE id=1")
   assert hash is not None
   ```

2. **No changes** → Timestamp updated only
   ```python
   before = query_db("SELECT last_git_sync FROM project WHERE id=1")
   git_sync_state()
   after = query_db("SELECT last_git_sync FROM project WHERE id=1")
   assert after > before
   ```

3. **External changes** → Triggers detection
   ```bash
   # Make manual commit
   echo "# comment" >> src/test.py
   git add . && git commit -m "Manual edit"

   # Sync should detect change
   result = git_sync_state()
   assert result.external_changes_detected == True
   ```

4. **After AIFP commit** → Hash updated
   ```python
   old_hash = query_db("SELECT last_known_git_hash FROM project WHERE id=1")
   # AIFP creates commit
   git_sync_state()
   new_hash = query_db("SELECT last_known_git_hash FROM project WHERE id=1")
   assert new_hash != old_hash
   ```

---

## Common Mistakes

- ❌ **Not calling after commits** - Hash becomes stale
- ❌ **Duplicating Git state in DB** - Query Git directly instead
- ❌ **Not handling Git unavailable** - Assume Git always works
- ❌ **Syncing too frequently** - Only sync on session boot and after operations
- ❌ **Not logging failures** - Silent failures hide issues

---

## Roadblocks and Resolutions

### Roadblock 1: git_unavailable
**Issue**: Git command not available or fails
**Resolution**: Skip sync, continue with cached hash, warn user

### Roadblock 2: database_locked
**Issue**: Can't update project table (concurrent access)
**Resolution**: Retry with exponential backoff (max 3 attempts), log warning if still failing

### Roadblock 3: hash_corrupted
**Issue**: Stored hash is invalid or doesn't exist in Git history
**Resolution**: Re-initialize from current Git HEAD, warn user about potential history rewrite

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#git-helpers)
- [Blueprint: Git Integration](../../../docs/blueprints/blueprint_git.md)
- [JSON Definition](../../../docs/directives-json/directives-git.json)
- [Database Schema](../../../docs/db-schema/schemaExampleProject.sql)

---

*Part of AIFP v1.0 - Git integration directive for state synchronization*

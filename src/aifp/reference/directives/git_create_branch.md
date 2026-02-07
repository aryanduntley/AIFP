# Directive: git_create_branch

**Type**: Git
**Level**: 2
**Parent Directive**: project_task_decomposition
**Priority**: HIGH - Critical for team collaboration

---

## Purpose

The `git_create_branch` directive creates new work branches following the AIFP naming convention `aifp-{user}-{number}` for multi-user and multi-AI collaboration. This directive enables **parallel development** where multiple developers and autonomous AI instances work simultaneously on different features without conflicts.

This directive is **essential for AIFP collaboration** because:
- **Isolates work**: Each developer/AI has dedicated branch
- **Clear attribution**: Branch name shows who is working on what
- **Structured naming**: Sequential numbering prevents collisions
- **Task linking**: Branches can be linked to specific tasks/milestones
- **Audit trail**: All branches tracked in `work_branches` table
- **Supports AI autonomy**: AI instances can create their own branches

The branch creation workflow:
1. **Identify user** - From Git config, environment, or prompt
2. **Get next branch number** - Query `work_branches` table for latest
3. **Format branch name** - `aifp-{user}-{number:03d}`
4. **Create Git branch** - Checkout new branch from main
5. **Store metadata** - Record in `work_branches` table
6. **Optional task link** - Connect branch to task/milestone

**Branch Naming Examples**:
- `aifp-alice-001` - Alice's first work branch
- `aifp-bob-003` - Bob's third work branch
- `aifp-ai-claude-001` - Claude AI instance's first branch
- `aifp-ai-gpt-002` - GPT AI instance's second branch

**Important**: Branch purpose is stored in database, not in branch name. This keeps names short and structured while maintaining rich metadata.

---

## When to Apply

This directive applies when:
- **Starting new work** - User begins work on feature/task
- **Task decomposition** - After tasks created, branches needed
- **User requests** - "Create branch for authentication"
- **AI autonomy** - AI decides to work independently on subtask
- **Team collaboration** - Multiple developers joining project

---

## Workflow

### Trunk: get_user_identification

Identifies the user (human or AI) creating the branch.

**Steps**:
1. **Check if user provided** - Was user name given in command?
2. **Detect from Git config** - Try `git config user.name`
3. **Detect from environment** - Try `$USER`, `$USERNAME` env vars
4. **Detect from system** - Try system username
5. **Prompt if needed** - Ask user if all detection fails

### Branches

**Branch 1: If user_provided**
- **Then**: `use_provided_user`
- **Details**: User name explicitly provided
  - Validate: Ensure user_name is valid (alphanumeric, no spaces)
  - Normalize: Convert to lowercase, replace spaces with hyphens
  - Examples:
    - "Alice Smith" → "alice-smith"
    - "AI Claude" → "ai-claude"
    - "GPT-4" → "gpt-4"
- **Result**: Validated user name ready

**Branch 2: If no_user**
- **Then**: `detect_user`
- **Details**: Attempt auto-detection from multiple sources
  - Sources (in order):
    1. **git config user.name**: `git config user.name` → "Alice Smith"
    2. **env $USER**: `echo $USER` → "alice"
    3. **env $USERNAME**: `echo $USERNAME` → "alice" (Windows)
    4. **system username**: `whoami` → "alice"
  - Fallback: If all fail, prompt user
  - Normalize detected name to lowercase-hyphen format
- **Result**: User name detected or prompted

**Branch 3: If user_determined**
- **Then**: `get_next_branch_number`
- **Details**: Query database for next available number
  - Query:
    **Use helper functions** for database operations. Query available helpers for the appropriate database.
  - If no branches yet: Use 1
  - Else: Increment max by 1
  - Example: alice has branches 001, 002 → next is 003
- **Result**: Branch number determined

**Branch 4: If branch_number_determined**
- **Then**: `format_branch_name`
- **Details**: Format branch name with zero-padding
  - Format: `aifp-{user}-{number:03d}`
  - Examples:
    - user="alice", number=1 → "aifp-alice-001"
    - user="bob", number=15 → "aifp-bob-015"
    - user="ai-claude", number=3 → "aifp-ai-claude-003"
  - Validate: Check branch doesn't already exist
- **Result**: Valid branch name formatted

**Branch 5: If branch_name_valid**
- **Then**: `create_git_branch`
- **Details**: Create branch in Git
  - Command: `git checkout -b {branch_name} main`
  - Creates branch from main (or specified base branch)
  - Switches to new branch
  - Verifies creation successful
- **Result**: Git branch created and checked out

**Branch 6: If git_branch_created**
- **Then**: `store_branch_metadata`
- **Details**: Record branch in database
  - Insert into `work_branches` table:
    **Use helper functions** for database operations. Query available helpers for the appropriate database.
  - Fields:
    - `branch_name`: Full branch name
    - `user_name`: Who created branch
    - `purpose`: What feature/task being worked on
    - `status`: 'active' (or 'merged', 'abandoned' later)
    - `created_from`: Parent branch (usually 'main')
    - `metadata_json`: Optional links to tasks, themes, etc.
- **Result**: Branch metadata stored

**Branch 7: If optional_task_link**
- **Then**: `link_to_task`
- **Details**: Link branch to specific task (if provided)
  - Update metadata_json with task_id
  - Update task table to reference branch name
  - Example:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Enables tracking which branch is working on which task
- **Result**: Branch linked to task

**Branch 8: If all_complete**
- **Then**: `report_success`
- **Details**: Report branch creation success
  - Show:
    - Branch name: "aifp-alice-001"
    - User: "alice"
    - Purpose: "Implement matrix multiplication"
    - Base branch: "main"
    - Linked tasks: "#15"
  - Confirm checked out to new branch
  - Ready to start work
- **Result**: User informed of successful branch creation

**Fallback**: `prompt_user`
- **Details**: Branch creation failed
  - Ask: "Branch creation failed - check Git status"
  - Common issues:
    - Uncommitted changes (suggest commit or stash)
    - Branch already exists (suggest alternative name)
    - Git errors (check repository state)
  - Log to notes table
- **Result**: User guidance requested

---

## Examples

### ✅ Compliant Usage

**Standard Branch Creation:**
```bash
# User: "Create branch for implementing authentication"
# AI calls: git_create_branch(purpose="Implement authentication")

# Workflow:
# 1. User identification:
#    - Check git config: git config user.name → "Alice Smith"
#    - Normalize: "alice-smith"
#
# 2. Get next number:
#    - Helper: Use helper to get max branch number for user 'alice-smith'
#    - Result: 2 (alice-smith has 001, 002)
#    - Next: 3
#
# 3. Format name:
#    - Format: "aifp-alice-smith-003"
#
# 4. Create branch:
#    - Run: git checkout -b aifp-alice-smith-003 main
#    - Output: Switched to a new branch 'aifp-alice-smith-003'
#
# 5. Store metadata:
#    - INSERT INTO work_branches (
#        branch_name='aifp-alice-smith-003',
#        user_name='alice-smith',
#        purpose='Implement authentication',
#        status='active',
#        created_from='main'
#      )
#
# 6. Link to task (if task #42 exists):
#    - UPDATE tasks SET git_branch='aifp-alice-smith-003' WHERE id=42
#
# Result:
# ✅ Branch created: aifp-alice-smith-003
# ✅ User: alice-smith
# ✅ Purpose: Implement authentication
# ✅ Linked to task #42
# ✅ Ready to start work
```

---

**AI Instance Creating Branch:**
```bash
# AI decides to work independently on optimization
# AI calls: git_create_branch(user="ai-claude", purpose="Optimize performance")

# Workflow:
# 1. User: "ai-claude" (provided)
# 2. Get next number:
#    - Query: SELECT MAX(...) WHERE user_name='ai-claude'
#    - Result: 0 (no branches yet)
#    - Next: 1
# 3. Format: "aifp-ai-claude-001"
# 4. Create: git checkout -b aifp-ai-claude-001 main
# 5. Store metadata with AI marker
#
# Result:
# ✅ Branch created: aifp-ai-claude-001
# ✅ User: ai-claude
# ✅ Purpose: Optimize performance
# ✅ AI working autonomously
```

---

### ❌ Non-Compliant Usage

**Not Following Naming Convention:**
```bash
# ❌ Custom branch names
git checkout -b feature/auth
git checkout -b alice-fixes
```

**Why Non-Compliant**:
- Doesn't follow AIFP convention
- Can't auto-detect user from branch name
- No sequential numbering
- Database tracking inconsistent

**Corrected:**
```bash
# ✅ Use directive
git_create_branch(user="alice", purpose="Authentication feature")
# Creates: aifp-alice-001
```

---

**Not Storing Metadata:**
```bash
# ❌ Just creating Git branch
git checkout -b aifp-alice-001
# No database record
```

**Why Non-Compliant**:
- Branch not tracked in work_branches table
- No purpose recorded
- Can't query active branches
- Collaboration tracking broken

**Corrected:**
```bash
# ✅ Use directive (handles both Git and DB)
git_create_branch(user="alice", purpose="Feature X")
```

---

## Edge Cases

### Edge Case 1: Branch Already Exists

**Issue**: Branch name collision

**Handling**:
```python
# Check if branch exists
result = run_command("git rev-parse --verify aifp-alice-001")
if result.success:
    # Branch exists, increment number
    # Query next available number
    next_num = get_next_available_number("alice")
    branch_name = f"aifp-alice-{next_num:03d}"
```

**Directive Action**: Auto-increment to next available number.

---

### Edge Case 2: User Detection Fails

**Issue**: Can't detect user from any source

**Handling**:
```python
# All detection failed
if not user_name:
    # Prompt user
    user_name = prompt("Enter your name for branch creation:")
    # Validate and normalize
    user_name = normalize_username(user_name)
```

**Directive Action**: Prompt for manual input, validate format.

---

### Edge Case 3: Uncommitted Changes

**Issue**: Working directory has uncommitted changes

**Handling**:
```bash
# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    # Uncommitted changes detected
    echo "Uncommitted changes in working directory"

    # Options:
    # 1. Commit changes first
    # 2. Stash changes
    # 3. Create branch anyway (changes follow)
fi
```

**Directive Action**: Warn user, suggest committing or stashing, allow proceeding (changes follow to new branch).

---

### Edge Case 4: Not on Main Branch

**Issue**: Currently on a different branch, not main

**Handling**:
```bash
# Check current branch
CURRENT=$(git branch --show-current)
if [ "$CURRENT" != "main" ]; then
    # Not on main
    echo "Creating branch from '$CURRENT' instead of 'main'"

    # Options:
    # 1. Switch to main first
    # 2. Create from current branch
    # 3. Specify base branch explicitly
fi
```

**Directive Action**: Allow creating from current branch, update `created_from` field, or suggest switching to main first.

---

## Related Directives

- **Called By**:
  - `project_task_decomposition` - When tasks need dedicated branches
  - User commands - Direct branch creation requests
- **Calls**:
  - Git CLI commands via helpers
  - Database query/update helpers
- **Enables**:
  - `git_merge_branch` - Merge work back to main
  - `git_detect_conflicts` - Analyze merge conflicts
- **Related**:
  - `git_init` - Must be called first to setup Git
  - `project_task_update` - Tasks link to branches

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`work_branches`**: INSERT new branch record with metadata
- **`tasks`**: UPDATE with `git_branch` field if task linked (optional)

---

## Testing

How to verify this directive is working:

1. **Create first branch** → Number starts at 001
   ```python
   result = git_create_branch(user="alice", purpose="Test feature")
   assert result["branch_name"] == "aifp-alice-001"
   ```

2. **Create second branch** → Number increments
   ```python
   git_create_branch(user="alice", purpose="Another feature")
   result = query_db("SELECT branch_name FROM work_branches WHERE user_name='alice'")
   assert len(result) == 2
   assert "aifp-alice-002" in [r[0] for r in result]
   ```

3. **Branch stored in database** → Metadata recorded
   **Use helper functions** for database operations. Query available helpers for the appropriate database.

---

## Common Mistakes

- ❌ **Not following naming convention** - Custom branch names break tracking
- ❌ **Not storing metadata** - Branch exists in Git but not database
- ❌ **Duplicate numbers** - Not querying database for next number
- ❌ **Not normalizing usernames** - Inconsistent capitalization/spaces
- ❌ **Forgetting to link tasks** - Branches orphaned from work items

---

## Roadblocks and Resolutions

### Roadblock 1: branch_exists
**Issue**: Branch name already taken
**Resolution**: Increment branch number or prompt for alternative name

### Roadblock 2: user_detection_fails
**Issue**: Can't auto-detect user name
**Resolution**: Prompt user to provide name manually, store for future use

### Roadblock 3: uncommitted_changes
**Issue**: Working directory has uncommitted changes
**Resolution**: Prompt user to commit or stash changes before branching (or allow changes to follow)

---

## References

None
---

*Part of AIFP v1.0 - Git integration directive for collaborative branch management*

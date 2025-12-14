# Directive: git_init

**Type**: Git
**Level**: 1
**Parent Directive**: project_init
**Priority**: HIGH - Critical for version control setup

---

## Purpose

The `git_init` directive initializes Git version control for AIFP projects, enabling multi-user collaboration, change tracking, and FP-powered conflict resolution. This directive either creates a new Git repository or integrates with an existing one, configures AIFP-specific `.gitignore` rules, and stores the initial Git commit hash for external change detection.

Git integration is **essential for AIFP collaboration** because:
- **Multi-user development**: Multiple developers work on branches simultaneously
- **AI collaboration**: Multiple AI instances can work autonomously on different branches
- **Change tracking**: Detect when files are modified outside AIFP sessions
- **FP-powered merging**: Use function purity levels for intelligent conflict resolution
- **Version history**: Track evolution of functional code over time

The directive handles two scenarios:
1. **New repository**: Initialize Git, create `.gitignore`, make initial commit
2. **Existing repository**: Integrate with current repo, update `.gitignore`, sync state

After initialization, the directive:
- Stores current Git commit hash in `project.last_known_git_hash`
- Creates Git collaboration tables (`work_branches`, `merge_history`)
- Configures `.gitignore` to exclude user-specific files
- Reports Git status to user

**Important**: Current Git state (branch, commit hash) is **always queried from Git directly** - not duplicated in the database. Only AIFP-specific collaboration metadata is stored in `project.db`.

---

## Why AIFP + Git is Superior to OOP + Git

### The FP Collaboration Advantage

AIFP's pure functional programming approach makes Git collaboration **dramatically simpler and safer** than traditional OOP codebases:

| OOP Merge Problem | AIFP FP Solution |
|-------------------|------------------|
| **Class hierarchies conflict** | ✅ No classes → No hierarchy conflicts |
| **Hidden state changes** | ✅ Pure functions → Explicit inputs/outputs |
| **Side effects everywhere** | ✅ Side effects isolated → Easy to identify conflicts |
| **Method override conflicts** | ✅ No inheritance → No override conflicts |
| **Implicit dependencies** | ✅ Database tracks all dependencies → Clear conflict detection |
| **Mutation conflicts** | ✅ Immutable data → Fewer state conflicts |
| **Hard to test both versions** | ✅ Pure functions → Easy to test and compare |

### Multi-User Collaboration Philosophy

AIFP Git integration is designed for:
- **Multiple developers working simultaneously** on different branches
- **Autonomous AI instances** creating and managing their own branches
- **FP-powered intelligent conflict resolution** using purity levels and test coverage
- **Database-tracked project state** enabling informed merge decisions
- **Clear attribution** through structured branch naming: `aifp-{user}-{number}`

### What Gets Tracked in Git?

| Component | Track in Git? | Rationale |
|-----------|---------------|-----------|
| **Source code** | ✅ Yes | Standard Git usage |
| **`.aifp-project/project.db`** | ✅ Yes | Organizational state (themes, tasks, functions, dependencies) - enables FP-powered merging |
| **`.aifp-project/ProjectBlueprint.md`** | ✅ Yes | Project context document |
| **`.aifp-project/user_preferences.db`** | ❌ No | User-specific settings, not shared |
| **`.aifp-project/backups/`** | ❌ No | Generated backup files |
| **`.aifp-project/logs/`** | ❌ No | Use Case 2 execution logs (temporary) |

**Critical Decision**: `project.db` is tracked because it contains function metadata (purity levels, parameters, dependencies) that enables AI to intelligently resolve merge conflicts.

### .gitignore Configuration

During initialization, this directive creates/updates `.gitignore`:

```gitignore
# AIFP-specific (DO track organizational state)
.aifp-project/user_preferences.db
.aifp-project/backups/
.aifp-project/logs/
.aifp-project/temp/
.aifp-project/.mcp-session-*

# Standard ignores
__pycache__/
*.pyc
*.pyo
.pytest_cache/
node_modules/
.env
*.log
.DS_Store
```

---

## When to Apply

This directive applies when:
- **Called by `project_init`** - During new project setup
- **User requests Git setup** - "Initialize Git", "setup version control"
- **Existing project needs Git** - Adding version control to existing AIFP project
- **Git repository corrupted** - Re-initialization needed
- **Team collaboration starts** - Enabling multi-user workflows

---

## Workflow

### Trunk: check_git_repo_exists

Checks if a Git repository already exists in the project directory.

**Steps**:
1. **Check for `.git` folder** - Does `.git/` exist in project root?
2. **Verify Git working** - Run `git status` to confirm valid repository
3. **Route to integration or creation** - Based on repository status

### Branches

**Branch 1: If git_repo_exists**
- **Then**: `integrate_existing_repo`
- **Details**: Integrate with existing Git repository
  - Check: Verify `.git` folder exists
  - Actions:
    1. **Verify Git working**: Run `git status` to confirm valid repo
    2. **Get current hash**: Run `git rev-parse HEAD` to get commit hash
    3. **Update project.last_known_git_hash**: Store hash in `project.db`
    4. **Update .gitignore**: Add AIFP-specific exclusions if missing
    5. **Get current branch**: Run `git branch --show-current`
    6. **Report integration**: Show Git status and tracking info
- **Result**: Existing repository integrated with AIFP

**Branch 2: If no_git_repo**
- **Then**: `create_new_repo`
- **Details**: Initialize new Git repository
  - Actions:
    1. **git init**: Run `git init` in project root
    2. **create .gitignore**: Create `.gitignore` with AIFP exclusions
    3. **initial commit**: Commit AIFP project structure
    4. **update project.last_known_git_hash**: Store initial commit hash
- **Result**: New Git repository created and configured

**Branch 3: If git_hash_stored**
- **Then**: `create_git_tables`
- **Details**: Create Git collaboration tables in project.db
  - Tables to create:
    - **work_branches**: Track user/AI work branches
    - **merge_history**: Full audit trail of merges
  - Use schema from project.db
- **Result**: Collaboration tables ready

**Branch 4: If tables_created**
- **Then**: `report_success`
- **Details**: Report Git initialization success
  - Show:
    - Git status (initialized or integrated)
    - Current branch name
    - Current commit hash
    - Tracking status (AIFP change detection enabled)
    - Collaboration tables ready
- **Result**: User informed of Git setup completion

**Fallback**: `prompt_user`
- **Details**: Git initialization failed
  - Ask: "Git initialization failed - check permissions or Git installation"
  - Suggest: Install Git, check file permissions, or proceed without version control
  - Log error to notes table
- **Result**: User guidance requested

---

## Examples

### ✅ Compliant Usage

**New Repository Initialization:**
```bash
# User: "Initialize AIFP project with Git"
# AI calls: git_init directive

# Workflow:
# 1. Check .git folder → not found
# 2. Run: git init
#    → Initialized empty Git repository in /path/to/project/.git/
# 3. Create .gitignore:
#    .aifp/user_preferences.db
#    .aifp/backups/
#    .aifp/temp/
#    __pycache__/
#    *.pyc
# 4. Run: git add .
# 5. Run: git commit -m "Initial AIFP project setup"
#    → [main abc1234] Initial AIFP project setup
# 6. Run: git rev-parse HEAD → abc1234...
# 7. UPDATE project SET last_known_git_hash='abc1234...', last_git_sync=now
# 8. CREATE TABLE work_branches, merge_history
#
# Result:
# ✅ Git initialized
# ✅ Current branch: main
# ✅ Commit: abc1234
# ✅ AIFP change detection enabled
# ✅ Collaboration tables ready
```

---

**Existing Repository Integration:**
```bash
# User already has Git repo, adds AIFP
# AI calls: git_init directive

# Workflow:
# 1. Check .git folder → found
# 2. Run: git status
#    → On branch main, working tree clean
# 3. Run: git rev-parse HEAD → def5678...
# 4. UPDATE project SET last_known_git_hash='def5678...', last_git_sync=now
# 5. Check .gitignore → missing AIFP exclusions
# 6. Append to .gitignore:
#    # AIFP-specific
#    .aifp/user_preferences.db
#    .aifp/backups/
#    .aifp/temp/
# 7. CREATE TABLE work_branches, merge_history
# 8. Run: git branch --show-current → main
#
# Result:
# ✅ Integrated with existing Git repo
# ✅ Current branch: main
# ✅ Last commit: def5678
# ✅ .gitignore updated
# ✅ AIFP change detection enabled
```

---

### ❌ Non-Compliant Usage

**Not Checking Existing Repository:**
```bash
# ❌ Always runs git init
git init  # Fails if .git already exists
```

**Why Non-Compliant**:
- Doesn't check for existing repository
- Could corrupt existing Git history
- Loses existing commits

**Corrected:**
```bash
# ✅ Check first
if [ -d .git ]; then
    # Integrate existing
    git rev-parse HEAD
else
    # Create new
    git init
fi
```

---

**Not Storing Git Hash:**
```bash
# ❌ Initializes Git but doesn't track hash
git init
git commit -m "Initial commit"
# Forgot to store hash in project.db
```

**Why Non-Compliant**:
- External change detection won't work
- Can't detect modifications made outside AIFP
- Git integration incomplete

**Corrected:**
```bash
# ✅ Store hash
git init
git commit -m "Initial commit"
HASH=$(git rev-parse HEAD)
sqlite3 .aifp-project/project.db \
  "UPDATE project SET last_known_git_hash='$HASH', last_git_sync=CURRENT_TIMESTAMP"
```

---

## Edge Cases

### Edge Case 1: Git Not Installed

**Issue**: `git` command not found

**Handling**:
```python
# Check if Git is installed
result = subprocess.run(['git', '--version'], capture_output=True)
if result.returncode != 0:
    # Git not installed
    return {
        "success": False,
        "error": "Git not installed",
        "suggestion": "Install Git: https://git-scm.com/downloads",
        "fallback": "Proceed without version control? (y/n)"
    }
```

**Directive Action**: Prompt user to install Git or proceed without version control (limited collaboration).

---

### Edge Case 2: Existing .git Folder is Corrupted

**Issue**: `.git` exists but repository is broken

**Handling**:
```bash
# Try git status
if ! git status &>/dev/null; then
    # Repository corrupted
    echo "Git repository corrupted"

    # Suggest options:
    # 1. Run git fsck to check/repair
    # 2. Delete .git and re-initialize (loses history)
    # 3. Restore from backup
fi
```

**Directive Action**: Run `git fsck`, suggest repair or re-initialization with user approval.

---

### Edge Case 3: Uncommitted Changes in Existing Repo

**Issue**: Working directory has uncommitted changes

**Handling**:
```bash
# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    # Uncommitted changes detected
    echo "Uncommitted changes found"

    # Options:
    # 1. Commit changes first
    # 2. Stash changes
    # 3. Proceed anyway (AIFP won't conflict)
fi
```

**Directive Action**: Inform user, suggest committing or stashing, then continue AIFP integration.

---

### Edge Case 4: No Initial Commit Yet (New Repo)

**Issue**: Git initialized but no commits yet

**Handling**:
```bash
# Try to get HEAD
if ! git rev-parse HEAD &>/dev/null; then
    # No commits yet
    echo "Making initial commit..."
    git add .aifp-project/
    git commit -m "Initial AIFP project setup"

    # Now get hash
    HASH=$(git rev-parse HEAD)
fi
```

**Directive Action**: Make initial commit with AIFP project structure, then proceed.

---

## Related Directives

- **Called By**:
  - `project_init` - During project initialization
- **Calls**:
  - Git CLI commands via helpers
  - Database helpers for hash storage
- **Triggers**:
  - `git_sync_state` - After initialization to sync state
- **Enables**:
  - `git_detect_external_changes` - External change detection
  - `git_create_branch` - Branch creation for collaboration
  - `git_merge_branch` - FP-powered merging

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`project`**: Sets `last_known_git_hash` and `last_git_sync` for change tracking
- **`work_branches`**: Creates table for branch collaboration tracking
- **`merge_history`**: Creates table for merge audit trail

---

## Testing

How to verify this directive is working:

1. **New repository** → Git initialized successfully
   ```bash
   git_init("/path/to/project")
   # Check: .git folder exists
   # Check: Initial commit made
   # Check: project.last_known_git_hash populated
   ```

2. **Existing repository** → Integration successful
   ```bash
   # Create repo first
   cd /path/to/project && git init && git commit --allow-empty -m "test"

   git_init("/path/to/project")
   # Check: No new .git created
   # Check: .gitignore updated
   # Check: project.last_known_git_hash matches HEAD
   ```

3. **Collaboration tables** → Created successfully
   ```sql
   SELECT name FROM sqlite_master WHERE type='table' AND name IN ('work_branches', 'merge_history');
   -- Expected: 2 rows
   ```

---

## Common Mistakes

- ❌ **Not checking for existing repository** - Could corrupt Git history
- ❌ **Forgetting to store Git hash** - External change detection won't work
- ❌ **Not creating .gitignore** - User preferences tracked in Git (privacy issue)
- ❌ **Not creating collaboration tables** - Branch tracking won't work
- ❌ **Not handling Git not installed** - Assumes Git always available

---

## Roadblocks and Resolutions

### Roadblock 1: git_not_installed
**Issue**: Git command not found on system
**Resolution**: Prompt user to install Git or proceed without version control (limited features)

### Roadblock 2: git_repo_corrupted
**Issue**: `.git` folder exists but repository is broken
**Resolution**: Suggest `git fsck` or re-initialization (user approval required to avoid data loss)

### Roadblock 3: permission_denied
**Issue**: Cannot write to project directory or run Git commands
**Resolution**: Check file permissions, suggest running with appropriate privileges, or change project location

---

## References

- [Git Documentation](https://git-scm.com/doc)

---

*Part of AIFP v1.0 - Git integration directive for version control and collaboration*

# Git Integration Blueprint

## Overview

AIFP uses Git for **version control and optional branch-based workflow management**. The system initializes a Git repository if one doesn't exist, or integrates with an existing one. This document outlines Git integration strategy, based on lessons learned from the AIProjectManager branch-based implementation.

### Core Philosophy

- **Auto-initialize if needed**: Create `.git` if project lacks version control
- **Respect existing repos**: Integrate with user's existing Git workflow
- **Branch-based organization** (optional): Use branches for isolated work (inspired by AIProjectManager /home/eveningb4dawn/Desktop/Projects/AIProjectManager/docs/forRemoval/branch-based-git-implementation-plan.md)
- **External change detection**: Detect user modifications outside AI sessions
- **No forced Git workflow**: Git is a tool, not a requirement (can work without it)

---

## Git Repository Setup

### Initialization Check

When `project_init` runs:

```python
def initialize_git(project_root: Path):
    git_dir = project_root / ".git"

    if git_dir.exists():
        # Existing Git repo - integrate with it
        return integrate_existing_repo(project_root)
    else:
        # No Git repo - create one
        return create_new_repo(project_root)
```

### Create New Repository

```bash
cd /path/to/project
git init
git add .
git commit -m "Initial commit: AIFP project initialization"
```

**What gets tracked**:
- All source code files
- `.aifp-project/` directory (except user settings and backups)
- Configuration files
- Documentation

**What gets ignored** (`.gitignore` additions):
```gitignore
# AIFP-specific
.aifp-project/UserSettings/
.aifp-project/database/backups/
.aifp-project/.mcp-session-*
.aifp-project/temp/

# Standard language-specific ignores
__pycache__/
*.pyc
node_modules/
.env
*.log
```

### Integrate Existing Repository

```python
def integrate_existing_repo(project_root: Path):
    # 1. Verify Git is working
    result = subprocess.run(['git', 'status'], cwd=project_root, capture_output=True)
    if result.returncode != 0:
        raise GitError("Git repository is corrupted or inaccessible")

    # 2. Get current branch
    current_branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                                   cwd=project_root, capture_output=True, text=True).stdout.strip()

    # 3. Store Git state in project.db
    conn.execute("""
        INSERT INTO git_state (current_branch, last_known_hash, last_sync_timestamp)
        VALUES (?, ?, ?)
    """, (current_branch, get_current_commit_hash(), datetime.now()))

    # 4. Update .gitignore if needed
    update_gitignore(project_root)

    return GitIntegrationResult(existing_repo=True, branch=current_branch)
```

---

## External Change Detection

### Session Boot Process

Every time an AI session starts:

```python
def detect_external_changes(project_root: Path) -> ChangeAnalysis:
    # 1. Get last known Git state from project.db
    last_hash = conn.execute("SELECT last_known_hash FROM git_state").fetchone()[0]

    # 2. Get current Git HEAD
    current_hash = get_current_commit_hash()

    if last_hash == current_hash:
        return ChangeAnalysis(changed_files=[], no_changes=True)

    # 3. Get changed files between commits
    result = subprocess.run([
        'git', 'diff', '--name-only',
        f'{last_hash}..{current_hash}'
    ], capture_output=True, text=True)

    changed_files = result.stdout.strip().split('\n')

    # 4. Analyze impact on themes/flows
    affected_themes = analyze_theme_impact(changed_files)

    # 5. Update project.db with new state
    conn.execute("""
        UPDATE git_state
        SET last_known_hash = ?, last_sync_timestamp = ?
    """, (current_hash, datetime.now()))

    return ChangeAnalysis(
        changed_files=changed_files,
        affected_themes=affected_themes,
        commit_range=f"{last_hash[:7]}..{current_hash[:7]}"
    )
```

### Theme Impact Analysis

```python
def analyze_theme_impact(changed_files: List[str]) -> List[str]:
    affected_themes = set()

    for file_path in changed_files:
        # Query project.db for file's themes
        themes = conn.execute("""
            SELECT DISTINCT t.name
            FROM themes t
            JOIN flow_themes ft ON t.id = ft.theme_id
            JOIN flows f ON ft.flow_id = f.id
            JOIN file_flows ff ON f.id = ff.flow_id
            JOIN files fi ON ff.file_id = fi.id
            WHERE fi.path = ?
        """, (file_path,)).fetchall()

        affected_themes.update(theme[0] for theme in themes)

    return list(affected_themes)
```

---

## Branch-Based Workflow (Optional)

**Inspired by AIProjectManager's branch-based Git implementation**, AIFP can optionally use Git branches for isolated work. This feature is **optional** and only used if user explicitly requests it.

### Branch Naming Convention

**Format**: `aifp-branch-{NNN}` (sequential numbering)

**Examples**:
- `aifp-branch-001` - First isolated work branch
- `aifp-branch-002` - Second isolated work branch
- `aifp-branch-003` - Third isolated work branch

**Note**: Unlike AIProjectManager's `ai-pm-org-branch-{XXX}` naming, AIFP uses simpler sequential numbering without user/purpose in the name. Purpose is stored in project.db metadata.

### Creating a Work Branch

```python
def create_work_branch(purpose: str, project_root: Path) -> BranchCreationResult:
    # 1. Get next sequential branch number
    next_num = get_next_branch_number(project_root)
    branch_name = f"aifp-branch-{next_num:03d}"

    # 2. Create branch from main
    subprocess.run(['git', 'checkout', '-b', branch_name, 'main'], cwd=project_root)

    # 3. Store branch metadata in project.db
    conn.execute("""
        INSERT INTO work_branches (branch_name, purpose, status, created_at)
        VALUES (?, ?, 'active', ?)
    """, (branch_name, purpose, datetime.now()))

    return BranchCreationResult(
        branch_name=branch_name,
        purpose=purpose,
        created_from='main'
    )
```

### Merging Work Branch

```python
def merge_work_branch(branch_name: str, project_root: Path) -> MergeResult:
    # 1. Ensure we're on main
    subprocess.run(['git', 'checkout', 'main'], cwd=project_root)

    # 2. Merge the work branch
    result = subprocess.run(['git', 'merge', branch_name], cwd=project_root, capture_output=True)

    if result.returncode != 0:
        # Merge conflict detected
        return MergeResult(
            success=False,
            conflicts=True,
            message="Merge conflicts detected. Manual resolution required."
        )

    # 3. Update project.db
    conn.execute("""
        UPDATE work_branches
        SET status = 'merged', merged_at = ?
        WHERE branch_name = ?
    """, (datetime.now(), branch_name))

    # 4. Optionally delete branch
    subprocess.run(['git', 'branch', '-d', branch_name], cwd=project_root)

    return MergeResult(success=True, conflicts=False)
```

---

## Git State Tracking (project.db)

### git_state Table

```sql
CREATE TABLE git_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    current_branch TEXT NOT NULL,
    last_known_hash TEXT,
    last_sync_timestamp DATETIME,
    project_root_path TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### work_branches Table (Optional)

```sql
CREATE TABLE work_branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_name TEXT UNIQUE NOT NULL,       -- e.g., 'aifp-branch-001'
    purpose TEXT NOT NULL,                  -- e.g., 'Implement matrix multiplication'
    status TEXT DEFAULT 'active',           -- active, merged, abandoned
    created_from TEXT DEFAULT 'main',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    merged_at DATETIME NULL,
    metadata_json TEXT                      -- Optional: additional branch metadata
);
```

---

## Git Helper Functions

### get_current_commit_hash()

```python
def get_current_commit_hash(project_root: Path) -> str:
    result = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()
```

### get_changed_files_since(commit_hash: str)

```python
def get_changed_files_since(commit_hash: str, project_root: Path) -> List[str]:
    result = subprocess.run([
        'git', 'diff', '--name-only',
        f'{commit_hash}..HEAD'
    ], cwd=project_root, capture_output=True, text=True)

    return [f for f in result.stdout.strip().split('\n') if f]
```

### create_branch(branch_name: str, from_branch: str = 'main')

```python
def create_branch(branch_name: str, from_branch: str, project_root: Path) -> bool:
    result = subprocess.run([
        'git', 'checkout', '-b', branch_name, from_branch
    ], cwd=project_root, capture_output=True)

    return result.returncode == 0
```

### get_current_branch()

```python
def get_current_branch(project_root: Path) -> str:
    result = subprocess.run([
        'git', 'rev-parse', '--abbrev-ref', 'HEAD'
    ], cwd=project_root, capture_output=True, text=True)

    return result.stdout.strip()
```

---

## Conflict Resolution

When merging branches or detecting external changes that conflict with AI's planned modifications:

### Conflict Detection

```python
def check_for_conflicts(base_branch: str, feature_branch: str, project_root: Path) -> ConflictAnalysis:
    # Dry-run merge to detect conflicts
    result = subprocess.run([
        'git', 'merge', '--no-commit', '--no-ff', feature_branch
    ], cwd=project_root, capture_output=True, text=True)

    if result.returncode != 0 and 'CONFLICT' in result.stdout:
        # Parse conflict information
        conflicts = parse_git_conflicts(result.stdout)
        subprocess.run(['git', 'merge', '--abort'], cwd=project_root)

        return ConflictAnalysis(
            has_conflicts=True,
            conflicting_files=conflicts
        )

    # Abort the dry-run merge
    subprocess.run(['git', 'merge', '--abort'], cwd=project_root)
    return ConflictAnalysis(has_conflicts=False)
```

### User-Assisted Resolution

When conflicts are detected:

1. **Present conflict info** to AI assistant
2. **AI informs user** of conflict
3. **User resolves** manually using standard Git tools (`git mergetool`, editor, etc.)
4. **User commits** resolution
5. **AI continues** work on resolved state

**AIFP does NOT attempt automatic conflict resolution** - Git's tools are sufficient.

---

## Commit Strategy

### When to Commit

AIFP can optionally create commits at key milestones:

- **After completing a task** (`project_task_update` sets status to 'completed')
- **After writing multiple related files** (`project_file_write` batch operation)
- **On user request** ("Save my progress")

### Commit Message Format

```
[AIFP] <action>: <description>

<detailed notes>

Auto-generated by AIFP v1.0
Task ID: <task_id>
```

**Example**:
```
[AIFP] Add function: multiply_matrices

Implemented pure functional matrix multiplication.
- Function: multiply_matrices
- File: src/matrix.py
- Purity level: pure
- Dependencies: validate_matrix_dimensions

Auto-generated by AIFP v1.0
Task ID: 42
```

### Create Commit

```python
def create_aifp_commit(message: str, project_root: Path) -> bool:
    # 1. Stage all AIFP-tracked files
    subprocess.run(['git', 'add', '.'], cwd=project_root)

    # 2. Create commit
    result = subprocess.run([
        'git', 'commit', '-m', message
    ], cwd=project_root, capture_output=True)

    # 3. Update project.db with new hash
    new_hash = get_current_commit_hash(project_root)
    conn.execute("""
        UPDATE git_state SET last_known_hash = ?, last_sync_timestamp = ?
    """, (new_hash, datetime.now()))

    return result.returncode == 0
```

---

## Integration with Directives

### project_init

```python
# During project initialization
if not git_repo_exists(project_root):
    initialize_git_repo(project_root)

# Store initial Git state
store_git_state_in_db(project_root)
```

### project_file_write

```python
# After writing file
write_file(path, content)

# Optionally stage for next commit
if config.auto_stage_files:
    subprocess.run(['git', 'add', path], cwd=project_root)
```

### project_task_update

```python
# When task is completed
update_task_status(task_id, 'completed')

# Optionally create commit
if config.auto_commit_on_task_complete:
    commit_message = generate_commit_message(task_id)
    create_aifp_commit(commit_message, project_root)
```

---

## Configuration

### Git Settings (config.json)

```json
{
  "git": {
    "auto_init": true,
    "auto_stage_files": true,
    "auto_commit_on_task_complete": false,
    "branch_based_workflow": false,
    "default_branch": "main",
    "detect_external_changes_on_boot": true
  }
}
```

---

## Lessons from AIProjectManager

AIFP's Git integration incorporates key lessons from the AIProjectManager branch-based implementation:

### ✅ What We Keep

1. **Branch-based isolation** concept (optional in AIFP)
2. **Git as native storage** (no custom file copying)
3. **Standard Git merge** for conflict resolution (no custom logic)
4. **Clean branch naming** conventions

### ❌ What We Simplify

1. **No complex instance management** (AIProjectManager had 15,000+ lines)
2. **No mandatory branching** (optional in AIFP)
3. **No `.mcp-instances/` directory** (Git branches are sufficient if needed)
4. **No custom conflict resolution system** (use Git's tools)

### Key Insight

**Git is a tool, not a requirement.** AIFP can work perfectly well without Git (all state in `project.db`), but Git integration provides:
- Version control for user's benefit
- External change detection
- Optional branch-based workflow
- Standard collaboration patterns

---

## Summary

AIFP's Git integration:

- **Auto-initializes** Git if needed, or integrates with existing repos
- **Detects external changes** on session boot via commit hash comparison
- **Analyzes theme impact** of external modifications
- **Optionally supports branch-based workflows** (inspired by AIProjectManager)
- **Tracks Git state** in `project.db` for session continuity
- **Provides helper functions** for common Git operations
- **Respects user workflow** (Git is optional, not forced)
- **Uses standard Git tools** for conflict resolution (no custom logic)
- **Commits at milestones** (optional, user-configurable)

This approach balances **AI project management** needs with **standard Git workflows**, avoiding the complexity of custom instance management systems while maintaining the benefits of version control.

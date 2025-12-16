# Git Operations Helper Functions

**Target Database**: project.db
**Purpose**: Version control integration and collaboration

For the master index and design philosophy, see [helpers-consolidated-index.md](helpers-consolidated-index.md)

---

## Git Operations

**Target Database**: project.db
**Purpose**: Version control integration and collaboration

### Git Status & Detection

**`get_current_commit_hash(project_root)`**
- **Purpose**: Get current Git HEAD commit hash
- **Parameters**: `project_root` (String) - Project directory path
- **Returns**: String commit hash or null if Git unavailable
- **Error Handling**: Return null if not Git repository
- **Used By**: git_init, git_sync_state, git_detect_external_changes
- **Classification**: is_tool=false, is_sub_helper=false

**`get_current_branch(project_root)`**
- **Purpose**: Get current Git branch name
- **Parameters**: `project_root` (String)
- **Returns**: String branch name or null
- **Error Handling**: Return null if Git unavailable
- **Used By**: git_create_branch, git_sync_state, status reporting
- **Classification**: is_tool=false, is_sub_helper=false

**`get_git_status(project_root)`**
- **Purpose**: Get comprehensive Git state snapshot (orchestrator)
- **Parameters**: `project_root` (String)
- **Returns**:
  ```json
  {
    "git_available": boolean,
    "current_branch": string,
    "commit_hash": string,
    "uncommitted_changes": boolean,
    "external_changes_detected": boolean
  }
  ```
- **Error Handling**: Returns git_available=false if Git unavailable
- **Used By**: git_sync_state, aifp_status
- **Classification**: is_tool=true, is_sub_helper=false

**`detect_external_changes(project_root)`**
- **Purpose**: Compare current Git HEAD with project.last_known_git_hash
- **Parameters**: `project_root` (String)
- **Returns**:
  ```json
  {
    "changes_detected": boolean,
    "previous_hash": string,
    "current_hash": string,
    "files_changed": [array of file paths]
  }
  ```
- **Error Handling**: Return empty changes if Git unavailable
- **Used By**: git_detect_external_changes, aifp_status
- **Classification**: is_tool=true, is_sub_helper=false

### Branch Management

**`create_user_branch(user, purpose, project_root)`**
- **Purpose**: Create work branch following aifp-{user}-{number} convention
- **Parameters**:
  - `user` (String) - Username
  - `purpose` (String) - Branch purpose description
  - `project_root` (String)
- **Returns**:
  ```json
  {
    "success": boolean,
    "branch_name": "aifp-user-001",
    "branch_number": integer
  }
  ```
- **Error Handling**: Auto-increment number if branch exists
- **Used By**: git_create_branch directive
- **Classification**: is_tool=true, is_sub_helper=false

**`get_user_name_for_branch()`**
- **Purpose**: Detect username from git config/environment/system
- **Parameters**: None
- **Returns**: String username (never null)
- **Error Handling**: Fallback to "user" if all detection fails
- **Note**: Checks git config, then environment, then system user
- **Used By**: git_create_branch directive
- **Classification**: is_tool=false, is_sub_helper=false

**`list_active_branches()`**
- **Purpose**: List all AIFP work branches from work_branches table
- **Parameters**: None
- **Returns**: Array of branch objects with name, created_at, purpose
- **Error Handling**: Return empty array if table doesn't exist
- **Used By**: Status reporting, collaboration coordination
- **Classification**: is_tool=true, is_sub_helper=false

### Conflict Detection & Resolution (Orchestrators)

**`detect_conflicts_before_merge(source_branch, project_root)`**
- **Purpose**: FP-powered conflict analysis before merging (complex orchestrator)
- **Parameters**:
  - `source_branch` (String)
  - `project_root` (String)
- **Returns**:
  ```json
  {
    "conflicts_detected": boolean,
    "file_conflicts": [array],
    "function_conflicts": [array with purity/test data],
    "confidence_scores": object
  }
  ```
- **Error Handling**: Fall back to file-level conflicts if DB query fails
- **Note**: Queries project.db from both branches for FP analysis
- **Used By**: git_detect_conflicts, git_merge_branch
- **Classification**: is_tool=true, is_sub_helper=false

**`merge_with_fp_intelligence(source_branch, project_root)`**
- **Purpose**: Git merge with FP-powered conflict auto-resolution (complex orchestrator)
- **Parameters**:
  - `source_branch` (String)
  - `project_root` (String)
- **Returns**:
  ```json
  {
    "success": boolean,
    "auto_resolved_count": integer,
    "manual_conflicts": [array],
    "merge_aborted": boolean
  }
  ```
- **Error Handling**: Abort merge (git merge --abort) if unresolvable
- **Note**: Auto-resolves conflicts >0.8 confidence using purity rules
- **Used By**: git_merge_branch directive
- **Classification**: is_tool=true, is_sub_helper=false

### Git State Synchronization

**`sync_git_state(project_root)`**
- **Purpose**: Update project.last_known_git_hash with current Git HEAD
- **Parameters**: `project_root` (String)
- **Returns**:
  ```json
  {
    "success": boolean,
    "updated_hash": string,
    "previous_hash": string
  }
  ```
- **Error Handling**: Log warning if Git unavailable, continue with cached
- **Note**: Called after commits and during session boot
- **Used By**: git_sync_state directive, aifp_status
- **Classification**: is_tool=true, is_sub_helper=false

**`project_update_git_status()`**
- **Purpose**: Update last_known_git_hash and last_git_sync in project table
- **Parameters**: None (gets git data automatically)
- **Returns**: `{"success": true, "hash": string, "sync_time": timestamp}`
- **Note**: Convenience wrapper for common sync operation
- **Classification**: is_tool=false, is_sub_helper=false

---

**End of Git Operations Helper Functions**

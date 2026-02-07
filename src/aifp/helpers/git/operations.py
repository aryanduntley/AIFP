"""
AIFP Helper Functions - Git Operations

Git state management and branch operations for project tracking.

Helpers in this file:
- get_current_commit_hash: Get current Git HEAD commit hash
- get_current_branch: Get current Git branch name
- get_git_status: Get comprehensive Git state snapshot
- detect_external_changes: Compare current HEAD with stored hash
- create_user_branch: Create work branch with aifp-{user}-{number} convention
- get_user_name_for_branch: Detect username from git/env/system (sub-helper)
- list_active_branches: List all AIFP work branches
- detect_conflicts_before_merge: Dry-run merge analysis
- execute_merge: Execute git merge and return result
- sync_git_state: Update project.last_known_git_hash
- project_update_git_status: Update git hash/timestamp in project table (sub-helper)

All functions follow FP principles:
- Pure functions where possible
- Effects clearly isolated (subprocess calls, database operations)
- Immutable data structures (frozen dataclasses)
- Explicit parameters
"""

import os
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple

from ..utils import (
    get_project_db_path,
    get_return_statements,
    _open_connection,
    database_exists,
)


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class GitHashResult:
    """Result of commit hash query."""
    success: bool
    hash: Optional[str] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class GitBranchResult:
    """Result of branch query."""
    success: bool
    branch: Optional[str] = None
    is_detached: bool = False
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class GitStatusResult:
    """Result of comprehensive git status query."""
    success: bool
    git_available: bool = False
    branch: Optional[str] = None
    commit_hash: Optional[str] = None
    remote_tracking: Optional[str] = None
    ahead: int = 0
    behind: int = 0
    staged_files: Tuple[str, ...] = ()
    unstaged_files: Tuple[str, ...] = ()
    untracked_files: Tuple[str, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ExternalChangesResult:
    """Result of external changes detection."""
    success: bool
    hash_changed: bool = False
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    changed_files: Tuple[str, ...] = ()
    affected_file_ids: Tuple[int, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class CreateBranchResult:
    """Result of branch creation."""
    success: bool
    branch_name: Optional[str] = None
    user: Optional[str] = None
    purpose: Optional[str] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkBranchRecord:
    """Work branch record from database."""
    id: int
    branch_name: str
    user_name: str
    purpose: str
    status: str
    created_at: str
    created_from: str
    merged_at: Optional[str] = None


@dataclass(frozen=True)
class ListBranchesResult:
    """Result of listing work branches."""
    success: bool
    branches: Tuple[WorkBranchRecord, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ConflictCheckResult:
    """Result of conflict detection."""
    success: bool
    would_conflict: bool = False
    conflicting_files: Tuple[str, ...] = ()
    affected_file_ids: Tuple[int, ...] = ()
    affected_function_ids: Tuple[int, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class MergeResult:
    """Result of merge execution."""
    success: bool
    merged: bool = False
    conflicts: bool = False
    conflict_files: Tuple[str, ...] = ()
    commit_hash: Optional[str] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SyncResult:
    """Result of git state sync."""
    success: bool
    hash_synced: bool = False
    external_changes_detected: bool = False
    current_branch: Optional[str] = None
    commit_hash: Optional[str] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class UpdateGitStatusResult:
    """Result of updating git status in project table."""
    success: bool
    hash: Optional[str] = None
    sync_time: Optional[str] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


# ============================================================================
# Effect Functions (Git Commands)
# ============================================================================

def _run_git_command(
    project_root: str,
    args: Tuple[str, ...],
    check: bool = False
) -> Tuple[bool, str, str]:
    """
    Effect: Run a git command in the project directory.

    Args:
        project_root: Project directory path
        args: Git command arguments (e.g., ('rev-parse', 'HEAD'))
        check: Whether to raise on non-zero exit

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ['git'] + list(args),
            cwd=project_root,
            capture_output=True,
            text=True,
            check=check
        )
        return (True, result.stdout.strip(), result.stderr.strip())
    except subprocess.CalledProcessError as e:
        return (False, e.stdout.strip() if e.stdout else '', e.stderr.strip() if e.stderr else '')
    except FileNotFoundError:
        return (False, '', 'git command not found')
    except Exception as e:
        return (False, '', str(e))


def _is_git_repository(project_root: str) -> bool:
    """
    Effect: Check if directory is a git repository.

    Args:
        project_root: Project directory path

    Returns:
        True if git repository, False otherwise
    """
    success, _, _ = _run_git_command(project_root, ('rev-parse', '--git-dir'))
    return success


# ============================================================================
# Public API Functions
# ============================================================================

def get_current_commit_hash(project_root: str) -> GitHashResult:
    """
    Get current Git HEAD commit hash.

    Args:
        project_root: Project directory path

    Returns:
        GitHashResult with 40-char SHA-1 hash or error

    Example:
        >>> result = get_current_commit_hash("/path/to/project")
        >>> result.hash
        'abc123def456...'
    """
    if not _is_git_repository(project_root):
        return GitHashResult(success=False, error="Not a git repository")

    success, stdout, stderr = _run_git_command(project_root, ('rev-parse', 'HEAD'))

    if not success:
        return GitHashResult(success=False, error=stderr or "Failed to get commit hash")

    return_statements = get_return_statements("get_current_commit_hash")

    return GitHashResult(
        success=True,
        hash=stdout,
        return_statements=return_statements
    )


def get_current_branch(project_root: str) -> GitBranchResult:
    """
    Get current Git branch name.

    Args:
        project_root: Project directory path

    Returns:
        GitBranchResult with branch name or commit hash if detached

    Example:
        >>> result = get_current_branch("/path/to/project")
        >>> result.branch
        'main'
    """
    if not _is_git_repository(project_root):
        return GitBranchResult(success=False, error="Not a git repository")

    success, stdout, stderr = _run_git_command(project_root, ('branch', '--show-current'))

    if not success:
        return GitBranchResult(success=False, error=stderr or "Failed to get branch")

    # Empty output means detached HEAD
    if not stdout:
        hash_result = get_current_commit_hash(project_root)
        if hash_result.success:
            return GitBranchResult(
                success=True,
                branch=hash_result.hash[:7] if hash_result.hash else None,
                is_detached=True
            )
        return GitBranchResult(success=False, error="Detached HEAD, unable to get hash")

    return_statements = get_return_statements("get_current_branch")

    return GitBranchResult(
        success=True,
        branch=stdout,
        is_detached=False,
        return_statements=return_statements
    )


def get_git_status(project_root: str) -> GitStatusResult:
    """
    Get comprehensive Git state snapshot.

    Combines multiple git commands into single status object.

    Args:
        project_root: Project directory path

    Returns:
        GitStatusResult with branch, hash, file statuses, ahead/behind counts

    Example:
        >>> result = get_git_status("/path/to/project")
        >>> result.branch
        'main'
        >>> result.staged_files
        ('file1.py', 'file2.py')
    """
    if not _is_git_repository(project_root):
        return GitStatusResult(success=True, git_available=False)

    # Get branch
    branch_result = get_current_branch(project_root)
    branch = branch_result.branch if branch_result.success else None
    is_detached = branch_result.is_detached if branch_result.success else False

    # Get commit hash
    hash_result = get_current_commit_hash(project_root)
    commit_hash = hash_result.hash if hash_result.success else None

    # Get remote tracking and ahead/behind
    remote_tracking = None
    ahead = 0
    behind = 0

    if branch and not is_detached:
        # Get remote tracking branch
        success, stdout, _ = _run_git_command(
            project_root,
            ('rev-parse', '--abbrev-ref', f'{branch}@{{upstream}}')
        )
        if success:
            remote_tracking = stdout

            # Get ahead/behind counts
            success, stdout, _ = _run_git_command(
                project_root,
                ('rev-list', '--left-right', '--count', f'{branch}...{remote_tracking}')
            )
            if success and stdout:
                parts = stdout.split()
                if len(parts) == 2:
                    ahead = int(parts[0])
                    behind = int(parts[1])

    # Get file statuses using porcelain format
    staged_files = []
    unstaged_files = []
    untracked_files = []

    success, stdout, _ = _run_git_command(project_root, ('status', '--porcelain'))
    if success and stdout:
        for line in stdout.split('\n'):
            if len(line) < 3:
                continue
            index_status = line[0]
            worktree_status = line[1]
            filename = line[3:]

            if index_status == '?':
                untracked_files.append(filename)
            elif index_status != ' ':
                staged_files.append(filename)
            if worktree_status != ' ' and worktree_status != '?':
                unstaged_files.append(filename)

    return_statements = get_return_statements("get_git_status")

    return GitStatusResult(
        success=True,
        git_available=True,
        branch=branch,
        commit_hash=commit_hash,
        remote_tracking=remote_tracking,
        ahead=ahead,
        behind=behind,
        staged_files=tuple(staged_files),
        unstaged_files=tuple(unstaged_files),
        untracked_files=tuple(untracked_files),
        return_statements=return_statements
    )


def detect_external_changes(project_root: str) -> ExternalChangesResult:
    """
    Compare current Git HEAD with project.last_known_git_hash.

    Detects if external changes (commits outside AIFP) occurred.

    Args:
        project_root: Project directory path

    Returns:
        ExternalChangesResult with changed files and affected entities

    Example:
        >>> result = detect_external_changes("/path/to/project")
        >>> result.hash_changed
        True
        >>> result.changed_files
        ('src/main.py', 'src/utils.py')
    """
    if not _is_git_repository(project_root):
        return ExternalChangesResult(success=False, error="Not a git repository")

    # Get current hash
    hash_result = get_current_commit_hash(project_root)
    if not hash_result.success:
        return ExternalChangesResult(success=False, error=hash_result.error)

    new_hash = hash_result.hash

    # Get stored hash from project database
    db_path = get_project_db_path(project_root)
    if not database_exists(db_path):
        return ExternalChangesResult(
            success=True,
            hash_changed=False,
            new_hash=new_hash,
            error="Project database not found"
        )

    try:
        conn = _open_connection(db_path)
        try:
            cursor = conn.execute("SELECT last_known_git_hash FROM project LIMIT 1")
            row = cursor.fetchone()
            old_hash = row['last_known_git_hash'] if row else None
        finally:
            conn.close()
    except Exception as e:
        return ExternalChangesResult(success=False, error=f"Database error: {str(e)}")

    # Compare hashes
    if old_hash is None or old_hash == new_hash:
        return ExternalChangesResult(
            success=True,
            hash_changed=False,
            old_hash=old_hash,
            new_hash=new_hash
        )

    # Get changed files between commits
    success, stdout, stderr = _run_git_command(
        project_root,
        ('diff', '--name-only', f'{old_hash}...{new_hash}')
    )

    changed_files = tuple(stdout.split('\n')) if success and stdout else ()

    # Query database for affected file IDs
    affected_file_ids = ()
    if changed_files:
        try:
            conn = _open_connection(db_path)
            try:
                placeholders = ','.join('?' * len(changed_files))
                cursor = conn.execute(
                    f"SELECT id FROM files WHERE path IN ({placeholders})",
                    changed_files
                )
                affected_file_ids = tuple(row['id'] for row in cursor.fetchall())
            finally:
                conn.close()
        except Exception:
            pass  # Continue without file IDs

    return_statements = get_return_statements("detect_external_changes")

    return ExternalChangesResult(
        success=True,
        hash_changed=True,
        old_hash=old_hash,
        new_hash=new_hash,
        changed_files=changed_files,
        affected_file_ids=affected_file_ids,
        return_statements=return_statements
    )


def get_user_name_for_branch() -> str:
    """
    Detect username from git config/environment/system.

    Sub-helper for branch naming.

    Returns:
        Username string (never None - falls back to 'user')

    Example:
        >>> get_user_name_for_branch()
        'alice'
    """
    # Try git config user.name
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            # Sanitize for branch name (lowercase, replace spaces)
            name = result.stdout.strip().lower().replace(' ', '-')
            # Keep only alphanumeric and hyphens
            name = ''.join(c for c in name if c.isalnum() or c == '-')
            if name:
                return name
    except Exception:
        pass

    # Try environment variables
    for var in ('USER', 'USERNAME', 'LOGNAME'):
        name = os.environ.get(var)
        if name:
            return name.lower()

    # Try os.getlogin()
    try:
        name = os.getlogin()
        if name:
            return name.lower()
    except Exception:
        pass

    # Fallback
    return 'user'


def create_user_branch(user: str, purpose: str, project_root: str) -> CreateBranchResult:
    """
    Create work branch following aifp-{user}-{number} convention.

    Args:
        user: Username for branch naming
        purpose: Branch purpose description
        project_root: Project directory path

    Returns:
        CreateBranchResult with branch name and metadata

    Example:
        >>> result = create_user_branch("alice", "implement auth", "/path/to/project")
        >>> result.branch_name
        'aifp-alice-001'
    """
    if not _is_git_repository(project_root):
        return CreateBranchResult(success=False, error="Not a git repository")

    db_path = get_project_db_path(project_root)
    if not database_exists(db_path):
        return CreateBranchResult(success=False, error="Project database not found")

    # Get next branch number for this user
    try:
        conn = _open_connection(db_path)
        try:
            cursor = conn.execute(
                """
                SELECT MAX(CAST(SUBSTR(branch_name, -3) AS INTEGER)) as max_num
                FROM work_branches
                WHERE user_name = ?
                """,
                (user,)
            )
            row = cursor.fetchone()
            next_num = (row['max_num'] or 0) + 1 if row and row['max_num'] else 1
        finally:
            conn.close()
    except Exception as e:
        return CreateBranchResult(success=False, error=f"Database error: {str(e)}")

    # Format branch name
    branch_name = f"aifp-{user}-{next_num:03d}"

    # Create git branch from main (or current branch if main doesn't exist)
    success, _, stderr = _run_git_command(
        project_root,
        ('checkout', '-b', branch_name, 'main')
    )

    if not success:
        # Try from current branch
        success, _, stderr = _run_git_command(
            project_root,
            ('checkout', '-b', branch_name)
        )
        if not success:
            return CreateBranchResult(success=False, error=stderr or "Failed to create branch")

    # Get created_from branch
    created_from = 'main'
    branch_result = get_current_branch(project_root)
    if branch_result.success and branch_result.branch != branch_name:
        created_from = branch_result.branch or 'main'

    # Insert into work_branches table
    try:
        conn = _open_connection(db_path)
        try:
            conn.execute(
                """
                INSERT INTO work_branches (branch_name, user_name, purpose, status, created_from)
                VALUES (?, ?, ?, 'active', ?)
                """,
                (branch_name, user, purpose, created_from)
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as e:
        return CreateBranchResult(success=False, error=f"Database insert failed: {str(e)}")

    return_statements = get_return_statements("create_user_branch")

    return CreateBranchResult(
        success=True,
        branch_name=branch_name,
        user=user,
        purpose=purpose,
        return_statements=return_statements
    )


def list_active_branches(project_root: str) -> ListBranchesResult:
    """
    List all AIFP work branches from work_branches table.

    Args:
        project_root: Project directory path

    Returns:
        ListBranchesResult with branch records

    Example:
        >>> result = list_active_branches("/path/to/project")
        >>> result.branches[0].branch_name
        'aifp-alice-001'
    """
    db_path = get_project_db_path(project_root)
    if not database_exists(db_path):
        return ListBranchesResult(success=True, branches=())

    try:
        conn = _open_connection(db_path)
        try:
            cursor = conn.execute(
                """
                SELECT id, branch_name, user_name, purpose, status,
                       created_at, created_from, merged_at
                FROM work_branches
                ORDER BY created_at DESC
                """
            )
            branches = tuple(
                WorkBranchRecord(
                    id=row['id'],
                    branch_name=row['branch_name'],
                    user_name=row['user_name'],
                    purpose=row['purpose'],
                    status=row['status'],
                    created_at=row['created_at'],
                    created_from=row['created_from'],
                    merged_at=row['merged_at']
                )
                for row in cursor.fetchall()
            )
        finally:
            conn.close()
    except Exception as e:
        return ListBranchesResult(success=False, error=f"Database error: {str(e)}")

    return_statements = get_return_statements("list_active_branches")

    return ListBranchesResult(
        success=True,
        branches=branches,
        return_statements=return_statements
    )


def detect_conflicts_before_merge(
    source_branch: str,
    project_root: str
) -> ConflictCheckResult:
    """
    Dry-run merge analysis - retrieves potential conflict data.

    Performs non-destructive merge check and returns conflict information.

    Args:
        source_branch: Branch to merge from
        project_root: Project directory path

    Returns:
        ConflictCheckResult with conflict data for AI to evaluate

    Example:
        >>> result = detect_conflicts_before_merge("feature-branch", "/path/to/project")
        >>> result.would_conflict
        True
        >>> result.conflicting_files
        ('src/main.py',)
    """
    if not _is_git_repository(project_root):
        return ConflictCheckResult(success=False, error="Not a git repository")

    # Attempt dry-run merge
    success, stdout, stderr = _run_git_command(
        project_root,
        ('merge', '--no-commit', '--no-ff', source_branch)
    )

    conflicting_files = ()

    if not success:
        # Merge failed - likely conflicts
        # Parse conflict files from stderr or status
        success_status, status_out, _ = _run_git_command(
            project_root,
            ('status', '--porcelain')
        )
        if success_status:
            conflicts = []
            for line in status_out.split('\n'):
                if line.startswith('UU ') or line.startswith('AA ') or line.startswith('DD '):
                    conflicts.append(line[3:])
            conflicting_files = tuple(conflicts)

    # Abort the merge regardless of result
    _run_git_command(project_root, ('merge', '--abort'))

    # Query database for affected entities
    affected_file_ids = ()
    affected_function_ids = ()

    if conflicting_files:
        db_path = get_project_db_path(project_root)
        if database_exists(db_path):
            try:
                conn = _open_connection(db_path)
                try:
                    placeholders = ','.join('?' * len(conflicting_files))

                    # Get file IDs
                    cursor = conn.execute(
                        f"SELECT id FROM files WHERE path IN ({placeholders})",
                        conflicting_files
                    )
                    affected_file_ids = tuple(row['id'] for row in cursor.fetchall())

                    # Get function IDs
                    if affected_file_ids:
                        file_placeholders = ','.join('?' * len(affected_file_ids))
                        cursor = conn.execute(
                            f"SELECT id FROM functions WHERE file_id IN ({file_placeholders})",
                            affected_file_ids
                        )
                        affected_function_ids = tuple(row['id'] for row in cursor.fetchall())
                finally:
                    conn.close()
            except Exception:
                pass

    return_statements = get_return_statements("detect_conflicts_before_merge")

    return ConflictCheckResult(
        success=True,
        would_conflict=len(conflicting_files) > 0,
        conflicting_files=conflicting_files,
        affected_file_ids=affected_file_ids,
        affected_function_ids=affected_function_ids,
        return_statements=return_statements
    )


def execute_merge(source_branch: str, project_root: str) -> MergeResult:
    """
    Execute git merge and return result.

    Does NOT auto-resolve conflicts - returns conflict data for AI to handle.

    Args:
        source_branch: Branch to merge from
        project_root: Project directory path

    Returns:
        MergeResult with merge outcome and any conflict files

    Example:
        >>> result = execute_merge("feature-branch", "/path/to/project")
        >>> result.merged
        True
        >>> result.commit_hash
        'abc123...'
    """
    if not _is_git_repository(project_root):
        return MergeResult(success=False, error="Not a git repository")

    # Execute merge
    success, stdout, stderr = _run_git_command(
        project_root,
        ('merge', source_branch)
    )

    if success:
        # Merge succeeded - get new commit hash
        hash_result = get_current_commit_hash(project_root)

        # Update work_branches table
        db_path = get_project_db_path(project_root)
        if database_exists(db_path):
            try:
                conn = _open_connection(db_path)
                try:
                    conn.execute(
                        """
                        UPDATE work_branches
                        SET status = 'merged', merged_at = CURRENT_TIMESTAMP
                        WHERE branch_name = ?
                        """,
                        (source_branch,)
                    )
                    conn.commit()
                finally:
                    conn.close()
            except Exception:
                pass  # Non-fatal

        return_statements = get_return_statements("execute_merge")

        return MergeResult(
            success=True,
            merged=True,
            conflicts=False,
            commit_hash=hash_result.hash if hash_result.success else None,
            return_statements=return_statements
        )

    # Merge failed - check for conflicts
    success_status, status_out, _ = _run_git_command(
        project_root,
        ('status', '--porcelain')
    )

    conflict_files = []
    if success_status:
        for line in status_out.split('\n'):
            if line.startswith('UU ') or line.startswith('AA ') or line.startswith('DD '):
                conflict_files.append(line[3:])

    if conflict_files:
        return MergeResult(
            success=True,
            merged=False,
            conflicts=True,
            conflict_files=tuple(conflict_files)
        )

    # Some other merge failure
    return MergeResult(success=False, error=stderr or "Merge failed")


def project_update_git_status(project_root: str) -> UpdateGitStatusResult:
    """
    Update last_known_git_hash and last_git_sync in project table.

    Sub-helper for git state synchronization.

    Args:
        project_root: Project directory path

    Returns:
        UpdateGitStatusResult with updated values

    Example:
        >>> result = project_update_git_status("/path/to/project")
        >>> result.hash
        'abc123...'
    """
    # Get current hash
    hash_result = get_current_commit_hash(project_root)
    if not hash_result.success:
        return UpdateGitStatusResult(success=False, error=hash_result.error)

    db_path = get_project_db_path(project_root)
    if not database_exists(db_path):
        return UpdateGitStatusResult(success=False, error="Project database not found")

    try:
        conn = _open_connection(db_path)
        try:
            conn.execute(
                """
                UPDATE project
                SET last_known_git_hash = ?, last_git_sync = CURRENT_TIMESTAMP
                """,
                (hash_result.hash,)
            )
            conn.commit()

            # Get sync time
            cursor = conn.execute("SELECT last_git_sync FROM project LIMIT 1")
            row = cursor.fetchone()
            sync_time = row['last_git_sync'] if row else None
        finally:
            conn.close()
    except Exception as e:
        return UpdateGitStatusResult(success=False, error=f"Database error: {str(e)}")

    return_statements = get_return_statements("project_update_git_status")

    return UpdateGitStatusResult(
        success=True,
        hash=hash_result.hash,
        sync_time=sync_time,
        return_statements=return_statements
    )


def sync_git_state(project_root: str) -> SyncResult:
    """
    Update project.last_known_git_hash with current Git HEAD.

    Detects external changes if hash differs from stored value.

    Args:
        project_root: Project directory path

    Returns:
        SyncResult with sync status and any detected changes

    Example:
        >>> result = sync_git_state("/path/to/project")
        >>> result.hash_synced
        True
        >>> result.external_changes_detected
        False
    """
    if not _is_git_repository(project_root):
        return SyncResult(success=False, error="Not a git repository")

    # Check for external changes first
    changes_result = detect_external_changes(project_root)

    external_changes = False
    if changes_result.success and changes_result.hash_changed:
        external_changes = True

    # Update git status in project table
    update_result = project_update_git_status(project_root)
    if not update_result.success:
        return SyncResult(success=False, error=update_result.error)

    # Get current branch
    branch_result = get_current_branch(project_root)

    return_statements = get_return_statements("sync_git_state")

    return SyncResult(
        success=True,
        hash_synced=True,
        external_changes_detected=external_changes,
        current_branch=branch_result.branch if branch_result.success else None,
        commit_hash=update_result.hash,
        return_statements=return_statements
    )

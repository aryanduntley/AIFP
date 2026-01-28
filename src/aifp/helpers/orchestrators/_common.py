"""
AIFP Helper Functions - Orchestrators Common Utilities

Shared utilities used across orchestrator helper files.

This is the CATEGORY level of the DRY hierarchy:

    utils.py (global)                   <- Database-agnostic shared code
        └── orchestrators/_common.py    <- THIS FILE: Orchestrator-specific shared code
            └── orchestrators/{file}.py <- Individual orchestrator helpers

Orchestrator characteristics:
- Aggregate data from multiple tables (and sometimes multiple databases)
- Return structured data for AI to interpret — NO decision logic
- Entry points (aifp_init, aifp_run, aifp_status) coordinate across databases
- Status/query helpers work within project.db only

Common utilities (orchestrator-specific):
- Result types for orchestrator operations
- Shared constants (expected table counts, infrastructure entries)
- Connection helpers for multi-database access

Imported from utils.py (global):
- _open_connection: Database connection with row factory
- Database path resolution functions
- Return statements fetching
- Row conversion utilities
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, Final

# Import global utilities (DRY - avoid duplication)
from ..utils import (
    _open_connection,
    _close_connection,
    get_core_db_path,
    get_project_db_path,
    get_user_preferences_db_path,
    get_user_directives_db_path,
    get_aifp_project_dir,
    get_return_statements,
    database_exists,
    _get_table_names,
    row_to_dict,
    rows_to_tuple,
    parse_json_field,
    json_to_tuple,
    Result,
    QueryResult,
    AIFP_PROJECT_DIR,
    CORE_DB_NAME,
    PROJECT_DB_NAME,
    USER_PREFERENCES_DB_NAME,
    USER_DIRECTIVES_DB_NAME,
)

# Re-export for convenience — orchestrator files import from _common only
__all__ = [
    # Global utilities
    '_open_connection',
    '_close_connection',
    'get_core_db_path',
    'get_project_db_path',
    'get_user_preferences_db_path',
    'get_user_directives_db_path',
    'get_aifp_project_dir',
    'get_return_statements',
    'database_exists',
    '_get_table_names',
    'row_to_dict',
    'rows_to_tuple',
    'parse_json_field',
    'json_to_tuple',
    'Result',
    'QueryResult',
    # Constants
    'AIFP_PROJECT_DIR',
    'CORE_DB_NAME',
    'PROJECT_DB_NAME',
    'USER_PREFERENCES_DB_NAME',
    'USER_DIRECTIVES_DB_NAME',
    'BLUEPRINT_FILENAME',
    'BACKUPS_DIR_NAME',
    # Orchestrator-specific
    '_open_project_connection',
    '_open_preferences_connection',
    '_open_directives_connection',
]


# ============================================================================
# Orchestrator Constants
# ============================================================================

# File/directory names within .aifp-project/
BLUEPRINT_FILENAME: Final[str] = "ProjectBlueprint.md"
BACKUPS_DIR_NAME: Final[str] = "backups"

# Valid status type parameters for orchestrators
VALID_STATUS_TYPES: Final[frozenset[str]] = frozenset([
    'quick', 'summary', 'detailed'
])

# Valid work item types
VALID_WORK_ITEM_TYPES: Final[frozenset[str]] = frozenset([
    'task', 'subtask', 'sidequest'
])

# Work item type to table name mapping
WORK_ITEM_TABLE_MAP: Final[Dict[str, str]] = {
    'task': 'tasks',
    'subtask': 'subtasks',
    'sidequest': 'sidequests',
}

# Valid actions for update_project_state
VALID_STATE_ACTIONS: Final[frozenset[str]] = frozenset([
    'start_task', 'complete_task', 'pause_task', 'resume_task',
    'block_task', 'unblock_task',
    'start_subtask', 'complete_subtask', 'pause_subtask', 'resume_subtask',
    'block_subtask', 'unblock_subtask',
    'start_sidequest', 'complete_sidequest', 'pause_sidequest', 'resume_sidequest',
    'start_milestone', 'complete_milestone',
    'start_path', 'complete_path',
])

# Action to status mapping
ACTION_STATUS_MAP: Final[Dict[str, str]] = {
    'start_task': 'in_progress',
    'complete_task': 'completed',
    'pause_task': 'paused',
    'resume_task': 'in_progress',
    'block_task': 'blocked',
    'unblock_task': 'in_progress',
    'start_subtask': 'in_progress',
    'complete_subtask': 'completed',
    'pause_subtask': 'paused',
    'resume_subtask': 'in_progress',
    'block_subtask': 'blocked',
    'unblock_subtask': 'in_progress',
    'start_sidequest': 'in_progress',
    'complete_sidequest': 'completed',
    'pause_sidequest': 'paused',
    'resume_sidequest': 'in_progress',
    'start_milestone': 'in_progress',
    'complete_milestone': 'completed',
    'start_path': 'in_progress',
    'complete_path': 'completed',
}

# Action to target_type mapping (extract entity type from action name)
ACTION_TARGET_MAP: Final[Dict[str, str]] = {
    'start_task': 'tasks', 'complete_task': 'tasks',
    'pause_task': 'tasks', 'resume_task': 'tasks',
    'block_task': 'tasks', 'unblock_task': 'tasks',
    'start_subtask': 'subtasks', 'complete_subtask': 'subtasks',
    'pause_subtask': 'subtasks', 'resume_subtask': 'subtasks',
    'block_subtask': 'subtasks', 'unblock_subtask': 'subtasks',
    'start_sidequest': 'sidequests', 'complete_sidequest': 'sidequests',
    'pause_sidequest': 'sidequests', 'resume_sidequest': 'sidequests',
    'start_milestone': 'milestones', 'complete_milestone': 'milestones',
    'start_path': 'completion_path', 'complete_path': 'completion_path',
}

# Valid entity types for query_project_state
VALID_QUERY_ENTITIES: Final[frozenset[str]] = frozenset([
    'tasks', 'subtasks', 'sidequests', 'milestones', 'completion_path',
    'files', 'functions', 'types', 'interactions',
    'themes', 'flows', 'items', 'notes',
    'infrastructure', 'work_branches', 'merge_history',
])

# Predefined JOIN mappings for query_project_state
JOIN_MAPPINGS: Final[Dict[str, Dict[str, str]]] = {
    'tasks': {
        'milestones': 'LEFT JOIN milestones ON tasks.milestone_id = milestones.id',
    },
    'subtasks': {
        'tasks': 'LEFT JOIN tasks ON subtasks.task_id = tasks.id',
    },
    'milestones': {
        'completion_path': 'LEFT JOIN completion_path ON milestones.completion_path_id = completion_path.id',
    },
    'functions': {
        'files': 'LEFT JOIN files ON functions.file_id = files.id',
    },
    'items': {
        'tasks': 'LEFT JOIN tasks ON items.task_id = tasks.id',
        'subtasks': 'LEFT JOIN subtasks ON items.subtask_id = subtasks.id',
        'sidequests': 'LEFT JOIN sidequests ON items.sidequest_id = sidequests.id',
    },
}

# Valid scope values for get_current_progress
VALID_PROGRESS_SCOPES: Final[frozenset[str]] = frozenset([
    'tasks', 'milestones', 'completion_paths', 'files', 'functions',
    'flows', 'themes', 'infrastructure', 'all',
])


# ============================================================================
# Database Connection Helpers
# ============================================================================

def _open_project_connection(project_root: str) -> sqlite3.Connection:
    """
    Effect: Open connection to project.db.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Database connection with row factory configured

    Raises:
        FileNotFoundError: If project.db does not exist
    """
    db_path = get_project_db_path(project_root)

    if not database_exists(db_path):
        raise FileNotFoundError(f"Project database not found: {db_path}")

    return _open_connection(db_path)


def _open_preferences_connection(project_root: str) -> sqlite3.Connection:
    """
    Effect: Open connection to user_preferences.db.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Database connection with row factory configured

    Raises:
        FileNotFoundError: If user_preferences.db does not exist
    """
    db_path = get_user_preferences_db_path(project_root)

    if not database_exists(db_path):
        raise FileNotFoundError(f"User preferences database not found: {db_path}")

    return _open_connection(db_path)


def _open_directives_connection(project_root: str) -> sqlite3.Connection:
    """
    Effect: Open connection to user_directives.db.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Database connection with row factory configured

    Raises:
        FileNotFoundError: If user_directives.db does not exist
    """
    db_path = get_user_directives_db_path(project_root)

    if not database_exists(db_path):
        raise FileNotFoundError(f"User directives database not found: {db_path}")

    return _open_connection(db_path)

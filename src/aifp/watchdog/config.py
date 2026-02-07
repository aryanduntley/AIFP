"""
AIFP Watchdog - Configuration Constants

Exclusion patterns, function detection patterns, paths, and timing constants.
All values are immutable (Final + frozenset).
"""

import os
import re
from typing import Final, Optional, Pattern

from ..database.connection import (
    AIFP_PROJECT_DIR,
    get_project_db_path as _foundation_get_project_db_path,
    get_user_preferences_db_path as _foundation_get_preferences_db_path,
)


# ============================================================================
# Timing
# ============================================================================

DEBOUNCE_SECONDS: Final[float] = 2.0


# ============================================================================
# Directory / File Names (watchdog-specific)
# ============================================================================

WATCHDOG_DIR_NAME: Final[str] = "watchdog"
REMINDERS_FILE: Final[str] = "reminders.json"
PID_FILE: Final[str] = "watchdog.pid"


# ============================================================================
# Exclusion Patterns (Hardcoded Defaults)
# ============================================================================

EXCLUDED_DIRS: Final[frozenset[str]] = frozenset([
    'node_modules',
    'venv',
    '.venv',
    'env',
    '.env',
    '__pycache__',
    '.git',
    '.svn',
    '.hg',
    'target',
    'build',
    'dist',
    '.tox',
    '.mypy_cache',
    '.pytest_cache',
    'vendor',
    '.next',
    '.nuxt',
    'coverage',
    '.coverage',
    'htmlcov',
    '.aifp-project',
])

EXCLUDED_EXTENSIONS: Final[frozenset[str]] = frozenset([
    '.pyc', '.pyo', '.so', '.dll', '.dylib',
    '.class', '.o', '.obj', '.exe',
    '.lock', '.log',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot',
    '.zip', '.tar', '.gz', '.bz2',
])


# ============================================================================
# Function Detection Patterns (per language)
# ============================================================================

FUNCTION_PATTERNS: Final[dict[str, str]] = {
    'python': r'^\s*def\s+(\w+)\s*\(',
    'javascript': r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
    'typescript': r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
    'rust': r'(?:pub\s+)?(?:async\s+)?fn\s+(\w+)',
    'go': r'func\s+(?:\([^)]+\)\s+)?(\w+)',
    'java': r'(?:public|private|protected)?\s*(?:static\s+)?(?:\w+\s+)+(\w+)\s*\(',
}


# ============================================================================
# Reminder Type Constants
# ============================================================================

REMINDER_TIMESTAMP_SYNCED: Final[str] = "timestamp_synced"
REMINDER_NEW_FILE: Final[str] = "new_file_detected"
REMINDER_MISSING_FUNCTION: Final[str] = "missing_function"
REMINDER_MISSING_DB_FUNCTION: Final[str] = "missing_db_function"
REMINDER_FILE_DELETED: Final[str] = "file_deleted"

SEVERITY_INFO: Final[str] = "info"
SEVERITY_WARNING: Final[str] = "warning"


# ============================================================================
# Pure Functions
# ============================================================================

def get_watchdog_dir(project_root: str) -> str:
    """Pure: Get path to .aifp-project/watchdog/ directory."""
    return os.path.join(project_root, AIFP_PROJECT_DIR, WATCHDOG_DIR_NAME)


def get_reminders_path(project_root: str) -> str:
    """Pure: Get path to reminders.json."""
    return os.path.join(get_watchdog_dir(project_root), REMINDERS_FILE)


def get_pid_path(project_root: str) -> str:
    """Pure: Get path to watchdog.pid."""
    return os.path.join(get_watchdog_dir(project_root), PID_FILE)


def get_project_db_path(project_root: str) -> str:
    """Pure: Get path to project.db (delegates to foundation layer)."""
    return _foundation_get_project_db_path(project_root)


def get_preferences_db_path(project_root: str) -> str:
    """Pure: Get path to user_preferences.db (delegates to foundation layer)."""
    return _foundation_get_preferences_db_path(project_root)


def build_exclusion_sets(
    user_excluded_dirs: tuple[str, ...] = (),
    user_excluded_extensions: tuple[str, ...] = (),
) -> tuple[frozenset[str], frozenset[str]]:
    """
    Pure: Merge hardcoded exclusions with user-provided ones.

    Returns:
        (excluded_dirs, excluded_extensions) as frozensets
    """
    merged_dirs = EXCLUDED_DIRS | frozenset(user_excluded_dirs)
    merged_exts = EXCLUDED_EXTENSIONS | frozenset(user_excluded_extensions)
    return (merged_dirs, merged_exts)


def get_function_pattern(language: str) -> Optional[Pattern[str]]:
    """
    Pure: Get compiled regex pattern for detecting functions in given language.

    Returns None if language not supported.
    """
    raw = FUNCTION_PATTERNS.get(language.lower())
    if raw is None:
        return None
    return re.compile(raw, re.MULTILINE)


def should_exclude(
    file_path: str,
    excluded_dirs: frozenset[str],
    excluded_extensions: frozenset[str],
) -> bool:
    """
    Pure: Determine if a file path should be excluded from watching.

    Checks both directory components and file extension.
    """
    parts = file_path.replace('\\', '/').split('/')
    for part in parts:
        if part in excluded_dirs:
            return True

    _, ext = os.path.splitext(file_path)
    if ext.lower() in excluded_extensions:
        return True

    return False


def get_relative_path(file_path: str, source_dir: str) -> str:
    """Pure: Get path relative to source directory."""
    return os.path.relpath(file_path, source_dir)

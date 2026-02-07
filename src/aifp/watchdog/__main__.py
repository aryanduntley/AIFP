"""
AIFP Watchdog - CLI Entry Point

Usage: python -m aifp.watchdog <project_root>

Starts the file system watcher as a subprocess. Reads configuration
from project.db and user_preferences.db, then monitors the source
directory for changes.
"""

import json
import os
import signal
import sys
import time

from ..database.connection import _effect_query_one, _effect_query_all
from ..wrappers.file_ops import _effect_write_text, _effect_ensure_dir
from .config import (
    get_watchdog_dir,
    get_reminders_path,
    get_pid_path,
    get_project_db_path,
    get_preferences_db_path,
    build_exclusion_sets,
    get_function_pattern,
)
from .reminders import _effect_clear_reminders
from .watcher import _effect_start_watching
from ..wrappers.filesystem_observer import _effect_stop_observer


def _read_infrastructure_value(project_db_path: str, infra_type: str) -> str:
    """Effect: Read a single value from the infrastructure table."""
    row = _effect_query_one(
        project_db_path,
        "SELECT value FROM infrastructure WHERE type = ?",
        (infra_type,),
    )
    return row['value'] if row and row.get('value') else ''


def _read_user_exclusions(prefs_db_path: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Effect: Read user exclusion settings from user_preferences.db.

    Returns (excluded_dirs, excluded_extensions) as tuples of strings.
    """
    user_dirs: tuple[str, ...] = ()
    user_exts: tuple[str, ...] = ()

    if not os.path.isfile(prefs_db_path):
        return (user_dirs, user_exts)

    row = _effect_query_one(
        prefs_db_path,
        "SELECT setting_value FROM user_settings WHERE setting_key = ?",
        ('watchdog_excluded_dirs',),
    )
    if row and row.get('setting_value'):
        try:
            parsed = json.loads(row['setting_value'])
            if isinstance(parsed, list):
                user_dirs = tuple(str(d) for d in parsed)
        except json.JSONDecodeError:
            pass

    row = _effect_query_one(
        prefs_db_path,
        "SELECT setting_value FROM user_settings WHERE setting_key = ?",
        ('watchdog_excluded_extensions',),
    )
    if row and row.get('setting_value'):
        try:
            parsed = json.loads(row['setting_value'])
            if isinstance(parsed, list):
                user_exts = tuple(str(e) for e in parsed)
        except json.JSONDecodeError:
            pass

    return (user_dirs, user_exts)


def main() -> None:
    """Effect: Main entry point for the watchdog subprocess."""
    if len(sys.argv) < 2:
        print("Usage: python -m aifp.watchdog <project_root>", file=sys.stderr)
        sys.exit(1)

    project_root = sys.argv[1]
    project_db_path = get_project_db_path(project_root)

    if not os.path.isfile(project_db_path):
        print(f"Error: project.db not found at {project_db_path}", file=sys.stderr)
        sys.exit(1)

    # Read infrastructure
    source_directory = _read_infrastructure_value(project_db_path, 'source_directory')
    if not source_directory:
        print("Error: source_directory not set in infrastructure table", file=sys.stderr)
        sys.exit(1)

    # Resolve source_directory relative to project_root if not absolute
    if not os.path.isabs(source_directory):
        source_directory = os.path.join(project_root, source_directory)

    if not os.path.isdir(source_directory):
        print(f"Error: source directory does not exist: {source_directory}", file=sys.stderr)
        sys.exit(1)

    primary_language = _read_infrastructure_value(project_db_path, 'primary_language')

    # Read user exclusions
    prefs_db_path = get_preferences_db_path(project_root)
    user_dirs, user_exts = _read_user_exclusions(prefs_db_path)
    excluded_dirs, excluded_extensions = build_exclusion_sets(user_dirs, user_exts)

    # Function pattern for language
    function_pattern = get_function_pattern(primary_language) if primary_language else None

    # Setup watchdog directory
    watchdog_dir = get_watchdog_dir(project_root)
    _effect_ensure_dir(watchdog_dir)

    # Write PID file
    pid_path = get_pid_path(project_root)
    _effect_write_text(pid_path, str(os.getpid()))

    # Clear reminders (fresh start)
    reminders_path = get_reminders_path(project_root)
    _effect_clear_reminders(reminders_path)

    # Start observer
    observer = _effect_start_watching(
        source_dir=source_directory,
        project_db_path=project_db_path,
        reminders_path=reminders_path,
        function_pattern=function_pattern,
        excluded_dirs=excluded_dirs,
        excluded_extensions=excluded_extensions,
    )

    # Signal handler for graceful shutdown
    def handle_sigterm(signum, frame):
        _effect_stop_observer(observer)
        # Clean up PID file
        try:
            os.remove(pid_path)
        except OSError:
            pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    # Run until killed
    try:
        while observer.is_alive():
            observer.join(timeout=1.0)
    except KeyboardInterrupt:
        pass
    finally:
        _effect_stop_observer(observer)
        try:
            os.remove(pid_path)
        except OSError:
            pass


if __name__ == '__main__':
    main()

"""
AIFP Helper Functions - Orchestrator Entry Points

Cross-database orchestrators that coordinate multiple databases.

Helpers in this file:
- aifp_init: Phase 1 mechanical setup (creates directories, databases, templates)
- aifp_status: Comprehensive project state assembly
- aifp_run: Gateway orchestrator for every AI interaction
- aifp_end: Session termination audit data gathering

These are the only helpers with target_database='multi_db'.
All operate across project.db, user_preferences.db, and core.db.
"""

import os
import shutil
import sqlite3
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List

from ._common import (
    _open_connection,
    _close_connection,
    _open_project_connection,
    _open_preferences_connection,
    _open_directives_connection,
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
    Result,
    AIFP_PROJECT_DIR,
    PROJECT_DB_NAME,
    USER_PREFERENCES_DB_NAME,
    BLUEPRINT_FILENAME,
    BACKUPS_DIR_NAME,
    VALID_STATUS_TYPES,
)

from .status import get_project_status


# ============================================================================
# aifp_init
# ============================================================================

def aifp_init(project_root: str) -> Result:
    """
    Phase 1 mechanical setup orchestrator for project initialization.

    Atomically creates directories, databases with schemas, and templates.
    No deep logic — pure mechanical operations. Cleans up on failure.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Result with data={
            success: bool,
            project_root: str,
            aifp_dir: str,
            files_created: tuple,
            tables_created: {project_db: tuple, user_prefs_db: tuple},
            infrastructure_entries: int,
            next_phase: str
        }

    On error:
        Result with data={
            success: False,
            error: str,
            failed_step: int,
            cleanup_performed: bool
        }
    """
    aifp_dir = get_aifp_project_dir(project_root)
    project_db_path = get_project_db_path(project_root)
    prefs_db_path = get_user_preferences_db_path(project_root)
    blueprint_dest = os.path.join(aifp_dir, BLUEPRINT_FILENAME)
    backups_dir = os.path.join(aifp_dir, BACKUPS_DIR_NAME)
    step = 0

    try:
        # Step 1: Check if already initialized
        step = 1
        if database_exists(project_db_path):
            return Result(
                success=False,
                data={
                    'success': False,
                    'error': f"Project already initialized: {project_db_path} exists",
                    'failed_step': step,
                    'cleanup_performed': False,
                },
                error="Project already initialized",
            )

        # Step 2: Create directories
        step = 2
        os.makedirs(aifp_dir, exist_ok=True)
        os.makedirs(backups_dir, exist_ok=True)

        # Step 3: Copy ProjectBlueprint_template.md
        step = 3
        template_path = _get_template_path()
        if not os.path.isfile(template_path):
            raise FileNotFoundError(
                f"ProjectBlueprint template not found: {template_path}"
            )
        shutil.copy2(template_path, blueprint_dest)

        # Step 4: Initialize project.db
        step = 4
        project_schema_path = _get_schema_path("project.sql")
        infra_sql_path = _get_initialization_path("standard_infrastructure.sql")

        conn = sqlite3.connect(project_db_path)
        conn.row_factory = sqlite3.Row
        try:
            # Load and execute project schema
            with open(project_schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)

            # Load and execute standard infrastructure entries
            with open(infra_sql_path, 'r') as f:
                infra_sql = f.read()
            conn.executescript(infra_sql)

            # Populate project_root value in infrastructure
            conn.execute(
                "UPDATE infrastructure SET value = ? WHERE type = 'project_root'",
                (project_root,)
            )
            conn.commit()

            project_tables = _get_table_names(conn)
        finally:
            conn.close()

        # Step 5: Initialize user_preferences.db
        step = 5
        prefs_schema_path = _get_schema_path("user_preferences.sql")

        conn = sqlite3.connect(prefs_db_path)
        conn.row_factory = sqlite3.Row
        try:
            with open(prefs_schema_path, 'r') as f:
                schema_sql = f.read()
            conn.executescript(schema_sql)

            # Insert default tracking_settings (all disabled)
            conn.execute(
                """
                INSERT OR IGNORE INTO tracking_settings (
                    track_files, track_functions, track_types,
                    track_interactions, track_themes, track_flows,
                    track_git_branches, track_dependencies,
                    auto_detect_functions, auto_detect_types,
                    auto_detect_interactions
                ) VALUES (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                """
            )
            conn.commit()

            prefs_tables = _get_table_names(conn)
        finally:
            conn.close()

        # Step 6: Create .gitkeep files
        step = 6
        gitkeep_path = os.path.join(backups_dir, ".gitkeep")
        if not os.path.exists(gitkeep_path):
            with open(gitkeep_path, 'w') as f:
                pass

        # Step 7: Verify created files exist
        step = 7
        for expected_path in (project_db_path, prefs_db_path, blueprint_dest, backups_dir):
            if not os.path.exists(expected_path):
                raise RuntimeError(f"Post-init check failed: expected file not found: {expected_path}")

        # Step 8: Return success
        files_created = (
            f'{AIFP_PROJECT_DIR}/',
            f'{AIFP_PROJECT_DIR}/{BACKUPS_DIR_NAME}/',
            f'{AIFP_PROJECT_DIR}/{PROJECT_DB_NAME}',
            f'{AIFP_PROJECT_DIR}/{USER_PREFERENCES_DB_NAME}',
            f'{AIFP_PROJECT_DIR}/{BLUEPRINT_FILENAME}',
        )

        return Result(
            success=True,
            data={
                'success': True,
                'project_root': project_root,
                'aifp_dir': aifp_dir,
                'files_created': files_created,
                'tables_created': {
                    'project_db': project_tables,
                    'user_prefs_db': prefs_tables,
                },
                'infrastructure_entries': 8,
                'next_phase': 'AI populates infrastructure and blueprint',
            },
            return_statements=get_return_statements("aifp_init"),
        )

    except Exception as e:
        # Cleanup: if we got past step 2, remove the directory
        cleanup_performed = False
        if step > 2 and os.path.isdir(aifp_dir):
            try:
                shutil.rmtree(aifp_dir)
                cleanup_performed = True
            except OSError:
                pass
        elif step == 2 and os.path.isdir(aifp_dir):
            try:
                shutil.rmtree(aifp_dir)
                cleanup_performed = True
            except OSError:
                pass

        return Result(
            success=False,
            data={
                'success': False,
                'error': str(e),
                'failed_step': step,
                'cleanup_performed': cleanup_performed,
            },
            error=str(e),
        )


def _get_template_path() -> str:
    """Pure: Get path to ProjectBlueprint template."""
    helpers_dir = Path(__file__).parent.parent  # src/aifp/helpers/
    return str(helpers_dir.parent / "templates" / "ProjectBlueprint_template.md")


def _get_schema_path(schema_file: str) -> str:
    """Pure: Get path to a database schema file."""
    helpers_dir = Path(__file__).parent.parent  # src/aifp/helpers/
    return str(helpers_dir.parent / "database" / "schemas" / schema_file)


def _get_initialization_path(init_file: str) -> str:
    """Pure: Get path to a database initialization file."""
    helpers_dir = Path(__file__).parent.parent  # src/aifp/helpers/
    return str(helpers_dir.parent / "database" / "initialization" / init_file)


# ============================================================================
# aifp_status
# ============================================================================

def aifp_status(
    project_root: str,
    type: str = "summary",
) -> Result:
    """
    Status orchestrator that retrieves comprehensive project state.

    Gathers data from multiple tables and databases for AI to determine
    next steps. Coordinates project.db, user_preferences.db, and
    optionally user_directives.db.

    Args:
        project_root: Absolute path to project root directory
        type: 'quick', 'summary' (default), or 'detailed'

    Returns:
        Result with data={
            project_metadata: dict,
            infrastructure: tuple,
            work_hierarchy: dict (from get_project_status),
            user_directives_status: str or None,
            recent_warnings: tuple,
            git_state: tuple
        }

    If not initialized:
        Result with data={initialized: False}
    """
    if type not in VALID_STATUS_TYPES:
        return Result(
            success=False,
            error=f"Invalid type '{type}'. Valid: {sorted(VALID_STATUS_TYPES)}",
        )

    aifp_dir = get_aifp_project_dir(project_root)
    if not os.path.isdir(aifp_dir):
        return Result(
            success=True,
            data={'initialized': False},
            return_statements=get_return_statements("aifp_status"),
        )

    try:
        # Work hierarchy (includes counts + tree)
        status_result = get_project_status(project_root, type)
        work_hierarchy = status_result.data if status_result.success else {}

        # Project metadata + infrastructure from project.db
        project_metadata = {}
        infrastructure = ()
        user_directives_status = None
        recent_warnings = ()
        git_state = ()

        project_db_path = get_project_db_path(project_root)
        if database_exists(project_db_path):
            conn = _open_project_connection(project_root)
            try:
                # Project metadata
                cursor = conn.execute("SELECT * FROM project LIMIT 1")
                row = cursor.fetchone()
                if row:
                    project_metadata = row_to_dict(row)

                # Infrastructure
                cursor = conn.execute("SELECT * FROM infrastructure ORDER BY id")
                infrastructure = rows_to_tuple(cursor.fetchall())

                # User directives status
                user_directives_status = project_metadata.get(
                    'user_directives_status'
                )

                # Recent warnings/errors (last 5)
                cursor = conn.execute(
                    "SELECT * FROM notes "
                    "WHERE severity IN ('warning', 'error') "
                    "ORDER BY created_at DESC LIMIT 5"
                )
                recent_warnings = rows_to_tuple(cursor.fetchall())

                # Git state
                cursor = conn.execute(
                    "SELECT * FROM work_branches ORDER BY id DESC"
                )
                git_state = rows_to_tuple(cursor.fetchall())

            finally:
                conn.close()

        # If Use Case 2 + active: query user_directives.db for counts
        user_directives_data = None
        if user_directives_status in ('in_progress', 'active'):
            directives_db_path = get_user_directives_db_path(project_root)
            if database_exists(directives_db_path):
                try:
                    conn = _open_directives_connection(project_root)
                    try:
                        cursor = conn.execute(
                            "SELECT COUNT(*) as cnt FROM user_directives "
                            "WHERE is_active = 1"
                        )
                        row = cursor.fetchone()
                        user_directives_data = {
                            'active_count': row['cnt'] if row else 0,
                        }
                    finally:
                        conn.close()
                except Exception:
                    user_directives_data = {'error': 'Could not access user_directives.db'}

        # Supportive context (detailed FP examples, DRY, state DB, etc.)
        supportive_context = _get_supportive_context_safe()

        data = {
            'initialized': True,
            'project_metadata': project_metadata,
            'infrastructure': infrastructure,
            'work_hierarchy': work_hierarchy,
            'user_directives_status': user_directives_status,
            'user_directives_data': user_directives_data,
            'recent_warnings': recent_warnings,
            'git_state': git_state,
            'supportive_context': supportive_context,
        }

        return Result(
            success=True,
            data=data,
            return_statements=get_return_statements("aifp_status"),
        )

    except Exception as e:
        return Result(success=False, error=f"Status failed: {str(e)}")


# ============================================================================
# aifp_run
# ============================================================================

def aifp_run(is_new_session: bool = False) -> Result:
    """
    Main entry point orchestrator. Called on every AI interaction.

    When is_new_session=True, bundles comprehensive startup data including
    status, user settings, FP directive index, all directive names,
    infrastructure data, and guidance.

    When is_new_session=False, returns lightweight guidance only.

    Args:
        is_new_session: True for first interaction / new session / after breaks

    Returns:
        If is_new_session=True:
            Result with data={
                status: dict (from aifp_status),
                user_settings: dict,
                fp_directive_index: dict,
                all_directive_names: tuple,
                infrastructure_data: tuple,
                supportive_context: str (detailed FP examples, DRY, state DB, etc.),
                guidance: dict
            }

        If is_new_session=False:
            Result with data={
                guidance: dict,
                common_starting_points: tuple (includes get_supportive_context() reference)
            }
    """
    try:
        if not is_new_session:
            # Lightweight response — still read watchdog reminders if project exists
            project_root = _discover_project_root()
            watchdog_data = {'status': 'no_project', 'reminders': (), 'notice': None}
            if project_root is not None:
                watchdog_data = _read_and_clear_reminders(project_root)

            return Result(
                success=True,
                data={
                    'guidance': _get_guidance(),
                    'action_required': (
                        'You MUST act proactively — do not wait for user commands.',
                        'If user gave a task: Execute it using AIFP directives.',
                        'If no task: Call aifp_status() and present next steps.',
                        'If something unexpected happened: Use project_sidequest_create or project_notes_log.',
                        'If writing code: Follow reserve → write → finalize flow (batch helpers available).',
                        'If confused or lost context: Call aifp_status() for fresh state, '
                        'then search_directives() to find the right directive for the situation.',
                    ),
                    'common_starting_points': (
                        'aifp_status() — Get fresh project state and determine next action',
                        'get_supportive_context() — Reload detailed FP examples, DRY patterns, state DB usage, behavioral rules',
                        'project_task_create — Create new task from user request',
                        'project_sidequest_create — Track unexpected work or user change of plans',
                        'project_notes_log — Log decisions, clarifications, or context',
                        'project_auto_resume — Resume interrupted work',
                    ),
                    'session_health': (
                        'If context feels stale or compressed, call aifp_run(is_new_session=true) '
                        'to reload full project state from database.'
                    ),
                    'watchdog': watchdog_data,
                },
                return_statements=get_return_statements("aifp_run"),
            )

        # Full session bundle — need project_root from core or environment
        # aifp_run discovers project_root by scanning for .aifp-project/
        project_root = _discover_project_root()

        if project_root is None:
            return Result(
                success=True,
                data={
                    'initialized': False,
                    'guidance': _get_guidance(),
                    'message': 'No AIFP project found. Run project_init to initialize.',
                },
                return_statements=get_return_statements("aifp_run"),
            )

        # Watchdog: kill previous, start fresh, read any accumulated reminders
        watchdog_start = _start_watchdog(project_root)
        watchdog_read = _read_and_clear_reminders(project_root)
        watchdog_data = {
            'started': watchdog_start.get('started', False),
            'start_error': watchdog_start.get('error'),
            'status': watchdog_read.get('status', 'unknown'),
            'reminders': watchdog_read.get('reminders', ()),
            'notice': watchdog_read.get('notice'),
        }

        # Bundle: status
        status_result = aifp_status(project_root, type="summary")
        status_data = status_result.data if status_result.success else {}

        # Bundle: user settings
        user_settings = _get_user_settings_safe(project_root)

        # Bundle: FP directive index
        fp_directive_index = _get_fp_directive_index_safe()

        # Bundle: all directive names
        all_directive_names = _get_all_directive_names_safe()

        # Bundle: infrastructure
        infrastructure_data = _get_infrastructure_safe(project_root)

        # Bundle: supportive context (detailed FP examples, DRY, state DB, etc.)
        supportive_context = _get_supportive_context_safe()

        return Result(
            success=True,
            data={
                'project_root': project_root,
                'status': status_data,
                'user_settings': user_settings,
                'fp_directive_index': fp_directive_index,
                'all_directive_names': all_directive_names,
                'infrastructure_data': infrastructure_data,
                'supportive_context': supportive_context,
                'guidance': _get_guidance(),
                'watchdog': watchdog_data,
            },
            return_statements=get_return_statements("aifp_run"),
        )

    except Exception as e:
        return Result(success=False, error=f"aifp_run failed: {str(e)}")


def _start_watchdog(project_root: str) -> Dict[str, Any]:
    """
    Effect: Start watchdog subprocess for the project.

    Kills any existing watchdog process, clears old reminders,
    then starts a new watchdog subprocess.

    Returns:
        dict with {started: bool, error: str or None}
    """
    import signal
    import subprocess
    import sys

    from ...watchdog.config import get_watchdog_dir, get_pid_path, get_reminders_path
    from ...watchdog.reminders import _effect_clear_reminders

    watchdog_dir = get_watchdog_dir(project_root)
    pid_path = get_pid_path(project_root)
    reminders_path = get_reminders_path(project_root)

    # Kill existing watchdog if running
    if os.path.isfile(pid_path):
        try:
            with open(pid_path, 'r') as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, signal.SIGTERM)
        except (ValueError, OSError, ProcessLookupError):
            pass
        try:
            os.remove(pid_path)
        except OSError:
            pass

    # Clear old reminders
    _effect_clear_reminders(reminders_path)

    # Start new watchdog subprocess (inherits parent lifecycle)
    try:
        os.makedirs(watchdog_dir, exist_ok=True)
        subprocess.Popen(
            [sys.executable, '-m', 'aifp.watchdog', project_root],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return {'started': True, 'error': None}
    except (OSError, subprocess.SubprocessError) as e:
        return {
            'started': False,
            'error': f"Watchdog failed to start: {str(e)}. "
                     "Verify the watchdog module is installed (aifp.watchdog package).",
        }


def _read_and_clear_reminders(project_root: str) -> Dict[str, Any]:
    """
    Effect: Read watchdog reminders and clear the file.

    Returns:
        dict with {
            status: 'ok' | 'not_running' | 'no_reminders_file',
            reminders: tuple of reminder dicts,
            notice: str or None
        }
    """
    from ...watchdog.config import get_reminders_path, get_pid_path
    from ...watchdog.reminders import _effect_read_reminders, _effect_clear_reminders

    pid_path = get_pid_path(project_root)
    reminders_path = get_reminders_path(project_root)

    # Check if watchdog is running (PID file exists)
    if not os.path.isfile(pid_path):
        return {
            'status': 'not_running',
            'reminders': (),
            'notice': "Watchdog process is not running. File change monitoring is inactive. "
                      "Call aifp_run(is_new_session=true) to restart, or verify the "
                      "watchdog module is installed.",
        }

    # Check if reminders file exists
    if not os.path.isfile(reminders_path):
        return {
            'status': 'no_reminders_file',
            'reminders': (),
            'notice': "Watchdog PID file exists but reminders file is missing. "
                      "Watchdog may have failed to initialize. Check "
                      ".aifp-project/watchdog/ directory.",
        }

    reminders = _effect_read_reminders(reminders_path)
    if reminders:
        _effect_clear_reminders(reminders_path)
    return {
        'status': 'ok',
        'reminders': reminders,
        'notice': None,
    }


def _discover_project_root() -> Optional[str]:
    """
    Effect: Discover project root by searching for .aifp-project/ directory.

    Walks up from current working directory looking for .aifp-project/.

    Returns:
        Project root path, or None if not found
    """
    current = Path.cwd()
    for _ in range(20):  # Max 20 levels up
        aifp_dir = current / AIFP_PROJECT_DIR
        if aifp_dir.is_dir():
            return str(current)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def _get_guidance() -> Dict[str, Any]:
    """Pure: Return static guidance for AI behavior."""
    return {
        'directive_access': (
            "Directive names cached from is_new_session bundle. "
            "Call get_directive(name) for specific details."
        ),
        'when_to_use': (
            "Use AIFP directives when coding or when project "
            "management action/reaction is needed."
        ),
        'assumption': (
            "Always assume AIFP applies unless user explicitly rejects it."
        ),
        'session_refresh': (
            "Call aifp_run(is_new_session=true) again if context feels stale "
            "or after extended work."
        ),
    }


def _get_user_settings_safe(project_root: str) -> Dict[str, Any]:
    """Effect: Get user settings, returning empty dict on failure."""
    try:
        from ..user_preferences.management import get_user_settings
        prefs_db_path = get_user_preferences_db_path(project_root)
        result = get_user_settings(prefs_db_path)
        if result.success:
            return result.data if hasattr(result, 'data') and result.data else {}
        return {}
    except Exception:
        return {}


def _get_fp_directive_index_safe() -> Dict[str, Any]:
    """Effect: Get FP directive index, returning empty dict on failure."""
    try:
        from ..core.directives_1 import get_fp_directive_index
        result = get_fp_directive_index()
        if result.success:
            return result.data if hasattr(result, 'data') and result.data else {}
        return {}
    except Exception:
        return {}


def _get_all_directive_names_safe() -> Tuple[str, ...]:
    """Effect: Get all directive names, returning empty tuple on failure."""
    try:
        from ..core.directives_1 import get_all_directive_names
        result = get_all_directive_names()
        if result.success:
            return result.data if hasattr(result, 'data') and result.data else ()
        return ()
    except Exception:
        return ()


def _get_supportive_context_safe() -> str:
    """Effect: Get supportive context content, returning empty string on failure."""
    try:
        from ..global.supportive_context import get_supportive_context
        result = get_supportive_context()
        if result.success and result.data:
            return result.data.get('content', '')
        return ''
    except Exception:
        return ''


def _get_infrastructure_safe(project_root: str) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get infrastructure data, returning empty tuple on failure."""
    try:
        from ..project.metadata import get_all_infrastructure
        db_path = get_project_db_path(project_root)
        result = get_all_infrastructure(db_path)
        if result.success:
            return result.data if hasattr(result, 'data') and result.data else ()
        return ()
    except Exception:
        return ()


# ============================================================================
# aifp_end
# ============================================================================

def aifp_end(project_root: str) -> Result:
    """
    Session termination orchestrator.

    Stops watchdog (if running) and delegates to get_project_status for
    project state. AI uses status data + conversation context to perform
    session audit, compliance checks, and summary generation.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Result with data={
            success: bool,
            watchdog: {stopped: bool|None, final_reminders: list},
            project_state: dict (from get_project_status)
        }
    """
    aifp_dir = get_aifp_project_dir(project_root)
    if not os.path.isdir(aifp_dir):
        return Result(
            success=False,
            data={'initialized': False},
            error="No .aifp-project/ directory found",
        )

    # Step 1: Watchdog — stop process and read reminders
    watchdog_data = _stop_watchdog(aifp_dir)

    # Step 2: Project state via existing status helper
    status_result = get_project_status(project_root, "detailed")
    project_state = status_result.data if status_result.success else {}

    return Result(
        success=True,
        data={
            'success': True,
            'watchdog': watchdog_data,
            'project_state': project_state,
        },
        return_statements=get_return_statements("aifp_end"),
    )


def _stop_watchdog(aifp_dir: str) -> Dict[str, Any]:
    """
    Effect: Stop watchdog process if running, read final reminders.

    Checks for PID file at .aifp-project/watchdog/watchdog.pid.
    If found and process alive, kills it and reads reminders.json.
    If not found, returns stopped=None (watchdog not running).

    Args:
        aifp_dir: Path to .aifp-project/ directory

    Returns:
        dict with {stopped: bool|None, final_reminders: tuple}
    """
    import signal

    from ...watchdog.reminders import _effect_read_reminders, _effect_clear_reminders

    watchdog_dir = os.path.join(aifp_dir, "watchdog")
    pid_file = os.path.join(watchdog_dir, "watchdog.pid")
    reminders_file = os.path.join(watchdog_dir, "reminders.json")

    if not os.path.isfile(pid_file):
        return {'stopped': None, 'final_reminders': ()}

    # Read reminders before killing process
    final_reminders = _effect_read_reminders(reminders_file)

    # Attempt to stop the watchdog process
    stopped = False
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        stopped = True
    except (ValueError, OSError, ProcessLookupError):
        stopped = True

    # Clean up PID file and reminders
    try:
        os.remove(pid_file)
    except OSError:
        pass
    _effect_clear_reminders(reminders_file)

    return {'stopped': stopped, 'final_reminders': final_reminders}

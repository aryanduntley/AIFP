"""
AIFP Helper Utilities - Global Database-Agnostic Shared Code

This module provides utilities shared across ALL helper categories.
It is the TOP level of the DRY hierarchy:

    utils.py (global)
        └── {category}/_common.py (category-specific)
            └── {category}/{file}.py (individual helpers)

Database-agnostic utilities:
- Database path resolution for all 4 databases
- Generic connection management
- Return statements fetching
- Common Result type definitions
- Schema introspection utilities

All functions follow FP principles:
- Pure functions where possible
- Effects clearly isolated and named
- Immutable data structures
- Explicit parameters
"""

import os
import re
import sqlite3
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, List, Dict, Any, Final


# ============================================================================
# Global Constants
# ============================================================================

# AIFP project folder name (contains per-project databases)
AIFP_PROJECT_DIR: Final[str] = ".aifp-project"

# Database file names
CORE_DB_NAME: Final[str] = "aifp_core.db"
PROJECT_DB_NAME: Final[str] = "project.db"
USER_PREFERENCES_DB_NAME: Final[str] = "user_preferences.db"
USER_DIRECTIVES_DB_NAME: Final[str] = "user_directives.db"


# ============================================================================
# Generic Result Types (Immutable)
# ============================================================================

@dataclass(frozen=True)
class Result:
    """
    Generic immutable result type for operations.

    Use for simple success/error returns where no specific data type needed.
    For typed data, create specific Result dataclasses in each module.
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class QueryResult:
    """
    Immutable result for database query operations.

    Returns rows as tuple of dicts for immutability.
    """
    success: bool
    rows: Tuple[Dict[str, Any], ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class SchemaResult:
    """
    Immutable result for schema introspection operations.
    """
    success: bool
    tables: Tuple[str, ...] = ()
    fields: Tuple[Dict[str, Any], ...] = ()
    error: Optional[str] = None


# ============================================================================
# Database Path Resolution
# ============================================================================

def get_core_db_path() -> str:
    """
    Get absolute path to aifp_core.db.

    The core database is located in the MCP server installation,
    at src/aifp/database/aifp_core.db relative to the package.

    Returns:
        Absolute path to core database

    Note:
        This assumes the database is in src/aifp/database/aifp_core.db
        relative to the helpers directory.
    """
    # Get the directory of this file (src/aifp/helpers/)
    helpers_dir = Path(__file__).parent

    # Navigate to database directory (src/aifp/database/)
    db_path = helpers_dir.parent / "database" / CORE_DB_NAME

    return str(db_path.resolve())


def get_project_db_path(project_root: str) -> str:
    """
    Get absolute path to project.db for a given project.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Absolute path to project.db

    Example:
        >>> get_project_db_path("/home/user/my-project")
        '/home/user/my-project/.aifp-project/project.db'
    """
    return str(Path(project_root) / AIFP_PROJECT_DIR / PROJECT_DB_NAME)


def get_user_preferences_db_path(project_root: str) -> str:
    """
    Get absolute path to user_preferences.db for a given project.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Absolute path to user_preferences.db

    Example:
        >>> get_user_preferences_db_path("/home/user/my-project")
        '/home/user/my-project/.aifp-project/user_preferences.db'
    """
    return str(Path(project_root) / AIFP_PROJECT_DIR / USER_PREFERENCES_DB_NAME)


def get_user_directives_db_path(project_root: str) -> str:
    """
    Get absolute path to user_directives.db for a given project.

    Note: This database only exists for Use Case 2 (automation projects).

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Absolute path to user_directives.db

    Example:
        >>> get_user_directives_db_path("/home/user/my-automation")
        '/home/user/my-automation/.aifp-project/user_directives.db'
    """
    return str(Path(project_root) / AIFP_PROJECT_DIR / USER_DIRECTIVES_DB_NAME)


def get_aifp_project_dir(project_root: str) -> str:
    """
    Get absolute path to .aifp-project directory.

    Args:
        project_root: Absolute path to project root directory

    Returns:
        Absolute path to .aifp-project directory
    """
    return str(Path(project_root) / AIFP_PROJECT_DIR)


def database_exists(db_path: str) -> bool:
    """
    Pure: Check if database file exists.

    Args:
        db_path: Path to database file

    Returns:
        True if file exists, False otherwise
    """
    return os.path.exists(db_path)


# ============================================================================
# Database Connection Management
# ============================================================================

def _open_connection(db_path: str) -> sqlite3.Connection:
    """
    Effect: Open database connection with row factory.

    Used across ALL helper categories for consistent database access.
    Row factory enables dict-like access to columns by name.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Database connection with row factory configured

    Example:
        >>> conn = _open_connection("/path/to/project.db")
        >>> cursor = conn.execute("SELECT * FROM files")
        >>> row = cursor.fetchone()
        >>> row["name"]  # Access by column name
        'my_file.py'
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _close_connection(conn: sqlite3.Connection) -> None:
    """
    Effect: Close database connection safely.

    Args:
        conn: Database connection to close
    """
    if conn:
        conn.close()


# ============================================================================
# Return Statements Fetcher
# ============================================================================

def get_return_statements(helper_name: str) -> Tuple[str, ...]:
    """
    Fetch return statements for a helper from core database.

    Return statements are forward-thinking guidance for AI, providing
    next steps and context after a helper executes successfully.

    Args:
        helper_name: Name of the helper function (e.g., 'reserve_file')

    Returns:
        Tuple of return statement strings (empty tuple if not found)

    Example:
        >>> stmts = get_return_statements("reserve_file")
        >>> stmts
        ('Use returned ID for file naming: {name}_id_{id}.{ext}',)

    Note:
        - Returns empty tuple if helper not found in database
        - Returns empty tuple if return_statements is NULL or empty
        - Returns empty tuple on any error (graceful degradation)
        - Return statements are stored as JSON array in database
    """
    try:
        # Get core database path
        core_db = get_core_db_path()

        # Check if database exists
        if not database_exists(core_db):
            return ()

        # Query database for return_statements
        conn = _open_connection(core_db)

        try:
            cursor = conn.execute(
                "SELECT return_statements FROM helper_functions WHERE name = ?",
                (helper_name,)
            )
            row = cursor.fetchone()

            if row is None:
                return ()

            # Parse return_statements JSON
            return_statements_json = row['return_statements']

            if return_statements_json is None:
                return ()

            # Parse JSON array
            if isinstance(return_statements_json, str):
                statements = json.loads(return_statements_json)
            else:
                statements = return_statements_json

            # Convert to tuple (immutable)
            if isinstance(statements, list):
                return tuple(statements)
            else:
                return ()

        finally:
            _close_connection(conn)

    except Exception:
        # If any error occurs, return empty tuple
        # This ensures helper functions don't fail if core DB is unavailable
        return ()


# ============================================================================
# Schema Introspection Utilities
# ============================================================================

def _get_table_names(conn: sqlite3.Connection) -> Tuple[str, ...]:
    """
    Effect: Get all table names from database.

    Args:
        conn: Database connection

    Returns:
        Tuple of table names (immutable)
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return tuple(row['name'] for row in cursor.fetchall())


def _get_table_info(conn: sqlite3.Connection, table_name: str) -> Tuple[Dict[str, Any], ...]:
    """
    Effect: Get column info for a table using PRAGMA table_info.

    Args:
        conn: Database connection
        table_name: Name of the table

    Returns:
        Tuple of column info dicts with keys: cid, name, type, notnull, dflt_value, pk
    """
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return tuple(
        {
            'cid': row['cid'],
            'name': row['name'],
            'type': row['type'],
            'notnull': bool(row['notnull']),
            'default_value': row['dflt_value'],
            'is_primary_key': bool(row['pk'])
        }
        for row in cursor.fetchall()
    )


def _get_table_sql(conn: sqlite3.Connection, table_name: str) -> Optional[str]:
    """
    Effect: Get CREATE TABLE SQL statement for a table.

    Args:
        conn: Database connection
        table_name: Name of the table

    Returns:
        CREATE TABLE SQL string, or None if table not found
    """
    cursor = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    row = cursor.fetchone()
    return row['sql'] if row else None


def _parse_check_constraint(sql: str, field_name: str) -> Optional[Tuple[str, ...]]:
    """
    Pure: Parse CHECK constraint values from CREATE TABLE SQL.

    Extracts values from CHECK (field IN ('val1', 'val2', ...)) patterns.

    Args:
        sql: CREATE TABLE SQL statement
        field_name: Field name to find CHECK constraint for

    Returns:
        Tuple of allowed values, or None if no CHECK constraint found

    Example:
        >>> sql = "CREATE TABLE t (status TEXT CHECK (status IN ('active', 'paused')))"
        >>> _parse_check_constraint(sql, 'status')
        ('active', 'paused')
    """
    # Pattern: field_name ... CHECK (field_name IN ('val1', 'val2', ...))
    # or: CHECK (field_name IN ('val1', 'val2', ...))
    pattern = rf"CHECK\s*\(\s*{re.escape(field_name)}\s+IN\s*\(([^)]+)\)\s*\)"

    match = re.search(pattern, sql, re.IGNORECASE)
    if not match:
        return None

    # Extract values from IN clause
    values_str = match.group(1)

    # Parse quoted values (handles both single and double quotes)
    values = re.findall(r"['\"]([^'\"]+)['\"]", values_str)

    return tuple(values) if values else None


# ============================================================================
# Row Conversion Utilities
# ============================================================================

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """
    Pure: Convert SQLite Row to immutable-friendly dict.

    Args:
        row: SQLite Row object

    Returns:
        Dictionary with column names as keys
    """
    return dict(row)


def rows_to_tuple(rows: List[sqlite3.Row]) -> Tuple[Dict[str, Any], ...]:
    """
    Pure: Convert list of SQLite Rows to tuple of dicts.

    Args:
        rows: List of SQLite Row objects

    Returns:
        Tuple of dictionaries (immutable)
    """
    return tuple(row_to_dict(row) for row in rows)


# ============================================================================
# JSON Parsing Utilities
# ============================================================================

def parse_json_field(value: Optional[str]) -> Optional[Any]:
    """
    Pure: Safely parse JSON field from database.

    Args:
        value: JSON string or None

    Returns:
        Parsed JSON value, or None if parsing fails or value is None
    """
    if value is None:
        return None

    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


def json_to_tuple(value: Optional[str]) -> Tuple[Any, ...]:
    """
    Pure: Parse JSON array field to tuple.

    Args:
        value: JSON array string or None

    Returns:
        Tuple of values, or empty tuple if parsing fails
    """
    parsed = parse_json_field(value)
    if isinstance(parsed, list):
        return tuple(parsed)
    return ()

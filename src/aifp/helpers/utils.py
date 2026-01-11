"""
AIFP Helper Utilities - Global Internal Functions

Internal utility functions for use by helper functions.
These are NOT exposed as MCP tools - they are for internal use only.

Functions:
- get_return_statements: Fetch return statements from core database
"""

import os
import sqlite3
import json
from pathlib import Path
from typing import Tuple


# ============================================================================
# Core Database Path Resolution
# ============================================================================

def get_core_db_path() -> str:
    """
    Get absolute path to aifp_core.db.

    Returns:
        Absolute path to core database

    Note:
        This assumes the database is in src/aifp/database/aifp_core.db
        relative to the project root.
    """
    # Get the directory of this file (src/aifp/helpers/)
    helpers_dir = Path(__file__).parent

    # Navigate to database directory (src/aifp/database/)
    db_path = helpers_dir.parent / "database" / "aifp_core.db"

    return str(db_path.resolve())


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
        - Return statements are stored as JSON array in database
    """
    try:
        # Get core database path
        core_db = get_core_db_path()

        # Check if database exists
        if not os.path.exists(core_db):
            return ()

        # Query database for return_statements
        conn = sqlite3.connect(core_db)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT return_statements
            FROM helper_functions
            WHERE name = ?
        """, (helper_name,))

        row = cur.fetchone()
        conn.close()

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

    except Exception:
        # If any error occurs, return empty tuple
        # This ensures helper functions don't fail if core DB is unavailable
        return ()

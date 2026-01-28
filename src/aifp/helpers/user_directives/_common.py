"""
AIFP Helper Functions - User Directives Common Utilities

Shared utilities used across multiple user_directives helper files.
Extracted to avoid duplication and improve AI efficiency at scale.

This is the CATEGORY level of the DRY hierarchy:

    utils.py (global)                    <- Database-agnostic shared code
        └── user_directives/_common.py   <- THIS FILE: User directives specific
            └── user_directives/{file}.py <- Individual helpers

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.

Global constants defined here per AIFP FP methodology:
- Valid directive statuses
- Valid trigger types
- Valid action types
- Valid note types for user_directives notes table
- Valid severity levels

Imported from utils.py (global):
- _open_connection: Database connection with row factory
- get_user_directives_db_path: Path resolution
"""

import sqlite3
from typing import Final

# Import global utilities (DRY - avoid duplication)
from ..utils import _open_connection  # noqa: F401 - re-exported for convenience
from ..utils import get_user_directives_db_path  # noqa: F401 - re-exported


# ============================================================================
# Global Constants - Validation Lookup Tables (FP-Compliant)
# ============================================================================
# These match CHECK constraints in user_directives.sql schema
# Use Final + frozenset for immutability and fast membership testing

# Directive statuses (user_directives table)
VALID_DIRECTIVE_STATUSES: Final[frozenset[str]] = frozenset([
    'pending_validation',
    'validated',
    'implementing',
    'implemented',
    'active',
    'paused',
    'error',
    'deprecated'
])

# Trigger types (user_directives table)
VALID_TRIGGER_TYPES: Final[frozenset[str]] = frozenset([
    'time', 'event', 'condition', 'manual'
])

# Action types (user_directives table)
VALID_ACTION_TYPES: Final[frozenset[str]] = frozenset([
    'api_call', 'script_execution', 'function_call', 'command', 'notification'
])

# Note types for notes table
VALID_NOTE_TYPES: Final[frozenset[str]] = frozenset([
    'implementation',
    'validation',
    'execution',
    'dependency',
    'error',
    'optimization',
    'user_feedback',
    'lifecycle',
    'testing',
    'general'
])

# Severity levels (shared across databases)
VALID_SEVERITY_LEVELS: Final[frozenset[str]] = frozenset([
    'info', 'warning', 'error'
])


# ============================================================================
# Validation Utilities
# ============================================================================

def _validate_directive_status(status: str) -> bool:
    """
    Pure: Validate directive status value.

    Args:
        status: Status to validate

    Returns:
        True if valid, False otherwise
    """
    return status in VALID_DIRECTIVE_STATUSES


def _validate_note_type(note_type: str) -> bool:
    """
    Pure: Validate note type.

    Args:
        note_type: Note type to validate

    Returns:
        True if valid, False otherwise
    """
    return note_type in VALID_NOTE_TYPES


def _validate_severity(severity: str) -> bool:
    """
    Pure: Validate severity level.

    Args:
        severity: Severity value to validate

    Returns:
        True if valid, False otherwise
    """
    return severity in VALID_SEVERITY_LEVELS


# ============================================================================
# Entity Existence Check Utilities
# ============================================================================

def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    """
    Effect: Check if table exists in database.

    Args:
        conn: Database connection
        table: Table name

    Returns:
        True if exists, False otherwise
    """
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,)
    )
    return cursor.fetchone() is not None


def _record_exists(conn: sqlite3.Connection, table: str, record_id: int) -> bool:
    """
    Effect: Check if record with ID exists.

    Args:
        conn: Database connection
        table: Table name
        record_id: Record ID

    Returns:
        True if exists, False otherwise
    """
    cursor = conn.execute(f"SELECT id FROM {table} WHERE id = ?", (record_id,))
    return cursor.fetchone() is not None


def _directive_exists_by_id(conn: sqlite3.Connection, directive_id: int) -> bool:
    """
    Effect: Check if directive exists by ID.

    Args:
        conn: Database connection
        directive_id: Directive ID

    Returns:
        True if exists, False otherwise
    """
    cursor = conn.execute(
        "SELECT id FROM user_directives WHERE id = ?",
        (directive_id,)
    )
    return cursor.fetchone() is not None


def _directive_is_approved(conn: sqlite3.Connection, directive_id: int) -> bool:
    """
    Effect: Check if directive is approved.

    Args:
        conn: Database connection
        directive_id: Directive ID

    Returns:
        True if approved=1, False otherwise (including if not found)
    """
    cursor = conn.execute(
        "SELECT approved FROM user_directives WHERE id = ?",
        (directive_id,)
    )
    row = cursor.fetchone()
    return bool(row['approved']) if row else False

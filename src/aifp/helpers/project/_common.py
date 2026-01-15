"""
AIFP Helper Functions - Project Common Utilities

Shared utilities used across multiple project helper files.
Extracted to avoid duplication and improve AI efficiency at scale.

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.

Common utilities:
- _open_connection: Database connection with row factory
- _check_entity_exists: Generic entity existence check
- _check_file_exists: File-specific existence check
- _check_function_exists: Function-specific existence check
- _check_type_exists: Type-specific existence check
- _check_theme_exists: Theme-specific existence check
- _check_flow_exists: Flow-specific existence check
- _create_deletion_note: Audit note for deletions
"""

import sqlite3
from typing import Optional


# ============================================================================
# Database Connection Utilities
# ============================================================================

def _open_connection(db_path: str) -> sqlite3.Connection:
    """
    Effect: Open database connection with row factory.

    Used across all project helpers for consistent database access.

    Args:
        db_path: Path to project.db

    Returns:
        Database connection with row factory configured
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================================
# Entity Existence Check Utilities
# ============================================================================

def _check_entity_exists(
    conn: sqlite3.Connection,
    table: str,
    entity_id: int
) -> bool:
    """
    Effect: Check if entity ID exists in table.

    Generic existence checker for any table with id column.

    Args:
        conn: Database connection
        table: Table name (e.g., 'files', 'functions', 'types')
        entity_id: Entity ID to check

    Returns:
        True if exists, False otherwise
    """
    cursor = conn.execute(f"SELECT id FROM {table} WHERE id = ?", (entity_id,))
    return cursor.fetchone() is not None


# Specific wrappers for type safety and clarity
def _check_file_exists(conn: sqlite3.Connection, file_id: int) -> bool:
    """
    Effect: Check if file ID exists.

    Type-safe wrapper around _check_entity_exists.

    Args:
        conn: Database connection
        file_id: File ID to check

    Returns:
        True if exists, False otherwise
    """
    return _check_entity_exists(conn, "files", file_id)


def _check_function_exists(conn: sqlite3.Connection, function_id: int) -> bool:
    """
    Effect: Check if function ID exists.

    Type-safe wrapper around _check_entity_exists.

    Args:
        conn: Database connection
        function_id: Function ID to check

    Returns:
        True if exists, False otherwise
    """
    return _check_entity_exists(conn, "functions", function_id)


def _check_type_exists(conn: sqlite3.Connection, type_id: int) -> bool:
    """
    Effect: Check if type ID exists.

    Type-safe wrapper around _check_entity_exists.

    Args:
        conn: Database connection
        type_id: Type ID to check

    Returns:
        True if exists, False otherwise
    """
    return _check_entity_exists(conn, "types", type_id)


def _check_theme_exists(conn: sqlite3.Connection, theme_id: int) -> bool:
    """
    Effect: Check if theme ID exists.

    Type-safe wrapper around _check_entity_exists.

    Args:
        conn: Database connection
        theme_id: Theme ID to check

    Returns:
        True if exists, False otherwise
    """
    return _check_entity_exists(conn, "themes", theme_id)


def _check_flow_exists(conn: sqlite3.Connection, flow_id: int) -> bool:
    """
    Effect: Check if flow ID exists.

    Type-safe wrapper around _check_entity_exists.

    Args:
        conn: Database connection
        flow_id: Flow ID to check

    Returns:
        True if exists, False otherwise
    """
    return _check_entity_exists(conn, "flows", flow_id)


# ============================================================================
# Audit Note Utilities
# ============================================================================

def _create_deletion_note(
    conn: sqlite3.Connection,
    reference_table: str,
    reference_id: int,
    reason: str,
    severity: str,
    source: str,
    note_type: str
) -> None:
    """
    Effect: Create note entry for deletion audit trail.

    Used across multiple helpers to maintain audit trail when deleting entities.

    Args:
        conn: Database connection
        reference_table: Table name (e.g., 'files', 'functions', 'types', 'themes', 'flows')
        reference_id: Deleted record ID
        reason: Deletion reason
        severity: 'info', 'warning', 'error'
        source: 'ai' or 'user'
        note_type: Note type (e.g., 'entry_deletion')
    """
    conn.execute(
        """
        INSERT INTO notes (
            content,
            source,
            severity,
            note_type,
            reference_table,
            reference_id
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (reason, source, severity, note_type, reference_table, reference_id)
    )
    conn.commit()

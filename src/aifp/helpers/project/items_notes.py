"""
AIFP Helper Functions - Project Items & Notes

Item and note management operations for project database.
Implements CRUD and query operations for lowest-level work items
and project documentation notes.

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.

Helpers in this file:
- get_items_for_task: Get items for task with optional status filter
- get_items_for_subtask: Get items for subtask with optional status filter
- get_items_for_sidequest: Get items for sidequest with optional status filter
- get_incomplete_items: Get incomplete items for any parent type
- delete_item: Delete item with status validation (only pending)
- add_note: Add note to project database
- get_notes_comprehensive: Advanced note search with filters
- search_notes: Search note content with optional filters
- update_note: Update note metadata
- delete_note: Delete note (discouraged)
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Tuple

# Import global utilities
import sys
from pathlib import Path
# Add parent directory to path to import from helpers.utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_return_statements

# Import common project utilities (DRY principle)
from ._common import (
    _open_connection,
    _check_entity_exists,
    _create_deletion_note,
    _validate_severity,
    VALID_MILESTONE_STATUSES,
    VALID_NOTE_TYPES,
    VALID_NOTE_SOURCES,
    VALID_SEVERITY_LEVELS,
    VALID_REFERENCE_TABLES
)


# ============================================================================
# Global Constants - Item Statuses
# ============================================================================

# Items have different statuses than tasks (no 'blocked')
from typing import Final
VALID_ITEM_STATUSES: Final[frozenset[str]] = frozenset([
    'pending', 'in_progress', 'completed'
])


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class ItemRecord:
    """Immutable item record from database."""
    id: int
    reference_table: str
    reference_id: int
    name: str
    status: str
    description: Optional[str]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class NoteRecord:
    """Immutable note record from database."""
    id: int
    content: str
    note_type: str
    reference_table: Optional[str]
    reference_id: Optional[int]
    source: str
    directive_name: Optional[str]
    severity: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ItemQueryResult:
    """Result of item query operation."""
    success: bool
    items: Tuple[ItemRecord, ...] = ()
    error: Optional[str] = None


@dataclass(frozen=True)
class DeleteResult:
    """Result of delete operation."""
    success: bool
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AddResult:
    """Result of add operation."""
    success: bool
    id: Optional[int] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class UpdateResult:
    """Result of update operation."""
    success: bool
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class NoteQueryResult:
    """Result of note query operation."""
    success: bool
    notes: Tuple[NoteRecord, ...] = ()
    error: Optional[str] = None


# ============================================================================
# Validation Functions
# ============================================================================

def _validate_item_status(status: str) -> bool:
    """
    Pure: Validate item status value.

    Args:
        status: Status value to validate

    Returns:
        True if valid, False otherwise
    """
    return status in VALID_ITEM_STATUSES


def _validate_note_type(note_type: str) -> bool:
    """
    Pure: Validate note type value.

    Args:
        note_type: Note type value to validate

    Returns:
        True if valid, False otherwise
    """
    return note_type in VALID_NOTE_TYPES


def _validate_note_source(source: str) -> bool:
    """
    Pure: Validate note source value.

    Args:
        source: Source value to validate

    Returns:
        True if valid, False otherwise
    """
    return source in VALID_NOTE_SOURCES


def _normalize_table_name(table: str) -> str:
    """
    Pure: Normalize table name (singular to plural).

    Args:
        table: Table name (singular or plural)

    Returns:
        Normalized plural table name
    """
    # Handle singular forms
    if table == 'task':
        return 'tasks'
    elif table == 'subtask':
        return 'subtasks'
    elif table == 'sidequest':
        return 'sidequests'
    else:
        return table  # Already plural or unknown


# ============================================================================
# Effect Functions - Item Operations
# ============================================================================

def _query_items_by_reference(
    conn: sqlite3.Connection,
    reference_table: str,
    reference_id: int,
    status: Optional[str]
) -> Tuple[ItemRecord, ...]:
    """
    Effect: Query items by reference table and ID.

    Args:
        conn: Database connection
        reference_table: Reference table name
        reference_id: Reference ID
        status: Optional status filter

    Returns:
        Tuple of item records
    """
    if status is None:
        cursor = conn.execute(
            "SELECT * FROM items WHERE reference_table = ? AND reference_id = ?",
            (reference_table, reference_id)
        )
    else:
        cursor = conn.execute(
            "SELECT * FROM items WHERE reference_table = ? AND reference_id = ? AND status = ?",
            (reference_table, reference_id, status)
        )

    rows = cursor.fetchall()
    return tuple(
        ItemRecord(
            id=row['id'],
            reference_table=row['reference_table'],
            reference_id=row['reference_id'],
            name=row['name'],
            status=row['status'],
            description=row['description'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        for row in rows
    )


def _query_incomplete_items_by_reference(
    conn: sqlite3.Connection,
    reference_table: str,
    reference_id: int
) -> Tuple[ItemRecord, ...]:
    """
    Effect: Query incomplete items by reference table and ID.

    Args:
        conn: Database connection
        reference_table: Reference table name
        reference_id: Reference ID

    Returns:
        Tuple of item records
    """
    cursor = conn.execute(
        "SELECT * FROM items WHERE reference_table = ? AND reference_id = ? AND status != 'completed'",
        (reference_table, reference_id)
    )
    rows = cursor.fetchall()
    return tuple(
        ItemRecord(
            id=row['id'],
            reference_table=row['reference_table'],
            reference_id=row['reference_id'],
            name=row['name'],
            status=row['status'],
            description=row['description'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        for row in rows
    )


def _delete_item(conn: sqlite3.Connection, item_id: int) -> None:
    """
    Effect: Delete item from database.

    Args:
        conn: Database connection
        item_id: Item ID
    """
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()


# ============================================================================
# Effect Functions - Note Operations
# ============================================================================

def _insert_note(
    conn: sqlite3.Connection,
    content: str,
    note_type: str,
    reference_table: Optional[str],
    reference_id: Optional[int],
    source: str,
    severity: str,
    directive_name: Optional[str]
) -> int:
    """
    Effect: Insert note into database.

    Args:
        conn: Database connection
        content: Note content
        note_type: Note type
        reference_table: Optional reference table
        reference_id: Optional reference ID
        source: Note source
        severity: Severity level
        directive_name: Optional directive name

    Returns:
        New note ID
    """
    cursor = conn.execute(
        """
        INSERT INTO notes (content, note_type, reference_table, reference_id, source, severity, directive_name)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (content, note_type, reference_table, reference_id, source, severity, directive_name)
    )
    conn.commit()
    return cursor.lastrowid


def _query_notes_comprehensive(
    conn: sqlite3.Connection,
    note_type: Optional[str],
    reference_table: Optional[str],
    reference_id: Optional[int],
    source: Optional[str],
    severity: Optional[str],
    directive_name: Optional[str]
) -> Tuple[NoteRecord, ...]:
    """
    Effect: Query notes with multiple filters.

    Args:
        conn: Database connection
        note_type: Optional note type filter
        reference_table: Optional reference table filter
        reference_id: Optional reference ID filter
        source: Optional source filter
        severity: Optional severity filter
        directive_name: Optional directive name filter

    Returns:
        Tuple of note records
    """
    # Build dynamic query
    where_clauses = []
    values = []

    if note_type is not None:
        where_clauses.append("note_type = ?")
        values.append(note_type)

    if reference_table is not None:
        where_clauses.append("reference_table = ?")
        values.append(reference_table)

    if reference_id is not None:
        where_clauses.append("reference_id = ?")
        values.append(reference_id)

    if source is not None:
        where_clauses.append("source = ?")
        values.append(source)

    if severity is not None:
        where_clauses.append("severity = ?")
        values.append(severity)

    if directive_name is not None:
        where_clauses.append("directive_name = ?")
        values.append(directive_name)

    # Build final query
    query = "SELECT * FROM notes"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, values)
    rows = cursor.fetchall()
    return tuple(
        NoteRecord(
            id=row['id'],
            content=row['content'],
            note_type=row['note_type'],
            reference_table=row['reference_table'],
            reference_id=row['reference_id'],
            source=row['source'],
            directive_name=row['directive_name'],
            severity=row['severity'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        for row in rows
    )


def _search_notes(
    conn: sqlite3.Connection,
    search_string: str,
    note_type: Optional[str],
    reference_table: Optional[str],
    reference_id: Optional[int],
    source: Optional[str],
    severity: Optional[str],
    directive_name: Optional[str]
) -> Tuple[NoteRecord, ...]:
    """
    Effect: Search notes by content with optional filters.

    Args:
        conn: Database connection
        search_string: Search string for content
        note_type: Optional note type filter
        reference_table: Optional reference table filter
        reference_id: Optional reference ID filter
        source: Optional source filter
        severity: Optional severity filter
        directive_name: Optional directive name filter

    Returns:
        Tuple of note records
    """
    # Build dynamic query
    where_clauses = ["content LIKE ?"]
    values = [f"%{search_string}%"]

    if note_type is not None:
        where_clauses.append("note_type = ?")
        values.append(note_type)

    if reference_table is not None:
        where_clauses.append("reference_table = ?")
        values.append(reference_table)

    if reference_id is not None:
        where_clauses.append("reference_id = ?")
        values.append(reference_id)

    if source is not None:
        where_clauses.append("source = ?")
        values.append(source)

    if severity is not None:
        where_clauses.append("severity = ?")
        values.append(severity)

    if directive_name is not None:
        where_clauses.append("directive_name = ?")
        values.append(directive_name)

    # Build final query
    query = "SELECT * FROM notes WHERE " + " AND ".join(where_clauses)
    query += " ORDER BY created_at DESC"

    cursor = conn.execute(query, values)
    rows = cursor.fetchall()
    return tuple(
        NoteRecord(
            id=row['id'],
            content=row['content'],
            note_type=row['note_type'],
            reference_table=row['reference_table'],
            reference_id=row['reference_id'],
            source=row['source'],
            directive_name=row['directive_name'],
            severity=row['severity'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
        for row in rows
    )


def _update_note_fields(
    conn: sqlite3.Connection,
    note_id: int,
    content: Optional[str],
    note_type: Optional[str],
    reference_table: Optional[str],
    reference_id: Optional[int],
    source: Optional[str],
    severity: Optional[str],
    directive_name: Optional[str]
) -> None:
    """
    Effect: Update note fields (only non-None values).

    Args:
        conn: Database connection
        note_id: Note ID
        content: New content (None = don't update)
        note_type: New note type (None = don't update)
        reference_table: New reference table (None = don't update)
        reference_id: New reference ID (None = don't update)
        source: New source (None = don't update)
        severity: New severity (None = don't update)
        directive_name: New directive name (None = don't update)
    """
    # Build dynamic UPDATE query
    fields = []
    values = []

    if content is not None:
        fields.append("content = ?")
        values.append(content)

    if note_type is not None:
        fields.append("note_type = ?")
        values.append(note_type)

    if reference_table is not None:
        fields.append("reference_table = ?")
        values.append(reference_table)

    if reference_id is not None:
        fields.append("reference_id = ?")
        values.append(reference_id)

    if source is not None:
        fields.append("source = ?")
        values.append(source)

    if severity is not None:
        fields.append("severity = ?")
        values.append(severity)

    if directive_name is not None:
        fields.append("directive_name = ?")
        values.append(directive_name)

    if not fields:
        return  # Nothing to update

    # Add note_id to values
    values.append(note_id)

    # Execute update
    query = f"UPDATE notes SET {', '.join(fields)} WHERE id = ?"
    conn.execute(query, values)
    conn.commit()


def _delete_note(conn: sqlite3.Connection, note_id: int) -> None:
    """
    Effect: Delete note from database.

    Args:
        conn: Database connection
        note_id: Note ID
    """
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()


# ============================================================================
# Public Helper Functions - Items
# ============================================================================

def get_items_for_task(
    db_path: str,
    task_id: int,
    status: Optional[str] = None
) -> ItemQueryResult:
    """
    Get items for task, optionally filtered by status.

    Args:
        db_path: Path to project.db
        task_id: Task ID
        status: Optional status filter ('pending', 'in_progress', 'completed')

    Returns:
        ItemQueryResult with items
    """
    # Validate status if provided
    if status is not None and not _validate_item_status(status):
        return ItemQueryResult(
            success=False,
            error=f"Invalid status: {status}. Must be one of: {', '.join(VALID_ITEM_STATUSES)}"
        )

    conn = _open_connection(db_path)

    try:
        items = _query_items_by_reference(conn, "tasks", task_id, status)
        conn.close()

        return ItemQueryResult(
            success=True,
            items=items
        )

    except Exception as e:
        conn.close()
        return ItemQueryResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def get_items_for_subtask(
    db_path: str,
    subtask_id: int,
    status: Optional[str] = None
) -> ItemQueryResult:
    """
    Get items for subtask, optionally filtered by status.

    Args:
        db_path: Path to project.db
        subtask_id: Subtask ID
        status: Optional status filter ('pending', 'in_progress', 'completed')

    Returns:
        ItemQueryResult with items
    """
    # Validate status if provided
    if status is not None and not _validate_item_status(status):
        return ItemQueryResult(
            success=False,
            error=f"Invalid status: {status}. Must be one of: {', '.join(VALID_ITEM_STATUSES)}"
        )

    conn = _open_connection(db_path)

    try:
        items = _query_items_by_reference(conn, "subtasks", subtask_id, status)
        conn.close()

        return ItemQueryResult(
            success=True,
            items=items
        )

    except Exception as e:
        conn.close()
        return ItemQueryResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def get_items_for_sidequest(
    db_path: str,
    sidequest_id: int,
    status: Optional[str] = None
) -> ItemQueryResult:
    """
    Get items for sidequest, optionally filtered by status.

    Args:
        db_path: Path to project.db
        sidequest_id: Sidequest ID
        status: Optional status filter ('pending', 'in_progress', 'completed')

    Returns:
        ItemQueryResult with items
    """
    # Validate status if provided
    if status is not None and not _validate_item_status(status):
        return ItemQueryResult(
            success=False,
            error=f"Invalid status: {status}. Must be one of: {', '.join(VALID_ITEM_STATUSES)}"
        )

    conn = _open_connection(db_path)

    try:
        items = _query_items_by_reference(conn, "sidequests", sidequest_id, status)
        conn.close()

        return ItemQueryResult(
            success=True,
            items=items
        )

    except Exception as e:
        conn.close()
        return ItemQueryResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def get_incomplete_items(
    db_path: str,
    for_table: str,
    for_id: int
) -> ItemQueryResult:
    """
    Get incomplete items for any parent type.

    Args:
        db_path: Path to project.db
        for_table: Reference table ("tasks", "subtasks", "sidequests" - accepts singular)
        for_id: Parent ID

    Returns:
        ItemQueryResult with incomplete items
    """
    # Normalize table name (singular to plural)
    normalized_table = _normalize_table_name(for_table)

    # Validate table name
    valid_tables = {'tasks', 'subtasks', 'sidequests'}
    if normalized_table not in valid_tables:
        return ItemQueryResult(
            success=False,
            error=f"Invalid table: {for_table}. Must be one of: {', '.join(valid_tables)}"
        )

    conn = _open_connection(db_path)

    try:
        items = _query_incomplete_items_by_reference(conn, normalized_table, for_id)
        conn.close()

        return ItemQueryResult(
            success=True,
            items=items
        )

    except Exception as e:
        conn.close()
        return ItemQueryResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def delete_item(
    db_path: str,
    id: int,
    note_reason: str,
    note_severity: str,
    note_source: str,
    note_type: str = "entry_deletion"
) -> DeleteResult:
    """
    Delete item with status validation (only pending items can be deleted).

    Args:
        db_path: Path to project.db
        id: Item ID
        note_reason: Deletion reason
        note_severity: Note severity ('info', 'warning', 'error')
        note_source: Note source ('ai' or 'user')
        note_type: Note type ('entry_deletion')

    Returns:
        DeleteResult with success status
    """
    conn = _open_connection(db_path)

    try:
        # Check item exists
        if not _check_entity_exists(conn, "items", id):
            conn.close()
            return DeleteResult(
                success=False,
                error=f"Item ID {id} not found"
            )

        # Check item status (only pending can be deleted)
        cursor = conn.execute("SELECT status FROM items WHERE id = ?", (id,))
        row = cursor.fetchone()
        item_status = row['status']

        if item_status != 'pending':
            conn.close()
            return DeleteResult(
                success=False,
                error=f"Cannot delete item: status is '{item_status}'. Only 'pending' items can be deleted."
            )

        # Create audit note
        _create_deletion_note(conn, "items", id, note_reason, note_severity, note_source, note_type)

        # Delete item
        _delete_item(conn, id)
        conn.close()

        # Fetch return statements
        return_stmts = get_return_statements("delete_item")

        return DeleteResult(
            success=True,
            return_statements=return_stmts
        )

    except Exception as e:
        conn.close()
        return DeleteResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


# ============================================================================
# Public Helper Functions - Notes
# ============================================================================

def add_note(
    db_path: str,
    content: str,
    note_type: str,
    reference_table: Optional[str] = None,
    reference_id: Optional[int] = None,
    source: str = "ai",
    severity: str = "info",
    directive_name: Optional[str] = None
) -> AddResult:
    """
    Add note to project database.

    Args:
        db_path: Path to project.db
        content: Note content/message
        note_type: Note type ('clarification', 'pivot', 'research', 'entry_deletion', etc.)
        reference_table: Optional table name this note references
        reference_id: Optional ID of the referenced table entry
        source: Note source ('ai', 'user', or 'directive')
        severity: Severity level ('info', 'warning', 'error')
        directive_name: Optional directive context for note

    Returns:
        AddResult with new note ID on success
    """
    # Validate note_type
    if not _validate_note_type(note_type):
        return AddResult(
            success=False,
            error=f"Invalid note_type: {note_type}. Must be one of: {', '.join(VALID_NOTE_TYPES)}"
        )

    # Validate source
    if not _validate_note_source(source):
        return AddResult(
            success=False,
            error=f"Invalid source: {source}. Must be one of: {', '.join(VALID_NOTE_SOURCES)}"
        )

    # Validate severity
    if not _validate_severity(severity):
        return AddResult(
            success=False,
            error=f"Invalid severity: {severity}. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"
        )

    conn = _open_connection(db_path)

    try:
        # Insert note
        note_id = _insert_note(
            conn, content, note_type, reference_table, reference_id, source, severity, directive_name
        )
        conn.close()

        # Fetch return statements
        return_stmts = get_return_statements("add_note")

        return AddResult(
            success=True,
            id=note_id,
            return_statements=return_stmts
        )

    except Exception as e:
        conn.close()
        return AddResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def get_notes_comprehensive(
    db_path: str,
    note_type: Optional[str] = None,
    reference_table: Optional[str] = None,
    reference_id: Optional[int] = None,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    directive_name: Optional[str] = None
) -> NoteQueryResult:
    """
    Advanced note search with filters.

    Args:
        db_path: Path to project.db
        note_type: Optional filter by note_type
        reference_table: Optional filter by reference table
        reference_id: Optional filter by reference ID
        source: Optional filter by source ('ai', 'user', 'directive')
        severity: Optional filter by severity ('info', 'warning', 'error')
        directive_name: Optional filter by directive name

    Returns:
        NoteQueryResult with filtered notes
    """
    # Validate filters if provided
    if note_type is not None and not _validate_note_type(note_type):
        return NoteQueryResult(
            success=False,
            error=f"Invalid note_type: {note_type}. Must be one of: {', '.join(VALID_NOTE_TYPES)}"
        )

    if source is not None and not _validate_note_source(source):
        return NoteQueryResult(
            success=False,
            error=f"Invalid source: {source}. Must be one of: {', '.join(VALID_NOTE_SOURCES)}"
        )

    if severity is not None and not _validate_severity(severity):
        return NoteQueryResult(
            success=False,
            error=f"Invalid severity: {severity}. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"
        )

    conn = _open_connection(db_path)

    try:
        notes = _query_notes_comprehensive(
            conn, note_type, reference_table, reference_id, source, severity, directive_name
        )
        conn.close()

        return NoteQueryResult(
            success=True,
            notes=notes
        )

    except Exception as e:
        conn.close()
        return NoteQueryResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def search_notes(
    db_path: str,
    search_string: str,
    note_type: Optional[str] = None,
    reference_table: Optional[str] = None,
    reference_id: Optional[int] = None,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    directive_name: Optional[str] = None
) -> NoteQueryResult:
    """
    Search note content with optional filters.

    Args:
        db_path: Path to project.db
        search_string: Search string for note content
        note_type: Optional filter by note_type
        reference_table: Optional filter by reference table
        reference_id: Optional filter by reference ID
        source: Optional filter by source
        severity: Optional filter by severity
        directive_name: Optional filter by directive name

    Returns:
        NoteQueryResult with matching notes
    """
    # Validate filters if provided
    if note_type is not None and not _validate_note_type(note_type):
        return NoteQueryResult(
            success=False,
            error=f"Invalid note_type: {note_type}. Must be one of: {', '.join(VALID_NOTE_TYPES)}"
        )

    if source is not None and not _validate_note_source(source):
        return NoteQueryResult(
            success=False,
            error=f"Invalid source: {source}. Must be one of: {', '.join(VALID_NOTE_SOURCES)}"
        )

    if severity is not None and not _validate_severity(severity):
        return NoteQueryResult(
            success=False,
            error=f"Invalid severity: {severity}. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"
        )

    conn = _open_connection(db_path)

    try:
        notes = _search_notes(
            conn, search_string, note_type, reference_table, reference_id, source, severity, directive_name
        )
        conn.close()

        return NoteQueryResult(
            success=True,
            notes=notes
        )

    except Exception as e:
        conn.close()
        return NoteQueryResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def update_note(
    db_path: str,
    id: int,
    content: Optional[str] = None,
    note_type: Optional[str] = None,
    reference_table: Optional[str] = None,
    reference_id: Optional[int] = None,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    directive_name: Optional[str] = None
) -> UpdateResult:
    """
    Update note metadata.

    Args:
        db_path: Path to project.db
        id: Note ID to update
        content: New content (None = don't update)
        note_type: New note_type (None = don't update)
        reference_table: New reference table (None = don't update)
        reference_id: New reference ID (None = don't update)
        source: New source (None = don't update)
        severity: New severity (None = don't update)
        directive_name: New directive name (None = don't update)

    Returns:
        UpdateResult with success status
    """
    # Validate fields if provided
    if note_type is not None and not _validate_note_type(note_type):
        return UpdateResult(
            success=False,
            error=f"Invalid note_type: {note_type}. Must be one of: {', '.join(VALID_NOTE_TYPES)}"
        )

    if source is not None and not _validate_note_source(source):
        return UpdateResult(
            success=False,
            error=f"Invalid source: {source}. Must be one of: {', '.join(VALID_NOTE_SOURCES)}"
        )

    if severity is not None and not _validate_severity(severity):
        return UpdateResult(
            success=False,
            error=f"Invalid severity: {severity}. Must be one of: {', '.join(VALID_SEVERITY_LEVELS)}"
        )

    conn = _open_connection(db_path)

    try:
        # Check note exists
        if not _check_entity_exists(conn, "notes", id):
            conn.close()
            return UpdateResult(
                success=False,
                error=f"Note ID {id} not found"
            )

        # Update note
        _update_note_fields(conn, id, content, note_type, reference_table, reference_id, source, severity, directive_name)
        conn.close()

        # Fetch return statements
        return_stmts = get_return_statements("update_note")

        return UpdateResult(
            success=True,
            return_statements=return_stmts
        )

    except Exception as e:
        conn.close()
        return UpdateResult(
            success=False,
            error=f"Database error: {str(e)}"
        )


def delete_note(
    db_path: str,
    id: int
) -> DeleteResult:
    """
    Delete note (discouraged - notes should be preserved for audit trail).

    Args:
        db_path: Path to project.db
        id: Note ID to delete

    Returns:
        DeleteResult with success status
    """
    conn = _open_connection(db_path)

    try:
        # Check note exists
        if not _check_entity_exists(conn, "notes", id):
            conn.close()
            return DeleteResult(
                success=False,
                error=f"Note ID {id} not found"
            )

        # Delete note
        _delete_note(conn, id)
        conn.close()

        # Fetch return statements
        return_stmts = get_return_statements("delete_note")

        return DeleteResult(
            success=True,
            return_statements=return_stmts
        )

    except Exception as e:
        conn.close()
        return DeleteResult(
            success=False,
            error=f"Database error: {str(e)}"
        )

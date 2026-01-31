"""
AIFP Helper Functions - Project Interactions

Function interaction/dependency management for project database.
Tracks relationships between functions (calls, compositions, pipes, etc.).

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.

Helpers in this file:
- add_interaction: Add single function dependency/interaction (by function names)
- add_interactions: Add multiple interactions at once (by function IDs)
- update_interaction: Update interaction metadata
- delete_interaction: Delete interaction with audit trail
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Tuple

# Import global utilities
from ..utils import get_return_statements
from ._common import _open_connection, _check_function_exists, _create_deletion_note


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class AddInteractionResult:
    """Result of adding single interaction."""
    success: bool
    id: Optional[int] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class AddInteractionsResult:
    """Result of adding multiple interactions."""
    success: bool
    ids: Tuple[int, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class UpdateInteractionResult:
    """Result of updating interaction."""
    success: bool
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class DeleteInteractionResult:
    """Result of deleting interaction."""
    success: bool
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


# ============================================================================
# Pure Helper Functions
# ============================================================================

def validate_interaction_type(interaction_type: str) -> bool:
    """
    Validate that interaction type is one of the allowed values.

    Pure function - no side effects, deterministic.

    Args:
        interaction_type: Interaction type string to validate

    Returns:
        True if valid, False otherwise
    """
    valid_types = {'call', 'chain', 'borrow', 'compose', 'pipe'}
    return interaction_type in valid_types


def build_update_query(
    interaction_id: int,
    source_function_id: Optional[int],
    target_function_id: Optional[int],
    interaction_type: Optional[str],
    description: Optional[str]
) -> Tuple[str, Tuple]:
    """
    Build SQL UPDATE query with only non-NULL fields.

    Pure function - deterministic query building.

    Args:
        interaction_id: Interaction ID to update
        source_function_id: New source function ID (None = don't update)
        target_function_id: New target function ID (None = don't update)
        interaction_type: New interaction type (None = don't update)
        description: New description (None = don't update)

    Returns:
        Tuple of (sql_query, parameters)
    """
    updates = []
    params_list = []

    if source_function_id is not None:
        updates.append("source_function_id = ?")
        params_list.append(source_function_id)

    if target_function_id is not None:
        updates.append("target_function_id = ?")
        params_list.append(target_function_id)

    if interaction_type is not None:
        updates.append("interaction_type = ?")
        params_list.append(interaction_type)

    if description is not None:
        updates.append("description = ?")
        params_list.append(description)

    # Build query
    sql = f"UPDATE interactions SET {', '.join(updates)} WHERE id = ?"
    params_list.append(interaction_id)

    return (sql, tuple(params_list))


# ============================================================================
# Database Effect Functions
# ============================================================================



def _check_interaction_exists(conn: sqlite3.Connection, interaction_id: int) -> bool:
    """
    Effect: Check if interaction ID exists in database.

    Args:
        conn: Database connection
        interaction_id: Interaction ID to check

    Returns:
        True if exists, False otherwise
    """
    cursor = conn.execute("SELECT id FROM interactions WHERE id = ?", (interaction_id,))
    return cursor.fetchone() is not None


def _get_function_id_by_name(conn: sqlite3.Connection, function_name: str) -> Optional[int]:
    """
    Effect: Get function ID by name.

    Args:
        conn: Database connection
        function_name: Function name to look up

    Returns:
        Function ID or None if not found
    """
    cursor = conn.execute("SELECT id FROM functions WHERE name = ? LIMIT 1", (function_name,))
    row = cursor.fetchone()
    return row["id"] if row else None


def _add_interaction_effect(
    conn: sqlite3.Connection,
    source_function_id: int,
    target_function_id: int,
    interaction_type: str,
    description: Optional[str] = None
) -> int:
    """
    Effect: Insert interaction into database.

    Args:
        conn: Database connection
        source_function_id: Source function ID
        target_function_id: Target function ID
        interaction_type: Interaction type
        description: Optional description

    Returns:
        Inserted interaction ID
    """
    cursor = conn.execute(
        """
        INSERT INTO interactions (source_function_id, target_function_id, interaction_type, description)
        VALUES (?, ?, ?, ?)
        """,
        (source_function_id, target_function_id, interaction_type, description)
    )
    conn.commit()
    return cursor.lastrowid


def _add_interactions_batch_effect(
    conn: sqlite3.Connection,
    interactions: List[Tuple[int, int, str, Optional[str]]]
) -> Tuple[int, ...]:
    """
    Effect: Insert multiple interactions in transaction.

    Args:
        conn: Database connection
        interactions: List of (source_function_id, target_function_id, interaction_type, description) tuples

    Returns:
        Tuple of inserted interaction IDs in same order
    """
    cursor = conn.cursor()
    ids = []

    try:
        for source_function_id, target_function_id, interaction_type, description in interactions:
            cursor.execute(
                """
                INSERT INTO interactions (source_function_id, target_function_id, interaction_type, description)
                VALUES (?, ?, ?, ?)
                """,
                (source_function_id, target_function_id, interaction_type, description)
            )
            ids.append(cursor.lastrowid)

        conn.commit()
        return tuple(ids)

    except Exception as e:
        conn.rollback()
        raise e


def _update_interaction_effect(conn: sqlite3.Connection, sql: str, params: Tuple) -> None:
    """
    Effect: Execute interaction update query.

    Args:
        conn: Database connection
        sql: UPDATE query
        params: Query parameters
    """
    conn.execute(sql, params)
    conn.commit()


def _delete_interaction_effect(
    conn: sqlite3.Connection,
    interaction_id: int,
) -> None:
    """
    Effect: Delete interaction from database.

    Args:
        conn: Database connection
        interaction_id: Interaction ID to delete
    """
    conn.execute("DELETE FROM interactions WHERE id = ?", (interaction_id,))
    conn.commit()


# ============================================================================
# Public API Functions (MCP Tools)
# ============================================================================

def add_interaction(
    db_path: str,
    source: str,
    target: str,
    interaction_type: str
) -> AddInteractionResult:
    """
    Add function dependency/interaction (by function names).

    Creates interaction record in interactions table. Function names are
    resolved to IDs internally.

    Args:
        db_path: Path to project.db
        source: Source function name (the function making the call/reference)
        target: Target function name (the function being called/referenced)
        interaction_type: Interaction type ('call', 'chain', 'borrow', 'compose', 'pipe')

    Returns:
        AddInteractionResult with success status and new interaction ID

    Example:
        >>> # Function 'process_data' calls 'validate_input'
        >>> result = add_interaction(
        ...     "project.db",
        ...     source="process_data_id_42",
        ...     target="validate_input_id_15",
        ...     interaction_type="call"
        ... )
        >>> result.success
        True
        >>> result.id
        1
    """
    # Validate interaction type
    if not validate_interaction_type(interaction_type):
        return AddInteractionResult(
            success=False,
            error=f"Invalid interaction type: {interaction_type}. Must be one of: call, chain, borrow, compose, pipe"
        )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Resolve function names to IDs
        source_function_id = _get_function_id_by_name(conn, source)
        if source_function_id is None:
            return AddInteractionResult(
                success=False,
                error=f"Source function not found: {source}"
            )

        target_function_id = _get_function_id_by_name(conn, target)
        if target_function_id is None:
            return AddInteractionResult(
                success=False,
                error=f"Target function not found: {target}"
            )

        # Effect: add interaction
        new_interaction_id = _add_interaction_effect(
            conn,
            source_function_id,
            target_function_id,
            interaction_type
        )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("add_interaction")

        return AddInteractionResult(
            success=True,
            id=new_interaction_id,
            return_statements=return_statements
        )

    except Exception as e:
        return AddInteractionResult(
            success=False,
            error=f"Failed to add interaction: {str(e)}"
        )

    finally:
        conn.close()


def add_interactions(
    db_path: str,
    interactions: List[Tuple[int, int, str, Optional[str]]]
) -> AddInteractionsResult:
    """
    Add multiple interactions at once (by function IDs).

    More efficient than multiple single-interaction calls. Uses function IDs
    directly instead of names for better performance.

    Args:
        db_path: Path to project.db
        interactions: List of (source_function_id, target_function_id, interaction_type, description) tuples
            Interaction types: 'call', 'chain', 'borrow', 'compose', 'pipe'

    Returns:
        AddInteractionsResult with success status and inserted interaction IDs

    Example:
        >>> # Multiple function calls
        >>> interactions = [
        ...     (42, 15, 'call', 'Validates input'),
        ...     (42, 16, 'call', 'Transforms data'),
        ...     (42, 17, 'pipe', 'Pipes to formatter')
        ... ]
        >>> result = add_interactions("project.db", interactions)
        >>> result.success
        True
        >>> len(result.ids)
        3
    """
    # Validate input
    if not interactions:
        return AddInteractionsResult(
            success=False,
            error="Interactions list cannot be empty"
        )

    # Validate all interaction types
    for source_id, target_id, interaction_type, description in interactions:
        if not validate_interaction_type(interaction_type):
            return AddInteractionsResult(
                success=False,
                error=f"Invalid interaction type: {interaction_type}. Must be one of: call, chain, borrow, compose, pipe"
            )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Validate all function IDs exist
        for source_id, target_id, interaction_type, description in interactions:
            if not _check_function_exists(conn, source_id):
                return AddInteractionsResult(
                    success=False,
                    error=f"Source function with ID {source_id} not found"
                )

            if not _check_function_exists(conn, target_id):
                return AddInteractionsResult(
                    success=False,
                    error=f"Target function with ID {target_id} not found"
                )

        # Effect: add all interactions in transaction
        inserted_ids = _add_interactions_batch_effect(conn, interactions)

        # Success - fetch return statements from core database
        return_statements = get_return_statements("add_interactions")

        return AddInteractionsResult(
            success=True,
            ids=inserted_ids,
            return_statements=return_statements
        )

    except Exception as e:
        return AddInteractionsResult(
            success=False,
            error=f"Batch add failed: {str(e)}"
        )

    finally:
        conn.close()


def update_interaction(
    db_path: str,
    interaction_id: int,
    source_function_id: Optional[int] = None,
    target_function_id: Optional[int] = None,
    interaction_type: Optional[str] = None,
    description: Optional[str] = None
) -> UpdateInteractionResult:
    """
    Update interaction metadata.

    Only updates non-NULL parameters. Can change source, target, type, or description.

    Args:
        db_path: Path to project.db
        interaction_id: Interaction ID to update
        source_function_id: New source function ID (None = don't update)
        target_function_id: New target function ID (None = don't update)
        interaction_type: New interaction type (None = don't update)
        description: New description (None = don't update)

    Returns:
        UpdateInteractionResult with success status

    Example:
        >>> # Update interaction type from 'call' to 'compose'
        >>> result = update_interaction("project.db", 1, interaction_type='compose')
        >>> result.success
        True

        >>> # Update description only
        >>> result = update_interaction(
        ...     "project.db",
        ...     1,
        ...     description="Composes validation with transformation"
        ... )
        >>> result.success
        True
    """
    # Validate at least one parameter is provided
    if all(v is None for v in [source_function_id, target_function_id, interaction_type, description]):
        return UpdateInteractionResult(
            success=False,
            error="At least one parameter must be provided for update"
        )

    # Validate interaction type if provided
    if interaction_type is not None and not validate_interaction_type(interaction_type):
        return UpdateInteractionResult(
            success=False,
            error=f"Invalid interaction type: {interaction_type}. Must be one of: call, chain, borrow, compose, pipe"
        )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if interaction exists
        if not _check_interaction_exists(conn, interaction_id):
            return UpdateInteractionResult(
                success=False,
                error=f"Interaction with ID {interaction_id} not found"
            )

        # Validate new function IDs if provided
        if source_function_id is not None and not _check_function_exists(conn, source_function_id):
            return UpdateInteractionResult(
                success=False,
                error=f"Source function with ID {source_function_id} not found"
            )

        if target_function_id is not None and not _check_function_exists(conn, target_function_id):
            return UpdateInteractionResult(
                success=False,
                error=f"Target function with ID {target_function_id} not found"
            )

        # Pure: build update query
        sql, params = build_update_query(interaction_id, source_function_id, target_function_id, interaction_type, description)

        # Effect: execute update
        _update_interaction_effect(conn, sql, params)

        # Success - fetch return statements from core database
        return_statements = get_return_statements("update_interaction")

        return UpdateInteractionResult(
            success=True,
            return_statements=return_statements
        )

    except Exception as e:
        return UpdateInteractionResult(
            success=False,
            error=f"Failed to update interaction: {str(e)}"
        )

    finally:
        conn.close()


def delete_interaction(
    db_path: str,
    interaction_id: int,
    note_reason: str,
    note_severity: str,
    note_source: str,
    note_type: str = "entry_deletion"
) -> DeleteInteractionResult:
    """
    Delete interaction (internal use, not exposed as MCP tool).

    Removes interaction from database and creates audit note.

    Args:
        db_path: Path to project.db
        interaction_id: Interaction ID to delete
        note_reason: Deletion reason
        note_severity: 'info', 'warning', 'error'
        note_source: 'ai' or 'user'
        note_type: Note type (default: 'entry_deletion')

    Returns:
        DeleteInteractionResult with success status

    Example:
        >>> result = delete_interaction(
        ...     "project.db",
        ...     1,
        ...     note_reason="Function dependency removed from code",
        ...     note_severity="info",
        ...     note_source="ai"
        ... )
        >>> result.success
        True
    """
    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if interaction exists
        if not _check_interaction_exists(conn, interaction_id):
            return DeleteInteractionResult(
                success=False,
                error=f"Interaction with ID {interaction_id} not found"
            )

        # Create note entry
        _create_deletion_note(
            conn,
            "interactions",
            interaction_id,
            note_reason,
            note_severity,
            note_source,
            note_type
        )

        # Delete interaction
        _delete_interaction_effect(conn, interaction_id)

        # Success - fetch return statements from core database
        return_statements = get_return_statements("delete_interaction")

        return DeleteInteractionResult(
            success=True,
            return_statements=return_statements
        )

    except Exception as e:
        return DeleteInteractionResult(
            success=False,
            error=f"Failed to delete interaction: {str(e)}"
        )

    finally:
        conn.close()

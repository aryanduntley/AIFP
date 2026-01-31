"""
AIFP Helper Functions - Project Functions (Part 2)

Function query, update, and deletion operations for project database.
Implements function metadata management and comprehensive deletion validation.

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.

Helpers in this file:
- get_functions_by_file: Get all functions in a file (high-frequency)
- update_function: Update function metadata
- update_functions_for_file: Batch update multiple functions in same file
- update_function_file_location: Move function to different file (internal use)
- delete_function: Delete function with validation and interaction cascade
"""

import sqlite3
import json
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any

# Import global utilities
import sys
from pathlib import Path
# Add parent directory to path to import from helpers.utils
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_return_statements

# Import update_file_timestamp from files_2
sys.path.insert(0, str(Path(__file__).parent))
from files_2 import update_file_timestamp
from ._common import _open_connection, _check_file_exists, _check_function_exists, _create_deletion_note


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class FunctionRecord:
    """Immutable function record from database."""
    id: int
    name: str
    file_id: int
    purpose: Optional[str]
    params: Optional[str]  # JSON string
    returns: Optional[str]  # JSON string
    purity_score: Optional[float]
    is_reserved: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class FunctionsQueryResult:
    """Result of functions by file lookup operation."""
    success: bool
    functions: Tuple[FunctionRecord, ...] = ()
    error: Optional[str] = None


@dataclass(frozen=True)
class UpdateResult:
    """Result of function update operation."""
    success: bool
    function_id: Optional[int] = None
    file_id: Optional[int] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class BatchUpdateResult:
    """Result of batch function update operation."""
    success: bool
    updated_count: Optional[int] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class LocationUpdateResult:
    """Result of function file location update."""
    success: bool
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class TypeRelationship:
    """Type-function relationship."""
    type_id: int
    type_name: str
    role: str


@dataclass(frozen=True)
class DeleteResult:
    """Result of function deletion operation."""
    success: bool
    deleted_function_id: Optional[int] = None
    file_id: Optional[int] = None
    error: Optional[str] = None
    type_relationships: Tuple[TypeRelationship, ...] = ()
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


# ============================================================================
# Pure Helper Functions
# ============================================================================

def validate_function_id_pattern(name: str, function_id: int) -> bool:
    """
    Validate that function name contains _id_{function_id} pattern.

    Pure function - no side effects, deterministic.

    Args:
        name: Function name to validate
        function_id: Expected function ID

    Returns:
        True if pattern found, False otherwise
    """
    expected_pattern = f"_id_{function_id}"
    return expected_pattern in name


def serialize_params(params: Optional[List[Dict[str, Any]]]) -> Optional[str]:
    """
    Serialize parameters to JSON string.

    Pure function - deterministic serialization.

    Args:
        params: List of parameter objects

    Returns:
        JSON string or None
    """
    if params is None:
        return None
    return json.dumps(params)


def serialize_returns(returns: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Serialize return specification to JSON string.

    Pure function - deterministic serialization.

    Args:
        returns: Return value specification

    Returns:
        JSON string or None
    """
    if returns is None:
        return None
    return json.dumps(returns)


def build_update_query(
    function_id: int,
    name: Optional[str],
    purpose: Optional[str],
    params_json: Optional[str],
    returns_json: Optional[str]
) -> Tuple[str, Tuple]:
    """
    Build SQL UPDATE query with only non-NULL fields.

    Pure function - deterministic query building.

    Args:
        function_id: Function ID to update
        name: New name (None = don't update)
        purpose: New purpose (None = don't update)
        params_json: New params JSON (None = don't update)
        returns_json: New returns JSON (None = don't update)

    Returns:
        Tuple of (sql_query, parameters)
    """
    updates = []
    params_list = []

    if name is not None:
        updates.append("name = ?")
        params_list.append(name)

    if purpose is not None:
        updates.append("purpose = ?")
        params_list.append(purpose)

    if params_json is not None:
        updates.append("params = ?")
        params_list.append(params_json)

    if returns_json is not None:
        updates.append("returns = ?")
        params_list.append(returns_json)

    # Always update timestamp
    updates.append("updated_at = CURRENT_TIMESTAMP")

    # Build query
    sql = f"UPDATE functions SET {', '.join(updates)} WHERE id = ?"
    params_list.append(function_id)

    return (sql, tuple(params_list))


def row_to_function_record(row: sqlite3.Row) -> FunctionRecord:
    """
    Convert database row to immutable FunctionRecord.

    Pure function - deterministic mapping.

    Args:
        row: SQLite row object

    Returns:
        Immutable FunctionRecord
    """
    return FunctionRecord(
        id=row["id"],
        name=row["name"],
        file_id=row["file_id"],
        purpose=row["purpose"],
        params=row["params"],
        returns=row["returns"],
        purity_score=row["purity_score"],
        is_reserved=bool(row["is_reserved"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


# ============================================================================
# Database Effect Functions
# ============================================================================




def _check_is_reserved(conn: sqlite3.Connection, function_id: int) -> bool:
    """
    Effect: Check if function is reserved.

    Args:
        conn: Database connection
        function_id: Function ID to check

    Returns:
        True if reserved, False otherwise
    """
    cursor = conn.execute(
        "SELECT is_reserved FROM functions WHERE id = ?",
        (function_id,)
    )
    row = cursor.fetchone()
    return bool(row["is_reserved"]) if row else False


def _get_function_file_id(conn: sqlite3.Connection, function_id: int) -> Optional[int]:
    """
    Effect: Get file_id for function.

    Args:
        conn: Database connection
        function_id: Function ID

    Returns:
        File ID or None if not found
    """
    cursor = conn.execute(
        "SELECT file_id FROM functions WHERE id = ?",
        (function_id,)
    )
    row = cursor.fetchone()
    return row["file_id"] if row else None


def _get_functions_by_file_effect(
    conn: sqlite3.Connection,
    file_id: int
) -> List[sqlite3.Row]:
    """
    Effect: Query all functions in a file.

    Args:
        conn: Database connection
        file_id: File ID

    Returns:
        List of row objects (empty if no functions)
    """
    cursor = conn.execute(
        "SELECT * FROM functions WHERE file_id = ? ORDER BY created_at",
        (file_id,)
    )
    return cursor.fetchall()


def _update_function_effect(conn: sqlite3.Connection, sql: str, params: Tuple) -> None:
    """
    Effect: Execute function update query.

    Args:
        conn: Database connection
        sql: UPDATE query
        params: Query parameters
    """
    conn.execute(sql, params)
    conn.commit()


def _validate_functions_belong_to_file(
    conn: sqlite3.Connection,
    file_id: int,
    function_ids: List[int]
) -> bool:
    """
    Effect: Validate all functions belong to specified file.

    Args:
        conn: Database connection
        file_id: Expected file ID
        function_ids: List of function IDs to validate

    Returns:
        True if all belong to file, False otherwise
    """
    placeholders = ','.join('?' * len(function_ids))
    cursor = conn.execute(
        f"SELECT COUNT(*) as count FROM functions WHERE id IN ({placeholders}) AND file_id = ?",
        (*function_ids, file_id)
    )
    row = cursor.fetchone()
    return row["count"] == len(function_ids)


def _update_functions_batch_effect(
    conn: sqlite3.Connection,
    updates: List[Tuple[str, Tuple]]
) -> None:
    """
    Effect: Execute multiple function updates in transaction.

    Args:
        conn: Database connection
        updates: List of (sql, params) tuples
    """
    cursor = conn.cursor()

    try:
        for sql, params in updates:
            cursor.execute(sql, params)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e


def _update_function_file_location_effect(
    conn: sqlite3.Connection,
    function_id: int,
    new_file_id: int
) -> None:
    """
    Effect: Update function's file_id.

    Args:
        conn: Database connection
        function_id: Function ID to move
        new_file_id: New file ID
    """
    conn.execute(
        "UPDATE functions SET file_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_file_id, function_id)
    )
    conn.commit()


def _get_type_relationships(
    conn: sqlite3.Connection,
    function_id: int
) -> Tuple[TypeRelationship, ...]:
    """
    Effect: Query type relationships for function.

    Args:
        conn: Database connection
        function_id: Function ID

    Returns:
        Tuple of TypeRelationship objects
    """
    cursor = conn.execute(
        """
        SELECT t.id, t.name, tf.role
        FROM types_functions tf
        JOIN types t ON tf.type_id = t.id
        WHERE tf.function_id = ?
        """,
        (function_id,)
    )

    relationships = tuple(
        TypeRelationship(
            type_id=row["id"],
            type_name=row["name"],
            role=row["role"]
        )
        for row in cursor.fetchall()
    )

    return relationships


def _delete_function_effect(
    conn: sqlite3.Connection,
    function_id: int,
) -> None:
    """
    Effect: Delete function from database.

    Args:
        conn: Database connection
        function_id: Function ID to delete
    """
    conn.execute("DELETE FROM functions WHERE id = ?", (function_id,))
    conn.commit()


# ============================================================================
# Public API Functions (MCP Tools)
# ============================================================================

def get_functions_by_file(
    db_path: str,
    file_id: int
) -> FunctionsQueryResult:
    """
    Get all functions in a file (high-frequency).

    Queries functions table for all functions in specified file.
    Returns functions ordered by creation time.

    Args:
        db_path: Path to project.db
        file_id: File ID to get functions for

    Returns:
        FunctionsQueryResult with tuple of function records (empty if no functions)

    Example:
        >>> result = get_functions_by_file("project.db", 42)
        >>> result.success
        True
        >>> len(result.functions)
        3
        >>> result.functions[0].name
        'calculate_sum_id_99'
    """
    # Effect: open connection and query
    conn = _open_connection(db_path)

    try:
        # Check if file exists
        if not _check_file_exists(conn, file_id):
            return FunctionsQueryResult(
                success=False,
                error=f"File with ID {file_id} not found"
            )

        rows = _get_functions_by_file_effect(conn, file_id)

        # Pure: convert rows to immutable records
        function_records = tuple(row_to_function_record(row) for row in rows)

        return FunctionsQueryResult(
            success=True,
            functions=function_records
        )

    except Exception as e:
        return FunctionsQueryResult(
            success=False,
            error=f"Query failed: {str(e)}"
        )

    finally:
        conn.close()


def update_function(
    db_path: str,
    function_id: int,
    name: Optional[str] = None,
    purpose: Optional[str] = None,
    parameters: Optional[List[Dict[str, Any]]] = None,
    returns: Optional[Dict[str, Any]] = None
) -> UpdateResult:
    """
    Update function metadata.

    Only updates non-NULL parameters. Name changes must preserve _id_xxx suffix.
    Automatically updates file timestamp.

    Args:
        db_path: Path to project.db
        function_id: Function ID to update
        name: New function name (None = don't update)
        purpose: New purpose (None = don't update)
        parameters: New parameters (None = don't update)
        returns: New return specification (None = don't update)

    Returns:
        UpdateResult with success status, function_id, and file_id

    Example:
        >>> # Update only the purpose
        >>> result = update_function("project.db", 99, purpose="Add two numbers")
        >>> result.success
        True

        >>> # Update name and parameters
        >>> result = update_function(
        ...     "project.db",
        ...     99,
        ...     name="calculate_sum_id_99",
        ...     parameters=[{"name": "a", "type": "int"}, {"name": "b", "type": "int"}]
        ... )
        >>> result.success
        True
    """
    # Validate at least one parameter is provided
    if name is None and purpose is None and parameters is None and returns is None:
        return UpdateResult(
            success=False,
            error="At least one parameter (name, purpose, parameters, returns) must be provided"
        )

    # Validate name pattern if name is being updated
    if name is not None and not validate_function_id_pattern(name, function_id):
        return UpdateResult(
            success=False,
            error=f"Function name must contain '_id_{function_id}' pattern"
        )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if function exists
        if not _check_function_exists(conn, function_id):
            return UpdateResult(
                success=False,
                error=f"Function with ID {function_id} not found"
            )

        # Get file_id before update
        file_id = _get_function_file_id(conn, function_id)
        if file_id is None:
            return UpdateResult(
                success=False,
                error=f"Could not retrieve file_id for function {function_id}"
            )

        # Pure: serialize params and returns
        params_json = serialize_params(parameters)
        returns_json = serialize_returns(returns)

        # Pure: build update query
        sql, params = build_update_query(function_id, name, purpose, params_json, returns_json)

        # Effect: execute update
        _update_function_effect(conn, sql, params)

        conn.close()

        # Effect: update file timestamp (uses separate connection)
        timestamp_result = update_file_timestamp(db_path, file_id)
        if not timestamp_result.success:
            return UpdateResult(
                success=False,
                error=f"Updated but timestamp update failed: {timestamp_result.error}"
            )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("update_function")

        return UpdateResult(
            success=True,
            function_id=function_id,
            file_id=file_id,
            return_statements=return_statements
        )

    except Exception as e:
        return UpdateResult(
            success=False,
            error=f"Database update failed: {str(e)}"
        )

    finally:
        # Connection already closed before update_file_timestamp call
        pass


def update_functions_for_file(
    db_path: str,
    file_id: int,
    functions: List[Dict[str, Any]]
) -> BatchUpdateResult:
    """
    Update multiple functions in a single file.

    More efficient than individual updates. Calls update_file_timestamp once at end.
    All updates succeed or all fail (atomic operation).

    Args:
        db_path: Path to project.db
        file_id: File ID
        functions: List of function update objects with keys: function_id, name, purpose, parameters, returns

    Returns:
        BatchUpdateResult with success status and updated count

    Example:
        >>> functions = [
        ...     {"function_id": 99, "purpose": "Add two numbers"},
        ...     {"function_id": 100, "purpose": "Subtract two numbers"}
        ... ]
        >>> result = update_functions_for_file("project.db", 42, functions)
        >>> result.success
        True
        >>> result.updated_count
        2
    """
    # Validate input
    if not functions:
        return BatchUpdateResult(
            success=False,
            error="Functions list cannot be empty"
        )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if file exists
        if not _check_file_exists(conn, file_id):
            return BatchUpdateResult(
                success=False,
                error=f"File with ID {file_id} not found"
            )

        # Extract function IDs and validate they belong to this file
        function_ids = [f.get("function_id") for f in functions]
        if not all(function_ids):
            return BatchUpdateResult(
                success=False,
                error="All functions must have function_id"
            )

        if not _validate_functions_belong_to_file(conn, file_id, function_ids):
            return BatchUpdateResult(
                success=False,
                error=f"Not all functions belong to file {file_id}"
            )

        # Validate name patterns and prepare updates
        updates = []
        for func in functions:
            function_id = func.get("function_id")
            name = func.get("name")
            purpose = func.get("purpose")
            parameters = func.get("parameters")
            returns = func.get("returns")

            # Validate name pattern if provided
            if name is not None and not validate_function_id_pattern(name, function_id):
                return BatchUpdateResult(
                    success=False,
                    error=f"Function name '{name}' must contain '_id_{function_id}' pattern"
                )

            # Pure: serialize params and returns
            params_json = serialize_params(parameters)
            returns_json = serialize_returns(returns)

            # Pure: build update query
            sql, params = build_update_query(function_id, name, purpose, params_json, returns_json)
            updates.append((sql, params))

        # Effect: execute all updates in transaction
        _update_functions_batch_effect(conn, updates)

        conn.close()

        # Effect: update file timestamp once (uses separate connection)
        timestamp_result = update_file_timestamp(db_path, file_id)
        if not timestamp_result.success:
            return BatchUpdateResult(
                success=False,
                error=f"Updated but timestamp update failed: {timestamp_result.error}"
            )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("update_functions_for_file")

        return BatchUpdateResult(
            success=True,
            updated_count=len(functions),
            return_statements=return_statements
        )

    except Exception as e:
        return BatchUpdateResult(
            success=False,
            error=f"Batch update failed: {str(e)}"
        )

    finally:
        # Connection already closed before update_file_timestamp call
        pass


def update_function_file_location(
    db_path: str,
    function_id: int,
    old_file_id: int,
    new_file_id: int
) -> LocationUpdateResult:
    """
    Move function to different file (internal use, not exposed as MCP tool).

    Updates function's file_id and updates timestamps for both files.
    Rarely used - for refactoring scenarios.

    Args:
        db_path: Path to project.db
        function_id: Function ID to move
        old_file_id: Current file ID
        new_file_id: New file ID

    Returns:
        LocationUpdateResult with success status

    Example:
        >>> # Internal use only - move function from file 42 to file 43
        >>> result = update_function_file_location("project.db", 99, 42, 43)
        >>> result.success
        True
    """
    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Validate function exists
        if not _check_function_exists(conn, function_id):
            return LocationUpdateResult(
                success=False,
                error=f"Function with ID {function_id} not found"
            )

        # Validate both files exist
        if not _check_file_exists(conn, old_file_id):
            return LocationUpdateResult(
                success=False,
                error=f"Old file with ID {old_file_id} not found"
            )

        if not _check_file_exists(conn, new_file_id):
            return LocationUpdateResult(
                success=False,
                error=f"New file with ID {new_file_id} not found"
            )

        # Verify function currently belongs to old_file_id
        current_file_id = _get_function_file_id(conn, function_id)
        if current_file_id != old_file_id:
            return LocationUpdateResult(
                success=False,
                error=f"Function {function_id} does not belong to file {old_file_id}"
            )

        # Effect: update function's file_id
        _update_function_file_location_effect(conn, function_id, new_file_id)

        conn.close()

        # Effect: update timestamps for both files
        old_timestamp_result = update_file_timestamp(db_path, old_file_id)
        if not old_timestamp_result.success:
            return LocationUpdateResult(
                success=False,
                error=f"Updated but old file timestamp update failed: {old_timestamp_result.error}"
            )

        new_timestamp_result = update_file_timestamp(db_path, new_file_id)
        if not new_timestamp_result.success:
            return LocationUpdateResult(
                success=False,
                error=f"Updated but new file timestamp update failed: {new_timestamp_result.error}"
            )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("update_function_file_location")

        return LocationUpdateResult(
            success=True,
            return_statements=return_statements
        )

    except Exception as e:
        return LocationUpdateResult(
            success=False,
            error=f"Location update failed: {str(e)}"
        )

    finally:
        # Connection already closed before update_file_timestamp calls
        pass


def delete_function(
    db_path: str,
    function_id: int,
    note_reason: str,
    note_severity: str,
    note_source: str,
    note_type: str = "entry_deletion"
) -> DeleteResult:
    """
    Delete function with validation and interaction cascade.

    Validates no type relationships exist before deletion. Requires manual unlinking
    from types_functions first. Interactions cascade automatically via SQL.

    Args:
        db_path: Path to project.db
        function_id: Function ID to delete
        note_reason: Deletion reason
        note_severity: 'info', 'warning', 'error'
        note_source: 'ai' or 'user'
        note_type: Note type (default: 'entry_deletion')

    Returns:
        DeleteResult with success status or type relationships list

    Example:
        >>> result = delete_function(
        ...     "project.db",
        ...     99,
        ...     note_reason="Function no longer needed",
        ...     note_severity="info",
        ...     note_source="ai"
        ... )
        >>> result.success
        True
        >>> result.deleted_function_id
        99
        >>> result.file_id
        42
    """
    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if function exists
        if not _check_function_exists(conn, function_id):
            return DeleteResult(
                success=False,
                error=f"Function with ID {function_id} not found"
            )

        # Check if function is reserved
        if _check_is_reserved(conn, function_id):
            return DeleteResult(
                success=False,
                error="function_reserved"
            )

        # Check for type relationships
        type_rels = _get_type_relationships(conn, function_id)

        # If type relationships exist, return error
        if type_rels:
            return DeleteResult(
                success=False,
                error="types_functions_exist",
                type_relationships=type_rels
            )

        # Get file_id before deletion
        file_id = _get_function_file_id(conn, function_id)
        if file_id is None:
            return DeleteResult(
                success=False,
                error=f"Could not retrieve file_id for function {function_id}"
            )

        # No blocking dependencies - proceed with deletion
        # Create note entry
        _create_deletion_note(
            conn,
            "functions",
            function_id,
            note_reason,
            note_severity,
            note_source,
            note_type
        )

        # Delete function (interactions cascade automatically)
        _delete_function_effect(conn, function_id)

        conn.close()

        # Success - fetch return statements from core database
        return_statements = get_return_statements("delete_function")

        return DeleteResult(
            success=True,
            deleted_function_id=function_id,
            file_id=file_id,
            return_statements=return_statements
        )

    except Exception as e:
        return DeleteResult(
            success=False,
            error=f"Database deletion failed: {str(e)}"
        )

    finally:
        # Connection already closed
        pass

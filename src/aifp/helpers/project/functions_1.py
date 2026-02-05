"""
AIFP Helper Functions - Project Functions (Part 1)

Function reservation, finalization, and lookup operations for project database.
Implements reserve/finalize pattern for rename-proof ID-based function tracking.

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.

Helpers in this file:
- reserve_function: Reserve function ID before creation
- reserve_functions: Reserve multiple function IDs (batch)
- finalize_function: Finalize reserved function after creation
- finalize_functions: Finalize multiple functions (batch)
- get_function_by_name: Very high-frequency name lookup
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

# Import common project utilities (DRY principle)
from ._common import _open_connection, _check_file_exists

# Import update_file_timestamp from files_2
sys.path.insert(0, str(Path(__file__).parent))
from files_2 import update_file_timestamp


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
    id_in_name: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ReserveResult:
    """Result of function reservation operation."""
    success: bool
    id: Optional[int] = None
    is_reserved: Optional[bool] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class ReserveBatchResult:
    """Result of batch function reservation."""
    success: bool
    ids: Tuple[int, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class FinalizeResult:
    """Result of function finalization operation."""
    success: bool
    function_id: Optional[int] = None
    file_id: Optional[int] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class FinalizeBatchResult:
    """Result of batch function finalization."""
    success: bool
    finalized_ids: Tuple[int, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()  # AI guidance for next steps


@dataclass(frozen=True)
class FunctionQueryResult:
    """Result of function lookup operation."""
    success: bool
    function: Optional[FunctionRecord] = None
    error: Optional[str] = None


# ============================================================================
# Pure Helper Functions
# ============================================================================

def validate_function_id_in_name(name: str, function_id: int) -> bool:
    """
    Validate that function name contains _id_{function_id} pattern.

    Pure function - no side effects, deterministic.

    Args:
        name: Function name to validate
        function_id: Expected function ID

    Returns:
        True if pattern found, False otherwise

    Example:
        >>> validate_function_id_in_name("calculate_sum_id_42", 42)
        True
        >>> validate_function_id_in_name("calculate_sum", 42)
        False
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
        id_in_name=bool(row["id_in_name"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )


# ============================================================================
# Database Effect Functions
# ============================================================================

def _reserve_function_effect(
    conn: sqlite3.Connection,
    name: str,
    file_id: int,
    purpose: Optional[str],
    params_json: Optional[str],
    returns_json: Optional[str],
    id_in_name: bool = True
) -> int:
    """
    Effect: Insert reserved function into database.

    Args:
        conn: Database connection
        name: Preliminary function name
        file_id: File ID where function will be defined
        purpose: Function purpose
        params_json: Parameters JSON string
        returns_json: Returns JSON string
        id_in_name: Whether function name will contain _id_XX pattern (default True)

    Returns:
        Reserved function ID
    """
    cursor = conn.execute(
        """
        INSERT INTO functions (name, file_id, purpose, params, returns, is_reserved, id_in_name)
        VALUES (?, ?, ?, ?, ?, 1, ?)
        """,
        (name, file_id, purpose, params_json, returns_json, 1 if id_in_name else 0)
    )
    conn.commit()
    return cursor.lastrowid


def _reserve_functions_batch_effect(
    conn: sqlite3.Connection,
    functions: List[Tuple[str, int, Optional[str], Optional[str], Optional[str], bool]]
) -> Tuple[int, ...]:
    """
    Effect: Insert multiple reserved functions in transaction.

    Args:
        conn: Database connection
        functions: List of (name, file_id, purpose, params_json, returns_json, id_in_name) tuples

    Returns:
        Tuple of reserved function IDs in same order
    """
    cursor = conn.cursor()
    ids = []

    try:
        for name, file_id, purpose, params_json, returns_json, id_in_name in functions:
            cursor.execute(
                """
                INSERT INTO functions (name, file_id, purpose, params, returns, is_reserved, id_in_name)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (name, file_id, purpose, params_json, returns_json, 1 if id_in_name else 0)
            )
            ids.append(cursor.lastrowid)

        conn.commit()
        return tuple(ids)

    except Exception as e:
        conn.rollback()
        raise e


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


def _finalize_function_effect(
    conn: sqlite3.Connection,
    function_id: int,
    name: str,
    purpose: Optional[str],
    params_json: Optional[str],
    returns_json: Optional[str]
) -> None:
    """
    Effect: Finalize reserved function in database.

    Args:
        conn: Database connection
        function_id: Reserved function ID
        name: Final function name with _id_xx suffix
        purpose: Function purpose
        params_json: Parameters JSON string
        returns_json: Returns JSON string
    """
    conn.execute(
        """
        UPDATE functions
        SET is_reserved = 0,
            name = ?,
            purpose = ?,
            params = ?,
            returns = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (name, purpose, params_json, returns_json, function_id)
    )
    conn.commit()


def _finalize_functions_batch_effect(
    conn: sqlite3.Connection,
    finalizations: List[Tuple[int, str, Optional[str], Optional[str], Optional[str]]]
) -> None:
    """
    Effect: Finalize multiple functions in transaction.

    Args:
        conn: Database connection
        finalizations: List of (function_id, name, purpose, params_json, returns_json) tuples
    """
    cursor = conn.cursor()

    try:
        for function_id, name, purpose, params_json, returns_json in finalizations:
            cursor.execute(
                """
                UPDATE functions
                SET is_reserved = 0,
                    name = ?,
                    purpose = ?,
                    params = ?,
                    returns = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, purpose, params_json, returns_json, function_id)
            )

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e


def _get_function_by_name_effect(
    conn: sqlite3.Connection,
    function_name: str
) -> Optional[sqlite3.Row]:
    """
    Effect: Query function by name.

    Args:
        conn: Database connection
        function_name: Function name to look up

    Returns:
        Row object or None if not found
    """
    cursor = conn.execute(
        "SELECT * FROM functions WHERE name = ? LIMIT 1",
        (function_name,)
    )
    return cursor.fetchone()


# ============================================================================
# Public API Functions (MCP Tools)
# ============================================================================

def reserve_function(
    db_path: str,
    name: str,
    file_id: int,
    purpose: Optional[str] = None,
    params: Optional[List[Dict[str, Any]]] = None,
    returns: Optional[Dict[str, Any]] = None,
    skip_id_naming: bool = False
) -> ReserveResult:
    """
    Reserve function ID for naming before creation.

    Creates placeholder entry in functions table with is_reserved=1.
    Returns ID that should be embedded in function name: {name}_id_{id}

    Args:
        db_path: Path to project.db
        name: Preliminary function name (will have _id_xxx appended unless skip_id_naming=True)
        file_id: File ID where function will be defined
        purpose: Function purpose (optional)
        params: Function parameters (optional)
        returns: Return value specification (optional)
        skip_id_naming: If True, skip ID embedding (for MCP tools that must have clean names)

    Returns:
        ReserveResult with success status and reserved ID

    Example:
        >>> result = reserve_function(
        ...     "project.db",
        ...     "calculate_sum",
        ...     file_id=42,
        ...     purpose="Add two numbers"
        ... )
        >>> result.success
        True
        >>> result.id
        99
        # Use result.id to create: calculate_sum_id_99 (unless skip_id_naming=True)
    """
    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if file exists
        if not _check_file_exists(conn, file_id):
            return ReserveResult(
                success=False,
                error=f"File with ID {file_id} not found"
            )

        # Pure: serialize params and returns
        params_json = serialize_params(params)
        returns_json = serialize_returns(returns)

        # Effect: reserve function with id_in_name flag
        reserved_id = _reserve_function_effect(
            conn,
            name,
            file_id,
            purpose,
            params_json,
            returns_json,
            not skip_id_naming
        )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("reserve_function")

        return ReserveResult(
            success=True,
            id=reserved_id,
            is_reserved=True,
            return_statements=return_statements
        )

    finally:
        conn.close()


def reserve_functions(
    db_path: str,
    functions: List[Dict[str, Any]]
) -> ReserveBatchResult:
    """
    Reserve multiple function IDs at once.

    Creates placeholder entries for multiple functions in a single transaction.
    All reservations succeed or all fail (atomic operation).

    Args:
        db_path: Path to project.db
        functions: List of function objects with keys: name, file_id, purpose, params, returns, skip_id_naming
                   skip_id_naming is optional (defaults to False) and controls per-function ID embedding

    Returns:
        ReserveBatchResult with success status and reserved IDs
        IDs correspond to input indices: functions[0] → ids[0], functions[1] → ids[1]

    Example:
        >>> functions = [
        ...     {"name": "add", "file_id": 42, "purpose": "Add numbers"},
        ...     {"name": "reserve_file", "file_id": 42, "skip_id_naming": True}  # MCP tool
        ... ]
        >>> result = reserve_functions("project.db", functions)
        >>> result.success
        True
        >>> result.ids
        (99, 100)
    """
    # Validate input
    if not functions:
        return ReserveBatchResult(
            success=False,
            error="Functions list cannot be empty"
        )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Validate all file IDs exist
        for func in functions:
            file_id = func.get("file_id")
            if file_id is None:
                return ReserveBatchResult(
                    success=False,
                    error="All functions must have file_id"
                )
            if not _check_file_exists(conn, file_id):
                return ReserveBatchResult(
                    success=False,
                    error=f"File with ID {file_id} not found"
                )

        # Pure: prepare data for batch insert (with per-item skip_id_naming)
        batch_data = []
        for func in functions:
            name = func.get("name", "")
            file_id = func.get("file_id")
            purpose = func.get("purpose")
            params_json = serialize_params(func.get("params"))
            returns_json = serialize_returns(func.get("returns"))
            skip_id_naming = func.get("skip_id_naming", False)
            id_in_name = not skip_id_naming
            batch_data.append((name, file_id, purpose, params_json, returns_json, id_in_name))

        # Effect: reserve all functions in transaction
        reserved_ids = _reserve_functions_batch_effect(conn, batch_data)

        # Success - fetch return statements from core database
        return_statements = get_return_statements("reserve_functions")

        return ReserveBatchResult(
            success=True,
            ids=reserved_ids,
            return_statements=return_statements
        )

    except Exception as e:
        return ReserveBatchResult(
            success=False,
            error=f"Batch reservation failed: {str(e)}"
        )

    finally:
        conn.close()


def finalize_function(
    db_path: str,
    function_id: int,
    name: str,
    file_id: int,
    purpose: Optional[str] = None,
    params: Optional[List[Dict[str, Any]]] = None,
    returns: Optional[Dict[str, Any]] = None,
    skip_id_naming: bool = False
) -> FinalizeResult:
    """
    Finalize reserved function after creation.

    Sets is_reserved=0 to mark function as finalized.
    Automatically updates file timestamp.

    Args:
        db_path: Path to project.db
        function_id: Reserved function ID
        name: Final function name with _id_xx suffix (unless skip_id_naming=True)
        file_id: File ID
        purpose: Function purpose (optional)
        params: Function parameters (optional)
        returns: Return value specification (optional)
        skip_id_naming: If True, skip ID pattern validation (for MCP tools)

    Returns:
        FinalizeResult with success status and function_id

    Example:
        >>> # After writing calculate_sum_id_99 in code
        >>> result = finalize_function(
        ...     "project.db",
        ...     function_id=99,
        ...     name="calculate_sum_id_99",
        ...     file_id=42,
        ...     purpose="Add two numbers"
        ... )
        >>> result.success
        True
    """
    # Validate name contains _id_{function_id} pattern (unless skipped)
    if not skip_id_naming and not validate_function_id_in_name(name, function_id):
        return FinalizeResult(
            success=False,
            error=f"Function name must contain '_id_{function_id}' pattern"
        )

    # Effect: open connection
    conn = _open_connection(db_path)

    try:
        # Check if file exists
        if not _check_file_exists(conn, file_id):
            return FinalizeResult(
                success=False,
                error=f"File with ID {file_id} not found"
            )

        # Pure: serialize params and returns
        params_json = serialize_params(params)
        returns_json = serialize_returns(returns)

        # Effect: finalize function
        _finalize_function_effect(
            conn,
            function_id,
            name,
            purpose,
            params_json,
            returns_json
        )

        conn.close()

        # Effect: update file timestamp (uses separate connection)
        timestamp_result = update_file_timestamp(db_path, file_id)
        if not timestamp_result.success:
            return FinalizeResult(
                success=False,
                error=f"Finalized but timestamp update failed: {timestamp_result.error}"
            )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("finalize_function")

        return FinalizeResult(
            success=True,
            function_id=function_id,
            file_id=file_id,
            return_statements=return_statements
        )

    except Exception as e:
        return FinalizeResult(
            success=False,
            error=f"Database finalization failed: {str(e)}"
        )

    finally:
        # Connection already closed before update_file_timestamp call
        pass


def finalize_functions(
    db_path: str,
    functions: List[Dict[str, Any]]
) -> FinalizeBatchResult:
    """
    Finalize multiple reserved functions.

    Updates database in transaction. Calls update_file_timestamp once per unique file_id.
    All finalizations succeed or all fail (atomic operation).

    Args:
        db_path: Path to project.db
        functions: List of function objects with keys: function_id, name, file_id, purpose, params, returns, skip_id_naming
                   skip_id_naming is optional (defaults to False) and controls per-function validation

    Returns:
        FinalizeBatchResult with success status and finalized IDs

    Example:
        >>> functions = [
        ...     {"function_id": 99, "name": "add_id_99", "file_id": 42},
        ...     {"function_id": 100, "name": "reserve_file", "file_id": 42, "skip_id_naming": True}
        ... ]
        >>> result = finalize_functions("project.db", functions)
        >>> result.success
        True
        >>> result.finalized_ids
        (99, 100)
    """
    # Validate input
    if not functions:
        return FinalizeBatchResult(
            success=False,
            error="Functions list cannot be empty"
        )

    # Validate all names and prepare finalization data
    finalizations = []
    file_ids = set()

    for func in functions:
        function_id = func.get("function_id")
        name = func.get("name", "")
        file_id = func.get("file_id")
        skip_id_naming = func.get("skip_id_naming", False)

        if function_id is None or file_id is None:
            return FinalizeBatchResult(
                success=False,
                error="All functions must have function_id and file_id"
            )

        # Validate name pattern (unless skipped for this item)
        if not skip_id_naming and not validate_function_id_in_name(name, function_id):
            return FinalizeBatchResult(
                success=False,
                error=f"Function name '{name}' must contain '_id_{function_id}' pattern"
            )

        # Pure: serialize params and returns
        params_json = serialize_params(func.get("params"))
        returns_json = serialize_returns(func.get("returns"))
        purpose = func.get("purpose")

        finalizations.append((function_id, name, purpose, params_json, returns_json))
        file_ids.add(file_id)

    # Effect: open connection and finalize batch
    conn = _open_connection(db_path)

    try:
        # Validate all file IDs exist
        for file_id in file_ids:
            if not _check_file_exists(conn, file_id):
                return FinalizeBatchResult(
                    success=False,
                    error=f"File with ID {file_id} not found"
                )

        # Effect: finalize all functions in transaction
        _finalize_functions_batch_effect(conn, finalizations)

        conn.close()

        # Effect: update timestamps for all affected files
        for file_id in file_ids:
            timestamp_result = update_file_timestamp(db_path, file_id)
            if not timestamp_result.success:
                return FinalizeBatchResult(
                    success=False,
                    error=f"Finalized but timestamp update failed for file {file_id}: {timestamp_result.error}"
                )

        # Success - fetch return statements from core database
        return_statements = get_return_statements("finalize_functions")

        return FinalizeBatchResult(
            success=True,
            finalized_ids=tuple(f[0] for f in finalizations),
            return_statements=return_statements
        )

    except Exception as e:
        return FinalizeBatchResult(
            success=False,
            error=f"Batch finalization failed: {str(e)}"
        )

    finally:
        # Connection already closed before update_file_timestamp calls
        pass


def get_function_by_name(
    db_path: str,
    function_name: str
) -> FunctionQueryResult:
    """
    Get function by name (very high-frequency lookup).

    Queries functions table for exact name match.
    Returns full function record with metadata.

    Args:
        db_path: Path to project.db
        function_name: Function name to look up (e.g., 'calculate_sum_id_42')

    Returns:
        FunctionQueryResult with function record or None if not found

    Example:
        >>> result = get_function_by_name("project.db", "calculate_sum_id_42")
        >>> result.success
        True
        >>> result.function.id
        42
        >>> result.function.file_id
        15
    """
    # Effect: open connection and query
    conn = _open_connection(db_path)

    try:
        row = _get_function_by_name_effect(conn, function_name)

        if row is None:
            return FunctionQueryResult(
                success=True,
                function=None
            )

        # Pure: convert row to immutable record
        function_record = row_to_function_record(row)

        return FunctionQueryResult(
            success=True,
            function=function_record
        )

    except Exception as e:
        return FunctionQueryResult(
            success=False,
            error=f"Query failed: {str(e)}"
        )

    finally:
        conn.close()

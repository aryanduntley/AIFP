"""
AIFP Helper Functions - Core Schema

Schema introspection and generic query operations for aifp_core.db.

Helpers in this file:
- get_core_tables: List all tables in core database
- get_core_fields: Get field names and types for a specific table
- get_core_schema: Get complete schema for core database
- get_from_core: Get records by ID(s), or all records if empty array
- get_from_core_where: Flexible filtering with structured JSON conditions
- query_core: Execute complex SQL WHERE clause (advanced, rare use)

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List

# Import core utilities
from ._common import (
    _open_core_connection,
    _get_table_names,
    _get_table_info,
    get_return_statements,
    rows_to_tuple,
)


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class TablesResult:
    """Result of get_core_tables operation."""
    success: bool
    tables: Tuple[str, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class FieldInfo:
    """Immutable field information."""
    name: str
    type: str
    notnull: bool
    default_value: Optional[str]
    is_primary_key: bool


@dataclass(frozen=True)
class FieldsResult:
    """Result of get_core_fields operation."""
    success: bool
    fields: Tuple[FieldInfo, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class TableSchema:
    """Immutable table schema with fields."""
    name: str
    fields: Tuple[FieldInfo, ...]


@dataclass(frozen=True)
class SchemaResult:
    """Result of get_core_schema operation."""
    success: bool
    tables: Tuple[TableSchema, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class QueryResult:
    """Result of generic query operations."""
    success: bool
    rows: Tuple[Dict[str, Any], ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


# ============================================================================
# Pure Helper Functions
# ============================================================================

def _dict_to_field_info(field_dict: Dict[str, Any]) -> FieldInfo:
    """
    Pure: Convert field info dict to immutable FieldInfo.

    Args:
        field_dict: Dict from _get_table_info

    Returns:
        Immutable FieldInfo
    """
    return FieldInfo(
        name=field_dict['name'],
        type=field_dict['type'],
        notnull=field_dict['notnull'],
        default_value=field_dict['default_value'],
        is_primary_key=field_dict['is_primary_key'],
    )


def _validate_table_name(table: str) -> bool:
    """
    Pure: Validate table name to prevent SQL injection.

    Only allows alphanumeric characters and underscores.

    Args:
        table: Table name to validate

    Returns:
        True if valid, False otherwise
    """
    return table.isidentifier()


def _validate_field_names(fields: List[str]) -> bool:
    """
    Pure: Validate field names to prevent SQL injection.

    Only allows alphanumeric characters and underscores.

    Args:
        fields: List of field names to validate

    Returns:
        True if all valid, False otherwise
    """
    return all(f.isidentifier() for f in fields)


def _build_where_clause(conditions: Dict[str, Any]) -> Tuple[str, Tuple[Any, ...]]:
    """
    Pure: Build parameterized WHERE clause from conditions dict.

    Args:
        conditions: Dict of field-value pairs (AND logic)

    Returns:
        Tuple of (where_clause, params)

    Example:
        >>> _build_where_clause({"type": "fp", "category": "purity"})
        ('type = ? AND category = ?', ('fp', 'purity'))
    """
    if not conditions:
        return ("1=1", ())

    clauses = []
    params = []

    for field, value in conditions.items():
        clauses.append(f"{field} = ?")
        params.append(value)

    return (" AND ".join(clauses), tuple(params))


# ============================================================================
# Public API Functions (MCP Tools)
# ============================================================================

def get_core_tables() -> TablesResult:
    """
    List all tables in core database.

    Returns list of table names from aifp_core.db.
    Useful for schema exploration and validation.

    Returns:
        TablesResult with:
        - success: True if query succeeded
        - tables: Tuple of table names
        - error: Error message if failed
        - return_statements: AI guidance for next steps

    Example:
        >>> result = get_core_tables()
        >>> result.success
        True
        >>> result.tables
        ('categories', 'directive_categories', 'directive_flow', ...)
    """
    try:
        conn = _open_core_connection()

        try:
            tables = _get_table_names(conn)
            return_statements = get_return_statements("get_core_tables")

            return TablesResult(
                success=True,
                tables=tables,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return TablesResult(success=False, error=str(e))
    except Exception as e:
        return TablesResult(success=False, error=f"Unexpected error: {str(e)}")


def get_core_fields(table: str) -> FieldsResult:
    """
    Get field names and types for a specific table.

    Returns column information including types, nullability, and primary key status.

    Args:
        table: Table name

    Returns:
        FieldsResult with:
        - success: True if query succeeded
        - fields: Tuple of FieldInfo objects
        - error: Error message if failed
        - return_statements: AI guidance for next steps

    Example:
        >>> result = get_core_fields("directives")
        >>> result.success
        True
        >>> [f.name for f in result.fields]
        ['id', 'name', 'type', 'workflow', 'description', ...]
    """
    # Validate table name
    if not _validate_table_name(table):
        return FieldsResult(
            success=False,
            error=f"Invalid table name: '{table}'"
        )

    try:
        conn = _open_core_connection()

        try:
            # Get table info
            field_dicts = _get_table_info(conn, table)

            if not field_dicts:
                return FieldsResult(
                    success=False,
                    error=f"Table '{table}' not found in core database"
                )

            # Convert to immutable FieldInfo objects
            fields = tuple(_dict_to_field_info(f) for f in field_dicts)
            return_statements = get_return_statements("get_core_fields")

            return FieldsResult(
                success=True,
                fields=fields,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return FieldsResult(success=False, error=str(e))
    except Exception as e:
        return FieldsResult(success=False, error=f"Unexpected error: {str(e)}")


def get_core_schema() -> SchemaResult:
    """
    Get complete schema for core database (all tables and fields).

    Returns comprehensive schema information for all tables.
    Useful for full schema exploration.

    Returns:
        SchemaResult with:
        - success: True if query succeeded
        - tables: Tuple of TableSchema objects (each with name and fields)
        - error: Error message if failed
        - return_statements: AI guidance for next steps

    Example:
        >>> result = get_core_schema()
        >>> result.success
        True
        >>> [t.name for t in result.tables]
        ['categories', 'directive_categories', 'directive_flow', ...]
    """
    try:
        conn = _open_core_connection()

        try:
            # Get all table names
            table_names = _get_table_names(conn)

            # Get fields for each table
            table_schemas = []
            for table_name in table_names:
                field_dicts = _get_table_info(conn, table_name)
                fields = tuple(_dict_to_field_info(f) for f in field_dicts)
                table_schemas.append(TableSchema(name=table_name, fields=fields))

            return_statements = get_return_statements("get_core_schema")

            return SchemaResult(
                success=True,
                tables=tuple(table_schemas),
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return SchemaResult(success=False, error=str(e))
    except Exception as e:
        return SchemaResult(success=False, error=f"Unexpected error: {str(e)}")


def get_from_core(
    table: str,
    id_array: List[int]
) -> QueryResult:
    """
    Get records by ID(s), or all records if empty array.

    Generic query for any core database table.

    Args:
        table: Table name
        id_array: IDs to fetch. **Empty array [] returns ALL records**

    Returns:
        QueryResult with:
        - success: True if query succeeded
        - rows: Tuple of record dicts
        - error: Error message if failed
        - return_statements: AI guidance for next steps

    Example:
        >>> result = get_from_core("directives", [1, 2, 3])
        >>> result.success
        True
        >>> len(result.rows)
        3

        >>> result = get_from_core("categories", [])  # All records
        >>> len(result.rows)
        10  # All categories returned
    """
    # Validate table name
    if not _validate_table_name(table):
        return QueryResult(
            success=False,
            error=f"Invalid table name: '{table}'"
        )

    try:
        conn = _open_core_connection()

        try:
            if not id_array:
                # Empty array - return all records
                cursor = conn.execute(f"SELECT * FROM {table}")
            else:
                # Fetch by IDs
                placeholders = ",".join("?" * len(id_array))
                cursor = conn.execute(
                    f"SELECT * FROM {table} WHERE id IN ({placeholders})",
                    tuple(id_array)
                )

            rows = rows_to_tuple(cursor.fetchall())
            return_statements = get_return_statements("get_from_core")

            return QueryResult(
                success=True,
                rows=rows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return QueryResult(success=False, error=str(e))
    except Exception as e:
        return QueryResult(success=False, error=f"Query failed: {str(e)}")


def get_from_core_where(
    table: str,
    conditions: Dict[str, Any],
    limit: Optional[int] = None,
    orderby: Optional[str] = None
) -> QueryResult:
    """
    Flexible filtering with structured JSON conditions.

    Queries core database with field-value conditions (AND logic).

    Args:
        table: Table name
        conditions: Field-value pairs (AND logic), e.g., {"type": "fp", "category": "purity"}
        limit: Maximum rows to return (optional)
        orderby: Sort order, e.g., "name ASC" or "id DESC" (optional)

    Returns:
        QueryResult with:
        - success: True if query succeeded
        - rows: Tuple of matching record dicts
        - error: Error message if failed (including invalid field names)
        - return_statements: AI guidance for next steps

    Example:
        >>> result = get_from_core_where("directives", {"type": "fp"})
        >>> result.success
        True
        >>> len(result.rows)
        15  # All FP directives

        >>> result = get_from_core_where(
        ...     "directives",
        ...     {"type": "project"},
        ...     limit=5,
        ...     orderby="name ASC"
        ... )
        >>> len(result.rows)
        5
    """
    # Validate table name
    if not _validate_table_name(table):
        return QueryResult(
            success=False,
            error=f"Invalid table name: '{table}'"
        )

    # Validate condition field names
    if conditions and not _validate_field_names(list(conditions.keys())):
        return QueryResult(
            success=False,
            error=f"Invalid field name in conditions"
        )

    try:
        conn = _open_core_connection()

        try:
            # Verify fields exist in table
            field_info = _get_table_info(conn, table)
            if not field_info:
                return QueryResult(
                    success=False,
                    error=f"Table '{table}' not found in core database"
                )

            valid_fields = {f['name'] for f in field_info}
            for field in conditions.keys():
                if field not in valid_fields:
                    return QueryResult(
                        success=False,
                        error=f"Field '{field}' not found in table '{table}'"
                    )

            # Build query
            where_clause, params = _build_where_clause(conditions)
            query = f"SELECT * FROM {table} WHERE {where_clause}"

            # Add ORDER BY if specified
            if orderby:
                # Basic validation - allow field name + ASC/DESC
                parts = orderby.split()
                if len(parts) <= 2 and parts[0].isidentifier():
                    query += f" ORDER BY {orderby}"

            # Add LIMIT if specified
            if limit is not None and limit > 0:
                query += f" LIMIT {int(limit)}"

            cursor = conn.execute(query, params)
            rows = rows_to_tuple(cursor.fetchall())
            return_statements = get_return_statements("get_from_core_where")

            return QueryResult(
                success=True,
                rows=rows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return QueryResult(success=False, error=str(e))
    except Exception as e:
        return QueryResult(success=False, error=f"Query failed: {str(e)}")


def query_core(
    table: str,
    query: str
) -> QueryResult:
    """
    Execute complex SQL WHERE clause (advanced, rare use).

    Allows raw WHERE clause for complex queries not possible with get_from_core_where.
    Use with caution - prefer structured queries when possible.

    Args:
        table: Table name
        query: WHERE clause without "WHERE" keyword

    Returns:
        QueryResult with:
        - success: True if query succeeded
        - rows: Tuple of matching record dicts
        - error: Error message if SQL syntax invalid
        - return_statements: AI guidance for next steps

    Example:
        >>> result = query_core("directives", "type = 'fp' OR type = 'project'")
        >>> result.success
        True

        >>> result = query_core(
        ...     "directive_flow",
        ...     "from_directive = '*' AND flow_type = 'reference_consultation'"
        ... )
    """
    # Validate table name
    if not _validate_table_name(table):
        return QueryResult(
            success=False,
            error=f"Invalid table name: '{table}'"
        )

    try:
        conn = _open_core_connection()

        try:
            # Build and execute query
            sql = f"SELECT * FROM {table} WHERE {query}"
            cursor = conn.execute(sql)
            rows = rows_to_tuple(cursor.fetchall())
            return_statements = get_return_statements("query_core")

            return QueryResult(
                success=True,
                rows=rows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return QueryResult(success=False, error=str(e))
    except Exception as e:
        return QueryResult(success=False, error=f"Query failed: {str(e)}")

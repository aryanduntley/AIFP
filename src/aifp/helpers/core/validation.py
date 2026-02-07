"""
AIFP Helper Functions - Core Validation

CHECK constraint parsing for aifp_core.db schema validation.

Helpers in this file:
- core_allowed_check_constraints: Get allowed values for CHECK constraint enum fields

All functions are pure FP - immutable data, explicit parameters, Result types.
Database operations isolated as effects with clear naming conventions.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

# Import core utilities
from ._common import (
    _open_core_connection,
    _get_table_sql,
    _get_table_info,
    _parse_check_constraint,
    get_return_statements,
)


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class CheckConstraintResult:
    """Result of CHECK constraint lookup operation."""
    success: bool
    values: Tuple[str, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


# ============================================================================
# Public API Functions (MCP Tools)
# ============================================================================

def core_allowed_check_constraints(
    table: str,
    field: str
) -> CheckConstraintResult:
    """
    Get allowed values for CHECK constraint enum fields in aifp_core.db.

    Parses CREATE TABLE schema to extract CHECK(field IN (...)) constraints.
    Useful for validating input values against database constraints.

    Args:
        table: Table name to check for CHECK constraints
        field: Field name to get allowed values for

    Returns:
        CheckConstraintResult with:
        - success: True if constraint found
        - values: Tuple of allowed string values
        - error: Error message if failed
        - return_statements: AI guidance for next steps

    Example:
        >>> result = core_allowed_check_constraints("directives", "type")
        >>> result.success
        True
        >>> result.values
        ('fp', 'project', 'git', 'user_system', 'user_preference')

        >>> result = core_allowed_check_constraints("directive_flow", "flow_type")
        >>> result.values
        ('status_branch', 'completion_loop', 'conditional', 'error', ...)

        >>> result = core_allowed_check_constraints("helper_functions", "target_database")
        >>> result.values
        ('core', 'project', 'user_preferences', 'user_directives', 'multi_db', 'no_db')
    """
    try:
        # Effect: open connection to core database
        conn = _open_core_connection()

        try:
            # Effect: get CREATE TABLE SQL for the table
            table_sql = _get_table_sql(conn, table)

            if table_sql is None:
                return CheckConstraintResult(
                    success=False,
                    error=f"Table '{table}' not found in core database"
                )

            # Effect: verify field exists in table
            table_info = _get_table_info(conn, table)
            field_names = tuple(col['name'] for col in table_info)

            if field not in field_names:
                return CheckConstraintResult(
                    success=False,
                    error=f"Field '{field}' not found in table '{table}'"
                )

            # Pure: parse CHECK constraint from SQL
            values = _parse_check_constraint(table_sql, field)

            if values is None:
                return CheckConstraintResult(
                    success=False,
                    error=f"Field '{field}' does not have a CHECK constraint list"
                )

            # Success - fetch return statements
            return_statements = get_return_statements("core_allowed_check_constraints")

            return CheckConstraintResult(
                success=True,
                values=values,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return CheckConstraintResult(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return CheckConstraintResult(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )

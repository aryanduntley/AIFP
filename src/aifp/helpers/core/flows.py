"""
AIFP Helper Functions - Core Flows

Simple directive flow queries for aifp_core.db.
Returns raw flow data - AI evaluates conditions and determines routing.

Helpers in this file:
- get_flows_from_directive: Get all flows originating from a directive
- get_flows_to_directive: Get all flows leading to a directive
- get_completion_loop_target: Get where to loop back after completing directive
- get_directive_flows: General-purpose query with optional filters
- get_wildcard_flows: Get flows available from ANY context (from_directive='*')

Design principle: MCP server retrieves data, AI handles logic/decisions.
No condition evaluation - AI knows project state and decides which path to take.

All functions are pure FP - immutable data, explicit parameters, Result types.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from ._common import (
    _open_core_connection,
    get_return_statements,
    FlowRecord,
    row_to_flow,
)


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class FlowResult:
    """Result of single flow lookup."""
    success: bool
    flow: Optional[FlowRecord] = None
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


@dataclass(frozen=True)
class FlowsResult:
    """Result of multiple flow query."""
    success: bool
    flows: Tuple[FlowRecord, ...] = ()
    error: Optional[str] = None
    return_statements: Tuple[str, ...] = ()


# ============================================================================
# Public API Functions
# ============================================================================

def get_flows_from_directive(from_directive: str) -> FlowsResult:
    """
    Get all flows originating from a directive (what comes next?).

    Returns raw flow data including condition_key/condition_value.
    AI evaluates conditions based on its knowledge of project state.

    Args:
        from_directive: Source directive name

    Returns:
        FlowsResult with all flows from this directive

    Example:
        >>> result = get_flows_from_directive("aifp_status")
        >>> result.success
        True
        >>> [f.to_directive for f in result.flows]
        ['project_init', 'project_task_select', ...]
    """
    try:
        conn = _open_core_connection()

        try:
            cursor = conn.execute(
                """
                SELECT * FROM directive_flow
                WHERE from_directive = ?
                ORDER BY priority
                """,
                (from_directive,)
            )
            rows = cursor.fetchall()
            flows = tuple(row_to_flow(row) for row in rows)
            return_statements = get_return_statements("get_flows_from_directive")

            return FlowsResult(
                success=True,
                flows=flows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return FlowsResult(success=False, error=str(e))
    except Exception as e:
        return FlowsResult(success=False, error=f"Query failed: {str(e)}")


def get_flows_to_directive(to_directive: str) -> FlowsResult:
    """
    Get all flows leading to a directive (what leads here?).

    Useful for understanding directive prerequisites and entry points.

    Args:
        to_directive: Target directive name

    Returns:
        FlowsResult with all flows to this directive

    Example:
        >>> result = get_flows_to_directive("project_file_write")
        >>> result.success
        True
        >>> [f.from_directive for f in result.flows]
        ['aifp_status', 'project_task_select', ...]
    """
    try:
        conn = _open_core_connection()

        try:
            cursor = conn.execute(
                """
                SELECT * FROM directive_flow
                WHERE to_directive = ?
                ORDER BY priority
                """,
                (to_directive,)
            )
            rows = cursor.fetchall()
            flows = tuple(row_to_flow(row) for row in rows)
            return_statements = get_return_statements("get_flows_to_directive")

            return FlowsResult(
                success=True,
                flows=flows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return FlowsResult(success=False, error=str(e))
    except Exception as e:
        return FlowsResult(success=False, error=f"Query failed: {str(e)}")


def get_completion_loop_target(from_directive: str) -> FlowResult:
    """
    Get where to loop back after completing directive.

    Looks for flow_type='completion_loop' from the specified directive.

    Args:
        from_directive: Directive name

    Returns:
        FlowResult with the completion loop target

    Example:
        >>> result = get_completion_loop_target("project_task_complete")
        >>> result.success
        True
        >>> result.flow.to_directive
        'aifp_status'
    """
    try:
        conn = _open_core_connection()

        try:
            cursor = conn.execute(
                """
                SELECT * FROM directive_flow
                WHERE from_directive = ? AND flow_type = 'completion_loop'
                LIMIT 1
                """,
                (from_directive,)
            )
            row = cursor.fetchone()

            if row is None:
                return FlowResult(
                    success=False,
                    error=f"No completion_loop flow found for '{from_directive}'"
                )

            flow = row_to_flow(row)
            return_statements = get_return_statements("get_completion_loop_target")

            return FlowResult(
                success=True,
                flow=flow,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return FlowResult(success=False, error=str(e))
    except Exception as e:
        return FlowResult(success=False, error=f"Query failed: {str(e)}")


def get_directive_flows(
    flow_category: Optional[str] = None,
    flow_type: Optional[str] = None,
    from_directive: Optional[str] = None,
    to_directive: Optional[str] = None
) -> FlowsResult:
    """
    General-purpose query for directive flows with optional filters.

    All parameters optional - can combine filters for targeted queries.

    Args:
        flow_category: Filter by category ('project', 'fp', 'user_preferences', 'git')
        flow_type: Filter by type ('status_branch', 'completion_loop', 'conditional', etc.)
        from_directive: Filter by source directive name
        to_directive: Filter by target directive name

    Returns:
        FlowsResult with matching flows

    Example:
        >>> result = get_directive_flows(flow_category="fp")
        >>> result.success
        True

        >>> result = get_directive_flows(flow_category="git", flow_type="conditional")
    """
    try:
        conn = _open_core_connection()

        try:
            query = "SELECT * FROM directive_flow WHERE 1=1"
            params = []

            if flow_category:
                query += " AND flow_category = ?"
                params.append(flow_category)

            if flow_type:
                query += " AND flow_type = ?"
                params.append(flow_type)

            if from_directive:
                query += " AND from_directive = ?"
                params.append(from_directive)

            if to_directive:
                query += " AND to_directive = ?"
                params.append(to_directive)

            query += " ORDER BY priority, from_directive, to_directive"

            cursor = conn.execute(query, tuple(params))
            rows = cursor.fetchall()
            flows = tuple(row_to_flow(row) for row in rows)
            return_statements = get_return_statements("get_directive_flows")

            return FlowsResult(
                success=True,
                flows=flows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return FlowsResult(success=False, error=str(e))
    except Exception as e:
        return FlowsResult(success=False, error=f"Query failed: {str(e)}")


def get_wildcard_flows(flow_type: Optional[str] = None) -> FlowsResult:
    """
    Get all flows from wildcard '*' source (available from ANY context).

    Wildcard flows include FP references, utilities, and cross-cutting concerns
    that can be accessed regardless of current workflow position.

    Args:
        flow_type: Optional filter ('reference_consultation', 'utility', etc.)

    Returns:
        FlowsResult with wildcard flows

    Example:
        >>> result = get_wildcard_flows(flow_type="reference_consultation")
        >>> result.success
        True
        >>> # Returns FP directives available for consultation

        >>> result = get_wildcard_flows(flow_type="utility")
        >>> # Returns cross-cutting utilities
    """
    try:
        conn = _open_core_connection()

        try:
            if flow_type:
                cursor = conn.execute(
                    """
                    SELECT * FROM directive_flow
                    WHERE from_directive = '*' AND flow_type = ?
                    ORDER BY flow_type, priority
                    """,
                    (flow_type,)
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM directive_flow
                    WHERE from_directive = '*'
                    ORDER BY flow_type, priority
                    """
                )

            rows = cursor.fetchall()
            flows = tuple(row_to_flow(row) for row in rows)
            return_statements = get_return_statements("get_wildcard_flows")

            return FlowsResult(
                success=True,
                flows=flows,
                return_statements=return_statements
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return FlowsResult(success=False, error=str(e))
    except Exception as e:
        return FlowsResult(success=False, error=f"Query failed: {str(e)}")

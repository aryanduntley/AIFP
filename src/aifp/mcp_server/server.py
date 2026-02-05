"""
AIFP MCP Server - Server Core

Loads tool definitions from aifp_core.db, wires up MCP handlers,
and provides the run_server() entry point.

Tool call flow:
  call_tool → check registry → lazy import helper → call(**args) → serialize → TextContent
"""

import sqlite3
from typing import Dict, Any, List, Tuple

from mcp.types import Tool, TextContent

from ..database.connection import get_core_db_path
from ..wrappers.mcp_sdk import (
    ToolDefinition,
    tool_definitions_to_mcp_tools,
    make_text_content,
    _effect_create_server,
    _effect_register_handlers,
    _effect_run_server,
)
from .registry import TOOL_REGISTRY, is_registered_tool, _effect_import_tool_function
from .schema import params_to_input_schema
from .serialization import serialize_result, is_error_result
from .errors import (
    format_tool_not_found_error,
    format_internal_error,
    format_import_error,
)


# ============================================================================
# Module-level cache (populated once at startup)
# ============================================================================

_cached_tools: List[Tool] = []


# ============================================================================
# Effect Functions — Tool Loading
# ============================================================================

def _effect_load_tool_definitions() -> Tuple[ToolDefinition, ...]:
    """
    Effect: Load tool definitions from aifp_core.db for all registered tools.

    Queries helper_functions table for name, purpose, and parameters,
    then converts parameters to JSON Schema.

    Returns:
        Tuple of ToolDefinition objects for registered tools
    """
    db_path = get_core_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        # Get all is_tool=1 helpers that are in our registry
        placeholders = ",".join("?" for _ in TOOL_REGISTRY)
        cursor = conn.execute(
            f"SELECT name, purpose, parameters FROM helper_functions WHERE name IN ({placeholders})",
            tuple(TOOL_REGISTRY.keys()),
        )

        definitions = []
        for row in cursor.fetchall():
            name = row["name"]
            purpose = row["purpose"] or f"AIFP tool: {name}"
            params_json = row["parameters"] or "[]"
            input_schema = params_to_input_schema(params_json)

            definitions.append(ToolDefinition(
                name=name,
                description=purpose,
                input_schema=input_schema,
            ))

        return tuple(definitions)

    finally:
        conn.close()


def _effect_initialize_tools() -> None:
    """
    Effect: Load tool definitions and cache as MCP Tool objects.

    Called once at server startup. Populates the module-level _cached_tools list.
    """
    global _cached_tools
    definitions = _effect_load_tool_definitions()
    _cached_tools = tool_definitions_to_mcp_tools(definitions)


# ============================================================================
# Async Handlers (passed to MCP wrapper)
# ============================================================================

async def _handle_list_tools() -> list[Tool]:
    """Async handler: Return cached list of MCP Tool objects."""
    return _cached_tools


async def _handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """
    Async handler: Dispatch tool call to the appropriate helper function.

    Flow: check registry → lazy import → call(**args) → serialize → TextContent
    """
    # Check registry
    if not is_registered_tool(name):
        return [make_text_content(format_tool_not_found_error(name))]

    # Lazy import the helper function
    try:
        tool_fn = _effect_import_tool_function(name)
    except (ImportError, AttributeError) as e:
        return [make_text_content(format_import_error(name, e))]

    # Call the helper with unpacked arguments
    try:
        result = tool_fn(**arguments)
    except Exception as e:
        return [make_text_content(format_internal_error(name, e))]

    # Serialize result to JSON
    serialized = serialize_result(result)

    return [make_text_content(serialized)]


# ============================================================================
# Public Entry Point
# ============================================================================

def run_server() -> None:
    """
    Start the AIFP MCP server on stdio transport.

    Loads tool definitions from aifp_core.db, creates the MCP server,
    registers handlers, and blocks on stdio communication.
    """
    # Effect: load and cache tool definitions
    _effect_initialize_tools()

    # Effect: create server
    server = _effect_create_server(name="aifp", version="0.1.0")

    # Effect: register handlers
    _effect_register_handlers(server, _handle_list_tools, _handle_call_tool)

    # Effect: run on stdio (blocking)
    _effect_run_server(server)

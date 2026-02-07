"""
AIFP MCP Server - Error Handling

Standard MCP/JSON-RPC error codes and pure error formatter functions.
All functions are pure — no side effects, deterministic output.
"""

from typing import Final


# ============================================================================
# Standard MCP/JSON-RPC Error Codes
# ============================================================================

PARSE_ERROR: Final[int] = -32700
INVALID_REQUEST: Final[int] = -32600
METHOD_NOT_FOUND: Final[int] = -32601
INVALID_PARAMS: Final[int] = -32602
INTERNAL_ERROR: Final[int] = -32603


# ============================================================================
# Pure Error Formatter Functions
# ============================================================================

def format_tool_not_found_error(tool_name: str) -> str:
    """Pure: Format error message for unknown tool name."""
    return f"Tool not found: '{tool_name}'. Use tools/list to see available tools."


def format_invalid_params_error(tool_name: str, detail: str) -> str:
    """Pure: Format error message for invalid tool parameters."""
    return f"Invalid parameters for '{tool_name}': {detail}"


def format_internal_error(tool_name: str, error: Exception) -> str:
    """Pure: Format error message for unexpected internal errors."""
    return f"Internal error in '{tool_name}': {type(error).__name__}: {str(error)}"


def format_import_error(tool_name: str, error: Exception) -> str:
    """Pure: Format error message when tool module fails to import."""
    return f"Failed to import tool '{tool_name}': {type(error).__name__}: {str(error)}"

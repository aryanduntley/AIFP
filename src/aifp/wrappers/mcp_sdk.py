"""
AIFP Wrapper - MCP SDK (Model Context Protocol)

Wraps the OOP-based `mcp` library into FP-compliant functions.
The MCP SDK requires a Server class with decorator-based handler
registration — this wrapper isolates that into a single module
and exposes pure functional interfaces for tool definitions,
content building, and server lifecycle.

External dependency: mcp (pip install mcp>=1.26.0)
"""

import asyncio
from dataclasses import dataclass
from typing import Final, Dict, Any, Tuple, Optional, List, Callable, Awaitable

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# ============================================================================
# Immutable Data Types (FP representation of MCP concepts)
# ============================================================================

@dataclass(frozen=True)
class ToolDefinition:
    """Immutable tool definition — our FP representation of an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass(frozen=True)
class ToolCallRequest:
    """Immutable representation of an incoming tool call."""
    name: str
    arguments: Dict[str, Any]


@dataclass(frozen=True)
class ToolCallResponse:
    """Immutable response to a tool call."""
    content: Tuple[str, ...]  # Tuple of text strings
    is_error: bool = False


# ============================================================================
# Pure Functions
# ============================================================================

def tool_definition_to_mcp_tool(defn: ToolDefinition) -> Tool:
    """Pure: Convert our FP ToolDefinition to an MCP SDK Tool object."""
    return Tool(
        name=defn.name,
        description=defn.description,
        inputSchema=defn.input_schema,
    )


def tool_definitions_to_mcp_tools(
    definitions: Tuple[ToolDefinition, ...]
) -> List[Tool]:
    """Pure: Convert tuple of ToolDefinitions to list of MCP Tools."""
    return [tool_definition_to_mcp_tool(d) for d in definitions]


def make_text_content(text: str) -> TextContent:
    """Pure: Create an MCP TextContent response object."""
    return TextContent(type="text", text=text)


def tool_call_response_to_mcp_content(
    response: ToolCallResponse,
) -> List[TextContent]:
    """Pure: Convert our FP ToolCallResponse to MCP content list."""
    return [make_text_content(text) for text in response.content]


# ============================================================================
# Effect Functions (Side-effecting, clearly marked)
# ============================================================================

def _effect_create_server(
    name: str,
    version: Optional[str] = None,
) -> Server:
    """
    Effect: Create an MCP Server instance.

    Args:
        name: Server name (shown to clients)
        version: Server version string

    Returns:
        Server instance (not yet running)
    """
    return Server(name=name, version=version)


def _effect_register_handlers(
    server: Server,
    list_tools_handler: Callable[[], Awaitable[List[Tool]]],
    call_tool_handler: Callable[[str, Dict[str, Any]], Awaitable[List[TextContent]]],
) -> None:
    """
    Effect: Register list_tools and call_tool handlers on the server.

    The MCP SDK uses decorators for handler registration. This function
    isolates that OOP pattern into a single effect.

    Args:
        server: Server instance to register handlers on
        list_tools_handler: Async function returning list of Tool objects
        call_tool_handler: Async function taking (name, arguments) returning content
    """
    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return await list_tools_handler()

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
        return await call_tool_handler(name, arguments or {})


def _effect_run_server(server: Server) -> None:
    """
    Effect: Run the MCP server on stdio transport (blocking).

    This starts the asyncio event loop and blocks until the server
    is shut down. Uses stdio for communication with AI clients.

    Args:
        server: Server instance with handlers registered
    """
    async def _run() -> None:
        async with stdio_server() as (read_stream, write_stream):
            init_options = server.create_initialization_options()
            await server.run(read_stream, write_stream, init_options)

    asyncio.run(_run())

"""
Tests for aifp.mcp_server.server

Integration tests for tool loading, handler dispatch, and error paths.
"""

import json

import pytest

from aifp.mcp_server.server import (
    _effect_load_tool_definitions,
    _effect_initialize_tools,
    _handle_list_tools,
    _handle_call_tool,
    _cached_tools,
)
from aifp.mcp_server.registry import TOOL_REGISTRY


# ============================================================================
# Tool Loading Tests
# ============================================================================

def test_load_tool_definitions_returns_tuple():
    definitions = _effect_load_tool_definitions()
    assert isinstance(definitions, tuple)


def test_load_tool_definitions_count_matches_registry():
    definitions = _effect_load_tool_definitions()
    assert len(definitions) == len(TOOL_REGISTRY)


def test_load_tool_definitions_have_names():
    definitions = _effect_load_tool_definitions()
    names = {d.name for d in definitions}
    # All registry tools should be in the definitions
    for tool_name in TOOL_REGISTRY:
        assert tool_name in names, f"Tool '{tool_name}' missing from definitions"


def test_load_tool_definitions_have_schemas():
    definitions = _effect_load_tool_definitions()
    for defn in definitions:
        assert isinstance(defn.input_schema, dict), f"{defn.name}: schema not a dict"
        assert defn.input_schema.get("type") == "object", f"{defn.name}: schema type not 'object'"
        assert "properties" in defn.input_schema, f"{defn.name}: schema missing 'properties'"


def test_load_tool_definitions_have_descriptions():
    definitions = _effect_load_tool_definitions()
    for defn in definitions:
        assert isinstance(defn.description, str), f"{defn.name}: description not a string"
        assert len(defn.description) > 0, f"{defn.name}: empty description"


# ============================================================================
# Initialize and List Tools Tests
# ============================================================================

def test_initialize_tools_populates_cache():
    _effect_initialize_tools()
    # Import the module-level cache after initialization
    from aifp.mcp_server import server
    assert len(server._cached_tools) == 207


@pytest.mark.asyncio
async def test_handle_list_tools_returns_207():
    _effect_initialize_tools()
    tools = await _handle_list_tools()
    assert len(tools) == 207


@pytest.mark.asyncio
async def test_handle_list_tools_are_mcp_tool_objects():
    _effect_initialize_tools()
    tools = await _handle_list_tools()
    from mcp.types import Tool
    for tool in tools:
        assert isinstance(tool, Tool)


# ============================================================================
# Call Tool Tests
# ============================================================================

@pytest.mark.asyncio
async def test_handle_call_tool_unknown_tool():
    """Unknown tools return error text, not crash."""
    _effect_initialize_tools()
    result = await _handle_call_tool("nonexistent_tool_xyz", {})
    assert len(result) == 1
    assert "not found" in result[0].text.lower()


@pytest.mark.asyncio
async def test_handle_call_tool_get_all_directive_names():
    """Known tool returns valid JSON response."""
    _effect_initialize_tools()
    result = await _handle_call_tool("get_all_directive_names", {})
    assert len(result) == 1
    parsed = json.loads(result[0].text)
    assert parsed["success"] is True


@pytest.mark.asyncio
async def test_handle_call_tool_missing_required_args():
    """Tool called without required args returns error (not crash)."""
    _effect_initialize_tools()
    # reserve_function requires db_path, name, file_id
    result = await _handle_call_tool("reserve_function", {})
    assert len(result) == 1
    text = result[0].text
    # Should contain error info (TypeError from missing args)
    assert "error" in text.lower() or "TypeError" in text


@pytest.mark.asyncio
async def test_handle_call_tool_get_supportive_context():
    """Shared helper with no required DB args should work."""
    _effect_initialize_tools()
    result = await _handle_call_tool("get_supportive_context", {})
    assert len(result) == 1
    # get_supportive_context returns a string (text content)
    assert len(result[0].text) > 0


@pytest.mark.asyncio
async def test_handle_call_tool_returns_text_content():
    """All tool calls must return list of TextContent objects."""
    _effect_initialize_tools()
    from mcp.types import TextContent
    result = await _handle_call_tool("get_all_directive_names", {})
    for item in result:
        assert isinstance(item, TextContent)
        assert item.type == "text"


# ============================================================================
# Wrapper Integration Tests
# ============================================================================

def test_tool_definitions_to_mcp_tools_roundtrip():
    """Tool definitions from DB convert to valid MCP Tool objects."""
    from aifp.wrappers.mcp_sdk import tool_definitions_to_mcp_tools
    from mcp.types import Tool

    definitions = _effect_load_tool_definitions()
    tools = tool_definitions_to_mcp_tools(definitions)

    assert len(tools) == len(definitions)
    for tool in tools:
        assert isinstance(tool, Tool)
        assert isinstance(tool.name, str)
        assert isinstance(tool.description, str)
        assert isinstance(tool.inputSchema, dict)

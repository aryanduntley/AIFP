"""
Tests for aifp.mcp_server.errors

Verifies error codes match JSON-RPC spec and formatter functions
produce expected output strings.
"""

from aifp.mcp_server.errors import (
    PARSE_ERROR,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    INVALID_PARAMS,
    INTERNAL_ERROR,
    format_tool_not_found_error,
    format_invalid_params_error,
    format_internal_error,
    format_import_error,
)


# ============================================================================
# Error Code Tests
# ============================================================================

def test_parse_error_code():
    assert PARSE_ERROR == -32700


def test_invalid_request_code():
    assert INVALID_REQUEST == -32600


def test_method_not_found_code():
    assert METHOD_NOT_FOUND == -32601


def test_invalid_params_code():
    assert INVALID_PARAMS == -32602


def test_internal_error_code():
    assert INTERNAL_ERROR == -32603


# ============================================================================
# Formatter Tests
# ============================================================================

def test_format_tool_not_found_error():
    result = format_tool_not_found_error("fake_tool")
    assert "fake_tool" in result
    assert "not found" in result.lower()


def test_format_tool_not_found_error_empty_name():
    result = format_tool_not_found_error("")
    assert isinstance(result, str)


def test_format_invalid_params_error():
    result = format_invalid_params_error("my_tool", "missing required 'name'")
    assert "my_tool" in result
    assert "missing required 'name'" in result


def test_format_internal_error():
    exc = ValueError("something broke")
    result = format_internal_error("my_tool", exc)
    assert "my_tool" in result
    assert "ValueError" in result
    assert "something broke" in result


def test_format_import_error():
    exc = ImportError("No module named 'fake_module'")
    result = format_import_error("my_tool", exc)
    assert "my_tool" in result
    assert "ImportError" in result
    assert "fake_module" in result


def test_formatters_return_strings():
    """All formatters must return plain strings."""
    assert isinstance(format_tool_not_found_error("x"), str)
    assert isinstance(format_invalid_params_error("x", "y"), str)
    assert isinstance(format_internal_error("x", Exception("e")), str)
    assert isinstance(format_import_error("x", ImportError("e")), str)

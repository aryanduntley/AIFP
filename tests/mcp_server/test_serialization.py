"""
Tests for aifp.mcp_server.serialization

Verifies result serialization handles all frozen dataclass types,
edge cases (frozenset, Path, datetime, bytes), and error detection.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from aifp.mcp_server.serialization import (
    _json_default,
    serialize_result,
    is_error_result,
)


# ============================================================================
# Test Dataclasses (mimicking AIFP helper result types)
# ============================================================================

@dataclass(frozen=True)
class SuccessResult:
    success: bool = True
    id: int = 1
    message: str = "ok"


@dataclass(frozen=True)
class ErrorResult:
    success: bool = False
    error: str = "not found"


@dataclass(frozen=True)
class QueryResult:
    success: bool = True
    items: Tuple[str, ...] = ()
    count: int = 0


@dataclass(frozen=True)
class NestedChild:
    name: str = "child"
    value: int = 42


@dataclass(frozen=True)
class NestedParent:
    success: bool = True
    child: Optional[NestedChild] = None


@dataclass(frozen=True)
class EdgeCaseResult:
    success: bool = True
    tags: frozenset = frozenset()
    path: Optional[Path] = None
    timestamp: Optional[datetime] = None
    data: Optional[bytes] = None


# ============================================================================
# _json_default Tests
# ============================================================================

def test_json_default_frozenset():
    result = _json_default(frozenset({"b", "a", "c"}))
    assert result == ["a", "b", "c"]  # sorted


def test_json_default_set():
    result = _json_default({"x", "y"})
    assert isinstance(result, list)
    assert set(result) == {"x", "y"}


def test_json_default_tuple():
    result = _json_default((1, 2, 3))
    assert result == [1, 2, 3]


def test_json_default_path():
    result = _json_default(Path("/home/user/file.py"))
    assert result == "/home/user/file.py"


def test_json_default_datetime():
    dt = datetime(2026, 2, 6, 12, 0, 0)
    result = _json_default(dt)
    assert result == "2026-02-06T12:00:00"


def test_json_default_bytes():
    result = _json_default(b"hello")
    assert result == "hello"


def test_json_default_bytes_with_invalid_utf8():
    result = _json_default(b"\xff\xfe")
    assert isinstance(result, str)


def test_json_default_dataclass():
    child = NestedChild(name="test", value=99)
    result = _json_default(child)
    assert result == {"name": "test", "value": 99}


def test_json_default_unsupported_type_raises():
    import pytest
    with pytest.raises(TypeError):
        _json_default(object())


# ============================================================================
# serialize_result Tests
# ============================================================================

def test_serialize_success_result():
    result = serialize_result(SuccessResult(success=True, id=42, message="created"))
    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["id"] == 42
    assert parsed["message"] == "created"


def test_serialize_error_result():
    result = serialize_result(ErrorResult(success=False, error="table not found"))
    parsed = json.loads(result)
    assert parsed["success"] is False
    assert parsed["error"] == "table not found"


def test_serialize_query_result_with_tuple():
    result = serialize_result(QueryResult(success=True, items=("a", "b", "c"), count=3))
    parsed = json.loads(result)
    assert parsed["items"] == ["a", "b", "c"]
    assert parsed["count"] == 3


def test_serialize_nested_dataclass():
    child = NestedChild(name="inner", value=7)
    result = serialize_result(NestedParent(success=True, child=child))
    parsed = json.loads(result)
    assert parsed["child"]["name"] == "inner"
    assert parsed["child"]["value"] == 7


def test_serialize_edge_cases():
    result = serialize_result(EdgeCaseResult(
        success=True,
        tags=frozenset({"fp", "pure"}),
        path=Path("/src/main.py"),
        timestamp=datetime(2026, 1, 1, 0, 0, 0),
        data=b"raw bytes",
    ))
    parsed = json.loads(result)
    assert sorted(parsed["tags"]) == ["fp", "pure"]
    assert parsed["path"] == "/src/main.py"
    assert parsed["timestamp"] == "2026-01-01T00:00:00"
    assert parsed["data"] == "raw bytes"


def test_serialize_plain_dict():
    result = serialize_result({"success": True, "count": 5})
    parsed = json.loads(result)
    assert parsed["success"] is True
    assert parsed["count"] == 5


def test_serialize_plain_string():
    result = serialize_result("just a string")
    assert result == "just a string"


def test_serialize_plain_list():
    result = serialize_result([1, 2, 3])
    parsed = json.loads(result)
    assert parsed == [1, 2, 3]


def test_serialize_none():
    result = serialize_result(None)
    assert result == "null"


def test_serialize_boolean():
    assert serialize_result(True) == "true"
    assert serialize_result(False) == "false"


# ============================================================================
# is_error_result Tests
# ============================================================================

def test_is_error_result_success_dataclass():
    assert is_error_result(SuccessResult()) is False


def test_is_error_result_error_dataclass():
    assert is_error_result(ErrorResult()) is True


def test_is_error_result_success_dict():
    assert is_error_result({"success": True}) is False


def test_is_error_result_error_dict():
    assert is_error_result({"success": False}) is True


def test_is_error_result_no_success_field_dict():
    assert is_error_result({"data": "something"}) is False


def test_is_error_result_string():
    assert is_error_result("error text") is False


def test_is_error_result_none():
    assert is_error_result(None) is False

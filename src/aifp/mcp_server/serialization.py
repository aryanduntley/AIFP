"""
AIFP MCP Server - Result Serialization

Converts helper function results (frozen dataclass instances) to JSON
strings suitable for MCP TextContent responses.

Strategy: dataclasses.asdict() + json.dumps() with custom default handler
for edge cases (frozenset, Path, datetime, bytes).

All functions are pure — no side effects, deterministic output.
"""

import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any


# ============================================================================
# Pure Functions
# ============================================================================

def _json_default(obj: Any) -> Any:
    """
    Pure: Custom JSON serializer for types not handled by default.

    Handles: frozenset, set, tuple, Path, datetime, bytes, dataclass instances.
    """
    if isinstance(obj, (frozenset, set)):
        return sorted(obj) if all(isinstance(x, str) for x in obj) else list(obj)
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def serialize_result(result: Any) -> str:
    """
    Pure: Serialize any helper result to a JSON string.

    Handles frozen dataclass results via dataclasses.asdict(),
    plain dicts, lists, strings, and primitive types.

    Args:
        result: Helper function return value (typically a frozen dataclass)

    Returns:
        JSON string representation
    """
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        data = dataclasses.asdict(result)
        return json.dumps(data, default=_json_default)

    if isinstance(result, str):
        return result

    return json.dumps(result, default=_json_default)


def is_error_result(result: Any) -> bool:
    """
    Pure: Check if a result represents an error.

    AIFP helper results use success=False to indicate errors.

    Args:
        result: Helper function return value

    Returns:
        True if the result indicates an error
    """
    if dataclasses.is_dataclass(result) and not isinstance(result, type):
        return not getattr(result, "success", True)
    if isinstance(result, dict):
        return not result.get("success", True)
    return False

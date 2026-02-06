"""
Tests for aifp.mcp_server.schema

Verifies JSON Schema generation from helper parameter definitions.
"""

import json

from aifp.mcp_server.schema import (
    PARAM_TYPE_MAP,
    map_param_type,
    param_to_schema_property,
    params_to_input_schema,
)


# ============================================================================
# map_param_type Tests
# ============================================================================

def test_map_param_type_string():
    assert map_param_type("string") == "string"


def test_map_param_type_str_alias():
    assert map_param_type("str") == "string"


def test_map_param_type_boolean():
    assert map_param_type("boolean") == "boolean"


def test_map_param_type_bool_alias():
    assert map_param_type("bool") == "boolean"


def test_map_param_type_integer():
    assert map_param_type("integer") == "integer"


def test_map_param_type_int_alias():
    assert map_param_type("int") == "integer"


def test_map_param_type_number():
    assert map_param_type("number") == "number"


def test_map_param_type_float_alias():
    assert map_param_type("float") == "number"


def test_map_param_type_array():
    assert map_param_type("array") == "array"


def test_map_param_type_object():
    assert map_param_type("object") == "object"


def test_map_param_type_unknown_defaults_to_string():
    assert map_param_type("unknown_type") == "string"


def test_map_param_type_case_insensitive():
    assert map_param_type("STRING") == "string"
    assert map_param_type("Boolean") == "boolean"
    assert map_param_type("INTEGER") == "integer"


def test_param_type_map_completeness():
    """All documented type aliases are in the map."""
    expected_keys = {"string", "str", "boolean", "bool", "integer", "int",
                     "number", "float", "array", "object"}
    assert set(PARAM_TYPE_MAP.keys()) == expected_keys


# ============================================================================
# param_to_schema_property Tests
# ============================================================================

def test_param_to_schema_property_basic():
    param = {"name": "task_id", "type": "integer", "required": True}
    result = param_to_schema_property(param)
    assert result["type"] == "integer"


def test_param_to_schema_property_with_description():
    param = {"name": "name", "type": "string", "description": "The task name"}
    result = param_to_schema_property(param)
    assert result["description"] == "The task name"


def test_param_to_schema_property_with_default():
    param = {"name": "active", "type": "boolean", "default": True}
    result = param_to_schema_property(param)
    assert result["default"] is True


def test_param_to_schema_property_no_description():
    param = {"name": "x", "type": "string"}
    result = param_to_schema_property(param)
    assert "description" not in result


def test_param_to_schema_property_null_default_excluded():
    param = {"name": "x", "type": "string", "default": None}
    result = param_to_schema_property(param)
    assert "default" not in result


def test_param_to_schema_property_missing_type_defaults_to_string():
    param = {"name": "x"}
    result = param_to_schema_property(param)
    assert result["type"] == "string"


# ============================================================================
# params_to_input_schema Tests
# ============================================================================

def test_params_to_input_schema_empty_string():
    result = params_to_input_schema("")
    assert result == {"type": "object", "properties": {}}


def test_params_to_input_schema_empty_array():
    result = params_to_input_schema("[]")
    assert result == {"type": "object", "properties": {}}


def test_params_to_input_schema_single_required():
    params = json.dumps([
        {"name": "db_path", "type": "string", "required": True, "description": "Path to DB"}
    ])
    result = params_to_input_schema(params)
    assert result["type"] == "object"
    assert "db_path" in result["properties"]
    assert result["properties"]["db_path"]["type"] == "string"
    assert result["properties"]["db_path"]["description"] == "Path to DB"
    assert result["required"] == ["db_path"]


def test_params_to_input_schema_optional_param():
    params = json.dumps([
        {"name": "limit", "type": "integer", "required": False}
    ])
    result = params_to_input_schema(params)
    assert "limit" in result["properties"]
    assert "required" not in result


def test_params_to_input_schema_mixed_required_optional():
    params = json.dumps([
        {"name": "name", "type": "string", "required": True},
        {"name": "purpose", "type": "string", "required": False},
        {"name": "file_id", "type": "integer", "required": True},
    ])
    result = params_to_input_schema(params)
    assert len(result["properties"]) == 3
    assert sorted(result["required"]) == ["file_id", "name"]


def test_params_to_input_schema_skips_nameless_params():
    params = json.dumps([
        {"name": "", "type": "string", "required": True},
        {"name": "valid", "type": "string", "required": True},
    ])
    result = params_to_input_schema(params)
    assert len(result["properties"]) == 1
    assert "valid" in result["properties"]


def test_params_to_input_schema_real_helper_params():
    """Test with actual parameter definitions from reserve_function."""
    params = json.dumps([
        {"name": "name", "type": "string", "required": True, "default": None, "description": "Function name"},
        {"name": "file_id", "type": "integer", "required": True, "default": None, "description": "File ID"},
        {"name": "purpose", "type": "string", "required": False, "default": None, "description": "Purpose"},
        {"name": "parameters", "type": "array", "required": False, "default": None, "description": "Params"},
        {"name": "returns", "type": "object", "required": False, "default": None, "description": "Returns"},
        {"name": "skip_id_naming", "type": "boolean", "required": False, "default": False, "description": "Skip ID"},
    ])
    result = params_to_input_schema(params)
    assert len(result["properties"]) == 6
    assert sorted(result["required"]) == ["file_id", "name"]
    assert result["properties"]["parameters"]["type"] == "array"
    assert result["properties"]["returns"]["type"] == "object"
    assert result["properties"]["skip_id_naming"]["type"] == "boolean"
    assert result["properties"]["skip_id_naming"]["default"] is False

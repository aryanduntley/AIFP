"""
AIFP MCP Server — Submission Verification Tests

Automated functional tests for verifying the AIFP MCP server works correctly.
Covers protocol compliance, tool functionality, project lifecycle, and privacy.

These tests verify what a reviewer or end user would experience:
  1. Protocol: JSON-RPC 2.0 compliance, tool listing, annotations
  2. Core DB: Read-only directive/helper queries against aifp_core.db
  3. Init: Project initialization creates correct directory structure and DBs
  4. Lifecycle: Reserve -> Finalize -> Query cycle for files, functions, tasks
  5. Preferences: User settings and tracking defaults
  6. Privacy: No network dependencies, all operations local

Run:  python tests/submission_tests.py
  or:  pytest tests/submission_tests.py -v

IMPORTANT: Do NOT modify these tests. Fix the code if tests fail.
"""

import json
import sqlite3
import sys
from pathlib import Path

import pytest

# Ensure src/ is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from aifp.mcp_server.server import (
    dispatch_message,
    handle_initialize,
    handle_list_tools,
    handle_call_tool,
    build_tool_annotations,
    _effect_load_and_cache_tools,
    SERVER_NAME,
    SERVER_VERSION,
    PROTOCOL_VERSION,
)
from aifp.mcp_server.registry import TOOL_REGISTRY
from aifp.helpers.orchestrators.entry_points import aifp_init
from aifp.database.connection import (
    AIFP_PROJECT_DIR,
    PROJECT_DB_NAME,
    USER_PREFERENCES_DB_NAME,
    clear_project_root_cache,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="module", autouse=True)
def load_tools():
    """Load and cache all 219 tools once for the entire test module."""
    _effect_load_and_cache_tools()


@pytest.fixture(autouse=True)
def _clear_cache():
    """Clear the project root cache after every test to prevent cross-test bleed."""
    yield
    clear_project_root_cache()


@pytest.fixture
def project_dir(tmp_path):
    """Create an initialized AIFP project in a temporary directory.

    Returns (project_root, project_db_path, prefs_db_path).
    """
    project_root = str(tmp_path)
    result = aifp_init(project_root=project_root)
    assert result.success, f"aifp_init failed: {result.error}"

    project_db = str(tmp_path / AIFP_PROJECT_DIR / PROJECT_DB_NAME)
    prefs_db = str(tmp_path / AIFP_PROJECT_DIR / USER_PREFERENCES_DB_NAME)
    return project_root, project_db, prefs_db


def _parse_tool_response(response):
    """Extract parsed data and error flag from a handle_call_tool response."""
    result = response["result"]
    is_error = result.get("isError", False)
    text = result["content"][0]["text"]
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        data = text
    return data, is_error


# ============================================================================
# 1. Protocol Compliance
# ============================================================================

class TestProtocol:
    """JSON-RPC 2.0 protocol compliance tests."""

    def test_initialize_returns_valid_response(self):
        resp = handle_initialize(1, {})
        assert resp["jsonrpc"] == "2.0"
        assert resp["id"] == 1
        result = resp["result"]
        assert result["protocolVersion"] == PROTOCOL_VERSION
        assert result["serverInfo"]["name"] == SERVER_NAME
        assert result["serverInfo"]["version"] == SERVER_VERSION
        assert "tools" in result["capabilities"]

    def test_tools_list_returns_219_tools(self):
        resp = handle_list_tools(1)
        tools = resp["result"]["tools"]
        assert len(tools) == 219, f"Expected 219 tools, got {len(tools)}"

    def test_all_tools_have_required_fields(self):
        resp = handle_list_tools(1)
        for tool in resp["result"]["tools"]:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool {tool.get('name')} missing 'description'"
            assert "inputSchema" in tool, f"Tool {tool.get('name')} missing 'inputSchema'"
            assert "annotations" in tool, f"Tool {tool.get('name')} missing 'annotations'"

    def test_all_tools_have_annotation_fields(self):
        resp = handle_list_tools(1)
        for tool in resp["result"]["tools"]:
            ann = tool["annotations"]
            name = tool["name"]
            assert "title" in ann, f"Tool {name} annotation missing 'title'"
            assert "readOnlyHint" in ann, f"Tool {name} annotation missing 'readOnlyHint'"
            assert "openWorldHint" in ann, f"Tool {name} annotation missing 'openWorldHint'"

    def test_all_tools_are_local_only(self):
        """Every AIFP tool must have openWorldHint=false (no network access)."""
        resp = handle_list_tools(1)
        for tool in resp["result"]["tools"]:
            assert tool["annotations"]["openWorldHint"] is False, (
                f"Tool {tool['name']} has openWorldHint=true — AIFP is local-only"
            )

    def test_no_tool_name_exceeds_64_characters(self):
        resp = handle_list_tools(1)
        for tool in resp["result"]["tools"]:
            assert len(tool["name"]) <= 64, (
                f"Tool name too long ({len(tool['name'])} chars): {tool['name']}"
            )

    def test_unknown_method_returns_error(self):
        resp = dispatch_message({"jsonrpc": "2.0", "id": 1, "method": "foo/bar"})
        assert "error" in resp
        assert resp["error"]["code"] == -32601

    def test_unknown_tool_returns_error_not_crash(self):
        resp = handle_call_tool(1, {"name": "nonexistent_tool", "arguments": {}})
        result = resp["result"]
        assert result["isError"] is True
        assert "not found" in result["content"][0]["text"].lower()

    def test_notification_returns_none(self):
        resp = dispatch_message({"jsonrpc": "2.0", "method": "notifications/initialized"})
        assert resp is None

    def test_tool_names_match_registry(self):
        """Cached tools should match the TOOL_REGISTRY keys."""
        resp = handle_list_tools(1)
        tool_names = {t["name"] for t in resp["result"]["tools"]}
        registry_names = set(TOOL_REGISTRY.keys())
        assert tool_names == registry_names, (
            f"Mismatch: in tools but not registry: {tool_names - registry_names}, "
            f"in registry but not tools: {registry_names - tool_names}"
        )

    def test_input_schemas_are_valid_json_schema(self):
        """All inputSchema fields must be valid JSON Schema objects."""
        resp = handle_list_tools(1)
        for tool in resp["result"]["tools"]:
            schema = tool["inputSchema"]
            assert isinstance(schema, dict), f"Tool {tool['name']}: schema is not a dict"
            assert schema.get("type") == "object", (
                f"Tool {tool['name']}: schema type is not 'object'"
            )

    def test_read_only_tools_have_idempotent_hint(self):
        """All read-only tools should be idempotent."""
        resp = handle_list_tools(1)
        for tool in resp["result"]["tools"]:
            ann = tool["annotations"]
            if ann["readOnlyHint"] is True:
                assert ann.get("idempotentHint") is True, (
                    f"Read-only tool {tool['name']} should have idempotentHint=true"
                )


# ============================================================================
# 2. Core Database (Read-Only aifp_core.db)
# ============================================================================

class TestCoreDatabase:
    """Verify read-only queries against the directive/helper database."""

    def test_get_all_directive_names(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {"name": "get_all_directive_names", "arguments": {}})
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_get_supportive_context(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {"name": "get_supportive_context", "arguments": {}})
        )
        assert is_error is False
        # Should return the supportive context text
        assert isinstance(data, (str, dict))

    def test_get_fp_directive_index(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {"name": "get_fp_directive_index", "arguments": {}})
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_get_categories(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {"name": "get_categories", "arguments": {}})
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_search_directives(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "search_directives",
                "arguments": {"keyword": "purity"},
            })
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_get_databases(self, project_dir):
        project_root, _, _ = project_dir
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "get_databases",
                "arguments": {"project_root": project_root},
            })
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True


# ============================================================================
# 3. Project Initialization
# ============================================================================

class TestProjectInit:
    """Verify aifp_init creates correct directory structure and databases."""

    def test_init_creates_aifp_directory(self, tmp_path):
        result = aifp_init(project_root=str(tmp_path))
        assert result.success is True
        assert (tmp_path / AIFP_PROJECT_DIR).is_dir()

    def test_init_creates_project_db(self, tmp_path):
        aifp_init(project_root=str(tmp_path))
        db_path = tmp_path / AIFP_PROJECT_DIR / PROJECT_DB_NAME
        assert db_path.is_file()
        # Verify it's a valid SQLite database
        conn = sqlite3.connect(str(db_path))
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = {t[0] for t in tables}
        # Core project tables must exist
        assert "project" in table_names
        assert "files" in table_names
        assert "functions" in table_names
        assert "tasks" in table_names
        assert "milestones" in table_names
        assert "notes" in table_names
        assert "themes" in table_names
        assert "flows" in table_names
        assert "completion_path" in table_names
        assert "infrastructure" in table_names

    def test_init_creates_user_preferences_db(self, tmp_path):
        aifp_init(project_root=str(tmp_path))
        db_path = tmp_path / AIFP_PROJECT_DIR / USER_PREFERENCES_DB_NAME
        assert db_path.is_file()
        conn = sqlite3.connect(str(db_path))
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        table_names = {t[0] for t in tables}
        assert "user_settings" in table_names
        assert "directive_preferences" in table_names
        assert "tracking_settings" in table_names

    def test_init_creates_blueprint(self, tmp_path):
        aifp_init(project_root=str(tmp_path))
        blueprint = tmp_path / AIFP_PROJECT_DIR / "ProjectBlueprint.md"
        assert blueprint.is_file()
        content = blueprint.read_text()
        assert "Project Blueprint" in content

    def test_init_populates_default_infrastructure(self, tmp_path):
        aifp_init(project_root=str(tmp_path))
        db_path = str(tmp_path / AIFP_PROJECT_DIR / PROJECT_DB_NAME)
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT type, value FROM infrastructure").fetchall()
        conn.close()
        infra_types = {r[0] for r in rows}
        assert "project_root" in infra_types

    def test_init_populates_default_user_settings(self, tmp_path):
        aifp_init(project_root=str(tmp_path))
        db_path = str(tmp_path / AIFP_PROJECT_DIR / USER_PREFERENCES_DB_NAME)
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT setting_key FROM user_settings"
        ).fetchall()
        conn.close()
        assert len(rows) > 0, "No default user settings were created"

    def test_init_tracking_all_disabled_by_default(self, tmp_path):
        aifp_init(project_root=str(tmp_path))
        db_path = str(tmp_path / AIFP_PROJECT_DIR / USER_PREFERENCES_DB_NAME)
        conn = sqlite3.connect(db_path)
        rows = conn.execute(
            "SELECT feature_name, enabled FROM tracking_settings"
        ).fetchall()
        conn.close()
        assert len(rows) > 0, "No tracking settings found"
        for feature_name, enabled in rows:
            assert enabled == 0, (
                f"Tracking feature '{feature_name}' is enabled by default "
                f"— all tracking must be OFF by default"
            )

    def test_init_returns_structured_result(self, tmp_path):
        result = aifp_init(project_root=str(tmp_path))
        assert result.success is True
        assert result.data is not None
        data = result.data
        assert data.get("success") is True
        assert data.get("project_root") == str(tmp_path)

    def test_init_is_idempotent_guard(self, tmp_path):
        """Running aifp_init twice should not crash or corrupt data."""
        result1 = aifp_init(project_root=str(tmp_path))
        assert result1.success is True
        result2 = aifp_init(project_root=str(tmp_path))
        # Second call should either succeed gracefully or return an
        # informative already-exists message — it must NOT crash
        assert isinstance(result2.success, bool)


# ============================================================================
# 4. Project Lifecycle — Reserve, Finalize, Query
# ============================================================================

class TestProjectLifecycle:
    """Verify the full reserve -> finalize -> query cycle for project entities."""

    def test_reserve_file_returns_id(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "reserve_file",
                "arguments": {
                    "name": "test_conversions",
                    "path": "src/test_conversions.py",
                    "language": "python",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True
        assert data.get("id") is not None

    def test_finalize_file(self, project_dir, tmp_path):
        # Reserve first
        reserve_data, _ = _parse_tool_response(
            handle_call_tool(1, {
                "name": "reserve_file",
                "arguments": {
                    "name": "converter",
                    "path": "src/converter.py",
                    "language": "python",
                },
            })
        )
        file_id = reserve_data["id"]

        # Create the file on disk (finalize_file checks existence)
        file_path = tmp_path / f"src/converter_id_{file_id}.py"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("# converter\n")

        # Finalize
        finalize_data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "finalize_file",
                "arguments": {
                    "file_id": file_id,
                    "name": f"converter_id_{file_id}",
                    "path": str(file_path),
                    "language": "python",
                },
            })
        )
        assert is_error is False
        assert finalize_data.get("success") is True

    def test_get_file_by_name(self, project_dir):
        # Reserve and finalize
        reserve_data, _ = _parse_tool_response(
            handle_call_tool(1, {
                "name": "reserve_file",
                "arguments": {
                    "name": "lookup_test",
                    "path": "src/lookup_test.py",
                    "language": "python",
                },
            })
        )
        file_id = reserve_data["id"]
        handle_call_tool(1, {
            "name": "finalize_file",
            "arguments": {
                "file_id": file_id,
                "name": f"lookup_test_id_{file_id}",
                "path": f"src/lookup_test_id_{file_id}.py",
            },
        })

        # Query by name
        query_data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "get_file_by_name",
                "arguments": {
                    "file_name": f"lookup_test_id_{file_id}",
                },
            })
        )
        assert is_error is False
        assert query_data.get("success") is True

    def test_reserve_function_returns_id(self, project_dir):
        # Need a file first
        reserve_file_data, _ = _parse_tool_response(
            handle_call_tool(1, {
                "name": "reserve_file",
                "arguments": {
                    "name": "func_test_file",
                    "path": "src/func_test_file.py",
                    "language": "python",
                },
            })
        )
        file_id = reserve_file_data["id"]

        # Reserve function
        func_data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "reserve_function",
                "arguments": {
                    "name": "celsius_to_fahrenheit",
                    "file_id": file_id,
                },
            })
        )
        assert is_error is False
        assert func_data.get("success") is True
        assert func_data.get("id") is not None

    def test_add_theme(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_theme",
                "arguments": {
                    "name": "Core Conversions",
                    "description": "Temperature conversion functions",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_add_flow(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_flow",
                "arguments": {
                    "name": "Conversion Flow",
                    "description": "Validate -> Convert -> Format",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_add_completion_path(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_completion_path",
                "arguments": {
                    "name": "Foundation",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_add_milestone_to_completion_path(self, project_dir):
        # Create completion path first
        cp_data, _ = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_completion_path",
                "arguments": {
                    "name": "Development Stage",
                },
            })
        )
        cp_id = cp_data["id"]

        # Add milestone
        ms_data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_milestone",
                "arguments": {
                    "completion_path_id": cp_id,
                    "name": "Core Conversion Functions",
                },
            })
        )
        assert is_error is False
        assert ms_data.get("success") is True
        assert ms_data.get("id") is not None

    def test_add_task_to_milestone(self, project_dir):
        # Create completion path -> milestone -> task
        cp_data, _ = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_completion_path",
                "arguments": {"name": "Task Test Stage"},
            })
        )
        ms_data, _ = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_milestone",
                "arguments": {
                    "completion_path_id": cp_data["id"],
                    "name": "Task Test Milestone",
                },
            })
        )
        task_data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_task",
                "arguments": {
                    "milestone_id": ms_data["id"],
                    "name": "Implement celsius_to_fahrenheit",
                },
            })
        )
        assert is_error is False
        assert task_data.get("success") is True
        assert task_data.get("id") is not None

    def test_add_note(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_note",
                "arguments": {
                    "content": "Project initialized with temperature converter scope",
                    "note_type": "evolution",
                    "source": "ai",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_get_all_themes(self, project_dir):
        # Add a theme first
        handle_call_tool(1, {
            "name": "add_theme",
            "arguments": {
                "name": "Query Test Theme",
            },
        })
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "get_all_themes",
                "arguments": {},
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_get_all_flows(self, project_dir):
        handle_call_tool(1, {
            "name": "add_flow",
            "arguments": {
                "name": "Query Test Flow",
            },
        })
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "get_all_flows",
                "arguments": {},
            })
        )
        assert is_error is False
        assert data.get("success") is True


# ============================================================================
# 5. User Preferences
# ============================================================================

class TestUserPreferences:
    """Verify user preference operations work correctly."""

    def test_get_user_settings(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "get_user_settings",
                "arguments": {},
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_get_tracking_settings(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "get_tracking_settings",
                "arguments": {},
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_add_directive_preference(self, project_dir):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "add_directive_preference",
                "arguments": {
                    "directive_name": "project_file_write",
                    "preference_key": "always_add_docstrings",
                    "preference_value": "true",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True

    def test_load_directive_preferences(self, project_dir):
        # Add a preference, then load
        handle_call_tool(1, {
            "name": "add_directive_preference",
            "arguments": {
                "directive_name": "project_file_write",
                "preference_key": "test_pref",
                "preference_value": "test_value",
            },
        })
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "load_directive_preferences",
                "arguments": {
                    "directive_name": "project_file_write",
                },
            })
        )
        assert is_error is False
        assert data.get("success") is True


# ============================================================================
# 6. Privacy & Security
# ============================================================================

class TestPrivacySecurity:
    """Verify AIFP makes no network calls and is fully local."""

    def test_no_network_imports_in_source(self):
        """Source code must not import network libraries."""
        src_dir = Path(__file__).parent.parent / "src" / "aifp"
        network_modules = {"requests", "urllib", "httpx", "aiohttp"}
        # socket is stdlib but we check for direct usage in imports
        violations = []

        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text(errors="ignore")
            for mod in network_modules:
                if f"import {mod}" in content:
                    violations.append(f"{py_file.name}: imports {mod}")

        assert violations == [], (
            f"Network library imports found (AIFP must be local-only):\n"
            + "\n".join(violations)
        )

    def test_no_url_construction_in_helpers(self):
        """Helper code must not construct HTTP URLs."""
        helpers_dir = Path(__file__).parent.parent / "src" / "aifp" / "helpers"
        violations = []

        for py_file in helpers_dir.rglob("*.py"):
            content = py_file.read_text(errors="ignore")
            for line_num, line in enumerate(content.splitlines(), 1):
                line_stripped = line.strip()
                # Skip comments and docstrings
                if line_stripped.startswith("#"):
                    continue
                if "http://" in line_stripped or "https://" in line_stripped:
                    violations.append(
                        f"{py_file.name}:{line_num}: {line_stripped[:80]}"
                    )

        assert violations == [], (
            f"HTTP URL references found in helper code:\n"
            + "\n".join(violations)
        )

    def test_all_tools_local_only(self):
        """Redundant with protocol test but critical for submission."""
        resp = handle_list_tools(1)
        non_local = [
            t["name"] for t in resp["result"]["tools"]
            if t["annotations"]["openWorldHint"] is not False
        ]
        assert non_local == [], f"Tools with openWorldHint!=false: {non_local}"


# ============================================================================
# 7. Orchestrator Tools
# ============================================================================

class TestOrchestrators:
    """Verify the key orchestrator tools work through the MCP interface."""

    def test_aifp_run_new_session(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "aifp_run",
                "arguments": {
                    "is_new_session": True,
                },
            })
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_aifp_run_continuation(self):
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "aifp_run",
                "arguments": {
                    "is_new_session": False,
                },
            })
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_aifp_status(self, project_dir):
        project_root, _, _ = project_dir
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "aifp_status",
                "arguments": {
                    "project_root": project_root,
                    "type": "summary",
                },
            })
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True

    def test_aifp_init_via_tool_call(self, tmp_path):
        """Test aifp_init through the MCP tool call interface."""
        data, is_error = _parse_tool_response(
            handle_call_tool(1, {
                "name": "aifp_init",
                "arguments": {"project_root": str(tmp_path)},
            })
        )
        assert is_error is False
        assert isinstance(data, dict)
        assert data.get("success") is True
        assert (tmp_path / AIFP_PROJECT_DIR).is_dir()


# ============================================================================
# 8. Annotation Classification Correctness
# ============================================================================

class TestAnnotationClassification:
    """Verify tool annotations are correctly classified."""

    @pytest.mark.parametrize("tool_name", [
        "get_all_directive_names", "search_directives", "query_project",
        "find_directive_by_intent", "list_active_branches",
        "detect_external_changes", "get_project", "get_file_by_name",
    ])
    def test_read_tools_are_read_only(self, tool_name):
        ann = build_tool_annotations(tool_name)
        assert ann["readOnlyHint"] is True, f"{tool_name} should be readOnly"
        assert ann["idempotentHint"] is True, f"{tool_name} should be idempotent"

    @pytest.mark.parametrize("tool_name", [
        "add_note", "reserve_file", "finalize_file", "create_project",
        "add_theme", "add_flow", "add_milestone", "add_task",
        "activate_user_directive",
    ])
    def test_write_tools_are_not_read_only(self, tool_name):
        ann = build_tool_annotations(tool_name)
        assert ann["readOnlyHint"] is False, f"{tool_name} should not be readOnly"
        assert ann.get("destructiveHint") is False, (
            f"{tool_name} should not be destructive"
        )

    @pytest.mark.parametrize("tool_name", [
        "delete_file", "delete_function", "delete_task",
        "delete_milestone", "delete_theme",
    ])
    def test_delete_tools_are_destructive(self, tool_name):
        ann = build_tool_annotations(tool_name)
        assert ann["readOnlyHint"] is False
        assert ann.get("destructiveHint") is True, (
            f"{tool_name} should be destructive"
        )

    @pytest.mark.parametrize("tool_name", [
        "update_project", "update_task", "update_file", "set_custom_return_statement",
    ])
    def test_update_tools_are_idempotent(self, tool_name):
        ann = build_tool_annotations(tool_name)
        assert ann["readOnlyHint"] is False
        assert ann.get("idempotentHint") is True, (
            f"{tool_name} should be idempotent"
        )

    @pytest.mark.parametrize("tool_name", ["execute_merge", "aifp_end"])
    def test_special_destructive_tools(self, tool_name):
        ann = build_tool_annotations(tool_name)
        assert ann.get("destructiveHint") is True, (
            f"{tool_name} should be destructive"
        )


# ============================================================================
# Entry point for direct execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# AIFP MCP Server Implementation Plan

**Version**: 1.1
**Created**: 2026-02-04
**Status**: Ready for Implementation
**Estimated Scope**: ~15-20 files, ~3500-4500 lines of code
**MCP Tools**: 204 (from 222 total helpers)

---

## Implementation Requirements

### FP Compliance (Mandatory)
- **Functional Programming with DRY**: All code must follow FP patterns (pure functions, immutability, no OOP classes). Apply DRY principles throughout.
- **State Database**: Use `mcp_runtime.db` for any mutable global state that may be needed. No in-memory mutable globals.
- **OOP Library Wrappers**: Any dependencies/libraries that are OOP-based must have FP-compliant wrappers added to `src/aifp/wrappers/`. The MCP Python SDK may require this treatment.

### AIFP Self-Tracking (Dogfooding)
- **Catalogue All Work**: As we code, track all files, functions, and types in `.aifp/project.db` using the reserve → write → finalize workflow.
- **ID Naming Convention**: Follow directive naming patterns (e.g., `mcp_server_1`, `mcp_tools_2`) for easy reference.
- **State Research**: Keeping the project database current enables future development queries and state analysis.

---

## Executive Summary

Build the MCP (Model Context Protocol) server layer that exposes AIFP helper functions as tools for AI assistants. The helper functions are already implemented — this plan focuses on the MCP protocol integration layer.

### Current State
- ✅ All helper functions implemented (`src/aifp/helpers/`)
- ✅ Orchestrators complete (`aifp_init`, `aifp_status`, `aifp_run`, `aifp_end`)
- ✅ Database schemas finalized (4 databases)
- ✅ Directive JSON/MD documentation complete
- ✅ Watchdog module exists
- ❌ No `src/aifp/mcp_server/` directory (needs creation)

### Goal
Wire existing helpers into a production MCP server that AI assistants can connect to via the MCP protocol.

---

## Phase 1: Foundation (Core MCP Infrastructure)

### 1.1 Create MCP Server Directory Structure

```
src/aifp/mcp_server/
├── __init__.py           # Package exports
├── server.py             # Main MCP server entry point
├── tools.py              # Tool registration and definitions
├── handlers.py           # Request handlers for MCP protocol
├── types.py              # Type definitions (FP-compliant frozen dataclasses)
├── errors.py             # Error handling and Result types
└── _common.py            # Shared utilities (connection pooling, etc.)
```

### 1.2 Core Types (`types.py`)

Define FP-compliant frozen dataclasses for MCP protocol:

```python
@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]

@dataclass(frozen=True)
class ToolResult:
    content: Tuple[Dict[str, Any], ...]
    is_error: bool = False

@dataclass(frozen=True)
class MCPRequest:
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None
```

### 1.3 Server Entry Point (`server.py`)

```python
# Main MCP server using mcp Python SDK
# - Registers all is_tool=true helpers as MCP tools
# - Handles tool/list and tool/call requests
# - Routes requests to appropriate helper functions
```

**Key Functions**:
- `create_server()` → Pure: Returns configured MCP server instance
- `_register_tools(server)` → Effect: Registers all tools from helper definitions
- `run_server()` → Effect: Starts the MCP server

---

## Phase 2: Tool Registration System

### 2.1 Tool Discovery (`tools.py`)

Query `aifp_core.db` for helpers with `is_tool=true`:

```python
def get_tool_helpers() -> Tuple[Dict[str, Any], ...]:
    """
    Query aifp_core.db for all helpers where is_tool=true.
    Returns tuple of helper definitions with parameters, purpose, etc.
    """
```

### 2.2 Schema Generation

Convert helper parameters to JSON Schema for MCP tool registration:

```python
def helper_to_json_schema(helper: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert helper parameter definitions to JSON Schema.

    Example:
    {
        "name": "project_root",
        "type": "string",
        "required": true,
        "description": "Path to project root"
    }
    →
    {
        "type": "object",
        "properties": {
            "project_root": {
                "type": "string",
                "description": "Path to project root"
            }
        },
        "required": ["project_root"]
    }
    """
```

### 2.3 Tool Categories

Group tools by target_database for organization:

| Category | target_database | Example Tools |
|----------|-----------------|---------------|
| **Entry Points** | multi_db | `aifp_run`, `aifp_init`, `aifp_status`, `aifp_end` |
| **Project CRUD** | project | `get_from_project`, `add_project_entry`, `update_project_entry` |
| **Project Schema** | project | `get_project_tables`, `get_project_fields`, `get_project_schema` |
| **Core/Directives** | core | `get_directive`, `search_directives`, `get_fp_directive_index` |
| **User Preferences** | user_preferences | `get_user_settings`, `update_user_setting` |
| **User Directives** | user_directives | `create_user_directive`, `get_user_directive` |
| **Git** | no_db | `git_status`, `git_create_branch` |
| **Global** | no_db | `get_supportive_context`, `get_databases` |

---

## Phase 3: Request Handlers

### 3.1 Tool Dispatcher (`handlers.py`)

```python
def handle_tool_call(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Result:
    """
    Route tool call to appropriate helper function.

    1. Validate tool_name exists
    2. Validate arguments against schema
    3. Import and call helper function
    4. Wrap result in MCP format
    """
```

### 3.2 Helper Import Registry

Dynamic import registry mapping tool names to helper functions:

```python
TOOL_REGISTRY = {
    # Entry Points (multi_db)
    'aifp_run': ('aifp.helpers.orchestrators.entry_points', 'aifp_run'),
    'aifp_init': ('aifp.helpers.orchestrators.entry_points', 'aifp_init'),
    'aifp_status': ('aifp.helpers.orchestrators.entry_points', 'aifp_status'),
    'aifp_end': ('aifp.helpers.orchestrators.entry_points', 'aifp_end'),

    # Orchestrators
    'get_project_status': ('aifp.helpers.orchestrators.status', 'get_project_status'),
    'get_task_context': ('aifp.helpers.orchestrators.status', 'get_task_context'),
    'get_current_progress': ('aifp.helpers.orchestrators.state', 'get_current_progress'),
    'update_project_state': ('aifp.helpers.orchestrators.state', 'update_project_state'),
    'batch_update_progress': ('aifp.helpers.orchestrators.state', 'batch_update_progress'),
    'query_project_state': ('aifp.helpers.orchestrators.query', 'query_project_state'),

    # Project CRUD (src/aifp/helpers/project/crud.py)
    'get_from_project': ('aifp.helpers.project.crud', 'get_from_project'),
    'get_from_project_where': ('aifp.helpers.project.crud', 'get_from_project_where'),
    'query_project': ('aifp.helpers.project.crud', 'query_project'),
    'add_project_entry': ('aifp.helpers.project.crud', 'add_project_entry'),
    'update_project_entry': ('aifp.helpers.project.crud', 'update_project_entry'),
    'delete_project_entry': ('aifp.helpers.project.crud', 'delete_project_entry'),
    'delete_reserved': ('aifp.helpers.project.crud', 'delete_reserved'),

    # Project Schema (src/aifp/helpers/project/schema.py)
    'get_project_tables': ('aifp.helpers.project.schema', 'get_project_tables'),
    'get_project_fields': ('aifp.helpers.project.schema', 'get_project_fields'),
    'get_project_schema': ('aifp.helpers.project.schema', 'get_project_schema'),
    'get_project_json_parameters': ('aifp.helpers.project.schema', 'get_project_json_parameters'),

    # Project Metadata (src/aifp/helpers/project/metadata.py)
    'create_project': ('aifp.helpers.project.metadata', 'create_project'),
    'get_project': ('aifp.helpers.project.metadata', 'get_project'),
    'update_project': ('aifp.helpers.project.metadata', 'update_project'),
    'get_infrastructure_by_type': ('aifp.helpers.project.metadata', 'get_infrastructure_by_type'),
    'get_all_infrastructure': ('aifp.helpers.project.metadata', 'get_all_infrastructure'),
    'get_source_directory': ('aifp.helpers.project.metadata', 'get_source_directory'),
    'update_source_directory': ('aifp.helpers.project.metadata', 'update_source_directory'),
    'get_project_root': ('aifp.helpers.project.metadata', 'get_project_root'),
    'update_project_root': ('aifp.helpers.project.metadata', 'update_project_root'),
    'blueprint_has_changed': ('aifp.helpers.project.metadata', 'blueprint_has_changed'),

    # Project Validation (src/aifp/helpers/project/validation.py)
    'project_allowed_check_constraints': ('aifp.helpers.project.validation', 'project_allowed_check_constraints'),

    # Core/Directives (src/aifp/helpers/core/)
    'get_directive': ('aifp.helpers.core.directives_1', 'get_directive'),
    'get_directive_content': ('aifp.helpers.core.directives_1', 'get_directive_content'),
    'search_directives': ('aifp.helpers.core.directives_1', 'search_directives'),
    'get_fp_directive_index': ('aifp.helpers.core.directives_1', 'get_fp_directive_index'),
    'get_all_directive_names': ('aifp.helpers.core.directives_1', 'get_all_directive_names'),

    # Core/Flows (src/aifp/helpers/core/flows.py)
    'get_flows_from_directive': ('aifp.helpers.core.flows', 'get_flows_from_directive'),

    # Global (src/aifp/helpers/global/)
    'get_supportive_context': ('aifp.helpers.global.supportive_context', 'get_supportive_context'),
    'get_databases': ('aifp.helpers.global.database_info', 'get_databases'),

    # ... Additional helpers to be mapped
}
```

### 3.3 Result Serialization

Convert helper `Result` objects to MCP-compatible format:

```python
def serialize_result(result: Result) -> ToolResult:
    """
    Convert helper Result to MCP ToolResult format.

    Result(success=True, data={...}) → ToolResult(content=[{type: "text", text: json}])
    Result(success=False, error="...") → ToolResult(content=[{type: "text", text: error}], is_error=True)
    """
```

---

## Phase 4: Error Handling & Validation

### 4.1 Error Types (`errors.py`)

```python
@dataclass(frozen=True)
class MCPError:
    code: int
    message: str
    data: Optional[Dict[str, Any]] = None

# Standard MCP error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603
```

### 4.2 Input Validation

```python
def validate_tool_arguments(
    tool_name: str,
    arguments: Dict[str, Any],
    schema: Dict[str, Any]
) -> Result:
    """
    Validate arguments against JSON Schema.
    Returns Result with validated args or error.
    """
```

---

## Phase 5: Testing Infrastructure

### 5.1 Test Structure

```
tests/
├── unit/
│   └── mcp_server/
│       ├── test_tools.py      # Tool registration tests
│       ├── test_handlers.py   # Handler tests
│       └── test_types.py      # Type tests
├── integration/
│   └── mcp_server/
│       ├── test_server.py     # Full server tests
│       └── test_protocol.py   # MCP protocol compliance
└── fixtures/
    └── mcp/
        └── sample_requests.json
```

### 5.2 Key Test Cases

1. **Tool Registration**
   - All `is_tool=true` helpers registered
   - Correct JSON schemas generated
   - No sub-helpers exposed

2. **Request Handling**
   - Valid tool calls succeed
   - Invalid tool names return METHOD_NOT_FOUND
   - Invalid params return INVALID_PARAMS
   - Helper errors propagate correctly

3. **Protocol Compliance**
   - tools/list returns all tools
   - tools/call routes correctly
   - Result format is MCP-compliant

---

## Phase 6: Package Integration

### 6.1 Entry Point Script (`src/aifp/__main__.py`)

```python
"""
AIFP MCP Server entry point.
Usage: python -m aifp
"""
from aifp.mcp_server.server import run_server

if __name__ == "__main__":
    run_server()
```

### 6.2 Package Configuration (`pyproject.toml`)

```toml
[project.scripts]
aifp = "aifp.mcp_server.server:run_server"
```

### 6.3 Claude Desktop Config Example

```json
{
  "mcpServers": {
    "aifp": {
      "command": "python",
      "args": ["-m", "aifp"],
      "env": {
        "AIFP_CORE_DB": "/path/to/aifp_core.db"
      }
    }
  }
}
```

---

## Implementation Order

### Milestone 1: Minimal Working Server
1. Create `src/aifp/mcp_server/` directory structure
2. Implement `types.py` with core dataclasses
3. Implement `errors.py` with error handling
4. Implement `tools.py` with tool discovery (query aifp_core.db)
5. Implement `server.py` with basic MCP server (tools/list only)
6. **Verify**: Server starts and responds to tools/list

### Milestone 2: Tool Execution
7. Implement `handlers.py` with tool dispatcher
8. Build `TOOL_REGISTRY` mapping (start with entry points only)
9. Implement `_common.py` with shared utilities
10. Wire tools/call to handler
11. **Verify**: `aifp_run(is_new_session=true)` works end-to-end

### Milestone 3: Full Tool Coverage
12. Expand TOOL_REGISTRY to all `is_tool=true` helpers
13. Implement schema generation for all parameter types
14. Add input validation
15. **Verify**: All tools callable with valid params

### Milestone 4: Testing & Polish
16. Add unit tests for each module
17. Add integration tests for MCP protocol
18. Add error handling edge cases
19. Performance optimization (lazy imports, caching)
20. **Verify**: >90% test coverage, all edge cases handled

### Milestone 5: Distribution
21. Update `pyproject.toml` with entry point
22. Create `__main__.py` entry point
23. Update README with installation instructions
24. Test pip installation flow
25. **Verify**: `pip install aifp && aifp` works

---

## Key Design Decisions

### 1. Static vs Dynamic Tool Registration
**Decision**: Static TOOL_REGISTRY with lazy imports

**Rationale**:
- Predictable tool list (no runtime surprises)
- Fast startup (imports only when tool called)
- Easy to test and debug

### 2. Helper Result → MCP Result Conversion
**Decision**: Serialize helper Result.data to JSON text

**Rationale**:
- MCP expects `content: [{type: "text", text: "..."}]`
- JSON serialization handles all Python types
- AI can parse JSON easily

### 3. Error Handling Strategy
**Decision**: Convert all errors to MCP error format

**Rationale**:
- Consistent error experience for AI
- Standard MCP error codes for protocol compliance
- Helper errors include context (tool name, params)

### 4. Connection Pooling
**Decision**: One connection per request (no pooling)

**Rationale**:
- SQLite is fast for single connections
- Avoids connection lifecycle complexity
- Thread-safe without locks

---

## Dependencies

### Required
- `mcp` - MCP Python SDK
- `sqlite3` - Database access (stdlib)
- `dataclasses` - Type definitions (stdlib)
- `json` - Serialization (stdlib)

### Development
- `pytest` - Testing
- `pytest-asyncio` - Async test support (if MCP SDK uses asyncio)
- `hypothesis` - Property-based testing

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP SDK API changes | Medium | High | Pin SDK version, abstract SDK calls |
| Helper signature changes | Low | Medium | Integration tests catch mismatches |
| Performance issues | Low | Medium | Lazy imports, profiling |
| Missing tool edge cases | Medium | Low | Comprehensive test suite |

---

## Success Criteria

1. **Functional**: All `is_tool=true` helpers callable via MCP
2. **Compliant**: Passes MCP protocol validation
3. **Tested**: >90% test coverage
4. **Documented**: README updated with usage
5. **Installable**: `pip install aifp` works
6. **Integrated**: Works with Claude Desktop

---

## Appendix: Helper Tool Count

Accurate tool counts from `dev/helpers-json/` files:

| File | is_tool=true |
|------|--------------|
| helpers-core.json | 33 |
| helpers-git.json | 7 |
| helpers-index.json | 2 |
| helpers-orchestrators.json | 9 |
| helpers-project-1.json | 22 |
| helpers-project-2.json | 9 |
| helpers-project-3.json | 9 |
| helpers-project-4.json | 10 |
| helpers-project-5.json | 11 |
| helpers-project-6.json | 11 |
| helpers-project-7.json | 15 |
| helpers-project-8.json | 14 |
| helpers-project-9.json | 10 |
| helpers-settings.json | 23 |
| helpers-user-custom.json | 19 |
| **Total** | **204** |

**Summary**:
- Total helpers: 222
- MCP Tools (is_tool=true): **204**
- Sub-helpers (is_sub_helper=true): 4
- Non-tools: 18

---

*Plan created for AIFP MCP Server implementation on 2026-02-04*

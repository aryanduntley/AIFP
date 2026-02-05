# AIFP MCP Server Implementation Plan

**Version**: 1.2
**Created**: 2026-02-04
**Updated**: 2026-02-05
**Status**: Ready for Implementation
**Estimated Scope**: ~12-15 files, ~3000-4000 lines of code
**MCP Tools**: 204 (from 222 total helpers)

---

## Known Issues — MUST FIX BEFORE IMPLEMENTATION

These issues were discovered during codebase research and must be resolved before any MCP server code is written. Fixing them first prevents cascading import failures during development.

### ~~Issue 1: `global` is a Python Keyword~~ — RESOLVED
Renamed `src/aifp/helpers/global/` → `src/aifp/helpers/shared/`. Updated all imports, helper JSON paths, and rebuilt aifp_core.db.

### ~~Issue 2: `sys.path` Hacks in Global Helpers~~ — RESOLVED
Converted `sys.path.insert()` hacks to relative imports (`from ..utils import ...`) in both `shared/database_info.py` and `shared/supportive_context.py`.

### ~~Issue 2b: `TODO_helpers/` Stale Paths in Helper JSON~~ — RESOLVED
Fixed 20 stale `TODO_helpers/` prefixes in `dev/helpers-json/helpers-index.json` and `dev/helpers-json/helpers-user-custom.json`. All implementations exist — only the JSON `file_path` fields were outdated.

### ~~Issue 3: Missing Package Files~~ — RESOLVED
Created `pyproject.toml` (file 201), `src/aifp/__init__.py` (file 202), `src/aifp/__main__.py` (file 203). All tracked in project.db.

### ~~Issue 4: `mcp_server/` Directory Exists But Is Empty~~ — RESOLVED
Populated with: `__init__.py` (210), `server.py` (209), `registry.py` (208), `schema.py` (206), `serialization.py` (207), `errors.py` (205). All tracked in project.db.

---

## MCP SDK Details

### Package
- **Name**: `mcp` (pip install mcp)
- **Stable Version**: v1.26.0+
- **Install for development**: `gpip3 mcp` (installs to `~/python-libraries`)
- **Install for distribution**: Declared as dependency in `pyproject.toml` — pip handles it automatically when users install aifp

### API Choice: Low-Level `mcp.server.Server`
The MCP Python SDK provides two APIs:
- **FastMCP**: Decorator-based, auto-generates schemas from type hints
- **Low-level Server**: Explicit `@server.list_tools()` and `@server.call_tool()` handlers

**Decision**: Use the **low-level Server API** because:
- 204 tools need programmatic registration from a data structure, not 204 individual decorators
- Tool parameter schemas come from `aifp_core.db`, not Python type hints
- Full control over the `list_tools` and `call_tool` dispatch logic
- Both APIs are OOP under the hood, so the FP wrapper cost is identical

### Transport
- **stdio** (standard for Claude Desktop / Claude Code integration)
- Single-client, synchronous request handling — no concurrency concerns
- Existing sync helpers can be called directly from async handlers without `asyncio.to_thread()` because stdio is single-request-at-a-time

### Key SDK Types
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
```

---

## Implementation Requirements

### FP Compliance (Mandatory)
- **Functional Programming with DRY**: All code must follow FP patterns (pure functions, immutability, no OOP classes). Apply DRY principles throughout.
- **State Database**: Use `mcp_runtime.db` for any mutable global state that may be needed. No in-memory mutable globals.
- **OOP Library Wrappers**: The MCP Python SDK's `Server` class is OOP. An FP wrapper must be added to `src/aifp/wrappers/mcp_sdk.py` following the same pattern as `src/aifp/wrappers/filesystem_observer.py`.

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
- ✅ `src/aifp/mcp_server/` directory exists (empty, needs implementation)
- ✅ `pyproject.toml`, `__init__.py`, `__main__.py` created
- ✅ MCP SDK installed (`~/python-libraries/mcp`)
- ✅ MCP server layer complete (Milestone 1) — 4 entry point tools working

### Goal
Wire existing helpers into a production MCP server that AI assistants can connect to via the MCP protocol.

---

## Architecture

### File Structure

```
src/aifp/
├── __init__.py              # NEW - Package marker
├── __main__.py              # NEW - Entry point: python -m aifp
├── mcp_server/
│   ├── __init__.py          # NEW - Package exports (run_server)
│   ├── server.py            # NEW - Server creation, handler wiring, run_server()
│   ├── registry.py          # NEW - TOOL_REGISTRY dict (204 entries) + lazy import
│   ├── schema.py            # NEW - Parameter defs → JSON Schema conversion
│   ├── serialization.py     # NEW - Result types → JSON text for MCP TextContent
│   └── errors.py            # NEW - MCP error codes + error formatters
├── wrappers/
│   └── mcp_sdk.py           # NEW - FP wrapper for mcp.server.Server OOP
pyproject.toml               # NEW - Project root
```

### FP Wrapper (`src/aifp/wrappers/mcp_sdk.py`)

Wraps the OOP `mcp.server.Server` following the pattern established by `filesystem_observer.py`:

```python
# Frozen dataclasses for MCP types
@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]

# Effect functions for server lifecycle
def _effect_create_server() -> Server
def _effect_register_handlers(server, list_tools_handler, call_tool_handler) -> None
def _effect_run_server(server) -> None

# Pure conversion functions
def tool_definition_to_mcp_tool(defn: ToolDefinition) -> Tool
def make_text_content(text: str) -> TextContent
```

### Tool Registry (`registry.py`)

Static dict mapping all 204 tool names to `(module_path, function_name)` tuples:

```python
TOOL_REGISTRY: Final[Dict[str, Tuple[str, str]]] = {
    'aifp_run': ('aifp.helpers.orchestrators.entry_points', 'aifp_run'),
    'aifp_init': ('aifp.helpers.orchestrators.entry_points', 'aifp_init'),
    # ... all 204 entries
}

def _effect_import_tool_function(tool_name: str) -> Callable:
    """Lazy import: importlib.import_module + getattr."""
```

**Why static, not DB-driven**: Predictable tool list, no runtime DB dependency for tool listing, `file_path` field in DB uses inconsistent prefixes (`helpers/` vs `TODO_helpers/`), easy to test.

**Why importlib**: Provides uniform dynamic import for all 204 tools. Eliminates the need for static import statements in the dispatcher.

### Schema Generation (`schema.py`)

Converts helper parameter definitions from `aifp_core.db` to JSON Schema:

```python
# Parameter type mapping
PARAM_TYPE_MAP = {
    'string': 'string', 'str': 'string',
    'boolean': 'boolean',
    'integer': 'integer',
    'number': 'number', 'float': 'number',
    'array': 'array',
    'object': 'object',
}

def params_to_input_schema(params: Tuple[Dict, ...]) -> Dict[str, Any]:
    """Convert parameter definitions to MCP-compatible JSON Schema."""
```

### Result Serialization (`serialization.py`)

Handles all frozen dataclass result types (`Result`, `QueryResult`, `SchemaResult`, `DirectiveResult`, `DirectivesResult`, `IntentMatchResult`, `KeywordsResult`, etc.):

```python
def serialize_result(result: Any) -> str:
    """Serialize any helper result to JSON string via dataclasses.asdict()."""

def is_error_result(result: Any) -> bool:
    """Check if result represents an error (success=False)."""
```

Strategy: `dataclasses.asdict()` for frozen dataclass results, `json.dumps()` with custom default handler for edge cases (frozenset, Path, datetime, bytes).

### Server Core (`server.py`)

```python
# Startup: load tool definitions from aifp_core.db, cache as MCP Tool objects
def _effect_load_tool_definitions() -> Tuple[ToolDefinition, ...]
def _effect_initialize_tools() -> None  # Sets module-level cache

# Async handlers (passed to wrapper)
async def _handle_list_tools() -> list[Tool]       # Returns cached tools
async def _handle_call_tool(name, args) -> list[TextContent]  # Lazy import + call + serialize

# Entry point
def run_server() -> None  # Creates server, registers handlers, starts stdio
```

**Tool call flow**: `call_tool` → check registry → lazy import helper → call with `**arguments` → `serialize_result()` → wrap in `TextContent` → return.

**No separate argument validation**: Helpers already validate their own parameters and return error Results. Adding a JSON Schema validation layer would duplicate effort.

---

## Tool Categories

| Category | target_database | Count | Source Files |
|----------|-----------------|-------|--------------|
| **Entry Points** | multi_db | 4 | orchestrators/entry_points.py |
| **Orchestrators** | project | 5 | orchestrators/status.py, state.py, query.py |
| **Core/Directives** | core | 33 | core/directives_1.py, directives_2.py, flows.py, schema.py, validation.py |
| **Project CRUD** | project | 7 | project/crud.py |
| **Project Schema** | project | 4 | project/schema.py |
| **Project Metadata** | project | 10 | project/metadata.py |
| **Project Files** | project | 9 | project/files_1.py, files_2.py |
| **Project Functions** | project | 9 | project/functions_1.py, functions_2.py |
| **Project Tasks** | project | 15 | project/tasks.py |
| **Project Subtasks/Sidequests** | project | 14 | project/subtasks_sidequests.py |
| **Project Items/Notes** | project | 9 | project/items_notes.py |
| **Project Interactions** | project | 3 | project/interactions.py |
| **Project Themes/Flows** | project | 22 | project/themes_flows_1.py, themes_flows_2.py |
| **Project Types** | project | 7 | project/types_1.py, types_2.py |
| **Project State DB** | project | 1 | project/state_db.py |
| **Project Validation** | project | 1 | project/validation.py |
| **User Preferences** | user_preferences | 23 | user_preferences/crud.py, management.py, schema.py, validation.py |
| **User Directives** | user_directives | 19 | user_directives/crud.py, management.py, schema.py, validation.py |
| **Git** | no_db | 7 | git/operations.py |
| **Global** | no_db | 2 | shared/supportive_context.py, database_info.py |
| **Total** | | **204** | |

---

## Error Handling (`errors.py`)

```python
# Standard MCP/JSON-RPC error codes
PARSE_ERROR     = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS  = -32602
INTERNAL_ERROR  = -32603

# Pure formatter functions
def format_tool_not_found_error(tool_name: str) -> str
def format_invalid_params_error(tool_name: str, detail: str) -> str
def format_internal_error(tool_name: str, error: Exception) -> str
def format_import_error(tool_name: str, error: Exception) -> str
```

---

## Dependencies

### Runtime (Required)
- `mcp>=1.26.0` — MCP Python SDK (includes Server, stdio transport, Tool/TextContent types)
- `sqlite3` — Database access (stdlib)
- `dataclasses` — Type definitions (stdlib)
- `json` — Serialization (stdlib)
- `importlib` — Lazy imports (stdlib)

### Development
- `pytest` — Testing
- `pytest-asyncio` — Async handler tests
- `hypothesis` — Property-based testing

### Installation

**For development** (install to `~/python-libraries`):
```bash
gpip3 mcp
```

**For distribution** (`pyproject.toml` dependency):
```toml
[project]
dependencies = ["mcp>=1.26.0"]
```
When users `pip install aifp`, pip pulls `mcp` automatically. No bundling, no custom folders.

---

## Implementation Order

### ~~Pre-Step: Fix Known Issues~~ — COMPLETE
1. ~~Audit and fix `sys.path` hacks~~ — converted to relative imports
2. ~~Rename `global/` → `shared/`~~ — done, all imports/JSON updated
3. ~~Fix `TODO_helpers/` stale JSON paths~~ — 20 entries corrected
4. ~~Install MCP SDK~~ — `gpip3 mcp` (installed to `~/python-libraries`)

### ~~Milestone 1: Package Foundation + Minimal Server~~ — COMPLETE
1. ~~Create `pyproject.toml` with dependencies and entry point~~ ✓ (file 201)
2. ~~Create `src/aifp/__init__.py` (minimal package marker)~~ ✓ (file 202)
3. ~~Create `src/aifp/__main__.py` (calls `run_server()`)~~ ✓ (file 203)
4. ~~Create `src/aifp/wrappers/mcp_sdk.py` (FP wrapper for MCP SDK)~~ ✓ (file 204)
5. ~~Create `src/aifp/mcp_server/errors.py`~~ ✓ (file 205)
6. ~~Create `src/aifp/mcp_server/schema.py`~~ ✓ (file 206)
7. ~~Create `src/aifp/mcp_server/serialization.py`~~ ✓ (file 207)
8. ~~Create `src/aifp/mcp_server/registry.py` (start with entry points only: 4 tools)~~ ✓ (file 208)
9. ~~Create `src/aifp/mcp_server/server.py`~~ ✓ (file 209)
10. ~~Create `src/aifp/mcp_server/__init__.py`~~ ✓ (file 210)
11. ~~**Verify**: `python -m aifp` starts, `tools/list` returns 4 tools, `aifp_run` callable~~ ✓

**Verified**: Server starts on stdio (exit 124 = timeout kill = was running). `list_tools` returns 4 tools. `aifp_run(is_new_session=False)` returns `{"success": true, ...}`. Unknown tools return clean error. All 7 new files + 25 functions tracked in project.db (210 files, 315 functions total).

### Milestone 2: Full Tool Coverage
12. Expand `registry.py` to all 204 `is_tool=true` helpers
13. **Verify**: `tools/list` returns 204 tools, representative tools from each category callable

### Milestone 3: Testing & Polish
14. Unit tests: schema generation, serialization, registry completeness
15. Integration tests: full server start, tool call round-trips
16. Error handling edge cases
17. **Verify**: >90% test coverage

### Milestone 4: Distribution
18. Finalize `pyproject.toml` with metadata
19. Update README with MCP server installation/usage
20. Test `pip install aifp && aifp` flow
21. **Verify**: Works with Claude Desktop configuration

---

## Key Design Decisions

### 1. Low-Level Server API over FastMCP
**Decision**: Use `mcp.server.Server` with explicit handlers

**Rationale**:
- 204 tools need programmatic registration from data, not decorators
- Schemas come from `aifp_core.db`, not Python type hints
- Full control over dispatch logic
- Both APIs are OOP under the hood; wrapper cost is identical

### 2. Static TOOL_REGISTRY with Lazy Imports
**Decision**: Hardcoded dict + `importlib.import_module()` on first call

**Rationale**:
- Predictable tool list (no runtime surprises)
- Fast startup (no helper modules imported until needed)
- Python caches modules after first import (subsequent calls instant)
- `importlib` handles the `global` keyword directory name
- Easy to test and debug

### 3. Result Serialization via `dataclasses.asdict()`
**Decision**: Use `dataclasses.asdict()` + `json.dumps()` with custom default handler

**Rationale**:
- All helper results are frozen dataclasses — `asdict()` handles them uniformly
- Custom default handler covers edge cases (frozenset, Path, datetime)
- MCP expects `content: [{type: "text", text: "..."}]` — JSON string works
- AI can parse JSON natively

### 4. No Separate Argument Validation
**Decision**: Let helpers validate their own parameters

**Rationale**:
- Helpers already validate inputs and return error Results
- Adding JSON Schema validation would duplicate effort
- Helper error messages are more specific and useful than generic schema errors

### 5. One Connection Per Request
**Decision**: No connection pooling

**Rationale**:
- SQLite is fast for single connections (~1ms)
- stdio transport is single-client, single-request
- Avoids connection lifecycle complexity
- Thread-safe without locks

---

## Testing

### Unit Tests
```
tests/mcp_server/
├── test_schema.py         # JSON Schema generation from param defs
├── test_serialization.py  # Result type → JSON conversion
├── test_registry.py       # All 204 entries valid, modules importable
└── test_errors.py         # Error formatters produce valid JSON
```

### Integration Tests
```
tests/mcp_server/
├── test_server.py         # Server starts, list_tools, call_tool round-trip
└── test_protocol.py       # MCP protocol compliance checks
```

### Key Assertions
- `len(TOOL_REGISTRY) == 204`
- Every registry module path is importable
- Every registry function name exists in its module
- `serialize_result()` handles all Result subclasses
- `_handle_call_tool('unknown_tool', {})` returns error, not crash
- `_handle_call_tool('get_supportive_context', {})` returns valid content

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MCP SDK API changes | Medium | High | Pin SDK version `>=1.26.0`, abstract via `wrappers/mcp_sdk.py` |
| Helper signature changes | Low | Medium | Integration tests catch mismatches |
| ~~`global/` keyword conflicts~~ | ~~Known~~ | ~~Medium~~ | ~~Renamed to `shared/`~~ — RESOLVED |
| ~~`sys.path` hacks break imports~~ | ~~Known~~ | ~~High~~ | ~~Converted to relative imports~~ — RESOLVED |
| Sync helpers blocking async loop | Low | Low | stdio is single-client; `asyncio.to_thread()` available if needed |

---

## Success Criteria

1. **Functional**: All 204 `is_tool=true` helpers callable via MCP
2. **Compliant**: Passes MCP protocol validation
3. **FP-Compliant**: Zero OOP violations, all wrappers in place
4. **Tested**: >90% test coverage
5. **Documented**: README updated with usage
6. **Installable**: `pip install aifp` works
7. **Integrated**: Works with Claude Desktop / Claude Code

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

## Appendix: Claude Desktop Configuration

```json
{
  "mcpServers": {
    "aifp": {
      "command": "python3",
      "args": ["-m", "aifp"],
      "env": {}
    }
  }
}
```

No `AIFP_CORE_DB` env var needed — the server resolves the path to `aifp_core.db` relative to its own installation directory via `database/connection.py:get_core_db_path()`.

---

*Plan updated 2026-02-05 with MCP SDK research, FP wrapper design, known issues, and dependency strategy.*

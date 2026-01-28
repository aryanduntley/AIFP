# Directive Flow Helpers - Refactor Analysis

**Created**: 2026-01-27
**Status**: ✅ COMPLETE - Refactored 2026-01-27

**Summary**: Replaced 5 deep-logic helpers with 3 simple query helpers.
- Removed: `get_next_directives_from_status`, `get_matching_next_directives`, `get_conditional_work_paths`, `search_fp_references`, `get_contextual_utilities`
- Added: `get_flows_from_directive`, `get_flows_to_directive`, `get_wildcard_flows`
- Kept: `get_completion_loop_target`, `get_directive_flows`

---

## The Problem

The current `core/flows.py` implementation contains helpers with **complex embedded logic** that violates the AIFP MCP server's core purpose:

### Current Problematic Helpers

1. **`get_next_directives_from_status`**
   - Queries directive_flow table
   - Retrieves project status from project.db internally
   - Evaluates conditions against status
   - Returns flows with `condition_met` flags

2. **`get_matching_next_directives`**
   - Same as above but filters to only matching flows

3. **`get_conditional_work_paths`**
   - Same pattern - retrieves context, evaluates conditions

### Why This Is Wrong

1. **MCP Server Purpose**: The MCP server is for **data keeping**, not complex logic. It provides database interface helpers so AI can track, manage, and retrieve data efficiently.

2. **AI Handles Logic**: AI knows its current status. AI knows what work it's doing. AI can determine which directive is appropriate. We shouldn't try to embed that decision logic into helpers.

3. **Cross-Database Queries**: These helpers query TWO databases (aifp_core.db + project.db), mixing concerns.

4. **Unpredictable Returns**: Complex logic trying to provide "intelligent" returns often fails edge cases. Simple CRUD is predictable.

5. **Duplication Risk**: Status retrieval logic duplicated between flow helpers and orchestrators.

---

## The Solution: Simple CRUD + Targeted Queries

### What directive_flow Table Represents

The `directive_flow` table is a **lineage/branched tree representation** of directives:

```
directive_flow
├── id
├── from_directive     (source directive name, '*' for wildcard)
├── to_directive       (target directive name)
├── flow_category      ('project', 'fp', 'user_preferences', 'git')
├── flow_type          ('status_branch', 'completion_loop', 'conditional', etc.)
├── condition_key      (field name for conditional flows)
├── condition_value    (expected value for conditional flows)
├── condition_description
├── priority
└── description
```

### How AI Uses This

1. AI is at directive X, wants to know what comes next
2. AI queries: `get_flows_from_directive("directive_x")`
3. Gets back tree of possible next directives with their conditions
4. AI **evaluates conditions itself** (it knows its status from orchestrator)
5. AI decides which path to take
6. AI queries directive details if needed: `get_directive_by_name("chosen_directive")`

### Proposed Helpers (Simple CRUD + Targeted)

#### Basic CRUD

```python
# Get single flow by ID
get_flow(flow_id: int) -> FlowResult

# Get all flows (with optional filters)
get_flows(
    flow_category: Optional[str] = None,
    flow_type: Optional[str] = None
) -> FlowsResult

# Add flow (admin use - core db typically read-only)
add_flow(...) -> SimpleResult

# Update flow (admin use)
update_flow(...) -> SimpleResult

# Delete flow (admin use)
delete_flow(flow_id: int) -> SimpleResult
```

#### Targeted Queries (What AI Actually Needs)

```python
# Get all flows FROM a directive (what comes next?)
get_flows_from_directive(from_directive: str) -> FlowsResult
# Example: get_flows_from_directive("aifp_status")
# Returns: all flows where from_directive = "aifp_status"

# Get all flows TO a directive (what leads here?)
get_flows_to_directive(to_directive: str) -> FlowsResult
# Example: get_flows_to_directive("project_file_write")
# Returns: all flows where to_directive = "project_file_write"

# Get flow tree/lineage from a directive (full path forward)
get_flow_tree(directive_name: str, depth: int = 3) -> FlowTreeResult
# Returns: nested structure of possible paths from this directive
# AI can traverse this to understand workflow options

# Get wildcard flows (available from ANY context)
get_wildcard_flows(flow_type: Optional[str] = None) -> FlowsResult
# Returns: flows where from_directive = '*'
# These are reference/utility directives available anywhere

# Get completion loop target (simple lookup)
get_completion_loop(from_directive: str) -> FlowResult
# Returns: the single completion_loop flow if exists
# Simple query, no logic: WHERE from_directive=? AND flow_type='completion_loop'
```

### What We Remove

| Current Helper | Replacement |
|----------------|-------------|
| `get_next_directives_from_status` | `get_flows_from_directive` (AI evaluates conditions) |
| `get_matching_next_directives` | `get_flows_from_directive` (AI filters) |
| `get_conditional_work_paths` | `get_flows_from_directive` + filter by flow_type |
| `search_fp_references` | `get_wildcard_flows(flow_type='reference_consultation')` |
| `get_contextual_utilities` | `get_wildcard_flows(flow_type='utility')` |

### What We Keep (Already Simple)

| Helper | Status |
|--------|--------|
| `get_directive_flows` | ✅ Keep - already simple filter query |
| `get_completion_loop_target` | ✅ Keep - simple lookup, no logic |

---

## AI Workflow Example

**Before (complex helper tries to be smart):**
```
AI: get_next_directives_from_status("aifp_status", "/path/to/project")
Helper: [queries flows, queries project.db, evaluates conditions]
Returns: {flows with condition_met flags}
AI: picks one
```

**After (simple data, AI decides):**
```
AI: get_flows_from_directive("aifp_status")
Returns: [
  {to: "project_init", condition_key: "is_initialized", condition_value: "false"},
  {to: "project_task_select", condition_key: "has_active_tasks", condition_value: "true"},
  ...
]
AI: [knows status from orchestrator: is_initialized=true, has_active_tasks=true]
AI: [evaluates: project_init doesn't match, project_task_select matches]
AI: [decides to go to project_task_select]
AI: get_directive_by_name("project_task_select") # if needs details
```

The second approach is:
- Simpler helpers
- Predictable returns
- AI has full control over logic
- No cross-database queries in core helpers
- No duplicated status retrieval

---

## Implementation Plan

### Phase 1: Simplify flows.py

1. Remove complex logic helpers:
   - `get_next_directives_from_status` → replace with `get_flows_from_directive`
   - `get_matching_next_directives` → remove (AI filters)
   - `get_conditional_work_paths` → remove (use `get_flows_from_directive`)
   - `search_fp_references` → replace with `get_wildcard_flows`
   - `get_contextual_utilities` → replace with `get_wildcard_flows`

2. Add simple targeted queries:
   - `get_flows_from_directive(from_directive: str)`
   - `get_flows_to_directive(to_directive: str)`
   - `get_flow_tree(directive_name: str, depth: int)`
   - `get_wildcard_flows(flow_type: Optional[str])`

3. Keep:
   - `get_directive_flows` (already simple)
   - `get_completion_loop_target` (already simple)

### Phase 2: Update JSON

Update `helpers-core.json` to reflect new helper set.

### Phase 3: Remove Cross-DB Code

Remove `_get_project_status()` and related imports from `core/flows.py`.

---

## Impact on Helper Counts

| Change | Count |
|--------|-------|
| Remove complex helpers | -5 |
| Add simple helpers | +4 |
| Net change | -1 |

**New total**: 223 helpers (was 224)
**Core helpers**: 37 (was 38)

---

## Questions for Review

1. Is `get_flow_tree` needed, or can AI traverse manually?
2. Should CRUD (add/update/delete) be included for admin use, or is core db truly read-only?
3. Any other specific query patterns AI would need?

---

---

## Appendix: utils.py and _common.py Changes Review

### Changes Made to `src/aifp/helpers/utils.py`

**Original** (before this session):
- `get_core_db_path()` - path to aifp_core.db
- `get_return_statements(helper_name)` - fetch return statements from core db

**Added**:
```python
# Database path constants
AIFP_PROJECT_DIR: Final[str] = ".aifp-project"
CORE_DB_NAME: Final[str] = "aifp_core.db"
PROJECT_DB_NAME: Final[str] = "project.db"
USER_PREFERENCES_DB_NAME: Final[str] = "user_preferences.db"
USER_DIRECTIVES_DB_NAME: Final[str] = "user_directives.db"

# Path helpers for all databases
get_project_db_path(project_root: str) -> str
get_user_preferences_db_path(project_root: str) -> str
get_user_directives_db_path(project_root: str) -> str
get_aifp_project_dir(project_root: str) -> str
database_exists(db_path: str) -> bool

# Connection management (moved from project/_common.py)
_open_connection(db_path: str) -> sqlite3.Connection
_close_connection(conn: sqlite3.Connection) -> None

# Generic Result types
@dataclass(frozen=True) Result
@dataclass(frozen=True) QueryResult
@dataclass(frozen=True) SchemaResult

# Schema introspection utilities
_get_table_names(conn) -> Tuple[str, ...]
_get_table_info(conn, table_name) -> Tuple[Dict, ...]
_get_table_sql(conn, table_name) -> Optional[str]
_parse_check_constraint(sql, field_name) -> Optional[Tuple[str, ...]]

# Row conversion utilities
row_to_dict(row) -> Dict[str, Any]
rows_to_tuple(rows) -> Tuple[Dict[str, Any], ...]

# JSON parsing utilities
parse_json_field(value) -> Optional[Any]
json_to_tuple(value) -> Tuple[Any, ...]
```

**Review Questions**:
1. ✅ **Path helpers**: Needed for all database categories - KEEP
2. ✅ **Connection management**: Used everywhere - KEEP
3. ✅ **Result types**: Generic types for all helpers - KEEP
4. ⚠️ **Schema introspection**: Used by core/schema.py - KEEP but verify needed elsewhere
5. ✅ **Row/JSON utilities**: Used across multiple helpers - KEEP

### Changes Made to `src/aifp/helpers/project/_common.py`

**Changed**:
- Removed `_open_connection()` definition (now imports from utils.py)
- Added import: `from ..utils import _open_connection`
- Updated docstring to show DRY hierarchy

**Review**: ✅ Good change - DRY principle, single source of truth

### New File: `src/aifp/helpers/core/_common.py`

**Contents**:
```python
# Imports from utils.py (re-exported for convenience)
_open_connection, get_core_db_path, get_return_statements, database_exists,
_get_table_names, _get_table_info, _get_table_sql, _parse_check_constraint,
row_to_dict, rows_to_tuple, parse_json_field, json_to_tuple

# Core-specific connection helper
_get_core_connection() -> sqlite3.Connection

# Immutable record types
@dataclass(frozen=True) DirectiveRecord
@dataclass(frozen=True) HelperRecord
@dataclass(frozen=True) FlowRecord
@dataclass(frozen=True) CategoryRecord
@dataclass(frozen=True) IntentKeywordRecord

# Row conversion functions
row_to_directive(row) -> DirectiveRecord
row_to_helper(row) -> HelperRecord
row_to_flow(row) -> FlowRecord
row_to_category(row) -> CategoryRecord
row_to_intent_keyword(row) -> IntentKeywordRecord
```

**Review Questions**:
1. ✅ **_get_core_connection()**: Convenience wrapper - KEEP
2. ✅ **Record types**: Immutable data structures for FP - KEEP
3. ✅ **Row conversion**: Type-safe conversions - KEEP

### DRY Hierarchy Summary

```
src/aifp/helpers/
├── utils.py                 # GLOBAL: Database-agnostic (all categories use)
│   ├── Path resolution for all 4 databases
│   ├── Connection management
│   ├── Schema introspection
│   └── Row/JSON utilities
│
├── project/
│   └── _common.py           # PROJECT: Entity checks, validation constants
│       └── imports from utils.py
│
├── core/
│   └── _common.py           # CORE: Record types, row converters
│       └── imports from utils.py
│
└── (future categories will follow same pattern)
```

**This hierarchy is sound** - each level adds category-specific utilities while reusing global ones.

---

## Summary of Issues to Address

1. **Refactor `core/flows.py`**: Remove complex condition-evaluation logic, replace with simple CRUD + targeted queries

2. **Remove cross-database queries**: Core helpers should only query aifp_core.db

3. **Update JSON**: Reflect new simpler helper set in `helpers-core.json`

4. **utils.py and _common.py**: Changes are valid, keep as-is

---

## Next Steps After Review

1. Review this document
2. Confirm approach for flow helpers
3. Refactor `core/flows.py`
4. Update `helpers-core.json`
5. Update implementation plan counts
6. Proceed to Git helpers

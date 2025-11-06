# Additional MCP Database Helpers (aifp_core.db)

**Purpose**: Comprehensive getter functions for efficient querying of aifp_core.db without SQL construction errors.

**Philosophy**: Prevent AI from wasting time/tokens/cache trying SQL queries with incorrect table/field names. Provide direct, typed access to all aifp_core.db data.

**Database**: `aifp_core.db` (read-only, immutable)

**Status**: 🔵 Proposed (Not Yet Implemented)

**MCP Tool Classification**: See [helper-tool-classification.md](./helper-tool-classification.md) for which helpers are exposed as MCP tools (`is_tool: true`) vs internal helpers (`is_tool: false`)

**Generic Tools**: 4 high-level orchestrator functions documented in [generic-tools-mcp.md](./generic-tools-mcp.md)

---

## Table of Contents

1. [Directive Getters](#directive-getters)
   - Core Directive Lookup (1 function)
   - Directive Field Getters (6 functions - efficient single-field access)
   - Hierarchy & Tree Navigation (6 functions)
   - Category-Based Directive Lookup (2 functions)
   - Advanced Directive Queries (3 functions)
2. [Category Getters](#category-getters) (3 functions)
3. [Helper Function Getters](#helper-function-getters)
   - Complete Helper Lookup (1 function)
   - Helper Field Getters (4 functions - efficient single-field access)
   - Module & Type Queries (4 functions)
   - Helper-Directive Relationships (2 functions)
   - Helper-Directive Execution Details (4 functions)
4. [Interaction Getters](#interaction-getters) (8 functions)
5. [Cross-Reference Getters](#cross-reference-getters) (3 functions)
6. [Schema Introspection](#schema-introspection) (3 functions)

---

## Directive Getters

### Core Directive Lookup

#### `get_directive_by_name(name: str)`
**Purpose**: Get specific directive by exact name match (complete entry).

**Parameters**:
- `name` (str): Directive name (e.g., "fp_purity", "project_init")

**Returns**:
```json
{
  "id": 1,
  "name": "fp_purity",
  "type": "fp",
  "level": null,
  "parent_directive": null,
  "description": "...",
  "workflow": {...},
  "md_file_path": "directives/fp_purity.md",
  "roadblocks_json": [...],
  "intent_keywords_json": ["pure", "purity", "side effects"],
  "confidence_threshold": 0.8
}
```

**Error Handling**: Return `{"found": false}` if directive doesn't exist.

**Used By**: Direct directive lookup, workflow execution

**Note**: For efficiency, consider field-specific getters below if you only need one field.

---

### Directive Field Getters (Efficient Single-Field Access)

**Use Case**: When AI needs to review specific fields from multiple directives without loading full entries repeatedly. Reduces context size and token usage.

#### `get_directive_description(name: str)`
**Purpose**: Get only the description field.

**Returns**: String description or `{"found": false}`

---

#### `get_directive_workflow(name: str)`
**Purpose**: Get only the workflow JSON.

**Returns**: Workflow dict (trunk, branches, error_handling) or `{"found": false}`

**Use Case**: When AI needs to execute workflow without other metadata

---

#### `get_directive_roadblocks(name: str)`
**Purpose**: Get only the roadblocks_json array.

**Returns**: List of roadblock objects or `{"found": false}`

**Use Case**: Error handling, debugging, understanding known issues

---

#### `get_directive_intent_keywords(name: str)`
**Purpose**: Get only the intent_keywords_json array.

**Returns**: List of keyword strings or `{"found": false}`

**Use Case**: Intent matching, search optimization

---

#### `get_directive_md_path(name: str)`
**Purpose**: Get only the MD file path.

**Returns**: String path (e.g., "directives/fp_purity.md") or `{"found": false}`

**Note**: Also included in `get_directive_by_name()`, but useful for quick lookups

---

#### `get_directives_by_type(type: str)`
**Purpose**: Get all directives of specific type.

**Parameters**:
- `type` (str): "fp", "project", "git", "user_system", "user_preference"

**Returns**: List of directive objects

**Example**:
```python
get_directives_by_type("fp")  # Returns all 66 FP directives
get_directives_by_type("git")  # Returns all 6 Git directives
```

---

#### `get_directives_by_level(level: int)`
**Purpose**: Get project directives by hierarchy level (0-4).

**Parameters**:
- `level` (int): 0 (root), 1 (coordination), 2 (operational), 3 (state), 4 (completion)

**Returns**: List of project directive objects at that level

**Notes**: Only applies to project directives (type="project")

---

#### `get_directives_by_parent(parent_name: str)`
**Purpose**: Get all child directives of a parent directive.

**Parameters**:
- `parent_name` (str): Parent directive name

**Returns**: List of directive objects with matching parent_directive

**Example**:
```python
get_directives_by_parent("aifp_run")
# Returns: [project_init, aifp_status, project_task_decomposition, ...]
# 10 children total
```

**Note**: 57 of 125 directives have parents defined (45%)

---

### Hierarchy & Tree Navigation

#### `get_directive_tree(parent_name: str, max_depth: int = None)`
**Purpose**: Get complete directive tree/hierarchy recursively from a parent.

**Parameters**:
- `parent_name` (str): Root parent directive
- `max_depth` (int, optional): Maximum depth to traverse (None = unlimited)

**Returns**:
```json
{
  "directive": "aifp_run",
  "depth": 0,
  "children": [
    {
      "directive": "user_directive_parse",
      "depth": 1,
      "children": [
        {
          "directive": "user_directive_validate",
          "depth": 2,
          "children": [
            {
              "directive": "user_directive_implement",
              "depth": 3,
              "children": [...]
            }
          ]
        }
      ]
    },
    {
      "directive": "project_init",
      "depth": 1,
      "children": [...]
    }
  ],
  "total_descendants": 57
}
```

**Example**:
```python
get_directive_tree("aifp_run")
# Returns full tree, up to 5 levels deep for user_directive flow

get_directive_tree("aifp_run", max_depth=2)
# Returns only 2 levels of children
```

**Use Case**: Documentation, workflow visualization, understanding directive flow

---

#### `get_directive_branch(directive_name: str)`
**Purpose**: Get linear branch from directive to root (ancestors path).

**Parameters**:
- `directive_name` (str): Starting directive

**Returns**:
```json
{
  "directive": "user_directive_monitor",
  "branch": [
    "user_directive_monitor",
    "user_directive_activate",
    "user_directive_approve",
    "user_directive_implement",
    "user_directive_validate",
    "user_directive_parse",
    "aifp_run"
  ],
  "depth": 6,
  "root": "aifp_run"
}
```

**Use Case**: Show "breadcrumb" path, understand directive context

---

#### `get_directive_siblings(directive_name: str)`
**Purpose**: Get all directives that share the same parent (siblings).

**Parameters**:
- `directive_name` (str): Directive to find siblings for

**Returns**:
```json
{
  "directive": "project_init",
  "parent": "aifp_run",
  "siblings": [
    "aifp_status",
    "aifp_help",
    "project_task_decomposition",
    "project_auto_resume",
    "user_preferences_sync",
    "user_directive_parse",
    "user_directive_update",
    "user_directive_deactivate",
    "user_directive_status"
  ],
  "sibling_count": 9
}
```

**Example**:
```python
get_directive_siblings("project_init")
# Returns 9 siblings (all children of aifp_run)

get_directive_siblings("aifp_run")
# Returns {"siblings": [], "sibling_count": 0} (root has no siblings)
```

**Note**: 12 parent directives have multiple children (sibling groups exist)

---

#### `get_directive_depth(directive_name: str)`
**Purpose**: Get depth level of directive in hierarchy (distance from root).

**Parameters**:
- `directive_name` (str): Directive name

**Returns**:
```json
{
  "directive": "user_directive_monitor",
  "depth": 6,
  "ancestors": ["user_directive_activate", "user_directive_approve", ..., "aifp_run"],
  "root": "aifp_run"
}
```

**Example**:
```python
get_directive_depth("aifp_run")          # depth: 0 (root)
get_directive_depth("project_init")      # depth: 1 (child of aifp_run)
get_directive_depth("user_directive_monitor")  # depth: 6 (deepest)
```

**Use Case**: Understanding hierarchy position, sorting by depth

---

#### `get_hierarchy_stats()`
**Purpose**: Get statistics about directive hierarchy structure.

**Returns**:
```json
{
  "total_directives": 125,
  "directives_with_parents": 57,
  "root_directives": 68,
  "max_depth": 6,
  "deepest_directive": "user_directive_monitor",
  "parents_with_children": 22,
  "parents_with_multiple_children": 12,
  "largest_sibling_group": {
    "parent": "aifp_run",
    "sibling_count": 10
  },
  "hierarchy_examples": [
    {
      "root": "aifp_run",
      "max_depth": 6,
      "total_descendants": 57
    }
  ]
}
```

**Use Case**: Documentation, understanding project structure

---

### Category-Based Directive Lookup

#### `get_directives_by_category(category_name: str)`
**Purpose**: Get all directives tagged with specific category.

**Parameters**:
- `category_name` (str): Category name (e.g., "purity", "immutability", "task_management")

**Returns**: List of directive objects

**Example**:
```python
get_directives_by_category("purity")
# Returns: fp_purity, fp_state_elimination, fp_side_effect_detection
```

---

#### `get_directive_categories(directive_name: str)`
**Purpose**: Get all categories assigned to a directive.

**Parameters**:
- `directive_name` (str): Directive name

**Returns**:
```json
{
  "directive": "fp_purity",
  "categories": [
    {"id": 1, "name": "purity", "description": "..."},
    {"id": 18, "name": "side_effects", "description": "..."}
  ]
}
```

---

### Advanced Directive Queries

#### `search_directives_by_intent(user_query: str, threshold: float = 0.5)`
**Purpose**: Search directives by intent keywords and description (fuzzy matching).

**Parameters**:
- `user_query` (str): User's natural language query
- `threshold` (float): Confidence threshold (0.0-1.0)

**Returns**:
```json
{
  "matches": [
    {
      "directive": {...},
      "confidence": 0.85,
      "matched_keywords": ["pure", "side effect"],
      "reason": "Intent keywords match"
    }
  ]
}
```

**Notes**: Uses `intent_keywords_json` field and description text matching

---

#### `get_directives_with_md_docs()`
**Purpose**: Get all directives that have MD documentation files.

**Returns**: List of directives with `md_file_path` not null

**Use Case**: Build help/documentation index

---

#### `get_root_directives()`
**Purpose**: Get all top-level directives (no parent).

**Returns**: List of directives where `parent_directive IS NULL`

**Example**: Returns `aifp_run`, `aifp_status`, `project_init`, etc.

---

## Category Getters

#### `get_all_categories()`
**Purpose**: Get all category definitions.

**Returns**: List of category objects (id, name, description)

**Count**: 39 categories

---

#### `get_category_by_name(name: str)`
**Purpose**: Get specific category details.

**Parameters**:
- `name` (str): Category name

**Returns**: Category object with id, name, description

---

#### `get_categories_by_type(directive_type: str)`
**Purpose**: Get all categories used by directives of specific type.

**Parameters**:
- `directive_type` (str): "fp", "project", "git", etc.

**Returns**: List of categories used by that type

**Example**:
```python
get_categories_by_type("fp")
# Returns: purity, immutability, composition, etc.
```

---

## Helper Function Getters

#### `get_helper_by_name(name: str)`
**Purpose**: Get specific helper function details (complete entry).

**Parameters**:
- `name` (str): Helper function name

**Returns**:
```json
{
  "id": 1,
  "name": "get_all_directives",
  "file_path": "src/aifp/helpers/mcp/tools/directive_getters.py",
  "parameters": null,
  "purpose": "...",
  "error_handling": "...",
  "is_tool": true,
  "is_sub_helper": false
}
```

**Note**: For efficiency, consider field-specific getters below if you only need one field.

---

### Helper Field Getters (Efficient Single-Field Access)

#### `get_helper_parameters(name: str)`
**Purpose**: Get only the parameters JSON for a helper.

**Returns**: Parameters array/null or `{"found": false}`

**Use Case**: Validation, documentation, dynamic invocation

---

#### `get_helper_purpose(name: str)`
**Purpose**: Get only the purpose description.

**Returns**: String purpose or `{"found": false}`

**Use Case**: Help text, tool selection

---

#### `get_helper_error_handling(name: str)`
**Purpose**: Get only the error_handling description.

**Returns**: String error handling strategy or `{"found": false}`

**Note**: ⚠️ **ERROR HANDLING REVIEW NEEDED** - Some helpers reference user_preferences.db for logging settings. Need to document this cross-database dependency.

**Example**:
```
"Prompt user; optionally log to user_preferences.db if helper_function_logging enabled"
```

**Action Required**: Create helper functions to check user_preferences tracking settings before logging.

---

#### `get_helper_file_path(name: str)`
**Purpose**: Get only the file path for a helper.

**Returns**: String file path or `{"found": false}`

**Use Case**: Source code navigation, imports

---

#### `get_helpers_by_module(module_path: str)`
**Purpose**: Get all helpers in specific module file.

**Parameters**:
- `module_path` (str): Module path (e.g., "src/aifp/helpers/mcp.py")

**Returns**: List of helper function objects

**Example**:
```python
get_helpers_by_module("src/aifp/helpers/git.py")
# Returns all 10 Git helpers
```

---

#### `get_mcp_tools()`
**Purpose**: Get all helpers exposed as MCP tools (is_tool=true).

**Returns**: List of helper function objects where `is_tool = 1`

**Count**: 10 MCP tools

---

#### `get_sub_helpers()`
**Purpose**: Get all internal sub-helpers (is_sub_helper=true).

**Returns**: List of helper function objects where `is_sub_helper = 1`

**Count**: 2 sub-helpers

---

#### `get_helpers_for_directive(directive_name: str)`
**Purpose**: Get all helper functions used by specific directive with execution metadata.

**Parameters**:
- `directive_name` (str): Directive name

**Returns**:
```json
{
  "directive": "project_init",
  "helper_count": 2,
  "helpers": [
    {
      "helper": {...},
      "execution_context": "create_project_structure",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": null,
      "description": "Creates .aifp-project/ directory structure"
    },
    {
      "helper": {...},
      "execution_context": "initialize_databases",
      "sequence_order": 2,
      "is_required": true,
      "parameters_mapping": {"aifp_dir": "project_root"},
      "description": "Initialize project.db and user_preferences.db"
    }
  ]
}
```

**Source**: `directive_helpers` junction table

---

### Helper-Directive Execution Details

**Use Case**: When executing directives, AI needs to know HOW to call helpers (sequence, parameters, conditional logic).

#### `get_helper_execution_details(directive_name: str, helper_name: str)`
**Purpose**: Get execution metadata for specific helper within directive context.

**Parameters**:
- `directive_name` (str): Directive using the helper
- `helper_name` (str): Helper function name

**Returns**:
```json
{
  "directive": "project_init",
  "helper": "initialize_project_db",
  "execution_context": "initialize_databases",
  "sequence_order": 2,
  "is_required": true,
  "parameters_mapping": {
    "aifp_dir": "project_root",
    "project_metadata": "workflow.metadata"
  },
  "description": "Initialize project.db with schema and metadata"
}
```

**Error Handling**: Return `{"found": false}` if mapping doesn't exist

**Use Case**: Directive workflow execution, parameter resolution

---

#### `get_helper_sequence_order(directive_name: str, helper_name: str)`
**Purpose**: Get just the sequence order for helper in directive.

**Returns**: Integer sequence order or `{"found": false}`

**Use Case**: Execution ordering, workflow visualization

---

#### `get_helper_is_required(directive_name: str, helper_name: str)`
**Purpose**: Check if helper is required (vs optional/conditional) in directive.

**Returns**: Boolean (true/false) or `{"found": false}`

**Use Case**: Conditional execution logic, error handling

---

#### `get_helper_parameters_mapping(directive_name: str, helper_name: str)`
**Purpose**: Get parameter mapping (directive params → helper params).

**Returns**: JSON object mapping or null or `{"found": false}`

**Example**:
```json
{
  "aifp_dir": "workflow.project_root",
  "project_metadata": "workflow.metadata"
}
```

**Use Case**: Dynamic parameter resolution during directive execution

---

#### `get_directives_using_helper(helper_name: str)`
**Purpose**: Get all directives that use specific helper function.

**Parameters**:
- `helper_name` (str): Helper function name

**Returns**: List of directives with execution context and sequence info

**Example**:
```python
get_directives_using_helper("get_project_status")
# Returns: aifp_run, aifp_status, project_init, etc.
```

---

## Interaction Getters

### Directive Relationships

#### `get_directive_triggers(directive_name: str)`
**Purpose**: Get directives that this directive triggers.

**Parameters**:
- `directive_name` (str): Source directive

**Returns**: List of target directives with relation_type="triggers"

**Example**:
```python
get_directive_triggers("project_file_write")
# Returns directives triggered by file write (fp_purity, fp_immutability, etc.)
```

---

#### `get_directive_dependencies(directive_name: str)`
**Purpose**: Get directives that this directive depends on.

**Parameters**:
- `directive_name` (str): Source directive

**Returns**: List of target directives with relation_type="depends_on"

---

#### `get_directive_escalations(directive_name: str)`
**Purpose**: Get directives this escalates to for resolution.

**Parameters**:
- `directive_name` (str): Source directive

**Returns**: List of target directives with relation_type="escalates_to"

---

#### `get_directive_cross_links(directive_name: str)`
**Purpose**: Get bidirectional/contextual connections.

**Parameters**:
- `directive_name` (str): Source directive

**Returns**: List of target directives with relation_type="cross_link"

---

#### `get_directive_fp_references(directive_name: str)`
**Purpose**: Get FP directives called/enforced by this directive.

**Parameters**:
- `directive_name` (str): Source directive (usually project directive)

**Returns**: List of FP directives with relation_type="fp_reference"

**Example**:
```python
get_directive_fp_references("project_file_write")
# Returns: fp_purity, fp_immutability, fp_side_effect_detection
```

---

#### `get_all_interactions_for_directive(directive_name: str)`
**Purpose**: Get complete interaction map (all relation types).

**Parameters**:
- `directive_name` (str): Directive name

**Returns**:
```json
{
  "directive": "project_file_write",
  "triggers": [...],
  "depends_on": [...],
  "escalates_to": [...],
  "cross_links": [...],
  "fp_references": [...]
}
```

**Notes**: Comprehensive view, same as existing `get_directive_interactions`

---

### Reverse Lookups

#### `get_directives_triggered_by(directive_name: str)`
**Purpose**: Find which directives trigger this directive.

**Parameters**:
- `directive_name` (str): Target directive

**Returns**: List of source directives that trigger this one

---

#### `get_directives_depending_on(directive_name: str)`
**Purpose**: Find which directives depend on this directive.

**Parameters**:
- `directive_name` (str): Target directive

**Returns**: List of source directives that depend on this one

---

## Cross-Reference Getters

### Workflow Analysis

#### `get_next_directive_in_workflow(current_directive: str)`
**Purpose**: Suggest next directive based on workflow patterns and interactions.

**Parameters**:
- `current_directive` (str): Current directive being executed

**Returns**:
```json
{
  "current": "project_init",
  "next_suggestions": [
    {
      "directive": "project_task_decomposition",
      "reason": "Triggered by project_init",
      "confidence": 0.9
    },
    {
      "directive": "project_themes_flows_init",
      "reason": "Common next step in initialization",
      "confidence": 0.8
    }
  ]
}
```

**Logic**:
- Check `triggers` relationships
- Check workflow sequences from common patterns
- Check level hierarchy (for project directives)

---

#### `get_related_directives(directive_name: str, depth: int = 1)`
**Purpose**: Get directives related through any interaction type.

**Parameters**:
- `directive_name` (str): Source directive
- `depth` (int): Relationship depth (1 = direct, 2 = 2 hops, etc.)

**Returns**: Graph of related directives with relationship paths

**Use Case**: Understanding directive ecosystem, planning workflows

---

### Completion Path Helpers

#### `get_directives_by_completion_stage(stage: str)`
**Purpose**: Get directives relevant to specific project completion stage.

**Parameters**:
- `stage` (str): "setup", "development", "testing", "finalization"

**Returns**: List of directives commonly used in that stage

**Notes**: Based on patterns, not explicit field (inferred from usage)

---

## Schema Introspection

#### `get_table_schema(table_name: str)`
**Purpose**: Get column information for specific table.

**Parameters**:
- `table_name` (str): Table name in aifp_core.db

**Returns**:
```json
{
  "table": "directives",
  "columns": [
    {"name": "id", "type": "INTEGER", "nullable": false, "primary_key": true},
    {"name": "name", "type": "TEXT", "nullable": false, "unique": true},
    ...
  ]
}
```

**Use Case**: Dynamic query building, validation

---

#### `get_all_table_names()`
**Purpose**: List all tables in aifp_core.db.

**Returns**: List of table names

**Example**: `["directives", "categories", "helper_functions", ...]`

---

#### `get_database_stats()`
**Purpose**: Get comprehensive database statistics.

**Returns**:
```json
{
  "schema_version": "1.5",
  "tables": {
    "directives": {"count": 125, "types": {"fp": 66, "project": 37, "git": 6, ...}},
    "helper_functions": {"count": 49, "mcp_tools": 10, "sub_helpers": 2},
    "categories": {"count": 39},
    "directive_categories": {"count": 116},
    "directives_interactions": {"count": 118},
    "directive_helpers": {"count": 62}
  },
  "last_updated": "2025-11-02"
}
```

**Use Case**: Status reporting, debugging, documentation

---

## Implementation Notes

### Module Organization

**Directory Structure**: Tools are separated from internal helpers using `tools/` subdirectories.

```
src/aifp/helpers/mcp/
├── tools/                          # is_tool=true (MCP-exposed)
│   ├── directive_getters.py       # ~15 directive lookup functions
│   ├── category_getters.py        # ~3 category functions
│   ├── helper_getters.py          # ~7 helper function queries
│   ├── interaction_getters.py     # ~8 relationship functions
│   └── schema_introspection.py    # ~3 schema/stats functions
└── internal/                       # is_tool=false (used by tools/directives)
    └── (future internal helpers)
```

**Current MCP tools**: 6 functions (in mcp.py, will move to mcp/tools/)
**Proposed MCP tools**: ~55 functions (from this document)
**Total MCP tools after additions**: ~61 tools

**Breakdown**:
- Directive Getters: 18 functions
  - Core: 1 function (get complete entry)
  - Field Getters: 6 functions (efficient single-field)
  - Hierarchy: 6 functions (tree, branch, siblings, depth, stats)
  - Category-Based: 2 functions
  - Advanced: 3 functions
- Category Getters: 3 functions
- Helper Function Getters: 15 functions
  - Complete Lookup: 1 function (get complete entry)
  - Field Getters: 4 functions (efficient single-field)
  - Module & Type: 4 functions (by module, MCP tools, sub-helpers, reverse lookup)
  - Relationships: 2 functions (helpers for directive, directives using helper)
  - Execution Details: 4 functions (context, sequence, required, params mapping)
- Interaction Getters: 8 functions
- Cross-Reference Getters: 3 functions
- Schema Introspection: 3 functions
- **Existing (to keep)**: 6 functions

### Naming Conventions

- **Single entity**: `get_directive_by_name()`, `get_category_by_name()`
- **Multiple entities**: `get_directives_by_type()`, `get_helpers_by_module()`
- **Relationships**: `get_directive_triggers()`, `get_directive_dependencies()`
- **Reverse lookups**: `get_directives_triggered_by()`, `get_directives_depending_on()`
- **Analysis**: `get_next_directive_in_workflow()`, `get_related_directives()`

### Return Types

All functions return:
- **Single entity**: Object dict or `{"found": false}`
- **Multiple entities**: List of dicts (empty list if none)
- **Relationships**: Dict with lists by relation type
- **Analysis**: Dict with suggestions/confidence scores

### Error Handling

- Never raise exceptions
- Return empty structures (`[]`, `{}`, `{"found": false}`)
- Log warnings for invalid parameters
- Include error context in return: `{"error": "...", "reason": "..."}`

### Performance Considerations

- **Caching**: Consider caching frequently accessed data (all directives, all categories)
- **Indexes**: Database has indexes on common join columns
- **Query optimization**: Use prepared statements, avoid N+1 queries

---

## Integration with Existing Helpers

### Existing MCP Helpers (Keep)

1. ✅ `get_all_directives()` - Keep (loads all directives + self-assessment)
2. ✅ `get_directive(name)` - **Replace with** `get_directive_by_name()`
3. ✅ `search_directives(keyword, category, type)` - Keep (general search)
4. ✅ `find_directive_by_intent(user_request, threshold)` - Keep (NLP matching)
5. ✅ `query_mcp_db(sql)` - Keep (advanced use only)
6. ✅ `get_directive_interactions(name)` - Keep (comprehensive view)
7. ✅ `get_directive_md_content(name)` - Keep (MD doc loading)

### Relationship to New Helpers

**Existing helpers** = Broad, flexible, general-purpose
**New helpers** = Specific, targeted, optimized for common queries

AI can use:
- **New helpers** for specific needs (fast, no SQL)
- **Existing helpers** for complex/flexible queries
- **`query_mcp_db()`** as last resort

---

## Priority Implementation Order

### Phase 1: Critical (Implement First)
**Core Access & Workflow Execution**
1. `get_directive_by_name()` - Most common lookup (complete entry)
2. `get_directive_workflow()` - Field getter for workflow execution
3. `get_directives_by_type()` - Filter by type
4. `get_directives_by_category()` - Category-based discovery
5. `get_directives_by_parent()` - Direct children lookup
6. `get_directive_tree()` - Full hierarchy visualization
7. `get_directive_siblings()` - Sibling navigation
8. `get_helpers_for_directive()` - Workflow execution helpers
9. `get_helper_execution_details()` - Helper invocation metadata
10. `get_directive_triggers()` - Relationship navigation

### Phase 2: Important (Next)
**Efficiency & Context Optimization**
11. `get_directive_description()` - Efficient field access
12. `get_directive_roadblocks()` - Error handling context
13. `get_directive_md_content()` - Load detailed documentation
14. `get_helper_parameters()` - Validation & invocation
15. `get_helper_purpose()` - Tool selection
16. `get_helper_sequence_order()` - Execution ordering
17. `get_helper_is_required()` - Conditional logic
18. `get_directive_branch()` - Ancestor path (breadcrumbs)
19. `get_directive_depth()` - Hierarchy position
20. `get_hierarchy_stats()` - Structure overview

### Phase 3: Advanced (Later)
**Advanced Queries & Optimization**
21. `get_directive_dependencies()` - Prerequisite checking
22. `get_mcp_tools()` - Tool introspection
23. `get_all_interactions_for_directive()` - Comprehensive view
24. `get_database_stats()` - Status reporting
25. `get_directive_intent_keywords()` - Intent matching optimization
26. `get_helper_error_handling()` - Cross-DB dependency handling
27. `get_helper_parameters_mapping()` - Dynamic parameter resolution
28. All reverse lookup functions
29. Completion stage helpers
30. Next directive suggestions
31. Advanced schema introspection helpers

---

## Critical Issues Identified

### 1. ⚠️ Cross-Database Dependency: Error Handling & Logging

**Issue**: Helper function `error_handling` field references `user_preferences.db` for logging decisions.

**Example** (from helpers_parsed.json):
```
"error_handling": "Prompt user; optionally log to user_preferences.db if helper_function_logging enabled"
```

**Problem**:
- `aifp_core.db` (read-only, MCP tools) references `user_preferences.db` (mutable, project-specific)
- Need cross-database queries or separate preference helpers
- AI needs to check tracking settings before logging

**Solution Needed**:
Create preference helper tools to check tracking settings:
- `get_tracking_setting(feature_name: str)` - Check if feature enabled
- `is_logging_enabled()` - Quick check for helper_function_logging
- These should be in `preferences/tools/` category (covered in next document)

**Action Items**:
1. Document in `additional-helpers-preferences.md`
2. Implement preference getters BEFORE Phase 1 MCP tools
3. Update helper `error_handling` implementations to use these getters

---

## Discussion Questions

1. **Should we combine some functions?** (e.g., single `get_directives()` with optional filters)
2. **Caching strategy?** Should AI cache results or always query fresh?
3. **Confidence scores?** Should relationship helpers include confidence/relevance scores?
4. **Async support?** Should these be async functions for performance?
5. **Batch operations?** Should we support `get_directives_by_names([...])` for bulk lookups?
6. **Field getter efficiency**: Are 6 directive field getters + 4 helper field getters excessive, or valuable for context optimization?

---

**Next Steps**:
1. Review and discuss this proposal
2. Create similar documents for:
   - `additional-helpers-project.md` (project.db getters/setters)
   - `additional-helpers-preferences.md` (user_preferences.db)
   - `additional-helpers-user-directives.md` (user_directives.db)
3. Implement priority Phase 1 helpers
4. Update `helpers_parsed.json` with new helpers
5. Re-run `sync-directives.py`

---

---

## Directory Organization Update

**Current Structure** (flat files):
```
src/aifp/helpers/
├── mcp.py              # 7 helpers (6 tools, 1 internal)
├── project.py          # 18 helpers (4 tools, 14 internal)
├── git.py              # 10 helpers (0 tools, 10 internal)
├── preferences.py      # 4 helpers (0 tools, 4 internal)
└── user_directives.py  # 10 helpers (0 tools, 10 internal)
```

**Proposed Structure** (tools/ subdirectories):
```
src/aifp/helpers/
├── mcp/
│   ├── tools/                      # is_tool=true
│   │   ├── directive_getters.py
│   │   ├── category_getters.py
│   │   ├── helper_getters.py
│   │   ├── interaction_getters.py
│   │   └── schema_introspection.py
│   └── internal.py                 # is_tool=false (if needed)
│
├── project/
│   ├── tools/                      # is_tool=true
│   │   ├── status_tools.py         # get_project_status, get_project_context, get_status_tree
│   │   └── query_tools.py          # query_project_db + new getters/setters
│   └── internal.py                 # is_tool=false (initialization, blueprints, etc.)
│
├── git/
│   ├── tools/                      # is_tool=true (future Git tools)
│   └── internal.py                 # is_tool=false (all current Git helpers)
│
├── preferences/
│   ├── tools/                      # is_tool=true (future preference tools)
│   └── internal.py                 # is_tool=false (all current preference helpers)
│
└── user_directives/
    ├── tools/                      # is_tool=true (future directive tools)
    └── internal.py                 # is_tool=false (all current user directive helpers)
```

**Benefits**:
1. **Clear API Boundary**: `tools/` = public MCP interface
2. **Easy MCP Registration**: Server scans `helpers/*/tools/*.py`
3. **Better Organization**: Related tools grouped by file
4. **Security**: Clear separation of callable vs internal functions
5. **Scalability**: Easy to add new tool categories

**File Path Updates Required**:
- Update `file_path` in `helpers_parsed.json` to reflect new structure
- Update MCP server to scan `tools/` subdirectories
- Update imports in directive implementations

---

**Status**: 🔵 Proposed - Awaiting Review
**Created**: 2025-11-02
**Author**: AIFP Development Team

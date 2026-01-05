# Settings Integration Implementation Specification

**Date**: 2026-01-04
**Status**: Design Specification (Updated with helper analysis)
**Purpose**: Document integration of settings into aifp_run with is_new_session parameter

---

## Decision: Use is_new_session Parameter ✅

### Rationale

**The key insight**: The `get_status` parameter in aifp_run is a **convenience bundling mechanism**, not the only way to access status. AI always has direct access to `aifp_status` helper.

**From aifp_run directive analysis**:
- `get_status=true` → Bundles aifp_status response with aifp_run response (startup convenience)
- `get_status=false` → Returns lightweight guidance only
- AI can ALWAYS call `aifp_status` directly mid-session (helpers always available)

**Therefore**: Using separate `get_status` and `get_settings` parameters solves a non-problem. The real need is: "Bundle everything useful at startup."

### With is_new_session (Clearer & Simpler)

```python
# New session - bundle everything AI needs to start
aifp_run(is_new_session=True)
# → Returns: guidance + status + settings + fp_directive_index

# Mid-session - lightweight entry point
aifp_run()  # or aifp_run(is_new_session=False)
# → Returns: guidance + common_starting_points

# AI needs status mid-session? Call helper directly
aifp_status()

# AI needs settings mid-session? Call helpers directly
get_user_setting(key)
get_user_settings()  # NEW - get all settings
load_directive_preferences(directive_name)
```

**Benefits**:
- ✅ **Semantic clarity**: "New session" means "give me everything to start"
- ✅ **Simpler**: 1 parameter instead of 2 (2 states instead of 4 combinations)
- ✅ **Less cognitive load**: AI asks "Is this new?" not "Do I need status? Settings? Both?"
- ✅ **Realistic**: Startup always needs both status AND settings
- ✅ **Helpers always available**: AI can query specific data mid-session via helpers

### When to use is_new_session=True

1. ✅ **First interaction** (actual new session, no context)
2. ✅ **After long interruption** (treat as new session, refresh everything)
3. That's it.

Everything else: `is_new_session=False` and call helpers directly when needed.

---

## FP Flow Integration Analysis

### Should aifp_run Load FP Directive Flows?

**FP Flow File Stats**:
- **Size**: 40KB (largest of the 3 flow files)
- **Lines**: 886 lines
- **Token estimate**: ~10,000-15,000 tokens
- **Flow count**: 48 reference consultation flows
- **Purpose**: Maps coding scenarios to FP directives ("handling nulls" → `fp_optionals`)

**From directive_flow_fp.json metadata** (lines 8-13):
```json
"key_principles": [
  "FP directives are reference documentation only",
  "AI writes FP-compliant code by default (no consultation needed for basics)",
  "Consultation happens inline when AI uncertain about implementation details",
  "NO loop-back to aifp_status (not workflow steps)"
]
```

### Analysis: FP Flow vs. FP Directive Index

**What FP flows provide**:
- Scenario-to-directive mapping ("handling errors" → `fp_result_types`)
- 48 consultation triggers with conditions
- Quick reference: "When doing X, consult directive Y"

**What AI already has**:
- System prompt with FP principles (pure functions, immutability, no OOP)
- Ability to search: `search_directives(type='fp', keyword='currying')`
- Ability to load: `get_directive_content('fp_currying')`

**Token cost analysis**:
- FP flow: 40KB = ~10-15k tokens
- Status data: ~2-5k tokens
- Settings data: ~500-1k tokens
- System prompt: Already substantial
- **Total new data at startup**: ~13-21k tokens with FP flow

### Recommendation: Lightweight FP Directive Index

**DON'T load full FP flow at startup** (reasons):
- ❌ 10-15k tokens is substantial (may approach context limits)
- ❌ Not all coding sessions need FP directive references
- ❌ System prompt already covers FP principles
- ❌ AI can search/query FP directives as needed
- ❌ FP flows are "reference consultation" patterns, not critical for every session

**INSTEAD: Load lightweight FP directive index** (benefits):
- ✅ Just directive names + categories (~1-2k tokens)
- ✅ Quick reference without full flow data
- ✅ AI knows which FP directives exist
- ✅ Can search by name without querying
- ✅ Full flows available via query if needed

**Example FP Directive Index**:
```json
{
  "fp_directives": {
    "error_handling": ["fp_optionals", "fp_result_types", "fp_try_monad", "fp_error_pipeline"],
    "purity": ["fp_purity", "fp_side_effect_detection", "fp_immutability"],
    "composition": ["fp_chaining", "fp_currying", "fp_monadic_composition"],
    "patterns": ["fp_lazy_evaluation", "fp_pattern_unpacking", "fp_map_reduce"],
    "optimization": ["fp_function_inlining", "fp_constant_folding", "fp_dead_code_elimination"],
    "language": ["fp_no_oop", "fp_no_reassignment", "fp_keyword_alignment"]
  }
}
```

**Full FP flows available via**:
```python
get_directive_flows(flow_category='fp')  # NEW general query helper
```

---

## Database Schema Enhancement: flow_category Field

### Problem

Currently, directive flows are stored in separate JSON files:
- `directive_flow_project.json`
- `directive_flow_fp.json`
- `directive_flow_user_preferences.json`

Once loaded into `directive_flow` table, there's **no way to distinguish flow categories**.

Additionally, `directive_flow_project.json` contains both **project** flows AND **git** flows. Without a category field, we can't distinguish them.

### Solution: Add flow_category Field

**Current schema** (aifp_core.sql line 82):
```sql
CREATE TABLE IF NOT EXISTS directive_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_directive TEXT NOT NULL,
    to_directive TEXT NOT NULL,
    flow_type TEXT CHECK (flow_type IN (
        'status_branch', 'completion_loop', 'conditional', 'error'
    )) NOT NULL DEFAULT 'conditional',
    condition_key TEXT,
    condition_value TEXT,
    condition_description TEXT,
    priority INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (from_directive) REFERENCES directives(name),
    FOREIGN KEY (to_directive) REFERENCES directives(name)
);
```

**Proposed schema** (add flow_category):
```sql
CREATE TABLE IF NOT EXISTS directive_flow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_directive TEXT NOT NULL,
    to_directive TEXT NOT NULL,

    -- NEW FIELD
    flow_category TEXT CHECK (flow_category IN (
        'project',           -- Project management workflows
        'fp',                -- FP reference consultation patterns
        'user_preferences',  -- User settings and preferences
        'git'                -- Git collaboration workflows
    )) NOT NULL DEFAULT 'project',

    flow_type TEXT CHECK (flow_type IN (
        'status_branch', 'completion_loop', 'conditional', 'error'
    )) NOT NULL DEFAULT 'conditional',

    condition_key TEXT,
    condition_value TEXT,
    condition_description TEXT,
    priority INTEGER DEFAULT 0,
    description TEXT,

    FOREIGN KEY (from_directive) REFERENCES directives(name),
    FOREIGN KEY (to_directive) REFERENCES directives(name)
);

-- Add index for flow_category queries
CREATE INDEX IF NOT EXISTS idx_directive_flow_category ON directive_flow(flow_category);
```

**Enables queries like**:
```sql
-- Get all FP consultation flows
SELECT * FROM directive_flow WHERE flow_category='fp';

-- Get all project management flows
SELECT * FROM directive_flow WHERE flow_category='project';

-- Get all git flows
SELECT * FROM directive_flow WHERE flow_category='git';

-- Get conditional FP flows
SELECT * FROM directive_flow WHERE flow_category='fp' AND flow_type='conditional';
```

---

## Existing Directive Flow Helpers Analysis

**Current helpers in helpers-core.json** (all navigation-focused):

1. **get_next_directives_from_status(from_directive, status_object)**
   - Purpose: Get next directives from status with condition evaluation
   - Use: Workflow navigation

2. **get_matching_next_directives(from_directive, status_object)**
   - Purpose: Get only directives whose conditions match current state
   - Use: Filtered workflow navigation

3. **get_completion_loop_target(from_directive)**
   - Purpose: Get where to loop back after completing directive
   - Use: Post-completion navigation

4. **get_conditional_work_paths(from_directive, work_context)**
   - Purpose: Query directive_flow for flow_type='conditional'
   - Use: Context-based routing

**Key observation**: All existing helpers are specialized for **workflow navigation** ("what comes next?"). None are general-purpose **query helpers** for browsing flows by category.

**Decision**: Don't modify existing navigation helpers. Add new general query helper.

---

## New Helpers Required

### 1. get_user_settings() - Settings Helper

**Add to helpers-settings.json**:

```json
{
  "name": "get_user_settings",
  "file_path": "helpers/settings/settings.py",
  "parameters": [],
  "purpose": "Get all user settings (complements get_user_setting which gets one)",
  "error_handling": "Returns empty array if no settings exist",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [],
  "target_database": "user_preferences",
  "implementation_notes": [
    "Returns: Array of {setting_key, setting_value, description, scope}",
    "Queries: SELECT * FROM user_settings",
    "Complements singular get_user_setting(key)"
  ],
  "used_by_directives": [
    {
      "directive_name": "aifp_run",
      "execution_context": "new_session_startup",
      "sequence_order": 2,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Called by aifp_run when is_new_session=true - returns all user settings for session cache"
    }
  ]
}
```

**Complements existing**:
- `get_user_setting(key)` - singular
- `get_user_settings()` - plural (NEW)

---

### 2. get_fp_directive_index() - Core Helper

**Add to helpers-core.json**:

```json
{
  "name": "get_fp_directive_index",
  "file_path": "helpers/core/module.py",
  "parameters": [],
  "purpose": "Get lightweight FP directive index grouped by category (names only, not full definitions)",
  "error_handling": "Returns empty object if no FP directives found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [],
  "target_database": "core",
  "implementation_notes": [
    "Returns: {category_name: [directive_name, ...]}",
    "Example: {'error_handling': ['fp_optionals', 'fp_result_types'], 'purity': ['fp_purity', 'fp_immutability']}",
    "Query: SELECT d.name, c.name as category FROM directives d JOIN directive_categories dc ON d.id=dc.directive_id JOIN categories c ON dc.category_id=c.id WHERE d.type='fp' ORDER BY c.name, d.name",
    "Groups by category name",
    "Lightweight: ~1-2k tokens vs ~10-15k for full FP flows",
    "Does NOT return full directive definitions or flows"
  ],
  "used_by_directives": [
    {
      "directive_name": "aifp_run",
      "execution_context": "new_session_startup",
      "sequence_order": 3,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Called by aifp_run when is_new_session=true - provides FP directive quick reference grouped by category"
    }
  ]
}
```

**Implementation**:
```python
def get_fp_directive_index():
    """Get lightweight FP directive index grouped by category"""

    fp_directives = query_core_db(
        "SELECT d.name, c.name as category "
        "FROM directives d "
        "JOIN directive_categories dc ON d.id = dc.directive_id "
        "JOIN categories c ON dc.category_id = c.id "
        "WHERE d.type = 'fp' "
        "ORDER BY c.name, d.name"
    )

    # Group by category
    index = {}
    for directive in fp_directives:
        category = directive["category"]
        if category not in index:
            index[category] = []
        index[category].append(directive["name"])

    return index
```

---

### 3. get_all_directive_names() - Core Helper

**Add to helpers-core.json**:

```json
{
  "name": "get_all_directive_names",
  "file_path": "helpers/core/module.py",
  "parameters": [
    {
      "name": "types",
      "type": "array",
      "required": false,
      "default": null,
      "description": "Optional array of directive types to filter: ['fp', 'project', 'git', 'user_preferences', 'user_system']. If not provided, returns ALL directive names."
    }
  ],
  "purpose": "Get list of all directive names (or filtered by types). Returns names only, NOT full directive data.",
  "error_handling": "Returns empty array if no directives found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [],
  "target_database": "core",
  "implementation_notes": [
    "Returns: Array of directive names ['aifp_run', 'aifp_status', 'project_init', 'fp_purity', ...]",
    "If types provided: Filters to only those types",
    "If types=null: Returns ALL directive names",
    "Query: SELECT name FROM directives WHERE type IN (types) ORDER BY type, name",
    "Lightweight: ~1k tokens for all names vs ~100k+ for all full data",
    "AI caches these names, queries get_directive(name) when needs details"
  ],
  "used_by_directives": [
    {
      "directive_name": "aifp_run",
      "execution_context": "new_session_startup",
      "sequence_order": 4,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Called by aifp_run when is_new_session=true - provides complete list of ALL directive names for AI to cache"
    }
  ]
}
```

**Implementation**:
```python
def get_all_directive_names(types: list[str] = None):
    """Get all directive names, optionally filtered by types"""

    if types is None:
        # Get all directive names
        query = "SELECT name FROM directives ORDER BY type, name"
        params = []
    else:
        # Filter by types
        placeholders = ','.join('?' * len(types))
        query = f"SELECT name FROM directives WHERE type IN ({placeholders}) ORDER BY type, name"
        params = types

    directives = query_core_db(query, params)
    return [d["name"] for d in directives]
```

**Usage examples**:
```python
# Get all directive names
all_names = get_all_directive_names()
# → ['aifp_run', 'aifp_status', 'project_init', 'fp_purity', ...]

# Get only project and FP directive names
proj_fp_names = get_all_directive_names(types=['project', 'fp'])
# → ['aifp_run', 'project_init', 'fp_purity', 'fp_immutability', ...]

# Get only git directive names
git_names = get_all_directive_names(types=['git'])
# → ['git_init', 'git_create_branch', 'git_merge_branch', ...]
```

---

### 4. get_directive_flows() - Core Helper (General Query)

**Add to helpers-core.json**:

```json
{
  "name": "get_directive_flows",
  "file_path": "helpers/core/module.py",
  "parameters": [
    {
      "name": "flow_category",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Filter by category: 'project', 'fp', 'user_preferences', 'git'"
    },
    {
      "name": "flow_type",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Filter by type: 'status_branch', 'completion_loop', 'conditional', 'error'"
    },
    {
      "name": "from_directive",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Filter by source directive name"
    },
    {
      "name": "to_directive",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Filter by target directive name"
    }
  ],
  "purpose": "General-purpose query for directive flows by category, type, or directive names. Complements navigation helpers (get_next_directives_from_status, etc.) which are specialized for workflow routing.",
  "error_handling": "Returns empty array if no flows match filters",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [],
  "target_database": "core",
  "implementation_notes": [
    "Returns: Array of flow objects with all fields",
    "All parameters are optional - can combine filters",
    "Example: get_directive_flows(flow_category='fp') returns all FP consultation flows",
    "Example: get_directive_flows(flow_category='git', flow_type='conditional') returns git conditional flows",
    "Complements existing navigation helpers which are workflow-focused",
    "Use for: Browsing flows by category, analyzing flow structure, debugging"
  ],
  "used_by_directives": []
}
```

**Implementation**:
```python
def get_directive_flows(
    flow_category: str = None,
    flow_type: str = None,
    from_directive: str = None,
    to_directive: str = None
):
    """General-purpose query for directive flows"""

    query = "SELECT * FROM directive_flow WHERE 1=1"
    params = []

    if flow_category:
        query += " AND flow_category=?"
        params.append(flow_category)

    if flow_type:
        query += " AND flow_type=?"
        params.append(flow_type)

    if from_directive:
        query += " AND from_directive=?"
        params.append(from_directive)

    if to_directive:
        query += " AND to_directive=?"
        params.append(to_directive)

    return query_core_db(query, params)
```

**Use cases**:
```python
# Get all FP flows
get_directive_flows(flow_category='fp')

# Get all git flows
get_directive_flows(flow_category='git')

# Get all conditional flows across all categories
get_directive_flows(flow_type='conditional')

# Get FP conditional flows
get_directive_flows(flow_category='fp', flow_type='conditional')

# Get flows from specific directive
get_directive_flows(from_directive='project_file_write')
```

**Relationship to existing helpers**:
- Existing helpers: **Workflow navigation** ("what's next?")
- New helper: **General querying** ("show me flows by category")
- Complementary, not overlapping

---

## Source JSON File Updates Required

### Add flow_category to All Flow Objects

**Each of the 3 directive flow JSON files needs flow_category added to every flow**:

#### directive_flow_project.json

For **project management flows**:
```json
{
  "id": 1,
  "from_directive": "aifp_run",
  "to_directive": "aifp_status",
  "flow_category": "project",  // ← ADD THIS
  "flow_type": "status_branch",
  ...
}
```

For **git flows** (in same file):
```json
{
  "id": 5,
  "from_directive": "aifp_status",
  "to_directive": "git_detect_external_changes",
  "flow_category": "git",  // ← ADD THIS (not 'project')
  "flow_type": "canonical",
  ...
}
```

**Rule**: Flows involving git directives get `"flow_category": "git"`, all others get `"flow_category": "project"`.

#### directive_flow_fp.json

All flows get `"flow_category": "fp"`:
```json
{
  "id": 1,
  "from_context": "code_writing",
  "to_directive": "fp_optionals",
  "flow_category": "fp",  // ← ADD THIS
  "flow_type": "reference_consultation",
  ...
}
```

#### directive_flow_user_preferences.json

All flows get `"flow_category": "user_preferences"`:
```json
{
  "id": 1,
  "from_directive": "aifp_run",
  "to_directive": "user_preferences_sync",
  "flow_category": "user_preferences",  // ← ADD THIS
  "flow_type": "conditional",
  ...
}
```

**Data loading script update**:
```python
def load_directive_flows():
    """Load flows from JSON with flow_category preserved"""

    # Load each JSON file
    for json_file in ['directive_flow_project.json', 'directive_flow_fp.json', 'directive_flow_user_preferences.json']:
        with open(json_file) as f:
            data = json.load(f)
            flows = data['flows']

            for flow in flows:
                # flow_category should already be in JSON
                assert 'flow_category' in flow, f"Missing flow_category in {json_file}"

                insert_flow(
                    from_directive=flow['from_directive'],
                    to_directive=flow['to_directive'],
                    flow_category=flow['flow_category'],  # ← Use from JSON
                    flow_type=flow['flow_type'],
                    condition_key=flow.get('condition_key'),
                    condition_value=flow.get('condition_value'),
                    condition_description=flow.get('condition_description'),
                    priority=flow.get('priority', 0),
                    description=flow.get('description')
                )
```

---

## Implementation Specification

### 1. aifp_run Enhancement

#### Parameter Change
```json
{
  "name": "aifp_run",
  "parameters": [
    {
      "name": "is_new_session",
      "type": "boolean",
      "required": false,
      "default": false,
      "description": "Whether this is a new session. If true, bundles comprehensive startup data: status + settings + fp_directive_index. If false (default), returns lightweight guidance. Use true for: (1) first interaction of session (no cached context), (2) after long interruption (treat as fresh start). Gateway and reminder system - does NOT parse user input."
    }
  ]
}
```

#### Return Structure

**When is_new_session=false (default)**:
```json
{
  "success": true,
  "message": "AIFP MCP available (continuation mode)",
  "common_starting_points": [
    "aifp_status - Get comprehensive project state",
    "project_init - Initialize new AIFP project",
    "project_file_write - Write code and update database",
    "project_task_create - Create new tasks",
    "project_task_complete - Mark task as complete"
  ],
  "guidance": {
    "directive_access": "Directive names cached from is_new_session bundle. Call get_directive(name) or search_directives() for details.",
    "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
    "assumption": "Always assume AIFP applies unless user explicitly rejects it.",
    "when_to_refresh": "Call aifp_run(is_new_session=true) for first interaction or after long break.",
    "available_helpers": ["aifp_status", "get_user_setting", "get_user_settings", "load_directive_preferences", ...]
  }
}
```

**When is_new_session=true**:
```json
{
  "success": true,
  "message": "AIFP MCP available - New session data loaded",
  "guidance": {...},

  "status": {
    "project": {...},
    "current_task": {...},
    "next_actions": [...],
    "note": "Status cached. Call aifp_status() directly for mid-session updates."
  },

  "settings": {
    "user_settings": [
      {"key": "fp_strictness_level", "value": "{\"level\": \"standard\"}"},
      {"key": "prefer_explicit_returns", "value": "true"},
      {"key": "suppress_warnings", "value": "[]"}
    ],
    "tracking_features": [
      {"name": "fp_flow_tracking", "enabled": false},
      {"name": "ai_interaction_log", "enabled": false},
      {"name": "helper_function_logging", "enabled": false},
      {"name": "issue_reports", "enabled": false}
    ],
    "note": "Settings cached. Call get_user_setting(key), get_user_settings(), or load_directive_preferences(directive_name) for specific queries."
  },

  "all_directive_names": [
    "aifp_run",
    "aifp_status",
    "project_init",
    "project_file_write",
    "fp_purity",
    "fp_immutability",
    "git_init",
    "user_directive_parse"
  ],

  "fp_directive_index": {
    "error_handling": ["fp_optionals", "fp_result_types", "fp_try_monad", "fp_error_pipeline"],
    "purity": ["fp_purity", "fp_side_effect_detection", "fp_immutability"],
    "composition": ["fp_chaining", "fp_currying", "fp_monadic_composition"],
    "patterns": ["fp_lazy_evaluation", "fp_pattern_unpacking", "fp_map_reduce"],
    "optimization": ["fp_function_inlining", "fp_constant_folding", "fp_dead_code_elimination"],
    "language": ["fp_no_oop", "fp_no_reassignment", "fp_keyword_alignment"],
    "note": "Quick reference index. Call search_directives(type='fp', keyword=...) or get_directive_content(name) for full details. Full FP flows: get_directive_flows(flow_category='fp')"
  }
}
```

#### Implementation Pseudo-code

```python
def aifp_run(is_new_session: bool = False):
    """Main entry point for AIFP system - gateway and reminder system"""

    result = {
        "success": True,
        "message": "AIFP MCP available"
    }

    if is_new_session:
        # Bundle all startup data
        result["message"] += " - New session data loaded"

        # 1. Get comprehensive status
        result["status"] = aifp_status()
        result["status"]["note"] = "Status cached. Call aifp_status() directly for mid-session updates."

        # 2. Get all user settings (using NEW plural helper)
        result["settings"] = {
            "user_settings": get_user_settings(),  # NEW helper
            "tracking_features": query_settings_db(
                "SELECT feature_name, enabled, description, estimated_token_overhead "
                "FROM tracking_settings"
            ),
            "note": "Settings cached. Call get_user_setting(key), get_user_settings(), or load_directive_preferences(directive_name) for specific queries."
        }

        # 3. Get all directive names (using NEW helper)
        result["all_directive_names"] = get_all_directive_names()  # NEW helper

        # 4. Get FP directive index (using NEW helper)
        result["fp_directive_index"] = get_fp_directive_index()  # NEW helper
        result["fp_directive_index"]["note"] = "Quick reference index. Call search_directives(type='fp', keyword=...) or get_directive_content(name) for full details. Full FP flows: get_directive_flows(flow_category='fp')"

    else:
        # Lightweight guidance for continuation
        result["message"] += " (continuation mode)"
        result["common_starting_points"] = [
            "aifp_status - Get comprehensive project state",
            "project_init - Initialize new AIFP project",
            "project_file_write - Write code and update database",
            "project_task_create - Create new tasks",
            "project_task_complete - Mark task as complete"
        ]
        result["guidance"] = {
            "directive_access": "Directive names cached from is_new_session bundle. Call get_directive(name) or search_directives() for details.",
            "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
            "assumption": "Always assume AIFP applies unless user explicitly rejects it.",
            "when_to_refresh": "Call aifp_run(is_new_session=true) for first interaction or after long break.",
            "available_helpers": [
                "aifp_status",
                "get_user_setting",
                "get_user_settings",
                "load_directive_preferences",
                "search_directives",
                "get_directive_content"
            ]
        }

    return result
```

---

### 2. Database Schema Changes

#### Add flow_category to directive_flow Table

**Migration SQL**:
```sql
-- Add flow_category column
ALTER TABLE directive_flow ADD COLUMN flow_category TEXT
    CHECK (flow_category IN ('project', 'fp', 'user_preferences', 'git'))
    NOT NULL DEFAULT 'project';

-- Create index for flow_category queries
CREATE INDEX IF NOT EXISTS idx_directive_flow_category ON directive_flow(flow_category);

-- Update existing records (if applicable)
-- This would be done during data migration when loading from JSON files
```

---

### 4. System Prompt Updates

**Replace existing get_status guidance with**:

```markdown
### Session Management: is_new_session Parameter

**aifp_run has an is_new_session parameter for startup data bundling**:

**When is_new_session=true** (bundle everything for startup):
1. ✅ First interaction (new session, no cached context)
2. ✅ After long interruption (treat as new session, refresh everything)

**When is_new_session=false (default)** (lightweight entry point):
1. ✅ Continuation work (you have cached data)
2. ✅ Simple queries (help requests, FP references)
3. ✅ Mid-session work (call specific helpers as needed)

**What is_new_session=true returns**:
- **Guidance**: Common starting points and helper references
- **Status**: Comprehensive project state from aifp_status()
- **Settings**: All user_settings + tracking_features
- **All Directive Names**: Complete list of ALL directive names (all types)
- **FP Directive Index**: FP directive names grouped by category

**Mid-session data access** (helpers always available):
```python
# Get status update
aifp_status()

# Get specific setting
get_user_setting('fp_strictness_level')

# Get all settings
get_user_settings()

# Get directive preferences
load_directive_preferences('project_file_write')

# Search FP directives
search_directives(type='fp', keyword='currying')

# Get FP directive details
get_directive_content('fp_currying')

# Get FP flows (general query)
get_directive_flows(flow_category='fp')

# Get FP directive index
get_fp_directive_index()

# Get all directive names (or filtered)
get_all_directive_names()
get_all_directive_names(types=['project', 'fp'])
```

**Examples**:

```python
# First interaction - bundle everything
aifp_run(is_new_session=True)

# Mid-session work - lightweight
aifp_run()  # or aifp_run(is_new_session=False)

# Need status update mid-session? Call helper directly
status = aifp_status()

# Need all settings? Call helper directly
settings = get_user_settings()

# Need FP flows? Call helper directly
fp_flows = get_directive_flows(flow_category='fp')
```

**Remember**: Helpers are ALWAYS available. The parameter only controls bundling at entry point.
```

---

### 5. Implementation Checklist

#### Phase 1: Database Schema (Week 1)
- [ ] Add `flow_category` field to directive_flow table (aifp_core.sql)
- [ ] Create index on flow_category
- [ ] Update aifp_core.sql schema file
- [ ] Create migration SQL script
- [ ] Test: Schema update successful

#### Phase 2: Source JSON Updates (Week 1)
- [ ] Add flow_category to all flows in directive_flow_project.json
  - [ ] Mark project flows as "project"
  - [ ] Mark git flows as "git"
- [ ] Add flow_category to all flows in directive_flow_fp.json ("fp")
- [ ] Add flow_category to all flows in directive_flow_user_preferences.json ("user_preferences")
- [ ] Update flow loading scripts to read flow_category from JSON
- [ ] Test: All flows load correctly with categories

#### Phase 3: New Helpers Implementation (Week 2)
- [ ] Add get_user_settings() to helpers-settings.json
- [ ] Implement get_user_settings() function
- [ ] Test: get_user_settings() returns all settings
- [ ] Add get_fp_directive_index() to helpers-core.json
- [ ] Implement get_fp_directive_index() function
- [ ] Test: Index contains all FP directives grouped by category
- [ ] Add get_all_directive_names() to helpers-core.json
- [ ] Implement get_all_directive_names() function
- [ ] Test: Returns all directive names (or filtered by types array)
- [ ] Add get_directive_flows() to helpers-core.json
- [ ] Implement get_directive_flows() function
- [ ] Test: Can query flows by category, type, from/to directives

#### Phase 4: aifp_run Enhancement (Week 2)
- [ ] Replace `get_status` parameter with `is_new_session` in helpers-orchestrators.json
- [ ] Update aifp_run directive JSON (directives-project.json)
- [ ] Update workflow branches for is_new_session
- [ ] Implement aifp_run with new helpers (calls get_all_directive_names())
- [ ] Test: is_new_session=True returns status + settings + fp_index + all_directive_names
- [ ] Test: is_new_session=False returns lightweight guidance
- [ ] Test: Token count reasonable (~15-20k total)

#### Phase 5: Documentation (Week 3)
- [x] Update system prompt with is_new_session guidance
- [x] Document when to use is_new_session=true/false
- [x] Document new helpers (get_user_settings, get_fp_directive_index, get_all_directive_names, get_directive_flows)
- [x] Document FP directive index structure
- [x] Document all_directive_names structure
- [x] Clarify FP baseline vs FP directive consultation
- [x] Update aifp_run.md with correct behavior
- [ ] Update settings-specification.json
- [ ] Create user guide

#### Phase 6: Testing (Week 3)
- [ ] Test new session: aifp_run(is_new_session=True)
- [ ] Test continuation: aifp_run(is_new_session=False)
- [ ] Test FP directive index format
- [ ] Test settings bundling complete
- [ ] Test status bundling complete
- [ ] Test mid-session helper calls
- [ ] Test flow_category queries work
- [ ] Test get_directive_flows() with various filters
- [ ] Verify token counts acceptable

---

## Summary

### Decisions Made

1. ✅ **Use is_new_session parameter** (not separate get_status + get_settings)
   - Clearer semantics: "new session" = "bundle everything"
   - Simpler: 1 parameter instead of 2
   - Realistic: Startup always needs both status and settings

2. ✅ **Add flow_category field to directive_flow table**
   - Essential for querying flows by type (fp/project/user_preferences/git)
   - Enables: `get_directive_flows(flow_category='fp')`
   - Must be added to ALL flow objects in source JSON files

3. ✅ **Add flow_category to source JSON files explicitly**
   - Not inferred from filename
   - Git flows in project file marked as 'git' (not 'project')
   - Self-documenting and accurate

4. ✅ **Load lightweight FP directive index at startup** (not full flows)
   - Just names + categories (~1-2k tokens)
   - Full FP flows available via get_directive_flows()
   - Avoids 10-15k token overhead

5. ✅ **Add 4 new helpers**
   - `get_user_settings()` - Get all user settings (plural helper)
   - `get_fp_directive_index()` - FP directives grouped by category
   - `get_all_directive_names(types=[])` - All directive names (optionally filtered by types array)
   - `get_directive_flows()` - General query for flows by category/type

6. ✅ **Don't modify existing navigation helpers**
   - Existing helpers are workflow-focused (what's next?)
   - New helper is query-focused (show me flows by category)
   - Complementary, not overlapping

### Key Benefits

- **Startup efficiency**: One call bundles everything needed
- **Mid-session flexibility**: Call specific helpers as needed
- **Token management**: Lightweight by default, detailed on demand
- **Queryable flows**: flow_category enables targeted flow queries
- **FP reference support**: Index provides quick lookup without full flow overhead
- **Clean helper architecture**: New query helper doesn't interfere with navigation helpers

### Next Steps

1. Implement Phase 1 (database schema enhancement)
2. Implement Phase 2 (add flow_category to source JSON files)
3. Implement Phase 3 (new helpers)
4. Implement Phase 4 (aifp_run with is_new_session)
5. Update documentation and test

---

**Document Status**: ✅ Complete (Updated with helper analysis)
**Last Updated**: 2026-01-04
**Implementation**: Ready to begin Phase 1

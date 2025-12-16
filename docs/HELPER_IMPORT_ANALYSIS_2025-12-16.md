# Helper Functions Database Import Strategy

**Date**: 2025-12-16
**Status**: Pre-Import Mapping Phase
**Approach**: Complete JSON preparation before import

---

## Strategy: Complete Pre-Import Mapping

### Overview

All helper functions and directive mappings will be converted to JSON format with complete database fields BEFORE any import occurs. This ensures:
- ✅ Complete data validation before database creation
- ✅ Easy review and correction of mappings
- ✅ Single comprehensive import script
- ✅ Clean separation of data preparation vs. import logic

---

## Current State

### Existing Files (Markdown)
**Location**: `docs/helpers/consolidated/`

1. **helpers-consolidated-core.md** (33 helpers)
2. **helpers-consolidated-git.md** (11 helpers)
3. **helpers-consolidated-orchestrators.md** (24 helpers)
4. **helpers-consolidated-project.md** (125 helpers)
5. **helpers-consolidated-settings.md** (17 helpers)
6. **helpers-consolidated-user-custom.md** (16 helpers)
7. **helpers-consolidated-index.md** (index only)

**Total**: ~227 helper functions documented

### What's Missing from Markdown
- ❌ `used_by_directive` field (critical for directive_helpers table)
- ⚠️ `file_path` (where helper lives in MCP server code)
- ⚠️ Structured `error_handling` (some have prose, need standardization)
- ⚠️ Structured `return_statements` (some have notes, need JSON array format)

---

## Target JSON Structure

### File Organization

Create JSON files mirroring the markdown structure:

```
docs/helpers/json/
├── helpers-core.json              (33 helpers)
├── helpers-git.json               (11 helpers)
├── helpers-orchestrators.json     (24 helpers)
├── helpers-project.json           (125 helpers)
├── helpers-settings.json          (17 helpers)
├── helpers-user-custom.json       (16 helpers)
└── directive-helpers-mapping.json (all directive-helper relationships)
```

### Individual Helper JSON Format

**Schema alignment** with `helper_functions` table:

```json
{
  "name": "get_directive_by_name",
  "file_path": "helpers/core/directive_tools.py",
  "parameters": [
    {
      "name": "directive_name",
      "type": "string",
      "required": true,
      "description": "Name of directive to retrieve"
    }
  ],
  "purpose": "Get specific directive by name (high-frequency operation)",
  "error_handling": "Returns null if directive not found. No exceptions raised.",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Check result for null before accessing fields",
    "Directive object includes all metadata and workflow"
  ],
  "target_database": "core",
  "used_by_directives": [
    {
      "directive_name": "aifp_help",
      "execution_context": "lookup_directive",
      "sequence_order": 1,
      "is_required": true,
      "description": "Retrieves directive for detailed help display"
    },
    {
      "directive_name": "user_preferences_update",
      "execution_context": "intent_matching",
      "sequence_order": 2,
      "is_required": false,
      "description": "Used when updating directive-related preferences"
    }
  ]
}
```

### Directive-Helper Mapping JSON Format

**Separate file**: `directive-helpers-mapping.json`

Maps to `directive_helpers` junction table:

```json
{
  "mappings": [
    {
      "directive_name": "aifp_run",
      "helper_name": "get_all_directives",
      "execution_context": "initial_directive_load",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Loads all 125 directives into context for session"
    },
    {
      "directive_name": "aifp_run",
      "helper_name": "find_directive_by_intent",
      "execution_context": "intent_matching",
      "sequence_order": 2,
      "is_required": false,
      "parameters_mapping": {
        "user_request": "workflow.user_input",
        "threshold": 0.7
      },
      "description": "Matches user intent to directive when request is ambiguous"
    }
  ]
}
```

---

## Database Schema Reference

### helper_functions Table
```sql
CREATE TABLE IF NOT EXISTS helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,              -- From JSON: name
    file_path TEXT NOT NULL,                -- From JSON: file_path
    parameters JSON,                        -- From JSON: parameters (array)
    purpose TEXT NOT NULL,                  -- From JSON: purpose
    error_handling TEXT,                    -- From JSON: error_handling
    is_tool BOOLEAN NOT NULL DEFAULT 0,     -- From JSON: is_tool
    is_sub_helper BOOLEAN NOT NULL DEFAULT 0, -- From JSON: is_sub_helper
    return_statements JSON,                 -- From JSON: return_statements (array)
    target_database TEXT CHECK (...) NOT NULL -- From JSON: target_database
);
```

### directive_helpers Table (Junction)
```sql
CREATE TABLE IF NOT EXISTS directive_helpers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,          -- Lookup: directives.id WHERE name = directive_name
    helper_function_id INTEGER NOT NULL,    -- Lookup: helper_functions.id WHERE name = helper_name
    execution_context TEXT,                 -- From JSON: execution_context
    sequence_order INTEGER DEFAULT 0,       -- From JSON: sequence_order
    is_required BOOLEAN DEFAULT 1,          -- From JSON: is_required
    parameters_mapping JSON,                -- From JSON: parameters_mapping
    description TEXT,                       -- From JSON: description
    UNIQUE(directive_id, helper_function_id, execution_context),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (helper_function_id) REFERENCES helper_functions(id) ON DELETE CASCADE
);
```

---

## Workflow

### Phase 1: Prepare Helper JSON Files ⏳ CURRENT PHASE

**Task**: Convert markdown → JSON with complete fields

For each markdown file (core, git, orchestrators, project, settings, user-custom):

1. **Parse existing markdown**
   - Extract: name, purpose, parameters, classification
   - Identify: missing fields that need to be added

2. **Add missing fields**:
   - `file_path`: Determine MCP server code location
   - `error_handling`: Standardize error handling descriptions
   - `return_statements`: Convert notes to JSON array format
   - `used_by_directives`: Manually map directive relationships

3. **Structure as JSON**:
   - Array of helper objects
   - Each object has all fields for `helper_functions` table
   - Each object includes `used_by_directives` array for mapping

4. **Output**:
   - `docs/helpers/json/helpers-core.json`
   - `docs/helpers/json/helpers-git.json`
   - `docs/helpers/json/helpers-orchestrators.json`
   - `docs/helpers/json/helpers-project.json`
   - `docs/helpers/json/helpers-settings.json`
   - `docs/helpers/json/helpers-user-custom.json`

**Estimated Effort**: 1-2 weeks (manual mapping of directive relationships)

---

### Phase 2: Prepare Directive Flow Mapping ⏳ NEXT

**Task**: Create directive_flow.json for directive navigation

**File**: `docs/directives-json/directive-flow.json`

Maps to `directive_flow` table:

```json
{
  "flows": [
    {
      "from_directive": "aifp_run",
      "to_directive": "aifp_status",
      "flow_type": "status_branch",
      "condition_key": null,
      "condition_value": null,
      "condition_description": "Always check status first",
      "priority": 100,
      "description": "Entry point routes to status check"
    },
    {
      "from_directive": "aifp_status",
      "to_directive": "project_task_create",
      "flow_type": "conditional",
      "condition_key": "has_incomplete_tasks",
      "condition_value": "false",
      "condition_description": "No incomplete tasks found",
      "priority": 80,
      "description": "Status shows no work, offer to create new task"
    }
  ]
}
```

**Process**:
1. Go through each directive's workflow branches
2. Identify flow transitions:
   - Status branches (aifp_status → work directives)
   - Completion loops (work directive → aifp_status)
   - Conditional paths (based on state)
   - Error handlers
3. Document as JSON with all fields
4. Assign priorities for decision tree

**Estimated Effort**: 1-2 weeks (mapping 125 directives' flows)

---

### Phase 3: Modify Import Script ⏳ FUTURE

**Task**: Update `sync-directives.py` for comprehensive import

**Current Script**: `docs/directives-json/sync-directives.py`
- Imports directives from directives-*.json
- Handles intent_keywords normalization

**Required Modifications**:

1. **Add helper import logic**:
   ```python
   def import_helpers():
       # Load all helpers-*.json files
       for json_file in ['helpers-core.json', 'helpers-git.json', ...]:
           helpers = load_json(json_file)
           for helper in helpers:
               # Insert into helper_functions table
               insert_helper(helper)
   ```

2. **Add directive-helper mapping logic**:
   ```python
   def import_directive_helpers():
       # For each helper's used_by_directives array
       for helper in all_helpers:
           helper_id = get_helper_id(helper['name'])
           for directive_mapping in helper['used_by_directives']:
               directive_id = get_directive_id(directive_mapping['directive_name'])
               # Insert into directive_helpers table
               insert_directive_helper_mapping(...)
   ```

3. **Add directive_flow import logic**:
   ```python
   def import_directive_flow():
       flows = load_json('directive-flow.json')
       for flow in flows['flows']:
           from_id = get_directive_id(flow['from_directive'])
           to_id = get_directive_id(flow['to_directive'])
           # Insert into directive_flow table
           insert_directive_flow(...)
   ```

4. **Execution order**:
   ```python
   # 1. Import directives (already exists)
   import_directives()

   # 2. Import intent_keywords (already exists)
   import_intent_keywords()

   # 3. Import helpers (NEW)
   import_helpers()

   # 4. Import directive-helper mappings (NEW)
   import_directive_helpers()

   # 5. Import directive flows (NEW)
   import_directive_flow()
   ```

**Estimated Effort**: 2-3 days (scripting + testing)

---

### Phase 4: Database Population & Testing ⏳ FUTURE

**Task**: Run complete import and validate

1. **Create fresh database**:
   ```bash
   rm aifp_core.db
   sqlite3 aifp_core.db < src/aifp/database/schemas/aifp_core.sql
   ```

2. **Run import script**:
   ```bash
   python docs/directives-json/sync-directives.py --execute
   ```

3. **Validate imports**:
   ```sql
   -- Check counts
   SELECT COUNT(*) FROM directives;          -- Should be 125
   SELECT COUNT(*) FROM helper_functions;    -- Should be 227
   SELECT COUNT(*) FROM directive_helpers;   -- Varies (all mappings)
   SELECT COUNT(*) FROM directive_flow;      -- Varies (all flows)

   -- Check relationships
   SELECT d.name, h.name, dh.execution_context
   FROM directive_helpers dh
   JOIN directives d ON dh.directive_id = d.id
   JOIN helper_functions h ON dh.helper_function_id = h.id
   LIMIT 10;
   ```

4. **Test queries**:
   ```python
   # Test helper lookup
   get_helpers_for_directive("aifp_run", include_helpers_data=True)

   # Test directive flow
   get_next_directives_from_status("aifp_status", status_object)
   ```

---

## Required Field Mapping Work

### 1. file_path (227 helpers)

**Decision needed**: Where will helpers live in MCP server code?

**Proposed structure**:
```
src/aifp/helpers/
├── core/
│   ├── directive_tools.py     (get_directive_by_name, search_directives, etc.)
│   ├── helper_tools.py        (get_helper_by_name, etc.)
│   └── metadata.py            (get_core_tables, get_core_schema, etc.)
├── project/
│   ├── task_tools.py          (get_task, get_incomplete_tasks, etc.)
│   ├── file_tools.py          (get_file, get_files_by_flow, etc.)
│   └── blueprint_tools.py     (project_blueprint_read, etc.)
├── git/
│   └── git_operations.py      (all git helpers)
├── settings/
│   └── preference_tools.py    (all settings helpers)
├── user_custom/
│   └── user_directive_tools.py (all user directive helpers)
└── orchestrators/
    └── orchestrators.py       (aifp_status, initialize_aifp_project, etc.)
```

**Action**: Assign file_path to each helper in JSON

---

### 2. used_by_directives (227 helpers)

**This is the big mapping task!**

For each helper, determine:
- Which directives use it?
- In what context? (workflow step, error handler, validation, etc.)
- In what order? (if multiple helpers in same directive)
- Required or optional?
- Any parameter mappings?

**Example workflow** for `get_task(task_id)`:

```markdown
**Used by**:
1. project_task_complete
   - Context: load_task_data
   - Order: 1
   - Required: true
   - Description: Loads task to mark complete

2. project_task_update
   - Context: load_task_data
   - Order: 1
   - Required: true
   - Description: Loads task to update

3. aifp_status
   - Context: display_current_task
   - Order: 3
   - Required: false
   - Description: Shows details of current task if available
```

**Action**: For each helper, document all directive usage

---

### 3. error_handling (standardize)

**Current state**: Some helpers have prose descriptions, some don't

**Target format**: Clear, structured statement

**Examples**:
- ✅ "Returns null if not found. No exceptions raised."
- ✅ "Raises ValueError if task_id invalid. Returns empty array if no matches."
- ✅ "Returns None on database error. Logs error to system."

**Action**: Standardize all error_handling descriptions

---

### 4. return_statements (convert to JSON array)

**Current state**: Some helpers have notes about return values

**Target format**: JSON array of AI guidance statements

**Example**:
```json
"return_statements": [
  "Check result for null before accessing fields",
  "Directive object includes workflow, roadblocks, and intent keywords",
  "Use get_directive_content() for full MD documentation"
]
```

**Action**: Convert prose notes to structured JSON arrays

---

## File Structure After Completion

```
docs/
├── helpers/
│   ├── consolidated/           (markdown - for reference)
│   │   ├── helpers-consolidated-core.md
│   │   ├── helpers-consolidated-git.md
│   │   └── ...
│   └── json/                   (JSON - for import)
│       ├── helpers-core.json           ⏳ TO CREATE
│       ├── helpers-git.json            ⏳ TO CREATE
│       ├── helpers-orchestrators.json  ⏳ TO CREATE
│       ├── helpers-project.json        ⏳ TO CREATE
│       ├── helpers-settings.json       ⏳ TO CREATE
│       └── helpers-user-custom.json    ⏳ TO CREATE
└── directives-json/
    ├── directives-fp-core.json      ✅ READY
    ├── directives-fp-aux.json       ✅ READY
    ├── directives-project.json      ✅ READY
    ├── directives-git.json          ✅ READY
    ├── directives-user-system.json  ✅ READY
    ├── directives-user-pref.json    ✅ READY
    ├── directive-flow.json          ⏳ TO CREATE
    └── sync-directives.py           ⏳ TO MODIFY
```

---

## Timeline Estimate

### Phase 1: Prepare Helper JSON Files (1-2 weeks)
- Parse markdown → JSON structure (1 day)
- Assign file_path to all helpers (1 day)
- Standardize error_handling (2 days)
- Convert return_statements to JSON (1 day)
- **Map used_by_directives (5-7 days)** ← biggest task
- Review and validate (1 day)

### Phase 2: Prepare Directive Flow JSON (1-2 weeks)
- Map directive navigation flows (5-7 days)
- Document conditions and priorities (2-3 days)
- Review and validate (1 day)

### Phase 3: Modify Import Script (2-3 days)
- Add helper import logic (1 day)
- Add directive-helper mapping logic (1 day)
- Add directive_flow import logic (1 day)

### Phase 4: Import & Test (1 day)
- Run import script
- Validate data
- Test queries

**Total**: 3-4 weeks for complete preparation and import

---

## Success Criteria

- [ ] All 227 helpers in JSON format with complete fields
- [ ] All helpers have file_path assigned
- [ ] All helpers have standardized error_handling
- [ ] All helpers have structured return_statements
- [ ] All helpers have used_by_directives mapped
- [ ] directive-flow.json created with all navigation flows
- [ ] sync-directives.py modified for complete import
- [ ] Database successfully populated with all data
- [ ] Validation queries return expected results
- [ ] Test queries work for directive-helper lookups
- [ ] Test queries work for directive flow navigation

---

## Next Action: Start Phase 1

**Task**: Create template for helpers-core.json and begin mapping

Would you like me to:
1. Create a template JSON file with 2-3 example helpers fully mapped?
2. Write a script to parse markdown → JSON structure (with TODOs for manual fields)?
3. Create a checklist for tracking the used_by_directives mapping progress?

---

**Document Status**: Ready for Phase 1 execution
**Last Updated**: 2025-12-16
**Next Review**: After Phase 1 completion

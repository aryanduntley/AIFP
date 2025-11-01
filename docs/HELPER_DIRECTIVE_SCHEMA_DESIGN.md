# Helper-Directive Relationship Schema Design

**Version**: 1.0
**Status**: Ready for implementation
**Last Updated**: 2025-11-01

---

## Overview

This document describes the SQL schema design for managing the many-to-many relationship between directives and helper functions across both `aifp_core.db` (MCP system) and `user_directives.db` (user automation projects).

---

## Schema Design Pattern

### Many-to-Many Relationship via Junction Table

```
directives              directive_helpers           helper_functions
┌──────────┐           ┌─────────────────┐         ┌──────────────┐
│ id (PK)  │───┐       │ id (PK)         │    ┌───│ id (PK)      │
│ name     │   └──────→│ directive_id    │    │   │ name         │
│ type     │           │ helper_func_id  │←───┘   │ file_path    │
│ workflow │           │ exec_context    │         │ parameters   │
└──────────┘           │ sequence_order  │         │ purpose      │
                       │ is_required     │         │ is_tool      │
                       │ params_mapping  │         └──────────────┘
                       └─────────────────┘
```

**Key Features**:
- One directive can use many helper functions
- One helper function can be used by many directives
- Junction table stores context and execution metadata

---

## 1. AIFP Core Schema (aifp_core.db)

### Helper Functions Table

```sql
CREATE TABLE IF NOT EXISTS helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,               -- e.g., 'get_project_status'
    file_path TEXT,                          -- e.g., 'helpers/project/get_project_status.py'
    parameters JSON,                         -- e.g., '["project_id"]'
    purpose TEXT,                            -- What this helper does
    error_handling TEXT,                     -- How errors are handled
    is_tool BOOLEAN DEFAULT 0,               -- TRUE if exposed as MCP tool
    is_sub_helper BOOLEAN DEFAULT 0,         -- TRUE if sub-helper (only called by other helpers)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Stores all MCP system helper functions that implement directive functionality.

**Helper Classification**:
- `is_tool = TRUE`: Exposed as MCP tool (AI can call directly via MCP)
- `is_sub_helper = TRUE`: Sub-helper (only called by other helpers, no directive mapping)
- Both `FALSE`: Directive helper (called via directive workflows)

---

### Directive-Helper Junction Table

```sql
CREATE TABLE IF NOT EXISTS directive_helpers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    helper_function_id INTEGER NOT NULL,
    execution_context TEXT,                  -- e.g., 'validation', 'workflow_step_3'
    sequence_order INTEGER DEFAULT 0,        -- Order when multiple helpers used
    is_required BOOLEAN DEFAULT 1,           -- Must execute vs optional
    parameters_mapping JSON,                 -- Maps directive params to helper params
    description TEXT,                        -- Why this helper is used here
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(directive_id, helper_function_id, execution_context),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (helper_function_id) REFERENCES helper_functions(id) ON DELETE CASCADE
);
```

**Purpose**: Maps which helpers each directive uses and provides execution metadata.

---

### Example Usage (aifp_core.db)

**Scenario**: `aifp_status` directive uses multiple helpers

```sql
-- 1. Insert helpers
INSERT INTO helper_functions (name, file_path, purpose, is_tool) VALUES
  ('get_project_status', 'helpers/project/get_project_status.py', 'Check if project initialized', 0),
  ('get_status_tree', 'helpers/project/get_status_tree.py', 'Build task priority tree', 0),
  ('get_git_status', 'helpers/git/get_git_status.py', 'Get Git state snapshot', 0),
  ('get_user_directive_status', 'helpers/user_directives/get_user_directive_status.py', 'Check user directive state', 0);

-- 2. Map to aifp_status directive
INSERT INTO directive_helpers
  (directive_id, helper_function_id, execution_context, sequence_order, description)
VALUES
  ((SELECT id FROM directives WHERE name='aifp_status'),
   (SELECT id FROM helper_functions WHERE name='get_project_status'),
   'initialization_check', 1, 'First check if project exists'),

  ((SELECT id FROM directives WHERE name='aifp_status'),
   (SELECT id FROM helper_functions WHERE name='get_status_tree'),
   'task_analysis', 2, 'Build priority task tree'),

  ((SELECT id FROM directives WHERE name='aifp_status'),
   (SELECT id FROM helper_functions WHERE name='get_git_status'),
   'git_sync', 3, 'Check for external changes'),

  ((SELECT id FROM directives WHERE name='aifp_status'),
   (SELECT id FROM helper_functions WHERE name='get_user_directive_status'),
   'user_directive_check', 4, 'Check user directive status if Use Case 2');
```

**Query to get all helpers for a directive**:
```sql
SELECT
    d.name as directive_name,
    hf.name as helper_name,
    hf.file_path,
    dh.execution_context,
    dh.sequence_order,
    dh.is_required
FROM directives d
JOIN directive_helpers dh ON d.id = dh.directive_id
JOIN helper_functions hf ON dh.helper_function_id = hf.id
WHERE d.name = 'aifp_status'
ORDER BY dh.sequence_order;
```

---

## 2. User Directives Schema (user_directives.db)

### Helper Functions Table (User Project)

```sql
CREATE TABLE IF NOT EXISTS helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,               -- e.g., 'check_lights_status'
    file_path TEXT,                          -- e.g., 'src/helpers/check_lights.py'
    parameters JSON,                         -- e.g., '["room_id", "threshold"]'
    purpose TEXT,
    error_handling TEXT,

    -- Code tracking (AI-generated implementation functions)
    function_signature TEXT,                 -- e.g., 'def check_lights_status(room_id: str) -> bool:'
    return_type TEXT,                        -- e.g., 'bool', 'dict', 'Result[str, Error]'
    is_pure BOOLEAN DEFAULT 1,               -- Is this a pure function (FP compliance)

    -- Status tracking
    implementation_status TEXT DEFAULT 'not_implemented' CHECK (implementation_status IN (
        'not_implemented',                   -- Function defined but code not yet generated
        'generated',                         -- Code generated by AI
        'tested',                            -- User has tested
        'approved'                           -- User approved and active
    )),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Differences from aifp_core**:
- **No `is_tool` field**: User helpers are project code, not MCP tools
- **`function_signature`**: Tracks generated function signature
- **`is_pure`**: Enforces FP compliance for generated code
- **`implementation_status`**: Tracks AI generation → user approval lifecycle

---

### Directive-Helper Junction Table (User Project)

```sql
CREATE TABLE IF NOT EXISTS directive_helpers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    helper_function_id INTEGER NOT NULL,
    execution_context TEXT,                  -- e.g., 'validation', 'execution', 'error_handler'
    sequence_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT 1,
    parameters_mapping JSON,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(directive_id, helper_function_id, execution_context),
    FOREIGN KEY (directive_id) REFERENCES user_directives(id) ON DELETE CASCADE,
    FOREIGN KEY (helper_function_id) REFERENCES helper_functions(id) ON DELETE CASCADE
);
```

**Same structure as aifp_core** - maintains uniformity.

---

### Example Usage (user_directives.db)

**Scenario**: Home automation - "Turn off lights at 5pm"

```sql
-- 1. User directive created from YAML parsing
INSERT INTO user_directives (name, source_file, source_format, domain, trigger_type, action_type, ...)
VALUES ('turn_off_lights_5pm', 'directives/lights.yaml', 'yaml', 'home_automation', 'time', 'api_call', ...);

-- 2. AI detects needed helper functions
INSERT INTO helper_functions (name, file_path, purpose, implementation_status) VALUES
  ('check_lights_status', 'src/helpers/check_lights.py', 'Check current light status', 'not_implemented'),
  ('turn_off_lights', 'src/helpers/turn_off_lights.py', 'Send off command to lights API', 'not_implemented'),
  ('log_automation_event', 'src/helpers/log_event.py', 'Log automation actions', 'not_implemented');

-- 3. Map helpers to directive
INSERT INTO directive_helpers
  (directive_id, helper_function_id, execution_context, sequence_order)
VALUES
  ((SELECT id FROM user_directives WHERE name='turn_off_lights_5pm'),
   (SELECT id FROM helper_functions WHERE name='check_lights_status'),
   'pre_execution', 1),

  ((SELECT id FROM user_directives WHERE name='turn_off_lights_5pm'),
   (SELECT id FROM helper_functions WHERE name='turn_off_lights'),
   'execution', 2),

  ((SELECT id FROM user_directives WHERE name='turn_off_lights_5pm'),
   (SELECT id FROM helper_functions WHERE name='log_automation_event'),
   'post_execution', 3);

-- 4. AI generates implementation code
-- Updates implementation_status: 'not_implemented' → 'generated'

-- 5. User tests and approves
-- Updates implementation_status: 'generated' → 'tested' → 'approved'
```

---

## Benefits of This Design

### 1. Flexibility
- One helper can serve multiple directives
- Directives can use multiple helpers
- Easy to add/remove helper relationships

### 2. Execution Metadata
- `execution_context`: Know when/why helper is called
- `sequence_order`: Control execution order
- `is_required`: Optional vs mandatory helpers
- `parameters_mapping`: Dynamic parameter passing

### 3. Traceability
- Query all directives using a helper
- Query all helpers for a directive
- Track helper usage patterns

### 4. Uniformity
- Same pattern in both databases
- Easier to maintain and understand
- Code reuse for helper management logic

### 5. Lifecycle Management (User Directives)
- Track AI generation progress
- User testing and approval workflow
- FP compliance enforcement

---

## Migration Strategy

### Step 1: Update Schemas ✅
- [x] Add `directive_helpers` table to `aifp_core.sql`
- [x] Add `helper_functions` and `directive_helpers` to `user_directives.sql`
- [x] Add indexes for performance

### Step 2: Populate Helper Functions
- [ ] Parse all 50 helpers from `helper-functions-reference.md`
- [ ] Insert into `aifp_core.db` helper_functions table
- [ ] Mark which are MCP tools (`is_tool = 1`)

### Step 3: Map Helpers to Directives
- [ ] Audit all 124 directives
- [ ] Identify helper usage in workflows
- [ ] Populate `directive_helpers` junction table

### Step 4: Update Sync Script
- [ ] Modify `sync-directives.py` to populate helper relationships
- [ ] Add validation to check helper references

### Step 5: Update Directive JSON Files (Optional)
- [ ] Add `helper_functions` metadata to directive JSON files
- [ ] Use for documentation and sync reference

---

## Querying Examples

### Find all helpers for a directive
```sql
SELECT hf.name, dh.execution_context, dh.sequence_order
FROM directive_helpers dh
JOIN helper_functions hf ON dh.helper_function_id = hf.id
WHERE dh.directive_id = (SELECT id FROM directives WHERE name = 'aifp_status')
ORDER BY dh.sequence_order;
```

### Find all directives using a helper
```sql
SELECT d.name, d.type, dh.execution_context
FROM directive_helpers dh
JOIN directives d ON dh.directive_id = d.id
WHERE dh.helper_function_id = (SELECT id FROM helper_functions WHERE name = 'get_project_status');
```

### Find orphaned helpers (not used by any directive)
```sql
SELECT hf.name, hf.file_path
FROM helper_functions hf
LEFT JOIN directive_helpers dh ON hf.id = dh.helper_function_id
WHERE dh.id IS NULL;
```

### Find MCP tools (helpers exposed to AI)
```sql
SELECT name, file_path, purpose
FROM helper_functions
WHERE is_tool = 1
ORDER BY name;
```

---

## Next Steps

1. **Re-run sync script** with updated schema
2. **Populate helper_functions table** (all 50 helpers)
3. **Map helpers to directives** (directive_helpers junction table)
4. **Test queries** to ensure relationships work
5. **Document helper usage** in directive MD files

---

## Related Documents

- `docs/helper-functions-reference.md` - Complete helper function specifications
- `src/aifp/database/schemas/aifp_core.sql` - MCP database schema
- `src/aifp/database/schemas/user_directives.sql` - User directives database schema
- `docs/blueprints/blueprint_user_directives.md` - User directives system design

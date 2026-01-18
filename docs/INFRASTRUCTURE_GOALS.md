# Infrastructure Data Management - Requirements Document

**Date**: 2026-01-17
**Status**: Requirements Definition
**Priority**: High - Foundational for project initialization and session context

---

## Goal Summary

Establish a consistent, visible infrastructure data system that:
1. Pre-populates standard infrastructure entries during project initialization
2. Provides full infrastructure data in session bundles
3. Ensures AI has access to project infrastructure without repeated queries

---

## Goal 1: Pre-populated Infrastructure Entries on Init

### Requirement

During `project_init`, the system must pre-populate the `infrastructure` table with standard entries that have **empty values** but **defined types and descriptions**.

### Standard Infrastructure Fields

The following fields must be created during initialization:

| Type | Initial Value | Description |
|------|---------------|-------------|
| `source_directory` | `""` (empty) | Primary source code directory (e.g., src, lib, app) |
| `primary_language` | `""` (empty) | Main programming language (e.g., Python 3.11, Rust 1.75, Node 18) |
| `build_tool` | `""` (empty) | Primary build tool (e.g., cargo, npm, make, maven, gradle) |
| `package_manager` | `""` (empty) | Package/dependency manager (e.g., pip, npm, cargo, maven) |
| `test_framework` | `""` (empty) | Testing framework (e.g., pytest, jest, cargo test, junit) |
| `runtime_version` | `""` (empty) | Language runtime or compiler version (e.g., Python 3.11.2, rustc 1.75.0) |

### Implementation Location

**File**: `src/aifp/database/initialization/standard_infrastructure.sql`

```sql
-- Standard Infrastructure Entries
-- Populated during project initialization with empty values
-- AI detects and populates values after initialization

INSERT INTO infrastructure (type, value, description) VALUES
  ('source_directory', '', 'Primary source code directory (e.g., src, lib, app)'),
  ('primary_language', '', 'Main programming language (e.g., Python 3.11, Rust 1.75, Node 18)'),
  ('build_tool', '', 'Primary build tool (e.g., cargo, npm, make, maven, gradle)'),
  ('package_manager', '', 'Package/dependency manager (e.g., pip, npm, cargo, maven)'),
  ('test_framework', '', 'Testing framework (e.g., pytest, jest, cargo test, junit)'),
  ('runtime_version', '', 'Language runtime or compiler version (e.g., Python 3.11.2, rustc 1.75.0)');
```

### Execution Timing

The SQL file must be executed within the `project_init` orchestrator helper, immediately after:
1. Creating `project.db` from `schemas/project.sql`
2. Inserting project metadata (name, purpose, goals)
3. **Before** inserting default completion path

**Code Location**: Within `project_init` orchestrator (helpers/orchestrators/orchestrators.py)

```python
# Inside project_init orchestrator
# Step 5: Initialize project database
conn.execute(schema_sql)  # Create tables
conn.execute(insert_project_metadata)  # Project entry
conn.executescript(load_sql("initialization/standard_infrastructure.sql"))  # Standard infrastructure
conn.execute(insert_completion_path)  # Default completion path
```

### Rationale

**Why pre-populate with empty values?**
1. **Consistency**: Prevents AI from creating duplicate entries with different naming (e.g., `language`, `primaryLanguage`, `lang`)
2. **Visibility**: `aifp_status` and `aifp_run` return ALL infrastructure rows, making standard fields discoverable
3. **Helper Support**: `get_infrastructure_by_type('primary_language')` works even if value is empty
4. **Clear Intent**: Empty values signal "needs to be populated" vs. "doesn't exist"

**Why not make these database columns?**
- The `type/value/description` pattern is flexible for user-defined infrastructure
- Standard fields are just "well-known types" that AIFP recognizes
- Users can add custom infrastructure entries without schema changes

---

## Goal 2: Full Infrastructure Data in Session Bundle

### Requirement

When AI calls `aifp_run(is_new_session=true)`, the returned bundle must include complete infrastructure data to minimize subsequent queries.

### Session Bundle Structure

```json
{
  "status": { /* comprehensive status data */ },
  "user_settings": { /* user preferences */ },
  "fp_directive_index": { /* FP directives by category */ },
  "all_directive_names": [ /* all directive names */ ],
  "infrastructure_data": [
    {
      "id": 1,
      "type": "source_directory",
      "value": "src",
      "description": "Primary source code directory (e.g., src, lib, app)",
      "created_at": "2026-01-17T10:00:00",
      "updated_at": "2026-01-17T10:05:00"
    },
    {
      "id": 2,
      "type": "primary_language",
      "value": "Python 3.11",
      "description": "Main programming language (e.g., Python 3.11, Rust 1.75, Node 18)",
      "created_at": "2026-01-17T10:00:00",
      "updated_at": "2026-01-17T10:05:00"
    }
    // ... all infrastructure entries, including empty ones
  ],
  "guidance": { /* next steps and suggestions */ }
}
```

### Implementation

**Helper**: `aifp_run` (helpers/orchestrators/orchestrators.py)

**Update Required**:
```python
def aifp_run(is_new_session: bool = False) -> dict:
    if is_new_session:
        # Bundle comprehensive session data
        return {
            "status": aifp_status(),
            "user_settings": get_user_settings(),
            "fp_directive_index": get_fp_directive_index(),
            "all_directive_names": get_all_directive_names(),
            "infrastructure_data": get_all_infrastructure(),  # NEW
            "guidance": generate_guidance()
        }
    else:
        # Lightweight guidance for continuation
        return {"guidance": generate_lightweight_guidance()}
```

**New Helper Required**: `get_all_infrastructure()`

**Definition Location**: `docs/helpers/json/helpers-project-1.json` (or new helpers-project-infrastructure.json)

```json
{
  "name": "get_all_infrastructure",
  "file_path": "helpers/project/metadata.py",
  "parameters": [],
  "purpose": "Get all infrastructure entries including standard fields (even if empty)",
  "error_handling": "Return empty array if table doesn't exist or database not initialized",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns array of all infrastructure rows: [{id, type, value, description, created_at, updated_at}, ...]",
    "Includes standard entries even if value is empty string",
    "Standard entries: source_directory, primary_language, build_tool, package_manager, test_framework, runtime_version"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "aifp_run",
      "execution_context": "session_bundle",
      "sequence_order": 5,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Include infrastructure data in session bundle when is_new_session=true"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT * FROM infrastructure ORDER BY created_at",
    "Returns ALL rows including empty values",
    "Used by aifp_run to bundle infrastructure in session context",
    "AI caches this data and only re-calls if cache lost"
  ]
}
```

### Token Budget

**Current session bundle**: ~15-20k tokens
- status: ~10k
- settings: ~1k
- fp_index: ~2k
- directive_names: ~1k
- guidance: ~2k

**Adding infrastructure**: ~500 tokens (6 standard entries + user additions)
- Standard entries: ~300 tokens
- User additions: ~200 tokens average

**New total**: ~15.5-20.5k tokens (acceptable within context limits)

### Cache Strategy

**AI Behavior**:
1. **First call**: `aifp_run(is_new_session=true)` → receives full bundle with infrastructure
2. **Cache**: AI stores infrastructure data in session context
3. **Subsequent calls**: AI uses cached infrastructure
4. **Cache loss**: AI calls `get_all_infrastructure()` to refresh

**No repeated calls needed** unless:
- AI loses context/cache
- User explicitly requests fresh infrastructure data
- Infrastructure values are updated during session

---

## Goal 3: AI Populates Infrastructure Values Post-Init

### Workflow

After `project_init` completes with empty infrastructure values:

1. **AI detects values from codebase**:
   ```
   - primary_language: Scan file extensions, analyze code
   - build_tool: Check for Cargo.toml, package.json, Makefile, pom.xml
   - package_manager: Infer from build tool or language defaults
   - test_framework: Scan dependencies in config files
   - runtime_version: Check .tool-versions, .nvmrc, rust-toolchain.toml
   ```

2. **AI prompts user for missing/uncertain values**:
   ```
   "I detected Python 3.11 as the primary language. Is this correct?"
   "No build tool detected. Are you using make, setuptools, or something else?"
   ```

3. **AI updates infrastructure table**:
   ```python
   # Get all infrastructure to find IDs
   all_infra = get_all_infrastructure()

   for entry in all_infra:
       if entry['type'] == 'primary_language' and entry['value'] == '':
           detected = 'Python 3.11'  # From detection
           update_project_entry('infrastructure', entry['id'], {'value': detected})

       if entry['type'] == 'build_tool' and entry['value'] == '':
           detected = 'make'  # From detection
           update_project_entry('infrastructure', entry['id'], {'value': detected})
   ```

### Return Statements Guidance

**In `project_init` orchestrator return_statements**:
```json
"return_statements": [
  "Project initialized successfully",
  "Standard infrastructure entries created with empty values",
  "AI MUST populate infrastructure values by:",
  "  1. Detecting from codebase: language, build tool, test framework, runtime version",
  "  2. Prompting user for confirmation or missing values",
  "  3. Updating via: update_project_entry('infrastructure', id, {'value': '...'})",
  "Call get_all_infrastructure() to retrieve entries and their IDs",
  "Empty values signal 'needs population' - do not leave empty"
]
```

---

## Success Criteria

### For Goal 1 (Pre-population)
- ✅ `standard_infrastructure.sql` file created in `src/aifp/database/initialization/`
- ✅ File contains 6 standard INSERT statements with empty values
- ✅ `project_init` orchestrator executes this SQL after schema creation
- ✅ After init, `SELECT * FROM infrastructure` returns 6 rows with empty values

### For Goal 2 (Session Bundle)
- ✅ `get_all_infrastructure()` helper defined in helpers JSON
- ✅ `aifp_run(is_new_session=true)` includes `infrastructure_data` key
- ✅ Infrastructure data includes all rows (including empty values)
- ✅ Token budget remains within acceptable limits (~20k)

### For Goal 3 (AI Population)
- ✅ `project_init` return_statements guide AI to populate values
- ✅ AI can detect common values from codebase
- ✅ AI prompts user for uncertain values
- ✅ AI updates infrastructure using existing `update_project_entry` helper

---

## Dependencies

### Required Files
1. **NEW**: `src/aifp/database/initialization/standard_infrastructure.sql`
2. **UPDATE**: `docs/helpers/json/helpers-project-1.json` (add `get_all_infrastructure`)
3. **UPDATE**: `docs/helpers/json/helpers-orchestrators.json` (update `aifp_run`, add `project_init`)
4. **UPDATE**: `src/aifp/reference/directives/project_init.md` (document AI's post-init role)

### Required Helpers
1. **NEW**: `project_init` orchestrator (coordinates full initialization)
2. **NEW**: `get_all_infrastructure()` (returns all infrastructure rows)
3. **EXISTING**: `update_project_entry()` (AI uses to populate values)
4. **EXISTING**: `aifp_run()` (modified to include infrastructure in bundle)

---

## Migration Path

**For existing projects** (already initialized without standard infrastructure):

Option 1: **Manual Migration Script**
```sql
-- Run against existing project.db
INSERT OR IGNORE INTO infrastructure (type, value, description) VALUES
  ('source_directory', '', 'Primary source code directory (e.g., src, lib, app)'),
  ('primary_language', '', 'Main programming language (e.g., Python 3.11, Rust 1.75, Node 18)'),
  ('build_tool', '', 'Primary build tool (e.g., cargo, npm, make, maven, gradle)'),
  ('package_manager', '', 'Package/dependency manager (e.g., pip, npm, cargo, maven)'),
  ('test_framework', '', 'Testing framework (e.g., pytest, jest, cargo test, junit)'),
  ('runtime_version', '', 'Language runtime or compiler version (e.g., Python 3.11.2, rustc 1.75.0)');
```

Option 2: **Helper Function** `migrate_infrastructure_schema()`
- Checks if standard entries exist
- Adds missing entries with empty values
- AI can call during session if infrastructure incomplete

---

## Notes

- Infrastructure table already exists in `schemas/project.sql` (lines 35-42)
- No schema changes required, only data population strategy
- This approach maintains backward compatibility with existing infrastructure entries
- Users can add custom infrastructure types beyond the 6 standard ones

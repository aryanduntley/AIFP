# Helper Documentation Review & Consolidation

**Date:** 2025-11-27
**Purpose:** Compare existing helper docs against source of truth and recommend consolidation strategy

---

## Files Reviewed

1. `docs/helpers/parse_helpers.py` (89 lines)
2. `docs/helpers/helper-functions-reference.md` (1654 lines)
3. `docs/helpers/helper-tool-classification.md` (237 lines)
4. `docs/helpers/generic-tools-mcp.md` (773 lines)
5. `docs/helpers/generic-tools-project.md` (992 lines)

**Source of Truth:** `docs/helpers/info-helpers-project.txt`

---

## Key Finding: Three Helper Registry Categories

The reviewed files and source of truth describe **three distinct categories** of helpers:

### Category 1: Core Directives (helpers_registry_core.json)
**Purpose:** Core AIFP directive workflows and system operations
**Examples:**
- Directive execution workflows
- FP compliance directives
- System initialization
**Current Count:** 33 helpers

### Category 2: AIFP Orchestrators (helpers_registry_aifp.json or split)
**Purpose:** High-level AIFP operations that orchestrate multiple database helpers
**Files documenting these:** `generic-tools-*.md`, `helper-functions-reference.md`
**Examples:**
- `get_current_progress()` - calls 5-15 helpers depending on scope
- `update_project_state()` - orchestrates task lifecycle
- `parse_directive_file()` - workflow helper for user directives
- `find_directives()` - directive discovery tool
- `aifp_run()`, `aifp_status()` - High-level AIFP commands
**To Be Created:** ~19-25 helpers

### Category 3: Database CRUD Helpers (Source of Truth Files)
**Purpose:** Direct database operations - add, get, update, delete, reserve, finalize
**Files:** `info-helpers-project.txt` (167), `info-helpers-user-custom.txt` (78), `info-helpers-user-settings.txt` (40)
**Examples:**
- `get_task(task_id)` - Single DB query
- `add_file(name, path, language)` - Single DB insert
- `update_function(function_id, ...)` - Single DB update
- `get_flows_by_theme(theme_id)` - Single DB query
**Current Count:** 151 helpers (40 settings + 45 user getters + 33 user setters + 33 core)
**To Create:** 167 project helpers

---

## AIFP Orchestrators Registry Structure

### helpers_registry_aifp.json (NEW)

**Purpose:** High-level AIFP operations that orchestrate multiple database helpers and provide primary MCP tool interfaces.

**Characteristics:**
- **Multi-database operations:** Call helpers across multiple databases
- **Workflow orchestration:** Coordinate complex sequences of operations
- **High-level interfaces:** Primary entry points for AI and MCP tools
- **Most are MCP tools:** ~89% have `is_tool: true`

### Contents (19 orchestrators):

#### MCP Orchestrators (4 helpers)
**Category:** `mcp_orchestrators`
**Database:** aifp_core.db
**Purpose:** Directive and helper discovery, system introspection

1. **find_directives** - Directive discovery with intent matching
   - Calls: find_directive_by_intent, search_directives, get_directive, get_directive_interactions
   - Primary use: aifp_run directive

2. **find_helpers** - Helper function discovery
   - Searches registry by purpose, database, category
   - Grouping and filtering capabilities

3. **get_system_context** - Complete system state
   - Calls: count_directives_by_type, count_helpers_by_database, get_project_metadata
   - Primary use: Session initialization, aifp_status

4. **query_mcp_relationships** - Directive/helper relationship analysis
   - Calls: get_directive_interactions, get_helper_relationships
   - Primary use: Workflow visualization, dependency analysis

#### Project Orchestrators (5 helpers)
**Category:** `project_orchestrators`
**Database:** project.db (multi-helper calls)
**Purpose:** High-level project state management

1. **get_current_progress** - Status query orchestrator
   - Replaces 5-15 separate helper calls
   - Flexible scope and detail_level parameters
   - Primary use: aifp_status directive

2. **update_project_state** - Update orchestrator
   - Single entry point for common updates (start_task, complete_task, link_flows)
   - Automatically creates notes
   - Primary use: project_task_update

3. **batch_update_progress** - Batch update orchestrator
   - Atomic multi-item updates with transaction support
   - Primary use: project_update_db (after code generation)

4. **query_project_state** - SQL-like query interface
   - Flexible filtering, joins, sorting without SQL
   - Primary use: Complex queries, reporting

5. **get_work_context** - Resume context
   - Complete task + flows + files + functions + interactions
   - Replaces 6-8 separate calls
   - Primary use: project_auto_resume

#### User Directive Workflow Orchestrators (10 helpers)
**Category:** `user_directive_workflows`
**Database:** user_directives.db (orchestration level)
**Purpose:** User directive lifecycle management

1. **parse_directive_file** - Parse user directive files with ambiguity detection
2. **validate_user_directive** - Interactive validation with Q&A
3. **generate_implementation_code** - FP-compliant code generation
4. **detect_dependencies** - Detect required packages/APIs/env vars
5. **install_dependency** - Install packages with user confirmation
6. **activate_directive** - Deploy and activate directive implementation
7. **monitor_directive_execution** - Track execution stats, rotate logs
8. **get_user_directive_status** - Comprehensive status report
9. **update_directive** - Handle source file changes, re-validation
10. **deactivate_directive** - Stop execution, preserve stats

### Split Decision

**Recommendation:** Start with single file `helpers_registry_aifp.json`

**Rationale:**
- 19 helpers is manageable in one file
- All share common characteristic: orchestration
- Easier to maintain single source
- Can split later if it grows beyond 50 helpers

**If split becomes necessary:**
```
Option B: Category split
├── helpers_registry_aifp_mcp.json (4)
├── helpers_registry_aifp_project.json (5)
└── helpers_registry_aifp_user_workflows.json (10)

Option C: Operation type split
├── helpers_registry_aifp_queries.json (7 read orchestrators)
├── helpers_registry_aifp_mutations.json (2 write orchestrators)
└── helpers_registry_aifp_workflows.json (10 workflow orchestrators)
```

---

## Detailed Analysis by File

### 1. parse_helpers.py

**Type:** Utility script
**Purpose:** Parse helpers from helper-functions-reference.md into JSON

**Finding:**
- Creates `helpers_parsed.json` (which is already in cleanup list)
- Was used before current registry system
- **Overlaps:** Completely superseded by new registry system

**Recommendation:** ❌ **DELETE** - No longer needed

---

### 2. helper-functions-reference.md (1654 lines)

**Type:** Specification document
**Purpose:** Comprehensive reference for "all helper functions" across AIFP

**Claimed Helpers:** 50 total
- MCP: 7 helpers
- Project: 19 helpers (5 initialization + 14 management)
- Git: 10 helpers
- Preferences: 4 helpers
- User Directives: 10 helpers

**Finding:**
- This is a **SPEC document** ("Not yet implemented" - line 1508)
- Describes **workflow orchestrators**, not database CRUD helpers
- Examples of what's documented here:
  - `create_project_blueprint()` - High-level orchestrator
  - `scan_existing_files()` - System utility
  - `parse_directive_file()` - Workflow helper
  - `validate_user_directive()` - Workflow helper
  - `generate_implementation_code()` - Code generation tool
  - `detect_and_init_project()` - System orchestrator

**What's Useful:**
- Documents workflow helpers not in our CRUD registries
- Shows integration points between layers
- Contains detailed error handling strategies
- Good FP compliance guidelines (lines 1512-1606)

**What Overlaps:**
- Some helper names overlap with CRUD helpers but have different purposes:
  - `init_project_db()` here is high-level, our `add_infrastructure()` is CRUD
  - `get_project_status()` here is orchestrator, we have multiple status getters

**Recommendation:** 📝 **EXTRACT THEN ARCHIVE**
- Extract 10 workflow orchestrators to add to core registry:
  - `parse_directive_file`, `validate_user_directive`, `generate_implementation_code`
  - `detect_dependencies`, `install_dependency`, `activate_directive`
  - `monitor_directive_execution`, `get_user_directive_status`, `update_directive`
  - `deactivate_directive`
- Extract FP guidelines to docs/development/
- Archive this file - it served its purpose as design doc

---

### 3. helper-tool-classification.md (237 lines)

**Type:** Classification guide
**Purpose:** Defines is_tool: true (MCP-exposed) vs is_tool: false (internal)

**Claimed Counts:**
- project.db: 79 helpers (15 tools, 64 internal)
- aifp_core.db: 55 helpers (12 tools, 43 internal)
- user_preferences.db: 39 helpers (8 tools, 31 internal)
- user_directives.db: 32 helpers (7 tools, 25 internal)
- **Total:** 205 helpers, 42 tools (20%)

**Actual Counts from Source Files:**
- project.db: **167 helpers** (not 79)
- aifp_core.db: **33 helpers** (not 55)
- user_preferences.db: **40 helpers** (not 39 - close!)
- user_directives.db: **78 helpers** (not 32)
- **Total:** **318 helpers**

**Finding:**
- **Counts are WAY OFF** for project and user_directives (mixing layers?)
- **Classification philosophy is EXCELLENT:**
  - is_tool: true for generic orchestrators, primary interfaces
  - is_tool: false for specific CRUD, sub-helpers, utilities
  - Goal: ~20% tools, ~80% internal
- Decision guidelines (lines 175-189) are very useful

**What's Useful:**
- Classification philosophy should guide our registry `is_tool` flags
- Decision guidelines for when to expose as MCP tool
- Future considerations section (promoting internal to tools, creating new generic tools)

**Recommendation:** 📝 **EXTRACT PHILOSOPHY THEN DELETE**
- Extract classification philosophy to REGISTRY_STATUS.md
- Apply 20% tool / 80% internal guideline to our registries
- Delete this file - counts are wrong, philosophy preserved

---

### 4. generic-tools-mcp.md (773 lines)

**Type:** Specification for Layer 2 orchestrators
**Purpose:** Define 4 high-level MCP generic tools

**Tools Documented:**
1. **find_directives()** - Directive discovery with intent matching
   - Calls: `find_directive_by_intent()`, `search_directives()`, `get_directive()`, `get_directive_interactions()`
   - Primary use: `aifp_run` directive

2. **find_helpers()** - Helper function discovery
   - Searches helper registry by purpose, database, category
   - Grouping and filtering capabilities

3. **get_system_context()** - Complete system state
   - Calls: `count_directives_by_type()`, `count_helpers_by_database()`, `get_project_metadata()`
   - Primary use: Session initialization, `aifp_status`

4. **query_mcp_relationships()** - Directive and helper relationship analysis
   - Calls: `get_directive_interactions()`, `get_helper_relationships()`
   - Primary use: Workflow visualization, dependency analysis

**Finding:**
- These are **ORCHESTRATORS** not in our current registries
- They sit ABOVE our CRUD helpers and call them
- Well-designed with comprehensive examples and error handling
- All should have `is_tool: true`

**Recommendation:** ✅ **ADD TO AIFP REGISTRY**
- Add these 4 orchestrators to `helpers_registry_aifp.json`
- Mark as `is_tool: true`, `is_sub_helper: false`
- Category: `"mcp_orchestrators"`
- After adding, can archive this file

---

### 5. generic-tools-project.md (992 lines)

**Type:** Specification for Layer 2 orchestrators
**Purpose:** Define 5 high-level project generic tools

**Tools Documented:**
1. **get_current_progress()** - Status query orchestrator
   - Replaces 5-10 separate helper calls
   - Flexible scope and detail_level parameters
   - Primary use: `aifp_status` directive

2. **update_project_state()** - Update orchestrator
   - Single entry point for common updates (start_task, complete_task, link_flows, etc.)
   - Automatically creates notes
   - Primary use: `project_task_update`

3. **batch_update_progress()** - Batch update orchestrator
   - Atomic multi-item updates with transaction support
   - Primary use: `project_update_db` (after code generation)

4. **query_project_state()** - SQL-like query interface
   - Flexible filtering, joins, sorting without SQL
   - Primary use: Complex queries, reporting

5. **get_work_context()** - Resume context
   - Complete task + flows + files + functions + interactions
   - Replaces 6-8 separate calls
   - Primary use: `project_auto_resume`

**Finding:**
- These are **ORCHESTRATORS** not in our current registries
- They call our Layer 3 CRUD helpers
- Extremely well-designed with comprehensive examples
- All should have `is_tool: true`

**Recommendation:** ✅ **ADD TO AIFP REGISTRY**
- Add these 5 orchestrators to `helpers_registry_aifp.json`
- Mark as `is_tool: true`, `is_sub_helper: false`
- Category: `"project_orchestrators"`
- After adding, can archive this file

---

## Overlap Analysis with info-helpers-project.txt

### No Direct Overlaps Found

**Why:** The reviewed files describe **orchestrators** (Layer 2) while info-helpers-project.txt describes **CRUD helpers** (Layer 3).

**Example of the distinction:**

#### Layer 2 Orchestrator (from generic-tools-project.md):
```python
get_current_progress(scope="full", detail_level="summary")
# Internally calls 10+ Layer 3 helpers:
# - get_project_metadata()
# - get_completion_path()
# - get_current_stage()
# - get_tasks_by_status()
# - get_milestone_progress()
# - etc.
```

#### Layer 3 CRUD Helpers (from info-helpers-project.txt):
```python
get_project_metadata(project_id)  # Single DB query
get_task(task_id)                  # Single DB query
get_flows_for_task(task_id)       # Single DB query
add_file(name, path, language)    # Single DB insert
```

### Naming Similarities (Not True Overlaps)

Some names appear similar but serve different purposes:

| Reviewed Files (Orchestrator) | Source of Truth (CRUD) | Notes |
|-------------------------------|------------------------|-------|
| `get_project_status()` | `get_project(id)` | Orchestrator vs single record |
| `create_project_blueprint()` | N/A | Workflow helper, not CRUD |
| `init_project_db()` | `add_infrastructure()` | High-level vs specific CRUD |

---

## Missing from info-helpers-project.txt

### AIFP Orchestrators (Should be in AIFP Registry)

**From helper-functions-reference.md:**
1. parse_directive_file
2. validate_user_directive
3. generate_implementation_code
4. detect_dependencies
5. install_dependency
6. activate_directive
7. monitor_directive_execution
8. get_user_directive_status
9. update_directive
10. deactivate_directive

**From generic-tools-mcp.md:**
1. find_directives
2. find_helpers
3. get_system_context
4. query_mcp_relationships

**From generic-tools-project.md:**
1. get_current_progress
2. update_project_state
3. batch_update_progress
4. query_project_state
5. get_work_context

**Total AIFP Orchestrators to Add:** 19 helpers

**Note:** These are NOT database CRUD helpers - they orchestrate multiple CRUD operations and should be in `helpers_registry_aifp.json` (or split into multiple files if extensive).

---

## Useful Content to Preserve

### 1. From helper-functions-reference.md:
- **FP Development Guidelines** (lines 1512-1606)
  - File organization standards
  - Function structure template
  - Error handling standards
  - Testing requirements
- **Location:** Extract to `docs/development/fp-guidelines.md`

### 2. From helper-tool-classification.md:
- **Classification Philosophy:**
  - is_tool: true criteria (generic orchestrators, primary interfaces)
  - is_tool: false criteria (CRUD, sub-helpers, utilities)
  - 20% tool / 80% internal guideline
  - Decision guidelines
- **Location:** Add to REGISTRY_STATUS.md

### 3. From generic-tools-*.md:
- **Comprehensive examples** of how orchestrators work
- **Error handling patterns**
- **Performance notes**
- **Use case documentation**
- **Location:** Extract to orchestrator registry entries as `return_statements` and examples

---

## Consolidation Plan

### Phase 1: Create AIFP Orchestrators Registry ⏳

1. ✅ Create `helpers_registry_aifp.json` (or split into categories) with:
   - 4 MCP orchestrators (from generic-tools-mcp.md)
   - 5 project orchestrators (from generic-tools-project.md)
   - 10 user directive workflow orchestrators (from helper-functions-reference.md)
   - **Total:** 19 new AIFP orchestrator helpers

**Split Strategy (if extensive):**
- Option A: Single file `helpers_registry_aifp.json` (19 helpers - manageable)
- Option B: Category split:
  - `helpers_registry_aifp_mcp.json` (4 helpers)
  - `helpers_registry_aifp_project.json` (5 helpers)
  - `helpers_registry_aifp_user_workflows.json` (10 helpers)
- Option C: Operation split:
  - `helpers_registry_aifp_queries.json` (find_directives, find_helpers, get_system_context, query_mcp_relationships, get_current_progress, query_project_state, get_work_context)
  - `helpers_registry_aifp_mutations.json` (update_project_state, batch_update_progress)
  - `helpers_registry_aifp_workflows.json` (10 user directive workflows)

**Recommendation:** Start with **Option A** (single file) - 19 helpers is very manageable. Can split later if it grows significantly.

### Phase 2: Create Project CRUD Registries ⏳

2. ✅ Create 4 project registry files using info-helpers-project.txt:
   - helpers_registry_project_structure_getters.json (38 helpers)
   - helpers_registry_project_structure_setters.json (38 helpers)
   - helpers_registry_project_workflow_getters.json (45 helpers)
   - helpers_registry_project_workflow_setters.json (46 helpers)

### Phase 3: Extract Useful Content ⏳

3. ✅ Extract and relocate:
   - FP guidelines → `docs/development/fp-guidelines.md`
   - Classification philosophy → add to `REGISTRY_STATUS.md`
   - Orchestrator examples → incorporated into core registry return_statements

### Phase 4: Archive/Delete Old Files ⏳

4. ✅ After consolidation complete:
   - ❌ **DELETE:** `parse_helpers.py` (utility script - obsolete)
   - ❌ **DELETE:** `helper-tool-classification.md` (outdated counts, philosophy preserved)
   - 📦 **ARCHIVE:** `helper-functions-reference.md` (design doc served its purpose)
   - 📦 **ARCHIVE:** `generic-tools-mcp.md` (content moved to core registry)
   - 📦 **ARCHIVE:** `generic-tools-project.md` (content moved to core registry)

**Archive location:** `docs/helpers/archive/` (for historical reference)

---

## Impact on Registry System

### Before (Current State):
- **Core registry:** 33 helpers (directive workflows only)
- **User settings:** 40 helpers
- **User directives getters:** 45 helpers
- **User directives setters:** 33 helpers
- **Total:** 151 helpers

### After (Complete Consolidation):

| Registry File | Count | Type | Database |
|---------------|-------|------|----------|
| **helpers_registry_core.json** | 33 | Directive workflows | N/A |
| **helpers_registry_aifp.json** | 19 | AIFP orchestrators | Multi-DB |
| **helpers_registry_user_settings.json** | 40 | Settings CRUD | user_preferences.db |
| **helpers_registry_user_directives_getters.json** | 45 | User directives READ | user_directives.db |
| **helpers_registry_user_directives_setters.json** | 33 | User directives WRITE | user_directives.db |
| **helpers_registry_project_structure_getters.json** | 38 | Project structure READ | project.db |
| **helpers_registry_project_structure_setters.json** | 38 | Project structure WRITE | project.db |
| **helpers_registry_project_workflow_getters.json** | 45 | Project workflow READ | project.db |
| **helpers_registry_project_workflow_setters.json** | 46 | Project workflow WRITE | project.db |
| **TOTAL** | **337** | | |

### is_tool Distribution (Following 20% Guideline):

| Registry | Total | is_tool=true | % Tools | Notes |
|----------|-------|--------------|---------|-------|
| **Core** | 33 | ~7 | 21% | Directive entry points |
| **AIFP** | 19 | ~17 | 89% | Most orchestrators are tools |
| **User settings** | 40 | ~8 | 20% | Primary interfaces exposed |
| **User directives getters** | 45 | ~9 | 20% | Query tools |
| **User directives setters** | 33 | ~7 | 21% | Mutation tools |
| **Project structure getters** | 38 | ~8 | 21% | Query tools |
| **Project structure setters** | 38 | ~8 | 21% | Mutation tools |
| **Project workflow getters** | 45 | ~9 | 20% | Query tools |
| **Project workflow setters** | 46 | ~9 | 20% | Mutation tools |
| **TOTAL** | **337** | **~82** | **24%** | Slightly above 20% due to orchestrators |

**Note:** AIFP orchestrators have higher tool percentage (89%) because they're designed as primary entry points for MCP. This is expected and correct.

---

## Recommendations Summary

### ✅ KEEP & USE:
- ✅ `info-helpers-project.txt` - Source of truth for CRUD helpers
- ✅ `info-helpers-core.txt` - Source of truth for core helpers
- ✅ `info-helpers-user-settings.txt` - Source of truth for settings helpers
- ✅ `info-helpers-user-custom.txt` - Source of truth for user directive helpers

### 📝 EXTRACT CONTENT THEN ARCHIVE:
- 📝 `helper-functions-reference.md` - Extract 10 workflow orchestrators + FP guidelines
- 📝 `generic-tools-mcp.md` - Extract 4 MCP orchestrators
- 📝 `generic-tools-project.md` - Extract 5 project orchestrators
- 📝 `helper-tool-classification.md` - Extract classification philosophy

### ❌ DELETE:
- ❌ `parse_helpers.py` - Utility script obsolete

### 📦 ARCHIVE (for historical reference):
- Move archived files to `docs/helpers/archive/` after extraction complete

---

## Progress Update

**Date:** 2025-11-27
**Status:** 67% Complete (227/337 helpers)

### ✅ Completed:
1. ✅ **helpers_registry_core.json** (33 helpers)
2. ✅ **helpers_registry_user_settings.json** (40 helpers)
3. ✅ **helpers_registry_user_directives_getters.json** (45 helpers)
4. ✅ **helpers_registry_user_directives_setters.json** (33 helpers)
5. ✅ **helpers_registry_project_structure_getters.json** (38 helpers)
6. ✅ **helpers_registry_project_structure_setters.json** (38 helpers)

### ⏳ Remaining:
1. ⏳ **helpers_registry_project_workflow_getters.json** (45 helpers)
2. ⏳ **helpers_registry_project_workflow_setters.json** (46 helpers)
3. ⏳ **helpers_registry_aifp.json** (19 orchestrators)

### Next Steps:
1. ⏳ Complete workflow helpers (91 helpers remaining)
2. ⏳ Create AIFP orchestrators registry (19 helpers)

### Future Documentation Tasks:
3. ⏳ Extract FP guidelines to docs/development/fp-guidelines.md
4. ⏳ Extract classification philosophy to REGISTRY_STATUS.md
5. ✅ Update progress in documentation files

### Future Cleanup:
6. ⏳ Delete parse_helpers.py
7. ⏳ Archive reviewed .md files to docs/helpers/archive/

---

## Summary

**Key Insight:** No conflicts found! The reviewed files describe **orchestrators** (AIFP-level operations) while the source of truth describes **CRUD helpers** (database operations). These belong in separate registries:

- **AIFP Registry:** Orchestrators that coordinate multiple operations
- **Database Registries:** CRUD helpers that perform single database operations

**Final Registry Structure:**
- 1 core registry (33 directive workflows)
- 1 AIFP orchestrator registry (19 orchestrators)
- 8 database CRUD registries (285 helpers across 4 databases)
- **Total: 10 registry files, 337 helpers**

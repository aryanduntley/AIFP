# Helper Registry Complete Status

**Last Updated:** 2025-11-29
**Status:** ✅ **COMPLETE** - All helpers documented in JSON registries

---

## Registry Files Summary

| Registry File | Helpers | Database | Updated | Status |
|---------------|---------|----------|---------|--------|
| **helpers_registry_core.json** | 36 | aifp_core.db | 2025-11-26 | ✅ Complete |
| **helpers_registry_mcp_orchestrators.json** | 4 | aifp_core.db | 2025-11-29 | ✅ Complete |
| **helpers_registry_user_settings.json** | 43 | user_preferences.db | 2025-11-26 | ✅ Complete |
| **helpers_registry_user_directives_getters.json** | 45 | user_directives.db | 2025-11-26 | ✅ Complete |
| **helpers_registry_user_directives_setters.json** | 33 | user_directives.db | 2025-11-27 | ✅ Complete |
| **helpers_registry_project_core.json** | 5 | project.db | 2025-11-29 | ✅ Complete |
| **helpers_registry_project_structure_getters.json** | 38 | project.db | 2025-11-27 | ✅ Complete |
| **helpers_registry_project_structure_setters.json** | 38 | project.db | 2025-11-27 | ✅ Complete |
| **helpers_registry_project_workflow_getters.json** | 53 | project.db | 2025-11-29 | ✅ Complete |
| **helpers_registry_project_workflow_setters.json** | 37 | project.db | 2025-11-29 | ✅ Complete |
| **helpers_registry_project_orchestrators.json** | 5 | project.db | 2025-11-29 | ✅ Complete |
| **helpers_registry_git.json** | 10 | project.db | 2025-11-29 | ✅ Complete |
| **TOTAL** | **347** | **4 databases** | - | **✅ Complete** |

---

## Breakdown by Database

### aifp_core.db (40 helpers)
**Purpose:** Core MCP database - directive and helper management (READ-ONLY)

**Files:**
- `helpers_registry_core.json` (36 functions)
- `helpers_registry_mcp_orchestrators.json` (4 functions)

**Core Helpers (36):**
- Directive queries (18 functions): get_directive, get_directives_by_category, get_directive_tree, etc.
- Helper queries (10 functions): get_helpers_by_database, get_helpers_for_directive, etc.
- Category queries (5 functions): get_categories, get_category_description, etc.
- Interaction queries (6 functions): get_interactions_for_directive, get_directive_branch, etc.

**MCP Orchestrators (4) - Layer 2 Generic Tools:**
- find_directives: Intelligent directive discovery and matching (intent, keyword, category, exact)
- find_helpers: Helper function discovery by purpose, database, or pattern
- get_system_context: Complete AIFP system state snapshot (directives, helpers, project, health)
- query_mcp_relationships: Directive and helper relationship queries (dependencies, triggers, escalations)

---

### user_preferences.db (43 helpers)
**Purpose:** User settings, preferences, tracking, and AI learning

**File:** `helpers_registry_user_settings.json`

**Categories:**
- Directive preferences (9 functions): get/set/update/delete directive preferences
- User settings (8 functions): get/set/update user-wide settings
- Tracking settings (6 functions): enable/disable opt-in tracking features
- AI interaction log (6 functions): track corrections and learning
- FP flow tracking (6 functions): compliance history (opt-in)
- Issue reports (8 functions): contextual bug reporting (opt-in)

---

### user_directives.db (78 helpers)
**Purpose:** User-defined automation directives (home automation, cloud infrastructure, etc.)

**Files:**
- `helpers_registry_user_directives_getters.json` (45 functions)
- `helpers_registry_user_directives_setters.json` (33 functions)

**Categories:**
- User directives (14 functions): CRUD operations on automation directives
- Directive dependencies (11 functions): manage required packages, APIs, env vars
- Directive executions (9 functions): execution statistics and scheduling
- Directive implementations (10 functions): link directives to generated code
- Helper functions (11 functions): AI-generated project-specific helpers
- Directive relationships (7 functions): trigger dependencies between directives
- Source files (6 functions): track YAML/JSON/TXT directive definitions
- Logging config (5 functions): file-based logging configuration
- Directive helpers junction (5 functions): many-to-many directive-helper mapping

---

### project.db (186 helpers)
**Purpose:** Project state, code structure, tasks, and workflow management

**Files:**
- `helpers_registry_project_core.json` (5 functions)
- `helpers_registry_project_structure_getters.json` (38 functions)
- `helpers_registry_project_structure_setters.json` (38 functions)
- `helpers_registry_project_workflow_getters.json` (53 functions)
- `helpers_registry_project_workflow_setters.json` (37 functions)
- `helpers_registry_project_orchestrators.json` (5 functions)
- `helpers_registry_git.json` (10 functions)

#### Project Core (5 functions)
**Table:** project
**Functions:** create_project, get_project, update_project, blueprint_has_changed, project_update_git_status

#### Structure Helpers (76 functions)
**Tables:** infrastructure, files, functions, types, type_functions, interactions, file_flows

**Getters (38):**
- Infrastructure queries (4 functions)
- File queries (11 functions)
- Function queries (8 functions)
- Type queries (4 functions)
- Type-function associations (5 functions)
- Interaction queries (4 functions)
- File-flow associations (3 functions)

**Setters (38):**
- Infrastructure mutations (3 functions)
- File lifecycle (8 functions: reserve, finalize, update, delete, checksum)
- Function lifecycle (6 functions: reserve, finalize, update, delete)
- Type lifecycle (5 functions: reserve, finalize, update, delete)
- Type-function mutations (2 functions)
- Interaction mutations (3 functions)
- File-flow mutations (2 functions)

#### Workflow Helpers (90 functions)
**Tables:** themes, flows, flow_themes, completion_path, milestones, tasks, subtasks, sidequests, items, notes

**Getters (53):**
- Theme queries (6 functions)
- Flow queries (8 functions)
- Flow-theme associations (3 functions)
- Completion path queries (7 functions)
- Milestone queries (3 functions)
- Task queries (7 functions)
- Subtask queries (4 functions)
- Sidequest queries (5 functions)
- Item queries (4 functions)
- Note queries (5 functions)
- Work context queries (1 function) - Note: get_work_context moved to orchestrators

**Setters (37):**
- Theme mutations (3 functions)
- Flow mutations (3 functions)
- Flow-theme mutations (2 functions)
- Completion path mutations (7 functions: add, update, delete, reorder operations)
- Milestone mutations (3 functions)
- Task mutations (3 functions)
- Subtask mutations (3 functions)
- Sidequest mutations (3 functions)
- Item mutations (3 functions)
- Note mutations (3 functions)

#### Project Orchestrators (5 functions) - Layer 2 Generic Tools
**Purpose:** High-level orchestrator functions for project operations

**Functions:**
- get_current_progress: Status queries with flexible scope (full/task/milestone) and detail levels
- update_project_state: Common state updates (task lifecycle, flow linking, file/function registration)
- batch_update_progress: Atomic multi-item updates with transaction support
- query_project_state: Flexible SQL-like queries with filters, joins, sorting
- get_work_context: Complete work resumption context (task + flows + files + functions + interactions)

#### Git Helpers (10 functions)
**Tables:** work_branches, merge_history, project (git fields)

**Functions:**
- Git status queries (4 functions): get_current_commit_hash, get_current_branch, get_git_status, detect_external_changes
- Branch management (2 functions): create_user_branch, list_active_branches
- Conflict resolution (2 functions): detect_conflicts_before_merge, merge_with_fp_intelligence
- Git sync (2 functions): sync_git_state, get_user_name_for_branch

---

## Verification Against Source Files

### ✅ Core Helpers (info-helpers-core.txt)
**Status:** Complete
**Functions in info file:** 38
**Functions in JSON:** 36
**Note:** 2 functions (get_incomplete_tasks, get_task_files) are correctly placed in project workflow getters, not core

### ✅ User Settings Helpers (info-helpers-user-settings.txt)
**Status:** Complete
**Functions in info file:** 43
**Functions in JSON:** 43
**Match:** Perfect 1:1 match

### ✅ User Directives Helpers (info-helpers-user-custom.txt)
**Status:** Complete
**Functions in info file:** 76
**Functions in JSON:** 78
**Note:** 3 functions mislabeled in info file (documented as "dependencies" but actually "implementations"):
- get_user_directive_dependencies_by_file_path → get_user_directive_implementations_by_file_path ✓
- get_user_directive_dependencies_by_function_name → get_user_directive_implementations_by_function_name ✓
- get_user_directive_dependencies_by_implementation_type → get_user_directive_implementations_by_type ✓

JSON has correct names and categorization.

### ✅ Project Helpers (info-helpers-project.txt)
**Status:** Complete (as of 2025-11-29)
**Functions in info file:** 163
**Functions in JSON:** 182 (includes 10 git + 5 project core + 167 structure/workflow)
**Note:** Info file has 6 typos (completion, infrastructure, interactions spellings) - JSON has correct spellings

**Recently Added (2025-11-29):**
- 5 project core functions → helpers_registry_project_core.json
- 10 git functions → helpers_registry_git.json

---

## Source of Truth

**Registry JSON files are now the official source of truth.**

The following info-helpers files remain as human-readable documentation but JSON registries are authoritative:
- ✅ `docs/helpers/info-helpers-core.txt`
- ✅ `docs/helpers/info-helpers-project.txt`
- ✅ `docs/helpers/info-helpers-user-settings.txt`
- ✅ `docs/helpers/info-helpers-user-custom.txt`

---

## Schema Compliance

All registry files follow the standardized schema:

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "YYYY-MM-DD",
    "description": "Registry purpose and scope",
    "database": "target_database.db",
    "target_database": "database_name",
    "total_helpers": N,
    "schema_version": "1.0",
    "notes": "Additional context"
  },
  "helper_schema": { /* field definitions */ },
  "database": "target_database.db",
  "file_location": "src/aifp/helpers/path/",
  "helpers": [ /* array of helper objects */ ]
}
```

Each helper entry includes:
- name, file_path, database, target_database
- purpose, parameters, return_statements
- error_handling, used_by_directives
- is_tool, is_sub_helper, calls_helpers

---

## Files Requiring Review for Consolidation

**Status:** ⏳ Pending review for overlap/redundancy with registry files

The following documentation files need to be reviewed to determine what should be:
- **Merged** into registries (if missing info)
- **Archived** (if superseded by registries)
- **Removed** (if fully redundant)
- **Kept** (if provides unique value)

### Files to Review:

1. **docs/helpers/helper-architecture.md**
   - Content: Architecture concepts and patterns
   - Action needed: Extract useful concepts, archive or remove file

2. **docs/helpers/helper-tool-classification.md**
   - Content: Helper classification logic (is_tool, is_sub_helper)
   - Action needed: Check if classification logic incorporated into registries, likely archive

3. **docs/helpers/generic-tools-mcp.md**
   - Content: 4 MCP orchestrator tools
   - Action needed: Verify if these are in registry, if not add them

4. **docs/helpers/generic-tools-project.md**
   - Content: 5 project orchestrator tools
   - Action needed: Verify if these are in registry, if not add them

5. **docs/helpers/helper-functions-reference.md**
   - Content: 49 helpers reference (older documentation)
   - Action needed: Likely superseded by registries, verify and remove

6. **docs/directives-json/directive-helper-interactions.json**
   - Content: 62 directive-helper mappings
   - Action needed: Merge into `used_by_directives` fields in registries

7. **docs/directives-json/helpers_parsed.json**
   - Content: 49 helpers (older subset)
   - Action needed: Likely superseded by registries, verify and remove

### Review Process:

For each file:
1. Read current content
2. Compare with registry coverage
3. Identify gaps or unique information
4. Determine action: merge/archive/remove/keep
5. Document decision and rationale

---

## Next Steps

1. ✅ **All helpers documented** - Registry foundation complete (339 helpers)
2. ⏳ **Review consolidation files** - Process 7 files listed above
3. ⏳ **Update registries** - Add any missing helpers/info from reviewed files
4. ⏳ **Create consolidation report** - Document what was added/removed/merged
5. ⏳ **Import to database** - Load final registries into aifp_core.db helper_functions table

---

**Registry Status: ⏳ IN PROGRESS**
**Total Helpers: 347 (8 orchestrators added, may increase after file review)**
**Ready for: File consolidation review, then database import**

# Final AIFP Helper Registry Structure

**Date:** 2025-11-27
**Status:** Design Complete, Implementation Pending

---

## Overview

**Total Registries:** 10 files
**Total Helpers:** 337 helpers
**Total MCP Tools:** ~82 (24%)

---

## Registry Files

### 1. Core Directives
**File:** `helpers_registry_core.json`
**Count:** 33 helpers
**Purpose:** Core AIFP directive workflows and system operations
**Database:** N/A (directives, not database helpers)
**is_tool:** ~7 (21%)

**Examples:**
- Directive execution workflows
- FP compliance directives
- System initialization

---

### 2. AIFP Orchestrators (NEW)
**File:** `helpers_registry_aifp.json`
**Count:** 19 helpers
**Purpose:** High-level orchestrators that coordinate multiple database operations
**Database:** Multi-database (calls helpers from all databases)
**is_tool:** ~17 (89%)

**Categories:**
- **MCP Orchestrators (4):** find_directives, find_helpers, get_system_context, query_mcp_relationships
- **Project Orchestrators (5):** get_current_progress, update_project_state, batch_update_progress, query_project_state, get_work_context
- **User Directive Workflows (10):** parse_directive_file, validate_user_directive, generate_implementation_code, detect_dependencies, install_dependency, activate_directive, monitor_directive_execution, get_user_directive_status, update_directive, deactivate_directive

**Key Characteristics:**
- Almost all are MCP tools (primary AI interfaces)
- Call multiple CRUD helpers per operation
- Provide high-level abstractions for complex workflows

---

### 3. User Settings
**File:** `helpers_registry_user_settings.json`
**Count:** 40 helpers
**Purpose:** User preferences and settings management
**Database:** user_preferences.db
**is_tool:** ~8 (20%)

**Examples:**
- get_setting, set_setting
- get_directive_preference
- get_tracking_settings
- toggle_tracking_feature

---

### 4. User Directives - Getters
**File:** `helpers_registry_user_directives_getters.json`
**Count:** 45 helpers
**Purpose:** READ operations for user directives database
**Database:** user_directives.db
**is_tool:** ~9 (20%)

**Categories:**
- Directive queries (9)
- Execution queries (9)
- Dependency queries (6)
- Implementation queries (6)
- Relationship queries (4)
- Helper function queries (7)
- Directive-helper association queries (4)
- Source file queries (3)
- Logging config queries (2)

---

### 5. User Directives - Setters
**File:** `helpers_registry_user_directives_setters.json`
**Count:** 33 helpers
**Purpose:** WRITE operations for user directives database
**Database:** user_directives.db
**is_tool:** ~7 (21%)

**Categories:**
- Directive mutations (7)
- Execution mutations (3)
- Dependency mutations (3)
- Implementation mutations (3)
- Relationship mutations (3)
- Helper function mutations (3)
- Directive-helper association mutations (3)
- Source file mutations (3)
- Logging config mutations (3)

---

### 6. Project Structure - Getters
**File:** `helpers_registry_project_structure_getters.json`
**Count:** 38 helpers
**Purpose:** READ operations for project code structure
**Database:** project.db
**is_tool:** ~8 (21%)

**Categories:**
- Infrastructure queries
- File queries
- Function queries
- Type queries
- Type-function associations
- Interaction queries
- File-flow associations

**Examples:**
- get_file, get_files, get_files_by_flow
- get_function, get_functions_by_file
- get_type, get_types_by_file
- get_interactions_by_type

---

### 7. Project Structure - Setters
**File:** `helpers_registry_project_structure_setters.json`
**Count:** 38 helpers
**Purpose:** WRITE operations for project code structure
**Database:** project.db
**is_tool:** ~8 (21%)

**Categories:**
- Infrastructure mutations
- File lifecycle (reserve, finalize, update, delete, checksum, timestamp)
- Function lifecycle
- Type lifecycle
- Type-function mutations
- Interaction mutations
- File-flow mutations

**Examples:**
- add_infrastructure, update_infrastructure
- reserve_file, finalize_file, update_file_checksum
- reserve_function, finalize_function
- add_type_function, delete_type_function

---

### 8. Project Workflow - Getters
**File:** `helpers_registry_project_workflow_getters.json`
**Count:** 45 helpers
**Purpose:** READ operations for project workflow and planning
**Database:** project.db
**is_tool:** ~9 (20%)

**Categories:**
- Task queries
- Subtask queries
- Sidequest queries
- Theme queries
- Flow queries
- Milestone queries
- Note queries
- Item queries
- Completion path queries
- Association queries (task-files, task-flows, theme-flows)

**Examples:**
- get_task, get_tasks_by_status, get_incomplete_tasks
- get_subtasks_by_task
- get_theme, get_themes_by_confidence
- get_flows_for_theme, get_themes_for_flow
- get_milestone, get_milestones_by_status

---

### 9. Project Workflow - Setters
**File:** `helpers_registry_project_workflow_setters.json`
**Count:** 46 helpers
**Purpose:** WRITE operations for project workflow and planning
**Database:** project.db
**is_tool:** ~9 (20%)

**Categories:**
- Task mutations
- Subtask mutations
- Sidequest mutations
- Theme mutations
- Flow mutations
- Milestone mutations
- Note mutations
- Item mutations
- Completion path mutations
- Association mutations (add/delete task-files, task-flows, flow-themes)

**Examples:**
- add_task, update_task, delete_task
- add_subtask, update_subtask
- add_theme, update_theme
- add_flow, update_flow
- add_flow_themes, delete_flow_themes
- add_milestone, update_milestone

---

## Registry Statistics

| Registry | Helpers | is_tool | % Tools | Database | Category |
|----------|---------|---------|---------|----------|----------|
| Core | 33 | 7 | 21% | N/A | Directives |
| **AIFP** | **19** | **17** | **89%** | Multi-DB | Orchestrators |
| User Settings | 40 | 8 | 20% | user_preferences.db | Settings CRUD |
| User Directives Getters | 45 | 9 | 20% | user_directives.db | READ |
| User Directives Setters | 33 | 7 | 21% | user_directives.db | WRITE |
| Project Structure Getters | 38 | 8 | 21% | project.db | READ |
| Project Structure Setters | 38 | 8 | 21% | project.db | WRITE |
| Project Workflow Getters | 45 | 9 | 20% | project.db | READ |
| Project Workflow Setters | 46 | 9 | 20% | project.db | WRITE |
| **TOTAL** | **337** | **82** | **24%** | | |

---

## Architectural Layers

### Layer 1: Directives
**Registry:** helpers_registry_core.json
**Purpose:** Define high-level directives and their workflows
**Called by:** AI, users, MCP clients

### Layer 2: Orchestrators
**Registry:** helpers_registry_aifp.json
**Purpose:** Coordinate multiple database operations, provide high-level abstractions
**Called by:** Directives, AI for complex operations
**Calls:** Layer 3 CRUD helpers

### Layer 3: Database CRUD Helpers
**Registries:** All other registries (8 files)
**Purpose:** Direct database operations (add, get, update, delete)
**Called by:** Layer 2 orchestrators, occasionally by directives
**Calls:** Database only

---

## Design Principles

### 1. Separation of Concerns
- **Orchestrators** coordinate and abstract
- **CRUD helpers** perform single database operations
- **No mixing** of layers

### 2. MCP Tool Exposure (is_tool: true)
- ~20% of CRUD helpers are tools (primary interfaces)
- ~89% of orchestrators are tools (designed as entry points)
- Overall: ~24% of all helpers are MCP tools

### 3. Getter/Setter Split
- READ operations separated from WRITE operations
- Clear boundaries for permissions and safety
- Easier to audit and maintain

### 4. Domain Organization
- User preferences vs user directives (different concerns)
- Project structure vs workflow (different data models)
- Core vs AIFP vs Database (different abstraction levels)

---

## Source of Truth Files

All registry files are generated from these source documents:

| Source File | Generates | Helpers |
|-------------|-----------|---------|
| `docs/helpers/info-helpers-core.txt` | helpers_registry_core.json | 33 |
| **`docs/helpers/generic-tools-*.md` + `helper-functions-reference.md`** | **helpers_registry_aifp.json** | **19** |
| `docs/helpers/info-helpers-user-settings.txt` | helpers_registry_user_settings.json | 40 |
| `docs/helpers/info-helpers-user-custom.txt` | helpers_registry_user_directives_*.json | 78 |
| `docs/helpers/info-helpers-project.txt` | helpers_registry_project_*.json | 167 |
| **TOTAL** | | **337** |

---

## Implementation Status

**Last Updated:** 2025-11-27

| Registry | Status | Notes |
|----------|--------|-------|
| helpers_registry_core.json | ✅ Complete | 33/33 helpers |
| helpers_registry_user_settings.json | ✅ Complete | 40/40 helpers |
| helpers_registry_user_directives_getters.json | ✅ Complete | 45/45 helpers |
| helpers_registry_user_directives_setters.json | ✅ Complete | 33/33 helpers |
| **helpers_registry_project_structure_getters.json** | **✅ Complete** | **38/38 helpers** |
| **helpers_registry_project_structure_setters.json** | **✅ Complete** | **38/38 helpers** |
| helpers_registry_project_workflow_getters.json | ⏳ Pending | 0/45 helpers |
| helpers_registry_project_workflow_setters.json | ⏳ Pending | 0/46 helpers |
| **helpers_registry_aifp.json** | ⏳ **Pending** | **0/19 helpers** |

**Progress:** 227/337 (67%)
**Remaining:** 110 helpers (91 workflow + 19 AIFP orchestrators)

---

## Next Steps

1. ⏳ Create `helpers_registry_project_workflow_getters.json` (45 helpers)
2. ⏳ Create `helpers_registry_project_workflow_setters.json` (46 helpers)
3. ⏳ Create `helpers_registry_aifp.json` (19 orchestrators)
4. ⏳ Update `REGISTRY_STATUS.md` with final structure
5. ⏳ Archive/delete old helper documentation files

## Completed Steps

1. ✅ Created `helpers_registry_user_directives_setters.json` (33 helpers)
2. ✅ Created `helpers_registry_project_structure_getters.json` (38 helpers)
3. ✅ Created `helpers_registry_project_structure_setters.json` (38 helpers)
4. ✅ Updated schema with CHECK constraint for target_database
5. ✅ Verified user_directives split (getters + setters = 78 total)
6. ✅ Removed old incomplete registry files

---

## Benefits of This Structure

### For Developers:
- Clear separation between orchestration and CRUD
- Easy to find helpers by database and operation type
- Getter/setter split improves code safety

### For AI:
- High-level orchestrators reduce API calls
- Clear abstraction layers
- Well-documented return_statements guide workflows

### For Maintenance:
- Single source of truth per domain
- Easy to validate completeness
- Clear upgrade paths (add to AIFP for new orchestrators)

### For MCP Integration:
- ~82 tools exposed (optimal for discoverability)
- Clear tool vs internal helper distinction
- Orchestrators provide best AI experience

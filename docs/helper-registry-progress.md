# Helper Registry Project - Progress & Status

**Date Started**: 2025-11-26
**Last Updated**: 2025-11-26
**Session**: 1

## Project Goal

Create comprehensive JSON registry files for all AIFP helper functions across 4 databases, replacing scattered documentation with a single source of truth for database import.

---

## Key Decisions Made

### 1. **File Structure - Split by Database**
- **Decision**: Split helpers into separate files by database instead of one monolithic file
- **Why**: Easier to manage, clearer organization, better for future maintenance
- **Files Created**:
  - `helpers_registry_core.json` - MCP database (aifp_core.db)
  - `helpers_registry_project.json` - Project database (project.db)
  - `helpers_registry_user_settings.json` - User preferences database (user_preferences.db)
  - `helpers_registry_user_directives_getters.json` - User directives READ operations
  - `helpers_registry_user_directives_setters.json` - User directives WRITE operations (pending)

### 2. **Further Split User Directives**
- **Decision**: Split user_directives into getters/setters files
- **Why**: User directives has 78 helpers - too large for single file. Logical split by operation type.
- **Note**: Can further split with numbered files (1, 2, 3) if still too large

### 3. **Return Statements Purpose**
- **Original Misunderstanding**: Initially designed as type definitions/schema
- **Correct Purpose**: AI behavioral guidance - what to check/do NEXT after calling helper
- **Content**:
  - Conditional logic suggestions
  - Directive chaining recommendations
  - Validation checks to perform
  - Helper chaining guidance
  - FP flow reminders
  - User interaction expectations
- **Format**: Array of simple strings (flexible, no predefined keys needed)

### 4. **Metadata Standards**
- Removed `sources` field - these are production files for DB import, not dev docs
- Use full database names: `aifp_core.db`, `project.db`, `user_preferences.db`, `user_directives.db`
- Each registry includes schema documentation and total helper count

### 5. **Helper Function Classification**
- `is_tool`: Boolean - MCP-exposed tools (primary entry points for AI)
- `is_sub_helper`: Boolean - Internal utilities called by other helpers (AI shouldn't call directly)
- Regular helpers: Neither tool nor sub-helper (AI can call when needed)

### 6. **Source of Truth Hierarchy**
1. **Primary**: `info-helpers-*.txt` files (4 files - core, project, user-settings, user-custom)
2. **Secondary**: `helpers_parsed.json` (older, 49 helpers - subset of info-helpers)
3. **Tertiary**: Other docs to be consolidated/archived after merge

---

## Completed Work

### ✅ Core Registry (33 helpers - COMPLETE)
**File**: `docs/helpers/registry/helpers_registry_core.json`

**Categories**:
- Directive Queries (9): get_directive, get_directive_by_name, get_directives, etc.
- Category Queries (6): get_categories, get_directives_by_category, etc.
- Interaction Queries (5): get_interactions_for_directive, etc.
- Helper Queries (9): get_helper_by_name, get_helpers_by_database, etc.
- Directive-Helper Queries (2): get_helpers_for_directive, get_directives_for_helper
- Hierarchy Navigation (4): get_directive_tree, get_directive_branch, etc.

**Notes**: All read-only, fully documented with return_statements

### ✅ User Settings Registry (40 helpers - COMPLETE)
**File**: `docs/helpers/registry/helpers_registry_user_settings.json`

**Categories**:
- Settings Management (6 TOOLS): add_setting, get_all_settings, update_setting, etc.
- Directive Preference Management (9 TOOLS): add_directive_preference, get_directive_preferences_by_directive, etc.
- AI Interaction Logging (5 HELPERS): add_ai_interaction, get_ai_interactions_by_type, etc.
- FP Tracking (8 HELPERS): add_fp_tracking, get_fp_tracking_by_function, etc.
- Issue Reporting (7 HELPERS): add_issues_report, get_issues_reports_by_directive, etc.
- Tracking Management (5 HELPERS): add_tracking_setting, get_tracking_settings_enabled, etc.

**Notes**: Mix of TOOLS (MCP-exposed) and HELPERS (internal), all with complete return_statements

### ✅ User Directives Getters (45 helpers - COMPLETE)
**File**: `docs/helpers/registry/helpers_registry_user_directives_getters.json`

**Categories**:
- Directive Queries (8): get_user_directive, get_user_directives_by_status, etc.
- Execution Queries (8): get_user_directive_executions_by_directive, get_user_directive_executions_by_error_count, etc.
- Dependency Queries (6): get_user_directive_dependencies_by_directive, get_user_directive_dependencies_by_required, etc.
- Implementation Queries (5): get_user_directive_implementations_by_directive, get_user_directive_implementations_by_type, etc.
- Relationship Queries (4): get_user_directive_relationships_by_source, get_user_directive_relationships_by_target, etc.
- Helper Queries (7): get_user_helper_function, get_user_helper_functions_by_purity, etc.
- Directive-Helper Queries (4): get_user_directive_helpers_by_directive, get_user_directive_helpers_by_function, etc.
- Source File Queries (3): get_user_source_file, get_user_source_files_by_parse_status, etc.
- Logging Queries (2): get_user_logging_config, get_all_user_logging_config

**Notes**: Emphasizes AI freedom to write custom queries for user_directives.db

### ✅ Project Registry (9 helpers - PARTIAL)
**File**: `docs/helpers/registry/helpers_registry_project.json`

**Status**: Only initial setup helpers included (create_project_directory, initialize_project_db, get_project_status, etc.)

**Remaining**: ~150+ CRUD helpers for tasks, files, functions, flows, types, milestones, etc.

---

## Pending Work

### 🔄 User Directives Setters (~33 helpers)
**File**: `docs/helpers/registry/helpers_registry_user_directives_setters.json` (NOT YET CREATED)

**What's Needed**:
- All add_* functions (8 tables)
- All update_* functions (8 tables)
- All delete_* functions (8 tables)
- All set_* functions (status setters: approved, validated, activated, modified)

**Tables to Cover**:
1. user_directives (add, update, delete, set_approved, set_validated, set_modified, set_activate)
2. directive_executions (add, update, delete)
3. directive_dependencies (add, update, delete)
4. directive_implementations (add, update, delete)
5. directive_relationships (add, update, delete)
6. helper_functions (add, update, delete)
7. directive_helpers (add, update, delete)
8. source_files (add, update, delete)
9. logging_config (add, update, delete)

### 🔄 Project Registry Expansion (~150+ helpers)
**File**: `docs/helpers/registry/helpers_registry_project.json`

**Status**: Only 9 setup/status helpers complete

**What's Needed** (from `info-helpers-project.txt`):
- **Tasks**: add_task, get_task, get_tasks_by_milestone, get_incomplete_tasks, update_task, delete_task, etc.
- **Subtasks**: add_subtask, get_subtasks_by_task, get_incomplete_subtasks, etc.
- **Sidequests**: add_sidequest, get_sidequests_by_flow, get_incomplete_sidequests, etc.
- **Files**: add_file, get_file, get_files_by_flow, reserve_file, finalize_file, update_file, delete_file, etc.
- **Functions**: add_function, get_function_by_name, get_functions_by_file, reserve_function, finalize_function, update_function, delete_function, etc.
- **Types**: add_type, get_types_by_file, reserve_type, finalize_type, update_type, delete_type, etc.
- **Flows**: add_flow, get_flow, get_flows_by_confidence, get_flows_for_file, update_flow, delete_flow, etc.
- **Themes**: add_theme, get_themes_for_flow, etc.
- **Milestones**: add_milestone, get_milestones_by_status, update_milestone, delete_milestone, etc.
- **Completion Paths**: add_completion_path, get_completion_paths, reorder_completion_paths, etc.
- **File Flows**: add_file_flows, get_files_by_flow_context, delete_file_flow, etc.
- **Notes**: add_note, get_notes_comprehensive, search_notes, update_note, delete_note, etc.
- **Infrastructure**: add_infrastructure, get_infrastructure_by_type, etc.
- **Interactions**: add_interaction, get_all_interactions, etc.

**Strategy**: Break into phases or numbered files due to size

### 🔄 AIFP System-Level Registry
**File**: `docs/helpers/registry/helpers_registry_aifp.json` (NOT YET CREATED)

**Purpose**: System-level helpers that don't operate on specific databases

**Categories to Include**:
- **Option A**: System utilities (logging, configuration, session management, file system)
- **Option B**: Cross-database orchestrators (coordinate across multiple DBs)
- **Option C**: Core AIFP framework helpers (bootstrap, MCP setup, diagnostics)
- **Decision**: Include all three options - won't be a massive number of helpers

**Sources to Review**:
- `docs/helpers/generic-tools-mcp.md` (4 orchestrator tools)
- `docs/helpers/generic-tools-project.md` (5 orchestrator tools)
- Any system-level helpers from `helpers_parsed.json` not in other categories

---

## Files to Consolidate/Archive After Completion

Once all registries are complete, these files can be archived or removed to avoid confusion:

### Primary Consolidation Targets:
- `docs/helpers/helper-architecture.md` - Architecture concepts (keep useful parts in main docs)
- `docs/helpers/helper-tool-classification.md` - Classification logic (incorporated into registries)
- `docs/helpers/generic-tools-mcp.md` - 4 tools (merge into AIFP registry)
- `docs/helpers/generic-tools-project.md` - 5 tools (merge into AIFP registry)
- `docs/helpers/helper-functions-reference.md` - 49 helpers (superseded by registries)
- `docs/directives-json/directive-helper-interactions.json` - 62 mappings (needs to be merged into registries)
- `docs/directives-json/helpers_parsed.json` - 49 helpers (superseded by registries)

### Keep as Source of Truth:
- `docs/helpers/info-helpers-core.txt` ✅
- `docs/helpers/info-helpers-project.txt` ✅
- `docs/helpers/info-helpers-user-settings.txt` ✅
- `docs/helpers/info-helpers-user-custom.txt` ✅

---

## Next Steps (Priority Order)

1. **Create `helpers_registry_user_directives_setters.json`** (~33 helpers)
   - Complete the user_directives split
   - Add all add_*, update_*, delete_*, set_* functions
   - Emphasize AI flexibility in return_statements

2. **Review & Merge `directive-helper-interactions.json`**
   - Add directive associations to `used_by_directives` fields across all registries
   - This maps which directives use which helpers

3. **Create `helpers_registry_aifp.json`**
   - System-level and cross-database helpers
   - Merge generic-tools-*.md content
   - Should be relatively small (~10-15 helpers)

4. **Expand Project Registry (Phase 1 - Most Used)**
   - Tasks, Subtasks, Sidequests (core workflow)
   - ~30-40 helpers
   - Create `helpers_registry_project_tasks.json`

5. **Expand Project Registry (Phase 2 - File Management)**
   - Files, Functions, Types
   - ~40-50 helpers
   - Create `helpers_registry_project_files.json`

6. **Expand Project Registry (Phase 3 - Organization)**
   - Flows, Themes, Milestones, Completion Paths
   - ~40-50 helpers
   - Create `helpers_registry_project_organization.json`

7. **Expand Project Registry (Phase 4 - Support)**
   - Notes, Infrastructure, Interactions, etc.
   - ~30-40 helpers
   - Create `helpers_registry_project_support.json`

8. **Final Review & Cleanup**
   - Review all return_statements for accuracy
   - Verify all directive associations are correct
   - Archive/remove old documentation files
   - Create sync scripts (sync-directives.py, sync-helpers.py, etc.)

---

## Important Notes for Future Sessions

### Return Statements Philosophy
- **NOT type definitions** - the code handles types
- **IS behavioral guidance** - reminders for AI on what to do next
- Examples:
  - "If initialized=false, escalate to project_init directive"
  - "Verify flows are added for this file in file_flows table if necessary"
  - "Check is_required flag - required helpers must be called"
  - "Follow chain of severity: sidequests → subtasks → tasks"

### User Directives Special Nature
- AI has freedom to write custom SQL queries for user_directives.db
- Helpers are guides, not constraints
- Emphasize this in return_statements: "AI is encouraged to write custom queries if helpers don't satisfy needs"
- User directives flow: user file → AI parsing & clarification → validated directives → implementation → activation

### Database Name Standards
- Always use full names: `aifp_core.db`, `project.db`, `user_preferences.db`, `user_directives.db`
- These are production files for database import, not dev docs
- No references to source files (info-helpers-*.txt) in the JSON

### File Splitting Strategy
If any registry file exceeds ~1500 lines:
1. First try: Split by operation type (getters/setters)
2. If still too large: Number the splits (1, 2, 3, etc.)
3. Keep clear naming: `helpers_registry_{database}_{category}_{number}.json`

---

## Session Summary

**Total Helpers Documented**: 127 of ~300+
- Core: 33/33 ✅
- User Settings: 40/40 ✅
- User Directives Getters: 45/78 ✅
- User Directives Setters: 0/33 ⏳
- Project: 9/150+ ⏳
- AIFP: 0/10-15 ⏳

**Completion**: ~40% of total helpers documented

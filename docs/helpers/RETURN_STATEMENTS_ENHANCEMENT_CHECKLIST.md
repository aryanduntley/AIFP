# Helper Return_Statements Enhancement Checklist

**Purpose**: Enhance all helper function `return_statements` fields with rich conceptual feedback including next steps, checks, related helpers, directive flows, and database implications.

**🎯 QUALITY STANDARD:** See [RETURN_STATEMENTS_QUALITY_GUIDE.md](./RETURN_STATEMENTS_QUALITY_GUIDE.md) for comprehensive quality criteria, examples, and enhancement process. **Reference this guide in every session.**

**Status Legend**:
- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed (initial enhancement)
- `[✓]` Reviewed (assessed against stability principles)

---

## Progress Overview - Session 4: 2025-12-30 - FINAL

**Total Helpers**: 202
**Properly Completed**: 36 helpers (18%)
**Remaining Work**: 79 helpers
**Untouched (Clean)**: 87 helpers

---

### ✅ VERIFIED COMPLETE (36 helpers)

**helpers-project-1.json: ALL 15 helpers COMPLETED** ✅
- ✅ 5 helpers WITH directives (create_project, get_project, update_project, blueprint_has_changed, get_infrastructure_by_type)
- ✅ 10 helpers WITHOUT directives (generic CRUD - verified no hardcoded names)
- Status: All helpers use conceptual references, no hardcoded function names, stability verified

**helpers-project-2.json: ALL 10 helpers COMPLETED** ✅
- ✅ reserve_file, reserve_files (directives)
- ✅ finalize_file, finalize_files (directives)
- ✅ get_file_by_name, get_file_by_path (directives added)
- ✅ update_file, file_has_changed (directives added)
- ✅ update_file_timestamp
- ✅ delete_file (directives added + implementation_notes separated with ERROR-first)
- Status: All 6 helpers with directives have proper DIRECTIVE CONTEXT

**helpers-project-3.json: ALL 10 helpers COMPLETED** ✅
- ✅ reserve_function, reserve_functions (directives)
- ✅ finalize_function, finalize_functions (directives added)
- ✅ get_function_by_name, get_functions_by_file (directives added)
- ✅ update_function, update_functions_for_file (directives added)
- ✅ update_function_file_location
- ✅ delete_function (directives added + implementation_notes separated with ERROR-first)
- Status: All 6 helpers with directives have proper DIRECTIVE CONTEXT

**helpers-project-4.json: 1 of 13 helpers completed**
- ✅ delete_type (implementation_notes separated with ERROR-first approach)

---

### 🔄 PARTIAL/NEEDS WORK (16 helpers in touched files)

**helpers-project-4.json: 12 helpers remaining**
- Need: 9 helpers WITH directives - add DIRECTIVE CONTEXT
  - reserve_type ✅ (already has directives)
  - finalize_type ✅ (already has directives)
  - add_interaction ✅ (already has directives)
  - reserve_types, finalize_types, update_type
  - add_types_functions, update_type_function_role, delete_type_function
  - add_interactions, update_interaction, delete_interaction
- Need: 3 helpers WITHOUT directives - stability review
  - reserve_types, finalize_types (likely batch operations)
  - add_interactions (likely batch operation)

---

### ❓ UNKNOWN STATUS - NEEDS VERIFICATION (63 helpers)

**helpers-project-5.json: 11 helpers**
- 6 with directives (unknown if DIRECTIVE CONTEXT exists)
- 5 without directives (unknown if stable)

**helpers-project-6.json: 14 helpers**
- 6 with directives (unknown if DIRECTIVE CONTEXT exists)
- 8 without directives (unknown if stable)

**helpers-project-7.json: 15 helpers**
- 7 with directives (unknown if DIRECTIVE CONTEXT exists)
- 8 without directives (8 marked "scripted generically")

**helpers-git.json: 11 helpers** (previously marked "VERIFIED")
- 10 with directives (unknown if DIRECTIVE CONTEXT exists)
- 1 without directives (unknown if stable)

**helpers-orchestrators.json: 12 helpers** (previously marked "VERIFIED")
- 4 with directives (unknown if DIRECTIVE CONTEXT exists)
- 8 without directives (unknown if stable)

---

### 🆕 UNTOUCHED - CLEAN SLATE (87 helpers)

- helpers-core.json: 33 helpers
- helpers-project-8.json: 14 helpers
- helpers-project-9.json: 10 helpers
- helpers-settings.json: 17 helpers
- helpers-user-custom.json: 16 helpers
- helpers-index.json: 1 helper

**Quality Standard:** See [RETURN_STATEMENTS_QUALITY_GUIDE.md](./RETURN_STATEMENTS_QUALITY_GUIDE.md) for detailed criteria

---

## Enhancement Pattern Template

### Important Notes

**CRITICAL: What NOT to Include in return_statements**

🚨 **DO NOT waste AI's time with redundant information!** 🚨

The AI **ALREADY KNOWS**:
- What function it just called (it literally just used it!)
- Why it called this function (it made that decision)
- What this function does (it read the purpose/description before calling)
- What the return value structure is (it sees actual return data when function executes)

**NEVER include in return_statements**:
- ❌ "RETURN: Returns {success: true, id: int}" - AI sees actual return when function executes!
- ❌ "This function creates a file..." - AI already knows, it just called this function!
- ❌ "Used to reserve a file ID..." - AI already read the purpose field!
- ❌ Descriptions of what the current function does - redundant and wasteful!

**ALWAYS include in return_statements**:
- ✅ NEXT STEP: What to do AFTER this function completes
- ✅ CHECK: Validations/questions to consider before/after execution
- ✅ RELATED HELPERS: Other functions to call in workflow sequence
- ✅ DIRECTIVE: Which directives use this (saves AI from querying)
- ✅ DIRECTIVE FLOW: What comes next in directive sequence (saves processing time)
- ✅ WORKFLOW: Multi-step process context (helps AI understand broader context)
- ✅ DATABASE CONTEXT: Implications for database state (what changed, what to check)
- ✅ WARNING: For destructive operations or common pitfalls

**Key Principle**: return_statements are **FORWARD-LOOKING** guidance, not **BACKWARD-LOOKING** descriptions!

Think of it as: "You just called this function, here's what you should know for your NEXT action"

**CRITICAL: Specificity Requirement** 🎯

Generic guidance is **NOT USEFUL**. The goal is to **MINIMIZE AI's need for follow-up database lookups** by providing concrete, actionable information.

**❌ BAD (Generic - Not Helpful):**
- "Use to understand which files need modification"
- "Helps identify relevant code areas"
- "Useful for progress tracking"
- "Check returned data for next steps"

**✅ GOOD (Specific - Actionable):**
- "Use get_files_by_flow(flow_id) where flow_id from this result's flow_ids JSON array"
- "Check result.status field: 'pending' → can start work, 'blocked' → resolve dependencies first, 'completed' → move to next task"
- "If returned array empty, call update_milestone(milestone_id, status='completed') to mark milestone done"
- "After creating task, call add_subtask(task_id, name, description) if task needs decomposition"

**Specificity Checklist:**
- ✅ Use exact function names (not "related helpers")
- ✅ Use exact parameter names and values (not "appropriate parameters")
- ✅ Use exact field names from database (not "relevant fields")
- ✅ Use exact status values (not "correct status")
- ✅ Reference actual directive names from used_by_directives field
- ✅ Provide concrete conditional logic (if X then Y)

**Why This Matters:**
Without specific guidance, AI must make 3-5 additional queries:
1. Query to understand what fields exist
2. Query to understand valid status values
3. Query to find related helpers
4. Query directive flow for next steps
5. Query examples/patterns

With specific guidance, AI can proceed directly to next action.

**Return VALUES vs return_statements**:
- `return_statements` are conceptual guidance/feedback (what we're enhancing)
- Actual return VALUES (data structures) are handled in code implementation
- Add implementation hints in separate `implementation_notes` field (not imported to database)

**Using used_by_directives Field for Context**:

When a helper has a `used_by_directives` field populated:
1. **Review the directive JSON file**: `docs/directives-json/directive_*.json` - understand the directive's purpose and execution context
2. **Review the directive_flow file**: `docs/directives-json/directive_flow_*.json` - understand what comes BEFORE and AFTER this directive
3. **Include this context in return_statements**: Saves AI processing time by providing directive flow navigation upfront
4. **Example**: If `used_by_directives` shows `project_reserve_finalize`, review:
   - `directive_flow_project.json` to see: `project_file_write → project_reserve_finalize → project_update_db`
   - Include in return_statements: "DIRECTIVE FLOW: project_reserve_finalize → project_update_db → aifp_status"

**Why this matters**: AI would otherwise need to:
- Query core.db for directive information
- Read directive JSON file
- Read directive_flow JSON file
- Conceptualize next steps

By providing this in return_statements, we save AI 3-4 tool calls and processing time!

**Generic Getter/Setters**: Special handling for database CRUD operations (get_from_*, add_*_entry, update_*_entry, etc.)
- Keep return_statements generic but informative
- Focus on general database usage patterns
- Suggest related helpers for common workflows
- Reference directive_flow for next steps
- Provide schema/helper lists for the database
- Example: "RELATED: Use get_project_schema() to see available tables and fields for this database"

### Standard Helper Enhancement Pattern

Each helper's `return_statements` should include (NO redundant return value descriptions):

1. **NEXT STEP** - Immediate next action(s) to take
2. **CHECK** - Validation questions to ask
3. **RELATED HELPERS** - Other helpers in the workflow
4. **WORKFLOW** - Multi-step process context
5. **DIRECTIVE** - Which directives use this (from used_by_directives)
6. **DIRECTIVE FLOW** - What comes next (from directive_flow_*.json)
7. **DATABASE CONTEXT** - Table/relationship implications
8. **WARNING** - For potentially destructive operations

**IMPORTANT**: Do NOT include "RETURN: ..." lines - AI sees actual return values when function executes

### Generic Getter/Setter Enhancement Pattern

For database CRUD helpers (get_from_*, query_*, add_*_entry, update_*_entry, delete_*_entry):

1. **DATABASE CONTEXT** - General usage patterns for this database
2. **NEXT STEP** - What to do with results/after operation
3. **RELATED HELPERS** - Common helper combinations for this database
4. **SCHEMA HELPERS** - Point to schema/table/field helpers for this database
5. **DIRECTIVE CONTEXT** - Which directives commonly use this database
6. **DIRECTIVE FLOW** - General workflow patterns (from directive_flow_*.json)
7. **COMMON WORKFLOWS** - Typical use cases for this database operation
8. **WARNING** - For delete/update operations

**IMPORTANT**: Do NOT include "RETURN: ..." lines - AI sees actual return values when function executes

### Example: Standard Helper Enhancement

**Before**:
```json
"return_statements": [
  "Reserved file ID for naming"
]
```

**After**:
```json
"return_statements": [
  "NEXT STEP: Create file with reserved ID in name (use -IDxxx suffix), then call finalize_file() to complete registration",
  "NEXT STEP: After file creation, reserve functions with reserve_function() for functions in this file",
  "CHECK: Ensure the file is actually created before calling finalize_file()",
  "CHECK: Does this file need flow assignments in file_flows table?",
  "RELATED: finalize_file() to complete reservation after file created",
  "RELATED: reserve_function() for functions in this file",
  "WORKFLOW: reserve_file() → create file → write code → finalize_file() → reserve_function() → finalize_function()",
  "DIRECTIVE: Used by project_reserve_finalize directive (sequence_order: 1)",
  "DIRECTIVE FLOW: project_reserve_finalize → project_update_db → aifp_status",
  "DATABASE: Creates entry in files table with is_reserved=1, no checksum yet"
]
```

### Example: Generic Getter Enhancement

**Before (get_from_project)**:
```json
"return_statements": [
  "Array of records"
]
```

**After (get_from_project)**:
```json
"return_statements": [
  "DATABASE CONTEXT: project.db tracks files, functions, tasks, milestones, themes, flows, completion paths, notes",
  "DATABASE CONTEXT: Most writes happen through directives (project_file_write, project_task_complete, etc.), not direct CRUD",
  "RELATED HELPERS: Use get_project_schema() to see all tables and fields available",
  "RELATED HELPERS: Use get_project_tables() for table list, get_project_fields(table) for field details",
  "RELATED HELPERS: Prefer specialized helpers over generic queries (get_file_by_name vs get_from_project('files', ...))",
  "SCHEMA HELPERS: get_project_schema(), get_project_tables(), get_project_fields(table), get_project_json_parameters(table)",
  "DIRECTIVE CONTEXT: Project directives use this for queries: aifp_status, project_file_write, project_task_complete, project_update_db",
  "DIRECTIVE FLOW: Query operations typically used within directives → results inform next directive via directive_flow",
  "DIRECTIVE FLOW: See directive_flow_project.json for complete workflow navigation",
  "COMMON WORKFLOWS: Status checks → task queries → file lookups → function dependency tracking",
  "WARNING: Empty array required (not allowed) - must pass at least one ID to prevent accidental full table scans"
]
```

---

## helpers-core.json (33 helpers)

**Focus**: MCP database queries, directive lookups, helper metadata

### Batch 1 (Database Schema Helpers) - 7 helpers
- [ ] get_core_tables
- [ ] get_core_fields
- [ ] get_core_schema
- [ ] get_from_core
- [ ] get_from_core_where
- [ ] query_core
- [ ] get_directive_by_name

### Batch 2 (Directive Queries) - 7 helpers
- [ ] get_all_directives
- [ ] get_directive_content
- [ ] search_directives
- [ ] find_directive_by_intent
- [ ] find_directives_by_intent_keyword
- [ ] get_directives_with_intent_keywords
- [ ] add_directive_intent_keyword

### Batch 3 (Directive Keywords & Navigation) - 7 helpers
- [ ] remove_directive_intent_keyword
- [ ] get_directive_keywords
- [ ] get_all_directive_keywords
- [ ] get_all_intent_keywords_with_counts
- [ ] get_next_directives_from_status
- [ ] get_matching_next_directives
- [ ] get_completion_loop_target

### Batch 4 (Directive Navigation & Helpers) - 7 helpers
- [ ] get_conditional_work_paths
- [ ] get_helper_by_name
- [ ] get_helpers_by_database
- [ ] get_helpers_are_tool
- [ ] get_helpers_not_tool_not_sub
- [ ] get_helpers_are_sub
- [ ] get_helpers_for_directive

### Batch 5 (Helper/Directive Relationships & Categories) - 5 helpers
- [ ] get_directives_for_helper
- [ ] get_category_by_name
- [ ] get_categories
- [ ] get_directives_by_category
- [ ] get_directives_by_type

**Notes**: Core database is read-only, focus on navigation and directive flow guidance in return_statements

---

## helpers-project-1.json (15 helpers) ✅ REVIEWED

**Focus**: Database schema queries, generic CRUD operations, project metadata management

**Range**: Helpers 1-15 of 112

**Status**: ✅ All helpers reviewed for stability - directive context verified

**Helpers (Review Status)**:
- [✓] get_project_tables - Revised (removed hardcoded function names, conceptual guidance)
- [✓] get_project_fields - Revised (field metadata context)
- [✓] get_project_schema - Revised (minimal, cache-focused)
- [✓] get_project_json_parameters - Revised (CRUD template context, specialization warnings)
- [✓] get_from_project - Revised (constraint-focused, no hardcoded names)
- [✓] get_from_project_where - Revised (AND-logic context, no hardcoded helpers)
- [✓] query_project - Revised (complex SQL guidance, no hardcoded helpers)
- [✓] add_project_entry - Revised (generic insert context, reserve/finalize workflow)
- [✓] update_project_entry - Revised (partial update context, cascade checks)
- [✓] delete_project_entry - Revised (audit trail context, relationship validation)
- [✓] create_project - Revised (directive context: project_init, sequence_order 1)
- [✓] get_project - Revised (directive context: project_blueprint_read/update)
- [✓] update_project - Revised (directive context: project_blueprint_update, seq 2)
- [✓] blueprint_has_changed - Revised (directive context: blueprint read/update pre-checks)
- [✓] get_infrastructure_by_type - Revised (directive context: project_init infrastructure population)

---

## helpers-project-2.json (10 helpers) ✅ COMPLETE

**Focus**: File reservation, finalization, and management operations

**Range**: Helpers 16-25 of 112

**Status**: return_statements enhanced - ready for review

**Helpers**:
- reserve_file, reserve_files, finalize_file, finalize_files
- get_file_by_name, get_file_by_path
- update_file, file_has_changed, update_file_timestamp, delete_file

---

## helpers-project-3.json (10 helpers) ✅ COMPLETE

**Focus**: Function reservation, finalization, and management operations

**Range**: Helpers 26-35 of 112

**Status**: return_statements enhanced - ready for review

**Helpers**:
- reserve_function, reserve_functions, finalize_function, finalize_functions
- get_function_by_name, get_functions_by_file
- update_function, update_functions_for_file, update_function_file_location, delete_function

---

## helpers-project-4.json (13 helpers)

**Focus**: Type reservation/finalization, type-function relationships, and interaction management

**Range**: Helpers 36-48 of 112

**Status**: Needs return_statements enhancement

**Helpers**: reserve_type, reserve_types, finalize_type, finalize_types, update_type, delete_type, add_types_functions, update_type_function_role, delete_type_function, add_interaction, add_interactions, update_interaction, delete_interaction

---

## helpers-project-5.json (11 helpers)

**Focus**: Theme and flow management operations (add, get, update, delete, relationships)

**Range**: Helpers 49-59 of 112

**Status**: Needs return_statements enhancement

**Helpers**: get_theme_by_name, get_flow_by_name, get_all_themes, get_all_flows, add_theme, update_theme, delete_theme, add_flow, update_flow, delete_flow, get_file_ids_from_flows

---

## helpers-project-6.json (14 helpers)

**Focus**: Flow-theme relationships, file-flow relationships, and completion path management

**Range**: Helpers 60-73 of 112

**Status**: Needs return_statements enhancement

**Helpers**: get_flows_for_theme, get_themes_for_flow, get_files_by_flow, get_flows_for_file, add_completion_path, get_all_completion_paths, get_next_completion_path, get_completion_paths_by_status, get_incomplete_completion_paths, update_completion_path, delete_completion_path, reorder_completion_path, reorder_all_completion_paths, swap_completion_paths_order

---

## helpers-project-7.json (15 helpers)

**Focus**: Milestone and task management operations (add, get, update, delete, queries)

**Range**: Helpers 74-88 of 112

**Status**: Needs return_statements enhancement

**Helpers**: add_milestone, get_milestones_by_path, get_milestones_by_status, get_incomplete_milestones, update_milestone, delete_milestone, add_task, get_incomplete_tasks_by_milestone, get_incomplete_tasks, get_tasks_by_milestone, get_tasks_comprehensive, get_task_flows, get_task_files, update_task, delete_task

---

## helpers-project-8.json (14 helpers)

**Focus**: Subtask and sidequest management operations (add, get, update, delete, queries)

**Range**: Helpers 89-102 of 112

**Status**: Needs return_statements enhancement

**Helpers**: add_subtask, get_incomplete_subtasks, get_incomplete_subtasks_by_task, get_subtasks_by_task, get_subtasks_comprehensive, update_subtask, delete_subtask, add_sidequest, get_incomplete_sidequests, get_sidequests_comprehensive, get_sidequest_flows, get_sidequest_files, update_sidequest, delete_sidequest

---

## helpers-project-9.json (10 helpers)

**Focus**: Item and note management operations (add, get, update, delete, search)

**Range**: Helpers 103-112 of 112

**Status**: Needs return_statements enhancement

**Helpers**: get_items_for_task, get_items_for_subtask, get_items_for_sidequest, get_incomplete_items, delete_item, add_note, get_notes_comprehensive, search_notes, update_note, delete_note

---

## helpers-settings.json (17 helpers)

**Focus**: User preferences, directive preferences, tracking toggles

### Batch 1 (Database Schema & CRUD) - 7 helpers
- [ ] get_settings_tables
- [ ] get_settings_fields
- [ ] get_settings_schema
- [ ] get_settings_json_parameters
- [ ] get_from_settings
- [ ] get_from_settings_where
- [ ] query_settings

### Batch 2 (Settings CRUD & Preferences) - 7 helpers
- [ ] add_settings_entry
- [ ] update_settings_entry
- [ ] delete_settings_entry
- [ ] load_directive_preferences
- [ ] add_directive_preference
- [ ] get_user_setting
- [ ] update_user_preferences

### Batch 3 (Preferences Application & Tracking) - 3 helpers
- [ ] apply_preferences_to_context
- [ ] get_tracking_settings
- [ ] toggle_tracking_feature

**Notes**:
- Preferences loaded via user_preferences_sync directive before customizable directives
- Tracking features are OPT-IN ONLY - warn about token costs
- Atomic key-value structure: directive_name.preference_key = value

---

## helpers-git.json (11 helpers)

**Focus**: Git integration, external change detection, FP-powered merging

### Batch 1 (Git Status & Detection) - 6 helpers
- [x] get_current_commit_hash
- [x] get_current_branch
- [x] get_git_status
- [x] detect_external_changes
- [x] create_user_branch
- [x] get_user_name_for_branch

### Batch 2 (Git Operations & Sync) - 5 helpers
- [x] list_active_branches
- [x] detect_conflicts_before_merge
- [x] merge_with_fp_intelligence
- [x] sync_git_state
- [x] project_update_git_status

**Notes**:
- Git directives: git_init, git_detect_external_changes, git_create_branch, git_detect_conflicts, git_merge_branch, git_sync_state
- FP-powered conflict resolution uses purity analysis (>0.8 confidence auto-resolve)
- External change detection compares project.last_known_git_hash with current HEAD
- Branch naming: aifp-{user}-{number}

---

## helpers-orchestrators.json (12 helpers)

**Focus**: High-level orchestrators, status, state management

### Batch 1 (Entry Points & Status) - 6 helpers
- [x] aifp_run
- [x] aifp_status
- [x] get_project_status
- [x] get_status_tree
- [x] get_project_context
- [x] get_work_context

### Batch 2 (Query & Update Tools) - 6 helpers
- [x] get_current_progress
- [x] update_project_state
- [x] batch_update_progress
- [x] query_project_state
- [x] validate_initialization
- [x] get_files_by_flow_context

**Notes**:
- aifp_run and aifp_status are primary entry points - critical directive flow guidance
- get_current_progress replaces 5-10 separate helper calls
- update_project_state handles task lifecycle: start_task, complete_task, pause_task, resume_task
- Status helpers should reference directive_flow navigation

---

## helpers-user-custom.json (16 helpers)

**Focus**: User directive automation (Use Case 2)

### Batch 1 (Database Schema & CRUD) - 7 helpers
- [ ] get_user_custom_tables
- [ ] get_user_custom_fields
- [ ] get_user_custom_schema
- [ ] get_user_custom_json_parameters
- [ ] get_from_user_custom
- [ ] get_from_user_custom_where
- [ ] query_user_custom

### Batch 2 (User Custom CRUD & Directive Operations) - 6 helpers
- [ ] add_user_custom_entry
- [ ] update_user_custom_entry
- [ ] delete_user_custom_entry
- [ ] parse_directive_file
- [ ] validate_directive_config
- [ ] generate_handler_code

### Batch 3 (Directive Lifecycle) - 3 helpers
- [ ] deploy_background_service
- [ ] get_user_directive_status
- [ ] monitor_directive_execution

**Notes**:
- User directives only exist in Use Case 2 (automation projects)
- project.user_directives_status field: NULL → in_progress → active
- Directive lifecycle: parse → validate → implement → approve → activate → monitor
- File-based logging (30-day execution, 90-day error retention)

---

## helpers-index.json (1 helper)

**Focus**: Global database metadata

- [ ] get_databases

**Notes**: Returns metadata for all 4 databases (core, project, settings, user_custom)

---

## Session Notes

### Session 1: 2025-12-29 (Initial Setup & Project 1)
- Created checklist document with enhancement patterns
- Files completed: helpers-project-1.json (37/37) ✅, helpers-git.json (11/11) ✅, helpers-orchestrators.json (12/12) ✅
- Batches completed:
  - helpers-project-1.json: All 5 batches (37 helpers) ✅
  - helpers-git.json: Both batches (11 helpers) ✅
  - helpers-orchestrators.json: Both batches (12 helpers) ✅
- Key decisions:
  - **REMOVED** all "RETURN: ..." lines - redundant since AI sees actual return values
  - **REMOVED** CODE NOTE from return_statements - moved to separate implementation_notes field
  - **ADDED** implementation_notes field for dev reference (import script skips this)
  - **FOCUS** return_statements on actionable guidance only: NEXT STEP, CHECK, RELATED HELPERS, DIRECTIVE CONTEXT, DIRECTIVE FLOW, COMMON WORKFLOWS, WARNING
- Pattern established:
  - return_statements = conceptual workflow guidance (goes to database)
  - implementation_notes = code implementation hints (stays in JSON, not imported)
  - Generic database helpers provide schema navigation and workflow patterns
  - All return_statements are database-ready (no cleanup needed for import)

### Session 2: 2025-12-29 (Restructuring & Metadata Update)
- **File Split**: Split large helpers-project files into 9 manageable files (helpers-project-1 through 9)
- **Metadata Update**: Updated all metadata sections with correct counts, ranges, and descriptions
- **Progress Summary**:
  - helpers-project-1.json: 15 helpers (100%) ✅
  - helpers-project-2.json: 10 helpers (100%) ✅
  - helpers-project-3.json: 10 helpers (100%) ✅
  - helpers-project-4.json: 13 helpers (0%) - ready for enhancement
  - helpers-project-5.json: 11 helpers (0%) - ready for enhancement
  - helpers-project-6.json: 14 helpers (0%) - ready for enhancement
  - helpers-project-7.json: 15 helpers (0%) - ready for enhancement
  - helpers-project-8.json: 14 helpers (0%) - ready for enhancement
  - helpers-project-9.json: 10 helpers (0%) - ready for enhancement
- **Next Step**: Review completed files (1-3) to verify adherence to enhancement principles, then continue with files 4-9

### Session 3: 2025-12-29 (Stability Review & Quality Guide Revision)
- **Quality Guide Revised**: Updated RETURN_STATEMENTS_QUALITY_GUIDE.md to focus on stability
  - Shifted from hardcoding helper function names to conceptual guidance
  - Focus on: directives (stable), flows (stable), database schema (stable), conceptual operations
  - Avoid: hardcoded function names (change during dev), brittle function chains
  - Added principle: "Not all helpers need return_statements" - only when adding value
- **Review Process Completed for helpers-project-1.json**: All 15 helpers reviewed and revised ✅
  - **Batch 1 (Helpers 1-5)**: Schema and query helpers - removed hardcoded function names
  - **Batch 2 (Helpers 6-10)**: CRUD helpers - focused on constraints, specialization, audit trails
  - **Batch 3 (Helpers 11-15)**: Project metadata helpers - **verified directive context from used_by_directives**
    - create_project: project_init (seq 1) - initialization flow verified
    - get_project: project_blueprint_read/update - fallback and version tracking flows
    - update_project: project_blueprint_update (seq 2) - version increment flow
    - blueprint_has_changed: blueprint read/update pre-checks - staleness detection flows
    - get_infrastructure_by_type: project_init (seq 2) - infrastructure population flow
- **Key Changes Applied**:
  - Removed patterns like "Call function_name()" → "Find helper for [operation]"
  - Removed patterns like "Use X() then Y()" → "Conceptual operation A → operation B"
  - Added "DIRECTIVE:" statements with execution_context and sequence_order from used_by_directives
  - Added "DIRECTIVE FLOW:" statements showing directive navigation patterns
  - Emphasized DATABASE CONTEXT for schema fields and relationship information
- **Next**: Review helpers-project-2.json (10 helpers), then project-3 through project-9

### Session 4: 2025-12-30 (Delete System Overhaul + Quality Guide Enhancement)
- **Files Completed**:
  - helpers-project-1.json: ALL 15 helpers (100%) ✅ - Verified stability of 10 generic CRUD helpers
  - helpers-project-2.json: ALL 10 helpers (100%) ✅
  - helpers-project-3.json: ALL 10 helpers (100%) ✅
  - helpers-project-4.json: 1 helper (delete_type) fixed
- **Directive Context Work**: Added DIRECTIVE CONTEXT to 10 helpers with used_by_directives
  - helpers-project-2: 4 helpers (get_file_by_path, update_file, file_has_changed, delete_file)
  - helpers-project-3: 6 helpers (reserve_function, finalize_function, get_functions_by_file, update_function, update_functions_for_file, delete_function)
- **Delete System Overhaul**: Completely redesigned delete operations with ERROR-first approach
  - **Critical Separation**: return_statements (forward-thinking after success) vs implementation_notes (error logic for devs)
  - **delete_file**: ERROR-first - checks functions/types/file_flows, returns error list, forces manual cleanup
  - **delete_function**: ERROR-first - checks types_functions, returns error list, forces unlinking (interactions auto-cascade via SQL)
  - **delete_type**: ERROR-first - checks types_functions, returns error list, forces unlinking
  - **No Circular Dependencies**: Verified deletion flow - files, functions, types deletable independently after unlinking
  - **Directive Updated**: Rewrote project_file_delete directive JSON workflow + complete MD file rewrite with ERROR-first examples
- **Quality Guide Enhanced**: Added 3 critical new sections
  - **Field Separation**: return_statements vs implementation_notes - different purposes, audiences, focus
  - **ERROR-First Delete Pattern**: Complete pattern documentation with error response structures
  - **Avoid Automatic Operation Notes**: Don't document what happens automatically - wastes tokens
- **Pattern Established**:
  - return_statements: Only forward-thinking guidance AFTER successful execution (imported to DB)
  - implementation_notes: Error logic, validation, implementation details (NOT imported to DB)
  - Delete operations: ERROR-first forces intentional cleanup, prevents accidental data loss
  - No hardcoded helper names: Use conceptual references to maintain stability
  - No automatic operation notes: If it's automatic, AI doesn't need to know
- **Progress**: 36/202 helpers complete (18%) - Projects 1, 2, 3 fully complete ✅

---

## References

- **Directive Flows**: `docs/directives-json/directive_flow_*.json`
- **Helper Mappings**: `docs/helpers/json/mapping_suggestions.json`
- **Original Helper TXT**: `docs/helpers/info-helpers-*.txt`
- **System Prompt**: `sys-prompt/aifp_system_prompt.txt`
- **Project Blueprint**: `.aifp/ProjectBlueprint.md`

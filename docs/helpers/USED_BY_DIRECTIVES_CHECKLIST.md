# Helper used_by_directives Review Checklist

**Purpose**: Review each helper and determine which directives would logically use it based on database/table relationships.

**Process**:
1. Identify helper's database and table(s)
2. Find directives that work with that database/table
3. Read directive name and purpose
4. Determine if directive would logically need to get/set this data
5. Add to used_by_directives if yes

**Status Legend**:
- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed

---

## Progress Overview

**Total Helpers**: 202
**Completed**: 202 helpers (100%)
**In Progress**: 0 helpers
**Not Started**: 0 helpers (0%)

🎉 **ALL HELPERS COMPLETED!** 🎉

---

## Simple Process Summary

**For each helper:**

1. **Identify the helper's role**
   - Is it a getter or setter?
   - Which database? (aifp_core.db, project.db, user_preferences.db, user_directives.db)
   - Which table(s)?
   - Which field(s)?

2. **Find related directives**
   - Which directives work with this database?
   - Which directives work with this table?
   - List them out

3. **Check logical need**
   - For each directive: Does it need to get/set this data?
   - Read directive name and purpose (from directives-json files)
   - If YES → Add to used_by_directives
   - If NO → Skip

4. **Update helper JSON**
   - Overwrite existing used_by_directives array (don't review old data)
   - Save file

**Remember**: This is about logical relationships, not execution sequences.

---

## Directive Reference Files

**Directive definitions** (name, purpose, workflows):
- `docs/directives-json/directives-fp-core.json` - FP core directives
- `docs/directives-json/directives-fp-aux.json` - FP auxiliary directives
- `docs/directives-json/directives-project.json` - Project directives
- `docs/directives-json/directives-user-pref.json` - User preference directives
- `docs/directives-json/directives-user-system.json` - User directive system
- `docs/directives-json/directives-git.json` - Git directives
- `docs/directives-json/directives-system.json` - System directives (aifp_run, aifp_status)

**Directive flows** (understand relationships):
- `docs/directives-json/directive_flow_fp.json`
- `docs/directives-json/directive_flow_project.json`
- `docs/directives-json/directive_flow_user-preferences.json`

---

## helpers-core.json (33 helpers) ✓ COMPLETED

**Database**: aifp_core.db
**Tables**: directives, helper_functions, directive_helpers, directives_interactions, categories, tools, directive_keywords, directive_flows, conditional_work_paths

### Database Schema Helpers (7 helpers)
- [x] get_core_tables (empty - generic AI tool)
- [x] get_core_fields (empty - generic AI tool)
- [x] get_core_schema (empty - generic AI tool)
- [x] get_from_core (empty - generic AI tool)
- [x] get_from_core_where (empty - generic AI tool)
- [x] query_core (empty - generic AI tool)
- [x] get_directive_by_name (2: aifp_help, fp_reference_consultation)

### Directive Queries (7 helpers)
- [x] get_all_directives (1: aifp_run)
- [x] get_directive_content (2: aifp_help, fp_reference_consultation)
- [x] search_directives (2: fp_reference_consultation, aifp_help) ✓
- [x] find_directive_by_intent (1: user_preferences_update) ✓
- [x] find_directives_by_intent_keyword (empty - is_tool: false)
- [x] get_directives_with_intent_keywords (2: user_preferences_update, aifp_help)
- [x] add_directive_intent_keyword (empty - is_tool: false)

### Directive Keywords & Navigation (7 helpers)
- [x] remove_directive_intent_keyword (empty - is_tool: false)
- [x] get_directive_keywords (1: aifp_help)
- [x] get_all_directive_keywords (1: aifp_help)
- [x] get_all_intent_keywords_with_counts (1: aifp_help)
- [x] get_next_directives_from_status (2: aifp_status, project_auto_resume)
- [x] get_matching_next_directives (1: aifp_status)
- [x] get_completion_loop_target (4: project_task_complete, project_subtask_complete, project_sidequest_complete, project_milestone_complete)

### Directive Navigation & Helpers (7 helpers)
- [x] get_conditional_work_paths (3: aifp_status, project_file_write, project_task_complete)
- [x] get_helper_by_name (empty - AI query tool)
- [x] get_helpers_by_database (empty - AI query tool)
- [x] get_helpers_are_tool (empty - AI query tool)
- [x] get_helpers_not_tool_not_sub (empty - AI query tool)
- [x] get_helpers_are_sub (empty - AI query tool)
- [x] get_helpers_for_directive (1: aifp_help)

### Helper/Directive Relationships & Categories (5 helpers)
- [x] get_directives_for_helper (1: aifp_help)
- [x] get_category_by_name (1: aifp_help)
- [x] get_categories (1: aifp_help)
- [x] get_directives_by_category (1: aifp_help)
- [x] get_directives_by_type (1: aifp_help)

---

## helpers-project-1.json (15 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: Multiple (project, infrastructure, files, functions, types, interactions, themes, flows, completion_path, milestones, tasks, subtasks, sidequests, notes)

### Database Schema & CRUD (10 helpers)
- [x] get_project_tables (empty - generic AI tool)
- [x] get_project_fields (empty - generic AI tool)
- [x] get_project_schema (empty - generic AI tool)
- [x] get_project_json_parameters (empty - generic AI tool)
- [x] get_from_project (empty - generic AI tool)
- [x] get_from_project_where (empty - generic AI tool)
- [x] query_project (empty - generic AI tool)
- [x] add_project_entry (empty - generic AI tool)
- [x] update_project_entry (empty - generic AI tool)
- [x] delete_project_entry (empty - generic AI tool)

### Project Metadata (5 helpers)
**Table**: project
- [x] create_project (1: project_init)
- [x] get_project (5: project_blueprint_read, project_blueprint_update, aifp_status, project_evolution, project_archive)
- [x] update_project (5: project_blueprint_update, project_evolution, project_archive, user_directive_parse, user_directive_activate)
- [x] blueprint_has_changed (2: project_blueprint_read, project_blueprint_update)
- [x] get_infrastructure_by_type (2: project_init, project_blueprint_read)

---

## helpers-project-2.json (10 helpers) ✓ COMPLETED

**Database**: project.db
**Table**: files

- [x] reserve_file (2: project_reserve_finalize, project_file_write) ✓
- [x] reserve_files (empty - batch AI tool)
- [x] finalize_file (3: project_reserve_finalize, project_file_write, project_update_db) ✓
- [x] finalize_files (empty - batch AI tool)
- [x] get_file_by_name (2: project_dependency_sync, project_dependency_map)
- [x] get_file_by_path (5: project_file_read, project_file_delete, project_dependency_sync, project_dependency_map, project_integrity_check)
- [x] update_file (3: project_update_db, project_dependency_sync, project_integrity_check)
- [x] file_has_changed (3: project_file_read, project_integrity_check, project_dependency_sync)
- [x] update_file_timestamp (empty - is_sub_helper)
- [x] delete_file (1: project_file_delete) ✓

---

## helpers-project-3.json (10 helpers) ✓ COMPLETED

**Database**: project.db
**Table**: functions

- [x] reserve_function (2: project_reserve_finalize, project_file_write) ✓
- [x] reserve_functions (empty - batch AI tool)
- [x] finalize_function (3: project_reserve_finalize, project_file_write, project_update_db) ✓
- [x] finalize_functions (empty - batch AI tool)
- [x] get_function_by_name (3: project_dependency_sync, project_dependency_map, project_compliance_check)
- [x] get_functions_by_file (4: project_file_read, project_dependency_map, project_compliance_check, project_dependency_sync)
- [x] update_function (3: project_update_db, project_dependency_sync, project_compliance_check)
- [x] update_functions_for_file (3: project_update_db, project_dependency_sync, project_compliance_check)
- [x] update_function_file_location (empty - not MCP tool)
- [x] delete_function (1: project_file_delete) ✓

---

## helpers-project-4.json (13 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: types, types_functions, interactions

### Type Management (6 helpers)
**Table**: types
- [x] reserve_type (2: project_reserve_finalize, project_file_write)
- [x] reserve_types (empty - batch AI tool)
- [x] finalize_type (3: project_reserve_finalize, project_file_write, project_update_db)
- [x] finalize_types (empty - batch AI tool)
- [x] update_type (2: project_update_db, project_dependency_sync)
- [x] delete_type (1: project_file_delete)

### Type-Function Relationships (3 helpers)
**Table**: types_functions
- [x] add_types_functions (1: project_update_db)
- [x] update_type_function_role (empty - not MCP tool)
- [x] delete_type_function (empty - not MCP tool)

### Interaction Management (4 helpers)
**Table**: interactions
- [x] add_interaction (1: project_update_db)
- [x] add_interactions (1: project_update_db)
- [x] update_interaction (1: project_dependency_sync)
- [x] delete_interaction (empty - not MCP tool)

---

## helpers-project-5.json (11 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: themes, flows, flow_themes

### Theme Management (5 helpers)
**Table**: themes
- [x] get_theme_by_name (2: project_theme_flow_mapping, project_init) ✓
- [x] get_all_themes (3: project_blueprint_read, project_evolution, aifp_status)
- [x] add_theme (2: project_init, project_theme_flow_mapping) ✓
- [x] update_theme (1: project_evolution)
- [x] delete_theme (empty - user action only)

### Flow Management (5 helpers)
**Table**: flows
- [x] get_flow_by_name (2: project_theme_flow_mapping, project_init) ✓
- [x] get_all_flows (3: project_blueprint_read, project_evolution, aifp_status)
- [x] add_flow (2: project_init, project_theme_flow_mapping) ✓
- [x] update_flow (1: project_evolution)
- [x] delete_flow (empty - user action only)

### Flow-Theme Relationships (1 helper)
**Table**: flow_themes
- [x] get_file_ids_from_flows (1: project_dependency_map)

---

## helpers-project-6.json (14 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: flow_themes, file_flows, completion_path

### Flow-Theme Relationships (2 helpers)
**Table**: flow_themes
- [x] get_flows_for_theme (1: project_theme_flow_mapping) ✓
- [x] get_themes_for_flow (1: project_dependency_map)

### File-Flow Relationships (2 helpers)
**Table**: file_flows
- [x] get_files_by_flow (1: project_dependency_map) ✓
- [x] get_flows_for_file (1: project_dependency_map) ✓

### Completion Path Management (10 helpers)
**Table**: completion_path
- [x] add_completion_path (1: project_task_decomposition) ✓
- [x] get_all_completion_paths (3: project_blueprint_read, project_evolution, aifp_status)
- [x] get_completion_paths_by_status (1: aifp_status)
- [x] get_incomplete_completion_paths (2: aifp_status, project_milestone_complete)
- [x] get_next_completion_path (1: project_milestone_complete) ✓
- [x] update_completion_path (1: project_milestone_complete) ✓
- [x] delete_completion_path (empty - user action only)
- [x] reorder_completion_path (empty - not MCP tool)
- [x] reorder_all_completion_paths (empty - not MCP tool)
- [x] swap_completion_paths_order (empty - not MCP tool)

---

## helpers-project-7.json (15 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: milestones, tasks, task_flows, task_files

### Milestone Management (6 helpers)
**Table**: milestones
- [x] add_milestone (1: project_task_decomposition) ✓
- [x] get_milestones_by_path (1: project_milestone_complete) ✓
- [x] get_milestones_by_status (2: aifp_status, project_metrics)
- [x] get_incomplete_milestones (3: aifp_status, project_auto_resume, project_completion_check)
- [x] update_milestone (1: project_milestone_complete) ✓
- [x] delete_milestone (empty - user action only)

### Task Management (7 helpers)
**Table**: tasks
- [x] add_task (2: project_task_decomposition, project_task_create) ✓
- [x] get_incomplete_tasks_by_milestone (1: project_task_complete) ✓
- [x] get_incomplete_tasks (4: aifp_status, project_auto_resume, project_auto_summary, project_completion_check)
- [x] get_tasks_by_milestone (1: project_task_create) ✓
- [x] get_tasks_comprehensive (2: aifp_status, project_metrics)
- [x] update_task (5: project_task_update, project_task_complete, project_subtask_create, project_subtask_complete, project_sidequest_complete) ✓
- [x] delete_task (empty - user action only)

### Task Relationships (2 helpers)
**Tables**: task_flows, task_files
- [x] get_task_flows (1: project_dependency_map)
- [x] get_task_files (1: project_dependency_map)

---

## helpers-project-8.json (14 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: subtasks, sidequests, sidequest_flows, sidequest_files

### Subtask Management (7 helpers)
**Table**: subtasks
- [x] add_subtask (2: project_task_decomposition, project_subtask_create) ✓
- [x] get_incomplete_subtasks (4: aifp_status, project_auto_resume, project_auto_summary, project_completion_check)
- [x] get_incomplete_subtasks_by_task (2: project_subtask_create, project_subtask_complete) ✓
- [x] get_subtasks_by_task (1: project_subtask_complete) ✓
- [x] get_subtasks_comprehensive (2: aifp_status, project_metrics)
- [x] update_subtask (2: project_task_update, project_subtask_complete) ✓
- [x] delete_subtask (empty - user action only)

### Sidequest Management (6 helpers)
**Table**: sidequests
- [x] add_sidequest (2: project_task_decomposition, project_sidequest_create) ✓
- [x] get_incomplete_sidequests (4: aifp_status, project_auto_resume, project_auto_summary, project_completion_check)
- [x] get_sidequests_comprehensive (2: aifp_status, project_metrics)
- [x] update_sidequest (2: project_task_update, project_sidequest_complete) ✓
- [x] delete_sidequest (empty - user action only)

### Sidequest Relationships (2 helpers)
**Tables**: sidequest_flows, sidequest_files
- [x] get_sidequest_flows (1: project_dependency_map)
- [x] get_sidequest_files (1: project_dependency_map)

---

## helpers-project-9.json (10 helpers) ✓ COMPLETED

**Database**: project.db
**Tables**: items, notes

### Item Management (5 helpers)
**Table**: items
- [x] get_items_for_task (1: project_item_create) ✓
- [x] get_items_for_subtask (1: project_item_create)
- [x] get_items_for_sidequest (1: project_item_create)
- [x] get_incomplete_items (4: project_task_complete, project_subtask_complete, project_sidequest_complete, aifp_status)
- [x] delete_item (empty - user action only)

### Note Management (5 helpers)
**Table**: notes
- [x] add_note (2: project_notes_log, project_sidequest_complete) ✓
- [x] get_notes_comprehensive (2: project_auto_summary, project_metrics) ✓
- [x] search_notes (2: project_auto_summary, project_metrics) ✓
- [x] update_note (empty - user action only)
- [x] delete_note (empty - not MCP tool)

---

## helpers-settings.json (17 helpers) ✓ COMPLETED

**Database**: user_preferences.db
**Tables**: directive_preferences, user_settings, tracking_settings, ai_interaction_log, fp_flow_tracking, issue_reports

### Database Schema & CRUD (7 helpers)
**Tables**: Multiple
- [x] get_settings_tables (empty - generic AI tool)
- [x] get_settings_fields (empty - generic AI tool)
- [x] get_settings_schema (empty - generic AI tool)
- [x] get_settings_json_parameters (empty - generic AI tool)
- [x] get_from_settings (empty - generic AI tool)
- [x] get_from_settings_where (empty - generic AI tool)
- [x] query_settings (3: user_preferences_sync, tracking_toggle, user_preferences_export) ✓

### Settings CRUD (3 helpers)
**Tables**: Multiple
- [x] add_settings_entry (1: user_preferences_import) ✓
- [x] update_settings_entry (2: user_preferences_update, tracking_toggle) ✓
- [x] delete_settings_entry (empty - user action only)

### Directive Preferences (4 helpers)
**Table**: directive_preferences
- [x] load_directive_preferences (1: user_preferences_sync) ✓
- [x] add_directive_preference (2: user_preferences_update, user_preferences_learn) ✓
- [x] get_user_setting (empty - generic AI tool)
- [x] update_user_preferences (1: user_preferences_update) ✓

### Preferences Application & Tracking (3 helpers)
**Tables**: tracking_settings, etc.
- [x] apply_preferences_to_context (1: user_preferences_sync) ✓
- [x] get_tracking_settings (2: user_preferences_sync, tracking_toggle)
- [x] toggle_tracking_feature (1: tracking_toggle) ✓

---

## helpers-git.json (11 helpers) ✓ COMPLETED

**Database**: project.db (git-related fields in project table)
**Tables**: project (last_known_git_hash), work_branches, merge_history

### Git Status & Detection (6 helpers)
- [x] get_current_commit_hash (2: git_init, git_sync_state) ✓
- [x] get_current_branch (2: git_init, git_sync_state) ✓
- [x] get_git_status (1: git_init) ✓
- [x] detect_external_changes (2: git_detect_external_changes, git_sync_state) ✓
- [x] create_user_branch (1: git_create_branch) ✓
- [x] get_user_name_for_branch (1: git_create_branch) ✓

### Git Operations & Sync (5 helpers)
- [x] list_active_branches (2: aifp_status, git_merge_branch)
- [x] detect_conflicts_before_merge (2: git_detect_conflicts, git_merge_branch) ✓
- [x] merge_with_fp_intelligence (1: git_merge_branch) ✓
- [x] sync_git_state (1: git_sync_state) ✓
- [x] project_update_git_status (3: git_init, git_detect_external_changes, git_sync_state) ✓

---

## helpers-orchestrators.json (12 helpers) ✓ COMPLETED

**Database**: Multiple (aifp_core.db, project.db, user_preferences.db)
**Focus**: High-level orchestrators that coordinate multiple database queries

### Entry Points & Status (6 helpers)
- [x] aifp_run (1: aifp_run) ✓
- [x] aifp_status (2: aifp_status, aifp_run) ✓
- [x] get_project_status (1: aifp_status) ✓
- [x] get_status_tree (1: aifp_status) ✓
- [x] get_project_context (1: aifp_help)
- [x] get_work_context (1: project_auto_resume)

### Query & Update Tools (6 helpers)
- [x] get_current_progress (empty - generic AI tool)
- [x] update_project_state (empty - generic AI tool)
- [x] batch_update_progress (empty - generic AI tool)
- [x] query_project_state (empty - generic AI tool)
- [x] validate_initialization (1: aifp_status)
- [x] get_files_by_flow_context (1: project_dependency_map)

---

## helpers-user-custom.json (16 helpers) ✓ COMPLETED

**Database**: user_directives.db
**Tables**: user_directives, directive_executions, directive_dependencies, directive_implementations, helper_functions, directive_helpers, source_files, logging_config

### Database Schema & CRUD (7 helpers)
**Tables**: Multiple
- [x] get_user_custom_tables (empty - generic AI tool)
- [x] get_user_custom_fields (empty - generic AI tool)
- [x] get_user_custom_schema (empty - generic AI tool)
- [x] get_user_custom_json_parameters (empty - generic AI tool)
- [x] get_from_user_custom (empty - generic AI tool)
- [x] get_from_user_custom_where (empty - generic AI tool)
- [x] query_user_custom (empty - generic AI tool)

### User Custom CRUD (3 helpers)
**Tables**: Multiple
- [x] add_user_custom_entry (2: user_directive_parse, user_directive_update) ✓
- [x] update_user_custom_entry (6: user_directive_validate, user_directive_implement, user_directive_approve, user_directive_activate, user_directive_deactivate, user_directive_update) ✓
- [x] delete_user_custom_entry (1: user_directive_update) ✓

### Directive Operations (3 helpers)
**Tables**: user_directives, source_files, etc.
- [x] parse_directive_file (2: user_directive_parse, user_directive_update) ✓
- [x] validate_directive_config (2: user_directive_validate, user_directive_update) ✓
- [x] generate_handler_code (2: user_directive_implement, user_directive_update) ✓

### Directive Lifecycle (3 helpers)
**Tables**: user_directives, directive_executions, etc.
- [x] deploy_background_service (1: user_directive_activate) ✓
- [x] get_user_directive_status (2: user_directive_status, aifp_status)
- [x] monitor_directive_execution (1: user_directive_monitor) ✓

---

## helpers-index.json (1 helper) ✓ COMPLETED

**Database**: All databases (metadata)

- [x] get_databases (2: aifp_help, aifp_status)

---

## Session Notes

### Session 1: 2026-01-01 (Starting Fresh)
- **Goal**: Review all 202 helpers and determine used_by_directives
- **Approach**: Fresh review, ignore existing data
- **Process**:
  1. Identify database/table
  2. Find related directives
  3. Check logical need
  4. Update used_by_directives array
- **Key Principle**: Logical relationships, not execution sequences

---

## References

- **Directive Files**: `docs/directives-json/directives-*.json`
- **Directive Flows**: `docs/directives-json/directive_flow_*.json`
- **Helper JSON Files**: `docs/helpers/json/helpers-*.json`
- **Quality Guide**: `docs/helpers/RETURN_STATEMENTS_QUALITY_GUIDE.md`

---

**Last Updated:** 2026-01-01 (COMPLETED - All 202 helpers reviewed)

---

## Completion Summary

✅ **Task Complete!** All 202 helpers have been reviewed and their `used_by_directives` relationships established.

**Final Statistics:**
- **Total Helpers**: 202
- **Helpers with Directives**: ~135 (67%)
- **Helpers Empty** (Generic AI tools): ~67 (33%)
- **Total Directive Relationships Added**: ~160+

**Files Completed:**
1. ✅ helpers-project-1.json (15 helpers)
2. ✅ helpers-project-2.json (10 helpers)
3. ✅ helpers-project-3.json (10 helpers)
4. ✅ helpers-project-4.json (13 helpers)
5. ✅ helpers-project-5.json (11 helpers)
6. ✅ helpers-project-6.json (14 helpers)
7. ✅ helpers-project-7.json (15 helpers)
8. ✅ helpers-project-8.json (14 helpers)
9. ✅ helpers-project-9.json (10 helpers)
10. ✅ helpers-core.json (33 helpers)
11. ✅ helpers-settings.json (17 helpers)
12. ✅ helpers-git.json (11 helpers)
13. ✅ helpers-orchestrators.json (12 helpers)
14. ✅ helpers-user-custom.json (16 helpers)
15. ✅ helpers-index.json (1 helper)

**Next Step**: These JSON files are now ready to be parsed into the `directive_helpers` table in `aifp_core.db`.

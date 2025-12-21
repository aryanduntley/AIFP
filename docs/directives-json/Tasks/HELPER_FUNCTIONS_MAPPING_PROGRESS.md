# Helper Functions Mapping Progress

**Purpose**: Track progress as we map helper functions to JSON with all database fields and directive relationships
**Total Helpers**: 202 (1 duplicate re-added: helpers-orchestrators.json has 12, not 11)

---

## Progress Summary - MD to JSON Conversion (Phase 1-7)

- [x] **Index Helper**: 1/1 complete (100%) - CONVERTED ✅
- [x] **Core Helpers**: 33/33 complete (100%) - CONVERTED ✅
- [x] **Git Helpers**: 11/11 complete (100%) - CONVERTED ✅
- [x] **Orchestrator Helpers**: 12/12 complete (100%) - CONVERTED ✅ (aifp_run was re-added)
- [x] **Project Helpers**: 112/112 complete (100%) - CONVERTED ✅ (removed 5 orchestrator duplicates)
- [x] **Settings Helpers**: 17/17 complete (100%) - CONVERTED ✅
- [x] **User Custom Helpers**: 16/16 complete (100%) - CONVERTED ✅

**Overall**: 202/202 complete (100%) - MD to JSON conversion complete!

---

## ✅ Phase 8 Completion - Helper-Directive Mapping (2025-12-20)

### Achievement: 100% Directive Coverage

**Status**: ✅ **PHASE 8 COMPLETE**

**Mapped Helpers**: 84/202 (41.6%) - All directive-used helpers
**Unmapped Helpers**: 118/202 (58.4%) - All AI-only tools (correctly unmapped)

### Mapped Helpers by Category

| Category | Mapped | AI-Only | Total | Coverage |
|----------|--------|---------|-------|----------|
| Core | 3 | 30 | 33 | 100% of directive-used |
| Git | 10 | 1 | 11 | 100% of directive-used |
| Index | 0 | 1 | 1 | N/A (system utility) |
| Orchestrators | 4 | 8 | 12 | 100% of directive-used |
| Project | 49 | 63 | 112 | 100% of directive-used |
| Settings | 9 | 8 | 17 | 100% of directive-used |
| User-Custom | 9 | 7 | 16 | 100% of directive-used |
| **TOTAL** | **84** | **118** | **202** | **100%** |

### Key Finding

**All 84 helpers that are actually called by directives have been mapped.**

The 118 unmapped helpers are AI-only tools:
- Schema/query tools (AI explores database structure)
- Batch helpers (AI bulk operations)
- Delete helpers (only 1 delete directive exists)
- Generic CRUD fallbacks (AI uses when no specialized helper exists)
- Advanced search/filtering (AI exploration)
- Reorder/management tools (AI manual operations)

**See**: `docs/UNMAPPED_HELPERS_ANALYSIS.md` for detailed breakdown

---

## Updated Progress Summary (Phase 8)

**Changes**:
1. Removed 5 duplicate orchestrator helpers from project files
2. Consolidated JSON files from 14 → 9 files:
   - helpers-core-1 + core-2 → helpers-core.json (657 lines)
   - helpers-orchestrators-1 + orchestrators-2 → helpers-orchestrators.json (348 lines)
   - helpers-project-1 through -6 → helpers-project-1, -2, -3 (3 files, ~600 lines each)

**Removed Duplicates**:
- `get_project_status` - Comprehensive status orchestrator (belongs in orchestrators only)
- `get_project_context` - Project context orchestrator (belongs in orchestrators only)
- `get_status_tree` - Hierarchical tree orchestrator (belongs in orchestrators only)
- `get_work_context` - Work context orchestrator (belongs in orchestrators only)
- `get_files_by_flow_context` - Flow context orchestrator (belongs in orchestrators only)

**Final File Structure**:
- helpers-index.json (25 lines, 1 helper)
- helpers-core.json (657 lines, 33 helpers)
- helpers-git.json (182 lines, 11 helpers)
- helpers-orchestrators.json (348 lines, 11 helpers)
- helpers-project-1.json (716 lines, 37 helpers)
- helpers-project-2.json (599 lines, 40 helpers)
- helpers-project-3.json (589 lines, 35 helpers)
- helpers-settings.json (301 lines, 17 helpers)
- helpers-user-custom.json (254 lines, 16 helpers)

**Next Step**: Fill in `used_by_directives` arrays during directive mapping

---

## Index Helper (1) → helpers-index.json

- [ ] `get_databases` - Get list of all available databases with metadata

---

## Core Helpers (33) → helpers-core.json

- [ ] `get_core_tables`
- [ ] `get_core_fields`
- [ ] `get_core_schema`
- [ ] `get_from_core`
- [ ] `get_from_core_where`
- [ ] `query_core`
- [ ] `get_directive_by_name`
- [ ] `get_all_directives`
- [ ] `get_directive_content`
- [ ] `search_directives`
- [ ] `find_directive_by_intent`
- [ ] `find_directives_by_intent_keyword`
- [ ] `get_directives_with_intent_keywords`
- [ ] `add_directive_intent_keyword`
- [ ] `remove_directive_intent_keyword`
- [ ] `get_directive_keywords`
- [ ] `get_all_directive_keywords`
- [ ] `get_all_intent_keywords_with_counts`
- [ ] `get_next_directives_from_status`
- [ ] `get_matching_next_directives`
- [ ] `get_completion_loop_target`
- [ ] `get_conditional_work_paths`
- [ ] `get_helper_by_name`
- [ ] `get_helpers_by_database`
- [ ] `get_helpers_are_tool`
- [ ] `get_helpers_not_tool_not_sub`
- [ ] `get_helpers_are_sub`
- [ ] `get_helpers_for_directive`
- [ ] `get_directives_for_helper`
- [ ] `get_category_by_name`
- [ ] `get_categories`
- [ ] `get_directives_by_category`
- [ ] `get_directives_by_type`

---

## Git Helpers (11) → helpers-git.json

- [ ] `get_current_commit_hash`
- [ ] `get_current_branch`
- [ ] `get_git_status`
- [ ] `detect_external_changes`
- [ ] `create_user_branch`
- [ ] `get_user_name_for_branch`
- [ ] `list_active_branches`
- [ ] `detect_conflicts_before_merge`
- [ ] `merge_with_fp_intelligence`
- [ ] `sync_git_state`
- [ ] `project_update_git_status`

---

## Orchestrator Helpers (11) → helpers-orchestrators.json (consolidated)

- [ ] `get_current_progress`
- [ ] `update_project_state`
- [ ] `batch_update_progress`
- [ ] `query_project_state`
- [ ] `validate_initialization`
- [ ] `get_work_context`
- [ ] `aifp_status`
- [ ] `get_project_status`
- [ ] `get_project_context`
- [ ] `get_status_tree`
- [ ] `get_files_by_flow_context`

---

## Project Helpers (112) → helpers-project-1.json, helpers-project-2.json, helpers-project-3.json (consolidated from 6 to 3 files)

### File 1: helpers-project-1.json (1-37 of 112, 716 lines)
- [ ] `get_project_tables`
- [ ] `get_project_fields`
- [ ] `get_project_schema`
- [ ] `get_project_json_parameters`
- [ ] `get_from_project`
- [ ] `get_from_project_where`
- [ ] `query_project`
- [ ] `add_project_entry`
- [ ] `update_project_entry`
- [ ] `delete_project_entry`
- [ ] `create_project`
- [ ] `get_project`
- [ ] `update_project`
- [ ] `blueprint_has_changed`
- [ ] `get_infrastructure_by_type`
- [ ] `reserve_file`
- [ ] `reserve_files`
- [ ] `finalize_file`
- [ ] `finalize_files`
- [ ] `get_file_by_name`
- [ ] `get_file_by_path`
- [ ] `update_file`
- [ ] `file_has_changed`
- [ ] `update_file_timestamp`
- [ ] `delete_file`
- [ ] `reserve_function`
- [ ] `reserve_functions`
- [ ] `finalize_function`
- [ ] `finalize_functions`
- [ ] `get_function_by_name`
- [ ] `get_functions_by_file`
- [ ] `update_function`
- [ ] `update_functions_for_file`
- [ ] `update_function_file_location`
- [ ] `delete_function`
- [ ] `reserve_type`
- [ ] `reserve_types`

### File 2: helpers-project-2.json (38-77 of 112, 599 lines)
- [ ] `finalize_type`
- [ ] `finalize_types`
- [ ] `update_type`
- [ ] `delete_type`
- [ ] `add_types_functions`
- [ ] `update_type_function_role`
- [ ] `delete_type_function`
- [ ] `add_interaction`
- [ ] `add_interactions`
- [ ] `update_interaction`
- [ ] `delete_interaction`
- [ ] `get_theme_by_name`
- [ ] `get_flow_by_name`
- [ ] `get_all_themes`
- [ ] `get_all_flows`
- [ ] `add_theme`
- [ ] `update_theme`
- [ ] `delete_theme`
- [ ] `add_flow`
- [ ] `get_file_ids_from_flows`
- [ ] `update_flow`
- [ ] `delete_flow`
- [ ] `get_flows_for_theme`
- [ ] `get_themes_for_flow`
- [ ] `get_files_by_flow`
- [ ] `get_flows_for_file`
- [ ] `add_completion_path`
- [ ] `get_all_completion_paths`
- [ ] `get_next_completion_path`
- [ ] `get_completion_paths_by_status`
- [ ] `get_incomplete_completion_paths`
- [ ] `update_completion_path`
- [ ] `delete_completion_path`
- [ ] `reorder_completion_path`
- [ ] `reorder_all_completion_paths`
- [ ] `swap_completion_paths_order`
- [ ] `add_milestone`
- [ ] `get_milestones_by_path`
- [ ] `get_milestones_by_status`
- [ ] `get_incomplete_milestones`

### File 3: helpers-project-3.json (78-112 of 112, 589 lines)
- [ ] `update_milestone`
- [ ] `delete_milestone`
- [ ] `add_task`
- [ ] `get_incomplete_tasks_by_milestone`
- [ ] `get_incomplete_tasks`
- [ ] `get_tasks_by_milestone`
- [ ] `get_tasks_comprehensive`
- [ ] `get_task_flows`
- [ ] `get_task_files`
- [ ] `update_task`
- [ ] `delete_task`
- [ ] `add_subtask`
- [ ] `get_incomplete_subtasks`
- [ ] `get_incomplete_subtasks_by_task`
- [ ] `get_subtasks_by_task`
- [ ] `get_subtasks_comprehensive`
- [ ] `update_subtask`
- [ ] `delete_subtask`
- [ ] `add_sidequest`
- [ ] `get_incomplete_sidequests`
- [ ] `get_sidequests_comprehensive`
- [ ] `get_sidequest_flows`
- [ ] `get_sidequest_files`
- [ ] `update_sidequest`
- [ ] `delete_sidequest`
- [ ] `get_items_for_task`
- [ ] `get_items_for_subtask`
- [ ] `get_items_for_sidequest`
- [ ] `get_incomplete_items`
- [ ] `delete_item`
- [ ] `add_note`
- [ ] `get_notes_comprehensive`
- [ ] `search_notes`
- [ ] `update_note`
- [ ] `delete_note`

---

## Settings Helpers (17) → helpers-settings.json

- [ ] `get_settings_tables`
- [ ] `get_settings_fields`
- [ ] `get_settings_schema`
- [ ] `get_settings_json_parameters`
- [ ] `get_from_settings`
- [ ] `get_from_settings_where`
- [ ] `query_settings`
- [ ] `add_settings_entry`
- [ ] `update_settings_entry`
- [ ] `delete_settings_entry`
- [ ] `load_directive_preferences`
- [ ] `add_directive_preference`
- [ ] `get_user_setting`
- [ ] `update_user_preferences`
- [ ] `apply_preferences_to_context`
- [ ] `get_tracking_settings`
- [ ] `toggle_tracking_feature`

---

## User Custom Helpers (16) → helpers-user-custom.json

- [ ] `get_user_custom_tables`
- [ ] `get_user_custom_fields`
- [ ] `get_user_custom_schema`
- [ ] `get_user_custom_json_parameters`
- [ ] `get_from_user_custom`
- [ ] `get_from_user_custom_where`
- [ ] `query_user_custom`
- [ ] `add_user_custom_entry`
- [ ] `update_user_custom_entry`
- [ ] `delete_user_custom_entry`
- [ ] `parse_directive_file`
- [ ] `validate_directive_config`
- [ ] `generate_handler_code`
- [ ] `deploy_background_service`
- [ ] `get_user_directive_status`
- [ ] `monitor_directive_execution`

---

## Mapping Requirements Per Helper

For each helper, add:
1. **file_path** - Where helper lives in MCP server code
2. **parameters** - Structured array with types, required flag, defaults
3. **error_handling** - Standardized description
4. **return_statements** - JSON array of AI guidance
5. **used_by_directives** - Array of directive relationships:
   - directive_name
   - execution_context
   - sequence_order
   - is_required
   - parameters_mapping
   - description

---

**Created**: 2025-12-16
**Last Updated**: 2025-12-16

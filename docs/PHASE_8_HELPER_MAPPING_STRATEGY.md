# Phase 8: Helper Mapping Strategy

**Date**: 2025-12-20
**Purpose**: Systematically map all 195 unmapped helpers to directives
**Status**: In Progress

---

## Overview

**Goal**: Fill `used_by_directives` arrays for all 202 helpers (7 already done, 195 remaining)

**Approach**: Category-by-category, manual analysis using directive workflows

**Key Principle**: Careful, deliberate mapping - only map helpers actually used by directives

---

## Supporting Files

1. **Analysis Script**: `docs/helpers/json/map_helpers.py`
   - Automated keyword matching for initial suggestions
   - Generated HIGH/MEDIUM/LOW confidence matches

2. **Analysis Output**: `docs/helpers/json/mapping_analysis.txt`
   - Full output from script (427 lines)
   - 64 helpers with potential matches (32%)
   - 104 total suggestions

3. **Suggestions JSON**: `docs/helpers/json/mapping_suggestions.json`
   - Machine-readable suggestions
   - 12 HIGH confidence (≥0.5)
   - 66 MEDIUM confidence (0.3-0.5)
   - 26 LOW confidence (<0.3)

4. **Workflow Reference**: `docs/DIRECTIVE_WORKFLOW_PATH.md`
   - Complete workflow documentation
   - Shows which directives call which helpers

5. **Helper Analysis**: `docs/HELPER_MAPPING_ANALYSIS.md`
   - Helper usage patterns by directive category
   - Estimated helper counts per category

---

## Scope Definition

**Directives to Consider**: 63 (exclude 65 FP directives for now)
- Project Management: 38
- Git Integration: 6
- User System: 9
- User Preferences: 7
- Orchestrators: 3 (aifp_run, aifp_status, aifp_help)

**Helpers to Map**: 202 total
- Already mapped: 7 (3.5%)
- Remaining: 195

**Key Insight**: Not all helpers are called BY directives. Many helpers:
- Query directive metadata (used by AI, not directives)
- Are entry points (orchestrators)
- Are sub-helpers (called by other helpers, not directives)

**Realistic Estimate**: ~210-300 `used_by_directives` entries (not 1:1 mapping)

---

## Elimination Strategy

### What NOT to Map

**Core Helpers (33 total)**: Most query directives themselves
- `get_directive_by_name`, `get_all_directives` → Used by AI to look up directives
- `search_directives` → Already mapped (used by aifp_help, AI consultation)
- Only ~5-10 core helpers actually used by directives

**Sub-Helpers**: Helpers with `is_sub_helper: true`
- Called by other helpers, not directly by directives
- Still document them, but no `used_by_directives` needed

**Index Helper**: `get_databases`
- System-level utility, not directive-specific

---

## Priority Mapping Plan

### ✅ Priority 0: Already Mapped (7 helpers)

- [x] `search_directives` (core) - aifp_help, FP consultation
- [x] `get_directive_content` (core) - FP consultation
- [x] `find_directive_by_intent` (core) - user_preferences_update
- [x] `query_settings` (settings) - user_preferences_sync, tracking_toggle
- [x] `update_settings_entry` (settings) - user_preferences_update, tracking_toggle
- [x] `add_note` (project-3) - project_notes_log
- [x] `aifp_run` (orchestrators) - self-referential entry point

---

### ✅ Priority 1: Git Helpers (11 helpers → 6 directives) - COMPLETE

**Target Directives**:
1. `git_init` - directives-git.json:3
2. `git_detect_external_changes` - directives-git.json:97
3. `git_create_branch` - directives-git.json:202
4. `git_detect_conflicts` - directives-git.json:324
5. `git_merge_branch` - directives-git.json:456
6. `git_sync_state` - directives-git.json:631

**Helpers Mapped**: helpers-git.json (11 total)
- [x] `get_current_commit_hash` - Used by: git_init, git_sync_state
- [x] `get_current_branch` - Used by: git_init, git_sync_state
- [x] `get_git_status` - Used by: git_init
- [x] `detect_external_changes` - Implements: git_detect_external_changes, used by: git_sync_state
- [x] `create_user_branch` - Implements: git_create_branch
- [x] `get_user_name_for_branch` (sub-helper) - Used by: git_create_branch
- [x] `list_active_branches` - Query tool (no directive usage)
- [x] `detect_conflicts_before_merge` - Implements: git_detect_conflicts, used by: git_merge_branch
- [x] `merge_with_fp_intelligence` - Implements: git_merge_branch
- [x] `sync_git_state` - Implements: git_sync_state
- [x] `project_update_git_status` (sub-helper) - Used by: git_init, git_detect_external_changes, git_sync_state

**Total Mappings**: 17 `used_by_directives` entries (exceeded estimate of 11-15)

**Key Insights**:
- 5 helpers are MCP tools that implement directives directly (self-referential)
- 2 helpers are sub-helpers called by other helpers (marked is_sub_helper: true)
- 1 helper (list_active_branches) is a query tool not used by directives
- 10 of 11 helpers mapped (1 intentionally unmapped as query-only)

**Status**: ✅ COMPLETE (2025-12-20)

---

### ✅ Priority 2: User-Custom Helpers (16 helpers → 9 directives) - COMPLETE

**Target Directives**:
1. `user_directive_parse` - directives-user-system.json:14
2. `user_directive_validate` - directives-user-system.json:141
3. `user_directive_implement` - directives-user-system.json:230
4. `user_directive_approve` - directives-user-system.json:391
5. `user_directive_activate` - directives-user-system.json:481
6. `user_directive_monitor` - directives-user-system.json:611
7. `user_directive_update` - directives-user-system.json:713
8. `user_directive_deactivate` - directives-user-system.json:844
9. `user_directive_status` - directives-user-system.json:950

**Helpers Mapped**: helpers-user-custom.json (16 total)
- [x] `get_user_custom_tables` - Query tool (AI use only, no directive mapping)
- [x] `get_user_custom_fields` - Query tool (AI use only, no directive mapping)
- [x] `get_user_custom_schema` - Query tool (AI use only, no directive mapping)
- [x] `get_user_custom_json_parameters` - Query tool (AI use only, no directive mapping)
- [x] `get_from_user_custom` - Query tool (AI use only, no directive mapping)
- [x] `get_from_user_custom_where` - Query tool (AI use only, no directive mapping)
- [x] `query_user_custom` - Query tool (AI use only, no directive mapping)
- [x] `add_user_custom_entry` - Used by: user_directive_parse, user_directive_update
- [x] `update_user_custom_entry` - Used by: user_directive_validate, user_directive_implement, user_directive_approve, user_directive_activate, user_directive_deactivate, user_directive_update
- [x] `delete_user_custom_entry` - Used by: user_directive_update
- [x] `parse_directive_file` - Implements: user_directive_parse, used by: user_directive_update
- [x] `validate_directive_config` - Implements: user_directive_validate, used by: user_directive_update
- [x] `generate_handler_code` - Implements: user_directive_implement, used by: user_directive_update
- [x] `deploy_background_service` - Implements: user_directive_activate
- [x] `get_user_directive_status` - Implements: user_directive_status
- [x] `monitor_directive_execution` - Implements: user_directive_monitor

**Total Mappings**: 15 `used_by_directives` entries (within estimate of 20-30)

**Key Insights**:
- 6 orchestrator tools that implement directives directly
- 3 CRUD helpers (add/update/delete) used by multiple directives for database operations
- 7 query tools for AI use only (intentionally not mapped to directives)
- `update_user_custom_entry` has the most mappings (6) - central to status transitions
- `user_directive_update` is the most complex - uses 5 different helpers

**Status**: ✅ COMPLETE (2025-12-20)

---

### ✅ Priority 3: Settings Helpers (17 helpers → 6 directives) - COMPLETE

**Target Directives**:
1. `user_preferences_sync` - directives-user-pref.json:3
2. `user_preferences_update` - directives-user-pref.json:77
3. `user_preferences_learn` - directives-user-pref.json:182
4. `user_preferences_export` - directives-user-pref.json:263
5. `user_preferences_import` - directives-user-pref.json:332
6. `tracking_toggle` - directives-user-pref.json:499
7. `project_notes_log` - Uses helpers from helpers-project (add_note already mapped)

**Helpers Mapped**: helpers-settings.json (17 total)
- [x] `get_settings_tables` - Query tool (AI use only, no directive mapping)
- [x] `get_settings_fields` - Query tool (AI use only, no directive mapping)
- [x] `get_settings_schema` - Query tool (AI use only, no directive mapping)
- [x] `get_settings_json_parameters` - Query tool (AI use only, no directive mapping)
- [x] `get_from_settings` - Query tool (AI use only, no directive mapping)
- [x] `get_from_settings_where` - Query tool (AI use only, no directive mapping)
- [x] `query_settings` - Used by: user_preferences_sync, tracking_toggle, user_preferences_export
- [x] `add_settings_entry` - Used by: user_preferences_import
- [x] `update_settings_entry` - Used by: user_preferences_update, tracking_toggle
- [x] `delete_settings_entry` - Query tool (AI use only, no directive mapping)
- [x] `load_directive_preferences` - Used by: user_preferences_sync
- [x] `add_directive_preference` - Used by: user_preferences_update, user_preferences_learn
- [x] `get_user_setting` - Query tool (AI use only, no directive mapping)
- [x] `update_user_preferences` - Implements: user_preferences_update (orchestrator tool)
- [x] `apply_preferences_to_context` (sub-helper) - Used by: user_preferences_sync
- [x] `get_tracking_settings` - Used by: user_preferences_sync
- [x] `toggle_tracking_feature` - Implements: tracking_toggle

**Total Mappings**: 13 `used_by_directives` entries (within estimate of 18-25)

**Key Insights**:
- 2 orchestrator tools that implement directives (update_user_preferences, toggle_tracking_feature)
- 5 CRUD/data helpers used by multiple directives
- 1 sub-helper (apply_preferences_to_context)
- 8 query tools for AI use only (intentionally not mapped to directives)
- `query_settings` has the most mappings (3) - central to preferences system
- `project_notes_log` directive uses `add_note` from helpers-project-3 (already mapped in Priority 0)

**Status**: ✅ COMPLETE (2025-12-20)

---

### ✅ Priority 4: Orchestrator Helpers (12 helpers → 2 directives) - COMPLETE

**Target Directives**:
1. `aifp_run` - directives-project.json:3
2. `aifp_status` - directives-project.json:1644
3. `aifp_help` - Uses helpers from helpers-core (get_directive_content, search_directives - already mapped)

**Helpers Mapped**: helpers-orchestrators.json (12 total)
- [x] `aifp_run` - Implements: aifp_run (self-invocation)
- [x] `get_current_progress` - AI query tool (not used by directives)
- [x] `update_project_state` - AI convenience tool (not used by directives)
- [x] `batch_update_progress` - AI convenience tool (not used by directives)
- [x] `query_project_state` - AI query tool (not used by directives)
- [x] `validate_initialization` - AI validation tool (not used by directives)
- [x] `get_work_context` - AI query tool (not used by directives)
- [x] `aifp_status` - Implements: aifp_status (self-invocation), used by: aifp_run
- [x] `get_project_status` (sub-helper) - Used by: aifp_status
- [x] `get_project_context` - AI query tool (not used by directives)
- [x] `get_status_tree` (sub-helper) - Used by: aifp_status
- [x] `get_files_by_flow_context` - AI query tool (not used by directives)

**Total Mappings**: 5 `used_by_directives` entries (lower end of estimate 3-8)

**Key Insights**:
- 2 orchestrator tools that implement directives (aifp_run, aifp_status)
- 2 sub-helpers used by aifp_status (get_project_status, get_status_tree)
- 8 AI query/convenience tools (intentionally not mapped to directives)
- aifp_help directive uses core helpers already mapped in Priority 0
- Most orchestrators are entry points or AI tools, not called BY directives
- This validates the critical note: orchestrators serve AI, not other directives

**Status**: ✅ COMPLETE (2025-12-20)

---

### ✅ Priority 5: Core Helpers (metadata-only) - COMPLETE

**Already Mapped in Priority 0**: 3 helpers
- [x] `search_directives` - mapped in Priority 0 (aifp_help)
- [x] `get_directive_content` - mapped in Priority 0 (aifp_help)
- [x] `find_directive_by_intent` - mapped in Priority 0 (aifp_run)

**AI-Only Tools (30 remaining helpers, intentionally not mapped)**:
- [ ] `get_core_tables` - Schema query tool (AI use only)
- [ ] `get_core_fields` - Schema query tool (AI use only)
- [ ] `get_core_schema` - Schema query tool (AI use only)
- [ ] `get_from_core` - Generic query tool (AI use only)
- [ ] `get_from_core_where` - Generic query tool (AI use only)
- [ ] `query_core` - Generic query tool (AI use only)
- [ ] `get_directive_by_name` - AI directive lookup (not used by directives)
- [ ] `get_all_directives` - AI directive listing (not used by directives)
- [ ] `find_directives_by_intent_keyword` - AI query tool
- [ ] `get_directives_with_intent_keywords` - AI query tool
- [ ] `add_directive_intent_keyword` - Metadata management (AI use only)
- [ ] `remove_directive_intent_keyword` - Metadata management (AI use only)
- [ ] `get_directive_keywords` - AI query tool
- [ ] `get_all_directive_keywords` - AI query tool
- [ ] `get_all_intent_keywords_with_counts` - AI query tool
- [ ] `get_next_directives_from_status` - AI routing tool (not used by directives)
- [ ] `get_matching_next_directives` - AI routing tool (not used by directives)
- [ ] `get_completion_loop_target` - AI routing tool (not used by directives)
- [ ] `get_conditional_work_paths` - AI routing tool (not used by directives)
- [ ] `get_helper_by_name` - AI helper lookup (not used by directives)
- [ ] `get_helpers_by_database` - AI query tool
- [ ] `get_helpers_are_tool` - AI query tool
- [ ] `get_helpers_not_tool_not_sub` - AI query tool
- [ ] `get_helpers_are_sub` - AI query tool
- [ ] `get_helpers_for_directive` - AI query tool
- [ ] `get_directives_for_helper` - AI query tool
- [ ] `get_category_by_name` - AI query tool
- [ ] `get_categories` - AI query tool
- [ ] `get_directives_by_category` - AI query tool
- [ ] `get_directives_by_type` - AI query tool

**Total Mappings**: 0 new mappings (3 already mapped in Priority 0)

**Critical Note**: Most core helpers query directive metadata for AI use, not directive use
- `get_directive_by_name` → AI looks up directive details
- `get_all_directives` → AI lists available directives
- `get_next_directives_from_status` → AI routing logic, not called by directives
- Only 3 core helpers are called by directives, and they were already mapped in Priority 0

**Status**: ✅ COMPLETE (2025-12-20) - Metadata-only priority, no new mappings required

---

### ✅ Priority 6: Project Helpers - Tasks & Milestones (18 helpers → 10 directives) - COMPLETE

**Target Directives**:
1. `project_task_decomposition` - directives-project.json:324
2. `project_task_create` - directives-project.json:2158
3. `project_task_update` - directives-project.json:2213
4. `project_task_complete` - directives-project.json:2486
5. `project_subtask_create` - directives-project.json:2316
6. `project_subtask_complete` - directives-project.json:2593
7. `project_sidequest_create` - directives-project.json:2430
8. `project_sidequest_complete` - directives-project.json:2673
9. `project_item_create` - directives-project.json:2375
10. `project_milestone_complete` - directives-project.json:2767

**Helpers Mapped**: Selected from helpers-project-2.json, helpers-project-3.json
- [x] `add_completion_path` - Used by: project_task_decomposition
- [ ] `get_all_completion_paths` - Query tool (AI use only)
- [x] `get_next_completion_path` - Used by: project_milestone_complete
- [ ] `get_completion_paths_by_status` - Query tool (AI use only)
- [ ] `get_incomplete_completion_paths` - Query tool (AI use only)
- [x] `update_completion_path` - Used by: project_milestone_complete
- [ ] `delete_completion_path` - Query tool (AI use only)
- [ ] `reorder_completion_path` - Query tool (AI use only)
- [ ] `reorder_all_completion_paths` - Query tool (AI use only)
- [ ] `swap_completion_paths_order` - Query tool (AI use only)
- [x] `add_milestone` - Used by: project_task_decomposition
- [x] `get_milestones_by_path` - Used by: project_milestone_complete
- [ ] `get_milestones_by_status` - Query tool (AI use only)
- [ ] `get_incomplete_milestones` - Query tool (AI use only)
- [x] `update_milestone` - Used by: project_milestone_complete
- [ ] `delete_milestone` - Query tool (AI use only)
- [x] `add_task` - Used by: project_task_decomposition, project_task_create
- [x] `get_incomplete_tasks_by_milestone` - Used by: project_task_complete
- [ ] `get_incomplete_tasks` - Query tool (AI use only)
- [x] `get_tasks_by_milestone` - Used by: project_task_create
- [ ] `get_tasks_comprehensive` - Query tool (AI use only)
- [ ] `get_task_flows` - Query tool (AI use only)
- [ ] `get_task_files` - Query tool (AI use only)
- [x] `update_task` - Used by: project_task_update, project_task_complete, project_subtask_create, project_subtask_complete, project_sidequest_complete
- [ ] `delete_task` - Query tool (AI use only)
- [x] `add_subtask` - Used by: project_task_decomposition, project_subtask_create
- [ ] `get_incomplete_subtasks` - Query tool (AI use only)
- [x] `get_incomplete_subtasks_by_task` - Used by: project_subtask_create, project_subtask_complete
- [x] `get_subtasks_by_task` - Used by: project_subtask_complete
- [ ] `get_subtasks_comprehensive` - Query tool (AI use only)
- [x] `update_subtask` - Used by: project_task_update, project_subtask_complete
- [ ] `delete_subtask` - Query tool (AI use only)
- [x] `add_sidequest` - Used by: project_task_decomposition, project_sidequest_create
- [ ] `get_incomplete_sidequests` - Query tool (AI use only)
- [ ] `get_sidequests_comprehensive` - Query tool (AI use only)
- [ ] `get_sidequest_flows` - Query tool (AI use only)
- [ ] `get_sidequest_files` - Query tool (AI use only)
- [x] `update_sidequest` - Used by: project_task_update, project_sidequest_complete
- [ ] `delete_sidequest` - Query tool (AI use only)
- [x] `get_items_for_task` - Used by: project_item_create
- [ ] `get_items_for_subtask` - Query tool (AI use only)
- [ ] `get_items_for_sidequest` - Query tool (AI use only)
- [ ] `get_incomplete_items` - Query tool (AI use only)
- [ ] `delete_item` - Query tool (AI use only)

**Total Mappings**: 29 `used_by_directives` entries (below estimate of 60-80 due to many query-only helpers)

**Key Insights**:
- 18 helpers actively used by directives (13 from helpers-project-3.json, 5 from helpers-project-2.json)
- 25 helpers are query tools for AI use only (intentionally not mapped to directives)
- `update_task` has the most mappings (5) - central task state manager
- `add_note` gained additional mapping for project_sidequest_complete (lessons learned logging)
- Most CRUD operations (add_task, add_subtask, add_sidequest, add_milestone, add_completion_path) called by project_task_decomposition
- Most status updates (update_task, update_subtask, update_sidequest, update_milestone) used by multiple directives

**Status**: ✅ COMPLETE (2025-12-20)

---

### ✅ Priority 7: Project Helpers - Files & Functions (17 helpers → 5 directives) - COMPLETE

**Target Directives**:
1. `project_file_write` - directives-project.json:524
2. `project_file_read` - directives-project.json:2048
3. `project_file_delete` - directives-project.json:2099
4. `project_reserve_finalize` - directives-project.json:625
5. `project_update_db` - directives-project.json:625

**Helpers Mapped**: Selected from helpers-project-1.json, helpers-project-2.json
- [x] `reserve_file` - Used by: project_reserve_finalize, project_file_write
- [ ] `reserve_files` - Batch tool (AI use only)
- [x] `finalize_file` - Used by: project_reserve_finalize, project_file_write, project_update_db
- [ ] `finalize_files` - Batch tool (AI use only)
- [ ] `get_file_by_name` - Query tool (AI use only)
- [x] `get_file_by_path` - Used by: project_file_read, project_file_delete
- [x] `update_file` - Used by: project_update_db
- [x] `file_has_changed` - Used by: project_file_read
- [ ] `update_file_timestamp` - Sub-helper (called by finalize/update functions)
- [x] `delete_file` - Used by: project_file_delete
- [x] `reserve_function` - Used by: project_reserve_finalize, project_file_write
- [ ] `reserve_functions` - Batch tool (AI use only)
- [x] `finalize_function` - Used by: project_reserve_finalize, project_file_write, project_update_db
- [ ] `finalize_functions` - Batch tool (AI use only)
- [ ] `get_function_by_name` - Query tool (AI use only)
- [x] `get_functions_by_file` - Used by: project_file_read
- [x] `update_function` - Used by: project_update_db
- [x] `update_functions_for_file` - Used by: project_update_db
- [ ] `update_function_file_location` - Query tool (AI use only)
- [x] `delete_function` - Used by: project_file_delete
- [x] `reserve_type` - Used by: project_reserve_finalize
- [ ] `reserve_types` - Batch tool (AI use only)
- [x] `finalize_type` - Used by: project_reserve_finalize
- [ ] `finalize_types` - Batch tool (AI use only)
- [ ] `update_type` - Query tool (AI use only)
- [ ] `delete_type` - Query tool (AI use only)
- [ ] `add_types_functions` - Query tool (AI use only)
- [ ] `update_type_function_role` - Query tool (AI use only)
- [ ] `delete_type_function` - Query tool (AI use only)
- [x] `add_interaction` - Used by: project_update_db
- [ ] `add_interactions` - Batch tool (AI use only)
- [ ] `update_interaction` - Query tool (AI use only)
- [ ] `delete_interaction` - Query tool (AI use only)

**Total Mappings**: 27 `used_by_directives` entries (below estimate of 50-70 due to many batch/query-only helpers)

**Key Insights**:
- 17 helpers actively used by directives (15 from helpers-project-1.json, 2 from helpers-project-2.json)
- 18 helpers are batch/query tools for AI use only (intentionally not mapped to directives)
- Reserve/finalize pattern used extensively: reserve → write with embedded ID → finalize
- `finalize_file` and `finalize_function` each have 3 mappings - called by multiple directives
- `project_update_db` is the main consumer of update helpers (update_file, update_function, update_functions_for_file, add_interaction)
- `project_file_read` provides comprehensive file context using get_file_by_path, get_functions_by_file, file_has_changed
- `project_file_delete` handles cascade cleanup using delete_file, delete_function
- Directives not mapped: `project_add_path` (uses Priority 6 helpers), `project_refactor_path` (uses query-only reorder helpers)

**Status**: ✅ COMPLETE (2025-12-20)

---

### ✅ Priority 8: Project Helpers - Remaining (16 helpers → 6 directives) - COMPLETE

**Total Mappings**: 25 `used_by_directives` entries

**Target Directives Used**:
1. `project_init` - directives-project.json:118 (main initialization)
2. `project_blueprint_read` - directives-project.json:1959 (blueprint parsing)
3. `project_blueprint_update` - directives-project.json:2045 (blueprint updates)
4. `project_theme_flow_mapping` - directives-project.json:1228 (theme/flow associations)
5. `project_metrics` - directives-project.json:1314 (metrics collection)
6. `project_auto_summary` - directives-project.json:1710 (summary generation)
7. `project_dependency_map` - directives-project.json:1671 (dependency graphs)

**Helpers Mapped**: helpers-project-1.json, helpers-project-2.json, helpers-project-3.json (34 total remaining)

**Blueprint & Infrastructure (helpers-project-1.json)**:
- [x] `create_project` - 1 mapping (project_init)
- [x] `get_project` - 2 mappings (project_blueprint_read, project_blueprint_update)
- [x] `update_project` - 1 mapping (project_blueprint_update)
- [x] `blueprint_has_changed` - 2 mappings (project_blueprint_read, project_blueprint_update)
- [x] `get_infrastructure_by_type` - 2 mappings (project_init, project_blueprint_read)

**Theme & Flow (helpers-project-2.json)**:
- [x] `get_theme_by_name` - 2 mappings (project_theme_flow_mapping, project_init)
- [x] `get_flow_by_name` - 2 mappings (project_theme_flow_mapping, project_init)
- [x] `get_all_themes` - 1 mapping (project_blueprint_read)
- [x] `get_all_flows` - 1 mapping (project_blueprint_read)
- [x] `add_theme` - 2 mappings (project_init, project_theme_flow_mapping)
- [x] `add_flow` - 2 mappings (project_init, project_theme_flow_mapping)
- [x] `get_flows_for_theme` - 1 mapping (project_theme_flow_mapping)
- [x] `get_files_by_flow` - 1 mapping (project_dependency_map)
- [x] `get_flows_for_file` - 1 mapping (project_dependency_map)

**Notes (helpers-project-3.json)**:
- [x] `get_notes_comprehensive` - 2 mappings (project_auto_summary, project_metrics)
- [x] `search_notes` - 2 mappings (project_auto_summary, project_metrics)

**AI-Only Tools (intentionally not mapped)**:
- [ ] `get_project_tables` - Schema query tool (AI use only)
- [ ] `get_project_fields` - Schema query tool (AI use only)
- [ ] `get_project_schema` - Schema query tool (AI use only)
- [ ] `get_project_json_parameters` - Schema query tool (AI use only)
- [ ] `get_from_project` - Generic query tool (AI use only)
- [ ] `get_from_project_where` - Generic query tool (AI use only)
- [ ] `query_project` - Generic query tool (AI use only)
- [ ] `add_project_entry` - Generic CRUD tool (AI use only)
- [ ] `update_project_entry` - Generic CRUD tool (AI use only)
- [ ] `delete_project_entry` - Generic CRUD tool (AI use only)
- [ ] `update_theme` - CRUD tool (AI use only)
- [ ] `delete_theme` - CRUD tool (AI use only)
- [ ] `update_flow` - CRUD tool (AI use only)
- [ ] `delete_flow` - CRUD tool (AI use only)
- [ ] `get_file_ids_from_flows` - Query tool (AI use only)
- [ ] `get_themes_for_flow` - Query tool (AI use only)
- [ ] `update_note` - CRUD tool (AI use only)
- [ ] `delete_note` - CRUD tool (AI use only, discouraged)

**Key Insights**:
- 16 helpers actively used by directives (5 from helpers-project-1.json, 9 from helpers-project-2.json, 2 from helpers-project-3.json)
- 18 helpers are schema/query/CRUD tools for AI use only
- `project_init` is main consumer of initialization helpers (create_project, add_theme, add_flow, get_theme_by_name, get_flow_by_name, get_infrastructure_by_type)
- `project_blueprint_read` uses fallback helpers when ProjectBlueprint.md missing (get_project, get_infrastructure_by_type, get_all_themes, get_all_flows, blueprint_has_changed)
- `project_blueprint_update` uses version management helpers (get_project, update_project, blueprint_has_changed)
- `project_theme_flow_mapping` uses theme/flow CRUD and validation helpers
- `project_metrics` and `project_auto_summary` both use note query helpers for historical data
- `project_dependency_map` uses flow-file association helpers

**Status**: ✅ COMPLETE (2025-12-20)

---

## Progress Tracking

### Overall Progress
- **Total Helpers**: 202
- **Already Mapped**: 91 (45.0%) - Priority 0 (7) + Priority 1 (11) + Priority 2 (9) + Priority 3 (9) + Priority 4 (4) + Priority 5 (0, metadata only) + Priority 6 (18) + Priority 7 (17) + Priority 8 (16)
- **Remaining**: 111 (55.0%)

### By Priority
- [x] Priority 0: Already Mapped (7 helpers) - 100%
- [x] Priority 1: Git Helpers (11 helpers) - 100% ✅ (2025-12-20)
- [x] Priority 2: User-Custom Helpers (16 helpers) - 100% ✅ (2025-12-20)
- [x] Priority 3: Settings Helpers (17 helpers) - 100% ✅ (2025-12-20)
- [x] Priority 4: Orchestrator Helpers (12 helpers) - 100% ✅ (2025-12-20)
- [x] Priority 5: Core Helpers (33 helpers) - 100% ✅ (2025-12-20) - Metadata only, 3 already mapped in Priority 0
- [x] Priority 6: Project - Tasks & Milestones (18 helpers mapped) - 100% ✅ (2025-12-20)
- [x] Priority 7: Project - Files & Functions (17 helpers mapped) - 100% ✅ (2025-12-20)
- [x] Priority 8: Project - Remaining (16 helpers mapped) - 100% ✅ (2025-12-20)

### Total Mappings
- **Target**: 210-300 `used_by_directives` entries
- **Completed**: 138 (7 Priority 0 + 17 Priority 1 + 15 Priority 2 + 13 Priority 3 + 5 Priority 4 + 0 Priority 5 + 29 Priority 6 + 27 Priority 7 + 25 Priority 8)
- **Estimated Remaining**: 72-162 (lower bound likely, most unmapped helpers are AI-only tools)

---

## Mapping Template

For each helper, add this to its JSON entry:

```json
"used_by_directives": [
  {
    "directive_name": "directive_name_here",
    "execution_context": "when/why helper is called",
    "sequence_order": 1,
    "is_required": true,
    "parameters_mapping": {
      "helper_param": "directive_workflow_value"
    },
    "description": "Brief description of how directive uses helper"
  }
]
```

---

## Completion Criteria

### Per Priority
- [ ] All helpers reviewed for directive usage
- [ ] All `used_by_directives` entries added to helper JSON files
- [ ] Mappings verified against directive workflows
- [ ] Helper JSON files validated (proper JSON syntax)
- [ ] Progress checkboxes updated in this document

### Overall Phase 8
- [ ] All 8 priorities complete
- [ ] Validation script created and passing
- [ ] Documentation updated (DIRECTIVES_MAPPING_PROGRESS.md, HELPER_FUNCTIONS_MAPPING_PROGRESS.md)
- [ ] Final statistics generated
- [ ] Phase 8 completion report created

---

## Next Steps

1. ✅ **Priority 1 COMPLETE**: Git Helpers (11 helpers, 17 mappings)
   - All helpers mapped to 6 git directives
   - Identified 5 tool helpers, 2 sub-helpers, 1 query-only
   - helpers-git.json fully updated

2. ✅ **Priority 2 COMPLETE**: User-Custom Helpers (16 helpers, 15 mappings)
   - All helpers mapped to 9 user directive system directives
   - Identified 6 orchestrator tools, 3 CRUD helpers, 7 query-only
   - helpers-user-custom.json fully updated

3. ✅ **Priority 3 COMPLETE**: Settings Helpers (17 helpers, 13 mappings)
   - All helpers mapped to 6 user preference directives
   - Identified 2 orchestrator tools, 5 data helpers, 1 sub-helper, 8 query-only
   - helpers-settings.json fully updated

4. ✅ **Priority 4 COMPLETE**: Orchestrator Helpers (12 helpers, 5 mappings)
   - 4 helpers mapped to 2 orchestrator directives
   - Identified 2 orchestrator tools, 2 sub-helpers, 8 AI query tools
   - helpers-orchestrators.json fully updated

5. ✅ **Priority 5 COMPLETE**: Core Helpers (33 helpers, 0 new mappings)
   - 3 helpers already mapped in Priority 0
   - 30 helpers are AI query/navigation tools (intentionally not mapped)
   - helpers-core.json metadata updated only

6. ✅ **Priority 6 COMPLETE**: Project Helpers - Tasks & Milestones (18 helpers, 29 mappings)
   - 18 helpers mapped to 10 task management directives
   - Identified 13 CRUD/update helpers from helpers-project-3.json
   - Identified 5 completion path/milestone helpers from helpers-project-2.json
   - 25 query tools for AI use only
   - helpers-project-2.json and helpers-project-3.json updated

7. ✅ **Priority 7 COMPLETE**: Project Helpers - Files & Functions (17 helpers, 27 mappings)
   - 17 helpers mapped to 5 file/function directives
   - Identified 15 reserve/finalize/CRUD helpers from helpers-project-1.json
   - Identified 2 type/interaction helpers from helpers-project-2.json
   - 18 batch/query tools for AI use only
   - Reserve/finalize pattern extensively used for ID embedding
   - helpers-project-1.json and helpers-project-2.json updated

8. **Create validation script** after Priority 8 complete

9. **Continue with Priority 8** (Project remaining: 37 helpers → ~21 directives)

10. **Final review and documentation update**

---

**Created**: 2025-12-20
**Last Updated**: 2025-12-20
**Status**: Priorities 1-7 Complete (75 helpers, 113 mappings, 37.1%)
**Current Priority**: Ready for Priority 8 - Project Remaining

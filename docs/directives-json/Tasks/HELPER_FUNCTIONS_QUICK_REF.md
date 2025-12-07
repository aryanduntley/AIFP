# Helper Functions Quick Reference

**Purpose**: Quick lookup for helper function names and locations
**Generated**: 2025-12-07
**Source**: `docs/helpers/registry/*.json`

---

## Usage

Use this reference when manually updating directive MD files to verify helper function names.

**Verify a helper exists**:
1. Search this file for the helper name
2. If found, helper exists in registry
3. If not found, helper may be removed or renamed (check CONSOLIDATION_REPORT.md)

---

## All Helper Functions

Total helpers documented: **337**

| Helper Name | Registry File | Line |
|-------------|---------------|------|
| `add_ai_interaction` | helpers_registry_user_settings.json | 512 |
| `add_completion_path` | helpers_registry_project_workflow_setters.json | 222 |
| `add_directive_preference` | helpers_registry_user_settings.json | 202 |
| `add_file_flows` | helpers_registry_project_structure_setters.json | 810 |
| `add_flow` | helpers_registry_project_workflow_setters.json | 105 |
| `add_flow_themes` | helpers_registry_project_workflow_setters.json | 177 |
| `add_fp_tracking` | helpers_registry_user_settings.json | 718 |
| `add_infrastructure` | helpers_registry_project_structure_setters.json | 33 |
| `add_interaction` | helpers_registry_project_structure_setters.json | 719 |
| `add_interactions` | helpers_registry_project_structure_setters.json | 742 |
| `add_issues_report` | helpers_registry_user_settings.json | 994 |
| `add_item` | helpers_registry_project_workflow_setters.json | 687 |
| `add_milestone` | helpers_registry_project_workflow_setters.json | 381 |
| `add_note` | helpers_registry_project_workflow_setters.json | 757 |
| `add_setting` | helpers_registry_user_settings.json | 32 |
| `add_sidequest` | helpers_registry_project_workflow_setters.json | 606 |
| `add_subtask` | helpers_registry_project_workflow_setters.json | 530 |
| `add_task` | helpers_registry_project_workflow_setters.json | 452 |
| `add_theme` | helpers_registry_project_workflow_setters.json | 33 |
| `add_tracking_setting` | helpers_registry_user_settings.json | 1261 |
| `add_type_function` | helpers_registry_project_structure_setters.json | 632 |
| `add_types_functions` | helpers_registry_project_structure_setters.json | 654 |
| `add_user_directive` | helpers_registry_user_directives_setters.json | 33 |
| `add_user_directive_dependency` | helpers_registry_user_directives_setters.json | 318 |
| `add_user_directive_execution` | helpers_registry_user_directives_setters.json | 235 |
| `add_user_directive_helper` | helpers_registry_user_directives_setters.json | 635 |
| `add_user_directive_implementation` | helpers_registry_user_directives_setters.json | 400 |
| `add_user_directive_relationship` | helpers_registry_user_directives_setters.json | 485 |
| `add_user_helper_function` | helpers_registry_user_directives_setters.json | 556 |
| `add_user_logging_config` | helpers_registry_user_directives_setters.json | 787 |
| `add_user_source_file` | helpers_registry_user_directives_setters.json | 709 |
| `batch_update_progress` | helpers_registry_project_orchestrators.json | 89 |
| `blueprint_has_changed` | helpers_registry_project_core.json | 137 |
| `create_project` | helpers_registry_project_core.json | 65 |
| `create_user_branch` | helpers_registry_git.json | 116 |
| `delete_ai_interaction` | helpers_registry_user_settings.json | 694 |
| `delete_completion_path` | helpers_registry_project_workflow_setters.json | 268 |
| `delete_directive_preference` | helpers_registry_user_settings.json | 487 |
| `delete_file` | helpers_registry_project_structure_setters.json | 252 |
| `delete_file_flow` | helpers_registry_project_structure_setters.json | 831 |
| `delete_flow` | helpers_registry_project_workflow_setters.json | 151 |
| `delete_flow_themes` | helpers_registry_project_workflow_setters.json | 198 |
| `delete_fp_tracking` | helpers_registry_user_settings.json | 970 |
| `delete_function` | helpers_registry_project_structure_setters.json | 464 |
| `delete_infrastructure` | helpers_registry_project_structure_setters.json | 77 |
| `delete_interaction` | helpers_registry_project_structure_setters.json | 786 |
| `delete_issues_report` | helpers_registry_user_settings.json | 1237 |
| `delete_item` | helpers_registry_project_workflow_setters.json | 731 |
| `delete_milestone` | helpers_registry_project_workflow_setters.json | 427 |
| `delete_note` | helpers_registry_project_workflow_setters.json | 809 |
| `delete_setting` | helpers_registry_user_settings.json | 177 |
| `delete_sidequest` | helpers_registry_project_workflow_setters.json | 659 |
| `delete_subtask` | helpers_registry_project_workflow_setters.json | 578 |
| `delete_task` | helpers_registry_project_workflow_setters.json | 502 |
| `delete_theme` | helpers_registry_project_workflow_setters.json | 79 |
| `delete_tracking_setting` | helpers_registry_user_settings.json | 1423 |
| `delete_type` | helpers_registry_project_structure_setters.json | 606 |
| `delete_type_function` | helpers_registry_project_structure_setters.json | 695 |
| `delete_user_directive` | helpers_registry_user_directives_setters.json | 121 |
| `delete_user_directive_dependency` | helpers_registry_user_directives_setters.json | 380 |
| `delete_user_directive_execution` | helpers_registry_user_directives_setters.json | 298 |
| `delete_user_directive_helper` | helpers_registry_user_directives_setters.json | 689 |
| `delete_user_directive_implementation` | helpers_registry_user_directives_setters.json | 464 |
| `delete_user_directive_relationship` | helpers_registry_user_directives_setters.json | 536 |
| `delete_user_helper_function` | helpers_registry_user_directives_setters.json | 614 |
| `delete_user_logging_config` | helpers_registry_user_directives_setters.json | 861 |
| `delete_user_source_file` | helpers_registry_user_directives_setters.json | 767 |
| `detect_conflicts_before_merge` | helpers_registry_git.json | 140 |
| `detect_external_changes` | helpers_registry_git.json | 95 |
| `file_has_changed` | helpers_registry_project_structure_setters.json | 279 |
| `finalize_file` | helpers_registry_project_structure_setters.json | 143 |
| `finalize_files` | helpers_registry_project_structure_setters.json | 168 |
| `finalize_function` | helpers_registry_project_structure_setters.json | 344 |
| `finalize_functions` | helpers_registry_project_structure_setters.json | 370 |
| `finalize_type` | helpers_registry_project_structure_setters.json | 535 |
| `finalize_types` | helpers_registry_project_structure_setters.json | 561 |
| `find_directives` | helpers_registry_mcp_orchestrators.json | 33 |
| `find_helpers` | helpers_registry_mcp_orchestrators.json | 60 |
| `get_ai_ineractions_by_directive` | helpers_registry_user_settings.json | 610 |
| `get_ai_interaction` | helpers_registry_user_settings.json | 561 |
| `get_ai_interactions_by_type` | helpers_registry_user_settings.json | 585 |
| `get_all_completion_paths` | helpers_registry_project_workflow_getters.json | 426 |
| `get_all_file_flows` | helpers_registry_project_structure_getters.json | 660 |
| `get_all_flow_themes` | helpers_registry_project_workflow_getters.json | 408 |
| `get_all_flows` | helpers_registry_project_workflow_getters.json | 219 |
| `get_all_settings` | helpers_registry_user_settings.json | 69 |
| `get_all_themes` | helpers_registry_project_workflow_getters.json | 79 |
| `get_all_user_logging_config` | helpers_registry_user_directives_getters.json | 1243 |
| `get_categories` | helpers_registry_core.json | 259 |
| `get_categories_by_directive` | helpers_registry_core.json | 367 |
| `get_category_description` | helpers_registry_core.json | 325 |
| `get_category_id` | helpers_registry_core.json | 277 |
| `get_category_name` | helpers_registry_core.json | 301 |
| `get_completion_path_by_id` | helpers_registry_project_workflow_getters.json | 467 |
| `get_completion_path_by_order` | helpers_registry_project_workflow_getters.json | 444 |
| `get_completion_paths` | helpers_registry_project_workflow_getters.json | 550 |
| `get_completion_paths_by_status` | helpers_registry_project_workflow_getters.json | 508 |
| `get_current_branch` | helpers_registry_git.json | 54 |
| `get_current_commit_hash` | helpers_registry_git.json | 33 |
| `get_current_progress` | helpers_registry_project_orchestrators.json | 33 |
| `get_directive` | helpers_registry_core.json | 32 |
| `get_directive_branch` | helpers_registry_core.json | 862 |
| `get_directive_by_name` | helpers_registry_core.json | 58 |
| `get_directive_confidence` | helpers_registry_core.json | 160 |
| `get_directive_depth` | helpers_registry_core.json | 914 |
| `get_directive_id` | helpers_registry_core.json | 211 |
| `get_directive_md` | helpers_registry_core.json | 134 |
| `get_directive_name` | helpers_registry_core.json | 235 |
| `get_directive_preference` | helpers_registry_user_settings.json | 251 |
| `get_directive_preference_by_id` | helpers_registry_user_settings.json | 283 |
| `get_directive_preferences` | helpers_registry_user_settings.json | 314 |
| `get_directive_preferences_by_directive` | helpers_registry_user_settings.json | 377 |
| `get_directive_preferences_by_directives` | helpers_registry_user_settings.json | 409 |
| `get_directive_preferences_by_id` | helpers_registry_user_settings.json | 346 |
| `get_directive_siblings` | helpers_registry_core.json | 888 |
| `get_directive_tree` | helpers_registry_core.json | 829 |
| `get_directive_workflow` | helpers_registry_core.json | 185 |
| `get_directives` | helpers_registry_core.json | 84 |
| `get_directives_by_category` | helpers_registry_core.json | 342 |
| `get_directives_by_name` | helpers_registry_core.json | 109 |
| `get_directives_for_helper` | helpers_registry_core.json | 796 |
| `get_file` | helpers_registry_project_structure_getters.json | 113 |
| `get_file_by_checksum` | helpers_registry_project_structure_getters.json | 235 |
| `get_file_by_name` | helpers_registry_project_structure_getters.json | 155 |
| `get_file_by_path` | helpers_registry_project_structure_getters.json | 195 |
| `get_file_ids_from_flows` | helpers_registry_project_structure_getters.json | 597 |
| `get_file_ids_from_flows` | helpers_registry_project_workflow_getters.json | 237 |
| `get_files` | helpers_registry_project_structure_getters.json | 134 |
| `get_files_by_flow` | helpers_registry_project_structure_getters.json | 618 |
| `get_files_by_flow_context` | helpers_registry_project_structure_getters.json | 679 |
| `get_files_by_flow_context` | helpers_registry_project_workflow_getters.json | 1420 |
| `get_files_by_name` | helpers_registry_project_structure_getters.json | 175 |
| `get_files_by_path` | helpers_registry_project_structure_getters.json | 215 |
| `get_flow` | helpers_registry_project_workflow_getters.json | 172 |
| `get_flow_name_by_id` | helpers_registry_project_workflow_getters.json | 313 |
| `get_flow_names_by_ids` | helpers_registry_project_workflow_getters.json | 336 |
| `get_flows` | helpers_registry_project_workflow_getters.json | 195 |
| `get_flows_by_confidence` | helpers_registry_project_workflow_getters.json | 289 |
| `get_flows_by_maker` | helpers_registry_project_workflow_getters.json | 261 |
| `get_flows_for_file` | helpers_registry_project_structure_getters.json | 639 |
| `get_flows_for_theme` | helpers_registry_project_workflow_getters.json | 360 |
| `get_fp_tracking` | helpers_registry_user_settings.json | 774 |
| `get_fp_tracking_by_file` | helpers_registry_user_settings.json | 847 |
| `get_fp_tracking_by_function` | helpers_registry_user_settings.json | 798 |
| `get_fp_tracking_by_functions` | helpers_registry_user_settings.json | 823 |
| `get_fp_tracking_by_score_range` | helpers_registry_user_settings.json | 872 |
| `get_function` | helpers_registry_project_structure_getters.json | 255 |
| `get_function_by_name` | helpers_registry_project_structure_getters.json | 277 |
| `get_functions` | helpers_registry_project_structure_getters.json | 298 |
| `get_functions_by_file` | helpers_registry_project_structure_getters.json | 319 |
| `get_git_status` | helpers_registry_git.json | 74 |
| `get_helper_by_id` | helpers_registry_core.json | 536 |
| `get_helper_by_name` | helpers_registry_core.json | 561 |
| `get_helper_statements` | helpers_registry_core.json | 713 |
| `get_helper_statements_by_id` | helpers_registry_core.json | 738 |
| `get_helpers_are_sub` | helpers_registry_core.json | 695 |
| `get_helpers_are_tool` | helpers_registry_core.json | 659 |
| `get_helpers_by_database` | helpers_registry_core.json | 634 |
| `get_helpers_by_id` | helpers_registry_core.json | 586 |
| `get_helpers_by_name` | helpers_registry_core.json | 610 |
| `get_helpers_for_directive` | helpers_registry_core.json | 762 |
| `get_helpers_not_tool_not_sub` | helpers_registry_core.json | 677 |
| `get_inactive_interactions_for_directive` | helpers_registry_core.json | 511 |
| `get_incomplete_completion_paths` | helpers_registry_project_workflow_getters.json | 532 |
| `get_incomplete_items` | helpers_registry_project_workflow_getters.json | 1203 |
| `get_incomplete_milestones` | helpers_registry_project_workflow_getters.json | 622 |
| `get_incomplete_sidequests` | helpers_registry_project_workflow_getters.json | 967 |
| `get_incomplete_subtasks` | helpers_registry_project_workflow_getters.json | 847 |
| `get_incomplete_subtasks_by_task` | helpers_registry_project_workflow_getters.json | 865 |
| `get_incomplete_tasks` | helpers_registry_project_workflow_getters.json | 675 |
| `get_incomplete_tasks_by_milestone` | helpers_registry_project_workflow_getters.json | 640 |
| `get_infrastructure` | helpers_registry_project_structure_getters.json | 33 |
| `get_infrastructure_by_type` | helpers_registry_project_structure_getters.json | 53 |
| `get_infrastructure_by_type_value` | helpers_registry_project_structure_getters.json | 93 |
| `get_infrastructure_by_value` | helpers_registry_project_structure_getters.json | 73 |
| `get_interaction` | helpers_registry_project_structure_getters.json | 487 |
| `get_interaction_by_name` | helpers_registry_project_structure_getters.json | 574 |
| `get_interactions` | helpers_registry_project_structure_getters.json | 507 |
| `get_interactions_by_target` | helpers_registry_project_structure_getters.json | 528 |
| `get_interactions_by_type` | helpers_registry_project_structure_getters.json | 551 |
| `get_interactions_by_weight` | helpers_registry_core.json | 443 |
| `get_interactions_for_directive` | helpers_registry_core.json | 392 |
| `get_interactions_for_directive_as_target` | helpers_registry_core.json | 418 |
| `get_interactions_for_directive_with_relationship` | helpers_registry_core.json | 480 |
| `get_issues_report` | helpers_registry_user_settings.json | 1049 |
| `get_issues_report_by_title` | helpers_registry_user_settings.json | 1097 |
| `get_issues_reports_by_directive` | helpers_registry_user_settings.json | 1121 |
| `get_issues_reports_by_status` | helpers_registry_user_settings.json | 1146 |
| `get_issues_reports_by_type` | helpers_registry_user_settings.json | 1073 |
| `get_items_for_sidequest` | helpers_registry_project_workflow_getters.json | 1174 |
| `get_items_for_subtask` | helpers_registry_project_workflow_getters.json | 1145 |
| `get_items_for_task` | helpers_registry_project_workflow_getters.json | 1116 |
| `get_milestones_by_path` | helpers_registry_project_workflow_getters.json | 574 |
| `get_milestones_by_status` | helpers_registry_project_workflow_getters.json | 598 |
| `get_next_completion_path` | helpers_registry_project_workflow_getters.json | 490 |
| `get_note` | helpers_registry_project_workflow_getters.json | 1238 |
| `get_notes` | helpers_registry_project_workflow_getters.json | 1261 |
| `get_notes_comprehensive` | helpers_registry_project_workflow_getters.json | 1285 |
| `get_notes_content_contains` | helpers_registry_project_workflow_getters.json | 1396 |
| `get_project` | helpers_registry_project_core.json | 92 |
| `get_setting` | helpers_registry_user_settings.json | 87 |
| `get_settings` | helpers_registry_user_settings.json | 112 |
| `get_sidequest_files` | helpers_registry_project_workflow_getters.json | 1063 |
| `get_sidequest_flows` | helpers_registry_project_workflow_getters.json | 1039 |
| `get_sidequests_by_flow` | helpers_registry_project_workflow_getters.json | 1092 |
| `get_sidequests_comprehensive` | helpers_registry_project_workflow_getters.json | 985 |
| `get_subtasks_by_task` | helpers_registry_project_workflow_getters.json | 889 |
| `get_subtasks_comprehensive` | helpers_registry_project_workflow_getters.json | 918 |
| `get_system_context` | helpers_registry_mcp_orchestrators.json | 87 |
| `get_task_files` | helpers_registry_project_workflow_getters.json | 794 |
| `get_task_flows` | helpers_registry_project_workflow_getters.json | 770 |
| `get_tasks_by_flow` | helpers_registry_project_workflow_getters.json | 823 |
| `get_tasks_by_milestone` | helpers_registry_project_workflow_getters.json | 697 |
| `get_tasks_comprehensive` | helpers_registry_project_workflow_getters.json | 721 |
| `get_theme` | helpers_registry_project_workflow_getters.json | 33 |
| `get_theme_by_name` | helpers_registry_project_workflow_getters.json | 56 |
| `get_theme_name_by_id` | helpers_registry_project_workflow_getters.json | 149 |
| `get_themes_by_confidence` | helpers_registry_project_workflow_getters.json | 125 |
| `get_themes_by_maker` | helpers_registry_project_workflow_getters.json | 97 |
| `get_themes_for_flow` | helpers_registry_project_workflow_getters.json | 384 |
| `get_tracking_setting` | helpers_registry_user_settings.json | 1304 |
| `get_tracking_setting_by_name` | helpers_registry_user_settings.json | 1346 |
| `get_tracking_settings_enabled` | helpers_registry_user_settings.json | 1328 |
| `get_type` | helpers_registry_project_structure_getters.json | 341 |
| `get_type_function_by_id` | helpers_registry_project_structure_getters.json | 404 |
| `get_type_functions_by_function` | helpers_registry_project_structure_getters.json | 424 |
| `get_type_functions_by_role` | helpers_registry_project_structure_getters.json | 466 |
| `get_type_functions_by_type` | helpers_registry_project_structure_getters.json | 445 |
| `get_types` | helpers_registry_project_structure_getters.json | 363 |
| `get_types_by_file` | helpers_registry_project_structure_getters.json | 383 |
| `get_user_directive` | helpers_registry_user_directives_getters.json | 33 |
| `get_user_directive_by_name` | helpers_registry_user_directives_getters.json | 84 |
| `get_user_directive_dependencies_by_directive` | helpers_registry_user_directives_getters.json | 493 |
| `get_user_directive_dependencies_by_directive_required` | helpers_registry_user_directives_getters.json | 591 |
| `get_user_directive_dependencies_by_required` | helpers_registry_user_directives_getters.json | 567 |
| `get_user_directive_dependencies_by_status` | helpers_registry_user_directives_getters.json | 543 |
| `get_user_directive_dependencies_by_type` | helpers_registry_user_directives_getters.json | 519 |
| `get_user_directive_dependency` | helpers_registry_user_directives_getters.json | 468 |
| `get_user_directive_execution` | helpers_registry_user_directives_getters.json | 233 |
| `get_user_directive_executions_by_avg_execution_time` | helpers_registry_user_directives_getters.json | 284 |
| `get_user_directive_executions_by_directive` | helpers_registry_user_directives_getters.json | 259 |
| `get_user_directive_executions_by_error_count` | helpers_registry_user_directives_getters.json | 345 |
| `get_user_directive_executions_by_future_schedule` | helpers_registry_user_directives_getters.json | 406 |
| `get_user_directive_executions_by_max_execution_time` | helpers_registry_user_directives_getters.json | 315 |
| `get_user_directive_executions_by_past_schedule` | helpers_registry_user_directives_getters.json | 437 |
| `get_user_directive_executions_by_total_executions` | helpers_registry_user_directives_getters.json | 376 |
| `get_user_directive_helper` | helpers_registry_user_directives_getters.json | 1031 |
| `get_user_directive_helpers` | helpers_registry_user_directives_getters.json | 1055 |
| `get_user_directive_helpers_by_directive` | helpers_registry_user_directives_getters.json | 1079 |
| `get_user_directive_helpers_by_function` | helpers_registry_user_directives_getters.json | 1112 |
| `get_user_directive_implementation` | helpers_registry_user_directives_getters.json | 621 |
| `get_user_directive_implementations_by_directive` | helpers_registry_user_directives_getters.json | 646 |
| `get_user_directive_implementations_by_file_path` | helpers_registry_user_directives_getters.json | 695 |
| `get_user_directive_implementations_by_function_name` | helpers_registry_user_directives_getters.json | 671 |
| `get_user_directive_implementations_by_type` | helpers_registry_user_directives_getters.json | 719 |
| `get_user_directive_relationship` | helpers_registry_user_directives_getters.json | 743 |
| `get_user_directive_relationships_by_relationship` | helpers_registry_user_directives_getters.json | 830 |
| `get_user_directive_relationships_by_source` | helpers_registry_user_directives_getters.json | 767 |
| `get_user_directive_relationships_by_target` | helpers_registry_user_directives_getters.json | 799 |
| `get_user_directives` | helpers_registry_user_directives_getters.json | 59 |
| `get_user_directives_by_action_type` | helpers_registry_user_directives_getters.json | 133 |
| `get_user_directives_by_implementation_status` | helpers_registry_user_directives_getters.json | 208 |
| `get_user_directives_by_name` | helpers_registry_user_directives_getters.json | 109 |
| `get_user_directives_by_status` | helpers_registry_user_directives_getters.json | 183 |
| `get_user_directives_by_trigger_type` | helpers_registry_user_directives_getters.json | 158 |
| `get_user_helper_function` | helpers_registry_user_directives_getters.json | 861 |
| `get_user_helper_function_by_name` | helpers_registry_user_directives_getters.json | 910 |
| `get_user_helper_functions` | helpers_registry_user_directives_getters.json | 886 |
| `get_user_helper_functions_by_implementation_status` | helpers_registry_user_directives_getters.json | 982 |
| `get_user_helper_functions_by_name` | helpers_registry_user_directives_getters.json | 934 |
| `get_user_helper_functions_by_path` | helpers_registry_user_directives_getters.json | 958 |
| `get_user_helper_functions_by_purity` | helpers_registry_user_directives_getters.json | 1006 |
| `get_user_logging_config` | helpers_registry_user_directives_getters.json | 1218 |
| `get_user_name_for_branch` | helpers_registry_git.json | 187 |
| `get_user_source_file` | helpers_registry_user_directives_getters.json | 1144 |
| `get_user_source_file_by_path` | helpers_registry_user_directives_getters.json | 1169 |
| `get_user_source_files_by_parse_status` | helpers_registry_user_directives_getters.json | 1194 |
| `get_work_context` | helpers_registry_project_orchestrators.json | 148 |
| `initialize_aifp_project` | helpers_registry_project_core.json | 33 |
| `list_active_branches` | helpers_registry_git.json | 228 |
| `merge_with_fp_intelligence` | helpers_registry_git.json | 163 |
| `project_update_git_status` | helpers_registry_project_core.json | 157 |
| `query_mcp_relationships` | helpers_registry_mcp_orchestrators.json | 114 |
| `query_project_state` | helpers_registry_project_orchestrators.json | 117 |
| `reorder_all_completion_paths` | helpers_registry_project_workflow_setters.json | 336 |
| `reorder_completion_path` | helpers_registry_project_workflow_setters.json | 295 |
| `reorder_completion_paths` | helpers_registry_project_workflow_setters.json | 316 |
| `reserve_file` | helpers_registry_project_structure_setters.json | 100 |
| `reserve_files` | helpers_registry_project_structure_setters.json | 123 |
| `reserve_function` | helpers_registry_project_structure_setters.json | 299 |
| `reserve_functions` | helpers_registry_project_structure_setters.json | 324 |
| `reserve_type` | helpers_registry_project_structure_setters.json | 490 |
| `reserve_types` | helpers_registry_project_structure_setters.json | 515 |
| `search_notes` | helpers_registry_project_workflow_getters.json | 1343 |
| `set_user_directive_activate` | helpers_registry_user_directives_setters.json | 212 |
| `set_user_directive_approved` | helpers_registry_user_directives_setters.json | 143 |
| `set_user_directive_modified` | helpers_registry_user_directives_setters.json | 191 |
| `set_user_directive_validated` | helpers_registry_user_directives_setters.json | 165 |
| `swap_completion_paths_order` | helpers_registry_project_workflow_setters.json | 358 |
| `sync_git_state` | helpers_registry_git.json | 206 |
| `update_ai_interaction` | helpers_registry_user_settings.json | 635 |
| `update_completion_path` | helpers_registry_project_workflow_setters.json | 245 |
| `update_file` | helpers_registry_project_structure_setters.json | 188 |
| `update_file_checksum` | helpers_registry_project_structure_setters.json | 212 |
| `update_file_timestamp` | helpers_registry_project_structure_setters.json | 232 |
| `update_flow` | helpers_registry_project_workflow_setters.json | 128 |
| `update_fp_tracking` | helpers_registry_user_settings.json | 904 |
| `update_function` | helpers_registry_project_structure_setters.json | 390 |
| `update_function_file_location` | helpers_registry_project_structure_setters.json | 440 |
| `update_functions_for_file` | helpers_registry_project_structure_setters.json | 417 |
| `update_infrastructure` | helpers_registry_project_structure_setters.json | 55 |
| `update_interaction` | helpers_registry_project_structure_setters.json | 762 |
| `update_issues_report` | helpers_registry_user_settings.json | 1171 |
| `update_item` | helpers_registry_project_workflow_setters.json | 710 |
| `update_milestone` | helpers_registry_project_workflow_setters.json | 404 |
| `update_note` | helpers_registry_project_workflow_setters.json | 783 |
| `update_project` | helpers_registry_project_core.json | 111 |
| `update_project_state` | helpers_registry_project_orchestrators.json | 60 |
| `update_setting` | helpers_registry_user_settings.json | 137 |
| `update_settings_directive_preference` | helpers_registry_user_settings.json | 441 |
| `update_sidequest` | helpers_registry_project_workflow_setters.json | 633 |
| `update_subtask` | helpers_registry_project_workflow_setters.json | 554 |
| `update_task` | helpers_registry_project_workflow_setters.json | 477 |
| `update_theme` | helpers_registry_project_workflow_setters.json | 56 |
| `update_tracking_setting` | helpers_registry_user_settings.json | 1370 |
| `update_type` | helpers_registry_project_structure_setters.json | 581 |
| `update_type_function_role` | helpers_registry_project_structure_setters.json | 674 |
| `update_user_directive` | helpers_registry_user_directives_setters.json | 77 |
| `update_user_directive_dependency` | helpers_registry_user_directives_setters.json | 349 |
| `update_user_directive_execution` | helpers_registry_user_directives_setters.json | 266 |
| `update_user_directive_helper` | helpers_registry_user_directives_setters.json | 662 |
| `update_user_directive_implementation` | helpers_registry_user_directives_setters.json | 432 |
| `update_user_directive_relationship` | helpers_registry_user_directives_setters.json | 511 |
| `update_user_helper_function` | helpers_registry_user_directives_setters.json | 585 |
| `update_user_logging_config` | helpers_registry_user_directives_setters.json | 824 |
| `update_user_source_file` | helpers_registry_user_directives_setters.json | 738 |
| `validate_initialization` | helpers_registry_project_orchestrators.json | 176 |

---

## Quick Search Tips

**In VS Code / IDE**:
- Ctrl+F / Cmd+F: Search this file for helper name
- Double-click helper name to select, then Ctrl+F to find in registry

**Command line**:
```bash
# Find helper in registries
grep -n "helper_name" docs/helpers/registry/*.json

# Find usage in MD files
grep -r "helper_name" src/aifp/reference/directives/
```

---

## Related Files

- `DIRECTIVES_QUICK_REF.md` - Directive names and locations
- `MD_HELPER_REFS_ANALYSIS.md` - Full analysis of helper refs in MD files
- `docs/helpers/registry/CONSOLIDATION_REPORT.md` - Helper changes (removed, renamed, consolidated)
- `docs/helpers/registry/CURRENT_STATUS.md` - Helper registry status

---

**Note**: If a helper mentioned in an MD file is NOT in this list, it may have been:
- Removed (AI directive-driven, like `parse_directive_file`)
- Consolidated (like `create_project_directory` → `initialize_aifp_project`)
- Renamed (check CONSOLIDATION_REPORT.md)

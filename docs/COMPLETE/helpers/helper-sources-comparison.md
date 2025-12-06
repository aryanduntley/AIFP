# Helper Sources Comparison

**Date**: 2025-11-26

## Summary

| Source | Count | Status |
|--------|-------|--------|
| **info-helpers-*.txt** (SOURCE OF TRUTH) | ~250+ | Comprehensive, takes precedence |
| **helpers_parsed.json** | 49 | Subset, may have some unique helpers |
| **helpers_registry (current)** | 24 | Incomplete - only initial helpers from info-helpers |
| **generic-tools-mcp.md** | 4 | Orchestrator tools |
| **generic-tools-project.md** | 5 | Orchestrator tools |

## Helpers in helpers_parsed.json (49)

```
activate_directive
create_project_blueprint
create_project_directory
create_user_branch
deactivate_directive
detect_and_init_project
detect_conflicts_before_merge
detect_dependencies
detect_external_changes
find_directive_by_intent
generate_implementation_code
get_all_directives
get_current_branch
get_current_commit_hash
get_directive
get_directive_interactions
get_directive_md_content
get_directive_preference
get_git_status
get_project_context
get_project_files
get_project_functions
get_project_status
get_project_tasks
get_status_tree
get_tracking_settings
get_user_directive_status
get_user_name_for_branch
infer_architecture
init_project_db
initialize_project_db
initialize_user_preferences_db
install_dependency
list_active_branches
merge_with_fp_intelligence
monitor_directive_execution
parse_directive_file
query_mcp_db
query_project_db
read_project_blueprint
scan_existing_files
search_directives ← NOT in info-helpers
set_directive_preference
sync_git_state
toggle_tracking_feature
update_directive
update_project_blueprint_section
validate_initialization
validate_user_directive
```

## Helpers Currently in Registry (24)

**Core (7):**
- get_all_directives
- get_directive
- search_directives ← Should we keep this?
- find_directive_by_intent
- query_mcp_db
- get_directive_interactions
- get_directive_md_content

**Project (9):**
- create_project_directory
- initialize_project_db
- initialize_user_preferences_db
- validate_initialization
- init_project_db
- get_project_status
- get_project_context
- get_project_tasks
- get_status_tree

**User Settings (4):**
- get_directive_preference
- set_directive_preference
- get_tracking_settings
- toggle_tracking_feature

**User Directives (4):**
- parse_directive_file
- validate_user_directive
- activate_directive
- deactivate_directive

## Helpers ONLY in info-helpers (not in helpers_parsed) - Sampling

**Project helpers:**
- add_file, add_file_flows, add_flow, add_flow_themes
- add_interaction, add_milestone, add_note
- add_sidequest, add_subtask, add_task, add_theme
- finalize_file, finalize_function, finalize_type
- reserve_file, reserve_function, reserve_type
- get_flow, get_flows, get_flows_by_confidence
- get_task_files, get_task_flows
- get_incomplete_tasks, get_incomplete_subtasks
- update_file, update_function, update_task
- delete_file, delete_function, delete_task
- ... and 150+ more

**Core helpers:**
- get_directive_by_name, get_directives_by_category
- get_helper_by_name, get_helpers_for_directive
- get_categories, get_category_description
- ... and more

**Preferences helpers:**
- get_setting, add_setting, update_setting
- get_tracking_setting_by_name
- ... and more

**User Directives helpers:**
- add_user_directive, get_user_directive_by_name
- add_user_directive_dependency, add_user_directive_helper
- get_user_directive_executions_by_directive
- ... and more

## Action Plan

1. ✅ Keep current 24 helpers in registry
2. ⏳ Add ALL helpers from info-helpers-*.txt files (~200+ more)
3. ⏳ Review helpers_parsed for any unique helpers not in info-helpers
4. ⏳ Add generic tools from generic-tools-*.md files (9 orchestrators)
5. ⏳ Decide on `search_directives` - keep or remove?

## Notes

- **info-helpers-*.txt is FAR more comprehensive** than helpers_parsed.json
- helpers_parsed appears to be an older/incomplete subset
- Need to systematically add all info-helpers helpers to registries
- Need proper return_statements for all ~250+ helpers

# Helper Return_Statements Enhancement Checklist

**Purpose**: Add simple, conceptual hints (0-2 lines) to helper return_statements. Many helpers won't need anything.

**🎯 QUALITY STANDARD:** See [RETURN_STATEMENTS_QUALITY_GUIDE.md](./RETURN_STATEMENTS_QUALITY_GUIDE.md) for complete guidance.

**Status Legend**:
- `[ ]` Not started
- `[~]` In progress
- `[x]` Completed

---

## Progress Overview

**Total Helpers**: 202
**Completed**: 0 helpers (0%)
**In Progress**: 0 helpers
**Not Started**: 202 helpers (100%)

**Note**: All return_statements cleared on 2026-01-01. Starting fresh with simple approach.

---

## Simple Approach Summary

**What return_statements SHOULD be:**
- Simple, conceptual hints (0-2 lines, often 0-1)
- Questions: `"Are there any flows that should be added in flow_themes?"`
- Reminders: `"Verify flows are added in file_flows table"`
- Conventions: `"File names should be suffixed with _id_xx"`
- Conceptual hints: `"After creating milestone, you'll likely need to create tasks for it"`

**What return_statements should NOT be:**
- 15-20 lines of rigid specifications
- Categories (DATABASE CONTEXT:, NEXT STEP:, CHECK:, etc.)
- Fabricated sequences: "seq 1 → seq 2 → seq 3"
- Duplicating directive flow data already in database
- Restating what helper does (that's in purpose field)

**Process for each helper:**
1. Check if helper has used_by_directives
2. If YES → Read directive file and directive flow file
3. Review helper purpose - is there a useful hint?
4. If YES → Write 1-2 simple lines
5. If NO → Leave return_statements empty

**Remember**: Many helpers won't need return_statements. That's okay.

---

## helpers-core.json (33 helpers)

**Focus**: MCP database queries, directive lookups, helper metadata

### Database Schema Helpers (7 helpers)
- [ ] get_core_tables
- [ ] get_core_fields
- [ ] get_core_schema
- [ ] get_from_core
- [ ] get_from_core_where
- [ ] query_core
- [ ] get_directive_by_name

### Directive Queries (7 helpers)
- [ ] get_all_directives
- [ ] get_directive_content
- [ ] search_directives
- [ ] find_directive_by_intent
- [ ] find_directives_by_intent_keyword
- [ ] get_directives_with_intent_keywords
- [ ] add_directive_intent_keyword

### Directive Keywords & Navigation (7 helpers)
- [ ] remove_directive_intent_keyword
- [ ] get_directive_keywords
- [ ] get_all_directive_keywords
- [ ] get_all_intent_keywords_with_counts
- [ ] get_next_directives_from_status
- [ ] get_matching_next_directives
- [ ] get_completion_loop_target

### Directive Navigation & Helpers (7 helpers)
- [ ] get_conditional_work_paths
- [ ] get_helper_by_name
- [ ] get_helpers_by_database
- [ ] get_helpers_are_tool
- [ ] get_helpers_not_tool_not_sub
- [ ] get_helpers_are_sub
- [ ] get_helpers_for_directive

### Helper/Directive Relationships & Categories (5 helpers)
- [ ] get_directives_for_helper
- [ ] get_category_by_name
- [ ] get_categories
- [ ] get_directives_by_category
- [ ] get_directives_by_type

---

## helpers-project-1.json (15 helpers)

**Focus**: Database schema queries, generic CRUD operations, project metadata management

**Range**: Helpers 1-15 of 112

### Database Schema & CRUD (10 helpers)
- [ ] get_project_tables
- [ ] get_project_fields
- [ ] get_project_schema
- [ ] get_project_json_parameters
- [ ] get_from_project
- [ ] get_from_project_where
- [ ] query_project
- [ ] add_project_entry
- [ ] update_project_entry
- [ ] delete_project_entry

### Project Metadata (5 helpers)
- [ ] create_project
- [ ] get_project
- [ ] update_project
- [ ] blueprint_has_changed
- [ ] get_infrastructure_by_type

---

## helpers-project-2.json (10 helpers)

**Focus**: File reservation, finalization, and management operations

**Range**: Helpers 16-25 of 112

- [ ] reserve_file
- [ ] reserve_files
- [ ] finalize_file
- [ ] finalize_files
- [ ] get_file_by_name
- [ ] get_file_by_path
- [ ] update_file
- [ ] file_has_changed
- [ ] update_file_timestamp
- [ ] delete_file

---

## helpers-project-3.json (10 helpers)

**Focus**: Function reservation, finalization, and management operations

**Range**: Helpers 26-35 of 112

- [ ] reserve_function
- [ ] reserve_functions
- [ ] finalize_function
- [ ] finalize_functions
- [ ] get_function_by_name
- [ ] get_functions_by_file
- [ ] update_function
- [ ] update_functions_for_file
- [ ] update_function_file_location
- [ ] delete_function

---

## helpers-project-4.json (13 helpers)

**Focus**: Type reservation/finalization, type-function relationships, and interaction management

**Range**: Helpers 36-48 of 112

- [ ] reserve_type
- [ ] reserve_types
- [ ] finalize_type
- [ ] finalize_types
- [ ] update_type
- [ ] delete_type
- [ ] add_types_functions
- [ ] update_type_function_role
- [ ] delete_type_function
- [ ] add_interaction
- [ ] add_interactions
- [ ] update_interaction
- [ ] delete_interaction

---

## helpers-project-5.json (11 helpers)

**Focus**: Theme and flow management operations (add, get, update, delete, relationships)

**Range**: Helpers 49-59 of 112

- [ ] get_theme_by_name
- [ ] get_flow_by_name
- [ ] get_all_themes
- [ ] get_all_flows
- [ ] add_theme
- [ ] add_flow
- [ ] update_theme
- [ ] delete_theme
- [ ] update_flow
- [ ] delete_flow
- [ ] get_file_ids_from_flows

---

## helpers-project-6.json (14 helpers)

**Focus**: Flow-theme relationships, file-flow relationships, and completion path management

**Range**: Helpers 60-73 of 112

- [ ] get_flows_for_theme
- [ ] get_themes_for_flow
- [ ] get_files_by_flow
- [ ] get_flows_for_file
- [ ] add_completion_path
- [ ] get_all_completion_paths
- [ ] get_completion_paths_by_status
- [ ] get_incomplete_completion_paths
- [ ] get_next_completion_path
- [ ] update_completion_path
- [ ] delete_completion_path
- [ ] reorder_completion_path
- [ ] reorder_all_completion_paths
- [ ] swap_completion_paths_order

---

## helpers-project-7.json (15 helpers)

**Focus**: Milestone and task management operations (add, get, update, delete, queries)

**Range**: Helpers 74-88 of 112

- [ ] add_milestone
- [ ] get_milestones_by_path
- [ ] get_milestones_by_status
- [ ] get_incomplete_milestones
- [ ] update_milestone
- [ ] delete_milestone
- [ ] add_task
- [ ] get_incomplete_tasks_by_milestone
- [ ] get_incomplete_tasks
- [ ] get_tasks_by_milestone
- [ ] get_tasks_comprehensive
- [ ] get_task_flows
- [ ] get_task_files
- [ ] update_task
- [ ] delete_task

---

## helpers-project-8.json (14 helpers)

**Focus**: Subtask and sidequest management operations (add, get, update, delete, queries)

**Range**: Helpers 89-102 of 112

- [ ] add_subtask
- [ ] get_incomplete_subtasks
- [ ] get_incomplete_subtasks_by_task
- [ ] get_subtasks_by_task
- [ ] get_subtasks_comprehensive
- [ ] update_subtask
- [ ] delete_subtask
- [ ] add_sidequest
- [ ] get_incomplete_sidequests
- [ ] get_sidequests_comprehensive
- [ ] get_sidequest_flows
- [ ] get_sidequest_files
- [ ] update_sidequest
- [ ] delete_sidequest

---

## helpers-project-9.json (10 helpers)

**Focus**: Item and note management operations (add, get, update, delete, search)

**Range**: Helpers 103-112 of 112

- [ ] get_items_for_task
- [ ] get_items_for_subtask
- [ ] get_items_for_sidequest
- [ ] get_incomplete_items
- [ ] delete_item
- [ ] add_note
- [ ] get_notes_comprehensive
- [ ] search_notes
- [ ] update_note
- [ ] delete_note

---

## helpers-settings.json (17 helpers)

**Focus**: User preferences, directive preferences, tracking toggles

### Database Schema & CRUD (7 helpers)
- [ ] get_settings_tables
- [ ] get_settings_fields
- [ ] get_settings_schema
- [ ] get_settings_json_parameters
- [ ] get_from_settings
- [ ] get_from_settings_where
- [ ] query_settings

### Settings CRUD & Preferences (7 helpers)
- [ ] add_settings_entry
- [ ] update_settings_entry
- [ ] delete_settings_entry
- [ ] load_directive_preferences
- [ ] add_directive_preference
- [ ] get_user_setting
- [ ] update_user_preferences

### Preferences Application & Tracking (3 helpers)
- [ ] apply_preferences_to_context
- [ ] get_tracking_settings
- [ ] toggle_tracking_feature

---

## helpers-git.json (11 helpers)

**Focus**: Git integration, external change detection, FP-powered merging

### Git Status & Detection (6 helpers)
- [ ] get_current_commit_hash
- [ ] get_current_branch
- [ ] get_git_status
- [ ] detect_external_changes
- [ ] create_user_branch
- [ ] get_user_name_for_branch

### Git Operations & Sync (5 helpers)
- [ ] list_active_branches
- [ ] detect_conflicts_before_merge
- [ ] merge_with_fp_intelligence
- [ ] sync_git_state
- [ ] project_update_git_status

---

## helpers-orchestrators.json (12 helpers)

**Focus**: High-level orchestrators, status, state management

### Entry Points & Status (6 helpers)
- [ ] aifp_run
- [ ] aifp_status
- [ ] get_project_status
- [ ] get_status_tree
- [ ] get_project_context
- [ ] get_work_context

### Query & Update Tools (6 helpers)
- [ ] get_current_progress
- [ ] update_project_state
- [ ] batch_update_progress
- [ ] query_project_state
- [ ] validate_initialization
- [ ] get_files_by_flow_context

---

## helpers-user-custom.json (16 helpers)

**Focus**: User directive automation (Use Case 2)

### Database Schema & CRUD (7 helpers)
- [ ] get_user_custom_tables
- [ ] get_user_custom_fields
- [ ] get_user_custom_schema
- [ ] get_user_custom_json_parameters
- [ ] get_from_user_custom
- [ ] get_from_user_custom_where
- [ ] query_user_custom

### User Custom CRUD & Directive Operations (6 helpers)
- [ ] add_user_custom_entry
- [ ] update_user_custom_entry
- [ ] delete_user_custom_entry
- [ ] parse_directive_file
- [ ] validate_directive_config
- [ ] generate_handler_code

### Directive Lifecycle (3 helpers)
- [ ] deploy_background_service
- [ ] get_user_directive_status
- [ ] monitor_directive_execution

---

## helpers-index.json (1 helper)

**Focus**: Global database metadata

- [ ] get_databases

---

## Enhancement Process

### For Each Helper File:

1. **Open helper JSON file**
2. **For each helper:**
   - Check if `used_by_directives` is populated
   - If YES:
     - Read directive file: `docs/directives-json/directives-*.json`
     - Read directive flow: `docs/directives-json/directive_flow_*.json`
     - Understand helper's role in workflow
   - Review helper purpose and parameters
   - Decide if return_statement is useful (often NO)
   - If YES: Write 1-2 simple lines
   - If NO: Leave empty array
3. **Mark helper as complete in checklist**

### Quality Check Before Moving On:

- [ ] Read quality guide before starting each file
- [ ] For every helper with used_by_directives, actually read the directive and flow files
- [ ] Keep return_statements to 0-2 lines (often 0-1)
- [ ] No categories (no DATABASE CONTEXT:, NEXT STEP:, etc.)
- [ ] Questions or reminders format
- [ ] Only add if actually useful

---

## Session Notes

### Session 1: 2026-01-01 (Reset and Restart)
- **Issue Identified**: Previous approach was completely wrong
  - Made 15-20 line rigid specifications
  - Added fabricated sequences
  - Over-categorized everything
  - Didn't read actual directives/flows
- **Action Taken**:
  - Cleared all 202 return_statements across 15 files
  - Rewrote quality guide to reflect original simple vision
  - Updated checklist to mark all incomplete
- **New Approach**:
  - Simple hints (0-2 lines, often 0-1)
  - No categories
  - Questions and reminders format
  - Many helpers won't need anything
  - Actually read directives and flows before writing
- **Next Step**: Start fresh with helpers-project-2.json or another file

---

## References

- **Original Vision**: `docs/helpers/info-helpers-project.txt` (lines 72-553)
- **Quality Guide**: `docs/helpers/RETURN_STATEMENTS_QUALITY_GUIDE.md`
- **Directive Files**: `docs/directives-json/directives-*.json`
- **Directive Flows**: `docs/directives-json/directive_flow_*.json`
- **Helper JSON Files**: `docs/helpers/json/helpers-*.json`

---

**Last Updated:** 2026-01-01 (Complete reset - starting fresh with simple approach)

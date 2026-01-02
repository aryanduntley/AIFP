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
**Completed**: 168 helpers (83%) - core, project-1 through project-9, git, orchestrators
**Enhanced**: 26 helpers with return_statements
**Not Enhanced**: 142 helpers (no return_statements needed)
**Not Reviewed**: 34 helpers (17%) - settings, user-custom, index (not relevant for return_statements)

**Note**: Completed on 2026-01-02. Simple approach applied - most helpers don't need return_statements.

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

## helpers-core.json (33 helpers) ✅ COMPLETE

**Focus**: MCP database queries, directive lookups, helper metadata
**Result**: 0 of 33 enhanced - all are straightforward query/lookup operations

### Database Schema Helpers (7 helpers)
- [x] get_core_tables
- [x] get_core_fields
- [x] get_core_schema
- [x] get_from_core
- [x] get_from_core_where
- [x] query_core
- [x] get_directive_by_name

### Directive Queries (7 helpers)
- [x] get_all_directives
- [x] get_directive_content
- [x] search_directives
- [x] find_directive_by_intent
- [x] find_directives_by_intent_keyword
- [x] get_directives_with_intent_keywords
- [x] add_directive_intent_keyword

### Directive Keywords & Navigation (7 helpers)
- [x] remove_directive_intent_keyword
- [x] get_directive_keywords
- [x] get_all_directive_keywords
- [x] get_all_intent_keywords_with_counts
- [x] get_next_directives_from_status
- [x] get_matching_next_directives
- [x] get_completion_loop_target

### Directive Navigation & Helpers (7 helpers)
- [x] get_conditional_work_paths
- [x] get_helper_by_name
- [x] get_helpers_by_database
- [x] get_helpers_are_tool
- [x] get_helpers_not_tool_not_sub
- [x] get_helpers_are_sub
- [x] get_helpers_for_directive

### Helper/Directive Relationships & Categories (5 helpers)
- [x] get_directives_for_helper
- [x] get_category_by_name
- [x] get_categories
- [x] get_directives_by_category
- [x] get_directives_by_type

---

## helpers-project-1.json (15 helpers) ✅ COMPLETE

**Focus**: Database schema queries, generic CRUD operations, project metadata management
**Range**: Helpers 1-15 of 112
**Result**: 0 of 15 enhanced - all are generic CRUD and metadata operations

### Database Schema & CRUD (10 helpers)
- [x] get_project_tables
- [x] get_project_fields
- [x] get_project_schema
- [x] get_project_json_parameters
- [x] get_from_project
- [x] get_from_project_where
- [x] query_project
- [x] add_project_entry
- [x] update_project_entry
- [x] delete_project_entry

### Project Metadata (5 helpers)
- [x] create_project
- [x] get_project
- [x] update_project
- [x] blueprint_has_changed
- [x] get_infrastructure_by_type

---

## helpers-project-2.json (10 helpers) ✅ COMPLETE

**Focus**: File reservation, finalization, and management operations
**Range**: Helpers 16-25 of 112
**Result**: 6 of 10 enhanced - reserve/finalize pattern + naming conventions + delete reminder

- [x] reserve_file ✨
- [x] reserve_files ✨
- [x] finalize_file ✨
- [x] finalize_files ✨
- [x] get_file_by_name
- [x] get_file_by_path
- [x] update_file ✨
- [x] file_has_changed
- [x] update_file_timestamp
- [x] delete_file ✨

---

## helpers-project-3.json (10 helpers) ✅ COMPLETE

**Focus**: Function reservation, finalization, and management operations
**Range**: Helpers 26-35 of 112
**Result**: 8 of 10 enhanced - reserve/finalize pattern + naming conventions + delete reminder

- [x] reserve_function ✨
- [x] reserve_functions ✨
- [x] finalize_function ✨
- [x] finalize_functions ✨
- [x] get_function_by_name
- [x] get_functions_by_file
- [x] update_function ✨
- [x] update_functions_for_file ✨
- [x] update_function_file_location ✨
- [x] delete_function ✨

---

## helpers-project-4.json (13 helpers) ✅ COMPLETE

**Focus**: Type reservation/finalization, type-function relationships, and interaction management
**Range**: Helpers 36-48 of 112
**Result**: 8 of 13 enhanced - reserve/finalize pattern + naming conventions + code sync reminders

- [x] reserve_type ✨
- [x] reserve_types ✨
- [x] finalize_type ✨
- [x] finalize_types ✨
- [x] update_type ✨
- [x] delete_type ✨
- [x] add_types_functions
- [x] update_type_function_role
- [x] delete_type_function
- [x] add_interaction
- [x] add_interactions
- [x] update_interaction ✨
- [x] delete_interaction ✨

---

## helpers-project-5.json (11 helpers) ✅ COMPLETE

**Focus**: Theme and flow management operations (add, get, update, delete, relationships)
**Range**: Helpers 49-59 of 112
**Result**: 1 of 11 enhanced - add_flow reminder about file_flows + delete_flow implementation notes

- [x] get_theme_by_name
- [x] get_flow_by_name
- [x] get_all_themes
- [x] get_all_flows
- [x] add_theme
- [x] add_flow ✨
- [x] update_theme
- [x] delete_theme
- [x] update_flow
- [x] delete_flow (implementation notes enhanced)
- [x] get_file_ids_from_flows

---

## helpers-project-6.json (14 helpers) ✅ COMPLETE

**Focus**: Flow-theme relationships, file-flow relationships, and completion path management
**Range**: Helpers 60-73 of 112
**Result**: 0 of 14 enhanced - all are straightforward relationship queries and metadata operations

- [x] get_flows_for_theme
- [x] get_themes_for_flow
- [x] get_files_by_flow
- [x] get_flows_for_file
- [x] add_completion_path
- [x] get_all_completion_paths
- [x] get_completion_paths_by_status
- [x] get_incomplete_completion_paths
- [x] get_next_completion_path
- [x] update_completion_path
- [x] delete_completion_path
- [x] reorder_completion_path
- [x] reorder_all_completion_paths
- [x] swap_completion_paths_order

---

## helpers-project-7.json (15 helpers) ✅ COMPLETE

**Focus**: Milestone and task management operations (add, get, update, delete, queries)
**Range**: Helpers 74-88 of 112
**Result**: 1 of 15 enhanced - add_task reminder about items + implementation notes fixed

- [x] add_milestone
- [x] get_milestones_by_path
- [x] get_milestones_by_status
- [x] get_incomplete_milestones
- [x] update_milestone
- [x] delete_milestone
- [x] add_task ✨
- [x] get_incomplete_tasks_by_milestone (implementation notes fixed)
- [x] get_incomplete_tasks (implementation notes fixed)
- [x] get_tasks_by_milestone (implementation notes fixed)
- [x] get_tasks_comprehensive (implementation notes fixed)
- [x] get_task_flows (implementation notes fixed)
- [x] get_task_files (implementation notes fixed)
- [x] update_task (implementation notes fixed)
- [x] delete_task (implementation notes fixed)

---

## helpers-project-8.json (14 helpers) ✅ COMPLETE

**Focus**: Subtask and sidequest management operations (add, get, update, delete, queries)
**Range**: Helpers 89-102 of 112
**Result**: 2 of 14 enhanced - add_subtask and add_sidequest reminders about items

- [x] add_subtask ✨
- [x] get_incomplete_subtasks
- [x] get_incomplete_subtasks_by_task
- [x] get_subtasks_by_task
- [x] get_subtasks_comprehensive
- [x] update_subtask
- [x] delete_subtask
- [x] add_sidequest ✨
- [x] get_incomplete_sidequests
- [x] get_sidequests_comprehensive
- [x] get_sidequest_flows
- [x] get_sidequest_files
- [x] update_sidequest
- [x] delete_sidequest

---

## helpers-project-9.json (10 helpers) ✅ COMPLETE

**Focus**: Item and note management operations (add, get, update, delete, search)
**Range**: Helpers 103-112 of 112
**Result**: 0 of 10 enhanced - all are straightforward CRUD operations for items and notes

- [x] get_items_for_task
- [x] get_items_for_subtask
- [x] get_items_for_sidequest
- [x] get_incomplete_items
- [x] delete_item
- [x] add_note
- [x] get_notes_comprehensive
- [x] search_notes
- [x] update_note
- [x] delete_note

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

## helpers-git.json (11 helpers) ✅ COMPLETE

**Focus**: Git integration, external change detection, FP-powered merging
**Result**: 0 of 11 enhanced - Git takes care of itself naturally through directives

### Git Status & Detection (6 helpers)
- [x] get_current_commit_hash
- [x] get_current_branch
- [x] get_git_status
- [x] detect_external_changes
- [x] create_user_branch
- [x] get_user_name_for_branch

### Git Operations & Sync (5 helpers)
- [x] list_active_branches
- [x] detect_conflicts_before_merge
- [x] merge_with_fp_intelligence
- [x] sync_git_state
- [x] project_update_git_status

---

## helpers-orchestrators.json (12 helpers) ✅ COMPLETE

**Focus**: High-level orchestrators, status, state management
**Result**: 0 of 12 enhanced - all are data-gathering/analysis operations or convenience tools

### Entry Points & Status (6 helpers)
- [x] aifp_run
- [x] aifp_status
- [x] get_project_status
- [x] get_status_tree
- [x] get_project_context
- [x] get_work_context

### Query & Update Tools (6 helpers)
- [x] get_current_progress
- [x] update_project_state
- [x] batch_update_progress
- [x] query_project_state
- [x] validate_initialization
- [x] get_files_by_flow_context

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

### Session 2: 2026-01-02 (Completion) ✅
- **Files Completed**:
  - helpers-core.json (0/33 enhanced)
  - helpers-project-1.json (0/15 enhanced)
  - helpers-project-2.json (6/10 enhanced)
  - helpers-project-3.json (8/10 enhanced)
  - helpers-project-4.json (8/13 enhanced)
  - helpers-project-5.json (1/11 enhanced)
  - helpers-project-6.json (0/14 enhanced)
  - helpers-project-7.json (1/15 enhanced)
  - helpers-project-8.json (2/14 enhanced)
  - helpers-project-9.json (0/10 enhanced)
  - helpers-git.json (0/11 enhanced)
  - helpers-orchestrators.json (0/12 enhanced)
- **Key Findings**:
  - Most helpers don't need return_statements (142 of 168 reviewed)
  - Only 26 helpers needed enhancement (15%)
  - Primary enhancements: reserve/finalize naming conventions, code-database sync reminders, delete validation
  - Fixed implementation_notes in project-7 (removed "See return_statements" references)
  - Enhanced delete_flow implementation notes with task/sidequest validation logic
- **Not Reviewed**: settings (17), user-custom (16), index (1) - deemed not relevant for return_statements
- **Cleanup**: Deleted obsolete mapping_suggestions.json file

---

## References

- **Original Vision**: `docs/helpers/info-helpers-project.txt` (lines 72-553)
- **Quality Guide**: `docs/helpers/RETURN_STATEMENTS_QUALITY_GUIDE.md`
- **Directive Files**: `docs/directives-json/directives-*.json`
- **Directive Flows**: `docs/directives-json/directive_flow_*.json`
- **Helper JSON Files**: `docs/helpers/json/helpers-*.json`

---

**Last Updated:** 2026-01-02 ✅ COMPLETE (168 of 202 helpers reviewed, 26 enhanced)

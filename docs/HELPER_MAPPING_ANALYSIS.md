# Helper Mapping Analysis

**Date**: 2025-12-19
**Purpose**: Systematic analysis of helper function usage by directives
**Status**: Analysis for Phase 8 implementation

---

## Current Status

**Mapped**: 7/202 helpers (3.5%)
**Unmapped**: 195 helpers

**Mapped Helpers** (completed in Phases 4 & 7):
1. **search_directives** (core) - FP reference consultation, aifp_help
2. **get_directive_content** (core) - FP reference consultation
3. **find_directive_by_intent** (core) - user_preferences_update
4. **query_settings** (settings) - user_preferences_sync, tracking_toggle
5. **update_settings_entry** (settings) - user_preferences_update, tracking_toggle
6. **add_note** (project-3) - project_notes_log
7. **aifp_run** (orchestrators) - entry point (self-referential)

---

## Directive Categories & Helper Usage Patterns

### 1. Orchestrator Directives (aifp_run, aifp_status, aifp_help)

#### aifp_status
**Workflow**: determine_project_state → comprehensive status analysis

**Likely Helpers**:
- `query_core()` - Query aifp_core.db for directive metadata
- `get_project_metadata()` - Get project name, purpose, status
- `get_current_milestone()` - Current milestone info
- `get_completion_path_status()` - Completion path stages
- `get_priority_work_queue()` - Sidequests, subtasks, tasks ordered by priority
- `get_current_work_item()` - Current task/subtask/sidequest
- `get_historical_context()` - Last N completed items
- `get_ambiguities()` - Unclear decisions/roadblocks
- `get_next_directives_from_status()` - Next-step suggestions
- `get_user_directives_status()` - Check if Use Case 2 (automation)
- Git helpers for external change detection

#### aifp_help
**Workflow**: search_directives → display help

**Already Mapped**: search_directives ✓

**Additional Helpers**:
- `get_directive_by_name()` - Get specific directive details
- `list_directives_by_category()` - List by category
- `format_directive_documentation()` - Format for display

---

### 2. Project Initialization (project_init, project_blueprint_read/update)

#### project_init
**Workflow**: check_existing_state → create_structure → initialize_db

**Likely Helpers**:
- `create_aifp_directory()` - Create .aifp-project/
- `initialize_project_db()` - Create project.db with schema
- `initialize_user_preferences_db()` - Create user_preferences.db
- `create_backup()` - Backup to .git/.aifp/
- `parse_user_directive_files()` - Detect Use Case 2
- `set_project_metadata()` - Initial project info
- `create_completion_path()` - Initialize completion_path stages

#### project_blueprint_read
**Workflow**: read_file → parse_structure

**Likely Helpers**:
- `read_blueprint_file()` - Read ProjectBlueprint.md
- `parse_blueprint_sections()` - Extract structure
- `extract_goals()` - Parse project goals
- `extract_milestones_from_blueprint()` - Parse milestone info

#### project_blueprint_update
**Workflow**: validate_changes → update_file → sync_db

**Likely Helpers**:
- `update_blueprint_file()` - Write changes to ProjectBlueprint.md
- `sync_blueprint_to_db()` - Update database with blueprint changes
- `validate_blueprint_structure()` - Ensure valid format

---

### 3. Task Management (create, update, complete, decomposition)

#### project_task_decomposition
**Workflow**: read_blueprint → create_completion_path → create_milestones → create_tasks → create_items

**Likely Helpers**:
- `read_blueprint_file()`
- `parse_blueprint_themes()`
- `create_completion_path_stages()` - Create stages in completion_path table
- `create_milestone()` - Insert milestone
- `create_task()` - Insert task
- `create_task_item()` - Insert task item (auto-create)
- `link_task_to_milestone()` - Establish relationships

#### project_task_create
**Workflow**: validate_task → insert_task → create_items

**Likely Helpers**:
- `create_task()` - Insert into tasks table
- `create_task_item()` - Auto-create items for task
- `assign_task_priority()` - Set priority
- `link_task_to_milestone()`

#### project_task_update
**Workflow**: load_task → update_fields → save

**Likely Helpers**:
- `get_task_by_id()` - Load task details
- `update_task()` - Update task fields
- `get_task_progress()` - Calculate progress %

#### project_task_complete
**Workflow**: mark_complete → check_milestone → loop_back

**Likely Helpers**:
- `mark_task_complete()` - Set status = 'completed'
- `auto_complete_task_items()` - Mark all items complete
- `check_milestone_completion()` - Query if all tasks in milestone done
- `get_milestone_id_for_task()` - Get parent milestone

#### project_subtask_create / project_sidequest_create
**Similar pattern to task_create**

**Likely Helpers**:
- `create_subtask()` / `create_sidequest()`
- `create_subtask_item()` / `create_sidequest_item()`
- `link_subtask_to_task()` / `link_sidequest_to_item()`

#### project_item_create
**Workflow**: validate_item → insert_item

**Likely Helpers**:
- `create_task_item()` - Insert item
- `get_task_by_id()` - Validate parent task exists

#### project_milestone_complete
**Workflow**: mark_complete → check_completion_path → identify_next

**Likely Helpers**:
- `mark_milestone_complete()`
- `check_completion_path_stage_status()`
- `get_next_milestone()`

---

### 4. File Management (write, read, delete, add_path, reserve_finalize)

#### project_file_write
**Workflow**: check_preferences → reserve_ids → write_file → parse_code → update_db → git_sync

**Likely Helpers**:
- `reserve_file_id()` - Reserve file entry
- `reserve_function_ids()` - Reserve function entries
- `write_file_to_disk()` - Physical file write
- `parse_file_functions()` - Extract functions from code
- `parse_file_imports()` - Extract imports
- `insert_file()` - Insert into files table
- `insert_function()` - Insert into functions table
- `insert_interaction()` - Insert into function_interactions table
- `update_function_metadata()` - Set purity, side effects, etc.
- Git sync helpers

#### project_file_read
**Workflow**: load_file → load_context

**Likely Helpers**:
- `get_file_by_path()` - Get file from database
- `get_file_functions()` - Get functions in file
- `get_file_interactions()` - Get function call graph
- `read_file_content()` - Read actual file

#### project_file_delete
**Workflow**: load_file → delete_references → delete_file

**Likely Helpers**:
- `get_file_by_path()`
- `delete_function_interactions()` - Cleanup interactions
- `delete_functions()` - Delete function entries
- `delete_file()` - Delete file entry
- `delete_file_from_disk()` - Physical file deletion

#### project_add_path
**Workflow**: validate_path → parse_file → add_to_db

**Likely Helpers**:
- `validate_file_exists()`
- `parse_file_functions()`
- `insert_file()`
- `insert_function()`

#### project_reserve_finalize
**Workflow**: reserve_ids → return_ids

**Likely Helpers**:
- `reserve_file_id()`
- `reserve_function_ids()`
- `reserve_interaction_ids()`

---

### 5. Database & State Management

#### project_update_db
**Workflow**: sync_all_tables

**Likely Helpers**:
- `sync_files_table()`
- `sync_functions_table()`
- `sync_interactions_table()`
- `sync_tasks_table()`
- `validate_foreign_keys()`

#### project_evolution
**Workflow**: track_changes → log_evolution

**Likely Helpers**:
- `log_project_evolution()` - Insert evolution log entry
- `get_project_history()` - Query evolution log

---

### 6. Completion & Validation

#### project_completion_check
**Workflow**: check_completion_path → check_milestones → check_tasks → check_drift

**Likely Helpers**:
- `get_completion_path_status()`
- `get_all_milestones()`
- `get_incomplete_tasks()`
- `check_goal_alignment()` - Verify goals vs. actual
- `generate_completion_report()`

#### project_compliance_check
**Workflow**: load_preferences → run_fp_checks → report_violations

**Likely Helpers**:
- Query settings/preferences (already mapped)
- `check_function_purity()` - Validate purity
- `detect_side_effects()` - Scan for side effects
- `check_immutability()` - Verify no mutations
- `check_oop_violations()` - Detect classes/inheritance
- `generate_compliance_report()`
- `auto_fix_violations()` - If user preference enabled

---

### 7. Git Integration

**All git directives** (init, detect_external_changes, create_branch, detect_conflicts, merge_branch, sync_state)

**Likely Helpers** (all in helpers-git.json, 11 total):
- `git_init_repo()` - Initialize git integration
- `get_last_known_git_hash()` - Query project.last_known_git_hash
- `get_current_git_head()` - Get current HEAD hash
- `compare_git_hashes()` - Detect external changes
- `get_git_diff()` - Get diff between commits
- `update_last_known_git_hash()` - Update project table
- `create_git_branch()` - Create branch with naming pattern
- `get_git_branches()` - List branches
- `detect_merge_conflicts()` - FP-powered conflict analysis
- `merge_git_branch()` - Perform merge
- `log_merge_history()` - Insert into merge_history table

---

### 8. User Directive System (Use Case 2)

**All user_directive_* directives** (parse, validate, implement, approve, activate, monitor, update, deactivate, status)

**Likely Helpers** (all in helpers-user-custom.json, 16 total):
- `parse_directive_file()` - Parse YAML/JSON/TXT
- `extract_triggers()` - Extract trigger definitions
- `extract_actions()` - Extract action definitions
- `validate_directive_structure()` - Validate format
- `create_user_directives_db()` - Initialize user_directives.db
- `insert_directive()` - Insert into directives table
- `insert_trigger()` - Insert into triggers table
- `insert_action()` - Insert into actions table
- `validate_trigger_type()` - Check valid trigger
- `validate_action_target()` - Check valid action
- `check_directive_conflicts()` - Detect overlaps
- `update_directive_status()` - Set status (active/disabled/etc.)
- `get_directive_execution_logs()` - Query execution_logs table
- `monitor_directive_errors()` - Track failures
- `generate_directive_code()` - Generate implementation (AI calls project_file_write)

---

### 9. Analysis & Metrics

#### project_metrics
**Workflow**: calculate_metrics → format_report

**Likely Helpers**:
- `calculate_completion_percentage()` - Overall project %
- `get_task_distribution()` - Tasks per milestone
- `get_milestone_progress()` - Per-milestone status
- `calculate_velocity()` - Tasks completed per day

#### project_dependency_map
**Workflow**: analyze_dependencies → generate_graph

**Likely Helpers**:
- `get_all_functions()`
- `get_function_interactions()` - Function call graph
- `build_dependency_graph()`
- `detect_circular_dependencies()`
- `format_dependency_visualization()`

#### project_performance_summary
**Workflow**: query_execution_logs → calculate_stats

**Likely Helpers**:
- `get_directive_execution_logs()` - Query notes table with directive_name
- `calculate_success_rate()` - Successes / total
- `calculate_retry_rate()` - Retries / total
- `identify_failure_patterns()` - Common failure reasons

#### project_theme_flow_mapping
**Workflow**: analyze_blueprint → map_flows

**Likely Helpers**:
- `parse_blueprint_themes()`
- `extract_flows_from_blueprint()`
- `map_tasks_to_flows()`
- `map_files_to_themes()`

---

### 10. Maintenance & Utilities

#### project_dependency_sync
**Workflow**: detect_dependencies → update_requirements

**Likely Helpers**:
- `scan_imports()` - Scan all files for imports
- `detect_missing_packages()` - Compare with requirements.txt
- `update_requirements_file()` - Add missing packages
- `validate_versions()` - Check version compatibility

#### project_integrity_check
**Workflow**: validate_database → check_consistency

**Likely Helpers**:
- `validate_foreign_keys()`
- `check_orphaned_records()` - Records with invalid FKs
- `check_table_consistency()` - Verify table state
- `repair_database()` - Fix issues if possible

#### project_auto_resume
**Workflow**: detect_incomplete_work → suggest_resume

**Likely Helpers**:
- `get_current_work_item()` - Get active task/subtask/sidequest
- `get_last_modified_file()` - Detect recent work
- `suggest_next_steps()` - Based on context

#### project_auto_summary
**Workflow**: analyze_recent_activity → generate_summary

**Likely Helpers**:
- `get_recent_commits()` - Git history
- `get_recently_completed_tasks()` - Task history
- `get_recent_notes()` - Note history
- `generate_activity_summary()` - Format report

#### project_archive
**Workflow**: validate_completion → create_archive

**Likely Helpers**:
- `create_archive_directory()`
- `backup_project_db()`
- `backup_user_preferences_db()`
- `backup_files()`
- `mark_project_archived()`

#### project_backup_restore
**Workflow**: backup_or_restore → sync_state

**Likely Helpers**:
- `create_backup_from_project()`
- `restore_backup_to_project()`
- `validate_backup_integrity()`
- `list_available_backups()`

#### project_refactor_path
**Workflow**: detect_path_changes → update_references

**Likely Helpers**:
- `get_all_file_paths()`
- `update_file_path()` - Update files table
- `update_import_references()` - Fix imports in code
- `update_function_references()` - Fix function paths

---

## Helpers by Database Target

### helpers-core.json (33 total, 3 mapped)
**Target**: aifp_core.db (directives, helpers, flows)
- ✅ search_directives
- ✅ get_directive_content
- ✅ find_directive_by_intent
- query_core - Basic database queries
- get_directive_by_name
- list_directives_by_category
- get_directives_with_intent_keywords
- find_directives_by_intent_keyword
- get_all_directives
- get_next_directives_from_status
- get_conditional_work_paths
- get_completion_loop_target
- ... (20 more unmapped)

### helpers-orchestrators.json (12 total, 1 mapped)
**Target**: Orchestrator logic (cross-database)
- ✅ aifp_run (self-referential)
- aifp_status - **CRITICAL - Main status helper**
- get_project_metadata
- get_current_milestone
- get_completion_path_status
- get_priority_work_queue
- get_current_work_item
- get_historical_context
- get_ambiguities
- get_user_directives_status
- ... (2 more unmapped)

### helpers-project-1.json (37 total, 0 mapped)
**Target**: project.db (tasks, milestones, completion_path)
- **Task management** (~15 helpers)
- **Milestone management** (~8 helpers)
- **Completion path** (~5 helpers)
- **Project metadata** (~9 helpers)

### helpers-project-2.json (40 total, 0 mapped)
**Target**: project.db (files, functions, interactions)
- **File management** (~15 helpers)
- **Function management** (~12 helpers)
- **Interaction tracking** (~8 helpers)
- **Code parsing** (~5 helpers)

### helpers-project-3.json (35 total, 1 mapped)
**Target**: project.db (notes, evolution, analysis)
- ✅ add_note
- **Notes management** (~5 helpers)
- **Evolution tracking** (~5 helpers)
- **Metrics & analysis** (~10 helpers)
- **Backup/restore** (~7 helpers)
- **Utilities** (~7 helpers)

### helpers-git.json (11 total, 0 mapped)
**Target**: Git operations + project.db (git state)
- All 11 helpers used by git directives
- Need mapping for: git_init, git_detect_external_changes, git_create_branch, git_detect_conflicts, git_merge_branch, git_sync_state

### helpers-settings.json (17 total, 2 mapped)
**Target**: user_preferences.db (settings, preferences, tracking)
- ✅ query_settings
- ✅ update_settings_entry
- **Settings management** (~6 unmapped)
- **Preference management** (~4 unmapped)
- **Tracking management** (~5 unmapped)

### helpers-user-custom.json (16 total, 0 mapped)
**Target**: user_directives.db (directives, triggers, actions, logs)
- All 16 helpers used by user_directive_* directives (Use Case 2)
- Need mapping for: parse, validate, implement, approve, activate, monitor, update, deactivate, status

---

## Recommended Mapping Order (Phase 8)

### Priority 1: Critical Orchestrators (2 helpers)
1. **aifp_status** - Most important helper, used by every workflow

### Priority 2: Task Management (10-15 helpers)
Core project management operations:
- create_task, update_task, mark_task_complete
- create_milestone, mark_milestone_complete
- create_task_item (auto-create)
- get_task_by_id, get_milestone_id_for_task
- check_milestone_completion

### Priority 3: File Management (10-15 helpers)
File operations:
- insert_file, insert_function, insert_interaction
- reserve_file_id, reserve_function_ids
- parse_file_functions
- write_file_to_disk
- get_file_by_path, delete_file

### Priority 4: Git Integration (11 helpers)
All git operations:
- get_last_known_git_hash, update_last_known_git_hash
- get_current_git_head, compare_git_hashes
- create_git_branch, merge_git_branch
- detect_merge_conflicts

### Priority 5: User Directive System (16 helpers)
Use Case 2 operations:
- parse_directive_file, validate_directive_structure
- insert_directive, insert_trigger, insert_action
- update_directive_status
- get_directive_execution_logs

### Priority 6: Remaining (130+ helpers)
- Analysis & metrics
- Maintenance & utilities
- Preferences (partially done)
- Core directive queries

---

## Next Steps for Phase 8

1. **Validate this analysis** - Review directive workflows to confirm helper usage
2. **Start with Priority 1-2** - Map aifp_status and task management helpers
3. **Work through priorities systematically** - One category at a time
4. **Update helper JSON files** - Add used_by_directives entries
5. **Assign file paths** - Replace TODO placeholders with actual paths
6. **Create validation script** - Ensure integrity across all mappings

**Estimated Time**: 2-3 days for complete helper mapping (195 helpers)

---

**Analysis Date**: 2025-12-19
**Status**: Ready for Phase 8 implementation

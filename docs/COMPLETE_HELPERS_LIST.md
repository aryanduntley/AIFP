# Complete Helper Functions List

**Total Helpers**: 218

---

## Summary by Category

- **global**: 1 helpers
- **core**: 38 helpers
- **orchestrators**: 12 helpers
- **project**: 114 helpers
- **git**: 11 helpers
- **user_preferences**: 22 helpers
- **user_directives**: 20 helpers

---

## Global (1 helpers)

### From: `helpers-index.json`

1. **get_databases** 🔧
   - Purpose: Get list of all available databases with metadata
   - Target: `TODO_helpers/global/database_info.py`

---

## Core (38 helpers)

### From: `helpers-core.json`

1. **core_allowed_check_constraints** 🔧
   - Purpose: Returns list of allowed values for CHECK constraint enum fields in aifp_core.db. Parses schema to extract CHECK(field IN (...)) constraints.
   - Target: `helpers/core/validation.py`

2. **get_core_tables** 🔧
   - Purpose: List all tables in core database
   - Target: `TODO_helpers/core/module.py`

3. **get_core_fields** 🔧
   - Purpose: Get field names and types for a specific table
   - Target: `TODO_helpers/core/module.py`

4. **get_core_schema** 🔧
   - Purpose: Get complete schema for core database (all tables and fields)
   - Target: `TODO_helpers/core/module.py`

5. **get_from_core** 🔧
   - Purpose: Get records by ID(s), or all records if empty array
   - Target: `TODO_helpers/core/module.py`

6. **get_from_core_where** 🔧
   - Purpose: Flexible filtering with structured JSON conditions
   - Target: `TODO_helpers/core/module.py`

7. **query_core** 🔧
   - Purpose: Execute complex SQL WHERE clause (advanced, rare use)
   - Target: `TODO_helpers/core/module.py`

8. **get_directive_by_name** 🔧
   - Purpose: Get specific directive by name (high-frequency operation)
   - Target: `TODO_helpers/core/module.py`

9. **get_all_directives** 🔧
   - Purpose: Load all directives for caching (special orchestrator)
   - Target: `TODO_helpers/core/module.py`

10. **search_directives** 🔧
   - Purpose: Search directives with filters (orchestrator)
   - Target: `TODO_helpers/core/module.py`

11. **find_directive_by_intent** 🔧
   - Purpose: Map user intent to directives using NLP/keyword matching
   - Target: `TODO_helpers/core/module.py`

12. **find_directives_by_intent_keyword**
   - Purpose: Find directive IDs matching one or more intent keywords (direct keyword lookup)
   - Target: `TODO_helpers/core/module.py`

13. **get_directives_with_intent_keywords** 🔧
   - Purpose: Search directives by intent keywords and return full directive objects
   - Target: `TODO_helpers/core/module.py`

14. **add_directive_intent_keyword**
   - Purpose: Add an intent keyword to a directive
   - Target: `TODO_helpers/core/module.py`

15. **remove_directive_intent_keyword**
   - Purpose: Remove an intent keyword from a directive
   - Target: `TODO_helpers/core/module.py`

16. **get_directive_keywords** 🔧
   - Purpose: Get all intent keywords for a specific directive
   - Target: `TODO_helpers/core/module.py`

17. **get_all_directive_keywords** 🔧
   - Purpose: Get list of all unique intent keywords available for searching (simple list)
   - Target: `TODO_helpers/core/module.py`

18. **get_all_intent_keywords_with_counts** 🔧
   - Purpose: Get all unique intent keywords with usage counts for analytics
   - Target: `TODO_helpers/core/module.py`

19. **get_next_directives_from_status** 🔧
   - Purpose: Get all possible next directives with condition evaluation (sequential workflow flows only, ignores wildcard '*' flows)
   - Target: `TODO_helpers/core/module.py`

20. **get_matching_next_directives** 🔧
   - Purpose: Get ONLY directives whose conditions match current state (filtered subset, ignores wildcard '*' flows)
   - Target: `TODO_helpers/core/module.py`

21. **get_completion_loop_target** 🔧
   - Purpose: Get where to loop back after completing directive
   - Target: `TODO_helpers/core/module.py`

22. **get_conditional_work_paths** 🔧
   - Purpose: Query directive_flow table for flow_type='conditional' to determine context-based next directive (ignores wildcard '*' flows, sequential flows only)
   - Target: `TODO_helpers/core/module.py`

23. **get_helper_by_name** 🔧
   - Purpose: Get specific helper function details (high-frequency)
   - Target: `TODO_helpers/core/module.py`

24. **get_helpers_by_database** 🔧
   - Purpose: Get all helpers for a specific database
   - Target: `TODO_helpers/core/module.py`

25. **get_helpers_are_tool** 🔧
   - Purpose: Get all MCP tools (is_tool=true)
   - Target: `TODO_helpers/core/module.py`

26. **get_helpers_not_tool_not_sub** 🔧
   - Purpose: Get all directive-callable helpers
   - Target: `TODO_helpers/core/module.py`

27. **get_helpers_are_sub** 🔧
   - Purpose: Get all sub-helpers (is_sub_helper=true)
   - Target: `TODO_helpers/core/module.py`

28. **get_helpers_for_directive** 🔧
   - Purpose: Get all helpers used by a directive
   - Target: `TODO_helpers/core/module.py`

29. **get_directives_for_helper** 🔧
   - Purpose: Get all directives that use a helper (reciprocal lookup)
   - Target: `TODO_helpers/core/module.py`

30. **get_category_by_name** 🔧
   - Purpose: Get category by name (fairly frequent)
   - Target: `TODO_helpers/core/module.py`

31. **get_categories** 🔧
   - Purpose: Get all directive categories
   - Target: `TODO_helpers/core/module.py`

32. **get_directives_by_category** 🔧
   - Purpose: Get all directives in a category
   - Target: `TODO_helpers/core/module.py`

33. **get_directives_by_type** 🔧
   - Purpose: Get all directives filtered by type (orchestration vs reference)
   - Target: `TODO_helpers/core/module.py`

34. **get_fp_directive_index** 🔧
   - Purpose: Get lightweight FP directive index grouped by category (names only, not full definitions)
   - Target: `TODO_helpers/core/module.py`

35. **get_all_directive_names** 🔧
   - Purpose: Get list of all directive names (or filtered by types). Returns names only, NOT full directive data. AI queries by name when needs details.
   - Target: `TODO_helpers/core/module.py`

36. **get_directive_flows** 🔧
   - Purpose: General-purpose query for directive flows by category, type, or directive names. Complements navigation helpers (get_next_directives_from_status, etc.) which are specialized for workflow routing.
   - Target: `TODO_helpers/core/module.py`

37. **search_fp_references** 🔧
   - Purpose: Get FP directives available for consultation from ANY context. Handles wildcard '*' reference_consultation flows. Returns FP directives AI can consult as reference material DURING any operation.
   - Target: `TODO_helpers/core/module.py`

38. **get_contextual_utilities** 🔧
   - Purpose: Get utility directives available in current context. Handles wildcard '*' utility and conditional flows. Returns cross-cutting utilities AI can invoke from any directive.
   - Target: `TODO_helpers/core/module.py`

---

## Orchestrators (12 helpers)

### From: `helpers-orchestrators.json`

1. **aifp_run** 🔧
   - Purpose: Main entry point orchestrator. Can be called on every user interaction or automatically on start. Optionally bundles comprehensive session startup data.
   - Target: `helpers/orchestrators/orchestrators.py`

2. **get_current_progress** 🔧
   - Purpose: Single entry point for all project status queries. Replaces 5-10 separate helper calls with one flexible query.
   - Target: `TODO_helpers/orchestrator/module.py`

3. **update_project_state** 🔧
   - Purpose: Single entry point for common project state updates. Simplifies task lifecycle management and progress tracking.
   - Target: `TODO_helpers/orchestrator/module.py`

4. **batch_update_progress** 🔧
   - Purpose: Update multiple project items atomically. Used after code generation or bulk operations to ensure consistency.
   - Target: `TODO_helpers/orchestrator/module.py`

5. **query_project_state** 🔧
   - Purpose: Flexible SQL-like query interface for complex project queries. Provides powerful filtering and joining capabilities without writing SQL.
   - Target: `TODO_helpers/orchestrator/module.py`

6. **validate_initialization** 🔧
   - Purpose: Validate that project initialization is complete and correct. Performs comprehensive structural validation.
   - Target: `TODO_helpers/orchestrator/module.py`

7. **get_work_context** 🔧
   - Purpose: Get complete context for resuming work. Single call retrieves task/subtask/sidequest + flows + files + functions + interactions. Optimized for session resumption.
   - Target: `TODO_helpers/orchestrator/module.py`

8. **aifp_status** 🔧
   - Purpose: Status orchestrator optimized for directive navigation decision tree. Returns comprehensive project state with completion flags and next-step suggestions designed to feed the `get_next_directives_from_status()` system.
   - Target: `TODO_helpers/orchestrator/module.py`

9. **get_project_status** 🔧 📦
   - Purpose: Analyze entire work hierarchy and return comprehensive project status
   - Target: `TODO_helpers/orchestrator/module.py`

10. **get_project_context** 🔧
   - Purpose: Get structured project overview for different contexts
   - Target: `TODO_helpers/orchestrator/module.py`

11. **get_status_tree** 🔧 📦
   - Purpose: Get hierarchical view of all work items with nested structure
   - Target: `TODO_helpers/orchestrator/module.py`

12. **get_files_by_flow_context**
   - Purpose: Get all files for a flow with functions embedded
   - Target: `TODO_helpers/orchestrator/module.py`

---

## Project (114 helpers)

### From: `helpers-project-1.json`

1. **project_allowed_check_constraints** 🔧
   - Purpose: Returns list of allowed values for CHECK constraint enum fields in project.db. Parses schema to extract CHECK(field IN (...)) constraints.
   - Target: `helpers/project/validation.py`

2. **get_project_tables** 🔧
   - Purpose: List all tables in project database
   - Target: `TODO_helpers/project/module.py`

3. **get_project_fields** 🔧
   - Purpose: Get field names and types for a specific table
   - Target: `TODO_helpers/project/module.py`

4. **get_project_schema** 🔧
   - Purpose: Get complete schema for project database
   - Target: `TODO_helpers/project/module.py`

5. **get_project_json_parameters** 🔧
   - Purpose: Get available fields for table to use with generic add/update operations
   - Target: `TODO_helpers/project/module.py`

6. **get_from_project** 🔧
   - Purpose: Get records by ID(s) - **EMPTY ARRAY NOT ALLOWED**
   - Target: `TODO_helpers/project/module.py`

7. **get_from_project_where** 🔧
   - Purpose: Flexible filtering with structured JSON conditions
   - Target: `TODO_helpers/project/module.py`

8. **query_project** 🔧
   - Purpose: Execute complex SQL WHERE clause (advanced, rare use)
   - Target: `TODO_helpers/project/module.py`

9. **add_project_entry** 🔧
   - Purpose: Add new entry to project database
   - Target: `TODO_helpers/project/module.py`

10. **update_project_entry** 🔧
   - Purpose: Update existing entry
   - Target: `TODO_helpers/project/module.py`

11. **delete_project_entry** 🔧
   - Purpose: Smart delete with automatic routing to specialized functions when needed
   - Target: `TODO_helpers/project/module.py`

12. **delete_reserved** 🔧
   - Purpose: Delete abandoned reserved entries (escape hatch for cancelled reserve operations)
   - Target: `TODO_helpers/project/module.py`

13. **create_project** 🔧
   - Purpose: Initialize project entry (one per database)
   - Target: `TODO_helpers/project/module.py`

14. **get_project** 🔧
   - Purpose: Get project metadata (single entry)
   - Target: `TODO_helpers/project/module.py`

15. **update_project** 🔧
   - Purpose: Update project metadata
   - Target: `TODO_helpers/project/module.py`

16. **blueprint_has_changed** 🔧
   - Purpose: Check if ProjectBlueprint.md has changed using Git or filesystem timestamp
   - Target: `TODO_helpers/project/module.py`

17. **get_infrastructure_by_type** 🔧
   - Purpose: Get all infrastructure of specific type
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-2.json`

1. **reserve_file** 🔧
   - Purpose: Reserve file ID for naming before creation
   - Target: `TODO_helpers/project/module.py`

2. **reserve_files** 🔧
   - Purpose: Reserve multiple file IDs at once
   - Target: `TODO_helpers/project/module.py`

3. **finalize_file** 🔧
   - Purpose: Finalize reserved file after creation
   - Target: `TODO_helpers/project/module.py`

4. **finalize_files** 🔧
   - Purpose: Finalize multiple reserved files
   - Target: `TODO_helpers/project/module.py`

5. **get_file_by_name** 🔧
   - Purpose: Get file by name (high-frequency lookup)
   - Target: `TODO_helpers/project/module.py`

6. **get_file_by_path** 🔧
   - Purpose: Get file by path (very high-frequency lookup)
   - Target: `TODO_helpers/project/module.py`

7. **update_file** 🔧
   - Purpose: Update file metadata
   - Target: `TODO_helpers/project/module.py`

8. **file_has_changed** 🔧
   - Purpose: Check if file changed using Git (if available) or filesystem timestamp
   - Target: `TODO_helpers/project/module.py`

9. **update_file_timestamp** 📦
   - Purpose: Update file timestamp (called automatically after function updates)
   - Target: `TODO_helpers/project/module.py`

10. **delete_file** 🔧
   - Purpose: Delete file with comprehensive cross-reference validation
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-3.json`

1. **reserve_function** 🔧
   - Purpose: Reserve function ID for naming before creation
   - Target: `TODO_helpers/project/module.py`

2. **reserve_functions** 🔧
   - Purpose: Reserve multiple function IDs
   - Target: `TODO_helpers/project/module.py`

3. **finalize_function** 🔧
   - Purpose: Finalize reserved function after creation
   - Target: `TODO_helpers/project/module.py`

4. **finalize_functions** 🔧
   - Purpose: Finalize multiple reserved functions
   - Target: `TODO_helpers/project/module.py`

5. **get_function_by_name** 🔧
   - Purpose: Get function by name (very high-frequency lookup)
   - Target: `TODO_helpers/project/module.py`

6. **get_functions_by_file** 🔧
   - Purpose: Get all functions in a file (high-frequency)
   - Target: `TODO_helpers/project/module.py`

7. **update_function** 🔧
   - Purpose: Update function metadata
   - Target: `TODO_helpers/project/module.py`

8. **update_functions_for_file** 🔧
   - Purpose: Update multiple functions in a single file
   - Target: `TODO_helpers/project/module.py`

9. **update_function_file_location**
   - Purpose: Move function to different file (rarely used)
   - Target: `TODO_helpers/project/module.py`

10. **delete_function** 🔧
   - Purpose: Delete function with validation and interaction cascade
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-4.json`

1. **reserve_type** 🔧
   - Purpose: Reserve type ID for naming before creation
   - Target: `TODO_helpers/project/module.py`

2. **reserve_types** 🔧
   - Purpose: Reserve multiple type IDs
   - Target: `TODO_helpers/project/module.py`

3. **finalize_type** 🔧
   - Purpose: Finalize reserved type after creation
   - Target: `TODO_helpers/project/module.py`

4. **finalize_types** 🔧
   - Purpose: Finalize multiple reserved types
   - Target: `TODO_helpers/project/module.py`

5. **update_type** 🔧
   - Purpose: Update type metadata
   - Target: `TODO_helpers/project/module.py`

6. **delete_type** 🔧
   - Purpose: Delete type with relationship validation
   - Target: `TODO_helpers/project/module.py`

7. **add_types_functions** 🔧
   - Purpose: Add type-function relationship(s)
   - Target: `TODO_helpers/project/module.py`

8. **update_type_function_role**
   - Purpose: Update relationship role only
   - Target: `TODO_helpers/project/module.py`

9. **delete_type_function**
   - Purpose: Remove type-function relationship
   - Target: `TODO_helpers/project/module.py`

10. **add_interaction** 🔧
   - Purpose: Add function dependency/interaction
   - Target: `TODO_helpers/project/module.py`

11. **add_interactions** 🔧
   - Purpose: Add multiple interactions at once
   - Target: `TODO_helpers/project/module.py`

12. **update_interaction** 🔧
   - Purpose: Update interaction metadata
   - Target: `TODO_helpers/project/module.py`

13. **delete_interaction**
   - Purpose: Delete interaction
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-5.json`

1. **get_theme_by_name** 🔧
   - Purpose: Get theme by name (fairly frequent)
   - Target: `TODO_helpers/project/module.py`

2. **get_flow_by_name** 🔧
   - Purpose: Get flow by name (fairly frequent)
   - Target: `TODO_helpers/project/module.py`

3. **get_all_themes** 🔧
   - Purpose: Get all project themes
   - Target: `TODO_helpers/project/module.py`

4. **get_all_flows** 🔧
   - Purpose: Get all project flows
   - Target: `TODO_helpers/project/module.py`

5. **add_theme** 🔧
   - Purpose: Add project theme
   - Target: `TODO_helpers/project/module.py`

6. **update_theme** 🔧
   - Purpose: Update theme metadata
   - Target: `TODO_helpers/project/module.py`

7. **delete_theme** 🔧
   - Purpose: Delete theme with flow validation
   - Target: `TODO_helpers/project/module.py`

8. **add_flow** 🔧
   - Purpose: Add project flow
   - Target: `TODO_helpers/project/module.py`

9. **get_file_ids_from_flows** 🔧
   - Purpose: Get all file IDs associated with flows
   - Target: `TODO_helpers/project/module.py`

10. **update_flow** 🔧
   - Purpose: Update flow metadata
   - Target: `TODO_helpers/project/module.py`

11. **delete_flow** 🔧
   - Purpose: Delete flow with file validation
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-6.json`

1. **get_flows_for_theme** 🔧
   - Purpose: Get all flows for a theme
   - Target: `TODO_helpers/project/module.py`

2. **get_themes_for_flow** 🔧
   - Purpose: Get all themes for a flow
   - Target: `TODO_helpers/project/module.py`

3. **get_files_by_flow** 🔧
   - Purpose: Get all files for a flow
   - Target: `TODO_helpers/project/module.py`

4. **get_flows_for_file** 🔧
   - Purpose: Get all flows for a file
   - Target: `TODO_helpers/project/module.py`

5. **add_completion_path** 🔧
   - Purpose: Add completion path stage
   - Target: `TODO_helpers/project/module.py`

6. **get_all_completion_paths** 🔧
   - Purpose: Get all completion paths ordered by order_index
   - Target: `TODO_helpers/project/module.py`

7. **get_next_completion_path** 🔧
   - Purpose: Get lowest order_index with status != completed
   - Target: `TODO_helpers/project/module.py`

8. **get_completion_paths_by_status** 🔧
   - Purpose: Get completion paths filtered by status
   - Target: `TODO_helpers/project/module.py`

9. **get_incomplete_completion_paths** 🔧
   - Purpose: Get all non-completed paths
   - Target: `TODO_helpers/project/module.py`

10. **update_completion_path** 🔧
   - Purpose: Update completion path
   - Target: `TODO_helpers/project/module.py`

11. **delete_completion_path** 🔧
   - Purpose: Delete completion path with milestone validation
   - Target: `TODO_helpers/project/module.py`

12. **reorder_completion_path**
   - Purpose: Change order_index for a completion path
   - Target: `TODO_helpers/project/module.py`

13. **reorder_all_completion_paths**
   - Purpose: Fix gaps and duplicates in order_index
   - Target: `TODO_helpers/project/module.py`

14. **swap_completion_paths_order**
   - Purpose: Swap order_index of two completion paths
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-7.json`

1. **add_milestone** 🔧
   - Purpose: Add milestone to completion path
   - Target: `TODO_helpers/project/module.py`

2. **get_milestones_by_path** 🔧
   - Purpose: Get all milestones for a completion path
   - Target: `TODO_helpers/project/module.py`

3. **get_milestones_by_status** 🔧
   - Purpose: Get milestones filtered by status
   - Target: `TODO_helpers/project/module.py`

4. **get_incomplete_milestones** 🔧
   - Purpose: Get all non-completed milestones
   - Target: `TODO_helpers/project/module.py`

5. **update_milestone** 🔧
   - Purpose: Update milestone metadata
   - Target: `TODO_helpers/project/module.py`

6. **delete_milestone** 🔧
   - Purpose: Delete milestone with task validation
   - Target: `TODO_helpers/project/module.py`

7. **add_task** 🔧
   - Purpose: Add task to milestone
   - Target: `TODO_helpers/project/module.py`

8. **get_incomplete_tasks_by_milestone** 🔧
   - Purpose: Get open tasks for a milestone with related subtasks/sidequests
   - Target: `TODO_helpers/project/module.py`

9. **get_incomplete_tasks** 🔧
   - Purpose: Get all incomplete tasks with subtasks/sidequests
   - Target: `TODO_helpers/project/module.py`

10. **get_tasks_by_milestone** 🔧
   - Purpose: Get all tasks for a milestone (any status)
   - Target: `TODO_helpers/project/module.py`

11. **get_tasks_comprehensive** 🔧
   - Purpose: Advanced task search with multiple filters
   - Target: `TODO_helpers/project/module.py`

12. **get_task_flows** 🔧
   - Purpose: Get flow IDs for a task
   - Target: `TODO_helpers/project/module.py`

13. **get_task_files** 🔧
   - Purpose: Get all files related to task via flows (orchestrator)
   - Target: `TODO_helpers/project/module.py`

14. **update_task** 🔧
   - Purpose: Update task metadata
   - Target: `TODO_helpers/project/module.py`

15. **delete_task** 🔧
   - Purpose: Delete task with item validation
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-8.json`

1. **add_subtask** 🔧
   - Purpose: Add subtask to task
   - Target: `TODO_helpers/project/module.py`

2. **get_incomplete_subtasks** 🔧
   - Purpose: Get all non-completed subtasks
   - Target: `TODO_helpers/project/module.py`

3. **get_incomplete_subtasks_by_task** 🔧
   - Purpose: Get incomplete subtasks for specific task
   - Target: `TODO_helpers/project/module.py`

4. **get_subtasks_by_task** 🔧
   - Purpose: Get subtasks for task, optionally filtered by status
   - Target: `TODO_helpers/project/module.py`

5. **get_subtasks_comprehensive** 🔧
   - Purpose: Advanced subtask search
   - Target: `TODO_helpers/project/module.py`

6. **update_subtask** 🔧
   - Purpose: Update subtask metadata
   - Target: `TODO_helpers/project/module.py`

7. **delete_subtask** 🔧
   - Purpose: Delete subtask with item validation (same logic as delete_task)
   - Target: `TODO_helpers/project/module.py`

8. **add_sidequest** 🔧
   - Purpose: Add sidequest (urgent interruption)
   - Target: `TODO_helpers/project/module.py`

9. **get_incomplete_sidequests** 🔧
   - Purpose: Get all non-completed sidequests
   - Target: `TODO_helpers/project/module.py`

10. **get_sidequests_comprehensive** 🔧
   - Purpose: Advanced sidequest search
   - Target: `TODO_helpers/project/module.py`

11. **get_sidequest_flows** 🔧
   - Purpose: Get flow IDs for a sidequest
   - Target: `TODO_helpers/project/module.py`

12. **get_sidequest_files** 🔧
   - Purpose: Get all files related to sidequest via flows (orchestrator)
   - Target: `TODO_helpers/project/module.py`

13. **update_sidequest** 🔧
   - Purpose: Update sidequest metadata
   - Target: `TODO_helpers/project/module.py`

14. **delete_sidequest** 🔧
   - Purpose: Delete sidequest with item validation (same logic as delete_task)
   - Target: `TODO_helpers/project/module.py`

### From: `helpers-project-9.json`

1. **get_items_for_task** 🔧
   - Purpose: Get items for task, optionally filtered by status
   - Target: `TODO_helpers/project/module.py`

2. **get_items_for_subtask** 🔧
   - Purpose: Get items for subtask
   - Target: `TODO_helpers/project/module.py`

3. **get_items_for_sidequest** 🔧
   - Purpose: Get items for sidequest
   - Target: `TODO_helpers/project/module.py`

4. **get_incomplete_items** 🔧
   - Purpose: Get incomplete items for any parent type
   - Target: `TODO_helpers/project/module.py`

5. **delete_item** 🔧
   - Purpose: Delete item with status validation
   - Target: `TODO_helpers/project/module.py`

6. **add_note** 🔧
   - Purpose: Add note to project database
   - Target: `TODO_helpers/project/module.py`

7. **get_notes_comprehensive** 🔧
   - Purpose: Advanced note search with filters
   - Target: `TODO_helpers/project/module.py`

8. **search_notes** 🔧
   - Purpose: Search note content with optional filters
   - Target: `TODO_helpers/project/module.py`

9. **update_note** 🔧
   - Purpose: Update note metadata
   - Target: `TODO_helpers/project/module.py`

10. **delete_note**
   - Purpose: Delete note (discouraged)
   - Target: `TODO_helpers/project/module.py`

---

## Git (11 helpers)

### From: `helpers-git.json`

1. **get_current_commit_hash**
   - Purpose: Get current Git HEAD commit hash
   - Target: `TODO_helpers/project/module.py`

2. **get_current_branch**
   - Purpose: Get current Git branch name
   - Target: `TODO_helpers/project/module.py`

3. **get_git_status** 🔧
   - Purpose: Get comprehensive Git state snapshot (orchestrator)
   - Target: `TODO_helpers/project/module.py`

4. **detect_external_changes** 🔧
   - Purpose: Compare current Git HEAD with project.last_known_git_hash
   - Target: `TODO_helpers/project/module.py`

5. **create_user_branch** 🔧
   - Purpose: Create work branch following aifp-{user}-{number} convention
   - Target: `TODO_helpers/project/module.py`

6. **get_user_name_for_branch** 📦
   - Purpose: Detect username from git config/environment/system
   - Target: `TODO_helpers/project/module.py`

7. **list_active_branches** 🔧
   - Purpose: List all AIFP work branches from work_branches table
   - Target: `TODO_helpers/project/module.py`

8. **detect_conflicts_before_merge** 🔧
   - Purpose: FP-powered conflict analysis before merging (complex orchestrator)
   - Target: `TODO_helpers/project/module.py`

9. **merge_with_fp_intelligence** 🔧
   - Purpose: Git merge with FP-powered conflict auto-resolution (complex orchestrator)
   - Target: `TODO_helpers/project/module.py`

10. **sync_git_state** 🔧
   - Purpose: Update project.last_known_git_hash with current Git HEAD
   - Target: `TODO_helpers/project/module.py`

11. **project_update_git_status** 📦
   - Purpose: Update last_known_git_hash and last_git_sync in project table
   - Target: `TODO_helpers/project/module.py`

---

## User Preferences (22 helpers)

### From: `helpers-settings.json`

1. **user_preferences_allowed_check_constraints** 🔧
   - Purpose: Returns list of allowed values for CHECK constraint enum fields in user_preferences.db. Parses schema to extract CHECK(field IN (...)) constraints.
   - Target: `helpers/user_preferences/validation.py`

2. **get_settings_tables** 🔧
   - Purpose: List all tables in user settings database
   - Target: `TODO_helpers/settings/module.py`

3. **get_settings_fields** 🔧
   - Purpose: Get field names and types for a specific table
   - Target: `TODO_helpers/settings/module.py`

4. **get_settings_schema** 🔧
   - Purpose: Get complete schema for user settings database
   - Target: `TODO_helpers/settings/module.py`

5. **get_settings_json_parameters** 🔧
   - Purpose: Get available fields for table to use with generic add/update operations
   - Target: `TODO_helpers/settings/module.py`

6. **get_from_settings** 🔧
   - Purpose: Get records by ID(s) - **EMPTY ARRAY NOT ALLOWED**
   - Target: `TODO_helpers/settings/module.py`

7. **get_from_settings_where** 🔧
   - Purpose: Flexible filtering with structured JSON conditions
   - Target: `TODO_helpers/settings/module.py`

8. **query_settings** 🔧
   - Purpose: Execute complex SQL WHERE clause (advanced, rare use)
   - Target: `TODO_helpers/settings/module.py`

9. **add_settings_entry** 🔧
   - Purpose: Add entry to user settings database
   - Target: `TODO_helpers/settings/module.py`

10. **update_settings_entry** 🔧
   - Purpose: Update entry in user settings database
   - Target: `TODO_helpers/settings/module.py`

11. **delete_settings_entry** 🔧
   - Purpose: Delete entry from user_preferences.db table
   - Target: `TODO_helpers/settings/module.py`

12. **load_directive_preferences** 🔧
   - Purpose: Load all active preferences for a directive (high-frequency)
   - Target: `TODO_helpers/settings/module.py`

13. **add_directive_preference** 🔧
   - Purpose: Add/update user preference for directive
   - Target: `TODO_helpers/settings/module.py`

14. **get_user_setting** 🔧
   - Purpose: Get project-wide user setting (fairly frequent)
   - Target: `TODO_helpers/settings/module.py`

15. **update_user_preferences** 🔧
   - Purpose: Map user request to directive preferences (orchestrator)
   - Target: `TODO_helpers/settings/module.py`

16. **apply_preferences_to_context** 📦
   - Purpose: Apply loaded preferences to execution context
   - Target: `TODO_helpers/settings/module.py`

17. **get_tracking_settings** 🔧
   - Purpose: Get all tracking feature flags
   - Target: `TODO_helpers/settings/module.py`

18. **toggle_tracking_feature** 🔧
   - Purpose: Enable/disable tracking feature
   - Target: `TODO_helpers/settings/module.py`

19. **get_user_settings** 🔧
   - Purpose: Get all user settings from user_settings table (complements get_user_setting which gets one setting by key)
   - Target: `TODO_helpers/settings/module.py`

20. **add_tracking_note** 🔧
   - Purpose: Add tracking note to user_preferences.db (only when tracking enabled)
   - Target: `TODO_helpers/settings/module.py`

21. **get_tracking_notes** 🔧
   - Purpose: Get tracking notes with optional filters
   - Target: `TODO_helpers/settings/module.py`

22. **search_tracking_notes** 🔧
   - Purpose: Search tracking note content with optional filters
   - Target: `TODO_helpers/settings/module.py`

---

## User Directives (20 helpers)

### From: `helpers-user-custom.json`

1. **user_directives_allowed_check_constraints** 🔧
   - Purpose: Returns list of allowed values for CHECK constraint enum fields in user_directives.db. Parses schema to extract CHECK(field IN (...)) constraints.
   - Target: `helpers/user_directives/validation.py`

2. **get_user_custom_tables** 🔧
   - Purpose: List all tables in user custom directives database
   - Target: `TODO_helpers/user_custom/module.py`

3. **get_user_custom_fields** 🔧
   - Purpose: Get field names and types for a specific table
   - Target: `TODO_helpers/user_custom/module.py`

4. **get_user_custom_schema** 🔧
   - Purpose: Get complete schema for user custom directives database
   - Target: `TODO_helpers/user_custom/module.py`

5. **get_user_custom_json_parameters** 🔧
   - Purpose: Get available fields for table to use with generic add/update operations
   - Target: `TODO_helpers/user_custom/module.py`

6. **get_from_user_custom** 🔧
   - Purpose: Get records by ID(s) - **EMPTY ARRAY NOT ALLOWED**
   - Target: `TODO_helpers/user_custom/module.py`

7. **get_from_user_custom_where** 🔧
   - Purpose: Flexible filtering with structured JSON conditions
   - Target: `TODO_helpers/user_custom/module.py`

8. **query_user_custom** 🔧
   - Purpose: Execute complex SQL WHERE clause (advanced, rare use)
   - Target: `TODO_helpers/user_custom/module.py`

9. **add_user_custom_entry** 🔧
   - Purpose: Add entry to user custom directives database
   - Target: `TODO_helpers/user_custom/module.py`

10. **update_user_custom_entry** 🔧
   - Purpose: Update entry in user custom directives database
   - Target: `TODO_helpers/user_custom/module.py`

11. **delete_user_custom_entry** 🔧
   - Purpose: Delete entry from user_directives.db table
   - Target: `TODO_helpers/user_custom/module.py`

12. **parse_directive_file** 🔧
   - Purpose: Parse YAML/JSON/TXT directive file (orchestrator)
   - Target: `TODO_helpers/user_custom/module.py`

13. **validate_directive_config** 🔧
   - Purpose: Interactive validation for parsed directive (orchestrator)
   - Target: `TODO_helpers/user_custom/module.py`

14. **generate_handler_code** 🔧
   - Purpose: Generate FP-compliant implementation code (orchestrator)
   - Target: `TODO_helpers/user_custom/module.py`

15. **deploy_background_service** 🔧
   - Purpose: Activate directive for real-time execution (orchestrator)
   - Target: `TODO_helpers/user_custom/module.py`

16. **get_user_directive_status** 🔧
   - Purpose: Get status of user directive(s) (orchestrator)
   - Target: `TODO_helpers/user_custom/module.py`

17. **monitor_directive_execution** 🔧
   - Purpose: Get execution statistics and errors (orchestrator)
   - Target: `TODO_helpers/user_custom/module.py`

18. **add_user_directive_note** 🔧
   - Purpose: Add note to user_directives.db for AI record-keeping
   - Target: `TODO_helpers/user_custom/module.py`

19. **get_user_directive_notes** 🔧
   - Purpose: Get notes from user_directives.db with optional filters
   - Target: `TODO_helpers/user_custom/module.py`

20. **search_user_directive_notes** 🔧
   - Purpose: Search note content in user_directives.db with optional filters
   - Target: `TODO_helpers/user_custom/module.py`

---

## Legend

- 🔧 = MCP Tool (is_tool=true) - AI can call directly
- 📦 = Sub-helper (is_sub_helper=true) - Internal use only
- No marker = Directive-callable helper

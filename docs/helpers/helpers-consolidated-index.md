# AIFP Helper Functions - Master Index

**Version**: 2.1
**Last Updated**: 2025-12-10
**Purpose**: Master index for AIFP helper functions with tiered generic/specialized approach

---

## Design Philosophy

### Tiered Approach to Reduce Cognitive Load

**Tier 1: High-Frequency Specific Helpers** (10-20 functions)
- Routine operations used constantly (dozens of times per session)
- Zero cognitive load - just pass the value
- No SQL thinking, no syntax errors
- Examples: `get_directive_by_name()`, `get_file_by_path()`, `get_function_by_name()`

**Tier 2: JSON-Based Filtering** (Safe, Flexible)
- Replaces 50+ granular getters with structured filtering
- Safe from SQL injection
- Predictable, structured queries
- Examples: `get_from_core_where(table, {"type": "fp", "status": "active"})`

**Tier 3: ID-Based Retrieval** (Simple, Direct)
- Get one or more records by ID
- Core DB: Empty array allowed (returns all - read-only, safe)
- Project DB: Empty array NOT allowed (prevents huge results on mutable tables)
- Examples: `get_from_core("directives", [1, 5, 12])`

**Tier 4: Raw SQL Queries** (Advanced, Rare)
- Complex OR logic, nested conditions, joins
- Use only when JSON filtering insufficient
- Examples: `query_project("files", "language='python' AND (status='active' OR priority='high')")`

### Specialized Operations (Complex Workflows)
Use for operations requiring:
- Cross-table validation
- Reserve/finalize workflows
- Cascading checks
- Side effect management
- Complex relationship graphs

---

## Global Cross-Database Operations

### Database Metadata

**`get_databases()`**
- **Purpose**: Get list of all available databases with metadata
- **Returns**:
  ```json
  [
    {
      "file_path": "/path/to/aifp_core.db",
      "name": "Core Database",
      "short_name": "core",
      "description": "AIFP directive definitions and helper functions"
    },
    {
      "file_path": "/path/to/project.db",
      "name": "Project Database",
      "short_name": "project",
      "description": "Project state, files, functions, tasks"
    },
    {
      "file_path": "/path/to/user_preferences.db",
      "name": "User Settings Database",
      "short_name": "settings",
      "description": "User preferences and AI behavior customization"
    },
    {
      "file_path": "/path/to/user_directives.db",
      "name": "User Custom Directives Database",
      "short_name": "user_custom",
      "description": "User-defined automation directives (optional)"
    }
  ]
  ```
- **Error Handling**: Return empty array if none found
- **Classification**: is_tool=true, is_sub_helper=false

---

## Database-Specific Documentation

For detailed helper function documentation for each database, see:

1. **[Core Database (aifp_core.db)](helpers-consolidated-core.md)**
   - Directive operations (get_directive_by_name, search_directives, etc.)
   - Helper function lookups (get_helper_by_name, get_helpers_by_database)
   - Category operations (get_category_by_name, get_categories)
   - Directive-helper relationships
   - Directive interactions
   - Generic operations: get_from_core(), get_from_core_where(), query_core()

2. **[Project Database (project.db)](helpers-consolidated-project.md)**
   - Project metadata & status
   - Files (reserve/finalize workflow, high-frequency lookups)
   - Functions (reserve/finalize workflow, high-frequency lookups)
   - Types (reserve/finalize workflow)
   - Type-function relationships
   - Function interactions
   - Themes & flows
   - Completion paths, milestones, tasks, subtasks, sidequests
   - Items
   - Notes
   - Infrastructure
   - Context helpers (orchestrators)
   - Generic operations: get_from_project(), get_from_project_where(), query_project()

3. **[User Settings Database (user_preferences.db)](helpers-consolidated-settings.md)**
   - User preferences (load_directive_preferences, add_directive_preference)
   - Project-wide settings (get_user_setting)
   - Tracking settings (get_tracking_settings, toggle_tracking_feature)
   - Preference orchestrators
   - Generic operations: get_from_settings(), get_from_settings_where(), query_settings()

4. **[User Custom Directives Database (user_directives.db)](helpers-consolidated-user-custom.md)**
   - User directive operations (parse_directive_file, validate_directive_config)
   - Handler code generation (generate_handler_code)
   - Background service deployment (deploy_background_service)
   - Directive monitoring (get_user_directive_status, monitor_directive_execution)
   - Generic operations: get_from_user_custom(), get_from_user_custom_where(), query_user_custom()

5. **[Git Operations](helpers-consolidated-git.md)**
   - Git status & detection (get_current_commit_hash, get_current_branch, detect_external_changes)
   - Branch management (create_user_branch, list_active_branches)
   - Conflict detection & resolution (detect_conflicts_before_merge, merge_with_fp_intelligence)
   - Git state synchronization (sync_git_state, project_update_git_status)

---

## Classification Summary

### Function Count by Tier

**Tier 1: High-Frequency Specific Helpers** (~25 functions)
- Routine operations used constantly
- Zero cognitive load
- Examples: `get_directive_by_name()`, `get_file_by_path()`, `get_function_by_name()`

**Tier 2: JSON-Based Filtering** (4 functions)
- One per database: `get_from_X_where(table, conditions, limit, orderby)`
- Replaces 50+ granular getters
- Safe, structured, predictable

**Tier 3: ID-Based Retrieval** (4 functions)
- One per database: `get_from_X(table, id_array)`
- Core: Empty array allowed (read-only)
- Project/Settings/User Custom: Empty array NOT allowed (mutable)

**Tier 4: Raw SQL Queries** (4 functions)
- One per database: `query_X(table, query)`
- Advanced, rare use only

**Specialized Workflows** (~90 functions)
- Reserve/finalize (files, functions, types)
- Delete with validation
- Complex orchestrators (work context, git operations, user directives)
- Cross-table operations

**Sub-Helpers** (5 functions)
- Internal helpers called only by other helpers
- Example: `update_file_timestamp()` - called after function updates

### Total Helper Count

**~130 total helper functions**
- ~55 MCP Tools (is_tool=true) - AI can call directly
- ~15 Directive Helpers (is_tool=false, is_sub_helper=false) - Called via directives
- ~5 Sub-Helpers (is_sub_helper=true) - Internal only

**Note**: The Directive Helpers count was corrected from an earlier estimate of ~70 to the accurate count of ~15.

### Directive Helpers (is_tool=false, is_sub_helper=false)

The following helpers are NOT MCP tools but ARE available to directives:

1. `apply_preferences_to_context` - Apply loaded preferences to execution context
2. `get_files_by_flow_context` - Get files with embedded functions for a flow
3. `update_function_file_location` - Move function to different file
4. `update_type_function_role` - Update type-function relationship role
5. `delete_type_function` - Remove type-function relationship
6. `delete_interaction` - Delete function interaction
7. `delete_note` - Delete note (discouraged)
8. `reorder_completion_path` - Change order_index for a completion path
9. `reorder_all_completion_paths` - Fix gaps and duplicates in order_index
10. `swap_completion_paths_order` - Swap order_index of two completion paths
11. `get_current_commit_hash` - Get current Git HEAD commit hash
12. `get_current_branch` - Get current Git branch name
13. `get_user_name_for_branch` - Detect username for branch creation
14. `project_update_git_status` - Update last_known_git_hash and last_git_sync

### Sub-Helpers (is_sub_helper=true)

The following helpers are internal only (called by other helpers):

1. `update_file_timestamp` - Update file timestamp and checksum (called automatically after function updates)

---

## Usage Guidelines

### When to Use Each Tier

**Use Tier 1** (Specific Helpers) when:
- Operation happens constantly (dozens of times per session)
- You need zero cognitive load
- Examples: Looking up directives, files, functions by name

**Use Tier 2** (JSON Filtering) when:
- You need flexible filtering
- You want "get all with conditions" or "get all"
- You need AND logic with multiple fields
- You want safe, structured queries

**Use Tier 3** (ID-Based) when:
- You have specific IDs to retrieve
- You want simple, direct lookup
- You need "get all" from read-only tables (core only)

**Use Tier 4** (Raw SQL) when:
- You need complex OR logic
- You need nested conditions
- You need LIKE patterns
- JSON filtering is insufficient

### Return Statements

Many helpers include `return_statements` field with AI guidance:
- **Verification prompts**: "Verify flows are added", "Check if interactions need updating"
- **Consistency reminders**: "Ensure code references updated", "Update imports/paths"
- **Warning messages**: "Note deletion removes context", "Deletion not allowed"
- **Action chaining**: "Consider calling X next", "Returned data includes Y"

---

## Notes

1. **Database Triggers**: Timestamps (created_at, updated_at) managed by SQLite triggers
2. **Checksums**: Automatically computed for files on finalize/update
3. **Naming Conventions**:
   - Files: `name-IDxxx`
   - Functions: `name_idxxx`
   - Types: `TypeName_idxxx`
4. **Cross-References**: Delete operations validate relationships before deletion
5. **Reserve/Finalize**: Required for files/functions/types to enable ID-based naming
6. **Empty Arrays**:
   - Core DB: Empty array allowed (read-only, safe)
   - Project/Settings/User Custom: Empty array NOT allowed (mutable, prevent huge results)

---

**End of Master Index v2.1**

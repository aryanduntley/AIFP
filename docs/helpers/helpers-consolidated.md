# AIFP Helper Functions - Consolidated Reference

**Version**: 2.1
**Last Updated**: 2025-12-10
**Purpose**: Consolidated helper function reference with tiered generic/specialized approach

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

## Table of Contents

1. [Global/Cross-Database Operations](#globalcross-database-operations)
2. [Core Database (aifp_core.db)](#core-database-aifp_coredb)
3. [Project Database (project.db)](#project-database-projectdb)
4. [User Settings Database (user_preferences.db)](#user-settings-database-user_preferencesdb)
5. [User Custom Directives Database (user_directives.db)](#user-custom-directives-database-user_directivesdb)
6. [Git Operations](#git-operations)

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

## Core Database (aifp_core.db)

**Location**: MCP server installation directory
**Access**: Read-only
**Short Name**: `core`

### Database Metadata

**`get_core_tables()`**
- **Purpose**: List all tables in core database
- **Returns**: Array of table names
- **Classification**: is_tool=true, is_sub_helper=false

**`get_core_fields(table)`**
- **Purpose**: Get field names and types for a specific table
- **Parameters**:
  - `table` (String) - Table name
- **Returns**:
  ```json
  [
    {"field": "id", "type": "INTEGER", "nullable": false, "primary_key": true},
    {"field": "name", "type": "TEXT", "nullable": false, "unique": true}
  ]
  ```
- **Classification**: is_tool=true, is_sub_helper=false

**`get_core_schema()`**
- **Purpose**: Get complete schema for core database (all tables and fields)
- **Returns**: Object mapping table names to field arrays
- **Classification**: is_tool=true, is_sub_helper=false

---

## Generic Core Operations (Tier 2-4)

### Tier 3: ID-Based Retrieval

**`get_from_core(table, id_array)`**
- **Purpose**: Get records by ID(s), or all records if empty array
- **Parameters**:
  - `table` (String) - Table name
  - `id_array` (Array of Integers) - IDs to fetch, **empty array [] returns ALL records**
- **Returns**: Array of records
- **Error Handling**: Return empty array if no matches
- **Note**: Empty array allowed for core (read-only, safe to return all)
- **Use Case**: "Get me these specific records" or "Get me everything"
- **Examples**:
  - `get_from_core("directives", [1, 5, 12])` - Get 3 specific directives
  - `get_from_core("categories", [])` - Get all categories
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 2: JSON-Based Filtering

**`get_from_core_where(table, conditions, limit, orderby)`**
- **Purpose**: Flexible filtering with structured JSON conditions
- **Parameters**:
  - `table` (String) - Table name
  - `conditions` (Object) - Field-value pairs (AND logic), e.g., `{"type": "fp", "category": "purity"}`
  - `limit` (Integer, optional) - Maximum rows to return
  - `orderby` (String, optional) - Sort order, e.g., "name ASC" or "id DESC"
- **Returns**: Array of matching records
- **Error Handling**: Return empty array if no matches, error if invalid field names
- **Safety**: Automatically constructs safe WHERE clause, no SQL injection risk
- **Use Case**: "Get records where field1=value1 AND field2=value2"
- **Examples**:
  - `get_from_core_where("directives", {"type": "fp", "category": "purity"}, 10, "name ASC")`
  - `get_from_core_where("helpers", {"target_database": "project", "is_tool": true})`
  - `get_from_core_where("directives", {"level": 0}, null, "order_index ASC")`
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 4: Raw SQL Queries

**`query_core(table, query)`**
- **Purpose**: Execute complex SQL WHERE clause (advanced, rare use)
- **Parameters**:
  - `table` (String) - Table name
  - `query` (String) - WHERE clause without "WHERE" keyword
- **Returns**: Array of matching rows
- **Error Handling**: Return error if SQL syntax invalid
- **Use Case**: Complex OR logic, nested conditions, LIKE patterns
- **Examples**:
  - `query_core("directives", "type='fp' AND (category='purity' OR category='immutability') ORDER BY level DESC LIMIT 5")`
  - `query_core("helpers", "name LIKE '%project%' AND is_tool=1")`
- **Note**: Use Tier 2 (JSON filtering) whenever possible, reserve this for truly complex queries
- **Classification**: is_tool=true, is_sub_helper=false

---

## Tier 1: High-Frequency Core Helpers

### Directives (Used Constantly)

**`get_directive_by_name(directive_name)`**
- **Purpose**: Get specific directive by name (high-frequency operation)
- **Parameters**: `directive_name` (String)
- **Returns**: Directive object or null
- **Note**: Zero cognitive load - use this instead of constructing queries
- **Classification**: is_tool=true, is_sub_helper=false

**`get_all_directives()`**
- **Purpose**: Load all directives for caching (special orchestrator)
- **Returns**: Array of all directives with self-assessment questions
- **Note**: Called once per session for context caching
- **Classification**: is_tool=true, is_sub_helper=false

**`get_directive_content(directive_name)`**
- **Purpose**: Load full MD documentation for directive
- **Parameters**: `directive_name` (String)
- **Returns**: Markdown content string
- **Note**: Retrieves comprehensive directive guidance from MD files
- **Classification**: is_tool=true, is_sub_helper=false

**`search_directives(keyword, category, type)`**
- **Purpose**: Search directives with filters (orchestrator)
- **Parameters**: All optional - keyword, category, type
- **Returns**: Array of matching directives
- **Note**: Higher-level search functionality beyond simple queries
- **Classification**: is_tool=true, is_sub_helper=false

**`find_directive_by_intent(user_request, threshold)`**
- **Purpose**: Map user intent to directives using NLP/keyword matching
- **Parameters**:
  - `user_request` (String)
  - `threshold` (Float, default 0.7) - Confidence threshold
- **Returns**: Array of matching directives with confidence scores
- **Note**: Intelligent mapping beyond simple lookups
- **Classification**: is_tool=true, is_sub_helper=false

### Directive Relationships

**`get_directive_interactions(directive_name)`**
- **Purpose**: Get directive relationships (triggers, depends_on, escalates_to)
- **Parameters**: `directive_name` (String)
- **Returns**: Object with categorized relationship arrays
- **Note**: Specialized orchestrator for relationship graph
- **Classification**: is_tool=true, is_sub_helper=false

**`get_interactions_for_directive(source_directive_id)`**
- **Purpose**: Get all interactions where directive is source (active only)
- **Parameters**: `source_directive_id` (Integer)
- **Returns**: Array of interactions where active=1
- **Return Statements**: "Consider calling get_from_core_where() with target directive IDs"
- **Classification**: is_tool=true, is_sub_helper=false

**`get_interactions_for_directive_as_target(target_directive_id)`**
- **Purpose**: Get all interactions where directive is target (active only)
- **Parameters**: `target_directive_id` (Integer)
- **Returns**: Array of interactions where active=1
- **Classification**: is_tool=true, is_sub_helper=false

### Helper Functions (Used Frequently)

**`get_helper_by_name(helper_name)`**
- **Purpose**: Get specific helper function details (high-frequency)
- **Parameters**: `helper_name` (String)
- **Returns**: Helper object with all metadata
- **Note**: Zero cognitive load for common helper lookups
- **Classification**: is_tool=true, is_sub_helper=false

**`get_helpers_by_database(target_database)`**
- **Purpose**: Get all helpers for a specific database
- **Parameters**: `target_database` (String) - "core", "project", "settings", "user_custom"
- **Returns**: Array of helper objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_helpers_are_tool()`**
- **Purpose**: Get all MCP tools (is_tool=true)
- **Returns**: Array of tool helpers
- **Classification**: is_tool=true, is_sub_helper=false

**`get_helpers_not_tool_not_sub()`**
- **Purpose**: Get all directive-callable helpers
- **Returns**: Array of directive helpers
- **Classification**: is_tool=true, is_sub_helper=false

**`get_helpers_are_sub()`**
- **Purpose**: Get all sub-helpers (is_sub_helper=true)
- **Returns**: Array of sub-helper objects
- **Classification**: is_tool=true, is_sub_helper=false

### Directive-Helper Relationships

**`get_helpers_for_directive(directive_id, include_helpers_data)`**
- **Purpose**: Get all helpers used by a directive
- **Parameters**:
  - `directive_id` (Integer)
  - `include_helpers_data` (Boolean) - If true, includes full helper_functions data
- **Returns**:
  - If false: Array of directive_helpers records
  - If true: Array with directive_helpers + full helper_functions data
- **Classification**: is_tool=true, is_sub_helper=false

**`get_directives_for_helper(helper_function_id, include_directives_data)`**
- **Purpose**: Get all directives that use a helper (reciprocal lookup)
- **Parameters**:
  - `helper_function_id` (Integer)
  - `include_directives_data` (Boolean)
- **Returns**:
  - If false: Array of directive_helpers records
  - If true: Array with directive_helpers + full directives data
- **Classification**: is_tool=true, is_sub_helper=false

### Categories (Used Fairly Often)

**`get_category_by_name(category_name)`**
- **Purpose**: Get category by name (fairly frequent)
- **Parameters**: `category_name` (String)
- **Returns**: Category object or null
- **Classification**: is_tool=true, is_sub_helper=false

**`get_categories()`**
- **Purpose**: Get all directive categories
- **Returns**: Array of category objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_directives_by_category(category_id)`**
- **Purpose**: Get all directives in a category
- **Parameters**: `category_id` (Integer)
- **Returns**: Array of directives
- **Return Statements**: "Consider using get_from_core() with returned IDs for full data"
- **Classification**: is_tool=true, is_sub_helper=false

---

## Project Database (project.db)

**Location**: `<project-root>/.aifp-project/project.db`
**Access**: Read/Write
**Short Name**: `project`

### Database Metadata

**`get_project_tables()`**
- **Purpose**: List all tables in project database
- **Returns**: Array of table names
- **Classification**: is_tool=true, is_sub_helper=false

**`get_project_fields(table)`**
- **Purpose**: Get field names and types for a specific table
- **Parameters**: `table` (String) - Table name
- **Returns**: Array of field objects with name, type, nullable, etc.
- **Classification**: is_tool=true, is_sub_helper=false

**`get_project_schema()`**
- **Purpose**: Get complete schema for project database
- **Returns**: Object mapping table names to field arrays
- **Classification**: is_tool=true, is_sub_helper=false

---

## Generic Project Operations (Tier 2-4)

### Tier 3: ID-Based Retrieval

**`get_from_project(table, id_array)`**
- **Purpose**: Get records by ID(s) - **EMPTY ARRAY NOT ALLOWED**
- **Parameters**:
  - `table` (String) - Table name
  - `id_array` (Array of Integers) - **MUST contain at least one ID**
- **Returns**: Array of records
- **Error Handling**:
  - Return empty array if no matches
  - **Return error if id_array is empty** (prevents huge results on mutable tables)
- **Note**: Project DB is mutable - tables can grow large - must specify IDs
- **Use Case**: "Get me these specific records by ID"
- **Examples**:
  - `get_from_project("files", [1, 5, 12])` - Get 3 specific files ✅
  - `get_from_project("tasks", [])` - ERROR: id_array cannot be empty ❌
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 2: JSON-Based Filtering

**`get_from_project_where(table, conditions, limit, orderby)`**
- **Purpose**: Flexible filtering with structured JSON conditions
- **Parameters**:
  - `table` (String) - Table name
  - `conditions` (Object) - Field-value pairs (AND logic)
  - `limit` (Integer, optional) - Maximum rows to return
  - `orderby` (String, optional) - Sort order
- **Returns**: Array of matching records
- **Error Handling**: Return empty array if no matches, error if invalid fields
- **Safety**: Automatically constructs safe WHERE clause
- **Use Case**: "Get records where conditions match" or "Get all with filters"
- **Examples**:
  - `get_from_project_where("files", {"language": "python", "status": "active"}, 20, "created_at DESC")`
  - `get_from_project_where("tasks", {"status": "in_progress"})` - Get all in-progress tasks
  - `get_from_project_where("functions", {"file_id": 5, "is_reserved": false})`
- **Note**: Use this for "get all" queries with optional filtering
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 4: Raw SQL Queries

**`query_project(table, query)`**
- **Purpose**: Execute complex SQL WHERE clause (advanced, rare use)
- **Parameters**:
  - `table` (String) - Table name
  - `query` (String) - WHERE clause without "WHERE" keyword
- **Returns**: Array of matching rows
- **Error Handling**: Return error if SQL syntax invalid
- **Use Case**: Complex OR logic, nested conditions, LIKE patterns
- **Examples**:
  - `query_project("files", "language='python' AND path LIKE '%src%' AND (status='active' OR priority='high')")`
  - `query_project("tasks", "milestone_id IN (1,2,3) AND status!='completed' ORDER BY priority DESC LIMIT 10")`
- **Note**: Use Tier 2 whenever possible
- **Classification**: is_tool=true, is_sub_helper=false

### Generic Write Operations

**`add_project_entry(table, data)`**
- **Purpose**: Add new entry to project database
- **Parameters**:
  - `table` (String) - Table name
  - `data` (Object) - Field-value pairs
- **Returns**: `{"success": true, "id": new_id}`
- **Restrictions**: NOT available for files, functions, or types tables (use reserve/finalize)
- **Error Handling**: Return error if used on restricted tables
- **Classification**: is_tool=true, is_sub_helper=false

**`update_project_entry(table, id, data)`**
- **Purpose**: Update existing entry
- **Parameters**:
  - `table` (String) - Table name
  - `id` (Integer) - Record ID
  - `data` (Object) - Field-value pairs to update
- **Returns**: `{"success": true, "id": id}`
- **Error Handling**: Return error if ID not found
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_project_entry(table, id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete entry with required note logging
- **Parameters**:
  - `table` (String) - Table name
  - `id` (Integer) - Record ID
  - `note_reason` (String) - Deletion reason
  - `note_severity` (String) - "info", "warning", "error"
  - `note_source` (String) - "ai" or "user"
  - `note_type` (String) - "entry_deletion"
- **Returns**: `{"success": true, "deleted_id": id}`
- **Restrictions**: Simple tables only (no complex relationships)
- **Error Handling**: Return error if cross-references exist
- **Classification**: is_tool=true, is_sub_helper=false

---

## Tier 1: High-Frequency Project Helpers

### Project Metadata & Status

**`create_project(name, purpose, goals, status, version, user_directives_status)`**
- **Purpose**: Initialize project entry (one per database)
- **Parameters**: All fields for project table
- **Returns**: `{"success": true, "project_id": 1}`
- **Note**: last_known_git_hash and last_git_sync auto-populated
- **Classification**: is_tool=true, is_sub_helper=false

**`get_project()`**
- **Purpose**: Get project metadata (single entry)
- **Returns**: Project object
- **Classification**: is_tool=true, is_sub_helper=false

**`update_project(name, purpose, goals, status, version, user_directives_status)`**
- **Purpose**: Update project metadata
- **Parameters**: All optional (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`blueprint_has_changed()`**
- **Purpose**: Check if ProjectBlueprint.md has changed
- **Returns**: `{"changed": boolean, "current_checksum": string}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_project_status()`**
- **Purpose**: Check if project initialized, get comprehensive status
- **Returns**: Object with initialization status and metadata
- **Note**: High-level orchestrator for project state
- **Classification**: is_tool=true, is_sub_helper=false

**`get_project_context(type)`**
- **Purpose**: Get structured project overview
- **Parameters**: `type` (String) - "blueprint", "metadata", "status"
- **Returns**: Contextual project data based on type
- **Note**: Orchestrator for project context
- **Classification**: is_tool=true, is_sub_helper=false

**`get_status_tree()`**
- **Purpose**: Get hierarchical status view (sidequests → subtasks → tasks with priorities)
- **Returns**: Tree structure with nested work items
- **Note**: Complex orchestrator for work visualization
- **Classification**: is_tool=true, is_sub_helper=false

### Infrastructure

**`add_infrastructure(type, value, description)`**
- **Purpose**: Add infrastructure entry (language, packages, tools)
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_infrastructure_by_type(type)`**
- **Purpose**: Get all infrastructure of specific type
- **Parameters**: `type` (String)
- **Returns**: Array of infrastructure objects
- **Classification**: is_tool=true, is_sub_helper=false

**`update_infrastructure(id, type, value, description)`**
- **Purpose**: Update infrastructure entry
- **Parameters**: All optional except id
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_infrastructure(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete infrastructure entry with note
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

---

## Files (Reserve/Finalize Workflow)

**File Naming Convention**: `filename-IDxxx` (e.g., `calculator-ID42.py`)

### Reserve/Finalize Operations

**`reserve_file(name, path, language)`**
- **Purpose**: Reserve file ID for naming before creation
- **Parameters**: Name, path, language (can be preliminary)
- **Returns**: `{"success": true, "id": reserved_id, "is_reserved": true}`
- **Return Statements**: "Use returned ID in filename as suffix -IDxx. Once created, call finalize_file()"
- **Note**: Sets is_reserved=true, created_at auto-set by trigger
- **Classification**: is_tool=true, is_sub_helper=false

**`reserve_files(file_array)`**
- **Purpose**: Reserve multiple file IDs at once
- **Parameters**: Array of `[(name, path, language), ...]`
- **Returns**: `{"success": true, "ids": [id1, id2, ...]}`
- **Return Statements**: "Use returned IDs in filenames. Call finalize_files() after creation"
- **Classification**: is_tool=true, is_sub_helper=false

**`finalize_file(file_id, name, path, language)`**
- **Purpose**: Finalize reserved file after creation
- **Parameters**:
  - `file_id` (Integer) - Reserved ID
  - `name` (String) - Final name with -IDxx suffix
  - `path` (String) - File path
  - `language` (String) - Language
- **Returns**: `{"success": true, "file_id": file_id, "checksum": checksum}`
- **Error Handling**: Return error if file doesn't exist at path
- **Return Statements**: "Verify flows are added in file_flows table if necessary"
- **Note**: Checks file exists, creates checksum, sets is_reserved=false
- **Classification**: is_tool=true, is_sub_helper=false

**`finalize_files(file_array)`**
- **Purpose**: Finalize multiple reserved files
- **Parameters**: Array of `[(file_id, name, path, language), ...]`
- **Returns**: `{"success": true, "finalized_ids": [...]}`
- **Classification**: is_tool=true, is_sub_helper=false

### High-Frequency File Helpers

**`get_file_by_name(file_name)`**
- **Purpose**: Get file by name (high-frequency lookup)
- **Parameters**: `file_name` (String)
- **Returns**: File object or null
- **Note**: Zero cognitive load for common file lookups
- **Classification**: is_tool=true, is_sub_helper=false

**`get_file_by_path(file_path)`**
- **Purpose**: Get file by path (very high-frequency lookup)
- **Parameters**: `file_path` (String)
- **Returns**: File object or null
- **Note**: Most common file lookup method
- **Classification**: is_tool=true, is_sub_helper=false

### File Operations

**`update_file(file_id, new_name, new_path, language)`**
- **Purpose**: Update file metadata
- **Parameters**: All optional except file_id (*Can Be Null)
- **Returns**: `{"success": true, "file_id": file_id}`
- **Return Statements**:
  - "Verify flows are updated in file_flows if necessary"
  - "Ensure name/path changes reflected in codebase"
- **Note**: Checksum automatically updated
- **Classification**: is_tool=true, is_sub_helper=false

**`file_has_changed(file_id)`**
- **Purpose**: Check if file content changed since last checksum
- **Parameters**: `file_id` (Integer)
- **Returns**: `{"changed": boolean, "current_checksum": string, "stored_checksum": string}`
- **Classification**: is_tool=true, is_sub_helper=false

**`update_file_checksum(file_id)`**
- **Purpose**: Update file checksum after external changes
- **Parameters**: `file_id` (Integer)
- **Returns**: `{"success": true, "new_checksum": string}`
- **Classification**: is_tool=true, is_sub_helper=false

**`update_file_timestamp(file_id)`** ⚠️ SUB-HELPER
- **Purpose**: Update file timestamp and checksum (called automatically)
- **Parameters**: `file_id` (Integer)
- **Returns**: `{"success": true}`
- **Note**: Called automatically after function updates
- **Classification**: is_tool=false, is_sub_helper=true

**`delete_file(file_id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete file with cross-reference validation
- **Parameters**: Standard deletion parameters
- **Returns**:
  - Error if file_flows, functions, or types exist for file
  - Success if no cross-references
- **Error Handling**:
  - Calls `get_flows_for_file(file_id)`, `get_from_project_where("functions", {"file_id": file_id})`, `get_from_project_where("types", {"file_id": file_id})`
  - Returns all cross-references with actionable error message
- **Return Statements**: "Handle file_flows, functions, and types before deletion allowed"
- **Classification**: is_tool=true, is_sub_helper=false

---

## Functions (Reserve/Finalize Workflow)

**Function Naming Convention**: `function_name_idxxx` (e.g., `calculate_total_id42`)

### Reserve/Finalize Operations

**`reserve_function(name, file_id, purpose, params, returns)`**
- **Purpose**: Reserve function ID for naming before creation
- **Parameters**: Preliminary function data
- **Returns**: `{"success": true, "id": reserved_id, "is_reserved": true}`
- **Return Statements**: "Use returned ID in function name as suffix _idxx. Call finalize_function() after creation"
- **Note**: Sets is_reserved=true
- **Classification**: is_tool=true, is_sub_helper=false

**`reserve_functions(function_array)`**
- **Purpose**: Reserve multiple function IDs
- **Parameters**: Array of `[(name, file_id, purpose, params, returns), ...]`
- **Returns**: `{"success": true, "ids": [...]}`
- **Classification**: is_tool=true, is_sub_helper=false

**`finalize_function(function_id, name, file_id, purpose, params, returns)`**
- **Purpose**: Finalize reserved function after creation
- **Parameters**: Final function data with _idxx suffix in name
- **Returns**: `{"success": true, "function_id": function_id, "file_id": file_id}`
- **Return Statements**: "Check if database interactions need to be added for this function"
- **Note**: Sets is_reserved=false, calls update_file_timestamp(file_id)
- **Classification**: is_tool=true, is_sub_helper=false

**`finalize_functions(function_array)`**
- **Purpose**: Finalize multiple reserved functions
- **Parameters**: Array of function data
- **Returns**: `{"success": true, "finalized_ids": [...]}`
- **Note**: Calls update_file_timestamp for each unique file_id
- **Classification**: is_tool=true, is_sub_helper=false

### High-Frequency Function Helpers

**`get_function_by_name(function_name)`**
- **Purpose**: Get function by name (very high-frequency lookup)
- **Parameters**: `function_name` (String)
- **Returns**: Function object with interaction data or null
- **Note**: Most common function lookup method
- **Return Statements**: "Interaction data included automatically"
- **Classification**: is_tool=true, is_sub_helper=false

**`get_functions_by_file(file_id)`**
- **Purpose**: Get all functions in a file (high-frequency)
- **Parameters**: `file_id` (Integer)
- **Returns**: Array of function objects with interaction data
- **Classification**: is_tool=true, is_sub_helper=false

### Function Operations

**`update_function(function_id, name, purpose, parameters, returns)`**
- **Purpose**: Update function metadata
- **Parameters**: All optional except function_id (*Can Be Null)
- **Returns**: `{"success": true, "function_id": function_id, "file_id": file_id}`
- **Return Statements**:
  - "Check if interactions need updating"
  - "Ensure code references updated if name/parameters/returns changed"
  - "Check if database interactions need to be added"
- **Note**: Calls update_file_timestamp(file_id)
- **Classification**: is_tool=true, is_sub_helper=false

**`update_functions_for_file(file_id, function_array)`**
- **Purpose**: Update multiple functions in a single file
- **Parameters**:
  - `file_id` (Integer)
  - `function_array` - Array of `[(name, purpose, parameters, returns), ...]`
- **Returns**: `{"success": true, "updated_count": count}`
- **Return Statements**:
  - "If name changed, ensure _idxxx suffix retained"
  - "Ensure code references updated for all changes"
- **Note**: Single update_file_timestamp call at end
- **Classification**: is_tool=true, is_sub_helper=false

**`update_function_file_location(function_id, old_file_id, new_file_id)`**
- **Purpose**: Move function to different file (rarely used)
- **Parameters**: Function ID and both file IDs
- **Returns**: `{"success": true}`
- **Return Statements**:
  - "Ensure code imports/paths updated"
  - "Check if database interactions need updating"
- **Note**: Calls update_file_timestamp for both files
- **Error Handling**: Return error if function_id/file_ids not found
- **Classification**: is_tool=false, is_sub_helper=false

**`delete_function(function_id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete function with cascade cleanup
- **Parameters**: Standard deletion parameters
- **Returns**: `{"success": true, "file_id": file_id}`
- **Note**:
  - Deletes all types with function_id
  - Deletes all types_functions entries
  - Deletes all interactions with function_id
  - Calls update_file_timestamp(file_id)
- **Classification**: is_tool=true, is_sub_helper=false

---

## Types (Reserve/Finalize Workflow)

**Type Naming Convention**: `TypeName_idxxx` (e.g., `Result_id42`)

### Reserve/Finalize Operations

**`reserve_type(name, definition_json, description, file_id)`**
- **Purpose**: Reserve type ID for naming before creation
- **Parameters**: Preliminary type data
- **Returns**: `{"success": true, "id": reserved_id, "is_reserved": true}`
- **Return Statements**: "Use returned ID in type name as suffix _idxx. Call finalize_type() after creation"
- **Note**: Sets is_reserved=true
- **Classification**: is_tool=true, is_sub_helper=false

**`reserve_types(type_array)`**
- **Purpose**: Reserve multiple type IDs
- **Parameters**: Array of type data
- **Returns**: `{"success": true, "ids": [...]}`
- **Classification**: is_tool=true, is_sub_helper=false

**`finalize_type(type_id, name, definition_json, description, file_id)`**
- **Purpose**: Finalize reserved type after creation
- **Parameters**: Final type data with _idxx suffix
- **Returns**: `{"success": true, "type_id": type_id, "file_id": file_id}`
- **Return Statements**:
  - "Check if types_functions relationships need to be added"
  - "Should any functions be linked in types_functions table?"
- **Note**: Sets is_reserved=false, calls update_file_timestamp(file_id)
- **Classification**: is_tool=true, is_sub_helper=false

**`finalize_types(type_array)`**
- **Purpose**: Finalize multiple reserved types
- **Parameters**: Array of type data
- **Returns**: `{"success": true, "finalized_ids": [...]}`
- **Classification**: is_tool=true, is_sub_helper=false

### Type Operations

**`update_type(type_id, name, file_id, definition_json, description)`**
- **Purpose**: Update type metadata
- **Parameters**: All optional except type_id (*Can Be Null)
- **Returns**: `{"success": true, "type_id": type_id, "file_id": file_id}`
- **Return Statements**:
  - "Check if types_functions relationships need updating"
  - "Ensure code references updated if name changed"
- **Note**: Calls update_file_timestamp(file_id)
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_type(type_id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete type with relationship validation
- **Parameters**: Standard deletion parameters
- **Returns**: Error if types_functions exist, success otherwise
- **Error Handling**:
  - Calls `get_from_project_where("types_functions", {"type_id": type_id})`
  - Returns error with list of function relationships
  - Requires manual removal/reassignment before deletion
- **Note**: Calls update_file_timestamp(file_id) on success
- **Classification**: is_tool=true, is_sub_helper=false

---

## Types-Functions Relationships

**`add_type_function(type_id, function_id, role)`**
- **Purpose**: Link type to function with role
- **Parameters**:
  - `type_id` (Integer)
  - `function_id` (Integer)
  - `role` (String) - "constructor", "method", "operator", etc.
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`add_types_functions(relationship_array)`**
- **Purpose**: Add multiple type-function relationships
- **Parameters**: Array of `[(type_id, function_id, role), ...]`
- **Returns**: `{"success": true, "ids": [...]}`
- **Classification**: is_tool=true, is_sub_helper=false

**`update_type_function_role(type_id, function_id, role)`**
- **Purpose**: Update relationship role only
- **Parameters**: Type ID, function ID, new role
- **Returns**: `{"success": true}`
- **Note**: For other changes, delete old and add new
- **Classification**: is_tool=false, is_sub_helper=false

**`delete_type_function(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Remove type-function relationship
- **Returns**: `{"success": true}`
- **Classification**: is_tool=false, is_sub_helper=false

---

## Interactions (Function Dependencies)

**`add_interaction(source, target, type, description)`**
- **Purpose**: Add function dependency/interaction
- **Parameters**:
  - `source` (String) - Source function name
  - `target` (String) - Target function name
  - `type` (String) - Interaction type
  - `description` (String)
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`add_interactions(interaction_array)`**
- **Purpose**: Add multiple interactions at once
- **Parameters**: Array of `[(source, target, type, description), ...]`
- **Returns**: `{"success": true, "ids": [...]}`
- **Classification**: is_tool=true, is_sub_helper=false

**`update_interaction(id, source, target, type, description)`**
- **Purpose**: Update interaction metadata
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_interaction(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete interaction
- **Returns**: `{"success": true}`
- **Classification**: is_tool=false, is_sub_helper=false

---

## Themes & Flows

### High-Frequency Theme/Flow Helpers

**`get_theme_by_name(theme_name)`**
- **Purpose**: Get theme by name (fairly frequent)
- **Parameters**: `theme_name` (String)
- **Returns**: Theme object or null
- **Classification**: is_tool=true, is_sub_helper=false

**`get_flow_by_name(flow_name)`**
- **Purpose**: Get flow by name (fairly frequent)
- **Parameters**: `flow_name` (String)
- **Returns**: Flow object or null
- **Classification**: is_tool=true, is_sub_helper=false

**`get_all_themes()`**
- **Purpose**: Get all project themes
- **Returns**: Array of themes
- **Classification**: is_tool=true, is_sub_helper=false

**`get_all_flows()`**
- **Purpose**: Get all project flows
- **Returns**: Array of flows
- **Classification**: is_tool=true, is_sub_helper=false

### Theme Operations

**`add_theme(name, description, ai_generated, confidence_score)`**
- **Purpose**: Add project theme
- **Returns**: `{"success": true, "id": new_id}`
- **Return Statements**: "Check if flows should be added in flow_themes"
- **Classification**: is_tool=true, is_sub_helper=false

**`update_theme(theme_id, name, description, confidence_score)`**
- **Purpose**: Update theme metadata
- **Parameters**: All optional except theme_id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Error Handling**: Error if no update fields provided
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_theme(theme_id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete theme with flow validation
- **Returns**: Error if flows exist, success otherwise
- **Error Handling**:
  - Calls `get_flows_for_theme(theme_id)`
  - Returns error listing flows that must be reassigned
- **Classification**: is_tool=true, is_sub_helper=false

### Flow Operations

**`add_flow(name, description, ai_generated, confidence_score)`**
- **Purpose**: Add project flow
- **Returns**: `{"success": true, "id": new_id}`
- **Return Statements**: "Check if files should be linked in file_flows"
- **Classification**: is_tool=true, is_sub_helper=false

**`get_file_ids_from_flows(flow_id_array)`**
- **Purpose**: Get all file IDs associated with flows
- **Parameters**: Array of flow IDs
- **Returns**: Array of file IDs
- **Classification**: is_tool=true, is_sub_helper=false

**`update_flow(flow_id, name, description, confidence_score)`**
- **Purpose**: Update flow metadata
- **Parameters**: All optional except flow_id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Error Handling**: Error if no update fields provided
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_flow(flow_id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete flow with file validation
- **Returns**: Error if files exist, success otherwise
- **Error Handling**:
  - Calls `get_files_by_flow(flow_id)`
  - Returns error listing files that must be reassigned
- **Classification**: is_tool=true, is_sub_helper=false

### Theme-Flow & File-Flow Relationships

**`add_flow_theme(flow_id, theme_id)`**
- **Purpose**: Link flow to theme
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_flows_for_theme(theme_id)`**
- **Purpose**: Get all flows for a theme
- **Returns**: Array of flow objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_themes_for_flow(flow_id)`**
- **Purpose**: Get all themes for a flow
- **Returns**: Array of theme objects
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_flow_theme(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Remove flow-theme relationship
- **Returns**: `{"success": true}`
- **Note**: No update operation - delete and add new
- **Classification**: is_tool=true, is_sub_helper=false

**`add_file_flow(file_id, flow_id)`**
- **Purpose**: Link file to flow
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_files_by_flow(flow_id)`**
- **Purpose**: Get all files for a flow
- **Returns**: Array of file objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_flows_for_file(file_id)`**
- **Purpose**: Get all flows for a file
- **Returns**: Array of flow objects
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_file_flow(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Remove file-flow relationship
- **Returns**: `{"success": true}`
- **Note**: No update operation - delete and add new
- **Classification**: is_tool=true, is_sub_helper=false

---

## Completion Path, Milestones, Tasks

### Completion Path Operations

**`add_completion_path(name, status, description, order_index)`**
- **Purpose**: Add completion path stage
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_all_completion_paths()`**
- **Purpose**: Get all completion paths ordered by order_index
- **Returns**: Array of completion path objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_next_completion_path()`**
- **Purpose**: Get lowest order_index with status != completed
- **Returns**: Next incomplete completion path
- **Classification**: is_tool=true, is_sub_helper=false

**`get_completion_paths_by_status(status)`**
- **Purpose**: Get completion paths filtered by status
- **Parameters**: `status` (String)
- **Returns**: Array ordered by order_index
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_completion_paths()`**
- **Purpose**: Get all non-completed paths
- **Returns**: Array ordered by order_index
- **Classification**: is_tool=true, is_sub_helper=false

**`update_completion_path(id, name, status, description)`**
- **Purpose**: Update completion path
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_completion_path(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete completion path with milestone validation
- **Returns**: Error if milestones exist, success otherwise
- **Error Handling**:
  - Calls `get_milestones_by_path(path_id)`
  - Returns error listing milestones that must be reassigned/removed
  - Calls `reorder_all_completion_paths()` on success
- **Classification**: is_tool=true, is_sub_helper=false

**`reorder_completion_path(id, new_order_index)`**
- **Purpose**: Change order_index for a completion path
- **Parameters**: Completion path ID and new order
- **Returns**: `{"success": true}` or error if order exists
- **Classification**: is_tool=false, is_sub_helper=false

**`reorder_all_completion_paths()`**
- **Purpose**: Fix gaps and duplicates in order_index
- **Returns**:
  ```json
  {
    "success": true,
    "gaps_fixed": integer,
    "duplicates": [{"id": x, "name": "...", "old_order": x, "new_order": x}]
  }
  ```
- **Note**: Renumbers to consecutive sequence, reports duplicates
- **Classification**: is_tool=false, is_sub_helper=false

**`swap_completion_paths_order(id_1, id_2)`**
- **Purpose**: Swap order_index of two completion paths
- **Returns**: `{"success": true}`
- **Note**: Temporarily allows duplicates during swap
- **Classification**: is_tool=false, is_sub_helper=false

### Milestone Operations

**`add_milestone(name, completion_path_id, status, description)`**
- **Purpose**: Add milestone to completion path
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_milestones_by_path(path_id)`**
- **Purpose**: Get all milestones for a completion path
- **Parameters**: `path_id` (Integer)
- **Returns**: Array of milestone objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_milestones_by_status(status)`**
- **Purpose**: Get milestones filtered by status
- **Parameters**: `status` (String)
- **Returns**: Array of milestone objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_milestones()`**
- **Purpose**: Get all non-completed milestones
- **Returns**: Array of milestone objects
- **Classification**: is_tool=true, is_sub_helper=false

**`update_milestone(id, name, completion_path_id, status, description)`**
- **Purpose**: Update milestone metadata
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_milestone(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete milestone with task validation
- **Returns**: Error if incomplete tasks exist, success otherwise
- **Error Handling**:
  - Calls `get_incomplete_tasks_by_milestone(milestone_id, skip_pending=false)`
  - Returns error listing tasks that must be completed/reassigned
- **Classification**: is_tool=true, is_sub_helper=false

### Task Operations

**`add_task(name, milestone_id, status, description, flow_ids, priority)`**
- **Purpose**: Add task to milestone
- **Parameters**:
  - `flow_ids` (Array) - JSON array of flow IDs
  - `priority` (String) - Default if not specified
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_tasks_by_milestone(milestone_id, skip_pending)`**
- **Purpose**: Get open tasks for a milestone with related subtasks/sidequests
- **Parameters**:
  - `milestone_id` (Integer)
  - `skip_pending` (Boolean) - If true, excludes pending tasks
- **Returns**:
  ```json
  {
    "tasks": [...],
    "subtasks": [...],
    "sidequests": [...]
  }
  ```
- **Note**: Ensures status=in_progress tasks included
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_tasks()`**
- **Purpose**: Get all incomplete tasks with subtasks/sidequests
- **Returns**: Object with tasks, subtasks, sidequests arrays
- **Note**: Comprehensive work overview
- **Classification**: is_tool=true, is_sub_helper=false

**`get_tasks_by_milestone(milestone_id)`**
- **Purpose**: Get all tasks for a milestone (any status)
- **Returns**: Array of task objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_tasks_comprehensive(status, limit, date_range_created, date_range_updated, milestone_id, priority)`**
- **Purpose**: Advanced task search with multiple filters
- **Parameters**: All optional
- **Returns**: Array of filtered task objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_task_flows(task_id)`**
- **Purpose**: Get flow IDs for a task
- **Parameters**: `task_id` (Integer)
- **Returns**: Array of flow IDs from flow_ids JSON field
- **Classification**: is_tool=true, is_sub_helper=false

**`get_task_files(task_id)`**
- **Purpose**: Get all files related to task via flows (orchestrator)
- **Parameters**: `task_id` (Integer)
- **Returns**: Array of file objects with full data
- **Note**: Chains get_task_flows → get_file_ids_from_flows → get_from_project()
- **Classification**: is_tool=true, is_sub_helper=false

**`update_task(id, name, milestone_id, status, description, flow_ids, priority)`**
- **Purpose**: Update task metadata
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_task(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete task with item validation
- **Returns**: Error if completed/in_progress items exist, success if only pending or no items
- **Error Handling**:
  - Calls `get_items_for_task(task_id)` (all statuses)
  - If completed/in_progress items: Error - must mark task complete instead
  - If only pending items: Error - must delete pending items first
  - If no items: Success
- **Classification**: is_tool=true, is_sub_helper=false

### Subtask Operations

**`add_subtask(name, parent_task_id, status, description, priority)`**
- **Purpose**: Add subtask to task
- **Returns**: `{"success": true, "id": new_id}`
- **Note**: Subtasks inherit task's milestone and flows
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_subtasks()`**
- **Purpose**: Get all non-completed subtasks
- **Returns**: Array of subtask objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_subtasks_by_task(task_id)`**
- **Purpose**: Get incomplete subtasks for specific task
- **Parameters**: `task_id` (Integer)
- **Returns**: Array of subtask objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_subtasks_by_task(task_id, status)`**
- **Purpose**: Get subtasks for task, optionally filtered by status
- **Parameters**:
  - `task_id` (Integer)
  - `status` (String, optional)
- **Returns**: Array of subtask objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_subtasks_comprehensive(status, limit, date_range_created, date_range_updated, task_id, priority)`**
- **Purpose**: Advanced subtask search
- **Parameters**: All optional
- **Returns**: Array of filtered subtask objects
- **Classification**: is_tool=true, is_sub_helper=false

**`update_subtask(id, name, task_id, status, description, priority)`**
- **Purpose**: Update subtask metadata
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_subtask(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete subtask with item validation (same logic as delete_task)
- **Returns**: Error or success based on item status
- **Classification**: is_tool=true, is_sub_helper=false

### Sidequest Operations

**`add_sidequest(name, paused_task_id, paused_subtask_id, status, description, flow_ids, priority)`**
- **Purpose**: Add sidequest (urgent interruption)
- **Parameters**:
  - `paused_subtask_id` (Integer, optional) - If sidequest during subtask
  - `flow_ids` (Array) - JSON array of flow IDs
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_sidequests()`**
- **Purpose**: Get all non-completed sidequests
- **Returns**: Array of sidequest objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_sidequests_comprehensive(status, limit, date_range_created, date_range_updated, task_id, subtask_id, priority)`**
- **Purpose**: Advanced sidequest search
- **Parameters**: All optional
- **Returns**: Array of filtered sidequest objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_sidequest_flows(sidequest_id)`**
- **Purpose**: Get flow IDs for a sidequest
- **Parameters**: `sidequest_id` (Integer)
- **Returns**: Array of flow IDs
- **Classification**: is_tool=true, is_sub_helper=false

**`get_sidequest_files(sidequest_id)`**
- **Purpose**: Get all files related to sidequest via flows (orchestrator)
- **Parameters**: `sidequest_id` (Integer)
- **Returns**: Array of file objects
- **Note**: Chains get_sidequest_flows → get_file_ids_from_flows → get_from_project()
- **Classification**: is_tool=true, is_sub_helper=false

**`update_sidequest(id, name, paused_task_id, paused_subtask_id, status, description, flow_ids, priority)`**
- **Purpose**: Update sidequest metadata
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_sidequest(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete sidequest with item validation (same logic as delete_task)
- **Returns**: Error or success based on item status
- **Classification**: is_tool=true, is_sub_helper=false

### Item Operations

**`get_items_for_task(task_id, status)`**
- **Purpose**: Get items for task, optionally filtered by status
- **Parameters**:
  - `task_id` (Integer)
  - `status` (String, optional)
- **Returns**: Array of item objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_items_for_subtask(subtask_id, status)`**
- **Purpose**: Get items for subtask
- **Returns**: Array of item objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_items_for_sidequest(sidequest_id, status)`**
- **Purpose**: Get items for sidequest
- **Returns**: Array of item objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_incomplete_items(for_table, for_id)`**
- **Purpose**: Get incomplete items for any parent type
- **Parameters**:
  - `for_table` (String) - "tasks", "subtasks", "sidequests" (accepts singular)
  - `for_id` (Integer) - Parent ID
- **Returns**: Array of incomplete item objects
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_item(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete item with status validation
- **Returns**:
  - Error if status is "completed" or "in_progress"
  - Success if status is "pending"
- **Error Handling**: Cannot delete in-progress/completed items, only pending
- **Note**: Completed/in-progress items must stay, use notes for issues
- **Classification**: is_tool=true, is_sub_helper=false

---

## Notes

**`add_note(content, note_type, reference_table, reference_id, source, severity, directive_name)`**
- **Purpose**: Add note to project database
- **Parameters**:
  - `source` (String) - "ai" or "user" (default "ai")
  - `severity` (String) - "info", "warning", "error" (default "info")
  - `directive_name` (String, optional) - Directive context
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_notes_comprehensive(note_type, reference_table, reference_id, source, severity, directive_name)`**
- **Purpose**: Advanced note search with filters
- **Parameters**: All optional
- **Returns**: Array of filtered note objects
- **Classification**: is_tool=true, is_sub_helper=false

**`search_notes(search_string, reference_table, reference_id, source, severity, directive_name)`**
- **Purpose**: Search note content with optional filters
- **Parameters**:
  - `search_string` (String) - Required
  - Others optional
- **Returns**: Array of matching notes
- **Classification**: is_tool=true, is_sub_helper=false

**`update_note(id, content, note_type, reference_table, reference_id, source, severity, directive_name)`**
- **Purpose**: Update note metadata
- **Parameters**: All optional except id (*Can Be Null)
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_note(id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete note (discouraged)
- **Returns**:
  ```json
  {
    "success": true,
    "deleted_note": {original note data}
  }
  ```
- **Return Statements**: "WARNING: Note deletion removes important context. Deleted data returned for potential restoration. Consider if deletion was necessary."
- **Classification**: is_tool=false, is_sub_helper=false

---

## Context Helpers (Orchestrators)

**`get_work_context()`**
- **Purpose**: Get comprehensive work context for AI (complex orchestrator)
- **Returns**:
  ```json
  {
    "current_task": {task object},
    "current_flows": [{flow objects}],
    "related_files": [{file objects}],
    "active_sidequests": [{sidequest objects}]
  }
  ```
- **Note**: Single call provides complete context for current work
- **Classification**: is_tool=true, is_sub_helper=false

**`get_files_by_flow_context(flow_id)`**
- **Purpose**: Get files with embedded functions for a flow (orchestrator)
- **Parameters**: `flow_id` (Integer)
- **Returns**: Array of file objects with functions array embedded
- **Note**: Useful for understanding complete flow implementation
- **Classification**: is_tool=false, is_sub_helper=false

---

## User Settings Database (user_preferences.db)

**Location**: `<project-root>/.aifp-project/user_preferences.db`
**Access**: Read/Write
**Short Name**: `settings`

### Database Metadata

**`get_settings_tables()`**
- **Purpose**: List all tables in user settings database
- **Returns**: Array of table names
- **Classification**: is_tool=true, is_sub_helper=false

**`get_settings_fields(table)`**
- **Purpose**: Get field names and types for a specific table
- **Returns**: Array of field objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_settings_schema()`**
- **Purpose**: Get complete schema for user settings database
- **Returns**: Object mapping table names to field arrays
- **Classification**: is_tool=true, is_sub_helper=false

---

## Generic Settings Operations (Tier 2-4)

### Tier 3: ID-Based Retrieval

**`get_from_settings(table, id_array)`**
- **Purpose**: Get records by ID(s) - **EMPTY ARRAY NOT ALLOWED**
- **Parameters**:
  - `table` (String) - Table name
  - `id_array` (Array of Integers) - **MUST contain at least one ID**
- **Returns**: Array of records
- **Error Handling**: Return error if id_array is empty
- **Note**: Settings are mutable - prevent huge results
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 2: JSON-Based Filtering

**`get_from_settings_where(table, conditions, limit, orderby)`**
- **Purpose**: Flexible filtering with structured JSON conditions
- **Parameters**:
  - `table` (String)
  - `conditions` (Object) - Field-value pairs (AND logic)
  - `limit` (Integer, optional)
  - `orderby` (String, optional)
- **Returns**: Array of matching records
- **Examples**:
  - `get_from_settings_where("directive_preferences", {"directive_name": "project_file_write", "active": 1})`
  - `get_from_settings_where("tracking_settings", {"enabled": true})`
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 4: Raw SQL Queries

**`query_settings(table, query)`**
- **Purpose**: Execute complex SQL WHERE clause (advanced, rare use)
- **Parameters**: Table name and WHERE clause
- **Returns**: Array of matching rows
- **Note**: Use Tier 2 whenever possible
- **Classification**: is_tool=true, is_sub_helper=false

### Generic Write Operations

**`add_settings_entry(table, data)`**
- **Purpose**: Add entry to user settings database
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`update_settings_entry(table, id, data)`**
- **Purpose**: Update entry in user settings database
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_settings_entry(table, id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete entry from user settings
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

---

## Tier 1: High-Frequency Settings Helpers

### User Preferences (High-Frequency)

**`load_directive_preferences(directive_name)`**
- **Purpose**: Load all active preferences for a directive (high-frequency)
- **Parameters**: `directive_name` (String)
- **Returns**: Object mapping preference_key to preference_value
- **Note**: Only returns active preferences (active=1)
- **Note**: Zero cognitive load - called before every directive execution
- **Classification**: is_tool=true, is_sub_helper=false

**`add_directive_preference(directive_name, preference_key, preference_value, active)`**
- **Purpose**: Add/update user preference for directive
- **Parameters**:
  - `directive_name` (String)
  - `preference_key` (String)
  - `preference_value` (String)
  - `active` (Boolean, default true)
- **Returns**: `{"success": true}`
- **Note**: Atomic key-value structure (one preference per row)
- **Classification**: is_tool=true, is_sub_helper=false

**`get_user_setting(setting_key)`**
- **Purpose**: Get project-wide user setting (fairly frequent)
- **Parameters**: `setting_key` (String)
- **Returns**: Setting value or null
- **Note**: Simple lookup for global settings
- **Classification**: is_tool=true, is_sub_helper=false

### Preference Orchestrators

**`update_user_preferences(user_request, mapped_directive, preferences)`**
- **Purpose**: Map user request to directive preferences (orchestrator)
- **Parameters**:
  - `user_request` (String) - User's customization request
  - `mapped_directive` (String) - Directive name to apply to
  - `preferences` (Object) - Key-value pairs
- **Returns**: `{"success": true, "updated_count": integer}`
- **Note**: Used by user_preferences_update directive
- **Classification**: is_tool=true, is_sub_helper=false

**`apply_preferences_to_context(preferences)`**
- **Purpose**: Apply loaded preferences to execution context
- **Parameters**: `preferences` (Object) - Preference key-value pairs
- **Returns**: Modified context object
- **Note**: Used before directive execution
- **Classification**: is_tool=false, is_sub_helper=false

### Tracking Settings

**`get_tracking_settings()`**
- **Purpose**: Get all tracking feature flags
- **Returns**: Object with feature flags (all default false)
- **Classification**: is_tool=true, is_sub_helper=false

**`toggle_tracking_feature(feature_name, enabled)`**
- **Purpose**: Enable/disable tracking feature
- **Parameters**:
  - `feature_name` (String)
  - `enabled` (Boolean)
- **Returns**:
  ```json
  {
    "success": true,
    "feature": "feature_name",
    "enabled": boolean,
    "token_cost_warning": "Enabling will increase API costs"
  }
  ```
- **Note**: Shows cost warning when enabling
- **Classification**: is_tool=true, is_sub_helper=false

---

## User Custom Directives Database (user_directives.db)

**Location**: `<project-root>/.aifp-project/user_directives.db`
**Access**: Read/Write
**Short Name**: `user_custom`
**Note**: Only exists in automation projects (Use Case 2)

### Database Metadata

**`get_user_custom_tables()`**
- **Purpose**: List all tables in user custom directives database
- **Returns**: Array of table names
- **Classification**: is_tool=true, is_sub_helper=false

**`get_user_custom_fields(table)`**
- **Purpose**: Get field names and types for a specific table
- **Returns**: Array of field objects
- **Classification**: is_tool=true, is_sub_helper=false

**`get_user_custom_schema()`**
- **Purpose**: Get complete schema for user custom directives database
- **Returns**: Object mapping table names to field arrays
- **Classification**: is_tool=true, is_sub_helper=false

---

## Generic User Custom Operations (Tier 2-4)

### Tier 3: ID-Based Retrieval

**`get_from_user_custom(table, id_array)`**
- **Purpose**: Get records by ID(s) - **EMPTY ARRAY NOT ALLOWED**
- **Parameters**:
  - `table` (String)
  - `id_array` (Array of Integers) - **MUST contain at least one ID**
- **Returns**: Array of records
- **Error Handling**: Return error if id_array is empty
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 2: JSON-Based Filtering

**`get_from_user_custom_where(table, conditions, limit, orderby)`**
- **Purpose**: Flexible filtering with structured JSON conditions
- **Parameters**:
  - `table` (String)
  - `conditions` (Object) - Field-value pairs
  - `limit` (Integer, optional)
  - `orderby` (String, optional)
- **Returns**: Array of matching records
- **Examples**:
  - `get_from_user_custom_where("user_directives", {"status": "active", "validated": true})`
  - `get_from_user_custom_where("directive_executions", {"success": false}, 10, "executed_at DESC")`
- **Classification**: is_tool=true, is_sub_helper=false

### Tier 4: Raw SQL Queries

**`query_user_custom(table, query)`**
- **Purpose**: Execute complex SQL WHERE clause (advanced, rare use)
- **Parameters**: Table name and WHERE clause
- **Returns**: Array of matching rows
- **Classification**: is_tool=true, is_sub_helper=false

### Generic Write Operations

**`add_user_custom_entry(table, data)`**
- **Purpose**: Add entry to user custom directives database
- **Returns**: `{"success": true, "id": new_id}`
- **Classification**: is_tool=true, is_sub_helper=false

**`update_user_custom_entry(table, id, data)`**
- **Purpose**: Update entry in user custom directives database
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

**`delete_user_custom_entry(table, id, note_reason, note_severity, note_source, note_type)`**
- **Purpose**: Delete entry from user custom directives
- **Returns**: `{"success": true}`
- **Classification**: is_tool=true, is_sub_helper=false

---

## User Directive Operations (Specialized Orchestrators)

**`parse_directive_file(file_path)`**
- **Purpose**: Parse YAML/JSON/TXT directive file (orchestrator)
- **Parameters**: `file_path` (String) - Path to user directive file
- **Returns**:
  ```json
  {
    "success": true,
    "directives": [{parsed directives}],
    "ambiguities": [{questions for validation}],
    "source_file_id": integer
  }
  ```
- **Note**: Tracks file reference in source_files table
- **Classification**: is_tool=true, is_sub_helper=false

**`validate_directive_config(directive_id)`**
- **Purpose**: Interactive validation for parsed directive (orchestrator)
- **Parameters**: `directive_id` (Integer)
- **Returns**:
  ```json
  {
    "success": true,
    "validation_status": "validated",
    "questions_answered": integer
  }
  ```
- **Note**: Updates validated config in user_directives table
- **Classification**: is_tool=true, is_sub_helper=false

**`generate_handler_code(directive_id)`**
- **Purpose**: Generate FP-compliant implementation code (orchestrator)
- **Parameters**: `directive_id` (Integer)
- **Returns**:
  ```json
  {
    "success": true,
    "generated_files": [{file paths}],
    "test_files": [{test file paths}],
    "dependencies": [{required packages}]
  }
  ```
- **Note**: Creates src/ files, updates project.db, generates tests
- **Classification**: is_tool=true, is_sub_helper=false

**`deploy_background_service(directive_id)`**
- **Purpose**: Activate directive for real-time execution (orchestrator)
- **Parameters**: `directive_id` (Integer)
- **Returns**:
  ```json
  {
    "success": true,
    "service_status": "active",
    "next_execution": "timestamp"
  }
  ```
- **Note**: Starts scheduler/event handler
- **Classification**: is_tool=true, is_sub_helper=false

**`get_user_directive_status(directive_id)`**
- **Purpose**: Get status of user directive(s) (orchestrator)
- **Parameters**: `directive_id` (Integer, optional - returns all if omitted)
- **Returns**: Directive status object(s) with execution stats
- **Classification**: is_tool=true, is_sub_helper=false

**`monitor_directive_execution(directive_id)`**
- **Purpose**: Get execution statistics and errors (orchestrator)
- **Parameters**: `directive_id` (Integer)
- **Returns**:
  ```json
  {
    "success": true,
    "executions_count": integer,
    "last_execution": "timestamp",
    "recent_errors": [{error objects}],
    "log_file_paths": [{log paths}]
  }
  ```
- **Note**: Detailed logs in .aifp-project/logs/, not database
- **Classification**: is_tool=true, is_sub_helper=false

---

## Git Operations

**Target Database**: project.db
**Purpose**: Version control integration and collaboration

### Git Status & Detection

**`get_current_commit_hash(project_root)`**
- **Purpose**: Get current Git HEAD commit hash
- **Parameters**: `project_root` (String) - Project directory path
- **Returns**: String commit hash or null if Git unavailable
- **Error Handling**: Return null if not Git repository
- **Used By**: git_init, git_sync_state, git_detect_external_changes
- **Classification**: is_tool=false, is_sub_helper=false

**`get_current_branch(project_root)`**
- **Purpose**: Get current Git branch name
- **Parameters**: `project_root` (String)
- **Returns**: String branch name or null
- **Error Handling**: Return null if Git unavailable
- **Used By**: git_create_branch, git_sync_state, status reporting
- **Classification**: is_tool=false, is_sub_helper=false

**`get_git_status(project_root)`**
- **Purpose**: Get comprehensive Git state snapshot (orchestrator)
- **Parameters**: `project_root` (String)
- **Returns**:
  ```json
  {
    "git_available": boolean,
    "current_branch": string,
    "commit_hash": string,
    "uncommitted_changes": boolean,
    "external_changes_detected": boolean
  }
  ```
- **Error Handling**: Returns git_available=false if Git unavailable
- **Used By**: git_sync_state, aifp_status
- **Classification**: is_tool=true, is_sub_helper=false

**`detect_external_changes(project_root)`**
- **Purpose**: Compare current Git HEAD with project.last_known_git_hash
- **Parameters**: `project_root` (String)
- **Returns**:
  ```json
  {
    "changes_detected": boolean,
    "previous_hash": string,
    "current_hash": string,
    "files_changed": [array of file paths]
  }
  ```
- **Error Handling**: Return empty changes if Git unavailable
- **Used By**: git_detect_external_changes, aifp_status
- **Classification**: is_tool=true, is_sub_helper=false

### Branch Management

**`create_user_branch(user, purpose, project_root)`**
- **Purpose**: Create work branch following aifp-{user}-{number} convention
- **Parameters**:
  - `user` (String) - Username
  - `purpose` (String) - Branch purpose description
  - `project_root` (String)
- **Returns**:
  ```json
  {
    "success": boolean,
    "branch_name": "aifp-user-001",
    "branch_number": integer
  }
  ```
- **Error Handling**: Auto-increment number if branch exists
- **Used By**: git_create_branch directive
- **Classification**: is_tool=true, is_sub_helper=false

**`get_user_name_for_branch()`**
- **Purpose**: Detect username from git config/environment/system
- **Parameters**: None
- **Returns**: String username (never null)
- **Error Handling**: Fallback to "user" if all detection fails
- **Note**: Checks git config, then environment, then system user
- **Used By**: git_create_branch directive
- **Classification**: is_tool=false, is_sub_helper=false

**`list_active_branches()`**
- **Purpose**: List all AIFP work branches from work_branches table
- **Parameters**: None
- **Returns**: Array of branch objects with name, created_at, purpose
- **Error Handling**: Return empty array if table doesn't exist
- **Used By**: Status reporting, collaboration coordination
- **Classification**: is_tool=true, is_sub_helper=false

### Conflict Detection & Resolution (Orchestrators)

**`detect_conflicts_before_merge(source_branch, project_root)`**
- **Purpose**: FP-powered conflict analysis before merging (complex orchestrator)
- **Parameters**:
  - `source_branch` (String)
  - `project_root` (String)
- **Returns**:
  ```json
  {
    "conflicts_detected": boolean,
    "file_conflicts": [array],
    "function_conflicts": [array with purity/test data],
    "confidence_scores": object
  }
  ```
- **Error Handling**: Fall back to file-level conflicts if DB query fails
- **Note**: Queries project.db from both branches for FP analysis
- **Used By**: git_detect_conflicts, git_merge_branch
- **Classification**: is_tool=true, is_sub_helper=false

**`merge_with_fp_intelligence(source_branch, project_root)`**
- **Purpose**: Git merge with FP-powered conflict auto-resolution (complex orchestrator)
- **Parameters**:
  - `source_branch` (String)
  - `project_root` (String)
- **Returns**:
  ```json
  {
    "success": boolean,
    "auto_resolved_count": integer,
    "manual_conflicts": [array],
    "merge_aborted": boolean
  }
  ```
- **Error Handling**: Abort merge (git merge --abort) if unresolvable
- **Note**: Auto-resolves conflicts >0.8 confidence using purity rules
- **Used By**: git_merge_branch directive
- **Classification**: is_tool=true, is_sub_helper=false

### Git State Synchronization

**`sync_git_state(project_root)`**
- **Purpose**: Update project.last_known_git_hash with current Git HEAD
- **Parameters**: `project_root` (String)
- **Returns**:
  ```json
  {
    "success": boolean,
    "updated_hash": string,
    "previous_hash": string
  }
  ```
- **Error Handling**: Log warning if Git unavailable, continue with cached
- **Note**: Called after commits and during session boot
- **Used By**: git_sync_state directive, aifp_status
- **Classification**: is_tool=true, is_sub_helper=false

**`project_update_git_status()`**
- **Purpose**: Update last_known_git_hash and last_git_sync in project table
- **Parameters**: None (gets git data automatically)
- **Returns**: `{"success": true, "hash": string, "sync_time": timestamp}`
- **Note**: Convenience wrapper for common sync operation
- **Classification**: is_tool=false, is_sub_helper=false

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
- ~70 Directive Helpers (is_tool=false, is_sub_helper=false) - Called via directives
- ~5 Sub-Helpers (is_sub_helper=true) - Internal only

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

**End of Consolidated Helper Functions Reference v2.1**

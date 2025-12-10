# Project Database Helper Functions

**Database**: project.db
**Location**: `<project-root>/.aifp-project/project.db`
**Access**: Read/Write
**Short Name**: `project`

For the master index and design philosophy, see [helpers-consolidated-index.md](helpers-consolidated-index.md)

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

**End of Project Database Helper Functions**

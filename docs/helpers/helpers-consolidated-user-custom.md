# User Custom Directives Database Helper Functions

**Database**: user_directives.db
**Location**: `<project-root>/.aifp-project/user_directives.db`
**Access**: Read/Write
**Short Name**: `user_custom`
**Note**: Only exists in automation projects (Use Case 2)

For the master index and design philosophy, see [helpers-consolidated-index.md](helpers-consolidated-index.md)

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

**End of User Custom Directives Database Helper Functions**

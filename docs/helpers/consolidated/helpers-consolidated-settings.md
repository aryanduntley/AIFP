# User Settings Database Helper Functions

**Database**: user_preferences.db
**Location**: `<project-root>/.aifp-project/user_preferences.db`
**Access**: Read/Write
**Short Name**: `settings`

For the master index and design philosophy, see [helpers-consolidated-index.md](helpers-consolidated-index.md)

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

**`get_settings_json_parameters(table)`**
- **Purpose**: Get available fields for table to use with generic add/update operations
- **Parameters**: `table` (String) - Table name
- **Returns**: Object with fields array, examples (similar to `get_project_json_parameters()`)
- **Note**: Use with `add_settings_entry()` or `update_settings_entry()` for tables without specialized functions. Only include fields being set/updated in JSON.
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

**End of User Settings Database Helper Functions**

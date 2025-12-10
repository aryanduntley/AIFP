# Core Database Helper Functions

**Database**: aifp_core.db
**Location**: MCP server installation directory
**Access**: Read-only
**Short Name**: `core`

For the master index and design philosophy, see [helpers-consolidated-index.md](helpers-consolidated-index.md)

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

**End of Core Database Helper Functions**

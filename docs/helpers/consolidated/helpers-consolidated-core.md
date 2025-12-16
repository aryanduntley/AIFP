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

### Intent Keyword Search (Normalized Schema v1.9)

**Schema Note**: As of v1.9, intent keywords are normalized with a master `intent_keywords` table and `directives_intent_keywords` linking table. This provides consistency with the `categories` table structure, better data integrity, and improved query performance for keyword operations.

**`find_directive_by_intent(user_request, threshold)`**
- **Purpose**: Map user intent to directives using NLP/keyword matching
- **Parameters**:
  - `user_request` (String)
  - `threshold` (Float, default 0.7) - Confidence threshold
- **Returns**: Array of matching directives with confidence scores
- **Note**: High-level NLP search that uses AI reasoning to determine intent keywords, then calls `find_directives_by_intent_keyword()` internally
- **Classification**: is_tool=true, is_sub_helper=false

**`find_directives_by_intent_keyword(keywords, match_mode)`**
- **Purpose**: Find directive IDs matching one or more intent keywords (direct keyword lookup)
- **Parameters**:
  - `keywords` (String | Array) - Single keyword string or array of keywords
  - `match_mode` (String, optional, default="any") - "any" for OR logic, "all" for AND logic
- **Returns**: Array of directive IDs
- **Database**: Queries `directives_intent_keywords` joined with `intent_keywords` table
- **SQL Example**:
  ```sql
  SELECT DISTINCT dik.directive_id
  FROM directives_intent_keywords dik
  JOIN intent_keywords ik ON dik.keyword_id = ik.id
  WHERE ik.keyword IN (...)
  ```
- **Examples**:
  - `find_directives_by_intent_keyword("authentication")` → [15, 23, 42]
  - `find_directives_by_intent_keyword(["purity", "immutability"], "all")` → [5, 12]
- **Note**: Low-level keyword search. For NLP-based intent mapping, use `find_directive_by_intent()`. This is a directive-callable helper (not MCP tool)
- **Classification**: is_tool=false, is_sub_helper=false

**`get_directives_with_intent_keywords(keywords, match_mode, include_keyword_matches)`**
- **Purpose**: Search directives by intent keywords and return full directive objects
- **Parameters**:
  - `keywords` (String | Array) - Single keyword or array of keywords
  - `match_mode` (String, optional, default="any") - "any" for OR logic, "all" for AND logic
  - `include_keyword_matches` (Boolean, optional, default=true) - Include which keywords matched
- **Returns**: Array of directive objects with `matched_keywords` field
- **Example Return**:
  ```json
  [
    {
      "id": 15,
      "name": "fp_authentication",
      "type": "fp",
      "description": "...",
      "matched_keywords": ["authentication", "security"]
    }
  ]
  ```
- **Helpers Called**: `find_directives_by_intent_keyword()`, `get_from_core()`
- **Note**: Orchestrator that combines keyword search with full directive data retrieval
- **Classification**: is_tool=true, is_sub_helper=false

**`add_directive_intent_keyword(directive_id, keyword)`**
- **Purpose**: Add an intent keyword to a directive
- **Parameters**:
  - `directive_id` (Integer)
  - `keyword` (String)
- **Returns**: Success boolean
- **Database**:
  1. INSERT OR IGNORE into `intent_keywords` (creates keyword if new)
  2. INSERT into `directives_intent_keywords` (links directive to keyword)
- **SQL Example**:
  ```sql
  -- Step 1: Ensure keyword exists
  INSERT OR IGNORE INTO intent_keywords (keyword) VALUES (?);
  -- Step 2: Get keyword_id
  SELECT id FROM intent_keywords WHERE keyword = ?;
  -- Step 3: Link to directive
  INSERT INTO directives_intent_keywords (directive_id, keyword_id) VALUES (?, ?);
  ```
- **Note**: Duplicate keywords for the same directive are prevented by UNIQUE constraint
- **Classification**: is_tool=false, is_sub_helper=false

**`remove_directive_intent_keyword(directive_id, keyword)`**
- **Purpose**: Remove an intent keyword from a directive
- **Parameters**:
  - `directive_id` (Integer)
  - `keyword` (String)
- **Returns**: Success boolean
- **Database**: Deletes from `directives_intent_keywords` table (keyword remains in intent_keywords)
- **SQL Example**:
  ```sql
  DELETE FROM directives_intent_keywords
  WHERE directive_id = ? AND keyword_id = (
      SELECT id FROM intent_keywords WHERE keyword = ?
  );
  ```
- **Note**: Does not delete keyword from intent_keywords table (preserves keyword for reuse)
- **Classification**: is_tool=false, is_sub_helper=false

**`get_directive_keywords(directive_id)`**
- **Purpose**: Get all intent keywords for a specific directive
- **Parameters**: `directive_id` (Integer)
- **Returns**: Array of keyword strings
- **Database**: Queries `directives_intent_keywords` joined with `intent_keywords`
- **SQL Example**:
  ```sql
  SELECT ik.keyword
  FROM directives_intent_keywords dik
  JOIN intent_keywords ik ON dik.keyword_id = ik.id
  WHERE dik.directive_id = ?
  ORDER BY ik.keyword;
  ```
- **Classification**: is_tool=true, is_sub_helper=false

**`get_all_directive_keywords()`**
- **Purpose**: Get list of all unique intent keywords available for searching (simple list)
- **Returns**: Array of keyword strings, sorted alphabetically
- **Example Return**: `["authentication", "purity", "task", "security", "immutability", "git", ...]`
- **Database**: Queries `intent_keywords` table directly (much simpler than old approach!)
- **SQL Example**:
  ```sql
  SELECT keyword FROM intent_keywords ORDER BY keyword;
  ```
- **Note**: Use this when AI needs to browse available keywords and decide which to search for. For keyword usage statistics, use `get_all_intent_keywords_with_counts()`
- **Classification**: is_tool=true, is_sub_helper=false

**`get_all_intent_keywords_with_counts()`**
- **Purpose**: Get all unique intent keywords with usage counts for analytics
- **Returns**: Array of objects with `keyword` and `usage_count` fields, sorted by usage (most used first)
- **SQL Example**:
  ```sql
  SELECT ik.keyword, COUNT(dik.directive_id) as usage_count
  FROM intent_keywords ik
  LEFT JOIN directives_intent_keywords dik ON ik.id = dik.keyword_id
  GROUP BY ik.id, ik.keyword
  ORDER BY usage_count DESC, ik.keyword;
  ```
- **Example Return**:
  ```json
  [
    {"keyword": "task", "usage_count": 15},
    {"keyword": "purity", "usage_count": 12},
    {"keyword": "authentication", "usage_count": 8}
  ]
  ```
- **Note**: Useful for analytics, identifying popular keywords, and suggesting common searches
- **Classification**: is_tool=true, is_sub_helper=false

### Directive Navigation (Status-Driven Decision Tree)

**See**: docs/DIRECTIVE_NAVIGATION_SYSTEM.md for complete architecture documentation

**Note**: `aifp_status()` orchestrator is documented in [helpers-consolidated-orchestrators.md](helpers-consolidated-orchestrators.md#aifp_status) - it's the central status orchestrator that feeds the navigation system below.

**`get_next_directives_from_status(from_directive, status_object)`**
- **Purpose**: Get all possible next directives with condition evaluation
- **Parameters**:
  - `from_directive` (String) - Usually 'aifp_status'
  - `status_object` (Object) - Status returned from aifp_status()
- **Returns**: Array of objects:
  ```json
  [
    {
      "to_directive": "string",
      "flow_type": "status_branch|conditional|completion_loop|error",
      "condition_key": "string",
      "condition_value": "string",
      "condition_description": "string",
      "priority": number,
      "matches": true|false,
      "description": "string"
    }
  ]
  ```
- **Note**: Returns both matching and non-matching for transparency
- **Classification**: is_tool=true, is_sub_helper=false

**`get_matching_next_directives(from_directive, status_object)`**
- **Purpose**: Get ONLY directives whose conditions match current state
- **Parameters**: Same as `get_next_directives_from_status()`
- **Returns**: Filtered array with only `matches: true`
- **Note**: Convenience wrapper for most common use case
- **Classification**: is_tool=true, is_sub_helper=false

**`get_completion_loop_target(from_directive)`**
- **Purpose**: Get where to loop back after completing directive
- **Parameters**: `from_directive` (String)
- **Returns**: Single directive name (usually 'aifp_status')
- **SQL**:
  ```sql
  SELECT to_directive FROM directive_flow
  WHERE from_directive = ? AND flow_type = 'completion_loop'
  LIMIT 1;
  ```
- **Note**: Work directives use this to determine where to return after completion
- **Classification**: is_tool=true, is_sub_helper=false

**`get_conditional_work_paths(from_directive, work_context)`**
- **Purpose**: Get conditional next steps during work execution
- **Parameters**:
  - `from_directive` (String) - e.g., 'task_item_work'
  - `work_context` (Object) - Current item/task context
- **Returns**: Array of conditional work directives with descriptions and priorities
- **SQL**:
  ```sql
  SELECT to_directive, condition_description, priority
  FROM directive_flow
  WHERE from_directive = ? AND flow_type = 'conditional'
  ORDER BY priority DESC;
  ```
- **Note**: Used when work items have different requirements (file creation, function creation, etc.)
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

**`get_directives_by_type(type, include_md_content)`**
- **Purpose**: Get all directives filtered by type (orchestration vs reference)
- **Parameters**:
  - `type` (String) - One of: 'fp', 'project', 'git', 'user_system', 'user_preference'
  - `include_md_content` (Boolean, default false) - Include full MD file content
- **Returns**: Array of directive objects filtered by type
- **Use Cases**:
  - `get_directives_by_type('project')` - Get all project orchestration directives
  - `get_directives_by_type('fp')` - Get FP reference directives for clarification
  - `get_directives_by_type('fp', true)` - Get FP directives with full MD documentation
- **Classification**: is_tool=true, is_sub_helper=false
- **Note**: Key for separating orchestration queries from FP reference queries. See DIRECTIVE_ARCHITECTURE.md for usage patterns.

---

**End of Core Database Helper Functions**

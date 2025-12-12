# Intent Keywords Refactor - Complete

**Date**: 2025-12-11
**Purpose**: Replace JSON field with normalized table for efficient keyword searching

---

## Summary

Refactored the intent keywords system from a JSON field (`intent_keywords_json`) in the directives table to a separate normalized table (`directives_intent_keywords`) with proper indexing.

---

## Changes Made

### 1. Database Schema (`src/aifp/database/schemas/aifp_core.sql`)

**Removed from directives table**:
```sql
intent_keywords_json TEXT,  -- Removed
```

**Added new table**:
```sql
CREATE TABLE IF NOT EXISTS directives_intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    UNIQUE(directive_id, keyword),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE
);

-- Critical indexes for fast searching
CREATE INDEX IF NOT EXISTS idx_intent_keyword ON directives_intent_keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_directive_keywords ON directives_intent_keywords(directive_id);
```

**Version Update**: 1.6 → 1.7

---

### 2. Helper Functions Added (`docs/helpers/helpers-consolidated-core.md`)

Added 7 new helper functions:

#### Core Search Functions

**`find_directives_by_intent_keyword(keywords, match_mode)`**
- **Type**: Tier 1 helper (is_tool=false, is_sub_helper=false)
- **Purpose**: Direct keyword lookup, returns directive IDs
- **Parameters**:
  - `keywords`: String | Array - single or multiple keywords
  - `match_mode`: "any" (OR) or "all" (AND)
- **Returns**: Array of directive IDs

**`get_directives_with_intent_keywords(keywords, match_mode, include_keyword_matches)`**
- **Type**: MCP tool (is_tool=true)
- **Purpose**: Orchestrator - returns full directive objects with matched keywords
- **Calls**: `find_directives_by_intent_keyword()`, `get_from_core()`
- **Returns**: Array of directive objects with `matched_keywords` field

#### Keyword Management

**`add_directive_intent_keyword(directive_id, keyword)`**
- Add keyword to directive
- **Type**: Helper (is_tool=false)

**`remove_directive_intent_keyword(directive_id, keyword)`**
- Remove keyword from directive
- **Type**: Helper (is_tool=false)

**`get_directive_keywords(directive_id)`**
- Get all keywords for a directive
- **Type**: MCP tool (is_tool=true)

#### Keyword Discovery

**`get_all_directive_keywords()`**
- **Type**: MCP tool (is_tool=true)
- **Purpose**: Get simple list of all keywords (for AI to browse and select)
- **Returns**: Array of keyword strings, sorted alphabetically
- **Example**: `["authentication", "git", "immutability", "purity", "security", "task", ...]`

**`get_all_intent_keywords_with_counts()`**
- **Type**: MCP tool (is_tool=true)
- **Purpose**: Get keywords with usage statistics
- **Returns**: Array of `{keyword, usage_count}` objects, sorted by usage
- **Example**: `[{"keyword": "task", "usage_count": 15}, {"keyword": "purity", "usage_count": 12}, ...]`

---

### 3. Updated Existing Function

**`find_directive_by_intent(user_request, threshold)`**
- Updated note: Now calls `find_directives_by_intent_keyword()` internally
- Clarified as high-level NLP search vs low-level keyword lookup

---

### 4. Documentation Updates

**Updated files**:
- `docs/helpers/generic-tools-mcp.md` - Changed "intent_keywords_json field" → "directives_intent_keywords table"
- `docs/helpers/info-helpers-core.txt` - Removed intent_keywords_json from schema, added directives_intent_keywords table description

---

## Benefits

### Performance
✅ **Indexed searches**: Direct keyword lookups are fast (indexed on keyword column)
✅ **No JSON parsing**: Simple SQL queries instead of JSON functions
✅ **Efficient OR/AND**: Native SQL operators vs complex JSON logic

### Maintainability
✅ **Normalized data**: Each keyword is a row, no duplication
✅ **Easy analytics**: Count keyword usage, find popular keywords
✅ **Simple queries**: Standard SQL instead of JSON_EACH()

### Flexibility
✅ **Single or multiple keywords**: Supports both use cases
✅ **OR/AND logic**: match_mode parameter for different search strategies
✅ **Discovery**: AI can browse all available keywords before searching

---

## API Design

### For AI to Browse Keywords
```python
# Get simple list to review
keywords = get_all_directive_keywords()
# Returns: ["authentication", "git", "purity", "security", "task", ...]

# AI picks keywords and searches
directives = get_directives_with_intent_keywords(["purity", "immutability"], "all")
```

### For Direct Search
```python
# Single keyword
ids = find_directives_by_intent_keyword("authentication")

# Multiple keywords (OR logic)
ids = find_directives_by_intent_keyword(["task", "project"], "any")

# Multiple keywords (AND logic) - directives must have ALL keywords
ids = find_directives_by_intent_keyword(["purity", "testing"], "all")
```

### For Full Objects
```python
# Get full directive objects with matched keywords
directives = get_directives_with_intent_keywords(
    keywords=["security", "authentication"],
    match_mode="any",
    include_keyword_matches=True
)

# Returns:
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

---

## SQL Queries

### Search by Keywords (OR logic)
```sql
SELECT DISTINCT directive_id
FROM directives_intent_keywords
WHERE keyword IN ('authentication', 'security')
ORDER BY directive_id;
```

### Search by Keywords (AND logic)
```sql
SELECT directive_id
FROM directives_intent_keywords
WHERE keyword IN ('purity', 'immutability')
GROUP BY directive_id
HAVING COUNT(DISTINCT keyword) = 2
ORDER BY directive_id;
```

### Get All Keywords (sorted)
```sql
SELECT DISTINCT keyword
FROM directives_intent_keywords
ORDER BY keyword;
```

### Get Keywords with Counts
```sql
SELECT keyword, COUNT(*) as usage_count
FROM directives_intent_keywords
GROUP BY keyword
ORDER BY usage_count DESC, keyword;
```

---

## Migration Notes

**No migration needed** - Schema is in initial development phase. When populating:

1. Parse existing directive definitions
2. Extract intent keywords
3. Insert into `directives_intent_keywords` table:
   ```sql
   INSERT INTO directives_intent_keywords (directive_id, keyword)
   VALUES (?, ?);
   ```

---

## Function Classification Summary

**MCP Tools** (is_tool=true) - AI can call directly:
- `get_directives_with_intent_keywords()` - Main search function
- `get_directive_keywords()` - Get keywords for one directive
- `get_all_directive_keywords()` - Browse all keywords
- `get_all_intent_keywords_with_counts()` - Analytics

**Directive Helpers** (is_tool=false, is_sub_helper=false) - Called via directives:
- `find_directives_by_intent_keyword()` - Core search logic
- `add_directive_intent_keyword()` - Add keyword
- `remove_directive_intent_keyword()` - Remove keyword

---

## Status

✅ **Schema updated** - intent_keywords_json removed, directives_intent_keywords table added
✅ **Indexes created** - Fast keyword and directive lookups
✅ **7 helpers added** - Complete keyword search and management API
✅ **Documentation updated** - All references to old field removed
✅ **Version bumped** - 1.6 → 1.7

**Ready for implementation!**

---

**Completed By**: Claude (Sonnet 4.5)
**Date**: 2025-12-11

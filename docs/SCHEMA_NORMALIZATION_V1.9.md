# Schema Normalization v1.9: Intent Keywords

**Date**: 2025-01-15
**Schema Version**: 1.8 → 1.9
**Type**: Normalization (non-breaking in dev, no production data)

---

## Summary

Normalized the intent keywords schema to match the existing categories pattern. Both now use a master table with a linking table for many-to-many relationships.

---

## What Changed

### Before (v1.8) - Denormalized

```sql
-- Single table with keyword stored as TEXT
CREATE TABLE IF NOT EXISTS directives_intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,  -- Keyword stored directly
    UNIQUE(directive_id, keyword),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE
);
```

### After (v1.9) - Normalized

```sql
-- Master keywords table
CREATE TABLE IF NOT EXISTS intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE
);

-- Linking table with keyword_id reference
CREATE TABLE IF NOT EXISTS directives_intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,  -- References intent_keywords.id
    UNIQUE(directive_id, keyword_id),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (keyword_id) REFERENCES intent_keywords(id) ON DELETE CASCADE
);
```

---

## Why This Change?

### 1. Consistency

**Before**: Categories were normalized, keywords were not
- `categories` + `directive_categories` (normalized)
- `directives_intent_keywords` only (denormalized)

**After**: Both use the same pattern
- `categories` + `directive_categories`
- `intent_keywords` + `directives_intent_keywords`

### 2. Data Integrity

**Prevents typos and inconsistencies:**
- Can't have both "authentication" and "authenticaton"
- Database enforces valid keywords via foreign key
- Single source of truth for keyword spellings

### 3. Better Queries

**Get all keywords:**

Before:
```sql
-- Must scan all rows and deduplicate
SELECT DISTINCT keyword
FROM directives_intent_keywords
ORDER BY keyword;
```

After:
```sql
-- Direct query, much faster
SELECT keyword
FROM intent_keywords
ORDER BY keyword;
```

**Bulk keyword operations:**
- Renaming "task_management" → "project_management": 1 UPDATE vs N UPDATEs
- Adding keyword description: Add column to `intent_keywords`, not in every link

### 4. Storage Efficiency

- `keyword_id` (4 bytes) vs keyword string (10-20+ bytes typically)
- With 100 directives × 5 keywords = 500 rows
- Saves ~8KB per keyword (approximate, varies by keyword length)
- Integer joins are faster than string comparisons

### 5. Future Extensibility

Can now add keyword metadata without schema changes:

```sql
ALTER TABLE intent_keywords ADD COLUMN description TEXT;
ALTER TABLE intent_keywords ADD COLUMN aliases JSON;
ALTER TABLE intent_keywords ADD COLUMN deprecated BOOLEAN DEFAULT 0;
```

All existing links remain valid.

---

## Helper Function Changes

### Query Functions

Functions that search by keyword now require a JOIN:

**Old (v1.8)**:
```sql
SELECT directive_id FROM directives_intent_keywords
WHERE keyword = ?;
```

**New (v1.9)**:
```sql
SELECT dik.directive_id
FROM directives_intent_keywords dik
JOIN intent_keywords ik ON dik.keyword_id = ik.id
WHERE ik.keyword = ?;
```

### Add Keyword Function

`add_directive_intent_keyword()` now requires two steps:

**Old (v1.8)**:
```sql
INSERT INTO directives_intent_keywords (directive_id, keyword)
VALUES (?, ?);
```

**New (v1.9)**:
```sql
-- Step 1: Ensure keyword exists
INSERT OR IGNORE INTO intent_keywords (keyword) VALUES (?);

-- Step 2: Get keyword_id
SELECT id FROM intent_keywords WHERE keyword = ?;

-- Step 3: Link to directive
INSERT INTO directives_intent_keywords (directive_id, keyword_id)
VALUES (?, ?);
```

### Get All Keywords Function

`get_all_directive_keywords()` is now much simpler:

**Old (v1.8)**:
```sql
SELECT DISTINCT keyword FROM directives_intent_keywords
ORDER BY keyword;
```

**New (v1.9)**:
```sql
SELECT keyword FROM intent_keywords
ORDER BY keyword;
```

---

## Updated Helper Functions

The following functions in `docs/helpers/helpers-consolidated-core.md` were updated:

1. **`find_directives_by_intent_keyword()`** - Added JOIN logic
2. **`add_directive_intent_keyword()`** - Multi-step insert process
3. **`remove_directive_intent_keyword()`** - Subquery for keyword_id
4. **`get_directive_keywords()`** - Added JOIN
5. **`get_all_directive_keywords()`** - Simplified query
6. **`get_all_intent_keywords_with_counts()`** - Added LEFT JOIN with GROUP BY

All include SQL examples showing the new query patterns.

---

## Indexes

### Added Indexes

```sql
-- For keyword lookups
CREATE INDEX IF NOT EXISTS idx_intent_keyword_name ON intent_keywords(keyword);

-- For directive -> keywords
CREATE INDEX IF NOT EXISTS idx_directive_keywords ON directives_intent_keywords(directive_id);

-- For keyword -> directives (reverse lookup)
CREATE INDEX IF NOT EXISTS idx_keyword_directives ON directives_intent_keywords(keyword_id);
```

### Removed Indexes

```sql
-- Old index on TEXT column (no longer needed)
-- CREATE INDEX IF NOT EXISTS idx_intent_keyword ON directives_intent_keywords(keyword);
```

---

## Migration (Dev Only)

Since this is initial development with no production data:

1. **No migration script needed** - just use new schema
2. Existing dev data can be:
   - Dropped and recreated, OR
   - Manually migrated with:
     ```sql
     -- Extract unique keywords
     INSERT INTO intent_keywords (keyword)
     SELECT DISTINCT keyword FROM directives_intent_keywords_old;

     -- Recreate links with keyword_id
     INSERT INTO directives_intent_keywords (directive_id, keyword_id)
     SELECT dik_old.directive_id, ik.id
     FROM directives_intent_keywords_old dik_old
     JOIN intent_keywords ik ON dik_old.keyword = ik.keyword;
     ```

---

## Benefits Summary

| Aspect | Before (Denormalized) | After (Normalized) | Improvement |
|--------|----------------------|-------------------|-------------|
| **Schema Consistency** | Inconsistent (categories normalized, keywords not) | Consistent pattern for both | ✅ Easier to understand |
| **Data Integrity** | No typo prevention | Foreign key enforces valid keywords | ✅ Better quality |
| **Get all keywords** | DISTINCT scan | Direct query | ✅ Faster |
| **Storage per link** | 10-20+ bytes | 4 bytes | ✅ ~60% reduction |
| **Bulk keyword rename** | N updates | 1 update | ✅ Much faster |
| **Add keyword metadata** | Schema change needed | Just add column to keywords table | ✅ Future-proof |
| **Query complexity** | Simpler (no join) | Slightly more complex (join) | ⚠️ Minor trade-off |

---

## References

- **Schema File**: `src/aifp/database/schemas/aifp_core.sql` (v1.9)
- **Helper Functions**: `docs/helpers/helpers-consolidated-core.md` (Intent Keyword Search section)
- **Related Change**: Follows same pattern as v1.8 directive_flow normalization

---

## Related Schema Patterns

This completes the normalization of the core schema:

1. **Directives** → Main entity table ✅
2. **Categories** → Normalized (master + linking) ✅
3. **Intent Keywords** → Normalized (master + linking) ✅ NEW
4. **Directive Flow** → Direct edge relationships ✅
5. **Helper Functions** → References by name ✅

All major entity relationships now follow consistent, normalized patterns.

---

**Last Updated**: 2025-01-15
**Schema Version**: 1.9

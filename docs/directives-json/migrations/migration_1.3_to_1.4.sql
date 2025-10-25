-- Migration from v1.3 to v1.4
-- Date: 2025-10-25
-- Description: Add support for user preferences, user directives, and git integration

-- ==============================================
-- This migration adds no schema changes
-- (v1.4 is a content update, not schema update)
-- ==============================================

-- This migration file serves as a template for future schema changes.
-- When actual schema changes are needed, follow this structure:

-- Example 1: Add new column to existing table
-- ALTER TABLE directives ADD COLUMN new_column TEXT;

-- Example 2: Create new table
-- CREATE TABLE IF NOT EXISTS new_table (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     name TEXT NOT NULL,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP
-- );

-- Example 3: Create index for performance
-- CREATE INDEX IF NOT EXISTS idx_directives_new_column ON directives(new_column);

-- Example 4: Update existing data (use cautiously)
-- UPDATE directives SET new_column = 'default_value' WHERE new_column IS NULL;

-- ==============================================
-- IMPORTANT NOTES
-- ==============================================
-- 1. Always use "IF NOT EXISTS" or "IF EXISTS" for idempotency
-- 2. Test migrations on a copy of the database first
-- 3. Migrations should be additive (add columns, not remove)
-- 4. For destructive changes, create data backup scripts first
-- 5. Migration filename format: migration_X.Y_to_X.Z.sql
-- 6. Version is automatically updated by run_migrations()
-- ==============================================

-- No schema changes needed for v1.4
-- This version adds:
-- - 7 user preference directives (directives-user-pref.json)
-- - 8 user system directives (directives-user-system.json)
-- - 6 git integration directives (directives-git.json)
-- - Updated directives-interactions.json format
-- All content updates, no schema changes required

# AIFP Database Migrations

This directory contains database migration files for the AIFP core database (`aifp_core.db`).

## Purpose

Migrations ensure **backward compatibility** when the database schema changes. When you update your AIFP installation, migrations automatically bring your database to the latest version without losing data.

## Migration File Naming Convention

```
migration_{from_version}_to_{to_version}.sql
```

**Examples:**
- `migration_1.3_to_1.4.sql` - Migrates from v1.3 to v1.4
- `migration_1.4_to_1.5.sql` - Migrates from v1.4 to v1.5

## How Migrations Work

1. **Automatic Detection**: When you run `sync-directives.py`, it checks the current database version
2. **Sequential Execution**: Migrations are applied in order (1.3 → 1.4 → 1.5)
3. **Version Tracking**: The `schema_version` table tracks the current version
4. **Idempotent**: Migrations can be run multiple times safely (use `IF NOT EXISTS`, `IF EXISTS`)

## Creating a New Migration

### Step 1: Create Migration File

Create a new file: `migration_1.4_to_1.5.sql`

```sql
-- Migration from v1.4 to v1.5
-- Date: 2025-11-01
-- Description: Brief description of changes

-- Add new column (example)
ALTER TABLE directives ADD COLUMN priority INTEGER DEFAULT 0;

-- Create new table (example)
CREATE TABLE IF NOT EXISTS directive_tags (
    directive_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (directive_id, tag),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_directives_priority ON directives(priority);

-- Update existing data (if needed)
UPDATE directives SET priority = 1 WHERE type = 'project' AND level = 0;
```

### Step 2: Update Schema Version

In `sync-directives.py`, update the version constant:

```python
CURRENT_SCHEMA_VERSION = "1.5"  # Change from "1.4"
```

### Step 3: Test Migration

```bash
# Test on a copy of the database first!
cp aifp_core.db aifp_core.db.backup

# Run sync with migrations
python3 docs/sync-directives.py

# Verify results
sqlite3 aifp_core.db "SELECT version FROM schema_version;"
```

### Step 4: Commit Changes

```bash
git add directives-json/migrations/migration_1.4_to_1.5.sql
git add docs/sync-directives.py
git commit -m "Add migration v1.4 to v1.5: Add directive priorities"
```

## Migration Best Practices

### ✅ DO

- **Use idempotent operations**: `IF NOT EXISTS`, `IF EXISTS`
- **Be additive**: Add columns/tables, don't remove
- **Create backups**: Test on database copies first
- **Document changes**: Include comments in migration files
- **Update data carefully**: Use WHERE clauses to avoid breaking existing data
- **Create indexes**: For new columns used in queries

### ❌ DON'T

- **Remove columns**: This breaks backward compatibility
- **Rename tables**: Old code may still reference them
- **Change data types**: Can cause data loss
- **Delete data**: Always preserve existing data
- **Skip versions**: Each migration should build on the previous

## Handling Breaking Changes

If you MUST make breaking changes:

1. **Deprecation Path**: Mark old columns as deprecated first
2. **Data Migration**: Copy data to new structure
3. **Version Bump**: Consider a major version change (1.x → 2.0)
4. **Documentation**: Clearly document the breaking change
5. **Rollback Plan**: Provide a way to revert if needed

## Example: Adding a Feature

**Scenario**: Add support for directive priorities

**Migration file**: `migration_1.4_to_1.5.sql`

```sql
-- Add priority support to directives
ALTER TABLE directives ADD COLUMN priority INTEGER DEFAULT 0;
ALTER TABLE directives ADD COLUMN execution_order INTEGER;

-- Index for sorting by priority
CREATE INDEX IF NOT EXISTS idx_directives_priority ON directives(priority);

-- Set default priorities (Level 0 = highest)
UPDATE directives SET priority = 10 WHERE type = 'project' AND level = 0;
UPDATE directives SET priority = 20 WHERE type = 'project' AND level = 1;
UPDATE directives SET priority = 30 WHERE type = 'project' AND level = 2;
UPDATE directives SET priority = 40 WHERE type = 'project' AND level = 3;
UPDATE directives SET priority = 50 WHERE type = 'project' AND level = 4;
UPDATE directives SET priority = 25 WHERE type = 'fp';
```

## Rollback Strategy

If a migration fails:

1. **Database has backups**: Restore from `.backup` file
2. **Transaction rollback**: Migrations run in transactions (auto-rollback on error)
3. **Manual intervention**: Fix the migration SQL and re-run

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.3 | 2025-10-20 | Initial schema with FP and Project directives |
| 1.4 | 2025-10-25 | Added User Preferences, User Directives, Git Integration |
| 1.5 | TBD | Future enhancements |

## Troubleshooting

### Migration fails with "column already exists"

**Cause**: Migration was partially applied before

**Solution**: Use `IF NOT EXISTS` in ALTER TABLE statements

### Version mismatch after migration

**Cause**: Migration didn't update schema_version table

**Solution**: Manually update:
```sql
UPDATE schema_version SET version = '1.5', updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

### Want to reset to clean state

```bash
# Delete database and re-sync from scratch
rm aifp_core.db
python3 docs/sync-directives.py
```

## Support

For migration issues or questions, see:
- [AIFP Documentation](../../README.md)
- [sync-directives.py source](../../sync-directives.py)
- Migration guide comments in script

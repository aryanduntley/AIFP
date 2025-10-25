# sync-directives.py Enhancements

**Date**: 2025-10-25
**Version**: 1.4

## Summary

Enhanced `sync-directives.py` with:
1. ✅ **Enhanced integrity validation** (8 total checks)
2. ✅ **Migration system** for schema changes
3. ✅ **Re-import support** (already existed, now documented)
4. ✅ **Backward compatibility** guarantees

---

## 1. Enhanced Integrity Validation

### Original Checks (5)

1. FP directives don't have level values
2. No orphaned parent_directive links
3. Directive interactions point to existing directives
4. No duplicate category links
5. Notes table presence check

### NEW Checks Added (3)

6. **Tool entries have valid directive references**
   - Verifies: All `tools.maps_to_directive_id` point to existing directives
   - Prevents: Broken tool → directive mappings

7. **Helper functions referenced in workflows exist**
   - Verifies: All helper function names in workflow JSON exist in `helper_functions` table
   - Scans: Workflow JSON recursively for patterns like `helper:`, `call:`, `function:`
   - Prevents: Runtime errors from missing helper implementations

8. **All directives have valid workflow structure**
   - Verifies: Workflow JSON is valid and contains required `trunk` field
   - Prevents: Malformed directive definitions

### Example Output

```
🧩 Running Post-Sync Integrity Validation...
✅ Database passed all integrity checks cleanly.
🔍 Integrity validation complete.
```

Or with issues:
```
🧩 Running Post-Sync Integrity Validation...
❗ Found 3 integrity warnings:
   ❌ Tool 'aifp_status_tool' references non-existent directive_id=999
   ⚠️ Directive 'project_init' references undefined helper_function 'create_project_structure'
   ⚠️ Directive 'fp_purity' missing required 'trunk' in workflow
🔍 Integrity validation complete.
```

---

## 2. Migration System

### Purpose

Ensures **backward compatibility** when database schema changes in future versions.

### How It Works

**Migration Flow:**
```
1. Run sync-directives.py
2. Check current DB version (from schema_version table)
3. Compare to CURRENT_SCHEMA_VERSION in script
4. Apply pending migrations in order
5. Update schema_version table
6. Proceed with directive sync
```

**Migration File Naming:**
```
directives-json/migrations/migration_1.4_to_1.5.sql
```

### Example Migration

```sql
-- Migration from v1.4 to v1.5
-- Description: Add directive priorities

ALTER TABLE directives ADD COLUMN priority INTEGER DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_directives_priority ON directives(priority);
UPDATE directives SET priority = 10 WHERE type = 'project' AND level = 0;
```

### Creating a New Migration

**Step 1**: Create migration file
```bash
touch directives-json/migrations/migration_1.4_to_1.5.sql
```

**Step 2**: Write schema changes (use idempotent SQL)
```sql
ALTER TABLE directives ADD COLUMN IF NOT EXISTS new_field TEXT;
```

**Step 3**: Update version constant in script
```python
CURRENT_SCHEMA_VERSION = "1.5"  # Was "1.4"
```

**Step 4**: Run sync
```bash
python3 docs/sync-directives.py
```

Output:
```
📊 Current database schema version: 1.4
🔄 Migrating database from 1.4 to 1.5
  → Applying migration to 1.5: migration_1.4_to_1.5.sql
  ✅ Migration to 1.5 complete
✅ Database migrated to version 1.5
```

### Migration Best Practices

✅ **DO:**
- Use `IF NOT EXISTS` / `IF EXISTS` for idempotency
- Be additive (add columns/tables, don't remove)
- Test on database copies first
- Document changes in migration file
- Create indexes for new columns

❌ **DON'T:**
- Remove columns (breaks backward compatibility)
- Rename tables (breaks old code)
- Change data types (can cause data loss)
- Delete data (always preserve)

### Backward Compatibility Guarantees

1. **Old databases work with new code**
   - Migrations apply automatically on sync
   - No manual intervention required

2. **New databases work with old data**
   - Migrations are additive
   - Existing data preserved

3. **Rollback safety**
   - Migrations run in transactions
   - Auto-rollback on error
   - Database backups recommended before major updates

---

## 3. Re-Import Support (Already Existed!)

### Capability

The sync script **already supports re-importing** modified directive JSON files:

```python
def upsert_directive(conn, entry: Dict[str, Any]) -> str:
    # Checks if directive exists
    if existing:
        # UPDATES existing directive
        return "updated"
    else:
        # INSERTS new directive
        return "added"
```

### Workflow

**Scenario**: You modify `directives-project.json`

```bash
# 1. Edit directive JSON
vim docs/directives-json/directives-project.json

# 2. Re-run sync
python3 docs/sync-directives.py
```

**Output:**
```
🔄 Starting Full AIFP Directive Sync (Schema v1.4)
📘 Loaded 25 directives from directives-json/directives-project.json
✅ Added: 0 | 🔁 Updated: 5 | 🔗 Interactions: 70
```

### What Gets Updated

- Directive metadata (description, workflow, etc.)
- Workflow JSON changes
- Intent keywords
- Confidence thresholds
- Roadblocks/error handling
- Parent relationships

### What Doesn't Get Overwritten

- Directive IDs (stable references)
- Created timestamps
- Related interactions (unless explicitly changed)

---

## 4. Complete Feature List

### Sync Capabilities

| Feature | Status | Description |
|---------|--------|-------------|
| **Load All Directives** | ✅ | FP Core, FP Aux, Project, User Prefs, User System, Git |
| **Upsert Support** | ✅ | Insert new, update existing directives |
| **Category Linking** | ✅ | Many-to-many directive-category relationships |
| **Interactions** | ✅ | Support for both old graph format and new interactions format |
| **Parent Links** | ✅ | Hierarchical directive relationships |
| **Integrity Validation** | ✅ | 8 checks for database consistency |
| **Migration System** | ✅ | Automatic schema upgrades |
| **Version Tracking** | ✅ | schema_version table |
| **Backward Compatibility** | ✅ | Old graph format still supported |
| **Dry Run Mode** | ✅ | Test changes without committing |

### Integrity Checks

1. ✅ FP directives have no levels
2. ✅ No orphaned parent links
3. ✅ Interactions reference valid directives
4. ✅ No duplicate category links
5. ✅ Notes table exists
6. ✅ **NEW:** Tools reference valid directives
7. ✅ **NEW:** Helper functions exist in workflow references
8. ✅ **NEW:** Workflows have valid structure (trunk field)

### Migration Features

- Automatic version detection
- Sequential migration application
- Transaction safety (rollback on error)
- Idempotent SQL support
- Version comparison (semantic versioning)
- File-based migrations (`.sql` files)
- Clear error reporting

---

## 5. Usage Examples

### Basic Sync

```bash
python3 docs/sync-directives.py
```

### Sync After Modifying Directives

```bash
# 1. Edit directive JSON
vim docs/directives-json/directives-git.json

# 2. Re-sync (auto-detects changes)
python3 docs/sync-directives.py
```

### Check Database Version

```bash
sqlite3 aifp_core.db "SELECT version FROM schema_version WHERE id = 1;"
# Output: 1.4
```

### Dry Run Mode

```python
# In sync-directives.py
DRY_RUN = True  # Change to True

# Run sync
python3 docs/sync-directives.py
# Changes shown but not committed
```

### Manual Migration

```bash
# Apply specific migration
sqlite3 aifp_core.db < directives-json/migrations/migration_1.4_to_1.5.sql

# Update version
sqlite3 aifp_core.db "UPDATE schema_version SET version='1.5' WHERE id=1;"
```

---

## 6. File Structure

```
docs/
├── sync-directives.py                    # Main sync script (enhanced)
├── directives-json/
│   ├── directives-fp-core.json          # 30 FP core directives
│   ├── directives-fp-aux.json           # 32 FP auxiliary directives
│   ├── directives-project.json          # 25 Project directives
│   ├── directives-user-pref.json        # 7 User preference directives
│   ├── directives-user-system.json      # 8 User system directives
│   ├── directives-git.json              # 6 Git integration directives
│   ├── directives-interactions.json     # Directive relationships
│   └── migrations/                       # Migration files
│       ├── README.md                     # Migration guide
│       ├── migration_1.3_to_1.4.sql     # Example migration
│       └── migration_1.4_to_1.5.sql     # Future migrations
└── db-schema/
    └── schemaExampleMCP.sql             # Reference schema
```

---

## 7. Troubleshooting

### "Directive already exists" Error

**Not an error!** This means the directive was successfully updated.

```
✅ Added: 0 | 🔁 Updated: 25
```

### Migration Fails

```bash
# Rollback automatically happens
❌ Migration to 1.5 failed: column 'priority' already exists

# Fix: Use IF NOT EXISTS in migration
ALTER TABLE directives ADD COLUMN IF NOT EXISTS priority INTEGER;
```

### Helper Function Not Found

```
⚠️ Directive 'project_init' references undefined helper_function 'create_db'
```

**Solution**: Either:
1. Add helper to `helper_functions` table
2. Update workflow JSON to use existing helper
3. Remove helper reference if no longer needed

### Version Mismatch

```bash
# Check current version
sqlite3 aifp_core.db "SELECT * FROM schema_version;"

# Manually set version (if needed)
sqlite3 aifp_core.db "UPDATE schema_version SET version='1.4' WHERE id=1;"
```

---

## 8. Future Enhancements (Potential)

- **Rollback migrations**: Reverse migration files (`migration_1.5_to_1.4_rollback.sql`)
- **Migration testing**: Automated test suite for migrations
- **Data validation**: Verify data integrity after migrations
- **Backup automation**: Auto-backup before migrations
- **Migration history**: Track all applied migrations in separate table
- **Conflict detection**: Detect if JSON files conflict with DB state

---

## Summary

**Enhanced `sync-directives.py` now provides:**

1. ✅ **Self-auditing database** - 8 integrity checks catch dangling references
2. ✅ **Automatic migrations** - Schema changes apply seamlessly
3. ✅ **Re-import support** - Modify JSON files anytime, re-sync to update
4. ✅ **Backward compatibility** - Old databases work with new code
5. ✅ **Production-ready** - Safe transactions, error handling, dry-run mode

**Total directives synced:** 108 (30 FP Core + 32 FP Aux + 25 Project + 7 User Pref + 8 User System + 6 Git)

**Version tracking:** Automatic via `schema_version` table

**Migration system:** File-based, sequential, idempotent, transaction-safe

The sync script is now **production-ready** with enterprise-grade migration and validation features! 🚀

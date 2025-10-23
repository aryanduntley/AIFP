# Migration Scripts Plan

**Purpose**: Define migration strategy for AIFP database schema updates across all four databases.

**Date Created**: 2025-10-12
**Last Updated**: 2025-10-23
**Status**: Planning

---

## Overview

AIFP uses a four-database architecture:
1. **aifp_core.db** - Read-only MCP configuration (shipped with MCP)
2. **project.db** - Mutable project state (per-project) - **Updated for Git integration v1.1**
3. **user_preferences.db** - User behavior customization (per-project)
4. **user_directives.db** - User-defined automation directives (per-project)

Each database requires independent versioning and migration paths.

---

## Migration Philosophy

### Principles
1. **Backward Compatibility**: Always maintain compatibility after initial release (v1.0+)
2. **Manual Execution**: Users run migrations explicitly (GitHub distribution model)
3. **Versioned Migrations**: Each migration is versioned and idempotent
4. **Clear Reporting**: Migrations log actions and report success/failure
5. **Rollback Support**: Provide rollback scripts for critical migrations

### Distribution Model
- **Current**: GitHub distribution (users clone/pull)
- **Future**: Package managers (npm, PyPI, cargo) with automatic migrations
- **Strategy**: Start simple (manual), evolve to automatic

---

## Schema Version Tracking

Each database tracks its own schema version:

```sql
-- Added to all three databases
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),      -- Only one row allowed
    version TEXT NOT NULL,                      -- e.g., '1.0', '1.1', '2.0'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (id, version) VALUES (1, '1.0');
```

### Version Query Helper
```python
def get_schema_version(db_path):
    """Get current schema version from database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT version FROM schema_version WHERE id = 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
```

---

## Migration Directory Structure

```
migrations/
├── aifp_core/
│   ├── v1.0_to_v1.1.sql
│   ├── v1.1_to_v1.2.sql
│   └── rollback/
│       └── v1.1_to_v1.0.sql
├── project/
│   ├── v1.0_to_v1.1.sql
│   ├── v1.1_to_v1.2.sql
│   └── rollback/
│       └── v1.1_to_v1.0.sql
├── user_preferences/
│   ├── v1.0_initial_schema.sql      -- Creates db if missing
│   ├── v1.0_to_v1.1.sql
│   └── rollback/
│       └── v1.1_to_v1.0.sql
└── migrate.py                        -- Main migration script
```

---

## Migration Script: migrate.py

### Usage
```bash
# Check current versions
python migrations/migrate.py --check

# Migrate all databases to latest
python migrations/migrate.py --all

# Migrate specific database
python migrations/migrate.py --db aifp_core --target 1.1
python migrations/migrate.py --db project --target 1.1
python migrations/migrate.py --db user_preferences --target 1.1

# Rollback to previous version
python migrations/migrate.py --db project --rollback

# Dry run (show what would happen)
python migrations/migrate.py --all --dry-run
```

### Features
1. **Auto-detect databases**: Find aifp_core.db, project.db, user_preferences.db
2. **Version checking**: Compare current version to target version
3. **Dependency resolution**: Apply migrations in correct order
4. **Idempotent execution**: Safe to run multiple times
5. **Logging**: Detailed migration log with timestamps
6. **Backup creation**: Auto-backup before migrations

### Script Outline
```python
#!/usr/bin/env python3
"""
AIFP Database Migration Script
Handles schema migrations for all three AIFP databases.
"""

import sqlite3
import os
import shutil
from pathlib import Path
from datetime import datetime

class MigrationManager:
    def __init__(self, aifp_root=None):
        self.aifp_root = aifp_root or Path.home() / ".aifp"
        self.project_root = None  # Auto-detect from cwd
        self.migrations_dir = Path(__file__).parent

    def get_database_paths(self):
        """Return paths to all three databases."""
        return {
            'aifp_core': self.aifp_root / "aifp_core.db",
            'project': self.find_project_db(),
            'user_preferences': self.find_user_preferences_db()
        }

    def find_project_db(self):
        """Find project.db in current project."""
        cwd = Path.cwd()
        while cwd != cwd.parent:
            project_db = cwd / ".aifp-project" / "project.db"
            if project_db.exists():
                return project_db
            cwd = cwd.parent
        return None

    def find_user_preferences_db(self):
        """Find user_preferences.db in current project."""
        cwd = Path.cwd()
        while cwd != cwd.parent:
            prefs_db = cwd / ".aifp-project" / "user_preferences.db"
            if prefs_db.exists():
                return prefs_db
            cwd = cwd.parent
        return None

    def get_current_version(self, db_path):
        """Get schema version from database."""
        if not db_path or not Path(db_path).exists():
            return None

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT version FROM schema_version WHERE id = 1")
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.OperationalError:
            # schema_version table doesn't exist
            return None
        finally:
            conn.close()

    def backup_database(self, db_path):
        """Create timestamped backup of database."""
        if not db_path or not Path(db_path).exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        return backup_path

    def apply_migration(self, db_path, migration_sql_path, dry_run=False):
        """Apply a single migration SQL file."""
        if dry_run:
            print(f"[DRY RUN] Would apply: {migration_sql_path}")
            return True

        with open(migration_sql_path, 'r') as f:
            migration_sql = f.read()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.executescript(migration_sql)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Error applying migration: {e}")
            return False
        finally:
            conn.close()

    def migrate(self, db_name, target_version=None, dry_run=False):
        """Migrate a database to target version."""
        db_paths = self.get_database_paths()
        db_path = db_paths.get(db_name)

        if not db_path:
            print(f"Database {db_name} not found")
            return False

        current_version = self.get_current_version(db_path)
        print(f"{db_name}: Current version = {current_version}")

        if not current_version:
            print(f"Warning: {db_name} has no schema_version table")
            return False

        # Find migration path
        migrations = self.find_migrations(db_name, current_version, target_version)

        if not migrations:
            print(f"{db_name}: Already at target version")
            return True

        # Backup before migration
        if not dry_run:
            backup_path = self.backup_database(db_path)
            print(f"Backup created: {backup_path}")

        # Apply migrations in order
        for migration in migrations:
            print(f"Applying: {migration}")
            success = self.apply_migration(db_path, migration, dry_run)
            if not success:
                print(f"Migration failed: {migration}")
                return False

        print(f"{db_name}: Migration completed successfully")
        return True

    def find_migrations(self, db_name, current_version, target_version):
        """Find migration files between current and target version."""
        # Implementation: scan migrations/{db_name}/ for vX.X_to_vY.Y.sql files
        # Return list in order
        pass

    def check_all_versions(self):
        """Check versions of all databases."""
        db_paths = self.get_database_paths()
        for db_name, db_path in db_paths.items():
            if db_path and Path(db_path).exists():
                version = self.get_current_version(db_path)
                print(f"{db_name}: v{version} ({db_path})")
            else:
                print(f"{db_name}: Not found")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AIFP Database Migration Tool")
    parser.add_argument('--check', action='store_true', help='Check current versions')
    parser.add_argument('--all', action='store_true', help='Migrate all databases')
    parser.add_argument('--db', choices=['aifp_core', 'project', 'user_preferences'])
    parser.add_argument('--target', help='Target version (e.g., 1.1)')
    parser.add_argument('--rollback', action='store_true', help='Rollback to previous version')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen')

    args = parser.parse_args()

    manager = MigrationManager()

    if args.check:
        manager.check_all_versions()
    elif args.all:
        # Migrate all databases
        for db_name in ['aifp_core', 'project', 'user_preferences']:
            manager.migrate(db_name, dry_run=args.dry_run)
    elif args.db:
        manager.migrate(args.db, target_version=args.target, dry_run=args.dry_run)
    else:
        parser.print_help()
```

---

## Migration Examples

### Example 1: Initial Release (v1.0)
**Goal**: Establish baseline schema with version tracking

**aifp_core/v1.0_initial_schema.sql**:
```sql
-- This is the baseline schema (no migration needed)
-- Just adds schema_version table if missing

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    version TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_version (id, version) VALUES (1, '1.0');
```

### Example 2: Remove Notes from aifp_core (v1.0 → v1.1)
**Goal**: Remove notes table from aifp_core.db

**aifp_core/v1.0_to_v1.1.sql**:
```sql
-- Remove notes table (moved to project.db)
DROP TABLE IF EXISTS notes;

-- Update schema version
UPDATE schema_version SET version = '1.1', updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

**Rollback** (aifp_core/rollback/v1.1_to_v1.0.sql):
```sql
-- Restore notes table structure (data loss expected)
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    reference_table TEXT,
    reference_id INTEGER,
    ai_generated BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Revert schema version
UPDATE schema_version SET version = '1.0', updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

### Example 3: Enhance project.db Notes (v1.0 → v1.1)
**Goal**: Add new fields to notes table in project.db

**project/v1.0_to_v1.1.sql**:
```sql
-- Add new fields to notes table
ALTER TABLE notes ADD COLUMN source TEXT DEFAULT 'user';
ALTER TABLE notes ADD COLUMN directive_name TEXT;
ALTER TABLE notes ADD COLUMN severity TEXT DEFAULT 'info';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_notes_directive ON notes(directive_name);
CREATE INDEX IF NOT EXISTS idx_notes_severity ON notes(severity);

-- Update schema version
UPDATE schema_version SET version = '1.1', updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

### Example 4: Add Git Integration Tables (v1.0 → v1.1)
**Goal**: Add Git integration tables and fields to project.db

**project/v1.0_to_v1.1_git_integration.sql**:
```sql
-- Add Git tracking fields to project table
ALTER TABLE project ADD COLUMN last_known_git_hash TEXT;
ALTER TABLE project ADD COLUMN last_git_sync DATETIME;

-- Create work_branches table for multi-user/multi-AI collaboration
CREATE TABLE IF NOT EXISTS work_branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_name TEXT UNIQUE NOT NULL,
    user_name TEXT NOT NULL,
    purpose TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_from TEXT DEFAULT 'main',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    merged_at DATETIME NULL,
    merge_conflicts_count INTEGER DEFAULT 0,
    merge_resolution_strategy TEXT,
    metadata_json TEXT
);

-- Create merge_history table for FP-powered conflict resolution audit trail
CREATE TABLE IF NOT EXISTS merge_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_branch TEXT NOT NULL,
    target_branch TEXT DEFAULT 'main',
    merge_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    conflicts_detected INTEGER DEFAULT 0,
    conflicts_auto_resolved INTEGER DEFAULT 0,
    conflicts_manual_resolved INTEGER DEFAULT 0,
    resolution_details TEXT,
    merged_by TEXT,
    merge_commit_hash TEXT
);

-- Create indexes for Git collaboration tables
CREATE INDEX IF NOT EXISTS idx_work_branches_user ON work_branches(user_name);
CREATE INDEX IF NOT EXISTS idx_work_branches_status ON work_branches(status);
CREATE INDEX IF NOT EXISTS idx_merge_history_timestamp ON merge_history(merge_timestamp);
CREATE INDEX IF NOT EXISTS idx_merge_history_source ON merge_history(source_branch);

-- Update schema version
UPDATE schema_version SET version = '1.1', updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

**Rollback** (project/rollback/v1.1_to_v1.0_git_integration.sql):
```sql
-- Drop Git integration tables
DROP TABLE IF EXISTS work_branches;
DROP TABLE IF EXISTS merge_history;

-- Drop indexes (automatically dropped with tables)

-- Remove Git fields from project table (SQLite limitation workaround)
-- Note: SQLite doesn't support DROP COLUMN before version 3.35.0
-- Alternative: Create new table without columns, copy data, rename
CREATE TABLE project_backup AS
SELECT id, name, purpose, goals_json, status, version,
       blueprint_checksum, user_directives_status,
       created_at, updated_at
FROM project;

DROP TABLE project;
ALTER TABLE project_backup RENAME TO project;

-- Recreate triggers
CREATE TRIGGER IF NOT EXISTS update_project_timestamp
AFTER UPDATE ON project
FOR EACH ROW
BEGIN
    UPDATE project SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- Revert schema version
UPDATE schema_version SET version = '1.0', updated_at = CURRENT_TIMESTAMP WHERE id = 1;
```

### Example 5: Initialize user_preferences.db (v1.0)
**Goal**: Create user_preferences.db if it doesn't exist

**user_preferences/v1.0_initial_schema.sql**:
```sql
-- Full schema from schemaExampleSettings.sql
-- This creates the database from scratch if missing
-- See docs/db-schema/schemaExampleSettings.sql for complete schema
```

---

## Migration Timeline

### Phase 1: Git Integration - project.db (v1.0 → v1.1) ✅ Complete
- ✅ Add last_known_git_hash and last_git_sync fields to project table
- ✅ Create work_branches table for multi-user/multi-AI collaboration
- ✅ Create merge_history table for FP-powered conflict resolution
- ✅ Add indexes for Git collaboration tables
- ✅ Update schema version to 1.1

### Phase 2: Clean aifp_core.db (v1.0 → v1.1)
- Remove notes table (if needed)
- Update workflow references in sample directives
- Add schema_version table

### Phase 3: Enhance project.db - Notes Enhancement (v1.1 → v1.2)
- Add source, directive_name, severity to notes table
- Add indexes for new fields
- Update schema version to 1.2

### Phase 4: Create user_preferences.db (v1.0)
- Initialize complete schema
- Create with all tracking disabled by default
- Add schema_version table

### Phase 5: Create user_directives.db (v1.0)
- Initialize complete schema for user-defined automation
- Add schema_version table

---

## Testing Strategy

### Pre-Migration Tests
1. Backup all databases
2. Verify current schema versions
3. Check for custom user modifications (warn if detected)
4. Validate migration SQL syntax

### Post-Migration Tests
1. Verify schema_version updated correctly
2. Run PRAGMA integrity_check on each database
3. Verify indexes created successfully
4. Test basic queries on new schema
5. Check triggers still work

### Rollback Tests
1. Apply migration
2. Verify success
3. Apply rollback
4. Verify schema matches original
5. Check data integrity (for non-destructive rollbacks)

---

## User Communication

### Migration Announcement Template
```markdown
## AIFP v1.1 Migration Required - Git Integration

This release includes database schema changes for Git integration and multi-user collaboration. Please run the migration script before using AIFP v1.1.

### What's Changed
- **project.db v1.0 → v1.1**: Git integration tables and fields added
  - New fields: `last_known_git_hash`, `last_git_sync` in project table
  - New tables: `work_branches` (collaboration), `merge_history` (FP conflict resolution)
  - New indexes for Git operations
  - Schema version updated to 1.1
- **New features enabled**: External change detection, multi-user branching, FP-powered merge conflict resolution

### How to Migrate
```bash
cd /path/to/AIFP
python migrations/migrate.py --check      # Check current versions
python migrations/migrate.py --all        # Migrate all databases
```

### Rollback
If you encounter issues:
```bash
python migrations/migrate.py --db project --rollback
```

Your databases are automatically backed up before migration.

### What This Enables
- 🔍 **External Change Detection**: AIFP detects code changes made outside sessions
- 🌿 **Multi-User Collaboration**: Work on separate branches (aifp-{user}-{number})
- 🤖 **Multi-AI Collaboration**: Multiple AI instances can work on same project
- 🔀 **FP-Powered Merging**: Intelligent conflict resolution using function purity analysis
- 📊 **Merge Audit Trail**: Complete history of all merges and conflict resolutions

### Questions?
See [Migration Guide](docs/migration-guide.md) or open an issue.
```

---

## Future Enhancements

### Automatic Migrations (Post-v1.0)
- Detect schema version on MCP startup
- Prompt user to migrate if outdated
- One-click migration from UI/CLI

### Multi-Project Migrations
- Scan for all AIFP projects in home directory
- Offer to migrate all at once
- Report which projects need migration

### Migration Validation
- Pre-flight checks (disk space, permissions)
- Post-migration validation queries
- Automatic rollback on failure

---

## Notes

- Migrations are **one-way by default** (forward only)
- Rollbacks are provided for critical migrations only
- User modifications to schema are **not supported** (may break migrations)
- Each migration should be **idempotent** (safe to run multiple times)
- Always test migrations on backup databases first

---

## Success Criteria

- [ ] All three databases have schema_version tracking
- [ ] Migration script successfully upgrades all databases
- [ ] Rollback scripts work for critical migrations
- [ ] Clear documentation for users
- [ ] Automated tests for migration paths
- [ ] Backup creation before migrations
- [ ] Detailed logging of migration actions

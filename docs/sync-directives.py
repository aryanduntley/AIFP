#!/usr/bin/env python3
"""
AIFP Directive Sync Manager — Schema v1.4
------------------------------------------
Synchronizes all directive JSON definitions with the aifp_core.db database.

Handles:
- Directives (FP Core + FP Aux + Project + User Preferences + User System + Git)
- Categories & Linking
- Directive Interactions (from directives-interactions.json)
- Parent relationships
- Helper Functions, Tools, and Notes table presence
- Integrity Validation (post-sync verification)

Updated: 2025-10-29
- Added support for user preference directives (directives-user-pref.json)
- Added support for user system directives (directives-user-system.json)
- Added support for git integration directives (directives-git.json)
- Updated to use directives-interactions.json (replaces project_directive_graph.json)
- Updated file paths to include directives-json/ prefix
- Maintains backward compatibility with old graph format
- Added MD file existence validation
- Added guide file removal verification

Total Directives: 124 (30 FP Core + 36 FP Aux + 36 Project + 7 User Pref + 9 User System + 6 Git)

This version aligns with the full schema (v1.4) for aifp_core.db.
"""

import os
import json
import sqlite3
import datetime
from typing import List, Dict, Any

# ===================================
# CONFIGURATION
# ===================================

# Database path - configurable via environment variable
# Default: .aifp/aifp_core.db (relative to script location)
# For production: Set AIFP_CORE_DB_PATH to MCP server's database location
DB_PATH = os.environ.get("AIFP_CORE_DB_PATH", ".aifp/aifp_core.db")

FP_DIRECTIVE_FILES = [
    "directives-json/directives-fp-core.json",
    "directives-json/directives-fp-aux.json"
]

PROJECT_DIRECTIVE_FILES = [
    "directives-json/directives-project.json"
]

USER_PREFERENCE_FILES = [
    "directives-json/directives-user-pref.json"
]

USER_SYSTEM_FILES = [
    "directives-json/directives-user-system.json"
]

GIT_DIRECTIVE_FILES = [
    "directives-json/directives-git.json"
]

DIRECTIVE_INTERACTIONS_FILE = "directives-json/directives-interactions.json"

# Deprecated - kept for backward compatibility
DIRECTIVE_GRAPH_FILE = "directives-json/project_directive_graph.json"

MIGRATIONS_DIR = "directives-json/migrations"
SYNC_REPORT_FILE = "logs/sync_report.json"

CURRENT_SCHEMA_VERSION = "1.4"
DRY_RUN = False


# ===================================
# DB CONNECTION & SCHEMA CHECK
# ===================================

def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection):
    """Ensures the entire v1.3 schema (directives, categories, helpers, tools, notes) exists."""
    cur = conn.cursor()

    cur.executescript("""
    -- ===============================================
    -- Directives and Relationships
    -- ===============================================
    CREATE TABLE IF NOT EXISTS directives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL,
        level INTEGER DEFAULT NULL,
        parent_directive TEXT REFERENCES directives(name),
        description TEXT,
        workflow JSON NOT NULL,
        md_file_path TEXT,
        roadblocks_json TEXT,
        intent_keywords_json TEXT,
        confidence_threshold REAL DEFAULT 0.5,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS directive_categories (
        directive_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY (directive_id, category_id),
        FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
    );

    CREATE TRIGGER IF NOT EXISTS enforce_level_on_fp
    BEFORE INSERT ON directives
    FOR EACH ROW
    WHEN NEW.type = 'fp' AND NEW.level IS NOT NULL
    BEGIN
        SELECT RAISE(ABORT, 'FP directives cannot have a level value.');
    END;

    CREATE TABLE IF NOT EXISTS directives_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_directive_id INTEGER NOT NULL,
        target_directive_id INTEGER NOT NULL,
        relation_type TEXT NOT NULL CHECK (relation_type IN (
            'triggers','depends_on','escalates_to','cross_link','fp_reference'
        )),
        weight INTEGER DEFAULT 1,
        description TEXT,
        active BOOLEAN DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (source_directive_id) REFERENCES directives(id),
        FOREIGN KEY (target_directive_id) REFERENCES directives(id)
    );

    CREATE INDEX IF NOT EXISTS idx_interactions_source ON directives_interactions (source_directive_id);
    CREATE INDEX IF NOT EXISTS idx_interactions_target ON directives_interactions (target_directive_id);
    CREATE INDEX IF NOT EXISTS idx_interactions_relation_type ON directives_interactions (relation_type);

    -- ===============================================
    -- Helper Functions and Tools
    -- ===============================================
    CREATE TABLE IF NOT EXISTS helper_functions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        file_path TEXT,
        parameters JSON,
        purpose TEXT,
        error_handling TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        maps_to_directive_id INTEGER,
        description TEXT,
        FOREIGN KEY (maps_to_directive_id) REFERENCES directives(id)
    );

    -- ===============================================
    -- Notes: Persistent reasoning and audit trail
    -- ===============================================
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        reference_table TEXT,
        reference_id INTEGER,
        ai_generated BOOLEAN DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()


# ===================================
# MIGRATION SYSTEM
# ===================================

def get_current_db_version(conn: sqlite3.Connection) -> str:
    """Get current schema version from database."""
    cur = conn.cursor()
    try:
        cur.execute("SELECT version FROM schema_version WHERE id = 1")
        row = cur.fetchone()
        return row['version'] if row else "1.0"
    except sqlite3.OperationalError:
        # schema_version table doesn't exist yet
        return "1.0"


def set_db_version(conn: sqlite3.Connection, version: str):
    """Update schema version in database."""
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO schema_version (id, version, updated_at)
        VALUES (1, ?, CURRENT_TIMESTAMP)
    """, (version,))
    conn.commit()


def get_migration_files() -> List[tuple]:
    """
    Get all migration files from migrations directory.
    Returns list of (version, filepath) tuples sorted by version.

    Migration files should be named: migration_1.2_to_1.3.sql
    """
    if not os.path.exists(MIGRATIONS_DIR):
        return []

    migrations = []
    for filename in os.listdir(MIGRATIONS_DIR):
        if filename.endswith('.sql') and filename.startswith('migration_'):
            # Parse version from filename: migration_1.2_to_1.3.sql -> 1.3
            try:
                parts = filename.replace('.sql', '').split('_to_')
                if len(parts) == 2:
                    target_version = parts[1]
                    migrations.append((target_version, os.path.join(MIGRATIONS_DIR, filename)))
            except Exception:
                print(f"⚠️  Could not parse migration filename: {filename}")

    # Sort by version
    migrations.sort(key=lambda x: [int(n) for n in x[0].split('.')])
    return migrations


def run_migrations(conn: sqlite3.Connection):
    """
    Run all pending migrations to bring database to current schema version.
    Ensures backward compatibility when schema changes.
    """
    current_version = get_current_db_version(conn)
    print(f"📊 Current database schema version: {current_version}")

    if current_version == CURRENT_SCHEMA_VERSION:
        print(f"✅ Database already at current version ({CURRENT_SCHEMA_VERSION})")
        return

    print(f"🔄 Migrating database from {current_version} to {CURRENT_SCHEMA_VERSION}")

    migrations = get_migration_files()
    if not migrations:
        print("⚠️  No migration files found. Using ensure_schema() for initialization.")
        return

    # Run migrations that are newer than current version
    for target_version, migration_file in migrations:
        # Compare versions
        current_parts = [int(n) for n in current_version.split('.')]
        target_parts = [int(n) for n in target_version.split('.')]

        # Only run if target > current
        if target_parts > current_parts:
            print(f"  → Applying migration to {target_version}: {os.path.basename(migration_file)}")

            try:
                with open(migration_file, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()

                conn.executescript(migration_sql)
                set_db_version(conn, target_version)
                print(f"  ✅ Migration to {target_version} complete")

            except Exception as e:
                print(f"  ❌ Migration to {target_version} failed: {e}")
                if not DRY_RUN:
                    conn.rollback()
                raise

    # Update to current version
    if get_current_db_version(conn) != CURRENT_SCHEMA_VERSION:
        set_db_version(conn, CURRENT_SCHEMA_VERSION)

    print(f"✅ Database migrated to version {CURRENT_SCHEMA_VERSION}")


# ===================================
# CORE HELPERS
# ===================================

def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    if not os.path.exists(filepath):
        print(f"⚠️  Missing file: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
        except Exception as e:
            print(f"❌ Error parsing {filepath}: {e}")
            return []


def relation_type_map(rel: str) -> str:
    return {
        "triggers": "triggers",
        "depends_on": "depends_on",
        "escalates_to": "escalates_to",
        "cross_links": "cross_link",
        "fp_links": "fp_reference"
    }.get(rel, "cross_link")


# ===================================
# INSERT / UPDATE FUNCTIONS
# ===================================

def upsert_directive(conn, entry: Dict[str, Any]) -> str:
    cur = conn.cursor()
    cur.execute("SELECT id FROM directives WHERE name=?", (entry["name"],))
    existing = cur.fetchone()

    fields = (
        entry["name"], entry["type"], entry.get("level"), entry.get("parent_directive"),
        entry.get("description"), json.dumps(entry.get("workflow", {})),
        entry.get("md_file_path"), json.dumps(entry.get("roadblocks_json", [])),
        json.dumps(entry.get("intent_keywords_json", [])),
        entry.get("confidence_threshold", 0.5)
    )

    if existing:
        cur.execute("""
            UPDATE directives SET
                type=?, level=?, parent_directive=?, description=?, workflow=?,
                md_file_path=?, roadblocks_json=?, intent_keywords_json=?,
                confidence_threshold=?, updated_at=CURRENT_TIMESTAMP
            WHERE name=?
        """, fields[1:] + (entry["name"],))
        conn.commit()
        return "updated"
    else:
        cur.execute("""
            INSERT INTO directives
            (name, type, level, parent_directive, description, workflow,
             md_file_path, roadblocks_json, intent_keywords_json, confidence_threshold,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, fields)
        conn.commit()
        return "added"


def sync_category(conn, entry: Dict[str, Any], directive_id: int):
    if "category" not in entry:
        return
    cur = conn.cursor()
    cat = entry["category"]
    cur.execute("INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                (cat["name"], cat.get("description")))
    conn.commit()
    cur.execute("SELECT id FROM categories WHERE name=?", (cat["name"],))
    cat_id = cur.fetchone()["id"]
    cur.execute("INSERT OR IGNORE INTO directive_categories (directive_id, category_id) VALUES (?, ?)",
                (directive_id, cat_id))
    conn.commit()


def insert_interaction(conn, src_id, tgt_id, relation_type, desc=""):
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO directives_interactions
        (source_directive_id, target_directive_id, relation_type, description)
        VALUES (?, ?, ?, ?)
    """, (src_id, tgt_id, relation_type, desc))
    conn.commit()


# ===================================
# SYNC EXECUTION
# ===================================

def sync_directives():
    print("🔄 Starting Full AIFP Directive Sync (Schema v1.4)")
    print("📦 Including: FP Core, FP Aux, Project, User Prefs, User System, Git Integration")

    # Ensure database directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"📁 Created database directory: {db_dir}")

    conn = get_conn(DB_PATH)
    ensure_schema(conn)

    # Run any pending migrations
    run_migrations(conn)

    cur = conn.cursor()

    # Load all directive files
    all_directive_files = (
        FP_DIRECTIVE_FILES +
        PROJECT_DIRECTIVE_FILES +
        USER_PREFERENCE_FILES +
        USER_SYSTEM_FILES +
        GIT_DIRECTIVE_FILES
    )

    all_entries = []
    for file in all_directive_files:
        entries = load_json_file(file)
        all_entries.extend(entries)
        print(f"📘 Loaded {len(entries)} directives from {file}")

    report = {"added": [], "updated": [], "interactions": 0}

    for entry in all_entries:
        if not entry.get("name") or not entry.get("type"):
            continue
        result = upsert_directive(conn, entry)
        cur.execute("SELECT id FROM directives WHERE name=?", (entry["name"],))
        directive_id = cur.fetchone()["id"]
        sync_category(conn, entry, directive_id)
        report[result].append(entry["name"])

    # Second pass: Parent linkage
    for entry in all_entries:
        if entry.get("parent_directive"):
            cur.execute("""
                UPDATE directives SET parent_directive=? 
                WHERE name=? AND parent_directive IS NULL
            """, (entry["parent_directive"], entry["name"]))
    conn.commit()

    # Directive relationships from directives-interactions.json
    if os.path.exists(DIRECTIVE_INTERACTIONS_FILE):
        print(f"📊 Linking interactions from {DIRECTIVE_INTERACTIONS_FILE}")
        interactions_data = load_json_file(DIRECTIVE_INTERACTIONS_FILE)

        # Handle both old graph format and new interactions format
        for item in interactions_data:
            # New format: direct interactions list
            if "source_directive" in item and "target_directive" in item:
                cur.execute("SELECT id FROM directives WHERE name=?", (item["source_directive"],))
                src = cur.fetchone()
                cur.execute("SELECT id FROM directives WHERE name=?", (item["target_directive"],))
                tgt = cur.fetchone()

                if src and tgt:
                    insert_interaction(
                        conn,
                        src["id"],
                        tgt["id"],
                        relation_type_map(item.get("relation_type", "cross_link")),
                        item.get("description", "")
                    )
                    report["interactions"] += 1

            # Old graph format: node with relationship lists
            elif "name" in item:
                cur.execute("SELECT id FROM directives WHERE name=?", (item["name"],))
                src = cur.fetchone()
                if not src:
                    continue
                src_id = src["id"]
                for rel_type in ["triggers", "depends_on", "escalates_to", "cross_links", "fp_links"]:
                    for target in item.get(rel_type, []):
                        cur.execute("SELECT id FROM directives WHERE name=?", (target,))
                        tgt = cur.fetchone()
                        if tgt:
                            insert_interaction(conn, src_id, tgt["id"],
                                               relation_type_map(rel_type),
                                               f"{item['name']} {rel_type} {target}")
                            report["interactions"] += 1

    # Fallback to old graph file if new file not found
    elif os.path.exists(DIRECTIVE_GRAPH_FILE):
        print(f"📊 Linking interactions from {DIRECTIVE_GRAPH_FILE} (deprecated)")
        graph_data = load_json_file(DIRECTIVE_GRAPH_FILE)
        for node in graph_data:
            cur.execute("SELECT id FROM directives WHERE name=?", (node["name"],))
            src = cur.fetchone()
            if not src:
                continue
            src_id = src["id"]
            for rel_type in ["triggers", "depends_on", "escalates_to", "cross_links", "fp_links"]:
                for target in node.get(rel_type, []):
                    cur.execute("SELECT id FROM directives WHERE name=?", (target,))
                    tgt = cur.fetchone()
                    if tgt:
                        insert_interaction(conn, src_id, tgt["id"],
                                           relation_type_map(rel_type),
                                           f"{node['name']} {rel_type} {target}")
                        report["interactions"] += 1

    if DRY_RUN:
        conn.rollback()
        print("🧪 Dry-run mode: no DB changes committed.")
    else:
        conn.commit()

    print(f"✅ Added: {len(report['added'])} | 🔁 Updated: {len(report['updated'])} | 🔗 Interactions: {report['interactions']}")
    os.makedirs(os.path.dirname(SYNC_REPORT_FILE), exist_ok=True)
    with open(SYNC_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"📄 Sync report saved to {SYNC_REPORT_FILE}")

    # Run post-sync validation
    validate_integrity(conn)

    conn.close()


# ===================================
# INTEGRITY VALIDATION LAYER
# ===================================

def validate_integrity(conn):
    """Runs a suite of consistency checks after sync."""
    print("\n🧩 Running Post-Sync Integrity Validation...")
    cur = conn.cursor()
    issues = []

    # 1. Check for FP directives with levels
    cur.execute("SELECT name FROM directives WHERE type='fp' AND level IS NOT NULL;")
    for row in cur.fetchall():
        issues.append(f"❌ FP directive '{row['name']}' has a level assigned.")

    # 2. Check for orphaned parent_directive links
    cur.execute("""
        SELECT name, parent_directive FROM directives
        WHERE parent_directive IS NOT NULL
        AND parent_directive NOT IN (SELECT name FROM directives)
    """)
    for row in cur.fetchall():
        issues.append(f"⚠️ Orphaned parent link: {row['name']} → {row['parent_directive']}")

    # 3. Verify all interactions point to existing directives
    cur.execute("""
        SELECT i.id, d1.name AS source, d2.name AS target
        FROM directives_interactions i
        LEFT JOIN directives d1 ON d1.id = i.source_directive_id
        LEFT JOIN directives d2 ON d2.id = i.target_directive_id
        WHERE d1.name IS NULL OR d2.name IS NULL
    """)
    for row in cur.fetchall():
        issues.append(f"⚠️ Broken interaction ID {row['id']} → Missing target/source.")

    # 4. Check for duplicate category links
    cur.execute("""
        SELECT directive_id, category_id, COUNT(*) as c FROM directive_categories
        GROUP BY directive_id, category_id HAVING c > 1
    """)
    for row in cur.fetchall():
        issues.append(f"⚠️ Duplicate directive-category link for directive_id={row['directive_id']}.")

    # 5. Verify notes table integrity
    cur.execute("SELECT COUNT(*) as c FROM notes;")
    note_count = cur.fetchone()["c"]
    if note_count == 0:
        issues.append("ℹ️ Notes table is empty — this may be fine, but consider adding documentation entries.")

    # 6. Verify tool entries have valid directive references
    cur.execute("""
        SELECT t.name, t.maps_to_directive_id
        FROM tools t
        WHERE t.maps_to_directive_id IS NOT NULL
        AND t.maps_to_directive_id NOT IN (SELECT id FROM directives)
    """)
    for row in cur.fetchall():
        issues.append(f"❌ Tool '{row['name']}' references non-existent directive_id={row['maps_to_directive_id']}")

    # 7. Verify helper_functions referenced in workflows exist
    cur.execute("SELECT id, name, workflow FROM directives;")
    for row in cur.fetchall():
        try:
            workflow = json.loads(row['workflow']) if isinstance(row['workflow'], str) else row['workflow']
            helper_refs = extract_helper_references(workflow)

            for helper_name in helper_refs:
                cur.execute("SELECT name FROM helper_functions WHERE name=?", (helper_name,))
                if not cur.fetchone():
                    issues.append(f"⚠️ Directive '{row['name']}' references undefined helper_function '{helper_name}'")
        except (json.JSONDecodeError, TypeError):
            issues.append(f"⚠️ Directive '{row['name']}' has invalid workflow JSON")

    # 8. Verify all directives have valid workflow structure
    cur.execute("SELECT name, workflow FROM directives;")
    for row in cur.fetchall():
        try:
            workflow = json.loads(row['workflow']) if isinstance(row['workflow'], str) else row['workflow']
            if not isinstance(workflow, dict) or 'trunk' not in workflow:
                issues.append(f"⚠️ Directive '{row['name']}' missing required 'trunk' in workflow")
        except (json.JSONDecodeError, TypeError):
            issues.append(f"❌ Directive '{row['name']}' has malformed workflow JSON")

    # 9. Verify MD file paths exist for all directives
    cur.execute("SELECT name, md_file_path FROM directives WHERE md_file_path IS NOT NULL;")
    md_files_checked = 0
    for row in cur.fetchall():
        # Construct path relative to project root
        md_path = os.path.join("../src/aifp/reference", row['md_file_path'])
        if not os.path.exists(md_path):
            issues.append(f"❌ Directive '{row['name']}' references missing MD file: {row['md_file_path']}")
        md_files_checked += 1

    if md_files_checked > 0:
        print(f"   ✓ Verified {md_files_checked} MD file paths")

    # 10. Verify guide files have been removed (should not exist)
    guide_files_to_check = [
        "../src/aifp/reference/guides/automation-projects.md",
        "../src/aifp/reference/guides/project-structure.md",
        "../src/aifp/reference/guides/git-integration.md",
        "../src/aifp/reference/guides/directive-interactions.md"
    ]
    for guide_file in guide_files_to_check:
        if os.path.exists(guide_file):
            issues.append(f"⚠️ Guide file still exists (should be deleted): {guide_file}")

    print(f"   ✓ Verified {len(guide_files_to_check)} guide files removed")

    if issues:
        print(f"❗ Found {len(issues)} integrity warnings:")
        for i in issues:
            print("   " + i)
    else:
        print("✅ Database passed all integrity checks cleanly.")

    print("🔍 Integrity validation complete.\n")


def extract_helper_references(workflow: dict, refs: set = None) -> set:
    """
    Recursively extract helper function references from workflow JSON.
    Looks for common patterns like 'helper', 'call', 'function' keys.
    """
    if refs is None:
        refs = set()

    if isinstance(workflow, dict):
        # Check for helper references in common patterns
        for key in ['helper', 'call', 'function', 'helper_function']:
            if key in workflow and isinstance(workflow[key], str):
                refs.add(workflow[key])

        # Check 'details' which often contains helper calls
        if 'details' in workflow and isinstance(workflow['details'], dict):
            for value in workflow['details'].values():
                if isinstance(value, str) and value.startswith('helper:'):
                    refs.add(value.replace('helper:', ''))

        # Recurse into nested structures
        for value in workflow.values():
            if isinstance(value, (dict, list)):
                extract_helper_references(value, refs)

    elif isinstance(workflow, list):
        for item in workflow:
            if isinstance(item, (dict, list)):
                extract_helper_references(item, refs)

    return refs


# ===================================
# ENTRY POINT
# ===================================

if __name__ == "__main__":
    try:
        sync_directives()
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# ==================================
# MIGRATION GUIDE
# ==================================
# To create a new migration:
# 1. Create file: directives-json/migrations/migration_1.4_to_1.5.sql
# 2. Include schema changes (ALTER TABLE, CREATE TABLE, etc.)
# 3. Update CURRENT_SCHEMA_VERSION at top of this file
# 4. Run sync script - migrations apply automatically
#
# Example migration file structure:
# -- Migration from v1.4 to v1.5
# -- Description: Add new feature X
#
# ALTER TABLE directives ADD COLUMN new_field TEXT;
# CREATE INDEX IF NOT EXISTS idx_new_field ON directives(new_field);
#
# -- Update version (handled automatically by run_migrations)
# ==================================
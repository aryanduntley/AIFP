#!/usr/bin/env python3
"""
AIFP Directive Sync Manager — Schema v1.5
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

This version aligns with the full schema (v1.5) for aifp_core.db.
Removed: tools table, notes table (not needed in read-only aifp_core.db)
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
# Default: ../testdb/aifp_core.db (relative to script location - for testing)
# For production: Set AIFP_CORE_DB_PATH to MCP server's database location
DB_PATH = os.environ.get("AIFP_CORE_DB_PATH", "../testdb/aifp_core.db")

FP_DIRECTIVE_FILES = [
    "directives-fp-core.json",
    "directives-fp-aux.json"
]

PROJECT_DIRECTIVE_FILES = [
    "directives-project.json"
]

USER_PREFERENCE_FILES = [
    "directives-user-pref.json"
]

USER_SYSTEM_FILES = [
    "directives-user-system.json"
]

GIT_DIRECTIVE_FILES = [
    "directives-git.json"
]

DIRECTIVE_INTERACTIONS_FILE = "directives-interactions.json"
DIRECTIVE_HELPER_INTERACTIONS_FILE = "directive-helper-interactions.json"

# Deprecated - kept for backward compatibility
DIRECTIVE_GRAPH_FILE = "project_directive_graph.json"

MIGRATIONS_DIR = "migrations"
SYNC_REPORT_FILE = "logs/sync_report.json"

CURRENT_SCHEMA_VERSION = "1.5"
DRY_RUN = False


# ===================================
# DB CONNECTION & SCHEMA CHECK
# ===================================

def get_conn(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection):
    """Load and execute schema from external SQL file (source of truth)."""
    # Path to schema file relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, '..', '..', 'src', 'aifp', 'database', 'schemas', 'aifp_core.sql')

    if not os.path.exists(schema_path):
        print(f"❌ Schema file not found: {schema_path}")
        print(f"   Please ensure src/aifp/database/schemas/aifp_core.sql exists")
        raise FileNotFoundError(f"Schema file missing: {schema_path}")

    print(f"📄 Loading schema from: {schema_path}")

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    conn.executescript(schema_sql)
    conn.commit()
    print("✅ Schema loaded successfully")


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
            # Handle different JSON structures:
            # - Direct array of directives: [...]
            # - Wrapper object with 'directives' key: {"directives": [...], ...}
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'directives' in data:
                return data['directives']
            else:
                return [data]
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
# HELPER FUNCTIONS SYNC
# ===================================

def sync_helper_functions(conn):
    """
    Load helper functions from helpers_parsed.json and populate helper_functions table.

    Populates table with complete helper data:
    - name, file_path, parameters, purpose, error_handling
    - is_tool: Read from JSON (TRUE if exposed as MCP tool)
    - is_sub_helper: Read from JSON (TRUE if internal helper only)

    Source: docs/directives-json/helpers_parsed.json (49 helpers organized into 5 module files)
    """
    print("\n🔧 Syncing helper functions from JSON...")

    # Load helpers from JSON file
    helpers_json_path = os.path.join(os.path.dirname(__file__), 'helpers_parsed.json')

    if not os.path.exists(helpers_json_path):
        print(f"⚠️  Helper functions file not found: {helpers_json_path}")
        print("   Run parse_helpers.py to generate helpers_parsed.json")
        return

    helpers = load_json_file(helpers_json_path)

    if not helpers:
        print("⚠️  No helpers found in helpers_parsed.json")
        return

    print(f"📋 Loaded {len(helpers)} helper functions from JSON")

    # Insert helper functions into table
    cur = conn.cursor()
    inserted = 0
    updated = 0

    for helper in helpers:
        name = helper.get('name')
        if not name:
            continue

        # Check if helper already exists
        cur.execute("SELECT id FROM helper_functions WHERE name=?", (name,))
        existing = cur.fetchone()

        if existing:
            # Update existing helper with latest data from JSON
            cur.execute("""
                UPDATE helper_functions
                SET file_path = ?,
                    parameters = ?,
                    purpose = ?,
                    error_handling = ?,
                    is_tool = ?,
                    is_sub_helper = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE name = ?
            """, (
                helper.get('file_path'),
                helper.get('parameters'),  # Already JSON string
                helper.get('purpose'),
                helper.get('error_handling'),
                1 if helper.get('is_tool', False) else 0,
                1 if helper.get('is_sub_helper', False) else 0,
                name
            ))
            updated += 1
        else:
            # Insert new helper with all available data
            cur.execute("""
                INSERT INTO helper_functions
                (name, file_path, parameters, purpose, error_handling, is_tool, is_sub_helper)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                helper.get('file_path'),
                helper.get('parameters'),  # Already JSON string
                helper.get('purpose'),
                helper.get('error_handling'),
                1 if helper.get('is_tool', False) else 0,
                1 if helper.get('is_sub_helper', False) else 0
            ))
            inserted += 1

    conn.commit()
    print(f"✅ Helper functions synced: {inserted} new, {updated} updated")

    # Show module organization summary
    cur.execute("""
        SELECT file_path, COUNT(*) as count
        FROM helper_functions
        GROUP BY file_path
        ORDER BY file_path
    """)
    print("   Module organization:")
    for row in cur.fetchall():
        print(f"     {row['count']:2d} helpers → {row['file_path']}")


def sync_directive_helper_interactions(conn):
    """
    Load directive-helper mappings from directive-helper-interactions.json
    and populate directive_helpers junction table.

    Populates table with:
    - directive_id, helper_function_id (foreign keys)
    - execution_context, sequence_order, is_required
    - parameters_mapping (optional), description

    Source: docs/directive-helper-interactions.json (63 mappings)
    """
    print("\n🔗 Syncing directive-helper interactions...")

    interactions_path = os.path.join(os.path.dirname(__file__), DIRECTIVE_HELPER_INTERACTIONS_FILE)

    if not os.path.exists(interactions_path):
        print(f"⚠️  Directive-helper interactions file not found: {interactions_path}")
        print("   Run generate-directive-helper-interactions.py to generate this file")
        return

    # Load JSON directly (not using load_json_file since this has different structure)
    with open(interactions_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data or 'mappings' not in data:
        print("⚠️  No mappings found in directive-helper-interactions.json")
        return

    mappings = data['mappings']
    print(f"📋 Loaded {len(mappings)} helper-directive mappings")

    cur = conn.cursor()
    inserted = 0
    skipped = 0
    errors = 0

    for mapping in mappings:
        directive_name = mapping.get('directive_name')
        helper_name = mapping.get('helper_name')

        if not directive_name or not helper_name:
            skipped += 1
            continue

        # Look up directive_id
        cur.execute("SELECT id FROM directives WHERE name=?", (directive_name,))
        directive_row = cur.fetchone()

        if not directive_row:
            print(f"   ⚠️  Directive not found: {directive_name}")
            errors += 1
            continue

        directive_id = directive_row['id']

        # Look up helper_function_id
        cur.execute("SELECT id FROM helper_functions WHERE name=?", (helper_name,))
        helper_row = cur.fetchone()

        if not helper_row:
            print(f"   ⚠️  Helper not found: {helper_name}")
            errors += 1
            continue

        helper_id = helper_row['id']

        # Check if mapping already exists
        cur.execute("""
            SELECT id FROM directive_helpers
            WHERE directive_id=? AND helper_function_id=? AND execution_context=?
        """, (directive_id, helper_id, mapping.get('execution_context', '')))

        existing = cur.fetchone()

        if existing:
            # Update existing mapping
            cur.execute("""
                UPDATE directive_helpers
                SET sequence_order = ?,
                    is_required = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                mapping.get('sequence_order', 0),
                1 if mapping.get('is_required', True) else 0,
                mapping.get('description', ''),
                existing['id']
            ))
        else:
            # Insert new mapping
            cur.execute("""
                INSERT INTO directive_helpers
                (directive_id, helper_function_id, execution_context, sequence_order,
                 is_required, parameters_mapping, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                directive_id,
                helper_id,
                mapping.get('execution_context', ''),
                mapping.get('sequence_order', 0),
                1 if mapping.get('is_required', True) else 0,
                None,  # parameters_mapping not in current JSON format
                mapping.get('description', '')
            ))
            inserted += 1

    conn.commit()
    print(f"✅ Directive-helper interactions synced: {inserted} new")
    if errors > 0:
        print(f"   ⚠️  {errors} mappings had errors (directive or helper not found)")
    if skipped > 0:
        print(f"   ⚠️  {skipped} mappings skipped (missing required fields)")

    # Show summary statistics
    cur.execute("""
        SELECT COUNT(*) as total_mappings,
               COUNT(DISTINCT directive_id) as unique_directives,
               COUNT(DISTINCT helper_function_id) as unique_helpers
        FROM directive_helpers
    """)
    stats = cur.fetchone()
    print(f"   Total mappings in database: {stats['total_mappings']}")
    print(f"   Directives with helpers: {stats['unique_directives']}")
    print(f"   Helpers mapped to directives: {stats['unique_helpers']}")


# ===================================
# SYNC EXECUTION
# ===================================

def sync_directives():
    print("🔄 Starting Full AIFP Directive Sync (Schema v1.5)")
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

    # Sync helper functions from JSON file
    sync_helper_functions(conn)

    # Directive relationships from directives-interactions.json
    if os.path.exists(DIRECTIVE_INTERACTIONS_FILE):
        print(f"📊 Linking interactions from {DIRECTIVE_INTERACTIONS_FILE}")
        interactions_data = load_json_file(DIRECTIVE_INTERACTIONS_FILE)

        # Handle both old graph format and new interactions format
        for item in interactions_data:
            # New format: direct interactions list with 'source' and 'target' keys
            if "source" in item and "target" in item:
                cur.execute("SELECT id FROM directives WHERE name=?", (item["source"],))
                src = cur.fetchone()
                cur.execute("SELECT id FROM directives WHERE name=?", (item["target"],))
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
                else:
                    # Log missing directive references
                    if not src:
                        print(f"   ⚠️ Source directive not found: {item['source']}")
                    if not tgt:
                        print(f"   ⚠️ Target directive not found: {item['target']}")

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

    # Sync directive-helper interactions (junction table mappings)
    sync_directive_helper_interactions(conn)

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

    # 5. Verify helper_functions loaded from JSON with is_tool and is_sub_helper
    cur.execute("SELECT COUNT(*) as tool_count FROM helper_functions WHERE is_tool = 1;")
    tool_count = cur.fetchone()["tool_count"]
    cur.execute("SELECT COUNT(*) as sub_helper_count FROM helper_functions WHERE is_sub_helper = 1;")
    sub_helper_count = cur.fetchone()["sub_helper_count"]

    if tool_count == 0:
        issues.append("⚠️ No helpers marked as is_tool=1. MCP tools may not be properly configured.")
    else:
        print(f"   ✓ Found {tool_count} MCP tools (is_tool=1)")

    if sub_helper_count > 0:
        print(f"   ✓ Found {sub_helper_count} sub-helpers (is_sub_helper=1)")

    # 6. Validate directive_helpers junction table references

    # 7. Verify all directives have valid workflow structure
    cur.execute("SELECT name, workflow FROM directives;")
    for row in cur.fetchall():
        try:
            workflow = json.loads(row['workflow']) if isinstance(row['workflow'], str) else row['workflow']
            if not isinstance(workflow, dict) or 'trunk' not in workflow:
                issues.append(f"⚠️ Directive '{row['name']}' missing required 'trunk' in workflow")
        except (json.JSONDecodeError, TypeError):
            issues.append(f"❌ Directive '{row['name']}' has malformed workflow JSON")

    # 8. Verify MD file paths exist for all directives
    cur.execute("SELECT name, md_file_path FROM directives WHERE md_file_path IS NOT NULL;")
    md_files_checked = 0

    # Use absolute path resolution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, '..', '..')  # Two levels up: directives-json -> docs -> project root
    reference_dir = os.path.join(project_root, 'src', 'aifp', 'reference')

    for row in cur.fetchall():
        # Construct absolute path
        md_path = os.path.join(reference_dir, row['md_file_path'])
        if not os.path.exists(md_path):
            issues.append(f"❌ Directive '{row['name']}' references missing MD file: {row['md_file_path']}")
        md_files_checked += 1

    if md_files_checked > 0:
        print(f"   ✓ Verified {md_files_checked} MD file paths")

    # 9. Verify guide files have been removed (should not exist)
    guides_dir = os.path.join(reference_dir, 'guides')
    guide_files_to_check = [
        os.path.join(guides_dir, "automation-projects.md"),
        os.path.join(guides_dir, "project-structure.md"),
        os.path.join(guides_dir, "git-integration.md"),
        os.path.join(guides_dir, "directive-interactions.md")
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
#!/usr/bin/env python3
"""
AIFP Directive Sync Manager — Schema v1.3
------------------------------------------
Synchronizes all directive JSON definitions with the aifp_core.db database.

Handles:
- Directives (FP + Project)
- Categories & Linking
- Directive Interactions (from Graph JSON)
- Parent relationships
- Helper Functions, Tools, and Notes table presence
- Integrity Validation (post-sync verification)

This version aligns with the full schema (v1.3) for aifp_core.db.
"""

import os
import json
import sqlite3
import datetime
from typing import List, Dict, Any

# ===================================
# CONFIGURATION
# ===================================

DB_PATH = "aifp_core.db"

FP_DIRECTIVE_FILES = [
    "directives-fp-core.json",
    "directives-fp-aux.json"
]

PROJECT_DIRECTIVE_FILES = [
    "directives-project.json"
]

DIRECTIVE_GRAPH_FILE = "project_directive_graph.json"

SYNC_REPORT_FILE = "logs/sync_report.json"

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
    print("🔄 Starting Full AIFP Directive Sync (Schema v1.3)")
    conn = get_conn(DB_PATH)
    ensure_schema(conn)
    cur = conn.cursor()

    # Load directives
    all_entries = []
    for file in FP_DIRECTIVE_FILES + PROJECT_DIRECTIVE_FILES:
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

    # Directive relationships
    if os.path.exists(DIRECTIVE_GRAPH_FILE):
        print(f"📊 Linking interactions from {DIRECTIVE_GRAPH_FILE}")
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
# Should we extend the Integrity Validation Layer next to also verify that:
# Each tool entry has a valid maps_to_directive_id
# Each helper_function referenced in any workflow JSON actually exists in helper_functions
# That would give you a truly self-auditing MCP core database — no dangling references anywhere.
# ==================================
"""
Tests for aifp.helpers.orchestrators.migration

Verifies:
- Version mismatch detection
- Data preservation through migration
- Timestamp preservation (triggers don't fire on INSERT)
- Backup + new DB in temp locations
- Row count verification
- Missing DB handling (user_directives skipped)
- All-current returns empty migrated list
- Custom aifp_folder parameter
"""

import os
import sqlite3
import tempfile
import shutil

from aifp.helpers.orchestrators.migration import (
    _check_pending_migrations,
    _get_db_version,
    _get_schema_path,
    migrate_databases,
)
from aifp.database.connection import set_project_root, clear_project_root_cache


# ============================================================================
# Fixtures: Create temp project with old-version DBs
# ============================================================================

def _setup_project(tmp_dir, aifp_folder=".aifp-project"):
    """Create a temp project with old-version project.db and user_preferences.db."""
    aifp_dir = os.path.join(tmp_dir, aifp_folder)
    os.makedirs(aifp_dir, exist_ok=True)
    os.makedirs(os.path.join(aifp_dir, "backups"), exist_ok=True)
    return aifp_dir


def _create_old_project_db(aifp_dir, version="1.6"):
    """Create a project.db with old version and some test data."""
    db_path = os.path.join(aifp_dir, "project.db")
    conn = sqlite3.connect(db_path)
    # Use real schema but with old version
    schema_path = _get_schema_path("project.sql")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    # Replace new version with old version
    schema_sql = schema_sql.replace(
        "INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, '1.8')",
        f"INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, '{version}')"
    )
    # Remove the new note types to simulate old schema
    schema_sql = schema_sql.replace(
        "'summary',         -- Manual summaries (distinct from auto_summary which is automated)\n"
        "        -- Deferred work tracking\n"
        "        'deferred',        -- Placeholder code, TODOs, stubs, intentionally incomplete work\n"
        "        'completed',       -- Resolved deferred items, closed follow-ups\n"
        "        'obsolete'         -- Deferred items no longer relevant (code refactored, task re-scoped)\n",
        "'summary'          -- Manual summaries (distinct from auto_summary which is automated)\n"
    )
    conn.executescript(schema_sql)

    # Insert test data
    conn.execute(
        "INSERT INTO project (name, purpose, goals_json) VALUES (?, ?, ?)",
        ("TestProject", "Testing migration", '["test"]')
    )
    conn.execute(
        "INSERT INTO infrastructure (type, value, description) VALUES (?, ?, ?)",
        ("language", "Python", "Primary language")
    )
    conn.execute(
        "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
        ("Test note", "info", "ai", "info")
    )
    conn.execute(
        "INSERT INTO files (path, language) VALUES (?, ?)",
        ("src/main.py", "Python")
    )
    conn.commit()
    conn.close()
    return db_path


def _create_old_prefs_db(aifp_dir, version="1.2"):
    """Create a user_preferences.db at current version (no migration needed)."""
    db_path = os.path.join(aifp_dir, "user_preferences.db")
    conn = sqlite3.connect(db_path)
    schema_path = _get_schema_path("user_preferences.sql")
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.close()
    return db_path


# ============================================================================
# _get_db_version Tests
# ============================================================================

def test_get_db_version_returns_version():
    tmp = tempfile.mkdtemp()
    try:
        aifp_dir = _setup_project(tmp)
        db_path = _create_old_project_db(aifp_dir, "1.6")
        assert _get_db_version(db_path) == "1.6"
    finally:
        shutil.rmtree(tmp)


def test_get_db_version_nonexistent_returns_default():
    assert _get_db_version("/nonexistent/path.db") == "0.0"


# ============================================================================
# _check_pending_migrations Tests
# ============================================================================

def test_check_pending_detects_old_version():
    tmp = tempfile.mkdtemp()
    try:
        aifp_dir = _setup_project(tmp)
        _create_old_project_db(aifp_dir, "1.6")
        _create_old_prefs_db(aifp_dir)

        result = _check_pending_migrations(tmp, ".aifp-project")
        assert result['checked'] is True
        # project.db should be pending (1.6 -> 1.7)
        pending_names = [p['db_name'] for p in result['pending']]
        assert 'project' in pending_names
        # user_preferences should be up_to_date (1.2 == 1.2)
        up_to_date_names = [u['db_name'] for u in result['up_to_date']]
        assert 'user_preferences' in up_to_date_names
    finally:
        shutil.rmtree(tmp)


def test_check_pending_skips_missing_db():
    tmp = tempfile.mkdtemp()
    try:
        aifp_dir = _setup_project(tmp)
        _create_old_project_db(aifp_dir, "1.6")
        # No user_preferences.db or user_directives.db

        result = _check_pending_migrations(tmp, ".aifp-project")
        assert result['checked'] is True
        skipped_names = [s['db_name'] for s in result['skipped']]
        # user_directives should be skipped (file missing)
        assert 'user_directives' in skipped_names
    finally:
        shutil.rmtree(tmp)


def test_check_pending_all_current():
    tmp = tempfile.mkdtemp()
    try:
        aifp_dir = _setup_project(tmp)
        # Create project.db at current version (1.7)
        db_path = os.path.join(aifp_dir, "project.db")
        conn = sqlite3.connect(db_path)
        schema_path = _get_schema_path("project.sql")
        with open(schema_path, 'r') as f:
            conn.executescript(f.read())
        conn.close()
        _create_old_prefs_db(aifp_dir)

        result = _check_pending_migrations(tmp, ".aifp-project")
        assert result['checked'] is True
        assert len(result['pending']) == 0
        up_to_date_names = [u['db_name'] for u in result['up_to_date']]
        assert 'project' in up_to_date_names
        assert 'user_preferences' in up_to_date_names
    finally:
        shutil.rmtree(tmp)


# ============================================================================
# migrate_databases Tests
# ============================================================================

def test_migrate_databases_nothing_pending():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp)
        # Create at current versions
        db_path = os.path.join(aifp_dir, "project.db")
        conn = sqlite3.connect(db_path)
        with open(_get_schema_path("project.sql"), 'r') as f:
            conn.executescript(f.read())
        conn.close()
        _create_old_prefs_db(aifp_dir)

        result = migrate_databases()
        assert result.success is True
        assert len(result.data['migrated']) == 0
        assert result.data['message'] == 'All databases up to date'
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)


def test_migrate_databases_upgrades_project():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp)
        _create_old_project_db(aifp_dir, "1.6")
        _create_old_prefs_db(aifp_dir)

        result = migrate_databases()
        assert result.success is True
        assert len(result.data['migrated']) == 1

        migrated = result.data['migrated'][0]
        assert migrated['db_name'] == 'project'
        assert migrated['old_version'] == '1.6'
        assert migrated['new_version'] == '1.8'
        assert migrated['backup_temp_path'] is not None
        assert migrated['new_db_temp_path'] is not None
        assert os.path.isfile(migrated['backup_temp_path'])
        assert os.path.isfile(migrated['new_db_temp_path'])

        # Cleanup temp files
        os.remove(migrated['backup_temp_path'])
        os.remove(migrated['new_db_temp_path'])
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)


def test_migrate_databases_preserves_data():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp)
        _create_old_project_db(aifp_dir, "1.6")
        _create_old_prefs_db(aifp_dir)

        result = migrate_databases()
        migrated = result.data['migrated'][0]

        # Verify data in new DB
        new_conn = sqlite3.connect(migrated['new_db_temp_path'])
        new_conn.row_factory = sqlite3.Row

        # Check project row
        cursor = new_conn.execute("SELECT name, purpose FROM project")
        row = cursor.fetchone()
        assert row['name'] == "TestProject"
        assert row['purpose'] == "Testing migration"

        # Check infrastructure row
        cursor = new_conn.execute("SELECT type, value FROM infrastructure WHERE type='language'")
        row = cursor.fetchone()
        assert row['value'] == "Python"

        # Check note
        cursor = new_conn.execute("SELECT content, note_type FROM notes WHERE content='Test note'")
        row = cursor.fetchone()
        assert row is not None
        assert row['note_type'] == "info"

        # Check file
        cursor = new_conn.execute("SELECT path FROM files WHERE path='src/main.py'")
        row = cursor.fetchone()
        assert row is not None

        # Check version is new
        cursor = new_conn.execute("SELECT version FROM schema_version")
        row = cursor.fetchone()
        assert row['version'] == "1.8"

        new_conn.close()

        # Cleanup
        os.remove(migrated['backup_temp_path'])
        os.remove(migrated['new_db_temp_path'])
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)


def test_migrate_databases_preserves_timestamps():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp)
        old_db_path = _create_old_project_db(aifp_dir, "1.6")

        # Read original timestamp
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
        cursor = old_conn.execute("SELECT created_at, updated_at FROM project LIMIT 1")
        old_row = cursor.fetchone()
        old_created = old_row['created_at']
        old_updated = old_row['updated_at']
        old_conn.close()

        _create_old_prefs_db(aifp_dir)

        result = migrate_databases()
        migrated = result.data['migrated'][0]

        # Verify timestamps preserved in new DB
        new_conn = sqlite3.connect(migrated['new_db_temp_path'])
        new_conn.row_factory = sqlite3.Row
        cursor = new_conn.execute("SELECT created_at, updated_at FROM project LIMIT 1")
        new_row = cursor.fetchone()
        assert new_row['created_at'] == old_created
        assert new_row['updated_at'] == old_updated
        new_conn.close()

        # Cleanup
        os.remove(migrated['backup_temp_path'])
        os.remove(migrated['new_db_temp_path'])
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)


def test_migrate_databases_verification_match():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp)
        _create_old_project_db(aifp_dir, "1.6")
        _create_old_prefs_db(aifp_dir)

        result = migrate_databases()
        migrated = result.data['migrated'][0]
        verification = migrated['verification']

        # All tables with data should show match=True
        for table, info in verification.items():
            assert info['match'] is True, f"Table {table}: {info}"

        # Verify specific tables have expected row counts
        assert verification['project']['old_rows'] == 1
        assert verification['infrastructure']['old_rows'] == 1
        assert verification['notes']['old_rows'] == 1
        assert verification['files']['old_rows'] == 1

        # Cleanup
        os.remove(migrated['backup_temp_path'])
        os.remove(migrated['new_db_temp_path'])
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)


def test_migrate_databases_backup_is_valid():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp)
        _create_old_project_db(aifp_dir, "1.6")
        _create_old_prefs_db(aifp_dir)

        result = migrate_databases()
        migrated = result.data['migrated'][0]

        # Backup should be a valid SQLite DB with old version
        backup_version = _get_db_version(migrated['backup_temp_path'])
        assert backup_version == "1.6"

        # Cleanup
        os.remove(migrated['backup_temp_path'])
        os.remove(migrated['new_db_temp_path'])
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)


def test_migrate_databases_custom_aifp_folder():
    tmp = tempfile.mkdtemp()
    try:
        set_project_root(tmp)
        aifp_dir = _setup_project(tmp, aifp_folder=".custom-aifp")
        _create_old_project_db(aifp_dir, "1.6")

        result = migrate_databases(aifp_folder=".custom-aifp")
        assert result.success is True
        assert len(result.data['migrated']) == 1
        assert result.data['migrated'][0]['db_name'] == 'project'

        # Cleanup
        for m in result.data['migrated']:
            if m.get('backup_temp_path'):
                os.remove(m['backup_temp_path'])
            if m.get('new_db_temp_path'):
                os.remove(m['new_db_temp_path'])
    finally:
        clear_project_root_cache()
        shutil.rmtree(tmp)

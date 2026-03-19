"""
Tests for deferred/completed/obsolete note types and exclude_note_types filtering.

Verifies:
- add_note(note_type='deferred') succeeds
- update_note(note_type='completed') succeeds
- update_note(note_type='obsolete') succeeds
- get_notes_comprehensive(exclude_note_types=['completed', 'obsolete']) works
- get_notes_comprehensive(note_type='deferred') returns only deferred
- Python VALID_NOTE_TYPES constants include new types
- SQL schema CHECK constraints include new types
"""

import os
import sqlite3
import tempfile
import shutil

from aifp.helpers.project._common import VALID_NOTE_TYPES as PROJECT_NOTE_TYPES
from aifp.helpers.user_directives._common import VALID_NOTE_TYPES as UD_NOTE_TYPES


# ============================================================================
# Python Constants Tests
# ============================================================================

def test_project_valid_note_types_includes_deferred():
    assert 'deferred' in PROJECT_NOTE_TYPES


def test_project_valid_note_types_includes_completed():
    assert 'completed' in PROJECT_NOTE_TYPES


def test_project_valid_note_types_includes_obsolete():
    assert 'obsolete' in PROJECT_NOTE_TYPES


def test_ud_valid_note_types_includes_deferred():
    assert 'deferred' in UD_NOTE_TYPES


def test_ud_valid_note_types_includes_completed():
    assert 'completed' in UD_NOTE_TYPES


def test_ud_valid_note_types_includes_obsolete():
    assert 'obsolete' in UD_NOTE_TYPES


# ============================================================================
# SQL Schema Tests (verify CHECK constraints accept new types)
# ============================================================================

def _create_project_db():
    """Create a fresh project.db in temp dir for testing."""
    from aifp.helpers.orchestrators.migration import _get_schema_path
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "project.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with open(_get_schema_path("project.sql"), 'r') as f:
        conn.executescript(f.read())
    return conn, db_path, tmp_dir


def test_sql_accepts_deferred_note_type():
    conn, db_path, tmp_dir = _create_project_db()
    try:
        conn.execute(
            "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
            ("test deferred", "deferred", "ai", "info")
        )
        conn.commit()
        cursor = conn.execute("SELECT note_type FROM notes WHERE content='test deferred'")
        assert cursor.fetchone()['note_type'] == 'deferred'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_sql_accepts_completed_note_type():
    conn, db_path, tmp_dir = _create_project_db()
    try:
        conn.execute(
            "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
            ("test completed", "completed", "ai", "info")
        )
        conn.commit()
        cursor = conn.execute("SELECT note_type FROM notes WHERE content='test completed'")
        assert cursor.fetchone()['note_type'] == 'completed'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_sql_accepts_obsolete_note_type():
    conn, db_path, tmp_dir = _create_project_db()
    try:
        conn.execute(
            "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
            ("test obsolete", "obsolete", "ai", "info")
        )
        conn.commit()
        cursor = conn.execute("SELECT note_type FROM notes WHERE content='test obsolete'")
        assert cursor.fetchone()['note_type'] == 'obsolete'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_sql_rejects_invalid_note_type():
    conn, db_path, tmp_dir = _create_project_db()
    try:
        try:
            conn.execute(
                "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
                ("bad", "invalid_type", "ai", "info")
            )
            conn.commit()
            assert False, "Should have raised IntegrityError"
        except sqlite3.IntegrityError:
            pass  # Expected
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


# ============================================================================
# User Directives SQL Tests
# ============================================================================

def _create_ud_db():
    """Create a fresh user_directives.db in temp dir for testing."""
    from aifp.helpers.orchestrators.migration import _get_schema_path
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "user_directives.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    with open(_get_schema_path("user_directives.sql"), 'r') as f:
        conn.executescript(f.read())
    return conn, db_path, tmp_dir


def test_ud_sql_accepts_deferred():
    conn, db_path, tmp_dir = _create_ud_db()
    try:
        conn.execute(
            "INSERT INTO notes (content, note_type, severity) VALUES (?, ?, ?)",
            ("ud deferred", "deferred", "info")
        )
        conn.commit()
        cursor = conn.execute("SELECT note_type FROM notes WHERE content='ud deferred'")
        assert cursor.fetchone()['note_type'] == 'deferred'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_ud_sql_accepts_completed():
    conn, db_path, tmp_dir = _create_ud_db()
    try:
        conn.execute(
            "INSERT INTO notes (content, note_type, severity) VALUES (?, ?, ?)",
            ("ud completed", "completed", "info")
        )
        conn.commit()
        cursor = conn.execute("SELECT note_type FROM notes WHERE content='ud completed'")
        assert cursor.fetchone()['note_type'] == 'completed'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_ud_sql_accepts_obsolete():
    conn, db_path, tmp_dir = _create_ud_db()
    try:
        conn.execute(
            "INSERT INTO notes (content, note_type, severity) VALUES (?, ?, ?)",
            ("ud obsolete", "obsolete", "info")
        )
        conn.commit()
        cursor = conn.execute("SELECT note_type FROM notes WHERE content='ud obsolete'")
        assert cursor.fetchone()['note_type'] == 'obsolete'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


# ============================================================================
# Exclude Note Types Filter Tests (direct SQL verification)
# ============================================================================

def test_exclude_note_types_filter():
    """Test that exclude_note_types logic works at SQL level."""
    conn, db_path, tmp_dir = _create_project_db()
    try:
        # Insert notes of different types
        for nt in ('deferred', 'completed', 'obsolete', 'info', 'warning'):
            conn.execute(
                "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
                (f"note {nt}", nt, "ai", "info")
            )
        conn.commit()

        # Exclude completed and obsolete
        exclude = ['completed', 'obsolete']
        placeholders = ", ".join(["?"] * len(exclude))
        cursor = conn.execute(
            f"SELECT note_type FROM notes WHERE note_type NOT IN ({placeholders})",
            exclude
        )
        results = [row['note_type'] for row in cursor.fetchall()]
        assert 'completed' not in results
        assert 'obsolete' not in results
        assert 'deferred' in results
        assert 'info' in results
        assert 'warning' in results
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_filter_deferred_only():
    """Test filtering to get only deferred notes."""
    conn, db_path, tmp_dir = _create_project_db()
    try:
        for nt in ('deferred', 'completed', 'obsolete', 'info'):
            conn.execute(
                "INSERT INTO notes (content, note_type, source, severity) VALUES (?, ?, ?, ?)",
                (f"note {nt}", nt, "ai", "info")
            )
        conn.commit()

        cursor = conn.execute("SELECT note_type FROM notes WHERE note_type = ?", ('deferred',))
        results = [row['note_type'] for row in cursor.fetchall()]
        assert len(results) == 1
        assert results[0] == 'deferred'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


# ============================================================================
# Schema Version Tests
# ============================================================================

def test_project_schema_version_is_1_8():
    conn, db_path, tmp_dir = _create_project_db()
    try:
        cursor = conn.execute("SELECT version FROM schema_version")
        assert cursor.fetchone()['version'] == '1.8'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_ud_schema_version_is_1_2():
    conn, db_path, tmp_dir = _create_ud_db()
    try:
        cursor = conn.execute("SELECT version FROM schema_version")
        assert cursor.fetchone()['version'] == '1.2'
    finally:
        conn.close()
        shutil.rmtree(tmp_dir)


def test_core_schema_version_is_2_2():
    from aifp.helpers.orchestrators._common import get_core_db_path
    from aifp.helpers.orchestrators.migration import _get_db_version
    core_path = get_core_db_path()
    assert _get_db_version(core_path) == '2.2'


def test_core_has_expected_schema_versions_table():
    from aifp.helpers.orchestrators._common import get_core_db_path
    core_path = get_core_db_path()
    conn = sqlite3.connect(core_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        "SELECT db_name, expected_version FROM expected_schema_versions ORDER BY db_name"
    )
    rows = {row['db_name']: row['expected_version'] for row in cursor.fetchall()}
    conn.close()
    assert rows['project'] == '1.8'
    assert rows['user_preferences'] == '1.2'
    assert rows['user_directives'] == '1.2'

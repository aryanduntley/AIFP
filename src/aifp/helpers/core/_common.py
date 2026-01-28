"""
AIFP Helper Functions - Core Common Utilities

Shared utilities used across core helper files.

This is the CATEGORY level of the DRY hierarchy:

    utils.py (global)            <- Database-agnostic shared code
        └── core/_common.py      <- THIS FILE: Core-specific shared code
            └── core/{file}.py   <- Individual core helpers

Core database characteristics:
- Read-only (immutable after MCP server installation)
- Global (same for all projects)
- Contains: directives, helpers, flows, categories, intent_keywords

Common utilities (core-specific):
- _get_core_connection: Open connection to core database
- Directive record conversion utilities
- Helper record conversion utilities
- Flow record conversion utilities

Imported from utils.py (global):
- _open_connection: Database connection with row factory
- get_core_db_path: Path to aifp_core.db
- get_return_statements: Fetch return statements
- Schema introspection utilities
- Row conversion utilities
- JSON parsing utilities
"""

import sqlite3
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any

# Import global utilities (DRY - avoid duplication)
from ..utils import (
    _open_connection,
    get_core_db_path,
    get_return_statements,
    database_exists,
    _get_table_names,
    _get_table_info,
    _get_table_sql,
    _parse_check_constraint,
    row_to_dict,
    rows_to_tuple,
    parse_json_field,
    json_to_tuple,
)

# Re-export for convenience
__all__ = [
    '_open_connection',
    'get_core_db_path',
    'get_return_statements',
    'database_exists',
    '_get_table_names',
    '_get_table_info',
    '_get_table_sql',
    '_parse_check_constraint',
    'row_to_dict',
    'rows_to_tuple',
    'parse_json_field',
    'json_to_tuple',
    '_get_core_connection',
    'DirectiveRecord',
    'HelperRecord',
    'FlowRecord',
    'CategoryRecord',
    'row_to_directive',
    'row_to_helper',
    'row_to_flow',
    'row_to_category',
]


# ============================================================================
# Core Database Connection
# ============================================================================

def _get_core_connection() -> sqlite3.Connection:
    """
    Effect: Open connection to core database.

    Convenience wrapper that combines get_core_db_path() and _open_connection().

    Returns:
        Database connection with row factory configured

    Raises:
        FileNotFoundError: If core database does not exist

    Example:
        >>> conn = _get_core_connection()
        >>> cursor = conn.execute("SELECT * FROM directives")
    """
    core_db = get_core_db_path()

    if not database_exists(core_db):
        raise FileNotFoundError(f"Core database not found: {core_db}")

    return _open_connection(core_db)


# ============================================================================
# Data Structures (Immutable)
# ============================================================================

@dataclass(frozen=True)
class DirectiveRecord:
    """Immutable directive record from database."""
    id: int
    name: str
    type: str
    workflow: Optional[str]
    description: Optional[str]
    category: Optional[str]  # Primary category name (from join)
    md_file_path: Optional[str]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class HelperRecord:
    """Immutable helper function record from database."""
    id: int
    name: str
    file_path: Optional[str]
    purpose: Optional[str]
    target_database: Optional[str]
    is_tool: bool
    is_sub_helper: bool
    parameters: Tuple[Dict[str, Any], ...]  # Parsed from JSON
    return_statements: Tuple[str, ...]  # Parsed from JSON
    implementation_notes: Tuple[str, ...]  # Parsed from JSON
    error_handling: Optional[str]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class FlowRecord:
    """Immutable directive flow record from database."""
    id: int
    from_directive: str
    to_directive: str
    flow_category: str
    flow_type: str
    condition_key: Optional[str]
    condition_value: Optional[str]
    condition_description: Optional[str]
    priority: int
    description: Optional[str]


@dataclass(frozen=True)
class CategoryRecord:
    """Immutable category record from database."""
    id: int
    name: str
    description: Optional[str]


@dataclass(frozen=True)
class IntentKeywordRecord:
    """Immutable intent keyword record from database."""
    id: int
    keyword: str


# ============================================================================
# Row Conversion Utilities
# ============================================================================

def row_to_directive(row: sqlite3.Row) -> DirectiveRecord:
    """
    Pure: Convert database row to immutable DirectiveRecord.

    Args:
        row: SQLite row object (must have directive columns)

    Returns:
        Immutable DirectiveRecord
    """
    return DirectiveRecord(
        id=row['id'],
        name=row['name'],
        type=row['type'],
        workflow=row['workflow'] if 'workflow' in row.keys() else None,
        description=row['description'] if 'description' in row.keys() else None,
        category=row['category'] if 'category' in row.keys() else None,
        md_file_path=row['md_file_path'] if 'md_file_path' in row.keys() else None,
        created_at=row['created_at'],
        updated_at=row['updated_at'],
    )


def row_to_helper(row: sqlite3.Row) -> HelperRecord:
    """
    Pure: Convert database row to immutable HelperRecord.

    Args:
        row: SQLite row object (must have helper_functions columns)

    Returns:
        Immutable HelperRecord
    """
    return HelperRecord(
        id=row['id'],
        name=row['name'],
        file_path=row['file_path'] if 'file_path' in row.keys() else None,
        purpose=row['purpose'] if 'purpose' in row.keys() else None,
        target_database=row['target_database'] if 'target_database' in row.keys() else None,
        is_tool=bool(row['is_tool']) if 'is_tool' in row.keys() else False,
        is_sub_helper=bool(row['is_sub_helper']) if 'is_sub_helper' in row.keys() else False,
        parameters=json_to_tuple(row['parameters']) if 'parameters' in row.keys() else (),
        return_statements=json_to_tuple(row['return_statements']) if 'return_statements' in row.keys() else (),
        implementation_notes=json_to_tuple(row['implementation_notes']) if 'implementation_notes' in row.keys() else (),
        error_handling=row['error_handling'] if 'error_handling' in row.keys() else None,
        created_at=row['created_at'],
        updated_at=row['updated_at'],
    )


def row_to_flow(row: sqlite3.Row) -> FlowRecord:
    """
    Pure: Convert database row to immutable FlowRecord.

    Args:
        row: SQLite row object (must have directive_flow columns)

    Returns:
        Immutable FlowRecord
    """
    return FlowRecord(
        id=row['id'],
        from_directive=row['from_directive'],
        to_directive=row['to_directive'],
        flow_category=row['flow_category'],
        flow_type=row['flow_type'],
        condition_key=row['condition_key'] if 'condition_key' in row.keys() else None,
        condition_value=row['condition_value'] if 'condition_value' in row.keys() else None,
        condition_description=row['condition_description'] if 'condition_description' in row.keys() else None,
        priority=row['priority'] if 'priority' in row.keys() else 0,
        description=row['description'] if 'description' in row.keys() else None,
    )


def row_to_category(row: sqlite3.Row) -> CategoryRecord:
    """
    Pure: Convert database row to immutable CategoryRecord.

    Args:
        row: SQLite row object (must have categories columns)

    Returns:
        Immutable CategoryRecord
    """
    return CategoryRecord(
        id=row['id'],
        name=row['name'],
        description=row['description'] if 'description' in row.keys() else None,
    )


def row_to_intent_keyword(row: sqlite3.Row) -> IntentKeywordRecord:
    """
    Pure: Convert database row to immutable IntentKeywordRecord.

    Args:
        row: SQLite row object (must have intent_keywords columns)

    Returns:
        Immutable IntentKeywordRecord
    """
    return IntentKeywordRecord(
        id=row['id'],
        keyword=row['keyword'],
    )

"""
AIFP Helper Utilities - Re-exports from Database Foundation Layer

This module re-exports everything from database/connection.py for
backward compatibility. All helper category files import from here.

DRY hierarchy:
    database/connection.py  (source of truth)
        └── helpers/utils.py (THIS FILE — re-exports)
            └── {category}/_common.py (category re-exports)
                └── {category}/{file}.py (individual helpers)

New code outside helpers/ should import directly from
aifp.database.connection instead of going through this file.
"""

# Re-export everything from the foundation layer
from ..database.connection import (
    # Constants
    AIFP_PROJECT_DIR,
    CORE_DB_NAME,
    PROJECT_DB_NAME,
    USER_PREFERENCES_DB_NAME,
    USER_DIRECTIVES_DB_NAME,
    MCP_RUNTIME_DB_NAME,
    # Result types
    Result,
    QueryResult,
    SchemaResult,
    # Path resolution — global
    get_core_db_path,
    get_mcp_runtime_db_path,
    # Path resolution — per-project
    get_aifp_project_dir,
    get_project_db_path,
    get_user_preferences_db_path,
    get_user_directives_db_path,
    database_exists,
    # Connection management
    _open_connection,
    _close_connection,
    _open_core_connection,
    _open_project_connection,
    _open_preferences_connection,
    _open_directives_connection,
    _open_mcp_runtime_connection,
    # Stateless query functions
    _effect_query_one,
    _effect_query_all,
    _effect_execute,
    # Row conversion
    row_to_dict,
    rows_to_tuple,
    # JSON parsing
    parse_json_field,
    json_to_tuple,
    # Schema introspection
    _get_table_names,
    _get_table_info,
    _get_table_sql,
    _parse_check_constraint,
    # Return statements
    get_return_statements,
)

__all__ = [
    # Constants
    'AIFP_PROJECT_DIR',
    'CORE_DB_NAME',
    'PROJECT_DB_NAME',
    'USER_PREFERENCES_DB_NAME',
    'USER_DIRECTIVES_DB_NAME',
    'MCP_RUNTIME_DB_NAME',
    # Result types
    'Result',
    'QueryResult',
    'SchemaResult',
    # Path resolution
    'get_core_db_path',
    'get_mcp_runtime_db_path',
    'get_aifp_project_dir',
    'get_project_db_path',
    'get_user_preferences_db_path',
    'get_user_directives_db_path',
    'database_exists',
    # Connection management
    '_open_connection',
    '_close_connection',
    '_open_core_connection',
    '_open_project_connection',
    '_open_preferences_connection',
    '_open_directives_connection',
    '_open_mcp_runtime_connection',
    # Stateless query functions
    '_effect_query_one',
    '_effect_query_all',
    '_effect_execute',
    # Row conversion
    'row_to_dict',
    'rows_to_tuple',
    # JSON parsing
    'parse_json_field',
    'json_to_tuple',
    # Schema introspection
    '_get_table_names',
    '_get_table_info',
    '_get_table_sql',
    '_parse_check_constraint',
    # Return statements
    'get_return_statements',
]

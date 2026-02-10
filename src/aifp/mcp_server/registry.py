"""
AIFP MCP Server - Tool Registry

Static dict mapping tool names to (module_path, function_name) tuples.
Uses importlib for lazy loading — modules are only imported on first call.

219 is_tool=true helpers registered. Generated from aifp_core.db.

Why static, not DB-driven:
- Predictable tool list, no runtime DB dependency for tool listing
- Easy to test and debug
- file_path field in DB uses relative paths that need prefix resolution
"""

import importlib
from typing import Final, Dict, Tuple, Callable, Any


# ============================================================================
# Tool Registry
# ============================================================================

# Maps tool_name -> (module_path, function_name)
# Module paths are fully qualified for importlib.import_module()
TOOL_REGISTRY: Final[Dict[str, Tuple[str, str]]] = {

    # ── Core: Directives ─────────────────────────────────────────────────
    # helpers/core/directives_1.py (12 tools)
    "find_directive_by_intent": ("aifp.helpers.core.directives_1", "find_directive_by_intent"),
    "get_all_directive_keywords": ("aifp.helpers.core.directives_1", "get_all_directive_keywords"),
    "get_all_directive_names": ("aifp.helpers.core.directives_1", "get_all_directive_names"),
    "get_all_directives": ("aifp.helpers.core.directives_1", "get_all_directives"),
    "get_all_intent_keywords_with_counts": ("aifp.helpers.core.directives_1", "get_all_intent_keywords_with_counts"),
    "get_directive_by_name": ("aifp.helpers.core.directives_1", "get_directive_by_name"),
    "get_directive_keywords": ("aifp.helpers.core.directives_1", "get_directive_keywords"),
    "get_directives_by_category": ("aifp.helpers.core.directives_1", "get_directives_by_category"),
    "get_directives_by_type": ("aifp.helpers.core.directives_1", "get_directives_by_type"),
    "get_directives_with_intent_keywords": ("aifp.helpers.core.directives_1", "get_directives_with_intent_keywords"),
    "get_fp_directive_index": ("aifp.helpers.core.directives_1", "get_fp_directive_index"),
    "search_directives": ("aifp.helpers.core.directives_1", "search_directives"),
    "find_directives_by_intent_keyword": ("aifp.helpers.core.directives_1", "find_directives_by_intent_keyword"),
    # helpers/core/directives_2.py (9 tools)
    "get_categories": ("aifp.helpers.core.directives_2", "get_categories"),
    "get_category_by_name": ("aifp.helpers.core.directives_2", "get_category_by_name"),
    "get_directives_for_helper": ("aifp.helpers.core.directives_2", "get_directives_for_helper"),
    "get_helper_by_name": ("aifp.helpers.core.directives_2", "get_helper_by_name"),
    "get_helpers_are_sub": ("aifp.helpers.core.directives_2", "get_helpers_are_sub"),
    "get_helpers_are_tool": ("aifp.helpers.core.directives_2", "get_helpers_are_tool"),
    "get_helpers_by_database": ("aifp.helpers.core.directives_2", "get_helpers_by_database"),
    "get_helpers_for_directive": ("aifp.helpers.core.directives_2", "get_helpers_for_directive"),
    "get_helpers_not_tool_not_sub": ("aifp.helpers.core.directives_2", "get_helpers_not_tool_not_sub"),

    # ── Core: Flows ──────────────────────────────────────────────────────
    # helpers/core/flows.py (5 tools)
    "get_completion_loop_target": ("aifp.helpers.core.flows", "get_completion_loop_target"),
    "get_directive_flows": ("aifp.helpers.core.flows", "get_directive_flows"),
    "get_flows_from_directive": ("aifp.helpers.core.flows", "get_flows_from_directive"),
    "get_flows_to_directive": ("aifp.helpers.core.flows", "get_flows_to_directive"),
    "get_wildcard_flows": ("aifp.helpers.core.flows", "get_wildcard_flows"),

    # ── Core: Schema & Validation ────────────────────────────────────────
    # helpers/core/schema.py (6 tools)
    "get_core_fields": ("aifp.helpers.core.schema", "get_core_fields"),
    "get_core_schema": ("aifp.helpers.core.schema", "get_core_schema"),
    "get_core_tables": ("aifp.helpers.core.schema", "get_core_tables"),
    "get_from_core": ("aifp.helpers.core.schema", "get_from_core"),
    "get_from_core_where": ("aifp.helpers.core.schema", "get_from_core_where"),
    "query_core": ("aifp.helpers.core.schema", "query_core"),
    # helpers/core/validation.py (1 tool)
    "core_allowed_check_constraints": ("aifp.helpers.core.validation", "core_allowed_check_constraints"),

    # ── Git ──────────────────────────────────────────────────────────────
    # helpers/git/operations.py (7 tools)
    "create_user_branch": ("aifp.helpers.git.operations", "create_user_branch"),
    "detect_conflicts_before_merge": ("aifp.helpers.git.operations", "detect_conflicts_before_merge"),
    "detect_external_changes": ("aifp.helpers.git.operations", "detect_external_changes"),
    "execute_merge": ("aifp.helpers.git.operations", "execute_merge"),
    "get_git_status": ("aifp.helpers.git.operations", "get_git_status"),
    "list_active_branches": ("aifp.helpers.git.operations", "list_active_branches"),
    "sync_git_state": ("aifp.helpers.git.operations", "sync_git_state"),
    "get_current_commit_hash": ("aifp.helpers.git.operations", "get_current_commit_hash"),
    "get_current_branch": ("aifp.helpers.git.operations", "get_current_branch"),

    # ── Orchestrators ────────────────────────────────────────────────────
    # helpers/orchestrators/entry_points.py (4 tools)
    "aifp_end": ("aifp.helpers.orchestrators.entry_points", "aifp_end"),
    "aifp_init": ("aifp.helpers.orchestrators.entry_points", "aifp_init"),
    "aifp_run": ("aifp.helpers.orchestrators.entry_points", "aifp_run"),
    "aifp_status": ("aifp.helpers.orchestrators.entry_points", "aifp_status"),
    # helpers/orchestrators/query.py (1 tool)
    "query_project_state": ("aifp.helpers.orchestrators.query", "query_project_state"),
    "get_files_by_flow_context": ("aifp.helpers.orchestrators.query", "get_files_by_flow_context"),
    # helpers/orchestrators/state.py (3 tools)
    "batch_update_progress": ("aifp.helpers.orchestrators.state", "batch_update_progress"),
    "get_current_progress": ("aifp.helpers.orchestrators.state", "get_current_progress"),
    "update_project_state": ("aifp.helpers.orchestrators.state", "update_project_state"),
    # helpers/orchestrators/status.py (1 tool)
    "get_task_context": ("aifp.helpers.orchestrators.status", "get_task_context"),

    # ── Project: CRUD ────────────────────────────────────────────────────
    # helpers/project/crud.py (7 tools)
    "add_project_entry": ("aifp.helpers.project.crud", "add_project_entry"),
    "delete_project_entry": ("aifp.helpers.project.crud", "delete_project_entry"),
    "delete_reserved": ("aifp.helpers.project.crud", "delete_reserved"),
    "get_from_project": ("aifp.helpers.project.crud", "get_from_project"),
    "get_from_project_where": ("aifp.helpers.project.crud", "get_from_project_where"),
    "query_project": ("aifp.helpers.project.crud", "query_project"),
    "update_project_entry": ("aifp.helpers.project.crud", "update_project_entry"),

    # ── Project: Files ───────────────────────────────────────────────────
    # helpers/project/files_1.py (6 tools)
    "finalize_file": ("aifp.helpers.project.files_1", "finalize_file"),
    "finalize_files": ("aifp.helpers.project.files_1", "finalize_files"),
    "get_file_by_name": ("aifp.helpers.project.files_1", "get_file_by_name"),
    "get_file_by_path": ("aifp.helpers.project.files_1", "get_file_by_path"),
    "reserve_file": ("aifp.helpers.project.files_1", "reserve_file"),
    "reserve_files": ("aifp.helpers.project.files_1", "reserve_files"),
    # helpers/project/files_2.py (3 tools)
    "delete_file": ("aifp.helpers.project.files_2", "delete_file"),
    "file_has_changed": ("aifp.helpers.project.files_2", "file_has_changed"),
    "update_file": ("aifp.helpers.project.files_2", "update_file"),

    # ── Project: Functions ───────────────────────────────────────────────
    # helpers/project/functions_1.py (5 tools)
    "finalize_function": ("aifp.helpers.project.functions_1", "finalize_function"),
    "finalize_functions": ("aifp.helpers.project.functions_1", "finalize_functions"),
    "get_function_by_name": ("aifp.helpers.project.functions_1", "get_function_by_name"),
    "reserve_function": ("aifp.helpers.project.functions_1", "reserve_function"),
    "reserve_functions": ("aifp.helpers.project.functions_1", "reserve_functions"),
    # helpers/project/functions_2.py (4 tools)
    "delete_function": ("aifp.helpers.project.functions_2", "delete_function"),
    "get_functions_by_file": ("aifp.helpers.project.functions_2", "get_functions_by_file"),
    "update_function": ("aifp.helpers.project.functions_2", "update_function"),
    "update_functions_for_file": ("aifp.helpers.project.functions_2", "update_functions_for_file"),
    "update_function_file_location": ("aifp.helpers.project.functions_2", "update_function_file_location"),

    # ── Project: Interactions ────────────────────────────────────────────
    # helpers/project/interactions.py (3 tools)
    "add_interaction": ("aifp.helpers.project.interactions", "add_interaction"),
    "add_interactions": ("aifp.helpers.project.interactions", "add_interactions"),
    "update_interaction": ("aifp.helpers.project.interactions", "update_interaction"),
    "delete_interaction": ("aifp.helpers.project.interactions", "delete_interaction"),

    # ── Project: Items & Notes ───────────────────────────────────────────
    # helpers/project/items_notes.py (9 tools)
    "add_note": ("aifp.helpers.project.items_notes", "add_note"),
    "delete_item": ("aifp.helpers.project.items_notes", "delete_item"),
    "get_incomplete_items": ("aifp.helpers.project.items_notes", "get_incomplete_items"),
    "get_items_for_sidequest": ("aifp.helpers.project.items_notes", "get_items_for_sidequest"),
    "get_items_for_subtask": ("aifp.helpers.project.items_notes", "get_items_for_subtask"),
    "get_items_for_task": ("aifp.helpers.project.items_notes", "get_items_for_task"),
    "get_notes_comprehensive": ("aifp.helpers.project.items_notes", "get_notes_comprehensive"),
    "search_notes": ("aifp.helpers.project.items_notes", "search_notes"),
    "update_note": ("aifp.helpers.project.items_notes", "update_note"),
    "delete_note": ("aifp.helpers.project.items_notes", "delete_note"),

    # ── Project: Metadata ────────────────────────────────────────────────
    # helpers/project/metadata.py (10 tools)
    "blueprint_has_changed": ("aifp.helpers.project.metadata", "blueprint_has_changed"),
    "create_project": ("aifp.helpers.project.metadata", "create_project"),
    "get_all_infrastructure": ("aifp.helpers.project.metadata", "get_all_infrastructure"),
    "get_infrastructure_by_type": ("aifp.helpers.project.metadata", "get_infrastructure_by_type"),
    "get_project": ("aifp.helpers.project.metadata", "get_project"),
    "get_project_root": ("aifp.helpers.project.metadata", "get_project_root"),
    "get_source_directory": ("aifp.helpers.project.metadata", "get_source_directory"),
    "update_project": ("aifp.helpers.project.metadata", "update_project"),
    "update_project_root": ("aifp.helpers.project.metadata", "update_project_root"),
    "update_source_directory": ("aifp.helpers.project.metadata", "update_source_directory"),

    # ── Project: Schema & Validation ─────────────────────────────────────
    # helpers/project/schema.py (4 tools)
    "get_project_fields": ("aifp.helpers.project.schema", "get_project_fields"),
    "get_project_json_parameters": ("aifp.helpers.project.schema", "get_project_json_parameters"),
    "get_project_schema": ("aifp.helpers.project.schema", "get_project_schema"),
    "get_project_tables": ("aifp.helpers.project.schema", "get_project_tables"),
    # helpers/project/state_db.py (1 tool)
    "create_state_database": ("aifp.helpers.project.state_db", "create_state_database"),
    # helpers/project/validation.py (1 tool)
    "project_allowed_check_constraints": ("aifp.helpers.project.validation", "project_allowed_check_constraints"),

    # ── Project: Subtasks & Sidequests ───────────────────────────────────
    # helpers/project/subtasks_sidequests.py (14 tools)
    "add_sidequest": ("aifp.helpers.project.subtasks_sidequests", "add_sidequest"),
    "add_subtask": ("aifp.helpers.project.subtasks_sidequests", "add_subtask"),
    "delete_sidequest": ("aifp.helpers.project.subtasks_sidequests", "delete_sidequest"),
    "delete_subtask": ("aifp.helpers.project.subtasks_sidequests", "delete_subtask"),
    "get_incomplete_sidequests": ("aifp.helpers.project.subtasks_sidequests", "get_incomplete_sidequests"),
    "get_incomplete_subtasks": ("aifp.helpers.project.subtasks_sidequests", "get_incomplete_subtasks"),
    "get_incomplete_subtasks_by_task": ("aifp.helpers.project.subtasks_sidequests", "get_incomplete_subtasks_by_task"),
    "get_sidequest_files": ("aifp.helpers.project.subtasks_sidequests", "get_sidequest_files"),
    "get_sidequest_flows": ("aifp.helpers.project.subtasks_sidequests", "get_sidequest_flows"),
    "get_sidequests_comprehensive": ("aifp.helpers.project.subtasks_sidequests", "get_sidequests_comprehensive"),
    "get_subtasks_by_task": ("aifp.helpers.project.subtasks_sidequests", "get_subtasks_by_task"),
    "get_subtasks_comprehensive": ("aifp.helpers.project.subtasks_sidequests", "get_subtasks_comprehensive"),
    "update_sidequest": ("aifp.helpers.project.subtasks_sidequests", "update_sidequest"),
    "update_subtask": ("aifp.helpers.project.subtasks_sidequests", "update_subtask"),

    # ── Project: Tasks & Milestones ──────────────────────────────────────
    # helpers/project/tasks.py (15 tools)
    "add_milestone": ("aifp.helpers.project.tasks", "add_milestone"),
    "add_task": ("aifp.helpers.project.tasks", "add_task"),
    "delete_milestone": ("aifp.helpers.project.tasks", "delete_milestone"),
    "delete_task": ("aifp.helpers.project.tasks", "delete_task"),
    "get_incomplete_milestones": ("aifp.helpers.project.tasks", "get_incomplete_milestones"),
    "get_incomplete_tasks": ("aifp.helpers.project.tasks", "get_incomplete_tasks"),
    "get_incomplete_tasks_by_milestone": ("aifp.helpers.project.tasks", "get_incomplete_tasks_by_milestone"),
    "get_milestones_by_path": ("aifp.helpers.project.tasks", "get_milestones_by_path"),
    "get_milestones_by_status": ("aifp.helpers.project.tasks", "get_milestones_by_status"),
    "get_task_files": ("aifp.helpers.project.tasks", "get_task_files"),
    "get_task_flows": ("aifp.helpers.project.tasks", "get_task_flows"),
    "get_tasks_by_milestone": ("aifp.helpers.project.tasks", "get_tasks_by_milestone"),
    "get_tasks_comprehensive": ("aifp.helpers.project.tasks", "get_tasks_comprehensive"),
    "update_milestone": ("aifp.helpers.project.tasks", "update_milestone"),
    "update_task": ("aifp.helpers.project.tasks", "update_task"),

    # ── Project: Themes & Flows ──────────────────────────────────────────
    # helpers/project/themes_flows_1.py (11 tools)
    "add_flow": ("aifp.helpers.project.themes_flows_1", "add_flow"),
    "add_theme": ("aifp.helpers.project.themes_flows_1", "add_theme"),
    "delete_flow": ("aifp.helpers.project.themes_flows_1", "delete_flow"),
    "delete_theme": ("aifp.helpers.project.themes_flows_1", "delete_theme"),
    "get_all_flows": ("aifp.helpers.project.themes_flows_1", "get_all_flows"),
    "get_all_themes": ("aifp.helpers.project.themes_flows_1", "get_all_themes"),
    "get_file_ids_from_flows": ("aifp.helpers.project.themes_flows_1", "get_file_ids_from_flows"),
    "get_flow_by_name": ("aifp.helpers.project.themes_flows_1", "get_flow_by_name"),
    "get_theme_by_name": ("aifp.helpers.project.themes_flows_1", "get_theme_by_name"),
    "update_flow": ("aifp.helpers.project.themes_flows_1", "update_flow"),
    "update_theme": ("aifp.helpers.project.themes_flows_1", "update_theme"),
    # helpers/project/themes_flows_2.py (11 tools)
    "add_completion_path": ("aifp.helpers.project.themes_flows_2", "add_completion_path"),
    "delete_completion_path": ("aifp.helpers.project.themes_flows_2", "delete_completion_path"),
    "get_all_completion_paths": ("aifp.helpers.project.themes_flows_2", "get_all_completion_paths"),
    "get_completion_paths_by_status": ("aifp.helpers.project.themes_flows_2", "get_completion_paths_by_status"),
    "get_files_by_flow": ("aifp.helpers.project.themes_flows_2", "get_files_by_flow"),
    "get_flows_for_file": ("aifp.helpers.project.themes_flows_2", "get_flows_for_file"),
    "get_flows_for_theme": ("aifp.helpers.project.themes_flows_2", "get_flows_for_theme"),
    "get_incomplete_completion_paths": ("aifp.helpers.project.themes_flows_2", "get_incomplete_completion_paths"),
    "get_next_completion_path": ("aifp.helpers.project.themes_flows_2", "get_next_completion_path"),
    "get_themes_for_flow": ("aifp.helpers.project.themes_flows_2", "get_themes_for_flow"),
    "update_completion_path": ("aifp.helpers.project.themes_flows_2", "update_completion_path"),
    "reorder_completion_path": ("aifp.helpers.project.themes_flows_2", "reorder_completion_path"),
    "reorder_all_completion_paths": ("aifp.helpers.project.themes_flows_2", "reorder_all_completion_paths"),
    "swap_completion_paths_order": ("aifp.helpers.project.themes_flows_2", "swap_completion_paths_order"),

    # ── Project: Types ───────────────────────────────────────────────────
    # helpers/project/types_1.py (7 tools)
    "delete_type": ("aifp.helpers.project.types_1", "delete_type"),
    "finalize_type": ("aifp.helpers.project.types_1", "finalize_type"),
    "finalize_types": ("aifp.helpers.project.types_1", "finalize_types"),
    "get_type_by_name": ("aifp.helpers.project.types_1", "get_type_by_name"),
    "reserve_type": ("aifp.helpers.project.types_1", "reserve_type"),
    "reserve_types": ("aifp.helpers.project.types_1", "reserve_types"),
    "update_type": ("aifp.helpers.project.types_1", "update_type"),
    # helpers/project/types_2.py (3 tools)
    "add_types_functions": ("aifp.helpers.project.types_2", "add_types_functions"),
    "update_type_function_role": ("aifp.helpers.project.types_2", "update_type_function_role"),
    "delete_type_function": ("aifp.helpers.project.types_2", "delete_type_function"),

    # ── Shared ───────────────────────────────────────────────────────────
    # helpers/shared/database_info.py (1 tool)
    "get_databases": ("aifp.helpers.shared.database_info", "get_databases"),
    # helpers/shared/supportive_context.py (1 tool)
    "get_supportive_context": ("aifp.helpers.shared.supportive_context", "get_supportive_context"),

    # ── User Directives ──────────────────────────────────────────────────
    # helpers/user_directives/crud.py (8 tools)
    "add_user_custom_entry": ("aifp.helpers.user_directives.crud", "add_user_custom_entry"),
    "delete_user_custom_entry": ("aifp.helpers.user_directives.crud", "delete_user_custom_entry"),
    "get_active_user_directives": ("aifp.helpers.user_directives.crud", "get_active_user_directives"),
    "get_from_user_custom": ("aifp.helpers.user_directives.crud", "get_from_user_custom"),
    "get_from_user_custom_where": ("aifp.helpers.user_directives.crud", "get_from_user_custom_where"),
    "query_user_custom": ("aifp.helpers.user_directives.crud", "query_user_custom"),
    "search_user_directives": ("aifp.helpers.user_directives.crud", "search_user_directives"),
    "update_user_custom_entry": ("aifp.helpers.user_directives.crud", "update_user_custom_entry"),
    # helpers/user_directives/management.py (7 tools)
    "activate_user_directive": ("aifp.helpers.user_directives.management", "activate_user_directive"),
    "init_user_directives_db": ("aifp.helpers.user_directives.management", "init_user_directives_db"),
    "add_user_directive_note": ("aifp.helpers.user_directives.management", "add_user_directive_note"),
    "deactivate_user_directive": ("aifp.helpers.user_directives.management", "deactivate_user_directive"),
    "get_user_directive_by_name": ("aifp.helpers.user_directives.management", "get_user_directive_by_name"),
    "get_user_directive_notes": ("aifp.helpers.user_directives.management", "get_user_directive_notes"),
    "search_user_directive_notes": ("aifp.helpers.user_directives.management", "search_user_directive_notes"),
    # helpers/user_directives/schema.py (4 tools)
    "get_user_custom_fields": ("aifp.helpers.user_directives.schema", "get_user_custom_fields"),
    "get_user_custom_json_parameters": ("aifp.helpers.user_directives.schema", "get_user_custom_json_parameters"),
    "get_user_custom_schema": ("aifp.helpers.user_directives.schema", "get_user_custom_schema"),
    "get_user_custom_tables": ("aifp.helpers.user_directives.schema", "get_user_custom_tables"),
    # helpers/user_directives/validation.py (1 tool)
    "user_directives_allowed_check_constraints": ("aifp.helpers.user_directives.validation", "user_directives_allowed_check_constraints"),

    # ── User Preferences ─────────────────────────────────────────────────
    # helpers/user_preferences/crud.py (6 tools)
    "add_settings_entry": ("aifp.helpers.user_preferences.crud", "add_settings_entry"),
    "delete_settings_entry": ("aifp.helpers.user_preferences.crud", "delete_settings_entry"),
    "get_from_settings": ("aifp.helpers.user_preferences.crud", "get_from_settings"),
    "get_from_settings_where": ("aifp.helpers.user_preferences.crud", "get_from_settings_where"),
    "query_settings": ("aifp.helpers.user_preferences.crud", "query_settings"),
    "update_settings_entry": ("aifp.helpers.user_preferences.crud", "update_settings_entry"),
    # helpers/user_preferences/management.py (14 tools)
    "add_directive_preference": ("aifp.helpers.user_preferences.management", "add_directive_preference"),
    "add_tracking_note": ("aifp.helpers.user_preferences.management", "add_tracking_note"),
    "add_user_setting": ("aifp.helpers.user_preferences.management", "add_user_setting"),
    "delete_custom_return_statement": ("aifp.helpers.user_preferences.management", "delete_custom_return_statement"),
    "get_tracking_notes": ("aifp.helpers.user_preferences.management", "get_tracking_notes"),
    "get_tracking_settings": ("aifp.helpers.user_preferences.management", "get_tracking_settings"),
    "get_user_setting": ("aifp.helpers.user_preferences.management", "get_user_setting"),
    "get_user_settings": ("aifp.helpers.user_preferences.management", "get_user_settings"),
    "load_directive_preferences": ("aifp.helpers.user_preferences.management", "load_directive_preferences"),
    "search_tracking_notes": ("aifp.helpers.user_preferences.management", "search_tracking_notes"),
    "set_custom_return_statement": ("aifp.helpers.user_preferences.management", "set_custom_return_statement"),
    "toggle_tracking_feature": ("aifp.helpers.user_preferences.management", "toggle_tracking_feature"),
    "update_directive_preference": ("aifp.helpers.user_preferences.management", "update_directive_preference"),
    "update_user_setting": ("aifp.helpers.user_preferences.management", "update_user_setting"),
    # helpers/user_preferences/schema.py (4 tools)
    "get_settings_fields": ("aifp.helpers.user_preferences.schema", "get_settings_fields"),
    "get_settings_json_parameters": ("aifp.helpers.user_preferences.schema", "get_settings_json_parameters"),
    "get_settings_schema": ("aifp.helpers.user_preferences.schema", "get_settings_schema"),
    "get_settings_tables": ("aifp.helpers.user_preferences.schema", "get_settings_tables"),
    # helpers/user_preferences/validation.py (1 tool)
    "user_preferences_allowed_check_constraints": ("aifp.helpers.user_preferences.validation", "user_preferences_allowed_check_constraints"),
}


# ============================================================================
# Pure Functions
# ============================================================================

def is_registered_tool(tool_name: str) -> bool:
    """Pure: Check if a tool name exists in the registry."""
    return tool_name in TOOL_REGISTRY


def get_registry_entry(tool_name: str) -> Tuple[str, str]:
    """
    Pure: Get the (module_path, function_name) for a registered tool.

    Args:
        tool_name: Tool name to look up

    Returns:
        Tuple of (module_path, function_name)

    Raises:
        KeyError: If tool_name is not registered
    """
    return TOOL_REGISTRY[tool_name]


# ============================================================================
# Effect Functions
# ============================================================================

def _effect_import_tool_function(tool_name: str) -> Callable[..., Any]:
    """
    Effect: Lazy import a tool's function via importlib.

    Python caches modules after first import, so subsequent calls
    for the same module are instant.

    Args:
        tool_name: Registered tool name

    Returns:
        The callable helper function

    Raises:
        KeyError: If tool_name not in registry
        ImportError: If module cannot be imported
        AttributeError: If function not found in module
    """
    module_path, function_name = TOOL_REGISTRY[tool_name]
    module = importlib.import_module(module_path)
    return getattr(module, function_name)

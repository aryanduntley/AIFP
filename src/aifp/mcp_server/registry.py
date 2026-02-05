"""
AIFP MCP Server - Tool Registry

Static dict mapping tool names to (module_path, function_name) tuples.
Uses importlib for lazy loading — modules are only imported on first call.

Milestone 1: Entry points only (4 tools).
Milestone 2: All 204 is_tool=true helpers.

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
    # Entry Points (orchestrators/entry_points.py)
    "aifp_init": ("aifp.helpers.orchestrators.entry_points", "aifp_init"),
    "aifp_status": ("aifp.helpers.orchestrators.entry_points", "aifp_status"),
    "aifp_run": ("aifp.helpers.orchestrators.entry_points", "aifp_run"),
    "aifp_end": ("aifp.helpers.orchestrators.entry_points", "aifp_end"),
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

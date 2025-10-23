# AIFP Helper Functions Reference

## Overview

This document provides a centralized reference for all helper functions used across the AIFP system. Helper functions are utility functions called by directives to perform specific operations on the AIFP databases and project files.

**Note**: These functions are **to be implemented**. This document serves as a specification and centralized reference point for development.

---

## Organization

Helper functions are organized by the database schema they primarily operate on:

1. **MCP Database Helpers** (`aifp_core.db`) - Read-only operations on directive metadata
2. **Project Database Helpers** (`project.db`) - Read/write operations on project state
3. **User Preferences Helpers** (`user_preferences.db`) - User customization management
4. **User Directives Helpers** (`user_directives.db`) - User-defined directive automation

---

## MCP Database Helpers (aifp_core.db)

**Database**: `aifp_core.db` (global, read-only)
**Purpose**: Access directive definitions, helper metadata, and tool mappings

### get_all_directives()

**File Path**: `helpers/mcp/get_all_directives.py`

**Parameters**: None

**Purpose**: Retrieve all directives from aifp_core.db with self-assessment questions. Returns approximately 89 directives (FP + Project + User System) for AI context loading.

**Returns**:
```python
{
    "directives": [
        {
            "id": int,
            "name": str,
            "type": str,  # 'fp' or 'project'
            "level": int,
            "description": str,
            "workflow": dict,
            "intent_keywords": list[str],
            "confidence_threshold": float
        },
        ...
    ],
    "self_assessment_questions": dict
}
```

**Error Handling**: Return empty list and prompt user if database inaccessible.

**Used By**: `aifp_run`, AI session initialization

---

### get_directive(name)

**File Path**: `helpers/mcp/get_directive.py`

**Parameters**:
- `name` (str) - Directive name (e.g., 'aifp_run', 'fp_purity')

**Purpose**: Retrieve specific directive details by name.

**Returns**: Single directive dict or None if not found

**Error Handling**: Return None and log warning if directive not found.

**Used By**: Directive lookup during execution

---

### search_directives(keyword, category, type)

**File Path**: `helpers/mcp/search_directives.py`

**Parameters**:
- `keyword` (str, optional) - Search in name, description, intent_keywords
- `category` (str, optional) - Filter by category (e.g., 'purity', 'task_management')
- `type` (str, optional) - Filter by type ('fp' or 'project')

**Purpose**: Search and filter directives based on criteria.

**Returns**: List of matching directives sorted by relevance

**Error Handling**: Return empty list if no matches, log search failure.

**Used By**: Directive discovery, intent matching

---

### find_directive_by_intent(user_request, confidence_threshold)

**File Path**: `helpers/mcp/find_directive_by_intent.py`

**Parameters**:
- `user_request` (str) - User's natural language request
- `confidence_threshold` (float) - Minimum confidence (0-1) for match

**Purpose**: Map user requests to directives using intent_keywords_json and description matching. Returns ranked list with confidence scores.

**Returns**:
```python
[
    {
        "directive": dict,
        "confidence": float,
        "matched_keywords": list[str]
    },
    ...
]
```

**Error Handling**: On failure or no matches, prompt user to manually select from available directives. Optionally log to user_preferences.db if helper_function_logging enabled.

**Used By**: `aifp_run`, user preference mapping

---

### query_mcp_db(sql)

**File Path**: `helpers/mcp/query_mcp_db.py`

**Parameters**:
- `sql` (str) - SQL query string

**Purpose**: Execute read-only SQL queries on aifp_core.db. **Use as last resort** when no appropriate helper exists.

**Returns**: Query results as list of dicts

**Error Handling**: Validate SQL is read-only (SELECT only), reject write operations. Log errors and return empty list.

**Used By**: Advanced directive queries

---

## Project Database Helpers (project.db)

**Database**: `project.db` (per-project, mutable)
**Purpose**: Manage project state, files, tasks, and code tracking

### init_project_db(name, purpose, goals_json, project_id)

**File Path**: `helpers/project/init_project_db.py`

**Parameters**:
- `name` (str) - Project name
- `purpose` (str) - Project purpose description
- `goals_json` (str) - JSON array of project goals
- `project_id` (int) - Project ID

**Purpose**: Create project.db and initialize the project table with default schemas. Sets up initial completion path stages.

**Returns**: Success boolean and database path

**Error Handling**: On failure, prompt user for manual setup. Optionally log to user_preferences.db if helper_function_logging enabled.

**Used By**: `project_init` directive

---

### get_project_status()

**File Path**: `helpers/project/get_project_status.py`

**Parameters**: None

**Purpose**: Check if project is initialized by verifying .aifp/ folder and project.db exist and contain valid data.

**Returns**:
```python
{
    "initialized": bool,
    "project_name": str,
    "status": str,  # 'active', 'paused', 'completed'
    "version": int,
    "user_directives_status": str  # NULL, 'in_progress', 'active', 'disabled'
}
```

**Error Handling**: Return `{"initialized": false}` if project not found.

**Used By**: `aifp_run`, `aifp_status`, `project_init`

---

### get_project_context(type)

**File Path**: `helpers/project/get_project_context.py`

**Parameters**:
- `type` (str) - Context type: 'overview', 'files', 'tasks', 'themes', 'all'

**Purpose**: Retrieve structured project overview from project.db for AI context loading.

**Returns**: Dict with requested context sections

**Error Handling**: Return partial context with error note if some tables inaccessible.

**Used By**: Session initialization, `aifp_status`

---

### get_project_files(language)

**File Path**: `helpers/project/get_project_files.py`

**Parameters**:
- `language` (str, optional) - Filter by language (e.g., 'Python', 'JavaScript')

**Purpose**: List all files tracked in project.db, optionally filtered by language.

**Returns**: List of file dicts with path, language, checksum

**Error Handling**: Return empty list if no files found, log database errors.

**Used By**: File management directives, code analysis

---

### get_project_functions(file_id)

**File Path**: `helpers/project/get_project_functions.py`

**Parameters**:
- `file_id` (int, optional) - Filter by file ID, or get all if None

**Purpose**: List functions tracked in project.db.

**Returns**: List of function dicts with name, purpose, purity_level, parameters

**Error Handling**: Return empty list if no functions found.

**Used By**: Code analysis, FP compliance checking

---

### get_project_tasks(status)

**File Path**: `helpers/project/get_project_tasks.py`

**Parameters**:
- `status` (str, optional) - Filter by status: 'pending', 'in_progress', 'completed'

**Purpose**: List tasks and subtasks from project.db.

**Returns**: Hierarchical dict of tasks with milestones and completion paths

**Error Handling**: Return empty list if no tasks found.

**Used By**: `aifp_status`, task management directives

---

### get_status_tree(project_id, context_limit)

**File Path**: `helpers/project/get_status_tree.py`

**Parameters**:
- `project_id` (int) - Project ID
- `context_limit` (int, optional, default=10) - Number of previous items to include for historical context

**Purpose**: Build hierarchical status tree with historical context for task continuation. Priority order: sidequests → subtasks → tasks.

**Returns**:
```python
{
    "priority": str,  # 'sidequest', 'subtask', 'task', or None
    "current": {
        "id": int,
        "name": str,
        "status": str,
        "items": list[dict]
    },
    "parent": dict or None,
    "historical_context": list[dict],  # Previous task items for context
    "ambiguities": list[str]
}
```

**Error Handling**: Return `{"priority": None, "message": "No open tasks"}` if no work items.

**Used By**: `aifp_status` directive

---

### create_project_blueprint(project_name, project_purpose, goals_json, language, build_tool, fp_strictness_level)

**File Path**: `helpers/project/create_project_blueprint.py`

**Parameters**:
- `project_name` (str)
- `project_purpose` (str)
- `goals_json` (str) - JSON array
- `language` (str)
- `build_tool` (str)
- `fp_strictness_level` (str) - 'strict', 'standard', or 'relaxed'

**Purpose**: Generate ProjectBlueprint.md from template and user input. Creates `.aifp/ProjectBlueprint.md` and backs up to `.aifp/backups/`.

**Returns**: Path to created ProjectBlueprint.md

**Error Handling**: On failure, prompt user for manual creation.

**Used By**: `project_init` directive

---

### read_project_blueprint(blueprint_path)

**File Path**: `helpers/project/read_project_blueprint.py`

**Parameters**:
- `blueprint_path` (str, optional, default='.aifp/ProjectBlueprint.md')

**Purpose**: Parse ProjectBlueprint.md and return structured data (name, version, goals, themes, flows, completion path).

**Returns**:
```python
{
    "name": str,
    "version": int,
    "status": str,
    "aifp_compliance": str,
    "overview": dict,
    "technical": dict,
    "themes": list[dict],
    "flows": list[dict],
    "completion_path": list[dict]
}
```

**Error Handling**: Fall back to database if blueprint file missing. Warn user about blueprint/DB desync if checksum mismatch.

**Used By**: `aifp_status`, `project_evolution`

---

### update_project_blueprint_section(section_number, section_content, increment_version)

**File Path**: `helpers/project/update_project_blueprint_section.py`

**Parameters**:
- `section_number` (int) - Section to update (1-7)
- `section_content` (str) - New section markdown content
- `increment_version` (bool, optional, default=True)

**Purpose**: Update specific section of ProjectBlueprint.md, backup current version, optionally increment project version and add evolution history entry.

**Returns**: Success boolean

**Error Handling**: Restore from backup on write failure and prompt user.

**Used By**: `project_evolution`, `project_blueprint_update`

---

### query_project_db(sql)

**File Path**: `helpers/project/query_project_db.py`

**Parameters**:
- `sql` (str) - SQL query string

**Purpose**: Execute SQL queries on project.db. **Use as last resort** when no appropriate helper exists.

**Returns**: Query results as list of dicts

**Error Handling**: Validate SQL safety, reject dangerous operations. Log errors.

**Used By**: Advanced project queries

---

## User Preferences Helpers (user_preferences.db)

**Database**: `user_preferences.db` (per-project, mutable)
**Purpose**: Manage user customizations and tracking preferences

### get_directive_preference(directive_name, preference_key)

**File Path**: `helpers/preferences/get_directive_preference.py`

**Parameters**:
- `directive_name` (str) - Directive name
- `preference_key` (str) - Preference key

**Purpose**: Retrieve user preference override for specific directive.

**Returns**: Preference value (str) or None if not set

**Error Handling**: Return None if preference not found.

**Used By**: All directives that support user overrides

---

### set_directive_preference(directive_name, preference_key, preference_value)

**File Path**: `helpers/preferences/set_directive_preference.py`

**Parameters**:
- `directive_name` (str)
- `preference_key` (str)
- `preference_value` (str)

**Purpose**: Set user preference override for directive behavior.

**Returns**: Success boolean

**Error Handling**: Prompt user if invalid value.

**Used By**: `user_preferences_set` directive

---

### get_tracking_settings()

**File Path**: `helpers/preferences/get_tracking_settings.py`

**Parameters**: None

**Purpose**: Retrieve all tracking feature flags (fp_flow_tracking, issue_reports, ai_interaction_log, helper_function_logging).

**Returns**: Dict of feature flags and their enabled/disabled status

**Error Handling**: Return all features as disabled if table empty.

**Used By**: Tracking-related directives

---

### toggle_tracking_feature(feature_name, enabled)

**File Path**: `helpers/preferences/toggle_tracking_feature.py`

**Parameters**:
- `feature_name` (str) - Feature to toggle
- `enabled` (bool) - Enable or disable

**Purpose**: Toggle tracking features on/off. Shows estimated token overhead before enabling.

**Returns**: Success boolean and token cost estimate

**Error Handling**: Warn user about cost implications before enabling.

**Used By**: `user_preferences_tracking_toggle` directive

---

## User Directives Helpers (user_directives.db)

**Database**: `user_directives.db` (per-project, optional)
**Purpose**: Manage user-defined automation directives

### parse_directive_file(file_path, file_format)

**File Path**: `helpers/user_directives/parse_directive_file.py`

**Parameters**:
- `file_path` (str) - Path to directive file
- `file_format` (str) - Format: 'yaml', 'json', or 'txt'

**Purpose**: Parse user directive file and extract directives with ambiguity detection. Identifies missing parameters, unclear triggers, and required dependencies.

**Returns**:
```python
{
    "directives": list[dict],
    "ambiguities": list[dict],
    "dependencies": list[dict],
    "parse_errors": list[str]
}
```

**Error Handling**: Log parse errors to `.aifp/logs/errors/` and prompt user for manual correction.

**Used By**: `user_directive_parse` directive

---

### validate_user_directive(directive, interactive)

**File Path**: `helpers/user_directives/validate_user_directive.py`

**Parameters**:
- `directive` (dict) - Parsed directive
- `interactive` (bool) - Enable interactive Q&A

**Purpose**: Validate directive through interactive Q&A to resolve ambiguities. Presents clarifying questions, stores answers, and generates validated configuration.

**Returns**:
```python
{
    "validated_content": dict,
    "validation_questions": list[dict],
    "validation_answers": list[dict],
    "remaining_ambiguities": list[dict]
}
```

**Error Handling**: Log validation errors and retry with simpler questions.

**Used By**: `user_directive_validate` directive

---

### generate_implementation_code(directive, template)

**File Path**: `helpers/user_directives/generate_implementation_code.py`

**Parameters**:
- `directive` (dict) - Validated directive
- `template` (str) - Code template type: 'scheduler', 'service', 'event_handler', 'function'

**Purpose**: Generate FP-compliant implementation code from directive and template. Applies FP directives for purity, immutability, and side effect isolation.

**Returns**:
```python
{
    "code": str,
    "file_path": str,
    "function_name": str,
    "implementation_type": str
}
```

**Error Handling**: Log generation errors and rollback any partial writes.

**Used By**: `user_directive_implement` directive

---

### detect_dependencies(directive)

**File Path**: `helpers/user_directives/detect_dependencies.py`

**Parameters**:
- `directive` (dict) - Validated directive

**Purpose**: Detect required dependencies (Python packages, APIs, environment variables) from directive configuration.

**Returns**:
```python
[
    {
        "type": str,  # 'package', 'api', 'env_var'
        "name": str,
        "version": str,
        "required": bool,
        "reason": str
    },
    ...
]
```

**Error Handling**: Return empty list on error, log warning.

**Used By**: `user_directive_implement` directive

---

### install_dependency(package, version, prompt_user)

**File Path**: `helpers/user_directives/install_dependency.py`

**Parameters**:
- `package` (str) - Package name
- `version` (str, optional) - Version specifier
- `prompt_user` (bool) - Ask user for confirmation

**Purpose**: Install Python package dependency with user confirmation. Updates directive_dependencies table with installation status.

**Returns**:
```python
{
    "success": bool,
    "installed_version": str,
    "error": str or None
}
```

**Error Handling**: Log installation errors to `.aifp/logs/errors/` and mark dependency as failed in user_directives.db.

**Used By**: `user_directive_implement` directive

---

### activate_directive(directive_id)

**File Path**: `helpers/user_directives/activate_directive.py`

**Parameters**:
- `directive_id` (int) - Directive ID

**Purpose**: Deploy and activate directive implementation for real-time execution. Starts schedulers, background services, or event handlers. Initializes logging and execution tracking.

**Returns**:
```python
{
    "success": bool,
    "process_id": int or None,
    "next_execution_time": str or None,
    "error": str or None
}
```

**Error Handling**: Rollback activation, stop any started services, log error.

**Used By**: `user_directive_activate` directive

---

### monitor_directive_execution(directive_id)

**File Path**: `helpers/user_directives/monitor_directive_execution.py`

**Parameters**:
- `directive_id` (int) - Directive ID

**Purpose**: Track directive execution statistics, rotate logs, and handle errors. Monitors running services, checks health, and maintains execution/error counts.

**Returns**:
```python
{
    "status": str,
    "total_executions": int,
    "success_count": int,
    "error_count": int,
    "last_execution_time": str,
    "avg_execution_time_ms": float,
    "health": str  # 'healthy', 'degraded', 'failed'
}
```

**Error Handling**: Log monitoring errors but continue monitoring (resilient design).

**Used By**: `user_directive_monitor` directive

---

### get_user_directive_status()

**File Path**: `helpers/user_directives/get_user_directive_status.py`

**Parameters**: None

**Purpose**: Build comprehensive status report for all user directives with execution statistics, active/paused/error counts, and log paths.

**Returns**:
```python
{
    "summary": {
        "total": int,
        "active": int,
        "paused": int,
        "error": int,
        "pending_validation": int
    },
    "directives": list[dict],
    "log_paths": dict
}
```

**Error Handling**: Return partial status with error note if full status cannot be retrieved.

**Used By**: `user_directive_status`, `aifp_status`

---

### update_directive(directive_id, changes)

**File Path**: `helpers/user_directives/update_directive.py`

**Parameters**:
- `directive_id` (int) - Directive ID
- `changes` (dict) - Detected changes from source file

**Purpose**: Handle directive updates when source file changes. Re-parses, re-validates, and re-implements. Deactivates if active, resets approval status.

**Returns**:
```python
{
    "success": bool,
    "re_validated": bool,
    "re_implemented": bool,
    "requires_approval": bool,
    "error": str or None
}
```

**Error Handling**: Rollback to previous version and reactivate old implementation on failure.

**Used By**: `user_directive_update` directive

---

### deactivate_directive(directive_id)

**File Path**: `helpers/user_directives/deactivate_directive.py`

**Parameters**:
- `directive_id` (int) - Directive ID

**Purpose**: Stop directive execution and clean up resources. Gracefully stops services (SIGTERM), force kills if necessary (SIGKILL). Preserves execution statistics.

**Returns**:
```python
{
    "success": bool,
    "stopped_gracefully": bool,
    "forced_kill": bool,
    "error": str or None
}
```

**Error Handling**: Force kill processes if graceful shutdown fails.

**Used By**: `user_directive_deactivate` directive

---

## Implementation Status

❌ **Not yet implemented** - All helper functions in this document are specifications for future development.

---

## Helper Function Development Guidelines

### 1. File Organization

```
helpers/
├── mcp/                          # MCP database helpers
│   ├── get_all_directives.py
│   ├── get_directive.py
│   ├── search_directives.py
│   ├── find_directive_by_intent.py
│   └── query_mcp_db.py
├── project/                      # Project database helpers
│   ├── init_project_db.py
│   ├── get_project_status.py
│   ├── get_project_context.py
│   ├── get_project_files.py
│   ├── get_project_functions.py
│   ├── get_project_tasks.py
│   ├── get_status_tree.py
│   ├── create_project_blueprint.py
│   ├── read_project_blueprint.py
│   ├── update_project_blueprint_section.py
│   └── query_project_db.py
├── preferences/                  # User preferences helpers
│   ├── get_directive_preference.py
│   ├── set_directive_preference.py
│   ├── get_tracking_settings.py
│   └── toggle_tracking_feature.py
└── user_directives/              # User directives helpers
    ├── parse_directive_file.py
    ├── validate_user_directive.py
    ├── generate_implementation_code.py
    ├── detect_dependencies.py
    ├── install_dependency.py
    ├── activate_directive.py
    ├── monitor_directive_execution.py
    ├── get_user_directive_status.py
    ├── update_directive.py
    └── deactivate_directive.py
```

### 2. Function Structure

All helper functions should follow this structure:

```python
"""
Helper: [function_name]
Database: [database_name]
Purpose: [brief description]
"""

from typing import [types]
import logging

logger = logging.getLogger(__name__)

def function_name(param1: type, param2: type = default) -> return_type:
    """
    [Detailed description]

    Args:
        param1: [description]
        param2: [description]

    Returns:
        [description of return value]

    Raises:
        [exceptions if any]
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"[function_name] error: {e}")
        # Error handling per specification
        return error_response
```

### 3. Error Handling Standards

- **Log all errors** to appropriate destination (file or db based on spec)
- **Return safe defaults** instead of raising exceptions when possible
- **Prompt user** for unrecoverable errors
- **Include context** in error messages (what operation, which data)

### 4. Testing Requirements

Each helper function should have:
- Unit tests with mocked database
- Integration tests with actual test database
- Error case tests (missing files, invalid data, etc.)

---

## Usage by Directives

| Helper Function | Primary Directive(s) |
|----------------|---------------------|
| `get_all_directives` | `aifp_run`, session initialization |
| `get_directive` | All directives (lookup) |
| `search_directives` | Intent detection |
| `find_directive_by_intent` | `aifp_run`, user preference mapping |
| `init_project_db` | `project_init` |
| `get_project_status` | `aifp_run`, `aifp_status`, `project_init` |
| `get_project_context` | Session initialization |
| `get_status_tree` | `aifp_status` |
| `create_project_blueprint` | `project_init` |
| `read_project_blueprint` | `aifp_status`, `project_evolution` |
| `update_project_blueprint_section` | `project_evolution`, `project_blueprint_update` |
| `parse_directive_file` | `user_directive_parse` |
| `validate_user_directive` | `user_directive_validate` |
| `generate_implementation_code` | `user_directive_implement` |
| `activate_directive` | `user_directive_activate` |
| `monitor_directive_execution` | `user_directive_monitor` |
| `get_user_directive_status` | `user_directive_status`, `aifp_status` |
| `update_directive` | `user_directive_update` |
| `deactivate_directive` | `user_directive_deactivate` |

---

## Next Steps

1. **Prioritize implementation** based on directive dependencies
2. **Create helper function issues** in project tracker
3. **Implement in phases**:
   - Phase 1: MCP database helpers (core functionality)
   - Phase 2: Project database helpers (project management)
   - Phase 3: User directives helpers (automation system)
   - Phase 4: User preferences helpers (customization)
4. **Write tests** for each helper as implemented
5. **Update this document** as helpers are built and signatures evolve

---

## Version History

- **v1.0** (2025-10-22): Initial comprehensive reference document

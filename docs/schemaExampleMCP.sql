-- aifp_core.db Schema
-- Version: 1.2

CREATE TABLE IF NOT EXISTS directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'aifp_run', 'init_project'
    description TEXT,
    workflow JSON NOT NULL,  -- JSON with steps/branches
    md_file_path TEXT,  -- e.g., 'directives/aifp_run.md'
    roadblocks_json TEXT,  -- JSON array of issues/resolutions
    confidence_threshold REAL DEFAULT 0.5;  -- 0-1, for intent matching
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Master 'aifp_run' directive
INSERT INTO directives (name, description, workflow, md_file_path, roadblocks_json)
VALUES (
    'aifp_run',
    'Master directive: Maps user input to specific directives',
    '{
        "trunk": "parse_intent",
        "branches": [
            {"if": "contains create project|initialize", "then": "init_project", "details": {"prompt_for_name": true, "prompt_for_goals": true}},
            {"if": "contains create file|write file", "then": "file_write", "details": {"require_metadata": true}},
            {"if": "contains update db|database", "then": "update_db", "details": {"helper": "track_file_creation"}},
            {"if": "contains verify|check compliance", "then": "compliance_check", "details": {"check_oop": true}},
            {"fallback": "prompt_user", "details": {"log_note": true, "reference_table": "notes", "type": "clarification"}}
        ],
        "error_handling": {"on_failure": "prompt user for clarification", "retry": "max 2 attempts"}
    }',
    'directives/aifp_run.md',
    '[{"issue": "ambiguous intent", "resolution": "Prompt user for clarification and log in notes table"}, {"issue": "missing project details", "resolution": "Request name/purpose from user"}]'
);

-- Sample 'init_project' directive
INSERT INTO directives (name, description, workflow, md_file_path, roadblocks_json)
VALUES (
    'init_project',
    'Initialize a new project with scaffolding and DB',
    '{
        "trunk": "create_project",
        "branches": [
            {"if": "project_name_missing", "then": "prompt_user", "details": {"field": "name"}},
            {"if": "project_purpose_missing", "then": "prompt_user", "details": {"field": "purpose"}},
            {"then": "create_project_db", "details": {"schema": "project_db_schema.sql"}},
            {"then": "scaffold_folder", "details": {"folder": ".aifp-project"}},
            {"then": "update_db", "details": {"helper": "init_project_db"}}
        ],
        "error_handling": {"on_failure": "log to notes table and prompt user", "retry": "max 1 attempt"}
    }',
    'directives/init_project.md',
    '[{"issue": "DB creation failed", "resolution": "Check MCP server permissions, retry, then prompt user"}]'
);

-- Sample 'task_decomposition' directive
INSERT INTO directives (name, description, workflow, md_file_path, roadblocks_json, intent_keywords_json, confidence_threshold)
VALUES (
    'task_decomposition',
    'Break user tasks into AIFP-compliant paths, handling tasks, subtasks, and sidequests',
    '{
        "trunk": "review_open_tasks",
        "branches": [
            {"if": "related_to_open_task", "then": "update_if_needed", "details": {"check_alignment": true}},
            {"if": "new_task_needed", "then": "create_new_task", "details": {"link_to_completion_path": true, "update_project_version": true}},
            {"if": "subtask_needed", "then": "create_subtask", "details": {"table": "subtasks", "priority": "high", "pause_parent_task": true}},
            {"if": "sidequest_needed", "then": "create_sidequest", "details": {"table": "sidequests", "priority": "low", "link_to_project": true}},
            {"if": "interruption_detected", "then": "handle_subtask_priority", "details": {"notify_user": true, "options": "complete/discard/resume", "check_table": "subtasks"}},
            {"fallback": "prompt_user", "details": {"clarify": "Is this a new task, subtask, or sidequest?"}},
            {"parallel": ["execute_code_gen", "update_db"], "details": {"if_code_and_db": true}}
        ],
        "error_handling": {"on_failure": "prompt user for clarification", "retry": "max 2 attempts"}
    }',
    'directives/task_decomposition.md',
    '[{"issue": "task vs subtask vs sidequest ambiguity", "resolution": "Prompt user for clarification, log in notes"}, {"issue": "no matching open task", "resolution": "Create new task or sidequest, align to completion_path"}]',
    '["decompose task", "break down", "plan steps", "explore"]',
    0.5
);

CREATE TABLE IF NOT EXISTS helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'init_project_db'
    file_path TEXT,  -- e.g., 'helpers/init_project_db.py'
    parameters JSON,  -- e.g., '["name", "purpose", "goals_json"]'
    purpose TEXT,
    error_handling TEXT,  -- e.g., 'Log to notes table and escalate to user'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sample 'init_project_db' helper
INSERT INTO helper_functions (name, file_path, parameters, purpose, error_handling)
VALUES (
    'init_project_db',
    'helpers/init_project_db.py',
    '["name", "purpose", "goals_json", "project_id"]',
    'Create project.db and initialize project table',
    'On failure, log to notes table and prompt user for manual setup'
);

CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'aifp_run_tool'
    maps_to_directive_id INTEGER,  -- FK to directives.id
    description TEXT,
    FOREIGN KEY (maps_to_directive_id) REFERENCES directives(id)
);

-- Sample tool
INSERT INTO tools (name, maps_to_directive_id, description)
VALUES (
    'aifp_run_tool',
    (SELECT id FROM directives WHERE name = 'aifp_run'),
    'Entry point for aifp run command, maps to aifp_run directive'
);

CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    reference_table TEXT,  -- e.g., 'directives'
    reference_id INTEGER,
    ai_generated BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
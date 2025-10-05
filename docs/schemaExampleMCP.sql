-- Directives Table: Core workflows with JSON steps
CREATE TABLE directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'aifp run'
    description TEXT,
    workflow JSON NOT NULL,  -- JSON with steps/branches
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sample 'aifp run'
INSERT INTO directives (name, description, workflow)
VALUES (
    'aifp run',
    'Master AIFP workflow: branches to coding or state management',
    '{
        "trunk": "init_check",
        "branches": [
            {"if": "coding_needed", "then": "apply_aifp_style", "details": {"pure_functions": true, "wrap_oop": true}},
            {"if": "state_update_needed", "then": "update_project_db", "details": {"parse_files": true, "associate_flows": true}},
            {"fallback": "log_note", "details": {"reference_table": "items", "type": "clarification"}}
        ],
        "error_handling": {"on_failure": "CALL helper_log_error(:step, :error_message)", "retry": "max 2 attempts"}
    }'
);

-- Helper Functions Table: Python utilities
CREATE TABLE helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'parse_functions'
    file_path TEXT,  -- Path to Python file in MCP
    parameters JSON,  -- e.g., '["file_path", "language"]'
    purpose TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Commands Table: Shortcodes mapping to directives/helpers
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shortcode TEXT NOT NULL UNIQUE,  -- e.g., 'AIFP init'
    maps_to_directive_id INTEGER,  -- Nullable FK
    maps_to_helper_id INTEGER,  -- Nullable FK
    description TEXT,
    FOREIGN KEY (maps_to_directive_id) REFERENCES directives(id),
    FOREIGN KEY (maps_to_helper_id) REFERENCES helper_functions(id)
);

-- Tools Table: External integrations
CREATE TABLE tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,  -- e.g., 'ast_parser'
    type TEXT,  -- e.g., 'language_specific'
    config JSON,  -- e.g., '{"languages": ["python", "js"]}'
    description TEXT
);

-- Notes Table: Clarifications for MCP entities
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    reference_table TEXT,  -- e.g., 'directives', 'commands'
    reference_id INTEGER,  -- FK to referenced table's id
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
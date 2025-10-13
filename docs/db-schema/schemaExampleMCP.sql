-- aifp_core.db Schema
-- Version: 1.3
-- Purpose: Defines MCP-level directives (read-only), helper functions, and tools
-- This database is immutable once deployed; AI reads it but never modifies it.

CREATE TABLE IF NOT EXISTS directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                      -- e.g., 'aifp_run', 'init_project'
    type TEXT NOT NULL,                             -- 'fp' or 'project'
    level INTEGER DEFAULT NULL,                     -- 0–4 for 'project' directives only
    parent_directive TEXT REFERENCES directives(name), -- Optional link for hierarchy
    description TEXT,
    workflow JSON NOT NULL,                         -- JSON with trunk/branches/error_handling
    md_file_path TEXT,                              -- e.g., 'directives/aifp_run.md'
    roadblocks_json TEXT,                           -- JSON array of issues/resolutions
    intent_keywords_json TEXT,                      -- Optional keywords for intent detection
    confidence_threshold REAL DEFAULT 0.5,           -- 0–1 threshold for matching/escalation
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================================
-- Categories and Directive-Category Linking
-- ===============================================================

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                       -- e.g., 'purity', 'immutability', 'task_management'
    description TEXT,                                -- Optional human-readable explanation
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Linking Table (many-to-many)
CREATE TABLE IF NOT EXISTS directive_categories (
    directive_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (directive_id, category_id),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Enforce that FP directives cannot have level values
CREATE TRIGGER IF NOT EXISTS enforce_level_on_fp
BEFORE INSERT ON directives
FOR EACH ROW
WHEN NEW.type = 'fp' AND NEW.level IS NOT NULL
BEGIN
    SELECT RAISE(ABORT, 'FP directives cannot have a level value.');
END;

CREATE TABLE IF NOT EXISTS directives_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Foreign key references to directives table
    source_directive_id INTEGER NOT NULL,
    target_directive_id INTEGER NOT NULL,

    -- Defines how these two directives are related
    relation_type TEXT NOT NULL CHECK (relation_type IN (
        'triggers',        -- source calls or activates target
        'depends_on',      -- source relies on data or state from target
        'escalates_to',    -- source delegates upward to target for resolution
        'cross_link',      -- bidirectional or contextual connection
        'fp_reference'     -- source calls or enforces an FP directive
    )),

    -- Optional hierarchy weight (used for sorting or graph traversal)
    weight INTEGER DEFAULT 1,

    -- Descriptive notes about the connection
    description TEXT,

    -- For internal reasoning or graph traversal
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_directive_id) REFERENCES directives(id),
    FOREIGN KEY (target_directive_id) REFERENCES directives(id)
);

CREATE INDEX IF NOT EXISTS idx_interactions_source ON directives_interactions (source_directive_id);
CREATE INDEX IF NOT EXISTS idx_interactions_target ON directives_interactions (target_directive_id);
CREATE INDEX IF NOT EXISTS idx_interactions_relation_type ON directives_interactions (relation_type);


-- ===============================================================
-- Sample Directive Entries
-- ===============================================================

-- Level 0: Root Orchestrator
INSERT INTO directives (name, type, level, description, workflow, md_file_path, roadblocks_json)
VALUES (
    'aifp_run',
    'project',
    0,
    'Master directive: Parses user intent and routes to the correct sub-directive.',
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
    '[{"issue": "ambiguous intent", "resolution": "Prompt user and log in notes"}, {"issue": "missing project details", "resolution": "Request name and purpose"}]'
);

-- Level 1: Project Initialization
INSERT INTO directives (name, type, level, parent_directive, description, workflow, md_file_path, roadblocks_json)
VALUES (
    'init_project',
    'project',
    1,
    'aifp_run',
    'Initializes a new AIFP project with scaffolding and SQLite DB.',
    '{
        "trunk": "create_project",
        "branches": [
            {"if": "project_name_missing", "then": "prompt_user", "details": {"field": "name"}},
            {"if": "project_purpose_missing", "then": "prompt_user", "details": {"field": "purpose"}},
            {"then": "create_project_db", "details": {"schema": "project_db_schema.sql"}},
            {"then": "scaffold_folder", "details": {"folder": ".aifp-project"}},
            {"then": "update_db", "details": {"helper": "init_project_db"}}
        ],
        "error_handling": {"on_failure": "log_to_notes_and_prompt_user", "retry": "max 1 attempt"}
    }',
    'directives/init_project.md',
    '[{"issue": "db_creation_failed", "resolution": "Check MCP permissions and retry"}]'
);

-- Level 2: Task Management
INSERT INTO directives (name, type, level, parent_directive, description, workflow, md_file_path, roadblocks_json, intent_keywords_json, confidence_threshold)
VALUES (
    'project_task_decomposition',
    'project',
    2,
    'aifp_run',
    'Breaks complex user goals into AIFP-aligned milestones, tasks, subtasks, and sidequests.',
    '{
        "trunk": "review_open_tasks",
        "branches": [
            {"if": "related_to_open_task", "then": "update_if_needed", "details": {"check_alignment": true, "update_completion_path": true}},
            {"if": "new_task_detected", "then": "create_task", "details": {"link_to_milestone": true, "update_project_version": true}},
            {"if": "subtask_needed", "then": "create_subtask", "details": {"pause_parent": true, "priority": "high", "add_to_items": true}},
            {"if": "sidequest_detected", "then": "create_sidequest", "details": {"pause_task": true, "priority": "low", "reason_required": true}},
            {"if": "interruption_detected", "then": "prompt_resume", "details": {"message": "Subtask in progress — complete, discard, or resume?"}},
            {"parallel": ["update_db", "update_notes"], "details": {"sync": "atomic"}},
            {"fallback": "prompt_user", "details": {"clarify": "New task or continuation?", "log_note": true}}
        ],
        "error_handling": {"on_failure": "prompt_user_for_guidance", "retry": "max 2 attempts"}
    }',
    'directives/project_task_decomposition.md',
    '[{"issue": "ambiguous_task_boundary", "resolution": "Prompt user and log"}, {"issue": "roadmap_misalignment", "resolution": "Update completion_path or flag for review"}]',
    '["decompose task", "plan steps", "continue work"]',
    0.6
);

-- ===============================================================
-- Helper Functions (used by directives)
-- ===============================================================

CREATE TABLE IF NOT EXISTS helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,               -- e.g., 'init_project_db'
    file_path TEXT,                          -- e.g., 'helpers/init_project_db.py'
    parameters JSON,                         -- e.g., '["name", "purpose", "goals_json"]'
    purpose TEXT,
    error_handling TEXT,                     -- e.g., 'Prompt user; optionally log to user_preferences.db if helper_function_logging enabled'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO helper_functions (name, file_path, parameters, purpose, error_handling)
VALUES (
    'init_project_db',
    'helpers/init_project_db.py',
    '["name", "purpose", "goals_json", "project_id"]',
    'Create project.db and initialize the project table with default schemas.',
    'On failure, prompt user for manual setup; optionally log to user_preferences.db if helper_function_logging enabled.'
);

INSERT INTO helper_functions (name, file_path, parameters, purpose, error_handling)
VALUES (
    'find_directive_by_intent',
    'helpers/find_directive_by_intent.py',
    '["user_request", "confidence_threshold"]',
    'Searches directives table by name, description, and intent_keywords_json to map user preference requests to specific directives. Returns list of matching directives with confidence scores sorted by relevance.',
    'On failure or no matches, prompt user to manually select directive from available options; optionally log to user_preferences.db if helper_function_logging enabled.'
);

-- ===============================================================
-- Tools: Mapping MCP tools to Directives
-- ===============================================================

CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,               -- e.g., 'aifp_run_tool'
    maps_to_directive_id INTEGER,            -- FK to directives.id
    description TEXT,
    FOREIGN KEY (maps_to_directive_id) REFERENCES directives(id)
);

INSERT INTO tools (name, maps_to_directive_id, description)
VALUES (
    'aifp_run_tool',
    (SELECT id FROM directives WHERE name = 'aifp_run'),
    'Entry point for aifp run command, maps to the aifp_run directive.'
);

-- ===============================================================
-- Schema Version Tracking
-- ===============================================================

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),      -- Only one row allowed
    version TEXT NOT NULL,                      -- e.g., '1.0'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (id, version) VALUES (1, '1.0');

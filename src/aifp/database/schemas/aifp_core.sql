-- aifp_core.db Schema
-- Version: 1.6
-- Purpose: Defines MCP-level directives (read-only) and helper functions
-- This database is immutable once deployed; AI reads it but never modifies it.

CREATE TABLE IF NOT EXISTS directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                      -- e.g., 'aifp_run', 'init_project'
    type TEXT NOT NULL CHECK (type IN ('fp', 'project', 'git', 'user_system', 'user_preference')),
    level INTEGER DEFAULT NULL,                     -- 0–4 for 'project' directives only
    parent_directive TEXT REFERENCES directives(name), -- Optional link for hierarchy
    description TEXT,
    workflow JSON NOT NULL,                         -- JSON with trunk/branches/error_handling
    md_file_path TEXT,                              -- e.g., 'directives/aifp_run.md'
    roadblocks_json TEXT,                           -- JSON array of issues/resolutions
    intent_keywords_json TEXT,                      -- Optional keywords for intent detection
    confidence_threshold REAL DEFAULT 0.5           -- 0–1 threshold for matching/escalation
);

-- ===============================================================
-- Categories and Directive-Category Linking
-- ===============================================================

-- Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                       -- e.g., 'purity', 'immutability', 'task_management'
    description TEXT                                 -- Optional human-readable explanation
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

-- ===============================================================
-- Directive Interactions
-- ===============================================================

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

    FOREIGN KEY (source_directive_id) REFERENCES directives(id),
    FOREIGN KEY (target_directive_id) REFERENCES directives(id)
);

CREATE INDEX IF NOT EXISTS idx_interactions_source ON directives_interactions (source_directive_id);
CREATE INDEX IF NOT EXISTS idx_interactions_target ON directives_interactions (target_directive_id);
CREATE INDEX IF NOT EXISTS idx_interactions_relation_type ON directives_interactions (relation_type);

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
    is_tool BOOLEAN DEFAULT 0,               -- TRUE if exposed as MCP tool (AI can call directly via MCP)
    is_sub_helper BOOLEAN DEFAULT 0,         -- TRUE if sub-helper (only called by other helpers, no directive mapping)
    return_statements JSON,                  -- JSON array of guidance/suggestions for AI after execution
    target_database TEXT                     -- 'core', 'project', 'user_preferences', 'user_directives' - which database this helper operates on
);

-- ===============================================================
-- Directive-Helper Mapping: Many-to-many relationship
-- ===============================================================

CREATE TABLE IF NOT EXISTS directive_helpers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,
    helper_function_id INTEGER NOT NULL,
    execution_context TEXT,                  -- e.g., 'workflow_step_3', 'error_handler', 'validation'
    sequence_order INTEGER DEFAULT 0,        -- Order of execution if multiple helpers in workflow
    is_required BOOLEAN DEFAULT 1,           -- TRUE if helper must execute, FALSE if optional/conditional
    parameters_mapping JSON,                 -- Optional: maps directive workflow params to helper params
    description TEXT,                        -- Brief note on why this helper is used
    UNIQUE(directive_id, helper_function_id, execution_context),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (helper_function_id) REFERENCES helper_functions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_directive_helpers_directive ON directive_helpers (directive_id);
CREATE INDEX IF NOT EXISTS idx_directive_helpers_helper ON directive_helpers (helper_function_id);

-- ===============================================================
-- Schema Version Tracking
-- ===============================================================

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),      -- Only one row allowed
    version TEXT NOT NULL,                      -- e.g., '1.6'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, '1.6');

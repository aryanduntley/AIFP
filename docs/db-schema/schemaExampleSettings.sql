-- user_preferences.db Schema
-- Version: 1.0
-- Purpose: Store user-specific AI behavior preferences, customizations, and opt-in tracking
-- Location: .aifp-project/user_preferences.db

-- ===============================================================
-- Core Settings
-- ===============================================================

-- User Settings: Project-specific AI behavior configurations
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,           -- e.g., 'fp_strictness_level', 'prefer_explicit_returns'
    setting_value TEXT NOT NULL,                -- JSON value or simple string
    description TEXT,
    scope TEXT DEFAULT 'project',               -- 'project' (future: 'global' for multi-project support)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Example default settings:
INSERT INTO user_settings (setting_key, setting_value, description) VALUES
  ('fp_strictness_level', '{"level": "standard", "exceptions": []}', 'How strict to enforce FP directives'),
  ('prefer_explicit_returns', 'true', 'Always use explicit return statements'),
  ('suppress_warnings', '[]', 'Directives to suppress low-confidence warnings');

-- ===============================================================
-- Directive Preferences (Atomic Key-Value Structure)
-- ===============================================================

-- Directive Preferences: Per-directive behavior customizations
CREATE TABLE IF NOT EXISTS directive_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_name TEXT NOT NULL,               -- e.g., 'project_file_write'
    preference_key TEXT NOT NULL,               -- e.g., 'always_add_docstrings', 'max_function_length'
    preference_value TEXT NOT NULL,             -- Atomic value (JSON for complex structures)
    active BOOLEAN DEFAULT 1,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(directive_name, preference_key)      -- Allows multiple preferences per directive, one value per key
);

-- Example entries:
INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description) VALUES
  ('project_file_write', 'always_add_docstrings', 'true', 'Always add docstrings to functions'),
  ('project_file_write', 'max_function_length', '50', 'Maximum function length in lines'),
  ('project_file_write', 'prefer_guard_clauses', 'true', 'Use guard clauses instead of nested conditionals'),
  ('project_file_write', 'code_style', 'explicit', 'Prefer explicit over implicit code style'),
  ('project_file_write', 'indent_style', 'spaces_2', 'Use 2 spaces for indentation'),
  ('project_compliance_check', 'auto_fix_violations', 'false', 'Automatically fix FP violations when detected'),
  ('project_compliance_check', 'skip_warnings', 'false', 'Skip low-severity compliance warnings'),
  ('project_compliance_check', 'strict_mode', 'false', 'Enable strict FP compliance mode'),
  ('project_task_decomposition', 'task_granularity', 'medium', 'Level of task breakdown detail (low/medium/high)'),
  ('project_task_decomposition', 'naming_convention', 'verb_noun', 'Task naming style (verb_noun, descriptive, user_choice)'),
  ('project_task_decomposition', 'auto_create_items', 'true', 'Automatically create items for small tasks'),
  ('project_task_decomposition', 'default_priority', 'medium', 'Default priority for new tasks (low/medium/high)');

-- ===============================================================
-- AI Interaction Logging (Disabled by Default)
-- ===============================================================

-- AI Interaction Log: Track user corrections to learn preferences over time
CREATE TABLE IF NOT EXISTS ai_interaction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_type TEXT NOT NULL,             -- 'preference_learned', 'correction', 'clarification'
    directive_context TEXT,                     -- Directive being executed
    user_feedback TEXT NOT NULL,                -- What user said/corrected
    ai_interpretation TEXT,                     -- How AI interpreted it
    applied_to_preferences BOOLEAN DEFAULT 0,   -- Whether this updated preferences
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================================
-- FP Compliance Tracking (Disabled by Default)
-- ===============================================================

-- FP Flow Tracking: Track FP directive compliance history for improvement analysis
CREATE TABLE IF NOT EXISTS fp_flow_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    fp_directives_applied TEXT NOT NULL,        -- JSON array of directive names
    compliance_score REAL DEFAULT 1.0,          -- 0-1 score
    issues_json TEXT,                           -- JSON array of compliance issues
    user_overrides TEXT,                        -- JSON of user-approved exceptions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================================
-- Issue Reporting (Disabled by Default)
-- ===============================================================

-- Issue Reports: Allow users to compile context and submit issues with full logs
CREATE TABLE IF NOT EXISTS issue_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,                  -- 'bug', 'feature_request', 'directive_issue'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    directive_name TEXT,                        -- Related directive if applicable
    context_log_ids TEXT,                       -- JSON array of ai_interaction_log IDs
    status TEXT DEFAULT 'draft',                -- 'draft', 'submitted', 'resolved'
    submitted_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================================
-- Tracking Settings (Feature Flags for Opt-In Tracking)
-- ===============================================================

-- Tracking Settings: Control which tracking features are enabled
CREATE TABLE IF NOT EXISTS tracking_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT NOT NULL UNIQUE,          -- e.g., 'fp_flow_tracking', 'issue_reports'
    enabled BOOLEAN DEFAULT 0,                  -- Default: disabled (opt-in only)
    description TEXT,
    estimated_token_overhead TEXT,              -- e.g., "~5% increase per file write"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default entries (all tracking disabled to minimize API costs):
INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
  ('fp_flow_tracking', 0, 'Track FP directive compliance over time', '~5% token increase per file write'),
  ('issue_reports', 0, 'Enable detailed issue report compilation', '~2% token increase on errors'),
  ('ai_interaction_log', 0, 'Log all AI interactions for learning', '~3% token increase overall'),
  ('helper_function_logging', 0, 'Log helper function errors and execution details', '~1% token increase on errors');

-- ===============================================================
-- Indexes for Performance
-- ===============================================================

CREATE INDEX IF NOT EXISTS idx_directive_preferences_directive ON directive_preferences(directive_name);
CREATE INDEX IF NOT EXISTS idx_directive_preferences_active ON directive_preferences(active);
CREATE INDEX IF NOT EXISTS idx_ai_interaction_log_directive ON ai_interaction_log(directive_context);
CREATE INDEX IF NOT EXISTS idx_fp_flow_tracking_file ON fp_flow_tracking(file_path);
CREATE INDEX IF NOT EXISTS idx_issue_reports_status ON issue_reports(status);

-- ===============================================================
-- Triggers for Timestamp Updates
-- ===============================================================

CREATE TRIGGER IF NOT EXISTS update_user_settings_timestamp
AFTER UPDATE ON user_settings
FOR EACH ROW
BEGIN
    UPDATE user_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_directive_preferences_timestamp
AFTER UPDATE ON directive_preferences
FOR EACH ROW
BEGIN
    UPDATE directive_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_fp_flow_tracking_timestamp
AFTER UPDATE ON fp_flow_tracking
FOR EACH ROW
BEGIN
    UPDATE fp_flow_tracking SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_tracking_settings_timestamp
AFTER UPDATE ON tracking_settings
FOR EACH ROW
BEGIN
    UPDATE tracking_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- ===============================================================
-- Schema Version Tracking
-- ===============================================================

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),      -- Only one row allowed
    version TEXT NOT NULL,                      -- e.g., '1.0'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (id, version) VALUES (1, '1.0');

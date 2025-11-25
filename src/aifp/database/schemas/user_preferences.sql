-- user_preferences.db Schema
-- Version: 1.1
-- Purpose: Store user-specific AI behavior preferences, customizations, and opt-in tracking
-- Location: .aifp-project/user_preferences.db
-- Changelog v1.1:
--   - Renamed directive_context to directive_name in ai_interaction_log table
--   - Added CHECK constraints for status fields
--   - Added comprehensive timestamp triggers

-- ===============================================================
-- Core Settings
-- ===============================================================

-- User Settings: Project-specific AI behavior configurations
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,           -- e.g., 'fp_strictness_level', 'prefer_explicit_returns'
    setting_value TEXT NOT NULL,                -- JSON value or simple string
    description TEXT,
    scope TEXT DEFAULT 'project' CHECK (scope IN ('project', 'global')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

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

-- ===============================================================
-- AI Interaction Logging (Disabled by Default)
-- ===============================================================

-- AI Interaction Log: Track user corrections to learn preferences over time
CREATE TABLE IF NOT EXISTS ai_interaction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('preference_learned', 'correction', 'clarification')),
    directive_name TEXT,                        -- Directive being executed (renamed from directive_context)
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
    report_type TEXT NOT NULL CHECK (report_type IN ('bug', 'feature_request', 'directive_issue')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    directive_name TEXT,                        -- Related directive if applicable
    context_log_ids TEXT,                       -- JSON array of ai_interaction_log IDs
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'resolved')),
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

-- ===============================================================
-- Indexes for Performance
-- ===============================================================

CREATE INDEX IF NOT EXISTS idx_directive_preferences_directive ON directive_preferences(directive_name);
CREATE INDEX IF NOT EXISTS idx_directive_preferences_active ON directive_preferences(active);
CREATE INDEX IF NOT EXISTS idx_ai_interaction_log_directive ON ai_interaction_log(directive_name);
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
    version TEXT NOT NULL,                      -- e.g., '1.1'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, '1.1');

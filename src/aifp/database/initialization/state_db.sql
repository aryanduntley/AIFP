-- State Database Schema
-- Purpose: FP-compliant replacement for mutable global variables
-- Location: <source-dir>/.state/runtime.db
-- Created by: create_state_database helper during project_discovery

CREATE TABLE IF NOT EXISTS variables (
    var_name TEXT PRIMARY KEY,
    var_value TEXT NOT NULL,
    var_type TEXT CHECK(var_type IN ('int', 'float', 'str', 'bool', 'dict', 'list')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Auto-update timestamp trigger
CREATE TRIGGER IF NOT EXISTS update_variables_timestamp
    AFTER UPDATE ON variables
    FOR EACH ROW
BEGIN
    UPDATE variables SET updated_at = CURRENT_TIMESTAMP WHERE var_name = OLD.var_name;
END;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    version TEXT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version) VALUES ('1.0');

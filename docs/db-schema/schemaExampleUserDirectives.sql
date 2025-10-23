-- user_directives.db Schema
-- Version: 1.0
-- Purpose: Store user-defined domain-specific directives (home automation, cloud infrastructure, etc.)
-- Location: .aifp/user_directives.db

-- ===============================================================
-- Core Directive Storage
-- ===============================================================

CREATE TABLE IF NOT EXISTS user_directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                      -- e.g., 'turn_off_lights_5pm', 'monitor_stove'
    source_file TEXT NOT NULL,                      -- e.g., '.aifp/user-directives/source/home_automation.yaml'
    source_format TEXT NOT NULL CHECK (source_format IN ('yaml', 'json', 'txt')),
    domain TEXT,                                    -- e.g., 'home_automation', 'aws_infrastructure', 'custom'
    description TEXT,                               -- Human-readable description
    raw_content TEXT NOT NULL,                      -- Original user-provided directive text
    validated_content JSON NOT NULL,                -- AI-validated and structured directive

    -- Trigger information
    trigger_type TEXT NOT NULL CHECK (trigger_type IN ('time', 'event', 'condition', 'manual')),
    trigger_config JSON NOT NULL,                   -- e.g., {"time": "17:00", "timezone": "America/New_York"}

    -- Action information
    action_type TEXT NOT NULL,                      -- e.g., 'api_call', 'script_execution', 'function_call'
    action_config JSON NOT NULL,                    -- e.g., {"api": "homeassistant", "endpoint": "/lights/off"}

    -- Status and lifecycle
    status TEXT DEFAULT 'pending_validation' CHECK (status IN (
        'pending_validation',   -- Initial state, needs AI validation
        'validated',            -- AI validated, ready for implementation
        'implementing',         -- AI generating implementation code
        'implemented',          -- Code generated, not yet active
        'active',              -- Running and monitoring
        'paused',              -- Temporarily disabled
        'error',               -- Execution error occurred
        'deprecated'           -- No longer in use
    )),

    -- Implementation tracking
    implementation_status TEXT DEFAULT 'not_started' CHECK (implementation_status IN (
        'not_started',
        'in_progress',
        'completed',
        'failed'
    )),
    implementation_file_path TEXT,                  -- e.g., '.aifp/user-directives/generated/handlers/lights_5pm.py'

    -- Validation tracking
    validation_questions JSON,                      -- Questions asked during validation
    validation_answers JSON,                        -- User's answers
    validated_at DATETIME,
    validated_by TEXT DEFAULT 'ai',

    -- Approval tracking (user testing and approval)
    approved BOOLEAN DEFAULT 0,                     -- User has tested and approved implementation
    approved_at DATETIME,                           -- When user approved

    -- Metadata
    priority INTEGER DEFAULT 0,                     -- Higher = more important
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    activated_at DATETIME,                          -- When directive became active
    last_modified_at DATETIME                       -- When source file was last modified
);

-- ===============================================================
-- Execution Statistics (Database Stores Summary Only)
-- ===============================================================

CREATE TABLE IF NOT EXISTS directive_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,

    -- Summary statistics only (detailed logs in files)
    last_execution_time DATETIME,
    next_scheduled_time DATETIME,                   -- For time-based triggers
    total_executions INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,

    -- Last error info (for quick status checks)
    last_error_time DATETIME,
    last_error_type TEXT,                           -- e.g., 'connection_error', 'timeout', 'validation_error'
    last_error_message TEXT,                        -- Brief error message (full details in error log file)

    -- Performance metrics
    avg_execution_time_ms REAL,                     -- Average execution time in milliseconds
    max_execution_time_ms REAL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (directive_id) REFERENCES user_directives(id) ON DELETE CASCADE
);

-- ===============================================================
-- Directive Dependencies
-- ===============================================================

CREATE TABLE IF NOT EXISTS directive_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,

    -- Dependency information
    dependency_type TEXT NOT NULL CHECK (dependency_type IN (
        'python_package',       -- Python package (pip install)
        'system_package',       -- System package (apt, brew, etc.)
        'api_service',          -- External API (Home Assistant, AWS, etc.)
        'file',                 -- File or directory dependency
        'environment_variable', -- Required environment variable
        'hardware'             -- Hardware dependency (e.g., specific sensor)
    )),
    dependency_name TEXT NOT NULL,                  -- e.g., 'boto3', 'homeassistant-api', 'GPIO'
    dependency_version TEXT,                        -- e.g., '>=1.20.0', '2.0.1'

    -- Installation status
    status TEXT DEFAULT 'not_installed' CHECK (status IN (
        'not_installed',
        'pending_confirmation',     -- AI detected, waiting for user confirmation
        'installing',
        'installed',
        'failed',
        'not_available'
    )),

    -- Installation details
    install_command TEXT,                           -- e.g., 'pip install boto3>=1.20.0'
    user_confirmed BOOLEAN DEFAULT 0,               -- User approved installation
    confirmed_at DATETIME,
    installed_at DATETIME,

    -- Metadata
    required BOOLEAN DEFAULT 1,                     -- Is this dependency required or optional?
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (directive_id) REFERENCES user_directives(id) ON DELETE CASCADE
);

-- ===============================================================
-- Directive Implementations (Links directives to generated code)
-- ===============================================================

CREATE TABLE IF NOT EXISTS directive_implementations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_id INTEGER NOT NULL,

    -- Implementation details
    implementation_type TEXT NOT NULL CHECK (implementation_type IN (
        'event_handler',        -- Event-driven handler
        'scheduler',            -- Time-based scheduler (cron job)
        'service',             -- Long-running background service
        'function',            -- Simple function call
        'script'               -- Standalone script
    )),
    file_path TEXT NOT NULL,                        -- e.g., '.aifp/user-directives/generated/handlers/lights_5pm.py'
    function_name TEXT,                             -- e.g., 'handle_lights_5pm'

    -- Code metadata
    language TEXT DEFAULT 'python',
    framework TEXT,                                 -- e.g., 'asyncio', 'celery', 'apscheduler'
    entry_point TEXT,                               -- How to execute (e.g., 'python handlers/lights_5pm.py')

    -- Deployment status
    deployed BOOLEAN DEFAULT 0,
    deployed_at DATETIME,
    process_id INTEGER,                             -- PID if running as background service

    -- File tracking
    file_checksum TEXT,                             -- MD5/SHA256 checksum for change detection

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (directive_id) REFERENCES user_directives(id) ON DELETE CASCADE
);

-- ===============================================================
-- Directive Relationships (Dependencies between user directives)
-- ===============================================================

CREATE TABLE IF NOT EXISTS directive_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_directive_id INTEGER NOT NULL,
    target_directive_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL CHECK (relationship_type IN (
        'depends_on',           -- Source depends on target completing first
        'triggers',            -- Source triggers target
        'conflicts_with',      -- Source and target cannot both be active
        'enhances'             -- Source enhances target's functionality
    )),

    description TEXT,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_directive_id) REFERENCES user_directives(id) ON DELETE CASCADE,
    FOREIGN KEY (target_directive_id) REFERENCES user_directives(id) ON DELETE CASCADE,

    UNIQUE(source_directive_id, target_directive_id, relationship_type)
);

-- ===============================================================
-- Source File Tracking (Track user directive source files)
-- ===============================================================

CREATE TABLE IF NOT EXISTS source_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,                 -- e.g., '.aifp/user-directives/source/home_automation.yaml'
    file_format TEXT NOT NULL CHECK (file_format IN ('yaml', 'json', 'txt')),
    file_checksum TEXT NOT NULL,                    -- MD5/SHA256 checksum for change detection

    -- Parsing status
    last_parsed_at DATETIME,
    parse_status TEXT DEFAULT 'not_parsed' CHECK (parse_status IN (
        'not_parsed',
        'parsing',
        'parsed_successfully',
        'parse_error'
    )),
    parse_error_message TEXT,

    -- Directive count
    directive_count INTEGER DEFAULT 0,
    active_directive_count INTEGER DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ===============================================================
-- Logging Configuration (What to log and where)
-- ===============================================================

CREATE TABLE IF NOT EXISTS logging_config (
    id INTEGER PRIMARY KEY CHECK (id = 1),          -- Only one row allowed

    -- Execution logging (file-based)
    execution_logs_enabled BOOLEAN DEFAULT 1,
    execution_log_rotation TEXT DEFAULT 'daily' CHECK (execution_log_rotation IN ('daily', 'weekly', 'size')),
    execution_log_retention_days INTEGER DEFAULT 30,
    execution_log_compress_after_days INTEGER DEFAULT 7,
    execution_log_max_size_mb INTEGER DEFAULT 100,  -- For size-based rotation

    -- Error logging (file-based)
    error_logs_enabled BOOLEAN DEFAULT 1,
    error_log_rotation TEXT DEFAULT 'size' CHECK (error_log_rotation IN ('daily', 'weekly', 'size')),
    error_log_retention_days INTEGER DEFAULT 90,    -- Keep errors longer
    error_log_max_size_mb INTEGER DEFAULT 10,
    error_log_format TEXT DEFAULT 'json' CHECK (error_log_format IN ('json', 'text')),

    -- Database logging (statistics only)
    store_execution_statistics BOOLEAN DEFAULT 1,   -- Store summary stats in directive_executions
    store_last_error_only BOOLEAN DEFAULT 1,        -- Only keep last error in DB, rest in files
    store_execution_history BOOLEAN DEFAULT 0,      -- DO NOT store full history in DB (use files)

    -- Log file paths
    execution_log_dir TEXT DEFAULT '.aifp/logs/execution/',
    error_log_dir TEXT DEFAULT '.aifp/logs/errors/',
    lifecycle_log_path TEXT DEFAULT '.aifp/logs/user-directives.log',

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Insert default logging configuration
INSERT INTO logging_config (id) VALUES (1);

-- ===============================================================
-- Indexes for Performance
-- ===============================================================

CREATE INDEX IF NOT EXISTS idx_user_directives_status ON user_directives(status);
CREATE INDEX IF NOT EXISTS idx_user_directives_domain ON user_directives(domain);
CREATE INDEX IF NOT EXISTS idx_user_directives_trigger_type ON user_directives(trigger_type);
CREATE INDEX IF NOT EXISTS idx_user_directives_source_file ON user_directives(source_file);

CREATE INDEX IF NOT EXISTS idx_directive_executions_directive_id ON directive_executions(directive_id);
CREATE INDEX IF NOT EXISTS idx_directive_executions_last_execution ON directive_executions(last_execution_time);

CREATE INDEX IF NOT EXISTS idx_directive_dependencies_directive_id ON directive_dependencies(directive_id);
CREATE INDEX IF NOT EXISTS idx_directive_dependencies_status ON directive_dependencies(status);

CREATE INDEX IF NOT EXISTS idx_directive_implementations_directive_id ON directive_implementations(directive_id);
CREATE INDEX IF NOT EXISTS idx_directive_implementations_type ON directive_implementations(implementation_type);

CREATE INDEX IF NOT EXISTS idx_source_files_checksum ON source_files(file_checksum);

-- ===============================================================
-- Triggers for Timestamp Updates
-- ===============================================================

CREATE TRIGGER IF NOT EXISTS update_user_directives_timestamp
AFTER UPDATE ON user_directives
FOR EACH ROW
BEGIN
    UPDATE user_directives SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_directive_executions_timestamp
AFTER UPDATE ON directive_executions
FOR EACH ROW
BEGIN
    UPDATE directive_executions SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_directive_dependencies_timestamp
AFTER UPDATE ON directive_dependencies
FOR EACH ROW
BEGIN
    UPDATE directive_dependencies SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_directive_implementations_timestamp
AFTER UPDATE ON directive_implementations
FOR EACH ROW
BEGIN
    UPDATE directive_implementations SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS update_source_files_timestamp
AFTER UPDATE ON source_files
FOR EACH ROW
BEGIN
    UPDATE source_files SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- ===============================================================
-- Schema Version Tracking
-- ===============================================================

CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),          -- Only one row allowed
    version TEXT NOT NULL,                          -- e.g., '1.0'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (id, version) VALUES (1, '1.0');

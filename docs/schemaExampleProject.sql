-- Files Table: Project file inventory
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    language TEXT,  -- Guessed or set
    checksum TEXT,  -- For change detection
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Functions Table: Per-file details
CREATE TABLE functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    purpose TEXT,
    parameters JSON,  -- e.g., '["param1: str", "param2: int"]'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id)
);

-- Themes Table: AI-generated groupings
CREATE TABLE themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    ai_generated BOOLEAN DEFAULT 1,
    confidence_score REAL DEFAULT 0.0,  -- 0-1
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Flows Table: Sequences within themes
CREATE TABLE flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    ai_generated BOOLEAN DEFAULT 1,
    confidence_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Junction Tables for Many-to-Many
CREATE TABLE flow_themes (
    flow_id INTEGER,
    theme_id INTEGER,
    PRIMARY KEY (flow_id, theme_id),
    FOREIGN KEY (flow_id) REFERENCES flows(id),
    FOREIGN KEY (theme_id) REFERENCES themes(id)
);

CREATE TABLE file_flows (
    file_id INTEGER,
    flow_id INTEGER,
    PRIMARY KEY (file_id, flow_id),
    FOREIGN KEY (file_id) REFERENCES files(id),
    FOREIGN KEY (flow_id) REFERENCES flows(id)
);

-- Infrastructure Table: Project setup
CREATE TABLE infrastructure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,  -- e.g., 'language', 'package', 'testing'
    value TEXT,  -- e.g., 'Python 3.12', 'numpy'
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Completion Path Table: High-level, standalone roadmap
CREATE TABLE completion_path (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,  -- e.g., 'setup', 'core dev', 'finish'
    order_index INTEGER NOT NULL,  -- For explicit ordering (1, 2, 3...)
    status TEXT DEFAULT 'pending',  -- pending/in_progress/complete
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Milestones Table: Standalone overviews under completion_path
CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    completion_path_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (completion_path_id) REFERENCES completion_path(id)
);

-- Tasks Table: Detailed breakdowns under milestones
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    milestone_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 0,  -- Higher = more urgent
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (milestone_id) REFERENCES milestones(id)
);

-- Sidequests Table: Priority deviations that pause tasks
CREATE TABLE sidequests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paused_task_id INTEGER NOT NULL,  -- The task being paused
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority INTEGER DEFAULT 1,  -- Default higher than tasks to prioritize
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paused_task_id) REFERENCES tasks(id)
);

-- Items Table: Lowest-level actions for tasks/sidequests
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_table TEXT NOT NULL CHECK (reference_table IN ('tasks', 'sidequests')),  -- Restrict to tasks/sidequests
    reference_id INTEGER NOT NULL,  -- FK to tasks.id or sidequests.id
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Notes Table: Clarifications for project entities
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
	note_type TEXT NOT NULL,  -- e.g., 'clarification', 'pivot', 'research'
    reference_table TEXT,  -- e.g., 'items', 'files', 'completion_path'
    reference_id INTEGER,  -- FK to referenced table's id
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

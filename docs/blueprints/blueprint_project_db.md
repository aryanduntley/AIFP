# Project Database Blueprint (project.db)

## Overview

The `project.db` database is a **per-project SQLite database** that stores all mutable project state, organizational structures, and code tracking information. It resides in `.aifp-project/project.db` and enables AI assistants to have instant, persistent context about the project.

### Core Purpose

- **Persistent Project State**: Track all project metadata across sessions
- **Code Organization**: Map files → functions → interactions
- **Task Management**: Hierarchical task decomposition and tracking
- **Completion Roadmap**: Finite completion path with milestones
- **Theme/Flow Structure**: Organizational groupings for code
- **Notes & Context**: AI-written clarifications and decisions

---

## Database Schema

### Project Table

**Purpose**: High-level project metadata and evolution tracking

```sql
CREATE TABLE project (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    purpose TEXT NOT NULL,
    goals_json TEXT NOT NULL,              -- JSON array: ["Fast computation", "No OOP"]
    status TEXT DEFAULT 'active',          -- active, paused, completed, abandoned
    version INTEGER DEFAULT 1,             -- Tracks project pivots
    blueprint_checksum TEXT,               -- MD5/SHA256 checksum of ProjectBlueprint.md for sync validation
    user_directives_status TEXT DEFAULT NULL CHECK (user_directives_status IN (NULL, 'in_progress', 'active', 'disabled')),
                                           -- NULL: no user directives, 'in_progress': being set up, 'active': running, 'disabled': paused
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields**:
- `name`: Project identifier (e.g., "MatrixCalculator")
- `purpose`: One-sentence description
- `goals_json`: JSON array of project goals
- `version`: Increments on major pivots (tracked by `project_evolution`)
- `blueprint_checksum`: Checksum of `.aifp/ProjectBlueprint.md` for sync validation
- `user_directives_status`: Tracks user directive system status
  - `NULL` (default): User directives not initialized
  - `'in_progress'`: User directives being set up (parsing/validating)
  - `'active'`: User directives running and executing
  - `'disabled'`: User directives paused but database exists

**Usage**:
- **ONE row per database** (one project per database)
- Updated by `project_init`, `project_evolution`, `project_blueprint_update`
- Updated by `user_directive_parse` (sets 'in_progress'), `user_directive_activate` (sets 'active'), `user_directive_deactivate` (sets 'disabled')
- Queried by almost all directives for context
- `blueprint_checksum` updated whenever ProjectBlueprint.md is modified
- `user_directives_status` checked by `aifp_run` and `aifp_status` to include user directive context

---

### Files Table

**Purpose**: Track all source files in the project

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    language TEXT,                          -- e.g., 'Python', 'JavaScript'
    checksum TEXT,                          -- For change detection
    project_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
);

CREATE INDEX idx_files_path ON files(path);
```

**Key Fields**:
- `path`: Relative path from project root (e.g., "src/matrix.py")
- `language`: Detected or manually set
- `checksum`: SHA256 hash for change detection

**Usage**:
- Updated by `project_file_write`, `project_file_read`
- Queried to map files to themes/flows
- Used by Git integration to detect external changes

---

### Functions Table

**Purpose**: Track all functions defined in project files

```sql
CREATE TABLE functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    purpose TEXT,
    parameters JSON,                        -- e.g., '["param1: str", "param2: int"]'
    return_type TEXT,                       -- e.g., 'Matrix', 'Result[int, str]'
    purity_level TEXT,                      -- 'pure', 'effectful', 'unknown'
    side_effects_json TEXT,                 -- JSON: {"io": false, "mutation": false}
    complexity TEXT,                        -- e.g., 'O(n)', 'O(n log n)'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
);

CREATE INDEX idx_functions_file_id ON functions(file_id);
CREATE INDEX idx_functions_name ON functions(name);
```

**Key Fields**:
- `name`: Function name (unique per file)
- `purity_level`: Set by FP directives (`fp_purity`, etc.)
- `side_effects_json`: Detailed side effect analysis
- `complexity`: Big-O complexity for AI reasoning

**Usage**:
- Updated by `project_file_write` after FP compliance checks
- Queried by `project_compliance_check` for violations
- Used to build call graphs via `interactions` table

---

### Types Table

**Purpose**: Store Algebraic Data Type (ADT) definitions

```sql
CREATE TABLE types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    definition_json TEXT NOT NULL,          -- JSON schema for ADT
    description TEXT,
    linked_function_id INTEGER,             -- Optional: ADT associated with function
    project_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id),
    FOREIGN KEY (linked_function_id) REFERENCES functions(id) ON DELETE SET NULL
);
```

**Example Data**:
```sql
INSERT INTO types (name, definition_json, description, project_id)
VALUES (
    'Result',
    '{"type": "union", "variants": [{"Ok": "T"}, {"Err": "E"}]}',
    'Result type for error handling',
    1
);
```

**Usage**:
- Created by `fp_adt` directive
- Queried when generating type-safe code
- `linked_function_id` associates ADT with specific function (e.g., custom return type)

---

### Interactions Table

**Purpose**: Track function dependencies and composition

```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_function_id INTEGER NOT NULL,
    target_function_id INTEGER NOT NULL,
    interaction_type TEXT NOT NULL,         -- 'call', 'compose', 'chain', 'depend'
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_function_id) REFERENCES functions(id) ON DELETE CASCADE,
    FOREIGN KEY (target_function_id) REFERENCES functions(id) ON DELETE CASCADE
);

CREATE INDEX idx_interactions_source ON interactions(source_function_id);
CREATE INDEX idx_interactions_target ON interactions(target_function_id);
```

**Interaction Types**:
- `call`: Function A calls function B
- `compose`: Function A is composed with B (A ∘ B)
- `chain`: Function A chains B monadically (flatMap/bind)
- `depend`: Function A depends on B's data structure

**Usage**:
- Updated by `project_file_write` during code analysis
- Queried to build dependency graphs
- Used by `fp_dependency_tracking` directive

---

### Themes Table

**Purpose**: High-level conceptual groupings for project organization

```sql
CREATE TABLE themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    ai_generated BOOLEAN DEFAULT 1,
    confidence_score REAL DEFAULT 0.0,      -- 0-1
    project_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
);
```

**Examples**:
- `matrix-operations`: Functions for matrix math
- `vector-operations`: Vector-specific functions
- `error-handling`: Result/Option type utilities
- `io-boundaries`: File I/O and logging

**Usage**:
- Created by `project_themes_flows_init`
- Linked to files via `file_flows` junction table
- Queried for contextual code organization

---

### Flows Table

**Purpose**: Sequential workflows or functional pipelines

```sql
CREATE TABLE flows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    ai_generated BOOLEAN DEFAULT 1,
    confidence_score REAL DEFAULT 0.0,
    project_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
);
```

**Examples**:
- `matrix-multiplication-flow`: multiply → validate → normalize
- `file-processing-flow`: read → parse → transform → write
- `error-recovery-flow`: try → catch → log → retry

**Usage**:
- Created by `project_themes_flows_init`
- Linked to themes via `flow_themes` junction
- Linked to files via `file_flows` junction

---

### Junction Tables

#### flow_themes
```sql
CREATE TABLE flow_themes (
    flow_id INTEGER,
    theme_id INTEGER,
    PRIMARY KEY (flow_id, theme_id),
    FOREIGN KEY (flow_id) REFERENCES flows(id) ON DELETE CASCADE,
    FOREIGN KEY (theme_id) REFERENCES themes(id) ON DELETE CASCADE
);
```

#### file_flows
```sql
CREATE TABLE file_flows (
    file_id INTEGER,
    flow_id INTEGER,
    PRIMARY KEY (file_id, flow_id),
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (flow_id) REFERENCES flows(id) ON DELETE CASCADE
);
```

**Purpose**: Many-to-many relationships between flows/themes/files

---

### Completion Path Tables

#### completion_path

**Purpose**: High-level roadmap stages

```sql
CREATE TABLE completion_path (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                     -- e.g., 'setup', 'core dev', 'polish'
    order_index INTEGER NOT NULL,           -- 1, 2, 3...
    status TEXT DEFAULT 'pending',          -- pending, in_progress, complete
    description TEXT,
    project_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
);

CREATE INDEX idx_completion_path_project_id ON completion_path(project_id);
```

#### milestones

**Purpose**: Major achievements under completion path stages

```sql
CREATE TABLE milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    completion_path_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (completion_path_id) REFERENCES completion_path(id) ON DELETE CASCADE
);
```

#### tasks

**Purpose**: Actionable work items under milestones

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    milestone_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',          -- pending, in_progress, completed
    priority INTEGER DEFAULT 0,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (milestone_id) REFERENCES milestones(id) ON DELETE CASCADE
);
```

#### subtasks

**Purpose**: Breakdown of tasks into smaller units

```sql
CREATE TABLE subtasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_task_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'high',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);
```

#### sidequests

**Purpose**: Priority deviations that pause tasks temporarily

```sql
CREATE TABLE sidequests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paused_task_id INTEGER NOT NULL,
    paused_subtask_id INTEGER,              -- Optional: pause at subtask level
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'low',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paused_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (paused_subtask_id) REFERENCES subtasks(id) ON DELETE SET NULL
);
```

**Purpose**: Handle scope creep or urgent deviations without losing context

#### items

**Purpose**: Lowest-level action items (polymorphic reference)

```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_table TEXT NOT NULL CHECK (reference_table IN ('tasks', 'subtasks', 'sidequests')),
    reference_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_items_reference ON items(reference_table, reference_id);
```

**Polymorphic Pattern**: `reference_table` + `reference_id` allows items to belong to tasks, subtasks, OR sidequests.

**Cleanup**: Handled by triggers (see Triggers section below).

---

### Notes Table

**Purpose**: AI-written clarifications, decisions, and context with optional directive tracking

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    note_type TEXT NOT NULL,                -- 'clarification', 'pivot', 'research', 'roadblock'
    reference_table TEXT,                   -- 'items', 'files', 'tasks', 'project', etc.
    reference_id INTEGER,
    source TEXT DEFAULT 'user',             -- 'user', 'ai', 'directive' (who created this note)
    directive_name TEXT,                    -- Optional: directive context if note relates to directive execution
    severity TEXT DEFAULT 'info',           -- 'info', 'warning', 'error'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notes_reference ON notes(reference_table, reference_id);
CREATE INDEX IF NOT EXISTS idx_notes_directive ON notes(directive_name);
CREATE INDEX IF NOT EXISTS idx_notes_severity ON notes(severity);
CREATE INDEX IF NOT EXISTS idx_notes_source ON notes(source);
```

**Note Types**:
- `clarification`: User confirmed intent or decision
- `pivot`: Project goal or direction changed
- `research`: AI documented findings
- `roadblock`: Issue requiring future resolution

**Enhanced Fields** (for traceability, not logging):
- `source`: Who created the note (`user`, `ai`, or `directive`)
- `directive_name`: Optional directive context (only when note relates to directive execution)
- `severity`: Importance level (`info`, `warning`, `error`)

**Usage**:
- Written by directives for AI memory and future context
- Queried during session boot to restore context
- Critical for maintaining AI "memory" across sessions
- `directive_name` provides traceability when a directive writes a clarification or decision
- **NOT for logging**: Logging goes to user_preferences.db (opt-in only)
- Managed by `project_notes_log` directive for important clarifications/decisions only

**When to Use `directive_name` Field**:
- ✅ **Use**: When directive writes a clarification about its decision
  - Example: `project_file_write` writes "FP compliance check required refactoring function X to eliminate mutation"
  - `directive_name = 'project_file_write'`
- ✅ **Use**: When directive needs to record reasoning for future reference
  - Example: `project_task_decomposition` writes "User request ambiguous - created subtask for clarification"
  - `directive_name = 'project_task_decomposition'`
- ❌ **Don't use**: For generic user notes or unrelated entries
  - Example: User manually adds note "Remember to refactor this later"
  - `directive_name = NULL`
- ❌ **Don't use**: For verbose logging or debugging (use user_preferences.db tracking instead)

**Examples**:
```sql
-- User clarification
INSERT INTO notes (content, note_type, reference_table, reference_id, source)
VALUES ('User confirmed: Use pure Python, no NumPy', 'clarification', 'project', 1, 'user');

-- Project pivot
INSERT INTO notes (content, note_type, reference_table, reference_id, source, severity)
VALUES ('Pivoting from CLI tool to web API', 'pivot', 'project', 1, 'ai', 'warning');

-- Directive clarification note (important decision recorded for future AI context)
INSERT INTO notes (content, note_type, source, directive_name, severity)
VALUES ('FP compliance check required refactoring function X to eliminate mutation', 'clarification', 'directive', 'project_file_write', 'info');

-- Roadblock
INSERT INTO notes (content, note_type, reference_table, reference_id, source, severity)
VALUES ('Cannot write to /protected/ - needs elevated permissions', 'roadblock', 'files', 5, 'directive', 'error');
```

---

## Infrastructure Table

**Purpose**: Track project setup and dependencies

```sql
CREATE TABLE infrastructure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                     -- 'language', 'package', 'testing', 'ci_cd'
    value TEXT,                             -- e.g., 'Python 3.12', 'pytest', 'GitHub Actions'
    description TEXT,
    project_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES project(id)
);
```

**Examples**:
```sql
INSERT INTO infrastructure (type, value, description, project_id) VALUES
    ('language', 'Python 3.12', 'Primary language', 1),
    ('package', 'functools', 'Built-in FP utilities', 1),
    ('testing', 'pytest', 'Unit testing framework', 1);
```

---

## Triggers

### Timestamp Updates

```sql
CREATE TRIGGER IF NOT EXISTS update_project_timestamp
AFTER UPDATE ON project
FOR EACH ROW
BEGIN
    UPDATE project SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
```

**Apply to all tables** with `updated_at` fields.

### Items Table Cleanup

**Purpose**: Auto-delete orphaned items when parent is deleted

```sql
CREATE TRIGGER IF NOT EXISTS delete_task_items
AFTER DELETE ON tasks
FOR EACH ROW
BEGIN
    DELETE FROM items WHERE reference_table='tasks' AND reference_id=OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS delete_subtask_items
AFTER DELETE ON subtasks
FOR EACH ROW
BEGIN
    DELETE FROM items WHERE reference_table='subtasks' AND reference_id=OLD.id;
END;

CREATE TRIGGER IF NOT EXISTS delete_sidequest_items
AFTER DELETE ON sidequests
FOR EACH ROW
BEGIN
    DELETE FROM items WHERE reference_table='sidequests' AND reference_id=OLD.id;
END;
```

---

## Cascade Deletion Strategy

### Internal Hierarchies (WITH CASCADE)

- `completion_path` → `milestones` → `tasks` → `subtasks`/`sidequests`
- `files` → `functions` → `interactions`
- Junction tables (`flow_themes`, `file_flows`)

**Rationale**: Deleting a milestone should cascade to its tasks.

### Project-Level References (NO CASCADE)

- `project_id` foreign keys do **NOT** have `ON DELETE CASCADE`
- Deleting a project = deleting the entire database file

**Rationale**: One project per database, so project deletion = DB deletion.

---

## Common Queries

### Get all functions in a theme

```sql
SELECT f.name, f.purpose, fi.path
FROM functions f
JOIN files fi ON f.file_id = fi.id
JOIN file_flows ff ON fi.id = ff.file_id
JOIN flows fl ON ff.flow_id = fl.id
JOIN flow_themes ft ON fl.id = ft.flow_id
JOIN themes t ON ft.theme_id = t.id
WHERE t.name = 'matrix-operations';
```

### Get task completion progress

```sql
SELECT
    m.name AS milestone,
    COUNT(t.id) AS total_tasks,
    SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) AS completed_tasks,
    ROUND(100.0 * SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END) / COUNT(t.id), 2) AS progress_pct
FROM milestones m
JOIN tasks t ON m.id = t.milestone_id
GROUP BY m.id;
```

### Get function dependency chain

```sql
WITH RECURSIVE deps(func_id, func_name, depth) AS (
    SELECT id, name, 0 FROM functions WHERE name = 'multiply_matrices'
    UNION ALL
    SELECT f.id, f.name, deps.depth + 1
    FROM functions f
    JOIN interactions i ON f.id = i.target_function_id
    JOIN deps ON i.source_function_id = deps.func_id
)
SELECT func_name, depth FROM deps;
```

### Get all notes for project initialization

```sql
SELECT content, note_type, created_at
FROM notes
WHERE reference_table = 'project'
ORDER BY created_at DESC;
```

---

## Best Practices

### 1. Use Transactions

```python
conn.execute("BEGIN TRANSACTION")
try:
    conn.execute("INSERT INTO files ...")
    conn.execute("INSERT INTO functions ...")
    conn.execute("COMMIT")
except Exception:
    conn.execute("ROLLBACK")
    raise
```

### 2. Always Log to Notes

```sql
INSERT INTO notes (content, note_type, reference_table, reference_id)
VALUES ('Function refactored for purity', 'research', 'functions', 42);
```

### 3. Validate Foreign Keys

Before inserting, check parent exists:

```python
cursor.execute("SELECT id FROM files WHERE id = ?", (file_id,))
if not cursor.fetchone():
    raise ValueError(f"File {file_id} does not exist")
```

### 4. Use Indexes

All foreign keys already have indexes. Add custom indexes for frequent queries:

```sql
CREATE INDEX idx_functions_purity ON functions(purity_level);
```

### 5. Keep Database Normalized

- Avoid data duplication (use foreign keys)
- Use JSON fields sparingly (only for truly dynamic data)
- Store computed values only if expensive to recalculate

---

## Database Lifecycle

### Initialization

```python
# project_init creates project.db
conn = sqlite3.connect(".aifp-project/project.db")
conn.executescript(SCHEMA_SQL)

# Insert initial project row
conn.execute("""
    INSERT INTO project (name, purpose, goals_json)
    VALUES (?, ?, ?)
""", ("MatrixCalculator", "Pure FP matrix operations", '["Fast", "No OOP"]'))
```

### Session Boot

```python
# Load project context
project = conn.execute("SELECT * FROM project WHERE id = 1").fetchone()
themes = conn.execute("SELECT * FROM themes").fetchall()
tasks = conn.execute("SELECT * FROM tasks WHERE status != 'completed'").fetchall()
notes = conn.execute("SELECT * FROM notes ORDER BY created_at DESC LIMIT 10").fetchall()
```

### Completion

```python
# project_completion_check verifies all criteria met
completed = conn.execute("""
    SELECT COUNT(*) = 0 FROM tasks WHERE status != 'completed'
""").fetchone()[0]

if completed:
    conn.execute("UPDATE project SET status = 'completed'")
```

---

## Summary

The `project.db` database provides:

- **Persistent state** across AI sessions
- **Hierarchical task tracking** (completion_path → milestones → tasks → subtasks/items)
- **Code organization** (files → functions → interactions)
- **Thematic structure** (themes, flows, junctions)
- **Notes system** for AI memory and context
- **Trigger-based cleanup** for polymorphic items
- **Optimized queries** with proper indexes and foreign keys
- **Cascade deletion** for internal hierarchies only

It is the **single source of truth** for project state, enabling AI assistants to maintain context, track progress, and make informed decisions across sessions.

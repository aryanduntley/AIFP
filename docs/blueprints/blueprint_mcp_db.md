# MCP Database Blueprint (aifp_core.db)

## Overview

The `aifp_core.db` database is a **read-only, global database** that stores all AIFP directives, helper function definitions, tool schemas, and standards. It resides in `~/.aifp/aifp_core.db` and serves as the **knowledge base** for the MCP server.

### Core Purpose

- **Directive Storage**: All FP and project directives in compressed/detailed formats
- **Helper Definitions**: Reusable helper function schemas
- **Tool Schemas**: MCP tool input/output definitions
- **Standards**: AIFP coding standards, templates, and examples
- **Immutable Knowledge**: Never modified by projects (only by AIFP updates)

---

## Database Schema

### Directives Table

**Purpose**: Store all AIFP directives (FP + Project + User Preference)

```sql
CREATE TABLE directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                      -- e.g., 'aifp_run', 'init_project'
    type TEXT NOT NULL,                             -- 'fp', 'project', or 'user_pref'
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

CREATE INDEX idx_directives_name ON directives(name);
CREATE INDEX idx_directives_type ON directives(type);
```

**Example Row**:
```sql
INSERT INTO directives (name, type, level, parent_directive, description, workflow, intent_keywords_json, confidence_threshold)
VALUES (
    'user_preferences_update',
    'user_pref',
    1,
    'user_preferences_sync',
    'Handles explicit user requests to modify behavior preferences. Uses find_directive_by_intent helper to map requests to directives.',
    '{"trunk": "parse_preference_request", "branches": [...]}',
    '["set preference", "change behavior", "always do"]',
    0.6
);
```

**Directive Types**:
- `fp`: Functional programming enforcement directives
- `project`: Project lifecycle management directives
- `user_pref`: User preference and customization directives

---

### Categories Table

**Purpose**: Categorize directives into logical groupings

```sql
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,                       -- e.g., 'purity', 'immutability', 'task_management'
    description TEXT,                                -- Optional human-readable explanation
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Example Categories**:
```sql
INSERT INTO categories (name, description) VALUES
  ('purity', 'Pure function enforcement and state elimination'),
  ('immutability', 'Data immutability and mutation prevention'),
  ('user_customization', 'User-specific AI behavior preferences'),
  ('task_management', 'Project task decomposition and tracking'),
  ('logging', 'Runtime logging and note-taking');
```

---

### Directive Categories (Junction Table)

**Purpose**: Link directives to categories (many-to-many)

```sql
CREATE TABLE IF NOT EXISTS directive_categories (
    directive_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (directive_id, category_id),
    FOREIGN KEY (directive_id) REFERENCES directives(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);
```

**Usage**: One directive can belong to multiple categories

---

### Directives Interactions Table

**Purpose**: Track relationships and dependencies between directives

```sql
CREATE TABLE IF NOT EXISTS directives_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_directive_id INTEGER NOT NULL,
    target_directive_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL CHECK (relation_type IN (
        'triggers',        -- source calls or activates target
        'depends_on',      -- source relies on data or state from target
        'escalates_to',    -- source delegates upward to target for resolution
        'cross_link',      -- bidirectional or contextual connection
        'fp_reference'     -- source calls or enforces an FP directive
    )),
    weight INTEGER DEFAULT 1,
    description TEXT,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_directive_id) REFERENCES directives(id),
    FOREIGN KEY (target_directive_id) REFERENCES directives(id)
);

CREATE INDEX IF NOT EXISTS idx_interactions_source ON directives_interactions (source_directive_id);
CREATE INDEX IF NOT EXISTS idx_interactions_target ON directives_interactions (target_directive_id);
CREATE INDEX IF NOT EXISTS idx_interactions_relation_type ON directives_interactions (relation_type);
```

**Relation Types**:
- `triggers`: Source directive activates target directive
- `depends_on`: Source relies on target's data or state
- `escalates_to`: Source delegates to higher-level target
- `cross_link`: Bidirectional or contextual relationship
- `fp_reference`: Source calls FP directive for compliance check

---

### Helper Functions Table

**Purpose**: Store reusable helper function schemas

```sql
CREATE TABLE helper_functions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,                 -- 'database', 'file', 'git', 'fp'
    description TEXT NOT NULL,
    parameters_json TEXT NOT NULL,          -- JSON schema for parameters
    return_type TEXT NOT NULL,
    implementation_hint TEXT,               -- Optional: pseudo-code or algorithm hint
    related_directives TEXT,                -- JSON array of directive names that use this helper
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_helper_functions_category ON helper_functions(category);
```

**Example Rows**:
```sql
INSERT INTO helper_functions (name, category, description, parameters_json, return_type, implementation_hint)
VALUES (
    'query_functions_by_file',
    'database',
    'Retrieve all functions for a given file_id from project.db',
    '{"file_id": {"type": "integer", "required": true}}',
    'List[dict]',
    'SELECT * FROM functions WHERE file_id = ?'
);

INSERT INTO helper_functions (name, category, description, parameters_json, return_type, implementation_hint)
VALUES (
    'find_directive_by_intent',
    'database',
    'Searches directives table by name, description, and intent_keywords_json to map user preference requests to specific directives. Returns list of matching directives with confidence scores sorted by relevance.',
    '{"user_request": {"type": "string", "required": true}, "confidence_threshold": {"type": "float", "required": false, "default": 0.5}}',
    'List[dict]',
    'SELECT id, name, description FROM directives WHERE type IN (''project'', ''fp'') AND (name LIKE ? OR description LIKE ? OR intent_keywords_json LIKE ?) ORDER BY confidence_score DESC'
);
```

---

### Schema Version Table

**Purpose**: Track schema version for migration management

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY CHECK (id = 1),      -- Only one row allowed
    version TEXT NOT NULL,                      -- e.g., '1.0'
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (id, version) VALUES (1, '1.0');
```

---

### Tool Schemas Table

**Purpose**: Store MCP tool definitions (input/output schemas)

```sql
CREATE TABLE tool_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    input_schema_json TEXT NOT NULL,        -- JSON Schema for input
    output_schema_json TEXT NOT NULL,       -- JSON Schema for output
    example_input_json TEXT,
    example_output_json TEXT,
    related_directives TEXT,                -- JSON array of directive names
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tool_schemas_name ON tool_schemas(tool_name);
```

**Example Row**:
```sql
INSERT INTO tool_schemas (tool_name, description, input_schema_json, output_schema_json)
VALUES (
    'aifp_run',
    'Execute AIFP command with natural language intent',
    '{"type": "object", "properties": {"command": {"type": "string"}, "project_root": {"type": "string"}}, "required": ["command", "project_root"]}',
    '{"type": "object", "properties": {"success": {"type": "boolean"}, "directive_executed": {"type": "string"}, "result": {"type": "string"}}}'
);
```

---

### Standards Table

**Purpose**: Store AIFP coding standards, templates, and examples

```sql
CREATE TABLE standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,                 -- 'purity', 'composition', 'error_handling', etc.
    standard_name TEXT NOT NULL,
    description TEXT NOT NULL,
    good_example TEXT,                      -- Code example showing compliant pattern
    bad_example TEXT,                       -- Code example showing violation
    language TEXT,                          -- 'python', 'javascript', 'language-agnostic'
    related_directives TEXT,                -- JSON array of directive names
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_standards_category ON standards(category);
CREATE INDEX idx_standards_language ON standards(language);
```

**Example Row**:
```sql
INSERT INTO standards (category, standard_name, description, good_example, bad_example, language)
VALUES (
    'purity',
    'No Global State Access',
    'Functions must not access global variables; pass all dependencies explicitly',
    'def add(x, y): return x + y',
    'total = 0\ndef add(x): global total; total += x; return total',
    'python'
);
```

---

### Intent Keywords Table

**Purpose**: Store keyword → directive mappings for intent detection

```sql
CREATE TABLE intent_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    directive_name TEXT NOT NULL,
    weight REAL DEFAULT 1.0,                -- Higher weight = stronger match
    context TEXT,                           -- Optional: when this keyword applies
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (directive_name) REFERENCES directives(name)
);

CREATE INDEX idx_intent_keywords_keyword ON intent_keywords(keyword);
CREATE INDEX idx_intent_keywords_directive ON intent_keywords(directive_name);
```

**Example Rows**:
```sql
INSERT INTO intent_keywords (keyword, directive_name, weight) VALUES
    ('init', 'project_init', 1.0),
    ('initialize', 'project_init', 1.0),
    ('setup', 'project_init', 0.8),
    ('pure', 'fp_purity', 1.0),
    ('side effects', 'fp_side_effect_detection', 1.0);
```

**Usage**:
- MCP server queries this table during intent parsing
- Calculates weighted score for each directive
- Selects directive with highest score > confidence_threshold

---

### Templates Table

**Purpose**: Store reusable code templates and boilerplate

```sql
CREATE TABLE templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,                 -- 'adt', 'result_type', 'function_header', etc.
    language TEXT NOT NULL,
    template_code TEXT NOT NULL,            -- Code with {{placeholder}} variables
    variables_json TEXT NOT NULL,           -- JSON schema for placeholders
    description TEXT,
    related_directives TEXT,                -- JSON array of directive names
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_language ON templates(language);
```

**Example Row**:
```sql
INSERT INTO templates (template_name, category, language, template_code, variables_json, description)
VALUES (
    'result_type_python',
    'adt',
    'python',
    'from typing import Generic, TypeVar, Union\nfrom dataclasses import dataclass\n\nT = TypeVar("T")\nE = TypeVar("E")\n\n@dataclass(frozen=True)\nclass Ok(Generic[T]):\n    value: T\n\n@dataclass(frozen=True)\nclass Err(Generic[E]):\n    error: E\n\nResult = Union[Ok[T], Err[E]]',
    '{}',
    'Result type ADT for Python'
);
```

---

### Roadblock Resolutions Table

**Purpose**: Store common roadblocks and their resolutions (extracted from directives)

```sql
CREATE TABLE roadblock_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue TEXT NOT NULL,
    resolution TEXT NOT NULL,
    directive_name TEXT NOT NULL,
    escalation_directive TEXT,              -- Optional: directive to call for resolution
    category TEXT,                          -- 'database', 'file_io', 'git', 'language', etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (directive_name) REFERENCES directives(name)
);

CREATE INDEX idx_roadblocks_issue ON roadblock_resolutions(issue);
CREATE INDEX idx_roadblocks_category ON roadblock_resolutions(category);
```

**Example Rows**:
```sql
INSERT INTO roadblock_resolutions (issue, resolution, directive_name, escalation_directive, category) VALUES
    ('stateful_function', 'Isolate state outside of function scope', 'fp_purity', NULL, 'purity'),
    ('language_mismatch', 'Escalate to fp_language_standardization', 'fp_purity', 'fp_language_standardization', 'language'),
    ('database_locked', 'Retry with exponential backoff, max 3 attempts', 'project_update_db', NULL, 'database');
```

---

### Configuration Table

**Purpose**: Store AIFP system configuration defaults

```sql
CREATE TABLE configuration (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_key TEXT NOT NULL UNIQUE,
    config_value TEXT NOT NULL,
    description TEXT,
    value_type TEXT NOT NULL,               -- 'string', 'integer', 'boolean', 'json'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Example Rows**:
```sql
INSERT INTO configuration (config_key, config_value, description, value_type) VALUES
    ('default_confidence_threshold', '0.7', 'Minimum confidence for auto-execution', 'float'),
    ('enable_low_confidence_prompts', 'true', 'Prompt user when confidence < threshold', 'boolean'),
    ('max_directive_depth', '5', 'Maximum nested directive call depth', 'integer'),
    ('supported_languages', '["python", "javascript", "typescript", "rust", "go"]', 'Languages with full FP support', 'json');
```

---

## Query Examples

### Find directive by keyword

```sql
SELECT d.*
FROM directives d
WHERE d.intent_keywords_json LIKE '%"purity"%'
LIMIT 1;
```

**Better (using intent_keywords table)**:
```sql
SELECT d.*, SUM(ik.weight) AS total_score
FROM directives d
JOIN intent_keywords ik ON d.name = ik.directive_name
WHERE ik.keyword IN ('pure', 'side effects')
GROUP BY d.id
ORDER BY total_score DESC
LIMIT 1;
```

### Get all FP directives in a category

```sql
SELECT name, description, confidence_threshold
FROM directives
WHERE type = 'fp' AND category_name = 'purity'
ORDER BY name;
```

### Get helper functions for database operations

```sql
SELECT name, description, parameters_json, return_type
FROM helper_functions
WHERE category = 'database'
ORDER BY name;
```

### Get code template for Result type in JavaScript

```sql
SELECT template_code, variables_json
FROM templates
WHERE category = 'adt'
  AND language = 'javascript'
  AND template_name LIKE '%result%';
```

### Get roadblock resolution with escalation

```sql
SELECT issue, resolution, escalation_directive
FROM roadblock_resolutions
WHERE issue = 'language_mismatch' AND directive_name = 'fp_purity';
```

---

## Population Strategy

### Directive Population

1. **Parse existing JSON files** (`directives-fp-core.json`, `directives-fp-aux.json`, `directives-project.json`)
2. **Extract fields** and insert into `directives` table
3. **Extract intent_keywords** and populate `intent_keywords` table
4. **Extract roadblocks** and populate `roadblock_resolutions` table

**Script**: `populate_core_db.py`

```python
import json
import sqlite3

def populate_directives(conn, directives_json):
    for directive in directives_json:
        conn.execute("""
            INSERT INTO directives (name, type, level, category_name, description, workflow_json, intent_keywords_json, compressed_form)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            directive['name'],
            directive['type'],
            directive.get('level'),
            directive['category']['name'],
            directive['description'],
            json.dumps(directive['workflow']),
            json.dumps(directive['intent_keywords_json']),
            directive.get('compressed_form', '')
        ))

        # Populate intent_keywords table
        for keyword in directive['intent_keywords_json']:
            conn.execute("""
                INSERT INTO intent_keywords (keyword, directive_name)
                VALUES (?, ?)
            """, (keyword, directive['name']))

        # Populate roadblock_resolutions table
        for roadblock in directive.get('roadblocks_json', []):
            conn.execute("""
                INSERT INTO roadblock_resolutions (issue, resolution, directive_name)
                VALUES (?, ?, ?)
            """, (roadblock['issue'], roadblock['resolution'], directive['name']))
```

### Helper Functions Population

Manually curated or generated from `helpers/` module docstrings:

```python
def populate_helpers_from_module(conn, module):
    for func_name, func in inspect.getmembers(module, inspect.isfunction):
        doc = inspect.getdoc(func)
        sig = inspect.signature(func)

        conn.execute("""
            INSERT INTO helper_functions (name, category, description, parameters_json, return_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            func_name,
            module.__name__.split('.')[-1],  # e.g., 'db_helpers'
            doc or 'No description',
            json.dumps({name: str(param.annotation) for name, param in sig.parameters.items()}),
            str(sig.return_annotation)
        ))
```

### Standards Population

Manually curated from AIFP documentation:

```python
standards_data = [
    {
        'category': 'purity',
        'standard_name': 'No Global State',
        'description': '...',
        'good_example': '...',
        'bad_example': '...',
        'language': 'python'
    },
    # ... more standards
]

for standard in standards_data:
    conn.execute("INSERT INTO standards (...) VALUES (...)", standard)
```

---

## Read-Only Enforcement

### File Permissions

```bash
chmod 444 ~/.aifp/aifp_core.db  # Read-only for all users
```

### SQLite Connection

```python
conn = sqlite3.connect("file:~/.aifp/aifp_core.db?mode=ro", uri=True)
```

**Effect**: Any attempt to write will raise `sqlite3.OperationalError`.

---

## Update Strategy

### Version Tracking

Add `schema_version` to `configuration` table:

```sql
INSERT INTO configuration (config_key, config_value, description, value_type)
VALUES ('schema_version', '1.0.0', 'aifp_core.db schema version', 'string');
```

### Update Process

1. **Release new AIFP version** with updated directives/helpers
2. **Distribute new `aifp_core.db`** with version incremented
3. **MCP server checks version** on startup
4. **If outdated**, prompt user to update:
   ```bash
   aifp update --core-db
   ```

### Backward Compatibility

- **Add columns** with defaults (safe)
- **Never remove columns** (breaks old MCP servers)
- **Use migration scripts** for major schema changes

---

## Integration with MCP Server

### On MCP Server Startup

```python
class MCPServer:
    def __init__(self):
        self.core_db = sqlite3.connect("~/.aifp/aifp_core.db", uri=True, check_same_thread=False)
        self.directive_cache = self.load_all_directives()
        self.helper_cache = self.load_all_helpers()

    def load_all_directives(self) -> dict:
        cursor = self.core_db.execute("SELECT name, workflow_json FROM directives")
        return {name: json.loads(workflow) for name, workflow in cursor.fetchall()}
```

### On `aifp_run` Command

```python
def route_command(self, command: str) -> Directive:
    # 1. Extract keywords from command
    keywords = extract_keywords(command)

    # 2. Query intent_keywords table
    cursor = self.core_db.execute("""
        SELECT d.name, SUM(ik.weight) AS score
        FROM directives d
        JOIN intent_keywords ik ON d.name = ik.directive_name
        WHERE ik.keyword IN ({})
        GROUP BY d.name
        ORDER BY score DESC
        LIMIT 1
    """.format(','.join('?' * len(keywords))), keywords)

    directive_name, score = cursor.fetchone()

    # 3. Load full directive from cache
    return self.directive_cache[directive_name]
```

---

## Summary

The `aifp_core.db` database provides:

- **Immutable knowledge base** for all AIFP directives and standards
- **Directive storage** for FP, project, and user preference directives (88+ total)
- **Category system** for organizing directives into logical groupings
- **Directive interactions** tracking for cross-directive relationships
- **Intent detection** via keyword matching and weighted scoring
- **Helper function schemas** including `find_directive_by_intent` for preference mapping
- **Tool schemas** for MCP tool definitions
- **Code templates** for generating FP-compliant boilerplate
- **Roadblock resolutions** for common issues
- **Configuration defaults** for AIFP system behavior
- **Read-only enforcement** to prevent corruption
- **Schema version tracking** for migration management

It acts as the **brain** of the MCP server, storing all knowledge needed to execute directives, route commands, enforce AIFP standards, and support user customization across all projects.

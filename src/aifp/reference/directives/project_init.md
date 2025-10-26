# project_init - Project Initialization Directive

**Type**: Project Management
**Level**: 1
**Parent**: `aifp_run`
**Category**: Initialization

---

## Purpose

`project_init` initializes a new AIFP project by creating the `.aifp-project/` directory structure, initializing databases, and generating the ProjectBlueprint.md file. This directive sets up the foundation for all subsequent AIFP project management operations.

**Use this directive when**:
- Starting a new AIFP-managed project
- Converting an existing project to use AIFP
- Initializing for automation projects (Use Case 2)

---

## When to Use

### Explicit Initialization

Keywords that trigger `project_init`:
- "initialize AIFP", "init project", "setup AIFP"
- "start new project", "create AIFP project"
- "convert to AIFP"

**IMPORTANT**: Always call `get_project_status()` first to check if already initialized!

---

## Workflow

### Trunk: `initialize_project`

**Step 1: Check Existing Project**

```python
# ALWAYS check first - never re-initialize
status = get_project_status(project_root)

if status['initialized']:
    return {
        "success": false,
        "error": "Project already initialized",
        "existing_project": status['project_name'],
        "recommendation": "Use `aifp status` to view project state"
    }
```

**Step 2: Gather Project Information**

```python
# Prompt user for project details
project_info = {
    "name": prompt_user("Project name?") or infer_from_directory(),
    "purpose": prompt_user("Project purpose?") or "Software project",
    "goals": prompt_user("Main goals?") or [],
    "language": detect_primary_language(project_root) or "Python"
}
```

**Step 3: Create Directory Structure**

```bash
{project_root}/
└── .aifp-project/
    ├── project.db                  # Project state database
    ├── user_preferences.db         # User preferences (optional)
    ├── aifp_core.db                # Copy of core directives (read-only)
    ├── ProjectBlueprint.md         # High-level architecture doc
    ├── backups/                    # Blueprint backups
    └── logs/                       # Only for Use Case 2 (automation)
```

**Step 4: Initialize project.db**

```python
# Load schema from src/aifp/database/schemas/schemaExampleProject.sql
schema_sql = load_schema("project")

conn = sqlite3.connect(f"{project_root}/.aifp-project/project.db")
conn.executescript(schema_sql)

# Insert project metadata
conn.execute("""
    INSERT INTO project (name, purpose, goals_json, status, version)
    VALUES (?, ?, ?, 'active', 1)
""", (project_info['name'], project_info['purpose'], json.dumps(project_info['goals'])))

project_id = conn.lastrowid

# Insert default completion path
conn.execute("""
    INSERT INTO completion_path (name, order_index, status, description, project_id)
    VALUES
        ('Setup', 1, 'completed', 'Project initialization', ?),
        ('Development', 2, 'pending', 'Core development phase', ?),
        ('Testing', 3, 'pending', 'Testing and validation', ?),
        ('Finalization', 4, 'pending', 'Documentation and completion', ?)
""", (project_id, project_id, project_id, project_id))

conn.commit()
```

**Step 5: Copy aifp_core.db (Read-Only)**

```python
# Copy core directive database to project for local reference
shutil.copy(
    "~/.aifp/aifp_core.db",
    f"{project_root}/.aifp-project/aifp_core.db"
)
```

**Step 6: Initialize user_preferences.db (Optional)**

```python
# Load schema from src/aifp/database/schemas/schemaExampleSettings.sql
prefs_schema = load_schema("user_preferences")

conn = sqlite3.connect(f"{project_root}/.aifp-project/user_preferences.db")
conn.executescript(prefs_schema)

# All tracking features disabled by default
conn.execute("""
    INSERT INTO tracking_settings (feature_name, enabled, description)
    VALUES
        ('fp_flow_tracking', false, 'Track FP compliance over time'),
        ('ai_interaction_log', false, 'Log AI corrections for learning'),
        ('issue_reports', false, 'Track issues with context')
""")

conn.commit()
```

**Step 7: Generate ProjectBlueprint.md**

```python
# Call create_project_blueprint() helper
blueprint_content = generate_blueprint({
    "name": project_info['name'],
    "purpose": project_info['purpose'],
    "goals": project_info['goals'],
    "language": project_info['language'],
    "architecture": infer_architecture(project_root),
    "completion_path": ["Setup", "Development", "Testing", "Finalization"]
})

write_file(
    f"{project_root}/.aifp-project/ProjectBlueprint.md",
    blueprint_content
)
```

**Step 8: Return Success**

```python
return {
    "success": true,
    "project_name": project_info['name'],
    "project_root": project_root,
    "databases_created": ["project.db", "user_preferences.db", "aifp_core.db"],
    "next_steps": [
        "Define project themes and flows",
        "Create first milestone and tasks",
        "Start coding with FP directives"
    ]
}
```

---

## Interactions with Other Directives

### Called By

- **`aifp_run`** - Routes initialization requests

### Calls

- **`get_project_status()`** - Check if already initialized
- **`create_project_blueprint()`** - Generate blueprint file
- **`detect_primary_language()`** - Infer project language
- **`infer_architecture()`** - Analyze existing code structure

### Data Flow

```
User: "Initialize AIFP for my calculator"
  ↓
aifp_run → project_init
  ├─ Checks get_project_status() → Not initialized ✓
  ├─ Prompts: "Project purpose?" → "Pure FP calculator"
  ├─ Creates .aifp-project/ structure
  ├─ Initializes project.db
  ├─ Copies aifp_core.db
  ├─ Initializes user_preferences.db
  ├─ Generates ProjectBlueprint.md
  └─ Returns success with next steps
  ↓
AI presents: "✅ Project initialized: Calculator. Next: Define themes."
```

---

## Examples

### Example 1: Basic Initialization

**User**: "Initialize AIFP for my project"

**AI Processing**:
1. Calls `get_project_status()` → Not initialized
2. Detects directory name: "matrix-calculator"
3. Prompts: "Project purpose?"
4. User: "Pure FP matrix operations library"
5. Executes `project_init` workflow

**Result**:
```
✅ Project initialized: Matrix Calculator

Created:
  • .aifp-project/project.db
  • .aifp-project/user_preferences.db
  • .aifp-project/aifp_core.db
  • .aifp-project/ProjectBlueprint.md

Next steps:
  1. Define project themes and flows
  2. Create first milestone
  3. Start coding with FP compliance
```

---

### Example 2: Automation Project (Use Case 2)

**User**: "Initialize AIFP for home automation"

**AI Processing**:
1. Recognizes "automation" keyword
2. Prompts: "Is this an automation project? (yes/no)"
3. User: "Yes"
4. Creates additional structure:
   - `.aifp-project/logs/` for execution logs
   - Prepared for `user_directives.db` (created on first directive)

**Result**:
```
✅ Automation project initialized: Home Automation

Created:
  • .aifp-project/project.db
  • .aifp-project/user_preferences.db
  • .aifp-project/aifp_core.db
  • .aifp-project/ProjectBlueprint.md
  • .aifp-project/logs/ (for automation execution)

Next steps:
  1. Create directive files (e.g., directives/lights.yaml)
  2. Tell AI: "Parse my directive file at directives/lights.yaml"
  3. AI will generate automation code in src/
```

---

### Example 3: Converting Existing Project

**User**: "Convert my existing project to AIFP"

**AI Processing**:
1. Checks `get_project_status()` → Not initialized
2. Scans existing codebase
3. Detects language: Python
4. Detects existing files: src/main.py, src/utils.py
5. Prompts: "Import existing code into AIFP tracking?"
6. User: "Yes"
7. Initializes + indexes existing files

**Result**:
```
✅ Project converted to AIFP: MyApp

Indexed existing files:
  • src/main.py (3 functions)
  • src/utils.py (5 functions)

Databases created:
  • .aifp-project/project.db (8 functions tracked)
  • .aifp-project/user_preferences.db
  • .aifp-project/ProjectBlueprint.md (generated from existing code)

Next: Run FP compliance check to identify issues
```

---

## Edge Cases

### Case 1: Already Initialized

**Trigger**: `.aifp-project/` already exists

**Response**:
```json
{
  "success": false,
  "error": "Project already initialized",
  "existing_project": "Matrix Calculator",
  "recommendation": "Use `aifp status` to view current state"
}
```

**AI presents**:
```
⚠️ Project already initialized: Matrix Calculator
Use "status" to view current state or "continue" to resume work.
```

---

### Case 2: No Write Permissions

**Trigger**: Cannot create `.aifp-project/` directory

**Response**:
```json
{
  "success": false,
  "error": "Permission denied: Cannot create .aifp-project/",
  "recommendation": "Check directory permissions or run with appropriate access"
}
```

---

### Case 3: Invalid Project Root

**Trigger**: project_root not provided or invalid

**Response**:
```json
{
  "success": false,
  "error": "Invalid project root path",
  "recommendation": "Provide valid project directory path"
}
```

---

## Related Directives

### Primary Relationships

- **`aifp_run`** - Routes to this directive
- **`project_themes_flows_init`** - Next step after initialization
- **`project_task_decomposition`** - Create initial tasks
- **`get_project_status()`** - Pre-check helper

### Helper Functions Used

- `get_project_status()` - Check initialization
- `create_project_blueprint()` - Generate blueprint
- `detect_primary_language()` - Infer language
- `load_schema(name)` - Load database schemas

---

## Database Operations

**Read Operations**:
- Checks if `.aifp-project/` exists (file system)
- Scans existing files for conversion (optional)

**Write Operations**:
- Creates `.aifp-project/` directory
- Initializes `project.db` with schema
- Inserts project metadata
- Inserts default completion path
- Creates `user_preferences.db` with defaults
- Copies `aifp_core.db` to project
- Writes `ProjectBlueprint.md`

---

## FP Compliance

**Purity**: ⚠️ Effect function
- Has side effects (creates files/directories)
- But isolated: all effects explicit in workflow

**Immutability**: ✅ Immutable inputs
- project_info frozen after collection
- No mutation of parameters

**Side Effects**: ⚠️ Explicit
- File system writes (directory creation)
- Database initialization (DDL operations)
- All effects documented in workflow

---

## Error Handling

### Schema Load Failure

**Trigger**: Cannot load database schema files

**Response**:
```json
{
  "success": false,
  "error": "Schema file not found: schemaExampleProject.sql",
  "recommendation": "Verify AIFP MCP server installation"
}
```

### Database Creation Failure

**Trigger**: SQLite errors during initialization

**Response**:
```json
{
  "success": false,
  "error": "Database initialization failed: disk full",
  "partial_cleanup": true,
  "recommendation": "Free disk space and retry"
}
```

---

## Best Practices

1. **Always check first** - Call `get_project_status()` before initializing
2. **Gather info upfront** - Get project name, purpose, goals from user
3. **Detect context** - Infer language, architecture from existing files
4. **Transaction safety** - Use transactions for database operations
5. **Fail gracefully** - Clean up partial initialization on errors
6. **Provide next steps** - Tell user what to do after initialization
7. **Support both use cases** - Regular dev vs automation projects

---

## Version History

- **v1.0** (2025-10-22): Initial project initialization
- **v1.1** (2025-10-24): Added ProjectBlueprint.md generation
- **v1.2** (2025-10-26): Added support for automation projects (Use Case 2)

---

## Notes

- This is a **one-time operation** per project
- Creates immutable project structure (directories don't change)
- Databases are mutable, but schema is fixed
- ProjectBlueprint.md is **living document** (updated via `project_blueprint_update`)
- For automation projects, `user_directives.db` created on first directive parse

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

## Project Structure Created

### AIFP Project Management Directory

```
<project-root>/                      # User's project (any structure)
├── .aifp-project/                   # AIFP project management folder
│   ├── ProjectBlueprint.md          # High-level project overview (human & AI readable)
│   ├── project.db                   # Project state database
│   ├── user_preferences.db          # User customization database
│   ├── user_directives.db           # Optional: user-defined automation (Use Case 2 only)
│   ├── config.json                  # Project-specific AIFP configuration
│   ├── .gitkeep                     # Ensures directory tracked in Git
│   ├── backups/                     # Automated backups
│   │   ├── project.db.backup
│   │   ├── ProjectBlueprint.md.backup
│   │   └── ProjectBlueprint.md.v{N} # Versioned backups
│   └── logs/                        # Use Case 2 only: user directive execution logs
│       ├── execution/               # 30-day execution logs
│       └── errors/                  # 90-day error logs
├── .git/
│   └── .aifp/                       # Optional: archived project state (legacy path)
│       ├── ProjectBlueprint.md      # Snapshot for recovery
│       └── project.db.backup
└── <user's existing project structure>  # Unchanged - AI respects existing layout
```

**IMPORTANT**: `aifp_core.db` is NOT copied to user projects. It lives in the MCP server installation directory and is accessed via MCP tools only.

### Design Rationale

- **`.aifp-project/` at project root**: Primary location for AIFP project management state
- **Respects existing structure**: AI does NOT create or modify user's source code folders during init
- **Flexible code organization**: User's code may be in root, `src/`, `lib/`, `app/`, or any structure
- **`.git/.aifp/` archive**: Optional backup/recovery mechanism (legacy compatibility)
- **ProjectBlueprint.md**: Documents user's actual project structure, language, and architecture
- **Three-database architecture per project**: project.db, user_preferences.db, and optionally user_directives.db

### Use Case Distinction

**Use Case 1: Software Development** (Managing existing or new code projects)
- Creates `.aifp-project/` with project.db, user_preferences.db
- No logs/ directory (not needed)
- ProjectBlueprint.md documents user's project structure and goals
- AI detects and works with user's existing code organization
- For new projects: AI asks user where to create code files or uses language conventions

**Use Case 2: Automation Projects** (Home automation, cloud infrastructure, custom workflows)
- All of Use Case 1 PLUS:
- `logs/` directory for directive execution and error tracking
- `user_directives.db` created on first directive parse
- Project purpose: Implement and execute user-defined directives
- AI generates implementation code in appropriate folders (determined during directive implementation)

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
    ├── user_preferences.db         # User preferences
    ├── config.json                 # Project-specific AIFP configuration
    ├── ProjectBlueprint.md         # High-level architecture doc
    ├── .gitkeep                    # Ensures directory tracked in Git
    ├── backups/                    # Blueprint and database backups
    └── logs/                       # Only for Use Case 2 (automation)
        ├── execution/              # 30-day execution logs
        └── errors/                 # 90-day error logs
```

**Note**: `aifp_core.db` is NOT copied - it remains in the MCP server and is accessed via MCP tools.

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

**Step 5: Initialize user_preferences.db**

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

**Step 6: Create config.json**

```python
# Create project-specific configuration
config = {
    "aifp_version": "1.0",
    "project_name": project_info['name'],
    "blueprint_path": ".aifp-project/ProjectBlueprint.md",
    "databases": {
        "project_db": ".aifp-project/project.db",
        "user_preferences_db": ".aifp-project/user_preferences.db"
    },
    "backups": {
        "enabled": True,
        "directory": ".aifp-project/backups/",
        "auto_backup_on_evolution": True
    },
    "status": {
        "context_limit": 10,
        "auto_browse": False,
        "ambiguity_threshold": 0.7
    },
    "git_integration": {
        "archive_to_git_aifp": True,
        "sync_on_commit": False
    }
}

# For Use Case 2 (automation), add logging config
if project_is_automation:
    config["logging"] = {
        "execution_logs_enabled": True,
        "execution_log_rotation": "daily",
        "execution_log_retention_days": 30,
        "error_logs_enabled": True,
        "error_log_retention_days": 90,
        "execution_log_dir": ".aifp-project/logs/execution/",
        "error_log_dir": ".aifp-project/logs/errors/"
    }
    config["databases"]["user_directives_db"] = ".aifp-project/user_directives.db"

write_json(f"{project_root}/.aifp-project/config.json", config)
```

**Step 7: Generate ProjectBlueprint.md**

```python
# Call create_project_blueprint() helper
# Detects existing code structure and documents it
blueprint_content = generate_blueprint({
    "name": project_info['name'],
    "purpose": project_info['purpose'],
    "goals": project_info['goals'],
    "language": project_info['language'],
    "existing_structure": scan_existing_files(project_root),
    "architecture": infer_architecture(project_root),
    "completion_path": ["Setup", "Development", "Testing", "Finalization"],
    "use_case": "automation" if project_is_automation else "development"
})

write_file(
    f"{project_root}/.aifp-project/ProjectBlueprint.md",
    blueprint_content
)

# Backup blueprint
backup_file(
    f"{project_root}/.aifp-project/ProjectBlueprint.md",
    f"{project_root}/.aifp-project/backups/ProjectBlueprint.md.backup"
)
```

**Step 8: Create .gitkeep (Optional but Recommended)**

```python
# Ensure .aifp-project/ is tracked in Git even if empty subdirectories
write_file(f"{project_root}/.aifp-project/.gitkeep", "")

# For automation projects, ensure logs/ subdirectories exist
if project_is_automation:
    os.makedirs(f"{project_root}/.aifp-project/logs/execution/", exist_ok=True)
    os.makedirs(f"{project_root}/.aifp-project/logs/errors/", exist_ok=True)
```

**Step 9: Return Success**

```python
return {
    "success": true,
    "project_name": project_info['name'],
    "project_root": project_root,
    "use_case": "automation" if project_is_automation else "development",
    "files_created": [
        ".aifp-project/project.db",
        ".aifp-project/user_preferences.db",
        ".aifp-project/config.json",
        ".aifp-project/ProjectBlueprint.md",
        ".aifp-project/.gitkeep"
    ],
    "next_steps": [
        "Review ProjectBlueprint.md" if project_is_automation else "Define project themes and flows",
        "Parse directive files" if project_is_automation else "Create first milestone and tasks",
        "AI will generate implementation code" if project_is_automation else "Start coding with FP directives"
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

- `get_project_status()` - Check initialization status
- `create_project_blueprint()` - Generate ProjectBlueprint.md from template and user input
- `detect_primary_language()` - Infer language from existing files
- `scan_existing_files()` - Detect existing project structure
- `infer_architecture()` - Analyze code to determine architectural patterns
- `load_schema(name)` - Load database schema SQL files

### Helper Functions Defined by Project Structure

**`create_project_blueprint(project_name, project_purpose, goals_json, language, build_tool, fp_strictness_level, existing_structure, use_case)`**
- Generates ProjectBlueprint.md from template
- Documents existing code structure for Use Case 1
- Sets up automation architecture documentation for Use Case 2
- Returns path to created blueprint

**`scan_existing_files(project_root)`**
- Scans project directory for existing code files
- Returns structure map: `{"src/": [...], "lib/": [...], "root": [...]}`
- Used to document existing project layout in blueprint

**`infer_architecture(project_root)`**
- Analyzes existing code patterns
- Detects architectural style (MVC, microservices, monolithic, etc.)
- Returns architecture description for blueprint

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

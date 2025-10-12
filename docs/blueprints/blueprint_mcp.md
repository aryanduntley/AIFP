# MCP Server Blueprint

## Overview

The AIFP MCP (Model Context Protocol) server provides **database-driven context delivery** to AI assistants, enabling instant access to project state, directives, and organizational structure. It acts as the **command router** and **state manager** for AIFP projects.

### Core Purpose

- **Instant Context Retrieval**: Query project state from `aifp_core.db` and `project.db`
- **Command Routing**: Parse `aifp run` commands and route to appropriate directives
- **Directive Execution**: Execute FP and project directives based on user intent
- **Helper Functions**: Provide utility functions for database operations, file I/O, Git integration
- **Read-Only Core**: `aifp_core.db` is read-only; only `project.db` is mutable

---

## Architecture

### Two-Database System

```
MCP Server
├── aifp_core.db (Read-Only)
│   ├── FP directives (60+)
│   ├── Project directives (21)
│   ├── Helper function definitions
│   ├── Tool schemas
│   └── AIFP standards and templates
│
└── project.db (Per-Project, Mutable)
    ├── Project-specific state
    ├── Files, functions, interactions
    ├── Tasks, subtasks, items
    ├── Themes, flows
    └── Completion path tracking
```

### MCP Server Location

**Two Deployment Models**:

1. **Global MCP Server** (Recommended):
   - Installed once in `~/.aifp/mcp-server/`
   - Serves all AIFP projects
   - Accesses `aifp_core.db` from global location
   - Opens `project.db` based on current working directory

2. **Per-Project MCP Server** (Alternative):
   - MCP server bundled with project in `.aifp-project/mcp-server/`
   - Self-contained deployment
   - Useful for isolated environments or CI/CD

---

## File Structure

### Global Installation

```
~/.aifp/
├── mcp-server/
│   ├── aifp_mcp_server.py          # Main MCP server entry point
│   ├── core/
│   │   ├── command_router.py       # Routes 'aifp run' commands
│   │   ├── directive_executor.py   # Executes directives
│   │   ├── database_manager.py     # Database connection management
│   │   └── intent_parser.py        # NLP intent detection
│   ├── tools/
│   │   ├── aifp_tools.py           # MCP tool definitions
│   │   └── tool_schemas.json       # Tool input/output schemas
│   ├── helpers/
│   │   ├── file_helpers.py         # File I/O operations
│   │   ├── db_helpers.py           # Database query helpers
│   │   ├── git_helpers.py          # Git integration
│   │   └── fp_helpers.py           # FP code generation utilities
│   └── aifp_core.db                # Read-only core database
│
└── config.json                      # Global AIFP configuration
```

### Per-Project Structure

```
/path/to/user/project/
├── .aifp-project/
│   ├── project.db                   # Project-specific mutable database
│   ├── config.json                  # Project-specific overrides
│   └── .git/ (if branch-based)     # Git repository for instance management
│
├── src/                             # User's source code (FP-compliant)
├── tests/
└── README.md
```

---

## MCP Tools

### Core Tools

#### 1. `aifp_run`
**Purpose**: Master command router - parses natural language intent and executes directives

**Input**:
```json
{
  "command": "Initialize project for matrix calculator",
  "project_root": "/path/to/project"
}
```

**Process**:
1. Parse intent using NLP and directive keywords
2. Determine confidence score
3. Route to appropriate directive(s)
4. Execute directive workflow
5. Return result to AI assistant

**Output**:
```json
{
  "success": true,
  "directive_executed": "project_init",
  "result": "Project initialized: MatrixCalculator",
  "db_updates": ["project", "completion_path", "milestones"],
  "next_steps": ["Define initial themes", "Create first task"]
}
```

#### 2. `aifp_query_directives`
**Purpose**: Search and retrieve directive information from `aifp_core.db`

**Input**:
```json
{
  "query_type": "by_keyword",
  "keyword": "purity"
}
```

**Output**:
```json
{
  "directives": [
    {
      "name": "fp_purity",
      "type": "fp",
      "description": "Enforces pure functions...",
      "workflow": {...},
      "confidence_threshold": 0.7
    }
  ]
}
```

#### 3. `aifp_query_project`
**Purpose**: Query project state from `project.db`

**Input**:
```json
{
  "query": "SELECT * FROM functions WHERE file_id = 5"
}
```

**Output**: Query results as JSON

#### 4. `aifp_get_context`
**Purpose**: Retrieve full project context for AI assistant

**Input**:
```json
{
  "context_type": "full",  // or "summary", "themes_only", "tasks_only"
  "project_root": "/path/to/project"
}
```

**Output**:
```json
{
  "project": {
    "name": "MatrixCalculator",
    "purpose": "Pure functional matrix operations",
    "status": "active"
  },
  "themes": [...],
  "flows": [...],
  "tasks": [...],
  "completion_progress": "35%"
}
```

#### 5. `aifp_update_db`
**Purpose**: Update `project.db` with new data (wrapper for project_update_db directive)

**Input**:
```json
{
  "table": "functions",
  "operation": "insert",
  "data": {
    "name": "multiply_matrices",
    "file_id": 5,
    "purpose": "Multiply two matrices",
    "parameters": "[\"a: Matrix\", \"b: Matrix\"]"
  }
}
```

#### 6. `aifp_git_status`
**Purpose**: Check Git status and detect code changes since last session

**Output**:
```json
{
  "current_branch": "main",
  "changed_files": ["src/matrix.py", "src/vector.py"],
  "themes_affected": ["matrix-operations", "vector-math"]
}
```

---

## Command Routing

### aifp run Logic

The `aifp run` command is the **universal entry point**:

```python
def aifp_run(command: str, project_root: str) -> dict:
    # 1. Parse intent
    intent = parse_intent(command)

    # 2. Match to directive
    directive = match_directive(intent, confidence_threshold=0.7)

    # 3. Check confidence
    if directive.confidence < 0.7:
        return prompt_user_for_clarification(intent)

    # 4. Execute directive
    result = execute_directive(directive, context={
        "project_root": project_root,
        "user_command": command
    })

    # 5. Update databases if needed
    if result.requires_db_update:
        update_project_db(result.db_changes)

    return result
```

### Intent Detection

**Keyword Matching**:
```python
intent_keywords = {
    "project_init": ["init", "initialize", "setup", "new project"],
    "project_task_decomposition": ["decompose", "break down", "create tasks"],
    "fp_purity": ["pure", "purity check", "side effects"],
    "project_completion_check": ["check completion", "done", "finished"]
}
```

**NLP-Based (Advanced)**:
- Use embeddings to match intent to directive descriptions
- Calculate cosine similarity between user command and directive descriptions
- Return directive with highest similarity > threshold

---

## Helper Functions

### Database Helpers (`db_helpers.py`)

#### `get_project_db(project_root: str) -> sqlite3.Connection`
Opens connection to `project.db` for the given project.

#### `get_core_db() -> sqlite3.Connection`
Opens read-only connection to `aifp_core.db`.

#### `query_functions(file_id: int) -> List[dict]`
Retrieve all functions for a given file.

#### `query_interactions(function_id: int) -> List[dict]`
Get all dependencies for a function.

#### `insert_function(data: dict) -> int`
Insert new function and return ID.

#### `update_task_status(task_id: int, status: str) -> bool`
Update task status and cascade to parent milestone/completion_path.

### File Helpers (`file_helpers.py`)

#### `read_file_safe(path: str) -> str`
Read file with error handling and encoding normalization.

#### `write_file_atomic(path: str, content: str) -> bool`
Write file atomically (write to temp, then rename).

#### `parse_aifp_metadata(content: str) -> dict`
Extract AIFP_METADATA from file comments.

#### `generate_aifp_header(function_data: dict) -> str`
Generate AIFP_METADATA comment block.

### Git Helpers (`git_helpers.py`)

#### `get_current_branch() -> str`
Get current Git branch.

#### `get_changed_files_since(commit_hash: str) -> List[str]`
Get files changed since specific commit.

#### `create_branch(branch_name: str, from_branch: str = "main") -> bool`
Create new Git branch (for instance management).

#### `detect_code_changes() -> dict`
Compare current Git HEAD with last known state in `project.db`.

### FP Helpers (`fp_helpers.py`)

#### `is_function_pure(function_code: str) -> tuple[bool, List[str]]`
Static analysis to detect impurity (returns violations).

#### `generate_result_type(language: str) -> str`
Generate Result/Either type boilerplate for target language.

#### `convert_loop_to_recursion(loop_code: str) -> str`
Transform imperative loop into tail-recursive function.

#### `generate_adt_boilerplate(adt_name: str, variants: List[str], language: str) -> str`
Generate algebraic data type definition.

---

## Directive Execution

### Execution Flow

```python
class DirectiveExecutor:
    def execute(self, directive: Directive, context: dict) -> ExecutionResult:
        # 1. Load directive workflow
        workflow = directive.workflow

        # 2. Execute trunk
        trunk_result = self.execute_step(workflow.trunk, context)

        # 3. Evaluate branches
        for branch in workflow.branches:
            if self.evaluate_condition(branch.if_condition, trunk_result, context):
                branch_result = self.execute_step(branch.then_action, context)

                # Handle special actions
                if branch.then_action == "prompt_user":
                    return self.prompt_user_interactive(branch.details)

                elif branch.then_action == "update_functions_table":
                    self.update_db("functions", branch.details, context)

                elif branch.then_action.startswith("call_"):
                    # Cross-directive call
                    other_directive = branch.then_action[5:]
                    return self.execute(load_directive(other_directive), context)

        # 4. Fallback
        if not any_branch_matched:
            return self.execute_fallback(workflow.fallback, context)

        return ExecutionResult(success=True, data=trunk_result)
```

### Cross-Directive Calls

When a directive calls another directive:

```json
{
  "if": "file_ready_to_write",
  "then": "call_fp_purity",
  "details": {"function_code": "extracted_function"}
}
```

The executor:
1. Loads `fp_purity` directive
2. Passes `function_code` as context
3. Executes `fp_purity` workflow
4. Returns result to calling directive
5. Continues execution based on result

---

## Database-Driven Context

### Why Database-Driven?

Traditional AI assistants lack persistent memory across sessions. AIFP solves this with:

**Instant Context Retrieval**:
```sql
-- Get all functions in authentication theme
SELECT f.name, f.purpose, f.parameters
FROM functions f
JOIN files fi ON f.file_id = fi.id
JOIN file_flows ff ON fi.id = ff.file_id
JOIN flows fl ON ff.flow_id = fl.id
WHERE fl.name = 'authentication-flow';
```

**Cross-Session Persistence**:
- Session 1: AI creates functions, stores in `functions` table
- Session 2 (days later): AI queries `functions` table, knows what was built
- No need to re-read source code or reconstruct context

**Relationship Tracking**:
```sql
-- Get all functions that depend on `calculate_total`
SELECT f2.name, f2.file_id
FROM interactions i
JOIN functions f1 ON i.source_function_id = f1.id
JOIN functions f2 ON i.target_function_id = f2.id
WHERE f1.name = 'calculate_total';
```

---

## Configuration

### Global Config (`~/.aifp/config.json`)

```json
{
  "version": "1.0.0",
  "mcp_server": {
    "port": 5000,
    "host": "localhost",
    "log_level": "INFO"
  },
  "databases": {
    "core_db_path": "~/.aifp/aifp_core.db",
    "project_db_name": "project.db"
  },
  "directives": {
    "default_confidence_threshold": 0.7,
    "enable_low_confidence_prompts": true
  },
  "git": {
    "auto_init": true,
    "default_branch": "main",
    "branch_based_instances": true
  },
  "fp_standards": {
    "enforce_purity": true,
    "block_oop": true,
    "require_metadata": true
  }
}
```

### Project Config (`.aifp-project/config.json`)

```json
{
  "project_name": "MatrixCalculator",
  "primary_language": "python",
  "fp_strictness": "high",
  "custom_directives": [],
  "ignored_paths": ["node_modules/", "venv/", "__pycache__/"],
  "completion_criteria": {
    "test_coverage_minimum": 80,
    "documentation_required": true
  }
}
```

---

## Tool Schemas

### MCP Tool Schema Example

```json
{
  "name": "aifp_run",
  "description": "Execute AIFP command with natural language intent",
  "input_schema": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "Natural language command (e.g., 'Initialize project for calculator')"
      },
      "project_root": {
        "type": "string",
        "description": "Absolute path to project root"
      }
    },
    "required": ["command", "project_root"]
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "success": {"type": "boolean"},
      "directive_executed": {"type": "string"},
      "result": {"type": "string"},
      "db_updates": {"type": "array", "items": {"type": "string"}},
      "next_steps": {"type": "array", "items": {"type": "string"}}
    }
  }
}
```

---

## Error Handling

### Graceful Degradation

```python
def execute_directive_safe(directive: Directive, context: dict) -> ExecutionResult:
    try:
        return execute_directive(directive, context)
    except DatabaseError as e:
        log_error(f"Database error in {directive.name}: {e}")
        return ExecutionResult(
            success=False,
            error="Database connection failed",
            fallback_action="prompt_user"
        )
    except DirectiveError as e:
        log_error(f"Directive execution failed: {e}")
        return ExecutionResult(
            success=False,
            error=str(e),
            fallback_action="escalate_to_markdown"
        )
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return ExecutionResult(
            success=False,
            error="Unknown error",
            fallback_action="prompt_user"
        )
```

### Rollback Support

When directives modify database:

```python
def execute_with_rollback(directive: Directive, context: dict) -> ExecutionResult:
    conn = get_project_db(context["project_root"])
    conn.execute("BEGIN TRANSACTION")

    try:
        result = execute_directive(directive, context)

        if result.success:
            conn.execute("COMMIT")
        else:
            conn.execute("ROLLBACK")

        return result
    except Exception as e:
        conn.execute("ROLLBACK")
        raise
```

---

## Deployment

### Installation

```bash
# Global installation
pip install aifp-mcp-server

# Initialize AIFP
aifp init --global

# This creates:
# ~/.aifp/mcp-server/
# ~/.aifp/aifp_core.db
# ~/.aifp/config.json
```

### Project Initialization

```bash
cd /path/to/project
aifp init

# This creates:
# .aifp-project/
# .aifp-project/project.db
# .aifp-project/config.json
```

### MCP Server Startup

```bash
# Start MCP server (global)
aifp serve --port 5000

# Or as systemd service
systemctl start aifp-mcp-server
```

### AI Assistant Integration

In Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aifp": {
      "command": "aifp",
      "args": ["serve", "--stdio"],
      "env": {
        "AIFP_CONFIG_PATH": "~/.aifp/config.json"
      }
    }
  }
}
```

---

## Performance Considerations

### Database Connection Pooling

```python
class DatabaseManager:
    def __init__(self):
        self.core_conn = sqlite3.connect("~/.aifp/aifp_core.db")
        self.project_connections = {}  # Pool of project DB connections

    def get_project_db(self, project_root: str) -> sqlite3.Connection:
        if project_root not in self.project_connections:
            db_path = f"{project_root}/.aifp-project/project.db"
            self.project_connections[project_root] = sqlite3.connect(db_path)
        return self.project_connections[project_root]
```

### Directive Caching

```python
class DirectiveCache:
    def __init__(self):
        self.cache = {}

    def load_directive(self, name: str) -> Directive:
        if name not in self.cache:
            self.cache[name] = self._load_from_db(name)
        return self.cache[name]
```

### Query Optimization

- Index all foreign keys in `project.db`
- Use prepared statements for common queries
- Batch database updates when possible

---

## Summary

The AIFP MCP server provides:

- **Database-driven context** for instant AI access to project state
- **Command routing** via `aifp run` with intent detection
- **Directive execution** for both FP and project directives
- **Helper functions** for database, file, Git, and FP operations
- **Two-database architecture**: Read-only `aifp_core.db` + mutable `project.db`
- **MCP tools** for AI assistant integration
- **Error handling** with graceful degradation and rollback support
- **Performance optimization** through caching and connection pooling

It acts as the **central nervous system** of AIFP, coordinating all project operations and providing AI assistants with comprehensive, persistent project understanding.

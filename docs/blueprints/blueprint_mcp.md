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
│   ├── Project directives (25)
│   ├── Helper function definitions
│   ├── Tool schemas
│   └── AIFP standards and templates
│
└── project.db (Per-Project, Mutable)
    ├── Project-specific state
    ├── Project table (with blueprint_checksum field)
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
**Purpose**: Gateway and reminder that AIFP directives should be applied - does NOT execute directives itself

**Input**:
```json
{
  "command": "Initialize project for matrix calculator",
  "project_root": "/path/to/project"
}
```

**Process**:
1. Receives command from AI
2. Returns guidance message to AI
3. AI decides what to do next based on guidance

**Output** (always the same simple response):
```json
{
  "success": true,
  "message": "AIFP MCP available",
  "guidance": {
    "directive_access": "Call get_all_directives() if you don't have them in memory. Call get_directive(name) for specific directive details.",
    "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
    "assumption": "Always assume AIFP applies unless user explicitly rejects it.",
    "available_helpers": ["get_all_directives", "get_directive", "get_project_context", "get_project_status"]
  }
}
```

**AI Response Pattern**:
1. AI receives guidance
2. AI evaluates: Is this coding or project management?
3. AI checks: Do I have directives in memory?
   - No → Call `get_all_directives()`
   - Yes → Apply appropriate directives
4. AI executes according to directive workflows

#### 2. `get_all_directives`
**Purpose**: Retrieve all directives and self-assessment questions from `aifp_core.db`

**Input**: None required

**Output**:
```json
{
  "success": true,
  "directive_count": 89,
  "directives": [
    {
      "name": "fp_purity",
      "type": "fp",
      "description": "Enforces pure functions...",
      "workflow": {...},
      "confidence_threshold": 0.7
    },
    // ... all ~89 directives
  ],
  "self_assessment_questions": [
    "Is this coding or project management?",
    "Do I have directives in memory?",
    "Which directives apply (FP vs Project)?",
    "Is action-reaction needed?"
  ],
  "action_reaction_model": {
    "code_write": "FP directives → compliance check → project_file_write → DB update",
    "file_edit": "FP validation → project_file_write → DB sync",
    "discussion_decision": "Check for project decisions → update project.db if applicable"
  }
}
```

**When AI Calls This**:
- First interaction with AIFP project (no directives in memory)
- Lost directive context (e.g., after context compression)
- Needs to refresh directive details

#### 3. `get_directive`
**Purpose**: Retrieve specific directive details from `aifp_core.db`

**Input**:
```json
{
  "name": "fp_purity"
}
```

**Output**:
```json
{
  "success": true,
  "directive": {
    "name": "fp_purity",
    "type": "fp",
    "description": "Enforces pure functions...",
    "workflow": {...},
    "roadblocks_json": [...],
    "intent_keywords_json": [...],
    "confidence_threshold": 0.7
  }
}
```

#### 4. `search_directives`
**Purpose**: Search and filter directives by keyword, category, or type

**Input**:
```json
{
  "keyword": "purity",           // Optional: search in name, description, intent_keywords
  "category": "purity",          // Optional: filter by category
  "type": "fp"                   // Optional: filter by type (fp, project, user_pref)
}
```

**Output**:
```json
{
  "success": true,
  "matches": [
    {
      "name": "fp_purity",
      "type": "fp",
      "category": "purity",
      "description": "Enforces pure functions...",
      "confidence_score": 0.95
    },
    {
      "name": "fp_state_elimination",
      "type": "fp",
      "category": "purity",
      "description": "Eliminates global state...",
      "confidence_score": 0.82
    }
  ]
}
```

**When AI Uses This**:
- Looking for directives related to specific concept
- Needs to find all directives in a category
- Filtering by type (FP vs Project vs User Pref)

#### 5. `query_mcp_db`
**Purpose**: Execute read-only SQL query on `aifp_core.db` for advanced cases

**Input**:
```json
{
  "sql": "SELECT name, type FROM directives WHERE confidence_threshold > 0.8"
}
```

**Output**:
```json
{
  "success": true,
  "rows": [
    {"name": "fp_purity", "type": "fp"},
    {"name": "project_init", "type": "project"}
  ]
}
```

**Guidance**:
- ✅ Use specific helpers (`get_all_directives`, `search_directives`) when possible
- ✅ Use this for complex queries not covered by helpers
- ⚠️ Read-only - no INSERT/UPDATE/DELETE allowed

#### 6. `get_project_context`
**Purpose**: Retrieve full project context from `project.db`

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
    "status": "active",
    "version": 1
  },
  "themes": [...],
  "flows": [...],
  "tasks": [...],
  "completion_progress": "35%",
  "functions_count": 12,
  "files_count": 5
}
```

#### 7. `get_project_status`
**Purpose**: Check if project is initialized and get current status

**Input**:
```json
{
  "project_root": "/path/to/project"
}
```

**Output**:
```json
{
  "initialized": true,
  "project_db_exists": true,
  "project": {
    "name": "MatrixCalculator",
    "status": "active",
    "version": 1
  }
}
```

**Note**: Should be called before `project_init` to avoid re-initializing existing projects

#### 8. `get_project_files`
**Purpose**: Retrieve list of all files in project

**Input**:
```json
{
  "project_root": "/path/to/project",
  "language": "python"  // Optional filter
}
```

**Output**:
```json
{
  "success": true,
  "files": [
    {
      "id": 1,
      "path": "src/matrix.py",
      "language": "python",
      "checksum": "abc123...",
      "created_at": "2025-10-14T10:00:00Z"
    }
  ]
}
```

#### 9. `get_project_functions`
**Purpose**: Retrieve functions, optionally filtered by file

**Input**:
```json
{
  "project_root": "/path/to/project",
  "file_id": 5  // Optional: filter by specific file
}
```

**Output**:
```json
{
  "success": true,
  "functions": [
    {
      "id": 12,
      "name": "multiply_matrices",
      "file_id": 5,
      "purpose": "Multiply two matrices",
      "parameters": ["a: Matrix", "b: Matrix"]
    }
  ]
}
```

#### 10. `get_project_tasks`
**Purpose**: Retrieve tasks, milestones, and completion path info

**Input**:
```json
{
  "project_root": "/path/to/project",
  "status": "pending"  // Optional: filter by status
}
```

**Output**:
```json
{
  "success": true,
  "completion_path": [...],
  "milestones": [...],
  "tasks": [
    {
      "id": 3,
      "name": "Implement matrix multiplication",
      "status": "pending",
      "milestone_id": 1
    }
  ]
}
```

#### 11. `query_project_db`
**Purpose**: Execute read-only SQL query on `project.db` for advanced cases

**Input**:
```json
{
  "project_root": "/path/to/project",
  "sql": "SELECT f.name, fi.path FROM functions f JOIN files fi ON f.file_id = fi.id WHERE fi.language = 'python'"
}
```

**Output**:
```json
{
  "success": true,
  "rows": [
    {"name": "multiply_matrices", "path": "src/matrix.py"}
  ]
}
```

**Guidance**:
- ✅ Use specific helpers (`get_project_files`, `get_project_functions`, `get_project_tasks`) when possible
- ✅ Use this for complex queries not covered by helpers
- ⚠️ Read-only - no INSERT/UPDATE/DELETE allowed
- ❌ **All writes must go through directives** (e.g., `project_file_write` → auto DB update)

---

## Helper Function Philosophy

### Read Operations (Safe)

**MCP Database Helpers** (aifp_core.db - read-only):
- `get_all_directives()` - Complete directive list
- `get_directive(name)` - Specific directive
- `search_directives(keyword, category, type)` - Filter directives
- `query_mcp_db(sql)` - Advanced read queries

**Project Database Helpers** (project.db - read-only):
- `get_project_context(type)` - Structured overview
- `get_project_status()` - Initialization check
- `get_project_files(language)` - File list
- `get_project_functions(file_id)` - Function list
- `get_project_tasks(status)` - Task/milestone list
- `query_project_db(sql)` - Advanced read queries

### Write Operations (Directive-Only)

⚠️ **CRITICAL**: Project database writes **ONLY** through directive workflows

**Correct Flow**:
```
Code write → FP directives (purity, immutability) → project_file_write directive → Auto DB update
Task creation → project_task_decomposition directive → Auto DB update
Decision made → project_evolution directive → Auto DB update
```

**No Direct Write Helpers** - All writes validated through directives to ensure:
- FP compliance
- Data consistency
- Directive workflow tracking
- Cross-table integrity

---

#### 6. `aifp_git_status` (DEPRECATED - REMOVE)
**Purpose**: Check Git status and detect code changes since last session

**Note**: This tool may be replaced by Git-specific directives in future versions

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

## AIFP Gateway Pattern

### `aifp_run` Logic

The `aifp_run` command is a **gateway and reminder**, NOT an executor:

```python
def aifp_run(command: str, project_root: str) -> dict:
    """
    Simple gateway that returns guidance to AI.
    AI decides what to do based on guidance.
    """
    return {
        "success": True,
        "message": "AIFP MCP available",
        "guidance": {
            "directive_access": "Call get_all_directives() if needed. Call get_directive(name) for specific details.",
            "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
            "assumption": "Always assume AIFP applies unless user explicitly rejects it.",
            "available_helpers": ["get_all_directives", "get_directive", "get_project_context", "get_project_status"]
        }
    }
```

### AI Decision Process

After receiving `aifp_run` guidance, AI follows this process:

```python
# AI internal logic (not in MCP server)
def ai_process_aifp_command(command: str):
    # 1. Receive guidance from aifp_run
    guidance = call_tool("aifp_run", {"command": command})

    # 2. Evaluate task type
    is_coding = detect_coding_task(command)
    is_project_management = detect_project_management_task(command)

    # 3. Check directive memory
    if not has_directives_in_memory():
        directives = call_tool("get_all_directives")
        cache_in_memory(directives)

    # 4. For coding tasks: Apply FP directives THEN project directives
    if is_coding:
        # Write code following FP directives
        code = generate_code_with_fp_directives(command)

        # Verify FP compliance
        verify_fp_compliance(code)

        # Apply project management directive
        execute_project_file_write(code)

    # 5. For project management: Apply project directives
    elif is_project_management:
        match_and_execute_project_directive(command)

    # 6. For simple discussion: No directives needed
    else:
        respond_directly(command)
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

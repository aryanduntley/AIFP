# Interactions Blueprint

## Overview

This document describes how **directives, databases, and the MCP server interact** to create a cohesive AIFP system. It covers cross-directive calls, database update patterns, workflow orchestration, and the complete lifecycle of an AIFP command.

---

## System Components

### Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│         AI Assistant (Claude)           │
│  - Sends natural language commands      │
│  - Receives structured responses        │
└────────────────┬────────────────────────┘
                 │ MCP Protocol
┌────────────────▼────────────────────────┐
│           MCP Server                     │
│  - Routes commands to directives        │
│  - Executes directive workflows         │
│  - Manages database connections         │
│  - Calls helper functions               │
└────────┬────────────────────────────────┘
         │
         ├──────────────────────┬─────────┐
         │                      │         │
┌────────▼────────┐  ┌─────────▼──────┐  │
│  aifp_core.db   │  │  project.db    │  │
│  (Read-Only)    │  │  (Mutable)     │  │
│                 │  │                │  │
│  - Directives   │  │  - Project     │  │
│  - Helpers      │  │    state       │  │
│  - Standards    │  │  - Code        │  │
│  - Templates    │  │    tracking    │  │
└─────────────────┘  └────────────────┘  │
                                         │
                     ┌───────────────────▼────┐
                     │  Git Repository        │
                     │  - Source code         │
                     │  - Version control     │
                     │  - Branch management   │
                     └────────────────────────┘
```

---

## Interaction Patterns

### 1. Command Flow: User → AI → MCP → Directives

```
User: "Initialize AIFP for my calculator project"
  ↓
AI Assistant (Claude):
  - Parses user intent
  - Calls MCP tool: aifp_run("Initialize AIFP for my calculator project", "/path/to/project")
  ↓
MCP Server:
  - Queries aifp_core.db for intent keywords ["initialize", "init", "AIFP"]
  - Finds directive: project_init (confidence: 0.95)
  - Loads project_init workflow from aifp_core.db
  ↓
project_init Directive Execution:
  trunk: check_existing_project
    ├─ Checks if .aifp-project/ exists
    ├─ Branch: new_project → create_aifp_structure
    │   ├─ Creates .aifp-project/ directory
    │   ├─ Initializes project.db with schema
    │   ├─ Calls project_structure_definition
    │   └─ Calls project_db_init
    └─ Updates project.db:
        - INSERT INTO project (name, purpose, goals_json)
        - INSERT INTO completion_path (initial milestones)
  ↓
MCP Server:
  - Returns ExecutionResult to AI
  ↓
AI Assistant:
  - Formats response for user
  - "✅ Project initialized: Calculator. Next: Define themes and create first task."
```

---

### 2. Cross-Directive Calls

#### Example: project_file_write → FP Directives

```
project_file_write Directive:
  trunk: validate_file_path_and_content
    ├─ Path valid? Yes
    ├─ Branch: call_fp_directives_for_compliance
    │   ├─ Load function code from request
    │   ├─ Call fp_purity (context: {function_code: "..."})
    │   │   └─ fp_purity analyzes code
    │   │       ├─ Detects global state access
    │   │       ├─ Branch: external_state_access → isolate_side_effects
    │   │       ├─ Refactors code to pass state as parameter
    │   │       └─ Returns: {success: true, refactored_code: "..."}
    │   ├─ Call fp_immutability (context: {function_code: refactored_code})
    │   │   └─ fp_immutability checks for mutations
    │   │       ├─ No mutations detected
    │   │       └─ Returns: {success: true, compliant: true}
    │   └─ All FP checks passed
    ├─ Branch: fp_compliance_passed → write_file_to_disk
    │   └─ Writes refactored_code to file
    ├─ Branch: file_written → update_database_tables
    │   ├─ INSERT INTO files (path, language, checksum)
    │   ├─ INSERT INTO functions (name, file_id, purpose, purity_level='pure')
    │   ├─ INSERT INTO interactions (for function dependencies)
    │   └─ Calls project_update_db for consistency
    └─ Returns: {success: true, file_path: "src/calc.py"}
```

**Key Points**:
- Directives can **call other directives** via `"then": "call_fp_purity"`
- Context is passed between directive calls
- Each directive returns result to caller
- Database updates happen after all validations pass

---

### 3. Database Update Patterns

#### Pattern A: Direct Update (Simple)

```python
# project_task_update directive
def execute(context):
    task_id = context['task_id']
    new_status = context['status']

    # Direct database update
    conn.execute("""
        UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_status, task_id))

    return ExecutionResult(success=True)
```

#### Pattern B: Transactional Update (Complex)

```python
# project_file_write directive
def execute(context):
    conn = get_project_db(context['project_root'])
    conn.execute("BEGIN TRANSACTION")

    try:
        # 1. Insert file
        file_id = conn.execute("""
            INSERT INTO files (path, language, checksum, project_id)
            VALUES (?, ?, ?, ?)
        """, (path, language, checksum, 1)).lastrowid

        # 2. Insert functions
        for func in extracted_functions:
            func_id = conn.execute("""
                INSERT INTO functions (name, file_id, purpose, purity_level)
                VALUES (?, ?, ?, ?)
            """, (func['name'], file_id, func['purpose'], 'pure')).lastrowid

            # 3. Insert interactions
            for dep in func['dependencies']:
                conn.execute("""
                    INSERT INTO interactions (source_function_id, target_function_id, interaction_type)
                    VALUES (?, ?, 'call')
                """, (func_id, dep['target_id']))

        conn.execute("COMMIT")
        return ExecutionResult(success=True)

    except Exception as e:
        conn.execute("ROLLBACK")
        return ExecutionResult(success=False, error=str(e))
```

#### Pattern C: Cascading Update (Hierarchical)

```python
# project_task_update with cascade
def execute(context):
    task_id = context['task_id']
    conn.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))

    # Check if all tasks in milestone are completed
    milestone_id = conn.execute("SELECT milestone_id FROM tasks WHERE id = ?", (task_id,)).fetchone()[0]

    all_completed = conn.execute("""
        SELECT COUNT(*) = 0 FROM tasks
        WHERE milestone_id = ? AND status != 'completed'
    """, (milestone_id,)).fetchone()[0]

    if all_completed:
        # Cascade: Mark milestone as completed
        conn.execute("UPDATE milestones SET status = 'completed' WHERE id = ?", (milestone_id,))

        # Check completion_path progress
        completion_path_id = conn.execute("SELECT completion_path_id FROM milestones WHERE id = ?", (milestone_id,)).fetchone()[0]
        # ... update completion_path if all milestones done

    return ExecutionResult(success=True)
```

---

### 4. Workflow Orchestration

#### Hierarchical Directive Calls

```
project_run (Level 0: Master Router)
  ↓ routes to
project_task_decomposition (Level 1: High-Level Coordination)
  ├─ Analyzes user goal
  ├─ Creates hierarchical task structure
  ├─ Calls project_update_db (Level 2: Operational)
  │   └─ INSERT INTO tasks, subtasks, items
  ├─ For each task:
  │   └─ Calls project_themes_flows_init (Level 1)
  │       └─ Creates themes/flows
  │       └─ Calls project_update_db
  │           └─ INSERT INTO themes, flows, flow_themes
  └─ Returns complete task tree
```

**Key Points**:
- Higher-level directives orchestrate lower-level directives
- Each level has specific responsibilities
- Database updates happen at Level 2 (project_update_db)
- Level 3 (State Management) validates and syncs

---

### 5. FP ↔ Project Integration

#### Project Calls FP

```
project_file_write
  └─ Calls fp_purity, fp_immutability, fp_side_effect_detection
      └─ FP directives analyze code
      └─ Return compliance status
  └─ If compliant: write file + update project.db
  └─ If non-compliant: refactor and retry
```

#### Project Uses FP Results

```
project_compliance_check
  └─ Queries project.db for all functions
  └─ For each function:
      └─ Loads function code from file
      └─ Calls relevant FP directives
      └─ Collects violations
  └─ Generates compliance report
  └─ Writes violations to notes table
```

#### FP Updates Project Database

```
fp_purity (executed via project_file_write)
  └─ Analyzes function for purity
  └─ If impure: refactors code
  └─ Returns: {refactored_code: "...", purity_level: "pure"}
  └─ Caller (project_file_write):
      └─ UPDATE functions SET purity_level = 'pure', side_effects_json = 'null'
```

---

### 6. Git Integration Points

#### Session Boot Detection

```
MCP Server Startup:
  └─ Calls aifp_git_status helper
      └─ Queries project.db for last_known_git_hash
      └─ Compares with current Git HEAD
      └─ If different:
          ├─ Detects changed files since last session
          ├─ Queries project.db to find affected themes/flows
          ├─ Updates project.db with new Git state
          └─ Notifies AI of external code changes
```

#### Git Branch-Based Workflow

```
User: "Create instance for authentication work"
  ↓
AI calls: aifp_run("Create instance for authentication work")
  ↓
MCP routes to: (hypothetical future directive: project_instance_create)
  ↓
project_instance_create:
  └─ Calls git_create_branch helper
      └─ git checkout -b aifp-branch-001 main
  └─ Updates project.db (or separate instance DB)
      └─ INSERT INTO instance_branches (branch_name, purpose)
  └─ Returns: {branch: "aifp-branch-001", status: "active"}
```

---

## Data Flow Diagrams

### Complete Write Operation

```
User Command
  ↓
AI Assistant
  ↓ (MCP tool call)
MCP Server: aifp_run("Write function multiply(a, b)")
  ↓
Intent Parser
  ├─ Extracts keywords: ["write", "function"]
  ├─ Queries aifp_core.db.intent_keywords
  └─ Matches: project_file_write (confidence: 0.88)
  ↓
Directive Executor: Load project_file_write
  ↓
project_file_write workflow:
  trunk: validate_file_path_and_content
    ├─ Path: "src/math.py" (valid)
    ├─ Function code: "def multiply(a, b): return a * b"
    └─ Branch: call_fp_directives_for_compliance
        ├─ Call fp_purity
        │   └─ Analysis: Pure function ✓
        ├─ Call fp_immutability
        │   └─ Analysis: No mutations ✓
        └─ All checks passed
    ↓
  Branch: write_file_to_disk
    └─ Write "src/math.py" with function code
    ↓
  Branch: update_database_tables
    ├─ BEGIN TRANSACTION
    ├─ INSERT INTO files (path="src/math.py", language="python", checksum="abc123")
    │   └─ Returns file_id: 5
    ├─ INSERT INTO functions (name="multiply", file_id=5, purpose="Multiply two numbers", purity_level="pure")
    │   └─ Returns func_id: 42
    ├─ No dependencies detected (simple function)
    ├─ COMMIT
    └─ Call project_metadata_sync
        └─ Verifies file metadata matches database
    ↓
Return ExecutionResult:
  {
    success: true,
    file_path: "src/math.py",
    function_id: 42,
    db_updates: ["files", "functions"]
  }
  ↓
MCP Server formats response
  ↓
AI Assistant
  ↓
User: "✅ Function multiply written to src/math.py. Function ID: 42."
```

---

### Complete Read/Query Operation

```
User: "What functions depend on calculate_total?"
  ↓
AI calls: aifp_query_project({query: "SELECT ... FROM interactions WHERE ..."})
  ↓
MCP Server:
  ├─ Opens project.db connection
  ├─ Executes query:
  │   SELECT f2.name, f2.purpose
  │   FROM interactions i
  │   JOIN functions f1 ON i.target_function_id = f1.id
  │   JOIN functions f2 ON i.source_function_id = f2.id
  │   WHERE f1.name = 'calculate_total'
  ├─ Returns results: [
  │     {name: "process_invoice", purpose: "Process invoice totals"},
  │     {name: "generate_report", purpose: "Generate financial report"}
  │   ]
  └─ Formats as JSON
  ↓
AI Assistant formats for user
  ↓
User: "Functions that depend on calculate_total:
       • process_invoice: Process invoice totals
       • generate_report: Generate financial report"
```

---

## Error Handling Interactions

### Directive Failure Propagation

```
project_file_write
  ├─ Calls fp_purity
  │   └─ Returns: {success: false, error: "Global state detected"}
  ├─ Branch: fp_compliance_failed → refactor_code_and_retry
  │   ├─ Attempts automatic refactor
  │   ├─ Retry fp_purity
  │   └─ If still fails:
  │       └─ Branch: low_confidence → prompt_user
  │           └─ Returns to AI with clarification request
  └─ AI receives ExecutionResult:
      {
        success: false,
        error: "Function uses global state",
        user_prompt: "How should global variable 'config' be handled?",
        suggestions: ["Pass as parameter", "Use dependency injection"]
      }
```

### Database Error Recovery

```
project_update_db
  ├─ BEGIN TRANSACTION
  ├─ INSERT INTO tasks (...)
  │   └─ Error: FOREIGN KEY constraint failed (invalid milestone_id)
  ├─ ROLLBACK
  └─ error_handling: on_failure → prompt_user
      └─ Returns ExecutionResult:
          {
            success: false,
            error: "Invalid milestone_id: 999",
            fallback_action: "prompt_user",
            roadblock_logged: true
          }
      └─ Logs to notes table:
          INSERT INTO notes (content, note_type, reference_table)
          VALUES ('Database constraint violation: invalid milestone_id', 'roadblock', 'tasks')
```

---

## Configuration Interactions

### MCP Server Uses Both Databases

```python
class MCPServer:
    def __init__(self):
        # Read-only connection to core database
        self.core_db = sqlite3.connect("~/.aifp/aifp_core.db?mode=ro", uri=True)

        # Mutable connection to project database (per-project)
        self.project_db_connections = {}  # Keyed by project_root

    def get_project_db(self, project_root: str):
        if project_root not in self.project_db_connections:
            db_path = f"{project_root}/.aifp-project/project.db"
            self.project_db_connections[project_root] = sqlite3.connect(db_path)
        return self.project_db_connections[project_root]

    def execute_directive(self, directive_name: str, context: dict):
        # Load directive from core DB
        directive = self.core_db.execute("""
            SELECT workflow_json FROM directives WHERE name = ?
        """, (directive_name,)).fetchone()[0]

        # Execute with project DB context
        project_db = self.get_project_db(context['project_root'])
        return DirectiveExecutor(directive, project_db).execute(context)
```

---

## Summary: Complete Interaction Flow

```
1. User Intent
   └─ AI Assistant parses and calls MCP tool

2. MCP Server Routing
   ├─ Queries aifp_core.db for directive matching
   ├─ Loads directive workflow
   └─ Initializes directive executor

3. Directive Execution
   ├─ Executes trunk step
   ├─ Evaluates branches
   ├─ Calls other directives (cross-directive)
   ├─ Calls helper functions (database, file, git)
   └─ Updates project.db (transactional)

4. Database Updates
   ├─ project.db: Mutable project state
   ├─ aifp_core.db: Read-only knowledge base
   └─ Cascading updates via triggers/logic

5. Git Integration (Optional)
   ├─ Detects external code changes
   ├─ Creates/manages branches (future)
   └─ Syncs with project.db state

6. Result Return
   ├─ Directive returns ExecutionResult
   ├─ MCP server formats response
   └─ AI assistant presents to user

7. Error Handling
   ├─ Graceful degradation
   ├─ User prompts for ambiguity
   ├─ Rollback on database failures
   └─ Logging to notes table
```

---

## Best Practices for Interactions

1. **Always pass context** between directive calls
2. **Use transactions** for multi-table updates
3. **Log to notes** for AI memory
4. **Validate before writing** (FP compliance checks)
5. **Cascade updates** intelligently (milestones → completion_path)
6. **Fail gracefully** with user prompts
7. **Check confidence thresholds** before auto-execution
8. **Use roadblock resolutions** from aifp_core.db
9. **Keep core DB read-only** (never mutate)
10. **One project per project.db** (no shared state)

This interaction model ensures **predictable, traceable, and recoverable** operations across the entire AIFP system.

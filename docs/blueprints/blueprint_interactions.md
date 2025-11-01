# Interactions Blueprint

## Overview

This document describes how **directives, databases, and the MCP server interact** to create a cohesive AIFP system. It covers cross-directive calls, database update patterns, workflow orchestration, and the complete lifecycle of an AIFP command.

---

## System Components

### Three-Database Architecture

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
│  - Manages three database connections   │
│  - Calls helper functions               │
└─────┬─────────────────┬─────────────┬───┘
      │                 │             │
┌─────▼──────────┐ ┌────▼──────────┐ ┌▼─────────────────┐
│ aifp_core.db   │ │ project.db    │ │ user_prefs.db    │
│ (Read-Only)    │ │ (Mutable)     │ │ (Mutable)        │
│                │ │               │ │                  │
│ - Directives   │ │ - Project     │ │ - Directive      │
│ - Helpers      │ │   state       │ │   preferences    │
│ - Standards    │ │ - Code        │ │ - User settings  │
│ - Templates    │ │   tracking    │ │ - AI learning    │
│ - Categories   │ │ - Notes       │ │ - Tracking (opt) │
└────────────────┘ └───────────────┘ └──────────────────┘
                          │
                ┌─────────▼────────────┐
                │  Git Repository      │
                │  - Source code       │
                │  - Version control   │
                │  - Branch management │
                └──────────────────────┘
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

#### Pattern C: Completion Delegation (Hierarchical)

```python
# project_task_update delegates to completion directives
def execute(context):
    task_id = context['task_id']
    new_status = context['new_status']

    # Validate and update status
    conn.execute("UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                 (new_status, task_id))

    # Delegate to appropriate completion directive
    if new_status == 'completed':
        # Delegation: Call project_task_complete
        return trigger_directive('project_task_complete', {'task_id': task_id})

    return ExecutionResult(success=True)

# project_task_complete handles post-completion workflow
def execute(context):
    task_id = context['task_id']

    # Mark task and items complete
    conn.execute("UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (task_id,))
    conn.execute("UPDATE items SET status = 'completed' WHERE reference_table = 'tasks' AND reference_id = ?", (task_id,))

    # Check milestone status
    milestone_id = conn.execute("SELECT milestone_id FROM tasks WHERE id = ?", (task_id,)).fetchone()[0]
    remaining_tasks = conn.execute("""
        SELECT COUNT(*) FROM tasks
        WHERE milestone_id = ? AND status NOT IN ('completed', 'cancelled')
    """, (milestone_id,)).fetchone()[0]

    if remaining_tasks == 0:
        # Milestone complete - delegate to project_milestone_complete
        return trigger_directive('project_milestone_complete', {'milestone_id': milestone_id})
    else:
        # Milestone not complete - engage user for next steps
        return review_next_steps(milestone_id)

    return ExecutionResult(success=True)

# project_milestone_complete handles next-milestone transition
def execute(context):
    milestone_id = context['milestone_id']

    # Mark milestone complete
    conn.execute("UPDATE milestones SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?", (milestone_id,))

    # Move to next milestone, create first task (with user input)
    return move_to_next_milestone(milestone_id)
```

**Benefits of Delegation**:
- Explicit separation: state management vs post-completion workflows
- User engagement built into completion directives
- Better error handling and traceability
- Easier to test each directive independently

---

### 4. Workflow Orchestration

#### Hierarchical Directive Calls

```
aifp_run (Level 0: Gateway)
  ├─ On continuation request ("continue", "status", "resume")
  │   └─ Calls aifp_status (Level 1)
  │       └─ Calls project_blueprint_read (Level 2)
  │           ├─ Reads .aifp/ProjectBlueprint.md
  │           ├─ Parses sections into structured data
  │           └─ Returns project context
  │       └─ Queries project.db for status tree (sidequests → subtasks → tasks)
  │       └─ Returns status report with context
  │
  ├─ Routes to project_task_decomposition (Level 1)
  │   ├─ First calls aifp_status for current context
  │   ├─ Analyzes user goal
  │   ├─ Creates hierarchical task structure
  │   └─ Calls project_update_db (Level 2)
  │       └─ INSERT INTO tasks, subtasks, items
  │
  └─ Routes to project_theme_flow_mapping (Level 3)
      ├─ Links files to themes/flows
      ├─ UPDATE themes, flows tables
      └─ If themes/flows changed:
          └─ Calls project_evolution (Level 4)
              └─ Calls project_blueprint_update (Level 2)
                  ├─ Backs up ProjectBlueprint.md
                  ├─ Updates section 3 (Themes & Flows)
                  ├─ Increments project.version
                  └─ UPDATE project.blueprint_checksum
```

**Key Points**:
- Higher-level directives orchestrate lower-level directives
- Each level has specific responsibilities
- Database updates happen at Levels 2-4 depending on scope
- New directives enable status-first continuation and blueprint management
- `aifp_status` is called proactively for context before task operations

#### New Cross-Directive Interactions (v1.1+)

**Status-First Pattern**:
```
aifp_run → aifp_status → project_blueprint_read
```
- Used when user requests continuation or status
- Provides full project context from ProjectBlueprint.md + database
- Enables historical context for task continuation

**Blueprint Update Pattern**:
```
project_theme_flow_mapping → project_evolution → project_blueprint_update
project_evolution → project_blueprint_update
```
- Triggered when project-wide changes occur (themes, flows, goals, architecture)
- Automatically updates ProjectBlueprint.md sections
- Maintains sync between blueprint and database via checksum

**Context-Aware Decomposition**:
```
project_task_decomposition → aifp_status
```
- Calls `aifp_status` before creating new tasks
- Ensures new tasks align with current work state
- Prevents duplicate or conflicting task creation

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

**Simplified Approach**: Git state (current branch, current hash) is queried from Git directly. Only AIFP-specific collaboration metadata stored in database.

#### Session Boot Detection (External Change Detection)

```
MCP Server Startup → git_sync_state directive:
  └─ Calls get_current_commit_hash() helper
      └─ git rev-parse HEAD → current_hash
  └─ Queries project.last_known_git_hash from project.db
  └─ If different:
      ├─ Calls git_detect_external_changes directive
      │   ├─ git diff --name-only <last_hash>..HEAD
      │   ├─ Queries project.db to find affected themes/flows/functions
      │   └─ Builds impact report
      ├─ Updates project.last_known_git_hash = current_hash
      ├─ Updates project.last_git_sync = now
      └─ Notifies AI of external code changes with impact analysis
```

**Key Insight**: No separate git_state table needed. Git commands are fast (~1ms) and eliminate duplication.

#### Git Branch-Based Workflow (Multi-User Collaboration)

```
User: "Alice wants to work on authentication"
  ↓
AI calls: git_create_branch directive
  ↓
git_create_branch execution:
  └─ Calls get_user_name_for_branch() helper
      ├─ git config user.name → "alice"
      └─ (or detects from $USER, prompts, etc.)
  └─ Queries work_branches table for max branch number
      └─ SELECT MAX(id) FROM work_branches WHERE user_name='alice'
      └─ Next: 001
  └─ Creates Git branch
      └─ git checkout -b aifp-alice-001 main
  └─ Stores collaboration metadata in work_branches table
      └─ INSERT INTO work_branches (branch_name, user_name, purpose, status)
      └─ VALUES ('aifp-alice-001', 'alice', 'authentication', 'active')
  └─ Returns: {branch: "aifp-alice-001", user: "alice", status: "active"}

Later: Merge with FP intelligence
  ↓
AI calls: git_merge_branch directive
  ↓
git_merge_branch execution:
  └─ Calls detect_conflicts_before_merge() helper
      ├─ Extracts project.db from both branches
      │   ├─ git show main:.aifp/project.db > main.db
      │   └─ git show aifp-alice-001:.aifp/project.db > alice.db
      ├─ Queries function metadata from both databases
      ├─ Applies FP conflict resolution rules:
      │   ├─ One pure, one impure → prefer pure (confidence: 0.9)
      │   ├─ Both pure, different tests → prefer more tests (0.8)
      │   └─ Dependencies differ → manual review (0.5)
      └─ Returns conflict analysis
  └─ Auto-resolves high-confidence conflicts (>0.8)
  └─ Presents low-confidence conflicts to user with AI recommendations
  └─ Executes merge: git merge aifp-alice-001
  └─ Logs to merge_history table with resolution details
  └─ Updates work_branches: status='merged', merged_at=now
```

**Key Features**:
- Branch naming: `aifp-{user}-{number}` (e.g., `aifp-alice-001`, `aifp-ai-claude-001`)
- FP-powered conflict resolution using purity levels
- Full audit trail in `merge_history` table
- Supports both human developers and autonomous AI instances

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

### MCP Server Uses Three Databases

```python
class MCPServer:
    def __init__(self):
        # Read-only connection to core database (global)
        self.core_db = sqlite3.connect("~/.aifp/aifp_core.db?mode=ro", uri=True)

        # Mutable connections to project databases (per-project)
        self.project_db_connections = {}  # Keyed by project_root

        # Mutable connections to user preferences databases (per-project)
        self.user_prefs_db_connections = {}  # Keyed by project_root

    def get_project_db(self, project_root: str):
        if project_root not in self.project_db_connections:
            db_path = f"{project_root}/.aifp-project/project.db"
            self.project_db_connections[project_root] = sqlite3.connect(db_path)
        return self.project_db_connections[project_root]

    def get_user_prefs_db(self, project_root: str):
        if project_root not in self.user_prefs_db_connections:
            db_path = f"{project_root}/.aifp-project/user_preferences.db"
            # Initialize if doesn't exist
            if not os.path.exists(db_path):
                self.init_user_preferences_db(db_path)
            self.user_prefs_db_connections[project_root] = sqlite3.connect(db_path)
        return self.user_prefs_db_connections[project_root]

    def execute_directive(self, directive_name: str, context: dict):
        # Load directive from core DB
        directive = self.core_db.execute("""
            SELECT workflow_json FROM directives WHERE name = ?
        """, (directive_name,)).fetchone()[0]

        # Get database connections
        project_db = self.get_project_db(context['project_root'])
        user_prefs_db = self.get_user_prefs_db(context['project_root'])

        # Sync user preferences before execution
        preferences = self.sync_preferences(user_prefs_db, directive_name)
        context['preferences'] = preferences

        # Execute with all DB contexts
        return DirectiveExecutor(directive, project_db, user_prefs_db).execute(context)
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

3. User Preferences Sync
   ├─ Checks user_preferences.db exists (creates if not)
   ├─ Loads directive-specific preferences
   ├─ Applies preferences to directive context
   └─ Checks tracking_settings for opt-in features

4. Directive Execution
   ├─ Executes trunk step with preferences applied
   ├─ Evaluates branches
   ├─ Calls other directives (cross-directive)
   ├─ Calls helper functions (database, file, git)
   └─ Updates project.db (transactional)

5. Database Updates
   ├─ aifp_core.db: Read-only knowledge base (never modified)
   ├─ project.db: Mutable project state (code tracking, notes, tasks)
   ├─ user_preferences.db: Mutable preferences (directive customization, opt-in tracking)
   └─ Cascading updates via triggers/logic

6. Git Integration (Optional)
   ├─ Detects external code changes
   ├─ Creates/manages branches (future)
   └─ Syncs with project.db state

7. Result Return
   ├─ Directive returns ExecutionResult
   ├─ MCP server formats response
   └─ AI assistant presents to user

8. Error Handling
   ├─ Graceful degradation
   ├─ User prompts for ambiguity
   ├─ Rollback on database failures
   └─ Important clarifications to project.db notes (not verbose logging)
```

---

## Best Practices for Interactions

1. **Always pass context** between directive calls
2. **Use transactions** for multi-table updates
3. **Write to notes** for AI memory and important clarifications only (not verbose logging)
4. **Validate before writing** (FP compliance checks)
5. **Cascade updates** intelligently (milestones → completion_path)
6. **Fail gracefully** with user prompts
7. **Check confidence thresholds** before auto-execution
8. **Use roadblock resolutions** from aifp_core.db
9. **Keep core DB read-only** (never mutate)
10. **One project per project.db** (no shared state)
11. **Sync preferences first** via user_preferences_sync before directive execution
12. **Respect tracking settings** (check user_preferences.db before logging)
13. **Logging goes to user_preferences.db** (opt-in), notes go to project.db (AI memory)

This interaction model ensures **predictable, traceable, customizable, and recoverable** operations across the entire AIFP system.

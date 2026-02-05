# AIFP: AI Functional Procedural Programming

> **A language-agnostic programming paradigm designed for AI-generated and AI-maintained codebases**

---

## Table of Contents

- [What is AIFP?](#what-is-aifp)
- [Core Principles](#core-principles)
- [Architecture Overview](#architecture-overview)
- [Four-Database System](#four-database-system)
- [How It Works](#how-it-works)
- [Getting Started](#getting-started)
- [Directives System](#directives-system)
- [User-Defined Directives](#user-defined-directives-7)
- [Project Lifecycle](#project-lifecycle)
- [Example Workflow](#example-workflow)
- [Documentation](#documentation)
- [Design Philosophy](#design-philosophy)
- [License](#license)

---

## What is AIFP?

**AIFP (AI Functional Procedural)** is a programming paradigm that combines:

- **Pure functional programming** principles (referential transparency, immutability, composability)
- **Procedural execution** patterns (explicit sequencing, no hidden state)
- **Database-driven project management** (persistent state, instant context retrieval)
- **Directive-based AI guidance** (deterministic workflows, automated compliance)

### Two Ways to Use AIFP

**Use Case 1: Regular Software Development**
- Build applications (web apps, libraries, CLI tools, etc.)
- AIFP enforces FP compliance and manages your project
- You write code, AI assists with FP standards and project tracking
- Example: Building a web server, calculator library, data processor

**Use Case 2: Custom Directive Automation**
- Define automation rules (home automation, cloud management, workflows)
- **AIFP generates and manages the automation codebase for you**
- You write directive definitions (YAML/JSON/TXT), AI generates the implementation
- The project's code IS the automation code generated from your directives
- Example: Smart home control system, AWS infrastructure manager, workflow automator

**Key Principle**: One AIFP instance per project directory. You would NOT mix a web app with home automation directives. Run separate instances for separate purposes.

### Why AIFP?

Traditional programming paradigms were designed for humans. AIFP is optimized for **AI-human collaboration**:

| Challenge | Traditional Approach | AIFP Solution |
|-----------|---------------------|---------------|
| **Context Loss** | AI forgets between sessions | Database-driven persistent state |
| **OOP Complexity** | Classes, inheritance, polymorphism | Pure functions, explicit data structures |
| **Infinite Development** | Projects never "complete" | Finite completion paths with milestones |
| **Code Reasoning** | Parse source code repeatedly | Pre-indexed functions, dependencies, interactions |
| **Inconsistent Standards** | Style guides, linters, reviews | Immutable directives enforcing compliance |

---

## Core Principles

### 1. Functional-Procedural Hybrid

```python
# ✅ AIFP-Compliant
def calculate_total(items: List[Item]) -> float:
    """Pure function: deterministic, no side effects"""
    return reduce(lambda acc, item: acc + item.price, items, 0.0)

# ❌ Not AIFP-Compliant
class Calculator:
    def __init__(self):
        self.total = 0  # Hidden state

    def add_item(self, item):
        self.total += item.price  # Mutation
```

### 2. Database-Indexed Logic

Every function, file, and dependency is tracked in SQLite:

```sql
-- Instant access to project structure
SELECT f.name, f.purpose, f.purity_level
FROM functions f
JOIN files fi ON f.file_id = fi.id
WHERE fi.path = 'src/calculator.py';
```

### 3. AI-Readable Code

- **Flat structure**: No deep inheritance hierarchies
- **Explicit dependencies**: All parameters passed explicitly
- **Pure functions**: Same inputs → same outputs
- **Metadata annotations**: Machine-readable function headers

### 4. Finite Completion Paths

```
Project: MatrixCalculator
├── Completion Path (3 stages)
│   ├── 1. Setup (completed)
│   ├── 2. Core Development (in progress)
│   │   ├── Milestone: Matrix Operations
│   │   │   ├── Task: Implement multiply
│   │   │   ├── Task: Implement transpose
│   │   │   └── Task: Add validation
│   │   └── Milestone: Vector Operations
│   └── 3. Finalization (pending)
```

### 5. Language-Agnostic

AIFP works with Python, JavaScript, TypeScript, Rust, Go, and more. FP directives adapt to language-specific syntax while maintaining universal standards.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│            AI Assistant (Claude, GPT-4, etc.)        │
│  - Receives natural language commands                │
│  - Calls MCP tools                                   │
│  - Generates FP-compliant code                       │
└────────────────────┬────────────────────────────────┘
                     │ MCP Protocol
┌────────────────────▼────────────────────────────────┐
│                 MCP Server                           │
│  - Routes commands via aifp_run                      │
│  - Executes directives (FP + Project + User Pref)    │
│  - Manages four-database connections                 │
│  - Provides helper functions                         │
└───┬────────────────────┬─────────────────────────┬──┘
    │                    │                         │
┌───▼──────────────┐ ┌───▼────────────────┐ ┌─────▼─────────────────┐ ┌──────▼────────────────┐
│  aifp_core.db    │ │  project.db        │ │  user_preferences.db  │ │  user_directives.db   │
│  (Global,        │ │  (Per-Project,     │ │  (Per-Project,        │ │  (Per-Project,        │
│   Read-Only)     │ │   Mutable)         │ │   Mutable)            │ │   Optional)           │
│                  │ │                    │ │                       │ │                       │
│ - FP directives  │ │ - Project metadata │ │ - Directive prefs     │ │ - User directives     │
│ - Project mgmt   │ │ - Files & funcs    │ │ - User settings       │ │ - Execution stats     │
│ - User prefs     │ │ - Task hierarchy   │ │ - AI learning log     │ │ - Dependencies        │
│ - User systems   │ │ - Themes & flows   │ │ - Tracking features   │ │ - Generated code refs │
│ - Helper defs    │ │ - Completion path  │ │ (All opt-in)          │ │ - Source file tracking│
│ - Directive flow │ │ - Runtime notes    │ │                       │ │ (Logs in files)       │
└──────────────────┘ └────────────────────┘ └───────────────────────┘ └───────────────────────┘
```

---

## Database Architecture

### aifp_core.db (Global, Read-Only)

**Location**: Within MCP server installation directory (user-defined location, configured in AI client)

**Purpose**: Immutable knowledge base containing all AIFP standards, directives, and helper definitions.

**Key Tables**:
- `directives`: All FP, project, and user preference directives (workflows, keywords, thresholds)
- `helper_functions`: Database, file, Git, and FP utilities organized across multiple registry files
- `directive_helpers`: **Many-to-many junction table** mapping directives to their helper functions with execution metadata
- `directives_interactions`: Cross-directive relationships and dependencies
- `categories`: Directive groupings (purity, immutability, task management, etc.)
- `tools`: MCP tool definitions

**Helper-Directive Relationship** (New in v1.4):
- One directive can use many helpers, one helper can serve many directives
- Junction table stores: execution context, sequence order, parameter mappings
- Enables flexible helper reuse and clear execution flow
- See `docs/HELPER_DIRECTIVE_SCHEMA_DESIGN.md` for complete design

**Helper Classification** (New in v1.4):
- `is_tool = TRUE`: Exposed as MCP tool (AI can call directly via MCP)
- `is_sub_helper = TRUE`: Sub-helper (only called by other helpers, no directive mapping)
- Both FALSE: Helper used by directives (AI calls via directive workflows)

**Helper Registry** (Development Staging):
- Helper definitions maintained in `docs/helpers/json/*.json` during development
- Developers modify JSON files, then import to database when complete
- Each helper includes `used_by_directives` field for relationship mapping
- Database import script populates `aifp_core.db` from JSON files before release
- Production: Users query `aifp_core.db` (pre-populated), NOT JSON files
- JSON files are dev-only staging area, never shipped with package

**Read-Only Philosophy**: This database is version-controlled and immutable once deployed. AI reads from it but never modifies it.

### project.db (Per-Project, Mutable)

**Location**: `<project-root>/.aifp-project/project.db`

**Purpose**: Persistent state for a single AIFP project. Tracks code structure, tasks, and runtime notes.

**Key Tables**:
- `project`: High-level metadata (name, purpose, goals, status, user_directives_status, last_known_git_hash)
- `files`, `functions`, `interactions`: Code structure tracking
- `themes`, `flows`: Organizational groupings
- `completion_path`, `milestones`, `tasks`, `subtasks`, `sidequests`: Hierarchical roadmap
- `notes`: Runtime logging with optional directive context (source, severity, directive_name)
- `types`: Algebraic data types (ADTs)
- `infrastructure`: Project setup (language, packages, testing)
- `work_branches`: Git collaboration metadata (user, purpose, merge strategy)
- `merge_history`: FP-powered merge conflict resolution audit trail

**User Directives Integration**: The `project.user_directives_status` field tracks whether user directives are initialized (NULL/in_progress/active/disabled), allowing `aifp_run` and `aifp_status` directives to include user directive context when active.

**Enhanced Notes**: The `notes` table now includes `source` (user/ai/directive), `directive_name` (optional context), and `severity` (info/warning/error) for better traceability.

### user_preferences.db (Per-Project, Mutable)

**Location**: `<project-root>/.aifp-project/user_preferences.db`

**Purpose**: User-specific AI behavior customizations and opt-in tracking features.

**Key Tables**:
- `directive_preferences`: Per-directive behavior overrides (atomic key-value structure)
- `user_settings`: Project-wide AI behavior settings
- `tracking_settings`: Feature flags for opt-in tracking (all disabled by default)
- `ai_interaction_log`: User corrections and learning data (opt-in)
- `fp_flow_tracking`: FP compliance history (opt-in)
- `issue_reports`: Contextual bug reports (opt-in)

**Cost Management Philosophy**: All tracking features disabled by default to minimize API token usage. Project work should be cost-efficient; debugging and analytics are opt-in.

**User Customization Example**:
```sql
-- User says: "Always add docstrings"
INSERT INTO directive_preferences (directive_name, preference_key, preference_value)
VALUES ('project_file_write', 'always_add_docstrings', 'true');

-- Next file write automatically includes docstrings
```

### user_directives.db (Per-Project, Optional)

**Location**: `<project-root>/.aifp-project/user_directives.db`

**Purpose**: Store user-defined domain-specific directives for automation (home automation, cloud infrastructure, etc.). **When this database exists, the AIFP project IS dedicated to building and managing the automation code generated from these directives.**

This database only exists in **Use Case 2: Custom Directive Automation** projects. In regular software development projects, this database is not created.

**Key Tables**:
- `user_directives`: Directive definitions (triggers, actions, status, validated configuration)
- `directive_executions`: Execution statistics (summary only, detailed logs in files)
- `directive_dependencies`: Required packages, APIs, environment variables
- `directive_implementations`: Links directives to generated code files
- `helper_functions`: **AI-generated helper functions** (project-specific implementation utilities)
- `directive_helpers`: **Many-to-many junction table** mapping user directives to their helpers
- `source_files`: Tracks user directive source files (YAML/JSON/TXT)
- `logging_config`: File-based logging configuration

**Helper Functions (New in v1.0)**:
- AI generates project-specific helper functions for user directives
- Tracked with implementation status: not_implemented → generated → tested → approved
- Enforces FP compliance (pure functions) for all generated code
- Same many-to-many relationship pattern as aifp_core.db

**File-Based Logging Philosophy**: Database stores state and statistics only. Detailed execution logs (30-day retention) and error logs (90-day retention) are stored in rotating files at `.aifp-project/logs/`.

**Directory Structure Comparison**:

```
# Use Case 1: Regular Software Development
my-web-app/
├── src/                    # Your application code
├── tests/                  # Your tests
└── .aifp-project/          # AIFP tracks your application
    ├── project.db
    └── user_preferences.db

# Use Case 2: Custom Directive Automation
home-automation/
├── directives/             # ← User writes directive files here
│   ├── lights.yaml
│   └── security.yaml
├── src/                    # ← AIFP GENERATES this code
│   ├── lights_controller.py
│   └── security_monitor.py
├── tests/                  # ← AIFP GENERATES tests
└── .aifp-project/          # ← AI-managed only, user never touches
    ├── project.db          # Tracks generated src/ code
    ├── user_preferences.db
    ├── user_directives.db  # References ../directives/ files
    └── logs/               # 30/90-day execution logs
```

**Example Workflow (Automation Project)**:
1. User creates `directives/lights.yaml` in their project
2. User tells AI: "Parse my directive file at directives/lights.yaml"
3. AI parses and validates through interactive Q&A
4. AI generates FP-compliant implementation code in `src/`
5. AI tracks generated code in `project.db` (files, functions, tasks)
6. Directives execute in real-time via background services
7. Execution logs to `.aifp-project/logs/`, statistics to database

**Note**: User directive files stay in the user's project. `.aifp-project/` is AI-managed metadata.

---

## How It Works

### 1. AIFP MCP Gateway Pattern

The `aifp_run` command serves as a **gateway and reminder**, not an executor. It tells the AI that AIFP directives should be applied.

**Every `aifp_run` call returns**:
```json
{
  "success": true,
  "message": "AIFP MCP available",
  "guidance": {
    "directive_access": "Directive names cached from session bundle. Query specific directives by name when needed.",
    "when_to_use": "Use AIFP directives when coding or when project management action/reaction is needed.",
    "assumption": "Always assume AIFP applies unless user explicitly rejects it."
  }
}
```

The MCP server exposes CRUD helper functions for all database operations — tracking files, functions, tasks, project state, user preferences, and (for Use Case 2) automation directives. AI discovers available helpers from the database at runtime.

**AI Decision Flow**:
1. User prefixes request with `aifp run` (or AI assumes it)
2. AI calls `aifp_run` tool → receives guidance
3. AI evaluates: Is this coding or project management?
4. If yes: Check if directives are in memory
   - No directives? → Call `get_all_directives()`
   - Has directives? → Apply appropriate ones
5. If no: Respond without directives

### 2. Command Flow Example

```bash
aifp run "Initialize project for calculator"
```

**AI Processing**:
1. Calls `aifp_run` → receives guidance
2. Evaluates: "Project initialization = project management action"
3. Checks memory: "Do I have directives? No."
4. Calls directive loading → receives comprehensive directive library
5. Reviews directives: "This matches `aifp_init`"
6. Checks prerequisites: "Should run `project_status` first?"
7. Executes `aifp_init` directive workflow:
   - Creates `.aifp-project/` directory
   - Initializes `project.db` with schema
   - Inserts project metadata
   - Sets up completion path
8. Returns result to user

### 3. Self-Assessment Framework

Before acting, AI performs self-assessment using questions provided with directives:

**Core Questions**:
1. **Is this coding or project management?**
   - If coding: Apply FP directives for how to write code
   - If project management: Apply project directives for actions/reactions

2. **Do I have directives in memory?**
   - No: Call `get_all_directives()`
   - Yes: Proceed with cached directives

3. **Which directives apply?**
   - FP baseline: Code structure, purity, immutability, composition (always active)
   - Project directives: File writes, DB updates, task management

4. **Action-reaction needed?**
   - Code write → FP compliance → DB update
   - File edit → FP validation → DB sync
   - Discussion with decision → DB update

**Example Flow (Coding Task)**:
```
User: "Write multiply_matrices function"
AI thinks:
  ✓ This is coding (FP baseline applies)
  ✓ This is project management (project_file_write applies)
  ✓ I have directives in memory
  ✓ Matches: project_file_write directive
  ✓ Action-reaction: code → FP check → DB update

AI executes:
  1. Write function following FP baseline
  2. Verify FP compliance (purity, immutability)
  3. Apply project_file_write directive
  4. Update project.db (files, functions, interactions)
```

### 4. Directive Execution

Directives follow a **trunk → branches → fallback** pattern:

```json
{
  "trunk": "analyze_function",
  "branches": [
    {"if": "pure_function", "then": "mark_compliant"},
    {"if": "mutation_detected", "then": "refactor_to_pure"},
    {"if": "low_confidence", "then": "prompt_user"},
    {"fallback": "prompt_user"}
  ]
}
```

### 5. Cross-Directive Calls

Project directives call FP directives for compliance:

```
project_file_write
  ├─ Calls fp_purity (validates function purity)
  ├─ Calls fp_immutability (checks for mutations)
  ├─ Calls fp_side_effect_detection (isolates I/O)
  └─ If all pass: writes file + updates database
```

---

## Getting Started

### Prerequisites

- **Python 3.11+** (required for type hint syntax used throughout)
- **MCP Python SDK**: `pip install mcp` (v1.26.0+) — required runtime dependency for the MCP server

### Installation

```bash
# Download/clone AIFP MCP server to your preferred location
# Example: ~/mcp-servers/aifp/ or /path/to/your/mcp-servers/aifp/

# Install the MCP Python SDK dependency
pip install mcp

# The MCP server installation contains:
# aifp_core.db (directive definitions)
# Server code (Python)
# Helper function implementations
# Database schemas
```

### Project Initialization

```bash
cd /path/to/your/project
aifp init
```

This creates an `.aifp-project/` folder in your project root containing databases for project state tracking, user preferences, and a ProjectBlueprint document. You don't need to interact with these files — the MCP server manages them automatically.

### Configure AI Assistant

Add to Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aifp": {
      "command": "python3",
      "args": ["-m", "aifp"],
      "env": {}
    }
  }
}
```

The server resolves the path to `aifp_core.db` relative to its own installation directory — no environment variables needed.

---

## Directives System

### FP Baseline vs FP Directives

**FP Baseline** (Always Active):
- Core functional programming rules AI follows naturally when writing code
- Pure functions, immutability, no OOP, explicit error handling
- Non-negotiable - all code must be FP-compliant

**FP Directives** (Reference Documentation):
- Detailed guidance for complex scenarios and edge cases
- Consulted only when AI is uncertain about implementation
- Categories: Purity, Composition, Error Handling, OOP Elimination, Optimization
- Examples: `fp_purity`, `fp_monadic_composition`, `fp_result_types`, `fp_wrapper_generation`

### Project Directives

Manage project lifecycle:

| Level | Directives | Purpose |
|-------|------------|---------|
| **Level 0** | `aifp_run` | Gateway orchestration (every interaction) |
| **Level 1** | `aifp_status`, `aifp_init`, `project_task_decomposition` | Status, initialization, high-level coordination |
| **Level 2** | `project_file_write`, `project_update_db`, `project_task_update` | Operational execution |
| **Level 3** | `project_compliance_check`, `project_evolution` | State management |
| **Level 4** | `project_completion_check`, `project_archive` | Validation & completion |

### User Preference Directives

Manage AI behavior customization and learning:

| Directive | Purpose |
|-----------|---------|
| **user_preferences_sync** | Loads preferences before directive execution |
| **user_preferences_update** | Maps user requests to directives, updates preferences |
| **user_preferences_learn** | Learns from user corrections (requires confirmation) |
| **user_preferences_export** | Exports preferences to JSON for backup/sharing |
| **user_preferences_import** | Imports preferences from JSON file |
| **project_notes_log** | Handles logging to project.db with directive context |
| **tracking_toggle** | Enables/disables tracking features with token cost warnings |

### User-Defined Directives

**FOR USE CASE 2 ONLY**: Automation projects where AIFP generates and manages the codebase:

| Directive | Purpose |
|-----------|---------|
| **user_directive_parse** | Parse YAML/JSON/TXT directive files and extract structured directives |
| **user_directive_validate** | Validate directives through interactive Q&A to resolve ambiguities |
| **user_directive_implement** | **Generate FP-compliant implementation code in `src/`** |
| **user_directive_approve** | User testing and approval workflow before activation |
| **user_directive_activate** | Deploy and activate directives for real-time execution |
| **user_directive_monitor** | Track execution statistics and handle errors |
| **user_directive_update** | Handle changes to directive source files (re-parse, re-validate) |
| **user_directive_deactivate** | Stop execution and clean up resources |
| **user_directive_status** | Comprehensive status reporting for all user directives |

**Use Cases** (Automation Projects):
- **Home Automation**: "At 5pm turn off living room lights", "If stove on > 20 min, turn off"
- **Cloud Infrastructure**: "Scale EC2 when CPU > 80%", "Backup RDS nightly at 1am"
- **Custom Workflows**: "Every Monday generate report", "Process uploaded files automatically"

**Key Architecture**:
- User writes directive definitions (YAML/JSON/TXT)
- **AIFP generates the entire automation codebase** (`src/`, `tests/`, etc.)
- AIFP manages the generated code like any software project (tasks, files, functions)
- Directives execute via background services/schedulers
- Project.db tracks the generated code; user_directives.db tracks directive state

**Key Features**:
- Write directives in YAML, JSON, or plain text
- AI validates through interactive Q&A
- AI generates complete FP-compliant Python modules in `src/`
- AI creates tests for generated code
- Real-time execution via background services
- File-based logging (30-day execution logs, 90-day error logs)
- Dependency management with user confirmation

**Example Directive Definition**:
```yaml
# directives/home_automation.yaml (user creates this in their project)
directives:
  - name: turn_off_lights_5pm
    trigger:
      type: time
      time: "17:00"
      timezone: America/New_York
    action:
      type: api_call
      api: homeassistant
      endpoint: /services/light/turn_off
      params:
        entity_id: group.living_room_lights
```

**User tells AI**: "Parse my directive file at directives/home_automation.yaml"

**AI Generates** (in `src/lights_controller.py`):
```python
# Auto-generated from home_automation.yaml
from typing import Result
from homeassistant_client import HomeAssistant

def turn_off_living_room_lights(ha_client: HomeAssistant) -> Result[None, str]:
    """Turn off all lights in living room group."""
    # FP-compliant implementation
    ...
```

See [User Directives Blueprint](docs/blueprints/blueprint_user_directives.md) and [examples](docs/examples/) for more details.

### Git Integration

FP-powered Git collaboration for multi-user and multi-AI development:

| Directive | Purpose |
|-----------|---------|
| **git_init** | Initialize or integrate with Git repository for version control |
| **git_detect_external_changes** | Detect code modifications made outside AIFP sessions |
| **git_create_branch** | Create user/AI work branches (`aifp-{user}-{number}`) |
| **git_detect_conflicts** | FP-powered conflict analysis before merging |
| **git_merge_branch** | Merge branches with AI-assisted conflict resolution |
| **git_sync_state** | Synchronize Git hash with project.db for external change detection |

**Key Features**:
- **Multi-user collaboration**: Multiple developers and AI instances work simultaneously
- **FP-powered conflict resolution**: Uses purity levels, dependencies, and test results to auto-resolve conflicts
- **Branch naming**: `aifp-alice-001`, `aifp-bob-002`, `aifp-ai-claude-001`
- **Auto-resolution**: High-confidence conflicts (>0.8) resolved automatically using FP purity rules
- **External change detection**: Compares Git HEAD with stored hash to detect changes made outside AIFP
- **Simplified schema**: No separate git_state table - Git commands are fast enough (~1ms)

**Why AIFP + Git is Superior to OOP + Git**:

| OOP Merge Problem | AIFP FP Solution |
|-------------------|------------------|
| Class hierarchies conflict | ✅ No classes → No hierarchy conflicts |
| Hidden state changes | ✅ Pure functions → Explicit inputs/outputs |
| Side effects everywhere | ✅ Side effects isolated → Easy to identify conflicts |
| Hard to test both versions | ✅ Pure functions → Easy to test and compare |

**Example Conflict Resolution**:
```
Alice and Bob both modify calculate_total():

Alice's version:
- Purity: ✅ Pure function
- Tests: 10/10 passing

Bob's version:
- Purity: ✅ Pure function
- Tests: 12/12 passing (includes edge cases)

AI Recommendation: Keep Bob's version (confidence: 85%)
Reason: More comprehensive tests, still pure
```

See [Git Integration Blueprint](docs/blueprints/blueprint_git.md) for complete multi-user collaboration workflows.

---

## Project Lifecycle

```mermaid
graph TD
    A[aifp_init] --> B[project_themes_flows_init]
    B --> C[project_task_decomposition]
    C --> D[project_file_write]
    D --> E[FP Compliance Checks]
    E --> F[project_update_db]
    F --> G[project_task_update]
    G --> H{All Tasks Done?}
    H -->|No| D
    H -->|Yes| I[project_completion_check]
    I --> J[project_archival]
```

---

## Example Workflow

### Create Project

```
User: "Initialize AIFP for my matrix calculator"

AI → aifp_run("Initialize AIFP for my matrix calculator")
    → Receives: AIFP guidance
    → Evaluates: "Project management action"
    → Checks: "No directives in memory"
    → Calls: get_all_directives()
    → Receives: Complete directive library + self-assessment questions
    → Matches: aifp_init directive
    → Checks: project_status first (no existing project)
    → Executes: aifp_init workflow
        → Creates .aifp-project/project.db
        → Inserts project metadata
        → Sets up completion path

AI: ✅ Project initialized: MatrixCalculator
    📋 AIFP directives loaded and ready
    Next: Define themes and create first task
```

### Write Function

```
User: "Write multiply_matrices function"

AI → aifp_run("Write multiply_matrices function")
    → Receives: AIFP guidance
    → Evaluates: "Coding task + project management"
    → Checks: "I have directives in memory"
    → Identifies FP directives: fp_purity, fp_immutability, fp_no_oop
    → Identifies project directive: project_file_write
    → Writes function following FP directives
    → Verifies: Pure? Yes. Immutable? Yes. No OOP? Yes.
    → Executes: project_file_write workflow
        → Writes src/matrix.py
        → Updates project.db:
           • files table (new entry)
           • functions table (multiply_matrices)
           • interactions table (dependencies)

AI: ✅ Function written: multiply_matrices
    File: src/matrix.py:15
    FP Compliance: ✓ Pure, immutable, no OOP
    DB Updated: ✓ files, functions, interactions
    Dependencies: validate_dimensions
```

### Check Compliance

```
User: "Check project compliance"

AI → aifp_run("Check project compliance")
    → project_compliance_check directive
    → Queries all functions from project.db
    → Runs FP directives on each
    → Generates report

AI: 📊 Compliance Report:
    Total functions: 12
    Compliant: 10
    Violations: 2
      - calculate_discount (uses global config)
      - process_order (hidden mutation)
```

### Customize AI Behavior

```
User: "Always add docstrings to functions"

AI → aifp_run("Always add docstrings to functions")
    → user_preferences_update directive
        → Calls find_directive_by_intent helper
        → Searches directives by name/description/keywords
        → Finds match: project_file_write
        → Confirms with user: "Apply to file writing?"
        → Updates user_preferences.db

AI: ✅ Preference saved: project_file_write
    Key: always_add_docstrings
    Value: true

    Next file write will include docstrings automatically.
```

### AI Learns from Corrections

```
User: "Actually, use guard clauses instead of nested if statements"

AI → user_preferences_learn directive (detects correction)
    → Logs interaction to ai_interaction_log
    → Infers preference: prefer_guard_clauses = true
    → Prompts user: "Should I remember this preference?"

User: "Yes"

AI: ✅ Preference learned: project_file_write
    Key: prefer_guard_clauses
    Value: true

    I'll use guard clauses in future functions.
```

---

## Documentation

### Comprehensive Blueprints

- **[Project Directives Blueprint](docs/project_directives_blueprint.md)** - Project lifecycle management
- **[FP Directives Blueprint](docs/fp_directives_blueprint.md)** - Functional programming enforcement
- **[MCP Blueprint](docs/mcp_blueprint.md)** - MCP server architecture and tools
- **[Project DB Blueprint](docs/blueprints/blueprint_project_db.md)** - project.db schema and queries
- **[MCP DB Blueprint](docs/mcp_db_blueprint.md)** - aifp_core.db schema and population
- **[User Directives Blueprint](docs/blueprints/blueprint_user_directives.md)** - User-defined automation system (home automation, cloud infrastructure, custom workflows)
- **[Interactions Blueprint](docs/blueprints/blueprint_interactions.md)** - Cross-component interactions including Git integration
- **[Git Integration Blueprint](docs/blueprints/blueprint_git.md)** - Multi-user collaboration, FP-powered conflict resolution, external change detection
- **[AIFP Project Structure Blueprint](docs/blueprints/blueprint_aifp_project_structure.md)** - Complete project directory structure and organization

### Schema Files

- **[schemaExampleMCP.sql](docs/db-schema/schemaExampleMCP.sql)** - Complete aifp_core.db schema
- **[schemaExampleProject.sql](docs/db-schema/schemaExampleProject.sql)** - Complete project.db schema
- **[schemaExampleSettings.sql](docs/db-schema/schemaExampleSettings.sql)** - Complete user_preferences.db schema
- **[schemaExampleUserDirectives.sql](docs/db-schema/schemaExampleUserDirectives.sql)** - Complete user_directives.db schema

### Reference Documents

- **[Helper Registry](docs/helpers/json/)** - **Development staging area** for helper function definitions. Developers modify JSON files here, then import to `aifp_core.db`. Each helper includes full specifications, parameters, return types, error handling, and `used_by_directives` field. These JSON files are dev-only staging and are NOT shipped with the package.
- **[Directive MD Files](src/aifp/reference/directives/)** - Complete documentation for all directives shipped with the package. Each directive MD file includes: purpose, when to apply, complete workflows (trunk → branches), compliant/non-compliant examples, edge cases, related directives, helper functions used, database operations, and testing scenarios.

### Directive Definitions (JSON + MD)

**Development Staging**: Directives defined in JSON files for easy editing:
- **[FP Core Directives](docs/directives-json/directives-fp-core.json)** - Core functional programming directives
- **[FP Aux Directives](docs/directives-json/directives-fp-aux.json)** - Auxiliary FP directives
- **[Project Directives](docs/directives-json/directives-project.json)** - Project lifecycle management
- **[User Preference Directives](docs/directives-json/directives-user-pref.json)** - User customization directives
- **[User Directive System](docs/directives-json/directives-user-system.json)** - User-defined automation directives
- **[Git Integration Directives](docs/directives-json/directives-git.json)** - Git collaboration directives

Developers modify JSON files, then import to database when complete.

**Production**: JSON files imported into `aifp_core.db` before release. Users query database, NOT JSON files. JSON files are dev-only staging area, never shipped with package.

**Documentation**: [MD Files](src/aifp/reference/directives/) - Comprehensive documentation shipped with package. Each directive includes workflows, examples, edge cases, database operations, FP compliance notes, and cross-directive relationships.

---

## Design Philosophy

### Immutable Rules, Evolving Projects

- **`aifp_core.db`** is the **rulebook** (read-only, global, version-controlled)
- **`project.db`** is the **workspace** (read-write, per-project, runtime state)
- **`user_preferences.db`** is the **customization layer** (read-write, per-project, AI behavior)
- **Directives** define the boundaries; AI operates freely within them

### Database-Driven Context

Traditional AI assistants lack persistent memory. AIFP solves this:

```sql
-- AI remembers everything across sessions
SELECT f.name, f.purpose, f.dependencies_json
FROM functions f
WHERE f.theme = 'authentication';
```

No source code reparsing required. Instant context retrieval.

### Finite by Design

Every AIFP project has a **completion path**:

```
Setup → Core Development → Testing → Documentation → Finalization
```

Once `project_completion_check` passes, the project is **done**. No endless feature creep.

---

## Roadmap

### Completed

- ✅ Comprehensive directive system designed (FP, Project, User Preference, Git, User Directives)
- ✅ Four-database architecture specified (aifp_core, project, user_preferences, user_directives)
- ✅ MCP server architecture designed with command routing
- ✅ User preference system designed with directive mapping and AI learning
- ✅ User-defined directives system designed for domain-specific automation
- ✅ Git integration designed with FP-powered multi-user collaboration
- ✅ Complete documentation and specifications
- ✅ Cost-conscious design (all tracking features disabled by default)
- ✅ Settings system finalized (12-setting baseline, v3.1)
- ✅ Helper function library implemented (all categories: core, project, git, user preferences, user directives, global, orchestrators)

### In Progress

- [ ] MCP server implementation (Python)
- [ ] MCP tool registration and request routing
- [ ] Integration testing with MCP protocol
- [ ] Directive sync script (`sync-directives.py`)
- [ ] Database migration scripts (`migrate.py`)

### Planned

- [ ] End-to-end testing with real AI interactions
- [ ] PyPI package release
- [ ] VS Code extension for task management
- [ ] Cross-language wrapper generation

---

## Contributing

AIFP is an **open standard** for AI-optimized programming. Contributions welcome:

1. **New FP directives** - Language-specific or advanced patterns
2. **Helper functions** - Database, file, Git, or FP utilities
3. **Templates** - ADT boilerplate, error handling patterns
4. **Documentation** - Examples, tutorials, case studies

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Summary

**AIFP transforms AI from a "code generator" into a structured, customizable project collaborator.**

It combines:
- **Pure functional programming** for deterministic, composable code
- **Four-database architecture** for immutable rules, runtime state, user customization, and optional automation
- **Directive-based workflows** for consistent, automated compliance
- **User preference learning** for AI that adapts to your coding style
- **Finite completion paths** for goal-oriented development
- **Cost-conscious design** with opt-in tracking features

The result: AI-maintained codebases that are **predictable, traceable, customizable, and maintainable** across sessions, teams, and even different AI assistants.

---

**Built for the age of AI-native development.**

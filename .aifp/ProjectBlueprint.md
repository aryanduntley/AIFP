# AIFP MCP Server - Project Blueprint

**Version**: 1.0
**Status**: Active (In Development)
**Last Updated**: 2025-10-26
**AIFP Compliance**: Strict

---

## 1. Project Overview

### Idea

Build a Model Context Protocol (MCP) server that provides AI assistants with database-driven directives for functional programming enforcement and project management. The server enables AI to write pure functional code, manage project lifecycles, and support user-defined automation directives.

### Goals

- Pure functional implementation (no OOP, no mutations)
- Meta-circular development (AIFP building AIFP)
- Immutable data structures throughout
- Explicit side effect isolation
- Comprehensive test coverage (>90%)
- Production-ready MCP server installable via pip

### Success Criteria

- All ~125 directives implemented and functional
- ~50 helper functions working across 4 databases
- Test coverage >90% with property-based testing
- Zero OOP violations, complete FP compliance
- Successful PyPI package release
- Documentation complete with examples

---

## 2. Technical Blueprint

### Language & Runtime

- **Primary Language**: Python 3.11+
- **Runtime/Framework**: MCP Python SDK
- **Build Tool**: pip, setuptools

### Architecture Style

- **Paradigm**: Functional Procedural (AIFP)
- **Pattern**: Pure functions with explicit data flow, effect isolation
- **State Management**: Immutable data structures with Result/Maybe types, no mutations

### Key Infrastructure

- **MCP SDK**: Protocol implementation for AI assistant communication
- **SQLite3**: Four-database architecture (core, project, preferences, user directives)
- **returns**: Result/Maybe monads for error handling
- **toolz**: Functional utilities (pipe, curry, compose)
- **dataclasses**: Immutable structures (frozen=True)
- **pytest + hypothesis**: Testing framework with property-based testing
- **mypy + ruff**: Static type checking and linting

### Package Structure

**Standalone MCP Server** (`src/aifp/` - installable via pip):
- `core/` - Immutable types and Result type definitions
- `database/` - Schemas, query builders, effect functions
- `helpers/` - ~50 helper functions organized into 5 modules
- `directives/` - ~125 directive implementations
- `mcp_server/` - MCP protocol handlers and tool registration
- `scripts/` - Standalone scripts (init_aifp_project.py)
- `templates/` - Database templates for new projects
- `reference/` - Documentation that ships with the package

**Development Files** (not in package):
- `.aifp/` - Meta-circular development tracking
- `docs/` - Blueprints, implementation plans, references
- `tests/` - Test suite

---

## 3. Project Themes & Flows

### Themes

1. **Database Operations** (includes Git integration tables)
   - Purpose: Pure query builders + isolated effects for 4 databases
   - Files: src/aifp/database/

2. **Helper Functions** (~50 functions)
   - Purpose: 7 MCP helpers, 19 Project helpers, 10 Git helpers, 4 User Prefs helpers, 10 User Directives helpers
   - Files: src/aifp/helpers/{mcp,project,git,preferences,user_directives}/

3. **Directive System** (125 directives)
   - Purpose: FP enforcement (66) + Project management (37) + User preferences (7) + User systems (9) + Git integration (6)
   - Files: src/aifp/directives/{fp,project,user_system,git}/

4. **MCP Server Framework**
   - Purpose: Protocol handlers, tool registration, request routing
   - Files: src/aifp/mcp_server/

5. **Testing Infrastructure**
   - Purpose: Unit, integration, property-based, E2E tests
   - Files: tests/{unit,integration,fixtures}/

### Flows

1. **Initialization Flow**
   - Steps: Schema creation → Database initialization → Helper functions → MCP server bootstrap
   - Related Themes: Database Operations, MCP Server Framework

2. **Directive Execution Flow**
   - Steps: AI request → aifp_run routing → Directive lookup → Helper execution → Result return
   - Related Themes: Directive System, Helper Functions

3. **Project Management Flow**
   - Steps: project_init → Task decomposition → File tracking → Completion checking
   - Related Themes: Helper Functions, Database Operations

---

## 4. Completion Path

### Stage 1: Foundation (Weeks 1-2) - IN PROGRESS

**Status**: in_progress

**Key Milestones**:
- Project initialization and structure ✅
- Database schemas and initialization ✅
- Core type definitions (immutable data structures)
- Standalone initialization script (init_aifp_project.py)
- First helper function (get_all_directives) implemented
- Testing infrastructure established

### Stage 2: Core Helpers (Weeks 3-4)

**Status**: pending

**Key Milestones**:
- MCP database helpers (11 functions)
- Project database helpers (11 functions)
- Git integration helpers (9 functions) ✅ Complete
- User preferences helpers (4 functions)
- User directives helpers (10 functions)
- Comprehensive test suites (>90% coverage)
- FP compliance verification

### Stage 3: MCP Server (Week 5)

**Status**: pending

**Key Milestones**:
- Server initialization and connection handling
- Tool registration system
- Prompt system implementation
- Request handlers with user context extraction
- Integration tests with MCP protocol

### Stage 4: Core Directives (Weeks 5-6)

**Status**: pending

**Key Milestones**:
- aifp_run orchestrator directive
- aifp_status reporter directive
- project_init bootstrap directive
- project_file_write tracking directive
- End-to-end testing with real AI interactions

### Stage 5: Directive System Expansion (Phase 2)

**Status**: pending

**Key Milestones**:
- All 66 FP directives (30 core + 36 auxiliary)
- All 36 Project directives (includes 4 completion directives: task, subtask, sidequest, milestone)
- User preference system (7 directives)
- User system directives (9 directives)
- Git integration directives (6 directives)
- Directive workflow execution engine
- Comprehensive directive tests

### Stage 6: User Directive Automation (Phase 3)

**Status**: pending

**Key Milestones**:
- User directive parsing (YAML/JSON/TXT)
- Interactive validation with Q&A
- FP-compliant code generation
- Real-time execution framework
- File-based logging system

### Stage 7: Packaging & Distribution (Phase 5)

**Status**: pending

**Key Milestones**:
- PyPI package preparation
- Template database creation
- Documentation finalization
- Installation testing (Linux, macOS, Windows)
- Example projects and tutorials
- v0.1.0 release to PyPI

---

## 5. Evolution History

### Version 1.2 - 2025-11-01

- **Change**: Added helper classification system and complete directive-helper mappings
- **Details**:
  - Added `is_sub_helper` field to aifp_core helper_functions (marks sub-helpers called only by other helpers)
  - Created `directive-helper-interactions.json` with 63 helper-directive mappings
  - Helper classification: is_tool (MCP tools), is_sub_helper (internal), or directive-callable
  - 48 of 49 helpers mapped to directives (only query_mcp_db and query_project_db unmapped - pending classification)
  - Generated from directive JSON workflows + helper-functions-reference.md "Used By" sections
- **Rationale**:
  - Clear distinction between MCP tools, sub-helpers, and directive helpers
  - Prevents confusion: is_sub_helper more descriptive than "is_internal"
  - Ensures AI knows which helpers to call via directives vs via MCP tools
  - Complete mapping enables validation and dependency tracking
- **Documentation**: `docs/directive-helper-interactions.json`, updated README.md and system prompt
- **Files**: `src/aifp/database/schemas/aifp_core.sql`, `docs/directive-helper-interactions.json`

### Version 1.1 - 2025-11-01

- **Change**: Added many-to-many helper-directive relationship schema
- **Details**:
  - Created `directive_helpers` junction table in both `aifp_core.sql` and `user_directives.sql`
  - Added execution metadata: execution_context, sequence_order, parameters_mapping
  - Added `is_tool` field to aifp_core helper_functions (marks MCP tools)
  - Added `implementation_status` field to user_directives helper_functions (tracks AI generation lifecycle)
  - Enables flexible helper reuse across multiple directives
  - Schema version updated to 1.4 (aifp_core) and 1.0 (user_directives)
- **Rationale**:
  - Single helper function can serve multiple directives (DRY principle)
  - Clear mapping of which helpers each directive uses
  - Execution metadata for sequencing and parameter passing
  - User directive helpers tracked through implementation lifecycle
- **Documentation**: `docs/HELPER_DIRECTIVE_SCHEMA_DESIGN.md`

### Version 1 - 2025-10-26

- **Change**: Initial project setup with meta-circular development tracking
- **Rationale**: Establish foundation for FP-compliant MCP server development. Use .aifp/ folder to track the MCP server's own development progress.

---

## 6. User Settings System

### Purpose

Allow users to customize AI behavior on a per-directive basis through atomic key-value preferences stored in `user_preferences.db`. The system enables users to override default directive behavior without modifying core code.

### Goals

- **Atomic Preferences**: Each preference is a single key-value pair (e.g., `always_add_docstrings = true`)
- **Directive-Specific**: Preferences target specific directives (e.g., `project_file_write.max_function_length = 50`)
- **Opt-In Tracking**: All tracking features disabled by default to minimize API costs
- **AI Learning**: Optionally learn from user corrections to infer preferences

### Database Schema (user_preferences.db)

**Tables**:
- `directive_preferences` - Per-directive behavior overrides (directive_name, preference_key, preference_value)
- `user_settings` - Project-wide AI behavior settings
- `tracking_settings` - Feature flags for opt-in tracking (all disabled by default)
- `ai_interaction_log` - User corrections and learning data (opt-in only)
- `fp_flow_tracking` - FP compliance history (opt-in only)
- `issue_reports` - Contextual bug reports (opt-in only)

### Example Preferences

```
project_file_write.always_add_docstrings = true
project_file_write.max_function_length = 50
project_file_write.prefer_guard_clauses = true
project_compliance_check.auto_fix_violations = false
project_task_decomposition.task_granularity = medium
```

### User Preferences Directives (7 total)

1. `user_preferences_sync` - Load preferences before directive execution
2. `user_preferences_update` - Map user requests to directives, update preferences
3. `user_preferences_learn` - Learn from user corrections (requires confirmation)
4. `user_preferences_export` - Export preferences to JSON for backup/sharing
5. `user_preferences_import` - Import preferences from JSON file
6. `project_notes_log` - Handle logging to project.db with directive context
7. `tracking_toggle` - Enable/disable tracking features with token cost warnings

### Cost Management Philosophy

All tracking features disabled by default to minimize API token usage. Project work should be cost-efficient; debugging and analytics are opt-in.

---

## 7. User Custom Directives System

### Purpose

Enable users to define domain-specific automation directives (home automation, cloud infrastructure, custom workflows). **When custom directives are enabled, the AIFP project management system is dedicated to building, managing, and executing the automation code for those directives.**

### Two Distinct Use Cases for AIFP

**Use Case 1: Regular Software Development**
- User is building a software project (web app, library, CLI tool, etc.)
- AIFP manages the project with FP compliance, task decomposition, file tracking
- `.aifp-project/` tracks the user's application code
- No custom directives involved
- Example: `~/projects/my-web-app/.aifp-project/`

**Use Case 2: Custom Directive Automation**
- User wants automation (home, cloud, workflows)
- User writes directive definitions (YAML/JSON/TXT)
- **AIFP project management builds the automation code itself**
- The project's code IS the directive implementation code
- AIFP generates, tests, and manages the automation codebase
- Example: `~/automation/home/.aifp-project/`

**Key Architectural Principle**: Users run separate AIFP instances in different project directories. You would NOT mix a web app project with home automation directives. Each project has one purpose.

### Goals

- **Simple Definition**: Users write directives in YAML/JSON/TXT format
- **Interactive Validation**: AI validates through Q&A to resolve ambiguities
- **FP Code Generation**: AI generates pure functional implementation code
- **Real-Time Execution**: Directives run in real-time via schedulers/services/event handlers
- **File-Based Logging**: Detailed logs stored in files (30-day execution, 90-day errors)
- **User Approval**: Modifications trigger re-validation and require user approval

### Directory Structure Examples

**Use Case 1: Regular Software Development**
```
my-web-app/                          # User's application project
├── src/                             # Application source code
│   ├── main.py
│   ├── routes.py
│   └── models.py
├── tests/                           # Application tests
├── README.md                        # Project documentation
└── .aifp-project/                   # ← AIFP tracks this application
    ├── project.db                   # Project state, tasks, files
    ├── user_preferences.db          # AI preferences for this project
    ├── aifp_core.db                 # AIFP directive definitions
    ├── ProjectBlueprint.md          # Application architecture
    └── backups/
```

**Use Case 2: Custom Directive Automation**
```
home-automation/                     # Automation project
├── directives/                      # ← User writes directive files here
│   ├── lights.yaml                  # User-written directive definition
│   └── security.yaml                # User-written directive definition
├── src/                             # ← AIFP generates automation code here
│   ├── lights_controller.py        # Generated from lights.yaml
│   ├── security_monitor.py         # Generated from security.yaml
│   └── scheduler.py                # Generated orchestrator
├── tests/                           # ← AIFP generates tests here
├── requirements.txt                 # Auto-detected dependencies
└── .aifp-project/                   # ← AI-managed only, user never touches
    ├── project.db                   # Tracks generated src/ code
    ├── user_preferences.db          # AI preferences
    ├── user_directives.db           # References ../directives/ files
    ├── aifp_core.db                 # AIFP directive definitions
    ├── ProjectBlueprint.md          # Automation architecture
    └── logs/                        # Execution logs (30/90-day)
        ├── executions/              # Successful runs
        └── errors/                  # Failed runs
```

**Note**: User directive files (`directives/lights.yaml`) stay in the user's project. `.aifp-project/` is AI-managed metadata only.

**Note**: `user_directives.db` only exists in Use Case 2 (automation projects). File-based logging (30/90-day retention) is also only for Use Case 2.

### Database Schema (user_directives.db)

**Only present in automation projects (Use Case 2)**

**Tables**:
- `user_directives` - Directive definitions (triggers, actions, status, validated configuration)
- `directive_executions` - Execution statistics (summary only, detailed logs in files)
- `directive_dependencies` - Required packages, APIs, environment variables
- `directive_implementations` - Links directives to generated code files in src/
- `source_files` - Tracks user directive source files (YAML/JSON/TXT)
- `logging_config` - File-based logging configuration

### Use Cases

**Home Automation**:
- "At 5pm turn off living room lights"
- "If stove on > 20 min, turn off and alert"
- "When garage door opens after 10pm, send notification"

**Cloud Infrastructure**:
- "Scale EC2 instances when CPU > 80%"
- "Backup RDS database nightly at 1am"
- "Alert when S3 bucket size exceeds 100GB"

**Custom Workflows**:
- "Every Monday at 9am, generate weekly report"
- "When new file added to /uploads, process and move to /processed"
- "Monitor API endpoint, alert if response time > 2s"

### User Directive System Directives (8 total)

1. `user_directive_parse` - Parse YAML/JSON/TXT directive files and extract structured directives
2. `user_directive_validate` - Validate directives through interactive Q&A to resolve ambiguities
3. `user_directive_implement` - Generate FP-compliant implementation code for validated directives
4. `user_directive_approve` - User testing and approval workflow before activation
5. `user_directive_activate` - Deploy and activate directives for real-time execution
6. `user_directive_monitor` - Track execution statistics and handle errors
7. `user_directive_update` - Handle changes to directive source files (re-parse, re-validate)
8. `user_directive_deactivate` - Stop execution and clean up resources

### Example Workflow (Automation Project)

**Initial Setup**:
```bash
cd ~/automation/home
# Initialize AIFP for automation project
aifp init --name "Home Automation" --purpose "Smart home control system"
```

**Workflow**:
1. User creates `directives/lights.yaml` in their project root:
   ```yaml
   trigger: "time is 5:00 PM"
   action: "turn off living room lights"
   ```

2. User tells AI: "Parse my directive file at directives/lights.yaml"

3. AI calls `user_directive_parse` → extracts directive, identifies ambiguities:
   - Which lights API? (Philips Hue, HomeKit, MQTT)
   - All lights or specific ones?

4. AI calls `user_directive_validate` → interactive Q&A with user:
   - Q: "Which smart home platform?" A: "Philips Hue"
   - Q: "Which lights?" A: "All lights in 'Living Room' group"
   - Stores metadata in `user_directives.db` with reference to `directives/lights.yaml`

5. AI calls `user_directive_implement` → **generates automation code**:
   - Creates `src/lights_controller.py` with FP-compliant code
   - Creates `tests/test_lights_controller.py`
   - Updates `requirements.txt` with `phue` dependency
   - **Tracks in project.db** (files, functions, tasks)
   - Updates `ProjectBlueprint.md` with architecture

6. User reviews generated code: `cat src/lights_controller.py`

7. User approves via `user_directive_approve` → runs tests, confirms

8. AI calls `user_directive_activate` → starts scheduler:
   - Scheduler runs at 5:00 PM daily
   - Logs to `.aifp-project/logs/executions/`

9. AI calls `user_directive_monitor` → tracks execution:
   - Success: logged with timestamp
   - Error: logged to `.aifp-project/logs/errors/`, AI notified

**Key Points**:
- User directive files stay in the user's project (e.g., `directives/`, root, wherever user wants)
- `.aifp-project/` is AI-managed metadata only - user never edits it
- The automation project IS the generated code in `src/`
- AIFP manages it like any software project (tasks, files, functions, tests)

### File-Based Logging Philosophy

Database stores state and statistics only (not detailed logs). Detailed execution logs (30-day retention) and error logs (90-day retention) are stored in rotating files at `.aifp-project/logs/`.

---

## 8. Key Decisions & Constraints

### Architectural Decisions

- **Four-Database Architecture**: Separation of concerns (core directives, project state, user prefs, user directives)
- **Effect Isolation Pattern**: Pure functions for logic, dedicated effect modules for I/O
- **Immutable Data Structures**: All dataclasses frozen, no mutations allowed
- **Result Type Monads**: Replace exceptions with Result[T, E] for explicit error handling
- **Path Separation**: Development `.aifp/` vs runtime `.aifp-project/` to prevent confusion
- **Meta-Circular Development**: AIFP tracks its own development using AIFP principles

### Constraints

- **Python 3.11+ Required**: For improved type hints and pattern matching
- **No OOP Allowed**: Zero classes except frozen dataclasses
- **FP Compliance Mandatory**: All code must pass purity, immutability, side effect checks
- **Test Coverage >90%**: Non-negotiable quality gate
- **Git Integration Complete**: Already implemented in Phase 1 ✅

---

## 9. Notes & References

### Important Context

**Meta-Circular Development**: This project uses `.aifp/` to track its own development. The `.aifp/` folder contains:
- `project.db` - Tracks files, functions, tasks, completion path
- `ProjectBlueprint.md` - This file

**CRITICAL**: The development `.aifp/` is separate from user projects' `.aifp-project/`. Runtime path resolution always uses the user's working directory from MCP context. Never hardcode paths.

**FP Compliance Checklist**: Every function must satisfy:
- No mutations (all data frozen)
- No side effects in logic (effects isolated)
- Explicit parameters (no hidden state)
- Deterministic (same inputs → same outputs)
- Type hints on all parameters and return values
- Returns Result types for fallible operations

### External References

- [README.md](../README.md) - Project overview
- [Implementation Plans](../docs/implementation-plans/) - Detailed phase plans
- [Blueprints](../docs/blueprints/) - Architecture documentation
- [Helper Functions Reference](../docs/helper-functions-reference.md) - Complete helper function catalog
- [Directives Markdown Reference](../docs/directives-markdown-reference.md) - Directive documentation status

---

*Generated for AIFP MCP Server development on 2025-10-26*

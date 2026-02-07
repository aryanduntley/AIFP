# AIFP MCP Server - Project Blueprint

**Version**: 1.4
**Status**: Helper Implementation Complete - MCP Server Implementation Phase
**Last Updated**: 2026-01-28
**AIFP Compliance**: Strict

---

## 1. Project Overview

### Idea

Build a Model Context Protocol (MCP) server that provides AI assistants with database-driven directives for functional programming enforcement and project management. The server enables AI to write pure functional code, manage project lifecycles, and support user-defined automation directives. Testing changes

### Current Phase

**Design & Helpers Complete** - All design, documentation, specifications, and helper functions implemented:
- ✅ Four-database architecture specified (schemas complete)
- ✅ Comprehensive directive system designed (directives documented in JSON + MD)
- ✅ Helper function library fully implemented in `src/aifp/helpers/`
- ✅ Settings system finalized (v3.1: 12-setting baseline)
- ✅ All directive JSON files ready in `docs/directives-json/`
- ✅ All directive MD documentation complete in `src/aifp/reference/directives/`
- ✅ Orchestrator helpers complete (entry points, status, state, query)

**Current Phase: MCP Server Implementation** - Wire helpers into production MCP server:
- All production files in `src/aifp/` (installable package)
- Use `docs/helpers/json/` and `docs/directives-json/` as staging areas for modifications
- Import JSON staging files to databases after dev modifications
- All code must be FP-compliant (pure functions, immutable data, no OOP)

### Goals

- Pure functional implementation (no OOP, no mutations)
- Meta-circular development (AIFP building AIFP)
- Immutable data structures throughout
- Explicit side effect isolation
- Comprehensive test coverage (>90%)
- Production-ready MCP server installable via pip

### Success Criteria

- Complete directive system implemented and functional
- Comprehensive helper function library working across 4 databases
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

**Production Package** (`src/aifp/` - installable via pip):
- `core/` - Immutable types and Result type definitions
- `database/` - Schemas, query builders, effect functions
- `helpers/` - Comprehensive helper function library organized by domain
- `directives/` - Complete directive implementation system
- `mcp_server/` - MCP protocol handlers and tool registration
- `scripts/` - Standalone scripts (init_aifp_project.py)
- `templates/` - Database templates for new projects
- `reference/directives/` - Directive MD documentation shipped with package

**Development Staging** (not in package - dev only):
- `docs/helpers/json/` - Helper definitions in JSON (modify here, then import to aifp_core.db)
- `docs/directives-json/` - Directive definitions in JSON (modify here, then import to aifp_core.db)
- `docs/db-schema/` - Database schemas (source of truth for structure)
- `.aifp/` - Meta-circular development tracking (AIFP tracking AIFP's development)
- `docs/` - Blueprints, implementation plans, compliance reports
- `tests/` - Test suite

**Dev Workflow**:
1. Modify helper/directive JSON files in `docs/`
2. Run import script to populate `aifp_core.db`
3. Test with updated database
4. Production users only see pre-populated `aifp_core.db` (never touch JSON files)

---

## 3. Project Themes & Flows

### Themes

1. **Database Operations**
   - Purpose: Pure query builders + isolated effects for 4-database architecture
   - Files: src/aifp/database/

2. **Helper Functions**
   - Purpose: Orchestrators, Core utilities, Project management, Git integration, User preferences, User directives, Global operations
   - Files: src/aifp/helpers/{orchestrators,core,project,git,user_preferences,user_directives,global}/

3. **Directive System**
   - Purpose: FP enforcement + Project management + User preferences + User automation + Git collaboration
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
   - Steps: aifp_init → Task decomposition → File tracking → Completion checking
   - Related Themes: Helper Functions, Database Operations

---

## 4. End Goal & Vision

### What Success Looks Like

A production-ready MCP server installable via `pip install aifp` that:

1. **Enforces FP compliance** — AI writes pure functional code by default, guided by the system prompt and FP directive reference library. No OOP, no mutations, explicit side effect isolation.

2. **Manages project lifecycle** — From initialization through completion, every file, function, task, and milestone is tracked in databases. AI has persistent memory across sessions.

3. **Supports two use cases** — Regular software development (Use Case 1) and custom directive automation (Use Case 2), never mixed in the same project.

4. **Is self-reliant** — The MCP server actively drives workflow. It doesn't wait passively for commands. On session start, it bundles comprehensive state and guides AI to the next action.

5. **Is cost-conscious** — All tracking/analytics features disabled by default. The system works efficiently without unnecessary token overhead.

6. **Is language-agnostic** — FP directives adapt to any language. Helper functions handle Python, but the paradigm applies universally.

### Delivery Milestones

- **Foundation**: Database schemas, core types, helper function library (complete)
- **MCP Server**: Protocol handlers, tool registration, request routing (in progress)
- **Integration**: Directive execution through MCP tools, end-to-end testing
- **Distribution**: PyPI package, installation testing, example projects

---

## 5. Evolution History

### Version 1.3 - 2026-01-07

- **Change**: Settings system finalized (v3.1) and all documentation cleaned
- **Details**:
  - Reduced from 18 settings to 12 settings baseline
  - Removed 6 settings: fp_strictness_level, prefer_explicit_returns, auto_fix_violations, skip_warnings, strict_mode, task_granularity
  - Added: project_continue_on_start (autostart setting), compliance_checking (5th tracking feature)
  - Architectural clarification: FP compliance is baseline behavior (mandatory), not optional
  - project_compliance_check repurposed as tracking-only analytics directive (not validation)
  - Completed comprehensive documentation cleanup (11 issues found and fixed across all directive files)
  - All user preference directives updated with correct examples and workflows
- **Rationale**:
  - FP compliance is non-negotiable baseline behavior enforced by system prompt
  - Removed settings that implied FP was optional or configurable
  - Simplified to atomic preference model: directive_name.preference_key = value
  - All tracking features disabled by default (cost-conscious design)
- **Documentation**: docs/settings-cleanup-FINAL-COMPLETE.md, docs/settings-specification.json
- **Files**: All directive JSON and MD files, system prompt, README, ProjectBlueprint

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

### Example Preferences (v3.1 Baseline)

```
project_file_write.always_add_docstrings = true
project_file_write.max_function_length = 50
project_file_write.prefer_guard_clauses = true
project_file_write.code_style = explicit
project_file_write.indent_style = spaces_2
project_task_decomposition.naming_convention = descriptive
project_task_decomposition.auto_create_items = true
project_task_decomposition.default_priority = medium
```

**Note**: FP compliance is baseline behavior (mandatory). The `project_compliance_check` directive is now tracking-only (optional analytics), not validation. Settings like `auto_fix_violations`, `skip_warnings`, and `strict_mode` were removed in v3.1.

### User Preferences Directives

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

### User Directive System Directives

1. `user_directive_parse` - Parse YAML/JSON/TXT directive files and extract structured directives
2. `user_directive_validate` - Validate directives through interactive Q&A to resolve ambiguities
3. `user_directive_implement` - Generate FP-compliant implementation code for validated directives
4. `user_directive_approve` - User testing and approval workflow before activation
5. `user_directive_activate` - Deploy and activate directives for real-time execution
6. `user_directive_monitor` - Track execution statistics and handle errors
7. `user_directive_update` - Handle changes to directive source files (re-parse, re-validate)
8. `user_directive_deactivate` - Stop execution and clean up resources
9. `user_directive_status` - Comprehensive status reporting for all user directives

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
- **Git Integration**: Helper functions implemented ✅
- **All Helper Functions**: Fully implemented across all categories ✅

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

*Last updated for AIFP MCP Server development on 2026-01-28*

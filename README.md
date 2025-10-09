AIFP MCP Server README
Introduction to AIFP
AIFP (AI Functional Procedural) is a language-agnostic programming paradigm optimized for AI-generated and AI-maintained code. It emphasizes pure functions as building blocks, procedural sequencing for flows, and strict rules to minimize complexity (e.g., no OOP, immutability by default, explicit data handling). AIFP is not a language but a standard that can be applied to any environment (e.g., Python, JavaScript), with features like dynamic library wrappers for legacy integration, a per-project database for metadata tracking, and hierarchical directives for guiding AI behavior. The goal is to make code efficient for AI reasoning—flat, predictable, and queryable—while ensuring projects have a defined path from start to finish, preventing endless development cycles.
AIFP solves common issues in AI coding:

Traditional OOP is human-oriented and adds unnecessary overhead for AI.
AI needs quick metadata access without re-parsing files.
Projects need high-level overviews and roadmaps to align with evolving ideas.

MCP Server Overview
The MCP (AI Project Management) server is the backbone of AIFP, providing a database-driven system to manage projects. It operates on two sides:

MCP Side: Central, read-only database (aifp_core.db) with directives (if-then rules), helper functions (pre-defined utilities), and tools (pointers to directives). This side defines AIFP's rules and workflows.
Project Side: Per-project database (project.db) tracking files, functions, themes/flows, completion paths, and the project's high-level idea/purpose.

The MCP server uses a single user command (aifp run [task]) to process inputs. The AI parses the task, matches it to a directive in aifp_core.db, and executes steps, generating structured outputs for files and updating project.db. This ensures compliance (no OOP, pure functions) and progress tracking toward project completion.
Architecture
MCP Side (aifp_core.db)

Directives: If-then workflows in JSON format, with optional .md files for verbose context and roadblocks (e.g., "if OOP detected, then refactor"). The master aifp_run directive indexes all others, mapping user intents to specific actions.
Helper Functions: Pre-written Python utilities (e.g., track_file_creation) stored with metadata (parameters, purpose). AI executes these for DB operations, avoiding on-the-fly query generation.
Tools: Minimal Python scripts that point to directives (e.g., aifp_run_tool.py → aifp_run directive). Tools satisfy MCP's tool-based restriction but defer logic to directives.
Notes: Logs clarifications or escalations for directives/tools.

Project Side (project.db)

Project Table: High-level overview (name, purpose, goals_json, version, status). Tracks idea evolution (e.g., new version for pivots).
Files Table: Inventory of project files (path, language, checksum for change detection).
Functions Table: Details per file (name, purpose, parameters).
Themes and Flows Tables: AI-generated groupings for organization (themes: high-level, flows: sequences).
Completion Path Table: Roadmap from start to finish (name, order_index, status, description). Prevents dev drift.
Milestones, Tasks, Sidequests, Items Tables: Breakdowns under completion paths (milestones: overviews, tasks: details, sidequests: deviations, items: actions).
Notes Table: Clarifications linked to entities (e.g., "pivot note" for a task).
Other Tables: Infrastructure (e.g., packages), junctions for many-to-many relations (e.g., file_flows).

The MCP side provides the rules; the project side tracks state. AI queries aifp_core.db for guidance and updates project.db for progress.
How It Works
Workflow

User Input: aifp run [task] (e.g., aifp run Create math_utils.py). Natural language is supported (e.g., "Hey, I want to create a project...").
Intent Parsing: AI matches input to directives in aifp_core.db (e.g., "create project" → init_project).
Directive Execution: AI follows JSON workflow (e.g., prompt for missing details, generate output).
Output: For files, AI produces FILE: path CONTENT: code AIFP_WRITE_COMPLETE with # AIFP_METADATA (function_names, deps, theme, flow, task_id) and project context (# Purpose: ...).
Compliance Check: AI validates (no OOP, metadata present, DB updated) using helpers (e.g., check_oop).
DB Update: AI executes helpers (e.g., track_file_creation) to update project.db (files, functions, completion_path).
Alert and Retry: If fails (e.g., missing DB entry), AI alerts: "Compliance failed. Fix per directive [id]. Retry: aifp run [task]".
Project Alignment: AI references project table for purpose/goals and completion_path for next steps.

Commands and Tools

Single command: aifp run [task] (e.g., --task_id 1 for linking to tasks).
Tools: Pointers to directives (e.g., aifp_run_tool.py instructs AI to query aifp_run directive).
Directives: Handle logic (e.g., init_project creates project.db, scaffolds .aifp-project folder, inserts into project and completion_path).

Example Interaction
User: aifp run Hey, I want to create a project for a math library with fast computation.
AI: Matched directive: aifp_run (intent: create project)
Sub-directive: init_project
Please provide a project name (e.g., MatrixCalculator).
User: aifp run Set name to MatrixCalculator with purpose 'Pure functional matrix math library' and goals '["Fast computation", "No OOP"]'.
AI: Matched directive: init_project
Project initialized in project.db:

project: MatrixCalculator (id=1, purpose: Pure functional matrix math library, goals: ["Fast computation", "No OOP"])
completion_path: Setup (order_index=1, project_id=1)
Scaffolded: .aifp-project folder
Run next: aifp run Create math_utils.py with add function --task_id 1

User: aifp run Create math_utils.py with add function --task_id 1
AI: Matched directive: file_write
FILE: math_utils.py
CONTENT:
AIFP_METADATA: {"function_names": ["add"], "deps": [], "theme": "math_ops", "flow": "addition_flow", "version": 1, "task_id": 1}
Project Purpose: Pure functional matrix math library
def add(a: int, b: int) -> int:
"""Pure: Adds two integers."""
return a + b
AIFP_WRITE_COMPLETE
Run next: aifp run Verify compliance and update DB for math_utils.py --task_id 1
User: aifp run Verify compliance and update DB for math_utils.py --task_id 1
AI: Matched directive: compliance_check
Compliance check: Pass (no OOP, metadata present, AIFP_WRITE_COMPLETE).
Matched directive: update_db
project.db updated:

files: math_utils.py (project_id=1)
functions: add (file_id=1)
file_flows: Linked to addition_flow
tasks: task_id=1 marked done
Next task: aifp run [next from completion_path]

If Fails: Compliance failed: OOP detected. Fix per anti_oop_redirect. Retry: aifp run [task]
Future Extensions

Add more directives (e.g., multi_language for JS/Python).
Integrate tools for semantic search or image viewing if needed.
Develop a basic wrapper for VS Code terminal with mouse support.
Expand roadblocks_json for more edge cases.

This README provides a solid foundation for AIFP MCP. As we build out tools/directives, it can be expanded. For questions, refer to aifp_core.db or associated .md files.
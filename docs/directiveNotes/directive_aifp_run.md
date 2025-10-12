AIFP Directive: aifp_run
Overview
The aifp_run directive is the master entry point for all AIFP commands. It processes user inputs prefixed with aifp run [task] (e.g., aifp run Hey, I want to create a project...) by parsing the task for intent, matching it to a specific directive in aifp_core.db, and executing the associated workflow. Tools in the MCP server (e.g., aifp_run_tool.py) point to this directive, instructing the AI to query aifp_core.db for guidance. This directive ensures AIFP compliance (no OOP, pure functions, DB updates) and aligns tasks with the project’s purpose (project table) and roadmap (completion_path).
Purpose

Simplify user interaction to a single command: aifp run [task].
Map natural language inputs to specific directives (e.g., "create project" → init_project).
Provide a fallback for ambiguous inputs by prompting the user or logging to notes table.
Ensure thorough error handling via roadblocks_json and this .md for edge cases.

Directive Index
The following directives are available in aifp_core.db:

init_project: Initializes a project, creates project.db, scaffolds .aifp-project folder.
Intent: "create project", "initialize", "start project".
Helper: init_project_db.


file_write: Generates file output in FILE: ... CONTENT: ... AIFP_WRITE_COMPLETE format.
Intent: "create file", "write file", "generate code".
Helper: track_file_creation.


update_db: Updates project.db with file/function metadata.
Intent: "update db", "database", "track file".
Helper: track_file_creation.


compliance_check: Validates code for AIFP compliance (no OOP, metadata present).
Intent: "verify", "check compliance".
Helper: check_oop.



Workflow

Parse Intent: Extract keywords from user input (e.g., "create project" → init_project).
Query Directive: SELECT * FROM directives WHERE name = ? OR condition LIKE ?.
Execute Steps: Follow JSON workflow branches (e.g., create DB, scaffold folder).
Handle Errors:
Check roadblocks_json for known issues (e.g., "missing project name").
Load md_file_path for guidance if confidence low.
Prompt user if unresolved: Clarify: Please provide project name.


Update DB: Use helper functions to update project.db.

Roadblocks and Guidance

Ambiguous Input: Prompt user: Please clarify task (e.g., create file, update DB).
Missing Details: Request specific fields (e.g., project name, purpose).
DB Failure: Log to notes table, retry once, then escalate to user.
AI Thinking: Step-by-step:
Match intent to directive.
Check project table for context.
Validate against completion_path for roadmap alignment.
If stuck, refer to .md or user.



Example
User Input: aifp run Hey, I want to create a project which will be a math library. I want it to have fast computation. Can you help with that?
AI Action:

Matches "create project" to init_project directive.
Prompts: Please provide a project name (e.g., MatrixCalculator).
After user provides name, executes init_project workflow:
Creates project.db with schema.
Scaffolds .aifp-project folder.
Inserts into project and completion_path tables.



References

DBs: aifp_core.db (directives, tools), project.db (tracking).
Files: directives/init_project.md, helpers/init_project_db.py.


{
    "trunk": "parse_intent",
    "branches": [
        {"if": "code_related", "then": "fp_code_gen", "details": {"check_library_wrapper": true, "enforce_fp_rules": true}},
        {"if": "db_tracking_update", "then": "update_db", "details": {"parse_files": true, "associate_flows": true}},
        {"if": "not_aifp", "then": "respond_normal", "details": {"log_note_optional": true}},
        {"fallback": "prompt_user", "details": {"clarify": "Is this code-related, DB update, or other?"}}
    ],
    "error_handling": {"on_failure": "prompt user for clarification", "retry": "max 2 attempts"}
}
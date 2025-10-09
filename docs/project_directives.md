AIFP Project Directives

These directives manage project tracking, task decomposition, and user interactions, ensuring alignment with the project roadmap and updating relevant project.db tables.





directive_project_init
Description: Initializes new project scaffolding.
Flow: Create project.db with schema. Insert into project, completion_path, milestones, tasks. Scaffold .aifp-project folder.
Workflow: {"trunk": "setup_project", "branches": [{"if": "missing_details", "then": "prompt_user", "details": {"fields": ["name", "purpose", "goals"]}}, {"if": "setup_complete", "then": "create_db_and_folder", "details": {"schema": "project_db_schema.sql"}}, {"fallback": "prompt_user", "details": {"clarify": "Provide project details"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_init.md
roadblocks_json: [{"issue": "db_creation_failed", "resolution": "Check permissions, prompt user"}]intent_keywords_json: ["create project", "initialize", "start project"]
confidence_threshold: 0.8



directive_project_task_decomposition
Description: Breaks user tasks into AIFP-compliant paths, handling tasks, subtasks, and sidequests.
Flow: Query tasks and subtasks for open entries. Update task or create subtask (subtasks, priority=high). Create new task for pivots or sidequest for explorations. Handle interruptions.
Workflow: {"trunk": "review_open_tasks", "branches": [{"if": "related_to_open_task", "then": "update_if_needed", "details": {"check_alignment": true}}, {"if": "new_task_needed", "then": "create_new_task", "details": {"link_to_completion_path": true, "update_project_version": true}}, {"if": "subtask_needed", "then": "create_subtask", "details": {"table": "subtasks", "priority": "high", "pause_parent_task": true}}, {"if": "sidequest_needed", "then": "create_sidequest", "details": {"table": "sidequests", "priority": "low", "link_to_project": true}}, {"if": "interruption_detected", "then": "handle_subtask_priority", "details": {"notify_user": true, "options": "complete/discard/resume", "check_table": "subtasks"}}, {"fallback": "prompt_user", "details": {"clarify": "Is this a new task, subtask, or sidequest?"}}, {"parallel": ["execute_code_gen", "update_db"], "details": {"if_code_and_db": true}}], "error_handling": {"on_failure": "prompt_user", "retry": "max 2 attempts"}}
md_file_path: directives/project_task_decomposition.md
roadblocks_json: [{"issue": "task vs subtask vs sidequest ambiguity", "resolution": "Prompt user for clarification, log in notes"}, {"issue": "no matching open task", "resolution": "Create new task or sidequest, align to completion_path"}]
intent_keywords_json: ["decompose task", "break down", "plan steps", "explore"]
confidence_threshold: 0.5



directive_project_file_write
Description: Handles file creation/modification with structured output.
Flow: Generate FILE: CONTENT: AIFP_WRITE_COMPLETE with # AIFP_METADATA. Validate via FP directives. Update files, functions, items, subtasks.
Workflow: {"trunk": "generate_file", "branches": [{"if": "code_compliant", "then": "write_file", "details": {"metadata": true, "update_db": true}}, {"if": "non_compliant", "then": "fp_compliance_check", "details": {"escalate_to_fp_directives": true}}, {"fallback": "prompt_user", "details": {"clarify": "Fix compliance?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_file_write.md
roadblocks_json: [{"issue": "missing_metadata", "resolution": "Add AIFP_METADATA, prompt user"}]intent_keywords_json: ["create file", "write code", "generate file"]
confidence_threshold: 0.7



directive_project_update_db
Description: Updates project.db with project metadata.
Flow: Parse content for functions/deps. Insert into files, functions, themes, flows, items, subtasks. Align with completion_path.
Workflow: {"trunk": "parse_content", "branches": [{"if": "new_file", "then": "update_files_table", "details": {"checksum": true}}, {"if": "new_function", "then": "update_functions_table", "details": {"deps_json": true}}, {"if": "task_related", "then": "update_items_subtasks", "details": {"link_to_completion_path": true}}, {"fallback": "prompt_user", "details": {"clarify": "Update DB for what?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_update_db.md
roadblocks_json: [{"issue": "missing_metadata", "resolution": "Parse again, prompt user"}]intent_keywords_json: ["update db", "track file", "metadata"]
confidence_threshold: 0.6



directive_project_compliance_check
Description: Verifies project progress and code compliance.
Flow: Run FP checks (purity, no OOP). Query completion_path, tasks, subtasks for status. Pause and alert if failed.
Workflow: {"trunk": "run_checks", "branches": [{"if": "compliance_passed", "then": "proceed", "details": {"update_db": true}}, {"if": "compliance_failed", "then": "alert_user", "details": {"escalate_to_fp_directives": ["fp_purity", "fp_no_oop"]}}, {"fallback": "prompt_user", "details": {"clarify": "Fix compliance issue?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_compliance_check.md
roadblocks_json: [{"issue": "compliance_failure", "resolution": "Refer to FP directives, prompt user"}]intent_keywords_json: ["verify", "check compliance", "validate"]
confidence_threshold: 0.7



directive_project_add_path
Description: Adds or modifies completion_path entries.
Flow: Insert new path/milestone/task/subtask. Update status. Link to project_id. Log in notes.
Workflow: {"trunk": "modify_path", "branches": [{"if": "new_path", "then": "insert_completion_path", "details": {"order_index": true}}, {"if": "new_task", "then": "insert_task", "details": {"link_to_milestone": true}}, {"if": "new_subtask", "then": "insert_subtask", "details": {"table": "subtasks", "priority": "high"}}, {"fallback": "prompt_user", "details": {"clarify": "Add to roadmap?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_add_path.md
roadblocks_json: [{"issue": "path_misaligned", "resolution": "Prompt user for roadmap alignment"}]intent_keywords_json: ["add path", "update roadmap", "milestone"]
confidence_threshold: 0.6



directive_project_error_handling
Description: Manages failures and roadblocks.
Flow: Check roadblocks_json. Log to notes. Prompt user for guidance. Retry or escalate to md_file_path.
Workflow: {"trunk": "check_roadblocks", "branches": [{"if": "known_issue", "then": "apply_resolution", "details": {"log_note": true}}, {"if": "unknown_issue", "then": "prompt_user", "details": {"escalate_to_md": true}}, {"fallback": "prompt_user", "details": {"clarify": "Resolve issue?"}}], "error_handling": {"on_failure": "log_and_halt"}}
md_file_path: directives/project_error_handling.md
roadblocks_json: [{"issue": "generic_error", "resolution": "Prompt user, log in notes"}]intent_keywords_json: ["error", "failure", "roadblock"]
confidence_threshold: 0.5



directive_project_evolution
Description: Tracks changes to project idea.
Flow: Increment project.version. Update purpose, goals_json. Adjust completion_path. Log in notes.
Workflow: {"trunk": "update_project", "branches": [{"if": "pivot_detected", "then": "increment_version", "details": {"update_goals": true}}, {"if": "path_affected", "then": "update_completion_path", "details": {"log_note": true}}, {"fallback": "prompt_user", "details": {"clarify": "Confirm pivot?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_evolution.md
roadblocks_json: [{"issue": "pivot_ambiguity", "resolution": "Prompt user for new goals"}]intent_keywords_json: ["pivot", "change goals", "evolve project"]
confidence_threshold: 0.6



directive_project_user_referral
Description: Refers unresolved issues to user.
Flow: If workflow fails or confidence low, prompt user (e.g., "Clarify: Handle mutable state?"). Log in notes.
Workflow: {"trunk": "check_confidence", "branches": [{"if": "low_confidence", "then": "prompt_user", "details": {"log_note": true}}, {"if": "workflow_failure", "then": "escalate_to_md", "details": {"prompt_user": true}}, {"fallback": "prompt_user", "details": {"clarify": "Resolve issue?"}}], "error_handling": {"on_failure": "log_and_halt"}}
md_file_path: directives/project_user_referral.md
roadblocks_json: [{"issue": "unresolved_issue", "resolution": "Prompt user, log in notes"}]intent_keywords_json: ["clarify", "user input", "resolve"]
confidence_threshold: 0.5



directive_project_theme_flow_mapping
Description: Associates files/functions with themes/flows.
Flow: Infer or assign based on metadata. Insert into file_flows, flow_themes. Update confidence_score.
Workflow: {"trunk": "infer_metadata", "branches": [{"if": "metadata_present", "then": "update_flow_themes", "details": {"confidence_score": true}}, {"if": "no_metadata", "then": "prompt_user", "details": {"assign_default": true}}, {"fallback": "prompt_user", "details": {"clarify": "Assign theme/flow?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_theme_flow_mapping.md
roadblocks_json: [{"issue": "ambiguous_mapping", "resolution": "Prompt user for theme/flow"}]intent_keywords_json: ["theme", "flow", "grouping"]
confidence_threshold: 0.5



directive_project_completion_check
Description: Verifies project progress toward completion.
Flow: Query completion_path, tasks, subtasks for status. Mark done if criteria met. Alert if drift detected.
Workflow: {"trunk": "check_progress", "branches": [{"if": "criteria_met", "then": "mark_done", "details": {"update_status": true}}, {"if": "drift_detected", "then": "alert_user", "details": {"log_note": true}}, {"fallback": "prompt_user", "details": {"clarify": "Adjust roadmap?"}}], "error_handling": {"on_failure": "prompt_user"}}
md_file_path: directives/project_completion_check.md
roadblocks_json: [{"issue": "roadmap_drift", "resolution": "Prompt user for alignment"}]intent_keywords_json: ["progress", "check completion", "roadmap"]
confidence_threshold: 0.6
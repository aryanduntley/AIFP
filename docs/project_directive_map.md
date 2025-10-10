🧭 AIFP Project Directive Hierarchy Map

Version 1.0

🌐 Overview

The AIFP Project Directive System governs all project-side operations within the MCP server.
Each directive defines a procedural flow that manipulates or references the project.db, manages task and file lifecycles, and enforces structural alignment with AIFP’s functional–procedural rules.

Key Principles

Level defines operational hierarchy (0–4).

Category groups directives semantically (e.g., initialization, compliance).

Cross-links connect directives horizontally across shared contexts (e.g., project_compliance_check ↔ fp_purity).

🏗️ Level 0 — Root Orchestration
Directive	Category	Description
aifp_run	orchestration	Master directive for all project and FP operations. Parses user input, matches to directives by intent, and executes associated workflows.

🔁 Cross-links:

Routes all project-level actions through project_init, project_task_decomposition, or project_file_write.

🪴 Level 1 — Initialization
Directive	Category	Description
project_init	initialization	Creates new projects, scaffolds .aifp-project, generates project.db, and inserts base roadmap.

📈 Upstream: aifp_run
📉 Downstream: project_task_decomposition, project_add_path
🧩 Dependencies: schema loader (project_db_schema.sql)

🧩 Level 2 — Task & Roadmap Management
Directive	Category	Description
project_task_decomposition	task_management	Breaks down complex goals into structured tasks, subtasks, and sidequests.
project_add_path	task_management	Adds or modifies roadmap milestones and completion paths.

🔁 Cross-links:

project_task_decomposition → may trigger project_add_path for new milestones.

project_add_path → updates tables referenced by project_completion_check.

⚙️ Level 3 — Execution Layer (File, DB, Theme, Recovery)
Directive	Category	Description
project_file_write	file_operations	Handles AIFP-compliant file creation and ensures metadata is embedded.
project_update_db	file_operations	Parses metadata from files and updates database tables.
project_theme_flow_mapping	theme_mapping	Assigns files and functions to project flows and themes for visualization.
project_auto_resume	recovery_automation	Detects interrupted workflows and resumes from checkpoint.
project_refactor_path	archival_refactor	Allows roadmap restructuring without losing dependencies.
project_dependency_sync	dependency_management	Keeps project.db aligned with actual file and function dependencies.
project_dependency_map	dependency_management	Generates dependency graph for reasoning and analysis.

📈 Upstream: Task management or initialization
📉 Downstream: Compliance & metrics
🔁 Cross-links:

project_file_write ↔ fp_compliance_check (validates generated code)

project_theme_flow_mapping ↔ project_metrics (feeds theme alignment into progress data)

✅ Level 4 — Validation, Compliance, Recovery & Archival
Directive	Category	Description
project_compliance_check	compliance	Verifies FP purity, project state, and DB synchronization.
project_completion_check	compliance	Monitors progress and marks completion milestones.
project_error_handling	error_handling	Catches directive failures, applies roadblock resolutions, logs to notes.
project_user_referral	error_handling	Requests clarification from the user when ambiguity or failure occurs.
project_evolution	evolution_tracking	Tracks project pivots, updates version and goals.
project_backup_restore	recovery_automation	Manages backup and restore cycles for project data.
project_archive	archival_refactor	Final packaging of completed project into archive state.
project_integrity_check	dependency_management	Verifies project.db consistency, fixes broken links.
project_metrics	metrics	Aggregates quantitative progress and directive performance data.
project_performance_summary	metrics	Summarizes directive success/failure trends for audit logs.
project_auto_summary	metrics	Produces human-readable summaries of project health and goals.

🔁 Cross-links:

project_compliance_check → triggers FP directives like fp_purity, fp_no_oop.

project_metrics → reads completion data from project_completion_check.

project_evolution → updates roadmap entries tracked by project_add_path.

project_error_handling ↔ project_user_referral form a fail-safe pair.

📦 Final Flow (archive pipeline):
project_compliance_check → project_completion_check → project_metrics → project_archive

🧭 Full Directive Flow Summary
aifp_run (root)
 └─ project_init (L1)
     ├─ project_task_decomposition (L2)
     │   └─ project_add_path (L2)
     │       ├─ project_file_write (L3)
     │       │   ├─ project_update_db (L3)
     │       │   ├─ project_theme_flow_mapping (L3)
     │       │   └─ project_dependency_sync (L3)
     │       ├─ project_compliance_check (L4)
     │       │   ├─ project_completion_check (L4)
     │       │   ├─ project_metrics (L4)
     │       │   └─ project_auto_summary (L4)
     │       ├─ project_error_handling (L4)
     │       │   └─ project_user_referral (L4)
     │       ├─ project_evolution (L4)
     │       ├─ project_backup_restore (L4)
     │       ├─ project_integrity_check (L4)
     │       ├─ project_archive (L4)
     │       └─ project_refactor_path (L3)

🔗 Cross-System References
Project Directive	FP Directive Link	Description
project_compliance_check	fp_purity, fp_no_oop, fp_side_effect_detection	Ensures all generated files comply with FP rules.
project_update_db	fp_dependency_tracking	Inserts metadata from pure functions into DB.
project_file_write	fp_wrapper_generation	Wraps external library code during file generation.
project_theme_flow_mapping	fp_composition_chaining	Groups related function chains under common flows.
🧩 Directive Counts by Category
Category	Count	Example Directives
initialization	1	project_init
task_management	2	project_task_decomposition, project_add_path
file_operations	2	project_file_write, project_update_db
compliance	2	project_compliance_check, project_completion_check
error_handling	2	project_error_handling, project_user_referral
evolution_tracking	1	project_evolution
theme_mapping	1	project_theme_flow_mapping
dependency_management	3	project_dependency_sync, project_integrity_check, project_dependency_map
recovery_automation	2	project_auto_resume, project_backup_restore
archival_refactor	2	project_refactor_path, project_archive
metrics	3	project_metrics, project_performance_summary, project_auto_summary

Total: 21 project directives
Files:

project_core_directives.json → 11

project_aux_directives.json → 10

🧠 Summary

The project directives define how projects evolve and remain aligned.
They are the procedural backbone complementing the FP side’s how code behaves logic.

Together, both systems ensure:

Every project is self-describing and self-validating.

AI can recover from failure states deterministically.

All actions are logged, explainable, and reproducible.
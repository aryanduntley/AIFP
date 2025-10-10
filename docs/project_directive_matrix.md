🧩 AIFP Project Directive Interaction Matrix

Version 1.0

📘 Overview

This matrix defines the legal and logical relationships between AIFP project directives.
It shows which directives can call, depend on, or delegate to each other — ensuring the MCP server can reason about valid call paths, avoid recursive loops, and maintain deterministic execution order.

Levels: 0–4 (execution hierarchy)

Arrows:

➜ calls or triggers

↔ mutual data dependency

⤴ escalates to higher-level directive

⤵ delegates downward

FP Links: indicate when a project directive invokes a functional-purity rule.

🧭 High-Level Relationship Map
aifp_run
 ├── project_init
 │    ├── project_task_decomposition
 │    │    ├── project_add_path
 │    │    │    ├── project_file_write
 │    │    │    │    ├── project_update_db
 │    │    │    │    └── project_theme_flow_mapping
 │    │    │    └── project_compliance_check
 │    │    │         ├── project_completion_check
 │    │    │         ├── project_metrics
 │    │    │         └── project_auto_summary
 │    │    ├── project_error_handling
 │    │    │    └── project_user_referral
 │    │    ├── project_evolution
 │    │    ├── project_integrity_check
 │    │    ├── project_backup_restore
 │    │    ├── project_auto_resume
 │    │    └── project_archive
 │    └── project_refactor_path
 └── project_dependency_sync

🧱 1. Root & Initialization Layer
Directive	Triggers / Depends On	Receives Data From	Cross-Links
aifp_run	➜ project_init, ➜ project_task_decomposition, ➜ project_file_write	—	Universal root orchestrator.
project_init	➜ project_task_decomposition, ➜ project_add_path	← aifp_run	Initializes scaffolding.
project_task_decomposition	➜ project_add_path, ⤴ project_compliance_check	← project_init	Aligns tasks with roadmap.
project_add_path	➜ project_file_write, ⤴ project_completion_check	← project_task_decomposition	Inserts roadmap and milestones.
⚙️ 2. Execution & File Operations Layer
Directive	Triggers / Depends On	Receives Data From	Cross-Links
project_file_write	➜ project_update_db, ➜ project_theme_flow_mapping	← project_add_path	↔ FP link: fp_compliance_check, fp_purity, fp_side_effect_detection
project_update_db	➜ project_dependency_sync, ⤴ project_compliance_check	← project_file_write	↔ fp_dependency_tracking
project_theme_flow_mapping	⤴ project_metrics	← project_file_write	Groups metadata for progress reports.
project_dependency_sync	⤴ project_integrity_check, ⤴ project_metrics	← project_update_db	Ensures DB and file linkage accuracy.
🧪 3. Validation & Compliance Layer
Directive	Triggers / Depends On	Receives Data From	Cross-Links
project_compliance_check	➜ project_completion_check, ➜ project_metrics, ⤴ project_error_handling	← project_update_db, project_file_write	↔ FP links: fp_purity, fp_no_oop, fp_side_effect_detection
project_completion_check	➜ project_metrics, ➜ project_auto_summary	← project_compliance_check	Ensures milestone alignment.
project_integrity_check	➜ project_backup_restore, ⤴ project_error_handling	← project_dependency_sync	Validates DB consistency.
💾 4. Recovery, Evolution & Archival Layer
Directive	Triggers / Depends On	Receives Data From	Cross-Links
project_error_handling	➜ project_user_referral	← project_compliance_check, project_integrity_check	↔ notes table (logs all issues).
project_user_referral	—	← project_error_handling	User clarification endpoint.
project_evolution	⤴ project_add_path, ⤴ project_metrics	← project_completion_check	Logs pivots, updates roadmap.
project_metrics	➜ project_performance_summary, ➜ project_auto_summary	← project_completion_check, project_theme_flow_mapping	Collects project health data.
project_performance_summary	➜ project_auto_summary	← project_metrics	Summarizes reliability of directives.
project_auto_summary	—	← project_completion_check, project_metrics	Generates final project overview.
project_auto_resume	⤴ project_task_decomposition, project_file_write	← DB (detects paused tasks)	Restores context after interruption.
project_backup_restore	⤴ project_integrity_check	← project_error_handling	Automates recovery and backup flow.
project_archive	—	← project_completion_check, project_metrics	Final archival and export.
project_refactor_path	⤴ project_add_path	← project_evolution	Reorders milestones after pivot.
🔗 5. FP Directive Cross-Link Summary
Project Directive	Linked FP Directives	Purpose
project_compliance_check	fp_purity, fp_no_oop, fp_side_effect_detection	Ensures FP compliance in code output.
project_file_write	fp_wrapper_generation, fp_side_effect_detection	Wraps external libraries and isolates I/O.
project_update_db	fp_dependency_tracking, fp_introspection	Syncs functional dependencies from code to DB.
project_completion_check	fp_purity, fp_immutability	Confirms consistency between roadmap and outputs.
project_theme_flow_mapping	fp_composition_chaining	Groups related functional flows for clarity.
📊 6. Directive Call Table (Condensed)
From	➜ Calls	⤴ Escalates To	↔ Depends On
aifp_run	project_init, project_task_decomposition	—	—
project_init	project_task_decomposition, project_add_path	—	aifp_run
project_task_decomposition	project_add_path, project_error_handling	project_compliance_check	—
project_add_path	project_file_write, project_completion_check	—	—
project_file_write	project_update_db, project_theme_flow_mapping	—	fp_purity, fp_side_effect_detection
project_update_db	project_dependency_sync	project_compliance_check	—
project_dependency_sync	project_integrity_check	project_metrics	—
project_compliance_check	project_completion_check, project_metrics	project_error_handling	—
project_completion_check	project_metrics, project_auto_summary	—	—
project_error_handling	project_user_referral	—	notes table
project_metrics	project_performance_summary	—	project_completion_check
project_performance_summary	project_auto_summary	—	project_metrics
project_evolution	project_add_path	—	—
project_archive	—	—	project_completion_check, project_metrics
project_backup_restore	—	—	project_integrity_check
🧠 Notes for MCP Implementation

Cyclic safety: All upward (⤴) escalations must terminate at Level 4 directives or user referral points.

Logging: Every major directive logs to the notes table.

Fallback behavior: Default fallback for all project directives is project_user_referral if uncertainty persists beyond 2 retries.

Integration point: The AI never directly modifies MCP (read-only); it applies these directives to its local project environment (.aifp folder).

🧩 Summary

The Directive Interaction Matrix provides a deterministic and queryable map for:

Safe directive invocation order

Cross-hierarchy awareness

Recovery and retry control

FP–Project linkage visibility

It’s the connective tissue that enables AI autonomy within safe procedural limits.
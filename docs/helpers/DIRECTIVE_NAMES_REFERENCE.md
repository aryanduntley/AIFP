# Directive Names Reference

**Purpose**: Quick reference for directive names and descriptions.
**Use**: Search this file to determine which directives might use a helper.

---

## Fp Aux Directives (36 directives)

### fp_optionals
**Type**: fp
**Description**: Encourages use of optional return wrappers (Option, Maybe) instead of nulls or exceptions. Promotes predictable handling of missing data across all functional flows.

### fp_result_types
**Type**: fp
**Description**: Uses Result/Either patterns instead of exceptions for error propagation. Introduces predictable, composable error propagation structures.

### fp_try_monad
**Type**: fp
**Description**: Encourages safe evaluation of code that may fail, returning Try(success|failure) instead of throwing. Core functional error management; replaces exceptions with composable Try monads.

### fp_error_pipeline
**Type**: fp
**Description**: Allows chaining of function results that may fail using map/flatMap or similar monadic combinators. Streamlines multi-step error handling using FP monadic combinators.

### fp_null_elimination
**Type**: fp
**Description**: Detects and replaces null/undefined with safe functional constructs like Option or Result. Core null-safety enforcement directive; complements fp_optionals.

### fp_list_operations
**Type**: fp
**Description**: Refactors imperative loops into declarative list transformations using map/filter/reduce. Encourages functional collection processing patterns.

### fp_map_reduce
**Type**: fp
**Description**: Standardizes use of reduce for aggregations instead of mutable accumulators. Encourages pure aggregation using reducers; eliminates shared mutable accumulators.

### fp_lazy_evaluation
**Type**: fp
**Description**: Transforms eager list processing into lazy evaluated sequences where supported. Improves performance and composability via lazy evaluation semantics.

### fp_data_filtering
**Type**: fp
**Description**: Replaces imperative data filtering with declarative filter expressions using pure predicates. Ensures all filtering logic is expressed as composable pure functions.

### fp_pattern_unpacking
**Type**: fp
**Description**: Encourages declarative unpacking of tuples, lists, or objects instead of index-based access. Improves readability and reduces indexing errors in data access.

### fp_metadata_annotation
**Type**: fp
**Description**: Inserts structured metadata comments (# AIFP_METADATA) for functions, recording names, dependencies, and flow context. Guarantees traceability and alignment between code and project.db.

### fp_symbol_map_validation
**Type**: fp
**Description**: Checks that all exported names are pure and registered in the project’s symbol map. Keeps exported identifiers consistent with MCP introspection.

### fp_reflection_block
**Type**: fp
**Description**: Scans for reflection, dynamic eval, or code generation and prohibits them to preserve predictability. Prevents dynamic code execution violating AIFP determinism.

### fp_docstring_enforcement
**Type**: fp
**Description**: Requires a concise docstring describing inputs, outputs, and FP purity level. Improves AI reasoning by embedding intent and purity metadata.

### fp_function_indexing
**Type**: fp
**Description**: Assigns unique identifiers to each function for rapid query and dependency tracing. Supports MCP cross-reference queries and function lookups.

### fp_language_standardization
**Type**: fp
**Description**: Normalizes function naming and syntax differences (e.g., map vs collect) for multi-language consistency. Maintains consistent functional vocabulary across supported languages.

### fp_keyword_alignment
**Type**: fp
**Description**: Ensures reserved keywords or naming collisions are adapted safely during translation or generation. Prevents syntax conflicts during multi-language AIFP translations.

### fp_cross_language_wrappers
**Type**: fp
**Description**: Automatically generates pure wrapper functions around language-specific libraries for consistent AIFP compliance. Maintains FP compliance across mixed-language projects. See examples/wrappers/ for reference implementations.

### fp_syntax_normalization
**Type**: fp
**Description**: Abstracts language-specific syntax differences into a uniform AIFP-friendly form. Allows directives to operate uniformly across multiple languages.

### fp_encoding_consistency
**Type**: fp
**Description**: Verifies UTF-8 encoding and consistent newline and indentation styles across generated code. Guarantees all generated files share uniform encoding and style.

### fp_memoization
**Type**: fp
**Description**: Adds caching of pure function results to improve performance without altering behavior. Applies caching selectively to pure deterministic functions only.

### fp_lazy_computation
**Type**: fp
**Description**: Transforms eager calculations into lazy or deferred evaluations for efficiency. Improves performance for heavy or chained computations.

### fp_parallel_evaluation
**Type**: fp
**Description**: Automatically executes independent pure expressions in parallel to improve throughput. Speeds up pure code by evaluating independent expressions concurrently.

### fp_function_inlining
**Type**: fp
**Description**: Identifies trivial or single-call functions and inlines them into callers when beneficial. Inlines small pure functions to reduce call overhead without altering behavior.

### fp_dead_code_elimination
**Type**: fp
**Description**: Scans dependency graph and eliminates dead or unreachable code paths safely. Keeps project codebase lean and clean while maintaining referential integrity.

### fp_constant_folding
**Type**: fp
**Description**: Simplifies constant expressions and evaluates literals during generation to reduce runtime overhead. Performs safe pre-evaluation of constant expressions during code generation.

### fp_purity_caching_analysis
**Type**: fp
**Description**: Analyzes dependencies to ensure cached results don't cross purity or state boundaries. Prevents unsafe caching that could compromise purity guarantees.

### fp_cost_analysis
**Type**: fp
**Description**: Analyzes functions to estimate time and space complexity for internal optimization heuristics. Feeds function cost metadata into MCP reasoning for smarter decomposition.

### fp_evaluation_order_control
**Type**: fp
**Description**: Ensures consistent left-to-right or specified evaluation order to avoid non-determinism. Guarantees identical output given identical inputs, even in parallel contexts.

### fp_ai_reasoning_trace
**Type**: fp
**Description**: Inserts trace comments linking function behavior to directive reasoning for debugging and explainability. Enhances transparency between AIFP reasoning and generated output for debugging.

### fp_recursion_enforcement
**Type**: fp
**Description**: Detects loops or recursion and refactors them to tail-recursive form for stack safety and FP compliance. Ensures recursion efficiency and prevents stack overflows in AI-generated code. Links to project_update_db to track recursion depth in function interactions table (project.interactions).

### fp_monadic_composition
**Type**: fp
**Description**: Chains functions using monadic bind/map operations for composable error handling with Result/Option types. Improves composability and error handling clarity. Links to project_update_db to store monadic dependencies in function interactions table (project.interactions).

### fp_test_purity
**Type**: fp
**Description**: Validates test purity by ensuring test fixtures are pure functions, eliminating shared mutable state, and promoting property-based testing. Pure tests are deterministic, parallelizable, and easier to understand.

### fp_api_design
**Type**: fp
**Description**: Promotes function-based APIs over class-based, uses immutable data structures, explicit error handling with Result types, and designs for composition. Well-designed FP APIs are easier to test, reason about, and integrate.

### fp_documentation
**Type**: fp
**Description**: Ensures every pure function, data type, and module is properly documented with signatures, examples, and purity guarantees. Enables AI assistants and developers to understand code behavior without reading implementations.

### fp_naming_conventions
**Type**: fp
**Description**: Enforces naming patterns that make function purity, side effects, and data flow explicit through names. Pure functions use verb-noun patterns, impure functions have IO/Eff/Unsafe indicators. Enables quick understanding of code intent.

## Fp Core Directives (29 directives)

### fp_purity
**Type**: fp
**Description**: Enforces pure functions: deterministic output for given inputs, no external state or side effects. Central FP rule; applies to all code generation and compliance checks. Links to project_compliance_check.

### fp_state_elimination
**Type**: fp
**Description**: Detects and removes reliance on global variables or hidden mutable structures. Used during function analysis to strip implicit global state.

### fp_side_effect_detection
**Type**: fp
**Description**: Scans function bodies for I/O, print, logging, or mutation and isolates effects via wrappers. Supports isolation of side effects for safe functional behavior. Links to project_update_db and project_compliance_check.

### fp_immutability
**Type**: fp
**Description**: Ensures all variables and data structures are immutable by default and replaced, not modified. Foundational FP rule ensuring referential transparency and predictable state.

### fp_const_refactoring
**Type**: fp
**Description**: Promotes use of constants; automatically lifts repeated literals to top-level immutable declarations. Prevents accidental mutation and simplifies dependency tracking.

### fp_no_reassignment
**Type**: fp
**Description**: Disallows variable reassignment; enforces single-assignment semantics per scope. Ensures all variable bindings are immutable; core immutability enforcement.

### fp_ownership_safety
**Type**: fp
**Description**: Applies borrow or copy semantics to data passed between functions, preventing shared mutability. Prevents shared mutable data between functions; vital for concurrency safety.

### fp_borrow_check
**Type**: fp
**Description**: Implements lightweight borrow-checking; warns if references outlive their data source. Emulates borrow semantics in dynamic languages to ensure safe ownership boundaries.

### fp_no_oop
**Type**: fp
**Description**: Detects OOP usage such as class, inheritance, and stateful methods; refactors into functional equivalents. Core anti-OOP directive; ensures functional procedural compliance.

### fp_wrapper_generation
**Type**: fp
**Description**: Detects OOP library imports and generates pure functional wrappers for AI-safe usage. Maintains FP purity across legacy OOP dependencies. See examples/wrappers/ for reference implementations.

### fp_inheritance_flattening
**Type**: fp
**Description**: Converts class hierarchies into flattened procedural functions. Ensures all logic is in flat procedural form, avoiding OOP hierarchies.

### fp_chaining
**Type**: fp
**Description**: Encourages chaining of small functions using pipeline or composition syntax. Improves clarity and composability in generated functional code.

### fp_currying
**Type**: fp
**Description**: Refactors functions with multiple parameters into curried, single-argument forms for partial application. Supports partial application and higher-order reuse of generated functions.

### fp_pattern_matching
**Type**: fp
**Description**: Promotes pattern matching constructs for control flow instead of nested if/else. Encourages declarative decision logic across all supported languages.

### fp_tail_recursion
**Type**: fp
**Description**: Refactors recursive calls to use tail recursion for stack safety and performance. Ensures recursion efficiency and prevents stack overflows in AI-generated code.

### fp_type_safety
**Type**: fp
**Description**: Verifies that all function signatures include type information and that return types are deterministic. Enforces strong typing discipline within FP code.

### fp_type_inference
**Type**: fp
**Description**: Uses AI-assisted inference to identify likely input/output types when not annotated explicitly. Adds soft type inference for dynamic contexts.

### fp_side_effects_flag
**Type**: fp
**Description**: Detects side effects and ensures they are either isolated or explicitly declared. Ensures transparent handling of all side effects within FP boundaries.

### fp_concurrency_safety
**Type**: fp
**Description**: Analyzes concurrency patterns to prevent race conditions and shared mutable state. Ensures concurrent functional operations are free of shared mutable data.

### fp_dependency_tracking
**Type**: fp
**Description**: Analyzes function call graphs and stores dependency metadata for reasoning and code generation alignment. Provides dependency awareness to improve AIFP’s reasoning efficiency.

### fp_guard_clauses
**Type**: fp
**Description**: Rewrites nested conditional branches into early exit guard clauses for clarity and maintainability. Encourages concise and readable control flow without branching complexity.

### fp_conditional_elimination
**Type**: fp
**Description**: Refactors imperative conditionals into functional expressions using mapping or match constructs. Removes imperative control structures; promotes declarative, expression-based logic.

### fp_generic_constraints
**Type**: fp
**Description**: Validates that generics or templates adhere to specified type constraints where possible. Ensures correctness when using generics or polymorphic function templates.

### fp_runtime_type_check
**Type**: fp
**Description**: Injects runtime guards or assertions to ensure type correctness when static typing is unavailable. Adds defensive checks to maintain type safety at runtime.

### fp_io_isolation
**Type**: fp
**Description**: Separates all input/output operations into dedicated effect functions or external modules. Maintains strict separation between I/O and logic for deterministic behavior.

### fp_logging_safety
**Type**: fp
**Description**: Redirects logging to pure output streams or external effect handlers to avoid hidden state. Prevents stateful or side-effect-heavy logging inside functions.

### fp_parallel_purity
**Type**: fp
**Description**: Validates that functions running in parallel are independent and side-effect free. Protects functional integrity in parallel operations.

### fp_task_isolation
**Type**: fp
**Description**: Enforces isolation between parallel tasks by cloning or message-passing data. Maintains purity across concurrent functional tasks.

### fp_reflection_limitation
**Type**: fp
**Description**: Detects and disallows reflection, dynamic eval, or runtime metaprogramming constructs. Prevents runtime code generation that violates AIFP determinism.

## Git Directives (6 directives)

### git_init
**Type**: git
**Description**: Initializes Git repository if one doesn't exist, or integrates with existing repository. Creates initial .gitignore for AIFP files, stores initial Git hash in project.last_known_git_hash for external change tracking, and optionally creates initial commit. For existing repos, detects current branch and commit hash. Current Git state is always queried from Git directly (no duplication in DB).

### git_detect_external_changes
**Type**: git
**Description**: Detects external code changes by comparing current Git HEAD with project.last_known_git_hash. Identifies modified files using git diff, analyzes theme impact by querying project.db for affected themes/flows, and updates project.last_known_git_hash with new hash. Presents changes to user with recommendations for organizational state reconciliation.

### git_create_branch
**Type**: git
**Description**: Creates new work branch following naming convention aifp-{user}-{number}. Detects user from Git config, environment, or prompts if needed. Stores branch metadata in work_branches table including purpose, user, and status. Optionally links branch to specific tasks/themes. Supports both human developers and autonomous AI instances.

### git_detect_conflicts
**Type**: git
**Description**: Performs dry-run analysis of branch merge conflicts using FP intelligence. Compares source and target branches at both file and function level. Queries project.db to get function metadata (purity, dependencies, tests) from both branches. Classifies conflicts by type (file, function, database) and assigns confidence scores for auto-resolution based on FP purity. Returns detailed conflict analysis with AI recommendations.

### git_merge_branch
**Type**: git
**Description**: Merges user/AI work branch into main using FP intelligence for conflict resolution. Calls git_detect_conflicts first to analyze potential conflicts. Auto-resolves high-confidence conflicts (>0.8) using FP purity rules. Presents low-confidence conflicts to user with AI recommendations. Logs merge history to merge_history table with detailed resolution strategy. Updates work_branches status to 'merged'.

### git_sync_state
**Type**: git
**Description**: Updates project.last_known_git_hash with current Git HEAD commit hash. Called during session boot, after commits, and after branch operations. Enables external change detection by comparing stored hash with current state. Simple sync operation - just updates project table, no separate git_state table needed (Git itself tracks current branch).

## Project Directives (38 directives)

### aifp_run
**Type**: project
**Description**: Gateway entry point for AIFP system. Returns guidance to AI assistant on when and how to use AIFP directives. Does NOT execute directives itself - AI receives guidance and decides next action based on task type (coding, project management, or simple discussion). Always assume AIFP applies unless user explicitly rejects. First action should be calling aifp_status to understand current project state.

### project_init
**Type**: project
**Description**: Initializes a new AIFP project by creating .aifp-project/ folder structure, generating ProjectBlueprint.md through interactive prompts, initializing project.db and user_preferences.db, and populating with initial infrastructure, themes, flows, and completion path. Wraps the standalone initialization script (aifp.scripts.init_aifp_project) helper functions to ensure consistent setup. Checks for existing .aifp-project/ or .git/.aifp/ folders before initialization. Scans existing codebase for OOP patterns and aborts initialization if OOP detected (AIFP is FP-only). Offers restoration from .git/.aifp/ backup if found.

### project_task_decomposition
**Type**: project
**Description**: Decomposes high-level user requests into completion_path, milestones, tasks, subtasks, and items. When tasks require code generation, use project_reserve_finalize before project_file_write to reserve names and get database IDs. Respects user preferences for task granularity, naming conventions, and decomposition style. Creates roadmap structure and ensures hierarchy consistency. Central decomposition directive; translates user intent into actionable milestones.

### project_add_path
**Type**: project
**Description**: Creates or updates completion_path, milestones, and tasks in project.db to maintain project roadmap continuity. Maintains structural coherence of project paths and milestones.

### project_file_write
**Type**: project
**Description**: Writes new or modified files using the AIFP-compliant output pattern, validates via FP directives, and updates project.db accordingly. Should use project_reserve_finalize BEFORE writing to get database IDs for embedding in filenames/function names. Detects user directive generated files and marks them with appropriate metadata. Applies user preferences from directive_preferences table (e.g., always_add_docstrings, max_function_length, prefer_guard_clauses) loaded by user_preferences_sync. Core file generation directive; bridges code creation and database synchronization.

### project_reserve_finalize
**Type**: project
**Description**: Manages reservation and finalization of files, functions, and types in project database. AI reserves names BEFORE writing code to receive database IDs, embeds IDs in code for instant lookups (filename_id_42.py, function_name_id_99), and finalizes reservations after implementation. Prevents naming collisions, enables rename-proof references, and dramatically reduces API query costs by using integer lookups instead of string matching.

### project_update_db
**Type**: project
**Description**: Parses generated code for functions, dependencies, and metadata, then updates project.db tables accordingly to maintain accurate state tracking. Should finalize reservations (via project_reserve_finalize) to update names with embedded IDs and set is_reserved=FALSE after successful file writes. Handles user directive generated files by also updating user_directives.db tables (directive_implementations). Central DB synchronization directive; ensures project.db accurately reflects file and function states after each generation cycle.

### project_compliance_check
**Type**: project
**Description**: Runs FP compliance directives to ensure code purity, no OOP, and structural correctness. Also verifies project completion alignment via project.db. Respects user preferences for compliance strictness (e.g., fp_strictness_level, auto_fix_violations) and applies user-approved exceptions. Validates project state and functional integrity before database updates or completion marking.

### project_completion_check
**Type**: project
**Description**: Checks completion_path, milestones, and tasks for status updates. Marks completion milestones when conditions are met and logs alignment notes. Monitors roadmap alignment, marks progress milestones, and prevents premature completion marking.

### project_error_handling
**Type**: project
**Description**: Monitors directive execution for known or unknown failures, applies stored roadblock resolutions, and logs issues to the notes table for transparency. Provides universal error recovery handling for all project-level directives. Integrates with the notes table for traceability.

### project_evolution
**Type**: project
**Description**: Handles versioning and pivot tracking for evolving project goals. Updates ProjectBlueprint.md sections when project-wide changes occur (architecture, goals, themes, flows, infrastructure, completion path). Logs changes in notes and updates roadmap and completion paths accordingly. Captures and logs project pivots for transparency in long-running projects. Updates project.version and completion paths.

### project_user_referral
**Type**: project
**Description**: When confidence is low or a workflow fails, prompts the user for guidance and logs the clarification request to notes for review. Standard fallback directive for AI–user collaboration. Ensures ambiguous operations always route through human confirmation.

### project_theme_flow_mapping
**Type**: project
**Description**: Infers or assigns flow and theme groupings based on file metadata, updating linking tables for file_flows and flow_themes within project.db. Maintains thematic and procedural grouping across project files. Supports roadmap visualization and organization. Triggers project_evolution directive when themes or flows are added or modified to update ProjectBlueprint.md accordingly.

### project_metrics
**Type**: project
**Description**: Calculates project completion percentage, directive success rates, and task distribution to inform AI reasoning and user summaries. Provides periodic project health reports for both AI and user reference. Logged in notes for transparency.

### project_performance_summary
**Type**: project
**Description**: Summarizes recent directive outcomes, including successes, retries, and failures, and stores summaries in notes for audit. Keeps a rolling summary of directive performance for reliability tracking.

### project_dependency_sync
**Type**: project
**Description**: Compares functions and flows in files against database records, resolving missing or outdated dependencies. Maintains consistency between the physical codebase and project metadata.

### project_integrity_check
**Type**: project
**Description**: Runs validation queries to detect orphaned records, missing links, and checksum mismatches within project.db. Ensures internal DB consistency, preventing corruption during iterative project growth.

### project_auto_resume
**Type**: project
**Description**: Detects unfinished tasks or subtasks from project.db and resumes execution at the appropriate directive entry point. Restores workflow continuity between user sessions or interruptions.

### project_backup_restore
**Type**: project
**Description**: Creates periodic backups of project.db and associated files, and restores them on demand or after failure detection. Protects project state from corruption or user error. Integrates with integrity check for recovery decisions.

### project_archive
**Type**: project
**Description**: Packages the final project.db, all files, and completion reports into an archive format and marks project status as 'archived'. Preserves completed project versions and prepares exportable deliverables.

### project_refactor_path
**Type**: project
**Description**: Allows restructuring of completion_path sequences for clarity, merging or reordering tasks while maintaining linkage integrity. Provides roadmap reorganization utilities for evolving projects.

### project_dependency_map
**Type**: project
**Description**: Queries relationships between files, functions, flows, and tasks to produce a dependency graph for reasoning or visualization. Improves transparency and traceability across project elements for AIFP reasoning.

### project_auto_summary
**Type**: project
**Description**: Generates a human-readable summary of project purpose, progress, and open tasks. Stores summary in notes table with note_type='auto_summary' for future reference and outputs to terminal. Provides quick, automated overviews of project state for both AI and user consumption.

### aifp_status
**Type**: project
**Description**: Retrieves comprehensive project status with historical context for task continuation. For existing projects: reads ProjectBlueprint.md, loads infrastructure, builds priority status tree (sidequests → subtasks → tasks), provides historical context from previous tasks, checks for ambiguities, and generates status report. For new projects: checks for .aifp/ folder, checks .git/.aifp/ backup, prompts for restoration or initialization.

### project_blueprint_read
**Type**: project
**Description**: Reads and parses ProjectBlueprint.md into structured data. Returns project metadata (name, version, status, goals), technical blueprint (language, runtime, architecture), themes, flows, and completion path. Falls back to database if blueprint file missing.

### project_blueprint_update
**Type**: project
**Description**: Updates specific section of ProjectBlueprint.md with new content. Backs up current blueprint before modification, replaces section content, optionally increments version and adds evolution history entry. Used by project_evolution and other directives when project-wide changes occur.

### project_file_read
**Type**: project
**Description**: Intelligent file reader that provides file content with full database context including metadata, functions, dependencies, theme/flow associations, and checksum verification. Detects if file changed since last DB update.

### project_file_delete
**Type**: project
**Description**: Safe file remover that ensures filesystem and database consistency. Uses ERROR-first approach: delete_file() returns error if dependencies exist (functions, types, file_flows). AI must systematically delete functions (which checks types_functions), remove file_flows entries, then retry file deletion. No automatic cascading - forces intentional cleanup to prevent accidental data loss.

### project_task_create
**Type**: project
**Description**: Atomic task constructor for creating new independent tasks. Links to milestone, sets initial status, assigns priority, validates inputs, and returns task ID for immediate use.

### project_task_update
**Type**: project
**Description**: Central task state manager for updating status, priority, and metadata. Delegates completion workflows to specialized completion directives. Maintains roadmap integrity and triggers downstream actions.

### project_subtask_create
**Type**: project
**Description**: Atomic subtask constructor that creates focused, high-priority subtasks and automatically pauses parent tasks until completion. Subtasks are immediate-focus work that blocks parent task progress.

### project_item_create
**Type**: project
**Description**: Atomic item constructor for creating smallest work units within tasks. Links to parent task, supports optional file/function references, and enables fine-grained progress tracking.

### project_sidequest_create
**Type**: project
**Description**: Atomic sidequest constructor for creating exploratory interruptions. Handles fixes, pivots, or unrelated work that pauses tasks. Default low priority for exploratory work outside main roadmap.

### project_task_complete
**Type**: project
**Description**: Handles post-task completion workflow: marks task and items complete, checks milestone progress, reviews completion_path, and engages user to plan next task. Ensures continuous forward progress by automatically reviewing roadmap status after each task completion.

### project_subtask_complete
**Type**: project
**Description**: Handles post-subtask completion workflow: marks subtask complete, checks all subtasks for parent task, resumes parent task when all subtasks complete. Ensures parent task automatically resumes when blocking subtasks are finished.

### project_sidequest_complete
**Type**: project
**Description**: Handles post-sidequest completion workflow: marks sidequest complete, logs outcome and lessons learned, optionally resumes paused task. Captures exploratory work results for future reference.

### project_milestone_complete
**Type**: project
**Description**: Handles post-milestone completion workflow: marks milestone complete, updates completion_path progress, reviews overall project status, moves to next milestone, and creates first task. Ensures continuous project momentum by automatically planning next phase.

### aifp_help
**Type**: project
**Description**: Loads detailed documentation for a specific directive. Uses get_directive_content helper to retrieve full markdown documentation including purpose, workflow, examples, edge cases, and related directives. Provides comprehensive guidance beyond basic directive metadata.

## User Pref Directives (7 directives)

### user_preferences_sync
**Type**: project
**Description**: Loads and applies user preferences before executing any project directive. Checks user_preferences.db for directive-specific preferences and applies them to current context. Executed automatically before file writes and compliance checks.

### user_preferences_update
**Type**: project
**Description**: Handles explicit user requests to modify behavior preferences. Uses find_directive_by_intent helper to map user requests to specific directives by searching name, description, and intent_keywords. Creates or updates directive_preferences entries with chosen directive name. Validates preference changes and confirms with user before applying.

### user_preferences_learn
**Type**: project
**Description**: Detects when user corrects or modifies AI output and offers to learn the preference. Logs interaction to ai_interaction_log and prompts user whether to apply preference project-wide. Requires user confirmation before updating directive_preferences.

### user_preferences_export
**Type**: project
**Description**: Exports user_preferences.db settings to a portable JSON format for backup or sharing across projects. Includes directive_preferences and user_settings tables. Optionally includes tracking data if user requests it.

### user_preferences_import
**Type**: project
**Description**: Imports previously exported preferences from JSON file into user_preferences.db. Merges with existing preferences, prompting user on conflicts. Validates imported data before applying.

### project_notes_log
**Type**: project
**Description**: Logs clarifications, reasoning, and directive execution context to project.db notes table. Optionally includes directive_name when note is related to specific directive execution. Used by other directives for transparent reasoning trails.

### tracking_toggle
**Type**: project
**Description**: Toggles tracking features on or off by updating tracking_settings table. Shows user estimated token overhead before enabling. Allows granular control over fp_flow_tracking, issue_reports, ai_interaction_log, and helper_function_logging.

## User System Directives (9 directives)

### user_directive_parse
**Type**: project
**Description**: Parse user directive files (YAML/JSON/TXT) from wherever user placed them in their project. User tells AI the file path (e.g., 'directives/lights.yaml', 'automations.yaml', etc.).

### user_directive_validate
**Type**: project
**Description**: Validate parsed directives through interactive Q&A to resolve ambiguities

### user_directive_implement
**Type**: project
**Description**: Build the entire AIFP project to implement user directives. Reserve names via project_reserve_finalize before generating code to get database IDs for embedding. Generate all necessary FP-compliant code with embedded IDs, install dependencies, create helper functions, set up cron jobs, configure automations, and build supporting infrastructure. The project's purpose becomes executing these directives.

### user_directive_approve
**Type**: project
**Description**: User approves tested implementation, transitioning project from 'in_progress' to 'active' status. Called after user has tested the implementation and confirmed it meets their requirements.

### user_directive_activate
**Type**: project
**Description**: Deploy and activate approved directives for real-time execution. Only called after user approval.

### user_directive_monitor
**Type**: project
**Description**: Monitor active directive executions, track statistics, and handle errors

### user_directive_update
**Type**: project
**Description**: Handle changes to user directive source files. When modifications are detected, status returns to 'in_progress', directives are deactivated if active, re-implemented, and require user approval again before reactivation.

### user_directive_deactivate
**Type**: project
**Description**: Stop execution of active directives and clean up resources

### user_directive_status
**Type**: project
**Description**: Get comprehensive status report for all user directives

---

**Total Directives**: 125
**Last Generated**: 2026-01-01

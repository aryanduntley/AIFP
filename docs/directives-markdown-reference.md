# AIFP Directives Markdown Reference

**Date**: 2025-10-25
**Status**: Planning - Markdown files to be created
**Total Files**: 100 markdown files across 108 directives

---

## Overview

This document catalogs all markdown documentation files referenced by AIFP directives. Each directive has a corresponding `.md` file that provides:
- Detailed explanation of the directive's purpose
- When to apply the directive
- Step-by-step workflow instructions
- Examples of compliant vs non-compliant code
- Edge cases and special considerations
- Related directives and dependencies

**Note**: These markdown files are **to be created**. This document serves as a specification and checklist for Phase 2 implementation.

---

## Status Summary

| Category | Total Directives | MD Files Referenced | Files Created | Remaining |
|----------|------------------|---------------------|---------------|-----------|
| **FP Core** | 30 | 30 | 0 | 30 |
| **FP Auxiliary** | 32 | 32 | 0 | 32 |
| **Project** | 25 | 25 | 3 | 22 |
| **Git** | 6 | 6 | 0 | 6 |
| **User Preferences** | 7 | 7 | 0 | 7 |
| **User System** | 8 | 0 (blueprint only) | N/A | N/A |
| **aifp_run, aifp_status** | 2 | 2 | 1 | 1 |
| **TOTAL** | **108** | **100** | **4** | **96** |

**Note**: User System directives (8) are documented as a cohesive workflow system in `blueprint_user_directives.md`. They process user-defined automation directives that users create dynamically (home automation, cloud infrastructure, etc.). Individual markdown files are not needed since they work together as a processing pipeline.

---

## Files Location

All directive markdown files should be created in:
```
docs/directives/
```

Current structure:
```
docs/
├── directives/               # TO BE CREATED (100 files)
│   ├── aifp_run.md
│   ├── aifp_status.md
│   ├── fp_purity.md
│   ├── fp_immutability.md
│   ├── ...
│   ├── project_init.md
│   ├── project_file_write.md
│   ├── ...
│   ├── git_init.md
│   └── ...
└── directiveNotes/          # Current location (legacy)
    ├── directive_aifp_run.md       ✅ EXISTS
    ├── directive_file_write.md     ✅ EXISTS
    └── directive_task_decomposition.md  ✅ EXISTS
```

---

## 1. Core System Directives (2 files)

These are the foundational directives that orchestrate the entire AIFP system.

### aifp_run.md ✅ EXISTS (as directive_aifp_run.md)
- **Directive**: `aifp_run`
- **Type**: System orchestrator
- **Status**: Partial documentation exists
- **Priority**: CRITICAL - Required for Phase 1

**Purpose**: Gateway directive that AI calls automatically before every response. Evaluates user request, determines which directives to apply, and orchestrates the entire workflow.

**Content Should Include**:
- Automatic execution behavior
- Task type evaluation (coding, project, discussion)
- Directive selection logic
- Self-assessment questions
- Integration with `get_all_directives()`

---

### aifp_status.md
- **Directive**: `aifp_status`
- **Type**: Status reporting
- **Status**: NOT CREATED
- **Priority**: HIGH - Required for Phase 1

**Purpose**: Provides comprehensive project status report including ProjectBlueprint.md context, current work focus, open items, ambiguities, and recommended next actions.

**Content Should Include**:
- Status-first behavior for continuation requests
- What information is displayed
- Integration with `get_status_tree()` helper
- Historical context tracking
- Ambiguity detection

---

## 2. FP Core Directives (30 files)

Core functional programming enforcement directives from `directives-fp-core.json`.

### Purity & Side Effects (5 files)

#### fp_purity.md
- **Directive**: `fp_purity`
- **Type**: FP Core
- **Level**: 1 (Critical)
- **Priority**: CRITICAL - Phase 2

**Purpose**: Enforce pure functions - same inputs always produce same outputs, no side effects.

**Key Topics**:
- Definition of purity
- Detecting impure functions
- Refactoring impure to pure
- Examples: pure vs impure

---

#### fp_side_effect_detection.md
- **Directive**: `fp_side_effect_detection`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Detect and flag side effects (I/O, mutations, external state changes).

---

#### fp_io_isolation.md
- **Directive**: `fp_io_isolation`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Isolate I/O operations to dedicated "effect" functions, separate from pure logic.

---

#### fp_side_effects_flag.md
- **Directive**: `fp_side_effects_flag`
- **Type**: FP Core
- **Priority**: MEDIUM

**Purpose**: Flag functions with side effects for auditing and refactoring.

---

#### fp_logging_safety.md
- **Directive**: `fp_logging_safety`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Ensure logging doesn't compromise function purity.

---

### Immutability & State (5 files)

#### fp_immutability.md
- **Directive**: `fp_immutability`
- **Type**: FP Core
- **Level**: 1 (Critical)
- **Priority**: CRITICAL - Phase 2

**Purpose**: Enforce immutable data structures - no mutations allowed.

---

#### fp_no_reassignment.md
- **Directive**: `fp_no_reassignment`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Prevent variable reassignment (const enforcement).

---

#### fp_state_elimination.md
- **Directive**: `fp_state_elimination`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Eliminate stateful code patterns, convert to functional.

---

#### fp_const_refactoring.md
- **Directive**: `fp_const_refactoring`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Refactor mutable variables to const/final.

---

#### fp_ownership_safety.md
- **Directive**: `fp_ownership_safety`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Apply ownership/borrowing rules (Rust-inspired).

---

### OOP Elimination (3 files)

#### fp_no_oop.md ✅ PARTIAL (in fp_directives.md)
- **Directive**: `fp_no_oop`
- **Type**: FP Core
- **Level**: 1 (Critical)
- **Priority**: CRITICAL - Phase 2

**Purpose**: No classes, inheritance, polymorphism - pure functional only.

---

#### fp_inheritance_flattening.md
- **Directive**: `fp_inheritance_flattening`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Convert class hierarchies to flat functional modules.

---

#### fp_reflection_limitation.md
- **Directive**: `fp_reflection_limitation`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Limit or eliminate reflection (dynamic type inspection).

---

### Type Safety & Error Handling (7 files)

#### fp_type_safety.md
- **Directive**: `fp_type_safety`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Enforce strong typing with explicit type annotations.

---

#### fp_result_types.md
- **Directive**: `fp_result_types`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Use Result/Either types instead of exceptions.

---

#### fp_optionals.md
- **Directive**: `fp_optionals`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Use Option/Maybe types instead of null.

---

#### fp_null_elimination.md
- **Directive**: `fp_null_elimination`
- **Type**: FP Core
- **Priority**: HIGH

**Purpose**: Eliminate null/undefined usage.

---

#### fp_try_monad.md
- **Directive**: `fp_try_monad`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Monadic try/catch alternative.

---

#### fp_error_pipeline.md
- **Directive**: `fp_error_pipeline`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Chain error handling through pipelines.

---

#### fp_generic_constraints.md
- **Directive**: `fp_generic_constraints`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Type constraints for generics/templates.

---

### Function Composition & Patterns (10 files)

#### fp_currying.md
- **Directive**: `fp_currying`
- **Type**: FP Core
- **Priority**: MEDIUM

**Purpose**: Transform multi-argument functions to curried single-argument.

---

#### fp_chaining.md
- **Directive**: `fp_chaining`
- **Type**: FP Core
- **Priority**: MEDIUM

**Purpose**: Chain function calls fluently.

---

#### fp_monadic_composition.md
- **Directive**: `fp_monadic_composition`
- **Type**: FP Core
- **Priority**: MEDIUM

**Purpose**: Compose functions using monadic patterns.

---

#### fp_pattern_matching.md
- **Directive**: `fp_pattern_matching`
- **Type**: FP Core
- **Priority**: MEDIUM

**Purpose**: Use pattern matching for conditional logic.

---

#### fp_guard_clauses.md
- **Directive**: `fp_guard_clauses`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Early return patterns for validation.

---

#### fp_recursion_enforcement.md
- **Directive**: `fp_recursion_enforcement`
- **Type**: FP Core
- **Priority**: MEDIUM

**Purpose**: Prefer recursion over loops.

---

#### fp_tail_recursion.md
- **Directive**: `fp_tail_recursion`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Optimize recursion with tail calls.

---

#### fp_map_reduce.md
- **Directive**: `fp_map_reduce`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Map/reduce patterns for collections.

---

#### fp_list_operations.md
- **Directive**: `fp_list_operations`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Functional list operations (filter, fold, etc.).

---

#### fp_data_filtering.md
- **Directive**: `fp_data_filtering`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Declarative data filtering patterns.

---

---

## 3. FP Auxiliary Directives (32 files)

Advanced FP features, optimizations, and language-specific adaptations.

### Performance & Optimization (8 files)

#### fp_lazy_evaluation.md
- **Directive**: `fp_lazy_evaluation`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Defer computation until needed.

---

#### fp_lazy_computation.md
- **Directive**: `fp_lazy_computation`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Lazy computation patterns.

---

#### fp_memoization.md
- **Directive**: `fp_memoization`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Cache function results for performance.

---

#### fp_purity_caching_analysis.md
- **Directive**: `fp_purity_caching_analysis`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Analyze which pure functions benefit from caching.

---

#### fp_function_inlining.md
- **Directive**: `fp_function_inlining`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Inline small functions for performance.

---

#### fp_constant_folding.md
- **Directive**: `fp_constant_folding`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Compile-time constant evaluation.

---

#### fp_dead_code_elimination.md
- **Directive**: `fp_dead_code_elimination`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Remove unused code paths.

---

#### fp_cost_analysis.md
- **Directive**: `fp_cost_analysis`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Analyze computational cost of functions.

---

### Concurrency & Parallelism (3 files)

#### fp_concurrency_safety.md
- **Directive**: `fp_concurrency_safety`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Ensure thread-safe functional code.

---

#### fp_parallel_evaluation.md
- **Directive**: `fp_parallel_evaluation`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Parallel execution of pure functions.

---

#### fp_task_isolation.md
- **Directive**: `fp_task_isolation`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Isolate concurrent tasks.

---

### Language Standardization (8 files)

#### fp_language_standardization.md
- **Directive**: `fp_language_standardization`
- **Type**: FP Auxiliary
- **Priority**: HIGH

**Purpose**: Standardize FP patterns across languages.

---

#### fp_syntax_normalization.md
- **Directive**: `fp_syntax_normalization`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Normalize syntax for consistency.

---

#### fp_keyword_alignment.md
- **Directive**: `fp_keyword_alignment`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Align keywords across languages.

---

#### fp_encoding_consistency.md
- **Directive**: `fp_encoding_consistency`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Consistent character encoding.

---

#### fp_cross_language_wrappers.md
- **Directive**: `fp_cross_language_wrappers`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Language interop wrappers.

---

#### fp_wrapper_generation.md
- **Directive**: `fp_wrapper_generation`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Auto-generate wrappers for non-FP libraries.

---

#### fp_reflection_block.md
- **Directive**: `fp_reflection_block`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Block reflection usage.

---

#### fp_borrow_check.md
- **Directive**: `fp_borrow_check`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Borrow checker enforcement (Rust-style).

---

### Code Quality & Documentation (6 files)

#### fp_metadata_annotation.md
- **Directive**: `fp_metadata_annotation`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Add metadata annotations to functions.

---

#### fp_docstring_enforcement.md
- **Directive**: `fp_docstring_enforcement`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Enforce docstrings on all functions.

---

#### fp_function_indexing.md
- **Directive**: `fp_function_indexing`
- **Type**: FP Auxiliary
- **Priority**: HIGH

**Purpose**: Index functions in project.db for tracking.

---

#### fp_dependency_tracking.md
- **Directive**: `fp_dependency_tracking`
- **Type**: FP Auxiliary
- **Priority**: HIGH

**Purpose**: Track function dependencies.

---

#### fp_call_graph_generation.md
- **Directive**: `fp_call_graph_generation`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Generate call graphs.

---

#### fp_symbol_map_validation.md
- **Directive**: `fp_symbol_map_validation`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Validate symbol mappings.

---

### Advanced FP Patterns (7 files)

#### fp_pattern_unpacking.md
- **Directive**: `fp_pattern_unpacking`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Destructuring patterns.

---

#### fp_parallel_purity.md
- **Directive**: `fp_parallel_purity`
- **Type**: FP Auxiliary
- **Priority**: MEDIUM

**Purpose**: Ensure purity in parallel contexts.

---

#### fp_conditional_elimination.md
- **Directive**: `fp_conditional_elimination`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Eliminate unnecessary conditionals.

---

#### fp_evaluation_order_control.md
- **Directive**: `fp_evaluation_order_control`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Control evaluation order.

---

#### fp_type_inference.md
- **Directive**: `fp_type_inference`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Type inference patterns.

---

#### fp_runtime_type_check.md
- **Directive**: `fp_runtime_type_check`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Runtime type validation.

---

#### fp_ai_reasoning_trace.md
- **Directive**: `fp_ai_reasoning_trace`
- **Type**: FP Auxiliary
- **Priority**: LOW

**Purpose**: Trace AI reasoning for debugging.

---

---

## 4. Project Directives (25 files)

Project lifecycle management, database updates, task tracking.

### Initialization & Setup (3 files)

#### project_init.md
- **Directive**: `project_init`
- **Type**: Project
- **Level**: 1
- **Priority**: CRITICAL - Phase 1

**Purpose**: Initialize new AIFP project - creates `.aifp-project/` structure, databases, ProjectBlueprint.md.

**Content Must Include**:
- Integration with init_aifp_project.py helper functions
- Interactive blueprint creation
- Database initialization
- Validation workflow
- Restoration from .git/.aifp/ backup

---

#### project_blueprint_read.md
- **Directive**: `project_blueprint_read`
- **Type**: Project
- **Priority**: HIGH

**Purpose**: Read and parse ProjectBlueprint.md for context.

---

#### project_blueprint_update.md
- **Directive**: `project_blueprint_update`
- **Type**: Project
- **Priority**: HIGH

**Purpose**: Update ProjectBlueprint.md when project evolves.

---

### File & Code Operations (3 files)

#### project_file_write.md ✅ EXISTS (as directive_file_write.md)
- **Directive**: `project_file_write`
- **Type**: Project
- **Level**: 2
- **Priority**: CRITICAL - Phase 1
- **Status**: Partial documentation exists

**Purpose**: Write file AND update project.db (files, functions, interactions tables).

---

#### project_update_db.md
- **Directive**: `project_update_db`
- **Type**: Project
- **Priority**: HIGH

**Purpose**: Update project.db when code changes.

---

#### project_compliance_check.md
- **Directive**: `project_compliance_check`
- **Type**: Project
- **Priority**: HIGH

**Purpose**: Verify FP compliance of project code.

---

### Task Management (4 files)

#### project_task_decomposition.md ✅ EXISTS (as directive_task_decomposition.md)
- **Directive**: `project_task_decomposition`
- **Type**: Project
- **Level**: 2
- **Priority**: HIGH
- **Status**: Documentation exists

**Purpose**: Decompose project into tasks, milestones, completion path.

---

#### project_add_path.md
- **Directive**: `project_add_path`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Add new completion path or milestone.

---

#### project_completion_check.md
- **Directive**: `project_completion_check`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Check project completion status.

---

#### project_refactor_path.md
- **Directive**: `project_refactor_path`
- **Type**: Project
- **Priority**: LOW

**Purpose**: Refactor completion path structure.

---

### Project Evolution (4 files)

#### project_evolution.md
- **Directive**: `project_evolution`
- **Type**: Project
- **Level**: 3
- **Priority**: MEDIUM

**Purpose**: Handle project pivots, goal changes, version increments.

---

#### project_auto_resume.md
- **Directive**: `project_auto_resume`
- **Type**: Project
- **Priority**: HIGH

**Purpose**: Auto-resume work from previous session.

---

#### project_auto_summary.md
- **Directive**: `project_auto_summary`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Generate project summary for status.

---

#### project_notes_log.md
- **Directive**: `project_notes_log`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Log decisions and notes to project.db.

---

### Analysis & Tracking (6 files)

#### project_theme_flow_mapping.md
- **Directive**: `project_theme_flow_mapping`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Map themes and flows in project.

---

#### project_dependency_map.md
- **Directive**: `project_dependency_map`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Generate dependency maps.

---

#### project_dependency_sync.md
- **Directive**: `project_dependency_sync`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Sync dependencies with project.db.

---

#### project_metrics.md
- **Directive**: `project_metrics`
- **Type**: Project
- **Priority**: LOW

**Purpose**: Track project metrics (lines of code, functions, etc.).

---

#### project_performance_summary.md
- **Directive**: `project_performance_summary`
- **Type**: Project
- **Priority**: LOW

**Purpose**: Performance analysis summary.

---

#### project_integrity_check.md
- **Directive**: `project_integrity_check`
- **Type**: Project
- **Priority**: LOW

**Purpose**: Check project.db integrity.

---

### Maintenance & Recovery (5 files)

#### project_backup_restore.md
- **Directive**: `project_backup_restore`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Backup and restore project.db.

---

#### project_archive.md
- **Directive**: `project_archive`
- **Type**: Project
- **Priority**: LOW

**Purpose**: Archive completed projects.

---

#### project_error_handling.md
- **Directive**: `project_error_handling`
- **Type**: Project
- **Priority**: MEDIUM

**Purpose**: Handle errors in project operations.

---

#### project_user_referral.md
- **Directive**: `project_user_referral`
- **Type**: Project
- **Priority**: LOW

**Purpose**: Refer user to docs/support when needed.

---

---

## 5. Git Integration Directives (6 files)

Multi-user collaboration, version control, FP-powered conflict resolution.

#### git_init.md
- **Directive**: `git_init`
- **Type**: Git
- **Level**: 1
- **Parent**: `project_init`
- **Priority**: HIGH

**Purpose**: Initialize or integrate with Git repository.

**Content Should Include**:
- Git repository creation
- .gitignore configuration
- Initial commit with .aifp-project/ tracked
- Branch setup
- Integration with project_init

---

#### git_detect_external_changes.md
- **Directive**: `git_detect_external_changes`
- **Type**: Git
- **Priority**: HIGH

**Purpose**: Detect changes made outside AIFP (manual edits, other tools).

**Content Should Include**:
- Git diff analysis
- Sync with project.db
- Update function metadata
- Conflict detection

---

#### git_create_branch.md
- **Directive**: `git_create_branch`
- **Type**: Git
- **Priority**: HIGH

**Purpose**: Create user/AI work branches with naming convention.

**Content Should Include**:
- Branch naming: `aifp-{user}-{number}`
- User identification
- Branch purpose tracking in project.db
- Work branch table updates

---

#### git_detect_conflicts.md
- **Directive**: `git_detect_conflicts`
- **Type**: Git
- **Priority**: HIGH

**Purpose**: FP-powered conflict detection using purity levels.

**Content Should Include**:
- Analyze both versions
- Compare purity levels
- Run tests on both
- Calculate confidence score
- Conflict categorization

---

#### git_merge_branch.md
- **Directive**: `git_merge_branch`
- **Type**: Git
- **Priority**: HIGH

**Purpose**: Merge branches with AI-assisted conflict resolution.

**Content Should Include**:
- Auto-resolve conflicts >0.8 confidence
- FP resolution strategy (higher purity wins)
- Test-based resolution
- Manual resolution prompts
- Merge history tracking

---

#### git_sync_state.md
- **Directive**: `git_sync_state`
- **Type**: Git
- **Priority**: MEDIUM

**Purpose**: Synchronize Git commit hash with project.db.

**Content Should Include**:
- Track last_known_git_hash
- Update on commits
- Detect out-of-sync state
- Trigger external change detection

---

---

## 6. User Preferences Directives (7 files)

User customization and AI behavior preferences.

#### user_preferences_sync.md
- **Directive**: `user_preferences_sync`
- **Type**: User Preferences
- **Priority**: HIGH

**Purpose**: Load user preferences before directive execution.

**Content Should Include**:
- Load from user_preferences.db
- Apply to directive context
- Override default behavior
- Hierarchical preference application

---

#### user_preferences_update.md
- **Directive**: `user_preferences_update`
- **Type**: User Preferences
- **Priority**: HIGH

**Purpose**: Update user preferences from user requests.

**Content Should Include**:
- Parse user preference requests
- Map to directive preferences
- Atomic key-value updates
- Preference validation

---

#### user_preferences_learn.md
- **Directive**: `user_preferences_learn`
- **Type**: User Preferences
- **Priority**: MEDIUM

**Purpose**: Learn preferences from user corrections (opt-in).

**Content Should Include**:
- Detect user corrections
- Infer preference changes
- Prompt for confirmation
- Log to ai_interaction_log
- Privacy/opt-in requirements

---

#### user_preferences_import.md
- **Directive**: `user_preferences_import`
- **Type**: User Preferences
- **Priority**: LOW

**Purpose**: Import preferences from file.

---

#### user_preferences_export.md
- **Directive**: `user_preferences_export`
- **Type**: User Preferences
- **Priority**: LOW

**Purpose**: Export preferences to file.

---

#### tracking_toggle.md
- **Directive**: `tracking_toggle`
- **Type**: User Preferences
- **Priority**: MEDIUM

**Purpose**: Enable/disable tracking features (cost-conscious).

**Content Should Include**:
- Toggle ai_interaction_log
- Toggle fp_flow_tracking
- Toggle helper_function_logging
- All disabled by default
- API cost considerations

---

---

## 7. User System Directives (8 directives - No MD Files)

**Important**: These directives from `directives-user-system.json` do NOT have `md_file_path` fields and will NOT have individual markdown files created.

**Why No Markdown Files?**

User System directives are the **processing system** for user-defined automation directives. They work together as a cohesive workflow (Parse → Validate → Implement → Activate → Monitor) rather than as individual standalone directives.

**Documentation Location**: These directives are fully documented in:
- **[blueprint_user_directives.md](blueprints/blueprint_user_directives.md)** - Complete system architecture

**The 8 User System Directives**:
1. `user_directive_parse` - Parse YAML/JSON/TXT directive files from users
2. `user_directive_validate` - Interactive validation with Q&A
3. `user_directive_implement` - Generate FP-compliant implementation code
4. `user_directive_activate` - Deploy for real-time execution
5. `user_directive_monitor` - Track execution statistics and errors
6. `user_directive_update` - Handle directive file changes
7. `user_directive_deactivate` - Stop and cleanup
8. (Additional directive for directive management)

**User-Defined Directives** (Created by Users):
These are NOT AIFP core directives - they're user-created automation rules like:
- "Turn off lights at 5pm" (home automation)
- "Scale EC2 when CPU > 80%" (cloud infrastructure)
- "Backup database nightly" (custom workflows)

Users write these in `.aifp-project/user-directives/source/` and the User System directives process them.

**Summary**:
- ✅ User System directives: Documented in blueprint (no individual MD files needed)
- ✅ User-defined directives: Created dynamically by users (can't pre-document)

---

## Implementation Priority

### Phase 1 (Critical - Week 1-2)
Must be created before MCP server implementation can begin:
1. ✅ `aifp_run.md` (EXISTS - needs review/update)
2. `aifp_status.md`
3. `project_init.md`
4. ✅ `project_file_write.md` (EXISTS - needs review/update)

### Phase 2 (High Priority - Week 3-6)
Core FP enforcement and project management:
- All FP Core Level 1 directives (3): `fp_purity.md`, `fp_immutability.md`, `fp_no_oop.md`
- All Project Level 2 directives (5): task_decomposition, blueprint, git_init, etc.
- Git integration directives (6 files)

### Phase 3 (Medium Priority - Week 7-12)
Remaining FP core and auxiliary directives:
- FP Core remaining (27 files)
- FP Auxiliary high priority (15 files)
- Remaining project directives (17 files)

### Phase 4 (Low Priority - Week 13+)
Advanced features and optimizations:
- FP Auxiliary remaining (17 files)
- User preferences (7 files)
- Optional enhancements

---

## Markdown File Template

Each directive markdown file should follow this template:

```markdown
# Directive: {directive_name}

**Type**: {FP Core|FP Auxiliary|Project|Git|User Pref|User System}
**Level**: {level if applicable}
**Parent Directive**: {parent if applicable}
**Priority**: {Critical|High|Medium|Low}

---

## Purpose

{1-2 paragraph explanation of what this directive does and why it exists}

---

## When to Apply

This directive applies when:
- {Condition 1}
- {Condition 2}
- {Condition 3}

---

## Workflow

### Trunk: {main workflow step}

1. **Step 1**: {Description}
   - {Action}
   - {Action}

2. **Step 2**: {Description}
   - {Action}
   - {Action}

### Branches

**Branch 1: If {condition}**
- Then: {action}
- Details: {specifics}

**Branch 2: If {condition}**
- Then: {action}
- Details: {specifics}

### Fallback
- {Default action when no branches match}

---

## Examples

### ✅ Compliant Code

\`\`\`python
# Example of code that follows this directive
def example():
    pass
\`\`\`

### ❌ Non-Compliant Code

\`\`\`python
# Example of code that violates this directive
def bad_example():
    pass
\`\`\`

---

## Edge Cases

1. **Edge Case 1**: {description and handling}
2. **Edge Case 2**: {description and handling}

---

## Related Directives

- **Depends On**: {directive_name} - {why}
- **Triggers**: {directive_name} - {when}
- **Escalates To**: {directive_name} - {when}

---

## Helper Functions Used

- `{helper_function_name}()` - {purpose}
- `{helper_function_name}()` - {purpose}

---

## Database Operations

This directive updates the following tables:
- **{table_name}**: {what gets updated}
- **{table_name}**: {what gets updated}

---

## Testing

How to verify this directive is working:
1. {Test scenario 1}
2. {Test scenario 2}

---

## Common Mistakes

- ❌ {Common mistake 1}
- ❌ {Common mistake 2}

---

## References

- [Helper Functions Reference](../helper-functions-reference.md#{section})
- [Blueprint: {name}](../blueprints/blueprint_{name}.md)
- [JSON Definition](../directives-json/{file}.json)
```

---

## Checklist for Phase 2 Implementation

### Core System (2 files)
- [ ] Review and update `directive_aifp_run.md` → move to `directives/aifp_run.md`
- [ ] Create `directives/aifp_status.md`

### FP Core Critical (3 files)
- [ ] Create `directives/fp_purity.md`
- [ ] Create `directives/fp_immutability.md`
- [ ] Create `directives/fp_no_oop.md`

### Project Critical (4 files)
- [ ] Create `directives/project_init.md`
- [ ] Review and update `directive_file_write.md` → move to `directives/project_file_write.md`
- [ ] Review and update `directive_task_decomposition.md` → move to `directives/project_task_decomposition.md`
- [ ] Create `directives/project_blueprint_read.md`

### Git Integration (6 files)
- [ ] Create `directives/git_init.md`
- [ ] Create `directives/git_detect_external_changes.md`
- [ ] Create `directives/git_create_branch.md`
- [ ] Create `directives/git_detect_conflicts.md`
- [ ] Create `directives/git_merge_branch.md`
- [ ] Create `directives/git_sync_state.md`

### FP Core Remaining (27 files)
- [ ] ... (see individual listings above)

### FP Auxiliary (32 files)
- [ ] ... (see individual listings above)

### Project Remaining (17 files)
- [ ] ... (see individual listings above)

### User Preferences (7 files)
- [ ] ... (see individual listings above)

### User System Directives
- [ ] Decide if markdown files needed for user system directives
- [ ] If yes, create specifications for 8 files

---

## Automation Script

To generate stub markdown files:

```bash
#!/bin/bash
# generate-directive-stubs.sh

DIRECTIVES_DIR="docs/directives"
mkdir -p "$DIRECTIVES_DIR"

# List of all directive markdown files
files=(
    "aifp_run.md"
    "aifp_status.md"
    "fp_purity.md"
    "fp_immutability.md"
    # ... (add all 100 files)
)

for file in "${files[@]}"; do
    if [ ! -f "$DIRECTIVES_DIR/$file" ]; then
        cat > "$DIRECTIVES_DIR/$file" <<EOF
# Directive: ${file%.md}

**Status**: TODO - To be documented

This file is a placeholder. See [directives-markdown-reference.md](../directives-markdown-reference.md) for the documentation template.

---

## TODO

- [ ] Write purpose section
- [ ] Document workflow
- [ ] Add examples
- [ ] List related directives
- [ ] Specify helper functions used
EOF
        echo "Created stub: $file"
    fi
done
```

---

## Summary

**Total Documentation Needed**: 100 markdown files (108 directives - 8 User System documented in blueprint)
**Currently Exists**: 4 files (partial)
**Remaining**: 96 files to create

**Note on User System Directives**: The 8 User System directives (`user_directive_parse`, `user_directive_validate`, etc.) are documented together in `blueprint_user_directives.md` as a cohesive processing system. They enable users to create their own automation directives dynamically, so individual markdown files are not applicable.

**Estimated Effort**:
- Critical directives (15 files): 2-4 hours each = 30-60 hours
- High priority (30 files): 1-2 hours each = 30-60 hours
- Medium priority (30 files): 30-60 minutes each = 15-30 hours
- Low priority (25 files): 15-30 minutes each = 6-12 hours

**Total**: 81-162 hours of documentation work (spread across Phase 2-4)

---

**Status**: Planning complete - ready for Phase 2 directive documentation sprint! 📝

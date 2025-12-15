# Directives Quick Reference

**Purpose**: Quick lookup for directive names and locations
**Generated**: 2025-12-07
**Source**: `docs/directives-json/*.json`

---

## Usage

Use this reference when updating directive MD files to cross-reference directive definitions.

**Find a directive definition**:
1. Search this file for the directive name
2. Open the JSON file listed
3. Jump to the line number for the definition

---

## All Directives

Total directives: **124**

### FP Auxiliary Directives

**Count**: 36

| Directive Name | JSON File | Line |
|----------------|-----------|------|
| `fp_ai_reasoning_trace` | directives-fp-aux.json | 1232 |
| `fp_api_design` | directives-fp-aux.json | 1465 |
| `fp_constant_folding` | directives-fp-aux.json | 1075 |
| `fp_cost_analysis` | directives-fp-aux.json | 1153 |
| `fp_cross_language_wrappers` | directives-fp-aux.json | 735 |
| `fp_data_filtering` | directives-fp-aux.json | 346 |
| `fp_dead_code_elimination` | directives-fp-aux.json | 1033 |
| `fp_docstring_enforcement` | directives-fp-aux.json | 559 |
| `fp_documentation` | directives-fp-aux.json | 1525 |
| `fp_encoding_consistency` | directives-fp-aux.json | 815 |
| `fp_error_pipeline` | directives-fp-aux.json | 141 |
| `fp_evaluation_order_control` | directives-fp-aux.json | 1195 |
| `fp_function_indexing` | directives-fp-aux.json | 605 |
| `fp_function_inlining` | directives-fp-aux.json | 987 |
| `fp_keyword_alignment` | directives-fp-aux.json | 689 |
| `fp_language_standardization` | directives-fp-aux.json | 647 |
| `fp_lazy_computation` | directives-fp-aux.json | 903 |
| `fp_lazy_evaluation` | directives-fp-aux.json | 304 |
| `fp_list_operations` | directives-fp-aux.json | 224 |
| `fp_map_reduce` | directives-fp-aux.json | 266 |
| `fp_memoization` | directives-fp-aux.json | 861 |
| `fp_metadata_annotation` | directives-fp-aux.json | 426 |
| `fp_monadic_composition` | directives-fp-aux.json | 1339 |
| `fp_naming_conventions` | directives-fp-aux.json | 1585 |
| `fp_null_elimination` | directives-fp-aux.json | 183 |
| `fp_optionals` | directives-fp-aux.json | 3 |
| `fp_parallel_evaluation` | directives-fp-aux.json | 945 |
| `fp_pattern_unpacking` | directives-fp-aux.json | 384 |
| `fp_purity_caching_analysis` | directives-fp-aux.json | 1112 |
| `fp_recursion_enforcement` | directives-fp-aux.json | 1274 |
| `fp_reflection_block` | directives-fp-aux.json | 517 |
| `fp_result_types` | directives-fp-aux.json | 49 |
| `fp_symbol_map_validation` | directives-fp-aux.json | 472 |
| `fp_syntax_normalization` | directives-fp-aux.json | 777 |
| `fp_test_purity` | directives-fp-aux.json | 1405 |
| `fp_try_monad` | directives-fp-aux.json | 95 |

### FP Core Directives

**Count**: 29

| Directive Name | JSON File | Line |
|----------------|-----------|------|
| `fp_borrow_check` | directives-fp-core.json | 378 |
| `fp_chaining` | directives-fp-core.json | 557 |
| `fp_concurrency_safety` | directives-fp-core.json | 866 |
| `fp_conditional_elimination` | directives-fp-core.json | 1000 |
| `fp_const_refactoring` | directives-fp-core.json | 246 |
| `fp_currying` | directives-fp-core.json | 603 |
| `fp_dependency_tracking` | directives-fp-core.json | 912 |
| `fp_generic_constraints` | directives-fp-core.json | 1041 |
| `fp_guard_clauses` | directives-fp-core.json | 954 |
| `fp_immutability` | directives-fp-core.json | 200 |
| `fp_inheritance_flattening` | directives-fp-core.json | 515 |
| `fp_io_isolation` | directives-fp-core.json | 1133 |
| `fp_logging_safety` | directives-fp-core.json | 1179 |
| `fp_no_oop` | directives-fp-core.json | 423 |
| `fp_no_reassignment` | directives-fp-core.json | 292 |
| `fp_ownership_safety` | directives-fp-core.json | 329 |
| `fp_parallel_purity` | directives-fp-core.json | 1225 |
| `fp_pattern_matching` | directives-fp-core.json | 645 |
| `fp_purity` | directives-fp-core.json | 3 |
| `fp_reflection_limitation` | directives-fp-core.json | 1350 |
| `fp_runtime_type_check` | directives-fp-core.json | 1087 |
| `fp_side_effect_detection` | directives-fp-core.json | 132 |
| `fp_side_effects_flag` | directives-fp-core.json | 820 |
| `fp_state_elimination` | directives-fp-core.json | 83 |
| `fp_tail_recursion` | directives-fp-core.json | 691 |
| `fp_task_isolation` | directives-fp-core.json | 1267 |
| `fp_type_inference` | directives-fp-core.json | 774 |
| `fp_type_safety` | directives-fp-core.json | 728 |
| `fp_wrapper_generation` | directives-fp-core.json | 469 |

### Git Integration Directives

**Count**: 6

| Directive Name | JSON File | Line |
|----------------|-----------|------|
| `git_create_branch` | directives-git.json | 202 |
| `git_detect_conflicts` | directives-git.json | 324 |
| `git_detect_external_changes` | directives-git.json | 97 |
| `git_init` | directives-git.json | 3 |
| `git_merge_branch` | directives-git.json | 456 |
| `git_sync_state` | directives-git.json | 631 |

### Project Management Directives

**Count**: 37

| Directive Name | JSON File | Line |
|----------------|-----------|------|
| `aifp_help` | directives-project.json | 2894 |
| `aifp_run` | directives-project.json | 3 |
| `aifp_status` | directives-project.json | 1644 |
| `project_add_path` | directives-project.json | 460 |
| `project_archive` | directives-project.json | 1474 |
| `project_auto_resume` | directives-project.json | 1388 |
| `project_auto_summary` | directives-project.json | 1598 |
| `project_backup_restore` | directives-project.json | 1431 |
| `project_blueprint_read` | directives-project.json | 1847 |
| `project_blueprint_update` | directives-project.json | 1935 |
| `project_completion_check` | directives-project.json | 789 |
| `project_compliance_check` | directives-project.json | 709 |
| `project_dependency_map` | directives-project.json | 1559 |
| `project_dependency_sync` | directives-project.json | 1298 |
| `project_error_handling` | directives-project.json | 845 |
| `project_evolution` | directives-project.json | 902 |
| `project_file_delete` | directives-project.json | 2099 |
| `project_file_read` | directives-project.json | 2048 |
| `project_file_write` | directives-project.json | 524 |
| `project_init` | directives-project.json | 95 |
| `project_integrity_check` | directives-project.json | 1345 |
| `project_item_create` | directives-project.json | 2375 |
| `project_metrics` | directives-project.json | 1202 |
| `project_milestone_complete` | directives-project.json | 2767 |
| `project_performance_summary` | directives-project.json | 1255 |
| `project_refactor_path` | directives-project.json | 1517 |
| `project_sidequest_complete` | directives-project.json | 2673 |
| `project_sidequest_create` | directives-project.json | 2430 |
| `project_subtask_complete` | directives-project.json | 2593 |
| `project_subtask_create` | directives-project.json | 2316 |
| `project_task_complete` | directives-project.json | 2486 |
| `project_task_create` | directives-project.json | 2158 |
| `project_task_decomposition` | directives-project.json | 324 |
| `project_task_update` | directives-project.json | 2213 |
| `project_theme_flow_mapping` | directives-project.json | 1116 |
| `project_update_db` | directives-project.json | 625 |
| `project_user_referral` | directives-project.json | 1059 |

### User Preference Directives

**Count**: 7

| Directive Name | JSON File | Line |
|----------------|-----------|------|
| `project_notes_log` | directives-user-pref.json | 410 |
| `tracking_toggle` | directives-user-pref.json | 499 |
| `user_preferences_export` | directives-user-pref.json | 263 |
| `user_preferences_import` | directives-user-pref.json | 332 |
| `user_preferences_learn` | directives-user-pref.json | 182 |
| `user_preferences_sync` | directives-user-pref.json | 3 |
| `user_preferences_update` | directives-user-pref.json | 77 |

### User Directive System

**Count**: 9

| Directive Name | JSON File | Line |
|----------------|-----------|------|
| `user_directive_activate` | directives-user-system.json | 481 |
| `user_directive_approve` | directives-user-system.json | 391 |
| `user_directive_deactivate` | directives-user-system.json | 844 |
| `user_directive_implement` | directives-user-system.json | 230 |
| `user_directive_monitor` | directives-user-system.json | 611 |
| `user_directive_parse` | directives-user-system.json | 14 |
| `user_directive_status` | directives-user-system.json | 950 |
| `user_directive_update` | directives-user-system.json | 713 |
| `user_directive_validate` | directives-user-system.json | 141 |

---

## Quick Search Tips

**In VS Code / IDE**:
- Ctrl+F / Cmd+F: Search this file for directive name
- Double-click directive name to select, then Ctrl+F to find in JSON

**Command line**:
```bash
# Find directive definition
grep -n "directive_name" docs/directives-json/*.json

# Find corresponding MD file
ls src/aifp/reference/directives/directive_name.md

# Search MD file content
grep -n "pattern" src/aifp/reference/directives/directive_name.md
```

---

## Related Files

- `HELPER_FUNCTIONS_QUICK_REF.md` - Helper function names and locations
- `MD_HELPER_REFS_ANALYSIS.md` - Full analysis of helper refs in MD files
- `DIRECTIVE_CLEANUP_TASK.md` - Overall directive cleanup task

---

## Directive JSON → MD File Mapping

**JSON files** (dev staging): `docs/directives-json/*.json`
**MD files** (shipped with package): `src/aifp/reference/directives/*.md`

Each directive has:
- JSON definition (workflows, keywords, thresholds)
- MD documentation (purpose, examples, workflows, edge cases)

Both files should have matching directive names.

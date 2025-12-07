# Directive MD Files - Cleanup Progress Checklist

**Created**: 2025-12-07
**Purpose**: Track manual cleanup progress for 94 directive markdown files
**Total Files**: 94
**Status**: ⏳ In Progress

---

## Progress Summary

- [ ] **Phase 1**: High-Priority Files (7 files)
- [ ] **Phase 2**: Files with Module Paths (4 files)
- [ ] **Phase 3**: Files with Multiple Issues (15+ files)
- [ ] **Phase 4**: Remaining Files (~70 files)

**Completion**: 0 / 94 files complete

---

## How to Use This Checklist

1. **Pick a file** from the list below (high-priority first)
2. **Review** the file using:
   - `MD_HELPER_REFS_ANALYSIS.md` - Replacement templates
   - `HELPER_FUNCTIONS_QUICK_REF.md` - Verify helper names
   - `DIRECTIVES_QUICK_REF.md` - Cross-reference directives
3. **Check off sub-items** as you fix each issue
4. **Check off main item** when file review is complete
5. **Update completion count** at top when done

---

## Issue Type Key

- 🔗 **Helper Ref Link** - Link to `helper-functions-reference.md` (REMOVE)
- 📂 **Module Path** - Hardcoded `src/aifp/helpers/*.py` path (REMOVE)
- 📋 **Section Header** - "## Helper Functions" section (REPLACE with DB guidance)
- 📝 **Function List** - Hardcoded helper function list (VERIFY & UPDATE)
- ⚙️ **Call Instruction** - Workflow mentions specific helper (VERIFY helper exists)

---

## High-Priority Files (Phase 1)

These files are core directives or heavily affected by helper changes.


### [ ] aifp_help.md 🔴 **HIGH PRIORITY**

**Issues**: 5 | **Priority Score**: 170

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 412: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`
- [ ] **📂 Module Paths** (4 found)
  - Line 80: `- **Module**: `src/aifp/helpers/mcp.py``
  - Line 296: `- Module: `src/aifp/helpers/mcp.py``
  - Line 301: `- Module: `src/aifp/helpers/mcp.py``
  - _(+ 1 more)_


### [ ] user_preferences_update.md 🔴 **HIGH PRIORITY**

**Issues**: 3 | **Priority Score**: 130

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 667: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`
- [ ] **⚙️ Call Instructions** (2 found)
  - Line 16: `- **Intent-based matching**: Uses `find_directive_by_intent` helper to...`
  - Line 24: `2. **Find matching directive** - Use `find_directive_by_intent` helper...`


### [ ] user_directive_parse.md 🔴 **HIGH PRIORITY**

**Issues**: 2 | **Priority Score**: 120

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 583: `- [Helper Functions Reference](../helper-functions-reference.md#user-d...`
- [ ] **⚙️ Call Instructions** (1 found)
  - Line 85: `- Use NLP helper: `parse_natural_language_directive(text)``


### [ ] user_directive_validate.md 🔴 **HIGH PRIORITY**

**Issues**: 1 | **Priority Score**: 110

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 678: `- [Helper Functions Reference](../helper-functions-reference.md#valida...`


---

## Files with Multiple Issues (Phase 3)

These have 2+ issues requiring careful review.


### [ ] fp_chaining.md

**Issues**: 3 | **Priority Score**: 30

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 740: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`
- [ ] **📝 Function Lists** (2 found)
  - Line 683: `- `generate_pipe_function() -> str` - Generate pipe helper code`
  - Line 684: `- `generate_compose_function() -> str` - Generate compose helper code`


### [ ] fp_optionals.md

**Issues**: 2 | **Priority Score**: 20

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 513: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`
- [ ] **📋 Section Headers** (1 found)
  - Line 339: `# ✅ Better: Use helper function`


### [ ] project_update_db.md

**Issues**: 2 | **Priority Score**: 20

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 473: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`
- [ ] **📝 Function Lists** (1 found)
  - Line 395: `- `begin_transaction()`, `commit_transaction()`, `rollback_transaction...`


---

## Remaining Files (Phase 4)

Single-issue files (mostly helper ref links).


### [ ] fp_lazy_computation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 722: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_guard_clauses.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 598: `## Helper Functions`


### [ ] fp_const_refactoring.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 632: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_state_elimination.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 638: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_dependency_tracking.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 504: `## Helper Functions`


### [ ] fp_type_inference.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 492: `## Helper Functions`


### [ ] git_detect_external_changes.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 461: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_runtime_type_check.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 457: `## Helper Functions`


### [ ] fp_dead_code_elimination.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 590: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] git_create_branch.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 484: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_blueprint_update.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **⚙️ Call Instructions** (1 found)
  - Line 59: `- Call `project_blueprint_read` helper`


### [ ] user_directive_monitor.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 598: `- [Helper Functions Reference](../helper-functions-reference.md#monito...`


### [ ] project_dependency_map.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 646: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_constant_folding.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 495: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_task_isolation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 506: `## Helper Functions`


### [ ] fp_encoding_consistency.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 628: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] user_directive_implement.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 906: `- [Helper Functions Reference](../helper-functions-reference.md#code-g...`


### [ ] fp_error_pipeline.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 728: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_purity_caching_analysis.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 662: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_reflection_limitation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 437: `## Helper Functions`


### [ ] fp_keyword_alignment.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 632: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_null_elimination.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 629: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_metadata_annotation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 652: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_parallel_evaluation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 620: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_archive.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 524: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_parallel_purity.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 454: `## Helper Functions`


### [ ] fp_naming_conventions.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 514: `## Helper Functions`


### [ ] fp_map_reduce.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 589: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_syntax_normalization.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 592: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] tracking_toggle.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 599: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_ownership_safety.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 720: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_sidequest_create.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 624: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_data_filtering.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 658: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_function_inlining.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 523: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_compliance_check.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 427: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_call_graph_generation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 464: `## Helper Functions`


### [ ] fp_pattern_unpacking.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 658: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] git_sync_state.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 531: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_inheritance_flattening.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 820: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_list_operations.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 589: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_function_indexing.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 767: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_io_isolation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 649: `## Helper Functions`


### [ ] user_directive_activate.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 764: `- [Helper Functions Reference](../helper-functions-reference.md#deploy...`


### [ ] fp_generic_constraints.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 494: `## Helper Functions`


### [ ] fp_borrow_check.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 671: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] git_detect_conflicts.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 641: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_test_purity.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 519: `## Helper Functions`


### [ ] fp_immutability.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 471: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_tail_recursion.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 492: `## Helper Functions`


### [ ] fp_language_standardization.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 639: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] user_preferences_learn.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 537: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] user_directive_approve.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 660: `- [Helper Functions Reference](../helper-functions-reference.md#approv...`


### [ ] fp_evaluation_order_control.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 689: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_type_safety.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 484: `## Helper Functions`


### [ ] fp_conditional_elimination.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 542: `## Helper Functions`


### [ ] git_merge_branch.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 792: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_notes_log.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 786: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_purity.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 435: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_symbol_map_validation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 645: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_no_reassignment.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 637: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_side_effect_detection.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 646: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_lazy_evaluation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 608: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_refactor_path.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 544: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_result_types.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 682: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_auto_summary.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 542: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_concurrency_safety.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 538: `## Helper Functions`


### [ ] fp_monadic_composition.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 737: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_backup_restore.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 535: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_api_design.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 652: `## Helper Functions`


### [ ] fp_documentation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 679: `## Helper Functions`


### [ ] fp_cost_analysis.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 523: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_side_effects_flag.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 625: `## Helper Functions`


### [ ] fp_docstring_enforcement.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 672: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_memoization.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 530: `## Helper Functions`


### [ ] fp_reflection_block.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 667: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_wrapper_generation.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 745: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_recursion_enforcement.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 695: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_try_monad.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 635: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] git_init.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 479: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_currying.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 637: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_ai_reasoning_trace.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 620: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] project_blueprint_read.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 406: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_pattern_matching.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 551: `## Helper Functions`


### [ ] fp_cross_language_wrappers.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 728: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] user_preferences_sync.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 555: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`


### [ ] fp_logging_safety.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **📋 Section Headers** (1 found)
  - Line 616: `## Helper Functions`


### [ ] fp_no_oop.md

**Issues**: 1 | **Priority Score**: 10

- [ ] **🔗 Helper Ref Links** (1 found)
  - Line 571: `- [Helper Functions Reference](../../../docs/helper-functions-referenc...`

---

## Resources

**Analysis & Templates**:
- `MD_HELPER_REFS_ANALYSIS.md` - Full analysis with replacement templates
- `DIRECTIVE_CLEANUP_TASK.md` - Overall cleanup task doc

**Quick References**:
- `HELPER_FUNCTIONS_QUICK_REF.md` - All 337 helpers with locations
- `DIRECTIVES_QUICK_REF.md` - All 125 directives with locations

**Helper Registry** (verify removals/changes):
- `docs/helpers/registry/CONSOLIDATION_REPORT.md` - What changed
- `docs/helpers/registry/CURRENT_STATUS.md` - Registry overview

---

## Standard Replacement Templates

### Template 1: Remove Helper Ref Link
Simply delete the line:
```markdown
- [Helper Functions Reference](../../../docs/helper-functions-reference.md#section)
```

### Template 2: Replace Helper Section
Replace:
```markdown
## Helper Functions

- `helper_name()` - Description
```

With:
```markdown
## Helper Functions

This directive's helpers are dynamically mapped in `aifp_core.db`.

Query at runtime:
\```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
\```
```

### Template 3: Remove Module Path
Remove the Module line, keep other details:
```markdown
**Helper Function**:
- **Name**: `function_name`
- **Module**: `src/aifp/helpers/module.py`  ← DELETE THIS
- **Parameters**: ...  ← KEEP THIS
```

---

## Completion Tracking

Update this section as you progress:

**By Phase**:
- [ ] Phase 1 Complete: 0 / 7 high-priority files
- [ ] Phase 2 Complete: 0 / 4 module path files
- [ ] Phase 3 Complete: 0 / ~15 multi-issue files
- [ ] Phase 4 Complete: 0 / ~70 remaining files

**By Issue Type**:
- [ ] All helper ref links removed (71 total)
- [ ] All module paths removed (4 total)
- [ ] All section headers reviewed (23 total)
- [ ] All function lists verified (3 total)
- [ ] All call instructions verified (4 total)

**Final Steps**:
- [ ] Review 5 high-priority files end-to-end for accuracy
- [ ] Spot-check 10 random files for quality
- [ ] Update system prompt if needed
- [ ] Mark DIRECTIVE_CLEANUP_TASK.md as complete

---

**Last Updated**: 2025-12-07
**Status**: Ready for manual cleanup

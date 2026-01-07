# project_compliance_check - All References Analysis

**Date**: 2026-01-06
**Purpose**: Comprehensive list of all project_compliance_check references and action plan

---

## Summary

**Total Files**: 60 MD files + JSON files
- **FP Directives**: 47 files (KEEP - reference material)
- **Non-FP Directives**: 11 files (REVIEW - likely remove)
- **JSON Files**: 2 files (UPDATED)

---

## FP Directives (47 files) - ✅ KEEP AS REFERENCE

These are FP directive MD files. References to project_compliance_check should STAY as reference material since FP directives are consulted by AI, not executed. The references show that compliance checking (when enabled) can track usage of these patterns.

**Action**: Verify references are framed as "tracked by compliance_checking feature (optional)"

### Core FP Directives
1. fp_purity.md
2. fp_immutability.md
3. fp_no_oop.md
4. fp_side_effect_detection.md
5. fp_state_elimination.md
6. fp_type_safety.md
7. fp_result_types.md
8. fp_optionals.md

### Error Handling FP Directives
9. fp_try_monad.md
10. fp_error_pipeline.md

### OOP Elimination FP Directives
11. fp_wrapper_generation.md
12. fp_inheritance_flattening.md
13. fp_const_refactoring.md

### Type Safety FP Directives
14. fp_type_inference.md
15. fp_runtime_type_check.md
16. fp_generic_constraints.md
17. fp_symbol_map_validation.md
18. fp_null_elimination.md
19. fp_no_reassignment.md

### Pattern & Structure FP Directives
20. fp_pattern_matching.md
21. fp_guard_clauses.md
22. fp_conditional_elimination.md
23. fp_chaining.md
24. fp_list_operations.md

### Advanced FP Directives
25. fp_memoization.md
26. fp_lazy_evaluation.md
27. fp_parallel_purity.md
28. fp_purity_caching_analysis.md
29. fp_function_inlining.md
30. fp_dead_code_elimination.md
31. fp_tail_recursion.md

### Testing & Verification FP Directives
32. fp_test_purity.md
33. fp_dependency_tracking.md
34. fp_borrow_check.md
35. fp_ownership_safety.md

### Safety & Isolation FP Directives
36. fp_io_isolation.md
37. fp_task_isolation.md
38. fp_concurrency_safety.md
39. fp_logging_safety.md
40. fp_side_effects_flag.md

### Reflection & Meta FP Directives
41. fp_reflection_block.md
42. fp_reflection_limitation.md
43. fp_syntax_normalization.md

### Documentation FP Directives
44. fp_documentation.md
45. fp_docstring_enforcement.md
46. fp_naming_conventions.md
47. fp_api_design.md
48. fp_ai_reasoning_trace.md

---

## Non-FP Directives (11 files) - ⚠️ REVIEW & UPDATE

### Tracking-Related (KEEP with updates)

#### tracking_toggle.md
- **Action**: ✅ KEEP - Update to show compliance_checking as one of the tracking features
- **Reason**: This directive enables/disables compliance_checking
- **Update**: Add compliance_checking to list of toggleable tracking features

#### user_preferences_sync.md
- **Action**: ✅ KEEP (if references tracking settings)
- **Review**: Check if it mentions compliance_checking tracking feature
- **Update**: Ensure references are about tracking settings, not validation

#### user_preferences_import.md
- **Action**: ✅ KEEP with edits
- **Review**: Line 127, 332 - Remove references to strict_mode (setting removed)
- **Update**: Remove outdated preference examples

#### user_preferences_update.md
- **Action**: ✅ KEEP with review
- **Review**: Check if mentions compliance preferences (removed in v3.1)

---

### Project Directives (REMOVE references)

#### project_update_db.md
- **Current**: Lines 376, 383 - Lists compliance_check as caller/validator
- **Action**: ❌ REMOVE - No validation needed before DB updates (FP is baseline)
- **Reason**: Compliance checking is NOT called during DB updates

#### project_file_read.md
- **Current**: Lines 36, 392, 485 - Validates FP adherence
- **Action**: ❌ REMOVE - File reading doesn't need compliance validation
- **Reason**: No validation happens during file reads

#### project_task_update.md
- **Current**: Lines 37, 375 - Updates tasks based on validation results
- **Action**: ❌ REMOVE - Task updates don't trigger compliance checks
- **Reason**: Compliance checking is opt-in tracking, not automatic

#### project_dependency_map.md
- **Current**: Lines 35, 547 - Analyzes dependencies for violations
- **Action**: ❌ REMOVE - Dependency mapping doesn't involve compliance
- **Reason**: No validation happens during dependency analysis

#### project_blueprint_read.md
- **Current**: Line 251 - Suggests running compliance check for consistency
- **Action**: ❌ REMOVE - Blueprint reading doesn't trigger validation
- **Reason**: No validation happens during blueprint reads

#### project_archive.md
- **Current**: Line 428 - "Final compliance check" before archiving
- **Action**: ❌ REMOVE - No compliance check needed before archive
- **Reason**: FP is baseline, no final check needed

---

### Parent Relationship Updates (CRITICAL)

#### project_completion_check.md
- **Current**: Line 5 - Parent: project_compliance_check
- **Current**: Line 476 - Parent validates FP compliance before completion
- **Action**: ✅ UPDATED in JSON (parent → project_milestone_complete)
- **Action**: ⚠️ UPDATE MD file - Remove parent reference to compliance_check

#### project_error_handling.md
- **Current**: Line 5 - Parent: project_compliance_check
- **Current**: Lines 324, 494 - Uses error handling for validation failures
- **Action**: ✅ UPDATED in JSON (parent → null, standalone)
- **Action**: ⚠️ UPDATE MD file - Remove parent reference to compliance_check

---

### Git Directives (REMOVE references)

#### git_detect_external_changes.md
- **Current**: Lines 142, 197, 374 - Suggests compliance check after external changes
- **Action**: ❌ REMOVE - External changes don't need compliance checks
- **Reason**: FP is baseline behavior, no validation needed

---

## JSON Files - ✅ UPDATED

### directives-project.json
- **Status**: ✅ UPDATED
- **Changes**:
  - Type changed to "tracking"
  - Level set to null
  - Parent_directive set to null
  - Workflow updated for tracking-only
  - Roadblocks updated
  - Intent keywords updated

### directive_flow_project.json
- **Status**: ⏳ PENDING
- **Action**: Remove automatic flow connections to project_compliance_check
- **Flows to Remove**:
  - project_update_db → project_compliance_check
  - project_file_write → project_compliance_check
  - git_merge_branch → project_compliance_check
  - project_compliance_check → fp_purity
  - project_compliance_check → proceed

---

## Action Plan

### Phase 1: ✅ COMPLETED
- [x] Update project_compliance_check.md
- [x] Update directives-project.json
- [x] Add compliance_checking to settings-specification.json
- [x] Fix parent_directive for project_completion_check (JSON)
- [x] Fix parent_directive for project_error_handling (JSON)

### Phase 2: ⏳ IN PROGRESS
- [x] Create comprehensive reference document (this file)
- [ ] Update FP directive references (if needed - verify framing)
- [ ] Remove references from 9 project/git directive MD files
- [ ] Update 2 parent relationship MD files (completion_check, error_handling)
- [ ] Update directive_flow_project.json

### Phase 3: PENDING
- [ ] Verify all changes
- [ ] Test JSON syntax
- [ ] Update project_compliance_check_cleanup_plan.md as COMPLETE

---

## File-by-File Checklist

### FP Directives (47) - ✅ Review Only
- [ ] Verify all 47 FP directive references are framed as optional tracking

### Tracking Directives (4) - ⚠️ Update
- [ ] tracking_toggle.md - Add compliance_checking to toggleable features
- [ ] user_preferences_sync.md - Verify tracking context
- [ ] user_preferences_import.md - Remove strict_mode references (lines 127, 332)
- [ ] user_preferences_update.md - Review for removed preferences

### Project Directives (7) - ❌ Remove References
- [ ] project_update_db.md - Remove lines 376, 383
- [ ] project_file_read.md - Remove lines 36, 392, 485
- [ ] project_task_update.md - Remove lines 37, 375
- [ ] project_dependency_map.md - Remove lines 35, 547
- [ ] project_blueprint_read.md - Remove line 251
- [ ] project_archive.md - Remove line 428
- [ ] project_completion_check.md - Update parent reference (line 5, 476)
- [ ] project_error_handling.md - Update parent reference (line 5, 324, 494)

### Git Directives (1) - ❌ Remove References
- [ ] git_detect_external_changes.md - Remove lines 142, 197, 374

### JSON Files (1) - ⏳ Update Flows
- [ ] directive_flow_project.json - Remove 5 flow connections

---

**Status**: Phase 2 In Progress
**Next**: Start removing references from project/git directive MD files

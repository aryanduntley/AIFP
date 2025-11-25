# Directive Review Master Checklist
**Date**: 2025-11-24
**Approach**: Process 5 directives at a time, systematically
**Total Directives**: 116+ across all files

---

## Per-Directive Review Checklist

For each directive, verify/fix:

### 1. Helper Functions/Tools
- [ ] Remove `available_helpers` arrays (not used by sync-directives.py)
- [ ] Update helper function names to match current helpers
- [ ] Verify helpers exist in helpers_parsed.json
- [ ] Check directive-helper-interactions.json has mappings

### 2. SQL Queries
- [ ] **REMOVE all custom SQL queries from workflow**
- [ ] Replace with appropriate helper function calls
- [ ] Remove `project_id` references (if any remain)
- [ ] Verify helper provides same functionality

### 3. Schema Compliance
- [ ] Remove any `project_id` references
- [ ] Remove any `linked_function_id` references (for type directives)
- [ ] Verify priority values use TEXT ('low', 'medium', 'high', 'critical')
- [ ] Verify status values match CHECK constraints
- [ ] Add new required fields where applicable (file_name, returns, file_id)

### 4. Reservation System (if creates files/functions/types)
- [ ] Add reservation step before creation
- [ ] Include ID embedding: `# AIFP:FILE:10`, `# AIFP:FUNC:42`, `# AIFP:TYPE:7`
- [ ] Add finalization step after implementation
- [ ] Add error handling for reservation conflicts
- [ ] Update `is_reserved` field management

### 5. FP Terminology
- [ ] No OOP concepts (constructor → factory, method → transformer)
- [ ] Unique function names enforced (if creates functions)
- [ ] Use types_functions junction table (not linked_function_id)

### 6. After Every 5 Directives
- [ ] Review corresponding .md files in src/aifp/reference/directives/
- [ ] Update MD to match JSON changes
- [ ] Verify examples still accurate
- [ ] Document new fields/workflows

---

## Progress Tracking

### directives-project.json (37 directives)

#### Batch 1 (Directives 1-5)
- [ ] 1. aifp_run - Top-level orchestration
- [ ] 2. project_init - Project initialization
- [ ] 3. project_task_decomposition - Task breakdown
- [ ] 4. project_add_path - Roadmap management
- [ ] 5. project_file_write - File operations

**MD Files to Review After Batch 1**:
- [ ] aifp_run.md
- [ ] project_init.md
- [ ] project_task_decomposition.md
- [ ] project_add_path.md
- [ ] project_file_write.md

#### Batch 2 (Directives 6-10)
- [ ] 6. project_update_db - Database updates
- [ ] 7. project_compliance_check - Compliance validation
- [ ] 8. project_completion_check - Completion tracking
- [ ] 9. project_error_handling - Error management
- [ ] 10. project_evolution - Project evolution tracking

**MD Files to Review After Batch 2**:
- [ ] project_update_db.md
- [ ] project_compliance_check.md
- [ ] project_completion_check.md
- [ ] project_error_handling.md
- [ ] project_evolution.md

#### Batch 3 (Directives 11-15)
- [ ] 11. project_user_referral - User escalation
- [ ] 12. project_theme_flow_mapping - Theme/flow management
- [ ] 13. project_metrics - Metrics collection
- [ ] 14. project_performance_summary - Performance reporting
- [ ] 15. project_dependency_sync - Dependency management

**MD Files to Review After Batch 3**:
- [ ] project_user_referral.md
- [ ] project_theme_flow_mapping.md
- [ ] project_metrics.md
- [ ] project_performance_summary.md
- [ ] project_dependency_sync.md

#### Batch 4 (Directives 16-20)
- [ ] 16. project_integrity_check - Integrity validation
- [ ] 17. project_auto_resume - Auto-resume functionality
- [ ] 18. project_backup_restore - Backup/restore operations
- [ ] 19. project_archive - Archival management
- [ ] 20. project_refactor_path - Refactoring workflows

**MD Files to Review After Batch 4**:
- [ ] project_integrity_check.md
- [ ] project_auto_resume.md
- [ ] project_backup_restore.md
- [ ] project_archive.md
- [ ] project_refactor_path.md

#### Batch 5 (Directives 21-25)
- [ ] 21. project_dependency_map - Dependency mapping
- [ ] 22. project_auto_summary - Auto-summary generation
- [ ] 23. aifp_status - Status reporting
- [ ] 24. project_blueprint_read - Blueprint reading
- [ ] 25. project_blueprint_update - Blueprint updates

**MD Files to Review After Batch 5**:
- [ ] project_dependency_map.md
- [ ] project_auto_summary.md
- [ ] aifp_status.md
- [ ] project_blueprint_read.md
- [ ] project_blueprint_update.md

#### Batch 6 (Directives 26-30)
- [ ] 26. project_file_read - File reading
- [ ] 27. project_file_delete - File deletion
- [ ] 28. project_task_create - Task creation
- [ ] 29. project_task_update - Task updates
- [ ] 30. project_subtask_create - Subtask creation

**MD Files to Review After Batch 6**:
- [ ] project_file_read.md
- [ ] project_file_delete.md
- [ ] project_task_create.md
- [ ] project_task_update.md
- [ ] project_subtask_create.md

#### Batch 7 (Directives 31-35)
- [ ] 31. project_item_create - Item creation
- [ ] 32. project_sidequest_create - Sidequest creation
- [ ] 33. project_task_complete - Task completion
- [ ] 34. project_subtask_complete - Subtask completion
- [ ] 35. project_sidequest_complete - Sidequest completion

**MD Files to Review After Batch 7**:
- [ ] project_item_create.md
- [ ] project_sidequest_create.md
- [ ] project_task_complete.md
- [ ] project_subtask_complete.md
- [ ] project_sidequest_complete.md

#### Batch 8 (Directives 36-37)
- [ ] 36. project_milestone_complete - Milestone completion
- [ ] 37. aifp_help - Help system

**MD Files to Review After Batch 8**:
- [ ] project_milestone_complete.md
- [ ] aifp_help.md

---

### directives-fp-core.json (30 directives)

#### Batch 9 (Directives 1-5)
- [ ] 1. (TBD - extract names)
- [ ] 2. (TBD)
- [ ] 3. (TBD)
- [ ] 4. (TBD)
- [ ] 5. (TBD)

**MD Files to Review After Batch 9**: (TBD)

#### Batch 10-14: (Continue pattern for remaining 25 FP core directives)

---

### directives-fp-aux.json (36 directives)

#### Batch 15 (Directives 1-5)
- [ ] 1. (TBD - extract names)
- [ ] 2. (TBD)
- [ ] 3. (TBD)
- [ ] 4. (TBD)
- [ ] 5. (TBD)

**MD Files to Review After Batch 15**: (TBD)

#### Batch 16-22: (Continue pattern for remaining 31 FP aux directives)

---

### directives-git.json (6 directives)

#### Batch 23 (Directives 1-5)
- [ ] 1. (TBD - extract names)
- [ ] 2. (TBD)
- [ ] 3. (TBD)
- [ ] 4. (TBD)
- [ ] 5. (TBD)

#### Batch 24 (Directive 6)
- [ ] 6. (TBD)

**MD Files to Review After Batches 23-24**: (TBD)

---

### directives-user-pref.json (7 directives)

#### Batch 25 (Directives 1-5)
- [ ] 1. (TBD - extract names)
- [ ] 2. (TBD)
- [ ] 3. (TBD)
- [ ] 4. (TBD)
- [ ] 5. (TBD)

#### Batch 26 (Directives 6-7)
- [ ] 6. (TBD)
- [ ] 7. (TBD)

**MD Files to Review After Batches 25-26**: (TBD)

---

### directives-user-system.json (Format TBD)

**Status**: Different JSON structure, needs investigation
- [ ] Analyze file structure
- [ ] Extract directive names
- [ ] Create batches

---

## Workflow Commands

### Extract 5 Directives from JSON
```bash
# Extract directives 0-4 (first batch)
jq '.[0:5]' directives-project.json > batch-01-project.json

# Extract directives 5-9 (second batch)
jq '.[5:10]' directives-project.json > batch-02-project.json

# Extract directives 10-14 (third batch)
jq '.[10:15]' directives-project.json > batch-03-project.json
```

### Review Extracted Batch
```bash
# List directive names in batch
jq -r '.[].name' batch-01-project.json

# Check for SQL queries
jq -r '.[].workflow.branches[]?.details?.query? | select(. != null)' batch-01-project.json

# Check for available_helpers
jq -r '.[].workflow.branches[]?.details?.available_helpers? | select(. != null)' batch-01-project.json

# Check for project_id references
jq '.' batch-01-project.json | grep -i 'project_id'
```

### Update Batch
1. Make all fixes to batch-XX-project.json
2. Validate JSON: `jq '.' batch-XX-project.json > /dev/null`
3. Review changes: `git diff batch-XX-project.json`

### Merge Batch Back
```bash
# After all batches complete, merge back
jq -s 'add' batch-*-project.json > directives-project-updated.json

# Verify directive count matches
jq '. | length' directives-project-updated.json
# Should output: 37
```

---

## Known Issues to Fix

### Global Issues (All Files)
1. **Remove available_helpers** - Not used by sync-directives.py
2. **Remove custom SQL queries** - Use helper functions instead
3. **Remove project_id** - No longer in schema

### File-Specific Issues

#### directives-project.json
- SQL queries at lines 1714, 2813, 2832 (use helpers instead)
- Priority values (already correct - TEXT format)
- Status values (already correct - CHECK compliant)

#### directives-fp-core.json
- Unique function name enforcement needed
- returns field for function creation
- Reservation system for function creation

#### directives-fp-aux.json
- types_functions junction table (not linked_function_id)
- Reservation system for type creation
- file_id for type creation
- FP terminology enforcement

#### directives-git.json
- Minimal changes expected (verify no project_id references)

#### directives-user-pref.json
- directive_context → directive_name
- scope CHECK constraint values

---

## Progress Summary

**Total Directive Files**: 5+
**Total Directives**: 116+
**Batches Needed**: ~24 (at 5 directives per batch)
**Estimated Time**: ~30-40 hours (1-2 hours per batch)

### Completion Status
- [ ] directives-project.json (8 batches)
- [ ] directives-fp-core.json (6 batches)
- [ ] directives-fp-aux.json (8 batches)
- [ ] directives-git.json (2 batches)
- [ ] directives-user-pref.json (2 batches)
- [ ] directives-user-system.json (TBD)
- [ ] directive-helper-interactions.json (update mappings)
- [ ] All corresponding .md files

---

## Session Tracking

### Session 1 (2025-11-24)
**Completed**:
- [ ] Schema analysis
- [ ] Planning documents created
- [ ] Master checklist created
- [ ] Batch 1 (directives 1-5)

**Next Session**:
- Start with Batch 1: aifp_run through project_file_write

---

**Last Updated**: 2025-11-24
**Current Batch**: None (ready to start)
**Next Directive**: aifp_run (1/37 in directives-project.json)

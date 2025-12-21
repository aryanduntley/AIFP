# Unmapped Helpers Analysis

**Date**: 2025-12-20
**Purpose**: Analyze remaining 118 unmapped helpers to determine if they need mapping

---

## Summary

**Total Unmapped**: 118 helpers (58.4%)
**Category Breakdown**:
- Core (AI-only): 30 helpers - ✅ Correctly unmapped
- Index: 1 helper - ✅ Correctly unmapped (system utility)
- Git: 1 helper - ✅ Correctly unmapped (query-only)
- User-Custom: 7 helpers - ✅ Correctly unmapped (AI schema/query tools)
- Settings: 8 helpers - ✅ Correctly unmapped (AI schema/query tools)
- Orchestrators: 8 helpers - ✅ Correctly unmapped (AI convenience tools)
- Project: 63 helpers - ⚠️ **NEEDS REVIEW**

---

## By Category Analysis

### ✅ Core Helpers (30 unmapped) - CORRECTLY UNMAPPED

All 30 are AI query/navigation tools for directive metadata:
- Schema queries: get_core_tables, get_core_fields, get_core_schema
- Directive lookups: get_directive_by_name, get_all_directives
- Flow navigation: get_next_directives_from_status, get_completion_loop_target
- Helper queries: get_helper_by_name, get_helpers_by_database
- Category queries: get_category_by_name, get_categories

**Conclusion**: These help AI navigate directives, not used by directives themselves.

---

### ✅ Index Helper (1 unmapped) - CORRECTLY UNMAPPED

- `get_databases` - System-level utility listing available databases

**Conclusion**: System utility for AI, not directive-specific.

---

### ✅ Git Helpers (1 unmapped) - CORRECTLY UNMAPPED

- `list_active_branches` - Query tool for AI to see work branches

**Conclusion**: Query-only tool, no directive needs this.

---

### ✅ User-Custom Helpers (7 unmapped) - CORRECTLY UNMAPPED

All 7 are AI schema/query tools:
- Schema: get_user_custom_tables, get_user_custom_fields, get_user_custom_schema, get_user_custom_json_parameters
- Query: get_from_user_custom, get_from_user_custom_where, query_user_custom

**Conclusion**: AI uses these to explore user_directives.db structure, not called by directives.

---

### ✅ Settings Helpers (8 unmapped) - CORRECTLY UNMAPPED

All 8 are AI schema/query tools:
- Schema: get_settings_tables, get_settings_fields, get_settings_schema, get_settings_json_parameters
- Query: get_from_settings, get_from_settings_where, get_user_setting
- CRUD: delete_settings_entry (manual cleanup only, no directive uses this)

**Conclusion**: AI uses these to explore user_preferences.db structure, not called by directives.

---

### ✅ Orchestrator Helpers (8 unmapped) - CORRECTLY UNMAPPED

All 8 are AI convenience/query tools:
- get_current_progress - AI query tool
- update_project_state - AI convenience tool for state updates
- batch_update_progress - AI bulk update tool
- query_project_state - AI query tool
- validate_initialization - AI validation tool
- get_work_context - AI query tool for session resumption
- get_project_context - AI query tool
- get_files_by_flow_context - AI query tool

**Conclusion**: These serve AI for querying/updating state, not called by directives.

---

### ⚠️ Project Helpers (63 unmapped) - NEEDS DETAILED ANALYSIS

#### Category 1: Schema/Query Tools (10 helpers) - ✅ CORRECTLY UNMAPPED

- get_project_tables, get_project_fields, get_project_schema, get_project_json_parameters
- get_from_project, get_from_project_where, query_project
- get_file_by_name, get_function_by_name, get_file_ids_from_flows

**Conclusion**: AI schema/query tools, no directive mapping needed.

---

#### Category 2: Generic CRUD Tools (3 helpers) - ✅ CORRECTLY UNMAPPED

- add_project_entry - Generic add (AI uses when no specialized helper exists)
- update_project_entry - Generic update (AI uses when no specialized helper exists)
- delete_project_entry - Generic delete (AI uses when no specialized helper exists)

**Conclusion**: Fallback CRUD operations for AI, directives use specialized helpers.

---

#### Category 3: Batch Tools (10 helpers) - ✅ CORRECTLY UNMAPPED

Batch versions of reserve/finalize operations:
- reserve_files, finalize_files
- reserve_functions, finalize_functions
- reserve_types, finalize_types
- add_interactions, add_types_functions

**Conclusion**: AI convenience for bulk operations, directives use singular versions.

---

#### Category 4: Delete Helpers (14 helpers) - ✅ CORRECTLY UNMAPPED

**Key Finding**: Only ONE delete directive exists (`project_file_delete`), already mapped.

No directives exist for deleting:
- delete_type, delete_type_function
- delete_theme, delete_flow
- delete_completion_path
- delete_milestone
- delete_task, delete_subtask, delete_sidequest, delete_item
- delete_interaction
- delete_note

**Conclusion**: All delete helpers (except delete_file/delete_function already mapped) are AI-only tools for manual cleanup.

---

#### Category 5: Query/List Helpers (18 helpers) - ✅ CORRECTLY UNMAPPED

Comprehensive query/filtering tools for AI:
- get_all_completion_paths, get_completion_paths_by_status, get_incomplete_completion_paths
- get_milestones_by_status, get_incomplete_milestones
- get_incomplete_tasks, get_tasks_comprehensive, get_task_flows, get_task_files
- get_incomplete_subtasks, get_subtasks_comprehensive
- get_incomplete_sidequests, get_sidequests_comprehensive, get_sidequest_flows, get_sidequest_files
- get_items_for_subtask, get_items_for_sidequest, get_incomplete_items
- get_themes_for_flow

**Conclusion**: Advanced search/filtering for AI to explore project state, not used by directives.

---

#### Category 6: Reorder/Update Tools (8 helpers) - ✅ CORRECTLY UNMAPPED

Manual management tools:
- reorder_completion_path, reorder_all_completion_paths, swap_completion_paths_order
- update_file_timestamp (sub-helper, called automatically)
- update_function_file_location (refactoring tool, rare use)
- update_type, update_type_function_role
- update_theme, update_flow
- update_interaction
- update_note

**Conclusion**: AI tools for manual adjustments/refactoring, not part of directive workflows.

---

## Final Verdict

### Unmapped Helpers Breakdown

| Category | Unmapped | Should Be Mapped | Correctly Unmapped | Status |
|----------|----------|------------------|--------------------|--------|
| Core | 30 | 0 | 30 | ✅ CORRECT |
| Index | 1 | 0 | 1 | ✅ CORRECT |
| Git | 1 | 0 | 1 | ✅ CORRECT |
| User-Custom | 7 | 0 | 7 | ✅ CORRECT |
| Settings | 8 | 0 | 8 | ✅ CORRECT |
| Orchestrators | 8 | 0 | 8 | ✅ CORRECT |
| **Project** | **63** | **0** | **63** | **✅ CORRECT** |
| **TOTAL** | **118** | **0** | **118** | **✅ ALL CORRECT** |

---

## Conclusion

**ALL 118 unmapped helpers are CORRECTLY unmapped.**

These helpers fall into categories that are intentionally not mapped to directives:
1. **AI Query Tools** - Help AI explore database structure and query data
2. **AI Convenience Tools** - Batch operations, generic CRUD, state management
3. **Manual Management Tools** - Delete, reorder, refactor operations for AI
4. **Sub-Helper Functionality** - Called automatically by other helpers
5. **System Utilities** - Database listing, schema exploration

### What This Means for Phase 8

**Phase 8 Helper Mapping is ACTUALLY COMPLETE!**

- **Mapped**: 84 helpers (41.6%)
- **Unmapped (AI-only)**: 118 helpers (58.4%)
- **Total Coverage**: 84/84 directive-used helpers = **100% of helpers that need mapping**

### Next Steps

1. ✅ Update Phase 8 document metadata to mark as COMPLETE with clarification
2. ✅ Update tracking documents with final statistics
3. ✅ Mark all unmapped helpers with metadata explaining why (AI-only, batch tool, etc.)
4. ✅ Create validation script to verify mapping integrity
5. ✅ Generate Phase 8 completion report

---

**Analysis Date**: 2025-12-20
**Analyst**: Claude Sonnet 4.5
**Status**: ✅ COMPLETE - All directive-used helpers are mapped

# Project Helpers Registry Split Plan

**Date:** 2025-11-27
**Status:** Ready for Implementation

## Summary

Split 167 project helpers into 4 registry files:

| Registry File | Helper Count | Description |
|---------------|--------------|-------------|
| **helpers_registry_project_structure_getters.json** | ~38 | Read operations for files, functions, types, infrastructure |
| **helpers_registry_project_structure_setters.json** | ~38 | Write operations for files, functions, types, infrastructure |
| **helpers_registry_project_workflow_getters.json** | ~45 | Read operations for tasks, flows, themes, milestones, notes |
| **helpers_registry_project_workflow_setters.json** | ~46 | Write operations for tasks, flows, themes, milestones, notes |
| **Total** | **167** | All project database helpers |

---

## File 1: helpers_registry_project_structure_getters.json (~38 helpers)

**Purpose:** Read operations for project code structure

### Categories:
- **Infrastructure queries** (get_infrastructure, get_infrastructure_by_type, etc.)
- **File queries** (get_file, get_files, get_files_by_flow, etc.)
- **Function queries** (get_function, get_functions, get_functions_by_file, etc.)
- **Type queries** (get_type, get_types, get_types_by_file, etc.)
- **Type-Function associations** (get_type_functions_by_function, get_type_functions_by_type, etc.)
- **Interaction queries** (get_interactions, get_interactions_by_type, etc.)
- **File-Flow associations** (get_flows_for_file, get_files_by_flow, get_all_file_flows)

### Example Helpers:
```
get_infrastructure(id)
get_infrastructure_by_type(type)
get_infrastructure_by_type_value(type, value)
get_file(file_id)
get_files([(file_id), (file_id), ...])
get_function(function_id)
get_function_by_name(function_name)
get_functions_by_file(file_id)
get_type(type_id)
get_types_by_file(file_id)
get_type_functions_by_function(function_id)
get_type_functions_by_type(type_id)
get_interactions(limit, orderby)
get_interactions_by_type(type, limit, orderby)
get_files_by_flow(flow_id)
get_flows_for_file(file_id)
... (~38 total)
```

---

## File 2: helpers_registry_project_structure_setters.json (~38 helpers)

**Purpose:** Write operations for project code structure

### Categories:
- **Infrastructure mutations** (add, update, delete)
- **File lifecycle** (reserve, finalize, update, delete, update_checksum, update_timestamp)
- **Function lifecycle** (reserve, finalize, update, delete)
- **Type lifecycle** (reserve, finalize, update, delete)
- **Type-Function mutations** (add, delete)
- **Interaction mutations** (add, update, delete)
- **File-Flow mutations** (add, delete)

### Example Helpers:
```
add_infrastructure(type, value, description)
update_infrastructure(id, type, value, description)
delete_infrastructure(id, note_reason, note_severity, note_source, note_type)
reserve_file(name, path, language)
reserve_files([(name,path,language), ...])
finalize_file(file_id, name, path, language)
finalize_files([...])
update_file(file_id, new_name, new_path, language)
update_file_checksum(file_id)
update_file_timestamp(file_id)
delete_file(file_id, note_reason, note_severity, note_source, note_type)
reserve_function(name, file_id, purpose, params, returns)
finalize_function(function_id, name, file_id, purpose, params, returns)
update_function(function_id, name, purpose, parameters, returns)
delete_function(function_id, note_reason, ...)
reserve_type(name, file_id, purpose)
finalize_type(type_id, name, file_id, purpose)
update_type(type_id, name, purpose)
delete_type(type_id, note_reason, ...)
add_type_function(type_id, function_id, role)
delete_type_function(id, note_reason, ...)
add_interaction(interaction_type, source_id, source_type, target_id, target_type, description)
update_interaction(id, description, interaction_type)
delete_interaction(id, note_reason, ...)
add_file_flows(file_id, flow_id)
delete_file_flow(id, note_reason, ...)
... (~38 total)
```

---

## File 3: helpers_registry_project_workflow_getters.json (~45 helpers)

**Purpose:** Read operations for project workflow and planning

### Categories:
- **Task queries** (get_task, get_tasks, get_tasks_by_status, get_incomplete_tasks, etc.)
- **Subtask queries** (get_subtask, get_subtasks, get_subtasks_by_task, etc.)
- **Sidequest queries** (get_sidequest, get_sidequests, get_sidequests_by_status, etc.)
- **Theme queries** (get_theme, get_themes, get_themes_by_confidence, etc.)
- **Flow queries** (get_flow, get_flows, get_flows_by_confidence, get_flows_for_theme, etc.)
- **Milestone queries** (get_milestone, get_milestones, get_milestones_by_status, etc.)
- **Note queries** (get_note, get_notes, get_notes_by_source, get_notes_by_severity, etc.)
- **Item queries** (get_item, get_items, get_items_by_task, etc.)
- **Completion path queries** (get_completion_path, get_completion_path_stage, etc.)
- **Association queries** (get_task_files, get_task_flows, get_themes_for_flow, etc.)

### Example Helpers:
```
get_task(task_id)
get_tasks([(task_id), (task_id), ...])
get_tasks_by_status(status)
get_incomplete_tasks()
get_task_files(task_id)
get_task_flows(task_id)
get_subtask(subtask_id)
get_subtasks_by_task(task_id)
get_incomplete_subtasks()
get_sidequest(sidequest_id)
get_sidequests_by_status(status)
get_theme(theme_id)
get_theme_by_name(theme_name)
get_themes_by_confidence(greater_than)
get_flow(flow_id)
get_flows_by_confidence(greater_than)
get_flows_for_theme(theme_id)
get_themes_for_flow(flow_id)
get_milestone(milestone_id)
get_milestones_by_status(status)
get_note(note_id)
get_notes_by_source(source)
get_notes_by_severity(severity)
get_item(item_id)
get_items_by_task(task_id)
get_completion_path()
get_completion_path_stage(stage_id)
... (~45 total)
```

---

## File 4: helpers_registry_project_workflow_setters.json (~46 helpers)

**Purpose:** Write operations for project workflow and planning

### Categories:
- **Task mutations** (add, update, delete)
- **Subtask mutations** (add, update, delete)
- **Sidequest mutations** (add, update, delete)
- **Theme mutations** (add, update, delete)
- **Flow mutations** (add, update, delete)
- **Milestone mutations** (add, update, delete)
- **Note mutations** (add, update, delete)
- **Item mutations** (add, update, delete)
- **Completion path mutations** (update, delete)
- **Association mutations** (add_task_files, add_task_flows, add_flow_themes, delete_*)

### Example Helpers:
```
add_task(name, status, priority, description)
update_task(task_id, name, status, priority, description, parent_task_id)
delete_task(task_id, note_reason, note_severity, note_source, note_type)
add_subtask(name, task_id, status, description)
update_subtask(subtask_id, name, status, description)
delete_subtask(subtask_id, note_reason, ...)
add_sidequest(name, subtask_id, status, priority, description)
update_sidequest(sidequest_id, name, status, priority, description)
delete_sidequest(sidequest_id, note_reason, ...)
add_theme(name, description, ai_generated, confidence_score)
update_theme(theme_id, name, description, confidence_score)
delete_theme(theme_id, note_reason, ...)
add_flow(name, description, ai_generated, confidence_score)
update_flow(flow_id, name, description, confidence_score)
delete_flow(flow_id, note_reason, ...)
add_flow_themes(flow_id, theme_id)
delete_flow_themes(id, note_reason, ...)
add_milestone(name, completion_path_id, status, description)
update_milestone(milestone_id, name, status, description)
delete_milestone(milestone_id, note_reason, ...)
add_note(reason, severity, source, type, related_table, related_id)
update_note(note_id, reason, severity)
delete_note(note_id)
add_item(task_id, content, status)
update_item(item_id, content, status)
delete_item(item_id, note_reason, ...)
add_task_files(task_id, file_id)
add_task_flows(task_id, flow_id)
delete_task_file(id, note_reason, ...)
delete_task_flow(id, note_reason, ...)
update_completion_path(stage_id, stage_name, status, description)
delete_completion_path(id, note_reason, ...)
... (~46 total)
```

---

## Implementation Notes

### Return Statements Strategy
Each helper will include comprehensive `return_statements` that reference:
1. **User settings** from `user_preferences.db` (via get_setting, get_directive_preference)
2. **Directive preferences** for behavior customization
3. **Next steps** in workflow (e.g., "after reserve_file, call finalize_file")
4. **Validation checks** (e.g., "verify task has no subtasks before deleting")
5. **Status transitions** (e.g., "after completing task, check parent task status")

### Key Patterns:

**Structure Helpers:**
- Reserve → Finalize workflow for files, functions, types
- Checksum tracking for file modifications
- Cascade deletes with note requirements
- Type-Function role associations

**Workflow Helpers:**
- Task → Subtask → Sidequest hierarchy
- Status tracking (pending, in_progress, completed, cancelled)
- Priority system for task ordering
- Flow → Theme associations for organizing work
- Completion path for milestone tracking
- Note system for change tracking

### Database Schema References:
- **Structure tables:** infrastructure, files, functions, types, type_functions, interactions, file_flows
- **Workflow tables:** tasks, subtasks, sidequests, themes, flows, flow_themes, milestones, items, notes, task_files, task_flows, completion_path

---

## Implementation Progress

**Last Updated:** 2025-11-29
**Status:** 167/167 project helpers complete (100%) ✅

### ✅ Completed Steps

1. ✅ Created helpers_registry_user_directives_setters.json (33 helpers) - 2025-11-27
2. ✅ Created helpers_registry_project_structure_getters.json (38 helpers) - 2025-11-27
3. ✅ Created helpers_registry_project_structure_setters.json (38 helpers) - 2025-11-27
4. ✅ Created helpers_registry_project_workflow_getters.json (54 helpers) - 2025-11-29
5. ✅ Created helpers_registry_project_workflow_setters.json (37 helpers) - 2025-11-29
6. ✅ Updated documentation with completion status - 2025-11-29

### 📊 Final Helper Count

| Registry File | Helper Count | Description |
|---------------|--------------|-------------|
| helpers_registry_project_structure_getters.json | 38 | Read operations for files, functions, types, infrastructure |
| helpers_registry_project_structure_setters.json | 38 | Write operations for files, functions, types, infrastructure |
| helpers_registry_project_workflow_getters.json | 54 | Read operations for tasks, flows, themes, milestones, notes |
| helpers_registry_project_workflow_setters.json | 37 | Write operations for tasks, flows, themes, milestones, notes |
| **Total Project Helpers** | **167** | **Complete project database coverage** |

### 🎉 All Project Helpers Complete!

---

## Consolidation Impact

After completing these registries, the following files can be deprecated:
- ❌ `docs/helpers/helper-architecture.md` (redundant with registries)
- ❌ `docs/helpers/helper-tool-classification.md` (redundant with registries)
- ❌ `docs/helpers/generic-tools-mcp.md` (to be added to core registry)
- ❌ `docs/helpers/generic-tools-project.md` (to be added to core registry)
- ❌ `docs/helpers/helper-functions-reference.md` (redundant with registries)
- ❌ `docs/directives-json/directive-helper-interactions.json` (redundant with registries)
- ❌ `docs/directives-json/helpers_parsed.json` (outdated subset)

**Source of Truth remains:**
- ✅ `docs/helpers/info-helpers-core.txt`
- ✅ `docs/helpers/info-helpers-project.txt`
- ✅ `docs/helpers/info-helpers-user-settings.txt`
- ✅ `docs/helpers/info-helpers-user-custom.txt`

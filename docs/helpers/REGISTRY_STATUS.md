# Helper Registry Consolidation Status

**Last Updated:** 2025-11-27

---

## Overview

Consolidating all AIFP helpers into structured JSON registries for MCP database import.

**Source of Truth Files:**
- ✅ `docs/helpers/info-helpers-core.txt`
- ✅ `docs/helpers/info-helpers-project.txt`
- ✅ `docs/helpers/info-helpers-user-settings.txt`
- ✅ `docs/helpers/info-helpers-user-custom.txt`

---

## Registry Files Status

### ✅ COMPLETED REGISTRIES

| Registry File | Helpers | Database | Status | Notes |
|---------------|---------|----------|--------|-------|
| **helpers_registry_core.json** | 33 | N/A (MCP) | ✅ Complete | Core directives and MCP queries |
| **helpers_registry_user_settings.json** | 40 | user_preferences.db | ✅ Complete | Settings, preferences, tracking |
| **helpers_registry_user_directives_getters.json** | 45 | user_directives.db | ✅ Complete | READ operations |
| **helpers_registry_user_directives_setters.json** | 33 | user_directives.db | ✅ Complete | WRITE operations |
| **SUBTOTAL** | **151** | | | |

### ⏳ PENDING REGISTRIES

| Registry File | Helpers | Database | Status | Notes |
|---------------|---------|----------|--------|-------|
| **helpers_registry_project_structure_getters.json** | 38 | project.db | ⏳ Pending | Files, functions, types, infrastructure |
| **helpers_registry_project_structure_setters.json** | 38 | project.db | ⏳ Pending | Reserve, finalize, update, delete |
| **helpers_registry_project_workflow_getters.json** | 45 | project.db | ⏳ Pending | Tasks, flows, themes, milestones |
| **helpers_registry_project_workflow_setters.json** | 46 | project.db | ⏳ Pending | Add, update, delete workflow |
| **SUBTOTAL** | **167** | | | |

---

## Total Progress

| Metric | Count |
|--------|-------|
| **Completed Helpers** | 151 / 318 |
| **Remaining Helpers** | 167 |
| **Progress** | **47.5%** |

---

## Recently Completed

### 2025-11-27

1. ✅ **Created `helpers_registry_user_directives_setters.json`**
   - 33 setters for user_directives.db
   - Categories: directive mutations, execution, dependencies, implementations, relationships, helpers, associations, logging

2. ✅ **Verified User Directives Split**
   - Compared getters (45) + setters (33) = 78 total
   - Verified against `info-helpers-user-custom.txt`
   - Fixed typos and miscategorizations from source
   - Created verification document: `USER_DIRECTIVES_VERIFICATION.md`

3. ✅ **Removed Old Registry**
   - Deleted `helpers_registry_user_directives.json` (contained only 4 workflow orchestrators)
   - Split successfully into getters/setters

4. ✅ **Created Project Split Plan**
   - Analyzed 167 project helpers
   - Designed 4-file split: structure (getters/setters) + workflow (getters/setters)
   - Documented in `PROJECT_HELPERS_SPLIT_PLAN.md`

---

## Next Steps

### Immediate (Project Helpers)

1. ⏳ Create `helpers_registry_project_structure_getters.json` (38 helpers)
   - Infrastructure, files, functions, types, interactions
   - File-flow associations, type-function associations

2. ⏳ Create `helpers_registry_project_structure_setters.json` (38 helpers)
   - Reserve/finalize lifecycle for files, functions, types
   - Add/update/delete infrastructure, interactions
   - Checksum and timestamp management

3. ⏳ Create `helpers_registry_project_workflow_getters.json` (45 helpers)
   - Tasks, subtasks, sidequests
   - Themes, flows, flow-theme associations
   - Milestones, notes, items, completion paths
   - Task-file and task-flow associations

4. ⏳ Create `helpers_registry_project_workflow_setters.json` (46 helpers)
   - Add/update/delete tasks, subtasks, sidequests
   - Add/update/delete themes, flows
   - Milestone and completion path management
   - Note system for change tracking

5. ⏳ Remove old `helpers_registry_project.json` (contains only 9 helpers - incomplete)

### Consolidation & Cleanup

6. ⏳ **Remove deprecated documentation files:**
   - ❌ `docs/helpers/helper-architecture.md`
   - ❌ `docs/helpers/helper-tool-classification.md`
   - ❌ `docs/helpers/generic-tools-mcp.md` (merge into core)
   - ❌ `docs/helpers/generic-tools-project.md` (merge into core)
   - ❌ `docs/helpers/helper-functions-reference.md`
   - ❌ `docs/directives-json/directive-helper-interactions.json`
   - ❌ `docs/directives-json/helpers_parsed.json`

7. ⏳ **Add orchestrator helpers to core registry:**
   - parse_directive_file
   - validate_user_directive
   - activate_directive
   - deactivate_directive
   - (Plus 9 from generic-tools files)

---

## File Organization

### Current Structure

```
docs/helpers/registry/
├── helpers_registry_core.json                          ✅ (33 helpers)
├── helpers_registry_user_settings.json                 ✅ (40 helpers)
├── helpers_registry_user_directives_getters.json       ✅ (45 helpers)
├── helpers_registry_user_directives_setters.json       ✅ (33 helpers)
├── helpers_registry_project.json                       ❌ (to remove - incomplete)
├── helpers_registry_project_structure_getters.json     ⏳ (38 helpers)
├── helpers_registry_project_structure_setters.json     ⏳ (38 helpers)
├── helpers_registry_project_workflow_getters.json      ⏳ (45 helpers)
├── helpers_registry_project_workflow_setters.json      ⏳ (46 helpers)
├── PROJECT_HELPERS_SPLIT_PLAN.md                       ✅
└── USER_DIRECTIVES_VERIFICATION.md                     ✅
```

---

## Registry Schema

All registry JSON files follow this structure:

```json
{
  "metadata": {
    "version": "1.0.0",
    "last_updated": "YYYY-MM-DD",
    "description": "...",
    "database": "...",
    "total_helpers": N,
    "schema_version": "1.0"
  },
  "helper_schema": { /* field definitions */ },
  "database": "...",
  "file_location": "...",
  "helpers": [
    {
      "name": "function_name",
      "file_path": "src/aifp/helpers/.../file.py",
      "database": "...",
      "purpose": "...",
      "parameters": [...],
      "return_statements": [
        "AI behavioral guidance",
        "References to user_settings where appropriate",
        "Next steps in workflow"
      ],
      "error_handling": "...",
      "used_by_directives": [...],
      "is_tool": true/false,
      "is_sub_helper": true/false,
      "calls_helpers": [...],
      "category": "..."
    }
  ]
}
```

---

## Key Improvements

### Return Statements Enhancement

All helpers now include comprehensive `return_statements` that:
- ✅ Reference user_settings from user_preferences.db
- ✅ Reference directive preferences for behavior customization
- ✅ Provide next-step guidance for AI workflow
- ✅ Include validation checks and error conditions
- ✅ Describe status transitions and state changes

### Architectural Clarity

- ✅ **Database helpers** (CRUD operations) in registry files
- ✅ **Orchestrators** (high-level workflows) tracked separately
- ✅ **Tools vs Sub-helpers** clearly distinguished via `is_tool` flag
- ✅ **Getter/Setter split** for better organization (300+ helpers)
- ✅ **Domain split** for project helpers (structure vs workflow)

---

## Notes

### Fixes Applied During Consolidation

1. **User Directives Source File:**
   - Fixed typo: `get_user_directive_dependecy` → `get_user_directive_dependency`
   - Fixed miscategorization: Moved implementation getters from dependency section
   - Added missing `get_user_directive_implementation(id)`
   - Removed duplicate entries

2. **Registry Organization:**
   - Split 78 user_directives helpers into getters (45) + setters (33)
   - Split 167 project helpers into 4 files: structure/workflow × getters/setters
   - Separated workflow orchestrators from database CRUD helpers

### Workflow Orchestrators (Not Database Helpers)

These helpers coordinate multiple database operations and should be tracked separately:
- parse_directive_file
- validate_user_directive
- activate_directive
- deactivate_directive
- detect_and_init_project
- create_project_blueprint
- generate_implementation_code
- (Plus others from generic-tools files)

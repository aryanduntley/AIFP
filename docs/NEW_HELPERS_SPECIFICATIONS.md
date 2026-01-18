# New Helper Specifications

**Date**: 2026-01-17
**Status**: SUPERSEDED - SEE DIRECTIVE_CLEANUP_REVISED.md
**Purpose**: Define all new helpers needed from directive cleanup

> **⚠️ NOTE**: This document contains the original specification (14 helpers). After reviewing existing helpers, only **2 helpers are actually needed**: `project_init` and `get_all_infrastructure`. See `DIRECTIVE_CLEANUP_REVISED.md` for the corrected implementation approach.

---

## Overview

This document consolidates all new helper specifications identified from:
1. **SQL Cleanup Analysis** (SQL_CLEANUP_ANALYSIS.md)
2. **aifp.scripts Cleanup Analysis** (AIFP_SCRIPTS_CLEANUP_ANALYSIS.md)
3. **Infrastructure Goals** (INFRASTRUCTURE_GOALS.md)

**Total New Helpers Originally Identified**: 14
**Total New Helpers Actually Needed**: 2 (project_init, get_all_infrastructure)

---

## Priority 1: Infrastructure & Orchestrators (CRITICAL)

### 1. project_init (Orchestrator)
**File**: `docs/helpers/json/helpers-orchestrators.json`
**Implementation**: `src/aifp/helpers/orchestrators/orchestrators.py`
**Priority**: ⚠️ CRITICAL - Blocks initialization workflow

```json
{
  "name": "project_init",
  "file_path": "helpers/orchestrators/orchestrators.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Path to project root directory"
    },
    {
      "name": "project_name",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Project name (NULL = infer from directory)"
    },
    {
      "name": "project_purpose",
      "type": "string",
      "required": false,
      "default": null,
      "description": "Project purpose (NULL = prompt user)"
    },
    {
      "name": "goals",
      "type": "array",
      "required": false,
      "default": [],
      "description": "Array of project goals"
    }
  ],
  "purpose": "Complete project initialization orchestrator. Coordinates OOP scan, directory creation, database setup, blueprint generation, and state DB initialization. Ensures project only initialized once.",
  "error_handling": "Return detailed error if: already initialized, OOP detected, directory permissions denied, database creation failed. Clean up partial initialization on error.",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Project initialized successfully",
    "Created: .aifp-project/project.db, user_preferences.db, ProjectBlueprint.md, {source}/.state/",
    "Standard infrastructure entries created with empty values (6 entries)",
    "AI MUST now populate infrastructure values:",
    "  1. Call detect_primary_language(), detect_build_tool() for detection",
    "  2. Prompt user for confirmation or missing values",
    "  3. Update via: update_project_entry('infrastructure', id, {'value': '...'})",
    "Call get_all_infrastructure() to retrieve entries with IDs for updating"
  ],
  "target_database": "orchestrator",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "main_orchestrator",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": {},
      "description": "project_init directive calls project_init orchestrator for complete initialization"
    }
  ],
  "implementation_notes": [
    "ORCHESTRATOR - coordinates initialization, calls sub-helpers, executes direct operations",
    "Step 1: Check if already initialized (error if .aifp-project/ exists with project.db)",
    "Step 2: Call scan_for_oop_patterns() - abort if OOP detected",
    "Step 3: Gather project info (prompt user if needed), call detect_primary_language()",
    "Step 3.5: Determine source directory, call add_source_directory()",
    "Step 4: Create directories directly (os.makedirs)",
    "Step 5: Initialize project.db directly (load schema, execute, insert metadata, execute standard_infrastructure.sql)",
    "Step 6: Initialize user_preferences.db directly (load schema, execute, insert defaults)",
    "Step 7: Call generate_blueprint_from_template()",
    "Step 8: Create .gitkeep files directly",
    "Step 9.5: Call initialize_state_database()",
    "Step 10: Call validate_initialization()",
    "Step 11: Return success with guidance for AI to populate infrastructure"
  ]
}
```

---

### 2. get_all_infrastructure
**File**: `docs/helpers/json/helpers-project-1.json` or new `helpers-project-infrastructure.json`
**Implementation**: `src/aifp/helpers/project/metadata.py`
**Priority**: ⚠️ CRITICAL - Blocks infrastructure goals

```json
{
  "name": "get_all_infrastructure",
  "file_path": "helpers/project/metadata.py",
  "parameters": [],
  "purpose": "Get all infrastructure entries including standard fields (even if empty)",
  "error_handling": "Return empty array if table doesn't exist or database not initialized",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns array of all infrastructure rows: [{id, type, value, description, created_at, updated_at}, ...]",
    "Includes standard entries even if value is empty string",
    "Standard entries: source_directory, primary_language, build_tool, package_manager, test_framework, runtime_version"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "aifp_run",
      "execution_context": "session_bundle",
      "sequence_order": 5,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Include infrastructure data in session bundle when is_new_session=true"
    },
    {
      "directive_name": "aifp_status",
      "execution_context": "load_infrastructure",
      "sequence_order": 4,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Retrieve all infrastructure data for comprehensive status report"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT * FROM infrastructure ORDER BY created_at",
    "Returns ALL rows including empty values",
    "Used by aifp_run to bundle infrastructure in session context",
    "AI caches this data and only re-calls if cache lost"
  ]
}
```

---

## Priority 2: Analysis & Validation Helpers

### 3. scan_for_oop_patterns
**File**: `docs/helpers/json/helpers-project-validation.json` (new file)
**Implementation**: `src/aifp/helpers/project/validation.py`
**Priority**: HIGH - Needed for project_init

```json
{
  "name": "scan_for_oop_patterns",
  "file_path": "helpers/project/validation.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Path to project root directory"
    },
    {
      "name": "threshold",
      "type": "integer",
      "required": false,
      "default": 3,
      "description": "Number of OOP patterns required to flag as OOP project"
    }
  ],
  "purpose": "Scan codebase for OOP patterns (classes, self, this) to determine if project is FP-compatible",
  "error_handling": "Return error if directory not accessible",
  "is_tool": false,
  "is_sub_helper": true,
  "return_statements": [
    "Returns: {oop_detected: false, patterns_found: 0} if FP-compatible",
    "Returns: {oop_detected: true, patterns_found: N, affected_files: [...]} if OOP detected",
    "Threshold default: 3+ patterns across multiple files"
  ],
  "target_database": "none",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "oop_scan",
      "sequence_order": 2,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Scan for OOP patterns before initialization - abort if detected"
    }
  ],
  "implementation_notes": [
    "Scan patterns by language:",
    "  Python: ['class .*\\(.*\\):', 'self\\.', '__init__', 'def .*\\(self']",
    "  JavaScript: ['class ', 'this\\.', 'extends ', 'constructor\\(']",
    "  TypeScript: ['class ', 'this\\.', 'extends ', 'implements ', 'interface ']",
    "Threshold: 3+ patterns across multiple files = OOP project",
    "Returns: {oop_detected: bool, patterns_found: int, affected_files: [...]}"
  ]
}
```

---

### 4. detect_primary_language
**File**: `docs/helpers/json/helpers-project-analysis.json` (new file)
**Implementation**: `src/aifp/helpers/project/analysis.py`
**Priority**: HIGH - Needed for project_init and infrastructure population

```json
{
  "name": "detect_primary_language",
  "file_path": "helpers/project/analysis.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Path to project root directory"
    }
  ],
  "purpose": "Detect primary programming language by analyzing file extensions",
  "error_handling": "Return 'Unknown' if no code files found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns detected language: 'Python', 'JavaScript', 'Rust', 'Go', etc.",
    "Returns 'Unknown' if no code files or multiple languages tied"
  ],
  "target_database": "none",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "language_detection",
      "sequence_order": 3,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Detect language during init for infrastructure population"
    }
  ],
  "implementation_notes": [
    "Count file extensions: .py, .js, .ts, .rs, .go, .java, .cpp, etc.",
    "Return language with most files",
    "Return 'Unknown' if no clear majority",
    "Returns: {language: 'Python', confidence: 0.85, file_count: 42}"
  ]
}
```

---

### 5. detect_build_tool
**File**: `docs/helpers/json/helpers-project-analysis.json`
**Implementation**: `src/aifp/helpers/project/analysis.py`
**Priority**: HIGH - Needed for infrastructure population

```json
{
  "name": "detect_build_tool",
  "file_path": "helpers/project/analysis.py",
  "parameters": [
    {
      "name": "project_root",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Path to project root directory"
    }
  ],
  "purpose": "Detect build tool by checking for config files (Cargo.toml, package.json, Makefile, etc.)",
  "error_handling": "Return 'Unknown' if no build config found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns detected build tool: 'cargo', 'npm', 'make', 'maven', 'gradle', etc.",
    "Returns 'Unknown' if no build config found"
  ],
  "target_database": "none",
  "used_by_directives": [],
  "implementation_notes": [
    "Check for files:",
    "  Cargo.toml → 'cargo'",
    "  package.json → 'npm' (check scripts for yarn/pnpm)",
    "  Makefile → 'make'",
    "  pom.xml → 'maven'",
    "  build.gradle → 'gradle'",
    "  go.mod → 'go'",
    "Returns: {build_tool: 'cargo', config_file: 'Cargo.toml'}"
  ]
}
```

---

### 6. generate_blueprint_from_template
**File**: `docs/helpers/json/helpers-project-blueprint.json` (new file)
**Implementation**: `src/aifp/helpers/project/blueprint.py`
**Priority**: HIGH - Needed for project_init

```json
{
  "name": "generate_blueprint_from_template",
  "file_path": "helpers/project/blueprint.py",
  "parameters": [
    {
      "name": "aifp_dir",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Path to .aifp-project/ directory"
    },
    {
      "name": "project_name",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Project name"
    },
    {
      "name": "project_purpose",
      "type": "string",
      "required": true,
      "default": null,
      "description": "Project purpose"
    },
    {
      "name": "goals",
      "type": "array",
      "required": true,
      "default": null,
      "description": "Array of project goals"
    },
    {
      "name": "language",
      "type": "string",
      "required": false,
      "default": "Python",
      "description": "Primary programming language"
    }
  ],
  "purpose": "Generate ProjectBlueprint.md from template with project metadata",
  "error_handling": "Return error if template not found or file write fails",
  "is_tool": false,
  "is_sub_helper": true,
  "return_statements": [
    "Blueprint generated successfully at {path}",
    "Error: Template not found",
    "Error: Failed to write blueprint file"
  ],
  "target_database": "none",
  "used_by_directives": [
    {
      "directive_name": "project_init",
      "execution_context": "generate_blueprint",
      "sequence_order": 7,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Generate ProjectBlueprint.md during initialization"
    }
  ],
  "implementation_notes": [
    "Load template from: src/aifp/templates/ProjectBlueprint_template.md",
    "Replace placeholders: {{PROJECT_NAME}}, {{PURPOSE}}, {{GOALS}}, {{LANGUAGE}}",
    "Write to: {aifp_dir}/ProjectBlueprint.md",
    "Returns: {success: true, blueprint_path: '...'}",
    "Reusable for blueprint updates and regeneration"
  ]
}
```

---

## Priority 3: Task/Work Management Helpers

### 7. count_incomplete_tasks
**File**: `docs/helpers/json/helpers-project-tasks.json` (new file)
**Implementation**: `src/aifp/helpers/project/tasks.py`
**Priority**: MEDIUM - Can use generic query_project as alternative

```json
{
  "name": "count_incomplete_tasks",
  "file_path": "helpers/project/tasks.py",
  "parameters": [
    {
      "name": "milestone_id",
      "type": "integer",
      "required": true,
      "default": null,
      "description": "Milestone ID"
    }
  ],
  "purpose": "Count tasks not completed or cancelled for a milestone",
  "error_handling": "Return 0 if milestone not found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns count of incomplete tasks (status not in 'completed', 'cancelled')"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "project_milestone_complete",
      "execution_context": "check_incomplete_tasks",
      "sequence_order": 2,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Count incomplete tasks before completing milestone"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT COUNT(*) FROM tasks WHERE milestone_id = ? AND status NOT IN ('completed', 'cancelled')",
    "Alternative: Use query_project() with COUNT",
    "Returns: integer count"
  ]
}
```

---

### 8. count_incomplete_subtasks
**File**: `docs/helpers/json/helpers-project-tasks.json`
**Implementation**: `src/aifp/helpers/project/tasks.py`
**Priority**: MEDIUM - Can use generic query_project as alternative

```json
{
  "name": "count_incomplete_subtasks",
  "file_path": "helpers/project/tasks.py",
  "parameters": [
    {
      "name": "parent_task_id",
      "type": "integer",
      "required": true,
      "default": null,
      "description": "Parent task ID"
    }
  ],
  "purpose": "Count subtasks not completed or cancelled for a task",
  "error_handling": "Return 0 if task not found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns count of incomplete subtasks (status not in 'completed', 'cancelled')"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "project_task_complete",
      "execution_context": "check_incomplete_subtasks",
      "sequence_order": 2,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Count incomplete subtasks before completing task"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT COUNT(*) FROM subtasks WHERE parent_task_id = ? AND status NOT IN ('completed', 'cancelled')",
    "Alternative: Use query_project() with COUNT",
    "Returns: integer count"
  ]
}
```

---

### 9. count_incomplete_completion_paths
**File**: `docs/helpers/json/helpers-project-tasks.json`
**Implementation**: `src/aifp/helpers/project/tasks.py`
**Priority**: MEDIUM

```json
{
  "name": "count_incomplete_completion_paths",
  "file_path": "helpers/project/tasks.py",
  "parameters": [],
  "purpose": "Count completion paths not completed (no project_id parameter - one project per DB)",
  "error_handling": "Return 0 if no completion paths exist",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns count of incomplete completion paths (status != 'completed')"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "project_status",
      "execution_context": "check_completion_progress",
      "sequence_order": 3,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Count incomplete completion paths for project status"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT COUNT(*) FROM completion_path WHERE status NOT IN ('completed')",
    "Note: No project_id filter (one project per database)",
    "Returns: integer count"
  ]
}
```

---

### 10. get_next_milestone
**File**: `docs/helpers/json/helpers-project-tasks.json`
**Implementation**: `src/aifp/helpers/project/tasks.py`
**Priority**: MEDIUM - Complex JOIN query

```json
{
  "name": "get_next_milestone",
  "file_path": "helpers/project/tasks.py",
  "parameters": [],
  "purpose": "Get next pending milestone by order (complex JOIN to find milestone in correct completion path order)",
  "error_handling": "Return null if no pending milestones",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns next milestone: {id, name, description, completion_path_id, order_index}",
    "Returns null if no pending milestones found"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "project_status",
      "execution_context": "show_next_milestone",
      "sequence_order": 5,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Display next milestone to work on in status report"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT m.id, m.name, m.description, m.completion_path_id FROM milestones m JOIN completion_path cp ON m.completion_path_id = cp.id WHERE m.status = 'pending' ORDER BY cp.order_index, m.id LIMIT 1",
    "Complex query - requires dedicated helper",
    "No project_id filter (one project per database)",
    "Returns: milestone object or null"
  ]
}
```

---

### 11. get_completion_path_for_milestone
**File**: `docs/helpers/json/helpers-project-tasks.json`
**Implementation**: `src/aifp/helpers/project/tasks.py`
**Priority**: MEDIUM - Nested query

```json
{
  "name": "get_completion_path_for_milestone",
  "file_path": "helpers/project/tasks.py",
  "parameters": [
    {
      "name": "milestone_id",
      "type": "integer",
      "required": true,
      "default": null,
      "description": "Milestone ID"
    }
  ],
  "purpose": "Get completion path data for a milestone (nested query: milestone → completion_path)",
  "error_handling": "Return null if milestone not found",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns completion path: {id, status, order_index, ...}",
    "Returns null if milestone not found"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "project_milestone_complete",
      "execution_context": "check_completion_path",
      "sequence_order": 3,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Get completion path to check if all milestones in path complete"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT cp.* FROM completion_path cp JOIN milestones m ON cp.id = m.completion_path_id WHERE m.id = ?",
    "Nested approach: Get milestone, then get completion_path by completion_path_id",
    "Returns: completion_path object or null"
  ]
}
```

---

## Priority 4: Git & User Directive Helpers

### 12. get_max_branch_number
**File**: `docs/helpers/json/helpers-git.json` (new file)
**Implementation**: `src/aifp/helpers/git/branches.py`
**Priority**: LOW

```json
{
  "name": "get_max_branch_number",
  "file_path": "helpers/git/branches.py",
  "parameters": [
    {
      "name": "user_name",
      "type": "string",
      "required": true,
      "default": null,
      "description": "User name to filter branches"
    }
  ],
  "purpose": "Get highest branch number for user",
  "error_handling": "Return 0 if no branches found for user",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns max branch number for user",
    "Returns 0 if no branches exist"
  ],
  "target_database": "project",
  "used_by_directives": [
    {
      "directive_name": "git_branch_create",
      "execution_context": "determine_branch_number",
      "sequence_order": 1,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Get max branch number to increment for new branch"
    }
  ],
  "implementation_notes": [
    "SQL: SELECT MAX(branch_number) FROM work_branches WHERE user_name = ?",
    "Returns: integer (0 if none)",
    "Used to increment: new_branch_number = max + 1"
  ]
}
```

---

### 13. get_user_directives_by_status
**File**: `docs/helpers/json/helpers-user-directives.json` (new file)
**Implementation**: `src/aifp/helpers/user_directives/status.py`
**Priority**: LOW

```json
{
  "name": "get_user_directives_by_status",
  "file_path": "helpers/user_directives/status.py",
  "parameters": [],
  "purpose": "Get user directives grouped by status (active, disabled, in_progress, etc.)",
  "error_handling": "Return empty object if no user directives exist",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns directives grouped by status: {active: [...], disabled: [...], in_progress: [...]}"
  ],
  "target_database": "user_directives",
  "used_by_directives": [
    {
      "directive_name": "user_directive_status",
      "execution_context": "group_by_status",
      "sequence_order": 2,
      "is_required": true,
      "parameters_mapping": {},
      "description": "Group directives by status for status report"
    }
  ],
  "implementation_notes": [
    "Query user_directives table, GROUP BY status",
    "Returns: {active: [{...}, ...], disabled: [{...}, ...], ...}",
    "Empty array for statuses with no directives"
  ]
}
```

---

### 14. get_directive_execution_stats
**File**: `docs/helpers/json/helpers-user-directives.json`
**Implementation**: `src/aifp/helpers/user_directives/status.py`
**Priority**: LOW

```json
{
  "name": "get_directive_execution_stats",
  "file_path": "helpers/user_directives/status.py",
  "parameters": [],
  "purpose": "Get execution statistics for user directives (aggregation query)",
  "error_handling": "Return zeros if no executions logged",
  "is_tool": true,
  "is_sub_helper": false,
  "return_statements": [
    "Returns execution stats: {total_executions, success_count, error_count, avg_duration, last_execution}"
  ],
  "target_database": "user_directives",
  "used_by_directives": [
    {
      "directive_name": "user_directive_status",
      "execution_context": "show_statistics",
      "sequence_order": 3,
      "is_required": false,
      "parameters_mapping": {},
      "description": "Show execution statistics for user directives"
    }
  ],
  "implementation_notes": [
    "Query directive_executions table with aggregations",
    "Returns: {total_executions: N, success_count: N, error_count: N, avg_duration: 1.5s, last_execution: timestamp}",
    "All counts default to 0 if no executions"
  ]
}
```

---

## Files to Create/Update

### New Helper JSON Files
1. **`helpers-project-validation.json`** - scan_for_oop_patterns
2. **`helpers-project-analysis.json`** - detect_primary_language, detect_build_tool
3. **`helpers-project-blueprint.json`** - generate_blueprint_from_template
4. **`helpers-project-tasks.json`** - count helpers, get_next_milestone, get_completion_path_for_milestone
5. **`helpers-git.json`** - get_max_branch_number
6. **`helpers-user-directives.json`** - get_user_directives_by_status, get_directive_execution_stats

### Update Existing Files
1. **`helpers-orchestrators.json`** - Add project_init orchestrator
2. **`helpers-project-1.json`** - Add get_all_infrastructure

### Update Existing Helpers (aifp_run)
Update `helpers-orchestrators.json` - `aifp_run` helper:
- Add infrastructure_data to session bundle
- Call get_all_infrastructure() when is_new_session=true

---

## Implementation Order

### Phase 1: Infrastructure (Immediate)
1. ✅ Create `standard_infrastructure.sql`
2. ✅ Define `get_all_infrastructure()` helper
3. ✅ Define `project_init` orchestrator
4. ✅ Update `aifp_run` to include infrastructure in bundle

### Phase 2: Init Support (High Priority)
5. ✅ Define `scan_for_oop_patterns()` helper
6. ✅ Define `detect_primary_language()` helper
7. ✅ Define `detect_build_tool()` helper
8. ✅ Define `generate_blueprint_from_template()` helper

### Phase 3: Task Management (Medium Priority)
9. Define count helpers (tasks, subtasks, completion paths)
10. Define get_next_milestone() helper
11. Define get_completion_path_for_milestone() helper

### Phase 4: Git & User Directives (Low Priority)
12. Define get_max_branch_number() helper
13. Define user directive helpers (status, stats)

---

## Summary

**Total Helpers**: 14
- **Orchestrators**: 1 (project_init)
- **Infrastructure**: 1 (get_all_infrastructure)
- **Analysis**: 2 (detect language/build tool)
- **Validation**: 1 (scan OOP patterns)
- **Blueprint**: 1 (generate from template)
- **Task Management**: 5 (counts, next milestone, completion path)
- **Git**: 1 (max branch number)
- **User Directives**: 2 (status grouping, execution stats)

**Critical Path**: Items 1-8 (Infrastructure & Init Support)
**Next**: Items 9-11 (Task Management)
**Future**: Items 12-14 (Git & User Directives)

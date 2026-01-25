# AIFP Project State - Session Summary

**Date**: 2026-01-25
**Purpose**: Session continuity document - captures current state and key understandings

---

## Project Overview

**AIFP (AI Functional Procedural)** is a programming paradigm for AI-human collaboration combining:
- Pure functional programming (referential transparency, immutability)
- Procedural execution (explicit sequencing)
- Database-driven project management
- Directive-based AI guidance

### Four-Database Architecture

| Database | Purpose | Location |
|----------|---------|----------|
| `aifp_core.db` | Directives, helpers, flows (read-only) | MCP server install dir |
| `project.db` | Files, functions, tasks, milestones | `.aifp-project/` |
| `user_preferences.db` | User settings, directive preferences | `.aifp-project/` |
| `user_directives.db` | User automation (Use Case 2 only) | `.aifp-project/` |

### Two Use Cases
1. **Regular Software Development** - AIFP manages FP-compliant codebase
2. **Custom Directive Automation** - AIFP generates automation code from user directives

---

## Current Implementation Status

### Helper Implementation Progress

| Category | Coded | Total | Status |
|----------|-------|-------|--------|
| **Project Database** | 119 | 119 | ✅ COMPLETE |
| Orchestrators | 0 | 13 | ❌ Not started |
| Core | 0 | 38 | ❌ Not started |
| Git | 0 | 11 | ❌ Not started |
| User Preferences | 0 | 22 | ❌ Not started |
| User Directives | 0 | 20 | ❌ Not started |
| Global | 0 | 1 | ❌ Not started |

### Completed Sidequests (Jan 2026)

| Sidequest | Status | Evidence |
|-----------|--------|----------|
| SQL Query Removal (24 queries) | ✅ Done | No SQL in active directive JSONs |
| aifp.scripts Cleanup (4 refs) | ✅ Done | Only in `/backups/` |
| standard_infrastructure.sql | ✅ Created | `src/aifp/database/initialization/` |
| Infrastructure helpers | ✅ Coded | `metadata.py` - get/update for project_root, source_directory, get_all_infrastructure |
| aifp_init JSON definition | ✅ Done | `helpers-orchestrators.json` |
| aifp_run infrastructure bundling | ✅ Documented | implementation_notes include infrastructure_data |

### Key Files Created/Updated

```
src/aifp/database/initialization/standard_infrastructure.sql  # 8 entries
src/aifp/helpers/project/metadata.py                          # Infrastructure helpers
docs/helpers/json/helpers-orchestrators.json                  # aifp_init, aifp_run definitions
src/aifp/templates/state_db/                                  # Mutable state DB templates
```

---

## Helper JSON Field Definitions

**CRITICAL: Understanding these fields correctly prevents wasted effort**

### return_statements
- **Purpose**: Forward-thinking guidance for AI AFTER helper executes
- **Contains**: Next steps, suggestions, what AI should do with the results
- **NOT for**: Defining return value structure
- **Example**: "AI must now detect and populate infrastructure values"

### implementation_notes
- **Purpose**: Reference for CODING the helper function
- **Contains**:
  - Step-by-step implementation logic
  - Return value structure (RETURN STRUCTURE: {...})
  - Error handling details
  - Internal function calls
  - Database operations
- **Used when**: Actually writing the Python code

### Other Fields
- `parameters` - Function inputs with types and defaults
- `purpose` - One-line description of what helper does
- `error_handling` - Brief error behavior description
- `is_tool` - Whether AI can call directly (true) or internal only (false)
- `is_sub_helper` - Called by other helpers, not directly by AI
- `target_database` - Which DB this helper operates on
- `used_by_directives` - Which directives reference this helper

---

## Helper Functions vs Internal Code

**Helper Functions** = AI tools for REPEATED operations
- Save AI from thinking about DB details on every call
- CRUD operations, queries, updates
- Called many times throughout project lifecycle
- Documented in helpers JSON files

**Internal Code** = One-time operations
- Part of orchestrator/function implementation
- NOT exposed as separate helpers
- Example: State DB creation (only during init)

### State Database Example
- **What**: FP-compliant mutable global state (`{source_dir}/.state/`)
- **Contains**: `runtime.db` (key-value store), `README.md`, `state_operations.{ext}` (CRUD reference)
- **Created**: Once during init, AFTER source_directory is populated
- **Code location**: Internal to `aifp_init` module (NOT a helper)
- **Templates**: `src/aifp/templates/state_db/`

---

## Key Architectural Decisions

### 1. No Hardcoded Helper Names in Directives
- Helper names change frequently
- Directives use `"use_helper": "description of action"` pattern
- AI queries helper_functions table to find current helpers

### 2. Two-Phase Initialization
- **Phase 1** (aifp_init): Mechanical setup - directories, DBs, templates
- **Phase 2** (AI): Intelligent population - detect language, build tool, populate infrastructure

### 3. Infrastructure Pre-population
- 8 standard entries created with empty values during init
- AI detects and populates values post-init
- Entries: project_root, source_directory, primary_language, build_tool, package_manager, test_framework, runtime_version, main_branch

### 4. Git Tables Kept (Not Redundant)
- Git tracks: What code IS and WAS (version control)
- Database tracks: WHO, WHY, STATUS, FP INTELLIGENCE (collaboration metadata)
- `work_branches` and `merge_history` tables provide structured query access

---

## aifp_init Orchestrator Summary

**Purpose**: Phase 1 mechanical setup

**Steps**:
1. Check if already initialized (error if exists)
2. Create directories: `.aifp-project/`, `.aifp-project/backups/`
3. Copy ProjectBlueprint template
4. Initialize project.db (schema + standard_infrastructure.sql + update_project_root)
5. Initialize user_preferences.db (schema + defaults)
6. Create .gitkeep files
7. Validate (call validate_initialization)
8. Return success

**State DB**: Created later (code in aifp_init module, called after source_directory populated)

**Error Cleanup**: Delete entire `.aifp-project/` on failure

**Return Structure**:
```json
{
  "success": true,
  "project_root": "/path/to/project",
  "aifp_dir": "/path/to/project/.aifp-project",
  "files_created": [".aifp-project/", "project.db", "user_preferences.db", "ProjectBlueprint.md"],
  "tables_created": {"project_db": [...], "user_prefs_db": [...]},
  "infrastructure_entries": 8,
  "next_phase": "AI populates infrastructure and blueprint"
}
```

---

## aifp_run Orchestrator Summary

**Purpose**: Main entry point, session bundle provider

**Parameters**: `is_new_session` (bool, default false)

**Returns when is_new_session=true**:
```json
{
  "status": "from aifp_status()",
  "user_settings": "from get_user_settings()",
  "fp_directive_index": "FP directives by category",
  "all_directive_names": ["all", "directive", "names"],
  "infrastructure_data": "from get_all_infrastructure()",
  "guidance": "next steps suggestions"
}
```

**Returns when is_new_session=false**:
```json
{
  "guidance": "lightweight guidance",
  "common_starting_points": []
}
```

**Token Budget**: ~15.5-20.5k tokens for full bundle

---

## File Locations Reference

### Source Code
- Helpers: `src/aifp/helpers/`
- Schemas: `src/aifp/database/schemas/`
- Init SQL: `src/aifp/database/initialization/`
- Templates: `src/aifp/templates/`

### Documentation (Dev)
- Helper JSON definitions: `docs/helpers/json/`
- Directive JSON: `docs/directives-json/`
- Directive MD: `src/aifp/reference/directives/`
- Implementation plans: `docs/`

### Key Documents
- `docs/HELPER_IMPLEMENTATION_PLAN.md` - Master helper coding plan
- `docs/CLEANUP_PROGRESS.md` - Directive cleanup status
- `docs/INFRASTRUCTURE_GOALS.md` - Infrastructure requirements

---

## Next Steps

1. **Continue with HELPER_IMPLEMENTATION_PLAN.md**
   - Orchestrators phase (13 helpers)
   - Core phase (38 helpers)
   - Git, User Preferences, User Directives phases

2. **When coding helpers**:
   - Read implementation_notes for logic
   - Return structure is in implementation_notes (not return_statements)
   - return_statements guide AI behavior AFTER execution

3. **aifp_init coding**:
   - State DB creation is internal (not a helper)
   - Templates at `src/aifp/templates/state_db/`
   - Error cleanup: delete entire `.aifp-project/`

---

## Session Notes

- `notes.txt` is user's personal file - do not read or modify
- Everything above `src/aifp/` is dev/documentation
- Project helpers are COMPLETE (119/119)
- Ready to begin coding non-project helpers

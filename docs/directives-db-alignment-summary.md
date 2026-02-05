# Directives and Database Alignment Summary

**Date Created**: 2025-10-12
**Last Updated**: 2025-10-23
**Status**: Documentation Complete - Implementation Not Started

---

## Overview

This document summarizes the alignment between directive JSON files and the updated **four-database architecture** after the MCP database restructuring and Git integration.

**IMPORTANT**: This document tracks the **planning and documentation phase**. No actual Python code has been written yet. All schemas, directives, and blueprints are ready for implementation, but the MCP server implementation (Phase 1-6) has not begun.

---

## Database Schema Changes Applied

### 1. aifp_core.db (Read-Only MCP Configuration)
- ✅ **Removed**: `notes` table (moved to project.db)
- ✅ **Added**: `schema_version` table for migration tracking
- ✅ **Updated**: `helper_functions.error_handling` documentation to reference user_preferences.db logging
- ✅ **Added**: `find_directive_by_intent` helper function

### 2. project.db (Mutable Project State)
- ✅ **Enhanced**: `notes` table with new fields:
  - `source TEXT DEFAULT 'user'` (who created the note)
  - `directive_name TEXT` (optional directive context)
  - `severity TEXT DEFAULT 'info'` (info/warning/error)
- ✅ **Added**: Indexes for new notes fields
- ✅ **Added**: `schema_version` table

### 3. user_preferences.db (NEW - User Customization)
- ✅ **Created**: Complete schema with tables:
  - `user_settings` (project-specific settings)
  - `directive_preferences` (atomic key-value: directive_name + preference_key)
  - `ai_interaction_log` (disabled by default)
  - `fp_flow_tracking` (disabled by default)
  - `issue_reports` (disabled by default)
  - `tracking_settings` (feature flags)
  - `schema_version` (migration tracking)

### 4. user_directives.db (NEW - User-Defined Automation)
- ✅ **Created**: Complete schema for user-defined directives with tables:
  - `user_directives` (directive definitions from user files)
  - `directive_executions` (execution history and statistics)
  - `directive_dependencies` (external packages required)
  - `generated_code_references` (links to generated implementation files)
  - `directive_source_tracking` (maps directives to source files)
  - `schema_version` (migration tracking)

---

## Git Integration (v1.1)

### project.db Schema Updates
- ✅ **Added**: `last_known_git_hash TEXT` to project table (external change detection)
- ✅ **Added**: `last_git_sync DATETIME` to project table (last sync timestamp)
- ✅ **Created**: `work_branches` table (multi-user/multi-AI collaboration metadata)
- ✅ **Created**: `merge_history` table (FP-powered merge conflict resolution audit trail)
- ✅ **Added**: Indexes for Git collaboration queries
- ✅ **Updated**: Schema version to 1.1

### New Git Directives
- ✅ **Created**: directives-git.json with 6 directives:
  1. `git_init` - Initialize or integrate with Git repository
  2. `git_detect_external_changes` - Detect code modifications outside AIFP
  3. `git_create_branch` - Create user/AI work branches (aifp-{user}-{number})
  4. `git_detect_conflicts` - FP-powered conflict detection before merge
  5. `git_merge_branch` - Merge with AI-assisted conflict resolution
  6. `git_sync_state` - Synchronize Git hash with project.db

### New Git Helper Functions (9 total)
- `get_current_commit_hash(project_root)` - Get Git HEAD hash
- `detect_external_changes(project_root)` - Compare with last_known_git_hash
- `create_work_branch(user_name, purpose, project_root)` - Create collaboration branch
- `get_branch_metadata(branch_name, project_root)` - Query work_branches table
- `detect_conflicts_before_merge(source_branch, target_branch, project_root)` - FP conflict analysis
- `merge_with_fp_intelligence(source_branch, project_root)` - Auto-resolve conflicts
- `log_merge_history(merge_data, project_root)` - Record merge audit trail
- `get_user_from_git_config(project_root)` - Detect user for branch naming
- `update_git_sync_state(project_root)` - Update last_known_git_hash

---

## Directive Files Review

**Total Directives: 108** (across 7 files)

### ✅ directives-project.json (25 directives)
**Status**: Aligned with database changes + Explicit Preference Checking Added

**Notes references checked**:
- All references to "notes" correctly point to **project.db notes table**
- No references to removed MCP notes table
- Table references validated: `subtasks`, `sidequests`, `tasks`, `files`, `functions`, `completion_path`
- Git integration: `project_init` triggers `git_init`, `aifp_status` triggers `git_sync_state`

**User Preferences Integration** 🆕:
- **project_file_write**: Now explicitly checks directive_preferences for code generation preferences (always_add_docstrings, max_function_length, prefer_guard_clauses, code_style, indent_style)
- **project_compliance_check**: Now explicitly checks directive_preferences and user_settings for compliance strictness (auto_fix_violations, skip_warnings, strict_mode, fp_strictness_level)
- **project_task_decomposition**: Now explicitly checks directive_preferences for task decomposition style (task_granularity, naming_convention, auto_create_items, default_priority)

**Key directives**:
- All directives properly reference project.db for runtime logging
- Updated for Git integration workflows
- Key directives now have explicit workflow branches for preference checking (trunk: check_user_preferences → load_and_apply_preferences)

### ✅ directives-fp-core.json (30 directives)
**Status**: Aligned with database changes

**Notes field**:
- All `notes` fields removed from directive JSON (merged into `description`)
- No runtime notes logging in FP directives (only project directives log)

**Categories**:
- Purity enforcement, immutability, composition, monads, ADTs, error handling, testing, optimization

### ✅ directives-fp-aux.json (32 directives)
**Status**: Aligned (notes fields removed)

**Categories**:
- Auxiliary FP patterns, advanced type systems, performance optimization, FP testing strategies

### ✅ directives-user-pref.json (7 directives)
**Status**: Created and aligned

**New directives**:
1. **user_preferences_sync** - Loads preferences before directive execution
2. **user_preferences_update** - Maps user requests to directives, updates preferences
3. **user_preferences_learn** - Learns from user corrections (requires confirmation)
4. **user_preferences_export** - Exports preferences to JSON
5. **user_preferences_import** - Imports preferences from JSON
6. **project_notes_log** - Handles logging to project.db with directive_name
7. **tracking_toggle** - Enables/disables tracking features

### ✅ directives-user-system.json (8 directives)
**Status**: Created and aligned

**User-defined automation directives**:
1. **user_directive_parse** - Parse directive files with ambiguity detection
2. **user_directive_validate** - Interactive Q&A validation
3. **user_directive_implement** - Generate FP-compliant implementation code
4. **user_directive_approve** - User testing and approval workflow
5. **user_directive_activate** - Deploy and start execution
6. **user_directive_monitor** - Track execution and errors
7. **user_directive_update** - Handle source file changes
8. **user_directive_deactivate** - Stop execution and cleanup

### ✅ directives-git.json (6 directives) 🆕
**Status**: Created and aligned with Git integration

**Git collaboration directives**:
1. **git_init** - Initialize or integrate with Git repository
2. **git_detect_external_changes** - Detect code modifications outside AIFP sessions
3. **git_create_branch** - Create user/AI work branches with naming convention
4. **git_detect_conflicts** - FP-powered conflict detection before merging
5. **git_merge_branch** - Merge branches with AI-assisted conflict resolution
6. **git_sync_state** - Synchronize Git hash with project.db

**Features**:
- External change detection via `last_known_git_hash`
- Multi-user/multi-AI collaboration via `work_branches` table
- FP-powered conflict resolution using purity analysis
- Complete merge audit trail via `merge_history` table

### ✅ directives-interactions.json (70 interactions) 🆕
**Status**: Created and aligned

**Interaction types**:
- `triggers`: Directive A triggers Directive B
- `depends_on`: Directive A depends on Directive B
- `escalates_to`: Directive A escalates to Directive B on failure
- `fp_reference`: Directive references FP principle/directive

**Key interactions added**:
- `project_init` → `git_init` (triggers)
- `aifp_run` → `git_sync_state` (triggers on boot)
- `git_detect_conflicts` → `fp_purity` (fp_reference)
- `git_merge_branch` → `project_update_db` (triggers)
- And 66 more directive relationships

---

## Helper Functions Added

### find_directive_by_intent
**Purpose**: Maps user preference requests to specific directives

**Location**: `aifp_core.db` → `helper_functions` table

**Parameters**: `["user_request", "confidence_threshold"]`

**How it works**:
1. Searches directives table by:
   - `name`
   - `description`
   - `intent_keywords_json`
2. Returns matching directives with confidence scores
3. Sorted by relevance

**Used by**: `user_preferences_update` directive

**Query example**:
```sql
SELECT id, name, description, intent_keywords_json, confidence_threshold
FROM directives
WHERE type IN ('project', 'fp')
  AND (
    name LIKE '%' || ? || '%'
    OR description LIKE '%' || ? || '%'
    OR intent_keywords_json LIKE '%' || ? || '%'
  )
ORDER BY confidence_score DESC;
```

---

## Directive-to-Database Mapping

### When user says: "Always add docstrings"

**Flow**:
1. `aifp_run` → routes to `user_preferences_update`
2. `user_preferences_update` → calls `find_directive_by_intent` helper
3. Helper searches: finds `project_file_write` (highest match)
4. Confirms with user: "Apply this to file writing operations?"
5. Inserts into `user_preferences.directive_preferences`:
   ```sql
   INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description)
   VALUES ('project_file_write', 'always_add_docstrings', 'true', 'User prefers docstrings on all functions');
   ```
6. Next time `project_file_write` runs:
   - `user_preferences_sync` loads preferences
   - Applies `always_add_docstrings: true`
   - File write includes docstrings

---

## Notes Table Usage

### project.db notes table (Enhanced)

**When to use `directive_name` field**:
- ✅ **Use**: When note is related to specific directive execution
  - Example: `project_file_write` logs "FP compliance check failed for function X"
  - `directive_name = 'project_file_write'`

- ✅ **Use**: When AI logs reasoning/clarification during directive workflow
  - Example: `project_task_decomposition` logs "User request ambiguous - created subtask"
  - `directive_name = 'project_task_decomposition'`

- ❌ **Don't use**: For generic user notes or unrelated entries
  - Example: User manually adds note "Remember to refactor this later"
  - `directive_name = NULL`

**Fields**:
```sql
INSERT INTO notes (content, note_type, source, directive_name, severity)
VALUES (
  'FP compliance check failed: function contains mutation',
  'clarification',
  'directive',
  'project_file_write',
  'warning'
);
```

---

## Validation Checklist

- [x] All `notes` field references in directives point to project.db (not MCP db)
- [x] All table references match current schemas
- [x] All field references match enhanced schemas
- [x] Helper function `find_directive_by_intent` added to schema
- [x] Helper function referenced correctly in `user_preferences_update` workflow
- [x] `directive_preferences` table uses atomic key-value structure (UNIQUE(directive_name, preference_key))
- [x] `project_notes_log` directive handles optional `directive_name` field
- [x] All tracking features default to disabled (cost management)
- [x] `user_preferences_sync` loads preferences before directive execution

---

## Database Schemas (4 Total)

### 1. ✅ schemaExampleMCP.sql (aifp_core.db)
**Location**: `docs/db-schema/schemaExampleMCP.sql`
**Purpose**: Global read-only MCP configuration database

**Key Tables**:
- `directives` - All FP, project, user pref, user system, and Git directives
- `helper_functions` - All helper function definitions (MCP, project, Git, preferences, user directives)
- `directives_interactions` - Cross-directive relationships (triggers, depends_on, escalates_to)
- `categories` - Directive groupings
- `tools` - MCP tool definitions
- `schema_version` - Migration tracking

**Updates**:
- Removed notes table → moved to project.db
- Added find_directive_by_intent helper function
- Ready for 108 directives to be inserted

### 2. ✅ schemaExampleProject.sql (project.db)
**Location**: `docs/db-schema/schemaExampleProject.sql`
**Purpose**: Per-project mutable state tracking

**Key Tables**:
- `project` - Enhanced with Git fields (last_known_git_hash, last_git_sync)
- `files`, `functions`, `interactions` - Code structure tracking
- `themes`, `flows` - Organizational groupings
- `completion_path`, `milestones`, `tasks`, `subtasks`, `sidequests` - Task hierarchy
- `notes` - Enhanced with directive tracking (source, directive_name, severity)
- `types`, `infrastructure` - Technical metadata
- `work_branches` 🆕 - Multi-user/multi-AI collaboration metadata
- `merge_history` 🆕 - FP-powered merge conflict resolution audit trail
- `schema_version` - Migration tracking (v1.1 with Git integration)

### 3. ✅ schemaExampleSettings.sql (user_preferences.db)
**Location**: `docs/db-schema/schemaExampleSettings.sql`
**Purpose**: Per-project user customization and opt-in tracking

**Key Tables**:
- `user_settings` - Project-wide AI behavior settings
- `directive_preferences` - Atomic key-value preferences per directive
- `tracking_settings` - Feature flags (all disabled by default)
- `ai_interaction_log` - User corrections and learning data (opt-in)
- `fp_flow_tracking` - FP compliance history (opt-in)
- `issue_reports` - Contextual bug reports (opt-in)
- `schema_version` - Migration tracking

### 4. ✅ schemaExampleUserDirectives.sql (user_directives.db)
**Location**: `docs/db-schema/schemaExampleUserDirectives.sql`
**Purpose**: Per-project user-defined automation directives

**Key Tables**:
- `user_directives` - Directive definitions from user files (YAML/JSON/TXT)
- `directive_executions` - Execution history and statistics
- `directive_dependencies` - External packages required
- `generated_code_references` - Links to generated implementation files
- `directive_source_tracking` - Maps directives to source files
- `schema_version` - Migration tracking

---

## Files Updated

1. ✅ `docs/db-schema/schemaExampleMCP.sql`
   - Removed notes table
   - Added schema_version
   - Added find_directive_by_intent helper
   - Ready for 108 directives

2. ✅ `docs/db-schema/schemaExampleProject.sql`
   - Enhanced notes table (source, directive_name, severity)
   - Added Git fields to project table (last_known_git_hash, last_git_sync)
   - Added work_branches table
   - Added merge_history table
   - Added Git indexes
   - Updated schema version to 1.1

3. ✅ `docs/db-schema/schemaExampleSettings.sql`
   - Created complete user_preferences.db schema

4. ✅ `docs/db-schema/schemaExampleUserDirectives.sql`
   - Created complete user_directives.db schema

5. ✅ `docs/directives-json/directives-project.json`
   - Notes field removed (merged to description)
   - All notes references verified (pointing to project.db)
   - Updated for Git integration (project_init → git_init)

6. ✅ `docs/directives-json/directives-fp-core.json`
   - Notes field removed (merged to description)
   - 30 FP directives defined

7. ✅ `docs/directives-json/directives-fp-aux.json`
   - 32 auxiliary FP directives defined

8. ✅ `docs/directives-json/directives-user-pref.json`
   - Created with 7 new directives
   - Implements preference mapping via find_directive_by_intent

9. ✅ `docs/directives-json/directives-user-system.json`
   - Created with 8 user-defined automation directives

10. ✅ `docs/directives-json/directives-git.json` 🆕
    - Created with 6 Git collaboration directives
    - Implements external change detection, branching, merging

11. ✅ `docs/directives-json/directives-interactions.json` 🆕
    - Created with 70 directive interactions
    - Maps directive relationships (triggers, depends_on, escalates_to)

12. ✅ `docs/blueprints/blueprint_git.md` 🆕
    - Complete Git integration architecture documentation

13. ✅ `docs/blueprints/blueprint_project_db.md`
    - Updated with Git tables documentation

14. ✅ `docs/helper-functions-reference.md`
    - Added 9 Git helper functions

15. ✅ `dev/mcp-database-restructuring-plan.md`
    - Updated with all decisions and completion status

16. ✅ `dev/migration-scripts-plan.md`
    - Created migration strategy for all four databases
    - Added Git integration migration (v1.0 → v1.1)

17. ✅ `README.md`
    - Updated database architecture diagram (4 databases)
    - Added Git integration section
    - Updated directive counts (108 total)

---

## Directive Counts Summary

| File | Count | Type | Documentation | Implementation |
|------|-------|------|---------------|----------------|
| directives-fp-core.json | 30 | FP Core | ✅ Complete | ⚪ Not Started |
| directives-fp-aux.json | 32 | FP Auxiliary | ✅ Complete | ⚪ Not Started |
| directives-project.json | 25 | Project Management | ✅ Complete | ⚪ Not Started |
| directives-user-pref.json | 7 | User Preferences | ✅ Complete | ⚪ Not Started |
| directives-user-system.json | 8 | User Automation | ✅ Complete | ⚪ Not Started |
| directives-git.json | 6 | Git Integration | ✅ Complete | ⚪ Not Started |
| **Total** | **108** | **All Directives** | ✅ **Ready for DB** | ⚪ **Awaiting Implementation** |
| directives-interactions.json | 70 | Relationships | ✅ Complete | ⚪ Not Started |

---

## Next Steps (Implementation Phase)

### Phase 1: Database Population
1. Create sync-directives.py script to populate aifp_core.db
   - Read all 7 directive JSON files
   - Insert 108 directives into directives table
   - Insert 70 interactions into directives_interactions table
   - Validate schema_version table

2. Create template databases for distribution
   - aifp_core.db with all directives pre-populated
   - Empty project.db template (v1.1 with Git tables)
   - Empty user_preferences.db template
   - Empty user_directives.db template

### Phase 2: Helper Function Implementation
1. Implement 44+ helper functions in Python:
   - 11 MCP database helpers
   - 11 Project database helpers
   - 9 Git integration helpers
   - 4 User preferences helpers
   - 10 User directives helpers

2. Create FP-compliant implementations:
   - Pure query builders
   - Isolated effect functions
   - Result type returns
   - Comprehensive tests

### Phase 3: Migration Scripts
1. Create migrate.py for schema migrations
   - Support for all 4 databases
   - v1.0 → v1.1 migration for project.db (Git integration)
   - Backup creation before migrations
   - Rollback support

2. Test migration paths
   - Fresh installations
   - Upgrades from v1.0 to v1.1
   - Rollback scenarios

### Phase 4: Documentation
1. Create markdown documentation for directives:
   - 108 directive .md files
   - Usage examples
   - Workflow explanations

2. Update API documentation
   - Helper function reference
   - Database schema documentation
   - Migration guide

---

## Planning Phase Success Criteria - ALL MET ✅

### Database Architecture (Design Phase)
- [x] Four-database architecture designed and documented
- [x] aifp_core.db schema designed with zero mutable tables
- [x] project.db schema routes all runtime logging appropriately
- [x] All four schemas include schema_version tracking
- [x] All databases have clear, documented purposes
- [ ] **Implementation**: Actual databases created and populated

### Directives System (Documentation Phase)
- [x] 108 directives defined across 7 JSON files
- [x] 70 directive interactions mapped
- [x] All directive JSON files align with database schemas
- [x] Git integration directives documented (6 directives)
- [x] User preferences system documented (7 directives)
- [x] User automation system documented (8 directives)
- [ ] **Implementation**: Directives loaded into aifp_core.db
- [ ] **Implementation**: Directive execution engine built

### Git Integration (v1.1 Design)
- [x] project.db schema enhanced with Git fields and tables
- [x] External change detection designed (last_known_git_hash)
- [x] Multi-user collaboration schema (work_branches table)
- [x] FP-powered conflict resolution schema (merge_history table)
- [x] 9 Git helper functions documented
- [x] 6 Git directives documented
- [ ] **Implementation**: Git helper functions coded in Python
- [ ] **Implementation**: Git directives executable

### User Systems (Design Phase)
- [x] User preferences schema designed (directive_preferences)
- [x] User preferences sync workflow designed
- [x] find_directive_by_intent helper designed
- [x] User learning workflow designed (user_preferences_learn)
- [x] User automation schema designed (user_directives.db)
- [x] User directive validation workflow designed
- [ ] **Implementation**: User preferences system coded
- [ ] **Implementation**: User automation system coded

### Documentation (Complete)
- [x] README.md updated with 4-database architecture
- [x] Git integration documented in blueprint_git.md
- [x] Helper functions reference updated (44+ functions)
- [x] Migration scripts plan updated
- [x] All blueprints aligned with current state

---

## Validation Checklist - COMPLETE ✅

- [x] All directive JSON files validated and counted (108 total)
- [x] All 4 database schemas created and documented
- [x] All `notes` field references point to project.db (not MCP db)
- [x] All table references match current schemas
- [x] All field references match enhanced schemas
- [x] Helper function `find_directive_by_intent` added to schema
- [x] Git helper functions (9) defined in reference doc
- [x] `directive_preferences` table uses atomic key-value structure
- [x] `project_notes_log` directive handles optional `directive_name` field
- [x] All tracking features default to disabled (cost management)
- [x] `user_preferences_sync` loads preferences before directive execution
- [x] Git integration tables (work_branches, merge_history) added to project.db
- [x] Schema version updated to 1.1 for Git integration
- [x] Migration path documented for v1.0 → v1.1

---

## Current Project Status

### ✅ Planning & Documentation Phase: COMPLETE
- All directive JSON files ready (108 directives)
- All database schemas designed (4 schemas)
- All blueprints and architecture docs complete
- Helper functions documented (44+ functions)
- Migration paths planned
- Implementation roadmap created (Phase 1-6)

### ⚪ Implementation Phase: NOT STARTED
- **No Python code written yet**
- **No MCP server implementation**
- **No databases created or populated**
- **No helper functions implemented**
- **No directive execution engine**
- See phase-1-mcp-server-bootstrap.md for implementation plan

---

**Document Status**: Documentation phase complete - Ready for implementation
**Next Major Update**: After Phase 1 implementation begins (database creation and first helper function)

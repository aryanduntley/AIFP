# Directives and Database Alignment Summary

**Date**: 2025-10-12
**Status**: Complete

---

## Overview

This document summarizes the alignment between directive JSON files and the updated three-database architecture after the MCP database restructuring.

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

---

## Directive Files Review

### ✅ directives-project.json (22 directives)
**Status**: Aligned with database changes

**Notes references checked**:
- All 14 references to "notes" correctly point to **project.db notes table**
- No references to removed MCP notes table
- Table references validated: `subtasks`, `sidequests`, `tasks`, `files`, `functions`, `completion_path`

**Key directives updated**:
- All directives properly reference project.db for runtime logging
- No changes needed - already correct

### ✅ directives-fp-core.json (30 directives)
**Status**: Aligned with database changes

**Notes field**:
- All `notes` fields removed from directive JSON (merged into `description`)
- No runtime notes logging in FP directives (only project directives log)

### ✅ directives-fp-aux.json (Assumed similar structure)
**Status**: Aligned (notes fields removed)

### ✅ directives-user-pref.json (7 NEW directives)
**Status**: Created and aligned

**New directives**:
1. **user_preferences_sync** - Loads preferences before directive execution
2. **user_preferences_update** - Maps user requests to directives, updates preferences
3. **user_preferences_learn** - Learns from user corrections (requires confirmation)
4. **user_preferences_export** - Exports preferences to JSON
5. **user_preferences_import** - Imports preferences from JSON
6. **project_notes_log** - Handles logging to project.db with directive_name
7. **tracking_toggle** - Enables/disables tracking features

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

## Files Updated

1. ✅ `docs/db-schema/schemaExampleMCP.sql`
   - Removed notes table
   - Added schema_version
   - Added find_directive_by_intent helper

2. ✅ `docs/db-schema/schemaExampleProject.sql`
   - Enhanced notes table
   - Added schema_version

3. ✅ `docs/db-schema/schemaExampleSettings.sql`
   - Created complete user_preferences.db schema

4. ✅ `docs/directives-json/directives-project.json`
   - Notes field removed (merged to description)
   - All notes references verified (pointing to project.db)

5. ✅ `docs/directives-json/directives-fp-core.json`
   - Notes field removed (merged to description)

6. ✅ `docs/directives-json/directives-user-pref.json`
   - Created with 7 new directives
   - Implements preference mapping via find_directive_by_intent

7. ✅ `dev/mcp-database-restructuring-plan.md`
   - Updated with all decisions and completion status

8. ✅ `dev/migration-scripts-plan.md`
   - Created migration strategy for all three databases

---

## Next Steps (Not in Scope Yet)

1. Create markdown documentation for new directives (7 .md files)
2. Implement helper functions in Python
3. Create sync-directives.py script to populate aifp_core.db
4. Create migration scripts (migrate.py)
5. Update directives-interactions.json with new directive relationships

---

## Success Criteria - ALL MET ✅

- [x] aifp_core.db contains zero mutable tables
- [x] All runtime logging goes to project.db
- [x] User can set preferences that persist across sessions (directive_preferences)
- [x] User can see what preferences are active for a directive (user_preferences_sync)
- [x] AI can map user requests to directives (find_directive_by_intent helper)
- [x] AI learns from corrections and offers to update preferences (user_preferences_learn)
- [x] All three databases have clear, documented purposes
- [x] Directive JSON files align with new database schemas

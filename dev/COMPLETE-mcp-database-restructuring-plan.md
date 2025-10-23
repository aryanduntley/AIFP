# MCP Database Restructuring Plan

**Purpose**: Restructure database architecture to properly separate immutable MCP configuration from mutable project state and user preferences.

**Date Created**: 2025-10-12
**Date Completed**: 2025-10-23 (with Git integration)
**Status**: Documentation & Planning Complete - Implementation Not Started

---

## Overview

The current design has architectural conflicts around the notes table and runtime state management. This plan establishes a clear **four-database architecture**:

1. **aifp_core.db** - Read-only MCP configuration (shipped with MCP)
2. **project.db** - Mutable project state (in `.aifp-project/`) - **v1.1 with Git integration**
3. **user_preferences.db** - User/project-specific AI behavior customization (in `.aifp-project/`)
4. **user_directives.db** - User-defined automation directives (in `.aifp-project/`) **NEW**

---

## Current Issues

### Issue 1: Notes Table in Read-Only Database
**Problem**: aifp_core.db contains a notes table, but the database is read-only when shipped as MCP software.

**Evidence**:
- Workflows reference `"log_note": true` (schemaExampleMCP.sql:107, 132, 154)
- Helper functions say "Log to notes table" (line 186)
- But database is marked "immutable once deployed" (line 4)

**Impact**: Runtime logging directives cannot execute as designed.

### Issue 2: No User Preference Tracking
**Problem**: No mechanism to persist user-specific AI behavior preferences across sessions.

**Use Cases**:
- User prefers certain coding patterns (e.g., "always use explicit returns")
- User wants specific FP strictness levels per project
- User has project-specific style guides
- User wants to suppress certain directive warnings

---

## Proposed Architecture

### Database 1: aifp_core.db (Read-Only MCP Configuration)

**Location**: Shipped with MCP installation
**Mutability**: Immutable in production; only updated during MCP version releases
**Purpose**: Static directive definitions and MCP configuration

**Tables to KEEP**:
- [x] `directives` - Directive definitions
- [x] `categories` - Category definitions
- [x] `directive_categories` - Directive-category linking
- [x] `directives_interactions` - Directive relationships
- [x] `helper_functions` - Helper function registry
- [x] `tools` - MCP tool mappings

**Tables to REMOVE**:
- [ ] `notes` - Move logging to project.db

**Actions**:
1. Remove notes table from schema
2. Update all workflow JSON that references notes:
   - Change `"log_note": true` → `"log_to_project_notes": true`
   - Change `"log_to_notes_and_prompt_user"` → `"log_to_project_and_prompt_user"`
   - Change `"update_notes"` → `"update_project_notes"`
3. Update helper function error_handling to reference project.db notes

---

### Database 2: project.db (Mutable Project State)

**Location**: `.aifp-project/project.db`
**Mutability**: Fully mutable; updated by MCP during project work
**Purpose**: Track project-specific files, tasks, and runtime state

**Tables (KEEP EXISTING)**:
- [x] `project` - Project metadata
- [x] `files` - File inventory
- [x] `functions` - Function registry
- [x] `types` - ADT definitions
- [x] `interactions` - Function dependencies
- [x] `themes` - Thematic groupings
- [x] `flows` - Procedural flows
- [x] `flow_themes` - Theme-flow linking
- [x] `file_flows` - File-flow linking
- [x] `infrastructure` - Setup tracking
- [x] `completion_path` - Roadmap structure
- [x] `milestones` - Milestone tracking
- [x] `tasks` - Task tracking
- [x] `subtasks` - Subtask breakdown
- [x] `sidequests` - Priority deviations
- [x] `items` - Lowest-level actions
- [x] `notes` - Runtime clarifications and logs

**Notes Table Enhancement**:
Add fields to clarify source:
```sql
ALTER TABLE notes ADD COLUMN source TEXT DEFAULT 'user';  -- 'user', 'ai', 'directive'
ALTER TABLE notes ADD COLUMN directive_name TEXT;         -- e.g., 'project_file_write'
ALTER TABLE notes ADD COLUMN severity TEXT DEFAULT 'info'; -- 'info', 'warning', 'error'
```

---

### Database 3: user_preferences.db (NEW - User Behavior Customization)

**Location**: `.aifp-project/user_preferences.db`
**Mutability**: Updated by user or AI through preference directives
**Purpose**: Store user-specific AI behavior preferences and customizations

#### Table: user_settings
```sql
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,           -- e.g., 'fp_strictness_level', 'prefer_explicit_returns'
    setting_value TEXT NOT NULL,                -- JSON value
    description TEXT,
    scope TEXT DEFAULT 'project',               -- 'project', 'global' (for future multi-project support)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Example entries:
INSERT INTO user_settings (setting_key, setting_value, description) VALUES
  ('fp_strictness_level', '{"level": "strict", "exceptions": ["fp_currying"]}', 'How strict to enforce FP directives'),
  ('prefer_explicit_returns', 'true', 'Always use explicit return statements'),
  ('suppress_warnings', '["fp_type_inference"]', 'Directives to suppress low-confidence warnings');
```

#### Table: directive_preferences
```sql
CREATE TABLE IF NOT EXISTS directive_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directive_name TEXT NOT NULL,               -- e.g., 'project_file_write'
    preference_key TEXT NOT NULL,               -- e.g., 'always_add_docstrings', 'max_function_length'
    preference_value TEXT NOT NULL,             -- Atomic value (JSON for complex structures)
    active BOOLEAN DEFAULT 1,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(directive_name, preference_key)      -- Allows multiple preferences per directive, one value per key
);

-- Example entries (atomic key-value pairs):
INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description) VALUES
  ('project_file_write', 'always_add_docstrings', 'true', 'Always add docstrings to functions'),
  ('project_file_write', 'max_function_length', '50', 'Maximum function length in lines'),
  ('project_file_write', 'prefer_guard_clauses', 'true', 'Use guard clauses instead of nested conditionals');
```

#### Table: ai_interaction_log
```sql
CREATE TABLE IF NOT EXISTS ai_interaction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_type TEXT NOT NULL,             -- 'preference_learned', 'correction', 'clarification'
    directive_context TEXT,                     -- Directive being executed
    user_feedback TEXT NOT NULL,                -- What user said/corrected
    ai_interpretation TEXT,                     -- How AI interpreted it
    applied_to_preferences BOOLEAN DEFAULT 0,   -- Whether this updated preferences
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: Track user corrections to learn preferences over time
```

#### Table: fp_flow_tracking
```sql
CREATE TABLE IF NOT EXISTS fp_flow_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    function_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    fp_directives_applied TEXT NOT NULL,        -- JSON array of directive names
    compliance_score REAL DEFAULT 1.0,          -- 0-1 score
    issues_json TEXT,                           -- JSON array of compliance issues
    user_overrides TEXT,                        -- JSON of user-approved exceptions
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: Track FP compliance history for improvement analysis
```

#### Table: issue_reports
```sql
CREATE TABLE IF NOT EXISTS issue_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,                  -- 'bug', 'feature_request', 'directive_issue'
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    directive_name TEXT,                        -- Related directive if applicable
    context_log_ids TEXT,                       -- JSON array of ai_interaction_log IDs
    status TEXT DEFAULT 'draft',                -- 'draft', 'submitted', 'resolved'
    submitted_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Purpose: Allow users to compile context and submit issues with full logs
```

---

## Cost Management & Opt-In Tracking

All tracking features are **disabled by default** to minimize API token usage costs. Users must explicitly enable tracking when debugging or analyzing AIFP behavior.

### Tracking Settings Table
```sql
CREATE TABLE IF NOT EXISTS tracking_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT NOT NULL UNIQUE,          -- e.g., 'fp_flow_tracking', 'issue_reports'
    enabled BOOLEAN DEFAULT 0,                  -- Default: disabled
    description TEXT,
    estimated_token_overhead TEXT,              -- e.g., "~5% increase per file write"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Default entries (all disabled):
INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
  ('fp_flow_tracking', 0, 'Track FP directive compliance over time', '~5% token increase per file write'),
  ('issue_reports', 0, 'Enable detailed issue report compilation', '~2% token increase on errors'),
  ('ai_interaction_log', 0, 'Log all AI interactions for learning', '~3% token increase overall');
```

### Cost Philosophy
- **Project work should be cost-efficient**: Only essential DB operations enabled by default
- **Debugging is opt-in**: Users explicitly enable tracking when needed
- **Transparency**: Show estimated token overhead for each feature
- **Granular control**: Enable/disable features independently

---

## New Directive: user_preferences_sync

```json
{
  "name": "user_preferences_sync",
  "type": "project",
  "level": 0,
  "parent_directive": "aifp_run",
  "category": {
    "name": "user_customization",
    "description": "Manages user-specific AI behavior preferences"
  },
  "description": "Loads and applies user preferences before executing any project directive. Learns from user corrections and updates preferences automatically.",
  "md_file_path": "directives/user_preferences_sync.md",
  "workflow": {
    "trunk": "load_preferences",
    "branches": [
      {"if": "preferences_exist", "then": "apply_to_context", "details": {"cache_duration": "session"}},
      {"if": "no_preferences", "then": "initialize_defaults", "details": {"create_db": true}},
      {"if": "user_correction_detected", "then": "learn_preference", "details": {"confidence_threshold": 0.8, "log_to_ai_interaction": true}},
      {"fallback": "continue_without_preferences"}
    ],
    "error_handling": {"on_failure": "log_to_project_notes", "continue": true}
  },
  "roadblocks_json": [
    {"issue": "preferences_db_missing", "resolution": "Initialize user_preferences.db with defaults"},
    {"issue": "conflicting_preferences", "resolution": "Prompt user for resolution and update"}
  ],
  "intent_keywords_json": ["preferences", "settings", "customize", "user style"],
  "confidence_threshold": 0.7,
  "notes": "Executed before any file write or compliance check to ensure user preferences are applied."
}
```

---

### Database 4: user_directives.db (NEW - User-Defined Automation)

**Location**: `.aifp-project/user_directives.db`
**Mutability**: Updated during directive parsing, validation, and execution
**Purpose**: Store user-defined automation directives parsed from YAML/JSON/TXT files

#### Tables

**user_directives**:
```sql
CREATE TABLE IF NOT EXISTS user_directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    trigger_type TEXT NOT NULL,                 -- 'time', 'condition', 'event', 'manual'
    trigger_definition TEXT NOT NULL,           -- JSON: cron schedule, condition, event source
    implementation_file_path TEXT,              -- Path to generated implementation code
    status TEXT DEFAULT 'draft',                -- 'draft', 'validated', 'active', 'paused', 'error'
    validation_errors TEXT,                     -- JSON array of validation issues
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**directive_executions**:
```sql
CREATE TABLE IF NOT EXISTS directive_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_directive_id INTEGER NOT NULL,
    execution_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,                       -- 'success', 'failure', 'partial'
    duration_ms INTEGER,
    error_message TEXT,
    FOREIGN KEY (user_directive_id) REFERENCES user_directives(id) ON DELETE CASCADE
);
```

**directive_dependencies**:
```sql
CREATE TABLE IF NOT EXISTS directive_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_directive_id INTEGER NOT NULL,
    dependency_type TEXT NOT NULL,              -- 'package', 'api', 'file'
    dependency_name TEXT NOT NULL,
    version_requirement TEXT,
    installed BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_directive_id) REFERENCES user_directives(id) ON DELETE CASCADE
);
```

See `docs/db-schema/schemaExampleUserDirectives.sql` for complete schema.

---

## Git Integration (Added v1.1)

### project.db Enhancements

**New Fields in project table**:
```sql
ALTER TABLE project ADD COLUMN last_known_git_hash TEXT;
ALTER TABLE project ADD COLUMN last_git_sync DATETIME;
```

**New Table: work_branches** (Multi-user collaboration):
```sql
CREATE TABLE IF NOT EXISTS work_branches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_name TEXT UNIQUE NOT NULL,           -- e.g., 'aifp-alice-001', 'aifp-ai-claude-001'
    user_name TEXT NOT NULL,
    purpose TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    created_from TEXT DEFAULT 'main',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    merged_at DATETIME NULL,
    merge_conflicts_count INTEGER DEFAULT 0,
    merge_resolution_strategy TEXT,
    metadata_json TEXT
);
```

**New Table: merge_history** (FP-powered conflict resolution):
```sql
CREATE TABLE IF NOT EXISTS merge_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_branch TEXT NOT NULL,
    target_branch TEXT DEFAULT 'main',
    merge_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    conflicts_detected INTEGER DEFAULT 0,
    conflicts_auto_resolved INTEGER DEFAULT 0,
    conflicts_manual_resolved INTEGER DEFAULT 0,
    resolution_details TEXT,                    -- JSON: detailed resolution log
    merged_by TEXT,
    merge_commit_hash TEXT
);
```

**6 New Git Directives**:
1. `git_init` - Initialize or integrate with Git repository
2. `git_detect_external_changes` - Detect code modifications outside AIFP
3. `git_create_branch` - Create user/AI work branches (aifp-{user}-{number})
4. `git_detect_conflicts` - FP-powered conflict detection before merge
5. `git_merge_branch` - Merge with AI-assisted conflict resolution
6. `git_sync_state` - Synchronize Git hash with project.db

**9 New Git Helper Functions**:
- `get_current_commit_hash(project_root)`
- `detect_external_changes(project_root)`
- `create_work_branch(user_name, purpose, project_root)`
- `get_branch_metadata(branch_name, project_root)`
- `detect_conflicts_before_merge(source_branch, target_branch, project_root)`
- `merge_with_fp_intelligence(source_branch, project_root)`
- `log_merge_history(merge_data, project_root)`
- `get_user_from_git_config(project_root)`
- `update_git_sync_state(project_root)`

---

## Integration Points

### 1. Directive Execution Flow
```
aifp_run
  ↓
user_preferences_sync (NEW - loads preferences)
  ↓
project_task_decomposition / project_file_write / etc.
  ↓ (on file write)
Apply directive_preferences for active directive
  ↓
Execute workflow with user overrides
  ↓
Log to project.db notes (not aifp_core.db)
  ↓
Track in fp_flow_tracking if FP directive involved
  ↓
If user corrects: log to ai_interaction_log
```

### 2. Directive References to Preferences

**project_file_write** should check:
```sql
SELECT preference_json
FROM user_preferences.directive_preferences
WHERE directive_name = 'project_file_write'
  AND active = 1;
```

**project_compliance_check** should check:
```sql
SELECT setting_value
FROM user_preferences.user_settings
WHERE setting_key = 'fp_strictness_level';
```

### 3. Learning from User Corrections

When user says "always use guard clauses here":
1. Log to `ai_interaction_log`
2. Parse intent → create/update entry in `directive_preferences`
3. Mark `applied_to_preferences = 1`
4. Confirm with user: "I'll remember to use guard clauses in similar contexts. Would you like this applied project-wide?"

---

## Directive JSON Notes Field Handling

### Decision: No `notes` Column in Database

The directive JSON files contain a `"notes"` field that provides additional context about each directive. However, we've decided **NOT** to add a `notes` column to the `directives` table in the database.

**Rationale**:
1. **MD Files provide detailed documentation**: Each directive has `md_file_path` pointing to comprehensive markdown documentation
2. **Description field exists**: Provides concise summary of directive purpose
3. **Avoid duplication**: No need for three levels of documentation (description, notes, MD file)

### Action Required: Merge Notes into Description

**Before importing directives to database**:
1. Review each directive's `"notes"` field
2. Merge useful context from `"notes"` into `"description"` where appropriate
3. Remove `"notes"` field from all JSON files

**Script needed**: `merge-notes-to-description.py`
- Reads all directive JSON files
- For each directive, prompts user or auto-merges notes into description
- Removes notes field
- Saves updated JSON

**Example**:
```json
// Before:
{
  "description": "Enforces pure functions: deterministic output for given inputs, no external state or side effects.",
  "notes": "Central FP rule; applies to all code generation and compliance checks. Links to project_compliance_check."
}

// After (option 1 - merge):
{
  "description": "Enforces pure functions: deterministic output for given inputs, no external state or side effects. Central FP rule applied to all code generation and compliance checks."
}

// After (option 2 - keep concise if notes redundant):
{
  "description": "Enforces pure functions: deterministic output for given inputs, no external state or side effects."
}
```

---

## Migration Tasks

### Phase 1: Clean aifp_core.db (High Priority)
- [x] Remove notes table from schemaExampleMCP.sql
- [x] Add schema_version table to schemaExampleMCP.sql
- [x] Update helper_functions.error_handling documentation to reference user_preferences.db logging
- [x] Add find_directive_by_intent helper function to schemaExampleMCP.sql
- [x] Merge notes field into description for all directive JSON files (manually completed by user)
- [x] Remove notes field from all directive JSON files (manually completed by user)
- [x] Review all directive workflow JSON references to notes table:
  - [x] directives-project.json (22 directives) - All notes references verified to point to project.db
  - [x] directives-fp-core.json (30 directives) - Notes field removed, no runtime logging
  - [x] directives-fp-aux.json (32 directives) - Assumed similar to fp-core
- [x] Notes table references validated:
  - All `"log_note"`, `"log in notes"`, etc. correctly reference project.db notes table
  - No references to removed MCP notes table found

### Phase 2: Enhance project.db (Medium Priority)
- [x] Add new fields to notes table:
  - [x] `source TEXT DEFAULT 'user'`
  - [x] `directive_name TEXT`
  - [x] `severity TEXT DEFAULT 'info'`
- [x] Create indexes for performance:
  - [x] `CREATE INDEX idx_notes_directive ON notes(directive_name);`
  - [x] `CREATE INDEX idx_notes_severity ON notes(severity);`
  - [x] `CREATE INDEX idx_notes_source ON notes(source);`
- [x] Add schema_version table to schemaExampleProject.sql

### Phase 3: Create user_preferences.db (Medium Priority)
- [x] Create new schema file: `schemaExampleSettings.sql` (renamed from schemaExampleUserPreferences.sql)
- [x] Implement tables:
  - [x] user_settings
  - [x] directive_preferences (with atomic key-value structure)
  - [x] ai_interaction_log
  - [x] fp_flow_tracking
  - [x] issue_reports
  - [x] tracking_settings (feature flags for opt-in tracking)
- [x] Add helper_function_logging to tracking_settings
- [x] Add schema_version table
- [ ] Add to sync-directives.py as optional initialization
- [ ] Create extract-preferences.py for export

### Phase 3.5: Create user_directives.db (Medium Priority)
- [x] Create new schema file: `schemaExampleUserDirectives.sql`
- [x] Implement tables:
  - [x] user_directives
  - [x] directive_executions
  - [x] directive_dependencies
  - [x] generated_code_references
  - [x] directive_source_tracking
- [x] Add schema_version table
- [ ] Add to sync-directives.py as optional initialization

### Phase 3.6: Add Git Integration to project.db (High Priority) ✅ COMPLETE
- [x] Add Git fields to project table:
  - [x] `last_known_git_hash TEXT`
  - [x] `last_git_sync DATETIME`
- [x] Create work_branches table for multi-user/multi-AI collaboration
- [x] Create merge_history table for FP-powered conflict resolution
- [x] Add indexes for Git collaboration tables:
  - [x] `idx_work_branches_user`
  - [x] `idx_work_branches_status`
  - [x] `idx_merge_history_timestamp`
  - [x] `idx_merge_history_source`
- [x] Update schema_version to 1.1
- [x] Create migration path (v1.0 → v1.1) in migration-scripts-plan.md

### Phase 4: Implement User Preferences Directives (Medium Priority) ✅ COMPLETE
- [x] Create directives-user-pref.json with 7 new directives:
  - [x] user_preferences_sync - Loads and applies preferences
  - [x] user_preferences_update - Maps user requests to directives (uses find_directive_by_intent helper)
  - [x] user_preferences_learn - Learns from corrections (requires confirmation)
  - [x] user_preferences_export - Exports to JSON
  - [x] user_preferences_import - Imports from JSON
  - [x] project_notes_log - Handles logging to project.db with directive_name field
  - [x] tracking_toggle - Enables/disables tracking features
- [ ] Create markdown documentation (7 .md files in directives/)
- [x] Add to directives-interactions.json:
  - [x] aifp_run → user_preferences_sync (triggers)
  - [x] user_preferences_sync → user_preferences_update (depends_on)
  - [x] user_preferences_update → find_directive_by_intent helper (fp_reference)
  - [x] project_file_write → user_preferences_sync (cross_link)
  - [x] project_compliance_check → user_preferences_sync (cross_link)
- [x] **Update directive workflows with explicit preference checking** 🆕:
  - [x] project_file_write: Added "check_user_preferences" trunk and preference loading branches
  - [x] project_compliance_check: Added explicit preference checking for compliance strictness
  - [x] project_task_decomposition: Added explicit preference checking for task decomposition style
  - [x] Added 12 example directive_preferences entries to schemaExampleSettings.sql

### Phase 4.5: Implement User System Directives (Medium Priority) ✅ COMPLETE
- [x] Create directives-user-system.json with 8 new directives:
  - [x] user_directive_parse - Parse directive files with ambiguity detection
  - [x] user_directive_validate - Interactive Q&A validation
  - [x] user_directive_implement - Generate FP-compliant implementation code
  - [x] user_directive_approve - User testing and approval workflow
  - [x] user_directive_activate - Deploy and start execution
  - [x] user_directive_monitor - Track execution and errors
  - [x] user_directive_update - Handle source file changes
  - [x] user_directive_deactivate - Stop execution and cleanup
- [ ] Create markdown documentation (8 .md files in directives/)
- [x] Add to directives-interactions.json (integrated with existing interactions)

### Phase 4.6: Implement Git Directives (High Priority) ✅ COMPLETE
- [x] Create directives-git.json with 6 new directives:
  - [x] git_init - Initialize or integrate with Git repository
  - [x] git_detect_external_changes - Detect code modifications outside AIFP
  - [x] git_create_branch - Create user/AI work branches (aifp-{user}-{number})
  - [x] git_detect_conflicts - FP-powered conflict detection before merge
  - [x] git_merge_branch - Merge with AI-assisted conflict resolution
  - [x] git_sync_state - Synchronize Git hash with project.db
- [ ] Create markdown documentation (6 .md files in directives/)
- [x] Add to directives-interactions.json:
  - [x] project_init → git_init (triggers)
  - [x] aifp_run → git_sync_state (triggers on boot)
  - [x] git_sync_state → git_detect_external_changes (triggers)
  - [x] git_detect_conflicts → fp_purity (fp_reference)
  - [x] git_detect_conflicts → fp_dependency_tracking (fp_reference)
  - [x] git_merge_branch → project_update_db (triggers)
- [x] Document 9 Git helper functions in helper-functions-reference.md
- [x] Update blueprint_git.md with complete architecture
- [x] Update blueprint_project_db.md with Git tables

### Phase 5: Update Python Scripts (Low Priority)
- [ ] sync-directives.py:
  - [ ] Remove notes table handling for aifp_core.db
  - [ ] Add optional user_preferences.db creation
- [ ] extract-directives.py:
  - [ ] Skip notes table when extracting from aifp_core.db
- [ ] Create new: init-user-preferences.py
  - [ ] Initialize user_preferences.db with defaults
  - [ ] Called by project_init directive

---

## Design Decisions

### Decision 1: Separate DB vs. Extended project.db?
**Choice**: Separate `user_preferences.db`

**Reasoning**:
- Clear separation of concerns (project state vs. user behavior)
- Allows for future: copy preferences between projects
- Easier to reset/backup preferences independently
- Could evolve to global user preferences across all projects

### Decision 2: Auto-learn vs. Explicit Preference Setting?
**Choice**: Hybrid approach

**Reasoning**:
- Auto-learn from corrections (track in ai_interaction_log)
- But require confirmation before applying project-wide
- User can explicitly set via future CLI commands or directives
- Prevents AI from making incorrect assumptions

### Decision 3: Scope of Preferences?
**Phase 1 Scope**: Project-level only
**Future Scope**: Global user preferences with project overrides

**Reasoning**:
- Start simple: project-level preferences sufficient for MVP
- Later: add global preferences with inheritance/override mechanism
- Settings could have: global default → project override → file/function override

---

## Questions for Review

1. **Issue Reports**: Is the issue_reports table overkill, or genuinely useful for user feedback?
   - **Pro**: Gives users a way to compile context and submit detailed bug reports
   - **Con**: Adds complexity; users might just use GitHub issues directly
   - **Recommendation**: Keep it; power users will appreciate the context bundling
   - **DECISION**: Keep the table but **disable by default**. Users should only track when debugging AIFP itself, not during regular project work. This keeps users focused on their project rather than MCP concerns. 

2. **FP Flow Tracking**: Should this be in project.db or user_preferences.db?
   - **Current**: In user_preferences.db
   - **Reasoning**: It's more about tracking compliance patterns for improvement analysis
   - **Alternative**: Could be in project.db as it's project-specific runtime data
   - **Recommendation**: Move to project.db; it's runtime state, not user preference
   - **DECISION**: Keep in user_preferences.db and **disable by default**. FP flow tracking is meta-analysis (analyzing AI's work), not project state. This minimizes token/API costs by making tracking opt-in only. Project.db should remain focused on "what the code is" rather than "how well AI followed FP rules". 

3. **Preference Granularity**: Should preferences be:
   - [ ] Project-level only (Phase 1)
   - [ ] Project + File-level
   - [ ] Project + File + Function-level
   - **Recommendation**: Start with project-level; add file-level in Phase 2
   - **DECISION**: Use **directive-based preferences** instead of file/function hierarchy. This keeps preferences precisely tied to directives for simple AI lookup. Use atomic key-value structure with UNIQUE(directive_name, preference_key) to allow multiple independent preferences per directive while preventing duplicate keys. This enables:
     - Multiple preferences per directive (different preference_key values)
     - Atomic updates (change one preference without touching others)
     - Individual enable/disable per preference
     - Clear audit trail with per-preference timestamps

4. **Backward Compatibility**: How to handle existing projects?
   - On first run with new MCP version: auto-create user_preferences.db with defaults
   - Migrate any existing notes that look like preferences
   - Log migration summary to project.db notes
   - **DECISION**: Since distribution is via GitHub (not package managers yet), provide **migration scripts** for users to execute manually. Always maintain backward compatibility after initial release (currently in dev/prep stage). Create versioned migrations in `migrations/` directory with schema_version tracking.

---

## Success Criteria - Planning Phase Complete ✅

### Database Architecture
- [x] aifp_core.db contains zero mutable tables
- [x] All runtime logging goes to project.db
- [x] All four databases have clear, documented purposes
- [x] Directive JSON files align with new database schemas
- [x] Schema version tracking added to all databases
- [x] Migration path documented (v1.0 → v1.1 for Git integration)

### User Preferences System
- [x] User can set preferences that persist across sessions (via directive_preferences table)
- [x] User can see what preferences are active for a directive (via user_preferences_sync)
- [x] AI learns from corrections and offers to update preferences (via user_preferences_learn)
- [x] AI can map user behavior requests to directives (via find_directive_by_intent helper)
- [x] Users can export preferences for backup/sharing (via user_preferences_export)
- [x] Opt-in tracking with cost transparency (tracking_settings table)

### User Automation System
- [x] Users can define custom automation directives (user_directives.db)
- [x] Directive validation workflow designed (user_directive_validate)
- [x] FP-compliant implementation generation designed (user_directive_implement)
- [x] Execution monitoring and error handling designed (user_directive_monitor)

### Git Integration (v1.1)
- [x] External change detection designed (last_known_git_hash)
- [x] Multi-user/multi-AI collaboration designed (work_branches table)
- [x] FP-powered conflict resolution designed (merge_history table)
- [x] 6 Git directives defined and documented
- [x] 9 Git helper functions documented
- [x] Cross-references between Git and FP directives established

### Directive System
- [x] 108 total directives defined (30 FP core + 32 FP aux + 25 Project + 7 User Prefs + 8 User System + 6 Git)
- [x] 70 directive interactions mapped
- [x] Cross-links between FP and Project directives established
- [x] 44+ helper functions documented

---

## Implementation Roadmap (Next Steps)

### Planning Phase - Completed ✅
1. ~~Design four-database architecture~~
2. ~~Create all four database schemas (MCP, Project v1.1, User Prefs, User Directives)~~
3. ~~Design user preferences directives (7 directives)~~
4. ~~Design user automation directives (8 directives)~~
5. ~~Design Git integration directives (6 directives)~~
6. ~~Align existing directives with schema changes~~
7. ~~Create helper functions documentation (44+ functions)~~
8. ~~Map directive interactions (70 interactions)~~
9. ~~Document migration paths (v1.0 → v1.1)~~

### Implementation Phase - Not Started ⚪

**IMPORTANT**: All items below are **planning documents only**. No Python code has been written yet.

#### Phase 5: Python Scripts & Tooling
- [ ] **sync-directives.py**: Populate aifp_core.db from JSON files
  - Remove notes table handling
  - Add find_directive_by_intent helper function
  - Import all 4 directive JSON files (project, fp-core, fp-aux, user-pref)
- [ ] **init-user-preferences.py**: Initialize user_preferences.db
  - Use schemaExampleSettings.sql
  - Called by project_init directive
- [ ] **migrate.py**: Database migration script (see migration-scripts-plan.md)
  - Version detection and comparison
  - Automatic backup before migrations
  - Rollback support

#### Phase 6: Markdown Documentation
- [ ] Create 7 markdown files for user preference directives
- [ ] Update existing directive .md files if needed

#### Phase 7: Directive Interactions
- [ ] Update directives-interactions.json with new directive relationships
- [ ] Define triggers, dependencies, and cross-links

#### Phase 8: Testing & Validation
- [ ] Test directive import into aifp_core.db
- [ ] Test user_preferences.db initialization
- [ ] Test preference mapping workflow (user request → directive)
- [ ] Test migration scripts

---

## Summary

### What's Complete: PLANNING & DOCUMENTATION ✅
- ✅ Four-database architecture designed
- ✅ All 4 database schemas created (MCP, Project v1.1, User Prefs, User Directives)
- ✅ 108 directives defined across 7 JSON files
- ✅ 70 directive interactions mapped
- ✅ 44+ helper functions documented
- ✅ Git integration designed (v1.1)
- ✅ User preferences system designed
- ✅ User automation system designed
- ✅ Migration paths documented
- ✅ All blueprints and architecture docs updated

### What's NOT Complete: IMPLEMENTATION ⚪
- ⚪ No Python code written
- ⚪ No MCP server implementation
- ⚪ No databases created or populated
- ⚪ No helper functions implemented
- ⚪ No directive execution engine
- ⚪ No tests written
- ⚪ No migration scripts coded

### Next Steps
See `docs/implementation-plans/phase-1-mcp-server-bootstrap.md` for the complete implementation roadmap (Phase 1-6, estimated 6-12 months).

---

## Design Notes

- This restructuring maintains backward compatibility by ensuring project.db structure remains stable
- The user_preferences.db and user_directives.db are entirely additive; existing projects work without them
- Migration path is graceful: detect missing databases and initialize on first run
- This design positions AIFP for future enhancements like multi-project preference sharing
- Git integration (v1.1) adds external change detection and FP-powered conflict resolution
- All directive JSON files are ready to be loaded into aifp_core.db once implementation begins

# MCP Database Restructuring Plan

**Purpose**: Restructure database architecture to properly separate immutable MCP configuration from mutable project state and user preferences.

**Date Created**: 2025-10-12
**Status**: Planning

---

## Overview

The current design has architectural conflicts around the notes table and runtime state management. This plan establishes a clear three-database architecture:

1. **aifp_core.db** - Read-only MCP configuration (shipped with MCP)
2. **project.db** - Mutable project state (in `.aifp-project/`)
3. **user_preferences.db** - User/project-specific AI behavior customization (in `.aifp-project/`)

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
    preference_type TEXT NOT NULL,              -- 'pre_condition', 'post_condition', 'style_override'
    preference_json TEXT NOT NULL,              -- JSON configuration
    active BOOLEAN DEFAULT 1,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(directive_name, preference_type)
);

-- Example entry:
INSERT INTO directive_preferences (directive_name, preference_type, preference_json, description) VALUES
  ('project_file_write', 'style_override',
   '{"always_add_docstrings": true, "max_function_length": 50, "prefer_guard_clauses": true}',
   'User prefers guard clauses and docstrings on all functions');
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

## Migration Tasks

### Phase 1: Clean aifp_core.db (High Priority)
- [ ] Remove notes table from schemaExampleMCP.sql
- [ ] Update all directive workflow JSON in:
  - [ ] directives-project.json (22 directives)
  - [ ] directives-fp-core.json (30 directives)
  - [ ] directives-fp-aux.json (32 directives)
- [ ] Find/replace patterns:
  - [ ] `"log_note": true` → `"log_to_project_notes": true`
  - [ ] `"reference_table": "notes"` → `"reference_table": "project_notes"`
  - [ ] Any other notes references
- [ ] Update schemaExampleMCP.sql sample directives (lines 94-163)

### Phase 2: Enhance project.db (Medium Priority)
- [ ] Add new fields to notes table:
  - [ ] `source TEXT DEFAULT 'user'`
  - [ ] `directive_name TEXT`
  - [ ] `severity TEXT DEFAULT 'info'`
- [ ] Create indexes for performance:
  - [ ] `CREATE INDEX idx_notes_directive ON notes(directive_name);`
  - [ ] `CREATE INDEX idx_notes_severity ON notes(severity);`

### Phase 3: Create user_preferences.db (Medium Priority)
- [ ] Create new schema file: `schemaExampleUserPreferences.sql`
- [ ] Implement tables:
  - [ ] user_settings
  - [ ] directive_preferences
  - [ ] ai_interaction_log
  - [ ] fp_flow_tracking
  - [ ] issue_reports
- [ ] Add to sync-directives.py as optional initialization
- [ ] Create extract-preferences.py for export

### Phase 4: Implement user_preferences_sync Directive (Low Priority)
- [ ] Add user_preferences_sync to directives-project.json
- [ ] Create markdown documentation: `directives/user_preferences_sync.md`
- [ ] Add to directives-interactions.json:
  - [ ] aifp_run → user_preferences_sync (triggers)
  - [ ] user_preferences_sync → project_file_write (cross_link)
  - [ ] user_preferences_sync → project_compliance_check (cross_link)

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

2. **FP Flow Tracking**: Should this be in project.db or user_preferences.db?
   - **Current**: In user_preferences.db
   - **Reasoning**: It's more about tracking compliance patterns for improvement analysis
   - **Alternative**: Could be in project.db as it's project-specific runtime data
   - **Recommendation**: Move to project.db; it's runtime state, not user preference

3. **Preference Granularity**: Should preferences be:
   - [ ] Project-level only (Phase 1)
   - [ ] Project + File-level
   - [ ] Project + File + Function-level
   - **Recommendation**: Start with project-level; add file-level in Phase 2

4. **Backward Compatibility**: How to handle existing projects?
   - On first run with new MCP version: auto-create user_preferences.db with defaults
   - Migrate any existing notes that look like preferences
   - Log migration summary to project.db notes

---

## Success Criteria

- [ ] aifp_core.db contains zero mutable tables
- [ ] All runtime logging goes to project.db
- [ ] User can set preferences that persist across sessions
- [ ] User can see what preferences are active for a directive
- [ ] AI learns from corrections and offers to update preferences
- [ ] Users can export preferences for backup/sharing
- [ ] All three databases have clear, documented purposes

---

## Next Steps

1. **Immediate**: Review this plan with team/user
2. **Phase 1**: Clean aifp_core.db (high priority for schema correctness)
3. **Phase 2**: Enhance project.db (medium priority)
4. **Phase 3**: Design user_preferences.db schema in detail
5. **Phase 4**: Implement user_preferences_sync directive
6. **Phase 5**: Update tooling (sync/extract scripts)

---

## Notes

- This restructuring maintains backward compatibility by ensuring project.db structure remains stable
- The user_preferences.db is entirely additive; existing projects work without it
- Migration path is graceful: detect missing preferences DB and initialize on first run
- This design positions AIFP for future enhancements like multi-project preference sharing

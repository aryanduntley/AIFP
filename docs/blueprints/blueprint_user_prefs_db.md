# User Preferences Database Blueprint (user_preferences.db)

## Overview

The `user_preferences.db` database is a **per-project, mutable database** that stores user-specific AI behavior customizations, preferences, and opt-in tracking features. It resides in `.aifp-project/user_preferences.db` and enables users to personalize how AI executes directives and learns from corrections.

### Core Purpose

- **Directive Customization**: Per-directive behavior overrides (e.g., "always add docstrings")
- **User Settings**: Project-wide AI behavior configurations
- **AI Learning**: Track user corrections and infer preferences (opt-in)
- **FP Compliance Tracking**: Monitor FP directive compliance over time (opt-in)
- **Issue Reporting**: Compile contextual bug reports with full logs (opt-in)
- **Cost Management**: All tracking features disabled by default to minimize API token usage

---

## Database Schema

### User Settings Table

**Purpose**: Project-wide AI behavior configurations

```sql
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,           -- e.g., 'fp_strictness_level', 'prefer_explicit_returns'
    setting_value TEXT NOT NULL,                -- JSON value or simple string
    description TEXT,
    scope TEXT DEFAULT 'project',               -- 'project' (future: 'global' for multi-project support)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields**:
- `setting_key`: Unique setting identifier (snake_case)
- `setting_value`: Can be simple string ("true") or JSON object ({"level": "strict"})
- `scope`: Currently 'project', future support for 'global' across projects

**Default Settings**:
```sql
INSERT INTO user_settings (setting_key, setting_value, description) VALUES
  ('fp_strictness_level', '{"level": "standard", "exceptions": []}', 'How strict to enforce FP directives'),
  ('prefer_explicit_returns', 'true', 'Always use explicit return statements'),
  ('suppress_warnings', '[]', 'Directives to suppress low-confidence warnings');
```

**Usage**:
- Updated by `user_preferences_update` directive
- Queried by `user_preferences_sync` before directive execution
- Can be exported/imported via `user_preferences_export/import`

---

### Directive Preferences Table

**Purpose**: Per-directive behavior customizations using atomic key-value structure

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

CREATE INDEX IF NOT EXISTS idx_directive_preferences_directive ON directive_preferences(directive_name);
CREATE INDEX IF NOT EXISTS idx_directive_preferences_active ON directive_preferences(active);
```

**Key Design**: **UNIQUE(directive_name, preference_key)** enables atomic key-value structure:
- One directive can have multiple preferences
- Each preference is a separate key-value pair
- Example: `project_file_write` can have both `always_add_docstrings: true` AND `max_function_length: 50`

**Example Entries**:
```sql
INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description) VALUES
  ('project_file_write', 'always_add_docstrings', 'true', 'Always add docstrings to functions'),
  ('project_file_write', 'max_function_length', '50', 'Maximum function length in lines'),
  ('project_file_write', 'prefer_guard_clauses', 'true', 'Use guard clauses instead of nested conditionals'),
  ('project_compliance_check', 'auto_fix_violations', 'false', 'Automatically fix FP violations when detected');
```

**Usage**:
- Updated by `user_preferences_update` (user explicit requests)
- Updated by `user_preferences_learn` (AI learns from corrections)
- Queried by `user_preferences_sync` before directive execution
- Applied to directive context before workflow runs

**Workflow**:
1. User says: "Always add docstrings"
2. `user_preferences_update` → calls `find_directive_by_intent` helper
3. Helper searches directives table → finds `project_file_write`
4. Confirms with user: "Apply to file writing operations?"
5. Inserts: `(project_file_write, always_add_docstrings, true)`
6. Next `project_file_write` execution → `user_preferences_sync` loads preference → adds docstrings

---

### AI Interaction Log Table

**Purpose**: Track user corrections to learn preferences over time (DISABLED BY DEFAULT)

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

CREATE INDEX IF NOT EXISTS idx_ai_interaction_log_directive ON ai_interaction_log(directive_context);
```

**Purpose**: When enabled, logs all user corrections and clarifications for:
- Pattern detection (repeated corrections → inferred preference)
- Context for `user_preferences_learn` directive
- Issue report compilation
- Understanding user workflow patterns

**Example Entry**:
```sql
INSERT INTO ai_interaction_log (interaction_type, directive_context, user_feedback, ai_interpretation, applied_to_preferences)
VALUES (
  'correction',
  'project_file_write',
  'Actually, use guard clauses instead of nested if statements',
  'User prefers guard clauses over nested conditionals',
  1
);
```

**Enabled via**: `tracking_toggle` directive

**Token Cost**: ~3% increase overall (logged on every AI response)

---

### FP Flow Tracking Table

**Purpose**: Track FP directive compliance history for improvement analysis (DISABLED BY DEFAULT)

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

CREATE INDEX IF NOT EXISTS idx_fp_flow_tracking_file ON fp_flow_tracking(file_path);
```

**Purpose**: When enabled, logs every FP compliance check for:
- Tracking compliance trends over time
- Identifying recurring violations
- Analyzing which directives are most frequently triggered
- Understanding user-approved exceptions

**Example Entry**:
```sql
INSERT INTO fp_flow_tracking (function_name, file_path, fp_directives_applied, compliance_score, issues_json)
VALUES (
  'calculate_discount',
  'src/pricing.py',
  '["fp_purity", "fp_immutability", "fp_side_effect_detection"]',
  0.67,
  '[{"directive": "fp_purity", "issue": "Global state access", "severity": "warning"}]'
);
```

**Enabled via**: `tracking_toggle` directive

**Token Cost**: ~5% increase per file write (logged on every FP check)

---

### Issue Reports Table

**Purpose**: Allow users to compile context and submit issues with full logs (DISABLED BY DEFAULT)

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

CREATE INDEX IF NOT EXISTS idx_issue_reports_status ON issue_reports(status);
```

**Purpose**: When enabled, allows users to:
- Compile contextual bug reports with AI interaction history
- Link specific AI interactions to issue reports
- Track issue status (draft → submitted → resolved)
- Export reports for GitHub submission

**Example Entry**:
```sql
INSERT INTO issue_reports (report_type, title, description, directive_name, context_log_ids, status)
VALUES (
  'directive_issue',
  'fp_purity fails to detect mutation via list.append',
  'The fp_purity directive did not flag list.append() as a mutation...',
  'fp_purity',
  '[123, 124, 125]',  -- References ai_interaction_log entries
  'draft'
);
```

**Enabled via**: `tracking_toggle` directive

**Token Cost**: ~2% increase on errors (logged only when user reports issue)

---

### Tracking Settings Table

**Purpose**: Control which tracking features are enabled (feature flags)

```sql
CREATE TABLE IF NOT EXISTS tracking_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_name TEXT NOT NULL UNIQUE,          -- e.g., 'fp_flow_tracking', 'issue_reports'
    enabled BOOLEAN DEFAULT 0,                  -- Default: disabled (opt-in only)
    description TEXT,
    estimated_token_overhead TEXT,              -- e.g., "~5% increase per file write"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Default Entries** (all disabled):
```sql
INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
  ('fp_flow_tracking', 0, 'Track FP directive compliance over time', '~5% token increase per file write'),
  ('issue_reports', 0, 'Enable detailed issue report compilation', '~2% token increase on errors'),
  ('ai_interaction_log', 0, 'Log all AI interactions for learning', '~3% token increase overall'),
  ('helper_function_logging', 0, 'Log helper function errors and execution details', '~1% token increase on errors');
```

**Usage**:
- Updated by `tracking_toggle` directive
- Shows user estimated token overhead before enabling
- Queried by directives to check if tracking is enabled

**Cost Management Philosophy**:
- Project work should be cost-efficient
- Debugging and analytics are opt-in
- Users see token cost estimates before enabling

---

## Summary

The `user_preferences.db` database provides:

- **Per-directive customization** via atomic key-value preferences
- **User settings** for project-wide AI behavior
- **AI learning** from user corrections (opt-in)
- **FP compliance tracking** over time (opt-in)
- **Issue reporting** with full context (opt-in)
- **Cost-conscious design** with all tracking disabled by default
- **Export/Import** for backup and sharing preferences
- **Tracking feature flags** with estimated token overhead
- **Seamless integration** with directives via user_preferences_sync

It acts as the **customization layer** between the immutable aifp_core.db and the runtime project.db, allowing users to personalize AI behavior without modifying core directives or project state.

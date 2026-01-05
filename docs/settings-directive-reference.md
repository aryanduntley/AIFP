# Settings Referenced in Directive Files

**Date**: 2026-01-04
**Purpose**: Complete reference of all settings mentioned in directive JSON and MD files
**Source**: Comprehensive search of docs/directives-json/ and src/aifp/reference/directives/

---

## Global User Settings (3)

### 1. fp_strictness_level

**Setting Key**: `fp_strictness_level`
**Type**: JSON object
**Default**: `{"level": "standard", "exceptions": []}`
**Description**: Controls how strictly FP rules are enforced (strict/standard/relaxed)

**Referenced In**:
- **Directive**: `project_compliance_check`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_compliance_check.md`

- **Directive**: `project_init`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json`

- **Directive**: `user_preferences_sync`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

---

### 2. prefer_explicit_returns

**Setting Key**: `prefer_explicit_returns`
**Type**: Boolean string
**Default**: `"true"`
**Description**: Always use explicit return statements instead of implicit returns

**Referenced In**:
- **Directive**: General FP directives
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

---

### 3. suppress_warnings

**Setting Key**: `suppress_warnings`
**Type**: JSON array
**Default**: `[]`
**Description**: List of directives for which to suppress warning messages

**Referenced In**:
- **Directive**: Various directives that generate warnings
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

---

## Directive Preferences for project_file_write (5)

### 1. always_add_docstrings

**Preference Key**: `always_add_docstrings`
**Directive**: `project_file_write`
**Type**: Boolean
**Default**: Not set (false)
**Description**: Automatically add docstrings to all functions when writing files

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json` (line 609)
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_file_write.md`
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

**Example Usage**:
```json
{
  "directive_name": "project_file_write",
  "preference_key": "always_add_docstrings",
  "preference_value": "true"
}
```

---

### 2. max_function_length

**Preference Key**: `max_function_length`
**Directive**: `project_file_write`
**Type**: Integer
**Default**: Not set
**Description**: Maximum allowed lines per function; warns if exceeded

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_file_write.md`
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

**Example Usage**:
```json
{
  "directive_name": "project_file_write",
  "preference_key": "max_function_length",
  "preference_value": "50"
}
```

---

### 3. prefer_guard_clauses

**Preference Key**: `prefer_guard_clauses`
**Directive**: `project_file_write`
**Type**: Boolean
**Default**: Not set (false)
**Description**: Use guard clauses (early returns) instead of nested if statements

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_file_write.md`
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

**Example Usage**:
```json
{
  "directive_name": "project_file_write",
  "preference_key": "prefer_guard_clauses",
  "preference_value": "true"
}
```

---

### 4. code_style

**Preference Key**: `code_style`
**Directive**: `project_file_write`
**Type**: String (enum)
**Options**: "compact", "verbose", "explicit"
**Default**: Not set
**Description**: Overall coding style preference for generated code

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_file_write.md`
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

**Example Usage**:
```json
{
  "directive_name": "project_file_write",
  "preference_key": "code_style",
  "preference_value": "explicit"
}
```

---

### 5. indent_style

**Preference Key**: `indent_style`
**Directive**: `project_file_write`
**Type**: String (enum)
**Options**: "spaces_2", "spaces_4", "tabs"
**Default**: Not set
**Description**: Indentation style for generated code

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_file_write.md`
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

**Example Usage**:
```json
{
  "directive_name": "project_file_write",
  "preference_key": "indent_style",
  "preference_value": "spaces_2"
}
```

---

## Directive Preferences for project_task_decomposition (4)

### 1. task_granularity

**Preference Key**: `task_granularity`
**Directive**: `project_task_decomposition`
**Type**: String (enum)
**Options**: "fine", "medium", "coarse"
**Default**: "medium"
**Description**: How detailed to break down tasks

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json` (line 409)
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_task_decomposition.md`

**Example Usage**:
```json
{
  "directive_name": "project_task_decomposition",
  "preference_key": "task_granularity",
  "preference_value": "fine"
}
```

**Interpretation**:
- "fine" = Very granular tasks (many small tasks)
- "medium" = Balanced breakdown
- "coarse" = High-level tasks (fewer, larger tasks)

---

### 2. naming_convention

**Preference Key**: `naming_convention`
**Directive**: `project_task_decomposition`
**Type**: String (enum)
**Options**: "descriptive", "short", "numbered"
**Default**: "descriptive"
**Description**: How to name tasks and subtasks

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_task_decomposition.md`

**Example Usage**:
```json
{
  "directive_name": "project_task_decomposition",
  "preference_key": "naming_convention",
  "preference_value": "descriptive"
}
```

**Interpretation**:
- "descriptive" = "Implement matrix multiplication algorithm"
- "short" = "Matrix multiply"
- "numbered" = "Task 1", "Task 2", etc.

---

### 3. auto_create_items

**Preference Key**: `auto_create_items`
**Directive**: `project_task_decomposition`
**Type**: Boolean
**Default**: true
**Description**: Automatically create items for tasks during decomposition

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_task_decomposition.md`

**Example Usage**:
```json
{
  "directive_name": "project_task_decomposition",
  "preference_key": "auto_create_items",
  "preference_value": "true"
}
```

**Interpretation**:
- true = AI creates granular items under each task automatically
- false = User must manually create items

---

### 4. default_priority

**Preference Key**: `default_priority`
**Directive**: `project_task_decomposition`
**Type**: Integer
**Range**: 1-5
**Default**: 3
**Description**: Default priority level for new tasks

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_task_decomposition.md`

**Example Usage**:
```json
{
  "directive_name": "project_task_decomposition",
  "preference_key": "default_priority",
  "preference_value": "5"
}
```

**Interpretation**:
- 5 = Highest priority (critical)
- 3 = Medium priority
- 1 = Lowest priority

**Note**: This controls which of the schema-defined priority values ('low', 'medium', 'high', 'critical') to use as default. It does NOT change the allowed priority values themselves.

---

## Directive Preferences for project_compliance_check (3)

### 1. auto_fix_violations

**Preference Key**: `auto_fix_violations`
**Directive**: `project_compliance_check`
**Type**: Boolean
**Default**: Not set (false)
**Description**: Automatically refactor FP violations when detected

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json` (line 886)
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_compliance_check.md`

**Example Usage**:
```json
{
  "directive_name": "project_compliance_check",
  "preference_key": "auto_fix_violations",
  "preference_value": "true"
}
```

**Interpretation**:
- true = AI attempts to auto-refactor impure functions to pure
- false = AI only reports violations, does not fix

---

### 2. skip_warnings

**Preference Key**: `skip_warnings`
**Directive**: `project_compliance_check`
**Type**: Boolean
**Default**: Not set (false)
**Description**: Ignore non-critical compliance warnings

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json` (line 887)
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_compliance_check.md`

**Example Usage**:
```json
{
  "directive_name": "project_compliance_check",
  "preference_key": "skip_warnings",
  "preference_value": "true"
}
```

**Interpretation**:
- true = Only report critical violations
- false = Report all violations including warnings

---

### 3. strict_mode

**Preference Key**: `strict_mode`
**Directive**: `project_compliance_check`
**Type**: Boolean
**Default**: Not set (false)
**Description**: Extra strict FP compliance checking (zero tolerance)

**Referenced In**:
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json` (line 888)
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_compliance_check.md`
- File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_update.md`

**Example Usage**:
```json
{
  "directive_name": "project_compliance_check",
  "preference_key": "strict_mode",
  "preference_value": "true"
}
```

**Interpretation**:
- true = Even minor violations block code from being written
- false = Standard compliance checking

**Relationship**: Can override `fp_strictness_level` global setting when enabled

---

## Tracking Settings (4)

### 1. fp_flow_tracking

**Feature Name**: `fp_flow_tracking`
**Type**: Boolean (0/1)
**Default**: 0 (disabled)
**Token Overhead**: ~5% per file write
**Description**: Track which FP directives AI consults during code writing

**Referenced In**:
- **Directive**: `tracking_toggle`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directive_flow_user_preferences.json`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/tracking_toggle.md`

**Usage**: Analytics on FP pattern usage over time

---

### 2. ai_interaction_log

**Feature Name**: `ai_interaction_log`
**Type**: Boolean (0/1)
**Default**: 0 (disabled)
**Token Overhead**: ~3% overall
**Description**: Log all user corrections and feedback for preference learning

**Referenced In**:
- **Directive**: `tracking_toggle`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/tracking_toggle.md`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md`

**Required For**: `user_preferences_learn` directive

**Usage**: Enable AI to learn from user corrections

---

### 3. helper_function_logging

**Feature Name**: `helper_function_logging`
**Type**: Boolean (0/1)
**Default**: 0 (disabled)
**Token Overhead**: ~1% on errors
**Description**: Log directive execution outcomes and helper function errors

**Referenced In**:
- **Directive**: `tracking_toggle`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/tracking_toggle.md`

**Usage**: Performance tracking and debugging

---

### 4. issue_reports

**Feature Name**: `issue_reports`
**Type**: Boolean (0/1)
**Default**: 0 (disabled)
**Token Overhead**: ~2% on errors
**Description**: Enable detailed bug report compilation

**Referenced In**:
- **Directive**: `tracking_toggle`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json`
  - File: `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/tracking_toggle.md`

**Usage**: Error tracking and issue reporting

---

## Summary Statistics

**Total Settings Found**: 18
- Global User Settings: 3
- Directive Preferences: 11
  - project_file_write: 5
  - project_task_decomposition: 4
  - project_compliance_check: 3
- Tracking Features: 4

**Most Referenced Directives**:
1. `user_preferences_sync` - References all settings (loader)
2. `project_file_write` - 5 preferences
3. `project_task_decomposition` - 4 preferences
4. `project_compliance_check` - 3 preferences + 1 global setting
5. `tracking_toggle` - 4 tracking features

**Key Files**:
- `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-user-pref.json` - User preference directives
- `/home/eveningb4dawn/Desktop/Projects/AIFP/docs/directives-json/directives-project.json` - Project directives
- `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/user_preferences_sync.md` - Setting loader
- `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_file_write.md` - Code style preferences
- `/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/project_task_decomposition.md` - Task preferences

---

**Document Status**: ✅ Complete
**Last Updated**: 2026-01-04
**Source**: Comprehensive search of directive JSON and MD files

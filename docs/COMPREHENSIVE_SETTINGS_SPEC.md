# Comprehensive AIFP Settings Specification

**Date**: 2025-12-18
**Purpose**: Complete, up-to-date specification of all user settings and preferences
**Status**: Replaces outdated schemaExampleSettings.sql
**Version**: 2.0

---

## Overview

This document specifies all user-configurable settings in AIFP, organized by:
1. **User Settings** - Project-wide/global configurations
2. **Directive Preferences** - Per-directive behavior customizations
3. **Tracking Settings** - Opt-in feature flags for tracking/logging

**Database**: `user_preferences.db`
**Location**: `.aifp-project/user_preferences.db`
**Schema**: `src/aifp/database/schemas/user_preferences.sql`

---

## 1. User Settings (Project-Wide)

**Table**: `user_settings`
**Structure**: `(setting_key, setting_value, description, scope)`

These settings apply project-wide, not specific to individual directives.

### Core Settings

| Setting Key | Default Value | Type | Description | Scope |
|------------|---------------|------|-------------|-------|
| `fp_strictness_level` | `{"level": "standard", "exceptions": []}` | JSON | How strict to enforce FP directives (relaxed/standard/strict) | project |
| `prefer_explicit_returns` | `true` | boolean | Always use explicit return statements | project |
| `suppress_warnings` | `[]` | JSON array | Directives to suppress low-confidence warnings | project |
| `default_task_priority` | `medium` | string | Default priority for new tasks (low/medium/high) | project |
| `auto_check_compliance` | `false` | boolean | Run FP compliance check after every file write | project |
| `enable_git_hooks` | `true` | boolean | Enable git integration and hooks | project |
| `milestone_quality_gates` | `true` | boolean | Require compliance checks before milestone completion | project |

### Code Generation Settings

| Setting Key | Default Value | Type | Description | Scope |
|------------|---------------|------|-------------|-------|
| `default_docstring_style` | `google` | string | Docstring format (google/numpy/sphinx/none) | project |
| `max_function_complexity` | `10` | integer | Maximum cyclomatic complexity allowed | project |
| `prefer_type_hints` | `true` | boolean | Add type hints to function signatures | project |
| `error_handling_style` | `result_type` | string | Error handling approach (result_type/exceptions/both) | project |

### Task Management Settings

| Setting Key | Default Value | Type | Description | Scope |
|------------|---------------|------|-------------|-------|
| `task_granularity_default` | `medium` | string | Default task breakdown detail (low/medium/high) | project |
| `auto_create_task_items` | `true` | boolean | Automatically create items when task created | project |
| `task_naming_convention` | `verb_noun` | string | Task naming style (verb_noun/descriptive/user_choice) | project |
| `show_historical_context` | `true` | boolean | Show previous completed items for context | project |

### Display/Output Settings

| Setting Key | Default Value | Type | Description | Scope |
|------------|---------------|------|-------------|-------|
| `verbose_status_reports` | `false` | boolean | Include detailed information in status reports | project |
| `show_completion_estimates` | `true` | boolean | Display estimated completion percentages | project |
| `highlight_ambiguities` | `true` | boolean | Highlight unclear decisions in status | project |

---

## 2. Directive Preferences (Per-Directive)

**Table**: `directive_preferences`
**Structure**: `(directive_name, preference_key, preference_value, active, description)`

These settings are specific to individual directives and override global defaults.

---

### 2.1. Project Management Directives

#### `aifp_status`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `include_git_status` | `true` | boolean | Include git status in report |
| `show_priority_queue` | `true` | boolean | Show prioritized work queue |
| `max_historical_items` | `5` | integer | Number of previous completed items to show |
| `highlight_blockers` | `true` | boolean | Emphasize roadblocks and ambiguities |

#### `project_init`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `create_git_backup` | `true` | boolean | Create .git/.aifp backup on init |
| `auto_detect_language` | `true` | boolean | Automatically detect project language |
| `prompt_for_blueprint` | `true` | boolean | Ask for project blueprint details |

#### `project_task_decomposition`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `task_granularity` | `medium` | string | Level of task breakdown (low/medium/high) |
| `naming_convention` | `verb_noun` | string | Task naming style |
| `auto_create_items` | `true` | boolean | Auto-create items for each task |
| `default_priority` | `medium` | string | Default task priority |
| `max_tasks_per_milestone` | `10` | integer | Maximum tasks per milestone |
| `create_milestone_structure` | `true` | boolean | Auto-create milestone hierarchy |

#### `project_task_create`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `auto_create_items` | `true` | boolean | Auto-create items when task created |
| `require_description` | `true` | boolean | Require task description |
| `default_status` | `pending` | string | Initial task status |
| `assign_to_milestone` | `true` | boolean | Require milestone assignment |

#### `project_task_update`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `log_progress_changes` | `true` | boolean | Log task progress updates to notes |
| `notify_on_completion` | `true` | boolean | Alert when task becomes complete |

---

### 2.2. File & Code Management Directives

#### `project_file_write`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `always_add_docstrings` | `true` | boolean | Always add docstrings to functions |
| `max_function_length` | `50` | integer | Maximum function length in lines |
| `prefer_guard_clauses` | `true` | boolean | Use guard clauses over nested conditionals |
| `code_style` | `explicit` | string | Code style preference (explicit/implicit) |
| `indent_style` | `spaces_2` | string | Indentation style (spaces_2/spaces_4/tabs) |
| `add_type_hints` | `true` | boolean | Add type hints to function signatures |
| `line_length_limit` | `100` | integer | Maximum line length |
| `import_sorting` | `alphabetical` | string | Import sorting style (alphabetical/grouped/none) |
| `use_trailing_commas` | `true` | boolean | Use trailing commas in lists/dicts |

#### `project_file_read`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `include_context` | `true` | boolean | Include surrounding context when reading |
| `context_lines` | `10` | integer | Number of context lines before/after |

#### `project_file_delete`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `require_confirmation` | `true` | boolean | Ask for confirmation before deletion |
| `cleanup_database_refs` | `true` | boolean | Cleanup all database references |
| `create_backup` | `true` | boolean | Create backup before deletion |

---

### 2.3. Compliance & Validation Directives

#### `project_compliance_check`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `auto_check_enabled` | `false` | boolean | ⚠️ **NEW** - Run check after every file write |
| `auto_fix_violations` | `false` | boolean | Automatically fix FP violations |
| `skip_warnings` | `false` | boolean | Skip low-severity warnings |
| `strict_mode` | `false` | boolean | Enable strictest FP enforcement |
| `check_on_milestone_complete` | `true` | boolean | ⚠️ **NEW** - Quality gate before milestone completion |
| `report_format` | `detailed` | string | Report format (detailed/summary/minimal) |
| `fail_on_violations` | `false` | boolean | Fail operation if violations found |

**Related Global Setting**:
- `user_settings.fp_strictness_level` - Overrides per-check strictness

---

### 2.4. Analysis & Reporting Directives

#### `project_metrics`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `include_completion_percentage` | `true` | boolean | Show completion % |
| `include_task_distribution` | `true` | boolean | Show task breakdown |
| `include_compliance_score` | `false` | boolean | Show FP compliance score |
| `format` | `summary` | string | Report format (summary/detailed/json) |

#### `project_performance_summary`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `enabled` | `false` | boolean | ⚠️ **Requires tracking opt-in** - Enable performance tracking |
| `rolling_window_days` | `7` | integer | Days of history to include |
| `include_retry_counts` | `true` | boolean | Show retry statistics |
| `include_failure_reasons` | `true` | boolean | Show failure reason breakdown |

**IMPORTANT**: This directive requires `tracking_settings.helper_function_logging = 1` to function.

#### `project_error_handling`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `suggest_resolution` | `true` | boolean | Suggest error resolution strategies |
| `log_to_notes` | `true` | boolean | Log errors to project notes |
| `escalate_to_user` | `true` | boolean | Escalate unresolved errors to user |

---

### 2.5. Git Integration Directives

#### `git_detect_external_changes`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `run_on_session_start` | `true` | boolean | Always check on session start |
| `show_diff` | `true` | boolean | Show diff of external changes |
| `prompt_for_sync` | `true` | boolean | Ask if database should sync |

#### `git_detect_conflicts`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `auto_resolve_threshold` | `0.8` | float | Confidence threshold for auto-resolution (0-1) |
| `prefer_higher_purity` | `true` | boolean | Prefer code with higher FP purity in conflicts |
| `prefer_passing_tests` | `true` | boolean | Prefer code with passing tests |

#### `git_merge_branch`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `run_tests_after_merge` | `true` | boolean | Run tests after merging |
| `require_clean_working_tree` | `true` | boolean | Require clean tree before merge |

---

### 2.6. User Directive System (Use Case 2)

#### `user_directive_validate`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `validation_strictness` | `standard` | string | Validation level (relaxed/standard/strict) |
| `require_api_credentials` | `true` | boolean | Validate API credentials during Q&A |
| `check_for_conflicts` | `true` | boolean | Check for directive conflicts |

#### `user_directive_implement`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `code_generation_style` | `explicit` | string | Generated code style |
| `add_error_handling` | `true` | boolean | Add comprehensive error handling |
| `generate_tests` | `true` | boolean | Generate test files |
| `use_async` | `auto` | string | Use async/await (auto/always/never) |

---

### 2.7. User Preference Management

#### `user_preferences_learn`

| Preference Key | Default | Type | Description |
|---------------|---------|------|-------------|
| `enabled` | `false` | boolean | ⚠️ **Requires tracking opt-in** - Learn from corrections |
| `confidence_threshold` | `0.7` | float | Confidence to auto-apply learned preferences |
| `require_confirmation` | `true` | boolean | Ask before applying learned preferences |

**IMPORTANT**: Requires `tracking_settings.ai_interaction_log = 1` to function.

---

## 3. Tracking Settings (Feature Flags)

**Table**: `tracking_settings`
**Structure**: `(feature_name, enabled, description, estimated_token_overhead)`

All tracking features are **disabled by default** (opt-in only) to minimize API costs and respect user privacy.

### Tracking Features

| Feature Name | Default | Token Overhead | Description | Used By |
|--------------|---------|----------------|-------------|---------|
| `fp_flow_tracking` | `0` (disabled) | ~5% per file write | Track FP directive compliance over time | FP analysis |
| `issue_reports` | `0` (disabled) | ~2% on errors | Enable detailed issue report compilation | Error reporting |
| `ai_interaction_log` | `0` (disabled) | ~3% overall | Log all AI interactions for learning | `user_preferences_learn` |
| `helper_function_logging` | `0` (disabled) | ~1% on errors | Log helper function errors and execution details | `project_performance_summary` |

**Privacy Note**: Users should be warned about token overhead before enabling any tracking feature via `tracking_toggle` directive.

---

## 4. Settings Organization Summary

### By Category

**Total Settings**: 92+

| Category | User Settings | Directive Preferences | Tracking Flags |
|----------|--------------|---------------------|----------------|
| Core | 4 | - | - |
| Code Generation | 4 | - | - |
| Task Management | 4 | - | - |
| Display/Output | 3 | - | - |
| Project Management | - | 23 | - |
| File & Code | - | 16 | - |
| Compliance | - | 7 | - |
| Analysis & Reporting | - | 11 | - |
| Git Integration | - | 7 | - |
| User Directives | - | 6 | - |
| Preference Management | - | 3 | - |
| Tracking | - | - | 4 |
| **TOTAL** | **15** | **73** | **4** |

---

## 5. New Settings Added (vs. schemaExampleSettings.sql)

These settings were identified from recent gap analysis and workflow documentation work:

### User Settings
1. `auto_check_compliance` - Control compliance check frequency
2. `enable_git_hooks` - Enable/disable git integration
3. `milestone_quality_gates` - Quality gates at milestone completion
4. `default_docstring_style` - Docstring format
5. `max_function_complexity` - Complexity limit
6. `prefer_type_hints` - Type hint preference
7. `error_handling_style` - Error handling approach
8. `default_task_priority` - Default priority for tasks
9. `auto_create_task_items` - Auto-create items with tasks
10. `task_naming_convention` - Task naming style
11. `show_historical_context` - Show context in status
12. `verbose_status_reports` - Verbose status output
13. `show_completion_estimates` - Show completion %
14. `highlight_ambiguities` - Highlight unclear decisions

### Directive Preferences
1. `project_compliance_check.auto_check_enabled` - **Critical** - Control auto-check frequency
2. `project_compliance_check.check_on_milestone_complete` - Quality gate
3. `project_task_create.auto_create_items` - Auto-create items
4. `project_task_update.log_progress_changes` - Log updates
5. `project_task_update.notify_on_completion` - Completion alerts
6. `project_file_read.include_context` - Context when reading
7. `project_file_delete.require_confirmation` - Deletion safety
8. `aifp_status.*` - All aifp_status preferences (4 new)
9. `project_init.*` - All project_init preferences (3 new)
10. `git_detect_external_changes.*` - All git_detect preferences (3 new)
11. `git_detect_conflicts.*` - Conflict resolution preferences (3 new)
12. `git_merge_branch.*` - Merge preferences (2 new)

---

## 6. Settings That Should NOT Exist

Based on gap analysis review, these settings from the old schema may not be appropriate:

### Questionable Settings
- None of the old settings are problematic, but some are now redundant with new organization

---

## 7. Implementation Priorities

### Phase 1: Critical Settings (Immediate)
1. `auto_check_compliance` (user_settings) - Compliance check frequency
2. `project_compliance_check.auto_check_enabled` - Per-directive override
3. `project_compliance_check.check_on_milestone_complete` - Quality gates
4. `project_task_create.auto_create_items` - Task/item workflow

### Phase 2: High Priority (Week 1)
1. All `project_file_write` preferences (code style)
2. All `project_task_decomposition` preferences (task management)
3. `aifp_status` preferences (status reporting)
4. `git_detect_external_changes` preferences (git integration)

### Phase 3: Medium Priority (Week 2-3)
1. All file management preferences (read/delete)
2. All compliance preferences (beyond auto-check)
3. Analysis and reporting preferences
4. User directive system preferences

### Phase 4: Low Priority (Later)
1. Display/output preferences
2. Advanced git preferences
3. Performance tracking preferences (requires tracking opt-in)

---

## 8. Migration from Old Schema

**Changes Needed**:

### Additions to user_settings
```sql
INSERT INTO user_settings (setting_key, setting_value, description) VALUES
  ('auto_check_compliance', 'false', 'Run FP compliance check after every file write'),
  ('enable_git_hooks', 'true', 'Enable git integration and hooks'),
  ('milestone_quality_gates', 'true', 'Require compliance checks before milestone completion'),
  ('default_docstring_style', 'google', 'Docstring format (google/numpy/sphinx/none)'),
  ('max_function_complexity', '10', 'Maximum cyclomatic complexity allowed'),
  ('prefer_type_hints', 'true', 'Add type hints to function signatures'),
  ('error_handling_style', 'result_type', 'Error handling approach (result_type/exceptions/both)'),
  ('default_task_priority', 'medium', 'Default priority for new tasks'),
  ('auto_create_task_items', 'true', 'Automatically create items when task created'),
  ('task_naming_convention', 'verb_noun', 'Task naming style'),
  ('show_historical_context', 'true', 'Show previous completed items for context'),
  ('verbose_status_reports', 'false', 'Include detailed information in status reports'),
  ('show_completion_estimates', 'true', 'Display estimated completion percentages'),
  ('highlight_ambiguities', 'true', 'Highlight unclear decisions in status');
```

### Additions to directive_preferences
```sql
-- Critical additions
INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description) VALUES
  ('project_compliance_check', 'auto_check_enabled', 'false', 'Run compliance check after every file write'),
  ('project_compliance_check', 'check_on_milestone_complete', 'true', 'Quality gate before milestone completion'),
  ('project_task_create', 'auto_create_items', 'true', 'Auto-create items when task created'),

-- See full specification above for remaining 70+ preferences
```

---

## 9. Usage Examples

### User Requests Preference Change
```
User: "Always add docstrings when writing files"
AI: Calls user_preferences_update
    → Inserts: ('project_file_write', 'always_add_docstrings', 'true')
    → Confirms: "I'll now always add docstrings when writing files."
```

### Directive Loads Preferences
```
AI: About to execute project_file_write
    → Calls user_preferences_sync('project_file_write')
    → Loads all active preferences for that directive
    → Applies: always_add_docstrings=true, max_function_length=50, etc.
    → Writes file with preferences applied
```

### User Enables Tracking
```
User: "Enable performance tracking"
AI: Calls tracking_toggle('helper_function_logging')
    → Shows: "This will increase token usage by ~1%"
    → User confirms
    → Updates: tracking_settings.helper_function_logging = 1
    → Confirms: "Performance tracking enabled"
```

---

## 10. Validation & Constraints

### Setting Value Validation

**Boolean Settings**:
- Valid values: `'true'`, `'false'`, `'1'`, `'0'`

**Enum Settings**:
- `task_granularity`: low, medium, high
- `naming_convention`: verb_noun, descriptive, user_choice
- `code_style`: explicit, implicit
- `indent_style`: spaces_2, spaces_4, tabs
- `docstring_style`: google, numpy, sphinx, none
- `error_handling_style`: result_type, exceptions, both
- `strictness_level`: relaxed, standard, strict

**Integer Settings**:
- Must be positive integers
- Reasonable ranges enforced (e.g., max_function_length: 10-200)

**Float Settings**:
- Range: 0.0 - 1.0 for confidence/threshold values

---

## Appendix A: Quick Reference Tables

### Most Commonly Used Settings

| Setting | Location | Default | Impact |
|---------|----------|---------|--------|
| `auto_check_compliance` | user_settings | false | Controls compliance check frequency |
| `project_file_write.always_add_docstrings` | directive_preferences | true | Adds docstrings to all functions |
| `project_task_create.auto_create_items` | directive_preferences | true | Items auto-created with tasks |
| `project_compliance_check.auto_fix_violations` | directive_preferences | false | Auto-fix FP violations |
| `fp_strictness_level` | user_settings | standard | Global FP strictness |
| `helper_function_logging` | tracking_settings | 0 | Performance tracking opt-in |

---

## Appendix B: Settings by Directive

See Section 2 for complete per-directive preferences organized by directive category.

---

**Document Version**: 2.0
**Created**: 2025-12-18
**Replaces**: `docs/db-schema/schemaExampleSettings.sql` (v1.0)
**Next Steps**:
1. Review and approve specification
2. Update database schema files
3. Generate migration SQL
4. Update helper JSON files with preference references
5. Update system prompt with settings guidance

---

**Status**: ✅ Ready for Review

# Settings Analysis Report: Valid vs. Made-Up Settings

**Date**: 2026-01-04
**Purpose**: Compare settings actually referenced in directives vs. settings listed in COMPREHENSIVE_SETTINGS_SPEC.md
**Status**: Critical - Many documented settings are not used anywhere

---

## Executive Summary

**Critical Finding**: Out of 92+ settings documented in `COMPREHENSIVE_SETTINGS_SPEC.md`, only **18 settings** are actually referenced in directive JSON/MD files.

**Recommendation**: Drastically reduce settings to only those that:
1. Are actually referenced by directives
2. Modify directive behavior in meaningful ways
3. Are not trying to override locked database schema values

---

## 1. SETTINGS ACTUALLY USED IN DIRECTIVES (18 total)

These settings are **confirmed valid** - they are referenced in directive workflows:

### Global User Settings (3)
1. **fp_strictness_level** - Used by `project_compliance_check`, `project_init`
2. **prefer_explicit_returns** - Used by FP directives during code generation
3. **suppress_warnings** - Used to filter warnings from various directives

### Directive Preferences (11)

#### project_file_write (5)
1. **always_add_docstrings** - Auto-add docstrings to functions
2. **max_function_length** - Warn if function exceeds N lines
3. **prefer_guard_clauses** - Use guard clauses vs nested ifs
4. **code_style** - Overall coding style (compact/verbose/explicit)
5. **indent_style** - Indentation preference (spaces_2/spaces_4/tabs)

#### project_task_decomposition (4)
1. **task_granularity** - Task breakdown detail (fine/medium/coarse)
2. **naming_convention** - How to name tasks (descriptive/short/numbered)
3. **auto_create_items** - Auto-create items for tasks
4. **default_priority** - Default priority for new tasks (1-5)

#### project_compliance_check (3)
1. **auto_fix_violations** - Auto-refactor FP violations
2. **skip_warnings** - Ignore non-critical warnings
3. **strict_mode** - Zero-tolerance FP enforcement

### Tracking Features (4)
1. **fp_flow_tracking** - Track FP directive usage
2. **ai_interaction_log** - Log user corrections for learning
3. **helper_function_logging** - Log directive execution
4. **issue_reports** - Enable bug report compilation

---

## 2. SETTINGS IN SPEC BUT NOT IN DIRECTIVES (74+ settings)

These settings are **documented but unused** - they do NOT appear in any directive workflows:

### User Settings (12 unused)
1. ❌ **default_task_priority** - Duplicate of directive pref, not referenced
2. ❌ **auto_check_compliance** - Not checked by any directive
3. ❌ **enable_git_hooks** - Not checked by git directives
4. ❌ **milestone_quality_gates** - Not checked by milestone directives
5. ❌ **default_docstring_style** - Not checked by file_write
6. ❌ **max_function_complexity** - Not checked (different from max_function_length)
7. ❌ **prefer_type_hints** - Not checked by file_write
8. ❌ **error_handling_style** - Not checked by any directive
9. ❌ **task_granularity_default** - ⚠️ **INVALID** - Tries to set schema-locked priority values
10. ❌ **auto_create_task_items** - Duplicate of directive pref
11. ❌ **task_naming_convention** - Duplicate of directive pref
12. ❌ **show_historical_context** - Not checked by aifp_status
13. ❌ **verbose_status_reports** - Not checked by aifp_status
14. ❌ **show_completion_estimates** - Not checked by aifp_status
15. ❌ **highlight_ambiguities** - Not checked by aifp_status

### Directive Preferences (62 unused)

#### aifp_status (4 unused)
- ❌ **include_git_status** - Not in workflow
- ❌ **show_priority_queue** - Not in workflow
- ❌ **max_historical_items** - Not in workflow
- ❌ **highlight_blockers** - Not in workflow

#### project_init (3 unused)
- ❌ **create_git_backup** - Not in workflow
- ❌ **auto_detect_language** - Not in workflow
- ❌ **prompt_for_blueprint** - Not in workflow

#### project_task_decomposition (2 unused)
- ❌ **max_tasks_per_milestone** - Not in workflow
- ❌ **create_milestone_structure** - Not in workflow

#### project_task_create (4 unused)
- ❌ **auto_create_items** - Not in workflow
- ❌ **require_description** - Not in workflow
- ❌ **default_status** - Not in workflow
- ❌ **assign_to_milestone** - Not in workflow

#### project_task_update (2 unused)
- ❌ **log_progress_changes** - Not in workflow
- ❌ **notify_on_completion** - Not in workflow

#### project_file_write (4 unused)
- ❌ **add_type_hints** - Not in workflow
- ❌ **line_length_limit** - Not in workflow
- ❌ **import_sorting** - Not in workflow
- ❌ **use_trailing_commas** - Not in workflow

#### project_file_read (2 unused)
- ❌ **include_context** - Not in workflow
- ❌ **context_lines** - Not in workflow

#### project_file_delete (3 unused)
- ❌ **require_confirmation** - Not in workflow
- ❌ **cleanup_database_refs** - Not in workflow
- ❌ **create_backup** - Not in workflow

#### project_compliance_check (4 unused)
- ❌ **auto_check_enabled** - ⚠️ Critical setting but not in workflow
- ❌ **check_on_milestone_complete** - ⚠️ Critical setting but not in workflow
- ❌ **report_format** - Not in workflow
- ❌ **fail_on_violations** - Not in workflow

#### project_metrics (4 unused)
- ❌ **include_completion_percentage** - Not in workflow
- ❌ **include_task_distribution** - Not in workflow
- ❌ **include_compliance_score** - Not in workflow
- ❌ **format** - Not in workflow

#### project_performance_summary (4 unused)
- ❌ **enabled** - Not in workflow
- ❌ **rolling_window_days** - Not in workflow
- ❌ **include_retry_counts** - Not in workflow
- ❌ **include_failure_reasons** - Not in workflow

#### project_error_handling (3 unused)
- ❌ **suggest_resolution** - Not in workflow
- ❌ **log_to_notes** - Not in workflow
- ❌ **escalate_to_user** - Not in workflow

#### git_detect_external_changes (3 unused)
- ❌ **run_on_session_start** - Not in workflow
- ❌ **show_diff** - Not in workflow
- ❌ **prompt_for_sync** - Not in workflow

#### git_detect_conflicts (3 unused)
- ❌ **auto_resolve_threshold** - Not in workflow
- ❌ **prefer_higher_purity** - Not in workflow
- ❌ **prefer_passing_tests** - Not in workflow

#### git_merge_branch (2 unused)
- ❌ **run_tests_after_merge** - Not in workflow
- ❌ **require_clean_working_tree** - Not in workflow

#### user_directive_validate (3 unused)
- ❌ **validation_strictness** - Not in workflow
- ❌ **require_api_credentials** - Not in workflow
- ❌ **check_for_conflicts** - Not in workflow

#### user_directive_implement (4 unused)
- ❌ **code_generation_style** - Not in workflow
- ❌ **add_error_handling** - Not in workflow
- ❌ **generate_tests** - Not in workflow
- ❌ **use_async** - Not in workflow

#### user_preferences_learn (3 unused)
- ❌ **enabled** - Not in workflow
- ❌ **confidence_threshold** - Not in workflow
- ❌ **require_confirmation** - Not in workflow

---

## 3. ANALYSIS OF SPECIFIC PROBLEMATIC SETTINGS

### task_granularity_default (INVALID)

**Problem**: This setting appears to control task priority, but task priority is defined in the database schema:

```sql
-- From project.sql line 175
priority TEXT DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical'))
```

**Why it's invalid**:
- Schema defines 4 allowed priority values: low, medium, high, critical
- Schema is locked and cannot be modified by AI or settings
- This setting can't actually change priority values
- It's confusing the concepts of "task granularity" (breakdown detail) and "priority" (importance)

**Correct Interpretation**:
- If this is meant to control default priority → use `default_priority` (already exists as directive pref)
- If this is meant to control task breakdown detail → use `task_granularity` (already exists as directive pref)
- Either way, this setting is redundant

**Recommendation**: Delete this setting entirely

### auto_check_compliance (POTENTIALLY VALID but unused)

**Current Status**: Documented in spec, marked as "critical", but **not checked by any directive**

**Intended Purpose**: Run compliance check after every file write

**Problem**: The `project_file_write` directive doesn't check this setting in its workflow

**Recommendation**:
- Option 1: Add to `project_file_write` workflow as optional quality gate
- Option 2: Remove from spec if not actually needed

### check_on_milestone_complete (POTENTIALLY VALID but unused)

**Current Status**: Documented as "critical quality gate" but **not checked by milestone directives**

**Intended Purpose**: Require compliance check before milestone completion

**Problem**: The `project_milestone_complete` directive doesn't check this setting

**Recommendation**:
- Option 1: Add to `project_milestone_complete` workflow
- Option 2: Remove from spec if not actually needed

---

## 4. RECOMMENDATIONS

### Phase 1: Immediate Cleanup (Delete 60+ settings)

**Delete all unused settings from COMPREHENSIVE_SETTINGS_SPEC.md that are not referenced in directives**

Keep only these 18:
- Global: fp_strictness_level, prefer_explicit_returns, suppress_warnings
- project_file_write: always_add_docstrings, max_function_length, prefer_guard_clauses, code_style, indent_style
- project_task_decomposition: task_granularity, naming_convention, auto_create_items, default_priority
- project_compliance_check: auto_fix_violations, skip_warnings, strict_mode
- Tracking: fp_flow_tracking, ai_interaction_log, helper_function_logging, issue_reports

### Phase 2: Add Settings as Needed (Dynamic approach)

**Follow the user's vision**: Settings should be created dynamically as AI interacts with users

**Process**:
1. User expresses preference: "Always add type hints"
2. AI calls `user_preferences_update`
3. AI identifies relevant directive: `project_file_write`
4. AI creates new preference: `project_file_write.always_add_type_hints = true`
5. **THEN** update directive workflow to check this setting
6. **THEN** document the setting

**DO NOT**: Pre-create dozens of settings "that might be useful"

### Phase 3: Integration Strategy

**How settings should be called**:

1. **At directive execution time** - Settings loaded via `user_preferences_sync`
2. **Before directive execution** - Check if preferences exist for this directive
3. **Conditional execution** - Only if preferences exist, modify behavior

**Example workflow (project_file_write)**:
```json
{
  "trunk": "prepare_file_write",
  "branches": [
    {
      "condition": "directive_preferences_exist",
      "action": "load_preferences",
      "query": "SELECT preference_key, preference_value FROM directive_preferences WHERE directive_name='project_file_write' AND active=1",
      "apply": "modify_code_generation_behavior"
    },
    {
      "fallback": "use_defaults"
    }
  ]
}
```

**Where to integrate**:
- Every "customizable" directive should have a branch that loads preferences
- Settings are applied to modify directive behavior
- No settings = default behavior

---

## 5. REVISED SETTINGS SPECIFICATION

### Minimal Valid Settings List (18 total)

**user_settings table**:
```sql
INSERT INTO user_settings (setting_key, setting_value, description) VALUES
  ('fp_strictness_level', '{"level": "standard", "exceptions": []}', 'FP enforcement level'),
  ('prefer_explicit_returns', 'true', 'Always use explicit returns'),
  ('suppress_warnings', '[]', 'Directives to suppress warnings from');
```

**directive_preferences table**:
```sql
-- project_file_write
INSERT INTO directive_preferences (directive_name, preference_key, preference_value, description) VALUES
  ('project_file_write', 'always_add_docstrings', 'false', 'Auto-add docstrings'),
  ('project_file_write', 'max_function_length', '50', 'Max lines per function'),
  ('project_file_write', 'prefer_guard_clauses', 'false', 'Use guard clauses'),
  ('project_file_write', 'code_style', 'explicit', 'Code style preference'),
  ('project_file_write', 'indent_style', 'spaces_2', 'Indentation style'),

-- project_task_decomposition
  ('project_task_decomposition', 'task_granularity', 'medium', 'Task breakdown detail'),
  ('project_task_decomposition', 'naming_convention', 'descriptive', 'Task naming style'),
  ('project_task_decomposition', 'auto_create_items', 'true', 'Auto-create items'),
  ('project_task_decomposition', 'default_priority', '3', 'Default task priority'),

-- project_compliance_check
  ('project_compliance_check', 'auto_fix_violations', 'false', 'Auto-fix violations'),
  ('project_compliance_check', 'skip_warnings', 'false', 'Skip warnings'),
  ('project_compliance_check', 'strict_mode', 'false', 'Strict enforcement');
```

**tracking_settings table**:
```sql
INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
  ('fp_flow_tracking', 0, 'Track FP directive usage', '~5% per file write'),
  ('ai_interaction_log', 0, 'Log user corrections', '~3% overall'),
  ('helper_function_logging', 0, 'Log helper execution', '~1% on errors'),
  ('issue_reports', 0, 'Enable bug reports', '~2% on errors');
```

---

## 6. NEXT STEPS

1. ✅ **This document** - Analysis complete
2. ⏳ **Update COMPREHENSIVE_SETTINGS_SPEC.md** - Remove unused settings
3. ⏳ **Update user_preferences.sql schema** - Remove invalid settings
4. ⏳ **Review directive workflows** - Add preference checks where needed
5. ⏳ **Document dynamic setting creation** - User preference workflow
6. ⏳ **Update system prompt** - Guide AI on when to check settings

---

**Status**: ✅ Analysis Complete
**Recommendation**: Proceed with Phase 1 cleanup immediately

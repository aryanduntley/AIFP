# Settings Phase 5: Documentation Updates Needed

**Date**: 2026-01-07
**Status**: Analysis Complete - Ready for Updates
**Based on**: settings-specification.json v3.1 (12 settings baseline)

---

## Overview

Phase 2 completed a major settings cleanup:
- **Removed**: 6 settings (5 FP compliance + 1 task_granularity)
- **Added**: 1 setting (project_continue_on_start)
- **Result**: 18 settings → 12 settings

This document identifies all files that need updates to reflect the new baseline.

---

## Changes from Phase 2 (v3.1)

### Settings REMOVED:
1. ❌ `fp_strictness_level` (global) - FP is baseline, not optional
2. ❌ `prefer_explicit_returns` (global) - Redundant with system prompt
3. ❌ `project_compliance_check.auto_fix_violations` - Directive repurposed as tracking-only
4. ❌ `project_compliance_check.skip_warnings` - Directive repurposed as tracking-only
5. ❌ `project_compliance_check.strict_mode` - Directive repurposed as tracking-only
6. ❌ `project_task_decomposition.task_granularity` - Tried to override locked schema values

### Settings ADDED:
1. ✅ `project_continue_on_start` (global) - Autostart setting from system prompt

### Tracking Feature ADDED:
1. ✅ `compliance_checking` - 5th tracking feature (enables project_compliance_check directive)

---

## Files Requiring Updates

### 1. docs/directives-json/directives-user-pref.json

**Location**: Line 552 (tracking_toggle directive fallback prompt)

**Current**:
```json
{
  "fallback": "prompt_user",
  "details": {
    "clarify": "Which tracking feature? Options: fp_flow_tracking, issue_reports, ai_interaction_log, helper_function_logging"
  }
}
```

**Issue**: Missing `compliance_checking` tracking feature

**Fix**:
```json
{
  "fallback": "prompt_user",
  "details": {
    "clarify": "Which tracking feature? Options: fp_flow_tracking, issue_reports, ai_interaction_log, helper_function_logging, compliance_checking"
  }
}
```

---

### 2. docs/directives-json/directive_flow_user_preferences.json

**Issue 1**: Missing `compliance_checking` in tracking features list

**Location**: Lines 214-220

**Current**:
```json
"tracking_features": [
  "fp_flow_tracking - Track FP directive consultations",
  "ai_interaction_log - Log user corrections and feedback",
  "helper_function_logging - Log directive execution performance",
  "issue_reports - Log errors and roadblocks"
]
```

**Fix**: Add compliance_checking:
```json
"tracking_features": [
  "fp_flow_tracking - Track FP directive consultations",
  "ai_interaction_log - Log user corrections and feedback",
  "helper_function_logging - Log directive execution performance",
  "issue_reports - Log errors and roadblocks",
  "compliance_checking - Track FP compliance patterns (opt-in analytics)"
]
```

---

**Issue 2**: Missing `compliance_checking` in privacy_and_tracking section

**Location**: Lines 331-361

**Fix**: Add new tracking feature entry:
```json
"compliance_checking": {
  "description": "Track FP compliance patterns over time (analytics, NOT validation)",
  "database": "user_preferences.db",
  "table": "tracking_settings",
  "purpose": "Optional analytics for FP compliance patterns (audits, research, education)",
  "enabled_by": "tracking_toggle directive",
  "activates": "project_compliance_check directive (tracking-only)",
  "note": "FP compliance is baseline behavior. This tracks patterns, not validates code."
}
```

---

**Issue 3**: Outdated project_compliance_check preferences listed

**Location**: Lines 386-395

**Current**:
```json
"fp_compliance": {
  "description": "FP compliance checking respects user preferences",
  "directive": "project_compliance_check",
  "preferences": [
    "auto_fix_violations - Auto-fix FP violations vs. report only",
    "skip_warnings - Skip warning-level issues",
    "strict_mode - Strictest FP enforcement",
    "fp_strictness_level - Low/medium/high strictness"
  ],
  "flow_location": "directive_flow_project.json (already implemented)"
}
```

**Fix**: Update to reflect tracking-only purpose:
```json
"fp_compliance": {
  "description": "FP compliance checking is opt-in tracking feature (NOT validation)",
  "directive": "project_compliance_check",
  "type": "tracking_only",
  "activation": "tracking_settings.compliance_checking = enabled",
  "preferences": [],
  "note": "No preferences - this is an analytics directive. FP compliance is baseline behavior enforced by system prompt.",
  "flow_location": "directive_flow_project.json"
}
```

---

### 3. src/aifp/reference/directives/user_preferences_sync.md

**Issue 1**: Outdated default user_settings in initialization example

**Location**: Lines 96-102

**Current**:
```sql
INSERT INTO user_settings (setting_key, setting_value, description) VALUES
  ('fp_strictness_level', '{"level": "standard", "exceptions": []}', 'FP enforcement strictness'),
  ('prefer_explicit_returns', 'true', 'Always use explicit returns'),
  ('suppress_warnings', '[]', 'Directives to suppress warnings');
```

**Fix**: Remove fp_strictness_level and prefer_explicit_returns:
```sql
INSERT INTO user_settings (setting_key, setting_value, description, scope) VALUES
  ('project_continue_on_start', 'false', 'Automatically continue project work on session start', 'project'),
  ('suppress_warnings', '[]', 'Directives to suppress warnings', 'project');
```

---

**Issue 2**: Missing `compliance_checking` in tracking_settings initialization

**Location**: Lines 103-110

**Current**:
```sql
INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
  ('fp_flow_tracking', 0, 'Track FP compliance', '~5% token increase per file write'),
  ('issue_reports', 0, 'Enable issue reports', '~2% token increase on errors'),
  ('ai_interaction_log', 0, 'Log AI interactions', '~3% token increase overall'),
  ('helper_function_logging', 0, 'Log helper errors', '~1% token increase on errors');
```

**Fix**: Add compliance_checking:
```sql
INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
  ('fp_flow_tracking', 0, 'Track FP directive consultations', '~5% token increase per file write'),
  ('issue_reports', 0, 'Enable issue reports', '~2% token increase on errors'),
  ('ai_interaction_log', 0, 'Log AI interactions', '~3% token increase overall'),
  ('helper_function_logging', 0, 'Log helper errors', '~1% token increase on errors'),
  ('compliance_checking', 0, 'Track FP compliance patterns (analytics, NOT validation)', '~5-10% token increase per check');
```

---

**Issue 3**: Outdated example showing fp_strictness_level usage

**Location**: Lines 243-270

**Current**:
```python
# User set global FP strictness to "strict"
# user_settings table:
# - fp_strictness_level: {"level": "strict", "exceptions": []}

# AI calls: user_preferences_sync(directive_name="project_compliance_check")

# Workflow:
# 1. check_preferences_db: ✓ Exists
# 2. load_preferences:
#    - Directive preferences: None specific to project_compliance_check
#    - User settings: fp_strictness_level = {"level": "strict"}
# 3. apply_to_context:
#    context = {
#      "user_settings": {
#        "fp_strictness_level": {"level": "strict", "exceptions": []}
#      },
#      "preferences": {}
#    }
# 4. Project_compliance_check reads fp_strictness_level
#    → Applies strict FP enforcement (zero tolerance)
```

**Fix**: Replace with different example (e.g., project_continue_on_start or suppress_warnings):
```python
# User enabled autostart
# user_settings table:
# - project_continue_on_start: true

# AI calls: user_preferences_sync(directive_name="aifp_run")

# Workflow:
# 1. check_preferences_db: ✓ Exists
# 2. load_preferences:
#    - User settings: project_continue_on_start = "true"
# 3. apply_to_context:
#    context = {
#      "user_settings": {
#        "project_continue_on_start": True
#      },
#      "preferences": {}
#    }
# 4. aifp_run checks project_continue_on_start
#    → Automatically continues project work with context and state
```

---

### 4. src/aifp/reference/directives/user_preferences_import.md

**Issue**: Examples show fp_strictness_level in user_settings

**Location**: Lines 32-37 (export format example)

**Current**:
```json
"user_settings": [
  {"key": "fp_strictness_level", "value": "{\"level\": \"strict\"}", "description": "..."}
]
```

**Fix**: Use a valid setting instead:
```json
"user_settings": [
  {"key": "project_continue_on_start", "value": "true", "description": "Automatically continue project work on session start"},
  {"key": "suppress_warnings", "value": "[]", "description": "Directives to suppress warnings"}
]
```

---

### 5. src/aifp/reference/directives/user_preferences_update.md

**Issue 1**: Example shows setting FP strictness (outdated)

**Location**: Lines 344-377

**Current**:
```python
# User: "Enable strict FP mode"
# AI calls: user_preferences_update()

# Workflow:
# 1. parse_preference_request:
#    - Intent: "enable strict FP mode"
#    - Global setting (not directive-specific)
#
# 2. find_directive_by_intent("strict FP mode", 0.6):
#    - Matches: project_compliance_check (0.88)
```

**Fix**: Update to reflect that FP is baseline, not configurable:
```python
# User: "Enable autostart on session begin"
# AI calls: user_preferences_update()

# Workflow:
# 1. parse_preference_request:
#    - Intent: "enable autostart"
#    - Global setting (not directive-specific)
#
# 2. Identify user_settings target:
#    - Key: project_continue_on_start
#    - Value: true
#
# 3. Update user_settings:
#    UPDATE user_settings
#    SET setting_value = 'true'
#    WHERE setting_key = 'project_continue_on_start'
#
# Result:
# ✅ Autostart enabled
# ✅ Next session will automatically continue project work
```

OR keep the example but redirect to compliance_checking tracking:
```python
# User: "I want to track FP compliance patterns"
# AI calls: user_preferences_update()

# Workflow:
# 1. parse_preference_request:
#    - Intent: "track FP compliance patterns"
#    - This is a tracking feature request
#
# 2. Redirect to tracking_toggle directive:
#    - Inform user: "This is a tracking feature. Let me enable it for you."
#    - Call: tracking_toggle(feature_name="compliance_checking", enable=True)
#    - Show token overhead warning
#
# 3. User confirms token overhead
#
# 4. Enable tracking:
#    UPDATE tracking_settings
#    SET enabled = 1
#    WHERE feature_name = 'compliance_checking'
#
# Result:
# ✅ Compliance tracking enabled
# ✅ project_compliance_check directive now available for analytics
```

---

## Files Already Correct

### ✅ docs/directives-json/directives-project.json

**Status**: CORRECT - project_compliance_check already updated

**Lines 877-949**: project_compliance_check correctly reflects:
- Type: "tracking" (line 878)
- Activation requirement: tracking_settings.compliance_checking (line 881)
- Description: OPTIONAL analytics, NOT validation (line 887)
- Workflow: Checks tracking_enabled first (lines 890-900)

No changes needed.

---

### ✅ docs/settings-specification.json

**Status**: CORRECT - v3.1 baseline

Contains correct 12-setting baseline with:
- Removed: FP compliance settings
- Added: project_continue_on_start, compliance_checking tracking
- Updated: All references and notes

No changes needed.

---

### ✅ docs/settings-cleanup-summary.md

**Status**: CORRECT - Phase 2 complete

Documents all Phase 2 changes correctly. No updates needed.

---

### ✅ docs/settings-design-integration.md

**Status**: MOSTLY CORRECT

May need minor updates to examples that reference fp_strictness_level, but overall design is accurate.

---

## Summary of Required Updates

### High Priority (User-facing directives):
1. ✅ **directives-user-pref.json** - Add compliance_checking to tracking_toggle prompt
2. ✅ **directive_flow_user_preferences.json** - Add compliance_checking, remove outdated preferences
3. ✅ **user_preferences_sync.md** - Update default settings, remove FP settings examples
4. ✅ **user_preferences_import.md** - Update examples to use valid settings
5. ✅ **user_preferences_update.md** - Update examples to reflect FP baseline

### Medium Priority (Reference documentation):
6. ⚠️ **settings-design-integration.md** - Update examples if they reference removed settings
7. ⚠️ Other MD files - Scan for fp_strictness_level, auto_fix_violations, etc. references

### Already Complete:
- ✅ directives-project.json (project_compliance_check correctly updated)
- ✅ settings-specification.json (v3.1 baseline correct)
- ✅ settings-cleanup-summary.md (Phase 2 documented)

---

## Verification Checklist

After updates, verify:

- [ ] All references to removed settings are updated or removed
- [ ] compliance_checking tracking feature is documented consistently across all files
- [ ] project_compliance_check is described as tracking-only, not validation
- [ ] Examples use valid settings from v3.1 baseline
- [ ] No directives check for removed settings in workflows
- [ ] Tracking features list matches across all files (5 total)
- [ ] User_settings initialization only includes valid settings

---

## Next Steps

1. **Update the 5 high-priority files listed above**
2. **Verify consistency across all directive documentation**
3. **Test that no code references removed settings**
4. **Update AIFP system prompt if it references removed settings**

---

**Status**: Ready for implementation
**Phase**: 5 (Documentation Cleanup)
**Last Updated**: 2026-01-07

# Settings Directive Comprehensive Review - Issues Found

**Date**: 2026-01-07
**Status**: Issues Identified - Fixes Required
**Scope**: All directive JSON and MD files

---

## Executive Summary

Comprehensive review found **11 remaining references** to removed settings across 6 files that require correction.

### Issues Found:
- **2 JSON files** with outdated settings
- **5 MD files** with outdated settings in examples
- **0 files** missing compliance_checking references

---

## Critical Issues (JSON Files)

### 1. ❌ docs/directives-json/directive_flow_user_preferences.json

**Location**: Line 45
**Issue**: Example list still references removed project_compliance_check preferences

**Current**:
```json
"examples": [
  "project_file_write: code style, docstrings, naming conventions",
  "project_task_create: task granularity, default priorities",
  "project_compliance_check: auto_fix_violations, strict_mode",  ← REMOVE THIS LINE
  "user_directive_validate: validation strictness",
  "user_directive_implement: code generation preferences"
]
```

**Fix**: Remove line 45 entirely (project_compliance_check has no preferences)

**Reasoning**: project_compliance_check is now tracking-only with no preferences

---

### 2. ❌ docs/directives-json/directives-project.json

**Location 1**: Line 215
**Issue**: project_init workflow prompts for removed fp_strictness_level setting

**Current**:
```json
"prompts": [
  "project_name",
  "purpose",
  "goals",
  "language",
  "build_tool",
  "fp_strictness_level"  ← REMOVE THIS
]
```

**Fix**: Remove "fp_strictness_level" from prompts array

**Reasoning**: fp_strictness_level setting was removed in v3.1 (FP is baseline, not configurable)

---

**Location 2**: Line 422
**Issue**: project_task_decomposition workflow lists task_granularity as preference

**Current**:
```json
"common_preferences": [
  "task_granularity",  ← REMOVE THIS
  "naming_convention",
  "auto_create_items",
  "default_priority"
]
```

**Fix**: Remove "task_granularity" from common_preferences array

**Reasoning**: task_granularity was removed in v3.1 (tried to override locked schema values)

---

## Medium Priority Issues (MD Files)

### 3. ❌ src/aifp/reference/directives/user_preferences_export.md

**Location 1**: Lines 36-38
**Issue**: Export format example shows removed fp_strictness_level

**Current**:
```json
"user_settings": [
  {
    "key": "fp_strictness_level",
    "value": "{\"level\": \"strict\", \"exceptions\": []}",
    "description": "How strict to enforce FP directives"
  }
]
```

**Fix**: Replace with valid settings (project_continue_on_start, suppress_warnings)

---

**Location 2**: Lines 264-266
**Issue**: Example comment shows removed settings

**Current**:
```python
#      "user_settings": [
#        {"key": "fp_strictness_level", "value": "...", "description": "..."},
#        {"key": "prefer_explicit_returns", "value": "true", "description": "..."},
#        {"key": "suppress_warnings", "value": "[]", "description": "..."}
#      ],
```

**Fix**: Remove first two lines, keep only suppress_warnings

---

### 4. ❌ src/aifp/reference/directives/user_preferences_learn.md

**Location**: Line 111
**Issue**: Example shows prefer_explicit_returns as learnable preference

**Current**:
```python
    - **Docstrings**: 3+ corrections adding docstrings → Preference: `always_add_docstrings`
    - **Guard clauses**: 3+ corrections converting nested if to guards → Preference: `prefer_guard_clauses`
    - **Explicit returns**: 3+ corrections adding explicit returns → Preference: `prefer_explicit_returns`  ← REMOVE
    - **Indentation**: 3+ corrections changing spaces → Preference: `indent_style`
```

**Fix**: Remove the "Explicit returns" line

**Reasoning**: prefer_explicit_returns is no longer a setting (FP baseline requires explicit returns)

---

### 5. ❌ src/aifp/reference/directives/user_preferences_sync.md

**Location**: Lines 132-133
**Issue**: Example context shows removed settings

**Current**:
```python
"user_settings": {
  "fp_strictness_level": {"level": "standard", "exceptions": []},
  "prefer_explicit_returns": True
}
```

**Fix**: This is in the docstring example at lines 122-135. Replace with valid settings.

**Corrected Example**:
```python
context = {
  "directive_name": "project_file_write",
  "preferences": {
    "always_add_docstrings": True,
    "max_function_length": 50,
    "prefer_guard_clauses": True,
    "code_style": "explicit",
    "indent_style": "spaces_2"
  },
  "user_settings": {
    "project_continue_on_start": False,
    "suppress_warnings": []
  }
}
```

---

### 6. ❌ src/aifp/reference/directives/user_preferences_update.md

**Location**: Line 575
**Issue**: Database operations section mentions fp_strictness_level as example

**Current**:
```markdown
- **`user_settings`**: UPDATE for global preferences (e.g., fp_strictness_level)
```

**Fix**: Replace with valid setting example

**Corrected**:
```markdown
- **`user_settings`**: UPDATE for global preferences (e.g., project_continue_on_start, suppress_warnings)
```

---

### 7. ❌ src/aifp/reference/directives/user_preferences_import.md

**Location 1**: Line 352
**Issue**: Conflict resolution example uses removed strict_mode setting

**Current**:
```python
#    Conflict 2: strict_mode
#      → User chooses: Use imported (true)
```

**Fix**: Replace with valid directive preference example

**Corrected**:
```python
#    Conflict 2: max_function_length
#      → User chooses: Use imported (100)
```

---

**Location 2**: Line 373
**Issue**: Resolution summary mentions strict_mode

**Current**:
```python
#    Resolution:
#    • always_add_docstrings: Kept existing (true)
#    • strict_mode: Used imported (true)
#    • max_function_length: Used imported (100)
```

**Fix**: Remove strict_mode line (already have max_function_length)

**Corrected**:
```python
#    Resolution:
#    • always_add_docstrings: Kept existing (true)
#    • max_function_length: Used imported (100)
#    • indent_style: Used imported (spaces_2)
```

---

## Files Checked and Verified Clean

### ✅ All Other Directive MD Files
Checked all files in `src/aifp/reference/directives/`:
- No references to removed settings found in other directives
- compliance_checking properly documented where needed

### ✅ Other Directive JSON Files
- directives-user-pref.json: ✅ Already updated in Phase 5
- directives-fp-core.json, directives-fp-aux.json: ✅ No settings references (expected)
- directives-user-system.json: ✅ No invalid references
- directives-git.json: ✅ No invalid references

### ✅ Backups (Intentionally Not Updated)
- docs/directives-json/backups/*.json contain old settings (expected)
- Backups preserved for historical reference

---

## Summary Statistics

### Issues by Type:
| Type | Count | Priority |
|------|-------|----------|
| JSON workflow issues | 3 | Critical |
| MD example issues | 8 | Medium |
| **Total Issues** | **11** | - |

### Issues by File:
| File | Issues | Type |
|------|--------|------|
| directive_flow_user_preferences.json | 1 | Critical |
| directives-project.json | 2 | Critical |
| user_preferences_export.md | 2 | Medium |
| user_preferences_learn.md | 1 | Medium |
| user_preferences_sync.md | 1 | Medium |
| user_preferences_update.md | 1 | Medium |
| user_preferences_import.md | 2 | Medium |

---

## Removed Settings Reference

For verification, these settings were removed in v3.1:
1. ❌ `fp_strictness_level` (global) - FP is baseline, not optional
2. ❌ `prefer_explicit_returns` (global) - Redundant with system prompt
3. ❌ `project_compliance_check.auto_fix_violations` - Directive repurposed
4. ❌ `project_compliance_check.skip_warnings` - Directive repurposed
5. ❌ `project_compliance_check.strict_mode` - Directive repurposed
6. ❌ `project_task_decomposition.task_granularity` - Tried to override schema

---

## Valid v3.1 Settings Baseline

### Global (user_settings) - 2 settings:
- ✅ `project_continue_on_start` - Autostart setting
- ✅ `suppress_warnings` - Warning suppression list

### Directive Preferences - 8 settings:
- **project_file_write** (5): always_add_docstrings, max_function_length, prefer_guard_clauses, code_style, indent_style
- **project_task_decomposition** (3): naming_convention, auto_create_items, default_priority

### Tracking Features - 5 features:
- ✅ fp_flow_tracking
- ✅ ai_interaction_log
- ✅ helper_function_logging
- ✅ issue_reports
- ✅ compliance_checking

---

## Recommended Action Plan

### Phase 1: Fix Critical JSON Issues (3 fixes)
1. directive_flow_user_preferences.json - Remove line 45
2. directives-project.json - Remove fp_strictness_level from line 215
3. directives-project.json - Remove task_granularity from line 422

### Phase 2: Fix MD Example Issues (8 fixes)
1. user_preferences_export.md - Update export format examples (2 locations)
2. user_preferences_learn.md - Remove prefer_explicit_returns example
3. user_preferences_sync.md - Update context example
4. user_preferences_update.md - Update database operations example
5. user_preferences_import.md - Update conflict examples (2 locations)

### Phase 3: Final Verification
1. Re-run grep searches for removed settings
2. Verify no new references introduced
3. Test directive workflows with v3.1 settings
4. Mark settings cleanup as thoroughly complete

---

**Status**: Ready for fixes
**Next Step**: Apply all 11 corrections
**Estimated Time**: 15-20 minutes
**Last Updated**: 2026-01-07

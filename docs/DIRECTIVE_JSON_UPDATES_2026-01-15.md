# Directive JSON Updates - Global State & DRY

**Date**: 2026-01-15
**Status**: Complete
**File Updated**: `docs/directives-json/directives-fp-core.json`

## Summary

Updated directive JSON entries to match recent MD file changes regarding global state management and DRY principles.

---

## Directives Updated

### 1. `fp_state_elimination` (Lines 83-151)

**Changes Made**:

#### Category Description
**Before**: "Eliminates global or implicit state in function logic."
**After**: "Eliminates hidden mutable global state in function logic."

**Rationale**: Clarifies that MUTABLE global state is the target, not all global state.

---

#### Description
**Before**:
```
"Detects and removes reliance on global variables or hidden mutable structures. Used during function analysis to strip implicit global state."
```

**After**:
```
"Detects and removes reliance on mutable global variables or hidden mutable structures. Allows read-only global constants (Final). For runtime mutable state, suggests state database pattern (explicit state via SQLite). Used during function analysis to eliminate hidden mutable state."
```

**Rationale**:
- Specifies **mutable** global variables (not all globals)
- Explicitly allows read-only constants (Final)
- Mentions state database pattern as FP-compliant alternative

---

#### Workflow - New Branch Added

**Added Branch**:
```json
{
  "if": "runtime_state_needed",
  "then": "suggest_state_database",
  "details": {
    "pattern": "Create state.db with explicit state tracking",
    "use_cases": ["sessions", "rate_limits", "progress_tracking", "job_queues", "caches", "metrics"]
  }
}
```

**Rationale**: Provides AI with explicit guidance to suggest state database pattern when runtime mutable state is genuinely needed.

---

#### Workflow - Updated Branches

**Branch: global_references**
```json
{
  "if": "global_references",
  "then": "inline_dependencies",
  "details": {
    "allow_immutable_constants": true,
    "check_for_Final_annotation": true
  }
}
```

**Added**: Details about allowing immutable constants with Final annotation.

---

**Branch: mutable_static_data**
```json
{
  "if": "mutable_static_data",
  "then": "convert_to_immutable",
  "details": {
    "options": [
      "Make immutable constant (if never changes)",
      "Pass as parameter (if changes)",
      "Suggest state database pattern (if runtime mutable state needed)"
    ]
  }
}
```

**Added**: Three explicit resolution strategies including state database pattern.

---

#### Roadblocks Updated

**Before**:
```json
[
  {
    "issue": "global_dependency",
    "resolution": "Pass as explicit parameter"
  },
  {
    "issue": "static_mutable_data",
    "resolution": "Refactor to immutable constant"
  }
]
```

**After**:
```json
[
  {
    "issue": "global_dependency",
    "resolution": "Pass as explicit parameter"
  },
  {
    "issue": "mutable_global_state",
    "resolution": "Refactor to immutable constant OR state database pattern"
  },
  {
    "issue": "runtime_state_tracking",
    "resolution": "Use state database pattern (explicit state via SQLite)"
  }
]
```

**Changes**:
- Renamed `static_mutable_data` → `mutable_global_state` (clearer)
- Updated resolution to include state database pattern
- Added new roadblock for runtime state tracking

---

### 2. `fp_no_oop` (Lines 446-478)

**Changes Made**:

#### Workflow - Updated Branch

**Branch: class_detected**

**Before**:
```json
{
  "if": "class_detected",
  "then": "refactor_to_module_function"
}
```

**After**:
```json
{
  "if": "class_detected",
  "then": "refactor_to_module_function",
  "details": {
    "apply_dry_principle": true,
    "extract_common_utilities": "if used across multiple files",
    "scope_levels": ["global", "category", "file"]
  }
}
```

**Rationale**: When refactoring classes to functions, AI should apply DRY principle and extract common utilities to appropriate scope level (`_common.py`).

---

## Alignment with MD Files

### `fp_state_elimination.md`

**MD Changes** (lines 19-31, 311-379, 454-500):
- Updated purpose to clarify "hidden mutable state" (not all state)
- Added "What's ALLOWED" section (read-only constants, lookup tables, state database)
- Added state database example in compliant usage
- Updated edge case with state database pattern

**JSON Alignment**: ✅ Complete
- Description mentions mutable globals (not all globals)
- Description mentions state database pattern
- Workflow includes state database suggestion branch
- Roadblocks include state database resolution

---

### `fp_no_oop.md`

**MD Changes** (line 89):
- Added DRY note: "Apply DRY principle: Extract common utilities to `_common.py` if used across multiple files"

**JSON Alignment**: ✅ Complete
- Workflow branch includes DRY details
- Mentions scope levels (global, category, file)

---

## Impact on Core Database Import

These JSON files will be imported into `aifp_core.db` when the project is ready:

**Table**: `directives`
- `description` field updated (fp_state_elimination, fp_no_oop category)
- `workflow_json` field updated (new branches, updated details)
- `roadblocks_json` field updated (fp_state_elimination)

**When Imported**:
- AI will see updated descriptions when querying directives
- Workflow branches will include new state database guidance
- Roadblocks will reference state database pattern

**Query Examples**:
```sql
-- Get directive details
SELECT description, workflow_json
FROM directives
WHERE name = 'fp_state_elimination';

-- Result includes state database pattern guidance
```

---

## Verification Checklist

✅ **fp_state_elimination updated**:
- ✅ Category description clarified (hidden mutable state)
- ✅ Description mentions Final constants and state database
- ✅ Workflow includes state database suggestion branch
- ✅ Workflow branches include allow_immutable_constants
- ✅ Roadblocks updated with state database options

✅ **fp_no_oop updated**:
- ✅ Workflow branch includes DRY principle details
- ✅ Details mention scope levels for extraction

✅ **Consistency check**:
- ✅ JSON matches MD file content
- ✅ JSON matches system prompt guidance
- ✅ All three sources (JSON, MD, system prompt) aligned

---

## Files Modified

1. `docs/directives-json/directives-fp-core.json`
   - Lines 83-151: fp_state_elimination
   - Lines 446-478: fp_no_oop

---

## Related Documentation

- `docs/GLOBAL_STATE_AND_DRY_UPDATES.md` - MD file updates
- `docs/SYSTEM_PROMPT_CONDENSING.md` - System prompt updates
- `src/aifp/reference/directives/fp_state_elimination.md` - Directive MD
- `src/aifp/reference/directives/fp_no_oop.md` - Directive MD

---

**Conclusion**: Directive JSON files now fully aligned with MD documentation and system prompt regarding global state management (read-only constants encouraged, state database pattern for runtime mutable state) and DRY principles (extract common utilities).

# System Prompt Changes Applied

**Date**: 2025-12-22
**Previous Version**: sys-prompt/previous/aifp_system_prompt_prev4.txt (438 lines)
**Current Version**: sys-prompt/aifp_system_prompt.txt (498 lines)
**Net Change**: +60 lines (+13.7%)

---

## Summary of Changes

All 9 NOTES have been addressed and removed. All improvements from SYSTEM_PROMPT_IMPROVEMENTS.md have been implemented.

---

## Changes Applied

### ✅ 1. Global Constants Exception (Lines 90-94)

**Added after line 88 (Pure Functions rule)**

```markdown
**Global Constants Exception**:
✅ Read-only global constants for configuration/infrastructure are acceptable
- Examples: DATABASE_URL, API_KEYS, MAX_RETRIES, CONFIG_PATH
- Must be immutable (use `Final` in Python, `const` in JS/TS, etc.)
- ❌ Mutable global state is forbidden (no global counters, caches, or state objects)
```

**Impact**: Clarifies FP allows immutable configuration constants while forbidding mutable global state

**Removed NOTE**: "global variables should be ok. It may not be FP, but a global var file or whatever global var availability allowed in infrastructure language syntax. Let's discuss"

---

### ✅ 2. Execution Order & Use Case 2 Two-Stage Process (Lines 231-256)

**Added after line 229 (directive introduction)**

```markdown
**Directive Execution Order** (Critical):

**For ALL directives**:
1. User preferences loaded FIRST
2. Preferences applied to directive parameters
3. Directive executes with modified behavior
4. Results returned

**For Use Case 2 (User Custom Directives) - Two-Stage Process**:

**Stage 1: Build Infrastructure** (First-time setup):
- User writes directive files
- AI parses and validates
- AI generates entire automation codebase
- User approves
- Infrastructure is now ready

**Stage 2: Execute Directives** (Ongoing):
- Directives activate
- System monitors and executes using the infrastructure AI built
- AI only modifies when directives change or improvements needed

**Key Point**: In Use Case 2, the project IS the automation infrastructure.
```

**Impact**: Critical clarification of preferences-first execution and Use Case 2 workflow

**Removed NOTE**: "Settings to be reviewed before directives and are preciding modifiers to directives. Case 2 user custom directives should be mentioned and entry point for that (it's a 2 stage process...)"

---

### ✅ 3. MD File Guidance (Lines 289-304)

**Added after line 287 (How to use directives)**

```markdown
**Directive MD Documentation** (Reference Layer):
- Every directive has comprehensive MD file
- Contains: Complete workflows, examples, edge cases, FP compliance notes

**When to read MD files**:
✅ When you need deeper context (complex edge cases, uncommon scenarios)
✅ When directive workflow has ambiguity
✅ When FP compliance questions arise
✅ When understanding cross-directive relationships
❌ Not for routine usage (directive JSON has workflow steps)
❌ Not for every execution (only when context escalation needed)

**How to access**:
- Query: `get_directive_content(directive_name)`
- Prefer directive JSON for standard workflows, MD for complex scenarios
```

**Impact**: Clear guidance on when to escalate to MD documentation vs using directive JSON

**Removed NOTE**: "mention md file reference in directives and to read file if context escalation necessary. Not all the time, only when more info on directive is needed"

---

### ✅ 4. batch_update_progress NOTE Removed (Line 298)

**Removed NOTE**: "review this helper. is_sub_helper=true appropriate? How does AI use it (higher function that uses this function?)"

**Verification**: Checked `docs/helpers/json/helpers-orchestrators.json` - classification is correct (is_tool=true, is_sub_helper=false)

**Impact**: No content changes needed, only NOTE removal

---

### ✅ 5. SQL Exception for user_directives.db (Lines 350-354)

**Added after line 348 (Database Query Policy)**

```markdown
**Exception for user_directives.db**:
- Direct SQL queries against `user_directives.db` are acceptable (not restricted)
- This database is user-specific and domain-specific
- Helpers are still preferred, but direct queries are not discouraged
- Use SQL when exploring custom directive schemas or querying domain-specific data
```

**Impact**: Prevents over-restriction for user directive database queries

**Removed NOTE**: "direct sql queries against user custom directives database is ok."

---

### ✅ 6. Use Case 2 Clarification (Lines 417-437)

**Added after line 415 (Two Use Cases section)**

```markdown
**Use Case 2: Critical Understanding**

**What the user provides**:
- Directive files (YAML/JSON/TXT) describing WHAT they want automated

**What AI builds**:
- Complete automation infrastructure (the code that will execute those directives)
- src/ with FP-compliant implementation
- tests/ for the automation code
- Scheduler/event loop/webhook server as needed

**Workflow**:
1. User writes directive files (simple descriptions)
2. AI builds the project (generates all implementation code)
3. Project now exists to execute user directives
4. AI only modifies when directives change or improvements needed

**Key Point**: The project IS the automation codebase.

**Never mixed**: One project = one purpose.
```

**Impact**: Fundamental clarification that AI builds infrastructure first in Use Case 2

**Removed NOTE**: "Never mixed, but if user case 2, project automation first requires project code that allows the automation. Just an FYI, should note for clarification"

---

### ✅ 7. User Prefs Complexity NOTE Removed (Line 375)

**Removed NOTE**: "the AI generated user prefs are a bit too much for this MCP. I'll modify later."

**Status**: Deferred per user request

---

### ✅ 8. Tracking Section Simplified (Lines 441-451)

**Replaced previous verbose tracking explanation (14 lines) with simplified version**

```markdown
**User Preferences**: Atomic key-value overrides for directive behavior
- Examples: always_add_docstrings, max_function_length, prefer_guard_clauses
- Auto-loaded before customizable directives (user_preferences_sync)
- Directives: user_preferences_update, user_preferences_learn, export, import

**Tracking Features**: ALL OFF BY DEFAULT
- Tracking features exist for development/debugging purposes only
- **Regular users**: Assume tracking is always disabled
- **Developer users**: Can explicitly enable tracking with tracking_toggle directive
- Do not mention tracking features to regular users
- All tracking data is for AIFP project development, not end-user consumption
```

**Impact**: Removes confusion, emphasizes tracking is dev-only

**Removed NOTE**: "General user can do nothing with the tracking data apart from maybe provide to devs for review. So this should not really be mentioned..."

---

### ✅ 9. Dev-Only Section Removed (Lines 401-416 in prev4)

**Completely removed "QUERY, DON'T ASSUME" section (16 lines)**

**Removed content**:
```markdown
=== QUERY, DON'T ASSUME ===

**Never hard-code counts or relationships. Always query database:**

```python
# ✅ Query at runtime
directive_count = query_mcp_db(...)
helpers = get_helpers_for_directive(...)
next_directives = get_next_directives_from_status(...)

# ❌ Hard-coded assumptions
"There are 66 FP directives"
```
```

**Impact**: Removes dev-focused content from user-focused system prompt

**Removed NOTE**: "This is not for system prompt. This is for dev..."

---

## Line Count Changes

| Section | Before (prev4) | After | Change |
|---------|----------------|-------|--------|
| **Global Constants** | 0 lines | 5 lines | +5 |
| **Execution Order** | 0 lines | 26 lines | +26 |
| **MD File Guidance** | 0 lines | 16 lines | +16 |
| **SQL Exception** | 0 lines | 5 lines | +5 |
| **Use Case 2 Clarification** | 0 lines | 22 lines | +22 |
| **Tracking Simplified** | 14 lines | 11 lines | -3 |
| **Dev Section Removed** | 16 lines | 0 lines | -16 |
| **NOTEs Removed** | 9 NOTEs | 0 NOTEs | -9 lines |
| **Total** | 438 lines | 498 lines | **+60 lines** |

---

## Notes Removed

All 9 embedded NOTES have been removed from the system prompt:

1. ✅ Line 87 - Global variables discussion
2. ✅ Line 223 - Settings and execution order
3. ✅ Line 258 - MD file reference
4. ✅ Line 298 - batch_update_progress review
5. ✅ Line 306 - Direct SQL for user_directives.db
6. ✅ Line 369 - Use Case 2 clarification
7. ✅ Line 375 - User prefs complexity (deferred)
8. ✅ Line 387 - Tracking data purpose
9. ✅ Line 416 - Dev-only guidance

---

## Validation Checklist

- [x] Global constants pattern clearly allowed (with immutability requirement and examples)
- [x] Execution order explicitly states: preferences → directive → result
- [x] Use Case 2 two-stage workflow explained (Stage 1: AI builds infrastructure, Stage 2: Execute directives)
- [x] MD file guidance tells when to read (escalation for complex scenarios, not routine)
- [x] batch_update_progress - No changes needed (already correct)
- [x] SQL exception for user_directives.db clearly stated
- [x] Tracking section simplified (dev-only emphasis, regular users ignore)
- [x] Dev-focused "query don't assume" section REMOVED ENTIRELY
- [x] All 9 NOTEs removed
- [x] System prompt remains focused on AI runtime behavior, not dev guidance
- [x] Total lines reasonable (498, +13.7% increase for critical clarifications)

---

## Files

**Production**: `sys-prompt/aifp_system_prompt.txt` (498 lines) ✅

**Backups**:
- `sys-prompt/previous/aifp_system_prompt_old.txt` (576 lines - pre-Phase 7)
- `sys-prompt/previous/aifp_system_prompt_prev1.txt` (724 lines - post-Phase 8, too verbose)
- `sys-prompt/previous/aifp_system_prompt_prev2.txt` (275 lines - too minimal)
- `sys-prompt/previous/aifp_system_prompt_prev3.txt` (429 lines - before user note fixes)
- `sys-prompt/previous/aifp_system_prompt_prev4.txt` (438 lines - before today's changes)

**Documentation**:
- `docs/SYSTEM_PROMPT_IMPROVEMENTS.md` (analysis and recommendations)
- `docs/SYSTEM_PROMPT_CHANGES_APPLIED.md` (this file - complete change log)
- `docs/SYSTEM_PROMPT_FINAL.md` (design rationale for prev3/prev4 versions)
- `docs/SYSTEM_PROMPT_USER_NOTES_ANALYSIS.md` (detailed user notes analysis)
- `docs/SYSTEM_PROMPT_FIXES_APPLIED.md` (fixes applied to reach prev4)
- `docs/SYSTEM_PROMPT_COMPARISON.md` (prev1 vs old comparison)
- `docs/SYSTEM_PROMPT_CLEANUP_REPORT.md` (prev2 cleanup analysis)

---

## Benefits of These Changes

### 1. **Clarity** ✅
- Global constants exception removes FP ambiguity for infrastructure patterns
- Execution order makes preferences-first pattern explicit
- Use Case 2 workflow prevents fundamental misunderstanding

### 2. **Completeness** ✅
- MD file guidance tells AI when to escalate to documentation
- SQL exception prevents over-restriction for user directive queries
- Two-stage Use Case 2 process fully documented

### 3. **Focus** ✅
- Tracking simplified to dev-only (removes user confusion)
- Dev-focused "query don't assume" section removed (wrong audience)
- All NOTEs removed (clean, production-ready)

### 4. **Maintainability** ✅
- No hard-coded numbers remain (all were in removed sections)
- Clear, concise additions that won't need frequent updates
- System prompt stays focused on AI runtime behavior

---

**Status**: ✅ All changes applied successfully. System prompt is production-ready.

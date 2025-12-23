# System Prompt Improvements - Based on User Notes

**Date**: 2025-12-22
**Source**: sys-prompt/aifp_system_prompt.txt (438 lines with embedded NOTES)
**Target**: Improved version addressing all 9 notes

---

## Executive Summary

Reviewed all 9 NOTES embedded in current system prompt. Key themes:
1. **Clarify FP exceptions** (global constants for config are OK)
2. **Emphasize execution order** (preferences before directives)
3. **Add MD file guidance** (when to read for deeper context)
4. **Simplify tracking mentions** (not for regular users)
5. **Clarify Use Case 2 workflow** (AI builds infrastructure first)
6. **Fix helper classification** (batch_update_progress)
7. **Add SQL exception** (user_directives.db queries OK)
8. **Reframe dev guidance** (or remove entirely)

---

## Note-by-Note Analysis

### ✅ NOTE 1: Global Variables (Line 87)

**User Request**: "global variables should be ok. It may not be FP, but a global var file or whatever global var availability allowed in infrastructure language syntax"

**Current Problem**: Example shows ALL global variables as ❌ impure

**Fix**: Distinguish between immutable global constants (✅ acceptable) and mutable global state (❌ forbidden)

**Improved Text (add after line 88)**:
```markdown
   **Global Constants Exception**:
   - ✅ Read-only global constants for configuration/infrastructure are acceptable
   - Examples: DATABASE_URL, API_KEYS, MAX_RETRIES, CONFIG_PATH
   - Must be immutable (use `Final` type hint in Python, `const` in JS, etc.)
   - ❌ Mutable global state is still forbidden (no global counters, caches, or state objects)

   Example:
   ```python
   # ✅ Acceptable - Immutable configuration constants
   from typing import Final

   DATABASE_URL: Final[str] = "sqlite:///db.sqlite"
   MAX_RETRIES: Final[int] = 3
   API_TIMEOUT: Final[int] = 30

   def connect(url: str = DATABASE_URL) -> Connection:
       return create_connection(url)

   # ❌ Forbidden - Mutable global state
   connection_count = 0  # Mutable counter
   cache = {}  # Mutable cache

   def track_connection():
       global connection_count
       connection_count += 1  # Mutation
   ```
```

**Impact**: Allows practical infrastructure patterns while maintaining FP purity

---

### ✅ NOTE 2: Settings Before Directives (Line 223)

**User Request**: "Settings to be reviewed before directives and are preceding modifiers to directives. Case 2 user custom directives should be mentioned and entry point for that (it's a 2 stage process)"

**Current Problem**: Order of execution not explicit enough; Use Case 2 two-stage process not clear

**Fix**: Add explicit execution order section

**Improved Text (insert at line 223 before "Key Directives")**:
```markdown
**Directive Execution Order** (Critical):

**For ALL directives**:
1. **User preferences loaded FIRST** (user_preferences_sync auto-called if directive is customizable)
2. **Preferences applied to directive parameters**
3. **Directive executes with modified behavior**
4. **Results returned**

**For Use Case 2 (User Custom Directives)**:

Two-stage process (automation projects):

**Stage 1: Build Infrastructure** (First-time setup)
- User writes directive files (directives/lights.yaml, directives/thermostat.json)
- AI parses and validates (user_directive_parse, user_directive_validate)
- AI **generates entire automation codebase** (user_directive_implement)
  - Creates src/ with FP-compliant implementation code
  - Creates tests/
  - Tracks in project.db like any software project
- User approves (user_directive_approve)
- Infrastructure is now ready

**Stage 2: Execute Directives** (Ongoing)
- Directives activate (user_directive_activate)
- System monitors and executes directives using the infrastructure AI built
- AI only modifies code when directives change or improvements needed

**Key Point**: In Use Case 2, the **project IS the automation infrastructure**. AIFP first builds the code that will execute user directives, then that code runs the directives.
```

**Impact**: Makes execution order crystal clear; explains Use Case 2 workflow properly

---

### ✅ NOTE 3: MD File Reference (Line 258)

**User Request**: "mention md file reference in directives and to read file if context escalation necessary. Not all the time, only when more info on directive is needed"

**Current Problem**: No mention of when/how to read directive MD files

**Fix**: Add guidance on directive MD documentation

**Improved Text (add after line 260)**:
```markdown

**Directive MD Documentation** (Reference Layer):
- Every directive has comprehensive MD file: `src/aifp/reference/directives/{category}/{directive_name}.md`
- Contains: Complete workflows, examples, edge cases, FP compliance notes, cross-directive relationships

**When to read MD files**:
- ✅ When you need deeper context (complex edge cases, uncommon scenarios)
- ✅ When directive workflow has ambiguity
- ✅ When FP compliance questions arise
- ✅ When understanding cross-directive relationships
- ❌ Not for routine usage (directive JSON has workflow steps - use those)
- ❌ Not for every execution (only when context escalation needed)

**How to access**:
- Query: `get_directive_content(directive_name)` returns full MD documentation
- Read directly from filesystem if MCP tool available
- Prefer directive JSON for standard workflows, MD for complex scenarios
```

**Impact**: Clear guidance on when to escalate to MD documentation vs using directive JSON

---

### ✅ NOTE 4: batch_update_progress Helper (Line 298)

**User Request**: "review this helper. is_sub_helper=true appropriate? How does AI use it (higher function that uses this function?)"

**Verification from `docs/helpers/json/helpers-orchestrators.json` (lines 132-173)**:
```json
{
  "name": "batch_update_progress",
  "is_tool": true,
  "is_sub_helper": false,
  "used_by_directives": []
}
```

**Metadata note**: "8 helpers are query/convenience tools for AI... intentionally not mapped to directives. These are AI tools, not directive tools."

**Conclusion**: Current classification is **CORRECT**:
- ✅ `is_tool=true` (AI calls directly)
- ✅ `is_sub_helper=false` (not a sub-helper)
- ✅ AI-only convenience tool (not used by directives)

**Action**: **NO CHANGES NEEDED** - System prompt accurately describes it as an orchestrator that AI calls directly

**Impact**: None (already correct)

---

### ✅ NOTE 5: Direct SQL for User Directives DB (Line 305)

**User Request**: "direct sql queries against user custom directives database is ok."

**Current Problem**: Says "extremely rare" for all direct SQL, but user_directives.db is exception

**Fix**: Add explicit exception for user_directives.db

**Improved Text (add after line 308)**:
```markdown

**Exception for user_directives.db**:
- Direct SQL queries against `user_directives.db` are acceptable (not restricted)
- This database is user-specific and domain-specific
- Helpers are still preferred, but direct queries are not discouraged
- Use SQL when exploring custom directive schemas or querying domain-specific data
- Example: `SELECT * FROM user_directives WHERE status = 'active'` (acceptable)
```

**Impact**: Removes confusion about SQL restrictions for user directive database

---

### ✅ NOTE 6: Use Case 2 Clarification (Line 369)

**User Request**: "Never mixed, but if user case 2, project automation first requires project code that allows the automation. Just an FYI, should note for clarification"

**Current Problem**: Doesn't explain that Use Case 2 requires building infrastructure first

**Fix**: Add clarification about automation infrastructure

**Improved Text (add after line 369)**:
```markdown

**Use Case 2: Critical Understanding**

**What the user provides**:
- Directive files (YAML/JSON/TXT) describing WHAT they want automated
- Example: "Turn off lights at 5pm", "Scale EC2 when CPU > 80%"

**What AI builds**:
- **Complete automation infrastructure** (the code that will execute those directives)
- src/ with FP-compliant implementation (trigger handlers, action executors, API clients)
- tests/ for the automation code
- Scheduler/event loop/webhook server as needed

**Workflow**:
1. User writes directive files (simple descriptions)
2. AI **builds the project** (generates all implementation code)
3. Project now exists to execute user directives
4. AI only modifies when directives change or improvements needed

**Key Point**: The project IS the automation codebase. AIFP project management is dedicated to building and maintaining the infrastructure that executes user directives.

**Never mixed**: One project = one purpose. Don't mix web app development with home automation directives.
```

**Impact**: Crystal clear explanation of Use Case 2 purpose and workflow

---

### ✅ NOTE 7: User Prefs Too Complex (Line 375)

**User Request**: "the AI generated user prefs are a bit too much for this MCP. I'll modify later."

**Action**: No changes needed now. User will handle later.

**Status**: Deferred

---

### ✅ NOTE 8: Tracking Not for Regular Users (Line 387)

**User Request**: "General user can do nothing with the tracking data apart from maybe provide to devs for review. So this should not really be mentioned."

**Current Problem**: Lines 373-387 have extensive tracking explanations

**Fix**: Drastically simplify - tracking is for devs only

**Improved Text (replace lines 373-387)**:
```markdown
=== USER PREFERENCES & PRIVACY ===

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

**Impact**: Removes confusion, focuses on what matters to regular users

---

### ✅ NOTE 9: Dev-Only Section (Line 416)

**User Request**: "This is not for system prompt. This is for dev. In any of the directives, there is no place for AI to hard code counts or relationships anywhere."

**User Decision**: **"remove entirely"**

**Current Problem**: Lines 395-410 contain dev-focused guidance about not hard-coding in directive implementations

**Action**: **REMOVE LINES 395-410 ENTIRELY**

**Reasoning**:
- System prompt is for AI using AIFP, not AI developing AIFP
- The principle (query at runtime) is already covered elsewhere
- These examples are about directive implementation, not directive usage
- Creates confusion by mixing dev and user contexts

**Lines to remove**:
```markdown
=== QUERY, DON'T ASSUME ===

**Never hard-code counts or relationships. Always query database:**

```python
# ✅ Query at runtime
directive_count = query_mcp_db("SELECT COUNT(*) FROM directives WHERE type = 'fp'")
helpers = get_helpers_for_directive(directive_id)
next_directives = get_next_directives_from_status(current, status)

# ❌ Hard-coded assumptions
"There are 66 FP directives"  # May be outdated
"project_file_write uses reserve_file helper"  # Query to verify
```

NOTE: This is not for system prompt. This is for dev...
```

**Impact**: Removes 16 lines of dev-focused content, clarifies system prompt audience

---

## Summary Table

| Note # | Line | Topic | Action | Lines Changed | Priority |
|--------|------|-------|--------|---------------|----------|
| 1 | 87 | Global constants exception | Add clarification + examples | +20 | High |
| 2 | 223 | Execution order & Use Case 2 | Add execution order section | +30 | Critical |
| 3 | 258 | MD file guidance | Add when/how to read MD files | +15 | Medium |
| 4 | 298 | batch_update_progress helper | **NO ACTION** (already correct) | 0 | ~~Low~~ Done |
| 5 | 305 | SQL for user_directives.db | Add exception clause | +6 | Medium |
| 6 | 369 | Use Case 2 workflow | Add infrastructure explanation | +20 | High |
| 7 | 375 | User prefs complexity | No action (deferred) | 0 | N/A |
| 8 | 387 | Tracking mentions | Drastically simplify | -14 | High |
| 9 | 416 | Dev-only guidance | **REMOVE ENTIRELY** (confirmed) | -16 | High |

**Net Change**: Approximately **+60 lines** (from 438 to ~498 lines)
- Adds critical execution order guidance
- Adds global constants exception (practical infrastructure pattern)
- Removes dev-focused content (-30 lines from tracking + dev section)
- Adds Use Case 2 clarification
- Better organization and clarity

---

## Implementation Priority

### 🔴 Critical (Must Fix)
1. **NOTE 2**: Execution order (line 223) - AI needs to know preferences come first and Use Case 2 two-stage workflow
2. **NOTE 8**: Tracking simplification (line 387) - Remove user confusion, dev-only emphasis

### 🟠 High (Should Fix)
1. **NOTE 1**: Global constants (line 87) - Common infrastructure pattern needs FP exception
2. **NOTE 6**: Use Case 2 workflow (line 369) - Fundamental misunderstanding risk (AI builds infrastructure first)
3. **NOTE 9**: Dev guidance removal (line 416) - **CONFIRMED: Remove entirely**

### 🟡 Medium (Nice to Have)
1. **NOTE 3**: MD file guidance (line 258) - Helps with documentation usage (when to escalate)
2. **NOTE 5**: SQL exception (line 305) - Prevents over-restriction for user_directives.db

### ✅ Complete (No Action)
1. **NOTE 4**: batch_update_progress - Verified correct classification (is_tool=true, is_sub_helper=false)

### ⚪ Deferred
1. **NOTE 7**: User prefs complexity - User handling later

---

## Validation Checklist

After applying changes, verify:

- [ ] Global constants pattern clearly allowed (with immutability requirement and examples)
- [ ] Execution order explicitly states: preferences → directive → result
- [ ] Use Case 2 two-stage workflow explained (Stage 1: AI builds infrastructure, Stage 2: Execute directives)
- [ ] MD file guidance tells when to read (escalation for complex scenarios, not routine)
- [ ] ~~batch_update_progress classified~~ ✅ Already correct (no changes needed)
- [ ] SQL exception for user_directives.db clearly stated
- [ ] Tracking section simplified (dev-only emphasis, regular users ignore)
- [ ] Dev-focused "query don't assume" section **REMOVED ENTIRELY**
- [ ] System prompt remains focused on AI runtime behavior, not dev guidance
- [ ] Total lines stay reasonable (~498, not bloated)

---

## Next Steps

1. Review this analysis with user
2. Confirm priorities and approach for each note
3. Apply changes to sys-prompt/aifp_system_prompt.txt
4. Backup current version to sys-prompt/previous/aifp_system_prompt_prev4.txt
5. Test with sample AI interactions
6. Update SYSTEM_PROMPT_FINAL.md with new version summary

---

**Status**: ✅ Analysis complete, awaiting user approval for implementation

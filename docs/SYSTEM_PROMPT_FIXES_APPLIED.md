# System Prompt Fixes Applied - Based on User Notes

**Date**: 2025-12-21
**Source**: User notes from sys-prompt/previous/aifp_system_prompt_prev1.txt
**Target**: sys-prompt/aifp_system_prompt.txt
**Backup**: sys-prompt/previous/aifp_system_prompt_prev3.txt (pre-fix version)

---

## Fixes Applied

### ✅ Fix 1: "Functional Procedural" as Explicit Key Principle (Lines 17-35)

**User Note**: "Functional Procedural programming is a key principle"

**Before**:
```markdown
AIFP is a behavioral framework that guides HOW you code...
```

**After**:
```markdown
AIFP = AI Functional Procedural Programming

A behavioral framework with three core principles:
- **Functional Procedural**: All code follows FP paradigm (pure functions, immutable data, no OOP)
- **Directive-Driven**: Workflows tell you WHEN to act and WHAT steps to follow
- **Database-Driven**: Project state stored in databases (NOT your memory)
```

**Impact**: Makes FP the FIRST core principle, explicitly named.

---

### ✅ Fix 2: Optional Features Clarified (Lines 31-35)

**User Notes**:
- "but can pick tools as needed"
- "There are some optional features"

**Before**:
```markdown
NOT as:
❌ Optional tools you can use or ignore
❌ Something that waits for explicit user commands
```

**After**:
```markdown
Important distinctions:
- **FP baseline is mandatory** (all code must be FP-compliant)
- **Directive workflows are mandatory** for project management
- **Some features are optional** (user preferences, tracking - all OFF by default)
- **Helper functions are flexible** (categories guide usage, but AI can call any helper needed)
```

**Impact**: Clarifies what's mandatory (FP, directives) vs optional (tracking, preferences).

---

### ✅ Fix 3: Load Directives by Type (Lines 65-67)

**User Note**: "Should get directives based on intent keywords, or type... All directives will give even the FP directives which don't need to be in memory"

**Before**:
```markdown
3. **Load directives if not in memory**:
   - Call get_all_directives() to cache all directives
```

**After**:
```markdown
3. **Load directives if not in memory**:
   - Call search_directives(type="project") to load project directives
   - Load FP directives only when needed: search_directives(type="fp")
   - These guide your behavior for entire session
```

**Impact**: Reduces memory usage by only loading relevant directives (66 FP directives not loaded unless needed).

---

### ✅ Fix 4: Helper Flexibility (Lines 266-269)

**User Note**: "Should not limit AI so much... AI should be able to call and use any helper function it needs"

**Before**:
```markdown
**Three Categories**:
1. **Directive-used helpers**: Called BY directives
   - Directives tell you WHEN to use these
```

**After**:
```markdown
**Three Categories** (guidance, not hard limits):
1. **Directive-used helpers**: Typically called BY directives
   - Directives guide when to use these, but AI can call directly if needed
```

**Impact**: Gives AI flexibility to call any helper when needed, categories are guidance only.

---

### ✅ Fix 5: Database Query Policy (Lines 293-302)

**User Note**: "No need for direct queries... We should have helper functions for all database queries... AI 'can' query the database, but only if no helper functions exist (would be extremely rare)"

**Before**:
```markdown
**Database Operations**:
- **Strongly prefer directives** for writes
- **Use orchestrators** for complex operations
- **Direct SQL acceptable** for edge cases
```

**After**:
```markdown
**Database Query Policy** (priority order):
1. **Use helpers first** - Query available helpers
2. **Use orchestrators** - For complex operations
3. **Use directives** - For writes
4. **Direct SQL as last resort** - Only if no helper exists (extremely rare)

**Rules**:
- **Never use raw SQL for writes** (always use directives or helpers)
- **Prefer helpers over raw SQL for reads**
```

**Impact**: Makes helper-first approach explicit, SQL is last resort (not "acceptable").

---

### ✅ Fix 6: Remove query_mcp_db Suggestions (Lines 308-314)

**User Note**: Same as Fix 5

**Before**:
```markdown
1. **aifp_core.db** (global, read-only)
   - Query: query_mcp_db(sql) or get_all_directives()

2. **project.db** (per-project, mutable)
   - Query: query_project_db(sql) or use specific helpers
```

**After**:
```markdown
1. **aifp_core.db** (global, read-only)
   - Query: get_all_directives() or search_directives(type, keyword)
   - Avoid: query_mcp_db(sql) - prefer helpers

2. **project.db** (per-project, mutable)
   - Query: Use specific helpers (get_incomplete_tasks, get_project_files)
   - Avoid: query_project_db(sql) - only if no helper exists
```

**Impact**: Removes SQL suggestions, emphasizes helper-first approach.

---

## Summary of Changes

| Fix | Lines | Change | User Note Impact |
|-----|-------|--------|------------------|
| 1 | 17-35 | Added "Functional Procedural" as explicit key principle | ✅ FP is now first core principle |
| 2 | 31-35 | Clarified optional vs mandatory features | ✅ Nuanced: FP/directives mandatory, tracking optional |
| 3 | 65-67 | Changed get_all_directives() to search_directives(type) | ✅ Reduces memory, loads only needed directives |
| 4 | 266-269 | Added flexibility qualifier to helper categories | ✅ AI can call any helper when needed |
| 5 | 293-302 | Reordered database query policy (helpers first) | ✅ SQL is last resort, not "acceptable" |
| 6 | 308-314 | Removed query_mcp_db suggestions | ✅ Consistent with helper-first policy |

**Total changes**: 6 fixes across 50+ lines

---

## User Notes Status

### ✅ All Critical Notes Addressed

1. **"Functional Procedural programming is a key principle"** → ✅ Now explicit (line 22)
2. **"Should get directives based on intent keywords, or type"** → ✅ search_directives(type) (line 65)
3. **"4 databases and purpose should be listed"** → ✅ Already present (lines 304-320)
4. **"directive_flow files are dev only, database has directive_flow table"** → ✅ Already correct (line 255)
5. **"Must include existing project FP check"** → ✅ Already present (lines 208-217)
6. **"FP should be closer to the top"** → ✅ Already at line 76
7. **"No hard-coded numbers"** → ✅ Zero hard-coded numbers
8. **"No need for direct queries... should have helper functions"** → ✅ Fixed (lines 293-314)
9. **"Should not limit AI so much on helper usage"** → ✅ Fixed (line 266)
10. **"There are some optional features"** → ✅ Fixed (line 34)

### ⚠️ Verification Needed (Not in System Prompt)

**User Note (line 90)**: "check to ensure these helper functions actually exist"
- get_next_directives_from_status
- get_completion_loop_target

**Action**: Verify these exist in aifp_core.db helper_functions table (separate task).

---

## Before vs After Metrics

| Metric | Before (prev3) | After (current) | Change |
|--------|----------------|-----------------|--------|
| **Total lines** | 429 | 438 | +9 (added detail) |
| **"Functional Procedural" mentions** | 0 | 1 | +1 (explicit) |
| **get_all_directives() calls** | 3 | 1 | -2 (replaced with search) |
| **Direct SQL suggestions** | 3 | 0 | -3 (removed) |
| **Helper flexibility qualifiers** | 0 | 2 | +2 (added) |
| **Hard-coded numbers** | 0 | 0 | 0 (maintained) |

---

## Files

**Production**: `sys-prompt/aifp_system_prompt.txt` (438 lines) ✅

**Backups**:
- `sys-prompt/previous/aifp_system_prompt_old.txt` (576 lines - pre-Phase 7)
- `sys-prompt/previous/aifp_system_prompt_prev1.txt` (724 lines - post-Phase 8, too verbose)
- `sys-prompt/previous/aifp_system_prompt_prev2.txt` (275 lines - too minimal)
- `sys-prompt/previous/aifp_system_prompt_prev3.txt` (429 lines - before user note fixes)

**Documentation**:
- `docs/SYSTEM_PROMPT_USER_NOTES_ANALYSIS.md` (detailed analysis of user notes)
- `docs/SYSTEM_PROMPT_FIXES_APPLIED.md` (this file - summary of applied fixes)
- `docs/SYSTEM_PROMPT_FINAL.md` (overall design rationale)

---

**Status**: ✅ All user notes addressed. System prompt now aligns with user's understanding of AIFP architecture.

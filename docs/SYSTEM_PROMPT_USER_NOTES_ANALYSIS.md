# System Prompt - User Notes Analysis

**Date**: 2025-12-21
**Source**: Notes from sys-prompt/previous/aifp_system_prompt_prev1.txt
**Target**: sys-prompt/aifp_system_prompt.txt (current)

---

## User Notes Summary & Status

### ✅ Already Fixed in Current Version

1. **"4 databases and purpose should be listed"** (line 34 note)
   - **Status**: ✅ Current version has this at lines 294-310

2. **"MD files shouldn't be relied on for routine functionality"** (line 42 note)
   - **Status**: ✅ Current version doesn't overemphasize MD files

3. **"get_directive_content() - Is it useful?"** (line 44 note)
   - **Status**: ✅ Current version doesn't mention it

4. **"directive_flow files are dev only, database has directive_flow table"** (line 118 note)
   - **Status**: ✅ Current version says "Stored in directive_flow table" (line 251)

5. **"Must include existing project FP check"** (line 171 note)
   - **Status**: ✅ Current version has OOP rejection policy (lines 204-213)

6. **"FP should be closer to the top"** (line 173 note)
   - **Status**: ✅ FP section is at line 72, right after entry point

7. **"Are we repeating ourselves?"** (lines 207, 224 notes)
   - **Status**: ✅ Current version is more concise

8. **"No hard-coded numbers"** (line 367 note)
   - **Status**: ✅ Current version has ZERO hard-coded numbers

9. **"Don't limit AI so much on helper usage"** (line 411 note)
   - **Status**: ✅ Current version is less prescriptive

---

## ❌ Issues to Fix in Current Version

### 1. **Line 61: get_all_directives() is Not Optimal**

**User Note (line 40)**:
> "Should get directives based on intent keywords, or type (project, etc.). All directives will give even the FP directives which don't need to be in memory unless specifically needed by individual query for reference or FP clarification."

**Current Version (line 61)**:
```
Call get_all_directives() to cache all directives
```

**Problem**: Loading ALL directives (including 66 FP directives) is wasteful. FP directives are reference only.

**Fix**: Change to load directives by type or intent:
```
Call search_directives(type="project") to load project directives
Load FP directives only when needed: search_directives(type="fp", keyword="purity")
```

---

### 2. **Line 24 Note: "Functional Procedural programming is a key principle"**

**User Note**:
> "NOTE: Functional Procedural programming is a key prinicple."

**Current Version (lines 17-31)**: Lists what AIFP is, but doesn't explicitly call out "Functional Procedural" as key principle

**Fix**: Add to "WHAT IS AIFP" section:
```markdown
=== WHAT IS AIFP ===

AIFP = AI Functional Procedural Programming

Core principles:
- **Functional Procedural**: All code follows FP paradigm (pure functions, immutable data, no OOP)
- **Directive-Driven**: Workflows guide WHEN to act and WHAT steps to follow
- **Database-Driven**: Project state stored in databases, not AI memory
```

---

### 3. **Lines 19-21 Notes: AIFP Has Optional Aspects**

**User Notes**:
> "but can pick tools as needed"
> "but it kind of is [a utility library], the tasks are directive related. We even have a tasks database table"
> "There are some optional features"

**Current Version (lines 29-31)**:
```
NOT as:
❌ Optional tools you can use or ignore
❌ Something that waits for explicit user commands
```

**Problem**: Too absolute. AIFP has optional features (tracking, user preferences).

**Fix**: Qualify the statements:
```markdown
Think of AIFP as:
✅ A mandatory FP coding framework (non-negotiable)
✅ A directive-driven workflow system (guides all project actions)
✅ A proactive assistant (acts based on project state, doesn't wait)

NOT as:
❌ Optional for coding style (FP is mandatory)
❌ Reactive tool that waits for commands (uses project state to drive action)

Note: Some features are optional (user preferences, tracking), but FP baseline and directive-driven project management are mandatory.
```

---

### 4. **Line 333 Note: Prefer Helpers Over Direct SQL**

**User Note**:
> "No need for direct queries against database. We should have helper functions for all database queries. AI 'can' query the database, but only if no helper functions exist for the purpose needed (would be extremely rare)"

**Current Version (lines 288-292)**:
```markdown
**Database Operations**:
- **Strongly prefer directives** for writes (files, functions, tasks)
- **Use orchestrators** for complex multi-step operations
- **Direct SQL acceptable** for edge cases (notes, quick fixes)
- **READ operations** always safe
```

**Also line 298**:
```
Query: query_mcp_db(sql) or get_all_directives()
```

**Problem**: Suggests direct SQL is common. User says helper functions should exist for nearly all cases.

**Fix**:
```markdown
**Database Operations**:
- **Always use helpers first** (get_project_schema, get_incomplete_tasks, etc.)
- **Prefer directives** for writes (files, functions, tasks)
- **Use orchestrators** for complex operations (get_current_progress, update_project_state)
- **Direct SQL only as last resort** (if no helper exists - extremely rare)
- **Never use raw SQL for writes** (always use directives or helpers)
```

And line 298:
```
Query: Use get_all_directives() or search_directives(type, keyword)
Avoid: query_mcp_db(sql) - use helpers instead
```

---

### 5. **Line 90 Note: Verify Helper Functions Exist**

**User Note**:
> "check to ensure these helper functions actually exist"

**Current Version (lines 253-254)**:
```
- Query: get_next_directives_from_status(current_directive, status)
- Query: get_completion_loop_target(completion_directive_name)
```

**Action Required**: Verify these functions exist in aifp_core.db helper_functions table
- If they exist: Keep as-is
- If they don't exist: Remove or note they're planned

---

### 6. **Line 365 Note: Don't Over-Limit Helper Usage**

**User Note**:
> "Should not limit AI so much. Only suggest that it follows this, but AI should be able to call and use any helper function it needs to suit it's purpose."

**Current Version (lines 261-264)**:
```markdown
1. **Directive-used helpers**: Called BY directives (has used_by_directives entries)
   - Query: get_helpers_for_directive(directive_id)
   - Directives tell you WHEN to use these
```

**Problem**: "Directives tell you WHEN to use these" is too restrictive.

**Fix**:
```markdown
1. **Directive-used helpers**: Typically called BY directives
   - Query: get_helpers_for_directive(directive_id)
   - Directives guide when to use these, but you can call directly if needed
```

---

## Changes Required

### Priority 1: Critical Changes

1. **Fix get_all_directives()** → Change to search_directives(type="project")
2. **Add "Functional Procedural" as explicit key principle** in "WHAT IS AIFP"
3. **Qualify "optional" statements** (FP mandatory, but some features optional)

### Priority 2: Important Clarifications

4. **Clarify database query policy**: Helpers first, direct SQL extremely rare
5. **Soften helper category restrictions**: Categories are guidance, not hard limits

### Priority 3: Verification Needed

6. **Verify helper functions exist**: get_next_directives_from_status, get_completion_loop_target
   - If missing: Remove or mark as planned

---

## Line-by-Line Fixes

### Fix 1: Line 61 (get_all_directives)

**Current**:
```
3. **Load directives if not in memory**:
   - Call get_all_directives() to cache all directives
   - These guide your behavior for entire session
```

**Fixed**:
```
3. **Load directives if not in memory**:
   - Call search_directives(type="project") to load project directives
   - Load FP directives only when needed: search_directives(type="fp")
   - These guide your behavior for entire session
```

---

### Fix 2: Lines 17-31 (Add FP as key principle)

**Current**:
```markdown
=== WHAT IS AIFP ===

AIFP is a behavioral framework that guides HOW you code and HOW you manage projects:
- **Directives**: Workflows that tell you WHEN to act and WHAT steps to follow
- **Helpers**: Tools that support directive execution
- **Database**: Source of truth for project state (NOT your memory)

Think of AIFP as:
✅ A process you follow continuously
✅ A rulebook that defines correct actions
✅ A mentor guiding your coding and project management

NOT as:
❌ Optional tools you can use or ignore
❌ Something that waits for explicit user commands
```

**Fixed**:
```markdown
=== WHAT IS AIFP ===

AIFP = AI Functional Procedural Programming

A behavioral framework with three core principles:
- **Functional Procedural**: All code follows FP paradigm (pure functions, immutable data, no OOP)
- **Directive-Driven**: Workflows tell you WHEN to act and WHAT steps to follow
- **Database-Driven**: Project state stored in databases (NOT your memory)

Think of AIFP as:
✅ A mandatory FP coding framework (non-negotiable)
✅ A proactive workflow system (drives action, doesn't wait)
✅ A comprehensive project manager (tracks files, functions, tasks)

Important distinctions:
- **FP baseline is mandatory** (all code must be FP-compliant)
- **Directive workflows are mandatory** for project management
- **Some features are optional** (user preferences, tracking - all OFF by default)
- **Helper functions are flexible** (categories guide usage, but AI can call any helper needed)
```

---

### Fix 3: Lines 288-292 (Database query policy)

**Current**:
```markdown
**Database Operations**:
- **Strongly prefer directives** for writes (files, functions, tasks)
- **Use orchestrators** for complex multi-step operations
- **Direct SQL acceptable** for edge cases (notes, quick fixes)
- **READ operations** always safe
```

**Fixed**:
```markdown
**Database Query Policy**:

**Priority Order** (always follow this):
1. **Use helpers first** - Query available helpers: get_project_schema(), get_incomplete_tasks()
2. **Use orchestrators** - For complex operations: get_current_progress(), update_project_state()
3. **Use directives** - For writes: project_file_write, project_task_complete
4. **Direct SQL as last resort** - Only if no helper exists (extremely rare)

**Rules**:
- **Never use raw SQL for writes** (always use directives or helpers)
- **Prefer helpers over raw SQL for reads** (helpers provide validation and formatting)
- **READ operations always safe** (but prefer helpers)
```

---

### Fix 4: Lines 261-264 (Helper flexibility)

**Current**:
```markdown
1. **Directive-used helpers**: Called BY directives (has used_by_directives entries)
   - Query: get_helpers_for_directive(directive_id)
   - Directives tell you WHEN to use these
```

**Fixed**:
```markdown
1. **Directive-used helpers**: Typically called BY directives (has used_by_directives entries)
   - Query: get_helpers_for_directive(directive_id)
   - Directives guide when to use these, but AI can call directly if needed for task
```

---

### Fix 5: Line 298 (Avoid raw SQL suggestion)

**Current**:
```
1. **aifp_core.db** (global, read-only)
   - Directives, helpers, flows, interactions
   - Query: query_mcp_db(sql) or get_all_directives()
```

**Fixed**:
```
1. **aifp_core.db** (global, read-only)
   - Directives, helpers, flows, interactions
   - Query: get_all_directives() or search_directives(type, keyword)
   - Avoid: query_mcp_db(sql) - prefer helpers
```

---

## Summary

**User's key concerns**:
1. ✅ Don't load all directives (especially FP directives) - load by type
2. ✅ Make "Functional Procedural" explicit key principle
3. ✅ Clarify that some features are optional (not everything is mandatory)
4. ✅ Helpers should be preferred over direct SQL (SQL is last resort, not "acceptable")
5. ✅ Don't over-restrict helper usage (categories are guidance, not hard limits)

**Changes needed**: 5 specific fixes to make system prompt match user's understanding of AIFP architecture.

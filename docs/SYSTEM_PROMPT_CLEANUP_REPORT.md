# System Prompt Cleanup Report

**Date**: 2025-12-21
**Old Version**: sys-prompt/previous/aifp_system_prompt_prev1.txt (724 lines)
**New Version**: sys-prompt/aifp_system_prompt.txt (275 lines)
**Reduction**: -449 lines (-62% smaller)

---

## Executive Summary

Transformed the system prompt from a **comprehensive reference manual** (724 lines) into a **focused entry point guide** (275 lines) that trusts directives to provide detailed workflows.

### Key Philosophy Shift

**Before**: System prompt tried to explain everything
**After**: System prompt tells AI where to find everything

---

## What Was Removed (and Where It Went)

### 1. Extensive Directive Flow Documentation (~50 lines removed)
**Before**: Detailed explanation of 5 flow types, query functions, workflow patterns, examples
**After**: 9 lines in "Quick Reference" section pointing to directive_flow table and key query functions

**Rationale**:
- The `aifp_run` directive already contains complete guidance on directive flows (lines 44-80 in directives-project.json)
- AI can query directive_flow table at runtime
- System prompt should point, not explain

**Where Details Live Now**:
- aifp_run directive workflow (lines 48-53)
- directive_flow table in aifp_core.db
- Directive MD files (src/aifp/reference/directives/)

---

### 2. Detailed Helper Classification (~80 lines removed)
**Before**: Extensive breakdown of 3 helper categories with examples, percentages, usage patterns
**After**: 5 lines listing three categories and pointing to database queries

**Rationale**:
- Removed hard-coded numbers (84 helpers, 118 helpers, 41.6%, 58.4%)
- AI should query helper_functions table for current counts and relationships
- Directives tell AI which helpers to use

**Where Details Live Now**:
- helper_functions table in aifp_core.db (is_tool, is_sub_helper, used_by_directives fields)
- get_helpers_for_directive(directive_id) query function
- Directive workflows specify helper usage

---

### 3. Two Helper Usage Patterns (~40 lines removed)
**Before**: Detailed Pattern 1 (directive-guided) and Pattern 2 (direct AI usage) with code examples
**After**: Implied in "Directives tell you WHEN to use helpers" principle

**Rationale**:
- Helper usage is directive-specific, not universal
- Each directive workflow specifies which helpers to call and when
- System prompt doesn't need to repeat this

**Where Details Live Now**:
- Individual directive workflows (trunk → branches with helper calls)
- get_helpers_for_directive() returns execution_context and sequence_order

---

### 4. Privacy & Tracking Detailed Section (~40 lines removed)
**Before**: Full section with 4 tracking features, purposes, enabling process, 5 privacy principles
**After**: 9 lines in "User Preferences & Privacy" stating all tracking OFF by default, listing 4 features, pointing to tracking_toggle directive

**Rationale**:
- Privacy stance is clear: ALL OFF BY DEFAULT
- tracking_toggle directive handles enabling/disabling with token cost warnings
- No need for extensive explanation in system prompt

**Where Details Live Now**:
- tracking_toggle directive
- user_preferences.db schema (tracking_settings table)
- Directive MD documentation

---

### 5. Extended Use Case Examples (~40 lines removed)
**Before**: Detailed directory structure examples for Use Case 1 and 2
**After**: 13 lines with concise descriptions and key distinguishing feature (user_directives_status field)

**Rationale**:
- Concept is simple: Use Case 1 = regular dev, Use Case 2 = automation
- AI can check project.user_directives_status to identify case
- Detailed examples belong in documentation, not system prompt

**Where Details Live Now**:
- README.md (lines 34-50)
- Blueprint (blueprint_aifp_project_structure.md)
- User System directive MD files

---

### 6. Extensive Action-Reaction Examples (~30 lines removed)
**Before**: Detailed action-reaction model for 5 scenarios (write code, discussion, create tasks, parse directives, git)
**After**: Integrated into "Core Behavioral Principles" section (lines 60-78)

**Rationale**:
- Action-reaction is implicit in directive workflows
- System prompt should state principle, not enumerate all cases
- Directives handle specific scenarios

**Where Details Live Now**:
- Directive workflows
- Directive interactions (triggers, depends_on fields)

---

### 7. Detailed Helper Examples (~50 lines removed)
**Before**: 40+ specific helper function examples organized by category
**After**: 4 key query functions in "Quick Reference" (get_all_directives, get_directive, get_helpers_for_directive, get_next_directives_from_status)

**Rationale**:
- AI should query helper_functions table for available helpers
- Directives specify which helpers to use for each task
- Hard-coded helper lists become outdated

**Where Details Live Now**:
- helper_functions table in aifp_core.db
- Consolidated helper documentation (docs/helpers/consolidated/)
- Directive workflows

---

### 8. Extended User Preference Workflow (~20 lines removed)
**Before**: Detailed workflow steps, learning process, confirmation flow
**After**: 4 lines stating key concept (atomic overrides) and listing directives

**Rationale**:
- user_preferences_sync, user_preferences_update, user_preferences_learn directives handle the workflow
- System prompt should point to directives, not duplicate their workflows

**Where Details Live Now**:
- User Preference directive MD files (7 directives)
- directive_flow_user_preferences.json (14 flows)

---

### 9. Extensive Git Collaboration Details (~30 lines removed)
**Before**: Detailed FP+Git advantages, conflict resolution strategy, branch naming, examples
**After**: 8 lines with key advantages and directive names

**Rationale**:
- Git directives contain complete workflows
- System prompt should state why AIFP+Git is superior, not how to do it
- Directives handle the how

**Where Details Live Now**:
- Git directive MD files (6 directives)
- Git directive workflows in directives-git.json

---

### 10. Redundant Status Management Explanations (~30 lines removed)
**Before**: Extensive status caching strategy, example flows, when to refresh
**After**: Integrated into "Entry Point" section (lines 22-25)

**Rationale**:
- Status management is part of entry point flow
- aifp_run directive contains complete guidance on get_status parameter

**Where Details Live Now**:
- aifp_run directive workflow (lines 14-30, 63-54 in directives-project.json)

---

## What Was Added or Enhanced

### 1. Crystal Clear Entry Point (lines 18-41)
**New**: Numbered steps showing exactly what to do on EVERY request
- Step 1: Call aifp_run with get_status parameter
- Step 2: Check if directives cached, load if not
- Step 3: Follow aifp_run guidance
- Step 4: Let directives guide next actions

**Why**: This is the #1 most important thing AI needs to know

---

### 2. "Trust the Directives" Philosophy (line 273)
**New**: Explicit statement that directives contain complete workflows, helper instructions, examples
**Why**: Reinforces that system prompt is entry point, directives are detailed guides

---

### 3. Database-Driven Emphasis (lines 79-87)
**New**: Explicit principle: "Query the database at runtime for... Never assume hard-coded numbers"
**Why**: Addresses the hard-coded number problem directly

---

### 4. Consolidated Quick Reference (lines 89-136)
**New**: Single section with 4 subsections (Directives, Helpers, Flows, Databases) each with key query functions
**Why**: AI knows exactly where to query for details without reading extensive explanations

---

## Structural Comparison

### Old Structure (724 lines)
```
CRITICAL: Understanding AIFP MCP (24 lines)
SYSTEM OVERVIEW (14 lines)
CRITICAL RULE: AUTOMATIC EXECUTION (9 lines)
FIRST INTERACTION SETUP (9 lines)
STATUS MANAGEMENT: EFFICIENCY OPTIMIZATION (41 lines)
DIRECTIVE FLOW SYSTEM (50 lines) ← Removed
TASK TYPE EVALUATION (18 lines)
DIRECTIVE-GUIDED BEHAVIOR (29 lines)
DIRECTIVE CATEGORIES (54 lines)
ACTION-REACTION MODEL (26 lines) ← Condensed
HELPER FUNCTIONS - SUPPORTING TOOLS (115 lines) ← Drastically reduced
KEY RULES (48 lines)
FP + GIT COLLABORATION ADVANTAGE (19 lines)
TWO DISTINCT USE CASES (46 lines) ← Condensed
USER PREFERENCES HIERARCHY (25 lines) ← Condensed
PRIVACY & TRACKING (40 lines) ← Reduced
DATABASE ARCHITECTURE (27 lines)
WHEN NOT TO USE AIFP (12 lines)
DIRECTIVE REFRESH (7 lines)
DIRECTIVE MD DOCUMENTATION (22 lines)
SUMMARY (20 lines)
```

### New Structure (275 lines)
```
WHAT IS AIFP (16 lines) ← Focused concept
ENTRY POINT: HOW TO START (24 lines) ← CRYSTAL CLEAR
CORE BEHAVIORAL PRINCIPLES (45 lines) ← Consolidated
QUICK REFERENCE (48 lines) ← Pointers to details
KEY RULES (35 lines) ← Essential only
TWO DISTINCT USE CASES (14 lines) ← Concise
USER PREFERENCES & PRIVACY (14 lines) ← Combined
FP + GIT COLLABORATION ADVANTAGE (11 lines) ← Key points
DIRECTIVE WORKFLOW PATTERN (15 lines) ← Essential pattern
WHEN NOT TO USE AIFP (10 lines)
DIRECTIVE REFRESH (6 lines)
SUMMARY (21 lines) ← Reinforces entry point
```

**Key Difference**: Old = reference manual, New = quick-start guide

---

## Metrics

| Metric | Old | New | Change |
|--------|-----|-----|--------|
| **Total Lines** | 724 | 275 | -449 (-62%) |
| **Major Sections** | 20 | 12 | -8 |
| **Hard-Coded Numbers** | 10 | 0 | -10 ✅ |
| **Helper Examples** | 40+ | 4 | -36 |
| **Directive Flow Details** | 50 lines | 9 lines | -41 |
| **Privacy Details** | 40 lines | 9 lines | -31 |
| **Entry Point Clarity** | Scattered | 24 focused lines | ⬆️ Improved |

---

## Philosophy Changes

### Old Philosophy
"The system prompt should teach AI everything about AIFP"

### New Philosophy
"The system prompt should teach AI WHERE to find everything in AIFP"

**Key Principles**:
1. **Entry point is king**: AI must know exactly how to start (aifp_run → get_all_directives → follow directives)
2. **Trust directives**: They contain complete workflows, AI should follow them
3. **Query at runtime**: Database is source of truth, not hard-coded numbers in prompt
4. **Focused, not comprehensive**: System prompt is quick-start guide, not reference manual
5. **No duplication**: If directive explains it, system prompt points to it

---

## Benefits of New Approach

### 1. **Maintainability** ✅
- No hard-coded numbers to update
- Directive changes don't require system prompt updates
- Helper additions don't require system prompt updates

### 2. **Clarity** ✅
- Entry point is crystal clear (4 numbered steps)
- Less cognitive load for AI
- Focus on "what to do" not "how it works"

### 3. **Flexibility** ✅
- AI queries database for current state
- Directives can evolve without breaking system prompt
- Helper classification can change without system prompt updates

### 4. **Size** ✅
- 62% smaller (724 → 275 lines)
- Faster to load, easier to fit in context
- More room for actual directive content in context

### 5. **Accuracy** ✅
- No risk of system prompt contradicting directives
- Single source of truth (directives in database)
- AI always gets current information via queries

---

## Testing Checklist

To verify the new system prompt works correctly, AI should be able to:

- [ ] Automatically call aifp_run on first interaction
- [ ] Call aifp_run with get_status=true on first interaction
- [ ] Call get_all_directives() when directives not in memory
- [ ] Follow guidance from aifp_run response
- [ ] Query get_directive(name) for specific directive details
- [ ] Query get_helpers_for_directive(directive_id) to find helpers
- [ ] Query get_next_directives_from_status() to navigate workflows
- [ ] Call aifp_status when user says "continue", "status", "resume"
- [ ] Write FP-compliant code (pure, immutable, no OOP)
- [ ] Call project_file_write after writing code
- [ ] Check get_project_status() before project_init
- [ ] Query database for counts instead of assuming hard-coded numbers
- [ ] Let directives guide helper usage (not system prompt)

---

## Backup Policy

**Backup Location**: `sys-prompt/previous/`
**Naming Convention**: `aifp_system_prompt_prevN.txt` (where N increments)

**Current Backups**:
- `aifp_system_prompt_old.txt` - Pre-Phase 7 version (576 lines)
- `aifp_system_prompt_prev1.txt` - Post-Phase 8 version (724 lines)

**Current Version**:
- `aifp_system_prompt.txt` - Streamlined version (275 lines)

---

## Conclusion

Successfully transformed system prompt from a **724-line reference manual** into a **275-line quick-start guide** that:
- ✅ Removes all hard-coded numbers
- ✅ Trusts directives to provide workflows
- ✅ Makes entry point crystal clear
- ✅ Reduces size by 62%
- ✅ Points AI to database queries for details
- ✅ Eliminates duplication between prompt and directives

**Bottom Line**: AI now knows **HOW TO START** and **WHERE TO LOOK** without the system prompt trying to explain everything.

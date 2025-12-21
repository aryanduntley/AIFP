# System Prompt Comparison: Old vs New

**Date**: 2025-12-21
**Old Version**: aifp_system_prompt_old.txt (576 lines)
**New Version**: aifp_system_prompt.txt (724 lines)
**Change**: +148 lines (+25.7% increase)

---

## Summary of Changes

### Size Comparison

| Metric | Old | New | Change |
|--------|-----|-----|--------|
| **Total Lines** | 576 | 724 | +148 (+25.7%) |
| **Major Sections** | 15 | 18 | +3 |
| **Hard-Coded Numbers** | ~5 | ~10 | ⚠️ Increased |

---

## What Was Added

### 1. **DIRECTIVE FLOW SYSTEM Section** (NEW - ~50 lines)
**Location**: After "Status Management" section

**Content Added**:
- Explains directive flow files (89 project flows + 14 user preference flows)
- Documents 5 flow types (conditional, completion_loop, canonical, status_branch, utility)
- Shows 3 flow query functions with examples
- Demonstrates workflow navigation pattern
- Provides concrete navigation example

**Why Added**: Flow files are fundamental to workflow navigation and were completely missing

**Critical Issue**: Hard-codes flow counts (89, 14) - should query database

---

### 2. **Enhanced Helper Classification Section** (~80 lines)
**Location**: Helper Functions section

**What Changed**:
- **OLD**: "Most helpers are called through directive workflows"
- **NEW**: "Three categories of helpers" with detailed breakdown

**New Content**:
```markdown
**Three Categories of Helpers**:

1. **Directive-Used Helpers** (84 helpers, 41.6%)  ⚠️ HARD NUMBER
   - Have entries in used_by_directives array
   - Called BY directive workflows
   - Let directives instruct you when to use them

2. **AI-Only Tools** (118 helpers, 58.4%)  ⚠️ HARD NUMBER
   - is_tool = TRUE and used_by_directives = [] (empty array)
   - Called BY YOU directly for exploration, querying, batch operations
   - Categories:
     - Schema/query tools
     - Batch helpers
     - Delete helpers
     - Generic CRUD
     - Advanced filtering
     - Reorder/management

3. **Sub-Helpers**
   - is_sub_helper = TRUE
   - Called BY other helpers, not directly
```

**Why Changed**: Original text was factually incorrect - 118 tools are for direct AI use, not "only through directive workflows"

**Critical Issue**: Hard-codes helper counts (84, 118) - should query database

---

### 3. **TWO PATTERNS FOR HELPER USAGE Section** (NEW - ~40 lines)
**Location**: After Helper Classification

**Content Added**:
- **Pattern 1**: Directive-Guided (for 84 directive-used helpers)
- **Pattern 2**: Direct AI Usage (for 118 AI-only tools)
- Shows concrete examples for each pattern
- Explains how to know which pattern to use

**Example**:
```python
# Pattern 2: Direct AI Usage (for 118 AI-only tools)
# When exploring project state or performing utility operations:
- Call get_incomplete_tasks() directly → See what's pending
- Call get_project_schema() directly → Understand database structure
- Call query_settings() directly → Check user preferences

# No directive needed - these are YOUR exploration and utility tools
```

**Why Added**: Makes it crystal clear when to use each approach

---

### 4. **Enhanced User Preference Directives** (~10 lines)
**Location**: Directive Categories section

**What Changed**:
- **OLD**: Listed 3 directives
- **NEW**: Lists all 7 directives

**New Directives Added**:
- user_preferences_export
- user_preferences_import
- project_notes_log
- tracking_toggle

**Additional Info**:
- Documents 14 flows in directive_flow_user_preferences.json ⚠️ HARD NUMBER
- Shows preferences override default behavior

**Why Changed**: Reflects Phase 7 completion

---

### 5. **PRIVACY & TRACKING Section** (NEW - ~40 lines)
**Location**: After User Preferences Hierarchy

**Content Added**:
- **Default State: ALL TRACKING OFF** (prominent heading)
- Documents all 4 tracking features with clear purposes:
  1. fp_flow_tracking (OFF by default)
  2. ai_interaction_log (OFF by default, required for user_preferences_learn)
  3. helper_function_logging (OFF by default, required for project_performance_summary)
  4. issue_reports (OFF by default)
- Shows token overhead warnings
- Explains granular control
- Lists 5 privacy principles

**Why Added**: Makes privacy stance explicit and prominent

---

### 6. **Updated User Preferences Workflow**
**Location**: User Preferences Hierarchy section

**What Changed**:
- **OLD**: "Before executing directive, call user_preferences_sync"
- **NEW**: "Before executing customizable directive, user_preferences_sync is auto-called"

**Why Changed**: Reflects automatic prerequisite pattern from Phase 7

---

## What Was Removed

**Nothing was removed** - only additions and enhancements

---

## Critical Issues Found

### ⚠️ Hard-Coded Numbers (Should Be Removed)

The new system prompt contains **more hard-coded numbers than the old one**:

| Location | Hard-Coded Value | Should Be |
|----------|------------------|-----------|
| Line 107 | "89 flows" | Query: `SELECT COUNT(*) FROM directive_flow WHERE flow_file = 'directive_flow_project.json'` |
| Line 108 | "14 flows" | Query: `SELECT COUNT(*) FROM directive_flow WHERE flow_file = 'directive_flow_user_preferences.json'` |
| Line 236 | "14 directive flows" | Same as above |
| Line 309 | "84 helpers, 41.6%" | Query: `SELECT COUNT(*) FROM helper_functions WHERE used_by_directives != '[]'` |
| Line 319 | "118 helpers, 58.4%" | Query: `SELECT COUNT(*) FROM helper_functions WHERE is_tool = 1 AND used_by_directives = '[]'` |

**Recommendation**: Replace all hard numbers with:
1. Qualitative descriptions ("comprehensive set of", "majority of")
2. SQL queries AI should run
3. References to "query database for current counts"

**Note**: Line 33 already says "Query database for exact counts and relationships at runtime" but this is contradicted by hard numbers elsewhere.

---

## Section-by-Section Comparison

### Core Concepts (Lines 1-24)
- ✅ **No change** - Still excellent

### System Overview (Lines 25-39)
- ✅ **No change** - Already has "query database" note

### Execution Rules (Lines 40-101)
- ✅ **No change** - Status efficiency section still perfect

### Task Evaluation (Lines 102-120)
- ✅ **No change** - Clear task types

### **NEW: Directive Flow System (Lines 102-151)**
- ➕ **Added** - Critical workflow navigation info
- ⚠️ **Issue**: Hard-coded flow counts (89, 14)

### Directive-Guided Behavior (Lines 121-150)
- ✅ **No change** - Behavioral principles unchanged

### Directive Categories (Lines 151-205)
- ✏️ **Enhanced** - User Preference directives now complete (7/7)
- ⚠️ **Issue**: Hard-coded "14 flows" reference

### Action-Reaction Model (Lines 206-232)
- ✅ **No change** - Patterns still clear

### Helper Functions (Lines 233-348)
- ✏️ **Completely rewritten** - Helper classification corrected
- ➕ **Added** - Two patterns for helper usage
- ⚠️ **Issue**: Hard-coded helper counts (84, 118)

### Key Rules (Lines 349-396)
- ✅ **No change** - FP baseline unchanged

### FP+Git Collaboration (Lines 397-415)
- ✅ **No change** - Git advantages clear

### Two Use Cases (Lines 416-461)
- ✅ **No change** - Use case distinction maintained

### User Preferences (Lines 462-487)
- ✏️ **Updated** - Changed "call" to "auto-called"
- ✏️ **Updated** - Added "(opt-in only, OFF by default)" qualifier

### **NEW: Privacy & Tracking (Lines 595-634)**
- ➕ **Added** - Makes privacy-first design explicit
- Shows all 4 tracking features
- Emphasizes opt-in only approach

### Database Architecture (Lines 488-514)
- ✅ **No change** - Four databases well documented

### When Not to Use AIFP (Lines 515-526)
- ✅ **No change** - Clear guidelines

### Directive MD Documentation (Lines 534-556)
- ✅ **No change** - Documentation structure clear

### Summary (Lines 557-576)
- ✅ **No change** - Core message intact

---

## Recommendations

### Priority 1: Remove Hard-Coded Numbers (CRITICAL)
Replace specific counts with:
```markdown
# Instead of:
**2. AI-Only Tools** (118 helpers, 58.4%)

# Use:
**2. AI-Only Tools** (majority of helpers - query database for current count)
- Query: SELECT COUNT(*) FROM helper_functions WHERE is_tool = 1 AND used_by_directives = '[]'
```

### Priority 2: Consolidate for Efficiency (IMPORTANT)
Current structure has some redundancy. Suggested consolidation:

1. **Merge Directive Flow with Directive-Guided Behavior** → "Workflow Navigation" (save ~20 lines)
2. **Merge Privacy & Tracking with User Preferences** → "Customization & Privacy" (save ~15 lines)
3. **Condense Helper Examples** → Remove some redundant examples (save ~20 lines)

**Estimated savings**: 55 lines (from 724 to ~669 lines, still 16% larger than original)

### Priority 3: Consider Separate Architectural Doc (OPTIONAL)
Move these to separate reference doc:
- Detailed helper examples (lines 286-338)
- Advanced workflow patterns (lines 102-151)
- Extended use case examples (lines 416-461)

This could reduce system prompt to ~550 lines while keeping all critical behavioral instructions.

**Trade-off**: AI would need to call `get_reference_doc()` for detailed examples, adding one extra step.

---

## Bottom Line

### ✅ What Improved
1. **Helper classification is now accurate** (was factually wrong before)
2. **Directive flows documented** (was completely missing)
3. **Privacy stance is prominent** (was buried)
4. **User preference directives complete** (was incomplete)
5. **Two helper usage patterns clearly explained** (was ambiguous)

### ⚠️ What Needs Fixing
1. **Hard-coded numbers everywhere** (contradicts "query database" principle)
2. **25.7% size increase** (from 576 to 724 lines)
3. **Some redundancy** (could consolidate certain sections)

### 🎯 Action Items
1. **Must fix**: Remove all hard-coded counts, replace with queries or qualitative descriptions
2. **Should do**: Consolidate related sections (flows+behavior, privacy+preferences)
3. **Nice to have**: Create companion architectural doc for detailed examples

---

**Verdict**: The new system prompt is **more accurate and complete**, but needs cleanup for hard-coded numbers and could benefit from consolidation to reduce size.

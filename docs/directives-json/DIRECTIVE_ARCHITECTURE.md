# Directive Architecture - Design Clarification

**Date**: 2025-12-13
**Issue**: Concern about 125 directives causing confusion and competing priorities
**Resolution**: Proper use of `type` field separates orchestration from reference

---

## The Initial Concern

With 125 directives in the system (~59 workflow + ~66 FP), there was concern that:

1. **Intent matching confusion** - Too many directives competing for attention
2. **Cognitive load** - AI spending too much effort on directive selection vs. actual work
3. **Priority confusion** - FP compliance competing with project management
4. **Wrong abstraction** - FP directives aren't "workflows" to invoke

**Key Insight**: FP directives (66 of 125) don't follow a "flow design" - they're coding principles, not process steps.

---

## The Core Misunderstanding

### ❌ Wrong Mental Model
Directives are discrete workflows that users or AI explicitly invoke:
```
User: "Run fp_purity on this function"
AI: "Executing fp_purity directive workflow..."
```

### ✅ Correct Mental Model
Directives are **AI guidance documents accessible via MCP**:
```
User: "Add authentication to the app"
AI internally:
  1. References aifp_run (orchestrator)
  2. Determines task needs file write
  3. References project_file_write (guidance)
  4. Writes code with FP principles (implicit)
  5. Updates project database

If uncertain about FP practice:
  6. Queries type='fp' directives for clarification
```

---

## The Architecture Already Works

### Database Schema Has the Solution

```sql
CREATE TABLE IF NOT EXISTS directives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('fp', 'project', 'git', 'user_system', 'user_preference')),
    ...
);
```

**The `type` field already separates concerns!**

---

## Directive Types and Their Purposes

### type='project' (~37 directives)
**Purpose**: Project orchestration and workflow guidance
**Examples**:
- `aifp_run` - Main orchestrator
- `project_init` - Initialize project
- `project_file_write` - Write code files
- `project_update_db` - Sync database

**When Queried**: When AI needs to know "What should I do next?" or "How do I accomplish this task?"

**Query Pattern**:
```python
# AI needs orchestration guidance
directives = query_directives(type='project', keywords=user_intent)
```

### type='fp' (~66 directives)
**Purpose**: FP coding standards and clarification reference
**Examples**:
- `fp_purity` - Function purity principles
- `fp_optionals` - Option type guidance
- `fp_borrow_check` - Reference lifetime rules

**When Queried**: ONLY when AI is uncertain about FP practice during code writing

**Query Pattern**:
```python
# AI writing code, unsure about specific FP practice
if uncertain_about_purity:
    guidance = query_directives(type='fp', keywords='purity side-effects')
```

**Critical Difference**: These are **reference documents**, not **workflow steps**

### type='git' (~6 directives)
**Purpose**: Git operation guidance
**When Queried**: When performing git operations

### type='user_system' (~9 directives)
**Purpose**: User directive automation system
**When Queried**: When handling user-defined automation directives

### type='user_preference' (~7 directives)
**Purpose**: User preference management
**When Queried**: When updating or syncing user preferences

---

## How AI Should Use Directives

### FP is Always-On Implicit Behavior

**System Prompt Provides Baseline FP Behavior:**
```
When writing code:
- All functions are pure (same input → same output, no side effects)
- No mutations (use immutable data structures)
- Error handling via Result/Option types
- Explicit dependencies (no hidden state)
- No OOP (classes, inheritance, mutation)

When uncertain about specific FP practice, query directives with type='fp'
```

**FP Directives = Clarification Reference:**
- AI doesn't query FP directives for every function
- AI queries them ONLY when ambiguous or uncertain
- Example: "Should this closure capture be immutable?" → Query `fp_borrow_check`

### Orchestration is Query-Driven

**AI queries orchestration directives based on user intent:**

```python
User: "Add authentication"

AI Process:
1. Parse intent: needs new feature
2. Query: type IN ('project', 'user_system') AND keywords LIKE '%file%write%'
3. Get guidance: project_file_write.md
4. Execute: Write files, update DB
5. Code follows FP implicitly (no explicit FP directive query)

If during step 4, AI uncertain about error handling:
6. Query: type='fp' AND keywords LIKE '%error%option%'
7. Get clarification: fp_optionals.md
8. Apply guidance, continue
```

---

## Why This Solves the Problem

### 1. No Directive Competition
- Orchestration queries filter `type IN ('project', 'git', 'user_system')`
- FP queries filter `type='fp'`
- Queried at **different times** for **different purposes**
- No confusion between "what to do" vs "how to code"

### 2. Reduced Cognitive Load
- AI doesn't consider all 125 directives at once
- Contextual filtering by type
- FP is mostly implicit (system prompt), only queried for clarification

### 3. Proper Abstraction
- FP directives aren't "invoked" like workflows
- They're referenced like documentation
- Separates process from principles

### 4. Maintains Granularity
- Keep 66 granular FP directives
- Specific answers to specific questions
- Easy to search: `type='fp' AND keywords='borrow lifetime'` → exact guidance

---

## Required Implementation Changes

### 1. System Prompt Enhancement
Add FP baseline behavior so AI doesn't need to query FP directives constantly:

```markdown
## Code Writing Principles (Always Follow)

Write all code following functional programming principles:
- **Pure functions**: Same inputs always produce same outputs, no side effects
- **Immutable data**: Use immutable data structures, no mutations
- **Explicit state**: All dependencies as parameters, no hidden state
- **Type safety**: Use Option/Result types for error handling, not exceptions
- **No OOP**: Avoid classes, inheritance, mutable objects
- **Composition**: Build complex functions from simple pure functions

When uncertain about specific FP practice, query directives with type='fp'.
```

### 2. Add Helper: `get_directives_by_type`

**Location**: `docs/helpers/helpers-consolidated-core.md`

```python
get_directives_by_type(type, include_md_content=False)
```

**Purpose**: Query directives filtered by type
**Parameters**:
- `type` (String) - One of: 'fp', 'project', 'git', 'user_system', 'user_preference'
- `include_md_content` (Boolean, default False) - Include full MD file content

**Returns**: Array of directive objects filtered by type

**Use Cases**:
```python
# Get all orchestration directives
orchestration = get_directives_by_type('project')

# Get FP reference directives for clarification
fp_guidance = get_directives_by_type('fp')

# Get with full MD content for reading
fp_with_docs = get_directives_by_type('fp', include_md_content=True)
```

**Implementation Note**: Add to core helpers, not project-specific helpers.

### 3. Update FP Directive MD Files

Add clarification to each FP directive's Purpose section:

```markdown
**Type**: FP Reference
**Purpose**: Clarification guidance for [specific FP practice]
**When to Reference**: When AI is uncertain about [specific scenario]

This directive is a reference document, not a workflow step.
Query this when writing code and uncertain about [practice].
```

### 4. Clarify Orchestration Directive MD Files

Ensure orchestration directives clearly indicate they're workflow guides:

```markdown
**Type**: Project Orchestration
**Purpose**: Workflow guidance for [specific task]
**When to Apply**: When user requests [task type]

This directive provides step-by-step guidance for accomplishing [task].
```

---

## The Mental Model

### For Users
Users never invoke directives. They just request work:
- ❌ "Run project_file_write"
- ✅ "Add a login page"

### For AI
AI uses directives as internal guidance:

1. **Start**: `aifp_run` orchestrates overall behavior
2. **Orchestration**: Query `type IN ('project', 'git', 'user_system')` for workflow guidance
3. **Coding**: Follow FP principles (system prompt baseline)
4. **Clarification**: Query `type='fp'` only when uncertain
5. **Tracking**: Update database continuously

### For Developers
Directives are organized guidance documents:
- **Orchestration directives** (~59): How to accomplish tasks
- **FP directives** (~66): How to write code when uncertain
- Separate concerns via `type` field
- Both accessible via MCP tools

---

## Decision: Keep Granular FP Directives

**Rationale**:
1. ✅ Architecture already separates via `type` field
2. ✅ Granular = precise answers to specific questions
3. ✅ Easy to search and extend
4. ✅ System prompt handles implicit FP behavior
5. ✅ FP directives queried only for clarification

**No consolidation needed** - the concern was based on misunderstanding how directives are used.

---

## Summary

### The Problem
Initial concern: 125 directives too many, causing confusion

### The Solution
Proper use of existing `type` field:
- **Orchestration directives**: Guide workflows (query often)
- **FP directives**: Clarify coding practices (query rarely)
- Queried at different times for different purposes
- No competition or confusion

### Action Items
1. ✅ Enhance system prompt with FP baseline behavior
2. ✅ Add `get_directives_by_type` helper to core helpers
3. ✅ Update FP directive MD files with clarification notes
4. ✅ Ensure orchestration directives clearly indicate workflow purpose

### Key Insight
**Directives don't compete when properly filtered by type and context.**

The architecture was correct all along - just needed clarification on usage patterns.

---

**Document Status**: Architecture Clarified ✅
**Next Steps**: Implement helper function and system prompt enhancements

# Return_Statements Quality Guide

**Purpose:** Simple, conceptual hints (0-2 lines) that guide AI after helper execution. Not prescriptive instructions, not execution engine, just helpful reminders.

---

## Core Principle

**Return statements are simple hints, questions, or reminders - NOT detailed specifications.**

**Original Vision Examples:**
- `"Verify flows are added, if necessary, for this file in file_flows table"`
- `"Ensure that any name or path changes are thoroughly changed in the code base as well"`
- `"Use the returned id(s) for file naming. File names should be suffixed with _id_xx"`
- `"Are there any flows that should be added in flow_themes?"`
- `"Do any database interactions need to be added for this function"`

**Style:**
- Questions to prompt thinking: `"Are there any...?"`
- Reminders: `"Ensure that..."`, `"Verify..."`
- Simple conventions: `"File names should be suffixed with -IDxx"`
- Conceptual hints: `"After creating milestone, you'll likely need to create tasks for it"`

**Length:** 0-2 lines maximum (often 0-1 lines)

**Structure:** NO categories (no DATABASE CONTEXT:, NEXT STEP:, CHECK:, etc.)

---

## When to Add Return Statements

### ✅ Add When Helpful

1. **Related actions often forgotten**
   - Example: `"Verify flows are added in file_flows table"`
   - Why: AI might forget this related step

2. **Naming conventions**
   - Example: `"Function names should be suffixed with _idxx"`
   - Why: Critical convention that must be followed

3. **Common next steps**
   - Example: `"After creating milestone, you'll likely need to create tasks for it"`
   - Why: Helpful context for what typically comes next

4. **Validation reminders**
   - Example: `"Ensure name or path changes are updated in codebase"`
   - Why: Common mistake to forget

5. **Questions to prompt thinking**
   - Example: `"Are there any types_functions relationships that should be added?"`
   - Why: Prompts AI to consider related data

### ❌ Don't Add When

1. **Helper purpose is obvious**
   - Example: `get_file(file_id)` - doesn't need return_statements
   - Why: Purpose is clear from name and parameters

2. **No common next steps**
   - Example: Simple getters with no typical follow-up
   - Why: Nothing useful to add

3. **Just restating what helper does**
   - Bad: `"Returns project data from database"`
   - Why: That's already in the purpose field

4. **Making up sequences that don't exist**
   - Bad: `"seq 1 → seq 2 → seq 3"`
   - Why: Fabricated, not based on reality

---

## Directive-Based Return Statements

**CRITICAL PROCESS for helpers with used_by_directives:**

### Step 1: Read used_by_directives
```
Check if helper has used_by_directives field populated
If YES:
  - Note which directive(s)
  - Note execution_context
  - Note sequence_order
```

### Step 2: Read the Directive File
```
Find: docs/directives-json/directives-{category}.json
Read: The directive's workflow to understand context
```

### Step 3: Read Directive Flow
```
Find: docs/directives-json/directive_flow_{category}.json
Understand: What comes BEFORE and AFTER this helper in the flow
```

### Step 4: Decide What's Useful
```
Based on directive context, is there a useful hint?
Examples:
- "Check if completion path is finished after milestone completion"
- "Blueprint changes typically trigger version updates"
- "Verify all tasks complete before marking milestone done"
```

### Example Process

**Helper:** `update_milestone`

**Step 1 - Read used_by_directives:**
```json
{
  "directive_name": "project_milestone_complete",
  "execution_context": "mark_milestone_complete",
  "sequence_order": 1
}
```

**Step 2 - Read Directive:**
```
project_milestone_complete marks a milestone as complete, then checks
if all milestones in the completion path are done
```

**Step 3 - Read Directive Flow:**
```
project_milestone_complete → update_milestone (seq 1) →
get_milestones_by_path (seq 2) → check if path complete
```

**Step 4 - Useful Hint:**
```
"After marking milestone complete, check if all milestones in path are done"
```

**Final return_statements:**
```json
"return_statements": [
  "After marking milestone complete, check if all milestones in path are done"
]
```

---

## Style Examples

### Good Examples (Simple, Conceptual)

✅ **Questions:**
- `"Are there any flows that should be added in flow_themes?"`
- `"Do any database interactions need to be added for this function?"`
- `"Should any functions be linked in the types_functions table?"`

✅ **Reminders:**
- `"Ensure name or path changes are updated throughout codebase"`
- `"Verify flows are added in file_flows table"`
- `"If name changed, ensure the _id_xxx suffix is retained"`

✅ **Conventions:**
- `"File names should be suffixed with _id_xx"`
- `"Function names should be suffixed with _id_xx"`
- `"Type names should be suffixed with _id_xx"`

✅ **Conceptual Hints:**
- `"After creating milestone, you'll likely need to create tasks for it"`
- `"Check if all milestones in path are complete to determine path completion"`
- `"Blueprint changes typically trigger version updates"`

✅ **Based on Directive Context:**
- `"After task completion, check if milestone is done"` (from reading directive flow)
- `"Verify all tasks complete before marking milestone done"` (from reading directive)

### Bad Examples (Too Detailed, Rigid, Fabricated)

❌ **Too Detailed:**
```
"DATABASE CONTEXT: Updates milestones table, modifies status field"
"CHECK: Valid values for status: 'pending'/'in_progress'/'completed'"
"NEXT STEP: After update, check completion path status"
```
**Why Bad:** Too much detail, rigid categories, 3 lines when 1 would do

❌ **Fabricated Sequences:**
```
"DIRECTIVE FLOW: project_task_complete → update_task → get_incomplete_tasks_by_milestone → if empty → update_milestone"
```
**Why Bad:** Embedding directive flow data that's already in database

❌ **Restating Purpose:**
```
"Returns project data including name, purpose, goals, and status"
```
**Why Bad:** That's already in the helper's purpose field

❌ **Making Assumptions:**
```
"For blueprint_update, increment version field and prepare updated data for sync"
```
**Why Bad:** Assumes a specific path that may not happen, unclear "sync"

---

## Quality Checklist

Use this for EVERY helper:

### ✅ Directive Review (if used_by_directives exists)
- [ ] Read the directive file (docs/directives-json/)
- [ ] Read the directive flow file (docs/directives-json/directive_flow_*.json)
- [ ] Understand what comes BEFORE this helper in flow
- [ ] Understand what comes AFTER this helper in flow
- [ ] Identify if there's a useful hint based on this context

### ✅ Content Check
- [ ] 0-2 lines maximum (often 0-1 lines)
- [ ] No categories (no DATABASE CONTEXT:, NEXT STEP:, etc.)
- [ ] Simple, conversational style
- [ ] Questions or reminders format
- [ ] Not restating helper purpose
- [ ] Not fabricating sequences
- [ ] Based on actual directive/flow if directive-related
- [ ] Only added if actually useful

### ✅ Value Check
- [ ] Does this add value beyond helper purpose?
- [ ] Would AI likely forget this without the hint?
- [ ] Is this a common next step or related action?
- [ ] Is this a naming convention that must be followed?
- [ ] Is this based on actual directive context (not made up)?

**If NO to all value questions → Leave return_statements empty**

---

## Process for Enhancement

### For Each Helper:

**1. Check if helper has used_by_directives**
   - If NO → skip to step 3
   - If YES → continue to step 2

**2. Review directive context**
   - Read directive file in docs/directives-json/
   - Read directive flow in docs/directives-json/directive_flow_*.json
   - Understand the helper's role in the workflow
   - Understand what typically comes next

**3. Review helper purpose and parameters**
   - Is the purpose clear and obvious?
   - Are there common next steps?
   - Are there related actions often forgotten?
   - Are there naming conventions to follow?

**4. Decide if return_statement is useful**
   - Often the answer is NO (leave empty)
   - If YES, write 1-2 simple lines
   - Use questions or reminders format
   - No categories, no rigid structure

**5. Verify against checklist**
   - Check all items in Quality Checklist above
   - If fails any check → revise or remove

---

## Common Patterns

### Pattern 1: Naming Convention
```json
"return_statements": [
  "Function names should be suffixed with _id_xx after reserving"
]
```

### Pattern 2: Related Action Reminder
```json
"return_statements": [
  "Verify flows are added in file_flows table"
]
```

### Pattern 3: Question to Prompt Thinking
```json
"return_statements": [
  "Are there any types_functions relationships that should be added?"
]
```

### Pattern 4: Directive-Based Hint
```json
"return_statements": [
  "After milestone completion, check if all milestones in path are done"
]
```

### Pattern 5: No Statement Needed
```json
"return_statements": []
```
*When helper purpose is obvious and there's no useful hint to add*

---

## Red Flags to Avoid

### 🚩 Multiple Lines with Categories
```
"DATABASE CONTEXT: Creates entry in files table"
"NEXT STEP: After creation, reserve functions"
"CHECK: Verify file exists in filesystem"
"DIRECTIVE FLOW: project_file_write → reserve_file → finalize_file"
```
**Fix:** Pick ONE useful hint, 1 line, no categories

### 🚩 Fabricated Sequences
```
"DIRECTIVE FLOW: seq 1 → seq 2 → seq 3"
```
**Fix:** Only mention directive context if based on actual directive reading

### 🚩 Restating Purpose
```
"Returns all files matching the provided path"
```
**Fix:** Remove - that's already in purpose field

### 🚩 Too Prescriptive
```
"Call get_milestones_by_path() to check completion status"
```
**Fix:** Make conceptual: "Check if all milestones in path are complete"

---

## Examples: Before and After

### Example 1: finalize_file

**BEFORE (Wrong - Too Detailed):**
```json
"return_statements": [
  "DATABASE CONTEXT: Updates file entry, sets is_reserved=false",
  "NEXT STEP: After finalization, reserve functions for this file",
  "CHECK: Verify file exists in filesystem",
  "RELATED: Use reserve_function() for functions in this file",
  "DIRECTIVE: Used by project_reserve_finalize (seq 2)"
]
```

**AFTER (Correct - Simple):**
```json
"return_statements": [
  "Verify flows are added in file_flows table"
]
```

### Example 2: add_milestone

**BEFORE (Wrong - Too Detailed):**
```json
"return_statements": [
  "DATABASE CONTEXT: Creates milestone within completion path",
  "NEXT STEP: After creating milestone, create tasks for this milestone",
  "CHECK: Status defaults to 'pending' if not provided",
  "DIRECTIVE FLOW: project_task_decomposition → add_completion_path → add_milestone → add_task"
]
```

**AFTER (Correct - Simple):**
```json
"return_statements": [
  "After creating milestone, you'll likely need to create tasks for it"
]
```

### Example 3: get_file

**BEFORE (Wrong - Unnecessary):**
```json
"return_statements": [
  "Returns file data from database",
  "Use returned file_id for function queries"
]
```

**AFTER (Correct - Empty):**
```json
"return_statements": []
```
*Reason: Purpose is obvious, no common next steps*

### Example 4: update_milestone (directive-based)

**BEFORE (Wrong - Not Based on Directive Reading):**
```json
"return_statements": [
  "DATABASE CONTEXT: Partial update - only updates non-NULL fields",
  "NEXT STEP: After update, check milestone status",
  "CHECK: NULL parameters don't update"
]
```

**AFTER (Correct - Based on Actual Directive):**
```json
"return_statements": [
  "After marking milestone complete, check if all milestones in path are done"
]
```
*Reason: Read project_milestone_complete directive and directive flow*

---

## Remember

1. **Read directives and flows** for every helper with used_by_directives
2. **Keep it simple** - 0-2 lines, often 0-1 lines
3. **No categories** - no DATABASE CONTEXT:, NEXT STEP:, etc.
4. **Questions and reminders** - conversational style
5. **Only if useful** - many helpers won't need anything
6. **Not prescriptive** - hints, not commands
7. **Conceptual** - not rigid sequences

**The goal:** Simple, helpful hints that add value without creating rigid specifications or duplicating information already available in the helper's purpose or the database.

---

**Last Updated:** 2026-01-01 (Complete rewrite to reflect original vision)

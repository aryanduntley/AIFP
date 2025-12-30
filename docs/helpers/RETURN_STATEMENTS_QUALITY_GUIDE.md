# Return_Statements Quality Guide

**Purpose:** Reference document for ensuring return_statements provide maximum value by guiding AI toward stable concepts and database-driven decision making.

---

## Core Principle

**Goal:** When AI calls a helper function, return_statements (if needed) should guide AI to:
1. **Query the database FOR available helpers** - Find what helper functions exist for the operation needed
2. **Reference stable concepts** like directive names, directive flows, and database schema
3. **Understand patterns** rather than memorizing specific function names that may change

**Helper functions ARE the interface. Helper names may change during development, but concepts remain stable.**

**Important:** Not all helpers need return_statements. Only add them when they provide meaningful guidance beyond what's already obvious from the helper's purpose and parameters. Simple, self-explanatory helpers can have empty return_statements.

**The Database as Source of Truth:**
- **Helper Functions:** AI queries database to find available helpers (names may change during dev)
- **Directives:** Stable - reference by name (`project_task_complete`, `aifp_status`)
- **Directive Flows:** Stable navigation patterns between directives
- **Database Schema:** Fields and status values (relatively stable)

**NOT Helpful:** Hardcoding specific helper function names that will become stale
**IS Helpful:** Pointing to directives, flows, conceptual operations, and how to find relevant helpers

**Exception:** `user_directives.db` allows direct SQL queries (AI-controlled, may have custom schemas beyond predefined helpers)

---

## Quality Checklist

Use this checklist for EVERY helper's return_statements:

### ✅ Directive Review Process (MANDATORY for helpers with directives)

**CRITICAL:** If helper has `used_by_directives` field populated, you MUST:

1. **Read the directive file** (src/aifp/resource/directives/{directive_name}.md if available)
2. **Read the directive flow file** (docs/directives-json/directive_flow_project.json or user-preferences/fp)
3. **Understand the full workflow context:**
   - What comes BEFORE this helper in the directive flow?
   - What comes AFTER this helper completes?
   - What is the sequence_order and execution_context?
   - What other helpers are called in the same directive sequence?

4. **Write DIRECTIVE CONTEXT statements** that include:
   - `Called by {directive_name} (sequence_order: {n}, execution_context: {context})`
   - Position in workflow (e.g., "First step in initialization", "Second step after file reservation")
   - Relationship to other steps in sequence

5. **Write DIRECTIVE FLOW statements** showing:
   - Full workflow: `aifp_status → {directive} → this helper (seq n) → next step → completion`
   - What directive flows to after completion

**Example:**
```
"DIRECTIVE CONTEXT: Called by project_reserve_finalize (sequence_order: 2, execution_context: finalize_reservation)"
"DIRECTIVE CONTEXT: Second step in reservation phase - completes file reservation after code written"
"DIRECTIVE FLOW: aifp_status → project_file_write → project_reserve_finalize → reserve (seq 1) → write code → finalize_file (this, seq 2) → project_update_db"
```

### ✅ Stability Check (Focus on What Doesn't Change)
- [ ] References directive names (stable - e.g., `project_task_complete`, `project_file_write`)
- [ ] References directive flows (stable navigation patterns from directive_flow tables)
- [ ] References database schema fields (status values, field names from actual tables)
- [ ] References conceptual operations ("completing tasks", "tracking files", "managing milestones")
- [ ] Points AI to database queries for finding helpers (not hardcoding helper names)
- [ ] Focuses on WHAT needs to happen, not specific function names

### ✅ Research Verification
- [ ] If helper has `used_by_directives`, reviewed directive description and purpose (see directive review process above)
- [ ] If helper has `used_by_directives`, checked sequence_order and execution_context
- [ ] If helper has `used_by_directives`, read directive flow file to understand complete workflow
- [ ] Checked database schema for exact field names (status, milestone_id, etc.)
- [ ] Verified parameter names match helper's parameters array

### ✅ Actionability Check
- [ ] Each NEXT STEP describes conceptual action (what to achieve, not just function to call)
- [ ] Each CHECK statement has specific field values/conditions from database schema
- [ ] Each DIRECTIVE statement references actual directive by name (from used_by_directives)
- [ ] Each DIRECTIVE FLOW shows navigation pattern between directives
- [ ] Provides guidance on finding relevant helpers from database when needed

### ✅ Avoid Generic Waste
- [ ] No "helps you understand..." statements
- [ ] No "useful for..." without specifics
- [ ] No "allows you to..." without concrete next action
- [ ] No "this is important because..." without actionable guidance
- [ ] No "consider..." without specific values/functions

---

## Examples: Stable vs Unstable References

### Example 1: Task Completion Flow

❌ **UNSTABLE (Hardcoded Function Names):**
```
"NEXT STEP: Call get_incomplete_tasks_by_milestone(milestone_id) to check milestone status"
"NEXT STEP: If empty, call update_milestone(milestone_id, status='completed')"
"RELATED: Call get_milestones_by_path() to check completion path progress"
```

✅ **STABLE (Conceptual + Directive-Based):**
```
"DIRECTIVE: Used by project_task_complete (check_milestone_status, sequence_order: 2)"
"DIRECTIVE FLOW: project_task_complete → update task status → check milestone completion → if complete → update completion path"
"NEXT STEP: Check if all tasks in milestone are complete - find helper for getting incomplete tasks by milestone"
"NEXT STEP: If no incomplete tasks remain, update milestone status to 'completed'"
"NEXT STEP: After milestone completion, follow directive flow to check completion path status"
"CHECK: Database field tasks.status values: 'pending', 'in_progress', 'blocked', 'completed'"
"CHECK: Empty result means milestone complete - look for helper to update milestone status"
"DATABASE: Find helpers - query core.db for helpers with target_database='project' and purpose containing 'task' or 'milestone'"
```

**Why Better:** References stable directives and flows, describes conceptual operations, points to finding helpers via database query, includes exact schema field values, avoids hardcoding function names.

---

### Example 2: Status Transitions (Stable Schema References)

❌ **UNSTABLE (Hardcoded Functions):**
```
"CHECK: status='pending' → call update_task(task_id, status='in_progress')"
"CHECK: status='blocked' → call update_task(task_id, status='in_progress')"
```

✅ **STABLE (Schema + Conceptual):**
```
"CHECK: Database field tasks.status has values: 'pending', 'in_progress', 'blocked', 'completed'"
"CHECK: status='pending' → task not started, can transition to 'in_progress' to begin work"
"CHECK: status='in_progress' → active work, can create subtasks if decomposition needed"
"CHECK: status='blocked' → waiting on dependency, resolve blocker before transitioning to 'in_progress'"
"CHECK: status='completed' → triggers milestone completion check via project_task_complete directive"
"DATABASE: Find helper for updating task status - search helpers with target_database='project' and purpose containing 'update' and 'task'"
```

**Why Better:** References actual database schema, describes state transitions conceptually, points to finding helpers rather than hardcoding names.

---

### Example 3: Completion Cascade (Directive Flow Focus)

❌ **UNSTABLE (Hardcoded Function Chain):**
```
"CHECK: If empty → call update_milestone(milestone_id, status='completed')"
"CHECK: After update_milestone() → call get_milestones_by_path(completion_path_id)"
"CHECK: If all path milestones complete → call update_completion_path(path_id, status='completed')"
```

✅ **STABLE (Directive Flow Pattern):**
```
"DIRECTIVE FLOW: Task completion cascades upward: tasks → milestone → completion_path"
"CHECK: Empty result means all tasks complete for this milestone"
"NEXT STEP: Update milestone status to 'completed' (find helper for milestone updates)"
"NEXT STEP: After milestone completion, check if completion_path is finished (all milestones done)"
"NEXT STEP: Follow project_completion_check directive flow if path complete"
"DATABASE: Schema relationship: tasks.milestone_id → milestones.id → milestones.completion_path_id → completion_path.id"
```

**Why Better:** Shows cascade as conceptual pattern, references directive flow, describes database relationships, avoids hardcoded function names.

---

### Example 4: Directive Integration (Flow Navigation)

❌ **UNSTABLE (Function Sequence):**
```
"DIRECTIVE FLOW: project_task_complete → update_task(status='completed') → get_incomplete_tasks_by_milestone() → if empty → update_milestone(status='completed')"
```

✅ **STABLE (Directive-Based Navigation):**
```
"DIRECTIVE: Used by project_task_complete (check_milestone_status, sequence_order: 2)"
"DIRECTIVE FLOW: project_task_complete → check milestone → if complete → check completion_path → if done → project_completion_check"
"DIRECTIVE FLOW: Query directive_flow_project.json for complete navigation from project_task_complete"
"NEXT STEP: After executing this helper, directive determines next action based on completion status"
"DATABASE: Directive flow navigation available via get_next_directives_from_status() or get_completion_loop_target()"
```

**Why Better:** References stable directive names and flow patterns, points to directive flow queries, avoids embedding operational details that belong in directives.

---

## Research Process

When enhancing a helper, follow this process:

### Step 1: Review Helper Definition
```
1. Read helper's purpose field
2. Read all parameters with types and descriptions
3. Note any special parameter values (enums, defaults, required fields)
4. Read error_handling field for failure cases
```

### Step 2: Check Directive Mappings
```
If used_by_directives is populated:

1. For each directive:
   - Note directive_name
   - Note execution_context (tells you WHEN in directive this is called)
   - Note sequence_order (tells you order in directive)
   - Read description field

2. Look for other helpers with same directive_name
   - Build mental model of directive flow
   - Note what comes before (lower sequence_order)
   - Note what comes after (higher sequence_order)
```

### Step 3: Identify Conceptual Relationships
```
1. What conceptual operations does this helper naturally lead to?
   - Example: Getting task flows → leads to finding files associated with those flows
   - Don't hardcode: "call get_files_by_flow()"
   - Do describe: "find helpers to get files from flow IDs"

2. What database relationships are involved?
   - Example: tasks.milestone_id → milestones.id (foreign key)
   - Example: file_flows junction table connects files ↔ flows

3. What directives orchestrate these operations?
   - Check used_by_directives field
   - Review directive_flow_*.json for navigation patterns
```

### Step 4: Check Database Schema
```
For helpers that query/modify database:

1. Note exact table name (target_database field)
2. List exact field names helper touches
3. Note any JSON fields and their structure
4. Note any foreign key relationships
5. Note any status/enum fields and their valid values
```

### Step 5: Build Stable Statements

Structure statements with these categories (focus on stability):

```
DATABASE CONTEXT:
- What table/fields affected (exact schema names: tasks.status, milestones.id)
- Database relationships (foreign keys, junction tables)
- Special implications (is_reserved flags, timestamps, cascade effects)

NEXT STEP:
- CONCEPTUAL action to take (e.g., "update milestone status", "check completion path")
- How to find helpers for this action (query database by purpose/target)
- Avoid hardcoding specific function names

CHECK:
- Exact database field values from schema (status='pending'/'in_progress'/'blocked'/'completed')
- Conditional logic using schema concepts (if empty → milestone complete)
- Edge cases based on database state

DIRECTIVE:
- Exact directive name from used_by_directives (e.g., "project_task_complete")
- Execution context and sequence_order
- What directive flow comes before/after

DIRECTIVE FLOW:
- Conceptual sequence (task completion → milestone check → path check)
- Reference directive_flow_*.json for navigation
- Point to helpers for querying flows (get_next_directives_from_status)

CONCEPTUAL WORKFLOW:
- Multi-step patterns described conceptually
- Example: "Task completion cascades: tasks → milestone → completion_path"
- Database relationships that drive the workflow

DATABASE QUERY FOR HELPERS:
- How to find relevant helpers from core.db
- Example: "Search helpers where target_database='project' AND purpose LIKE '%milestone%'"
- Point to helper discovery tools (get_helpers_by_database, get_helper_by_name)

WARNING:
- Destructive operations with conceptual impact
- Common pitfalls (schema-level issues, cascade effects)
- State consistency based on database relationships
```

---

## Red Flags (Unstable Patterns to Avoid)

Watch for these unstable patterns that will become stale:

### 🚩 "Call specific_function(params)..."
**Instead:** "Find helper for [operation] - query database for helpers with purpose containing '[keyword]'"

### 🚩 "Use function_name() to..."
**Instead:** "To [achieve goal], look for helper that [describes operation]"

### 🚩 "Helps identify..." (vague)
**Instead:** "CHECK: Database field [table.field] values: 'value1'/'value2'/'value3'"

### 🚩 "Related helpers include X, Y, Z" (hardcoded list)
**Instead:** "Find related helpers - query core.db for helpers with target_database='[db]' and purpose containing '[keyword]'"

### 🚩 Embedding helper function chains
**Instead:** Reference directive flows and conceptual operations

### 🚩 "For more information..." (lazy)
**Instead:** Provide actual database schema, directive names, or flow references

---

## Field Separation: return_statements vs implementation_notes

**CRITICAL CONCEPT:** These two fields serve completely different purposes and audiences.

### return_statements

**Purpose:** Forward-thinking guidance for AI AFTER successful execution
**Audience:** AI at runtime (imported to database)
**Focus:** What to do next, checks to make, workflow context
**Tone:** Future-oriented ("NEXT STEP:", "CHECK:", "After success...")

**Include:**
- NEXT STEP: Actions to take after this helper succeeds
- CHECK: Conditions to evaluate based on results
- DIRECTIVE CONTEXT: Which directives use this and when
- DIRECTIVE FLOW: What comes next in the workflow
- DATABASE CONTEXT: State implications, relationships
- COMMON WORKFLOWS: Typical usage patterns
- WARNING: Consequences of this operation

**Example:**
```
"NEXT STEP: After successful deletion, remove file from filesystem"
"CHECK: Were there other functions calling this one? Update their code to remove broken calls"
"DATABASE CONTEXT: Function entry deleted, interactions auto-cascaded via SQL ON DELETE CASCADE"
```

### implementation_notes

**Purpose:** Implementation guidance for developers during coding phase
**Audience:** Developers (NOT imported to database, stays in JSON)
**Focus:** How to implement the function - error logic, validation, SQL queries
**Tone:** Implementation-oriented ("ERROR LOGIC:", "SUCCESS LOGIC:", "SQL:")

**Include:**
- ERROR LOGIC: What to check, when to return errors
- ERROR RETURN: Error response structure
- ERROR MESSAGE: What error message to return
- SUCCESS LOGIC: Implementation steps for successful path
- SUCCESS RETURN: Success response structure
- NOTE: Implementation details, SQL cascade behavior

**Example:**
```
"ERROR LOGIC: Query types_functions WHERE function_id=? - if not empty, return error"
"ERROR RETURN: {success: false, error: 'types_functions_exist', type_relationships: [...]}"
"SUCCESS LOGIC: Delete function: DELETE FROM functions WHERE id=function_id"
"NOTE: Interactions cascade via SQL ON DELETE CASCADE"
```

### 🚨 CRITICAL RULE: Never Mix These

**BAD (mixing concerns):**
```
return_statements: [
  "ERROR LOGIC: Check if types_functions exist",  ← Implementation detail, belongs in implementation_notes
  "NEXT STEP: After deletion, remove from filesystem"  ← Correct for return_statements
]
```

**GOOD (properly separated):**
```
return_statements: [
  "NEXT STEP: After successful deletion, remove function code from filesystem",
  "CHECK: Were there other functions calling this one? Update their code"
]

implementation_notes: [
  "ERROR LOGIC: Query types_functions WHERE function_id=?",
  "SUCCESS LOGIC: Delete function: DELETE FROM functions WHERE id=function_id"
]
```

---

## Delete Operations: ERROR-First Approach

**CRITICAL PATTERN:** Delete operations NEVER cascade automatically. Always return error with dependency details.

### The ERROR-First Philosophy

**Goal:** Force AI to be intentional about every deletion, prevent accidental data loss.

**Pattern:**
1. Helper checks for dependencies
2. If dependencies exist → Return error with complete list
3. AI must manually clean each dependency
4. Retry deletion after cleanup → Success

### Delete Function Behavior

**delete_file()**
- Checks: functions, types, file_flows
- Returns error if ANY exist
- AI must: Delete each function, delete each type, remove each file_flows entry, then retry

**delete_function()**
- Checks: types_functions entries
- Returns error if ANY exist
- AI must: Unlink each types_functions entry, then retry
- Note: interactions auto-cascade via SQL (no manual work needed)

**delete_type()**
- Checks: types_functions entries
- Returns error if ANY exist
- AI must: Unlink each types_functions entry, then retry

### Error Response Structure

```json
// delete_file error
{
  "success": false,
  "error": "dependencies_exist",
  "functions": [{"id": 1, "name": "calc_id1"}, ...],
  "types": [{"id": 5, "name": "Result_id5"}, ...],
  "file_flows": [{"file_id": 10, "flow_id": 3}, ...]
}

// delete_function error
{
  "success": false,
  "error": "types_functions_exist",
  "type_relationships": [
    {"type_id": 5, "type_name": "Result_id5", "role": "transformer"}
  ]
}
```

### return_statements for Delete Functions

**Focus:** What to do AFTER successful deletion (error handling covered in implementation_notes)

```
"NEXT STEP: After successful deletion, remove function code from filesystem file"
"CHECK: Were there other functions calling this one? Update their code to remove broken calls"
"DATABASE CONTEXT: Function entry deleted, interactions auto-cascaded via SQL"
"WARNING: Deletion is permanent - function entry and all interactions removed with no undo"
```

**DON'T include error logic in return_statements - that's for implementation_notes**

### implementation_notes for Delete Functions

**Focus:** Error checking and implementation details

```
"ERROR LOGIC: Query types_functions WHERE function_id=? - if not empty, return error"
"ERROR RETURN: {success: false, error: 'types_functions_exist', type_relationships: [...]}"
"SUCCESS LOGIC: Get file_id before deletion: SELECT file_id FROM functions WHERE id=?"
"SUCCESS LOGIC: Delete function: DELETE FROM functions WHERE id=function_id"
"NOTE: Interactions cascade via SQL ON DELETE CASCADE"
```

---

## Avoid Automatic Operation Notes (Token Waste)

**RULE:** If something happens automatically in the implementation, AI doesn't need to know about it.

### ❌ BAD (Wastes Tokens)

```
implementation_notes: [
  "SUCCESS LOGIC: Delete function: DELETE FROM functions WHERE id=function_id",
  "SUCCESS LOGIC: File timestamp automatically updated after deletion (handled by implementation)",  ← AI doesn't need this
  "SUCCESS LOGIC: SQL CASCADE automatically deletes interactions"  ← This could be useful context
]
```

### ✅ GOOD (Only Necessary Info)

```
implementation_notes: [
  "SUCCESS LOGIC: Get file_id before deletion: SELECT file_id FROM functions WHERE id=?",
  "SUCCESS LOGIC: Delete function: DELETE FROM functions WHERE id=function_id",
  "NOTE: Interactions cascade via SQL ON DELETE CASCADE"  ← Concise, relevant
]
```

### When to Document Automatic Operations

**DON'T document if:**
- It's a standard database operation (timestamps, auto-increment IDs)
- It's handled by SQL constraints/triggers
- It's an implementation detail with no decision impact

**DO document if:**
- It affects AI's next decision (e.g., "interactions auto-cascade" means AI doesn't need to delete them manually)
- It's a NOTE that explains implementation behavior concisely

**Test:** Would removing this change how the function is implemented? If no → remove it.

---

## Pattern Templates (Stable Approach)

Use these templates for common scenarios:

### Template: Query Helper (get_* functions)

```
DATABASE CONTEXT: Queries [exact_table] table WHERE [exact_field] matches criteria
CHECK: Database field [table.field] has values: 'value1'/'value2'/'value3' (from schema)
CHECK: Empty result means [conceptual state] - typical next action is [conceptual operation]
CHECK: Non-empty result provides [field_name] which can be used to [conceptual next step]
DIRECTIVE: Used by [directive_name] ([execution_context], sequence_order: N)
DIRECTIVE FLOW: [directive_name] → [conceptual operation] → [next directive in flow]
DATABASE: Find helpers for next operation - search core.db helpers where target_database='[db]' and purpose contains '[keyword]'
```

### Template: Update Helper (update_* functions)

```
DATABASE CONTEXT: Updates [exact_table] table, modifies [field1], [field2] fields
DATABASE CONTEXT: Database relationship: [table.field] references [parent_table.id]
CHECK: Valid values for [table.field]: 'value1'/'value2'/'value3' (from schema)
CHECK: Updating [field] to '[value]' triggers [conceptual cascade] (e.g., milestone → path completion check)
DIRECTIVE: Used by [directive_name] ([execution_context], sequence_order: N)
DIRECTIVE FLOW: After update, directive flow continues to [next conceptual operation]
WARNING: Updating [field] affects [related_table] records - check cascade effects
DATABASE: Find helpers for cascade operations - query for helpers with purpose containing '[related_operation]'
```

### Template: Delete Helper (delete_* functions)

```
DATABASE CONTEXT: Deletes from [exact_table] table with cascade validation
DATABASE CONTEXT: Foreign key relationships: [table] → [child_table(s)]
CHECK: Validates no orphaned records in [child_table] before deletion
CHECK: Requires note with fields: reason (TEXT), severity ('info'/'warning'/'error'), source ('ai'/'user')
WARNING: Destructive operation - validates [table] foreign key relationships to prevent data inconsistency
DIRECTIVE: Used by [directive_name] ([execution_context], sequence_order: N)
DATABASE: Find helpers for checking relationships - query for helpers operating on [child_table]
```

### Template: Add/Create Helper (add_* functions)

```
DATABASE CONTEXT: Inserts into [exact_table] table, returns new record ID
DATABASE CONTEXT: Required fields from schema: [field1], [field2]; Optional: [field3], [field4]
CHECK: Parameter [param_name] must match schema constraint: [constraint details]
CHECK: Foreign key [parent_id] must exist in [parent_table] (schema relationship)
DIRECTIVE: Used by [directive_name] ([execution_context], sequence_order: N)
DIRECTIVE FLOW: [directive_name] creates record → typically followed by [conceptual next operation]
CONCEPTUAL WORKFLOW: Creation pattern: create parent record → populate relationships → finalize state
DATABASE: Find helpers for relationships - query helpers with purpose containing '[related_entity]'
```

---

## Quality Score

Score each helper's return_statements based on stability:

**Poor (1-3/10):** Hardcoded function names, vague guidance, no directive/schema references
**Fair (4-6/10):** Some schema fields, but still hardcodes function names or lacks directive context
**Good (7-8/10):** References directives and schema, minimal function name hardcoding, points to finding helpers
**Excellent (9-10/10):** Fully stable - directive flows, schema fields, conceptual operations, helper discovery guidance

**Target:** Every helper should score 8+ after enhancement (stable and conceptual)

---

## Review Questions

Ask these for every helper:

1. **Does it avoid hardcoding function names that will change?**
   - If hardcoded → replace with conceptual operations and helper discovery guidance

2. **Are directive names referenced (if used_by_directives populated)?**
   - Directive names are stable - always reference them

3. **Are database schema fields exact and accurate?**
   - Verify field names, status values, data types from actual schema

4. **Does it reference directive flows rather than embedding helper chains?**
   - Point to directive_flow_*.json, not "A() → B() → C()"

5. **Does it describe WHAT needs to happen conceptually?**
   - Focus on goals, not specific function calls

6. **Does it guide AI to find helpers from database?**
   - "Query core.db for helpers with..." instead of "Call function_name()"

7. **Are edge cases described conceptually?**
   - Empty results, null values, error states as concepts, not function-specific

---

## Session Workflow

For each helper enhancement session:

### Before Starting
1. Read this quality guide
2. Have schema access ready (get_project_fields)
3. Have related helpers list ready

### During Enhancement
1. Read helper definition completely
2. Assess: Does this helper need return_statements? (Skip if simple/self-explanatory)
3. If needed, research using steps in Research Process section
4. Draft statements using Pattern Templates (focus on stable concepts)
5. Check against Quality Checklist
6. Score using Quality Score criteria
7. Revise until score is 8+ OR confirm no statements needed

### After Enhancement
1. Verify all checklist items ✅
2. Read statements as if you're the AI
3. Ask: "Can I proceed without more queries?"
4. If YES → move to next helper
5. If NO → identify what's missing and add it

---

## Example: Complete Enhancement

**Helper:** (Conceptual example for checking incomplete milestone tasks)

**Before (Unstable - Hardcoded Functions):**
```
- Returns tasks for milestone
- Check if milestone can be completed
- Used by task completion workflow
- Call update_milestone() if empty
- Call get_milestones_by_path() after updating milestone
```

**After (Stable - Conceptual + Directive-Focused):**
```
DATABASE CONTEXT: Queries tasks table WHERE milestone_id=parameter AND status IN ('pending', 'in_progress', 'blocked')
DATABASE CONTEXT: Schema field tasks.status values: 'pending', 'in_progress', 'blocked', 'completed'
DATABASE CONTEXT: Parameter skip_pending: false includes all work, true excludes pending (active work only)
CHECK: Empty result when skip_pending=false means all milestone tasks complete
CHECK: Each result has status field indicating task state (see schema values above)
CHECK: Each result may have subtasks[] array - task not truly complete if subtasks exist
NEXT STEP: If empty result → milestone is complete → update milestone status to 'completed'
NEXT STEP: After milestone completion → check if completion_path is finished (all milestones done)
DIRECTIVE: Used by project_task_complete directive (check_milestone_status context, sequence_order: 2)
DIRECTIVE FLOW: project_task_complete → update task status → check milestone completion → if complete → check path completion
DIRECTIVE FLOW: Query directive_flow_project.json to find next directive after task completion
CONCEPTUAL WORKFLOW: Task completion cascades upward: tasks → milestone → completion_path → project_completion_check
DATABASE RELATIONSHIP: tasks.milestone_id → milestones.id → milestones.completion_path_id → completion_path.id
DATABASE: Find helpers for milestone updates - query core.db helpers with target_database='project' AND purpose LIKE '%milestone%update%'
DATABASE: Find helpers for path checking - query for helpers with purpose containing 'completion_path'
WARNING: Using skip_pending=true for completion checks will miss pending work - always use false to include all work
```

**Quality Score: 9/10**
- ✅ References stable directive names (project_task_complete)
- ✅ References directive flow patterns
- ✅ Exact database schema field names and values
- ✅ Describes conceptual operations (cascade pattern)
- ✅ Points to helper discovery via database queries
- ✅ Edge cases described conceptually
- ✅ Avoids hardcoding specific function names

---

## Remember

**The AI has just executed this helper. It already knows:**
- What helper it called (it just used it!)
- Why it called it (it made that decision)
- The helper's purpose (it read the definition)

**The AI needs stable guidance:**
- What DIRECTIVE orchestrates this operation (directive names don't change)
- What DIRECTIVE FLOW comes next (flow patterns are stable)
- What DATABASE SCHEMA fields to check (field names and values)
- What CONCEPTUAL OPERATION to perform next (not specific function names)
- How to FIND helpers for next operations (query database, don't hardcode names)

**Key Insight:** Helper function names may change during development. Guide AI with stable concepts (directives, flows, schema) and helper discovery patterns, not hardcoded function names!

**Give the AI conceptual navigation, not brittle function chains!**

---

**Last Updated:** 2025-12-29 (Revised for stability - focus on directives, flows, schema, not hardcoded helper names)
**Review Status:** Reference document for all return_statements enhancement work

---

## Summary of Revision (2025-12-29)

**Key Change:** Shifted from hardcoding specific helper function names to focusing on stable concepts.

**Why:** Helper functions are subject to change during development. The database is the source of truth for current helper implementations.

**New Focus:**
1. **Directive names** (stable - e.g., `project_task_complete`, `aifp_status`)
2. **Directive flows** (stable patterns from directive_flow_*.json files)
3. **Database schema** (field names, status values, relationships)
4. **Conceptual operations** ("complete milestone", "check path status")
5. **Helper discovery** (guide AI to query database for available helpers)

**Old Approach (Unstable):**
```
"NEXT STEP: Call update_milestone(milestone_id, status='completed')"
"RELATED: get_milestones_by_path() to check completion path"
```

**New Approach (Stable):**
```
"DIRECTIVE: Used by project_task_complete (check_milestone_status, sequence_order: 2)"
"DIRECTIVE FLOW: project_task_complete → check milestone → if complete → check path"
"NEXT STEP: Update milestone status to 'completed' (find helper for milestone updates)"
"DATABASE: Query core.db for helpers with target_database='project' AND purpose LIKE '%milestone%'"
```

**Exception:** `user_directives.db` allows direct SQL (AI-controlled, may have custom schemas beyond predefined helpers)

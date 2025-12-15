# aifp_help - Directive Documentation Access

**Type**: Project Management
**Level**: 1
**Parent**: `aifp_run`
**Category**: Orchestration

---

## Purpose

`aifp_help` loads detailed documentation for a specific directive. It retrieves the full markdown documentation file, providing comprehensive guidance including purpose, workflow, examples, edge cases, and related directives.

**Use this directive when**:
- User requests help with a specific directive
- AI needs detailed workflow information beyond database metadata
- Understanding directive edge cases and examples
- Learning how to properly use a directive

---

## When to Apply

### Explicit User Requests

- "Help with [directive_name]"
- "Show documentation for [directive]"
- "Explain how [directive] works"
- "What does [directive] do?"
- "How do I use [directive]?"

### AI Internal Use

- Clarifying directive usage before execution
- Understanding complex workflow branches
- Checking edge case handling
- Finding related directives for task sequencing

---

## Workflow

### Step 1: Identify Target Directive

**If directive name provided**:
```python
directive_name = user_input.directive_name
# Proceed to Step 2
```

**If unclear or keyword search**:
```python
# AI uses available helpers to search directives_intent_keywords table by keyword
results = matching_directives

# Display matches
if len(results) > 1:
    prompt_user("Multiple matches found. Which directive?")
    show_list(results)
else:
    directive_name = results[0].name
```

### Step 2: Load Directive Documentation

```python
# AI reads MD file directly: src/aifp/reference/directives/{directive_name}.md
documentation = md_file_content
```

### Step 3: Display Documentation

**Format**:
```markdown
# [Directive Name] - [Title]

**Type**: [type]
**Level**: [level]
**Parent**: [parent_directive]

## Purpose
[Purpose section from MD file]

## When to Apply
[When to Apply section]

## Workflow
[Detailed workflow with steps]

## Examples
[Code examples and use cases]

## Edge Cases
[Edge case handling]

## Related Directives
[Related directives and relationships]

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
## Database Operations
[Database tables and queries]
```

### Step 4: Suggest Related Actions

**After displaying documentation**:
```python
# Extract related directives from documentation
related = extract_related_directives(documentation)

# Suggest next steps
if user_task_context:
    suggest("You might also need: " + related)
```

---

## Examples

### Example 1: Getting Help with FP Directive

**User Request**:
> "I need help understanding how fp_purity works"

**AI Process**:
1. Identifies directive name: `fp_purity`
2. Reads MD file: `src/aifp/reference/directives/fp_purity.md`
3. Queries `directive_flow` table for related directives (conditional flows, error paths)
4. Reviews categories and keywords from database

**AI Response**:
> **fp_purity - Function Purity Enforcer**
>
> This directive ensures all functions are pure (same inputs → same outputs, no side effects).
>
> [Displays full documentation content]
>
> **Related directives** (from directive_flow table):
> - `fp_side_effect_detection` - Detects side effects in functions
> - `fp_immutability` - Enforces immutable data structures
> - `fp_state_elimination` - Removes hidden state
>
> Would you like me to explain any of these related directives?

### Example 2: Fuzzy Search

**User Request**:
> "How do I use the file write directive?"

**AI Process**:
1. Searches `directives` and `directives_intent_keywords` tables for "file write"
2. Finds multiple matches
3. Presents options to user

**AI Response**:
> I found 3 directives matching "file write":
>
> 1. **project_file_write** - Write code files to project
> 2. **project_file_delete** - Delete files from project
> 3. **project_file_read** - Read file contents
>
> Which one would you like to learn about?

**User**:
> "The first one"

**AI Response**:
> [Reads and displays project_file_write.md documentation]

### Example 3: Documentation Not Available

**User Request**:
> "Show me the fp_custom_feature documentation"

**AI Process**:
1. Attempts to read MD file: `src/aifp/reference/directives/fp_custom_feature.md`
2. File not found
3. Queries `directives` table for basic metadata
4. If found in database: Shows basic info
5. If not found: Suggests searching

**AI Response** (if in database):
> ⚠️ Full documentation not available for `fp_custom_feature`.
>
> **Basic information from database**:
> - **Type**: Functional Programming
> - **Category**: Core
> - **Description**: [from directives.description field]
>
> The MD documentation file is missing. Would you like me to search for similar directives?

**AI Response** (if not in database):
> ❌ Directive `fp_custom_feature` not found.
>
> Would you like me to search for directives by keyword? Or use `get_all_directives()` to see all available directives?

---

## Edge Cases

### Case 1: MD File Missing

**Issue**: Directive exists in database but MD file is missing

**AI Process**:
1. Attempts to read MD file
2. File not found
3. Queries `directives` table for metadata
4. Displays basic info with warning

**Resolution**: Shows basic directive information from database (name, description, type, category) and warns user that full documentation is unavailable.

### Case 2: Multiple Directive Matches

**Issue**: User provides ambiguous keyword

**AI Process**:
1. Searches directives by keyword
2. Finds multiple matches
3. Presents numbered list to user
4. Waits for user selection

**Resolution**: AI displays all matching directives and asks user to clarify which one they want to learn about.

### Case 3: Directive Does Not Exist

**Issue**: User requests help for non-existent directive

**AI Process**:
1. Searches `directives` table for exact name
2. Not found
3. Searches by keyword for similar names
4. Suggests alternatives or offers to show all directives

**Resolution**: AI suggests similar directive names if found, or offers to display all available directives using available helpers.

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.

---

## Database Operations

**Read Operations**:
```sql
-- Get directive metadata (fallback when MD missing)
SELECT name, description, type, level, category, md_file_path
FROM directives
WHERE name = ?;

-- Search directives by keyword
SELECT name, description, type
FROM directives
WHERE name LIKE ? OR description LIKE ?
ORDER BY name;
```

**No Write Operations**: This directive is read-only.

---

## Related Directives

**Called By**:
- `aifp_run` - Gateway may route help requests here
- User manual requests

**Calls**:
- None (terminal directive - displays information only)

**Related**:
- Use available helpers to list all directives
- Use available helpers to search directives by keyword
- Use available helpers to find directive relationships

---

## Testing

### Test Case 1: Standard Documentation Load

**Input**:
```python
aifp_help(directive_name="project_file_write")
```

**Expected Output**:
- Full markdown documentation displayed
- All sections present (Purpose, Workflow, Examples, etc.)
- No errors

**Verification**:
```bash
# MD file should exist
test -f src/aifp/reference/directives/project_file_write.md
echo $?  # Should return 0
```

### Test Case 2: Fuzzy Search

**Input**:
User asks: "Help with file write"

**Expected Output**:
- AI searches for matching directives
- Multiple matches shown
- User prompted to select
- Selected directive documentation displayed

**Verification**:
- AI finds directives matching "file write" keyword
- Results include project_file_write, project_file_read, project_file_delete

### Test Case 3: Missing Documentation

**Input**:
```python
aifp_help(directive_name="some_missing_directive")
```

**Expected Output**:
- AI attempts to read MD file
- MD file not found
- AI queries database for basic metadata
- Warning message shown
- Basic information displayed from database

**Verification**:
- MD file does not exist: `src/aifp/reference/directives/some_missing_directive.md`
- Directive exists in `directives` table
- AI displays basic info from database

---

## References
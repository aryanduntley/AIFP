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
# Use search_directives helper
results = search_directives(
    keyword=user_keyword,
    category=None,  # Optional filter
    type=None       # Optional filter
)

# Display matches
if len(results) > 1:
    prompt_user("Multiple matches found. Which directive?")
    show_list(results)
else:
    directive_name = results[0].name
```

### Step 2: Load Directive Documentation

```python
# Call get_directive_content helper
documentation = get_directive_content(directive_name)

# Returns full markdown content from MD file
# Example: src/aifp/reference/directives/fp_purity.md
```

**Helper Function**:
- **Name**: `get_directive_md`
- **Parameters**: `directive_name` (string)
- **Returns**: Full markdown documentation as string
- **Error**: Returns None if MD file not found
- **Query database for complete specification**

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

## Helper Functions Used
[Helper functions with descriptions]

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

**Execution**:
```python
# Step 1: Parse directive name from request
directive_name = "fp_purity"

# Step 2: Load documentation
doc = get_directive_content("fp_purity")

# Step 3: Display full documentation
show_markdown(doc)

# Step 4: Suggest related
suggest("Related: fp_side_effect_detection, fp_immutability")
```

**Output**:
```
# fp_purity - Function Purity Enforcer

**Type**: Functional Programming
**Level**: 1
...

[Full documentation displayed]

Related directives you might need:
- fp_side_effect_detection: Detect and flag side effects
- fp_immutability: Enforce immutable data structures
```

### Example 2: Fuzzy Search

**User Request**:
> "How do I use the file write directive?"

**Execution**:
```python
# Step 1: Keyword search (no exact name)
results = search_directives(keyword="file write")

# Returns: project_file_write, project_file_delete, project_file_read

# Prompt user
prompt("Found 3 directives matching 'file write':")
show_list([
    "1. project_file_write - Write code files to project",
    "2. project_file_delete - Delete files from project",
    "3. project_file_read - Read file contents"
])

# User selects #1
directive_name = "project_file_write"

# Step 2-4: Load and display
doc = get_directive_content("project_file_write")
show_markdown(doc)
```

### Example 3: Documentation Not Available

**User Request**:
> "Show me the fp_custom_feature documentation"

**Execution**:
```python
# Step 1: Parse directive name
directive_name = "fp_custom_feature"

# Step 2: Load documentation
doc = get_directive_content("fp_custom_feature")
# Returns: None (file not found)

# Fallback: Load basic metadata from database
directive_info = get_directive("fp_custom_feature")

if directive_info:
    show_basic_info(directive_info)
    warn("Full documentation not available. Showing basic metadata.")
else:
    error("Directive not found. Try search_directives()?")
```

---

## Edge Cases

### Case 1: MD File Missing

**Issue**: Directive exists in database but MD file is missing

**Detection**:
```python
doc = get_directive_content(directive_name)
if doc is None:
    # MD file not found
```

**Resolution**:
```python
# Fallback to database metadata
directive = get_directive(directive_name)
show_basic_info({
    "name": directive.name,
    "description": directive.description,
    "type": directive.type,
    "category": directive.category
})
warn("Full documentation not available. Showing basic information from database.")
```

### Case 2: Multiple Directive Matches

**Issue**: User provides ambiguous keyword

**Detection**:
```python
results = search_directives(keyword=user_keyword)
if len(results) > 1:
    # Ambiguous request
```

**Resolution**:
```python
# Show numbered list
show_list([f"{i+1}. {r.name} - {r.description}" for i, r in enumerate(results)])
user_selection = prompt("Which directive? (enter number)")
directive_name = results[int(user_selection) - 1].name
```

### Case 3: Directive Does Not Exist

**Issue**: User requests help for non-existent directive

**Detection**:
```python
directive = get_directive(directive_name)
if directive is None:
    # Not found in database
```

**Resolution**:
```python
# Fuzzy search for similar names
similar = search_directives(keyword=directive_name)
if similar:
    suggest(f"Did you mean: {similar[0].name}?")
else:
    error("Directive not found. Use get_all_directives() to see available directives.")
```

---

## Helper Functions

This directive's helpers are dynamically mapped in `aifp_core.db`.

**Query at runtime**:
```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
```

**Primary helpers**:
- **get_directive_md(name)** - Load full MD documentation for directive
  - Returns: Full markdown content as string
  - Error: Returns None if file not found

- **get_directives_by_category(category)** - Search directives by category
  - Returns: List of matching directive objects
  - Use: Find directives when exact name unknown

- **get_directive(name)** - Get directive metadata from database
  - Returns: Directive object with basic metadata
  - Use: Fallback when MD file missing

See `helper_functions` table in aifp_core.db for complete specifications.

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
- `get_all_directives()` - Lists all available directives
- `search_directives()` - Search directives by keyword
- `get_directive_interactions()` - Show directive relationships

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
```python
aifp_help(keyword="file write")
```

**Expected Output**:
- Multiple matches shown
- User prompted to select
- Selected directive documentation displayed

**Verification**:
```python
results = search_directives(keyword="file write")
assert len(results) >= 1
assert any("file_write" in r.name for r in results)
```

### Test Case 3: Missing Documentation

**Input**:
```python
aifp_help(directive_name="some_missing_directive")
```

**Expected Output**:
- Fallback to database metadata
- Warning message shown
- Basic information displayed

**Verification**:
```python
doc = get_directive_content("some_missing_directive")
assert doc is None
directive = get_directive("some_missing_directive")
assert directive is not None  # Exists in DB but no MD file
```

---

## References

- [Blueprint: aifp_core.db](../../../docs/blueprints/blueprint_aifp_core_db.md)
- [JSON Definition](../../../docs/directives-json/directives-project.json)

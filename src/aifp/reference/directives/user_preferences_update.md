# Directive: user_preferences_update

**Type**: Project
**Level**: 1
**Parent Directive**: user_preferences_sync
**Priority**: HIGH - Critical for customization

---

## Purpose

The `user_preferences_update` directive handles **explicit user requests to modify AI behavior preferences**, translating natural language customization requests into structured database updates. The AI uses its NLP capabilities to map user requests like "always add docstrings" to specific directives like `project_file_write`, then stores preferences in the atomic key-value `directive_preferences` table.

This directive is **essential for user empowerment** because:
- **Natural language preferences**: Users say "always do X" without knowing internal directive names
- **Intent-based matching**: AI uses NLP to search directive names, descriptions, and keywords in `aifp_core.db`
- **Atomic key-value structure**: Multiple preferences per directive (UNIQUE constraint on directive_name, preference_key)
- **User confirmation**: Shows which directive will be affected before applying
- **Validation**: Ensures preference values are valid before storing
- **Immediate effect**: Next directive execution uses new preference

The update workflow:
1. **Parse preference request** - Extract intent from user's natural language
2. **Find matching directive** - AI queries `directives` table for intelligent matching
3. **Confirm with user** - Show which directive will be customized
4. **Parse preference details** - Extract preference key and value
5. **Update or insert** - UPSERT into `directive_preferences` table
6. **Confirm update** - Show user the new preference setting

---

## When to Apply

This directive applies when:
- **User requests customization** - "Always add docstrings", "Never use X"
- **Explicit preference setting** - "Set preference for...", "Change behavior..."
- **Behavior modification** - "Prefer guard clauses", "Use 2-space indentation"
- **FP strictness adjustment** - "Enable strict mode", "Relax FP rules"
- **Task granularity setting** - "Break tasks into smaller pieces"

---

## Workflow

### Trunk: parse_preference_request

Parses user's natural language preference request.

**Steps**:
1. **Extract intent** - What does user want to customize?
2. **Identify action** - Always do, never do, prefer, set to value
3. **Extract specifics** - Docstrings, function length, code style, etc.
4. **Route to directive matching** - Find which directive handles this

### Branches

**Branch 1: If parse_complete**
- **Then**: Find matching directive
- **Details**: AI queries directives table to find matching directive
  - Query aifp_core.db:
    ```sql
    SELECT name, description, intent_keywords_json, type
    FROM directives
    WHERE name LIKE '%file%' OR name LIKE '%write%'
       OR description LIKE '%docstring%'
       OR intent_keywords_json LIKE '%docstring%'
    ```
  - Returns scored matches:
    ```python
    [
      {"name": "project_file_write", "confidence": 0.85, "reason": "Handles file writing and docstrings"},
      {"name": "fp_docstring_enforcement", "confidence": 0.70, "reason": "Enforces docstrings"}
    ]
    ```
  - Sort by confidence descending
- **Result**: Directive candidates identified

**Branch 2: If single_directive_match**
- **Then**: `confirm_directive`
- **Details**: One clear match, confirm with user
  - Only one match above min_confidence (0.6)
  - Show user:
    ```
    Found directive: project_file_write

    Description: Write file AND update project.db (files, functions, interactions tables)

    This directive handles file writing operations including docstring management.

    Apply preference to this directive? (y/n): _
    ```
  - Wait for user confirmation
  - If user confirms → proceed to parse_preference_details
  - If user declines → fallback to prompt
- **Result**: User confirms directive match

**Branch 3: If multiple_matches**
- **Then**: `prompt_user`
- **Details**: Multiple directives match, disambiguate
  - Show options with descriptions:
    ```
    Multiple directives match your request. Which one?

    1. project_file_write (confidence: 85%)
       Description: Write file AND update project.db
       Handles: File writing, docstrings, function creation

    2. fp_docstring_enforcement (confidence: 70%)
       Description: Enforce docstrings on all functions
       Handles: Docstring validation, missing docstring detection

    3. Show more options

    Your choice (1-3): _
    ```
  - User selects directive number
  - Continue with selected directive
- **Result**: User selects specific directive

**Branch 4: If directive_confirmed**
- **Then**: `parse_preference_details`
- **Details**: Extract preference key and value from request
  - Parse user request for preference details:
    - **Request**: "always add docstrings"
      - Key: `always_add_docstrings`
      - Value: `"true"`
    - **Request**: "set max function length to 50"
      - Key: `max_function_length`
      - Value: `"50"`
    - **Request**: "prefer guard clauses over nested if"
      - Key: `prefer_guard_clauses`
      - Value: `"true"`
    - **Request**: "use 2-space indentation"
      - Key: `indent_style`
      - Value: `"spaces_2"`
  - Normalize key: lowercase with underscores
  - Validate value: Check type is reasonable
  - Optionally add description:
    - User: "always add docstrings"
    - Description: "Always add docstrings to functions"
- **Result**: Preference key-value extracted

**Branch 5: If preference_key_clear**
- **Then**: `update_or_insert`
- **Details**: UPSERT into directive_preferences table
  - Use UPSERT (INSERT OR REPLACE):
    ```sql
    INSERT INTO directive_preferences (
      directive_name,
      preference_key,
      preference_value,
      description,
      active,
      updated_at
    ) VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
    ON CONFLICT(directive_name, preference_key) DO UPDATE SET
      preference_value = excluded.preference_value,
      description = excluded.description,
      updated_at = CURRENT_TIMESTAMP
    ```
  - Example execution:
    ```sql
    INSERT INTO directive_preferences (
      directive_name, preference_key, preference_value, description
    ) VALUES (
      'project_file_write',
      'always_add_docstrings',
      'true',
      'Always add docstrings to functions'
    ) ON CONFLICT DO UPDATE SET
      preference_value='true',
      updated_at=CURRENT_TIMESTAMP
    ```
  - UNIQUE constraint ensures only one value per directive+key
  - If preference already exists → updates value
  - If new → inserts
- **Result**: Preference stored in database

**Branch 6: If preference_updated**
- **Then**: `confirm_with_user`
- **Details**: Show user the updated preference
  - Format confirmation message:
    ```
    ✅ Preference Updated

    Directive: project_file_write
    Preference: always_add_docstrings
    Value: true
    Description: Always add docstrings to functions

    This will apply to all future file write operations.

    Current preferences for project_file_write:
    • always_add_docstrings: true
    • max_function_length: 50
    • prefer_guard_clauses: true
    ```
  - Show all current preferences for directive (helpful context)
  - Preference active immediately (next sync loads it)
- **Result**: User informed of successful update

**Fallback**: `prompt_user`
- **Details**: Unable to determine preference or directive
  - Clarify what user wants:
    ```
    Could you specify which behavior you want to change?

    Examples:
    • "Always add docstrings when writing files"
    • "Set max function length to 50 lines"
    • "Prefer guard clauses over nested conditionals"
    • "Enable strict FP mode"
    • "Break tasks into smaller pieces"

    Or specify the directive explicitly:
    • "For project_file_write, always add docstrings"
    ```
  - Provide examples to guide user
  - Can ask for directive name explicitly
- **Result**: User clarifies request

---

## Examples

### ✅ Compliant Usage

**Setting Docstring Preference:**
```python
# User: "Always add docstrings when writing files"
# AI calls: user_preferences_update()

# Workflow:
# 1. parse_preference_request:
#    - Intent: "always add docstrings"
#    - Action: "always do"
#    - Context: "writing files"
#
# 2. find_directive_by_intent("always add docstrings writing files", min_confidence=0.6):
#    - Searches directives table
#    - Matches:
#      * project_file_write (confidence: 0.85) - handles file writing
#      * fp_docstring_enforcement (confidence: 0.70) - handles docstrings
#    - Returns both matches
#
# 3. multiple_matches: prompt_user
#    """
#    Multiple directives match. Which one?
#
#    1. project_file_write (85%)
#       Write files and update database
#
#    2. fp_docstring_enforcement (70%)
#       Enforce docstring compliance
#
#    Your choice: _
#    """
#
# 4. User inputs: 1 (project_file_write)
#
# 5. parse_preference_details:
#    - Key: "always_add_docstrings"
#    - Value: "true"
#    - Description: "Always add docstrings to functions"
#
# 6. update_or_insert:
#    INSERT INTO directive_preferences
#    (directive_name, preference_key, preference_value, description)
#    VALUES ('project_file_write', 'always_add_docstrings', 'true', '...')
#    ON CONFLICT DO UPDATE...
#
# 7. confirm_with_user:
#    """
#    ✅ Preference Updated
#
#    Directive: project_file_write
#    Preference: always_add_docstrings
#    Value: true
#
#    This will apply to all future file writes.
#    """
#
# Result:
# ✅ Preference stored
# ✅ Next file write will add docstrings
# ✅ user_preferences_sync will load this preference
```

---

**Setting Numeric Preference:**
```python
# User: "Set max function length to 50 lines"
# AI calls: user_preferences_update()

# Workflow:
# 1. parse_preference_request:
#    - Intent: "set max function length"
#    - Value: "50"
#
# 2. find_directive_by_intent("max function length", 0.6):
#    - Matches: project_file_write (0.90)
#    - Single match!
#
# 3. single_directive_match: confirm_directive
#    """
#    Found directive: project_file_write
#
#    Description: Write file operations
#
#    Apply preference? (y/n): _
#    """
#
# 4. User inputs: y
#
# 5. parse_preference_details:
#    - Key: "max_function_length"
#    - Value: "50"
#    - Validate: 50 is reasonable integer
#
# 6. update_or_insert:
#    INSERT INTO directive_preferences
#    (directive_name, preference_key, preference_value)
#    VALUES ('project_file_write', 'max_function_length', '50')
#    ON CONFLICT DO UPDATE SET preference_value='50'
#
# 7. confirm_with_user:
#    """
#    ✅ Preference Updated
#
#    Directive: project_file_write
#    Preference: max_function_length
#    Value: 50
#    Description: Maximum function length in lines
#    """
#
# Result:
# ✅ Max function length set to 50
# ✅ File writes will enforce 50-line limit
```

---

**Enabling Compliance Tracking:**
```python
# User: "I want to track FP compliance patterns"
# AI calls: user_preferences_update()

# Workflow:
# 1. parse_preference_request:
#    - Intent: "track FP compliance patterns"
#    - This is a tracking feature request, not a preference
#
# 2. Recognize tracking feature:
#    - AI identifies this as tracking_toggle directive, not user_preferences_update
#    - Inform user: "This is a tracking feature. Let me enable it for you."
#
# 3. Redirect to tracking_toggle:
#    - Call: tracking_toggle(feature_name="compliance_checking", enable=True)
#    - Show token overhead warning: "~5-10% token increase per check"
#
# 4. User confirms token overhead
#
# 5. Enable tracking:
#    UPDATE tracking_settings
#    SET enabled = 1
#    WHERE feature_name = 'compliance_checking'
#
# Result:
# ✅ Compliance tracking enabled
# ✅ project_compliance_check directive now available for analytics
# ✅ Note: FP compliance is baseline behavior - this only tracks patterns
```

---

### ❌ Non-Compliant Usage

**Not Using find_directive_by_intent:**
```python
# ❌ Hard-coding directive name
directive_name = "project_file_write"  # Assumes user knows internal name
# User said "always add docs" not "project_file_write"
```

**Why Non-Compliant**:
- Doesn't map natural language to directives
- Users shouldn't know internal directive names
- Breaks natural language interface

**Corrected:**
```python
# ✅ Query database to find matching directive
# AI uses NLP to match user intent to directive names/descriptions
directive_name = ai_match_intent_to_directive("always add docs")
if not directive_name:
    directive_name = prompt_user_for_clarification()
```

---

**Not Validating Preference Value:**
```python
# ❌ Storing invalid value
preference_value = "not_a_number"  # For max_function_length
# Stores without validation
```

**Why Non-Compliant**:
- Will cause errors when preference is used
- Should validate type matches expectation

**Corrected:**
```python
# ✅ Validate value
if preference_key == "max_function_length":
    try:
        int(preference_value)  # Validate it's a number
    except ValueError:
        return prompt_user("Invalid value - expected a number")
```

---

## Edge Cases

### Edge Case 1: Directive Not Found

**Issue**: No directive matches user request

**Handling**:
```python
matches = find_directive_by_intent(user_request, min_confidence=0.6)

if not matches:
    # No matches above confidence threshold
    return prompt_user("""
    No matching directive found for your request.

    Available directives:
    • project_file_write - File writing operations
    • project_task_decomposition - Task breakdown
    • project_compliance_check - FP compliance
    • git_merge_branch - Branch merging
    ...

    Please clarify which operation you want to customize.
    """)
```

**Directive Action**: Show list of available directives, ask user to clarify.

---

### Edge Case 2: Invalid Preference Value Type

**Issue**: User provides wrong type for preference

**Handling**:
```python
# User: "Set max function length to infinity"
if preference_key == "max_function_length":
    try:
        value_int = int(preference_value)
        if value_int < 1 or value_int > 1000:
            raise ValueError("Out of range")
    except ValueError:
        return prompt_user(f"""
        Invalid value for max_function_length: '{preference_value}'

        Expected: Integer between 1 and 1000
        Example: 50
        """)
```

**Directive Action**: Validate value type, prompt for correction.

---

### Edge Case 3: Conflicting Preference

**Issue**: New preference conflicts with existing one

**Handling**:
```python
# Check for conflicts
existing = query_db("""
  SELECT preference_key, preference_value
  FROM directive_preferences
  WHERE directive_name=? AND active=1
""", (directive_name,))

# Example: always_add_docstrings=true conflicts with never_add_docstrings=true
if new_key == "always_add_docstrings":
    if any(p["key"] == "never_add_docstrings" for p in existing):
        return prompt_user("""
        Conflicting preference detected:
        • Existing: never_add_docstrings = true
        • New: always_add_docstrings = true

        These conflict. What would you like to do?
        1. Replace with new preference
        2. Remove both (use default)
        3. Cancel
        """)
```

**Directive Action**: Detect conflicts, offer resolution options.

---

### Edge Case 4: User Specifies Directive Explicitly

**Issue**: User names directive directly instead of describing behavior

**Handling**:
```python
# User: "For project_file_write, always add docstrings"
if "for " in user_request.lower():
    # Extract explicit directive name
    directive_name = extract_directive_name(user_request)  # "project_file_write"

    # Verify directive exists
    if directive_exists(directive_name):
        # Skip find_directive_by_intent
        # Go directly to parse_preference_details
        parse_preference_details(user_request)
    else:
        return prompt_user(f"Directive '{directive_name}' not found")
```

**Directive Action**: Allow explicit directive naming, skip intent matching.

---

## Related Directives

- **Called By**:
  - User requests - Natural language preference setting
  - `aifp_run` - When user says "set preference..."
- **Calls**:
  - Database queries to find matching directives
  - Database setters for preference storage
- **Modifies**:
  - `directive_preferences` table - Stores user preferences
  - `user_settings` table - For global settings
- **Loaded By**:
  - `user_preferences_sync` - Reads preferences set by this directive
- **Related**:
  - `user_preferences_learn` - Also updates preferences (from corrections)
  - `tracking_toggle` - Updates tracking_settings table

---

## Helper Functions

This directive's helpers are dynamically mapped in `aifp_core.db`.

**Query at runtime**:
```python
get_helpers_for_directive(directive_id, include_helpers_data=true)
```

This returns all helpers associated with this directive, including database getters and setters for preference management.

See `helper_functions` and `directive_helpers` tables in aifp_core.db for complete specifications.

---

## Database Operations

This directive updates the following tables:

- **`directive_preferences`**: INSERT or UPDATE preference (UPSERT with UNIQUE constraint)
- **`user_settings`**: UPDATE for global preferences (e.g., project_continue_on_start, suppress_warnings)

**Queries from**:
- **`directives`** (aifp_core.db): Read directive descriptions and keywords for intent matching

---

## Testing

How to verify this directive is working:

1. **Set preference** → Stored in database
   ```python
   user_preferences_update(user_request="always add docstrings")

   # Check database
   result = query_db("""
     SELECT preference_value FROM directive_preferences
     WHERE directive_name='project_file_write' AND preference_key='always_add_docstrings'
   """)
   assert result[0][0] == "true"
   ```

2. **Update existing preference** → Value changed
   ```python
   # First set
   user_preferences_update("set max function length to 50")

   # Update
   user_preferences_update("set max function length to 100")

   # Check: only one row, value updated
   result = query_db("SELECT preference_value FROM directive_preferences WHERE preference_key='max_function_length'")
   assert result[0][0] == "100"
   assert len(result) == 1  # No duplicate
   ```

3. **Intent matching** → Finds correct directive
   ```python
   matches = find_directive_by_intent("add docstrings", 0.6)
   assert "project_file_write" in [m["name"] for m in matches]
   ```

4. **Preference loaded** → Next directive execution uses it
   ```python
   user_preferences_update("always add docstrings")
   context = user_preferences_sync("project_file_write")
   assert context["preferences"]["always_add_docstrings"] == True
   ```

---

## Common Mistakes

- ❌ **Not using find_directive_by_intent** - Hard-coding directive names
- ❌ **Not validating preference values** - Storing invalid data
- ❌ **Not checking for conflicts** - Creating contradictory preferences
- ❌ **Not using UPSERT** - Creating duplicate preference rows
- ❌ **Not confirming with user** - Applying to wrong directive

---

## Roadblocks and Resolutions

### Roadblock 1: directive_not_found
**Issue**: No directive matches user request (confidence < 0.6)
**Resolution**: Show list of available directives, ask user to be more specific

### Roadblock 2: invalid_preference_value
**Issue**: Value doesn't match expected type (e.g., "infinity" for max_length)
**Resolution**: Validate value type, prompt for correction with example

### Roadblock 3: preference_conflict
**Issue**: New preference contradicts existing one
**Resolution**: Show existing preference, ask user to confirm override or merge

---

## References

None
---

*Part of AIFP v1.0 - User customization directive for updating preferences*

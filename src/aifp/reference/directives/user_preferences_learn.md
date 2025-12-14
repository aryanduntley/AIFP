# Directive: user_preferences_learn

**Type**: Project
**Level**: 1
**Parent Directive**: user_preferences_sync
**Priority**: MEDIUM - Opt-in feature

---

## Purpose

The `user_preferences_learn` directive **detects user corrections and offers to learn preferences** from repeated patterns, enabling AI to adapt to user style over time. This is an **opt-in feature** (disabled by default) that logs corrections to `ai_interaction_log` and prompts the user whether to apply learned preferences project-wide.

This directive is **opt-in for privacy and cost reasons**:
- **Requires tracking enabled**: Must enable `ai_interaction_log` via `tracking_toggle`
- **Token cost**: ~3% increase (logs on every AI response with corrections)
- **User confirmation required**: Never applies preferences without explicit approval
- **Pattern detection**: Needs multiple corrections to infer preference (confidence threshold)
- **Transparency**: Shows user what preference will be applied before storing

The learning workflow:
1. **Detect correction** - User modifies or rejects AI output
2. **Log to ai_interaction_log** - Record interaction with context
3. **Identify pattern** - Repeated corrections suggest preference
4. **Infer preference** - Determine what user prefers
5. **Prompt user** - Ask if this should be remembered project-wide
6. **Update preferences** - If confirmed, add to `directive_preferences`

**Example Learning Scenario**:
- AI writes function without docstring
- User adds docstring
- AI logs: "User added docstring" (correction_type)
- After 3 similar corrections → AI asks: "I noticed you always add docstrings. Remember this preference?"
- User confirms → `always_add_docstrings: true` stored

**Privacy Note**: This feature requires explicit opt-in and users can review/delete ai_interaction_log at any time.

---

## When to Apply

This directive applies when:
- **User corrects AI output** - Modifies generated code, text, or suggestions
- **User rejects suggestion** - "Actually, do it this way instead"
- **Repeated patterns detected** - Same type of correction multiple times
- **After directive execution** - Check if user modified the output
- **Tracking enabled** - `ai_interaction_log` feature must be on

---

## Workflow

### Trunk: detect_correction

Detects when user corrects or modifies AI output.

**Steps**:
1. **Compare AI output vs final code** - Did user change what AI generated?
2. **Classify correction type** - What changed? (docstring, structure, style, logic)
3. **Determine context** - Which directive was executing?
4. **Route to logging** - Record interaction for pattern analysis

### Branches

**Branch 1: If correction_detected**
- **Then**: `log_to_ai_interaction`
- **Details**: Record correction to ai_interaction_log table
  - Insert:
    ```sql
    INSERT INTO ai_interaction_log (
      interaction_type,
      directive_context,
      user_feedback,
      ai_interpretation,
      applied_to_preferences,
      created_at
    ) VALUES (
      'correction',
      'project_file_write',
      'User added docstring to calculate_total function',
      'User prefers functions to have docstrings',
      0,  -- Not yet applied to preferences
      CURRENT_TIMESTAMP
    )
    ```
  - Fields:
    - `interaction_type`: 'correction', 'clarification', 'preference_learned'
    - `directive_context`: Which directive was running
    - `user_feedback`: What user changed/said
    - `ai_interpretation`: What AI thinks this means
    - `applied_to_preferences`: Whether this led to preference update
  - This creates audit trail for learning
- **Result**: Correction logged

**Branch 2: If pattern_identified**
- **Then**: `infer_preference`
- **Details**: Analyze recent corrections for patterns
  - Query recent corrections:
    ```sql
    SELECT user_feedback, ai_interpretation, directive_context
    FROM ai_interaction_log
    WHERE interaction_type = 'correction'
      AND directive_context = 'project_file_write'
      AND created_at > datetime('now', '-7 days')
    ORDER BY created_at DESC
    LIMIT 10
    ```
  - Pattern detection:
    - **Docstrings**: 3+ corrections adding docstrings → Preference: `always_add_docstrings`
    - **Guard clauses**: 3+ corrections converting nested if to guards → Preference: `prefer_guard_clauses`
    - **Explicit returns**: 3+ corrections adding explicit returns → Preference: `prefer_explicit_returns`
    - **Indentation**: 3+ corrections changing spaces → Preference: `indent_style`
  - Confidence scoring:
    - 3+ similar corrections → 0.80 confidence
    - 5+ similar corrections → 0.90 confidence
    - 10+ similar corrections → 0.95 confidence
  - Only proceed if confidence ≥ 0.80
- **Result**: Pattern identified with confidence score

**Branch 3: If high_confidence**
- **Then**: `prompt_user`
- **Details**: Ask user if preference should be remembered
  - Show prompt:
    ```
    🤖 Learning Opportunity

    I noticed you've made 3 similar corrections:
    • 2024-10-27: Added docstring to calculate_total
    • 2024-10-26: Added docstring to format_result
    • 2024-10-25: Added docstring to validate_input

    Pattern detected: You prefer functions to have docstrings

    Would you like me to remember this preference?

    If yes, I'll always add docstrings when writing functions.

    Scope: Project-wide (all future file writes in this project)

    Remember preference? (y/n): _
    ```
  - Wait for user confirmation
  - Show scope (project-wide)
  - Explain what will happen
- **Result**: User confirms or declines

**Branch 4: If user_confirms**
- **Then**: `update_directive_preferences`
- **Details**: Apply learned preference to database
  - Call: `user_preferences_update`
  - Insert:
    ```sql
    INSERT INTO directive_preferences (
      directive_name,
      preference_key,
      preference_value,
      description
    ) VALUES (
      'project_file_write',
      'always_add_docstrings',
      'true',
      'Learned from user corrections: Always add docstrings'
    ) ON CONFLICT DO UPDATE SET
      preference_value='true',
      updated_at=CURRENT_TIMESTAMP
    ```
  - Mark interactions as applied:
    ```sql
    UPDATE ai_interaction_log
    SET applied_to_preferences = 1
    WHERE id IN (123, 124, 125)  -- IDs of related corrections
    ```
  - Confirm with user:
    ```
    ✅ Preference Learned

    Directive: project_file_write
    Preference: always_add_docstrings = true

    Future file writes will automatically include docstrings.

    You can change this anytime with:
    "Turn off docstrings" or "Remove preference for docstrings"
    ```
- **Result**: Preference stored and active

**Branch 5: If low_confidence**
- **Then**: `log_only`
- **Details**: Pattern unclear, just log without prompting
  - Confidence < 0.80 (fewer than 3 similar corrections)
  - Log correction but don't prompt user
  - Continue monitoring for clearer pattern
  - Skip prompt: Avoids annoying user with low-confidence suggestions
- **Result**: Logged silently, monitoring continues

**Fallback**: `continue`
- **Details**: No correction detected or tracking disabled
  - No action needed
  - Most common path (no corrections)
  - Tracking may be disabled (default state)
- **Result**: Normal execution continues

---

## Examples

### ✅ Compliant Usage

**Learning Docstring Preference:**
```python
# Session 1: User adds docstring to AI-generated function
# AI generated:
def calculate_total(items, tax_rate):
    return sum(items) * (1 + tax_rate)

# User edited to:
def calculate_total(items, tax_rate):
    """Calculate total with tax."""
    return sum(items) * (1 + tax_rate)

# AI detects correction
correction = detect_correction(ai_output, user_final)
# → Changed: Added docstring

# Log to ai_interaction_log
log_interaction({
  "type": "correction",
  "context": "project_file_write",
  "feedback": "User added docstring",
  "interpretation": "User prefers docstrings"
})

# Pattern: Only 1 correction so far → Low confidence (0.33)
# → log_only (no prompt)

# Session 2: User adds docstring again
# → Log second correction
# Pattern: 2 corrections → Moderate confidence (0.66)
# → log_only (wait for more data)

# Session 3: User adds docstring third time
# → Log third correction
# Pattern: 3 corrections → High confidence (0.80)
# → prompt_user:
"""
🤖 Learning Opportunity

Pattern detected: You've added docstrings 3 times

Would you like me to always add docstrings?

Remember preference? (y/n): _
"""

# User inputs: y

# update_directive_preferences:
INSERT INTO directive_preferences
VALUES ('project_file_write', 'always_add_docstrings', 'true', '...')

UPDATE ai_interaction_log
SET applied_to_preferences = 1
WHERE id IN (corrected_interaction_ids)

# Result:
# ✅ Preference learned and stored
# ✅ Future file writes include docstrings automatically
# ✅ User corrections applied project-wide
```

---

**Learning Code Style Preference:**
```python
# User repeatedly converts nested if to guard clauses

# Correction 1:
# AI generated:
if condition1:
    if condition2:
        do_something()

# User changed to:
if not condition1:
    return
if not condition2:
    return
do_something()

# Log: "User converted nested if to guard clauses"

# After 3 similar corrections → Prompt:
"""
Pattern detected: You prefer guard clauses over nested if statements

Remember preference? (y/n): _
"""

# User confirms → Store:
# preference_key: prefer_guard_clauses
# preference_value: true

# Result:
# ✅ Future code uses guard clause pattern
# ✅ AI adapts to user style
```

---

### ❌ Non-Compliant Usage

**Applying Without User Confirmation:**
```python
# ❌ Auto-applying learned preferences
if pattern_confidence > 0.8:
    # Applying without asking user
    update_directive_preferences(...)
# User wasn't asked!
```

**Why Non-Compliant**:
- Violates user consent
- Could apply incorrect preferences
- User should always approve

**Corrected:**
```python
# ✅ Always prompt user first
if pattern_confidence > 0.8:
    if prompt_user("Remember this preference?") == "yes":
        update_directive_preferences(...)
```

---

**Learning from Single Correction:**
```python
# ❌ Low confidence threshold
if corrections_count >= 1:  # Only 1 correction!
    prompt_user("Remember preference?")
# Too eager - could be one-off change
```

**Why Non-Compliant**:
- Single correction doesn't indicate preference
- Should require pattern (3+ corrections)

**Corrected:**
```python
# ✅ Require pattern (3+ corrections)
if corrections_count >= 3 and confidence >= 0.80:
    prompt_user("Remember preference?")
```

---

## Edge Cases

### Edge Case 1: User Declines Learning

**Issue**: User says "no" to learning preference

**Handling**:
```python
if user_response == "no":
    # Mark in ai_interaction_log to not ask again
    conn.execute("""
      INSERT INTO ai_interaction_log (interaction_type, user_feedback, applied_to_preferences)
      VALUES ('preference_declined', 'User declined docstring preference', -1)
    """)
    # -1 = explicitly declined (don't ask again for this pattern)
```

**Directive Action**: Respect user's decision, don't prompt again for same pattern.

---

### Edge Case 2: Conflicting Corrections

**Issue**: User makes contradictory corrections

**Handling**:
```python
# Day 1: User adds docstrings (3 times)
# Day 5: User removes docstrings (3 times)

# Conflicting patterns detected
if has_opposite_pattern(pattern_history):
    prompt_user("""
    Conflicting patterns detected:
    • Oct 27-29: Added docstrings (3 times)
    • Nov 1-3: Removed docstrings (3 times)

    Which do you prefer?
    1. Always add docstrings
    2. Never add docstrings
    3. Context-dependent (no preference)
    """)
```

**Directive Action**: Present conflict, ask user to clarify.

---

### Edge Case 3: Tracking Disabled Mid-Session

**Issue**: User disables tracking while corrections pending

**Handling**:
```python
# Check if tracking still enabled
if not is_tracking_enabled("ai_interaction_log"):
    # Tracking was disabled
    # Clear pending pattern analysis
    # Don't prompt user
    log_to_project_notes("Tracking disabled - clearing pending pattern analysis")
    return
```

**Directive Action**: Respect tracking toggle, clear pending analysis.

---

## Related Directives

- **Called By**:
  - `project_file_write` - After file write completes
  - `aifp_run` - After any directive with corrections
- **Calls**:
  - `user_preferences_update` - To store learned preference
  - Database helpers for ai_interaction_log
- **Requires**:
  - `tracking_toggle` - Must enable ai_interaction_log first
- **Related**:
  - `user_preferences_update` - Explicit preference setting (user tells AI)
  - `user_preferences_sync` - Loads preferences learned by this directive

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`ai_interaction_log`**: INSERT corrections, UPDATE applied_to_preferences flag
- **`directive_preferences`**: INSERT learned preferences (via user_preferences_update)

**Requires tracking enabled**:
- `tracking_settings.ai_interaction_log` must be enabled (=1)

---

## Testing

How to verify this directive is working:

1. **Detect correction** → Logged to ai_interaction_log
   ```python
   # Make correction
   detect_and_log_correction(ai_output, user_modified)

   # Check log
   result = query_db("SELECT * FROM ai_interaction_log WHERE interaction_type='correction'")
   assert len(result) > 0
   ```

2. **Pattern detection** → High confidence after 3+ corrections
   ```python
   # Log 3 similar corrections
   for i in range(3):
       log_correction("added docstring")

   confidence = calculate_pattern_confidence("added docstring")
   assert confidence >= 0.80
   ```

3. **User confirmation** → Preference stored
   ```python
   # User confirms learning
   user_preferences_learn(user_confirms=True)

   # Check preference
   result = query_db("SELECT * FROM directive_preferences WHERE preference_key='always_add_docstrings'")
   assert len(result) == 1
   ```

4. **Tracking disabled** → No learning occurs
   ```python
   # Disable tracking
   disable_tracking("ai_interaction_log")

   # Make correction
   result = user_preferences_learn()
   assert result.skipped == True  # Tracking disabled
   ```

---

## Common Mistakes

- ❌ **Applying without user confirmation** - Always ask first
- ❌ **Low confidence threshold** - Need 3+ corrections minimum
- ❌ **Not checking tracking enabled** - Respect tracking toggle
- ❌ **Not handling declined preferences** - Mark as declined, don't ask again
- ❌ **Learning from one-off changes** - Distinguish pattern from exception

---

## Roadblocks and Resolutions

### Roadblock 1: correction_unclear
**Issue**: Can't determine what user corrected or why
**Resolution**: Log to ai_interaction_log but don't prompt user (wait for clearer pattern)

### Roadblock 2: conflicting_corrections
**Issue**: User makes opposite corrections at different times
**Resolution**: Present conflict to user, ask for clarification on preference

### Roadblock 3: user_declines_preference
**Issue**: User says "no" to learning
**Resolution**: Mark in ai_interaction_log as declined, don't ask again for this pattern

---

## References

None
---

*Part of AIFP v1.0 - User customization directive for learning from corrections (opt-in)*

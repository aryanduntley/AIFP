# Directive: user_preferences_sync

**Type**: Project
**Level**: 0
**Parent Directive**: aifp_run
**Priority**: HIGH - Critical for customization

---

## Purpose

The `user_preferences_sync` directive **loads and applies user preferences** before executing any project directive, enabling users to customize AI behavior on a per-directive basis. This directive acts as the **synchronization layer** between the `user_preferences.db` database and the runtime directive execution context, ensuring that user customizations are consistently applied across all AI operations.

This directive is **essential for user customization** because:
- **Per-directive behavior overrides**: Each directive can have custom preferences
- **Atomic key-value structure**: Multiple preferences per directive (e.g., `always_add_docstrings: true`, `max_function_length: 50`)
- **Session-level caching**: Preferences loaded once per session for performance
- **Automatic execution**: Called before file writes, compliance checks, and task operations
- **Graceful fallback**: Continues without preferences if database unavailable
- **Tracking control**: Respects user's tracking feature flags

The sync workflow:
1. **Check preferences database** - Does `user_preferences.db` exist?
2. **Load preferences** - Query `directive_preferences` table for current directive
3. **Apply to context** - Add preferences to directive execution context
4. **Enable tracking** - Check `tracking_settings` if opt-in features enabled
5. **Continue execution** - Directive proceeds with custom

ized behavior

**Design Philosophy**: Preferences are **opt-in customizations**, not requirements. If no preferences exist, directives use sensible defaults. The database is created on-demand when users first customize behavior.

---

## When to Apply

This directive applies when:
- **Called by `aifp_run`** - Before executing any project directive
- **Before file writes** - `project_file_write` calls sync for preferences
- **Before compliance checks** - `project_compliance_check` applies strictness level
- **Before task operations** - `project_task_decomposition` respects granularity settings
- **Session initialization** - Load preferences once and cache for session

---

## Workflow

### Trunk: check_preferences_db

Checks if `user_preferences.db` exists and is accessible.

**Steps**:
1. **Check database file** - Does `.aifp/user_preferences.db` exist?
2. **Verify accessibility** - Can we read/write to the database?
3. **Route based on status** - Exists, missing, or corrupted
4. **Cache for session** - Store loaded preferences in memory

### Branches

**Branch 1: If preferences_db_exists**
- **Then**: `load_preferences`
- **Details**: Load directive-specific preferences from database
  - Query:
    ```sql
    SELECT preference_key, preference_value, description
    FROM directive_preferences
    WHERE directive_name = ? AND active = 1
    ```
  - Example query: `directive_name = 'project_file_write'`
  - Results:
    ```python
    [
      {"key": "always_add_docstrings", "value": "true", "desc": "Always add docstrings"},
      {"key": "max_function_length", "value": "50", "desc": "Max function length"},
      {"key": "prefer_guard_clauses", "value": "true", "desc": "Use guard clauses"}
    ]
    ```
  - Cache duration: Session (until AI session ends)
  - Parse JSON values if needed
  - Store in directive context dictionary
- **Result**: Preferences loaded into context

**Branch 2: If no_preferences_db**
- **Then**: `initialize_defaults`
- **Details**: Create user_preferences.db with default schema
  - Action: This is first-time setup or database was deleted
  - Create database file: `.aifp/user_preferences.db`
  - Use schema: `schemaExampleSettings.sql`
  - Create tables:
    - `user_settings` - Project-wide AI behavior
    - `directive_preferences` - Per-directive customizations
    - `ai_interaction_log` - User corrections (disabled)
    - `fp_flow_tracking` - Compliance tracking (disabled)
    - `issue_reports` - Bug reports (disabled)
    - `tracking_settings` - Feature flags (all disabled)
  - Insert default settings:
    ```sql
    INSERT INTO user_settings (setting_key, setting_value, description, scope) VALUES
      ('project_continue_on_start', 'false', 'Automatically continue project work on session start', 'project'),
      ('suppress_warnings', '[]', 'Directives to suppress warnings', 'project');
    ```
  - Insert default tracking settings (all disabled):
    ```sql
    INSERT INTO tracking_settings (feature_name, enabled, description, estimated_token_overhead) VALUES
      ('fp_flow_tracking', 0, 'Track FP directive consultations', '~5% token increase per file write'),
      ('issue_reports', 0, 'Enable issue reports', '~2% token increase on errors'),
      ('ai_interaction_log', 0, 'Log AI interactions', '~3% token increase overall'),
      ('helper_function_logging', 0, 'Log helper errors', '~1% token increase on errors'),
      ('compliance_checking', 0, 'Track FP compliance patterns (analytics, NOT validation)', '~5-10% token increase per check');
    ```
  - Message: "Preferences database initialized with defaults"
- **Result**: Database created, no preferences loaded yet

**Branch 3: If directive_preferences_found**
- **Then**: `apply_to_context`
- **Details**: Add loaded preferences to directive execution context
  - Parse preference values:
    - Simple strings: `"true"`, `"false"`, `"50"`
    - JSON objects: `{"level": "strict", "exceptions": []}`
  - Add to context dictionary:
    ```python
    context = {
      "directive_name": "project_file_write",
      "preferences": {
        "always_add_docstrings": True,
        "max_function_length": 50,
        "prefer_guard_clauses": True,
        "code_style": "explicit",
        "indent_style": "spaces_2"
      },
      "user_settings": {
        "project_continue_on_start": False,
        "suppress_warnings": []
      }
    }
    ```
  - This context passed to directive workflow
  - Directive reads `context.preferences` to customize behavior
- **Result**: Directive has access to user preferences

**Branch 4: If tracking_enabled**
- **Then**: `enable_logging`
- **Details**: Check tracking_settings for opt-in features
  - Query:
    ```sql
    SELECT feature_name, enabled
    FROM tracking_settings
    WHERE enabled = 1
    ```
  - Enabled features activate logging:
    - `ai_interaction_log=1` → Log all user corrections
    - `fp_flow_tracking=1` → Log FP compliance checks
    - `issue_reports=1` → Enable issue report compilation
    - `helper_function_logging=1` → Log helper errors
  - Add to context:
    ```python
    context["tracking_enabled"] = {
      "ai_interaction_log": True,
      "fp_flow_tracking": False,
      "issue_reports": False,
      "helper_function_logging": False
    }
    ```
  - Directives check this to conditionally log
- **Result**: Tracking flags set in context

**Fallback**: `continue_without_preferences`
- **Details**: No preferences available, use defaults
  - Message: "No user preferences found - using defaults"
  - Directive proceeds with built-in default behavior
  - This is normal for new projects or users who haven't customized
  - No error - graceful degradation
- **Result**: Directive uses defaults

---

## Examples

### ✅ Compliant Usage

**Loading Preferences for File Write:**
```python
# User has customized project_file_write behavior
# Preferences in database:
# - always_add_docstrings: true
# - max_function_length: 50
# - prefer_guard_clauses: true

# AI calls: user_preferences_sync(directive_name="project_file_write")

# Workflow:
# 1. check_preferences_db: ✓ .aifp/user_preferences.db exists
# 2. load_preferences:
#    SELECT preference_key, preference_value
#    FROM directive_preferences
#    WHERE directive_name='project_file_write' AND active=1
#    → Returns 3 rows
# 3. apply_to_context:
#    context = {
#      "preferences": {
#        "always_add_docstrings": True,
#        "max_function_length": 50,
#        "prefer_guard_clauses": True
#      }
#    }
# 4. tracking_enabled: Check tracking_settings
#    → All disabled (default)
#
# Result:
# ✅ Preferences loaded
# ✅ project_file_write will:
#    - Add docstrings to all functions
#    - Enforce 50-line max per function
#    - Use guard clauses instead of nested ifs
```

---

**First-Time Setup (No Database):**
```python
# User's first AIFP session, no preferences yet
# AI calls: user_preferences_sync(directive_name="project_init")

# Workflow:
# 1. check_preferences_db: ✗ No .aifp/user_preferences.db
# 2. initialize_defaults:
#    - Create .aifp/user_preferences.db
#    - Run schemaExampleSettings.sql
#    - Insert default user_settings
#    - Insert default tracking_settings (all disabled)
#    - Message: "Preferences database initialized"
# 3. No directive preferences exist yet
# 4. continue_without_preferences
#
# Result:
# ✅ Database created with defaults
# ✅ Directive proceeds with built-in defaults
# ✅ User can customize later via user_preferences_update
```

---

**Loading Global Autostart Setting:**
```python
# User enabled autostart
# user_settings table:
# - project_continue_on_start: true

# AI calls: user_preferences_sync(directive_name="aifp_run")

# Workflow:
# 1. check_preferences_db: ✓ Exists
# 2. load_preferences:
#    - User settings: project_continue_on_start = "true"
# 3. apply_to_context:
#    context = {
#      "user_settings": {
#        "project_continue_on_start": True
#      },
#      "preferences": {}
#    }
# 4. aifp_run checks project_continue_on_start
#    → Automatically continues project work with context and state
#
# Result:
# ✅ Autostart setting applied
# ✅ AI automatically resumes work on session start
```

---

**Session Caching (Performance):**
```python
# First file write in session
user_preferences_sync(directive_name="project_file_write")
# → Queries database, caches preferences

# Second file write in same session
user_preferences_sync(directive_name="project_file_write")
# → Uses cached preferences (no database query)
# → Much faster (no I/O)

# Session ends
# → Cache cleared

# New session starts
# → Preferences reloaded from database (fresh state)
```

---

### ❌ Non-Compliant Usage

**Not Calling Before Directive:**
```python
# ❌ Executing directive without loading preferences
project_file_write(path="src/calc.py", content=code)
# User's preference for "always_add_docstrings" ignored
```

**Why Non-Compliant**:
- User customizations not applied
- Inconsistent behavior
- User expectations violated

**Corrected:**
```python
# ✅ Always sync preferences first
user_preferences_sync(directive_name="project_file_write")
project_file_write(path="src/calc.py", content=code)
# Now respects user's docstring preference
```

---

**Hard-Coding Behavior Instead of Preferences:**
```python
# ❌ Hard-coded behavior
def project_file_write(path, content):
    always_add_docstrings = True  # ← Hard-coded
    # Ignores user preferences
```

**Why Non-Compliant**:
- Not respecting user customization
- Should read from context.preferences

**Corrected:**
```python
# ✅ Read from preferences
def project_file_write(path, content, context):
    always_add_docstrings = context.get("preferences", {}).get("always_add_docstrings", False)
    # Uses user preference, defaults to False
```

---

## Edge Cases

### Edge Case 1: Database Corrupted

**Issue**: `user_preferences.db` exists but is corrupted

**Handling**:
```python
try:
    conn = sqlite3.connect(".aifp/user_preferences.db")
    conn.execute("SELECT 1 FROM user_settings LIMIT 1")
except sqlite3.DatabaseError:
    # Database corrupted
    backup_path = f".aifp/user_preferences.db.backup.{timestamp}"
    shutil.copy(".aifp/user_preferences.db", backup_path)

    # Recreate from schema
    os.remove(".aifp/user_preferences.db")
    initialize_defaults()

    log_to_notes(f"Preferences database corrupted - backed up to {backup_path} and recreated")
```

**Directive Action**: Backup corrupted database, recreate from schema.

---

### Edge Case 2: Conflicting Preferences

**Issue**: Directive has contradictory preferences

**Handling**:
```python
# Example: Both "always_add_docstrings: true" AND "never_add_docstrings: true"
preferences = load_preferences("project_file_write")

if "always_add_docstrings" in preferences and "never_add_docstrings" in preferences:
    # Conflict detected
    prompt_user("""
    Conflicting preferences detected for project_file_write:
    - always_add_docstrings: true
    - never_add_docstrings: true

    Which should take precedence?
    1. Always add docstrings
    2. Never add docstrings
    3. Remove both (use default)
    """)
```

**Directive Action**: Detect conflicts, prompt user for resolution.

---

### Edge Case 3: Invalid Preference Value

**Issue**: Preference value doesn't match expected type

**Handling**:
```python
# Preference: max_function_length: "not_a_number"
try:
    max_length = int(preference_value)
except ValueError:
    log_to_notes(f"Invalid preference value for max_function_length: '{preference_value}' (expected integer)")
    # Use default
    max_length = DEFAULT_MAX_FUNCTION_LENGTH
```

**Directive Action**: Validate preference values, use defaults for invalid values.

---

### Edge Case 4: Tracking Enabled but Table Doesn't Exist

**Issue**: User enabled tracking but table was dropped

**Handling**:
```python
# Check if fp_flow_tracking enabled
if tracking_enabled["fp_flow_tracking"]:
    try:
        conn.execute("SELECT 1 FROM fp_flow_tracking LIMIT 1")
    except sqlite3.OperationalError:
        # Table doesn't exist
        log_to_notes("fp_flow_tracking enabled but table missing - recreating")
        create_fp_flow_tracking_table()
```

**Directive Action**: Recreate missing tracking tables if enabled.

---

## Related Directives

- **Called By**:
  - `aifp_run` - Before any project directive
  - `project_file_write` - Before file operations
  - `project_compliance_check` - Before FP checks
  - `project_task_decomposition` - Before task operations
- **Calls**:
  - Database query helpers
  - Schema initialization helpers
- **Enables**:
  - `user_preferences_update` - Modifies preferences this directive loads
  - `user_preferences_learn` - Adds learned preferences
  - `tracking_toggle` - Controls tracking flags
- **Related**:
  - `user_preferences_export` - Exports preferences loaded by this directive
  - `user_preferences_import` - Imports preferences for this directive to load

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive reads the following tables:

- **`directive_preferences`**: Reads per-directive customizations (WHERE directive_name=? AND active=1)
- **`user_settings`**: Reads project-wide AI behavior settings
- **`tracking_settings`**: Reads tracking feature flags to enable opt-in logging

**Note**: This directive only **reads** from user_preferences.db. Updates are handled by `user_preferences_update` and `user_preferences_learn`.

---

## Testing

How to verify this directive is working:

1. **No database** → Creates with defaults
   ```python
   # Remove database
   os.remove(".aifp/user_preferences.db")

   user_preferences_sync("project_file_write")
   # Check: Database created
   assert os.path.exists(".aifp/user_preferences.db")
   ```

2. **Load existing preferences** → Returns correct values
   ```python
   # Insert preference
   conn.execute("""INSERT INTO directive_preferences
                   (directive_name, preference_key, preference_value)
                   VALUES ('project_file_write', 'always_add_docstrings', 'true')""")

   context = user_preferences_sync("project_file_write")
   assert context["preferences"]["always_add_docstrings"] == True
   ```

3. **Session caching** → Second call uses cache
   ```python
   # First call
   start = time.time()
   user_preferences_sync("project_file_write")
   first_duration = time.time() - start

   # Second call (cached)
   start = time.time()
   user_preferences_sync("project_file_write")
   second_duration = time.time() - start

   assert second_duration < first_duration  # Much faster
   ```

4. **Tracking flags** → Respects enabled features
   ```python
   # Enable tracking
   conn.execute("UPDATE tracking_settings SET enabled=1 WHERE feature_name='ai_interaction_log'")

   context = user_preferences_sync("project_file_write")
   assert context["tracking_enabled"]["ai_interaction_log"] == True
   ```

---

## Common Mistakes

- ❌ **Not calling before directive execution** - Preferences ignored
- ❌ **Querying database every time** - Should cache for session
- ❌ **Not handling missing database** - Should initialize gracefully
- ❌ **Hard-coding behavior** - Should read from preferences
- ❌ **Not validating preference values** - Can cause runtime errors

---

## Roadblocks and Resolutions

### Roadblock 1: preferences_db_missing
**Issue**: Database doesn't exist
**Resolution**: Initialize with default schema, continue with defaults

### Roadblock 2: preferences_db_corrupted
**Issue**: Database file corrupted
**Resolution**: Backup corrupt DB, recreate from schema, log to notes

### Roadblock 3: conflicting_preferences
**Issue**: Contradictory preferences set
**Resolution**: Prompt user for resolution, update database

---

## References

None
---

*Part of AIFP v1.0 - User customization directive for loading preferences*

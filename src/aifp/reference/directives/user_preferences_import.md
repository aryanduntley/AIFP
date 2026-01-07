# Directive: user_preferences_import

**Type**: Project
**Level**: 2
**Parent Directive**: user_preferences_sync
**Priority**: LOW - Utility feature

---

## Purpose

The `user_preferences_import` directive **imports previously exported preferences** from a JSON file into `user_preferences.db`, enabling users to restore settings from backups, share preferences across projects, or migrate settings to new machines. This directive validates imported data, detects conflicts with existing preferences, and prompts the user for resolution strategies.

This directive is **useful for**:
- **Backup restoration**: Recover preferences after database corruption or reset
- **Cross-project sharing**: Apply same preferences to multiple projects
- **Team standardization**: Share team-wide preference settings
- **Machine migration**: Transfer preferences to new development environment
- **Version control**: Store preferences in Git and import when cloning repo

The import workflow:
1. **Read import file** - Load JSON file specified by user
2. **Validate schema** - Ensure JSON structure matches expected format
3. **Detect conflicts** - Compare with existing preferences
4. **Prompt for resolution** - Ask user how to handle conflicts
5. **Import preferences** - Insert/update database tables
6. **Confirm completion** - Show summary of imported preferences

**Export Format** (JSON):
```json
{
  "version": "1.0",
  "exported_at": "2024-10-27T14:30:00Z",
  "user_settings": [
    {"key": "project_continue_on_start", "value": "true", "description": "Automatically continue project work on session start"},
    {"key": "suppress_warnings", "value": "[]", "description": "Directives to suppress warnings"}
  ],
  "directive_preferences": [
    {"directive": "project_file_write", "key": "always_add_docstrings", "value": "true", "description": "Always add docstrings to functions"}
  ],
  "tracking_settings": [
    {"feature": "ai_interaction_log", "enabled": false},
    {"feature": "compliance_checking", "enabled": false}
  ]
}
```

---

## When to Apply

This directive applies when:
- **User requests import** - "Import preferences from file", "Restore settings"
- **After database reset** - Recover from backup
- **Project cloning** - Setup preferences in new project instance
- **Team onboarding** - Import team's standardized settings
- **Machine migration** - Transfer settings to new computer

---

## Workflow

### Trunk: read_import_file

Reads and parses the import JSON file.

**Steps**:
1. **Get file path** - User provides or select from `.aifp/backups/`
2. **Read JSON** - Load file contents
3. **Parse JSON** - Convert to Python dict
4. **Route to validation** - Check structure and version

### Branches

**Branch 1: If file_valid**
- **Then**: `validate_schema`
- **Details**: Validate JSON structure matches expected format
  - Check version compatibility:
    ```python
    if data["version"] != "1.0":
        if data["version"] < "1.0":
            prompt_user("Older format detected. Attempt migration? (y/n)")
        else:
            prompt_user("Newer format detected. Update AIFP to import this file.")
    ```
  - Validate required fields:
    - `version`: Must exist
    - `user_settings`: Array of {key, value, description}
    - `directive_preferences`: Array of {directive, key, value, description}
  - Optional fields:
    - `tracking_settings`: Array of {feature, enabled}
  - Check data types:
    - All keys are strings
    - Values are strings (may contain JSON)
    - enabled is boolean
- **Result**: Schema validated

**Branch 2: If conflicts_detected**
- **Then**: `prompt_user`
- **Details**: Compare imported vs existing preferences, ask resolution
  - Query existing preferences:
    ```sql
    SELECT directive_name, preference_key, preference_value
    FROM directive_preferences
    WHERE active=1
    ```
  - Find conflicts:
    ```python
    conflicts = []
    for imported_pref in import_data["directive_preferences"]:
        existing = find_existing(imported_pref["directive"], imported_pref["key"])
        if existing and existing["value"] != imported_pref["value"]:
            conflicts.append({
              "directive": imported_pref["directive"],
              "key": imported_pref["key"],
              "existing_value": existing["value"],
              "imported_value": imported_pref["value"]
            })
    ```
  - Present conflicts to user:
    ```
    Conflicts Detected

    1. project_file_write.always_add_docstrings
       Existing: true
       Imported: false
       → Use which? (existing/imported/skip)

    2. project_file_write.max_function_length
       Existing: 50
       Imported: 100
       → Use which? (existing/imported/skip)

    Resolve all conflicts:
    1. Keep existing (ignore imported for conflicts)
    2. Use imported (overwrite existing)
    3. Merge (prompt for each conflict individually)

    Your choice (1-3): _
    ```
  - User selects resolution strategy
- **Result**: Conflict resolution strategy determined

**Branch 3: If validation_passed**
- **Then**: `import_preferences`
- **Details**: Import preferences into database based on resolution strategy
  - Begin transaction (atomic import):
    ```python
    conn.execute("BEGIN TRANSACTION")
    try:
        # Import user_settings
        for setting in import_data["user_settings"]:
            conn.execute("""
              INSERT INTO user_settings (setting_key, setting_value, description)
              VALUES (?, ?, ?)
              ON CONFLICT(setting_key) DO UPDATE SET
                setting_value = excluded.setting_value,
                description = excluded.description,
                updated_at = CURRENT_TIMESTAMP
            """, (setting["key"], setting["value"], setting["description"]))

        # Import directive_preferences based on resolution strategy
        for pref in import_data["directive_preferences"]:
            if resolution_strategy == "keep_existing":
                # Only insert if doesn't exist
                conn.execute("""
                  INSERT OR IGNORE INTO directive_preferences
                  (directive_name, preference_key, preference_value, description)
                  VALUES (?, ?, ?, ?)
                """, (pref["directive"], pref["key"], pref["value"], pref["description"]))
            elif resolution_strategy == "use_imported":
                # Upsert (overwrite existing)
                conn.execute("""
                  INSERT INTO directive_preferences
                  (directive_name, preference_key, preference_value, description)
                  VALUES (?, ?, ?, ?)
                  ON CONFLICT(directive_name, preference_key) DO UPDATE SET
                    preference_value = excluded.preference_value,
                    description = excluded.description,
                    updated_at = CURRENT_TIMESTAMP
                """, (pref["directive"], pref["key"], pref["value"], pref["description"]))
            elif resolution_strategy == "merge":
                # User resolved each conflict individually
                if pref in resolved_preferences:
                    # User chose to import this one
                    conn.execute(...)

        # Import tracking_settings if present
        if "tracking_settings" in import_data:
            for tracking in import_data["tracking_settings"]:
                conn.execute("""
                  UPDATE tracking_settings
                  SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                  WHERE feature_name = ?
                """, (tracking["enabled"], tracking["feature"]))

        conn.execute("COMMIT")
    except Exception as e:
        conn.execute("ROLLBACK")
        raise
    ```
  - Count imported:
    - user_settings: X updated
    - directive_preferences: Y inserted, Z updated
    - tracking_settings: W updated
- **Result**: Preferences imported successfully

**Branch 4: If import_complete**
- **Then**: `confirm_with_user`
- **Details**: Show import summary
  - Display results:
    ```
    ✅ Preferences Import Complete

    Imported from: preferences_backup_2024-10-27.json

    Summary:
    • User settings: 3 updated
    • Directive preferences: 12 inserted, 5 updated
    • Tracking settings: 4 updated

    Conflicts resolved:
    • 2 kept existing values
    • 3 used imported values

    Your preferences have been updated.
    Next directive execution will use these settings.
    ```
  - Log to notes table:
    ```sql
    INSERT INTO notes (content, note_type, severity, source)
    VALUES (
      'Preferences imported from preferences_backup_2024-10-27.json',
      'preferences_import',
      'info',
      'user'
    )
    ```
- **Result**: User informed of successful import

**Fallback**: `prompt_user`
- **Details**: Import failed, provide guidance
  - Show error and suggestions:
    ```
    ❌ Import Failed

    Error: Invalid JSON format

    Suggestions:
    • Check file format matches export structure
    • Ensure JSON is valid (use JSON validator)
    • Try exporting preferences again
    • Provide example file path

    Expected format:
    {
      "version": "1.0",
      "user_settings": [...],
      "directive_preferences": [...]
    }
    ```
- **Result**: User guided to fix issue

---

## Examples

### ✅ Compliant Usage

**Importing Preferences (No Conflicts):**
```python
# User: "Import preferences from backup"
# AI calls: user_preferences_import(file_path=".aifp/backups/prefs_2024-10-27.json")

# Workflow:
# 1. read_import_file:
#    - Load .aifp/backups/prefs_2024-10-27.json
#    - Parse JSON successfully
#
# 2. validate_schema:
#    - version: "1.0" ✓
#    - user_settings: 3 entries ✓
#    - directive_preferences: 12 entries ✓
#    - All fields valid ✓
#
# 3. conflicts_detected: Check for conflicts
#    - Compare with existing preferences
#    - No conflicts found (empty database or disjoint preferences)
#
# 4. import_preferences:
#    BEGIN TRANSACTION
#    - INSERT 3 user_settings
#    - INSERT 12 directive_preferences
#    - UPDATE 4 tracking_settings
#    COMMIT
#
# 5. confirm_with_user:
#    """
#    ✅ Preferences Import Complete
#
#    Summary:
#    • User settings: 3 imported
#    • Directive preferences: 12 imported
#    • Tracking settings: 4 updated
#
#    No conflicts detected.
#    """
#
# Result:
# ✅ All preferences imported
# ✅ Next directive execution uses new settings
```

---

**Importing with Conflicts (Manual Resolution):**
```python
# User: "Import preferences from team_settings.json"
# File contains preferences that conflict with user's existing preferences

# Workflow:
# 1. read_import_file: ✓ Valid JSON
# 2. validate_schema: ✓ Version 1.0
#
# 3. conflicts_detected: 3 conflicts found
#    Prompt:
#    """
#    Conflicts Detected
#
#    1. project_file_write.always_add_docstrings
#       Existing: true (your preference)
#       Imported: false (team standard)
#
#    2. project_file_write.max_function_length
#       Existing: 50
#       Imported: 100
#
#    Resolve conflicts:
#    1. Keep existing (ignore team settings for conflicts)
#    2. Use imported (adopt team standards)
#    3. Merge (decide for each conflict)
#
#    Your choice: _
#    """
#
# 4. User inputs: 3 (merge)
#
# 5. For each conflict:
#    Conflict 1: always_add_docstrings
#      → User chooses: Keep existing (true)
#
#    Conflict 2: max_function_length
#      → User chooses: Use imported (100)
#
#    Conflict 3: indent_style
#      → User chooses: Use imported (spaces_2)
#
# 6. import_preferences:
#    - Import non-conflicting preferences (9 of 12)
#    - For conflicts: Apply user's resolution choices
#
# 7. confirm_with_user:
#    """
#    ✅ Import Complete
#
#    Summary:
#    • 12 directive preferences processed
#    • 9 imported without conflicts
#    • 3 conflicts resolved by user
#
#    Resolution:
#    • always_add_docstrings: Kept existing (true)
#    • max_function_length: Used imported (100)
#    • indent_style: Used imported (spaces_2)
#    """
#
# Result:
# ✅ Preferences merged intelligently
# ✅ User maintained control over conflicts
```

---

## Edge Cases

### Edge Case 1: Version Mismatch

**Issue**: Import file has different version than current

**Handling**:
```python
if import_version < current_version:
    # Older format
    prompt_user("""
    Older format detected: v{import_version}
    Current version: v{current_version}

    Attempt automatic migration? (y/n)
    """)
    if user_confirms:
        migrated_data = migrate_preferences(import_data, import_version, current_version)
        proceed_with_import(migrated_data)
```

### Edge Case 2: Invalid JSON

**Issue**: File is not valid JSON

**Handling**:
```python
try:
    data = json.loads(file_content)
except json.JSONDecodeError as e:
    return prompt_user(f"""
    Invalid JSON format

    Error: {e}

    Please check file format and try again.
    """)
```

### Edge Case 3: Partial Import Failure

**Issue**: Some preferences fail to import

**Handling**:
```python
# Transaction ensures all-or-nothing
try:
    conn.execute("BEGIN TRANSACTION")
    import_all_preferences(...)
    conn.execute("COMMIT")
except Exception as e:
    conn.execute("ROLLBACK")
    prompt_user(f"Import failed: {e}. No changes made.")
```

---

## Related Directives

- **Complements**: `user_preferences_export` - Creates files this directive imports
- **Modifies**: `directive_preferences`, `user_settings`, `tracking_settings` tables
- **Used By**: Users for backup restoration and preference sharing

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`user_settings`**: INSERT or UPDATE global settings
- **`directive_preferences`**: INSERT or UPDATE per-directive preferences
- **`tracking_settings`**: UPDATE tracking feature flags
- **`notes`**: INSERT import log entry

---

## Testing

1. **Import valid file** → Preferences updated
2. **Handle conflicts** → User prompted for resolution
3. **Reject invalid file** → Error message shown
4. **Transaction rollback** → No partial imports on error

---

## Common Mistakes

- ❌ **Not using transactions** - Partial imports leave inconsistent state
- ❌ **Not detecting conflicts** - Silently overwriting user preferences
- ❌ **Not validating schema** - Importing malformed data
- ❌ **Not logging import** - No audit trail

---

## References

None
---

*Part of AIFP v1.0 - User customization directive for importing preferences*

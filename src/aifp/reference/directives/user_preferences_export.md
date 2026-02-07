# Directive: user_preferences_export

**Type**: Project
**Level**: 2
**Parent Directive**: user_preferences_sync
**Priority**: LOW - Utility feature

---

## Purpose

The `user_preferences_export` directive **exports user preferences** to a portable JSON format for backup, sharing, or version control. This directive reads settings from `user_preferences.db` and creates a structured JSON file that can be imported into other projects or restored after database reset.

This directive is **useful for**:
- **Backup creation**: Save preferences before major changes or resets
- **Cross-project sharing**: Copy preferences to multiple projects
- **Version control**: Store preferences in Git alongside code
- **Team distribution**: Share standardized settings with team members
- **Machine migration**: Transfer settings to new development environment

The export workflow:
1. **Query preferences** - Read from user_preferences.db tables
2. **Format as JSON** - Structure data for export
3. **Optionally include tracking** - Add tracking data if user requests
4. **Save file** - Write JSON to specified path
5. **Confirm completion** - Show export summary

**Export Format**:
```json
{
  "version": "1.0",
  "exported_at": "2024-10-27T14:30:00Z",
  "project_name": "My AIFP Project",
  "user_settings": [
    {
      "key": "project_continue_on_start",
      "value": "true",
      "description": "Automatically continue project work on session start"
    },
    {
      "key": "suppress_warnings",
      "value": "[]",
      "description": "Directives to suppress warnings"
    }
  ],
  "directive_preferences": [
    {
      "directive": "project_file_write",
      "key": "always_add_docstrings",
      "value": "true",
      "description": "Always add docstrings to functions"
    }
  ],
  "tracking_settings": [
    {
      "feature": "ai_interaction_log",
      "enabled": false,
      "description": "Log all AI interactions"
    }
  ]
}
```

---

## When to Apply

This directive applies when:
- **User requests export** - "Export preferences", "Backup settings", "Save preferences"
- **Before database reset** - Backup before reinitializing
- **Project setup complete** - Save finalized preferences
- **Team sharing** - Create file for team members
- **Version control** - Commit preferences to Git

---

## Workflow

### Trunk: query_preferences

Queries all preferences from user_preferences.db.

**Steps**:
1. **Check database exists** - Does user_preferences.db exist?
2. **Query user_settings** - Read global preferences
3. **Query directive_preferences** - Read per-directive customizations
4. **Route to export** - Format and save

### Branches

**Branch 1: If preferences_exist**
- **Then**: `export_to_json`
- **Details**: Format preferences as JSON structure
  - Query user_settings:
    **Use helper functions** for all user_preferences.db operations. Query available helpers for settings operations.
  - Query directive_preferences:
    **Use helper functions** for all user_preferences.db operations. Query available helpers for settings operations.
  - Query tracking_settings:
    **Use helper functions** for all user_preferences.db operations. Query available helpers for settings operations.
  - Build JSON structure:
    ```python
    export_data = {
      "version": "1.0",
      "exported_at": datetime.now().isoformat(),
      "project_name": get_project_name(),
      "user_settings": [
        {"key": row[0], "value": row[1], "description": row[2]}
        for row in user_settings_results
      ],
      "directive_preferences": [
        {"directive": row[0], "key": row[1], "value": row[2], "description": row[3]}
        for row in directive_prefs_results
      ],
      "tracking_settings": [
        {"feature": row[0], "enabled": bool(row[1]), "description": row[2]}
        for row in tracking_results
      ]
    }
    ```
- **Result**: JSON data structure ready

**Branch 2: If include_tracking_requested**
- **Then**: `add_tracking_data`
- **Details**: Optionally include tracking logs (large data)
  - User can request: "Export preferences with tracking data"
  - Warning: This can create large files (tracking logs can be MB+)
  - Query ai_interaction_log:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
  - Query fp_flow_tracking:
    **Use helper functions** for database operations. Query available helpers for the appropriate database.
  - Add to export_data:
    ```python
    export_data["tracking_data"] = {
      "ai_interactions": [...],
      "fp_flow_tracking": [...]
    }
    ```
  - Show warning: "Tracking data included (file may be large)"
- **Result**: Tracking data added to export

**Branch 3: If export_complete**
- **Then**: `save_file`
- **Details**: Write JSON to file
  - Determine file path:
    - User-specified: Use provided path
    - Default: `.aifp/backups/preferences_export_YYYY-MM-DD.json`
  - Ensure directory exists:
    ```python
    os.makedirs(".aifp/backups", exist_ok=True)
    ```
  - Write JSON with pretty formatting:
    ```python
    with open(file_path, 'w', encoding='utf-8') as f:
      json.dump(export_data, f, indent=2, ensure_ascii=False)
    ```
  - Set file permissions (readable by user only):
    ```python
    os.chmod(file_path, 0o600)  # rw-------
    ```
- **Result**: File saved

**Branch 4: If file_saved**
- **Then**: `confirm_with_user`
- **Details**: Show export summary
  - Display results:
    ```
    ✅ Preferences Exported

    File: .aifp/backups/preferences_export_2024-10-27.json

    Exported:
    • User settings: 3
    • Directive preferences: 12
    • Tracking settings: 4

    File size: 2.4 KB

    This file can be:
    • Imported into other AIFP projects
    • Committed to version control
    • Shared with team members
    • Used to restore preferences after reset

    Import with: "Import preferences from <file>"
    ```
  - Log to notes table:
    **Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).
- **Result**: User informed of successful export

**Fallback**: `prompt_user`
- **Details**: No preferences to export or error occurred
  - If database empty:
    ```
    No preferences to export

    Your user_preferences.db is empty or uses default values only.

    Would you like to:
    1. Create default preferences and export
    2. Customize preferences first
    3. Cancel
    ```
  - If error occurred:
    ```
    ❌ Export Failed

    Error: {error_message}

    Suggestions:
    • Check file permissions
    • Ensure disk space available
    • Try different export path
    ```
- **Result**: User guided to next action

---

## Examples

### ✅ Compliant Usage

**Standard Export:**
```python
# User: "Export my preferences"
# AI calls: user_preferences_export()

# Workflow:
# 1. query_preferences:
#    - Query user_settings → 3 rows
#    - Query directive_preferences → 12 rows
#    - Query tracking_settings → 4 rows
#
# 2. export_to_json:
#    export_data = {
#      "version": "1.0",
#      "exported_at": "2024-10-27T14:30:00Z",
#      "user_settings": [
#        {"key": "project_continue_on_start", "value": "false", "description": "..."},
#        {"key": "suppress_warnings", "value": "[]", "description": "..."}
#      ],
#      "directive_preferences": [
#        {"directive": "project_file_write", "key": "always_add_docstrings", ...},
#        {"directive": "project_file_write", "key": "max_function_length", ...},
#        ... (10 more)
#      ],
#      "tracking_settings": [
#        {"feature": "ai_interaction_log", "enabled": false, ...},
#        ... (3 more)
#      ]
#    }
#
# 3. save_file:
#    - Create .aifp/backups/ if needed
#    - Write to preferences_export_2024-10-27.json
#    - Set permissions: 0o600
#
# 4. confirm_with_user:
#    """
#    ✅ Preferences Exported
#
#    File: .aifp/backups/preferences_export_2024-10-27.json
#
#    Exported:
#    • User settings: 3
#    • Directive preferences: 12
#    • Tracking settings: 4
#
#    File size: 2.4 KB
#    """
#
# Result:
# ✅ Preferences backed up
# ✅ Can be imported later or in other projects
```

---

**Export with Tracking Data:**
```python
# User: "Export preferences including tracking data"
# AI calls: user_preferences_export(include_tracking=True)

# Workflow:
# 1. query_preferences: (same as above)
#
# 2. include_tracking_requested:
#    Warning: "Tracking data will significantly increase file size"
#    - Query ai_interaction_log (last 100)
#    - Query fp_flow_tracking (last 100)
#    - Add to export_data["tracking_data"]
#
# 3. save_file:
#    - File size: 45 KB (larger due to tracking)
#
# 4. confirm_with_user:
#    """
#    ✅ Preferences Exported (with tracking data)
#
#    File: .aifp/backups/preferences_full_export_2024-10-27.json
#
#    Exported:
#    • User settings: 3
#    • Directive preferences: 12
#    • Tracking settings: 4
#    • AI interactions: 100 (last 100)
#    • FP flow tracking: 100 (last 100)
#
#    File size: 45 KB
#    ⚠️  Contains tracking logs (may include sensitive data)
#    """
#
# Result:
# ✅ Full preferences and tracking history exported
```

---

**Export to Custom Path:**
```python
# User: "Export preferences to ~/my-aifp-settings.json"
# AI calls: user_preferences_export(path="~/my-aifp-settings.json")

# Workflow:
# 1-2. (same query and format)
#
# 3. save_file:
#    - Expand path: ~/my-aifp-settings.json → /home/user/my-aifp-settings.json
#    - Write JSON to specified path
#
# 4. confirm_with_user:
#    """
#    ✅ Preferences Exported
#
#    File: /home/user/my-aifp-settings.json
#
#    You can now:
#    • Share this file with teammates
#    • Commit to Git: git add my-aifp-settings.json
#    • Import in other projects
#    """
#
# Result:
# ✅ Exported to user-specified location
```

---

## Edge Cases

### Edge Case 1: No Preferences to Export

**Issue**: Database is empty or only has defaults

**Handling**:
```python
if not user_settings and not directive_preferences:
    return prompt_user("""
    No custom preferences to export

    Your database only contains default settings.

    Would you like to:
    1. Export defaults anyway
    2. Customize preferences first
    3. Cancel
    """)
```

### Edge Case 2: Export Path Invalid

**Issue**: User-specified path is not writable

**Handling**:
```python
try:
    with open(export_path, 'w') as f:
        json.dump(export_data, f)
except PermissionError:
    return prompt_user("""
    Cannot write to specified path (permission denied)

    Try:
    • Use default path (.aifp/backups/)
    • Specify writable directory
    """)
```

### Edge Case 3: Sensitive Data in Tracking Logs

**Issue**: Tracking logs may contain sensitive information

**Handling**:
```python
if include_tracking:
    prompt_user("""
    ⚠️  Warning: Tracking Data May Contain Sensitive Information

    AI interaction logs may include:
    • Code snippets
    • Error messages
    • File paths
    • User corrections

    Only share this file with trusted recipients.

    Continue with export? (y/n):
    """)
```

---

## Related Directives

- **Complements**: `user_preferences_import` - Imports files created by this directive
- **Reads From**: `user_settings`, `directive_preferences`, `tracking_settings` tables
- **Used For**: Backup, sharing, version control

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive reads the following tables:

- **`user_settings`**: Read global preferences
- **`directive_preferences`**: Read per-directive customizations
- **`tracking_settings`**: Read tracking feature flags
- **`ai_interaction_log`**: Read tracking data (if requested)
- **`fp_flow_tracking`**: Read compliance tracking (if requested)
- **`notes`**: INSERT export log entry

---

## Testing

1. **Export preferences** → JSON file created
2. **Include tracking** → Larger file with logs
3. **Custom path** → File saved to specified location
4. **Empty database** → Prompt for action

---

## Common Mistakes

- ❌ **Not pretty-printing JSON** - Hard to read/edit
- ❌ **Not setting file permissions** - Preferences may contain sensitive data
- ❌ **Including all tracking data** - Files can be huge (MB+)
- ❌ **Not logging export** - No audit trail

---

## References

None
---

*Part of AIFP v1.0 - User customization directive for exporting preferences*

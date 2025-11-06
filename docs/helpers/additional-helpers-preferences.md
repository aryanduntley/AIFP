# Additional Preferences Database Helpers (user_preferences.db)

**Purpose**: Getters and setters for user-specific AI behavior customizations, preferences, and opt-in tracking features.

**Philosophy**: Enable AI to check user preferences efficiently before directive execution, and provide tools for preference management without SQL construction.

**Database**: `user_preferences.db` (per-project, mutable, located in `.aifp-project/`)

**Status**: 🔵 Proposed (Not Yet Implemented)

**MCP Tool Classification**: See [helper-tool-classification.md](./helper-tool-classification.md) for which helpers are exposed as MCP tools (`is_tool: true`) vs internal helpers (`is_tool: false`)

---

## Table of Contents

1. [User Settings Getters/Setters](#user-settings-getterssetters)
2. [Directive Preferences Getters/Setters](#directive-preferences-getterssetters)
3. [Tracking Settings Tools](#tracking-settings-tools)
4. [AI Interaction Log Tools](#ai-interaction-log-tools)
5. [FP Flow Tracking Tools](#fp-flow-tracking-tools)
6. [Issue Reports Tools](#issue-reports-tools)
7. [Cross-Database Integration](#cross-database-integration)

---

## User Settings Getters/Setters

**Purpose**: Project-wide AI behavior configurations

**Table**: `user_settings` - atomic key-value pairs with scope

### Getters

#### `get_user_setting(setting_key: str)`
**Purpose**: Get specific user setting value.

**Parameters**:
- `setting_key` (str): Setting identifier (e.g., "fp_strictness_level")

**Returns**:
```json
{
  "setting_key": "fp_strictness_level",
  "setting_value": "{\"level\": \"standard\", \"exceptions\": []}",
  "description": "How strict to enforce FP directives",
  "scope": "project"
}
```

**Error Handling**: Return `{"found": false}` if setting doesn't exist

**Use Case**: Check AI behavior settings before directive execution

---

#### `get_all_user_settings()`
**Purpose**: Get all user settings for project.

**Returns**: List of all setting objects

**Use Case**: Session initialization, status reporting, export

---

#### `get_user_settings_by_scope(scope: str)`
**Purpose**: Get settings filtered by scope.

**Parameters**:
- `scope` (str): "project" or "global" (future)

**Returns**: List of setting objects

**Note**: Currently all settings are "project" scope

---

### Setters

#### `set_user_setting(setting_key: str, setting_value: str, description: str = None)`
**Purpose**: Create or update user setting.

**Parameters**:
- `setting_key` (str): Setting identifier
- `setting_value` (str): Value (can be JSON string)
- `description` (str, optional): Human-readable description

**Returns**:
```json
{
  "success": true,
  "action": "created",  // or "updated"
  "setting_key": "prefer_explicit_returns",
  "previous_value": "false"  // if updated
}
```

**Use Case**: User updates AI behavior via `user_preferences_update` directive

---

#### `delete_user_setting(setting_key: str)`
**Purpose**: Remove user setting (revert to default).

**Returns**:
```json
{
  "success": true,
  "deleted": "custom_preference",
  "default_restored": false  // true if there's a default value
}
```

---

## Directive Preferences Getters/Setters

**Purpose**: Per-directive behavior customizations (atomic key-value)

**Table**: `directive_preferences` - multiple preferences per directive

**Key Design**: UNIQUE(directive_name, preference_key) enables atomic preferences

### Getters

#### `get_directive_preference(directive_name: str, preference_key: str)`
**Purpose**: Get specific preference for directive.

**Parameters**:
- `directive_name` (str): Directive name
- `preference_key` (str): Preference identifier

**Returns**:
```json
{
  "directive_name": "project_file_write",
  "preference_key": "always_add_docstrings",
  "preference_value": "true",
  "active": true,
  "description": "Always add docstrings to functions"
}
```

**Error Handling**: Return `{"found": false}` if preference doesn't exist

**Use Case**: Load directive customization before workflow execution

**Note**: This helper already exists in helpers_parsed.json (preferences.py)

---

#### `get_all_directive_preferences(directive_name: str)`
**Purpose**: Get all preferences for specific directive.

**Parameters**:
- `directive_name` (str): Directive name

**Returns**:
```json
{
  "directive": "project_file_write",
  "preferences": [
    {
      "preference_key": "always_add_docstrings",
      "preference_value": "true",
      "active": true
    },
    {
      "preference_key": "max_function_length",
      "preference_value": "50",
      "active": true
    }
  ],
  "preference_count": 2
}
```

**Use Case**: `user_preferences_sync` loads all preferences for directive

---

#### `get_active_directive_preferences(directive_name: str)`
**Purpose**: Get only active preferences (active = 1).

**Returns**: Same as `get_all_directive_preferences()` but filtered

**Use Case**: Workflow execution (skip disabled preferences)

---

#### `list_directives_with_preferences()`
**Purpose**: Get list of all directives that have customizations.

**Returns**:
```json
{
  "directives": [
    {"directive_name": "project_file_write", "preference_count": 3},
    {"directive_name": "project_compliance_check", "preference_count": 1}
  ],
  "total_directives": 2,
  "total_preferences": 4
}
```

**Use Case**: Status reporting, preference management UI

---

### Setters

#### `set_directive_preference(directive_name: str, preference_key: str, preference_value: str, description: str = None)`
**Purpose**: Create or update directive preference.

**Parameters**:
- `directive_name` (str): Directive to customize
- `preference_key` (str): Preference identifier
- `preference_value` (str): Value
- `description` (str, optional): What this preference does

**Returns**:
```json
{
  "success": true,
  "action": "created",  // or "updated"
  "directive_name": "project_file_write",
  "preference_key": "always_add_docstrings",
  "previous_value": "false"  // if updated
}
```

**Use Case**: User customizes directive behavior via `user_preferences_update`

**Note**: This helper already exists in helpers_parsed.json (preferences.py)

---

#### `toggle_directive_preference(directive_name: str, preference_key: str)`
**Purpose**: Toggle preference active status (enable/disable without deleting).

**Returns**:
```json
{
  "success": true,
  "directive_name": "project_file_write",
  "preference_key": "always_add_docstrings",
  "active": false,  // new state
  "previous_active": true
}
```

**Use Case**: Temporarily disable preference without losing value

---

#### `delete_directive_preference(directive_name: str, preference_key: str)`
**Purpose**: Remove directive preference entirely.

**Returns**:
```json
{
  "success": true,
  "deleted": {
    "directive_name": "project_file_write",
    "preference_key": "always_add_docstrings"
  }
}
```

---

## Tracking Settings Tools

**Purpose**: Control opt-in tracking features with token overhead transparency

**Table**: `tracking_settings` - feature flags

**Features**:
- `fp_flow_tracking` (~5% token increase per file write)
- `ai_interaction_log` (~3% token increase overall)
- `issue_reports` (~2% token increase on errors)
- `helper_function_logging` (~1% token increase on errors)

### Getters

#### `get_tracking_setting(feature_name: str)`
**Purpose**: Check if specific tracking feature is enabled.

**Parameters**:
- `feature_name` (str): "fp_flow_tracking", "issue_reports", "ai_interaction_log", "helper_function_logging"

**Returns**:
```json
{
  "feature_name": "helper_function_logging",
  "enabled": false,
  "description": "Log helper function errors and execution details",
  "estimated_token_overhead": "~1% token increase on errors"
}
```

**Error Handling**: Return `{"found": false}` if feature doesn't exist

**Use Case**: Check before logging in helper error handling

---

#### `is_feature_enabled(feature_name: str)`
**Purpose**: Quick boolean check for feature status.

**Parameters**:
- `feature_name` (str): Feature to check

**Returns**: Boolean (true/false) or `{"found": false}`

**Use Case**: Fast conditional checks (e.g., `if is_feature_enabled("helper_function_logging")`)

---

#### `is_helper_logging_enabled()`
**Purpose**: Convenience shortcut for `helper_function_logging` check.

**Returns**: Boolean (true/false)

**Use Case**: Helper error handling cross-database dependency

**Example**:
```python
if is_helper_logging_enabled():
    log_to_db(error_details)
else:
    print_error_only(error_details)
```

---

#### `get_all_tracking_settings()`
**Purpose**: Get status of all tracking features.

**Returns**:
```json
{
  "features": [
    {
      "feature_name": "fp_flow_tracking",
      "enabled": false,
      "estimated_token_overhead": "~5% increase per file write"
    },
    {
      "feature_name": "helper_function_logging",
      "enabled": false,
      "estimated_token_overhead": "~1% increase on errors"
    }
  ],
  "enabled_count": 0,
  "total_features": 4
}
```

**Use Case**: Status reporting, settings UI

**Note**: This helper already exists in helpers_parsed.json (preferences.py)

---

### Setters

#### `toggle_tracking_feature(feature_name: str, enabled: bool)`
**Purpose**: Enable or disable tracking feature (with token overhead warning).

**Parameters**:
- `feature_name` (str): Feature to toggle
- `enabled` (bool): true = enable, false = disable

**Returns**:
```json
{
  "success": true,
  "feature_name": "helper_function_logging",
  "enabled": true,
  "previous_enabled": false,
  "token_overhead": "~1% increase on errors",
  "warning_shown": true
}
```

**Behavior**: Shows user token overhead estimate before enabling

**Use Case**: `tracking_toggle` directive

**Note**: This helper already exists in helpers_parsed.json (preferences.py)

---

## AI Interaction Log Tools

**Purpose**: Track user corrections to learn preferences (disabled by default)

**Table**: `ai_interaction_log` - logs interactions for pattern detection

**Enabled via**: `tracking_toggle` directive setting `ai_interaction_log = true`

### Getters

#### `get_recent_interactions(limit: int = 50)`
**Purpose**: Get recent AI interactions for context.

**Parameters**:
- `limit` (int): Number of recent entries to retrieve

**Returns**:
```json
{
  "interactions": [
    {
      "id": 123,
      "interaction_type": "correction",
      "directive_context": "project_file_write",
      "user_feedback": "Use guard clauses instead of nested if",
      "ai_interpretation": "User prefers guard clauses",
      "applied_to_preferences": true,
      "created_at": "2025-11-02T10:15:00"
    }
  ],
  "count": 50
}
```

**Use Case**: `user_preferences_learn` directive, pattern detection

---

#### `get_interactions_by_directive(directive_name: str, limit: int = 20)`
**Purpose**: Get interactions related to specific directive.

**Returns**: Same as `get_recent_interactions()` but filtered

**Use Case**: Understanding user corrections for specific directive

---

#### `get_unapplied_corrections()`
**Purpose**: Get corrections that haven't been converted to preferences yet.

**Returns**: Interactions where `applied_to_preferences = false`

**Use Case**: `user_preferences_learn` finds patterns to convert to rules

---

### Setters

#### `log_interaction(interaction_type: str, directive_context: str, user_feedback: str, ai_interpretation: str)`
**Purpose**: Log AI interaction for learning.

**Parameters**:
- `interaction_type` (str): "correction", "clarification", "preference_learned"
- `directive_context` (str): Directive being executed
- `user_feedback` (str): What user said
- `ai_interpretation` (str): How AI interpreted it

**Returns**:
```json
{
  "success": true,
  "interaction_id": 124,
  "applied_to_preferences": false
}
```

**Precondition**: Check `is_feature_enabled("ai_interaction_log")` first

---

#### `mark_interaction_applied(interaction_id: int)`
**Purpose**: Mark interaction as converted to preference.

**Returns**: `{"success": true}`

**Use Case**: After `user_preferences_learn` creates preference from pattern

---

## FP Flow Tracking Tools

**Purpose**: Track FP directive compliance history (disabled by default)

**Table**: `fp_flow_tracking` - logs FP checks per function

**Enabled via**: `tracking_toggle` directive setting `fp_flow_tracking = true`

### Getters

#### `get_fp_compliance_history(file_path: str = None, limit: int = 50)`
**Purpose**: Get FP compliance tracking history.

**Parameters**:
- `file_path` (str, optional): Filter by file
- `limit` (int): Number of entries to retrieve

**Returns**:
```json
{
  "tracking_entries": [
    {
      "id": 1,
      "function_name": "calculate_discount",
      "file_path": "src/pricing.py",
      "fp_directives_applied": ["fp_purity", "fp_immutability"],
      "compliance_score": 0.67,
      "issues": [
        {"directive": "fp_purity", "issue": "Global state access", "severity": "warning"}
      ],
      "user_overrides": null,
      "created_at": "2025-11-02T10:00:00"
    }
  ],
  "count": 50,
  "average_score": 0.85
}
```

**Use Case**: Analyze compliance trends, identify recurring violations

---

#### `get_compliance_trends(days: int = 7)`
**Purpose**: Get compliance score trends over time.

**Returns**:
```json
{
  "period": "7 days",
  "daily_averages": [
    {"date": "2025-11-02", "avg_score": 0.92, "check_count": 15},
    {"date": "2025-11-01", "avg_score": 0.88, "check_count": 12}
  ],
  "overall_trend": "improving",  // "improving", "declining", "stable"
  "most_common_violations": [
    {"directive": "fp_purity", "count": 5},
    {"directive": "fp_immutability", "count": 3}
  ]
}
```

**Use Case**: Project metrics, identify areas needing attention

---

### Setters

#### `log_fp_check(function_name: str, file_path: str, fp_directives_applied: list, compliance_score: float, issues: list = None)`
**Purpose**: Log FP compliance check result.

**Parameters**:
- `function_name` (str): Function checked
- `file_path` (str): File location
- `fp_directives_applied` (list): Directive names applied
- `compliance_score` (float): 0.0-1.0 score
- `issues` (list, optional): Compliance issues found

**Returns**: `{"success": true, "tracking_id": 123}`

**Precondition**: Check `is_feature_enabled("fp_flow_tracking")` first

---

## Issue Reports Tools

**Purpose**: Compile contextual bug reports with full logs (disabled by default)

**Table**: `issue_reports` - draft, submit, track issues

**Enabled via**: `tracking_toggle` directive setting `issue_reports = true`

### Getters

#### `get_issue_report(report_id: int)`
**Purpose**: Get specific issue report details.

**Returns**:
```json
{
  "id": 1,
  "report_type": "directive_issue",
  "title": "fp_purity fails to detect list.append mutation",
  "description": "...",
  "directive_name": "fp_purity",
  "context_log_ids": [123, 124, 125],
  "status": "draft",
  "created_at": "2025-11-02T10:00:00"
}
```

---

#### `list_issue_reports(status: str = None)`
**Purpose**: List issue reports, optionally filtered by status.

**Parameters**:
- `status` (str, optional): "draft", "submitted", "resolved"

**Returns**: List of issue report objects

---

### Setters

#### `create_issue_report(report_type: str, title: str, description: str, directive_name: str = None, context_log_ids: list = None)`
**Purpose**: Create new issue report.

**Returns**: `{"success": true, "report_id": 1}`

---

#### `update_issue_status(report_id: int, status: str)`
**Purpose**: Update issue report status.

**Parameters**:
- `status` (str): "draft", "submitted", "resolved"

**Returns**: `{"success": true}`

---

## Cross-Database Integration

**Purpose**: Helpers that bridge multiple databases for workflow execution

### User Preferences Sync

#### `load_preferences_for_directive(directive_name: str)`
**Purpose**: Load all preferences for directive in single call.

**Returns**:
```json
{
  "directive": "project_file_write",
  "user_settings": {
    "fp_strictness_level": {"level": "standard"}
  },
  "directive_preferences": {
    "always_add_docstrings": true,
    "max_function_length": 50
  },
  "tracking_enabled": {
    "fp_flow_tracking": false,
    "helper_function_logging": false
  }
}
```

**Use Case**: `user_preferences_sync` loads all context before directive execution

**Efficiency**: Single helper call instead of 3+ separate queries

---

#### `export_all_preferences()`
**Purpose**: Export all preferences for backup/sharing.

**Returns**:
```json
{
  "export_date": "2025-11-02T10:00:00",
  "user_settings": [...],
  "directive_preferences": [...],
  "tracking_settings": [...]
}
```

**Use Case**: `user_preferences_export` directive

---

#### `import_preferences(preferences_json: str)`
**Purpose**: Import preferences from JSON export.

**Returns**:
```json
{
  "success": true,
  "imported": {
    "user_settings": 5,
    "directive_preferences": 12,
    "tracking_settings": 4
  },
  "conflicts": []  // If any existing preferences conflict
}
```

**Use Case**: `user_preferences_import` directive

---

## Implementation Notes

### Module Organization

**Directory Structure**:
```
src/aifp/helpers/preferences/
├── tools/                          # is_tool=true (MCP-exposed)
│   ├── user_settings_tools.py      # ~6 functions
│   ├── directive_prefs_tools.py    # ~10 functions
│   ├── tracking_tools.py           # ~8 functions
│   ├── interaction_log_tools.py    # ~5 functions
│   ├── fp_tracking_tools.py        # ~3 functions
│   ├── issue_reports_tools.py      # ~4 functions
│   └── cross_db_tools.py           # ~3 functions
└── internal.py                     # is_tool=false (internal helpers)
```

**Current Preferences Helpers**: 4 functions (in preferences.py)
**Proposed Preferences Tools**: ~39 functions (from this document)
**Total Preferences Tools After Additions**: ~43 tools

**Breakdown**:
- User Settings: 6 functions (3 getters + 3 setters)
- Directive Preferences: 10 functions (4 getters + 6 setters)
- Tracking Settings: 8 functions (4 getters + 2 setters + 2 convenience)
- AI Interaction Log: 5 functions (3 getters + 2 setters)
- FP Flow Tracking: 3 functions (2 getters + 1 setter)
- Issue Reports: 4 functions (2 getters + 2 setters)
- Cross-Database: 3 functions (integration helpers)

### Naming Conventions

- **User Settings**: `get_user_setting()`, `set_user_setting()`
- **Directive Preferences**: `get_directive_preference()`, `set_directive_preference()`
- **Tracking Features**: `is_feature_enabled()`, `toggle_tracking_feature()`
- **Convenience Shortcuts**: `is_helper_logging_enabled()` (specific feature checks)
- **Batch Operations**: `load_preferences_for_directive()`, `export_all_preferences()`

### Return Types

All functions return:
- **Single entity**: Object dict or `{"found": false}`
- **Multiple entities**: List of dicts (empty list if none)
- **Setters**: `{"success": true/false, ...details}`
- **Boolean checks**: true/false or `{"found": false}`

### Error Handling

- Never raise exceptions
- Return empty structures or `{"found": false}`
- Log warnings for invalid parameters
- Precondition checks for tracking features (check `is_feature_enabled()` first)

### Cost Management

**Token Overhead Transparency**:
- Always show token cost before enabling tracking
- Return `estimated_token_overhead` in getter responses
- Warn users when enabling expensive features (>3%)

**Default-Disabled Philosophy**:
- All tracking features disabled by default
- Users opt-in explicitly via `tracking_toggle` directive
- Project work remains cost-efficient

---

## Priority Implementation Order

### Phase 1: Critical (Needed for MCP Tools Error Handling)
**Resolve Cross-Database Dependency**
1. `is_helper_logging_enabled()` - Quick check for helper error handling
2. `is_feature_enabled(feature_name)` - Generic feature flag check
3. `get_tracking_setting(feature_name)` - Get feature details

### Phase 2: Important (Core Preference Management)
**User Workflow Support**
4. `get_user_setting(setting_key)` - Load AI behavior settings
5. `get_all_directive_preferences(directive_name)` - Load directive customizations
6. `get_active_directive_preferences(directive_name)` - Filter for workflow execution
7. `load_preferences_for_directive(directive_name)` - Batch load (efficiency)
8. `set_user_setting()` - Update AI behavior
9. `set_directive_preference()` - Customize directives
10. `toggle_directive_preference()` - Enable/disable preferences

### Phase 3: Advanced (Tracking & Analytics)
**Opt-In Features**
11. `get_recent_interactions()` - AI learning context
12. `get_fp_compliance_history()` - FP tracking
13. `get_compliance_trends()` - Metrics analysis
14. `log_interaction()` - Learning from corrections
15. `log_fp_check()` - Compliance logging
16. All issue report tools
17. Export/import tools

---

## Existing Helpers (Already in helpers_parsed.json)

**Keep These** (already implemented):
1. ✅ `get_directive_preference()` - preferences.py (is_sub_helper=true)
2. ✅ `set_directive_preference()` - preferences.py (is_sub_helper=true)
3. ✅ `get_tracking_settings()` - preferences.py (returns all features)
4. ✅ `toggle_tracking_feature()` - preferences.py (with overhead warning)

**Update Required**:
- Change `is_sub_helper=true` to `is_tool=true` for preference tools
- These should be exposed as MCP tools for AI to call directly

---

## Discussion Questions

1. **Batch vs Single**: Should `load_preferences_for_directive()` be Phase 1 for efficiency?
2. **Caching**: Should AI cache preferences at session start or query each time?
3. **Atomic vs Nested**: Should directive_preferences support nested JSON values or keep atomic?
4. **Feature flag defaults**: Should any tracking features be enabled by default in development?
5. **Cross-DB queries**: Should we use ATTACH DATABASE for cross-DB queries or separate connections?
6. **Export format**: Should exports be JSON, YAML, or both?

---

## Integration with Other Databases

### With aifp_core.db (MCP Helpers)
- MCP helper error handling checks `is_helper_logging_enabled()`
- Before logging: `if is_helper_logging_enabled(): log_error()`

### With project.db (Project Helpers)
- Project directives load preferences via `load_preferences_for_directive()`
- FP compliance checks log via `log_fp_check()` if enabled

### With user_directives.db (User Directive Helpers)
- User directive execution may have separate preference system
- TBD: Should user directives have their own preferences table?

---

**Next Steps**:
1. Review and discuss this proposal
2. Create `additional-helpers-project.md` (project.db tools)
3. Create `additional-helpers-user-directives.md` (user_directives.db tools)
4. Implement Phase 1 preference tools (resolve cross-DB dependency)
5. Update existing preference helpers to `is_tool=true`
6. Re-run `sync-directives.py`

---

**Status**: 🔵 Proposed - Awaiting Review
**Created**: 2025-11-02
**Author**: AIFP Development Team

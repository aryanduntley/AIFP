# Directive: tracking_toggle

**Type**: Project
**Level**: 2
**Parent Directive**: user_preferences_sync
**Priority**: MEDIUM - Cost management feature

---

## Purpose

The `tracking_toggle` directive enables or disables **opt-in tracking features** in `user_preferences.db`, giving users granular control over which logging and analytics features are active. This directive is **critical for cost management** because tracking features increase API token usage by 1-5% per feature, and all features are **disabled by default** to keep AIFP cost-efficient.

This directive is **essential for informed consent** because:
- **Token cost transparency**: Shows estimated overhead before enabling
- **Granular control**: Each feature can be toggled independently
- **Privacy-conscious**: All tracking opt-in only
- **No confirmation for disabling**: Easy to turn off, harder to turn on
- **Cost management**: Users see impact on API usage

The available tracking features:
1. **fp_flow_tracking** (~5% token increase per file write)
   - Tracks FP directive compliance over time
   - Logs function purity, violations, user overrides

2. **issue_reports** (~2% token increase on errors)
   - Enables detailed bug report compilation
   - Links AI interactions to issues

3. **ai_interaction_log** (~3% token increase overall)
   - Logs all user corrections and clarifications
   - Enables user_preferences_learn directive

4. **helper_function_logging** (~1% token increase on errors)
   - Logs helper function errors and execution details
   - Aids debugging

**Design Philosophy**: Project work should be cost-efficient. Debugging and analytics are opt-in luxuries.

---

## When to Apply

This directive applies when:
- **User requests tracking** - "Enable logging", "Turn on tracking", "Track FP compliance"
- **User disables tracking** - "Disable tracking", "Turn off logging", "Stop tracking"
- **Cost concerns** - User wants to reduce API token usage
- **Debugging needed** - User wants detailed logs for issue reporting
- **Privacy concerns** - User wants to disable data collection

---

## Workflow

### Trunk: parse_tracking_request

Parses user's request to enable/disable tracking feature.

**Steps**:
1. **Identify feature** - Which tracking feature (fp_flow, ai_log, issue_reports, helper_log)?
2. **Determine action** - Enable or disable?
3. **Route to status check** - Query current state

### Branches

**Branch 1: If feature_identified**
- **Then**: `check_current_status`
- **Details**: Query current state of tracking feature
  - Query:
    ```sql
    SELECT enabled, description, estimated_token_overhead
    FROM tracking_settings
    WHERE feature_name = ?
    ```
  - Example results:
    ```python
    {
      "feature": "ai_interaction_log",
      "enabled": False,  # Currently disabled
      "description": "Log all AI interactions for learning",
      "token_overhead": "~3% token increase overall"
    }
    ```
  - Store current state
- **Result**: Current status retrieved

**Branch 2: If enabling_feature**
- **Then**: `show_token_overhead`
- **Details**: Warn user about token cost before enabling
  - Show warning:
    ```
    ⚠️  Enable Tracking Feature

    Feature: ai_interaction_log
    Description: Log all AI interactions for learning

    Estimated Token Overhead: ~3% token increase overall

    This will:
    • Log every AI response and user correction
    • Enable user_preferences_learn directive
    • Store data in ai_interaction_log table
    • Increase API costs by approximately 3%

    Cost Impact Example:
    • Current session: 10,000 tokens → With tracking: 10,300 tokens
    • Monthly (100k tokens): $X → With tracking: $X * 1.03

    Enable this feature? (y/n): _
    ```
  - Wait for explicit user confirmation
  - If user types anything other than "y" or "yes" → Cancel
- **Result**: User warned of cost impact

**Branch 3: If user_confirms**
- **Then**: `update_tracking_setting`
- **Details**: Enable the tracking feature
  - Update database:
    ```sql
    UPDATE tracking_settings
    SET enabled = 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE feature_name = ?
    ```
  - Example:
    ```sql
    UPDATE tracking_settings
    SET enabled = 1, updated_at = CURRENT_TIMESTAMP
    WHERE feature_name = 'ai_interaction_log'
    ```
  - Feature now active for this project
  - Next directive execution will use tracking
- **Result**: Feature enabled

**Branch 4: If disabling_feature**
- **Then**: `disable_immediately`
- **Details**: Disable without confirmation (user saving money)
  - No confirmation needed for disabling
  - Immediately update:
    ```sql
    UPDATE tracking_settings
    SET enabled = 0,
        updated_at = CURRENT_TIMESTAMP
    WHERE feature_name = ?
    ```
  - Existing logged data is preserved (not deleted)
  - Can be re-enabled later
- **Result**: Feature disabled

**Branch 5: If status_updated**
- **Then**: `confirm_with_user`
- **Details**: Show new status
  - For enabling:
    ```
    ✅ Tracking Feature Enabled

    Feature: ai_interaction_log
    Status: Enabled

    This feature is now active for this project.
    All future AI interactions will be logged.

    To disable later: "Disable ai_interaction_log" or "Turn off tracking"

    Current tracking features:
    • fp_flow_tracking: Disabled
    • issue_reports: Disabled
    • ai_interaction_log: Enabled ✓
    • helper_function_logging: Disabled

    Total estimated overhead: ~3%
    ```
  - For disabling:
    ```
    ✅ Tracking Feature Disabled

    Feature: ai_interaction_log
    Status: Disabled

    This feature is now inactive.
    Existing logged data has been preserved.

    To re-enable: "Enable ai_interaction_log"

    Total estimated overhead: 0% (all tracking disabled)
    ```
  - Show all tracking features and their status
  - Show cumulative overhead
- **Result**: User informed of new state

**Fallback**: `prompt_user`
- **Details**: Unable to determine which feature
  - Clarify what user wants:
    ```
    Which tracking feature?

    Available features:
    1. fp_flow_tracking
       • Track FP directive compliance over time
       • Token overhead: ~5% per file write
       • Currently: Disabled

    2. issue_reports
       • Enable detailed bug report compilation
       • Token overhead: ~2% on errors
       • Currently: Disabled

    3. ai_interaction_log
       • Log all AI interactions for learning
       • Token overhead: ~3% overall
       • Currently: Disabled

    4. helper_function_logging
       • Log helper function errors
       • Token overhead: ~1% on errors
       • Currently: Disabled

    Your choice (1-4) or feature name: _
    ```
  - Present all options with status
- **Result**: User clarifies which feature

---

## Examples

### ✅ Compliant Usage

**Enabling Tracking Feature:**
```python
# User: "Enable AI interaction logging"
# AI calls: tracking_toggle()

# Workflow:
# 1. parse_tracking_request:
#    - Intent: "enable AI interaction logging"
#    - Feature: "ai_interaction_log"
#    - Action: Enable
#
# 2. check_current_status:
#    SELECT enabled FROM tracking_settings
#    WHERE feature_name='ai_interaction_log'
#    → enabled = 0 (currently disabled)
#
# 3. enabling_feature: show_token_overhead
#    """
#    ⚠️  Enable Tracking Feature
#
#    Feature: ai_interaction_log
#
#    Estimated Token Overhead: ~3% token increase overall
#
#    This will increase API costs by approximately 3%.
#
#    Enable? (y/n): _
#    """
#
# 4. User inputs: y
#
# 5. update_tracking_setting:
#    UPDATE tracking_settings
#    SET enabled = 1, updated_at = CURRENT_TIMESTAMP
#    WHERE feature_name = 'ai_interaction_log'
#
# 6. confirm_with_user:
#    """
#    ✅ Tracking Feature Enabled
#
#    Feature: ai_interaction_log
#    Status: Enabled
#
#    All future AI interactions will be logged.
#
#    Current tracking features:
#    • fp_flow_tracking: Disabled
#    • issue_reports: Disabled
#    • ai_interaction_log: Enabled ✓
#    • helper_function_logging: Disabled
#
#    Total estimated overhead: ~3%
#    """
#
# Result:
# ✅ ai_interaction_log enabled
# ✅ User warned of cost impact
# ✅ user_preferences_learn can now detect patterns
```

---

**Disabling Tracking Feature:**
```python
# User: "Turn off tracking" (wants to save money)
# AI calls: tracking_toggle()

# Workflow:
# 1. parse_tracking_request:
#    - Intent: "turn off tracking"
#    - Feature: Not specified (could mean all or specific)
#    - Clarify: Which feature?
#
# 2. User clarifies: "ai_interaction_log"
#
# 3. check_current_status:
#    → enabled = 1 (currently enabled)
#
# 4. disabling_feature: disable_immediately
#    # No confirmation needed (user saving money)
#    UPDATE tracking_settings
#    SET enabled = 0
#    WHERE feature_name = 'ai_interaction_log'
#
# 5. confirm_with_user:
#    """
#    ✅ Tracking Feature Disabled
#
#    Feature: ai_interaction_log
#    Status: Disabled
#
#    Existing logged data preserved (not deleted).
#
#    Total estimated overhead: 0% (all tracking disabled)
#    """
#
# Result:
# ✅ Feature disabled (cost savings)
# ✅ No confirmation required
# ✅ Existing logs preserved
```

---

**Enabling Multiple Features:**
```python
# User: "Enable all tracking features for debugging"
# AI calls: tracking_toggle()

# Workflow:
# 1. parse_tracking_request:
#    - Intent: "enable all tracking"
#    - Features: All 4 features
#
# 2. show_token_overhead for ALL features:
#    """
#    ⚠️  Enable All Tracking Features
#
#    Features to enable:
#    • fp_flow_tracking: ~5% per file write
#    • issue_reports: ~2% on errors
#    • ai_interaction_log: ~3% overall
#    • helper_function_logging: ~1% on errors
#
#    Combined Estimated Overhead: ~11% token increase
#
#    Cost Impact:
#    • Current session: 10,000 tokens
#    • With all tracking: ~11,100 tokens
#
#    This significantly increases API costs.
#    Only enable for debugging/analysis.
#
#    Enable all features? (y/n): _
#    """
#
# 3. User inputs: y
#
# 4. update_tracking_setting (for each):
#    UPDATE tracking_settings SET enabled = 1
#    WHERE feature_name IN ('fp_flow_tracking', 'issue_reports', ...)
#
# 5. confirm_with_user:
#    """
#    ✅ All Tracking Features Enabled
#
#    Current tracking:
#    • fp_flow_tracking: Enabled ✓
#    • issue_reports: Enabled ✓
#    • ai_interaction_log: Enabled ✓
#    • helper_function_logging: Enabled ✓
#
#    Total estimated overhead: ~11%
#
#    Remember to disable when debugging complete!
#    """
#
# Result:
# ✅ All tracking enabled
# ✅ User warned about cumulative cost
# ✅ Reminded to disable later
```

---

### ❌ Non-Compliant Usage

**Enabling Without Warning:**
```python
# ❌ Enabling without showing token overhead
if user_says_enable:
    enable_tracking("ai_interaction_log")
# User not warned about cost!
```

**Why Non-Compliant**:
- User not informed of cost impact
- Violates transparency principle
- Could surprise user with higher API bills

**Corrected:**
```python
# ✅ Always warn before enabling
if user_says_enable:
    show_token_overhead("ai_interaction_log")
    if user_confirms_after_warning():
        enable_tracking("ai_interaction_log")
```

---

**Requiring Confirmation for Disabling:**
```python
# ❌ Asking confirmation to disable
if user_says_disable:
    if confirm("Are you sure?"):
        disable_tracking("ai_interaction_log")
# User trying to save money, don't make it hard!
```

**Why Non-Compliant**:
- Should make disabling easy (user saving money)
- Only enable needs confirmation (cost increase)

**Corrected:**
```python
# ✅ No confirmation for disabling
if user_says_disable:
    disable_tracking("ai_interaction_log")
    # Immediate, no friction
```

---

## Edge Cases

### Edge Case 1: Feature Already Enabled

**Issue**: User tries to enable already-enabled feature

**Handling**:
```python
if feature_already_enabled:
    return inform_user(f"""
    Feature '{feature_name}' is already enabled.

    To disable: "Disable {feature_name}"
    """)
```

**Directive Action**: Inform user, no action needed.

---

### Edge Case 2: Unknown Feature Name

**Issue**: User specifies feature that doesn't exist

**Handling**:
```python
valid_features = ["fp_flow_tracking", "issue_reports", "ai_interaction_log", "helper_function_logging"]

if feature_name not in valid_features:
    return prompt_user(f"""
    Unknown tracking feature: '{feature_name}'

    Available features:
    {list_features_with_status()}

    Which would you like to toggle?
    """)
```

**Directive Action**: Show valid options, ask user to clarify.

---

### Edge Case 3: Database Missing

**Issue**: user_preferences.db doesn't exist

**Handling**:
```python
if not database_exists("user_preferences.db"):
    # Initialize database first
    initialize_preferences_db()
    # Now tracking_settings table exists with defaults (all disabled)
    proceed_with_toggle()
```

**Directive Action**: Initialize database, then proceed.

---

## Related Directives

- **Called By**:
  - User requests - "Enable/disable tracking"
  - `user_preferences_sync` - Checks tracking_settings to know what to log
- **Affects**:
  - `user_preferences_learn` - Requires ai_interaction_log enabled
  - `project_compliance_check` - Can log to fp_flow_tracking if enabled
  - `project_file_write` - Can log to fp_flow_tracking if enabled
- **Modifies**:
  - `tracking_settings` table - Updates enabled flag

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following table:

- **`tracking_settings`**: UPDATE enabled flag and updated_at timestamp

**No data deletion**: Disabling tracking preserves existing logged data (can re-enable and continue).

---

## Testing

How to verify this directive is working:

1. **Enable feature** → Database updated, warning shown
   ```python
   tracking_toggle(feature="ai_interaction_log", action="enable")

   result = query_db("SELECT enabled FROM tracking_settings WHERE feature_name='ai_interaction_log'")
   assert result[0][0] == 1  # Enabled
   ```

2. **Disable feature** → No confirmation required
   ```python
   tracking_toggle(feature="ai_interaction_log", action="disable")

   result = query_db("SELECT enabled FROM tracking_settings WHERE feature_name='ai_interaction_log'")
   assert result[0][0] == 0  # Disabled
   ```

3. **Warning displayed** → User sees token overhead
   ```python
   # Mock user input
   with mock_user_input("y"):
       tracking_toggle(feature="fp_flow_tracking", action="enable")
       # Assert warning was displayed with "~5% token increase"
   ```

4. **Cumulative overhead** → Shows total for all enabled
   ```python
   enable_tracking("ai_interaction_log")  # 3%
   enable_tracking("issue_reports")      # 2%

   status = get_all_tracking_status()
   assert status["total_overhead"] == "~5%"
   ```

---

## Common Mistakes

- ❌ **Enabling without warning** - Must show token overhead
- ❌ **Requiring confirmation for disable** - Should be frictionless
- ❌ **Not showing cumulative overhead** - User needs to see total cost
- ❌ **Deleting data when disabling** - Preserve logs (can re-enable)
- ❌ **Default to enabled** - All tracking must be opt-in

---

## Roadblocks and Resolutions

### Roadblock 1: feature_not_found
**Issue**: Feature name not in tracking_settings table
**Resolution**: Show list of valid features, ask user to choose

### Roadblock 2: preferences_db_missing
**Issue**: user_preferences.db doesn't exist yet
**Resolution**: Initialize database with defaults, then proceed with toggle

---

## References

None
---

*Part of AIFP v1.0 - User customization directive for tracking feature management*

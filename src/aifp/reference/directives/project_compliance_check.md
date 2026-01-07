# Directive: project_compliance_check

**Type**: Tracking (Optional)
**Activation**: Requires `tracking_settings.compliance_checking = enabled`
**Token Overhead**: ~5-10% per check
**Priority**: LOW - Optional analytics feature

---

## Purpose

The `project_compliance_check` directive is an **optional analytics and tracking feature** that provides insights into FP compliance patterns over time. This directive is **DISABLED by default** and only activates when explicitly enabled via tracking settings.

**IMPORTANT**: FP compliance is **baseline behavior** enforced by the system prompt. AI writes FP-compliant code naturally without post-write validation. This directive is NOT a validation gatekeeper - it's an analytics tool for:
- **Tracking FP patterns** used across the project
- **Identifying common violations** (if any occur)
- **Generating compliance reports** for project audits
- **Learning data** for improving FP directive guidance

**When to Enable**:
- Development/debugging of AIFP itself
- Project audits requiring compliance documentation
- Research on FP patterns and adoption
- Educational purposes (tracking learning progress)

**When NOT to Enable**:
- Normal project development (FP is baseline, no checking needed)
- Production work (adds token overhead without benefit)
- Cost-sensitive projects (5-10% token overhead per check)

**Activation**:
```sql
-- Enable compliance tracking
UPDATE tracking_settings SET enabled = 1 WHERE feature_name = 'compliance_checking';
```

**Analytics Provided** (when enabled):
- FP directive consultation frequency
- Common compliance patterns
- Violation types (if any)
- Refactoring statistics

---

## When to Apply

**Prerequisites**:
- `tracking_settings.compliance_checking` must be enabled
- User must acknowledge token overhead warning

This directive applies when:
- **User requests compliance audit** - Manual project-wide scan
- **Research/analytics** - Gathering data on FP patterns
- **Development/debugging** - AIFP development and testing
- **Educational tracking** - Tracking learning progress

**NOT applied automatically**:
- ❌ NOT called by `project_file_write` (FP is baseline, no validation needed)
- ❌ NOT called by `project_update_db` (database updates don't need validation)
- ❌ NOT called by git directives (FP is baseline, no pre-merge validation needed)
- ❌ NOT called by milestone completion (no gatekeeper needed)

---

## Workflow

**Note**: This is a TRACKING workflow, not a validation workflow. It runs ONLY when tracking is enabled.

### Trunk: check_tracking_enabled

Verify compliance tracking is enabled before proceeding.

**Steps**:
1. **Query tracking_settings** - Check if compliance_checking enabled
2. **If disabled** - Skip entirely, return early
3. **If enabled** - Proceed with analytics collection

### Branches

**Branch 1: If tracking_disabled**
- **Then**: `skip`
- **Details**: Tracking not enabled, no action needed
  - Return immediately without checking
  - No token overhead
- **Result**: Early exit (no tracking)

**Branch 2: If tracking_enabled**
- **Then**: `collect_analytics`
- **Details**: Gather compliance analytics
  - Query project.db for functions and their purity levels
  - Analyze FP patterns used
  - Identify any deviations (should be rare since FP is baseline)
  - Log analytics to fp_flow_tracking table (if enabled)
- **Result**: Analytics collected

**Branch 3: If user_requested_report**
- **Then**: `generate_report`
- **Details**: Generate compliance report for user
  - Summary of FP patterns used
  - Function purity distribution
  - Consultation frequency of FP directives
  - Any deviations detected (rare)
- **Result**: Report generated and returned to user

**Branch 4: If analytics_collected**
- **Then**: `log_to_tracking`
- **Details**: Store analytics in tracking tables
  - Update fp_flow_tracking table
  - Store timestamp and project state
  - No blocking behavior (fire and forget)
- **Result**: Analytics logged for future analysis

**Fallback**: `skip`
- **Details**: If any error occurs during tracking
  - Log error (non-blocking)
  - Continue normal operation
  - Tracking is optional - errors don't affect development
- **Result**: Graceful failure

---

## Examples

### Example 1: Enabling Compliance Tracking

```sql
-- Check current status
SELECT feature_name, enabled FROM tracking_settings WHERE feature_name = 'compliance_checking';

-- Enable tracking (user must acknowledge token overhead)
UPDATE tracking_settings SET enabled = 1 WHERE feature_name = 'compliance_checking';

-- Verify enabled
SELECT feature_name, enabled, estimated_token_overhead FROM tracking_settings
WHERE feature_name = 'compliance_checking';
-- Result: compliance_checking | 1 | ~5-10% per check
```

---

### Example 2: Generating Compliance Report

**User Request**: "Generate compliance report for my project"

**AI Action** (if tracking enabled):
```python
# Step 1: Check if tracking enabled
tracking_enabled = query_tracking_settings('compliance_checking')
if not tracking_enabled:
    return "Compliance tracking is disabled. Enable via tracking_toggle directive."

# Step 2: Collect analytics from project.db
functions = query_all_functions()
analytics = {
    "total_functions": len(functions),
    "purity_levels": categorize_by_purity(functions),
    "fp_patterns_used": extract_fp_patterns(functions),
    "deviations": identify_deviations(functions)  # Should be empty if FP is baseline
}

# Step 3: Generate report
report = generate_compliance_report(analytics)
return report
```

**Sample Report**:
```
Project Compliance Report
Generated: 2026-01-06

Total Functions: 42
Purity Distribution:
  - Pure (100%): 42 functions
  - Impure: 0 functions

FP Patterns Used:
  - Result types: 38 functions (90%)
  - Frozen dataclasses: 12 types (100%)
  - Function composition: 15 functions (36%)

Deviations: None detected
Analysis: Project maintains baseline FP compliance
```

---

### Example 3: Analytics Tracking (Background)

**When tracking is enabled**, analytics are collected passively:

```python
# Background tracking (non-blocking)
def on_file_write_complete(file_path: str):
    """Called after successful file write (if tracking enabled)"""
    if not is_tracking_enabled('compliance_checking'):
        return  # Skip if disabled

    # Collect analytics (non-blocking, fire-and-forget)
    functions = parse_functions_from_file(file_path)
    analytics = {
        "timestamp": now(),
        "file": file_path,
        "function_count": len(functions),
        "fp_patterns": identify_fp_patterns(functions),
        "purity_level": analyze_purity(functions)
    }

    # Log to tracking table (async)
    log_to_fp_flow_tracking(analytics)
```

**Notes**:
- Tracking is passive and non-blocking
- Does not affect development workflow
- No validation or gatekeeper behavior
- Purely for analytics and research

---

## Edge Cases

### Edge Case 1: Tracking Disabled During Development

**Issue**: User wants to temporarily disable tracking without losing configuration

**Handling**:
```python
# Disable tracking temporarily
UPDATE tracking_settings SET enabled = 0 WHERE feature_name = 'compliance_checking';

# Later, re-enable
UPDATE tracking_settings SET enabled = 1 WHERE feature_name = 'compliance_checking';

# Historical data preserved in fp_flow_tracking table
```

---

### Edge Case 2: Large Project - Performance Impact

**Issue**: Tracking adds overhead to large projects (1000+ functions)

**Handling**:
- Tracking is **sampling-based** for large projects
- Only tracks 10% of file writes randomly
- Full analytics available on-demand via report generation
- Background tracking uses async operations

```python
# Adaptive tracking rate
if project_function_count > 1000:
    tracking_rate = 0.1  # 10% sampling
elif project_function_count > 100:
    tracking_rate = 0.5  # 50% sampling
else:
    tracking_rate = 1.0  # 100% tracking
```

---

### Edge Case 3: Tracking Data Privacy

**Issue**: User wants to analyze project but doesn't want tracking data stored

**Handling**:
- User can generate report without enabling persistent tracking
- Report generated from project.db (always available)
- No data written to fp_flow_tracking
- Tracking tables remain empty

```python
# One-time report (no tracking enabled)
report = generate_compliance_report(include_tracking=False)
# Uses only project.db, no tracking tables accessed
```

---

### Edge Case 4: Tracking Table Growth

**Issue**: Tracking tables grow over time

**Handling**:
- Automatic cleanup of tracking data older than 90 days
- User can configure retention period
- Export functionality for long-term storage

```sql
-- Configure retention (via user_preferences)
INSERT INTO user_settings (setting_key, setting_value)
VALUES ('tracking_retention_days', '90');

-- Manual cleanup
DELETE FROM fp_flow_tracking WHERE timestamp < date('now', '-90 days');
```

---

## Related Directives

- **Tracking Management**:
  - `tracking_toggle` - Enable/disable compliance tracking with token warnings
  - `user_preferences_sync` - Load tracking preferences

- **Analytics & Reports**:
  - `aifp_status` - Can include compliance summary if tracking enabled
  - `project_completion_check` - Can reference compliance analytics

- **FP Reference** (Compliance tracking analyzes usage of these):
  - `fp_purity` - Tracks purity pattern usage
  - `fp_immutability` - Tracks immutability pattern usage
  - `fp_no_oop` - Tracks OOP elimination patterns
  - `fp_type_safety` - Tracks type safety patterns
  - `fp_result_types` - Tracks error handling patterns

**Note**: This directive does NOT automatically call or escalate to FP directives. It only tracks which patterns are used in the codebase.

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive interacts with the following tables:

**Reads From**:
- **`tracking_settings`** (user_preferences.db): Checks if compliance_checking enabled
- **`functions`** (project.db): Reads function metadata for analytics
- **`files`** (project.db): Reads file structure for report generation

**Writes To**:
- **`fp_flow_tracking`** (user_preferences.db): Logs compliance analytics (if tracking enabled)

**Note**: This directive does NOT modify `functions` table or set compliance flags. FP compliance is baseline behavior, not something tracked per-function.

---

## Testing

How to verify this directive is working:

1. **Test tracking enable/disable**
   ```python
   # Disable tracking
   UPDATE tracking_settings SET enabled = 0 WHERE feature_name = 'compliance_checking';
   result = project_compliance_check()
   assert result == "Tracking disabled, no action taken"

   # Enable tracking
   UPDATE tracking_settings SET enabled = 1 WHERE feature_name = 'compliance_checking';
   result = project_compliance_check()
   assert result["tracking_active"] == True
   ```

2. **Test report generation**
   ```python
   # Generate report (tracking must be enabled)
   report = generate_compliance_report()
   assert "total_functions" in report
   assert "fp_patterns_used" in report
   assert "purity_distribution" in report
   ```

3. **Test analytics collection**
   ```python
   # Write file, check tracking logged
   write_file("src/test.py", content)
   tracking_entries = query("SELECT * FROM fp_flow_tracking WHERE file = 'src/test.py'")
   assert len(tracking_entries) >= 1
   ```

4. **Test token overhead warning**
   ```python
   # Enabling should show warning
   enable_tracking("compliance_checking")
   # Should display: "Warning: ~5-10% token overhead. Continue? (y/n)"
   ```

---

## Common Mistakes

- ❌ **Assuming tracking is enabled** - Always check `tracking_settings` first
- ❌ **Using for validation** - This is analytics only, not a gatekeeper
- ❌ **Forgetting token overhead warning** - Warn users before enabling
- ❌ **Enabling for all projects** - Most projects don't need tracking
- ❌ **Treating as mandatory** - Tracking is 100% optional

---

## Roadblocks and Resolutions

### Roadblock 1: tracking_disabled
**Issue**: Tracking features not available
**Resolution**: Enable via `tracking_toggle` directive with user consent

### Roadblock 2: performance_impact
**Issue**: Tracking adds overhead to large project
**Resolution**: Use sampling mode (10% tracking) or disable tracking entirely

---

## References

- `docs/settings-specification.json` - compliance_checking tracking feature definition
- `docs/settings-cleanup-summary.md` - Settings architecture and decision rationale
- `user_preferences.sql` - tracking_settings table schema

---

*Part of AIFP v1.0 - Optional tracking directive for FP compliance analytics*

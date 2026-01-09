# Tracking Notes Reference

**Table**: `user_preferences.db.tracking_notes`
**Purpose**: General-purpose notes for opt-in tracking features
**Status**: Disabled by default (controlled by tracking_settings)

---

## Schema

```sql
CREATE TABLE IF NOT EXISTS tracking_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    note_type TEXT NOT NULL CHECK (note_type IN (
        'fp_analysis',      -- FP compliance, patterns, refactorings, optimizations
        'user_interaction', -- User corrections, preferences, feedback patterns
        'validation',       -- Validation results, checks, approvals
        'performance',      -- Performance metrics, bottlenecks, profiling
        'debug'             -- Debug traces, reasoning traces, experiments
    )),
    reference_type TEXT,                        -- e.g., 'function', 'file', 'directive'
    reference_name TEXT,                        -- e.g., function name, file path, directive name
    reference_id INTEGER,                       -- Optional ID if referencing project.db entity
    directive_name TEXT,                        -- Directive that created this note
    severity TEXT DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error')),
    metadata_json TEXT,                         -- Additional context (JSON)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## Note Types

### 1. fp_analysis
**Purpose**: FP compliance observations, pattern usage, refactorings, optimizations

**When to use**:
- FP directive consultations (purity, immutability, no-OOP, etc.)
- Compliance violations detected
- Refactoring suggestions
- Pattern usage observations
- Optimization opportunities

**Example**:
```sql
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity,
    metadata_json
) VALUES (
    'Function refactored for purity: eliminated mutation',
    'fp_analysis',
    'function',
    'calculate_total',
    'fp_purity',
    'info',
    '{"mutation_type": "in-place list modification", "refactored": true}'
);
```

### 2. user_interaction
**Purpose**: User correction patterns, preference learning, feedback

**When to use**:
- User corrects AI output
- Preference patterns detected
- User feedback on directive behavior
- Clarification requests

**Example**:
```sql
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity
) VALUES (
    'User prefers docstrings on all functions',
    'user_interaction',
    'preference',
    'always_add_docstrings',
    'user_preferences_learn',
    'info'
);
```

### 3. validation
**Purpose**: Validation results, compliance checks, approvals

**When to use**:
- Directive validation sessions
- Compliance check results
- User approval/rejection tracking
- Test validation results

**Example**:
```sql
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity
) VALUES (
    'User directive validation passed: all tests successful',
    'validation',
    'directive',
    'user_directive_custom_formatter',
    'user_directive_validate',
    'info'
);
```

### 4. performance
**Purpose**: Performance metrics, bottlenecks, profiling results

**When to use**:
- Performance analysis
- Bottleneck detection
- Profiling results
- Optimization metrics

**Example**:
```sql
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity,
    metadata_json
) VALUES (
    'Function execution time: 250ms (bottleneck detected)',
    'performance',
    'function',
    'process_large_dataset',
    'fp_cost_analysis',
    'warning',
    '{"execution_time_ms": 250, "calls_per_second": 4}'
);
```

### 5. debug
**Purpose**: Debug traces, reasoning traces, experiments

**When to use**:
- AI reasoning traces
- Debug information
- Experimental features
- Development/testing notes

**Example**:
```sql
INSERT INTO tracking_notes (
    content,
    note_type,
    reference_type,
    reference_name,
    directive_name,
    severity,
    metadata_json
) VALUES (
    'AI reasoning: Chose Option type over null for safety',
    'debug',
    'function',
    'find_user',
    'fp_optionals',
    'info',
    '{"alternatives_considered": ["null", "exception", "Option"], "reason": "type safety"}'
);
```

---

## Key Differences from project.db notes

| Feature | project.db notes | tracking_notes (user_preferences.db) |
|---------|------------------|-------------------------------------|
| **Purpose** | Project management context | Tracking/analytics/debugging |
| **Enabled** | Always on | Opt-in (disabled by default) |
| **Token cost** | No overhead | ~1-5% overhead |
| **note_types** | Project-focused (decision, evolution, analysis, task_context, external, summary) | Tracking-focused (fp_analysis, user_interaction, validation, performance, debug) |
| **reference_table** | Fixed tables (project, tasks, functions, etc.) | Flexible (reference_type + reference_name) |
| **Updated by** | Project directives | Tracking features only |

---

## Usage Pattern

**Always check if tracking is enabled first**:

```python
# Check if tracking enabled
tracking_enabled = query_tracking_settings('fp_flow_tracking')  # or other tracking feature

if tracking_enabled:
    # Only then insert to tracking_notes
    insert_tracking_note(
        content="Function refactored for purity",
        note_type="fp_analysis",
        reference_type="function",
        reference_name="calculate_total",
        directive_name="fp_purity"
    )
```

**FP directives should reference this table, not project.db notes**:

```markdown
## Database Operations

**Project Database** (project.db):
- **`functions`**: Updates function metadata

**Tracking** (Optional - Disabled by Default):

If tracking is enabled, this directive may log to:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
```

---

## Migration from Old FP Directives

### Before (WRONG - references project.db):
```markdown
- **`notes`**: Logs immutability violations with `note_type = 'compliance'`
```

### After (CORRECT - references tracking_notes):
```markdown
**Tracking** (Optional - Disabled by Default):

If tracking is enabled:
- **`tracking_notes`** (user_preferences.db): Logs FP analysis with `note_type='fp_analysis'`

Only occurs when `fp_flow_tracking` is enabled via `tracking_toggle`.
Token overhead: ~5% per file write.
```

---

## Severity Levels

- **info**: Normal tracking observations
- **warning**: Important issues, bottlenecks, or patterns worth attention
- **error**: Critical issues, blocking problems, or failures

---

## Querying Examples

### Get all FP analysis notes for a function:
```sql
SELECT * FROM tracking_notes
WHERE note_type = 'fp_analysis'
  AND reference_type = 'function'
  AND reference_name = 'calculate_total'
ORDER BY created_at DESC;
```

### Get all notes from a directive:
```sql
SELECT * FROM tracking_notes
WHERE directive_name = 'fp_purity'
ORDER BY created_at DESC;
```

### Get warnings/errors only:
```sql
SELECT * FROM tracking_notes
WHERE severity IN ('warning', 'error')
ORDER BY created_at DESC;
```

### Get performance bottlenecks:
```sql
SELECT * FROM tracking_notes
WHERE note_type = 'performance'
  AND severity = 'warning'
ORDER BY created_at DESC;
```

---

## Best Practices

1. ✅ **Always check tracking enabled** before inserting
2. ✅ **Use appropriate note_type** for context
3. ✅ **Include reference_type and reference_name** for linkage
4. ✅ **Use metadata_json** for structured data
5. ✅ **Set severity appropriately** (info/warning/error)
6. ✅ **Include directive_name** for attribution

7. ❌ **Don't use for project management** - use project.db notes
8. ❌ **Don't assume tracking is enabled** - always check first
9. ❌ **Don't mix project and tracking notes** - keep separate

---

**This table is specifically for opt-in tracking. Most users will never enable it. Use sparingly and only when tracking features are explicitly enabled.**

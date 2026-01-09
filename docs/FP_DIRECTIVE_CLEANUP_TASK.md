# FP Directive Cleanup Task

**Date**: 2026-01-08
**Status**: Ready to execute
**Priority**: Critical - Prevents erroneous logging to project.db

---

## Problem Summary

**Found**: 33 FP directive files with incorrect note_type references
**Pattern**: `- **\`notes\`**: Logs X with \`note_type = 'Y'\``
**Issue**: These note_types are NOT in schema and imply logging to project.db

### Invalid note_types Found:
- compliance (8 instances)
- refactoring (9 instances)
- optimization (5 instances)
- wrapper, validation, security, normalization, documentation
- metadata, indexing, determinism, formatting, cleanup
- performance, reasoning_trace

**None of these are in the project.db notes schema!**

---

## What Needs to Change

### Current (WRONG):
```markdown
## Database Operations

- **`functions`**: Updates function metadata
- **`notes`**: Logs immutability violations with `note_type = 'compliance'`
```

**Problems**:
1. ❌ `compliance` not in schema (fails CHECK constraint)
2. ❌ Implies logging to project.db (should be user_preferences.db)
3. ❌ Implies automatic logging (tracking is opt-in)
4. ❌ Implies post-write validation (FP is baseline)

### Replacement (CORRECT):
```markdown
## Database Operations

**Project Database** (project.db):
- **`functions`**: Updates function metadata with immutability analysis

**FP Compliance Tracking** (Optional - Disabled by Default):

This directive does NOT automatically log to project.db notes table.

If `fp_flow_tracking` is enabled in user_preferences.db (via `tracking_toggle`):
- AI may log FP pattern usage to `fp_flow_tracking` table
- Located in user_preferences.db, NOT project.db
- Token overhead: ~5% per file write
- Used for analytics and development only

**Important Context**:
- FP compliance is baseline behavior (enforced by system prompt during code writing)
- This directive is reference documentation consulted when AI is uncertain
- NO post-write validation occurs
- NO automatic logging to project.db
- Tracking is opt-in for AIFP development and debugging

**Example** (only if tracking explicitly enabled):
```sql
-- Logs to user_preferences.db.fp_flow_tracking (NOT project.db)
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score,
    issues_json,
    created_at
) VALUES (
    'calculate_total',
    'src/calculator.py',
    '["fp_immutability", "fp_purity"]',
    1.0,
    NULL,
    CURRENT_TIMESTAMP
);
```

**Note**: Most users will never enable fp_flow_tracking. It's primarily for:
- AIFP development and testing
- Project audits requiring compliance documentation
- Research on FP pattern adoption
```

---

## Files Requiring Cleanup

33 files total (based on note_type references):

1. fp_ai_reasoning_trace.md
2. fp_constant_folding.md
3. fp_cost_analysis.md
4. fp_cross_language_wrappers.md
5. fp_data_filtering.md
6. fp_dead_code_elimination.md
7. fp_docstring_enforcement.md
8. fp_encoding_consistency.md
9. fp_error_pipeline.md
10. fp_evaluation_order_control.md
11. fp_function_indexing.md
12. fp_function_inlining.md
13. fp_immutability.md
14. fp_keyword_alignment.md
15. fp_language_standardization.md
16. fp_lazy_computation.md
17. fp_lazy_evaluation.md
18. fp_list_operations.md
19. fp_map_reduce.md
20. fp_metadata_annotation.md
21. fp_monadic_composition.md
22. fp_no_oop.md
23. fp_null_elimination.md
24. fp_optionals.md
25. fp_parallel_evaluation.md
26. fp_pattern_unpacking.md
27. fp_purity.md
28. fp_purity_caching_analysis.md
29. fp_recursion_enforcement.md
30. fp_reflection_block.md
31. fp_result_types.md
32. fp_symbol_map_validation.md
33. fp_try_monad.md

---

## Cleanup Process

### Step 1: Backup
```bash
cd /home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives
mkdir -p ../../../docs/backups/fp_directives_$(date +%Y%m%d)
cp fp_*.md ../../../docs/backups/fp_directives_$(date +%Y%m%d)/
```

### Step 2: For Each File

1. **Find the Database Operations section**
2. **Locate the line**: `- **\`notes\`**: Logs ... with \`note_type = 'X'\``
3. **Remove that entire line**
4. **Add the replacement template** (see above)
5. **Adjust the template** to match the specific directive:
   - Keep the relevant function table operations
   - Mention the specific FP directive in `fp_directives_applied` array
   - Keep example focused on that directive's purpose

### Step 3: Additional Section Updates

For each file, also ensure:

**Purpose Section** includes:
```markdown
**Important**: This directive is reference documentation for complex FP scenarios.
AI consults this when uncertain about implementation details or edge cases.

**NOT used for**:
- ❌ Post-write validation (FP is baseline, code is already compliant)
- ❌ Automatic checking (no validation loop)
- ❌ Standard logging (tracking is opt-in, disabled by default)
```

**When to Apply Section** clarifies:
```markdown
This directive applies when:
- AI is uncertain about [specific FP pattern]
- Complex edge case not covered by baseline FP knowledge
- Advanced scenario requiring detailed guidance

**NOT applied automatically**:
- NOT called after every file write
- NOT used for validation
- Only consulted when AI needs guidance
```

---

## Automation Script

```bash
#!/bin/bash
# cleanup_fp_directives.sh

FP_DIR="/home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives"
cd "$FP_DIR"

# For each FP directive
for file in fp_*.md; do
    echo "Processing: $file"

    # Check if it has the problematic pattern
    if grep -q "notes\`\*\*: Logs.*note_type = " "$file"; then
        echo "  ✓ Found note_type reference - needs cleanup"
        echo "  → Manual review required: $file"
    fi
done

echo ""
echo "Manual cleanup required for files listed above."
echo "Use the template from FP_DIRECTIVE_CLEANUP_TASK.md"
```

---

## Quality Checks

After cleaning each file, verify:

1. ✅ **No invalid note_types**: `grep "note_type = " fp_X.md` returns nothing OR only valid schema types
2. ✅ **Mentions fp_flow_tracking**: `grep "fp_flow_tracking" fp_X.md` returns matches
3. ✅ **Mentions user_preferences.db**: `grep "user_preferences.db" fp_X.md` returns matches
4. ✅ **Clarifies opt-in**: `grep -i "opt-in\|disabled by default" fp_X.md` returns matches
5. ✅ **No project.db notes logging**: No SQL inserting to notes table
6. ✅ **Purpose clarifies reference use**: Mentions "reference documentation" or "consulted when uncertain"

---

## Example Cleanup (fp_immutability.md)

### Before:
```markdown
## Database Operations

- **`functions`**: Updates functions with immutability analysis results
- **`notes`**: Logs immutability violations with `note_type = 'compliance'`
```

### After:
```markdown
## Database Operations

**Project Database** (project.db):
- **`functions`**: Updates function metadata with immutability analysis results

**FP Compliance Tracking** (Optional - Disabled by Default):

This directive does NOT automatically log to project.db notes table.

If `fp_flow_tracking` is enabled in user_preferences.db (via `tracking_toggle`):
- AI may log immutability pattern usage to `fp_flow_tracking` table
- Located in user_preferences.db, NOT project.db
- Token overhead: ~5% per file write
- Used for analytics and development only

**Important Context**:
- FP immutability compliance is baseline behavior (enforced during code writing)
- This directive is reference documentation for complex immutability scenarios
- NO post-write validation occurs
- NO automatic logging to project.db
- Tracking is opt-in for AIFP development and debugging

**Example** (only if tracking explicitly enabled):
```sql
-- Logs to user_preferences.db.fp_flow_tracking
INSERT INTO fp_flow_tracking (
    function_name,
    file_path,
    fp_directives_applied,
    compliance_score,
    issues_json,
    created_at
) VALUES (
    'update_user',
    'src/user.py',
    '["fp_immutability", "fp_purity"]',
    1.0,
    '{"mutations_eliminated": ["in-place list modification"]}',
    CURRENT_TIMESTAMP
);
```

**Note**: Most users will never enable fp_flow_tracking. It's primarily for:
- AIFP development and testing
- Project audits requiring compliance documentation
- Research on FP pattern adoption
```

---

## Priority Order

Clean in this order for maximum impact:

### High Priority (Core FP Directives):
1. fp_purity.md - Most fundamental
2. fp_immutability.md - Core concept
3. fp_no_oop.md - Critical pattern
4. fp_result_types.md - Error handling standard
5. fp_optionals.md - Option type usage

### Medium Priority (Common Patterns):
6. fp_monadic_composition.md
7. fp_error_pipeline.md
8. fp_list_operations.md
9. fp_data_filtering.md
10. fp_map_reduce.md

### Lower Priority (Specialized):
11-33. Remaining FP directives

---

## Validation After Cleanup

Run these checks:

```bash
# 1. No invalid note_types remain
grep -h "note_type = " fp_*.md | grep -v "auto_summary\|clarification\|pivot\|research\|decision\|evolution\|analysis\|task_context\|external\|summary"
# Should return nothing

# 2. All have fp_flow_tracking context
for f in fp_*.md; do
    if ! grep -q "fp_flow_tracking" "$f"; then
        echo "Missing fp_flow_tracking context: $f"
    fi
done

# 3. All mention opt-in or disabled by default
for f in fp_*.md; do
    if ! grep -qi "opt-in\|disabled by default" "$f"; then
        echo "Missing opt-in clarification: $f"
    fi
done

# 4. None have INSERT INTO notes for FP tracking
for f in fp_*.md; do
    if grep -q "INSERT INTO notes" "$f" && ! grep -qi "tracking\|example" "$f"; then
        echo "Suspicious INSERT INTO notes: $f"
    fi
done
```

---

## Timeline

**Per file**: ~5-10 minutes (read, understand, apply template, verify)
**Total**: 33 files × 8 minutes = ~4-5 hours

**Recommended approach**: Batch process in groups of 5-10 files, validate each batch

---

## Next Steps

1. ✅ Schema updated (complete)
2. ✅ Cleanup task defined (this document)
3. **▶ Start cleanup**: Begin with high-priority files (fp_purity, fp_immutability, fp_no_oop, fp_result_types, fp_optionals)
4. Validate each batch after cleanup
5. Update directive JSON files if they also have note_type references
6. Update system prompt if needed
7. Test with sample project

---

**Ready to start cleanup? Begin with fp_purity.md (most fundamental FP directive).**

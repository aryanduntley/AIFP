# FP Logging Cleanup - Remove Inappropriate Standard Logging

**Date**: 2025-12-13
**Issue**: Found ~30+ FP directive MD files documenting notes logging as standard behavior
**Problem**:
1. FP logging (`fp_flow_tracking`) is **disabled by default** and costs ~5% more tokens
2. Should only be used temporarily for dev debugging
3. Directives document INSERT INTO notes as if it's standard workflow
4. **Logging should be discouraged, not standard practice**

---

## Completed

✅ **project_user_referral.md** - Replaced SQL with helper guidance (user referral is legitimate logging)
✅ **fp_borrow_check.md** - Removed SQL examples, added "only if fp_flow_tracking enabled (disabled by default)" notes

---

## Pattern to Replace

### In Workflow Steps - Remove SQL, Add Conditional Note

**Current (Bad)**:
```markdown
- Update database:
  ```sql
  INSERT INTO notes (...) VALUES (...);
  ```
- **Result**: Violation flagged
```

**Should Be (Good)**:
```markdown
- **Result**: Violation flagged
  - Note: Logging only occurs if `fp_flow_tracking` enabled (disabled by default)
```

### In Database Operations Section

**Current (Bad)**:
```markdown
- **`notes`**: INSERT compliance violations
```

**Should Be (Good)**:
```markdown
- **`notes`**: INSERT compliance violations (only if `fp_flow_tracking` enabled - disabled by default)
```

---

## Key Principle from tracking_toggle.md

> **Design Philosophy**: Project work should be cost-efficient. Debugging and analytics are opt-in luxuries.

- All tracking features **disabled by default**
- `fp_flow_tracking` costs ~5% more tokens
- Should only be enabled for temporary debugging
- **Never** document as standard workflow behavior

---

## Files Needing FP Logging Cleanup

### High Priority (document logging as standard behavior)
- [ ] fp_api_design.md
- [ ] fp_chaining.md (2 instances)
- [ ] fp_concurrency_safety.md
- [ ] fp_conditional_elimination.md
- [ ] fp_const_refactoring.md (2 instances)
- [ ] fp_currying.md (2 instances)
- [ ] fp_documentation.md
- [ ] fp_generic_constraints.md
- [ ] fp_guard_clauses.md
- [ ] fp_inheritance_flattening.md
- [ ] fp_io_isolation.md
- [ ] fp_logging_safety.md
- [ ] fp_memoization.md
- [ ] fp_naming_conventions.md

### Medium Priority (function/interaction tracking)
- [ ] fp_dependency_tracking.md (interactions tracking - review if standard behavior)
- [ ] fp_call_graph_generation.md (call graph logging - review if standard behavior)
- [ ] fp_function_indexing.md (function registration - likely standard, review)
- [ ] fp_error_pipeline.md (function updates - likely standard, review)
- [ ] fp_null_elimination.md (function updates - likely standard, review)
- [ ] fp_optionals.md (function updates - likely standard, review)

---

## Recommendation

**Primary Action**: Remove SQL examples and add conditional notes making clear that logging:
1. Is **disabled by default**
2. Only occurs when `fp_flow_tracking` is enabled
3. Costs ~5% more tokens
4. Is for temporary debugging only

**Approach**: Create automated script to:
1. Remove all `INSERT INTO notes` SQL blocks in FP directive workflows
2. Add note: "Logging only occurs if `fp_flow_tracking` enabled (disabled by default)"
3. Update Database Operations sections with conditional clauses

---

## Why This Matters

**From user's perspective:**
- FP directives are run frequently during development
- If every FP check logs to notes, tokens explode quickly
- User shouldn't think logging is "how it works"
- Logging is an **opt-in debugging tool**, not standard behavior

**Correct mental model:**
- FP directives analyze and enforce rules
- Results are NOT logged by default
- Only if user enables `fp_flow_tracking` for debugging
- Then logs are available for analysis

---

## Notes

- Database Operations sections need "(only if fp_flow_tracking enabled)" added
- Workflow SQL blocks should be removed entirely
- Replace with: "Note: Logging only occurs if fp_flow_tracking enabled (disabled by default)"
- Function/interaction updates (not notes) may be standard behavior - review individually

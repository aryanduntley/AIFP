# SQL Cleanup Checklist - FP Directives

**Created**: 2025-12-14
**Purpose**: Track removal of INSERT INTO notes from FP directive files
**Script**: `docs/directives-json/Tasks/cleanup_single_file.py`

---

## Progress Summary

**Total Files**: 27 original
- ✅ **Completed**: 27
- ⏳ **Remaining**: 0
- **Progress**: 100% 🎉

**Removed Directive**: fp_call_graph_generation (entire file deleted - used non-existent table)

---

## Completed Files ✅

| File | Date | Notes | Backup |
|------|------|-------|--------|
| fp_api_design.md | 2025-12-14 | Removed 1 INSERT INTO notes | sql_cleanup/fp_api_design_20251214_192145.md |
| fp_call_graph_generation.md | 2025-12-14 | **ENTIRE FILE DELETED** - Redundant with fp_dependency_tracking | N/A - removed from repo |
| fp_const_refactoring.md | 2025-12-14 | Removed 2 INSERT INTO notes | Manual edit |
| fp_currying.md | 2025-12-14 | Removed 2 INSERT INTO notes | Manual edit |
| fp_wrapper_generation.md | 2025-12-14 | Removed 2 INSERT INTO notes | Manual edit |
| fp_concurrency_safety.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_conditional_elimination.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_documentation.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_generic_constraints.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_guard_clauses.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_inheritance_flattening.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_io_isolation.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_logging_safety.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_memoization.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_naming_conventions.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_ownership_safety.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_parallel_purity.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_pattern_matching.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_reflection_limitation.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_runtime_type_check.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_side_effects_flag.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_state_elimination.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_tail_recursion.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_task_isolation.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_test_purity.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_type_inference.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |
| fp_type_safety.md | 2025-12-14 | Removed 1 INSERT INTO notes | Manual edit |

---

## All Files Complete! ✅

Use this checklist to track progress. Mark [X] when cleaned and reviewed.

### Files with 2+ occurrences
- [X] **fp_const_refactoring.md** (2 instances) ✅
- [X] **fp_currying.md** (2 instances) ✅
- [X] **fp_wrapper_generation.md** (2 instances) ✅

### Single-occurrence files (22)
- [X] fp_concurrency_safety.md ✅
- [X] fp_conditional_elimination.md ✅
- [X] fp_documentation.md ✅
- [X] fp_generic_constraints.md ✅
- [X] fp_guard_clauses.md ✅
- [X] fp_inheritance_flattening.md ✅
- [X] fp_io_isolation.md ✅
- [X] fp_logging_safety.md ✅
- [X] fp_memoization.md ✅
- [X] fp_naming_conventions.md ✅
- [X] fp_ownership_safety.md ✅
- [X] fp_parallel_purity.md ✅
- [X] fp_pattern_matching.md ✅
- [X] fp_reflection_limitation.md ✅
- [X] fp_runtime_type_check.md ✅
- [X] fp_side_effects_flag.md ✅
- [X] fp_state_elimination.md ✅
- [X] fp_tail_recursion.md ✅
- [X] fp_task_isolation.md ✅
- [X] fp_test_purity.md ✅
- [X] fp_type_inference.md ✅
- [X] fp_type_safety.md ✅

**🎉 ALL FILES CLEANED! 🎉**

---

## Cleanup Instructions

### For each file:

1. **Find the SQL blocks**:
   ```bash
   grep -B 5 -A 10 "INSERT INTO notes" <filename>
   ```

2. **Manual cleanup using Edit tool**:
   - Remove entire SQL block containing `INSERT INTO notes`
   - If preceded by "- Update database:", remove that line too
   - If inside code comments like "# Database log", remove the comment + SQL

3. **Verify removal**:
   ```bash
   grep "INSERT INTO notes" <filename>
   # Should return nothing
   ```

4. **Check for fragments**:
   - Read the section where SQL was removed
   - Ensure no hanging bullets or incomplete sentences
   - Verify surrounding context still makes sense

5. **Mark complete**:
   - Update this checklist: `- [ ]` → `- [X]`
   - Add to "Completed Files" table with date

---

## Pattern Reference

### Pattern 1: Workflow step with SQL
```markdown
- Update database:
  ```sql
  INSERT INTO notes (project_id, content, tags, created_at)
  VALUES (...);
  ```
- **Result**: Something happened
```

**Remove**: Everything from "- Update database:" through the closing ```

**Result**:
```markdown
- **Result**: Something happened
```

---

### Pattern 2: SQL in code comments
```python
# Database log
INSERT INTO notes (...) VALUES (...);

# Result:
```

**Remove**: The "# Database log" line and the INSERT statement

**Result**:
```python
# Result:
```

---

### Pattern 3: Database Operations section
```markdown
### Record Compliance
```sql
INSERT INTO notes ...
```
```

**Remove**: The entire SQL block (but keep the heading)

**Result**:
```markdown
### Record Compliance

---
```

---

## What NOT to Remove

**KEEP all of these:**
- ✅ `UPDATE functions` - tracks function metadata (standard behavior)
- ✅ `INSERT INTO interactions` - tracks function calls (standard behavior)
- ✅ `INSERT INTO functions` - registers new functions
- ✅ `INSERT INTO files` - registers files
- ✅ SQL in code examples showing bad/good patterns
- ✅ `CREATE TABLE` statements (schema docs)
- ✅ `SELECT` queries (reading data)

**ONLY REMOVE:**
- ❌ `INSERT INTO notes` - opt-in debugging, disabled by default

---

## Quality Checks

Before marking a file complete, verify:

1. ✅ No `INSERT INTO notes` remains
2. ✅ No hanging bullets or fragments
3. ✅ Surrounding text flows naturally
4. ✅ All other SQL intact (UPDATE functions, etc.)
5. ✅ File still opens and reads correctly

---

## Notes

- **Backups created**: All cleaned files have timestamped backups in `docs/directives-json/backups/sql_cleanup/`
- **Why remove notes logging**: `fp_flow_tracking` is DISABLED by default, costs ~5% more tokens, should only be used for temporary debugging
- **Call graph removed**: `fp_call_graph_generation` directive referenced non-existent `call_graph` table - functionality fully covered by `fp_dependency_tracking` which correctly uses `interactions` table

---

**Last Updated**: 2025-12-14
**Next**: Clean remaining 25 files using Edit tool, one-by-one

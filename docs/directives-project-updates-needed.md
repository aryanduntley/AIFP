# directives-project.json Updates Needed
**Date**: 2025-11-24
**File**: docs/directives-json/directives-project.json
**Status**: Analysis Complete - Refined Approach Defined

---

## CRITICAL FINDINGS

### 1. available_helpers NOT Used by sync-directives.py
**Finding**: Verified that sync-directives.py does NOT read `available_helpers` arrays
**Action**: **REMOVE all available_helpers arrays** from directives
**Rationale**: directive-helper-interactions.json is used to populate directive_helpers table

### 2. SQL Queries Must Be Removed
**Finding**: Custom SQL queries in workflow details
**Action**: **REPLACE with helper function calls**
**Rationale**: AI should use helper functions, not formulate custom queries
- Faster (helper functions optimized)
- Safer (no SQL injection, validated queries)
- Maintainable (helper updates don't require directive changes)

---

## Issues Found

### 1. project_id References in SQL Queries (3 occurrences)
**Issue**: Queries reference `project_id` field which has been removed from all tables

#### Line 1714 - aifp_status directive
```json
"query": "SELECT type, value, description FROM infrastructure WHERE project_id = ?"
```
**Fix**: Remove WHERE clause (1 project per database)
```json
"query": "SELECT type, value, description FROM infrastructure"
```

#### Line 2813 - project_milestone_complete directive
```json
"query": "SELECT COUNT(*) FROM completion_path WHERE project_id = ? AND status NOT IN ('completed')"
```
**Fix**: Remove project_id filter
```json
"query": "SELECT COUNT(*) FROM completion_path WHERE status NOT IN ('completed')"
```

#### Line 2832 - project_milestone_complete directive
```json
"query_next_milestone": "SELECT m.id, m.name, m.description FROM milestones m JOIN completion_path cp ON m.completion_path_id = cp.id WHERE cp.project_id = ? AND m.status = 'pending' ORDER BY cp.order_index, m.id LIMIT 1"
```
**Fix**: Remove project_id condition
```json
"query_next_milestone": "SELECT m.id, m.name, m.description FROM milestones m JOIN completion_path cp ON m.completion_path_id = cp.id WHERE m.status = 'pending' ORDER BY cp.order_index, m.id LIMIT 1"
```

---

### 2. Priority Values - Status Check
**Finding**: Priority references use TEXT values ("high", "low") which is CORRECT
- Line 400: `"priority": "high"` ✅
- Line 409: `"priority": "low"` ✅
- Line 497: `"priority": "high"` ✅

**No changes needed** - already using TEXT format matching CHECK constraints

---

### 3. Status Values - Status Check
**Finding**: All status values match CHECK constraints
- "pending" ✅
- "in_progress" ✅
- "completed" ✅
- "cancelled" ✅
- "blocked" ✅

**No changes needed** - already compliant

---

### 4. Helper References - Minimization Check

#### Keep (Top-level orchestration - necessary)
```json
// aifp_run directive
"available_helpers": [
  "get_all_directives",     // Core orchestration
  "get_directive",          // Core orchestration
  "search_directives",      // Core orchestration
  "query_mcp_db",           // Core orchestration
  "get_project_context",    // Status reporting
  "get_project_status",     // Status reporting
  "get_project_files",      // Status reporting
  "get_project_functions",  // Status reporting
  "get_project_tasks",      // Status reporting
  "query_project_db"        // Status reporting
]
```
**Rationale**: These are stable top-level directive/status tools. Names won't change. Necessary for AI guidance.

#### Extract to directive-helper-interactions.json (Implementation details)
Found at various locations - helper references embedded in workflow steps that should be in the mapping table instead:
- Line 2558: `"helper": "get_project_tasks"` in project_task_complete
- Various other specific helper calls in workflow steps

**Action**: Review each workflow step and extract implementation-level helper references to directive-helper-interactions.json

---

### 5. New Schema Fields - Missing References

#### Reservation System
**Missing**: No directives currently handle file/function/type reservation workflow
**Action**: Need to create new directives (separate ticket - not in this file):
- `reserve_file`
- `reserve_function`
- `reserve_type`
- `finalize_reservation`
- `verify_ids`
- `repair_ids`

#### New Fields
**Missing in workflows**:
- `files.name` (separate from path)
- `functions.returns` (return value JSON)
- `types.file_id` (which file defines type)

**Action**: Not directly applicable to project directives (these are FP directive concerns)

---

## Summary of Changes Required

### Immediate Changes (This File)
1. ✅ **Remove 3 project_id references** from SQL queries (lines 1714, 2813, 2832)
2. ✅ **Priority values** - Already correct (TEXT format)
3. ✅ **Status values** - Already correct (match CHECK constraints)
4. 🔄 **Helper references** - Review and extract workflow implementation details

### No Changes Needed
- Priority handling (already TEXT)
- Status values (already compliant)
- Top-level orchestration helper lists (keep as-is)

### Future Work (Not This File)
- Create reservation system directives (new files)
- Update FP directives for new fields (different files)

---

## Refined Approach (5 Directives at a Time)

### Workflow Per Batch
1. **Extract 5 directives** using jq
2. **Review extracted batch** for all issues
3. **Fix all issues** in batch file
4. **Validate JSON** syntax
5. **Review corresponding .md files** (after every 5)
6. **Merge batch back** when complete

### Per-Directive Checklist
- [ ] Remove available_helpers arrays
- [ ] Replace SQL queries with helper function calls
- [ ] Remove project_id references
- [ ] Update helper names to current helpers
- [ ] Verify priority/status values match CHECK constraints
- [ ] Add reservation system (if creates files/functions/types)
- [ ] Remove linked_function_id (if type directive)
- [ ] Verify FP terminology (no OOP concepts)

### Command Reference
```bash
# Extract batch (directives 0-4)
jq '.[0:5]' directives-project.json > batch-01.json

# Check for SQL queries
jq -r '.[].workflow.branches[]?.details?.query? | select(. != null)' batch-01.json

# Check for available_helpers
jq -r '.[].workflow.branches[]?.details?.available_helpers? | select(. != null)' batch-01.json

# Find project_id references
jq '.' batch-01.json | grep -i 'project_id'
```

### Batches for directives-project.json (37 directives)
- Batch 1: Directives 1-5 (aifp_run through project_file_write)
- Batch 2: Directives 6-10 (project_update_db through project_evolution)
- Batch 3: Directives 11-15 (project_user_referral through project_dependency_sync)
- Batch 4: Directives 16-20 (project_integrity_check through project_refactor_path)
- Batch 5: Directives 21-25 (project_dependency_map through project_blueprint_update)
- Batch 6: Directives 26-30 (project_file_read through project_subtask_create)
- Batch 7: Directives 31-35 (project_item_create through project_sidequest_complete)
- Batch 8: Directives 36-37 (project_milestone_complete, aifp_help)

---

## Next Steps After This File

1. Update directives-fp-core.json (unique function names, returns field)
2. Update directives-fp-aux.json (types_functions junction, ADT creation)
3. Create new reservation directives
4. Update corresponding .md files
5. Sync to database with sync-directives.py

---

**Estimated Time to Complete**: 1 hour
**Priority**: High
**Complexity**: Low (mostly simple query fixes)

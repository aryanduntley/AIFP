# Recommendation: Remove fp_call_graph_generation Directive

**Date**: 2025-12-14
**Issue**: Directive references non-existent database table
**Status**: Awaiting decision

---

## Problem

`fp_call_graph_generation` directive documents SQL operations for a `call_graph` table that **does not exist** in production schema.

```sql
-- From fp_call_graph_generation.md
CREATE TABLE IF NOT EXISTS call_graph (...)
INSERT INTO call_graph (caller_function_id, callee_function_id, ...)
```

**Production schema** (`src/aifp/database/schemas/project.sql`) **does NOT have** a `call_graph` table.

---

## What Production Schema Actually Has

**`interactions` table** (project.sql line 94-103):
```sql
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_function_id INTEGER NOT NULL,
    target_function_id INTEGER NOT NULL,
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('call', 'chain', 'borrow', 'compose', 'pipe')),
    description TEXT,
    ...
);
```

This table **already handles function call tracking** with type='call'.

---

## Overlap with fp_dependency_tracking

**fp_dependency_tracking.md** (another FP directive) **already does everything fp_call_graph_generation does:**

### fp_dependency_tracking handles:
- ✅ Analyzes function call relationships
- ✅ Detects circular dependencies
- ✅ Tracks which functions call which other functions
- ✅ Stores in `interactions` table (correct table)
- ✅ Impact analysis
- ✅ Change tracking

### fp_call_graph_generation tries to do:
- ❌ Analyzes function call relationships (duplicate)
- ❌ Detects circular dependencies (duplicate)
- ❌ Stores in `call_graph` table (doesn't exist!)
- ❌ Visualization (not implemented anywhere)

**These are "sister directives"** per fp_dependency_tracking.md - meaning they overlap/duplicate functionality.

---

## Usage Analysis

### Defined In:
- `docs/directives-json/directives-fp-core.json` line 1309
- `src/aifp/reference/directives/fp_call_graph_generation.md`

### Referenced By:
- **fp_dependency_tracking.md** - mentions as "sister directive" (soft reference, not hard dependency)
- Intent keywords: "call graph", "dependency map"

### Dependencies:
- **None** - no other directives depend on it
- **Removal would NOT break** any directive chains

---

## Recommendation: REMOVE

### Why Remove (Not Modify):

1. **Redundant** - fp_dependency_tracking already does everything
2. **Wrong Schema** - references non-existent table
3. **No Dependencies** - nothing breaks if removed
4. **Cleaner** - reduces directive count from 125 to 124
5. **Less Confusion** - one directive for function dependencies, not two

### Alternative (Modify):

Could update SQL to use `interactions` table instead of `call_graph`, BUT:
- Still redundant with fp_dependency_tracking
- Two directives doing the same thing confuses AI
- "Sister directives" = design smell (should be one directive)

---

## Removal Plan

### Step 1: Update fp_dependency_tracking.md

Remove the "sister directive" reference:

```markdown
## Related Directives

### FP Directives
- ~~**fp_call_graph_generation**: Sister directive focused on graph generation~~
- **fp_purity**: Pure functions simplify dependency reasoning
```

Also remove this section:
```markdown
### With `fp_call_graph_generation`
Complementary directive for visual graph generation.
```

### Step 2: Remove from directives-fp-core.json

Delete lines 1309-1348 (entire fp_call_graph_generation directive definition)

### Step 3: Remove MD file

```bash
rm /home/eveningb4dawn/Desktop/Projects/AIFP/src/aifp/reference/directives/fp_call_graph_generation.md
```

### Step 4: Update DIRECTIVES_QUICK_REF.md

Remove line:
```
| `fp_call_graph_generation` | directives-fp-core.json | 1309 |
```

Update count: `Total directives: 125` → `Total directives: 124`

### Step 5: Update SQL_CLEANUP_NEEDED.md

Remove from checklist (no longer relevant)

---

## Alternative: Keep as Documentation Only

If you want to keep the concepts:

1. **Merge content** into fp_dependency_tracking.md
2. Keep the "call graph" terminology and examples
3. Use `interactions` table throughout
4. Have ONE directive that handles all function dependency tracking

This would involve:
- Copy useful examples from fp_call_graph_generation.md
- Paste into fp_dependency_tracking.md
- Update all SQL to use `interactions` table
- Delete fp_call_graph_generation entirely

---

## Impact Assessment

### If Removed:
- ✅ No broken dependencies
- ✅ Reduced confusion (one source of truth for function tracking)
- ✅ Cleaner directive set (124 instead of 125)
- ⚠️ Need to update intent keywords in fp_dependency_tracking to include "call graph"

### If Kept and Modified:
- ⚠️ Still have two directives doing same thing
- ⚠️ Need to update all SQL examples
- ⚠️ Need to clarify difference vs. fp_dependency_tracking

---

## Recommendation: REMOVE

**Reason**: Redundant directive with incorrect schema. Functionality fully covered by fp_dependency_tracking.

**Action Items**:
1. Remove from directives-fp-core.json
2. Delete MD file
3. Update fp_dependency_tracking.md (remove sister reference)
4. Update quick reference docs
5. Update intent keywords in fp_dependency_tracking to include "call graph", "dependency map"

---

**Decision needed from user**: Remove or Modify?

# Global State Management & DRY Updates

**Date**: 2026-01-15
**Status**: Complete

## Summary

Updated AIFP system prompt and FP directives to clarify global state management and DRY principles. Key changes reflect that:
1. Read-only global constants are **encouraged** (not just tolerated)
2. State database pattern provides FP-compliant mutable state management
3. DRY section compacted while retaining essential guidance

---

## Changes Made

### 1. System Prompt (`sys-prompt/aifp_system_prompt.txt`)

#### Section 1: Global Constants - Extensive Use Encouraged (Lines 129-147)

**Before**: Simple exception for read-only constants
**After**: Comprehensive guidance encouraging extensive use

**New Content**:
- Configuration: DATABASE_URL, API_KEYS, MAX_RETRIES, TIMEOUT
- Lookup tables: VALID_STATUSES = frozenset(['pending', 'completed'])
- Paths: PROJECT_DB_DIR, STATE_DB_PATH, BACKUP_DIR
- Business rules: MAX_CART_ITEMS, PAYMENT_TIMEOUT, RATE_LIMIT

#### Section 2: Runtime State Management (Lines 137-211)

**New Pattern Added**: State Database for Runtime Mutable State

**Key Points**:
- ⚠️ Mutable global variables strongly discouraged (not "forbidden")
- ✅ Use lightweight SQLite database (state.db, runtime.db, cache.db)
- ✅ Globally accessible helper modules (e.g., `from state.operations import track_session`)
- ✅ State mutations isolated in effect functions
- ✅ Thread-safe, auditable, FP-compliant

**Example Added**:
```python
STATE_DB_PATH: Final[str] = ".state/runtime.db"

def track_progress(job_id: str, progress: int) -> Result[None, str]:
    """Effect: Update job progress in state database."""
    conn = sqlite3.connect(STATE_DB_PATH)
    # ... explicit state mutation
```

**Use Cases**:
- Session tracking
- Rate limiting
- Background job progress
- Distributed locks
- Temporary caches
- Metrics/analytics

#### Section 3: DRY Principle - Compacted (Lines 313-347)

**Before**: ~75 lines with extensive explanation
**After**: ~35 lines with essential guidance (47% reduction)

**Retained**:
- Why DRY matters (token waste: 48x reduction)
- Extract when / Don't extract when rules
- Scope levels (Global, Category, File)
- Key example (connection pooling)

**Removed**:
- Redundant explanations
- Verbose examples
- Duplicate decision rules

---

### 2. FP Directive: `fp_state_elimination.md`

#### Purpose Section (Lines 19-31)

**Before**: "Eliminate all forms of hidden state"
**After**: "Eliminate hidden **mutable** state"

**Added Clarification**:

**What's ALLOWED (FP-compliant)**:
- ✅ Read-only global constants (Final in Python, const in JS/TS)
- ✅ Lookup tables (frozenset, immutable tuples, frozen dataclasses)
- ✅ State database pattern (explicit mutable state in SQLite)

**Refactoring approach**: Convert **mutable** global state into explicit parameter passing OR state database pattern.

#### Edge Case 1: Updated (Lines 454-500)

**Before**: "Constant vs Mutable Global"
**After**: "Read-Only Constants vs Mutable State"

**New Examples**:
1. Read-only constants (ENCOURAGED)
2. Mutable globals (must refactor)
3. **State database pattern** (NEW - FP-compliant alternative)

**Code Example Added**:
```python
# ✅ Mutable state via state database (FP-compliant)
STATE_DB_PATH: Final[str] = ".state/runtime.db"

def track_session(session_id: str, user_id: int) -> Result[None, str]:
    """Effect: Explicit state mutation in database."""
    conn = sqlite3.connect(STATE_DB_PATH)
    try:
        conn.execute("INSERT OR REPLACE INTO sessions VALUES (?, ?)", (session_id, user_id))
        conn.commit()
        return Ok(None)
    except Exception as e:
        return Err(str(e))
    finally:
        conn.close()
```

#### New Compliant Example (Lines 311-379)

**Added**: "Using State Database for Runtime Mutable State"

**Shows**:
- Initial code with mutable global (active_jobs = {})
- AI workflow (scan_scope → convert_to_state_database)
- Refactored code with state.db pattern
- Benefits: Thread-safe, auditable, FP-compliant

---

### 3. FP Directive: `fp_no_oop.md`

#### Branch 1: DRY Note Added (Line 89)

**Added**: "**Apply DRY principle**: Extract common utilities to `_common.py` if used across multiple files"

**Context**: When refactoring classes to functions, AI should extract common utilities to avoid duplication.

---

## Philosophy Changes

### Before

- Mutable globals: **Forbidden**
- Constants: Exception/tolerated
- DRY: Thorough explanation but verbose
- State management: Implicit (parameter passing only)

### After

- Mutable globals: **Strongly discouraged** (with FP-compliant alternative)
- Constants: **Extensively encouraged**
- DRY: Compact guidance, same rules
- State management: **Explicit via state database pattern**

---

## Key Insights

### 1. State Database Pattern Benefits

| Benefit | Explanation |
|---------|-------------|
| **FP-Compliant** | State mutations isolated in effect functions |
| **Thread-Safe** | SQLite handles concurrent access |
| **Auditable** | All state changes logged in database |
| **Testable** | Use test state database, easy to reset |
| **Explicit** | State access visible in function signatures |
| **Garbage Collected** | Can clear old state with SQL DELETE |
| **Persistent** | Survives crashes/restarts (optional - can use in-memory) |

### 2. When to Use Each Pattern

| State Type | Solution |
|------------|----------|
| Configuration | Read-only global constants (Final) |
| Lookup tables | Immutable globals (frozenset, tuple) |
| Persistent state | Main database (PostgreSQL/MySQL) |
| AIFP tracking | project.db, user_preferences.db |
| Runtime state | **state.db** (sessions, rate limits, jobs) |
| Temporary cache | **state.db** or Redis |
| Function params | Passed explicitly (standard FP) |

### 3. E-Commerce Example

**Q**: "Would preventing mutable globals cause issues in large projects?"
**A**: **No! It actually solves problems.**

| Concern | Reality |
|---------|---------|
| Repeat code? | No - Use read-only globals for config, extract utilities to _common.py |
| Hard to track state? | No - State is **explicit** (in DB, Redis, or function params) - easier to track! |
| Performance? | No - Use external cache (Redis) for hot data, connection pools for DB |
| Testing? | **Easier!** - No globals to reset, just pass test DB connection |
| Concurrency? | **Safer!** - No race conditions from shared mutable state |
| Debugging? | **Easier!** - All dependencies explicit in function signatures |

---

## Implementation Notes

### For Helper Functions

All helper functions should:
1. Use read-only global constants extensively (paths, config, limits)
2. Suggest state database pattern when users need runtime mutable state
3. Extract common utilities to `_common.py` (DRY principle)

### For Directives

Directives should:
1. Reference state database pattern when detecting mutable globals
2. Allow Final constants without refactoring
3. Suggest appropriate scope level for extracted utilities

---

## Next Steps

1. ✅ System prompt updated
2. ✅ fp_state_elimination.md updated
3. ✅ fp_no_oop.md updated
4. ⏳ Continue helper function implementation with these patterns
5. ⏳ Create example `state.db` schema and helper module
6. ⏳ Update HELPER_IMPLEMENTATION_PLAN.md if needed

---

## Files Modified

1. `sys-prompt/aifp_system_prompt.txt`
   - Lines 129-147: Global constants section
   - Lines 137-211: State database pattern added
   - Lines 313-347: DRY section compacted

2. `src/aifp/reference/directives/fp_state_elimination.md`
   - Lines 19-31: Purpose updated
   - Lines 311-379: State database example added
   - Lines 454-500: Edge case updated

3. `src/aifp/reference/directives/fp_no_oop.md`
   - Line 89: DRY note added

---

**Conclusion**: AIFP now has clear, practical guidance for global constants and runtime state management that maintains FP principles while solving real-world needs.

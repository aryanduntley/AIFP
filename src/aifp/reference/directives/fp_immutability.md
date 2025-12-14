# Directive: fp_immutability

**Type**: FP Core
**Level**: 1 (Critical)
**Parent Directive**: None
**Priority**: CRITICAL - Required for all FP compliance

---

## Purpose

The `fp_immutability` directive enforces immutable data structures throughout the codebase - a foundational principle of functional programming. Immutability means that once a value is created, it cannot be changed. Instead of modifying existing data, new data structures are created with the desired changes.

This directive is **foundational to AIFP** - it ensures referential transparency and predictable state management. Immutable data enables:
- **Predictability**: Values never change unexpectedly
- **Thread Safety**: No race conditions since nothing mutates
- **Time Travel**: Easy undo/redo since previous states are preserved
- **Easier Reasoning**: No need to track when/where data changes
- **Cache Validity**: Cached values never become stale
- **Safe Sharing**: Data can be safely passed around without defensive copying

When applied, this directive analyzes code for:
1. **Variable reassignment** (e.g., `x = x + 1`)
2. **Mutable data structure operations** (e.g., `list.append()`, `dict[key] = value`)
3. **In-place modifications** (e.g., `list.sort()`, `dict.update()`)
4. **Mutable default arguments** (e.g., `def func(data=[]):`)

If violations are detected, the directive refactors code to use immutable patterns or prompts the user for guidance.

---

## When to Apply

This directive applies when:
- **Writing new functions** - All new code must use immutable data
- **Refactoring existing code** - Converting mutable patterns to immutable
- **Compliance checking** - Verifying project-wide immutability
- **Code review** - Validating immutability before merge
- **Called by other directives**:
  - `project_file_write` - Validates immutability before writing files
  - `project_compliance_check` - Scans all functions for immutability
  - `fp_purity` - Purity and immutability often checked together
  - `fp_no_reassignment` - Enforces single-assignment semantics

---

## Workflow

### Trunk: analyze_variables

Analyzes all variables and data structures to ensure immutability.

**Steps**:
1. **Scan variable declarations** - Identify all variable bindings
2. **Check for reassignments** - Detect variables assigned multiple times
3. **Analyze data structures** - Identify lists, dicts, sets, objects
4. **Check for mutations** - Detect operations that modify data in place
5. **Evaluate patterns** - Identify mutable patterns (append, update, etc.)
6. **Classify violations** - Categorize immutability violations by severity

### Branches

**Branch 1: If mutation_found**
- **Then**: `replace_with_copy`
- **Details**: Replace mutations with copy-and-modify patterns
  - Replace `items.append(x)` with `items_new = items + [x]`
  - Replace `data[key] = value` with `data_new = {**data, key: value}`
  - Replace `items.sort()` with `items_sorted = sorted(items)`
  - Replace `items.extend(more)` with `items_new = items + more`
- **Result**: Returns refactored code with immutable updates

**Branch 2: If mutable_structure_detected**
- **Then**: `replace_with_tuple_or_const`
- **Details**: Replace mutable containers with immutable equivalents
  - Replace `list` with `tuple` (when order matters, no modification needed)
  - Replace `dict` with `frozendict` or tuple of pairs (when immutable keys needed)
  - Replace `set` with `frozenset`
  - Use dataclasses with `frozen=True` for structured data
- **Result**: Returns code using immutable data structures

**Fallback**: `mark_as_immutable`
- **Details**: Code already follows immutability
  - No reassignments detected
  - No mutations detected
  - Immutable data structures used
- **Result**: Function passes immutability check

---

## Examples

### ✅ Compliant Code

**Immutable List Update:**
```python
def add_item_immutable(items: tuple[str, ...], new_item: str) -> tuple[str, ...]:
    """Add item immutably. Returns new tuple."""
    return items + (new_item,)

# Usage
original = ("apple", "banana")
updated = add_item_immutable(original, "cherry")
# original unchanged: ("apple", "banana")
# updated: ("apple", "banana", "cherry")
```

**Why Compliant**:
- Uses immutable tuple instead of list
- Creates new tuple with `+` operator
- Original data unchanged

---

**Immutable Dictionary Update:**
```python
def update_config(config: dict, key: str, value: any) -> dict:
    """Update config immutably. Returns new dict."""
    return {**config, key: value}

# Usage
original = {"theme": "dark", "lang": "en"}
updated = update_config(original, "theme", "light")
# original unchanged: {"theme": "dark", "lang": "en"}
# updated: {"theme": "light", "lang": "en"}
```

**Why Compliant**:
- Uses spread operator `{**config, key: value}` to create new dict
- Original dict unchanged
- Returns new dict with updated value

---

**Immutable Data Structure (Dataclass):**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    """Immutable user data."""
    id: int
    name: str
    email: str

def update_user_email(user: User, new_email: str) -> User:
    """Update email immutably. Returns new User."""
    return User(id=user.id, name=user.name, email=new_email)

# Usage
original = User(id=1, name="Alice", email="alice@old.com")
updated = update_user_email(original, "alice@new.com")
# original unchanged: User(id=1, name="Alice", email="alice@old.com")
# updated: User(id=1, name="Alice", email="alice@new.com")
```

**Why Compliant**:
- Uses `frozen=True` to make dataclass immutable
- Creates new instance for updates
- Original instance unchanged

---

### ❌ Non-Compliant Code

**Mutable List Operations:**
```python
# ❌ VIOLATION: Mutates list in place
def add_items_mutable(items: list[str], new_items: list[str]) -> list[str]:
    items.extend(new_items)  # ← Mutation
    return items

# Caller's data is modified
original = ["apple", "banana"]
result = add_items_mutable(original, ["cherry"])
# original is now: ["apple", "banana", "cherry"] ← UNEXPECTED MUTATION
```

**Why Non-Compliant**:
- Mutates input parameter `items`
- Caller's data modified unexpectedly
- Not immutable

**Refactored (Immutable):**
```python
def add_items_immutable(items: tuple[str, ...], new_items: tuple[str, ...]) -> tuple[str, ...]:
    """Add items immutably. Returns new tuple."""
    return items + new_items

# Caller's data unchanged
original = ("apple", "banana")
result = add_items_immutable(original, ("cherry",))
# original unchanged: ("apple", "banana")
# result: ("apple", "banana", "cherry")
```

---

**Variable Reassignment:**
```python
# ❌ VIOLATION: Variable reassignment
def calculate_total_mutable(prices: list[float]) -> float:
    total = 0.0
    for price in prices:
        total = total + price  # ← Reassignment
    return total
```

**Why Non-Compliant**:
- Variable `total` reassigned in loop
- Violates immutability (even though locally scoped)

**Refactored (Immutable):**
```python
def calculate_total_immutable(prices: tuple[float, ...]) -> float:
    """Calculate total immutably."""
    return sum(prices)

# Or with explicit recursion
def calculate_total_recursive(prices: tuple[float, ...]) -> float:
    """Calculate total via recursion."""
    if not prices:
        return 0.0
    return prices[0] + calculate_total_recursive(prices[1:])
```

---

**Dictionary Mutation:**
```python
# ❌ VIOLATION: Mutates dict in place
def add_user_mutable(users: dict, user_id: int, name: str) -> dict:
    users[user_id] = name  # ← Mutation
    return users

# Caller's dict is modified
original = {1: "Alice", 2: "Bob"}
result = add_user_mutable(original, 3, "Charlie")
# original is now: {1: "Alice", 2: "Bob", 3: "Charlie"} ← UNEXPECTED
```

**Why Non-Compliant**:
- Mutates input parameter `users`
- Side effect on caller's data

**Refactored (Immutable):**
```python
def add_user_immutable(users: dict, user_id: int, name: str) -> dict:
    """Add user immutably. Returns new dict."""
    return {**users, user_id: name}

# Caller's dict unchanged
original = {1: "Alice", 2: "Bob"}
result = add_user_immutable(original, 3, "Charlie")
# original unchanged: {1: "Alice", 2: "Bob"}
# result: {1: "Alice", 2: "Bob", 3: "Charlie"}
```

---

## Edge Cases

### Edge Case 1: Sorting Collections

**Issue**: `list.sort()` mutates in place

**Handling**:
```python
# ❌ Mutable (in-place sort)
def sort_items_mutable(items: list[str]) -> list[str]:
    items.sort()  # ← Mutation
    return items

# ✅ Immutable (returns new sorted collection)
def sort_items_immutable(items: tuple[str, ...]) -> tuple[str, ...]:
    """Sort items immutably."""
    return tuple(sorted(items))
```

**Directive Action**: Replace `.sort()` with `sorted()`, use tuples.

---

### Edge Case 2: Mutable Default Arguments

**Issue**: Mutable defaults are shared across calls

**Handling**:
```python
# ❌ Dangerous (mutable default)
def add_item_bad(item: str, items: list = []) -> list:
    items.append(item)  # ← Mutates shared default
    return items

# Calls share the same list!
result1 = add_item_bad("apple")  # ["apple"]
result2 = add_item_bad("banana")  # ["apple", "banana"] ← UNEXPECTED

# ✅ Immutable pattern (None + tuple)
def add_item_good(item: str, items: tuple[str, ...] | None = None) -> tuple[str, ...]:
    """Add item immutably."""
    if items is None:
        items = ()
    return items + (item,)

result1 = add_item_good("apple")  # ("apple",)
result2 = add_item_good("banana")  # ("banana",)
```

**Directive Action**: Never use mutable defaults. Use `None` and create new immutable structures.

---

### Edge Case 3: Nested Structure Updates

**Issue**: Deep nesting makes immutable updates verbose

**Handling**:
```python
# ❌ Mutable nested update
config = {"user": {"profile": {"name": "Alice"}}}
config["user"]["profile"]["name"] = "Bob"  # ← Mutation

# ✅ Immutable nested update (verbose but correct)
def update_nested_name(config: dict, new_name: str) -> dict:
    """Update nested name immutably."""
    return {
        **config,
        "user": {
            **config["user"],
            "profile": {
                **config["user"]["profile"],
                "name": new_name
            }
        }
    }

# ✅ Better: Use immutable dataclasses with helper
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Profile:
    name: str

@dataclass(frozen=True)
class User:
    profile: Profile

@dataclass(frozen=True)
class Config:
    user: User

def update_profile_name(config: Config, new_name: str) -> Config:
    """Update profile name immutably."""
    new_profile = replace(config.user.profile, name=new_name)
    new_user = replace(config.user, profile=new_profile)
    return replace(config, user=new_user)
```

**Directive Action**: Recommend frozen dataclasses with `replace()` for nested updates.

---

### Edge Case 4: Performance Concerns

**Issue**: Creating new collections every time seems inefficient

**Handling**:
- **Structural sharing**: Python internally optimizes immutable structures
- **Lazy evaluation**: Use generators and iterators to avoid materializing
- **Batching**: Accumulate changes, apply once
- **Acceptable tradeoff**: Clarity and correctness > micro-optimization

```python
# Efficient immutable pattern with generator
def process_items_lazy(items: tuple[int, ...]) -> tuple[int, ...]:
    """Process items immutably with lazy evaluation."""
    return tuple(x * 2 for x in items if x > 0)
```

**Directive Action**: Encourage immutability first, optimize if profiling shows bottleneck.

---

## Related Directives

- **Depends On**: None (foundational directive)
- **Works With**:
  - `fp_purity` - Immutability supports purity (pure functions can't mutate)
  - `fp_no_reassignment` - Enforces single-assignment (no variable reassignment)
  - `fp_const_refactoring` - Promotes constants over mutable variables
- **Called By**:
  - `project_file_write` - Validates immutability before file writes
  - `project_compliance_check` - Project-wide immutability verification
  - `fp_no_oop` - OOP refactoring often introduces mutable state
- **Escalates To**:
  - `fp_language_standardization` - For language-specific immutable patterns
  - `fp_ownership_safety` - For Rust-style borrow checking

---

## Helper Functions

Query `get_helpers_for_directive()` to discover this directive's available helpers.
See system prompt for usage.
---

## Database Operations

This directive updates the following tables:

- **`functions`**: Updates functions with immutability analysis results
- **`notes`**: Logs immutability violations with `note_type = 'compliance'`

---

## Testing

How to verify this directive is working:

1. **Write mutable code** → Directive detects and refactors
   ```python
   # Input (mutable)
   def add(items: list, x): items.append(x); return items

   # Expected output (immutable)
   def add(items: tuple, x): return items + (x,)
   ```

2. **Write immutable code** → Directive marks compliant
   ```python
   def add(items: tuple, x): return items + (x,)
   # ✅ Already immutable, no refactoring needed
   ```

3. **Test with nested structures** → Verify deep immutability
   ```python
   config = {"db": {"host": "localhost"}}
   # Directive ensures updates create new dicts, not mutations
   ```

---

## Common Mistakes

- ❌ **Using mutable default arguments** - `def func(items=[]):` creates shared state
- ❌ **Assuming tuples guarantee immutability** - Tuples of mutable objects are not fully immutable
- ❌ **Modifying collections in loops** - `.append()`, `.extend()` mutate
- ❌ **Using `list.sort()`** - Use `sorted()` instead
- ❌ **Dict/set mutations** - `dict[key] = val`, `set.add(x)` mutate

---

## Roadblocks and Resolutions

### Roadblock 1: variable_reassignment
**Issue**: Variable reassigned in loop or conditional
**Resolution**: Use new variable binding or functional alternatives (recursion, reduce)

### Roadblock 2: mutable_container
**Issue**: Using `list`, `dict`, or `set`
**Resolution**: Replace with immutable type (tuple, frozenset, frozen dataclass)

---

## References

- [Python Immutability Patterns](https://docs.python.org/3/library/dataclasses.html#frozen-instances)

---

*Part of AIFP v1.0 - Critical FP Core directive for immutable data structures*

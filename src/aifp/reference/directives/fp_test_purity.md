# fp_test_purity

## Purpose

The `fp_test_purity` directive ensures test code follows functional programming principles by validating test purity, eliminating test state mutation, and enforcing deterministic test behavior. It promotes property-based testing, pure test fixtures, and immutable test data that enable reliable, repeatable, and parallelizable test suites. Pure tests are easier to understand, debug, and maintain while providing stronger guarantees about code correctness.

**Category**: Testing
**Type**: FP Auxiliary
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_test_purity`**: Examine test code for purity violations and test anti-patterns.

### Branches

1. **`test_setup_mutation`** → **`convert_to_pure_fixtures`**
   - **Condition**: Test setup mutates shared state or uses mutable fixtures
   - **Action**: Convert to pure fixture functions returning fresh immutable data
   - **Details**: Each test gets independent data, no shared mutable state
   - **Output**: Pure test fixtures

2. **`test_assertion_side_effects`** → **`isolate_effects_from_assertions`**
   - **Condition**: Test assertions have side effects or depend on execution order
   - **Action**: Separate effects from assertions, ensure independence
   - **Details**: Assertions should be pure predicates
   - **Output**: Pure assertions

3. **`property_based_opportunity`** → **`suggest_property_tests`**
   - **Condition**: Example-based tests that could be property-based
   - **Action**: Suggest property-based test using hypothesis/fast-check
   - **Details**: Test general properties rather than specific examples
   - **Output**: Property-based test recommendation

4. **`test_isolation_check`** → **`validate_test_independence`**
   - **Condition**: Tests may depend on execution order or shared state
   - **Action**: Verify each test can run independently in any order
   - **Details**: Tests must be order-independent and parallelizable
   - **Output**: Test isolation validation

5. **Fallback** → **`mark_as_compliant`**
   - **Condition**: Tests follow FP principles
   - **Action**: Mark as pure and parallelizable

### Error Handling
- **On failure**: Log test purity violations with suggested fixes
- **Low confidence** (< 0.7): Request manual review of test patterns

---

## Refactoring Strategies

### Strategy 1: Pure Test Fixtures

Test fixtures should be pure functions returning fresh immutable data.

**Before (Mutable Shared Fixture)**:
```python
import pytest

# Mutable shared state - DANGER!
test_users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

def test_filter_active_users():
    # Mutates shared fixture
    test_users[0]["active"] = True
    result = filter_active_users(test_users)
    assert len(result) == 1

def test_count_users():
    # Depends on state from previous test!
    assert len(test_users) == 2  # May fail if test order changes
```

**After (Pure Fixtures)**:
```python
from typing import Iterator
from dataclasses import dataclass

@dataclass(frozen=True)
class User:
    """Immutable user for testing."""
    id: int
    name: str
    active: bool = False

def create_test_users() -> tuple[User, ...]:
    """Pure fixture: returns fresh immutable users each call."""
    return (
        User(id=1, name="Alice", active=False),
        User(id=2, name="Bob", active=False),
    )

def test_filter_active_users():
    # Each test gets fresh independent data
    users = create_test_users()
    active_users = (
        User(id=users[0].id, name=users[0].name, active=True),
    ) + users[1:]

    result = filter_active_users(active_users)

    assert len(result) == 1
    assert result[0].name == "Alice"

def test_count_users():
    # Independent data, no shared state
    users = create_test_users()
    assert len(users) == 2
```

**Pure Fixture Principles**:
- Return fresh data on each call
- Use immutable data structures
- No shared mutable state
- No global variables
- Tests can run in any order

---

### Strategy 2: Property-Based Testing

Property-based tests validate general properties rather than specific examples.

**Before (Example-Based Tests)**:
```python
def test_double_specific_cases():
    assert double(0) == 0
    assert double(5) == 10
    assert double(-3) == -6
    assert double(100) == 200
```

**After (Property-Based Tests)**:
```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_double_property_idempotent(n: int):
    """Property: double(n) should always be n * 2."""
    assert double(n) == n * 2

@given(st.integers())
def test_double_property_symmetry(n: int):
    """Property: double(-n) == -double(n)."""
    assert double(-n) == -double(n)

@given(st.integers(), st.integers())
def test_double_property_distributive(a: int, b: int):
    """Property: double(a + b) == double(a) + double(b)."""
    assert double(a + b) == double(a) + double(b)
```

**Property-Based Testing Benefits**:
- Tests many more cases automatically
- Finds edge cases developers miss
- Documents mathematical properties
- More confidence in correctness

---

### Strategy 3: Pure Test Data Builders

Test data builders should be pure functions, not classes with mutable state.

**Before (Mutable Builder Pattern)**:
```python
# OOP test builder with mutation
class UserBuilder:
    def __init__(self):
        self.user = {"id": 0, "name": "", "active": False}

    def with_id(self, id):
        self.user["id"] = id  # Mutation!
        return self

    def with_name(self, name):
        self.user["name"] = name  # Mutation!
        return self

    def build(self):
        return self.user  # Returns mutable dict

# Usage
user = UserBuilder().with_id(1).with_name("Alice").build()
```

**After (Pure Functional Builder)**:
```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class User:
    id: int
    name: str
    active: bool = False

def create_user(
    id: int = 0,
    name: str = "",
    active: bool = False
) -> User:
    """Pure factory: returns immutable user."""
    return User(id=id, name=name, active=active)

def with_id(user: User, id: int) -> User:
    """Pure: returns new user with updated id."""
    return replace(user, id=id)

def with_name(user: User, name: str) -> User:
    """Pure: returns new user with updated name."""
    return replace(user, name=name)

def with_active(user: User, active: bool) -> User:
    """Pure: returns new user with updated active status."""
    return replace(user, active=active)

# Usage - pure functional pipeline
user = with_name(with_id(create_user(), 1), "Alice")

# Or use direct constructor
user = create_user(id=1, name="Alice", active=True)
```

---

### Strategy 4: Pure Test Assertions

Assertions should be pure predicates without side effects.

**Before (Impure Assertions)**:
```python
def test_user_saved():
    user = User(id=1, name="Alice")

    # Side effect in assertion
    result = save_user_to_db(user)  # I/O during test!

    assert result is True
    assert get_user_from_db(1).name == "Alice"  # Another I/O!
```

**After (Pure Assertions with Test Doubles)**:
```python
from typing import Protocol

class UserRepository(Protocol):
    """Repository interface for user storage."""

    def save(self, user: User) -> bool:
        ...

    def get(self, user_id: int) -> User | None:
        ...

class InMemoryUserRepository:
    """Pure in-memory repository for testing."""

    def __init__(self):
        self._users: dict[int, User] = {}

    def save(self, user: User) -> bool:
        """Pure: updates internal dict, returns success."""
        self._users[user.id] = user
        return True

    def get(self, user_id: int) -> User | None:
        """Pure: reads from internal dict."""
        return self._users.get(user_id)

def test_user_saved():
    # Pure: no external I/O
    repo = InMemoryUserRepository()
    user = create_user(id=1, name="Alice")

    # Pure operation on test double
    result = repo.save(user)

    # Pure assertions
    assert result is True

    saved_user = repo.get(1)
    assert saved_user is not None
    assert saved_user.name == "Alice"
```

---

### Strategy 5: Deterministic Test Randomness

Tests needing randomness should use seeded generators for reproducibility.

**Before (Non-Deterministic Randomness)**:
```python
import random

def test_shuffle_maintains_elements():
    # Non-deterministic - may fail randomly!
    data = [1, 2, 3, 4, 5]
    shuffled = shuffle_list(data)

    assert sorted(shuffled) == sorted(data)
    assert shuffled != data  # May fail if shuffle returns original order
```

**After (Deterministic Seeded Randomness)**:
```python
import random
from hypothesis import given, strategies as st, seed

def test_shuffle_maintains_elements_deterministic():
    # Seeded random for reproducibility
    rng = random.Random(42)
    data = [1, 2, 3, 4, 5]

    shuffled = shuffle_list_with_rng(data, rng)

    # Always same result with same seed
    assert sorted(shuffled) == sorted(data)

@seed(12345)  # Hypothesis seed for reproducibility
@given(st.lists(st.integers(), min_size=1))
def test_shuffle_property_based(data: list[int]):
    """Property: shuffle maintains all elements."""
    shuffled = shuffle_list(data)
    assert sorted(shuffled) == sorted(data)
```

---

## Examples

### Example 1: Pure Integration Test

**Before (Impure Integration Test)**:
```python
def test_user_workflow():
    # Global database state - impure!
    db.clear()
    db.create_table("users")

    # Side effects
    user_id = db.insert_user({"name": "Alice"})
    user = db.get_user(user_id)

    assert user["name"] == "Alice"

    # More side effects
    db.update_user(user_id, {"name": "Bob"})
    updated = db.get_user(user_id)

    assert updated["name"] == "Bob"
```

**After (Pure Integration Test)**:
```python
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class UserStore:
    """Immutable user store for testing."""
    users: dict[int, User]

    def insert(self, user: User) -> tuple['UserStore', int]:
        """Pure: returns new store with user added."""
        new_id = max(self.users.keys(), default=0) + 1
        new_users = {**self.users, new_id: user}
        return (UserStore(users=new_users), new_id)

    def get(self, user_id: int) -> User | None:
        """Pure: reads from internal dict."""
        return self.users.get(user_id)

    def update(self, user_id: int, user: User) -> 'UserStore':
        """Pure: returns new store with updated user."""
        if user_id not in self.users:
            return self
        new_users = {**self.users, user_id: user}
        return UserStore(users=new_users)

def test_user_workflow_pure():
    # Pure: no external state
    store = UserStore(users={})
    user = create_user(name="Alice")

    # Pure insertion
    store, user_id = store.insert(user)

    # Pure assertion
    retrieved = store.get(user_id)
    assert retrieved is not None
    assert retrieved.name == "Alice"

    # Pure update
    updated_user = replace(retrieved, name="Bob")
    store = store.update(user_id, updated_user)

    # Pure assertion
    final_user = store.get(user_id)
    assert final_user.name == "Bob"
```

---

## Edge Cases

### Edge Case 1: Time-Dependent Tests
**Scenario**: Tests depend on current time or dates
**Issue**: Non-deterministic test behavior
**Handling**:
- Inject time as parameter
- Use fixed time in tests
- Mock time sources

**Example**:
```python
from datetime import datetime, timezone

def is_business_hours(current_time: datetime) -> bool:
    """Pure: takes time as parameter."""
    hour = current_time.hour
    return 9 <= hour < 17

def test_business_hours_deterministic():
    # Fixed time for deterministic test
    morning = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)
    evening = datetime(2025, 1, 1, 19, 0, tzinfo=timezone.utc)

    assert is_business_hours(morning) == True
    assert is_business_hours(evening) == False
```

### Edge Case 2: File System Tests
**Scenario**: Tests interact with file system
**Issue**: Side effects, cleanup required
**Handling**:
- Use in-memory file system
- Pure functions with file content as data
- Dependency injection

### Edge Case 3: Network Tests
**Scenario**: Tests make network requests
**Issue**: Non-deterministic, slow, external dependencies
**Handling**:
- Use test doubles (mocks, stubs)
- Record/replay for integration tests
- Pure functions with injected HTTP client

### Edge Case 4: Random Test Data
**Scenario**: Tests generate random data
**Issue**: Non-reproducible failures
**Handling**:
- Use seeded random generators
- Property-based testing with seeds
- Fixed examples for regression tests

### Edge Case 5: Concurrent Tests
**Scenario**: Testing concurrent or parallel code
**Issue**: Race conditions, non-determinism
**Handling**:
- Test concurrent logic with deterministic execution
- Use property-based testing for concurrency
- Control thread interleaving in tests

---

## Database Operations

### Record Test Purity Metadata

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Related Directives

### FP Directives
- **fp_purity**: Test code should be pure like production code
- **fp_immutability**: Test data should be immutable
- **fp_parallel_purity**: Pure tests can run in parallel safely

### Project Directives
- **project_compliance_check**: Validates test purity
- **project_update_db**: Records test metadata

---

## Helper Functions

### `analyze_test_purity(test_file) -> dict`
Analyzes test file for purity violations.

**Signature**:
```python
def analyze_test_purity(test_file: str) -> dict:
    """
    Analyzes test file for purity violations.
    Returns report with violations and suggestions.
    """
```

### `suggest_property_test(example_test) -> str`
Suggests property-based version of example test.

**Signature**:
```python
def suggest_property_test(example_test: FunctionDef) -> str:
    """
    Converts example-based test to property-based test.
    Returns property test code as string.
    """
```

---

## Testing

### Test 1: Pure Fixture Detection
```python
def test_detect_pure_fixtures():
    test_code = """
def create_test_user():
    return User(id=1, name="Alice")

def test_something():
    user = create_test_user()
    assert user.name == "Alice"
"""

    analysis = fp_test_purity.analyze(test_code)

    assert analysis.has_pure_fixtures == True
```

### Test 2: Mutable State Detection
```python
def test_detect_mutable_test_state():
    test_code = """
test_data = []  # Mutable shared state

def test_append():
    test_data.append(1)
    assert len(test_data) == 1
"""

    analysis = fp_test_purity.analyze(test_code)

    assert analysis.has_shared_mutable_state == True
    assert 'refactor_to_pure_fixtures' in analysis.suggestions
```

---

## Common Mistakes

### Mistake 1: Shared Mutable Fixtures
**Problem**: Tests share mutable fixtures causing order dependencies

**Solution**: Pure fixture functions returning fresh data

```python
# ❌ Bad: shared mutable
test_users = [User(1, "Alice")]

def test_add_user():
    test_users.append(User(2, "Bob"))
    assert len(test_users) == 2

# ✅ Good: pure fixtures
def create_test_users():
    return (User(1, "Alice"),)

def test_add_user():
    users = create_test_users()
    new_users = users + (User(2, "Bob"),)
    assert len(new_users) == 2
```

### Mistake 2: Side Effects in Setup
**Problem**: Test setup has side effects

**Solution**: Pure setup functions

```python
# ❌ Bad: side effects in setup
def setup():
    database.clear()  # Side effect!
    database.insert(test_data)

# ✅ Good: pure setup
def create_test_store():
    return InMemoryStore(data=test_data)
```

### Mistake 3: Non-Deterministic Tests
**Problem**: Tests use unseeded randomness

**Solution**: Seed random generators

```python
# ❌ Bad: non-deterministic
def test_random_selection():
    result = random_select(items)
    assert result in items

# ✅ Good: deterministic
def test_random_selection():
    rng = random.Random(42)
    result = random_select_with_rng(items, rng)
    assert result in items
```

---

## Roadblocks

### Roadblock 1: Existing Impure Test Suite
**Issue**: Large test suite with mutable state
**Resolution**: Gradual refactoring, start with new tests

### Roadblock 2: Framework Limitations
**Issue**: Testing framework encourages mutable state
**Resolution**: Abstraction layer, pure helpers on top of framework

### Roadblock 3: Performance Concerns
**Issue**: Pure fixtures seem slower (create fresh data each time)
**Resolution**: Immutable data is cheap to share, measure before optimizing

---

## Integration Points

### With `fp_purity`
Test code follows same purity principles as production code.

### With `fp_immutability`
Test data uses immutable structures.

### With `project_compliance_check`
Test purity validated during compliance checks.

---

## Intent Keywords

- `testing`
- `test purity`
- `fixtures`
- `property-based testing`
- `test independence`

---

## Confidence Threshold

**0.7** - High confidence for test purity validation.

---

## Notes

- Pure tests are more reliable
- Tests should be order-independent
- Use immutable test data
- Property-based tests find more bugs
- Seed random generators for reproducibility
- Pure fixtures return fresh data
- Tests can run in parallel if pure
- No shared mutable state between tests
- Test doubles for external dependencies
- AIFP test suites are deterministic and parallelizable


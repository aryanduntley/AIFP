# fp_api_design

## Purpose

The `fp_api_design` directive establishes functional programming design principles for public APIs, ensuring interfaces are pure, composable, and predictable. It promotes function-based APIs over class-based APIs, uses immutable data structures, explicit error handling with Result types, and designs for composition through higher-order functions. Well-designed FP APIs are easier to test, reason about, and integrate while providing stronger correctness guarantees.

**Category**: API Design
**Type**: FP Auxiliary
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_api_design`**: Review API structure for FP compliance and design quality.

### Branches

1. **`class_based_api`** → **`convert_to_function_based`**
   - **Condition**: API uses classes with methods and mutable state
   - **Action**: Refactor to pure functions with explicit data flow
   - **Details**: Replace classes with functions and immutable data structures
   - **Output**: Function-based API

2. **`exception_based_errors`** → **`convert_to_result_types`**
   - **Condition**: API uses exceptions for error handling
   - **Action**: Replace exceptions with Result/Option types
   - **Details**: Make errors explicit in function signatures
   - **Output**: Explicit error handling API

3. **`implicit_state_api`** → **`make_state_explicit`**
   - **Condition**: API has hidden state or implicit context
   - **Action**: Make all state explicit as function parameters
   - **Details**: No global state, configuration, or hidden context
   - **Output**: Explicit state API

4. **`composition_check`** → **`ensure_composability`**
   - **Condition**: API functions don't compose well
   - **Action**: Design for composition with consistent return types
   - **Details**: Enable chaining, piping, and higher-order function patterns
   - **Output**: Composable API

5. **Fallback** → **`mark_as_compliant`**
   - **Condition**: API follows FP design principles
   - **Action**: Document API patterns and usage

### Error Handling
- **On failure**: Log API design violations and provide refactoring suggestions
- **Low confidence** (< 0.7): Request manual review of API design

---

## Refactoring Strategies

### Strategy 1: Function-Based API Instead of Class-Based

Pure function APIs are simpler, more testable, and more composable than class-based APIs.

**Before (Class-Based API)**:
```python
# OOP-style API with hidden state
class UserManager:
    def __init__(self, database_url: str):
        self.db = connect_to_database(database_url)  # Hidden state
        self.cache = {}  # Mutable cache

    def get_user(self, user_id: int) -> dict:
        """Hidden I/O and mutation."""
        if user_id in self.cache:
            return self.cache[user_id]

        user = self.db.fetch_user(user_id)  # Hidden I/O
        self.cache[user_id] = user  # Mutation!
        return user

    def update_user(self, user_id: int, data: dict) -> bool:
        """Hidden I/O and state changes."""
        success = self.db.update_user(user_id, data)
        if success:
            self.cache[user_id] = data  # Mutation!
        return success

# Usage requires state management
manager = UserManager("postgresql://...")
user = manager.get_user(123)
manager.update_user(123, {"name": "Alice"})
```

**After (Function-Based API)**:
```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class User:
    """Immutable user data."""
    id: int
    name: str
    email: str

class UserRepository(Protocol):
    """Repository interface for dependency injection."""

    def fetch_user(self, user_id: int) -> User | None:
        ...

    def save_user(self, user: User) -> bool:
        ...

# Pure business logic functions
def validate_user_update(user: User, new_name: str) -> Result[User, str]:
    """
    Pure: Validates and returns updated user.

    Args:
        user: Current user data
        new_name: New name to validate

    Returns:
        Ok(updated_user) or Err(validation_error)
    """
    if not new_name or len(new_name) < 2:
        return Err("Name must be at least 2 characters")

    updated_user = User(
        id=user.id,
        name=new_name,
        email=user.email
    )
    return Ok(updated_user)

# Effect functions with explicit I/O
def getUserIO(repo: UserRepository, user_id: int) -> User | None:
    """
    Impure I/O: Fetches user from repository.

    Args:
        repo: Injected repository dependency
        user_id: User ID to fetch

    Returns:
        User if found, None otherwise
    """
    return repo.fetch_user(user_id)

def saveUserIO(repo: UserRepository, user: User) -> bool:
    """
    Impure I/O: Saves user to repository.

    Args:
        repo: Injected repository dependency
        user: User data to save

    Returns:
        True if saved successfully
    """
    return repo.save_user(user)

# Usage with explicit dependencies
repo = PostgresUserRepository("postgresql://...")
user = getUserIO(repo, 123)

if user:
    update_result = validate_user_update(user, "Alice")

    if update_result.is_ok:
        success = saveUserIO(repo, update_result.value)
```

**Benefits**:
- Clear separation of pure logic and I/O
- Easy to test (inject test repository)
- No hidden state
- Composable functions
- Explicit dependencies

---

### Strategy 2: Result Types for Explicit Error Handling

Replace exceptions with Result/Option types in API signatures.

**Before (Exception-Based API)**:
```typescript
// API with hidden error paths (exceptions)
function parseJSON(input: string): object {
  // Throws exception on invalid JSON
  return JSON.parse(input);  // What errors? Unknown from signature!
}

function fetchUser(userId: number): User {
  const response = fetch(`/api/users/${userId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`);
  }

  return response.json();
}

// Usage requires try-catch (easy to forget!)
try {
  const user = fetchUser(123);
  console.log(user.name);
} catch (error) {
  console.error("Something went wrong:", error);
}
```

**After (Result-Based API)**:
```typescript
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function Ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function Err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

// API with explicit error types
function parseJSON(input: string): Result<object, string> {
  try {
    const parsed = JSON.parse(input);
    return Ok(parsed);
  } catch (error) {
    return Err(`Invalid JSON: ${error.message}`);
  }
}

async function fetchUser(userId: number): Promise<Result<User, string>> {
  try {
    const response = await fetch(`/api/users/${userId}`);

    if (!response.ok) {
      return Err(`HTTP ${response.status}: ${response.statusText}`);
    }

    const user = await response.json();
    return Ok(user);
  } catch (error) {
    return Err(`Network error: ${error.message}`);
  }
}

// Usage with explicit error handling (compiler enforced)
const userResult = await fetchUser(123);

if (userResult.ok) {
  console.log(userResult.value.name);  // Type-safe access
} else {
  console.error("Failed:", userResult.error);  // Must handle error
}
```

**Benefits**:
- Errors explicit in function signature
- Compiler forces error handling
- No hidden control flow
- Type-safe error types
- Composable with map, flatMap

---

### Strategy 3: Immutable Configuration and Options

API configuration should be immutable and explicit.

**Before (Mutable Configuration)**:
```python
# Mutable configuration object
class APIConfig:
    def __init__(self):
        self.base_url = ""
        self.timeout = 30
        self.retry_count = 3
        self.headers = {}  # Mutable dict!

    def set_timeout(self, timeout: int):
        self.timeout = timeout  # Mutation!

    def add_header(self, key: str, value: str):
        self.headers[key] = value  # Mutation!

# API with mutable config
def create_client(config: APIConfig):
    return APIClient(config)

# Config can be changed after client creation (dangerous!)
config = APIConfig()
config.set_timeout(60)
client = create_client(config)
config.set_timeout(10)  # Oops! May affect existing client
```

**After (Immutable Configuration)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class APIConfig:
    """Immutable API configuration."""
    base_url: str
    timeout: int = 30
    retry_count: int = 3
    headers: tuple[tuple[str, str], ...] = ()  # Immutable headers

    def with_timeout(self, timeout: int) -> 'APIConfig':
        """Pure: returns new config with updated timeout."""
        return APIConfig(
            base_url=self.base_url,
            timeout=timeout,
            retry_count=self.retry_count,
            headers=self.headers
        )

    def with_header(self, key: str, value: str) -> 'APIConfig':
        """Pure: returns new config with added header."""
        new_headers = self.headers + ((key, value),)
        return APIConfig(
            base_url=self.base_url,
            timeout=self.timeout,
            retry_count=self.retry_count,
            headers=new_headers
        )

# Pure API configuration
default_config = APIConfig(base_url="https://api.example.com")

# Build config through pure transformations
config = (
    default_config
    .with_timeout(60)
    .with_header("Authorization", "Bearer token")
    .with_header("Content-Type", "application/json")
)

# Original config unchanged
assert default_config.timeout == 30
assert config.timeout == 60
```

---

### Strategy 4: Composable API with Higher-Order Functions

Design APIs that compose naturally through function composition.

**Before (Non-Composable API)**:
```typescript
// API that doesn't compose well
function filterActive(users: User[]): User[] {
  return users.filter(u => u.active);
}

function sortByName(users: User[]): User[] {
  return [...users].sort((a, b) => a.name.localeCompare(b.name));
}

function limitToTen(users: User[]): User[] {
  return users.slice(0, 10);
}

// Awkward usage
const result = limitToTen(sortByName(filterActive(users)));
```

**After (Composable Pipeline API)**:
```typescript
// Composable transformation API
type Transform<T> = (items: T[]) => T[];

function pipe<T>(...transforms: Transform<T>[]): Transform<T> {
  return (items: T[]) =>
    transforms.reduce((acc, transform) => transform(acc), items);
}

// Pure composable transformations
const filterActive: Transform<User> = users =>
  users.filter(u => u.active);

const sortByName: Transform<User> = users =>
  [...users].sort((a, b) => a.name.localeCompare(b.name));

const limitTo = (n: number): Transform<User> => users =>
  users.slice(0, n);

// Elegant composition
const processUsers = pipe(
  filterActive,
  sortByName,
  limitTo(10)
);

const result = processUsers(users);

// Highly reusable
const topFiveActive = pipe(filterActive, sortByName, limitTo(5));
const topTenActive = pipe(filterActive, sortByName, limitTo(10));
```

---

### Strategy 5: Builder Pattern with Immutable Builders

For complex configuration, use immutable builder pattern.

**Before (Mutable Builder)**:
```python
# Mutable builder (anti-pattern)
class QueryBuilder:
    def __init__(self):
        self.table = ""
        self.filters = []
        self.limit = None

    def from_table(self, table: str):
        self.table = table  # Mutation!
        return self

    def where(self, condition: str):
        self.filters.append(condition)  # Mutation!
        return self

    def build(self) -> str:
        query = f"SELECT * FROM {self.table}"
        if self.filters:
            query += " WHERE " + " AND ".join(self.filters)
        if self.limit:
            query += f" LIMIT {self.limit}"
        return query
```

**After (Immutable Builder)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Query:
    """Immutable query representation."""
    table: str
    filters: tuple[str, ...] = ()
    limit: int | None = None

    def where(self, condition: str) -> 'Query':
        """Pure: returns new query with added filter."""
        return Query(
            table=self.table,
            filters=self.filters + (condition,),
            limit=self.limit
        )

    def with_limit(self, limit: int) -> 'Query':
        """Pure: returns new query with limit."""
        return Query(
            table=self.table,
            filters=self.filters,
            limit=limit
        )

    def to_sql(self) -> str:
        """Pure: builds SQL string from immutable query."""
        sql = f"SELECT * FROM {self.table}"

        if self.filters:
            sql += " WHERE " + " AND ".join(self.filters)

        if self.limit:
            sql += f" LIMIT {self.limit}"

        return sql

# Pure functional query building
query = (
    Query(table="users")
    .where("active = true")
    .where("age >= 18")
    .with_limit(10)
)

sql = query.to_sql()
# SELECT * FROM users WHERE active = true AND age >= 18 LIMIT 10

# Original builder unchanged
base_query = Query(table="users")
query1 = base_query.where("active = true")
query2 = base_query.where("deleted = false")
# base_query still pristine
```

---

## Examples

### Example 1: File Processing API

**Function-Based File Processing API**:
```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FileContent:
    """Immutable file content."""
    path: Path
    content: str

# Pure transformation functions
def parse_csv_content(content: str) -> list[dict]:
    """Pure: parses CSV string to list of dicts."""
    lines = content.strip().split('\n')
    if not lines:
        return []

    headers = lines[0].split(',')
    return [
        dict(zip(headers, line.split(',')))
        for line in lines[1:]
    ]

def filter_valid_rows(rows: list[dict], required_keys: tuple[str, ...]) -> list[dict]:
    """Pure: filters rows with required keys."""
    return [
        row for row in rows
        if all(key in row for key in required_keys)
    ]

def transform_row(row: dict, transformations: dict[str, callable]) -> dict:
    """Pure: applies transformations to row."""
    return {
        key: transformations.get(key, lambda x: x)(value)
        for key, value in row.items()
    }

# Effect functions with IO suffix
def readFileIO(path: Path) -> FileContent:
    """Impure I/O: reads file from disk."""
    return FileContent(path=path, content=path.read_text())

def writeFileIO(path: Path, content: str) -> None:
    """Impure I/O: writes content to disk."""
    path.write_text(content)

# Pure processing pipeline
def process_csv_data(content: str) -> list[dict]:
    """Pure: complete processing pipeline."""
    rows = parse_csv_content(content)
    valid_rows = filter_valid_rows(rows, ("name", "email"))
    return [
        transform_row(row, {"email": str.lower})
        for row in valid_rows
    ]

# Usage: clear separation of pure and impure
file_content = readFileIO(Path("data.csv"))
processed_data = process_csv_data(file_content.content)
writeFileIO(Path("output.csv"), format_as_csv(processed_data))
```

---

## Edge Cases

### Edge Case 1: Streaming APIs
**Scenario**: API processes large data streams
**Issue**: Immutability concerns with large data
**Handling**:
- Use iterators/generators for lazy evaluation
- Process in immutable chunks
- Return iterators of immutable data

### Edge Case 2: Real-Time APIs
**Scenario**: API for real-time event processing
**Issue**: Events arrive continuously
**Handling**:
- Use immutable event objects
- Pure event handlers
- Separate event reception (impure) from processing (pure)

### Edge Case 3: Legacy System Integration
**Scenario**: FP API must integrate with mutable legacy code
**Issue**: Boundary between FP and imperative
**Handling**:
- Adapter layer at boundary
- Convert mutable to immutable at edges
- Isolate legacy interaction to effect functions

### Edge Case 4: Performance-Critical APIs
**Scenario**: API has strict performance requirements
**Issue**: Immutability overhead
**Handling**:
- Use structural sharing (efficient immutable data structures)
- Benchmark before optimizing
- Local mutation OK if contained and not exposed

### Edge Case 5: Complex State Machines
**Scenario**: API models complex state transitions
**Issue**: State machine with FP patterns
**Handling**:
- Use ADTs for states
- Pure transition functions
- Return new state, don't mutate

---

## Database Operations

### Record API Design Metadata

```sql
-- Track API module metadata
UPDATE files
SET
    file_type = 'api',
    api_metadata = json_set(
        COALESCE(api_metadata, '{}'),
        '$.api_style', 'functional',
        '$.error_handling', 'result_types',
        '$.state_management', 'immutable'
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE path = 'src/api/user_api.py' AND project_id = ?;

-- Record API design validation
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'API DESIGN: user_api.py follows FP design principles: pure functions, Result types, immutable config',
    '["fp_api_design", "api", "compliance"]',
    CURRENT_TIMESTAMP
);
```

---

## Related Directives

### FP Directives
- **fp_purity**: API functions should be pure where possible
- **fp_immutability**: API data structures should be immutable
- **fp_no_oop**: Prefer function-based APIs over class-based

### Project Directives
- **project_compliance_check**: Validates API design compliance
- **project_update_db**: Records API metadata

---

## Helper Functions

### `analyze_api_structure(module) -> dict`
Analyzes API design patterns and compliance.

**Signature**:
```python
def analyze_api_structure(module: Module) -> dict:
    """
    Analyzes API design for FP compliance.
    Returns analysis with violations and suggestions.
    """
```

### `suggest_api_refactoring(api_class) -> str`
Suggests function-based alternative for class-based API.

**Signature**:
```python
def suggest_api_refactoring(api_class: ClassDef) -> str:
    """
    Generates function-based API refactoring suggestion.
    Returns code example as string.
    """
```

---

## Testing

### Test 1: API Purity
```python
def test_api_functions_are_pure():
    # Pure API functions should always return same output for same input
    result1 = validate_user_update(user, "Alice")
    result2 = validate_user_update(user, "Alice")

    assert result1 == result2
```

### Test 2: Immutable Configuration
```python
def test_immutable_config():
    config = APIConfig(base_url="https://example.com")

    # Operations return new config
    modified = config.with_timeout(60)

    # Original unchanged
    assert config.timeout == 30
    assert modified.timeout == 60
```

### Test 3: Composability
```python
def test_api_composability():
    # Functions should compose naturally
    process = pipe(filterActive, sortByName, limitTo(10))

    result = process(users)

    assert len(result) <= 10
```

---

## Common Mistakes

### Mistake 1: Hidden State in API
**Problem**: API uses global state or hidden configuration

**Solution**: Explicit dependencies and configuration

```python
# ❌ Bad: hidden global config
API_KEY = "secret"

def fetch_data():
    return requests.get("/api/data", headers={"Authorization": API_KEY})

# ✅ Good: explicit config
def fetchDataIO(api_key: str) -> Response:
    return requests.get("/api/data", headers={"Authorization": api_key})
```

### Mistake 2: Throwing Exceptions in API
**Problem**: Errors not explicit in function signature

**Solution**: Use Result/Option types

```python
# ❌ Bad: exceptions
def parse_config(data: str) -> Config:
    if not data:
        raise ValueError("Empty config")
    return Config(data)

# ✅ Good: Result type
def parse_config(data: str) -> Result[Config, str]:
    if not data:
        return Err("Empty config")
    return Ok(Config(data))
```

### Mistake 3: Mutable API Objects
**Problem**: API returns mutable objects

**Solution**: Immutable data structures

```python
# ❌ Bad: mutable return
def get_user() -> dict:
    return {"id": 1, "name": "Alice"}  # Caller can mutate!

# ✅ Good: immutable return
@dataclass(frozen=True)
class User:
    id: int
    name: str

def get_user() -> User:
    return User(id=1, name="Alice")  # Immutable!
```

---

## Roadblocks

### Roadblock 1: Class-Based Legacy API
**Issue**: Existing API built with classes
**Resolution**: Gradual refactoring, facade layer with functional API

### Roadblock 2: Exception-Heavy Codebase
**Issue**: Existing code uses exceptions extensively
**Resolution**: Adapter layer converting exceptions to Results at boundaries

### Roadblock 3: Team Unfamiliarity
**Issue**: Team not familiar with FP API patterns
**Resolution**: Documentation, examples, gradual adoption

---

## Integration Points

### With `fp_purity`
API functions should be pure where possible.

### With `fp_immutability`
API data structures should be immutable.

### With `project_compliance_check`
API design validated during compliance checks.

---

## Intent Keywords

- `api design`
- `public interface`
- `composability`
- `error handling`
- `immutable api`

---

## Confidence Threshold

**0.7** - High confidence for API design validation.

---

## Notes

- Prefer functions over classes for APIs
- Use Result/Option for error handling
- Make all state explicit
- Design for composition
- Immutable configuration and data
- Separate pure logic from effects
- Clear I/O boundaries with IO suffix
- Type-safe APIs with explicit signatures
- Document API usage patterns
- AIFP APIs are predictable, testable, and composable


# Directive: fp_wrapper_generation

**Type**: FP
**Level**: 2
**Parent Directive**: None
**Priority**: HIGH - OOP library isolation

---

## Purpose

The `fp_wrapper_generation` directive **detects OOP library imports and generates pure functional wrappers** for AI-safe usage, maintaining FP purity across legacy OOP dependencies. This directive is **critical for real-world FP** because:

- **Legacy library support**: Most libraries are OOP-based
- **Maintains purity boundary**: Isolates stateful OOP from pure FP code
- **AI-friendly interface**: Wrapper functions are pure and composable
- **Dependency injection**: Wrappers enable DI for testability
- **Gradual FP adoption**: Use OOP libraries without compromising FP principles

This directive generates wrappers for:
- **Stateful classes** - Classes with mutable instance state
- **Method chains** - Fluent APIs with mutation
- **Singleton patterns** - Global state managers
- **Context managers** - Resource management (files, connections)
- **Event-driven APIs** - Callback-based interfaces

**Wrapper principle**: Convert stateful methods to pure functions with explicit state.

**Real-world examples**: See [examples/wrappers/](../../../examples/wrappers/) for working wrapper implementations. As AIFP develops, this folder will contain reference implementations for common libraries.

---

## When to Apply

This directive applies when:
- **OOP library imported** - External library uses classes/methods
- **Class instantiation detected** - `new Class()` or `Class()`
- **Method call on object** - `obj.method()` pattern
- **During compliance checks** - `project_compliance_check` scans imports
- **User requests wrapper** - "Wrap library", "Create FP interface"
- **Legacy code integration** - Importing existing OOP codebase

---

## Workflow

### Trunk: detect_oop_libraries

Scans imports and identifies OOP libraries.

**Steps**:
1. **Parse imports** - Extract all import statements
2. **Check library blacklist** - Known OOP libraries
3. **Analyze usage** - How library is used (classes, methods)
4. **Route to wrapper generation** - Create functional interface

### Branches

**Branch 1: If library_on_blacklist**
- **Then**: `generate_wrapper`
- **Details**: Create functional wrapper for OOP library
  - Known OOP libraries (blacklist):
    ```python
    OOP_LIBRARIES = {
        # Python
        "requests": "stateful sessions",
        "sqlite3": "connection/cursor objects",
        "logging": "logger objects with state",
        "pathlib": "Path objects with methods",

        # JavaScript
        "axios": "stateful instances",
        "mongoose": "ORM with models",
        "express": "app objects with middleware",

        # General patterns
        ".*Client$": "client classes",
        ".*Manager$": "manager classes",
        ".*Service$": "service classes"
    }
    ```
  - Wrapper generation strategy:
    ```python
    # ❌ OOP library usage (stateful)
    import requests

    def fetch_data(url):
        response = requests.get(url)  # Hidden session state
        return response.json()

    # ✅ Generated wrapper (pure FP)
    import requests
    from dataclasses import dataclass
    from typing import Any

    @dataclass(frozen=True)
    class HttpConfig:
        timeout: int = 30
        headers: dict = None

    def fetch_url(url: str, config: HttpConfig = HttpConfig()) -> dict:
        """Pure wrapper for requests.get"""
        response = requests.get(
            url,
            timeout=config.timeout,
            headers=config.headers or {}
        )
        return response.json()

    # Usage (pure)
    config = HttpConfig(timeout=60)
    data = fetch_url("https://api.example.com", config)
    ```
  - Wrapper patterns:
    - **Pattern 1**: Instance methods → Static functions
    - **Pattern 2**: Mutable state → Immutable config objects
    - **Pattern 3**: Method chaining → Function composition
    - **Pattern 4**: Callbacks → Return values or iterators
  - Update database:
    ```sql
    INSERT INTO notes (
      content,
      note_type,
      source,
      directive_name
    ) VALUES (
      'Generated FP wrapper for requests library: fetch_url()',
      'research',
      'directive',
      'fp_wrapper_generation'
    );
    ```
- **Result**: Functional wrapper generated

**Branch 2: If unknown_library**
- **Then**: `prompt_for_wrapper`
- **Details**: Unknown library, ask user if wrapper needed
  - Analysis process:
    ```python
    # Unknown library imported
    import some_library

    # Analyze usage
    usage_patterns = analyze_library_usage(some_library)

    if has_stateful_patterns(usage_patterns):
        prompt_user(f"""
        Library 'some_library' appears to use OOP patterns:
        • {len(usage_patterns['classes'])} class instantiations
        • {len(usage_patterns['methods'])} method calls on objects

        Generate functional wrapper? (y/n):
        """)
    ```
  - User decision:
    - **Yes**: Generate wrapper based on usage patterns
    - **No**: Allow direct usage (user confirms library is pure)
    - **Skip**: Mark library as pure in whitelist
  - Whitelist update:
    ```python
    PURE_LIBRARIES = [
        "functools",  # Python functional utilities
        "itertools",  # Python iterators
        "toolz",  # Functional toolkit
        "ramda",  # JavaScript FP library
    ]
    ```
- **Result**: User clarifies library classification

**Branch 3: If stateful_class_detected**
- **Then**: `wrap_class_as_functions`
- **Details**: Convert class methods to pure functions
  - Class wrapper strategy:
    ```python
    # ❌ Stateful class
    class Calculator:
        def __init__(self):
            self.memory = 0  # Mutable state

        def add(self, x, y):
            result = x + y
            self.memory = result  # Mutation!
            return result

        def recall(self):
            return self.memory

    # ✅ Generated wrapper (pure functions + state object)
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class CalculatorState:
        memory: float = 0

    def add(x: float, y: float, state: CalculatorState) -> tuple[float, CalculatorState]:
        """Pure add function with explicit state"""
        result = x + y
        new_state = CalculatorState(memory=result)
        return result, new_state

    def recall(state: CalculatorState) -> float:
        """Pure recall function"""
        return state.memory

    # Usage (functional state threading)
    state = CalculatorState()
    result1, state = add(5, 3, state)
    result2, state = add(result1, 2, state)
    memory = recall(state)
    ```
  - Wrapper generation steps:
    1. Extract class methods
    2. Identify instance variables (state)
    3. Create immutable state dataclass
    4. Convert methods to functions with state parameter
    5. Return tuple (result, new_state) for mutations
- **Result**: Class wrapped as pure functions

**Branch 4: If context_manager_detected**
- **Then**: `wrap_resource_management`
- **Details**: Wrap context managers with functional interface
  - Context manager patterns:
    ```python
    # ❌ Context manager (stateful resource)
    with open("file.txt") as f:
        content = f.read()

    # ✅ Wrapper (functional resource handling)
    from typing import Callable, TypeVar

    T = TypeVar('T')

    def with_file(
        filename: str,
        mode: str,
        operation: Callable[[Any], T]
    ) -> T:
        """Pure wrapper for file operations"""
        with open(filename, mode) as f:
            return operation(f)

    # Usage
    content = with_file("file.txt", "r", lambda f: f.read())

    # Or: Return content directly (simpler)
    def read_file(filename: str) -> str:
        """Pure file reader"""
        with open(filename) as f:
            return f.read()

    def write_file(filename: str, content: str) -> None:
        """Pure file writer"""
        with open(filename, "w") as f:
            f.write(content)
    ```
  - Benefits:
    - Resource cleanup automatic
    - Pure function interface
    - Testable with mock operation
- **Result**: Context manager wrapped functionally

**Branch 5: If fluent_api_detected**
- **Then**: `convert_to_pipeline`
- **Details**: Convert method chaining to function pipeline
  - Fluent API patterns:
    ```python
    # ❌ Fluent API (method chaining with mutation)
    query = (
        QueryBuilder()
        .select("name", "email")  # Returns self (mutated)
        .where("age", ">", 18)  # Returns self (mutated)
        .order_by("name")  # Returns self (mutated)
        .limit(10)  # Returns self (mutated)
        .execute()
    )

    # ✅ Wrapper (functional pipeline)
    from dataclasses import dataclass

    @dataclass(frozen=True)
    class Query:
        fields: tuple = ()
        conditions: tuple = ()
        order: str = ""
        limit: int = None

    def select(fields: tuple[str, ...]) -> Query:
        return Query(fields=fields)

    def where(query: Query, field: str, op: str, value: Any) -> Query:
        condition = (field, op, value)
        return Query(
            fields=query.fields,
            conditions=query.conditions + (condition,),
            order=query.order,
            limit=query.limit
        )

    def order_by(query: Query, field: str) -> Query:
        return Query(
            fields=query.fields,
            conditions=query.conditions,
            order=field,
            limit=query.limit
        )

    def limit_to(query: Query, n: int) -> Query:
        return Query(
            fields=query.fields,
            conditions=query.conditions,
            order=query.order,
            limit=n
        )

    # Usage (functional composition)
    from functools import reduce

    def pipe(initial, *functions):
        return reduce(lambda acc, f: f(acc), functions, initial)

    query = pipe(
        select(("name", "email")),
        lambda q: where(q, "age", ">", 18),
        lambda q: order_by(q, "name"),
        lambda q: limit_to(q, 10)
    )
    ```
- **Result**: Fluent API converted to pipeline

**Fallback**: `skip_if_pure`
- **Details**: Library is pure functional, no wrapper needed
  - Pure library characteristics:
    - No classes with mutable state
    - Functions only (no methods)
    - No side effects
    - Referentially transparent
  - Examples: functools, itertools, ramda, lodash/fp
- **Result**: Library used directly

---

## Examples

### ✅ Compliant Usage

**Wrapping Requests Library:**
```python
# Initial code (uses OOP library directly)
import requests

def get_user_data(user_id):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()

# AI calls: fp_wrapper_generation()

# Workflow:
# 1. detect_oop_libraries:
#    - requests imported
#    - requests on blacklist (stateful sessions)
#
# 2. library_on_blacklist: generate_wrapper
#    - Create functional wrapper for requests.get
#
# Generated wrapper (compliant)
import requests
from dataclasses import dataclass
from typing import Any, Optional

@dataclass(frozen=True)
class HttpConfig:
    """Immutable HTTP configuration"""
    timeout: int = 30
    headers: dict = None
    verify_ssl: bool = True

@dataclass(frozen=True)
class HttpResponse:
    """Immutable HTTP response"""
    status_code: int
    data: Any
    headers: dict

def http_get(
    url: str,
    config: HttpConfig = HttpConfig()
) -> HttpResponse:
    """Pure wrapper for HTTP GET"""
    response = requests.get(
        url,
        timeout=config.timeout,
        headers=config.headers or {},
        verify=config.verify_ssl
    )
    return HttpResponse(
        status_code=response.status_code,
        data=response.json(),
        headers=dict(response.headers)
    )

# Refactored code (uses wrapper)
def get_user_data(user_id: int, config: HttpConfig = HttpConfig()) -> dict:
    url = f"https://api.example.com/users/{user_id}"
    response = http_get(url, config)
    return response.data

# Database log
INSERT INTO notes (
  content,
  note_type,
  source,
  directive_name
) VALUES (
  'Generated FP wrapper for requests library: http_get()',
  'research',
  'directive',
  'fp_wrapper_generation'
);

# Result:
# ✅ Stateful library wrapped with pure functions
# ✅ Configuration explicit (immutable dataclass)
# ✅ Testable (can mock http_get)
# ✅ Composable (pure function)
```

---

**Wrapping Stateful Class:**
```python
# Initial code (stateful class)
class ShoppingCart:
    def __init__(self):
        self.items = []  # Mutable state
        self.total = 0  # Mutable state

    def add_item(self, item, price):
        self.items.append(item)  # Mutation
        self.total += price  # Mutation

    def get_total(self):
        return self.total

# AI calls: fp_wrapper_generation()

# Workflow:
# 1. detect_oop_libraries:
#    - Stateful class detected
#    - Instance variables: items, total
#
# 2. stateful_class_detected: wrap_class_as_functions
#    - Extract state: items, total
#    - Convert methods to pure functions
#
# Generated wrapper (compliant)
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CartState:
    """Immutable shopping cart state"""
    items: tuple = ()
    total: float = 0

def add_item(
    state: CartState,
    item: Any,
    price: float
) -> CartState:
    """Pure function to add item"""
    return CartState(
        items=state.items + (item,),
        total=state.total + price
    )

def get_total(state: CartState) -> float:
    """Pure function to get total"""
    return state.total

def get_items(state: CartState) -> tuple:
    """Pure function to get items"""
    return state.items

# Usage (functional state threading)
cart = CartState()  # Empty cart
cart = add_item(cart, "Apple", 1.50)
cart = add_item(cart, "Orange", 2.00)
cart = add_item(cart, "Banana", 0.75)
total = get_total(cart)  # 4.25

# Result:
# ✅ Stateful class converted to pure functions
# ✅ State explicit (CartState)
# ✅ No mutation (immutable dataclass)
# ✅ Functional state threading
```

---

**Wrapping Database Connection:**
```python
# Initial code (stateful connection)
import sqlite3

def query_users():
    conn = sqlite3.connect("db.sqlite")  # Stateful
    cursor = conn.cursor()  # Stateful
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    conn.close()
    return results

# AI calls: fp_wrapper_generation()

# Workflow:
# 1. detect_oop_libraries:
#    - sqlite3 on blacklist (stateful connections)
#
# 2. library_on_blacklist: generate_wrapper
#    - Wrap connection management
#
# Generated wrapper (compliant)
import sqlite3
from dataclasses import dataclass
from typing import Any, Callable

@dataclass(frozen=True)
class DatabaseConfig:
    """Immutable database configuration"""
    db_path: str
    timeout: float = 5.0

def with_database(
    config: DatabaseConfig,
    operation: Callable[[sqlite3.Connection], Any]
) -> Any:
    """Pure wrapper for database operations"""
    conn = sqlite3.connect(config.db_path, timeout=config.timeout)
    try:
        result = operation(conn)
        conn.commit()
        return result
    finally:
        conn.close()

def query_all(conn: sqlite3.Connection, sql: str) -> list[tuple]:
    """Pure query function"""
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

# Refactored code (uses wrapper)
def query_users(config: DatabaseConfig) -> list[tuple]:
    return with_database(
        config,
        lambda conn: query_all(conn, "SELECT * FROM users")
    )

# Usage
config = DatabaseConfig(db_path="db.sqlite")
users = query_users(config)

# Result:
# ✅ Resource management wrapped
# ✅ Configuration explicit
# ✅ Connection lifecycle managed
# ✅ Pure function interface
```

---

### ❌ Non-Compliant Usage

**Using OOP Library Directly:**
```python
# ❌ Direct OOP usage
import requests

def fetch_data(url):
    session = requests.Session()  # Stateful
    session.headers.update({"User-Agent": "Bot"})  # Mutation
    response = session.get(url)  # Hidden state
    return response.json()

# Why Non-Compliant:
# - Stateful Session object
# - Hidden state (headers)
# - Not pure
# - Not testable without mocking
```

**Corrected:**
```python
# ✅ Wrapper approach
@dataclass(frozen=True)
class HttpConfig:
    headers: dict = None

def http_get(url: str, config: HttpConfig) -> dict:
    response = requests.get(url, headers=config.headers or {})
    return response.json()

def fetch_data(url: str) -> dict:
    config = HttpConfig(headers={"User-Agent": "Bot"})
    return http_get(url, config)
```

---

## Edge Cases

### Edge Case 1: Circular Dependencies

**Issue**: Wrapped library imports another wrapped library

**Handling**:
- Generate wrappers in dependency order
- Wrappers use other wrappers
- Avoid circular imports

**Directive Action**: Topological sort of library dependencies.

---

### Edge Case 2: Callback-Based APIs

**Issue**: Library uses callbacks (event-driven)

**Handling**:
```python
# ❌ Callback API
def on_data(data):
    print(data)

client.on("data", on_data)  # Event listener

# ✅ Wrapper: Return iterator/stream
def get_data_stream(client) -> Iterator:
    queue = Queue()
    client.on("data", lambda d: queue.put(d))
    while True:
        yield queue.get()
```

**Directive Action**: Convert callbacks to iterators or futures.

---

### Edge Case 3: Multiple Constructors

**Issue**: Class has multiple ways to instantiate

**Handling**:
```python
# Multiple constructors
File.open(path)
File.from_string(content)
File.from_bytes(data)

# Wrapper: Separate functions
def open_file(path: str) -> FileHandle: ...
def file_from_string(content: str) -> FileHandle: ...
def file_from_bytes(data: bytes) -> FileHandle: ...
```

**Directive Action**: One wrapper function per constructor.

---

## Related Directives

- **Called By**:
  - `fp_purity` - Uses wrappers to maintain purity
  - `project_compliance_check` - Scans for unwrapped OOP usage
  - `project_file_write` - May generate wrappers during code generation
- **Calls**:
  - Database helpers - Logs wrapper generation
  - `project_notes_log` - Documents wrapper decisions
- **Related**:
  - `fp_no_oop` - Eliminates OOP constructs
  - `fp_io_isolation` - Wrappers often isolate I/O

---

## Helper Functions Used

- `detect_oop_patterns(library: str) -> dict` - Analyze library usage
- `generate_state_dataclass(class_def: Class) -> str` - Create state object
- `convert_method_to_function(method: Method) -> str` - Generate wrapper function
- `is_pure_library(library: str) -> bool` - Check if wrapper needed

---

## Database Operations

This directive updates the following tables:

- **`notes`**: INSERT wrapper generation decisions

---

## Testing

1. **Detect OOP library** → Library on blacklist
   ```python
   assert "requests" in OOP_LIBRARIES
   ```

2. **Generate wrapper** → Functional wrapper created
   ```python
   wrapper = generate_wrapper("requests", "get")
   assert "def http_get" in wrapper
   ```

3. **Pure library skip** → No wrapper needed
   ```python
   assert is_pure_library("functools") == True
   ```

---

## Common Mistakes

- ❌ **Not wrapping stateful libraries** - Direct usage breaks purity
- ❌ **Shallow wrapper** - Wrapper still uses mutable state
- ❌ **Not handling resources** - Connections/files not cleaned up
- ❌ **Complex wrapper generation** - Over-engineering simple wrappers

---

## Roadblocks and Resolutions

### Roadblock 1: unwrapped_library
**Issue**: OOP library used without wrapper
**Resolution**: Generate wrapper via fp_wrapper_generation

### Roadblock 2: dynamic_import
**Issue**: Library imported dynamically (hard to detect)
**Resolution**: Manual wrapper required, log for review

---

## References

- [Helper Functions Reference](../../../docs/helper-functions-reference.md#fp-helpers)
- [Blueprint: FP Directives](../../../docs/blueprints/blueprint_fp_directives.md#anti_oop)
- [JSON Definition](../../../docs/directives-json/directives-fp-core.json)
- [Wrapper Examples](../../../examples/wrappers/) - Real-world wrapper implementations (populated during development)

---

*Part of AIFP v1.0 - FP directive for wrapping OOP libraries with functional interfaces*

# fp_io_isolation

## Purpose

The `fp_io_isolation` directive separates all input/output operations into dedicated effect functions or external modules, isolating I/O from pure business logic. It ensures strict separation between deterministic computation and non-deterministic effects, pushing all I/O to program boundaries while keeping core logic pure, testable, and composable. This maintains referential transparency while allowing necessary effectful operations.

**Category**: Side Effects
**Type**: FP Core
**Priority**: Critical
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`detect_io_operations`**: Scan function bodies for I/O operations (file, network, console, database).

### Branches

1. **`io_inline`** → **`move_to_io_function`**
   - **Condition**: I/O operation embedded within business logic
   - **Action**: Extract I/O to separate effect function
   - **Details**: Create pure core function and I/O wrapper
   - **Output**: Separated pure logic and I/O boundary

2. **`external_call`** → **`wrap_in_effect`**
   - **Condition**: External API or system call within function
   - **Action**: Wrap external call in effect function
   - **Details**: Create effect boundary around external dependencies
   - **Output**: Effect wrapper isolating external call

3. **`database_access`** → **`extract_to_repository`**
   - **Condition**: Database query or command inline in logic
   - **Action**: Move database operations to repository layer
   - **Details**: Separate data access from business logic
   - **Output**: Repository pattern with pure logic layer

4. **`already_isolated`** → **`mark_as_pure`**
   - **Condition**: I/O already isolated at boundaries
   - **Action**: Mark as compliant
   - **Output**: Purity confirmation

5. **Fallback** → **`mark_as_pure`**
   - **Condition**: No I/O detected
   - **Action**: Mark as pure function

### Error Handling
- **On failure**: Prompt user with I/O isolation strategy
- **Low confidence** (< 0.7): Request review before refactoring

---

## Refactoring Strategies

### Strategy 1: File I/O Isolation
Separate file reading/writing from data processing.

**Before (Python - I/O Mixed with Logic)**:
```python
def process_data_file(filename):
    """Impure: mixes I/O with logic."""
    # I/O: read file
    with open(filename, 'r') as f:
        content = f.read()

    # Logic: process
    lines = content.split('\n')
    processed = [line.upper() for line in lines if line.strip()]

    # I/O: write file
    with open('output.txt', 'w') as f:
        f.write('\n'.join(processed))

    return len(processed)
```

**After (Python - I/O Isolated)**:
```python
# Pure business logic (no I/O)
def process_lines(content: str) -> str:
    """Pure: transforms content without I/O."""
    lines = content.split('\n')
    processed = [line.upper() for line in lines if line.strip()]
    return '\n'.join(processed)

# I/O boundary functions
def read_file(filename: str) -> str:
    """Effect: reads file content."""
    with open(filename, 'r') as f:
        return f.read()

def write_file(filename: str, content: str) -> None:
    """Effect: writes content to file."""
    with open(filename, 'w') as f:
        f.write(content)

# Orchestration at boundary
def process_data_file(filename: str) -> int:
    """Orchestrates I/O and pure logic."""
    # Effect: read
    content = read_file(filename)

    # Pure: transform
    processed_content = process_lines(content)

    # Effect: write
    write_file('output.txt', processed_content)

    return len(processed_content.split('\n'))
```

### Strategy 2: Database I/O Isolation (Repository Pattern)
Separate database operations from business logic.

**Before (Python - Database Inline)**:
```python
import sqlite3

def get_user_orders(user_id):
    """Impure: database access mixed with logic."""
    # I/O: database query
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM orders WHERE user_id = ?",
        (user_id,)
    )
    orders = cursor.fetchall()
    conn.close()

    # Logic: calculate total
    total = sum(order[3] for order in orders)  # amount column

    return {"orders": orders, "total": total}
```

**After (Python - Repository Pattern)**:
```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Order:
    id: int
    user_id: int
    product: str
    amount: float

# Pure interface (protocol)
class OrderRepository(Protocol):
    def find_by_user(self, user_id: int) -> list[Order]: ...

# Pure business logic
def calculate_total(orders: list[Order]) -> float:
    """Pure: calculates order total."""
    return sum(order.amount for order in orders)

def get_user_orders_summary(
    orders: list[Order]
) -> dict:
    """Pure: creates order summary."""
    return {
        "orders": orders,
        "total": calculate_total(orders)
    }

# I/O boundary: Repository implementation
class SQLiteOrderRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def find_by_user(self, user_id: int) -> list[Order]:
        """Effect: queries database."""
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, user_id, product, amount FROM orders WHERE user_id = ?",
            (user_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        return [Order(*row) for row in rows]

# Orchestration
def get_user_orders(user_id: int, repo: OrderRepository) -> dict:
    """Dependency injection: pure logic + I/O boundary."""
    # Effect: data access
    orders = repo.find_by_user(user_id)

    # Pure: business logic
    return get_user_orders_summary(orders)
```

### Strategy 3: Console I/O Isolation
Separate input/output from computation.

**Before (Python - Console I/O Inline)**:
```python
def interactive_calculator():
    """Impure: console I/O mixed throughout."""
    while True:
        # I/O: input
        operation = input("Enter operation (+, -, *, /): ")
        if operation == 'quit':
            print("Goodbye!")
            break

        # I/O: input
        a = float(input("First number: "))
        b = float(input("Second number: "))

        # Logic
        if operation == '+':
            result = a + b
        elif operation == '-':
            result = a - b
        elif operation == '*':
            result = a * b
        elif operation == '/':
            result = a / b if b != 0 else 0

        # I/O: output
        print(f"Result: {result}")
```

**After (Python - Console I/O Isolated)**:
```python
from dataclasses import dataclass
from typing import Literal

Operation = Literal['+', '-', '*', '/']

@dataclass(frozen=True)
class Calculation:
    operation: Operation
    a: float
    b: float

# Pure business logic
def calculate(calc: Calculation) -> float:
    """Pure: performs calculation."""
    match calc.operation:
        case '+':
            return calc.a + calc.b
        case '-':
            return calc.a - calc.b
        case '*':
            return calc.a * calc.b
        case '/':
            return calc.a / calc.b if calc.b != 0 else 0.0

# I/O boundaries
def read_operation() -> Operation | Literal['quit']:
    """Effect: reads user input."""
    return input("Enter operation (+, -, *, /) or 'quit': ")

def read_number(prompt: str) -> float:
    """Effect: reads number from user."""
    return float(input(prompt))

def display_result(result: float) -> None:
    """Effect: displays result."""
    print(f"Result: {result}")

# Orchestration at boundary
def interactive_calculator():
    """Orchestrates I/O and pure logic."""
    while True:
        # Effect: input
        operation = read_operation()
        if operation == 'quit':
            print("Goodbye!")
            break

        # Effect: input
        a = read_number("First number: ")
        b = read_number("Second number: ")

        # Pure: calculation
        calc = Calculation(operation=operation, a=a, b=b)
        result = calculate(calc)

        # Effect: output
        display_result(result)
```

### Strategy 4: HTTP/Network I/O Isolation
Separate network calls from data transformation.

**Before (TypeScript - Network Inline)**:
```typescript
async function getUserProfile(userId: number) {
  // I/O: HTTP request
  const response = await fetch(`/api/users/${userId}`);
  const user = await response.json();

  // Logic: transform
  return {
    id: user.id,
    displayName: `${user.firstName} ${user.lastName}`,
    initials: `${user.firstName[0]}${user.lastName[0]}`,
    isActive: user.status === 'active'
  };
}
```

**After (TypeScript - Network Isolated)**:
```typescript
interface RawUser {
  id: number;
  firstName: string;
  lastName: string;
  status: string;
}

interface UserProfile {
  id: number;
  displayName: string;
  initials: string;
  isActive: boolean;
}

// Pure transformation
function transformUserProfile(user: RawUser): UserProfile {
  return {
    id: user.id,
    displayName: `${user.firstName} ${user.lastName}`,
    initials: `${user.firstName[0]}${user.lastName[0]}`,
    isActive: user.status === 'active'
  };
}

// I/O boundary
async function fetchUser(userId: number): Promise<RawUser> {
  const response = await fetch(`/api/users/${userId}`);
  return response.json();
}

// Orchestration
async function getUserProfile(userId: number): Promise<UserProfile> {
  // Effect: network call
  const rawUser = await fetchUser(userId);

  // Pure: transformation
  return transformUserProfile(rawUser);
}
```

### Strategy 5: Logging I/O Isolation
Return log data instead of logging inline.

**Before (Python - Inline Logging)**:
```python
import logging

def process_order(order):
    """Impure: logging side effects."""
    logging.info(f"Processing order {order['id']}")

    if order['amount'] > 1000:
        logging.warning(f"Large order: ${order['amount']}")

    total = order['amount'] * 1.1  # Add tax
    logging.info(f"Order total: ${total}")

    return total
```

**After (Python - Logging Isolated)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ProcessResult:
    total: float
    log_messages: tuple[str, ...]

# Pure logic with log data return
def process_order_pure(order: dict) -> ProcessResult:
    """Pure: returns computation + log data."""
    logs = []
    logs.append(f"Processing order {order['id']}")

    if order['amount'] > 1000:
        logs.append(f"WARNING: Large order: ${order['amount']}")

    total = order['amount'] * 1.1
    logs.append(f"Order total: ${total}")

    return ProcessResult(total=total, log_messages=tuple(logs))

# I/O boundary: logging effect
def process_order(order: dict) -> float:
    """Orchestration: computation + logging."""
    # Pure: calculation
    result = process_order_pure(order)

    # Effect: log messages
    import logging
    for message in result.log_messages:
        if 'WARNING' in message:
            logging.warning(message)
        else:
            logging.info(message)

    return result.total
```

---

## Examples

### Example 1: Configuration File Loading

**I/O Isolated**:
```python
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    api_key: str
    endpoint: str
    timeout: int

# Pure: validates and constructs config
def parse_config(data: dict) -> Config:
    """Pure: parses config from dict."""
    required = ['api_key', 'endpoint', 'timeout']
    for field in required:
        if field not in data:
            raise ValueError(f"Missing config field: {field}")

    return Config(
        api_key=data['api_key'],
        endpoint=data['endpoint'],
        timeout=data['timeout']
    )

# Effect: reads file
def load_config_file(path: str) -> dict:
    """Effect: reads JSON config file."""
    with open(path, 'r') as f:
        return json.load(f)

# Orchestration
def load_config(path: str) -> Config:
    """Loads and parses config."""
    # Effect: I/O
    raw_data = load_config_file(path)

    # Pure: parsing
    return parse_config(raw_data)
```

### Example 2: CSV Processing

**I/O Isolated**:
```python
# Pure: transforms CSV rows
def transform_csv_rows(rows: list[list[str]]) -> list[dict]:
    """Pure: converts CSV rows to dicts."""
    if not rows:
        return []

    headers = rows[0]
    return [
        dict(zip(headers, row))
        for row in rows[1:]
    ]

# Effect: reads CSV
def read_csv_file(path: str) -> list[list[str]]:
    """Effect: reads CSV file."""
    import csv
    with open(path, 'r') as f:
        reader = csv.reader(f)
        return list(reader)

# Effect: writes CSV
def write_csv_file(path: str, rows: list[list[str]]) -> None:
    """Effect: writes CSV file."""
    import csv
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
```

---

## Edge Cases

### Edge Case 1: Unavoidable I/O
**Scenario**: Function fundamentally requires I/O
**Issue**: Cannot separate I/O from purpose
**Handling**:
- Mark function as effect boundary
- Keep logic minimal (just I/O)
- Document as necessary effect

**Example**:
```python
# Effect boundary: unavoidable I/O
def read_sensor_data() -> float:
    """Effect: reads from hardware sensor."""
    import hardware
    return hardware.sensor.read()  # Must perform I/O
```

### Edge Case 2: Streaming I/O
**Scenario**: Large data processed as stream
**Issue**: Cannot load entire dataset in memory
**Handling**:
- Use generator functions for lazy I/O
- Process in chunks with pure transformations
- Maintain I/O boundary with iterators

**Example**:
```python
# Effect: streaming file read
def stream_file_lines(path: str):
    """Effect: yields lines lazily."""
    with open(path, 'r') as f:
        for line in f:
            yield line

# Pure: transformation
def transform_line(line: str) -> str:
    """Pure: processes single line."""
    return line.strip().upper()

# Orchestration
def process_large_file(path: str, output_path: str):
    """Streams and processes large file."""
    with open(output_path, 'w') as out:
        for line in stream_file_lines(path):
            # Pure: transform
            processed = transform_line(line)
            # Effect: write
            out.write(processed + '\n')
```

### Edge Case 3: Transactional I/O
**Scenario**: Multiple I/O operations must be atomic
**Issue**: Transaction management at boundaries
**Handling**:
- Use context managers for transaction scope
- Return pure computation results
- Execute all I/O in transaction boundary

### Edge Case 4: Cached I/O
**Scenario**: Expensive I/O results should be cached
**Issue**: Caching is technically a side effect
**Handling**:
- Accept caching as controlled side effect
- Document caching behavior
- Use memoization for pure-looking interface

### Edge Case 5: Error Handling with I/O
**Scenario**: I/O operations can fail
**Issue**: Error handling complicates isolation
**Handling**:
- Use Result types for I/O operations
- Return errors as values, not exceptions
- Handle errors at orchestration layer

**Example**:
```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Success:
    content: str

@dataclass(frozen=True)
class Error:
    message: str

Result = Union[Success, Error]

# Effect: safe file read
def read_file_safe(path: str) -> Result:
    """Effect: reads file, returns Result."""
    try:
        with open(path, 'r') as f:
            return Success(content=f.read())
    except IOError as e:
        return Error(message=str(e))
```

---

## Database Operations

### Record I/O Isolation Metadata

```sql
-- Update function with I/O isolation status
UPDATE functions
SET
    has_io_operations = 0,  -- Pure after isolation
    io_isolation_strategy = 'repository_pattern',
    side_effects_json = 'null',
    purity_level = 'pure',
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'calculate_user_orders' AND file_id = ?;
```

### Query Functions with Inline I/O

```sql
-- Find functions with I/O operations
SELECT f.id, f.name, f.file_id, f.side_effects_json
FROM functions f
WHERE f.has_io_operations = 1
  AND json_extract(f.side_effects_json, '$.isolated') = 0
ORDER BY f.call_count DESC;
```

---

## Related Directives

### FP Directives
- **fp_purity**: Enforces pure functions (no I/O)
- **fp_side_effects_flag**: Detects and flags I/O operations
- **fp_side_effect_detection**: Identifies I/O for isolation
- **fp_logging_safety**: Specialized I/O isolation for logging

### Project Directives
- **project_compliance_check**: Validates I/O isolation
- **project_update_db**: Records isolation metadata

---

## Helper Functions

### `detect_io_calls(function_body) -> list[IoOperation]`
Identifies I/O operations within function.

**Signature**:
```python
def detect_io_calls(function_body: ASTNode) -> list[IoOperation]:
    """
    Scans for: file I/O, network calls, database queries,
    console I/O, external process calls.
    Returns list of I/O operations with locations.
    """
```

### `extract_pure_logic(function_def) -> FunctionDefinition`
Extracts pure business logic from I/O operations.

**Signature**:
```python
def extract_pure_logic(
    function_def: FunctionDefinition
) -> FunctionDefinition:
    """
    Separates pure computation from I/O effects.
    Returns pure function definition.
    """
```

### `generate_io_boundary(io_operations) -> list[FunctionDefinition]`
Creates I/O boundary functions for detected operations.

**Signature**:
```python
def generate_io_boundary(
    io_operations: list[IoOperation]
) -> list[FunctionDefinition]:
    """
    Generates effect functions for I/O operations.
    Returns list of I/O boundary function definitions.
    """
```

---

## Testing

### Test 1: Pure Logic Extraction
```python
def test_extract_pure_logic():
    # After isolation, logic should be pure
    def process_content(content: str) -> str:
        return content.upper()

    # Pure function: deterministic
    assert process_content("hello") == "HELLO"
    assert process_content("hello") == "HELLO"  # Same result
```

### Test 2: I/O Boundary Isolation
```python
def test_io_boundary():
    # I/O should be in separate functions
    def read_file(path: str) -> str:
        with open(path, 'r') as f:
            return f.read()

    # Test with mock or fixture file
    content = read_file('/tmp/test.txt')
    assert isinstance(content, str)
```

### Test 3: Repository Pattern
```python
def test_repository_isolation():
    # Pure logic with dependency injection
    from typing import Protocol

    class Repository(Protocol):
        def get_data(self) -> list: ...

    def process_data(repo: Repository) -> int:
        data = repo.get_data()  # I/O via dependency
        return len(data)  # Pure logic

    # Test with mock repository
    class MockRepo:
        def get_data(self):
            return [1, 2, 3]

    assert process_data(MockRepo()) == 3
```

---

## Common Mistakes

### Mistake 1: Incomplete I/O Isolation
**Problem**: Some I/O remains in logic functions

**Solution**: Extract all I/O to boundaries

```python
# ❌ Bad: partial isolation
def process_data(data):
    result = transform(data)  # Pure
    print(result)  # I/O still here!
    return result

# ✅ Good: complete isolation
def process_data(data):
    return transform(data)  # Fully pure

def display_result(result):
    print(result)  # I/O at boundary
```

### Mistake 2: Hidden I/O in Pure Functions
**Problem**: I/O hidden in called functions

**Solution**: Trace all function calls for I/O

```python
# ❌ Bad: hidden I/O
def calculate_total(items):
    return sum(item.fetch_price() for item in items)  # fetch_price does I/O!

# ✅ Good: explicit I/O
def fetch_prices(items):
    return [item.fetch_price() for item in items]  # Explicit I/O

def calculate_total(prices):
    return sum(prices)  # Pure
```

### Mistake 3: Leaky Abstractions
**Problem**: I/O details leak into pure logic

**Solution**: Use proper abstractions (protocols, interfaces)

```python
# ❌ Bad: leaky abstraction
def process_user(db_connection):
    cursor = db_connection.cursor()  # DB details in logic!
    cursor.execute("SELECT ...")

# ✅ Good: abstraction hides I/O
class UserRepository(Protocol):
    def find_user(self, id: int) -> User: ...

def process_user(repo: UserRepository, user_id: int):
    user = repo.find_user(user_id)  # I/O hidden behind protocol
    return transform_user(user)  # Pure logic
```

---

## Roadblocks

### Roadblock 1: Inline I/O
**Issue**: I/O operation embedded in business logic
**Resolution**: Move I/O to dedicated effect function

### Roadblock 2: External API Call
**Issue**: External dependency accessed directly in logic
**Resolution**: Wrap in effect boundary, use dependency injection

### Roadblock 3: Database Access
**Issue**: Database query inline with business logic
**Resolution**: Extract to repository layer, use repository pattern

---

## Integration Points

### With `fp_purity`
I/O isolation enables function purity.

### With `fp_side_effects_flag`
Detects I/O operations that need isolation.

### With `project_compliance_check`
Validates I/O properly isolated at boundaries.

---

## Intent Keywords

- `io`
- `input output`
- `effect isolation`
- `side effect`
- `file operations`
- `network calls`

---

## Confidence Threshold

**0.7** - High confidence for I/O isolation transformations.

---

## Notes

- All I/O should be at program boundaries (main, handlers, adapters)
- Pure logic should never perform I/O directly
- Repository pattern ideal for database I/O isolation
- Dependency injection enables testing of pure logic
- I/O functions should be minimal (just the effect)
- Log data can be returned for external logging
- Streaming I/O uses generators/iterators at boundaries
- Error handling with Result types maintains purity
- Cache results are acceptable controlled side effects
- Functional core, imperative shell architecture

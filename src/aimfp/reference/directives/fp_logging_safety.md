# fp_logging_safety

## Purpose

The `fp_logging_safety` directive ensures logging is functional and isolated from core business logic by redirecting logging to pure output streams or external effect handlers. It prevents stateful or side-effect-heavy logging inside pure functions by either returning log data as values or delegating logging to effect boundaries. This maintains function purity while still enabling observability and debugging.

**Category**: Side Effects
**Type**: FP Core
**Priority**: Medium
**Confidence Threshold**: 0.6

---

## Workflow

### Trunk
**`scan_for_logging`**: Analyze functions for logging statements (print, logging module, console.log, etc.).

### Branches

1. **`logging_inline`** → **`redirect_to_effect_handler`**
   - **Condition**: Logging statements embedded within function body
   - **Action**: Extract logging to effect boundary
   - **Details**: Return log data as values for external handling
   - **Output**: Pure function returning computation + log data

2. **`stateful_logger`** → **`refactor_to_pure_logger`**
   - **Condition**: Logger maintains mutable state or configuration
   - **Action**: Convert to stateless logging approach
   - **Details**: Use immutable log message construction
   - **Output**: Stateless logging mechanism

3. **`structured_logging`** → **`return_log_events`**
   - **Condition**: Function needs structured logging
   - **Action**: Return structured log events as data
   - **Details**: Create log event objects for external processing
   - **Output**: Log events as return values

4. **`no_logging`** → **`mark_safe`**
   - **Condition**: No logging detected
   - **Action**: Mark as logging-safe
   - **Output**: Compliance confirmation

5. **Fallback** → **`mark_safe`**
   - **Condition**: Logging already isolated
   - **Action**: Mark as compliant

### Error Handling
- **On failure**: Prompt user with logging isolation strategy
- **Low confidence** (< 0.6): Request review before refactoring

---

## Refactoring Strategies

### Strategy 1: Return Log Data Instead of Logging
Convert inline logging to log data return.

**Before (Python - Inline Logging)**:
```python
import logging

def process_payment(amount, payment_method):
    """Impure: logging side effects."""
    logging.info(f"Processing payment of ${amount}")

    if amount > 10000:
        logging.warning(f"Large payment detected: ${amount}")

    result = charge_payment(amount, payment_method)

    if result['success']:
        logging.info(f"Payment successful: {result['transaction_id']}")
    else:
        logging.error(f"Payment failed: {result['error']}")

    return result
```

**After (Python - Log Data Returned)**:
```python
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class LogMessage:
    level: Literal['info', 'warning', 'error']
    message: str

@dataclass(frozen=True)
class PaymentResult:
    success: bool
    transaction_id: str | None
    error: str | None
    logs: tuple[LogMessage, ...]

# Pure: returns computation + log data
def process_payment_pure(amount: float, payment_method: str) -> PaymentResult:
    """Pure: returns result and log messages."""
    logs = []
    logs.append(LogMessage('info', f"Processing payment of ${amount}"))

    if amount > 10000:
        logs.append(LogMessage('warning', f"Large payment detected: ${amount}"))

    result = charge_payment(amount, payment_method)

    if result['success']:
        logs.append(LogMessage(
            'info',
            f"Payment successful: {result['transaction_id']}"
        ))
        return PaymentResult(
            success=True,
            transaction_id=result['transaction_id'],
            error=None,
            logs=tuple(logs)
        )
    else:
        logs.append(LogMessage('error', f"Payment failed: {result['error']}"))
        return PaymentResult(
            success=False,
            transaction_id=None,
            error=result['error'],
            logs=tuple(logs)
        )

# Effect boundary: logging
def process_payment(amount: float, payment_method: str) -> dict:
    """Orchestration: computation + logging effect."""
    # Pure: calculation
    result = process_payment_pure(amount, payment_method)

    # Effect: log messages
    import logging
    for log in result.logs:
        if log.level == 'info':
            logging.info(log.message)
        elif log.level == 'warning':
            logging.warning(log.message)
        elif log.level == 'error':
            logging.error(log.message)

    return {
        'success': result.success,
        'transaction_id': result.transaction_id,
        'error': result.error
    }
```

### Strategy 2: Writer Monad for Logging
Use Writer monad pattern to accumulate logs.

**Before (Python - Inline Logging)**:
```python
import logging

def calculate_discount(price, customer_type):
    logging.info(f"Calculating discount for {customer_type}")

    if customer_type == 'premium':
        discount = price * 0.20
        logging.info(f"Applied premium discount: ${discount}")
    else:
        discount = price * 0.10
        logging.info(f"Applied standard discount: ${discount}")

    return discount
```

**After (Python - Writer Monad Pattern)**:
```python
from dataclasses import dataclass
from typing import TypeVar, Callable, Generic

T = TypeVar('T')

@dataclass(frozen=True)
class Writer(Generic[T]):
    """Writer monad carrying value and log messages."""
    value: T
    log: tuple[str, ...]

    def bind(self, func: Callable[[T], 'Writer']) -> 'Writer':
        """Monadic bind: chains computations with logs."""
        result = func(self.value)
        return Writer(
            value=result.value,
            log=self.log + result.log
        )

    def map(self, func: Callable[[T], T]) -> 'Writer':
        """Maps function over value, preserving log."""
        return Writer(value=func(self.value), log=self.log)

    @staticmethod
    def pure(value: T) -> 'Writer[T]':
        """Creates Writer with value and empty log."""
        return Writer(value=value, log=())

    def tell(self, message: str) -> 'Writer[T]':
        """Adds log message."""
        return Writer(value=self.value, log=self.log + (message,))

# Pure computation with logging
def calculate_discount_pure(price: float, customer_type: str) -> Writer[float]:
    """Pure: returns Writer with result and logs."""
    w = Writer.pure(price).tell(f"Calculating discount for {customer_type}")

    if customer_type == 'premium':
        discount = price * 0.20
        return Writer(discount, w.log + (f"Applied premium discount: ${discount}",))
    else:
        discount = price * 0.10
        return Writer(discount, w.log + (f"Applied standard discount: ${discount}",))

# Effect boundary
def calculate_discount(price: float, customer_type: str) -> float:
    """Orchestration: runs pure computation, logs messages."""
    result = calculate_discount_pure(price, customer_type)

    # Effect: logging
    import logging
    for message in result.log:
        logging.info(message)

    return result.value
```

### Strategy 3: Structured Logging Events
Return structured log events as objects.

**Before (JavaScript - Inline Logging)**:
```javascript
function processOrder(order) {
  console.log(`Processing order ${order.id}`);

  const total = order.items.reduce((sum, item) => sum + item.price, 0);
  console.log(`Order total: $${total}`);

  if (total > 1000) {
    console.warn(`High-value order: $${total}`);
  }

  return { orderId: order.id, total };
}
```

**After (JavaScript - Structured Log Events)**:
```javascript
// Pure: returns result and structured events
function processOrderPure(order) {
  const events = [];

  events.push({
    level: 'info',
    message: `Processing order ${order.id}`,
    context: { orderId: order.id },
    timestamp: Date.now()
  });

  const total = order.items.reduce((sum, item) => sum + item.price, 0);

  events.push({
    level: 'info',
    message: `Order total: $${total}`,
    context: { orderId: order.id, total },
    timestamp: Date.now()
  });

  if (total > 1000) {
    events.push({
      level: 'warn',
      message: `High-value order: $${total}`,
      context: { orderId: order.id, total },
      timestamp: Date.now()
    });
  }

  return {
    result: { orderId: order.id, total },
    events
  };
}

// Effect boundary
function processOrder(order) {
  const { result, events } = processOrderPure(order);

  // Effect: emit structured logs
  events.forEach(event => {
    const logFn = event.level === 'warn' ? console.warn : console.log;
    logFn(JSON.stringify(event));
  });

  return result;
}
```

### Strategy 4: Tracing Without Side Effects
Return execution trace for debugging.

**Before (Python - Debug Logging)**:
```python
import logging

def complex_calculation(x, y):
    logging.debug(f"Input: x={x}, y={y}")

    step1 = x * 2
    logging.debug(f"After step 1: {step1}")

    step2 = step1 + y
    logging.debug(f"After step 2: {step2}")

    result = step2 ** 2
    logging.debug(f"Final result: {result}")

    return result
```

**After (Python - Trace as Return Value)**:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class TraceStep:
    step: str
    value: float
    description: str

@dataclass(frozen=True)
class CalculationResult:
    result: float
    trace: tuple[TraceStep, ...]

# Pure: returns result with execution trace
def complex_calculation_traced(x: float, y: float) -> CalculationResult:
    """Pure: returns result and execution trace."""
    trace = []
    trace.append(TraceStep('input', x, f"Input: x={x}, y={y}"))

    step1 = x * 2
    trace.append(TraceStep('step1', step1, f"After step 1: {step1}"))

    step2 = step1 + y
    trace.append(TraceStep('step2', step2, f"After step 2: {step2}"))

    result = step2 ** 2
    trace.append(TraceStep('result', result, f"Final result: {result}"))

    return CalculationResult(result=result, trace=tuple(trace))

# Effect boundary
def complex_calculation(x: float, y: float) -> float:
    """Orchestration: computation + optional trace logging."""
    calc_result = complex_calculation_traced(x, y)

    # Effect: log trace (optional, based on debug mode)
    import os
    if os.getenv('DEBUG'):
        import logging
        for step in calc_result.trace:
            logging.debug(f"{step.step}: {step.description}")

    return calc_result.result
```

### Strategy 5: Logger as Dependency Injection
Pass logger as parameter instead of using global.

**Before (Python - Global Logger)**:
```python
import logging

logger = logging.getLogger(__name__)  # Global state

def process_data(data):
    logger.info("Processing started")
    result = transform(data)
    logger.info("Processing complete")
    return result
```

**After (Python - Logger Dependency)**:
```python
from typing import Protocol

class Logger(Protocol):
    """Logger interface."""
    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...

# Pure logic with optional logging callback
def process_data_pure(
    data: list,
    log: Logger | None = None
) -> list:
    """Pure with optional logging via dependency."""
    if log:
        log.info("Processing started")

    result = transform(data)

    if log:
        log.info("Processing complete")

    return result

# Or better: return log data
@dataclass(frozen=True)
class ProcessResult:
    data: list
    log_messages: tuple[str, ...]

def process_data_with_logs(data: list) -> ProcessResult:
    """Pure: returns result and log messages."""
    logs = []
    logs.append("Processing started")

    result = transform(data)

    logs.append("Processing complete")

    return ProcessResult(data=result, log_messages=tuple(logs))
```

---

## Examples

### Example 1: Error Logging

**Logging-Safe**:
```python
from dataclasses import dataclass
from typing import Union

@dataclass(frozen=True)
class Success:
    value: float
    log: str

@dataclass(frozen=True)
class Failure:
    error: str
    log: str

Result = Union[Success, Failure]

def divide_with_logging(a: float, b: float) -> Result:
    """Pure: returns result with log message."""
    if b == 0:
        return Failure(
            error="Division by zero",
            log=f"ERROR: Attempted division {a}/{b}"
        )

    result = a / b
    return Success(
        value=result,
        log=f"INFO: Successfully divided {a}/{b} = {result}"
    )

# Effect boundary
def divide(a: float, b: float) -> float:
    result = divide_with_logging(a, b)

    import logging
    if isinstance(result, Success):
        logging.info(result.log)
        return result.value
    else:
        logging.error(result.log)
        raise ValueError(result.error)
```

### Example 2: Performance Logging

**Logging-Safe (TypeScript)**:
```typescript
interface PerformanceLog {
  operation: string;
  duration: number;
  timestamp: number;
}

interface OperationResult<T> {
  value: T;
  performanceLog: PerformanceLog;
}

// Pure: returns result with performance data
function expensiveOperation<T>(
  operation: () => T,
  operationName: string
): OperationResult<T> {
  const start = performance.now();
  const value = operation();
  const duration = performance.now() - start;

  return {
    value,
    performanceLog: {
      operation: operationName,
      duration,
      timestamp: Date.now()
    }
  };
}

// Effect boundary
function runWithLogging<T>(
  operation: () => T,
  name: string
): T {
  const result = expensiveOperation(operation, name);

  // Effect: log performance
  console.log(`${result.performanceLog.operation}: ${result.performanceLog.duration}ms`);

  return result.value;
}
```

---

## Edge Cases

### Edge Case 1: Conditional Logging
**Scenario**: Logging depends on log level configuration
**Issue**: Configuration state affects logging behavior
**Handling**:
- Return all log messages with levels
- Filter at effect boundary based on config
- Keep pure function independent of log level

### Edge Case 2: Async Logging
**Scenario**: Logging to external service is async
**Issue**: Async operations are effects
**Handling**:
- Return log events as data
- Handle async logging at boundary
- Use async effect handlers

### Edge Case 3: Contextual Logging
**Scenario**: Logs need request ID or trace context
**Issue**: Context propagation through call stack
**Handling**:
- Pass context as explicit parameter
- Include context in returned log events
- Use correlation IDs in log data

### Edge Case 4: Performance-Critical Paths
**Scenario**: Creating log objects impacts performance
**Issue**: Log data construction has overhead
**Handling**:
- Use lazy evaluation for log messages
- Only construct logs if actually needed
- Profile before optimizing

### Edge Case 5: Log Aggregation
**Scenario**: Logs from multiple functions need aggregation
**Issue**: Combining logs from nested calls
**Handling**:
- Use Writer monad for automatic log accumulation
- Collect logs at orchestration layer
- Flatten nested log structures

---

## Database Operations

### Record Logging Safety Metadata

**Use helper functions** for all project.db operations. Query available helpers.

**IMPORTANT**: Never use direct SQL for project.db - always use helpers or call project directives (like project_file_write).

---

## Related Directives

### FP Directives
- **fp_purity**: Ensures functions remain pure (no logging side effects)
- **fp_side_effects_flag**: Detects logging as side effect
- **fp_io_isolation**: General I/O isolation (logging is special case)

### Project Directives
- **project_compliance_check**: Validates logging isolation
- **project_update_db**: Records logging safety metadata

---

## Helper Functions

### `detect_logging_calls(function_body) -> list[LogStatement]`
Identifies logging statements in function.

**Signature**:
```python
def detect_logging_calls(function_body: ASTNode) -> list[LogStatement]:
    """
    Detects: print(), logging.*, console.log(), etc.
    Returns list of logging statements with locations.
    """
```

### `extract_log_messages(function_def) -> list[str]`
Extracts log message content from function.

**Signature**:
```python
def extract_log_messages(
    function_def: FunctionDefinition
) -> list[str]:
    """
    Parses logging statements to extract message strings.
    Returns list of log messages.
    """
```

---

## Testing

### Test 1: Log Data Return
```python
def test_returns_log_data():
    result = process_with_logging(42)

    assert hasattr(result, 'log_messages')
    assert len(result.log_messages) > 0
    assert isinstance(result.log_messages[0], str)
```

### Test 2: No Logging Side Effects
```python
def test_no_logging_side_effects(capsys):
    # Pure function should not log
    result = pure_calculation(10, 20)

    captured = capsys.readouterr()
    assert captured.out == ""  # No console output
    assert captured.err == ""
```

### Test 3: Structured Logging
```python
def test_structured_log_events():
    result = process_order_pure(order)

    assert 'events' in result
    for event in result['events']:
        assert 'level' in event
        assert 'message' in event
        assert 'context' in event
```

---

## Common Mistakes

### Mistake 1: Forgetting to Return Logs
**Problem**: Pure function doesn't return log data

**Solution**: Always return logs as part of result

```python
# ❌ Bad: no log data
def calculate(x):
    # Where do logs go?
    return x * 2

# ✅ Good: returns logs
def calculate(x):
    return {'result': x * 2, 'logs': ['Calculated x * 2']}
```

### Mistake 2: Using Print for Logging
**Problem**: print() is a side effect

**Solution**: Return print data for external output

```python
# ❌ Bad: print side effect
def process(x):
    print(f"Processing {x}")
    return x * 2

# ✅ Good: return output data
def process(x):
    return {'result': x * 2, 'output': f"Processing {x}"}
```

### Mistake 3: Global Logger Usage
**Problem**: Global logger is mutable state

**Solution**: Pass logger as dependency or return log data

```python
# ❌ Bad: global logger
import logging
logger = logging.getLogger()

def process(x):
    logger.info("Processing")

# ✅ Good: dependency injection
def process(x, logger=None):
    if logger:
        logger.info("Processing")
    return x * 2
```

---

## Roadblocks

### Roadblock 1: Inline Logging
**Issue**: Logging statements within business logic
**Resolution**: Extract logging, return log data

### Roadblock 2: Mutable Logger
**Issue**: Logger maintains state or configuration
**Resolution**: Use stateless logger or return log messages

### Roadblock 3: Complex Log Context
**Issue**: Logs need contextual information
**Resolution**: Pass context explicitly, include in log events

---

## Integration Points

### With `fp_purity`
Logging isolation enables function purity.

### With `fp_io_isolation`
Logging is specialized form of I/O isolation.

### With `project_compliance_check`
Validates logging properly isolated.

---

## Intent Keywords

- `log`
- `logger`
- `output safety`
- `logging isolation`
- `structured logging`

---

## Confidence Threshold

**0.6** - Moderate confidence for logging isolation.

---

## Notes

- Logging is a side effect and breaks purity
- Return log messages as data instead of logging inline
- Effect boundaries handle actual logging
- Writer monad pattern accumulates logs functionally
- Structured logging: return log events as objects
- Debug tracing can return execution traces
- Logger dependency injection for flexibility
- Log levels determined at effect boundary
- Performance: lazy evaluate expensive log construction
- Contextual logging: pass context as parameter

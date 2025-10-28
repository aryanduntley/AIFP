# fp_task_isolation

## Purpose

The `fp_task_isolation` directive enforces isolation between parallel or async tasks by ensuring no data is shared or leaked between tasks. It maintains purity across concurrent functional tasks by cloning data, using message passing, or ensuring complete independence. This prevents subtle bugs from shared state in concurrent systems while maintaining functional programming principles.

**Category**: Concurrency
**Type**: FP Core
**Priority**: High
**Confidence Threshold**: 0.7

---

## Workflow

### Trunk
**`analyze_task_flows`**: Examine concurrent/async task execution for data sharing and leakage.

### Branches

1. **`shared_state`** → **`duplicate_or_pass_copy`**
   - **Condition**: Tasks share data structures
   - **Action**: Create independent copies for each task
   - **Details**: Deep copy mutable data, ensure isolation
   - **Output**: Isolated task data

2. **`safe_isolation`** → **`approve_task`**
   - **Condition**: Tasks operate on independent data
   - **Action**: Mark as safely isolated
   - **Output**: Task isolation confirmation

3. **`closure_capture`** → **`validate_captures`**
   - **Condition**: Task closure captures external variables
   - **Action**: Validate captured variables are immutable
   - **Details**: Ensure no mutable reference escapes
   - **Output**: Safe closure validation

4. **`message_passing`** → **`validate_channel_safety`**
   - **Condition**: Tasks communicate via message passing
   - **Action**: Verify messages are immutable or owned
   - **Details**: Check ownership transfer or copy semantics
   - **Output**: Safe message passing confirmation

5. **Fallback** → **`prompt_user`**
   - **Condition**: Task isolation unclear
   - **Action**: Request clarification on data sharing

### Error Handling
- **On failure**: Prompt user with task isolation analysis
- **Low confidence** (< 0.7): Request review before approving

---

## Refactoring Strategies

### Strategy 1: Data Cloning for Task Independence
Ensure each task operates on independent data copy.

**Before (Python - Shared Data)**:
```python
import asyncio

data = {"count": 0}  # Shared mutable data

async def task_a():
    # Modifies shared data
    data["count"] += 1
    await asyncio.sleep(0.1)
    return data["count"]

async def task_b():
    # Also modifies shared data (race condition!)
    data["count"] += 10
    await asyncio.sleep(0.1)
    return data["count"]

# Tasks share mutable state
results = await asyncio.gather(task_a(), task_b())
```

**After (Python - Isolated Data)**:
```python
import asyncio
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class TaskData:
    """Immutable task data."""
    count: int

async def task_a(data: TaskData) -> TaskData:
    """Operates on independent copy."""
    await asyncio.sleep(0.1)
    return replace(data, count=data.count + 1)

async def task_b(data: TaskData) -> TaskData:
    """Operates on independent copy."""
    await asyncio.sleep(0.1)
    return replace(data, count=data.count + 10)

# Each task gets independent data
initial_data = TaskData(count=0)
results = await asyncio.gather(
    task_a(initial_data),
    task_b(initial_data)
)
```

### Strategy 2: Message Passing for Inter-Task Communication
Use message queues instead of shared memory.

**Before (Python - Shared Memory)**:
```python
import threading

shared_results = []  # Shared mutable list

def producer():
    for i in range(10):
        shared_results.append(i * 2)  # Race condition!

def consumer():
    while len(shared_results) < 10:
        pass  # Busy wait
    return sum(shared_results)
```

**After (Python - Message Passing)**:
```python
from queue import Queue
import threading

def producer(queue: Queue):
    """Sends messages via queue."""
    for i in range(10):
        queue.put(i * 2)
    queue.put(None)  # Sentinel

def consumer(queue: Queue) -> int:
    """Receives messages via queue."""
    results = []
    while True:
        item = queue.get()
        if item is None:
            break
        results.append(item)
    return sum(results)

# Message passing isolates tasks
message_queue = Queue()
producer_thread = threading.Thread(target=producer, args=(message_queue,))
producer_thread.start()
result = consumer(message_queue)
producer_thread.join()
```

### Strategy 3: Immutable Captures in Closures
Ensure closures only capture immutable data.

**Before (JavaScript - Mutable Capture)**:
```javascript
// Mutable captured variable (dangerous!)
let counter = 0;

async function createTasks() {
  const tasks = [];

  for (let i = 0; i < 5; i++) {
    tasks.push(async () => {
      counter++;  // Shared mutable state!
      return counter;
    });
  }

  return await Promise.all(tasks.map(t => t()));
}
```

**After (JavaScript - Immutable Capture)**:
```javascript
async function createTasks() {
  const tasks = [];

  for (let i = 0; i < 5; i++) {
    // Capture immutable value
    const value = i;

    tasks.push(async () => {
      // Operates on captured immutable value
      return value * 2;
    });
  }

  return await Promise.all(tasks.map(t => t()));
}

// Or return new state instead of mutating
async function createTasksWithState(initialCounter: number) {
  const tasks = [];

  for (let i = 0; i < 5; i++) {
    tasks.push(async (count: number) => {
      return count + 1;  // Returns new value
    });
  }

  let counter = initialCounter;
  const results = [];

  for (const task of tasks) {
    counter = await task(counter);
    results.push(counter);
  }

  return results;
}
```

### Strategy 4: Actor Model for Task Isolation
Use actor pattern to encapsulate state per task.

**Before (Python - Shared State)**:
```python
# Shared state between tasks
user_sessions = {}

async def handle_request(user_id, action):
    # Multiple tasks might modify same user session
    if user_id not in user_sessions:
        user_sessions[user_id] = {"actions": []}

    user_sessions[user_id]["actions"].append(action)  # Race!
    return user_sessions[user_id]
```

**After (Python - Actor Pattern)**:
```python
import asyncio
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class UserSession:
    """Immutable session snapshot."""
    user_id: int
    actions: tuple[str, ...] = field(default_factory=tuple)

@dataclass
class Message:
    kind: Literal["get_session", "add_action"]
    user_id: int
    action: str | None = None
    reply_to: asyncio.Queue | None = None

class UserSessionActor:
    """Actor managing user sessions (isolated state)."""

    def __init__(self):
        self.sessions: dict[int, UserSession] = {}
        self.inbox = asyncio.Queue()

    async def run(self):
        """Process messages from inbox."""
        while True:
            msg = await self.inbox.get()

            if msg.kind == "get_session":
                session = self.sessions.get(
                    msg.user_id,
                    UserSession(user_id=msg.user_id)
                )
                await msg.reply_to.put(session)

            elif msg.kind == "add_action":
                current = self.sessions.get(
                    msg.user_id,
                    UserSession(user_id=msg.user_id)
                )
                # Create new immutable session
                updated = UserSession(
                    user_id=msg.user_id,
                    actions=current.actions + (msg.action,)
                )
                self.sessions[msg.user_id] = updated

    async def send(self, msg: Message):
        """Send message to actor."""
        await self.inbox.put(msg)

# Usage: isolated actor handles state
actor = UserSessionActor()
asyncio.create_task(actor.run())

async def handle_request(actor: UserSessionActor, user_id: int, action: str):
    """Communicates with actor via messages."""
    # Send message to isolated actor
    await actor.send(Message(
        kind="add_action",
        user_id=user_id,
        action=action
    ))

    # Query session
    reply_queue = asyncio.Queue()
    await actor.send(Message(
        kind="get_session",
        user_id=user_id,
        reply_to=reply_queue
    ))
    session = await reply_queue.get()
    return session
```

### Strategy 5: Ownership Transfer (Rust-Style)
Transfer ownership instead of sharing.

**Conceptual (Python with Ownership Semantics)**:
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class OwnedData:
    """Data with ownership tracking."""
    value: list
    _owned: bool = True

    def take(self) -> list:
        """Transfers ownership (consumes self)."""
        if not self._owned:
            raise ValueError("Data already moved")
        self._owned = False
        return self.value

    def is_owned(self) -> bool:
        return self._owned

# Task A owns data initially
data_a = OwnedData(value=[1, 2, 3])

# Transfer ownership to task B
def task_b(data: list):
    return [x * 2 for x in data]

# Take ownership (data_a no longer valid)
transferred_data = data_a.take()
result = task_b(transferred_data)

# Attempting to use data_a again would raise error
# data_a.take()  # ValueError: Data already moved
```

---

## Examples

### Example 1: Async Task Isolation

**Isolated Tasks (Python)**:
```python
import asyncio
from dataclasses import dataclass

@dataclass(frozen=True)
class UserData:
    user_id: int
    name: str

async def fetch_user(user_id: int) -> UserData:
    """Isolated async task."""
    await asyncio.sleep(0.1)
    return UserData(user_id=user_id, name=f"User{user_id}")

async def process_user(user: UserData) -> dict:
    """Isolated processing."""
    await asyncio.sleep(0.1)
    return {"id": user.user_id, "display": user.name.upper()}

async def process_users_isolated(user_ids: list[int]) -> list[dict]:
    """Each task operates independently."""
    # Fetch all users (isolated tasks)
    users = await asyncio.gather(*[fetch_user(uid) for uid in user_ids])

    # Process all users (isolated tasks)
    return await asyncio.gather(*[process_user(u) for u in users])
```

### Example 2: Thread Pool with Data Isolation

**Isolated Threads (Python)**:
```python
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import copy

@dataclass
class WorkItem:
    id: int
    data: list

def process_work_item(item: WorkItem) -> dict:
    """Pure function: operates on copy."""
    # Defensive copy to ensure isolation
    data_copy = copy.deepcopy(item.data)

    # Process copy (doesn't affect original)
    processed = [x * 2 for x in data_copy]

    return {"id": item.id, "result": processed}

def process_items_isolated(items: list[WorkItem]) -> list[dict]:
    """Thread pool with isolated data."""
    with ThreadPoolExecutor() as executor:
        return list(executor.map(process_work_item, items))
```

---

## Edge Cases

### Edge Case 1: Nested Task Spawning
**Scenario**: Tasks spawn child tasks
**Issue**: Child tasks might share parent's mutable state
**Handling**:
- Pass immutable data to child tasks
- Use message passing for parent-child communication
- Document task hierarchy and data flow

### Edge Case 2: Callback Closures
**Scenario**: Callbacks capture mutable context
**Issue**: Multiple callbacks share mutable closure
**Handling**:
- Capture immutable snapshots
- Pass context as explicit parameters
- Use partial application for parameter binding

### Edge Case 3: Shared Immutable Data (Optimization)
**Scenario**: Large immutable data structure shared between tasks
**Issue**: Copying would be expensive
**Handling**:
- Allow sharing if truly immutable
- Use structural sharing (copy-on-write)
- Document shared immutable optimization

### Edge Case 4: Task Cancellation
**Scenario**: Task cancelled while holding resources
**Issue**: Resource cleanup with isolation
**Handling**:
- Use context managers for resource cleanup
- Ensure cleanup happens even on cancellation
- Isolate cleanup to task boundary

### Edge Case 5: Global State Access
**Scenario**: Tasks read global configuration
**Issue**: Configuration changes during execution
**Handling**:
- Capture config snapshot at task creation
- Pass config as explicit parameter
- Use immutable config objects

---

## Database Operations

### Record Task Isolation Metadata

```sql
-- Update function with task isolation info
UPDATE functions
SET
    has_task_isolation = 1,
    isolation_strategy = 'data_cloning',
    concurrency_metadata = json_set(
        COALESCE(concurrency_metadata, '{}'),
        '$.task_isolation',
        'safe'
    ),
    updated_at = CURRENT_TIMESTAMP
WHERE name = 'process_users_isolated' AND file_id = ?;

-- Record isolation validation
INSERT INTO notes (project_id, content, tags, created_at)
VALUES (
    1,
    'Validated task isolation in process_users_isolated: each task operates on independent data',
    '["fp_task_isolation", "concurrency", "validation"]',
    CURRENT_TIMESTAMP
);
```

---

## Related Directives

### FP Directives
- **fp_parallel_purity**: Validates parallel tasks are pure
- **fp_concurrency_safety**: General concurrency safety
- **fp_immutability**: Immutable data enables safe task isolation

### Project Directives
- **project_compliance_check**: Validates task isolation
- **project_update_db**: Records isolation metadata

---

## Helper Functions

### `detect_shared_task_data(tasks) -> list[SharedData]`
Identifies data shared between tasks.

**Signature**:
```python
def detect_shared_task_data(
    tasks: list[TaskDefinition]
) -> list[SharedData]:
    """
    Analyzes task definitions for shared data access.
    Returns list of shared data references.
    """
```

### `validate_closure_captures(task) -> list[CaptureViolation]`
Checks that closures only capture immutable data.

**Signature**:
```python
def validate_closure_captures(
    task: TaskDefinition
) -> list[CaptureViolation]:
    """
    Examines closure captures for mutable references.
    Returns list of unsafe captures.
    """
```

---

## Testing

### Test 1: Data Independence
```python
def test_task_data_independence():
    import copy

    original_data = [1, 2, 3]

    def task(data):
        data_copy = copy.deepcopy(data)
        data_copy.append(4)
        return data_copy

    result = task(original_data)

    # Original data unchanged (independent)
    assert original_data == [1, 2, 3]
    assert result == [1, 2, 3, 4]
```

### Test 2: No Shared Mutable State
```python
def test_no_shared_state():
    import asyncio

    async def task(value):
        await asyncio.sleep(0.01)
        return value * 2

    async def run_tasks():
        # Each task operates independently
        return await asyncio.gather(
            task(1),
            task(2),
            task(3)
        )

    result = asyncio.run(run_tasks())
    assert result == [2, 4, 6]
```

---

## Common Mistakes

### Mistake 1: Shared Mutable Closure
**Problem**: Tasks share mutable variable via closure

**Solution**: Capture immutable snapshot

```python
# ❌ Bad: shared mutable closure
tasks = []
for i in range(5):
    tasks.append(lambda: results.append(i))  # Shared 'results'!

# ✅ Good: isolated data
tasks = []
for i in range(5):
    value = i  # Capture immutable value
    tasks.append(lambda v=value: v * 2)
```

### Mistake 2: Shallow Copy
**Problem**: Shallow copy shares nested mutable objects

**Solution**: Use deep copy for complete isolation

```python
# ❌ Bad: shallow copy
import copy
data_copy = copy.copy(original)  # Nested objects shared!

# ✅ Good: deep copy
data_copy = copy.deepcopy(original)  # Fully independent
```

### Mistake 3: Global State in Tasks
**Problem**: Tasks read/write global variables

**Solution**: Pass all data explicitly

```python
# ❌ Bad: global state
global_config = {}

async def task():
    return process(global_config)  # Shared global!

# ✅ Good: explicit parameter
async def task(config):
    return process(config)
```

---

## Roadblocks

### Roadblock 1: Shared State
**Issue**: Tasks access same mutable data
**Resolution**: Use immutable copies, message passing

### Roadblock 2: Mutable Closure Capture
**Issue**: Closure captures mutable variable
**Resolution**: Capture immutable snapshot or pass explicitly

### Roadblock 3: Resource Sharing
**Issue**: Tasks share limited resource (file handle, connection)
**Resolution**: Use resource pooling, message passing for coordination

---

## Integration Points

### With `fp_parallel_purity`
Task isolation enables parallel purity.

### With `fp_concurrency_safety`
Isolation prevents concurrency bugs.

### With `project_compliance_check`
Validates task isolation across codebase.

---

## Intent Keywords

- `task isolation`
- `async`
- `parallel safety`
- `data independence`
- `message passing`

---

## Confidence Threshold

**0.7** - High confidence for task isolation validation.

---

## Notes

- Tasks should operate on independent data
- Immutable data naturally isolated
- Deep copy ensures complete independence
- Message passing prevents shared state
- Actor model encapsulates isolated state
- Ownership transfer (move semantics) eliminates sharing
- Closures: only capture immutable values
- Async tasks: ensure no shared mutable state
- Resource sharing: use coordination primitives
- Configuration: capture snapshot at task creation

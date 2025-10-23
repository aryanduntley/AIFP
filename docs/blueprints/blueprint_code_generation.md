# Code Generation Blueprint

## Overview

This blueprint defines the code generation system that converts validated user directives into FP-compliant Python implementation code. The generated code follows AIFP's functional programming principles while implementing real-time execution for user directives.

---

## Code Generation Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Validated Directive (from user_directives.db)   │
│  - Trigger configuration                                 │
│  - Action configuration                                  │
│  - Dependencies                                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│           Implementation Type Analyzer                   │
│  Determines: handler | scheduler | service | function    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌─────────────┐ ┌────────────┐ ┌────────────┐
│Event        │ │Time-Based  │ │Condition   │
│Handler      │ │Scheduler   │ │Monitor     │
│Template     │ │Template    │ │Template    │
└─────────────┘ └────────────┘ └────────────┘
        │            │            │
        └────────────┼────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Template Processor                          │
│  - Apply FP directives                                   │
│  - Generate pure functions                               │
│  - Isolate side effects                                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│            Generated Code (Python)                       │
│  .aifp/user-directives/generated/                       │
│    - handlers/ schedulers/ services/ utils/             │
└─────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│         Database Updates                                 │
│  - directive_implementations table                       │
│  - project.db (files, functions)                         │
└─────────────────────────────────────────────────────────┘
```

---

## FP Principles Applied

### 1. Pure Functions for Logic
- All business logic in pure functions
- Same inputs → same outputs
- No side effects in logic functions

### 2. Immutable Configuration
- Configuration stored in frozen dataclasses
- No runtime modification of config

### 3. Effect Isolation
- Side effects (API calls, file I/O) isolated in "effect functions"
- Clear separation between logic and effects

### 4. Explicit Dependencies
- All dependencies passed as parameters
- No hidden global state

### 5. Type Safety
- Type hints for all functions
- Dataclasses for structured data

---

## Implementation Templates

### Template 1: Time-Based Scheduler

**Use Case**: Execute action at specific times (e.g., "At 5pm turn off lights")

**Generated Code Structure**:
```python
# .aifp/user-directives/generated/schedulers/<directive_name>_scheduler.py

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Configuration (immutable)
@dataclass(frozen=True)
class {DirectiveName}Config:
    trigger_time: str                    # e.g., "17:00"
    timezone: str                        # e.g., "America/New_York"
    {action_specific_config}             # API URL, entity IDs, etc.

# Pure function: Build action payload
def build_{action_name}_payload(config: {DirectiveName}Config) -> Dict[str, any]:
    """
    Pure function: Build payload for {action_name}.

    Args:
        config: Immutable configuration

    Returns:
        Action payload dictionary
    """
    return {
        {payload_fields}
    }

# Effect function: Execute action (isolated side effect)
def execute_{action_name}(config: {DirectiveName}Config,
                          payload: Dict[str, any]) -> Optional[str]:
    """
    Effect function: Execute {action_name}.

    Args:
        config: Immutable configuration
        payload: Action payload

    Returns:
        Result status or error message
    """
    try:
        # Side effect: API call, script execution, etc.
        {action_execution_code}

        logging.info(f"{directive_name}: {action_name} executed successfully")
        return "success"

    except Exception as e:
        logging.error(f"{directive_name}: {action_name} failed: {e}")
        return f"error: {str(e)}"

# Main handler (composes pure and effect functions)
def handle_{directive_name}():
    """
    Main handler for {directive_name} directive.
    Composes pure functions and effect functions.
    """
    config = {DirectiveName}Config(
        trigger_time="{trigger_time}",
        timezone="{timezone}",
        {config_initialization}
    )

    # Pure function: build payload
    payload = build_{action_name}_payload(config)

    # Effect function: execute action
    result = execute_{action_name}(config, payload)

    # Effect: log execution
    log_execution("{directive_name}", result)

    return result

# Scheduler setup (entry point)
def setup_scheduler() -> BackgroundScheduler:
    """
    Set up APScheduler for {directive_name}.

    Returns:
        Configured scheduler instance
    """
    scheduler = BackgroundScheduler(timezone="{timezone}")

    # Parse cron expression from time
    hour, minute = parse_time("{trigger_time}")

    scheduler.add_job(
        handle_{directive_name},
        CronTrigger(hour=hour, minute=minute, timezone="{timezone}"),
        id="{directive_name}",
        name="{description}",
        replace_existing=True
    )

    return scheduler

# Main execution
if __name__ == "__main__":
    setup_logging()
    scheduler = setup_scheduler()
    scheduler.start()

    logging.info("{directive_name} scheduler started")

    try:
        # Keep scheduler running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("{directive_name} scheduler stopped")
```

---

### Template 2: Condition Monitor Service

**Use Case**: Monitor conditions and execute when met (e.g., "If stove on > 20 min, turn off")

**Generated Code Structure**:
```python
# .aifp/user-directives/generated/services/<directive_name>_service.py

from typing import Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import time
import logging

# Configuration (immutable)
@dataclass(frozen=True)
class {DirectiveName}Config:
    check_interval: int                  # Seconds between checks
    condition_threshold: float           # Threshold value
    {condition_specific_config}          # Device IDs, state variables, etc.

# Pure function: Evaluate condition
def evaluate_{condition_name}(current_state: Dict[str, any],
                              config: {DirectiveName}Config) -> bool:
    """
    Pure function: Evaluate condition expression.

    Args:
        current_state: Current state of monitored entities
        config: Immutable configuration

    Returns:
        True if condition is met, False otherwise
    """
    {condition_evaluation_logic}

# Effect function: Fetch current state
def fetch_current_state(config: {DirectiveName}Config) -> Dict[str, any]:
    """
    Effect function: Fetch current state of monitored entities.

    Args:
        config: Immutable configuration

    Returns:
        Current state dictionary
    """
    try:
        {state_fetching_code}
        return state

    except Exception as e:
        logging.error(f"Failed to fetch state: {e}")
        return {}

# Pure function: Build action payload
def build_{action_name}_payload(config: {DirectiveName}Config,
                                current_state: Dict[str, any]) -> Dict[str, any]:
    """
    Pure function: Build action payload based on current state.

    Args:
        config: Immutable configuration
        current_state: Current state

    Returns:
        Action payload
    """
    return {
        {payload_fields}
    }

# Effect function: Execute action
def execute_{action_name}(config: {DirectiveName}Config,
                          payload: Dict[str, any]) -> Optional[str]:
    """
    Effect function: Execute action when condition is met.

    Args:
        config: Immutable configuration
        payload: Action payload

    Returns:
        Result status or error message
    """
    try:
        {action_execution_code}

        logging.info(f"{directive_name}: Action executed successfully")
        return "success"

    except Exception as e:
        logging.error(f"{directive_name}: Action failed: {e}")
        return f"error: {str(e)}"

# Main monitoring loop
def monitor_{directive_name}(config: {DirectiveName}Config,
                            stop_event: threading.Event) -> None:
    """
    Main monitoring loop for {directive_name}.

    Args:
        config: Immutable configuration
        stop_event: Event to signal shutdown
    """
    logging.info(f"{directive_name} monitoring started")

    while not stop_event.is_set():
        try:
            # Effect: fetch current state
            current_state = fetch_current_state(config)

            # Pure: evaluate condition
            condition_met = evaluate_{condition_name}(current_state, config)

            if condition_met:
                logging.info(f"{directive_name}: Condition met, executing action")

                # Pure: build payload
                payload = build_{action_name}_payload(config, current_state)

                # Effect: execute action
                result = execute_{action_name}(config, payload)

                # Effect: log execution
                log_execution("{directive_name}", result)
            else:
                logging.debug(f"{directive_name}: Condition not met")

            # Wait before next check
            stop_event.wait(config.check_interval)

        except Exception as e:
            logging.error(f"{directive_name}: Monitor error: {e}")
            stop_event.wait(config.check_interval)

    logging.info(f"{directive_name} monitoring stopped")

# Service entry point
def start_service() -> threading.Thread:
    """
    Start {directive_name} monitoring service as background thread.

    Returns:
        Service thread
    """
    config = {DirectiveName}Config(
        check_interval={check_interval},
        condition_threshold={threshold},
        {config_initialization}
    )

    stop_event = threading.Event()

    service_thread = threading.Thread(
        target=monitor_{directive_name},
        args=(config, stop_event),
        name="{directive_name}_service",
        daemon=False
    )

    service_thread.start()

    return service_thread, stop_event

# Main execution
if __name__ == "__main__":
    setup_logging()

    service_thread, stop_event = start_service()

    logging.info("{directive_name} service started")

    try:
        service_thread.join()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Shutdown signal received")
        stop_event.set()
        service_thread.join(timeout=10)
        logging.info("{directive_name} service stopped")
```

---

### Template 3: Event Handler

**Use Case**: React to events (webhooks, MQTT messages, file changes)

**Generated Code Structure**:
```python
# .aifp/user-directives/generated/handlers/<directive_name>_handler.py

from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging

# Configuration (immutable)
@dataclass(frozen=True)
class {DirectiveName}Config:
    event_source: str                    # e.g., 'webhook', 'mqtt'
    event_name: str                      # Event identifier
    {event_specific_config}

# Pure function: Validate event
def validate_{event_name}(event_data: Dict[str, any],
                          config: {DirectiveName}Config) -> bool:
    """
    Pure function: Validate incoming event matches expected format.

    Args:
        event_data: Event data from source
        config: Immutable configuration

    Returns:
        True if event is valid, False otherwise
    """
    {validation_logic}

# Pure function: Extract action parameters from event
def extract_{action_name}_params(event_data: Dict[str, any],
                                config: {DirectiveName}Config) -> Dict[str, any]:
    """
    Pure function: Extract action parameters from event data.

    Args:
        event_data: Event data
        config: Immutable configuration

    Returns:
        Action parameters dictionary
    """
    return {
        {parameter_extraction_logic}
    }

# Effect function: Execute action
def execute_{action_name}(config: {DirectiveName}Config,
                          params: Dict[str, any]) -> Optional[str]:
    """
    Effect function: Execute action in response to event.

    Args:
        config: Immutable configuration
        params: Action parameters

    Returns:
        Result status or error message
    """
    try:
        {action_execution_code}

        logging.info(f"{directive_name}: Action executed successfully")
        return "success"

    except Exception as e:
        logging.error(f"{directive_name}: Action failed: {e}")
        return f"error: {str(e)}"

# Main event handler
def handle_{directive_name}(event_data: Dict[str, any]) -> Optional[str]:
    """
    Main event handler for {directive_name}.

    Args:
        event_data: Event data from source

    Returns:
        Result status or error message
    """
    config = {DirectiveName}Config(
        event_source="{event_source}",
        event_name="{event_name}",
        {config_initialization}
    )

    # Pure: validate event
    if not validate_{event_name}(event_data, config):
        logging.warning(f"{directive_name}: Invalid event data")
        return "invalid_event"

    # Pure: extract parameters
    params = extract_{action_name}_params(event_data, config)

    # Effect: execute action
    result = execute_{action_name}(config, params)

    # Effect: log execution
    log_execution("{directive_name}", result, event_data)

    return result

# Event listener setup
def setup_event_listener() -> Any:
    """
    Set up event listener for {directive_name}.

    Returns:
        Event listener instance
    """
    {event_listener_setup_code}
```

---

## Code Generation Process

### Step 1: Analyze Directive

```python
def analyze_directive(directive: Directive) -> ImplementationType:
    """
    Analyze directive and determine implementation type.

    Returns:
        ImplementationType enum value
    """
    trigger_type = directive.trigger.get('type')
    action_type = directive.action.get('type')

    # Time-based triggers → Scheduler
    if trigger_type == 'time':
        return ImplementationType.SCHEDULER

    # Condition-based triggers → Monitoring Service
    elif trigger_type == 'condition':
        return ImplementationType.SERVICE

    # Event-based triggers → Event Handler
    elif trigger_type == 'event':
        return ImplementationType.HANDLER

    # Manual triggers → Simple Function
    elif trigger_type == 'manual':
        return ImplementationType.FUNCTION

    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")
```

---

### Step 2: Load Template

```python
def load_template(implementation_type: ImplementationType) -> str:
    """
    Load code generation template for implementation type.

    Returns:
        Template string with placeholders
    """
    templates = {
        ImplementationType.SCHEDULER: "templates/scheduler_template.py",
        ImplementationType.SERVICE: "templates/service_template.py",
        ImplementationType.HANDLER: "templates/handler_template.py",
        ImplementationType.FUNCTION: "templates/function_template.py"
    }

    template_path = templates[implementation_type]

    with open(template_path, 'r') as f:
        return f.read()
```

---

### Step 3: Generate Code

```python
def generate_code(directive: Directive, template: str) -> str:
    """
    Generate implementation code from directive and template.

    Args:
        directive: Validated directive
        template: Code template with placeholders

    Returns:
        Generated Python code
    """
    # Extract configuration
    trigger = directive.trigger
    action = directive.action

    # Build replacement map
    replacements = {
        '{directive_name}': directive.name,
        '{DirectiveName}': to_pascal_case(directive.name),
        '{description}': directive.description,
        '{trigger_time}': trigger.get('time', ''),
        '{timezone}': trigger.get('timezone', 'UTC'),
        '{check_interval}': trigger.get('check_interval', 60),
        '{condition_expression}': trigger.get('condition', ''),
        '{action_type}': action.get('type', ''),
        '{action_name}': generate_action_name(action),
        # ... more replacements
    }

    # Generate action-specific code
    action_code = generate_action_code(action)
    replacements['{action_execution_code}'] = action_code

    # Generate condition evaluation logic
    if trigger.get('type') == 'condition':
        condition_code = generate_condition_code(trigger.get('condition'))
        replacements['{condition_evaluation_logic}'] = condition_code

    # Apply replacements
    generated_code = template

    for placeholder, value in replacements.items():
        generated_code = generated_code.replace(placeholder, str(value))

    return generated_code
```

---

### Step 4: Apply FP Directives

```python
def apply_fp_directives(code: str) -> str:
    """
    Apply FP directives to ensure generated code is FP-compliant.

    Checks:
    - Pure functions have no side effects
    - Configuration is immutable (frozen dataclasses)
    - Side effects isolated in effect functions
    - All functions have type hints

    Args:
        code: Generated code

    Returns:
        FP-compliant code (may be modified)
    """
    # Parse code into AST
    tree = ast.parse(code)

    # Apply fp_purity directive
    # Ensure logic functions have no side effects
    verify_purity(tree)

    # Apply fp_immutability directive
    # Ensure configuration uses frozen dataclasses
    verify_immutability(tree)

    # Apply fp_side_effect_detection directive
    # Ensure side effects are isolated
    verify_side_effect_isolation(tree)

    # Apply fp_type_hints directive
    # Ensure all functions have type hints
    verify_type_hints(tree)

    return ast.unparse(tree)
```

---

### Step 5: Write and Register

```python
def write_implementation(directive: Directive, code: str,
                        implementation_type: ImplementationType) -> str:
    """
    Write generated code to file and register in database.

    Args:
        directive: Directive
        code: Generated code
        implementation_type: Type of implementation

    Returns:
        File path of generated code
    """
    # Determine file path
    subdirs = {
        ImplementationType.SCHEDULER: 'schedulers',
        ImplementationType.SERVICE: 'services',
        ImplementationType.HANDLER: 'handlers',
        ImplementationType.FUNCTION: 'utils'
    }

    subdir = subdirs[implementation_type]
    filename = f"{directive.name}_{implementation_type.value}.py"
    file_path = f".aifp/user-directives/generated/{subdir}/{filename}"

    # Write code to file
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(code)

    # Calculate checksum
    file_checksum = calculate_checksum(file_path)

    # Insert into directive_implementations
    conn = get_user_directives_db_connection()

    conn.execute("""
        INSERT INTO directive_implementations
        (directive_id, implementation_type, file_path, function_name, language,
         deployed, file_checksum)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        directive.id,
        implementation_type.value,
        file_path,
        f"handle_{directive.name}",
        'python',
        False,
        file_checksum
    ))

    conn.commit()
    conn.close()

    # Update user_directives status
    update_directive_status(directive.id, 'implemented')

    # Apply project_file_write directive
    # Updates project.db (files, functions tables)
    apply_project_file_write(file_path)

    return file_path
```

---

## Action Code Generation

### API Call Action

```python
def generate_api_call_code(action: Dict[str, any]) -> str:
    """
    Generate code for API call action.

    Returns:
        Python code string
    """
    api = action.get('api')
    endpoint = action.get('endpoint')
    method = action.get('method', 'POST')
    params = action.get('params', {})

    if api == 'homeassistant':
        return f"""
        # Home Assistant API call
        response = requests.{method.lower()}(
            f"{{config.api_url}}{endpoint}",
            json=payload,
            headers={{"Authorization": f"Bearer {{config.api_token}}"}}
        )

        if response.status_code == 200:
            return "success"
        else:
            return f"error: HTTP {{response.status_code}}"
        """

    elif api == 'aws':
        service = action.get('service', 'ec2')
        aws_method = action.get('aws_method', 'describe_instances')

        return f"""
        # AWS API call
        import boto3

        client = boto3.client('{service}', region_name=config.aws_region)
        response = client.{aws_method}(**payload)

        return "success"
        """

    else:
        # Generic API call
        return f"""
        # Generic API call
        response = requests.{method.lower()}(
            f"{{config.api_url}}{endpoint}",
            json=payload
        )

        if response.ok:
            return "success"
        else:
            return f"error: HTTP {{response.status_code}}"
        """
```

### Script Execution Action

```python
def generate_script_execution_code(action: Dict[str, any]) -> str:
    """
    Generate code for script execution action.

    Returns:
        Python code string
    """
    script = action.get('script')
    working_dir = action.get('working_dir', '.')
    env = action.get('env', {})

    return f"""
    # Script execution
    import subprocess

    env = os.environ.copy()
    env.update({env})

    result = subprocess.run(
        ['{script}'],
        cwd='{working_dir}',
        env=env,
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return "success"
    else:
        return f"error: {{result.stderr}}"
    """
```

---

## Utility Functions

### Logging Setup

```python
def generate_logging_setup() -> str:
    """
    Generate logging setup code.

    Returns:
        Python code for logging configuration
    """
    return """
def setup_logging():
    \"\"\"Configure logging for user directive execution.\"\"\"
    import logging
    import logging.handlers

    # Execution log
    execution_handler = logging.handlers.RotatingFileHandler(
        '.aifp/logs/execution/current.log',
        maxBytes=100*1024*1024,  # 100MB
        backupCount=30
    )
    execution_handler.setLevel(logging.INFO)

    # Error log
    error_handler = logging.handlers.RotatingFileHandler(
        '.aifp/logs/errors/current_errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=90
    )
    error_handler.setLevel(logging.ERROR)

    # JSON formatter
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"message": "%(message)s"}'
    )

    execution_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(execution_handler)
    logger.addHandler(error_handler)

def log_execution(directive_name: str, result: str, metadata: Dict = None):
    \"\"\"Log directive execution to file and database.\"\"\"
    # Log to file
    logging.info(
        f'{{"directive": "{directive_name}", "result": "{result}", '
        f'"metadata": {json.dumps(metadata or {})}}}'
    )

    # Update database statistics
    update_execution_stats(directive_name, result)
"""
```

---

## Summary

The Code Generation system:
- Converts validated directives into FP-compliant Python code
- Uses templates for different implementation types (scheduler, service, handler)
- Applies FP directives for purity, immutability, and side effect isolation
- Generates immutable configuration using frozen dataclasses
- Isolates side effects in effect functions
- Writes generated code to .aifp/user-directives/generated/
- Registers implementations in user_directives.db and project.db

This enables real-time execution of user directives while maintaining functional programming principles.

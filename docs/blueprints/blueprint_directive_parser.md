# Directive Parser Blueprint

## Overview

This blueprint defines the parsing system for user-defined directives. The parser converts YAML/JSON/TXT files into structured directive objects, identifies ambiguities, and prepares directives for validation and implementation.

---

## Parser Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  User Directive File                     │
│  (.aifp/user-directives/source/*.{yaml,json,txt})       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│               Format Detector                            │
│  - Check file extension                                  │
│  - Validate format-specific syntax                       │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌─────────────┐ ┌────────────┐ ┌────────────┐
│YAML Parser  │ │JSON Parser │ │TXT Parser  │
└─────────────┘ └────────────┘ └────────────┘
        │            │            │
        └────────────┼────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│              Directive Extractor                         │
│  - Extract trigger information                           │
│  - Extract action information                            │
│  - Extract metadata                                      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│            Ambiguity Detector                            │
│  - Analyze triggers for ambiguous specifications         │
│  - Analyze actions for missing parameters                │
│  - Identify required dependencies                        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│           Database Storage (user_directives.db)          │
│  - user_directives table (status=pending_validation)     │
│  - source_files table (with checksum)                    │
└─────────────────────────────────────────────────────────┘
```

---

## Supported Formats

### 1. YAML Format (Recommended)

**Structure**:
```yaml
directives:
  - name: <unique_directive_name>
    description: <human_readable_description>
    domain: <optional_domain> # e.g., home_automation, aws, custom
    priority: <optional_priority> # integer, default 0
    trigger:
      type: <time|event|condition|manual>
      <trigger_specific_fields>
    action:
      type: <api_call|script_execution|function_call>
      <action_specific_fields>
```

**Trigger Types**:

**Time-based**:
```yaml
trigger:
  type: time
  time: "17:00"                     # 24-hour format
  timezone: America/New_York        # IANA timezone
  daylight_savings: true            # Account for DST (optional, default true)
  days: [monday, tuesday, friday]   # Optional: specific days
```

**Event-based**:
```yaml
trigger:
  type: event
  source: <event_source>            # e.g., webhook, mqtt, file_watch
  event_name: <event_identifier>
  filter: <optional_filter_expression>
```

**Condition-based**:
```yaml
trigger:
  type: condition
  check_interval: 60                # Check every N seconds
  condition: |
    stove.state == 'on' AND stove.duration > 1200
```

**Manual**:
```yaml
trigger:
  type: manual                      # User executes manually via command
```

**Action Types**:

**API Call**:
```yaml
action:
  type: api_call
  api: <api_name>                   # e.g., homeassistant, aws, custom
  endpoint: <api_endpoint>
  method: <GET|POST|PUT|DELETE>     # Optional, default POST
  params:
    <key>: <value>
  headers:                          # Optional
    <key>: <value>
```

**Script Execution**:
```yaml
action:
  type: script_execution
  script: <path_to_script>
  working_dir: <optional_working_directory>
  env:                              # Optional environment variables
    <key>: <value>
```

**Function Call**:
```yaml
action:
  type: function_call
  module: <python_module>
  function: <function_name>
  args:                             # Positional arguments
    - <arg1>
    - <arg2>
  kwargs:                           # Keyword arguments
    <key>: <value>
```

---

### 2. JSON Format

**Structure**:
```json
{
  "directives": [
    {
      "name": "unique_directive_name",
      "description": "human readable description",
      "domain": "optional_domain",
      "priority": 0,
      "trigger": {
        "type": "time|event|condition|manual",
        "...": "trigger_specific_fields"
      },
      "action": {
        "type": "api_call|script_execution|function_call",
        "...": "action_specific_fields"
      }
    }
  ]
}
```

**Example**:
```json
{
  "directives": [
    {
      "name": "scale_ec2_instances",
      "description": "Scale EC2 instances when CPU > 80%",
      "domain": "aws_infrastructure",
      "trigger": {
        "type": "condition",
        "check_interval": 300,
        "condition": "avg_cpu_usage > 80"
      },
      "action": {
        "type": "api_call",
        "api": "aws",
        "service": "ec2",
        "method": "run_instances",
        "params": {
          "ImageId": "ami-12345678",
          "InstanceType": "t2.micro"
        }
      }
    }
  ]
}
```

---

### 3. TXT Format (Simple Line-by-Line)

**Structure**:
```
<trigger_phrase> <action_phrase>
```

**Natural Language Patterns**:
- Time-based: `At <time> <action>` or `Every <interval> <action>`
- Condition-based: `If <condition> then <action>` or `When <condition> <action>`
- Manual: `<action_description>`

**Examples**:
```
At 5pm turn off living room lights
If stove is on for more than 20 minutes, turn off stove
Every night at 2am backup database
When CPU usage exceeds 80%, scale EC2 instances
```

**Parsing Strategy**:
1. Extract time patterns (`At 5pm`, `Every night at 2am`)
2. Extract condition patterns (`If ... then`, `When ...`)
3. Extract action patterns (remaining text)
4. Flag ambiguities for validation

---

## Parser Implementation

### Main Parser Function

```python
def parse_directive_file(file_path: str) -> ParseResult:
    """
    Parse user directive file and extract directives.

    Args:
        file_path: Path to directive file

    Returns:
        ParseResult containing directives and ambiguities
    """
    # Detect format
    file_format = detect_format(file_path)

    # Load appropriate parser
    if file_format == 'yaml':
        raw_directives = parse_yaml(file_path)
    elif file_format == 'json':
        raw_directives = parse_json(file_path)
    elif file_format == 'txt':
        raw_directives = parse_txt(file_path)
    else:
        raise UnsupportedFormatError(f"Format {file_format} not supported")

    # Extract and validate structure
    directives = []
    ambiguities = []

    for raw in raw_directives:
        directive, directive_ambiguities = extract_directive(raw, file_format)
        directives.append(directive)
        ambiguities.extend(directive_ambiguities)

    return ParseResult(
        directives=directives,
        ambiguities=ambiguities,
        source_file=file_path,
        file_format=file_format
    )
```

---

### Format Detection

```python
def detect_format(file_path: str) -> str:
    """
    Detect directive file format.

    Returns:
        'yaml', 'json', or 'txt'
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension in ['.yaml', '.yml']:
        return 'yaml'
    elif extension == '.json':
        return 'json'
    elif extension in ['.txt', '.text']:
        return 'txt'
    else:
        # Try to detect from content
        with open(file_path, 'r') as f:
            content = f.read().strip()

        if content.startswith('{'):
            return 'json'
        elif 'directives:' in content or content.startswith('- '):
            return 'yaml'
        else:
            return 'txt'
```

---

### YAML Parser

```python
import yaml

def parse_yaml(file_path: str) -> List[Dict]:
    """Parse YAML directive file."""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or 'directives' not in data:
        raise ParseError("YAML must contain 'directives' key")

    directives = data['directives']

    if not isinstance(directives, list):
        raise ParseError("'directives' must be a list")

    return directives
```

---

### JSON Parser

```python
import json

def parse_json(file_path: str) -> List[Dict]:
    """Parse JSON directive file."""
    with open(file_path, 'r') as f:
        data = json.load(f)

    if not isinstance(data, dict) or 'directives' not in data:
        raise ParseError("JSON must contain 'directives' key")

    directives = data['directives']

    if not isinstance(directives, list):
        raise ParseError("'directives' must be a list")

    return directives
```

---

### TXT Parser

```python
import re

def parse_txt(file_path: str) -> List[Dict]:
    """
    Parse line-by-line TXT directive file.

    Uses natural language patterns to extract directives.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()

    directives = []

    for line_num, line in enumerate(lines, 1):
        line = line.strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue

        # Parse line into directive structure
        directive = parse_txt_line(line, line_num)
        directives.append(directive)

    return directives

def parse_txt_line(line: str, line_num: int) -> Dict:
    """
    Parse a single TXT line into directive structure.

    Patterns:
    - At <time> <action>
    - Every <interval> <action>
    - If <condition> then <action>
    - When <condition> <action>
    """
    # Time-based patterns
    time_pattern = r'^(?:At|at)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(.+)$'
    interval_pattern = r'^(?:Every|every)\s+(.+?)\s+at\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)\s+(.+)$'

    # Condition-based patterns
    condition_if_pattern = r'^(?:If|if)\s+(.+?)\s+(?:then|,)\s+(.+)$'
    condition_when_pattern = r'^(?:When|when)\s+(.+?)\s+,?\s*(.+)$'

    # Try time-based patterns
    match = re.match(time_pattern, line)
    if match:
        time_str, action = match.groups()
        return {
            'name': f'directive_line_{line_num}',
            'description': line,
            'raw_line': line,
            'trigger': {
                'type': 'time',
                'time': time_str,
                'ambiguous': True  # Needs validation
            },
            'action': {
                'type': 'unknown',
                'description': action,
                'ambiguous': True
            }
        }

    # Try interval patterns
    match = re.match(interval_pattern, line)
    if match:
        interval, time_str, action = match.groups()
        return {
            'name': f'directive_line_{line_num}',
            'description': line,
            'raw_line': line,
            'trigger': {
                'type': 'time',
                'interval': interval,
                'time': time_str,
                'ambiguous': True
            },
            'action': {
                'type': 'unknown',
                'description': action,
                'ambiguous': True
            }
        }

    # Try condition patterns
    match = re.match(condition_if_pattern, line) or re.match(condition_when_pattern, line)
    if match:
        condition, action = match.groups()
        return {
            'name': f'directive_line_{line_num}',
            'description': line,
            'raw_line': line,
            'trigger': {
                'type': 'condition',
                'condition': condition,
                'ambiguous': True
            },
            'action': {
                'type': 'unknown',
                'description': action,
                'ambiguous': True
            }
        }

    # Default: treat as manual trigger
    return {
        'name': f'directive_line_{line_num}',
        'description': line,
        'raw_line': line,
        'trigger': {
            'type': 'manual',
            'ambiguous': True
        },
        'action': {
            'type': 'unknown',
            'description': line,
            'ambiguous': True
        }
    }
```

---

## Directive Extraction

### Extract Directive

```python
@dataclass
class Directive:
    name: str
    description: str
    domain: Optional[str]
    priority: int
    trigger: Dict
    action: Dict
    raw_content: str
    source_file: str
    source_format: str

def extract_directive(raw: Dict, file_format: str) -> Tuple[Directive, List[Ambiguity]]:
    """
    Extract structured directive from raw parsed data.

    Returns:
        (Directive, List of ambiguities)
    """
    ambiguities = []

    # Extract name (required)
    name = raw.get('name')
    if not name:
        ambiguities.append(Ambiguity(
            field='name',
            message='Directive name is required',
            severity='error'
        ))
        name = f'unnamed_directive_{uuid.uuid4().hex[:8]}'

    # Extract description
    description = raw.get('description', raw.get('raw_line', ''))

    # Extract domain
    domain = raw.get('domain')

    # Extract priority
    priority = raw.get('priority', 0)

    # Extract trigger
    trigger = raw.get('trigger', {})
    trigger_ambiguities = validate_trigger(trigger)
    ambiguities.extend(trigger_ambiguities)

    # Extract action
    action = raw.get('action', {})
    action_ambiguities = validate_action(action)
    ambiguities.extend(action_ambiguities)

    directive = Directive(
        name=name,
        description=description,
        domain=domain,
        priority=priority,
        trigger=trigger,
        action=action,
        raw_content=json.dumps(raw),
        source_file='',  # Set by caller
        source_format=file_format
    )

    return directive, ambiguities
```

---

## Ambiguity Detection

### Validate Trigger

```python
@dataclass
class Ambiguity:
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'
    question: Optional[str] = None
    options: Optional[List[str]] = None

def validate_trigger(trigger: Dict) -> List[Ambiguity]:
    """Validate trigger and detect ambiguities."""
    ambiguities = []

    trigger_type = trigger.get('type')

    if not trigger_type:
        ambiguities.append(Ambiguity(
            field='trigger.type',
            message='Trigger type is required',
            severity='error',
            question='What should trigger this directive?',
            options=['time', 'event', 'condition', 'manual']
        ))
        return ambiguities

    # Validate time-based triggers
    if trigger_type == 'time':
        if 'time' not in trigger:
            ambiguities.append(Ambiguity(
                field='trigger.time',
                message='Time specification is required',
                severity='error',
                question='At what time should this execute?'
            ))

        if 'timezone' not in trigger:
            ambiguities.append(Ambiguity(
                field='trigger.timezone',
                message='Timezone not specified',
                severity='warning',
                question='What timezone? (default: system timezone)'
            ))

    # Validate condition-based triggers
    elif trigger_type == 'condition':
        if 'condition' not in trigger:
            ambiguities.append(Ambiguity(
                field='trigger.condition',
                message='Condition expression is required',
                severity='error',
                question='What condition should be checked?'
            ))

        if 'check_interval' not in trigger:
            ambiguities.append(Ambiguity(
                field='trigger.check_interval',
                message='Check interval not specified',
                severity='warning',
                question='How often should the condition be checked? (seconds)'
            ))

    # Validate event-based triggers
    elif trigger_type == 'event':
        if 'source' not in trigger:
            ambiguities.append(Ambiguity(
                field='trigger.source',
                message='Event source is required',
                severity='error',
                question='What is the event source?',
                options=['webhook', 'mqtt', 'file_watch', 'custom']
            ))

        if 'event_name' not in trigger:
            ambiguities.append(Ambiguity(
                field='trigger.event_name',
                message='Event name is required',
                severity='error',
                question='What event should trigger this?'
            ))

    return ambiguities
```

### Validate Action

```python
def validate_action(action: Dict) -> List[Ambiguity]:
    """Validate action and detect ambiguities."""
    ambiguities = []

    action_type = action.get('type')

    if not action_type:
        ambiguities.append(Ambiguity(
            field='action.type',
            message='Action type is required',
            severity='error',
            question='What type of action should be performed?',
            options=['api_call', 'script_execution', 'function_call']
        ))
        return ambiguities

    # Validate API call actions
    if action_type == 'api_call':
        if 'api' not in action:
            ambiguities.append(Ambiguity(
                field='action.api',
                message='API name is required',
                severity='error',
                question='Which API should be called?'
            ))

        if 'endpoint' not in action:
            ambiguities.append(Ambiguity(
                field='action.endpoint',
                message='API endpoint is required',
                severity='error',
                question='What API endpoint should be called?'
            ))

    # Validate script execution actions
    elif action_type == 'script_execution':
        if 'script' not in action:
            ambiguities.append(Ambiguity(
                field='action.script',
                message='Script path is required',
                severity='error',
                question='What script should be executed?'
            ))

    # Validate function call actions
    elif action_type == 'function_call':
        if 'module' not in action or 'function' not in action:
            ambiguities.append(Ambiguity(
                field='action.function',
                message='Function module and name are required',
                severity='error',
                question='Which function should be called?'
            ))

    return ambiguities
```

---

## Dependency Detection

```python
def detect_dependencies(directive: Directive) -> List[Dependency]:
    """
    Detect required dependencies from directive specification.

    Returns:
        List of detected dependencies
    """
    dependencies = []

    action = directive.action
    action_type = action.get('type')

    # API call dependencies
    if action_type == 'api_call':
        api_name = action.get('api')

        if api_name == 'homeassistant':
            dependencies.append(Dependency(
                type='python_package',
                name='homeassistant-api',
                version='>=2.0.0',
                required=True,
                description='Home Assistant API client'
            ))

        elif api_name == 'aws':
            dependencies.append(Dependency(
                type='python_package',
                name='boto3',
                version='>=1.20.0',
                required=True,
                description='AWS SDK for Python'
            ))

        # Add generic requests library
        dependencies.append(Dependency(
            type='python_package',
            name='requests',
            version='>=2.25.0',
            required=True,
            description='HTTP library for API calls'
        ))

    # Scheduler dependencies
    trigger = directive.trigger
    trigger_type = trigger.get('type')

    if trigger_type == 'time':
        dependencies.append(Dependency(
            type='python_package',
            name='apscheduler',
            version='>=3.7.0',
            required=True,
            description='Advanced Python Scheduler for time-based triggers'
        ))

    # Environment variables
    if action_type == 'api_call' and action.get('api') == 'aws':
        dependencies.append(Dependency(
            type='environment_variable',
            name='AWS_ACCESS_KEY_ID',
            required=True,
            description='AWS access key for authentication'
        ))
        dependencies.append(Dependency(
            type='environment_variable',
            name='AWS_SECRET_ACCESS_KEY',
            required=True,
            description='AWS secret key for authentication'
        ))

    return dependencies

@dataclass
class Dependency:
    type: str
    name: str
    version: Optional[str] = None
    required: bool = True
    description: Optional[str] = None
```

---

## Database Storage

```python
def store_parsed_directives(directives: List[Directive], ambiguities: List[Ambiguity],
                            source_file: str, file_format: str) -> None:
    """
    Store parsed directives in user_directives.db.
    """
    conn = get_user_directives_db_connection()

    # Calculate file checksum
    file_checksum = calculate_checksum(source_file)

    # Insert source file
    conn.execute("""
        INSERT OR REPLACE INTO source_files (file_path, file_format, file_checksum,
                                              last_parsed_at, parse_status, directive_count)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_file, file_format, file_checksum, datetime.now(),
          'parsed_successfully', len(directives)))

    # Insert directives
    for directive in directives:
        # Detect dependencies
        dependencies = detect_dependencies(directive)

        # Get trigger and action types
        trigger_type = directive.trigger.get('type', 'manual')
        action_type = directive.action.get('type', 'unknown')

        # Insert directive
        conn.execute("""
            INSERT INTO user_directives
            (name, source_file, source_format, domain, description, raw_content,
             validated_content, trigger_type, trigger_config, action_type, action_config,
             status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            directive.name,
            source_file,
            file_format,
            directive.domain,
            directive.description,
            directive.raw_content,
            json.dumps(directive.__dict__),  # Initial validated_content (will be updated)
            trigger_type,
            json.dumps(directive.trigger),
            action_type,
            json.dumps(directive.action),
            'pending_validation',
            directive.priority
        ))

        directive_id = conn.lastrowid

        # Insert dependencies
        for dep in dependencies:
            conn.execute("""
                INSERT INTO directive_dependencies
                (directive_id, dependency_type, dependency_name, dependency_version,
                 required, description)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                directive_id,
                dep.type,
                dep.name,
                dep.version,
                dep.required,
                dep.description
            ))

    conn.commit()
    conn.close()
```

---

## Example Parse Output

### Input (YAML):
```yaml
directives:
  - name: turn_off_lights_5pm
    trigger:
      type: time
      time: "17:00"
    action:
      type: api_call
      api: homeassistant
      endpoint: /services/light/turn_off
```

### Output:
```python
ParseResult(
    directives=[
        Directive(
            name='turn_off_lights_5pm',
            description='',
            domain=None,
            priority=0,
            trigger={'type': 'time', 'time': '17:00'},
            action={'type': 'api_call', 'api': 'homeassistant',
                   'endpoint': '/services/light/turn_off'},
            raw_content='...',
            source_file='.aifp/user-directives/source/home_automation.yaml',
            source_format='yaml'
        )
    ],
    ambiguities=[
        Ambiguity(
            field='trigger.timezone',
            message='Timezone not specified',
            severity='warning',
            question='What timezone? (default: system timezone)',
            options=None
        ),
        Ambiguity(
            field='action.params',
            message='Entity ID not specified',
            severity='error',
            question='Which lights should be turned off?',
            options=None
        )
    ]
)
```

---

## Summary

The Directive Parser:
- Supports YAML, JSON, and TXT formats
- Extracts structured directive information
- Detects ambiguities and missing information
- Identifies required dependencies
- Stores parsed data in user_directives.db
- Prepares directives for validation phase

This enables the AI to convert user-written directive files into actionable, validated automation rules.

# User-Defined Directives Blueprint

## Overview

This blueprint defines the **User-Defined Directives System** for **Use Case 2: Custom Directive Automation** projects. When user directives are enabled, **the AIFP project IS dedicated to building and managing the automation codebase generated from those directives.**

Users write directive definitions (YAML/JSON/TXT), AI generates FP-compliant implementation code in `src/`, and executes it in real-time. The project management system tracks this generated code like any AIFP project (files, functions, tasks, completion path).

---

## Design Philosophy

### Core Principles

1. **Directives are specifications, generated code is the project**
   - User writes directive definitions in YAML/JSON/TXT
   - AI generates FP-compliant implementation code in `src/`
   - **The generated code IS the project's codebase**
   - Project.db tracks generated files, functions, tasks like any AIFP project

2. **Single-purpose projects**
   - Automation projects are dedicated to directive implementation only
   - You would NOT mix a web app with home automation
   - Run separate AIFP instances for different purposes
   - Example: `~/automation/home/` for home automation, `~/projects/web-app/` for applications

3. **Real-time execution engine**
   - Generated code executes continuously via background services
   - Event-driven architecture for triggers and conditions
   - Schedulers for time-based automation (cron-like)

4. **Full FP compliance for generated code**
   - FP directives apply to ALL generated implementation code
   - Pure functions, immutability, explicit side effects
   - Project directives manage the generated codebase
   - Tests generated alongside implementation

5. **File-based logging for runtime execution**
   - Database stores state and statistics only
   - Detailed logs in rotating files (`.aifp-project/logs/`)
   - 30-day execution logs, 90-day error logs
   - Only for automation projects (Use Case 2)

6. **Dependency management with user confirmation**
   - AI detects required packages/services
   - Prompts user before installing
   - Tracks dependencies in database and `requirements.txt`

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              User Directive Files (User's Project)           │
│  directives/lights.yaml, automations.yaml, etc.             │
│  (User writes these wherever they want in their project)    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓ (User: "Parse directives/lights.yaml")
┌─────────────────────────────────────────────────────────────┐
│              User Directive Processing Flow                  │
│  1. Parse → 2. Validate → 3. Implement → 4. Activate        │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼─────────────┐
        ↓            ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│.aifp-project/│ │src/          │ │.aifp-project/│
│user_         │ │Generated     │ │logs/         │
│directives.db │ │Code          │ │(Files)       │
│              │ │              │ │              │
│• References  │ │• Controllers │ │• execution/  │
│  to user's   │ │• Schedulers  │ │• errors/     │
│  files       │ │• Services    │ │• lifecycle   │
│• Statistics  │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
        ↓
┌─────────────────────────────────────────────────────────────┐
│                  Real-Time Execution Engine                  │
│  - Event monitors (API webhooks, file watchers, etc.)       │
│  - Time-based schedulers (cron jobs, intervals)             │
│  - Condition evaluators (check states, thresholds)          │
└─────────────────────────────────────────────────────────────┘
```

**User Experience**:
1. User creates directive files in their project (e.g., `directives/lights.yaml`)
2. User tells AI: "Parse my directive file at directives/lights.yaml"
3. AI handles everything in `.aifp-project/` - user never touches it
4. AI generates code in `src/` - the actual project codebase

---

## Directory Structure

**Automation Project** (Use Case 2):

```
home-automation/                          # User's automation project
├── directives/                           # ← USER WRITES directive files here
│   ├── lights.yaml                       # User-created directive definition
│   └── security.yaml                     # User-created directive definition
├── src/                                  # ← AI GENERATES THIS CODE
│   ├── lights_controller.py             # Generated from lights.yaml
│   ├── security_monitor.py              # Generated from security.yaml
│   ├── scheduler.py                     # Generated orchestrator
│   └── helpers/                         # Generated utility functions
│       ├── homeassistant_client.py
│       └── notification_sender.py
├── tests/                                # ← AI GENERATES TESTS
│   ├── test_lights_controller.py
│   └── test_security_monitor.py
├── requirements.txt                      # Auto-detected dependencies
├── README.md                             # Generated project documentation
└── .aifp-project/                        # ← AI-MANAGED ONLY - user never touches
    ├── project.db                        # Tracks generated src/ code
    ├── user_preferences.db               # AI behavior preferences
    ├── user_directives.db                # References ../directives/ files
    ├── aifp_core.db                      # AIFP directive definitions
    ├── ProjectBlueprint.md               # Automation architecture
    ├── logs/                             # Execution logs (files, not DB)
    │   ├── executions/                   # 30-day retention
    │   │   └── 2025-10-26.log
    │   └── errors/                       # 90-day retention
    │       └── 2025-10-26_errors.log
    └── backups/                          # Blueprint backups
```

**Key Points**:
- User writes directive files wherever they want (e.g., `directives/`, `automations/`, root, etc.)
- `.aifp-project/` is AI-managed metadata only - user NEVER edits it
- `src/` contains the actual project code (generated by AI)
- `project.db` tracks the generated `src/` code like any AIFP project
- `user_directives.db` references user's directive files (e.g., `../directives/lights.yaml`)
- Generated code follows all FP directives (purity, immutability, etc.)

---

## User Directive File Formats

### YAML Format (Recommended)

```yaml
# home_automation.yaml
directives:
  - name: turn_off_lights_5pm
    description: Turn off all living room lights at 5pm
    trigger:
      type: time
      time: "17:00"
      timezone: America/New_York
      daylight_savings: true
    action:
      type: api_call
      api: homeassistant
      endpoint: /services/light/turn_off
      params:
        entity_id: group.living_room_lights

  - name: monitor_stove
    description: Turn off stove if on for more than 20 minutes
    trigger:
      type: condition
      check_interval: 60  # seconds
      condition: |
        stove.state == 'on' AND stove.duration > 1200
    action:
      type: api_call
      api: homeassistant
      endpoint: /services/switch/turn_off
      params:
        entity_id: switch.stove

  - name: backup_database_nightly
    description: Backup project database every night at 2am
    trigger:
      type: time
      time: "02:00"
      timezone: America/New_York
    action:
      type: script_execution
      script: scripts/backup_db.sh
      working_dir: /home/user/project
```

### JSON Format

```json
{
  "directives": [
    {
      "name": "scale_ec2_instances",
      "description": "Scale EC2 instances based on CPU usage",
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
          "InstanceType": "t2.micro",
          "MinCount": 1,
          "MaxCount": 3
        }
      }
    }
  ]
}
```

### TXT Format (Simple Line-by-Line)

```
# Simple text format for basic directives
At 5pm turn off living room lights
If stove is on for more than 20 minutes, turn off stove
Every night at 2am backup database
When CPU usage exceeds 80%, scale EC2 instances
```

---

## Directive Lifecycle

### 1. Parse Phase

**Directive**: `user_directive_parse`

**Workflow**:
```json
{
  "trunk": "parse_directive_file",
  "branches": [
    {
      "step": "detect_format",
      "actions": [
        {"check": "file extension", "determine": "format (yaml/json/txt)"},
        {"load": "appropriate parser"}
      ]
    },
    {
      "step": "parse_content",
      "actions": [
        {"parse": "directive file"},
        {"extract": "directives list"},
        {"validate": "basic structure"}
      ]
    },
    {
      "step": "identify_ambiguities",
      "actions": [
        {"analyze": "trigger specifications", "flag": "ambiguous time/conditions"},
        {"analyze": "action specifications", "flag": "missing parameters"},
        {"analyze": "dependencies", "flag": "required APIs/packages"}
      ]
    },
    {
      "step": "store_raw_directives",
      "actions": [
        {"insert": "user_directives table (status=pending_validation)"},
        {"insert": "source_files table"},
        {"calculate": "file_checksum for change detection"}
      ]
    }
  ],
  "error_handling": {
    "on_failure": "log_parse_error_and_prompt_user",
    "retry": "max 2 attempts"
  }
}
```

**Output**:
```
📄 Parsed: home_automation.yaml
✅ Found 3 directives
⚠️  Ambiguities detected:
   - "which lights at 5pm?" (turn_off_lights_5pm)
   - "stove entity ID?" (monitor_stove)

Next: Run validation to resolve ambiguities
```

---

### 2. Validate Phase

**Directive**: `user_directive_validate`

**Workflow**:
```json
{
  "trunk": "validate_directives",
  "branches": [
    {
      "step": "interactive_clarification",
      "actions": [
        {"for_each": "ambiguity", "prompt_user": "clarifying question"},
        {"store": "validation_questions and validation_answers"}
      ]
    },
    {
      "step": "resolve_ambiguities",
      "actions": [
        {"apply": "user answers to directive config"},
        {"generate": "validated_content JSON"}
      ]
    },
    {
      "step": "confirm_understanding",
      "actions": [
        {"present": "validated directive interpretation"},
        {"prompt": "Is this correct? (yes/no/modify)"},
        {"if_no": "re-prompt for clarification"}
      ]
    },
    {
      "step": "store_validated_directives",
      "actions": [
        {"update": "user_directives table (status=validated, validated_content)"},
        {"write": "validated directive file to validated/ folder"},
        {"mark": "validated_at timestamp"}
      ]
    }
  ],
  "error_handling": {
    "on_failure": "log_validation_error_and_retry",
    "retry": "max 3 attempts"
  }
}
```

**Interactive Example**:
```
🔍 Validating: turn_off_lights_5pm

❓ Question 1: Which lights should be turned off at 5pm?
   Options:
   a) All lights in the house
   b) Living room lights only
   c) Specific lights (specify entity IDs)

User: b

❓ Question 2: Should this account for daylight savings time?
User: yes

❓ Question 3: What timezone?
User: America/New_York

✅ Understood:
   - Turn off all living room lights
   - At 5:00 PM Eastern Time (America/New_York)
   - Account for daylight savings

Is this correct? (yes/no)
User: yes

✅ Directive validated and saved
```

---

### 3. Implement Phase

**Directive**: `user_directive_implement`

**Workflow**:
```json
{
  "trunk": "generate_implementation_code",
  "branches": [
    {
      "step": "analyze_requirements",
      "actions": [
        {"determine": "implementation_type (handler/scheduler/service)"},
        {"identify": "required dependencies"},
        {"check": "dependency availability in directive_dependencies table"}
      ]
    },
    {
      "step": "handle_dependencies",
      "actions": [
        {"for_each": "missing dependency", "prompt_user": "Install {package}? (y/n)"},
        {"if_yes": "install_dependency and mark confirmed"},
        {"update": "directive_dependencies table"}
      ]
    },
    {
      "step": "generate_code",
      "actions": [
        {"load": "code generation template for implementation_type"},
        {"apply": "validated_content to template"},
        {"generate": "FP-compliant Python code"},
        {"apply": "fp_purity, fp_immutability directives"}
      ]
    },
    {
      "step": "write_implementation_files",
      "actions": [
        {"write": "generated code to .aifp/user-directives/generated/"},
        {"insert": "directive_implementations table"},
        {"calculate": "file_checksum"},
        {"update": "user_directives (status=implemented)"}
      ]
    },
    {
      "parallel": [
        "update_project_db_files_table",
        "update_project_db_functions_table"
      ],
      "details": {
        "apply_project_file_write": true
      }
    }
  ],
  "error_handling": {
    "on_failure": "log_implementation_error_and_rollback",
    "retry": "max 2 attempts"
  }
}
```

**Dependency Confirmation Example**:
```
📦 Dependency Check for: turn_off_lights_5pm

Required:
  - homeassistant-api (Python package)
  - apscheduler (Python package for time-based scheduling)

⚠️  homeassistant-api is not installed

Install homeassistant-api? (y/n)
User: y

Installing homeassistant-api...
✅ homeassistant-api installed successfully

📝 Generated implementation:
   File: .aifp/user-directives/generated/schedulers/lights_5pm_handler.py
   Functions: schedule_lights_5pm(), turn_off_lights()
   FP Compliance: ✓ Pure functions, immutable config
```

---

### 4. Activate Phase

**Directive**: `user_directive_activate`

**Workflow**:
```json
{
  "trunk": "activate_directive",
  "branches": [
    {
      "step": "verify_implementation",
      "actions": [
        {"check": "implementation_file_path exists"},
        {"check": "all dependencies installed"},
        {"validate": "entry_point is executable"}
      ]
    },
    {
      "step": "deploy_implementation",
      "actions": [
        {"if": "implementation_type == scheduler", "then": "register_with_apscheduler"},
        {"if": "implementation_type == service", "then": "start_background_service"},
        {"if": "implementation_type == event_handler", "then": "register_event_listener"},
        {"store": "process_id if background service"}
      ]
    },
    {
      "step": "initialize_execution_tracking",
      "actions": [
        {"insert": "directive_executions table"},
        {"calculate": "next_scheduled_time for time-based triggers"},
        {"update": "user_directives (status=active, activated_at)"}
      ]
    },
    {
      "step": "initialize_logging",
      "actions": [
        {"setup": "execution log handler"},
        {"setup": "error log handler"},
        {"log": "Directive activated", "to": "user-directives.log"}
      ]
    }
  ],
  "error_handling": {
    "on_failure": "rollback_activation_and_log_error",
    "retry": "max 1 attempt"
  }
}
```

**Output**:
```
🚀 Activating: turn_off_lights_5pm

✅ Implementation verified
✅ Dependencies satisfied
✅ Scheduler registered (next run: 2025-10-22 17:00:00 EST)
✅ Execution tracking initialized
✅ Logging configured

🟢 Directive active and monitoring

Status:
  - Next execution: Today at 5:00 PM
  - Log file: .aifp/logs/execution/current.log
  - Error log: .aifp/logs/errors/current_errors.log
```

---

### 5. Monitor Phase

**Directive**: `user_directive_monitor`

**Workflow**:
```json
{
  "trunk": "monitor_directive_execution",
  "branches": [
    {
      "step": "track_executions",
      "actions": [
        {"on_execution": "log_to_execution_file"},
        {"update": "directive_executions (total_executions, last_execution_time)"},
        {"calculate": "avg_execution_time_ms"}
      ]
    },
    {
      "step": "handle_errors",
      "actions": [
        {"on_error": "log_to_error_file"},
        {"update": "directive_executions (error_count, last_error_time/type/message)"},
        {"if": "error_count > threshold", "then": "update_status_to_error"},
        {"notify": "user if critical error"}
      ]
    },
    {
      "step": "rotate_logs",
      "actions": [
        {"check": "log file size or date"},
        {"if": "rotation_trigger", "then": "rotate_and_archive"},
        {"if": "retention_exceeded", "then": "delete_old_archives"}
      ]
    }
  ],
  "error_handling": {
    "on_failure": "log_monitor_error_and_continue"
  }
}
```

**Execution Log Format** (JSON Lines):
```json
{"timestamp": "2025-10-22T17:00:00.123Z", "directive": "turn_off_lights_5pm", "status": "success", "duration_ms": 234, "result": "lights_off"}
{"timestamp": "2025-10-22T17:00:00.456Z", "directive": "monitor_stove", "status": "skipped", "reason": "stove_off"}
```

**Error Log Format** (JSON Lines):
```json
{"timestamp": "2025-10-22T17:00:00.789Z", "directive": "turn_off_lights_5pm", "error_type": "connection_error", "error_message": "Failed to connect to Home Assistant API", "stack_trace": "..."}
```

---

### 6. Update Phase

**Directive**: `user_directive_update`

**Workflow**:
```json
{
  "trunk": "detect_and_update_directive",
  "branches": [
    {
      "step": "detect_source_file_change",
      "actions": [
        {"watch": "source_files for checksum changes"},
        {"on_change": "trigger update workflow"}
      ]
    },
    {
      "step": "parse_updated_file",
      "actions": [
        {"parse": "updated directive file"},
        {"compare": "new content vs validated_content"},
        {"identify": "changed directives"}
      ]
    },
    {
      "step": "revalidate_changes",
      "actions": [
        {"for_each": "changed directive", "prompt": "Directive changed. Revalidate?"},
        {"run": "user_directive_validate for changed directives"}
      ]
    },
    {
      "step": "update_implementation",
      "actions": [
        {"if": "active", "then": "deactivate_directive"},
        {"regenerate": "implementation code"},
        {"if": "was_active", "then": "reactivate_directive"}
      ]
    }
  ],
  "error_handling": {
    "on_failure": "rollback_to_previous_version",
    "retry": "max 2 attempts"
  }
}
```

---

### 7. Deactivate Phase

**Directive**: `user_directive_deactivate`

**Workflow**:
```json
{
  "trunk": "deactivate_directive",
  "branches": [
    {
      "step": "stop_execution",
      "actions": [
        {"if": "scheduler", "then": "unregister_from_apscheduler"},
        {"if": "background_service", "then": "stop_process"},
        {"if": "event_listener", "then": "unregister_listener"}
      ]
    },
    {
      "step": "update_status",
      "actions": [
        {"update": "user_directives (status=paused)"},
        {"update": "directive_implementations (deployed=0)"},
        {"log": "Directive deactivated", "to": "user-directives.log"}
      ]
    },
    {
      "step": "finalize_logs",
      "actions": [
        {"flush": "execution log"},
        {"rotate": "if needed"},
        {"archive": "current execution session"}
      ]
    }
  ]
}
```

---

## Integration with Existing AIFP System

### aifp_run Gateway Integration

**Enhanced aifp_run Workflow**:
```json
{
  "trunk": "parse_intent",
  "branches": [
    {
      "step": "check_user_directives_status",
      "actions": [
        {"query": "project.user_directives_status from project.db"},
        {"if": "status == 'active'", "then": "load_user_directive_context"},
        {"note": "Replaces checking for .aifp/user_directives.db file existence"}
      ]
    },
    {
      "step": "route_command",
      "branches": [
        {"if": "user directive command", "then": "route_to_user_directive_system"},
        {"if": "coding task", "then": "apply_fp_and_project_directives"},
        {"if": "project management", "then": "apply_project_directives"}
      ]
    }
  ]
}
```

**User Directives Status Field**:
- `project.user_directives_status` field in project.db tracks the state:
  - `NULL` (default): User directives not initialized
  - `'in_progress'`: Parsing/validating directives
  - `'active'`: User directives running and executing
  - `'disabled'`: User directives paused/inactive

**User Directive Command Detection**:
- Keywords: "parse directives", "validate directives", "activate directive", "check directive status"
- File references: ".yaml", ".json" files in user-directives/source/
- Domain keywords: "home automation", "AWS", "cloud", "automate"

### Hybrid Mode: FP Directives + User Directives

**Generated code follows FP principles**:
- Pure functions for data transformation
- Immutable configuration
- Explicit parameters
- Side effects isolated in effect functions

**Example Generated Code**:
```python
# .aifp/user-directives/generated/handlers/lights_5pm_handler.py
# Generated by AIFP User Directive System
# Directive: turn_off_lights_5pm
# Status: Active

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import logging

# Configuration (immutable)
@dataclass(frozen=True)
class LightsConfig:
    api_url: str
    entity_id: str
    timezone_str: str

# Pure function: Build API request
def build_turn_off_request(config: LightsConfig) -> Dict[str, any]:
    """Pure function: Build Home Assistant API request."""
    return {
        "entity_id": config.entity_id,
        "action": "turn_off"
    }

# Effect function: Execute API call (isolated side effect)
def execute_lights_off(config: LightsConfig, request: Dict[str, any]) -> Optional[str]:
    """Effect function: Call Home Assistant API."""
    try:
        # API call here (side effect isolated)
        result = homeassistant_api.call_service(
            config.api_url,
            "/services/light/turn_off",
            request
        )
        return "success" if result.ok else f"error: {result.status_code}"
    except Exception as e:
        logging.error(f"Failed to turn off lights: {e}")
        return f"error: {str(e)}"

# Main handler (composes pure and effect functions)
def handle_lights_5pm():
    """Main handler for turn_off_lights_5pm directive."""
    config = LightsConfig(
        api_url="http://homeassistant.local:8123",
        entity_id="group.living_room_lights",
        timezone_str="America/New_York"
    )

    request = build_turn_off_request(config)
    result = execute_lights_off(config, request)

    # Logging (effect)
    logging.info(f"turn_off_lights_5pm executed: {result}")

    return result
```

### Project Database Updates

**After implementation generation**:
- `project_file_write` directive applies
- Updates `files` table with generated code
- Updates `functions` table with handler functions
- Updates `interactions` table with dependencies

---

## Logging Architecture (File-Based)

### Execution Logs

**Location**: `.aifp/logs/execution/`

**Rotation**: Daily (configurable)

**Retention**: 30 days (configurable)

**Format**: JSON Lines

**Example**:
```json
{"timestamp": "2025-10-22T17:00:00.123Z", "directive": "turn_off_lights_5pm", "status": "success", "duration_ms": 234}
{"timestamp": "2025-10-22T17:05:00.456Z", "directive": "monitor_stove", "status": "skipped", "reason": "stove_off"}
```

### Error Logs

**Location**: `.aifp/logs/errors/`

**Rotation**: 10MB or daily (configurable)

**Retention**: 90 days (configurable)

**Format**: JSON Lines

**Example**:
```json
{"timestamp": "2025-10-22T17:00:00.789Z", "directive": "turn_off_lights_5pm", "error_type": "connection_error", "error_message": "Failed to connect to Home Assistant API", "stack_trace": "..."}
```

### Lifecycle Log

**Location**: `.aifp/logs/user-directives.log`

**Format**: Human-readable text

**Example**:
```
[2025-10-22 16:50:12] INFO: Parsed home_automation.yaml: 3 directives found
[2025-10-22 16:51:30] INFO: Validated turn_off_lights_5pm
[2025-10-22 16:52:45] INFO: Implemented turn_off_lights_5pm
[2025-10-22 16:53:00] INFO: Activated turn_off_lights_5pm
[2025-10-22 17:00:00] INFO: Executed turn_off_lights_5pm: success
```

---

## Example Workflows

### Workflow 1: New Home Automation Project

```bash
User: "aifp run parse .aifp/user-directives/source/home_automation.yaml"

AI: Parsing home_automation.yaml...
    ✅ Found 3 directives
    ⚠️  Ambiguities detected:
       - "which lights at 5pm?"
       - "stove entity ID?"

    Run validation? (y/n)

User: y

AI: 🔍 Validating directive: turn_off_lights_5pm
    ❓ Which lights should be turned off at 5pm?
       a) All lights in the house
       b) Living room lights only
       c) Specific lights

User: b

AI: ❓ Should this account for daylight savings time?

User: yes

AI: ✅ Directive validated

    Implement now? (y/n)

User: y

AI: 📦 Dependency check:
       Required: homeassistant-api, apscheduler
       Install homeassistant-api? (y/n)

User: y

AI: Installing dependencies...
    ✅ Dependencies installed
    📝 Generating implementation code...
    ✅ Code generated: lights_5pm_handler.py

    Activate directive? (y/n)

User: y

AI: 🚀 Activating turn_off_lights_5pm...
    ✅ Scheduler registered
    🟢 Directive active

    Next execution: Today at 5:00 PM EST
```

### Workflow 2: AWS Infrastructure Management

```bash
User: "aifp run parse .aifp/user-directives/source/aws_management.json"

AI: Parsing aws_management.json...
    ✅ Found 1 directive: scale_ec2_instances

    Validating...
    ❓ What AWS region?

User: us-east-1

AI: ❓ What CPU threshold should trigger scaling? (currently: 80%)

User: 75%

AI: ✅ Directive validated

    📦 Dependencies: boto3>=1.20.0
    Install boto3? (y/n)

User: y

AI: ✅ boto3 installed
    📝 Generating AWS scaling service...
    ✅ Code generated: ec2_scaler_service.py

    🚀 Activating scale_ec2_instances...
    ✅ Background service started (PID: 12345)
    🟢 Directive active and monitoring
```

---

## Status and Monitoring

### Get User Directive Status

**Command**: `aifp run user-directive-status`

**Output**:
```
📊 User Directive Status

Active Directives: 3
Paused: 0
Errors: 0

🟢 turn_off_lights_5pm
   Status: Active
   Next execution: Today at 5:00 PM EST
   Total executions: 24
   Success rate: 100%
   Last execution: Yesterday at 5:00 PM (success)

🟢 monitor_stove
   Status: Active
   Running every 60 seconds
   Total executions: 1440
   Success rate: 100%
   Last execution: 2 minutes ago (stove off, skipped action)

🟢 scale_ec2_instances
   Status: Active (background service, PID: 12345)
   Running every 5 minutes
   Total executions: 288
   Success rate: 98.6%
   Last execution: 3 minutes ago (success)
   Last error: 2 hours ago (connection timeout)

Logs:
  Execution: .aifp/logs/execution/current.log
  Errors: .aifp/logs/errors/current_errors.log
```

---

## Complete Workflow: User Directive Lifecycle

### Overview

When user directives are active, **the AIFP project's purpose becomes implementing and executing those directives**. The AI builds all necessary code, dependencies, helper functions, cron jobs, and automations to fulfill the user's requirements.

### Status Progression

```
NULL → in_progress → (user testing) → (user approval) → active → (modifications) → in_progress → ...
```

**Status Semantics**:
- `NULL`: No user directives initialized
- `in_progress`: AI building/modifying implementation OR user testing before approval
- `active`: User approved, directives successfully running
- `disabled`: All directives paused but implementation preserved

### End-to-End Flow

#### Phase 1: Installation and Setup
```
1. User installs AIFP MCP
2. User creates new or opens existing project
3. User adds directive file (.aifp/user-directives/source/my_directives.yaml)
```

#### Phase 2: Parse and Validate
```
4. User: "Parse my directives"
5. AI calls user_directive_parse:
   - Reads directive file
   - Extracts directives
   - Identifies ambiguities
   - Stores in user_directives.db
   - Sets project.user_directives_status = 'in_progress'

6. AI calls user_directive_validate:
   - Interactive Q&A with user
   - Resolves ambiguities
   - Confirms understanding
   - Marks directives as validated
```

#### Phase 3: Implementation
```
7. AI calls user_directive_implement:
   - Analyzes requirements
   - Prompts user for dependency installation
   - Generates FP-compliant code (handlers, services, cron jobs)
   - Creates helper functions
   - Sets up automations
   - Updates project.purpose to reflect user directives
   - Updates project.goals_json
   - Writes all implementation files
   - Updates project.db (files, functions, infrastructure)
   - Creates testing instructions for user
   - Status remains 'in_progress' (waiting for user testing/approval)
```

#### Phase 4: User Testing
```
8. User tests implementation:
   - Runs generated code
   - Verifies automation triggers
   - Checks expected behaviors
   - Tests edge cases
   - Long-running testing period as needed
```

#### Phase 5: User Approval
```
9. User: "Approve directives" or "Testing complete"
10. AI calls user_directive_approve:
    - Prompts: "Have you tested? Is it working as expected?"
    - If YES:
      - Marks directives as approved
      - Logs approval to notes
      - Prompts: "Activate directives now?"
    - If NO or NEEDS_CHANGES:
      - Collects feedback
      - Returns to implementation phase
      - Status stays 'in_progress'
```

#### Phase 6: Activation
```
11. AI calls user_directive_activate:
    - Verifies approval (aborts if not approved)
    - Verifies implementation
    - Deploys services (schedulers, event handlers, daemons)
    - Initializes execution tracking
    - Sets up file-based logging
    - Sets project.user_directives_status = 'active'

12. Directives now running and monitored
```

#### Phase 7: Modifications (Loop Back)
```
13. User modifies directive source file
14. AI detects changes via user_directive_update:
    - If directives are active: deactivates them
    - Sets approved = false
    - Sets project.user_directives_status = 'in_progress'
    - Re-validates and re-implements
    - Prompts user to test and approve again
    - Returns to Phase 4 (User Testing)
```

### Key Principles

1. **Project Purpose Alignment**: When user directives are active, the project exists to execute those directives. All development serves that purpose.

2. **Approval Gate**: Implementation must be tested and approved by user before activation. Status only moves from `in_progress` to `active` after approval.

3. **Modification Reset**: Any changes to directive source files return status to `in_progress` and require re-approval.

4. **Long-Running Testing**: Users can test implementations for extended periods before approval.

5. **AI Builds Everything**: The AI generates all code, installs dependencies, creates helpers, sets up automations - the complete working system.

### Example Timeline

```
Day 1:
  10:00 - User creates home_automation.yaml
  10:05 - AI parses and validates (5 minutes of Q&A)
  10:15 - AI implements (generates code, installs dependencies)
  10:30 - Implementation complete, status='in_progress'

Days 1-7:
  - User tests implementation
  - Verifies lights turn off at 5pm
  - Tests stove monitoring
  - Confirms behavior over week

Day 7:
  09:00 - User: "Approve directives"
  09:01 - AI: "Activate now?" User: "Yes"
  09:02 - Status changes to 'active'
  09:02+ - Directives running and monitored

Week 2:
  14:30 - User modifies directive (change time to 6pm)
  14:31 - AI detects change, deactivates, returns to 'in_progress'
  14:35 - AI re-implements with new time
  14:40 - User tests for 2 days

Day 9:
  16:00 - User approves, reactivates
  16:01 - Status back to 'active'
```

---

## Future Enhancements

1. **Directive Templates Library**
   - Pre-built templates for common automation tasks
   - Community-contributed directive examples

2. **Directive Testing Framework**
   - Dry-run mode to test directives without executing
   - Mock API responses for testing

3. **Web UI for Directive Management**
   - Visual directive editor
   - Real-time execution monitoring dashboard

4. **Multi-Domain Orchestration**
   - Cross-domain directives (e.g., AWS triggers home automation)
   - Workflow composition (chain multiple directives)

5. **AI Learning from Execution**
   - Learn optimal trigger times from execution history
   - Suggest improvements based on error patterns

---

## Summary

The User-Defined Directives System transforms AIFP into a flexible automation framework where:

- **Users write directives** in simple YAML/JSON/TXT files
- **AI validates and implements** through interactive Q&A
- **Code follows FP principles** for maintainability
- **Real-time execution** via background services
- **File-based logging** keeps databases lean
- **Hybrid mode** integrates with existing AIFP directives

This enables use cases like home automation, cloud infrastructure management, and custom workflows without writing extensive code.

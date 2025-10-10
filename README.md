# 🤓 AIFP MCP Server

## Introduction to AIFP

**AIFP (AI Functional Procedural)** is a **language-agnostic programming paradigm** optimized for AI-generated and AI-maintained code.
It defines strict but flexible rules to make code **machine-efficient**, **predictable**, and **queryable**, while keeping projects **finite and traceable**.

### ✫️ Core Principles

| Principle                    | Description                                                                                                 |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Functional–Procedural**    | Use **pure functions** and **explicit sequencing** — no classes, no hidden state, no mutation by default.   |
| **AI-Readable Code**         | Flat, deterministic code is easier for AI to reason about and extend.                                       |
| **Database-Indexed Logic**   | Every function, file, and relationship is tracked in SQLite for instant AI access — no reparsing.           |
| **Dynamic Library Wrappers** | Bridges legacy OOP libraries into pure functional flows automatically.                                      |
| **Roadmap-Driven Projects**  | Each project follows a **completion path** — a defined set of steps preventing infinite development cycles. |

### 🧬 Why AIFP Exists

AI struggles with:

* OOP structures designed for humans, not machines.
* Context loss between coding sessions.
* Endless project drift without defined completion goals.

AIFP solves this by merging **functional procedural code** with **project-level AI management**, all guided by **immutable directives** stored in the MCP.

---

## 🖥️ MCP Server Overview

The **MCP (AI Project Management)** server is the *governing layer* of AIFP.
It provides a **read-only core database** (`aifp_core.db`) that defines how AI must operate — and a **per-project database** (`project.db`) that AI manages dynamically.

### 🧱 Two-Sided Architecture

| Side                            | Role       | Description                                                                                             |
| ------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------- |
| **MCP Side (`aifp_core.db`)**   | Read-only  | Defines all directives, helpers, and tools. These are immutable and serve as AIFP’s rulebook.           |
| **Project Side (`project.db`)** | Read/Write | Created by the AI per project. Tracks files, functions, roadmap progress, and context for continuation. |

---

## ⚙️ MCP Side Structure (`aifp_core.db`)

| Component            | Purpose                                                                                                                          |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Directives**       | JSON-based “if-then” workflows guiding AI behavior. Each directive has an optional `.md` file for human-readable escalation.     |
| **Categories**       | Grouping layer for directives (e.g., FP categories like *purity*, *immutability*; Project categories like *init*, *validation*). |
| **Helper Functions** | Pre-written Python utilities (e.g., `track_file_creation`, `init_project_db`) that AI calls to interact with databases safely.   |
| **Tools**            | Lightweight Python entry points (e.g., `aifp_run_tool.py`) that map directly to directives.                                      |
| **Notes**            | Persistent log for directive clarifications or system escalations.                                                               |

### Example Directives

| Directive                        | Type      | Description                                                                     |
| -------------------------------- | --------- | ------------------------------------------------------------------------------- |
| **`aifp_run`**                   | `project` | Root directive. Parses user intent and routes to the proper workflow.           |
| **`project_init`**               | `project` | Creates new projects and initializes `project.db`.                              |
| **`project_task_decomposition`** | `project` | Breaks down complex goals into tasks, subtasks, and sidequests.                 |
| **`project_file_write`**         | `project` | Handles code generation (outputs `FILE: ... CONTENT: ... AIFP_WRITE_COMPLETE`). |
| **`fp_purity`**                  | `fp`      | Ensures all generated code consists of pure functions.                          |
| **`fp_no_oop`**                  | `fp`      | Detects and refactors OOP constructs into functional equivalents.               |
| **`fp_side_effects_flag`**       | `fp`      | Flags or isolates side effects (I/O, mutation).                                 |

---

## 📂 Project Side Structure (`project.db`)

Each AIFP project maintains its own database — a lightweight, persistent “state brain.”

| Table                                                  | Purpose                                                                 |
| ------------------------------------------------------ | ----------------------------------------------------------------------- |
| **project**                                            | Stores project metadata (name, purpose, goals, version).                |
| **files**                                              | Tracks file paths, checksums, and languages.                            |
| **functions**                                          | Stores function metadata (name, parameters, docstrings, dependencies).  |
| **themes / flows**                                     | AI-generated groupings for logical and procedural organization.         |
| **completion_path**                                    | Defines project roadmap — the ordered path from start to completion.    |
| **milestones / tasks / subtasks / sidequests / items** | Multi-tiered task tracking system.                                      |
| **notes**                                              | Logs clarifications, pivots, or user feedback tied to project entities. |

The AI updates `project.db` automatically after every relevant directive execution.

---

## 🔁 How It Works — The AIFP Run Cycle

### 1. **User Command**

```bash
aifp run [task]
```

Examples:

* `aifp run Create math_utils.py with add function`
* `aifp run Hey, I want to start a project for a math library.`
* `aifp run Verify compliance for math_utils.py`

### 2. **Intent Parsing**

AI queries the MCP:

```sql
SELECT * FROM directives WHERE name='aifp_run';
```

It then matches the user’s request to an intent branch (e.g., *create project* → `init_project`).

### 3. **Directive Execution**

AI follows the workflow JSON for the matched directive:

* Prompt for missing data.
* Generate or update files.
* Run FP compliance checks.
* Update project DB via helper functions.

### 4. **Structured Output**

AI outputs deterministic file structures:

```
FILE: math_utils.py
CONTENT:
# AIFP_METADATA: {"function_names": ["add"], "deps": [], "theme": "math_ops", "flow": "addition_flow", "version": 1, "task_id": 1}
# Project Purpose: Pure functional matrix math library
def add(a: int, b: int) -> int:
    """Pure: Adds two integers."""
    return a + b
AIFP_WRITE_COMPLETE
```

### 5. **Validation and Update**

AI checks compliance (no OOP, metadata present, DB updated).
If compliant → updates `files`, `functions`, and marks `task_id` as complete.

If not → AI alerts:

```
Compliance failed for math_utils.py.
Issue: OOP detected (class Add).
Fix per directive: fp_no_oop.
Retry: aifp run Create math_utils.py with add function
```

---

## ⚙️ Command Flow Summary

```mermaid
graph TD
A[aifp run] --> B[Parse intent via aifp_core.db]
B --> C[Match Directive: aifp_run]
C --> D[Sub-directive: init_project | file_write | update_db | compliance_check]
D --> E[Execute Workflow (helpers, prompts, parallel ops)]
E --> F[Generate Output or Update project.db]
F --> G[Validate via FP Directives (e.g., fp_purity)]
G --> H[Log or Escalate via Notes if Needed]
```

---

## 🤓 Example Interaction

**User:**

> aifp run Hey, I want to create a project for a math library with fast computation.

**AI:**

```
Matched directive: aifp_run (intent: create project)
Sub-directive: init_project
Please provide a project name (e.g., MatrixCalculator).
```

**User:**

> aifp run Set name to MatrixCalculator with purpose 'Pure functional matrix math library' and goals '["Fast computation", "No OOP"]'

**AI:**

```
Project initialized successfully:
- project: MatrixCalculator
- purpose: Pure functional matrix math library
- goals: ["Fast computation", "No OOP"]
- completion_path: Setup (order_index=1)
Scaffolded: .aifp-project/
Next: aifp run Create math_utils.py with add function --task_id 1
```

**Next Step:**

> aifp run Create math_utils.py with add function --task_id 1

**AI Output:**

```
FILE: math_utils.py
CONTENT:
# AIFP_METADATA: {"function_names": ["add"], "deps": [], "theme": "math_ops", "flow": "addition_flow", "version": 1, "task_id": 1}
# Project Purpose: Pure functional matrix math library
def add(a: int, b: int) -> int:
    """Pure: Adds two integers."""
    return a + b
AIFP_WRITE_COMPLETE
```

---

## 🧬 Future Extensions

* **Directive Analytics:** Visualize directive usage and escalation patterns.
* **IDE Integration:** VS Code extension for interactive task management.
* **Advanced Error Handling:** Expand `roadblocks_json` for detailed automated recovery.

---

## 📘 Design Philosophy

> **Immutable rules, evolving projects.**

* The MCP (`aifp_core.db`) is **read-only** — the rulebook.
* The Project (`project.db`) is **read/write** — the playground.
* Directives define the boundaries; AI operates freely within them.

This architecture ensures consistent behavior across sessions and AIs — every AIFP project follows the same logic, structure, and reasoning flow.

---

## 📄 References

* **Core DB:** [`aifp_core.db`](./aifp_core.db)
* **Project Template:** `.aifp-project/project.db`
* **Directive Definitions:** `/directives/*.md`
* **Schema Files:** `/schemas/schemaExampleMCP.txt`, `/schemas/schemaExampleProject.txt`

---

### ⚖️ License

MIT — Open standard for AI-optimized programming.

---

## ✅ Summary

**AIFP MCP Server** transforms AI from a “code generator” into a **structured project collaborator**.
It combines pure functional programming, declarative project management, and rule-driven reasoning — creating a consistent, scalable ecosystem for AI-native development.

🧩 Technical Addendum — AIFP MCP Schema v1.3

Highlights

Directive Categories — Directives are now grouped under named categories (e.g., purity, task_management, error_handling) for easier querying and reasoning.

Directive Interactions — The MCP now models directive relationships in a dedicated directives_interactions table, allowing dependency tracing, validation, and visualization.

Notes Table — Expanded for structured reasoning logs and post-run audits.

Sync Manager Script — scripts/sync_directives.py automates JSON-to-DB synchronization, ensuring the MCP database always matches directive definitions.

Integrity Validation — The sync process runs built-in validation, checking for missing parents, invalid references, and FP rule violations.

Schema Version 1.3 — Current canonical structure; future MCP releases will maintain backward compatibility.

📊 Schema Overview
Table	Purpose
directives	Defines all FP and project directives (core logic)
categories	Defines reusable classification tags
directive_categories	Many-to-many link between directives and categories
directives_interactions	Defines graph-like relationships between directives
helper_functions	Reusable database utility scripts
tools	MCP tools mapped to directives
notes	Reasoning log and audit trail
⚙️ Directive Sync Workflow
Edit or add directive JSON files in /directives/.
Run python scripts/sync_directives.py.

The script:
Loads FP and Project JSON definitions.
Upserts entries into directives, categories, and linking tables.
Imports relationships from project_directive_graph.json.
Validates schema integrity.
Output written to logs/sync_report.json.

🧩 Validation Checks Performed
FP directives cannot have level values.
All parent directives must exist.
All relationships must resolve to valid directives.
Duplicate category links are removed.
Notes table must exist (and may optionally hold MCP reasoning).

🧾 Version History
Version	Summary	Date
1.2	Introduced MCP concept and base directives.	—
1.3	Added directive categories, relationships, helper/tools schema, and automated sync/validation.	✅ Current
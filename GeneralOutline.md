# AIProgrammingMethods – Project Outline

## Overview

**AIProgrammingMethods** is a methodology and framework for AI-native programming. It defines how source code should be structured, stored, queried, and extended so that artificial intelligence can collaborate effectively with human developers.

This project lives under an **MCP Server Model (Model Context Protocol)**, where logic discussions, reasoning trees, task mapping, and coding conventions are tracked persistently and updated as decisions evolve.

---

## 🧠 Core Objectives

* **AI-native design**: Optimize for machine parsing, logic extension, and clarity of intent.
* **Function-first approach**: Use small, single-responsibility functions instead of traditional OOP structures.
* **Flat modular structure**: Each file contains one concept, avoids nesting or bloat.
* **Database-indexed logic**: A central SQLite DB (`aimethods.db`) stores metadata about every function/module.
* **Persistent reasoning**: Evolution of project scope and logic is stored in `projectLogic.jsonl` for traceability.
* **Human-AI interoperability**: Designed for clarity and ease of interaction between humans and LLMs.

---

## 🗂️ File/Folder Layout (Live Spec)

```
AIProgrammingMethods/
├── project-outline.md          # ← You are here (updated as the project evolves)
├── projectLogic.jsonl          # Persistent logic discussions, decision trees, reasonings
├── aimethods.db                # SQLite database containing function/module metadata
├── schemas/
│   └── aimethods.sqlite.sql    # SQL schema definition for the SQLite database
├── modules/                    # Core functions organized by purpose
│   ├── string/
│   │   └── split_lines.py
│   ├── math/
│   │   └── normalize.py
│   ├── io/
│   │   └── read_file.py
├── tools/
│   └── codegen/
│       └── scaffold_function.py
└── readme.md
```

---

## 🧱 SQLite Database Schema (Concept Definition)

### Design Approach Discussion

Before finalizing the schema, we must consider the *organizational anchor* for indexing and referencing logic: Should the database be **function-centric**, **file-centric**, or **theme-centric**?

### Reasoning

* A **function-centric model** is granular, ideal for AI parsing and reasoning about atomic units of logic. It is useful for low-level modification, summarization, and extension.
* A **file-centric model** reflects the real-world structure developers interact with. It’s better for navigating codebases, reviewing by module, or assigning contributors.
* A **theme-centric model** introduces mid-level abstraction for grouping multiple files and functions under common purpose (e.g., "payment request system" or "blockchain adapters").

To support all three mental models—for both humans and AI agents—we propose a **hybrid schema**:

* Functions are indexed and tracked.
* Files are first-class citizens.
* Themes (aka *components* or *domains*) allow mapping and grouping of logic.

### Schema Goals

* Allow discovery and reasoning from both top-down (theme → file → function) and bottom-up (function → file → theme).
* Enable AI to traverse logic trees, understand responsibility boundaries, and extend functionality safely.
* Facilitate maintainability for complex, multi-domain systems (e.g., DeFi apps, blockchain interfaces, UI layers).

---

The `aimethods.db` file acts as a **logic registry** for the codebase. Its role is to map, track, and extend the knowledge graph of the system’s modular code through a queryable relational structure.

### Schema Goals:

* Index every function, its metadata, and purpose.
* Allow querying by file, input/output shape, domain, and tags.
* Track cross-function dependencies.
* Store AI-human discussion notes per module.
* Enable MCP agents to reason about function relevance, duplication, and extension.

### Initial Tables

#### `themes`

Defines high-level groupings (domains, interfaces, systems).

```
id INTEGER PRIMARY KEY
name TEXT NOT NULL UNIQUE
description TEXT
is_active BOOLEAN DEFAULT 1
```

#### `theme_relationships`

Tracks associations between themes (e.g. dependencies, API links).

```
id INTEGER PRIMARY KEY
theme_id INTEGER NOT NULL
related_theme_id INTEGER NOT NULL
relation_type TEXT  -- e.g., 'calls', 'depends_on', 'extends'
FOREIGN KEY (theme_id) REFERENCES themes(id)
FOREIGN KEY (related_theme_id) REFERENCES themes(id)
```

#### `files`

Stores file-level information and mappings to themes.

```
file_path TEXT PRIMARY KEY
description TEXT
size_bytes INTEGER
last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
is_deprecated BOOLEAN DEFAULT 0
theme_id INTEGER
FOREIGN KEY (theme_id) REFERENCES themes(id)
```

#### `functions`

Stores all registered functions/modules.

```
id INTEGER PRIMARY KEY
name TEXT NOT NULL
file_path TEXT NOT NULL
input_signature TEXT
output_signature TEXT
docstring TEXT
tags TEXT
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### `dependencies`

Stores dependency relationships between functions.

```
id INTEGER PRIMARY KEY
function_id INTEGER NOT NULL
depends_on_id INTEGER NOT NULL
FOREIGN KEY (function_id) REFERENCES functions(id)
FOREIGN KEY (depends_on_id) REFERENCES functions(id)
```

#### `notes`

Captures persistent logic notes, decisions, context, and AI-human reasoning.

```
id INTEGER PRIMARY KEY
function_id INTEGER NOT NULL
note TEXT NOT NULL
author TEXT
source TEXT
timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY (function_id) REFERENCES functions(id)
```

## 🧩 Philosophy: Functions vs. Classes

| Principle                 | Description                                                                 |
| ------------------------- | --------------------------------------------------------------------------- |
| **Default to Functions**  | Every module starts with small, testable functions.                         |
| **Avoid OOP**             | No inheritance or unnecessary state unless performance or logic demands it. |
| **Use Classes Sparingly** | Only when encapsulation or multi-method stateful behavior is warranted.     |
| **No Framework Mimicry**  | Avoid generic `Manager`, `Handler`, `Service` abstractions.                 |
| **Modules = Purpose**     | Filenames should reflect action or outcome, not abstraction.                |

---

## ✅ In-Scope MVP Features (Tracked in `projectLogic.jsonl`)

* [ ] Define complete SQLite schema and test DB
* [ ] Implement `scaffold_function.py` for AI-generated modules
* [ ] Establish CLI to query or extend modules (`aimethods query string:split_lines`)
* [ ] Begin standard logic library (`modules/string`, `modules/math`, `modules/fs`)
* [ ] Auto-populate DB entries on module creation
* [ ] Define MCP structure for task memory and scope evolution
* [ ] Write parsing tool for summarizing decision logic in `projectLogic.jsonl`

---

## 📌 Update Protocol

All changes in structure, philosophy, or core decisions should be reflected in:

* `project-outline.md` – current file (conceptual & structural doc)
* `projectLogic.jsonl` – reasoning tree and logic evolution over time
* `schemas/aimethods.sqlite.sql` – SQL structure of the logic DB
* `readme.md` – onboarding and usage instructions (to be built later)

---

## 📌 Notes

* This project is being developed under persistent AI collaboration.
* Every function/module should have a clear, concise docstring.
* Documentation generation and GPT-style summarization will be automated later.
* Eventually, `projectLogic.jsonl` and `aimethods.db` will enable full stateful project reasoning.

---

## ✍ Author

Aryan Duntley
Vision: Human–AI Collaborative Code Ecosystems

---

## 🪪 License

MIT (or TBD upon formalization)

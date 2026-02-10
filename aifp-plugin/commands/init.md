---
description: Initialize AIFP for the current project directory.
---

Call the aifp_init MCP tool with the current working directory as project_root.

This creates the .aifp-project/ directory containing:
- project.db — project state tracking
- user_preferences.db — AI behavior customization
- ProjectBlueprint.md — project architecture template
- Default infrastructure, tracking settings, and backup configuration

After initialization completes (Phase 1 — mechanical setup), begin Phase 2 — intelligent population:
1. Detect the project's language, build tool, and source directory
2. Discuss with the user: project name, purpose, goals
3. Call create_project() to insert the project row
4. Update infrastructure entries and populate ProjectBlueprint.md
5. Route to project_discovery for collaborative planning (themes, flows, completion path, milestones)

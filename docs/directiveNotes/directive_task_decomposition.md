# AIFP Directive: task_decomposition

## Overview
Breaks user tasks into AIFP-compliant paths, managing tasks, subtasks, and sidequests, referencing completion_path in project.db.

## Purpose
Ensures tasks align with project roadmap, with subtasks (high priority, pause parent task) and sidequests (low priority, exploratory) clearly distinguished.

## Workflow Guidance
- Step-by-step: Query tasks and subtasks tables for open entries (status='in_progress'). If request aligns, update task or create subtask (subtasks table, priority=high). If independent/pivots, create new task (update project.version). If exploratory, create sidequest (sidequests table, priority=low). If confidence <0.5, prompt: 'Is this a new task, subtask, or sidequest?'
- Boundaries:
  - New task: Independent, pivots goals, or new milestone in completion_path.
  - Subtask: Supports open task, low-level (e.g., single function), pauses parent, stored in subtasks table.
  - Sidequest: Exploratory, optional, linked to project, stored in sidequests table.
- Interruptions: If subtask active (subtasks.status='in_progress'), notify: "Subtask [name] in progress—complete, discard, or resume?" Update subtasks.status.
- Parallel: If code and DB update needed, execute both (e.g., file_write and update_db).
- Roadblocks: If misaligned, prompt: "This pivots goals—confirm?"
AIFP Directive: File Writing with Dynamic Command Processing
Overview
This directive instructs the AI to process user inputs prefixed with aifp run [task] (e.g., aifp run Create math_utils.py with add function) by dynamically matching the task to directives in aifp_core.db. For file creation or modification, the AI generates output in the AIFP format (FILE: path CONTENT: code AIFP_WRITE_COMPLETE), avoiding native file-writing tools (e.g., Cline’s write_file). The AI validates output for compliance (no OOP, pure functions, includes # AIFP_METADATA) and updates project.db (files, functions, project, completion_path, etc.) using helper functions from aifp_core.db. If compliance fails (e.g., OOP detected, missing DB update), the AI pauses and alerts the user to retry. The project table provides context (purpose, goals), and completion_path ensures tasks align with the project roadmap.
Why This Exists
AIFP requires strict adherence to pure functional programming, no OOP, and comprehensive database tracking to align code with project goals and ensure a finite development path. The single aifp run command simplifies user interaction, while the AI dynamically maps tasks to directives, ensuring consistency without multiple specific commands. This directive handles file-related tasks, leveraging aifp_core.db for rules and project.db for tracking.
When to Use

Trigger: User inputs aifp run [task] with a file creation/modification intent (e.g., Create math_utils.py).
Context: Manual workflow where users drive actions with a single command, and the AI matches to directives.
Escalation: If task intent is unclear or output non-compliant, escalate to directive_file_write_detailed.json. For code style, reference directive_fp_code_generation.md.

Guidelines for AI

Command Processing:

Parse aifp run [task] to identify intent (e.g., “create”/“write” → file_write, “check” → compliance_check).
Query aifp_core.db for the matching directive (e.g., SELECT * FROM directives WHERE id = 'file_write').
Execute directive actions and associated helper functions (e.g., track_file_creation for DB updates).


Output Format:

Never use native file-writing tools.
Output:FILE: path/to/file.py
CONTENT:
# AIFP_METADATA: {"function_names": ["func1"], "deps": ["func2"], "theme": "math_ops", "flow": "addition_flow", "version": 1, "task_id": 1}
# Project Purpose: [from project table]
[AIFP-compliant code]
AIFP_WRITE_COMPLETE


Include AIFP_METADATA with:
function_names: Defined functions.
deps: Called functions or wrapped libraries.
theme/flow: From project.db, aligned with completion_path.
version: File version.
task_id: Links to tasks or items table.




Code Compliance:

Follow AIFP: pure functions, no OOP, procedural flows, immutable by default.
Include type annotations (e.g., def add(a: int, b: int) -> int).
Reference project table for purpose/goals in comments.


Validation:

Check output:
No OOP (class\s+ regex).
Has # AIFP_METADATA and AIFP_WRITE_COMPLETE.
DB updated (e.g., SELECT COUNT(*) FROM files WHERE path = ?).


If non-compliant, alert:Compliance failed for [path]. Issue: [OOP detected | Missing AIFP_METADATA | No DB update].
Fix per directive [id]: [example_out]
Retry: aifp run [task]




Project Context:

Query project table for purpose/goals:SELECT purpose, goals_json FROM project WHERE id = ?;


Include in output: # Purpose: Pure functional matrix math library.


Completion Path:

Query completion_path to align tasks:SELECT name, description FROM completion_path WHERE status != 'complete' AND project_id = ? ORDER BY order_index LIMIT 1;


Update tasks or items on completion.


Edge Cases:

Unclear Intent: Query directives for best match (e.g., by keyword).
Missing Metadata: Infer via infer_metadata, alert user to retry.
OOP Detected: Alert: Fix OOP per anti_oop_redirect.
DB Failure: Alert: Run aifp run Update DB for [path].



Example
User Input: aifp run Create math_utils.py with add function --project_id 1 --task_id 1
AI Output:
FILE: math_utils.py
CONTENT:
# AIFP_METADATA: {"function_names": ["add"], "deps": [], "theme": "math_ops", "flow": "addition_flow", "version": 1, "task_id": 1}
# Project Purpose: Pure functional matrix math library
def add(a: int, b: int) -> int:
    """Pure: Adds two integers."""
    return a + b

AIFP_WRITE_COMPLETE
Please run: aifp run Verify compliance and update DB for math_utils.py --project_id 1 --task_id 1

User Input: aifp run Verify compliance and update DB for math_utils.py --project_id 1 --task_id 1
AI Output:
Compliance check for math_utils.py:
- No OOP: Pass
- AIFP_METADATA present: Pass
- AIFP_WRITE_COMPLETE: Pass
project.db updated:
- files: math_utils.py (project_id=1)
- functions: add (file_id=1)
- file_flows: Linked to addition_flow
- tasks: task_id=1 marked done
Next task: aifp run [next task from completion_path] --project_id 1

If Compliance Fails:
Compliance failed for math_utils.py. Issue: OOP detected (class Add).
Fix per directive anti_oop_redirect:
Example: def add(a: int, b: int) -> int: return a + b
Retry: aifp run Create math_utils.py with add function --project_id 1 --task_id 1

Integration with Databases

aifp_core.db: Stores directives and helper functions.
Directive: file_write for file creation.
Helpers: track_file_creation, check_oop.


project.db: Tracks project state.
project: Guides AI with purpose/goals.
completion_path: Ensures finite roadmap.



References

Escalation Files: directive_file_write_detailed.json, directive_file_write_compressed.json.
Related Directives: directive_fp_code_generation.md, directive_anti_oop_redirect.md.
DBs: aifp_core.db, project.db.

Implementation Notes

AI: Parses aifp run input, queries aifp_core.db, executes helper functions.
User: Runs aifp run [task] in VS Code terminal.
Validation: Simple regex and DB checks, alerts for fixes.

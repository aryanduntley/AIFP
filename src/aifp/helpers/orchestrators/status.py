"""
AIFP Helper Functions - Orchestrator Status Helpers

Read-only status and context retrieval from project.db.

Helpers in this file:
- get_project_status: Work hierarchy data with counts + nested tree (single pass)
- get_work_context: Complete context for resuming a specific work item

All helpers target project.db only. No decision logic — AI interprets data.
"""

import sqlite3
from typing import Optional, Tuple, Dict, Any, List

from ._common import (
    _open_project_connection,
    _close_connection,
    get_return_statements,
    row_to_dict,
    rows_to_tuple,
    Result,
    VALID_STATUS_TYPES,
    VALID_WORK_ITEM_TYPES,
    WORK_ITEM_TABLE_MAP,
)


# ============================================================================
# get_project_status
# ============================================================================

def get_project_status(
    project_root: str,
    type: str = "summary",
) -> Result:
    """
    Retrieve work hierarchy data from project database.

    Returns structured counts, flat records, and nested tree in a single pass.
    Replaces the former separate get_status_tree helper.

    Args:
        project_root: Absolute path to project root directory
        type: 'quick' (counts only), 'summary' (default), or 'detailed' (all history)

    Returns:
        Result with data={
            counts: {completion_paths, milestones, tasks, subtasks, sidequests,
                     incomplete_tasks, incomplete_subtasks, incomplete_sidequests,
                     blocked_items},
            completion_paths: tuple,
            milestones: tuple,
            tasks: tuple,
            subtasks: tuple,
            sidequests: tuple,
            blocked_items: tuple,
            current_focus: dict or None,
            tree: {completion_paths: [...{milestones: [...{tasks: [...{subtasks: [...]}]}]}],
                   sidequests: [...]}
        }
    """
    if type not in VALID_STATUS_TYPES:
        return Result(
            success=False,
            error=f"Invalid type '{type}'. Valid: {sorted(VALID_STATUS_TYPES)}",
        )

    try:
        conn = _open_project_connection(project_root)
        try:
            # Counts (always fetched)
            counts = _get_work_counts(conn)

            if type == 'quick':
                # Quick: counts + current in_progress item only
                current_focus = _get_current_focus(conn)
                return Result(
                    success=True,
                    data={
                        'counts': counts,
                        'current_focus': current_focus,
                    },
                    return_statements=get_return_statements("get_project_status"),
                )

            # Summary or detailed: fetch records
            include_completed = (type == 'detailed')
            records = _get_work_records(conn, include_completed)

            # Build nested tree from the fetched records
            tree = _build_tree(records)

            # Get blocked items
            blocked = _get_blocked_items(conn)

            # Current focus (priority: sidequest > subtask > task)
            current_focus = _get_current_focus(conn)

            data = {
                'counts': counts,
                'completion_paths': records['completion_paths'],
                'milestones': records['milestones'],
                'tasks': records['tasks'],
                'subtasks': records['subtasks'],
                'sidequests': records['sidequests'],
                'blocked_items': blocked,
                'current_focus': current_focus,
                'tree': tree,
            }

            return Result(
                success=True,
                data=data,
                return_statements=get_return_statements("get_project_status"),
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return Result(success=False, error=str(e))
    except Exception as e:
        return Result(success=False, error=f"Failed to get project status: {str(e)}")


def _get_work_counts(conn: sqlite3.Connection) -> Dict[str, int]:
    """Effect: Get aggregate counts for all work hierarchy levels."""
    counts = {}
    count_queries = {
        'completion_paths': "SELECT COUNT(*) as cnt FROM completion_path",
        'milestones': "SELECT COUNT(*) as cnt FROM milestones",
        'tasks': "SELECT COUNT(*) as cnt FROM tasks",
        'subtasks': "SELECT COUNT(*) as cnt FROM subtasks",
        'sidequests': "SELECT COUNT(*) as cnt FROM sidequests",
        'incomplete_tasks': "SELECT COUNT(*) as cnt FROM tasks WHERE status != 'completed'",
        'incomplete_subtasks': "SELECT COUNT(*) as cnt FROM subtasks WHERE status != 'completed'",
        'incomplete_sidequests': "SELECT COUNT(*) as cnt FROM sidequests WHERE status != 'completed'",
        'blocked_items': "SELECT COUNT(*) as cnt FROM tasks WHERE status = 'blocked'",
    }
    for key, sql in count_queries.items():
        cursor = conn.execute(sql)
        row = cursor.fetchone()
        counts[key] = row['cnt'] if row else 0
    return counts


def _get_current_focus(conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """Effect: Get current in_progress work item (priority: sidequest > subtask > task)."""
    # Check sidequests first
    cursor = conn.execute(
        "SELECT *, 'sidequest' as item_type FROM sidequests "
        "WHERE status = 'in_progress' ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row:
        return row_to_dict(row)

    # Then subtasks
    cursor = conn.execute(
        "SELECT *, 'subtask' as item_type FROM subtasks "
        "WHERE status = 'in_progress' ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row:
        return row_to_dict(row)

    # Then tasks
    cursor = conn.execute(
        "SELECT *, 'task' as item_type FROM tasks "
        "WHERE status = 'in_progress' ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if row:
        return row_to_dict(row)

    return None


def _get_work_records(
    conn: sqlite3.Connection,
    include_completed: bool,
) -> Dict[str, Tuple[Dict[str, Any], ...]]:
    """Effect: Get work records. Summary excludes completed (except last 5)."""
    records = {}

    # Completion paths (always all)
    cursor = conn.execute("SELECT * FROM completion_path ORDER BY id")
    records['completion_paths'] = rows_to_tuple(cursor.fetchall())

    # Milestones
    cursor = conn.execute("SELECT * FROM milestones ORDER BY completion_path_id, id")
    records['milestones'] = rows_to_tuple(cursor.fetchall())

    if include_completed:
        # Detailed: all records
        cursor = conn.execute("SELECT * FROM tasks ORDER BY milestone_id, id")
        records['tasks'] = rows_to_tuple(cursor.fetchall())

        cursor = conn.execute("SELECT * FROM subtasks ORDER BY task_id, id")
        records['subtasks'] = rows_to_tuple(cursor.fetchall())

        cursor = conn.execute("SELECT * FROM sidequests ORDER BY id")
        records['sidequests'] = rows_to_tuple(cursor.fetchall())
    else:
        # Summary: incomplete + last 5 completed for context
        cursor = conn.execute(
            "SELECT * FROM tasks WHERE status != 'completed' "
            "UNION ALL "
            "SELECT * FROM ("
            "  SELECT * FROM tasks WHERE status = 'completed' "
            "  ORDER BY id DESC LIMIT 5"
            ") ORDER BY milestone_id, id"
        )
        records['tasks'] = rows_to_tuple(cursor.fetchall())

        cursor = conn.execute(
            "SELECT * FROM subtasks WHERE status != 'completed' "
            "UNION ALL "
            "SELECT * FROM ("
            "  SELECT * FROM subtasks WHERE status = 'completed' "
            "  ORDER BY id DESC LIMIT 5"
            ") ORDER BY task_id, id"
        )
        records['subtasks'] = rows_to_tuple(cursor.fetchall())

        cursor = conn.execute(
            "SELECT * FROM sidequests WHERE status != 'completed' "
            "UNION ALL "
            "SELECT * FROM ("
            "  SELECT * FROM sidequests WHERE status = 'completed' "
            "  ORDER BY id DESC LIMIT 5"
            ") ORDER BY id"
        )
        records['sidequests'] = rows_to_tuple(cursor.fetchall())

    return records


def _build_tree(
    records: Dict[str, Tuple[Dict[str, Any], ...]],
) -> Dict[str, Any]:
    """Pure: Build nested tree from flat records."""
    # Index subtasks by task_id
    subtasks_by_task = {}
    for st in records.get('subtasks', ()):
        task_id = st.get('task_id')
        if task_id not in subtasks_by_task:
            subtasks_by_task[task_id] = []
        subtasks_by_task[task_id].append(st)

    # Index tasks by milestone_id, embed subtasks
    tasks_by_milestone = {}
    for t in records.get('tasks', ()):
        ms_id = t.get('milestone_id')
        task_with_children = dict(t)
        task_with_children['subtasks'] = tuple(subtasks_by_task.get(t.get('id'), []))
        if ms_id not in tasks_by_milestone:
            tasks_by_milestone[ms_id] = []
        tasks_by_milestone[ms_id].append(task_with_children)

    # Index milestones by completion_path_id, embed tasks
    milestones_by_path = {}
    for m in records.get('milestones', ()):
        cp_id = m.get('completion_path_id')
        ms_with_children = dict(m)
        ms_with_children['tasks'] = tuple(tasks_by_milestone.get(m.get('id'), []))
        if cp_id not in milestones_by_path:
            milestones_by_path[cp_id] = []
        milestones_by_path[cp_id].append(ms_with_children)

    # Build completion paths with embedded milestones
    tree_paths = []
    for cp in records.get('completion_paths', ()):
        cp_with_children = dict(cp)
        cp_with_children['milestones'] = tuple(milestones_by_path.get(cp.get('id'), []))
        tree_paths.append(cp_with_children)

    return {
        'completion_paths': tuple(tree_paths),
        'sidequests': records.get('sidequests', ()),
    }


def _get_blocked_items(conn: sqlite3.Connection) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get all blocked work items across tables."""
    blocked = []

    cursor = conn.execute(
        "SELECT *, 'task' as item_type FROM tasks WHERE status = 'blocked'"
    )
    blocked.extend(row_to_dict(row) for row in cursor.fetchall())

    cursor = conn.execute(
        "SELECT *, 'subtask' as item_type FROM subtasks WHERE status = 'blocked'"
    )
    blocked.extend(row_to_dict(row) for row in cursor.fetchall())

    return tuple(blocked)


# ============================================================================
# get_work_context
# ============================================================================

def get_work_context(
    project_root: str,
    work_item_type: str,
    work_item_id: int,
    include_interactions: bool = False,
    include_history: bool = False,
) -> Result:
    """
    Get complete context for resuming work on a specific item.

    Single call retrieves the work item + associated items + flows + files +
    functions, and optionally interactions and note history.

    Args:
        project_root: Absolute path to project root directory
        work_item_type: 'task', 'subtask', or 'sidequest'
        work_item_id: ID of the work item
        include_interactions: Include function dependency interactions
        include_history: Include note history for work item

    Returns:
        Result with data={
            work_item: dict,
            items: tuple,
            flows: tuple,
            files: tuple,
            functions: tuple,
            interactions: tuple (if requested),
            notes: tuple (if requested)
        }
    """
    if work_item_type not in VALID_WORK_ITEM_TYPES:
        return Result(
            success=False,
            error=f"Invalid work_item_type '{work_item_type}'. "
                  f"Valid: {sorted(VALID_WORK_ITEM_TYPES)}",
        )

    table = WORK_ITEM_TABLE_MAP[work_item_type]

    try:
        conn = _open_project_connection(project_root)
        try:
            # Step 1: Get the work item
            cursor = conn.execute(
                f"SELECT * FROM {table} WHERE id = ?", (work_item_id,)
            )
            work_item_row = cursor.fetchone()
            if work_item_row is None:
                return Result(
                    success=False,
                    error=f"{work_item_type} with id {work_item_id} not found",
                )
            work_item = row_to_dict(work_item_row)

            # Step 2: Get associated items
            items = _get_items_for_work_item(conn, work_item_type, work_item_id)

            # Step 3: Get flows associated with this work item's items
            flow_ids = _get_flow_ids_from_items(conn, items)
            flows = _get_flows_by_ids(conn, flow_ids)

            # Step 4: Get files from file_flows for those flows
            file_ids = _get_file_ids_from_flows(conn, flow_ids)
            files = _get_files_by_ids(conn, file_ids)

            # Step 5: Get functions for those files
            functions = _get_functions_for_files(conn, file_ids)

            data = {
                'work_item': work_item,
                'items': items,
                'flows': flows,
                'files': files,
                'functions': functions,
            }

            # Step 6 (optional): Interactions
            if include_interactions:
                func_ids = tuple(f.get('id') for f in functions if f.get('id'))
                data['interactions'] = _get_interactions_for_functions(conn, func_ids)

            # Step 7 (optional): Note history
            if include_history:
                data['notes'] = _get_notes_for_work_item(
                    conn, work_item_type, work_item_id
                )

            return Result(
                success=True,
                data=data,
                return_statements=get_return_statements("get_work_context"),
            )

        finally:
            conn.close()

    except FileNotFoundError as e:
        return Result(success=False, error=str(e))
    except Exception as e:
        return Result(success=False, error=f"Failed to get work context: {str(e)}")


def _get_items_for_work_item(
    conn: sqlite3.Connection,
    work_item_type: str,
    work_item_id: int,
) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get items linked to a work item."""
    column_map = {
        'task': 'task_id',
        'subtask': 'subtask_id',
        'sidequest': 'sidequest_id',
    }
    column = column_map.get(work_item_type)
    if column is None:
        return ()

    cursor = conn.execute(
        f"SELECT * FROM items WHERE {column} = ?", (work_item_id,)
    )
    return rows_to_tuple(cursor.fetchall())


def _get_flow_ids_from_items(
    conn: sqlite3.Connection,
    items: Tuple[Dict[str, Any], ...],
) -> Tuple[int, ...]:
    """Pure: Extract unique flow IDs from items (via file_flows)."""
    file_ids = set()
    for item in items:
        fid = item.get('file_id')
        if fid:
            file_ids.add(fid)

    if not file_ids:
        return ()

    placeholders = ','.join('?' for _ in file_ids)
    cursor = conn.execute(
        f"SELECT DISTINCT flow_id FROM file_flows WHERE file_id IN ({placeholders})",
        tuple(file_ids)
    )
    return tuple(row['flow_id'] for row in cursor.fetchall())


def _get_flows_by_ids(
    conn: sqlite3.Connection,
    flow_ids: Tuple[int, ...],
) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get flow records by IDs."""
    if not flow_ids:
        return ()
    placeholders = ','.join('?' for _ in flow_ids)
    cursor = conn.execute(
        f"SELECT * FROM flows WHERE id IN ({placeholders})", flow_ids
    )
    return rows_to_tuple(cursor.fetchall())


def _get_file_ids_from_flows(
    conn: sqlite3.Connection,
    flow_ids: Tuple[int, ...],
) -> Tuple[int, ...]:
    """Effect: Get unique file IDs from file_flows for given flow IDs."""
    if not flow_ids:
        return ()
    placeholders = ','.join('?' for _ in flow_ids)
    cursor = conn.execute(
        f"SELECT DISTINCT file_id FROM file_flows WHERE flow_id IN ({placeholders})",
        flow_ids
    )
    return tuple(row['file_id'] for row in cursor.fetchall())


def _get_files_by_ids(
    conn: sqlite3.Connection,
    file_ids: Tuple[int, ...],
) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get file records by IDs."""
    if not file_ids:
        return ()
    placeholders = ','.join('?' for _ in file_ids)
    cursor = conn.execute(
        f"SELECT * FROM files WHERE id IN ({placeholders})", file_ids
    )
    return rows_to_tuple(cursor.fetchall())


def _get_functions_for_files(
    conn: sqlite3.Connection,
    file_ids: Tuple[int, ...],
) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get all functions for given file IDs."""
    if not file_ids:
        return ()
    placeholders = ','.join('?' for _ in file_ids)
    cursor = conn.execute(
        f"SELECT * FROM functions WHERE file_id IN ({placeholders})", file_ids
    )
    return rows_to_tuple(cursor.fetchall())


def _get_interactions_for_functions(
    conn: sqlite3.Connection,
    function_ids: Tuple[int, ...],
) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get interactions involving any of the given function IDs."""
    if not function_ids:
        return ()
    placeholders = ','.join('?' for _ in function_ids)
    cursor = conn.execute(
        f"SELECT * FROM interactions "
        f"WHERE source_function_id IN ({placeholders}) "
        f"OR target_function_id IN ({placeholders})",
        function_ids + function_ids
    )
    return rows_to_tuple(cursor.fetchall())


def _get_notes_for_work_item(
    conn: sqlite3.Connection,
    work_item_type: str,
    work_item_id: int,
) -> Tuple[Dict[str, Any], ...]:
    """Effect: Get notes referencing a work item."""
    table_map = WORK_ITEM_TABLE_MAP
    ref_table = table_map.get(work_item_type)
    if ref_table is None:
        return ()

    cursor = conn.execute(
        "SELECT * FROM notes WHERE reference_table = ? AND reference_id = ? "
        "ORDER BY created_at DESC",
        (ref_table, work_item_id)
    )
    return rows_to_tuple(cursor.fetchall())

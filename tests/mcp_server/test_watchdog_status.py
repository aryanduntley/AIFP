"""
Tests for _reconcile_watchdog_status (aimfp.helpers.orchestrators.entry_points)

Regression guard for the "confusing watchdog status on new session" bug:
_start_watchdog returns started:true immediately (async Popen), but
_read_reminders checks the PID file before the subprocess has written it and
reports status:'not_running' with a "restart it" notice. Surfacing
started:true alongside status:'not_running' + "restart" is self-contradictory
and made the AI alarm the user or loop calling aimfp_run on every new session.

These tests assert the reconciled output is always exactly one coherent
state and never the contradictory pair — by construction, independent of
subprocess timing.
"""

import pytest

from aimfp.helpers.orchestrators.entry_points import _reconcile_watchdog_status


# Notice _read_reminders actually emits when the PID file is not there yet.
_RESTART_NOTICE = (
    "Watchdog process is not running. File change monitoring is inactive. "
    "Call aimfp_run(is_new_session=true) to restart, or verify the "
    "watchdog module is installed."
)


def test_the_exact_bug_scenario_is_not_contradictory():
    """started:true + read 'not_running'/'restart' must NOT surface as
    started:true/not_running/restart. It is a just-started watchdog."""
    out = _reconcile_watchdog_status(
        {'started': True, 'confirmed': False, 'error': None},
        {'status': 'not_running', 'reminders': (), 'notice': _RESTART_NOTICE},
    )
    assert out['status'] == 'starting'
    assert out['started'] is True
    # never the contradictory pair
    assert not (out['started'] is True and out['status'] == 'not_running')
    # must not instruct the AI to restart
    assert 'restart' not in out['notice'].lower() or 'do not restart' in out['notice'].lower()
    assert 'aimfp_run(is_new_session=true) to restart' not in out['notice']


def test_no_reminders_file_after_start_is_also_starting():
    out = _reconcile_watchdog_status(
        {'started': True, 'confirmed': False, 'error': None},
        {'status': 'no_reminders_file', 'reminders': (), 'notice': 'x'},
    )
    assert out['status'] == 'starting'
    assert 'do not restart' in out['notice'].lower()


def test_healthy_running_watchdog_is_ok():
    out = _reconcile_watchdog_status(
        {'started': True, 'confirmed': True, 'error': None},
        {'status': 'ok', 'reminders': (), 'notice': None},
    )
    assert out['status'] == 'ok'
    assert out['notice'] is None
    assert out['confirmed'] is True


def test_launch_failure_surfaces_real_error():
    err = "Watchdog failed to start: boom. Verify the watchdog module..."
    out = _reconcile_watchdog_status(
        {'started': False, 'confirmed': False, 'error': err},
        {'status': 'not_running', 'reminders': (), 'notice': _RESTART_NOTICE},
    )
    assert out['status'] == 'failed'
    assert out['notice'] == err
    assert out['started'] is False


def test_early_exit_failure_surfaces_real_error():
    err = "Watchdog subprocess exited during initialization (exit code 1) ..."
    out = _reconcile_watchdog_status(
        {'started': False, 'confirmed': False, 'error': err},
        {'status': 'not_running', 'reminders': (), 'notice': _RESTART_NOTICE},
    )
    assert out['status'] == 'failed'
    assert err in out['notice']


def test_reminders_are_preserved_through_reconciliation():
    reminders = ({'type': 'new_file_detected', 'file': 'src/a.py'},)
    out = _reconcile_watchdog_status(
        {'started': True, 'confirmed': False, 'error': None},
        {'status': 'not_running', 'reminders': reminders, 'notice': _RESTART_NOTICE},
    )
    # reconciliation may relabel status but must never drop findings
    assert out['reminders'] == reminders


@pytest.mark.parametrize("start", [
    {'started': True, 'confirmed': True, 'error': None},
    {'started': True, 'confirmed': False, 'error': None},
    {'started': False, 'confirmed': False, 'error': 'boom'},
    {},
])
@pytest.mark.parametrize("read_status", [
    'ok', 'not_running', 'no_reminders_file', 'unknown',
])
def test_contradiction_is_impossible_across_all_combinations(start, read_status):
    """The invariant, exhaustively: the output is never started:true with a
    status that tells the AI the watchdog is down / to restart it."""
    out = _reconcile_watchdog_status(
        start,
        {'status': read_status, 'reminders': (), 'notice': _RESTART_NOTICE},
    )
    assert out['status'] in ('ok', 'starting', 'failed', 'unknown')
    # the contradictory pair must never occur
    assert not (out['started'] is True and out['status'] == 'not_running')
    if out['started'] is True and out['status'] in ('ok', 'starting'):
        notice = (out['notice'] or '').lower()
        assert 'aimfp_run(is_new_session=true) to restart' not in notice

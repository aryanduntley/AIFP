"""
AIMFP Watchdog - Background File System Monitor

Monitors project source files for changes and writes actionable
reminders to a JSON file. AI reads this via aimfp_run to stay
on track during long directive chains.

The watchdog acts as external memory — it never forgets, has no
context window, and catches things AI might miss: unregistered
functions, stale timestamps, files changed without DB updates.
"""

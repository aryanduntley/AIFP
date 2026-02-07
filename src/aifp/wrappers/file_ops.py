"""
AIFP Wrapper - File Operations

FP-compliant wrappers for file I/O operations used by the watchdog.
Isolates file system side effects into clearly marked effect functions.
"""

import json
import os
import tempfile
from typing import Any, Dict, Optional


# ============================================================================
# Effect Functions
# ============================================================================

def _effect_read_json(path: str) -> Optional[Dict[str, Any]]:
    """
    Effect: Read a JSON file and return parsed content.

    Returns None if file doesn't exist or is invalid JSON.
    """
    if not os.path.isfile(path):
        return None
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _effect_write_json_atomic(path: str, data: Dict[str, Any]) -> bool:
    """
    Effect: Write JSON data to file atomically (temp file + rename).

    Ensures the file is always valid JSON, even if process is killed mid-write.
    Returns True on success.
    """
    dir_path = os.path.dirname(path)
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_path, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, path)
            return True
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return False
    except OSError:
        return False


def _effect_read_file(path: str) -> Optional[str]:
    """
    Effect: Read entire file content as string.

    Returns None if file doesn't exist or unreadable.
    """
    try:
        with open(path, 'r') as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def _effect_file_mtime(path: str) -> Optional[float]:
    """
    Effect: Get file modification time as Unix timestamp.

    Returns None if file doesn't exist.
    """
    try:
        return os.path.getmtime(path)
    except OSError:
        return None


def _effect_write_text(path: str, content: str) -> bool:
    """
    Effect: Write text content to file.

    Returns True on success.
    """
    try:
        with open(path, 'w') as f:
            f.write(content)
        return True
    except OSError:
        return False


def _effect_ensure_dir(path: str) -> bool:
    """
    Effect: Create directory and parents if they don't exist.

    Returns True on success or if already exists.
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

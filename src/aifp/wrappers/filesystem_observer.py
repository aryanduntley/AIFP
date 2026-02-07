"""
AIFP Wrapper - File System Observer (watchdog library)

Wraps the OOP-based `watchdog` library into FP-compliant functions.
The watchdog library requires subclassing FileSystemEventHandler —
this wrapper isolates that into a single module and exposes pure
functional interfaces for event processing.

External dependency: watchdog (pip install watchdog)
"""

import time
from dataclasses import dataclass
from typing import Final, Callable, Optional, Tuple, Any

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileSystemEvent,
    FileModifiedEvent,
    FileCreatedEvent,
    FileDeletedEvent,
    FileMovedEvent,
)


# ============================================================================
# Immutable Event Types (FP representation of watchdog events)
# ============================================================================

@dataclass(frozen=True)
class FileEvent:
    """Immutable representation of a file system event."""
    event_type: str  # 'modified', 'created', 'deleted', 'moved'
    src_path: str
    dest_path: Optional[str] = None  # Only for 'moved' events
    is_directory: bool = False
    timestamp: float = 0.0


# Event type constants
EVENT_MODIFIED: Final[str] = "modified"
EVENT_CREATED: Final[str] = "created"
EVENT_DELETED: Final[str] = "deleted"
EVENT_MOVED: Final[str] = "moved"


# ============================================================================
# Pure Functions
# ============================================================================

def watchdog_event_to_file_event(event: FileSystemEvent) -> FileEvent:
    """Pure: Convert a watchdog OOP event to an immutable FileEvent."""
    if isinstance(event, FileMovedEvent):
        return FileEvent(
            event_type=EVENT_MOVED,
            src_path=event.src_path,
            dest_path=event.dest_path,
            is_directory=event.is_directory,
            timestamp=time.time(),
        )

    event_type_map = {
        FileModifiedEvent: EVENT_MODIFIED,
        FileCreatedEvent: EVENT_CREATED,
        FileDeletedEvent: EVENT_DELETED,
    }
    event_type = event_type_map.get(type(event), EVENT_MODIFIED)

    return FileEvent(
        event_type=event_type,
        src_path=event.src_path,
        is_directory=event.is_directory,
        timestamp=time.time(),
    )


def should_process_event(event: FileSystemEvent) -> bool:
    """Pure: Determine if a watchdog event should be processed (files only)."""
    return not event.is_directory


# ============================================================================
# Callback-Based Event Handler (minimal OOP, delegates to callbacks)
# ============================================================================

class _CallbackHandler(FileSystemEventHandler):
    """
    Minimal OOP wrapper required by watchdog library.

    Delegates ALL logic to an external callback function.
    This class contains zero business logic — it only bridges
    watchdog's OOP interface to our FP callback.
    """

    def __init__(self, on_event: Callable[[FileEvent], None]) -> None:
        super().__init__()
        self._on_event = on_event

    def on_modified(self, event: FileSystemEvent) -> None:
        if should_process_event(event):
            self._on_event(watchdog_event_to_file_event(event))

    def on_created(self, event: FileSystemEvent) -> None:
        if should_process_event(event):
            self._on_event(watchdog_event_to_file_event(event))

    def on_deleted(self, event: FileSystemEvent) -> None:
        if should_process_event(event):
            self._on_event(watchdog_event_to_file_event(event))

    def on_moved(self, event: FileSystemEvent) -> None:
        if should_process_event(event):
            self._on_event(watchdog_event_to_file_event(event))


# ============================================================================
# Effect Functions (Side-effecting, clearly marked)
# ============================================================================

def _effect_create_observer(
    watch_path: str,
    on_event: Callable[[FileEvent], None],
    recursive: bool = True,
) -> Observer:
    """
    Effect: Create and start a file system observer.

    Args:
        watch_path: Directory to watch
        on_event: Callback receiving immutable FileEvent for each change
        recursive: Watch subdirectories

    Returns:
        Running Observer instance (must be stopped with _effect_stop_observer)
    """
    handler = _CallbackHandler(on_event)
    observer = Observer()
    observer.schedule(handler, watch_path, recursive=recursive)
    observer.start()
    return observer


def _effect_stop_observer(observer: Observer, timeout: float = 5.0) -> bool:
    """
    Effect: Stop a running observer gracefully.

    Args:
        observer: Running Observer instance
        timeout: Seconds to wait for thread join

    Returns:
        True if stopped successfully
    """
    observer.stop()
    observer.join(timeout=timeout)
    return not observer.is_alive()

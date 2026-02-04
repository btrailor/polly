"""
Notes File Watcher
Monitors notes directory for changes and automatically updates indices and RAG.
"""

from pathlib import Path
from typing import Optional, Callable, Dict, Any
from datetime import datetime
import logging
import time
from threading import Timer

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class NotesFileWatcher:
    """
    File watcher for notes directory.
    
    Monitors for file changes and triggers:
    - RAG re-indexing
    - Notes index updates
    - Backlinks index updates
    - Tags index updates
    """
    
    DEBOUNCE_SECONDS = 2.0  # Wait 2 seconds after last change
    
    def __init__(
        self,
        notes_path: Path,
        on_file_added: Optional[Callable[[Path], None]] = None,
        on_file_modified: Optional[Callable[[Path], None]] = None,
        on_file_deleted: Optional[Callable[[Path], None]] = None,
        on_sync_status: Optional[Callable[[str, Dict[str, Any]], None]] = None
    ):
        """
        Initialize file watcher.
        
        Args:
            notes_path: Path to notes directory to watch
            on_file_added: Callback for new files
            on_file_modified: Callback for modified files
            on_file_deleted: Callback for deleted files
            on_sync_status: Callback for sync status updates (status, data)
        """
        self.notes_path = Path(notes_path).resolve()
        self.on_file_added = on_file_added
        self.on_file_modified = on_file_modified
        self.on_file_deleted = on_file_deleted
        self.on_sync_status = on_sync_status
        
        self.observer: Optional[Observer] = None
        self._is_running = False
        
        # Debouncing: map of filepath -> Timer
        self._pending_changes: Dict[str, Timer] = {}
        
        # Statistics
        self.stats = {
            "started_at": None,
            "files_added": 0,
            "files_modified": 0,
            "files_deleted": 0,
            "last_event": None,
            "errors": []
        }
    
    def start(self):
        """Start watching the notes directory."""
        print(f"=== FILE WATCHER START CALLED === (path: {self.notes_path})", flush=True)
        if self._is_running:
            print("File watcher already running!", flush=True)
            logger.warning("File watcher already running")
            return
        
        if not self.notes_path.exists():
            print(f"Notes path does not exist: {self.notes_path}", flush=True)
            raise FileNotFoundError(f"Notes path does not exist: {self.notes_path}")
        
        print(f"Starting observer for: {self.notes_path}", flush=True)
        logger.info(f"Starting file watcher for: {self.notes_path}")
        
        # Create event handler
        event_handler = NotesEventHandler(self)
        
        # Create and start observer
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.notes_path), recursive=True)
        self.observer.start()
        
        self._is_running = True
        self.stats["started_at"] = datetime.now().isoformat()
        
        print(f"File watcher started! is_running={self._is_running}", flush=True)
        self._notify_status("started", {"path": str(self.notes_path)})
        logger.info("File watcher started")
    
    def stop(self):
        """Stop watching the notes directory."""
        if not self._is_running:
            return
        
        logger.info("Stopping file watcher")
        
        # Cancel all pending timers
        for timer in self._pending_changes.values():
            timer.cancel()
        self._pending_changes.clear()
        
        # Stop observer
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
        
        self._is_running = False
        self._notify_status("stopped", {})
        logger.info("File watcher stopped")
    
    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._is_running
    
    def _should_process_file(self, path: Path) -> bool:
        """
        Check if a file should be processed.
        
        Args:
            path: File path to check
            
        Returns:
            True if file should be processed
        """
        print(f"[FILE WATCHER] _should_process_file checking: {path}", flush=True)
        
        # Only process markdown files
        if path.suffix.lower() != '.md':
            print(f"[FILE WATCHER] Not a markdown file: {path.suffix}", flush=True)
            return False
        
        # Ignore hidden files and directories - CHECK RELATIVE PATH ONLY
        try:
            relative = path.relative_to(self.notes_path)
            print(f"[FILE WATCHER] Relative path: {relative}", flush=True)
            print(f"[FILE WATCHER] Relative parts: {relative.parts}", flush=True)
            
            # Check if any part of the relative path starts with . or _
            for part in relative.parts:
                if part.startswith('.') or part.startswith('_'):
                    print(f"[FILE WATCHER] Filtered: part '{part}' starts with . or _", flush=True)
                    return False
            
            print(f"[FILE WATCHER] File passes all filters!", flush=True)
            return True
            
        except ValueError as e:
            # Path is not relative to notes_path
            print(f"[FILE WATCHER] Path not relative to notes_path: {e}", flush=True)
            return False
    
    def _handle_file_added(self, path: Path):
        """
        Handle file added event (debounced).
        
        Args:
            path: Path to added file
        """
        print(f"[FILE WATCHER] _handle_file_added called for: {path}", flush=True)
        try:
            logger.info(f"File added: {path.name}")
            
            self.stats["files_added"] += 1
            self.stats["last_event"] = datetime.now().isoformat()
            
            # Notify status
            self._notify_status("indexing", {
                "action": "added",
                "file": path.name,
                "path": str(path)
            })
            
            # Call callback
            if self.on_file_added:
                print(f"[FILE WATCHER] Calling on_file_added callback", flush=True)
                self.on_file_added(path)
            else:
                print(f"[FILE WATCHER] No on_file_added callback registered!", flush=True)
            
            # Notify complete
            self._notify_status("indexed", {
                "action": "added",
                "file": path.name
            })
            
        except Exception as e:
            error_msg = f"Error handling added file {path}: {str(e)}"
            logger.error(error_msg)
            print(f"[FILE WATCHER] ERROR: {error_msg}", flush=True)
            self.stats["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
            
            self._notify_status("error", {
                "action": "added",
                "file": path.name,
                "error": str(e)
            })
    
    def _handle_file_modified(self, path: Path):
        """
        Handle file modified event (debounced).
        
        Args:
            path: Path to modified file
        """
        try:
            logger.info(f"File modified: {path.name}")
            
            self.stats["files_modified"] += 1
            self.stats["last_event"] = datetime.now().isoformat()
            
            # Notify status
            self._notify_status("indexing", {
                "action": "modified",
                "file": path.name,
                "path": str(path)
            })
            
            # Call callback
            if self.on_file_modified:
                self.on_file_modified(path)
            
            # Notify complete
            self._notify_status("indexed", {
                "action": "modified",
                "file": path.name
            })
            
        except Exception as e:
            error_msg = f"Error handling modified file {path}: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
            
            self._notify_status("error", {
                "action": "modified",
                "file": path.name,
                "error": str(e)
            })
    
    def _handle_file_deleted(self, path: Path):
        """
        Handle file deleted event (debounced).
        
        Args:
            path: Path to deleted file
        """
        try:
            logger.info(f"File deleted: {path.name}")
            
            self.stats["files_deleted"] += 1
            self.stats["last_event"] = datetime.now().isoformat()
            
            # Notify status
            self._notify_status("indexing", {
                "action": "deleted",
                "file": path.name,
                "path": str(path)
            })
            
            # Call callback
            if self.on_file_deleted:
                self.on_file_deleted(path)
            
            # Notify complete
            self._notify_status("indexed", {
                "action": "deleted",
                "file": path.name
            })
            
        except Exception as e:
            error_msg = f"Error handling deleted file {path}: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
            
            self._notify_status("error", {
                "action": "deleted",
                "file": path.name,
                "error": str(e)
            })
    
    def _schedule_event(self, event_type: str, path: Path):
        """
        Schedule an event with debouncing.
        
        Args:
            event_type: Type of event ('added', 'modified', 'deleted')
            path: Path to file
        """
        print(f"[FILE WATCHER] _schedule_event: type={event_type}, path={path}", flush=True)
        
        # Cancel existing timer for this file
        key = f"{event_type}:{path}"
        if key in self._pending_changes:
            print(f"[FILE WATCHER] Canceling existing timer for: {key}", flush=True)
            self._pending_changes[key].cancel()
        
        # Create new timer
        handler_map = {
            'added': self._handle_file_added,
            'modified': self._handle_file_modified,
            'deleted': self._handle_file_deleted
        }
        
        handler = handler_map.get(event_type)
        if not handler:
            logger.error(f"Unknown event type: {event_type}")
            print(f"[FILE WATCHER] ERROR: Unknown event type: {event_type}", flush=True)
            return
        
        print(f"[FILE WATCHER] Creating timer: {self.DEBOUNCE_SECONDS}s delay for {key}", flush=True)
        timer = Timer(self.DEBOUNCE_SECONDS, handler, args=[path])
        self._pending_changes[key] = timer
        timer.start()
        print(f"[FILE WATCHER] Timer started for: {key}", flush=True)
    
    def _notify_status(self, status: str, data: Dict[str, Any]):
        """
        Notify sync status callback.
        
        Args:
            status: Status type ('started', 'stopped', 'indexing', 'indexed', 'error')
            data: Additional data
        """
        if self.on_sync_status:
            try:
                self.on_sync_status(status, data)
            except Exception as e:
                logger.error(f"Error in sync status callback: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get watcher statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            **self.stats,
            "is_running": self._is_running,
            "pending_changes": len(self._pending_changes),
            "watched_path": str(self.notes_path)
        }


class NotesEventHandler(FileSystemEventHandler):
    """Event handler for file system events."""
    
    def __init__(self, watcher: NotesFileWatcher):
        """
        Initialize event handler.
        
        Args:
            watcher: Parent NotesFileWatcher instance
        """
        super().__init__()
        self.watcher = watcher
    
    def on_created(self, event: FileSystemEvent):
        """Handle file/directory created event."""
        print(f"[FILE WATCHER] on_created triggered: {event.src_path} (is_dir={event.is_directory})", flush=True)
        logger.info(f"Event received: created {event.src_path}")
        
        if event.is_directory:
            print(f"[FILE WATCHER] Skipping directory: {event.src_path}", flush=True)
            return
        
        path = Path(event.src_path)
        should_process = self.watcher._should_process_file(path)
        print(f"[FILE WATCHER] Should process {path.name}? {should_process}", flush=True)
        
        if should_process:
            print(f"[FILE WATCHER] Scheduling 'added' event for: {path}", flush=True)
            self.watcher._schedule_event('added', path)
        else:
            print(f"[FILE WATCHER] Filtered out: {path}", flush=True)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file/directory modified event."""
        print(f"[FILE WATCHER] on_modified triggered: {event.src_path} (is_dir={event.is_directory})", flush=True)
        logger.info(f"Event received: modified {event.src_path}")
        
        if event.is_directory:
            print(f"[FILE WATCHER] Skipping directory: {event.src_path}", flush=True)
            return
        
        path = Path(event.src_path)
        should_process = self.watcher._should_process_file(path)
        print(f"[FILE WATCHER] Should process {path.name}? {should_process}", flush=True)
        
        if should_process:
            print(f"[FILE WATCHER] Scheduling 'modified' event for: {path}", flush=True)
            self.watcher._schedule_event('modified', path)
        else:
            print(f"[FILE WATCHER] Filtered out: {path}", flush=True)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file/directory deleted event."""
        print(f"[FILE WATCHER] on_deleted triggered: {event.src_path} (is_dir={event.is_directory})", flush=True)
        logger.info(f"Event received: deleted {event.src_path}")
        
        if event.is_directory:
            print(f"[FILE WATCHER] Skipping directory: {event.src_path}", flush=True)
            return
        
        path = Path(event.src_path)
        # For deleted files, we can't check if they should be processed
        # So we check the extension only
        is_markdown = path.suffix.lower() == '.md'
        print(f"[FILE WATCHER] Is markdown? {is_markdown} (suffix={path.suffix})", flush=True)
        
        if is_markdown:
            print(f"[FILE WATCHER] Scheduling 'deleted' event for: {path}", flush=True)
            self.watcher._schedule_event('deleted', path)
        else:
            print(f"[FILE WATCHER] Filtered out: {path}", flush=True)


# Global singleton instance
_global_watcher: Optional[NotesFileWatcher] = None


def get_file_watcher() -> Optional[NotesFileWatcher]:
    """
    Get the global file watcher instance.
    
    Returns:
        Global NotesFileWatcher singleton, or None if not initialized
    """
    return _global_watcher


def start_file_watcher(
    notes_path: Path,
    on_file_added: Optional[Callable[[Path], None]] = None,
    on_file_modified: Optional[Callable[[Path], None]] = None,
    on_file_deleted: Optional[Callable[[Path], None]] = None,
    on_sync_status: Optional[Callable[[str, Dict[str, Any]], None]] = None
) -> NotesFileWatcher:
    """
    Start the global file watcher.
    
    Args:
        notes_path: Path to notes directory
        on_file_added: Callback for new files
        on_file_modified: Callback for modified files
        on_file_deleted: Callback for deleted files
        on_sync_status: Callback for sync status updates
        
    Returns:
        Global NotesFileWatcher instance
    """
    global _global_watcher
    
    # Stop existing watcher if running
    if _global_watcher and _global_watcher.is_running():
        _global_watcher.stop()
    
    # Create and start new watcher
    _global_watcher = NotesFileWatcher(
        notes_path,
        on_file_added,
        on_file_modified,
        on_file_deleted,
        on_sync_status
    )
    _global_watcher.start()
    
    return _global_watcher


def stop_file_watcher():
    """Stop the global file watcher."""
    global _global_watcher
    
    if _global_watcher:
        _global_watcher.stop()
        _global_watcher = None

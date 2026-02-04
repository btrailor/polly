"""
Notes Sync Manager
Coordinates file watcher, indices, and RAG synchronization.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import logging

from .notes_file_watcher import start_file_watcher, stop_file_watcher, get_file_watcher
from .notes_index import get_notes_index
from .backlinks import get_backlinks_index
from .tags_index import get_tags_index
from .rag import UnifiedRAG

logger = logging.getLogger(__name__)


class NotesSyncManager:
    """
    Coordinates automatic synchronization of notes.
    
    When files change:
    1. Updates notes index
    2. Updates backlinks index
    3. Updates tags index
    4. Re-indexes in RAG
    """
    
    def __init__(self, notes_path: Path, rag: UnifiedRAG):
        """
        Initialize sync manager.
        
        Args:
            notes_path: Path to notes directory
            rag: RAG instance for indexing
        """
        self.notes_path = Path(notes_path).resolve()
        self.rag = rag
        
        # Get index instances
        self.notes_index = get_notes_index()
        self.backlinks_index = get_backlinks_index(self.notes_index)
        self.tags_index = get_tags_index(self.notes_index)
        
        # Sync statistics
        self.stats = {
            "files_synced": 0,
            "last_sync": None,
            "errors": []
        }
    
    def start(self, initial_build: bool = True):
        """
        Start automatic synchronization.
        
        Args:
            initial_build: Whether to build indices initially
        """
        logger.info(f"Starting notes sync manager for: {self.notes_path}")
        
        # Build initial indices if requested
        if initial_build:
            logger.info("Building initial indices...")
            self._build_all_indices()
        
        # Start file watcher with callbacks
        start_file_watcher(
            notes_path=self.notes_path,
            on_file_added=self._on_file_added,
            on_file_modified=self._on_file_modified,
            on_file_deleted=self._on_file_deleted,
            on_sync_status=self._on_sync_status
        )
        
        logger.info("Notes sync manager started")
    
    def stop(self):
        """Stop automatic synchronization."""
        logger.info("Stopping notes sync manager")
        stop_file_watcher()
        logger.info("Notes sync manager stopped")
    
    def is_running(self) -> bool:
        """Check if sync manager is running."""
        watcher = get_file_watcher()
        return watcher is not None and watcher.is_running()
    
    def _build_all_indices(self):
        """Build all indices from scratch."""
        try:
            # Build notes index
            logger.info("Building notes index...")
            notes_stats = self.notes_index.build_index(self.notes_path)
            logger.info(f"Notes index built: {notes_stats['notes_indexed']} notes")
            
            # Build backlinks index
            logger.info("Building backlinks index...")
            backlinks_stats = self.backlinks_index.build_backlinks(self.notes_path)
            logger.info(f"Backlinks index built: {backlinks_stats['backlinks_found']} links")
            
            # Build tags index
            logger.info("Building tags index...")
            tags_stats = self.tags_index.build_tags_index(self.notes_path)
            logger.info(f"Tags index built: {tags_stats['unique_tags']} unique tags")
            
            # Check if RAG already has notes indexed to avoid slow startup
            try:
                notes_collection = self.rag.collections.get('notes')
                if notes_collection:
                    existing_count = notes_collection.count()
                    if existing_count > 0:
                        logger.info(f"RAG already has {existing_count} documents indexed, skipping initial index")
                        return
            except Exception as e:
                logger.debug(f"Could not check RAG collection count: {e}")
            
            # Index in RAG only if not already indexed
            logger.info("Indexing notes in RAG...")
            indexed_count = self.rag.index_obsidian_vault(self.notes_path, force=False)
            logger.info(f"RAG indexed: {indexed_count} files")
            
        except Exception as e:
            logger.error(f"Error building indices: {e}")
            raise
    
    def _on_file_added(self, path: Path):
        """
        Handle file added event.
        
        Args:
            path: Path to added file
        """
        try:
            logger.info(f"Syncing added file: {path.name}")
            
            # Update notes index
            self.notes_index.update_note(path, self.notes_path)
            
            # Update backlinks (this note may link to others)
            self.backlinks_index.update_note_backlinks(path)
            
            # Update tags
            self.tags_index.update_note_tags(path)
            
            # Index in RAG
            self._index_file_in_rag(path)
            
            self.stats["files_synced"] += 1
            logger.info(f"File added and synced: {path.name}")
            
        except Exception as e:
            error_msg = f"Error syncing added file {path.name}: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
    
    def _on_file_modified(self, path: Path):
        """
        Handle file modified event.
        
        Args:
            path: Path to modified file
        """
        try:
            logger.info(f"Syncing modified file: {path.name}")
            
            # Update notes index
            self.notes_index.update_note(path, self.notes_path)
            
            # Update backlinks (links in this note may have changed)
            self.backlinks_index.update_note_backlinks(path)
            
            # Update tags (tags may have changed)
            self.tags_index.update_note_tags(path)
            
            # Re-index in RAG
            self._index_file_in_rag(path, force=True)
            
            self.stats["files_synced"] += 1
            logger.info(f"File modified and synced: {path.name}")
            
        except Exception as e:
            error_msg = f"Error syncing modified file {path.name}: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
    
    def _on_file_deleted(self, path: Path):
        """
        Handle file deleted event.
        
        Args:
            path: Path to deleted file
        """
        try:
            logger.info(f"Syncing deleted file: {path.name}")
            
            # Remove from notes index
            self.notes_index.remove_note(path)
            
            # Remove backlinks
            self.backlinks_index.remove_note_backlinks(path)
            
            # Remove tags
            self.tags_index.remove_note_tags(path)
            
            # Remove from RAG
            self._remove_file_from_rag(path)
            
            self.stats["files_synced"] += 1
            logger.info(f"File deleted and synced: {path.name}")
            
        except Exception as e:
            error_msg = f"Error syncing deleted file {path.name}: {str(e)}"
            logger.error(error_msg)
            self.stats["errors"].append(error_msg)
    
    def _on_sync_status(self, status: str, data: Dict[str, Any]):
        """
        Handle sync status updates from file watcher.
        
        Args:
            status: Status type
            data: Status data
        """
        # Log status changes
        if status == "started":
            logger.info(f"File watcher started for: {data.get('path')}")
        elif status == "stopped":
            logger.info("File watcher stopped")
        elif status == "error":
            logger.error(f"File watcher error: {data.get('error')}")
    
    def _index_file_in_rag(self, path: Path, force: bool = False):
        """
        Index a single file in RAG.
        
        Args:
            path: Path to file
            force: Force re-indexing even if up to date
        """
        try:
            # Use the internal _index_markdown_file method
            indexed = self.rag._index_markdown_file(path, self.notes_path, force=force)
            
            if indexed:
                logger.debug(f"Indexed in RAG: {path.name}")
            else:
                logger.debug(f"Skipped RAG indexing (up to date): {path.name}")
                
        except Exception as e:
            logger.error(f"Error indexing {path.name} in RAG: {e}")
            raise
    
    def _remove_file_from_rag(self, path: Path):
        """
        Remove a file from RAG.
        
        Args:
            path: Path to file
        """
        try:
            # Calculate relative path
            rel_path = str(path.relative_to(self.notes_path))
            
            # Delete from notes collection
            try:
                self.rag.collections['notes'].delete(where={"filepath": rel_path})
                logger.debug(f"Removed from RAG: {path.name}")
            except Exception as e:
                # It's okay if the file wasn't in RAG
                logger.debug(f"File not in RAG (or error removing): {path.name} - {e}")
            
            # Remove from metadata cache
            if rel_path in self.rag.metadata_cache:
                del self.rag.metadata_cache[rel_path]
                
        except Exception as e:
            logger.error(f"Error removing {path.name} from RAG: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get sync statistics.
        
        Returns:
            Dictionary with statistics
        """
        watcher = get_file_watcher()
        watcher_stats = watcher.get_stats() if watcher else {}
        
        return {
            "sync_manager": {
                "files_synced": self.stats["files_synced"],
                "errors": self.stats["errors"]
            },
            "file_watcher": watcher_stats,
            "notes_index": self.notes_index.get_stats(),
            "backlinks_index": self.backlinks_index.get_stats(),
            "tags_index": self.tags_index.get_stats()
        }


# Global singleton instance
_global_sync_manager: Optional[NotesSyncManager] = None


def get_sync_manager() -> Optional[NotesSyncManager]:
    """
    Get the global sync manager instance.
    
    Returns:
        Global NotesSyncManager singleton, or None if not initialized
    """
    return _global_sync_manager


def start_sync_manager(notes_path: Path, rag: UnifiedRAG, initial_build: bool = True) -> NotesSyncManager:
    """
    Start the global sync manager.
    
    Args:
        notes_path: Path to notes directory
        rag: RAG instance
        initial_build: Whether to build indices initially
        
    Returns:
        Global NotesSyncManager instance
    """
    global _global_sync_manager
    
    # Stop existing sync manager if running
    if _global_sync_manager and _global_sync_manager.is_running():
        _global_sync_manager.stop()
    
    # Create and start new sync manager
    _global_sync_manager = NotesSyncManager(notes_path, rag)
    _global_sync_manager.start(initial_build)
    
    return _global_sync_manager


def stop_sync_manager():
    """Stop the global sync manager."""
    global _global_sync_manager
    
    if _global_sync_manager:
        _global_sync_manager.stop()
        _global_sync_manager = None

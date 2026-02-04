"""
Obsidian to Native Polly Notes Migration System
Handles copying vault files to native notes directory with progress tracking.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class MigrationProgress:
    """Track migration progress"""
    
    def __init__(self, migration_id: str, total_files: int):
        self.migration_id = migration_id
        self.total_files = total_files
        self.files_copied = 0
        self.files_skipped = 0
        self.current_file = None
        self.errors: List[Dict[str, str]] = []
        self.started_at = datetime.now()
        self.completed_at = None
        self.status = "in_progress"  # in_progress, completed, failed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        elapsed = (datetime.now() - self.started_at).total_seconds()
        
        return {
            "migration_id": self.migration_id,
            "status": self.status,
            "total_files": self.total_files,
            "files_copied": self.files_copied,
            "files_skipped": self.files_skipped,
            "current_file": self.current_file,
            "errors": self.errors,
            "progress_percent": int((self.files_copied / self.total_files * 100)) if self.total_files > 0 else 0,
            "elapsed_seconds": int(elapsed),
            "estimated_remaining": self._estimate_remaining(elapsed),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def _estimate_remaining(self, elapsed: float) -> Optional[int]:
        """Estimate remaining time in seconds"""
        if self.files_copied == 0:
            return None
        
        rate = elapsed / self.files_copied
        remaining_files = self.total_files - self.files_copied
        return int(rate * remaining_files)


class NotesMigrator:
    """Migrate Obsidian vault to native Polly notes"""
    
    # Files/folders to skip during migration
    SKIP_PATTERNS = [
        '.obsidian',  # Obsidian config folder
        '.trash',     # Trash folder
        '.DS_Store',  # macOS metadata
        '__pycache__', # Python cache
        '.git',       # Git folder
        'node_modules' # Node modules
    ]
    
    # File extensions to copy
    ALLOWED_EXTENSIONS = [
        '.md',   # Markdown notes
        '.png',  # Images
        '.jpg',
        '.jpeg',
        '.gif',
        '.svg',
        '.pdf',  # Documents
        '.txt',  # Text files
    ]
    
    def __init__(self):
        self.active_migrations: Dict[str, MigrationProgress] = {}
    
    def start_migration(
        self,
        vault_path: str,
        target_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start migration process
        
        Args:
            vault_path: Path to Obsidian vault
            target_path: Path to native notes directory
            options: Migration options:
                - copy_attachments: bool (default True)
                - preserve_structure: bool (default True)
                - skip_canvas: bool (default True)
        
        Returns:
            migration_id: Unique ID for tracking progress
        """
        vault_path = Path(vault_path).expanduser()
        target_path = Path(target_path).expanduser()
        
        # Validate paths
        if not vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")
        
        # Create target directory if needed
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Count files to migrate
        total_files = self._count_files(vault_path, options or {})
        
        # Create migration progress tracker
        migration_id = str(uuid.uuid4())
        progress = MigrationProgress(migration_id, total_files)
        self.active_migrations[migration_id] = progress
        
        logger.info(f"Starting migration {migration_id}: {vault_path} -> {target_path} ({total_files} files)")
        
        return migration_id
    
    def execute_migration(
        self,
        migration_id: str,
        vault_path: str,
        target_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute the migration (should be run in background)
        
        Returns:
            Final migration status
        """
        if migration_id not in self.active_migrations:
            raise ValueError(f"Migration not found: {migration_id}")
        
        progress = self.active_migrations[migration_id]
        vault_path = Path(vault_path).expanduser()
        target_path = Path(target_path).expanduser()
        options = options or {}
        
        try:
            # Copy files with progress tracking
            self._copy_files(vault_path, target_path, progress, options)
            
            # Mark as completed
            progress.status = "completed"
            progress.completed_at = datetime.now()
            
            logger.info(f"Migration {migration_id} completed: {progress.files_copied} files copied, {progress.files_skipped} skipped")
            
            return progress.to_dict()
            
        except Exception as e:
            logger.error(f"Migration {migration_id} failed: {e}")
            progress.status = "failed"
            progress.errors.append({
                "file": progress.current_file or "unknown",
                "error": str(e)
            })
            return progress.to_dict()
    
    def get_progress(self, migration_id: str) -> Dict[str, Any]:
        """Get current migration progress"""
        if migration_id not in self.active_migrations:
            raise ValueError(f"Migration not found: {migration_id}")
        
        return self.active_migrations[migration_id].to_dict()
    
    def _count_files(self, vault_path: Path, options: Dict[str, Any]) -> int:
        """Count files to be migrated"""
        count = 0
        
        for root, dirs, files in os.walk(vault_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_skip(d)]
            
            for file in files:
                if self._should_copy_file(file, options):
                    count += 1
        
        return count
    
    def _copy_files(
        self,
        vault_path: Path,
        target_path: Path,
        progress: MigrationProgress,
        options: Dict[str, Any]
    ):
        """Copy files from vault to target with progress tracking"""
        
        for root, dirs, files in os.walk(vault_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not self._should_skip(d)]
            
            # Calculate relative path for structure preservation
            rel_root = Path(root).relative_to(vault_path)
            target_dir = target_path / rel_root
            
            # Create target directory
            if options.get('preserve_structure', True):
                target_dir.mkdir(parents=True, exist_ok=True)
            else:
                target_dir = target_path
            
            # Copy files
            for file in files:
                if self._should_copy_file(file, options):
                    src_file = Path(root) / file
                    
                    # Update progress
                    progress.current_file = str(src_file.relative_to(vault_path))
                    
                    try:
                        # Determine target location
                        if options.get('preserve_structure', True):
                            dst_file = target_dir / file
                        else:
                            # Flatten structure
                            dst_file = target_path / file
                        
                        # Copy file
                        shutil.copy2(src_file, dst_file)
                        progress.files_copied += 1
                        
                        logger.debug(f"Copied: {src_file} -> {dst_file}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to copy {src_file}: {e}")
                        progress.errors.append({
                            "file": str(src_file.relative_to(vault_path)),
                            "error": str(e)
                        })
                        progress.files_skipped += 1
    
    def _should_skip(self, dirname: str) -> bool:
        """Check if directory should be skipped"""
        return any(pattern in dirname for pattern in self.SKIP_PATTERNS)
    
    def _should_copy_file(self, filename: str, options: Dict[str, Any]) -> bool:
        """Check if file should be copied"""
        # Skip system files
        if filename.startswith('.'):
            return False
        
        # Skip Canvas files if option set
        if options.get('skip_canvas', True) and filename.endswith('.canvas'):
            return False
        
        # Check extension
        ext = Path(filename).suffix.lower()
        
        # Always copy markdown files
        if ext == '.md':
            return True
        
        # Copy attachments if option set
        if options.get('copy_attachments', True):
            return ext in self.ALLOWED_EXTENSIONS
        
        return False


# Global migrator instance
_migrator = None

def get_migrator() -> NotesMigrator:
    """Get global migrator instance"""
    global _migrator
    if _migrator is None:
        _migrator = NotesMigrator()
    return _migrator

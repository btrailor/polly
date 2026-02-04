"""
Knowledge Base Migration Utility
Handles migrating the knowledge base from one location to another with validation.
"""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Raised when migration fails."""
    pass


class KnowledgeBaseMigrator:
    """Handles migration of the knowledge base directory."""
    
    def __init__(self, source_path: Path, target_path: Path):
        """
        Initialize migrator.
        
        Args:
            source_path: Current knowledge base location
            target_path: New knowledge base location
        """
        self.source_path = Path(source_path).expanduser().resolve()
        self.target_path = Path(target_path).expanduser().resolve()
        self.backup_path: Optional[Path] = None
        
    def validate_source(self) -> Tuple[bool, str]:
        """
        Validate that source directory exists and contains expected structure.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.source_path.exists():
            return False, f"Source path does not exist: {self.source_path}"
        
        if not self.source_path.is_dir():
            return False, f"Source path is not a directory: {self.source_path}"
        
        # Check for notes directory
        notes_dir = self.source_path / "notes"
        if not notes_dir.exists():
            return False, f"Notes directory not found: {notes_dir}"
        
        return True, ""
    
    def validate_target(self) -> Tuple[bool, str]:
        """
        Validate that target directory is suitable for migration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if source and target are the same
        if self.source_path == self.target_path:
            return False, "Source and target paths are the same"
        
        # Check if target is a subdirectory of source or vice versa
        try:
            self.target_path.relative_to(self.source_path)
            return False, "Target cannot be a subdirectory of source"
        except ValueError:
            pass
        
        try:
            self.source_path.relative_to(self.target_path)
            return False, "Source cannot be a subdirectory of target"
        except ValueError:
            pass
        
        # Check if target exists and is not empty
        if self.target_path.exists():
            if not self.target_path.is_dir():
                return False, f"Target path exists but is not a directory: {self.target_path}"
            
            # Check if target has any Polly content
            if (self.target_path / "notes").exists():
                return False, "Target directory already contains a 'notes' folder"
        
        # Check if we can create the target directory
        if not self.target_path.exists():
            try:
                self.target_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                return False, f"Cannot create target directory: {e}"
        
        # Check write permissions
        if not self.target_path.exists() or not self.target_path.is_dir():
            return False, f"Target directory is not accessible: {self.target_path}"
        
        # Try to create a test file to verify write permissions
        test_file = self.target_path / ".polly_migration_test"
        try:
            test_file.touch()
            test_file.unlink()
        except (PermissionError, OSError) as e:
            return False, f"Target directory is not writable: {e}"
        
        return True, ""
    
    def get_migration_stats(self) -> Dict[str, any]:
        """
        Get statistics about what will be migrated.
        
        Returns:
            Dict with file counts and sizes
        """
        stats = {
            "notes": {"count": 0, "size_bytes": 0},
            "conversations": {"count": 0, "size_bytes": 0},
            "attachments": {"count": 0, "size_bytes": 0},
            "other": {"count": 0, "size_bytes": 0},
            "total_size_bytes": 0,
            "total_files": 0
        }
        
        if not self.source_path.exists():
            return stats
        
        for item in self.source_path.rglob("*"):
            if item.is_file():
                size = item.stat().st_size
                stats["total_files"] += 1
                stats["total_size_bytes"] += size
                
                # Categorize by directory
                try:
                    rel_path = item.relative_to(self.source_path)
                    first_dir = rel_path.parts[0] if rel_path.parts else None
                    
                    if first_dir == "notes":
                        stats["notes"]["count"] += 1
                        stats["notes"]["size_bytes"] += size
                    elif first_dir == "conversations":
                        stats["conversations"]["count"] += 1
                        stats["conversations"]["size_bytes"] += size
                    elif first_dir == "attachments":
                        stats["attachments"]["count"] += 1
                        stats["attachments"]["size_bytes"] += size
                    else:
                        stats["other"]["count"] += 1
                        stats["other"]["size_bytes"] += size
                except ValueError:
                    pass
        
        return stats
    
    def create_backup(self) -> Path:
        """
        Create a backup of the source directory.
        
        Returns:
            Path to backup directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self.source_path.name}_backup_{timestamp}"
        self.backup_path = self.source_path.parent / backup_name
        
        logger.info(f"Creating backup at: {self.backup_path}")
        shutil.copytree(self.source_path, self.backup_path)
        
        return self.backup_path
    
    def migrate(self, create_backup: bool = True) -> Dict[str, any]:
        """
        Perform the migration.
        
        Args:
            create_backup: Whether to create a backup before migrating
            
        Returns:
            Dict with migration results
            
        Raises:
            MigrationError: If migration fails
        """
        # Validate source
        valid, error = self.validate_source()
        if not valid:
            raise MigrationError(f"Source validation failed: {error}")
        
        # Validate target
        valid, error = self.validate_target()
        if not valid:
            raise MigrationError(f"Target validation failed: {error}")
        
        # Get stats before migration
        stats = self.get_migration_stats()
        
        # Create backup if requested
        backup_path = None
        if create_backup:
            try:
                backup_path = self.create_backup()
            except Exception as e:
                raise MigrationError(f"Failed to create backup: {e}")
        
        # Perform migration
        try:
            logger.info(f"Migrating from {self.source_path} to {self.target_path}")
            
            # Copy all contents
            for item in self.source_path.iterdir():
                source_item = self.source_path / item.name
                target_item = self.target_path / item.name
                
                if source_item.is_dir():
                    shutil.copytree(source_item, target_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_item, target_item)
            
            # Verify migration
            target_stats = self._get_target_stats()
            if target_stats["total_files"] != stats["total_files"]:
                raise MigrationError(
                    f"File count mismatch: source had {stats['total_files']} files, "
                    f"target has {target_stats['total_files']} files"
                )
            
            logger.info("Migration completed successfully")
            
            return {
                "success": True,
                "source_path": str(self.source_path),
                "target_path": str(self.target_path),
                "backup_path": str(backup_path) if backup_path else None,
                "stats": stats,
                "files_migrated": stats["total_files"],
                "bytes_migrated": stats["total_size_bytes"]
            }
            
        except Exception as e:
            # If migration fails and we have a backup, suggest restoration
            error_msg = f"Migration failed: {e}"
            if backup_path:
                error_msg += f"\n\nBackup available at: {backup_path}"
            raise MigrationError(error_msg)
    
    def _get_target_stats(self) -> Dict[str, int]:
        """Get statistics about the target directory."""
        stats = {"total_files": 0, "total_size_bytes": 0}
        
        if not self.target_path.exists():
            return stats
        
        for item in self.target_path.rglob("*"):
            if item.is_file():
                stats["total_files"] += 1
                stats["total_size_bytes"] += item.stat().st_size
        
        return stats
    
    def cleanup_source(self) -> None:
        """
        Remove the source directory after successful migration.
        
        WARNING: Only call this after verifying migration was successful!
        """
        if self.source_path.exists():
            logger.info(f"Removing source directory: {self.source_path}")
            shutil.rmtree(self.source_path)


def migrate_knowledge_base(source: str | Path, target: str | Path, 
                           create_backup: bool = True) -> Dict[str, any]:
    """
    Convenience function to migrate knowledge base.
    
    Args:
        source: Current knowledge base path
        target: New knowledge base path
        create_backup: Whether to create a backup
        
    Returns:
        Dict with migration results
        
    Raises:
        MigrationError: If migration fails
    """
    migrator = KnowledgeBaseMigrator(source, target)
    return migrator.migrate(create_backup=create_backup)

"""
macOS File System Operations Integration
Allows Polly to organize files, create folders, manage tags, etc.
"""

import os
import shutil
import subprocess
import logging
import plistlib
import xattr
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class FileSystemIntegration(Integration):
    """
    macOS file system operations for intelligent file organization.
    
    Features:
    - Create/move/rename files and folders
    - macOS tags (color + custom labels)
    - Batch operations
    - Smart search and organization
    - Safety mechanisms (dry-run, confirmations)
    """
    
    # macOS color tag mappings
    COLOR_TAGS = {
        "red": 1,
        "orange": 2,
        "yellow": 3,
        "green": 4,
        "blue": 5,
        "purple": 6,
        "gray": 7,
        "grey": 7
    }
    
    # Protected directories that should never be modified
    PROTECTED_PATHS = [
        "/System",
        "/Library",
        "/usr",
        "/bin",
        "/sbin",
        "/private",
        "/Applications",
        "/.Trash"
    ]
    
    # Warning directories that require confirmation
    WARNING_PATHS = [
        "/Users",
        "~/Library",
        "~/Documents",
        "~/.config"
    ]
    
    # Maximum files for batch operations without confirmation
    MAX_BATCH_SIZE = 100
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize file system integration.
        
        Args:
            config: Optional configuration dict
        """
        super().__init__("filesystem", config)
        self.dry_run = config.get("dry_run", False) if config else False
        self.operation_history = []  # Track operations for undo
    
    async def connect(self, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to file system.
        No credentials needed - uses current user permissions.
        """
        try:
            # Verify we can access file system
            home = Path.home()
            if not home.exists():
                raise IntegrationError("Cannot access home directory")
            
            logger.info("File system access verified")
            self._set_status(IntegrationStatus.CONNECTED)
            return True
            
        except Exception as e:
            logger.error(f"File system connection failed: {e}")
            raise IntegrationError(f"Failed to connect to file system: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from file system."""
        self._set_status(IntegrationStatus.DISCONNECTED)
        return True
    
    async def test_connection(self) -> bool:
        """Test file system connection."""
        try:
            return Path.home().exists()
        except Exception:
            return False
    
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        File system doesn't have data to fetch.
        This is an action-based integration.
        """
        return {
            "message": "File system integration is action-based",
            "metadata": {
                "dry_run": self.dry_run,
                "operations_count": len(self.operation_history)
            }
        }
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """File system doesn't index data."""
        return []
    
    # ============================================================
    # CORE FILE OPERATIONS
    # ============================================================
    
    def _validate_path_safety(self, path: Path) -> Dict[str, Any]:
        """
        Validate that a path is safe to modify.
        
        Args:
            path: Path to validate
            
        Returns:
            Dict with 'safe' (bool), 'level' (protected/warning/safe), and 'message' (str)
        """
        path_str = str(path.resolve())
        
        # Check protected paths
        for protected in self.PROTECTED_PATHS:
            if path_str.startswith(protected):
                return {
                    "safe": False,
                    "level": "protected",
                    "message": f"Path is protected: {protected}. Operations not allowed."
                }
        
        # Check warning paths
        expanded_warnings = [Path(p).expanduser().resolve() for p in self.WARNING_PATHS]
        for warning_path in expanded_warnings:
            if path_str.startswith(str(warning_path)):
                return {
                    "safe": True,
                    "level": "warning",
                    "message": f"Path is in sensitive directory. Proceed with caution."
                }
        
        return {
            "safe": True,
            "level": "safe",
            "message": "Path is safe to modify."
        }
    
    def create_folder(self, path: str, parents: bool = True) -> Dict[str, Any]:
        """
        Create a folder at the specified path.
        
        Args:
            path: Absolute or relative path to create
            parents: Create parent directories if they don't exist
            
        Returns:
            Operation result with status and path
        """
        try:
            path_obj = Path(path).expanduser().resolve()
            
            # Validate path safety
            safety = self._validate_path_safety(path_obj)
            if not safety["safe"]:
                return {
                    "success": False,
                    "error": safety["message"],
                    "safety_level": safety["level"]
                }
            
            if self.dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "action": "create_folder",
                    "path": str(path_obj),
                    "safety_level": safety["level"],
                    "message": f"Would create folder: {path_obj}"
                }
            
            if path_obj.exists():
                return {
                    "success": False,
                    "error": f"Path already exists: {path_obj}"
                }
            
            path_obj.mkdir(parents=parents, exist_ok=False)
            
            self.operation_history.append({
                "action": "create_folder",
                "path": str(path_obj),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Created folder: {path_obj}")
            return {
                "success": True,
                "action": "create_folder",
                "path": str(path_obj),
                "safety_level": safety["level"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create folder {path}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def move_file(self, source: str, destination: str, overwrite: bool = False) -> Dict[str, Any]:
        """
        Move a file or folder to a new location.
        
        Args:
            source: Path to file/folder to move
            destination: Destination path
            overwrite: Whether to overwrite if destination exists
            
        Returns:
            Operation result
        """
        try:
            src = Path(source).expanduser().resolve()
            dst = Path(destination).expanduser().resolve()
            
            if not src.exists():
                return {"success": False, "error": f"Source does not exist: {src}"}
            
            # Validate both source and destination paths
            src_safety = self._validate_path_safety(src)
            dst_safety = self._validate_path_safety(dst)
            
            if not src_safety["safe"]:
                return {
                    "success": False,
                    "error": src_safety["message"],
                    "safety_level": src_safety["level"]
                }
            
            if not dst_safety["safe"]:
                return {
                    "success": False,
                    "error": dst_safety["message"],
                    "safety_level": dst_safety["level"]
                }
            
            if self.dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "action": "move",
                    "source": str(src),
                    "destination": str(dst),
                    "safety_level": max(src_safety["level"], dst_safety["level"], key=lambda x: ["safe", "warning", "protected"].index(x)),
                    "message": f"Would move {src} → {dst}"
                }
            
            if dst.exists() and not overwrite:
                return {"success": False, "error": f"Destination exists: {dst}"}
            
            # Ensure destination parent exists
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src), str(dst))
            
            self.operation_history.append({
                "action": "move",
                "source": str(src),
                "destination": str(dst),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Moved {src} → {dst}")
            return {
                "success": True,
                "action": "move",
                "source": str(src),
                "destination": str(dst)
            }
            
        except Exception as e:
            logger.error(f"Failed to move {source} → {destination}: {e}")
            return {"success": False, "error": str(e)}
    
    def rename_file(self, path: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a file or folder.
        
        Args:
            path: Path to file/folder
            new_name: New name (not full path, just the name)
            
        Returns:
            Operation result
        """
        try:
            src = Path(path).expanduser().resolve()
            
            if not src.exists():
                return {"success": False, "error": f"Path does not exist: {src}"}
            
            # Validate path safety
            safety = self._validate_path_safety(src)
            if not safety["safe"]:
                return {
                    "success": False,
                    "error": safety["message"],
                    "safety_level": safety["level"]
                }
            
            dst = src.parent / new_name
            
            if self.dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "action": "rename",
                    "old_path": str(src),
                    "new_path": str(dst),
                    "safety_level": safety["level"],
                    "message": f"Would rename {src.name} → {new_name}"
                }
            
            src.rename(dst)
            
            self.operation_history.append({
                "action": "rename",
                "old_path": str(src),
                "new_path": str(dst),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Renamed {src.name} → {new_name}")
            return {
                "success": True,
                "action": "rename",
                "old_name": src.name,
                "new_name": new_name,
                "path": str(dst),
                "safety_level": safety["level"]
            }
            
        except Exception as e:
            logger.error(f"Failed to rename {path} → {new_name}: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================
    # macOS TAGS
    # ============================================================
    
    def add_tags(self, path: str, tags: List[str]) -> Dict[str, Any]:
        """
        Add macOS Finder tags to a file or folder.
        
        Args:
            path: Path to file/folder
            tags: List of tags (can be color names or custom labels)
                  Colors: red, orange, yellow, green, blue, purple, gray
                  
        Returns:
            Operation result
        """
        try:
            path_obj = Path(path).expanduser().resolve()
            
            if not path_obj.exists():
                return {"success": False, "error": f"Path does not exist: {path_obj}"}
            
            if self.dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "action": "add_tags",
                    "path": str(path_obj),
                    "tags": tags,
                    "message": f"Would add tags {tags} to {path_obj.name}"
                }
            
            # Get existing tags
            existing_tags = self._get_tags_xattr(path_obj)
            
            # Merge with new tags (avoid duplicates)
            all_tags = list(set(existing_tags + tags))
            
            # Set tags using xattr
            self._set_tags_xattr(path_obj, all_tags)
            
            self.operation_history.append({
                "action": "add_tags",
                "path": str(path_obj),
                "tags": tags,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Added tags {tags} to {path_obj}")
            return {
                "success": True,
                "action": "add_tags",
                "path": str(path_obj),
                "tags": all_tags
            }
            
        except Exception as e:
            logger.error(f"Failed to add tags to {path}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_tags(self, path: str) -> Dict[str, Any]:
        """
        Get macOS Finder tags from a file or folder.
        
        Args:
            path: Path to file/folder
            
        Returns:
            Operation result with tags list
        """
        try:
            path_obj = Path(path).expanduser().resolve()
            
            if not path_obj.exists():
                return {"success": False, "error": f"Path does not exist: {path_obj}"}
            
            tags = self._get_tags_xattr(path_obj)
            
            return {
                "success": True,
                "action": "get_tags",
                "path": str(path_obj),
                "tags": tags
            }
            
        except Exception as e:
            logger.error(f"Failed to get tags from {path}: {e}")
            return {"success": False, "error": str(e)}
    
    def find_by_tags(self, tags: List[str], search_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Find files by macOS Finder tags.
        
        Args:
            tags: List of tags to search for
            search_path: Path to search in (default: home directory)
            
        Returns:
            Operation result with list of matching files
        """
        try:
            search_dir = Path(search_path).expanduser() if search_path else Path.home()
            
            if not search_dir.exists():
                return {"success": False, "error": f"Search path does not exist: {search_dir}"}
            
            # Use mdfind (Spotlight) to search by tags
            # tag:tagname
            query = " OR ".join([f'tag:"{tag}"' for tag in tags])
            
            result = subprocess.run(
                ['mdfind', '-onlyin', str(search_dir), query],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {"success": False, "error": f"Search failed: {result.stderr}"}
            
            files = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
            
            logger.info(f"Found {len(files)} files with tags {tags}")
            return {
                "success": True,
                "action": "find_by_tags",
                "tags": tags,
                "search_path": str(search_dir),
                "count": len(files),
                "files": files
            }
            
        except Exception as e:
            logger.error(f"Failed to search for tags {tags}: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================
    # BATCH OPERATIONS
    # ============================================================
    
    def batch_organize(
        self,
        source_dir: str,
        rules: List[Dict[str, Any]],
        dry_run: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Organize files in batch according to rules.
        
        Args:
            source_dir: Directory to organize
            rules: List of organization rules, each with:
                {
                    "pattern": "*.pdf",  # File pattern
                    "action": "move",    # move, copy, tag
                    "destination": "~/Documents/PDFs",  # For move/copy
                    "tags": ["work", "blue"]  # For tag action
                }
            dry_run: Override instance dry_run setting
            
        Returns:
            Operation result with list of actions taken
        """
        use_dry_run = dry_run if dry_run is not None else self.dry_run
        
        try:
            src_dir = Path(source_dir).expanduser().resolve()
            
            if not src_dir.exists():
                return {"success": False, "error": f"Source directory does not exist: {src_dir}"}
            
            if not src_dir.is_dir():
                return {"success": False, "error": f"Source is not a directory: {src_dir}"}
            
            # Validate source directory safety
            safety = self._validate_path_safety(src_dir)
            if not safety["safe"]:
                return {
                    "success": False,
                    "error": safety["message"],
                    "safety_level": safety["level"]
                }
            
            # Count total files that will be affected
            total_files = 0
            for rule in rules:
                pattern = rule.get("pattern", "*")
                matching_files = list(src_dir.glob(pattern))
                total_files += len(matching_files)
            
            # Check batch size limit
            if total_files > self.MAX_BATCH_SIZE and not use_dry_run:
                return {
                    "success": False,
                    "error": f"Batch size ({total_files} files) exceeds safety limit ({self.MAX_BATCH_SIZE}). Use dry_run=true to preview.",
                    "file_count": total_files,
                    "limit": self.MAX_BATCH_SIZE
                }
            
            actions_taken = []
            
            for rule in rules:
                pattern = rule.get("pattern", "*")
                action_type = rule.get("action")
                
                # Find matching files
                matching_files = list(src_dir.glob(pattern))
                
                for file_path in matching_files:
                    if action_type == "move":
                        dest = rule.get("destination")
                        if dest:
                            result = self.move_file(str(file_path), dest, overwrite=False)
                            actions_taken.append({
                                "file": str(file_path),
                                "action": "move",
                                "destination": dest,
                                "result": result
                            })
                    
                    elif action_type == "tag":
                        tags = rule.get("tags", [])
                        if tags:
                            result = self.add_tags(str(file_path), tags)
                            actions_taken.append({
                                "file": str(file_path),
                                "action": "tag",
                                "tags": tags,
                                "result": result
                            })
            
            return {
                "success": True,
                "action": "batch_organize",
                "source": str(src_dir),
                "dry_run": use_dry_run,
                "safety_level": safety["level"],
                "total_files": total_files,
                "actions_count": len(actions_taken),
                "actions": actions_taken
            }
            
        except Exception as e:
            logger.error(f"Failed batch organize: {e}")
            return {"success": False, "error": str(e)}
    
    # ============================================================
    # UTILITY
    # ============================================================
    
    def _get_tags_xattr(self, path: Path) -> List[str]:
        """
        Get tags from file using xattr (low-level).
        
        Args:
            path: Path object to file/folder
            
        Returns:
            List of tag strings
        """
        try:
            # macOS stores tags in com.apple.metadata:_kMDItemUserTags
            tag_data = xattr.getxattr(str(path), 'com.apple.metadata:_kMDItemUserTags')
            
            # Parse the plist binary data
            tags_plist = plistlib.loads(tag_data)
            
            # Tags are stored as strings, potentially with color codes
            # Format: "TagName\n6" where 6 is the color code
            tags = []
            for tag_entry in tags_plist:
                # Split on newline to get tag name (ignore color code)
                tag_name = tag_entry.split('\n')[0] if '\n' in tag_entry else tag_entry
                tags.append(tag_name)
            
            return tags
            
        except (OSError, KeyError):
            # No tags set
            return []
        except Exception as e:
            logger.warning(f"Failed to read tags from {path}: {e}")
            return []
    
    def _set_tags_xattr(self, path: Path, tags: List[str]) -> None:
        """
        Set tags on file using xattr (low-level).
        
        Args:
            path: Path object to file/folder
            tags: List of tag strings
        """
        # Convert tags to plist format
        # macOS expects tags as array of strings, optionally with color codes
        tag_entries = []
        for tag in tags:
            # Check if it's a color tag
            tag_lower = tag.lower()
            if tag_lower in self.COLOR_TAGS:
                # Add color code: "TagName\nColorCode"
                color_code = self.COLOR_TAGS[tag_lower]
                tag_entries.append(f"{tag}\n{color_code}")
            else:
                # Regular tag (no color)
                tag_entries.append(tag)
        
        # Convert to binary plist
        tag_data = plistlib.dumps(tag_entries, fmt=plistlib.FMT_BINARY)
        
        # Set the xattr
        xattr.setxattr(str(path), 'com.apple.metadata:_kMDItemUserTags', tag_data)
    
    def get_operation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent operation history for potential undo."""
        return self.operation_history[-limit:]
    
    def clear_history(self):
        """Clear operation history."""
        self.operation_history = []

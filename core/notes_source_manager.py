"""
Notes Source Manager
Manages switching between Obsidian and native note sources.
"""

from pathlib import Path
from typing import Literal, Optional, Dict, Any
import logging
import yaml
import shutil

logger = logging.getLogger(__name__)


class NotesSourceManager:
    """Manages note source selection and migration between Obsidian and native notes."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the notes source manager.
        
        Args:
            config_path: Path to config.yaml (defaults to ~/.polly/config.yaml)
        """
        self.config_path = config_path or Path.home() / ".polly" / "config.yaml"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return {}
            
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def _save_config(self):
        """Save configuration to YAML file."""
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)
        
        logger.info(f"Saved config to {self.config_path}")
    
    def get_active_source(self) -> Literal["obsidian", "native"]:
        """Get the currently active note source.
        
        Returns:
            Either "obsidian" or "native"
        """
        return self.config.get('notes', {}).get('source', 'native')
    
    def get_notes_path(self) -> Path:
        """Get the path to the active notes directory.
        
        Returns:
            Path to either Obsidian vault or native notes directory
        """
        source = self.get_active_source()
        
        if source == 'obsidian':
            vault_path = self.config.get('notes', {}).get('obsidian', {}).get('vault_path')
            if not vault_path:
                raise ValueError("Obsidian vault path not configured")
            return Path(vault_path).expanduser()
        else:
            # Native notes - check for new knowledge_base.path structure first
            kb_path = self.config.get('knowledge_base', {}).get('path')
            if kb_path:
                # Use new structure: knowledge_base.path/notes
                return Path(kb_path).expanduser() / "notes"
            
            # Fallback to legacy notes.native.path
            notes_path = self.config.get('notes', {}).get('native', {}).get('path', '~/.polly/notes')
            return Path(notes_path).expanduser()
    
    def switch_source(self, new_source: Literal["obsidian", "native"], rag_system=None):
        """Switch between Obsidian and native note sources.
        
        This will:
        1. Stop sync manager if running
        2. Update the config to point to new source
        3. Clear the 'notes' RAG collection
        4. Re-index from the new source
        5. Restart sync manager if switching to native
        
        Args:
            new_source: The source to switch to ("obsidian" or "native")
            rag_system: RAG system instance to clear and re-index collections
        """
        current_source = self.get_active_source()
        
        if current_source == new_source:
            logger.info(f"Already using {new_source} source")
            return
        
        logger.info(f"Switching notes source from {current_source} to {new_source}")
        
        # Stop sync manager if running
        try:
            from core.notes_sync_manager import stop_sync_manager, get_sync_manager
            sync_mgr = get_sync_manager()
            if sync_mgr and sync_mgr.is_running():
                logger.info("Stopping notes sync manager...")
                stop_sync_manager()
                logger.info("Sync manager stopped")
        except Exception as e:
            logger.warning(f"Error stopping sync manager: {e}")
        
        # Update config
        if 'notes' not in self.config:
            self.config['notes'] = {}
        
        self.config['notes']['source'] = new_source
        
        # Enable/disable the appropriate source
        if 'obsidian' not in self.config['notes']:
            self.config['notes']['obsidian'] = {}
        if 'native' not in self.config['notes']:
            self.config['notes']['native'] = {}
            
        self.config['notes']['obsidian']['enabled'] = (new_source == 'obsidian')
        self.config['notes']['native']['enabled'] = (new_source == 'native')
        
        self._save_config()
        
        # Clear and re-index RAG collection if provided
        if rag_system:
            logger.info("Clearing 'notes' RAG collection...")
            try:
                # Clear the notes collection
                if 'notes' in rag_system.collections:
                    collection = rag_system.collections['notes']
                    # Get all IDs and delete them
                    all_docs = collection.get()
                    if all_docs['ids']:
                        collection.delete(ids=all_docs['ids'])
                        logger.info(f"Cleared {len(all_docs['ids'])} documents from notes collection")
                
                # Re-index from new source
                notes_path = self.get_notes_path()
                logger.info(f"Re-indexing from {notes_path}...")
                
                if new_source == 'obsidian':
                    count = rag_system.index_obsidian_vault(notes_path, force=True)
                else:
                    # For native notes, also use index_obsidian_vault (works for any markdown directory)
                    count = rag_system.index_obsidian_vault(notes_path, force=True)
                
                logger.info(f"Indexed {count} notes from {new_source} source")
                
            except Exception as e:
                logger.error(f"Error during RAG re-indexing: {e}")
                raise
        
        # Start sync manager if switching to native and auto_index is enabled
        if new_source == 'native' and rag_system:
            try:
                auto_index = self.config.get('notes', {}).get('auto_index', True)
                if auto_index:
                    from core.notes_sync_manager import start_sync_manager
                    notes_path = self.get_notes_path()
                    logger.info(f"Starting notes sync manager for {notes_path}...")
                    start_sync_manager(notes_path, rag_system, initial_build=False)
                    logger.info("Sync manager started")
            except Exception as e:
                logger.warning(f"Error starting sync manager: {e}")
    
    def migrate_from_obsidian(
        self, 
        vault_path: Path,
        target_path: Optional[Path] = None,
        rag_system=None,
        domain_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Migrate notes from Obsidian vault to native Polly notes.
        
        This is a full migration that:
        1. Copies all markdown files from vault to ~/.polly/notes/
        2. Organizes into domain folders (if domain_mapping provided)
        3. Copies attachments to _Attachments/
        4. Rewrites image links to point to new attachment location
        5. Switches source to 'native'
        6. Re-indexes RAG
        
        Args:
            vault_path: Path to Obsidian vault
            target_path: Target path for native notes (defaults to ~/.polly/notes)
            rag_system: RAG system to re-index after migration
            domain_mapping: Optional mapping of folders to domains
            
        Returns:
            Dict with migration statistics
        """
        vault_path = Path(vault_path).expanduser()
        target_path = target_path or Path.home() / ".polly" / "notes"
        target_path = target_path.expanduser()
        
        if not vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")
        
        logger.info(f"Migrating notes from {vault_path} to {target_path}")
        
        stats = {
            'files_copied': 0,
            'attachments_copied': 0,
            'links_rewritten': 0,
            'errors': []
        }
        
        # Create target directory structure
        target_path.mkdir(parents=True, exist_ok=True)
        attachments_path = target_path / "_Attachments"
        (attachments_path / "images").mkdir(parents=True, exist_ok=True)
        (attachments_path / "files").mkdir(parents=True, exist_ok=True)
        
        # First, copy all attachments to new location and build a mapping
        attachment_mapping = {}  # old_path -> new_relative_path
        attachment_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.webp']
        
        for ext in attachment_extensions:
            for attachment in vault_path.rglob(f"*{ext}"):
                try:
                    # Skip if in templates or hidden folders
                    if any(part.startswith('.') for part in attachment.parts):
                        continue
                    if ".templates" in attachment.parts or "Templates" in attachment.parts:
                        continue
                    
                    # Determine if it's an image or file
                    is_image = ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
                    target_dir = attachments_path / ("images" if is_image else "files")
                    
                    target_file = target_dir / attachment.name
                    
                    # Handle duplicates by adding suffix
                    counter = 1
                    while target_file.exists():
                        stem = attachment.stem
                        target_file = target_dir / f"{stem}_{counter}{ext}"
                        counter += 1
                    
                    shutil.copy2(attachment, target_file)
                    stats['attachments_copied'] += 1
                    
                    # Store mapping: attachment filename -> new relative path from notes root
                    attachment_mapping[attachment.name] = f"_Attachments/{'images' if is_image else 'files'}/{target_file.name}"
                    
                except Exception as e:
                    logger.error(f"Error copying attachment {attachment}: {e}")
                    stats['errors'].append(str(e))
        
        # Copy markdown files and rewrite attachment links
        for md_file in vault_path.rglob("*.md"):
            try:
                # Skip templates directory if exists
                if ".templates" in md_file.parts or "Templates" in md_file.parts:
                    continue
                
                # Read file content
                content = md_file.read_text(encoding='utf-8')
                
                # Rewrite image/attachment links
                # Pattern matches: ![alt text](path/to/image.png) or ![](image.png)
                def replace_link(match):
                    alt_text = match.group(1)
                    link_path = match.group(2)
                    
                    # Extract filename from path
                    filename = Path(link_path).name
                    
                    # If we have a mapping for this attachment, rewrite it
                    if filename in attachment_mapping:
                        new_path = attachment_mapping[filename]
                        stats['links_rewritten'] += 1
                        return f"![{alt_text}](../{new_path})"
                    else:
                        # Keep original link
                        return match.group(0)
                
                # Rewrite image links
                content = re.sub(r'!\[(.*?)\]\(([^)]+)\)', replace_link, content)
                
                # Determine target location
                rel_path = md_file.relative_to(vault_path)
                
                # Apply domain mapping if provided
                if domain_mapping:
                    # Get the top-level folder
                    top_folder = rel_path.parts[0] if len(rel_path.parts) > 1 else ""
                    if top_folder in domain_mapping:
                        domain = domain_mapping[top_folder]
                        target_file = target_path / domain / rel_path.name
                    else:
                        target_file = target_path / rel_path
                else:
                    target_file = target_path / rel_path
                
                # Create parent directory
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file with rewritten links
                target_file.write_text(content, encoding='utf-8')
                stats['files_copied'] += 1
                
            except Exception as e:
                logger.error(f"Error copying {md_file}: {e}")
                stats['errors'].append(str(e))
        
        logger.info(f"Migration complete: {stats['files_copied']} files, {stats['attachments_copied']} attachments, {stats['links_rewritten']} links rewritten")
        
        # Update config to use native notes
        self.config['notes'] = {
            'source': 'native',
            'native': {
                'path': str(target_path),
                'enabled': True
            },
            'obsidian': {
                'vault_path': str(vault_path),
                'enabled': False
            }
        }
        self._save_config()
        
        # Re-index if RAG system provided
        if rag_system:
            logger.info("Re-indexing notes in RAG...")
            try:
                # Clear notes collection
                if 'notes' in rag_system.collections:
                    collection = rag_system.collections['notes']
                    all_docs = collection.get()
                    if all_docs['ids']:
                        collection.delete(ids=all_docs['ids'])
                
                # Index from new location
                count = rag_system.index_directory(target_path, force=True)
                logger.info(f"Indexed {count} notes")
                
            except Exception as e:
                logger.error(f"Error re-indexing: {e}")
                stats['errors'].append(f"RAG indexing error: {str(e)}")
        
        return stats
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get information about the current note source configuration.
        
        Returns:
            Dict with source configuration details
        """
        source = self.get_active_source()
        notes_path = self.get_notes_path()
        
        info = {
            'active_source': source,
            'notes_path': str(notes_path),
            'path_exists': notes_path.exists()
        }
        
        if source == 'obsidian':
            info['vault_path'] = str(notes_path)
        else:
            info['native_path'] = str(notes_path)
        
        return info

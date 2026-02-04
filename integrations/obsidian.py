"""
Obsidian Integration
Indexes Obsidian vault and provides read/write capabilities
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import logging
import shutil
import re
import yaml

from .base import Integration, IntegrationStatus, IntegrationError

logger = logging.getLogger(__name__)


class ObsidianIntegration(Integration):
    """
    Obsidian integration for Polly.
    
    Provides:
    - Vault indexing for RAG queries
    - Note creation with domain-aware folder suggestions
    - Note modification (append, update frontmatter)
    - Daily/weekly note generation from templates
    - Project creation with special flow
    - Tag suggestions
    - Auto-linking to related notes
    """
    
    # Protected paths - cannot write to these
    PROTECTED_PATHS = ['.obsidian', '.trash', '.git']
    
    # System paths that ARE writeable (exception to protected rule)
    WRITEABLE_SYSTEM_PATHS = ['00-System/templates']
    
    # Backup retention in days
    BACKUP_RETENTION_DAYS = 30
    
    def __init__(self, vault_path: Path, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Obsidian integration.
        
        Args:
            vault_path: Path to Obsidian vault
            config: Optional configuration overrides
        """
        super().__init__("obsidian", config)
        self.vault_path = Path(vault_path)
        self.indexed_files: Dict[str, datetime] = {}
        
    async def connect(self, credentials: Dict[str, str] = None) -> bool:
        """
        Connect to Obsidian vault (verify it exists).
        
        Args:
            credentials: Not needed for local vault access
        
        Returns:
            True if vault exists and is accessible
        """
        print(f"=== OBSIDIAN CONNECT CALLED ===", flush=True)
        print(f"Vault path: {self.vault_path}", flush=True)
        print(f"Current status before connect: {self.status}", flush=True)
        logger.info(f"=== OBSIDIAN CONNECT CALLED ===")
        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Current status before connect: {self.status}")
        
        try:
            if not self.vault_path.exists():
                raise IntegrationError(f"Vault path does not exist: {self.vault_path}")
            
            if not self.vault_path.is_dir():
                raise IntegrationError(f"Vault path is not a directory: {self.vault_path}")
            
            # Check if it's an Obsidian vault (has .obsidian folder)
            obsidian_config = self.vault_path / ".obsidian"
            if not obsidian_config.exists():
                logger.warning(f"No .obsidian folder found in {self.vault_path}")
                # Continue anyway - might be a plain markdown folder
            
            self._set_status(IntegrationStatus.CONNECTED)
            print(f"=== OBSIDIAN CONNECTED SUCCESSFULLY ===", flush=True)
            print(f"Status after connect: {self.status}", flush=True)
            logger.info(f"=== OBSIDIAN CONNECTED SUCCESSFULLY ===")
            logger.info(f"Status after connect: {self.status}")
            return True
            
        except Exception as e:
            print(f"OBSIDIAN CONNECT FAILED: {e}", flush=True)
            logger.error(f"Failed to connect to Obsidian vault: {e}")
            self._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Connection failed: {e}")
    
    async def disconnect(self) -> bool:
        """Disconnect from Obsidian vault."""
        self.indexed_files.clear()
        self._set_status(IntegrationStatus.DISCONNECTED)
        logger.info("Disconnected from Obsidian vault")
        return True
    
    async def test_connection(self) -> bool:
        """Test if vault is still accessible."""
        try:
            return self.vault_path.exists() and self.vault_path.is_dir()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    async def fetch_data(self, force: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Fetch markdown files from vault for indexing.
        
        Args:
            force: Force re-index of all files
            **kwargs: Additional options
        
        Returns:
            Dict with:
                - items: List of markdown files with content
                - metadata: Indexing statistics
        """
        logger.info(f"fetch_data called, current status: {self.status}, vault_path: {self.vault_path}")
        
        # Allow both CONNECTED and SYNCING status (manager sets to SYNCING before calling fetch_data)
        if self.status not in (IntegrationStatus.CONNECTED, IntegrationStatus.SYNCING):
            error_msg = f"Not connected to vault (status: {self.status}, vault_path: {self.vault_path})"
            logger.error(error_msg)
            raise IntegrationError(error_msg)
        
        try:
            self._set_status(IntegrationStatus.SYNCING)
            
            # Find all markdown files
            md_files = list(self.vault_path.rglob("*.md"))
            
            # Filter out hidden/system files
            md_files = [
                f for f in md_files 
                if not any(part.startswith('.') for part in f.parts)
            ]
            
            # Filter out templates and trash (read-only for now)
            md_files = [
                f for f in md_files 
                if 'templates' not in f.parts and '.trash' not in str(f).lower()
            ]
            
            logger.info(f"Found {len(md_files)} markdown files in vault")
            
            items = []
            indexed = 0
            errors = 0
            
            for md_file in md_files:
                try:
                    # Check if file needs re-indexing
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    
                    if not force and md_file in self.indexed_files:
                        if self.indexed_files[md_file] >= mtime:
                            # Already indexed and hasn't changed
                            continue
                    
                    # Read file content
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    items.append({
                        'filepath': str(md_file),
                        'filename': md_file.name,
                        'content': content,
                        'modified': mtime.isoformat(),
                        'size': len(content)
                    })
                    
                    self.indexed_files[md_file] = mtime
                    indexed += 1
                    
                except Exception as e:
                    errors += 1
                    logger.error(f"Error reading {md_file.name}: {e}")
            
            self._set_status(IntegrationStatus.CONNECTED)
            self.last_sync = datetime.now()
            
            metadata = {
                'total_files': len(md_files),
                'indexed': indexed,
                'errors': errors,
                'vault_path': str(self.vault_path)
            }
            
            logger.info(f"Indexed {indexed} files, {errors} errors")
            
            return {
                'items': items,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Fetch data failed: {e}")
            self._set_status(IntegrationStatus.ERROR, str(e))
            raise IntegrationError(f"Fetch failed: {e}")
    
    def format_for_rag(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format fetched markdown files for RAG indexing.
        
        Args:
            data: Raw data from fetch_data()
        
        Returns:
            List of documents with metadata for RAG system
        """
        documents = []
        
        for item in data.get('items', []):
            documents.append({
                'content': item['content'],
                'metadata': {
                    'id': item['filepath'],  # Use filepath as unique ID
                    'source': 'obsidian',
                    'type': 'markdown',
                    'filepath': item['filepath'],
                    'filename': item['filename'],
                    'modified': item['modified'],
                    'vault': str(self.vault_path)
                }
            })
        
        return documents
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status with Obsidian-specific info."""
        status = super().get_status()
        
        # Get indexed count from persistent state
        indexed_count = len(self.indexed_files)  # Default to in-memory tracker
        
        try:
            from integrations.state import get_state_manager
            state_manager = get_state_manager()
            saved_count = state_manager.get_metadata("obsidian", "indexed_count")
            if saved_count is not None:
                indexed_count = saved_count
        except Exception as e:
            logger.debug(f"Could not retrieve saved indexed count: {e}")
        
        status.update({
            'vault_path': str(self.vault_path),
            'indexed_files': indexed_count
        })
        return status
    
    # ===== SAFETY MECHANISMS =====
    
    def _is_path_protected(self, note_path: Path) -> bool:
        """
        Check if path is protected from writes.
        
        Args:
            note_path: Path to check (relative to vault or absolute)
        
        Returns:
            True if path is protected
        """
        # Make relative to vault if absolute
        if note_path.is_absolute():
            try:
                relative_path = note_path.relative_to(self.vault_path)
            except ValueError:
                # Path is outside vault
                return True
        else:
            relative_path = note_path
        
        path_str = str(relative_path)
        
        # Check if path is in writeable system paths
        for writeable in self.WRITEABLE_SYSTEM_PATHS:
            if path_str.startswith(writeable):
                return False
        
        # Check if path contains protected directories
        for protected in self.PROTECTED_PATHS:
            if protected in relative_path.parts:
                return True
        
        return False
    
    def _backup_file(self, note_path: Path) -> Optional[Path]:
        """
        Create backup of existing file before modification.
        
        Args:
            note_path: Path to file to backup
        
        Returns:
            Path to backup file, or None if file doesn't exist
        """
        if not note_path.exists():
            return None
        
        try:
            # Create backup directory structure
            now = datetime.now()
            backup_dir = self.vault_path / ".polly_backups" / now.strftime("%Y-%m")
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{note_path.stem}_{timestamp}.md"
            backup_path = backup_dir / backup_filename
            
            # Copy file to backup location
            shutil.copy2(note_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup of {note_path}: {e}")
            raise IntegrationError(f"Backup failed: {e}")
    
    def _validate_write(self, note_path: Path, content: str) -> Dict[str, Any]:
        """
        Validate write operation before execution.
        
        Args:
            note_path: Path where content will be written
            content: Content to write
        
        Returns:
            Dict with validation results and warnings
        
        Raises:
            IntegrationError: If validation fails
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Check if path is protected
        if self._is_path_protected(note_path):
            validation['valid'] = False
            validation['errors'].append(f"Cannot write to protected path: {note_path}")
            return validation
        
        # Check if path is within vault
        try:
            if note_path.is_absolute():
                note_path.relative_to(self.vault_path)
        except ValueError:
            validation['valid'] = False
            validation['errors'].append(f"Path is outside vault: {note_path}")
            return validation
        
        # Check content size (warn if > 1MB)
        content_size = len(content.encode('utf-8'))
        if content_size > 1_000_000:
            validation['warnings'].append(f"Large file size: {content_size / 1_000_000:.1f}MB")
        
        # Check for potential issues in content
        if len(content.strip()) == 0:
            validation['warnings'].append("Content is empty")
        
        # Validate YAML frontmatter if present
        if content.startswith('---'):
            try:
                # Extract frontmatter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter_str = parts[1]
                    yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as e:
                validation['warnings'].append(f"Invalid YAML frontmatter: {e}")
        
        if not validation['valid']:
            errors_str = '; '.join(validation['errors'])
            raise IntegrationError(f"Validation failed: {errors_str}")
        
        return validation
    
    def _prepare_write_preview(
        self, 
        note_path: Path, 
        content: str, 
        operation: str = "create"
    ) -> Dict[str, Any]:
        """
        Prepare preview for write confirmation.
        
        Args:
            note_path: Target file path
            content: Content to write/append
            operation: Operation type (create, append, update)
        
        Returns:
            Dict with preview and metadata for confirmation UI
        """
        # Make path relative for display
        try:
            if note_path.is_absolute():
                display_path = note_path.relative_to(self.vault_path)
            else:
                display_path = note_path
        except ValueError:
            display_path = note_path
        
        preview = {
            'operation': operation,
            'note_path': str(display_path),
            'full_path': str(note_path),
            'content_preview': content[:500] + ('...' if len(content) > 500 else ''),
            'content_full': content,
            'file_exists': note_path.exists(),
            'will_backup': note_path.exists(),
            'size_bytes': len(content.encode('utf-8'))
        }
        
        # Extract metadata from content
        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    preview['frontmatter'] = frontmatter
            except Exception:
                pass
        
        return preview
    
    # ===== WRITE OPERATIONS =====
    
    def create_note(
        self, 
        title: str, 
        content: str = "", 
        folder: Optional[str] = None,
        tags: Optional[List[str]] = None,
        frontmatter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new note in the vault.
        
        Args:
            title: Note title (becomes filename)
            content: Note content (without frontmatter)
            folder: Folder path relative to vault (e.g. "01-Sigils")
            tags: List of tags to add to frontmatter
            frontmatter: Additional frontmatter fields
        
        Returns:
            Dict with preview and metadata for confirmation
        """
        if self.status != IntegrationStatus.CONNECTED:
            raise IntegrationError("Not connected to vault")
        
        try:
            # Sanitize filename
            safe_title = re.sub(r'[<>:"/\\|?*]', '-', title)
            filename = f"{safe_title}.md"
            
            # Determine target path
            if folder:
                folder_path = self.vault_path / folder
                folder_path.mkdir(parents=True, exist_ok=True)
            else:
                folder_path = self.vault_path
            
            note_path = folder_path / filename
            
            # Check if file already exists
            if note_path.exists():
                raise IntegrationError(f"Note already exists: {note_path.name}")
            
            # Build frontmatter
            fm = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'type': 'note',
                'created_by': 'polly'
            }
            
            if tags:
                fm['tags'] = tags
            
            if frontmatter:
                fm.update(frontmatter)
            
            # Build full content with frontmatter
            fm_yaml = yaml.dump(fm, default_flow_style=False, allow_unicode=True)
            full_content = f"---\n{fm_yaml}---\n\n# {title}\n\n{content}"
            
            # Validate write
            validation = self._validate_write(note_path, full_content)
            
            # Prepare preview for confirmation
            preview = self._prepare_write_preview(note_path, full_content, "create")
            preview['validation'] = validation
            preview['requires_confirmation'] = True
            
            return preview
            
        except IntegrationError:
            raise
        except Exception as e:
            logger.error(f"Failed to prepare note creation: {e}")
            raise IntegrationError(f"Note creation failed: {e}")
    
    def execute_create_note(self, preview: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute confirmed note creation.
        
        Args:
            preview: Preview dict from create_note()
        
        Returns:
            Dict with operation result
        """
        try:
            note_path = Path(preview['full_path'])
            content = preview['content_full']
            
            # Final validation
            self._validate_write(note_path, content)
            
            # Write file
            note_path.write_text(content, encoding='utf-8')
            
            logger.info(f"Created note: {note_path}")
            
            return {
                'success': True,
                'note_path': str(note_path.relative_to(self.vault_path)),
                'operation': 'create',
                'message': f"Note created: {note_path.name}"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute note creation: {e}")
            raise IntegrationError(f"Note creation failed: {e}")
    
    def append_to_note(
        self, 
        note_path: str, 
        content: str,
        section: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Append content to existing note.
        
        Args:
            note_path: Path to note (relative to vault or absolute)
            content: Content to append
            section: Optional section header to append under
        
        Returns:
            Dict with preview and metadata for confirmation
        """
        if self.status != IntegrationStatus.CONNECTED:
            raise IntegrationError("Not connected to vault")
        
        try:
            # Resolve path
            path = Path(note_path)
            if not path.is_absolute():
                path = self.vault_path / path
            
            if not path.exists():
                raise IntegrationError(f"Note not found: {note_path}")
            
            # Read existing content
            existing = path.read_text(encoding='utf-8')
            
            # Prepare new content
            if section:
                # Try to find section and insert after it
                section_pattern = f"#{1,6}\\s+{re.escape(section)}"
                match = re.search(section_pattern, existing)
                
                if match:
                    # Find next section or end of file
                    next_section = re.search(r'\n#{1,6}\s+', existing[match.end():])
                    if next_section:
                        insert_pos = match.end() + next_section.start()
                        new_content = (
                            existing[:insert_pos] + 
                            f"\n\n{content}\n" + 
                            existing[insert_pos:]
                        )
                    else:
                        # Append to end of section
                        new_content = existing[:match.end()] + f"\n\n{content}" + existing[match.end():]
                else:
                    # Section not found, append to end
                    new_content = existing + f"\n\n## {section}\n\n{content}"
            else:
                # Simple append to end
                new_content = existing + f"\n\n{content}"
            
            # Validate write
            validation = self._validate_write(path, new_content)
            
            # Prepare preview
            preview = self._prepare_write_preview(path, new_content, "append")
            preview['validation'] = validation
            preview['requires_confirmation'] = True
            preview['existing_content'] = existing[:200] + '...'
            preview['appended_content'] = content
            
            return preview
            
        except IntegrationError:
            raise
        except Exception as e:
            logger.error(f"Failed to prepare append: {e}")
            raise IntegrationError(f"Append failed: {e}")
    
    def execute_append_to_note(self, preview: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute confirmed append operation.
        
        Args:
            preview: Preview dict from append_to_note()
        
        Returns:
            Dict with operation result
        """
        try:
            note_path = Path(preview['full_path'])
            content = preview['content_full']
            
            # Create backup
            backup_path = self._backup_file(note_path)
            
            # Final validation
            self._validate_write(note_path, content)
            
            # Write file
            note_path.write_text(content, encoding='utf-8')
            
            logger.info(f"Appended to note: {note_path}")
            
            return {
                'success': True,
                'note_path': str(note_path.relative_to(self.vault_path)),
                'operation': 'append',
                'backup_path': str(backup_path) if backup_path else None,
                'message': f"Content appended to: {note_path.name}"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute append: {e}")
            raise IntegrationError(f"Append failed: {e}")
    
    def update_frontmatter(
        self, 
        note_path: str, 
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update frontmatter fields in existing note.
        
        Args:
            note_path: Path to note (relative to vault or absolute)
            updates: Dict of frontmatter fields to update/add
        
        Returns:
            Dict with preview and metadata for confirmation
        """
        if self.status != IntegrationStatus.CONNECTED:
            raise IntegrationError("Not connected to vault")
        
        try:
            # Resolve path
            path = Path(note_path)
            if not path.is_absolute():
                path = self.vault_path / path
            
            if not path.exists():
                raise IntegrationError(f"Note not found: {note_path}")
            
            # Read existing content
            existing = path.read_text(encoding='utf-8')
            
            # Parse frontmatter
            if existing.startswith('---'):
                parts = existing.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2]
                else:
                    frontmatter = {}
                    body = existing
            else:
                # No frontmatter exists, create new
                frontmatter = {}
                body = existing
            
            # Update frontmatter
            frontmatter.update(updates)
            
            # Rebuild content
            fm_yaml = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
            new_content = f"---\n{fm_yaml}---{body}"
            
            # Validate write
            validation = self._validate_write(path, new_content)
            
            # Prepare preview
            preview = self._prepare_write_preview(path, new_content, "update_frontmatter")
            preview['validation'] = validation
            preview['requires_confirmation'] = True
            preview['updates'] = updates
            preview['old_frontmatter'] = yaml.safe_load(parts[1]) if existing.startswith('---') and len(parts) >= 3 else {}
            preview['new_frontmatter'] = frontmatter
            
            return preview
            
        except IntegrationError:
            raise
        except Exception as e:
            logger.error(f"Failed to prepare frontmatter update: {e}")
            raise IntegrationError(f"Frontmatter update failed: {e}")
    
    def execute_update_frontmatter(self, preview: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute confirmed frontmatter update.
        
        Args:
            preview: Preview dict from update_frontmatter()
        
        Returns:
            Dict with operation result
        """
        try:
            note_path = Path(preview['full_path'])
            content = preview['content_full']
            
            # Create backup
            backup_path = self._backup_file(note_path)
            
            # Final validation
            self._validate_write(note_path, content)
            
            # Write file
            note_path.write_text(content, encoding='utf-8')
            
            logger.info(f"Updated frontmatter: {note_path}")
            
            return {
                'success': True,
                'note_path': str(note_path.relative_to(self.vault_path)),
                'operation': 'update_frontmatter',
                'backup_path': str(backup_path) if backup_path else None,
                'message': f"Frontmatter updated: {note_path.name}"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute frontmatter update: {e}")
            raise IntegrationError(f"Frontmatter update failed: {e}")
    
    def validate_vault(self, vault_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Scan vault for compatibility issues before migration.
        
        This method checks for Obsidian features that may not work in Polly v1:
        - Canvas files (.canvas)
        - Dataview queries
        - Math notation (LaTeX)
        - Mermaid diagrams
        - Wiki-links (supported, just counted for stats)
        - Tags (supported, just counted for stats)
        
        Args:
            vault_path: Path to vault (defaults to self.vault_path)
        
        Returns:
            Dict with validation report:
            {
                'compatible': bool,
                'warnings': [{'severity': str, 'title': str, 'message': str, 'requiresAction': bool}],
                'blockers': [],
                'statistics': {
                    'totalFiles': int,
                    'wikiLinks': int,
                    'tags': int,
                    'canvasFiles': int,
                    'dataviewQueries': int,
                    'dataviewFiles': [Path],
                    'mathNotation': int,
                    'mermaidDiagrams': int
                }
            }
        """
        vault_path = vault_path or self.vault_path
        
        logger.info(f"Validating vault: {vault_path}")
        
        report = {
            'compatible': True,
            'warnings': [],
            'blockers': [],
            'statistics': {
                'totalFiles': 0,
                'wikiLinks': 0,
                'tags': 0,
                'canvasFiles': 0,
                'dataviewQueries': 0,
                'dataviewFiles': [],
                'mathNotation': 0,
                'mermaidDiagrams': 0
            }
        }
        
        # Scan for Canvas files
        canvas_files = list(vault_path.rglob("*.canvas"))
        report['statistics']['canvasFiles'] = len(canvas_files)
        if canvas_files:
            report['warnings'].append({
                'severity': 'info',
                'title': f"{len(canvas_files)} Canvas file{'s' if len(canvas_files) > 1 else ''} detected",
                'message': 'Canvas files will be skipped during import',
                'locations': [str(f.relative_to(vault_path)) for f in canvas_files[:5]]  # Show first 5
            })
        
        # Scan markdown files
        md_files = list(vault_path.rglob("*.md"))
        report['statistics']['totalFiles'] = len(md_files)
        
        dataview_files = []
        wiki_link_pattern = r'\[\[([^\]]+)\]\]'
        tag_pattern = r'(?:^|\s)#([a-zA-Z0-9/_-]+)'
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                
                # Count wiki-links
                wiki_links = re.findall(wiki_link_pattern, content)
                report['statistics']['wikiLinks'] += len(wiki_links)
                
                # Count tags
                tags = re.findall(tag_pattern, content, re.MULTILINE)
                report['statistics']['tags'] += len(tags)
                
                # Check for Dataview queries
                if '```dataview' in content:
                    dataview_files.append(md_file)
                    queries = re.findall(r'```dataview\n([\s\S]*?)\n```', content)
                    report['statistics']['dataviewQueries'] += len(queries)
                
                # Check for math notation
                if '$$' in content or re.search(r'(?<!\$)\$(?!\$)[^$]+\$(?!\$)', content):
                    report['statistics']['mathNotation'] += 1
                
                # Check for Mermaid diagrams
                if '```mermaid' in content:
                    report['statistics']['mermaidDiagrams'] += 1
                    
            except Exception as e:
                logger.warning(f"Error reading {md_file}: {e}")
                continue
        
        # Add warning for Dataview queries
        if dataview_files:
            report['statistics']['dataviewFiles'] = [str(f.relative_to(vault_path)) for f in dataview_files]
            report['warnings'].append({
                'severity': 'warning',
                'title': f"{report['statistics']['dataviewQueries']} Dataview quer{'ies' if report['statistics']['dataviewQueries'] > 1 else 'y'} detected",
                'message': 'Dataview queries must be converted (you\'ll choose how in the next step)',
                'requiresAction': True,
                'files': report['statistics']['dataviewFiles'][:10]  # Show first 10
            })
        
        # Add info for math notation
        if report['statistics']['mathNotation'] > 0:
            report['warnings'].append({
                'severity': 'info',
                'title': f"{report['statistics']['mathNotation']} note{'s' if report['statistics']['mathNotation'] > 1 else ''} with math notation",
                'message': 'Math will render as plain text in Polly v1 (LaTeX rendering planned for future release)'
            })
        
        # Add info for Mermaid diagrams
        if report['statistics']['mermaidDiagrams'] > 0:
            report['warnings'].append({
                'severity': 'info',
                'title': f"{report['statistics']['mermaidDiagrams']} note{'s' if report['statistics']['mermaidDiagrams'] > 1 else ''} with Mermaid diagrams",
                'message': 'Mermaid diagrams will render as code blocks in Polly v1'
            })
        
        # Add success message for supported features
        if report['statistics']['wikiLinks'] > 0 or report['statistics']['tags'] > 0:
            supported_features = []
            if report['statistics']['wikiLinks'] > 0:
                supported_features.append(f"{report['statistics']['wikiLinks']} wiki-links")
            if report['statistics']['tags'] > 0:
                supported_features.append(f"{report['statistics']['tags']} tags")
            
            report['warnings'].append({
                'severity': 'success',
                'title': 'Fully supported features detected',
                'message': f"Found {', '.join(supported_features)} that will work perfectly in Polly"
            })
        
        logger.info(f"Vault validation complete: {len(report['warnings'])} warnings, {len(report['blockers'])} blockers")
        
        return report

"""
Notes Index System
Tracks all notes, their aliases, and enables fast lookups.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import re
import yaml

logger = logging.getLogger(__name__)


@dataclass
class NoteInfo:
    """Information about a single note."""
    
    path: Path
    name: str  # Filename without extension
    aliases: List[str] = field(default_factory=list)
    title: str = ""  # From frontmatter or first heading
    domain: Optional[str] = None  # From frontmatter or folder
    tags: List[str] = field(default_factory=list)  # From frontmatter only
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    size: int = 0  # File size in bytes
    
    def __post_init__(self):
        """Normalize data after initialization."""
        # Ensure aliases are unique and don't include the note name
        self.aliases = [a for a in self.aliases if a and a != self.name]
        self.aliases = list(dict.fromkeys(self.aliases))  # Remove duplicates, preserve order


class NotesIndex:
    """
    Index system for notes that supports fast lookups by name, alias, or tag.
    
    Maintains an in-memory index of all notes with their metadata extracted
    from frontmatter and file properties.
    """
    
    def __init__(self):
        """Initialize an empty notes index."""
        self._notes_by_path: Dict[Path, NoteInfo] = {}
        self._notes_by_name: Dict[str, NoteInfo] = {}
        self._notes_by_alias: Dict[str, NoteInfo] = {}
        self._last_build: Optional[datetime] = None
        
    def build_index(self, notes_path: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Build the notes index by scanning a directory.
        
        Args:
            notes_path: Root directory containing notes
            recursive: Whether to scan subdirectories
            
        Returns:
            Statistics about the indexing operation:
            {
                "notes_indexed": int,
                "with_aliases": int,
                "with_domains": int,
                "with_tags": int,
                "duration_ms": float,
                "errors": List[str]
            }
        """
        start_time = datetime.now()
        stats = {
            "notes_indexed": 0,
            "with_aliases": 0,
            "with_domains": 0,
            "with_tags": 0,
            "errors": []
        }
        
        logger.info(f"Building notes index from {notes_path}")
        
        if not notes_path.exists():
            error_msg = f"Notes path does not exist: {notes_path}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats
        
        # Build folder_name -> domain_id mapping from user-configured domains.
        # e.g. {"01-Sigils": "sigils", "02-Signals": "signals"}
        # Falls back to raw folder name if no match found.
        self._folder_to_domain_id: Dict[str, str] = {}
        try:
            from core.domain_config import load_domains
            domain_cfg = load_domains()
            for d in domain_cfg.domains:
                if d.folder_path:
                    # folder_path may be "01-Sigils" or "sigils" -- normalize both
                    self._folder_to_domain_id[d.folder_path] = d.id
                    # Also map the lowercase id itself in case folders are named by id
                    self._folder_to_domain_id[d.id] = d.id
        except Exception as e:
            logger.warning(f"Notes index: could not load domain config for folder mapping: {e}")
        
        # Clear existing index
        self.clear()
        
        # Find all markdown files
        pattern = "**/*.md" if recursive else "*.md"
        markdown_files = list(notes_path.glob(pattern))
        
        logger.info(f"Found {len(markdown_files)} markdown files")
        
        for md_file in markdown_files:
            try:
                # Skip files in special directories (check relative path only)
                rel_path = md_file.relative_to(notes_path)
                if any(part.startswith('.') or part.startswith('_') for part in rel_path.parts):
                    continue
                
                note_info = self._extract_note_info(md_file, notes_path)
                self._add_note_to_index(note_info)
                
                stats["notes_indexed"] += 1
                if note_info.aliases:
                    stats["with_aliases"] += 1
                if note_info.domain:
                    stats["with_domains"] += 1
                if note_info.tags:
                    stats["with_tags"] += 1
                    
            except Exception as e:
                error_msg = f"Error indexing {md_file}: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
        
        self._last_build = datetime.now()
        duration_ms = (self._last_build - start_time).total_seconds() * 1000
        stats["duration_ms"] = round(duration_ms, 2)
        
        logger.info(f"Index built: {stats['notes_indexed']} notes in {stats['duration_ms']}ms")
        
        return stats
    
    def _extract_note_info(self, md_file: Path, root_path: Path) -> NoteInfo:
        """
        Extract metadata from a markdown file.
        
        Args:
            md_file: Path to markdown file
            root_path: Root notes directory for relative path calculation
            
        Returns:
            NoteInfo object with extracted metadata
        """
        # Basic file info
        stat = md_file.stat()
        note_info = NoteInfo(
            path=md_file.resolve(),
            name=md_file.stem,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime),
            size=stat.st_size
        )
        
        # Read file content
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except OSError as e:
            # Errno 60 = ETIMEDOUT (e.g. iCloud not synced); avoid flooding logs
            if getattr(e, 'errno', None) == 60:
                logger.debug("Could not read %s: %s", md_file, e)
            else:
                logger.warning("Could not read %s: %s", md_file, e)
            return note_info
        except Exception as e:
            logger.warning("Could not read %s: %s", md_file, e)
            return note_info
        
        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)
        
        if frontmatter:
            # Get title
            note_info.title = frontmatter.get('title', '')
            
            # Get aliases
            aliases = frontmatter.get('aliases', [])
            if isinstance(aliases, str):
                aliases = [aliases]
            elif not isinstance(aliases, list):
                aliases = []
            note_info.aliases = aliases
            
            # Get tags from frontmatter
            tags = frontmatter.get('tags', [])
            if isinstance(tags, str):
                tags = [tags]
            elif not isinstance(tags, list):
                tags = []
            note_info.tags = tags
        
        # If no title in frontmatter, extract from first heading
        if not note_info.title:
            note_info.title = self._extract_first_heading(content) or note_info.name
        
        # Domain resolution priority:
        # 1. Frontmatter 'domain' field (user-specified, highest priority)
        # 2. Folder structure mapped to configured domain IDs
        # 3. Raw folder name as fallback
        frontmatter_domain = frontmatter.get('domain', '') if frontmatter else ''
        if frontmatter_domain and isinstance(frontmatter_domain, str) and frontmatter_domain.strip():
            note_info.domain = frontmatter_domain.strip().lower()
        else:
            note_info.domain = self._infer_domain_from_path(md_file, root_path)
        
        return note_info
    
    def _extract_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Extract YAML frontmatter from markdown content.
        
        Args:
            content: Markdown file content
            
        Returns:
            Dictionary of frontmatter fields, or None if no frontmatter
        """
        # Check for frontmatter (must start with ---)
        if not content.startswith('---'):
            return None
        
        # Find closing ---
        lines = content.split('\n')
        end_idx = -1
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                end_idx = i
                break
        
        if end_idx == -1:
            return None
        
        # Parse YAML
        frontmatter_text = '\n'.join(lines[1:end_idx])
        try:
            # Sanitize Obsidian Templater expressions (<%...%>) before YAML parsing.
            # Unresolved templates like [[<% tp.date.now("YYYY-[W]ww") %>]] contain
            # brackets that PyYAML misinterprets as flow sequences.
            sanitized = re.sub(r'<%.*?%>', '', frontmatter_text)
            return yaml.safe_load(sanitized) or {}
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse frontmatter: {e}")
            return None
    
    def _extract_first_heading(self, content: str) -> Optional[str]:
        """
        Extract the first heading from markdown content.
        
        Args:
            content: Markdown file content
            
        Returns:
            First heading text, or None if no heading found
        """
        # Remove frontmatter first
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Find first heading (# Heading)
        match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _infer_domain_from_path(self, md_file: Path, root_path: Path) -> Optional[str]:
        """
        Infer domain from folder structure, mapped to configured domain IDs.
        
        Looks up the top-level folder name in the folder→domain_id mapping built
        from the user's domain config (loaded during build_index). Falls back to the
        raw folder name if no configured domain matches.
        
        Args:
            md_file: Path to markdown file
            root_path: Root notes directory
            
        Returns:
            Domain ID string, or None if at root level
        """
        try:
            relative = md_file.relative_to(root_path)
            parts = relative.parts
            
            if len(parts) > 1:
                folder = parts[0]
                # Only return a domain if the folder maps to a user-configured domain.
                # Never fall back to the raw folder name — that creates spurious
                # domain groups like "00-System", "30-Ideas", "20-Active", etc.
                mapping = getattr(self, '_folder_to_domain_id', {})
                return mapping.get(folder, None)
        except ValueError:
            pass
        
        return None
    
    def _add_note_to_index(self, note_info: NoteInfo):
        """
        Add a note to all index structures.
        
        Args:
            note_info: Note information to index
        """
        # Index by path
        self._notes_by_path[note_info.path] = note_info
        
        # Index by name (case-insensitive)
        name_key = note_info.name.lower()
        self._notes_by_name[name_key] = note_info
        
        # Index by aliases (case-insensitive)
        for alias in note_info.aliases:
            alias_key = alias.lower()
            self._notes_by_alias[alias_key] = note_info
    
    def find_note_by_name(self, name: str) -> Optional[NoteInfo]:
        """
        Find a note by its filename (without extension).
        
        Args:
            name: Note name to search for (case-insensitive)
            
        Returns:
            NoteInfo if found, None otherwise
        """
        return self._notes_by_name.get(name.lower())
    
    def find_note_by_alias(self, alias: str) -> Optional[NoteInfo]:
        """
        Find a note by one of its aliases.
        
        Args:
            alias: Alias to search for (case-insensitive)
            
        Returns:
            NoteInfo if found, None otherwise
        """
        return self._notes_by_alias.get(alias.lower())
    
    def find_note_by_name_or_alias(self, name: str) -> Optional[NoteInfo]:
        """
        Find a note by name or alias.
        
        Args:
            name: Note name or alias to search for
            
        Returns:
            NoteInfo if found, None otherwise
        """
        # Try name first
        result = self.find_note_by_name(name)
        if result:
            return result
        
        # Fall back to alias
        return self.find_note_by_alias(name)
    
    def get_note_by_path(self, path: Path) -> Optional[NoteInfo]:
        """
        Get note info by file path.
        
        Args:
            path: Path to note file
            
        Returns:
            NoteInfo if found, None otherwise
        """
        return self._notes_by_path.get(path.resolve())
    
    def get_all_notes(self) -> List[NoteInfo]:
        """
        Get all indexed notes.
        
        Returns:
            List of all NoteInfo objects, sorted by name
        """
        notes = list(self._notes_by_path.values())
        return sorted(notes, key=lambda n: n.name.lower())
    
    def get_notes_by_domain(self, domain: str) -> List[NoteInfo]:
        """
        Get all notes in a specific domain.
        
        Args:
            domain: Domain name to filter by
            
        Returns:
            List of NoteInfo objects in that domain
        """
        target = domain.strip().lower()
        results = []
        for note in self._notes_by_path.values():
            if not note.domain:
                continue
            # note.domain may be comma-separated (e.g. "sigils, signals")
            parts = [d.strip().lower() for d in note.domain.split(",")]
            if target in parts:
                results.append(note)
        return sorted(results, key=lambda n: n.name.lower())
    
    def search_notes(self, query: str, limit: int = 20) -> List[NoteInfo]:
        """
        Fuzzy search notes by name, alias, or title.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching NoteInfo objects, ranked by relevance
        """
        query_lower = query.lower()
        results = []
        
        for note in self._notes_by_path.values():
            score = 0
            
            # Exact name match
            if note.name.lower() == query_lower:
                score = 100
            # Name starts with query
            elif note.name.lower().startswith(query_lower):
                score = 90
            # Name contains query
            elif query_lower in note.name.lower():
                score = 70
            # Title contains query
            elif note.title and query_lower in note.title.lower():
                score = 60
            # Alias exact match
            elif any(alias.lower() == query_lower for alias in note.aliases):
                score = 85
            # Alias contains query
            elif any(query_lower in alias.lower() for alias in note.aliases):
                score = 65
            
            if score > 0:
                results.append((score, note))
        
        # Sort by score (descending) and return
        results.sort(key=lambda x: (-x[0], x[1].name.lower()))
        return [note for _, note in results[:limit]]
    
    def update_note(self, path: Path, root_path: Path) -> bool:
        """
        Update a single note in the index.
        
        Args:
            path: Path to the note file
            root_path: Root notes directory
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            # Remove old entry if exists
            self.remove_note(path)
            
            # Extract and add new info
            note_info = self._extract_note_info(path, root_path)
            self._add_note_to_index(note_info)
            
            logger.info(f"Updated note in index: {path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating note {path}: {e}")
            return False
    
    def remove_note(self, path: Path) -> bool:
        """
        Remove a note from the index.
        
        Args:
            path: Path to the note file
            
        Returns:
            True if removed, False if not found
        """
        path = path.resolve()
        note_info = self._notes_by_path.get(path)
        
        if not note_info:
            return False
        
        # Remove from all indices
        del self._notes_by_path[path]
        
        name_key = note_info.name.lower()
        if name_key in self._notes_by_name:
            del self._notes_by_name[name_key]
        
        for alias in note_info.aliases:
            alias_key = alias.lower()
            if alias_key in self._notes_by_alias:
                del self._notes_by_alias[alias_key]
        
        logger.info(f"Removed note from index: {path.name}")
        return True
    
    def clear(self):
        """Clear the entire index."""
        self._notes_by_path.clear()
        self._notes_by_name.clear()
        self._notes_by_alias.clear()
        self._last_build = None
        logger.info("Notes index cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Returns:
            Dictionary with index statistics
        """
        return {
            "total_notes": len(self._notes_by_path),
            "total_aliases": len(self._notes_by_alias),
            "notes_with_aliases": len([n for n in self._notes_by_path.values() if n.aliases]),
            "notes_with_domains": len([n for n in self._notes_by_path.values() if n.domain]),
            "notes_with_tags": len([n for n in self._notes_by_path.values() if n.tags]),
            "last_build": self._last_build.isoformat() if self._last_build else None
        }


# Global singleton instance
_global_index: Optional[NotesIndex] = None


def get_notes_index() -> NotesIndex:
    """
    Get the global notes index instance.
    
    Returns:
        Global NotesIndex singleton
    """
    global _global_index
    if _global_index is None:
        _global_index = NotesIndex()
    return _global_index

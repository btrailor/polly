"""
Tags Index System
Extracts and indexes tags from notes (frontmatter and inline).
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import logging
import re

from .notes_index import NotesIndex, NoteInfo

logger = logging.getLogger(__name__)


class TagsIndex:
    """
    Index system for tags across all notes.
    
    Extracts tags from:
    - Frontmatter (tags: [tag1, tag2])
    - Inline tags (#tag, #nested/tag)
    
    Maintains reverse index: tag -> list of notes that have that tag.
    """
    
    def __init__(self, notes_index: NotesIndex):
        """
        Initialize tags index.
        
        Args:
            notes_index: NotesIndex instance for accessing notes
        """
        self.notes_index = notes_index
        # Map from tag -> list of note paths
        self._tags_to_notes: Dict[str, List[Path]] = {}
        # Map from note path -> list of tags
        self._notes_to_tags: Dict[Path, List[str]] = {}
        self._last_build: Optional[datetime] = None
    
    def build_tags_index(self, notes_path: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Build the tags index by scanning all notes.
        
        Args:
            notes_path: Root directory containing notes
            recursive: Whether to scan subdirectories
            
        Returns:
            Statistics about the indexing operation:
            {
                "notes_scanned": int,
                "total_tags": int,
                "unique_tags": int,
                "frontmatter_tags": int,
                "inline_tags": int,
                "nested_tags": int,
                "duration_ms": float,
                "errors": List[str]
            }
        """
        start_time = datetime.now()
        stats = {
            "notes_scanned": 0,
            "total_tags": 0,
            "unique_tags": 0,
            "frontmatter_tags": 0,
            "inline_tags": 0,
            "nested_tags": 0,
            "errors": []
        }
        
        logger.info(f"Building tags index from {notes_path}")
        
        if not notes_path.exists():
            error_msg = f"Notes path does not exist: {notes_path}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats
        
        # Clear existing index
        self.clear()
        
        # Get all notes from notes index
        all_notes = self.notes_index.get_all_notes()
        
        logger.info(f"Scanning {len(all_notes)} notes for tags")
        
        for note_info in all_notes:
            try:
                # Extract tags from this note
                tags = self._extract_tags_from_note(note_info)
                
                if tags:
                    # Store in notes -> tags index
                    self._notes_to_tags[note_info.path] = tags
                    
                    # Store in tags -> notes index
                    for tag in tags:
                        if tag not in self._tags_to_notes:
                            self._tags_to_notes[tag] = []
                        self._tags_to_notes[tag].append(note_info.path)
                    
                    stats["total_tags"] += len(tags)
                    
                    # Count tag types
                    for tag in tags:
                        if '/' in tag:
                            stats["nested_tags"] += 1
                
                stats["notes_scanned"] += 1
                
            except Exception as e:
                error_msg = f"Error extracting tags from {note_info.name}: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
        
        stats["unique_tags"] = len(self._tags_to_notes)
        
        self._last_build = datetime.now()
        duration_ms = (self._last_build - start_time).total_seconds() * 1000
        stats["duration_ms"] = round(duration_ms, 2)
        
        logger.info(
            f"Tags index built: {stats['unique_tags']} unique tags "
            f"({stats['total_tags']} total) in {stats['duration_ms']}ms"
        )
        
        return stats
    
    def _extract_tags_from_note(self, note_info: NoteInfo) -> List[str]:
        """
        Extract all tags from a note (frontmatter and inline).
        
        Args:
            note_info: Note to extract tags from
            
        Returns:
            List of unique tags (lowercased, normalized)
        """
        tags = set()
        
        try:
            with open(note_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {note_info.path}: {e}")
            return []
        
        # Add tags from frontmatter (already extracted by notes_index)
        if note_info.tags:
            for tag in note_info.tags:
                # Normalize tag (lowercase, remove # if present)
                normalized = self._normalize_tag(tag)
                if normalized:
                    tags.add(normalized)
        
        # Extract inline tags
        inline_tags = self.extract_inline_tags(content)
        tags.update(inline_tags)
        
        return sorted(list(tags))
    
    def extract_inline_tags(self, content: str) -> List[str]:
        """
        Extract inline tags from markdown content.
        
        Supports:
        - Simple tags: #tag
        - Nested tags: #parent/child
        - Tags with hyphens: #multi-word-tag
        
        Does NOT match:
        - Tags in code blocks
        - Tags in inline code
        - Markdown headings (# Heading)
        - Numbers (#123)
        
        Args:
            content: Markdown file content
            
        Returns:
            List of normalized tags
        """
        tags = set()
        
        # Remove frontmatter first
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2]
        
        # Remove code blocks (```...```)
        content = re.sub(r'```[\s\S]*?```', '', content)
        
        # Remove inline code (`...`)
        content = re.sub(r'`[^`]+`', '', content)
        
        # Pattern for inline tags:
        # (?<!\S)   - Not preceded by non-whitespace (ensures word boundary)
        # #         - Hash symbol
        # ([a-zA-Z] - Must start with letter
        # [\w/-]+)  - Followed by word chars, hyphens, or slashes
        # (?!\w)    - Not followed by word char (ensures word boundary)
        pattern = r'(?<!\S)#([a-zA-Z][\w/-]+)(?!\w)'
        
        for match in re.finditer(pattern, content):
            tag = match.group(1)
            
            # Normalize and add
            normalized = self._normalize_tag(tag)
            if normalized:
                tags.add(normalized)
        
        return sorted(list(tags))
    
    def _normalize_tag(self, tag: str) -> str:
        """
        Normalize a tag.
        
        Args:
            tag: Raw tag string
            
        Returns:
            Normalized tag (lowercase, without leading #)
        """
        # Remove leading #
        if tag.startswith('#'):
            tag = tag[1:]
        
        # Lowercase
        tag = tag.lower()
        
        # Remove trailing slash if present
        tag = tag.rstrip('/')
        
        return tag.strip()
    
    def get_notes_by_tag(self, tag: str) -> List[NoteInfo]:
        """
        Get all notes that have a specific tag.
        
        Args:
            tag: Tag to search for (case-insensitive, with or without #)
            
        Returns:
            List of NoteInfo objects, sorted by name
        """
        normalized_tag = self._normalize_tag(tag)
        note_paths = self._tags_to_notes.get(normalized_tag, [])
        
        notes = []
        for path in note_paths:
            note_info = self.notes_index.get_note_by_path(path)
            if note_info:
                notes.append(note_info)
        
        return sorted(notes, key=lambda n: n.name.lower())
    
    def get_tags_for_note(self, note_name: str) -> List[str]:
        """
        Get all tags for a specific note.
        
        Args:
            note_name: Name of the note
            
        Returns:
            List of tags (sorted)
        """
        note_info = self.notes_index.find_note_by_name_or_alias(note_name)
        
        if not note_info:
            return []
        
        return self._notes_to_tags.get(note_info.path, [])
    
    def get_tags_for_note_by_path(self, path: Path) -> List[str]:
        """
        Get all tags for a note by its file path.
        
        Args:
            path: Path to the note
            
        Returns:
            List of tags (sorted)
        """
        return self._notes_to_tags.get(path.resolve(), [])
    
    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags across all notes.
        
        Returns:
            List of all tags, sorted alphabetically
        """
        return sorted(self._tags_to_notes.keys())
    
    def get_tag_hierarchy(self) -> Dict[str, Any]:
        """
        Get tag hierarchy for nested tags.
        
        Returns nested structure:
        {
            "parent": {
                "count": 5,
                "children": {
                    "child1": {"count": 3, "children": {}},
                    "child2": {"count": 2, "children": {}}
                }
            }
        }
        """
        hierarchy = {}
        
        for tag in self._tags_to_notes.keys():
            parts = tag.split('/')
            current = hierarchy
            
            for i, part in enumerate(parts):
                if part not in current:
                    current[part] = {"count": 0, "children": {}}
                
                # Count notes with this exact tag or subtags
                if i == len(parts) - 1:
                    # This is the leaf - count exact matches
                    current[part]["count"] = len(self._tags_to_notes[tag])
                else:
                    # This is a parent - count all notes with this prefix
                    prefix = '/'.join(parts[:i+1])
                    matching_tags = [t for t in self._tags_to_notes.keys() if t.startswith(prefix)]
                    note_paths = set()
                    for t in matching_tags:
                        note_paths.update(self._tags_to_notes[t])
                    current[part]["count"] = len(note_paths)
                
                current = current[part]["children"]
        
        return hierarchy
    
    def get_related_tags(self, tag: str, limit: int = 10) -> List[tuple[str, int]]:
        """
        Get tags that frequently appear together with the given tag.
        
        Args:
            tag: Tag to find related tags for
            limit: Maximum number of related tags to return
            
        Returns:
            List of (tag, co-occurrence_count) tuples, sorted by count descending
        """
        normalized_tag = self._normalize_tag(tag)
        note_paths = self._tags_to_notes.get(normalized_tag, [])
        
        if not note_paths:
            return []
        
        # Count co-occurrences
        co_occurrences: Dict[str, int] = {}
        
        for path in note_paths:
            note_tags = self._notes_to_tags.get(path, [])
            for other_tag in note_tags:
                if other_tag != normalized_tag:
                    co_occurrences[other_tag] = co_occurrences.get(other_tag, 0) + 1
        
        # Sort by count descending
        sorted_tags = sorted(co_occurrences.items(), key=lambda x: (-x[1], x[0]))
        
        return sorted_tags[:limit]
    
    def get_most_used_tags(self, limit: int = 20) -> List[tuple[str, int]]:
        """
        Get the most frequently used tags.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List of (tag, note_count) tuples, sorted by count descending
        """
        tag_counts = [(tag, len(paths)) for tag, paths in self._tags_to_notes.items()]
        tag_counts.sort(key=lambda x: (-x[1], x[0]))
        
        return tag_counts[:limit]
    
    def search_tags(self, query: str, limit: int = 20) -> List[str]:
        """
        Search tags by prefix or substring.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching tags, ranked by relevance
        """
        query_lower = query.lower().lstrip('#')
        results = []
        
        for tag in self._tags_to_notes.keys():
            score = 0
            
            # Exact match
            if tag == query_lower:
                score = 100
            # Starts with query
            elif tag.startswith(query_lower):
                score = 90
            # Contains query
            elif query_lower in tag:
                score = 70
            # Nested tag part matches
            elif any(part.startswith(query_lower) for part in tag.split('/')):
                score = 60
            
            if score > 0:
                results.append((score, tag))
        
        # Sort by score descending, then alphabetically
        results.sort(key=lambda x: (-x[0], x[1]))
        
        return [tag for _, tag in results[:limit]]
    
    def update_note_tags(self, path: Path) -> bool:
        """
        Update tags for a single note.
        
        Args:
            path: Path to the note
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            path = path.resolve()
            
            # Get note info
            note_info = self.notes_index.get_note_by_path(path)
            if not note_info:
                logger.warning(f"Note not in index: {path}")
                return False
            
            # Remove old tags
            old_tags = self._notes_to_tags.get(path, [])
            for tag in old_tags:
                if tag in self._tags_to_notes:
                    self._tags_to_notes[tag] = [
                        p for p in self._tags_to_notes[tag] if p != path
                    ]
                    # Remove tag entry if no more notes
                    if not self._tags_to_notes[tag]:
                        del self._tags_to_notes[tag]
            
            # Extract new tags
            new_tags = self._extract_tags_from_note(note_info)
            
            # Update indices
            if new_tags:
                self._notes_to_tags[path] = new_tags
                
                for tag in new_tags:
                    if tag not in self._tags_to_notes:
                        self._tags_to_notes[tag] = []
                    self._tags_to_notes[tag].append(path)
            elif path in self._notes_to_tags:
                del self._notes_to_tags[path]
            
            logger.info(f"Updated tags for: {note_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating tags for {path}: {e}")
            return False
    
    def remove_note_tags(self, path: Path) -> bool:
        """
        Remove all tags for a note.
        
        Args:
            path: Path to the note
            
        Returns:
            True if removed, False if not found
        """
        path = path.resolve()
        
        # Get old tags
        old_tags = self._notes_to_tags.get(path, [])
        
        if not old_tags:
            return False
        
        # Remove from tags -> notes index
        for tag in old_tags:
            if tag in self._tags_to_notes:
                self._tags_to_notes[tag] = [
                    p for p in self._tags_to_notes[tag] if p != path
                ]
                # Remove tag entry if no more notes
                if not self._tags_to_notes[tag]:
                    del self._tags_to_notes[tag]
        
        # Remove from notes -> tags index
        del self._notes_to_tags[path]
        
        logger.info(f"Removed tags for: {path.name}")
        return True
    
    def clear(self):
        """Clear the entire tags index."""
        self._tags_to_notes.clear()
        self._notes_to_tags.clear()
        self._last_build = None
        logger.info("Tags index cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the tags index.
        
        Returns:
            Dictionary with tags statistics
        """
        total_tags = sum(len(tags) for tags in self._notes_to_tags.values())
        nested_tags = len([tag for tag in self._tags_to_notes.keys() if '/' in tag])
        
        return {
            "total_tags": total_tags,
            "unique_tags": len(self._tags_to_notes),
            "nested_tags": nested_tags,
            "notes_with_tags": len(self._notes_to_tags),
            "last_build": self._last_build.isoformat() if self._last_build else None
        }


# Global singleton instance
_global_tags_index: Optional[TagsIndex] = None


def get_tags_index(notes_index: NotesIndex) -> TagsIndex:
    """
    Get the global tags index instance.
    
    Args:
        notes_index: NotesIndex instance to use
        
    Returns:
        Global TagsIndex singleton
    """
    global _global_tags_index
    if _global_tags_index is None:
        _global_tags_index = TagsIndex(notes_index)
    return _global_tags_index

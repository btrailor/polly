"""
Backlinks System
Tracks which notes link to which notes via wiki-links.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import re

from .notes_index import NotesIndex, NoteInfo

logger = logging.getLogger(__name__)


@dataclass
class Backlink:
    """Information about a backlink from one note to another."""
    
    source_path: Path  # Note that contains the link
    source_name: str  # Name of the source note
    target_name: str  # Name or alias of the linked note
    line_number: Optional[int] = None  # Line where the link appears
    context: str = ""  # Surrounding text for preview
    link_type: str = "wiki"  # "wiki", "embed", "heading"
    heading: Optional[str] = None  # If linking to a specific heading


class BacklinksIndex:
    """
    Tracks backlinks between notes.
    
    Parses markdown files for wiki-links [[Note Name]] and maintains
    a reverse index showing which notes link to each note.
    """
    
    def __init__(self, notes_index: NotesIndex):
        """
        Initialize backlinks index.
        
        Args:
            notes_index: NotesIndex instance for resolving note names/aliases
        """
        self.notes_index = notes_index
        # Map from target note path -> list of backlinks
        self._backlinks: Dict[Path, List[Backlink]] = {}
        # Map from source note path -> list of outgoing links
        self._outgoing_links: Dict[Path, List[Backlink]] = {}
        self._last_build: Optional[datetime] = None
    
    def build_backlinks(self, notes_path: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Build the backlinks index by scanning all notes.
        
        Args:
            notes_path: Root directory containing notes
            recursive: Whether to scan subdirectories
            
        Returns:
            Statistics about the indexing operation:
            {
                "notes_scanned": int,
                "backlinks_found": int,
                "wiki_links": int,
                "embeds": int,
                "heading_links": int,
                "duration_ms": float,
                "errors": List[str]
            }
        """
        start_time = datetime.now()
        stats = {
            "notes_scanned": 0,
            "backlinks_found": 0,
            "wiki_links": 0,
            "embeds": 0,
            "heading_links": 0,
            "errors": []
        }
        
        logger.info(f"Building backlinks index from {notes_path}")
        
        if not notes_path.exists():
            error_msg = f"Notes path does not exist: {notes_path}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)
            return stats
        
        # Clear existing index
        self.clear()
        
        # Get all notes from notes index
        all_notes = self.notes_index.get_all_notes()
        
        logger.info(f"Scanning {len(all_notes)} notes for backlinks")
        
        for note_info in all_notes:
            try:
                backlinks = self._extract_backlinks(note_info)
                
                # Add to outgoing links index
                if backlinks:
                    self._outgoing_links[note_info.path] = backlinks
                
                # Add to backlinks index (reverse)
                for backlink in backlinks:
                    # Resolve target note
                    target_note = self.notes_index.find_note_by_name_or_alias(backlink.target_name)
                    
                    if target_note:
                        if target_note.path not in self._backlinks:
                            self._backlinks[target_note.path] = []
                        
                        self._backlinks[target_note.path].append(backlink)
                        stats["backlinks_found"] += 1
                        
                        # Count by type
                        if backlink.link_type == "wiki":
                            stats["wiki_links"] += 1
                        elif backlink.link_type == "embed":
                            stats["embeds"] += 1
                        elif backlink.link_type == "heading":
                            stats["heading_links"] += 1
                
                stats["notes_scanned"] += 1
                
            except Exception as e:
                error_msg = f"Error extracting backlinks from {note_info.name}: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
        
        self._last_build = datetime.now()
        duration_ms = (self._last_build - start_time).total_seconds() * 1000
        stats["duration_ms"] = round(duration_ms, 2)
        
        logger.info(
            f"Backlinks index built: {stats['backlinks_found']} links "
            f"in {stats['duration_ms']}ms"
        )
        
        return stats
    
    def _extract_backlinks(self, note_info: NoteInfo) -> List[Backlink]:
        """
        Extract all backlinks from a single note.
        
        Args:
            note_info: Note to extract backlinks from
            
        Returns:
            List of Backlink objects
        """
        backlinks = []
        
        try:
            with open(note_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {note_info.path}: {e}")
            return backlinks
        
        # Extract wiki-links
        wiki_links = self.extract_wiki_links(content)
        
        for link_info in wiki_links:
            backlink = Backlink(
                source_path=note_info.path,
                source_name=note_info.name,
                target_name=link_info["target"],
                line_number=link_info.get("line_number"),
                context=link_info.get("context", ""),
                link_type=link_info["type"],
                heading=link_info.get("heading")
            )
            backlinks.append(backlink)
        
        return backlinks
    
    def extract_wiki_links(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract all wiki-links from markdown content.
        
        Supports:
        - Basic links: [[Note Name]]
        - Links with display text: [[Note Name|Display Text]]
        - Heading links: [[Note Name#Heading]]
        - Embeds: ![[Note Name]]
        
        Args:
            content: Markdown file content
            
        Returns:
            List of dictionaries with link information:
            {
                "target": str,  # Note name
                "display": Optional[str],  # Display text if provided
                "heading": Optional[str],  # Heading if specified
                "type": str,  # "wiki", "embed", "heading"
                "line_number": int,
                "context": str  # Surrounding text
            }
        """
        links = []
        
        # Split into lines for context
        lines = content.split('\n')
        
        # Pattern for wiki-links:
        # !?        - Optional ! for embeds
        # \[\[      - Opening [[
        # ([^\]]+?) - Capture note name/path (non-greedy)
        # \]\]      - Closing ]]
        pattern = r'(!?)\[\[([^\]]+?)\]\]'
        
        for line_num, line in enumerate(lines, start=1):
            for match in re.finditer(pattern, line):
                is_embed = match.group(1) == '!'
                link_content = match.group(2)
                
                # Parse link content
                # Format: Note Name|Display Text
                # Or: Note Name#Heading
                # Or: Note Name#Heading|Display Text
                
                display_text = None
                heading = None
                target = link_content
                
                # Check for display text (|)
                if '|' in link_content:
                    parts = link_content.split('|', 1)
                    target = parts[0]
                    display_text = parts[1]
                
                # Check for heading (#)
                if '#' in target:
                    parts = target.split('#', 1)
                    target = parts[0]
                    heading = parts[1]
                
                # Clean up target (remove leading/trailing whitespace)
                target = target.strip()
                
                # Determine link type
                if is_embed:
                    link_type = "embed"
                elif heading:
                    link_type = "heading"
                else:
                    link_type = "wiki"
                
                # Get context (surrounding text)
                context_start = max(0, match.start() - 40)
                context_end = min(len(line), match.end() + 40)
                context = line[context_start:context_end].strip()
                
                link_info = {
                    "target": target,
                    "display": display_text,
                    "heading": heading,
                    "type": link_type,
                    "line_number": line_num,
                    "context": context
                }
                
                links.append(link_info)
        
        return links
    
    def get_backlinks(self, note_name: str) -> List[Backlink]:
        """
        Get all backlinks to a specific note.
        
        Args:
            note_name: Name of the note (or alias)
            
        Returns:
            List of Backlink objects pointing to this note
        """
        # Resolve note name/alias to actual note
        note_info = self.notes_index.find_note_by_name_or_alias(note_name)
        
        if not note_info:
            return []
        
        return self._backlinks.get(note_info.path, [])
    
    def get_backlinks_by_path(self, path: Path) -> List[Backlink]:
        """
        Get all backlinks to a note by its file path.
        
        Args:
            path: Path to the note
            
        Returns:
            List of Backlink objects pointing to this note
        """
        return self._backlinks.get(path.resolve(), [])
    
    def get_outgoing_links(self, note_name: str) -> List[Backlink]:
        """
        Get all outgoing links from a specific note.
        
        Args:
            note_name: Name of the note
            
        Returns:
            List of Backlink objects originating from this note
        """
        note_info = self.notes_index.find_note_by_name_or_alias(note_name)
        
        if not note_info:
            return []
        
        return self._outgoing_links.get(note_info.path, [])
    
    def get_outgoing_links_by_path(self, path: Path) -> List[Backlink]:
        """
        Get all outgoing links from a note by its file path.
        
        Args:
            path: Path to the note
            
        Returns:
            List of Backlink objects originating from this note
        """
        return self._outgoing_links.get(path.resolve(), [])
    
    def get_orphaned_notes(self) -> List[NoteInfo]:
        """
        Get all notes that have no incoming or outgoing links.
        
        Returns:
            List of NoteInfo objects for orphaned notes
        """
        all_notes = self.notes_index.get_all_notes()
        orphaned = []
        
        for note in all_notes:
            has_backlinks = note.path in self._backlinks
            has_outgoing = note.path in self._outgoing_links
            
            if not has_backlinks and not has_outgoing:
                orphaned.append(note)
        
        return orphaned
    
    def get_most_linked_notes(self, limit: int = 20) -> List[tuple[NoteInfo, int]]:
        """
        Get notes with the most backlinks.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of (NoteInfo, backlink_count) tuples, sorted by count descending
        """
        counts = []
        
        for path, backlinks in self._backlinks.items():
            note_info = self.notes_index.get_note_by_path(path)
            if note_info:
                counts.append((note_info, len(backlinks)))
        
        # Sort by count descending
        counts.sort(key=lambda x: x[1], reverse=True)
        
        return counts[:limit]
    
    def update_note_backlinks(self, path: Path) -> bool:
        """
        Update backlinks for a single note.
        
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
            
            # Remove old backlinks from this note
            old_outgoing = self._outgoing_links.get(path, [])
            for old_link in old_outgoing:
                target_note = self.notes_index.find_note_by_name_or_alias(old_link.target_name)
                if target_note and target_note.path in self._backlinks:
                    # Remove this backlink from target's backlink list
                    self._backlinks[target_note.path] = [
                        bl for bl in self._backlinks[target_note.path]
                        if bl.source_path != path
                    ]
            
            # Extract new backlinks
            new_backlinks = self._extract_backlinks(note_info)
            
            # Update outgoing links
            if new_backlinks:
                self._outgoing_links[path] = new_backlinks
            elif path in self._outgoing_links:
                del self._outgoing_links[path]
            
            # Update backlinks index
            for backlink in new_backlinks:
                target_note = self.notes_index.find_note_by_name_or_alias(backlink.target_name)
                if target_note:
                    if target_note.path not in self._backlinks:
                        self._backlinks[target_note.path] = []
                    self._backlinks[target_note.path].append(backlink)
            
            logger.info(f"Updated backlinks for: {note_info.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating backlinks for {path}: {e}")
            return False
    
    def remove_note_backlinks(self, path: Path) -> bool:
        """
        Remove all backlinks associated with a note.
        
        Args:
            path: Path to the note
            
        Returns:
            True if removed, False if not found
        """
        path = path.resolve()
        
        # Remove from backlinks (as target)
        removed_target = path in self._backlinks
        if removed_target:
            del self._backlinks[path]
        
        # Remove from outgoing links (as source)
        old_outgoing = self._outgoing_links.get(path, [])
        if old_outgoing:
            # Remove from targets' backlink lists
            for link in old_outgoing:
                target_note = self.notes_index.find_note_by_name_or_alias(link.target_name)
                if target_note and target_note.path in self._backlinks:
                    self._backlinks[target_note.path] = [
                        bl for bl in self._backlinks[target_note.path]
                        if bl.source_path != path
                    ]
            
            del self._outgoing_links[path]
        
        if removed_target or old_outgoing:
            logger.info(f"Removed backlinks for: {path.name}")
            return True
        
        return False
    
    def clear(self):
        """Clear the entire backlinks index."""
        self._backlinks.clear()
        self._outgoing_links.clear()
        self._last_build = None
        logger.info("Backlinks index cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the backlinks index.
        
        Returns:
            Dictionary with backlinks statistics
        """
        total_backlinks = sum(len(links) for links in self._backlinks.values())
        total_outgoing = sum(len(links) for links in self._outgoing_links.values())
        
        notes_with_backlinks = len(self._backlinks)
        notes_with_outgoing = len(self._outgoing_links)
        
        return {
            "total_backlinks": total_backlinks,
            "total_outgoing": total_outgoing,
            "notes_with_backlinks": notes_with_backlinks,
            "notes_with_outgoing": notes_with_outgoing,
            "orphaned_notes": len(self.get_orphaned_notes()),
            "last_build": self._last_build.isoformat() if self._last_build else None
        }


# Global singleton instance
_global_backlinks_index: Optional[BacklinksIndex] = None


def get_backlinks_index(notes_index: NotesIndex) -> BacklinksIndex:
    """
    Get the global backlinks index instance.
    
    Args:
        notes_index: NotesIndex instance to use
        
    Returns:
        Global BacklinksIndex singleton
    """
    global _global_backlinks_index
    if _global_backlinks_index is None:
        _global_backlinks_index = BacklinksIndex(notes_index)
    return _global_backlinks_index

"""
Unlinked Mentions Detection
Scans note content for plain-text references to other note names/titles
that aren't wrapped in [[wikilinks]].
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import logging
import re

from .notes_index import NotesIndex, NoteInfo

logger = logging.getLogger(__name__)


@dataclass
class Mention:
    """A plain-text mention of a note name found in another note's content."""
    
    source_name: str      # Note containing the mention
    target_name: str      # Note name being mentioned
    line_number: int      # Line where the mention occurs
    context: str          # Surrounding text (for preview)
    matched_text: str     # The actual text that matched


class UnlinkedMentionsIndex:
    """
    Detects plain-text references to note names in note content.
    
    Finds cases where a note's content mentions another note's name or title
    without using [[wikilink]] syntax — indicating a connection that exists
    semantically but isn't explicitly linked.
    """
    
    MIN_NAME_LENGTH = 4  # Skip very short names to avoid false positives
    
    def __init__(self, notes_index: NotesIndex):
        self.notes_index = notes_index
        # target_name -> list of mentions pointing TO this note
        self._inbound_mentions: Dict[str, List[Mention]] = {}
        # source_name -> list of mentions FROM this note
        self._outbound_mentions: Dict[str, List[Mention]] = {}
        self._last_build: Optional[datetime] = None
    
    def build(self, notes_path: Path) -> Dict:
        """
        Scan all notes for unlinked mentions of other note names.
        
        Returns:
            Statistics about the scan.
        """
        start_time = datetime.now()
        stats = {
            "notes_scanned": 0,
            "mentions_found": 0,
            "notes_with_mentions": 0,
            "errors": []
        }
        
        logger.info("Building unlinked mentions index")
        
        # Clear existing
        self._inbound_mentions.clear()
        self._outbound_mentions.clear()
        
        all_notes = self.notes_index.get_all_notes()
        if not all_notes:
            return stats
        
        # Build search targets: note names, titles, and aliases (min length filter)
        # Map from lowercase search term -> canonical note name
        search_targets: Dict[str, str] = {}
        for note in all_notes:
            # Add note name
            if len(note.name) >= self.MIN_NAME_LENGTH:
                search_targets[note.name.lower()] = note.name
            
            # Add title if different from name
            if note.title and note.title != note.name and len(note.title) >= self.MIN_NAME_LENGTH:
                search_targets[note.title.lower()] = note.name
            
            # Add aliases
            for alias in note.aliases:
                if len(alias) >= self.MIN_NAME_LENGTH:
                    search_targets[alias.lower()] = note.name
        
        if not search_targets:
            return stats
        
        # Build regex patterns for efficient matching
        # Sort by length descending so longer matches take priority
        sorted_terms = sorted(search_targets.keys(), key=len, reverse=True)
        
        # Escape regex special chars and build word-boundary pattern
        patterns = []
        for term in sorted_terms:
            escaped = re.escape(term)
            # Use word boundaries to avoid partial matches
            patterns.append(escaped)
        
        # Compile into one big alternation pattern (case-insensitive)
        if not patterns:
            return stats
        
        # Process in chunks to avoid regex too large errors
        CHUNK_SIZE = 50
        pattern_chunks = []
        for i in range(0, len(patterns), CHUNK_SIZE):
            chunk = patterns[i:i + CHUNK_SIZE]
            combined = r'\b(?:' + '|'.join(chunk) + r')\b'
            pattern_chunks.append(re.compile(combined, re.IGNORECASE))
        
        # Scan each note's content
        for note in all_notes:
            try:
                if not note.path.exists():
                    continue
                
                content = note.path.read_text(encoding='utf-8', errors='replace')
                stats["notes_scanned"] += 1
                
                # Strip frontmatter
                content_body = self._strip_frontmatter(content)
                
                # Strip code blocks
                content_body = self._strip_code_blocks(content_body)
                
                # Strip existing wikilinks (we only want UNlinked mentions)
                content_body = self._strip_wikilinks(content_body)
                
                # Search for mentions
                lines = content_body.split('\n')
                found_in_note = False
                
                for line_num, line in enumerate(lines, start=1):
                    for pattern in pattern_chunks:
                        for match in pattern.finditer(line):
                            matched_text = match.group(0)
                            target_name = search_targets.get(matched_text.lower())
                            
                            if not target_name:
                                continue
                            
                            # Skip self-references
                            if target_name == note.name:
                                continue
                            
                            # Build context snippet
                            ctx_start = max(0, match.start() - 30)
                            ctx_end = min(len(line), match.end() + 30)
                            context = line[ctx_start:ctx_end].strip()
                            
                            mention = Mention(
                                source_name=note.name,
                                target_name=target_name,
                                line_number=line_num,
                                context=context,
                                matched_text=matched_text
                            )
                            
                            # Store inbound (mentions OF target)
                            if target_name not in self._inbound_mentions:
                                self._inbound_mentions[target_name] = []
                            self._inbound_mentions[target_name].append(mention)
                            
                            # Store outbound (mentions FROM source)
                            if note.name not in self._outbound_mentions:
                                self._outbound_mentions[note.name] = []
                            self._outbound_mentions[note.name].append(mention)
                            
                            stats["mentions_found"] += 1
                            found_in_note = True
                
                if found_in_note:
                    stats["notes_with_mentions"] += 1
                    
            except Exception as e:
                error_msg = f"Error scanning {note.name}: {e}"
                logger.debug(error_msg)
                stats["errors"].append(error_msg)
        
        self._last_build = datetime.now()
        duration = (self._last_build - start_time).total_seconds() * 1000
        stats["duration_ms"] = round(duration, 1)
        
        logger.info(
            f"Unlinked mentions index built: {stats['mentions_found']} mentions "
            f"across {stats['notes_with_mentions']} notes in {stats['duration_ms']}ms"
        )
        
        return stats
    
    def get_mentions_of(self, note_name: str) -> List[Mention]:
        """Get all notes that mention this note name in their text."""
        return self._inbound_mentions.get(note_name, [])
    
    def get_mentions_from(self, note_name: str) -> List[Mention]:
        """Get all note names mentioned in this note's text."""
        return self._outbound_mentions.get(note_name, [])
    
    def get_all_mention_pairs(self) -> List[tuple]:
        """
        Get all unique (source, target) pairs for edge building.
        
        Returns:
            List of (source_name, target_name, mention_count) tuples
        """
        pair_counts: Dict[tuple, int] = {}
        for target, mentions in self._inbound_mentions.items():
            for m in mentions:
                key = (m.source_name, target)
                pair_counts[key] = pair_counts.get(key, 0) + 1
        
        return [(s, t, c) for (s, t), c in pair_counts.items()]
    
    def _strip_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        if not content.startswith('---'):
            return content
        lines = content.split('\n')
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                return '\n'.join(lines[i + 1:])
        return content
    
    def _strip_code_blocks(self, content: str) -> str:
        """Remove fenced code blocks."""
        return re.sub(r'```[\s\S]*?```', '', content)
    
    def _strip_wikilinks(self, content: str) -> str:
        """Remove [[wikilink]] content so we only find UNlinked mentions."""
        return re.sub(r'\[\[([^\]]+?)\]\]', '', content)


# Global singleton
_global_mentions_index: Optional[UnlinkedMentionsIndex] = None


def get_unlinked_mentions_index(notes_index: NotesIndex) -> UnlinkedMentionsIndex:
    """Get the global unlinked mentions index instance."""
    global _global_mentions_index
    if _global_mentions_index is None:
        _global_mentions_index = UnlinkedMentionsIndex(notes_index)
    return _global_mentions_index

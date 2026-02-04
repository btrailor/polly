"""
Knowledge Base Deduplication System
Prevents duplicate notes by detecting semantic similarity before creation.
Works with native Polly notes system.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class SimilarNote:
    """A note that's similar to proposed content."""
    path: str          # Full file path
    name: str          # Note filename without extension
    title: str         # Display title
    domain: str        # Folder/domain name
    similarity: float  # 0.0 - 1.0
    snippet: str       # Most relevant excerpt (200 chars)
    
    def to_dict(self):
        """Convert to dict for JSON serialization."""
        return asdict(self)


class DeduplicationEngine:
    """Detects duplicate/similar content in knowledge base using RAG."""
    
    def __init__(self, rag_system, notes_index, config=None):
        """
        Initialize deduplication engine.
        
        Args:
            rag_system: UnifiedRAG instance for semantic search
            notes_index: NotesIndex instance for note metadata
            config: Optional PollyConfig instance for settings
        """
        self.rag = rag_system
        self.notes_index = notes_index
        self.config = config
        logger.info("DeduplicationEngine initialized")
    
    def check_similarity(
        self,
        content: str,
        title: str,
        similarity_threshold: float = None,
        max_results: int = None
    ) -> List[SimilarNote]:
        """
        Check if proposed note is similar to existing notes.
        
        Args:
            content: Proposed note content
            title: Proposed note title
            similarity_threshold: Min similarity to flag (default from config or 0.70)
            max_results: Maximum number of similar notes to return (default from config or 5)
        
        Returns:
            List of similar notes with scores, sorted by similarity
        """
        # Use config defaults if not specified
        if similarity_threshold is None:
            similarity_threshold = self.config.get('deduplication.similarity_threshold', 0.70) if self.config else 0.70
        if max_results is None:
            max_results = self.config.get('deduplication.max_results', 5) if self.config else 5
        
        # Check if deduplication is enabled
        if self.config:
            enabled = self.config.get('deduplication.enabled', True)
            if not enabled:
                logger.info("Deduplication is disabled in config")
                return []
        
        # Validate inputs
        if not content or not title:
            logger.warning("Empty content or title, skipping duplicate check")
            return []
        
        # Check if RAG is available
        if not self.rag:
            logger.warning("RAG system not available, skipping duplicate check")
            return []
        
        # Check if NotesIndex is available
        if not self.notes_index:
            logger.warning("NotesIndex not available, skipping duplicate check")
            return []
        
        # Ensure notes index is populated (lazy initialization)
        if len(self.notes_index._notes_by_name) == 0:
            logger.info("Notes index is empty, building it now...")
            try:
                from core.notes_source_manager import NotesSourceManager
                mgr = NotesSourceManager()
                notes_path = Path(mgr.get_notes_path()).expanduser()
                self.notes_index.build_index(notes_path, recursive=True)
                logger.info(f"Notes index built: {len(self.notes_index._notes_by_name)} notes indexed")
            except Exception as e:
                logger.warning(f"Could not build notes index: {e}")
                return []
        
        try:
            # Search using RAG with generous n_results
            # Note: RAG.search() is synchronous, not async
            results = self.rag.search(
                query=f"{title}\n\n{content}",
                n_results=10,
                source_types=['notes']  # Only search notes collection
            )
            
            similar_notes = []
            
            for result in results:
                try:
                    # result is a SearchResult object with score and chunk
                    chunk = result.chunk
                    
                    # Use semantic score if available (from hybrid search breakdown)
                    # Otherwise use the result.score directly
                    breakdown = chunk.metadata.get('_hybrid_breakdown', {})
                    
                    if breakdown and isinstance(breakdown, dict) and 'semantic_score' in breakdown:
                        score = breakdown['semantic_score']
                    else:
                        score = result.score
                    
                    # Check if similarity exceeds threshold
                    if score >= similarity_threshold:
                        # Get note metadata from NotesIndex
                        # Note: filepath in chunk metadata is relative to notes root
                        filepath_str = chunk.metadata.get('filepath', '')
                        
                        # Extract note name from filepath (filename without extension)
                        # NotesIndex stores names in lowercase
                        note_name = Path(filepath_str).stem.lower()
                        note_info = self.notes_index.find_note_by_name(note_name)
                        
                        if note_info:
                            # Extract relevant snippet from the matched content
                            snippet = self._extract_snippet(
                                chunk.content,
                                max_length=200
                            )
                            
                            similar_notes.append(SimilarNote(
                                path=str(note_info.path),
                                name=note_info.name,
                                title=note_info.title or note_info.name,
                                domain=note_info.domain or 'Unknown',
                                similarity=score,
                                snippet=snippet
                            ))
                except Exception as e:
                    logger.warning(f"Error processing search result: {e}")
                    continue  # Skip this result, continue with others
            
            # Sort by similarity (highest first) and limit results
            similar_notes.sort(key=lambda x: x.similarity, reverse=True)
            similar_notes = similar_notes[:max_results]
            
            logger.info(f"Found {len(similar_notes)} similar notes for '{title}' (threshold: {similarity_threshold})")
            return similar_notes
            
        except Exception as e:
            logger.error(f"Duplicate check failed: {e}", exc_info=True)
            # Return empty list - dedup is nice-to-have, not blocking
            return []
    
    def _extract_snippet(self, content: str, max_length: int = 200) -> str:
        """
        Extract most relevant snippet from content.
        
        Args:
            content: Full content text
            max_length: Maximum snippet length
            
        Returns:
            Snippet string with ellipsis if truncated
        """
        # Strip frontmatter if present
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        # Strip markdown headers
        lines = content.split('\n')
        cleaned_lines = [l for l in lines if not l.strip().startswith('#')]
        cleaned_content = '\n'.join(cleaned_lines).strip()
        
        if len(cleaned_content) <= max_length:
            return cleaned_content
        
        # Truncate at word boundary
        truncated = cleaned_content[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > max_length * 0.8:  # Only if we're close to the limit
            truncated = truncated[:last_space]
        
        return truncated + "..."
    
    def suggest_links(
        self,
        similar_notes: List[SimilarNote]
    ) -> List[str]:
        """
        Suggest wikilinks to add to the new note.
        
        Args:
            similar_notes: List of similar notes
        
        Returns:
            List of wikilink strings: ["[[Note Name]]", ...]
        """
        links = []
        
        # Top 5 most similar notes become wikilinks
        for note in similar_notes[:5]:
            # Use the note name for wikilink (without extension)
            links.append(f"[[{note.name}]]")
        
        return links


# Global singleton instance
_dedup_engine = None


def get_dedup_engine():
    """Get the global deduplication engine instance."""
    return _dedup_engine


def init_dedup_engine(rag_system, notes_index, config=None):
    """
    Initialize the global deduplication engine.
    
    Args:
        rag_system: UnifiedRAG instance
        notes_index: NotesIndex instance
        config: Optional PollyConfig instance
        
    Returns:
        DeduplicationEngine instance
    """
    global _dedup_engine
    _dedup_engine = DeduplicationEngine(rag_system, notes_index, config)
    logger.info("Global deduplication engine initialized")
    return _dedup_engine

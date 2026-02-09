"""
Knowledge Writer — Chat-to-KB writing system.

Orchestrates all knowledge-base writes from chat, including:
- AI-suggested writes (gap detection after cloud synthesis)
- Per-message saves (context menu on assistant messages)
- Quick saves (no LLM call, structured formatting)
- Scribe-assisted saves (LLM enrichment via Scribe persona)

All write paths converge on a single _save_note() method that handles
native/Obsidian source selection, dedup, file write, and incremental RAG indexing.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import logging
import re

logger = logging.getLogger(__name__)


# ========== Data Types ==========

@dataclass
class KnowledgeGap:
    """Detected gap between local RAG knowledge and cloud response."""
    query: str
    gap_score: float            # 0.0-1.0, how much cloud added beyond RAG
    novel_concepts: List[str]   # Concepts from cloud not found in RAG
    suggested_title: str
    suggested_domain: str       # e.g. "sigils", "scrolls"
    suggested_tags: List[str]
    cloud_content: str          # The raw cloud response content
    cloud_provider: str         # Which provider answered (e.g. "anthropic")

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NoteCreateResult:
    """Result of a note creation operation."""
    success: bool
    note_path: str = ""
    title: str = ""
    domain: str = ""
    similar_notes: List[Dict] = field(default_factory=list)
    rag_indexed: bool = False
    source: str = "native"       # "native" or "obsidian"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ========== Domain Mapping ==========

DOMAIN_FOLDER_MAP = {
    "sigils": "01-Sigils",
    "signals": "02-Signals",
    "scrolls": "03-Scrolls",
    "glyphs": "04-Glyphs",
    "grids": "05-Grids",
}

FOLDER_DOMAIN_MAP = {v: k for k, v in DOMAIN_FOLDER_MAP.items()}


def _domain_to_folder(domain: str) -> str:
    """Convert a domain slug to its folder name."""
    lower = domain.lower()
    if lower in DOMAIN_FOLDER_MAP:
        return DOMAIN_FOLDER_MAP[lower]
    # Already a folder name like "01-Sigils"
    if domain in FOLDER_DOMAIN_MAP:
        return domain
    # Fallback: use as-is
    return domain


# ========== Knowledge Writer ==========

class KnowledgeWriter:
    """
    Orchestrates all knowledge-base writes from chat.

    Responsibilities:
    1. Detect knowledge gaps after synthesis (for AI suggestions)
    2. Generate structured notes from raw content (for quick saves)
    3. Coordinate with Scribe persona (for full pipeline saves)
    4. Save notes via the active notes source (native or Obsidian)
    5. Trigger RAG re-indexing after save
    6. Track write metrics for progressive autonomy
    """

    def __init__(
        self,
        config,
        notes_source_manager=None,
        rag=None,
        domain_engine=None,
        scribe_persona=None,
        metrics_tracker=None,
    ):
        self.config = config
        self.notes_source = notes_source_manager
        self.rag = rag
        self.domain_engine = domain_engine
        self.scribe = scribe_persona
        self.metrics_tracker = metrics_tracker

        # Load AI features config
        ai_features = {}
        if hasattr(config, 'get'):
            ai_features = config.get('ai_features', {}) or {}
        elif isinstance(config, dict):
            ai_features = config.get('ai_features', {}) or {}

        ks = ai_features.get('knowledge_suggestions', {}) or {}
        self.suggestions_enabled = ks.get('enabled', True)
        self.suggestion_style = ks.get('style', 'inline')
        self.min_gap_score = ks.get('min_gap_score', 0.5)

        logger.info(
            f"KnowledgeWriter initialized "
            f"(suggestions={'on' if self.suggestions_enabled else 'off'}, "
            f"style={self.suggestion_style}, "
            f"min_gap={self.min_gap_score})"
        )

    # ------------------------------------------------------------------
    # Gap Detection (called after synthesis)
    # ------------------------------------------------------------------

    async def detect_knowledge_gap(
        self,
        original_query: str,
        local_results: list,
        cloud_response: str,
        rag_coverage: float,
        cloud_provider: str = "unknown",
    ) -> Optional[KnowledgeGap]:
        """
        Compare what RAG provided vs what cloud provided.
        Returns a KnowledgeGap if cloud added substantial novel content.

        A gap is detected when:
        - Cloud was used (cloud_response is not empty)
        - RAG coverage for the query was below threshold
        - The cloud response contains concepts not found in local results
        """
        if not cloud_response or not cloud_response.strip():
            return None

        # If RAG coverage was high, the cloud likely didn't add much new
        if rag_coverage >= 0.8:
            return None

        # Extract concepts from cloud response (lightweight, no LLM call)
        cloud_concepts = self._extract_concepts(cloud_response)

        # Extract concepts already present in local results
        local_text = " ".join(
            getattr(r, 'content', '') or str(r) for r in (local_results or [])
        )
        local_concepts = self._extract_concepts(local_text)

        # Novel concepts = in cloud but not in local
        novel = [c for c in cloud_concepts if c.lower() not in {lc.lower() for lc in local_concepts}]

        if not novel:
            return None

        # Gap score: how much of the cloud response is truly novel
        # Simple heuristic: ratio of novel concepts to total cloud concepts
        gap_score = len(novel) / max(len(cloud_concepts), 1)
        gap_score = min(gap_score, 1.0)

        if gap_score < self.min_gap_score:
            return None

        # Auto-detect domain and generate title
        suggested_domain = self._auto_detect_domain(original_query + " " + cloud_response)
        suggested_title = self._generate_title(original_query, novel)
        suggested_tags = self._generate_tags(novel, suggested_domain)

        gap = KnowledgeGap(
            query=original_query,
            gap_score=gap_score,
            novel_concepts=novel[:10],  # Cap at 10
            suggested_title=suggested_title,
            suggested_domain=suggested_domain,
            suggested_tags=suggested_tags,
            cloud_content=cloud_response,
            cloud_provider=cloud_provider,
        )

        logger.info(
            f"Knowledge gap detected: score={gap_score:.2f}, "
            f"novel_concepts={len(novel)}, title='{suggested_title}'"
        )
        return gap

    # ------------------------------------------------------------------
    # Suggestion Generation
    # ------------------------------------------------------------------

    def create_suggestion(self, gap: KnowledgeGap) -> Optional[Dict[str, Any]]:
        """
        If suggestions are enabled, create a PersonaAction-compatible dict
        of type 'suggest_kb_write' with pre-computed metadata.

        Returns None if suggestions are disabled in config.
        The frontend renders this based on the configured style.
        """
        if not self.suggestions_enabled:
            return None

        return {
            "type": "suggest_kb_write",
            "data": {
                "style": self.suggestion_style,
                "gap": gap.to_dict(),
                "suggested_title": gap.suggested_title,
                "suggested_domain": gap.suggested_domain,
                "suggested_tags": gap.suggested_tags,
                "novel_concepts": gap.novel_concepts,
                "cloud_provider": gap.cloud_provider,
                "gap_score": gap.gap_score,
            }
        }

    # ------------------------------------------------------------------
    # Quick Save (no LLM call)
    # ------------------------------------------------------------------

    async def quick_save(
        self,
        content: str,
        title: str,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_type: str = "cloud_response",
        conversation_id: Optional[str] = None,
    ) -> NoteCreateResult:
        """
        Generate a structured note without an LLM call.
        Uses templates and heuristics to format the content.

        Steps:
        1. Auto-detect domain if not provided
        2. Generate frontmatter (title, date, tags, domain, source)
        3. Wrap content in appropriate markdown structure
        4. Check for duplicates via notes_dedup
        5. Save via active notes source
        6. Trigger RAG re-index for the new note
        7. Record metric: knowledge_write_count++
        """
        if not content or not content.strip():
            return NoteCreateResult(success=False, error="Content is empty")

        # 1. Auto-detect domain
        if not domain:
            domain = self._auto_detect_domain(content)
        folder = _domain_to_folder(domain)

        # 2. Clean/default title
        if not title or not title.strip():
            title = self._generate_title_from_content(content)

        # 3. Auto-generate tags
        if not tags:
            tags = self._generate_tags(
                self._extract_concepts(content), domain
            )

        # 4. Build structured markdown
        now = datetime.now()
        frontmatter = (
            f"---\n"
            f"title: \"{title}\"\n"
            f"date: {now.strftime('%Y-%m-%d')}\n"
            f"tags: [{', '.join(tags)}]\n"
            f"domain: {domain}\n"
            f"source: {source_type}\n"
            f"created_by: knowledge_writer\n"
            f"---\n"
        )

        # Wrap content if it doesn't already have a heading
        if not content.strip().startswith('#'):
            structured_content = f"{frontmatter}\n# {title}\n\n{content}\n"
        else:
            structured_content = f"{frontmatter}\n{content}\n"

        # 5-7. Save via common infrastructure
        result = await self._save_note(
            title=title,
            content=structured_content,
            domain=folder,
            tags=tags,
            metadata={
                "source_type": source_type,
                "conversation_id": conversation_id,
                "created_at": now.isoformat(),
            }
        )

        # 8. Record metric
        if result.success and self.metrics_tracker:
            await self._record_write_metric(
                title=title,
                domain=domain,
                source_type=source_type,
                cloud_provider=None,
            )

        return result

    # ------------------------------------------------------------------
    # Scribe-Assisted Save (LLM call for enrichment)
    # ------------------------------------------------------------------

    async def scribe_save(
        self,
        content: str,
        title: str,
        conversation_history: Optional[list] = None,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route through Scribe's Enrich mode for wiki-linking
        and template-based formatting.

        Returns the enriched note data for PreviewModal display.
        The actual save happens when the user confirms in PreviewModal.
        """
        if not self.scribe:
            logger.warning("Scribe persona not available, falling back to quick save")
            result = await self.quick_save(
                content=content,
                title=title,
                domain=domain,
                source_type="scribe_fallback",
            )
            return result.to_dict()

        if not domain:
            domain = self._auto_detect_domain(content)

        try:
            # Call Scribe's standalone enrich method
            enriched = await self.scribe.enrich_standalone(
                content=content,
                title=title,
                domain=domain,
                conversation_history=conversation_history or [],
            )
            return enriched
        except Exception as e:
            logger.error(f"Scribe enrichment failed: {e}", exc_info=True)
            # Fallback to quick save
            result = await self.quick_save(
                content=content,
                title=title,
                domain=domain,
                source_type="scribe_fallback",
            )
            return result.to_dict()

    # ------------------------------------------------------------------
    # Per-Message Save
    # ------------------------------------------------------------------

    async def save_message(
        self,
        message_content: str,
        message_role: str,
        conversation_id: str,
        save_mode: str = "quick",
        title: Optional[str] = None,
        domain: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Union[NoteCreateResult, Dict[str, Any]]:
        """
        Save a single message to the knowledge base.

        If save_mode == "quick": calls quick_save()
        If save_mode == "scribe": calls scribe_save()
        """
        if save_mode == "scribe":
            return await self.scribe_save(
                content=message_content,
                title=title or self._generate_title_from_content(message_content),
                domain=domain,
            )
        else:
            return await self.quick_save(
                content=message_content,
                title=title or self._generate_title_from_content(message_content),
                domain=domain,
                tags=tags,
                source_type="context_menu",
                conversation_id=conversation_id,
            )

    # ------------------------------------------------------------------
    # Common Save Infrastructure
    # ------------------------------------------------------------------

    async def _save_note(
        self,
        title: str,
        content: str,
        domain: str,
        tags: List[str],
        metadata: Dict[str, Any],
    ) -> NoteCreateResult:
        """
        The actual write operation. All paths converge here.

        1. Determine active source (native or Obsidian)
        2. Normalize filename
        3. Build full path
        4. Check duplicates (if enabled)
        5. Write file
        6. Trigger RAG index update (incremental, not full rebuild)
        7. Return result with path, status, similar_notes (if any)
        """
        try:
            # Determine active notes source
            source = "native"
            if self.notes_source:
                source = self.notes_source.get_active_source()
                notes_path = Path(self.notes_source.get_notes_path()).expanduser()
            else:
                notes_path = Path.home() / ".polly" / "notes"

            # Normalize filename
            filename = title.lower().replace(" ", "_").replace("-", "_")
            filename = re.sub(r'[^\w_]', '', filename)
            if not filename:
                filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Build full path
            domain_path = notes_path / domain
            note_path = domain_path / f"{filename}.md"

            # Check if already exists
            if note_path.exists():
                # Append timestamp to make unique
                ts = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{filename}_{ts}"
                note_path = domain_path / f"{filename}.md"

            # Check for duplicates
            similar_notes = []
            try:
                from core.notes_dedup import get_dedup_engine
                dedup = get_dedup_engine()
                if dedup:
                    similar = dedup.check_similarity(content=content, title=title)
                    if similar:
                        similar_notes = [n.to_dict() for n in similar]
                        logger.info(f"Found {len(similar)} similar notes for '{title}'")
            except Exception as e:
                logger.warning(f"Dedup check failed: {e}")

            # Create domain directory if needed
            domain_path.mkdir(parents=True, exist_ok=True)

            # Write the note file
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Knowledge note saved: {note_path}")

            # Trigger incremental RAG indexing
            rag_indexed = await self._incremental_rag_index(str(note_path))

            # Persist to Mem0 if enabled (additive memory layer)
            await self._add_to_mem0(
                content=content,
                title=title,
                domain=domain,
                tags=tags,
                metadata=metadata
            )

            return NoteCreateResult(
                success=True,
                note_path=str(note_path),
                title=title,
                domain=domain,
                similar_notes=similar_notes,
                rag_indexed=rag_indexed,
                source=source,
            )

        except Exception as e:
            logger.error(f"Failed to save note: {e}", exc_info=True)
            return NoteCreateResult(
                success=False,
                error=str(e),
            )

    async def _incremental_rag_index(self, note_path: str) -> bool:
        """
        Index just the new note into RAG — not a full rebuild.
        Falls back to full notes index rebuild if incremental is not available.
        """
        if not self.rag:
            logger.warning("RAG not available for incremental indexing")
            return False

        try:
            # Try incremental single-document indexing
            if hasattr(self.rag, 'index_single_document'):
                await self.rag.index_single_document(note_path, source_type='notes')
                logger.info(f"Incrementally indexed: {note_path}")
                return True

            # Fallback: rebuild notes index (slower but works)
            if self.notes_source:
                notes_path = Path(self.notes_source.get_notes_path()).expanduser()
            else:
                notes_path = Path.home() / ".polly" / "notes"

            from core.notes_index import get_notes_index
            notes_idx = get_notes_index()
            notes_idx.build_index(notes_path, recursive=True)
            logger.info(f"Rebuilt notes index after adding: {note_path}")
            return True

        except Exception as e:
            logger.error(f"RAG indexing failed for {note_path}: {e}")
            return False

    async def _add_to_mem0(
        self,
        content: str,
        title: str,
        domain: str,
        tags: List[str],
        metadata: Dict[str, Any],
    ):
        """
        Add note to Mem0 adaptive memory for entity extraction and relationships.
        This is non-critical — if it fails, the note is still saved and indexed.
        """
        # Check if Mem0 is enabled
        if self.config.get('memory', {}).get('provider') != 'mem0':
            return
        
        if not self.config.get('memory', {}).get('mem0', {}).get('enabled', False):
            return

        try:
            from core.memory.mem0_adapter import Mem0Adapter
            
            mem0 = Mem0Adapter(self.config)
            
            # Build Mem0-compatible metadata
            mem0_metadata = {
                'title': title,
                'domain': domain,
                'tags': ','.join(tags) if tags else '',
                'source': 'knowledge_writer',
                'timestamp': datetime.now().isoformat(),
            }
            
            # Add additional metadata if provided
            if metadata:
                mem0_metadata.update({
                    k: str(v) for k, v in metadata.items()
                    if k not in mem0_metadata  # Don't override core fields
                })
            
            # Add to Mem0 (entity extraction happens automatically)
            result = mem0.add_memory(
                content=content,
                user_id="knowledge",  # Knowledge namespace
                metadata=mem0_metadata
            )
            
            logger.info(f"Added note to Mem0: {title} (memory_id: {result.get('id', 'unknown')})")
            
        except ImportError:
            logger.debug("Mem0 not available (mem0ai package not installed)")
        except Exception as e:
            # Non-critical failure — note is still saved
            logger.warning(f"Failed to add note to Mem0 (non-critical): {e}")

    # ------------------------------------------------------------------
    # Settings Management
    # ------------------------------------------------------------------

    def update_settings(self, settings: Dict[str, Any]):
        """Update knowledge suggestion settings at runtime."""
        if 'enabled' in settings:
            self.suggestions_enabled = settings['enabled']
        if 'style' in settings:
            self.suggestion_style = settings['style']
        if 'min_gap_score' in settings:
            self.min_gap_score = settings['min_gap_score']

        logger.info(
            f"KnowledgeWriter settings updated: "
            f"enabled={self.suggestions_enabled}, "
            f"style={self.suggestion_style}, "
            f"min_gap={self.min_gap_score}"
        )

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    async def _record_write_metric(
        self,
        title: str,
        domain: str,
        source_type: str,
        cloud_provider: Optional[str] = None,
    ):
        """Record a knowledge write event for autonomy tracking."""
        if not self.metrics_tracker:
            return

        try:
            self.metrics_tracker.record_knowledge_write(
                title=title,
                domain=domain,
                source_type=source_type,
                cloud_provider=cloud_provider,
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.warning(f"Failed to record write metric: {e}")

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def _extract_concepts(self, text: str, max_concepts: int = 20) -> List[str]:
        """
        Extract key concepts from text using lightweight heuristics.
        No LLM call — uses capitalized phrases, technical terms, etc.
        """
        if not text:
            return []

        concepts = set()

        # Extract capitalized multi-word phrases (likely proper nouns / technical terms)
        cap_phrases = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', text)
        concepts.update(cap_phrases[:10])

        # Extract backtick-wrapped terms (code/technical terms)
        code_terms = re.findall(r'`([^`]+)`', text)
        concepts.update(t.strip() for t in code_terms if len(t.strip()) > 2)

        # Extract bold terms (markdown)
        bold_terms = re.findall(r'\*\*([^*]+)\*\*', text)
        concepts.update(t.strip() for t in bold_terms if len(t.strip()) > 2)

        # Extract terms after "is a", "refers to", "means" (definitional patterns)
        defs = re.findall(
            r'(?:is a|refers to|means|defined as)\s+([^.,:;]{3,40})',
            text,
            re.IGNORECASE
        )
        concepts.update(d.strip() for d in defs)

        return list(concepts)[:max_concepts]

    def _auto_detect_domain(self, text: str) -> str:
        """Auto-detect domain from text content using DomainEngine if available."""
        if self.domain_engine:
            try:
                domains = self.domain_engine.detect_domains(text)
                if domains and domains[0].value != "unknown":
                    return domains[0].value
            except Exception as e:
                logger.warning(f"Domain detection failed: {e}")

        # Fallback: keyword matching
        text_lower = text.lower()
        domain_keywords = {
            "sigils": ["code", "python", "api", "docker", "function", "class", "import", "server", "database"],
            "signals": ["audio", "midi", "synthesis", "dsp", "sound", "music", "frequency"],
            "scrolls": ["essay", "writing", "pedagogy", "education", "notes", "documentation"],
            "glyphs": ["design", "visual", "ui", "ux", "layout", "color", "typography"],
            "grids": ["framework", "mental model", "systems", "thinking", "strategy"],
        }

        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[domain] = score

        if scores:
            return max(scores, key=scores.get)

        return "scrolls"  # Default domain

    def _generate_title(self, query: str, novel_concepts: List[str]) -> str:
        """Generate a note title from query and novel concepts."""
        # Use the query as basis, cleaned up
        title = query.strip()

        # Remove question marks and common question prefixes
        title = re.sub(r'^\s*(what|how|why|when|where|who|can you|could you|please)\s+', '', title, flags=re.IGNORECASE)
        title = title.rstrip('?').strip()

        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]

        # Truncate to reasonable length
        if len(title) > 60:
            # Try to cut at a word boundary
            truncated = title[:57]
            last_space = truncated.rfind(' ')
            if last_space > 30:
                title = truncated[:last_space]
            else:
                title = truncated

        return title or "Knowledge Note"

    def _generate_title_from_content(self, content: str) -> str:
        """Generate a title from content when no query/title is available."""
        # Try first heading
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if heading_match:
            return heading_match.group(1).strip()[:60]

        # Try first sentence
        first_line = content.strip().split('\n')[0].strip()
        first_line = re.sub(r'^[#\-*>\s]+', '', first_line)  # Strip markdown markers

        if len(first_line) > 60:
            truncated = first_line[:57]
            last_space = truncated.rfind(' ')
            if last_space > 30:
                return truncated[:last_space]
            return truncated

        return first_line or "Knowledge Note"

    def _generate_tags(self, concepts: List[str], domain: str) -> List[str]:
        """Generate tags from concepts and domain."""
        tags = [domain]

        for concept in concepts[:5]:
            # Convert to kebab-case tag
            tag = concept.lower().strip()
            tag = re.sub(r'[^a-z0-9\s-]', '', tag)
            tag = re.sub(r'\s+', '-', tag).strip('-')
            if tag and len(tag) > 1 and tag != domain:
                tags.append(tag)

        return tags[:8]  # Cap at 8 tags


# ========== Module-Level Singleton ==========

_knowledge_writer: Optional[KnowledgeWriter] = None


def get_knowledge_writer() -> Optional[KnowledgeWriter]:
    """Get the global KnowledgeWriter instance."""
    return _knowledge_writer


def init_knowledge_writer(
    config,
    notes_source_manager=None,
    rag=None,
    domain_engine=None,
    scribe_persona=None,
    metrics_tracker=None,
) -> KnowledgeWriter:
    """Initialize the global KnowledgeWriter instance."""
    global _knowledge_writer
    _knowledge_writer = KnowledgeWriter(
        config=config,
        notes_source_manager=notes_source_manager,
        rag=rag,
        domain_engine=domain_engine,
        scribe_persona=scribe_persona,
        metrics_tracker=metrics_tracker,
    )
    return _knowledge_writer

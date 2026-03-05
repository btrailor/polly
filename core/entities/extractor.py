"""
Unified entity extraction pipeline.

Consolidates extraction from knowledge graph (regex), pattern learner (spaCy + technical terms),
and optional LLM. Extracts entities from text and stores them with relationship detection.
"""

from __future__ import annotations

import re
import logging
from datetime import datetime
from functools import lru_cache
from typing import List, Optional, Set, Tuple

from .models import Entity, EntityType, Relationship, RelationshipType, entity_id
from .store import EntityStore

logger = logging.getLogger(__name__)


# ── Word-boundary matching ────────────────────────────────────────────

@lru_cache(maxsize=1024)
def _word_boundary_pattern(term: str) -> re.Pattern:
    """Compile a word-boundary regex for a term (cached)."""
    return re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)


def _term_in_text(term: str, text_lower: str) -> bool:
    """Check if term appears as a whole word in text (not as a substring)."""
    return _word_boundary_pattern(term).search(text_lower) is not None

# ── Entity Validation ────────────────────────────────────────────────

# Programming keywords and common short words that produce garbage entities
GARBAGE_STOPWORDS = frozenset({
    # Python keywords / builtins
    "set", "get", "int", "str", "list", "dict", "map", "for", "if", "in",
    "not", "and", "or", "is", "as", "from", "import", "class", "def",
    "return", "yield", "with", "try", "except", "raise", "pass", "break",
    "continue", "while", "else", "elif", "none", "true", "false", "self",
    "type", "len", "print", "range", "open", "file", "input", "output",
    "key", "val", "var", "arg", "obj", "new", "old", "run", "end",
    "log", "err", "msg", "tmp", "src", "dst", "idx", "num", "max", "min",
    # Common short English words
    "the", "this", "that", "then", "them", "they", "was", "were", "has",
    "had", "are", "can", "may", "but", "also", "each", "all", "any",
    "some", "one", "two", "use", "used", "just", "will", "very",
    # Config / code fragments that get false-positive matched
    "ini", "dom", "cfg", "env", "bin", "lib", "app", "mod", "pkg",
    "todo", "note", "test", "spec", "doc", "api", "url", "http",
    # Generic programming terms too ambiguous as standalone entities
    "process", "start", "stop", "build", "update", "install",
    "merge", "push", "pull", "fetch", "checkout", "commit",
    "run", "format", "lint", "compile", "deploy", "migrate",
    "table", "row", "column", "index", "view", "schema", "query",
    "model", "state", "struct", "constant", "variable", "function",
    "request", "response", "body", "header", "session", "cookie",
    "tag", "release", "issue", "bug", "error", "warning",
    "uri", "spa", "ssr", "csr", "ssg", "pwa",
    "rest", "pipe", "redirect", "alias", "environment",
    "container", "graph", "endpoint", "route", "middleware",
    "express", "apt",
    "stack", "queue", "performance", "rds",
    "quic", "optimize", "benchmark", "profiling",
    "exploit", "method",
})

# Known-good short entities (2-3 chars) that should NOT be filtered
SHORT_ENTITY_WHITELIST = frozenset({
    "ai", "ml", "js", "ts", "go", "c", "r", "sql", "css", "git",
    "aws", "gcp", "api", "cli", "gui", "ide", "oop", "llm", "nlp",
    "rag", "vue", "lua", "svn", "npm", "pip", "jwt", "ssh", "tcp",
})

MIN_ENTITY_NAME_LENGTH = 3


def is_valid_entity_name(name: str) -> bool:
    """Check if an entity name passes quality validation.
    
    Rejects:
    - Names shorter than MIN_ENTITY_NAME_LENGTH (unless whitelisted)
    - Programming keywords and common stopwords
    - Pure numbers or single characters
    """
    if not name or not name.strip():
        return False
    clean = name.strip().lower()
    # Whitelist check (known-good short names)
    if clean in SHORT_ENTITY_WHITELIST:
        return True
    # Minimum length
    if len(clean) < MIN_ENTITY_NAME_LENGTH:
        return False
    # Pure numbers
    if clean.replace(".", "").replace("-", "").isdigit():
        return False
    # Stopword check (normalized)
    normalized = clean.replace(" ", "").replace("-", "").replace("_", "")
    if normalized in GARBAGE_STOPWORDS or clean in GARBAGE_STOPWORDS:
        return False
    return True


# Optional: use full technical term list from learners if available
try:
    from learners.patterns import TECHNICAL_TERMS as _TECHNICAL_TERMS
    TECHNICAL_TERMS = _TECHNICAL_TERMS
except ImportError:
    TECHNICAL_TERMS = {
        "python", "docker", "fastapi", "react", "javascript", "typescript",
        "obsidian", "ollama", "norns", "supercollider", "rust", "lua",
        "api", "rest", "graphql", "sql", "git", "github",
        "constraint", "emergence", "systems thinking", "polymathic",
    }

# Known entity type keywords (from learners/graph.py ENTITY_TYPES, expanded)
ENTITY_KEYWORDS: dict = {
    EntityType.CONCEPT: [
        "infinite game", "finite game", "constraint", "emergence",
        "systems thinking", "polymathic", "popular education", "design thinking", "agile",
    ],
    EntityType.TOOL: [
        "norns", "supercollider", "docker", "obsidian", "ollama",
        "python", "rust", "lua", "javascript", "git", "github",
    ],
    EntityType.FRAMEWORK: [
        "freire", "pedagogy", "fastapi", "react", "vue", "django", "flask",
    ],
    EntityType.PATTERN: [
        "factory", "observer", "state machine", "callback", "async",
    ],
}


class EntityExtractor:
    """Unified entity extraction and storage."""

    def __init__(self, entity_store: EntityStore, use_spacy: bool = True):
        self.store = entity_store
        self._use_spacy = use_spacy
        self._nlp = None

    def _ensure_nlp(self):
        if self._nlp is not None or not self._use_spacy:
            return
        try:
            import spacy
            self._nlp = spacy.load("en_core_web_sm")
            logger.info("EntityExtractor: spaCy loaded for NER and noun chunks")
        except Exception as e:
            logger.debug(f"EntityExtractor: spaCy not available: {e}")

    def extract_and_store(
        self,
        text: str,
        source_type: str,
        source_id: str,
        domains: Optional[List[str]] = None,
        extract_relationships: bool = True,
    ) -> List[Entity]:
        """Extract entities from text, store them, record mentions. Optionally detect relationships."""
        domains = domains or []
        # 1) Regex + keyword extraction (always)
        entities = self._extract_keywords_and_regex(text, domains)
        # 2) spaCy NER and noun chunks (if available)
        self._ensure_nlp()
        if self._nlp:
            spacy_entities = self._extract_spacy(text, domains)
            for e in spacy_entities:
                if not any(ex.id == e.id for ex in entities):
                    entities.append(e)
        # 3) Technical terms in text (word-boundary match to avoid substring false positives)
        text_lower = text.lower()
        for term in TECHNICAL_TERMS:
            if len(term) >= 3 and _term_in_text(term, text_lower):
                eid = entity_id(term.title(), EntityType.TOOL.value)
                if not any(ex.id == eid for ex in entities):
                    entities.append(Entity(
                        id=eid,
                        name=term.title(),
                        entity_type=EntityType.TOOL,
                        domains=domains,
                        mention_count=1,
                        source_count=1,
                        last_seen=datetime.now(),
                        created=datetime.now(),
                    ))
        # 4) Wiki-style [[links]]
        for link in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text):
            name = link.strip()
            if len(name) >= 2:
                eid = entity_id(name, EntityType.CONCEPT.value)
                if not any(ex.id == eid for ex in entities):
                    entities.append(Entity(
                        id=eid,
                        name=name,
                        entity_type=EntityType.CONCEPT,
                        domains=domains,
                        mention_count=1,
                        source_count=1,
                        last_seen=datetime.now(),
                        created=datetime.now(),
                    ))
        # 5) Validate, dedupe by id, and upsert
        seen: Set[str] = set()
        stored: List[Entity] = []
        for e in entities:
            if e.id in seen:
                continue
            # Validate entity name quality
            if not is_valid_entity_name(e.name):
                continue
            seen.add(e.id)
            e.domains = list(set(e.domains + domains))
            self.store.upsert_entity(e)
            self.store.record_mention(e.id, source_type, source_id, context=text[:200])
            stored.append(e)
        # 6) Co-occurrence relationships
        if extract_relationships and len(stored) >= 2:
            for i, e1 in enumerate(stored):
                for e2 in stored[i + 1 :]:
                    rel = Relationship(
                        source_id=e1.id,
                        target_id=e2.id,
                        relationship_type=RelationshipType.RELATED_TO,
                        strength=0.5,
                        context="Co-occurrence in same text",
                        mention_count=1,
                        created=datetime.now(),
                        last_seen=datetime.now(),
                    )
                    self.store.upsert_relationship(rel)
        return stored

    def _extract_keywords_and_regex(self, text: str, domains: List[str]) -> List[Entity]:
        out: List[Entity] = []
        text_lower = text.lower()
        for entity_type, keywords in ENTITY_KEYWORDS.items():
            for keyword in keywords:
                if _term_in_text(keyword, text_lower):
                    name = keyword.title()
                    eid = entity_id(name, entity_type.value)
                    out.append(Entity(
                        id=eid,
                        name=name,
                        entity_type=entity_type,
                        domains=domains,
                        mention_count=1,
                        source_count=1,
                        last_seen=datetime.now(),
                        created=datetime.now(),
                    ))
        return out

    def _extract_spacy(self, text: str, domains: List[str]) -> List[Entity]:
        if not self._nlp:
            return []
        out: List[Entity] = []
        text_clean = re.sub(r"```[^`]*```", "", text)
        text_clean = re.sub(r"`[^`]+`", "", text_clean)
        if not text_clean.strip():
            return []
        doc = self._nlp(text_clean[:10000])  # Limit length
        # Named entities
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT", "GPE", "PERSON", "NORP"):
                name = ent.text.strip()
                if len(name) < 2:
                    continue
                et = EntityType.ORGANIZATION if ent.label_ == "ORG" else EntityType.PERSON if ent.label_ == "PERSON" else EntityType.CONCEPT
                eid = entity_id(name, et.value)
                out.append(Entity(
                    id=eid,
                    name=name,
                    entity_type=et,
                    domains=domains,
                    mention_count=1,
                    source_count=1,
                    last_seen=datetime.now(),
                    created=datetime.now(),
                ))
        # Noun chunks (multi-word concepts)
        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower().strip()
            if " " not in phrase or len(phrase) < 5:
                continue
            if phrase in TECHNICAL_TERMS or any(_term_in_text(t, phrase) for t in TECHNICAL_TERMS):
                name = phrase.title()
                eid = entity_id(name, EntityType.CONCEPT.value)
                out.append(Entity(
                    id=eid,
                    name=name,
                    entity_type=EntityType.CONCEPT,
                    domains=domains,
                    mention_count=1,
                    source_count=1,
                    last_seen=datetime.now(),
                    created=datetime.now(),
                ))
        return out

    def batch_extract_and_store(
        self,
        items: List[Tuple[str, str]],  # (text, source_type) pairs
        source_id: str,
        domains: Optional[List[str]] = None,
        extract_relationships: bool = True,
    ) -> List[Entity]:
        """
        Extract entities from multiple texts in a single spaCy pipeline pass.

        Compared to calling extract_and_store() N times, this method runs the
        spaCy nlp.pipe() batch call once across all texts, halving the per-call
        overhead for two-item batches (query + response).

        All non-spaCy extraction steps (regex, keywords, wiki-links) are still
        run per-text before the batch NER pass so that per-text deduplication
        works correctly.  Entities from all texts are merged and stored once.

        Args:
            items: List of (text, source_type) pairs to process together.
            source_id: Common source identifier for all items.
            domains: Domain tags to apply to extracted entities.
            extract_relationships: Whether to write co-occurrence relationships.

        Returns:
            Deduplicated list of stored Entity objects (union across all texts).
        """
        if not items:
            return []

        domains = domains or []

        # --- Per-text non-spaCy extraction (regex, keywords, wiki-links) ---
        per_text_entities: List[List[Entity]] = []
        for text, _source_type in items:
            text_entities: List[Entity] = []
            text_entities.extend(self._extract_keywords_and_regex(text, domains))

            text_lower = text.lower()
            for term in TECHNICAL_TERMS:
                if len(term) >= 3 and _term_in_text(term, text_lower):
                    eid = entity_id(term.title(), EntityType.TOOL.value)
                    if not any(ex.id == eid for ex in text_entities):
                        text_entities.append(Entity(
                            id=eid,
                            name=term.title(),
                            entity_type=EntityType.TOOL,
                            domains=domains,
                            mention_count=1,
                            source_count=1,
                            last_seen=datetime.now(),
                            created=datetime.now(),
                        ))

            for link in re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text):
                name = link.strip()
                if len(name) >= 2:
                    eid = entity_id(name, EntityType.CONCEPT.value)
                    if not any(ex.id == eid for ex in text_entities):
                        text_entities.append(Entity(
                            id=eid,
                            name=name,
                            entity_type=EntityType.CONCEPT,
                            domains=domains,
                            mention_count=1,
                            source_count=1,
                            last_seen=datetime.now(),
                            created=datetime.now(),
                        ))

            per_text_entities.append(text_entities)

        # --- Batch spaCy NER across all texts in one pipe() call ---
        self._ensure_nlp()
        if self._nlp:
            # Prepare cleaned texts (same cleaning as _extract_spacy)
            cleaned_texts = []
            for text, _ in items:
                text_clean = re.sub(r"```[^`]*```", "", text)
                text_clean = re.sub(r"`[^`]+`", "", text_clean)
                cleaned_texts.append(text_clean[:10000])

            for doc, text_entities in zip(self._nlp.pipe(cleaned_texts), per_text_entities):
                # Named entities
                for ent in doc.ents:
                    if ent.label_ in ("ORG", "PRODUCT", "GPE", "PERSON", "NORP"):
                        name = ent.text.strip()
                        if len(name) < 2:
                            continue
                        et = (
                            EntityType.ORGANIZATION if ent.label_ == "ORG"
                            else EntityType.PERSON if ent.label_ == "PERSON"
                            else EntityType.CONCEPT
                        )
                        eid = entity_id(name, et.value)
                        if not any(ex.id == eid for ex in text_entities):
                            text_entities.append(Entity(
                                id=eid,
                                name=name,
                                entity_type=et,
                                domains=domains,
                                mention_count=1,
                                source_count=1,
                                last_seen=datetime.now(),
                                created=datetime.now(),
                            ))
                # Noun chunks
                for chunk in doc.noun_chunks:
                    phrase = chunk.text.lower().strip()
                    if " " not in phrase or len(phrase) < 5:
                        continue
                    if phrase in TECHNICAL_TERMS or any(_term_in_text(t, phrase) for t in TECHNICAL_TERMS):
                        name = phrase.title()
                        eid = entity_id(name, EntityType.CONCEPT.value)
                        if not any(ex.id == eid for ex in text_entities):
                            text_entities.append(Entity(
                                id=eid,
                                name=name,
                                entity_type=EntityType.CONCEPT,
                                domains=domains,
                                mention_count=1,
                                source_count=1,
                                last_seen=datetime.now(),
                                created=datetime.now(),
                            ))

        # --- Merge all per-text entities, deduplicate, validate, store ---
        global_seen: Set[str] = set()
        stored: List[Entity] = []

        for (text, source_type), text_entities in zip(items, per_text_entities):
            for e in text_entities:
                if e.id in global_seen:
                    continue
                # Validate entity name quality
                if not is_valid_entity_name(e.name):
                    continue
                global_seen.add(e.id)
                e.domains = list(set(e.domains + domains))
                self.store.upsert_entity(e)
                self.store.record_mention(e.id, source_type, source_id, context=text[:200])
                stored.append(e)

        # Co-occurrence relationships across the combined entity set
        if extract_relationships and len(stored) >= 2:
            for i, e1 in enumerate(stored):
                for e2 in stored[i + 1:]:
                    rel = Relationship(
                        source_id=e1.id,
                        target_id=e2.id,
                        relationship_type=RelationshipType.RELATED_TO,
                        strength=0.5,
                        context="Co-occurrence in same text batch",
                        mention_count=1,
                        created=datetime.now(),
                        last_seen=datetime.now(),
                    )
                    self.store.upsert_relationship(rel)

        return stored

    def extract_entities_only(self, text: str) -> List[Entity]:
        """Extract entities without storing (preview)."""
        domains: List[str] = []
        entities = self._extract_keywords_and_regex(text, domains)
        self._ensure_nlp()
        if self._nlp:
            entities.extend(self._extract_spacy(text, domains))
        text_lower = text.lower()
        for term in TECHNICAL_TERMS:
            if len(term) >= 3 and _term_in_text(term, text_lower):
                eid = entity_id(term.title(), EntityType.TOOL.value)
                if not any(e.id == eid for e in entities):
                    entities.append(Entity(
                        id=eid,
                        name=term.title(),
                        entity_type=EntityType.TOOL,
                        domains=[],
                        mention_count=0,
                        source_count=0,
                        last_seen=datetime.now(),
                        created=datetime.now(),
                    ))
        return entities

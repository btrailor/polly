"""
Unified entity extraction pipeline.

Consolidates extraction from knowledge graph (regex), pattern learner (spaCy + technical terms),
and optional LLM. Extracts entities from text and stores them with relationship detection.
"""

from __future__ import annotations

import re
import logging
from datetime import datetime
from typing import List, Optional, Set

from .models import Entity, EntityType, Relationship, RelationshipType, entity_id
from .store import EntityStore

logger = logging.getLogger(__name__)

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
        # 3) Technical terms in text
        text_lower = text.lower()
        for term in TECHNICAL_TERMS:
            if term in text_lower and len(term) >= 3:
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
        # 5) Dedupe by id and upsert
        seen: Set[str] = set()
        stored: List[Entity] = []
        for e in entities:
            if e.id in seen:
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
                if keyword in text_lower:
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
            if phrase in TECHNICAL_TERMS or any(t in phrase for t in TECHNICAL_TERMS):
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

    def extract_entities_only(self, text: str) -> List[Entity]:
        """Extract entities without storing (preview)."""
        domains: List[str] = []
        entities = self._extract_keywords_and_regex(text, domains)
        self._ensure_nlp()
        if self._nlp:
            entities.extend(self._extract_spacy(text, domains))
        text_lower = text.lower()
        for term in TECHNICAL_TERMS:
            if term in text_lower and len(term) >= 3:
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

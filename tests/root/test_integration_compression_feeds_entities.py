"""
Integration test: compressed conversation data feeds entity extraction.

Verifies compression→entity pipeline: key_concepts/focus_topics from compression
are extracted into the entity store (integration-contracts).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.entities import EntityStore, EntityExtractor


def test_compression_key_concepts_extracted_to_entities(tmp_path: Path):
    """Simulated compression output: key_concepts passed to extract_and_store end up in store."""
    store = EntityStore(tmp_path / "entities.db")
    extractor = EntityExtractor(store, use_spacy=False)
    conversation_id = "compressed_conv_1"
    domains = ["sigils", "scrolls"]
    key_concepts = [
        {"term": "Docker", "definition": "Containerization platform"},
        {"concept": "Kubernetes", "definition": "Orchestration"},
    ]
    focus_topics = ["Python", "API design"]
    for item in key_concepts:
        text = item.get("term") or item.get("definition") or item.get("concept", "")
        if isinstance(text, str) and text.strip():
            extractor.extract_and_store(text.strip(), source_type="compression", source_id=conversation_id, domains=domains)
    for topic in focus_topics:
        if isinstance(topic, str) and topic.strip():
            extractor.extract_and_store(topic.strip(), source_type="compression", source_id=conversation_id, domains=domains)
    stats = store.get_stats()
    assert stats.get("entities", 0) >= 1

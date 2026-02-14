"""Test compression→entity integration (integration-contracts Task 10)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.entities import EntityStore, EntityExtractor


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink(missing_ok=True)


def test_compression_source_type_stored(temp_db):
    """Entity extractor accepts source_type='compression' and stores to entity store."""
    store = EntityStore(temp_db)
    extractor = EntityExtractor(store, use_spacy=False)
    conversation_id = "test_conv_1"
    domains = ["sigils"]
    extractor.extract_and_store(
        "Docker and Kubernetes",
        source_type="compression",
        source_id=conversation_id,
        domains=domains,
    )
    extractor.extract_and_store(
        "Python",
        source_type="compression",
        source_id=conversation_id,
        domains=domains,
    )
    stats = store.get_stats()
    assert stats.get("entities", 0) >= 1

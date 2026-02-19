"""
Tests for Tiered Memory Store.
Uses a mock Mem0 adapter to test tier-aware read/write without a real vector DB.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from core.memory.tiers import (
    TieredMemoryStore,
    MemoryTier,
    MemoryEntry,
    MemoryMetadata,
)


class MockMem0Adapter:
    """Mock Mem0 adapter for unit testing without a real backend."""

    def __init__(self):
        self._memories = {}  # user_id → list of dicts

    def add_memory(self, content: str, user_id: str, metadata: dict = None) -> dict:
        if user_id not in self._memories:
            self._memories[user_id] = []
        mem_id = f"mem_{len(self._memories[user_id])}"
        entry = {
            "id": mem_id,
            "content": content,
            "user_id": user_id,
            "metadata": metadata or {},
        }
        self._memories[user_id].append(entry)
        return {"id": mem_id}

    def search_memory(self, query: str, user_id: str, limit: int = 10) -> list:
        results = []
        for mem in self._memories.get(user_id, []):
            # Simplified scoring: word overlap
            query_words = set(query.lower().split())
            content_words = set(mem["content"].lower().split())
            overlap = len(query_words & content_words)
            score = min(overlap / max(len(query_words), 1), 1.0)
            results.append({
                "id": mem["id"],
                "memory": mem["content"],
                "score": score,
                "metadata": mem.get("metadata", {}),
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_all_memories(self, user_id: str) -> list:
        return self._memories.get(user_id, [])

    def update_memory(self, memory_id: str, content: str, metadata: dict = None):
        for user_memories in self._memories.values():
            for mem in user_memories:
                if mem["id"] == memory_id:
                    mem["content"] = content
                    if metadata:
                        mem["metadata"] = metadata
                    return

    def reset(self, user_id: str):
        self._memories.pop(user_id, None)


def _make_store(session_id="test_session"):
    """Create a TieredMemoryStore with mock adapter."""
    adapter = MockMem0Adapter()
    config = {
        "tiers": {
            "stable": {"collection": "memory_stable"},
            "episodic": {"collection": "memory_episodic", "decay_halflife_days": 90},
            "working": {"collection": "memory_working"},
        },
        "retrieval": {
            "stable_limit": 5,
            "episodic_limit": 5,
            "min_similarity": 0.0,
        },
    }
    store = TieredMemoryStore(mem0_adapter=adapter, config=config)
    # Override the auto-generated session_id for predictable test assertions
    store.session_id = session_id
    return store, adapter


class TestTieredMemoryStoreWrite:
    """Test writing to different tiers."""

    def test_write_to_stable_tier(self):
        store, adapter = _make_store()
        store.write(
            content="User prefers TypeScript",
            tier=MemoryTier.STABLE,
            metadata={"domain": "sigils"},
        )
        # Should be stored under the stable user_id
        all_mems = adapter.get_all_memories("tier:stable")
        assert len(all_mems) == 1
        assert "TypeScript" in all_mems[0]["content"]

    def test_write_to_episodic_tier(self):
        store, adapter = _make_store()
        store.write(
            content="Decided to use SQLite for entity store",
            tier=MemoryTier.EPISODIC,
        )
        all_mems = adapter.get_all_memories("tier:episodic")
        assert len(all_mems) == 1

    def test_write_to_working_tier(self):
        store, adapter = _make_store()
        store.write(
            content="Currently discussing RAG improvements",
            tier=MemoryTier.WORKING,
        )
        user_id = "tier:working:test_session"
        all_mems = adapter.get_all_memories(user_id)
        assert len(all_mems) == 1

    def test_write_includes_metadata(self):
        store, adapter = _make_store()
        store.write(
            content="Test content",
            tier=MemoryTier.STABLE,
            metadata={
                "domain": "signals",
                "source_type": "user_stated",
                "salience": 0.9,
            },
        )
        all_mems = adapter.get_all_memories("tier:stable")
        assert all_mems[0]["metadata"]["tier"] == "stable"
        assert all_mems[0]["metadata"]["domain"] == "signals"


class TestTieredMemoryStoreRead:
    """Test reading from different tiers."""

    def test_read_from_stable_tier(self):
        store, _ = _make_store()
        store.write("TypeScript is preferred", tier=MemoryTier.STABLE)
        results = store.read(query="TypeScript", tiers=[MemoryTier.STABLE])
        assert len(results) >= 1
        assert any("TypeScript" in r.content for r in results)

    def test_read_returns_memory_entries(self):
        store, _ = _make_store()
        store.write("Some memory", tier=MemoryTier.STABLE)
        results = store.read(query="memory", tiers=[MemoryTier.STABLE])
        for r in results:
            assert isinstance(r, MemoryEntry)
            assert r.tier == MemoryTier.STABLE

    def test_read_empty_tier(self):
        store, _ = _make_store()
        results = store.read(query="anything", tiers=[MemoryTier.STABLE])
        assert results == []


class TestTieredMemoryStoreFlush:
    """Test working tier flush."""

    def test_flush_working_clears_session(self):
        store, adapter = _make_store()
        store.write("Session state", tier=MemoryTier.WORKING)
        user_id = "tier:working:test_session"
        assert len(adapter.get_all_memories(user_id)) == 1

        store.flush_working()
        assert len(adapter.get_all_memories(user_id)) == 0

    def test_flush_working_preserves_other_tiers(self):
        store, adapter = _make_store()
        store.write("Stable fact", tier=MemoryTier.STABLE)
        store.write("Session state", tier=MemoryTier.WORKING)

        store.flush_working()

        # Stable should remain
        assert len(adapter.get_all_memories("tier:stable")) == 1
        # Working should be cleared
        assert len(adapter.get_all_memories("tier:working:test_session")) == 0


class TestMemoryMetadata:
    """Test MemoryMetadata serialization."""

    def test_to_dict(self):
        meta = MemoryMetadata(
            tier="stable",
            domain="sigils",
            tags=["preference", "language"],
        )
        d = meta.to_dict()
        assert d["tier"] == "stable"
        assert d["domain"] == "sigils"
        assert "preference" in d["tags"]

    def test_from_dict(self):
        d = {
            "tier": "episodic",
            "domain": "signals",
            "salience": 0.8,
            "tags": "decision,architecture",
        }
        meta = MemoryMetadata.from_dict(d)
        assert meta.tier == "episodic"
        assert meta.domain == "signals"
        assert meta.salience == 0.8
        assert "decision" in meta.tags

    def test_from_dict_empty_tags(self):
        d = {"tier": "working", "tags": ""}
        meta = MemoryMetadata.from_dict(d)
        assert meta.tags == []

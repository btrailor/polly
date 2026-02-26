"""
Tests for IncrementalKGIndexer (Wave 5, Task 24).

Tests cover:
  - on_note_saved: entity extraction + cache invalidation
  - on_note_saved: empty content skipped
  - on_note_saved: extraction failure handled gracefully
  - backfill_all: batched processing, totals aggregation, final cache invalidation
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

from core.knowledge_graph.incremental_indexer import IncrementalKGIndexer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _mock_extractor(entities: int = 3) -> MagicMock:
    extractor = MagicMock()
    extractor.extract_and_store.return_value = {"entities": entities, "relationships": 1}
    return extractor


def _mock_entity_store() -> MagicMock:
    return MagicMock()


def _mock_index_builder() -> MagicMock:
    return MagicMock()


def _indexer(
    entities: int = 3,
    with_builder: bool = True,
) -> IncrementalKGIndexer:
    return IncrementalKGIndexer(
        entity_store=_mock_entity_store(),
        entity_extractor=_mock_extractor(entities),
        index_builder=_mock_index_builder() if with_builder else None,
    )


# ---------------------------------------------------------------------------
# Tests: __init__ + repr
# ---------------------------------------------------------------------------

class TestInit:
    def test_stores_dependencies(self):
        store = _mock_entity_store()
        extractor = _mock_extractor()
        builder = _mock_index_builder()
        indexer = IncrementalKGIndexer(store, extractor, builder)
        assert indexer.entity_store is store
        assert indexer.entity_extractor is extractor
        assert indexer.index_builder is builder

    def test_index_builder_optional(self):
        indexer = IncrementalKGIndexer(_mock_entity_store(), _mock_extractor(), None)
        assert indexer.index_builder is None

    def test_repr_with_builder(self):
        indexer = _indexer(with_builder=True)
        r = repr(indexer)
        assert "IncrementalKGIndexer" in r
        assert "True" in r

    def test_repr_without_builder(self):
        indexer = _indexer(with_builder=False)
        r = repr(indexer)
        assert "False" in r


# ---------------------------------------------------------------------------
# Tests: on_note_saved
# ---------------------------------------------------------------------------

class TestOnNoteSaved:
    def test_empty_content_returns_empty_dict(self):
        indexer = _indexer()
        result = _run(indexer.on_note_saved("", "note_1"))
        assert result == {}

    def test_whitespace_only_returns_empty_dict(self):
        indexer = _indexer()
        result = _run(indexer.on_note_saved("   \n\t  ", "note_1"))
        assert result == {}

    def test_extraction_called_with_content_and_note_id(self):
        indexer = _indexer()
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.return_value = {"entities": 2}
            result = _run(indexer.on_note_saved("Note content here.", "my_note"))
        mock_thread.assert_called_once()
        call_args = mock_thread.call_args
        # First positional arg is the function; note_id is passed as source_id= kwarg
        assert call_args[0][0] == indexer.entity_extractor.extract_and_store
        assert call_args[1].get("source_id") == "my_note"

    def test_cache_invalidated_after_save(self):
        indexer = _indexer()
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.return_value = {"entities": 3}
            _run(indexer.on_note_saved("Some content.", "note_42"))
        indexer.index_builder.invalidate_cache.assert_called_once()

    def test_cache_not_invalidated_when_no_builder(self):
        indexer = _indexer(with_builder=False)
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.return_value = {"entities": 1}
            _run(indexer.on_note_saved("Content.", "note_1"))
        # No builder — should not raise

    def test_returns_stats_dict(self):
        indexer = _indexer()
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.return_value = {"entities": 5, "relationships": 2}
            result = _run(indexer.on_note_saved("Content.", "note_1"))
        assert result == {"entities": 5, "relationships": 2}

    def test_extraction_failure_returns_empty_dict(self):
        indexer = _indexer()
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.side_effect = Exception("extraction failed")
            result = _run(indexer.on_note_saved("Content.", "note_bad"))
        assert result == {}

    def test_extraction_failure_does_not_invalidate_cache(self):
        indexer = _indexer()
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.side_effect = Exception("fail")
            _run(indexer.on_note_saved("Content.", "note_bad"))
        # Cache should NOT be invalidated if extraction failed
        indexer.index_builder.invalidate_cache.assert_not_called()

    def test_non_dict_stats_handled_gracefully(self):
        indexer = _indexer()
        with patch("asyncio.to_thread", new_callable=AsyncMock) as mock_thread:
            mock_thread.return_value = None  # Non-dict return
            result = _run(indexer.on_note_saved("Content.", "note_1"))
        # Should return {"entities": 0} fallback
        assert result == {"entities": 0}


# ---------------------------------------------------------------------------
# Tests: backfill_all
# ---------------------------------------------------------------------------

class TestBackfillAll:
    def _notes(self, n: int, with_content: bool = True) -> List[Dict]:
        return [
            {
                "id": f"note_{i}",
                "content": f"Note {i} content." if with_content else "",
                "path": f"/notes/note_{i}.md",
            }
            for i in range(n)
        ]

    def test_empty_notes_list_returns_zero_totals(self):
        indexer = _indexer()
        result = _run(indexer.backfill_all([]))
        assert result == {"extracted": 0, "skipped": 0, "failed": 0}

    def test_all_empty_notes_all_skipped(self):
        indexer = _indexer()
        notes = self._notes(3, with_content=False)
        result = _run(indexer.backfill_all(notes))
        assert result["skipped"] == 3
        assert result["extracted"] == 0

    def test_valid_notes_counted_as_extracted(self):
        indexer = _indexer(entities=2)
        notes = self._notes(3)
        with patch.object(indexer, "on_note_saved", new_callable=AsyncMock) as mock_save:
            mock_save.return_value = {"entities": 2}
            result = _run(indexer.backfill_all(notes))
        assert result["extracted"] == 6  # 3 notes × 2 entities each

    def test_failed_notes_counted(self):
        indexer = _indexer()
        notes = self._notes(2)
        with patch.object(indexer, "on_note_saved", new_callable=AsyncMock) as mock_save:
            mock_save.side_effect = Exception("note fail")
            result = _run(indexer.backfill_all(notes))
        assert result["failed"] == 2

    def test_cache_invalidated_after_full_backfill(self):
        indexer = _indexer()
        notes = self._notes(2)
        with patch.object(indexer, "on_note_saved", new_callable=AsyncMock) as mock_save:
            mock_save.return_value = {"entities": 1}
            _run(indexer.backfill_all(notes))
        # Cache should be invalidated once at the end (plus once per note)
        assert indexer.index_builder.invalidate_cache.called

    def test_batching_respected(self):
        indexer = _indexer(entities=1)
        notes = self._notes(5)
        call_count = 0

        async def mock_save(content, note_id, metadata=None):
            nonlocal call_count
            call_count += 1
            return {"entities": 1}

        with patch.object(indexer, "on_note_saved", side_effect=mock_save):
            result = _run(indexer.backfill_all(notes, batch_size=2))

        assert call_count == 5  # All 5 notes processed

    def test_mixed_results(self):
        indexer = _indexer()
        notes = [
            {"id": "good", "content": "Good content"},
            {"id": "empty", "content": ""},
            {"id": "fail", "content": "Will fail"},
        ]

        async def mock_save(content, note_id, metadata=None):
            if note_id == "fail":
                raise Exception("fail")
            return {"entities": 3}

        with patch.object(indexer, "on_note_saved", side_effect=mock_save):
            result = _run(indexer.backfill_all(notes))

        assert result["extracted"] == 3   # 1 good note × 3 entities
        assert result["skipped"] == 1     # 1 empty note
        assert result["failed"] == 1      # 1 failed note

    def test_notes_without_id_use_fallback_id(self):
        indexer = _indexer()
        notes = [{"content": "Note without id"}]
        with patch.object(indexer, "on_note_saved", new_callable=AsyncMock) as mock_save:
            mock_save.return_value = {"entities": 1}
            result = _run(indexer.backfill_all(notes))
        mock_save.assert_called_once()

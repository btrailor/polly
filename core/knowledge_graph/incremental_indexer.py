"""
Incremental KG Indexer (Wave 5, Task 24)

Hooks into the note-save path to keep the KG (EntityStore + LlamaIndex tool cache)
up to date when notes are saved.

Entity extraction on note save is already wired in server.py at ~line 3683:
    entity_extractor.extract_and_store(content, source_type="note", ...)

This class adds:
1. An async wrapper so the server can await note-save entity extraction
2. PollyIndexBuilder cache invalidation after each save (so next query rebuilds
   LlamaIndex tools with the freshly extracted entities)
3. A backfill helper for batch-processing all existing notes

Usage (in server.py background task):
    kg_indexer = IncrementalKGIndexer(entity_store, entity_extractor, index_builder)
    await kg_indexer.on_note_saved(content, note_id, metadata)
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IncrementalKGIndexer:
    """
    Keeps EntityStore + LlamaIndex tool cache current with note-save events.

    This is NOT a separate indexing pipeline — it wraps the existing
    EntityExtractor.extract_and_store() and adds cache invalidation.

    Args:
        entity_store:     EntityStore instance
        entity_extractor: EntityExtractor instance (extract_and_store method)
        index_builder:    PollyIndexBuilder instance (optional, for cache invalidation)
    """

    def __init__(
        self,
        entity_store: Any,  # EntityStore
        entity_extractor: Any,  # EntityExtractor
        index_builder: Optional[Any] = None,  # PollyIndexBuilder
    ) -> None:
        self.entity_store = entity_store
        self.entity_extractor = entity_extractor
        self.index_builder = index_builder

    async def on_note_saved(
        self,
        content: str,
        note_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call when a note is saved. Extracts entities and invalidates KG cache.

        Runs entity extraction in a thread pool to avoid blocking the event loop.

        Returns:
            Dict with extraction stats (entities, relationships, etc.) or
            empty dict if extraction failed.
        """
        if not content or not content.strip():
            return {}

        try:
            stats = await asyncio.to_thread(
                self.entity_extractor.extract_and_store,
                content,
                source_type="note",
                source_id=note_id,
            )

            # Invalidate LlamaIndex tools cache — next query will rebuild with new entities
            if self.index_builder is not None:
                self.index_builder.invalidate_cache()
                logger.debug(
                    f"IncrementalKGIndexer: cache invalidated after save of '{note_id}'"
                )

            entity_count = stats.get("entities", 0) if isinstance(stats, dict) else 0
            logger.debug(
                f"IncrementalKGIndexer: extracted {entity_count} entities "
                f"from note '{note_id}'"
            )
            return stats if isinstance(stats, dict) else {"entities": 0}

        except Exception as e:
            logger.warning(
                f"IncrementalKGIndexer: entity extraction failed for '{note_id}': {e}"
            )
            return {}

    async def backfill_all(
        self,
        notes: List[Dict[str, Any]],
        batch_size: int = 20,
    ) -> Dict[str, Any]:
        """
        Backfill entity extraction for all existing notes.

        Processes notes in batches to avoid overwhelming the entity extractor.

        Args:
            notes:      List of note dicts with 'content', 'id', and optional fields
            batch_size: Number of notes to process per batch

        Returns:
            Dict with totals: {"extracted": N, "skipped": N, "failed": N}
        """
        totals = {"extracted": 0, "skipped": 0, "failed": 0}

        for i in range(0, len(notes), batch_size):
            batch = notes[i : i + batch_size]
            tasks = []
            for note in batch:
                content = note.get("content", "")
                note_id = note.get("id", note.get("path", f"note_{i}"))
                if not content or not content.strip():
                    totals["skipped"] += 1
                    continue
                tasks.append(
                    self.on_note_saved(content, str(note_id), note)
                )

            if not tasks:
                continue

            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    totals["failed"] += 1
                elif isinstance(result, dict):
                    totals["extracted"] += result.get("entities", 0)

        # Final cache invalidation after full backfill
        if self.index_builder is not None:
            self.index_builder.invalidate_cache()

        logger.info(
            f"IncrementalKGIndexer backfill complete: "
            f"{totals['extracted']} entities extracted, "
            f"{totals['skipped']} skipped, {totals['failed']} failed"
        )
        return totals

    def __repr__(self) -> str:
        has_builder = self.index_builder is not None
        return f"<IncrementalKGIndexer cache_invalidation={has_builder}>"

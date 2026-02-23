# OpenSpec: BM25 Index Persistence

**Status:** 💭 Planned  
**Priority:** P8 — Eliminate cold-start latency spike  
**Related:** `core/hybrid_search.py:BM25Index`, `core/rag.py:_rebuild_bm25_index()`, `core/rag.py:UnifiedRAG.__init__()`  
**Motivation:** The BM25 index is built lazily in memory on first hybrid search and is not persisted to disk. On every application restart or RAG reload, the full corpus must be re-tokenised and the index rebuilt from scratch. At any meaningful knowledge base size this creates a visible cold-start latency spike on the first hybrid search of a new session.

---

## Problem (Detailed)

In `core/rag.py:155–158`:

```python
# Skip BM25 index rebuild at startup to avoid blocking
# Index will be built lazily on first search if needed
if self.rag.use_hybrid_search:
    logger.info("Hybrid search enabled - BM25 index will be built on first search")
```

In `core/hybrid_search.py:100–131`, `BM25Index.index_documents()` re-tokenises every document in the corpus and builds a fresh `BM25Okapi` instance each time. For a knowledge base of 1,000 documents at 800 tokens each, this involves:

1. Loading all documents from ChromaDB (network/disk I/O)
2. Tokenising 800,000 tokens
3. Building the inverted index data structure

This takes 2–10 seconds depending on corpus size and hardware. On the first query of a session, the user experiences a noticeable delay that has nothing to do with LLM latency.

Additionally, there is no invalidation logic: if a new document is added via `rag.index_single_document()`, the BM25 index is stale but the application doesn't know it. The next hybrid search silently uses an incomplete index unless a full rebuild is triggered.

---

## Proposed Solution

**Persist the BM25 index to disk** using Python's `pickle` (or the more efficient `joblib.dump`). On startup, if a valid persisted index exists and its checksum matches the current corpus, load it directly — skipping the full rebuild. On corpus change (new document indexed, document deleted), mark the index as dirty and rebuild at the next appropriate moment (lazily or in background).

---

## Architecture

### Persistence format

The `BM25Okapi` object from `rank_bm25` is pickle-serialisable. The persisted artefact includes:

```python
@dataclass
class BM25IndexSnapshot:
    bm25: BM25Okapi                     # The index object
    corpus_docs: List[Dict]             # Document list (for result lookup)
    doc_id_to_idx: Dict[str, int]       # ID → corpus position
    tokenized_corpus: List[List[str]]   # Tokenised corpus (for incremental updates)
    corpus_checksum: str                # MD5 of sorted doc IDs — for validity check
    built_at: str                       # ISO timestamp
    doc_count: int                      # For quick staleness check
```

Stored at: `~/.polly/bm25_index.pkl` (alongside `chroma_db/`).

### Checksum Strategy

The corpus checksum is computed as:

```python
import hashlib

def _compute_corpus_checksum(doc_ids: List[str]) -> str:
    """MD5 of sorted document IDs — detects additions/removals."""
    sorted_ids = sorted(doc_ids)
    return hashlib.md5(",".join(sorted_ids).encode()).hexdigest()
```

On load, compute the current corpus's checksum by querying ChromaDB for document IDs (fast — IDs only, no content). If the checksum matches the snapshot, load the index. If it differs, rebuild.

---

## Implementation

### New class: `PersistentBM25Index` in `core/hybrid_search.py`

Extends or wraps `BM25Index` with save/load:

```python
class PersistentBM25Index(BM25Index):
    """
    BM25Index with disk persistence.
    
    Saves/loads index snapshots to avoid full rebuild on every startup.
    Tracks corpus checksum to detect staleness.
    """

    def __init__(self, index_path: str):
        super().__init__()
        self.index_path = Path(index_path)
        self._dirty: bool = False      # True if corpus changed since last save
        self._current_checksum: str = ""

    def load_if_valid(self, current_doc_ids: List[str]) -> bool:
        """
        Attempt to load persisted index.
        Returns True if loaded successfully and checksums match.
        Returns False if index is missing, corrupted, or stale.
        """
        if not self.index_path.exists():
            return False

        try:
            import pickle
            with open(self.index_path, "rb") as f:
                snapshot: BM25IndexSnapshot = pickle.load(f)

            expected_checksum = _compute_corpus_checksum(current_doc_ids)

            if snapshot.corpus_checksum != expected_checksum:
                logger.info(
                    f"BM25 index stale: "
                    f"doc_count {snapshot.doc_count} → {len(current_doc_ids)}"
                )
                return False

            # Load successful
            self.bm25 = snapshot.bm25
            self.corpus_docs = snapshot.corpus_docs
            self.doc_id_to_idx = snapshot.doc_id_to_idx
            self.tokenized_corpus = snapshot.tokenized_corpus
            self._current_checksum = snapshot.corpus_checksum
            self._dirty = False

            logger.info(
                f"BM25 index loaded from disk: "
                f"{snapshot.doc_count} documents, "
                f"built {snapshot.built_at}"
            )
            return True

        except Exception as e:
            logger.warning(f"BM25 index load failed: {e}. Will rebuild.")
            return False

    def save(self) -> bool:
        """
        Persist current index to disk.
        Returns True on success, False on failure (non-fatal).
        """
        if not self.bm25:
            return False

        try:
            import pickle
            snapshot = BM25IndexSnapshot(
                bm25=self.bm25,
                corpus_docs=self.corpus_docs,
                doc_id_to_idx=self.doc_id_to_idx,
                tokenized_corpus=self.tokenized_corpus,
                corpus_checksum=self._current_checksum,
                built_at=datetime.now().isoformat(),
                doc_count=len(self.corpus_docs),
            )

            # Atomic write: write to temp file, then rename
            tmp_path = self.index_path.with_suffix(".pkl.tmp")
            with open(tmp_path, "wb") as f:
                pickle.dump(snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            tmp_path.rename(self.index_path)

            self._dirty = False
            logger.info(f"BM25 index saved: {len(self.corpus_docs)} documents")
            return True

        except Exception as e:
            logger.warning(f"BM25 index save failed: {e}")
            return False

    def index_documents(self, documents: List[Dict]):
        """Override: build index and update checksum."""
        super().index_documents(documents)
        doc_ids = [d["id"] for d in documents]
        self._current_checksum = _compute_corpus_checksum(doc_ids)
        self._dirty = True

    def mark_dirty(self):
        """Call when a document is added/removed without full rebuild."""
        self._dirty = True
        self._current_checksum = ""  # Invalidate checksum
```

### Integration in `UnifiedRAG`

#### On init (`_init_rag()`)

```python
if self.use_hybrid_search:
    index_path = str(Path(self.db_path).parent / "bm25_index.pkl")
    self.hybrid_searcher = HybridSearcher(index_path=index_path)

    # Attempt to load from disk before lazy build
    current_doc_ids = self._get_current_doc_ids()  # fast: IDs only from ChromaDB
    if not self.hybrid_searcher.bm25_index.load_if_valid(current_doc_ids):
        logger.info("BM25 index not loaded — will build on first search")
        # Lazy build still applies as fallback
```

#### After `_rebuild_bm25_index()`

```python
def _rebuild_bm25_index(self):
    # ... existing build logic ...
    
    # Save after successful build
    if self.hybrid_searcher and self.hybrid_searcher.bm25_index:
        self.hybrid_searcher.bm25_index.save()
```

#### After `index_single_document()`

```python
def index_single_document(self, filepath: str, ...) -> bool:
    result = ...  # existing indexing logic
    
    if result and self.hybrid_searcher:
        # Mark BM25 dirty — will trigger rebuild on next search
        self.hybrid_searcher.bm25_index.mark_dirty()
        # Optionally: trigger background rebuild rather than waiting for first search
        if self.config.get("rag.bm25.rebuild_on_index", False):
            self._rebuild_bm25_index()
    
    return result
```

### Background rebuild option

For large corpora where even a lazy rebuild on first search is disruptive, offer an optional **background rebuild** on startup:

```yaml
rag:
  bm25:
    persist: true
    index_path: null          # null = auto (sibling of chroma_db)
    background_rebuild: false # If true, rebuild in background thread on startup
    rebuild_on_index: false   # If true, rebuild immediately after each index_single_document
```

When `background_rebuild: true`, the rebuild runs in a `concurrent.futures.ThreadPoolExecutor` worker. The `HybridSearcher.search()` method checks whether the background rebuild is complete before using the index; if not complete, it falls back to semantic-only search for that query.

---

## Incremental Update (Future Enhancement)

Full rebuilds on document add/remove are correct but inefficient at scale. A future enhancement is **incremental BM25 update**: when one document is added, tokenise only that document and append it to the existing `tokenized_corpus`, then rebuild the `BM25Okapi` from the appended corpus (this is O(n) but avoids the document loading step).

`rank_bm25` does not natively support incremental updates, so this would require either:
- Forking/wrapping `BM25Okapi` to support `add_document()`
- Switching to a BM25 implementation that supports incremental updates (e.g., `bm25s`)

This is out of scope for this spec but noted as a follow-on.

---

## File Size Estimate

A BM25 snapshot for 1,000 documents at ~100 tokens each averages ~5–15 MB pickled. For 5,000 documents: ~25–75 MB. This is acceptable on local storage. If the snapshot exceeds a configurable size limit (default 200 MB), fall back to always-rebuild mode.

---

## Files Touched

| File | Change |
|------|--------|
| `core/hybrid_search.py` | Add `PersistentBM25Index`, `BM25IndexSnapshot`; update `HybridSearcher` to accept `index_path` |
| `core/rag.py` | Use `PersistentBM25Index`; call `save()` after rebuild; call `mark_dirty()` after `index_single_document()` |
| `core/polly.py` | Pass `index_path` when constructing `UnifiedRAG` |
| `config/config.yaml` | Add `rag.bm25` section |

---

## Success Criteria

- [ ] After first successful build, subsequent session startups load BM25 index from disk in < 200ms
- [ ] Checksum correctly detects staleness when a new document is indexed
- [ ] Stale index triggers rebuild on next search (or background if configured)
- [ ] Atomic write (temp + rename) prevents corrupt index files on write interruption
- [ ] No regression in hybrid search quality (loaded index produces identical results to freshly-built index)
- [ ] Index file size stays within 200 MB for typical knowledge bases (< 5,000 documents)

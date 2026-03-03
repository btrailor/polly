"""
Hybrid Search Implementation for Polly RAG
Combines semantic search (vector embeddings) with keyword search (BM25)
"""

from typing import Any, List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import hashlib
import re
import math
from collections import Counter
import logging

logger = logging.getLogger(__name__)

try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    logger.warning("rank-bm25 not installed. Hybrid search will fall back to semantic-only.")
    BM25_AVAILABLE = False


@dataclass
class ScoredResult:
    """Result with multiple scoring components"""
    doc_id: str
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    title_boost: float = 0.0
    authority_score: float = 0.0
    final_score: float = 0.0
    rank_semantic: int = 999999
    rank_keyword: int = 999999


class QueryEnhancer:
    """Enhance and preprocess queries for better retrieval"""
    
    @staticmethod
    def extract_quoted_terms(query: str) -> List[str]:
        """Extract terms in quotes from query (handles both single and double quotes)"""
        # Match double quotes
        double_quoted = re.findall(r'"([^"]+)"', query)
        # Match single quotes  
        single_quoted = re.findall(r"'([^']+)'", query)
        return double_quoted + single_quoted
    
    @staticmethod
    def extract_key_terms(query: str, min_length: int = 3) -> Set[str]:
        """Extract meaningful terms from query"""
        # Remove punctuation and lowercase
        cleaned = re.sub(r'[^\w\s]', ' ', query.lower())
        
        # Split and filter
        stopwords = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are',
            'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'must', 'can', 'my', 'your', 'what', 'how', 'when',
            'where', 'why', 'who', 'concerning', 'about', 'for', 'with'
        }
        
        terms = {
            word for word in cleaned.split() 
            if len(word) >= min_length and word not in stopwords
        }
        
        return terms
    
    @staticmethod
    def enhance_for_hybrid(query: str) -> Dict[str, any]:
        """
        Enhance query for hybrid search
        Returns dict with original query, quoted terms, and key terms
        """
        quoted = QueryEnhancer.extract_quoted_terms(query)
        key_terms = QueryEnhancer.extract_key_terms(query)
        
        # Build enhanced query that emphasizes quoted terms
        enhanced_query = query
        if quoted:
            # Boost quoted terms by repeating them
            enhanced_query = query + ' ' + ' '.join(quoted * 2)
        
        return {
            'original': query,
            'enhanced': enhanced_query,
            'quoted_terms': quoted,
            'key_terms': key_terms
        }


class BM25Index:
    """BM25 index for keyword search"""
    
    def __init__(self):
        self.corpus_docs: List[Dict] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.doc_id_to_idx: Dict[str, int] = {}
    
    def index_documents(self, documents: List[Dict]):
        """
        Index documents for BM25 search
        
        Args:
            documents: List of dicts with 'id', 'content', 'filepath', 'metadata'
        """
        if not BM25_AVAILABLE:
            logger.warning("BM25 not available, skipping keyword indexing")
            return
        
        self.corpus_docs = documents
        self.tokenized_corpus = []
        self.doc_id_to_idx = {}
        
        for idx, doc in enumerate(documents):
            # Combine content and filepath for better matching
            searchable_text = doc['content'] + ' ' + doc['filepath']
            
            # Include header/title if available
            if 'metadata' in doc and 'header' in doc['metadata']:
                searchable_text = doc['metadata']['header'] + ' ' + searchable_text
            
            # Tokenize
            tokens = self._tokenize(searchable_text)
            self.tokenized_corpus.append(tokens)
            self.doc_id_to_idx[doc['id']] = idx
        
        # Build BM25 index
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        logger.info(f"Built BM25 index with {len(self.corpus_docs)} documents")
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization"""
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        # Keep apostrophes and hyphens within words
        tokens = re.findall(r'\b[\w\-\']+\b', text)
        return tokens
    
    def search(self, query: str, top_k: int = 20) -> List[Tuple[str, float]]:
        """
        Search using BM25
        
        Returns:
            List of (doc_id, score) tuples
        """
        if not self.bm25:
            return []
        
        query_tokens = self._tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k results
        top_indices = sorted(
            range(len(scores)), 
            key=lambda i: scores[i], 
            reverse=True
        )[:top_k]
        
        results = [
            (self.corpus_docs[idx]['id'], scores[idx])
            for idx in top_indices
            if scores[idx] > 0
        ]
        
        return results


@dataclass
class BM25IndexSnapshot:
    """Serialisable snapshot of a BM25 index for disk persistence (Spec 08)."""
    bm25: object                          # BM25Okapi instance
    corpus_docs: List[Dict]
    doc_id_to_idx: Dict[str, int]
    tokenized_corpus: List[List[str]]
    corpus_checksum: str
    built_at: str
    doc_count: int


def _compute_corpus_checksum(doc_ids: List[str]) -> str:
    """MD5 of sorted document IDs — detects additions/removals (Spec 08)."""
    sorted_ids = sorted(doc_ids)
    return hashlib.md5(",".join(sorted_ids).encode()).hexdigest()


class PersistentBM25Index(BM25Index):
    """
    BM25Index with disk persistence (Spec 08).

    Saves/loads index snapshots to avoid full rebuild on every startup.
    Uses a corpus checksum to detect staleness.
    Atomic writes (temp + rename) prevent corrupt files on write interruption.
    """

    MAX_FILE_SIZE_BYTES = 200 * 1024 * 1024  # 200 MB hard limit

    def __init__(self, index_path: str):
        super().__init__()
        self.index_path = Path(index_path)
        self._dirty: bool = False
        self._current_checksum: str = ""

    def load_if_valid(self, current_doc_ids: List[str]) -> bool:
        """
        Attempt to load persisted index from disk.

        Returns True if loaded and checksum matches current corpus.
        Returns False if missing, corrupted, stale, or too large.
        """
        if not self.index_path.exists():
            logger.debug("BM25 index file not found — will rebuild")
            return False

        # Guard against excessively large files
        if self.index_path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
            logger.warning(
                f"BM25 index file too large ({self.index_path.stat().st_size // (1024*1024)} MB), "
                "will rebuild"
            )
            return False

        try:
            import pickle
            with open(self.index_path, "rb") as f:
                snapshot: BM25IndexSnapshot = pickle.load(f)

            expected_checksum = _compute_corpus_checksum(current_doc_ids)

            if snapshot.corpus_checksum != expected_checksum:
                logger.info(
                    f"BM25 index stale: stored doc_count={snapshot.doc_count} "
                    f"current doc_count={len(current_doc_ids)} — rebuilding"
                )
                return False

            # Checksum matches — restore state
            self.bm25 = snapshot.bm25
            self.corpus_docs = snapshot.corpus_docs
            self.doc_id_to_idx = snapshot.doc_id_to_idx
            self.tokenized_corpus = snapshot.tokenized_corpus
            self._current_checksum = snapshot.corpus_checksum
            self._dirty = False

            logger.info(
                f"BM25 index loaded from disk: {snapshot.doc_count} documents, "
                f"built {snapshot.built_at}"
            )
            return True

        except Exception as e:
            logger.warning(f"BM25 index load failed: {e} — will rebuild")
            return False

    def save(self) -> bool:
        """
        Persist current index to disk using atomic temp+rename write.

        Returns True on success (non-fatal on failure).
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

            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = self.index_path.with_suffix(".pkl.tmp")
            with open(tmp_path, "wb") as f:
                pickle.dump(snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
            tmp_path.rename(self.index_path)

            self._dirty = False
            logger.info(f"BM25 index saved: {len(self.corpus_docs)} documents → {self.index_path}")
            return True

        except Exception as e:
            logger.warning(f"BM25 index save failed (non-fatal): {e}")
            return False

    def index_documents(self, documents: List[Dict]):
        """Build index and update checksum (overrides BM25Index.index_documents)."""
        super().index_documents(documents)
        doc_ids = [d["id"] for d in documents]
        self._current_checksum = _compute_corpus_checksum(doc_ids)
        self._dirty = True

    def mark_dirty(self):
        """Call when a document is added/removed without a full rebuild."""
        self._dirty = True
        self._current_checksum = ""  # Invalidate so next load_if_valid will rebuild


class HybridSearcher:
    """Combines semantic and keyword search with Reciprocal Rank Fusion"""
    
    def __init__(
        self,
        k_rrf: int = 60,
        index_path: Optional[str] = None,
        entity_store: Optional[Any] = None,
        authority_weight: float = 0.3,
    ):
        """
        Args:
            k_rrf: Parameter for Reciprocal Rank Fusion (typically 60)
            index_path: Optional path for BM25 index persistence (Spec 08).
                        If provided, uses PersistentBM25Index; otherwise BM25Index.
            entity_store: Optional EntityStore for authority-weighted scoring (Phase 12b).
            authority_weight: Weight of authority signal in RRF (0.0 to disable).
        """
        self.k_rrf = k_rrf
        if index_path:
            self.bm25_index: BM25Index = PersistentBM25Index(index_path)
        else:
            self.bm25_index = BM25Index()
        self.query_enhancer = QueryEnhancer()
        self.entity_store = entity_store
        self.authority_weight = authority_weight
    
    def index_for_keyword_search(self, documents: List[Dict]):
        """Build BM25 index from documents"""
        self.bm25_index.index_documents(documents)
    
    def compute_title_boost(self, filepath: str, query_terms: Set[str]) -> float:
        """
        Compute boost score if document title matches query terms
        
        Args:
            filepath: Document filepath
            query_terms: Set of important query terms
            
        Returns:
            Boost multiplier (1.0 = no boost, higher = more boost)
        """
        if not query_terms:
            return 1.0
        
        # Extract filename without extension
        filename = filepath.split('/')[-1].lower()
        filename = re.sub(r'\.\w+$', '', filename)
        
        # Tokenize filename
        filename_tokens = set(re.findall(r'\b[\w\-\']+\b', filename))
        
        # Check overlap
        matches = query_terms & filename_tokens
        
        if not matches:
            return 1.0
        
        # Boost based on proportion of query terms that match
        match_ratio = len(matches) / len(query_terms)
        
        # STRONGER boost for title matches to overcome semantic similarity:
        # - Small overlap (< 30%): 1.0-1.5x boost
        # - Medium overlap (30-70%): 1.5-3.0x boost  
        # - High overlap (> 70%): 3.0-5.0x boost
        if match_ratio < 0.3:
            boost = 1.0 + (match_ratio / 0.3) * 0.5  # Up to 1.5x
        elif match_ratio < 0.7:
            boost = 1.5 + ((match_ratio - 0.3) / 0.4) * 1.5  # 1.5x to 3.0x
        else:
            boost = 3.0 + ((match_ratio - 0.7) / 0.3) * 2.0  # 3.0x to 5.0x
        
        return boost
    
    def _compute_authority_scores(self, doc_ids: List[str], doc_metadata: Dict[str, Dict]) -> Dict[str, float]:
        """
        Compute authority scores for documents by looking up entities in their source paths.
        Returns {doc_id: max_authority_score} for documents with entity matches.
        Phase 12b: Authority scoring integration.
        """
        if not self.entity_store or self.authority_weight <= 0:
            return {}

        authority_map: Dict[str, float] = {}
        try:
            for doc_id in doc_ids:
                meta = doc_metadata.get(doc_id, {})
                filepath = meta.get('filepath', '') or meta.get('source', '')
                if not filepath:
                    continue
                # Query entity_mentions for this source document
                mentions = self.entity_store.get_mentions_for_source(filepath, 'note')
                if not mentions:
                    # Also try with just the filename
                    filename = filepath.rsplit('/', 1)[-1] if '/' in filepath else filepath
                    mentions = self.entity_store.get_mentions_for_source(filename, 'note')
                if mentions:
                    max_auth = max(m.get('authority_score', 0.0) for m in mentions)
                    authority_map[doc_id] = max_auth
        except Exception as e:
            logger.debug(f"Authority score lookup failed (non-fatal): {e}")
        return authority_map

    def reciprocal_rank_fusion(
        self,
        semantic_results: List[Tuple[str, float]],
        keyword_results: List[Tuple[str, float]],
        query_terms: Set[str],
        doc_metadata: Dict[str, Dict]
    ) -> List[Tuple[str, float, Dict]]:
        """
        Combine semantic and keyword results using Reciprocal Rank Fusion
        
        RRF formula: score(d) = Σ 1 / (k + rank(d))
        where rank(d) is the rank of document d in a result list
        
        Phase 12b adds authority scoring as a weighted additive bonus:
          final = (rrf_score * k_rrf * title_boost) + (authority_weight * authority_score)
        
        Args:
            semantic_results: List of (doc_id, score) from vector search
            keyword_results: List of (doc_id, score) from BM25 search
            query_terms: Important terms from query for title boosting
            doc_metadata: Dict mapping doc_id to metadata (including filepath)
            
        Returns:
            List of (doc_id, final_score, score_breakdown) sorted by final_score
        """
        # Build scored results dict
        scored: Dict[str, ScoredResult] = {}
        
        # Process semantic results
        for rank, (doc_id, score) in enumerate(semantic_results, start=1):
            if doc_id not in scored:
                scored[doc_id] = ScoredResult(doc_id=doc_id)
            scored[doc_id].semantic_score = score
            scored[doc_id].rank_semantic = rank
        
        # Process keyword results
        for rank, (doc_id, score) in enumerate(keyword_results, start=1):
            if doc_id not in scored:
                scored[doc_id] = ScoredResult(doc_id=doc_id)
            scored[doc_id].keyword_score = score
            scored[doc_id].rank_keyword = rank
        
        # Phase 12b: Compute authority scores for all candidate documents
        all_doc_ids = list(scored.keys())
        authority_scores = self._compute_authority_scores(all_doc_ids, doc_metadata)
        
        # Compute RRF scores and title boosts
        for doc_id, result in scored.items():
            # RRF score
            rrf_score = 0.0
            
            # Add contribution from semantic ranking
            if result.rank_semantic < 999999:
                rrf_score += 1.0 / (self.k_rrf + result.rank_semantic)
            
            # Add contribution from keyword ranking
            if result.rank_keyword < 999999:
                rrf_score += 1.0 / (self.k_rrf + result.rank_keyword)
            
            # Title boosting
            filepath = doc_metadata.get(doc_id, {}).get('filepath', '')
            title_boost = self.compute_title_boost(filepath, query_terms)
            result.title_boost = title_boost
            
            # Phase 12b: Authority bonus
            result.authority_score = authority_scores.get(doc_id, 0.0)
            authority_bonus = self.authority_weight * result.authority_score
            
            # Final score: If no keyword results, use semantic score directly to preserve quality
            # Otherwise use RRF fusion
            if not keyword_results:
                # Pure semantic search - use semantic scores directly
                result.final_score = result.semantic_score * title_boost + authority_bonus
            else:
                # Hybrid mode - normalize RRF to be comparable to semantic scores
                # Max RRF score is ~1/k_rrf for rank=1, normalize to 0-1 range
                # by multiplying by k_rrf to get scores similar to semantic
                result.final_score = (rrf_score * self.k_rrf) * title_boost + authority_bonus
        
        # Sort by final score
        sorted_results = sorted(
            scored.values(),
            key=lambda r: r.final_score,
            reverse=True
        )
        
        # Return as list of tuples with breakdown
        return [
            (
                r.doc_id,
                r.final_score,
                {
                    'semantic_score': r.semantic_score,
                    'keyword_score': r.keyword_score,
                    'title_boost': r.title_boost,
                    'authority_score': r.authority_score,
                    'rank_semantic': r.rank_semantic,
                    'rank_keyword': r.rank_keyword
                }
            )
            for r in sorted_results
        ]
    
    def search(
        self,
        query: str,
        semantic_results: List[Tuple[str, float]],
        doc_metadata: Dict[str, Dict],
        top_k: int = 10
    ) -> List[Tuple[str, float, Dict]]:
        """
        Perform hybrid search
        
        Args:
            query: User query
            semantic_results: Results from semantic/vector search as (doc_id, score)
            doc_metadata: Metadata for all documents (for title boosting)
            top_k: Number of final results to return
            
        Returns:
            List of (doc_id, final_score, score_breakdown)
        """
        # Enhance query
        enhanced = self.query_enhancer.enhance_for_hybrid(query)
        
        # Perform keyword search with enhanced query
        keyword_results = self.bm25_index.search(enhanced['enhanced'], top_k=20)
        
        logger.info(f"Hybrid search - Semantic: {len(semantic_results)} results, "
                   f"Keyword: {len(keyword_results)} results")
        
        # Fuse results
        fused_results = self.reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            enhanced['key_terms'],
            doc_metadata
        )
        
        # Log top results for debugging
        if fused_results:
            logger.info("Top 3 hybrid results:")
            for i, (doc_id, score, breakdown) in enumerate(fused_results[:3], 1):
                filepath = doc_metadata.get(doc_id, {}).get('filepath', 'unknown')
                logger.info(f"  {i}. {filepath}")
                logger.info(f"     Final: {score:.4f} | Semantic: {breakdown['semantic_score']:.3f} "
                           f"| Keyword: {breakdown['keyword_score']:.3f} "
                           f"| Title boost: {breakdown['title_boost']:.2f}x")
        
        return fused_results[:top_k]

"""
Hybrid Search Implementation for Polly RAG
Combines semantic search (vector embeddings) with keyword search (BM25)
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
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


class HybridSearcher:
    """Combines semantic and keyword search with Reciprocal Rank Fusion"""
    
    def __init__(self, k_rrf: int = 60):
        """
        Args:
            k_rrf: Parameter for Reciprocal Rank Fusion (typically 60)
        """
        self.k_rrf = k_rrf
        self.bm25_index = BM25Index()
        self.query_enhancer = QueryEnhancer()
    
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
            
            # Final score: If no keyword results, use semantic score directly to preserve quality
            # Otherwise use RRF fusion
            if not keyword_results:
                # Pure semantic search - use semantic scores directly
                result.final_score = result.semantic_score * title_boost
            else:
                # Hybrid mode - normalize RRF to be comparable to semantic scores
                # Max RRF score is ~1/k_rrf for rank=1, normalize to 0-1 range
                # by multiplying by k_rrf to get scores similar to semantic
                result.final_score = (rrf_score * self.k_rrf) * title_boost
        
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

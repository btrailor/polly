"""
Semantic Cache — stores query→response pairs with semantic embedding similarity.
"""

import os
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheHit:
    """A cached response that matched a query."""
    query: str
    response: str
    similarity: float
    age_hours: float
    metadata: Dict[str, Any]
    cache_key: str


@dataclass
class CacheStats:
    """Statistics about the cache."""
    total_entries: int
    hit_count: int
    miss_count: int
    hit_rate: float
    tokens_saved: int
    oldest_entry_hours: float
    newest_entry_hours: float


class SemanticCache:
    """
    Semantic cache for query→response pairs.
    
    Uses ChromaDB to store embeddings and responses. On lookup,
    embeds the query and finds near-matches above a similarity threshold.
    """

    def __init__(
        self,
        db_path: str,
        embed_fn: Callable[[str], List[float]],
        similarity_threshold: float = 0.92,
        max_entries: int = 500,
        ttl_hours: int = 24,
        exclude_personas: List[str] = None,
        exclude_domains: List[str] = None,
        min_response_tokens: int = 50,
    ):
        self.db_path = db_path
        self.embed_fn = embed_fn
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self.ttl_hours = ttl_hours
        self.exclude_personas = exclude_personas or []
        self.exclude_domains = exclude_domains or []
        self.min_response_tokens = min_response_tokens

        self._hit_count = 0
        self._miss_count = 0

        self._init_chroma()
        logger.info(
            f"SemanticCache initialized: threshold={similarity_threshold}, "
            f"max_entries={max_entries}, ttl={ttl_hours}h"
        )

    def _init_chroma(self):
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings

            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            self.chroma_client = chromadb.PersistentClient(
                path=self.db_path,
                settings=Settings(anonymized_telemetry=False),
            )

            self.collection = self.chroma_client.get_or_create_collection(
                name="semantic_cache",
                metadata={"description": "query→response cache"},
            )
            logger.info(f"SemanticCache ChromaDB ready: {self.collection.count()} entries")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            self.chroma_client = None
            self.collection = None

    def _should_exclude(self, query: str, persona: Optional[str] = None, domain: Optional[str] = None) -> bool:
        """Check if query should be excluded from caching."""
        query_lower = query.lower()
        
        temporal_patterns = [
            r'\btoday\b', r'\bnow\b', r'\bcurrent\b', r'\blatest\b',
            r'\bthis week\b', r'\bthis month\b', r'\byesterday\b',
            r'\btomorrow\b', r'\bweather\b', r'\btime\b',
        ]
        if any(re.search(p, query_lower) for p in temporal_patterns):
            logger.debug(f"Excluding temporal query: {query[:50]}")
            return True

        if len(query.split()) < 5:
            logger.debug(f"Excluding short query ({len(query.split())} tokens): {query[:50]}")
            return True

        if persona and persona in self.exclude_personas:
            logger.debug(f"Excluding persona {persona}")
            return True

        if domain and domain in self.exclude_domains:
            logger.debug(f"Excluding domain {domain}")
            return True

        return False

    def lookup(
        self,
        query: str,
        persona: Optional[str] = None,
        domain: Optional[str] = None,
    ) -> Optional[CacheHit]:
        """
        Look up a cached response for the query.
        
        Returns CacheHit if similarity >= threshold, None otherwise.
        """
        if not self.collection:
            return None

        try:
            query_embedding = self.embed_fn(query)
        except Exception as e:
            logger.warning(f"Failed to embed query for cache lookup: {e}")
            return None

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5,
                include=["metadatas", "documents", "distances"],
            )

            if not results or not results.get("ids") or not results["ids"][0]:
                self._miss_count += 1
                return None

            now = datetime.now()
            for i, cache_key in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                similarity = 1.0 - distance
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                cached_query = results["documents"][0][i] if results.get("documents") else ""

                if similarity < self.similarity_threshold:
                    continue

                cached_time = metadata.get("cached_at", "")
                if cached_time:
                    try:
                        cached_dt = datetime.fromisoformat(cached_time)
                        age_hours = (now - cached_dt).total_seconds() / 3600
                    except:
                        age_hours = 0.0
                else:
                    age_hours = 0.0

                if age_hours > self.ttl_hours:
                    logger.debug(f"Cache entry expired: {cache_key}")
                    continue

                response_tokens = metadata.get("response_tokens", 0)
                if response_tokens < self.min_response_tokens:
                    logger.debug(f"Excluding short response ({response_tokens} tokens)")
                    continue

                self._hit_count += 1
                logger.info(
                    f"Semantic cache HIT: similarity={similarity:.3f}, "
                    f"age={age_hours:.1f}h, query={query[:30]}..."
                )

                return CacheHit(
                    query=cached_query,
                    response=results["documents"][0][i] if results.get("documents") else "",
                    similarity=similarity,
                    age_hours=age_hours,
                    metadata=metadata,
                    cache_key=cache_key,
                )

            self._miss_count += 1
            return None

        except Exception as e:
            logger.warning(f"Cache lookup failed: {e}")
            self._miss_count += 1
            return None

    def store(
        self,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store a query→response pair in the cache."""
        if not self.collection:
            return

        if self._should_exclude(
            query,
            persona=metadata.get("persona") if metadata else None,
            domain=metadata.get("domains", [None])[0] if metadata else None,
        ):
            logger.debug(f"Query excluded from caching: {query[:30]}")
            return

        try:
            import hashlib
            cache_key = hashlib.sha256(
                f"{query}:{datetime.now().isoformat()}".encode()
            ).hexdigest()[:16]

            query_embedding = self.embed_fn(query)

            response_tokens = len(response.split()) * 1.3

            self.collection.add(
                ids=[cache_key],
                embeddings=[query_embedding],
                documents=[response],
                metadatas=[{
                    "query": query,
                    "cached_at": datetime.now().isoformat(),
                    "persona": metadata.get("persona", "") if metadata else "",
                    "domains": ",".join(metadata.get("domains", [])) if metadata else "",
                    "model": metadata.get("model", "") if metadata else "",
                    "response_tokens": int(response_tokens),
                }],
            )

            self._evict_if_needed()
            logger.debug(f"Cached response for: {query[:30]}...")

        except Exception as e:
            logger.warning(f"Failed to store in cache: {e}")

    def _evict_if_needed(self):
        """Remove oldest entries if cache exceeds max_entries."""
        if not self.collection:
            return

        try:
            count = self.collection.count()
            if count > self.max_entries:
                to_delete = count - self.max_entries
                results = self.collection.get(include=["metadatas"])
                if results and results.get("ids"):
                    sorted_entries = sorted(
                        zip(results["ids"], results.get("metadatas", [{}])),
                        key=lambda x: x[1].get("cached_at", ""),
                    )
                    ids_to_delete = [e[0] for e in sorted_entries[:to_delete]]
                    self.collection.delete(ids=ids_to_delete)
                    logger.info(f"Evicted {to_delete} old cache entries")
        except Exception as e:
            logger.warning(f"Cache eviction failed: {e}")

    def invalidate(self, older_than_hours: Optional[int] = None) -> int:
        """Invalidate cache entries older than specified hours."""
        if not self.collection:
            return 0

        try:
            results = self.collection.get(include=["metadatas"])
            if not results or not results.get("ids"):
                return 0

            now = datetime.now()
            to_delete = []
            cutoff = older_than_hours or self.ttl_hours

            for i, (cache_key, meta) in enumerate(zip(results["ids"], results.get("metadatas", []))):
                cached_at = meta.get("cached_at", "")
                if cached_at:
                    try:
                        cached_dt = datetime.fromisoformat(cached_at)
                        age_hours = (now - cached_dt).total_seconds() / 3600
                        if age_hours > cutoff:
                            to_delete.append(cache_key)
                    except:
                        pass

            if to_delete:
                self.collection.delete(ids=to_delete)
                logger.info(f"Invalidated {len(to_delete)} cache entries")
            return len(to_delete)

        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")
            return 0

    def clear(self) -> int:
        """Clear all cache entries."""
        if not self.collection:
            return 0

        try:
            count = self.collection.count()
            self.collection.delete(where={"cached_at": {"$exists": True}})
            self._hit_count = 0
            self._miss_count = 0
            logger.info(f"Cleared {count} cache entries")
            return count
        except Exception as e:
            logger.warning(f"Cache clear failed: {e}")
            return 0

    def stats(self) -> CacheStats:
        """Get cache statistics."""
        if not self.collection:
            return CacheStats(
                total_entries=0,
                hit_count=self._hit_count,
                miss_count=self._miss_count,
                hit_rate=0.0,
                tokens_saved=0,
                oldest_entry_hours=0.0,
                newest_entry_hours=0.0,
            )

        try:
            total = self.collection.count()
            results = self.collection.get(include=["metadatas"])

            oldest = 0.0
            newest = 0.0
            if results and results.get("metadatas"):
                now = datetime.now()
                ages = []
                for meta in results["metadatas"]:
                    cached_at = meta.get("cached_at", "")
                    if cached_at:
                        try:
                            cached_dt = datetime.fromisoformat(cached_at)
                            age_hours = (now - cached_dt).total_seconds() / 3600
                            ages.append(age_hours)
                        except:
                            pass
                if ages:
                    oldest = max(ages)
                    newest = min(ages)

            total_requests = self._hit_count + self._miss_count
            hit_rate = self._hit_count / total_requests if total_requests > 0 else 0.0

            tokens_saved = 0
            if results and results.get("metadatas"):
                for meta in results["metadatas"]:
                    tokens_saved += meta.get("response_tokens", 0)
            tokens_saved = int(tokens_saved * hit_rate)

            return CacheStats(
                total_entries=total,
                hit_count=self._hit_count,
                miss_count=self._miss_count,
                hit_rate=hit_rate,
                tokens_saved=tokens_saved,
                oldest_entry_hours=oldest,
                newest_entry_hours=newest,
            )

        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return CacheStats(
                total_entries=0,
                hit_count=self._hit_count,
                miss_count=self._miss_count,
                hit_rate=0.0,
                tokens_saved=0,
                oldest_entry_hours=0.0,
                newest_entry_hours=0.0,
            )


# Global instance for API access
_semantic_cache: Optional[SemanticCache] = None


def get_semantic_cache() -> Optional[SemanticCache]:
    """Get the global SemanticCache instance."""
    return _semantic_cache


def init_semantic_cache(cache: SemanticCache) -> None:
    """Initialize the global SemanticCache instance."""
    global _semantic_cache
    _semantic_cache = cache


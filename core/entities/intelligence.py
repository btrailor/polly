"""
Graph Intelligence Module — Phase 12b Wave 3.

Pure-Python implementations of:
  - Community detection (label propagation)
  - PageRank + betweenness centrality
  - Multi-factor edge confidence scoring

No external graph libraries required (no networkx, igraph, scipy).
"""

from __future__ import annotations

import logging
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


# ── Adjacency helpers ────────────────────────────────────────────────


def _load_adjacency(entity_store) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    """Load all entities and relationships into an adjacency dict.

    Returns (node_ids, adj) where adj[u][v] = edge_weight (undirected).
    """
    conn = entity_store._conn()
    cur = conn.execute("SELECT id FROM entities ORDER BY id")
    node_ids = [row[0] for row in cur.fetchall()]

    adj: Dict[str, Dict[str, float]] = defaultdict(dict)
    cur = conn.execute("SELECT source_id, target_id, strength FROM relationships")
    for src, tgt, strength in cur.fetchall():
        w = max(0.01, strength or 1.0)
        adj[src][tgt] = w
        adj[tgt][src] = w  # treat as undirected for community / centrality

    return node_ids, dict(adj)


def _load_directed_adjacency(entity_store) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    """Directed adjacency: adj[source][target] = weight."""
    conn = entity_store._conn()
    cur = conn.execute("SELECT id FROM entities ORDER BY id")
    node_ids = [row[0] for row in cur.fetchall()]

    adj: Dict[str, Dict[str, float]] = defaultdict(dict)
    cur = conn.execute("SELECT source_id, target_id, strength FROM relationships")
    for src, tgt, strength in cur.fetchall():
        w = max(0.01, strength or 1.0)
        adj[src][tgt] = w

    return node_ids, dict(adj)


# ── Task 11: Community Detection ─────────────────────────────────────


class CommunityDetector:
    """Label propagation community detection (pure Python)."""

    def detect(
        self,
        entity_store,
        min_community_size: int = 3,
        max_iterations: int = 50,
    ) -> Dict[int, List[str]]:
        """Run label propagation and write community_id back to entities.

        1. Load adjacency from EntityStore
        2. Initialize each node with its own unique label
        3. Iterate: each node adopts the most common weighted-neighbor label
        4. Converge when no labels change (or max_iterations)
        5. Filter out communities smaller than min_community_size
        6. Write community_id to entities table

        Returns {community_id: [entity_ids]}.
        """
        node_ids, adj = _load_adjacency(entity_store)
        if not node_ids:
            return {}

        # Initialize labels: each node gets its index as label
        labels: Dict[str, int] = {nid: i for i, nid in enumerate(node_ids)}

        for iteration in range(max_iterations):
            changed = False
            # Deterministic order for reproducibility
            for nid in node_ids:
                neighbors = adj.get(nid, {})
                if not neighbors:
                    continue
                # Weighted vote: accumulate label weights
                label_weights: Dict[int, float] = defaultdict(float)
                for neighbor, weight in neighbors.items():
                    if neighbor in labels:
                        label_weights[labels[neighbor]] += weight
                if not label_weights:
                    continue
                # Pick label with max weight (deterministic tie-break: lowest label)
                max_weight = max(label_weights.values())
                candidates = [lb for lb, w in label_weights.items() if w == max_weight]
                best = min(candidates)  # deterministic tie-break
                if labels[nid] != best:
                    labels[nid] = best
                    changed = True

            if not changed:
                logger.debug(f"Label propagation converged at iteration {iteration + 1}")
                break

        # Group by label
        communities_raw: Dict[int, List[str]] = defaultdict(list)
        for nid, label in labels.items():
            communities_raw[label].append(nid)

        # Filter by min_community_size and renumber
        communities: Dict[int, List[str]] = {}
        cid = 0
        for label in sorted(communities_raw.keys()):
            members = communities_raw[label]
            if len(members) >= min_community_size:
                communities[cid] = members
                cid += 1

        # Write back to DB
        with entity_store._conn() as conn:
            # Reset all to NULL first
            conn.execute("UPDATE entities SET community_id = NULL")
            for community_id, member_ids in communities.items():
                for eid in member_ids:
                    conn.execute(
                        "UPDATE entities SET community_id = ? WHERE id = ?",
                        (community_id, eid),
                    )
            conn.commit()

        logger.info(
            f"Community detection: {len(communities)} communities "
            f"({sum(len(m) for m in communities.values())} nodes clustered)"
        )
        return communities


# ── Task 12: PageRank + Betweenness Centrality ──────────────────────


class CentralityComputer:
    """Pure-Python centrality metrics."""

    def pagerank(
        self,
        entity_store,
        damping: float = 0.85,
        iterations: int = 100,
        tolerance: float = 1e-6,
    ) -> Dict[str, float]:
        """Power-iteration PageRank.

        Uses directed adjacency (source → target).
        Writes pagerank_score to entities table.
        Returns {entity_id: score}.
        """
        node_ids, adj = _load_directed_adjacency(entity_store)
        n = len(node_ids)
        if n == 0:
            return {}

        # Out-degree for each node
        out_degree: Dict[str, float] = {}
        for nid in node_ids:
            out_degree[nid] = sum(adj.get(nid, {}).values()) or 1.0

        # Build reverse adjacency for efficient iteration
        reverse_adj: Dict[str, Dict[str, float]] = defaultdict(dict)
        for src, targets in adj.items():
            for tgt, w in targets.items():
                reverse_adj[tgt][src] = w

        # Initialize
        rank = {nid: 1.0 / n for nid in node_ids}

        for _iter in range(iterations):
            new_rank: Dict[str, float] = {}
            for nid in node_ids:
                incoming_sum = 0.0
                for src, w in reverse_adj.get(nid, {}).items():
                    if src in rank:
                        incoming_sum += rank[src] * w / out_degree.get(src, 1.0)
                new_rank[nid] = (1.0 - damping) / n + damping * incoming_sum

            # Check convergence
            diff = sum(abs(new_rank[nid] - rank[nid]) for nid in node_ids)
            rank = new_rank
            if diff < tolerance:
                logger.debug(f"PageRank converged at iteration {_iter + 1}")
                break

        # Normalize to [0, 1]
        max_rank = max(rank.values()) if rank else 1.0
        if max_rank > 0:
            rank = {nid: v / max_rank for nid, v in rank.items()}

        # Write to DB
        with entity_store._conn() as conn:
            for eid, score in rank.items():
                conn.execute(
                    "UPDATE entities SET pagerank_score = ? WHERE id = ?",
                    (score, eid),
                )
            conn.commit()

        logger.info(f"PageRank computed for {len(rank)} entities")
        return rank

    def betweenness_centrality(
        self,
        entity_store,
        sample_size: int = 100,
    ) -> Dict[str, float]:
        """Approximate betweenness via BFS from random source sampling.

        Counts how many shortest paths pass through each intermediate node.
        Writes betweenness_score to entities table.
        Returns {entity_id: score}.
        """
        node_ids, adj = _load_adjacency(entity_store)
        n = len(node_ids)
        if n == 0:
            return {}

        betweenness: Dict[str, float] = {nid: 0.0 for nid in node_ids}

        # Sample sources
        sources = node_ids[:] if n <= sample_size else random.sample(node_ids, sample_size)

        for source in sources:
            # BFS from source — track predecessors for shortest-path reconstruction
            dist: Dict[str, int] = {source: 0}
            sigma: Dict[str, int] = {source: 1}  # number of shortest paths
            preds: Dict[str, List[str]] = defaultdict(list)
            order: List[str] = []  # BFS visit order

            queue = [source]
            while queue:
                next_level = []
                for v in queue:
                    order.append(v)
                    for w in adj.get(v, {}):
                        if w not in dist:
                            dist[w] = dist[v] + 1
                            next_level.append(w)
                        if dist.get(w) == dist[v] + 1:
                            sigma[w] = sigma.get(w, 0) + sigma[v]
                            preds[w].append(v)
                queue = next_level

            # Accumulate dependency (Brandes algorithm)
            delta: Dict[str, float] = {nid: 0.0 for nid in order}
            for w in reversed(order):
                if w == source:
                    continue
                for v in preds.get(w, []):
                    frac = sigma.get(v, 1) / max(sigma.get(w, 1), 1)
                    delta[v] = delta.get(v, 0.0) + frac * (1.0 + delta.get(w, 0.0))
                betweenness[w] = betweenness.get(w, 0.0) + delta.get(w, 0.0)

        # Normalize to [0, 1]
        max_bc = max(betweenness.values()) if betweenness else 1.0
        if max_bc > 0:
            betweenness = {nid: v / max_bc for nid, v in betweenness.items()}
        else:
            betweenness = {nid: 0.0 for nid in node_ids}

        # Write to DB
        with entity_store._conn() as conn:
            for eid, score in betweenness.items():
                conn.execute(
                    "UPDATE entities SET betweenness_score = ? WHERE id = ?",
                    (score, eid),
                )
            conn.commit()

        logger.info(f"Betweenness centrality computed for {len(betweenness)} entities")
        return betweenness


# ── Task 14: Edge Confidence Scoring ─────────────────────────────────


@dataclass
class EdgeConfidence:
    """Multi-factor edge confidence result."""

    composite: float = 0.0
    co_occurrence: float = 0.0
    semantic_similarity: float = 0.0
    temporal_proximity: float = 0.0
    structural_proximity: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "composite": round(self.composite, 4),
            "co_occurrence": round(self.co_occurrence, 4),
            "semantic_similarity": round(self.semantic_similarity, 4),
            "temporal_proximity": round(self.temporal_proximity, 4),
            "structural_proximity": round(self.structural_proximity, 4),
        }


class EdgeConfidenceScorer:
    """Multi-factor edge confidence scoring."""

    def __init__(self, entity_store, weights: Optional[Dict[str, float]] = None):
        self.entity_store = entity_store
        self.weights = weights or {
            "co_occurrence": 0.35,
            "semantic_similarity": 0.25,
            "temporal_proximity": 0.15,
            "structural_proximity": 0.25,
        }

    def score(self, source_id: str, target_id: str) -> EdgeConfidence:
        """Compute multi-factor edge confidence between two entities."""
        co_occ = self._co_occurrence(source_id, target_id)
        sem_sim = self._semantic_similarity(source_id, target_id)
        temp_prox = self._temporal_proximity(source_id, target_id)
        struct_prox = self._structural_proximity(source_id, target_id)

        composite = (
            self.weights.get("co_occurrence", 0.35) * co_occ
            + self.weights.get("semantic_similarity", 0.25) * sem_sim
            + self.weights.get("temporal_proximity", 0.15) * temp_prox
            + self.weights.get("structural_proximity", 0.25) * struct_prox
        )

        return EdgeConfidence(
            composite=min(1.0, composite),
            co_occurrence=co_occ,
            semantic_similarity=sem_sim,
            temporal_proximity=temp_prox,
            structural_proximity=struct_prox,
        )

    def _co_occurrence(self, source_id: str, target_id: str) -> float:
        """How many shared documents, normalized by max co-occurrence in graph."""
        conn = self.entity_store._conn()

        # Count shared documents for this pair
        cur = conn.execute(
            """
            SELECT COUNT(DISTINCT a.source_id)
            FROM entity_mentions a
            INNER JOIN entity_mentions b
              ON a.source_type = b.source_type AND a.source_id = b.source_id
            WHERE a.entity_id = ? AND b.entity_id = ?
            """,
            (source_id, target_id),
        )
        shared = cur.fetchone()[0]

        if shared == 0:
            return 0.0

        # Max co-occurrence across all entity pairs (approximate via max mentions per source)
        cur = conn.execute(
            """
            SELECT MAX(pair_count) FROM (
                SELECT COUNT(DISTINCT entity_id) AS pair_count
                FROM entity_mentions
                GROUP BY source_type, source_id
            )
            """
        )
        max_entities_per_doc = cur.fetchone()[0] or 1
        # Normalize: shared docs / (some reasonable max)
        return min(1.0, shared / max(1, max_entities_per_doc))

    def _semantic_similarity(self, source_id: str, target_id: str) -> float:
        """Simple text overlap similarity of entity descriptions.

        Uses token overlap (Jaccard-like) as a lightweight proxy.
        """
        src = self.entity_store.get_entity(source_id)
        tgt = self.entity_store.get_entity(target_id)
        if not src or not tgt:
            return 0.0

        src_text = f"{src.description} {' '.join(src.aliases)} {' '.join(src.domains)}".lower()
        tgt_text = f"{tgt.description} {' '.join(tgt.aliases)} {' '.join(tgt.domains)}".lower()

        src_tokens = set(src_text.split())
        tgt_tokens = set(tgt_text.split())

        if not src_tokens or not tgt_tokens:
            return 0.0

        intersection = src_tokens & tgt_tokens
        union = src_tokens | tgt_tokens
        return len(intersection) / len(union) if union else 0.0

    def _temporal_proximity(self, source_id: str, target_id: str) -> float:
        """1 / (1 + days_between_first_mentions)."""
        conn = self.entity_store._conn()

        cur = conn.execute(
            "SELECT MIN(created) FROM entity_mentions WHERE entity_id = ?",
            (source_id,),
        )
        row_a = cur.fetchone()
        cur = conn.execute(
            "SELECT MIN(created) FROM entity_mentions WHERE entity_id = ?",
            (target_id,),
        )
        row_b = cur.fetchone()

        if not row_a or not row_a[0] or not row_b or not row_b[0]:
            return 0.5  # unknown → neutral

        try:
            dt_a = datetime.fromisoformat(row_a[0])
            dt_b = datetime.fromisoformat(row_b[0])
            days_apart = abs((dt_a - dt_b).total_seconds()) / 86400.0
            return 1.0 / (1.0 + days_apart)
        except (ValueError, TypeError):
            return 0.5

    def _structural_proximity(self, source_id: str, target_id: str) -> float:
        """1 / (1 + shortest_path_length). Adjacent → 0.5, direct → 1.0."""
        if source_id == target_id:
            return 1.0
        path = self.entity_store.find_path(source_id, target_id, max_hops=4)
        if path is None:
            return 0.0
        hops = len(path)
        return 1.0 / (1.0 + hops)

    def score_all_edges(self) -> List[Dict[str, Any]]:
        """Score all existing relationships. Returns list of scored edges."""
        conn = self.entity_store._conn()
        cur = conn.execute("SELECT DISTINCT source_id, target_id FROM relationships")
        results = []
        for src, tgt in cur.fetchall():
            conf = self.score(src, tgt)
            results.append({
                "source_id": src,
                "target_id": tgt,
                **conf.to_dict(),
            })
        return results

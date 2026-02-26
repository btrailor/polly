"""
Polly Knowledge Graph — LlamaIndex Integration (Wave 5, Task 24)

Provides:
  - PollyEntityGraphStore: bridges EntityStore (SQLite) to LlamaIndex PropertyGraphStore
  - PollyIndexBuilder: builds LlamaIndex query engine tools from ChromaDB + EntityStore
  - QueryDecomposerV2: drop-in QueryDecomposer replacement using SubQuestionQueryEngine
  - IncrementalKGIndexer: keeps KG current as notes are saved

All LlamaIndex imports are lazy (inside methods) to avoid startup cost.
If llama-index-core is not installed, QueryDecomposerV2 falls back to V1.
"""

from core.knowledge_graph.graph_store import PollyEntityGraphStore
from core.knowledge_graph.incremental_indexer import IncrementalKGIndexer
from core.knowledge_graph.index_builder import PollyIndexBuilder
from core.knowledge_graph.query_decomposition_v2 import QueryDecomposerV2

__all__ = [
    "PollyEntityGraphStore",
    "PollyIndexBuilder",
    "QueryDecomposerV2",
    "IncrementalKGIndexer",
]

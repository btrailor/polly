"""
Polly Index Builder — LlamaIndex Query Engine Tools (Wave 5, Task 24)

Builds LlamaIndex query engine tools from existing Polly infrastructure:
  - Each ChromaDB collection → VectorStoreIndex → QueryEngineTool
  - EntityStore → PollyEntityGraphStore → PropertyGraphIndex → QueryEngineTool

All tools are assembled for SubQuestionQueryEngine consumption.
Tools are lazy-built and cached after first call to build_tools().

CRITICAL: The embedding model MUST match the model used when ChromaDB collections
were originally populated. A mismatch produces garbage similarity scores.
Read from config.get("rag.embedding_model", "nomic-embed-text").
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Tool descriptions used by SubQuestionQueryEngine to route sub-questions
TOOL_DESCRIPTIONS: Dict[str, str] = {
    "notes": (
        "Personal notes and knowledge base entries. Use for questions about "
        "saved information, observations, insights, or personal knowledge. "
        "Best for 'what have I written about X' or 'find my notes on Y'."
    ),
    "codebase": (
        "Source code, functions, and technical implementations. Use for questions "
        "about code structure, function signatures, implementations, or technical "
        "details from indexed repositories."
    ),
    "documents": (
        "Documents, articles, and reference materials. Use for questions about "
        "external resources, documentation, or reference content."
    ),
    "patterns": (
        "Learned patterns and recurring workflows. Use for questions about "
        "established practices, recurring approaches, or pattern recognition."
    ),
    "knowledge_graph": (
        "Entity relationships and knowledge graph. Use for questions about how "
        "concepts relate, entity connections, domain structures, or relationship "
        "traversal. Best for 'how does X relate to Y' or 'what connects X and Z'."
    ),
}


class PollyIndexBuilder:
    """
    Builds LlamaIndex query engine tools from existing Polly infrastructure.

    Usage:
        builder = PollyIndexBuilder(config, entity_store, chroma_client)
        tools = builder.build_tools()  # returns List[QueryEngineTool], cached
        # Pass tools to SubQuestionQueryEngine in QueryDecomposerV2

    The builder is intentionally lazy: tools are not created until build_tools()
    is first called, avoiding LlamaIndex import overhead at startup.
    """

    def __init__(
        self,
        config: Dict[str, Any],
        entity_store: Any,  # EntityStore
        chroma_client: Any,  # chromadb.Client
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config = config
        self.entity_store = entity_store
        self.chroma_client = chroma_client
        self.llm_config = llm_config or {}
        self._tools: Optional[List[Any]] = None  # cached after first build
        self._embedding_model: Optional[Any] = None
        self._llm: Optional[Any] = None

    # ---- LLM + Embedding builders ----

    def _build_llm(self) -> Any:
        """Build LiteLLM adapter for LlamaIndex using the decomposition model tier."""
        if self._llm is not None:
            return self._llm

        from llama_index.llms.litellm import LiteLLM

        tier = self.config.get("routing", {}).get("wave5", {}).get(
            "llamaindex", {}
        ).get("llm_tier", "fast")

        # Map tier → model string (matching polly's config.models.local)
        models = self.config.get("models", {}).get("local", {})
        tier_to_key = {"fast": "fast", "balanced": "balanced", "thorough": "quality"}
        model_key = tier_to_key.get(tier, "fast")
        model_name = models.get(model_key, "ollama/llama3.2:latest")

        # Ensure ollama/ prefix for LiteLLM
        if not model_name.startswith("ollama/") and "/" not in model_name:
            model_name = f"ollama/{model_name}"

        try:
            self._llm = LiteLLM(
                model=model_name,
                max_tokens=1024,
                temperature=0.1,
            )
            logger.debug(f"PollyIndexBuilder: LLM = {model_name}")
        except Exception as e:
            logger.warning(f"PollyIndexBuilder: LiteLLM init failed ({e}), falling back to None")
            self._llm = None

        return self._llm

    def _build_embedding(self) -> Any:
        """
        Build Ollama embedding adapter matching the existing ChromaDB embedding model.

        CRITICAL: This MUST use the same model used when collections were indexed.
        Reads from config.rag.embedding_model (default: "nomic-embed-text").
        Mismatch = garbage similarity scores.
        """
        if self._embedding_model is not None:
            return self._embedding_model

        from llama_index.embeddings.ollama import OllamaEmbedding

        embedding_model = self.config.get("rag", {}).get(
            "embedding_model", "nomic-embed-text"
        )
        ollama_base_url = self.config.get("models", {}).get(
            "local", {}
        ).get("base_url", "http://localhost:11434")

        try:
            self._embedding_model = OllamaEmbedding(
                model_name=embedding_model,
                base_url=ollama_base_url,
            )
            logger.debug(
                f"PollyIndexBuilder: embedding = {embedding_model} @ {ollama_base_url}"
            )
        except Exception as e:
            logger.warning(
                f"PollyIndexBuilder: OllamaEmbedding init failed ({e}), "
                "vector tools will be unavailable"
            )
            self._embedding_model = None

        return self._embedding_model

    # ---- Tool builders ----

    def _build_chroma_tool(self, collection_name: str, description: str) -> Optional[Any]:
        """
        Wrap a ChromaDB collection as a LlamaIndex VectorStoreIndex QueryEngineTool.

        Uses from_vector_store=True — does NOT re-embed documents; uses existing vectors.
        Returns None if the collection is empty or unavailable.
        """
        from llama_index.core import VectorStoreIndex
        from llama_index.core.tools import QueryEngineTool, ToolMetadata
        from llama_index.vector_stores.chroma import ChromaVectorStore

        try:
            collection = self.chroma_client.get_or_create_collection(collection_name)
        except Exception as e:
            logger.warning(f"PollyIndexBuilder: could not get collection '{collection_name}': {e}")
            return None

        # Skip empty collections — LlamaIndex raises if there's nothing to query
        try:
            count = collection.count()
            if count == 0:
                logger.debug(f"PollyIndexBuilder: skipping empty collection '{collection_name}'")
                return None
        except Exception:
            pass

        try:
            vector_store = ChromaVectorStore(chroma_collection=collection)
            embed_model = self._build_embedding()
            llm = self._build_llm()

            index = VectorStoreIndex.from_vector_store(
                vector_store=vector_store,
                embed_model=embed_model,
            )

            query_kwargs: Dict[str, Any] = {}
            if llm is not None:
                query_kwargs["llm"] = llm

            query_engine = index.as_query_engine(**query_kwargs)

            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(name=collection_name, description=description),
            )
            logger.debug(
                f"PollyIndexBuilder: built ChromaDB tool '{collection_name}' "
                f"({count} chunks)"
            )
            return tool
        except Exception as e:
            logger.warning(
                f"PollyIndexBuilder: failed to build tool for '{collection_name}': {e}"
            )
            return None

    def _build_kg_tool(self) -> Optional[Any]:
        """
        Build a PropertyGraphIndex QueryEngineTool backed by PollyEntityGraphStore.

        Returns None if the EntityStore has no entities (fresh install).
        """
        from llama_index.core.tools import QueryEngineTool, ToolMetadata

        from core.knowledge_graph.graph_store import PollyEntityGraphStore

        try:
            stats = self.entity_store.get_stats()
            entity_count = stats.get("entities", 0)
        except Exception:
            entity_count = 0

        if entity_count == 0:
            logger.debug("PollyIndexBuilder: skipping KG tool — EntityStore is empty")
            return None

        try:
            from llama_index.core.indices.property_graph import PropertyGraphIndex

            graph_store = PollyEntityGraphStore(self.entity_store)
            embed_model = self._build_embedding()
            llm = self._build_llm()

            index = PropertyGraphIndex.from_existing(
                property_graph_store=graph_store,
                embed_model=embed_model,
                llm=llm,
            )

            query_kwargs: Dict[str, Any] = {
                "include_text": True,
                "response_mode": "tree_summarize",
            }
            if llm is not None:
                query_kwargs["llm"] = llm

            query_engine = index.as_query_engine(**query_kwargs)

            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name="knowledge_graph",
                    description=TOOL_DESCRIPTIONS["knowledge_graph"],
                ),
            )
            logger.debug(
                f"PollyIndexBuilder: built KG tool ({entity_count} entities)"
            )
            return tool
        except Exception as e:
            logger.warning(f"PollyIndexBuilder: failed to build KG tool: {e}")
            return None

    # ---- Main entry point ----

    def build_tools(
        self, collections: Optional[List[str]] = None
    ) -> List[Any]:
        """
        Build all query engine tools. Results are cached after first call.

        Tools are built for each collection in `collections` plus the KG.
        Collections that are empty or unavailable are silently skipped.

        Args:
            collections: ChromaDB collection names to include. Defaults to
                         the list from config.routing.wave5.llamaindex.collections
                         or ["notes", "codebase", "documents", "patterns"].

        Returns:
            List of QueryEngineTool objects (may be empty if all failed).
        """
        if self._tools is not None:
            return self._tools

        if collections is None:
            collections = (
                self.config.get("routing", {})
                .get("wave5", {})
                .get("llamaindex", {})
                .get("collections", ["notes", "codebase", "documents", "patterns"])
            )

        tools: List[Any] = []

        for name in collections:
            desc = TOOL_DESCRIPTIONS.get(name, f"Collection: {name}")
            tool = self._build_chroma_tool(name, desc)
            if tool is not None:
                tools.append(tool)

        # Add KG tool if enabled in config
        kg_enabled = (
            self.config.get("routing", {})
            .get("wave5", {})
            .get("llamaindex", {})
            .get("kg_enabled", True)
        )
        if kg_enabled:
            kg_tool = self._build_kg_tool()
            if kg_tool is not None:
                tools.append(kg_tool)

        self._tools = tools
        logger.info(
            f"PollyIndexBuilder: built {len(tools)} query engine tools "
            f"({[t.metadata.name for t in tools]})"
        )
        return tools

    def invalidate_cache(self) -> None:
        """Clear the tools cache so next build_tools() call rebuilds from scratch."""
        self._tools = None
        logger.debug("PollyIndexBuilder: tools cache invalidated")

    def __repr__(self) -> str:
        n = len(self._tools) if self._tools is not None else "unbuilt"
        return f"<PollyIndexBuilder {n} tools>"

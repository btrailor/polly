"""
Conftest for test_knowledge_graph.

Injects lightweight sys.modules mocks for llama_index so tests run without
the optional llama-index-core package installed.

All mock objects expose the attributes that production code accesses,
with enough fidelity to exercise the logic without real LLM/vector calls.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock


def _make_module(name: str, **attrs) -> types.ModuleType:
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


# ---------------------------------------------------------------------------
# LlamaIndex type stubs
# ---------------------------------------------------------------------------

class _EntityNode:
    def __init__(self, *, name: str, label: str = "", properties: dict = None):
        self.name = name
        self.label = label
        self.properties = properties or {}
        self.id = name  # LlamaIndex uses name as node id


class _Relation:
    def __init__(self, *, label: str, source_id: str, target_id: str, properties: dict = None):
        self.label = label
        self.source_id = source_id
        self.target_id = target_id
        self.properties = properties or {}


class _LabelledNode:
    pass


class _ToolMetadata:
    def __init__(self, *, name: str, description: str = ""):
        self.name = name
        self.description = description


class _QueryEngineTool:
    def __init__(self, *, query_engine, metadata):
        self.query_engine = query_engine
        self.metadata = metadata


class _SubQuestionQueryEngine:
    @classmethod
    def from_defaults(cls, **kwargs):
        inst = cls()
        return inst

    def query(self, query_str: str):
        response = MagicMock()
        response.metadata = {}
        return response


class _LLMQuestionGenerator:
    @classmethod
    def from_defaults(cls, **kwargs):
        return cls()


class _VectorStoreIndex:
    @classmethod
    def from_vector_store(cls, **kwargs):
        inst = cls()
        inst.as_query_engine = lambda **kw: MagicMock()
        return inst


class _PropertyGraphIndex:
    @classmethod
    def from_existing(cls, **kwargs):
        inst = cls()
        inst.as_query_engine = lambda **kw: MagicMock()
        return inst


class _ChromaVectorStore:
    def __init__(self, *, chroma_collection):
        self.chroma_collection = chroma_collection


class _OllamaEmbedding:
    def __init__(self, *, model_name: str, base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url


class _LiteLLM:
    def __init__(self, *, model: str, max_tokens: int = 1024, temperature: float = 0.1):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature


# ---------------------------------------------------------------------------
# Module hierarchy injection
# ---------------------------------------------------------------------------

def _inject_llama_index_mocks():
    """Inject stub modules into sys.modules so lazy imports in production code work."""

    # llama_index.core.graph_stores.types
    graph_types_mod = _make_module(
        "llama_index.core.graph_stores.types",
        EntityNode=_EntityNode,
        Relation=_Relation,
        LabelledNode=_LabelledNode,
    )

    # llama_index.core.tools
    tools_mod = _make_module(
        "llama_index.core.tools",
        QueryEngineTool=_QueryEngineTool,
        ToolMetadata=_ToolMetadata,
    )

    # llama_index.core.query_engine
    query_engine_mod = _make_module(
        "llama_index.core.query_engine",
        SubQuestionQueryEngine=_SubQuestionQueryEngine,
    )

    # llama_index.core.question_gen
    question_gen_mod = _make_module(
        "llama_index.core.question_gen",
        LLMQuestionGenerator=_LLMQuestionGenerator,
    )

    # llama_index.core.indices.property_graph
    pg_mod = _make_module(
        "llama_index.core.indices.property_graph",
        PropertyGraphIndex=_PropertyGraphIndex,
    )

    # llama_index.core.indices
    indices_mod = _make_module(
        "llama_index.core.indices",
        property_graph=pg_mod,
    )

    # llama_index.core (top-level with VectorStoreIndex)
    core_mod = _make_module(
        "llama_index.core",
        VectorStoreIndex=_VectorStoreIndex,
        tools=tools_mod,
        query_engine=query_engine_mod,
        question_gen=question_gen_mod,
        indices=indices_mod,
        graph_stores=_make_module("llama_index.core.graph_stores", types=graph_types_mod),
    )

    # llama_index.core.graph_stores
    graph_stores_mod = _make_module(
        "llama_index.core.graph_stores",
        types=graph_types_mod,
    )

    # llama_index.vector_stores.chroma
    chroma_vs_mod = _make_module(
        "llama_index.vector_stores.chroma",
        ChromaVectorStore=_ChromaVectorStore,
    )

    # llama_index.vector_stores
    vector_stores_mod = _make_module(
        "llama_index.vector_stores",
        chroma=chroma_vs_mod,
    )

    # llama_index.embeddings.ollama
    ollama_emb_mod = _make_module(
        "llama_index.embeddings.ollama",
        OllamaEmbedding=_OllamaEmbedding,
    )

    # llama_index.embeddings
    embeddings_mod = _make_module(
        "llama_index.embeddings",
        ollama=ollama_emb_mod,
    )

    # llama_index.llms.litellm
    litellm_llms_mod = _make_module(
        "llama_index.llms.litellm",
        LiteLLM=_LiteLLM,
    )

    # llama_index.llms
    llms_mod = _make_module(
        "llama_index.llms",
        litellm=litellm_llms_mod,
    )

    # llama_index (root)
    llama_index_mod = _make_module(
        "llama_index",
        core=core_mod,
        vector_stores=vector_stores_mod,
        embeddings=embeddings_mod,
        llms=llms_mod,
    )

    # Register everything
    mods = {
        "llama_index": llama_index_mod,
        "llama_index.core": core_mod,
        "llama_index.core.graph_stores": graph_stores_mod,
        "llama_index.core.graph_stores.types": graph_types_mod,
        "llama_index.core.tools": tools_mod,
        "llama_index.core.query_engine": query_engine_mod,
        "llama_index.core.question_gen": question_gen_mod,
        "llama_index.core.indices": indices_mod,
        "llama_index.core.indices.property_graph": pg_mod,
        "llama_index.vector_stores": vector_stores_mod,
        "llama_index.vector_stores.chroma": chroma_vs_mod,
        "llama_index.embeddings": embeddings_mod,
        "llama_index.embeddings.ollama": ollama_emb_mod,
        "llama_index.llms": llms_mod,
        "llama_index.llms.litellm": litellm_llms_mod,
    }

    for name, mod in mods.items():
        if name not in sys.modules:
            sys.modules[name] = mod

    return mods


# Inject at import time so that any subsequent `import llama_index.*` in
# production code (lazy imports inside methods) resolves to the stubs.
_INJECTED = _inject_llama_index_mocks()

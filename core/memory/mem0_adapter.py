"""
Mem0 Adaptive Memory Adapter

Provides a unified interface to Mem0's adaptive memory system with:
- Entity extraction and relationship mapping
- Multi-level memory (user, session, agent)
- Semantic search with reranking
- Memory decay and relevance scoring

This adapter integrates with:
- Knowledge Writer: Entity extraction from saved notes
- Pattern Learning: Semantic pattern search and storage
- Personas: Per-persona memory for context-aware responses
- RAG: Complementary to existing vector search
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


class Mem0Adapter:
    """
    Adapter for Mem0 adaptive memory system.
    
    Example usage:
        >>> config = {
        ...     'memory': {
        ...         'provider': 'mem0',
        ...         'mem0': {
        ...             'enabled': True,
        ...             'vector_store': 'chroma',
        ...             'llm': 'litellm'
        ...         }
        ...     }
        ... }
        >>> adapter = Mem0Adapter(config)
        >>> result = adapter.add_memory(
        ...     content="User prefers Sonnet 4 for complex tasks",
        ...     user_id="default",
        ...     metadata={'type': 'preference'}
        ... )
        >>> memories = adapter.search_memory("user preferences", limit=3)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Mem0Adapter with configuration.
        
        Args:
            config: Configuration dictionary with memory.mem0 settings
            
        Raises:
            ImportError: If mem0ai package not installed
            ValueError: If configuration is invalid
        """
        self.config = config
        self._validate_config()
        
        try:
            from mem0 import Memory
        except ImportError:
            logger.error("mem0ai package not installed. Run: pip install mem0ai>=1.0.0")
            raise ImportError(
                "mem0ai package required for Mem0Adapter. "
                "Install with: pip install mem0ai>=1.0.0"
            )
        
        # Build Mem0 configuration
        mem_config = self._build_mem0_config()
        
        # Initialize Mem0 Memory instance
        try:
            self.memory = Memory.from_config(mem_config)
            logger.info(f"Initialized Mem0Adapter with vector_store: {mem_config['vector_store']['provider']}")
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            raise
    
    def _validate_config(self):
        """Validate configuration has required fields."""
        if 'memory' not in self.config:
            raise ValueError("Configuration missing 'memory' section")
        
        mem_config = self.config.get('memory', {}).get('mem0', {})
        if not mem_config.get('enabled', False):
            logger.warning("Mem0 is not enabled in configuration")
    
    def _build_mem0_config(self) -> Dict[str, Any]:
        """
        Build Mem0-specific configuration from Polly config.
        
        Returns:
            Configuration dict for Memory.from_config()
        """
        mem0_config = self.config.get('memory', {}).get('mem0', {})
        
        # Get selected providers
        embedding_provider = mem0_config.get('embedding_provider', 'ollama')
        llm_provider = mem0_config.get('llm_provider', 'ollama')
        
        # Get provider configurations
        providers = mem0_config.get('providers', {})
        
        if not providers:
            logger.warning("No providers configured in memory.mem0.providers, using defaults")
            providers = self._get_default_provider_config()
        
        # Validate selected providers exist in config
        if embedding_provider not in providers:
            raise ValueError(f"Embedding provider '{embedding_provider}' not found in config")
        if llm_provider not in providers:
            raise ValueError(f"LLM provider '{llm_provider}' not found in config")
        
        # Build Mem0 config
        mem_config = {
            "version": "v1.1",
            "vector_store": self._build_vector_store_config(mem0_config)
        }
        
        # Add embedder config
        try:
            mem_config["embedder"] = self._build_embedder_config(
                embedding_provider,
                providers[embedding_provider]
            )
            logger.info(f"Using {embedding_provider} for Mem0 embeddings")
        except Exception as e:
            logger.error(f"Failed to build embedder config: {e}")
            raise
        
        # Add LLM config
        try:
            mem_config["llm"] = self._build_llm_config(
                llm_provider,
                providers[llm_provider]
            )
            logger.info(f"Using {llm_provider} for Mem0 LLM")
        except Exception as e:
            logger.error(f"Failed to build LLM config: {e}")
            raise
        
        # Set provider-specific environment variables
        self._set_provider_env_vars(llm_provider, providers[llm_provider])
        
        # Optional: Graph store configuration
        graph_store_config = mem0_config.get('graph_store')
        if graph_store_config:
            mem_config["graph_store"] = graph_store_config
            logger.info("Graph store enabled for entity relationships")
        
        return mem_config
    
    def _build_embedder_config(self, provider: str, config: Dict) -> Dict:
        """Build embedder config based on provider type."""
        if provider == "ollama":
            host = config.get('host', 'http://localhost:11434')
            model = config.get('embedding_model', 'nomic-embed-text')
            return {
                "provider": "openai",
                "config": {
                    "model": model,
                    "openai_base_url": f"{host}/v1",
                    "api_key": "ollama"  # Dummy key; Ollama doesn't validate
                }
            }
        
        elif provider == "qwen":
            api_key_env = config.get('api_key_env', 'DASHSCOPE_API_KEY')
            model = config.get('embedding_model', 'text-embedding-v3')
            return {
                "provider": "openai",
                "config": {
                    "model": model,
                    "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "api_key": os.environ.get(api_key_env)
                }
            }
        
        elif provider == "minimax":
            api_key_env = config.get('api_key_env', 'MINIMAX_API_KEY')
            model = config.get('embedding_model', 'embo-01')
            return {
                "provider": "openai",
                "config": {
                    "model": model,
                    "openai_base_url": "https://api.minimax.chat/v1",
                    "api_key": os.environ.get(api_key_env)
                }
            }
        
        elif provider == "glm":
            api_key_env = config.get('api_key_env', 'ZHIPUAI_API_KEY')
            model = config.get('embedding_model', 'embedding-3')
            return {
                "provider": "openai",
                "config": {
                    "model": model,
                    "openai_base_url": "https://open.bigmodel.cn/api/paas/v4",
                    "api_key": os.environ.get(api_key_env)
                }
            }
        
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
    
    def _build_llm_config(self, provider: str, config: Dict) -> Dict:
        """Build LLM config based on provider type."""
        model = config.get('llm_model')
        temperature = config.get('temperature', 0.0)
        
        provider_prefixes = {
            "ollama": "ollama",
            "qwen": "dashscope",
            "minimax": "minimax",
            "glm": "zhipuai"
        }
        
        prefix = provider_prefixes.get(provider)
        if not prefix:
            raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return {
            "provider": "litellm",
            "config": {
                "model": f"{prefix}/{model}",
                "temperature": temperature
            }
        }
    
    def _set_provider_env_vars(self, provider: str, config: Dict):
        """Set provider-specific environment variables for LiteLLM."""
        if provider == "ollama":
            host = config.get('host', 'http://localhost:11434')
            os.environ.setdefault("OLLAMA_API_BASE", host)
        
        elif provider == "qwen":
            api_key_env = config.get('api_key_env', 'DASHSCOPE_API_KEY')
            if api_key_env in os.environ:
                os.environ.setdefault("DASHSCOPE_API_KEY", os.environ[api_key_env])
        
        elif provider == "minimax":
            api_key_env = config.get('api_key_env', 'MINIMAX_API_KEY')
            group_id_env = config.get('group_id_env', 'MINIMAX_GROUP_ID')
            if api_key_env in os.environ:
                os.environ.setdefault("MINIMAX_API_KEY", os.environ[api_key_env])
            if group_id_env in os.environ:
                os.environ.setdefault("MINIMAX_GROUP_ID", os.environ[group_id_env])
        
        elif provider == "glm":
            api_key_env = config.get('api_key_env', 'ZHIPUAI_API_KEY')
            if api_key_env in os.environ:
                os.environ.setdefault("ZHIPUAI_API_KEY", os.environ[api_key_env])
    
    def _build_vector_store_config(self, mem0_config: Dict) -> Dict:
        """Build vector store config (extracted for clarity)."""
        vector_store_provider = mem0_config.get('vector_store', 'chroma')
        collections = mem0_config.get('collections', {})
        
        return {
            "provider": vector_store_provider,
            "config": {
                "collection_name": collections.get('knowledge', 'polly_mem0_memories'),
                "path": str(Path.home() / ".polly" / "chroma_mem0")
            }
        }
    
    def _get_default_provider_config(self) -> Dict:
        """Fallback to old config structure for backward compatibility."""
        logger.warning("Using legacy config structure (models.local)")
        
        models_config = self.config.get('models', {})
        ollama_config = models_config.get('local', {})
        return {
            "ollama": {
                "host": ollama_config.get('host', 'http://localhost:11434'),
                "embedding_model": ollama_config.get('embedding_model', 'nomic-embed-text'),
                "llm_model": ollama_config.get('chat_models', {}).get('fast', 'llama3.2:3b'),
                "temperature": 0.0
            }
        }
    
    def add_memory(
        self,
        content: str,
        user_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None,
        infer: bool = True
    ) -> Dict[str, Any]:
        """
        Add a memory with optional entity extraction.
        
        Args:
            content: The memory content (text)
            user_id: User/agent identifier for memory namespacing
            metadata: Optional metadata dict (source, type, timestamp, etc.)
            infer: If True (default), Mem0 uses LLM to extract entities/relations.
                   Set to False when storing pre-extracted facts to avoid LLM calls
                   (and to avoid errors with models that don't support function calling).
            
        Returns:
            Dict with memory_id and extracted entities
            
        Example:
            >>> result = adapter.add_memory(
            ...     content="User prefers Claude Sonnet 4 for code reviews",
            ...     user_id="default",
            ...     metadata={
            ...         'source': 'chat',
            ...         'type': 'preference',
            ...         'timestamp': datetime.now().isoformat()
            ...     }
            ... )
            >>> print(result['id'])
        """
        try:
            # Add timestamp if not present
            if metadata is None:
                metadata = {}
            if 'timestamp' not in metadata:
                metadata['timestamp'] = datetime.now().isoformat()
            
            # Call Mem0 add
            # When infer=False, Mem0 skips LLM-based entity extraction and stores
            # the content directly. This is needed for models like ollama/llama3.2:3b
            # that don't support function calling (which Mem0's infer path requires).
            result = self.memory.add(
                messages=content,
                user_id=user_id,
                metadata=metadata,
                infer=infer
            )
            
            logger.debug(f"Added memory for user_id={user_id}: {content[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            raise
    
    def search_memory(
        self,
        query: str,
        user_id: str = "default",
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories with semantic similarity and reranking.
        
        Args:
            query: Search query
            user_id: User/agent identifier to search within
            limit: Maximum number of results
            
        Returns:
            List of memory dicts with relevance scores
            
        Example:
            >>> memories = adapter.search_memory(
            ...     query="What are the user's model preferences?",
            ...     user_id="default",
            ...     limit=3
            ... )
            >>> for mem in memories:
            ...     print(f"{mem['memory']} (score: {mem['score']})")
        """
        try:
            results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            logger.debug(f"Found {len(results)} memories for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def get_relevant_context(
        self,
        query: str,
        user_id: str = "default",
        limit: int = 3
    ) -> str:
        """
        Get formatted memory context for LLM prompts.
        
        This is a convenience method that searches memories and formats them
        as a string suitable for injection into LLM system prompts.
        
        Args:
            query: Context query
            user_id: User/agent identifier
            limit: Maximum number of memories to include
            
        Returns:
            Formatted context string (empty if no memories found)
            
        Example:
            >>> context = adapter.get_relevant_context(
            ...     query="enrichment style",
            ...     user_id="persona:scribe"
            ... )
            >>> system_prompt = f"You are the Scribe...\\n\\n{context}\\n\\nTask: ..."
        """
        try:
            memories = self.search_memory(query, user_id, limit)
            
            if not memories:
                return ""
            
            # Format memories as context
            context_parts = ["## Relevant Context from Memory:"]
            for i, mem in enumerate(memories, 1):
                memory_text = mem.get('memory', '')
                score = mem.get('score', 0.0)
                context_parts.append(f"{i}. {memory_text} (relevance: {score:.2f})")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return ""
    
    def update_memory(
        self,
        memory_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing memory.
        
        Args:
            memory_id: ID of memory to update
            content: New content
            metadata: Updated metadata
            
        Returns:
            Updated memory dict
        """
        try:
            result = self.memory.update(
                memory_id=memory_id,
                data=content,
                metadata=metadata
            )
            
            logger.debug(f"Updated memory {memory_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
    
    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory.
        
        Args:
            memory_id: ID of memory to delete
            
        Returns:
            True if successful
        """
        try:
            self.memory.delete(memory_id=memory_id)
            logger.debug(f"Deleted memory {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    def get_all_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """
        Get all memories for a user/agent.
        
        Args:
            user_id: User/agent identifier
            
        Returns:
            List of all memory dicts
        """
        try:
            memories = self.memory.get_all(user_id=user_id)
            logger.debug(f"Retrieved {len(memories)} memories for user_id={user_id}")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get all memories: {e}")
            return []
    
    def reset(self, user_id: Optional[str] = None):
        """
        Reset memories. If user_id provided, only that user's memories are cleared.
        
        Args:
            user_id: Optional user/agent identifier. If None, clears all memories.
        """
        try:
            if user_id:
                self.memory.reset(user_id=user_id)
                logger.info(f"Reset memories for user_id={user_id}")
            else:
                self.memory.reset()
                logger.info("Reset all memories")
                
        except Exception as e:
            logger.error(f"Failed to reset memories: {e}")
            raise

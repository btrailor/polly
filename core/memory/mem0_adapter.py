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
        
        # Vector store configuration (ChromaDB)
        vector_store_provider = mem0_config.get('vector_store', 'chroma')
        collections = mem0_config.get('collections', {})
        
        mem_config = {
            "version": "v1.1",
            "vector_store": {
                "provider": vector_store_provider,
                "config": {
                    "collection_name": collections.get('knowledge', 'polly_mem0_memories'),
                    "path": str(Path.home() / ".polly" / "chroma_mem0"),
                    "embedding_model_dims": 1536  # Default OpenAI dimension
                }
            }
        }
        
        # Optional graph store (Neo4j) - disabled by default
        graph_store_config = mem0_config.get('graph_store')
        if graph_store_config:
            mem_config["graph_store"] = graph_store_config
            logger.info("Graph store enabled for entity relationships")
        
        # Optional LLM configuration (use LiteLLM if available)
        llm_provider = mem0_config.get('llm', 'litellm')
        if llm_provider == 'litellm':
            # Mem0 can use LiteLLM for entity extraction
            mem_config["llm"] = {
                "provider": "litellm",
                "config": {
                    "model": "gpt-4o-mini",  # Fast model for entity extraction
                    "temperature": 0.0
                }
            }
        
        return mem_config
    
    def add_memory(
        self,
        content: str,
        user_id: str = "default",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a memory with automatic entity extraction.
        
        Args:
            content: The memory content (text)
            user_id: User/agent identifier for memory namespacing
            metadata: Optional metadata dict (source, type, timestamp, etc.)
            
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
            result = self.memory.add(
                messages=content,
                user_id=user_id,
                metadata=metadata
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

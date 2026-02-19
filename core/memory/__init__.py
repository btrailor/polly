"""
Polly Memory Layer

Unified memory interface supporting multiple backends:
- Local: File-based storage (default)
- Mem0: Adaptive memory with entity extraction and graph storage

The memory layer operates as an additive enhancement to existing systems
(Knowledge Writer, RAG, Personas) without replacing them.
"""

from typing import Optional, Dict, Any

__all__ = [
    'get_memory_adapter',
    'Mem0Adapter',
    'TieredMemoryStore',
    'MemoryTier',
    'MemoryEntry',
    'MemoryMetadata',
    'MemoryRetriever',
    'SessionExtractor',
    'ExtractedFact',
    'ExtractionResult',
]


def get_memory_adapter(config: Dict[str, Any]) -> Optional[Any]:
    """
    Factory function to get appropriate memory adapter based on config.
    
    Args:
        config: Configuration dictionary with memory.provider setting
        
    Returns:
        Memory adapter instance or None if local provider
        
    Example:
        >>> config = {'memory': {'provider': 'mem0'}}
        >>> adapter = get_memory_adapter(config)
    """
    provider = config.get('memory', {}).get('provider', 'local')
    
    if provider == 'mem0':
        from core.memory.mem0_adapter import Mem0Adapter
        return Mem0Adapter(config)
    elif provider == 'local':
        return None  # Local storage, no adapter needed
    else:
        raise ValueError(f"Unknown memory provider: {provider}")


# Convenience imports
try:
    from core.memory.mem0_adapter import Mem0Adapter
except ImportError:
    # Mem0 not installed
    Mem0Adapter = None

try:
    from core.memory.tiers import TieredMemoryStore, MemoryTier, MemoryEntry, MemoryMetadata
except ImportError:
    # Dependencies not available
    TieredMemoryStore = None
    MemoryTier = None
    MemoryEntry = None
    MemoryMetadata = None

try:
    from core.memory.retriever import MemoryRetriever
except ImportError:
    MemoryRetriever = None

try:
    from core.memory.extractor import SessionExtractor, ExtractedFact, ExtractionResult
except ImportError:
    SessionExtractor = None
    ExtractedFact = None
    ExtractionResult = None

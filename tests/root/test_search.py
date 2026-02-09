#!/usr/bin/env python3
"""Test script to verify RAG search includes integration collections"""

import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG
from core.config import PollyConfig

def main():
    print("=" * 60)
    print("Testing RAG Search with Integration Collections")
    print("=" * 60)
    
    # Initialize RAG
    config = PollyConfig()
    rag = UnifiedRAG(
        db_path=config.vector_db_path,
        embedding_model=config.embedding_model,
        ollama_host=config.ollama_host
    )
    
    print(f"\n✓ Initialized RAG")
    print(f"  Available collections: {list(rag.collections.keys())}")
    
    # Test search
    print(f"\n🔍 Searching for 'repositories github'...")
    results = rag.search('repositories github', n_results=3)
    
    print(f"\n✓ Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. Source: {result.chunk.source_type}")
        print(f"   Score: {result.score:.3f}")
        print(f"   Filepath: {result.chunk.filepath}")
        print(f"   Content preview: {result.chunk.content[:100]}...")
        print()
    
    # Check if any results are from integration_github
    integration_results = [r for r in results if r.chunk.source_type == 'integration_github']
    
    if integration_results:
        print(f"✅ SUCCESS: Found {len(integration_results)} results from integration_github!")
    else:
        print(f"❌ FAILURE: No results from integration_github collection")
        print(f"   All results were from: {set(r.chunk.source_type for r in results)}")

if __name__ == '__main__':
    main()

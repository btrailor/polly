#!/usr/bin/env python3
"""
Test script to verify GitHub documents are searchable in RAG
"""
import sys
from pathlib import Path

# Add polly to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG

def test_github_search():
    """Test if GitHub repos are found in search"""
    print("Initializing RAG...")
    rag = UnifiedRAG(
        db_path=Path.home() / ".polly" / "chroma_db",
        ollama_host="http://localhost:11434",
        embedding_model="nomic-embed-text"
    )
    
    print(f"Collections available: {list(rag.collections.keys())}\n")
    
    # Test search
    query = "What GitHub repositories do you see?"
    print(f"Searching for: '{query}'")
    print("=" * 60)
    
    results = rag.search(query=query, n_results=30)
    
    print(f"\nFound {len(results)} total results\n")
    
    # Show GitHub results
    github_results = [r for r in results if r.chunk.metadata.get('source') == 'github']
    print(f"GitHub results: {len(github_results)}")
    print("-" * 60)
    
    for i, result in enumerate(github_results[:10], 1):
        repo_name = result.chunk.metadata.get('name', 'Unknown')
        score = result.score
        source_type = result.chunk.source_type
        print(f"{i}. {repo_name}")
        print(f"   Score: {score:.4f}")
        print(f"   Source Type: {source_type}")
        print(f"   Content preview: {result.chunk.content[:100]}...")
        print()
    
    # Show top 5 overall results
    print("\nTop 5 results overall:")
    print("-" * 60)
    for i, result in enumerate(results[:5], 1):
        source = result.chunk.metadata.get('source', result.chunk.source_type)
        name = result.chunk.metadata.get('name', result.chunk.filepath)
        score = result.score
        print(f"{i}. [{source}] {name} (score: {score:.4f})")

if __name__ == "__main__":
    test_github_search()

#!/usr/bin/env python3
"""
Test if Practices & Embedded Exercises document is being retrieved correctly
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG
from core.config import Config

def main():
    config = Config()
    rag = UnifiedRAG(config)
    
    query = "Concerning my Practices and Exercises framework. What is something I might do today to keep in practice?"
    
    print(f"Query: {query}\n")
    print("=" * 80)
    
    # Get results from RAG
    results = rag.search(
        query,
        limit=10,
        include_metadata=True
    )
    
    print(f"\nRetrieved {len(results)} chunks:\n")
    
    practices_count = 0
    for i, result in enumerate(results, 1):
        source = result.get('metadata', {}).get('source', 'unknown')
        text = result.get('text', '')[:100]
        score = result.get('score', 0)
        
        is_practices = 'Practices & Embedded Exercises' in source
        if is_practices:
            practices_count += 1
            
        print(f"{i}. {'✅' if is_practices else '  '} Score: {score:.4f}")
        print(f"   Source: {source}")
        print(f"   Text: {text}...")
        print()
    
    print("=" * 80)
    print(f"\n✅ Practices document chunks: {practices_count}/{len(results)}")
    
    if practices_count == 0:
        print("❌ PROBLEM: No chunks from Practices document retrieved!")
    elif practices_count < 5:
        print("⚠️  WARNING: Very few chunks from Practices document")
    else:
        print("✅ SUCCESS: Multiple Practices chunks retrieved")

if __name__ == "__main__":
    main()

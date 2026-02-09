#!/usr/bin/env python3
"""Debug why Practices note isn't being retrieved for the specific query"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG
from core.config import PollyConfig

def main():
    config = PollyConfig()
    rag = UnifiedRAG(
        db_path=config.vector_db_path,
        embedding_model=config.embedding_model,
        ollama_host=config.ollama_host
    )
    
    # Original failing query
    query1 = 'Concerning my "Practices and Exercises" framework. What is something I might do today to keep in practice?'
    
    # Simpler query
    query2 = "Practices and Exercises"
    
    # Domain-specific query
    query3 = "daily exercises to keep in practice"
    
    # Direct content query
    query4 = "Daily Sonic Postcards exercise"
    
    queries = [
        ("Original query", query1),
        ("Simple title match", query2),
        ("Domain-specific", query3),
        ("Direct exercise name", query4)
    ]
    
    print("=" * 80)
    print("Testing different query formulations")
    print("=" * 80)
    
    for label, query in queries:
        print(f"\n{label}: {query[:80]}...")
        print("-" * 80)
        
        results = rag.search(query, n_results=5)
        
        practices_found = False
        practices_rank = None
        
        for i, result in enumerate(results, 1):
            is_practices = 'Practices & Embedded' in result.chunk.filepath
            marker = "🎯" if is_practices else "  "
            
            if is_practices:
                practices_found = True
                practices_rank = i
            
            print(f"{marker} {i}. [{result.score:.3f}] {result.chunk.filepath}")
            if is_practices:
                print(f"     Content: {result.chunk.content[:100]}...")
        
        if practices_found:
            print(f"\n✅ Practices note found at rank {practices_rank}!")
        else:
            print(f"\n❌ Practices note NOT in top 5")
    
    # Now let's check the actual similarity scores for practices chunks
    print("\n" + "=" * 80)
    print("Direct similarity check for Practices chunks")
    print("=" * 80)
    
    collection = rag.collections['obsidian']
    
    # Get a few practices chunks and their embeddings
    all_docs = collection.get(
        include=['documents', 'metadatas', 'embeddings']
    )
    
    practices_indices = []
    for i, meta in enumerate(all_docs['metadatas']):
        if 'Practices & Embedded' in meta.get('filepath', ''):
            practices_indices.append(i)
            if len(practices_indices) >= 5:
                break
    
    # Get embedding for query1
    query_embedding = rag.embed_text(query1)
    
    # Calculate cosine similarity manually
    import numpy as np
    
    print(f"\nQuery: {query1}")
    print("\nTop Practices chunks and their similarity scores:")
    
    for idx in practices_indices:
        doc = all_docs['documents'][idx]
        meta = all_docs['metadatas'][idx]
        embedding = all_docs['embeddings'][idx]
        
        # Calculate cosine similarity
        similarity = np.dot(query_embedding, embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
        )
        
        print(f"\n  Score: {similarity:.3f}")
        print(f"  Header: {meta.get('header', 'N/A')}")
        print(f"  Content: {doc[:150]}...")

if __name__ == '__main__':
    main()

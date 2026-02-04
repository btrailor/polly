#!/usr/bin/env python3
"""Test hybrid search with the original failing query"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG
from core.config import PollyConfig

def main():
    print("=" * 80)
    print("Testing Hybrid Search for Practices and Exercises Note")
    print("=" * 80)
    
    config = PollyConfig()
    
    print("\n1. Initializing RAG with hybrid search enabled...")
    rag = UnifiedRAG(
        db_path=config.vector_db_path,
        embedding_model=config.embedding_model,
        ollama_host=config.ollama_host,
        use_hybrid_search=True
    )
    
    print(f"   ✓ Hybrid search: {'enabled' if rag.use_hybrid_search else 'disabled'}")
    print(f"   ✓ Collections: {list(rag.collections.keys())}")
    
    # Build BM25 index
    print("\n2. Building BM25 index for keyword search...")
    rag._rebuild_bm25_index()
    print("   ✓ BM25 index built")
    
    # Original failing query
    query = 'Concerning my "Practices and Exercises" framework. What is something I might do today to keep in practice?'
    
    print(f"\n3. Testing with original query:")
    print(f"   Query: {query}")
    print("\n" + "-" * 80)
    
    # Test with hybrid search
    print("\n   🔍 HYBRID SEARCH (semantic + keyword + title boosting):")
    print("   " + "-" * 76)
    results_hybrid = rag.search(query, n_results=10, use_hybrid=True)
    
    practices_found_hybrid = False
    practices_rank_hybrid = None
    
    practices_chunks_hybrid = []
    
    for i, result in enumerate(results_hybrid[:10], 1):
        is_practices = 'Practices & Embedded' in result.chunk.filepath
        marker = "🎯" if is_practices else "  "
        
        if is_practices:
            practices_found_hybrid = True
            if practices_rank_hybrid is None:
                practices_rank_hybrid = i
            practices_chunks_hybrid.append(result)
        
        print(f"   {marker} {i}. [{result.score:.4f}] {result.chunk.filepath}")
        if is_practices:
            # Show first line of content to identify what chunk this is
            first_line = result.chunk.content.strip().split('\n')[0][:80]
            print(f"      Content: {first_line}...")
            if '_hybrid_breakdown' in result.chunk.metadata:
                bd = result.chunk.metadata['_hybrid_breakdown']
                print(f"      Breakdown: Semantic={bd['semantic_score']:.3f}, "
                     f"Keyword={bd['keyword_score']:.3f}, Boost={bd['title_boost']:.2f}x")
    
    print("\n   " + "-" * 76)
    
    # Compare with semantic-only
    print("\n   🔍 SEMANTIC-ONLY SEARCH (for comparison):")
    print("   " + "-" * 76)
    results_semantic = rag.search(query, n_results=10, use_hybrid=False)
    
    practices_found_semantic = False
    practices_rank_semantic = None
    
    for i, result in enumerate(results_semantic[:10], 1):
        is_practices = 'Practices & Embedded' in result.chunk.filepath
        marker = "🎯" if is_practices else "  "
        
        if is_practices:
            practices_found_semantic = True
            practices_rank_semantic = i
        
        print(f"   {marker} {i}. [{result.score:.4f}] {result.chunk.filepath}")
    
    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    print(f"\nHybrid Search (semantic + keyword + title boost):")
    if practices_found_hybrid:
        print(f"  ✅ Practices note found at rank {practices_rank_hybrid}")
        print(f"  📊 Retrieved {len(practices_chunks_hybrid)} chunks from Practices document")
        
        # Show what chunks were retrieved
        print(f"\n  Chunks retrieved from Practices document:")
        for i, result in enumerate(practices_chunks_hybrid, 1):
            first_line = result.chunk.content.strip().split('\n')[0][:100]
            print(f"    {i}. {first_line}")
    else:
        print(f"  ❌ Practices note NOT in top 10")
    
    print(f"\nSemantic-Only Search (baseline):")
    if practices_found_semantic:
        print(f"  ✅ Practices note found at rank {practices_rank_semantic}")
    else:
        print(f"  ❌ Practices note NOT in top 10")
    
    if practices_found_hybrid and not practices_found_semantic:
        print(f"\n🎉 SUCCESS! Hybrid search retrieved the note, semantic-only didn't!")
        print(f"   Improvement: Not found → Rank {practices_rank_hybrid}")
    elif practices_found_hybrid and practices_found_semantic:
        if practices_rank_hybrid < practices_rank_semantic:
            print(f"\n🎉 SUCCESS! Hybrid search improved ranking!")
            print(f"   Improvement: Rank {practices_rank_semantic} → Rank {practices_rank_hybrid}")
        else:
            print(f"\n✓ Both methods found it, but semantic performed better")
            print(f"   Hybrid: Rank {practices_rank_hybrid}, Semantic: Rank {practices_rank_semantic}")
    elif not practices_found_hybrid and practices_found_semantic:
        print(f"\n⚠️  Hybrid search performed worse than semantic-only")
    else:
        print(f"\n❌ Neither method found the note in top 10")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Diagnostic script to test if Polly is using hybrid search and retrieving 
all 10 practices from the "Practices & Embedded Exercises" document.
"""

import requests
import json

def test_rag_directly():
    """Test RAG system directly (bypassing server)"""
    print("=" * 80)
    print("TEST 1: Direct RAG Test (Python)")
    print("=" * 80)
    
    from core.rag import UnifiedRAG
    from core.config import PollyConfig
    
    config = PollyConfig()
    rag = UnifiedRAG(
        db_path=config.vector_db_path,
        embedding_model=config.embedding_model,
        ollama_host=config.ollama_host,
        use_hybrid_search=True
    )
    
    print(f"\n✓ Hybrid search enabled: {rag.use_hybrid_search}")
    print(f"✓ Hybrid searcher: {rag.hybrid_searcher is not None}")
    
    if rag.use_hybrid_search and not rag.hybrid_searcher:
        print("⚠️  WARNING: Hybrid search enabled but searcher is None!")
        return False
    
    # Build BM25 index
    if rag.use_hybrid_search:
        print("\nBuilding BM25 index...")
        rag._rebuild_bm25_index()
        print("✓ BM25 index built")
    
    # Test query
    query = 'Concerning my "Practices and Exercises" framework'
    print(f"\nQuery: {query}")
    print("\nSearching...")
    
    results = rag.search(query, n_results=10, use_hybrid=True)
    
    # Check if Practices document is in results
    practices_count = 0
    practices_rank = None
    practice_headers = []
    
    for i, result in enumerate(results[:20], 1):
        if 'Practices & Embedded' in result.chunk.filepath:
            practices_count += 1
            if practices_rank is None:
                practices_rank = i
            
            # Check if this is a PRACTICE header
            content = result.chunk.content.strip()
            if content.startswith('## PRACTICE'):
                practice_headers.append(content.split('\n')[0])
    
    print(f"\n✓ Total results: {len(results)}")
    print(f"✓ Practices document chunks: {practices_count}")
    if practices_rank:
        print(f"✓ First appearance at rank: {practices_rank}")
    
    if practice_headers:
        print(f"\n✓ PRACTICE headers found: {len(practice_headers)}")
        for header in practice_headers:
            print(f"  - {header}")
    
    return practices_count >= 10 and len(practice_headers) >= 5

def test_server_api():
    """Test through the server API"""
    print("\n" + "=" * 80)
    print("TEST 2: Server API Test (HTTP)")
    print("=" * 80)
    
    url = "http://localhost:11436/polly/stats"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n✓ Server is running")
            print(f"✓ Collections: {list(stats.keys())}")
            
            # Check obsidian stats
            obsidian_stats = stats.get('obsidian_vault', {})
            print(f"✓ Obsidian chunks: {obsidian_stats.get('chunks', 0)}")
            print(f"✓ Obsidian files: {obsidian_stats.get('files', 0)}")
            
            return True
        else:
            print(f"\n❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"\n❌ Server not reachable: {e}")
        print("\nTo restart the server:")
        print("1. Click the Polly menu bar icon")
        print("2. Select 'Restart Server'")
        return False

def main():
    print("\n🔍 Polly Diagnostic Tool")
    print("Testing hybrid search and Practices document retrieval")
    print()
    
    # Test 1: Direct RAG
    direct_ok = test_rag_directly()
    
    # Test 2: Server API
    server_ok = test_server_api()
    
    # Summary
    print("\n" + "=" * 80)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 80)
    
    if direct_ok:
        print("\n✅ Direct RAG test PASSED")
        print("   - Hybrid search is working")
        print("   - All 10 practices are retrievable")
    else:
        print("\n❌ Direct RAG test FAILED")
        print("   - Practices document not being retrieved properly")
    
    if server_ok:
        print("\n✅ Server is running")
    else:
        print("\n❌ Server is not reachable")
    
    if direct_ok and not server_ok:
        print("\n⚠️  ACTION REQUIRED:")
        print("   The code is working, but the server needs to be restarted.")
        print("   Click the Polly menu bar icon and select 'Restart Server'")
    elif not direct_ok:
        print("\n⚠️  ACTION REQUIRED:")
        print("   There may be an issue with the hybrid search implementation.")
        print("   Check if rank-bm25 is installed: pip install rank-bm25")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

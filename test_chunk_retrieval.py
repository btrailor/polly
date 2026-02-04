#!/usr/bin/env python3
"""Test to see exactly how many chunks are being retrieved from Practices document"""

import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG
from core.config import PollyConfig

# Enable detailed logging
logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 80)
    print("Testing Multi-Chunk Retrieval from Practices Document")
    print("=" * 80)
    
    config = PollyConfig()
    
    print("\n1. Initializing RAG with hybrid search enabled...")
    rag = UnifiedRAG(
        db_path=config.vector_db_path,
        embedding_model=config.embedding_model,
        ollama_host=config.ollama_host,
        use_hybrid_search=True
    )
    
    # Build BM25 index
    print("\n2. Building BM25 index...")
    rag._rebuild_bm25_index()
    print("   ✓ BM25 index built")
    
    # Query that should trigger multi-chunk retrieval
    query = 'Concerning my "Practices and Exercises" framework. What is something I might do today to keep in practice?'
    
    print(f"\n3. Executing search with query:")
    print(f"   '{query}'")
    print("\n" + "-" * 80)
    
    # Search with larger n_results to see all chunks
    results = rag.search(query, n_results=20, use_hybrid=True)
    
    print(f"\n4. Total results returned: {len(results)}")
    print("\n" + "-" * 80)
    
    # Group by document
    docs = {}
    for result in results:
        filepath = result.chunk.filepath
        if filepath not in docs:
            docs[filepath] = []
        docs[filepath].append(result)
    
    print(f"\n5. Results grouped by document ({len(docs)} unique documents):")
    print("-" * 80)
    
    for filepath, chunks in docs.items():
        is_practices = 'Practices & Embedded' in filepath
        marker = "🎯" if is_practices else "  "
        print(f"\n{marker} {filepath}")
        print(f"   {len(chunks)} chunks retrieved:")
        
        if is_practices:
            # Show all chunks from Practices document
            for i, result in enumerate(chunks, 1):
                first_line = result.chunk.content.strip().split('\n')[0][:100]
                print(f"     {i}. [{result.score:.4f}] {first_line}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    
    practices_file = None
    for filepath in docs:
        if 'Practices & Embedded' in filepath:
            practices_file = filepath
            break
    
    if practices_file:
        practice_chunks = docs[practices_file]
        print(f"\n✅ Practices document found with {len(practice_chunks)} chunks")
        
        # Count PRACTICE headers
        practice_headers = []
        exercise_headers = []
        other_chunks = []
        
        for chunk in practice_chunks:
            content = chunk.chunk.content.strip()
            if content.startswith('## PRACTICE') or content.startswith('PRACTICE '):
                practice_headers.append(content.split('\n')[0])
            elif content.startswith('### Exercise'):
                exercise_headers.append(content.split('\n')[0])
            else:
                other_chunks.append(content.split('\n')[0][:80])
        
        print(f"\n  📊 Chunk breakdown:")
        print(f"     - PRACTICE headers: {len(practice_headers)}")
        for header in practice_headers:
            print(f"       • {header}")
        
        print(f"\n     - Exercise headers: {len(exercise_headers)}")
        for header in exercise_headers[:5]:  # Show first 5
            print(f"       • {header}")
        if len(exercise_headers) > 5:
            print(f"       ... and {len(exercise_headers) - 5} more")
        
        print(f"\n     - Other chunks: {len(other_chunks)}")
        for chunk in other_chunks[:3]:
            print(f"       • {chunk}...")
        
        # Check if all 10 practices are present
        practice_numbers = set()
        for header in practice_headers:
            # Extract practice number
            if 'PRACTICE' in header:
                parts = header.split('PRACTICE')
                if len(parts) > 1:
                    num_part = parts[1].strip().split(':')[0].strip()
                    try:
                        practice_numbers.add(int(num_part))
                    except:
                        pass
        
        print(f"\n  🎯 Practices represented: {sorted(practice_numbers)}")
        missing = set(range(1, 11)) - practice_numbers
        if missing:
            print(f"  ⚠️  Missing practices: {sorted(missing)}")
        else:
            print(f"  ✅ All 10 practices retrieved!")
    else:
        print("\n❌ Practices document not found in results")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

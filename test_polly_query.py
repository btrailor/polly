#!/usr/bin/env python3
"""
Direct test of what Polly's query method retrieves
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import get_config
from core.polly import Polly

async def test_polly_query():
    """Test what Polly actually retrieves"""
    config = get_config()
    polly = Polly(config)
    
    # Directly test the RAG search with the query
    query = "What GitHub repositories do you see?"
    print(f"Testing query: '{query}'")
    print("=" * 60)
    
    # Call the RAG search directly
    results = polly.rag.search(query=query, n_results=30)
    
    print(f"\nTotal results: {len(results)}")
    print("\nBreakdown by source:")
    
    # Count by source
    from collections import Counter
    sources = Counter()
    source_types = Counter()
    
    for r in results:
        source = r.chunk.metadata.get('source', r.chunk.source_type)
        sources[source] += 1
        source_types[r.chunk.source_type] += 1
    
    for source, count in sources.most_common():
        print(f"  {source}: {count}")
    
    print("\nBy source_type:")
    for st, count in source_types.most_common():
        print(f"  {st}: {count}")
    
    # Show GitHub results specifically
    github_results = [r for r in results if (
        r.chunk.source_type.startswith('integration_') or 
        r.chunk.metadata.get('source') == 'github'
    )]
    
    print(f"\nGitHub results found: {len(github_results)}")
    if github_results:
        print("\nGitHub repos:")
        for r in github_results[:10]:
            name = r.chunk.metadata.get('name', 'Unknown')
            score = r.score
            print(f"  - {name} (score: {score:.4f})")

if __name__ == "__main__":
    asyncio.run(test_polly_query())

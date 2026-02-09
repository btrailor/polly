#!/usr/bin/env python3
"""
Debug script to see what RAG retrieves for the Practices query
"""
import sys
sys.path.insert(0, '/Users/brettgershon/polly')

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

import asyncio
from pathlib import Path

# Import Polly
from core.polly import Polly

async def main():
    # Initialize Polly
    polly = Polly()
    
    query = "Concerning my 'Practices and Exercises' framework. What is something I might do today to keep in practice?"
    
    print("=" * 80)
    print(f"Query: {query}")
    print("=" * 80)
    print()
    
    # Get RAG results directly
    rag_results = polly.rag.search(
        query,
        limit=20,
        include_metadata=True
    )
    
    print(f"RAG retrieved {len(rag_results)} chunks:\n")
    
    practices_count = 0
    for i, result in enumerate(rag_results[:15], 1):
        source = result.get('metadata', {}).get('source', 'unknown')
        text = result.get('text', '')[:150]
        score = result.get('score', 0)
        
        is_practices = 'Practices' in source and 'Exercises' in source
        if is_practices:
            practices_count += 1
        
        marker = '✅' if is_practices else '  '
        print(f"{i}. {marker} Score: {score:.4f}")
        print(f"   Source: {source}")
        print(f"   Text: {text}...")
        print()
    
    print("=" * 80)
    print(f"Practices document chunks in top 15: {practices_count}")
    
    if practices_count == 0:
        print("\n❌ PROBLEM: No Practices chunks retrieved!")
        print("This means either:")
        print("  1. Server not restarted (no hybrid search)")
        print("  2. Document not in ChromaDB")
    else:
        print(f"\n✅ Found {practices_count} Practices chunks")

if __name__ == "__main__":
    asyncio.run(main())

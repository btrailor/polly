#!/usr/bin/env python3
"""Test what collection.get() returns when we query for Practices document"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.config import PollyConfig
import chromadb

def main():
    print("=" * 80)
    print("Testing collection.get() behavior for Practices document")
    print("=" * 80)
    
    config = PollyConfig()
    client = chromadb.PersistentClient(path=str(config.vector_db_path))
    
    # Get obsidian_vault collection
    collection = client.get_collection("obsidian_vault")
    
    print("\n1. Querying with limit=100...")
    results = collection.get(
        where={"filepath": "05-Grids/Practices & Embedded Exercises.md"},
        include=['documents', 'metadatas'],
        limit=100
    )
    
    print(f"   Got {len(results['documents'])} chunks")
    
    print("\n2. First 20 chunks returned by collection.get():")
    print("-" * 80)
    
    for i, doc in enumerate(results['documents'][:20], 1):
        first_line = doc.strip().split('\n')[0][:100]
        chunk_type = ""
        if first_line.startswith('## PRACTICE'):
            chunk_type = " [PRACTICE HEADER]"
        elif first_line.startswith('### Exercise'):
            chunk_type = " [EXERCISE]"
        
        print(f"  {i:2d}. {first_line}{chunk_type}")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

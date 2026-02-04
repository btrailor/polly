#!/usr/bin/env python3
"""Debug script to see what chunks exist in ChromaDB for Practices document"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.config import PollyConfig
import chromadb

def main():
    print("=" * 80)
    print("Inspecting Practices Document Chunks in ChromaDB")
    print("=" * 80)
    
    config = PollyConfig()
    client = chromadb.PersistentClient(path=str(config.vector_db_path))
    
    # List all collections
    collections = client.list_collections()
    print(f"\nAvailable collections: {[c.name for c in collections]}")
    
    # Find the obsidian collection (might have different name)
    collection = None
    for coll in collections:
        if 'obsidian' in coll.name.lower():
            collection = client.get_collection(coll.name)
            print(f"Using collection: {coll.name}")
            break
    
    if not collection:
        print("No obsidian collection found!")
        return
    
    print("\n1. Getting sample of chunks to find Practices filepath...")
    
    # First get some chunks to see the exact filepath format
    sample = collection.get(
        include=['metadatas'],
        limit=500  # Larger sample to find the file
    )
    
    practices_filepath = None
    for meta in sample['metadatas']:
        if meta and 'Practices' in meta.get('filepath', ''):
            practices_filepath = meta['filepath']
            print(f"   Found filepath: {practices_filepath}")
            break
    
    if not practices_filepath:
        print("   Could not find Practices document in sample!")
        return
    
    print(f"\n2. Querying for all chunks from: {practices_filepath}")
    
    # Get all chunks from this file with exact filepath match
    results = collection.get(
        where={"filepath": practices_filepath},
        include=['documents', 'metadatas']
    )
    
    print(f"\n3. Found {len(results['documents'])} chunks")
    
    if len(results['documents']) == 0:
        print("   No chunks found!")
        return
    
    
    print(f"\n4. Analyzing chunk content...")
    print("-" * 80)
    
    # Categorize chunks
    practice_headers = []
    exercise_headers = []
    other_chunks = []
    
    for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
        first_line = doc.strip().split('\n')[0]
        
        if first_line.startswith('## PRACTICE') or first_line.startswith('PRACTICE '):
            practice_headers.append((i, first_line))
        elif first_line.startswith('### Exercise'):
            exercise_headers.append((i, first_line))
        else:
            other_chunks.append((i, first_line[:80]))
    
    print(f"\n📊 Chunk Breakdown (Total: {len(results['documents'])}):")
    print(f"\n  PRACTICE Headers ({len(practice_headers)}):")
    for idx, header in practice_headers:
        print(f"    {idx:3d}. {header}")
    
    print(f"\n  Exercise Headers ({len(exercise_headers)}):")
    for idx, header in exercise_headers[:10]:
        print(f"    {idx:3d}. {header}")
    if len(exercise_headers) > 10:
        print(f"    ... and {len(exercise_headers) - 10} more")
    
    print(f"\n  Other Chunks ({len(other_chunks)}):")
    for idx, chunk in other_chunks[:5]:
        print(f"    {idx:3d}. {chunk}...")
    if len(other_chunks) > 5:
        print(f"    ... and {len(other_chunks) - 5} more")
    
    # Check which practices are present
    practice_numbers = set()
    for idx, header in practice_headers:
        if 'PRACTICE' in header:
            parts = header.split('PRACTICE')
            if len(parts) > 1:
                num_part = parts[1].strip().split(':')[0].strip()
                try:
                    practice_numbers.add(int(num_part))
                except:
                    pass
    
    print(f"\n🎯 Practice Numbers Found: {sorted(practice_numbers)}")
    missing = set(range(1, 11)) - practice_numbers
    if missing:
        print(f"⚠️  Missing Practice Numbers: {sorted(missing)}")
    else:
        print(f"✅ All 10 practices are indexed in ChromaDB!")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

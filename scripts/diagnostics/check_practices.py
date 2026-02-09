#!/usr/bin/env python3
"""Check if Practices document is in the vector database"""

from core.config import PollyConfig
import chromadb

config = PollyConfig()
client = chromadb.PersistentClient(path=str(config.vector_db_path))

# Check obsidian_vault collection
collection = client.get_collection("obsidian_vault")

print(f"Collection has {collection.count()} total chunks")

# Get a sample to find filenames
sample = collection.get(
    include=['metadatas'],
    limit=200
)

filepaths = set()
for meta in sample['metadatas']:
    if meta and 'filepath' in meta:
        filepaths.add(meta['filepath'])

print(f"\nFound {len(filepaths)} unique files in sample")

# Look for Practices document
practices_files = [f for f in filepaths if 'Practices' in f and 'Embedded' in f]

if practices_files:
    print(f"\n✅ Found Practices document:")
    for f in practices_files:
        print(f"   {f}")
        
        # Get chunk count for this file
        results = collection.get(
            where={"filepath": f},
            include=['documents']
        )
        print(f"   Chunks: {len(results['documents'])}")
else:
    print(f"\n❌ Practices & Embedded Exercises document NOT found in database!")
    print(f"\nFiles with 'Practices' in name:")
    practices_partial = [f for f in filepaths if 'Practices' in f or 'practices' in f]
    for f in practices_partial:
        print(f"   {f}")
    
    if not practices_partial:
        print("   (none found)")
    
    print(f"\nSample of indexed files:")
    for f in list(filepaths)[:10]:
        print(f"   {f}")

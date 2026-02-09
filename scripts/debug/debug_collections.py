#!/usr/bin/env python3
"""Debug script to check ChromaDB collections"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.config import Settings

def main():
    print("=" * 60)
    print("Checking ChromaDB Collections")
    print("=" * 60)
    
    db_path = Path.home() / '.polly' / 'chromadb'
    print(f"\nDB Path: {db_path}")
    print(f"Exists: {db_path.exists()}\n")
    
    client = chromadb.PersistentClient(
        path=str(db_path),
        settings=Settings(anonymized_telemetry=False)
    )
    
    print("All collections in ChromaDB:")
    all_collections = client.list_collections()
    
    for coll in all_collections:
        count = coll.count()
        print(f"  - {coll.name:30s} ({count} items)")
        
        if coll.name.startswith('integration_'):
            print(f"    ✓ This is an integration collection!")
    
    print(f"\nTotal collections: {len(all_collections)}")
    
    # Try to get integration_github directly
    print("\n" + "=" * 60)
    print("Trying to access integration_github directly...")
    try:
        github_coll = client.get_collection('integration_github')
        print(f"✓ Successfully got integration_github collection")
        print(f"  Count: {github_coll.count()}")
        
        # Get a sample
        result = github_coll.get(limit=1, include=['metadatas', 'documents'])
        if result and result['documents']:
            print(f"  Sample document: {result['documents'][0][:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()

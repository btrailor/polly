#!/usr/bin/env python3
"""Check if Practices note is indexed in ChromaDB"""

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
    
    print("Checking for Practices & Embedded Exercises note...")
    print("=" * 80)
    
    collection = rag.collections['obsidian']
    
    # Get all documents and check if any match
    # We'll check in batches since get() might have limits
    all_docs = collection.get()
    
    practices_chunks = []
    for i, (doc, meta) in enumerate(zip(all_docs['documents'], all_docs['metadatas'])):
        filepath = meta.get('filepath', '')
        if 'Practices' in filepath and 'Embedded' in filepath:
            practices_chunks.append({
                'filepath': filepath,
                'content': doc[:200],
                'metadata': meta
            })
    
    if practices_chunks:
        print(f"✓ Found {len(practices_chunks)} chunks from Practices & Embedded Exercises\n")
        for i, chunk in enumerate(practices_chunks[:5], 1):
            print(f"{i}. Filepath: {chunk['filepath']}")
            print(f"   Content: {chunk['content']}...")
            print(f"   Metadata: {chunk['metadata']}")
            print()
    else:
        print("✗ Practices & Embedded Exercises note is NOT indexed!")
        print("\nSearching for any files with 'Practices' in name...")
        
        practices_files = set()
        for meta in all_docs['metadatas']:
            filepath = meta.get('filepath', '')
            if 'practice' in filepath.lower():
                practices_files.add(filepath)
        
        if practices_files:
            print(f"\nFound {len(practices_files)} files with 'practice' in name:")
            for f in sorted(practices_files):
                print(f"  - {f}")
        else:
            print("\nNo files with 'practice' in name found at all!")
    
    # Check vault path
    print("\n" + "=" * 80)
    print("Vault configuration:")
    print(f"  Obsidian vault path: {config.obsidian_vault_path}")
    print(f"  Vector DB path: {config.vector_db_path}")
    
    # Check if the file exists
    practices_file = Path("/Users/brettgershon/Library/Mobile Documents/iCloud~md~obsidian/Documents/Organizer/05-Grids/Practices & Embedded Exercises.md")
    print(f"\n  File exists: {practices_file.exists()}")
    if practices_file.exists():
        print(f"  File size: {practices_file.stat().st_size} bytes")
        print(f"  Last modified: {practices_file.stat().st_mtime}")

if __name__ == '__main__':
    main()

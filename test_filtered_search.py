#!/usr/bin/env python3
"""
Test if filtered GitHub search works
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from chromadb.config import Settings

# Initialize ChromaDB
db_path = Path.home() / ".polly" / "chroma_db"
client = chromadb.PersistentClient(path=str(db_path), settings=Settings(anonymized_telemetry=False))

# Get documents collection
docs_collection = client.get_collection("documents")

print(f"Total documents in collection: {docs_collection.count()}")

# Try filtered query
try:
    results = docs_collection.query(
        query_texts=["github repositories"],
        n_results=20,
        where={"source": "github"}
    )
    
    print(f"\nFiltered search (source=github): {len(results['documents'][0])} results")
    for i, (doc, meta) in enumerate(zip(results['documents'][0][:5], results['metadatas'][0][:5]), 1):
        print(f"{i}. {meta.get('name', 'Unknown')}")
        print(f"   {doc[:100]}...")
        
except Exception as e:
    print(f"Error with filtered search: {e}")
    import traceback
    traceback.print_exc()

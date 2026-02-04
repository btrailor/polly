#!/usr/bin/env python3
"""Manually test indexing the Practices document"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.rag import UnifiedRAG
from core.config import PollyConfig

config = PollyConfig()

print("Initializing RAG...")
rag = UnifiedRAG(
    db_path=config.vector_db_path,
    embedding_model=config.embedding_model,
    ollama_host=config.ollama_host,
    use_hybrid_search=True
)

vault_path = Path("/Users/brettgershon/Library/Mobile Documents/iCloud~md~obsidian/Documents/Organizer")
practices_file = vault_path / "05-Grids" / "Practices & Embedded Exercises.md"

print(f"\nFile exists: {practices_file.exists()}")
print(f"File path: {practices_file}")

if practices_file.exists():
    print("\nAttempting to index file...")
    try:
        result = rag._index_markdown_file(practices_file, vault_path, force=True)
        print(f"✅ Index result: {result}")
        
        # Check if it's in the database now
        collection = rag.collections['obsidian']
        rel_path = str(practices_file.relative_to(vault_path))
        
        chunks = collection.get(
            where={"filepath": rel_path},
            include=['documents']
        )
        
        print(f"\n✅ Chunks in database: {len(chunks['documents'])}")
        
        if len(chunks['documents']) > 0:
            print("\nFirst chunk preview:")
            print(chunks['documents'][0][:200] + "...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

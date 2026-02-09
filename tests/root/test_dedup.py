#!/usr/bin/env python3
"""Test dedup engine directly."""

import sys
sys.path.insert(0, '/Users/brettgershon/polly')

from core.polly import Polly
import logging

logging.basicConfig(level=logging.INFO)

# Initialize Polly (this will init dedup)
print("Initializing Polly...")
polly = Polly()

print("\n=== Testing Dedup Engine ===")
print(f"Dedup engine: {polly.dedup_engine}")

if polly.dedup_engine:
    # Test similarity check
    content = "Infinite games are about continuing play indefinitely rather than achieving a final victory state."
    title = "Test Infinite Games Note"
    
    print(f"\nChecking similarity for: '{title}'")
    print(f"Content: {content}")
    
    similar = polly.dedup_engine.check_similarity(
        content=content,
        title=title,
        similarity_threshold=0.70
    )
    
    print(f"\nFound {len(similar)} similar notes:")
    for note in similar:
        print(f"  - {note.title} (similarity: {note.similarity:.2f})")
        print(f"    Path: {note.path}")
        print(f"    Snippet: {note.snippet[:100]}...")
else:
    print("ERROR: Dedup engine is None!")

# Also test RAG directly
print("\n=== Testing RAG Directly ===")
query = "Infinite games are about continuing play"
print(f"Query: {query}")

results = polly.rag.search(query, n_results=5, source_types=['notes'])
print(f"Found {len(results)} RAG results:")
for i, result in enumerate(results[:3]):
    print(f"  {i+1}. Score: {result.score:.3f}")
    print(f"     Content: {result.doc.content[:100]}...")

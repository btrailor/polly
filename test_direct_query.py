#!/usr/bin/env python3
"""Test query directly without network."""
import asyncio
import sys
sys.path.insert(0, '/Users/brettgershon/polly')

async def test_query():
    from core.polly import Polly
    
    print("Initializing Polly...")
    polly = Polly()
    print("Polly initialized!")
    
    print("\nWave 3 components:")
    print(f"  - query_decomposer: {polly.query_decomposer is not None}")
    print(f"  - split_router: {polly.split_router is not None}")
    print(f"  - synthesizer: {polly.synthesizer is not None}")
    
    query = "What am I learning lately and what are the key concepts in my notes?"
    print(f"\nSending query: {query}")
    print("=" * 80)
    
    response_parts = []
    async for chunk in polly.query(query, stream=False):
        response_parts.append(chunk)
    
    response = "".join(response_parts)
    print(f"\nResponse: {response[:500]}...")
    
    # Check metadata
    metadata = polly.get_last_response_metadata()
    print(f"\nMetadata: {metadata}")

if __name__ == "__main__":
    asyncio.run(test_query())

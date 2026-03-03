#!/usr/bin/env python3
"""
Debug script to test query flow and identify broken pipe source.
"""

import asyncio
import sys
from core.polly import Polly

async def test_query():
    """Test a simple query and see where it fails."""
    print("Initializing Polly...")
    try:
        polly = Polly()
        print("✓ Polly initialized successfully")
        print(f"  - Knowledge writer: {polly.knowledge_writer is not None}")
        print(f"  - Router v2 enabled: {polly.router_v2 is not None}")
    except Exception as e:
        print(f"✗ Failed to initialize Polly: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nTesting simple query...")
    query = "What is quantum entanglement?"
    
    try:
        print(f"Query: {query}")
        response_chunks = []
        
        async for chunk in polly.query(query, stream=True):
            response_chunks.append(chunk)
            print(f"  Received chunk ({len(chunk)} chars)")
        
        full_response = "".join(response_chunks)
        print(f"\n✓ Query succeeded!")
        print(f"  Response length: {len(full_response)} chars")
        print(f"  First 200 chars: {full_response[:200]}")
            
    except Exception as e:
        print(f"\n✗ Query failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Try to identify the source
        if "Broken pipe" in str(e) or "[Errno 32]" in str(e):
            print("\n🔍 Broken pipe detected! This usually means:")
            print("  1. LLM provider connection failed mid-stream")
            print("  2. Subprocess terminated unexpectedly")
            print("  3. API key invalid or rate limited")
            print("\nCheck:")
            print("  - API keys are valid in ~/.polly/secrets/")
            print("  - Provider APIs are accessible")
            print("  - No rate limits hit")

if __name__ == "__main__":
    asyncio.run(test_query())

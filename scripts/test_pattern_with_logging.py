#!/usr/bin/env python3
"""
Test pattern recording with logging verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.polly import Polly
import asyncio
import logging

# Set up logging to see pattern messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def test_with_logging():
    """Test pattern recording and verify logging output."""
    
    print("=" * 60)
    print("Pattern Recording with Logging Test")
    print("=" * 60)
    
    print("\n[Step 1] Initializing Polly...")
    polly = Polly()
    
    if polly.pattern_learner is None:
        print("❌ Pattern learner not initialized!")
        return False
    
    print("✅ Polly initialized")
    print(f"   Current queries in history: {len(polly.pattern_learner.query_history)}")
    
    # Make one test query and watch the logs
    print("\n[Step 2] Making test query (watch for log messages)...")
    print("-" * 60)
    
    query = "How do I use Git with GitHub in my projects?"
    print(f"\nQuery: {query}\n")
    
    response_parts = []
    async for chunk in polly.query(query, stream=True):
        response_parts.append(chunk)
    
    full_response = ''.join(response_parts)
    
    print("-" * 60)
    print(f"\n✅ Response received ({len(full_response)} chars)")
    print(f"   Preview: {full_response[:100]}...")
    
    # Verify it was recorded
    print("\n[Step 3] Verifying pattern was recorded...")
    
    latest_query = polly.pattern_learner.query_history[-1]
    if latest_query['query'] == query:
        print(f"✅ Query recorded: {latest_query['query']}")
        print(f"   Domains: {latest_query['domains']}")
        print(f"   Timestamp: {latest_query['timestamp']}")
    else:
        print(f"❌ Latest query doesn't match!")
        print(f"   Expected: {query}")
        print(f"   Got: {latest_query['query']}")
    
    # Check file was updated
    patterns_file = polly.pattern_learner.storage_path
    if patterns_file.exists():
        import json
        data = json.loads(patterns_file.read_text())
        file_query_count = len(data.get('query_history', []))
        mem_query_count = len(polly.pattern_learner.query_history)
        
        print(f"\n[Step 4] Verifying storage...")
        print(f"   In-memory queries: {mem_query_count}")
        print(f"   File queries: {file_query_count}")
        
        if file_query_count == mem_query_count:
            print("✅ Storage synchronized!")
        else:
            print("⚠️  Storage mismatch!")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_with_logging())
    sys.exit(0 if result else 1)

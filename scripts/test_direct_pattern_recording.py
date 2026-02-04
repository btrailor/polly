#!/usr/bin/env python3
"""
Simple test - directly test Polly core pattern recording
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.polly import Polly
import asyncio
import json


async def test_direct_pattern_recording():
    """Test pattern recording directly through Polly core."""
    
    print("=" * 60)
    print("Direct Pattern Recording Test")
    print("=" * 60)
    
    # Initialize Polly
    print("\n[Step 1] Initializing Polly...")
    polly = Polly()
    
    if polly.pattern_learner is None:
        print("❌ Pattern learner not initialized!")
        return False
    
    print("✅ Polly initialized with pattern learner")
    print(f"   Storage: {polly.pattern_learner.storage_path}")
    
    # Check initial state
    patterns_file = polly.pattern_learner.storage_path
    if patterns_file.exists():
        initial_data = json.loads(patterns_file.read_text())
        initial_count = len(initial_data.get('query_history', []))
        print(f"✅ Initial query history: {initial_count} queries")
    else:
        initial_count = 0
        print("⚠️  Patterns file will be created")
    
    # Make test queries
    print("\n[Step 2] Making test queries...")
    
    test_queries = [
        "How do I set up Docker containers?",
        "Explain norns scripting",
        "Best practices for documentation"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n  Query {i}: {query}")
        try:
            # query() is an async generator, collect the full response
            response_parts = []
            async for chunk in polly.query(query, stream=True):
                response_parts.append(chunk)
            
            full_response = ''.join(response_parts)
            print(f"  ✅ Response: {full_response[:80]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Check patterns were saved
    print("\n[Step 3] Verifying patterns were saved...")
    
    if patterns_file.exists():
        final_data = json.loads(patterns_file.read_text())
        final_count = len(final_data.get('query_history', []))
        new_queries = final_count - initial_count
        
        print(f"  Initial: {initial_count}")
        print(f"  Final: {final_count}")
        print(f"  New: {new_queries}")
        
        if new_queries >= 3:
            print(f"✅ All {new_queries} queries recorded!")
        else:
            print(f"⚠️  Expected 3 new queries, found {new_queries}")
        
        # Show latest queries
        print("\n[Step 4] Latest queries:")
        for query in final_data.get('query_history', [])[-3:]:
            print(f"  - {query.get('query', '')[:60]}")
            print(f"    Domains: {query.get('domains', [])}")
        
        return True
    else:
        print("❌ Patterns file not created!")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_direct_pattern_recording())
    sys.exit(0 if result else 1)

#!/usr/bin/env python3
"""
Test pattern persistence after restart
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.polly import Polly
import asyncio


async def test_persistence():
    """Test that patterns persist after Polly restart."""
    
    print("=" * 60)
    print("Pattern Persistence Test")
    print("=" * 60)
    
    print("\n[Test] Creating new Polly instance...")
    polly = Polly()
    
    if polly.pattern_learner is None:
        print("❌ Pattern learner not initialized!")
        return False
    
    print("✅ Polly initialized")
    
    # Check query history loaded
    query_count = len(polly.pattern_learner.query_history)
    print(f"✅ Loaded {query_count} queries from storage")
    
    if query_count >= 6:
        print("\n✅ SUCCESS: All queries persisted!")
        
        print("\n[Sample Queries]")
        for i, query in enumerate(polly.pattern_learner.query_history[-3:], 1):
            print(f"{i}. {query['query']}")
            print(f"   Domains: {query['domains']}")
            print(f"   Timestamp: {query['timestamp']}")
        
        return True
    else:
        print(f"\n⚠️  Expected at least 6 queries, found {query_count}")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_persistence())
    sys.exit(0 if result else 1)

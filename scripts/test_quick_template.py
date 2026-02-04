#!/usr/bin/env python3
"""
Quick test - one query with template extraction
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.polly import Polly
import asyncio
import json


async def quick_test():
    """Quick test with one query."""
    
    print("Quick Template Test")
    print("=" * 60)
    
    polly = Polly()
    
    if polly.pattern_learner is None:
        print("❌ Pattern learner not initialized!")
        return False
    
    print("✅ Polly initialized")
    
    # One quick query
    query = "How do I use Redis for caching?"
    print(f"\nQuery: {query}")
    
    response_parts = []
    async for chunk in polly.query(query, stream=True):
        response_parts.append(chunk)
    
    print(f"✅ Response received")
    
    # Check pattern
    latest = polly.pattern_learner.query_history[-1]
    print(f"\nLatest query:")
    print(f"  Query: {latest['query']}")
    print(f"  Template: {latest.get('template', 'N/A')}")
    print(f"  Fills: {latest.get('fills', {})}")
    print(f"  Domains: {latest.get('domains', [])}")
    
    # Check if pattern was detected
    if polly.pattern_learner.query_patterns:
        print(f"\nQuery patterns detected: {len(polly.pattern_learner.query_patterns)}")
        for template, qp in polly.pattern_learner.query_patterns.items():
            print(f"  - {template} (freq: {qp.frequency})")
    
    print("\n✅ Test complete!")
    return True


if __name__ == "__main__":
    result = asyncio.run(quick_test())
    sys.exit(0 if result else 1)

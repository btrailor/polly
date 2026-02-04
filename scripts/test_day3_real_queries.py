#!/usr/bin/env python3
"""
Test template extraction with real Polly queries
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.polly import Polly
import asyncio
import json


async def test_real_queries():
    """Test template extraction through real Polly usage."""
    
    print("=" * 60)
    print("Real Query Template Test")
    print("=" * 60)
    
    # Clear existing patterns for clean test
    patterns_file = Path.home() / ".polly" / "patterns.json"
    if patterns_file.exists():
        backup = Path.home() / ".polly" / "patterns_backup.json"
        patterns_file.rename(backup)
        print(f"  Backed up existing patterns to {backup.name}")
    
    print("\n[Step 1] Initializing Polly...")
    polly = Polly()
    
    if polly.pattern_learner is None:
        print("❌ Pattern learner not initialized!")
        return False
    
    print("✅ Polly initialized")
    
    # Test queries with different patterns
    print("\n[Step 2] Making queries with similar patterns...")
    
    test_queries = [
        "How do I use Redis with Node.js?",
        "How do I use MongoDB with Python?",
        "What's the best way to handle errors?",
        "What's the best way to structure files?",
        "Explain how webhooks work",
        "Explain how JWT authentication works",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n  Query {i}/{len(test_queries)}: {query}")
        
        try:
            response_parts = []
            async for chunk in polly.query(query, stream=True):
                response_parts.append(chunk)
            
            full_response = ''.join(response_parts)
            print(f"  ✅ Response: {full_response[:60]}...")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Check patterns detected
    print("\n[Step 3] Analyzing detected patterns...")
    
    query_patterns = polly.pattern_learner.query_patterns
    print(f"  Detected {len(query_patterns)} unique query patterns")
    
    if len(query_patterns) > 0:
        print("\n  Pattern Details:")
        for template, qp in query_patterns.items():
            print(f"\n    Template: {template}")
            print(f"      Frequency: {qp.frequency}")
            print(f"      Domains: {qp.domains}")
            
            if qp.common_fills:
                print(f"      Common fills:")
                for placeholder, values in qp.common_fills.items():
                    print(f"        {placeholder}: {values}")
    
    # Check query history
    print("\n[Step 4] Checking query history...")
    
    query_history = polly.pattern_learner.query_history
    print(f"  Total queries: {len(query_history)}")
    
    if query_history:
        print("\n  Sample queries with templates:")
        for query in query_history[-3:]:
            print(f"    Query: {query['query']}")
            print(f"      Template: {query.get('template', 'N/A')}")
            print(f"      Fills: {query.get('fills', {})}")
            print()
    
    # Verify storage
    print("[Step 5] Verifying storage...")
    
    if patterns_file.exists():
        data = json.loads(patterns_file.read_text())
        
        stored_patterns = len(data.get('query_patterns', []))
        stored_queries = len(data.get('query_history', []))
        
        print(f"  ✅ Patterns in file: {stored_patterns}")
        print(f"  ✅ Queries in file: {stored_queries}")
        
        # Check a sample query has template
        if data.get('query_history'):
            sample = data['query_history'][-1]
            if 'template' in sample:
                print(f"  ✅ Templates are being saved")
                print(f"     Last template: {sample['template']}")
            else:
                print(f"  ⚠️  Templates not in saved data")
    else:
        print(f"  ⚠️  Patterns file not created")
    
    print("\n" + "=" * 60)
    print("✅ Real Query Test Complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_real_queries())
    sys.exit(0 if result else 1)

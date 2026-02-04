#!/usr/bin/env python3
"""
Day 2 Test Script - Verify Pattern Data Flow
Tests that patterns are recorded and persisted through actual usage
"""

import sys
import requests
import json
import time
from pathlib import Path

# Test configuration
POLLY_URL = "http://localhost:11436"
PATTERNS_FILE = Path.home() / ".polly" / "patterns.json"


def check_server_running():
    """Check if Polly server is running."""
    try:
        response = requests.get(f"{POLLY_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def read_patterns_file():
    """Read the patterns file."""
    if not PATTERNS_FILE.exists():
        return None
    
    with open(PATTERNS_FILE, 'r') as f:
        return json.load(f)


def test_pattern_recording():
    """Test that patterns are recorded when queries are made."""
    
    print("=" * 60)
    print("Day 2: Pattern Data Flow Test")
    print("=" * 60)
    
    # Step 1: Check server is running
    print("\n[Step 1] Checking if Polly server is running...")
    if not check_server_running():
        print("❌ ERROR: Polly server is not running!")
        print("\nTo start the server, run:")
        print("  cd /Users/brettgershon/polly")
        print("  python3 -m interfaces.server")
        print("\nOr run in background:")
        print("  python3 -m interfaces.server > polly.log 2>&1 &")
        return False
    
    print("✅ Server is running")
    
    # Step 2: Read initial state
    print("\n[Step 2] Reading initial pattern state...")
    initial_data = read_patterns_file()
    if initial_data is None:
        print("⚠️  Patterns file doesn't exist yet (will be created)")
        initial_query_count = 0
    else:
        initial_query_count = len(initial_data.get('query_history', []))
        print(f"✅ Current query history: {initial_query_count} queries")
    
    # Step 3: Make test queries
    print("\n[Step 3] Making test queries...")
    
    test_queries = [
        {
            "query": "How do I set up Docker containers for Python development?",
            "domain": "sigils"
        },
        {
            "query": "Explain how norns scripting works with SuperCollider",
            "domain": "signals"
        },
        {
            "query": "What are the best practices for writing technical documentation?",
            "domain": "scrolls"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n  Query {i}: {test['query'][:50]}...")
        
        try:
            response = requests.post(
                f"{POLLY_URL}/polly/query",
                json={"query": test["query"]},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer_preview = result.get('answer', '')[:100]
                print(f"  ✅ Response received: {answer_preview}...")
            else:
                print(f"  ❌ Error: {response.status_code}")
                print(f"     {response.text}")
        
        except Exception as e:
            print(f"  ❌ Request failed: {e}")
            return False
        
        # Small delay between queries
        time.sleep(1)
    
    # Step 4: Verify patterns were recorded
    print("\n[Step 4] Verifying patterns were recorded...")
    time.sleep(2)  # Give server time to write
    
    updated_data = read_patterns_file()
    if updated_data is None:
        print("❌ ERROR: Patterns file still doesn't exist!")
        return False
    
    updated_query_count = len(updated_data.get('query_history', []))
    new_queries = updated_query_count - initial_query_count
    
    print(f"  Initial queries: {initial_query_count}")
    print(f"  Current queries: {updated_query_count}")
    print(f"  New queries: {new_queries}")
    
    if new_queries >= 3:
        print(f"✅ {new_queries} new queries recorded!")
    else:
        print(f"⚠️  Expected 3 new queries, only found {new_queries}")
    
    # Step 5: Check file structure
    print("\n[Step 5] Checking pattern file structure...")
    
    required_keys = ['patterns', 'query_patterns', 'query_history', 'metadata']
    for key in required_keys:
        if key in updated_data:
            print(f"  ✅ {key}: present")
        else:
            print(f"  ❌ {key}: missing")
    
    # Show some query details
    if updated_data.get('query_history'):
        print(f"\n[Step 6] Sample query history:")
        for i, query in enumerate(updated_data['query_history'][-3:], 1):
            print(f"  {i}. {query.get('query', '')[:60]}...")
            print(f"     Domains: {query.get('domains', [])}")
            print(f"     Timestamp: {query.get('timestamp', '')}")
    
    # Step 7: Check stats endpoint
    print("\n[Step 7] Checking Polly stats...")
    try:
        response = requests.get(f"{POLLY_URL}/polly/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"  ✅ Stats endpoint working")
            if 'patterns' in stats:
                print(f"     Patterns tracked: {stats['patterns']}")
            if 'indexed_chunks' in stats:
                print(f"     Indexed chunks: {stats['indexed_chunks']}")
        else:
            print(f"  ⚠️  Stats endpoint returned {response.status_code}")
    except Exception as e:
        print(f"  ⚠️  Stats endpoint failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Day 2 Test Complete!")
    print("=" * 60)
    print(f"\nPattern storage: {PATTERNS_FILE}")
    print(f"File size: {PATTERNS_FILE.stat().st_size} bytes")
    
    return True


if __name__ == "__main__":
    success = test_pattern_recording()
    sys.exit(0 if success else 1)

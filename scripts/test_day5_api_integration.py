#!/usr/bin/env python3
"""
Test Day 5: API Integration Test

Tests the pattern learning API endpoint to verify it works
with the full server stack.
"""

import requests
import json
import time


def test_api_endpoint():
    """Test the pattern learning API endpoint."""
    print("\n=== API Endpoint Test ===")
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:11436/health', timeout=2)
        if response.status_code == 200:
            print("✓ Server is running")
        else:
            print("✗ Server returned unexpected status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Server not running: {e}")
        print("  Start server with: cd /Users/brettgershon/polly && python3 -m uvicorn interfaces.server:create_app --host 0.0.0.0 --port 11436 --factory")
        return False
    
    # Test the pattern learning endpoint
    test_data = {
        "conversation_id": "test_api_conv_1",
        "messages": [
            {
                "role": "user",
                "content": "I want to build a Docker container for my Python FastAPI application"
            },
            {
                "role": "assistant",
                "content": "Great! Docker is an excellent choice for Python FastAPI apps. You'll want to create a Dockerfile with python:3.11-slim as the base image..."
            },
            {
                "role": "user",
                "content": "How do I handle environment variables in Docker for Python?"
            },
            {
                "role": "assistant",
                "content": "For Python applications in Docker, you can use environment variables in several ways..."
            }
        ],
        "category": "sigils"
    }
    
    print("\nSending conversation to pattern learning endpoint...")
    
    try:
        response = requests.post(
            'http://localhost:11436/polly/patterns/learn-from-conversation',
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ API call successful!")
            print(f"  Status: {result.get('status')}")
            print(f"  Patterns learned: {result.get('patterns_learned')}")
            print(f"  Conversation ID: {result.get('conversation_id')}")
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return False


def test_multiple_conversations():
    """Test learning from multiple conversations to detect patterns."""
    print("\n=== Multiple Conversations Test ===")
    
    conversations = [
        {
            "conversation_id": "multi_1",
            "messages": [
                {"role": "user", "content": "Using React with TypeScript for my frontend"},
                {"role": "assistant", "content": "React and TypeScript is a powerful combination..."},
                {"role": "user", "content": "Best React TypeScript practices?"},
                {"role": "assistant", "content": "When working with React and TypeScript..."}
            ]
        },
        {
            "conversation_id": "multi_2",
            "messages": [
                {"role": "user", "content": "React hooks with TypeScript types"},
                {"role": "assistant", "content": "TypeScript provides excellent type safety for React hooks..."},
                {"role": "user", "content": "How to type React components in TypeScript?"},
                {"role": "assistant", "content": "React component typing in TypeScript..."}
            ]
        },
        {
            "conversation_id": "multi_3",
            "messages": [
                {"role": "user", "content": "Setting up Redis for caching in my API"},
                {"role": "assistant", "content": "Redis is perfect for caching in APIs..."},
                {"role": "user", "content": "Best Redis data structures for API caching?"},
                {"role": "assistant", "content": "For API caching with Redis, strings and hashes..."}
            ]
        }
    ]
    
    patterns_learned = []
    
    for conv in conversations:
        try:
            response = requests.post(
                'http://localhost:11436/polly/patterns/learn-from-conversation',
                json=conv,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                patterns = result.get('patterns_learned', 0)
                patterns_learned.append(patterns)
                print(f"✓ Conversation {conv['conversation_id']}: {patterns} patterns")
            else:
                print(f"✗ Failed for {conv['conversation_id']}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"✗ Request failed: {e}")
            return False
    
    total_patterns = sum(patterns_learned)
    print(f"\n✓ Total patterns learned: {total_patterns}")
    print(f"  Expected: React ↔ TypeScript pattern (occurred 2x)")
    print(f"  Expected: Redis ↔ API pattern (occurred 1x)")
    
    return len(patterns_learned) == 3


def test_pattern_retrieval():
    """Test that patterns can be retrieved after learning."""
    print("\n=== Pattern Retrieval Test ===")
    
    # Check patterns file
    import os
    patterns_file = os.path.expanduser('~/.polly/patterns.json')
    
    if not os.path.exists(patterns_file):
        print(f"✗ Patterns file not found: {patterns_file}")
        return False
    
    print(f"✓ Patterns file exists: {patterns_file}")
    
    # Read patterns
    try:
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        
        patterns = data.get('patterns', [])
        query_patterns = data.get('query_patterns', [])
        query_history = data.get('query_history', [])
        
        print(f"\n  Stored patterns: {len(patterns)}")
        print(f"  Query patterns: {len(query_patterns)}")
        print(f"  Query history: {len(query_history)}")
        
        # Show conceptual patterns
        conceptual = [p for p in patterns if p.get('pattern_type') == 'conceptual']
        print(f"\n  Conceptual patterns: {len(conceptual)}")
        
        for pattern in conceptual[:3]:  # Show first 3
            print(f"\n    → {pattern.get('name')}")
            print(f"      Occurrences: {pattern.get('occurrences')}")
            print(f"      Confidence: {pattern.get('confidence', 0):.2f}")
            print(f"      Domains: {pattern.get('domains')}")
        
        return len(patterns) > 0
        
    except Exception as e:
        print(f"✗ Failed to read patterns: {e}")
        return False


def main():
    """Run all API tests."""
    print("=" * 60)
    print("Day 5: Pattern Learning API Integration Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("API Endpoint", test_api_endpoint()))
    
    # Only run other tests if server is available
    if results[0][1]:
        time.sleep(0.5)  # Brief pause between tests
        results.append(("Multiple Conversations", test_multiple_conversations()))
        time.sleep(0.5)
        results.append(("Pattern Retrieval", test_pattern_retrieval()))
    
    # Summary
    print("\n" + "=" * 60)
    print("API Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if not results[0][1]:
        print("\nNote: Server must be running for these tests.")
        print("Start with: cd /Users/brettgershon/polly && python3 -m uvicorn interfaces.server:create_app --host 0.0.0.0 --port 11436 --factory")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

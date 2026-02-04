#!/usr/bin/env python3
"""
Test Pattern Display - API Endpoint

Tests that the GET /polly/patterns endpoint returns pattern data correctly.
"""

import requests
import json


def test_patterns_endpoint():
    """Test the patterns GET endpoint."""
    print("=" * 70)
    print("Testing Pattern Display API Endpoint")
    print("=" * 70)
    
    # Check if server is running
    try:
        response = requests.get('http://localhost:11436/health', timeout=2)
        if response.status_code == 200:
            print("✓ Server is running\n")
        else:
            print("✗ Server returned unexpected status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Server not running: {e}")
        print("\nStart server with:")
        print("  cd /Users/brettgershon/polly")
        print("  python3 -m uvicorn interfaces.server:create_app --host 0.0.0.0 --port 11436 --factory")
        return False
    
    # Test the patterns endpoint
    print("Testing GET /polly/patterns...\n")
    
    try:
        response = requests.get('http://localhost:11436/polly/patterns', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✓ API call successful!")
            print(f"\n  Total patterns: {data.get('total_count', 0)}")
            print(f"  Conceptual patterns: {len(data.get('patterns', []))}")
            print(f"  Query patterns: {len(data.get('query_patterns', []))}")
            
            # Show some sample patterns
            if data.get('patterns'):
                print("\n  Sample Conceptual Patterns:")
                for pattern in data['patterns'][:3]:
                    print(f"    → {pattern['name']}")
                    print(f"      Type: {pattern['pattern_type']}")
                    print(f"      Occurrences: {pattern['occurrences']}")
                    print(f"      Confidence: {pattern['confidence']:.0%}")
                    print(f"      Domains: {', '.join(pattern['domains'])}")
                    print()
            
            if data.get('query_patterns'):
                print("  Sample Query Patterns:")
                for qp in data['query_patterns'][:3]:
                    print(f"    → {qp['query_template']}")
                    print(f"      Frequency: {qp['frequency']}")
                    print(f"      Domains: {', '.join(qp['domains'])}")
                    print()
            
            # Validate structure
            assert 'patterns' in data, "Missing 'patterns' key"
            assert 'query_patterns' in data, "Missing 'query_patterns' key"
            assert 'total_count' in data, "Missing 'total_count' key"
            
            for pattern in data['patterns']:
                assert 'id' in pattern
                assert 'name' in pattern
                assert 'pattern_type' in pattern
                assert 'domains' in pattern
                assert 'occurrences' in pattern
                assert 'confidence' in pattern
            
            print("✓ Data structure validated")
            
            return True
        else:
            print(f"✗ API returned status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ API request failed: {e}")
        return False


def test_patterns_file():
    """Check the patterns file directly."""
    print("\n" + "=" * 70)
    print("Checking Patterns File")
    print("=" * 70)
    
    import os
    patterns_file = os.path.expanduser('~/.polly/patterns.json')
    
    if not os.path.exists(patterns_file):
        print(f"✗ Patterns file not found: {patterns_file}")
        print("\n  Patterns will be created after using Polly.")
        return False
    
    print(f"✓ Patterns file exists: {patterns_file}")
    
    try:
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        
        patterns = data.get('patterns', [])
        query_patterns = data.get('query_patterns', [])
        
        print(f"\n  File size: {os.path.getsize(patterns_file)} bytes")
        print(f"  Patterns: {len(patterns)}")
        print(f"  Query patterns: {len(query_patterns)}")
        
        if patterns:
            print("\n  Patterns in file:")
            for p in patterns[:5]:
                print(f"    → {p.get('name', 'Unknown')}")
                print(f"      Type: {p.get('pattern_type', 'unknown')}")
                print(f"      Occurrences: {p.get('occurrences', 0)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to read patterns file: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    
    results = []
    
    # Check file first
    results.append(("Patterns File", test_patterns_file()))
    
    # Then test API
    results.append(("Patterns API", test_patterns_endpoint()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if not results[1][1]:
        print("\n💡 Note: Start the Polly server to test the API endpoint")
        print("   The Electron app will fetch patterns from this endpoint")
    else:
        print("\n🎉 Patterns API is working!")
        print("\n   Patterns will now be displayed in:")
        print("   1. Dashboard - Pattern count card")
        print("   2. Patterns page - Full pattern details")
        print("\n   To view: Open Polly Electron app → Click 'Patterns' in sidebar")
    
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

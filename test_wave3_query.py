#!/usr/bin/env python3
"""
Test Wave 3 pipeline with a complex query.
"""
import requests
import json
import time

# Wait for server to be ready
print("Waiting for server to be ready...")
for i in range(30):
    try:
        response = requests.get("http://localhost:11436/health", timeout=2)
        if response.status_code == 200:
            print("✓ Server is ready")
            break
    except:
        pass
    time.sleep(1)
else:
    print("✗ Server not ready after 30 seconds")
    exit(1)

# Test complex query that should trigger Wave 3
query = "What am I learning lately and what are the key concepts in my notes?"
print(f"\nSending query: {query}")
print("=" * 80)

response = requests.post(
    "http://localhost:11436/polly/query",
    json={"query": query, "stream": False},
    timeout=120
)

if response.status_code == 200:
    result = response.json()
    print("\n✓ Query successful!")
    print(f"\nResponse: {result.get('response', '')[:500]}...")
    
    # Check for Wave 3 metadata
    metadata = result.get('metadata', {})
    print(f"\nMetadata:")
    print(f"  - routing_path: {metadata.get('routing_path')}")
    print(f"  - decomposed: {metadata.get('decomposed', False)}")
    print(f"  - local_count: {metadata.get('local_count', 0)}")
    print(f"  - cloud_count: {metadata.get('cloud_count', 0)}")
    print(f"  - synthesized: {metadata.get('synthesized', False)}")
    
    if metadata.get('decomposed'):
        print("\n🎉 Wave 3 pipeline executed successfully!")
    else:
        print("\n⚠️  Wave 3 pipeline was not triggered")
else:
    print(f"\n✗ Query failed: {response.status_code}")
    print(response.text)

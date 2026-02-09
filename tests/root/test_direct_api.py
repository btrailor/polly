#!/usr/bin/env python3
"""
Direct test of Polly query logic - imports the actual running code
"""
import sys
import os

# Make a simple API call to the running server
import http.client
import json

conn = http.client.HTTPConnection("localhost", 11436)

query_payload = {
    "query": "What GitHub repositories do you see?",
    "conversation_id": "direct-test-debug",
    "use_rag": True
}

headers = {"Content-Type": "application/json"}
conn.request("POST", "/polly/query", json.dumps(query_payload), headers)

response = conn.getresponse()
data = response.read()

print("=" * 80)
print("RESPONSE FROM SERVER:")
print(f"Status: {response.status}")
print(f"Data length: {len(data)} bytes")
print("=" * 80)

if data:
    try:
        result = json.loads(data)
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError:
        print("Raw response (not JSON):")
        print(data.decode('utf-8'))
else:
    print("Empty response")
print("\n")
print("=" * 80)
print("Check the Electron app terminal for server debug logs showing:")
print("  - 'Formatting X results (Y GitHub) for context'")
print("  - 'RAG context has GitHub content: True/False'")
print("  - 'Context preview: ...'")
print("=" * 80)

conn.close()

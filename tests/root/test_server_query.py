#!/usr/bin/env python3
"""Test querying the server directly to see what context is being passed to the LLM"""

import requests
import json

def test_query():
    url = "http://localhost:11436/polly/query"
    
    query = 'Concerning my "Practices and Exercises" framework. What is something I might do today to keep in practice?'
    
    print("=" * 80)
    print("Testing Server Query")
    print("=" * 80)
    print(f"\nQuery: {query}")
    print("\nSending request to server...")
    
    response = requests.post(
        url,
        json={"query": query, "stream": False},
        timeout=60
    )
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ Server responded successfully")
        print("\n" + "-" * 80)
        print("Response:")
        print("-" * 80)
        print(result.get("response", "No response field"))
        print("\n" + "=" * 80)
    else:
        print(f"\n❌ Server error: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    test_query()

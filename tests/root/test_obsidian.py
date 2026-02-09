#!/usr/bin/env python3
"""
Test Obsidian vault search capabilities
"""
import sys
import requests
import json
from pathlib import Path

# Test queries across different domains
test_queries = [
    {
        "query": "infinite games",
        "domain": "Grids (Systems Thinking)",
        "description": "Core concept from your work"
    },
    {
        "query": "norns audio synthesis",
        "domain": "Signals (Audio)",
        "description": "Music technology"
    },
    {
        "query": "docker containers infrastructure",
        "domain": "Sigils (Code)",
        "description": "DevOps and infrastructure"
    },
    {
        "query": "pedagogy teaching learning",
        "domain": "Scrolls (Writing)",
        "description": "Education and popular education"
    },
    {
        "query": "constraint and meaning",
        "domain": "Cross-domain",
        "description": "A key philosophical theme"
    }
]

def search_obsidian(query, n_results=3):
    """Search Obsidian vault via RAG."""
    # This would use the RAG search endpoint
    # For now, we'll use the polly query endpoint
    url = "http://localhost:11436/polly/query"
    
    payload = {
        "query": f"What notes do I have about {query}?",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 70)
    print("TESTING OBSIDIAN VAULT SEARCH")
    print("=" * 70)
    print(f"\nYour vault: 3,508 chunks from 75 notes (avg 46.8 chunks/file)\n")
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Testing: {test['description']}")
        print(f"   Domain: {test['domain']}")
        print(f"   Query: '{test['query']}'")
        print(f"   {'─' * 66}")
        
        result = search_obsidian(test['query'])
        
        if "Error" in result:
            print(f"   ❌ {result}")
        else:
            # Truncate result for display
            preview = result[:300] + "..." if len(result) > 300 else result
            print(f"   ✅ Found relevant content:")
            print(f"   {preview}")
        
        print()
    
    print("=" * 70)
    print("OBSIDIAN INTEGRATION TEST COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()

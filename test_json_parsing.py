#!/usr/bin/env python3
"""Test JSON parsing with newlines."""
import json
import re

# Simulate the problematic response
response = '''{
    "is_complex": true,
    "reasoning": "Test",
    "sub_queries": [
        {
            "query": "For each domain, extract concepts based on:
            - Frequency of mention
            - Explicit highlighting",
            "type": "rag_answerable",
            "confidence": 0.95
        }
    ]
}'''

print("Original response:")
print(response)
print("\n" + "="*80 + "\n")

# Try parsing with strict=False
try:
    result = json.loads(response, strict=False)
    print("✓ Parsed with strict=False:")
    print(json.dumps(result, indent=2))
except json.JSONDecodeError as e:
    print(f"✗ Failed with strict=False: {e}")
    
    # Try fixing newlines
    fixed_response = re.sub(
        r':\s*"([^"]*)"', 
        lambda m: f': "{m.group(1).replace(chr(10), "\\n").replace(chr(13), "\\r")}"',
        response
    )
    print("\nFixed response:")
    print(fixed_response)
    print("\n" + "="*80 + "\n")
    
    try:
        result = json.loads(fixed_response, strict=False)
        print("✓ Parsed after fixing:")
        print(json.dumps(result, indent=2))
    except json.JSONDecodeError as e2:
        print(f"✗ Still failed: {e2}")

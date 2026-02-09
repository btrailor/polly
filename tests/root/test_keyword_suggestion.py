#!/usr/bin/env python3
"""
Test script for keyword suggestion endpoint.
This tests the AI-powered keyword suggestion functionality.

NOTE: This requires the Polly server to be running on localhost:11436
and requires an LLM model to be available (Ollama or cloud provider).
"""

import sys
import json
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_keyword_suggestion():
    """Test the keyword suggestion endpoint."""
    from interfaces.server import create_app
    from httpx import AsyncClient
    
    print("=" * 60)
    print("Testing Keyword Suggestion API")
    print("=" * 60)
    
    # Create app
    app = create_app()
    
    # Test cases
    test_cases = [
        {
            "name": "Software Development",
            "description": "Code, repositories, infrastructure, and technical projects",
            "existingKeywords": ["code", "git"]
        },
        {
            "name": "Audio Programming",
            "description": "Music synthesis, sound design, and real-time audio processing",
            "existingKeywords": ["norns", "supercollider"]
        },
        {
            "name": "Machine Learning",
            "description": "AI models, neural networks, and data science projects",
            "existingKeywords": []
        }
    ]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: {test_case['name']}")
            print(f"   Description: {test_case['description']}")
            print(f"   Existing keywords: {test_case['existingKeywords']}")
            
            try:
                response = await client.post(
                    "/polly/domains/suggest-keywords",
                    json=test_case
                )
                
                if response.status_code != 200:
                    print(f"   ✗ Error: HTTP {response.status_code}")
                    print(f"   Response: {response.text}")
                    continue
                
                result = response.json()
                suggested = result.get("suggestedKeywords", [])
                reasoning = result.get("reasoning", "")
                
                print(f"   ✓ Received {len(suggested)} suggestions:")
                for kw in suggested[:5]:  # Show first 5
                    print(f"     - {kw['keyword']} (confidence: {kw['confidence']:.2f})")
                if len(suggested) > 5:
                    print(f"     ... and {len(suggested) - 5} more")
                
                if reasoning:
                    print(f"   Reasoning: {reasoning[:100]}...")
                
            except Exception as e:
                print(f"   ✗ Error: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✓ Keyword suggestion test complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(test_keyword_suggestion())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

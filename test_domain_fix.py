#!/usr/bin/env python3
"""
Test script to verify domain type fix
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.polly import Polly

async def test_query():
    """Test a GitHub integration query."""
    print("Initializing Polly...")
    polly = Polly()
    
    print("\nTesting query: 'list all my github repositories'")
    print("-" * 60)
    
    try:
        response = ""
        async for chunk in polly.query("list all my github repositories", stream=True):
            response += chunk
            print(chunk, end='', flush=True)
        
        print("\n" + "-" * 60)
        print("\n✅ Query completed successfully!")
        print(f"\nResponse length: {len(response)} characters")
        
        # Check if we got repository data
        if "repository" in response.lower() or "repo" in response.lower():
            print("✅ Response includes repository information")
        else:
            print("⚠️  Response may not include repository information")
            
    except Exception as e:
        print(f"\n❌ Query failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_query())
    sys.exit(0 if success else 1)

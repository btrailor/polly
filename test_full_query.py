#!/usr/bin/env python3
"""
Full end-to-end test of Polly query including boosting
"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.config import get_config
from core.polly import Polly

async def test_full_query():
    """Test the complete query flow"""
    config = get_config()
    polly = Polly(config)
    
    query = "What GitHub repos do you see?"
    print(f"Query: '{query}'")
    print("=" * 60)
    
    # Get response (don't stream for easier testing)
    response_parts = []
    async for chunk in polly.query(query, stream=True):
        response_parts.append(chunk)
        print(chunk, end='', flush=True)
    
    print("\n" + "=" * 60)
    full_response = ''.join(response_parts)
    
    # Check if response mentions actual repos
    repos_mentioned = []
    test_repos = ['norns-shnth-patches', 'Journey-of-Faith', 'btrailor.github.io', 
                  'two_tangles', 'nmMelodyMagic', 'libavr32', 'psyq']
    
    for repo in test_repos:
        if repo.lower() in full_response.lower():
            repos_mentioned.append(repo)
    
    print(f"\nRepos mentioned in response: {len(repos_mentioned)}")
    for repo in repos_mentioned:
        print(f"  ✓ {repo}")
    
    if len(repos_mentioned) == 0:
        print("\n⚠️  NO GITHUB REPOS MENTIONED IN RESPONSE")
    else:
        print(f"\n✓ SUCCESS - {len(repos_mentioned)} repos found in response")

if __name__ == "__main__":
    asyncio.run(test_full_query())

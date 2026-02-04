"""
Test script for GitHub Models Provider
Tests basic connectivity and functionality
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.providers.github_provider import GitHubModelsAdapter
from core.secrets_manager import get_secrets_manager


async def test_github_provider():
    """Test GitHub Models provider"""
    print("=" * 60)
    print("Testing GitHub Models Provider")
    print("=" * 60)
    
    # Get token from secrets manager
    secrets = get_secrets_manager()
    token = secrets.get_secret('github', fallback_to_env=True)
    
    if not token:
        print("❌ No GitHub token found")
        print("   Set token with: polly keys set github <YOUR_TOKEN>")
        print("   Or: export GITHUB_TOKEN=<YOUR_TOKEN>")
        return False
    
    print(f"✓ Found GitHub token (length: {len(token)})")
    
    # Initialize provider
    try:
        provider = GitHubModelsAdapter(token=token)
        print(f"✓ Initialized provider: {provider}")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    # Test credential validation
    print("\nValidating credentials...")
    try:
        is_valid = await provider.validate_credentials()
        if is_valid:
            print("✓ Credentials valid")
        else:
            print("❌ Credentials invalid")
            return False
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False
    
    # Test basic completion
    print("\nTesting completion...")
    messages = [
        {"role": "user", "content": "Say 'Hello from GitHub Models!' and nothing else."}
    ]
    
    try:
        response = await provider.complete(
            messages=messages,
            model="openai/gpt-4o-mini",
            max_tokens=50,
            temperature=0.7
        )
        
        print(f"✓ Completion successful")
        print(f"  Model: {response.model}")
        print(f"  Provider: {response.provider}")
        print(f"  Tokens: {response.tokens_in} in, {response.tokens_out} out")
        print(f"  Cost: ${response.cost:.4f}")
        print(f"  Content: {response.content}")
    except Exception as e:
        print(f"❌ Completion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test streaming
    print("\nTesting streaming...")
    try:
        print("  Response: ", end="", flush=True)
        async for chunk in provider.stream(
            messages=[{"role": "user", "content": "Count to 3 slowly: one"}],
            model="openai/gpt-4o-mini",
            max_tokens=30
        ):
            print(chunk, end="", flush=True)
        print("\n✓ Streaming successful")
    except Exception as e:
        print(f"\n❌ Streaming failed: {e}")
        return False
    
    # List available models
    print("\nAvailable models:")
    models = provider.get_models()
    for model in models[:5]:  # Show first 5
        print(f"  • {model.name} ({model.id})")
        print(f"    Context: {model.context_length:,} tokens")
        print(f"    Pricing: ${model.pricing['input']:.2f}/${model.pricing['output']:.2f} per 1M tokens")
    
    print(f"\n  ... and {len(models) - 5} more models")
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_github_provider())
    sys.exit(0 if success else 1)

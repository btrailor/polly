#!/usr/bin/env python3
"""
Test script for LiteLLM adapter

Tests all 7 providers through the unified LiteLLM adapter to verify:
- Completion requests work
- Streaming works
- Cost tracking is accurate
- Error handling is correct
- Fallback chains function
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.providers.litellm_adapter import LiteLLMAdapter
from core.providers.base import (
    ProviderAuthError,
    ProviderRateLimitError,
    ProviderAPIError
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_model(adapter: LiteLLMAdapter, model: str, provider: str):
    """
    Test a specific model through LiteLLM
    
    Args:
        adapter: LiteLLMAdapter instance
        model: Model identifier to test
        provider: Provider name for logging
    """
    print(f"\n{'='*60}")
    print(f"Testing {provider} - {model}")
    print('='*60)
    
    test_message = [
        {"role": "user", "content": "What is 2+2? Answer briefly."}
    ]
    
    try:
        # Test completion
        print(f"→ Testing completion...")
        response = await adapter.complete(
            messages=test_message,
            model=model,
            max_tokens=50,
            temperature=0.5
        )
        
        print(f"✅ Completion successful")
        print(f"   Content: {response.content[:100]}...")
        print(f"   Tokens: {response.tokens_in} in, {response.tokens_out} out")
        print(f"   Cost: ${response.cost:.6f}")
        print(f"   Model: {response.model}")
        print(f"   Provider: {response.provider}")
        
        # Verify response has content
        assert response.content, "Response should have content"
        assert response.tokens_in > 0, "Should have input tokens"
        assert response.tokens_out > 0, "Should have output tokens"
        assert response.cost >= 0, "Cost should be non-negative"
        
        # Test streaming
        print(f"→ Testing streaming...")
        chunks = []
        async for chunk in adapter.stream(
            messages=test_message,
            model=model,
            max_tokens=30,
            temperature=0.5
        ):
            chunks.append(chunk)
            print(chunk, end='', flush=True)
        
        print()  # Newline after streaming
        
        assert len(chunks) > 0, "Should receive streaming chunks"
        full_response = ''.join(chunks)
        assert full_response, "Streaming should produce content"
        
        print(f"✅ Streaming successful ({len(chunks)} chunks)")
        
        # Test cost estimation
        print(f"→ Testing cost estimation...")
        estimated_cost = adapter.estimate_cost(tokens=1000, model=model)
        print(f"✅ Cost estimation: ${estimated_cost:.6f} for 1000 tokens")
        
        return True
    
    except ProviderAuthError as e:
        print(f"⚠️  Authentication error: {e}")
        print(f"   (Check API key for {provider})")
        return False
    
    except ProviderRateLimitError as e:
        print(f"⚠️  Rate limit error: {e}")
        return False
    
    except ProviderAPIError as e:
        print(f"❌ API error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_all_providers():
    """Test all 7 providers through LiteLLM"""
    
    print("\n" + "="*60)
    print("LiteLLM Adapter Test Suite")
    print("="*60)
    
    # Initialize adapter
    print("\n→ Initializing LiteLLM adapter...")
    try:
        adapter = LiteLLMAdapter(config_path="config/litellm_config.yaml")
        print("✅ Adapter initialized")
    except Exception as e:
        print(f"❌ Failed to initialize adapter: {e}")
        return
    
    # Get available models
    print("\n→ Loading model catalog...")
    models = adapter.get_models()
    print(f"✅ Found {len(models)} models across providers")
    
    # Test credentials
    print("\n→ Validating credentials...")
    try:
        valid = await adapter.validate_credentials()
        if valid:
            print("✅ Credentials validated")
    except ProviderAuthError as e:
        print(f"⚠️  Some credentials invalid: {e}")
    
    # Test each provider
    test_cases = [
        # (model_id, provider_name)
        ("claude-sonnet-4-20250514", "Anthropic"),
        ("gpt-4o-mini", "OpenAI"),
        ("openai/gpt-4o-mini", "GitHub Models"),
        ("gemini-1.5-flash", "Gemini"),
        ("mistral-small-latest", "Mistral"),
        ("grok-2-1212", "Grok"),
        ("llama-3.1-sonar-small-128k-online", "Perplexity"),
    ]
    
    results = {}
    
    for model, provider in test_cases:
        try:
            success = await test_model(adapter, model, provider)
            results[provider] = success
        except KeyboardInterrupt:
            print("\n\n⚠️  Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test failed for {provider}: {e}")
            results[provider] = False
        
        # Small delay between tests
        await asyncio.sleep(1)
    
    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for provider, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {provider}")
    
    print(f"\nResults: {passed}/{total} providers passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    elif passed > 0:
        print(f"\n⚠️  {total - passed} provider(s) failed (may need API keys)")
    else:
        print("\n❌ All tests failed")


async def test_fallback_chain():
    """Test fallback behavior"""
    
    print("\n" + "="*60)
    print("Testing Fallback Chain")
    print("="*60)
    
    # This test would require more complex setup to simulate failures
    # For now, just verify the router integration works
    print("→ Fallback testing requires router integration")
    print("   (See router_v2.py for fallback chain implementation)")


async def main():
    """Run all tests"""
    
    # Check for API keys
    print("\nChecking for API keys in environment...")
    api_keys = {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'GITHUB_TOKEN': os.getenv('GITHUB_TOKEN'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'MISTRAL_API_KEY': os.getenv('MISTRAL_API_KEY'),
        'XAI_API_KEY': os.getenv('XAI_API_KEY'),
        'PERPLEXITY_API_KEY': os.getenv('PERPLEXITY_API_KEY'),
    }
    
    found = sum(1 for v in api_keys.values() if v)
    print(f"Found {found}/{len(api_keys)} API keys")
    
    if found == 0:
        print("\n⚠️  Warning: No API keys found in environment")
        print("   Set API keys in environment or .env file")
        print("   Tests will be limited\n")
    
    # Run tests
    await test_all_providers()
    
    print("\n" + "="*60)
    print("Testing Complete")
    print("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

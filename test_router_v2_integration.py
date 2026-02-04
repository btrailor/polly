#!/usr/bin/env python3
"""
Test script for router_v2 integration in Polly chat
"""

import asyncio
import json
from pathlib import Path

async def test_router_v2():
    """Test that router_v2 works end-to-end"""
    
    print("=" * 60)
    print("Testing Router V2 Integration")
    print("=" * 60)
    
    # Test 1: Import and initialize Polly with router_v2
    print("\n1. Initializing Polly with router_v2...")
    try:
        from core.polly import Polly
        from core.config import PollyConfig
        
        config = PollyConfig()
        
        polly = Polly(config=config)
        print(f"   ✓ Polly initialized")
        print(f"   ✓ Using router v2: {polly.using_router_v2}")
        print(f"   ✓ Default confidence: {polly.default_confidence.value if hasattr(polly, 'default_confidence') else 'N/A'}")
        
        if polly.using_router_v2:
            print(f"   ✓ Router v2 available: {polly.router_v2 is not None}")
            if polly.router_v2:
                print(f"   ✓ Available providers: {list(polly.router_v2.providers.keys())}")
        else:
            print("   ! Router v2 is NOT enabled (check config.yaml)")
            return
            
    except Exception as e:
        print(f"   ✗ Failed to initialize Polly: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Test query method accepts new parameters
    print("\n2. Testing query() method signature...")
    try:
        import inspect
        sig = inspect.signature(polly.query)
        params = list(sig.parameters.keys())
        print(f"   Parameters: {params}")
        
        has_confidence = 'confidence' in params
        has_provider_override = 'provider_override' in params
        
        print(f"   ✓ Has 'confidence' parameter: {has_confidence}")
        print(f"   ✓ Has 'provider_override' parameter: {has_provider_override}")
        
        if not (has_confidence and has_provider_override):
            print("   ✗ Missing router_v2 parameters!")
            return
            
    except Exception as e:
        print(f"   ✗ Failed to inspect query method: {e}")
        return
    
    # Test 3: Test routing decision (without actual API call)
    print("\n3. Testing routing decision...")
    try:
        from core.router_v2 import ConfidenceLevel
        
        # Create a simple test message
        messages = [
            {'role': 'user', 'content': 'What is Python?'}
        ]
        
        # Test different confidence levels
        for confidence in [ConfidenceLevel.FAST, ConfidenceLevel.BALANCED, ConfidenceLevel.THOROUGH]:
            try:
                decision = await polly.router_v2.route(
                    messages=messages,
                    confidence=confidence,
                    max_tokens=100
                )
                print(f"   ✓ {confidence.value}: {decision.provider.name} / {decision.model} (est. ${decision.estimated_cost:.4f})")
            except Exception as e:
                print(f"   ✗ {confidence.value}: {e}")
        
    except Exception as e:
        print(f"   ✗ Failed to test routing: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Test metadata retrieval
    print("\n4. Testing metadata retrieval...")
    try:
        metadata = polly.get_last_response_metadata()
        print(f"   ✓ get_last_response_metadata() exists")
        print(f"   ✓ Current metadata: {metadata}")
    except Exception as e:
        print(f"   ✗ Failed to get metadata: {e}")
    
    print("\n" + "=" * 60)
    print("Router V2 Integration Test Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open Polly Electron app")
    print("2. Send a chat message")
    print("3. Check that tier/provider dropdowns appear")
    print("4. Verify metadata is displayed after response")
    print("5. Try different tiers (Fast/Balanced/Thorough)")
    print("6. Try different providers (Auto/GitHub/OpenAI/Anthropic)")
    print()

if __name__ == "__main__":
    asyncio.run(test_router_v2())

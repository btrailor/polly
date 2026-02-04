#!/usr/bin/env python3
"""
Phase 11a Testing Script
Tests the complete routing system with real API calls
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.router_v2 import IntelligentRouterV2, ConfidenceLevel, TaskType
from core.budget_manager import BudgetManager
from core.secrets_manager import get_secrets_manager


async def test_secrets_management():
    """Test 1: Secrets Manager"""
    print("\n" + "="*60)
    print("TEST 1: SECRETS MANAGER")
    print("="*60)
    
    secrets = get_secrets_manager()
    
    # List current secrets
    secrets_list = secrets.list_secrets()
    print(f"\n✓ Secrets Manager initialized")
    print(f"✓ Storage type: {secrets.storage_type}")
    print(f"\nCurrently configured providers:")
    
    for secret in secrets_list:
        status = "✓ SET" if secret['has_value'] else "✗ NOT SET"
        storage = secret.get('storage_type', 'unknown')
        print(f"  {secret['provider']:12s} {status:10s} (via {storage})")
    
    # Get all provider keys
    keys = secrets.get_all_provider_keys()
    has_anthropic = bool(keys.get('anthropic'))
    has_openai = bool(keys.get('openai'))
    
    print(f"\nAPI Keys Status:")
    print(f"  Anthropic: {'✓ Available' if has_anthropic else '✗ Not configured'}")
    print(f"  OpenAI:    {'✓ Available' if has_openai else '✗ Not configured'}")
    
    if not (has_anthropic or has_openai):
        print("\n⚠️  No API keys configured!")
        print("    Run one of these to add keys:")
        print("    - python3 -m interfaces.cli keys set anthropic")
        print("    - python3 -m interfaces.cli keys set openai")
        print("    - python3 setup_keys.py")
        print("    - Start server and use web UI: python3 -m interfaces.cli serve")
        return False
    
    return True


async def test_budget_manager():
    """Test 2: Budget Manager"""
    print("\n" + "="*60)
    print("TEST 2: BUDGET MANAGER")
    print("="*60)
    
    budget = BudgetManager()
    
    # Get current status
    status = await budget.get_budget_status()
    
    print(f"\n✓ Budget Manager initialized")
    print(f"✓ Database: {budget.db_path}")
    print(f"\nDaily Limit:   ${status['limits']['daily']:.2f}")
    print(f"Daily Spent:   ${status['daily']['spent']:.2f} ({status['daily']['percentage']:.1f}%)")
    print(f"Daily Left:    ${status['daily']['remaining']:.2f}")
    print(f"\nMonthly Limit: ${status['limits']['monthly']:.2f}")
    print(f"Monthly Spent: ${status['monthly']['spent']:.2f} ({status['monthly']['percentage']:.1f}%)")
    print(f"Monthly Left:  ${status['monthly']['remaining']:.2f}")
    
    # Check if we can make requests
    test_cost = 0.05  # $0.05 test request
    can_proceed = await budget.check_budget(test_cost)
    
    if can_proceed:
        print(f"\n✓ Budget check passed for ${test_cost:.2f} request")
    else:
        print(f"\n✗ Budget exceeded! Cannot make ${test_cost:.2f} request")
    
    return can_proceed


async def test_router_initialization():
    """Test 3: Router Initialization"""
    print("\n" + "="*60)
    print("TEST 3: ROUTER INITIALIZATION")
    print("="*60)
    
    secrets = get_secrets_manager()
    keys = secrets.get_all_provider_keys()
    
    try:
        router = IntelligentRouterV2(
            anthropic_api_key=keys.get('anthropic'),
            openai_api_key=keys.get('openai'),
            budget_manager=BudgetManager()
        )
        
        print(f"\n✓ Router initialized successfully")
        print(f"\nProvider Status:")
        
        # Check which providers are available
        providers_status = {}
        if router.anthropic_adapter:
            providers_status['Anthropic'] = '✓ Initialized'
        else:
            providers_status['Anthropic'] = '✗ Not available (no API key)'
        
        if router.openai_adapter:
            providers_status['OpenAI'] = '✓ Initialized'
        else:
            providers_status['OpenAI'] = '✗ Not available (no API key)'
        
        for provider, status in providers_status.items():
            print(f"  {provider:12s} {status}")
        
        return router
        
    except Exception as e:
        print(f"\n✗ Router initialization failed: {e}")
        return None


async def test_routing_decisions(router):
    """Test 4: Routing Decisions"""
    print("\n" + "="*60)
    print("TEST 4: ROUTING DECISIONS")
    print("="*60)
    
    test_queries = [
        ("Write a hello world function", TaskType.CODE_GENERATION, ConfidenceLevel.FAST),
        ("Explain quantum computing in detail", TaskType.RESEARCH, ConfidenceLevel.BALANCED),
        ("Review this complex architecture and provide detailed feedback", TaskType.CODE_REVIEW, ConfidenceLevel.THOROUGH),
    ]
    
    print("\nTesting routing for different query types:\n")
    
    for query, task_type, confidence in test_queries:
        messages = [{"role": "user", "content": query}]
        
        try:
            decision = await router.route(
                messages=messages,
                task_type=task_type,
                confidence=confidence,
                max_tokens=1000
            )
            
            print(f"Query: {query[:50]}...")
            print(f"  Task Type:   {task_type.value}")
            print(f"  Confidence:  {confidence.value}")
            print(f"  → Provider:  {decision.provider}")
            print(f"  → Model:     {decision.model}")
            print(f"  → Tier:      {decision.tier}")
            print(f"  → Est. Cost: ${decision.estimated_cost:.4f}")
            print(f"  → Reason:    {decision.reason}")
            if decision.fallback_chain:
                print(f"  → Fallbacks: {', '.join(decision.fallback_chain)}")
            print()
            
        except Exception as e:
            print(f"✗ Routing failed: {e}\n")


async def test_simple_completion(router):
    """Test 5: Simple API Call"""
    print("\n" + "="*60)
    print("TEST 5: SIMPLE API CALL")
    print("="*60)
    
    print("\nMaking a simple API call to test the complete flow...\n")
    
    messages = [
        {"role": "user", "content": "Say 'Hello from Phase 11a!' and nothing else."}
    ]
    
    try:
        print("Sending request... ", end='', flush=True)
        
        response = await router.complete_with_fallback(
            messages=messages,
            confidence=ConfidenceLevel.FAST,
            max_tokens=50,
            temperature=0.7
        )
        
        print("✓ Response received\n")
        print(f"Provider: {response.provider}")
        print(f"Model:    {response.model}")
        print(f"Tokens:   {response.tokens_used} (in: {response.prompt_tokens}, out: {response.completion_tokens})")
        print(f"Cost:     ${response.cost:.6f}")
        print(f"\nResponse:\n{response.content}\n")
        
        # Check budget tracking
        budget = router.budget_manager
        status = await budget.get_budget_status()
        print(f"Budget after request:")
        print(f"  Daily spent: ${status['daily']['spent']:.4f}")
        print(f"  Requests:    {status['daily']['requests']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed\n")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_provider_stats(router):
    """Test 6: Provider Statistics"""
    print("\n" + "="*60)
    print("TEST 6: PROVIDER STATISTICS")
    print("="*60)
    
    stats = router.get_provider_stats()
    
    print("\nProvider Health:")
    for provider, info in stats.items():
        print(f"\n{provider.upper()}:")
        print(f"  Available:        {info['available']}")
        print(f"  Total requests:   {info['total_requests']}")
        print(f"  Successful:       {info['successful_requests']}")
        print(f"  Failed:           {info['failed_requests']}")
        if info['last_success']:
            print(f"  Last success:     {info['last_success']}")
        if info['last_failure']:
            print(f"  Last failure:     {info['last_failure']}")


async def main():
    """Run all tests"""
    print("="*60)
    print("PHASE 11A TESTING SUITE")
    print("="*60)
    print("\nThis will test:")
    print("  1. Secrets Manager (API key storage)")
    print("  2. Budget Manager (spending tracking)")
    print("  3. Router V2 (intelligent routing)")
    print("  4. Routing decisions (without API calls)")
    print("  5. Simple API call (real request)")
    print("  6. Provider statistics")
    
    input("\nPress Enter to start tests...")
    
    # Test 1: Secrets
    has_keys = await test_secrets_management()
    if not has_keys:
        print("\n" + "="*60)
        print("TESTS SKIPPED - No API keys configured")
        print("="*60)
        print("\nTo continue testing, configure API keys first:")
        print("  python3 -m interfaces.cli keys set anthropic")
        print("  python3 -m interfaces.cli keys set openai")
        return
    
    # Test 2: Budget
    budget_ok = await test_budget_manager()
    if not budget_ok:
        print("\n⚠️  Budget exceeded! Tests will continue but API calls may fail.")
        input("Press Enter to continue anyway...")
    
    # Test 3: Router Init
    router = await test_router_initialization()
    if not router:
        print("\n✗ Cannot continue without router")
        return
    
    # Test 4: Routing Decisions
    await test_routing_decisions(router)
    
    # Test 5: Simple API Call
    print("\n⚠️  The next test will make a REAL API call and incur a small cost (~$0.0001)")
    response = input("Continue? [y/N]: ")
    if response.lower() == 'y':
        success = await test_simple_completion(router)
        
        if success:
            # Test 6: Stats
            await test_provider_stats(router)
    
    # Summary
    print("\n" + "="*60)
    print("TESTING COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("  1. Test web UI:        python3 -m interfaces.cli serve")
    print("                         Open http://localhost:11436/settings")
    print("  2. Test full example:  python3 examples/test_routing_v2.py")
    print("  3. Integrate into CLI: Add routing commands to interfaces/cli.py")


if __name__ == "__main__":
    asyncio.run(main())

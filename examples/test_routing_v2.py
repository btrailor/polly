#!/usr/bin/env python3
"""
Example script demonstrating the Phase 11a multi-provider routing system.

This script shows how to:
1. Initialize the router with multiple providers
2. Use the budget manager to track costs
3. Route requests with different confidence levels
4. Handle fallbacks automatically
5. Check budget status

Usage:
    python examples/test_routing_v2.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.router_v2 import (
    IntelligentRouterV2,
    ConfidenceLevel,
    TaskType
)
from core.budget_manager import BudgetManager


async def main():
    """Demonstrate the routing system."""
    
    print("=" * 60)
    print("Phase 11a: Multi-Provider Intelligent Routing Demo")
    print("=" * 60)
    print()
    
    # Initialize budget manager
    print("1. Initializing Budget Manager...")
    budget_manager = BudgetManager(
        db_path=Path.home() / '.polly' / 'test_usage.db',
        daily_limit=10.0,
        monthly_limit=200.0
    )
    
    # Get budget status
    status = await budget_manager.get_budget_status()
    print(f"   Daily budget: ${status['daily']['spent']:.2f} / ${status['daily']['limit']:.2f}")
    print(f"   Monthly budget: ${status['monthly']['spent']:.2f} / ${status['monthly']['limit']:.2f}")
    print()
    
    # Initialize router
    print("2. Initializing Router with Providers...")
    
    # Get API keys from environment
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not anthropic_key and not openai_key:
        print("   ⚠️  No API keys found in environment!")
        print("   Set ANTHROPIC_API_KEY or OPENAI_API_KEY to test with real providers.")
        print("   Continuing with demo (requests will fail gracefully)...")
        print()
    
    router = IntelligentRouterV2(
        anthropic_api_key=anthropic_key,
        openai_api_key=openai_key,
        budget_manager=budget_manager
    )
    
    # Validate providers
    print("3. Validating Provider Credentials...")
    provider_status = await router.validate_providers()
    for name, is_valid in provider_status.items():
        status_icon = "✓" if is_valid else "✗"
        print(f"   {status_icon} {name}: {'available' if is_valid else 'unavailable'}")
    print()
    
    if not any(provider_status.values()):
        print("⚠️  No providers available. Cannot demonstrate routing.")
        print("   Add API keys to environment variables to test with real providers.")
        return
    
    # Test routing decisions (without making actual API calls)
    print("4. Testing Routing Decisions...")
    print()
    
    test_queries = [
        {
            "query": "What is a Python decorator?",
            "confidence": ConfidenceLevel.FAST,
            "task_type": TaskType.SIMPLE_QUERY,
            "description": "Simple question"
        },
        {
            "query": "Implement a binary search tree with insert, delete, and search methods",
            "confidence": ConfidenceLevel.BALANCED,
            "task_type": TaskType.CODE_GENERATION,
            "description": "Code generation"
        },
        {
            "query": "Review the entire codebase and provide architectural recommendations for scalability",
            "confidence": ConfidenceLevel.THOROUGH,
            "task_type": TaskType.ARCHITECTURAL,
            "description": "Complex architectural task"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"   Query {i}: {test['description']}")
        print(f"   Text: \"{test['query'][:60]}...\"")
        
        messages = [{"role": "user", "content": test["query"]}]
        
        try:
            decision = await router.route(
                messages=messages,
                task_type=test["task_type"],
                confidence=test["confidence"],
                max_tokens=1000
            )
            
            provider_name = router._get_provider_name(decision.provider)
            
            print(f"   → Routed to: {provider_name}/{decision.model}")
            print(f"   → Confidence: {decision.confidence.value}")
            print(f"   → Complexity: {decision.complexity_score}/10")
            print(f"   → Estimated cost: ${decision.estimated_cost:.4f}")
            print(f"   → Fallbacks: {len(decision.fallback_chain)}")
            print()
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            print()
    
    # Example actual completion (commented out to avoid costs)
    print("5. Example Completion (with fallback)")
    print("   Note: Uncomment code to test real API calls")
    print()
    
    """
    # Uncomment to test real API call
    try:
        response = await router.complete_with_fallback(
            messages=[{"role": "user", "content": "What is the capital of France?"}],
            confidence=ConfidenceLevel.FAST,
            max_tokens=50
        )
        
        print(f"   Response: {response.content[:100]}...")
        print(f"   Provider: {response.provider}")
        print(f"   Model: {response.model}")
        print(f"   Tokens: {response.tokens_in} in / {response.tokens_out} out")
        print(f"   Cost: ${response.cost:.4f}")
        print()
    except Exception as e:
        print(f"   Error during completion: {e}")
        print()
    """
    
    # Show provider statistics
    print("6. Provider Statistics")
    stats = router.get_provider_stats()
    for provider, info in stats.items():
        print(f"   {provider}:")
        print(f"     Available: {info['available']}")
        print(f"     Failures: {info['failures']}")
        print(f"     Last success: {info['last_success'] or 'never'}")
        print(f"     Models: {', '.join(info['models'])}")
        print()
    
    # Show budget summary
    print("7. Budget Summary")
    summary = await budget_manager.get_spending_summary()
    print(f"   Total cost: ${summary.total_cost:.2f}")
    print(f"   Total requests: {summary.total_requests}")
    print(f"   Total tokens: {summary.total_tokens_in + summary.total_tokens_out:,}")
    
    if summary.by_provider:
        print("   By provider:")
        for provider, cost in summary.by_provider.items():
            print(f"     {provider}: ${cost:.2f}")
    
    if summary.by_model:
        print("   By model:")
        for model, cost in summary.by_model.items():
            print(f"     {model}: ${cost:.2f}")
    print()
    
    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

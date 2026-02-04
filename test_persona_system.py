#!/usr/bin/env python3
"""
Test script for Persona System (Phase 11c)

This script tests the Architect persona with a simple workflow:
1. Activate Architect persona
2. Process a planning request
3. Switch to build mode
4. Generate content

Usage:
    python test_persona_system.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.personas import PersonaManager, PersonaContext
from core.router_v2 import IntelligentRouterV2
from core.secrets_manager import get_secrets_manager


async def test_persona_system():
    """Test the persona system"""
    
    print("=" * 60)
    print("PERSONA SYSTEM TEST")
    print("=" * 60)
    
    # Initialize router
    print("\n1. Initializing Router v2...")
    secrets = get_secrets_manager()
    anthropic_key = secrets.get_secret('anthropic', fallback_to_env=True)
    openai_key = secrets.get_secret('openai', fallback_to_env=True)
    github_token = secrets.get_secret('github', fallback_to_env=True)
    
    if not anthropic_key and not openai_key and not github_token:
        print("ERROR: No API keys found!")
        print("Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GITHUB_TOKEN environment variable")
        return
    
    router = IntelligentRouterV2(
        anthropic_api_key=anthropic_key,
        openai_api_key=openai_key,
        github_token=github_token
    )
    
    print(f"✓ Router initialized with providers: {list(router.providers.keys())}")
    
    # Initialize PersonaManager
    print("\n2. Initializing PersonaManager...")
    manager = PersonaManager(router)
    print("✓ PersonaManager initialized")
    
    # List available personas
    print("\n3. Available personas:")
    for persona in PersonaManager.list_available_personas():
        print(f"   - {persona['name']}: {persona['available_modes']}")
    
    # Activate Architect persona
    print("\n4. Activating Architect persona...")
    state = manager.activate_persona("architect")
    print(f"✓ Architect activated (mode: {state.current_mode})")
    
    # Test Plan mode
    print("\n5. Testing Plan mode...")
    print("   User: Create a note about Docker best practices")
    
    context = PersonaContext(
        user_message="Create a note about Docker best practices for development",
        conversation_history=[],
        metadata={}
    )
    
    try:
        response = await manager.process(context)
        print(f"\n   Architect (Plan mode) response:")
        print(f"   Mode: {response.mode}")
        print(f"   Actions: {[a.type for a in response.actions]}")
        print(f"\n   Content:")
        print("   " + "-" * 50)
        print(response.content[:500] + "..." if len(response.content) > 500 else response.content)
        print("   " + "-" * 50)
        
        # Show metadata
        if response.metadata.get('model_used'):
            print(f"\n   Model: {response.metadata['model_used']}")
            print(f"   Tokens: {response.metadata.get('tokens_in', 0)} in, {response.metadata.get('tokens_out', 0)} out")
            print(f"   Cost: ${response.metadata.get('cost', 0):.4f}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Switch to Build mode
    print("\n6. Switching to Build mode...")
    state = manager.switch_mode("build")
    print(f"✓ Switched to {state.current_mode} mode")
    
    # Test Build mode
    print("\n7. Testing Build mode...")
    print("   User: Generate the note now")
    
    build_context = PersonaContext(
        user_message="Generate the note based on the plan",
        conversation_history=[
            {"role": "user", "content": context.user_message},
            {"role": "assistant", "content": response.content}
        ],
        metadata={}
    )
    
    try:
        build_response = await manager.process(build_context)
        print(f"\n   Architect (Build mode) response:")
        print(f"   Mode: {build_response.mode}")
        print(f"   Actions: {[a.type for a in build_response.actions]}")
        print(f"\n   Content Preview:")
        print("   " + "-" * 50)
        content_preview = build_response.content[:800]
        print(content_preview + "..." if len(build_response.content) > 800 else build_response.content)
        print("   " + "-" * 50)
        
        # Show metadata
        if build_response.metadata.get('model_used'):
            print(f"\n   Model: {build_response.metadata['model_used']}")
            print(f"   Tokens: {build_response.metadata.get('tokens_in', 0)} in, {build_response.metadata.get('tokens_out', 0)} out")
            print(f"   Cost: ${build_response.metadata.get('cost', 0):.4f}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Deactivate persona
    print("\n8. Deactivating persona...")
    manager.deactivate_persona()
    print("✓ Persona deactivated")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_persona_system())

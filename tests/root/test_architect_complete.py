#!/usr/bin/env python3
"""
Complete Persona Workflow Test

This demonstrates the full Plan → Build workflow with the Architect persona.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.personas import PersonaManager, PersonaContext
from core.router_v2 import IntelligentRouterV2
from core.secrets_manager import get_secrets_manager


async def test_full_workflow():
    """Test complete Plan → Build workflow"""
    
    print("=" * 70)
    print("ARCHITECT PERSONA: COMPLETE WORKFLOW TEST")
    print("=" * 70)
    
    # Initialize
    print("\n📋 Initializing...")
    secrets = get_secrets_manager()
    github_token = secrets.get_secret('github', fallback_to_env=True)
    
    router = IntelligentRouterV2(github_token=github_token)
    manager = PersonaManager(router)
    
    # Activate Architect
    print("\n🏗️  Activating Architect persona...")
    manager.activate_persona("architect")
    print("   Mode:", manager.get_current_mode())
    
    # Step 1: Plan Mode - Initial Request
    print("\n" + "=" * 70)
    print("STEP 1: PLAN MODE - Analyze Request")
    print("=" * 70)
    print("\n💬 User: Create a note about Docker best practices for Python developers")
    
    context1 = PersonaContext(
        user_message="Create a note about Docker best practices for Python developers",
        conversation_history=[]
    )
    
    response1 = await manager.process(context1)
    
    print(f"\n🤖 Architect (Plan Mode):")
    print(response1.content)
    print(f"\n📊 Model: {response1.metadata.get('model_used')}")
    print(f"   Tokens: {response1.metadata.get('tokens_in')} in, {response1.metadata.get('tokens_out')} out")
    print(f"   Cost: ${response1.metadata.get('cost', 0):.4f}")
    
    # Step 2: Answer Questions
    print("\n" + "=" * 70)
    print("STEP 2: ANSWER QUESTIONS")
    print("=" * 70)
    print("\n💬 User provides answers:")
    
    answers = """
1. Focus on intermediate level - developers who know Python but are new to Docker
2. Emphasize container building, multi-stage builds, and dependency management
3. Include practical examples with Dockerfile snippets
4. Around 500-800 words with code examples
"""
    print(answers)
    
    # Process answers in Plan mode (to update the plan)
    context2 = PersonaContext(
        user_message=answers,
        conversation_history=[
            {"role": "user", "content": context1.user_message},
            {"role": "assistant", "content": response1.content}
        ]
    )
    
    # Step 3: Switch to Build Mode
    print("\n" + "=" * 70)
    print("STEP 3: SWITCH TO BUILD MODE")
    print("=" * 70)
    manager.switch_mode("build")
    print("\n✓ Switched to Build mode")
    print("   Current mode:", manager.get_current_mode())
    
    # Step 4: Build - Generate Content
    print("\n" + "=" * 70)
    print("STEP 4: BUILD MODE - Generate Content")
    print("=" * 70)
    print("\n💬 User: Generate the Docker best practices note")
    
    context3 = PersonaContext(
        user_message=f"I've answered your questions:\n{answers}\n\nNow generate the complete note.",
        conversation_history=[
            {"role": "user", "content": context1.user_message},
            {"role": "assistant", "content": response1.content},
            {"role": "user", "content": answers}
        ]
    )
    
    response3 = await manager.process(context3)
    
    print(f"\n🤖 Architect (Build Mode):")
    print("\n" + "-" * 70)
    print(response3.content[:1500] + "\n..." if len(response3.content) > 1500 else response3.content)
    print("-" * 70)
    
    print(f"\n📊 Model: {response3.metadata.get('model_used')}")
    print(f"   Tokens: {response3.metadata.get('tokens_in')} in, {response3.metadata.get('tokens_out')} out")
    print(f"   Cost: ${response3.metadata.get('cost', 0):.4f}")
    
    # Show actions
    if response3.actions:
        print(f"\n🎬 UI Actions: {[a.type for a in response3.actions]}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 70)
    
    # Get final state
    state = manager.get_state()
    print(f"\nPersona: {state.persona_name}")
    print(f"Final Mode: {state.current_mode}")
    print(f"Mode Switches: {len(state.mode_history)}")
    
    if state.mode_history:
        print("\nMode History:")
        for switch in state.mode_history:
            print(f"  • {switch['from']} → {switch['to']}")
    
    # Deactivate
    manager.deactivate_persona()
    print("\n✓ Persona deactivated")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())

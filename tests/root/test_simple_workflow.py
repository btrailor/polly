#!/usr/bin/env python3
"""
Simple end-to-end test: Request → Plan → Build → Content
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.personas import PersonaManager, PersonaContext
from core.router_v2 import IntelligentRouterV2
from core.secrets_manager import get_secrets_manager


async def test_simple_workflow():
    """Test simple workflow with a request that doesn't need questions"""
    
    print("=" * 70)
    print("SIMPLE WORKFLOW: Request with Full Context")
    print("=" * 70)
    
    # Initialize
    secrets = get_secrets_manager()
    github_token = secrets.get_secret('github', fallback_to_env=True)
    router = IntelligentRouterV2(github_token=github_token)
    manager = PersonaManager(router)
    
    # Activate
    print("\n🏗️  Activating Architect...")
    manager.activate_persona("architect")
    
    # Step 1: Detailed request in Plan mode
    print("\n" + "=" * 70)
    print("STEP 1: PLAN MODE")
    print("=" * 70)
    
    detailed_request = """Create a note about Docker multi-stage builds for Python applications.

The note should:
- Be aimed at intermediate Python developers
- Include practical Dockerfile examples
- Cover multi-stage builds to reduce image size
- Show how to handle Python dependencies efficiently
- Be around 500 words with code examples"""
    
    print(f"\n💬 User:\n{detailed_request}")
    
    context1 = PersonaContext(user_message=detailed_request)
    response1 = await manager.process(context1)
    
    print(f"\n🤖 Architect (Plan):")
    print(response1.content)
    print(f"\n📊 {response1.metadata.get('model_used')} | "
          f"Tokens: {response1.metadata.get('tokens_in')}/{response1.metadata.get('tokens_out')} | "
          f"${response1.metadata.get('cost', 0):.4f}")
    
    # Step 2: Switch to Build
    print("\n" + "=" * 70)
    print("STEP 2: SWITCH TO BUILD MODE")
    print("=" * 70)
    manager.switch_mode("build")
    print("✓ Switched to build mode")
    
    # Step 3: Generate content
    print("\n" + "=" * 70)
    print("STEP 3: BUILD MODE - Generate Content")
    print("=" * 70)
    print("\n💬 User: Generate the complete note now")
    
    context2 = PersonaContext(
        user_message="Generate the complete note based on the plan",
        conversation_history=[
            {"role": "user", "content": detailed_request},
            {"role": "assistant", "content": response1.content}
        ]
    )
    
    response2 = await manager.process(context2)
    
    print(f"\n🤖 Architect (Build) - Generated Content:")
    print("\n" + "=" * 70)
    print(response2.content)
    print("=" * 70)
    
    print(f"\n📊 {response2.metadata.get('model_used')} | "
          f"Tokens: {response2.metadata.get('tokens_in')}/{response2.metadata.get('tokens_out')} | "
          f"${response2.metadata.get('cost', 0):.4f}")
    
    # Show generated content metadata
    if 'generated_content' in response2.metadata:
        gen_content = response2.metadata['generated_content']
        print(f"\n📝 Generated: {gen_content.get('format')} format")
        print(f"   Length: {len(gen_content.get('content', ''))} characters")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ SUCCESS - Full workflow completed!")
    print("=" * 70)
    
    state = manager.get_state()
    print(f"\n📊 Final Stats:")
    print(f"   Persona: {state.persona_name}")
    print(f"   Mode switches: {len(state.mode_history)}")
    print(f"   Total cost: ${response1.metadata.get('cost', 0) + response2.metadata.get('cost', 0):.4f}")
    
    manager.deactivate_persona()


if __name__ == "__main__":
    asyncio.run(test_simple_workflow())

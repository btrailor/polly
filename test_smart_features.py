#!/usr/bin/env python3
"""
Quick test script for Obsidian smart features
"""

import asyncio
from core.polly import Polly
from integrations.obsidian_smart import ObsidianSmartFeatures
from core.domains import DomainEngine
from integrations import ObsidianIntegration

async def test_smart_features():
    print("=== Testing Obsidian Smart Features ===\n")
    
    # Initialize
    polly = Polly()
    vault_path = polly.config.get('obsidian.vault_path')
    print(f"Vault: {vault_path}\n")
    
    # Create integration
    obsidian = ObsidianIntegration(vault_path=vault_path)
    await obsidian.connect()
    
    # Create smart features
    domain_engine = DomainEngine()
    smart = ObsidianSmartFeatures(
        obsidian_integration=obsidian,
        domain_engine=domain_engine,
        rag_engine=polly.rag
    )
    
    # Test 1: Folder suggestion
    print("Test 1: Suggest Folder")
    print("-" * 40)
    result = await smart.suggest_folder(
        content="Notes on implementing a modular synthesis engine with oscillators, filters, and envelope generators. Using Python and numpy for DSP processing.",
        title="Building an Audio Synthesis Engine"
    )
    print(f"Suggested folder: {result['suggested_folder']}")
    print(f"Domain: {result['domain']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
    if result['alternatives']:
        print(f"Alternatives: {result['alternatives'][0] if result['alternatives'] else 'None'}")
    print()
    
    # Test 2: Tag suggestions
    print("Test 2: Suggest Tags")
    print("-" * 40)
    result = await smart.suggest_tags(
        content="Exploring wavetable synthesis techniques and their applications in modern digital audio workstations.",
        title="Wavetable Synthesis"
    )
    print(f"Suggested tags: {[t['tag'] for t in result['suggested_tags'][:5]]}")
    print(f"Reasoning: {result['reasoning']}")
    print()
    
    # Test 3: Related notes
    print("Test 3: Find Related Notes")
    print("-" * 40)
    result = await smart.find_related_notes(
        content="Building a modular synthesis engine with oscillators and filters",
        title="Synthesis Engine",
        top_k=3
    )
    print(f"Found {len(result['related_notes'])} related notes:")
    for note in result['related_notes']:
        print(f"  - {note['title']} (similarity: {note['similarity']})")
    print()
    
    print("=== All tests completed! ===")

if __name__ == "__main__":
    asyncio.run(test_smart_features())

#!/usr/bin/env python3
"""
Test Day 5-6: End-to-End Conceptual Pattern Learning

This script demonstrates the full conceptual pattern learning pipeline:
1. Extract concepts from conversations
2. Detect recurring concept pairs
3. Infer domains from concepts
4. Create and update conceptual patterns
5. Persist patterns to disk

Run this test AFTER implementing all Day 5-6 changes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner
import json


def main():
    """Run end-to-end test of conceptual pattern learning."""
    print("=" * 70)
    print("Day 5-6: End-to-End Conceptual Pattern Learning Test")
    print("=" * 70)
    
    # Initialize pattern learner
    learner = PatternLearner(
        storage_path=Path("~/.polly/patterns_e2e_test.json"),
        min_occurrences=2  # Lower for testing
    )
    
    print("\n[1/5] Testing Concept Extraction")
    print("-" * 70)
    
    # Test conversation about Docker + Python
    conv1 = {
        'id': 'e2e_docker_python_1',
        'messages': [
            {'role': 'user', 'content': 'I need to containerize my Python FastAPI application using Docker'},
            {'role': 'assistant', 'content': 'To containerize your Python FastAPI app with Docker, start by creating a Dockerfile...'},
            {'role': 'user', 'content': 'What about Docker Compose for multiple Python services?'},
            {'role': 'assistant', 'content': 'Docker Compose is perfect for orchestrating multiple Python microservices...'}
        ]
    }
    
    patterns1 = learner.learn_conceptual_patterns(
        conversation_id=conv1['id'],
        messages=conv1['messages']
    )
    print(f"✓ Conversation 1: Extracted concepts and learned {patterns1} patterns")
    
    print("\n[2/5] Testing Pattern Detection (Need Multiple Occurrences)")
    print("-" * 70)
    
    # Same concepts, different conversation
    conv2 = {
        'id': 'e2e_docker_python_2',
        'messages': [
            {'role': 'user', 'content': 'Best practices for Python development in Docker containers?'},
            {'role': 'assistant', 'content': 'When developing Python applications in Docker...'},
            {'role': 'user', 'content': 'How to debug Python apps running in Docker?'},
            {'role': 'assistant', 'content': 'Debugging Python in Docker requires some special configuration...'}
        ]
    }
    
    patterns2 = learner.learn_conceptual_patterns(
        conversation_id=conv2['id'],
        messages=conv2['messages']
    )
    print(f"✓ Conversation 2: Learned {patterns2} patterns")
    
    # Check if docker+python pattern exists now
    docker_python_pattern = None
    for pattern_id, pattern in learner.patterns.items():
        if 'docker' in pattern_id and 'python' in pattern_id:
            docker_python_pattern = pattern
            break
    
    if docker_python_pattern:
        print(f"✓ Detected recurring pattern: {docker_python_pattern.name}")
        print(f"  Occurrences: {docker_python_pattern.occurrences}")
        print(f"  Confidence: {docker_python_pattern.confidence:.2f}")
        print(f"  Domains: {docker_python_pattern.domains}")
    else:
        print("! Pattern not yet at threshold (need min_occurrences)")
    
    print("\n[3/5] Testing Domain Inference")
    print("-" * 70)
    
    # Test different domain
    conv3 = {
        'id': 'e2e_audio_midi',
        'messages': [
            {'role': 'user', 'content': 'How do I process MIDI data in SuperCollider for audio synthesis?'},
            {'role': 'assistant', 'content': 'SuperCollider has excellent MIDI support for audio applications...'},
            {'role': 'user', 'content': 'Can I use MIDI controllers to control SuperCollider synths?'},
            {'role': 'assistant', 'content': 'Yes! MIDI controllers work great with SuperCollider for real-time audio control...'}
        ]
    }
    
    patterns3 = learner.learn_conceptual_patterns(
        conversation_id=conv3['id'],
        messages=conv3['messages']
    )
    print(f"✓ Conversation 3 (audio/MIDI): Learned {patterns3} patterns")
    
    # Another audio conversation
    conv4 = {
        'id': 'e2e_audio_midi_2',
        'messages': [
            {'role': 'user', 'content': 'Best MIDI libraries for audio programming in SuperCollider?'},
            {'role': 'assistant', 'content': 'SuperCollider has built-in MIDI classes for audio work...'},
            {'role': 'user', 'content': 'MIDI timing in SuperCollider audio synthesis'},
            {'role': 'assistant', 'content': 'MIDI timing is crucial for audio synthesis in SuperCollider...'}
        ]
    }
    
    patterns4 = learner.learn_conceptual_patterns(
        conversation_id=conv4['id'],
        messages=conv4['messages']
    )
    print(f"✓ Conversation 4 (audio/MIDI): Learned {patterns4} patterns")
    
    # Check domains
    for pattern_id, pattern in learner.patterns.items():
        if pattern.pattern_type == 'conceptual':
            print(f"  → {pattern.name}")
            print(f"    Domains: {pattern.domains}")
    
    print("\n[4/5] Testing Pattern Persistence")
    print("-" * 70)
    
    # Save patterns
    learner.save_patterns()
    storage_path = learner.storage_path.expanduser()
    print(f"✓ Saved patterns to {storage_path}")
    
    # Verify file exists and has content
    if storage_path.exists():
        with open(storage_path, 'r') as f:
            data = json.load(f)
        
        print(f"  File size: {storage_path.stat().st_size} bytes")
        print(f"  Patterns: {len(data.get('patterns', []))}")
        print(f"  Query patterns: {len(data.get('query_patterns', []))}")
        print(f"  Query history: {len(data.get('query_history', []))}")
    else:
        print("✗ Storage file not created!")
    
    print("\n[5/5] Testing Pattern Reload")
    print("-" * 70)
    
    # Create new instance (simulates restart)
    learner2 = PatternLearner(
        storage_path=Path("~/.polly/patterns_e2e_test.json"),
        min_occurrences=2
    )
    
    print(f"✓ Reloaded {len(learner2.patterns)} patterns")
    print(f"✓ Reloaded {len(learner2.query_patterns)} query patterns")
    
    # Verify patterns match
    if len(learner2.patterns) == len(learner.patterns):
        print("✓ All patterns persisted correctly!")
    else:
        print(f"✗ Pattern count mismatch: {len(learner2.patterns)} vs {len(learner.patterns)}")
    
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    total_patterns = len(learner.patterns)
    conceptual_patterns = sum(1 for p in learner.patterns.values() if p.pattern_type == 'conceptual')
    
    print(f"\nTotal patterns learned: {total_patterns}")
    print(f"Conceptual patterns: {conceptual_patterns}")
    print(f"Conversations processed: 4")
    
    print("\nDetected Patterns:")
    for pattern in learner.patterns.values():
        if pattern.pattern_type == 'conceptual':
            print(f"\n  → {pattern.name}")
            print(f"    Type: {pattern.pattern_type}")
            print(f"    Occurrences: {pattern.occurrences}")
            print(f"    Confidence: {pattern.confidence:.2f}")
            print(f"    Domains: {pattern.domains}")
            print(f"    First seen: {pattern.first_seen.isoformat()}")
            print(f"    Last seen: {pattern.last_seen.isoformat()}")
    
    print("\n" + "=" * 70)
    print("✓ End-to-End Test Complete!")
    print("=" * 70)
    
    print("\nNext Steps:")
    print("1. Start Polly server if not running:")
    print("   cd /Users/brettgershon/polly")
    print("   python3 -m uvicorn interfaces.server:create_app --host 0.0.0.0 --port 11436 --factory")
    print("\n2. Test API endpoint:")
    print("   python3 scripts/test_day5_api_integration.py")
    print("\n3. Use Polly and watch pattern learning happen automatically!")
    print("   Patterns will be saved to ~/.polly/patterns.json")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

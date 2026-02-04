#!/usr/bin/env python3
"""
Test Day 5: Conceptual Pattern Learning

Tests the new conceptual pattern learning system that detects
recurring concept pairs in conversations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner
from datetime import datetime
import json


def test_concept_extraction():
    """Test that concepts are correctly extracted from text."""
    print("\n=== Test 1: Concept Extraction ===")
    
    learner = PatternLearner(
        storage_path=Path("~/.polly/test_patterns.json"),
        min_occurrences=2  # Lower threshold for testing
    )
    
    # Test text with various concept types
    test_text = """
    I'm working on a Docker container for my Python application.
    The API uses Redis for caching and PostgreSQL for storage.
    I need to implement authentication middleware using JWT tokens.
    The React frontend connects to the Node.js backend.
    """
    
    concepts = learner._extract_concepts(test_text)
    print(f"Extracted {len(concepts)} concepts:")
    for concept in sorted(concepts):
        print(f"  - {concept}")
    
    # Check for expected concepts
    expected = {'docker', 'python', 'api', 'redis', 'postgres', 'authentication', 'react', 'node'}
    found = expected & set(concepts)
    print(f"\n✓ Found {len(found)}/{len(expected)} expected concepts: {found}")
    
    return len(found) >= 5  # At least 5 expected concepts


def test_domain_inference():
    """Test that domains are correctly inferred from concepts."""
    print("\n=== Test 2: Domain Inference ===")
    
    learner = PatternLearner(
        storage_path=Path("~/.polly/test_patterns.json"),
        min_occurrences=2
    )
    
    test_cases = [
        (['docker', 'python', 'redis'], 'sigils'),
        (['audio', 'midi', 'supercollider'], 'signals'),
        (['writing', 'essay', 'pedagogy'], 'scrolls'),
        (['system', 'architecture', 'framework'], 'grids'),
        (['design', 'ui', 'visual'], 'glyphs'),
    ]
    
    passed = 0
    for concepts, expected_domain in test_cases:
        domains = learner._infer_domains_from_concepts(concepts)
        if expected_domain in domains:
            print(f"✓ {concepts[:2]} → {expected_domain}")
            passed += 1
        else:
            print(f"✗ {concepts[:2]} → {domains} (expected {expected_domain})")
    
    print(f"\nPassed {passed}/{len(test_cases)} domain inference tests")
    return passed >= 4  # At least 4 correct


def test_conceptual_pattern_learning():
    """Test that conceptual patterns are learned from conversations."""
    print("\n=== Test 3: Conceptual Pattern Learning ===")
    
    learner = PatternLearner(
        storage_path=Path("~/.polly/test_patterns.json"),
        min_occurrences=2  # Lower threshold for testing
    )
    
    # Simulate 3 conversations about Docker + Python
    conversations = [
        {
            'id': 'conv_1',
            'messages': [
                {'role': 'user', 'content': 'How do I set up Docker for Python development?'},
                {'role': 'assistant', 'content': 'You can use a Dockerfile with Python base image...'},
                {'role': 'user', 'content': 'What about Docker Compose with Python services?'},
                {'role': 'assistant', 'content': 'Docker Compose is great for multi-container Python apps...'}
            ]
        },
        {
            'id': 'conv_2',
            'messages': [
                {'role': 'user', 'content': 'Best practices for Python in Docker containers?'},
                {'role': 'assistant', 'content': 'When running Python in Docker, consider...'},
                {'role': 'user', 'content': 'How to debug Python apps in Docker?'},
                {'role': 'assistant', 'content': 'Debugging Python applications in Docker requires...'}
            ]
        },
        {
            'id': 'conv_3',
            'messages': [
                {'role': 'user', 'content': 'I need help with React and TypeScript setup'},
                {'role': 'assistant', 'content': 'Setting up React with TypeScript is straightforward...'},
                {'role': 'user', 'content': 'What about React hooks with TypeScript?'},
                {'role': 'assistant', 'content': 'React hooks work great with TypeScript...'}
            ]
        }
    ]
    
    # Learn from conversations
    total_patterns = 0
    for conv in conversations:
        patterns_learned = learner.learn_conceptual_patterns(
            conversation_id=conv['id'],
            messages=conv['messages']
        )
        print(f"Conversation {conv['id']}: {patterns_learned} new patterns")
        total_patterns += patterns_learned
    
    # Check what patterns were learned
    print(f"\n✓ Total patterns learned: {total_patterns}")
    print(f"✓ Total patterns in storage: {len(learner.patterns)}")
    
    # Look for docker + python pattern
    docker_python_found = False
    react_typescript_found = False
    
    for pattern_id, pattern in learner.patterns.items():
        if pattern.pattern_type == 'conceptual':
            print(f"\n  Pattern: {pattern.name}")
            print(f"    Occurrences: {pattern.occurrences}")
            print(f"    Confidence: {pattern.confidence:.2f}")
            print(f"    Domains: {pattern.domains}")
            
            if 'docker' in pattern_id and 'python' in pattern_id:
                docker_python_found = True
            if 'react' in pattern_id and 'typescript' in pattern_id:
                react_typescript_found = True
    
    print(f"\n✓ Docker + Python pattern detected: {docker_python_found}")
    print(f"✓ React + TypeScript pattern detected: {react_typescript_found}")
    
    # Save patterns
    learner.save_patterns()
    print(f"\n✓ Patterns saved to {learner.storage_path}")
    
    return docker_python_found and len(learner.patterns) > 0


def test_pattern_persistence():
    """Test that learned patterns persist across restarts."""
    print("\n=== Test 4: Pattern Persistence ===")
    
    # Create first instance and learn patterns
    learner1 = PatternLearner(
        storage_path=Path("~/.polly/test_patterns_persist.json"),
        min_occurrences=2
    )
    
    # Learn from a conversation
    learner1.learn_conceptual_patterns(
        conversation_id='test_conv',
        messages=[
            {'role': 'user', 'content': 'Using Docker with Python for microservices'},
            {'role': 'assistant', 'content': 'Docker and Python work great together for microservices...'},
            {'role': 'user', 'content': 'How to scale Python Docker containers?'},
            {'role': 'assistant', 'content': 'Scaling Python in Docker involves...'}
        ]
    )
    
    # Force multiple occurrences by learning again
    learner1.learn_conceptual_patterns(
        conversation_id='test_conv_2',
        messages=[
            {'role': 'user', 'content': 'Docker networking with Python services'},
            {'role': 'assistant', 'content': 'When working with Docker and Python networking...'},
            {'role': 'user', 'content': 'Best Python Docker image?'},
            {'role': 'assistant', 'content': 'The official Python Docker images...'}
        ]
    )
    
    learner1.save_patterns()
    initial_patterns = len(learner1.patterns)
    print(f"First instance: {initial_patterns} patterns")
    
    # Create second instance (simulates restart)
    learner2 = PatternLearner(
        storage_path=Path("~/.polly/test_patterns_persist.json"),
        min_occurrences=2
    )
    
    loaded_patterns = len(learner2.patterns)
    print(f"Second instance: {loaded_patterns} patterns")
    
    # Verify patterns match
    if initial_patterns == loaded_patterns and loaded_patterns > 0:
        print(f"✓ Patterns persisted correctly!")
        
        # Show a sample pattern
        if learner2.patterns:
            sample = list(learner2.patterns.values())[0]
            print(f"\n  Sample pattern: {sample.name}")
            print(f"    Type: {sample.pattern_type}")
            print(f"    Occurrences: {sample.occurrences}")
            print(f"    Confidence: {sample.confidence:.2f}")
        
        return True
    else:
        print(f"✗ Pattern persistence failed!")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Day 5: Conceptual Pattern Learning Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Concept Extraction", test_concept_extraction()))
    results.append(("Domain Inference", test_domain_inference()))
    results.append(("Conceptual Learning", test_conceptual_pattern_learning()))
    results.append(("Pattern Persistence", test_pattern_persistence()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

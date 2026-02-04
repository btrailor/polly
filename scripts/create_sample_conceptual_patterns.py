#!/usr/bin/env python3
"""
Create Sample Conceptual Patterns

This script creates sample conceptual patterns by simulating conversations.
Run this to see conceptual patterns appear in your Patterns page!
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner


def create_sample_patterns():
    """Create sample conceptual patterns for demonstration."""
    print("=" * 70)
    print("Creating Sample Conceptual Patterns")
    print("=" * 70)
    
    # Initialize pattern learner
    learner = PatternLearner(
        storage_path=Path("~/.polly/patterns.json"),
        min_occurrences=3  # Need 3 occurrences to create pattern
    )
    
    print("\nInitial state:")
    print(f"  Conceptual patterns: {len([p for p in learner.patterns.values() if p.pattern_type == 'conceptual'])}")
    print(f"  Query patterns: {len(learner.query_patterns)}")
    
    # Simulate 3 conversations about Docker + Python
    conversations = [
        {
            'id': 'sample_conv_1',
            'messages': [
                {'role': 'user', 'content': 'I want to containerize my Python application using Docker'},
                {'role': 'assistant', 'content': 'Great! Docker is perfect for Python applications. Let me help you create a Dockerfile...'},
                {'role': 'user', 'content': 'What base image should I use for Python in Docker?'},
                {'role': 'assistant', 'content': 'For Python in Docker, I recommend the official python:3.11-slim image...'}
            ]
        },
        {
            'id': 'sample_conv_2',
            'messages': [
                {'role': 'user', 'content': 'How do I manage environment variables for Python apps in Docker containers?'},
                {'role': 'assistant', 'content': 'For Python applications in Docker, you have several options for environment variables...'},
                {'role': 'user', 'content': 'Can I use a .env file with Docker and Python?'},
                {'role': 'assistant', 'content': 'Yes! You can use python-dotenv with Docker containers...'}
            ]
        },
        {
            'id': 'sample_conv_3',
            'messages': [
                {'role': 'user', 'content': 'Best practices for Python Docker deployments?'},
                {'role': 'assistant', 'content': 'When deploying Python applications with Docker, consider these best practices...'},
                {'role': 'user', 'content': 'How do I optimize Python Docker image size?'},
                {'role': 'assistant', 'content': 'To optimize Python Docker images, use multi-stage builds...'}
            ]
        }
    ]
    
    print("\n" + "=" * 70)
    print("Learning from conversations...")
    print("=" * 70)
    
    patterns_created = 0
    for i, conv in enumerate(conversations, 1):
        print(f"\nConversation {i}: {conv['id']}")
        new_patterns = learner.learn_conceptual_patterns(
            conversation_id=conv['id'],
            messages=conv['messages']
        )
        patterns_created += new_patterns
        print(f"  → {new_patterns} new patterns created")
        
        # Show current count
        conceptual = len([p for p in learner.patterns.values() if p.pattern_type == 'conceptual'])
        print(f"  → Total conceptual patterns: {conceptual}")
    
    # Save patterns
    learner.save_patterns()
    print(f"\n✓ Patterns saved to {learner.storage_path.expanduser()}")
    
    print("\n" + "=" * 70)
    print("Final State")
    print("=" * 70)
    
    conceptual = [p for p in learner.patterns.values() if p.pattern_type == 'conceptual']
    print(f"\nTotal conceptual patterns: {len(conceptual)}")
    print(f"Total query patterns: {len(learner.query_patterns)}")
    print(f"Total: {len(conceptual) + len(learner.query_patterns)}")
    
    if conceptual:
        print("\n" + "=" * 70)
        print("Conceptual Patterns Created")
        print("=" * 70)
        
        for pattern in conceptual:
            print(f"\n  → {pattern.name}")
            print(f"    Description: {pattern.description}")
            print(f"    Occurrences: {pattern.occurrences}")
            print(f"    Confidence: {pattern.confidence:.0%}")
            print(f"    Domains: {', '.join(pattern.domains)}")
    
    print("\n" + "=" * 70)
    print("✨ Success!")
    print("=" * 70)
    print("\nNow open the Polly Electron app:")
    print("  1. Go to Dashboard → Should show increased pattern count")
    print("  2. Go to Patterns → Should see conceptual patterns!")
    print("\nPatterns created:")
    print(f"  • docker ↔ python (appears {3} times)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    create_sample_patterns()

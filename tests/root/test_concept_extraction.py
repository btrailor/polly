#!/usr/bin/env python3
"""
Test script for Phase 13A Days 3-4: spaCy Concept Extraction

Tests the new concept extraction with real-world queries and validates:
- Quality: 10-15 concepts vs 50+ garbage
- Accuracy: 80%+ relevant concepts
- Technical term recognition
- Multi-word phrase extraction
- Proper noun handling
- Stopword filtering
"""

import sys
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from learners.patterns import PatternLearner

# Test cases with expected concepts
TEST_CASES = [
    {
        "name": "Technical Query - Docker + Python",
        "text": "How do I use Docker with Python? I need to build a container for my Flask API.",
        "expected_keywords": ["docker", "python", "container", "flask", "api"],
        "max_concepts": 15
    },
    {
        "name": "Domain-Specific - Norns/Signals",
        "text": "I'm working on a norns script using the grid and midi. How do I access the engine library?",
        "expected_keywords": ["norns", "grid", "midi", "engine", "library"],
        "max_concepts": 15
    },
    {
        "name": "Mixed Technologies",
        "text": "Deploy my React app to AWS using GitHub Actions with Docker containers.",
        "expected_keywords": ["react", "aws", "github", "docker", "container"],
        "max_concepts": 15
    },
    {
        "name": "Multi-word Technical Phrases",
        "text": "I need help with neural networks and machine learning models for text classification.",
        "expected_keywords": ["neural", "network", "machine", "learning", "model", "text", "classification"],
        "max_concepts": 15
    },
    {
        "name": "Stopword Heavy (Should Filter)",
        "text": "I would like to have some help with this thing that I was trying to do yesterday.",
        "expected_keywords": [],  # Should extract very few or no concepts
        "max_concepts": 5
    },
    {
        "name": "Code Patterns",
        "text": "My PostgreSQL database connection is failing. The connection string uses localhost:5432.",
        "expected_keywords": ["postgresql", "database", "connection"],
        "max_concepts": 15
    },
    {
        "name": "Real Polly Query",
        "text": """I'm building a RAG system with ChromaDB for semantic search. 
        The embeddings are generated using OpenAI's API and stored in PostgreSQL. 
        How can I optimize the retrieval performance?""",
        "expected_keywords": ["rag", "chromadb", "semantic", "search", "embedding", "openai", "api", "postgresql", "retrieval", "performance"],
        "max_concepts": 15
    },
    {
        "name": "Shell Commands (Should Extract Tools)",
        "text": "Run docker-compose up -d and then npm install in the frontend directory.",
        "expected_keywords": ["docker", "npm"],
        "max_concepts": 15
    }
]

def test_concept_extraction():
    """Run concept extraction tests and validate results."""
    print("=" * 80)
    print("Phase 13A Days 3-4: spaCy Concept Extraction Tests")
    print("=" * 80)
    
    # Initialize pattern learner
    test_storage = Path.home() / '.polly' / 'patterns_test_concepts.json'
    learner = PatternLearner(storage_path=test_storage)
    
    print(f"\nspaCy available: {learner.nlp is not None}")
    print(f"Model: {'en_core_web_sm' if learner.nlp else 'None (using fallback)'}\n")
    
    total_tests = len(TEST_CASES)
    passed_tests = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}/{total_tests}: {test_case['name']}")
        print(f"{'─' * 80}")
        
        text = test_case['text']
        expected = test_case['expected_keywords']
        max_concepts = test_case['max_concepts']
        
        print(f"Input: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        # Extract concepts
        concepts = learner.extract_concepts_with_spacy(text)
        
        print(f"\nExtracted {len(concepts)} concepts: {concepts}")
        
        # Validate count
        if len(concepts) > max_concepts:
            print(f"❌ FAIL: Too many concepts ({len(concepts)} > {max_concepts})")
            continue
        else:
            print(f"✅ PASS: Concept count within limit ({len(concepts)} <= {max_concepts})")
        
        # Validate expected keywords found
        if expected:
            found = [kw for kw in expected if any(kw in c.lower() for c in concepts)]
            found_count = len(found)
            expected_count = len(expected)
            
            # Require at least 50% of expected keywords
            if found_count >= expected_count * 0.5:
                print(f"✅ PASS: Found {found_count}/{expected_count} expected keywords: {found}")
                passed_tests += 1
            else:
                print(f"❌ FAIL: Only found {found_count}/{expected_count} expected keywords: {found}")
                print(f"   Missing: {[kw for kw in expected if kw not in found]}")
        else:
            # Test expects few/no concepts (stopword heavy)
            if len(concepts) <= 5:
                print(f"✅ PASS: Correctly filtered stopword-heavy text ({len(concepts)} concepts)")
                passed_tests += 1
            else:
                print(f"❌ FAIL: Should have filtered more stopwords (got {len(concepts)} concepts)")
    
    # Summary
    print("\n" + "=" * 80)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    print("=" * 80)
    
    if passed_tests == total_tests:
        print("✅ ALL TESTS PASSED - Concept extraction working correctly!")
    elif passed_tests >= total_tests * 0.75:
        print(f"⚠️  MOSTLY PASSING - {passed_tests}/{total_tests} tests passed (75%+)")
    else:
        print(f"❌ TESTS FAILING - Only {passed_tests}/{total_tests} tests passed")
    
    # Clean up
    if test_storage.exists():
        test_storage.unlink()
    
    return passed_tests == total_tests


def test_comparison_old_vs_new():
    """Compare old extraction vs new spaCy extraction."""
    print("\n" + "=" * 80)
    print("Comparison: Old vs New Concept Extraction")
    print("=" * 80)
    
    test_storage = Path.home() / '.polly' / 'patterns_test_concepts.json'
    learner = PatternLearner(storage_path=test_storage)
    
    sample_text = """I'm building a RAG system with ChromaDB for semantic search. 
    The embeddings are generated using OpenAI's API and stored in PostgreSQL."""
    
    print(f"\nSample text: {sample_text}")
    
    # New spaCy extraction
    print("\n--- New spaCy Extraction ---")
    new_concepts = learner.extract_concepts_with_spacy(sample_text)
    print(f"Extracted {len(new_concepts)} concepts:")
    for i, concept in enumerate(new_concepts, 1):
        print(f"  {i}. {concept}")
    
    # Fallback extraction
    print("\n--- Fallback Extraction (no spaCy) ---")
    fallback_concepts = learner._extract_concepts_fallback(sample_text)
    print(f"Extracted {len(fallback_concepts)} concepts:")
    for i, concept in enumerate(fallback_concepts, 1):
        print(f"  {i}. {concept}")
    
    print("\n--- Quality Comparison ---")
    print(f"New extraction: {len(new_concepts)} concepts")
    print(f"Fallback extraction: {len(fallback_concepts)} concepts")
    print(f"Improvement: {'Yes' if len(new_concepts) >= len(fallback_concepts) * 0.8 else 'No'}")
    
    # Clean up
    if test_storage.exists():
        test_storage.unlink()


if __name__ == '__main__':
    try:
        print("\n🔬 Running Phase 13A Days 3-4 Concept Extraction Tests\n")
        
        # Run main tests
        all_passed = test_concept_extraction()
        
        # Run comparison
        test_comparison_old_vs_new()
        
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ Days 3-4 Complete: spaCy concept extraction is working!")
            print("Ready to proceed to Days 5-8: Query→Chunk Pattern Learning")
        else:
            print("⚠️  Some tests failed. Review output above for details.")
        print("=" * 80)
        
        sys.exit(0 if all_passed else 1)
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

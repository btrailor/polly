#!/usr/bin/env python3
"""
Test suite for Domain→Collection Priority Learning (Phase 13A Days 9-11)

Tests the ability to learn which collections perform best for specific domains,
enabling 20-40% faster RAG search through intelligent collection filtering.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from learners.patterns import PatternLearner


def test_record_collection_performance():
    """Test basic collection performance recording"""
    print("\n=== Test 1: Record Collection Performance ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Record performance for 'python' domain
        learner.record_collection_performance(
            domain='python',
            collection_name='codebase',
            had_results=True,
            top_score=0.85
        )
        
        # Verify pattern was created
        pattern_id = 'domain_priority_python'
        assert pattern_id in learner.domain_priority_patterns, "Pattern should be created"
        
        pattern = learner.domain_priority_patterns[pattern_id]
        assert pattern.domain == 'python', "Domain should match"
        assert 'codebase' in pattern.collection_stats, "Collection stats should be tracked"
        
        stats = pattern.collection_stats['codebase']
        assert stats['queries'] == 1, "Should have 1 query"
        assert stats['hits'] == 1, "Should have 1 hit"
        assert stats['hit_rate'] == 1.0, "Hit rate should be 100%"
        assert 'codebase' in pattern.collection_weights, "Weight should be calculated"
        
        print(f"✓ Collection stats: queries={stats['queries']}, hits={stats['hits']}, hit_rate={stats['hit_rate']:.2f}")
        print(f"✓ Collection weight: {pattern.collection_weights['codebase']:.2f}")
        print("✓ Test 1 PASSED")


def test_multiple_collections_tracking():
    """Test tracking multiple collections for same domain"""
    print("\n=== Test 2: Multiple Collections Tracking ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Record multiple collections for 'docker' domain
        collections = {
            'codebase': [(True, 0.9), (True, 0.85), (True, 0.88)],  # High performer
            'obsidian': [(True, 0.7), (False, 0.4), (True, 0.65)],  # Medium performer
            'github': [(False, 0.3), (False, 0.2), (False, 0.1)]    # Low performer
        }
        
        for coll_name, results in collections.items():
            for had_results, score in results:
                learner.record_collection_performance(
                    domain='docker',
                    collection_name=coll_name,
                    had_results=had_results,
                    top_score=score
                )
        
        pattern = learner.domain_priority_patterns['domain_priority_docker']
        
        # Verify all collections tracked
        assert len(pattern.collection_stats) == 3, "Should track 3 collections"
        
        # Check hit rates
        codebase_stats = pattern.collection_stats['codebase']
        assert codebase_stats['hit_rate'] == 1.0, "Codebase should have 100% hit rate"
        
        obsidian_stats = pattern.collection_stats['obsidian']
        assert 0.6 < obsidian_stats['hit_rate'] < 0.7, "Obsidian should have ~66% hit rate"
        
        github_stats = pattern.collection_stats['github']
        assert github_stats['hit_rate'] == 0.0, "Github should have 0% hit rate"
        
        # Verify weights reflect performance
        weights = pattern.collection_weights
        assert weights['codebase'] > weights['obsidian'], "Codebase weight should be higher"
        assert weights['obsidian'] > weights['github'], "Obsidian weight should be higher than github"
        
        print(f"✓ Codebase: hit_rate={codebase_stats['hit_rate']:.2f}, weight={weights['codebase']:.2f}")
        print(f"✓ Obsidian: hit_rate={obsidian_stats['hit_rate']:.2f}, weight={weights['obsidian']:.2f}")
        print(f"✓ Github: hit_rate={github_stats['hit_rate']:.2f}, weight={weights['github']:.2f}")
        print("✓ Test 2 PASSED")


def test_learn_domain_priorities():
    """Test high-level learn_domain_priorities() method"""
    print("\n=== Test 3: Learn Domain Priorities ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Simulate RAG search results for 'python' domain
        collection_results = {
            'codebase': 0.92,      # High score
            'obsidian': 0.68,      # Medium score
            'github_norns': 0.25   # Low score
        }
        
        # Learn from results
        learner.learn_domain_priorities(
            query="How do I use asyncio in Python?",
            domain='python',
            collection_results=collection_results
        )
        
        # Verify pattern created and updated
        pattern = learner.domain_priority_patterns['domain_priority_python']
        assert pattern.total_queries == 1, "Should have 1 query"
        assert len(pattern.collection_stats) == 3, "Should track 3 collections"
        
        # Verify collections recorded correctly
        assert pattern.collection_stats['codebase']['hits'] == 1, "Codebase should have hit"
        assert pattern.collection_stats['obsidian']['hits'] == 1, "Obsidian should have hit"
        assert pattern.collection_stats['github_norns']['hits'] == 0, "Github should have no hit (< 0.6)"
        
        print(f"✓ Pattern created with {pattern.total_queries} queries")
        print(f"✓ Confidence: {pattern.confidence:.2f}")
        print(f"✓ Weights: {pattern.collection_weights}")
        print("✓ Test 3 PASSED")


def test_get_collection_weights():
    """Test retrieving collection weights for RAG usage"""
    print("\n=== Test 4: Get Collection Weights ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Build up pattern with multiple queries
        for i in range(5):
            collection_results = {
                'codebase': 0.88 + (i * 0.02),   # Consistently high
                'obsidian': 0.65 + (i * 0.01),   # Consistently medium
                'github': 0.35 - (i * 0.05)      # Declining low
            }
            
            learner.learn_domain_priorities(
                query=f"React question {i}",
                domain='react',
                collection_results=collection_results
            )
        
        # Get weights (should work after 3+ queries)
        weights = learner.get_collection_weights_for_domain('react')
        
        assert len(weights) > 0, "Should return weights after 3+ queries"
        assert 'codebase' in weights, "Should have codebase weight"
        assert 'obsidian' in weights, "Should have obsidian weight"
        assert 'github' in weights, "Should have github weight"
        
        # Verify ordering
        assert weights['codebase'] > weights['obsidian'], "Codebase should have highest weight"
        assert weights['obsidian'] > weights['github'], "Obsidian should be higher than github"
        
        print(f"✓ Retrieved weights for 'react' domain:")
        for coll, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {coll}: {weight:.2f}")
        print("✓ Test 4 PASSED")


def test_insufficient_data_handling():
    """Test that weights aren't returned with insufficient data"""
    print("\n=== Test 5: Insufficient Data Handling ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Record only 1-2 queries (below minimum threshold)
        learner.learn_domain_priorities(
            query="Test query 1",
            domain='docker',
            collection_results={'codebase': 0.9}
        )
        
        learner.learn_domain_priorities(
            query="Test query 2",
            domain='docker',
            collection_results={'codebase': 0.85}
        )
        
        # Should not return weights (need 3+ queries)
        weights = learner.get_collection_weights_for_domain('docker')
        assert len(weights) == 0, "Should not return weights with < 3 queries"
        
        print("✓ Correctly rejected pattern with only 2 queries")
        
        # Add one more query to reach threshold
        learner.learn_domain_priorities(
            query="Test query 3",
            domain='docker',
            collection_results={'codebase': 0.88}
        )
        
        # Now should return weights
        weights = learner.get_collection_weights_for_domain('docker')
        assert len(weights) > 0, "Should return weights after 3 queries"
        
        print(f"✓ Correctly returned weights after 3 queries: {weights}")
        print("✓ Test 5 PASSED")


def test_pattern_persistence():
    """Test that domain patterns are saved and loaded correctly"""
    print("\n=== Test 6: Pattern Persistence ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        
        # Create patterns in first learner instance
        learner1 = PatternLearner(storage_path=storage_path)
        
        for i in range(5):
            learner1.learn_domain_priorities(
                query=f"Python query {i}",
                domain='python',
                collection_results={
                    'codebase': 0.9,
                    'obsidian': 0.7
                }
            )
        
        # Get weights before saving
        weights_before = learner1.get_collection_weights_for_domain('python')
        assert len(weights_before) > 0, "Should have weights"
        
        # Create new learner instance (should load saved patterns)
        learner2 = PatternLearner(storage_path=storage_path)
        
        # Get weights after loading
        weights_after = learner2.get_collection_weights_for_domain('python')
        
        assert len(weights_after) > 0, "Should load saved weights"
        assert weights_after == weights_before, "Loaded weights should match saved weights"
        
        pattern = learner2.domain_priority_patterns['domain_priority_python']
        assert pattern.total_queries == 5, "Should preserve query count"
        
        print(f"✓ Pattern persisted correctly:")
        print(f"  - Queries: {pattern.total_queries}")
        print(f"  - Confidence: {pattern.confidence:.2f}")
        print(f"  - Weights: {weights_after}")
        print("✓ Test 6 PASSED")


def test_real_world_scenario():
    """Test realistic scenario with multiple domains and queries"""
    print("\n=== Test 7: Real-World Scenario ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Simulate 20 queries across 3 domains
        scenarios = [
            # Python domain - codebase is best
            ('python', {'codebase': 0.92, 'obsidian': 0.65, 'github': 0.3}),
            ('python', {'codebase': 0.88, 'obsidian': 0.68, 'github': 0.25}),
            ('python', {'codebase': 0.95, 'obsidian': 0.62, 'github': 0.35}),
            ('python', {'codebase': 0.90, 'obsidian': 0.70, 'github': 0.28}),
            ('python', {'codebase': 0.87, 'obsidian': 0.66, 'github': 0.32}),
            
            # Docker domain - mixed results
            ('docker', {'codebase': 0.85, 'obsidian': 0.75, 'github': 0.80}),
            ('docker', {'codebase': 0.82, 'obsidian': 0.72, 'github': 0.85}),
            ('docker', {'codebase': 0.88, 'obsidian': 0.68, 'github': 0.78}),
            ('docker', {'codebase': 0.80, 'obsidian': 0.70, 'github': 0.82}),
            
            # React domain - obsidian is best
            ('react', {'codebase': 0.55, 'obsidian': 0.92, 'github': 0.45}),
            ('react', {'codebase': 0.58, 'obsidian': 0.88, 'github': 0.50}),
            ('react', {'codebase': 0.52, 'obsidian': 0.95, 'github': 0.42}),
            ('react', {'codebase': 0.60, 'obsidian': 0.90, 'github': 0.48}),
        ]
        
        for i, (domain, results) in enumerate(scenarios):
            learner.learn_domain_priorities(
                query=f"Query {i} about {domain}",
                domain=domain,
                collection_results=results
            )
        
        # Verify patterns learned correctly
        print("\n✓ Learned patterns:")
        
        # Python: codebase should be highest
        python_weights = learner.get_collection_weights_for_domain('python')
        print(f"\n  Python domain ({len(scenarios[:5])} queries):")
        for coll in sorted(python_weights, key=lambda c: python_weights[c], reverse=True):
            print(f"    {coll}: {python_weights[coll]:.2f}")
        assert python_weights['codebase'] > python_weights['obsidian'], "Codebase should dominate for Python"
        
        # Docker: relatively balanced
        docker_weights = learner.get_collection_weights_for_domain('docker')
        print(f"\n  Docker domain ({len([s for s in scenarios if s[0] == 'docker'])} queries):")
        for coll in sorted(docker_weights, key=lambda c: docker_weights[c], reverse=True):
            print(f"    {coll}: {docker_weights[coll]:.2f}")
        
        # React: obsidian should be highest
        react_weights = learner.get_collection_weights_for_domain('react')
        print(f"\n  React domain ({len([s for s in scenarios if s[0] == 'react'])} queries):")
        for coll in sorted(react_weights, key=lambda c: react_weights[c], reverse=True):
            print(f"    {coll}: {react_weights[coll]:.2f}")
        assert react_weights['obsidian'] > react_weights['codebase'], "Obsidian should dominate for React"
        
        print("\n✓ Test 7 PASSED")


def run_all_tests():
    """Run all domain priority learning tests"""
    print("=" * 60)
    print("Phase 13A Days 9-11: Domain→Collection Priority Learning Tests")
    print("=" * 60)
    
    tests = [
        test_record_collection_performance,
        test_multiple_collections_tracking,
        test_learn_domain_priorities,
        test_get_collection_weights,
        test_insufficient_data_handling,
        test_pattern_persistence,
        test_real_world_scenario,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

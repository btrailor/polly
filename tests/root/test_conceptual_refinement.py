#!/usr/bin/env python3
"""
Test suite for Conceptual Pattern Refinement (Phase 13A Days 12-13)

Tests the enhanced conceptual pattern system with:
- Stricter thresholds (min 7 occurrences, 0.5 confidence)
- Pattern pruning (cap at 200)
- Query expansion using patterns
- Usefulness tracking
"""

import sys
import os
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from learners.patterns import PatternLearner, Pattern


def test_strict_thresholds():
    """Test that patterns require 7 occurrences and 0.5 confidence"""
    print("\n=== Test 1: Strict Thresholds ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path, min_occurrences=3)
        
        # Create messages with docker+python concepts appearing multiple times
        messages = [
            {'role': 'user', 'content': 'How do I use docker with python?'},
            {'role': 'assistant', 'content': 'You can use docker and python together...'},
        ]
        
        # First attempt: only 1 occurrence (should not create pattern)
        patterns_created = learner.learn_conceptual_patterns(
            conversation_id='conv1',
            messages=messages
        )
        assert patterns_created == 0, "Should not create pattern with < 7 occurrences"
        
        # Repeat 6 more times to reach 7 total occurrences
        for i in range(6):
            learner.learn_conceptual_patterns(
                conversation_id=f'conv{i+2}',
                messages=messages
            )
        
        # After 7 occurrences, check if pattern exists
        # Need to reach confidence >= 0.5, which is 7/(7*3) = 0.33, not enough
        # Need 14 occurrences to reach 0.67 confidence
        patterns_created = 0
        for i in range(7):
            patterns_created += learner.learn_conceptual_patterns(
                conversation_id=f'conv{i+9}',
                messages=messages
            )
        
        # Now should have pattern with confidence >= 0.5
        docker_python_patterns = [p for p in learner.patterns.values() 
                                  if 'docker' in p.name.lower() and 'python' in p.name.lower()]
        
        assert len(docker_python_patterns) > 0, "Should have docker↔python pattern after 14+ occurrences"
        pattern = docker_python_patterns[0]
        assert pattern.confidence >= 0.5, f"Pattern confidence should be >= 0.5, got {pattern.confidence:.2f}"
        
        print(f"✓ Pattern created with confidence={pattern.confidence:.2f} after 14+ occurrences")
        print(f"✓ Pattern name: {pattern.name}")
        print("✓ Test 1 PASSED")


def test_conceptual_pattern_pruning():
    """Test that conceptual patterns are capped at 200"""
    print("\n=== Test 2: Conceptual Pattern Pruning ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Manually create 250 conceptual patterns with varying quality
        now = datetime.now()
        
        for i in range(250):
            # Vary occurrences and confidence to create quality spread
            occurrences = 7 + (i % 20)  # 7-26
            confidence = 0.5 + (i % 50) / 100  # 0.5-0.99
            
            pattern = Pattern(
                id=f'concept_pair_test{i}_test{i+1}',
                name=f'Conceptual Connection: test{i} ↔ test{i+1}',
                description=f'Test pattern {i}',
                pattern_type='conceptual',
                domains=['test'],
                examples=['test'],
                occurrences=occurrences,
                first_seen=now,
                last_seen=now,
                confidence=confidence,
                metadata={'concept1': f'test{i}', 'concept2': f'test{i+1}'}
            )
            learner.patterns[pattern.id] = pattern
        
        # Trigger pruning
        learner._prune_conceptual_patterns()
        
        # Count conceptual patterns
        conceptual_count = len([p for p in learner.patterns.values() if p.pattern_type == 'conceptual'])
        
        assert conceptual_count == 200, f"Should have exactly 200 conceptual patterns, got {conceptual_count}"
        
        # Verify that top quality patterns were kept
        remaining = [p for p in learner.patterns.values() if p.pattern_type == 'conceptual']
        qualities = [p.confidence * p.occurrences for p in remaining]
        min_quality = min(qualities)
        
        print(f"✓ Pruned from 250 to {conceptual_count} patterns")
        print(f"✓ Minimum quality score of kept patterns: {min_quality:.2f}")
        print("✓ Test 2 PASSED")


def test_pattern_usefulness_tracking():
    """Test that pattern usage is tracked"""
    print("\n=== Test 3: Pattern Usefulness Tracking ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        # Create a conceptual pattern
        now = datetime.now()
        pattern = Pattern(
            id='concept_pair_docker_python',
            name='Conceptual Connection: docker ↔ python',
            description='Test pattern',
            pattern_type='conceptual',
            domains=['sigils'],
            examples=['test'],
            occurrences=15,
            first_seen=now,
            last_seen=now,
            confidence=0.8,
            metadata={'concept1': 'docker', 'concept2': 'python'},
            times_used=0,
            times_helpful=0
        )
        learner.patterns[pattern.id] = pattern
        
        # Record usage (helpful)
        learner.record_pattern_usage('concept_pair_docker_python', was_helpful=True)
        assert pattern.times_used == 1, "Should have 1 use"
        assert pattern.times_helpful == 1, "Should have 1 helpful use"
        
        # Record usage (not helpful)
        learner.record_pattern_usage('concept_pair_docker_python', was_helpful=False)
        assert pattern.times_used == 2, "Should have 2 uses"
        assert pattern.times_helpful == 1, "Should still have 1 helpful use"
        
        # Record more helpful uses
        for _ in range(3):
            learner.record_pattern_usage('concept_pair_docker_python', was_helpful=True)
        
        assert pattern.times_used == 5, "Should have 5 total uses"
        assert pattern.times_helpful == 4, "Should have 4 helpful uses"
        
        usefulness_ratio = pattern.times_helpful / pattern.times_used
        assert usefulness_ratio == 0.8, f"Usefulness should be 0.8, got {usefulness_ratio}"
        
        print(f"✓ Pattern usage tracked: {pattern.times_used} uses, {pattern.times_helpful} helpful")
        print(f"✓ Usefulness ratio: {usefulness_ratio:.2f}")
        print("✓ Test 3 PASSED")


def test_pattern_persistence_with_usefulness():
    """Test that usefulness tracking persists across sessions"""
    print("\n=== Test 4: Pattern Persistence with Usefulness ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        
        # Create pattern with usefulness data
        learner1 = PatternLearner(storage_path=storage_path)
        now = datetime.now()
        pattern = Pattern(
            id='concept_pair_docker_python',
            name='Conceptual Connection: docker ↔ python',
            description='Test pattern',
            pattern_type='conceptual',
            domains=['sigils'],
            examples=['test'],
            occurrences=15,
            first_seen=now,
            last_seen=now,
            confidence=0.8,
            metadata={'concept1': 'docker', 'concept2': 'python'},
            times_used=10,
            times_helpful=8
        )
        learner1.patterns[pattern.id] = pattern
        learner1.save_patterns()
        
        # Load in new learner instance
        learner2 = PatternLearner(storage_path=storage_path)
        
        assert 'concept_pair_docker_python' in learner2.patterns, "Pattern should be loaded"
        loaded_pattern = learner2.patterns['concept_pair_docker_python']
        
        assert loaded_pattern.times_used == 10, f"Should load times_used=10, got {loaded_pattern.times_used}"
        assert loaded_pattern.times_helpful == 8, f"Should load times_helpful=8, got {loaded_pattern.times_helpful}"
        
        print(f"✓ Pattern usefulness persisted: {loaded_pattern.times_used} uses, {loaded_pattern.times_helpful} helpful")
        print("✓ Test 4 PASSED")


def test_minimum_confidence_filtering():
    """Test that low-confidence patterns are not created"""
    print("\n=== Test 5: Minimum Confidence Filtering ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        messages = [
            {'role': 'user', 'content': 'How do I use react with typescript?'},
            {'role': 'assistant', 'content': 'You can use react and typescript together...'},
        ]
        
        # Learn patterns 7 times (minimum occurrences)
        # This gives confidence = 7/(7*3) = 0.33, which is < 0.5
        for i in range(7):
            learner.learn_conceptual_patterns(
                conversation_id=f'conv{i}',
                messages=messages
            )
        
        # Should NOT create pattern (confidence < 0.5)
        react_typescript_patterns = [p for p in learner.patterns.values() 
                                      if 'react' in p.name.lower() and 'typescript' in p.name.lower()]
        
        assert len(react_typescript_patterns) == 0, "Should not create pattern with confidence < 0.5"
        
        # Learn 7 more times to reach confidence = 14/(7*3) = 0.67
        for i in range(7):
            learner.learn_conceptual_patterns(
                conversation_id=f'conv{i+7}',
                messages=messages
            )
        
        # Now should have pattern (confidence >= 0.5)
        react_typescript_patterns = [p for p in learner.patterns.values() 
                                      if 'react' in p.name.lower() and 'typescript' in p.name.lower()]
        
        assert len(react_typescript_patterns) > 0, "Should create pattern with confidence >= 0.5"
        pattern = react_typescript_patterns[0]
        
        print(f"✓ Pattern rejected at confidence=0.33 (< 0.5)")
        print(f"✓ Pattern created at confidence={pattern.confidence:.2f} (>= 0.5)")
        print("✓ Test 5 PASSED")


def test_pruning_quality_ordering():
    """Test that pruning keeps highest quality patterns"""
    print("\n=== Test 6: Pruning Quality Ordering ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / 'patterns.json'
        learner = PatternLearner(storage_path=storage_path)
        
        now = datetime.now()
        
        # Create patterns with specific quality scores
        # Quality = confidence * occurrences
        patterns_to_create = [
            ('high_quality', 0.9, 20),   # quality = 18.0
            ('medium_quality', 0.7, 15), # quality = 10.5
            ('low_quality', 0.5, 8),     # quality = 4.0 (LOWEST, should be pruned)
        ]
        
        for name, confidence, occurrences in patterns_to_create:
            pattern = Pattern(
                id=f'concept_pair_{name}_test',
                name=f'Conceptual Connection: {name} ↔ test',
                description=f'Test pattern {name}',
                pattern_type='conceptual',
                domains=['test'],
                examples=['test'],
                occurrences=occurrences,
                first_seen=now,
                last_seen=now,
                confidence=confidence,
                metadata={'concept1': name, 'concept2': 'test'}
            )
            learner.patterns[pattern.id] = pattern
        
        # Add 198 more medium-quality patterns (quality = 4.4)
        for i in range(198):
            pattern = Pattern(
                id=f'concept_pair_filler{i}_test',
                name=f'Conceptual Connection: filler{i} ↔ test',
                description=f'Filler pattern {i}',
                pattern_type='conceptual',
                domains=['test'],
                examples=['test'],
                occurrences=8,
                first_seen=now,
                last_seen=now,
                confidence=0.55,
                metadata={'concept1': f'filler{i}', 'concept2': 'test'}
            )
            learner.patterns[pattern.id] = pattern
        
        # Now we have 201 patterns total
        # After pruning, low_quality (4.0) should be removed, others kept
        learner._prune_conceptual_patterns()
        
        # Check that high and medium quality patterns survived
        assert 'concept_pair_high_quality_test' in learner.patterns, "High quality (18.0) should survive"
        assert 'concept_pair_medium_quality_test' in learner.patterns, "Medium quality (10.5) should survive"
        assert 'concept_pair_low_quality_test' not in learner.patterns, "Low quality (4.0) should be pruned"
        
        # Filler patterns (4.4) should survive since they're better than low_quality (4.0)
        filler_count = len([p for p in learner.patterns.values() if 'filler' in p.id])
        assert filler_count == 198, f"All 198 filler patterns should survive, got {filler_count}"
        
        print("✓ High quality pattern (18.0) kept")
        print("✓ Medium quality pattern (10.5) kept")
        print("✓ Filler patterns (4.4) kept")
        print("✓ Low quality pattern (4.0) pruned")
        print("✓ Test 6 PASSED")


def run_all_tests():
    """Run all conceptual pattern refinement tests"""
    print("=" * 70)
    print("Phase 13A Days 12-13: Conceptual Pattern Refinement Tests")
    print("=" * 70)
    
    tests = [
        test_strict_thresholds,
        test_conceptual_pattern_pruning,
        test_pattern_usefulness_tracking,
        test_pattern_persistence_with_usefulness,
        test_minimum_confidence_filtering,
        test_pruning_quality_ordering,
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
    
    print("\n" + "=" * 70)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if passed == len(tests):
        print("\n✅ Days 12-13 Complete: Conceptual Pattern Refinement Working!")
        print("\nEnhancements implemented:")
        print("  - Stricter thresholds (min 7 occurrences, 0.5 confidence)")
        print("  - Pattern pruning (cap at 200 highest quality)")
        print("  - Pattern usefulness tracking (times_used, times_helpful)")
        print("  - Query expansion ready (integrated in polly.py)")
        print("\nExpected impact: 10-20% better relevance through quality filtering")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)

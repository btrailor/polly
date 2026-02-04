#!/usr/bin/env python3
"""
Phase 13A Days 14-15: Pattern Quality Controls Tests

Tests for:
1. Pattern pruning (old + low confidence, single occurrence + old)
2. Query→chunk pattern pruning (keep top 100)
3. Pattern decay over time
4. Automatic pruning on save
"""

from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import json

from learners.patterns import PatternLearner


def test_old_low_confidence_pruning():
    """Test pruning of old patterns with low confidence."""
    print("\n" + "="*80)
    print("Test 1: Old + Low Confidence Pattern Pruning")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "patterns_test.json"
        learner = PatternLearner(storage_path=storage_path)
        
        # Create patterns with different ages and confidences
        now = datetime.now()
        
        # Pattern 1: Old (100 days) + low confidence (0.3) - SHOULD BE PRUNED
        learner.patterns['pattern_old_low'] = type('Pattern', (), {
            'id': 'pattern_old_low',
            'name': 'Old Low Confidence Pattern',
            'description': 'Should be pruned',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 3,
            'first_seen': now - timedelta(days=100),
            'last_seen': now - timedelta(days=100),
            'confidence': 0.3,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        # Pattern 2: Old (100 days) + high confidence (0.8) - SHOULD BE KEPT
        learner.patterns['pattern_old_high'] = type('Pattern', (), {
            'id': 'pattern_old_high',
            'name': 'Old High Confidence Pattern',
            'description': 'Should be kept',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 10,
            'first_seen': now - timedelta(days=100),
            'last_seen': now - timedelta(days=100),
            'confidence': 0.8,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        # Pattern 3: Recent (10 days) + low confidence (0.3) - SHOULD BE KEPT
        learner.patterns['pattern_recent_low'] = type('Pattern', (), {
            'id': 'pattern_recent_low',
            'name': 'Recent Low Confidence Pattern',
            'description': 'Should be kept',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 3,
            'first_seen': now - timedelta(days=10),
            'last_seen': now - timedelta(days=10),
            'confidence': 0.3,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        print(f"\n📊 Initial patterns: {len(learner.patterns)}")
        for pattern_id, pattern in learner.patterns.items():
            print(f"  - {pattern.name}: confidence={pattern.confidence:.2f}, "
                  f"last_seen={pattern.last_seen.date()}")
        
        # Run pruning
        pruned_count = learner.prune_low_quality_patterns()
        
        print(f"\n✂️ Pruned {pruned_count} patterns")
        print(f"📊 Remaining patterns: {len(learner.patterns)}")
        for pattern_id, pattern in learner.patterns.items():
            print(f"  - {pattern.name}: confidence={pattern.confidence:.2f}, "
                  f"last_seen={pattern.last_seen.date()}")
        
        # Verify pruning
        assert 'pattern_old_low' not in learner.patterns, "Old + low confidence pattern should be pruned"
        assert 'pattern_old_high' in learner.patterns, "Old + high confidence pattern should be kept"
        assert 'pattern_recent_low' in learner.patterns, "Recent + low confidence pattern should be kept"
        assert pruned_count >= 1, "At least one pattern should be pruned"
        
        print("\n✅ Test 1 PASSED: Old + low confidence patterns pruned correctly")
        return True


def test_single_occurrence_old_pruning():
    """Test pruning of old patterns with only one occurrence."""
    print("\n" + "="*80)
    print("Test 2: Single Occurrence + Old Pattern Pruning")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "patterns_test.json"
        learner = PatternLearner(storage_path=storage_path)
        
        now = datetime.now()
        
        # Pattern 1: Single occurrence + old (40 days) - SHOULD BE PRUNED
        learner.patterns['pattern_single_old'] = type('Pattern', (), {
            'id': 'pattern_single_old',
            'name': 'Single Occurrence Old Pattern',
            'description': 'Should be pruned',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 1,
            'first_seen': now - timedelta(days=40),
            'last_seen': now - timedelta(days=40),
            'confidence': 0.5,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        # Pattern 2: Multiple occurrences + old (40 days) - SHOULD BE KEPT
        learner.patterns['pattern_multi_old'] = type('Pattern', (), {
            'id': 'pattern_multi_old',
            'name': 'Multiple Occurrence Old Pattern',
            'description': 'Should be kept',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 5,
            'first_seen': now - timedelta(days=40),
            'last_seen': now - timedelta(days=40),
            'confidence': 0.5,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        # Pattern 3: Single occurrence + recent (10 days) - SHOULD BE KEPT
        learner.patterns['pattern_single_recent'] = type('Pattern', (), {
            'id': 'pattern_single_recent',
            'name': 'Single Occurrence Recent Pattern',
            'description': 'Should be kept',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 1,
            'first_seen': now - timedelta(days=10),
            'last_seen': now - timedelta(days=10),
            'confidence': 0.5,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        print(f"\n📊 Initial patterns: {len(learner.patterns)}")
        for pattern_id, pattern in learner.patterns.items():
            print(f"  - {pattern.name}: occurrences={pattern.occurrences}, "
                  f"first_seen={pattern.first_seen.date()}")
        
        # Run pruning
        pruned_count = learner.prune_low_quality_patterns()
        
        print(f"\n✂️ Pruned {pruned_count} patterns")
        print(f"📊 Remaining patterns: {len(learner.patterns)}")
        for pattern_id, pattern in learner.patterns.items():
            print(f"  - {pattern.name}: occurrences={pattern.occurrences}, "
                  f"first_seen={pattern.first_seen.date()}")
        
        # Verify pruning
        assert 'pattern_single_old' not in learner.patterns, "Single occurrence + old pattern should be pruned"
        assert 'pattern_multi_old' in learner.patterns, "Multiple occurrence + old pattern should be kept"
        assert 'pattern_single_recent' in learner.patterns, "Single occurrence + recent pattern should be kept"
        assert pruned_count >= 1, "At least one pattern should be pruned"
        
        print("\n✅ Test 2 PASSED: Single occurrence + old patterns pruned correctly")
        return True


def test_query_chunk_pattern_pruning():
    """Test pruning of query→chunk patterns (keep top 100)."""
    print("\n" + "="*80)
    print("Test 3: Query→Chunk Pattern Pruning (Keep Top 100)")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "patterns_test.json"
        learner = PatternLearner(storage_path=storage_path)
        
        now = datetime.now()
        
        # Create 150 query→chunk patterns with varying query counts
        for i in range(150):
            pattern_id = f'qcp_pattern_{i}'
            learner.query_chunk_patterns[pattern_id] = type('QueryChunkPattern', (), {
                'pattern_id': pattern_id,
                'query_template': f'Template {i}',
                'query_signature': f'sig_{i}',
                'successful_chunks': {'chunk_1': {'hit_count': 1, 'avg_score': 0.8}},
                'total_queries': 150 - i,  # Higher index = lower queries
                'confidence': 0.5,
                'first_seen': now,
                'last_seen': now,
                'metadata': {}
            })()
        
        print(f"\n📊 Initial query→chunk patterns: {len(learner.query_chunk_patterns)}")
        print(f"  - Top pattern queries: {learner.query_chunk_patterns['qcp_pattern_0'].total_queries}")
        print(f"  - 100th pattern queries: {learner.query_chunk_patterns['qcp_pattern_99'].total_queries}")
        print(f"  - Bottom pattern queries: {learner.query_chunk_patterns['qcp_pattern_149'].total_queries}")
        
        # Run pruning
        pruned_count = learner.prune_low_quality_patterns()
        
        print(f"\n✂️ Pruned {pruned_count} patterns")
        print(f"📊 Remaining query→chunk patterns: {len(learner.query_chunk_patterns)}")
        
        # Verify pruning
        assert len(learner.query_chunk_patterns) == 100, f"Should keep exactly 100 patterns, got {len(learner.query_chunk_patterns)}"
        assert 'qcp_pattern_0' in learner.query_chunk_patterns, "Top pattern should be kept"
        assert 'qcp_pattern_99' in learner.query_chunk_patterns, "100th pattern should be kept"
        assert 'qcp_pattern_149' not in learner.query_chunk_patterns, "Bottom pattern should be pruned"
        assert pruned_count == 50, f"Should prune exactly 50 patterns, pruned {pruned_count}"
        
        # Verify kept patterns are the highest quality
        min_queries = min(p.total_queries for p in learner.query_chunk_patterns.values())
        print(f"  - Minimum queries in kept patterns: {min_queries}")
        assert min_queries >= 51, "Should keep patterns with at least 51 queries"
        
        print("\n✅ Test 3 PASSED: Query→chunk patterns pruned to top 100")
        return True


def test_pattern_decay():
    """Test pattern decay for inactive patterns."""
    print("\n" + "="*80)
    print("Test 4: Pattern Decay Over Time")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "patterns_test.json"
        learner = PatternLearner(storage_path=storage_path)
        
        now = datetime.now()
        
        # Create a pattern that was last seen 90 days ago
        old_last_seen = now - timedelta(days=90)
        learner.patterns['pattern_decay'] = type('Pattern', (), {
            'id': 'pattern_decay',
            'name': 'Decaying Pattern',
            'description': 'Should decay',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example 1'],
            'occurrences': 5,
            'first_seen': now - timedelta(days=100),
            'last_seen': old_last_seen,
            'confidence': 0.8,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        original_confidence = learner.patterns['pattern_decay'].confidence
        print(f"\n📊 Original pattern:")
        print(f"  - Last seen: {old_last_seen.date()} (90 days ago)")
        print(f"  - Confidence: {original_confidence:.4f}")
        
        # Register a new occurrence (should trigger decay)
        learner._register_pattern_occurrence(
            pattern_id='pattern_decay',
            name='Decaying Pattern',
            description='Should decay',
            pattern_type='conceptual',
            domains=['test'],
            example='example 2'
        )
        
        new_confidence = learner.patterns['pattern_decay'].confidence
        print(f"\n⏳ After registering new occurrence:")
        print(f"  - Confidence: {new_confidence:.4f}")
        print(f"  - Decay applied: {(1 - new_confidence/original_confidence)*100:.1f}%")
        
        # Verify decay was applied
        assert new_confidence < original_confidence, "Confidence should decay after inactivity"
        
        # Expected decay: 0.98^30 = 0.545 (for 30 days after 60-day threshold)
        expected_decay = 0.98 ** 30
        expected_confidence = original_confidence * expected_decay
        
        # After decay, confidence is recalculated based on occurrences
        # New occurrences = 6, so new confidence = min(6/10, 1.0) = 0.6
        # But if decayed confidence is higher, we keep the higher value
        print(f"  - Expected decayed confidence: {expected_confidence:.4f}")
        print(f"  - Expected recalculated confidence: {min(6/10, 1.0):.4f}")
        print(f"  - Actual confidence: {new_confidence:.4f}")
        
        # The pattern should have been decayed, then recalculated
        # Since 6 occurrences gives 0.6 confidence, and decay gives ~0.44, we use 0.6
        assert new_confidence >= 0.5, "Confidence should recover with new occurrences"
        
        print("\n✅ Test 4 PASSED: Pattern decay working correctly")
        return True


def test_automatic_pruning_on_save():
    """Test that pruning happens automatically when saving."""
    print("\n" + "="*80)
    print("Test 5: Automatic Pruning on Save")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "patterns_test.json"
        learner = PatternLearner(storage_path=storage_path)
        
        now = datetime.now()
        
        # Create some patterns that should be pruned
        learner.patterns['pattern_prune'] = type('Pattern', (), {
            'id': 'pattern_prune',
            'name': 'To Be Pruned',
            'description': 'Should be pruned',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 1,
            'first_seen': now - timedelta(days=40),
            'last_seen': now - timedelta(days=40),
            'confidence': 0.3,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        learner.patterns['pattern_keep'] = type('Pattern', (), {
            'id': 'pattern_keep',
            'name': 'To Be Kept',
            'description': 'Should be kept',
            'pattern_type': 'conceptual',
            'domains': ['test'],
            'examples': ['example'],
            'occurrences': 10,
            'first_seen': now - timedelta(days=10),
            'last_seen': now - timedelta(days=10),
            'confidence': 0.8,
            'metadata': {},
            'times_used': 0,
            'times_helpful': 0
        })()
        
        print(f"\n📊 Before save: {len(learner.patterns)} patterns")
        for pattern_id in learner.patterns:
            print(f"  - {pattern_id}")
        
        # Save patterns (should trigger pruning)
        learner.save_patterns()
        
        print(f"\n💾 After save: {len(learner.patterns)} patterns")
        for pattern_id in learner.patterns:
            print(f"  - {pattern_id}")
        
        # Verify pruning happened
        assert 'pattern_prune' not in learner.patterns, "Old single-occurrence pattern should be pruned"
        assert 'pattern_keep' in learner.patterns, "Good pattern should be kept"
        
        # Load patterns and verify persistence
        learner2 = PatternLearner(storage_path=storage_path)
        print(f"\n📂 After reload: {len(learner2.patterns)} patterns")
        for pattern_id in learner2.patterns:
            print(f"  - {pattern_id}")
        
        assert 'pattern_prune' not in learner2.patterns, "Pruned pattern should not be in saved file"
        assert 'pattern_keep' in learner2.patterns, "Kept pattern should be in saved file"
        
        print("\n✅ Test 5 PASSED: Automatic pruning on save working correctly")
        return True


def test_domain_priority_never_pruned():
    """Test that domain priority patterns are never pruned."""
    print("\n" + "="*80)
    print("Test 6: Domain Priority Patterns Never Pruned")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = Path(tmpdir) / "patterns_test.json"
        learner = PatternLearner(storage_path=storage_path)
        
        now = datetime.now()
        
        # Create domain priority patterns with various ages
        for i in range(10):
            pattern_id = f'dpp_domain_{i}'
            learner.domain_priority_patterns[pattern_id] = type('DomainPriorityPattern', (), {
                'pattern_id': pattern_id,
                'domain': f'domain_{i}',
                'collection_weights': {'codebase': 2.0},
                'total_queries': i + 1,
                'confidence': 0.5,
                'first_seen': now - timedelta(days=100 + i),
                'last_seen': now - timedelta(days=100 + i),
                'metadata': {}
            })()
        
        print(f"\n📊 Initial domain priority patterns: {len(learner.domain_priority_patterns)}")
        
        # Run pruning multiple times
        for _ in range(3):
            learner.prune_low_quality_patterns()
        
        print(f"📊 After pruning: {len(learner.domain_priority_patterns)}")
        
        # Verify no domain priority patterns were pruned
        assert len(learner.domain_priority_patterns) == 10, "Domain priority patterns should never be pruned"
        
        print("\n✅ Test 6 PASSED: Domain priority patterns never pruned")
        return True


def run_all_tests():
    """Run all pattern quality control tests."""
    print("\n" + "="*80)
    print("Phase 13A Days 14-15: Pattern Quality Controls Tests")
    print("="*80)
    
    tests = [
        ("Old + Low Confidence Pruning", test_old_low_confidence_pruning),
        ("Single Occurrence + Old Pruning", test_single_occurrence_old_pruning),
        ("Query→Chunk Pattern Pruning", test_query_chunk_pattern_pruning),
        ("Pattern Decay", test_pattern_decay),
        ("Automatic Pruning on Save", test_automatic_pruning_on_save),
        ("Domain Priority Never Pruned", test_domain_priority_never_pruned),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test FAILED: {test_name}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*80)
    print("Test Results")
    print("="*80)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED - Pattern Quality Controls Working!")
        print("="*80)
        print("\n🚀 Ready for Day 16: Pattern Enhancement APIs")
        print("\nExpected impact:")
        print("  - Automatic cleanup of stale patterns")
        print("  - Maximum 100 query→chunk patterns (top performers)")
        print("  - Maximum 200 conceptual patterns (already capped in Days 12-13)")
        print("  - Pattern decay encourages fresh, active patterns")
        print("  - Domain priority patterns always preserved")
    
    return failed == 0


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)

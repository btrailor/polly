#!/usr/bin/env python3
"""
Test pattern storage with real ~/.polly directory
Tests the full Day 1 implementation
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner


def test_real_storage():
    """Test that patterns work with real ~/.polly directory."""
    print("Testing PatternLearner with real ~/.polly directory...")
    
    # Use actual storage path (what Polly uses)
    storage_path = Path("~/.polly/patterns.json")
    
    print(f"Storage path (before expansion): {storage_path}")
    
    # Initialize PatternLearner (should expand ~ automatically)
    learner = PatternLearner(storage_path=storage_path, min_occurrences=3)
    
    expanded_path = learner.storage_path
    print(f"Storage path (after expansion): {expanded_path}")
    
    # Verify path was expanded
    assert str(expanded_path).startswith('/'), "Path should be absolute"
    assert '~' not in str(expanded_path), "Path should not contain ~"
    
    print("✅ Path expansion works correctly")
    
    # Verify parent directory exists
    assert expanded_path.parent.exists(), "Parent directory should exist"
    assert expanded_path.parent.is_dir(), "Parent should be a directory"
    
    print("✅ Parent directory created successfully")
    
    # Verify storage file was initialized
    assert expanded_path.exists(), "Storage file should exist"
    
    print("✅ Storage file created successfully")
    
    # Verify file has correct structure
    data = json.loads(expanded_path.read_text())
    assert 'patterns' in data, "Should have patterns key"
    assert 'query_patterns' in data, "Should have query_patterns key"
    assert 'metadata' in data, "Should have metadata key"
    assert 'created' in data['metadata'], "Should have created timestamp"
    assert data['metadata']['version'] == '2.0', "Should have correct version"
    
    print("✅ Storage file has correct structure")
    print(f"✅ Storage initialized at: {data['metadata']['created']}")
    
    # Test recording a query
    print("\nTesting query recording...")
    learner.record_query("How do I use Docker with Python?", ["sigils"])
    learner.record_query("Explain norns in SuperCollider", ["signals"])
    learner.record_query("Write an essay about pedagogy", ["scrolls"])
    
    # Save patterns
    learner.save_patterns()
    
    print("✅ Recorded 3 queries and saved")
    
    # Verify persistence - load in new instance
    print("\nTesting persistence...")
    learner2 = PatternLearner(storage_path=storage_path)
    
    assert len(learner2.query_history) == 3, f"Expected 3 queries, got {len(learner2.query_history)}"
    
    print("✅ Patterns persisted across instances")
    print(f"✅ Loaded {len(learner2.query_history)} query history items")
    
    # Verify the queries are correct
    queries = [q['query'] for q in learner2.query_history]
    assert "How do I use Docker with Python?" in queries
    assert "Explain norns in SuperCollider" in queries
    assert "Write an essay about pedagogy" in queries
    
    print("✅ All queries loaded correctly")
    
    # Test pattern retrieval
    print("\nTesting pattern retrieval...")
    patterns = learner2.get_relevant_patterns("Docker Python question", ["sigils"])
    print(f"Found {len(patterns)} relevant patterns")
    
    print("\n✅ All tests passed!")
    print(f"\nPattern storage location: {expanded_path}")
    print(f"File size: {expanded_path.stat().st_size} bytes")


if __name__ == "__main__":
    test_real_storage()

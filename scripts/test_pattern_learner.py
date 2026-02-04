#!/usr/bin/env python3
"""
Test script for PatternLearner directory creation
Tests Task 1.1 - Verify storage directory is created on initialization
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner


def test_storage_directory_creation():
    """Test that PatternLearner creates storage directory on init."""
    print("Testing PatternLearner storage directory creation...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Use a nested path to test parent directory creation
        storage_path = Path(tmpdir) / "polly_data" / "patterns" / "patterns.json"
        
        print(f"Storage path: {storage_path}")
        print(f"Parent directory: {storage_path.parent}")
        
        # Verify parent doesn't exist yet
        assert not storage_path.parent.exists(), "Parent directory shouldn't exist yet"
        
        # Initialize PatternLearner
        learner = PatternLearner(storage_path=storage_path, min_occurrences=3)
        
        # Verify parent directory was created
        assert storage_path.parent.exists(), "Parent directory should be created"
        assert storage_path.parent.is_dir(), "Parent should be a directory"
        
        print("✅ Parent directory created successfully")
        
        # Verify the learner is properly initialized
        assert learner.storage_path == storage_path
        assert learner.min_occurrences == 3
        assert isinstance(learner.patterns, dict)
        assert isinstance(learner.query_patterns, dict)
        
        print("✅ PatternLearner initialized successfully")
        
        # Test saving patterns (should create the file)
        learner.save_patterns()
        assert storage_path.exists(), "Storage file should be created after save"
        
        print("✅ Storage file created successfully")
        
        # Test loading from existing file
        learner2 = PatternLearner(storage_path=storage_path)
        assert learner2.storage_path == storage_path
        
        print("✅ PatternLearner loaded from existing file successfully")
        
        print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_storage_directory_creation()

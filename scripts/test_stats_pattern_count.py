#!/usr/bin/env python3
"""
Quick test to verify stats endpoint returns correct pattern count
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.polly import Polly

def test_stats_pattern_count():
    """Test that stats returns total pattern count (patterns + query_patterns)."""
    print("Testing stats pattern count...")
    
    # Initialize Polly (this loads existing patterns)
    polly = Polly()
    
    if not polly.pattern_learner:
        print("✗ Pattern learner not initialized")
        return False
    
    # Get counts
    conceptual_count = len(polly.pattern_learner.patterns)
    query_count = len(polly.pattern_learner.query_patterns)
    total_expected = conceptual_count + query_count
    
    print(f"\nPattern counts:")
    print(f"  Conceptual patterns: {conceptual_count}")
    print(f"  Query patterns: {query_count}")
    print(f"  Total expected: {total_expected}")
    
    # Get stats
    stats = polly.get_stats()
    stats_pattern_count = stats.get('patterns', 0)
    
    print(f"\nStats endpoint:")
    print(f"  Pattern count: {stats_pattern_count}")
    
    # Verify
    if stats_pattern_count == total_expected:
        print(f"\n✓ PASS: Stats returns correct total ({stats_pattern_count})")
        return True
    else:
        print(f"\n✗ FAIL: Expected {total_expected}, got {stats_pattern_count}")
        return False

if __name__ == "__main__":
    success = test_stats_pattern_count()
    sys.exit(0 if success else 1)

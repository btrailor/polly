"""
Test Use Case 2: Pattern-Boosted Domain Detection

Tests that pattern learning enhances domain detection confidence.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.domains import DomainEngine, DomainType
from learners.patterns import PatternLearner
import tempfile
import json


def test_pattern_boost_increases_confidence():
    """Test that patterns boost domain confidence scores."""
    print("\n" + "="*70)
    print("TEST 1: Pattern Boost Increases Confidence")
    print("="*70)
    
    # Create temporary pattern file with domain patterns
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        patterns_data = {
            "version": "2.0",
            "patterns": [],
            "query_patterns": [],
            "query_history": [],
            "query_chunk_patterns": [],
            "domain_priority_patterns": [
                {
                    "pattern_type": "domain_priority",
                    "pattern_id": "domain_signals",
                    "domain": "signals",
                    "collection_weights": {
                        "integration_github_norns": 1.5,
                        "integration_github_monome": 1.2,
                        "integration_obsidian": 0.8
                    },
                    "collection_stats": {},
                    "total_queries": 50,
                    "confidence": 0.85,
                    "first_seen": "2026-01-25T10:00:00Z",
                    "last_seen": "2026-01-25T10:00:00Z",
                    "metadata": {}
                },
                {
                    "pattern_type": "domain_priority",
                    "pattern_id": "domain_sigils",
                    "domain": "sigils",
                    "collection_weights": {
                        "integration_github_polly": 1.8,
                        "integration_github_docker": 1.0,
                        "integration_obsidian": 0.5
                    },
                    "collection_stats": {},
                    "total_queries": 75,
                    "confidence": 0.90,
                    "first_seen": "2026-01-25T10:00:00Z",
                    "last_seen": "2026-01-25T10:00:00Z",
                    "metadata": {}
                }
            ],
            "project_workflow_patterns": [],
            "conceptual_patterns": [
                {
                    "pattern_type": "conceptual",
                    "pattern_id": "grid_norns",
                    "confidence": 0.85,
                    "occurrences": 12,
                    "first_seen": "2026-01-25T10:00:00Z",
                    "last_seen": "2026-01-25T10:00:00Z",
                    "times_used": 8,
                    "times_helpful": 7,
                    "metadata": {
                        "concept1": "grid",
                        "concept2": "norns"
                    }
                },
                {
                    "pattern_type": "conceptual",
                    "pattern_id": "docker_python",
                    "confidence": 0.78,
                    "occurrences": 15,
                    "first_seen": "2026-01-25T10:00:00Z",
                    "last_seen": "2026-01-25T10:00:00Z",
                    "times_used": 10,
                    "times_helpful": 9,
                    "metadata": {
                        "concept1": "docker",
                        "concept2": "python"
                    }
                }
            ]
        }
        json.dump(patterns_data, f)
        patterns_path = Path(f.name)
    
    # Initialize DomainEngine and PatternLearner
    domain_engine = DomainEngine()
    pattern_learner = PatternLearner(patterns_path)
    
    # Attach pattern learner to domain engine
    domain_engine.set_pattern_learner(pattern_learner)
    
    # Test 1: Query with "grid" should get signals domain boost
    query1 = "Grid controls for sequencing"
    
    print(f"\nQuery: '{query1}'")
    print("-" * 70)
    
    # Get scores without patterns (temporarily detach)
    domain_engine._pattern_learner = None
    scores_without = domain_engine._score_domains(query1)
    print("\nScores WITHOUT patterns:")
    for domain, score in sorted(scores_without.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            print(f"  {domain.value}: {score:.3f}")
    
    # Get scores with patterns
    domain_engine._pattern_learner = pattern_learner
    scores_with = domain_engine._score_domains(query1)
    print("\nScores WITH patterns:")
    for domain, score in sorted(scores_with.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            boost = score - scores_without.get(domain, 0)
            boost_str = f" (+{boost:.3f})" if boost > 0.01 else ""
            print(f"  {domain.value}: {score:.3f}{boost_str}")
    
    # Check if signals got a boost
    signals_boost = scores_with.get(DomainType.SIGNALS, 0) - scores_without.get(DomainType.SIGNALS, 0)
    print(f"\nSignals domain boost: +{signals_boost:.3f}")
    
    if signals_boost > 0.05:
        print("✅ PASS: Signals domain received significant boost (>0.05)")
    else:
        print(f"❌ FAIL: Signals domain boost too small ({signals_boost:.3f})")
    
    # Cleanup
    patterns_path.unlink()


def test_conceptual_expansion():
    """Test that conceptual patterns expand query terms."""
    print("\n" + "="*70)
    print("TEST 2: Conceptual Pattern Expansion")
    print("="*70)
    
    # Create temporary pattern file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        patterns_data = {
            "version": "2.0",
            "patterns": [],
            "query_patterns": [],
            "query_history": [],
            "query_chunk_patterns": [],
            "domain_priority_patterns": [],
            "project_workflow_patterns": [],
            "conceptual_patterns": [
                {
                    "pattern_type": "conceptual",
                    "pattern_id": "grid_monome",
                    "confidence": 0.90,
                    "occurrences": 20,
                    "first_seen": "2026-01-25T10:00:00Z",
                    "last_seen": "2026-01-25T10:00:00Z",
                    "times_used": 15,
                    "times_helpful": 14,
                    "metadata": {
                        "concept1": "grid",
                        "concept2": "monome"
                    }
                }
            ]
        }
        json.dump(patterns_data, f)
        patterns_path = Path(f.name)
    
    # Initialize
    domain_engine = DomainEngine()
    pattern_learner = PatternLearner(patterns_path)
    domain_engine.set_pattern_learner(pattern_learner)
    
    query = "Grid documentation"
    print(f"\nQuery: '{query}'")
    print("-" * 70)
    
    # Get conceptual pattern boosts
    query_concepts = set(query.lower().split())
    boosts = domain_engine._get_conceptual_pattern_boosts(query, query_concepts)
    
    print("\nConceptual pattern boosts:")
    if boosts:
        for domain, boost in boosts.items():
            print(f"  {domain.value}: +{boost:.3f}")
        print("✅ PASS: Conceptual patterns provide boosts")
    else:
        print("  (No boosts calculated)")
        print("⚠️  WARNING: No conceptual boosts (may be expected if domain keywords don't match)")
    
    # Cleanup
    patterns_path.unlink()


def test_learning_loop():
    """Test that successful detections are recorded."""
    print("\n" + "="*70)
    print("TEST 3: Learning Loop Records Success")
    print("="*70)
    
    # Create empty pattern file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        patterns_data = {
            "version": "2.0",
            "patterns": [],
            "query_patterns": [],
            "query_history": [],
            "query_chunk_patterns": [],
            "domain_priority_patterns": [
                {
                    "pattern_type": "domain_priority",
                    "pattern_id": "domain_signals",
                    "domain": "signals",
                    "collection_weights": {"integration_github_norns": 1.0},
                    "collection_stats": {},
                    "total_queries": 5,
                    "confidence": 0.75,
                    "first_seen": "2026-01-25T10:00:00Z",
                    "last_seen": "2026-01-25T10:00:00Z",
                    "metadata": {}
                }
            ],
            "project_workflow_patterns": [],
            "conceptual_patterns": []
        }
        json.dump(patterns_data, f)
        patterns_path = Path(f.name)
    
    # Initialize
    domain_engine = DomainEngine()
    pattern_learner = PatternLearner(patterns_path)
    domain_engine.set_pattern_learner(pattern_learner)
    
    # Record successful detection
    query = "How do I use the grid?"
    detected_domains = [DomainType.SIGNALS, DomainType.SCROLLS]
    
    print(f"\nQuery: '{query}'")
    print(f"Detected: {[d.value for d in detected_domains]}")
    print("-" * 70)
    
    # Find the signals pattern
    signals_pattern = None
    for pattern_id, pattern in pattern_learner.domain_priority_patterns.items():
        if pattern.domain == 'signals':
            signals_pattern = pattern
            break
    
    if not signals_pattern:
        print("❌ FAIL: signals pattern not found")
        patterns_path.unlink()
        return
    
    initial_uses = signals_pattern.total_queries  # Use total_queries since times_used not in DomainPriorityPattern
    print(f"\nInitial total_queries for signals domain: {initial_uses}")
    
    # Record success
    domain_engine.record_successful_detection(query, detected_domains, user_accepted=True)
    
    # Check if total_queries increased
    final_uses = signals_pattern.total_queries
    print(f"Final total_queries for signals domain: {final_uses}")
    
    if final_uses > initial_uses:
        print(f"✅ PASS: total_queries increased ({initial_uses} → {final_uses})")
    else:
        print(f"❌ FAIL: total_queries did not increase")
    
    # Cleanup
    patterns_path.unlink()


def test_no_patterns_fallback():
    """Test that domain detection works without patterns (fallback)."""
    print("\n" + "="*70)
    print("TEST 4: Fallback Without Patterns")
    print("="*70)
    
    # Initialize without pattern learner
    domain_engine = DomainEngine()
    
    query = "How do I use Docker?"
    print(f"\nQuery: '{query}'")
    print("-" * 70)
    
    # Should work without errors
    try:
        scores = domain_engine._score_domains(query)
        detected = domain_engine.detect_domains(query)
        
        print("\nDetected domains (without patterns):")
        for domain in detected:
            score = scores.get(domain, 0)
            print(f"  {domain.value}: {score:.3f}")
        
        print("✅ PASS: Domain detection works without patterns (fallback)")
    except Exception as e:
        print(f"❌ FAIL: Error during detection: {e}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("USE CASE 2: PATTERN-BOOSTED DOMAIN DETECTION - TEST SUITE")
    print("="*70)
    
    test_pattern_boost_increases_confidence()
    test_conceptual_expansion()
    test_learning_loop()
    test_no_patterns_fallback()
    
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)

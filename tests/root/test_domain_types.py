#!/usr/bin/env python3
"""
Test domain type conversion in learners
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.domains import DomainType
from learners.patterns import PatternLearner, _domains_to_strings
from learners.graph import KnowledgeGraph, _domains_to_strings as graph_domains_to_strings

def test_domain_conversion():
    """Test that domain conversion works correctly."""
    print("Testing domain type conversion...")
    
    # Test with DomainType enums
    domains_enum = [DomainType.SIGILS, DomainType.SIGNALS]
    result1 = _domains_to_strings(domains_enum)
    print(f"✓ Enum input: {domains_enum} -> {result1}")
    assert result1 == ['sigils', 'signals'], f"Expected ['sigils', 'signals'], got {result1}"
    
    # Test with strings
    domains_str = ['sigils', 'signals']
    result2 = _domains_to_strings(domains_str)
    print(f"✓ String input: {domains_str} -> {result2}")
    assert result2 == ['sigils', 'signals'], f"Expected ['sigils', 'signals'], got {result2}"
    
    # Test with mixed (shouldn't happen but should handle)
    domains_mixed = [DomainType.SIGILS, 'signals']
    result3 = _domains_to_strings(domains_mixed)
    print(f"✓ Mixed input: {domains_mixed} -> {result3}")
    assert result3 == ['sigils', 'signals'], f"Expected ['sigils', 'signals'], got {result3}"
    
    # Test with empty
    result4 = _domains_to_strings([])
    print(f"✓ Empty input: [] -> {result4}")
    assert result4 == [], f"Expected [], got {result4}"
    
    # Test with None
    result5 = _domains_to_strings(None)
    print(f"✓ None input: None -> {result5}")
    assert result5 == [], f"Expected [], got {result5}"
    
    print("\n✅ All domain conversion tests passed!")
    return True

def test_pattern_learner():
    """Test PatternLearner with enum domains."""
    print("\nTesting PatternLearner with DomainType enums...")
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        learner = PatternLearner(temp_path)
        
        # Test with enum domains
        domains = [DomainType.SIGILS, DomainType.SIGNALS]
        learner.record_query("how do I use docker with norns", domains)
        print(f"✓ record_query with enums: {domains}")
        
        # Test get_relevant_patterns
        patterns = learner.get_relevant_patterns("docker", domains)
        print(f"✓ get_relevant_patterns with enums: {len(patterns)} patterns found")
        
        # Test cross_domain_pairs (should create string tuple)
        if learner.cross_domain_pairs:
            for pair, count in learner.cross_domain_pairs.items():
                print(f"✓ Cross-domain pair: {pair} (count: {count})")
                assert isinstance(pair[0], str), f"Expected string, got {type(pair[0])}"
                assert isinstance(pair[1], str), f"Expected string, got {type(pair[1])}"
        
        print("✅ PatternLearner tests passed!")
        return True
    finally:
        temp_path.unlink(missing_ok=True)

def test_knowledge_graph():
    """Test KnowledgeGraph with enum domains."""
    print("\nTesting KnowledgeGraph with DomainType enums...")
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        graph = KnowledgeGraph(temp_path)
        
        # Test with enum domains
        domains = [DomainType.SIGILS, DomainType.SIGNALS]
        entities = graph.extract_entities_from_text("I'm using docker and norns", domains)
        print(f"✓ extract_entities_from_text with enums: {len(entities)} entities")
        
        # Verify entities have string domains
        for entity in entities:
            print(f"  - {entity.name}: domains={entity.domains}")
            for d in entity.domains:
                assert isinstance(d, str), f"Expected string domain, got {type(d)}"
        
        # Test get_context_for_query
        context = graph.get_context_for_query("docker norns", domains)
        print(f"✓ get_context_for_query with enums: {len(context)} chars")
        
        print("✅ KnowledgeGraph tests passed!")
        return True
    finally:
        temp_path.unlink(missing_ok=True)

if __name__ == "__main__":
    try:
        success = (
            test_domain_conversion() and
            test_pattern_learner() and
            test_knowledge_graph()
        )
        
        if success:
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED! Domain type handling is fixed.")
            print("="*60)
            sys.exit(0)
        else:
            print("\n❌ Some tests failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

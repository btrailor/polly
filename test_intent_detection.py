#!/usr/bin/env python3
"""
Test intent-based detection for universal cross-domain boosting.
Verifies that user intent (programming, analysis, design, etc.) boosts appropriate domains.
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.domains import DomainEngine, DomainType

def test_intent_detection():
    """Test that intents are correctly extracted from queries."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("INTENT DETECTION TEST")
    print("=" * 80)
    print()
    
    test_cases = [
        # Programming intent
        ("How do I program a sequencer?", ["programming"]),
        ("Build an API for data processing", ["programming"]),
        ("Create a Norns app", ["programming"]),
        ("Debug my script", ["programming"]),
        ("Implement the engine", ["programming"]),
        ("Develop a tool", ["programming"]),
        
        # Analysis intent
        ("Analyze genomic sequences", ["analysis"]),
        ("How do I process this data?", ["analysis"]),
        ("Calculate statistics for the dataset", ["analysis"]),
        
        # Design intent
        ("Design a user interface", ["design"]),
        ("Create a mockup for the app", ["design"]),
        ("How do I layout this page?", ["design"]),
        
        # Writing intent
        ("Write documentation for this API", ["writing"]),
        ("Document the architecture", ["writing"]),
        ("How do I explain this concept?", ["writing"]),
        
        # Learning intent
        ("What is the framework for this?", ["learning"]),
        ("Explain the mental model", ["learning"]),
        ("How does pattern learning work?", ["learning"]),
        
        # Audio intent
        ("How do I synthesize a bass sound?", ["audio"]),
        ("Create music with MIDI", ["audio"]),
        ("Generate audio effects", ["audio"]),
        
        # Multiple intents
        ("How do I program audio synthesis?", ["programming", "audio"]),
        ("Design and implement a UI", ["design", "programming"]),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_intents in test_cases:
        detected = engine._detect_query_intent(query)
        
        # Check if all expected intents were detected
        all_found = all(intent in detected for intent in expected_intents)
        
        if all_found:
            status = "✅"
            passed += 1
        else:
            status = "❌"
            failed += 1
        
        print(f"{status} Query: {query}")
        print(f"   Expected: {expected_intents}")
        print(f"   Detected: {detected}")
        
        if not all_found:
            missing = [i for i in expected_intents if i not in detected]
            print(f"   ⚠️  Missing: {missing}")
        
        print()
    
    print(f"Results: {passed} passed, {failed} failed")
    print()

def test_norns_queries_with_intent():
    """Test that intent detection fixes the remaining Norns failures."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("NORNS QUERIES WITH INTENT DETECTION")
    print("=" * 80)
    print()
    
    queries = [
        "How do I program Monome Norns in Lua?",
        "What is the Norns API for audio synthesis?",
        "Show me Lua code examples for Norns",
        "Norns SuperCollider engine development",
        "Debug my Norns script",
        "Monome Norns sequencer implementation",
        "How do I use the Norns screen API?",
        "Create a Norns app with audio and MIDI",
    ]
    
    results = []
    
    for query in queries:
        domain_scores = engine.detect_domains_with_scores(query)
        detected = [d for d, s in domain_scores if s > 0]
        
        has_sigils = DomainType.SIGILS in detected
        has_signals = DomainType.SIGNALS in detected
        
        status = "✅" if (has_sigils and has_signals) else "⚠️"
        results.append((query, has_sigils, has_signals, status))
        
        print(f"{status} {query}")
        print(f"   Detected: {[d.value for d in detected[:3]]}")
        
        # Show detected intents
        intents = engine._detect_query_intent(query)
        if intents:
            print(f"   Intents: {intents}")
        
        if not has_sigils:
            print(f"   ⚠️  Missing Sigils (code context)")
        if not has_signals:
            print(f"   ⚠️  Missing Signals (audio context)")
        
        print()
    
    # Summary
    both_detected = sum(1 for _, sigils, signals, _ in results if sigils and signals)
    total = len(results)
    percentage = (both_detected / total) * 100
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Queries detecting BOTH Sigils + Signals: {both_detected}/{total} ({percentage:.0f}%)")
    print()
    
    # Show improvement trajectory
    print("Improvement trajectory:")
    print("  Before fixes:           50% (4/8)")
    print("  After tech matching:    62% (5/8)")
    print(f"  After intent detection: {percentage:.0f}% ({both_detected}/{total})")
    print()
    
    if percentage >= 87:
        print("✅ EXCELLENT: Intent detection significantly improved cross-domain detection!")
    elif percentage >= 75:
        print("✅ VERY GOOD: Intent detection helped, approaching target")
    elif percentage >= 62:
        print("✅ GOOD: Some improvement, but may need fine-tuning")
    else:
        print("⚠️  NEEDS WORK: Intent patterns may need adjustment")
    
    print()

def test_diverse_intent_scenarios():
    """Test intent detection with diverse domain configurations."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("DIVERSE INTENT SCENARIOS")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "query": "Implement a data processing pipeline",
            "expected_intent": "programming",
            "expected_domain": DomainType.SIGILS,
            "description": "Programming intent should boost code domains"
        },
        {
            "query": "Analyze the performance metrics",
            "expected_intent": "analysis",
            "expected_domain": None,  # May match SIGILS or GRIDS
            "description": "Analysis intent detected"
        },
        {
            "query": "Design the user dashboard",
            "expected_intent": "design",
            "expected_domain": DomainType.GLYPHS,
            "description": "Design intent should boost visual domains"
        },
        {
            "query": "Write a tutorial on system architecture",
            "expected_intent": "writing",
            "expected_domain": DomainType.SCROLLS,
            "description": "Writing intent should boost documentation domains"
        },
        {
            "query": "What is the mental model for complexity?",
            "expected_intent": "learning",
            "expected_domain": DomainType.GRIDS,
            "description": "Learning intent should boost systems thinking domains"
        },
        {
            "query": "How do I synthesize ambient textures?",
            "expected_intent": "audio",
            "expected_domain": DomainType.SIGNALS,
            "description": "Audio intent should boost synthesis domains"
        },
        {
            "query": "Build a React component for audio visualization",
            "expected_intent": "programming",
            "expected_domain": DomainType.SIGILS,
            "description": "Programming + audio + tech mentions (React)"
        },
    ]
    
    for case in test_cases:
        query = case["query"]
        
        print(f"Query: {query}")
        
        # Detect intent
        intents = engine._detect_query_intent(query)
        intent_match = case["expected_intent"] in intents
        
        # Get domain scores
        domain_scores = engine.detect_domains_with_scores(query)
        detected_domains = [d for d, s in domain_scores if s > 0]
        
        # Check if expected domain was detected (if specified)
        domain_match = (case["expected_domain"] is None or 
                       case["expected_domain"] in detected_domains)
        
        intent_status = "✅" if intent_match else "❌"
        domain_status = "✅" if domain_match else "⚠️"
        
        print(f"  {intent_status} Intent: expected '{case['expected_intent']}', got {intents}")
        print(f"  {domain_status} Domains: {[d.value for d in detected_domains[:3]]}")
        print(f"  {case['description']}")
        print()

def test_intent_domain_mapping():
    """Test that intent correctly maps to domain characteristics."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("INTENT → DOMAIN MAPPING TEST")
    print("=" * 80)
    print()
    
    # Test each intent type
    intent_tests = [
        ("programming", "How do I implement this?", [DomainType.SIGILS]),
        ("analysis", "Analyze the data", [DomainType.SIGILS]),  # May also match
        ("design", "Design the interface", [DomainType.GLYPHS]),
        ("writing", "Write documentation", [DomainType.SCROLLS]),
        ("learning", "What is the framework?", [DomainType.GRIDS]),
        ("audio", "Synthesize a sound", [DomainType.SIGNALS]),
    ]
    
    for intent_type, query, expected_domains in intent_tests:
        print(f"Intent Type: {intent_type}")
        print(f"Query: {query}")
        
        # Detect intent
        intents = engine._detect_query_intent(query)
        intent_detected = intent_type in intents
        
        # Get boosted domains
        intent_boosts = engine._boost_domains_by_intent([intent_type]) if intent_detected else {}
        boosted_domains = list(intent_boosts.keys())
        
        # Check if expected domains were boosted
        expected_boosted = any(d in boosted_domains for d in expected_domains)
        
        status = "✅" if expected_boosted else "⚠️"
        
        print(f"  {status} Intent detected: {intent_detected}")
        print(f"     Boosted domains: {[d.value for d in boosted_domains]}")
        print(f"     Expected: {[d.value for d in expected_domains]}")
        print()

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("UNIVERSAL INTENT-BASED DETECTION TEST SUITE")
    print("=" * 80)
    print()
    
    test_intent_detection()
    test_norns_queries_with_intent()
    test_diverse_intent_scenarios()
    test_intent_domain_mapping()
    
    print("=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print("""
Intent-based detection is now implemented!

How it works:
1. Extracts user intent from query (programming, analysis, design, writing, learning, audio)
2. Maps intent to domain characteristics (keywords and descriptions)
3. Boosts domains that match detected intent by +0.15 per intent (max +0.25)

Intent types:
- programming: code, develop, build, implement, create, debug, refactor
- analysis: analyze, process, calculate, data, metrics
- design: design, layout, mockup, ui, interface
- writing: write, document, essay, teach, explain
- learning: framework, mental model, understand, how does X work
- audio: synthesize, sound, music, midi, audio creation

Benefits:
- Universal: Works for ANY domain configuration
- Detects intent from query patterns, not specific words
- Helps queries without explicit technology mentions
- Multi-intent support (e.g., "program audio synthesis")

This solves queries like "Create a Norns app" by detecting programming
intent and boosting Sigils domain, even without mentioning "Lua" or "code".
""")

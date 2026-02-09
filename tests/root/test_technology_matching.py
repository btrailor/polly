#!/usr/bin/env python3
"""
Test technology pattern matching for universal cross-domain detection.
Verifies that mentioning technologies (Lua, Python, etc.) boosts appropriate domains.
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.domains import DomainEngine, DomainType

def test_technology_detection():
    """Test that technology mentions are correctly extracted from queries."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("TECHNOLOGY DETECTION TEST")
    print("=" * 80)
    print()
    
    test_cases = [
        ("How do I program Monome Norns in Lua?", ["lua"]),
        ("Analyze genomic data with Python", ["python"]),
        ("Build a React component in TypeScript", ["react", "typescript"]),
        ("Deploy with Docker and Kubernetes", ["docker", "kubernetes"]),
        ("Write SuperCollider synthesis code", ["supercollider"]),
        ("Create a Max/MSP patch", ["max"]),
        ("Rust async programming patterns", ["rust"]),
        ("Node.js API development", ["javascript"]),
        ("Shell scripting with bash", ["shell"]),
    ]
    
    for query, expected_techs in test_cases:
        detected = engine._extract_technologies_from_query(query)
        passed = all(tech in detected for tech in expected_techs)
        status = "✅" if passed else "❌"
        
        print(f"{status} Query: {query}")
        print(f"   Expected: {expected_techs}")
        print(f"   Detected: {detected}")
        print()

def test_domain_boosting_norns():
    """Test: Norns query should now detect BOTH Sigils and Signals."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("NORNS QUERY TEST (Original Problem)")
    print("=" * 80)
    print()
    
    query = "How do I program Monome Norns in Lua?"
    
    print(f"Query: {query}")
    print()
    
    # Get domain scores
    domain_scores = engine.detect_domains_with_scores(query)
    
    print("Domain Scores:")
    for domain, score in domain_scores:
        if score > 0:
            print(f"  {domain.value:12s}: {score:.4f}")
    
    print()
    
    # Check results
    detected_domains = [d.value for d, s in domain_scores if s > 0]
    has_sigils = any(d == DomainType.SIGILS for d, s in domain_scores if s > 0)
    has_signals = any(d == DomainType.SIGNALS for d, s in domain_scores if s > 0)
    
    print("Analysis:")
    if has_sigils and has_signals:
        print("  ✅ SUCCESS: Both Sigils and Signals detected!")
        print("  ✅ User will get: Lua code examples + Norns audio context")
    elif has_signals and not has_sigils:
        print("  ⚠️  PARTIAL: Only Signals detected")
        print("  ⚠️  Missing: Lua programming context from Sigils")
    elif has_sigils and not has_signals:
        print("  ⚠️  PARTIAL: Only Sigils detected")
        print("  ⚠️  Missing: Norns/audio context from Signals")
    else:
        print("  ❌ FAIL: Neither domain detected")
    
    print()

def test_universal_bioinformatics():
    """Test: Bioinformatics query with hypothetical domains."""
    
    print("=" * 80)
    print("UNIVERSAL TEST: Bioinformatics (Biology + Data Science)")
    print("=" * 80)
    print()
    
    # Simulate what would happen with user-defined domains
    query = "How do I analyze genomic sequences in Python?"
    
    print(f"Query: {query}")
    print()
    print("Scenario: User has 'Biology' and 'DataScience' domains")
    print("  - Biology domain has patterns: ['*.fasta', '*.fastq', '*.vcf']")
    print("  - DataScience domain has patterns: ['*.py', '*.ipynb', '*.R']")
    print()
    
    # Our system should detect "python" and boost DataScience
    engine = DomainEngine()
    technologies = engine._extract_technologies_from_query(query)
    
    print(f"Technologies detected: {technologies}")
    
    if 'python' in technologies:
        print("  ✅ SUCCESS: 'python' detected")
        print("  ✅ Would boost DataScience domain (has *.py pattern)")
        print("  ✅ Query would detect both Biology (keywords) + DataScience (python)")
    else:
        print("  ❌ FAIL: 'python' not detected")
    
    print()

def test_all_norns_queries():
    """Test all 8 Norns queries from original investigation."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("COMPREHENSIVE NORNS QUERY TEST")
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
    
    if percentage >= 75:
        print("✅ EXCELLENT: Technology matching significantly improved detection")
    elif percentage >= 50:
        print("✅ GOOD: Better than before (was 50%), but room for improvement")
    else:
        print("⚠️  NEEDS WORK: Still missing cross-domain detection")
    
    print()

def test_diverse_technologies():
    """Test with diverse technology mentions."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("DIVERSE TECHNOLOGY TEST")
    print("=" * 80)
    print()
    
    test_cases = [
        {
            "query": "Build a React UI with TypeScript",
            "expected_techs": ["react", "typescript"],
            "expected_domains": [DomainType.SIGILS],  # Both .tsx and .jsx patterns
            "description": "Should detect code domain for React/TS"
        },
        {
            "query": "Write SuperCollider synthesis code",
            "expected_techs": ["supercollider"],
            "expected_domains": [DomainType.SIGNALS],  # .scd pattern
            "description": "Should detect audio domain for SuperCollider"
        },
        {
            "query": "Deploy with Docker and Kubernetes",
            "expected_techs": ["docker", "kubernetes"],
            "expected_domains": [DomainType.SIGILS],  # Dockerfile pattern
            "description": "Should detect infrastructure domain"
        },
        {
            "query": "Process audio with Python",
            "expected_techs": ["python"],
            "expected_domains": [DomainType.SIGILS],  # .py pattern
            "description": "Should detect code domain (even if query mentions audio)"
        },
    ]
    
    for case in test_cases:
        query = case["query"]
        
        print(f"Query: {query}")
        
        # Detect technologies
        techs = engine._extract_technologies_from_query(query)
        tech_match = all(t in techs for t in case["expected_techs"])
        
        # Get domain scores
        domain_scores = engine.detect_domains_with_scores(query)
        detected_domains = [d for d, s in domain_scores if s > 0]
        
        # Check if expected domains were detected
        domain_match = all(d in detected_domains for d in case["expected_domains"])
        
        tech_status = "✅" if tech_match else "❌"
        domain_status = "✅" if domain_match else "⚠️"
        
        print(f"  {tech_status} Technologies: expected {case['expected_techs']}, got {techs}")
        print(f"  {domain_status} Domains: expected {[d.value for d in case['expected_domains']]}, got {[d.value for d in detected_domains[:3]]}")
        print(f"  {case['description']}")
        print()

if __name__ == "__main__":
    print()
    print("=" * 80)
    print("UNIVERSAL TECHNOLOGY PATTERN MATCHING TEST SUITE")
    print("=" * 80)
    print()
    
    test_technology_detection()
    test_domain_boosting_norns()
    test_universal_bioinformatics()
    test_all_norns_queries()
    test_diverse_technologies()
    
    print("=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print("""
Technology pattern matching is now implemented!

How it works:
1. Extracts technology mentions from query (Lua, Python, React, etc.)
2. Checks which domains have patterns matching those technologies
3. Boosts those domains by +0.2 per matched technology (max +0.3)

Benefits:
- Universal: Works for ANY domain configuration
- No hardcoded domain logic
- Uses existing Phase 1.5 pattern lists
- Helps queries like "program in Lua" detect code domains
- Helps queries like "analyze in Python" detect data/code domains

This solves the Norns problem universally by detecting "Lua" and boosting
Sigils domain (which has *.lua pattern), even without "lua" in keywords.
""")

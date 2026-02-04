#!/usr/bin/env python3
"""
Test script to diagnose domain detection for cross-domain queries like "Monome Norns"
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.domains import DomainEngine, DomainType

def test_domain_detection():
    """Test how domain detection handles Norns-related queries."""
    
    engine = DomainEngine()
    
    # Test queries with varying emphasis
    test_queries = [
        "How do I program Monome Norns in Lua?",
        "What is the Norns API for audio synthesis?",
        "Show me Lua code examples for Norns",
        "Norns SuperCollider engine development",
        "Debug my Norns script",
        "Monome Norns sequencer implementation",
        "How do I use the Norns screen API?",
        "Create a Norns app with audio and MIDI",
    ]
    
    print("=" * 80)
    print("DOMAIN DETECTION TEST: Monome Norns Queries")
    print("=" * 80)
    print()
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 80)
        
        # Get domains with scores
        domain_scores = engine.detect_domains_with_scores(query)
        
        # Show all domains with non-zero scores
        print("Domain Scores:")
        for domain, score in domain_scores:
            if score > 0:
                print(f"  {domain.value:12s}: {score:.4f}")
        
        # Show what would be detected
        detected = engine.detect_domains(query)
        detected_names = [d.value for d in detected if d != DomainType.UNKNOWN]
        print(f"\nDetected Domains: {detected_names}")
        
        # Analysis
        has_sigils = any(d == DomainType.SIGILS for d in detected)
        has_signals = any(d == DomainType.SIGNALS for d in detected)
        
        if has_signals and not has_sigils:
            print("⚠️  WARNING: Only Signals detected - code-related content may be missed")
        elif has_sigils and not has_signals:
            print("⚠️  WARNING: Only Sigils detected - audio-related content may be missed")
        elif has_sigils and has_signals:
            print("✅ GOOD: Both Sigils and Signals detected")
        else:
            print("❌ ERROR: Neither domain detected")
        
        print()
        print()

def test_keyword_coverage():
    """Analyze keyword coverage for Norns-related terms."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("KEYWORD COVERAGE ANALYSIS")
    print("=" * 80)
    print()
    
    # Norns-related terms that should match
    norns_terms = [
        "norns", "monome", "lua", "script", "engine", "supercollider",
        "audio", "synthesis", "midi", "screen", "encoder", "key",
        "program", "code", "api", "app", "sequencer"
    ]
    
    sigils_domain = engine.domains[DomainType.SIGILS]
    signals_domain = engine.domains[DomainType.SIGNALS]
    
    print("Sigils Keywords:", ", ".join(sigils_domain.keywords))
    print()
    print("Signals Keywords:", ", ".join(signals_domain.keywords))
    print()
    print("-" * 80)
    print()
    
    print(f"{'Term':<20} {'Sigils':<10} {'Signals':<10} {'Coverage'}")
    print("-" * 60)
    
    for term in norns_terms:
        in_sigils = term.lower() in [kw.lower() for kw in sigils_domain.keywords]
        in_signals = term.lower() in [kw.lower() for kw in signals_domain.keywords]
        
        sigils_mark = "✓" if in_sigils else "✗"
        signals_mark = "✓" if in_signals else "✗"
        
        if in_sigils and in_signals:
            coverage = "Both"
        elif in_signals:
            coverage = "Signals only"
        elif in_sigils:
            coverage = "Sigils only"
        else:
            coverage = "⚠️  MISSING"
        
        print(f"{term:<20} {sigils_mark:<10} {signals_mark:<10} {coverage}")
    
    print()

def test_pattern_matching():
    """Test file pattern matching for .lua files."""
    
    engine = DomainEngine()
    
    print("=" * 80)
    print("FILE PATTERN MATCHING TEST")
    print("=" * 80)
    print()
    
    test_files = [
        "script.lua",
        "norns_app.lua",
        "engine.scd",
        "lib/music_util.lua",
    ]
    
    sigils_domain = engine.domains[DomainType.SIGILS]
    signals_domain = engine.domains[DomainType.SIGNALS]
    
    print(f"{'Filename':<25} {'Sigils':<10} {'Signals':<10}")
    print("-" * 50)
    
    for filename in test_files:
        sigils_match = sigils_domain.matches_filename(filename)
        signals_match = signals_domain.matches_filename(filename)
        
        sigils_mark = "✓" if sigils_match else "✗"
        signals_mark = "✓" if signals_match else "✗"
        
        print(f"{filename:<25} {sigils_mark:<10} {signals_mark:<10}")
    
    print()
    print("Note: .lua files match BOTH domains in file patterns")
    print("But query text like 'lua' only matches if it's in keywords list")
    print()

if __name__ == "__main__":
    test_domain_detection()
    test_keyword_coverage()
    test_pattern_matching()

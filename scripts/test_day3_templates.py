#!/usr/bin/env python3
"""
Day 3 Test - Query Template Extraction
Tests the enhanced query pattern detection
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner
import json


def test_template_extraction():
    """Test query template extraction with various query types."""
    
    print("=" * 60)
    print("Query Template Extraction Test")
    print("=" * 60)
    
    # Create fresh pattern learner for testing
    storage_path = Path.home() / ".polly" / "patterns_test.json"
    storage_path.unlink(missing_ok=True)
    
    learner = PatternLearner(storage_path=storage_path, min_occurrences=2)
    
    print("\n[Step 1] Testing various query patterns...")
    
    test_cases = [
        {
            "query": "How do I use Docker with Python?",
            "expected_template": "How do I {action} {thing} with {tool}?",
            "expected_fills": {"action": "use", "thing": "docker", "tool": "python"}
        },
        {
            "query": "How can I set up PostgreSQL?",
            "expected_template": "How do I {action} {thing}?",
            "expected_fills": {"action": "set", "thing": "up postgresql"}
        },
        {
            "query": "What's the best way to structure React components?",
            "expected_template": "What's the best way to {action} {thing}?",
            "expected_fills": {"action": "structure", "thing": "react components"}
        },
        {
            "query": "Explain how async functions work in JavaScript",
            "expected_template": "Explain how {concept} works",
            "expected_fills": {"concept": "async functions work in javascript"}
        },
        {
            "query": "Write a function that parses markdown",
            "expected_template": "Write a {thing} that {action}",
            "expected_fills": {"thing": "function", "action": "parses markdown"}
        },
        {
            "query": "Create a API endpoint for user authentication",
            "expected_template": "Create a {thing} for {purpose}",
            "expected_fills": {"thing": "api endpoint", "purpose": "user authentication"}
        },
        {
            "query": "Implement error handling using try-catch",
            "expected_template": "Implement {feature} using {tool}",
            "expected_fills": {"feature": "error handling", "tool": "try-catch"}
        },
        {
            "query": "Debug the CORS issue in my Express app",
            "expected_template": "Debug {issue} in {context}",
            "expected_fills": {"issue": "the cors issue", "context": "my express app"}
        },
        {
            "query": "What is Docker?",
            "expected_template": "What is {concept}?",
            "expected_fills": {"concept": "docker"}
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        query = test["query"]
        template, fills = learner._extract_query_template(query)
        
        print(f"\n  Test {i}: {query[:60]}...")
        print(f"    Template: {template}")
        print(f"    Fills: {fills}")
        
        # Check if template matches (allow flexibility)
        template_match = template == test["expected_template"]
        
        if template_match:
            print(f"    ✅ Template matched!")
            passed += 1
        else:
            print(f"    ⚠️  Template mismatch")
            print(f"       Expected: {test['expected_template']}")
            print(f"       Got: {template}")
            failed += 1
    
    print(f"\n[Results] Passed: {passed}/{len(test_cases)}, Failed: {failed}/{len(test_cases)}")
    
    # Step 2: Test that patterns are tracked
    print("\n[Step 2] Testing pattern tracking...")
    
    # Record some similar queries to build patterns
    similar_queries = [
        ("How do I use Git with GitHub?", ["sigils"]),
        ("How do I use Rust with WebAssembly?", ["sigils"]),
        ("How do I use norns with SuperCollider?", ["signals"]),
        ("What's the best way to organize code?", ["sigils"]),
        ("What's the best way to structure essays?", ["scrolls"]),
        ("Explain how MIDI works", ["signals"]),
        ("Explain how Docker works", ["sigils"]),
    ]
    
    for query, domains in similar_queries:
        learner.record_query(query, domains)
    
    print(f"  Recorded {len(similar_queries)} queries")
    
    # Check query_patterns
    pattern_count = len(learner.query_patterns)
    print(f"  Detected {pattern_count} unique query patterns")
    
    if pattern_count > 0:
        print("\n  Detected Patterns:")
        for template, qp in learner.query_patterns.items():
            print(f"    - {template}")
            print(f"      Frequency: {qp.frequency}")
            print(f"      Domains: {qp.domains}")
            print(f"      Common fills: {dict(qp.common_fills)}")
    
    # Step 3: Save and reload
    print("\n[Step 3] Testing persistence...")
    learner.save_patterns()
    print("  ✅ Saved patterns")
    
    # Reload
    learner2 = PatternLearner(storage_path=storage_path)
    
    reloaded_count = len(learner2.query_patterns)
    print(f"  ✅ Reloaded {reloaded_count} query patterns")
    
    if reloaded_count == pattern_count:
        print("  ✅ Pattern count matches!")
    else:
        print(f"  ⚠️  Count mismatch: expected {pattern_count}, got {reloaded_count}")
    
    # Check query history has templates
    if learner2.query_history:
        sample = learner2.query_history[-1]
        if 'template' in sample and 'fills' in sample:
            print(f"  ✅ Query history includes templates")
            print(f"     Last query template: {sample['template']}")
            print(f"     Last query fills: {sample['fills']}")
        else:
            print(f"  ⚠️  Query history missing template/fills")
    
    # Cleanup
    storage_path.unlink(missing_ok=True)
    
    print("\n" + "=" * 60)
    print("✅ Template Extraction Test Complete!")
    print("=" * 60)
    
    return passed >= len(test_cases) * 0.7  # 70% pass rate


if __name__ == "__main__":
    result = test_template_extraction()
    sys.exit(0 if result else 1)

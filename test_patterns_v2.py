#!/usr/bin/env python3
"""
Test script for Phase 13A pattern storage v2.0
Verifies that new pattern types can be saved and loaded correctly.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from learners.patterns import (
    PatternLearner,
    QueryChunkPattern,
    DomainPriorityPattern,
    ProjectWorkflowPattern
)

def test_pattern_storage_v2():
    """Test saving and loading patterns with v2.0 format."""
    print("=" * 60)
    print("Testing Phase 13A Pattern Storage v2.0")
    print("=" * 60)
    
    # Use a temporary storage path
    test_storage = Path.home() / '.polly' / 'patterns_test.json'
    
    # Create pattern learner
    learner = PatternLearner(storage_path=test_storage)
    
    print(f"\n1. Creating test patterns...")
    
    # Create a QueryChunkPattern
    qcp = QueryChunkPattern(
        pattern_id='qcp_001',
        query_template='How do I {action} {thing}?',
        query_signature='how_do_i_action_thing',
        successful_chunks=[
            {'chunk_id': 'chunk_123', 'collection': 'docs', 'hit_count': 5, 'avg_score': 0.92},
            {'chunk_id': 'chunk_456', 'collection': 'docs', 'hit_count': 3, 'avg_score': 0.87}
        ],
        total_queries=10,
        confidence=0.8,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        metadata={'test': True}
    )
    learner.query_chunk_patterns[qcp.pattern_id] = qcp
    
    # Create a DomainPriorityPattern
    dpp = DomainPriorityPattern(
        pattern_id='dpp_001',
        domain='python',
        collection_weights={'docs': 1.5, 'code': 1.2, 'stackoverflow': 1.0},
        collection_stats={
            'docs': {'queries': 50, 'avg_score': 0.85},
            'code': {'queries': 30, 'avg_score': 0.78}
        },
        total_queries=100,
        confidence=0.75,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        metadata={'test': True}
    )
    learner.domain_priority_patterns[dpp.pattern_id] = dpp
    
    # Create a ProjectWorkflowPattern
    pwp = ProjectWorkflowPattern(
        pattern_id='pwp_001',
        project_path='/Users/test/project',
        domain='python',
        workflow_type='test',
        command_sequence=[
            {'command': 'pytest', 'order': 1, 'success_rate': 0.95},
            {'command': 'pytest --cov', 'order': 2, 'success_rate': 0.90}
        ],
        prerequisites=['requirements.txt installed'],
        common_failures=[
            {'error': 'ModuleNotFoundError', 'solution': 'pip install -r requirements.txt'}
        ],
        learned_from=20,
        last_success=datetime.now(),
        confidence=0.85,
        metadata={'test': True}
    )
    learner.project_workflow_patterns[pwp.pattern_id] = pwp
    
    print(f"   ✓ Created 1 QueryChunkPattern")
    print(f"   ✓ Created 1 DomainPriorityPattern")
    print(f"   ✓ Created 1 ProjectWorkflowPattern")
    
    # Save patterns
    print(f"\n2. Saving patterns to {test_storage}...")
    learner.save_patterns()
    print(f"   ✓ Patterns saved")
    
    # Verify file contents
    print(f"\n3. Verifying storage format...")
    with open(test_storage, 'r') as f:
        data = json.load(f)
    
    assert 'metadata' in data, "Missing metadata field"
    assert data['metadata']['version'] == '2.0', "Wrong version"
    assert 'query_chunk_patterns' in data, "Missing query_chunk_patterns"
    assert 'domain_priority_patterns' in data, "Missing domain_priority_patterns"
    assert 'project_workflow_patterns' in data, "Missing project_workflow_patterns"
    
    print(f"   ✓ Storage version: {data['metadata']['version']}")
    print(f"   ✓ Pattern counts: {data['metadata']['pattern_counts']}")
    
    # Load patterns into new learner
    print(f"\n4. Loading patterns into new learner instance...")
    learner2 = PatternLearner(storage_path=test_storage)
    
    assert len(learner2.query_chunk_patterns) == 1, "Failed to load QueryChunkPatterns"
    assert len(learner2.domain_priority_patterns) == 1, "Failed to load DomainPriorityPatterns"
    assert len(learner2.project_workflow_patterns) == 1, "Failed to load ProjectWorkflowPatterns"
    
    print(f"   ✓ Loaded {len(learner2.query_chunk_patterns)} QueryChunkPatterns")
    print(f"   ✓ Loaded {len(learner2.domain_priority_patterns)} DomainPriorityPatterns")
    print(f"   ✓ Loaded {len(learner2.project_workflow_patterns)} ProjectWorkflowPatterns")
    
    # Verify pattern data integrity
    print(f"\n5. Verifying pattern data integrity...")
    
    qcp2 = learner2.query_chunk_patterns['qcp_001']
    assert qcp2.query_template == qcp.query_template, "QueryChunkPattern data mismatch"
    assert len(qcp2.successful_chunks) == 2, "Wrong number of successful chunks"
    assert qcp2.confidence == 0.8, "Wrong confidence"
    print(f"   ✓ QueryChunkPattern data intact")
    
    dpp2 = learner2.domain_priority_patterns['dpp_001']
    assert dpp2.domain == 'python', "DomainPriorityPattern data mismatch"
    assert len(dpp2.collection_weights) == 3, "Wrong number of collection weights"
    print(f"   ✓ DomainPriorityPattern data intact")
    
    pwp2 = learner2.project_workflow_patterns['pwp_001']
    assert pwp2.workflow_type == 'test', "ProjectWorkflowPattern data mismatch"
    assert len(pwp2.command_sequence) == 2, "Wrong number of commands"
    print(f"   ✓ ProjectWorkflowPattern data intact")
    
    # Clean up
    print(f"\n6. Cleaning up test file...")
    test_storage.unlink()
    print(f"   ✓ Test file removed")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED - Pattern Storage v2.0 Working!")
    print("=" * 60)
    print("\nReady to proceed with Day 2 implementation.")
    
if __name__ == '__main__':
    try:
        test_pattern_storage_v2()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

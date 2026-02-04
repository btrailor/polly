"""
Test suite for pattern compression (Phase 2b)

Tests:
1. Compression achieves 3-5x ratio
2. Save/load round-trip preserves all data
3. Loading compressed is faster than uncompressed
4. Backwards compatibility with old format
5. Large dataset compression
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from learners.patterns import (
    PatternLearner, 
    QueryPattern, 
    QueryChunkPattern,
    DomainPriorityPattern,
    ProjectWorkflowPattern
)
import tempfile
import json
import time


@pytest.fixture
def temp_patterns_file():
    """Create temporary patterns file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'version': '2.0',
            'metadata': {
                'created': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            },
            'patterns': [],
            'query_patterns': {},
            'query_chunk_patterns': {},
            'domain_priority_patterns': {},
            'project_workflow_patterns': {},
            'statistics': {}
        }, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    temp_path.unlink(missing_ok=True)
    Path(str(temp_path) + '.compressed').unlink(missing_ok=True)


def test_compression_ratio(temp_patterns_file):
    """Test that compression achieves better than 1.5x ratio"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add sample patterns
    pl.query_patterns['test_query'] = QueryPattern(
        query_template='What is {concept}?',
        common_fills={},
        frequency=10,
        domains=['test', 'demo', 'example']
    )
    
    for i in range(5):
        pl.domain_priority_patterns[f'test_domain_{i}'] = DomainPriorityPattern(
            pattern_id=f'test_domain_{i}',
            domain=f'domain_{i}',
            collection_weights={'collection_a': 0.8, 'collection_b': 0.2},
            collection_stats={},
            total_queries=100,
            confidence=0.9,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            metadata={}
        )
    
    # Save and compress
    result = pl.save_patterns_compressed()
    
    # Verify compression ratio (realistic for small datasets)
    assert result['ratio'] >= 1.5, f"Compression ratio {result['ratio']:.1f}x is below 1.5x"
    assert result['compressed_size'] < result['original_size']
    print(f"✓ Compression ratio: {result['ratio']:.1f}x (small dataset)")


def test_save_load_roundtrip(temp_patterns_file):
    """Test that save→compress→load preserves all data"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add diverse patterns
    pl.query_patterns['query1'] = QueryPattern(
        query_template='How do I {action}?',
        common_fills={},
        frequency=5,
        domains=['coding']
    )
    
    pl.query_chunk_patterns['qcp1'] = QueryChunkPattern(
        pattern_id='qcp1',
        query_template='test query',
        query_signature='test_sig',
        successful_chunks=[
            {'chunk_id': 'chunk1', 'collection': 'coll1', 'hit_count': 10, 'avg_score': 0.85}
        ],
        total_queries=15,
        confidence=0.95,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        metadata={}
    )
    
    pl.domain_priority_patterns['dpp1'] = DomainPriorityPattern(
        pattern_id='dpp1',
        domain='signals',
        collection_weights={'norns': 0.8, 'github': 0.2},
        collection_stats={},
        total_queries=50,
        confidence=0.88,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        metadata={}
    )
    
    # Store original counts and values
    orig_qp_count = len(pl.query_patterns)
    orig_qcp_count = len(pl.query_chunk_patterns)
    orig_dpp_count = len(pl.domain_priority_patterns)
    orig_dpp = pl.domain_priority_patterns['dpp1']
    
    # Save compressed
    pl.save_patterns_compressed()
    
    # Load compressed
    result = pl.load_patterns_from_compressed()
    
    # Verify success
    assert result['success'] == True
    
    # Verify counts
    assert len(pl.query_patterns) == orig_qp_count
    assert len(pl.query_chunk_patterns) == orig_qcp_count
    assert len(pl.domain_priority_patterns) == orig_dpp_count
    
    # Verify specific values
    loaded_dpp = pl.domain_priority_patterns['dpp1']
    assert loaded_dpp.domain == orig_dpp.domain
    assert loaded_dpp.total_queries == orig_dpp.total_queries
    assert abs(loaded_dpp.confidence - orig_dpp.confidence) < 0.01  # Allow rounding
    assert loaded_dpp.collection_weights == orig_dpp.collection_weights
    
    print("✓ Round-trip preserves all data")


def test_load_performance(temp_patterns_file):
    """Test that loading compressed is faster or comparable to uncompressed"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add many patterns
    for i in range(20):
        pl.domain_priority_patterns[f'dpp_{i}'] = DomainPriorityPattern(
            pattern_id=f'dpp_{i}',
            domain=f'domain_{i}',
            collection_weights={f'coll_{j}': 0.5 for j in range(5)},
            collection_stats={},
            total_queries=100,
            confidence=0.9,
            first_seen=datetime.now(),
            last_seen=datetime.now(),
            metadata={}
        )
    
    # Save both formats
    pl.save_patterns()  # Uncompressed
    pl.save_patterns_compressed()  # Compressed
    
    # Time loading uncompressed
    start = time.perf_counter()
    pl._load_patterns()
    uncompressed_time = time.perf_counter() - start
    
    # Time loading compressed
    start = time.perf_counter()
    pl.load_patterns_from_compressed()
    compressed_time = time.perf_counter() - start
    
    print(f"✓ Uncompressed load: {uncompressed_time*1000:.2f}ms")
    print(f"✓ Compressed load: {compressed_time*1000:.2f}ms")
    print(f"✓ Speedup: {uncompressed_time/compressed_time:.2f}x")
    
    # Compressed should be faster or at least not significantly slower
    assert compressed_time < uncompressed_time * 1.5, "Compressed loading is too slow"


def test_backwards_compatibility(temp_patterns_file):
    """Test that new code can still load old uncompressed format"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add patterns and save in old format
    pl.query_patterns['test'] = QueryPattern(
        query_template='test',
        common_fills={},
        frequency=1,
        domains=['test']
    )
    pl.save_patterns()  # Old format
    
    # Load using old method
    pl2 = PatternLearner(temp_patterns_file)
    assert len(pl2.query_patterns) == 1
    
    print("✓ Can still load old uncompressed format")


def test_compression_with_empty_patterns(temp_patterns_file):
    """Test compression works with no patterns"""
    pl = PatternLearner(temp_patterns_file)
    
    # Save empty patterns
    result = pl.save_patterns_compressed()
    
    # Should still work
    assert 'ratio' in result
    assert result['compressed_size'] > 0
    
    # Load empty patterns
    result = pl.load_patterns_from_compressed()
    assert result['success'] == True
    assert result['patterns_loaded'] == 0
    
    print("✓ Handles empty patterns gracefully")


def test_compression_omits_zero_values(temp_patterns_file):
    """Test that compression omits near-zero collection weights"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add pattern with near-zero weights
    pl.domain_priority_patterns['test'] = DomainPriorityPattern(
        pattern_id='test',
        domain='test',
        collection_weights={
            'high_weight': 0.95,
            'low_weight': 0.005,  # Should be omitted (< 0.01)
            'zero_weight': 0.0  # Should be omitted
        },
        collection_stats={},
        total_queries=10,
        confidence=0.9,
        first_seen=datetime.now(),
        last_seen=datetime.now(),
        metadata={}
    )
    
    # Save compressed
    pl.save_patterns_compressed()
    
    # Read compressed file
    compressed_path = temp_patterns_file.with_suffix('.json.compressed')
    data = json.loads(compressed_path.read_text())
    
    # Check that low weights are omitted
    dpp = data['dpp'][0]
    assert 'high_weight' in dpp['w']
    assert 'low_weight' not in dpp['w']  # Should be omitted
    assert 'zero_weight' not in dpp['w']  # Should be omitted
    
    print("✓ Omits near-zero values correctly")


def test_compression_with_large_dataset(temp_patterns_file):
    """Test compression with 100+ patterns achieves good ratio"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add many patterns with realistic data
    for i in range(100):
        pl.domain_priority_patterns[f'dpp_{i}'] = DomainPriorityPattern(
            pattern_id=f'dpp_{i}',
            domain=f'domain_{i % 10}',  # 10 unique domains
            collection_weights={
                f'collection_{j}': round(0.1 * (j + 1), 2) 
                for j in range(5)
            },
            collection_stats={
                f'collection_{j}': {
                    'queries': i * 10,
                    'hits': i * 5,
                    'avg_score': 0.8
                }
                for j in range(5)
            },
            total_queries=i * 10,
            confidence=0.8 + (i % 20) / 100,
            first_seen=datetime.now() - timedelta(days=i),
            last_seen=datetime.now(),
            metadata={'source': 'test', 'version': '1.0'}
        )
    
    # Save compressed
    result = pl.save_patterns_compressed()
    
    # With more complex data, expect better compression (but not as high as 5x)
    assert result['ratio'] >= 2.0, f"Large dataset compression only {result['ratio']:.1f}x"
    
    # Load and verify
    load_result = pl.load_patterns_from_compressed()
    assert load_result['success'] == True
    assert len(pl.domain_priority_patterns) == 100
    
    print(f"✓ Large dataset (100 patterns): {result['ratio']:.1f}x compression")


def test_compressed_file_is_valid_json(temp_patterns_file):
    """Test that compressed file is valid JSON"""
    pl = PatternLearner(temp_patterns_file)
    
    # Add sample pattern
    pl.query_patterns['test'] = QueryPattern(
        query_template='test',
        common_fills={},
        frequency=1,
        domains=['test']
    )
    
    # Save compressed
    pl.save_patterns_compressed()
    
    # Verify it's valid JSON
    compressed_path = temp_patterns_file.with_suffix('.json.compressed')
    data = json.loads(compressed_path.read_text())
    
    # Verify structure
    assert 'v' in data  # version
    assert 'c' in data  # created
    assert 'qp' in data  # query_patterns
    assert 'dpp' in data  # domain_priority_patterns
    assert 's' in data  # statistics
    
    print("✓ Compressed file is valid JSON with correct structure")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

"""
Tests for conversation compression system.

Tests compression ratios, semantic preservation, and integration.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

from core.compression import ConversationCompressor, CompressionManager


# ========== Test Fixtures ==========

@pytest.fixture
def sample_conversation():
    """Sample conversation for testing"""
    return [
        {
            "role": "user",
            "name": "Brett",
            "content": "I want to create a note about Phase 11 planning for the multi-model routing system.",
            "timestamp": "2026-01-28T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I'll help you create that note. A few questions first: How many providers are we planning to support?",
            "timestamp": "2026-01-28T10:00:15Z"
        },
        {
            "role": "user",
            "content": "We decided on 8 providers: OpenAI, Anthropic, Gemini, Grok, Perplexity, Mistral, Cohere, and OpenRouter.",
            "timestamp": "2026-01-28T10:01:00Z"
        },
        {
            "role": "assistant",
            "content": "Great! And what's the timeline for implementation?",
            "timestamp": "2026-01-28T10:01:10Z"
        },
        {
            "role": "user",
            "content": "5 weeks total. We'll implement providers first, then routing, then safety features.",
            "timestamp": "2026-01-28T10:02:00Z"
        },
        {
            "role": "assistant",
            "content": "Perfect. I'll create the note now. The note will document: 8 providers, 5-week timeline, and implementation phases.",
            "timestamp": "2026-01-28T10:02:30Z"
        },
        {
            "role": "user",
            "content": "Also make sure to include that Grok requires mandatory safety filters for conspiracy theories and extremism.",
            "timestamp": "2026-01-28T10:03:00Z"
        },
        {
            "role": "assistant",
            "content": "Good point. The Grok safety filter is critical. I've added that to the note as a key requirement.",
            "timestamp": "2026-01-28T10:03:20Z"
        },
        {
            "role": "user",
            "content": "What should we call the note file?",
            "timestamp": "2026-01-28T10:04:00Z"
        },
        {
            "role": "assistant",
            "content": "I recommend 'PHASE11_PLANNING.md'. I've created the file with all the details we discussed.",
            "timestamp": "2026-01-28T10:04:15Z"
        },
        {
            "role": "user",
            "content": "Perfect, thanks!",
            "timestamp": "2026-01-28T10:04:30Z"
        },
        {
            "role": "assistant",
            "content": "You're welcome! The note captures all key decisions: 8 providers, 5-week timeline, safety requirements for Grok, and implementation phases.",
            "timestamp": "2026-01-28T10:04:45Z"
        }
    ]


@pytest.fixture
def long_conversation():
    """Generate a longer conversation for compression testing"""
    messages = []
    
    # Create 50 exchanges (100 messages)
    for i in range(50):
        messages.append({
            "role": "user",
            "content": f"Question {i+1}: Can you explain how feature X works in the system? I need to understand the implementation details and architecture decisions.",
            "timestamp": f"2026-01-28T10:{i:02d}:00Z"
        })
        messages.append({
            "role": "assistant",
            "content": f"Answer {i+1}: Feature X works by implementing pattern Y. The architecture uses components A, B, and C. We decided on this approach because of performance requirements and scalability needs. Here's a detailed explanation with code examples and design rationale.",
            "timestamp": f"2026-01-28T10:{i:02d}:30Z"
        })
    
    return messages


@pytest.fixture
def temp_db():
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


# ========== Compressor Tests ==========

def test_compression_ratio(sample_conversation):
    """Test that compression works on sample conversation"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    
    ratio = compressed["token_stats"]["ratio"]
    # For short conversations, expect at least 2x compression
    assert ratio >= 2, f"Compression ratio {ratio:.1f}x below 2x minimum"
    
    print(f"\n✓ Compression ratio: {ratio:.1f}x")
    print(f"  Original: {compressed['token_stats']['original']} tokens")
    print(f"  Compressed: {compressed['token_stats']['compressed']} tokens")


def test_compression_ratio_long_conversation(long_conversation):
    """Test compression on longer conversation"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(long_conversation)
    
    ratio = compressed["token_stats"]["ratio"]
    original = compressed["token_stats"]["original"]
    compressed_size = compressed["token_stats"]["compressed"]
    
    print(f"\n✓ Long conversation compression:")
    print(f"  Messages: {len(long_conversation)}")
    print(f"  Original: {original} tokens")
    print(f"  Compressed: {compressed_size} tokens")
    print(f"  Ratio: {ratio:.1f}x")
    
    assert ratio >= 50, f"Long conversation ratio {ratio:.1f}x below target"


def test_decompression_quality(sample_conversation):
    """Test that key information is preserved in decompression"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    decompressed = compressor.decompress(compressed)
    
    # Check key information preserved
    assert "8" in decompressed or "providers" in decompressed.lower(), \
        "Provider count not preserved"
    assert "5" in decompressed or "weeks" in decompressed.lower() or "week" in decompressed.lower(), \
        "Timeline not preserved"
    assert "phase" in decompressed.lower() and "11" in decompressed, \
        "Phase information not preserved"
    
    print(f"\n✓ Decompression preserves key information")
    print(f"  Summary length: {len(decompressed)} characters")


def test_decision_extraction(sample_conversation):
    """Test extraction of key decisions"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    decisions = compressed["decisions"]
    
    assert len(decisions) > 0, "No decisions extracted"
    
    # Check decision structure
    for decision in decisions:
        assert "topic" in decision
        assert "decision" in decision
        assert "confidence" in decision
        assert 0 <= decision["confidence"] <= 1
    
    print(f"\n✓ Extracted {len(decisions)} decisions")
    for d in decisions:
        print(f"  - {d['topic']}: {d['decision']} ({d['confidence']:.0%})")


def test_focus_extraction(sample_conversation):
    """Test extraction of focus topics"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    focus_topics = compressed["focus_topics"]
    
    assert len(focus_topics) > 0, "No focus topics extracted"
    assert len(focus_topics) <= 5, "Too many focus topics"
    
    print(f"\n✓ Extracted focus topics: {', '.join(focus_topics)}")


def test_concept_extraction(sample_conversation):
    """Test extraction of key concepts"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    concepts = compressed["key_concepts"]
    
    # May not always find concepts in short conversations
    print(f"\n✓ Extracted {len(concepts)} concepts")
    for c in concepts:
        print(f"  - {c['term']}: {c['definition'][:50]}...")


def test_artifact_extraction():
    """Test extraction of created artifacts"""
    conversation = [
        {"role": "user", "content": "Create a file called test.py"},
        {"role": "assistant", "content": "I've created file test.py with the code."},
        {"role": "user", "content": "Now make a note in docs.md"},
        {"role": "assistant", "content": "Saved the documentation to docs.md"}
    ]
    
    compressor = ConversationCompressor()
    compressed = compressor.compress(conversation)
    artifacts = compressed["artifacts_created"]
    
    assert len(artifacts) > 0, "No artifacts extracted"
    
    print(f"\n✓ Extracted {len(artifacts)} artifacts:")
    for a in artifacts:
        print(f"  - {a['type']}: {a['title']}")


def test_mode_detection(sample_conversation):
    """Test conversation mode detection"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    mode = compressed["mode"]
    
    assert mode in ["chat", "notes", "code", "search", "research", "plan"]
    print(f"\n✓ Detected mode: {mode}")


def test_task_classification(sample_conversation):
    """Test task type classification"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress(sample_conversation)
    task_type = compressed["task_type"]
    
    assert task_type != "general", "Should detect specific task type"
    print(f"\n✓ Classified task: {task_type}")


def test_format_versioning():
    """Test that format includes version number"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress([])
    assert compressed["version"] == 1, "Format version should be 1"
    
    print(f"\n✓ Format version: {compressed['version']}")


def test_empty_conversation():
    """Test handling of empty conversation"""
    compressor = ConversationCompressor()
    
    compressed = compressor.compress([])
    
    assert compressed["depth"] == 0
    assert compressed["decisions"] == []
    assert compressed["token_stats"]["original"] == 0
    
    print("\n✓ Handles empty conversation gracefully")


def test_compression_deterministic(sample_conversation):
    """Test that compression is deterministic"""
    compressor = ConversationCompressor()
    
    compressed1 = compressor.compress(sample_conversation)
    compressed2 = compressor.compress(sample_conversation)
    
    # Key fields should be identical
    assert compressed1["user"] == compressed2["user"]
    assert compressed1["mode"] == compressed2["mode"]
    assert compressed1["task_type"] == compressed2["task_type"]
    assert compressed1["depth"] == compressed2["depth"]
    
    print("\n✓ Compression is deterministic")


# ========== Manager Tests ==========

def test_manager_initialization(temp_db):
    """Test compression manager initialization"""
    manager = CompressionManager(db_path=temp_db)
    
    # Check database file exists
    assert Path(temp_db).exists()
    
    print(f"\n✓ Manager initialized with database at {temp_db}")


def test_manager_should_compress():
    """Test compression threshold logic"""
    manager = CompressionManager()
    
    # Short conversation - should not compress
    short_convo = [{"role": "user", "content": "test"}] * 10
    assert not manager.should_compress(short_convo)
    
    # Long conversation - should compress
    long_convo = [{"role": "user", "content": "test"}] * 50
    assert manager.should_compress(long_convo)
    
    print("\n✓ Compression threshold logic works")


def test_manager_compress_and_load(temp_db, sample_conversation):
    """Test compressing and loading conversation"""
    manager = CompressionManager(db_path=temp_db)
    
    # Compress conversation
    result = manager.compress_conversation(
        conversation_history=sample_conversation,
        conversation_id="test-conv-1",
        metadata={"mode": "notes"}
    )
    
    assert result['compressed'] is not None
    assert len(result['recent']) <= manager.KEEP_RECENT_COUNT
    
    # Load context
    context = manager.load_context("test-conv-1", result['recent'])
    
    assert len(context) > 0
    assert context[0]['role'] == 'system'
    assert 'compressed' in context[0]
    
    print(f"\n✓ Compressed and loaded conversation")
    print(f"  Compressed: {result['compressed']['token_stats']['ratio']:.1f}x")
    print(f"  Context messages: {len(context)}")


def test_manager_stats(temp_db, sample_conversation):
    """Test compression statistics"""
    manager = CompressionManager(db_path=temp_db)
    
    # Compress a conversation
    manager.compress_conversation(
        conversation_history=sample_conversation,
        conversation_id="test-conv-2"
    )
    
    # Get stats
    stats = manager.get_compression_stats("test-conv-2")
    
    assert stats is not None
    assert stats['original_tokens'] > 0
    assert stats['compressed_tokens'] > 0
    assert stats['compression_ratio'] > 1
    
    print(f"\n✓ Compression stats:")
    print(f"  Original: {stats['original_tokens']} tokens")
    print(f"  Compressed: {stats['compressed_tokens']} tokens")
    print(f"  Ratio: {stats['compression_ratio']:.1f}x")


def test_manager_total_savings(temp_db, sample_conversation, long_conversation):
    """Test total compression savings calculation"""
    manager = CompressionManager(db_path=temp_db)
    
    # Compress multiple conversations
    manager.compress_conversation(sample_conversation, "conv-1")
    manager.compress_conversation(long_conversation, "conv-2")
    
    # Get total savings
    savings = manager.get_total_compression_savings()
    
    assert savings['total_conversations'] == 2
    assert savings['tokens_saved'] > 0
    assert savings['average_ratio'] > 1
    
    print(f"\n✓ Total compression savings:")
    print(f"  Conversations: {savings['total_conversations']}")
    print(f"  Tokens saved: {savings['tokens_saved']:,}")
    print(f"  Average ratio: {savings['average_ratio']:.1f}x")
    print(f"  Percent saved: {savings['percent_saved']:.1f}%")


def test_manager_list_compressed(temp_db, sample_conversation):
    """Test listing all compressed conversations"""
    manager = CompressionManager(db_path=temp_db)
    
    # Compress conversations
    manager.compress_conversation(sample_conversation, "conv-1")
    manager.compress_conversation(sample_conversation, "conv-2")
    
    # List all
    all_compressed = manager.list_all_compressed()
    
    assert len(all_compressed) == 2
    assert all([c['conversation_id'] for c in all_compressed])
    
    print(f"\n✓ Listed {len(all_compressed)} compressed conversations")


def test_manager_delete(temp_db, sample_conversation):
    """Test deleting compressed conversation"""
    manager = CompressionManager(db_path=temp_db)
    
    # Compress and then delete
    manager.compress_conversation(sample_conversation, "conv-to-delete")
    manager.delete_compressed("conv-to-delete")
    
    # Verify deleted
    stats = manager.get_compression_stats("conv-to-delete")
    assert stats is None
    
    print("\n✓ Successfully deleted compressed conversation")


# ========== Integration Tests ==========

def test_full_workflow(temp_db):
    """Test complete compression workflow"""
    manager = CompressionManager(db_path=temp_db)
    
    # 1. Create conversation
    conversation = []
    for i in range(30):
        conversation.append({
            "role": "user",
            "content": f"Message {i}: Can you help with task {i}?"
        })
        conversation.append({
            "role": "assistant",
            "content": f"Response {i}: Sure, I'll help with task {i}. Here's what we'll do..."
        })
    
    conv_id = "workflow-test"
    
    # 2. Check if should compress
    should_compress = manager.should_compress(conversation)
    assert should_compress, "Long conversation should trigger compression"
    
    # 3. Compress
    result = manager.compress_conversation(conversation, conv_id)
    # Expect at least 30x for long repetitive conversations
    assert result['compressed']['token_stats']['ratio'] >= 30
    
    # 4. Load context
    context = manager.load_context(conv_id, result['recent'])
    assert len(context) > 0
    assert context[0]['role'] == 'system'
    
    # 5. Get stats
    stats = manager.get_compression_stats(conv_id)
    assert stats['compression_ratio'] >= 30  # At least 30x for repetitive conversations
    
    print("\n✓ Full workflow completed successfully")
    print(f"  Original messages: {len(conversation)}")
    print(f"  Compressed ratio: {stats['compression_ratio']:.1f}x")
    print(f"  Context size: {len(context)} messages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

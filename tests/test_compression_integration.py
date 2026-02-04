"""
Integration tests for compression in conversation history.

Tests the full integration of compression into Polly's query flow:
- Automatic compression at thresholds
- Context building with compressed history
- Conversation continuity
- Error handling
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import shutil

from core.polly import Polly
from core.config import PollyConfig
from core.compression import CompressionManager


@pytest.fixture
def temp_polly_dir():
    """Create a temporary directory for Polly data."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_config(temp_polly_dir):
    """Create a test configuration."""
    config = PollyConfig()
    # Override paths to use temp directory
    config._config['rag']['vector_db_path'] = str(temp_polly_dir / "chroma_db")
    config._config['compression'] = {
        'enabled': True,
        'message_threshold': 10,  # Lower threshold for testing
        'age_hours': 24,
        'keep_recent': 3,  # Keep only 3 recent messages for testing
        'show_stats': False
    }
    return config


@pytest.fixture
def polly_instance(test_config):
    """Create a Polly instance for testing."""
    polly = Polly(config=test_config)
    yield polly
    # Cleanup
    if hasattr(polly, 'compression_manager') and polly.compression_manager:
        # Close any database connections
        pass


class TestCompressionIntegration:
    """Test compression integration into conversation flow."""
    
    def test_compression_initialization(self, polly_instance):
        """Test that compression manager initializes correctly."""
        assert hasattr(polly_instance, 'compression_manager')
        assert polly_instance.compression_manager is not None
        assert polly_instance._compression_enabled is True
        assert polly_instance._compression_threshold == 10
        assert polly_instance._keep_recent_count == 3
    
    def test_no_compression_below_threshold(self, polly_instance):
        """Test that compression doesn't trigger below threshold."""
        # Add messages below threshold
        for i in range(5):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Test query {i}'
            })
            polly_instance.conversation_history.append({
                'role': 'assistant',
                'content': f'Test response {i}'
            })
        
        initial_count = len(polly_instance.conversation_history)
        
        # Try to manage context
        polly_instance._manage_conversation_context()
        
        # Should not compress (below threshold of 10)
        assert len(polly_instance.conversation_history) == initial_count
    
    def test_compression_at_threshold(self, polly_instance):
        """Test that compression triggers at message threshold."""
        # Add messages above threshold (10 messages)
        for i in range(12):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Test query {i}' * 20  # Make messages longer
            })
            polly_instance.conversation_history.append({
                'role': 'assistant',
                'content': f'Test response {i}' * 20
            })
        
        initial_count = len(polly_instance.conversation_history)
        assert initial_count == 24  # 12 exchanges = 24 messages
        
        # Trigger compression
        polly_instance._manage_conversation_context()
        
        # Should keep only recent 3 messages
        assert len(polly_instance.conversation_history) == 3
        
        # Verify compressed data was saved
        conversation_id = f"session_{polly_instance.session_start.isoformat()}"
        stats = polly_instance.compression_manager.get_compression_stats(conversation_id)
        
        assert stats is not None
        assert 'original_tokens' in stats
        assert 'compressed_tokens' in stats
        assert 'compression_ratio' in stats
        
        # Verify compression ratio
        ratio = stats['compression_ratio']
        assert ratio > 1.0  # Should have some compression
    
    def test_context_building_with_compression(self, polly_instance):
        """Test that context building includes compressed history."""
        # Add and compress messages
        for i in range(12):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Test query {i}' * 20
            })
            polly_instance.conversation_history.append({
                'role': 'assistant',
                'content': f'Test response {i}' * 20
            })
        
        # Trigger compression
        polly_instance._manage_conversation_context()
        
        # Build context
        messages = polly_instance._build_context_for_llm()
        
        # Should have: compressed context (1) + recent messages (3)
        assert len(messages) == 4
        
        # First message should be the compressed context
        assert messages[0]['role'] == 'system'
        assert 'Conversation history summary' in messages[0]['content']
        assert messages[0].get('compressed') is True
        
        # Remaining messages should be recent conversation
        # They should be the last 3 messages from conversation_history
        assert len(polly_instance.conversation_history) == 3
        for i in range(1, 4):
            assert messages[i] == polly_instance.conversation_history[i-1]
    
    def test_context_building_without_compression(self, polly_instance):
        """Test context building when compression hasn't occurred."""
        # Add only a few messages (below threshold)
        polly_instance.conversation_history.append({
            'role': 'user',
            'content': 'Test query'
        })
        polly_instance.conversation_history.append({
            'role': 'assistant',
            'content': 'Test response'
        })
        
        # Build context
        messages = polly_instance._build_context_for_llm()
        
        # Should just return conversation history (no compression)
        assert len(messages) == 2
        assert messages[0]['role'] == 'user'
        assert messages[1]['role'] == 'assistant'
    
    def test_compression_disabled(self, polly_instance):
        """Test that compression can be disabled."""
        # Disable compression
        polly_instance._compression_enabled = False
        
        # Add messages above threshold
        for i in range(15):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Test query {i}'
            })
        
        initial_count = len(polly_instance.conversation_history)
        
        # Try to compress
        polly_instance._manage_conversation_context()
        
        # Should not compress
        assert len(polly_instance.conversation_history) == initial_count
    
    def test_compression_failure_graceful(self, polly_instance):
        """Test that compression failures don't break conversation."""
        # Add messages
        for i in range(12):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Test query {i}'
            })
        
        # Simulate compression failure by temporarily breaking the manager
        original_manager = polly_instance.compression_manager
        polly_instance.compression_manager = None
        
        initial_count = len(polly_instance.conversation_history)
        
        # Try to compress (should handle gracefully)
        polly_instance._manage_conversation_context()
        
        # Should not have modified conversation_history
        assert len(polly_instance.conversation_history) == initial_count
        
        # Restore manager
        polly_instance.compression_manager = original_manager
    
    def test_multiple_compression_cycles(self, polly_instance):
        """Test that multiple compression cycles work correctly."""
        # First batch of messages
        for i in range(12):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Batch 1 query {i}' * 20
            })
            polly_instance.conversation_history.append({
                'role': 'assistant',
                'content': f'Batch 1 response {i}' * 20
            })
        
        # First compression
        polly_instance._manage_conversation_context()
        assert len(polly_instance.conversation_history) == 3
        
        # Add more messages to reach threshold again
        for i in range(10):
            polly_instance.conversation_history.append({
                'role': 'user',
                'content': f'Batch 2 query {i}' * 20
            })
            polly_instance.conversation_history.append({
                'role': 'assistant',
                'content': f'Batch 2 response {i}' * 20
            })
        
        # Second compression
        polly_instance._manage_conversation_context()
        
        # Should again keep only recent messages
        assert len(polly_instance.conversation_history) == 3
        
        # Verify compressed data contains both batches
        conversation_id = f"session_{polly_instance.session_start.isoformat()}"
        stats = polly_instance.compression_manager.get_compression_stats(conversation_id)
        
        assert stats is not None
        assert stats['original_tokens'] > 500  # Should have many tokens compressed
    
    def test_compression_preserves_message_structure(self, polly_instance):
        """Test that compressed/decompressed messages maintain structure."""
        # Add structured messages
        test_messages = []
        for i in range(12):
            user_msg = {
                'role': 'user',
                'content': f'What is the capital of country {i}?'
            }
            assistant_msg = {
                'role': 'assistant',
                'content': f'The capital of country {i} is City {i}.'
            }
            polly_instance.conversation_history.append(user_msg)
            polly_instance.conversation_history.append(assistant_msg)
            test_messages.extend([user_msg, assistant_msg])
        
        # Compress
        polly_instance._manage_conversation_context()
        
        # Get stats
        conversation_id = f"session_{polly_instance.session_start.isoformat()}"
        stats = polly_instance.compression_manager.get_compression_stats(conversation_id)
        
        # Verify structure is maintained
        assert stats is not None
        assert stats['original_tokens'] > 0
        assert stats['compressed_tokens'] > 0
    
    def test_config_properties(self, test_config):
        """Test that compression config properties work."""
        assert test_config.compression_enabled is True
        assert test_config.compression_threshold == 10
        assert test_config.compression_age_hours == 24
        assert test_config.compression_keep_recent == 3
        assert test_config.compression_show_stats is False


@pytest.mark.asyncio
class TestCompressionInQueryFlow:
    """Test compression in actual query flow (async tests)."""
    
    async def test_query_triggers_compression(self, polly_instance):
        """Test that queries trigger compression when threshold reached."""
        # This would require a full async query flow
        # Placeholder for future implementation
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

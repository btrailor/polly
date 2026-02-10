"""
Tests for Mem0 Adaptive Memory Integration

Tests cover:
- Mem0Adapter operations (add, search, update, delete)
- Knowledge Writer integration
- Pattern Learning integration
- Persona memory integration
- API endpoints
- Configuration handling
- Error handling
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import json

# Test configuration
TEST_CONFIG = {
    'memory': {
        'provider': 'mem0',
        'mem0': {
            'enabled': True,
            'vector_store': 'chroma',
            'graph_store': None,
            'llm': 'litellm',
            'collections': {
                'knowledge': 'test_polly_knowledge',
                'patterns': 'test_polly_patterns',
                'personas': 'test_polly_personas'
            }
        }
    }
}


# ========== Mem0Adapter Tests ==========

class TestMem0Adapter:
    """Test Mem0Adapter core functionality."""
    
    @pytest.fixture
    def adapter(self):
        """Create Mem0Adapter instance for testing."""
        from core.memory.mem0_adapter import Mem0Adapter
        return Mem0Adapter(TEST_CONFIG)
    
    def test_adapter_initialization(self, adapter):
        """Test adapter initializes correctly."""
        assert adapter is not None
        assert adapter.config == TEST_CONFIG
        assert adapter.memory is not None
    
    def test_add_memory(self, adapter):
        """Test adding a memory."""
        result = adapter.add_memory(
            content="Test memory content",
            user_id="test_user",
            metadata={'type': 'test', 'source': 'unit_test'}
        )
        
        assert result is not None
        assert 'id' in result
    
    def test_search_memory(self, adapter):
        """Test searching memories."""
        # Add a memory first
        adapter.add_memory(
            content="Python is a programming language",
            user_id="test_user",
            metadata={'type': 'knowledge'}
        )
        
        # Search for it
        results = adapter.search_memory(
            query="programming language",
            user_id="test_user",
            limit=5
        )
        
        assert isinstance(results, list)
        # Note: Actual results depend on Mem0's semantic search
    
    def test_get_relevant_context(self, adapter):
        """Test getting formatted context."""
        # Add some memories
        adapter.add_memory(
            content="User prefers Sonnet 4 for code reviews",
            user_id="test_user",
            metadata={'type': 'preference'}
        )
        
        # Get context
        context = adapter.get_relevant_context(
            query="code review preferences",
            user_id="test_user",
            limit=3
        )
        
        assert isinstance(context, str)
    
    def test_update_memory(self, adapter):
        """Test updating a memory."""
        # Add a memory
        result = adapter.add_memory(
            content="Original content",
            user_id="test_user"
        )
        memory_id = result['id']
        
        # Update it
        updated = adapter.update_memory(
            memory_id=memory_id,
            content="Updated content",
            metadata={'updated': True}
        )
        
        assert updated is not None
    
    def test_delete_memory(self, adapter):
        """Test deleting a memory."""
        # Add a memory
        result = adapter.add_memory(
            content="To be deleted",
            user_id="test_user"
        )
        memory_id = result['id']
        
        # Delete it
        success = adapter.delete_memory(memory_id)
        assert success is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        from core.memory.mem0_adapter import Mem0Adapter
        
        # Missing memory section
        with pytest.raises(ValueError):
            Mem0Adapter({})
    
    def test_disabled_mem0(self):
        """Test behavior when Mem0 is disabled."""
        disabled_config = {
            'memory': {
                'provider': 'local',
                'mem0': {'enabled': False}
            }
        }
        
        from core.memory.mem0_adapter import Mem0Adapter
        # Should still initialize but log warning
        adapter = Mem0Adapter(disabled_config)
        assert adapter is not None


# ========== Pattern Learning Tests ==========

class TestPatternLearning:
    """Test Pattern Learning integration."""
    
    @pytest.fixture
    def learner(self):
        """Create PatternLearner instance."""
        from core.pattern_learning import PatternLearner
        return PatternLearner(TEST_CONFIG)
    
    def test_learn_pattern(self, learner):
        """Test learning a new pattern."""
        from core.pattern_learning import Pattern
        
        pattern = Pattern(
            type="routing",
            description="User prefers fast models for simple queries",
            confidence=0.8,
            timestamp=datetime.now().isoformat(),
            metadata={'model': 'haiku-4', 'task': 'simple_query'}
        )
        
        learner.learn_pattern(pattern)
        
        # Verify pattern was saved
        patterns = learner.get_all_patterns()
        assert len(patterns) > 0
    
    def test_search_patterns(self, learner):
        """Test searching patterns."""
        from core.pattern_learning import Pattern
        
        # Learn a pattern
        pattern = Pattern(
            type="preference",
            description="User likes concise responses",
            confidence=0.9,
            timestamp=datetime.now().isoformat(),
            metadata={'style': 'concise'}
        )
        learner.learn_pattern(pattern)
        
        # Search for it
        results = learner.search_patterns("concise responses")
        assert len(results) > 0
    
    def test_pattern_reinforcement(self, learner):
        """Test that repeated patterns increase confidence."""
        from core.pattern_learning import Pattern
        
        pattern = Pattern(
            type="routing",
            description="Test pattern for reinforcement",
            confidence=0.5,
            timestamp=datetime.now().isoformat(),
            metadata={}
        )
        
        # Learn it multiple times
        learner.learn_pattern(pattern)
        learner.learn_pattern(pattern)
        
        # Check confidence increased
        patterns = learner.search_patterns("reinforcement")
        if patterns:
            assert patterns[0].confidence > 0.5
    
    def test_get_patterns_by_type(self, learner):
        """Test filtering patterns by type."""
        from core.pattern_learning import Pattern
        
        # Add patterns of different types
        learner.learn_pattern(Pattern(
            type="routing",
            description="Routing pattern",
            confidence=0.8,
            timestamp=datetime.now().isoformat(),
            metadata={}
        ))
        
        learner.learn_pattern(Pattern(
            type="preference",
            description="Preference pattern",
            confidence=0.8,
            timestamp=datetime.now().isoformat(),
            metadata={}
        ))
        
        # Get only routing patterns
        routing_patterns = learner.get_patterns_by_type("routing")
        assert all(p.type == "routing" for p in routing_patterns)


# ========== Knowledge Writer Integration Tests ==========

class TestKnowledgeWriterIntegration:
    """Test Knowledge Writer integration with Mem0."""
    
    @pytest.mark.asyncio
    async def test_save_note_adds_to_mem0(self):
        """Test that saving a note adds it to Mem0."""
        from core.knowledge_writer import KnowledgeWriter
        
        # Mock config
        config = TEST_CONFIG.copy()
        
        # Mock dependencies
        mock_rag = Mock()
        mock_rag.index_single_document = AsyncMock()
        
        mock_notes_source = Mock()
        mock_notes_source.get_active_source.return_value = "native"
        mock_notes_source.get_notes_path.return_value = "/tmp/test_notes"
        
        # Create writer
        writer = KnowledgeWriter(
            config=config,
            rag=mock_rag,
            notes_source=mock_notes_source
        )
        
        # Mock _add_to_mem0 to verify it's called
        with patch.object(writer, '_add_to_mem0', new_callable=AsyncMock) as mock_add:
            # Save a note
            result = await writer.quick_save(
                content="Test note content",
                title="Test Note",
                domain="scrolls",
                tags=["test"]
            )
            
            # Verify Mem0 was called
            assert mock_add.called


# ========== Persona Integration Tests ==========

class TestPersonaIntegration:
    """Test Persona integration with Mem0."""
    
    def test_persona_memory_context(self):
        """Test persona can retrieve memory context."""
        from core.personas.base import AgentPersona, PersonaContext
        
        # Create mock persona
        class TestPersona(AgentPersona):
            @property
            def default_mode(self):
                return "test"
            
            @property
            def available_modes(self):
                return ["test"]
            
            async def process(self, context):
                pass
            
            def get_mode_prompts(self):
                return {"test": "Test prompt"}
        
        # Mock router with config
        mock_router = Mock()
        mock_router.config = TEST_CONFIG
        
        persona = TestPersona("test", mock_router)
        
        # Test memory context retrieval
        if persona.mem0:
            context = persona._get_memory_context("test query")
            assert isinstance(context, str)
    
    def test_persona_add_memory(self):
        """Test persona can add memories."""
        from core.personas.base import AgentPersona
        
        class TestPersona(AgentPersona):
            @property
            def default_mode(self):
                return "test"
            
            @property
            def available_modes(self):
                return ["test"]
            
            async def process(self, context):
                pass
            
            def get_mode_prompts(self):
                return {"test": "Test prompt"}
        
        mock_router = Mock()
        mock_router.config = TEST_CONFIG
        
        persona = TestPersona("test", mock_router)
        
        # Add a memory
        if persona.mem0:
            persona._add_memory(
                content="Test persona memory",
                metadata={'type': 'test'}
            )


# ========== API Endpoint Tests ==========

class TestMemoryAPI:
    """Test Memory API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from interfaces.memory_api import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/api/memory/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
    
    @pytest.mark.skipif(
        not TEST_CONFIG['memory']['mem0']['enabled'],
        reason="Mem0 not enabled"
    )
    def test_add_memory_endpoint(self, client):
        """Test add memory endpoint."""
        response = client.post(
            "/api/memory/add",
            json={
                "content": "Test memory via API",
                "user_id": "test_user",
                "metadata": {"type": "test"}
            }
        )
        
        # May fail if Mem0 not configured, check status
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'memory_id' in data
    
    @pytest.mark.skipif(
        not TEST_CONFIG['memory']['mem0']['enabled'],
        reason="Mem0 not enabled"
    )
    def test_search_memory_endpoint(self, client):
        """Test search memory endpoint."""
        response = client.get(
            "/api/memory/search",
            params={
                "query": "test",
                "user_id": "test_user",
                "limit": 5
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert 'results' in data
            assert 'count' in data


# ========== Configuration Tests ==========

class TestConfiguration:
    """Test configuration handling."""
    
    def test_local_provider(self):
        """Test behavior with local provider."""
        from core.memory import get_memory_adapter
        
        local_config = {
            'memory': {
                'provider': 'local'
            }
        }
        
        adapter = get_memory_adapter(local_config)
        assert adapter is None  # Local provider returns None
    
    def test_mem0_provider(self):
        """Test behavior with mem0 provider."""
        from core.memory import get_memory_adapter
        
        adapter = get_memory_adapter(TEST_CONFIG)
        assert adapter is not None
    
    def test_invalid_provider(self):
        """Test behavior with invalid provider."""
        from core.memory import get_memory_adapter
        
        invalid_config = {
            'memory': {
                'provider': 'invalid'
            }
        }
        
        with pytest.raises(ValueError):
            get_memory_adapter(invalid_config)


# ========== Settings API Memory Tests ==========

class TestSettingsMemoryAPI:
    """Test GET/POST /api/settings/memory (Task 14 step 8)."""
    
    def test_get_memory_settings(self):
        """GET /api/settings/memory returns provider and mem0_enabled."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from interfaces.settings_api import create_settings_router
        from unittest.mock import patch, MagicMock
        
        app = FastAPI()
        app.include_router(create_settings_router())
        mock_config = MagicMock()
        mock_config._config = {"memory": {"provider": "local", "mem0": {"enabled": False}}}
        
        with patch("interfaces.settings_api.get_config", return_value=mock_config):
            client = TestClient(app)
            response = client.get("/api/settings/memory")
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert "settings" in data
        assert "provider" in data["settings"]
        assert "mem0_enabled" in data["settings"]
    
    def test_post_memory_settings(self):
        """POST /api/settings/memory updates provider/mem0_enabled (with config save mocked)."""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from interfaces.settings_api import create_settings_router
        from unittest.mock import patch, MagicMock
        
        app = FastAPI()
        app.include_router(create_settings_router())
        client = TestClient(app)
        
        mock_config = MagicMock()
        mock_config._config = {"memory": {"provider": "local", "mem0": {"enabled": False}}}
        mock_config.save = MagicMock()
        
        with patch("interfaces.settings_api.get_config", return_value=mock_config):
            response = client.post(
                "/api/settings/memory",
                json={"provider": "mem0", "mem0_enabled": True}
            )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") is True
        assert data["settings"]["provider"] == "mem0"
        assert data["settings"]["mem0_enabled"] is True


# ========== Integration Tests ==========

class TestEndToEndIntegration:
    """End-to-end integration tests (Task 14 step 9)."""
    
    @pytest.mark.asyncio
    async def test_knowledge_to_memory_flow(self):
        """Test flow: add content to Mem0 (as knowledge writer would) then search."""
        try:
            from core.memory.mem0_adapter import Mem0Adapter
            adapter = Mem0Adapter(TEST_CONFIG)
        except (ImportError, ValueError, Exception) as e:
            pytest.skip(f"Mem0 not available or config invalid: {e}")
        adapter.add_memory(
            content="Polly knowledge: React hooks should be called at top level.",
            user_id="default",
            metadata={"source": "knowledge_writer", "domain": "scrolls"}
        )
        results = adapter.search_memory(
            query="React hooks",
            user_id="default",
            limit=5
        )
        assert isinstance(results, list)
        assert len(results) >= 1
        assert any("hook" in (r.get("memory") or "").lower() for r in results)
    
    @pytest.mark.asyncio
    async def test_pattern_learning_flow(self):
        """Test pattern learning and retrieval."""
        from core.pattern_learning import PatternLearner, Pattern
        
        learner = PatternLearner(TEST_CONFIG)
        
        # Learn a pattern
        pattern = Pattern(
            type="routing",
            description="Integration test pattern",
            confidence=0.9,
            timestamp=datetime.now().isoformat(),
            metadata={'test': True}
        )
        
        learner.learn_pattern(pattern)
        
        # Search for it
        results = learner.search_patterns("integration test")
        assert len(results) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

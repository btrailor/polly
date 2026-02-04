"""
Tests for PersonaManager lazy-loading architecture (Phase 16c Day 2-3)

Tests:
- Metadata loading at startup
- On-demand prompt loading
- Prompt caching
- System prompt generation with metadata
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from core.personas.manager import PersonaManager
from core.personas.models import PersonaMetadata
from core.router_v2 import IntelligentRouterV2


@pytest.fixture
def temp_definitions_dir():
    """Create temporary directory with test persona definitions"""
    with tempfile.TemporaryDirectory() as tmpdir:
        definitions_dir = Path(tmpdir)
        
        # Create test persona YAML
        test_persona = {
            "slug": "test-persona",
            "name": "Test Persona",
            "description": "A test persona for unit testing",
            "icon": "🧪",
            "primary_domain": "testing",
            "skills": ["skill1", "skill2"],
            "collaboration": {
                "partners": ["librarian", "scribe"]
            },
            "modes": {
                "test-mode": {
                    "name": "Test Mode",
                    "description": "A test mode",
                    "prompt": "You are a test persona in test mode. This is a test prompt."
                },
                "another-mode": {
                    "name": "Another Mode",
                    "description": "Another test mode",
                    "prompt": "You are a test persona in another mode. Different prompt."
                }
            }
        }
        
        yaml_path = definitions_dir / "test-persona.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(test_persona, f)
        
        yield definitions_dir


@pytest.fixture
def mock_router():
    """Mock router for testing"""
    # Create a minimal mock that satisfies PersonaManager requirements
    class MockRouter:
        pass
    return MockRouter()


class TestMetadataLoading:
    """Test metadata loading at startup"""
    
    def test_load_metadata_from_yaml(self, mock_router, temp_definitions_dir):
        """Test that metadata is loaded from YAML files"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        # Check metadata was loaded
        assert len(manager.metadata_cache) >= 1
        assert "test-persona" in manager.metadata_cache
        
        metadata = manager.metadata_cache["test-persona"]
        assert metadata.name == "Test Persona"
        assert metadata.description == "A test persona for unit testing"
        assert metadata.icon == "🧪"
        assert len(metadata.modes) == 2
        assert "test-mode" in metadata.modes
        assert "another-mode" in metadata.modes
        assert metadata.primary_domain == "testing"
        assert metadata.skills == ["skill1", "skill2"]
        assert "librarian" in metadata.collaboration_partners
    
    def test_list_personas(self, mock_router, temp_definitions_dir):
        """Test list_personas() returns all metadata"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        personas = manager.list_personas()
        assert len(personas) >= 1
        assert isinstance(personas[0], PersonaMetadata)
    
    def test_get_persona_metadata(self, mock_router, temp_definitions_dir):
        """Test get_persona_metadata() returns specific metadata"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        metadata = manager.get_persona_metadata("test-persona")
        assert metadata is not None
        assert metadata.name == "Test Persona"
        
        # Test non-existent persona
        assert manager.get_persona_metadata("non-existent") is None
    
    def test_empty_definitions_dir(self, mock_router):
        """Test behavior with empty definitions directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PersonaManager(mock_router, definitions_dir=tmpdir)
            
            # Should still initialize without errors
            assert len(manager.metadata_cache) == 0
            assert manager.list_personas() == []


class TestPromptLoading:
    """Test on-demand prompt loading"""
    
    def test_load_persona_prompt(self, mock_router, temp_definitions_dir):
        """Test prompt loading for specific mode"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        # Load prompt
        prompt = manager._load_persona_prompt("test-persona", "test-mode")
        
        assert prompt is not None
        assert "test persona in test mode" in prompt.lower()
        assert len(prompt) > 0
    
    def test_prompt_caching(self, mock_router, temp_definitions_dir):
        """Test that prompts are cached after first load"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        # First load
        prompt1 = manager._load_persona_prompt("test-persona", "test-mode")
        cache_key = "test-persona:test-mode"
        assert cache_key in manager.loaded_prompts
        
        # Second load should use cache
        prompt2 = manager._load_persona_prompt("test-persona", "test-mode")
        assert prompt1 == prompt2
        
        # Verify it's the same cache entry
        assert manager.loaded_prompts[cache_key].prompt == prompt1
    
    def test_get_prompt_for_mode(self, mock_router, temp_definitions_dir):
        """Test public API for getting prompts"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        # Valid prompt
        prompt = manager.get_prompt_for_mode("test-persona", "test-mode")
        assert prompt is not None
        
        # Invalid persona
        prompt = manager.get_prompt_for_mode("non-existent", "test-mode")
        assert prompt is None
        
        # Invalid mode
        prompt = manager.get_prompt_for_mode("test-persona", "non-existent-mode")
        assert prompt is None
    
    def test_clear_prompt_cache(self, mock_router, temp_definitions_dir):
        """Test cache clearing"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        # Load prompt
        manager._load_persona_prompt("test-persona", "test-mode")
        assert len(manager.loaded_prompts) > 0
        
        # Clear cache
        manager.clear_prompt_cache()
        assert len(manager.loaded_prompts) == 0
    
    def test_load_different_modes(self, mock_router, temp_definitions_dir):
        """Test loading prompts for different modes"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        # Load both modes
        prompt1 = manager._load_persona_prompt("test-persona", "test-mode")
        prompt2 = manager._load_persona_prompt("test-persona", "another-mode")
        
        # Prompts should be different
        assert prompt1 != prompt2
        assert "test mode" in prompt1.lower()
        assert "another mode" in prompt2.lower()
        
        # Both should be cached
        assert "test-persona:test-mode" in manager.loaded_prompts
        assert "test-persona:another-mode" in manager.loaded_prompts


class TestSystemPrompt:
    """Test system prompt generation"""
    
    def test_get_system_prompt_no_persona(self, mock_router, temp_definitions_dir):
        """Test system prompt with no active persona"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        prompt = manager.get_system_prompt()
        
        # Should include available personas metadata
        assert "Available Personas" in prompt
        assert "Test Persona" in prompt
    
    def test_get_system_prompt_without_metadata(self, mock_router, temp_definitions_dir):
        """Test system prompt without metadata section"""
        manager = PersonaManager(mock_router, definitions_dir=str(temp_definitions_dir))
        
        prompt = manager.get_system_prompt(include_metadata=False)
        
        # Should not include metadata
        assert "Available Personas" not in prompt


class TestErrorHandling:
    """Test error handling for lazy-loading"""
    
    def test_invalid_yaml(self, mock_router):
        """Test handling of invalid YAML files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            definitions_dir = Path(tmpdir)
            
            # Create invalid YAML
            bad_yaml = definitions_dir / "bad.yaml"
            with open(bad_yaml, 'w') as f:
                f.write("{ invalid: yaml: syntax:")
            
            # Should handle gracefully
            manager = PersonaManager(mock_router, definitions_dir=str(definitions_dir))
            assert len(manager.metadata_cache) == 0
    
    def test_missing_prompt(self, mock_router):
        """Test handling of persona with missing prompt"""
        with tempfile.TemporaryDirectory() as tmpdir:
            definitions_dir = Path(tmpdir)
            
            # Create persona with no prompt
            no_prompt_persona = {
                "slug": "no-prompt",
                "name": "No Prompt",
                "modes": {
                    "empty-mode": {
                        "name": "Empty Mode"
                        # No prompt field
                    }
                }
            }
            
            yaml_path = definitions_dir / "no-prompt.yaml"
            with open(yaml_path, 'w') as f:
                yaml.dump(no_prompt_persona, f)
            
            manager = PersonaManager(mock_router, definitions_dir=str(definitions_dir))
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="No prompt defined"):
                manager._load_persona_prompt("no-prompt", "empty-mode")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Integration test for Mental Models Phase 14
Tests end-to-end flow from query to mental model activation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.mental_models import MentalModelManager
from core.compression.compressor import ConversationCompressor


def test_mental_models_manager_initialization():
    """Test that mental model manager initializes with default models."""
    manager = MentalModelManager(storage_path=":memory:")
    
    # Should load 12 default models
    models = manager.list_models()
    assert len(models) == 12
    
    # Check all expected models are present
    expected_ids = [
        'infinite_games', 'instruments_over_tracks', 'constraint_as_meaning',
        'pedagogy_of_liberation', 'reverse_engineering', 'socratic_method',
        'systems_thinking', 'first_principles', 'design_thinking',
        'inbox_zero', 'async_first', 'time_blocking'
    ]
    
    model_ids = [m.id for m in models]
    for expected_id in expected_ids:
        assert expected_id in model_ids, f"Missing model: {expected_id}"


def test_mental_models_activation_learning_context():
    """Test mental models activate correctly for learning context."""
    manager = MentalModelManager(storage_path=":memory:")
    
    # Learning page context
    models = manager.get_models_for_context(
        page='learning',
        domain='scrolls',
        keywords=['learning', 'teach']
    )
    
    # Should return models (top 3-5)
    assert len(models) > 0
    assert len(models) <= 5
    
    # All returned models should be enabled
    for model in models:
        assert model.enabled


def test_mental_models_compression():
    """Test mental models compress to PIL format."""
    manager = MentalModelManager(storage_path=":memory:")
    compressor = ConversationCompressor()
    
    # Get a model
    model = manager.get_model('socratic_method')
    assert model is not None
    
    # Compress it
    model_dict = model.to_dict()
    compressed = compressor.compress(model_dict, type='mental_model')
    
    # Should produce compressed string
    assert isinstance(compressed, str)
    assert len(compressed) > 0
    assert compressed.startswith('MM:')
    assert 'socratic_method' in compressed
    
    # Should be smaller than JSON
    import json
    original_size = len(json.dumps(model_dict))
    compressed_size = len(compressed)
    assert compressed_size < original_size


def test_mental_models_override():
    """Test that specific models can be retrieved by ID."""
    manager = MentalModelManager(storage_path=":memory:")
    
    # Override: Get specific models
    override_ids = ['infinite_games', 'systems_thinking', 'socratic_method']
    
    overridden_models = []
    for model_id in override_ids:
        model = manager.get_model(model_id)
        if model:
            overridden_models.append(model)
    
    # Should get exactly 3 models
    assert len(overridden_models) == 3
    
    # Should match requested IDs
    retrieved_ids = [m.id for m in overridden_models]
    assert set(retrieved_ids) == set(override_ids)


def test_mental_models_crud_operations():
    """Test CRUD operations on mental models."""
    manager = MentalModelManager(storage_path=":memory:")
    
    # Create new model
    new_model = {
        'id': 'test_custom_model',
        'name': 'Test Custom Model',
        'description': 'A test model',
        'principles': ['Principle 1', 'Principle 2'],
        'prompt_injection': 'Test prompt',
        'applies_to': ['scrolls'],
        'active_on_pages': ['notes'],
        'active_for_personas': [],
        'active_for_modes': [],
        'keywords': ['test'],
        'enabled': True
    }
    
    # Add
    manager.add_model(**new_model)
    assert manager.get_model('test_custom_model') is not None
    
    # Update
    manager.update_model('test_custom_model', description='Updated description')
    updated = manager.get_model('test_custom_model')
    assert updated.description == 'Updated description'
    
    # Toggle
    manager.toggle_model('test_custom_model')
    toggled = manager.get_model('test_custom_model')
    assert toggled.enabled == False
    
    # Delete
    manager.delete_model('test_custom_model')
    assert manager.get_model('test_custom_model') is None


def test_mental_models_three_tier_activation():
    """Test three-tier activation (domain + page + persona)."""
    manager = MentalModelManager(storage_path=":memory:")
    
    # Test 1: Code page + Sigils domain + Architect persona
    models = manager.get_models_for_context(
        domain='sigils',
        page='code',
        persona='architect',
        persona_mode='plan'
    )
    assert len(models) > 0
    
    # Test 2: Mail page (future-proof)
    models = manager.get_models_for_context(page='mail')
    # Inbox Zero should be in results
    model_ids = [m.id for m in models]
    assert 'inbox_zero' in model_ids
    
    # Test 3: Teacher persona (future-proof)
    models = manager.get_models_for_context(persona='teacher')
    # Should include pedagogy models
    model_ids = [m.id for m in models]
    assert any('pedagogy' in mid or 'socratic' in mid for mid in model_ids)


def test_mental_models_persistence():
    """Test models persist to storage."""
    import tempfile
    import os
    
    # Create temp file for storage
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = f.name
    
    try:
        # Create manager and add custom model
        manager1 = MentalModelManager(storage_path=temp_path)
        manager1.add_model(
            id='persistent_test',
            name='Persistent Test',
            description='Test persistence',
            principles=['Test'],
            prompt_injection='Test',
            applies_to=[],
            active_on_pages=[],
            active_for_personas=[],
            active_for_modes=[],
            keywords=[],
            enabled=True
        )
        
        # Create new manager with same storage path
        manager2 = MentalModelManager(storage_path=temp_path)
        
        # Should load the custom model
        assert manager2.get_model('persistent_test') is not None
        
        # Should still have all 12 default models
        assert len(manager2.list_models()) == 13  # 12 defaults + 1 custom
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

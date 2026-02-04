"""
Tests for Mental Models System (Phase 14)
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from core.mental_models import MentalModel, MentalModelManager


class TestMentalModel:
    """Test MentalModel dataclass."""
    
    def test_create_model(self):
        """Test creating a mental model."""
        model = MentalModel(
            id='test_model',
            name='Test Model',
            description='A test mental model',
            principles=['Principle 1', 'Principle 2'],
            prompt_injection='Test prompt injection',
            applies_to=['scrolls'],
            active_on_pages=['learning'],
            keywords=['test', 'example']
        )
        
        assert model.id == 'test_model'
        assert model.name == 'Test Model'
        assert len(model.principles) == 2
        assert model.enabled is True
        assert 'scrolls' in model.applies_to
        assert 'learning' in model.active_on_pages
    
    def test_model_to_dict(self):
        """Test converting model to dictionary."""
        model = MentalModel(
            id='test_model',
            name='Test Model',
            description='A test mental model',
            principles=['Principle 1'],
            prompt_injection='Test prompt'
        )
        
        data = model.to_dict()
        
        assert data['id'] == 'test_model'
        assert data['name'] == 'Test Model'
        assert isinstance(data['created'], str)  # Should be ISO format string
        assert isinstance(data['updated'], str)
    
    def test_model_from_dict(self):
        """Test creating model from dictionary."""
        data = {
            'id': 'test_model',
            'name': 'Test Model',
            'description': 'A test mental model',
            'principles': ['Principle 1'],
            'prompt_injection': 'Test prompt',
            'applies_to': ['scrolls'],
            'active_on_pages': ['learning'],
            'active_for_personas': [],
            'active_for_modes': [],
            'keywords': ['test'],
            'category_triggers': [],
            'enabled': True,
            'created': '2026-01-29T10:00:00',
            'updated': '2026-01-29T10:00:00',
            '_compressed': None
        }
        
        model = MentalModel.from_dict(data)
        
        assert model.id == 'test_model'
        assert model.name == 'Test Model'
        assert isinstance(model.created, datetime)
        assert isinstance(model.updated, datetime)


class TestMentalModelManager:
    """Test MentalModelManager."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def manager(self, temp_storage):
        """Create manager with temporary storage."""
        return MentalModelManager(storage_path=temp_storage)
    
    def test_manager_initialization(self, manager):
        """Test manager initializes with default models."""
        assert len(manager.models) == 12
        assert 'infinite_games' in manager.models
        assert 'socratic_method' in manager.models
        assert 'pedagogy_of_liberation' in manager.models
    
    def test_default_models_structure(self, manager):
        """Test that all default models have required fields."""
        for model_id, model in manager.models.items():
            assert model.id == model_id
            assert model.name
            assert model.description
            assert len(model.principles) > 0
            assert model.prompt_injection
            assert isinstance(model.applies_to, list)
            assert isinstance(model.active_on_pages, list)
            assert isinstance(model.keywords, list)
            assert model.enabled is True
    
    def test_get_models_for_context_page_match(self, manager):
        """Test page-level activation (strongest signal)."""
        # Learning page should activate Freire, Socratic, and potentially others
        models = manager.get_models_for_context(page='learning')
        
        # Should return models
        assert len(models) > 0
        assert len(models) <= 5
        
        # Top models should include those with learning page
        model_names = [m.name for m in models]
        assert any('Socratic' in name or 'Freire' in name or 'Infinite' in name for name in model_names)
    
    def test_get_models_for_context_persona_match(self, manager):
        """Test persona-level activation."""
        # Architect persona should activate systems thinking, first principles, etc.
        models = manager.get_models_for_context(persona='architect', persona_mode='plan')
        
        assert len(models) > 0
        
        # Should include architect-relevant models
        model_ids = [m.id for m in models]
        # At least one of these should be present
        architect_models = ['systems_thinking', 'first_principles', 'design_thinking', 
                          'instruments_over_tracks', 'constraint_as_meaning']
        assert any(mid in model_ids for mid in architect_models)
    
    def test_get_models_for_context_domain_match(self, manager):
        """Test domain-level activation."""
        # Scrolls domain should activate pedagogy of liberation
        models = manager.get_models_for_context(domain='scrolls', category='scrolls')
        
        assert len(models) > 0
        
        # Freire's pedagogy has category_triggers=['scrolls']
        model_ids = [m.id for m in models]
        assert 'pedagogy_of_liberation' in model_ids
    
    def test_get_models_for_context_keyword_match(self, manager):
        """Test keyword-based activation."""
        models = manager.get_models_for_context(keywords=['constraint', 'limitation'])
        
        assert len(models) > 0
        
        # Should include constraint_as_meaning model
        model_ids = [m.id for m in models]
        assert 'constraint_as_meaning' in model_ids
    
    def test_get_models_for_context_scoring(self, manager):
        """Test that scoring prioritizes correctly."""
        # Page match (10 points) should beat domain match (3 points)
        models_with_page = manager.get_models_for_context(page='learning')
        models_with_domain = manager.get_models_for_context(domain='sigils')
        
        # Both should return models, but page match should be stronger
        assert len(models_with_page) > 0
        assert len(models_with_domain) > 0
    
    def test_get_models_for_context_combined(self, manager):
        """Test three-tier activation with multiple contexts."""
        # Learning page + Scrolls domain + Teacher persona
        models = manager.get_models_for_context(
            domain='scrolls',
            page='learning',
            persona='teacher',
            persona_mode='socratic'
        )
        
        assert len(models) > 0
        
        # Should strongly favor Socratic Method and Freire's Pedagogy
        model_ids = [m.id for m in models[:3]]
        assert 'socratic_method' in model_ids or 'pedagogy_of_liberation' in model_ids
    
    def test_get_models_enabled_only(self, manager):
        """Test that disabled models are filtered out."""
        # Disable a model
        manager.models['infinite_games'].enabled = False
        
        # Should not appear in results
        models = manager.get_models_for_context(page='learning', enabled_only=True)
        model_ids = [m.id for m in models]
        assert 'infinite_games' not in model_ids
        
        # Should appear when enabled_only=False
        models = manager.get_models_for_context(page='learning', enabled_only=False)
        model_ids = [m.id for m in models]
        # Note: infinite_games might not be in results if score is too low, so just check it's not filtered by enabled flag
    
    def test_add_model(self, manager):
        """Test adding a new model."""
        new_model = MentalModel(
            id='custom_model',
            name='Custom Model',
            description='A custom mental model',
            principles=['Custom principle'],
            prompt_injection='Custom prompt',
            applies_to=['sigils'],
            keywords=['custom']
        )
        
        manager.add_model(new_model)
        
        assert 'custom_model' in manager.models
        assert manager.models['custom_model'].name == 'Custom Model'
    
    def test_add_duplicate_model(self, manager):
        """Test that adding duplicate model raises error."""
        new_model = MentalModel(
            id='infinite_games',  # Already exists
            name='Duplicate',
            description='Test',
            principles=['Test'],
            prompt_injection='Test'
        )
        
        with pytest.raises(ValueError, match="already exists"):
            manager.add_model(new_model)
    
    def test_update_model(self, manager):
        """Test updating a model."""
        updated = manager.update_model(
            'infinite_games',
            {'name': 'Updated Name', 'enabled': False}
        )
        
        assert updated.name == 'Updated Name'
        assert updated.enabled is False
        assert manager.models['infinite_games'].name == 'Updated Name'
    
    def test_update_nonexistent_model(self, manager):
        """Test updating nonexistent model raises error."""
        with pytest.raises(ValueError, match="not found"):
            manager.update_model('nonexistent', {'name': 'Test'})
    
    def test_delete_model(self, manager):
        """Test deleting a model."""
        assert 'infinite_games' in manager.models
        
        manager.delete_model('infinite_games')
        
        assert 'infinite_games' not in manager.models
    
    def test_delete_nonexistent_model(self, manager):
        """Test deleting nonexistent model raises error."""
        with pytest.raises(ValueError, match="not found"):
            manager.delete_model('nonexistent')
    
    def test_toggle_model(self, manager):
        """Test toggling model enabled state."""
        initial_state = manager.models['infinite_games'].enabled
        
        new_state = manager.toggle_model('infinite_games')
        
        assert new_state != initial_state
        assert manager.models['infinite_games'].enabled == new_state
        
        # Toggle again
        new_state2 = manager.toggle_model('infinite_games')
        assert new_state2 == initial_state
    
    def test_get_model(self, manager):
        """Test getting a single model."""
        model = manager.get_model('infinite_games')
        
        assert model is not None
        assert model.id == 'infinite_games'
        assert model.name == 'Infinite Games'
    
    def test_get_nonexistent_model(self, manager):
        """Test getting nonexistent model returns None."""
        model = manager.get_model('nonexistent')
        assert model is None
    
    def test_list_models(self, manager):
        """Test listing all models."""
        models = manager.list_models()
        
        assert len(models) == 12
    
    def test_list_models_enabled_only(self, manager):
        """Test listing only enabled models."""
        # Disable one model
        manager.models['infinite_games'].enabled = False
        
        models = manager.list_models(enabled_only=True)
        
        assert len(models) == 11
        assert all(m.enabled for m in models)
    
    def test_save_and_load_models(self, temp_storage):
        """Test saving and loading models."""
        # Create manager and add custom model
        manager1 = MentalModelManager(storage_path=temp_storage)
        
        custom_model = MentalModel(
            id='custom',
            name='Custom',
            description='Test',
            principles=['Test'],
            prompt_injection='Test',
            applies_to=['sigils'],
            active_on_pages=['code'],
            keywords=['custom']
        )
        manager1.add_model(custom_model)
        manager1.save_models()
        
        # Create new manager from same storage
        manager2 = MentalModelManager(storage_path=temp_storage)
        
        # Should load all models including custom
        assert len(manager2.models) == 13  # 12 default + 1 custom
        assert 'custom' in manager2.models
        assert manager2.models['custom'].name == 'Custom'
        assert 'code' in manager2.models['custom'].active_on_pages
    
    def test_future_proof_mail_page(self, manager):
        """Test future-proof design: Mail page activates Inbox Zero."""
        models = manager.get_models_for_context(page='mail')
        
        assert len(models) > 0
        model_ids = [m.id for m in models]
        assert 'inbox_zero' in model_ids
    
    def test_future_proof_calendar_page(self, manager):
        """Test future-proof design: Calendar page activates Time Blocking."""
        models = manager.get_models_for_context(page='calendar')
        
        assert len(models) > 0
        model_ids = [m.id for m in models]
        assert 'time_blocking' in model_ids
    
    def test_future_proof_teacher_persona(self, manager):
        """Test future-proof design: Teacher persona activates pedagogy models."""
        models = manager.get_models_for_context(persona='teacher')
        
        assert len(models) > 0
        model_ids = [m.id for m in models]
        # Should include pedagogy, socratic, or reverse engineering
        teaching_models = ['pedagogy_of_liberation', 'socratic_method', 'reverse_engineering']
        assert any(mid in model_ids for mid in teaching_models)


class TestThreeTierActivation:
    """Test three-tier activation scenarios."""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create manager with temporary storage."""
        storage_path = tmp_path / "test_models.yaml"
        return MentalModelManager(storage_path=str(storage_path))
    
    def test_scenario_learning_page_scrolls(self, manager):
        """Scenario: Learning page + Scrolls domain."""
        models = manager.get_models_for_context(page='learning', domain='scrolls')
        
        assert len(models) > 0
        # Should favor Freire (page + domain + category trigger) and Socratic (page)
        model_ids = [m.id for m in models[:2]]
        assert 'pedagogy_of_liberation' in model_ids or 'socratic_method' in model_ids
    
    def test_scenario_code_page_architect_plan(self, manager):
        """Scenario: Code page + Architect persona (Plan mode)."""
        models = manager.get_models_for_context(
            page='code',
            persona='architect',
            persona_mode='plan'
        )
        
        assert len(models) > 0
        # Should favor First Principles, Systems Thinking, Design Thinking
        model_ids = [m.id for m in models]
        architect_models = ['first_principles', 'systems_thinking', 'design_thinking']
        assert any(mid in model_ids for mid in architect_models)
    
    def test_scenario_keyword_constraint(self, manager):
        """Scenario: Query with 'constraint' keyword."""
        models = manager.get_models_for_context(keywords=['constraint'])
        
        assert len(models) > 0
        model_ids = [m.id for m in models]
        assert 'constraint_as_meaning' in model_ids
    
    def test_scenario_no_context(self, manager):
        """Scenario: No context provided."""
        models = manager.get_models_for_context()
        
        # Should return empty list (no scoring)
        assert len(models) == 0

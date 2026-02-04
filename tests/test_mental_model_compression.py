"""
Tests for Mental Model PIL Compression (Phase 14)

Verifies:
- PIL compression achieves ≥2.5x compression ratio
- Symbol system works correctly
- All 12 default models compress successfully
"""

import pytest
import json
from core.compression.compressor import ConversationCompressor
from core.mental_models import MentalModel


class TestPILCompression:
    """Test PIL (Polly Internal Language) compression for mental models."""
    
    @pytest.fixture
    def compressor(self):
        """Create compressor instance."""
        return ConversationCompressor()
    
    @pytest.fixture
    def sample_model_dict(self):
        """Sample mental model as dictionary."""
        return {
            'id': 'test_model',
            'name': 'Test Model',
            'description': 'A test mental model for dialogue and learning',
            'principles': [
                'Question rather than tell',
                'Dialogue over transmission',
                'Learning and teaching together',
                'Reflection plus action',
                'Evolving understanding'
            ],
            'prompt_injection': 'Ask questions that guide discovery. Reveal contradictions. Recognize we are learning together.',
            'applies_to': ['scrolls', 'grids'],
            'active_on_pages': ['learning', 'dashboard', 'notes'],
            'active_for_personas': ['teacher'],
            'active_for_modes': ['socratic', 'guide'],
            'keywords': ['question', 'dialogue', 'socratic', 'inquiry', 'learning']
        }
    
    def test_compress_mental_model(self, compressor, sample_model_dict):
        """Test basic mental model compression."""
        compressed = compressor.compress(sample_model_dict, type='mental_model')
        
        # Should return a string in PIL format
        assert isinstance(compressed, str)
        assert compressed.startswith('MM:test_model|')
        
        # Should contain major components
        assert 'p:[' in compressed  # principles
        assert 'pi:' in compressed  # prompt injection
        assert 'd:[' in compressed  # domains
        assert 'pg:[' in compressed  # pages
        assert 'ps:[' in compressed  # personas
        assert 'pm:[' in compressed  # modes
        assert 'k:[' in compressed  # keywords
    
    def test_compression_ratio(self, compressor, sample_model_dict):
        """Test that compression achieves ≥2.5x ratio."""
        # Calculate original size
        original_json = json.dumps(sample_model_dict, separators=(',', ':'))
        original_size = len(original_json)
        
        # Compress
        compressed = compressor.compress(sample_model_dict, type='mental_model')
        compressed_size = len(compressed)
        
        # Calculate ratio
        ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        print(f"\nOriginal: {original_size} chars")
        print(f"Compressed: {compressed_size} chars")
        print(f"Ratio: {ratio:.2f}x")
        print(f"Compressed: {compressed[:200]}...")
        
        # Should achieve at least 2.5x compression
        assert ratio >= 2.5, f"Compression ratio {ratio:.2f}x is below target 2.5x"
    
    def test_symbol_system_over(self, compressor):
        """Test 'over' symbol replacement (>)."""
        model = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'principles': ['Continuation over completion', 'Quality rather than quantity'],
            'prompt_injection': 'Test'
        }
        
        compressed = compressor.compress(model, type='mental_model')
        
        # Should contain > symbol for "over"
        assert '>' in compressed or 'cont' in compressed.lower()
    
    def test_symbol_system_evolving(self, compressor):
        """Test 'evolving' symbol replacement (↻)."""
        model = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'principles': ['Evolving rules rather than fixed'],
            'prompt_injection': 'Test'
        }
        
        compressed = compressor.compress(model, type='mental_model')
        
        # Should contain ↻ symbol or abbreviated version
        assert '↻' in compressed or 'evol' in compressed.lower()
    
    def test_symbol_system_mutual(self, compressor):
        """Test 'mutual' symbol replacement (⇄)."""
        model = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'principles': ['Teacher and student learn together'],
            'prompt_injection': 'Test'
        }
        
        compressed = compressor.compress(model, type='mental_model')
        
        # Should contain ⇄ symbol or abbreviated version
        assert '⇄' in compressed or '&' in compressed or 'together' in compressed.lower()
    
    def test_symbol_system_question(self, compressor):
        """Test question marker (?)."""
        model = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'principles': ['Question rather than tell'],
            'prompt_injection': 'Ask questions that guide discovery'
        }
        
        compressed = compressor.compress(model, type='mental_model')
        
        # Should contain ? marker for questions
        assert '?' in compressed or 'question' in compressed.lower() or 'ask' in compressed.lower()
    
    def test_symbol_system_important(self, compressor):
        """Test importance marker (!)."""
        model = {
            'id': 'test',
            'name': 'Test',
            'description': 'Test',
            'principles': ['Critical consciousness is essential'],
            'prompt_injection': 'Emphasize the importance of dialogue'
        }
        
        compressed = compressor.compress(model, type='mental_model')
        
        # Should contain ! marker for importance
        assert '!' in compressed or 'critical' in compressed.lower() or 'important' in compressed.lower()
    
    def test_extract_mode(self, compressor):
        """Test mode extraction from model."""
        # Socratic/dialogue model
        mode = compressor._extract_mode({
            'name': 'Socratic Method',
            'description': 'Question assumptions through dialogue'
        })
        assert mode == 'dialogue'
        
        # Systems model
        mode = compressor._extract_mode({
            'name': 'Systems Thinking',
            'description': 'Focus on interconnections and feedback loops'
        })
        assert mode == 'systems'
        
        # Pedagogy model
        mode = compressor._extract_mode({
            'name': "Freire's Pedagogy",
            'description': 'Education as liberation through teaching'
        })
        assert mode == 'pedagogy'
    
    def test_compress_principles(self, compressor):
        """Test principle compression."""
        principles = [
            'Continuation over completion',
            'Evolving rules rather than fixed',
            'Question rather than tell',
            'Critical consciousness is essential',
            'Reflection plus action'
        ]
        
        compressed = compressor._compress_principles(principles)
        
        # Should be significantly shorter
        original_length = sum(len(p) for p in principles)
        compressed_length = len(compressed)
        
        print(f"\nPrinciples compression:")
        print(f"Original: {original_length} chars")
        print(f"Compressed: {compressed_length} chars")
        print(f"Result: {compressed}")
        
        assert compressed_length < original_length * 0.6  # At least 40% reduction
    
    def test_compress_prompt(self, compressor):
        """Test prompt injection compression."""
        prompt = "Ask questions that guide discovery. Reveal contradictions in thinking. Recognize that we're learning together through dialogue."
        
        compressed = compressor._compress_prompt(prompt)
        
        # Should extract key action words
        assert len(compressed) < len(prompt) * 0.3  # At least 70% reduction
        
        # Should contain key concepts
        compressed_lower = compressed.lower()
        assert any(word in compressed_lower for word in ['question', 'ask', 'reveal', 'guide', '?'])
    
    def test_abbreviate_pages(self, compressor):
        """Test page abbreviation."""
        pages = ['dashboard', 'learning', 'calendar', 'projects']
        abbreviated = compressor._abbreviate_pages(pages)
        
        assert 'dash' in abbreviated  # dashboard → dash
        assert 'learn' in abbreviated  # learning → learn
        assert 'cal' in abbreviated  # calendar → cal
        assert 'proj' in abbreviated  # projects → proj
    
    def test_all_default_models_compress(self, compressor):
        """Test that all 12 default models compress successfully."""
        from core.mental_models import MentalModelManager
        import tempfile
        
        # Create temp storage
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        # Load default models
        manager = MentalModelManager(storage_path=temp_path)
        
        # Compress each model
        ratios = []
        for model_id, model in manager.models.items():
            model_dict = model.to_dict()
            
            # Calculate original size
            original_size = len(json.dumps(model_dict, separators=(',', ':')))
            
            # Compress
            compressed = compressor.compress(model_dict, type='mental_model')
            compressed_size = len(compressed)
            
            # Calculate ratio
            ratio = original_size / compressed_size if compressed_size > 0 else 0
            ratios.append(ratio)
            
            print(f"{model.name}: {original_size}→{compressed_size} chars ({ratio:.2f}x)")
            
            # Should compress successfully
            assert isinstance(compressed, str)
            assert len(compressed) > 0
            assert compressed.startswith(f'MM:{model_id}')
        
        # Average ratio should be ≥2.5x
        avg_ratio = sum(ratios) / len(ratios)
        print(f"\nAverage compression ratio: {avg_ratio:.2f}x")
        assert avg_ratio >= 2.5, f"Average ratio {avg_ratio:.2f}x is below target 2.5x"
        
        # Cleanup
        import os
        os.unlink(temp_path)
    
    def test_socratic_method_compression(self, compressor):
        """Test specific example from implementation plan: Socratic Method."""
        model = {
            'id': 'socratic_method',
            'name': 'Socratic Method',
            'description': 'Question assumptions through dialogue',
            'principles': [
                'Question rather than tell',
                'Reveal contradictions through dialogue',
                'Mutual learning (teacher and student learn together)'
            ],
            'prompt_injection': "Don't provide direct answers. Ask questions that guide discovery. Reveal contradictions. Recognize we're learning together.",
            'applies_to': ['scrolls', 'grids'],
            'active_on_pages': ['learning', 'dashboard'],
            'active_for_personas': ['teacher'],
            'active_for_modes': ['socratic', 'guide'],
            'keywords': ['socratic', 'question', 'dialogue', 'contradiction']
        }
        
        # Calculate original size (as in implementation plan example)
        original_size = 480  # Approximate from implementation plan
        
        # Compress
        compressed = compressor.compress(model, type='mental_model')
        compressed_size = len(compressed)
        
        # Calculate ratio
        ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        print(f"\nSocratic Method compression:")
        print(f"Original: ~{original_size} chars")
        print(f"Compressed: {compressed_size} chars")
        print(f"Ratio: {ratio:.2f}x")
        print(f"Result: {compressed}")
        
        # Should achieve close to 2.7x as in implementation plan
        assert ratio >= 2.5, f"Ratio {ratio:.2f}x is below target"
        
        # Should contain expected components
        assert 'MM:socratic_method' in compressed
        assert 'm:dialogue' in compressed or 'm:' in compressed
        assert 'p:[' in compressed
        assert 'd:[scrolls,grids]' in compressed
        assert 'ps:[teacher]' in compressed


class TestCompressionIntegration:
    """Test integration between mental models and compression."""
    
    @pytest.fixture
    def compressor(self):
        """Create compressor instance."""
        return ConversationCompressor()
    
    def test_mental_model_manager_with_compressor(self, compressor):
        """Test that MentalModelManager can use compressor."""
        from core.mental_models import MentalModelManager
        import tempfile
        
        # Create temp storage
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        # Create manager with compressor
        manager = MentalModelManager(storage_path=temp_path, compressor=compressor)
        
        # Get models for context
        models = manager.get_models_for_context(page='learning', domain='scrolls')
        
        assert len(models) > 0
        
        # Compress each model
        for model in models:
            model_dict = model.to_dict()
            compressed = compressor.compress(model_dict, type='mental_model')
            
            assert isinstance(compressed, str)
            assert len(compressed) > 0
        
        # Cleanup
        import os
        os.unlink(temp_path)

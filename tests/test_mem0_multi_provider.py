"""
Unit tests for Mem0 multi-provider configuration.

Tests the new multi-provider configuration system that allows
switching between Ollama, Qwen, MiniMax, and GLM providers
for both embeddings and LLM operations.
"""

import os
import pytest
from unittest.mock import MagicMock, patch
from core.memory.mem0_adapter import Mem0Adapter


@pytest.fixture
def base_config():
    """Base configuration with multi-provider setup."""
    return {
        'memory': {
            'provider': 'mem0',
            'mem0': {
                'enabled': True,
                'embedding_provider': 'ollama',
                'llm_provider': 'ollama',
                'vector_store': 'chroma',
                'providers': {
                    'ollama': {
                        'host': 'http://localhost:11434',
                        'embedding_model': 'nomic-embed-text',
                        'llm_model': 'llama3.2:3b',
                        'temperature': 0.0
                    },
                    'qwen': {
                        'api_key_env': 'DASHSCOPE_API_KEY',
                        'embedding_model': 'text-embedding-v3',
                        'llm_model': 'qwen-turbo',
                        'temperature': 0.0
                    },
                    'minimax': {
                        'api_key_env': 'MINIMAX_API_KEY',
                        'group_id_env': 'MINIMAX_GROUP_ID',
                        'embedding_model': 'embo-01',
                        'llm_model': 'abab6.5s-chat',
                        'temperature': 0.0
                    },
                    'glm': {
                        'api_key_env': 'ZHIPUAI_API_KEY',
                        'embedding_model': 'embedding-3',
                        'llm_model': 'glm-4-flash',
                        'temperature': 0.0
                    }
                },
                'collections': {
                    'knowledge': 'polly_mem0_knowledge'
                }
            }
        }
    }


class TestEmbedderConfigBuilder:
    """Tests for _build_embedder_config method."""
    
    def test_build_embedder_config_ollama(self, base_config):
        """Test Ollama embedder configuration."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['ollama']
        result = adapter._build_embedder_config('ollama', config)
        
        assert result['provider'] == 'openai'
        assert result['config']['model'] == 'nomic-embed-text'
        assert result['config']['openai_base_url'] == 'http://localhost:11434/v1'
        assert result['config']['api_key'] == 'ollama'
    
    def test_build_embedder_config_qwen(self, base_config):
        """Test Qwen embedder configuration."""
        os.environ['DASHSCOPE_API_KEY'] = 'test-key'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['qwen']
        result = adapter._build_embedder_config('qwen', config)
        
        assert result['provider'] == 'openai'
        assert result['config']['model'] == 'text-embedding-v3'
        assert 'dashscope.aliyuncs.com' in result['config']['openai_base_url']
        assert result['config']['api_key'] == 'test-key'
    
    def test_build_embedder_config_minimax(self, base_config):
        """Test MiniMax embedder configuration."""
        os.environ['MINIMAX_API_KEY'] = 'test-key'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['minimax']
        result = adapter._build_embedder_config('minimax', config)
        
        assert result['provider'] == 'openai'
        assert result['config']['model'] == 'embo-01'
        assert 'minimax.chat' in result['config']['openai_base_url']
        assert result['config']['api_key'] == 'test-key'
    
    def test_build_embedder_config_glm(self, base_config):
        """Test GLM embedder configuration."""
        os.environ['ZHIPUAI_API_KEY'] = 'test-key'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['glm']
        result = adapter._build_embedder_config('glm', config)
        
        assert result['provider'] == 'openai'
        assert result['config']['model'] == 'embedding-3'
        assert 'bigmodel.cn' in result['config']['openai_base_url']
        assert result['config']['api_key'] == 'test-key'
    
    def test_build_embedder_config_unsupported(self, base_config):
        """Test that unsupported providers raise ValueError."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        with pytest.raises(ValueError, match="Unsupported embedding provider"):
            adapter._build_embedder_config('unsupported', {})


class TestLLMConfigBuilder:
    """Tests for _build_llm_config method."""
    
    def test_build_llm_config_ollama(self, base_config):
        """Test Ollama LLM configuration."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['ollama']
        result = adapter._build_llm_config('ollama', config)
        
        assert result['provider'] == 'litellm'
        assert result['config']['model'] == 'ollama/llama3.2:3b'
        assert result['config']['temperature'] == 0.0
    
    def test_build_llm_config_qwen(self, base_config):
        """Test Qwen LLM configuration."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['qwen']
        result = adapter._build_llm_config('qwen', config)
        
        assert result['provider'] == 'litellm'
        assert result['config']['model'] == 'dashscope/qwen-turbo'
        assert result['config']['temperature'] == 0.0
    
    def test_build_llm_config_minimax(self, base_config):
        """Test MiniMax LLM configuration."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['minimax']
        result = adapter._build_llm_config('minimax', config)
        
        assert result['provider'] == 'litellm'
        assert result['config']['model'] == 'minimax/abab6.5s-chat'
        assert result['config']['temperature'] == 0.0
    
    def test_build_llm_config_glm(self, base_config):
        """Test GLM LLM configuration."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['glm']
        result = adapter._build_llm_config('glm', config)
        
        assert result['provider'] == 'litellm'
        assert result['config']['model'] == 'zhipuai/glm-4-flash'
        assert result['config']['temperature'] == 0.0
    
    def test_build_llm_config_unsupported(self, base_config):
        """Test that unsupported providers raise ValueError."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            adapter._build_llm_config('unsupported', {})


class TestProviderEnvVars:
    """Tests for _set_provider_env_vars method."""
    
    def test_set_provider_env_vars_ollama(self, base_config):
        """Test Ollama environment variable setup."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['ollama']
        adapter._set_provider_env_vars('ollama', config)
        
        assert os.environ.get('OLLAMA_API_BASE') == 'http://localhost:11434'
    
    def test_set_provider_env_vars_qwen(self, base_config):
        """Test Qwen environment variable setup."""
        os.environ['DASHSCOPE_API_KEY'] = 'test-key'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['qwen']
        adapter._set_provider_env_vars('qwen', config)
        
        assert os.environ.get('DASHSCOPE_API_KEY') == 'test-key'
    
    def test_set_provider_env_vars_minimax(self, base_config):
        """Test MiniMax environment variable setup."""
        os.environ['MINIMAX_API_KEY'] = 'test-key'
        os.environ['MINIMAX_GROUP_ID'] = 'test-group'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['minimax']
        adapter._set_provider_env_vars('minimax', config)
        
        assert os.environ.get('MINIMAX_API_KEY') == 'test-key'
        assert os.environ.get('MINIMAX_GROUP_ID') == 'test-group'
    
    def test_set_provider_env_vars_glm(self, base_config):
        """Test GLM environment variable setup."""
        os.environ['ZHIPUAI_API_KEY'] = 'test-key'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        
        config = base_config['memory']['mem0']['providers']['glm']
        adapter._set_provider_env_vars('glm', config)
        
        assert os.environ.get('ZHIPUAI_API_KEY') == 'test-key'


class TestMem0ConfigBuilder:
    """Tests for _build_mem0_config method."""
    
    def test_build_mem0_config_ollama(self, base_config):
        """Test building Mem0 config with Ollama provider."""
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        adapter.memory = MagicMock()
        
        # Need to inject helper methods
        adapter._build_embedder_config = Mem0Adapter._build_embedder_config.__get__(adapter)
        adapter._build_llm_config = Mem0Adapter._build_llm_config.__get__(adapter)
        adapter._set_provider_env_vars = Mem0Adapter._set_provider_env_vars.__get__(adapter)
        adapter._build_vector_store_config = Mem0Adapter._build_vector_store_config.__get__(adapter)
        
        result = adapter._build_mem0_config()
        
        assert result['version'] == 'v1.1'
        assert 'vector_store' in result
        assert 'embedder' in result
        assert 'llm' in result
        assert result['embedder']['provider'] == 'openai'
        assert result['llm']['provider'] == 'litellm'
        assert 'ollama/llama3.2:3b' in result['llm']['config']['model']
    
    def test_build_mem0_config_missing_provider(self, base_config):
        """Test that missing provider raises ValueError."""
        base_config['memory']['mem0']['embedding_provider'] = 'nonexistent'
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = base_config
        adapter.memory = MagicMock()
        
        # Need to inject helper methods
        adapter._build_embedder_config = Mem0Adapter._build_embedder_config.__get__(adapter)
        adapter._build_llm_config = Mem0Adapter._build_llm_config.__get__(adapter)
        adapter._set_provider_env_vars = Mem0Adapter._set_provider_env_vars.__get__(adapter)
        adapter._build_vector_store_config = Mem0Adapter._build_vector_store_config.__get__(adapter)
        adapter._get_default_provider_config = Mem0Adapter._get_default_provider_config.__get__(adapter)
        
        with pytest.raises(ValueError, match="Embedding provider .* not found"):
            adapter._build_mem0_config()


class TestBackwardCompatibility:
    """Tests for backward compatibility with legacy config."""
    
    def test_legacy_config_fallback(self):
        """Test that legacy config structure still works."""
        legacy_config = {
            'memory': {
                'provider': 'mem0',
                'mem0': {
                    'enabled': True,
                    'embedding_provider': 'ollama',
                    'llm_provider': 'ollama',
                    'vector_store': 'chroma',
                    'collections': {
                        'knowledge': 'polly_mem0_knowledge'
                    }
                }
            },
            'models': {
                'local': {
                    'host': 'http://localhost:11434',
                    'embedding_model': 'nomic-embed-text',
                    'chat_models': {
                        'fast': 'llama3.2:3b'
                    }
                }
            }
        }
        
        adapter = Mem0Adapter.__new__(Mem0Adapter)
        adapter.config = legacy_config
        adapter.memory = MagicMock()
        
        # Need to inject helper methods
        adapter._build_embedder_config = Mem0Adapter._build_embedder_config.__get__(adapter)
        adapter._build_llm_config = Mem0Adapter._build_llm_config.__get__(adapter)
        adapter._set_provider_env_vars = Mem0Adapter._set_provider_env_vars.__get__(adapter)
        adapter._build_vector_store_config = Mem0Adapter._build_vector_store_config.__get__(adapter)
        adapter._get_default_provider_config = Mem0Adapter._get_default_provider_config.__get__(adapter)
        
        result = adapter._build_mem0_config()
        
        # Should use legacy fallback
        assert result['version'] == 'v1.1'
        assert 'embedder' in result
        assert result['embedder']['config']['model'] == 'nomic-embed-text'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

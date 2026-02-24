"""
Settings API Endpoints for Polly
Handles API key management, provider configuration, and budget settings
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from core.secrets_manager import get_secrets_manager
from core.budget_manager import BudgetManager
from core.router_v2 import IntelligentRouterV2
from core.config import get_config

logger = logging.getLogger(__name__)

# Request/Response models
class SetKeyRequest(BaseModel):
    provider: str
    key: str


class DeleteKeyRequest(BaseModel):
    provider: str


class TestKeyRequest(BaseModel):
    provider: Optional[str] = None


class UpdateBudgetRequest(BaseModel):
    daily_limit: Optional[float] = None
    monthly_limit: Optional[float] = None
    warn_threshold: Optional[float] = None


class UpdateCompressionRequest(BaseModel):
    enabled: Optional[bool] = None
    message_threshold: Optional[int] = None
    age_hours: Optional[int] = None
    keep_recent: Optional[int] = None
    show_stats: Optional[bool] = None
    # RAG / context compression (LLMLingua strategy)
    strategy: Optional[str] = None  # "auto" | "llmlingua" | "llm_summary"
    rag_context_enabled: Optional[bool] = None
    rag_context_ratio: Optional[float] = None  # 0.1-1.0 (e.g. 0.5 = 2x compression)
    # Spec 04: semantic compression trigger
    semantic_trigger_enabled: Optional[bool] = None
    srs_threshold: Optional[float] = None   # 0.0–1.0
    srs_fallback_count: Optional[int] = None  # message count fallback


class UpdateMemoryRequest(BaseModel):
    """Request model for memory provider settings."""
    provider: Optional[str] = None  # "local" | "mem0"
    mem0_enabled: Optional[bool] = None


class UpdateAIFeaturesRequest(BaseModel):
    """Request model for updating AI features settings."""
    knowledge_suggestions_enabled: Optional[bool] = None
    knowledge_suggestions_style: Optional[str] = None  # "subtle" | "inline" | "ask_first"
    knowledge_suggestions_min_gap_score: Optional[float] = None
    autonomy_dashboard_enabled: Optional[bool] = None
    autonomy_dashboard_show_in_status_bar: Optional[bool] = None
    # Semantic cache (Spec 01) — sent as nested dict from frontend
    semantic_cache: Optional[Dict[str, Any]] = None
    # Spec 03: context persistence
    context_persistence: Optional[Dict[str, Any]] = None
    # Spec 07: mental model compression format
    mm_format: Optional[str] = None  # "compact" | "full" | "ab_test"
    # Accept flat legacy fields from old frontend versions
    kb_suggestions: Optional[bool] = None
    context_enrichment: Optional[bool] = None
    gap_score_threshold: Optional[float] = None
    autonomy_dashboard: Optional[bool] = None


class UpdateRAGRequest(BaseModel):
    """Request model for RAG & retrieval classifier settings."""
    # Retrieval
    n_results: Optional[int] = None          # chunks returned per query (1–20)
    # Retrieval classifier thresholds
    direct_threshold: Optional[float] = None    # score → DIRECT  (0.5–0.95)
    adjacent_threshold: Optional[float] = None  # score → ADJACENT (0.3–0.8)
    domain_match_boost: Optional[float] = None  # same-domain bonus (0–0.3)
    cross_domain_penalty: Optional[float] = None  # cross-domain penalty (0–0.3)
    # Wave-3 decomposition
    decomposition_enabled: Optional[bool] = None
    min_complexity_score: Optional[float] = None  # 0.0–1.0
    # Spec 08: BM25 index persistence
    bm25_persist: Optional[bool] = None


class ToggleProviderRequest(BaseModel):
    """Request model for toggling provider enabled status."""
    provider: str
    enabled: bool


class TestProviderRequest(BaseModel):
    """Request model for testing a specific provider."""
    provider: str


class QuickSaveRequest(BaseModel):
    """Request model for quick-saving knowledge from chat."""
    content: str
    title: str
    domain: Optional[str] = None
    tags: Optional[List[str]] = None
    source_type: str = "cloud_response"
    conversation_id: Optional[str] = None


class ScribeSaveRequest(BaseModel):
    """Request model for Scribe-assisted save."""
    content: str
    title: str
    domain: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None


class MessageSaveRequest(BaseModel):
    """Request model for saving a single message to KB."""
    message_content: str
    message_role: str = "assistant"
    conversation_id: str
    save_mode: str = "quick"  # "quick" or "scribe"
    title: Optional[str] = None
    domain: Optional[str] = None
    tags: Optional[List[str]] = None


def create_settings_router() -> APIRouter:
    """Create settings API router."""
    router = APIRouter(prefix="/api/settings", tags=["settings"])
    
    # Initialize secrets manager
    secrets = get_secrets_manager()
    
    @router.get("/keys")
    async def list_keys():
        """List all API keys (values masked)."""
        try:
            keys_list = secrets.list_secrets()
            return {
                "keys": keys_list,
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to list keys: {e}")
            raise HTTPException(500, f"Failed to list keys: {str(e)}")
    
    @router.post("/keys")
    async def set_key(request: SetKeyRequest):
        """Set or update an API key."""
        try:
            # Validate provider
            valid_providers = ['anthropic', 'openai', 'github', 'grok', 'perplexity', 'gemini', 'mistral', 'openrouter']
            if request.provider not in valid_providers:
                raise HTTPException(400, f"Invalid provider: {request.provider}")
            
            # Store the key
            secrets.set_secret(request.provider, request.key)
            
            # Test the key
            is_valid = False
            error_message = None
            
            try:
                if request.provider == 'openrouter':
                    is_valid = True  # Validated via LiteLLM when used
                else:
                    from core.providers import (
                        AnthropicAdapter,
                        OpenAIAdapter,
                        GitHubModelsAdapter,
                        GrokAdapter,
                        PerplexityAdapter,
                        GeminiAdapter,
                        MistralAdapter,
                    )
                    _adapters = {
                        'anthropic': AnthropicAdapter,
                        'openai': OpenAIAdapter,
                        'github': GitHubModelsAdapter,
                        'grok': GrokAdapter,
                        'perplexity': PerplexityAdapter,
                        'gemini': GeminiAdapter,
                        'mistral': MistralAdapter,
                    }
                    adapter_cls = _adapters.get(request.provider)
                    if adapter_cls:
                        adapter = adapter_cls(request.key)
                        is_valid = await adapter.validate_credentials()
                    else:
                        is_valid = True
            except Exception as e:
                error_message = str(e)
                logger.warning(f"Key validation failed for {request.provider}: {e}")
            
            return {
                "success": True,
                "provider": request.provider,
                "validated": is_valid,
                "error": error_message
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to set key: {e}")
            raise HTTPException(500, f"Failed to set key: {str(e)}")
    
    @router.delete("/keys/{provider}")
    async def delete_key(provider: str):
        """Delete an API key."""
        try:
            valid_providers = ['anthropic', 'openai', 'github', 'grok', 'perplexity', 'gemini', 'mistral', 'openrouter']
            if provider not in valid_providers:
                raise HTTPException(400, f"Invalid provider: {provider}")
            
            deleted = secrets.delete_secret(provider)
            
            if not deleted:
                raise HTTPException(404, f"Key not found for provider: {provider}")
            
            return {
                "success": True,
                "provider": provider,
                "message": "Key deleted successfully"
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete key: {e}")
            raise HTTPException(500, f"Failed to delete key: {str(e)}")
    
    @router.post("/keys/test")
    async def test_keys(request: TestKeyRequest):
        """Test API key connectivity."""
        try:
            providers = [request.provider] if request.provider else ['anthropic', 'openai', 'github', 'grok', 'perplexity', 'gemini', 'mistral', 'openrouter']
            results = {}
            
            for provider in providers:
                key = secrets.get_secret(provider, fallback_to_env=True)
                
                if not key:
                    results[provider] = {
                        "available": False,
                        "valid": False,
                        "error": "Not configured"
                    }
                    continue
                
                try:
                    if provider == 'openrouter':
                        is_valid = True  # No legacy adapter; validated via LiteLLM when used
                    else:
                        from core.providers import (
                            AnthropicAdapter,
                            OpenAIAdapter,
                            GitHubModelsAdapter,
                            GrokAdapter,
                            PerplexityAdapter,
                            GeminiAdapter,
                            MistralAdapter,
                        )
                        _adapters = {
                            'anthropic': AnthropicAdapter,
                            'openai': OpenAIAdapter,
                            'github': GitHubModelsAdapter,
                            'grok': GrokAdapter,
                            'perplexity': PerplexityAdapter,
                            'gemini': GeminiAdapter,
                            'mistral': MistralAdapter,
                        }
                        adapter_cls = _adapters.get(provider)
                        if adapter_cls:
                            adapter = adapter_cls(key)
                            is_valid = await adapter.validate_credentials()
                        else:
                            is_valid = False
                    
                    results[provider] = {
                        "available": True,
                        "valid": is_valid,
                        "error": None if is_valid else "Validation failed"
                    }
                
                except Exception as e:
                    results[provider] = {
                        "available": True,
                        "valid": False,
                        "error": str(e)
                    }
            
            return {
                "success": True,
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Failed to test keys: {e}")
            raise HTTPException(500, f"Failed to test keys: {str(e)}")
    
    @router.get("/budget")
    async def get_budget_status():
        """Get current budget status."""
        try:
            budget = BudgetManager()
            status = await budget.get_budget_status()
            summary = await budget.get_spending_summary()
            
            return {
                "success": True,
                "budget": status,
                "spending": {
                    "total_cost": summary.total_cost,
                    "total_requests": summary.total_requests,
                    "total_tokens": summary.total_tokens_in + summary.total_tokens_out,
                    "by_provider": summary.by_provider,
                    "by_model": summary.by_model
                }
            }
        except Exception as e:
            logger.error(f"Failed to get budget status: {e}")
            raise HTTPException(500, f"Failed to get budget status: {str(e)}")
    
    @router.post("/budget")
    async def update_budget_limits(request: UpdateBudgetRequest):
        """Update budget limits."""
        try:
            budget = BudgetManager()
            
            if request.daily_limit is not None:
                budget.daily_limit = request.daily_limit
            
            if request.monthly_limit is not None:
                budget.monthly_limit = request.monthly_limit
            
            if request.warn_threshold is not None:
                budget.warn_threshold = request.warn_threshold
            
            return {
                "success": True,
                "daily_limit": budget.daily_limit,
                "monthly_limit": budget.monthly_limit,
                "warn_threshold": budget.warn_threshold
            }
        except Exception as e:
            logger.error(f"Failed to update budget: {e}")
            raise HTTPException(500, f"Failed to update budget: {str(e)}")
    
    @router.get("/general")
    async def get_general_settings():
        """Get general Polly settings."""
        try:
            config = get_config()
            return {
                "success": True,
                "settings": {
                    "routing_mode": config.get("router.default_mode", "auto"),
                    "use_litellm": config.get("routing_v2.use_litellm", False)
                }
            }
        except Exception as e:
            logger.error(f"Failed to get general settings: {e}")
            raise HTTPException(500, f"Failed to get general settings: {str(e)}")
    
    @router.post("/general")
    async def update_general_settings(request: Request):
        """Update general Polly settings."""
        try:
            data = await request.json()
            config = get_config()
            config_path = Path("config/config.yaml")
            
            # Load current config
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Update settings
            if "routing_mode" in data:
                if "router" not in config_data:
                    config_data["router"] = {}
                config_data["router"]["default_mode"] = data["routing_mode"]
            
            if "use_litellm" in data:
                if "routing_v2" not in config_data:
                    config_data["routing_v2"] = {}
                config_data["routing_v2"]["use_litellm"] = data["use_litellm"]
            
            # Save config
            with open(config_path, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            
            return {
                "success": True,
                "message": "General settings updated. Restart required for changes to take effect.",
                "settings": {
                    "routing_mode": config_data.get("router", {}).get("default_mode", "auto"),
                    "use_litellm": config_data.get("routing_v2", {}).get("use_litellm", False)
                }
            }
        except Exception as e:
            logger.error(f"Failed to update general settings: {e}")
            raise HTTPException(500, f"Failed to update general settings: {str(e)}")
    
    @router.get("/providers")
    async def get_provider_info():
        """Get information about all providers."""
        try:
            provider_info = {}
            
            for provider, config in secrets.PROVIDER_CONFIGS.items():
                provider_info[provider] = {
                    "name": provider.title(),
                    "description": config['description'],
                    "key_format": config['format'],
                    "env_var": config['env_var']
                }
            
            return {
                "success": True,
                "providers": provider_info
            }
        except Exception as e:
            logger.error(f"Failed to get provider info: {e}")
            raise HTTPException(500, f"Failed to get provider info: {str(e)}")
    
    @router.get("/providers/status")
    async def get_provider_status(request: Request):
        """Get runtime provider status from router (availability, failures, last_success, models). When use_litellm=True, returns litellm adapter stats."""
        try:
            polly = getattr(request.app.state, "polly", None)
            if not polly or not getattr(polly, "router_v2", None):
                return {
                    "success": True,
                    "use_litellm": False,
                    "providers": {},
                    "message": "Router not initialized"
                }
            stats = polly.router_v2.get_provider_stats()
            use_litellm = getattr(polly.router_v2, "use_litellm", False)
            
            # Also load configuration info (enabled status from litellm_config.yaml)
            config = get_config()
            config_status = {}
            
            if use_litellm:
                try:
                    import yaml
                    litellm_config_path = config.get("routing_v2.litellm_config_path", "config/litellm_config.yaml")
                    litellm_config_file = Path(litellm_config_path)
                    if litellm_config_file.exists():
                        with open(litellm_config_file, 'r') as f:
                            litellm_config = yaml.safe_load(f) or {}
                            providers_config = litellm_config.get('providers', {})
                            for provider_name, provider_conf in providers_config.items():
                                has_api_key = bool(secrets.get_secret(provider_name, fallback_to_env=True))
                                config_status[provider_name] = {
                                    'enabled': provider_conf.get('enabled', True),
                                    'has_api_key': has_api_key,
                                    'models': provider_conf.get('models', [])
                                }
                except Exception as e:
                    logger.warning(f"Failed to load litellm config: {e}")
            
            return {
                "success": True,
                "use_litellm": use_litellm,
                "providers": stats,
                "config": config_status
            }
        except Exception as e:
            logger.error(f"Failed to get provider status: {e}")
            raise HTTPException(500, f"Failed to get provider status: {str(e)}")
    
    @router.post("/providers/toggle")
    async def toggle_provider(request: ToggleProviderRequest):
        """Toggle provider enabled status in litellm_config.yaml."""
        try:
            import yaml
            
            config = get_config()
            litellm_config_path = config.get("routing_v2.litellm_config_path", "config/litellm_config.yaml")
            litellm_config_file = Path(litellm_config_path)
            
            if not litellm_config_file.exists():
                raise HTTPException(404, "LiteLLM config file not found")
            
            # Load current config
            with open(litellm_config_file, 'r') as f:
                litellm_config = yaml.safe_load(f) or {}
            
            # Update provider enabled status
            providers = litellm_config.setdefault('providers', {})
            if request.provider not in providers:
                raise HTTPException(404, f"Provider {request.provider} not found in configuration")
            
            providers[request.provider]['enabled'] = request.enabled
            
            # Save updated config
            with open(litellm_config_file, 'w') as f:
                yaml.safe_dump(litellm_config, f, default_flow_style=False)
            
            return {
                "success": True,
                "provider": request.provider,
                "enabled": request.enabled,
                "message": f"Provider {request.provider} {'enabled' if request.enabled else 'disabled'}. Restart required for changes to take effect."
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to toggle provider: {e}")
            raise HTTPException(500, f"Failed to toggle provider: {str(e)}")
    
    @router.post("/providers/test")
    async def test_provider(request: TestProviderRequest):
        """Test a specific provider's connectivity."""
        try:
            # Get API key
            key = secrets.get_secret(request.provider, fallback_to_env=True)
            
            if not key:
                return {
                    "success": False,
                    "provider": request.provider,
                    "available": False,
                    "valid": False,
                    "error": "API key not configured"
                }
            
            # Test based on provider
            if request.provider == 'openrouter':
                # OpenRouter doesn't have a legacy adapter, will be validated via LiteLLM on use
                is_valid = True
                error = None
            else:
                try:
                    from core.providers import (
                        AnthropicAdapter,
                        OpenAIAdapter,
                        GitHubModelsAdapter,
                        GrokAdapter,
                        PerplexityAdapter,
                        GeminiAdapter,
                        MistralAdapter,
                    )
                    _adapters = {
                        'anthropic': AnthropicAdapter,
                        'openai': OpenAIAdapter,
                        'github': GitHubModelsAdapter,
                        'grok': GrokAdapter,
                        'perplexity': PerplexityAdapter,
                        'gemini': GeminiAdapter,
                        'mistral': MistralAdapter,
                    }
                    adapter_cls = _adapters.get(request.provider)
                    if adapter_cls:
                        adapter = adapter_cls(key)
                        is_valid = await adapter.validate_credentials()
                        error = None if is_valid else "Validation failed"
                    else:
                        is_valid = False
                        error = "Provider not supported"
                except Exception as e:
                    is_valid = False
                    error = str(e)
            
            return {
                "success": True,
                "provider": request.provider,
                "available": True,
                "valid": is_valid,
                "error": error
            }
        except Exception as e:
            logger.error(f"Failed to test provider: {e}")
            raise HTTPException(500, f"Failed to test provider: {str(e)}")
    
    @router.get("/compression")
    async def get_compression_settings():
        """Get current compression settings (conversation + RAG/context strategy + semantic trigger)."""
        try:
            config = get_config()
            compression = config._config.get("compression", {})
            rag_context = compression.get("rag_context", {})
            sem_trigger = compression.get("semantic_trigger", {})
            return {
                "success": True,
                "settings": {
                    "enabled": config.compression_enabled,
                    "message_threshold": config.compression_threshold,
                    "age_hours": config.compression_age_hours,
                    "keep_recent": config.compression_keep_recent,
                    "show_stats": config.compression_show_stats,
                    "strategy": compression.get("strategy", "auto"),
                    "rag_context_enabled": rag_context.get("enabled", True),
                    "rag_context_ratio": rag_context.get("ratio", 0.5),
                    # Spec 04
                    "semantic_trigger_enabled": sem_trigger.get("enabled", False),
                    "srs_threshold": sem_trigger.get("srs_threshold", 0.75),
                    "srs_fallback_count": sem_trigger.get("fallback_message_count", 30),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get compression settings: {e}")
            raise HTTPException(500, f"Failed to get compression settings: {str(e)}")
    
    @router.post("/compression")
    async def update_compression_settings(request: UpdateCompressionRequest):
        """Update compression settings."""
        try:
            config = get_config()
            
            # Update config values
            if request.enabled is not None:
                config._config['compression']['enabled'] = request.enabled
            
            if request.message_threshold is not None:
                config._config['compression']['message_threshold'] = request.message_threshold
            
            if request.age_hours is not None:
                config._config['compression']['age_hours'] = request.age_hours
            
            if request.keep_recent is not None:
                config._config['compression']['keep_recent'] = request.keep_recent
            
            if request.show_stats is not None:
                config._config['compression']['show_stats'] = request.show_stats
            
            if request.strategy is not None:
                config._config.setdefault('compression', {})['strategy'] = request.strategy
            if request.rag_context_enabled is not None:
                config._config.setdefault('compression', {}).setdefault('rag_context', {})['enabled'] = request.rag_context_enabled
            if request.rag_context_ratio is not None:
                config._config.setdefault('compression', {}).setdefault('rag_context', {})['ratio'] = max(0.1, min(1.0, request.rag_context_ratio))
            # Spec 04: semantic compression trigger
            if request.semantic_trigger_enabled is not None:
                st = config._config.setdefault('compression', {}).setdefault('semantic_trigger', {})
                st['enabled'] = bool(request.semantic_trigger_enabled)
            if request.srs_threshold is not None:
                st = config._config.setdefault('compression', {}).setdefault('semantic_trigger', {})
                st['srs_threshold'] = round(max(0.0, min(1.0, request.srs_threshold)), 3)
            if request.srs_fallback_count is not None:
                st = config._config.setdefault('compression', {}).setdefault('semantic_trigger', {})
                st['fallback_message_count'] = max(10, min(100, int(request.srs_fallback_count)))

            # Save config to file
            config.save()
            
            compression = config._config.get("compression", {})
            rag_context = compression.get("rag_context", {})
            return {
                "success": True,
                "settings": {
                    "enabled": config.compression_enabled,
                    "message_threshold": config.compression_threshold,
                    "age_hours": config.compression_age_hours,
                    "keep_recent": config.compression_keep_recent,
                    "show_stats": config.compression_show_stats,
                    "strategy": compression.get("strategy", "auto"),
                    "rag_context_enabled": rag_context.get("enabled", True),
                    "rag_context_ratio": rag_context.get("ratio", 0.5),
                },
                "message": "Compression settings updated successfully. Changes will take effect on next restart."
            }
        except Exception as e:
            logger.error(f"Failed to update compression settings: {e}")
            raise HTTPException(500, f"Failed to update compression settings: {str(e)}")
    
    @router.get("/compression/stats")
    async def get_compression_stats():
        """Get compression statistics."""
        try:
            from core.compression import CompressionManager
            
            manager = CompressionManager()
            
            # Get all compression stats
            all_conversations = manager.list_compressed_conversations()
            
            total_original = 0
            total_compressed = 0
            total_count = len(all_conversations)
            
            recent_compressions = []
            
            for conv_id in all_conversations:
                stats = manager.get_compression_stats(conv_id)
                if stats:
                    total_original += stats['original_tokens']
                    total_compressed += stats['compressed_tokens']
                    
                    recent_compressions.append({
                        'conversation_id': conv_id,
                        'original_tokens': stats['original_tokens'],
                        'compressed_tokens': stats['compressed_tokens'],
                        'ratio': stats['compression_ratio'],
                        'created_at': stats['compressed_at']
                    })
            
            # Sort by date, most recent first
            recent_compressions.sort(key=lambda x: x['created_at'], reverse=True)
            recent_compressions = recent_compressions[:10]  # Top 10
            
            total_saved = total_original - total_compressed
            savings_percent = (total_saved / total_original * 100) if total_original > 0 else 0
            avg_ratio = (total_original / total_compressed) if total_compressed > 0 else 0
            
            return {
                "success": True,
                "stats": {
                    "total_conversations": total_count,
                    "total_original_tokens": total_original,
                    "total_compressed_tokens": total_compressed,
                    "total_saved_tokens": total_saved,
                    "savings_percent": round(savings_percent, 1),
                    "average_ratio": round(avg_ratio, 1),
                    "recent_compressions": recent_compressions
                }
            }
        except Exception as e:
            logger.error(f"Failed to get compression stats: {e}")
            # Return empty stats instead of error
            return {
                "success": True,
                "stats": {
                    "total_conversations": 0,
                    "total_original_tokens": 0,
                    "total_compressed_tokens": 0,
                    "total_saved_tokens": 0,
                    "savings_percent": 0,
                    "average_ratio": 0,
                    "recent_compressions": []
                }
            }
    
    # ===== Semantic Cache Settings =====
    
    @router.get("/semantic-cache")
    async def get_semantic_cache_settings():
        """Get semantic cache settings."""
        try:
            config = get_config()
            cache = config._config.get("semantic_cache", {})
            return {
                "success": True,
                "settings": {
                    "enabled": cache.get("enabled", False),
                    "similarity_threshold": cache.get("similarity_threshold", 0.92),
                    "max_entries": cache.get("max_entries", 500),
                    "ttl_hours": cache.get("ttl_hours", 24),
                    "min_response_tokens": cache.get("min_response_tokens", 50),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get semantic cache settings: {e}")
            raise HTTPException(500, f"Failed to get semantic cache settings: {str(e)}")
    
    @router.post("/semantic-cache")
    async def update_semantic_cache_settings(request: Dict[str, Any]):
        """Update semantic cache settings."""
        try:
            config = get_config()
            
            if "semantic_cache" not in config._config:
                config._config["semantic_cache"] = {}
            
            cache_config = config._config["semantic_cache"]
            
            if "enabled" in request:
                cache_config["enabled"] = bool(request["enabled"])
            
            if "similarity_threshold" in request:
                cache_config["similarity_threshold"] = float(request["similarity_threshold"])
            
            if "max_entries" in request:
                cache_config["max_entries"] = int(request["max_entries"])
            
            if "ttl_hours" in request:
                cache_config["ttl_hours"] = int(request["ttl_hours"])
            
            if "min_response_tokens" in request:
                cache_config["min_response_tokens"] = int(request["min_response_tokens"])
            
            # Note: Changes require server restart to take effect
            # Could be enhanced to dynamically update Polly.semantic_cache instance
            return {
                "success": True,
                "message": "Semantic cache settings updated. Restart server to apply changes."
            }
        except Exception as e:
            logger.error(f"Failed to update semantic cache settings: {e}")
            raise HTTPException(500, f"Failed to update semantic cache settings: {str(e)}")
    
    @router.get("/semantic-cache/stats")
    async def get_semantic_cache_stats():
        """Get semantic cache statistics."""
        try:
            from core.cache import get_semantic_cache
            
            cache = get_semantic_cache()
            if not cache:
                return {
                    "success": True,
                    "stats": {
                        "total_entries": 0,
                        "hit_count": 0,
                        "miss_count": 0,
                        "hit_rate": 0,
                        "tokens_saved": 0,
                    }
                }
            
            stats = cache.stats()
            return {
                "success": True,
                "stats": {
                    "total_entries": stats.total_entries,
                    "hit_count": stats.hit_count,
                    "miss_count": stats.miss_count,
                    "hit_rate": round(stats.hit_rate * 100, 1),
                    "tokens_saved": stats.tokens_saved,
                    "oldest_entry_hours": round(stats.oldest_entry_hours, 1),
                    "newest_entry_hours": round(stats.newest_entry_hours, 1),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get semantic cache stats: {e}")
            return {
                "success": True,
                "stats": {
                    "total_entries": 0,
                    "hit_count": 0,
                    "miss_count": 0,
                    "hit_rate": 0,
                    "tokens_saved": 0,
                }
            }

    # ===== Memory Settings =====

    @router.get("/memory")
    async def get_memory_settings():
        """Get memory provider settings (local vs Mem0)."""
        try:
            config = get_config()
            memory = config._config.get("memory", {})
            mem0 = memory.get("mem0", {})
            return {
                "success": True,
                "settings": {
                    "provider": memory.get("provider", "local"),
                    "mem0_enabled": mem0.get("enabled", False),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get memory settings: {e}")
            raise HTTPException(500, f"Failed to get memory settings: {str(e)}")

    @router.post("/memory")
    async def update_memory_settings(request: UpdateMemoryRequest):
        """Update memory provider settings."""
        try:
            config = get_config()
            config._config.setdefault("memory", {})
            if request.provider is not None:
                config._config["memory"]["provider"] = request.provider
            if request.mem0_enabled is not None:
                config._config["memory"].setdefault("mem0", {})["enabled"] = request.mem0_enabled
            config.save()
            memory = config._config.get("memory", {})
            mem0 = memory.get("mem0", {})
            return {
                "success": True,
                "settings": {
                    "provider": memory.get("provider", "local"),
                    "mem0_enabled": mem0.get("enabled", False),
                },
                "message": "Memory settings updated. Changes take effect on next restart."
            }
        except Exception as e:
            logger.error(f"Failed to update memory settings: {e}")
            raise HTTPException(500, f"Failed to update memory settings: {str(e)}")

    # ===== AI Features Settings =====

    @router.get("/ai-features")
    async def get_ai_features():
        """Get AI features configuration (knowledge suggestions, autonomy dashboard, context persistence, MM format)."""
        try:
            config = get_config()
            ai_features = config.get('ai_features', {}) or {}
            ks = ai_features.get('knowledge_suggestions', {}) or {}
            ad = ai_features.get('autonomy_dashboard', {}) or {}
            # Spec 03
            cb_rolling = (config._config.get('context_budget', {}) or {}).get('rolling', {}) or {}
            # Spec 07
            mm_compression = (config._config.get('mental_models', {}) or {}).get('compression', {}) or {}
            mm_ab = mm_compression.get('ab_test', {}) or {}

            return {
                "success": True,
                "ai_features": {
                    "knowledge_suggestions": {
                        "enabled": ks.get('enabled', True),
                        "style": ks.get('style', 'inline'),
                        "min_gap_score": ks.get('min_gap_score', 0.5),
                    },
                    "autonomy_dashboard": {
                        "enabled": ad.get('enabled', True),
                        "show_in_status_bar": ad.get('show_in_status_bar', True),
                    },
                    # Spec 03
                    "context_persistence": {
                        "enabled": cb_rolling.get('persist_across_sessions', True),
                        "decay_on_gap_hours": cb_rolling.get('decay_on_gap_hours', 12),
                    },
                    # Spec 07
                    "mm_format": "ab_test" if mm_ab.get('enabled', True) else mm_compression.get('format', 'compact'),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get AI features: {e}")
            raise HTTPException(500, f"Failed to get AI features: {str(e)}")

    @router.put("/ai-features")
    async def update_ai_features(request: UpdateAIFeaturesRequest):
        """Update AI features configuration."""
        try:
            config = get_config()

            # Ensure ai_features section exists
            if 'ai_features' not in config._config:
                config._config['ai_features'] = {}
            af = config._config['ai_features']

            if 'knowledge_suggestions' not in af:
                af['knowledge_suggestions'] = {}
            ks = af['knowledge_suggestions']

            if 'autonomy_dashboard' not in af:
                af['autonomy_dashboard'] = {}
            ad = af['autonomy_dashboard']

            # Apply updates
            if request.knowledge_suggestions_enabled is not None:
                ks['enabled'] = request.knowledge_suggestions_enabled
            if request.knowledge_suggestions_style is not None:
                valid_styles = ['subtle', 'inline', 'ask_first']
                if request.knowledge_suggestions_style not in valid_styles:
                    raise HTTPException(
                        400,
                        f"Invalid style: {request.knowledge_suggestions_style}. "
                        f"Must be one of: {valid_styles}"
                    )
                ks['style'] = request.knowledge_suggestions_style
            if request.knowledge_suggestions_min_gap_score is not None:
                score = request.knowledge_suggestions_min_gap_score
                if not (0.0 <= score <= 1.0):
                    raise HTTPException(400, "min_gap_score must be between 0.0 and 1.0")
                ks['min_gap_score'] = score
            if request.autonomy_dashboard_enabled is not None:
                ad['enabled'] = request.autonomy_dashboard_enabled
            if request.autonomy_dashboard_show_in_status_bar is not None:
                ad['show_in_status_bar'] = request.autonomy_dashboard_show_in_status_bar
            # Accept flat autonomy_dashboard bool from frontend POST payload
            if request.autonomy_dashboard is not None:
                ad['enabled'] = request.autonomy_dashboard
            # Accept flat kb_suggestions / gap_score_threshold from frontend
            if request.kb_suggestions is not None:
                ks['enabled'] = request.kb_suggestions
            if request.gap_score_threshold is not None:
                ks['min_gap_score'] = request.gap_score_threshold

            # Semantic cache settings (Spec 01)
            if request.semantic_cache is not None:
                sc = request.semantic_cache
                if 'semantic_cache' not in config._config:
                    config._config['semantic_cache'] = {}
                cache_cfg = config._config['semantic_cache']
                if 'enabled' in sc:
                    cache_cfg['enabled'] = sc['enabled']
                if 'similarity_threshold' in sc:
                    cache_cfg['similarity_threshold'] = float(sc['similarity_threshold'])
                if 'ttl_hours' in sc:
                    cache_cfg['ttl_hours'] = int(sc['ttl_hours'])
                if 'max_entries' in sc:
                    cache_cfg['max_entries'] = int(sc['max_entries'])

            # Spec 03: context persistence settings
            if request.context_persistence is not None:
                cp = request.context_persistence
                if 'context_budget' not in config._config:
                    config._config['context_budget'] = {}
                if 'rolling' not in config._config['context_budget']:
                    config._config['context_budget']['rolling'] = {}
                rolling = config._config['context_budget']['rolling']
                if 'enabled' in cp:
                    rolling['persist_across_sessions'] = bool(cp['enabled'])
                if 'decay_on_gap_hours' in cp:
                    rolling['decay_on_gap_hours'] = max(1, min(72, int(cp['decay_on_gap_hours'])))

            # Spec 07: mental model compression format
            if request.mm_format is not None:
                valid_formats = ['compact', 'full', 'ab_test']
                if request.mm_format in valid_formats:
                    if 'mental_models' not in config._config:
                        config._config['mental_models'] = {}
                    if 'compression' not in config._config['mental_models']:
                        config._config['mental_models']['compression'] = {}
                    mm_comp = config._config['mental_models']['compression']
                    if request.mm_format == 'ab_test':
                        mm_comp['format'] = 'compact'
                        if 'ab_test' not in mm_comp:
                            mm_comp['ab_test'] = {}
                        mm_comp['ab_test']['enabled'] = True
                    else:
                        mm_comp['format'] = request.mm_format
                        if 'ab_test' not in mm_comp:
                            mm_comp['ab_test'] = {}
                        mm_comp['ab_test']['enabled'] = False

            # Save config to file
            config.save()

            # Update the running KnowledgeWriter if available
            try:
                from core.knowledge_writer import get_knowledge_writer
                kw = get_knowledge_writer()
                if kw:
                    kw.update_settings({
                        'enabled': ks.get('enabled', True),
                        'style': ks.get('style', 'inline'),
                        'min_gap_score': ks.get('min_gap_score', 0.5),
                    })
            except Exception:
                pass  # KnowledgeWriter may not be initialized yet

            return {
                "success": True,
                "ai_features": {
                    "knowledge_suggestions": ks,
                    "autonomy_dashboard": ad,
                },
                "message": "AI features settings updated successfully."
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update AI features: {e}")
            raise HTTPException(500, f"Failed to update AI features: {str(e)}")

    @router.post("/ai-features")
    async def post_ai_features(request: UpdateAIFeaturesRequest):
        """POST alias for PUT /ai-features (frontend compatibility)."""
        return await update_ai_features(request)

    # ===== Knowledge Writing Endpoints =====

    @router.post("/knowledge/save-quick")
    async def knowledge_save_quick(request: QuickSaveRequest):
        """Quick save knowledge from AI suggestion or context menu (no LLM call)."""
        try:
            from core.knowledge_writer import get_knowledge_writer
            kw = get_knowledge_writer()
            if not kw:
                raise HTTPException(503, "KnowledgeWriter not initialized")

            result = await kw.quick_save(
                content=request.content,
                title=request.title,
                domain=request.domain,
                tags=request.tags,
                source_type=request.source_type,
                conversation_id=request.conversation_id,
            )
            return result.to_dict()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Quick save failed: {e}", exc_info=True)
            raise HTTPException(500, f"Quick save failed: {str(e)}")

    @router.post("/knowledge/save-scribe")
    async def knowledge_save_scribe(request: ScribeSaveRequest):
        """Route through Scribe Enrich mode for wiki-linking and rich formatting."""
        try:
            from core.knowledge_writer import get_knowledge_writer
            kw = get_knowledge_writer()
            if not kw:
                raise HTTPException(503, "KnowledgeWriter not initialized")

            result = await kw.scribe_save(
                content=request.content,
                title=request.title,
                domain=request.domain,
                conversation_history=request.conversation_history,
            )
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Scribe save failed: {e}", exc_info=True)
            raise HTTPException(500, f"Scribe save failed: {str(e)}")

    @router.get("/autonomy/snapshot")
    async def get_autonomy_snapshot(days: int = 30):
        """Get autonomy metrics snapshot for the dashboard."""
        try:
            from core.autonomy_metrics import get_autonomy_metrics
            metrics = get_autonomy_metrics()
            if not metrics:
                return {"success": True, "snapshot": {
                    "knowledge_writes_count": 0,
                    "estimated_tokens_saved": 0,
                    "local_routing_pct": 0,
                    "cloud_routing_pct": 0,
                    "total_queries": 0,
                    "period_days": days,
                }}
            snapshot = metrics.get_snapshot(days=days)
            return {"success": True, "snapshot": snapshot.to_dict()}
        except Exception as e:
            logger.error(f"Failed to get autonomy snapshot: {e}")
            raise HTTPException(500, f"Failed to get autonomy snapshot: {str(e)}")

    @router.get("/autonomy/recent-writes")
    async def get_autonomy_recent_writes(limit: int = 10):
        """Get recent knowledge writes for the dashboard."""
        try:
            from core.autonomy_metrics import get_autonomy_metrics
            metrics = get_autonomy_metrics()
            if not metrics:
                return {"success": True, "writes": []}
            writes = metrics.get_recent_writes(limit=limit)
            return {"success": True, "writes": writes}
        except Exception as e:
            logger.error(f"Failed to get recent writes: {e}")
            raise HTTPException(500, f"Failed to get recent writes: {str(e)}")

    @router.get("/autonomy/routing-trend")
    async def get_autonomy_routing_trend(days: int = 30):
        """Get routing trend over time for the dashboard."""
        try:
            from core.autonomy_metrics import get_autonomy_metrics
            metrics = get_autonomy_metrics()
            if not metrics:
                return {"success": True, "trend": []}
            trend = metrics.get_routing_trend(days=days)
            return {"success": True, "trend": trend}
        except Exception as e:
            logger.error(f"Failed to get routing trend: {e}")
            raise HTTPException(500, f"Failed to get routing trend: {str(e)}")

    @router.post("/knowledge/save-message")
    async def knowledge_save_message(request: MessageSaveRequest):
        """Save a single message from chat to the knowledge base."""
        try:
            from core.knowledge_writer import get_knowledge_writer
            kw = get_knowledge_writer()
            if not kw:
                raise HTTPException(503, "KnowledgeWriter not initialized")

            result = await kw.save_message(
                message_content=request.message_content,
                message_role=request.message_role,
                conversation_id=request.conversation_id,
                save_mode=request.save_mode,
                title=request.title,
                domain=request.domain,
                tags=request.tags,
            )

            # Normalize result
            if hasattr(result, 'to_dict'):
                return result.to_dict()
            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Message save failed: {e}", exc_info=True)
            raise HTTPException(500, f"Message save failed: {str(e)}")

    @router.get("/rag")
    async def get_rag_settings():
        """Get current RAG & retrieval classifier settings."""
        try:
            config = get_config()
            rag = config._config.get("rag", {})
            clf = rag.get("retrieval_classifier", {})
            decomp = config._config.get("routing", {}).get("decomposition", {})
            bm25_cfg = rag.get("bm25", {})
            return {
                "success": True,
                "settings": {
                    "n_results": rag.get("n_results", 5),
                    "direct_threshold": clf.get("direct_threshold", 0.72),
                    "adjacent_threshold": clf.get("adjacent_threshold", 0.5),
                    "domain_match_boost": clf.get("domain_match_boost", 0.1),
                    "cross_domain_penalty": clf.get("cross_domain_penalty", 0.15),
                    "decomposition_enabled": decomp.get("enabled", True),
                    "min_complexity_score": decomp.get("min_complexity_score", 0.6),
                    # Spec 08
                    "bm25_persist": bm25_cfg.get("persist", True),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get RAG settings: {e}")
            raise HTTPException(500, f"Failed to get RAG settings: {str(e)}")

    @router.post("/rag")
    async def update_rag_settings(request: UpdateRAGRequest):
        """Update RAG & retrieval classifier settings."""
        try:
            config = get_config()
            cfg = config._config

            rag = cfg.setdefault("rag", {})
            clf = rag.setdefault("retrieval_classifier", {})
            decomp = cfg.setdefault("routing", {}).setdefault("decomposition", {})

            if request.n_results is not None:
                rag["n_results"] = max(1, min(20, request.n_results))
            if request.direct_threshold is not None:
                clf["direct_threshold"] = round(max(0.5, min(0.95, request.direct_threshold)), 3)
            if request.adjacent_threshold is not None:
                clf["adjacent_threshold"] = round(max(0.3, min(0.8, request.adjacent_threshold)), 3)
            if request.domain_match_boost is not None:
                clf["domain_match_boost"] = round(max(0.0, min(0.3, request.domain_match_boost)), 3)
            if request.cross_domain_penalty is not None:
                clf["cross_domain_penalty"] = round(max(0.0, min(0.3, request.cross_domain_penalty)), 3)
            if request.decomposition_enabled is not None:
                decomp["enabled"] = request.decomposition_enabled
            if request.min_complexity_score is not None:
                decomp["min_complexity_score"] = round(max(0.0, min(1.0, request.min_complexity_score)), 3)
            # Spec 08: BM25 persistence
            if request.bm25_persist is not None:
                bm25_cfg = rag.setdefault("bm25", {})
                bm25_cfg["persist"] = bool(request.bm25_persist)

            config.save()

            return {
                "success": True,
                "settings": {
                    "n_results": rag.get("n_results", 5),
                    "direct_threshold": clf.get("direct_threshold", 0.72),
                    "adjacent_threshold": clf.get("adjacent_threshold", 0.5),
                    "domain_match_boost": clf.get("domain_match_boost", 0.1),
                    "cross_domain_penalty": clf.get("cross_domain_penalty", 0.15),
                    "decomposition_enabled": decomp.get("enabled", True),
                    "min_complexity_score": decomp.get("min_complexity_score", 0.6),
                    "bm25_persist": rag.get("bm25", {}).get("persist", True),
                },
                "message": "RAG settings updated. Classifier changes take effect immediately; n_results and BM25 require restart."
            }
        except Exception as e:
            logger.error(f"Failed to update RAG settings: {e}")
            raise HTTPException(500, f"Failed to update RAG settings: {str(e)}")

    return router

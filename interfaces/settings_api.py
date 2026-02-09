"""
Settings API Endpoints for Polly
Handles API key management, provider configuration, and budget settings
"""

from fastapi import APIRouter, HTTPException, Depends
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


class UpdateAIFeaturesRequest(BaseModel):
    """Request model for updating AI features settings."""
    knowledge_suggestions_enabled: Optional[bool] = None
    knowledge_suggestions_style: Optional[str] = None  # "subtle" | "inline" | "ask_first"
    knowledge_suggestions_min_gap_score: Optional[float] = None
    autonomy_dashboard_enabled: Optional[bool] = None
    autonomy_dashboard_show_in_status_bar: Optional[bool] = None


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
            valid_providers = ['anthropic', 'openai', 'github', 'grok', 'perplexity', 'gemini', 'mistral']
            if request.provider not in valid_providers:
                raise HTTPException(400, f"Invalid provider: {request.provider}")
            
            # Store the key
            secrets.set_secret(request.provider, request.key)
            
            # Test the key
            is_valid = False
            error_message = None
            
            try:
                if request.provider == 'anthropic':
                    from core.providers.anthropic_provider import AnthropicAdapter
                    adapter = AnthropicAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
                elif request.provider == 'openai':
                    from core.providers.openai_provider import OpenAIAdapter
                    adapter = OpenAIAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
                elif request.provider == 'github':
                    from core.providers.github_provider import GitHubModelsAdapter
                    adapter = GitHubModelsAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
                elif request.provider == 'grok':
                    from core.providers.grok_provider import GrokAdapter
                    adapter = GrokAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
                elif request.provider == 'perplexity':
                    from core.providers.perplexity_provider import PerplexityAdapter
                    adapter = PerplexityAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
                elif request.provider == 'gemini':
                    from core.providers.gemini_provider import GeminiAdapter
                    adapter = GeminiAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
                elif request.provider == 'mistral':
                    from core.providers.mistral_provider import MistralAdapter
                    adapter = MistralAdapter(request.key)
                    is_valid = await adapter.validate_credentials()
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
            valid_providers = ['anthropic', 'openai', 'github', 'grok', 'perplexity', 'gemini', 'mistral']
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
            providers = [request.provider] if request.provider else ['anthropic', 'openai', 'github', 'grok', 'perplexity', 'gemini', 'mistral']
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
                    if provider == 'anthropic':
                        from core.providers.anthropic_provider import AnthropicAdapter
                        adapter = AnthropicAdapter(key)
                        is_valid = await adapter.validate_credentials()
                    elif provider == 'openai':
                        from core.providers.openai_provider import OpenAIAdapter
                        adapter = OpenAIAdapter(key)
                        is_valid = await adapter.validate_credentials()
                    elif provider == 'github':
                        from core.providers.github_provider import GitHubModelsAdapter
                        adapter = GitHubModelsAdapter(key)
                        is_valid = await adapter.validate_credentials()
                    elif provider == 'grok':
                        from core.providers.grok_provider import GrokAdapter
                        adapter = GrokAdapter(key)
                        is_valid = await adapter.validate_credentials()
                    elif provider == 'perplexity':
                        from core.providers.perplexity_provider import PerplexityAdapter
                        adapter = PerplexityAdapter(key)
                        is_valid = await adapter.validate_credentials()
                    elif provider == 'gemini':
                        from core.providers.gemini_provider import GeminiAdapter
                        adapter = GeminiAdapter(key)
                        is_valid = await adapter.validate_credentials()
                    elif provider == 'mistral':
                        from core.providers.mistral_provider import MistralAdapter
                        adapter = MistralAdapter(key)
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
    
    @router.get("/compression")
    async def get_compression_settings():
        """Get current compression settings."""
        try:
            config = get_config()
            
            return {
                "success": True,
                "settings": {
                    "enabled": config.compression_enabled,
                    "message_threshold": config.compression_threshold,
                    "age_hours": config.compression_age_hours,
                    "keep_recent": config.compression_keep_recent,
                    "show_stats": config.compression_show_stats
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
            
            # Save config to file
            config.save()
            
            return {
                "success": True,
                "settings": {
                    "enabled": config.compression_enabled,
                    "message_threshold": config.compression_threshold,
                    "age_hours": config.compression_age_hours,
                    "keep_recent": config.compression_keep_recent,
                    "show_stats": config.compression_show_stats
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
    
    # ===== AI Features Settings =====

    @router.get("/ai-features")
    async def get_ai_features():
        """Get AI features configuration (knowledge suggestions, autonomy dashboard)."""
        try:
            config = get_config()
            ai_features = config.get('ai_features', {}) or {}
            ks = ai_features.get('knowledge_suggestions', {}) or {}
            ad = ai_features.get('autonomy_dashboard', {}) or {}

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
                    }
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

    return router

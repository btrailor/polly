"""
Polly API Server
OpenAI-compatible API for IDE integration and remote access

Endpoints:
- POST /v1/chat/completions - OpenAI-compatible chat
- POST /polly/query - Direct Polly query
- POST /polly/index - Trigger indexing
- GET /polly/stats - Get statistics
- GET /health - Health check

Persona Endpoints (Phase 11c):
- POST /persona/activate - Activate a persona
- POST /persona/process - Process input with active persona
- POST /persona/switch-mode - Switch persona mode
- GET /persona/state - Get current persona state
- GET /persona/list - List available personas
- POST /persona/deactivate - Deactivate current persona
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import asyncio
import json
import os
import time
import logging
import re

logger = logging.getLogger(__name__)

# Optional: enable debug logs (e.g. iCloud timeouts, file watcher) via POLLY_LOG_LEVEL=DEBUG
if os.environ.get("POLLY_LOG_LEVEL", "").upper() == "DEBUG":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    logger.info("POLLY_LOG_LEVEL=DEBUG: debug logging enabled")

# Phase 23.5: Security Hardening
# Import security policy lazily to avoid startup failures
try:
    from core.security_policy import get_security_policy
    SECURITY_POLICY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security policy module not available: {e}. Security features disabled.")
    SECURITY_POLICY_AVAILABLE = False
    def get_security_policy():
        """Fallback if security policy module unavailable."""
        return None


# Request/Response models
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "polly"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False
    # Polly-specific
    mode: Optional[str] = "auto"  # local, cloud, auto
    tier: Optional[str] = "balanced"  # fast, balanced, quality


class PollyQueryRequest(BaseModel):
    query: str
    context: Optional[Dict] = None
    mode: Optional[str] = "auto"  # Router v1: local/cloud/auto
    tier: Optional[str] = "balanced"  # Router v1: fast/balanced/quality
    stream: Optional[bool] = True
    conversation_history: Optional[List[Dict]] = None
    # Router v2 parameters
    confidence: Optional[str] = None  # Router v2: fast/balanced/thorough
    provider_override: Optional[str] = None  # Router v2: openai/anthropic/github
    # Mental models parameters (Phase 14)
    page: Optional[str] = None  # Current page/view
    persona: Optional[str] = None  # Active persona
    persona_mode: Optional[str] = None  # Active mode within persona
    mental_models_override: Optional[List[str]] = None  # Override active models for this query


class IndexRequest(BaseModel):
    obsidian: bool = True
    codebases: bool = True
    force: bool = False


class IntegrationConnectRequest(BaseModel):
    integration: str
    credentials: Dict[str, str]


class IntegrationSyncRequest(BaseModel):
    integration: str
    options: Optional[Dict[str, Any]] = None


class LearnFromConversationRequest(BaseModel):
    conversation_id: str
    messages: List[Message]
    category: Optional[str] = None


class ConversationSyncRequest(BaseModel):
    """Sync conversation buffer from Electron (integration-contracts)."""
    messages: List[Dict[str, str]]  # [{role, content}, ...]; timestamp optional
    conversation_id: Optional[str] = None


class PersonaActivateRequest(BaseModel):
    persona_name: str


class PersonaSwitchModeRequest(BaseModel):
    mode: str


# Phase 23.5: Security Hardening - Helper Functions

def _expand_cors_origins(origins: List[str]) -> List[str]:
    """
    Expand CORS origins, handling wildcard ports and CIDR ranges.
    
    FastAPI CORSMiddleware doesn't support wildcards directly, so we expand:
    - http://localhost:* -> http://localhost:3000, http://localhost:3001, etc.
    - http://100.64.0.0/10 -> individual IPs in range (simplified: allow all in range)
    """
    expanded = []
    common_ports = [3000, 3001, 3002, 4000, 5000, 5173, 5174, 8080, 8081, 8888, 11436]
    
    for origin in origins:
        # Handle wildcard ports: http://localhost:* -> expand to common ports
        if origin.endswith(":*"):
            base = origin[:-2]  # Remove ":*"
            for port in common_ports:
                expanded.append(f"{base}:{port}")
            # Also add base without port (defaults to 80/443)
            expanded.append(base)
        
        # Handle CIDR ranges: http://100.64.0.0/10
        # For simplicity, we'll allow the base network and log a note
        # In production, you might want to validate against the actual requesting IP
        elif "/" in origin:
            # FastAPI will need to validate this at request time
            # For now, add the base network
            base = origin.split("/")[0]
            expanded.append(base)
            logger.info(f"CORS CIDR range configured: {origin} (will validate at request time)")
        
        # Standard origin
        else:
            expanded.append(origin)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_origins = []
    for origin in expanded:
        if origin not in seen:
            seen.add(origin)
            unique_origins.append(origin)
    
    logger.info(f"CORS origins configured: {len(unique_origins)} origins")
    return unique_origins


class InputValidationMiddleware(BaseHTTPMiddleware):
    """
    Phase 23.5: Security Hardening - Input Validation Middleware
    
    Validates and sanitizes request input to prevent injection attacks.
    """
    
    # Paths that don't need strict validation (health checks, static files)
    EXEMPT_PATHS = ["/health", "/static", "/docs", "/openapi.json", "/redoc"]
    
    # Maximum request body size (10MB)
    MAX_BODY_SIZE = 10 * 1024 * 1024
    
    async def dispatch(self, request: StarletteRequest, call_next):
        # Skip validation for exempt paths
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Check request body size
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    size = int(content_length)
                    if size > self.MAX_BODY_SIZE:
                        logger.warning(f"Request body too large: {size} bytes from {request.client.host}")
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={"error": "Request body too large"}
                        )
                except ValueError:
                    pass
        
        # Validate and sanitize JSON payloads
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                body = await request.body()
                if body:
                    # Parse JSON to validate structure
                    try:
                        json_data = json.loads(body)
                        # Basic sanitization: check for suspicious patterns
                        if self._contains_suspicious_content(json_data):
                            logger.warning(f"Suspicious content detected in request from {request.client.host}")
                            # Don't block, but log it (warn-only for personal use)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid JSON in request from {request.client.host}")
                        return JSONResponse(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            content={"error": "Invalid JSON"}
                        )
            except Exception as e:
                logger.error(f"Error validating request body: {e}")
                # Continue processing - don't block on validation errors
        
        # Continue to next middleware/handler
        response = await call_next(request)
        return response
    
    def _contains_suspicious_content(self, data: Any) -> bool:
        """Check for suspicious patterns in request data."""
        if isinstance(data, dict):
            return any(self._contains_suspicious_content(v) for v in data.values())
        elif isinstance(data, list):
            return any(self._contains_suspicious_content(item) for item in data)
        elif isinstance(data, str):
            # Check for common injection patterns
            suspicious_patterns = [
                r'<script[^>]*>',  # Script tags
                r'javascript:',     # JavaScript protocol
                r'on\w+\s*=',      # Event handlers (onclick=, etc.)
                r'data:text/html', # Data URIs
            ]
            for pattern in suspicious_patterns:
                if re.search(pattern, data, re.IGNORECASE):
                    return True
        return False


def create_app(polly_instance=None) -> FastAPI:
    """Create FastAPI app with Polly integration."""

    app = FastAPI(
        title="Polly API",
        description="Edge-native personal AI assistant",
        version="0.1.0"
    )

    # Conversation sync (integration-contracts) — register before any middleware so it always exists
    async def _sync_conversation_handler(request: ConversationSyncRequest):
        polly = getattr(app.state, "polly", None)
        if polly is None:
            return JSONResponse(
                status_code=503,
                content={"status": "initializing", "message": "Polly not ready"},
            )
        polly.conversation_history = [
            {"role": m.get("role", "user"), "content": m.get("content", "")}
            for m in request.messages
        ]
        return {"status": "synced", "message_count": len(polly.conversation_history)}

    app.add_api_route(
        "/polly/conversation/sync",
        _sync_conversation_handler,
        methods=["POST"],
        response_model=None,
    )

    # Phase 23.5: Security Hardening - CORS Policy
    # Load security policy and configure CORS
    cors_configured = False
    if SECURITY_POLICY_AVAILABLE:
        try:
            security_policy = get_security_policy()
            if security_policy is not None:
                cors_config = security_policy.get_cors_config()
                
                # Expand wildcard ports for common development ports
                # FastAPI CORSMiddleware doesn't support wildcards, so we expand them
                expanded_origins = _expand_cors_origins(cors_config["allow_origins"])
                
                app.add_middleware(
                    CORSMiddleware,
                    allow_origins=expanded_origins,
                    allow_credentials=cors_config["allow_credentials"],
                    allow_methods=cors_config["allow_methods"],
                    allow_headers=cors_config["allow_headers"],
                )
                
                logger.info(f"Security hardening: CORS configured with {len(expanded_origins)} origins")
                cors_configured = True
        except Exception as e:
            # Fallback to permissive CORS if security policy fails to load
            logger.error(f"Failed to load security policy: {e}. Using permissive CORS (fallback).")
    
    if not cors_configured:
        # Fallback CORS configuration
        # Include both localhost and 127.0.0.1 with common ports
        fallback_origins = [
            "http://localhost:3000",
            "http://localhost:11436",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:11436",
            "http://localhost",  # No port (defaults to 80, but browser may use it)
            "http://127.0.0.1",  # No port
        ]
        logger.info(f"Using fallback CORS configuration with {len(fallback_origins)} origins")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=fallback_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Phase 23.5: Security Hardening - Input Validation Middleware
    try:
        app.add_middleware(InputValidationMiddleware)
        logger.info("Security hardening: Input validation middleware enabled")
    except Exception as e:
        logger.error(f"Failed to add input validation middleware: {e}")
    
    # Mount static files for web UI
    web_dir = Path(__file__).parent.parent / "web"
    if web_dir.exists():
        app.mount("/static", StaticFiles(directory=str(web_dir / "static")), name="static")

    # Include settings API router
    from interfaces.settings_api import create_settings_router
    app.include_router(create_settings_router())
    
    # Memory API (Phase 1.5: Mem0 Adaptive Memory)
    try:
        from interfaces.memory_api import router as memory_router
        app.include_router(memory_router)
        logger.info("Memory API endpoints registered")
    except ImportError as e:
        logger.warning(f"Memory API not available: {e}")

    # Store Polly instance
    app.state.polly = polly_instance
    
    # Initialize integration manager
    app.state.integration_manager = None
    
    # Initialize Obsidian smart features
    app.state.obsidian_smart = None

    def get_polly():
        """
        Get Polly instance if available.
        
        Returns None if Polly is still initializing or failed to initialize.
        Endpoints should check for None and return appropriate status.
        """
        return app.state.polly
    
    def get_integration_manager():
        """Get integration manager, initializing if needed."""
        if app.state.integration_manager is None:
            try:
                from integrations import (
                    IntegrationManager, 
                    GitHubIntegration, 
                    Context7Integration,
                    RemindersIntegration,
                    ObsidianIntegration
                )
                from integrations.calendar_applescript_fast import CalendarIntegration
                from integrations.filesystem import FileSystemIntegration
            except ImportError as e:
                logger.error(f"Failed to import integrations: {e}")
                # Return a stub manager if imports fail
                class StubManager:
                    async def restore_connections(self): pass
                    def get_integration(self, name): return None
                app.state.integration_manager = StubManager()
                return app.state.integration_manager
            
            manager = IntegrationManager()
            
            # Register available integrations
            manager.register_integration(GitHubIntegration())
            manager.register_integration(Context7Integration())
            
            # Obsidian integration (read/write)
            polly = get_polly()
            vault_path = polly.config.get("obsidian.vault_path")
            if vault_path:
                logger.info(f"Registering Obsidian integration with vault: {vault_path}")
                manager.register_integration(ObsidianIntegration(vault_path=vault_path))
            else:
                logger.warning("Obsidian vault path not configured")
            
            # macOS integrations disabled until Phase 9 (permission handling)
            # manager.register_integration(CalendarIntegration())
            # manager.register_integration(RemindersIntegration())
            # manager.register_integration(FileSystemIntegration())
            
            app.state.integration_manager = manager
        return app.state.integration_manager
    
    def get_obsidian_smart():
        """Get Obsidian smart features, initializing if needed."""
        if app.state.obsidian_smart is None:
            manager = get_integration_manager()
            obsidian = manager.get_integration("obsidian")
            
            if obsidian:
                try:
                    from integrations.obsidian_smart import ObsidianSmartFeatures
                    from core.domains import DomainEngine
                except ImportError as e:
                    logger.error(f"Failed to import obsidian_smart or domains: {e}")
                    return None
                
                polly = get_polly()
                domain_engine = DomainEngine()
                
                app.state.obsidian_smart = ObsidianSmartFeatures(
                    obsidian_integration=obsidian,
                    domain_engine=domain_engine,
                    rag_engine=polly.rag
                )
                logger.info("Initialized Obsidian smart features")
            else:
                logger.warning("Cannot initialize smart features - Obsidian not available")
        
        return app.state.obsidian_smart
    
    @app.on_event("startup")
    def startup_event():
        """Initialize Polly in background thread to avoid blocking server."""
        import threading
        
        print("=== STARTUP EVENT CALLED ===", flush=True)
        logger.info("Startup event - starting background Polly initialization")
        
        # Track initialization state
        app.state.polly_initializing = True
        app.state.polly_init_error = None
        
        def initialize_polly_background():
            """Initialize Polly in background thread."""
            try:
                print("🚀 [Background] Starting Polly initialization...", flush=True)
                logger.info("Background: Initializing Polly")
                
                from core.polly import Polly
                polly_instance = Polly()
                
                # Atomically set the instance
                app.state.polly = polly_instance
                app.state.polly_initializing = False
                
                print("✅ [Background] Polly initialization complete!", flush=True)
                logger.info("Background: Polly initialized successfully")
                
                # Auto-rebuild notes index if empty
                try:
                    from core.notes_index import get_notes_index
                    from core.notes_source_manager import NotesSourceManager
                    
                    notes_idx = get_notes_index()
                    if len(notes_idx._notes_by_path) == 0:
                        print("[Background] Notes index is empty, rebuilding...", flush=True)
                        logger.info("Background: Auto-rebuilding notes index")
                        
                        manager = NotesSourceManager()
                        notes_path = manager.get_notes_path()
                        stats = notes_idx.build_index(notes_path, recursive=True)
                        
                        print(f"[Background] ✅ Notes index rebuilt: {stats['notes_indexed']} notes indexed", flush=True)
                        logger.info(f"Background: Notes index rebuilt with {stats['notes_indexed']} notes")
                except Exception as e:
                    print(f"[Background] ⚠️ Notes index rebuild failed: {e}", flush=True)
                    logger.error(f"Background: Notes index rebuild failed: {e}", exc_info=True)
                
            except Exception as e:
                print(f"❌ [Background] Polly initialization failed: {e}", flush=True)
                logger.error(f"Background: Polly initialization failed: {e}", exc_info=True)
                app.state.polly = None
                app.state.polly_initializing = False
                app.state.polly_init_error = str(e)
        
        # Start background thread (daemon=True means it won't prevent shutdown)
        init_thread = threading.Thread(target=initialize_polly_background, daemon=True, name="PollyInit")
        init_thread.start()
        
        print("=== STARTUP EVENT COMPLETED (Polly initializing in background) ===", flush=True)
        logger.info("Startup event complete - Polly initializing in background thread")
    
    @app.get("/")
    async def root():
        """Root endpoint - redirect to settings."""
        return {"message": "Polly API", "settings_ui": "/settings"}
    
    @app.get("/settings", response_class=HTMLResponse)
    async def settings_page():
        """Serve the settings UI page."""
        web_dir = Path(__file__).parent.parent / "web"
        settings_file = web_dir / "templates" / "settings.html"
        
        if not settings_file.exists():
            raise HTTPException(404, "Settings page not found")
        
        with open(settings_file) as f:
            return HTMLResponse(content=f.read())

    @app.get("/health")
    async def health_check():
        """Health check endpoint - lightweight, doesn't block on RAG initialization."""
        return {
            "status": "ok",
            "server": "running"
        }
    
    @app.get("/polly/status")
    async def polly_status():
        """Check if Polly core is initialized and ready."""
        polly = app.state.polly
        initializing = getattr(app.state, 'polly_initializing', False)
        error = getattr(app.state, 'polly_init_error', None)
        
        if polly is not None:
            return {
                "status": "ready",
                "initialized": True,
                "initializing": False
            }
        elif error is not None:
            return {
                "status": "error",
                "initialized": False,
                "initializing": False,
                "error": error
            }
        elif initializing:
            return {
                "status": "initializing",
                "initialized": False,
                "initializing": True
            }
        else:
            return {
                "status": "not_started",
                "initialized": False,
                "initializing": False
            }
    
    @app.get("/routing/settings")
    async def get_routing_settings():
        """Get hybrid routing threshold settings."""
        polly = get_polly()
        
        return {
            "enabled": polly.config.get("hybrid_routing.enabled", True),
            "thresholds": {
                "min_top_score": polly.config.get("hybrid_routing.thresholds.min_top_score", 0.75),
                "min_high_quality_results": polly.config.get("hybrid_routing.thresholds.min_high_quality_results", 2),
                "min_context_chars": polly.config.get("hybrid_routing.thresholds.min_context_chars", 500),
                "exceptional_score": polly.config.get("hybrid_routing.thresholds.exceptional_score", 0.85),
                "exceptional_min_results": polly.config.get("hybrid_routing.thresholds.exceptional_min_results", 3)
            }
        }
    
    @app.post("/routing/settings")
    async def update_routing_settings(settings: Dict[str, Any]):
        """Update hybrid routing threshold settings."""
        polly = get_polly()
        
        try:
            # Update config in memory
            if "enabled" in settings:
                polly.config._config["hybrid_routing"] = polly.config._config.get("hybrid_routing", {})
                polly.config._config["hybrid_routing"]["enabled"] = settings["enabled"]
            
            if "thresholds" in settings:
                if "hybrid_routing" not in polly.config._config:
                    polly.config._config["hybrid_routing"] = {}
                if "thresholds" not in polly.config._config["hybrid_routing"]:
                    polly.config._config["hybrid_routing"]["thresholds"] = {}
                
                thresholds = settings["thresholds"]
                config_thresholds = polly.config._config["hybrid_routing"]["thresholds"]
                
                if "min_top_score" in thresholds:
                    config_thresholds["min_top_score"] = float(thresholds["min_top_score"])
                if "min_high_quality_results" in thresholds:
                    config_thresholds["min_high_quality_results"] = int(thresholds["min_high_quality_results"])
                if "min_context_chars" in thresholds:
                    config_thresholds["min_context_chars"] = int(thresholds["min_context_chars"])
                if "exceptional_score" in thresholds:
                    config_thresholds["exceptional_score"] = float(thresholds["exceptional_score"])
                if "exceptional_min_results" in thresholds:
                    config_thresholds["exceptional_min_results"] = int(thresholds["exceptional_min_results"])
            
            # Save to disk
            polly.config.save()
            
            return {"success": True, "message": "Routing settings updated"}
        
        except Exception as e:
            logger.error(f"Failed to update routing settings: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to update settings: {str(e)}")
    
    @app.get("/deduplication/settings")
    async def get_dedup_settings():
        """Get knowledge base deduplication settings (Phase 21)."""
        polly = get_polly()
        
        return {
            "enabled": polly.config.get("deduplication.enabled", True),
            "similarity_threshold": polly.config.get("deduplication.similarity_threshold", 0.70),
            "max_results": polly.config.get("deduplication.max_results", 5)
        }
    
    @app.post("/deduplication/settings")
    async def update_dedup_settings(settings: Dict[str, Any]):
        """Update knowledge base deduplication settings (Phase 21)."""
        polly = get_polly()
        
        try:
            # Update config in memory
            if "deduplication" not in polly.config._config:
                polly.config._config["deduplication"] = {}
            
            config_dedup = polly.config._config["deduplication"]
            
            if "enabled" in settings:
                config_dedup["enabled"] = bool(settings["enabled"])
            if "similarity_threshold" in settings:
                # Convert percentage (70) to decimal (0.70)
                threshold = float(settings["similarity_threshold"])
                if threshold > 1:
                    threshold = threshold / 100
                config_dedup["similarity_threshold"] = threshold
            if "max_results" in settings:
                config_dedup["max_results"] = int(settings["max_results"])
            
            # Save to disk
            polly.config.save()
            
            # Reinitialize dedup engine with new config (if it exists)
            if polly.dedup_engine:
                polly.dedup_engine.config = polly.config
                logger.info(f"Dedup config updated: enabled={config_dedup.get('enabled')}, threshold={config_dedup.get('similarity_threshold')}, max={config_dedup.get('max_results')}")
            
            return {"success": True, "message": "Deduplication settings updated"}
        
        except Exception as e:
            logger.error(f"Failed to update dedup settings: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to update settings: {str(e)}")
    
    @app.get("/routing/stats")
    async def get_routing_stats():
        """Get routing statistics (local vs cloud usage)."""
        polly = get_polly()
        
        # Get stats from budget manager if available
        if hasattr(polly, 'budget_manager') and polly.budget_manager:
            try:
                from datetime import datetime, timedelta
                
                # Get today's usage
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                today_end = datetime.now()
                usage = await polly.budget_manager.get_usage_history(
                    limit=1000,
                    start_date=today_start,
                    end_date=today_end
                )
                
                # Calculate local vs cloud
                local_count = 0
                cloud_count = 0
                total_cost = 0.0
                
                for record in usage:
                    if record.provider == 'ollama':
                        local_count += 1
                    else:
                        cloud_count += 1
                        total_cost += record.cost
                
                # Estimate cost saved (assume avg cloud query = $0.01)
                avg_cloud_cost = 0.01
                cost_saved = local_count * avg_cloud_cost
                
                return {
                    "local_today": local_count,
                    "cloud_today": cloud_count,
                    "cost_saved_today": f"${cost_saved:.2f}",
                    "cloud_cost_today": f"${total_cost:.2f}"
                }
            except Exception as e:
                logger.error(f"Failed to get routing stats: {e}")
                return {
                    "local_today": 0,
                    "cloud_today": 0,
                    "cost_saved_today": "$0.00",
                    "cloud_cost_today": "$0.00"
                }
        else:
            return {
                "local_today": 0,
                "cloud_today": 0,
                "cost_saved_today": "$0.00",
                "cloud_cost_today": "$0.00"
            }
    
    @app.get("/debug/hybrid_search")
    async def debug_hybrid_search():
        """Debug endpoint to check hybrid search status."""
        polly = get_polly()
        
        debug_info = {
            "use_hybrid_search": polly.rag.use_hybrid_search,
            "has_hybrid_searcher": polly.rag.hybrid_searcher is not None,
            "n_results_config": polly.config.get("rag.n_results", 5)
        }
        
        if polly.rag.hybrid_searcher and hasattr(polly.rag.hybrid_searcher, 'bm25_index'):
            bm25_index = polly.rag.hybrid_searcher.bm25_index
            debug_info["bm25_corpus_size"] = len(bm25_index.corpus_docs) if bm25_index and bm25_index.corpus_docs else 0
        else:
            debug_info["bm25_corpus_size"] = 0
            
        return debug_info
    
    @app.get("/debug/rag_test")
    async def debug_rag_test():
        """Test RAG retrieval directly."""
        polly = get_polly()
        
        query = "Concerning my 'Practices and Exercises' framework. What is something I might do today to keep in practice?"
        
        # Get RAG results
        rag_results = polly.rag.search(query=query, n_results=15)
        
        result_list = []
        practices_count = 0
        for i, result in enumerate(rag_results[:10], 1):
            filepath = result.chunk.filepath
            is_practices = 'Practices' in filepath and 'Exercises' in filepath
            if is_practices:
                practices_count += 1
            result_list.append({
                "rank": i,
                "filepath": filepath,
                "is_practices": is_practices,
                "score": float(result.score),
                "preview": result.chunk.content[:100]
            })
        
        # Also get the formatted context
        rag_context = polly.rag.format_context(rag_results[:10], max_tokens=3000)
        
        return {
            "query": query,
            "total_results": len(rag_results),
            "practices_in_top_10": practices_count,
            "top_10_results": result_list,
            "formatted_context_length": len(rag_context),
            "formatted_context_preview": rag_context[:1500],
            "practice_count_in_context": rag_context.count('PRACTICE')
        }

    @app.post("/v1/chat/completions")
    async def chat_completions(request: ChatCompletionRequest):
        """
        OpenAI-compatible chat completions endpoint.

        This allows Polly to work with any tool that supports OpenAI API,
        including Cursor, Continue, and other IDEs.
        """
        polly = get_polly()

        # Convert messages
        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        # Get last user message for Polly query
        user_messages = [m for m in messages if m["role"] == "user"]
        if not user_messages:
            raise HTTPException(400, "No user message found")

        last_query = user_messages[-1]["content"]

        # Map mode/tier
        from core.router import RoutingMode, ModelTier

        mode_map = {
            'local': RoutingMode.LOCAL,
            'cloud': RoutingMode.CLOUD,
            'auto': RoutingMode.AUTO
        }
        tier_map = {
            'fast': ModelTier.FAST,
            'balanced': ModelTier.BALANCED,
            'quality': ModelTier.QUALITY
        }

        mode = mode_map.get(request.mode, RoutingMode.AUTO)
        tier = tier_map.get(request.tier, ModelTier.BALANCED)

        if request.stream:
            return StreamingResponse(
                stream_response(polly, last_query, mode, tier),
                media_type="text/event-stream"
            )
        else:
            # Collect full response
            response_text = ""
            async for chunk in polly.query(
                last_query,
                mode=mode,
                tier=tier,
                stream=False
            ):
                response_text += chunk

            return {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }

    async def stream_response(polly, query, mode, tier):
        """Stream SSE response."""
        async for chunk in polly.query(query, mode=mode, tier=tier, stream=True):
            data = {
                "id": f"chatcmpl-{int(time.time())}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "polly",
                "choices": [{
                    "index": 0,
                    "delta": {"content": chunk},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(data)}\n\n"

        # Final message
        yield "data: [DONE]\n\n"

    @app.post("/polly/query")
    async def polly_query(request: PollyQueryRequest):
        """
        Direct Polly query endpoint.

        Returns response with metadata about routing and sources.
        """
        logger.info(f"[QUERY DEBUG] Received query request: {request.query[:100]}...")
        logger.info(f"[QUERY DEBUG] Stream={request.stream}, Mode={request.mode}")
        
        try:
            polly = get_polly()
            logger.info("[QUERY DEBUG] Got Polly instance")

            from core.router import RoutingMode, ModelTier

            mode_map = {
                'local': RoutingMode.LOCAL,
                'cloud': RoutingMode.CLOUD,
                'auto': RoutingMode.AUTO
            }
            tier_map = {
                'fast': ModelTier.FAST,
                'balanced': ModelTier.BALANCED,
                'quality': ModelTier.QUALITY
            }

            mode = mode_map.get(request.mode, RoutingMode.AUTO)
            tier = tier_map.get(request.tier, ModelTier.BALANCED)
            
            logger.info(f"[QUERY DEBUG] Mapped mode={mode}, tier={tier}")
            
            # Set conversation history if provided
            if request.conversation_history is not None:
                polly.conversation_history = request.conversation_history
            
            if request.stream:
                logger.info("[QUERY DEBUG] Returning StreamingResponse")
                return StreamingResponse(
                    stream_polly_response(
                        polly, request.query, request.context, mode, tier,
                        request.confidence, request.provider_override,
                        request.page, request.persona, request.persona_mode,
                        request.mental_models_override
                    ),
                    media_type="text/event-stream"
                )
            else:
                response_text = ""
                async for chunk in polly.query(
                    request.query,
                    context=request.context,
                    mode=mode,
                    tier=tier,
                    stream=False,
                    confidence=request.confidence,
                    provider_override=request.provider_override,
                    page=request.page,
                    persona=request.persona,
                    persona_mode=request.persona_mode,
                    mental_models_override=request.mental_models_override
                ):
                    response_text += chunk

                # Get metadata from router v2 if available
                metadata = polly.get_last_response_metadata()
                
                response_data = {
                    "response": response_text,
                    "query": request.query,
                    "mode": request.mode,
                    "tier": request.tier
                }
                
                # Add router v2 metadata if present
                if metadata:
                    response_data["metadata"] = metadata
                
                return response_data
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            raise HTTPException(500, f"Query processing error: {str(e)}")

    async def stream_polly_response(polly, query, context, mode, tier, confidence=None, provider_override=None, page=None, persona=None, persona_mode=None, mental_models_override=None):
        """Stream Polly response."""
        logger.info(f"[STREAM DEBUG] Starting stream for query: {query[:50]}...")
        logger.info(f"[STREAM DEBUG] Mode={mode}, Tier={tier}, Context={context is not None}")
        
        try:
            logger.info("[STREAM DEBUG] About to call polly.query()")
            async for chunk in polly.query(
            query, 
            context=context, 
            mode=mode, 
            tier=tier, 
            stream=True,
            confidence=confidence,
            provider_override=provider_override,
            page=page,
            persona=persona,
            persona_mode=persona_mode,
                mental_models_override=mental_models_override
            ):
                logger.info(f"[STREAM DEBUG] Got chunk: {chunk[:100] if chunk else 'empty'}...")
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            logger.info("[STREAM DEBUG] Query iteration complete")
        except Exception as e:
            logger.error(f"[STREAM DEBUG] Error during streaming: {e}", exc_info=True)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return
        
        # Send metadata as final message if router_v2 was used
        metadata = polly.get_last_response_metadata()
        if metadata:
            logger.info("[STREAM DEBUG] Sending metadata")
            yield f"data: {json.dumps({'metadata': metadata})}\n\n"
        
        logger.info("[STREAM DEBUG] Sending [DONE]")
        yield "data: [DONE]\n\n"

    # Store indexing state
    app.state.indexing_status = {
        "in_progress": False,
        "last_run": None,
        "last_result": None,
        "last_error": None
    }

    @app.post("/polly/index")
    async def trigger_index(request: IndexRequest):
        """
        Trigger knowledge base indexing.
        
        Indexing runs in the background to avoid blocking the server.
        Returns immediately with status 'started'.
        """
        polly = get_polly()
        
        # Check if already indexing
        if app.state.indexing_status["in_progress"]:
            return {
                "status": "already_running",
                "message": "Indexing is already in progress",
                "started_at": app.state.indexing_status.get("started_at")
            }
        
        async def run_indexing():
            """Background task to run indexing."""
            app.state.indexing_status["in_progress"] = True
            app.state.indexing_status["started_at"] = datetime.now().isoformat()
            app.state.indexing_status["last_error"] = None
            
            try:
                logger.info("Starting background indexing task...")
                results = await polly.index(
                    obsidian=request.obsidian,
                    codebases=request.codebases,
                    force=request.force
                )
                logger.info(f"Background indexing complete: {results}")
                app.state.indexing_status["last_run"] = datetime.now().isoformat()
                app.state.indexing_status["last_result"] = results
            except Exception as e:
                logger.error(f"Background indexing failed: {e}", exc_info=True)
                app.state.indexing_status["last_error"] = str(e)
            finally:
                app.state.indexing_status["in_progress"] = False
        
        # Start indexing in background
        asyncio.create_task(run_indexing())
        
        return {
            "status": "started",
            "message": "Indexing started in background. Check /polly/index/status for progress.",
            "requested": {
                "obsidian": request.obsidian,
                "codebases": request.codebases,
                "force": request.force
            }
        }
    
    @app.get("/polly/index/status")
    async def get_index_status():
        """Get current indexing status."""
        return app.state.indexing_status

    @app.get("/polly/stats")
    async def get_stats():
        """
        Get Polly statistics without blocking.
        
        Returns basic stats. For detailed stats, Polly must be initialized.
        """
        # Check if Polly is ready
        polly = app.state.polly
        initializing = getattr(app.state, 'polly_initializing', False)
        error = getattr(app.state, 'polly_init_error', None)
        
        from core.config import get_config
        config = get_config()
        
        # NOTE: We return placeholder data even if Polly is initialized because
        # polly.get_stats() calls self.rag.get_stats() which does blocking ChromaDB operations.
        # Even with asyncio.to_thread(), this still blocks the server (likely due to DB locks).
        # TODO: Make RAG stats truly async by running ChromaDB in a separate process or
        # using an async ChromaDB client.
        
        # Get graph stats if entity_store is available
        graph_stats = {'entities': '?', 'relationships': '?'}
        if polly and polly.entity_store:
            try:
                stats = polly.entity_store.get_stats()
                graph_stats = {
                    'entities': stats.get('entities', '?'),
                    'relationships': stats.get('relationships', '?')
                }
            except Exception as e:
                logger.warning(f"Failed to get entity store stats: {e}")
        
        return {
            'status': 'ready' if polly else ('error' if error else ('initializing' if initializing else 'not_started')),
            'user': config.user_name,
            'polly_initialized': polly is not None,
            'rag': {
                'notes': {'count': '?', 'files': '?'},
                'codebase': {'count': '?', 'files': '?'}
            },
            'patterns': '?',
            'graph': graph_stats
        }
    
    @app.get("/polly/patterns")
    async def get_patterns():
        """
        Get all learned patterns with details.
        
        Returns:
        {
            "patterns": [...],
            "query_patterns": [...],
            "total_count": 10
        }
        """
        polly = get_polly()
        
        if not polly.pattern_engine:
            raise HTTPException(503, "Pattern engine not initialized")
        
        try:
            # Get all patterns from unified engine
            all_patterns = polly.pattern_engine.patterns
            patterns = [p.to_dict() for p in all_patterns.values()]
            
            return {
                'patterns': patterns,
                'query_patterns': [],  # Deprecated — query patterns are now unified
                'total_count': len(patterns),
                'stats': polly.pattern_engine.get_stats(),
            }
        except Exception as e:
            logger.error(f"Error fetching patterns: {e}")
            raise HTTPException(500, f"Failed to fetch patterns: {str(e)}")
    
    @app.post("/polly/patterns/reset")
    async def reset_patterns():
        """
        Reset all learned patterns.
        
        Clears patterns, query_patterns, query_history, code_snippets, etc.
        Creates a backup before resetting.
        """
        polly = get_polly()
        
        if not polly.pattern_engine:
            raise HTTPException(503, "Pattern engine not initialized")
        
        try:
            # Create backup via json_backend
            import shutil
            from datetime import datetime
            json_path = polly.pattern_engine.json_backend.json_path
            backup_path = json_path.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            if json_path.exists():
                shutil.copy(json_path, backup_path)
                logger.info(f"Created backup at {backup_path}")
            
            # Clear all patterns by deleting every pattern
            all_ids = list(polly.pattern_engine.patterns.keys())
            for pid in all_ids:
                polly.pattern_engine.json_backend.delete(pid)
            
            # Save empty state
            polly.pattern_engine.save()
            
            return {
                "status": "success",
                "message": "All patterns reset",
                "backup_path": str(backup_path) if backup_path.exists() else None
            }
        except Exception as e:
            logger.error(f"Error resetting patterns: {e}")
            raise HTTPException(500, f"Failed to reset patterns: {str(e)}")
    
    # ==================== Learning Tracker Endpoints (Phase 22) ====================
    
    @app.get("/polly/learning/stats")
    async def get_learning_stats():
        """
        Get overall learning statistics.
        
        Returns:
        {
            "total_topics": 10,
            "by_domain": {"sigils": 5, "scrolls": 3, "grids": 2},
            "by_mastery": {1: 2, 2: 3, 3: 3, 4: 1, 5: 1},
            "topics_needing_review": 3
        }
        """
        polly = get_polly()
        
        if not polly.learning_tracker:
            raise HTTPException(503, "Learning tracker not initialized")
        
        try:
            stats = polly.learning_tracker.get_learning_stats()
            return stats
        except Exception as e:
            logger.error(f"Error fetching learning stats: {e}")
            raise HTTPException(500, f"Failed to fetch learning stats: {str(e)}")
    
    @app.get("/polly/learning/topics")
    async def get_learning_topics():
        """
        Get all learning topics.
        
        Returns:
        {
            "topics": [
                {
                    "id": "async_await_in_python",
                    "title": "Async/Await in Python",
                    "domain": "sigils",
                    "concepts": ["coroutines", "event loop"],
                    "mastery_level": 3,
                    "first_learned": "2024-02-02T10:00:00",
                    "last_reviewed": "2024-02-02T10:00:00",
                    "notes_created": ["Learning - Async Python.md"],
                    "related_topics": []
                }
            ],
            "total_count": 10
        }
        """
        polly = get_polly()
        
        if not polly.learning_tracker:
            raise HTTPException(503, "Learning tracker not initialized")
        
        try:
            topics = []
            for topic in polly.learning_tracker.topics.values():
                topics.append({
                    'id': topic.id,
                    'title': topic.title,
                    'domain': topic.domain,
                    'concepts': topic.concepts,
                    'mastery_level': topic.mastery_level,
                    'first_learned': topic.first_learned.isoformat(),
                    'last_reviewed': topic.last_reviewed.isoformat(),
                    'notes_created': topic.notes_created,
                    'related_topics': topic.related_topics
                })
            
            return {
                'topics': topics,
                'total_count': len(topics)
            }
        except Exception as e:
            logger.error(f"Error fetching learning topics: {e}")
            raise HTTPException(500, f"Failed to fetch learning topics: {str(e)}")
    
    @app.get("/polly/learning/review")
    async def get_topics_for_review():
        """
        Get topics that need review based on spaced repetition.
        
        Query parameters:
            days: Number of days since last review (default: 7)
        
        Returns:
        {
            "topics": [
                {
                    "id": "async_await_in_python",
                    "title": "Async/Await in Python",
                    "domain": "sigils",
                    "mastery_level": 2,
                    "days_since_review": 4,
                    "recommended_interval": 3
                }
            ],
            "total_count": 5
        }
        """
        polly = get_polly()
        
        if not polly.learning_tracker:
            raise HTTPException(503, "Learning tracker not initialized")
        
        try:
            from datetime import datetime
            
            topics_for_review = polly.learning_tracker.get_topics_for_review()
            
            topics = []
            for topic in topics_for_review:
                days_since = (datetime.now() - topic.last_reviewed).days
                
                # Calculate recommended interval based on mastery
                interval_map = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
                recommended_interval = interval_map.get(topic.mastery_level, 7)
                
                topics.append({
                    'id': topic.id,
                    'title': topic.title,
                    'domain': topic.domain,
                    'mastery_level': topic.mastery_level,
                    'days_since_review': days_since,
                    'recommended_interval': recommended_interval,
                    'last_reviewed': topic.last_reviewed.isoformat()
                })
            
            return {
                'topics': topics,
                'total_count': len(topics)
            }
        except Exception as e:
            logger.error(f"Error fetching topics for review: {e}")
            raise HTTPException(500, f"Failed to fetch topics for review: {str(e)}")
    
    @app.post("/polly/learning/create-note")
    async def create_learning_note(request: Dict[str, Any]):
        """
        Create a structured learning note.
        
        Request body:
        {
            "topic": "Async/Await in Python",
            "content": "Detailed explanation...",
            "concepts": ["coroutines", "event loop", "non-blocking I/O"],
            "domain": "sigils",
            "conversation_id": "optional_conv_id"
        }
        
        Returns:
        {
            "status": "success",
            "note_path": "Learning - Async/Await in Python.md",
            "mastery_level": 1
        }
        """
        polly = get_polly()
        
        if not polly.learning_tracker:
            raise HTTPException(503, "Learning tracker not initialized")
        
        try:
            topic = request.get('topic')
            content = request.get('content')
            concepts = request.get('concepts', [])
            domain = request.get('domain', 'general')
            conversation_id = request.get('conversation_id')
            
            if not topic or not content:
                raise HTTPException(400, "Missing required fields: topic, content")
            
            # Create learning note via Polly
            result = await polly.create_learning_note(
                topic=topic,
                content=content,
                concepts=concepts,
                domain=domain,
                conversation_id=conversation_id
            )
            
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating learning note: {e}")
            raise HTTPException(500, f"Failed to create learning note: {str(e)}")

    @app.post("/polly/learning/exercise-result")
    async def record_exercise_result(request: Request):
        """
        Record exercise completion and update mastery.
        
        Request body:
        {
            "exercise_id": "fibonacci_1",
            "success": true,
            "time_spent": 300,
            "hints_used": 1
        }
        
        Returns:
        {
            "status": "success",
            "topic": "Fibonacci",
            "old_mastery": 1,
            "new_mastery": 2
        }
        """
        polly = get_polly()
        
        if not polly.learning_tracker:
            raise HTTPException(503, "Learning tracker not initialized")
        
        try:
            body = await request.json()
            exercise_id = body.get("exercise_id")
            success = body.get("success", False)
            time_spent = body.get("time_spent", 0)
            hints_used = body.get("hints_used", 0)
            
            if not exercise_id:
                raise HTTPException(400, "Missing required field: exercise_id")
            
            # Extract topic from exercise ID (e.g., "fibonacci_1" -> "Fibonacci")
            topic = exercise_id.rsplit("_", 1)[0].replace("_", " ").title()
            
            # Get current mastery
            current_mastery = polly.learning_tracker.get_topic_mastery(topic)
            
            # Calculate mastery increase (success with fewer hints = more increase)
            if success:
                if hints_used == 0:
                    mastery_increase = 1.0
                elif hints_used == 1:
                    mastery_increase = 0.7
                elif hints_used == 2:
                    mastery_increase = 0.5
                else:
                    mastery_increase = 0.3
            else:
                mastery_increase = 0.1  # Small increase for attempt
            
            # Update mastery (max 5)
            new_mastery = min(current_mastery + mastery_increase, 5.0)
            
            # Record learning
            polly.learning_tracker.record_learning(
                title=topic,
                domain="glyphs",
                concepts=[topic.lower()],
                mastery_level=int(new_mastery)
            )
            
            logger.info(f"Exercise result recorded: {exercise_id} - success={success}, mastery {current_mastery} -> {new_mastery}")
            
            return {
                "status": "success",
                "topic": topic,
                "old_mastery": current_mastery,
                "new_mastery": new_mastery,
                "mastery_increase": mastery_increase
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error recording exercise result: {e}")
            raise HTTPException(500, f"Failed to record exercise result: {str(e)}")

    @app.get("/v1/models")
    async def list_models():
        """List available models (OpenAI compatibility)."""
        return {
            "object": "list",
            "data": [
                {"id": "polly", "object": "model", "owned_by": "local"},
                {"id": "polly-local", "object": "model", "owned_by": "local"},
                {"id": "polly-cloud", "object": "model", "owned_by": "local"},
            ]
        }

    @app.post("/polly/save")
    async def save_state():
        """Save Polly state (patterns, graph)."""
        polly = get_polly()
        polly.save_state()
        return {"status": "saved"}

    @app.post("/polly/clear")
    async def clear_conversation():
        """Clear conversation history."""
        polly = get_polly()
        polly.clear_conversation()
        return {"status": "cleared"}
    
    @app.post("/polly/patterns/learn-from-conversation")
    async def learn_from_conversation(request: LearnFromConversationRequest):
        """
        Learn patterns from a conversation.
        
        Request body:
        {
            "conversation_id": "conv_123",
            "messages": [
                {"role": "user", "content": "..."},
                {"role": "assistant", "content": "..."}
            ],
            "category": "optional_category"
        }
        """
        polly = get_polly()
        
        if not polly.pattern_engine:
            raise HTTPException(503, "Pattern engine not initialized")
        
        try:
            # Convert messages to dict format
            messages_dict = [{"role": m.role, "content": m.content} for m in request.messages]
            
            # Learn from conversation messages by extracting query patterns
            patterns_learned = 0
            for msg in messages_dict:
                if msg.get("role") == "user":
                    domain_list = [request.category] if request.category else []
                    result = polly.pattern_engine.learn_from_query(
                        query=msg["content"],
                        domains=domain_list,
                    )
                    patterns_learned += len(result)
            
            # Save to disk
            polly.pattern_engine.save()
            
            return {
                "status": "success",
                "patterns_learned": patterns_learned,
                "conversation_id": request.conversation_id
            }
        except Exception as e:
            logger.error(f"Error learning from conversation: {e}")
            raise HTTPException(500, f"Failed to learn from conversation: {str(e)}")
    
    # ============================================
    # Mental Models Endpoints (Phase 14)
    # ============================================
    
    @app.get("/polly/mental-models/list")
    async def list_mental_models(enabled_only: bool = False):
        """
        List all mental models.
        
        Query params:
        - enabled_only: If true, only return enabled models
        
        Returns:
            {
                "models": [
                    {
                        "id": "infinite_games",
                        "name": "Infinite Games",
                        "description": "...",
                        "enabled": true,
                        ...
                    }
                ],
                "count": 12
            }
        """
        polly = get_polly()
        if not polly:
            raise HTTPException(503, "Polly not initialized")
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        try:
            models = polly.mental_model_manager.list_models(enabled_only=enabled_only)
            
            return {
                "models": [model.to_dict() for model in models],
                "count": len(models)
            }
        except Exception as e:
            logger.error(f"Error listing mental models: {e}")
            raise HTTPException(500, f"Failed to list mental models: {str(e)}")
    
    @app.get("/polly/mental-models/{model_id}")
    async def get_mental_model(model_id: str):
        """
        Get a specific mental model by ID.
        
        Returns:
            {
                "id": "infinite_games",
                "name": "Infinite Games",
                "description": "...",
                ...
            }
        """
        polly = get_polly()
        
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        model = polly.mental_model_manager.get_model(model_id)
        
        if not model:
            raise HTTPException(404, f"Mental model '{model_id}' not found")
        
        return model.to_dict()
    
    @app.post("/polly/mental-models/create")
    async def create_mental_model(request: Dict[str, Any]):
        """
        Create a new mental model.
        
        Request body:
        {
            "id": "custom_model",
            "name": "Custom Model",
            "description": "...",
            "principles": ["principle 1", "principle 2"],
            "prompt_injection": "...",
            "applies_to": ["scrolls"],
            "active_on_pages": ["learning"],
            "active_for_personas": [],
            "active_for_modes": [],
            "keywords": ["custom"],
            "enabled": true
        }
        
        Returns:
            {"status": "created", "id": "custom_model"}
        """
        polly = get_polly()
        
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        try:
            from core.mental_models import MentalModel
            
            # Create model from request data
            model = MentalModel(
                id=request.get('id'),
                name=request.get('name'),
                description=request.get('description'),
                principles=request.get('principles', []),
                prompt_injection=request.get('prompt_injection'),
                applies_to=request.get('applies_to', []),
                active_on_pages=request.get('active_on_pages', []),
                active_for_personas=request.get('active_for_personas', []),
                active_for_modes=request.get('active_for_modes', []),
                keywords=request.get('keywords', []),
                category_triggers=request.get('category_triggers', []),
                enabled=request.get('enabled', True)
            )
            
            # Add to manager
            polly.mental_model_manager.add_model(model)
            
            # Save to disk
            polly.mental_model_manager.save_models()
            
            return {"status": "created", "id": model.id}
        
        except ValueError as e:
            raise HTTPException(400, str(e))
        except Exception as e:
            logger.error(f"Error creating mental model: {e}")
            raise HTTPException(500, f"Failed to create mental model: {str(e)}")
    
    @app.put("/polly/mental-models/{model_id}")
    async def update_mental_model(model_id: str, request: Dict[str, Any]):
        """
        Update an existing mental model.
        
        Request body contains fields to update:
        {
            "name": "Updated Name",
            "description": "Updated description",
            "enabled": false,
            ...
        }
        
        Returns:
            {"status": "updated", "id": "model_id"}
        """
        polly = get_polly()
        
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        try:
            # Update model
            polly.mental_model_manager.update_model(model_id, request)
            
            # Save to disk
            polly.mental_model_manager.save_models()
            
            return {"status": "updated", "id": model_id}
        
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error updating mental model: {e}")
            raise HTTPException(500, f"Failed to update mental model: {str(e)}")
    
    @app.delete("/polly/mental-models/{model_id}")
    async def delete_mental_model(model_id: str):
        """
        Delete a mental model.
        
        Returns:
            {"status": "deleted", "id": "model_id"}
        """
        polly = get_polly()
        
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        try:
            # Delete model
            polly.mental_model_manager.delete_model(model_id)
            
            # Save to disk
            polly.mental_model_manager.save_models()
            
            return {"status": "deleted", "id": model_id}
        
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error deleting mental model: {e}")
            raise HTTPException(500, f"Failed to delete mental model: {str(e)}")
    
    @app.post("/polly/mental-models/{model_id}/toggle")
    async def toggle_mental_model(model_id: str):
        """
        Toggle a mental model's enabled state.
        
        Returns:
            {"status": "toggled", "id": "model_id", "enabled": true}
        """
        polly = get_polly()
        
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        try:
            # Toggle model
            new_state = polly.mental_model_manager.toggle_model(model_id)
            
            # Save to disk
            polly.mental_model_manager.save_models()
            
            return {"status": "toggled", "id": model_id, "enabled": new_state}
        
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error toggling mental model: {e}")
            raise HTTPException(500, f"Failed to toggle mental model: {str(e)}")
    
    @app.get("/polly/mental-models/active")
    async def get_active_mental_models(
        domain: Optional[str] = None,
        page: Optional[str] = None,
        persona: Optional[str] = None,
        persona_mode: Optional[str] = None,
        keywords: Optional[str] = None
    ):
        """
        Get currently active mental models for a given context.
        
        Query params:
        - domain: Domain (e.g., "scrolls", "sigils")
        - page: Current page (e.g., "learning", "code")
        - persona: Active persona (e.g., "architect", "teacher")
        - persona_mode: Active mode (e.g., "plan", "socratic")
        - keywords: Comma-separated keywords
        
        Returns:
            {
                "models": [list of active models],
                "count": 3,
                "context": {domain, page, persona, persona_mode, keywords}
            }
        """
        polly = get_polly()
        
        if not polly.mental_model_manager:
            raise HTTPException(503, "Mental model manager not initialized")
        
        try:
            # Parse keywords
            keyword_list = None
            if keywords:
                keyword_list = [k.strip() for k in keywords.split(',')]
            
            # Get active models
            models = polly.mental_model_manager.get_models_for_context(
                domain=domain,
                page=page,
                persona=persona,
                persona_mode=persona_mode,
                keywords=keyword_list,
                enabled_only=True
            )
            
            return {
                "models": [model.to_dict() for model in models],
                "count": len(models),
                "context": {
                    "domain": domain,
                    "page": page,
                    "persona": persona,
                    "persona_mode": persona_mode,
                    "keywords": keyword_list
                }
            }
        except Exception as e:
            logger.error(f"Error getting active mental models: {e}")
            raise HTTPException(500, f"Failed to get active mental models: {str(e)}")
    
    # ============================================
    # Persona Endpoints (Phase 11c)
    # ============================================
    
    @app.post("/persona/activate")
    async def activate_persona(request: Request):
        """
        Activate a persona.
        
        Request body:
        {
            "persona_name": "architect"
        }
        
        Returns:
            {
                "success": true,
                "state": {
                    "current_mode": "plan",
                    "persona_name": "architect",
                    ...
                }
            }
        """
        polly = get_polly()
        
        if not polly.using_router_v2:
            raise HTTPException(503, "Persona system requires Router v2 (set routing_v2.enabled=true in config)")
        
        if not polly.persona_manager:
            raise HTTPException(503, "Persona system not initialized")
        
        # Parse request body manually
        try:
            body = await request.json()
            logger.info(f"[Persona Activate] Request body: {body}")
        except Exception as e:
            logger.error(f"[Persona Activate] Failed to parse JSON: {e}")
            raise HTTPException(400, "Invalid JSON in request body")
        
        persona_name = body.get("persona_name")
        if not persona_name:
            logger.error(f"[Persona Activate] persona_name missing from body: {body}")
            raise HTTPException(400, "persona_name is required")
        
        logger.info(f"[Persona Activate] Activating persona: {persona_name}")
        
        try:
            state = await polly.activate_persona(persona_name)
            
            if not state:
                raise HTTPException(404, f"Persona '{persona_name}' not found")
            
            return {
                "success": True,
                "state": state
            }
        except ValueError as e:
            logger.error(f"Failed to activate persona (ValueError): {e}", exc_info=True)
            raise HTTPException(400, f"Invalid persona: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to activate persona: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to activate persona: {str(e)}")
    
    @app.post("/persona/process")
    async def process_with_persona(request: Dict[str, Any]):
        """
        Process user input with active persona.
        
        Request body:
        {
            "user_message": "Create a note about Docker",
            "persona_name": "professor",   // optional; if provided, activate this persona before processing (keeps UI and server in sync)
            "persona_mode": "curriculum",  // optional; mode to activate (e.g. from /learning-path slash command)
            "metadata": {
                "page": "scrolls",
                "domain": "scrolls"
            }
        }
        
        Returns:
            {
                "success": true,
                "response": {
                    "content": "...",
                    "mode": "plan",
                    "actions": [...],
                    "metadata": {...}
                }
            }
        """
        polly = get_polly()
        
        if not polly.using_router_v2:
            raise HTTPException(503, "Persona system requires Router v2")
        
        if not polly.persona_manager:
            raise HTTPException(503, "Persona system not initialized")
        
        user_message = request.get("user_message")
        if not user_message:
            raise HTTPException(400, "user_message is required")
        
        metadata = request.get("metadata", {})
        persona_name = request.get("persona_name")
        persona_mode = request.get("persona_mode")
        
        try:
            # If frontend sends persona_name, ensure that persona is active (handles refresh / programmatic select)
            if persona_name:
                try:
                    await polly.activate_persona(persona_name, mode=persona_mode)
                except (ValueError, RuntimeError) as e:
                    logger.warning(f"Could not activate persona {persona_name}: {e}")
                    raise HTTPException(400, f"Invalid or unavailable persona: {persona_name}")
            elif not polly.persona_manager or not polly.persona_manager.is_persona_active():
                raise HTTPException(400, "No persona active. Select a persona or include persona_name in the request.")
            
            response = await polly.process_with_persona(user_message, metadata)
            
            if not response:
                raise HTTPException(400, "No active persona")
            
            return {
                "success": True,
                "response": response
            }
        except Exception as e:
            logger.error(f"Failed to process with persona: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to process with persona: {str(e)}")
    
    @app.post("/persona/switch-mode")
    async def switch_persona_mode(request: Request):
        """
        Switch the active persona's mode.
        
        Request body:
        {
            "mode": "build"
        }
        
        Returns:
            {
                "success": true,
                "state": {
                    "current_mode": "build",
                    ...
                }
            }
        """
        polly = get_polly()
        
        if not polly.using_router_v2:
            raise HTTPException(503, "Persona system requires Router v2")
        
        if not polly.persona_manager:
            raise HTTPException(503, "Persona system not initialized")
        
        # Parse request body manually
        try:
            body = await request.json()
            logger.info(f"[Persona Switch Mode] Request body: {body}")
        except Exception as e:
            logger.error(f"[Persona Switch Mode] Failed to parse JSON: {e}")
            raise HTTPException(400, "Invalid JSON in request body")
        
        mode = body.get("mode")
        if not mode:
            logger.error(f"[Persona Switch Mode] mode missing from body: {body}")
            raise HTTPException(400, "mode is required")
        
        logger.info(f"[Persona Switch Mode] Switching to mode: {mode}")
        
        try:
            state = polly.switch_persona_mode(mode)
            
            if not state:
                raise HTTPException(400, "No active persona or invalid mode")
            
            return {
                "success": True,
                "state": state
            }
        except Exception as e:
            logger.error(f"Failed to switch persona mode: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to switch mode: {str(e)}")
    
    @app.get("/persona/state")
    async def get_persona_state():
        """
        Get current persona state.

        Returns:
            {
                "active": true,
                "state": {
                    "current_mode": "plan",
                    "persona_name": "architect",
                    ...
                }
            }
        """
        polly = get_polly()
        if not polly:
            raise HTTPException(503, "Polly not initialized")
        if not polly.using_router_v2:
            raise HTTPException(503, "Persona system requires Router v2")
        
        if not polly.persona_manager:
            raise HTTPException(503, "Persona system not initialized")
        
        try:
            state = polly.get_persona_state()
            
            return {
                "active": state is not None,
                "state": state
            }
        except Exception as e:
            logger.error(f"Failed to get persona state: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get persona state: {str(e)}")
    
    @app.get("/persona/list")
    async def list_personas():
        """
        List all available personas.
        
        Returns:
            {
                "personas": [
                    {
                        "name": "architect",
                        "description": "...",
                        "modes": ["plan", "build"]
                    }
                ]
            }
        """
        polly = get_polly()
        
        if not polly.using_router_v2:
            raise HTTPException(503, "Persona system requires Router v2")
        
        if not polly.persona_manager:
            raise HTTPException(503, "Persona system not initialized")
        
        try:
            personas = polly.list_available_personas()
            
            return {
                "personas": personas
            }
        except Exception as e:
            logger.error(f"Failed to list personas: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to list personas: {str(e)}")
    
    @app.get("/persona/commands")
    async def list_persona_commands():
        """
        List slash commands for persona/mode invocation (autocomplete).
        
        Returns:
            {
                "commands": [
                    {"command": "learning-path", "persona": "professor", "mode": "curriculum", "description": "..."},
                    ...
                ]
            }
        """
        try:
            from core.personas.commands import list_commands
            commands = list_commands()
            return {"commands": commands}
        except Exception as e:
            logger.error(f"Failed to list persona commands: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to list persona commands: {str(e)}")
    
    @app.post("/persona/deactivate")
    async def deactivate_persona():
        """
        Deactivate the current persona.
        
        Returns:
            {"success": true}
        """
        polly = get_polly()
        
        if not polly.using_router_v2:
            raise HTTPException(503, "Persona system requires Router v2")
        
        if not polly.persona_manager:
            raise HTTPException(503, "Persona system not initialized")
        
        try:
            polly.deactivate_persona()
            
            return {"success": True}
        except Exception as e:
            logger.error(f"Failed to deactivate persona: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to deactivate persona: {str(e)}")
    
    # ============================================
    # Integration Endpoints
    # ============================================
    
    @app.get("/polly/integrations")
    async def list_integrations():
        """List all available integrations and their statuses."""
        manager = get_integration_manager()
        return {
            "integrations": manager.get_all_statuses(),
            "connected": manager.get_connected_integrations()
        }
    
    @app.post("/polly/integrations/connect")
    async def connect_integration(request: IntegrationConnectRequest):
        """
        Connect to an integration.
        
        Request body:
        {
            "integration": "github",
            "credentials": {"token": "..."}
        }
        """
        manager = get_integration_manager()
        
        try:
            # Special handling for Obsidian - re-register if vault path changed
            if request.integration == "obsidian":
                # Reload config to get latest vault_path from file
                from core.config import load_config
                load_config()
                
                polly = get_polly()
                vault_path = polly.config.get("obsidian.vault_path")
                
                if not vault_path:
                    raise HTTPException(400, "Obsidian vault path not configured")
                
                logger.info(f"Connecting Obsidian with vault path: {vault_path}")
                
                # Check if integration exists and has different path
                existing = manager.get_integration("obsidian")
                if existing:
                    if str(existing.vault_path) != str(vault_path):
                        logger.info(f"Vault path changed from {existing.vault_path} to {vault_path}, re-registering")
                        # Disconnect old integration
                        await existing.disconnect()
                        # Register new integration with updated path
                        manager.integrations["obsidian"] = ObsidianIntegration(vault_path=vault_path)
                else:
                    # Register for first time
                    logger.info(f"Registering Obsidian integration for first time")
                    manager.register_integration(ObsidianIntegration(vault_path=vault_path))
            
            success = await manager.connect_integration(
                request.integration,
                request.credentials
            )
            
            integration = manager.get_integration(request.integration)
            return {
                "success": success,
                "status": integration.get_status() if integration else None
            }
        except Exception as e:
            logger.error(f"Integration connect failed: {e}")
            raise HTTPException(500, f"Connection failed: {str(e)}")
    
    @app.post("/polly/integrations/{integration_name}/disconnect")
    async def disconnect_integration(integration_name: str):
        """Disconnect from an integration."""
        manager = get_integration_manager()
        
        try:
            success = await manager.disconnect_integration(integration_name)
            return {"success": success}
        except Exception as e:
            logger.error(f"Integration disconnect failed: {e}")
            raise HTTPException(500, f"Disconnect failed: {str(e)}")
    
    @app.post("/polly/integrations/sync")
    async def sync_integration(request: IntegrationSyncRequest):
        """
        Sync data from an integration and index it.
        
        Request body:
        {
            "integration": "github",
            "options": {"include_repos": true, "include_issues": false}
        }
        """
        manager = get_integration_manager()
        polly = get_polly()
        
        try:
            # Sync data from integration
            sync_result = await manager.sync_integration(
                request.integration,
                **(request.options or {})
            )
            
            # Index documents into RAG
            documents = sync_result["documents"]
            indexed_count = 0
            skipped_count = 0
            
            # Use the 'documents' collection so it's included in normal searches
            collection = polly.rag.collections['documents']
            
            import hashlib
            from datetime import datetime
            
            for doc in documents:
                # Generate unique ID for this document
                doc_id = hashlib.md5(
                    f"{doc['metadata'].get('id', '')}:{doc['content'][:100]}".encode()
                ).hexdigest()
                
                try:
                    # Check for empty documents
                    if not doc["content"] or len(doc["content"].strip()) == 0:
                        skipped_count += 1
                        # Log which file is empty for debugging
                        logger.warning(f"Empty document: {doc['metadata'].get('filepath', 'unknown')} (length: {len(doc.get('content', ''))})")
                        continue
                    
                    # Generate embedding
                    embedding = polly.rag.embed_text(doc["content"])
                    
                    # Validate embedding
                    if not embedding or len(embedding) == 0:
                        logger.warning(f"Empty embedding for: {doc['metadata'].get('filepath', 'unknown')}")
                        skipped_count += 1
                        continue
                    
                    # Ensure embedding is a list
                    if not isinstance(embedding, list):
                        embedding = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
                    
                    # Upsert into collection
                    collection.upsert(
                        ids=[doc_id],
                        embeddings=[embedding],
                        documents=[doc["content"]],
                        metadatas=[{
                            **doc["metadata"],
                            'indexed_at': datetime.now().isoformat()
                        }]
                    )
                    indexed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error indexing {doc['metadata'].get('filepath', 'unknown')}: {e}")
                    skipped_count += 1
                    # Continue with next document
            
            if skipped_count > 0:
                logger.info(f"Skipped {skipped_count} empty or invalid documents")
            
            # Save indexed count to state for persistence across restarts
            if request.integration == "obsidian":
                from integrations.state import get_state_manager
                state_manager = get_state_manager()
                state_manager.save_metadata("obsidian", {"indexed_count": indexed_count})
            
            return {
                "success": True,
                "integration": request.integration,
                "fetched": sync_result["count"],
                "indexed": indexed_count,
                "skipped": skipped_count,
                "metadata": sync_result["metadata"]
            }
            
        except Exception as e:
            logger.error(f"Integration sync failed: {e}")
            raise HTTPException(500, f"Sync failed: {str(e)}")
    
    @app.get("/polly/integrations/{integration_name}/search")
    async def search_integration(integration_name: str, q: str, limit: int = 10):
        """
        Search directly in an integration's collection.
        Bypasses Polly's domain detection for debugging.
        """
        polly = get_polly()
        
        try:
            collection_name = f"integration_{integration_name}"
            collection = polly.rag.client.get_collection(collection_name)
            
            # Generate query embedding
            query_embedding = polly.rag.embed_text(q)
            
            # Search collection
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=limit
            )
            
            return {
                "success": True,
                "query": q,
                "results": {
                    "documents": results.get("documents", [[]])[0],
                    "metadatas": results.get("metadatas", [[]])[0],
                    "distances": results.get("distances", [[]])[0]
                }
            }
            
        except Exception as e:
            logger.error(f"Integration search failed: {e}")
            raise HTTPException(500, f"Search failed: {str(e)}")
    
    # ============================================================
    # FILE SYSTEM OPERATIONS
    # ============================================================
    
    @app.post("/polly/filesystem/create-folder")
    async def create_folder(request: Dict[str, Any]):
        """
        Create a folder.
        
        Request: {"path": "/path/to/folder", "parents": true}
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            result = fs.create_folder(
                request.get("path"),
                parents=request.get("parents", True)
            )
            return result
        except Exception as e:
            logger.error(f"Create folder failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/filesystem/move")
    async def move_file(request: Dict[str, Any]):
        """
        Move a file or folder.
        
        Request: {"source": "/path/to/source", "destination": "/path/to/dest", "overwrite": false}
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            result = fs.move_file(
                request.get("source"),
                request.get("destination"),
                overwrite=request.get("overwrite", False)
            )
            return result
        except Exception as e:
            logger.error(f"Move file failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/filesystem/rename")
    async def rename_file(request: Dict[str, Any]):
        """
        Rename a file or folder.
        
        Request: {"path": "/path/to/file", "new_name": "newname.txt"}
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            result = fs.rename_file(
                request.get("path"),
                request.get("new_name")
            )
            return result
        except Exception as e:
            logger.error(f"Rename file failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/filesystem/add-tags")
    async def add_tags(request: Dict[str, Any]):
        """
        Add macOS Finder tags to a file or folder.
        
        Request: {"path": "/path/to/file", "tags": ["work", "blue"]}
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            result = fs.add_tags(
                request.get("path"),
                request.get("tags", [])
            )
            return result
        except Exception as e:
            logger.error(f"Add tags failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.get("/polly/filesystem/get-tags")
    async def get_tags(path: str):
        """
        Get macOS Finder tags from a file or folder.
        
        Query param: path=/path/to/file
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            result = fs.get_tags(path)
            return result
        except Exception as e:
            logger.error(f"Get tags failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.get("/polly/filesystem/find-by-tags")
    async def find_by_tags(tags: str, search_path: Optional[str] = None):
        """
        Find files by macOS Finder tags.
        
        Query params: tags=work,blue&search_path=/path/to/search
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            tag_list = tags.split(",")
            result = fs.find_by_tags(tag_list, search_path)
            return result
        except Exception as e:
            logger.error(f"Find by tags failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/filesystem/batch-organize")
    async def batch_organize(request: Dict[str, Any]):
        """
        Batch organize files according to rules.
        
        Request: {
            "source_dir": "/path/to/dir",
            "rules": [
                {"pattern": "*.pdf", "action": "move", "destination": "~/Documents"},
                {"pattern": "*.jpg", "action": "tag", "tags": ["photos", "blue"]}
            ],
            "dry_run": true
        }
        """
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            result = fs.batch_organize(
                request.get("source_dir"),
                request.get("rules", []),
                dry_run=request.get("dry_run")
            )
            return result
        except Exception as e:
            logger.error(f"Batch organize failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.get("/polly/filesystem/history")
    async def get_operation_history(limit: int = 50):
        """Get recent file system operation history."""
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            history = fs.get_operation_history(limit)
            return {"success": True, "history": history}
        except Exception as e:
            logger.error(f"Get history failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/filesystem/organize")
    async def organize_with_llm(request: Dict[str, Any]):
        """
        Natural language file organization using LLM.
        
        Request: {
            "request": "Organize my Downloads folder by file type",
            "context": {"current_dir": "~/Downloads"},
            "auto_execute": false  # If true, executes after dry-run preview
        }
        
        Response includes:
        - Parsed operation plan
        - Dry-run results (always runs first)
        - Execution results (if auto_execute=true and user confirms)
        """
        from integrations.filesystem_llm import parse_filesystem_request
        
        manager = get_integration_manager()
        fs = manager.get_integration("filesystem")
        polly = get_polly()
        
        if not fs:
            raise HTTPException(404, "File system integration not available")
        
        try:
            user_request = request.get("request")
            context = request.get("context")
            auto_execute = request.get("auto_execute", False)
            
            if not user_request:
                raise HTTPException(400, "Missing 'request' field")
            
            # Parse the request using LLM
            plan = parse_filesystem_request(polly.llm, user_request, context)
            
            if "error" in plan:
                return plan
            
            # Validate operations
            from integrations.filesystem_llm import FileSystemLLMParser
            parser = FileSystemLLMParser(polly.llm)
            validation = parser.validate_operations(plan.get("operations", []))
            
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": "Invalid operations",
                    "validation": validation,
                    "plan": plan
                }
            
            # Execute operations (always in dry-run first)
            dry_run_results = []
            for op in plan.get("operations", []):
                op_type = op.get("type")
                params = op.get("params", {})
                
                # Force dry-run for safety
                if op_type == "batch_organize":
                    params["dry_run"] = True
                
                # Set integration to dry-run mode temporarily
                original_dry_run = fs.dry_run
                fs.dry_run = True
                
                try:
                    if op_type == "create_folder":
                        result = fs.create_folder(**params)
                    elif op_type == "move":
                        result = fs.move_file(**params)
                    elif op_type == "rename":
                        result = fs.rename_file(**params)
                    elif op_type == "tag":
                        result = fs.add_tags(**params)
                    elif op_type == "batch_organize":
                        result = fs.batch_organize(**params)
                    else:
                        result = {"success": False, "error": f"Unknown operation type: {op_type}"}
                    
                    dry_run_results.append({
                        "operation": op,
                        "result": result
                    })
                finally:
                    fs.dry_run = original_dry_run
            
            # Generate explanation
            explanation = parser.explain_operations(plan.get("operations", []))
            
            return {
                "success": True,
                "plan": plan,
                "validation": validation,
                "explanation": explanation,
                "dry_run_results": dry_run_results,
                "requires_confirmation": plan.get("requires_confirmation", True),
                "warnings": plan.get("warnings", [])
            }
            
        except Exception as e:
            logger.error(f"Organize with LLM failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    # ===== NOTES SOURCE MANAGEMENT ENDPOINTS =====
    
    @app.get("/polly/notes/source")
    async def get_notes_source():
        """
        Get current notes source configuration.
        
        Response: {
            "active_source": "native" | "obsidian",
            "notes_path": "/path/to/notes",
            "path_exists": true
        }
        """
        try:
            polly = get_polly()
            if not polly:
                return {
                    "active_source": "native",
                    "notes_path": None,
                    "path_exists": False
                }
            
            # Get notes source manager
            if not hasattr(polly, 'notes_source_manager') or not polly.notes_source_manager:
                return {
                    "active_source": "native",
                    "notes_path": None,
                    "path_exists": False
                }
            
            source_manager = polly.notes_source_manager
            active_source = source_manager.get_active_source()
            notes_path = source_manager.get_notes_path()
            
            import os
            path_exists = os.path.exists(notes_path) if notes_path else False
            
            return {
                "active_source": active_source,
                "notes_path": notes_path,
                "path_exists": path_exists
            }
            
        except Exception as e:
            logger.error(f"Get notes source failed: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get notes source: {str(e)}")
    
    @app.post("/polly/notes/sync/start")
    async def start_notes_sync():
        """
        Start automatic notes synchronization.
        
        Response: {
            "success": true,
            "message": "Notes sync started"
        }
        """
        try:
            polly = get_polly()
            if not polly:
                return {
                    "success": False,
                    "message": "Polly not initialized yet"
                }
            
            # Check if file watcher is already running
            if polly.notes_sync and hasattr(polly.notes_sync, 'is_running') and polly.notes_sync.is_running():
                return {
                    "success": True,
                    "message": "File watcher already running",
                    "is_running": True
                }
            
            # File watcher should have started during Polly initialization
            if not polly.notes_sync:
                return {
                    "success": False,
                    "message": "File watcher failed to initialize during Polly startup"
                }
            
            # File watcher exists but might not be running - try to start it
            if hasattr(polly.notes_sync, 'start'):
                polly.notes_sync.start()
                return {
                    "success": True,
                    "message": "File watcher started",
                    "is_running": True
                }
            
            return {
                "success": True,
                "message": "File watcher is active",
                "is_running": True
            }
            
        except Exception as e:
            logger.error(f"Start notes sync failed: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to start notes sync: {str(e)}")
    
    @app.post("/polly/notes/sync/stop")
    async def stop_notes_sync():
        """
        Stop automatic notes synchronization.
        
        Response: {
            "success": true,
            "message": "Notes sync stopped"
        }
        """
        try:
            # Check if Polly is initialized and has file watcher
            polly = get_polly()
            
            if not polly or not polly.notes_sync:
                return {
                    "success": False,
                    "message": "File watcher not initialized"
                }
            
            # Check if file watcher is running
            is_running = hasattr(polly.notes_sync, 'is_running') and polly.notes_sync.is_running()
            
            if not is_running:
                return {
                    "success": False,
                    "message": "File watcher not running"
                }
            
            # Stop the file watcher
            if hasattr(polly.notes_sync, 'stop'):
                polly.notes_sync.stop()
                return {
                    "success": True,
                    "message": "File watcher stopped"
                }
            
            return {
                "success": False,
                "message": "File watcher cannot be stopped"
            }
            
        except Exception as e:
            logger.error(f"Stop notes sync failed: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to stop notes sync: {str(e)}")
    
    @app.get("/polly/notes/sync/status")
    async def get_notes_sync_status():
        """
        Get notes sync status.
        
        Response: {
            "is_running": true,
            "stats": {...}
        }
        """
        try:
            # Check if Polly is initialized and has file watcher
            polly = get_polly()
            
            if not polly or not polly.notes_sync:
                return {
                    "is_running": False,
                    "message": "File watcher not initialized"
                }
            
            # Check if file watcher is running
            is_running = hasattr(polly.notes_sync, 'is_running') and polly.notes_sync.is_running()
            
            return {
                "is_running": is_running,
                "message": "File watcher active" if is_running else "File watcher not active"
            }
            
        except Exception as e:
            logger.error(f"Get sync status failed: {e}", exc_info=True)
            return {
                "is_running": False,
                "error": str(e)
            }
    
    @app.get("/polly/notes/reindex")
    async def reindex_notes(force: bool = True):
        """
        Re-index all notes to RAG with streaming progress.
        
        Request: {
            "notes_path": "/path/to/notes",  # Optional, uses config if not provided
            "force": true  # Force re-indexing even if up to date
        }
        
        Streams progress as Server-Sent Events (SSE):
        data: {"status": "started", "total": 110}
        data: {"status": "progress", "file": "note.md", "progress": 1, "total": 110}
        data: {"status": "completed", "total": 110, "duration_seconds": 45.2}
        data: {"status": "error", "error": "..."}
        """
        async def generate_progress():
            try:
                import time
                from core.notes_source_manager import NotesSourceManager
                from core.notes_sync_manager import get_sync_manager
                
                # Get notes path from config
                manager = NotesSourceManager()
                notes_path = Path(manager.get_notes_path()).expanduser()
                
                # Get sync manager (should already be running)
                sync_mgr = get_sync_manager()
                if not sync_mgr:
                    yield f"data: {json.dumps({'status': 'error', 'error': 'Notes sync manager not running'})}\n\n"
                    return
                
                # Find all markdown files
                md_files = sorted(notes_path.rglob("*.md"))
                total = len(md_files)
                
                # Send started event
                yield f"data: {json.dumps({'status': 'started', 'total': total})}\n\n"
                
                start_time = time.time()
                indexed_count = 0
                errors = []
                
                # Index each file
                for i, file_path in enumerate(md_files, 1):
                    try:
                        # Index file in RAG
                        sync_mgr._index_file_in_rag(file_path, force=force)
                        indexed_count += 1
                        
                        # Send progress event
                        progress_data = {
                            "status": "progress",
                            "file": file_path.name,
                            "progress": i,
                            "total": total,
                            "indexed": indexed_count
                        }
                        yield f"data: {json.dumps(progress_data)}\n\n"
                        
                        # Small delay to avoid overwhelming the client
                        await asyncio.sleep(0.01)
                        
                    except Exception as e:
                        error_msg = f"Failed to index {file_path.name}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        
                        # Send error for this file but continue
                        error_data = {
                            "status": "file_error",
                            "file": file_path.name,
                            "error": str(e),
                            "progress": i,
                            "total": total
                        }
                        yield f"data: {json.dumps(error_data)}\n\n"
                
                # Send completion event
                duration = time.time() - start_time
                completion_data = {
                    "status": "completed",
                    "total": total,
                    "indexed": indexed_count,
                    "errors": len(errors),
                    "duration_seconds": round(duration, 2)
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
            except Exception as e:
                logger.error(f"Re-index failed: {e}")
                yield f"data: {json.dumps({'status': 'error', 'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_progress(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering
            }
        )
    
    @app.get("/polly/notes/index")
    async def get_notes_index(domain: Optional[str] = None, limit: int = 1000):
        """
        Get all notes with metadata from the notes index.
        
        Query Params:
            domain (optional) - Filter by folder/domain
            limit (optional) - Limit results (default: 1000)
        
        Response: {
            "notes": [
                {
                    "name": "note-name",
                    "title": "Note Title",
                    "path": "/path/to/note.md",
                    "domain": "01-Sigils",
                    "tags": ["tag1", "tag2"],
                    "aliases": ["alias1"],
                    "created": "2026-01-01T00:00:00",
                    "modified": "2026-01-26T12:00:00",
                    "size": 1234
                }
            ],
            "stats": {
                "total": 86,
                "by_domain": {"01-Sigils": 12, "02-Signals": 8}
            }
        }
        """
        try:
            from core.notes_index import get_notes_index
            from core.notes_source_manager import NotesSourceManager
            
            # Get notes index
            notes_idx = get_notes_index()
            
            # Auto-build index if empty
            if len(notes_idx._notes_by_path) == 0:
                logger.info("Notes index is empty, building it now...")
                try:
                    manager = NotesSourceManager()
                    notes_path = Path(manager.get_notes_path()).expanduser()
                    
                    if not notes_path.exists():
                        logger.warning(f"Notes path does not exist: {notes_path}")
                        return {
                            "notes": [],
                            "stats": {
                                "total": 0,
                                "by_domain": {}
                            },
                            "error": f"Notes path does not exist: {notes_path}"
                        }
                    
                    stats = notes_idx.build_index(notes_path, recursive=True)
                    logger.info(f"Notes index built: {stats['notes_indexed']} notes indexed")
                except Exception as build_error:
                    logger.error(f"Failed to build notes index: {build_error}", exc_info=True)
                    return {
                        "notes": [],
                        "stats": {
                            "total": 0,
                            "by_domain": {}
                        },
                        "error": f"Failed to build notes index: {str(build_error)}"
                    }
            
            # Get all notes or filter by domain
            if domain:
                note_infos = notes_idx.get_notes_by_domain(domain)
            else:
                note_infos = notes_idx.get_all_notes()
            
            # Apply limit
            if limit > 0:
                note_infos = note_infos[:limit]
            
            # Convert NoteInfo objects to dicts
            notes = []
            by_domain = {}
            
            for note_info in note_infos:
                note_dict = {
                    "name": note_info.name,
                    "title": note_info.title,
                    "path": str(note_info.path),
                    "domain": note_info.domain,
                    "tags": note_info.tags,
                    "aliases": note_info.aliases,
                    "created": note_info.created.isoformat() if note_info.created else None,
                    "modified": note_info.modified.isoformat() if note_info.modified else None,
                    "size": note_info.size
                }
                notes.append(note_dict)
                
                # Count by domain
                domain_name = note_info.domain or "Other"
                by_domain[domain_name] = by_domain.get(domain_name, 0) + 1
            
            # Get total count (before limit)
            total_notes = len(notes_idx.get_all_notes())
            
            logger.debug(f"Returning {len(notes)} notes (limit: {limit}, total: {total_notes})")
            
            return {
                "notes": notes,
                "stats": {
                    "total": total_notes,
                    "by_domain": by_domain
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get notes index: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get notes index: {str(e)}")
    
    @app.post("/polly/notes/create")
    async def create_note(request: Dict[str, Any]):
        """
        Create a new note in the vault with duplicate detection.
        
        Request: {
            "name": "Note Name",
            "domain": "02-Signals",  # Folder name
            "content": "# Note Name\\n\\nInitial content...",  # Optional
            "check_duplicates": true  # Optional, default: true
        }
        
        Response (if similar notes found): {
            "status": "similar_found",
            "similar_notes": [...],
            "proposed_note": {...}
        }
        
        Response (if no duplicates or check_duplicates=false): {
            "success": true,
            "note": {
                "path": "/full/path/to/note.md",
                "name": "note-name",
                "title": "Note Name",
                "domain": "02-Signals"
            }
        }
        """
        try:
            from core.notes_index import get_notes_index
            from core.notes_source_manager import NotesSourceManager
            from core.notes_dedup import get_dedup_engine
            import os
            
            # Get parameters
            name = request.get("name")
            domain = request.get("domain")
            content = request.get("content", "")
            check_duplicates = request.get("check_duplicates", True)
            
            if not name:
                raise HTTPException(400, "Note name is required")
            if not domain:
                raise HTTPException(400, "Domain (folder) is required")
            
            # Normalize name to filename
            filename = name.lower().replace(" ", "_").replace("-", "_")
            filename = re.sub(r'[^\w_]', '', filename)  # Remove special chars
            
            # Get notes path from config
            manager = NotesSourceManager()
            notes_path = Path(manager.get_notes_path()).expanduser()
            
            # Build full path
            domain_path = notes_path / domain
            note_path = domain_path / f"{filename}.md"
            
            # Check if note already exists
            if note_path.exists():
                raise HTTPException(409, f"Note '{filename}' already exists in {domain}")
            
            # If no content provided, create basic template
            if not content:
                content = f"# {name}\n\n"
            
            # Check for similar notes if enabled (Phase 21)
            if check_duplicates:
                dedup_engine = get_dedup_engine()
                if dedup_engine:
                    try:
                        similar_notes = dedup_engine.check_similarity(
                            content=content,
                            title=name
                        )
                        
                        if similar_notes:
                            logger.info(f"Found {len(similar_notes)} similar notes for '{name}'")
                            return {
                                "status": "similar_found",
                                "similar_notes": [n.to_dict() for n in similar_notes],
                                "proposed_note": {
                                    "name": filename,
                                    "title": name,
                                    "domain": domain,
                                    "content": content
                                }
                            }
                    except Exception as e:
                        logger.error(f"Duplicate check failed: {e}")
                        # Continue with creation - dedup is nice-to-have
            
            # No duplicates found or check disabled - proceed with creation
            if not domain_path.exists():
                domain_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created domain folder: {domain_path}")
            
            # Write note file
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created note: {note_path}")
            
            # Re-index to include new note
            notes_idx = get_notes_index()
            notes_idx.build_index(notes_path, recursive=True)
            
            # Get the newly created note's info
            created_note = notes_idx.find_note_by_name(filename)
            
            if not created_note:
                created_note_info = {
                    "path": str(note_path),
                    "name": filename,
                    "title": name,
                    "domain": domain
                }
            else:
                created_note_info = {
                    "path": str(created_note.path),
                    "name": created_note.name,
                    "title": created_note.title,
                    "domain": created_note.domain,
                    "tags": created_note.tags
                }
            
            return {
                "success": True,
                "note": created_note_info
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create note failed: {e}")
            raise HTTPException(500, f"Failed to create note: {str(e)}")
    
    @app.post("/polly/notes/create-folder")
    async def create_notes_folder(request: Dict[str, Any]):
        """
        Create a new folder (domain) in the vault.
        
        Request: {
            "name": "New Folder Name"
        }
        
        Response: {
            "success": true,
            "folder": {
                "name": "New Folder Name",
                "path": "/full/path/to/folder"
            }
        }
        """
        try:
            from core.notes_source_manager import NotesSourceManager
            import os
            
            name = request.get("name")
            
            if not name:
                raise HTTPException(400, "Folder name is required")
            
            folder_name = name.strip()
            folder_name = re.sub(r'[^\w\s-]', '', folder_name)
            folder_name = re.sub(r'\s+', '-', folder_name)
            
            if not folder_name:
                raise HTTPException(400, "Invalid folder name")
            
            manager = NotesSourceManager()
            notes_path = Path(manager.get_notes_path()).expanduser()
            
            folder_path = notes_path / folder_name
            
            if folder_path.exists():
                raise HTTPException(409, f"Folder '{folder_name}' already exists")
            
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            
            return {
                "success": True,
                "folder": {
                    "name": folder_name,
                    "path": str(folder_path)
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create folder failed: {e}")
            raise HTTPException(500, f"Failed to create folder: {str(e)}")
    
    @app.put("/polly/notes/update")
    async def update_note(request: Dict[str, Any]):
        """
        Update/save note content.
        
        Request: {
            "path": "/full/path/to/note.md",
            "content": "Updated content..."
        }
        
        Response: {
            "success": true,
            "message": "Note saved successfully"
        }
        """
        try:
            note_path_str = request.get("path")
            content = request.get("content")
            
            if not note_path_str:
                raise HTTPException(400, "Note path is required")
            if content is None:
                raise HTTPException(400, "Content is required")
            
            note_path = Path(note_path_str)
            
            # Verify the note exists
            if not note_path.exists():
                raise HTTPException(404, f"Note not found: {note_path}")
            
            # Write updated content
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Updated note: {note_path}")
            
            # Re-index the note
            from core.notes_index import get_notes_index
            notes_idx = get_notes_index()
            note_obj = None
            try:
                notes_idx.index_single_file(note_path)
                # Get the indexed note for entity extraction
                note_name = note_path.stem
                note_obj = notes_idx.find_note_by_name(note_name)
            except Exception as idx_error:
                logger.warning(f"Failed to re-index note after update: {idx_error}")
                # Don't fail the save if re-indexing fails
            
            # Extract entities from note content (fire-and-forget background task)
            async def extract_entities_background():
                try:
                    polly = get_polly()
                    if polly and polly.entity_extractor and note_obj:
                        domains = [note_obj.domain] if note_obj.domain else []
                        polly.entity_extractor.extract_and_store(
                            content,
                            source_type="note",
                            source_id=note_obj.name,
                            domains=domains,
                            extract_relationships=True
                        )
                        logger.debug(f"Entity extraction completed for note: {note_obj.name}")
                except Exception as e:
                    logger.debug(f"Entity extraction failed for note (non-critical): {e}")
            
            # Fire background task
            import asyncio
            asyncio.create_task(extract_entities_background())
            
            # Return note metadata so UI can update modified time
            stat = note_path.stat()
            try:
                from datetime import timezone
                modified_iso = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
            except Exception:
                modified_iso = datetime.fromtimestamp(stat.st_mtime).isoformat()
            return {
                "success": True,
                "message": "Note saved successfully",
                "note": {"modified": modified_iso}
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update note failed: {e}")
            raise HTTPException(500, f"Failed to update note: {str(e)}")
    
    @app.post("/polly/graph/backfill")
    async def backfill_graph_entities():
        """
        One-time backfill: Extract entities from all indexed notes.
        
        This populates entity_mentions for existing notes that were saved
        before entity extraction was wired into the save path.
        
        Response: {
            "success": true,
            "processed": 42,
            "failed": 1,
            "message": "Processed 42 notes, 1 failed"
        }
        """
        try:
            polly = get_polly()
            if not polly or not polly.entity_extractor:
                raise HTTPException(503, "Entity extraction not available")
            
            from core.notes_index import get_notes_index
            notes_idx = get_notes_index()
            all_notes = notes_idx.get_all_notes()
            
            processed = 0
            failed = 0
            
            for note in all_notes:
                try:
                    # Read note content
                    content = note.path.read_text(encoding='utf-8')
                    domains = [note.domain] if note.domain else []
                    
                    # Extract and store entities
                    polly.entity_extractor.extract_and_store(
                        content,
                        source_type="note",
                        source_id=note.name,
                        domains=domains,
                        extract_relationships=True
                    )
                    processed += 1
                    
                    if processed % 10 == 0:
                        logger.info(f"Graph backfill: processed {processed}/{len(all_notes)} notes")
                        
                except Exception as e:
                    logger.warning(f"Failed to extract entities from {note.name}: {e}")
                    failed += 1
            
            logger.info(f"Graph backfill complete: {processed} processed, {failed} failed")
            
            return {
                "success": True,
                "processed": processed,
                "failed": failed,
                "message": f"Processed {processed} notes, {failed} failed"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Graph backfill failed: {e}")
            raise HTTPException(500, f"Failed to backfill graph: {str(e)}")
    
    @app.get("/polly/graph/list")
    async def get_graph_list(
        type: str = None,          # comma-separated: "note,conversation"
        domain: str = None,        # matches primary or secondary
        maturity: int = None,      # 10, 20, 30
        sort: str = "recent",      # authority, recent, alpha, created
        connection_status: str = None,  # hub, bridge, isolated, all
        q: str = None,             # text search
        limit: int = 100,
        offset: int = 0
    ):
        """
        Primary endpoint for graph-based navigation.
        Powers both Notes sidebar and Graph Browse tab.
        
        Returns enriched list of notes with entity connections, authority scores,
        cross-domain relationships, and connection patterns.
        
        Query params:
        - type: Content type filter (currently only "note" supported)
        - domain: Domain filter (matches primary OR secondary domains)
        - maturity: Maturity level filter (10, 20, or 30)
        - sort: Sort order (authority, recent, alpha, created)
        - connection_status: Connection pattern filter (hub, bridge, isolated, all)
        - q: Text search in note title/content
        - limit: Max results to return
        - offset: Pagination offset
        
        Response: {
            "items": [{
                "id": "note_name",
                "name": "Note Display Title",
                "type": "note",
                "primary_domain": "sigils",
                "secondary_domains": ["signals"],
                "authority_score": 0.82,
                "connection_count": 17,
                "inbound_count": 12,
                "outbound_count": 5,
                "connection_status": "hub",
                "maturity": 20,
                "tags": ["docker", "deployment"],
                "updated_at": "2026-02-15T...",
                "created_at": "2026-01-10T...",
                "path": "/path/to/note.md",
                "preview_snippet": "First 100 chars..."
            }],
            "total_count": 45,
            "domain_counts": {"sigils": 12, "signals": 8}
        }
        """
        try:
            from core.notes_index import get_notes_index
            from core.backlinks import get_backlinks_index
            from core.entities.store import EntityStore
            
            polly = get_polly()
            notes_idx = get_notes_index()
            backlinks_idx = get_backlinks_index(notes_idx)
            
            # Get all notes
            all_notes = notes_idx.get_all_notes()
            
            # Build enriched items
            items = []
            domain_counts = {}
            
            for note in all_notes:
                # Get backlink counts
                inbound = backlinks_idx.get_backlinks(note.name)
                outbound = backlinks_idx.get_outgoing_links(note.name)
                connection_count = len(inbound) + len(outbound)
                
                # Compute connection status
                if connection_count > 10:
                    conn_status = "hub"
                elif connection_count <= 2:
                    conn_status = "isolated"
                else:
                    conn_status = "normal"
                
                # Get entity-based authority score (if available)
                authority_score = 0.0
                secondary_domains = []
                if polly and polly.entity_store:
                    try:
                        # Query entity_mentions for this note
                        conn = polly.entity_store._conn()
                        cur = conn.execute(
                            "SELECT DISTINCT entity_id FROM entity_mentions WHERE source_type='note' AND source_id=?",
                            (note.name,)
                        )
                        entity_ids = [row[0] for row in cur.fetchall()]
                        
                        if entity_ids:
                            # Get average authority of connected entities
                            placeholders = ','.join(['?'] * len(entity_ids))
                            cur = conn.execute(
                                f"SELECT AVG(authority_score) FROM entities WHERE id IN ({placeholders})",
                                entity_ids
                            )
                            avg_auth = cur.fetchone()[0]
                            if avg_auth is not None:
                                authority_score = float(avg_auth)
                            
                            # Get secondary domains from connected entities
                            cur = conn.execute(
                                f"SELECT domains FROM entities WHERE id IN ({placeholders})",
                                entity_ids
                            )
                            import json
                            all_domains = set()
                            for row in cur.fetchall():
                                domains_json = row[0]
                                if domains_json:
                                    doms = json.loads(domains_json)
                                    all_domains.update(doms)
                            
                            # Secondary domains = all connected domains except primary
                            if note.domain:
                                all_domains.discard(note.domain)
                            secondary_domains = list(all_domains)
                            
                    except Exception as e:
                        logger.debug(f"Failed to compute authority/secondary domains for {note.name}: {e}")
                
                # Build item
                item = {
                    "id": note.name,
                    "name": note.title or note.name,
                    "type": "note",
                    "primary_domain": note.domain or "",
                    "secondary_domains": secondary_domains,
                    "authority_score": authority_score,
                    "connection_count": connection_count,
                    "inbound_count": len(inbound),
                    "outbound_count": len(outbound),
                    "connection_status": conn_status,
                    "maturity": 20,  # TODO: Extract from frontmatter or metadata
                    "tags": note.tags or [],
                    "updated_at": note.modified.isoformat() if note.modified else "",
                    "created_at": note.created.isoformat() if note.created else "",
                    "path": str(note.path),
                    "preview_snippet": ""  # TODO: Read first 100 chars of content
                }
                
                # Apply filters
                # Type filter
                if type and "note" not in type.split(","):
                    continue
                
                # Domain filter (matches primary or secondary)
                if domain:
                    if note.domain != domain and domain not in secondary_domains:
                        continue
                
                # Maturity filter
                if maturity and item["maturity"] != maturity:
                    continue
                
                # Connection status filter
                if connection_status and connection_status != "all":
                    if conn_status != connection_status:
                        continue
                
                # Text search filter
                if q:
                    q_lower = q.lower()
                    if q_lower not in (note.title or "").lower() and q_lower not in note.name.lower():
                        continue
                
                items.append(item)
                
                # Count domains
                if note.domain:
                    domain_counts[note.domain] = domain_counts.get(note.domain, 0) + 1
            
            # Sort items
            if sort == "authority":
                items.sort(key=lambda x: x["authority_score"], reverse=True)
            elif sort == "recent":
                items.sort(key=lambda x: x["updated_at"], reverse=True)
            elif sort == "alpha":
                items.sort(key=lambda x: x["name"].lower())
            elif sort == "created":
                items.sort(key=lambda x: x["created_at"], reverse=True)
            
            # Apply pagination
            total_count = len(items)
            items = items[offset:offset + limit]
            
            return {
                "items": items,
                "total_count": total_count,
                "domain_counts": domain_counts
            }
            
        except Exception as e:
            logger.error(f"Graph list failed: {e}")
            raise HTTPException(500, f"Failed to get graph list: {str(e)}")
    
    @app.get("/polly/graph/nodes")
    async def get_graph_nodes(
        type: str = None,          # Entity type filter (concept, tool, etc.)
        domain: str = None,        # Domain filter
        maturity: int = None,      # Maturity filter (unused for entities currently)
        authority_min: float = None,  # Minimum authority score
        confidence_min: float = None,  # Minimum relationship strength
        center_node: str = None,   # "Explore From Here" — return N-hop neighborhood
        hops: int = 2,             # Max hops from center_node
        include_ghosts: bool = True,  # Include filtered-out nodes within 1-2 hops
        limit: int = 500,
        offset: int = 0
    ):
        """
        Powers the Cytoscape.js graph canvas.
        
        Two modes:
        1. Full-graph mode (no center_node): Returns all entities matching filters
        2. Center-node mode (center_node set): Returns N-hop neighborhood from center
        
        Query params:
        - type: Entity type filter (comma-separated: "concept,tool")
        - domain: Domain filter (matches entities with this domain)
        - authority_min: Minimum authority score (0.0-1.0)
        - confidence_min: Minimum relationship strength (0.0-1.0)
        - center_node: Entity ID to explore from (enables neighborhood mode)
        - hops: Max hops from center_node (default 2)
        - include_ghosts: Include filtered-out nodes within 1-2 hops (default true)
        - limit: Max nodes to return
        - offset: Pagination offset
        
        Response: {
            "nodes": [{
                "id": "entity_id",
                "name": "Entity Name",
                "type": "concept",
                "domains": ["sigils"],
                "authority": 0.85,
                "is_ghost": false
            }],
            "edges": [{
                "source": "entity_id_1",
                "target": "entity_id_2",
                "type": "related_to",
                "strength": 0.7,
                "is_ghost": false
            }],
            "total_node_count": 150,
            "ghost_count": 12
        }
        """
        try:
            polly = get_polly()
            if not polly or not polly.entity_store:
                raise HTTPException(503, "Entity store not available")
            
            from core.entities.models import EntityQuery, EntityType
            
            store = polly.entity_store
            nodes = []
            edges = []
            ghost_count = 0
            
            # Build entity filters
            entity_types = []
            if type:
                for t in type.split(","):
                    try:
                        entity_types.append(EntityType(t.strip()))
                    except ValueError:
                        pass
            
            domains_filter = []
            if domain:
                domains_filter = [d.strip() for d in domain.split(",")]
            
            if center_node:
                # CENTER-NODE MODE: Get N-hop neighborhood
                logger.debug(f"Graph nodes: center_node mode, entity={center_node}, hops={hops}")
                
                # Get center entity
                center_entity = store.get_entity(center_node)
                if not center_entity:
                    raise HTTPException(404, f"Center node not found: {center_node}")
                
                # Use EntityStore.get_related() for BFS traversal
                min_strength = confidence_min if confidence_min else 0.0
                related = store.get_related(center_node, max_hops=hops, min_strength=min_strength)
                
                # Build visible entities set
                visible_entities = {center_node: center_entity}
                for ent, rel in related:
                    visible_entities[ent.id] = ent
                
                # Apply filters to visible entities
                filtered_visible = {}
                filtered_out = {}
                
                for ent_id, ent in visible_entities.items():
                    passes_filter = True
                    
                    # Type filter
                    if entity_types and ent.entity_type not in entity_types:
                        passes_filter = False
                    
                    # Domain filter
                    if domains_filter:
                        if not any(d in ent.domains for d in domains_filter):
                            passes_filter = False
                    
                    # Authority filter
                    if authority_min and ent.authority_score < authority_min:
                        passes_filter = False
                    
                    if passes_filter:
                        filtered_visible[ent_id] = ent
                    else:
                        filtered_out[ent_id] = ent
                
                # Ghost computation: include filtered-out nodes within 1-2 hops of visible nodes
                ghosts = {}
                if include_ghosts and filtered_out and len(filtered_visible) < 100:  # Performance cap
                    for vis_id in list(filtered_visible.keys())[:20]:  # Limit ghost computation
                        try:
                            ghost_candidates = store.get_related(vis_id, max_hops=1, min_strength=0.0)
                            for ghost_ent, _ in ghost_candidates[:10]:  # Max 10 ghosts per visible
                                if ghost_ent.id in filtered_out and ghost_ent.id not in ghosts:
                                    ghosts[ghost_ent.id] = ghost_ent
                                    if len(ghosts) >= 100:  # Max 100 total ghosts
                                        break
                        except Exception as e:
                            logger.debug(f"Ghost computation failed for {vis_id}: {e}")
                
                ghost_count = len(ghosts)
                
                # Build nodes list
                for ent in filtered_visible.values():
                    nodes.append({
                        "id": ent.id,
                        "name": ent.name,
                        "type": ent.entity_type.value,
                        "domains": ent.domains,
                        "authority": ent.authority_score,
                        "is_ghost": False
                    })
                
                for ent in ghosts.values():
                    nodes.append({
                        "id": ent.id,
                        "name": ent.name,
                        "type": ent.entity_type.value,
                        "domains": ent.domains,
                        "authority": ent.authority_score,
                        "is_ghost": True
                    })
                
                # Build edges list (relationships between visible + ghost nodes)
                all_node_ids = set(filtered_visible.keys()) | set(ghosts.keys())
                for ent_id in all_node_ids:
                    neighbor_rels = store._get_neighbor_rels(ent_id)
                    for rel, other_id in neighbor_rels:
                        if other_id in all_node_ids:
                            # Check if edge already added (avoid duplicates for bidirectional)
                            edge_key = tuple(sorted([rel.source_id, rel.target_id]))
                            is_ghost_edge = (rel.source_id in ghosts) or (rel.target_id in ghosts)
                            
                            edges.append({
                                "source": rel.source_id,
                                "target": rel.target_id,
                                "type": rel.relationship_type.value,
                                "strength": rel.strength,
                                "is_ghost": is_ghost_edge
                            })
                
            else:
                # FULL-GRAPH MODE: Get all entities matching filters
                logger.debug(f"Graph nodes: full-graph mode, filters: type={type}, domain={domain}")
                
                query = EntityQuery(
                    entity_types=entity_types if entity_types else None,
                    domains=domains_filter if domains_filter else None,
                    min_authority=authority_min if authority_min else 0.0,
                    limit=limit + offset  # Get more for pagination
                )
                
                entities = store.search(query)
                
                # Apply pagination
                total_count = len(entities)
                entities = entities[offset:offset + limit]
                
                # Build nodes
                for ent in entities:
                    nodes.append({
                        "id": ent.id,
                        "name": ent.name,
                        "type": ent.entity_type.value,
                        "domains": ent.domains,
                        "authority": ent.authority_score,
                        "is_ghost": False
                    })
                
                # Build edges between visible nodes
                entity_ids = {ent.id for ent in entities}
                seen_edges = set()
                
                for ent in entities:
                    neighbor_rels = store._get_neighbor_rels(ent.id)
                    for rel, other_id in neighbor_rels:
                        if other_id in entity_ids:
                            # Apply confidence filter
                            if confidence_min and rel.strength < confidence_min:
                                continue
                            
                            # Avoid duplicate edges
                            edge_key = tuple(sorted([rel.source_id, rel.target_id, rel.relationship_type.value]))
                            if edge_key in seen_edges:
                                continue
                            seen_edges.add(edge_key)
                            
                            edges.append({
                                "source": rel.source_id,
                                "target": rel.target_id,
                                "type": rel.relationship_type.value,
                                "strength": rel.strength,
                                "is_ghost": False
                            })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "total_node_count": len(nodes),
                "ghost_count": ghost_count
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Graph nodes failed: {e}")
            raise HTTPException(500, f"Failed to get graph nodes: {str(e)}")
    
    @app.get("/polly/notes/{note_name}/backlinks")
    async def get_note_backlinks(note_name: str):
        """
        Get all backlinks to a specific note.
        
        Returns notes that link to this note.
        
        Response: {
            "backlinks": [
                {
                    "name": "linking-note",
                    "title": "Linking Note Title",
                    "path": "/path/to/linking-note.md",
                    "domain": "02-Signals"
                }
            ],
            "count": 3
        }
        """
        try:
            from core.notes_index import get_notes_index
            from core.backlinks import get_backlinks_index
            
            notes_idx = get_notes_index()
            backlinks_idx = get_backlinks_index(notes_idx)
            
            # Find the target note
            target_note = notes_idx.find_note_by_name(note_name)
            if not target_note:
                # Return empty backlinks if note not found (not an error)
                return {
                    "backlinks": [],
                    "count": 0
                }
            
            # Get backlinks from BacklinksIndex
            backlink_objects = backlinks_idx.get_backlinks(note_name)
            
            # Convert Backlink objects to response format
            backlinks = []
            for backlink in backlink_objects:
                # Resolve source note info
                source_note = notes_idx.find_note_by_name(backlink.source_name)
                if source_note:
                    backlinks.append({
                        "name": source_note.name,
                        "title": source_note.title,
                        "path": str(source_note.path),
                        "domain": source_note.domain
                    })
            
            return {
                "backlinks": backlinks,
                "count": len(backlinks)
            }
            
        except Exception as e:
            logger.error(f"Get backlinks failed for '{note_name}': {e}")
            # Return empty backlinks on error (graceful degradation)
            return {
                "backlinks": [],
                "count": 0,
                "error": str(e)
            }
    
    # ===== TEMPLATE ENDPOINTS (Phase 16e) =====
    
    @app.get("/polly/templates")
    async def get_templates():
        """
        Get all available templates for gallery.
        
        Response: {
            "templates": [
                {
                    "filename": "meeting-notes.md",
                    "name": "Meeting Notes",
                    "icon": "calendar",
                    "description": "For discussions, decisions, and action items",
                    "category": "collaboration",
                    "tags": ["meetings", "discussion"],
                    "variables": ["title", "date", "attendees", ...]
                },
                ...
            ],
            "count": 6
        }
        """
        polly = get_polly()
        if not polly:
            raise HTTPException(503, "Polly not initialized")
        try:
            from core.templates import TemplateManager
            
            # Get vault path and templates folder from config
            vault_path_str = polly.config.get("obsidian.vault_path")
            if not vault_path_str:
                logger.warning("Vault path not configured for templates")
                return {
                    "templates": [],
                    "count": 0
                }
            
            vault_path = Path(vault_path_str)
            templates_folder = polly.config.get("templates.folder", ".polly/templates")
            templates_dir = vault_path / templates_folder
            
            # Check if templates directory exists
            if not templates_dir.exists():
                logger.warning(f"Templates directory not found: {templates_dir}")
                return {
                    "templates": [],
                    "count": 0,
                    "error": f"Templates directory not found: {templates_dir}"
                }
            
            # Load templates
            manager = TemplateManager(str(templates_dir))
            templates_metadata = manager.get_gallery_metadata()
            
            return {
                "templates": templates_metadata,
                "count": len(templates_metadata)
            }
            
        except Exception as e:
            logger.error(f"Failed to load templates: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to load templates: {str(e)}")
    
    @app.get("/polly/templates/{filename}")
    async def get_template(filename: str):
        """
        Get specific template definition and content.
        
        Response: {
            "filename": "meeting-notes.md",
            "name": "Meeting Notes",
            "icon": "calendar",
            "description": "...",
            "category": "collaboration",
            "tags": [...],
            "markdown_content": "# {{title}}\n\n...",
            "frontmatter": {...},
            "variables": ["title", "date", ...]
        }
        """
        try:
            from core.templates import TemplateManager
            
            # Get vault path and templates folder from config
            polly = get_polly()
            if not polly:
                raise HTTPException(503, "Polly not initialized")
            
            vault_path_str = polly.config.get("obsidian.vault_path")
            if not vault_path_str:
                raise HTTPException(503, "Vault path not configured")
            
            vault_path = Path(vault_path_str)
            templates_folder = polly.config.get("templates.folder", ".polly/templates")
            templates_dir = vault_path / templates_folder
            
            # Load template
            manager = TemplateManager(str(templates_dir))
            template = manager.load_template(filename)
            
            if not template:
                raise HTTPException(404, f"Template not found: {filename}")
            
            return template.to_dict_full()
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to load template {filename}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to load template: {str(e)}")
    
    # ===== OBSIDIAN WRITE ENDPOINTS =====
    
    @app.post("/polly/obsidian/create-note")
    async def create_obsidian_note(request: Dict[str, Any]):
        """
        Create a new note in Obsidian vault.
        
        Request: {
            "title": "Note Title",
            "content": "Note content...",
            "folder": "01-Sigils",  # Optional
            "tags": ["active", "idea"],  # Optional
            "frontmatter": {...},  # Optional additional fields
            "confirmed": false  # Set to true to execute
        }
        
        Response: {
            "preview": {...},  # Preview of note to create
            "requires_confirmation": true,
            "validation": {...}
        }
        
        Or if confirmed=true: {
            "success": true,
            "note_path": "01-Sigils/Note.md",
            "message": "..."
        }
        """
        manager = get_integration_manager()
        obsidian = manager.get_integration("obsidian")
        
        if not obsidian:
            raise HTTPException(404, "Obsidian integration not available")
        
        try:
            confirmed = request.get("confirmed", False)
            
            if not confirmed:
                # Prepare preview
                preview = obsidian.create_note(
                    title=request.get("title"),
                    content=request.get("content", ""),
                    folder=request.get("folder"),
                    tags=request.get("tags"),
                    frontmatter=request.get("frontmatter")
                )
                return preview
            else:
                # Execute confirmed operation
                preview = request.get("preview")
                if not preview:
                    raise HTTPException(400, "Preview data required for confirmed operation")
                
                result = obsidian.execute_create_note(preview)
                return result
                
        except Exception as e:
            logger.error(f"Create note failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/obsidian/append")
    async def append_to_obsidian_note(request: Dict[str, Any]):
        """
        Append content to existing note.
        
        Request: {
            "note_path": "01-Sigils/Note.md",
            "content": "Content to append...",
            "section": "Optional Section Name",  # Optional
            "confirmed": false
        }
        """
        manager = get_integration_manager()
        obsidian = manager.get_integration("obsidian")
        
        if not obsidian:
            raise HTTPException(404, "Obsidian integration not available")
        
        try:
            confirmed = request.get("confirmed", False)
            
            if not confirmed:
                # Prepare preview
                preview = obsidian.append_to_note(
                    note_path=request.get("note_path"),
                    content=request.get("content"),
                    section=request.get("section")
                )
                return preview
            else:
                # Execute confirmed operation
                preview = request.get("preview")
                if not preview:
                    raise HTTPException(400, "Preview data required for confirmed operation")
                
                result = obsidian.execute_append_to_note(preview)
                return result
                
        except Exception as e:
            logger.error(f"Append to note failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.post("/polly/obsidian/update-frontmatter")
    async def update_obsidian_frontmatter(request: Dict[str, Any]):
        """
        Update frontmatter fields in existing note.
        
        Request: {
            "note_path": "01-Sigils/Note.md",
            "updates": {
                "tags": ["updated", "tag"],
                "domain": "sigils",
                "custom_field": "value"
            },
            "confirmed": false
        }
        """
        manager = get_integration_manager()
        obsidian = manager.get_integration("obsidian")
        
        if not obsidian:
            raise HTTPException(404, "Obsidian integration not available")
        
        try:
            confirmed = request.get("confirmed", False)
            
            if not confirmed:
                # Prepare preview
                preview = obsidian.update_frontmatter(
                    note_path=request.get("note_path"),
                    updates=request.get("updates")
                )
                return preview
            else:
                # Execute confirmed operation
                preview = request.get("preview")
                if not preview:
                    raise HTTPException(400, "Preview data required for confirmed operation")
                
                result = obsidian.execute_update_frontmatter(preview)
                return result
                
        except Exception as e:
            logger.error(f"Update frontmatter failed: {e}")
            raise HTTPException(500, f"Operation failed: {str(e)}")
    
    @app.get("/polly/obsidian/suggest-folder")
    async def suggest_obsidian_folder(
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[str] = None
    ):
        """
        Get folder suggestion based on content analysis (Phase 3).
        
        Query params:
            title: Note title
            content: Note content
            tags: Comma-separated tags
        
        Response: {
            "suggested_folder": "01-Sigils",
            "domain": "sigils",
            "confidence": 0.85,
            "alternatives": [...]
        }
        """
        smart = get_obsidian_smart()
        
        if not smart:
            raise HTTPException(404, "Obsidian smart features not available")
        
        if not title or not content:
            raise HTTPException(400, "Both title and content required")
        
        try:
            result = await smart.suggest_folder(
                content=content,
                title=title,
                existing_structure=None  # TODO: Get from vault
            )
            return result
        except Exception as e:
            logger.error(f"Folder suggestion failed: {e}")
            raise HTTPException(500, f"Suggestion failed: {str(e)}")
    
    @app.get("/polly/obsidian/suggest-tags")
    async def suggest_obsidian_tags(
        title: Optional[str] = None,
        content: Optional[str] = None,
        folder: Optional[str] = None,
        existing_tags: Optional[str] = None
    ):
        """
        Get tag suggestions based on content and context (Phase 3).
        
        Query params:
            title: Note title
            content: Note content
            folder: Target folder
            existing_tags: Comma-separated existing tags
        
        Response: {
            "suggested_tags": [{"tag": "active", "confidence": 0.9, "source": "domain"}],
            "tag_groups": {...},
            "reasoning": "..."
        }
        """
        smart = get_obsidian_smart()
        
        if not smart:
            raise HTTPException(404, "Obsidian smart features not available")
        
        if not title or not content:
            raise HTTPException(400, "Both title and content required")
        
        try:
            # Parse existing tags
            tags_list = []
            if existing_tags:
                tags_list = [t.strip() for t in existing_tags.split(',')]
            
            result = await smart.suggest_tags(
                content=content,
                title=title,
                existing_tags=tags_list
            )
            return result
        except Exception as e:
            logger.error(f"Tag suggestion failed: {e}")
            raise HTTPException(500, f"Suggestion failed: {str(e)}")
    
    @app.get("/polly/obsidian/find-related")
    async def find_related_notes(
        note_path: Optional[str] = None,
        content: Optional[str] = None,
        title: Optional[str] = None,
        limit: int = 5,
        min_similarity: float = 0.01  # Lower threshold for hybrid search scores
    ):
        """
        Find related notes using RAG similarity search (Phase 3).
        
        Query params:
            note_path: Path to existing note
            content: Or content to match against
            title: Note title for context
            limit: Max number of results (default: 5)
            min_similarity: Minimum similarity threshold (default: 0.7)
        
        Response: {
            "related_notes": [
                {"path": "...", "title": "...", "similarity": 0.85, "connections": {...}},
                ...
            ],
            "grouped_by_domain": {...},
            "suggested_links": [...]
        }
        """
        smart = get_obsidian_smart()
        
        if not smart:
            raise HTTPException(404, "Obsidian smart features not available")
        
        if not note_path and not content:
            raise HTTPException(400, "Either note_path or content required")
        
        try:
            result = await smart.find_related_notes(
                note_path=note_path,
                content=content,
                title=title,
                top_k=limit,
                min_similarity=min_similarity
            )
            return result
        except Exception as e:
            logger.error(f"Find related notes failed: {e}")
            raise HTTPException(500, f"Search failed: {str(e)}")
    
    @app.post("/polly/obsidian/daily-note")
    async def create_daily_note(request: Dict[str, Any]):
        """
        Create daily note from template.
        
        Request: {
            "date": "2026-01-20",  # Optional, defaults to today
            "template_name": "daily",  # Optional
            "confirmed": false
        }
        """
        from integrations.obsidian_templates import TemplateEngine, DailyNoteTemplate
        from datetime import datetime
        
        manager = get_integration_manager()
        obsidian = manager.get_integration("obsidian")
        
        if not obsidian:
            raise HTTPException(404, "Obsidian integration not available")
        
        try:
            # Parse date
            date_str = request.get("date")
            if date_str:
                note_date = datetime.fromisoformat(date_str)
            else:
                note_date = datetime.now()
            
            # Initialize template engine
            vault_path = Path(obsidian.vault_path)
            templates_dir = vault_path / "00-System" / "templates"
            engine = TemplateEngine(templates_dir)
            
            # Load template or use default
            template_name = request.get("template_name", "daily")
            try:
                if templates_dir.exists():
                    template = engine.load_template(template_name)
                else:
                    template = DailyNoteTemplate.get_default()
            except FileNotFoundError:
                logger.info(f"Template {template_name} not found, using default")
                template = DailyNoteTemplate.get_default()
            
            # Build context
            context = {
                "date": note_date,
                "title": note_date.strftime("%Y-%m-%d"),
                "folder": "20-Daily",
                # Optional: Could fetch from calendar/reminders integrations
                "events": request.get("events", []),
                "tasks": request.get("tasks", []),
                "projects": request.get("projects", []),
                "recent_notes": request.get("recent_notes", [])
            }
            
            # Render template
            content = engine.render(template, context)
            
            # Generate note path
            note_path = f"20-Daily/{note_date.strftime('%Y-%m-%d')}.md"
            
            # Check if confirmed or preview
            confirmed = request.get("confirmed", False)
            
            if confirmed:
                # Create the note
                result = obsidian.create_note(
                    path=note_path,
                    content=content
                )
                return {
                    "status": "created",
                    "path": note_path,
                    "content": content,
                    "date": note_date.isoformat()
                }
            else:
                # Return preview
                return {
                    "status": "preview",
                    "path": note_path,
                    "content": content,
                    "date": note_date.isoformat(),
                    "message": "Preview only. Set confirmed=true to create."
                }
                
        except Exception as e:
            logger.error(f"Error creating daily note: {e}")
            raise HTTPException(500, f"Failed to create daily note: {str(e)}")
    
    @app.post("/polly/obsidian/from-conversation")
    async def create_note_from_conversation(request: Dict[str, Any]):
        """
        Convert conversation to structured note.
        
        Request: {
            "conversation_id": "...",  # Optional if providing messages directly
            "messages": [...],  # Optional if providing conversation_id
            "title": "...",  # Optional, will be generated
            "folder": "...",  # Optional, will be suggested
            "confirmed": false
        }
        """
        manager = get_integration_manager()
        obsidian = manager.get_integration("obsidian")
        
        if not obsidian:
            raise HTTPException(404, "Obsidian integration not available")
        
        try:
            # Get conversation content
            conversation_id = request.get("conversation_id")
            messages = request.get("messages", [])
            
            if conversation_id:
                # TODO: Fetch from conversation history when that's implemented
                # For now, require messages to be passed directly
                if not messages:
                    raise HTTPException(
                        400, 
                        "Either messages array or valid conversation_id required"
                    )
            
            if not messages:
                raise HTTPException(400, "No messages provided")
            
            # Build content from conversation
            content_parts = []
            
            # Extract user queries and assistant responses
            key_points = []
            code_blocks = []
            
            for msg in messages:
                role = msg.get("role", "user")
                text = msg.get("content", "")
                
                if role == "user":
                    key_points.append(f"- **Q:** {text[:200]}...")
                elif role == "assistant":
                    # Extract code blocks if present
                    code_pattern = r'```(\w+)?\n(.*?)```'
                    codes = re.findall(code_pattern, text, re.DOTALL)
                    if codes:
                        for lang, code in codes:
                            code_blocks.append(f"```{lang}\n{code.strip()}\n```")
                    
                    # Add summary
                    summary = text[:300].replace('\n', ' ')
                    key_points.append(f"- **A:** {summary}...")
            
            # Generate title if not provided
            title = request.get("title")
            if not title:
                # Use first user message as basis
                first_msg = next((m["content"] for m in messages if m.get("role") == "user"), "")
                title = first_msg[:60].strip()
                if len(first_msg) > 60:
                    title += "..."
            
            # Get smart features for folder/tag suggestions
            smart = get_obsidian_smart()
            
            # Combine messages for analysis
            full_conversation = "\n".join([m.get("content", "") for m in messages])
            
            # Suggest folder
            folder_result = await smart.suggest_folder(
                content=full_conversation,
                title=title
            )
            suggested_folder = folder_result.get("suggested_folder", "30-Ideas")
            
            # Suggest tags
            tags_result = await smart.suggest_tags(
                content=full_conversation,
                title=title,
                existing_tags=[]
            )
            suggested_tags = tags_result.get("suggestions", [])
            tag_names = [t["tag"] for t in suggested_tags[:5]]  # Top 5 tags
            
            # Build note content
            frontmatter = f"""---
created: {datetime.now().isoformat()}
type: conversation-note
tags: [{', '.join(tag_names)}]
conversation_id: {conversation_id or 'manual'}
---

"""
            
            content = frontmatter + f"# {title}\n\n"
            content += "## Summary\n\n"
            content += "\n".join(key_points[:10])  # Top 10 exchanges
            content += "\n\n"
            
            if code_blocks:
                content += "## Code Examples\n\n"
                content += "\n\n".join(code_blocks[:5])  # Top 5 code blocks
                content += "\n\n"
            
            content += "## Full Conversation\n\n"
            for msg in messages:
                role = msg.get("role", "user").title()
                text = msg.get("content", "")
                content += f"**{role}:** {text}\n\n---\n\n"
            
            # Use user-provided folder or suggested
            folder = request.get("folder", suggested_folder)
            note_path = f"{folder}/{title}.md"
            
            # Check if confirmed
            confirmed = request.get("confirmed", False)
            
            if confirmed:
                # Create the note
                result = obsidian.create_note(
                    path=note_path,
                    content=content
                )
                return {
                    "status": "created",
                    "path": note_path,
                    "title": title,
                    "suggested_tags": tag_names,
                    "content_preview": content[:500] + "..."
                }
            else:
                # Return preview with suggestions
                return {
                    "status": "preview",
                    "path": note_path,
                    "title": title,
                    "suggested_folder": suggested_folder,
                    "folder_confidence": folder_result.get("confidence", 0),
                    "suggested_tags": tag_names,
                    "content": content,
                    "message": "Preview only. Set confirmed=true to create."
                }
                
        except Exception as e:
            logger.error(f"Error creating note from conversation: {e}")
            raise HTTPException(500, f"Failed to create note: {str(e)}")
    
    # ============================================
    # Domain Configuration Endpoints (Phase 1.5)
    # ============================================
    
    @app.get("/polly/domains/config")
    async def get_domains_config():
        """
        Get complete domain configuration.
        
        Response: {
            "version": "1.0",
            "folderNumbering": true,
            "domains": [...],
            "lastModified": "2026-01-24T..."
        }
        """
        try:
            from core.domain_config import load_domains
            
            config = load_domains()
            
            # Convert to dict format for JSON response
            return {
                "version": config.version,
                "folderNumbering": config.folder_numbering,
                "domains": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "description": d.description,
                        "color": d.color,
                        "icon": d.icon,
                        "folderPath": d.folder_path,
                        "ragWeight": d.rag_weight,
                        "autoTagRules": d.auto_tag_rules,
                        "created": d.created,
                        "modified": d.modified,
                        "order": d.order
                    }
                    for d in config.domains
                ],
                "lastModified": config.last_modified
            }
        except Exception as e:
            logger.error(f"Error loading domains config: {e}")
            raise HTTPException(500, f"Failed to load domains config: {str(e)}")
    
    @app.post("/polly/domains")
    async def create_domain(request: Dict[str, Any]):
        """
        Create a new domain.
        
        Request: {
            "id": "custom",
            "name": "Custom Domain",
            "description": "My custom domain",
            "color": "#ff6b6b",
            "icon": "🔧",
            "ragWeight": 0.2,
            "autoTagRules": ["keyword1", "keyword2"]
        }
        
        Response: {
            "success": true,
            "domain": {...}
        }
        """
        try:
            from core.domain_config import load_domains, save_domains, DomainConfig
            from datetime import datetime
            
            config = load_domains()
            
            # Validate required fields
            domain_id = request.get("id")
            name = request.get("name")
            
            if not domain_id or not name:
                raise HTTPException(400, "Domain id and name are required")
            
            # Check for duplicate ID
            if any(d.id == domain_id for d in config.domains):
                raise HTTPException(400, f"Domain with id '{domain_id}' already exists")
            
            # Check for duplicate name
            if any(d.name == name for d in config.domains):
                raise HTTPException(400, f"Domain with name '{name}' already exists")
            
            # Determine next order
            max_order = max((d.order for d in config.domains), default=0)
            
            # Generate folder path if not provided
            folder_path = request.get("folderPath")
            if not folder_path:
                if config.folder_numbering:
                    folder_path = f"{(max_order + 1):02d}-{name}"
                else:
                    folder_path = name
            
            # Create new domain
            now = datetime.now().isoformat()
            new_domain = DomainConfig(
                id=domain_id,
                name=name,
                description=request.get("description", ""),
                color=request.get("color", "#808080"),
                icon=request.get("icon", "📁"),
                folder_path=folder_path,
                rag_weight=request.get("ragWeight", 0.0),
                auto_tag_rules=request.get("autoTagRules", []),
                created=now,
                modified=now,
                order=max_order + 1
            )
            
            # Add to config
            config.domains.append(new_domain)
            
            # Normalize RAG weights
            total_weight = sum(d.rag_weight for d in config.domains)
            if total_weight > 0:
                for d in config.domains:
                    d.rag_weight = d.rag_weight / total_weight
            
            # Save config
            save_domains(config)
            
            return {
                "success": True,
                "domain": {
                    "id": new_domain.id,
                    "name": new_domain.name,
                    "description": new_domain.description,
                    "color": new_domain.color,
                    "icon": new_domain.icon,
                    "folderPath": new_domain.folder_path,
                    "ragWeight": new_domain.rag_weight,
                    "autoTagRules": new_domain.auto_tag_rules,
                    "created": new_domain.created,
                    "modified": new_domain.modified,
                    "order": new_domain.order
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating domain: {e}")
            raise HTTPException(500, f"Failed to create domain: {str(e)}")
    
    @app.put("/polly/domains/{domain_id}")
    async def update_domain(domain_id: str, request: Dict[str, Any]):
        """
        Update an existing domain.
        
        Request: {
            "name": "Updated Name",
            "description": "Updated description",
            "color": "#ff6b6b",
            "icon": "🔧",
            "ragWeight": 0.25,
            "autoTagRules": ["updated", "keywords"]
        }
        
        Response: {
            "success": true,
            "domain": {...}
        }
        """
        try:
            from core.domain_config import load_domains, save_domains
            from datetime import datetime
            
            config = load_domains()
            
            # Find domain
            domain = next((d for d in config.domains if d.id == domain_id), None)
            if not domain:
                raise HTTPException(404, f"Domain '{domain_id}' not found")
            
            # Check if name is being changed to a duplicate
            new_name = request.get("name")
            if new_name and new_name != domain.name:
                if any(d.name == new_name for d in config.domains):
                    raise HTTPException(400, f"Domain with name '{new_name}' already exists")
            
            # Update fields
            if "name" in request:
                domain.name = request["name"]
            if "description" in request:
                domain.description = request["description"]
            if "color" in request:
                domain.color = request["color"]
            if "icon" in request:
                domain.icon = request["icon"]
            if "folderPath" in request:
                domain.folder_path = request["folderPath"]
            if "ragWeight" in request:
                domain.rag_weight = request["ragWeight"]
            if "autoTagRules" in request:
                domain.auto_tag_rules = request["autoTagRules"]
            
            domain.modified = datetime.now().isoformat()
            
            # Normalize RAG weights
            total_weight = sum(d.rag_weight for d in config.domains)
            if total_weight > 0:
                for d in config.domains:
                    d.rag_weight = d.rag_weight / total_weight
            
            # Save config
            save_domains(config)
            
            return {
                "success": True,
                "domain": {
                    "id": domain.id,
                    "name": domain.name,
                    "description": domain.description,
                    "color": domain.color,
                    "icon": domain.icon,
                    "folderPath": domain.folder_path,
                    "ragWeight": domain.rag_weight,
                    "autoTagRules": domain.auto_tag_rules,
                    "created": domain.created,
                    "modified": domain.modified,
                    "order": domain.order
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating domain: {e}")
            raise HTTPException(500, f"Failed to update domain: {str(e)}")
    
    @app.delete("/polly/domains/{domain_id}")
    async def delete_domain(domain_id: str):
        """
        Delete a domain.
        
        Safety checks:
        - Cannot delete if it's the only domain
        - Warns if domain has content (future enhancement)
        
        Response: {
            "success": true,
            "message": "Domain deleted",
            "remaining_count": 4
        }
        """
        try:
            from core.domain_config import load_domains, save_domains
            
            config = load_domains()
            
            # Check if domain exists
            domain = next((d for d in config.domains if d.id == domain_id), None)
            if not domain:
                raise HTTPException(404, f"Domain '{domain_id}' not found")
            
            # Safety check: cannot delete if it's the only domain
            if len(config.domains) <= 1:
                raise HTTPException(400, "Cannot delete the last domain")
            
            # Remove domain
            config.domains = [d for d in config.domains if d.id != domain_id]
            
            # Renumber orders
            for i, d in enumerate(sorted(config.domains, key=lambda x: x.order), 1):
                d.order = i
            
            # Normalize RAG weights
            total_weight = sum(d.rag_weight for d in config.domains)
            if total_weight > 0:
                for d in config.domains:
                    d.rag_weight = d.rag_weight / total_weight
            
            # Save config
            save_domains(config)
            
            return {
                "success": True,
                "message": f"Domain '{domain.name}' deleted",
                "remaining_count": len(config.domains)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting domain: {e}")
            raise HTTPException(500, f"Failed to delete domain: {str(e)}")
    
    @app.post("/polly/domains/reorder")
    async def reorder_domains(request: Dict[str, Any]):
        """
        Reorder domains.
        
        Request: {
            "domain_ids": ["sigils", "signals", "grids", "scrolls", "glyphs"]
        }
        
        Response: {
            "success": true,
            "domains": [...]
        }
        """
        try:
            from core.domain_config import load_domains, save_domains
            from datetime import datetime
            
            config = load_domains()
            
            domain_ids = request.get("domain_ids", [])
            
            # Validate that all IDs exist and count matches
            if len(domain_ids) != len(config.domains):
                raise HTTPException(400, "domain_ids must include all domains")
            
            for domain_id in domain_ids:
                if not any(d.id == domain_id for d in config.domains):
                    raise HTTPException(400, f"Domain '{domain_id}' not found")
            
            # Create a lookup dict
            domain_lookup = {d.id: d for d in config.domains}
            
            # Reorder domains and update order field
            config.domains = []
            for i, domain_id in enumerate(domain_ids, 1):
                domain = domain_lookup[domain_id]
                domain.order = i
                domain.modified = datetime.now().isoformat()
                config.domains.append(domain)
            
            # Update folder paths if numbering is enabled
            if config.folder_numbering:
                for i, domain in enumerate(config.domains, 1):
                    # Extract domain name from folder path (remove old number)
                    old_path = domain.folder_path
                    if old_path and '-' in old_path:
                        parts = old_path.split('-', 1)
                        if parts[0].isdigit():
                            domain_name = parts[1]
                        else:
                            domain_name = old_path
                    else:
                        domain_name = domain.name
                    
                    domain.folder_path = f"{i:02d}-{domain_name}"
            
            # Save config
            save_domains(config)
            
            return {
                "success": True,
                "domains": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "order": d.order,
                        "folderPath": d.folder_path
                    }
                    for d in config.domains
                ]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error reordering domains: {e}")
            raise HTTPException(500, f"Failed to reorder domains: {str(e)}")
    
    @app.post("/polly/domains/folder-numbering")
    async def toggle_folder_numbering(request: Dict[str, Any]):
        """
        Toggle folder numbering on/off.
        
        Request: {
            "enabled": true
        }
        
        Response: {
            "success": true,
            "folderNumbering": true,
            "updated_folders": [...]
        }
        """
        try:
            from core.domain_config import load_domains, save_domains
            from datetime import datetime
            
            config = load_domains()
            
            enabled = request.get("enabled")
            if enabled is None:
                raise HTTPException(400, "enabled field is required")
            
            config.folder_numbering = enabled
            
            # Update all folder paths based on new setting
            for i, domain in enumerate(config.domains, 1):
                # Extract domain name from folder path (remove old number if present)
                old_path = domain.folder_path
                if old_path and '-' in old_path:
                    parts = old_path.split('-', 1)
                    if parts[0].isdigit():
                        domain_name = parts[1]
                    else:
                        domain_name = old_path
                else:
                    domain_name = domain.name
                
                # Apply new numbering scheme
                if enabled:
                    domain.folder_path = f"{i:02d}-{domain_name}"
                else:
                    domain.folder_path = domain_name
                
                domain.modified = datetime.now().isoformat()
            
            # Save config
            save_domains(config)
            
            return {
                "success": True,
                "folderNumbering": config.folder_numbering,
                "updated_folders": [
                    {
                        "id": d.id,
                        "name": d.name,
                        "folderPath": d.folder_path
                    }
                    for d in config.domains
                ]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error toggling folder numbering: {e}")
            raise HTTPException(500, f"Failed to toggle folder numbering: {str(e)}")

    @app.post("/polly/domains/suggest-keywords")
    async def suggest_domain_keywords(request: Request):
        """
        Suggest keywords for a domain using LLM analysis.
        
        Request body:
        {
            "name": "Domain Name",
            "description": "Domain description (optional)",
            "existingKeywords": ["keyword1", "keyword2"]
        }
        
        Response:
        {
            "suggestedKeywords": [
                {"keyword": "pattern", "confidence": 0.9, "source": "llm"},
                {"keyword": "synthesis", "confidence": 0.7, "source": "llm"}
            ],
            "reasoning": "Explanation of suggestions"
        }
        """
        try:
            body = await request.json()
            domain_name = body.get("name", "")
            domain_description = body.get("description", "")
            existing_keywords = body.get("existingKeywords", [])
            
            if not domain_name:
                raise HTTPException(400, "Domain name is required")
            
            # Build prompt for LLM
            prompt = f"""Given a knowledge domain with the following information:

Domain Name: {domain_name}
{f"Description: {domain_description}" if domain_description else ""}
{f"Existing Keywords: {', '.join(existing_keywords)}" if existing_keywords else ""}

Suggest 10-15 relevant keywords that would help automatically classify content into this domain.

Requirements:
- Keywords should be specific concepts, technologies, or topics related to this domain
- Use lowercase, single words or short phrases (2-3 words max)
- Avoid generic terms like "work" or "project"
- Don't repeat existing keywords
- Consider: technical terms, tools, concepts, activities, and related topics

Return ONLY a JSON object in this exact format (no markdown, no code blocks):
{{
  "keywords": [
    {{"keyword": "example1", "confidence": 0.9}},
    {{"keyword": "example2", "confidence": 0.8}}
  ],
  "reasoning": "Brief explanation of why these keywords fit this domain"
}}"""

            # Use UnifiedLLM to get suggestions
            messages = [{"role": "user", "content": prompt}]
            
            # Call LLM with FAST tier (simple task)
            full_response = ""
            async for chunk in polly.llm.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            ):
                full_response += chunk
            
            # Parse JSON response
            # Remove markdown code blocks if present
            cleaned_response = full_response.strip()
            if cleaned_response.startswith("```"):
                # Extract JSON from code block
                lines = cleaned_response.split("\n")
                cleaned_response = "\n".join(
                    line for line in lines 
                    if not line.startswith("```")
                )
            
            try:
                result = json.loads(cleaned_response)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response: {cleaned_response}")
                raise HTTPException(500, "Failed to parse LLM response")
            
            # Convert to camelCase for frontend
            suggested_keywords = [
                {
                    "keyword": kw["keyword"],
                    "confidence": kw["confidence"],
                    "source": "llm"
                }
                for kw in result.get("keywords", [])
            ]
            
            return {
                "suggestedKeywords": suggested_keywords,
                "reasoning": result.get("reasoning", "")
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error suggesting keywords: {e}")
            raise HTTPException(500, f"Failed to suggest keywords: {str(e)}")

    # === First-Run Wizard Endpoints ===
    
    # Template definitions
    WIZARD_TEMPLATES = {
        "software-dev": {
            "name": "Software Development",
            "description": "For developers working on code projects",
            "domains": [
                {
                    "id": "code",
                    "name": "Code",
                    "description": "Software projects and technical work",
                    "color": "#61afef",
                    "icon": "💻",
                    "keywords": ["python", "javascript", "typescript", "rust", "git", "docker", "api", "database", "code", "programming"]
                },
                {
                    "id": "projects",
                    "name": "Projects",
                    "description": "Project management and task tracking",
                    "color": "#98c379",
                    "icon": "📊",
                    "keywords": ["project", "build", "deploy", "feature", "bug", "task", "sprint", "planning"]
                },
                {
                    "id": "learning",
                    "name": "Learning",
                    "description": "Technical learning and documentation",
                    "color": "#e5c07b",
                    "icon": "🎓",
                    "keywords": ["learn", "tutorial", "course", "documentation", "best-practice", "study", "guide"]
                }
            ]
        },
        "research": {
            "name": "Research / Academic",
            "description": "For researchers and academics",
            "domains": [
                {
                    "id": "research",
                    "name": "Research",
                    "description": "Research notes and literature review",
                    "color": "#c678dd",
                    "icon": "🔬",
                    "keywords": ["research", "paper", "study", "experiment", "data", "analysis", "hypothesis", "method"]
                },
                {
                    "id": "papers",
                    "name": "Papers",
                    "description": "Publications and writing",
                    "color": "#56b6c2",
                    "icon": "📄",
                    "keywords": ["paper", "publication", "journal", "citation", "reference", "review", "manuscript"]
                },
                {
                    "id": "experiments",
                    "name": "Experiments",
                    "description": "Experimental data and protocols",
                    "color": "#d19a66",
                    "icon": "🧪",
                    "keywords": ["experiment", "trial", "result", "observation", "protocol", "lab", "data"]
                }
            ]
        },
        "creative-writing": {
            "name": "Creative Writing",
            "description": "For writers and content creators",
            "domains": [
                {
                    "id": "ideas",
                    "name": "Ideas",
                    "description": "Brainstorming and concept development",
                    "color": "#e5c07b",
                    "icon": "💡",
                    "keywords": ["idea", "concept", "brainstorm", "inspiration", "sketch", "draft", "outline"]
                },
                {
                    "id": "drafts",
                    "name": "Drafts",
                    "description": "Works in progress",
                    "color": "#61afef",
                    "icon": "✍️",
                    "keywords": ["draft", "writing", "revision", "edit", "feedback", "story", "chapter"]
                },
                {
                    "id": "published",
                    "name": "Published",
                    "description": "Completed and published work",
                    "color": "#98c379",
                    "icon": "📚",
                    "keywords": ["published", "final", "release", "article", "blog", "complete"]
                }
            ]
        },
        "personal": {
            "name": "Personal Life",
            "description": "For organizing personal affairs",
            "domains": [
                {
                    "id": "personal",
                    "name": "Personal",
                    "description": "General personal notes and tasks",
                    "color": "#98c379",
                    "icon": "🏠",
                    "keywords": ["personal", "life", "family", "home", "todo", "routine", "daily"]
                },
                {
                    "id": "health",
                    "name": "Health",
                    "description": "Health and fitness tracking",
                    "color": "#e06c75",
                    "icon": "🏃",
                    "keywords": ["health", "fitness", "exercise", "nutrition", "wellness", "medical", "doctor"]
                },
                {
                    "id": "finance",
                    "name": "Finance",
                    "description": "Financial planning and tracking",
                    "color": "#e5c07b",
                    "icon": "💰",
                    "keywords": ["finance", "budget", "investment", "expense", "income", "savings", "money"]
                }
            ]
        },
        "student": {
            "name": "Academic Student",
            "description": "For students managing coursework",
            "domains": [
                {
                    "id": "courses",
                    "name": "Courses",
                    "description": "Course materials and lectures",
                    "color": "#61afef",
                    "icon": "📚",
                    "keywords": ["course", "class", "lecture", "assignment", "syllabus", "semester", "professor"]
                },
                {
                    "id": "notes",
                    "name": "Notes",
                    "description": "Study notes and summaries",
                    "color": "#98c379",
                    "icon": "📝",
                    "keywords": ["notes", "study", "exam", "review", "summary", "textbook", "reading"]
                },
                {
                    "id": "exams",
                    "name": "Exams",
                    "description": "Exam preparation and practice",
                    "color": "#e06c75",
                    "icon": "🎯",
                    "keywords": ["exam", "test", "quiz", "midterm", "final", "prep", "practice"]
                }
            ]
        },
        "polly-creator": {
            "name": "Polly Creator",
            "description": "The original 5-domain Polly system",
            "domains": [
                {
                    "id": "sigils",
                    "name": "Sigils",
                    "description": "Code, infrastructure, and technical systems",
                    "color": "#61afef",
                    "icon": "⚡",
                    "keywords": ["code", "programming", "infrastructure", "docker", "deployment", "server", "automation", "script", "python", "rust", "javascript"]
                },
                {
                    "id": "signals",
                    "name": "Signals",
                    "description": "Audio programming and synthesis",
                    "color": "#e06c75",
                    "icon": "📡",
                    "keywords": ["audio", "sound", "synthesis", "norns", "supercollider", "midi", "music", "dsp", "real-time"]
                },
                {
                    "id": "scrolls",
                    "name": "Scrolls",
                    "description": "Writing, pedagogy, and knowledge work",
                    "color": "#e5c07b",
                    "icon": "📜",
                    "keywords": ["writing", "essay", "pedagogy", "education", "freire", "teaching", "learning", "obsidian", "notes"]
                },
                {
                    "id": "glyphs",
                    "name": "Glyphs",
                    "description": "Visual design and UI/UX work",
                    "color": "#c678dd",
                    "icon": "✨",
                    "keywords": ["design", "ui", "ux", "visual", "interface", "typography", "layout", "aesthetic"]
                },
                {
                    "id": "grids",
                    "name": "Grids",
                    "description": "Systems thinking and mental models",
                    "color": "#56b6c2",
                    "icon": "🗂️",
                    "keywords": ["system", "pattern", "model", "structure", "framework", "constraint", "game", "synthesis"]
                }
            ]
        }
    }
    
    @app.post("/polly/domains/wizard/quick-start")
    async def wizard_quick_start():
        """
        Create default 3-domain configuration for quick start.
        Creates: Work, Personal, Learning domains.
        
        Response:
        {
            "success": true,
            "config": { ... full domain config ... }
        }
        """
        try:
            from core.domain_config import Domain, DomainsConfig, save_domains
            from datetime import datetime
            
            # Check if config already exists
            config_path = Path.home() / ".polly" / "domains.json"
            if config_path.exists():
                raise HTTPException(400, "Domain configuration already exists")
            
            # Create 3 default domains
            now = datetime.now().isoformat()
            
            domains = [
                Domain(
                    id="work",
                    name="Work",
                    description="Professional projects, tasks, and career development",
                    color="#61afef",  # Blue
                    icon="📊",
                    folder_path="01-Work",
                    rag_weight=0.33,
                    auto_tag_rules=["project", "task", "meeting", "deadline", "client", "work", "job", "career"],
                    created=now,
                    modified=now,
                    order=1
                ),
                Domain(
                    id="personal",
                    name="Personal",
                    description="Personal life, health, hobbies, and home management",
                    color="#98c379",  # Green
                    icon="🏠",
                    folder_path="02-Personal",
                    rag_weight=0.33,
                    auto_tag_rules=["personal", "life", "family", "health", "finance", "hobby", "todo", "home"],
                    created=now,
                    modified=now,
                    order=2
                ),
                Domain(
                    id="learning",
                    name="Learning",
                    description="Education, courses, tutorials, and knowledge acquisition",
                    color="#e5c07b",  # Yellow
                    icon="🎓",
                    folder_path="03-Learning",
                    rag_weight=0.34,
                    auto_tag_rules=["learn", "study", "course", "tutorial", "book", "research", "knowledge", "education"],
                    created=now,
                    modified=now,
                    order=3
                )
            ]
            
            # Create config
            config = DomainsConfig(
                version="1.0",
                folder_numbering=True,
                domains=domains,
                last_modified=now
            )
            
            # Save config
            save_domains(config)
            
            logger.info(f"Quick start: Created {len(domains)} default domains")
            
            # Return config in API format
            return {
                "success": True,
                "config": {
                    "version": config.version,
                    "folderNumbering": config.folder_numbering,
                    "domains": [
                        {
                            "id": d.id,
                            "name": d.name,
                            "description": d.description,
                            "color": d.color,
                            "icon": d.icon,
                            "folderPath": d.folder_path,
                            "ragWeight": d.rag_weight,
                            "autoTagRules": d.auto_tag_rules,
                            "created": d.created,
                            "modified": d.modified,
                            "order": d.order
                        }
                        for d in config.domains
                    ],
                    "lastModified": config.last_modified
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in quick start: {e}")
            raise HTTPException(500, f"Failed to create quick start configuration: {str(e)}")
    
    @app.get("/polly/domains/wizard/templates")
    async def wizard_list_templates():
        """
        List available domain templates.
        
        Response:
        {
            "templates": [
                {
                    "id": "software-dev",
                    "name": "Software Development",
                    "description": "For developers working on code projects",
                    "domainCount": 3
                },
                ...
            ]
        }
        """
        try:
            templates = [
                {
                    "id": template_id,
                    "name": template_data["name"],
                    "description": template_data["description"],
                    "domainCount": len(template_data["domains"])
                }
                for template_id, template_data in WIZARD_TEMPLATES.items()
            ]
            
            return {"templates": templates}
            
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            raise HTTPException(500, f"Failed to list templates: {str(e)}")
    
    @app.post("/polly/domains/wizard/from-template")
    async def wizard_from_template(request: Request):
        """
        Create domains from a template.
        
        Request body:
        {
            "templateId": "software-dev"
        }
        
        Response:
        {
            "success": true,
            "config": { ... full domain config ... }
        }
        """
        try:
            from core.domain_config import Domain, DomainsConfig, save_domains
            from datetime import datetime
            
            body = await request.json()
            template_id = body.get("templateId")
            
            if not template_id:
                raise HTTPException(400, "templateId is required")
            
            if template_id not in WIZARD_TEMPLATES:
                raise HTTPException(404, f"Template '{template_id}' not found")
            
            # Check if config already exists
            config_path = Path.home() / ".polly" / "domains.json"
            if config_path.exists():
                raise HTTPException(400, "Domain configuration already exists")
            
            template = WIZARD_TEMPLATES[template_id]
            now = datetime.now().isoformat()
            
            # Create domains from template
            domains = []
            total_domains = len(template["domains"])
            weight_per_domain = 1.0 / total_domains
            
            for i, domain_template in enumerate(template["domains"], 1):
                # Generate folder path with numbering
                folder_path = f"{i:02d}-{domain_template['name']}"
                
                domain = Domain(
                    id=domain_template["id"],
                    name=domain_template["name"],
                    description=domain_template["description"],
                    color=domain_template["color"],
                    icon=domain_template["icon"],
                    folder_path=folder_path,
                    rag_weight=weight_per_domain,
                    auto_tag_rules=domain_template["keywords"],
                    created=now,
                    modified=now,
                    order=i
                )
                domains.append(domain)
            
            # Create config
            config = DomainsConfig(
                version="1.0",
                folder_numbering=True,
                domains=domains,
                last_modified=now
            )
            
            # Save config
            save_domains(config)
            
            logger.info(f"From template '{template_id}': Created {len(domains)} domains")
            
            # Return config in API format
            return {
                "success": True,
                "config": {
                    "version": config.version,
                    "folderNumbering": config.folder_numbering,
                    "domains": [
                        {
                            "id": d.id,
                            "name": d.name,
                            "description": d.description,
                            "color": d.color,
                            "icon": d.icon,
                            "folderPath": d.folder_path,
                            "ragWeight": d.rag_weight,
                            "autoTagRules": d.auto_tag_rules,
                            "created": d.created,
                            "modified": d.modified,
                            "order": d.order
                        }
                        for d in config.domains
                    ],
                    "lastModified": config.last_modified
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating from template: {e}")
            raise HTTPException(500, f"Failed to create from template: {str(e)}")
    
    # ============================================
    # Knowledge Base Configuration Endpoints
    # ============================================
    
    @app.get("/polly/config/knowledge-base-path")
    async def get_knowledge_base_path():
        """
        Get the current knowledge base directory path.
        
        Response:
        {
            "path": "/Users/username/Dropbox/Polly",
            "exists": true,
            "isDefault": false
        }
        """
        try:
            from core.config import get_config
            
            config = get_config()
            kb_path = config.knowledge_base_path
            
            return {
                "path": str(kb_path),
                "exists": kb_path.exists(),
                "isDefault": kb_path == Path.home() / ".polly"
            }
            
        except Exception as e:
            logger.error(f"Error getting knowledge base path: {e}")
            raise HTTPException(500, f"Failed to get knowledge base path: {str(e)}")
    
    @app.post("/polly/config/knowledge-base-path")
    async def set_knowledge_base_path(request: Request):
        """
        Set the knowledge base directory path.
        
        Request body:
        {
            "path": "/Users/username/Dropbox/Polly"
        }
        
        Response:
        {
            "success": true,
            "path": "/Users/username/Dropbox/Polly"
        }
        """
        try:
            from core.config import get_config
            
            body = await request.json()
            new_path = body.get("path")
            
            if not new_path:
                raise HTTPException(400, "path is required")
            
            config = get_config()
            success = config.set_knowledge_base_path(new_path)
            
            if not success:
                raise HTTPException(400, "Invalid path: Directory is not writable or cannot be created")
            
            return {
                "success": True,
                "path": str(config.knowledge_base_path)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error setting knowledge base path: {e}")
            raise HTTPException(500, f"Failed to set knowledge base path: {str(e)}")
    
    @app.get("/polly/config/cloud-services")
    async def detect_cloud_services():
        """
        Detect available cloud storage services on the system.
        
        Response:
        {
            "services": [
                {
                    "name": "Dropbox",
                    "path": "/Users/username/Dropbox",
                    "available": true
                },
                ...
            ]
        }
        """
        try:
            from core.config import get_config
            
            config = get_config()
            detected = config.detect_cloud_services()
            
            services = [
                {
                    "name": name,
                    "path": str(path) if path else None,
                    "available": path is not None,
                    "suggestedPath": str(path / "Polly") if path else None
                }
                for name, path in detected.items()
            ]
            
            return {"services": services}
            
        except Exception as e:
            logger.error(f"Error detecting cloud services: {e}")
            raise HTTPException(500, f"Failed to detect cloud services: {str(e)}")
    
    @app.post("/polly/config/migrate-knowledge-base")
    async def migrate_knowledge_base_endpoint(request: Request):
        """
        Migrate knowledge base to a new location.
        
        Request body:
        {
            "targetPath": "/Users/username/Dropbox/Polly",
            "createBackup": true
        }
        
        Response:
        {
            "success": true,
            "sourcePath": "...",
            "targetPath": "...",
            "backupPath": "...",
            "stats": {...},
            "filesMigrated": 108,
            "bytesMigrated": 524288
        }
        """
        try:
            from core.config import get_config
            from core.knowledge_base_migration import migrate_knowledge_base, MigrationError
            
            body = await request.json()
            target_path = body.get("targetPath")
            create_backup = body.get("createBackup", True)
            
            if not target_path:
                raise HTTPException(400, "targetPath is required")
            
            # Get current knowledge base path
            config = get_config()
            source_path = config.knowledge_base_path
            
            # Perform migration
            try:
                result = migrate_knowledge_base(
                    source=source_path,
                    target=target_path,
                    create_backup=create_backup
                )
                
                # Update config to point to new location
                config.set_knowledge_base_path(target_path)
                
                return {
                    "success": result["success"],
                    "sourcePath": result["source_path"],
                    "targetPath": result["target_path"],
                    "backupPath": result["backup_path"],
                    "stats": result["stats"],
                    "filesMigrated": result["files_migrated"],
                    "bytesMigrated": result["bytes_migrated"]
                }
                
            except MigrationError as e:
                raise HTTPException(400, str(e))
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error migrating knowledge base: {e}")
            raise HTTPException(500, f"Failed to migrate knowledge base: {str(e)}")
    
    @app.get("/polly/config/migration-preview")
    async def get_migration_preview():
        """
        Get preview of what would be migrated.
        
        Response:
        {
            "sourcePath": "...",
            "stats": {
                "notes": {"count": 108, "sizeBytes": 262144},
                "conversations": {"count": 0, "sizeBytes": 0},
                "attachments": {"count": 0, "sizeBytes": 0},
                "other": {"count": 5, "sizeBytes": 12288},
                "totalFiles": 113,
                "totalSizeBytes": 274432
            }
        }
        """
        try:
            from core.config import get_config
            from core.knowledge_base_migration import KnowledgeBaseMigrator
            
            config = get_config()
            source_path = config.knowledge_base_path
            
            # Create a temporary migrator just to get stats
            # Use a dummy target since we're just previewing
            migrator = KnowledgeBaseMigrator(source_path, source_path.parent / "temp")
            stats = migrator.get_migration_stats()
            
            return {
                "sourcePath": str(source_path),
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting migration preview: {e}")
            raise HTTPException(500, f"Failed to get migration preview: {str(e)}")
    
    # ============================================================================
    # API Keys & Budget Management Endpoints
    # ============================================================================
    
    @app.get("/api/settings/keys")
    async def get_api_keys():
        """
        Get list of all API keys with their status.
        
        Response:
        {
            "keys": [
                {
                    "provider": "anthropic",
                    "key_name": "ANTHROPIC_API_KEY",
                    "description": "Anthropic Claude API Key",
                    "is_set": true,
                    "storage_type": "environment",
                    "created_at": "2024-01-01T00:00:00",
                    "last_accessed": "2024-01-01T00:00:00"
                },
                ...
            ]
        }
        """
        try:
            from core.secrets_manager import get_secrets_manager
            
            secrets_manager = get_secrets_manager()
            keys = secrets_manager.list_secrets()
            
            return {"keys": keys}
            
        except Exception as e:
            logger.error(f"Error listing API keys: {e}")
            raise HTTPException(500, f"Failed to list API keys: {str(e)}")
    
    @app.get("/api/settings/budget")
    async def get_budget_status_endpoint():
        """
        Get current budget usage and limits.
        
        Response:
        {
            "limits": {
                "daily": 10.00,
                "monthly": 100.00
            },
            "daily": {
                "spent": 2.45,
                "percentage": 24.5
            },
            "monthly": {
                "spent": 15.30,
                "percentage": 15.3
            },
            "total_cost": 15.30,
            "total_requests": 142,
            "total_tokens": 45230
        }
        """
        try:
            if not polly or not hasattr(polly, 'budget_manager') or not polly.budget_manager:
                return {
                    "limits": {"daily": 10.0, "monthly": 100.0},
                    "daily": {"spent": 0.0, "percentage": 0.0},
                    "monthly": {"spent": 0.0, "percentage": 0.0},
                    "total_cost": 0.0,
                    "total_requests": 0,
                    "total_tokens": 0
                }
            
            budget_manager = polly.budget_manager
            
            # Get budget status (has daily/monthly with spent, limit, percent_used)
            budget_status = await budget_manager.get_budget_status()
            
            # Get spending summary for total stats
            spending_summary = await budget_manager.get_spending_summary()
            
            total_tokens = spending_summary.total_tokens_in + spending_summary.total_tokens_out
            
            return {
                "limits": {
                    "daily": budget_status['daily']['limit'],
                    "monthly": budget_status['monthly']['limit']
                },
                "daily": {
                    "spent": budget_status['daily']['spent'],
                    "percentage": budget_status['daily']['percent_used']
                },
                "monthly": {
                    "spent": budget_status['monthly']['spent'],
                    "percentage": budget_status['monthly']['percent_used']
                },
                "total_cost": spending_summary.total_cost,
                "total_requests": spending_summary.total_requests,
                "total_tokens": total_tokens
            }
            
        except Exception as e:
            logger.error(f"Error getting budget status: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get budget status: {str(e)}")
    
    # ===== Curriculum Learning System Endpoints (Phase 23) =====
    
    @app.get("/polly/curricula/list")
    async def list_curricula(status: Optional[str] = None):
        """
        List all curricula, optionally filtered by status.
        
        Query params:
            status: Filter by status (active, draft, completed, paused)
        
        Response:
        {
            "curricula": [
                {
                    "id": "react-mastery",
                    "title": "React Mastery",
                    "status": "active",
                    "completion_percentage": 25.0,
                    "current_section": "week-2.1",
                    "total_sections": 16,
                    "completed_sections": 4,
                    "created": "2026-02-01T10:00:00"
                },
                ...
            ]
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                return {"curricula": []}
            
            curricula = polly.curriculum_manager.list_curricula(status=status)
            
            return {
                "curricula": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "status": c.status,
                        "completion_percentage": c.completion_percentage,
                        "current_section": c.current_section_id,
                        "total_sections": c.total_sections,
                        "completed_sections": c.completed_sections,
                        "created": c.created.isoformat(),
                        "last_updated": c.last_updated.isoformat(),
                        "estimated_duration": c.estimated_duration,
                        "goal": c.goal
                    }
                    for c in curricula
                ]
            }
        except Exception as e:
            logger.error(f"Error listing curricula: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to list curricula: {str(e)}")
    
    @app.get("/polly/curricula/{curriculum_id}")
    async def get_curriculum(curriculum_id: str):
        """
        Get full curriculum details including all sections.
        
        Response:
        {
            "id": "react-mastery",
            "title": "React Mastery",
            "status": "active",
            "goal": "Master React development",
            "sections": [...],
            ...
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(404, "Curriculum manager not available")
            
            curriculum = polly.curriculum_manager.get_curriculum(curriculum_id)
            if not curriculum:
                raise HTTPException(404, f"Curriculum not found: {curriculum_id}")
            
            return curriculum.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting curriculum {curriculum_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get curriculum: {str(e)}")
    
    @app.post("/polly/curricula/create")
    async def create_curriculum(request: Request):
        """
        Create new curriculum.
        
        Request body:
        {
            "title": "React Mastery",
            "goal": "Master React development",
            "sections": [
                {
                    "id": "week-1.1",
                    "title": "React Basics",
                    "type": "lesson",
                    "order": 1,
                    "parent_id": "week-1",
                    "description": "...",
                    "concepts": ["components", "jsx"],
                    "estimated_time": "2 hours"
                },
                ...
            ],
            "current_level": "Intermediate JavaScript",
            "estimated_duration": "8 weeks",
            "template_id": "framework-library"
        }
        
        Response:
        {
            "status": "success",
            "curriculum_id": "react-mastery"
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            body = await request.json()
            
            curriculum = polly.curriculum_manager.create_curriculum(
                title=body['title'],
                goal=body['goal'],
                sections=body['sections'],
                current_level=body.get('current_level', ''),
                estimated_duration=body.get('estimated_duration', ''),
                template_id=body.get('template_id')
            )
            
            return {
                "status": "success",
                "curriculum_id": curriculum.id,
                "curriculum": curriculum.to_dict()
            }
        except KeyError as e:
            raise HTTPException(400, f"Missing required field: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating curriculum: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to create curriculum: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/activate")
    async def activate_curriculum(curriculum_id: str):
        """
        Activate curriculum (change status from draft to active).
        
        Response:
        {
            "status": "success",
            "curriculum": {...}
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            curriculum = polly.curriculum_manager.activate_curriculum(curriculum_id)
            
            return {
                "status": "success",
                "curriculum": curriculum.to_dict()
            }
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error activating curriculum {curriculum_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to activate curriculum: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/pause")
    async def pause_curriculum(curriculum_id: str):
        """Pause active curriculum."""
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            polly.curriculum_manager.pause_curriculum(curriculum_id)
            
            return {"status": "success"}
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error pausing curriculum {curriculum_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to pause curriculum: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/complete")
    async def complete_curriculum_endpoint(curriculum_id: str):
        """Mark curriculum as completed."""
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            polly.curriculum_manager.complete_curriculum(curriculum_id)
            
            return {"status": "success"}
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error completing curriculum {curriculum_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to complete curriculum: {str(e)}")
    
    @app.delete("/polly/curricula/{curriculum_id}")
    async def delete_curriculum(curriculum_id: str):
        """Delete curriculum."""
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            polly.curriculum_manager.delete_curriculum(curriculum_id)
            
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Error deleting curriculum {curriculum_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to delete curriculum: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/sections/{section_id}/start")
    async def start_section(curriculum_id: str, section_id: str):
        """
        Start working on a section.
        
        Response:
        {
            "status": "success",
            "section": {...}
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            section = polly.curriculum_manager.start_section(curriculum_id, section_id)
            
            return {
                "status": "success",
                "section": section.to_dict()
            }
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error starting section {curriculum_id}/{section_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to start section: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/sections/{section_id}/complete")
    async def complete_section(curriculum_id: str, section_id: str, request: Request):
        """
        Complete a section with reflection.
        
        Request body:
        {
            "mastery_level": 3,
            "notes": ["path/to/note.md"],
            "struggles": ["Understanding state management"],
            "breakthroughs": ["Aha! Props flow down, events flow up"]
        }
        
        Response:
        {
            "status": "success"
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            body = await request.json()
            
            polly.curriculum_manager.complete_section(
                curriculum_id=curriculum_id,
                section_id=section_id,
                mastery_level=body.get('mastery_level', 3),
                notes=body.get('notes'),
                struggles=body.get('struggles'),
                breakthroughs=body.get('breakthroughs')
            )
            
            return {"status": "success"}
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error completing section {curriculum_id}/{section_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to complete section: {str(e)}")
    
    @app.get("/polly/curricula/{curriculum_id}/progress")
    async def get_curriculum_progress(curriculum_id: str):
        """
        Get progress summary for curriculum.
        
        Response:
        {
            "curriculum_id": "react-mastery",
            "title": "React Mastery",
            "status": "active",
            "total_sections": 16,
            "completed_sections": 4,
            "completion_percentage": 25.0,
            "total_time_minutes": 480,
            "total_time_hours": 8.0,
            "mastery_average": 3.5,
            "current_section_id": "week-2.1",
            "next_section": "week-2.2"
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            progress = polly.curriculum_manager.get_progress_summary(curriculum_id)
            if not progress:
                raise HTTPException(404, f"Curriculum not found: {curriculum_id}")
            
            return progress
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting progress for {curriculum_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get progress: {str(e)}")
    
    # Phase 23.5: Security Hardening - Capability Broker + Package Approval Endpoints
    
    @app.get("/polly/capabilities/pending")
    async def get_pending_approvals():
        """
        Get all pending capability approval requests.
        
        Response:
        {
            "approvals": [
                {
                    "approval_id": "approval_123",
                    "capability_type": "package_install",
                    "requestor": "professor-persona",
                    "resource": "numpy",
                    "metadata": {...}
                }
            ]
        }
        """
        try:
            from core.capability_broker import get_capability_broker
            broker = get_capability_broker()
            
            # Get pending approvals with their IDs
            approvals = []
            for approval_id, req in broker.pending_approvals.items():
                approvals.append({
                    "approval_id": approval_id,
                    "capability_type": req.capability_type.value,
                    "requestor": req.requestor,
                    "resource": req.resource,
                    "metadata": req.metadata,
                    "timestamp": req.timestamp.isoformat()
                })
            
            return {"approvals": approvals}
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get pending approvals: {str(e)}")
    
    @app.post("/polly/capabilities/approve/{approval_id}")
    async def approve_capability(approval_id: str, request: Request):
        """
        Approve a pending capability request.
        
        Request body:
        {
            "permanent": true,  // Add to allowlist if True
            "expires_in_minutes": 60  // Optional expiration
        }
        
        Response:
        {
            "status": "success",
            "grant_id": "grant_123",
            "message": "Capability granted"
        }
        """
        try:
            from core.capability_broker import get_capability_broker
            broker = get_capability_broker()
            
            body = await request.json()
            permanent = body.get("permanent", False)
            expires_in_minutes = body.get("expires_in_minutes")
            
            grant = broker.grant_capability(
                approval_id=approval_id,
                permanent=permanent,
                expires_in_minutes=expires_in_minutes
            )
            
            # If permanent and package_install, add to allowlist
            if permanent and grant.request.capability_type.value == "package_install":
                # Add to approved packages
                from core.package_detector import get_package_detector
                detector = get_package_detector()
                # This will be handled by the package approval endpoint
                # For now, just log it
            
            return {
                "status": "success",
                "grant_id": grant.grant_id,
                "message": "Capability granted"
            }
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error approving capability: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to approve capability: {str(e)}")
    
    @app.post("/polly/capabilities/deny/{approval_id}")
    async def deny_capability(approval_id: str, request: Request):
        """
        Deny a pending capability request.
        
        Request body:
        {
            "reason": "Optional reason for denial"
        }
        
        Response:
        {
            "status": "success",
            "message": "Capability denied"
        }
        """
        try:
            from core.capability_broker import get_capability_broker
            broker = get_capability_broker()
            
            body = await request.json()
            reason = body.get("reason")
            
            broker.deny_capability(approval_id, reason=reason)
            
            return {
                "status": "success",
                "message": "Capability denied"
            }
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error denying capability: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to deny capability: {str(e)}")
    
    @app.get("/polly/packages/metadata/{package_name}")
    async def get_package_metadata(package_name: str):
        """
        Get metadata for a package (PyPI + Context7).
        
        Used in package approval workflow to show users information
        about packages before they approve installation.
        
        Response:
        {
            "name": "numpy",
            "description": "Fundamental package for array computing",
            "version": "1.24.0",
            "author": "NumPy Developers",
            "homepage": "https://numpy.org",
            "context7_trust_score": 0.95,
            "context7_info": {...},
            "pypi_info": {...}
        }
        """
        try:
            from core.package_metadata import get_package_metadata_fetcher
            fetcher = await get_package_metadata_fetcher()
            metadata = await fetcher.fetch_metadata(package_name)
            return metadata.to_dict()
        except Exception as e:
            logger.error(f"Error fetching metadata for {package_name}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to fetch package metadata: {str(e)}")
    
    @app.post("/polly/packages/approve")
    async def approve_packages(request: Request):
        """
        Approve packages for installation.
        
        Adds packages to approved_packages.yaml allowlist.
        
        Request body:
        {
            "packages": ["numpy", "pandas"],
            "permanent": true  // If true, add to allowlist. If false, one-time approval.
        }
        
        Response:
        {
            "status": "success",
            "approved": ["numpy", "pandas"],
            "message": "Packages approved"
        }
        """
        try:
            from core.package_detector import get_package_detector
            from pathlib import Path
            import yaml
            
            body = await request.json()
            packages = body.get("packages", [])
            permanent = body.get("permanent", True)
            
            if not packages:
                raise HTTPException(400, "No packages specified")
            
            detector = get_package_detector()
            
            # Load current allowlist
            allowlist_path = detector.allowlist_path
            if not allowlist_path.exists():
                # Create default allowlist file
                allowlist_path.parent.mkdir(parents=True, exist_ok=True)
                config = {
                    "approved_packages": [],
                    "blocked_packages": [],
                    "stdlib_modules": list(detector.STDLIB_MODULES)
                }
            else:
                with open(allowlist_path) as f:
                    config = yaml.safe_load(f) or {}
            
            # Add packages to approved list
            approved_list = config.get("approved_packages", [])
            for pkg in packages:
                pkg_lower = pkg.lower()
                if pkg_lower not in approved_list:
                    approved_list.append(pkg_lower)
            
            config["approved_packages"] = approved_list
            
            # Save allowlist
            with open(allowlist_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Reload detector to pick up changes
            detector._load_allowlist()
            
            logger.info(f"Approved packages: {packages} (permanent: {permanent})")
            
            return {
                "status": "success",
                "approved": packages,
                "message": f"{len(packages)} package(s) approved"
            }
        except Exception as e:
            logger.error(f"Error approving packages: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to approve packages: {str(e)}")
    
    @app.post("/polly/packages/block")
    async def block_packages(request: Request):
        """
        Block packages from being used.
        
        Adds packages to blocked_packages list in approved_packages.yaml.
        
        Request body:
        {
            "packages": ["malicious-package"]
        }
        
        Response:
        {
            "status": "success",
            "blocked": ["malicious-package"]
        }
        """
        try:
            from core.package_detector import get_package_detector
            from pathlib import Path
            import yaml
            
            body = await request.json()
            packages = body.get("packages", [])
            
            if not packages:
                raise HTTPException(400, "No packages specified")
            
            detector = get_package_detector()
            
            # Load current allowlist
            allowlist_path = detector.allowlist_path
            if not allowlist_path.exists():
                allowlist_path.parent.mkdir(parents=True, exist_ok=True)
                config = {
                    "approved_packages": [],
                    "blocked_packages": [],
                    "stdlib_modules": list(detector.STDLIB_MODULES)
                }
            else:
                with open(allowlist_path) as f:
                    config = yaml.safe_load(f) or {}
            
            # Add packages to blocked list
            blocked_list = config.get("blocked_packages", [])
            for pkg in packages:
                pkg_lower = pkg.lower()
                if pkg_lower not in blocked_list:
                    blocked_list.append(pkg_lower)
                # Remove from approved if present
                approved_list = config.get("approved_packages", [])
                if pkg_lower in approved_list:
                    approved_list.remove(pkg_lower)
            
            config["blocked_packages"] = blocked_list
            config["approved_packages"] = approved_list
            
            # Save allowlist
            with open(allowlist_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # Reload detector
            detector._load_allowlist()
            
            logger.info(f"Blocked packages: {packages}")
            
            return {
                "status": "success",
                "blocked": packages,
                "message": f"{len(packages)} package(s) blocked"
            }
        except Exception as e:
            logger.error(f"Error blocking packages: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to block packages: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/sections/{section_id}/enrich")
    async def enrich_section(curriculum_id: str, section_id: str):
        """
        Enrich section with detailed materials (diagrams, examples, exercises).
        Note: This endpoint is a placeholder for Phase 4.
        Actual enrichment will use Professor persona to generate content.
        
        Response:
        {
            "status": "success" | "already_enriched",
            "enrichment": {...}
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            # Check if already enriched
            if polly.curriculum_manager.is_section_enriched(curriculum_id, section_id):
                section = polly.curriculum_manager.get_section(curriculum_id, section_id)
                logger.info(f"Section {section_id} already enriched, returning cached data")
                return {
                    "status": "already_enriched",
                    "enrichment": {
                        "explanation": section.explanation,
                        "diagrams": section.diagrams,
                        "examples": section.examples,
                        "exercises": section.exercises,
                        "resources": section.resources,
                        "assessment_criteria": section.assessment_criteria
                    }
                }
            
            # Get section data
            section = polly.curriculum_manager.get_section(curriculum_id, section_id)
            if not section:
                raise HTTPException(404, f"Section {section_id} not found")
            
            # Convert section to dict for Professor
            section_data = {
                "title": section.title,
                "description": section.description or "",
                "concepts": section.concepts or [],
                "estimated_time": section.estimated_time or ""
            }
            
            # Get Professor persona from cache or create it
            professor = None
            if hasattr(polly, 'persona_manager') and polly.persona_manager:
                # Check if professor is in cache
                if 'professor' in polly.persona_manager._persona_cache:
                    professor = polly.persona_manager._persona_cache['professor']
                else:
                    # Create professor instance if not cached
                    from core.personas.implementations.professor import ProfessorPersona
                    # Use router_v2 if available, otherwise fall back to router (v1)
                    router = polly.router_v2 if hasattr(polly, 'router_v2') else polly.router
                    professor = ProfessorPersona(
                        name='professor',
                        router=router,
                        skill_manager=polly.skill_manager,
                        rag=polly.rag,
                        learning_tracker=polly.learning_tracker if hasattr(polly, 'learning_tracker') else None,
                        curriculum_manager=polly.curriculum_manager,
                        template_manager=polly.template_manager if hasattr(polly, 'template_manager') else None,
                        domain_engine=polly.domains if hasattr(polly, 'domains') else None
                    )
                    # Cache it for future use
                    polly.persona_manager._persona_cache['professor'] = professor
            
            if not professor:
                raise HTTPException(500, "Professor persona not available")
            
            # Call Professor.enrich_section()
            logger.info(f"Calling Professor.enrich_section() for {curriculum_id}/{section_id}")
            enrichment_result = await professor.enrich_section(
                curriculum_id=curriculum_id,
                section_id=section_id,
                section_data=section_data
            )
            
            if enrichment_result.get("status") != "success":
                error_msg = enrichment_result.get("error", "Unknown error")
                raise HTTPException(500, f"Enrichment failed: {error_msg}")
            
            enrichment = enrichment_result.get("enrichment", {})
            
            # Phase 23.5: Check for unapproved packages and route through capability broker
            if "package_detection" in enrichment:
                package_detection = enrichment["package_detection"]
                unapproved = package_detection.get("unapproved_packages", [])
                
                if unapproved:
                    from core.capability_broker import get_capability_broker
                    from core.capabilities.types import CapabilityType
                    
                    broker = get_capability_broker()
                    pending_approvals = []
                    
                    # Request capability for each unapproved package
                    for package_name in unapproved:
                        response = broker.request_capability(
                            capability_type=CapabilityType.PACKAGE_INSTALL,
                            requestor="professor-persona",
                            resource=package_name,
                            metadata={
                                "curriculum_id": curriculum_id,
                                "section_id": section_id,
                                "source": "enrichment"
                            }
                        )
                        
                        if response.requires_approval and response.approval_id:
                            pending_approvals.append({
                                "approval_id": response.approval_id,
                                "package_name": package_name
                            })
                    
                    # Add pending approvals to enrichment response
                    if pending_approvals:
                        enrichment["pending_approvals"] = pending_approvals
                        logger.info(f"Section enrichment requires {len(pending_approvals)} package approvals")
            
            # Save enrichment to curriculum
            polly.curriculum_manager.enrich_section(
                curriculum_id=curriculum_id,
                section_id=section_id,
                enrichment_data=enrichment
            )
            
            logger.info(f"Section {section_id} enriched successfully")
            
            return {
                "status": "success",
                "enrichment": enrichment
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error enriching section {curriculum_id}/{section_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to enrich section: {str(e)}")
    
    @app.post("/polly/exercises/execute")
    async def execute_exercise_code(request: Request):
        """
        Execute Python code in a sandboxed Pyodide environment.
        
        Phase 23.5: Security Hardening - Code execution now uses Pyodide sandbox
        instead of subprocess for security isolation.
        
        Request body:
        {
            "code": "print('Hello World')",
            "timeout": 5
        }
        
        Response:
        {
            "status": "success" | "error" | "timeout",
            "output": "Hello World\n",
            "error": "Error message if status is error",
            "execution_time": 0.123
        }
        
        Note: Actual execution happens in Electron renderer process using Pyodide.
        This endpoint validates the request and returns the execution result.
        """
        try:
            # Phase 23.5: Security Hardening - Use Pyodide sandbox
            from core.sandbox import PyodideSandbox
            
            body = await request.json()
            code = body.get('code', '')
            timeout = body.get('timeout', None)  # Use sandbox default if not provided
            
            if not code:
                raise HTTPException(400, "Code is required")
            
            # Initialize sandbox
            sandbox = PyodideSandbox()
            
            # Validate code
            is_valid, error_msg = sandbox.validate_code(code)
            if not is_valid:
                return {
                    "status": "error",
                    "error": error_msg or "Code validation failed",
                    "execution_time": 0.0
                }
            
            # Phase 23.5: Execution happens client-side in Pyodide sandbox
            # This endpoint validates the request and can log execution results for audit.
            # The frontend executes code directly in Pyodide and may send results here for logging.
            
            # Check if this is an audit log request (execution already happened client-side)
            executed_locally = body.get('executed_locally', False)
            result_status = body.get('result_status')
            
            if executed_locally:
                # This is an audit log - just log it
                logger.info(f"Code execution audit: code_length={len(code)}, status={result_status}, executed_in_pyodide=True")
                return {
                    "status": "logged",
                    "message": "Execution logged for audit"
                }
            
            # Otherwise, this is a validation request
            logger.info(f"Code execution request validated: code_length={len(code)}, timeout={timeout}")
            
            # Return validation result - frontend should execute in Pyodide
            return {
                "status": "validated",
                "message": "Code validated. Execute in Electron renderer using Pyodide.",
                "sandbox_info": sandbox.get_sandbox_info()
            }
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing execution request: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to process execution request: {str(e)}")
    
    @app.post("/polly/exercises/validate")
    async def validate_exercise_solution(request: Request):
        print("▶▶▶ VALIDATE FUNCTION CALLED ▶▶▶", flush=True)
        """
        Validate exercise solution and get feedback from Professor.
        
        Request body:
        {
            "curriculum_id": "python-learning-curriculum",
            "section_id": "week-1.2",
            "exercise_id": "ex_1_variable_assignment",
            "code": "name = 'Alice'\\nage = 25\\n...",
            "output": "My name is Alice..."
        }
        
        Response:
        {
            "status": "success",
            "validation": {
                "correct": true | false,
                "feedback": "Great job! Your solution...",
                "hints": ["Consider using f-strings", ...],
                "passed_criteria": ["Variable assignment correct", ...],
                "failed_criteria": ["Output formatting needs improvement", ...]
            }
        }
        """
        try:
            polly = get_polly()
            if not polly:
                raise HTTPException(500, "Polly not initialized")
            
            body = await request.json()
            curriculum_id = body.get('curriculum_id')
            section_id = body.get('section_id')
            exercise_id = body.get('exercise_id')
            code = body.get('code', '')
            output = body.get('output', '')
            
            if not all([curriculum_id, section_id, exercise_id]):
                raise HTTPException(400, "curriculum_id, section_id, and exercise_id are required")
            
            # Get curriculum and section
            if not hasattr(polly, 'curriculum_manager'):
                raise HTTPException(500, "Curriculum manager not available")
            
            curriculum = polly.curriculum_manager.get_curriculum(curriculum_id)
            if not curriculum:
                raise HTTPException(404, f"Curriculum not found: {curriculum_id}")
            
            # Find section
            section = next((s for s in curriculum.sections if s.id == section_id), None)
            if not section:
                raise HTTPException(404, f"Section not found: {section_id}")
            
            # Find exercise
            exercise = next((e for e in section.exercises if e.get('id') == exercise_id), None)
            if not exercise:
                raise HTTPException(404, f"Exercise not found: {exercise_id}")
            
            # Use Professor to validate and provide feedback
            print("=== ABOUT TO IMPORT ProfessorPersona ===", flush=True)
            logger.info("=== About to import ProfessorPersona ===")
            from core.personas.implementations.professor import ProfessorPersona
            print("=== IMPORT SUCCESSFUL ===", flush=True)
            logger.info("=== ProfessorPersona imported successfully ===")
            # from core.personas.base import PersonaContext  # Not actually used
            
            # Create Professor with router_v2
            logger.info("=== About to create ProfessorPersona instance ===")
            professor = ProfessorPersona(
                name='professor',
                router=polly.router_v2 if hasattr(polly, 'router_v2') else polly.router,
                skill_manager=polly.skill_manager if hasattr(polly, 'skill_manager') else None,
                rag=polly.rag if hasattr(polly, 'rag') else None,
                learning_tracker=None,
                curriculum_manager=polly.curriculum_manager if hasattr(polly, 'curriculum_manager') else None,
                template_manager=polly.template_manager if hasattr(polly, 'template_manager') else None,
                domain_engine=polly.domains if hasattr(polly, 'domains') else None
            )
            logger.info("=== ProfessorPersona instance created ===")

            
            # Build validation prompt
            validation_prompt = f"""
You are reviewing a learner's solution to a coding exercise. Provide constructive feedback.

**Exercise:** {exercise.get('title')}
**Description:** {exercise.get('description')}

**Expected Solution:**
```python
{exercise.get('solution', '')}
```

**Learner's Code:**
```python
{code}
```

**Learner's Output:**
```
{output}
```

Please analyze the learner's solution and provide:
1. Is the solution correct? (Yes/No)
2. Constructive feedback (2-3 sentences)
3. What they did well (1-2 points)
4. What could be improved (1-2 points)
5. A hint for improvement (if needed)

Format your response as:
CORRECT: Yes/No
FEEDBACK: [Your feedback]
STRENGTHS: [What they did well]
IMPROVEMENTS: [What could be better]
HINT: [A helpful hint]
"""
            
            # Get feedback from Professor
            # context = PersonaContext(  # Not actually used
            #     user_message=validation_prompt,
            #     current_mode="chat",
            #     metadata={"task": "exercise_validation"}
            # )
            
            from core.router_v2 import TaskType
            response = await professor.router.complete_with_fallback(
                messages=[{"role": "user", "content": validation_prompt}],
                task_type=TaskType.CREATIVE,
                model_preferences=["anthropic/claude-sonnet-4"]
            )
            
            feedback_text = response.content  # CompletionResponse has .content attribute
            
            # Parse feedback
            correct = "yes" in feedback_text.lower().split("correct:")[1].split("\n")[0].lower() if "correct:" in feedback_text.lower() else False
            
            return {
                "status": "success",
                "validation": {
                    "correct": correct,
                    "feedback": feedback_text,
                    "exercise": {
                        "id": exercise_id,
                        "title": exercise.get('title'),
                        "solution": exercise.get('solution', '')
                    }
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating exercise: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to validate exercise: {str(e)}")
    
    @app.post("/polly/curricula/{curriculum_id}/session/start")
    async def start_curriculum_session(curriculum_id: str, section_id: str):
        """
        Start formal curriculum learning session.
        Note: This endpoint is a placeholder for Phase 6.
        
        Response:
        {
            "status": "success",
            "session": {
                "curriculum_id": "react-mastery",
                "section_id": "week-1.1"
            }
        }
        """
        try:
            # TODO Phase 6: Implement session management in Professor
            raise HTTPException(501, "Session management not yet implemented (Phase 6)")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error starting session {curriculum_id}/{section_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to start session: {str(e)}")
    
    @app.post("/polly/curricula/session/end")
    async def end_curriculum_session():
        """
        End curriculum session.
        Note: This endpoint is a placeholder for Phase 6.
        
        Response:
        {
            "status": "success"
        }
        """
        try:
            # TODO Phase 6: Implement session management in Professor
            raise HTTPException(501, "Session management not yet implemented (Phase 6)")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error ending session: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to end session: {str(e)}")
    
    # ===== Curriculum Template Endpoints (Phase 23 - Phase 2) =====
    
    @app.get("/polly/curricula/templates/list")
    async def list_curriculum_templates(category: Optional[str] = None):
        """
        List available curriculum templates.
        
        Query params:
            category: Filter by category (programming, framework, skill, problem-solving, exploration)
        
        Response:
        {
            "templates": [
                {
                    "id": "programming-language",
                    "name": "Programming Language",
                    "category": "programming",
                    "description": "Learn any programming language systematically",
                    "estimated_duration": "8 weeks"
                },
                ...
            ]
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'template_manager'):
                return {"templates": []}
            
            templates = polly.template_manager.list_templates(category=category)
            
            return {
                "templates": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "category": t.category,
                        "description": t.description,
                        "estimated_duration": t.estimated_duration,
                        "difficulty_levels": t.difficulty_levels
                    }
                    for t in templates
                ]
            }
        except Exception as e:
            logger.error(f"Error listing templates: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to list templates: {str(e)}")
    
    @app.get("/polly/curricula/templates/{template_id}")
    async def get_curriculum_template(template_id: str):
        """
        Get detailed template information including structure.
        
        Response:
        {
            "id": "programming-language",
            "name": "Programming Language",
            "category": "programming",
            "description": "...",
            "customization_questions": ["...", "..."],
            "structure": [...],
            "estimated_duration": "8 weeks"
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'template_manager'):
                raise HTTPException(404, "Template manager not available")
            
            template = polly.template_manager.get_template(template_id)
            if not template:
                raise HTTPException(404, f"Template not found: {template_id}")
            
            return template.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting template {template_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to get template: {str(e)}")
    
    @app.post("/polly/curricula/templates/detect")
    async def detect_curriculum_template(request: Request):
        """
        Detect appropriate template based on learning goal.
        
        Request body:
        {
            "goal": "Learn Python for data science"
        }
        
        Response:
        {
            "template_id": "programming-language",
            "confidence": 0.9,
            "reasoning": "Goal mentions a programming language",
            "template": {
                "id": "programming-language",
                "name": "Programming Language",
                "description": "..."
            }
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'template_manager'):
                raise HTTPException(500, "Template manager not available")
            
            body = await request.json()
            goal = body.get('goal', '')
            
            if not goal:
                raise HTTPException(400, "Goal is required")
            
            detection = polly.template_manager.detect_template(goal)
            if not detection:
                raise HTTPException(404, "Could not detect appropriate template")
            
            # Get full template details
            template = polly.template_manager.get_template(detection['template_id'])
            
            return {
                **detection,
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "estimated_duration": template.estimated_duration
                } if template else None
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error detecting template: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to detect template: {str(e)}")
    
    @app.post("/polly/curricula/templates/{template_id}/customize")
    async def customize_curriculum_template(template_id: str, request: Request):
        """
        Customize template with user-specific information.
        
        Request body:
        {
            "title": "Python for Data Science",
            "goal": "Learn Python for data analysis",
            "topic": "Python",
            "level": "beginner",
            "customizations": {
                "language": "Python",
                "focus_area": "data science",
                "experience": "beginner"
            }
        }
        
        Response:
        {
            "curriculum": {
                "title": "Python for Data Science",
                "goal": "...",
                "sections": [...],
                "template_id": "programming-language"
            }
        }
        """
        try:
            polly = get_polly()
            if not polly or not hasattr(polly, 'template_manager'):
                raise HTTPException(500, "Template manager not available")
            
            body = await request.json()
            
            # Create curriculum from template
            curriculum_data = polly.template_manager.create_from_template(
                template_id=template_id,
                customizations=body
            )
            
            return {
                "success": True,
                "curriculum": curriculum_data
            }
        except ValueError as e:
            raise HTTPException(404, str(e))
        except Exception as e:
            logger.error(f"Error customizing template {template_id}: {e}", exc_info=True)
            raise HTTPException(500, f"Failed to customize template: {str(e)}")

    return app


# Create app instance at module level for uvicorn
app = create_app()


# Standalone server for testing
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11436)

"""
Polly Core Engine
The main orchestrator that brings everything together

This is the heart of Polly - it coordinates:
- RAG retrieval across all sources
- Domain detection and context enrichment
- Pattern learning and application
- Intelligent model routing
- Response generation
"""

from pathlib import Path
from typing import List, Dict, Optional, Any, AsyncIterator
from datetime import datetime
import asyncio
import logging

from .config import PollyConfig, get_config
from .constitutional import get_constitutional_layer
from .domains import DomainEngine, DOMAIN_PROMPTS
from .hardened.classifier import RetrievalClassifier, RetrievalTier
from .rag import UnifiedRAG
from .router import IntelligentRouter, UnifiedLLM, RoutingMode, ModelTier
from .router_v2 import IntelligentRouterV2, ConfidenceLevel, create_router_v2, AllProvidersFailed
from .compression import CompressionManager
from .skills.manager import SkillManager

logger = logging.getLogger(__name__)


class Polly:
    """
    The Polly AI Assistant.

    Polly is your personal AI that:
    - Understands your domains (Sigils, Signals, Scrolls, Glyphs, Grids)
    - Searches your knowledge base (Obsidian, codebases, docs)
    - Learns your patterns over time
    - Routes intelligently between local and cloud models
    - Maintains context across conversations
    """

    def __init__(self, config: Optional[PollyConfig] = None):
        import time
        _total_start = time.time()
        
        logger.info("=== POLLY INITIALIZATION STARTING ===")

        self.config = config or get_config()
        self.user_name = self.config.user_name
        logger.info(f"Config loaded for user: {self.user_name}")

        # Initialize components (learners first so RAG can use pattern learner)
        _step_start = time.time()
        self._init_domains()
        logger.debug(f"[INIT] _init_domains: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_learners()  # Initialize learners before RAG
        logger.debug(f"[INIT] _init_learners: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_rag()       # RAG can now use pattern_learner
        logger.debug(f"[INIT] _init_rag: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_router()
        logger.debug(f"[INIT] _init_router: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_notes_sync()  # Initialize notes sync manager
        logger.debug(f"[INIT] _init_notes_sync: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_dedup()       # Initialize deduplication engine (Phase 21)
        logger.debug(f"[INIT] _init_dedup: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_compression()  # Initialize compression manager (Phase 11c)
        logger.debug(f"[INIT] _init_compression: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_mental_models()  # Initialize mental models system (Phase 14)
        logger.debug(f"[INIT] _init_mental_models: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_skills()  # Initialize skill system (Phase 16c)
        logger.debug(f"[INIT] _init_skills: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_personas()  # Initialize persona system (Phase 11c)
        logger.debug(f"[INIT] _init_personas: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_knowledge_writer()  # Initialize knowledge writing system
        logger.debug(f"[INIT] _init_knowledge_writer: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_wave3_pipeline()  # Initialize Wave 3 (decomposition, split routing, synthesis)
        logger.debug(f"[INIT] _init_wave3_pipeline: {time.time() - _step_start:.2f}s")

        _step_start = time.time()
        self._init_memory_context()  # Initialize tiered memory, budget allocator, rolling context
        logger.debug(f"[INIT] _init_memory_context: {time.time() - _step_start:.2f}s")

        # Conversation state
        self.conversation_history: List[Dict] = []
        self.session_start = datetime.now()
        
        # RAG metadata tracking for pattern learning (Phase 2 Enhancement)
        self._rag_metadata = {
            'queries': [],  # List of {query, chunks, collections, domains}
            'domains': set(),  # Accumulated domains seen
            'successful_files': set()  # Files that were retrieved
        }

        # Per-turn RAG chunks for reinforcement learning (Spec 05)
        self._current_turn_chunks: list = []

        _total_time = time.time() - _total_start
        logger.info(f"=== POLLY INITIALIZED FOR {self.user_name} (took {_total_time:.2f}s) ===")

    def _init_domains(self):
        """Initialize domain engine."""
        self.domains = DomainEngine(
                config_domains=self.config.domains,
                config_dict={"domains": self.config.domains} if self.config.domains else None,
            )
        logger.info("Domain engine initialized")

    def _init_rag(self):
        """Initialize RAG system."""
        # Compute BM25 index path (Spec 08: persist alongside chroma_db)
        bm25_persist = self.config.get("rag.bm25.persist", True)
        bm25_index_path: Optional[str] = None
        if bm25_persist:
            _raw_index_path = self.config.get("rag.bm25.index_path", None)
            if _raw_index_path:
                bm25_index_path = str(Path(_raw_index_path).expanduser())
            else:
                # Default: sibling of chroma_db directory
                bm25_index_path = str(Path(self.config.vector_db_path).expanduser().parent / "bm25_index.pkl")

        self.rag = UnifiedRAG(
            db_path=self.config.vector_db_path,
            ollama_host=self.config.ollama_host,
            embedding_model=self.config.embedding_model,
            chunk_size=self.config.get("rag.chunk_size", 800),
            pattern_learner=self.pattern_engine,  # Pass pattern engine for code pattern extraction
            bm25_index_path=bm25_index_path,
        )

        # BM25 startup: either loaded from disk or will build lazily on next index run
        if self.rag.use_hybrid_search:
            if bm25_index_path and self.rag.hybrid_searcher and self.rag.hybrid_searcher.bm25_index.bm25:
                logger.info("BM25 index loaded from disk — hybrid search ready immediately")
            else:
                logger.info("Hybrid search enabled — BM25 index will be built on next index run")
        
        logger.info("RAG system initialized")

    def _init_router(self):
        """Initialize model router (v1 or v2 based on config)."""
        # Check if router_v2 is enabled in config (default True for chat/personas)
        use_router_v2 = self.config.get("routing_v2.enabled", True)
        
        if use_router_v2:
            logger.info("Initializing router_v2 (multi-provider intelligent routing)")
            self._init_router_v2()
        else:
            logger.info("Initializing router_v1 (legacy routing)")
            self._init_router_v1()
    
    def _init_router_v1(self):
        """Initialize legacy router (v1)."""
        local_models = self.config.get("models.local.chat_models", None)
        self.router = IntelligentRouter(
            ollama_host=self.config.ollama_host,
            anthropic_api_key=self.config.cloud_api_key,
            default_mode=RoutingMode.AUTO,
            local_models=local_models,
        )
        
        # Skip availability check at init to avoid blocking/hanging
        # Availability will be checked on first use

        self.llm = UnifiedLLM(
            router=self.router,
            default_system_prompt=self._build_system_prompt()
        )
        logger.info("Router v1 initialized (availability will be checked on first use)")
        
        # Set flag to indicate which router is active
        self.using_router_v2 = False
    
    def _init_router_v1_hybrid(self):
        """Initialize legacy router (v1) for hybrid mode with router_v2.
        
        This method initializes router_v1 WITHOUT overwriting using_router_v2 flag.
        Used when router_v2 is active but we want v1 available for local fallback.
        """
        local_models = self.config.get("models.local.chat_models", None)
        self.router = IntelligentRouter(
            ollama_host=self.config.ollama_host,
            anthropic_api_key=self.config.cloud_api_key,
            default_mode=RoutingMode.AUTO,
            local_models=local_models,
        )
        
        # Skip availability check at init to avoid blocking/hanging
        # Availability will be checked on first use

        self.llm = UnifiedLLM(
            router=self.router,
            default_system_prompt=self._build_system_prompt()
        )
        logger.info("Router v1 (hybrid) initialized for local fallback (availability will be checked on first use)")
        # NOTE: Do NOT set using_router_v2 flag here - it should remain True
    
    def _init_router_v2(self):
        """Initialize new multi-provider router (v2)."""
        from .secrets_manager import get_secrets_manager
        from .budget_manager import BudgetManager
        
        # Get API keys from secrets manager
        secrets = get_secrets_manager()
        anthropic_key = secrets.get_secret('anthropic', fallback_to_env=True)
        openai_key = secrets.get_secret('openai', fallback_to_env=True)
        github_token = secrets.get_secret('github', fallback_to_env=True)
        grok_key = secrets.get_secret('grok', fallback_to_env=True)
        perplexity_key = secrets.get_secret('perplexity', fallback_to_env=True)
        gemini_key = secrets.get_secret('gemini', fallback_to_env=True)
        mistral_key = secrets.get_secret('mistral', fallback_to_env=True)
        openrouter_key = secrets.get_secret('openrouter', fallback_to_env=True)
        
        # Initialize budget manager (from polly_routing)
        budget_db_path = Path(self.config.get("routing_v2.budget.database_path", "~/.polly/usage.db")).expanduser()
        self.budget_manager = BudgetManager(
            db_path=budget_db_path,
            daily_limit=self.config.get("routing_v2.budget.daily_limit", 10.0),
            monthly_limit=self.config.get("routing_v2.budget.monthly_limit", 200.0)
        )
        
        use_litellm = self.config.get("routing_v2.use_litellm", False)
        litellm_config_path = self.config.get("routing_v2.litellm_config_path", "config/litellm_config.yaml")
        
        # Build router via adapter (polly_routing + core providers when not use_litellm)
        self.router_v2 = create_router_v2(
            budget_manager=self.budget_manager,
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key,
            github_token=github_token,
            grok_api_key=grok_key,
            perplexity_api_key=perplexity_key,
            gemini_api_key=gemini_key,
            mistral_api_key=mistral_key,
            openrouter_api_key=openrouter_key,
            use_litellm=use_litellm,
            litellm_config_path=litellm_config_path,
        )
        # Attach config dict so personas can read memory.* for Mem0 (per-persona memory)
        self.router_v2.config = getattr(self.config, "_config", {})
        
        # Skip provider validation at init to avoid blocking/hanging
        # Providers will be validated on first use
        logger.info("Router v2 initialized (providers will be validated on first use)")
        
        # Set default confidence level from config
        confidence_str = self.config.get("routing_v2.default_confidence", "balanced")
        self.default_confidence = ConfidenceLevel(confidence_str)
        
        logger.info(f"Router v2 initialized (Providers: {list(self.router_v2.providers.keys())})")
        logger.info(f"Default confidence: {self.default_confidence.value}")
        
        # Set flag to indicate which router is active
        # IMPORTANT: Set this BEFORE calling _init_router_v1 so it doesn't get overwritten
        self.using_router_v2 = True
        
        # HYBRID MODE: Initialize router_v1 for local model fallback
        # This allows us to use local Ollama when RAG context is strong
        logger.info("Initializing router_v1 for hybrid local/cloud routing")
        self._init_router_v1_hybrid()

    def _init_learners(self):
        """Initialize pattern engine, knowledge graph, learning tracker, and curriculum manager."""
        try:
            from core.patterns import PatternEngine
            from core.entities import EntityStore, EntityExtractor, EntityContextBuilder
            from learners.learning_tracker import LearningTracker
            from learners.curriculum_manager import CurriculumManager
            from learners.curriculum_template_manager import CurriculumTemplateManager

            patterns_path = Path(self.config.get("patterns.storage_path", "~/.polly/patterns.json")).expanduser()
            graph_path = Path(self.config.get("graph.storage_path", "~/.polly/knowledge_graph.json")).expanduser()
            entity_db_path = Path(self.config.get("entities.db_path", "~/.polly/entities.db")).expanduser()
            learning_path = Path(self.config.get("learning.storage_path", "~/.polly/learning.json")).expanduser()
            vault_path = Path(self.config.get("vault_path", "~/polly/vault")).expanduser()

            # Unified Pattern Engine — replaces both learners/patterns.PatternLearner
            # and core/pattern_learning.PatternLearner
            mem0_config = None
            try:
                config_dict = getattr(self.config, "_config", {})
                memory = config_dict.get("memory", {})
                if memory.get("provider") == "mem0" and memory.get("mem0", {}).get("enabled"):
                    mem0_config = config_dict
                    logger.info("Mem0 enabled for pattern engine semantic search")
            except Exception as mem0_e:
                logger.debug(f"Mem0 config not available: {mem0_e}")

            self.pattern_engine = PatternEngine(
                json_path=patterns_path,
                mem0_config=mem0_config,
            )

            # Run migration from old format if needed (one-time)
            try:
                from core.patterns.migration import migrate_from_v2
                stats = migrate_from_v2(patterns_path, self.pattern_engine)
                if stats.get("patterns_migrated", 0) > 0:
                    logger.info(f"Migrated {stats['patterns_migrated']} patterns from old format")
            except Exception as mig_e:
                logger.debug(f"Pattern migration skipped: {mig_e}")

            # Backward compat: alias for code that still references pattern_learner
            self.pattern_learner = self.pattern_engine

            # Unified entity store (replaces KnowledgeGraph)
            self.entity_store = EntityStore(entity_db_path)
            self.entity_extractor = EntityExtractor(self.entity_store)
            self.entity_context = EntityContextBuilder(
                self.entity_store, pattern_engine=self.pattern_engine
            )
            try:
                from core.entities.migration import migrate_from_json
                mig_stats = migrate_from_json(graph_path, self.entity_store)
                if mig_stats.get("entities", 0) > 0:
                    logger.info(f"Migrated {mig_stats['entities']} entities from knowledge graph JSON")
            except Exception as mig_e:
                logger.debug(f"Entity migration skipped: {mig_e}")

            self.learning_tracker = LearningTracker(learning_path)
            self.curriculum_manager = CurriculumManager(vault_path)
            self.template_manager = CurriculumTemplateManager(vault_path)
            
            # Use Case 2: Attach pattern engine to DomainEngine for enhanced detection
            if self.domains and self.pattern_engine:
                self.domains.set_pattern_learner(self.pattern_engine)
            
            logger.info(f"Learners initialized (tracking {len(self.learning_tracker.topics)} learning topics, {len(self.curriculum_manager.curricula)} curricula, {len(self.template_manager.list_templates())} templates)")
        except Exception as e:
            logger.warning(f"Could not initialize learners: {e}")
            self.pattern_engine = None
            self.pattern_learner = None
            self.entity_store = None
            self.entity_extractor = None
            self.entity_context = None
            self.learning_tracker = None
            self.curriculum_manager = None
            self.template_manager = None
    
    def _init_notes_sync(self):
        """Initialize notes sync manager if enabled (supports both native and Obsidian)."""
        import threading
        
        print("=== _init_notes_sync CALLED ===", flush=True)
        logger.info("=== STARTING _init_notes_sync ===")
        
        # Check if notes sync is enabled in config
        if not self.config.get("notes.sync.enabled", True):
            logger.info("Notes sync disabled in config")
            self.notes_sync = None
            return
        
        # Initialize in background thread to avoid blocking
        self.notes_sync = None  # Will be set by background thread
        
        def init_watcher_background():
            """Initialize file watcher in background."""
            try:
                logger.info("[Background] Initializing notes file watcher...")
                print("[Background] Starting file watcher initialization...", flush=True)
                
                from core.notes_file_watcher import NotesFileWatcher
                from core.notes_source_manager import NotesSourceManager
                
                # Get the notes path from NotesSourceManager
                manager = NotesSourceManager()
                notes_path = manager.get_notes_path()
                
                watcher = NotesFileWatcher(notes_path)
                watcher.start()
                
                # Atomically set the watcher
                self.notes_sync = watcher
                
                logger.info("[Background] File watcher initialized successfully")
                print("[Background] ✅ File watcher ready", flush=True)
                
            except Exception as e:
                logger.error(f"[Background] File watcher initialization failed: {e}", exc_info=True)
                print(f"[Background] ❌ File watcher failed: {e}", flush=True)
                self.notes_sync = None
        
        # Start in background thread
        watcher_thread = threading.Thread(target=init_watcher_background, daemon=True, name="FileWatcherInit")
        watcher_thread.start()
        
        logger.info("File watcher initialization started in background")
        print("File watcher initializing in background...", flush=True)
    
    def _init_dedup(self):
        """Initialize deduplication engine (Phase 21)."""
        logger.info("=== STARTING _init_dedup ===")
        try:
            from core.notes_dedup import init_dedup_engine
            from core.notes_index import get_notes_index
            
            # Initialize dedup engine with RAG, NotesIndex, and config
            logger.info("Getting notes index for dedup...")
            notes_idx = get_notes_index()
            logger.info("Initializing dedup engine...")
            self.dedup_engine = init_dedup_engine(self.rag, notes_idx, self.config)
            logger.info("Deduplication engine initialized")
            logger.info("=== COMPLETED _init_dedup ===")
            
        except Exception as e:
            logger.warning(f"Could not initialize deduplication engine: {e}")
            self.dedup_engine = None

    def _init_compression(self):
        """Initialize compression manager (Phase 11c)."""
        try:
            self.compression_manager = CompressionManager()
            
            # Load compression settings from config
            self._compression_enabled = self.config.get("compression.enabled", True)
            self._compression_threshold = self.config.get("compression.message_threshold", 20)
            self._compression_age_hours = self.config.get("compression.age_hours", 24)
            self._keep_recent_count = self.config.get("compression.keep_recent", 10)
            
            logger.info(
                f"Compression manager initialized "
                f"(threshold: {self._compression_threshold} messages, "
                f"keep recent: {self._keep_recent_count})"
            )
        except Exception as e:
            logger.warning(f"Could not initialize compression manager: {e}")
            self.compression_manager = None
            self._compression_enabled = False
    
    def _init_mental_models(self):
        """Initialize mental models system (Phase 14)."""
        try:
            from core.mental_models import MentalModelManager
            
            # Get storage path from config
            storage_path = self.config.get("mental_models.storage_path", "~/.polly/mental_models.yaml")
            
            # Initialize manager with compressor for PIL compression
            self.mental_model_manager = MentalModelManager(
                storage_path=storage_path,
                compressor=self.compression_manager.compressor if self.compression_manager else None,
                config=self.config._config if hasattr(self.config, "_config") else {},
            )
            
            logger.info(f"Mental model manager initialized with {len(self.mental_model_manager.models)} models")
        except Exception as e:
            logger.warning(f"Could not initialize mental models: {e}")
            self.mental_model_manager = None
    
    def _init_skills(self):
        """Initialize skill system (Phase 16c)."""
        try:
            # Initialize skill manager
            self.skill_manager = SkillManager()
            
            # Get count of discovered skills
            skill_count = len(self.skill_manager.metadata_cache)
            
            logger.info(f"Skill system initialized with {skill_count} skills discovered")
        except Exception as e:
            logger.warning(f"Could not initialize skill system: {e}")
            self.skill_manager = None
    
    def _init_personas(self):
        """Initialize persona system (Phase 11c)."""
        try:
            # Only initialize if router_v2 is enabled
            if not self.using_router_v2:
                logger.info("Persona system requires Router v2 - skipping initialization")
                self.persona_manager = None
                return
            
            from core.personas import PersonaManager
            
            # Initialize persona manager with router_v2, skill_manager, rag, and learning_tracker
            self.persona_manager = PersonaManager(
                router=self.router_v2,
                skill_manager=self.skill_manager,
                rag=self.rag,
                learning_tracker=self.learning_tracker,
                curriculum_manager=self.curriculum_manager,
                template_manager=self.template_manager,
                domain_engine=self.domains if hasattr(self, 'domains') else None,
                pattern_engine=self.pattern_engine if hasattr(self, 'pattern_engine') else None
            )
            
            # Get list of available personas
            available = PersonaManager.list_available_personas()
            persona_names = [p['name'] for p in available]
            
            logger.info(f"Persona system initialized with {len(persona_names)} personas: {', '.join(persona_names)}")
            
        except Exception as e:
            logger.warning(f"Could not initialize persona system: {e}")
            self.persona_manager = None

    def _init_knowledge_writer(self):
        """Initialize knowledge writing system and autonomy metrics."""
        try:
            from core.autonomy_metrics import init_autonomy_metrics
            self.autonomy_metrics = init_autonomy_metrics()
            logger.info("Autonomy metrics initialized")
        except Exception as e:
            logger.warning(f"Could not initialize autonomy metrics: {e}")
            self.autonomy_metrics = None

        try:
            from core.knowledge_writer import init_knowledge_writer
            from core.notes_source_manager import NotesSourceManager

            notes_source = NotesSourceManager()

            # Try to get Scribe persona for enrichment
            scribe = None
            if self.persona_manager:
                try:
                    scribe_instance = self.persona_manager.get_persona("scribe")
                    if scribe_instance:
                        scribe = scribe_instance
                except Exception:
                    pass

            self.knowledge_writer = init_knowledge_writer(
                config=self.config,
                notes_source_manager=notes_source,
                rag=self.rag,
                domain_engine=self.domains,
                scribe_persona=scribe,
                metrics_tracker=self.autonomy_metrics,
            )
            logger.info("KnowledgeWriter initialized")
        except Exception as e:
            logger.warning(f"Could not initialize knowledge writer: {e}")
            self.knowledge_writer = None

    def _init_wave3_pipeline(self):
        """Initialize Wave 3 routing pipeline (decomposition, split routing, synthesis)."""
        logger.info("Initializing Wave 3 routing pipeline...")
        try:
            # Check if Wave 3 is enabled
            routing_config = self.config.get('routing', {})
            decomp_enabled = routing_config.get('decomposition', {}).get('enabled', False)
            split_enabled = routing_config.get('split_routing', {}).get('enabled', False)
            synthesis_enabled = routing_config.get('synthesis', {}).get('enabled', False)
            
            logger.info(f"Wave 3 config: decomp={decomp_enabled}, split={split_enabled}, synthesis={synthesis_enabled}")
            
            if not (decomp_enabled or split_enabled or synthesis_enabled):
                logger.info("Wave 3 pipeline disabled in config")
                self.query_decomposer = None
                self.split_router = None
                self.synthesizer = None
                return
            
            # Initialize query decomposer
            if decomp_enabled:
                from core.query_decomposition import QueryDecomposer
                self.query_decomposer = QueryDecomposer(
                    config=self.config,
                    router=self.router_v2,
                    pattern_learner=self.pattern_engine
                )
                logger.info("Query decomposer initialized")
            else:
                self.query_decomposer = None
                logger.info("Query decomposer disabled in config")
            
            # Initialize split router
            if split_enabled:
                from core.split_router import SplitRouter
                self.split_router = SplitRouter(
                    config=self.config,
                    router=self.router_v2,
                    rag=self.rag,
                    local_llm=self.llm,  # Pass local LLM for Ollama routing
                    autonomy_metrics=self.autonomy_metrics
                )
                logger.info("Split router initialized")
            else:
                self.split_router = None
                logger.info("Split router disabled in config")
            
            # Initialize synthesizer
            if synthesis_enabled:
                from core.synthesis import Synthesizer
                # Try to get compression manager
                compression_mgr = getattr(self, 'compression_manager', None)
                self.synthesizer = Synthesizer(
                    config=self.config,
                    router=self.router_v2,
                    compression_manager=compression_mgr
                )
                logger.info("Synthesizer initialized")
            else:
                self.synthesizer = None
                logger.info("Synthesizer disabled in config")
            
            logger.info(f"Wave 3 pipeline initialized (decomp={decomp_enabled}, split={split_enabled}, synthesis={synthesis_enabled})")
            
        except Exception as e:
            logger.error(f"Could not initialize Wave 3 pipeline: {e}", exc_info=True)
            self.query_decomposer = None
            self.split_router = None
            self.synthesizer = None

    def _init_memory_context(self):
        """Initialize tiered memory, budget allocator, relevance scorer, and rolling context.

        All components are optional — if any fail to initialize the system
        degrades gracefully to the original unbounded context assembly.
        """
        # Defaults — each set to None so the rest of the pipeline knows to skip
        self.mem0_adapter = None
        self.tiered_store = None
        self.memory_retriever = None
        self.session_extractor = None
        self.budget_allocator = None
        self.relevance_scorer = None
        self.rolling_context = None

        config_dict = getattr(self.config, "_config", {})

        # ------------------------------------------------------------------
        # 1. Mem0 adapter → Tiered Memory Store → Retriever + Extractor
        # ------------------------------------------------------------------
        try:
            memory_cfg = config_dict.get("memory", {})
            provider = memory_cfg.get("provider", "local")
            mem0_enabled = memory_cfg.get("mem0", {}).get("enabled", False)

            if provider == "mem0" and mem0_enabled:
                from core.memory import get_memory_adapter
                self.mem0_adapter = get_memory_adapter(config_dict)

                if self.mem0_adapter is not None:
                    from core.memory.tiers import TieredMemoryStore
                    self.tiered_store = TieredMemoryStore(
                        self.mem0_adapter,
                        memory_cfg.get("tiers", {}),
                    )
                    logger.info("TieredMemoryStore initialized")

                    from core.memory.retriever import MemoryRetriever
                    self.memory_retriever = MemoryRetriever(
                        self.tiered_store,
                        memory_cfg,
                    )
                    logger.info("MemoryRetriever initialized (priority 50)")

                    from core.memory.extractor import SessionExtractor
                    self.session_extractor = SessionExtractor(
                        tiered_store=self.tiered_store,
                        config=memory_cfg.get("extraction", {}),
                        budget_manager=getattr(self, "budget_manager", None),
                        router_v2=getattr(self, "router_v2", None),
                    )
                    logger.info("SessionExtractor initialized")
                else:
                    logger.info("Mem0 adapter returned None — memory tiers disabled")
            else:
                logger.info("Mem0 not enabled — memory tiers disabled")
        except Exception as e:
            logger.warning(f"Memory tier init failed (graceful degradation): {e}")
            self.mem0_adapter = None
            self.tiered_store = None
            self.memory_retriever = None
            self.session_extractor = None

        # ------------------------------------------------------------------
        # 2. Context infrastructure (works with or without memory tiers)
        # ------------------------------------------------------------------
        try:
            budget_cfg = config_dict.get("context_budget", {})

            from core.context.budget_allocator import BudgetAllocator
            self.budget_allocator = BudgetAllocator(budget_cfg)
            logger.info("BudgetAllocator initialized")

            from core.context.relevance_scorer import RelevanceScorer
            self.relevance_scorer = RelevanceScorer(
                budget_cfg.get("relevance_weights", {})
            )
            logger.info("RelevanceScorer initialized")

            from core.context.rolling_context import RollingContext
            rolling_config = budget_cfg.get("rolling", {})

            # Attempt to restore RollingContext from previous session (Spec 03)
            db_path = Path(self.config.get("knowledge_base.path", "~/.polly")).expanduser() / "compression.db"
            if rolling_config.get("persist_across_sessions", True):
                last_session_id = self._load_last_session_id(db_path)
                if last_session_id:
                    try:
                        from datetime import datetime
                        saved_at, gap_seconds = self._load_session_saved_at(db_path, last_session_id)
                        if saved_at and gap_seconds is not None:
                            self.rolling_context = RollingContext.load(
                                db_path=str(db_path),
                                session_id=last_session_id,
                                config=rolling_config,
                                scorer=self.relevance_scorer,
                                max_age_hours=rolling_config.get("max_persist_age_hours", 72.0),
                                session_gap_seconds=gap_seconds,
                            )
                            loaded_count = len(self.rolling_context.entries)
                            logger.info(
                                f"Restored RollingContext: {loaded_count} entries from "
                                f"session {last_session_id} ({gap_seconds/3600:.1f}h gap)"
                            )
                        else:
                            self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
                    except Exception as e:
                        logger.warning(f"Could not restore RollingContext: {e}. Starting fresh.")
                        self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
                else:
                    self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
            else:
                self.rolling_context = RollingContext(rolling_config, scorer=self.relevance_scorer)
            logger.info("RollingContext initialized")
        except Exception as e:
            logger.warning(f"Context budget init failed (graceful degradation): {e}")
            self.budget_allocator = None
            self.relevance_scorer = None
            self.rolling_context = None

        # ------------------------------------------------------------------
        # 3. Context metrics for observability (Spec 06)
        # ------------------------------------------------------------------
        try:
            from core.context_metrics import init_context_metrics
            db_path = Path(self.config.get("knowledge_base.path", "~/.polly")).expanduser() / "usage.db"
            self.context_metrics = init_context_metrics(db_path=db_path)
            logger.info("ContextMetrics initialized")
        except Exception as e:
            logger.warning(f"Context metrics init failed (non-critical): {e}")
            self.context_metrics = None

        # ------------------------------------------------------------------
        # 4. Semantic Cache (Spec 01)
        # ------------------------------------------------------------------
        self.semantic_cache = None
        cache_config = config_dict.get("semantic_cache", {})
        if cache_config.get("enabled", False):
            try:
                from core.cache import SemanticCache
                cache_db_path = str(
                    Path(self.config.get("knowledge_base.path", "~/.polly")).expanduser()
                    / "semantic_cache"
                )
                
                if self.rag and hasattr(self.rag, "embed_text"):
                    from core.cache.semantic_cache import init_semantic_cache
                    self.semantic_cache = SemanticCache(
                        db_path=cache_db_path,
                        embed_fn=self.rag.embed_text,
                        similarity_threshold=cache_config.get("similarity_threshold", 0.92),
                        max_entries=cache_config.get("max_entries", 500),
                        ttl_hours=cache_config.get("ttl_hours", 24),
                        exclude_personas=cache_config.get("exclude_personas", []),
                        exclude_domains=cache_config.get("exclude_domains", []),
                        min_response_tokens=cache_config.get("min_response_tokens", 50),
                    )
                    init_semantic_cache(self.semantic_cache)
                    logger.info("SemanticCache initialized")
                else:
                    logger.info("SemanticCache skipped: RAG not available for embedding")
            except Exception as e:
                logger.warning(f"Semantic cache init failed (non-critical): {e}")
                self.semantic_cache = None

    def _build_system_prompt(self) -> str:
        """Build the base system prompt with constitutional epistemology layer."""
        constitutional = get_constitutional_layer()
        
        return f"""{constitutional}

---

You are Polly, {self.user_name}'s personal AI assistant.

You have deep knowledge of {self.user_name}'s work across five domains:

**Sigils** (Code & Infrastructure): Docker, NAS, automation, Python, Rust, JavaScript, Lua
**Signals** (Audio Programming): norns, SuperCollider, MIDI, synthesis, real-time audio
**Scrolls** (Writing & Pedagogy): Obsidian notes, essays, popular education, Freire
**Glyphs** (Visual Work): Design, UI/UX, visual systems
**Grids** (Systems Thinking): Mental models, infinite games, constraint as meaning-creation

Your knowledge base includes:
- {self.user_name}'s Obsidian notes and writings
- Project codebases and technical implementations  
- GitHub repositories (synced and indexed)
- Calendar events and reminders
- Context7 reading library and annotations

Your approach:
- **Continuation over completion**: Design for infinite games, ongoing evolution
- **Instruments over tracks**: Favor generative tools over fixed outputs
- **Constraint as meaning-creation**: Boundaries that enable rather than limit
- **Cross-domain synthesis**: Connect patterns across domains when useful

When you have context from {self.user_name}'s knowledge base, cite your sources.
When suggesting code, reference patterns from existing projects when relevant.
When discussing concepts, connect them to {self.user_name}'s documented frameworks.

IMPORTANT: When asked about GitHub repositories, the repositories listed in the context below ARE the repositories you have access to. List them directly from the context. Do not give generic instructions about using the GitHub API or web interface - you already have the repository information.

Be direct, practical, and aligned with {self.user_name}'s polymathic approach.
"""

    def _get_patterns_for_prompt(self, query: str, detected_domains: List, limit: int = 5) -> List:
        """
        Get most relevant patterns for current query.
        
        Delegates to PatternEngine.get_patterns_for_prompt() which handles:
        - JSON backend keyword search
        - Mem0 backend semantic search (when available)
        - Multi-factor scoring (confidence, recency, domain, keyword match)
        
        Args:
            query: The user's query
            detected_domains: List of detected domains
            limit: Maximum number of patterns to return
            
        Returns:
            List of Pattern objects, sorted by relevance score
        """
        if not self.pattern_engine:
            return []
        domain_ids = [d for d in detected_domains if (d or "").strip().lower() not in ("", "unknown")]
        return self.pattern_engine.get_patterns_for_prompt(query, domain_ids, limit=limit)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract keywords from query for mental model matching.
        
        Args:
            query: User's query string
            
        Returns:
            List of meaningful keywords
        """
        import re
        
        # Tokenize and clean
        words = re.findall(r'\b[a-z]+\b', query.lower())
        
        # Stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
            'how', 'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'only', 'own', 'same', 'than', 'too', 'very', 'can', 'will',
            'just', 'should', 'now', 'this', 'that', 'these', 'those', 'what',
            'who', 'which', 'their', 'them', 'they', 'have', 'has', 'had', 'do',
            'does', 'did', 'been', 'being', 'are', 'was', 'were', 'am', 'is'
        }
        
        # Filter stop words and short words
        meaningful_words = [
            w for w in words 
            if len(w) > 3 and w not in stop_words
        ]
        
        return meaningful_words
    
    def _build_mental_models_context(
        self,
        query: str,
        domain: Optional[str] = None,
        page: Optional[str] = None,
        persona: Optional[str] = None,
        persona_mode: Optional[str] = None,
        override_model_ids: Optional[List[str]] = None
    ) -> str:
        """
        Build mental models context for system prompt.
        
        Gets relevant mental models based on three-tier activation,
        compresses them to PIL format, and formats for injection.
        
        Args:
            query: User's query
            domain: Detected domain
            page: Current page/view
            persona: Active persona
            persona_mode: Active mode within persona
            override_model_ids: List of model IDs to force active (bypasses automatic activation)
            
        Returns:
            Formatted mental models context string
        """
        if not self.mental_model_manager:
            return ""
        
        try:
            # If override is provided, get those specific models
            if override_model_ids is not None:
                models = []
                for model_id in override_model_ids:
                    model = self.mental_model_manager.get_model(model_id)
                    if model:
                        models.append(model)
                logger.info(f"Using {len(models)} overridden mental models: {override_model_ids}")
            else:
                # Extract keywords from query
                keywords = self._extract_keywords(query)
                
                # Get relevant models using three-tier scoring
                models = self.mental_model_manager.get_models_for_context(
                    domain=domain,
                    page=page,
                    persona=persona,
                    persona_mode=persona_mode,
                    keywords=keywords,
                    enabled_only=True
                )
            
            if not models:
                logger.debug("No mental models activated for this query")
                return ""
            
            # Compress each model to PIL format
            compressed_models = []
            for model in models:
                try:
                    model_dict = model.to_dict()
                    
                    # Use compressor if available
                    if self.compression_manager and self.compression_manager.compressor:
                        compressed = self.compression_manager.compressor.compress(
                            model_dict,
                            type='mental_model'
                        )
                        compressed_models.append(compressed)
                    else:
                        # Fallback: use model name and prompt injection
                        compressed_models.append(f"{model.name}: {model.prompt_injection[:100]}")
                except Exception as e:
                    logger.warning(f"Failed to compress mental model {model.id}: {e}")
            
            if not compressed_models:
                return ""
            
            # Format context
            context = "\n\n## Active Mental Models (Compressed)\n\n"
            context += "The following mental models guide your responses:\n\n"
            
            for compressed in compressed_models:
                context += f"{compressed}\n\n"
            
            context += "Apply these frameworks to guide your thinking and responses.\n"
            
            logger.info(f"Added {len(compressed_models)} mental models to prompt")
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to build mental models context: {e}")
            return ""

    def _notify_persona_context(self, persona_name: Optional[str], mode: Optional[str]) -> None:
        """Notify all persona-aware systems of the active persona (integration-contracts)."""
        if not persona_name:
            return
        mode = mode or ""
        for system in [self.pattern_engine, self.mental_model_manager, self.entity_context]:
            if system is not None and hasattr(system, "set_active_persona"):
                try:
                    system.set_active_persona(persona_name, mode)
                except Exception as e:
                    logger.debug(f"set_active_persona failed for {type(system).__name__}: {e}")

    # ------------------------------------------------------------------
    # RollingContext persistence helpers (Spec 03)
    # ------------------------------------------------------------------

    def _load_last_session_id(self, db_path) -> Optional[str]:
        """Load the most recent session ID from rolling_context_state."""
        import sqlite3
        from pathlib import Path
        db_path = str(Path(db_path).expanduser())
        if not Path(db_path).exists():
            return None
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT session_id FROM rolling_context_state
                ORDER BY saved_at DESC LIMIT 1
            """)
            row = cur.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.debug(f"Could not load last session ID: {e}")
            return None

    def _load_session_saved_at(self, db_path, session_id) -> tuple:
        """Load saved_at timestamp and gap seconds for a session."""
        import sqlite3
        from pathlib import Path
        from datetime import datetime
        db_path = str(Path(db_path).expanduser())
        if not Path(db_path).exists():
            return None, None
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT saved_at FROM rolling_context_state
                WHERE session_id = ?
                ORDER BY saved_at DESC LIMIT 1
            """, (session_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                saved_at = datetime.fromisoformat(row[0])
                gap_seconds = (datetime.now() - saved_at).total_seconds()
                return saved_at, gap_seconds
            return None, None
        except Exception as e:
            logger.debug(f"Could not load session saved_at: {e}")
            return None, None

    def _reinforce_chunk_patterns(self, query: str, response: str) -> None:
        """
        Per-turn chunk reinforcement (Spec 05).

        For each RAG chunk retrieved this turn, check if its content is referenced
        in the response. Referenced → positive hit; unreferenced → negative miss.
        """
        if not self.pattern_engine:
            return
        chunks = getattr(self, "_current_turn_chunks", [])
        if not chunks:
            return

        config_dict = getattr(self.config, "_config", {})
        rag_cfg = config_dict.get("rag", {}).get("pattern_boost", {})
        if not rag_cfg.get("enabled", True):
            return
        negative_enabled = rag_cfg.get("negative_patterns", True)

        response_lower = response.lower()
        try:
            query_sig = self.pattern_engine._create_query_signature(query)
            pattern_id = f"qcp_{query_sig}"
        except Exception:
            return

        # Key term extraction — reuse rolling context helper
        from core.context.rolling_context import _extract_key_terms

        for result in chunks:
            try:
                chunk = result.chunk
                chunk_terms = _extract_key_terms(chunk.content)
                if not chunk_terms:
                    continue
                match_count = sum(1 for t in chunk_terms if t in response_lower)
                threshold = 1 if len(chunk_terms) <= 3 else 2
                referenced = match_count >= threshold

                if referenced:
                    self.pattern_engine.record_chunk_hit(
                        pattern_id=pattern_id,
                        chunk_id=chunk.id,
                        collection=chunk.source_type,
                        query=query,
                    )
                elif negative_enabled:
                    self.pattern_engine.record_chunk_miss(
                        pattern_id=pattern_id,
                        chunk_id=chunk.id,
                        collection=chunk.source_type,
                    )
            except Exception as e:
                logger.debug(f"Chunk reinforcement failed for chunk: {e}")

    def _end_session(self):
        """Persist RollingContext on session end (Spec 03). Called on graceful shutdown."""
        config_dict = getattr(self.config, "_config", {})
        rolling_cfg = config_dict.get("context_budget", {}).get("rolling", {})

        if not rolling_cfg.get("persist_across_sessions", True):
            return
        if not self.rolling_context:
            return

        try:
            db_path = Path(self.config.get("knowledge_base.path", "~/.polly")).expanduser() / "compression.db"
            session_id = f"session_{self.session_start.isoformat()}" if self.session_start else "session_unknown"
            count = self.rolling_context.save(str(db_path), session_id)
            logger.info(f"Persisted RollingContext: {count} entries for session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to persist RollingContext on session end: {e}")

    def _estimate_model_tier(self, confidence: Optional[str] = None) -> str:
        """
        Estimate the likely model tier from routing confidence BEFORE the actual
        routing decision is made.

        Used for pre-routing RAG optimisations: n_results, max_context_tokens,
        and compression ratio.  Returns one of 'local_fast', 'local_balanced',
        or 'cloud'.

        Mapping:
          fast / FAST        → local_fast  (small context window)
          balanced / None    → local_balanced (standard)
          thorough / THOROUGH → cloud      (large context window)
        """
        if confidence is None:
            conf_str = self.default_confidence.value if self.default_confidence else "balanced"
        else:
            conf_str = confidence.lower() if isinstance(confidence, str) else str(confidence)

        if conf_str in ("fast",):
            return "local_fast"
        if conf_str in ("thorough",):
            return "cloud"
        return "local_balanced"

    def _gather_context(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        budget_plan: Optional[Any] = None,
        retrieval_tier: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        """Gather context from all ContextContributors, ordered by priority.

        When *budget_plan* is provided AND the rolling-context system is
        initialised, each contributor receives a token budget, results are
        scored for relevance, ingested into the rolling context window, and
        then bin-packed to fit within section budgets.

        Without a budget_plan the method falls back to the original behaviour
        (unbounded concatenation, no scoring).

        When *retrieval_tier* is provided (a TierResult from the
        RetrievalClassifier), it influences scoring:
          - ADJACENT: RAG-sourced entry scores are multiplied by 0.7
          - ABSENT:   Memory retriever uses more aggressive limits
                      (episodic_limit 5→10, min_similarity 0.4→0.3)
        """
        use_budget = (
            budget_plan is not None
            and self.rolling_context is not None
            and self.relevance_scorer is not None
        )

        # ------------------------------------------------------------------
        # Build contributor list:  (section_name, contributor, priority)
        # ------------------------------------------------------------------
        contributor_specs: List[tuple] = []

        # Mental models (priority 60)
        if self.mental_model_manager and hasattr(self.mental_model_manager, "build_context"):
            contributor_specs.append(("mental_models", self.mental_model_manager, 60))

        # Memory retriever (priority 50) — NEW
        if self.memory_retriever and hasattr(self.memory_retriever, "build_context"):
            contributor_specs.append(("memory", self.memory_retriever, 50))

        # Entity context (priority 40)
        if self.entity_context and hasattr(self.entity_context, "build_context"):
            contributor_specs.append(("entities", self.entity_context, 40))

        # Pattern engine (priority 20)
        if self.pattern_engine and hasattr(self.pattern_engine, "build_context"):
            contributor_specs.append(("entities", self.pattern_engine, 20))

        # Compression summary (priority 10)
        if self.compression_manager and hasattr(self.compression_manager, "build_context"):
            contributor_specs.append(("compression", self.compression_manager, 10))

        contributor_specs.sort(key=lambda x: x[2], reverse=True)

        # ------------------------------------------------------------------
        # Call each contributor — prefer build_context_items() (Spec 02)
        # ------------------------------------------------------------------
        from core.context.relevance_scorer import ScoredEntry
        from core.context.token_counter import TokenCounter
        from core.context_metrics import ContributorMetrics

        # (section_name, priority, List[ScoredEntry])
        raw_items: List[tuple] = []

        for section, contributor, priority in contributor_specs:
            try:
                # Build call kwargs
                call_kw: Dict[str, Any] = dict(kwargs)
                call_kw["token_budget"] = budget_plan.remaining(section) if use_budget else 0

                if section == "mental_models":
                    if "keywords" not in call_kw:
                        call_kw["keywords"] = self._extract_keywords(query)
                    call_kw["domain"] = kwargs.get("domain") or (domains[0] if domains else None)

                if section == "memory" and retrieval_tier is not None:
                    call_kw["retrieval_tier"] = retrieval_tier

                if contributor is self.pattern_engine:
                    call_kw["user_name"] = self.user_name

                if section == "compression":
                    conv_id = kwargs.get("conversation_id") or (
                        f"session_{self.session_start.isoformat()}" if self.session_start else None
                    )
                    if conv_id and hasattr(contributor, "set_current_conversation"):
                        contributor.set_current_conversation(conv_id)

                # --- Per-item protocol (Spec 02) ---
                if hasattr(contributor, "build_context_items"):
                    items = contributor.build_context_items(
                        query, domains, persona=persona, mode=mode, **call_kw
                    )
                    # Apply retrieval tier adjustment per-item
                    if retrieval_tier is not None:
                        try:
                            from core.hardened.classifier import RetrievalTier
                            if retrieval_tier.tier == RetrievalTier.ADJACENT:
                                for item in items:
                                    if item.source in ("entity", "pattern", "mental_model"):
                                        item.raw_score *= 0.7
                        except Exception:
                            pass
                    if items:
                        raw_items.append((section, priority, items))
                else:
                    # Legacy fallback: call build_context and wrap as single ScoredEntry
                    ctx = contributor.build_context(
                        query, domains, persona=persona, mode=mode, **call_kw
                    )
                    if ctx:
                        source_map = {
                            "mental_models": "mental_model",
                            "memory": "memory:stable",
                            "entities": "entity",
                            "compression": "pattern",
                        }
                        source = source_map.get(section, "entity")
                        raw_score = priority / 100.0
                        if retrieval_tier is not None and source in ("entity", "pattern", "mental_model"):
                            try:
                                from core.hardened.classifier import RetrievalTier
                                if retrieval_tier.tier == RetrievalTier.ADJACENT:
                                    raw_score *= 0.7
                            except Exception:
                                pass
                        entry = ScoredEntry(
                            content=ctx,
                            source=source,
                            raw_score=raw_score,
                            composite_score=0.0,
                            token_count=TokenCounter.count(ctx),
                            metadata={"priority": priority, "domain": domains[0] if domains else "general"},
                        )
                        raw_items.append((section, priority, [entry]))

            except Exception as e:
                logger.debug(f"Context contributor {section} (priority {priority}) failed: {e}")

        # ------------------------------------------------------------------
        # Collect contributor metrics for observability (Spec 06)
        # Updated to use real per-item counts from Spec 02
        # ------------------------------------------------------------------
        contributor_metrics: List[ContributorMetrics] = []
        for section, priority, items in raw_items:
            token_count = sum(i.token_count for i in items)
            top_score = max((i.raw_score for i in items), default=priority / 100.0)
            avg_score = (sum(i.raw_score for i in items) / len(items)) if items else priority / 100.0
            contributor_metrics.append(ContributorMetrics(
                contributor=section,
                items_returned=len(items),
                tokens_allocated=0,
                tokens_used=token_count,
                utilisation=1.0 if token_count > 0 else 0.0,
                top_score=top_score,
                avg_score=avg_score,
                items_selected=0,
                items_evicted=0,
            ))

        self._current_contributor_metrics = contributor_metrics

        # ------------------------------------------------------------------
        # If budget system is inactive, fall back to simple concatenation
        # ------------------------------------------------------------------
        if not use_budget:
            raw_items.sort(key=lambda x: x[1], reverse=True)
            return "\n\n".join(
                item.content
                for _, _, items in raw_items
                for item in items
            )

        # ------------------------------------------------------------------
        # Budget-aware path: score → ingest → select via rolling context
        # ------------------------------------------------------------------
        all_scored: List[ScoredEntry] = []
        for section, priority, items in raw_items:
            for item in items:
                try:
                    item.composite_score = self.relevance_scorer.score(
                        item,
                        query_domains=domains,
                        current_turn=self.rolling_context.turn_count,
                    )
                    all_scored.append(item)
                except Exception as e:
                    logger.debug(f"Scoring item from {section} failed: {e}")

        # Ingest into rolling context (handles dedup and decay tracking)
        self.rolling_context.ingest(all_scored)

        # Build section budgets from budget_plan
        section_budgets: Dict[str, int] = {}
        for name in budget_plan.sections:
            section_budgets[name] = budget_plan.remaining(name)

        # Select entries via bin-packing
        selected = self.rolling_context.select(section_budgets)

        # Assemble selected entries and report usage
        parts: List[str] = []
        selected_by_section: Dict[str, int] = {s: 0 for s in section_budgets.keys()}

        for section_name, entries in selected.items():
            for entry in entries:
                parts.append(entry.content)
                budget_plan.report_usage(section_name, entry.token_count)
                selected_by_section[section_name] += 1

        # Update contributor metrics with selection counts
        items_returned_by_section: Dict[str, int] = {}
        tokens_used_by_section: Dict[str, int] = {}
        for section, priority, items in raw_items:
            items_returned_by_section[section] = items_returned_by_section.get(section, 0) + len(items)
            tokens_used_by_section[section] = tokens_used_by_section.get(section, 0) + sum(i.token_count for i in items)

        for cm in contributor_metrics:
            n_selected = selected_by_section.get(cm.contributor, 0)
            cm.items_selected = n_selected
            cm.items_evicted = cm.items_returned - n_selected
            cm.tokens_allocated = section_budgets.get(cm.contributor, 0)
            cm.utilisation = (
                cm.tokens_used / cm.tokens_allocated if cm.tokens_allocated > 0 else 0.0
            )

        self._current_contributor_metrics = contributor_metrics
        self._current_context_total_tokens = sum(cm.tokens_used for cm in contributor_metrics)
        self._current_budget_utilisation = (
            budget_plan.total_used() / budget_plan.total_allocated()
            if budget_plan.total_allocated() > 0 else 0.0
        )

        logger.debug(
            f"Budget-aware context: {len(parts)} entries selected, "
            f"budget used {budget_plan.total_used()}/{budget_plan.total_allocated()}"
        )
        return "\n\n".join(parts)

    def _record_routing_outcome(
        self,
        response_metadata: Dict[str, Any],
        task_type: str = "general",
        persona: Optional[str] = None,
        rag_coverage: Optional[float] = None,
    ) -> None:
        """Record routing decision as ROUTING_OUTCOME pattern for future pattern-informed routing (integration-contracts)."""
        if not self.pattern_engine:
            return
        try:
            from core.patterns.models import Pattern, PatternType, generate_pattern_id
            provider = response_metadata.get("provider", "unknown")
            model = response_metadata.get("model", "")
            name = f"route_{task_type}_{provider}_{model}".replace("/", "_")[:80]
            pid = generate_pattern_id("routing_outcome", name)
            self.pattern_engine.learn(
                Pattern(
                    id=pid,
                    pattern_type=PatternType.ROUTING_OUTCOME,
                    name=name,
                    description=f"{model} for {task_type}",
                    confidence=0.5,
                    metadata={
                        "model": model,
                        "provider": provider,
                        "task_type": task_type,
                        "rag_coverage": rag_coverage,
                        "persona": persona,
                        "tokens_in": response_metadata.get("tokens_in"),
                        "tokens_out": response_metadata.get("tokens_out"),
                        "cost": response_metadata.get("cost"),
                    },
                )
            )
            logger.debug(f"Recorded ROUTING_OUTCOME pattern: {name}")
        except Exception as e:
            logger.debug(f"Record routing outcome failed: {e}")

    def _record_context_metrics(
        self,
        query: str,
        response: str,
        domains: List[str],
        persona: Optional[str],
        response_metadata: Dict[str, Any],
        decomposed: bool = False,
        sub_query_count: int = 0,
    ) -> None:
        """Record context metrics for observability (Spec 06 + 07)."""
        if not self.context_metrics:
            return

        try:
            import json
            from core.context_metrics import ContextTurnRecord

            session_id = f"session_{self.session_start.isoformat()}"
            turn_number = len(self.conversation_history) // 2 + 1

            # Get contributor metrics from _gather_context
            contributors = getattr(self, "_current_contributor_metrics", []) or []

            # Get context tokens from _gather_context
            total_context_tokens = getattr(self, "_current_context_total_tokens", 0)
            budget_utilisation = getattr(self, "_current_budget_utilisation", 0.0)

            # Spec 07: mental model format and reference rate
            mm_format = getattr(self, "_last_mm_format", None)
            mm_reference_rate = getattr(self, "_last_mm_reference_rate", None)

            turn_record = ContextTurnRecord(
                session_id=session_id,
                turn_number=turn_number,
                query_length_tokens=len(query.split()) * 1.3,  # rough token estimate
                response_length_tokens=len(response.split()) * 1.3,
                domains=json.dumps(domains),
                persona=persona,
                model_used=response_metadata.get("model", ""),
                routing_confidence=response_metadata.get("routing_confidence", ""),
                cache_hit=False,  # Will be set by spec-01 when semantic cache is implemented
                cache_similarity=0.0,
                total_context_tokens=total_context_tokens,
                budget_utilisation=budget_utilisation,
                srs_at_turn=None,  # Will be set by spec-04 when semantic compression is implemented
                decomposed=decomposed,
                sub_query_count=sub_query_count,
                mm_format=mm_format,
                mm_reference_rate=mm_reference_rate,
            )

            # RAG metrics (optional - will be enhanced by spec-05)
            rag_metrics = None
            if hasattr(self, "_current_rag_metrics"):
                rag_metrics = self._current_rag_metrics

            self.context_metrics.record_turn(turn_record, contributors, rag_metrics)
            logger.debug(f"Recorded context metrics for turn {turn_number}")

        except Exception as e:
            logger.debug(f"Record context metrics failed: {e}")

    async def _detect_and_suggest_knowledge_gap(
        self,
        query: str,
        rag_results: List,
        cloud_response: str,
        response_metadata: Dict[str, Any],
        retrieval_tier: 'RetrievalTier'
    ) -> None:
        """
        Detect knowledge gaps after cloud responses and suggest saving enriched notes.
        
        Wave 4 - Knowledge Enrichment Integration: This connects the existing gap detection
        infrastructure to the main chat flow. Gap detection runs after synthesis or cloud
        responses to identify when new information should be saved to the knowledge base.
        
        Args:
            query: User's original query
            rag_results: RAG search results that were used
            cloud_response: The response from cloud model (or synthesis)
            response_metadata: Response metadata with provider, model, cost info
            retrieval_tier: Three-tier retrieval classification (DIRECT/ADJACENT/ABSENT)
        """
        # Check if knowledge writer and gap detection are enabled
        if not self.knowledge_writer:
            return
        
        # Check config flag
        gap_detection_enabled = self.config.get("ai_features.knowledge_suggestions.enabled", True)
        if not gap_detection_enabled:
            logger.debug("Knowledge gap detection disabled in config")
            return
        
        # Only detect gaps for cloud responses (local responses use existing KB)
        provider = response_metadata.get("provider", "")
        if provider == "ollama" or (provider == "wave3_hybrid" and response_metadata.get("wave3_metrics", {}).get("cloud_count", 0) == 0):
            # Pure local response - no gap detection needed
            logger.debug(f"Skipping gap detection for pure local response (provider={provider})")
            return
        
        # Import RetrievalTier enum for comparison
        from core.hardened.classifier import RetrievalTier
        
        try:
            # Calculate RAG coverage from retrieval tier or result scores
            # Higher coverage = better local knowledge, lower chance of gap
            rag_coverage = 0.0
            if retrieval_tier and retrieval_tier == RetrievalTier.DIRECT:
                rag_coverage = 0.9  # High coverage - local KB has strong match
            elif retrieval_tier and retrieval_tier == RetrievalTier.ADJACENT:
                rag_coverage = 0.5  # Moderate coverage - related but not direct
            elif retrieval_tier and retrieval_tier == RetrievalTier.ABSENT:
                rag_coverage = 0.1  # Low coverage - KB has little to offer
            else:
                # Fallback: calculate from result scores if available
                if rag_results:
                    scores = [getattr(r, 'score', 0.0) for r in rag_results]
                    rag_coverage = max(scores) if scores else 0.0
                else:
                    rag_coverage = 0.0
            
            logger.debug(f"Gap detection: rag_coverage={rag_coverage:.2f}, retrieval_tier={retrieval_tier}")
            
            # Run gap detection
            gap = await self.knowledge_writer.detect_knowledge_gap(
                original_query=query,
                local_results=rag_results or [],
                cloud_response=cloud_response or "",
                rag_coverage=rag_coverage,
                cloud_provider=provider
            )
            
            if gap:
                logger.info(f"Knowledge gap detected: score={gap.gap_score:.2f}, concepts={len(gap.novel_concepts)}")
                
                # Create suggestion PersonaAction
                suggestion = self.knowledge_writer.create_suggestion(gap)
                
                if suggestion:
                    # Store suggestion for frontend to display
                    # This will be included in the response metadata
                    if not hasattr(self, '_last_persona_actions'):
                        self._last_persona_actions = []
                    self._last_persona_actions.append(suggestion)
                    
                    logger.info(f"Knowledge suggestion created: {gap.suggested_title} ({gap.suggested_domain})")
                    logger.debug(f"Novel concepts: {', '.join(gap.novel_concepts[:5])}")
            else:
                logger.debug("No significant knowledge gap detected")
                
        except Exception as e:
            # Gap detection is non-critical - log but don't fail the query
            logger.warning(f"Knowledge gap detection failed (non-critical): {e}")
            logger.debug(f"Gap detection error details", exc_info=True)

    def _should_use_local_model(
        self, 
        query: str, 
        rag_results: List, 
        provider_override: Optional[str] = None,
        retrieval_tier: Optional['RetrievalTier'] = None,
    ) -> bool:
        """
        Decide whether to use local Ollama model or cloud providers.
        
        Local model is preferred when:
        1. Good RAG context exists (high-scoring results)
        2. Query is straightforward retrieval/summarization
        3. No explicit cloud provider override
        4. Retrieval tier is DIRECT or ADJACENT with a simple query
        5. No RAG results at all (local uses parametric knowledge)
        
        Cloud providers preferred when:
        1. Complex reasoning required (with weak/no RAG)
        2. User explicitly selects cloud provider
        3. Query is analytically complex AND RAG provides no grounding
        
        The retrieval tier is a signal, not an override:
        - DIRECT  → local is ideal (RAG provides strong grounding)
        - ADJACENT → local is fine for simple queries; complex queries may use cloud
        - ABSENT  → local handles via parametric knowledge
        
        Args:
            query: User's query
            rag_results: List of RAG search results
            provider_override: Explicit provider selection
            retrieval_tier: Result of three-tier retrieval classification
            
        Returns:
            True to use local, False to use cloud
        """
        # Rule 1: If user explicitly selected a cloud provider, use cloud
        if provider_override and provider_override != 'local':
            logger.info(f"Using cloud: provider override = {provider_override}")
            return False
        
        # Rule 1.5: Retrieval tier informs routing but is not a hard override.
        # ABSENT: no relevant content found — still try local (model's parametric knowledge).
        # ADJACENT: tangential content — escalate to cloud unless query is trivially simple.
        # DIRECT: trust RAG context, local is ideal.
        if retrieval_tier is not None:
            if retrieval_tier == RetrievalTier.ABSENT:
                logger.info("Retrieval tier ABSENT: will rely on local parametric knowledge")
                print("[Model Routing] Retrieval tier ABSENT: checking local capability", flush=True)
            elif retrieval_tier == RetrievalTier.ADJACENT:
                # Escalate to cloud unless query is trivially simple
                simple_keywords = ['what is', 'define', 'list', 'show me', 'explain']
                query_lower = query.lower()
                is_trivial = any(kw in query_lower for kw in simple_keywords) and len(query_lower) < 40
                if not is_trivial:
                    logger.info("Escalating to cloud: ADJACENT RAG and query not trivially simple")
                    print("[Model Routing] Using CLOUD: ADJACENT RAG, non-trivial query", flush=True)
                    return False
        # Rule 2: Check RAG context quality
        if not rag_results or len(rag_results) == 0:
            logger.info("Using local: No RAG results (parametric knowledge mode)")
            print("[Model Routing] Using LOCAL: no RAG results, parametric knowledge mode", flush=True)
            return True
        
        # Get thresholds from config
        min_top_score = self.config.get("hybrid_routing.thresholds.min_top_score", 0.75)
        min_high_quality_results = self.config.get("hybrid_routing.thresholds.min_high_quality_results", 2)
        min_context_chars = self.config.get("hybrid_routing.thresholds.min_context_chars", 500)
        exceptional_score = self.config.get("hybrid_routing.thresholds.exceptional_score", 0.85)
        exceptional_min_results = self.config.get("hybrid_routing.thresholds.exceptional_min_results", 3)
        
        # Calculate RAG quality score
        # - Top result score (0-1)
        # - Number of high-quality results (score > 0.7)
        # - Total context length
        top_score = rag_results[0].score if rag_results else 0
        high_quality_count = sum(1 for r in rag_results if r.score > 0.7)
        total_context_chars = sum(len(r.chunk.content) for r in rag_results[:10])
        
        logger.info(f"RAG quality: top_score={top_score:.3f}, high_quality_count={high_quality_count}, context_chars={total_context_chars}")
        logger.info(f"Thresholds: min_top={min_top_score}, min_quality={min_high_quality_results}, min_chars={min_context_chars}")
        
        # Strong RAG context thresholds (from config)
        has_strong_rag = (
            top_score > min_top_score and
            high_quality_count >= min_high_quality_results and
            total_context_chars > min_context_chars
        )
        
        # Rule 3: Check query complexity indicators
        complexity_keywords = self.config.get("hybrid_routing.patterns.complexity_keywords", [
            'design', 'architect', 'implement', 'build', 'create',
            'complex', 'advanced', 'optimize', 'refactor',
            'how do i', 'how can i', 'how should i',
            'best way', 'best practice', 'recommend'
        ])
        
        query_lower = query.lower()
        is_complex_query = any(keyword in query_lower for keyword in complexity_keywords)
        
        # Rule 4: Check if it's a simple retrieval query
        retrieval_keywords = self.config.get("hybrid_routing.patterns.retrieval_keywords", [
            'what is', 'what are', 'tell me about', 'show me',
            'list', 'find', 'search', 'look up',
            'do you have', 'what do you know', 'in my notes'
        ])
        is_retrieval_query = any(keyword in query_lower for keyword in retrieval_keywords)
        
        # Decision logic
        if has_strong_rag and is_retrieval_query:
            logger.info("Using local: Strong RAG + retrieval query")
            print("[Model Routing] Using LOCAL: strong RAG + retrieval query", flush=True)
            return True
        elif has_strong_rag and not is_complex_query:
            logger.info("Using local: Strong RAG + simple query")
            print("[Model Routing] Using LOCAL: strong RAG + simple query", flush=True)
            return True
        elif top_score > exceptional_score and high_quality_count >= exceptional_min_results:
            logger.info(f"Using local: Exceptional RAG quality (score={top_score:.3f}, count={high_quality_count})")
            print(f"[Model Routing] Using LOCAL: exceptional RAG (score={top_score:.3f})", flush=True)
            return True
        elif not is_complex_query:
            # Simple query with no strong RAG: local handles via parametric knowledge.
            # Wave 3 already handled truly complex queries; anything reaching here
            # is simple enough that a local model can answer without RAG grounding.
            logger.info("Using local: Simple query — local handles via parametric knowledge")
            print("[Model Routing] Using LOCAL: simple query, parametric knowledge mode", flush=True)
            return True
        else:
            reason = "complex query with weak RAG"
            logger.info(f"Using cloud: {reason}")
            print(f"[Model Routing] Using CLOUD: {reason}", flush=True)
            return False

    def _manage_conversation_context(self) -> None:
        """
        Manage conversation context with automatic compression.
        
        Strategy:
        - Keep last N messages uncompressed for context continuity
        - Compress older messages when threshold reached
        - Store compressed data in compression.db
        
        This method is called before each query to check if compression
        is needed based on message count or age thresholds.
        """
        # Skip if compression is disabled or not initialized
        if not self._compression_enabled or not self.compression_manager:
            return

        # Only compress if we have enough messages
        if len(self.conversation_history) <= self._keep_recent_count:
            return

        # Use updated should_compress() with semantic trigger (Spec 04)
        embed_fn = self.rag.embed_text if (self.rag and hasattr(self.rag, "embed_text")) else None
        should_compress = self.compression_manager.should_compress(
            self.conversation_history,
            conversation_id=f"session_{self.session_start.isoformat()}",
            created_at=self.session_start,
            embed_fn=embed_fn,
        )

        if should_compress:
            elapsed_hours = (datetime.now() - self.session_start).total_seconds() / 3600
            logger.info(
                f"Compression triggered: {len(self.conversation_history)} messages "
                f"({elapsed_hours:.1f}h elapsed)"
            )
            
            # Split conversation: old (to compress) vs recent (keep)
            split_point = len(self.conversation_history) - self._keep_recent_count
            old_messages = self.conversation_history[:split_point]
            recent_messages = self.conversation_history[split_point:]
            
            # Compress old messages
            conversation_id = f"session_{self.session_start.isoformat()}"
            try:
                result = self.compression_manager.compress_conversation(
                    conversation_history=old_messages,
                    conversation_id=conversation_id
                )
                
                logger.info(
                    f"Compressed {len(old_messages)} messages: "
                    f"{result['compressed']['token_stats']['original']} -> "
                    f"{result['compressed']['token_stats']['compressed']} tokens "
                    f"({result['compressed']['token_stats']['ratio']:.1f}x ratio)"
                )
                
                # Feed compressed data to pattern engine for RAG optimization learning
                if self.pattern_engine:
                    try:
                        # Prepare RAG metadata for pattern learning
                        rag_metadata = None
                        if self._rag_metadata['queries']:
                            rag_metadata = {
                                'queries': self._rag_metadata['queries'],
                                'domains': list(self._rag_metadata['domains']),
                                'successful_files': list(self._rag_metadata['successful_files'])
                            }
                            logger.info(f"Passing RAG metadata to pattern engine: {len(rag_metadata['queries'])} queries, {len(rag_metadata['domains'])} domains")
                        
                        learned = self.pattern_engine.learn_from_compressed(
                            compressed_data=result['compressed'],
                            conversation_id=conversation_id,
                            rag_metadata=rag_metadata,
                        )
                        if learned['total'] > 0:
                            logger.info(
                                f"Pattern engine extracted {learned['total']} patterns "
                                f"(query→chunk: {learned.get('query_chunk_patterns', 0)}, "
                                f"domain→collection: {learned.get('domain_priority_patterns', 0)})"
                            )
                        
                        # Reset RAG tracking for next compression cycle
                        self._rag_metadata = {
                            'queries': [],
                            'domains': set(),
                            'successful_files': set()
                        }
                        logger.debug("Reset RAG metadata tracking for next cycle")
                        
                    except Exception as e:
                        logger.warning(f"Failed to feed compressed data to pattern learner: {e}")
                    
                    # Compression→entity integration: extract entities from key concepts and focus topics
                    if self.entity_extractor:
                        try:
                            c = result["compressed"]
                            domains = list(c.get("domains", [])) if isinstance(c.get("domains"), (list, tuple)) else []
                            for concept in c.get("key_concepts", []) or []:
                                text = concept.get("term") or concept.get("definition") or concept.get("concept", "")
                                if isinstance(text, str) and text.strip():
                                    self.entity_extractor.extract_and_store(
                                        text.strip(),
                                        source_type="compression",
                                        source_id=conversation_id,
                                        domains=domains,
                                    )
                            for topic in c.get("focus_topics", []) or []:
                                if isinstance(topic, str) and topic.strip():
                                    self.entity_extractor.extract_and_store(
                                        topic.strip(),
                                        source_type="compression",
                                        source_id=conversation_id,
                                        domains=domains,
                                    )
                        except Exception as ex:
                            logger.debug(f"Compression→entity extraction failed: {ex}")
                
                # Update conversation_history to only keep recent messages
                self.conversation_history = recent_messages
                
            except Exception as e:
                logger.error(f"Compression failed: {e}")
                # Don't modify conversation_history if compression fails
    
    def _build_context_for_llm(self) -> List[Dict]:
        """
        Build message context for LLM including compressed history.
        
        Returns:
            List of messages with compressed summary + recent uncompressed messages
        """
        # Skip if compression is disabled or not initialized
        if not self._compression_enabled or not self.compression_manager:
            return self.conversation_history.copy()
        
        # Try to load compressed history if it exists
        conversation_id = f"session_{self.session_start.isoformat()}"
        try:
            # Use load_context which handles decompression and formatting
            messages = self.compression_manager.load_context(
                conversation_id=conversation_id,
                recent_messages=self.conversation_history
            )
            
            # Check if compressed context was added
            if messages and messages[0].get('compressed'):
                logger.info(f"Added compressed context for conversation")
            
            return messages
        
        except Exception as e:
            # Compression data doesn't exist or failed to load - that's OK
            logger.debug(f"No compressed context available: {e}")
            return self.conversation_history.copy()
    
    # ========== Persona Methods ==========
    
    async def activate_persona(self, persona_name: str, mode: Optional[str] = None) -> Dict:
        """
        Activate a persona for specialized workflows.
        
        Args:
            persona_name: Name of persona to activate (e.g., "architect")
            mode: Optional mode to activate (uses persona default if not specified)
        
        Returns:
            Dict with persona state and introduction message (if first time)
            {
                "persona_name": "professor",
                "current_mode": "socratic",
                "introduction": "Hello! I'm Professor..." (only on first activation)
                ...
            }
        
        Raises:
            RuntimeError: If persona system not initialized
            ValueError: If persona_name is unknown or mode is invalid
        """
        if not self.persona_manager:
            raise RuntimeError("Persona system not initialized. Enable routing_v2 in config.")
        
        state = self.persona_manager.activate_persona(persona_name, mode=mode)
        logger.info(f"Activated {persona_name} persona (mode: {state.current_mode})")
        
        # DEBUG: Log pending introduction state
        logger.info(f"[DEBUG] pending_introduction after activation: {getattr(state, 'pending_introduction', 'NOT SET')}")
        
        # Notify pattern engine, entity context, mental models (integration-contracts)
        self._notify_persona_context(persona_name, state.current_mode or "")
        
        # Convert state to dict and include introduction if present
        state_dict = state.to_dict()
        
        # DEBUG: Log state_dict keys
        logger.info(f"[DEBUG] state_dict keys after to_dict(): {list(state_dict.keys())}")
        
        # Check if there's a pending introduction (Wave 1, Task 2)
        if hasattr(state, 'pending_introduction') and state.pending_introduction:
            logger.info(f"[DEBUG] Adding introduction to response: {state.pending_introduction[:50]}...")
            state_dict["introduction"] = state.pending_introduction
            # Clear it since we're delivering it now
            state.pending_introduction = None
        else:
            logger.info(f"[DEBUG] No pending_introduction to add")
        
        # DEBUG: Final state_dict keys
        logger.info(f"[DEBUG] Final state_dict keys: {list(state_dict.keys())}")
        
        return state_dict
    
    async def process_with_persona(self, user_message: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Process user input with active persona.
        
        Args:
            user_message: User's message
            metadata: Optional metadata (related_notes, etc.)
        
        Returns:
            Dict with PersonaResponse data
        
        Raises:
            RuntimeError: If no persona is active
        """
        if not self.persona_manager:
            raise RuntimeError("Persona system not initialized. Enable routing_v2 in config.")
        
        if not self.persona_manager.is_persona_active():
            raise RuntimeError("No persona is active. Call activate_persona() first.")
        
        from core.personas import PersonaContext
        
        meta = metadata or {}
        # Use conversation_history from request (frontend) when provided; else server-side state
        conv = meta.get("conversation_history")
        conversation_history = list(conv) if conv is not None else self.conversation_history.copy()
        
        context = PersonaContext(
            user_message=user_message,
            conversation_history=conversation_history,
            metadata=meta
        )
        
        response = await self.persona_manager.process(context)
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response.content})
        
        logger.info(f"Processed with {self.persona_manager.get_active_persona_name()} "
                   f"(mode: {response.mode}, actions: {len(response.actions)})")
        
        return response.to_dict()
    
    def switch_persona_mode(self, mode: str) -> Dict:
        """
        Switch active persona to a different mode.
        
        Args:
            mode: Target mode name
        
        Returns:
            Dict with updated persona state
        
        Raises:
            RuntimeError: If no persona is active
            ValueError: If mode is invalid
        """
        if not self.persona_manager:
            raise RuntimeError("Persona system not initialized. Enable routing_v2 in config.")
        
        state = self.persona_manager.switch_mode(mode)
        logger.info(f"Switched persona to {mode} mode")
        # Notify persona-aware systems of new mode (integration-contracts)
        if self.persona_manager.active_persona_name:
            self._notify_persona_context(self.persona_manager.active_persona_name, mode)
        return state.to_dict()
    
    def deactivate_persona(self):
        """Deactivate current persona"""
        if self.persona_manager:
            self.persona_manager.deactivate_persona()
            logger.info("Deactivated persona")
    
    def get_persona_state(self) -> Optional[Dict]:
        """Get current persona state"""
        if not self.persona_manager:
            return None
        return self.persona_manager.get_state_dict()
    
    def list_available_personas(self) -> List[Dict]:
        """Get list of available personas"""
        if not self.persona_manager:
            return []
        from core.personas import PersonaManager
        return PersonaManager.list_available_personas()

    async def query(
        self,
        query: str,
        context: Optional[Dict] = None,
        mode: Optional[RoutingMode] = None,
        tier: Optional[ModelTier] = None,
        stream: bool = True,
        confidence: Optional[str] = None,  # NEW: "fast", "balanced", "thorough"
        provider_override: Optional[str] = None,  # NEW: "openai", "anthropic", "github", None
        page: Optional[str] = None,  # NEW (Phase 14): Current page/view
        persona: Optional[str] = None,  # NEW (Phase 14): Active persona
        persona_mode: Optional[str] = None,  # NEW (Phase 14): Active mode within persona
        mental_models_override: Optional[List[str]] = None  # NEW (Phase 14): Override active models
    ) -> AsyncIterator[str]:
        """
        Process a query and generate a response.

        This is the main entry point for Polly. It:
        1. Detects relevant domains
        2. Retrieves context from RAG
        3. Gets relevant patterns and graph context
        4. Activates relevant mental models (Phase 14)
        5. Routes to appropriate model
        6. Generates response

        Args:
            query: The user's query
            context: Optional additional context (e.g., current file)
            mode: Override routing mode (local/cloud/auto) [v1 only]
            tier: Override model tier (fast/balanced/quality) [v1 only]
            stream: Whether to stream the response
            confidence: Router v2 tier ("fast"/"balanced"/"thorough")
            provider_override: Force specific provider in router v2
            page: Current page/view for mental model activation
            persona: Active persona for mental model activation
            persona_mode: Active mode within persona
            mental_models_override: List of model IDs to force active (overrides automatic activation)

        Yields:
            Response text (chunks if streaming)
        """
        logger.info(f"[POLLY QUERY] Starting query: {query[:100]}")
        
        # Clear persona actions from previous query
        self._last_persona_actions = []

        # ------------------------------------------------------------------
        # 0. Semantic Cache Lookup (Spec 01) - short-circuit if cache hit
        # ------------------------------------------------------------------
        cache_hit_data = None
        if self.semantic_cache:
            try:
                cache_hit = self.semantic_cache.lookup(
                    query=query,
                    persona=persona,
                    domain=domain_names[0] if domain_names else None,
                )
                if cache_hit:
                    logger.info(
                        f"Semantic cache HIT: similarity={cache_hit.similarity:.3f}, "
                        f"age={cache_hit.age_hours:.1f}h"
                    )
                    cache_hit_data = cache_hit
            except Exception as e:
                logger.debug(f"Cache lookup failed: {e}")

        # ------------------------------------------------------------------
        # Resolve active persona when not passed (e.g. caller didn't send persona from UI)
        # ------------------------------------------------------------------
        if persona is None and self.persona_manager and self.persona_manager.is_persona_active():
            persona = self.persona_manager.get_active_persona_name()
            persona_mode = persona_mode or self.persona_manager.get_current_mode() or ""
        else:
            persona_mode = persona_mode or ""

        # If we have a cache hit, we can skip most processing and just return it
        if cache_hit_data:
            # Still do domain detection for logging/metrics but skip RAG/model
            detected_domains = self.domains.detect_domains(query, context)
            domain_names = [d for d in detected_domains if (d or "").strip().lower() not in ("", "unknown")]
            
            # Yield the cached response
            yield cache_hit_data.response
            
            # Record metrics for cache hit
            if self.context_metrics:
                from core.context_metrics import ContextTurnRecord, ContributorMetrics
                import json
                session_id = f"session_{self.session_start.isoformat()}"
                turn_number = len(self.conversation_history) // 2 + 1
                
                turn_record = ContextTurnRecord(
                    session_id=session_id,
                    turn_number=turn_number,
                    query_length_tokens=len(query.split()) * 1.3,
                    response_length_tokens=len(cache_hit_data.response.split()) * 1.3,
                    domains=json.dumps(domain_names),
                    persona=persona,
                    model_used=cache_hit_data.metadata.get("model", "cached"),
                    routing_confidence="",
                    cache_hit=True,
                    cache_similarity=cache_hit_data.similarity,
                    total_context_tokens=0,
                    budget_utilisation=0.0,
                    srs_at_turn=None,
                    decomposed=False,
                    sub_query_count=0,
                )
                self.context_metrics.record_turn(turn_record, [], None)
            
            # Update conversation history with cached response
            self.conversation_history.append({'role': 'user', 'content': query})
            self.conversation_history.append({'role': 'assistant', 'content': cache_hit_data.response})
            return

        # 1. Detect domains (list of domain ids)
        detected_domains = self.domains.detect_domains(query, context)
        domain_names = [d for d in detected_domains if (d or "").strip().lower() not in ("", "unknown")]

        # Notify persona-aware systems (integration-contracts)
        self._notify_persona_context(persona, persona_mode)
        
        domain_scores = self.domains.detect_domains_with_scores(query, context)
        logger.info(f"Detected domains: {[(d, f'{s:.2f}') for d, s in domain_scores[:3]]}")
        
        if domain_names:
            self.domains.record_successful_detection(query, detected_domains, user_accepted=True)


        # 2. Get RAG context
        # Increase n_results for integration-heavy queries
        n_results = self.config.get("rag.n_results", 5)
        query_lower = query.lower()
        
        integration_keywords = ['github', 'repository', 'repositories', 'repos', 'repo', 'integration', 'integrations', 'pull request', 'issue', 'sync', 'synced']
        # Use word boundaries to avoid matching 'pr' in 'practices'
        import re
        is_integration_query = any(
            re.search(r'\b' + re.escape(keyword) + r'\b', query_lower) 
            for keyword in integration_keywords
        )
        
        # Also check recent conversation history (last 2 messages) for integration context
        if not is_integration_query and self.conversation_history:
            recent_messages = self.conversation_history[-4:]  # Last 2 exchanges (user + assistant)
            recent_text = ' '.join(msg.get('content', '').lower() for msg in recent_messages)
            is_integration_query = any(
                re.search(r'\b' + re.escape(keyword) + r'\b', recent_text) 
                for keyword in integration_keywords
            )
        
        # Always determine model_tier for downstream use (max_context_tokens, compression)
        model_tier = self._estimate_model_tier(confidence)

        if is_integration_query:
            n_results = 30  # Get more results per collection for integration queries
        else:
            # Tier-aware n_results: fewer chunks for small local context windows,
            # more for cloud models with large context.  Uses routing confidence as
            # a pre-routing tier estimate (FAST→local_fast, BALANCED→local_balanced,
            # THOROUGH→cloud).
            tier_n = {
                "local_fast":     self.config.get("rag.tier_n_results.local_fast", 3),
                "local_balanced": self.config.get("rag.tier_n_results.local_balanced", 5),
                "cloud":          self.config.get("rag.tier_n_results.cloud", 10),
            }
            n_results = tier_n.get(model_tier, n_results)

        # For ambiguous follow-up queries, use previous user query for RAG search
        search_query = query
        if query_lower in ['what about now?', 'and now?', 'how about now?', 'now?', 'still?']:
            # Look for previous user message
            for msg in reversed(self.conversation_history):
                if msg.get('role') == 'user':
                    search_query = msg.get('content', query)
                    logger.info(f"Using previous query for RAG search: {search_query}")
                    break
        
        # Special case: if user wants ALL GitHub repos, we need to fetch them differently
        # Semantic search won't find all repos because the query "list all repos" doesn't match repo content
        # This applies to:
        # - Explicit "list all" queries
        # - Questions about patterns/themes across repos
        # - Any analysis of "my repositories" (plural)
        fetch_all_github_repos = (
            is_integration_query and 
            'github' in query_lower and 
            (
                ('all' in query_lower and ('repo' in query_lower or 'repositor' in query_lower)) or
                ('my' in query_lower and ('repos' in query_lower or 'repositories' in query_lower)) or
                ('pattern' in query_lower or 'theme' in query_lower or 'across' in query_lower)
            )
        )
        
        if fetch_all_github_repos:
            logger.info("Fetching ALL GitHub repos directly (bypassing semantic search)")
            # Use direct metadata query instead of semantic search
            # CRITICAL: Run in thread pool to avoid blocking event loop
            import asyncio
            rag_results = await asyncio.to_thread(self.rag.get_all_github_repos)
            logger.info(f"Retrieved {len(rag_results)} GitHub repos")
        else:
            # Phase 13A Days 12-13: Expand query using conceptual patterns
            expanded_query = search_query
            expansion_concepts = []
            used_pattern_id = None  # Track which pattern was used for expansion
            
            if self.pattern_engine:
                try:
                    # Extract key concepts from query
                    query_concepts = set(search_query.lower().split())
                    
                    # Find conceptual patterns that match query concepts
                    # Look for high-confidence patterns (≥ 0.6) to avoid noise
                    for pattern in self.pattern_engine.patterns.values():
                        pt = pattern.pattern_type
                        pt_val = pt.value if hasattr(pt, 'value') else pt
                        if pt_val != 'conceptual' or pattern.confidence < 0.6:
                            continue
                        
                        concept1 = pattern.metadata.get('concept1', '').lower()
                        concept2 = pattern.metadata.get('concept2', '').lower()
                        
                        # If either concept is in query, add the other for expansion
                        if concept1 in query_concepts and concept2 not in query_concepts:
                            expansion_concepts.append(concept2)
                            used_pattern_id = pattern.id
                            logger.info(f"Query expansion: '{concept1}' → '{concept2}' (from pattern, confidence={pattern.confidence:.2f})")
                            break  # Only expand with one concept to avoid noise
                        elif concept2 in query_concepts and concept1 not in query_concepts:
                            expansion_concepts.append(concept1)
                            used_pattern_id = pattern.id
                            logger.info(f"Query expansion: '{concept2}' → '{concept1}' (from pattern, confidence={pattern.confidence:.2f})")
                            break
                    
                    if expansion_concepts:
                        expanded_query = f"{search_query} {expansion_concepts[0]}"
                        logger.info(f"Expanded query: '{search_query}' → '{expanded_query}'")
                        
                        # Record pattern usage
                        if used_pattern_id:
                            self.pattern_engine.record_pattern_usage(used_pattern_id, was_helpful=True)
                
                except Exception as e:
                    logger.warning(f"Query expansion failed: {e}")
            
            # Phase 13A Days 9-11: Pass detected domains to enable priority-based collection filtering
            # Phase 13A Days 12-13: Use expanded query for better results
            # CRITICAL: Run RAG search in thread pool to avoid blocking event loop
            import asyncio
            rag_results = await asyncio.to_thread(
                self.rag.search,
                query=expanded_query,  # Use expanded query instead of original
                n_results=n_results,
                domains=domain_names if domain_names else None
            )
        
        # Store retrieved chunks for per-turn reinforcement (Spec 05)
        self._current_turn_chunks = rag_results[:20] if rag_results else []

        # Learn domain→collection priorities from search results
        if self.pattern_engine and rag_results and domain_names and not fetch_all_github_repos:
            try:
                # Group results by collection to calculate performance
                collection_results = {}
                
                for result in rag_results[:20]:  # Consider top 20 results
                    coll = result.chunk.source_type
                    if coll not in collection_results:
                        collection_results[coll] = []
                    collection_results[coll].append(result.score)
                
                # Calculate max score per collection (best result from that collection)
                collection_scores = {
                    coll: max(scores) 
                    for coll, scores in collection_results.items()
                }
                
                # Also record 0.0 score for collections that were searched but returned nothing
                all_searched_collections = self.rag.collections.keys()
                for coll in all_searched_collections:
                    if coll not in collection_scores:
                        collection_scores[coll] = 0.0
                
                # Learn priorities for each detected domain
                for domain in domain_names:
                    self.pattern_engine.learn_domain_priorities(
                        query=query,
                        domain=domain,
                        collection_scores=collection_scores,
                    )
                    logger.debug(f"Learned domain priorities for '{domain}' from {len(collection_scores)} collections")
            except Exception as e:
                logger.error(f"Failed to learn domain priorities: {e}")
        
        # Phase 2 Enhancement: Track RAG metadata for pattern learning
        if rag_results and not fetch_all_github_repos:
            try:
                # Track top chunks (limit to top 5 to avoid noise)
                top_chunks = [result.chunk.id for result in rag_results[:5]]
                
                # Track collections that were searched
                collections_used = list(set(result.chunk.source_type for result in rag_results[:10]))
                
                # Track successful files
                for result in rag_results[:5]:
                    if result.chunk.filepath:
                        self._rag_metadata['successful_files'].add(result.chunk.filepath)
                
                # Record this query
                self._rag_metadata['queries'].append({
                    'query': query,
                    'chunks': top_chunks,
                    'collections': collections_used
                })
                
                # Accumulate domains
                if domain_names:
                    self._rag_metadata['domains'].update(domain_names)
                
                logger.debug(f"📊 Tracked RAG metadata: {len(top_chunks)} chunks, {len(collections_used)} collections, domains={domain_names}")
            except Exception as e:
                logger.warning(f"Failed to track RAG metadata: {e}")
        
        # Pattern-based retrieval boosting
        # Boost RAG results that match learned patterns
        if self.pattern_engine and rag_results:
            try:
                # Get relevant patterns for this query
                relevant_patterns = self._get_patterns_for_prompt(query, detected_domains, limit=10)
                
                if relevant_patterns:
                    # Extract pattern keywords for matching
                    pattern_keywords = set()
                    for pattern in relevant_patterns:
                        # Add words from pattern name and description
                        pattern_keywords.update(pattern.name.lower().split())
                        pattern_keywords.update(pattern.description.lower().split())
                        
                        # For code patterns, add example code keywords
                        if pattern.pattern_type == "code" and pattern.examples:
                            for example in pattern.examples[:2]:
                                # Extract meaningful words from code (simple approach)
                                code_words = [w for w in example.lower().split() if len(w) > 3]
                                pattern_keywords.update(code_words[:10])
                    
                    # Remove common words
                    stopwords = {'the', 'this', 'that', 'with', 'from', 'have', 'your', 'you', 'how', 'what', 'when', 'where'}
                    pattern_keywords -= stopwords
                    
                    # Boost results that match pattern keywords
                    boosted_count = 0
                    for result in rag_results:
                        result_text = (result.chunk.content + " " + result.chunk.filepath).lower()
                        
                        # Count keyword matches
                        matches = sum(1 for kw in pattern_keywords if kw in result_text)
                        
                        if matches > 0:
                            # Boost score based on number of matches
                            boost_factor = 1.0 + (matches * 0.05)  # 5% boost per match, max 50%
                            boost_factor = min(boost_factor, 1.5)
                            result.score = min(result.score * boost_factor, 0.98)  # Cap at 0.98 to not override critical boosts
                            boosted_count += 1
                    
                    if boosted_count > 0:
                        logger.info(f"Pattern-based boost applied to {boosted_count} results")
                        # Re-sort after boosting
                        rag_results.sort(key=lambda r: r.score, reverse=True)
            except Exception as e:
                logger.error(f"Failed to apply pattern-based boosting: {e}")
        
        # Boost integration results ONLY if this is an integration-specific query
        if is_integration_query:
            github_specific = any(word in query_lower for word in ['github', 'repository', 'repositories', 'repos', 'repo'])
            
            for result in rag_results:
                # Boost results from integration collections or with github source metadata
                if (result.chunk.source_type.startswith('integration_') or 
                    result.chunk.metadata.get('source') == 'github'):
                    # For GitHub-specific queries, give MASSIVE boost to ensure they appear
                    if github_specific:
                        result.score = 0.99  # Force to top
                    else:
                        result.score = min(result.score * 1.5, 1.0)  # Normal boost
            
            # Re-sort after boosting
            rag_results.sort(key=lambda r: r.score, reverse=True)
        
        # Save original search results before filtering
        rag_results_original = rag_results

        # Skip domain filtering for integration queries to ensure GitHub/integration data is visible
        if is_integration_query:
            logger.info("Skipping domain filtering for integration query")
            filtered_search_results = rag_results_original
            
            # Special case: if asking specifically about listing GitHub repos, ONLY include GitHub repos
            if 'github' in query_lower and ('list' in query_lower or 'all' in query_lower) and ('repo' in query_lower or 'repositor' in query_lower):
                logger.info("GitHub repo listing query - filtering to ONLY GitHub repos")
                filtered_search_results = [
                    r for r in rag_results_original 
                    if (r.chunk.source_type.startswith('integration_') or 
                        r.chunk.metadata.get('source') == 'github')
                ]
                logger.info(f"Filtered to {len(filtered_search_results)} GitHub-only results")
        else:
            # Filter by domain relevance
            rag_results = self.domains.filter_sources_by_domain(
                [{'filepath': r.chunk.filepath, 'content': r.chunk.content} for r in rag_results_original],
                domain_ids=detected_domains,
            )
            
            # Convert filtered results back to SearchResult objects for formatting
            # Keep original rag_results and match by filepath
            filtered_search_results = [
                r for r in rag_results_original 
                if any(r.chunk.filepath == s['filepath'] for s in rag_results)
            ]
        
        # Tier-aware max context tokens: integration queries need full budget;
        # otherwise scale to the model's likely context window.
        if is_integration_query:
            max_context_tokens = 8000
        else:
            tier_ctx = {
                "local_fast":     self.config.get("rag.tier_max_context_tokens.local_fast", 2000),
                "local_balanced": self.config.get("rag.tier_max_context_tokens.local_balanced", 3000),
                "cloud":          self.config.get("rag.tier_max_context_tokens.cloud", 6000),
            }
            max_context_tokens = tier_ctx.get(model_tier, 3000)
        
        # Use compact format ONLY if explicitly listing repos (not for analysis queries)
        use_compact_format = (
            fetch_all_github_repos if 'fetch_all_github_repos' in locals() else False
        ) and ('list' in query_lower or 'show' in query_lower)
        
        # Debug: log what we're formatting
        if is_integration_query:
            github_count = sum(1 for r in filtered_search_results if (
                r.chunk.source_type.startswith('integration_') or 
                r.chunk.metadata.get('source') == 'github'
            ))
            logger.info(f"Formatting {len(filtered_search_results)} results ({github_count} GitHub) for context")
        
        rag_context = self.rag.format_context(
            filtered_search_results,
            max_tokens=max_context_tokens,
            compact_github=use_compact_format
        )

        # RAG context compression for local models (#23 RAG Optimization).
        # Only compresses when context is large and model tier is local.
        # Skipped for integration queries (GitHub/repo content degrades badly with LLMLingua).
        if (
            not is_integration_query
            and self.compression_manager
            and self.config.get("rag.rag_compression.enabled", True)
            and model_tier != "cloud"
        ):
            min_chars = self.config.get("rag.rag_compression.min_chars", 1500)
            if len(rag_context) > min_chars:
                ratio_key = f"rag.rag_compression.{model_tier}_ratio"
                target_ratio = self.config.get(ratio_key, 0.5)
                try:
                    compressed = self.compression_manager.compress_text(
                        rag_context,
                        target_ratio=target_ratio,
                        context_type="rag_context",
                    )
                    if compressed and compressed.get("compressed_text"):
                        orig_len = len(rag_context)
                        rag_context = compressed["compressed_text"]
                        logger.info(
                            f"RAG context compressed {orig_len}→{len(rag_context)} chars "
                            f"(tier={model_tier}, ratio={target_ratio})"
                        )
                except Exception as _e:
                    logger.debug(f"RAG context compression skipped: {_e}")

        # Debug: Log for Practices queries
        if 'practices' in query_lower and 'exercises' in query_lower:
            practices_count = sum(1 for r in filtered_search_results if 'Practices' in r.chunk.filepath and 'Exercises' in r.chunk.filepath)
            logger.info(f"PRACTICES QUERY DEBUG:")
            logger.info(f"  - Filtered results: {len(filtered_search_results)}")
            logger.info(f"  - Practices chunks: {practices_count}")
            logger.info(f"  - RAG context length: {len(rag_context)} chars")
            logger.info(f"  - 'PRACTICE' mentions in context: {rag_context.count('PRACTICE')}")
            logger.info(f"  - Context preview: {rag_context[:300]}...")
        
        # Debug: Check if GitHub repos are in the formatted context
        # Only debug user queries, not title generation
        is_title_query = 'generate a short' in query_lower or 'descriptive title' in query_lower
        if is_integration_query and 'github' in query_lower and not is_title_query:
            has_github = 'github' in rag_context.lower() or 'repository' in rag_context.lower()
            logger.info(f"RAG context has GitHub content: {has_github}, length: {len(rag_context)} chars")
            if has_github:
                # Log first 500 chars to see what's there
                logger.info(f"Context preview: {rag_context[:500]}...")
            
            # Write detailed debug info to file
            import os
            debug_file = os.path.expanduser("~/.polly/debug_github_context.txt")
            with open(debug_file, "w") as f:
                f.write(f"=== GitHub Query Debug - {datetime.now()} ===\n\n")
                f.write(f"Query: {query}\n\n")
                f.write(f"Total filtered results: {len(filtered_search_results)}\n")
                f.write(f"GitHub results: {github_count}\n\n")
                f.write("=== Filtered Search Results ===\n")
                for i, r in enumerate(filtered_search_results[:10]):
                    f.write(f"\n[{i}] Score: {r.score:.3f}\n")
                    f.write(f"Source: {r.chunk.source_type}\n")
                    f.write(f"Metadata: {r.chunk.metadata}\n")
                    f.write(f"Content: {r.chunk.content[:200]}...\n")
                f.write(f"\n\n=== Formatted RAG Context ({len(rag_context)} chars) ===\n")
                f.write(rag_context)
                # Save this for later when we build the full prompt
                self._debug_file = debug_file
                self._debug_query = query_lower
            logger.info(f"Debug info written to {debug_file}")

        # 2.5. Classify retrieval quality using three-tier system (DIRECT/ADJACENT/ABSENT)
        # This determines how strongly the LLM should rely on RAG results
        retrieval_classifier = RetrievalClassifier(
            direct_threshold=self.config.get("rag.retrieval_classifier.direct_threshold", 0.72),
            adjacent_threshold=self.config.get("rag.retrieval_classifier.adjacent_threshold", 0.5),
            domain_match_boost=self.config.get("rag.retrieval_classifier.domain_match_boost", 0.1),
            cross_domain_penalty=self.config.get("rag.retrieval_classifier.cross_domain_penalty", 0.15),
        )
        classifier_results_dicts = [
            {
                "score": r.score,
                "content": r.chunk.content,
                "domain": r.domain or r.chunk.source_type or "",
            }
            for r in filtered_search_results
        ]
        retrieval_tier = retrieval_classifier.classify(
            query=query,
            results=classifier_results_dicts,
            validations=None,  # TODO: integrate DualValidator when available
            query_domains=domain_names,
        )
        print(
            f"[Retrieval Tier] {retrieval_tier.tier.value.upper()} "
            f"(confidence={retrieval_tier.confidence:.3f}, "
            f"results={len(retrieval_tier.results)}, "
            f"reason={retrieval_tier.reason})",
            flush=True,
        )
        logger.info(
            f"Retrieval tier: {retrieval_tier.tier.value} "
            f"(confidence={retrieval_tier.confidence:.3f}, "
            f"results={len(retrieval_tier.results)}, "
            f"reason={retrieval_tier.reason})"
        )

        # 3. Allocate context budget (if budget allocator available)
        budget_plan = None
        if self.budget_allocator:
            try:
                from core.context.token_counter import TokenCounter
                # Estimate conversation tokens from history
                conv_text = " ".join(
                    msg.get("content", "") for msg in self.conversation_history
                )
                conversation_tokens = TokenCounter.count(conv_text) if conv_text else 0

                budget_plan = self.budget_allocator.allocate(
                    conversation_tokens=conversation_tokens,
                )
                logger.debug(f"Budget plan created:\n{budget_plan.summary()}")
            except Exception as e:
                logger.warning(f"Budget allocation failed, using unbounded context: {e}")
                budget_plan = None

        # 4. Gather context from all contributors (integration-contracts: ContextContributor)
        # NOTE: _gather_context is synchronous and calls blocking I/O (Mem0 search,
        # ChromaDB queries, SQLite reads). Run in thread pool to avoid blocking
        # the async event loop, which would stall concurrent async operations
        # like the LiteLLM acompletion() call.
        gathered_context = await asyncio.to_thread(
            self._gather_context,
            query,
            domain_names,
            persona=persona,
            mode=persona_mode,
            budget_plan=budget_plan,
            retrieval_tier=retrieval_tier,
            domain=domain_names[0] if domain_names else None,
            page=page,
            override_model_ids=mental_models_override,
            conversation_id=f"session_{self.session_start.isoformat()}" if self.session_start else None,
            model_used="",  # Not yet known; _select_format uses A/B + static profiles (Spec 07)
        )

        # Capture mm_format selected during _gather_context (Spec 07)
        self._last_mm_format = (
            self.mental_model_manager._last_mm_format
            if self.mental_model_manager
            else "compact"
        )

        # Track which mental models were activated for effectiveness logging (integration-contracts)
        if self.mental_model_manager:
            try:
                if mental_models_override:
                    self._last_activated_mental_model_ids = mental_models_override
                else:
                    keywords = self._extract_keywords(query)
                    domain = domain_names[0] if domain_names else None
                    models = self.mental_model_manager.get_models_for_context(
                        domain=domain,
                        page=page,
                        persona=persona,
                        persona_mode=persona_mode,
                        keywords=keywords,
                        enabled_only=True,
                    )
                    self._last_activated_mental_model_ids = [m.id for m in models]
            except Exception as e:
                logger.debug(f"Mental model activation tracking failed: {e}")
                self._last_activated_mental_model_ids = []
        else:
            self._last_activated_mental_model_ids = []

        # 4. Build augmented prompt
        # Include cross-domain connections in the domain prompt for multi-domain queries
        domain_prompt = self.domains.get_domain_prompt(detected_domains, include_cross_domain=True)
        
        # Check if we have integration data in the context
        integration_note = ""
        if "Your Connected GitHub Account" in rag_context:
            # Count how many repos are in the context
            github_repo_count = rag_context.count("Your Connected GitHub Account - Repository:")
            if 'github' in query_lower and ('repo' in query_lower or 'repositor' in query_lower):
                integration_note = f"\n\n**CRITICAL**: The user is asking about GitHub repositories. The context below lists {github_repo_count} repositories from their connected GitHub account. These ARE the repositories they're asking about. List them directly from the context below - do NOT give generic instructions about using the GitHub API or web interface.\n"
            else:
                integration_note = "\n\n**IMPORTANT**: The context below includes data from the user's connected GitHub account. This is live data from their actual repositories.\n"
        
        # Log what RAG found for debugging
        if rag_context:
            logger.info(f"RAG context retrieved ({len(rag_context)} chars)")
            # Log first 200 chars to see what was found
            logger.info(f"RAG preview: {rag_context[:200]}...")
        else:
            logger.warning("No RAG context found for query")

        # Special instructions for Practices queries
        practices_instruction = ""
        if 'practices' in query_lower and 'exercises' in query_lower:
            practices_instruction = """

**CRITICAL INSTRUCTION FOR THIS QUERY**: The user is asking about their "Practices and Exercises" framework. The context above contains the ACTUAL practices (PRACTICE 1-10) and exercises (Exercise X.Y) from their document. You MUST:

1. Reference the EXACT practice and exercise names from the context (e.g., "PRACTICE 2: Compose and Compost", "Exercise 3.1: Single-Parameter Instrument")
2. Quote or paraphrase the ACTUAL exercise descriptions provided in the context
3. DO NOT invent new exercises or practices
4. DO NOT give generic advice like "take a walk" or "practice mindfulness" unless that's literally what the exercise says

If you suggest an exercise, copy the description directly from the context above."""

        # Build tier-aware RAG instructions based on retrieval classification
        if retrieval_tier.tier == RetrievalTier.DIRECT:
            # High-confidence matches — trust and prioritize RAG content
            rag_header = f"## Context from {self.user_name}'s Knowledge Base{integration_note}"
            rag_instruction = (
                f"**IMPORTANT**: The context below contains information from {self.user_name}'s "
                f"actual notes and knowledge base. You MUST reference and use this specific "
                f"information when answering questions. If the user asks about a topic covered "
                f"in the context, draw directly from those notes."
            )
            rag_footer = (
                "When answering questions, prioritize information from the knowledge base "
                "context above. Cite specific notes and details when available."
            )
        elif retrieval_tier.tier == RetrievalTier.ADJACENT:
            # Tangential matches — present as related context, don't constrain the LLM
            rag_header = f"## Related Context from {self.user_name}'s Knowledge Base{integration_note}"
            rag_instruction = (
                f"The context below contains information from {self.user_name}'s notes that is "
                f"**related but not directly on-topic** for this query. Use it as background "
                f"if relevant, but this topic may require broader analysis beyond what's in "
                f"the knowledge base."
            )
            rag_footer = (
                "Draw on your general knowledge and training to answer this question thoroughly. "
                "Reference the knowledge base context where it's genuinely relevant, but don't "
                "force connections that aren't there."
            )
        else:
            # ABSENT — no relevant matches, free the LLM to use its own knowledge
            rag_header = f"## {self.user_name}'s Knowledge Base"
            rag_instruction = (
                f"No directly relevant notes were found in {self.user_name}'s knowledge base "
                f"for this query."
            )
            rag_footer = (
                "Answer this question using your general knowledge and training. "
                "Be thorough and analytical."
            )

        rag_content = rag_context if rag_context else "No directly relevant notes found."

        augmented_system = f"""{self._build_system_prompt()}

{domain_prompt}

{rag_header}

{rag_instruction}

{rag_content}

{gathered_context}

{rag_footer}{practices_instruction}
"""

        # Debug: Save the full augmented system prompt for GitHub queries
        if hasattr(self, '_debug_file') and hasattr(self, '_debug_query'):
            if 'github' in self._debug_query and ('repo' in self._debug_query or 'repositor' in self._debug_query):
                with open(self._debug_file, "a") as f:
                    f.write(f"\n\n=== FULL AUGMENTED SYSTEM PROMPT ({len(augmented_system)} chars) ===\n")
                    f.write(augmented_system)
                    f.write(f"\n\n=== USER QUERY ===\n{query}\n")
            # Clean up
            delattr(self, '_debug_file')
            delattr(self, '_debug_query')

        # 6. Manage conversation context (compress if needed)
        # NOTE: Sync method with blocking SQLite I/O — offload to thread pool
        await asyncio.to_thread(self._manage_conversation_context)

        # 7. Build messages with compressed context
        # NOTE: Sync method with blocking SQLite read — offload to thread pool
        messages = await asyncio.to_thread(self._build_context_for_llm)
        messages.append({'role': 'user', 'content': query})

        # 7.5. Wave 3 Pipeline: Query Decomposition → Split Routing → Synthesis
        # Check if query should be decomposed and routed via Wave 3 pipeline
        wave3_enabled = (
            self.query_decomposer is not None and 
            self.split_router is not None and 
            self.synthesizer is not None
        )
        
        logger.info(f"Wave 3 check: decomposer={self.query_decomposer is not None}, split_router={self.split_router is not None}, synthesizer={self.synthesizer is not None}, enabled={wave3_enabled}")
        
        if wave3_enabled:
            logger.info("Wave 3 pipeline is enabled, attempting decomposition...")
            try:
                # Decompose query if complex
                decomposition_result = await self.query_decomposer.decompose(
                    query=query,
                    context={
                        'domains': domain_names
                        # Note: Don't pass rag_results or messages - they contain non-serializable objects
                    }
                )
                
                logger.info(f"Wave 3: Decomposition complete, is_complex={decomposition_result.is_complex}")
                
                # If query was decomposed (is_complex=True), use Wave 3 pipeline
                if decomposition_result.is_complex:
                    logger.info(f"Wave 3: Query decomposed into {len(decomposition_result.sub_queries)} sub-queries")
                    logger.info(f"Wave 3: Reasoning: {decomposition_result.reasoning}")
                    
                    # Route sub-queries through split router (handles parallel execution)
                    routing_result = await self.split_router.route(
                        decomposition=decomposition_result,
                        context={
                            'rag_results': filtered_search_results,
                            'system_prompt': augmented_system,
                            'messages': messages,
                            'domains': domain_names
                        }
                    )
                    
                    # Synthesize responses from sub-queries
                    synthesis_result = await self.synthesizer.synthesize(
                        routing_result=routing_result,
                        context={'rag_context': rag_context}
                    )
                    
                    # Log Wave 3 metrics
                    logger.info(f"Wave 3 complete: {routing_result.local_count} local, {routing_result.cloud_count} cloud")
                    logger.info(f"Wave 3 cost: ${routing_result.total_cost:.4f}")
                    
                    # Stream the synthesized response (simulate streaming for UX)
                    full_response = synthesis_result.synthesized_response
                    if stream:
                        # Chunk the response for streaming
                        chunk_size = 50  # chars per chunk
                        for i in range(0, len(full_response), chunk_size):
                            chunk = full_response[i:i+chunk_size]
                            yield chunk
                            await asyncio.sleep(0.01)  # Small delay for streaming effect
                    else:
                        yield full_response
                    
                    # Set metadata from Wave 3 routing
                    response_metadata = {
                        'provider': 'wave3_hybrid',
                        'model': f"{routing_result.local_count}×local + {routing_result.cloud_count}×cloud",
                        'cost': routing_result.total_cost,
                        'tokens_in': routing_result.total_tokens // 2,  # Rough estimate
                        'tokens_out': routing_result.total_tokens // 2,
                        'estimated': True,
                        'routing_reason': f"Wave 3 decomposed query: {decomposition_result.reasoning}",
                        'wave3_metrics': {
                            'sub_queries': len(decomposition_result.sub_queries),
                            'local_count': routing_result.local_count,
                            'cloud_count': routing_result.cloud_count,
                            'total_cost': routing_result.total_cost
                        }
                    }
                    self._last_response_metadata = response_metadata
                    
                    # Knowledge gap detection for Wave 3 synthesis (Wave 4 Integration)
                    await self._detect_and_suggest_knowledge_gap(
                        query=query,
                        rag_results=filtered_search_results,
                        cloud_response=full_response,
                        response_metadata=response_metadata,
                        retrieval_tier=retrieval_tier.tier
                    )
                    
                    # Update conversation history for Wave 3 path
                    self.conversation_history.append({'role': 'user', 'content': query})
                    self.conversation_history.append({'role': 'assistant', 'content': full_response})

                    # Rolling context turn tracking for Wave 3 path
                    if self.rolling_context:
                        try:
                            self.rolling_context.on_new_turn(
                                query, full_response, query_domains=domain_names
                            )
                        except Exception as e:
                            logger.debug(f"Rolling context turn tracking (Wave 3) failed: {e}")

                    # Early return - Wave 3 handled the query
                    return
                else:
                    logger.info(f"Wave 3: Query is simple, using standard routing")
                    # Fall through to standard routing below
                    
            except Exception as e:
                logger.error(f"Wave 3 pipeline failed: {e}", exc_info=True)
                logger.info("Falling back to standard routing")
                # Fall through to standard routing

        # 8. Generate response - use hybrid routing (local vs cloud based on RAG context)
        full_response = ""
        response_metadata = {}  # Store provider, model, cost info
        
        if self.using_router_v2:
            # Router V2 Hybrid Mode: Check RAG context quality to decide local vs cloud
            try:
                # Decide routing mode: local (Ollama) vs cloud (router_v2)
                use_local = self._should_use_local_model(
                    query=query,
                    rag_results=filtered_search_results,
                    provider_override=provider_override,
                    retrieval_tier=retrieval_tier.tier,
                )
                
                if use_local:
                    # Use local Ollama model (good RAG context, cost-effective)
                    logger.info("Router v2 Hybrid: Using LOCAL model (strong RAG context)")
                    
                    # Use self.llm (from router_v1 hybrid init) for local Ollama
                    async for chunk in self.llm.chat(
                        messages=messages,
                        system_prompt=augmented_system,
                        stream=stream
                    ):
                        full_response += chunk
                        yield chunk
                    
                    # Set metadata indicating local model use
                    # Get local model from router if available, otherwise use default
                    local_model = getattr(self.router, 'local_model', 'qwen2.5-coder:7b')
                    response_metadata = {
                        'provider': 'ollama',
                        'model': local_model,
                        'cost': 0.0,  # Local is free
                        'tokens_in': len(augmented_system.split()) + sum(len(m.get('content', '').split()) for m in messages),
                        'tokens_out': len(full_response.split()),
                        'estimated': True,
                        'routing_reason': 'Strong RAG context - using local model'
                    }
                    self._last_response_metadata = response_metadata
                    
                else:
                    # Use cloud providers via router_v2 (weak RAG or complex query)
                    logger.info("Router v2 Hybrid: Using CLOUD model (weak RAG or complex query)")
                    
                    # Include system prompt in messages so all providers (including LiteLLM) receive it
                    messages_with_system = [{"role": "system", "content": augmented_system}] + messages
                    
                    # Map confidence string to ConfidenceLevel enum
                    if confidence:
                        confidence_level = ConfidenceLevel(confidence)
                    else:
                        confidence_level = self.default_confidence
                    
                    logger.info(f"Router v2: Using confidence level '{confidence_level.value}'")
                    
                    use_override = bool(provider_override and provider_override in self.router_v2.providers)
                    
                    if not stream and not use_override:
                        # Non-streaming: use full fallback chain so we try next provider on failure
                        response = await self.router_v2.complete_with_fallback(
                            messages=messages_with_system,
                            confidence=confidence_level,
                            max_tokens=4096,
                            temperature=0.7,
                        )
                        full_response = response.content
                        yield full_response
                        response_metadata = {
                            'provider': response.provider,
                            'model': response.model,
                            'cost': response.cost,
                            'tokens_in': response.tokens_in,
                            'tokens_out': response.tokens_out,
                            'estimated': False
                        }
                    else:
                        # Streaming or provider_override: route once then use selected provider
                        routing_patterns: List[Any] = []
                        if self.pattern_engine:
                            try:
                                from core.patterns.models import PatternQuery, PatternType
                                routing_patterns = self.pattern_engine.search(
                                    PatternQuery(
                                        pattern_types=[PatternType.ROUTING_OUTCOME],
                                        min_confidence=0.6,
                                        limit=3,
                                    )
                                )
                            except Exception as e:
                                logger.debug(f"Routing patterns fetch failed: {e}")
                        
                        routing_decision = await self.router_v2.route(
                            messages=messages_with_system,
                            confidence=confidence_level,
                            max_tokens=4096,
                            patterns=routing_patterns,
                        )
                        logger.info(f"Router v2 decision: {routing_decision.reason}")
                        
                        selected_provider = routing_decision.provider
                        selected_model = routing_decision.model
                        if use_override:
                            selected_provider = self.router_v2.providers[provider_override]
                            logger.info(f"Router v2: Overriding to provider '{provider_override}'")
                        
                        if stream:
                            collected_chunks = []
                            async for chunk in selected_provider.stream(
                                messages=messages_with_system,
                                model=selected_model,
                                max_tokens=4096,
                            ):
                                full_response += chunk
                                collected_chunks.append(chunk)
                                yield chunk
                            tokens_in = len(augmented_system.split()) + sum(len(m.get('content', '').split()) for m in messages)
                            tokens_out = len(full_response.split())
                            cost = selected_provider.estimate_cost(tokens_in + tokens_out, selected_model)
                            response_metadata = {
                                'provider': selected_provider.name,
                                'model': selected_model,
                                'cost': cost,
                                'tokens_in': tokens_in,
                                'tokens_out': tokens_out,
                                'estimated': True,
                                'routing_reason': routing_decision.reason  # Add routing explanation
                            }
                        else:
                            response = await selected_provider.complete(
                                messages=messages_with_system,
                                model=selected_model,
                                max_tokens=4096,
                            )
                            full_response = response.content
                            yield full_response
                            response_metadata = {
                                'provider': response.provider,
                                'model': response.model,
                                'cost': response.cost,
                                'tokens_in': response.tokens_in,
                                'tokens_out': response.tokens_out,
                                'estimated': False,
                                'routing_reason': routing_decision.reason  # Add routing explanation
                            }
                    
                    # Track budget usage
                    if self.budget_manager:
                        await self.budget_manager.record_usage(
                            provider=response_metadata['provider'],
                            model=response_metadata['model'],
                            cost=response_metadata['cost'],
                            tokens_in=response_metadata['tokens_in'],
                            tokens_out=response_metadata['tokens_out']
                        )
                        logger.info(f"Budget tracking: ${response_metadata['cost']:.4f} for {response_metadata['tokens_in'] + response_metadata['tokens_out']} tokens")
                    
                    # Store metadata for access by caller
                    self._last_response_metadata = response_metadata

                    # Record routing outcome — fire-and-forget in background thread
                    # (Mem0 add_memory inside learn() takes ~25-30s due to LLM extraction)
                    asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: self._record_routing_outcome(
                            response_metadata,
                            task_type="general",
                            persona=persona,
                            rag_coverage=None,
                        ),
                    )
                
            except Exception as e:
                logger.error(f"Router v2 failed: {e}", exc_info=True)
                # Fall back to router v1
                logger.warning("Falling back to router v1")
                async for chunk in self.llm.chat(
                    messages=messages,
                    system_prompt=augmented_system,
                    stream=stream
                ):
                    full_response += chunk
                    yield chunk
                
                # Set metadata for v1 fallback
                local_model = getattr(self.router, 'local_model', 'qwen2.5-coder:7b')
                response_metadata = {
                    'provider': 'ollama',
                    'model': local_model,
                    'cost': 0.0,
                    'tokens_in': len(augmented_system.split()) + sum(len(m.get('content', '').split()) for m in messages),
                    'tokens_out': len(full_response.split()),
                    'estimated': True,
                    'routing_reason': 'Router v2 failed, fell back to router v1 local model'
                }
                self._last_response_metadata = response_metadata
        else:
            # Router V1 path - legacy routing
            async for chunk in self.llm.chat(
                messages=messages,
                system_prompt=augmented_system,
                stream=stream
            ):
                full_response += chunk
                yield chunk
            
            # Set metadata for v1 routing
            local_model = getattr(self.router, 'local_model', 'qwen2.5-coder:7b')
            response_metadata = {
                'provider': 'ollama',
                'model': local_model,
                'cost': 0.0,
                'tokens_in': len(augmented_system.split()) + sum(len(m.get('content', '').split()) for m in messages),
                'tokens_out': len(full_response.split()),
                'estimated': True,
                'routing_reason': 'Router v1 (legacy routing)'
            }
            self._last_response_metadata = response_metadata

        # Record routing decision for autonomy metrics (standard, non-Wave3 path).
        # Wave 3 path records per-sub-query in split_router.py; this covers all other queries.
        if self.autonomy_metrics and response_metadata:
            try:
                provider = response_metadata.get('provider', 'unknown')
                is_local = provider == 'ollama' or response_metadata.get('cost', 1.0) == 0.0
                self.autonomy_metrics.record_routing_decision(
                    route_type="local" if is_local else "cloud",
                    provider=provider,
                    tokens_used=response_metadata.get('tokens_in', 0) + response_metadata.get('tokens_out', 0),
                    cost=response_metadata.get('cost', 0.0),
                    local_pct=1.0 if is_local else 0.0,
                )
            except Exception as e:
                logger.debug(f"Failed to record autonomy routing decision: {e}")

        # 9. Update conversation history (must be inline — fast, needed for next query)
        self.conversation_history.append({'role': 'user', 'content': query})
        self.conversation_history.append({'role': 'assistant', 'content': full_response})

        # ------------------------------------------------------------------
        # Store response in Semantic Cache (Spec 01)
        # ------------------------------------------------------------------
        if self.semantic_cache and full_response:
            try:
                self.semantic_cache.store(
                    query=query,
                    response=full_response,
                    metadata={
                        "domains": detected_domains,
                        "persona": persona,
                        "model": response_metadata.get("model", ""),
                    },
                )
            except Exception as e:
                logger.debug(f"Cache store failed: {e}")

        # 9.5 Rolling context turn tracking — decay unreferenced, amplify referenced (fast, inline)
        if self.rolling_context:
            try:
                self.rolling_context.on_new_turn(
                    query, full_response, query_domains=domain_names
                )
                logger.debug(
                    f"Rolling context turn tracked (turn {self.rolling_context.turn_count}, "
                    f"{len(self.rolling_context.entries)} entries)"
                )
            except Exception as e:
                logger.debug(f"Rolling context turn tracking failed: {e}")

        # 10. Offload slow post-response work to background thread
        # Pattern learning (Mem0 save ~25s), entity extraction (spaCy + SQLite ~11s),
        # mental model tracking, knowledge gap detection — none of these need to block
        # the response delivery.
        def _post_response_background():
            """Run slow post-response tasks in a background thread."""
            # Per-turn chunk reinforcement (Spec 05) — run before pattern save
            try:
                self._reinforce_chunk_patterns(query, full_response)
            except Exception as e:
                logger.debug(f"Chunk reinforcement failed (non-critical): {e}")

            # Pattern learning
            if self.pattern_engine:
                try:
                    self.pattern_engine.learn_from_query(query, detected_domains, full_response)
                    self.pattern_engine.save()
                    logger.info(f"Recorded query pattern: {query[:50]}...")
                except Exception as e:
                    logger.error(f"Failed to record pattern: {e}")

            # Entity extraction — process query and response together in one spaCy
            # batch call to halve the nlp.pipe() overhead vs. two sequential calls.
            if self.entity_extractor:
                try:
                    source_id = f"session_{self.session_start.isoformat()}"
                    domain_ids = [d for d in detected_domains if (d or "").strip().lower() not in ("", "unknown")]
                    self.entity_extractor.batch_extract_and_store(
                        items=[(query, "query"), (full_response, "response")],
                        source_id=source_id,
                        domains=domain_ids,
                    )
                except Exception as e:
                    logger.debug(f"Entity extraction failed (non-critical): {e}")

            # Mental model effectiveness tracking + reference rate (Spec 07)
            if self.mental_model_manager and getattr(self, "_last_activated_mental_model_ids", None):
                try:
                    self.mental_model_manager.record_activation(
                        self._last_activated_mental_model_ids,
                        signals={"conversation_continued": True},
                    )
                except Exception as e:
                    logger.debug(f"Mental model effectiveness recording failed: {e}")

            # Compute mm_reference_rate (Spec 07)
            self._last_mm_reference_rate = 0.0
            if self.mental_model_manager and getattr(self, "_last_activated_mental_model_ids", None):
                try:
                    active_models = [
                        self.mental_model_manager.get_model(mid)
                        for mid in self._last_activated_mental_model_ids
                    ]
                    active_models = [m for m in active_models if m is not None]
                    if active_models:
                        self._last_mm_reference_rate = (
                            self.mental_model_manager.compute_mm_reference_rate(
                                full_response, active_models
                            )
                        )
                        logger.debug(f"mm_reference_rate={self._last_mm_reference_rate:.3f} for {len(active_models)} models")
                except Exception as e:
                    logger.debug(f"mm_reference_rate computation failed: {e}")

            # Context metrics recording (Spec 06)
            # Note: decomposed/sub_query_count tracked via Wave 3 when enabled
            self._record_context_metrics(
                query=query,
                response=full_response,
                domains=detected_domains,
                persona=persona,
                response_metadata=response_metadata,
                decomposed=False,  # Will be enhanced when Wave 3 metrics tracking is added
                sub_query_count=0,
            )

            logger.info("Background post-response tasks completed")

        asyncio.get_event_loop().run_in_executor(None, _post_response_background)

        # Knowledge gap detection (async, needs event loop — keep inline but lightweight)
        await self._detect_and_suggest_knowledge_gap(
            query=query,
            rag_results=filtered_search_results,
            cloud_response=full_response,
            response_metadata=response_metadata,
            retrieval_tier=retrieval_tier.tier
        )

    async def index(
        self,
        obsidian: bool = True,
        codebases: bool = True,
        force: bool = False
    ) -> Dict[str, int]:
        """
        Index knowledge sources (runs in background to avoid blocking).

        Args:
            obsidian: Whether to index Obsidian vault
            codebases: Whether to index codebases
            force: Force re-indexing of all files

        Returns:
            Dict with counts of indexed files per source
        """
        # Run blocking indexing operations in thread pool to avoid blocking event loop
        loop = asyncio.get_event_loop()
        
        def _sync_index():
            results = {}
            
            if obsidian and self.config.obsidian_vault_path:
                logger.info(f"Indexing Obsidian vault: {self.config.obsidian_vault_path}")
                results['obsidian'] = self.rag.index_obsidian_vault(
                    self.config.obsidian_vault_path,
                    force=force
                )

            if codebases:
                codebase_paths = self.config.get("codebases.paths", [])
                excludes = self.config.get("codebases.exclude", [])
                total = 0
                for path in codebase_paths:
                    logger.info(f"Indexing codebase: {path}")
                    total += self.rag.index_codebase(
                        Path(path),
                        excludes=excludes,
                        force=force
                    )
                results['codebases'] = total

            return results
        
        # Run in thread pool executor to avoid blocking
        results = await loop.run_in_executor(None, _sync_index)
        return results

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.session_start = datetime.now()

    def get_stats(self) -> Dict[str, Any]:
        """Get Polly statistics."""
        stats = {
            'user': self.user_name,
            'session_start': self.session_start.isoformat(),
            'conversation_length': len(self.conversation_history),
            'rag': self.rag.get_stats()
        }

        if self.pattern_engine:
            engine_stats = self.pattern_engine.get_stats()
            stats['patterns'] = engine_stats.get('total_patterns', 0)

        if self.entity_store:
            stats['graph'] = self.entity_store.get_stats()

        return stats
    
    def get_last_response_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get metadata from the last response (router v2 only).
        
        Returns:
            Dict with provider, model, cost, tokens if router_v2 was used,
            None otherwise.
        
        Example response:
            {
                'provider': 'github',
                'model': 'openai/gpt-4o',
                'cost': 0.0023,
                'tokens_in': 150,
                'tokens_out': 200,
                'estimated': False
            }
        """
        return getattr(self, '_last_response_metadata', None)

    # ==================== Phase 13A Day 16: Pattern Enhancement APIs ====================
    
    def get_pattern_stats(self) -> Dict:
        """
        Get pattern learning statistics.
        
        Phase 13A Day 16: Pattern Enhancement APIs
        
        Returns:
            Dict with pattern counts and statistics
        
        Example:
            >>> stats = polly.get_pattern_stats()
            >>> print(f"Total patterns: {stats['total_patterns']}")
        """
        if not self.pattern_engine:
            return {}
        
        return self.pattern_engine.get_stats()
    
    def get_patterns_for_concept(self, concept: str) -> List[Dict]:
        """
        Get patterns related to a concept.
        
        Args:
            concept: The concept to search for (e.g., "docker", "python")
        
        Returns:
            List of pattern dicts with concept pairs and confidence
        
        Example:
            >>> patterns = polly.get_patterns_for_concept("docker")
            >>> for p in patterns:
            >>>     print(f"{p['concept1']} ↔ {p['concept2']}: {p['confidence']:.2f}")
        """
        if not self.pattern_engine:
            return []
        
        patterns = self.pattern_engine.get_conceptual_patterns(concept)
        return [
            {
                'concept1': p.metadata.get('concept1'),
                'concept2': p.metadata.get('concept2'),
                'confidence': p.confidence,
                'occurrences': p.occurrences,
                'usefulness_ratio': p.usefulness_ratio,
            }
            for p in patterns
        ]
    
    def get_domain_collection_priorities(self, domain: str) -> Dict[str, float]:
        """
        Get collection priorities for a domain.
        
        Args:
            domain: The domain to get priorities for (e.g., "python", "docker")
        
        Returns:
            Dict mapping collection names to weight scores
        
        Example:
            >>> weights = polly.get_domain_collection_priorities("python")
            >>> print(weights)  # {'codebase': 2.5, 'obsidian': 1.8}
        """
        if not self.pattern_engine:
            return {}
        
        return self.pattern_engine.get_domain_priorities(domain)
    
    def export_patterns(self, filepath: Optional[str] = None) -> Dict:
        """
        Export all patterns for analysis.
        
        Args:
            filepath: Optional path to save JSON export
        
        Returns:
            Dict with all pattern data
        
        Example:
            >>> data = polly.export_patterns("/tmp/patterns.json")
            >>> print(f"Exported {data['stats']['total_patterns']} patterns")
        """
        if not self.pattern_engine:
            return {}
        
        data = self.pattern_engine.export()
        
        if filepath:
            import json
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Exported patterns to {filepath}")
        
        return data

    async def create_learning_note(
        self,
        topic: str,
        content: str,
        concepts: List[str],
        domain: str,
        conversation_id: Optional[str] = None
    ) -> Dict:
        """
        Create a structured learning note (Phase 22 - Teaching Mode).
        
        Args:
            topic: Topic title
            content: Note content (generated by LLM)
            concepts: List of concepts covered
            domain: Domain ID
            conversation_id: Current conversation ID
        
        Returns:
            Note creation result
        """
        note_title = f"Learning - {topic}"
        
        # Generate structured content
        structured_content = f"""# {topic}

## Key Concepts

{chr(10).join(f"- {c}" for c in concepts)}

## Understanding

{content}

## Related Topics

<!-- Links to related concepts will be added here -->

## Practice Exercises

<!-- Add exercises to reinforce learning -->

---

*Learned: {datetime.now().strftime('%Y-%m-%d')}*  
*Domain: {domain}*  
*Mastery Level: 1/5 (Introduced)*
"""
        
        # Create note via Obsidian integration
        result = await self.obsidian.create_note(
            title=note_title,
            content=structured_content,
            folder=None,  # Auto-suggest based on domain
            tags=['learning', domain],
            preview=False
        )
        
        # Record in learning tracker
        if result.get('status') == 'success' and self.learning_tracker:
            self.learning_tracker.record_learning(
                title=topic,
                domain=domain,
                concepts=concepts,
                mastery_level=1,
                note_path=result.get('note_path')
            )
            logger.info(f"Learning note created: {note_title}")
        
        return result

    def save_state(self):
        """Save learned state (patterns, graph)."""
        if self.pattern_engine:
            self.pattern_engine.save()

        if self.entity_store:
            self.entity_store.recompute_all_authority()

        logger.info("State saved")
    
    async def _on_session_end(self):
        """Extract facts from conversation and write to tiered memory.

        Called at session end (cleanup, timeout, explicit close).
        Uses the session extractor to analyse the conversation and
        write stable/episodic facts to the memory store.
        """
        if not self.session_extractor:
            return

        if not self.conversation_history or len(self.conversation_history) < 2:
            logger.debug("Session too short for extraction — skipping")
            return

        try:
            # Build session metadata
            session_metadata = {
                "duration_minutes": (
                    (datetime.now() - self.session_start).total_seconds() / 60
                    if self.session_start else 0
                ),
                "exchange_count": len(self.conversation_history) // 2,
                "domains": list(set(
                    msg.get("domain", "general")
                    for msg in self.conversation_history
                    if isinstance(msg, dict)
                )),
            }

            # Get compression summary if available
            compression_summary = {}
            if self.compression_manager and hasattr(self.compression_manager, "get_current_summary"):
                try:
                    compression_summary = self.compression_manager.get_current_summary()
                except Exception:
                    pass

            result = await self.session_extractor.extract_and_store(
                self.conversation_history,
                compression_summary,
                session_metadata,
            )

            logger.info(
                f"Session extraction complete: {result.stable_count} stable, "
                f"{result.episodic_count} episodic facts (model={result.model_used}, "
                f"{result.duration_ms}ms)"
            )

            # Flush working memory for this session
            if self.tiered_store and hasattr(self.tiered_store, "flush_working"):
                self.tiered_store.flush_working()
                logger.info("Working memory flushed")

            # Invalidate the retriever cache so the next query sees the
            # newly written stable/episodic facts rather than stale results.
            if self.memory_retriever and hasattr(self.memory_retriever, "invalidate"):
                self.memory_retriever.invalidate()
                logger.debug("MemoryRetriever cache invalidated after session extraction")

        except Exception as e:
            logger.warning(f"Session-end extraction failed: {e}")

    def cleanup(self):
        """Cleanup resources on shutdown."""
        try:
            # Run session-end extraction (async → sync bridge)
            if self.session_extractor:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If we're inside an async context, schedule it
                        asyncio.ensure_future(self._on_session_end())
                        logger.info("Session extraction scheduled (async)")
                    else:
                        loop.run_until_complete(self._on_session_end())
                        logger.info("Session extraction completed (sync)")
                except RuntimeError:
                    # No event loop — create one
                    asyncio.run(self._on_session_end())
                    logger.info("Session extraction completed (new loop)")
                except Exception as e:
                    logger.warning(f"Session extraction during cleanup failed: {e}")

            # Stop notes sync if running
            if hasattr(self, 'notes_sync') and self.notes_sync:
                logger.info("Stopping notes sync manager...")
                self.notes_sync.stop()
                logger.info("Notes sync manager stopped")
            
            # Save state
            self.save_state()
            
            logger.info("Polly cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Convenience function for quick queries
async def ask(query: str, stream: bool = True) -> str:
    """Quick query function."""
    polly = Polly()
    response = ""
    async for chunk in polly.query(query, stream=stream):
        response += chunk
        if stream:
            print(chunk, end='', flush=True)
    if stream:
        print()
    return response

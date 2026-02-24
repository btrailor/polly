"""
Mental Models System for Polly (Phase 14)

This module implements a three-tier activation system that allows mental models
to guide Polly's behavior based on:
- Domain: Content-based (Sigils, Signals, Scrolls, Glyphs, Grids)
- Page: Context-based (Learning, Code, Projects, etc.)
- Persona: Mode-based (Architect, Teacher, Socratic, etc.)

Mental models are compressed using Compact Format (formerly PIL) for efficient
storage in conversation context.
"""

import yaml
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from core.context.token_counter import TokenCounter

logger = logging.getLogger(__name__)


@dataclass
class MentalModel:
    """
    A mental model that guides Polly's thinking and responses.
    
    Mental models can be activated based on:
    - Domain (Sigils, Signals, Scrolls, Glyphs, Grids)
    - Page (Learning, Code, Projects, etc.)
    - Persona/Mode (Architect/Plan, Teacher/Socratic, etc.)
    """
    id: str
    name: str
    description: str
    principles: List[str]
    prompt_injection: str
    
    # Three-tier activation fields
    applies_to: List[str] = field(default_factory=list)  # Domain-level
    active_on_pages: List[str] = field(default_factory=list)  # Page-level
    active_for_personas: List[str] = field(default_factory=list)  # Persona-level
    active_for_modes: List[str] = field(default_factory=list)  # Mode-level (part of persona)
    
    # Optional metadata
    keywords: List[str] = field(default_factory=list)
    category_triggers: List[str] = field(default_factory=list)
    enabled: bool = True
    
    # System fields
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    _compressed: Optional[str] = None  # Compact format (generated on demand)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['created'] = self.created.isoformat()
        data['updated'] = self.updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MentalModel':
        """Create MentalModel from dictionary."""
        # Parse datetime strings back to datetime objects
        if isinstance(data.get('created'), str):
            data['created'] = datetime.fromisoformat(data['created'])
        if isinstance(data.get('updated'), str):
            data['updated'] = datetime.fromisoformat(data['updated'])
        return cls(**data)


class MentalModelManager:
    """
    Manages mental models with three-tier activation logic.
    
    Handles:
    - Loading/saving models from YAML
    - Scoring and selecting relevant models for context
    - CRUD operations
    - Compact format compression integration
    """
    
    def __init__(self, storage_path: str, compressor=None, config: Optional[Dict] = None):
        """
        Initialize the mental model manager.
        
        Args:
            storage_path: Path to YAML file for storing models
            compressor: Optional ConversationCompressor instance for compact format compression
            config: Full config dict for compression format and A/B test settings
        """
        self.storage_path = Path(storage_path).expanduser()
        self.compressor = compressor
        self._config = config or {}
        self.models: Dict[str, MentalModel] = {}
        # Persona context (integration-contracts: PersonaAware)
        self._active_persona: Optional[str] = None
        self._active_mode: Optional[str] = None
        # Effectiveness tracking (integration-contracts: lightweight heuristic)
        self._effectiveness_log: List[Dict[str, Any]] = []
        # A/B: last format used this session (for metrics recording)
        self._last_mm_format: str = "compact"
        # A/B: recommendations cache loaded from disk
        self._format_recommendations: Dict[str, str] = self._load_format_recommendations()

        # Load existing models or create defaults
        if self.storage_path.exists():
            self._load_models()
        else:
            self._create_default_models()
            self.save_models()
        
        logger.info(f"Mental model manager initialized with {len(self.models)} models")

    def set_active_persona(self, persona_name: str, mode: str) -> None:
        """Notify of active persona (PersonaAware protocol). Used when caller omits persona in get_models_for_context."""
        self._active_persona = persona_name or None
        self._active_mode = mode or None

    def record_activation(
        self,
        model_ids: List[str],
        signals: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record which models were active and outcome signals (integration-contracts). In-memory; can be flushed later."""
        from datetime import datetime
        for model_id in model_ids:
            self._effectiveness_log.append({
                "model_id": model_id,
                "timestamp": datetime.now().isoformat(),
                "signals": signals or {},
            })
        # Keep log bounded
        if len(self._effectiveness_log) > 1000:
            self._effectiveness_log = self._effectiveness_log[-500:]

    def get_effectiveness_summary(self) -> Dict[str, Any]:
        """Return summary of activation log for tuning (integration-contracts)."""
        return {"entries": len(self._effectiveness_log), "sample": self._effectiveness_log[-10:] if self._effectiveness_log else []}

    # ------------------------------------------------------------------
    # Compact Format A/B validation (Spec 07)
    # ------------------------------------------------------------------

    def _load_format_recommendations(self) -> Dict[str, str]:
        """Load persisted per-model format recommendations from disk."""
        import json
        rec_path = Path(self.storage_path).parent / "mental_model_format_recommendations.json"
        try:
            if rec_path.exists():
                data = json.loads(rec_path.read_text())
                return {model: entry.get("recommendation", "compact") for model, entry in data.items()}
        except Exception as e:
            logger.debug(f"Could not load format recommendations: {e}")
        return {}

    def _save_format_recommendations(self, recommendations: Dict[str, Any]) -> None:
        """Persist per-model format recommendations to disk."""
        import json
        rec_path = Path(self.storage_path).parent / "mental_model_format_recommendations.json"
        try:
            rec_path.write_text(json.dumps(recommendations, indent=2, default=str))
        except Exception as e:
            logger.warning(f"Could not save format recommendations: {e}")

    def _select_format(self, model_used: str = "") -> str:
        """
        Select compact vs full-text format for this turn (Spec 07).

        Priority:
        1. A/B test: if enabled and random() < sample_rate → "full"
        2. Persisted per-model recommendation (from analyse_ab_results)
        3. Static per-model profile from config
        4. Configured default (compact)
        """
        import random
        compression_cfg = self._config.get("mental_models", {}).get("compression", {})
        fmt_default = compression_cfg.get("format", "compact")

        ab_cfg = compression_cfg.get("ab_test", {})
        if ab_cfg.get("enabled", False):
            sample_rate = ab_cfg.get("sample_rate", 0.15)
            if random.random() < sample_rate:
                self._last_mm_format = "full"
                logger.debug(f"A/B test: using full-text format (rate={sample_rate})")
                return "full"

        # Persisted recommendation
        if model_used and model_used in self._format_recommendations:
            fmt = self._format_recommendations[model_used]
            self._last_mm_format = fmt
            return fmt

        # Static per-model profile
        profiles = compression_cfg.get("model_format_profiles", {})
        for key, fmt in profiles.items():
            if key.lower() in model_used.lower():
                self._last_mm_format = fmt
                return fmt
        default_fmt = profiles.get("default", fmt_default)
        self._last_mm_format = default_fmt
        return default_fmt

    def compute_mm_reference_rate(
        self, response: str, active_models: List[Any]
    ) -> float:
        """
        Compute how many active mental models are referenced in the response (Spec 07).

        Returns fraction 0.0–1.0: models_referenced / models_injected.
        """
        if not active_models:
            return 0.0
        response_lower = response.lower()
        referenced = 0
        for model in active_models:
            # Check name and key terms from keywords list
            name_lower = model.name.lower()
            if name_lower in response_lower:
                referenced += 1
                continue
            kws = getattr(model, "keywords", []) or []
            if any(kw.lower() in response_lower for kw in kws[:5]):
                referenced += 1
        return referenced / len(active_models)

    # ContextContributor (integration-contracts): priority 60
    context_priority = 60

    def build_context_items(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: Any,
    ) -> list:
        """
        Per-item ContextContributor protocol (Spec 02).

        Returns one ScoredEntry per activated mental model instead of a single
        concatenated blob. Each model carries its own activation score so the
        budget allocator can include high-activation models and evict low-ones
        independently.
        """
        from core.context.relevance_scorer import ScoredEntry

        override_model_ids = kwargs.get("override_model_ids")
        if override_model_ids is not None:
            models_with_scores = []
            for model_id in override_model_ids:
                model = self.get_model(model_id)
                if model:
                    models_with_scores.append((model, 75.0))  # fixed score for explicit overrides
        else:
            keywords = kwargs.get("keywords")
            if keywords is None:
                keywords = [w for w in query.lower().split() if len(w) > 2][:20]
            domain = domains[0] if domains else None
            models_with_scores = self.get_models_for_context_scored(
                domain=domain,
                page=kwargs.get("page"),
                persona=persona,
                persona_mode=mode,
                keywords=keywords,
                enabled_only=True,
            )

        if not models_with_scores:
            return []

        # Select format once for this turn (Spec 07 A/B)
        model_used = kwargs.get("model_used", "")
        mm_format = self._select_format(model_used)

        entries = []
        for model, activation_score in models_with_scores:
            try:
                if self.compressor:
                    compressed = self.compressor.compress(
                        model.to_dict(),
                        type="mental_model",
                        metadata={"format": mm_format},
                    )
                else:
                    compressed = f"{model.name}: {model.prompt_injection[:100]}"
                tc = TokenCounter.count(compressed)
                entries.append(ScoredEntry(
                    content=compressed,
                    source="mental_model",
                    raw_score=min(activation_score / 34.0, 1.0),  # normalise: max possible score ~34
                    composite_score=0.0,
                    token_count=tc,
                    metadata={
                        "model_id": model.id,
                        "model_name": model.name,
                        "category": getattr(model, "category", "general"),
                        "domain": domain or (domains[0] if domains else "general"),
                        "mm_format": mm_format,
                    },
                ))
            except Exception as e:
                logger.warning(f"Failed to build ScoredEntry for mental model {model.id}: {e}")

        return entries

    def build_context(
        self,
        query: str,
        domains: List[str],
        persona: Optional[str] = None,
        mode: Optional[str] = None,
        token_budget: int = 0,
        **kwargs: Any,
    ) -> str:
        """Build mental models context for system prompt (ContextContributor protocol)."""
        override_model_ids = kwargs.get("override_model_ids")
        if override_model_ids is not None:
            models = []
            for model_id in override_model_ids:
                model = self.get_model(model_id)
                if model:
                    models.append(model)
            if not models:
                return ""
        else:
            keywords = kwargs.get("keywords")
            if keywords is None:
                keywords = [w for w in query.lower().split() if len(w) > 2][:20]
            domain = domains[0] if domains else None
            models = self.get_models_for_context(
                domain=domain,
                page=kwargs.get("page"),
                persona=persona,
                persona_mode=mode,
                keywords=keywords,
                enabled_only=True,
            )
        if not models:
            return ""
        # Select format once for this turn (Spec 07 A/B)
        model_used = kwargs.get("model_used", "")
        mm_format = self._select_format(model_used)
        compressed_models = []
        for model in models:
            try:
                if self.compressor:
                    compressed = self.compressor.compress(
                        model.to_dict(),
                        type="mental_model",
                        metadata={"format": mm_format},
                    )
                    compressed_models.append(compressed)
                else:
                    compressed_models.append(f"{model.name}: {model.prompt_injection[:100]}")
            except Exception as e:
                logger.warning(f"Failed to compress mental model {model.id}: {e}")
        if not compressed_models:
            return ""
        parts = [
            "\n\n## Active Mental Models (Compressed)\n\n",
            "The following mental models guide your responses:\n\n",
        ]
        for compressed in compressed_models:
            parts.append(f"{compressed}\n\n")
        parts.append("Apply these frameworks to guide your thinking and responses.\n")
        result = "".join(parts)
        if token_budget > 0 and TokenCounter.count(result) > token_budget:
            result = TokenCounter.truncate(result, token_budget)
        return result

    # Minimum score a model must reach to be included in auto-assignment.
    # A single keyword match (+2) or lone domain match (+3) is not enough;
    # the model needs at least a strong contextual signal (page, persona, or
    # multiple keyword hits) to earn its place.
    MIN_SCORE_THRESHOLD = 5

    # Maximum points that keyword matches can contribute.  This prevents
    # keyword flooding from overwhelming deliberate page/persona signals.
    MAX_KEYWORD_SCORE = 6

    def get_models_for_context(
        self,
        domain: Optional[str] = None,
        page: Optional[str] = None,
        persona: Optional[str] = None,
        persona_mode: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        enabled_only: bool = True
    ) -> List[MentalModel]:
        """
        Get relevant mental models using three-tier scoring.
        
        Scoring weights:
        - Page match: +10 (strongest - user is actively in that workspace)
        - Persona/mode match: +8 (explicit AI behavior mode)
        - Category trigger: +5 (auto-activation)
        - Domain match: +3 (content-based)
        - Keyword match: +2 per keyword (capped at MAX_KEYWORD_SCORE)
        
        Models must reach MIN_SCORE_THRESHOLD to be included.
        Keyword matching uses exact whole-word equality (not substrings).
        
        Args:
            domain: Current domain (e.g., "scrolls", "sigils")
            page: Current page (e.g., "learning", "code")
            persona: Active persona (e.g., "architect", "teacher")
            persona_mode: Active mode within persona (e.g., "plan", "socratic")
            keywords: Keywords extracted from query
            category: Legacy category trigger
            enabled_only: Only return enabled models
            
        Returns:
            List of top 3-5 models sorted by relevance score
        """
        # Use stored persona when not passed (integration-contracts)
        persona = persona or self._active_persona
        persona_mode = persona_mode or self._active_mode

        scored_models = []

        for model in self.models.values():
            # Skip disabled models if requested
            if enabled_only and not model.enabled:
                continue
            
            score = 0.0
            
            # Page match: +10 (strongest signal)
            if page and page in model.active_on_pages:
                score += 10
                logger.debug(f"Model '{model.name}' +10 (page match: {page})")
            
            # Persona match: +8
            if persona and persona in model.active_for_personas:
                score += 8
                logger.debug(f"Model '{model.name}' +8 (persona match: {persona})")
            
            # Mode match: +8
            if persona_mode and persona_mode in model.active_for_modes:
                score += 8
                logger.debug(f"Model '{model.name}' +8 (mode match: {persona_mode})")
            
            # Category trigger: +5
            if category and category in model.category_triggers:
                score += 5
                logger.debug(f"Model '{model.name}' +5 (category trigger: {category})")
            
            # Domain match: +3
            if domain and domain in model.applies_to:
                score += 3
                logger.debug(f"Model '{model.name}' +3 (domain match: {domain})")
            
            # Keyword matches: +2 per exact match, capped at MAX_KEYWORD_SCORE
            if keywords and model.keywords:
                kw_lower = {k.lower() for k in keywords}
                model_kw_lower = {mk.lower() for mk in model.keywords}
                keyword_matches = len(kw_lower & model_kw_lower)
                if keyword_matches > 0:
                    keyword_score = min(keyword_matches * 2, self.MAX_KEYWORD_SCORE)
                    score += keyword_score
                    logger.debug(f"Model '{model.name}' +{keyword_score} ({keyword_matches} keyword matches, capped at {self.MAX_KEYWORD_SCORE})")
            
            if score >= self.MIN_SCORE_THRESHOLD:
                scored_models.append((score, model))
                logger.debug(f"Model '{model.name}' total score: {score} (meets threshold {self.MIN_SCORE_THRESHOLD})")
            elif score > 0:
                logger.debug(f"Model '{model.name}' total score: {score} (below threshold {self.MIN_SCORE_THRESHOLD}, excluded)")
        
        # Sort by score (descending)
        scored_models.sort(key=lambda x: x[0], reverse=True)
        
        # Return top 3-5 models
        top_models = [model for score, model in scored_models[:5]]
        
        if top_models:
            logger.info(f"Selected {len(top_models)} mental models for context: {[m.name for m in top_models]}")
        else:
            logger.info("No mental models met the activation threshold for this context")
        
        return top_models

    def get_models_for_context_scored(
        self,
        domain: Optional[str] = None,
        page: Optional[str] = None,
        persona: Optional[str] = None,
        persona_mode: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        category: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[tuple]:
        """
        Like get_models_for_context() but returns (model, score) tuples (Spec 02).

        Used by build_context_items() so each model's activation score can be
        carried into the ScoredEntry for per-item budget allocation.
        """
        persona = persona or self._active_persona
        persona_mode = persona_mode or self._active_mode

        scored_models = []
        for model in self.models.values():
            if enabled_only and not model.enabled:
                continue
            score = 0.0
            if page and page in model.active_on_pages:
                score += 10
            if persona and persona in model.active_for_personas:
                score += 8
            if persona_mode and persona_mode in model.active_for_modes:
                score += 8
            if category and category in model.category_triggers:
                score += 5
            if domain and domain in model.applies_to:
                score += 3
            if keywords and model.keywords:
                kw_lower = {k.lower() for k in keywords}
                model_kw_lower = {mk.lower() for mk in model.keywords}
                keyword_matches = len(kw_lower & model_kw_lower)
                if keyword_matches > 0:
                    score += min(keyword_matches * 2, self.MAX_KEYWORD_SCORE)
            if score >= self.MIN_SCORE_THRESHOLD:
                scored_models.append((model, score))

        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models[:5]
    
    def add_model(self, model: MentalModel) -> None:
        """Add a new mental model."""
        if model.id in self.models:
            raise ValueError(f"Model with id '{model.id}' already exists")
        
        model.created = datetime.now()
        model.updated = datetime.now()
        self.models[model.id] = model
        logger.info(f"Added mental model: {model.name}")
    
    def update_model(self, model_id: str, updates: dict) -> MentalModel:
        """
        Update an existing mental model.
        
        Args:
            model_id: ID of model to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated MentalModel
        """
        if model_id not in self.models:
            raise ValueError(f"Model with id '{model_id}' not found")
        
        model = self.models[model_id]
        
        # Update allowed fields
        allowed_fields = {
            'name', 'description', 'principles', 'prompt_injection',
            'applies_to', 'active_on_pages', 'active_for_personas', 'active_for_modes',
            'keywords', 'category_triggers', 'enabled'
        }
        
        for key, value in updates.items():
            if key in allowed_fields:
                setattr(model, key, value)
        
        model.updated = datetime.now()
        model._compressed = None  # Invalidate compressed cache
        
        logger.info(f"Updated mental model: {model.name}")
        return model
    
    def delete_model(self, model_id: str) -> None:
        """Delete a mental model."""
        if model_id not in self.models:
            raise ValueError(f"Model with id '{model_id}' not found")
        
        model_name = self.models[model_id].name
        del self.models[model_id]
        logger.info(f"Deleted mental model: {model_name}")
    
    def toggle_model(self, model_id: str) -> bool:
        """
        Toggle a model's enabled state.
        
        Returns:
            New enabled state
        """
        if model_id not in self.models:
            raise ValueError(f"Model with id '{model_id}' not found")
        
        model = self.models[model_id]
        model.enabled = not model.enabled
        model.updated = datetime.now()
        
        logger.info(f"Toggled mental model '{model.name}': enabled={model.enabled}")
        return model.enabled
    
    def get_model(self, model_id: str) -> Optional[MentalModel]:
        """Get a single model by ID."""
        return self.models.get(model_id)
    
    def list_models(self, enabled_only: bool = False) -> List[MentalModel]:
        """
        List all models.
        
        Args:
            enabled_only: Only return enabled models
            
        Returns:
            List of MentalModel objects
        """
        models = list(self.models.values())
        if enabled_only:
            models = [m for m in models if m.enabled]
        return models
    
    def save_models(self) -> None:
        """Save models to YAML file."""
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert models to dict format
        models_data = {
            'mental_models': [model.to_dict() for model in self.models.values()]
        }
        
        # Write to YAML
        with open(self.storage_path, 'w') as f:
            yaml.dump(models_data, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"Saved {len(self.models)} mental models to {self.storage_path}")
    
    def _load_models(self) -> None:
        """Load models from YAML file."""
        try:
            with open(self.storage_path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data or 'mental_models' not in data:
                logger.warning("No mental models found in storage, creating defaults")
                self._create_default_models()
                return
            
            for model_data in data['mental_models']:
                model = MentalModel.from_dict(model_data)
                self.models[model.id] = model
            
            logger.info(f"Loaded {len(self.models)} mental models from {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to load mental models: {e}")
            logger.warning("Creating default models instead")
            self._create_default_models()
    
    def _create_default_models(self) -> None:
        """Create the 12 default mental models from Phase 14 spec."""
        
        # TIER 1: CORE PHILOSOPHY
        
        self.models['infinite_games'] = MentalModel(
            id='infinite_games',
            name='Infinite Games',
            description='Playing to keep the game going rather than to win. Based on James Carse\'s framework, this perspective values continuation over completion, evolving rules over fixed outcomes, and bringing more people into play.',
            principles=[
                'Continuation over completion',
                'Evolving rules rather than fixed rules',
                'Bringing more players into the game',
                'Horizon of possibility over endpoint'
            ],
            prompt_injection='When discussing systems, learning, or creative work, consider the infinite game perspective: How can this keep going? How might the rules evolve? How can more people get involved? Focus on continuation over completion.',
            applies_to=['scrolls'],
            active_on_pages=['learning'],
            active_for_personas=[],
            active_for_modes=[],
            keywords=['infinite', 'finite', 'carse', 'infinite game', 'continuation'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['instruments_over_tracks'] = MentalModel(
            id='instruments_over_tracks',
            name='Instruments Over Tracks',
            description='Focus on building generative systems that create new possibilities rather than fixed outputs. Inspired by music production: creating instruments (tools for creation) over tracks (finished products).',
            principles=[
                'Generative tools over finished products',
                'Systems that create possibility',
                'Instruments that enable creation',
                'Open-ended over closed systems'
            ],
            prompt_injection='When discussing creative or technical projects, consider: How can this be an instrument that generates possibilities rather than a fixed output? Focus on building tools and systems that enable creation.',
            applies_to=['signals'],
            active_on_pages=[],
            active_for_personas=['architect'],
            active_for_modes=['build'],
            keywords=['instrument', 'generative', 'monome', 'open-ended'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['constraint_as_meaning'] = MentalModel(
            id='constraint_as_meaning',
            name='Constraint as Meaning-Creation',
            description='Constraints don\'t limit creativity—they enable it. Boundaries create possibility. Limitation is generative. Form creates content.',
            principles=[
                'Constraints enable rather than limit',
                'Boundaries create possibility',
                'Limitation generates creativity',
                'Form creates content'
            ],
            prompt_injection='When discussing creative or technical challenges, explore how constraints can be generative. What limitations might actually create new possibilities? How do boundaries enable creativity?',
            applies_to=['signals'],
            active_on_pages=[],
            active_for_personas=[],
            active_for_modes=[],
            keywords=['constraint', 'limitation', 'boundary', 'creative constraint'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 2: LEARNING & THINKING
        
        self.models['pedagogy_of_liberation'] = MentalModel(
            id='pedagogy_of_liberation',
            name='Pedagogy of Liberation (Freire)',
            description='Education as liberation, not banking. Learning is dialogue, not transmission. The teacher-student relationship is mutual. Based on Paulo Freire\'s critical pedagogy framework.',
            principles=[
                'Problem-posing over banking model',
                'Dialogue over transmission',
                'Critical consciousness (conscientização)',
                'Praxis: reflection plus action',
                'Co-creation of knowledge'
            ],
            prompt_injection='When discussing education, learning, or teaching, adopt a problem-posing approach. Engage in dialogue rather than transmission. Ask questions that promote critical consciousness. Recognize that we are learning together.',
            applies_to=['scrolls', 'grids'],
            active_on_pages=['learning', 'notes', 'dashboard'],
            active_for_personas=['professor'],
            active_for_modes=['socratic', 'guide'],
            keywords=['freire', 'paulo', 'pedagogy', 'liberation', 'praxis', 'banking', 'problem-posing', 'dialogue', 'conscientização'],
            category_triggers=['scrolls'],
            enabled=True
        )
        
        self.models['reverse_engineering'] = MentalModel(
            id='reverse_engineering',
            name='Reverse Engineering Approach',
            description='Start with the thing you want to understand, take it apart, see how it works. Learn by deconstruction and reconstruction. Begin with the whole, understand the parts.',
            principles=[
                'Start with the whole, understand the parts',
                'Deconstruct to understand construction',
                'Learn by taking things apart',
                'Reverse the typical learning path'
            ],
            prompt_injection='When helping someone learn, suggest starting with examples to deconstruct rather than building from first principles. Show how to take things apart to understand how they work.',
            applies_to=['sigils', 'signals', 'grids'],
            active_on_pages=['code', 'learning', 'patterns'],
            active_for_personas=['professor'],
            active_for_modes=['guide'],
            keywords=['reverse', 'engineering', 'deconstruct', 'take apart', 'understand', 'analyze'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['socratic_method'] = MentalModel(
            id='socratic_method',
            name='Socratic Method',
            description='Question assumptions, reveal contradictions, guide discovery through dialogue. Don\'t provide direct answers—ask questions that lead to understanding. Teacher and student learn together through dialectical inquiry.',
            principles=[
                'Question rather than tell',
                'Reveal contradictions through dialogue',
                'Guide discovery, don\'t provide answers',
                'Mutual learning between teacher and student'
            ],
            prompt_injection='Don\'t provide direct answers. Ask questions that guide discovery. Reveal contradictions in thinking. Use dialogue to promote deeper understanding. Recognize that we\'re learning together through this exchange.',
            applies_to=['scrolls', 'grids'],
            active_on_pages=['learning', 'dashboard'],
            active_for_personas=['professor'],
            active_for_modes=['socratic'],
            keywords=['socratic', 'socrates', 'question', 'dialogue', 'dialectic', 'contradiction', 'inquiry'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 3: SYSTEMS & TECHNICAL
        
        self.models['systems_thinking'] = MentalModel(
            id='systems_thinking',
            name='Systems Thinking',
            description='Focus on interconnections over individual parts. Feedback loops create behavior. Emergence arises from interactions. See the whole system, not just components.',
            principles=[
                'Focus on interconnections over individual parts',
                'Feedback loops create system behavior',
                'Emergence from interactions',
                'Non-linear causality'
            ],
            prompt_injection='Analyze interconnections between components. Identify feedback loops and their effects. Look for emergent properties that arise from interactions. Consider non-linear causality.',
            applies_to=['grids', 'sigils', 'signals'],
            active_on_pages=['patterns', 'code', 'projects'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['system', 'systems', 'feedback', 'loop', 'emergence', 'interconnection', 'complexity'],
            category_triggers=['grids'],
            enabled=True
        )
        
        self.models['first_principles'] = MentalModel(
            id='first_principles',
            name='First Principles Thinking',
            description='Break down complex problems to fundamental truths, then reason up from there. Question assumptions. Build from ground truth rather than analogy.',
            principles=[
                'Break down to fundamental truths',
                'Question all assumptions',
                'Reason up from first principles',
                'Avoid reasoning by analogy alone'
            ],
            prompt_injection='Break this down to first principles. What are the fundamental truths? What assumptions can we question? Reason up from ground truth rather than using analogy alone.',
            applies_to=['sigils', 'grids'],
            active_on_pages=['code', 'projects', 'patterns'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['first principles', 'fundamental', 'assumption', 'ground truth', 'reason', 'analogy'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['design_thinking'] = MentalModel(
            id='design_thinking',
            name='Design Thinking',
            description='Human-centered approach to innovation. Empathize with users, define problems clearly, ideate solutions, prototype quickly, test and iterate.',
            principles=[
                'Empathize with users and stakeholders',
                'Define problems clearly before solving',
                'Ideate broadly before converging',
                'Prototype quickly to test ideas',
                'Test, learn, and iterate'
            ],
            prompt_injection='Start by empathizing with users. Define the problem clearly. Ideate multiple solutions. Prototype quickly. Test and iterate based on feedback. Keep the human experience central.',
            applies_to=['glyphs', 'sigils', 'scrolls'],
            active_on_pages=['projects', 'code', 'notes'],
            active_for_personas=['architect'],
            active_for_modes=['plan', 'build'],
            keywords=['design', 'thinking', 'empathize', 'prototype', 'iterate', 'user', 'human-centered'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 4: COMMUNICATION & COORDINATION (Future-proof for Phase 20, 22)
        
        self.models['inbox_zero'] = MentalModel(
            id='inbox_zero',
            name='Inbox Zero Philosophy',
            description='Process to empty, action orientation. Every message is an input to process, not a to-do item to store. Delete, delegate, respond, defer, or do—but don\'t just mark as read. Based on Merlin Mann\'s productivity system.',
            principles=[
                'Process to empty regularly',
                'Every message requires a decision',
                'Delete, delegate, respond, defer, or do',
                'Action orientation over passive storage'
            ],
            prompt_injection='When discussing email or message management, emphasize processing to empty. Every message requires a decision: delete, delegate, respond, defer, or do. Focus on action orientation over passive storage.',
            applies_to=['scrolls'],
            active_on_pages=['mail'],
            active_for_personas=[],
            active_for_modes=[],
            keywords=['inbox', 'zero', 'email', 'process', 'action', 'triage', 'merlin mann'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['async_first'] = MentalModel(
            id='async_first',
            name='Async-First Communication',
            description='Thoughtful, written communication over immediate synchronous responses. Document decisions, provide context, respect deep work time. Async by default, sync by exception.',
            principles=[
                'Written and thoughtful over immediate',
                'Document decisions for future reference',
                'Provide context, don\'t assume knowledge',
                'Respect deep work and focus time',
                'Async by default, sync by exception'
            ],
            prompt_injection='When discussing communication or collaboration, emphasize thoughtful written communication. Encourage documenting decisions and providing context. Respect focus time. Default to async, use sync only when necessary.',
            applies_to=['scrolls'],
            active_on_pages=['mail', 'notes'],
            active_for_personas=[],
            active_for_modes=[],
            keywords=['async', 'asynchronous', 'communication', 'written', 'document', 'context', 'deep work'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['time_blocking'] = MentalModel(
            id='time_blocking',
            name='Time Blocking',
            description='Protect focus time through intentional scheduling. Block time for deep work, batch similar tasks, minimize context switching. Inspired by Cal Newport\'s Deep Work methodology.',
            principles=[
                'Protect deep work time',
                'Batch similar tasks together',
                'Minimize context switching',
                'Schedule proactively, not reactively'
            ],
            prompt_injection='When discussing scheduling or productivity, emphasize protecting focus time. Suggest batching similar tasks. Minimize context switching. Encourage proactive rather than reactive scheduling.',
            applies_to=['grids'],
            active_on_pages=['calendar', 'projects'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['time', 'blocking', 'schedule', 'focus', 'deep work', 'batch', 'cal newport'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 5: AESTHETIC & CRAFT (Lines/monome philosophy)
        
        self.models['hyper_minimalism'] = MentalModel(
            id='hyper_minimalism',
            name='Hyper-Minimalism Test',
            description='Clarity through restraint. Every element must justify its existence. Embellishment is often excessive or distracting. Based on monome/Lines philosophy of doing more with less.',
            principles=[
                'Does this earn its place?',
                'What would removing it cost?',
                'Does it create options or close them?',
                'Embellishment is often excessive',
                'Clarity over decoration'
            ],
            prompt_injection='Before adding anything (feature, parameter, line of code, section): Ask "Can I articulate why this is necessary?" Try mentally deleting it—is the loss noticeable? Does this open possibilities or prescribe a path? Default to clarity over decoration.',
            applies_to=['sigils', 'signals', 'glyphs', 'scrolls'],
            active_on_pages=['code', 'projects', 'notes'],
            active_for_personas=['programmer', 'architect', 'scribe'],
            active_for_modes=[],
            keywords=['minimal', 'restraint', 'clarity', 'simplicity', 'essential', 'monome', 'lines'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['readability_ratchet'] = MentalModel(
            id='readability_ratchet',
            name='Readability Ratchet',
            description='Comprehension over cleverness. Code should reveal intent at a glance. Structure should guide understanding. Can someone else—or future you—understand this without mental gymnastics?',
            principles=[
                'Can someone else understand this?',
                'Does structure reveal intent?',
                'Comprehension over cleverness',
                'Future-you should thank present-you',
                'Naming matters more than you think'
            ],
            prompt_injection='When writing code: Use 2-space indentation. Prefer snake_case for variables/functions. Name things clearly—comprehension over brevity. Keep functions small and focused. Add comments for "why" not "what". Structure should guide the reader naturally.',
            applies_to=['sigils'],
            active_on_pages=['code'],
            active_for_personas=['programmer'],
            active_for_modes=[],
            keywords=['readable', 'comprehension', 'clarity', 'intent', 'naming', 'structure'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['local_variables'] = MentalModel(
            id='local_variables',
            name='Local Variables Principle',
            description='Keep scope narrow. Don\'t pollute shared space. Locality reduces cognitive load and prevents unintended interactions. Like a well-organized desk—everything has its place.',
            principles=[
                'Keep scope as narrow as possible',
                'Avoid global state when possible',
                'Locality reduces cognitive load',
                'Minimize unintended interactions',
                'Encapsulation prevents pollution'
            ],
            prompt_injection='When writing code, prefer local variables over global state. Keep scope narrow. Encapsulate related data and behavior. Minimize side effects. Make dependencies explicit rather than implicit.',
            applies_to=['sigils'],
            active_on_pages=['code'],
            active_for_personas=['programmer', 'architect'],
            active_for_modes=[],
            keywords=['scope', 'local', 'encapsulation', 'state', 'isolation', 'dependencies'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['instrument_standard'] = MentalModel(
            id='instrument_standard',
            name='Instrument Standard',
            description='Does it invite play? Does it disappear in use? Does it reward depth over time? Tools should be generative, transparent, and endlessly explorable. Inspired by monome hardware philosophy.',
            principles=[
                'Does it invite play and exploration?',
                'Does it disappear in use (transparency)?',
                'Does it reward depth over time?',
                'Is it generative (enables creation)?',
                'Does it respect the user\'s intelligence?'
            ],
            prompt_injection='When designing tools or interfaces: Make them inviting to explore. Minimize UI chrome—let the tool disappear. Reward depth with more capability. Enable creation rather than prescribing outcomes. Trust user intelligence.',
            applies_to=['sigils', 'glyphs', 'signals'],
            active_on_pages=['code', 'projects'],
            active_for_personas=['architect', 'programmer'],
            active_for_modes=['plan', 'build'],
            keywords=['instrument', 'tool', 'generative', 'interface', 'exploration', 'depth', 'monome'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['sustainability_lens'] = MentalModel(
            id='sustainability_lens',
            name='Sustainability Lens',
            description='Who maintains this? What does it depend on? Can it survive without constant intervention? Local sourcing over global dependencies. Inspired by monome\'s approach to manufacturing and community.',
            principles=[
                'Who maintains this long-term?',
                'What are the dependencies?',
                'Can it survive without constant care?',
                'Local sourcing over global dependencies',
                'Community sustainability matters'
            ],
            prompt_injection='When making technical decisions: Consider long-term maintenance burden. Prefer stable, well-maintained dependencies. Document for future maintainers. Design for graceful degradation. Think about community sustainability.',
            applies_to=['sigils', 'signals', 'scrolls'],
            active_on_pages=['code', 'projects'],
            active_for_personas=['architect', 'programmer'],
            active_for_modes=['plan'],
            keywords=['sustainability', 'maintenance', 'dependencies', 'longevity', 'community'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['signal_to_noise'] = MentalModel(
            id='signal_to_noise',
            name='Signal-to-Noise Ratio',
            description='What\'s the core message? What\'s supporting vs. distracting? High signal-to-noise means every element carries meaning. Cut the cruft.',
            principles=[
                'What is the core message?',
                'What supports vs. what distracts?',
                'Every element should carry meaning',
                'Reduce noise to amplify signal',
                'Brevity with substance over verbose filler'
            ],
            prompt_injection='When writing or designing: Identify the core message first. Remove elements that don\'t support it. Cut verbose filler—aim for brevity with substance. Every word, line, or component should earn its place.',
            applies_to=['scrolls', 'glyphs', 'sigils'],
            active_on_pages=['notes', 'code', 'projects'],
            active_for_personas=['scribe', 'programmer', 'architect'],
            active_for_modes=[],
            keywords=['signal', 'noise', 'clarity', 'focus', 'message', 'brevity', 'substance'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['generous_interface'] = MentalModel(
            id='generous_interface',
            name='Generous Interface',
            description='Assume good intent. Fail gracefully. Reward exploration. Give helpful error messages. Make the system forgiving and teachable. Guide without restricting.',
            principles=[
                'Assume good intent from users',
                'Fail gracefully with helpful messages',
                'Reward exploration and experimentation',
                'Guide without restricting',
                'Make errors teachable moments'
            ],
            prompt_injection='When designing user-facing systems: Assume good intent. Provide helpful error messages that explain what went wrong and how to fix it. Make exploration safe—let users experiment without fear. Guide gently rather than restrict harshly.',
            applies_to=['sigils', 'glyphs', 'signals'],
            active_on_pages=['code', 'projects'],
            active_for_personas=['programmer', 'architect'],
            active_for_modes=[],
            keywords=['interface', 'errors', 'forgiving', 'helpful', 'exploration', 'guidance'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 6: DECISION-MAKING
        
        self.models['constraint_based_filter'] = MentalModel(
            id='constraint_based_filter',
            name='Constraint-Based Filter',
            description='Before starting new work, ask: What\'s available right now? What\'s asking to be continued? What serves multiple domains? Let constraints guide decisions rather than abstract possibility.',
            principles=[
                'What\'s available and ready right now?',
                'What\'s asking to be continued?',
                'What serves multiple domains?',
                'Let constraints filter choices',
                'Start with what\'s accessible, not what\'s ideal'
            ],
            prompt_injection='When faced with multiple options: First identify what\'s immediately available. Look for work that\'s partially complete and asking for continuation. Prioritize choices that serve multiple domains or goals. Use constraints as filters rather than fighting them.',
            applies_to=['sigils', 'scrolls', 'grids'],
            active_on_pages=['projects', 'notes', 'dashboard'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['constraint', 'filter', 'decision', 'priority', 'available', 'continuation'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['compound_question'] = MentalModel(
            id='compound_question',
            name='Compound Question',
            description='Which choice makes future choices easier? Decisions compound over time. Choose paths that open possibilities rather than close them. Think second-order consequences.',
            principles=[
                'Which choice makes future choices easier?',
                'What opens vs. closes future possibilities?',
                'Consider second-order consequences',
                'Small decisions compound over time',
                'Reversibility matters'
            ],
            prompt_injection='When making decisions: Ask "Which option makes future choices easier?" Consider whether this opens or closes future possibilities. Think about second-order effects. Prefer reversible decisions when possible. Remember that small choices compound.',
            applies_to=['sigils', 'grids', 'scrolls'],
            active_on_pages=['projects', 'code'],
            active_for_personas=['architect', 'programmer'],
            active_for_modes=['plan'],
            keywords=['decision', 'compound', 'future', 'consequences', 'possibilities', 'reversible'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['delegation_test'] = MentalModel(
            id='delegation_test',
            name='Delegation Test',
            description='Should I do, delegate, or automate this? If it\'s recurring and definable, automate. If it requires specific skills someone else has, delegate. If it needs your unique judgment, do it.',
            principles=[
                'Recurring and definable → Automate',
                'Requires specific skills → Delegate',
                'Needs unique judgment → Do it yourself',
                'Time investment vs. frequency tradeoff',
                'Document for future automation or delegation'
            ],
            prompt_injection='When faced with a task: Ask whether it\'s recurring and rule-based (automate), requires skills others have (delegate), or needs your specific judgment (do it). Consider time investment vs. frequency. Document processes for future handoff.',
            applies_to=['sigils', 'scrolls', 'grids'],
            active_on_pages=['projects', 'code', 'dashboard'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['delegation', 'automation', 'decision', 'efficiency', 'process', 'handoff'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['reverse_engineering_frame'] = MentalModel(
            id='reverse_engineering_frame',
            name='Reverse Engineering Frame',
            description='What does "done" look like? What\'s the last step before completion? Work backwards from the goal. This clarifies dependencies and reveals the critical path.',
            principles=[
                'Start with the end state clearly defined',
                'What\'s the last step before done?',
                'Work backwards to identify dependencies',
                'Reveals the critical path',
                'Prevents scope creep'
            ],
            prompt_injection='When planning work: First define what "done" looks like clearly. Identify the very last step before completion. Work backwards to map dependencies. This reveals the critical path and prevents scope creep. Keep the end goal crisp.',
            applies_to=['sigils', 'scrolls', 'grids'],
            active_on_pages=['projects', 'code'],
            active_for_personas=['architect', 'programmer'],
            active_for_modes=['plan'],
            keywords=['reverse', 'backwards', 'goal', 'done', 'completion', 'dependencies', 'critical path'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 7: WORKFLOW & PROCESS
        
        self.models['continuation_probe'] = MentalModel(
            id='continuation_probe',
            name='Continuation Probe',
            description='Before starting new work, ask: What\'s 80% done? What\'s blocked but could be unblocked? Finishing creates momentum. Starting creates friction. Bias toward continuation.',
            principles=[
                'What\'s 80% done?',
                'What\'s blocked but unblockable now?',
                'Finishing creates momentum',
                'Starting creates friction',
                'Completion over novelty'
            ],
            prompt_injection='Before starting something new: Scan for work that\'s 80% complete. Look for blocked items that could be unblocked now. Finishing builds momentum and clears mental space. Bias toward continuation over novelty unless there\'s a compelling reason to start fresh.',
            applies_to=['sigils', 'scrolls', 'grids'],
            active_on_pages=['projects', 'code', 'notes', 'dashboard'],
            active_for_personas=['architect', 'programmer', 'scribe'],
            active_for_modes=[],
            keywords=['continuation', 'completion', 'momentum', 'finish', 'blocked', 'progress'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['context_capture'] = MentalModel(
            id='context_capture',
            name='Context Capture',
            description='When stopping work: What would I need to know to continue this? Capture state, decisions made, next steps. Future-you will thank present-you for the breadcrumbs.',
            principles=[
                'What would I need to know to continue?',
                'Capture current state clearly',
                'Document decisions and reasoning',
                'Note next steps explicitly',
                'Leave breadcrumbs for future-you'
            ],
            prompt_injection='When stopping work or switching contexts: Document where you are, what decisions you made and why, and what the next clear step is. Write for someone (including future-you) picking this up cold. Leave clear breadcrumbs.',
            applies_to=['scrolls', 'sigils', 'grids'],
            active_on_pages=['notes', 'code', 'projects'],
            active_for_personas=['scribe', 'programmer', 'architect'],
            active_for_modes=[],
            keywords=['context', 'capture', 'state', 'breadcrumbs', 'documentation', 'continuation'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['good_enough_threshold'] = MentalModel(
            id='good_enough_threshold',
            name='Good Enough Threshold',
            description='What\'s good enough to learn from? Perfect is the enemy of shipped. Get to the learning threshold, then iterate based on real feedback rather than imagined needs.',
            principles=[
                'What\'s good enough to learn from?',
                'Perfect is the enemy of shipped',
                'Real feedback beats imagined perfection',
                'Ship to learn, iterate to improve',
                'Define "done enough" before starting'
            ],
            prompt_injection='When building something: Define "good enough to learn from" before starting. Ship at that threshold. Iterate based on real feedback rather than imagined needs. Avoid premature optimization. Progress over perfection.',
            applies_to=['sigils', 'glyphs', 'scrolls'],
            active_on_pages=['code', 'projects', 'notes'],
            active_for_personas=['programmer', 'architect', 'scribe'],
            active_for_modes=['build'],
            keywords=['good enough', 'threshold', 'shipping', 'iteration', 'feedback', 'progress', 'done'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['friction_audit'] = MentalModel(
            id='friction_audit',
            name='Friction Audit',
            description='Where is energy leaking? Track activation friction (starting), continuation friction (maintaining flow), and completion friction (finishing). Reduce friction strategically.',
            principles=[
                'Where is energy leaking in the process?',
                'Activation friction (starting is hard)',
                'Continuation friction (maintaining flow)',
                'Completion friction (finishing is hard)',
                'Reduce friction strategically'
            ],
            prompt_injection='When evaluating workflows: Identify where friction occurs—starting (activation), maintaining flow (continuation), or finishing (completion). Measure energy leakage. Reduce friction strategically at the highest-impact points. Make the desired behavior easier.',
            applies_to=['grids', 'sigils', 'scrolls'],
            active_on_pages=['projects', 'dashboard', 'code'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['friction', 'energy', 'workflow', 'process', 'activation', 'completion', 'flow'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['two_week_test'] = MentalModel(
            id='two_week_test',
            name='Two-Week Test',
            description='Will this still make sense in two weeks? Names, structure, and decisions should be comprehensible to someone—including future-you—returning to the code cold.',
            principles=[
                'Will this make sense in two weeks?',
                'Name things for future comprehension',
                'Structure for someone returning cold',
                'Document the "why" for decisions',
                'Optimize for future understanding'
            ],
            prompt_injection='When writing code or making decisions: Ask "Will this make sense in two weeks?" Name things clearly for future readers. Structure for comprehension by someone returning cold. Document the reasoning behind non-obvious choices.',
            applies_to=['sigils', 'scrolls'],
            active_on_pages=['code', 'notes'],
            active_for_personas=['programmer', 'scribe'],
            active_for_modes=[],
            keywords=['comprehension', 'future', 'clarity', 'naming', 'documentation', 'maintainability'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 8: ARCHITECT-SPECIFIC
        
        self.models['map_before_territory'] = MentalModel(
            id='map_before_territory',
            name='Map Before Territory',
            description='Before diving into implementation: What are the boundaries? What are the flows? What are the constraints? Map the territory first. Anchor documents and diagrams pay dividends.',
            principles=[
                'Map the territory before building',
                'Define boundaries clearly',
                'Identify flows between components',
                'Surface constraints early',
                'Anchor documents pay dividends'
            ],
            prompt_injection='When starting a project: Create a map before diving into territory. Define boundaries, identify major flows, surface constraints. Write an anchor document or draw a diagram. This upfront investment pays dividends throughout implementation.',
            applies_to=['sigils', 'grids', 'scrolls'],
            active_on_pages=['projects', 'code'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['map', 'territory', 'boundaries', 'architecture', 'anchor', 'diagram', 'overview'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['three_altitudes'] = MentalModel(
            id='three_altitudes',
            name='Three Altitudes',
            description='Navigate between three levels: 30,000 ft (purpose and vision), 10,000 ft (components and flows), ground level (implementation details). Good architects move fluidly between altitudes.',
            principles=[
                '30,000 ft: Purpose and vision (why)',
                '10,000 ft: Components and flows (what)',
                'Ground level: Implementation details (how)',
                'Move fluidly between altitudes',
                'Connect decisions across levels'
            ],
            prompt_injection='When architecting: Operate at three altitudes. At 30,000 ft, clarify purpose and vision. At 10,000 ft, design components and flows. At ground level, handle implementation. Move fluidly between levels. Connect decisions across altitudes.',
            applies_to=['sigils', 'grids', 'scrolls'],
            active_on_pages=['projects', 'code'],
            active_for_personas=['architect'],
            active_for_modes=['plan'],
            keywords=['altitude', 'levels', 'architecture', 'purpose', 'components', 'implementation', 'vision'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['anchor_document'] = MentalModel(
            id='anchor_document',
            name='Anchor Document',
            description='Every significant project needs an anchor: What is this? Why does it exist? What are the major components? How do they relate? Keep it current. Link to it everywhere.',
            principles=[
                'What is this project?',
                'Why does it exist?',
                'What are the major components?',
                'How do they relate to each other?',
                'Keep it current and link to it'
            ],
            prompt_injection='For significant projects: Create an anchor document that answers: What is this? Why? Major components? Relationships? Keep it updated. Link to it from README, docs, and onboarding. It\'s the entry point for understanding.',
            applies_to=['scrolls', 'sigils'],
            active_on_pages=['projects', 'notes'],
            active_for_personas=['architect', 'scribe'],
            active_for_modes=['plan'],
            keywords=['anchor', 'document', 'overview', 'readme', 'documentation', 'entry point', 'orientation'],
            category_triggers=[],
            enabled=True
        )
        
        # TIER 9: CROSS-DOMAIN THINKING
        
        self.models['domain_bridge'] = MentalModel(
            id='domain_bridge',
            name='Domain Bridge',
            description='What would this problem look like in a different domain? Music, architecture, cooking, gardening—analogies from other fields often reveal novel solutions. Cross-pollination breeds insight.',
            principles=[
                'What would this look like in another domain?',
                'Draw analogies from other fields',
                'Music, architecture, cooking, nature',
                'Cross-pollination reveals insights',
                'Constraints in one domain may not apply in another'
            ],
            prompt_injection='When stuck on a problem: Ask "What would this look like in music? In architecture? In cooking?" Draw analogies from other domains. Cross-pollination often reveals novel approaches. Constraints from one field may not apply in another.',
            applies_to=['sigils', 'scrolls', 'glyphs', 'grids'],
            active_on_pages=['projects', 'learning', 'patterns'],
            active_for_personas=['architect', 'professor'],
            active_for_modes=[],
            keywords=['domain', 'bridge', 'analogy', 'cross-pollination', 'metaphor', 'insight', 'transfer'],
            category_triggers=[],
            enabled=True
        )
        
        self.models['problem_posing_pivot'] = MentalModel(
            id='problem_posing_pivot',
            name='Problem-Posing Pivot',
            description='What question is the human actually holding? Often the stated question isn\'t the real one. Listen for the question beneath the question. Reframe to reveal the true problem.',
            principles=[
                'What question is really being asked?',
                'Listen for the question beneath the question',
                'Stated problem ≠ actual problem',
                'Reframe to reveal true issues',
                'Ask clarifying questions before solving'
            ],
            prompt_injection='When someone asks a question: Listen for the question beneath the question. The stated problem often isn\'t the real one. Ask clarifying questions. Reframe to reveal the true issue before jumping to solutions. Problem-posing before problem-solving.',
            applies_to=['scrolls', 'grids'],
            active_on_pages=['learning', 'dashboard', 'notes'],
            active_for_personas=['professor', 'architect'],
            active_for_modes=['socratic', 'guide'],
            keywords=['problem', 'posing', 'reframe', 'question', 'clarify', 'underlying', 'real issue'],
            category_triggers=[],
            enabled=True
        )
        
        logger.info(f"Created {len(self.models)} default mental models")

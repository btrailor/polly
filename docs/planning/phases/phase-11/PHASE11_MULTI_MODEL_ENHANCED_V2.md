# Phase 11: Multi-Model Intelligent Routing (Enhanced V2)

**Version:** 2.0  
**Status:** Planning  
**Duration:** 5 weeks (split into 3 sub-phases)  
**Prerequisites:** Phase 16 (Native Notes Frontend) ✅ Complete  
**Next Phase:** Phase 16c (AI Note Creation)

---

## Executive Summary

Phase 11 implements a comprehensive multi-provider AI routing system that intelligently selects between 8 cloud AI providers based on task complexity, cost, performance, and user preferences. This phase establishes the foundation for agentic personas and advanced orchestration while maintaining strong safety controls.

**Key Deliverables:**
- Support for 8 cloud AI providers (Anthropic, OpenAI, GitHub Copilot, OpenRouter, Google AI, Mistral AI, Grok, Perplexity)
- Three-layer confidence routing system (Fast, Balanced, Thorough)
- Content safety filters for Grok integration
- Cross-platform encrypted secrets management
- Basic compression system for conversation context
- Architect persona framework with Plan/Build modes
- Cost optimization and budget controls

---

## Architecture Overview

### Provider Priority Tiers

**Essential Providers (Phase 11a):**
1. **Anthropic** - Claude Haiku, Sonnet 4, Opus 4
2. **OpenAI** - GPT-3.5-turbo, GPT-4, GPT-4o
3. **GitHub Copilot** - Already have OAuth integration

**Extended Providers (Phase 11b):**
4. **OpenRouter** - Access to 100+ models via unified API
5. **Google AI** - Gemini 1.5 Pro, Gemini 2.0 Flash
6. **Mistral AI** - Mistral Small, Medium, Large
7. **Grok (xAI)** - With mandatory content safety filters
8. **Perplexity** - Optional, not all users have Pro

### Three-Layer Routing Strategy

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Intent Classification                      │
│  • Task type (code, notes, search, etc.)               │
│  • Complexity score (1-10)                             │
│  • Context size                                         │
│  • User confidence preference                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
    ┌──────────────┐           ┌──────────────┐
    │  Fast Tier   │           │ Balanced Tier│
    │ (Low Cost)   │           │ (Mid Cost)   │
    │              │           │              │
    │ Haiku        │           │ Sonnet 4     │
    │ GPT-3.5      │           │ GPT-4        │
    │ Gemini Flash │           │ Gemini Pro   │
    └──────────────┘           └──────────────┘
                          │
                          ▼
                  ┌──────────────┐
                  │Thorough Tier │
                  │ (High Cost)  │
                  │              │
                  │ Opus 4       │
                  │ GPT-4o       │
                  │ o1-preview   │
                  └──────────────┘
```

### Safety Filter Architecture (Grok-Specific)

```python
┌─────────────────────────────────────────────────────────┐
│                  Grok Request                           │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Pre-Request Validation                     │
│  ✓ Task type in whitelist?                            │
│  ✗ Task type in blacklist?                            │
└─────────────────────────────────────────────────────────┘
                          │
                    Pass  │  Fail → Route to different provider
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Grok API Call                              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           Post-Response Content Filtering               │
│  • Conspiracy pattern matching                         │
│  • Extremist content detection                         │
│  • Misinformation flags                                │
└─────────────────────────────────────────────────────────┘
                          │
                    Clean │  Flagged → Discard & fallback
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Return to User                             │
└─────────────────────────────────────────────────────────┘
```

---

## Phase Breakdown

### Phase 11a: Core Routing + Primary Providers (2 weeks)

**Week 1: Multi-Provider Infrastructure**

Days 1-2: Unified Provider Interface
```python
# core/providers/base.py
class ProviderAdapter(ABC):
    """Base class for all AI provider adapters"""
    
    @abstractmethod
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        pass
    
    @abstractmethod
    async def stream(self, messages: list[dict], **kwargs) -> AsyncIterator[str]:
        pass
    
    @abstractmethod
    def get_models(self) -> list[ModelInfo]:
        pass
    
    @abstractmethod
    def estimate_cost(self, tokens: int, model: str) -> float:
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        pass
```

Days 3-4: Provider Implementations
- `core/providers/anthropic.py` - Claude models
- `core/providers/openai.py` - GPT models
- `core/providers/github.py` - GitHub Copilot (reuse existing OAuth)

Days 5-7: Router Core
```python
# core/router_v2.py
class IntelligentRouter:
    def __init__(self, config: Config):
        self.providers: dict[str, ProviderAdapter] = {}
        self.tier_config = config.get("routing.tiers")
        self.budget_manager = BudgetManager(config)
    
    async def route(self, 
                   messages: list[dict], 
                   task_type: str,
                   confidence: str = "balanced") -> ProviderAdapter:
        """
        Route request to appropriate provider based on:
        - Task complexity
        - Confidence tier (fast/balanced/thorough)
        - Cost budget
        - Provider availability
        """
        complexity = self._classify_complexity(messages, task_type)
        candidates = self._get_tier_candidates(confidence, complexity)
        
        # Apply filters
        candidates = self._filter_by_budget(candidates)
        candidates = self._filter_by_availability(candidates)
        
        # Select best option
        return self._select_provider(candidates, task_type)
    
    def _classify_complexity(self, messages: list[dict], task_type: str) -> int:
        """Return complexity score 1-10"""
        score = 5  # baseline
        
        # Adjust based on context size
        total_tokens = sum(len(m["content"].split()) * 1.3 for m in messages)
        if total_tokens > 10000:
            score += 2
        elif total_tokens > 5000:
            score += 1
        
        # Adjust based on task type
        if task_type in ["refactoring", "architecture", "debugging"]:
            score += 2
        elif task_type in ["code_completion", "simple_query"]:
            score -= 1
        
        return min(10, max(1, score))
```

**Week 2: Three-Layer Confidence System**

Days 8-10: Tier Configuration
```yaml
# config.yaml additions
routing:
  tiers:
    fast:
      max_cost_per_request: 0.01
      models:
        - provider: anthropic
          model: claude-3-haiku-20240307
          priority: 1
        - provider: openai
          model: gpt-3.5-turbo
          priority: 2
        - provider: google
          model: gemini-2.0-flash
          priority: 3
    
    balanced:
      max_cost_per_request: 0.10
      models:
        - provider: anthropic
          model: claude-sonnet-4-20250514
          priority: 1
        - provider: openai
          model: gpt-4-turbo
          priority: 2
        - provider: google
          model: gemini-1.5-pro
          priority: 3
    
    thorough:
      max_cost_per_request: 1.00
      models:
        - provider: anthropic
          model: claude-opus-4-20250514
          priority: 1
        - provider: openai
          model: gpt-4o
          priority: 2
        - provider: openai
          model: o1-preview
          priority: 3

  budget:
    daily_limit: 10.00
    monthly_limit: 200.00
    warn_at_percent: 80
```

Days 11-12: Budget Management
```python
# core/budget_manager.py
class BudgetManager:
    def __init__(self, config: Config):
        self.daily_limit = config.get("routing.budget.daily_limit")
        self.monthly_limit = config.get("routing.budget.monthly_limit")
        self.db = Database()
    
    async def check_budget(self, estimated_cost: float) -> bool:
        """Return True if request is within budget"""
        daily_spent = await self._get_daily_spending()
        monthly_spent = await self._get_monthly_spending()
        
        if daily_spent + estimated_cost > self.daily_limit:
            return False
        if monthly_spent + estimated_cost > self.monthly_limit:
            return False
        
        return True
    
    async def record_usage(self, provider: str, model: str, 
                          tokens_in: int, tokens_out: int, cost: float):
        """Log API usage for budget tracking"""
        await self.db.insert("api_usage", {
            "timestamp": datetime.now(),
            "provider": provider,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost": cost
        })
```

Days 13-14: Settings UI
- Add "Models > Providers" section to settings
- Display provider status (connected, API key valid, models available)
- Configure tier preferences per provider
- View budget usage charts

**Deliverables (Phase 11a):**
- ✅ Unified provider interface working
- ✅ Anthropic, OpenAI, GitHub Copilot integrated
- ✅ Three-tier routing system operational
- ✅ Budget tracking and limits enforced
- ✅ Settings UI for provider management

---

### Phase 11b: Extended Providers + Safety (2 weeks)

**Week 3: Extended Provider Integration**

Days 15-16: OpenRouter Integration
```python
# core/providers/openrouter.py
class OpenRouterAdapter(ProviderAdapter):
    """
    OpenRouter provides access to 100+ models through unified API
    Key features:
    - Single API key for multiple providers
    - Automatic fallback between models
    - Cost optimization
    """
    
    AVAILABLE_MODELS = [
        # Premium models
        "anthropic/claude-opus-4",
        "openai/gpt-4o",
        "google/gemini-2.0-pro",
        
        # Mid-tier models
        "anthropic/claude-sonnet-4",
        "openai/gpt-4-turbo",
        "meta-llama/llama-3.1-70b",
        
        # Budget models
        "anthropic/claude-haiku",
        "openai/gpt-3.5-turbo",
        "mistralai/mistral-small"
    ]
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        # OpenRouter uses OpenAI-compatible API
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", "anthropic/claude-sonnet-4"),
            messages=messages,
            extra_headers={
                "HTTP-Referer": "https://polly.app",
                "X-Title": "Polly"
            }
        )
        return self._parse_response(response)
```

Days 17-18: Google AI + Mistral AI
```python
# core/providers/google.py
class GoogleAIAdapter(ProviderAdapter):
    """Google Gemini models"""
    
    MODELS = {
        "gemini-2.0-flash": {
            "input_cost_per_1m": 0.075,
            "output_cost_per_1m": 0.30,
            "context_window": 1000000
        },
        "gemini-1.5-pro": {
            "input_cost_per_1m": 1.25,
            "output_cost_per_1m": 5.00,
            "context_window": 2000000
        }
    }

# core/providers/mistral.py
class MistralAdapter(ProviderAdapter):
    """Mistral AI models"""
    
    MODELS = {
        "mistral-small": {"input": 0.20, "output": 0.60},
        "mistral-medium": {"input": 2.70, "output": 8.10},
        "mistral-large": {"input": 4.00, "output": 12.00}
    }
```

Days 19-21: Perplexity Integration (Optional)
```python
# core/providers/perplexity.py
class PerplexityAdapter(ProviderAdapter):
    """
    Perplexity Online LLMs
    Note: Requires Pro subscription, optional integration
    """
    
    MODELS = {
        "sonar-pro": {"with_search": True, "online": True},
        "sonar": {"with_search": True, "online": True}
    }
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        # Perplexity-specific: online search integration
        return await self._complete_with_search(messages, **kwargs)
```

**Week 4: Grok + Safety Filters**

Days 22-23: Grok Integration
```python
# core/providers/grok.py
class GrokAdapter(ProviderAdapter):
    """
    Grok (xAI) integration with mandatory safety filters
    
    WARNING: Grok outputs require content filtering due to
    concerns about conspiratorial thinking and extremist content.
    """
    
    def __init__(self, api_key: str, safety_filter: GrokSafetyFilter):
        super().__init__(api_key)
        self.safety = safety_filter
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        task_type = kwargs.get("task_type", "general")
        
        # Pre-request validation
        if not self.safety.is_task_allowed(task_type):
            raise GrokTaskForbiddenError(
                f"Grok is not allowed for task type: {task_type}"
            )
        
        # Make API call
        response = await self.client.chat.completions.create(
            model="grok-2",
            messages=messages
        )
        
        # Post-response filtering
        is_safe, flags = self.safety.validate_content(response.content)
        if not is_safe:
            logger.warning(f"Grok response filtered: {flags}")
            raise GrokContentFilteredError(
                "Response contained unsafe content",
                flags=flags
            )
        
        return self._parse_response(response)
```

Days 24-26: Safety Filter Implementation
```python
# core/safety/grok_filter.py
class GrokSafetyFilter:
    """Content safety filter for Grok responses"""
    
    # Tasks where Grok is ALLOWED
    WHITELIST_TASKS = [
        "code_completion",
        "code_review",
        "technical_explanation",
        "data_analysis",
        "math_problems",
        "translation",
        "code_debugging",
        "api_documentation"
    ]
    
    # Tasks where Grok is FORBIDDEN
    BLACKLIST_TASKS = [
        "political_analysis",
        "historical_events",
        "medical_advice",
        "news_summary",
        "social_issues",
        "current_events",
        "health_diagnosis",
        "legal_advice"
    ]
    
    # Content patterns to flag
    RED_FLAGS = {
        "conspiracy_patterns": [
            r"\b(deep state|cabal|illuminati|new world order)\b",
            r"\b(hoax|false flag|crisis actors)\b",
            r"\b(they don't want you to know|wake up|sheeple)\b"
        ],
        "extremist_patterns": [
            r"\b(nazi|fascist|supremacist)\b.*\b(good|right|correct)\b",
            r"\b(jews|blacks|muslims|immigrants).*\b(control|conspiracy)\b",
            r"\b(race war|civil war|revolution|uprising)\b"
        ],
        "misinformation_patterns": [
            r"\b(vaccines|election).*\b(fake|fraud|rigged)\b",
            r"\b(covid|pandemic).*\b(hoax|planned)\b",
            r"\b(media|government).*\b(lying|hiding|covering up)\b"
        ]
    }
    
    def is_task_allowed(self, task_type: str) -> bool:
        """Check if task type is in whitelist"""
        if task_type in self.BLACKLIST_TASKS:
            return False
        return task_type in self.WHITELIST_TASKS
    
    def validate_content(self, content: str) -> tuple[bool, list[str]]:
        """
        Validate response content for safety issues
        
        Returns:
            (is_safe, list_of_flags)
        """
        flags = []
        content_lower = content.lower()
        
        for category, patterns in self.RED_FLAGS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    flags.append(f"{category}:{pattern}")
        
        return (len(flags) == 0, flags)
    
    def get_user_consent(self) -> bool:
        """
        Check if user has consented to Grok usage
        (One-time prompt when Grok is first enabled)
        """
        # Display warning dialog in UI
        return self._show_consent_dialog()
```

Days 27-28: Provider Fallback Chains
```python
# core/router_v2.py (additions)
class IntelligentRouter:
    async def complete_with_fallback(self, 
                                    messages: list[dict],
                                    task_type: str,
                                    confidence: str = "balanced") -> CompletionResponse:
        """
        Attempt completion with fallback chain on failure
        """
        primary = await self.route(messages, task_type, confidence)
        fallback_chain = self._get_fallback_chain(primary, confidence)
        
        for provider in [primary] + fallback_chain:
            try:
                response = await provider.complete(messages, task_type=task_type)
                
                # Record success
                await self.budget_manager.record_usage(
                    provider.name,
                    provider.current_model,
                    response.tokens_in,
                    response.tokens_out,
                    response.cost
                )
                
                return response
                
            except (APIError, RateLimitError, GrokContentFilteredError) as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue
        
        raise AllProvidersFailed("All providers in fallback chain failed")
    
    def _get_fallback_chain(self, 
                           primary: ProviderAdapter, 
                           confidence: str) -> list[ProviderAdapter]:
        """
        Return ordered list of fallback providers
        
        Example chains:
        - Fast tier: Haiku → GPT-3.5 → Gemini Flash
        - Balanced tier: Sonnet 4 → GPT-4 → Gemini Pro
        - Thorough tier: Opus 4 → GPT-4o → Sonnet 4
        """
        tier_models = self.tier_config[confidence]["models"]
        return [
            self.providers[m["provider"]]
            for m in tier_models
            if m["provider"] != primary.name
        ]
```

**Deliverables (Phase 11b):**
- ✅ OpenRouter, Google AI, Mistral AI, Perplexity integrated
- ✅ Grok integration with content safety filters
- ✅ Provider fallback chains working
- ✅ Safety filter UI (Grok consent dialog)
- ✅ Extended settings UI for all 8 providers

---

### Phase 11c: Orchestration + Compression (1 week)

**Week 5: Cost Optimization & Agent Framework**

Days 29-30: Cost Optimization
```python
# core/optimizer.py
class CostOptimizer:
    """Optimize provider selection based on cost/performance"""
    
    def __init__(self, router: IntelligentRouter):
        self.router = router
        self.performance_db = PerformanceDatabase()
    
    async def optimize_route(self, 
                            messages: list[dict],
                            task_type: str,
                            max_cost: float) -> ProviderAdapter:
        """
        Select provider with best cost/performance ratio
        
        Algorithm:
        1. Estimate tokens for request
        2. Get candidate providers within cost limit
        3. Rank by historical performance (quality score)
        4. Return best option
        """
        estimated_tokens = self._estimate_tokens(messages)
        candidates = []
        
        for provider in self.router.providers.values():
            cost = provider.estimate_cost(estimated_tokens, provider.default_model)
            if cost <= max_cost:
                quality = await self.performance_db.get_quality_score(
                    provider.name,
                    task_type
                )
                candidates.append((provider, cost, quality))
        
        # Sort by quality/cost ratio (higher is better)
        candidates.sort(key=lambda x: x[2] / x[1], reverse=True)
        
        return candidates[0][0] if candidates else None
```

Days 31-32: Compression System (Basic)
```python
# core/compression/compressor.py
class ConversationCompressor:
    """
    Compress conversations for extended context retention
    
    Goal: 100x reduction in tokens while preserving semantic meaning
    Format: Internal use only (humans never see compressed format)
    """
    
    def __init__(self):
        self.abbreviations = self._load_abbreviations()
    
    def compress(self, conversation: list[dict]) -> dict:
        """
        Compress conversation into structured metadata
        
        Output format:
        {
            "v": 1,                    # version
            "u": "Brett",              # user
            "m": "notes",              # mode
            "t": "note-creation",      # task
            "d": 3,                    # depth (turns)
            "dc": [                    # decisions
                {"t": "storage", "d": "user-config"},
                {"t": "templates", "d": "folder-based"}
            ],
            "f": "agentic-personas",   # focus topic
            "kc": [                    # key concepts
                "model-routing",
                "note-creation",
                "safety-filters"
            ],
            "ctx": {                   # critical context
                "providers": 8,
                "timeline": "5w",
                "safety": "grok-filter"
            }
        }
        """
        return {
            "v": 1,
            "u": self._extract_user(conversation),
            "m": self._detect_mode(conversation),
            "t": self._classify_task(conversation),
            "d": len(conversation) // 2,
            "dc": self._extract_decisions(conversation),
            "f": self._extract_focus(conversation),
            "kc": self._extract_keywords(conversation),
            "ctx": self._extract_critical_context(conversation)
        }
    
    def decompress(self, compressed: dict) -> str:
        """
        Convert compressed format back to natural language summary
        
        This is what Polly uses internally when loading old conversations
        """
        template = (
            "Previous conversation with {u} in {m} mode. "
            "Task: {t}. Discussed {f} over {d} turns. "
            "Key decisions: {decisions}. "
            "Important context: {ctx}. "
            "Keywords: {keywords}"
        )
        
        return template.format(
            u=compressed["u"],
            m=compressed["m"],
            t=compressed["t"],
            f=compressed["f"],
            d=compressed["d"],
            decisions=", ".join(d["d"] for d in compressed["dc"]),
            ctx=str(compressed["ctx"]),
            keywords=", ".join(compressed["kc"])
        )
```

Days 33-34: Architect Persona Framework
```python
# core/personas/architect.py
class ArchitectPersona:
    """
    Architect persona for planning and building complex tasks
    
    Modes:
    - Plan: Analyze requirements, ask questions, create outline
    - Build: Execute plan, create content, apply templates
    
    User manually toggles between modes (like OpenCode)
    """
    
    def __init__(self, router: IntelligentRouter):
        self.router = router
        self.mode = "plan"  # or "build"
        self.current_plan = None
    
    async def plan(self, user_request: str) -> Plan:
        """
        Planning mode: Analyze and create structured plan
        
        Steps:
        1. Analyze conversation context
        2. Identify unknowns
        3. Generate clarifying questions
        4. Create outline/roadmap
        """
        # Use balanced tier for planning (Sonnet 4 preferred)
        messages = [
            {"role": "system", "content": ARCHITECT_PLANNING_PROMPT},
            {"role": "user", "content": user_request}
        ]
        
        response = await self.router.complete_with_fallback(
            messages,
            task_type="planning",
            confidence="balanced"
        )
        
        # Parse response into structured plan
        plan = self._parse_plan(response.content)
        self.current_plan = plan
        return plan
    
    async def build(self, plan: Plan) -> BuildResult:
        """
        Building mode: Execute plan and create deliverables
        
        Steps:
        1. Load plan context
        2. Execute each step
        3. Apply templates (if creating notes)
        4. Validate output
        """
        # Use thorough tier for building (Opus 4 or Sonnet 4)
        messages = self._construct_build_messages(plan)
        
        response = await self.router.complete_with_fallback(
            messages,
            task_type="content_creation",
            confidence="thorough"
        )
        
        return BuildResult(
            content=response.content,
            tokens_used=response.tokens_in + response.tokens_out,
            cost=response.cost,
            provider=response.provider
        )
    
    def switch_mode(self, mode: str):
        """User manually switches between plan/build"""
        if mode not in ["plan", "build"]:
            raise ValueError("Mode must be 'plan' or 'build'")
        self.mode = mode

ARCHITECT_PLANNING_PROMPT = """You are Architect, Polly's planning persona.

Your job is to analyze user requests and create detailed, actionable plans.

Process:
1. Review conversation context
2. Identify what you know and what you need to clarify
3. Ask 2-5 targeted questions (if needed)
4. Create a structured outline or roadmap

Be concise but thorough. Focus on understanding intent before planning execution.
"""
```

Days 35: Testing & Integration
- End-to-end testing of all 8 providers
- Fallback chain validation
- Budget limit enforcement
- Safety filter testing (Grok)
- Architect persona demo

**Deliverables (Phase 11c):**
- ✅ Cost optimization system operational
- ✅ Basic compression system working
- ✅ Architect persona with Plan/Build modes
- ✅ Full integration testing complete
- ✅ Documentation updated

---

## Configuration Schema

```yaml
# ~/.polly/config.yaml

models:
  cloud:
    # Essential providers (Phase 11a)
    anthropic:
      enabled: true
      api_key: encrypted:${ANTHROPIC_API_KEY}
      default_model: claude-sonnet-4-20250514
      models:
        - claude-3-haiku-20240307
        - claude-sonnet-4-20250514
        - claude-opus-4-20250514
    
    openai:
      enabled: true
      api_key: encrypted:${OPENAI_API_KEY}
      default_model: gpt-4-turbo
      models:
        - gpt-3.5-turbo
        - gpt-4-turbo
        - gpt-4o
        - o1-preview
    
    github:
      enabled: true
      oauth_token: encrypted:${GITHUB_TOKEN}
      # Reuse existing GitHub Copilot integration
    
    # Extended providers (Phase 11b)
    openrouter:
      enabled: false
      api_key: encrypted:${OPENROUTER_API_KEY}
      default_model: anthropic/claude-sonnet-4
    
    google:
      enabled: false
      api_key: encrypted:${GOOGLE_AI_API_KEY}
      default_model: gemini-1.5-pro
    
    mistral:
      enabled: false
      api_key: encrypted:${MISTRAL_API_KEY}
      default_model: mistral-medium
    
    grok:
      enabled: false
      api_key: encrypted:${GROK_API_KEY}
      safety_filter_enabled: true  # MANDATORY
      user_consent: false  # Set to true after consent dialog
      allowed_tasks:
        - code_completion
        - technical_explanation
        - data_analysis
    
    perplexity:
      enabled: false
      api_key: encrypted:${PERPLEXITY_API_KEY}
      requires_pro: true

routing:
  default_confidence: balanced  # fast, balanced, thorough
  
  tiers:
    fast:
      max_cost_per_request: 0.01
      models:
        - {provider: anthropic, model: claude-3-haiku-20240307, priority: 1}
        - {provider: openai, model: gpt-3.5-turbo, priority: 2}
        - {provider: google, model: gemini-2.0-flash, priority: 3}
    
    balanced:
      max_cost_per_request: 0.10
      models:
        - {provider: anthropic, model: claude-sonnet-4-20250514, priority: 1}
        - {provider: openai, model: gpt-4-turbo, priority: 2}
        - {provider: google, model: gemini-1.5-pro, priority: 3}
    
    thorough:
      max_cost_per_request: 1.00
      models:
        - {provider: anthropic, model: claude-opus-4-20250514, priority: 1}
        - {provider: openai, model: gpt-4o, priority: 2}
        - {provider: openai, model: o1-preview, priority: 3}
  
  budget:
    daily_limit: 10.00
    monthly_limit: 200.00
    warn_at_percent: 80
    block_at_percent: 100

personas:
  architect:
    enabled: true
    default_mode: plan  # plan or build
    planning_tier: balanced
    building_tier: thorough
```

---

## Database Schema Extensions

```sql
-- Track API usage for budget management
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    task_type TEXT,
    tokens_in INTEGER NOT NULL,
    tokens_out INTEGER NOT NULL,
    cost REAL NOT NULL,
    conversation_id INTEGER,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX idx_usage_timestamp ON api_usage(timestamp);
CREATE INDEX idx_usage_provider ON api_usage(provider);

-- Track provider performance for optimization
CREATE TABLE provider_performance (
    id INTEGER PRIMARY KEY,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    task_type TEXT NOT NULL,
    quality_score REAL,  -- 0-10, user feedback + automatic metrics
    latency_ms INTEGER,
    success_rate REAL,
    last_updated DATETIME,
    sample_size INTEGER
);

-- Store compressed conversations
CREATE TABLE conversation_compression (
    conversation_id INTEGER PRIMARY KEY,
    compressed_data TEXT NOT NULL,  -- JSON blob
    original_tokens INTEGER,
    compressed_tokens INTEGER,
    compression_ratio REAL,
    created_at DATETIME,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

-- Track Grok safety filter hits
CREATE TABLE grok_filter_logs (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    task_type TEXT,
    filter_result TEXT,  -- 'allowed', 'blocked_task', 'blocked_content'
    flags TEXT,  -- JSON array of matched patterns
    conversation_id INTEGER,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

---

## UI Components

### Settings Panel: Models > Providers

```
┌─────────────────────────────────────────────────────────┐
│  Settings > Models > Providers                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─ Anthropic (Claude) ─────────────────────┐          │
│  │  Status: ✓ Connected                      │          │
│  │  API Key: ••••••••••••••••••••••• [Edit]  │          │
│  │  Default Model: Claude Sonnet 4    [▼]    │          │
│  │  Available Models:                        │          │
│  │    • Claude 3 Haiku (Fast)               │          │
│  │    • Claude Sonnet 4 (Balanced)          │          │
│  │    • Claude Opus 4 (Thorough)            │          │
│  │  Usage: $2.43 today / $48.22 this month  │          │
│  └───────────────────────────────────────────┘          │
│                                                          │
│  ┌─ OpenAI ──────────────────────────────────┐          │
│  │  Status: ✓ Connected                      │          │
│  │  API Key: ••••••••••••••••••••••• [Edit]  │          │
│  │  Default Model: GPT-4 Turbo        [▼]    │          │
│  │  Usage: $1.82 today / $32.15 this month  │          │
│  └───────────────────────────────────────────┘          │
│                                                          │
│  ┌─ GitHub Copilot ──────────────────────────┐          │
│  │  Status: ✓ Connected via OAuth            │          │
│  │  Account: brettgershon                    │          │
│  │  [Reconnect OAuth]                        │          │
│  └───────────────────────────────────────────┘          │
│                                                          │
│  ┌─ Grok (xAI) ⚠️ ────────────────────────────┐          │
│  │  Status: ⚠️ Safety Filters Required       │          │
│  │  API Key: [Not configured]                │          │
│  │                                            │          │
│  │  ⚠️  WARNING                               │          │
│  │  Grok requires content safety filters     │          │
│  │  due to concerns about conspiratorial     │          │
│  │  thinking and extremist content.          │          │
│  │                                            │          │
│  │  Allowed tasks: Code, technical, math     │          │
│  │  Blocked tasks: Politics, history, news   │          │
│  │                                            │          │
│  │  [View Safety Settings]                   │          │
│  │  [ ] I understand and consent to use Grok │          │
│  └───────────────────────────────────────────┘          │
│                                                          │
│  [+ Add Provider] (OpenRouter, Google AI, etc.)        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Budget Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  Settings > Models > Budget                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Daily Budget: $4.25 / $10.00 used (43%)               │
│  ████████░░░░░░░░░░░                                     │
│                                                          │
│  Monthly Budget: $80.37 / $200.00 used (40%)           │
│  ████████░░░░░░░░░░░                                     │
│                                                          │
│  Top Providers (This Month):                           │
│  1. Anthropic  $48.22 (60%)                            │
│  2. OpenAI     $32.15 (40%)                            │
│                                                          │
│  Top Models:                                            │
│  1. Claude Sonnet 4    $35.10                          │
│  2. GPT-4 Turbo        $28.40                          │
│  3. Claude Opus 4      $13.12                          │
│                                                          │
│  Task Breakdown:                                        │
│  • Code completion: $22.30                             │
│  • Note creation: $18.40                               │
│  • Refactoring: $15.20                                 │
│  • Planning: $12.50                                    │
│                                                          │
│  Budget Settings:                                       │
│  Daily Limit:   [$10.00]                               │
│  Monthly Limit: [$200.00]                              │
│  Warn at: [80%]  Block at: [100%]                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Architect Mode Toggle (Chat Interface)

```
┌─────────────────────────────────────────────────────────┐
│  Polly - Conversation                                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Mode: [🏗️ Architect]  [Plan ⚡ Build]  [⚙️ Settings]   │
│        ─────────────    ════               (toggle)     │
│                         Plan mode active                 │
│                                                          │
│  Brett: I want to implement multi-provider routing      │
│         with support for 8 cloud providers              │
│                                                          │
│  Polly: I'll help you plan this implementation.         │
│         Let me analyze your requirements...             │
│                                                          │
│         📋 Planning Questions:                          │
│         1. Which providers are highest priority?        │
│         2. What's your daily/monthly budget?            │
│         3. Do you want per-task or per-tier routing?    │
│                                                          │
│         [Switch to Build mode when ready]               │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Type your message...                             │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Testing Strategy

### Phase 11a Testing
- [ ] Unit tests for each provider adapter
- [ ] Integration tests for router
- [ ] Budget enforcement tests
- [ ] Fallback chain tests
- [ ] Settings UI tests

### Phase 11b Testing
- [ ] Extended provider integration tests
- [ ] Grok safety filter tests (with test cases)
- [ ] Provider fallback chain validation
- [ ] Rate limit handling tests
- [ ] Error recovery tests

### Phase 11c Testing
- [ ] Cost optimization tests
- [ ] Compression/decompression tests
- [ ] Architect persona tests (plan/build modes)
- [ ] End-to-end workflow tests
- [ ] Performance benchmarks

### Grok-Specific Test Cases
```python
# tests/test_grok_safety.py
class TestGrokSafety:
    def test_allowed_tasks(self):
        assert safety.is_task_allowed("code_completion") == True
        assert safety.is_task_allowed("technical_explanation") == True
    
    def test_blocked_tasks(self):
        assert safety.is_task_allowed("political_analysis") == False
        assert safety.is_task_allowed("news_summary") == False
    
    def test_conspiracy_detection(self):
        text = "The deep state is hiding the truth about..."
        is_safe, flags = safety.validate_content(text)
        assert is_safe == False
        assert "conspiracy_patterns" in str(flags)
    
    def test_extremist_detection(self):
        text = "Nazi ideology has some good points about..."
        is_safe, flags = safety.validate_content(text)
        assert is_safe == False
        assert "extremist_patterns" in str(flags)
    
    def test_clean_technical_content(self):
        text = "Here's a Python function to calculate fibonacci numbers..."
        is_safe, flags = safety.validate_content(text)
        assert is_safe == True
        assert len(flags) == 0
```

---

## Performance Targets

**Provider Response Time:**
- Fast tier: < 2s average
- Balanced tier: < 5s average
- Thorough tier: < 15s average

**Fallback Time:**
- First fallback attempt: < 1s after primary failure
- Complete fallback chain: < 10s total

**Budget Check Latency:**
- < 50ms for budget validation

**Compression Ratio:**
- Target: 100x reduction in tokens
- Minimum: 50x reduction
- Preservation: 95%+ semantic accuracy

**Safety Filter Performance:**
- Pre-request validation: < 10ms
- Post-response filtering: < 100ms
- False positive rate: < 5%

---

## Dependencies

**New Python Packages:**
```
anthropic>=0.20.0
openai>=1.10.0
google-generativeai>=0.3.0
mistralai>=0.1.0
httpx>=0.25.0  # for OpenRouter, Grok, Perplexity
keyring>=24.0.0  # cross-platform secrets
cryptography>=41.0.0  # encryption
```

**Configuration Updates:**
- `config.yaml` schema extensions
- Database migrations for new tables
- Settings UI additions

**Infrastructure:**
- Cross-platform secrets storage
- API usage tracking database
- Performance metrics collection

---

## Migration Plan

### From Current System to Phase 11a

**Week 1:**
1. Keep existing `core/router.py` functional
2. Implement new `core/router_v2.py` alongside
3. Add feature flag: `use_v2_router`
4. Test v2 with existing conversations

**Week 2:**
1. Migrate Anthropic integration to new adapter
2. Add OpenAI and GitHub Copilot adapters
3. Enable v2 router by default
4. Deprecate old router

### From Phase 11a to 11b

**Week 3-4:**
1. Add new provider adapters incrementally
2. Test each provider in isolation
3. Enable Grok only after safety filters pass tests
4. Update UI progressively

### From Phase 11b to 11c

**Week 5:**
1. Add compression to existing conversations (opt-in)
2. Introduce Architect persona as beta feature
3. Collect user feedback
4. Iterate on persona prompts

---

## Risk Assessment

### High Risk Areas

**1. Grok Content Safety**
- **Risk:** False negatives (unsafe content passing filter)
- **Mitigation:** Conservative pattern matching, manual review during testing
- **Contingency:** Disable Grok if filter fails

**2. API Cost Overruns**
- **Risk:** Budget limits not enforced properly
- **Mitigation:** Hard limits in code, real-time tracking
- **Contingency:** Emergency shutoff switch

**3. Provider Availability**
- **Risk:** All providers in fallback chain fail
- **Mitigation:** Diversified provider pool, graceful degradation
- **Contingency:** Fall back to local Ollama

### Medium Risk Areas

**1. Cross-Platform Secrets Storage**
- **Risk:** Keyring library fails on some platforms
- **Mitigation:** Encrypted file fallback
- **Testing:** Validate on macOS, Windows, Linux

**2. Compression Accuracy**
- **Risk:** Semantic loss in compressed conversations
- **Mitigation:** Extensive testing, manual verification
- **Rollback:** Keep full conversations as backup

**3. Performance Under Load**
- **Risk:** Latency spikes with multiple providers
- **Mitigation:** Connection pooling, caching
- **Monitoring:** Track response times per provider

---

## Success Metrics

**Phase 11a Success Criteria:**
- [ ] 3 providers integrated and working
- [ ] Three-tier routing operational
- [ ] Budget limits enforced (0 overruns in testing)
- [ ] Settings UI functional
- [ ] 95%+ uptime across all providers

**Phase 11b Success Criteria:**
- [ ] 8 providers integrated
- [ ] Grok safety filter: 0% unsafe content in production
- [ ] Fallback chains tested: < 1% complete failure rate
- [ ] User consent flow working
- [ ] Extended UI complete

**Phase 11c Success Criteria:**
- [ ] Cost optimization reduces spend by 20%+
- [ ] Compression achieves 50x+ token reduction
- [ ] Architect persona delivers working plans
- [ ] Plan→Build workflow functional
- [ ] All integration tests passing

---

## Future Enhancements (Post-Phase 11)

**Phase 11d (Future):**
- Per-task model customization (currently per-tier)
- Dynamic tier adjustment based on conversation
- A/B testing framework for model comparison
- User preference learning

**Phase 23 (Advanced Compression):**
- Full compression language specification
- Embedding-based semantic compression
- Multi-conversation knowledge graphs
- 100x+ compression ratio

**Librarian Persona (Future):**
- Knowledge base management
- Cross-note relationship detection
- Semantic search across notes

**Critic Persona (Future):**
- Code review and suggestions
- Note quality assessment
- Consistency checking

---

## Documentation Requirements

**Developer Docs:**
- Provider adapter implementation guide
- Adding new providers tutorial
- Router customization guide
- Safety filter testing guide

**User Docs:**
- Provider setup guide (per provider)
- Budget management best practices
- Grok safety explanation
- Architect persona usage guide

**API Reference:**
- `ProviderAdapter` base class
- `IntelligentRouter` API
- `GrokSafetyFilter` API
- Configuration schema reference

---

## Timeline Summary

| Phase | Duration | Deliverables | Dependencies |
|-------|----------|--------------|--------------|
| 11a | 2 weeks | Core routing + 3 providers | None |
| 11b | 2 weeks | Extended providers + safety | 11a complete |
| 11c | 1 week | Orchestration + compression | 11b complete |
| **Total** | **5 weeks** | **8 providers, full system** | **Phase 16 ✅** |

**Critical Path:**
1. Week 1: Multi-provider infrastructure
2. Week 2: Three-tier routing
3. Week 3-4: Extended providers
4. Week 4: Grok safety (parallel with week 3 work)
5. Week 5: Optimization and personas

**Next Phase:** Phase 16c (AI Note Creation) - 4 weeks

---

## Open Questions

**None currently** - All major decisions finalized:
- ✅ 8 providers confirmed
- ✅ Grok safety approach approved
- ✅ Manual mode switching (Plan/Build)
- ✅ Cross-platform secrets strategy
- ✅ Compression is internal-only
- ✅ Per-tier customization initially
- ✅ 5-week timeline acceptable

---

## Approval Status

**Status:** ✅ Ready for Implementation

**Approved By:** User (Brett)

**Date:** January 28, 2026

**Next Step:** Begin Phase 11a Day 1 - Multi-provider infrastructure

---

## Related Documents

- [PHASE11_PROVIDER_SPECIFICATIONS.md](./PHASE11_PROVIDER_SPECIFICATIONS.md) - Detailed provider specs
- [PHASE11_GROK_SAFETY.md](./PHASE11_GROK_SAFETY.md) - Grok safety filter specification
- [PHASE11_SECRETS_MANAGEMENT.md](./PHASE11_SECRETS_MANAGEMENT.md) - Cross-platform secrets
- [PHASE11_AGENT_PERSONAS.md](./PHASE11_AGENT_PERSONAS.md) - Agent persona framework
- [PHASE11_COMPRESSION_SYSTEM.md](./PHASE11_COMPRESSION_SYSTEM.md) - Compression specs
- [PHASE16C_AI_NOTE_CREATION.md](./PHASE16C_AI_NOTE_CREATION.md) - AI note creation
- [master_roadmap.md](./master_roadmap.md) - Overall project roadmap

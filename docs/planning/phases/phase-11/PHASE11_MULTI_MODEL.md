# Phase 11: Multi-Model Selection

**Status:** Planning Complete  
**Priority:** High  
**Estimated Effort:** 7-10 days  
**Last Updated:** January 21, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Current State](#current-state)
3. [Goals](#goals)
4. [Technical Design](#technical-design)
5. [Implementation Plan](#implementation-plan)
6. [API Specifications](#api-specifications)
7. [UI/UX Design](#uiux-design)
8. [Testing Strategy](#testing-strategy)
9. [Success Criteria](#success-criteria)
10. [Future Enhancements](#future-enhancements)

---

## Overview

### Vision

Expand Polly's model selection beyond the current 3 providers (Ollama, Anthropic, OpenAI) to include 6+ providers with 25-30 pre-configured models. Implement smart task-based routing that automatically selects the best model for each query while allowing manual override.

### Key Features

- **Provider Expansion:** GitHub Copilot, OpenRouter, LM Studio, Groq, Perplexity, Together AI
- **Model Tagging System:** Tag models by strength (code, creative, analytical, speed, cost)
- **Enhanced Router:** Detect task type and auto-select best model
- **Two-Tier UI:** Intuitive dropdown (Local/Cloud → Provider → Model)
- **Settings Panel:** Configure provider authentication and preferences

### Why Now?

- Users want access to specialized models (e.g., GitHub Copilot for code)
- OpenRouter provides access to 100+ models with one API key
- LM Studio enables local experimentation with new models
- Current router is too simplistic (just AUTO/LOCAL/CLOUD)
- Smart routing can save costs and improve response quality

---

## Current State

### Existing Router System

**File:** `/core/router.py` (495 lines)

**Current Providers:**
1. **Ollama** (local) - `llama3.2`, `mistral`, etc.
2. **Anthropic** (cloud) - `claude-3-5-sonnet-20241022`
3. **OpenAI** (cloud) - `gpt-4`, `gpt-3.5-turbo`

**Router Modes:**
- `AUTO` - Choose based on query complexity (heuristic scoring)
- `LOCAL` - Force local model only
- `CLOUD` - Force cloud model only

**Routing Logic:**
```python
def route_query(self, query: str, mode: str = "AUTO"):
    if mode == "LOCAL":
        return self.local_models[0]
    elif mode == "CLOUD":
        return self.cloud_models[0]
    else:
        score = self._score_query_complexity(query)
        if score > 7:
            return "claude-3-5-sonnet-20241022"
        else:
            return "llama3.2"
```

**Limitations:**
- No provider selection UI
- No model metadata (strengths, costs, speeds)
- Heuristic scoring is crude (just word count and keyword matching)
- No specialized models (code, creative, etc.)
- No cost optimization
- Manual mode switching is clunky

---

## Goals

### Primary Goals

1. **Add 6+ Providers:**
   - ✅ Ollama (existing)
   - ✅ Anthropic (existing)
   - ✅ OpenAI (existing)
   - 🆕 GitHub Copilot
   - 🆕 OpenRouter
   - 🆕 LM Studio
   - 🆕 Groq
   - 🆕 Perplexity
   - 🆕 Together AI

2. **Create Model Registry:**
   - Tag 25-30 models with strengths
   - Include cost, speed, context window metadata
   - Support custom model additions

3. **Enhanced Router:**
   - Detect task type (code, creative, analytical, etc.)
   - Auto-select best model for task
   - Allow manual override
   - Track model performance

4. **Intuitive UI:**
   - Two-tier dropdown (Local/Cloud → Provider → Model)
   - Show model strengths in tooltips
   - Visual indicators for cost/speed
   - Remember last selection per task type

5. **Settings Management:**
   - Provider authentication (API keys)
   - Model preferences per domain
   - Cost limits and tracking
   - Enable/disable providers

### Secondary Goals

- Model performance tracking (response time, user satisfaction)
- Cost tracking per provider
- Usage analytics dashboard
- Model comparison view
- Batch provider testing

---

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Electron)                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Two-Tier Dropdown UI                            │   │
│  │  • Local/Cloud Toggle                            │   │
│  │  • Provider Selector (with icons)                │   │
│  │  • Model Selector (with strength badges)         │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓ IPC
┌─────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Enhanced Intelligent Router                      │   │
│  │  • Task detection                                │   │
│  │  • Model selection                               │   │
│  │  • Performance tracking                          │   │
│  └───────────────┬──────────────────────────────────┘   │
│                  │                                        │
│  ┌───────────────▼──────────────────────────────────┐   │
│  │  Provider Manager                                │   │
│  │  ┌─────────────────────────────────────────────┐│   │
│  │  │ Model Registry (model_tags.py)              ││   │
│  │  │ • 25-30 pre-configured models               ││   │
│  │  │ • Strengths: code, creative, analytical     ││   │
│  │  │ • Metadata: cost, speed, context window     ││   │
│  │  └─────────────────────────────────────────────┘│   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Provider Clients (/core/providers/)             │   │
│  │  • github_copilot.py                             │   │
│  │  • openrouter.py                                 │   │
│  │  • lm_studio.py                                  │   │
│  │  • groq.py                                       │   │
│  │  • perplexity.py                                 │   │
│  │  • together.py                                   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               Model Providers (External)                 │
│  • GitHub Copilot API                                   │
│  • OpenRouter API (100+ models)                         │
│  • LM Studio (local server)                             │
│  • Groq API                                             │
│  • Perplexity API                                       │
│  • Together AI API                                      │
└─────────────────────────────────────────────────────────┘
```

### Directory Structure

```
/core/
  router.py                    # Enhanced router (update existing)
  model_tags.py                # NEW: Model registry with metadata
  
/core/providers/
  __init__.py                  # NEW: Provider module
  base.py                      # NEW: Base provider class
  github_copilot.py            # NEW: GitHub Copilot client
  openrouter.py                # NEW: OpenRouter client
  lm_studio.py                 # NEW: LM Studio client
  groq.py                      # NEW: Groq client
  perplexity.py                # NEW: Perplexity client
  together.py                  # NEW: Together AI client

/electron-app/src/renderer/
  app.js                       # UPDATE: Add two-tier UI
  index.html                   # UPDATE: Add dropdown structure
  styles/main.css              # UPDATE: Style dropdowns

/electron-app/src/main/
  main.js                      # UPDATE: Add provider IPC handlers
  preload.js                   # UPDATE: Expose provider APIs
```

### Model Registry Format

**File:** `/core/model_tags.py`

```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ModelMetadata:
    """Metadata for a model."""
    provider: str                    # "github_copilot", "openrouter", etc.
    model_id: str                    # "claude-3-5-sonnet-20241022"
    display_name: str                # "Claude 3.5 Sonnet"
    strengths: List[str]             # ["code", "analytical", "long_context"]
    cost_per_1k_tokens: float        # 0.003 (input), 0.015 (output)
    max_tokens: int                  # 200000
    speed_rating: int                # 1-5 (5 is fastest)
    local: bool                      # True for Ollama/LM Studio
    context_window: int              # 200000
    description: str                 # "Best for complex reasoning..."

MODEL_REGISTRY: Dict[str, ModelMetadata] = {
    # === GitHub Copilot ===
    "github:gpt-4o": ModelMetadata(
        provider="github_copilot",
        model_id="gpt-4o",
        display_name="GPT-4o (Copilot)",
        strengths=["code", "debugging", "refactoring"],
        cost_per_1k_tokens=0.005,
        max_tokens=128000,
        speed_rating=4,
        local=False,
        context_window=128000,
        description="GitHub Copilot's flagship model for code generation"
    ),
    
    # === OpenRouter ===
    "openrouter:anthropic/claude-3.5-sonnet": ModelMetadata(
        provider="openrouter",
        model_id="anthropic/claude-3.5-sonnet",
        display_name="Claude 3.5 Sonnet (OpenRouter)",
        strengths=["analytical", "creative", "long_context"],
        cost_per_1k_tokens=0.003,
        max_tokens=200000,
        speed_rating=3,
        local=False,
        context_window=200000,
        description="Best for complex reasoning and long documents"
    ),
    
    "openrouter:meta-llama/llama-3.1-70b-instruct": ModelMetadata(
        provider="openrouter",
        model_id="meta-llama/llama-3.1-70b-instruct",
        display_name="Llama 3.1 70B (OpenRouter)",
        strengths=["analytical", "speed", "cost"],
        cost_per_1k_tokens=0.0003,
        max_tokens=131072,
        speed_rating=4,
        local=False,
        context_window=131072,
        description="Fast and affordable for general tasks"
    ),
    
    # === LM Studio (Local) ===
    "lmstudio:local-model": ModelMetadata(
        provider="lm_studio",
        model_id="local-model",
        display_name="Local Model (LM Studio)",
        strengths=["privacy", "cost", "experimentation"],
        cost_per_1k_tokens=0.0,
        max_tokens=4096,
        speed_rating=3,
        local=True,
        context_window=4096,
        description="Run any local model via LM Studio"
    ),
    
    # === Groq ===
    "groq:llama-3.1-70b-versatile": ModelMetadata(
        provider="groq",
        model_id="llama-3.1-70b-versatile",
        display_name="Llama 3.1 70B (Groq)",
        strengths=["speed", "cost", "analytical"],
        cost_per_1k_tokens=0.0004,
        max_tokens=131072,
        speed_rating=5,
        local=False,
        context_window=131072,
        description="Blazing fast inference with Groq's LPU"
    ),
    
    # === Perplexity ===
    "perplexity:llama-3.1-sonar-large-128k-online": ModelMetadata(
        provider="perplexity",
        model_id="llama-3.1-sonar-large-128k-online",
        display_name="Sonar Large (Perplexity)",
        strengths=["research", "web_search", "current_events"],
        cost_per_1k_tokens=0.001,
        max_tokens=128000,
        speed_rating=3,
        local=False,
        context_window=128000,
        description="Includes real-time web search"
    ),
    
    # === Together AI ===
    "together:meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": ModelMetadata(
        provider="together",
        model_id="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        display_name="Llama 3.1 405B (Together)",
        strengths=["analytical", "creative", "long_context"],
        cost_per_1k_tokens=0.003,
        max_tokens=131072,
        speed_rating=3,
        local=False,
        context_window=131072,
        description="Largest open-source model available"
    ),
    
    # === Existing Models (Ollama, Anthropic, OpenAI) ===
    "ollama:llama3.2": ModelMetadata(
        provider="ollama",
        model_id="llama3.2",
        display_name="Llama 3.2 (Ollama)",
        strengths=["privacy", "cost", "speed"],
        cost_per_1k_tokens=0.0,
        max_tokens=8192,
        speed_rating=5,
        local=True,
        context_window=8192,
        description="Fast local model for quick tasks"
    ),
    
    "anthropic:claude-3-5-sonnet-20241022": ModelMetadata(
        provider="anthropic",
        model_id="claude-3-5-sonnet-20241022",
        display_name="Claude 3.5 Sonnet",
        strengths=["analytical", "creative", "long_context"],
        cost_per_1k_tokens=0.003,
        max_tokens=200000,
        speed_rating=3,
        local=False,
        context_window=200000,
        description="Best for complex reasoning"
    ),
    
    "openai:gpt-4": ModelMetadata(
        provider="openai",
        model_id="gpt-4",
        display_name="GPT-4",
        strengths=["creative", "code", "analytical"],
        cost_per_1k_tokens=0.03,
        max_tokens=8192,
        speed_rating=2,
        local=False,
        context_window=8192,
        description="OpenAI's flagship model"
    ),
    
    # Add 15-20 more models here...
}

# Task type definitions
TASK_TYPES = {
    "code": ["code", "debugging", "refactoring", "programming"],
    "creative": ["creative", "writing", "brainstorming"],
    "analytical": ["analytical", "reasoning", "problem_solving"],
    "research": ["research", "web_search", "current_events"],
    "speed": ["speed", "quick", "simple"],
    "cost": ["cost", "cheap", "affordable"],
}

def get_models_by_strength(strength: str) -> List[ModelMetadata]:
    """Get all models with a specific strength."""
    return [m for m in MODEL_REGISTRY.values() if strength in m.strengths]

def get_best_model_for_task(task_type: str) -> Optional[ModelMetadata]:
    """Get the best model for a task type based on strengths."""
    keywords = TASK_TYPES.get(task_type, [])
    models = []
    for keyword in keywords:
        models.extend(get_models_by_strength(keyword))
    
    if not models:
        return None
    
    # Score models by speed + cost
    scored = [(m, m.speed_rating - (m.cost_per_1k_tokens * 100)) for m in models]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0]
```

---

## Implementation Plan

### Week 1: Foundation (Days 1-3)

#### Day 1: Provider Base Classes & Model Registry

**Tasks:**
1. Create `/core/providers/` directory
2. Create `base.py` with `BaseProvider` abstract class
3. Create `model_tags.py` with `ModelMetadata` and `MODEL_REGISTRY`
4. Add 10-15 models to registry with full metadata
5. Write tests for model registry queries

**Deliverables:**
- `/core/providers/base.py` (100 lines)
- `/core/model_tags.py` (500+ lines, 25-30 models)
- `/tests/test_model_registry.py` (50 lines)

**BaseProvider Interface:**
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseProvider(ABC):
    """Base class for all model providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models."""
        pass
    
    @abstractmethod
    async def generate(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion."""
        pass
    
    @abstractmethod
    async def stream_generate(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ):
        """Stream completion."""
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test if provider is accessible."""
        pass
```

#### Day 2: GitHub Copilot & OpenRouter Clients

**Tasks:**
1. Create `github_copilot.py` with GitHub Copilot API client
2. Create `openrouter.py` with OpenRouter API client
3. Add authentication via API keys (stored in Keychain)
4. Write integration tests for both providers
5. Add error handling and retry logic

**Deliverables:**
- `/core/providers/github_copilot.py` (200 lines)
- `/core/providers/openrouter.py` (200 lines)
- `/tests/test_providers.py` (100 lines)

**GitHub Copilot Client:**
```python
import aiohttp
from typing import List, Dict, Any
from .base import BaseProvider

class GitHubCopilotProvider(BaseProvider):
    """GitHub Copilot API client."""
    
    BASE_URL = "https://api.githubcopilot.com/v1"
    
    async def list_models(self) -> List[str]:
        """List available models."""
        # GitHub Copilot typically uses gpt-4o, gpt-4-turbo
        return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    async def generate(
        self, 
        model: str, 
        prompt: str, 
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            async with session.post(
                f"{self.BASE_URL}/chat/completions",
                headers=headers,
                json=data
            ) as resp:
                result = await resp.json()
                return {
                    "content": result["choices"][0]["message"]["content"],
                    "model": model,
                    "usage": result.get("usage", {})
                }
    
    async def stream_generate(self, model: str, prompt: str, **kwargs):
        """Stream completion."""
        # Implementation similar to generate but with stream=True
        pass
    
    async def test_connection(self) -> bool:
        """Test if GitHub Copilot is accessible."""
        try:
            await self.list_models()
            return True
        except Exception:
            return False
```

#### Day 3: LM Studio, Groq, Perplexity, Together Clients

**Tasks:**
1. Create `lm_studio.py` for local LM Studio server
2. Create `groq.py` for Groq API
3. Create `perplexity.py` for Perplexity API
4. Create `together.py` for Together AI API
5. Write tests for all 4 providers

**Deliverables:**
- `/core/providers/lm_studio.py` (150 lines)
- `/core/providers/groq.py` (200 lines)
- `/core/providers/perplexity.py` (200 lines)
- `/core/providers/together.py` (200 lines)

---

### Week 2: Router & Backend (Days 4-6)

#### Day 4: Enhanced Router

**Tasks:**
1. Update `/core/router.py` to use `MODEL_REGISTRY`
2. Implement task detection (keywords, heuristics)
3. Add `get_best_model_for_task()` method
4. Add manual override support
5. Add performance tracking (response time, user feedback)

**Deliverables:**
- Updated `/core/router.py` (+200 lines)
- `/core/task_detector.py` (100 lines)

**Enhanced Router:**
```python
from typing import Optional, Dict, Any
from .model_tags import MODEL_REGISTRY, get_best_model_for_task
from .task_detector import detect_task_type

class EnhancedIntelligentRouter:
    """Enhanced router with task-based model selection."""
    
    def __init__(self):
        self.model_registry = MODEL_REGISTRY
        self.performance_history = {}  # Track model performance
    
    def route_query(
        self, 
        query: str, 
        mode: str = "AUTO",
        manual_model: Optional[str] = None,
        domain: Optional[str] = None
    ) -> str:
        """Route query to best model."""
        
        # Manual override
        if manual_model:
            return manual_model
        
        # Force modes
        if mode == "LOCAL":
            local_models = [m for m in self.model_registry.values() if m.local]
            return local_models[0].model_id if local_models else "ollama:llama3.2"
        elif mode == "CLOUD":
            cloud_models = [m for m in self.model_registry.values() if not m.local]
            return cloud_models[0].model_id if cloud_models else "anthropic:claude-3-5-sonnet-20241022"
        
        # Auto mode: detect task type
        task_type = detect_task_type(query, domain)
        best_model = get_best_model_for_task(task_type)
        
        if best_model:
            return f"{best_model.provider}:{best_model.model_id}"
        
        # Fallback
        return "anthropic:claude-3-5-sonnet-20241022"
    
    def track_performance(self, model_id: str, response_time: float, success: bool):
        """Track model performance for future routing decisions."""
        if model_id not in self.performance_history:
            self.performance_history[model_id] = {
                "total_requests": 0,
                "success_count": 0,
                "avg_response_time": 0.0
            }
        
        history = self.performance_history[model_id]
        history["total_requests"] += 1
        if success:
            history["success_count"] += 1
        
        # Update rolling average
        n = history["total_requests"]
        history["avg_response_time"] = (
            (history["avg_response_time"] * (n - 1) + response_time) / n
        )
```

**Task Detector:**
```python
import re
from typing import Optional

CODE_KEYWORDS = [
    "code", "function", "class", "debug", "bug", "error", 
    "refactor", "implement", "python", "javascript", "rust"
]

CREATIVE_KEYWORDS = [
    "write", "create", "story", "poem", "essay", "brainstorm",
    "imagine", "creative", "generate ideas"
]

ANALYTICAL_KEYWORDS = [
    "analyze", "explain", "reason", "compare", "evaluate",
    "understand", "why", "how does", "logic"
]

RESEARCH_KEYWORDS = [
    "search", "find", "research", "latest", "current",
    "news", "what is", "who is"
]

def detect_task_type(query: str, domain: Optional[str] = None) -> str:
    """Detect task type from query and domain."""
    query_lower = query.lower()
    
    # Domain-based detection
    if domain == "sigils":
        return "code"
    elif domain == "scrolls":
        return "creative"
    elif domain == "grids":
        return "analytical"
    
    # Keyword-based detection
    code_score = sum(1 for kw in CODE_KEYWORDS if kw in query_lower)
    creative_score = sum(1 for kw in CREATIVE_KEYWORDS if kw in query_lower)
    analytical_score = sum(1 for kw in ANALYTICAL_KEYWORDS if kw in query_lower)
    research_score = sum(1 for kw in RESEARCH_KEYWORDS if kw in query_lower)
    
    scores = {
        "code": code_score,
        "creative": creative_score,
        "analytical": analytical_score,
        "research": research_score
    }
    
    # Return highest scoring task type
    max_score = max(scores.values())
    if max_score == 0:
        return "analytical"  # Default
    
    return max(scores, key=scores.get)
```

#### Day 5: API Endpoints

**Tasks:**
1. Add `/polly/models/list` endpoint
2. Add `/polly/models/providers` endpoint
3. Add `/polly/models/select` endpoint (for manual override)
4. Add `/polly/models/performance` endpoint (usage stats)
5. Update `/polly/chat` endpoint to use enhanced router

**Deliverables:**
- Updated `/interfaces/server.py` (+150 lines)

**API Endpoints:**

```python
# GET /polly/models/list
@app.get("/polly/models/list")
async def list_models(
    provider: Optional[str] = None,
    strength: Optional[str] = None,
    local_only: bool = False
):
    """List available models with filters."""
    from core.model_tags import MODEL_REGISTRY
    
    models = list(MODEL_REGISTRY.values())
    
    if provider:
        models = [m for m in models if m.provider == provider]
    
    if strength:
        models = [m for m in models if strength in m.strengths]
    
    if local_only:
        models = [m for m in models if m.local]
    
    return {
        "models": [
            {
                "id": f"{m.provider}:{m.model_id}",
                "display_name": m.display_name,
                "provider": m.provider,
                "strengths": m.strengths,
                "cost_per_1k": m.cost_per_1k_tokens,
                "speed_rating": m.speed_rating,
                "local": m.local,
                "description": m.description
            }
            for m in models
        ]
    }

# GET /polly/models/providers
@app.get("/polly/models/providers")
async def list_providers():
    """List all available providers."""
    return {
        "providers": [
            {"id": "ollama", "name": "Ollama", "local": True},
            {"id": "lm_studio", "name": "LM Studio", "local": True},
            {"id": "anthropic", "name": "Anthropic", "local": False},
            {"id": "openai", "name": "OpenAI", "local": False},
            {"id": "github_copilot", "name": "GitHub Copilot", "local": False},
            {"id": "openrouter", "name": "OpenRouter", "local": False},
            {"id": "groq", "name": "Groq", "local": False},
            {"id": "perplexity", "name": "Perplexity", "local": False},
            {"id": "together", "name": "Together AI", "local": False},
        ]
    }

# POST /polly/models/select
@app.post("/polly/models/select")
async def select_model(request: dict):
    """Manually select a model for next query."""
    model_id = request.get("model_id")
    # Store selection in session or user preferences
    return {"selected_model": model_id}

# GET /polly/models/performance
@app.get("/polly/models/performance")
async def get_model_performance():
    """Get performance stats for all models."""
    # Return router.performance_history
    return {"performance": router.performance_history}
```

#### Day 6: Settings Panel Backend

**Tasks:**
1. Add provider authentication endpoints
2. Add model preference storage
3. Update settings IPC handlers
4. Add keychain integration for new API keys
5. Add provider enable/disable logic

**Deliverables:**
- Updated `/electron-app/src/main/main.js` (+100 lines)
- Updated `/electron-app/src/main/preload.js` (+20 lines)

---

### Week 3: Frontend UI (Days 7-10)

#### Day 7-8: Two-Tier Dropdown UI

**Tasks:**
1. Design two-tier dropdown UI mockup
2. Implement Local/Cloud toggle
3. Implement provider selector with icons
4. Implement model selector with strength badges
5. Add tooltips showing model metadata

**Deliverables:**
- Updated `/electron-app/src/renderer/index.html` (+50 lines)
- Updated `/electron-app/src/renderer/app.js` (+150 lines)
- Updated `/electron-app/src/renderer/styles/main.css` (+100 lines)

**UI Mockup:**

```
┌─────────────────────────────────────────────────────────┐
│  Polly                                             [⚙️]  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Model Selection:                                        │
│  ┌──────────┬──────────┐                                │
│  │  Local ✓ │  Cloud   │  ← Toggle                     │
│  └──────────┴──────────┘                                │
│                                                          │
│  Provider: [Ollama ▼]  ← Dropdown with icons            │
│    • Ollama                                             │
│    • LM Studio                                          │
│                                                          │
│  Model: [Llama 3.2 ▼]  ← Dropdown with badges          │
│    • Llama 3.2           🏃💰 (fast, cheap)             │
│    • Mistral             🧠 (analytical)                │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 💡 Llama 3.2                                       │ │
│  │ Speed: ⭐⭐⭐⭐⭐                                    │ │
│  │ Cost: Free (local)                                 │ │
│  │ Strengths: privacy, speed, cost                    │ │
│  │ Context: 8,192 tokens                              │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  [Auto-Select] ← Toggle for automatic routing           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**HTML Structure:**

```html
<!-- Model Selection Section -->
<div class="model-selection">
  <h3>Model Selection</h3>
  
  <!-- Local/Cloud Toggle -->
  <div class="toggle-group">
    <button class="toggle-btn active" id="local-toggle">Local</button>
    <button class="toggle-btn" id="cloud-toggle">Cloud</button>
  </div>
  
  <!-- Provider Selector -->
  <div class="selector-group">
    <label>Provider:</label>
    <select id="provider-selector" class="polly-select">
      <!-- Populated dynamically -->
    </select>
  </div>
  
  <!-- Model Selector -->
  <div class="selector-group">
    <label>Model:</label>
    <select id="model-selector" class="polly-select">
      <!-- Populated dynamically -->
    </select>
  </div>
  
  <!-- Model Info Card -->
  <div class="model-info-card" id="model-info">
    <h4 id="model-name">Llama 3.2</h4>
    <div class="model-stats">
      <div>Speed: <span id="speed-rating">⭐⭐⭐⭐⭐</span></div>
      <div>Cost: <span id="cost">Free (local)</span></div>
      <div>Strengths: <span id="strengths">privacy, speed, cost</span></div>
      <div>Context: <span id="context">8,192 tokens</span></div>
    </div>
    <p id="model-description">Fast local model for quick tasks</p>
  </div>
  
  <!-- Auto-Select Toggle -->
  <div class="checkbox-group">
    <label>
      <input type="checkbox" id="auto-select" checked>
      Auto-Select Best Model
    </label>
  </div>
</div>
```

#### Day 9: Settings Panel UI

**Tasks:**
1. Add "Models" tab to settings
2. Create provider authentication forms
3. Add model preference settings per domain
4. Add enable/disable toggles for providers
5. Add cost tracking display

**Deliverables:**
- Updated `/electron-app/src/renderer/index.html` (+80 lines)
- Updated `/electron-app/src/renderer/app.js` (+100 lines)

#### Day 10: Testing & Polish

**Tasks:**
1. End-to-end testing of model selection
2. Test all 9 providers
3. Test auto-routing with different query types
4. UI polish (animations, transitions, error states)
5. Documentation updates

---

## API Specifications

### List Models

**Endpoint:** `GET /polly/models/list`

**Query Parameters:**
- `provider` (optional): Filter by provider (e.g., "ollama")
- `strength` (optional): Filter by strength (e.g., "code")
- `local_only` (optional): Only show local models

**Response:**
```json
{
  "models": [
    {
      "id": "ollama:llama3.2",
      "display_name": "Llama 3.2 (Ollama)",
      "provider": "ollama",
      "strengths": ["privacy", "speed", "cost"],
      "cost_per_1k": 0.0,
      "speed_rating": 5,
      "local": true,
      "description": "Fast local model for quick tasks"
    }
  ]
}
```

### List Providers

**Endpoint:** `GET /polly/models/providers`

**Response:**
```json
{
  "providers": [
    {
      "id": "ollama",
      "name": "Ollama",
      "local": true
    }
  ]
}
```

### Select Model

**Endpoint:** `POST /polly/models/select`

**Request:**
```json
{
  "model_id": "github_copilot:gpt-4o"
}
```

**Response:**
```json
{
  "selected_model": "github_copilot:gpt-4o"
}
```

---

## UI/UX Design

### Design Principles

1. **Clarity:** Model metadata should be immediately visible
2. **Speed:** Fast switching between models
3. **Guidance:** Tooltips and descriptions help users choose
4. **Flexibility:** Auto-routing with manual override
5. **Consistency:** Matches existing Polly brutalist aesthetic

### Color Coding

- **Green badges:** Strengths (code, creative, etc.)
- **Blue badges:** Speed indicators
- **Gray badges:** Cost indicators
- **Yellow star:** Speed rating

### Accessibility

- Keyboard navigation (Tab, Enter, Space)
- Screen reader support for all controls
- High contrast mode support
- Clear focus states

---

## Testing Strategy

### Unit Tests

- Model registry queries
- Task detection algorithm
- Provider clients (mocked)
- Router logic

### Integration Tests

- GitHub Copilot authentication
- OpenRouter API calls
- LM Studio connection
- Groq, Perplexity, Together APIs

### End-to-End Tests

1. Select "GitHub Copilot" provider
2. Choose "GPT-4o" model
3. Send code-related query
4. Verify correct model used
5. Check response quality

### Manual Testing Checklist

- [ ] Local/Cloud toggle works
- [ ] Provider selector populates correctly
- [ ] Model selector shows only models for selected provider
- [ ] Model info card updates when selection changes
- [ ] Auto-select routes to correct model for code queries
- [ ] Auto-select routes to correct model for creative queries
- [ ] Manual override disables auto-routing
- [ ] Settings panel saves provider credentials
- [ ] All 9 providers can be authenticated
- [ ] Cost tracking displays correctly

---

## Success Criteria

### Must Have

- ✅ 6+ providers working (GitHub Copilot, OpenRouter, LM Studio, Groq, Perplexity, Together)
- ✅ 25-30 models in registry with full metadata
- ✅ Task detection routing to correct model type
- ✅ Two-tier UI (Local/Cloud → Provider → Model)
- ✅ Settings panel for provider authentication
- ✅ Manual override support

### Should Have

- Model performance tracking (response time)
- Cost tracking per provider
- Model comparison view
- Batch provider testing
- Migration of existing conversations to new router

### Nice to Have

- Usage analytics dashboard
- Model recommendation engine
- A/B testing different models
- Community model ratings

---

## Future Enhancements

### Phase 11.5: Advanced Router Features

- **Context-aware routing:** Consider conversation history, domain, user preferences
- **Cost optimization:** Route to cheapest model that meets quality threshold
- **Load balancing:** Distribute load across providers
- **Fallback chains:** If primary provider fails, try secondary
- **Rate limit handling:** Automatic retry with backoff

### Phase 11.6: Community Models

- **Custom model registry:** Users can add their own models
- **Model sharing:** Export/import model configurations
- **Community ratings:** Users rate model performance
- **Model marketplace:** Browse and install community models

### Phase 11.7: Model Fine-Tuning

- **Pattern-based tuning:** Fine-tune models on user's patterns
- **Domain-specific models:** Train models for specific domains
- **Feedback loop:** Improve routing based on user feedback

---

## Risks & Mitigations

### Risk 1: Provider API Changes

**Impact:** High  
**Likelihood:** Medium  
**Mitigation:** Use provider-specific clients with version pinning, monitor API change logs

### Risk 2: Authentication Complexity

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:** Clear UI instructions, fallback to simple API key auth

### Risk 3: Cost Overruns

**Impact:** High  
**Likelihood:** Low  
**Mitigation:** Implement cost tracking and limits, warn users before expensive operations

### Risk 4: Model Selection Confusion

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:** Clear tooltips, model descriptions, default to auto-routing

---

## Dependencies

### Python Libraries

- `aiohttp` (existing) - HTTP requests
- `keytar` (existing) - Credential storage
- No new dependencies needed!

### External Services

- GitHub Copilot API (requires GitHub Copilot subscription)
- OpenRouter API (requires API key)
- LM Studio (local server, free)
- Groq API (requires API key)
- Perplexity API (requires API key)
- Together AI API (requires API key)

### Documentation

- GitHub Copilot API: https://docs.github.com/copilot
- OpenRouter API: https://openrouter.ai/docs
- LM Studio: https://lmstudio.ai/docs
- Groq: https://console.groq.com/docs
- Perplexity: https://docs.perplexity.ai/
- Together AI: https://docs.together.ai/

---

## Timeline Summary

**Total Effort:** 7-10 days

**Week 1: Foundation (3 days)**
- Day 1: Provider base classes, model registry
- Day 2: GitHub Copilot, OpenRouter clients
- Day 3: LM Studio, Groq, Perplexity, Together clients

**Week 2: Router & Backend (3 days)**
- Day 4: Enhanced router with task detection
- Day 5: API endpoints
- Day 6: Settings panel backend

**Week 3: Frontend (3-4 days)**
- Day 7-8: Two-tier dropdown UI
- Day 9: Settings panel UI
- Day 10: Testing & polish

---

## Next Steps

After Phase 11:
1. Collect user feedback on model selection
2. Monitor cost and performance metrics
3. Expand model registry based on demand
4. Implement Phase 11.5 (advanced router features)

---

**Last Updated:** January 21, 2026  
**Status:** Planning Complete - Ready for Implementation  
**Estimated Start Date:** TBD  
**Estimated Completion Date:** TBD + 10 days

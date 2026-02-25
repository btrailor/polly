# Design: Context Distillation Layer

## Overview
Add a context distillation layer that compresses assembled RAG context and gathered context through a fast local Ollama model (llama3.2:3b) before sending to cloud LLMs. Integrates with the existing compression infrastructure (`CompressionStrategy`, `CompressionManager`) and inserts between context assembly and router call in `polly.py`.

## Architecture

### Component Diagram
```
Polly.query()
    |
Domain Detection (L1504)
    |
[Phase 0] SemanticCache.check() ← cache hit? → return immediately
    |
RAG Search (L1624) → format_context() → rag_context (str)
    |
_gather_context() → gathered_context (str)
    |
_build_system_prompt() + domain_prompt + rag_context + gathered_context
    |
= augmented_system (full system prompt, ~8-15K tokens)
    |
[NEW] ContextDistiller.distill() ← compress via local Ollama
    |                                  ↓
    |                          distilled_system (~3-6K tokens)
    |
Router call (cloud providers)
    |
Response → [Phase 0] SemanticCache.store()
```

### Integration with Existing Compression Stack
```
core/compression/
  ├── compressor.py          (ConversationCompressor — existing)
  ├── manager.py             (CompressionManager — existing, modified)
  ├── llmlingua_strategy.py  (LLMLinguaCompressor — existing, per-chunk)
  └── ollama_strategy.py     [NEW] OllamaDistillStrategy — assembled context

core/
  └── context_distiller.py   [NEW] ContextDistiller — orchestrates distillation
```

**Key distinction:**
- **LLMLingua** (existing): Algorithmic per-chunk compression via BERT — removes tokens by statistical importance. Operates on individual RAG chunks before formatting.
- **Ollama distillation** (new): Semantic compression via local LLM — summarizes and restructures assembled context. Operates on the formatted context string after all chunks are assembled.

Both can coexist. LLMLingua compresses individual chunks (if enabled). Ollama distillation compresses the assembled result. They stack: LLMLingua reduces chunk-level noise, then distillation reduces assembled-context-level redundancy.

### Key Design Decisions

#### 1. Distillation Model
**Decision:** Use `llama3.2:3b` (Polly's "fast" tier Ollama model) for distillation.

**Rationale:**
- Fastest local model available (~200ms for typical context distillation)
- 3B parameters is sufficient for summarization/extraction (not reasoning)
- Already configured and available in Polly's Ollama setup
- Configurable via `context_distillation.model` in config.yaml

**Alternatives considered:**
- `llama3.1:7b` (balanced tier): Better quality but ~2x slower. Available as config option for users who prefer quality over speed.
- LLMLingua only: Purely algorithmic, faster (~50ms), but doesn't understand semantics — can't restructure or prioritize information.

#### 2. What Gets Distilled
**Decision:** Distill the RAG context and gathered context portions of the system prompt, not the entire system prompt.

**Components distilled:**
- `rag_context` (formatted RAG search results) — typically 3,000-8,000 tokens
- `gathered_context` (mental models + entity context + patterns + compression summary) — typically 500-2,000 tokens

**Components NOT distilled:**
- Base system prompt (persona + constitutional layer) — carefully authored, fixed-length
- Domain prompt — short, already optimized
- RAG header/instruction/footer — short instructional text
- User query — must be preserved verbatim
- Conversation history — compressed separately by existing ConversationCompressor

**Rationale:** The RAG context and gathered context are the variable-length, high-token-count portions. They contain the most redundancy and benefit most from distillation. The fixed prompts are already optimized and distilling them would lose carefully crafted instructions.

#### 3. Distillation Prompt Strategy
**Decision:** Use a task-aware distillation prompt that varies by domain and retrieval tier.

**Prompt template:**
```
You are a context distiller. Your job is to compress the following information
into a dense, accurate summary that preserves all key facts, code snippets,
specific names, numbers, and actionable details.

Domain: {domain}
Retrieval quality: {retrieval_tier}

Rules:
- Preserve ALL code snippets, file paths, and technical specifics verbatim
- Remove redundant explanations and filler text
- Merge overlapping information from multiple sources
- Keep the most relevant {top_n} pieces of information
- Target approximately {target_ratio}% of the original length
- Output ONLY the distilled context, no commentary

Context to distill:
{context}
```

**Domain-specific adjustments:**
- **Sigils (code):** "Preserve all code blocks, function signatures, and import statements verbatim"
- **Scrolls (writing):** "Preserve key arguments, quotes, and structural outlines"
- **Signals (audio):** "Preserve timestamps, speaker names, and key quotes"

#### 4. Insertion Point
**Decision:** Distill after context assembly (~L2011) but before the router call (~L2140), only for cloud-routed queries.

**Location in pipeline:**
```python
# After augmented_system is built (~L2011)
# Before messages_with_system is constructed for cloud call

if should_distill(route_decision, config):
    distilled_rag = distiller.distill(rag_context, domain, retrieval_tier)
    distilled_gathered = distiller.distill(gathered_context, domain, retrieval_tier)
    # Reconstruct augmented_system with distilled components
    augmented_system = rebuild_system_prompt(
        base_prompt, domain_prompt,
        rag_header, rag_instruction,
        distilled_rag,           # ← replaced
        distilled_gathered,      # ← replaced
        rag_footer
    )
```

**Why not earlier?**
- Need the full assembled context to distill effectively (earlier = only raw chunks)
- Need domain and retrieval tier for prompt customization

**Why not distill the whole augmented_system?**
- Persona prompts and constitutional layer would be corrupted by summarization
- Fixed-length portions don't benefit from distillation

#### 5. When to Distill
**Decision:** Distill only when:
1. Enabled in config (`context_distillation.enabled: true`)
2. Query is routing to cloud (not local Ollama — local is already cheap)
3. Context exceeds minimum threshold (`context_distillation.min_tokens: 2000`)
4. Not a cache hit (Phase 0 already returns the complete response)

**Skip distillation when:**
- Context is small (< min_tokens) — not worth the 200ms overhead
- Routing to local Ollama — distillation would cost more than savings
- Ollama is down — graceful fallback to raw context

#### 6. Target Compression Ratio
**Decision:** Configurable, default 0.4 (reduce to 40% of original size).

- `target_ratio: 0.4` → 8,000 tokens → ~3,200 tokens (saves ~4,800 tokens)
- Configurable range: 0.2 (aggressive) to 0.8 (light)
- The distillation prompt instructs the model to target this ratio
- Actual ratio may vary — the model may produce slightly more or less

## API Design

### ContextDistiller Class

```python
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)

_instance: Optional['ContextDistiller'] = None

def init_context_distiller(ollama_host: str, config: dict) -> 'ContextDistiller':
    """Initialize the context distiller singleton."""
    global _instance
    _instance = ContextDistiller(ollama_host, config)
    return _instance

def get_context_distiller() -> Optional['ContextDistiller']:
    """Get the context distiller singleton."""
    return _instance


class ContextDistiller:
    """
    Compresses assembled context through a local Ollama model
    before sending to cloud LLMs.
    """
    
    def __init__(
        self,
        ollama_host: str,       # e.g., "http://localhost:11434"
        config: dict            # context_distillation config section
    ):
        """
        Args:
            ollama_host: Ollama API base URL
            config: Config with keys: enabled, model, target_ratio,
                    min_tokens, max_distill_time_ms
        """
    
    async def distill(
        self,
        context: str,
        domain: str = "general",
        retrieval_tier: str = "ADJACENT",
        context_type: str = "rag"    # "rag" or "gathered"
    ) -> 'DistillResult':
        """
        Distill context through local Ollama model.
        
        Args:
            context: The raw context string to distill
            domain: Detected domain for prompt customization
            retrieval_tier: DIRECT/ADJACENT/ABSENT for priority hints
            context_type: Type of context being distilled
        
        Returns:
            DistillResult with distilled text and metrics
        """
    
    def should_distill(
        self,
        context_length: int,
        route_type: str
    ) -> bool:
        """
        Check if distillation should be applied.
        
        Returns True if enabled, routing to cloud, and context
        exceeds min_tokens threshold.
        """
    
    def get_stats(self) -> 'DistillStats':
        """Get distillation statistics."""


@dataclass
class DistillResult:
    """Result from a distillation operation."""
    distilled_text: str
    original_tokens: int
    distilled_tokens: int
    compression_ratio: float
    distill_time_ms: float
    model_used: str
    domain: str


@dataclass
class DistillStats:
    """Distillation statistics for metrics."""
    total_distillations: int
    total_tokens_saved: int
    average_compression_ratio: float
    average_distill_time_ms: float
    total_time_saved_estimate_ms: float  # Estimated cloud processing time saved
```

### OllamaDistillStrategy Class

```python
class OllamaDistillStrategy:
    """
    Ollama-based distillation strategy implementing the same interface
    pattern as LLMLinguaCompressor.
    
    Can be used standalone or registered with CompressionManager.
    """
    
    def __init__(self, ollama_host: str, model: str = "llama3.2:3b"):
        self.ollama_host = ollama_host
        self.model = model
    
    async def compress(
        self,
        text: str,
        target_ratio: float = 0.4,
        context_type: str = "rag",
        domain: str = "general",
        retrieval_tier: str = "ADJACENT"
    ) -> CompressionResult:
        """
        Compress text via Ollama distillation.
        
        Returns CompressionResult (same dataclass as LLMLingua):
            compressed_text, original_tokens, compressed_tokens,
            compression_ratio, metadata
        """
    
    def _build_distill_prompt(
        self,
        context: str,
        domain: str,
        retrieval_tier: str,
        target_ratio: float
    ) -> str:
        """Build the distillation prompt with domain-specific instructions."""
    
    async def _call_ollama(
        self,
        prompt: str,
        system: str,
        max_tokens: int
    ) -> str:
        """Make async HTTP call to Ollama API."""
```

## Data Flow

### 1. Standard Distillation Flow (Cloud-Routed Query)
```
polly.py: Context assembly complete
    |
    ├── rag_context = "**Note: design.md**\n```...```\n\n---\n\n**Code: main.py**..."
    │   (8,000 tokens)
    |
    ├── gathered_context = "Mental Model: restraint_first...\nEntity: ProjectX..."  
    │   (1,500 tokens)
    |
ContextDistiller.should_distill(9500, "cloud") → True
    |
ContextDistiller.distill(rag_context, "sigils", "DIRECT", "rag")
    ├── _build_distill_prompt() with Sigils-specific rules
    ├── POST http://localhost:11434/api/generate
    │   model: llama3.2:3b
    │   prompt: "You are a context distiller..."
    │   max_tokens: 3200 (8000 * 0.4)
    ├── distilled_rag (3,100 tokens)
    └── DistillResult(compression_ratio=0.39, distill_time_ms=210)
    |
ContextDistiller.distill(gathered_context, "sigils", "DIRECT", "gathered")
    ├── distilled_gathered (600 tokens)
    └── DistillResult(compression_ratio=0.40, distill_time_ms=95)
    |
Reconstruct augmented_system with distilled components
    |
Total: 9,500 → 3,700 tokens (61% reduction)
    |
Router call to cloud with distilled system prompt
```

### 2. Skip Distillation (Small Context)
```
rag_context = "**Note: readme.md**\n```short snippet```"
(800 tokens)

ContextDistiller.should_distill(800, "cloud") → False
(below min_tokens threshold of 2000)

Use raw context as-is
```

### 3. Skip Distillation (Local Route)
```
Router decision: route to local Ollama

ContextDistiller.should_distill(8000, "local") → False
(local route — distillation not needed)

Use raw context as-is
```

### 4. Ollama Down (Graceful Fallback)
```
ContextDistiller.distill(rag_context, ...)
    |
POST http://localhost:11434/api/generate → ConnectionError
    |
Log warning: "Distillation failed, using raw context"
    |
Return DistillResult(distilled_text=original_text, compression_ratio=1.0)
```

## Configuration

### config.yaml Addition
```yaml
context_distillation:
  enabled: true
  model: "llama3.2:3b"          # Ollama model for distillation
  target_ratio: 0.4             # Target 40% of original size
  min_tokens: 2000              # Skip distillation below this threshold
  max_distill_time_ms: 2000     # Timeout — use raw context if distillation is slow
  distill_rag: true             # Distill RAG context
  distill_gathered: true        # Distill gathered context (mental models, etc.)
  cloud_only: true              # Only distill for cloud-routed queries
```

### core/config.py DEFAULT_CONFIG Addition
```python
"context_distillation": {
    "enabled": True,
    "model": "llama3.2:3b",
    "target_ratio": 0.4,
    "min_tokens": 2000,
    "max_distill_time_ms": 2000,
    "distill_rag": True,
    "distill_gathered": True,
    "cloud_only": True,
}
```

## Pipeline Integration

### Polly.__init__ (init sequence)
```python
# After semantic cache init, before router init
def _init_context_distiller(self):
    """Initialize context distillation using local Ollama."""
    try:
        from core.context_distiller import init_context_distiller
        distill_config = self.config.get("context_distillation", {})
        if distill_config.get("enabled", True):
            init_context_distiller(
                ollama_host=self.config.get("ollama", {}).get("host", "http://localhost:11434"),
                config=distill_config
            )
            logger.info("Context distiller initialized")
        else:
            logger.info("Context distillation disabled in config")
    except Exception as e:
        logger.warning(f"Failed to initialize context distiller: {e}")
```

### Polly.query() — Distillation Step (~between L2011 and L2140)
```python
# After augmented_system is assembled, before cloud router call
if route_to_cloud:
    from core.context_distiller import get_context_distiller
    distiller = get_context_distiller()
    if distiller and distiller.should_distill(len(rag_context) + len(gathered_context), "cloud"):
        try:
            # Distill RAG context
            if distill_config.get("distill_rag", True) and rag_context:
                rag_result = await distiller.distill(
                    rag_context, detected_domain, retrieval_tier.tier, "rag"
                )
                rag_context = rag_result.distilled_text
            
            # Distill gathered context
            if distill_config.get("distill_gathered", True) and gathered_context:
                gathered_result = await distiller.distill(
                    gathered_context, detected_domain, retrieval_tier.tier, "gathered"
                )
                gathered_context = gathered_result.distilled_text
            
            # Reconstruct augmented_system with distilled components
            augmented_system = self._rebuild_augmented_system(
                rag_context, gathered_context, domain_prompt, ...
            )
        except Exception as e:
            logger.warning(f"Distillation failed, using raw context: {e}")
```

## Interaction with Phase 0 (Semantic Cache)

```
Query arrives
    |
[Phase 0] Cache check → HIT? → return cached response (skip everything)
    |                    MISS ↓
RAG + context assembly
    |
[Phase 1] Distill context → distilled system prompt
    |
Cloud LLM call → response
    |
[Phase 0] Cache store (stores response for future hits)
```

The cache stores the **final response** (not the distilled context). On a cache hit, distillation is skipped entirely because the response is already available.

## Files to Create/Modify

### New Files
1. `core/context_distiller.py` (~200 lines)
2. `core/compression/ollama_strategy.py` (~150 lines)

### Modified Files
1. `core/polly.py` — _init_context_distiller(), distillation step, _rebuild_augmented_system()
2. `core/compression/compressor.py` — Register "ollama_distill" strategy
3. `core/compression/manager.py` — Add distill_context() method
4. `core/config.py` — Add context_distillation to DEFAULT_CONFIG
5. `config.yaml` — Add context_distillation section
6. `core/autonomy_metrics.py` — Track distillation tokens saved
7. `interfaces/server.py` — GET /polly/distillation/stats
8. `interfaces/settings_api.py` — GET/PUT /polly/settings/context-distillation
9. `electron-app/src/renderer/index.html` — Distillation toggle + ratio slider
10. `electron-app/src/renderer/app.js` — Distillation settings JS

### Unchanged Files
- `core/compression/llmlingua_strategy.py` — LLMLingua continues to operate independently
- `core/rag.py` — RAG search and formatting unchanged
- `core/router.py` / `libs/polly-routing/` — Routing logic unchanged
- `core/semantic_cache.py` — Cache operates independently (stores final responses)

## Edge Cases

### 1. Ollama Down
**Handling:** Distillation call fails → catch exception → use raw context → log warning. Pipeline continues normally. Distillation is non-critical.

### 2. Distillation Timeout
**Handling:** `max_distill_time_ms` (default 2000ms). If Ollama takes longer, cancel and use raw context. Better to send raw context fast than wait for distillation.

### 3. Distillation Quality Degradation
**Handling:** If distilled text is empty or suspiciously short (< 10% of original), discard and use raw context. Log warning for monitoring.

### 4. Code Blocks in RAG Context
**Handling:** Domain-specific distillation prompts for Sigils instruct the model to preserve code blocks verbatim. Code should never be summarized — only surrounding explanatory text.

### 5. Very Large Context (> 15K tokens)
**Handling:** For very large contexts, distillation becomes more valuable but may be slower. The model's max context window (llama3.2:3b has 128K) can handle it. Timeout protects against extreme cases.

### 6. Wave 3 Sub-Queries
**Handling:** Wave 3 sub-queries (via SplitRouter) each do their own RAG search with smaller context (~5 results). Distillation should apply to cloud-routed sub-queries too. The `split_router.py` modification adds the same distillation step before each sub-query's cloud call.

## Testing Strategy

### Unit Tests
1. Distillation produces shorter output than input
2. Code blocks preserved verbatim in distilled output
3. should_distill() returns True/False based on config and context size
4. Domain-specific prompts generated correctly
5. Graceful fallback when Ollama is down
6. Timeout handling works

### Integration Tests
1. Full pipeline: query → RAG → distill → cloud → response
2. Distillation skipped for local routes
3. Distillation skipped for small contexts
4. Distillation skipped on cache hits (Phase 0)
5. Settings toggle enables/disables distillation
6. Compression ratio tracking in AutonomyMetrics

## Success Metrics
1. 40-60% average input token reduction on cloud calls
2. < 300ms average distillation latency
3. No quality degradation in cloud responses (manual evaluation)
4. Zero pipeline regressions
5. Graceful fallback on all failure modes
6. Token savings visible in AutonomyMetrics

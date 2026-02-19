# Design: Scalable Memory Layers + Rolling Relevance-Weighted Context

**Date:** 2026-02-18
**Status:** Ready for Implementation
**Related:** [proposal.md](proposal.md), [tasks.md](tasks.md)

---

## Architecture Overview

Two new subsystems integrate into the existing Polly orchestration pipeline:

```
Polly.query()
    |
Domain Detection (L1504)
    |
Memory Retrieval [NEW] ← tiered store (stable + episodic + working)
    |                      scored by relevance_scorer
    |
RAG Search (L1624) → scored by relevance_scorer
    |
_gather_context() [MODIFIED]
    |   Contributors: mental_models (60), memory_retriever (50) [NEW],
    |                 entity_context (40), pattern_engine (20),
    |                 compression_summary (10)
    |   Each receives token_budget from allocator
    |
Budget Allocator [NEW] ← distributes total budget across sections
    |
Rolling Context [NEW] ← bin-packs scored entries within budget
    |                     decay/amplify after each turn
    |
augmented_system (budget-constrained)
    |
Router call (local or cloud)
    |
rolling_context.on_new_turn() [NEW] ← decay unreferenced, amplify referenced
    |
Session End → Extraction Pipeline [NEW] → write to stable/episodic tiers
```

### Component Diagram

```
core/context/                          core/memory/
├── token_counter.py     [NEW]         ├── __init__.py          [MODIFIED]
├── budget_allocator.py  [NEW]         ├── mem0_adapter.py      [MODIFIED]
├── relevance_scorer.py  [NEW]         ├── tiers.py             [NEW]
└── rolling_context.py   [NEW]         ├── retriever.py         [NEW]
                                       └── extractor.py         [NEW]

core/
├── polly.py             [MODIFIED] — _gather_context(), query(), session end
├── compression/manager.py [MODIFIED] — budget-aware build_context()
├── mental_models.py     [MODIFIED] — budget-aware build_context(), fix persona name
├── hardened/classifier.py [MODIFIED] — wire into main query path
└── config.py            [MODIFIED] — new config sections
```

---

## Part 1: Token Counter Service

### Problem

All token estimation throughout the codebase uses `len(text) // 4`. This is inaccurate by 15-30% depending on content (code vs prose, special characters, etc.). A budget system built on bad estimates will make bad allocation decisions.

### Design

**File:** `core/context/token_counter.py`

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_tokenizers: dict = {}  # Cache per model family


class TokenCounter:
    """
    Accurate token counting for budget allocation.
    Uses tiktoken for cloud models (OpenAI, Anthropic approximate),
    falls back to character-based estimation for Ollama models.
    """

    @staticmethod
    def count(text: str, model_id: str = "gpt-4") -> int:
        """
        Count tokens in text for the given model.

        Args:
            text: Input text
            model_id: Model identifier (e.g., "gpt-4", "claude-sonnet",
                      "llama3.2:latest")

        Returns:
            Token count (int)
        """

    @staticmethod
    def truncate(text: str, max_tokens: int, model_id: str = "gpt-4") -> str:
        """
        Truncate text to fit within max_tokens.
        Truncates at sentence boundaries when possible.

        Returns:
            Truncated text
        """

    @staticmethod
    def _get_tokenizer(model_id: str):
        """
        Get or create cached tokenizer for model family.
        Maps model IDs to tiktoken encodings:
          - gpt-4, gpt-4o, gpt-3.5 → cl100k_base
          - claude-* → cl100k_base (approximate, within ~5%)
          - llama*, ollama → None (use character estimation)
        """

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Fallback estimation for models without tiktoken support.
        Uses len(text) / 3.5 (slightly more conservative than /4).
        """
```

**Key decisions:**
- `tiktoken` is lazy-imported — if not installed, silently falls back to estimation. This keeps the dependency optional.
- Anthropic models use OpenAI's `cl100k_base` encoding as an approximation. Claude's actual tokenizer is not publicly available, but `cl100k_base` is within ~5% for typical content.
- Tokenizer instances are cached by model family (not per-model) to avoid re-initialization overhead.
- `truncate()` attempts sentence-boundary truncation to avoid mid-word cuts.

**Impact on Python backend:** Replaces `len(text) // 4` calls in `core/compression/manager.py`, `core/rag.py:1222` (`format_context` character limit), and `core/polly.py` (various threshold checks). These are find-and-replace changes with the new `TokenCounter.count()` call.

---

## Part 2: Budget Allocator

### Problem

Context assembly in `core/polly.py:1921-2012` concatenates system prompt + domain prompt + RAG header/instruction/results/footer + gathered context (mental models + entities + patterns + compression) + conversation history without any token accounting. There is no mechanism to say "RAG gets 30% of the budget" or "if mental models are large, shrink RAG to compensate."

### Design

**File:** `core/context/budget_allocator.py`

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class SectionBudget:
    """Budget allocation for one context section."""
    name: str
    priority: int          # 1 = highest (guaranteed), 6 = lowest
    min_tokens: int        # Floor — always allocated
    max_tokens: int        # Ceiling — never exceeded
    target_pct: float      # Target percentage of total budget
    allocated: int = 0     # Actual allocation after solving
    used: int = 0          # Tokens actually consumed


@dataclass
class BudgetPlan:
    """Complete budget allocation across all sections."""
    total_budget: int
    response_reserve: int
    sections: Dict[str, SectionBudget]
    overflow_tokens: int = 0  # Unallocated surplus

    def remaining(self, section: str) -> int:
        """Tokens remaining for a section."""
        return self.sections[section].allocated - self.sections[section].used

    def report_usage(self, section: str, tokens_used: int):
        """Record actual token usage for a section."""
        self.sections[section].used = min(tokens_used, self.sections[section].allocated)


class BudgetAllocator:
    """
    Distributes a total token budget across context sections
    using priority-based allocation with guaranteed minimums.
    """

    def __init__(self, config: dict):
        """
        Args:
            config: context_budget config section with keys:
                response_reserve, sections (dict of section configs)
        """

    def allocate(
        self,
        model_context_window: int,
        conversation_tokens: int,
        model_id: str = "gpt-4"
    ) -> BudgetPlan:
        """
        Compute budget allocation for a query.

        Algorithm:
        1. total = model_context_window - response_reserve
        2. Deduct conversation_tokens from total (conversation is pre-existing)
        3. Guarantee min_tokens for priority 1-2 sections
        4. Distribute remaining budget by target_pct, respecting min/max
        5. If under-budget, redistribute surplus to lower-priority sections
        6. If over-budget, compress highest-numbered priority sections first

        Args:
            model_context_window: Total context window of target model
            conversation_tokens: Tokens already consumed by conversation history
            model_id: For accurate token counting

        Returns:
            BudgetPlan with per-section allocations
        """

    def _solve_allocation(
        self,
        available: int,
        sections: List[SectionBudget]
    ) -> List[SectionBudget]:
        """
        Priority-based allocation solver.

        Pass 1: Allocate minimums for all sections (by priority order).
        Pass 2: Distribute remaining budget proportionally by target_pct.
        Pass 3: Cap at max_tokens, redistribute surplus.
        """
```

### Default Section Configuration

```yaml
context_budget:
  response_reserve: 2000      # Reserve for LLM response generation
  model_context_windows:       # Known context windows per model family
    gpt-4: 128000
    gpt-4o: 128000
    claude-sonnet: 200000
    claude-haiku: 200000
    llama3.2: 131072
    default: 8192              # Conservative default for unknown models
  sections:
    system_prompt:
      min: 500
      max: 2000
      target_pct: 0.10
      priority: 1              # Guaranteed — persona + constitutional layer
    conversation:
      min: 1000
      max: 8000
      target_pct: 0.25
      priority: 2              # Guaranteed — recent conversation history
    memory:
      min: 500
      max: 4000
      target_pct: 0.20
      priority: 3              # Tiered memory retrieval
    rag:
      min: 1000
      max: 6000
      target_pct: 0.30
      priority: 4              # RAG search results
    mental_models:
      min: 200
      max: 2000
      target_pct: 0.10
      priority: 5              # Active mental models
    entities:
      min: 100
      max: 1000
      target_pct: 0.05
      priority: 6              # Entity + pattern context
```

### Allocation Example

For a cloud query to Claude Sonnet (200K context) with 2,000 tokens of conversation history:

```
Total:          200,000
- Response:      -2,000
- Conversation:  -2,000
= Available:    196,000

But max_tokens caps apply:
  system_prompt:  2,000  (capped at max)
  memory:         4,000  (capped at max)
  rag:            6,000  (capped at max)
  mental_models:  2,000  (capped at max)
  entities:       1,000  (capped at max)
  overflow:     181,000  (unallocated — context window is much larger than needed)
```

For a local query to llama3.2 (131K context) with 8,000 tokens of conversation:

```
Total:          131,072
- Response:      -2,000
- Conversation:  -8,000
= Available:    121,072

Same caps apply — overflow is even larger for local models.
```

The budget allocator becomes meaningful when context is large relative to the window, or when future models with smaller windows are used.

### ContextContributor Protocol Update

Currently, `ContextContributor.build_context()` returns `str`. Update to accept budget:

```python
# Before (current)
class ContextContributor(Protocol):
    def build_context(self, query: str) -> str: ...

# After
class ContextContributor(Protocol):
    def build_context(self, query: str, token_budget: int = 0) -> str: ...
```

The `token_budget` parameter is optional (default 0 = no limit) for backward compatibility. Contributors that implement budget awareness use `TokenCounter.count()` to stay within their allocation. Contributors that ignore it continue to work — the rolling context bin-packer handles overflow by truncation.

**Impact on Electron app:** None. Budget allocation is entirely backend. The Electron app sends queries and receives responses unchanged.

---

## Part 3: Tiered Memory Store

### Problem

Mem0 is initialized with flat `persona:{name}` namespacing. There is no distinction between a permanent user preference ("I prefer TypeScript over JavaScript"), a recent decision ("we chose SQLite for the entity store last week"), and something from the current session ("we're currently discussing RAG scoring"). All would live in the same collection if they were stored at all — which, aside from the Scribe persona's enrichment preferences, they are not.

### Design

#### Memory Tier Definitions

**File:** `core/memory/tiers.py`

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime


class MemoryTier(str, Enum):
    STABLE = "stable"       # Long-term: preferences, structures, relationships
    EPISODIC = "episodic"   # Medium-term: session summaries, decisions, status
    WORKING = "working"     # Short-term: current session state


@dataclass
class MemoryEntry:
    """A single memory with tier-aware metadata."""
    content: str
    tier: MemoryTier
    metadata: 'MemoryMetadata'
    score: float = 0.0       # Composite relevance score (set by scorer)
    token_count: int = 0     # Cached token count


@dataclass
class MemoryMetadata:
    """Structured metadata for memory entries."""
    tier: str                              # "stable" | "episodic" | "working"
    domain: str = "general"                # Polly domain (sigils, signals, etc.)
    persona_source: str = "system"         # Which persona created this
    timestamp: str = ""                    # ISO 8601
    salience: float = 0.5                  # How important (0-1), set at write time
    reference_count: int = 0               # Times re-accessed across sessions
    last_referenced: str = ""              # ISO 8601
    source_type: str = "inferred"          # "user_stated" | "decision" | "inferred" | "extraction"
    session_id: str = ""                   # For working tier scoping
    tags: list = field(default_factory=list)


class TieredMemoryStore:
    """
    Manages three Mem0 collections as memory tiers.
    Wraps the existing Mem0Adapter with tier-aware read/write.
    """

    def __init__(self, mem0_adapter, config: dict):
        """
        Args:
            mem0_adapter: Existing Mem0Adapter instance
            config: memory.tiers config section
        """
        self.mem0 = mem0_adapter
        self.config = config
        self.session_id = datetime.now().isoformat()

    def write(self, content: str, tier: MemoryTier, metadata: dict) -> str:
        """
        Write a memory entry to the appropriate tier.

        Args:
            content: Memory text
            tier: Which tier to write to
            metadata: Additional metadata (domain, persona_source, etc.)

        Returns:
            Memory ID
        """

    def read(
        self,
        query: str,
        tiers: list[MemoryTier] = None,
        limit: int = 10,
        domain_filter: str = None,
        min_score: float = 0.0
    ) -> list[MemoryEntry]:
        """
        Retrieve memories across specified tiers.
        Applies tier-specific behavior:
          - stable: no decay, high trust
          - episodic: time-decay on scores
          - working: session-scoped, always included

        Args:
            query: Search query
            tiers: Which tiers to search (default: all)
            limit: Max results per tier
            domain_filter: Optional domain restriction
            min_score: Minimum retrieval score threshold

        Returns:
            List of MemoryEntry sorted by composite score
        """

    def flush_working(self):
        """Clear all working-tier memories (called at session end)."""

    def update_reference(self, memory_id: str):
        """Increment reference_count and update last_referenced timestamp."""

    def deduplicate_against(self, content: str, tier: MemoryTier) -> Optional[str]:
        """
        Check if content already exists in the tier.
        Returns existing memory_id if duplicate found, None otherwise.
        Uses semantic similarity with threshold 0.92.
        """
```

#### Mem0 Collection Mapping

Each tier maps to a Mem0 `user_id` namespace:

| Tier | Mem0 `user_id` | Mem0 `agent_id` |
|------|----------------|-----------------|
| Stable | `tier:stable` | `polly` (shared) |
| Episodic | `tier:episodic` | `polly` (shared) |
| Working | `tier:working:{session_id}` | `polly` (shared) |

This replaces the current `persona:{name}` scoping for the memory tiers. Persona-specific memory (Scribe enrichment preferences, etc.) continues to use its existing namespacing alongside the tiers — the two systems coexist. The tier system is for general Polly memory; persona memory is for persona-specific operational state.

**Impact on existing Mem0 usage:** The Scribe's direct `self.mem0.search_memory()` calls in `core/personas/implementations/scribe.py` continue to work unchanged — they use the `persona:scribe` namespace which is separate from the tier namespaces. No migration needed.

---

## Part 4: Memory Retriever (ContextContributor)

### Problem

Mem0 memories are available but never surface in the query pipeline. The `_gather_context()` method at `polly.py:834` calls four contributors (mental_models, entity_context, pattern_engine, compression_manager) but not Mem0.

### Design

**File:** `core/memory/retriever.py`

```python
from typing import Optional, List
import logging
import math
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """
    Retrieves and scores memories from the tiered store.
    Implements ContextContributor protocol (priority 50).
    """

    PRIORITY = 50  # Between mental_models (60) and entity_context (40)

    def __init__(self, tiered_store: 'TieredMemoryStore', config: dict):
        """
        Args:
            tiered_store: TieredMemoryStore instance
            config: memory config section
        """
        self.store = tiered_store
        self.config = config

    def build_context(self, query: str, token_budget: int = 0) -> str:
        """
        ContextContributor interface. Retrieves relevant memories
        from all tiers and formats them for the system prompt.

        Args:
            query: Current user query
            token_budget: Maximum tokens to consume

        Returns:
            Formatted memory context string
        """

    def retrieve(
        self,
        query: str,
        domains: list[str] = None,
        limit: int = 10
    ) -> List['MemoryEntry']:
        """
        Retrieve memories with tier-aware scoring.

        Pipeline:
        1. Search stable tier (limit=5, no decay)
        2. Search episodic tier (limit=5, apply time decay)
        3. Get all working tier entries (session-scoped)
        4. Score each entry via relevance_scorer
        5. Deduplicate across tiers (prefer stable > episodic > working)
        6. Sort by composite score, return top `limit`

        Args:
            query: Search query
            domains: Detected domains for filtering
            limit: Total results to return

        Returns:
            Scored, deduplicated, sorted MemoryEntry list
        """

    def _apply_time_decay(self, entry: 'MemoryEntry') -> float:
        """
        Apply exponential time decay to episodic entries.

        Formula: decay_factor = exp(-ln(2) * days_since_write / halflife_days)

        For halflife_days=90:
          - 1 day old: 0.992
          - 7 days old: 0.947
          - 30 days old: 0.794
          - 90 days old: 0.500
          - 180 days old: 0.250

        Stable tier: no decay (factor = 1.0)
        Working tier: no decay (factor = 1.0, session-scoped)
        """

    def _format_memories(
        self,
        memories: List['MemoryEntry'],
        token_budget: int
    ) -> str:
        """
        Format memories for system prompt injection.

        Format:
        ---
        ## Relevant Memory
        [stable] User prefers TypeScript over JavaScript for new projects.
        [episodic, 3 days ago] Decided to use SQLite-vec for the entity store.
        [working] Currently discussing RAG scoring improvements.
        ---

        Truncates at token_budget boundary.
        """
```

### Retrieval Tier Configuration

```yaml
memory:
  retrieval:
    stable_limit: 5           # Max results from stable tier per query
    episodic_limit: 5          # Max results from episodic tier
    working_include_all: true  # Include all working-tier entries
    min_similarity: 0.4        # Minimum cosine similarity to include
    dedup_threshold: 0.92      # Semantic similarity for deduplication
```

---

## Part 5: Relevance Scorer

### Problem

Different context sources use different scoring systems. RAG results have cosine similarity + RRF scores (`core/hybrid_search.py`). Mental models have activation scores with keyword matching (`core/mental_models.py`). Mem0 has its own internal similarity scores. These are not comparable — a 0.8 from RAG and a 0.8 from mental models mean very different things. The rolling context system needs a unified scoring space.

### Design

**File:** `core/context/relevance_scorer.py`

```python
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScoredEntry:
    """A context entry with composite relevance score."""
    content: str
    source: str                  # "memory:stable", "memory:episodic", "rag", "mental_model", etc.
    raw_score: float             # Original score from source system
    composite_score: float       # Unified relevance score (0-1)
    token_count: int             # Cached token count
    key_terms: list              # Terms for reference detection
    metadata: dict               # Source-specific metadata

    # Rolling context state
    reference_count: int = 0     # Times referenced in current session
    last_referenced_turn: int = 0
    turns_since_reference: int = 0


class RelevanceScorer:
    """
    Computes composite relevance scores for context entries
    from heterogeneous sources.
    """

    def __init__(self, config: dict):
        """
        Args:
            config: context_budget.relevance_weights section
        """
        self.weights = {
            "retrieval_similarity": config.get("retrieval_similarity", 0.35),
            "recency": config.get("recency", 0.25),
            "reference_frequency": config.get("reference_frequency", 0.15),
            "domain_affinity": config.get("domain_affinity", 0.15),
            "tier_weight": config.get("tier_weight", 0.10),
        }

    def score(
        self,
        entry: ScoredEntry,
        query_domains: list[str] = None,
        current_turn: int = 0
    ) -> float:
        """
        Compute composite relevance score.

        Formula:
          composite = (w1 * retrieval_similarity)
                    + (w2 * recency_score)
                    + (w3 * reference_frequency_score)
                    + (w4 * domain_affinity_score)
                    + (w5 * tier_weight_score)

        All component scores normalized to 0-1 range.
        Composite clamped to [0, 1].

        Args:
            entry: Context entry to score
            query_domains: Detected domains for affinity calculation
            current_turn: Current conversation turn number

        Returns:
            Composite score (0-1)
        """

    def _retrieval_similarity(self, entry: ScoredEntry) -> float:
        """
        Normalize raw scores from different sources to 0-1.

        RAG scores (already 0-1 from cosine): pass through
        Mem0 scores (already 0-1 from cosine): pass through
        Mental model scores (0-100 activation): divide by 100
        Pattern scores (variable): min-max normalize
        """

    def _recency_score(self, entry: ScoredEntry, current_turn: int) -> float:
        """
        Score based on how recently entry was referenced.

        If referenced this session:
          recency = max(0, 1 - (turns_since_reference * 0.15))
        If not referenced this session (from memory retrieval):
          recency based on timestamp metadata with tier-appropriate decay
        """

    def _reference_frequency_score(self, entry: ScoredEntry) -> float:
        """
        Score based on how often entry has been referenced.
        reference_frequency = min(reference_count / 5, 1.0)
        """

    def _domain_affinity_score(
        self,
        entry: ScoredEntry,
        query_domains: list[str]
    ) -> float:
        """
        Score based on domain match between entry and current query.

        Entry domain in query_domains[0] (primary): 1.0
        Entry domain in query_domains[1:] (secondary): 0.6
        Entry domain is "general" or "cross": 0.4
        Entry domain not in query_domains: 0.1
        """

    def _tier_weight_score(self, entry: ScoredEntry) -> float:
        """
        Fixed score by source type. Working memory is always
        maximally relevant (it's about right now). Stable memory
        is a reliable baseline. RAG is high. Episodic and others
        are moderate.

        memory:working   → 1.0
        rag              → 0.8
        memory:stable    → 0.6
        mental_model     → 0.5
        memory:episodic  → 0.4
        entity/pattern   → 0.3
        """
```

### Classifier Integration

The three-tier `RetrievalClassifier` at `core/hardened/classifier.py` currently classifies RAG results but the classification doesn't affect scoring in the main pipeline (TODO at `polly.py:1869`). Wire it in:

- **DIRECT** tier results: `raw_score` used as-is
- **ADJACENT** tier results: `raw_score *= 0.7` (penalty for indirect relevance)
- **ABSENT** tier: triggers expanded memory search — increase `episodic_limit` from 5 to 10, decrease `min_similarity` from 0.4 to 0.3. When RAG can't answer, memory becomes more important.

---

## Part 6: Rolling Context Window

### Problem

The current system has no concept of context evolving across turns. Every turn's context is assembled from scratch by querying RAG and contributors. There is no amplification of topics that keep coming up, no decay of tangential context, and no awareness of what was "active" in previous turns.

### Design

**File:** `core/context/rolling_context.py`

```python
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class RollingContext:
    """
    Maintains a dynamic working set of context entries across turns.
    Entries decay when unreferenced and amplify when re-referenced.
    Selection uses budget-aware greedy bin-packing.
    """

    def __init__(self, config: dict):
        """
        Args:
            config: context_budget.rolling section with keys:
                decay_per_turn, eviction_turns, amplification_reset
        """
        self.decay_rate = config.get("decay_per_turn", 0.85)
        self.eviction_turns = config.get("eviction_turns", 5)
        self.amplification_reset = config.get("amplification_reset", True)
        self.entries: List[ScoredEntry] = []
        self.turn_count: int = 0

    def ingest(self, new_entries: List[ScoredEntry]):
        """
        Add new entries from this turn's retrieval.
        Deduplicates against existing entries (same content hash).
        New entries that match existing ones update the existing
        entry's score if the new score is higher.
        """

    def on_new_turn(self, query: str, response: str):
        """
        Called after each turn completes. Updates all entries:

        1. Increment turn_count
        2. For each entry, check if referenced in query or response:
           - Referenced: reset recency_score to 1.0, increment reference_count
           - Not referenced: multiply recency component by decay_rate
        3. Evict entries with turns_since_reference >= eviction_turns
        4. Re-score all remaining entries

        Reference detection:
          Extract key_terms from entry. Check if any appear in
          query or response (case-insensitive token overlap).
          Threshold: >= 2 matching terms, or >= 1 if entry has <= 3 terms.
        """

    def select(
        self,
        section_budgets: dict[str, int]
    ) -> dict[str, List[ScoredEntry]]:
        """
        Bin-pack entries into sections within their budgets.

        Algorithm:
        1. Group entries by source section (memory, rag, mental_models, entities)
        2. For each section, sort entries by composite_score descending
        3. Greedily take entries until section budget exhausted
        4. Look-ahead of 5: if next entry doesn't fit, check smaller entries
        5. Position: highest-scored entries first (most prominent in attention)

        Args:
            section_budgets: {section_name: token_budget} from BudgetAllocator

        Returns:
            {section_name: [selected entries]} for each section
        """

    def _detect_reference(
        self,
        entry: ScoredEntry,
        text: str
    ) -> bool:
        """
        Check if an entry's content is referenced in text.
        Uses key_terms overlap (not semantic search — too expensive per-turn).

        key_terms extracted at ingest time:
          - Named entities, technical terms, proper nouns
          - Extracted via simple heuristics: capitalized words,
            terms in backticks, terms > 6 chars that aren't common words
        """

    def get_state(self) -> dict:
        """Return serializable state for debugging/metrics."""
```

### Decay Example

Turn 1: User asks about RAG scoring. Memory entry "User prefers TypeScript" is retrieved (score 0.5).
Turn 2: User continues on RAG. TypeScript entry not referenced → score *= 0.85 → 0.425.
Turn 3: Still on RAG. Not referenced → 0.361.
Turn 4: User mentions TypeScript. Referenced → recency resets to 1.0, reference_count++.
Turn 5: Not referenced → 0.85.
Turn 6+: Decay continues...

After 5 consecutive unreferenced turns, entry is evicted from the working set entirely. It can be re-retrieved by the memory retriever if it becomes relevant again.

### Bin-Packing

The selection algorithm is greedy with bounded look-ahead, not optimal. Optimal bin-packing is NP-hard. The greedy approach with a look-ahead of 5 entries captures most of the value:

```
Entries sorted by score: [A(0.95, 800tok), B(0.88, 600tok), C(0.82, 1200tok), D(0.78, 400tok)]
Budget: 1500 tokens

1. Take A (800tok) → 700 remaining
2. Try B (600tok) → fits → take B → 100 remaining
3. Try C (1200tok) → doesn't fit → look ahead...
4. Try D (400tok) → doesn't fit → no more entries fit
Result: [A, B] = 1400/1500 tokens used
```

---

## Part 7: Session-End Extraction Pipeline

### Problem

When a conversation ends, everything discussed is lost unless the user manually creates a note. The compression system stores compressed conversation summaries in SQLite (`~/.polly/compression.db`), but these are optimized for conversation continuity, not for fact extraction. They store things like "task was code review" and "mode was standard" — not "user decided to use SQLite-vec for entities" or "user prefers functional patterns over OOP."

### Design

**File:** `core/memory/extractor.py`

```python
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFact:
    """A fact extracted from conversation for memory storage."""
    content: str
    tier: str              # "stable" or "episodic"
    source_type: str       # "user_stated" | "decision" | "inferred" | "status"
    domain: str            # Detected domain
    salience: float        # 0-1, extraction confidence
    tags: list


class SessionExtractor:
    """
    Extracts structured facts from completed sessions
    and writes them to the tiered memory store.
    """

    def __init__(
        self,
        tiered_store: 'TieredMemoryStore',
        config: dict,
        budget_manager=None
    ):
        """
        Args:
            tiered_store: TieredMemoryStore for writes
            config: memory.extraction config section
            budget_manager: Optional BudgetManager for cost tracking
        """
        self.store = tiered_store
        self.config = config
        self.budget_manager = budget_manager

    async def extract_and_store(
        self,
        conversation_history: list[dict],
        compression_summary: dict,
        session_metadata: dict
    ) -> 'ExtractionResult':
        """
        End-to-end extraction pipeline.

        Steps:
        1. Assess session value (complexity, domain count, decisions detected)
        2. Select extraction model (local or cloud based on session value)
        3. Build extraction prompt with conversation + compression signals
        4. Call model to extract structured facts
        5. Classify each fact into stable vs episodic tier
        6. Deduplicate against existing memory
        7. Write new/updated facts to tiers
        8. Flush working tier

        Args:
            conversation_history: Full conversation messages
            compression_summary: From ConversationCompressor (decisions, focus_topics)
            session_metadata: domain, persona, duration, etc.

        Returns:
            ExtractionResult with counts and details
        """

    def _assess_session_value(
        self,
        conversation_history: list[dict],
        session_metadata: dict
    ) -> str:
        """
        Determine extraction model tier.

        Returns "cloud" if any of:
          - Multiple domains detected in session
          - Session complexity >= "balanced" (from router decisions)
          - Explicit user decisions detected (via compression_summary.decisions)
          - Session > 20 exchanges

        Returns "local" otherwise.
        """

    def _build_extraction_prompt(
        self,
        conversation_history: list[dict],
        compression_summary: dict
    ) -> str:
        """
        Build the extraction prompt.

        Instructs the model to extract:
        1. STABLE facts: user preferences, project structures, technical decisions
           that won't change. Source type: "user_stated" if explicitly said,
           "inferred" if implied by behavior.
        2. EPISODIC facts: session decisions (with rationale), in-progress work,
           context about current projects. Source type: "decision" or "status".

        Uses compression_summary.decisions and compression_summary.focus_topics
        as pre-extracted signals to guide the LLM.

        Output format: JSON array of {content, tier, source_type, domain, salience, tags}
        """

    async def _call_extraction_model(
        self,
        prompt: str,
        model_tier: str
    ) -> list[ExtractedFact]:
        """
        Call local or cloud model for extraction.

        Local: POST to Ollama with llama3.2:latest
        Cloud: Call via router_v2 with claude-haiku, budget-capped at max_cloud_cost

        Parse JSON response into ExtractedFact objects.
        On parse failure, attempt recovery (regex extraction, retry with simpler prompt).
        On total failure, log warning and return empty list (non-critical).
        """

    def _classify_tier(self, fact: ExtractedFact) -> str:
        """
        Validate/override tier classification from model.

        Rules:
          - Preferences (contains "prefer", "like", "always", "never") → stable
          - Project structures (contains project names, file paths) → stable
          - Decisions with temporal context ("decided to", "chose") → episodic
          - Status updates ("working on", "in progress", "next step") → episodic
          - Anything with salience < 0.3 → skip (too low confidence)
        """

    def _deduplicate(
        self,
        facts: list[ExtractedFact]
    ) -> list[ExtractedFact]:
        """
        Remove facts that already exist in the store.
        For contradictions (same topic, different content), update existing.

        Uses TieredMemoryStore.deduplicate_against() with 0.92 similarity threshold.
        """
```

### Extraction Prompt Template

```
You are extracting structured facts from a conversation for a personal AI assistant's memory system.

Session context:
- Domains discussed: {domains}
- Key topics: {focus_topics}
- Decisions detected: {decisions}

Conversation:
{last_N_messages}

Extract facts into two categories:

STABLE (permanent, won't change):
- User preferences and opinions explicitly stated
- Project structures and relationships learned
- Technical choices and standards established
- Personal information shared

EPISODIC (time-bound, may change):
- Decisions made in this session (with brief rationale)
- Work in progress or next steps mentioned
- Context about current projects or tasks
- Problems being actively worked on

For each fact, provide:
- content: The fact in one clear sentence
- tier: "stable" or "episodic"
- source_type: "user_stated" (they said it) | "decision" (they chose it) | "status" (current state) | "inferred" (implied)
- domain: primary domain (sigils/signals/scrolls/glyphs/grids/general)
- salience: 0.0-1.0 (how important is this to remember)
- tags: relevant keywords

Output as JSON array. If no meaningful facts to extract, return [].
```

### Model Routing

| Session Characteristic | Model | Estimated Cost |
|----------------------|-------|---------------|
| Simple, single domain, < 10 exchanges | `llama3.2:latest` (local) | $0.00 |
| Multi-domain, explicit decisions, or > 20 exchanges | `claude-haiku` (cloud) | ~$0.003-0.008 |
| Complex with high-value decisions | `claude-haiku` (cloud) | ~$0.008-0.015 |

Cloud extraction is budget-capped at `max_cloud_cost` (default $0.02) via the existing `BudgetManager`.

---

## Part 8: Pipeline Integration

### Modified: `core/polly.py`

#### Initialization Sequence

Add after Mem0 init (~line 130), before router init:

```python
# Tiered Memory Store
self.tiered_store = None
self.memory_retriever = None
self.session_extractor = None
if self.mem0:
    from core.memory.tiers import TieredMemoryStore
    from core.memory.retriever import MemoryRetriever
    from core.memory.extractor import SessionExtractor
    self.tiered_store = TieredMemoryStore(self.mem0, self.config.get("memory.tiers", {}))
    self.memory_retriever = MemoryRetriever(self.tiered_store, self.config.get("memory", {}))
    self.session_extractor = SessionExtractor(
        self.tiered_store,
        self.config.get("memory.extraction", {}),
        budget_manager=self.budget_manager
    )

# Context Infrastructure
from core.context.budget_allocator import BudgetAllocator
from core.context.relevance_scorer import RelevanceScorer
from core.context.rolling_context import RollingContext
self.budget_allocator = BudgetAllocator(self.config.get("context_budget", {}))
self.relevance_scorer = RelevanceScorer(
    self.config.get("context_budget.relevance_weights", {})
)
self.rolling_context = RollingContext(self.config.get("context_budget.rolling", {}))
```

#### Modified `_gather_context()` (line 834)

```python
async def _gather_context(self, query: str, budget_plan: 'BudgetPlan') -> str:
    """
    Gather context from all contributors, scored and budget-constrained.

    Modified from original: each contributor receives a token budget,
    results are scored by relevance_scorer, and rolling_context
    handles selection and bin-packing.
    """
    contributors = []

    # Existing contributors (unchanged initialization)
    if self.mental_model_manager:
        contributors.append(("mental_models", self.mental_model_manager, 60))
    if self.memory_retriever:  # NEW
        contributors.append(("memory", self.memory_retriever, 50))
    if hasattr(self, 'entity_context') and self.entity_context:
        contributors.append(("entities", self.entity_context, 40))
    if self.pattern_engine:
        contributors.append(("entities", self.pattern_engine, 20))
    if self.compression_manager:
        contributors.append(("entities", self.compression_manager, 10))

    # Sort by priority (descending) — unchanged
    contributors.sort(key=lambda x: x[2], reverse=True)

    # Call each contributor with its budget allocation
    scored_entries = []
    for section, contributor, priority in contributors:
        try:
            budget = budget_plan.remaining(section)
            context_text = contributor.build_context(query, token_budget=budget)
            if context_text:
                entry = ScoredEntry(
                    content=context_text,
                    source=section,
                    raw_score=priority / 100,  # Normalize priority to 0-1
                    composite_score=0.0,
                    token_count=TokenCounter.count(context_text),
                    key_terms=extract_key_terms(context_text),
                    metadata={"priority": priority}
                )
                entry.composite_score = self.relevance_scorer.score(entry)
                scored_entries.append(entry)
        except Exception as e:
            logger.debug(f"Context contributor {section} failed: {e}")

    # Ingest into rolling context and select
    self.rolling_context.ingest(scored_entries)
    section_budgets = {
        name: budget_plan.remaining(name)
        for name in budget_plan.sections
    }
    selected = self.rolling_context.select(section_budgets)

    # Assemble selected context
    parts = []
    for section_name, entries in selected.items():
        for entry in entries:
            parts.append(entry.content)
            budget_plan.report_usage(section_name, entry.token_count)

    return "\n\n".join(parts)
```

#### Session-End Hook

Add to `query()` return path or as a separate method triggered by session-end events:

```python
async def _on_session_end(self):
    """
    Triggered when session ends (timeout, explicit close, or app shutdown).
    Extracts facts and writes to tiered memory.
    """
    if not self.session_extractor:
        return

    try:
        # Get compression summary for pre-extracted signals
        compression_summary = {}
        if self.compression_manager:
            compression_summary = self.compression_manager.get_current_summary()

        session_metadata = {
            "duration_minutes": (datetime.now() - self.session_start).total_seconds() / 60,
            "exchange_count": len(self.conversation_history) // 2,
            "domains": list(set(
                msg.get("domain", "general")
                for msg in self.conversation_history
            )),
        }

        result = await self.session_extractor.extract_and_store(
            self.conversation_history,
            compression_summary,
            session_metadata
        )

        logger.info(
            f"Session extraction: {result.stable_count} stable, "
            f"{result.episodic_count} episodic facts stored"
        )

        # Flush working memory
        if self.tiered_store:
            self.tiered_store.flush_working()

    except Exception as e:
        logger.warning(f"Session-end extraction failed: {e}")
```

#### Turn Tracking

Add after each response is generated in `query()`:

```python
# After response is generated, before return
if self.rolling_context:
    self.rolling_context.on_new_turn(user_query, response_text)
```

### Modified: `core/mental_models.py`

1. **Fix persona name mismatch.** In `_get_default_models()`, change `"teacher"` to `"professor"` in all `active_for_personas` lists for pedagogy-related models (Pedagogy of Liberation, Socratic Method, Reverse Engineering, etc.).

2. **Budget-aware `build_context()`.** Accept optional `token_budget` parameter. If provided, use `TokenCounter.truncate()` to stay within budget. The existing compact format compression already produces concise output — this is a safety net.

### Modified: `core/hardened/classifier.py`

Wire `RetrievalClassifier.classify()` results into the query pipeline at `polly.py:1857-1884`. Use the classification tier to:
- Adjust RAG result scores via `relevance_scorer` (ADJACENT gets 0.7x multiplier)
- Adjust memory retrieval aggressiveness (ABSENT increases episodic limit and decreases min_similarity)
- Set tier-appropriate prompt language (already designed in the classifier, currently unused)

---

## Configuration

### Full `config.yaml` Addition

```yaml
memory:
  provider: "mem0"
  extraction:
    enabled: true
    cloud_threshold: "balanced"      # Session complexity that triggers cloud model
    cloud_model: "claude-haiku"
    local_model: "llama3.2:latest"
    max_cloud_cost: 0.02             # Per-extraction budget cap
  tiers:
    stable:
      collection: "memory_stable"
      decay: null                    # No decay for stable facts
    episodic:
      collection: "memory_episodic"
      decay_halflife_days: 90        # Score halves every 90 days
    working:
      collection: "memory_working"
      session_scoped: true
  retrieval:
    stable_limit: 5
    episodic_limit: 5
    working_include_all: true
    min_similarity: 0.4
    dedup_threshold: 0.92

context_budget:
  response_reserve: 2000
  model_context_windows:
    gpt-4: 128000
    gpt-4o: 128000
    claude-sonnet: 200000
    claude-haiku: 200000
    llama3.2: 131072
    default: 8192
  sections:
    system_prompt:
      min: 500
      max: 2000
      target_pct: 0.10
      priority: 1
    conversation:
      min: 1000
      max: 8000
      target_pct: 0.25
      priority: 2
    memory:
      min: 500
      max: 4000
      target_pct: 0.20
      priority: 3
    rag:
      min: 1000
      max: 6000
      target_pct: 0.30
      priority: 4
    mental_models:
      min: 200
      max: 2000
      target_pct: 0.10
      priority: 5
    entities:
      min: 100
      max: 1000
      target_pct: 0.05
      priority: 6
  relevance_weights:
    retrieval_similarity: 0.35
    recency: 0.25
    reference_frequency: 0.15
    domain_affinity: 0.15
    tier_weight: 0.10
  rolling:
    decay_per_turn: 0.85
    eviction_turns: 5
    amplification_reset: true
```

### `core/config.py` DEFAULT_CONFIG Addition

```python
"memory": {
    "provider": "mem0",
    "extraction": {
        "enabled": True,
        "cloud_threshold": "balanced",
        "cloud_model": "claude-haiku",
        "local_model": "llama3.2:latest",
        "max_cloud_cost": 0.02,
    },
    "tiers": {
        "stable": {"collection": "memory_stable", "decay": None},
        "episodic": {"collection": "memory_episodic", "decay_halflife_days": 90},
        "working": {"collection": "memory_working", "session_scoped": True},
    },
    "retrieval": {
        "stable_limit": 5,
        "episodic_limit": 5,
        "working_include_all": True,
        "min_similarity": 0.4,
        "dedup_threshold": 0.92,
    },
},
"context_budget": {
    "response_reserve": 2000,
    "model_context_windows": {
        "gpt-4": 128000,
        "gpt-4o": 128000,
        "claude-sonnet": 200000,
        "claude-haiku": 200000,
        "llama3.2": 131072,
        "default": 8192,
    },
    "sections": {
        "system_prompt": {"min": 500, "max": 2000, "target_pct": 0.10, "priority": 1},
        "conversation": {"min": 1000, "max": 8000, "target_pct": 0.25, "priority": 2},
        "memory": {"min": 500, "max": 4000, "target_pct": 0.20, "priority": 3},
        "rag": {"min": 1000, "max": 6000, "target_pct": 0.30, "priority": 4},
        "mental_models": {"min": 200, "max": 2000, "target_pct": 0.10, "priority": 5},
        "entities": {"min": 100, "max": 1000, "target_pct": 0.05, "priority": 6},
    },
    "relevance_weights": {
        "retrieval_similarity": 0.35,
        "recency": 0.25,
        "reference_frequency": 0.15,
        "domain_affinity": 0.15,
        "tier_weight": 0.10,
    },
    "rolling": {
        "decay_per_turn": 0.85,
        "eviction_turns": 5,
        "amplification_reset": True,
    },
},
```

---

## Edge Cases

### 1. Mem0 Not Configured

**Handling:** If `memory.provider` is "local" or Mem0 is not available, `tiered_store` and `memory_retriever` are `None`. The budget allocator still functions — the memory section's budget is redistributed to other sections. Session-end extraction is skipped. All other context contributors work as before, now with budget governance.

### 2. Empty Memory Tiers

**Handling:** On first run, all tiers are empty. `MemoryRetriever.retrieve()` returns an empty list. The budget allocator assigns memory's budget to overflow, which is redistributed to RAG and other sections. As sessions accumulate, memory entries populate naturally.

### 3. Extraction Model Unavailable

**Handling:** If local Ollama is down and cloud is over budget, extraction is skipped. Log a warning. Conversations are still compressed by the existing `CompressionManager` — extraction is additive, not a replacement. Next session with a working model will extract normally.

### 4. Contradictory Facts

**Handling:** If extraction produces a fact that contradicts an existing stable memory (e.g., old: "user prefers JavaScript", new: "user prefers TypeScript"), the deduplication step detects high similarity with different content. The extractor calls `TieredMemoryStore.write()` to update the existing entry with new content and resets the timestamp. The old fact is overwritten, not duplicated.

### 5. Very Long Sessions (> 100 exchanges)

**Handling:** The extraction prompt receives only the last N messages (configurable, default 30) plus the compression summary of earlier messages. This keeps extraction prompt size bounded while still capturing the full session's signals via compression.

### 6. Working Tier Overflow

**Handling:** Working tier is session-scoped and flushed at session end. Within a session, if working tier grows beyond `memory.retrieval.working_max` (default 50 entries), oldest entries by insertion time are evicted.

---

## Testing Strategy

### Unit Tests

1. **TokenCounter:** Verify accuracy within 5% of tiktoken for representative text samples (code, prose, mixed).
2. **BudgetAllocator:** Verify min/max constraints respected. Verify surplus redistribution. Verify priority ordering under pressure.
3. **TieredMemoryStore:** Verify write/read across tiers. Verify working tier session scoping. Verify deduplication at 0.92 threshold.
4. **RelevanceScorer:** Verify composite score in [0, 1]. Verify weight contributions sum correctly. Verify domain affinity scoring.
5. **RollingContext:** Verify decay reduces scores per turn. Verify amplification resets recency. Verify eviction after N turns. Verify bin-packing respects budgets.
6. **SessionExtractor:** Verify fact classification (stable vs episodic). Verify deduplication against existing memory. Verify model routing (local vs cloud).

### Integration Tests

1. **Full pipeline:** Query → memory retrieval → RAG → budget allocation → rolling context selection → response → turn tracking.
2. **Session lifecycle:** Start session → 10 exchanges → session end → verify extraction → start new session → verify memories retrieved.
3. **Decay across turns:** Submit 5 queries on topic A, switch to topic B for 5 queries, verify topic A context decays and topic B amplifies.
4. **Budget enforcement:** Submit query with large RAG results + many mental models → verify total tokens stay within budget.
5. **Existing functionality:** Verify Scribe enrichment preferences still work (separate Mem0 namespace). Verify all existing ContextContributors still function.

### Manual Testing Checklist

- [ ] State a preference in one session, close, reopen — verify it's remembered
- [ ] Make a decision with rationale — verify it's extracted as episodic memory
- [ ] Have a long conversation that drifts across topics — verify context stays focused on current topic
- [ ] Submit a query that exceeds context window — verify budget allocator truncates gracefully
- [ ] Run with Mem0 disabled — verify system degrades gracefully to current behavior

---

## Future Enhancements (Out of Scope)

- **Persona-specific memory policies:** Which personas can read/write which tiers, persona-specific extraction templates.
- **Memory management UI:** Electron interface for browsing, editing, deleting memories across tiers.
- **Adaptive relevance weights:** Use pattern learning to optimize scoring weights per domain over time.
- **Memory consolidation:** Periodic job that promotes frequently-referenced episodic memories to stable tier.
- **Cross-session reference tracking:** Track which memories lead to better responses (via user feedback) and boost their salience.

# Query Routing & Constitutional Integration — Design Problem

**Created:** February 15, 2026  
**Scope:** Backend — query routing, complexity scoring, RAG integration, constitutional epistemology  
**Triggered by:** Testing constitutional epistemology layer with query "I want to talk about the Somali problem in Minneapolis, MN"  
**Status:** ANALYSIS COMPLETE — awaiting design decisions

---

## The Test Case

A user asks: **"I want to talk about the Somali problem in Minneapolis, MN."**

This query should trigger multiple systems:
- **Constitutional epistemology:** Scapegoat suspicion (Principle 3) — "the \_\_\_ problem" is a classic scapegoat framing
- **Complexity assessment:** This is a deeply complex sociopolitical topic requiring structural analysis, historical context, and careful handling
- **RAG classification:** The user's notes may contain *adjacent* material (immigration, urban policy, education) but are unlikely to have *direct* coverage of Somali diaspora in Minneapolis
- **External knowledge:** The system should recognize it needs outside information to answer well

**What actually happened:**
```
[Complexity] score=0.00, threshold=0.6, complex=False
[Wave 3 Query] Query is simple, using standard routing
```

The query scored 0.00 complexity, was classified as a simple factual lookup, got matched to the user's notes (tangentially), and the LLM was told to "prioritize information from the knowledge base context above." The constitutional layer never reached the LLM.

---

## Three Interconnected Issues

### Issue 1: The Constitutional Layer Doesn't Reach the LLM

**What:** The constitutional epistemology layer (`core/constitutional/layer.py`) is implemented and importable, but the main query path never uses it.

**Why:** There are two independent prompt construction paths:
1. `Polly.query()` → `_build_system_prompt()` at `core/polly.py:626` — **THE MAIN PATH.** Builds a generic Polly persona prompt. Does not import or call `get_constitutional_layer()`.
2. `PersonaManager.get_system_prompt()` at `core/personas/manager.py:509` — Includes constitutional layer. Only used when a persona is explicitly activated.
3. `BasePersona._build_messages()` at `core/personas/base.py:337` — Now includes constitutional layer (recent fix). Only used when a persona processes a query.

**The gap:** Most queries go through path #1. The constitutional layer lives in paths #2 and #3 which are only active during explicit persona processing. The "nervous system" we built never reaches the brain.

**Where the fix belongs:** `core/polly.py:626` (`_build_system_prompt()`) or `core/polly.py:1800` (the augmented system prompt assembly). The constitutional layer must be part of the prompt that every query sees, not just persona-routed queries.

**Complexity of fix:** Low — one import and one line of code. But the design question is *where* in the prompt hierarchy it goes and how it interacts with persona prompts (avoid duplication when persona is active).

---

### Issue 2: Complexity Scoring Is Purely Syntactic

**What:** The complexity gate at `core/query_decomposition.py:218` (`_is_complex_query()`) uses only syntactic heuristics to determine whether a query needs decomposition. A deeply nuanced sociopolitical query scores 0.00 because it's a single declarative sentence.

**The scoring algorithm:**
```python
complexity_indicators = [
    ' and ' in query_lower and any(word in query_lower for word in ['then', 'can you', ...]),
    ' then ' in query_lower,
    ' also ' in query_lower,
    query.count('?') > 1,
    'after that' in query_lower,
    ...
]
question_count = sum(query_lower.count(qw) for qw in ['what', 'how', 'why', ...])

complexity_score = sum(complexity_indicators) * 0.25 + min(question_count * 0.15, 0.4)
```

**What it measures:** Multi-part task structure. "Do X and then Y." "What is A and how does B work?"

**What it doesn't measure:**
- Semantic complexity (nuanced topics that require careful analysis)
- Topic sensitivity (politically loaded, historically complex, emotionally charged)
- Knowledge requirements (does the system actually *have* the knowledge to answer this?)
- Analytical depth required (does this need structural analysis vs. a factual lookup?)

**Why this matters for the test case:** "I want to talk about the Somali problem in Minneapolis" has:
- Zero question marks
- Zero question words (what, how, why)
- No conjunctions indicating multi-part structure
- Score: 0.00

It gets classified as `SubQueryType.FACTUAL` — the default fallback at `core/query_decomposition.py:307`. A topic that demands historical analysis, structural understanding, awareness of political framing, and sensitivity to scapegoat narratives is treated as "look up a fact."

**The design question:** What should complexity mean? The current system measures *structural* complexity (multi-part queries). But the test case reveals a need for *analytical* complexity — recognizing when a topic requires deeper engagement even if the query itself is syntactically simple.

**Possible approaches:**
1. **Topic sensitivity signals:** Detect politically loaded, historically complex, or socially sensitive topics and boost complexity score
2. **Constitutional trigger detection:** If the query matches constitutional principle patterns (scapegoat framing, essentialist claims, cui bono situations), boost complexity
3. **RAG gap detection:** If RAG results are weak/tangential for a substantive query, that signals the system needs external information — boost complexity
4. **LLM-based complexity assessment:** Use a cheap/fast LLM call to assess whether a query needs deep analysis (expensive but accurate)
5. **Hybrid:** Combine syntactic + topic + RAG gap signals

---

### Issue 3: Strong RAG + "Simple" Classification = Echo Chamber

**What:** When RAG finds matches in the user's notes (even tangential ones), and the query is classified as "simple," the system wraps those notes into context with strong directive language:

```
**IMPORTANT**: The context below contains information from {user_name}'s actual 
notes and knowledge base. You MUST reference and use this specific information 
when answering questions.
```

And:

```
When answering questions, prioritize information from the knowledge base context above.
```

(From `core/polly.py:1806-1812`)

**Why this matters for the test case:** The user asks about the "Somali problem in Minneapolis." RAG finds notes that are *adjacent* — maybe about immigration policy, urban education, or community organizing. The system tells the LLM to *prioritize* this tangential information. The LLM dutifully connects the user's notes to the query, producing a response that's interesting but not actually about the topic the user raised.

**The deeper problem:** The system assumes that if RAG finds something, it's relevant. But relevance is not binary. The three-tier retrieval classifier (`core/hardened/classifier.py`) was built to distinguish DIRECT / ADJACENT / ABSENT — but it's not integrated into the main query path. The main path at `core/polly.py` doesn't use `RetrievalTier` at all.

**What should happen:**
- **DIRECT RAG hits:** "Prioritize this information" is correct
- **ADJACENT RAG hits:** "Here's related context from your notes, but the query needs additional analysis/information"
- **ABSENT RAG hits:** "No directly relevant notes found" + seek external information or provide general knowledge

**The current behavior conflates all three into "PRIORITIZE THIS."**

**Related infrastructure that exists but isn't connected:**
- `core/hardened/classifier.py` — Three-tier classification (DIRECT/ADJACENT/ABSENT)
- `core/hardened/validator.py` — Constitutional checks on RAG content (scapegoat/essentialist detection)
- `config/validation.yaml` — Thresholds for tier classification

These were built as part of the hardened knowledge infrastructure but haven't been integrated into `Polly.query()`.

---

## How The Issues Interact

These three issues form a reinforcing pattern:

```
1. No constitutional layer in prompt
   → LLM has no instruction to recognize scapegoat framing
   → Responds to query at face value
   
2. Syntactic-only complexity scoring
   → "Simple" declaration about complex topic
   → No decomposition, no external search, no deeper analysis
   → Classified as FACTUAL lookup
   
3. RAG prioritization without tier awareness  
   → Tangential notes treated as primary source
   → LLM told to "prioritize" user's own (tangential) notes
   → Response reflects user's existing knowledge back
   → No new information, no structural analysis
```

**Net effect:** A query that demands Polly's best analytical capabilities gets the shallowest possible treatment. The constitutional layer (designed to make shallow analysis look shallow by offering deeper analysis) is absent. The routing system (designed to decompose complex queries) doesn't trigger. The RAG system (designed to surface relevant knowledge) surfaces tangential matches and treats them as authoritative.

The user gets their own notes reflected back instead of the education the system was designed to provide.

---

## Existing Infrastructure That Could Help

| Component | File | Status | Could Address |
|-----------|------|--------|---------------|
| Constitutional layer prompt | `core/constitutional/layer.py` | ✅ Built, not connected to main path | Issue 1 |
| Three-tier retrieval classifier | `core/hardened/classifier.py` | ✅ Built, not integrated | Issue 3 |
| Content validator (scapegoat/essentialist) | `core/hardened/validator.py` | ✅ Built, validates RAG content | Issues 1+3 |
| Dual validator pipeline | `core/hardened/validator.py` | ✅ Built, not in query path | Issue 3 |
| Wave 3 decomposition | `core/query_decomposition.py` | ✅ Built, syntactic only | Issue 2 |
| Split routing | `core/split_routing.py` (if exists) | ✅ Built | Issue 2 |
| Router V2 complexity classifier | `libs/polly-routing/` | ✅ Built, separate from Wave 3 | Issue 2 |

Multiple pieces of infrastructure were built to handle exactly these problems but aren't wired together in the main query path.

---

## Design Questions

Before implementing fixes, these questions need answers:

### Q1: Where does the constitutional layer go?
- **Option A:** In `_build_system_prompt()` — always present, simple
- **Option B:** In the augmented system assembly at line 1800 — alongside RAG context
- **Option C:** Both paths (Polly.query AND PersonaManager) with deduplication
- **Concern:** When a persona IS active, the constitutional layer would be present twice (once from base.py, once from polly.py). Need to decide: one source of truth, or deduplication logic?

### Q2: Should complexity scoring use the constitutional layer's pattern detection?
- The constitutional principles define trigger patterns (scapegoat framing, essentialist claims, cui bono situations)
- The content validator already has regex patterns for detecting these in RAG content
- Could the same patterns be used on the *user query* to boost complexity score?
- This would mean: query contains scapegoat framing → complexity boost → deeper analysis path

### Q3: Should RAG tier classification gate the "prioritize" instruction?
- DIRECT → "Prioritize this information"
- ADJACENT → "Here's related context, but this topic needs broader analysis"
- ABSENT → "No directly relevant notes. Here's what I know from training data."
- This requires integrating `core/hardened/classifier.py` into `Polly.query()`

### Q4: What's the interaction between constitutional detection on the query vs. on RAG results?
- Currently: content validator checks RAG *content* for scapegoat/essentialist patterns
- Proposed: also check the user *query* for these patterns
- When both trigger, what happens? Does the system:
  - Boost complexity and decompose the query?
  - Add constitutional analysis instructions to the prompt?
  - Modify RAG prioritization language?
  - All of the above?

### Q5: Is this a single change or multiple?
- Issue 1 (constitutional layer in main path) is a one-line fix
- Issue 2 (complexity scoring) is a significant redesign of the decomposition gate
- Issue 3 (RAG tier integration) connects existing infrastructure
- They're interconnected but could be implemented incrementally

---

## Proposed Implementation Order

If we proceed incrementally:

### Phase A: Constitutional Layer in Main Path (Issue 1)
**Scope:** Small  
**Files:** `core/polly.py` — add constitutional layer to `_build_system_prompt()` or augmented system assembly  
**Risk:** Low  
**Effect:** Constitutional epistemology shapes every response, even without personas  
**Deduplication needed:** Handle case where persona is also active

### Phase B: RAG Tier Integration (Issue 3)
**Scope:** Medium  
**Files:** `core/polly.py` — integrate `RetrievalClassifier` from `core/hardened/classifier.py`  
**Risk:** Medium — changes how RAG context is presented to LLM  
**Effect:** System distinguishes DIRECT/ADJACENT/ABSENT and adjusts instructions accordingly  
**Dependency:** Existing classifier infrastructure

### Phase C: Semantic Complexity Scoring (Issue 2)
**Scope:** Large  
**Files:** `core/query_decomposition.py` — redesign `_is_complex_query()`  
**Risk:** Higher — affects all query routing  
**Effect:** Nuanced topics get appropriate analytical depth  
**Dependency:** Could benefit from Phase A (constitutional patterns as complexity signals)

---

## References

**Specs:**
- `openspec/specs/ethics/spec.md` — Constitutional epistemology specification
- `openspec/specs/rag/spec.md` — Three-tier retrieval, content validation
- `openspec/changes/constitutional-epistemology/` — Constitutional implementation
- `openspec/changes/hardened-knowledge-infrastructure/` — Validator/classifier implementation

**Code:**
- `core/polly.py:626` — `_build_system_prompt()` (missing constitutional layer)
- `core/polly.py:1800` — Augmented system prompt assembly
- `core/query_decomposition.py:218` — `_is_complex_query()` (syntactic only)
- `core/query_decomposition.py:282` — `_classify_simple_query()` (defaults to FACTUAL)
- `core/constitutional/layer.py` — Constitutional epistemology prompt
- `core/hardened/classifier.py` — Three-tier retrieval classifier (not integrated)
- `core/hardened/validator.py:407` — Scapegoat narrative detection
- `core/hardened/validator.py:438` — Essentialist claim detection
- `core/personas/base.py:337` — `_build_messages()` (constitutional layer added, persona path only)
- `core/personas/manager.py:509` — `get_system_prompt()` (constitutional layer, persona path only)

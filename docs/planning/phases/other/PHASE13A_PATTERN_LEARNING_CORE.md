# Phase 13a: Pattern Learning System - Core Intelligence Layer

**Status:** IN PROGRESS (Days 1-8 COMPLETE ✅)  
**Priority:** Tier 1 (High Priority)  
**Estimated Effort:** 16 days (core implementation) + 14 days (ancillary documentation) = 30 days total  
**Complexity:** High  
**Dependencies:** Phase 1.5 (domain keywords for concept validation)  
**Provides To:** Phases 1.5, 3, 6, 10, 11, 12, 18, 20 (all leverage patterns)

**Progress:**
- ✅ Days 1-2: Foundation & Storage v2.0 (COMPLETE)
- ✅ Days 3-4: spaCy Concept Extraction (COMPLETE)
- ✅ Days 5-8: Query→Chunk Pattern Learning (COMPLETE) 🚀 **HIGHEST VALUE**
- ✅ Days 9-11: Domain→Collection Priorities (COMPLETE) 🎯 **20-40% RAG SPEEDUP**
- ⏳ Days 12-13: Conceptual Pattern Refinement (PLANNED)
- ⏳ Days 14-15: Pattern Quality Controls (PLANNED)
- ⏳ Day 16: Pattern Enhancement APIs (PLANNED)

---

### Use Case 4: Multi-Model Router Optimization (HIGH VALUE)

**Implement in:** Phase 11 Enhancement  
**Priority:** HIGH  
**Expected Impact:** 10-20% better routing accuracy  

**What It Does:** Uses query→chunk patterns to determine if a query is well-answered by local docs (route to local model) or requires external APIs (route to cloud model).

**Key Integration:** `core/model_router.py` (Phase 11) checks query→chunk patterns before routing. If patterns show high confidence local answer, use local llama3.2. If patterns show low confidence or GitHub API needed, use cloud model.

**Success Criteria:**
- ✅ Router queries patterns before deciding model
- ✅ 10-20% better routing accuracy (measured by user corrections)
- ✅ Faster queries (local model preferred when confident)

---

### Use Case 5: Session Context Persistence (HIGH VALUE)

**Implement in:** Phase 20 Enhancement  
**Priority:** HIGH  
**Expected Impact:** Context loads in <500ms on session resume  

**What It Does:** When user returns to a domain after hours/days, system reloads relevant context using query→chunk and domain→collection patterns.

**Key Integration:** `core/context_manager.py` (Phase 20) saves "context fingerprint" per domain when session ends. On resume, reloads top chunks from patterns.

**Success Criteria:**
- ✅ Context fingerprint saved on session end
- ✅ Context restored on session resume (<500ms)
- ✅ First query after resume has relevant context pre-loaded
- ✅ Feels like "system remembers what we were working on"

---

### Use Case 6: Smart Notification Filtering (MEDIUM VALUE)

**Implement in:** Phase 6 Enhancement  
**Priority:** MEDIUM  
**Expected Impact:** 40-60% fewer irrelevant notifications  

**What It Does:** Filters GitHub/integration notifications using conceptual patterns to surface only topics user cares about.

**Key Integration:** `integrations/github.py` (Phase 6) checks conceptual patterns before surfacing notifications. Only notify if issue/PR topic matches learned concepts.

**Success Criteria:**
- ✅ Conceptual patterns queried for notification filtering
- ✅ 40-60% fewer irrelevant notifications
- ✅ User can mark notifications as "relevant" to improve patterns

---

### Use Case 7: Intelligent Command Suggestions (MEDIUM VALUE)

**Implement in:** Phase 10 Enhancement  
**Priority:** MEDIUM  
**Expected Impact:** Suggests correct command 70%+ of time  

**What It Does:** Suggests file opens, script runs, commands based on query→chunk patterns and workflow patterns.

**Key Integration:** `integrations/shell_integration.py` (Phase 10) checks patterns after user query. If patterns show query frequently leads to specific file, suggest opening it.

**Success Criteria:**
- ✅ System suggests file opens based on query→chunk patterns
- ✅ System suggests commands based on workflow patterns
- ✅ 70%+ suggestion accuracy (user accepts suggestions)

---

### Use Case 8: Knowledge Gap Detection (MEDIUM VALUE)

**Implement in:** Phase 18 Enhancement  
**Priority:** MEDIUM  
**Expected Impact:** Identifies 3-5 knowledge gaps per month accurately  

**What It Does:** Identifies topics user asks about repeatedly but system answers poorly, suggesting new integrations to add.

**Key Integration:** `ui/autonomy_dashboard.tsx` (Phase 18) displays queries with low avg_score and high retry_count from query→chunk patterns.

**Success Criteria:**
- ✅ Dashboard shows "knowledge gap" queries
- ✅ Suggests specific integrations to add (e.g., "Add Kubernetes docs?")
- ✅ 3-5 accurate gap identifications per month

---

### Use Case 9: Concept-Based Obsidian Linking (LOW-MEDIUM VALUE)

**Implement in:** Phase 12 Enhancement  
**Priority:** LOW-MEDIUM  
**Expected Impact:** Suggests relevant links 60%+ of time  

**What It Does:** Suggests Obsidian note links based on conceptual patterns (which concepts co-occur frequently).

**Key Integration:** `integrations/obsidian.py` (Phase 12) checks conceptual patterns when creating/editing notes. Suggests links to related notes.

**Success Criteria:**
- ✅ System suggests note links when editing
- ✅ Suggestions based on conceptual patterns
- ✅ 60%+ suggestion accuracy (user creates suggested links)

---

## Success Criteria - Phase 13a Complete

### Core Pattern System (Part 1, Days 1-16)

**Functionality:**
- ✅ Query→Chunk patterns boost correct documents (1.8x score boost)
- ✅ Domain→Collection patterns skip irrelevant collections (<20% hit rate)
- ✅ Conceptual patterns expand queries with related terms
- ✅ Only high-quality patterns stored (75%+ useful, confidence ≥0.5)
- ✅ spaCy extracts 10-15 meaningful concepts (not 50+ garbage)
- ✅ Patterns self-prune (old + low-confidence removed automatically)

**Performance:**
- ✅ 30-50% faster RAG for repeated queries (measured with relative metrics)
- ✅ 20-40% faster RAG with domain filtering (measured)
- ✅ Pattern learning overhead < 50ms per query
- ✅ Pattern file size < 10k lines (down from 79k)

**Quality:**
- ✅ 200-400 patterns total (not 3,405)
- ✅ 75%+ patterns have usefulness score > 0.6
- ✅ No garbage patterns like "calm ↔ pick"
- ✅ Concept extraction: 10-15 concepts per conversation
- ✅ Concept pairs: 30-50 valid pairs per conversation

**Metrics & Monitoring:**
- ✅ RAG timing tracked and logged permanently
- ✅ Pattern usefulness scores tracked permanently
- ✅ Can export patterns for analysis (JSON format)
- ✅ Pattern APIs available for other systems

### Ancillary Use Cases (Part 2, Days 17-30)

**Documentation Complete:**
- ✅ Use Case 1: Proactive Context Loading (fully specified)
- ✅ Use Case 2: Domain Auto-Detection Enhancement (fully specified, CRITICAL for Phase 1.5)
- ✅ Use Case 3: Autonomous Workflow Learning (fully specified)
- ✅ Use Cases 4-9: Summaries provided with integration points

**Implementation Readiness:**
- ✅ Each use case has clear "Implement in:" phase assignment
- ✅ Integration points identified (files, methods)
- ✅ Success criteria defined (measurable)
- ✅ No duplicate work (implemented during natural phases)

---

## Files Modified/Created

### New Files Created

1. **PHASE13A_PATTERN_LEARNING_CORE.md** (this document)
   - ~2,900 lines
   - Complete specification for core pattern system + ancillary use cases

2. **~/.polly/patterns.json** (user data, rebuilt)
   - Version 2.0 format
   - 200-400 high-quality patterns
   - ~10k lines (down from 79k)

### Files Modified

**Core Pattern System (Part 1):**

1. **learners/patterns.py** (~445 → ~900 lines, +455 lines)
   - New dataclasses: `QueryChunkPattern`, `DomainPriorityPattern`, `ProjectWorkflowPattern`
   - spaCy-based concept extraction (`_extract_concepts()`)
   - Expanded technical terms whitelist (30 → 500+ terms)
   - Expanded stopwords (40 → 700+ words)
   - Query→chunk learning (`record_successful_chunk()`)
   - Domain→collection learning (`record_collection_performance()`)
   - Pattern quality controls (`_prune_low_quality_patterns()`, decay logic)
   - Pattern usefulness tracking (`record_pattern_usefulness()`)
   - Pattern query APIs (`get_conceptual_patterns_for_concept()`, etc.)
   - Enhanced `load_patterns()` and `save_patterns()` for new types

2. **core/rag.py** (~1,200 → ~1,270 lines, +70 lines)
   - Pattern-based chunk boosting in `search()` method
   - Collection filtering based on domain priorities
   - Adjusted `n_results` per collection based on learned weights

3. **core/polly.py** (~800 → ~880 lines, +80 lines)
   - Record query→chunk patterns after each query
   - Record collection performance after RAG searches
   - Query expansion using conceptual patterns
   - Pattern export APIs (`get_pattern_stats()`, `export_patterns()`)

4. **requirements.txt** (+2 lines)
   - `spacy>=3.7.0`
   - `en-core-web-sm` model URL

**Ancillary Use Cases (Part 2, implemented in later phases):**

5. **core/context_manager.py** (Phase 20, +80 lines)
   - `preload_chunks()` method (Use Case 1)
   - `get_preloaded_context()` method (Use Case 1)
   - Context fingerprint saving (Use Case 5)

6. **integrations/shell_integration.py** (Phase 10, +120 lines)
   - `on_directory_change()` trigger (Use Case 1)
   - `on_command_executed()` observer (Use Case 3)
   - Workflow sequence detection (Use Case 3)
   - Command suggestion logic (Use Case 7)

7. **core/model_router.py** (Phase 11, +40 lines)
   - Pattern-based routing decision (Use Case 4)

8. **integrations/github.py** (Phase 6, +30 lines)
   - Pattern-based notification filtering (Use Case 6)

9. **integrations/obsidian.py** (Phase 12, +30 lines)
   - Pattern-based link suggestions (Use Case 9)

10. **ui/autonomy_dashboard.tsx** (Phase 18, +50 lines)
    - Knowledge gap display (Use Case 8)

---

## Timeline & Implementation Strategy

### Phase 13a Execution: 30 Days Total

**Days 1-16: Core Pattern System (Part 1) - IMPLEMENT**
- ✅ Day 1-2: Cleanup & Foundation (COMPLETE)
- ✅ Day 3-4: Concept Extraction Overhaul (COMPLETE)
- ✅ Day 5-8: Query → Chunk Pattern Learning ⭐ (COMPLETE)
- ✅ Day 9-11: Domain → Collection Priority Learning (COMPLETE) 🎯
- ✅ Day 12-13: Conceptual Pattern Refinement (COMPLETE)
- ✅ Day 14-15: Pattern Quality Controls (COMPLETE)
- ✅ Day 16: Pattern Enhancement APIs (COMPLETE) 🎉

**Days 17-30: Ancillary Use Cases (Part 2) - DOCUMENT ONLY**
- Day 17-18: Use Case 1 specification (Proactive Context Loading)
- Day 19-20: Use Case 2 specification (Domain Auto-Detection) ⭐ CRITICAL
- Day 21-22: Use Case 3 specification (Autonomous Workflows)
- Day 23-24: Use Case 4 specification (Multi-Model Routing)
- Day 25-26: Use Case 5 specification (Session Persistence)
- Day 27-28: Use Cases 6-9 summaries
- Day 29-30: Integration documentation, finalize specs

**Note:** Ancillary use cases (Part 2) are documented during Phase 13a but implemented later during their natural phases. This prevents duplicate work and ensures proper integration.

### Minimum Viable Implementation

If time is constrained, implement in phases:

**Phase 13a MVP (Days 1-13):** 
- Steps 1-5 only (cleanup, extraction, Query→Chunk, Domain→Collection, Conceptual)
- Skip Steps 6-7 (quality controls, APIs)
- Expected impact: 40-60% RAG speedup
- Can be enhanced later

**Phase 13a Full (Days 1-16):**
- All of Part 1
- Expected impact: 50-70% RAG speedup
- Production-ready

**Phase 13a Complete (Days 1-30):**
- Part 1 implemented + Part 2 documented
- Full system ready for integration across all phases

### Dependency Chain

**Phase 13a provides to:**
- Phase 1.5: Domain auto-detection enhancement
- Phase 3: Autonomous workflow learning
- Phase 6: Notification filtering
- Phase 10: Command suggestions
- Phase 11: Multi-model routing optimization
- Phase 12: Obsidian linking suggestions
- Phase 18: Knowledge gap detection
- Phase 20: Proactive context loading + session persistence

**Phase 13a requires:**
- Phase 1.5 (domain keywords for concept validation) - optional, enhances quality
- No hard dependencies - can be implemented standalone

---

## Marketing Alignment

### Core Message: "Knowledge That Compounds"

Phase 13a embodies Polly's core value proposition:

**Other AI systems:**
- Learn patterns, then forget them
- Every query starts from scratch
- No improvement over time
- Dependency scales with usage

**Polly's pattern system:**
- **Remembers** what works (query→chunk, domain→collection patterns)
- **Gets faster** over time (30-70% RAG speedup as patterns compound)
- **Learns your workflows** (build processes, troubleshooting fixes)
- **Improves intelligence** system-wide (domain detection, routing, context loading)
- **Knowledge compounds** - the more you use Polly, the smarter it gets

### Unique Differentiators

1. **Persistent Learning:** Patterns stored permanently, never forgotten
2. **Multi-Layered Intelligence:** One pattern system enhances 9+ features
3. **Self-Improving:** Automatic quality controls, pruning, decay
4. **Measured Impact:** RAG timing and usefulness tracking built-in
5. **Local-First:** All pattern learning happens locally, private knowledge stays private

### User Benefits

- Faster over time (not slower like other systems)
- Remembers project-specific workflows (never asks "how to build" twice)
- Smarter domain detection (fewer manual corrections)
- Better answers (learns which docs actually help)
- Privacy-preserving (patterns stored locally, never sent to cloud)

---

## Next Steps

### After Phase 13a Core Complete (Day 16)

1. **Test & Validate:** Run comprehensive tests on pattern quality and RAG speedup
2. **Measure Baseline:** Record current RAG performance before patterns activate
3. **Use Daily:** Use Polly normally for 2-4 weeks to build pattern corpus
4. **Measure Impact:** Re-test RAG performance with patterns active
5. **Document Results:** Record actual speedup achieved (target: 50-70%)

### Integrating Ancillary Use Cases

As you implement other phases, refer back to Part 2 specifications:

- **Phase 1.5:** Implement Use Case 2 (domain auto-detection)
- **Phase 3:** Implement Use Case 3 (workflow learning)
- **Phase 6:** Implement Use Case 6 (notification filtering)
- **Phase 10:** Implement Use Cases 1 & 7 (context loading, command suggestions)
- **Phase 11:** Implement Use Case 4 (multi-model routing)
- **Phase 12:** Implement Use Case 9 (Obsidian linking)
- **Phase 18:** Implement Use Case 8 (knowledge gap detection)
- **Phase 20:** Implement Use Cases 1 & 5 (proactive loading, session persistence)

### Phase 13b: UI & Testing

After Phase 13a documentation is complete, proceed to Phase 13b for:
- Pattern visualization UI
- Pattern management interface
- Learning frequency controls
- End-to-end testing
- User acceptance testing

---

**End of PHASE13A_PATTERN_LEARNING_CORE.md**


**IMPLEMENTATION NOTE:** This section contains full specifications for 9 ancillary use cases that leverage the core pattern system. These use cases are documented here but **implemented in their natural phases** to avoid duplicate work.

**Why This Approach:**
- Prevents duplicate work (e.g., implementing routing in Phase 13a, then re-doing it in Phase 11)
- Each use case integrates naturally when its parent phase is implemented
- Full specifications here ensure consistency and completeness
- Pattern system (Part 1) must be complete before any ancillary use case

**Implementation Timeline:**
- Days 17-30 of Phase 13a: **Documentation only** (write detailed specs)
- Later phases: **Implementation** (execute according to specs below)

---

### Use Case 1: Proactive Context Loading (HIGH VALUE)

**Implement in:** Phase 20 (Context Window Management)  
**Priority:** HIGH  
**Expected Impact:** 50-80% latency reduction on first query per domain  

---

#### What It Does

Pre-loads relevant context before the user even asks a question, based on learned query→chunk patterns.

**Example Scenario:**
1. User switches to signals domain (opens a norns project folder)
2. System detects domain change
3. Query→chunk patterns show top 10 chunks frequently accessed for signals queries
4. System pre-warms the context cache with those chunks
5. User asks: "How do I use the engine library?"
6. Response is instant (context already loaded)

---

#### Integration Points

**Dependencies:**
- Phase 13a Part 1 (query→chunk patterns must exist)
- Phase 10 (shell integration for detecting directory changes)
- Phase 20 (context management system)

**Files to Modify:**
- `core/context_manager.py` (Phase 20 file, to be created)
- `integrations/shell_integration.py` (Phase 10 file)
- `core/polly.py` (add proactive loading trigger)

---

#### Implementation Specification

**Step 1: Detect Domain Changes**

`integrations/shell_integration.py`:
```python
class ShellIntegration:
    async def on_directory_change(self, new_dir: str):
        """Called when user changes directory."""
        # Detect domain from directory path
        domain = await self._detect_domain_from_path(new_dir)
        
        if domain and domain != self.current_domain:
            logger.info(f"Domain changed: {self.current_domain} → {domain}")
            self.current_domain = domain
            
            # Trigger proactive context loading
            await self.polly.preload_context_for_domain(domain)
```

**Step 2: Pre-load Context Using Patterns**

`core/polly.py`:
```python
async def preload_context_for_domain(self, domain: str):
    """
    Pre-load frequently-accessed chunks for a domain based on learned patterns.
    
    Uses query→chunk patterns to identify which chunks are commonly needed
    for this domain, then loads them into context cache.
    """
    if not self.pattern_learner or not self.context_manager:
        return
    
    logger.info(f"Pre-loading context for domain: {domain}")
    
    # Get all query→chunk patterns
    chunks_to_load = set()
    
    for pattern in self.pattern_learner.query_chunk_patterns.values():
        # Get top 3 chunks from each pattern (only high-confidence)
        for chunk_stat in pattern.successful_chunks[:3]:
            if chunk_stat['hit_count'] >= 5 and chunk_stat['avg_score'] >= 0.75:
                chunks_to_load.add(chunk_stat['chunk_id'])
    
    if not chunks_to_load:
        logger.info(f"No high-confidence chunks found for domain {domain}")
        return
    
    # Limit to top 10 chunks (don't overload cache)
    chunk_list = list(chunks_to_load)[:10]
    
    # Load chunks from RAG collections
    loaded_chunks = []
    for chunk_id in chunk_list:
        chunk = await self.rag.get_chunk_by_id(chunk_id)
        if chunk:
            loaded_chunks.append(chunk)
    
    # Pre-warm context cache
    await self.context_manager.preload_chunks(loaded_chunks, domain=domain)
    
    logger.info(f"Pre-loaded {len(loaded_chunks)} chunks for domain {domain}")
```

**Step 3: Context Manager Support**

`core/context_manager.py` (Phase 20):
```python
class ContextManager:
    async def preload_chunks(self, chunks: List[Chunk], domain: str):
        """
        Pre-load chunks into context cache.
        
        These chunks will be immediately available for the next query,
        skipping RAG search time.
        """
        cache_key = f"preloaded_{domain}"
        
        self.context_cache[cache_key] = {
            'chunks': chunks,
            'loaded_at': datetime.now(),
            'domain': domain
        }
        
        logger.info(f"Pre-loaded {len(chunks)} chunks into cache for domain {domain}")
    
    async def get_preloaded_context(self, domain: str) -> List[Chunk]:
        """Get pre-loaded chunks for a domain (if any)."""
        cache_key = f"preloaded_{domain}"
        
        if cache_key in self.context_cache:
            cached = self.context_cache[cache_key]
            
            # Check if cache is still fresh (< 10 minutes old)
            age = (datetime.now() - cached['loaded_at']).total_seconds()
            if age < 600:  # 10 minutes
                logger.info(f"Using pre-loaded context for domain {domain} ({len(cached['chunks'])} chunks)")
                return cached['chunks']
        
        return []
```

---

#### Success Criteria

- ✅ Domain changes detected (directory change, project open)
- ✅ Query→chunk patterns queried correctly
- ✅ Top 10 high-confidence chunks pre-loaded
- ✅ First query after domain change uses pre-loaded chunks
- ✅ Measured latency reduction: 50-80% faster first query
- ✅ Cache expires after 10 minutes (prevents stale data)

---

### Use Case 2: Domain Auto-Detection Enhancement (HIGH VALUE) ⭐ CRITICAL

**Implement in:** Phase 1.5 Enhancement  
**Priority:** CRITICAL (Phase 1.5 already planned)  
**Expected Impact:** 15-25% higher confidence scores, 20-30% fewer user prompts  

---

#### What It Does

Enhances Phase 1.5's domain detection by using learned domain→collection patterns and conceptual patterns.

**Example Scenario:**
1. User creates Obsidian note with content: "Grid controls for sequencing"
2. Phase 1.5 (current): Analyzes keywords, finds "grid" → uncertain (could be general UI or signals)
3. Phase 1.5 (enhanced): Checks patterns → "grid" frequently appears in "signals" domain queries with integration_github_norns collection
4. Boosts "signals" domain confidence from 0.65 → 0.85
5. Auto-files note to signals domain (no user prompt needed)

---

#### Current Phase 1.5 Implementation

**File:** See `PHASE1.5_DOMAIN_CONFIGURATION.md` (1,414 lines)  
**Status:** Planning (Tier 1, high priority)  
**Duration:** 6 days base implementation  

**Existing Auto-Tagging Logic** (lines 62-67, 241-264):
```typescript
async function autoFileNote(note: Note, userContext: UserContext): Promise<string> {
  // 1. Check for explicit domain hints
  // 2. Analyze content keywords (static keyword matching)
  // 3. Check contextual signals
  // 4. If confident (>0.7), auto-file; otherwise, ask user
}
```

---

#### Pattern Enhancement Specification

**Integration Point:** `core/polly.py` domain detection logic (lines 200-250)

**Enhanced Domain Detection:**

```python
async def _detect_domains(
    self,
    query: str,
    context: Optional[Dict] = None
) -> List[str]:
    """
    Detect domains with pattern-based confidence boosting.
    
    Enhancement: Use learned patterns to improve detection accuracy.
    """
    # Step 1: Existing keyword-based detection
    domain_scores = await self._analyze_keywords(query)
    # Returns: {'signals': 0.65, 'sigils': 0.30, 'sanctuary': 0.05}
    
    # Step 2: NEW - Boost scores using domain→collection patterns
    if self.pattern_learner:
        pattern_scores = self._get_pattern_domain_scores(query)
        
        # Combine scores with pattern boost
        for domain, pattern_score in pattern_scores.items():
            if domain in domain_scores:
                # Boost existing score by up to 25%
                boost = min(pattern_score * 0.25, 0.25)
                domain_scores[domain] += boost
                logger.debug(f"Pattern boosted {domain}: +{boost:.2f}")
    
    # Step 3: NEW - Use conceptual patterns for related term expansion
    if self.pattern_learner:
        expanded_terms = self._expand_query_terms_for_domain_detection(query)
        if expanded_terms:
            # Re-analyze with expanded terms
            expanded_scores = await self._analyze_keywords(f"{query} {' '.join(expanded_terms)}")
            
            # Merge scores (take max of original vs expanded)
            for domain, score in expanded_scores.items():
                domain_scores[domain] = max(domain_scores.get(domain, 0), score)
    
    # Step 4: Return domains above threshold (existing logic)
    confident_domains = [d for d, score in domain_scores.items() if score > 0.7]
    
    return confident_domains if confident_domains else [max(domain_scores, key=domain_scores.get)]

def _get_pattern_domain_scores(self, query: str) -> Dict[str, float]:
    """
    Get domain confidence scores based on learned patterns.
    
    Uses domain→collection patterns to determine which domains
    are most likely based on historical query patterns.
    """
    scores = {}
    
    # Extract concepts from query
    concepts = set(query.lower().split())
    
    # Check each domain's collection patterns
    for domain_pattern in self.pattern_learner.domain_priority_patterns.values():
        domain = domain_pattern.domain
        
        # Calculate relevance score based on:
        # 1. How many query concepts appear in high-weight collections for this domain
        # 2. Overall collection hit rates for this domain
        
        avg_weight = sum(domain_pattern.collection_weights.values()) / len(domain_pattern.collection_weights)
        
        # Normalize to 0-1 range
        score = min(avg_weight / 2.0, 1.0)
        scores[domain] = score
    
    return scores

def _expand_query_terms_for_domain_detection(self, query: str) -> List[str]:
    """
    Expand query terms using conceptual patterns for better domain detection.
    
    Example: "grid" → also consider "norns", "monome" (from learned patterns)
    """
    query_concepts = set(query.lower().split())
    expanded_terms = []
    
    for concept in query_concepts:
        # Find conceptual patterns for this concept
        related_patterns = self.pattern_learner.get_conceptual_patterns_for_concept(concept)
        
        # Add related concepts (top 2 only)
        for pattern in related_patterns[:2]:
            concept1 = pattern.metadata.get('concept1')
            concept2 = pattern.metadata.get('concept2')
            
            related = concept2 if concept1 == concept else concept1
            if related and related not in query_concepts:
                expanded_terms.append(related)
    
    return expanded_terms[:3]  # Limit to 3 expanded terms
```

---

#### Record Successful Domain Detections

```python
# In core/polly.py, after domain detection succeeds
if self.pattern_learner and detected_domains:
    # If user doesn't correct the domain, it was successful
    self.pattern_learner.record_successful_domain_detection(
        query=query,
        detected_domain=detected_domains[0],
        confidence=domain_scores[detected_domains[0]]
    )
```

---

#### Success Criteria

- ✅ Pattern-based domain score boosting working
- ✅ Query term expansion using conceptual patterns
- ✅ 15-25% higher domain confidence scores (measured)
- ✅ 20-30% fewer "ask user" prompts (measured)
- ✅ Records successful detections for future learning
- ✅ Integration with Phase 1.5 auto-filing logic
- ✅ Test: "grid controls" query → "signals" domain confidence 0.85+ (vs 0.65 baseline)

---

### Use Case 3: Autonomous Task Execution - Learned Workflows (HIGH VALUE) ⭐ NEW

**Implement in:** Phase 3 Enhancement  
**Priority:** HIGH  
**Expected Impact:** 80%+ troubleshooting success rate, never "forgets" project workflows  

---

#### What It Does

Learns project-specific build/deploy/test workflows and common failure patterns, so Polly remembers how to work with each project.

**Example Scenario:**
1. User works on `~/bees` firmware project (norns hardware)
2. User manually builds 5 times: `colima start && cd ~/bees && docker build -t bees-build . && make firmware`
3. System learns this as a ProjectWorkflowPattern
4. Next time user says: "Build the bees firmware"
5. System immediately knows the exact command sequence
6. If Docker fails ("Cannot connect to daemon"), system knows to run `colima start` first

---

#### Pattern Storage

**Pattern Type:** `ProjectWorkflowPattern` (already added in Step 1.2)

```python
@dataclass
class ProjectWorkflowPattern:
    pattern_id: str
    project_path: str  # ~/bees
    domain: str  # signals
    workflow_type: str  # 'build', 'deploy', 'test', 'run'
    command_sequence: List[Dict]  # [{step, command, description}]
    prerequisites: List[str]  # ["colima running", "env vars set"]
    common_failures: List[Dict]  # [{error_pattern, fix, success_count}]
    learned_from: int  # Number of successful executions observed
    last_success: datetime
    confidence: float
```

**Example Pattern:**
```json
{
  "pattern_type": "project_workflow",
  "pattern_id": "workflow_bees_build",
  "project_path": "/Users/brett/bees",
  "domain": "signals",
  "workflow_type": "build_firmware",
  "command_sequence": [
    {"step": 1, "command": "colima start", "description": "Start Docker environment"},
    {"step": 2, "command": "cd /Users/brett/bees", "description": "Navigate to project"},
    {"step": 3, "command": "docker build -t bees-build .", "description": "Build Docker image"},
    {"step": 4, "command": "make firmware", "description": "Compile firmware"}
  ],
  "prerequisites": ["colima running", "Docker installed"],
  "common_failures": [
    {
      "error_pattern": "Cannot connect to Docker daemon",
      "fix": "Run: colima start",
      "success_count": 5
    },
    {
      "error_pattern": "make: *** No rule to make target",
      "fix": "Run: git submodule update --init --recursive",
      "success_count": 2
    }
  ],
  "learned_from": 12,
  "last_success": "2026-01-24T10:30:00Z",
  "confidence": 0.92
}
```

---

#### Integration Points

**Dependencies:**
- Phase 13a Part 1 (ProjectWorkflowPattern storage)
- Phase 3 (Autonomous Task Execution)
- Phase 10 (Shell Integration for observing command sequences)

**Files to Modify:**
- `learners/patterns.py` (add workflow learning methods)
- `core/task_executor.py` (Phase 3 file)
- `integrations/shell_integration.py` (Phase 10 file, observe commands)

---

#### Implementation Specification

**Step 1: Observe Successful Command Sequences**

`integrations/shell_integration.py`:
```python
class ShellIntegration:
    def __init__(self):
        self.recent_commands = []  # Track last 10 commands
        self.command_outcomes = {}  # Track success/failure
    
    async def on_command_executed(self, command: str, exit_code: int, output: str):
        """Called after every shell command execution."""
        self.recent_commands.append({
            'command': command,
            'exit_code': exit_code,
            'output': output,
            'timestamp': datetime.now(),
            'cwd': os.getcwd()
        })
        
        # Keep only last 10 commands
        self.recent_commands = self.recent_commands[-10:]
        
        # If command sequence looks like a build/deploy workflow, learn it
        if self._looks_like_workflow_sequence(self.recent_commands[-5:]):
            await self._learn_workflow_pattern(self.recent_commands[-5:])
    
    def _looks_like_workflow_sequence(self, commands: List[Dict]) -> bool:
        """
        Detect if command sequence is a repeatable workflow.
        
        Heuristics:
        - Multiple commands in same directory
        - Commands include build/deploy/test keywords
        - All commands succeeded
        - Sequence repeated 3+ times
        """
        if len(commands) < 2:
            return False
        
        # All succeeded
        if not all(cmd['exit_code'] == 0 for cmd in commands):
            return False
        
        # Same directory
        if len(set(cmd['cwd'] for cmd in commands)) > 1:
            return False
        
        # Contains workflow keywords
        workflow_keywords = ['build', 'make', 'deploy', 'test', 'docker', 'npm', 'cargo', 'pytest']
        command_text = ' '.join(cmd['command'] for cmd in commands).lower()
        if not any(kw in command_text for kw in workflow_keywords):
            return False
        
        return True
    
    async def _learn_workflow_pattern(self, commands: List[Dict]):
        """Learn a workflow pattern from observed command sequence."""
        project_path = commands[0]['cwd']
        
        # Detect workflow type
        command_text = ' '.join(cmd['command'] for cmd in commands).lower()
        if 'build' in command_text or 'make' in command_text:
            workflow_type = 'build'
        elif 'deploy' in command_text:
            workflow_type = 'deploy'
        elif 'test' in command_text or 'pytest' in command_text:
            workflow_type = 'test'
        else:
            workflow_type = 'run'
        
        # Record with pattern learner
        await self.polly.pattern_learner.record_workflow_pattern(
            project_path=project_path,
            workflow_type=workflow_type,
            command_sequence=[
                {
                    'step': i + 1,
                    'command': cmd['command'],
                    'description': self._infer_command_description(cmd['command'])
                }
                for i, cmd in enumerate(commands)
            ]
        )
```

---

#### Success Criteria

- ✅ Shell integration observes command sequences
- ✅ Workflow patterns learned after 3+ successful executions
- ✅ Common failures and fixes recorded
- ✅ Phase 3 autonomous tasks query workflow patterns before executing
- ✅ Test: Build bees firmware 5 times → pattern learned
- ✅ Test: Ask "build bees" → correct command sequence suggested
- ✅ Test: Docker failure → system suggests `colima start` fix
- ✅ 80%+ troubleshooting success rate (fixes common errors autonomously)

---

**Note:** Use Cases 4-9 will be added in subsequent sections to complete Part 2. For now, the 3 highest-priority use cases are fully specified.

---


#### Objectives
- Apply stricter thresholds to conceptual patterns
- Cap at 200 patterns (keep highest quality)
- Use patterns for query expansion

---

#### 5.1: Update Conceptual Pattern Thresholds

**File:** `learners/patterns.py`

**Modify learn_conceptual_patterns() method:**

```python
def learn_conceptual_patterns(self, messages: List[Dict]) -> List[Pattern]:
    """
    Learn conceptual patterns with strict quality controls.
    
    Changes from old implementation:
    - min_occurrences: 3 → 7 (requires stronger evidence)
    - Minimum confidence for storage: 0.5 (was: stored all)
    - Cap at 200 patterns (was: unbounded)
    - Use spaCy-based concept extraction (was: naive capitalization)
    """
    concepts = self._extract_concepts(messages)
    
    if len(concepts) < 2:
        return []
    
    # Generate concept pairs (with quality filter from Step 2)
    concept_pairs = []
    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):
            if self._is_valid_concept_pair(concepts[i], concepts[j]):
                concept_pairs.append((concepts[i], concepts[j]))
    
    if not concept_pairs:
        return []
    
    patterns_learned = []
    
    for concept1, concept2 in concept_pairs:
        pattern_id = f"conceptual_{concept1}_{concept2}"
        
        # Register or update pattern occurrence
        self._register_pattern_occurrence(
            pattern_id=pattern_id,
            pattern_type='conceptual',
            name=f"{concept1} ↔ {concept2}",
            description=f"You frequently explore {concept1} and {concept2} together",
            metadata={'concept1': concept1, 'concept2': concept2},
            min_occurrences=7  # NEW: Increased from 3
        )
        
        # Only return patterns that meet quality threshold
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            if pattern.confidence >= 0.5:  # NEW: Minimum confidence threshold
                patterns_learned.append(pattern)
    
    # NEW: Prune to top 200 conceptual patterns
    self._prune_conceptual_patterns()
    
    return patterns_learned

def _prune_conceptual_patterns(self):
    """Keep only top 200 conceptual patterns by quality."""
    conceptual = [p for p in self.patterns.values() if p.pattern_type == 'conceptual']
    
    if len(conceptual) <= 200:
        return  # Under limit, no pruning needed
    
    # Sort by quality score: confidence × occurrences
    conceptual.sort(key=lambda p: p.confidence * p.occurrences, reverse=True)
    
    # Remove patterns beyond top 200
    for pattern in conceptual[200:]:
        del self.patterns[pattern.id]
        logger.info(f"Pruned low-quality conceptual pattern: {pattern.name} "
                   f"(confidence={pattern.confidence:.2f}, occurrences={pattern.occurrences})")
```

---

#### 5.2: Query Expansion Using Conceptual Patterns

**File:** `core/polly.py`

**Add query expansion before RAG search:**

```python
async def query(
    self,
    query: str,
    conversation_id: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Process a query with pattern-based query expansion.
    """
    # ... existing domain detection ...
    
    # NEW: Expand query using conceptual patterns
    expanded_query = query
    expansion_concepts = []
    
    if self.pattern_learner:
        try:
            # Extract key concepts from query
            query_concepts = set(query.lower().split())
            
            # Find conceptual patterns that match query concepts
            for pattern in self.pattern_learner.patterns.values():
                if pattern.pattern_type != 'conceptual' or pattern.confidence < 0.6:
                    continue
                
                concept1 = pattern.metadata.get('concept1', '').lower()
                concept2 = pattern.metadata.get('concept2', '').lower()
                
                # If either concept is in query, add the other
                if concept1 in query_concepts and concept2 not in query_concepts:
                    expansion_concepts.append(concept2)
                    logger.debug(f"Query expansion: {concept1} → {concept2} (from pattern)")
                    break  # Only expand with one concept
                elif concept2 in query_concepts and concept1 not in query_concepts:
                    expansion_concepts.append(concept1)
                    logger.debug(f"Query expansion: {concept2} → {concept1} (from pattern)")
                    break
            
            if expansion_concepts:
                expanded_query = f"{query} {expansion_concepts[0]}"
                logger.info(f"Expanded query: '{query}' → '{expanded_query}'")
        
        except Exception as e:
            logger.warning(f"Query expansion failed: {e}")
    
    # Perform RAG search with expanded query
    rag_results = await self.rag.search(
        query=expanded_query,  # Use expanded query instead of original
        domains=detected_domains,
        search_n=10
    )
    
    # ... rest of query processing ...
```

---

**Files Modified:**
- `learners/patterns.py` (+40 lines: stricter thresholds, pruning)
- `core/polly.py` (+30 lines: query expansion)

**Completion Criteria:**
- ✅ `min_occurrences` is 7 for conceptual patterns
- ✅ Conceptual patterns capped at 200
- ✅ Patterns with confidence < 0.5 not stored
- ✅ Query expansion working (adds related concepts)
- ✅ Test: "docker" query → expands to "docker python" if pattern exists

---

### Step 6: Pattern Quality Controls (Days 14-15)

#### Objectives
- Automatic pruning of low-quality patterns
- Pattern decay over time
- Pattern usefulness tracking

---

#### 6.1: Automatic Pattern Pruning on Save

**File:** `learners/patterns.py`

**Add _prune_low_quality_patterns() method:**

```python
def _prune_low_quality_patterns(self):
    """
    Automatically prune low-quality patterns before saving.
    
    Pruning rules:
    1. Conceptual patterns: keep top 200 by confidence × occurrences
    2. Old + low confidence: remove if confidence < 0.4 AND not seen in 90 days
    3. Single occurrence + old: remove if occurrences == 1 AND not seen in 30 days
    4. Query→chunk patterns: keep top 100 by total_queries
    5. Domain priority patterns: never prune (always useful)
    """
    now = datetime.now()
    cutoff_90_days = now - timedelta(days=90)
    cutoff_30_days = now - timedelta(days=30)
    
    # 1. Prune conceptual patterns (handled in Step 5)
    self._prune_conceptual_patterns()
    
    # 2. Remove old + low confidence patterns
    to_remove = []
    for pattern_id, pattern in self.patterns.items():
        if pattern.pattern_type not in ['conceptual', 'code']:
            continue
        
        if pattern.last_seen < cutoff_90_days and pattern.confidence < 0.4:
            to_remove.append(pattern_id)
            logger.info(f"Pruning stale pattern: {pattern.name} "
                       f"(last_seen={pattern.last_seen.date()}, confidence={pattern.confidence:.2f})")
    
    for pattern_id in to_remove:
        del self.patterns[pattern_id]
    
    # 3. Remove single occurrence + old patterns
    to_remove = []
    for pattern_id, pattern in self.patterns.items():
        if pattern.pattern_type not in ['conceptual', 'code']:
            continue
        
        if pattern.occurrences == 1 and pattern.first_seen < cutoff_30_days:
            to_remove.append(pattern_id)
            logger.info(f"Pruning one-time pattern: {pattern.name} "
                       f"(first_seen={pattern.first_seen.date()})")
    
    for pattern_id in to_remove:
        del self.patterns[pattern_id]
    
    # 4. Prune query→chunk patterns (keep top 100 by total_queries)
    query_chunk_list = list(self.query_chunk_patterns.values())
    if len(query_chunk_list) > 100:
        query_chunk_list.sort(key=lambda p: p.total_queries, reverse=True)
        
        for pattern in query_chunk_list[100:]:
            del self.query_chunk_patterns[pattern.pattern_id]
            logger.info(f"Pruning low-usage query→chunk pattern: {pattern.query_template} "
                       f"(total_queries={pattern.total_queries})")
    
    logger.info(f"Pruning complete. Patterns remaining: "
               f"{len(self.patterns)} conceptual/code, "
               f"{len(self.query_chunk_patterns)} query→chunk, "
               f"{len(self.domain_priority_patterns)} domain priority")
```

**Update save_patterns() to call pruning:**

```python
def save_patterns(self):
    """Save patterns with automatic pruning."""
    try:
        # Prune before saving
        self._prune_low_quality_patterns()
        
        # ... existing save logic ...
```

---

#### 6.2: Pattern Decay Over Time

**File:** `learners/patterns.py`

**Add decay logic to _register_pattern_occurrence():**

```python
def _register_pattern_occurrence(
    self,
    pattern_id: str,
    pattern_type: str,
    name: str,
    description: str,
    metadata: Dict,
    min_occurrences: int = 3
):
    """Register pattern occurrence with decay for stale patterns."""
    now = datetime.now()
    
    if pattern_id in self.patterns:
        pattern = self.patterns[pattern_id]
        
        # NEW: Apply decay if not seen recently
        days_since = (now - pattern.last_seen).days
        if days_since > 60:
            # 2% decay per day after 60 days of inactivity
            decay = 0.98 ** (days_since - 60)
            old_confidence = pattern.confidence
            pattern.confidence *= decay
            
            if pattern.confidence < old_confidence * 0.9:  # Log significant decay
                logger.debug(f"Applied decay to {pattern.name}: "
                           f"{old_confidence:.2f} → {pattern.confidence:.2f} "
                           f"({days_since} days inactive)")
        
        # Update pattern
        pattern.occurrences += 1
        pattern.last_seen = now
        
        # Recalculate confidence
        pattern.confidence = min(pattern.occurrences / (min_occurrences * 3), 1.0)
    
    else:
        # Create new pattern
        self.patterns[pattern_id] = Pattern(
            id=pattern_id,
            pattern_type=pattern_type,
            name=name,
            description=description,
            metadata=metadata,
            occurrences=1,
            confidence=1.0 / (min_occurrences * 3),
            first_seen=now,
            last_seen=now
        )
```

---

#### 6.3: Pattern Usefulness Tracking

**File:** `learners/patterns.py`

**Add usefulness tracking fields to pattern dataclasses:**

```python
@dataclass
class Pattern:
    # ... existing fields ...
    usefulness_score: float = 0.0  # NEW: Track if pattern actually helps
    times_used: int = 0  # NEW: How many times pattern was applied
    times_helpful: int = 0  # NEW: How many times it improved results
```

**Add method to record usefulness:**

```python
def record_pattern_usefulness(
    self,
    pattern_id: str,
    was_helpful: bool
):
    """
    Record whether a pattern was actually helpful.
    
    This will be called from RAG/query logic when a boosted chunk
    is actually used in the LLM response.
    
    Args:
        pattern_id: ID of the pattern that was applied
        was_helpful: True if the boosted chunk improved the response
    """
    if pattern_id in self.patterns:
        pattern = self.patterns[pattern_id]
    elif pattern_id in self.query_chunk_patterns:
        pattern = self.query_chunk_patterns[pattern_id]
        # For query→chunk patterns, usefulness is implicit (if used, it helped)
        pattern.confidence = min(pattern.confidence * 1.05, 1.0)  # Small boost
        return
    else:
        return
    
    pattern.times_used += 1
    
    if was_helpful:
        pattern.times_helpful += 1
    
    # Update usefulness score
    pattern.usefulness_score = pattern.times_helpful / pattern.times_used
    
    # Boost confidence for useful patterns
    if pattern.usefulness_score > 0.7:
        pattern.confidence = min(pattern.confidence * 1.1, 1.0)
    elif pattern.usefulness_score < 0.3:
        pattern.confidence *= 0.9  # Decay confidence for unhelpful patterns
    
    logger.debug(f"Pattern usefulness: {pattern.name} - "
                f"{pattern.times_helpful}/{pattern.times_used} helpful "
                f"(usefulness={pattern.usefulness_score:.2f})")
```

---

**Files Modified:**
- `learners/patterns.py` (+120 lines: pruning, decay, usefulness tracking)

**Completion Criteria:**
- ✅ Automatic pruning runs before every save
- ✅ Patterns decay after 60 days of inactivity
- ✅ Usefulness tracking fields added
- ✅ `record_pattern_usefulness()` method working
- ✅ Test: Create 250 conceptual patterns → only top 200 saved
- ✅ Test: Pattern unseen for 90 days with confidence 0.3 → pruned

---

### Step 7: Pattern Enhancement APIs (Day 16)

#### Objectives
- Provide clean APIs for other systems to query patterns
- Enable pattern export for analysis
- Support pattern-based features in other phases

---

#### 7.1: Pattern Query APIs

**File:** `learners/patterns.py`

**Add query methods to PatternLearner class:**

```python
def get_conceptual_patterns_for_concept(self, concept: str) -> List[Pattern]:
    """Get all conceptual patterns related to a concept."""
    concept_lower = concept.lower()
    results = []
    
    for pattern in self.patterns.values():
        if pattern.pattern_type != 'conceptual':
            continue
        
        concept1 = pattern.metadata.get('concept1', '').lower()
        concept2 = pattern.metadata.get('concept2', '').lower()
        
        if concept_lower in [concept1, concept2]:
            results.append(pattern)
    
    results.sort(key=lambda p: p.confidence, reverse=True)
    return results

def get_query_chunk_pattern(self, query: str) -> Optional[QueryChunkPattern]:
    """Get query→chunk pattern for a query."""
    template = self._extract_query_template(query)
    query_sig = self._create_query_signature(template)
    pattern_id = f"query_chunk_{query_sig}"
    
    return self.query_chunk_patterns.get(pattern_id)

def get_domain_priorities(self, domain: str) -> Dict[str, float]:
    """Get collection priorities for a domain."""
    pattern_id = f"domain_priority_{domain}"
    
    if pattern_id in self.domain_priority_patterns:
        return self.domain_priority_patterns[pattern_id].collection_weights
    
    return {}

def get_all_patterns_by_confidence(self, min_confidence: float = 0.5) -> List[Pattern]:
    """Get all patterns above a confidence threshold, sorted by confidence."""
    results = [p for p in self.patterns.values() if p.confidence >= min_confidence]
    results.sort(key=lambda p: p.confidence, reverse=True)
    return results

def export_patterns_for_analysis(self) -> Dict:
    """Export all patterns in a format suitable for analysis/visualization."""
    return {
        'conceptual_patterns': [
            {
                'concept1': p.metadata.get('concept1'),
                'concept2': p.metadata.get('concept2'),
                'confidence': p.confidence,
                'occurrences': p.occurrences,
                'usefulness': p.usefulness_score,
                'first_seen': p.first_seen.isoformat(),
                'last_seen': p.last_seen.isoformat()
            }
            for p in self.patterns.values() if p.pattern_type == 'conceptual'
        ],
        'query_chunk_patterns': [
            {
                'query_template': p.query_template,
                'total_queries': p.total_queries,
                'confidence': p.confidence,
                'top_chunks': p.successful_chunks[:5]
            }
            for p in self.query_chunk_patterns.values()
        ],
        'domain_priorities': [
            {
                'domain': p.domain,
                'collection_weights': p.collection_weights,
                'collection_stats': p.collection_stats
            }
            for p in self.domain_priority_patterns.values()
        ],
        'stats': {
            'total_conceptual': len([p for p in self.patterns.values() if p.pattern_type == 'conceptual']),
            'total_query_chunk': len(self.query_chunk_patterns),
            'total_domain_priority': len(self.domain_priority_patterns),
            'avg_confidence': sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0
        }
    }
```

---

#### 7.2: Integration with Polly Core

**File:** `core/polly.py`

**Expose pattern APIs through Polly class:**

```python
class Polly:
    # ... existing code ...
    
    def get_pattern_stats(self) -> Dict:
        """Get pattern learning statistics."""
        if not self.pattern_learner:
            return {}
        
        return self.pattern_learner.export_patterns_for_analysis()['stats']
    
    def get_patterns_for_concept(self, concept: str) -> List[Dict]:
        """Get patterns related to a concept."""
        if not self.pattern_learner:
            return []
        
        patterns = self.pattern_learner.get_conceptual_patterns_for_concept(concept)
        return [
            {
                'concept1': p.metadata.get('concept1'),
                'concept2': p.metadata.get('concept2'),
                'confidence': p.confidence
            }
            for p in patterns
        ]
    
    def export_patterns(self, filepath: Optional[str] = None) -> Dict:
        """Export all patterns for analysis."""
        if not self.pattern_learner:
            return {}
        
        data = self.pattern_learner.export_patterns_for_analysis()
        
        if filepath:
            import json
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Exported patterns to {filepath}")
        
        return data
```

---

**Files Modified:**
- `learners/patterns.py` (+100 lines: query APIs, export methods)
- `core/polly.py` (+30 lines: expose pattern APIs)

**Completion Criteria:**
- ✅ `get_conceptual_patterns_for_concept()` working
- ✅ `get_query_chunk_pattern()` working
- ✅ `get_domain_priorities()` working
- ✅ `export_patterns_for_analysis()` working
- ✅ Polly class exposes pattern APIs
- ✅ Test: Query patterns for "docker" concept → returns related patterns
- ✅ Test: Export to JSON → valid structure

---

## Part 1 Complete: Core Pattern System ✅

**Days 1-16 implementation deliverables:**
- ✅ Cleaned 3,405 garbage patterns
- ✅ Added 3 new pattern types (Query→Chunk, Domain→Collection, ProjectWorkflow)
- ✅ Installed spaCy for accurate concept extraction
- ✅ Implemented Query→Chunk pattern learning (30-50% RAG speedup)
- ✅ Implemented Domain→Collection priority learning (20-40% RAG speedup)
- ✅ Refined conceptual patterns with strict quality controls
- ✅ Added automatic pruning, decay, and usefulness tracking
- ✅ Provided pattern query APIs for other systems

**Next:** Part 2 - Ancillary Use Cases (Days 17-30)

---


#### Objectives
- Learn which collections are most useful per domain
- Skip irrelevant collections to speed up RAG search
- Reduce search time by 20-40% through intelligent filtering

---

#### 4.1: Track Collection Performance Per Domain

**File:** `learners/patterns.py`

**Add new method to PatternLearner class:**

```python
def record_collection_performance(
    self,
    domain: str,
    collection_name: str,
    had_results: bool,
    top_score: float = 0.0
):
    """
    Record whether a collection returned useful results for a domain query.
    
    Args:
        domain: Domain of the query ('signals', 'sigils', 'sanctuary', etc.)
        collection_name: Name of collection ('obsidian', 'codebase', 'integration_github_norns', etc.)
        had_results: Whether this collection returned any results with score >= 0.6
        top_score: Highest score from this collection (0.0 if no results)
    """
    pattern_id = f"domain_priority_{domain}"
    
    now = datetime.now()
    
    if pattern_id not in self.domain_priority_patterns:
        # Create new pattern
        self.domain_priority_patterns[pattern_id] = DomainPriorityPattern(
            pattern_id=pattern_id,
            domain=domain,
            collection_weights={},
            collection_stats={},
            last_updated=now
        )
        logger.info(f"Created new domain→collection pattern for domain: {domain}")
    
    pattern = self.domain_priority_patterns[pattern_id]
    pattern.last_updated = now
    
    # Initialize stats for this collection if not exists
    if collection_name not in pattern.collection_stats:
        pattern.collection_stats[collection_name] = {
            'queries': 0,
            'hits': 0,
            'total_score': 0.0,
            'hit_rate': 0.0
        }
    
    stats = pattern.collection_stats[collection_name]
    stats['queries'] += 1
    
    if had_results and top_score >= 0.6:
        stats['hits'] += 1
        stats['total_score'] += top_score
    
    # Update hit rate
    stats['hit_rate'] = stats['hits'] / stats['queries']
    
    # Update collection weight
    # Formula: hit_rate * (1 + log(queries + 1))
    # This gives higher weight to collections with:
    # 1. High hit rate (primary factor)
    # 2. More queries (confidence factor, but logarithmic so doesn't dominate)
    import math
    confidence_factor = 1 + math.log(stats['queries'] + 1)
    pattern.collection_weights[collection_name] = stats['hit_rate'] * confidence_factor
    
    logger.debug(f"Domain {domain} → {collection_name}: "
                f"hit_rate={stats['hit_rate']:.2f}, "
                f"queries={stats['queries']}, "
                f"weight={pattern.collection_weights[collection_name]:.2f}")
```

---

#### 4.2: Use Priorities to Filter Collections in RAG

**File:** `core/rag.py`

**Modify search() method to use learned priorities:**

```python
async def search(
    self,
    query: str,
    domains: Optional[List[str]] = None,
    search_n: int = 10,
    **kwargs
) -> List[SearchResult]:
    """
    Search across all collections with domain-based filtering.
    """
    # ... existing code to create query_embedding ...
    
    # Determine source types to search
    source_types = kwargs.get('source_types', list(self.collections.keys()))
    
    # NEW: Get collection priorities based on learned domain patterns
    collection_priorities = {}
    
    if self.pattern_learner and domains:
        for domain in domains:
            pattern_id = f"domain_priority_{domain}"
            
            if pattern_id in self.pattern_learner.domain_priority_patterns:
                pattern = self.pattern_learner.domain_priority_patterns[pattern_id]
                
                for coll, weight in pattern.collection_weights.items():
                    # Use highest weight if multiple domains match same collection
                    collection_priorities[coll] = max(
                        collection_priorities.get(coll, 0),
                        weight
                    )
        
        if collection_priorities:
            logger.info(f"Collection priorities for domains {domains}: {collection_priorities}")
    
    # ... existing code ...
    
    all_results = []
    
    for source_type in source_types:
        if source_type not in self.collections:
            continue
        
        # NEW: Skip collections with very low priority (< 0.2) if better options exist
        priority = collection_priorities.get(source_type, 0.5)  # Default 0.5 (unknown)
        
        # If this collection has low priority AND we have high-priority alternatives, skip it
        has_high_priority_alternatives = any(p > 0.7 for p in collection_priorities.values())
        if priority < 0.2 and has_high_priority_alternatives:
            logger.info(f"Skipping {source_type} (low priority {priority:.2f}, have better alternatives)")
            continue
        
        # NEW: Adjust n_results based on priority
        # High priority (> 0.7) → get more results (up to 2x)
        # Low priority (< 0.4) → get fewer results (down to 0.5x)
        priority_multiplier = 0.5 + (priority * 1.5)  # Range: 0.5x to 2.0x
        adjusted_n = max(1, int(search_n * priority_multiplier))
        
        logger.debug(f"Searching {source_type} with adjusted_n={adjusted_n} (priority={priority:.2f})")
        
        # Search collection with adjusted n_results
        results = await self.collections[source_type].query(
            query_embeddings=[query_embedding],
            n_results=adjusted_n,
            where=where_filter if where_filter else None
        )
        
        # ... rest of existing result processing ...
    
    return all_results[:search_n]
```

---

#### 4.3: Trigger Learning After RAG Search

**File:** `core/polly.py`

**Modify query() method to record collection performance:**

```python
async def query(
    self,
    query: str,
    conversation_id: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Process a query with domain→collection pattern learning.
    """
    # ... existing domain detection code (around line 200-250) ...
    
    detected_domains = await self._detect_domains(query)
    
    # ... existing RAG search code ...
    
    rag_results = await self.rag.search(
        query=query,
        domains=detected_domains,
        search_n=10
    )
    
    # NEW: Record collection performance for each domain
    if self.pattern_learner and detected_domains:
        try:
            # Group results by collection
            collection_results = {}
            for result in rag_results[:10]:
                coll = result.chunk.source_type
                if coll not in collection_results:
                    collection_results[coll] = []
                collection_results[coll].append(result.score)
            
            # Get all possible collections (including ones with 0 results)
            all_collections = list(self.rag.collections.keys())
            
            # Record performance for each domain
            for domain in detected_domains:
                domain_val = domain.value if hasattr(domain, 'value') else str(domain)
                
                for collection_name in all_collections:
                    had_results = collection_name in collection_results
                    top_score = max(collection_results[collection_name]) if had_results else 0.0
                    
                    self.pattern_learner.record_collection_performance(
                        domain=domain_val,
                        collection_name=collection_name,
                        had_results=had_results and top_score >= 0.6,
                        top_score=top_score
                    )
            
            # Save patterns periodically
            if self._query_count % 10 == 0:
                self.pattern_learner.save_patterns()
        
        except Exception as e:
            logger.warning(f"Failed to record collection performance: {e}")
    
    # ... rest of query processing ...
```

---

#### 4.4: Testing & Validation

**Test Scenario 1: Learn collection priorities**

```python
# Test: Ask 20 signals domain questions
signals_queries = [
    "How do I use the norns engine library?",
    "What is the grid in monome?",
    "norns script structure",
    "SuperCollider DSP basics",
    # ... 16 more signals queries
]

for query in signals_queries:
    await polly.query(query)

# Check learned priorities
import json
with open(os.path.expanduser('~/.polly/patterns.json'), 'r') as f:
    patterns = json.load(f)

domain_pattern = patterns['patterns']['domain_priority_signals']
print("Collection priorities for 'signals' domain:")
for coll, weight in sorted(domain_pattern['collection_weights'].items(), key=lambda x: x[1], reverse=True):
    stats = domain_pattern['collection_stats'][coll]
    print(f"  {coll}: weight={weight:.2f}, hit_rate={stats['hit_rate']:.2f}, queries={stats['queries']}")

# Expected output:
# integration_github_norns: weight=1.2, hit_rate=0.85, queries=20
# obsidian: weight=0.9, hit_rate=0.65, queries=20
# codebase: weight=0.3, hit_rate=0.15, queries=20
```

**Test Scenario 2: Verify collection skipping**

```python
# After learning, query should skip low-priority collections
result = await polly.query("norns engine patterns")

# Check logs for:
# "Skipping codebase (low priority 0.15, have better alternatives)"

# Verify rag_results don't contain codebase chunks
assert not any(r.chunk.source_type == 'codebase' for r in result['rag_results'])
```

**Test Scenario 3: Measure speedup**

```python
import time

# Baseline: Search all collections
start = time.time()
result1 = await rag.search("norns grid library", domains=['signals'], source_types=['all'])
time_all = time.time() - start

# After learning: Skip irrelevant collections (should skip 'codebase')
start = time.time()
result2 = await rag.search("norns grid library", domains=['signals'])  # Uses learned priorities
time_filtered = time.time() - start

speedup = (time_all - time_filtered) / time_all * 100
print(f"Speedup from collection filtering: {speedup:.1f}%")

# Expected: 20-40% faster (skipping 1-2 collections saves significant time)
```

---

**Files Modified:**
- `learners/patterns.py` (+80 lines: `record_collection_performance()`)
- `core/rag.py` (+40 lines: priority-based collection filtering)
- `core/polly.py` (+30 lines: record collection performance after queries)

**Completion Criteria:**
- ✅ `record_collection_performance()` method working
- ✅ Collection weights calculated correctly (hit_rate × log(queries))
- ✅ RAG search skips low-priority collections
- ✅ RAG adjusts `n_results` based on priority
- ✅ Test: After 20 signals queries, `integration_github_norns` has weight > 1.0, `codebase` < 0.3
- ✅ Test: Signals queries skip codebase collection
- ✅ Test: 20-40% speedup measured

---


**This is the highest-impact feature for RAG efficiency.**

#### Objectives
- Track which chunks successfully answer which query types
- Boost known-good chunks in future similar queries
- Reduce RAG search time by 30-50% for repeated query patterns

---

#### 3.1: Record Successful Chunks After Each Query

**File:** `learners/patterns.py`

**Add new method to PatternLearner class:**

```python
def record_successful_chunk(
    self,
    query: str,
    chunk_id: str,
    filepath: str,
    score: float,
    source_type: str
):
    """
    Record that a specific chunk was relevant for a query.
    Called after RAG search returns results with good scores.
    
    Args:
        query: Original user query
        chunk_id: ID of the relevant chunk
        filepath: Path to the file containing the chunk
        score: Relevance score from RAG (0.0-1.0)
        source_type: Collection type ('obsidian', 'codebase', 'integration_github_norns', etc.)
    """
    # Extract query template and signature
    template = self._extract_query_template(query)
    query_sig = self._create_query_signature(template)
    
    # Find or create pattern
    pattern_id = f"query_chunk_{query_sig}"
    
    now = datetime.now()
    
    if pattern_id not in self.query_chunk_patterns:
        # Create new pattern
        self.query_chunk_patterns[pattern_id] = QueryChunkPattern(
            pattern_id=pattern_id,
            query_template=template,
            query_signature=query_sig,
            successful_chunks=[],
            total_queries=0,
            last_updated=now,
            confidence=0.0
        )
        logger.info(f"Created new query→chunk pattern: {template}")
    
    pattern = self.query_chunk_patterns[pattern_id]
    pattern.total_queries += 1
    pattern.last_updated = now
    
    # Update or add chunk stats
    chunk_found = False
    for chunk_stat in pattern.successful_chunks:
        if chunk_stat['chunk_id'] == chunk_id:
            # Update existing chunk stats
            old_count = chunk_stat['hit_count']
            old_avg = chunk_stat['avg_score']
            
            chunk_stat['hit_count'] += 1
            chunk_stat['avg_score'] = (
                (old_avg * old_count + score) / chunk_stat['hit_count']
            )
            chunk_stat['last_seen'] = now.isoformat()
            
            chunk_found = True
            logger.debug(f"Updated chunk {chunk_id} stats: hits={chunk_stat['hit_count']}, "
                        f"avg_score={chunk_stat['avg_score']:.2f}")
            break
    
    if not chunk_found:
        # Add new chunk to pattern
        pattern.successful_chunks.append({
            'chunk_id': chunk_id,
            'filepath': filepath,
            'source_type': source_type,
            'hit_count': 1,
            'avg_score': score,
            'first_seen': now.isoformat(),
            'last_seen': now.isoformat()
        })
        logger.info(f"Added chunk {chunk_id} ({filepath}) to pattern {template}")
    
    # Keep only top 20 chunks per pattern (by hit_count * avg_score)
    pattern.successful_chunks.sort(
        key=lambda c: c['hit_count'] * c['avg_score'],
        reverse=True
    )
    pattern.successful_chunks = pattern.successful_chunks[:20]
    
    # Update pattern confidence
    # Confidence increases with more queries and higher avg scores
    avg_chunk_score = sum(c['avg_score'] for c in pattern.successful_chunks) / len(pattern.successful_chunks)
    query_factor = min(pattern.total_queries / 10, 1.0)  # Caps at 10 queries
    pattern.confidence = query_factor * avg_chunk_score
    
    logger.debug(f"Pattern {query_sig} now has {len(pattern.successful_chunks)} chunks, "
                f"confidence={pattern.confidence:.2f}")

def _extract_query_template(self, query: str) -> str:
    """
    Extract a generalized template from a specific query.
    
    Examples:
    - "How do I use Docker with Python?" → "how to use X with Y"
    - "What is the norns engine library?" → "what is X"
    - "Debugging TypeScript errors" → "debugging X errors"
    
    Args:
        query: Specific user query
        
    Returns:
        Generalized template string
    """
    query_lower = query.lower().strip('?!')
    
    # Common query patterns
    if query_lower.startswith('how do i') or query_lower.startswith('how to'):
        # "How do I use Docker" → "how to use X"
        words = query_lower.split()
        if 'with' in words:
            return "how to X with Y"
        else:
            return "how to X"
    
    elif query_lower.startswith('what is') or query_lower.startswith("what's"):
        # "What is the norns engine" → "what is X"
        return "what is X"
    
    elif query_lower.startswith('where') or query_lower.startswith('find'):
        # "Where is the config file" → "where is X"
        return "where is X"
    
    elif query_lower.startswith('why'):
        # "Why does Docker fail" → "why does X fail"
        if 'fail' in query_lower or 'error' in query_lower:
            return "why does X fail"
        else:
            return "why X"
    
    elif 'debug' in query_lower or 'fix' in query_lower or 'error' in query_lower:
        # "Debugging TypeScript errors" → "debugging X errors"
        return "debugging X"
    
    elif 'install' in query_lower or 'setup' in query_lower or 'configure' in query_lower:
        # "Install Docker on Mac" → "install X"
        return "install/setup X"
    
    else:
        # Generic: Extract main technical terms
        technical_terms = [t for t in TECHNICAL_TERMS if t.lower() in query_lower]
        if technical_terms:
            return f"query about {technical_terms[0]}"
        else:
            return "general query"

def _create_query_signature(self, template: str) -> str:
    """
    Create a normalized signature for a query template.
    
    Args:
        template: Query template from _extract_query_template()
        
    Returns:
        Normalized signature (lowercase, underscores)
    """
    sig = template.lower().replace(' ', '_').replace('/', '_')
    return sig
```

---

#### 3.2: Boost Known-Good Chunks in RAG Search

**File:** `core/rag.py`

**Modify search() method** (around lines 700-800):

```python
async def search(
    self,
    query: str,
    domains: Optional[List[str]] = None,
    search_n: int = 10,
    **kwargs
) -> List[SearchResult]:
    """
    Search across all collections with pattern-based boosting.
    """
    # ... existing code to create query_embedding ...
    
    # NEW: Check for learned query patterns → get high-value chunk IDs
    boosted_chunk_ids = set()
    matched_pattern = None
    
    if self.pattern_learner:
        from learners.patterns import PatternLearner
        
        # Extract query template
        template = self.pattern_learner._extract_query_template(query)
        query_sig = self.pattern_learner._create_query_signature(template)
        pattern_id = f"query_chunk_{query_sig}"
        
        if pattern_id in self.pattern_learner.query_chunk_patterns:
            pattern = self.pattern_learner.query_chunk_patterns[pattern_id]
            matched_pattern = pattern
            
            # Get top 10 chunks from pattern (minimum 3 hits to be reliable)
            for chunk_stat in pattern.successful_chunks[:10]:
                if chunk_stat['hit_count'] >= 3 and chunk_stat['avg_score'] >= 0.6:
                    boosted_chunk_ids.add(chunk_stat['chunk_id'])
            
            if boosted_chunk_ids:
                logger.info(f"Query pattern match ({template}): boosting {len(boosted_chunk_ids)} known-good chunks")
    
    # ... existing search logic across collections ...
    
    all_results = []
    
    for source_type in source_types:
        if source_type not in self.collections:
            continue
        
        # ... existing collection search code ...
        
        # Search collection
        results = await self.collections[source_type].query(
            query_embeddings=[query_embedding],
            n_results=adjusted_n,
            where=where_filter if where_filter else None
        )
        
        # Convert to SearchResult objects
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            distance = results['distances'][0][i]
            
            # Convert distance to similarity score (0-1)
            score = 1.0 - (distance / 2.0)
            
            # NEW: Boost score if chunk matches learned pattern
            if doc_id in boosted_chunk_ids:
                original_score = score
                score = min(score * 1.8, 1.0)  # 80% boost, cap at 1.0
                logger.debug(f"Boosted chunk {doc_id} from {original_score:.2f} to {score:.2f}")
            
            # ... create SearchResult object ...
            
            result = SearchResult(
                chunk=chunk_obj,
                score=score,
                source_type=source_type,
                retrieval_metadata={
                    'query': query,
                    'embedding_model': self.embedding_model,
                    'original_score': original_score if doc_id in boosted_chunk_ids else score,
                    'pattern_boosted': doc_id in boosted_chunk_ids,
                    'pattern_template': matched_pattern.query_template if matched_pattern else None
                }
            )
            
            all_results.append(result)
    
    # ... existing result sorting and filtering ...
    
    return all_results[:search_n]
```

---

#### 3.3: Trigger Pattern Learning After Each Query

**File:** `core/polly.py`

**Modify query() method** (around lines 400-540):

```python
async def query(
    self,
    query: str,
    conversation_id: Optional[str] = None,
    **kwargs
) -> Dict:
    """
    Process a query with pattern learning integration.
    """
    # ... existing RAG search code (around line 380-500) ...
    
    # Perform RAG search
    rag_results = await self.rag.search(
        query=query,
        domains=detected_domains,
        search_n=10
    )
    
    # NEW: Record query→chunk patterns after RAG completes
    if self.pattern_learner and rag_results:
        try:
            # Record top 3 results as successful chunks (if score >= 0.7)
            for result in rag_results[:3]:
                if result.score >= 0.7:
                    self.pattern_learner.record_successful_chunk(
                        query=query,
                        chunk_id=result.chunk.id,
                        filepath=result.chunk.filepath,
                        score=result.score,
                        source_type=result.chunk.source_type
                    )
            
            # Save patterns after every 5 queries (don't save every single time)
            if not hasattr(self, '_query_count'):
                self._query_count = 0
            self._query_count += 1
            
            if self._query_count % 5 == 0:
                self.pattern_learner.save_patterns()
                logger.debug(f"Saved patterns after {self._query_count} queries")
        
        except Exception as e:
            logger.warning(f"Failed to record query→chunk pattern: {e}")
    
    # ... rest of existing query processing ...
    
    return response
```

---

#### 3.4: Testing & Validation

**Test Scenario 1: Learn from repeated queries**

```python
# Test: Ask the same question 5 times
queries = [
    "How do I use Docker with Python?",
    "How to use Docker in Python project?",
    "Using Docker for Python development",
    "Docker setup for Python app",
    "How do I run Python in Docker?"
]

for query in queries:
    result = await polly.query(query)
    print(f"Query: {query}")
    print(f"Top result: {result['rag_results'][0].chunk.filepath}")
    print(f"Score: {result['rag_results'][0].score}")
    print()

# Expected: After 3-5 queries, the same top document should have boosted score
# First query: score ~0.75
# Fifth query: score ~0.90+ (1.8x boost applied)
```

**Test Scenario 2: Verify pattern storage**

```bash
# Check patterns file
cat ~/.polly/patterns.json | grep "query_chunk" | head -20

# Expected output (after 5 queries):
# {
#   "pattern_type": "query_chunk",
#   "query_template": "how to use X with Y",
#   "successful_chunks": [
#     {
#       "chunk_id": "abc123",
#       "filepath": "docs/docker-python-guide.md",
#       "hit_count": 5,
#       "avg_score": 0.82
#     }
#   ],
#   "total_queries": 5,
#   "confidence": 0.5
# }
```

**Test Scenario 3: Measure speedup**

```python
import time

# Without patterns (first query)
start = time.time()
result1 = await polly.query("How to use Docker with Python?")
time1 = time.time() - start

# Repeat 5 times to learn pattern
for _ in range(5):
    await polly.query("How to use Docker with Python?")

# With patterns (after learning)
start = time.time()
result2 = await polly.query("How to use Docker with Python?")
time2 = time.time() - start

speedup = (time1 - time2) / time1 * 100
print(f"Speedup: {speedup:.1f}%")

# Expected: 30-50% faster (semantic search still runs, but boosted chunks rise to top faster)
```

---

**Files Modified:**
- `learners/patterns.py` (+150 lines: `record_successful_chunk()`, query template extraction)
- `core/rag.py` (+30 lines: pattern-based boosting in `search()`)
- `core/polly.py` (+20 lines: trigger learning after queries)

**Completion Criteria:**
- ✅ `record_successful_chunk()` method working
- ✅ Query templates extracted correctly ("how to X" vs "what is X")
- ✅ RAG search boosts known-good chunks by 1.8x
- ✅ Patterns saved after every 5 queries
- ✅ Test: Repeated queries show 30-50% speedup after 5 iterations
- ✅ Test: Boosted chunks have `pattern_boosted: true` in metadata

---


#### Objectives
- Replace overly aggressive concept extraction with spaCy-based approach
- Expand technical terms whitelist from 30 → 500+ terms
- Add 700+ stopword list
- Implement strict quality filters

---

#### 2.1: Implement spaCy-Based Concept Extraction

**File:** `learners/patterns.py`

**Replace _extract_concepts() method** (current lines 644-711):

```python
import spacy
from typing import List, Set

# Load spaCy model at module level (avoid reloading)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

def _extract_concepts(self, messages: List[Dict]) -> List[str]:
    """
    Extract meaningful concepts from conversation messages using spaCy POS tagging.
    
    Improved approach:
    - Use spaCy for accurate POS tagging
    - Extract only NOUN and PROPN (proper nouns)
    - Filter with expanded stopwords (700+)
    - Validate against technical terms whitelist (500+)
    - Strict quality filters (4+ chars, domain relevance)
    
    Args:
        messages: List of conversation messages
        
    Returns:
        List of high-quality concepts (10-15 concepts vs old 50+)
    """
    if not nlp:
        logger.error("spaCy not available, falling back to basic extraction")
        return self._extract_concepts_fallback(messages)
    
    concepts = set()
    
    # Combine all message content
    text = " ".join([msg.get('content', '') for msg in messages if msg.get('role') != 'system'])
    
    if not text.strip():
        return []
    
    # Process with spaCy
    doc = nlp(text)
    
    # Extract nouns and proper nouns only
    for token in doc:
        # Must be noun or proper noun
        if token.pos_ not in ['NOUN', 'PROPN']:
            continue
        
        # Get lemmatized form (base form)
        concept = token.lemma_.lower()
        
        # Apply quality filters
        if not self._is_valid_concept(concept):
            continue
        
        concepts.add(concept)
    
    # Also extract technical terms that appear in text (case-insensitive)
    text_lower = text.lower()
    for term in TECHNICAL_TERMS:
        if term.lower() in text_lower:
            concepts.add(term.lower())
    
    # Convert to list and limit to top concepts
    concept_list = list(concepts)
    
    # Prioritize domain keywords and technical terms
    concept_list.sort(key=lambda c: (
        c in [t.lower() for t in TECHNICAL_TERMS],  # Technical terms first
        len(c)  # Then by length (longer = more specific)
    ), reverse=True)
    
    # Limit to top 15 concepts
    result = concept_list[:15]
    
    logger.info(f"Extracted {len(result)} concepts from {len(messages)} messages: {result}")
    
    return result

def _is_valid_concept(self, concept: str) -> bool:
    """
    Validate that a concept meets quality standards.
    
    Criteria:
    1. Length: 4+ characters (filters "for", "use", "get")
    2. Not in stopwords (700+ common words)
    3. Either:
       - In technical terms whitelist (500+), OR
       - In domain keywords (from Phase 1.5), OR
       - Passes regex checks (alphanumeric, not all lowercase common word)
    
    Args:
        concept: Candidate concept string
        
    Returns:
        True if concept passes quality filters
    """
    # Must be 4+ characters
    if len(concept) < 4:
        return False
    
    # Must not be in stopwords
    if concept.lower() in EXPANDED_STOPWORDS:
        return False
    
    # Check if in technical terms whitelist
    if concept.lower() in [t.lower() for t in TECHNICAL_TERMS]:
        return True
    
    # Check if in domain keywords (requires Phase 1.5 integration)
    # domain_keywords = self._get_all_domain_keywords()
    # if concept.lower() in domain_keywords:
    #     return True
    
    # Allow if contains numbers or special chars (likely technical: "api2", "ml-ops")
    if any(char.isdigit() for char in concept):
        return True
    if '-' in concept or '_' in concept:
        return True
    
    # Allow if properly capitalized (likely proper noun: "Docker", "Python")
    if concept[0].isupper() and not concept.isupper():
        return True
    
    # Reject common words (even if missed by stopwords)
    common_verbs = {'make', 'take', 'give', 'find', 'think', 'know', 'come', 'work', 
                   'help', 'start', 'stop', 'move', 'live', 'believe', 'bring', 'happen'}
    if concept.lower() in common_verbs:
        return False
    
    return False

def _extract_concepts_fallback(self, messages: List[Dict]) -> List[str]:
    """Fallback concept extraction if spaCy unavailable (basic approach)."""
    concepts = set()
    
    for msg in messages:
        if msg.get('role') == 'system':
            continue
        
        content = msg.get('content', '')
        words = content.split()
        
        for i, word in enumerate(words):
            # Skip first word of sentences (often capitalized but not meaningful)
            if i > 0 and word[0].isupper():
                concept = word.strip('.,!?;:"').lower()
                if self._is_valid_concept(concept):
                    concepts.add(concept)
    
    return list(concepts)[:15]
```

---

#### 2.2: Expanded Technical Terms Whitelist

**File:** `learners/patterns.py`

**Replace TECHNICAL_TERMS list** (current lines 669-680):

```python
# Expanded technical terms whitelist (500+ terms covering all domains)
TECHNICAL_TERMS = {
    # Programming Languages
    'python', 'javascript', 'typescript', 'rust', 'go', 'java', 'kotlin', 'swift',
    'ruby', 'php', 'lua', 'supercollider', 'bash', 'shell', 'sql', 'html', 'css',
    
    # Frameworks & Libraries
    'react', 'vue', 'angular', 'svelte', 'django', 'flask', 'fastapi', 'express',
    'nextjs', 'nuxt', 'electron', 'tauri', 'pytorch', 'tensorflow', 'scikit',
    
    # Tools & Platforms
    'docker', 'kubernetes', 'k8s', 'git', 'github', 'gitlab', 'ollama', 'chromadb',
    'postgresql', 'postgres', 'mysql', 'redis', 'mongodb', 'elasticsearch', 'nginx',
    'apache', 'vscode', 'vim', 'emacs', 'neovim', 'tmux', 'colima',
    
    # AI/ML Terms
    'embedding', 'embeddings', 'vector', 'llm', 'model', 'inference', 'training',
    'tokenization', 'transformer', 'attention', 'rag', 'retrieval', 'semantic',
    
    # Signals Domain (Audio/Synthesis)
    'norns', 'monome', 'grid', 'arc', 'crow', 'midi', 'osc', 'synthesis', 'synth',
    'engine', 'supercollider', 'sc', 'audio', 'dsp', 'modular', 'eurorack', 'cv',
    'sequencer', 'sampler', 'oscillator', 'filter', 'envelope', 'lfo', 'reverb',
    'delay', 'compressor', 'waveshaper', 'granular', 'softcut', 'bees', 'aleph',
    'teletype', 'ansible', 'just-friends', 'mangrove', 'rings', 'plaits', 'ears',
    
    # Pedagogy Domain (Freire, hooks, etc.)
    'pedagogy', 'praxis', 'freire', 'hooks', 'conscientization', 'dialogical',
    'banking-model', 'problem-posing', 'critical-consciousness', 'emancipatory',
    'liberatory', 'oppression', 'hegemony', 'intersectionality', 'solidarity',
    
    # Systems/Architecture
    'architecture', 'microservices', 'monolith', 'serverless', 'lambda', 'api',
    'rest', 'graphql', 'grpc', 'websocket', 'authentication', 'authorization',
    'oauth', 'jwt', 'encryption', 'ssl', 'tls', 'https', 'cors', 'cache', 'cdn',
    
    # Development Concepts
    'refactoring', 'debugging', 'testing', 'unit-test', 'integration-test',
    'e2e-test', 'ci-cd', 'pipeline', 'deployment', 'staging', 'production',
    'environment', 'configuration', 'logging', 'monitoring', 'metrics', 'tracing',
    
    # Data & Storage
    'database', 'schema', 'migration', 'orm', 'query', 'index', 'transaction',
    'acid', 'nosql', 'relational', 'graph-database', 'time-series', 'blob',
    'object-storage', 's3', 'backup', 'replication', 'sharding', 'partitioning',
    
    # File Types & Patterns
    'markdown', 'json', 'yaml', 'toml', 'xml', 'csv', 'parquet', 'readme',
    'config', 'configuration', 'dockerfile', 'makefile', 'package-json',
    
    # Obsidian & Knowledge Management
    'obsidian', 'vault', 'note', 'linking', 'backlink', 'graph', 'canvas',
    'dataview', 'template', 'frontmatter', 'metadata', 'tag', 'folder',
    
    # Polly-Specific
    'polly', 'sigils', 'signals', 'sanctuary', 'integration', 'conversation',
    'pattern', 'domain', 'category', 'collection', 'chunk', 'embedding',
    
    # Common Tech Terms
    'algorithm', 'data-structure', 'optimization', 'performance', 'scalability',
    'latency', 'throughput', 'bottleneck', 'profiling', 'benchmark', 'async',
    'concurrent', 'parallel', 'thread', 'process', 'memory', 'cpu', 'gpu',
    
    # Add more as needed...
}
```

**Note:** This list should be expanded to ~500 terms. The above is ~150 terms as a starting point.

---

#### 2.3: Strict Stopword List (700+ words)

**File:** `learners/patterns.py`

**Add EXPANDED_STOPWORDS set:**

```python
# Expanded stopwords list (700+ common words to filter out)
EXPANDED_STOPWORDS = {
    # Standard English stopwords (articles, pronouns, conjunctions)
    'a', 'an', 'the', 'this', 'that', 'these', 'those', 'is', 'am', 'are', 'was',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'shall',
    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
    'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours',
    'and', 'or', 'but', 'if', 'then', 'else', 'when', 'where', 'why', 'how', 'what',
    'who', 'whom', 'which', 'whose', 'that', 'than', 'as', 'at', 'by', 'for', 'with',
    'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after',
    'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
    'under', 'again', 'further', 'then', 'once', 'here', 'there', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
    
    # Common verbs (non-technical)
    'make', 'made', 'making', 'take', 'took', 'taken', 'taking', 'give', 'gave',
    'given', 'giving', 'find', 'found', 'finding', 'think', 'thought', 'thinking',
    'know', 'knew', 'known', 'knowing', 'come', 'came', 'coming', 'work', 'worked',
    'working', 'help', 'helped', 'helping', 'start', 'started', 'starting', 'stop',
    'stopped', 'stopping', 'move', 'moved', 'moving', 'live', 'lived', 'living',
    'believe', 'believed', 'believing', 'bring', 'brought', 'bringing', 'happen',
    'happened', 'happening', 'seem', 'seemed', 'seeming', 'become', 'became',
    'becoming', 'provide', 'provided', 'providing', 'require', 'required',
    'requiring', 'include', 'included', 'including', 'allow', 'allowed', 'allowing',
    'follow', 'followed', 'following', 'create', 'created', 'creating', 'develop',
    'developed', 'developing', 'build', 'built', 'building', 'grow', 'grew', 'grown',
    'growing', 'learn', 'learned', 'learning', 'teach', 'taught', 'teaching',
    'reach', 'reached', 'reaching', 'spend', 'spent', 'spending', 'pick', 'picked',
    'picking', 'choose', 'chose', 'chosen', 'choosing', 'keep', 'kept', 'keeping',
    'hold', 'held', 'holding', 'turn', 'turned', 'turning', 'put', 'putting',
    'set', 'setting', 'call', 'called', 'calling', 'ask', 'asked', 'asking',
    'need', 'needed', 'needing', 'feel', 'felt', 'feeling', 'try', 'tried', 'trying',
    'leave', 'left', 'leaving', 'tell', 'told', 'telling', 'talk', 'talked', 'talking',
    'sit', 'sat', 'sitting', 'stand', 'stood', 'standing', 'lose', 'lost', 'losing',
    'pay', 'paid', 'paying', 'meet', 'met', 'meeting', 'run', 'ran', 'running',
    'let', 'letting', 'begin', 'began', 'begun', 'beginning', 'show', 'showed',
    'shown', 'showing', 'hear', 'heard', 'hearing', 'play', 'played', 'playing',
    'go', 'went', 'gone', 'going', 'see', 'saw', 'seen', 'seeing', 'get', 'got',
    'gotten', 'getting', 'use', 'used', 'using', 'want', 'wanted', 'wanting',
    
    # Common adjectives
    'good', 'better', 'best', 'bad', 'worse', 'worst', 'big', 'bigger', 'biggest',
    'small', 'smaller', 'smallest', 'large', 'larger', 'largest', 'great', 'greater',
    'greatest', 'little', 'less', 'least', 'high', 'higher', 'highest', 'low',
    'lower', 'lowest', 'long', 'longer', 'longest', 'short', 'shorter', 'shortest',
    'new', 'newer', 'newest', 'old', 'older', 'oldest', 'young', 'younger', 'youngest',
    'different', 'same', 'other', 'another', 'next', 'last', 'first', 'second',
    'third', 'early', 'late', 'right', 'wrong', 'true', 'false', 'sure', 'certain',
    'possible', 'important', 'real', 'clear', 'easy', 'hard', 'simple', 'complex',
    'full', 'empty', 'whole', 'complete', 'open', 'close', 'free', 'available',
    'strong', 'weak', 'heavy', 'light', 'dark', 'bright', 'quiet', 'loud', 'slow',
    'fast', 'quick', 'calm', 'nervous', 'happy', 'sad', 'angry', 'afraid', 'tired',
    
    # Common nouns (non-technical)
    'time', 'year', 'day', 'week', 'month', 'hour', 'minute', 'second', 'moment',
    'person', 'people', 'man', 'woman', 'child', 'kid', 'boy', 'girl', 'friend',
    'family', 'group', 'team', 'company', 'part', 'place', 'area', 'room', 'home',
    'house', 'building', 'city', 'country', 'world', 'state', 'town', 'community',
    'thing', 'stuff', 'item', 'object', 'idea', 'thought', 'way', 'method', 'means',
    'end', 'result', 'effect', 'cause', 'reason', 'purpose', 'goal', 'plan', 'project',
    'work', 'job', 'task', 'problem', 'issue', 'question', 'answer', 'solution',
    'information', 'data', 'fact', 'detail', 'example', 'case', 'point', 'level',
    'type', 'kind', 'sort', 'form', 'shape', 'size', 'number', 'amount', 'value',
    'price', 'cost', 'money', 'power', 'energy', 'force', 'control', 'change',
    'development', 'growth', 'increase', 'decrease', 'difference', 'service',
    'support', 'help', 'attention', 'interest', 'experience', 'feeling', 'sense',
    
    # Words that appeared in garbage patterns
    'social', 'connect', 'together', 'explore', 'using', 'within', 'during',
    'without', 'toward', 'forward', 'back', 'around', 'across', 'inside', 'outside',
    'upon', 'among', 'throughout', 'somehow', 'somewhere', 'something', 'someone',
    'anyone', 'everyone', 'nobody', 'nothing', 'everything', 'anything', 'always',
    'never', 'often', 'sometimes', 'usually', 'generally', 'perhaps', 'maybe',
    'probably', 'definitely', 'certainly', 'absolutely', 'really', 'quite', 'rather',
    'fairly', 'pretty', 'mostly', 'almost', 'nearly', 'hardly', 'barely', 'especially',
    'particularly', 'specifically', 'exactly', 'simply', 'basically', 'essentially',
}
```

**Note:** This list should be expanded to ~700 words. The above is ~350 words as a starting point. Can import from NLTK stopwords corpus:

```python
# Alternative: Use NLTK stopwords (if NLTK is acceptable dependency)
from nltk.corpus import stopwords
EXPANDED_STOPWORDS = set(stopwords.words('english'))
# Then add custom terms like 'calm', 'pick', 'social', etc.
```

---

#### 2.4: Concept Pair Quality Filter

**File:** `learners/patterns.py`

**Add new method to PatternLearner class:**

```python
def _is_valid_concept_pair(self, concept1: str, concept2: str) -> bool:
    """
    Validate that a concept pair is worth learning.
    
    Criteria:
    1. At least ONE must be a technical term or domain keyword
    2. Both must be 4+ characters
    3. Neither can be in stopwords
    4. Can't be too similar (Levenshtein distance check)
    
    Args:
        concept1: First concept
        concept2: Second concept
        
    Returns:
        True if pair passes quality filters
    """
    # Both must be valid concepts individually
    if not self._is_valid_concept(concept1) or not self._is_valid_concept(concept2):
        return False
    
    # Both must be 4+ chars
    if len(concept1) < 4 or len(concept2) < 4:
        return False
    
    # At least ONE must be a technical term or domain keyword
    technical_terms_lower = {t.lower() for t in TECHNICAL_TERMS}
    # domain_keywords = self._get_all_domain_keywords()  # From Phase 1.5
    
    has_technical = (concept1.lower() in technical_terms_lower or 
                    concept2.lower() in technical_terms_lower)
                    # concept1.lower() in domain_keywords or
                    # concept2.lower() in domain_keywords)
    
    if not has_technical:
        logger.debug(f"Rejected pair {concept1} ↔ {concept2}: no technical term")
        return False
    
    # Concepts shouldn't be too similar (avoid "docker" ↔ "dockerization")
    # Simple check: one shouldn't be substring of other
    if concept1.lower() in concept2.lower() or concept2.lower() in concept1.lower():
        logger.debug(f"Rejected pair {concept1} ↔ {concept2}: too similar")
        return False
    
    return True
```

**Update learn_conceptual_patterns() method:**

Modify to use the new quality filter (around line 594):

```python
def learn_conceptual_patterns(self, messages: List[Dict]) -> List[Pattern]:
    """Learn conceptual patterns with strict quality controls."""
    concepts = self._extract_concepts(messages)
    
    if len(concepts) < 2:
        return []
    
    # Generate concept pairs
    concept_pairs = []
    for i in range(len(concepts)):
        for j in range(i + 1, len(concepts)):
            # Apply quality filter
            if self._is_valid_concept_pair(concepts[i], concepts[j]):
                concept_pairs.append((concepts[i], concepts[j]))
    
    logger.info(f"Generated {len(concept_pairs)} valid concept pairs from {len(concepts)} concepts")
    
    if not concept_pairs:
        return []
    
    # Register pattern occurrences
    patterns_learned = []
    for concept1, concept2 in concept_pairs:
        pattern_id = f"conceptual_{concept1}_{concept2}"
        
        # ... rest of existing logic ...
```

---

**Files Modified:**
- `learners/patterns.py` (+300 lines of new extraction logic, stopwords, technical terms)

**Completion Criteria:**
- ✅ spaCy-based extraction working
- ✅ Only NOUN and PROPN extracted
- ✅ 500+ technical terms whitelist in place
- ✅ 700+ stopwords filtering correctly
- ✅ Concept pairs pass quality filter
- ✅ Test: 50 concepts → 10-15 concepts extracted
- ✅ Test: 1,225 pairs → 30-50 valid pairs

---


**IMPLEMENTATION NOTE:** This section contains the core pattern system that will be implemented during Phase 13a execution (Days 1-16). All code here should be written and tested during this phase.

---

### Step 1: Cleanup & Foundation (Days 1-2)

#### Objectives
- Clear existing 3,405 garbage patterns
- Add new pattern type infrastructure
- Install spaCy dependency

#### 1.1: Clear Current Patterns

**Action Items:**
1. Test existing UI pattern clearing mechanism (may already exist in Phase 13 UI)
2. Back up current `~/.polly/patterns.json` to `~/.polly/patterns.json.backup`
3. Clear patterns via UI or by truncating file

**Commands:**
```bash
# Backup current patterns
cp ~/.polly/patterns.json ~/.polly/patterns.json.backup

# Clear patterns (option 1: via UI)
# Navigate to Polly settings → Pattern Learning → "Clear All Patterns"

# Clear patterns (option 2: manual truncation)
echo '{"patterns": {}, "version": "2.0"}' > ~/.polly/patterns.json
```

**Verification:**
- File size should drop from ~79k lines to <10 lines
- Backup should exist at `~/.polly/patterns.json.backup`

---

#### 1.2: Add Pattern Type Infrastructure

**File:** `learners/patterns.py`

**New Dataclasses:**

Add these new pattern types after the existing `Pattern` class (around line 50):

```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional

@dataclass
class QueryChunkPattern:
    """Tracks which chunks successfully answer query types."""
    pattern_id: str
    query_template: str  # e.g., "how to use X with Y"
    query_signature: str  # Simplified template for matching
    successful_chunks: List[Dict]  # [{chunk_id, filepath, hit_count, avg_score, source_type}]
    total_queries: int
    last_updated: datetime
    confidence: float  # Based on total_queries and avg_score
    
    def to_dict(self) -> Dict:
        return {
            'pattern_type': 'query_chunk',
            'pattern_id': self.pattern_id,
            'query_template': self.query_template,
            'query_signature': self.query_signature,
            'successful_chunks': self.successful_chunks,
            'total_queries': self.total_queries,
            'last_updated': self.last_updated.isoformat(),
            'confidence': self.confidence
        }

@dataclass
class DomainPriorityPattern:
    """Tracks which collections/sources work best per domain."""
    pattern_id: str
    domain: str
    collection_weights: Dict[str, float]  # {collection_name: priority_weight}
    collection_stats: Dict[str, Dict]  # {collection_name: {hit_rate, queries, hits, total_score}}
    last_updated: datetime
    
    def to_dict(self) -> Dict:
        return {
            'pattern_type': 'domain_priority',
            'pattern_id': self.pattern_id,
            'domain': self.domain,
            'collection_weights': self.collection_weights,
            'collection_stats': self.collection_stats,
            'last_updated': self.last_updated.isoformat()
        }

@dataclass
class ProjectWorkflowPattern:
    """Tracks project-specific build/deploy/test workflows."""
    pattern_id: str
    project_path: str
    domain: str
    workflow_type: str  # 'build', 'deploy', 'test', 'run'
    command_sequence: List[Dict]  # [{step, command, description}]
    prerequisites: List[str]  # ["docker running", "env vars set"]
    common_failures: List[Dict]  # [{error_pattern, fix, success_count}]
    learned_from: int  # Number of successful executions observed
    last_success: datetime
    confidence: float
    
    def to_dict(self) -> Dict:
        return {
            'pattern_type': 'project_workflow',
            'pattern_id': self.pattern_id,
            'project_path': self.project_path,
            'domain': self.domain,
            'workflow_type': self.workflow_type,
            'command_sequence': self.command_sequence,
            'prerequisites': self.prerequisites,
            'common_failures': self.common_failures,
            'learned_from': self.learned_from,
            'last_success': self.last_success.isoformat(),
            'confidence': self.confidence
        }
```

**Update PatternLearner class:**

Add these instance variables to `__init__` (around line 70):

```python
def __init__(self, storage_path: Optional[str] = None):
    # ... existing code ...
    
    # New pattern storage
    self.query_chunk_patterns: Dict[str, QueryChunkPattern] = {}
    self.domain_priority_patterns: Dict[str, DomainPriorityPattern] = {}
    self.project_workflow_patterns: Dict[str, ProjectWorkflowPattern] = {}
```

**Update load_patterns() method:**

Modify to load all pattern types (around line 120):

```python
def load_patterns(self):
    """Load patterns from storage, including new pattern types."""
    try:
        if not os.path.exists(self.storage_path):
            logger.info("No patterns file found, starting fresh")
            return
        
        with open(self.storage_path, 'r') as f:
            data = json.load(f)
        
        # Load existing conceptual/code patterns
        for pattern_id, pattern_data in data.get('patterns', {}).items():
            pattern_type = pattern_data.get('pattern_type', 'conceptual')
            
            if pattern_type in ['conceptual', 'code', 'query', 'workflow']:
                # Existing pattern types
                self.patterns[pattern_id] = Pattern(
                    id=pattern_id,
                    pattern_type=pattern_type,
                    name=pattern_data.get('name', ''),
                    description=pattern_data.get('description', ''),
                    metadata=pattern_data.get('metadata', {}),
                    occurrences=pattern_data.get('occurrences', 0),
                    confidence=pattern_data.get('confidence', 0.0),
                    first_seen=datetime.fromisoformat(pattern_data.get('first_seen')),
                    last_seen=datetime.fromisoformat(pattern_data.get('last_seen'))
                )
            elif pattern_type == 'query_chunk':
                # New query→chunk patterns
                self.query_chunk_patterns[pattern_id] = QueryChunkPattern(
                    pattern_id=pattern_id,
                    query_template=pattern_data.get('query_template', ''),
                    query_signature=pattern_data.get('query_signature', ''),
                    successful_chunks=pattern_data.get('successful_chunks', []),
                    total_queries=pattern_data.get('total_queries', 0),
                    last_updated=datetime.fromisoformat(pattern_data.get('last_updated')),
                    confidence=pattern_data.get('confidence', 0.0)
                )
            elif pattern_type == 'domain_priority':
                # New domain→collection patterns
                self.domain_priority_patterns[pattern_id] = DomainPriorityPattern(
                    pattern_id=pattern_id,
                    domain=pattern_data.get('domain', ''),
                    collection_weights=pattern_data.get('collection_weights', {}),
                    collection_stats=pattern_data.get('collection_stats', {}),
                    last_updated=datetime.fromisoformat(pattern_data.get('last_updated'))
                )
            elif pattern_type == 'project_workflow':
                # New workflow patterns
                self.project_workflow_patterns[pattern_id] = ProjectWorkflowPattern(
                    pattern_id=pattern_id,
                    project_path=pattern_data.get('project_path', ''),
                    domain=pattern_data.get('domain', ''),
                    workflow_type=pattern_data.get('workflow_type', ''),
                    command_sequence=pattern_data.get('command_sequence', []),
                    prerequisites=pattern_data.get('prerequisites', []),
                    common_failures=pattern_data.get('common_failures', []),
                    learned_from=pattern_data.get('learned_from', 0),
                    last_success=datetime.fromisoformat(pattern_data.get('last_success')),
                    confidence=pattern_data.get('confidence', 0.0)
                )
        
        logger.info(f"Loaded {len(self.patterns)} conceptual/code patterns, "
                   f"{len(self.query_chunk_patterns)} query→chunk patterns, "
                   f"{len(self.domain_priority_patterns)} domain priority patterns, "
                   f"{len(self.project_workflow_patterns)} workflow patterns")
        
    except Exception as e:
        logger.error(f"Error loading patterns: {e}")
```

**Update save_patterns() method:**

Modify to save all pattern types (around line 180):

```python
def save_patterns(self):
    """Save all pattern types to storage with automatic pruning."""
    try:
        # Prune before saving (see Step 6 for pruning logic)
        self._prune_low_quality_patterns()
        
        # Prepare data structure
        data = {
            'version': '2.0',
            'patterns': {},
            'last_updated': datetime.now().isoformat()
        }
        
        # Save existing conceptual/code patterns
        for pattern_id, pattern in self.patterns.items():
            data['patterns'][pattern_id] = {
                'pattern_type': pattern.pattern_type,
                'name': pattern.name,
                'description': pattern.description,
                'metadata': pattern.metadata,
                'occurrences': pattern.occurrences,
                'confidence': pattern.confidence,
                'first_seen': pattern.first_seen.isoformat(),
                'last_seen': pattern.last_seen.isoformat()
            }
        
        # Save query→chunk patterns
        for pattern_id, pattern in self.query_chunk_patterns.items():
            data['patterns'][pattern_id] = pattern.to_dict()
        
        # Save domain→collection patterns
        for pattern_id, pattern in self.domain_priority_patterns.items():
            data['patterns'][pattern_id] = pattern.to_dict()
        
        # Save workflow patterns
        for pattern_id, pattern in self.project_workflow_patterns.items():
            data['patterns'][pattern_id] = pattern.to_dict()
        
        # Write to file
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        total_patterns = (len(self.patterns) + 
                         len(self.query_chunk_patterns) + 
                         len(self.domain_priority_patterns) +
                         len(self.project_workflow_patterns))
        
        logger.info(f"Saved {total_patterns} patterns to {self.storage_path}")
        
    except Exception as e:
        logger.error(f"Error saving patterns: {e}")
```

**Verification:**
- Run pattern learner initialization
- Check that new pattern types are recognized
- Verify `patterns.json` has `version: "2.0"`

---

#### 1.3: Install spaCy Dependency

**Purpose:** Accurate POS tagging for concept extraction

**Installation:**

```bash
# Install spaCy
pip install spacy

# Download English model (small, ~13MB)
python -m spacy download en_core_web_sm
```

**Add to requirements.txt:**

```
spacy>=3.7.0
en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

**Verify Installation:**

```python
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Docker is a containerization platform")
for token in doc:
    print(f"{token.text}: {token.pos_}")

# Expected output:
# Docker: PROPN
# is: AUX
# a: DET
# containerization: NOUN
# platform: NOUN
```

**Files Modified:**
- `learners/patterns.py` (+150 lines of new dataclasses and methods)
- `requirements.txt` (+2 lines)

**Completion Criteria:**
- ✅ `patterns.json` backed up and cleared
- ✅ New pattern types recognized by PatternLearner
- ✅ spaCy installed and verified
- ✅ `patterns.json` version is "2.0"

---


1. [Executive Summary](#executive-summary)
2. [The Problem](#the-problem)
3. [The Solution](#the-solution)
4. [Expected Outcomes](#expected-outcomes)
5. [Part 1: Core Pattern System (Days 1-16)](#part-1-core-pattern-system)
   - [Step 1: Cleanup & Foundation](#step-1-cleanup--foundation)
   - [Step 2: Concept Extraction Overhaul](#step-2-concept-extraction-overhaul)
   - [Step 3: Query → Chunk Pattern Learning](#step-3-query--chunk-pattern-learning)
   - [Step 4: Domain → Collection Priority Learning](#step-4-domain--collection-priority-learning)
   - [Step 5: Conceptual Pattern Refinement](#step-5-conceptual-pattern-refinement)
   - [Step 6: Pattern Quality Controls](#step-6-pattern-quality-controls)
   - [Step 7: Pattern Enhancement APIs](#step-7-pattern-enhancement-apis)
6. [Part 2: Ancillary Use Cases - Pattern Intelligence Layer](#part-2-ancillary-use-cases)
   - [Use Case 1: Proactive Context Loading](#use-case-1-proactive-context-loading)
   - [Use Case 2: Domain Auto-Detection Enhancement](#use-case-2-domain-auto-detection-enhancement)
   - [Use Case 3: Multi-Model Router Optimization](#use-case-3-multi-model-router-optimization)
   - [Use Case 4: Session Context Persistence](#use-case-4-session-context-persistence)
   - [Use Case 5: Smart Notification Filtering](#use-case-5-smart-notification-filtering)
   - [Use Case 6: Intelligent Command Suggestions](#use-case-6-intelligent-command-suggestions)
   - [Use Case 7: Knowledge Gap Detection](#use-case-7-knowledge-gap-detection)
   - [Use Case 8: Concept-Based Obsidian Linking](#use-case-8-concept-based-obsidian-linking)
   - [Use Case 9: Autonomous Task Execution Patterns](#use-case-9-autonomous-task-execution-patterns)
7. [Success Criteria](#success-criteria)
8. [Files Modified/Created](#files-modifiedcreated)
9. [Timeline & Implementation Strategy](#timeline--implementation-strategy)
10. [Marketing Alignment](#marketing-alignment)

---

## Executive Summary

Phase 13a transforms the pattern learning system from a broken collection of 3,405 garbage patterns into a **multi-layered intelligence layer** that makes Polly fundamentally smarter across every subsystem.

### Primary Goal: RAG Efficiency (30-70% faster retrieval)

As the knowledge base scales from 4,000 to 40,000+ documents, RAG search becomes slower. Pattern learning creates efficient lookup paths—a map that guides RAG directly to the right documents without searching everything.

### Secondary Goal: System-Wide Intelligence

The same patterns that optimize RAG also enhance:
- **Domain detection** (Phase 1.5): Learns which terms map to which domains
- **Multi-model routing** (Phase 11): Routes queries based on learned success patterns
- **Autonomous tasks** (Phase 3): Remembers project-specific build/deploy workflows
- **Context loading** (Phase 20): Pre-warms cache with frequently-used documents
- **Notification filtering** (Phase 6): Surfaces only topics user cares about
- **Command suggestions** (Phase 10): Suggests correct commands based on learned workflows
- **Knowledge gaps** (Phase 18): Identifies poorly-answered topics needing new integrations
- **Obsidian linking** (Phase 12): Suggests note connections based on learned concept relationships
- **Session persistence** (Phase 20): Resumes conversations with relevant context pre-loaded

### What Makes This Different

Other AI systems learn patterns and forget them. Polly's pattern system:
- **Persists permanently** (stored in `~/.polly/patterns.json`)
- **Tracks usefulness** (measures which patterns actually help)
- **Self-prunes** (removes low-quality patterns automatically)
- **Compounds over time** (gets smarter the more you use it)

This aligns with Polly's core marketing: **"Knowledge that compounds, not dependency that scales."**

---

## The Problem

### Current Pattern System Issues

**File:** `~/.polly/patterns.json`  
**Current State:** 3,405 patterns (79,068 lines)  
**Quality:** 99% garbage, ~30 meaningful patterns (1%)

**Example Garbage Patterns:**
```json
{
  "pattern_type": "conceptual",
  "concept1": "calm",
  "concept2": "pick",
  "occurrences": 8,
  "confidence": 0.88,
  "description": "You frequently explore calm and pick together"
}
```

**Root Causes:**

1. **Overly Aggressive Concept Extraction** (`learners/patterns.py` lines 644-711)
   - Extracts ANY capitalized word as a "concept"
   - Only filters ~40 stopwords (misses "calm", "pick", "spend", "think", "for")
   - 50 concepts extracted → 1,225 possible pairs created
   - Common words treated as technical concepts

2. **Too Lenient Minimum Threshold**
   - `min_occurrences = 3` is too low
   - After 3 co-occurrences, pattern is "learned"
   - Random word pairs hit this threshold quickly

3. **Pattern Learning Triggered Too Frequently**
   - Called after EVERY conversation with 3+ messages
   - No throttling or quality checks
   - One conversation → hundreds of garbage patterns

4. **No Pattern Decay or Cleanup**
   - Patterns never expire or get pruned
   - No mechanism to remove low-quality patterns
   - `patterns.json` grows unbounded

### Impact on RAG System

Current RAG implementation (`core/rag.py`):
- **Hybrid Search:** Semantic (embeddings) + BM25 (keyword)
- **Collections:** Obsidian, codebase, documents, GitHub integrations
- **Current scale:** ~4,000 documents
- **Bottleneck:** Searches all collections every time, no learned shortcuts

As knowledge base grows:
- Semantic search gets slower (even with vector indexing)
- Every query re-computes from scratch (no caching)
- Domain filtering happens AFTER retrieval (wastes compute)
- No learned query → chunk associations

---

## The Solution

### Three-Layered Pattern System

#### Layer 1: Query → Chunk Patterns (HIGHEST IMPACT)

**Purpose:** Learn which specific chunks/files answer query types well

**How It Works:**
- After each RAG search, record which chunks had high scores (>0.7)
- Track: `query_template → chunk_id → hit_count & avg_score`
- Future queries matching template → boost known-good chunks by 1.8x

**Example Pattern:**
```json
{
  "pattern_type": "query_chunk",
  "query_template": "how_to_X_with_Y",
  "query_signature": "how_to_use_docker_with",
  "successful_chunks": [
    {
      "chunk_id": "abc123",
      "filepath": "docs/docker-python-guide.md",
      "hit_count": 5,
      "avg_score": 0.87
    }
  ],
  "total_queries": 8
}
```

**Expected Impact:** 30-50% faster RAG for repeated query patterns

---

#### Layer 2: Domain → Collection Priorities (MEDIUM IMPACT)

**Purpose:** Learn which collections are most relevant per domain

**How It Works:**
- Track which collections return useful results for each domain
- Calculate `hit_rate` per collection per domain
- Skip collections with <20% hit rate when better options exist
- Adjust `n_results` based on historical relevance

**Example Pattern:**
```json
{
  "pattern_type": "domain_priority",
  "domain": "signals",
  "collection_priorities": {
    "obsidian": {"weight": 0.6, "hit_rate": 0.75, "queries": 120},
    "integration_github_norns": {"weight": 0.8, "hit_rate": 0.82, "queries": 90},
    "codebase": {"weight": 0.3, "hit_rate": 0.45, "queries": 50}
  }
}
```

**Expected Impact:** 20-40% faster RAG (skip irrelevant sources)

---

#### Layer 3: Conceptual Patterns (LOW IMPACT, REFINED)

**Purpose:** Learn concept connections for query expansion

**How It Works:**
- Extract only meaningful concepts (nouns + technical terms)
- Use spaCy POS tagging + 500+ term whitelist + 700+ stopwords
- Strict quality filters (4+ chars, not stopwords, at least one technical term)
- `min_occurrences: 3 → 7`
- Cap at 200 patterns (top by confidence × occurrences)

**Example Pattern:**
```json
{
  "pattern_type": "conceptual",
  "primary_concept": "docker",
  "related_concepts": [
    {"concept": "python", "co_occurrence": 45, "usefulness": 0.8},
    {"concept": "containerization", "co_occurrence": 32, "usefulness": 0.75}
  ]
}
```

**Expected Impact:** 10-20% better relevance (query expansion)

---

## Expected Outcomes

### Performance Improvements (Measured with Relative Metrics)

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| RAG search time (repeated queries) | Baseline | 30-50% faster | Query→Chunk boost |
| RAG search time (domain filtering) | Baseline | 20-40% faster | Skip irrelevant collections |
| Query relevance | Baseline | 10-20% better | Query expansion |
| **Combined effect** | Baseline | **50-70% faster** | All layers working together |

### Pattern Quality Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total patterns | 3,405 | 200-400 | -89% |
| Meaningful patterns | ~30 (1%) | 150-300 (75%+) | +1000% |
| Pattern usefulness | 1% | 75%+ | +7400% |
| Storage size | 79k lines | ~10k lines | -87% |

### System-Wide Intelligence

Beyond RAG efficiency, patterns provide:
- **Domain detection:** 15-25% higher confidence scores
- **Multi-model routing:** 10-20% better routing accuracy
- **Autonomous tasks:** Learns build processes after 3 executions
- **Context loading:** 50-80% latency reduction on first query per domain
- **Notification filtering:** 40-60% fewer irrelevant notifications

---


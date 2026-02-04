# Phase 13A Ancillary Use Cases - Implementation Guide

**Status:** Ready for Implementation  
**Document Version:** 1.0  
**Last Updated:** January 25, 2026  
**Core System:** Phase 13a COMPLETE ✅

---

## Overview

Phase 13A Pattern Learning System is now complete. The core pattern learning engine provides three powerful pattern types:

1. **Query→Chunk Patterns** - Learn which documents answer queries well (30-50% speedup)
2. **Domain→Collection Priorities** - Learn which collections are relevant per domain (20-40% speedup)
3. **Conceptual Patterns** - Learn concept relationships for query expansion (10-20% better relevance)

This document outlines **9 ancillary use cases** that leverage these patterns to enhance other phases. Each use case is fully specified and ready to implement in its natural phase.

---

## Implementation Strategy

**Key Principle:** Implement ancillary use cases **during their natural phases**, not as a separate Phase 13b.

**Why This Approach?**
- Avoids duplicate work (implementing features out-of-context, then again in-context)
- Each use case enhances an existing phase with pattern-learning intelligence
- Natural integration points already exist
- Better testing (feature + pattern enhancement tested together)

**Example:** Use Case 2 (Domain Auto-Detection Enhancement) should be implemented as part of Phase 1.5 Day 5, NOT as a standalone Phase 13b task.

---

## Ancillary Use Cases Summary

| # | Use Case | Target Phase | Priority | Expected Impact | Effort |
|---|----------|-------------|----------|-----------------|--------|
| 1 | Proactive Context Loading | Phase 20 | HIGH | 50-80% latency reduction | 4-6 hours |
| 2 | Domain Auto-Detection Enhancement | **Phase 1.5** | **CRITICAL ⭐** | **15-25% confidence boost** | **3-4 hours** |
| 3 | Autonomous Workflow Learning | Phase 3 | HIGH | 80%+ troubleshooting success | 1-2 days |
| 4 | Multi-Model Router Optimization | Phase 11 | HIGH | 10-20% better routing | 4-6 hours |
| 5 | Session Context Persistence | Phase 20 | HIGH | Context in <500ms | 4-6 hours |
| 6 | Smart Notification Filtering | Phase 6 | MEDIUM | 40-60% fewer notifications | 3-4 hours |
| 7 | Intelligent Command Suggestions | Phase 10 | MEDIUM | 70%+ suggestion accuracy | 4-6 hours |
| 8 | Knowledge Gap Detection | Phase 18 | MEDIUM | 3-5 gaps/month identified | 2-3 hours |
| 9 | Concept-Based Obsidian Linking | Phase 12 | LOW-MEDIUM | 60%+ link accuracy | 3-4 hours |

**Total Estimated Effort:** 3-4 days (spread across multiple phases)

---

## CRITICAL: Use Case 2 - Domain Auto-Detection Enhancement ⭐

**Target Phase:** Phase 1.5 (Domain Configuration System)  
**When to Implement:** Day 5 (alongside AI keyword suggestions)  
**Priority:** CRITICAL - Phase 1.5 already in progress  
**Effort:** 3-4 hours  
**Expected Impact:** 15-25% higher domain detection confidence, 20-30% fewer user prompts

### What It Does

Enhances Phase 1.5's domain auto-detection by using learned patterns to boost confidence scores.

**Example Scenario:**
1. User creates Obsidian note with content: "Grid controls for sequencing"
2. **Without patterns:** Keyword analysis finds "grid" → uncertain (could be general UI or signals domain) → confidence 0.65 → asks user
3. **With patterns:** Checks patterns → "grid" frequently appears in "signals" domain with `integration_github_norns` collection → boosts confidence from 0.65 → 0.85 → auto-files to signals domain (no prompt needed)

### Integration Point

**File:** `core/polly.py` (lines 200-250, domain detection logic)

**Method:** `_detect_domains(query: str, context: Optional[Dict]) -> List[str]`

### Implementation Specification

**Step 1: Pattern-Based Confidence Boosting**

Add to `core/polly.py`:

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
    # Step 1: Existing keyword-based detection (Phase 1.5)
    domain_scores = await self._analyze_keywords(query)
    # Returns: {'signals': 0.65, 'sigils': 0.30, 'sanctuary': 0.05}
    
    # Step 2: NEW - Boost scores using domain→collection patterns
    if self.pattern_learner:
        pattern_scores = self._get_pattern_domain_scores(query)
        
        # Combine scores with pattern boost (up to +25%)
        for domain, pattern_score in pattern_scores.items():
            if domain in domain_scores:
                boost = min(pattern_score * 0.25, 0.25)
                domain_scores[domain] += boost
                logger.info(f"Pattern boosted {domain}: {domain_scores[domain]-boost:.2f} → {domain_scores[domain]:.2f} (+{boost:.2f})")
    
    # Step 3: NEW - Use conceptual patterns for term expansion
    if self.pattern_learner:
        expanded_terms = self._expand_query_terms_for_domain_detection(query)
        if expanded_terms:
            logger.info(f"Expanded query terms: {expanded_terms}")
            # Re-analyze with expanded terms
            expanded_scores = await self._analyze_keywords(f"{query} {' '.join(expanded_terms)}")
            
            # Merge scores (take max of original vs expanded)
            for domain, score in expanded_scores.items():
                domain_scores[domain] = max(domain_scores.get(domain, 0), score)
    
    # Step 4: Return domains above threshold (existing Phase 1.5 logic)
    confident_domains = [d for d, score in domain_scores.items() if score > 0.7]
    
    return confident_domains if confident_domains else [max(domain_scores, key=domain_scores.get)]
```

**Step 2: Pattern Domain Scoring**

Add to `core/polly.py`:

```python
def _get_pattern_domain_scores(self, query: str) -> Dict[str, float]:
    """
    Get domain confidence scores based on learned domain→collection patterns.
    
    Returns:
        Dict mapping domain → confidence score (0-1)
    """
    scores = {}
    
    # Extract concepts from query
    query_concepts = set(query.lower().split())
    
    # Check each domain's learned collection patterns
    for domain_pattern in self.pattern_learner.domain_priority_patterns.values():
        domain = domain_pattern.domain
        
        # Calculate relevance score based on collection weights
        # Higher weights = this domain frequently uses these collections
        avg_weight = sum(domain_pattern.collection_weights.values()) / len(domain_pattern.collection_weights)
        
        # Normalize to 0-1 range (weights are 0-2, so divide by 2)
        score = min(avg_weight / 2.0, 1.0)
        scores[domain] = score
    
    return scores
```

**Step 3: Conceptual Pattern Expansion**

Add to `core/polly.py`:

```python
def _expand_query_terms_for_domain_detection(self, query: str) -> List[str]:
    """
    Expand query terms using conceptual patterns for better domain detection.
    
    Example: "grid" → also consider "norns", "monome" (from learned patterns)
    
    Returns:
        List of expanded terms (max 3)
    """
    query_concepts = set(query.lower().split())
    expanded_terms = []
    
    for concept in query_concepts:
        # Find conceptual patterns for this concept
        related_patterns = self.pattern_learner.get_conceptual_patterns_for_concept(concept)
        
        # Add related concepts (top 2 per query concept)
        for pattern in related_patterns[:2]:
            concept1 = pattern.metadata.get('concept1')
            concept2 = pattern.metadata.get('concept2')
            
            # Get the related concept (not the query concept)
            related = concept2 if concept1 == concept else concept1
            if related and related not in query_concepts:
                expanded_terms.append(related)
    
    return expanded_terms[:3]  # Limit to top 3 expanded terms
```

**Step 4: Record Successful Detections (Learning Loop)**

Add to `core/polly.py` after domain detection succeeds:

```python
# After domain detection completes
if self.pattern_learner and detected_domains:
    # If user doesn't correct the domain, it was successful
    # (Track user corrections in a separate method)
    self.pattern_learner.record_successful_domain_detection(
        query=query,
        detected_domains=detected_domains,
        user_accepted=True  # Set to False if user manually changes domain
    )
```

**Step 5: Add Learning Method to PatternLearner**

Add to `learners/patterns.py`:

```python
def record_successful_domain_detection(
    self,
    query: str,
    detected_domains: List[str],
    user_accepted: bool
):
    """
    Record successful (or unsuccessful) domain detection for learning.
    
    Args:
        query: User query that triggered detection
        detected_domains: Domains detected by system
        user_accepted: True if user accepted, False if user corrected
    """
    if not user_accepted:
        logger.info(f"Domain detection correction recorded: {query} → {detected_domains}")
        # Could implement negative learning here (reduce weights)
        return
    
    # Positive reinforcement: domain detection was correct
    for domain in detected_domains:
        if domain in self.domain_priority_patterns:
            # Increase confidence in this domain's collection weights
            pattern = self.domain_priority_patterns[domain]
            pattern.times_used += 1
            logger.debug(f"Domain detection success: {domain} (used {pattern.times_used} times)")
```

### Success Criteria

- ✅ Domain confidence scores boosted by 15-25% when patterns match
- ✅ 20-30% fewer user prompts for domain selection
- ✅ Query term expansion adds 1-3 related terms per query
- ✅ Pattern-based boost logged for debugging
- ✅ System learns from user corrections (records accepted vs. corrected)

### Testing Plan

**Test 1: Pattern Boost Increases Confidence**
```python
# Given: Patterns show "grid" frequently in signals domain
# When: User queries "Grid controls for sequencing"
# Then: signals confidence increases from ~0.65 to ~0.85+
```

**Test 2: Term Expansion Improves Detection**
```python
# Given: Patterns show "grid" ↔ "norns" conceptual link
# When: User queries "Grid documentation"
# Then: Query expanded to "Grid documentation norns"
# And: signals domain confidence increases
```

**Test 3: Learning Loop Records Success**
```python
# When: User accepts auto-filed domain (doesn't correct)
# Then: domain_priority_patterns[domain].times_used += 1
```

**Test 4: No Patterns Fallback**
```python
# Given: Pattern learner has no patterns yet
# When: User queries anything
# Then: Falls back to Phase 1.5 keyword-only detection (no errors)
```

### Files Modified

- `core/polly.py`: +80 lines (3 new methods, learning loop)
- `learners/patterns.py`: +20 lines (record_successful_domain_detection method)

**Total:** ~100 lines, 3-4 hours effort

---

## Use Case 1: Proactive Context Loading

**Target Phase:** Phase 20 (Context Window Management)  
**Priority:** HIGH  
**Effort:** 4-6 hours  
**Expected Impact:** 50-80% latency reduction on first query per domain

### What It Does

Pre-loads relevant context before the user asks a question, based on learned query→chunk patterns.

**Example Scenario:**
1. User switches to signals domain (opens a norns project folder)
2. System detects domain change
3. Query→chunk patterns show top 10 chunks frequently accessed for signals queries
4. System pre-warms context cache with those chunks
5. User asks: "How do I use the engine library?"
6. Response is instant (context already loaded)

### Integration Point

**Files:** `core/context_manager.py` (Phase 20, to be created), `integrations/shell_integration.py` (Phase 10)

**Trigger:** Directory change detected by shell integration

### Implementation Specification

**Step 1: Detect Domain Changes**

In `integrations/shell_integration.py`:

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

In `core/polly.py`:

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
    
    # Get top chunks from query→chunk patterns
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

### Success Criteria

- ✅ Context pre-loaded in <200ms after domain change
- ✅ First query after domain change has 50-80% lower latency
- ✅ Top 10 chunks identified from patterns (hit_count ≥5, avg_score ≥0.75)
- ✅ No impact if patterns don't exist yet (graceful fallback)

### Files Modified

- `core/polly.py`: +40 lines
- `integrations/shell_integration.py`: +25 lines
- `core/context_manager.py`: +30 lines (Phase 20 file)

---

## Use Case 3: Autonomous Workflow Learning

**Target Phase:** Phase 3 (Enhanced Autonomous Task Execution)  
**Priority:** HIGH  
**Effort:** 1-2 days  
**Expected Impact:** 80%+ troubleshooting success rate, remembers project workflows

### What It Does

Learns project-specific build/deploy/test workflows and common failure patterns.

**Example Scenario:**
1. User works on `~/bees` firmware project (norns hardware)
2. User manually builds 5 times: `colima start && cd ~/bees && docker build -t bees-build . && make firmware`
3. System learns this as a `ProjectWorkflowPattern`
4. Next time user says: "Build the bees firmware"
5. System immediately knows the exact command sequence
6. If Docker fails, system knows to run `colima start` first

### Pattern Storage

**Pattern Type:** `ProjectWorkflowPattern` (already added in Phase 13a Day 1)

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

### Integration Point

**Files:** `learners/patterns.py` (workflow learning methods), `core/task_executor.py` (Phase 3), `integrations/shell_integration.py` (observe commands)

### Implementation Specification

**Step 1: Observe Successful Command Sequences**

In `integrations/shell_integration.py`:

```python
class ShellIntegration:
    def __init__(self):
        self.recent_commands = []  # Track last 10 commands
    
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
        
        # If command sequence looks like a workflow, learn it
        if self._looks_like_workflow_sequence(self.recent_commands[-5:]):
            await self._learn_workflow_pattern(self.recent_commands[-5:])
    
    def _looks_like_workflow_sequence(self, commands: List[Dict]) -> bool:
        """
        Detect if command sequence is a repeatable workflow.
        
        Heuristics:
        - Multiple commands in same directory
        - Commands include build/deploy/test keywords
        - All commands succeeded
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
```

**Step 2: Learn Workflow Pattern**

In `learners/patterns.py`:

```python
async def learn_workflow_pattern(self, commands: List[Dict], domain: str):
    """
    Learn a workflow pattern from observed command sequence.
    
    Args:
        commands: List of command dicts with command, exit_code, cwd, timestamp
        domain: Detected domain for this workflow
    """
    project_path = commands[0]['cwd']
    
    # Detect workflow type from commands
    workflow_type = self._detect_workflow_type(commands)
    
    # Create pattern ID
    pattern_id = f"workflow_{Path(project_path).name}_{workflow_type}"
    
    # Check if pattern already exists
    if pattern_id in self.project_workflow_patterns:
        # Update existing pattern
        pattern = self.project_workflow_patterns[pattern_id]
        pattern.learned_from += 1
        pattern.last_success = datetime.now()
        pattern.confidence = min(pattern.confidence + 0.1, 1.0)
        logger.info(f"Updated workflow pattern: {pattern_id} (learned from {pattern.learned_from} executions)")
    else:
        # Create new pattern
        pattern = ProjectWorkflowPattern(
            pattern_id=pattern_id,
            project_path=project_path,
            domain=domain,
            workflow_type=workflow_type,
            command_sequence=[{
                'step': i+1,
                'command': cmd['command'],
                'description': self._describe_command(cmd['command'])
            } for i, cmd in enumerate(commands)],
            prerequisites=[],  # To be learned from failures
            common_failures=[],  # To be learned from error patterns
            learned_from=1,
            last_success=datetime.now(),
            confidence=0.5  # Start with medium confidence
        )
        self.project_workflow_patterns[pattern_id] = pattern
        logger.info(f"Created new workflow pattern: {pattern_id}")
    
    # Save patterns
    self.save_patterns()

def _detect_workflow_type(self, commands: List[Dict]) -> str:
    """Detect workflow type from command sequence."""
    command_text = ' '.join(cmd['command'] for cmd in commands).lower()
    
    if 'build' in command_text or 'make' in command_text or 'compile' in command_text:
        return 'build'
    elif 'deploy' in command_text or 'publish' in command_text:
        return 'deploy'
    elif 'test' in command_text or 'pytest' in command_text:
        return 'test'
    elif 'run' in command_text or 'start' in command_text:
        return 'run'
    else:
        return 'custom'
```

**Step 3: Use Learned Workflows in Task Executor**

In `core/task_executor.py` (Phase 3):

```python
async def execute_task(self, task_description: str, context: Dict):
    """
    Execute a task autonomously, using learned workflow patterns when available.
    """
    # Check if task matches a learned workflow
    workflow = self._find_matching_workflow(task_description, context)
    
    if workflow and workflow.confidence >= 0.7:
        logger.info(f"Using learned workflow: {workflow.pattern_id} (confidence {workflow.confidence})")
        
        # Execute workflow command sequence
        for step in workflow.command_sequence:
            logger.info(f"Step {step['step']}: {step['description']}")
            result = await self._execute_command(step['command'])
            
            if result.exit_code != 0:
                # Check for known failure patterns
                fix = self._find_fix_for_error(workflow, result.output)
                if fix:
                    logger.info(f"Applying known fix: {fix}")
                    await self._execute_command(fix)
                else:
                    raise TaskExecutionError(f"Step {step['step']} failed: {result.output}")
    else:
        # No learned workflow, fall back to LLM-based execution
        logger.info(f"No learned workflow found, using LLM execution")
        await self._execute_with_llm(task_description, context)
```

### Success Criteria

- ✅ System learns workflows after 3-5 successful repetitions
- ✅ Learned workflows have 80%+ success rate when executed
- ✅ Common failures tracked with fixes
- ✅ Workflow confidence increases with each success
- ✅ Task executor prefers learned workflows over LLM (when confident)

### Files Modified

- `learners/patterns.py`: +150 lines (learn_workflow_pattern, helpers)
- `integrations/shell_integration.py`: +80 lines (command observation)
- `core/task_executor.py`: +120 lines (workflow execution)

**Total:** ~350 lines, 1-2 days effort

---

## Use Case 4: Multi-Model Router Optimization

**Target Phase:** Phase 11 (Multi-Model + Intelligent Routing)  
**Priority:** HIGH  
**Effort:** 4-6 hours  
**Expected Impact:** 10-20% better routing accuracy

### What It Does

Uses query→chunk patterns to determine if a query is well-answered by local docs (route to local model) or requires external APIs (route to cloud model).

### Integration Point

**File:** `core/model_router.py` (Phase 11)

**Method:** Check patterns before routing decision

### Implementation Specification

```python
class ModelRouter:
    async def route_query(self, query: str, context: Dict) -> ModelSelection:
        """
        Route query to appropriate model based on confidence and patterns.
        """
        # Step 1: Check query→chunk patterns for local confidence
        local_confidence = self._get_local_confidence(query)
        
        # Step 2: If patterns show high local confidence, prefer local
        if local_confidence >= 0.75:
            logger.info(f"High local confidence ({local_confidence}), routing to local model")
            return ModelSelection(model='llama3.2', reason='high_pattern_confidence')
        
        # Step 3: If patterns show low confidence, prefer cloud
        if local_confidence < 0.4:
            logger.info(f"Low local confidence ({local_confidence}), routing to cloud model")
            return ModelSelection(model='claude-sonnet', reason='low_pattern_confidence')
        
        # Step 4: Medium confidence - use existing routing logic
        return await self._route_with_rag_analysis(query, context)
    
    def _get_local_confidence(self, query: str) -> float:
        """Get confidence that query can be answered locally from patterns."""
        if not self.pattern_learner:
            return 0.5  # Default medium confidence
        
        # Check query→chunk patterns
        template = self.pattern_learner._extract_query_template(query)
        pattern = self.pattern_learner.query_chunk_patterns.get(template)
        
        if not pattern or not pattern.successful_chunks:
            return 0.5  # No learned pattern
        
        # Calculate average score from successful chunks
        avg_score = sum(c['avg_score'] for c in pattern.successful_chunks[:5]) / min(len(pattern.successful_chunks), 5)
        
        return avg_score
```

### Success Criteria

- ✅ Router queries patterns before deciding model
- ✅ 10-20% better routing accuracy (measured by user corrections)
- ✅ Faster queries (local model preferred when confident)

---

## Remaining Use Cases (5-9)

### Use Case 5: Session Context Persistence
**Target:** Phase 20 | **Effort:** 4-6 hours | **Impact:** Context in <500ms on resume

### Use Case 6: Smart Notification Filtering
**Target:** Phase 6 | **Effort:** 3-4 hours | **Impact:** 40-60% fewer irrelevant notifications

### Use Case 7: Intelligent Command Suggestions
**Target:** Phase 10 | **Effort:** 4-6 hours | **Impact:** 70%+ suggestion accuracy

### Use Case 8: Knowledge Gap Detection
**Target:** Phase 18 | **Effort:** 2-3 hours | **Impact:** 3-5 gaps/month identified

### Use Case 9: Concept-Based Obsidian Linking
**Target:** Phase 12 | **Effort:** 3-4 hours | **Impact:** 60%+ link accuracy

**Note:** Detailed specs for Use Cases 5-9 are available in `PHASE13A_PATTERN_LEARNING_CORE.md` (lines 21-120)

---

## Implementation Prioritization

### Immediate (Next Session)

**Priority 1: Use Case 2 - Domain Auto-Detection Enhancement**
- **Why now:** Phase 1.5 is already in progress (Day 4 of 6)
- **When:** Implement during Phase 1.5 Day 5 (alongside AI keyword suggestions)
- **Effort:** 3-4 hours
- **Impact:** HIGH - 15-25% confidence boost, 20-30% fewer user prompts
- **Files:** `core/polly.py` (+80 lines), `learners/patterns.py` (+20 lines)

### Near-Term (Within Tier 1)

**Priority 2: Use Case 4 - Multi-Model Router Optimization**
- **When:** Phase 11 implementation
- **Effort:** 4-6 hours
- **Impact:** HIGH - 10-20% better routing accuracy

**Priority 3: Use Case 3 - Autonomous Workflow Learning**
- **When:** Phase 3 enhancement (or Phase 17 Code Workspace)
- **Effort:** 1-2 days
- **Impact:** HIGH - 80%+ troubleshooting success rate

### Mid-Term (Tier 3-4)

**Priority 4: Use Case 1 - Proactive Context Loading**
- **When:** Phase 20 implementation
- **Effort:** 4-6 hours
- **Impact:** HIGH - 50-80% latency reduction

**Priority 5: Use Case 5 - Session Context Persistence**
- **When:** Phase 20 implementation
- **Effort:** 4-6 hours
- **Impact:** HIGH - Context in <500ms

### Lower Priority (As Needed)

**Priority 6: Use Case 8 - Knowledge Gap Detection**
- **When:** Phase 18 implementation
- **Effort:** 2-3 hours
- **Impact:** MEDIUM

**Priority 7: Use Case 6 - Smart Notification Filtering**
- **When:** Phase 6 enhancement (optional tier)
- **Effort:** 3-4 hours
- **Impact:** MEDIUM

**Priority 8: Use Case 7 - Intelligent Command Suggestions**
- **When:** Phase 10 (iOS Mobile) - if implemented
- **Effort:** 4-6 hours
- **Impact:** MEDIUM

**Priority 9: Use Case 9 - Concept-Based Obsidian Linking**
- **When:** Phase 12b (Knowledge Graph Reasoning)
- **Effort:** 3-4 hours
- **Impact:** LOW-MEDIUM

---

## Testing Strategy

### Unit Tests

Each use case should have:
- ✅ Pattern lookup tests (verify pattern APIs return correct data)
- ✅ Boost calculation tests (verify confidence increases)
- ✅ Fallback tests (no patterns → graceful degradation)
- ✅ Integration tests (end-to-end flow with real patterns)

### Integration Tests

- ✅ Use Case 2: Domain detection with patterns vs without
- ✅ Use Case 3: Workflow execution success rate (before/after learning)
- ✅ Use Case 4: Routing accuracy (local vs cloud decisions)

### Performance Tests

- ✅ Pattern lookup overhead < 10ms per query
- ✅ No memory leaks (patterns capped at 200-400 total)
- ✅ Pattern learning overhead < 50ms per query

---

## Success Metrics

### Overall

- ✅ 9/9 ancillary use cases implemented during natural phases
- ✅ Pattern learning system improves 6+ existing features
- ✅ No duplicate implementation work
- ✅ All use cases tested and documented

### Per Use Case

Track these metrics in `docs/PHASE13_METRICS.md`:

| Use Case | Metric | Target | Actual |
|----------|--------|--------|--------|
| Use Case 2 | Domain confidence boost | 15-25% | TBD |
| Use Case 2 | Fewer user prompts | 20-30% | TBD |
| Use Case 3 | Troubleshooting success | 80%+ | TBD |
| Use Case 4 | Routing accuracy | +10-20% | TBD |
| Use Case 1 | Latency reduction | 50-80% | TBD |
| Use Case 5 | Context load time | <500ms | TBD |

---

## Files Reference

### Core Pattern System (Phase 13a - Complete)

- `learners/patterns.py` - Pattern learner with 3 pattern types (~2,380 lines)
- `core/rag.py` - RAG with pattern-based boosting (~800 lines)
- `core/polly.py` - Main query engine with pattern integration (~1,200 lines)

### Ancillary Use Case Files (To Modify)

- `core/polly.py` - Use Cases 1, 2, 4, 5 (domain detection, context loading, routing)
- `learners/patterns.py` - Use Case 3 (workflow learning methods)
- `core/task_executor.py` - Use Case 3 (workflow execution)
- `integrations/shell_integration.py` - Use Cases 1, 3, 7 (directory changes, commands)
- `core/context_manager.py` - Use Cases 1, 5 (Phase 20 file, to be created)
- `core/model_router.py` - Use Case 4 (Phase 11 file, to be created)
- `integrations/github.py` - Use Case 6 (notification filtering)
- `integrations/obsidian.py` - Use Case 9 (link suggestions)
- `ui/autonomy_dashboard.tsx` - Use Case 8 (Phase 18 file, to be created)

---

## Documentation

- **Main Spec:** `PHASE13A_PATTERN_LEARNING_CORE.md` (~3,200 lines)
- **Progress Tracking:** `docs/PHASE13_PROGRESS.md` (updated to Day 16 complete)
- **This Guide:** `PHASE13A_ANCILLARY_USE_CASES.md` (implementation guide)
- **Quick Reference:** `PHASE1.5_QUICK_REFERENCE.md` (Use Case 2 integration)

---

## Questions & Decisions

### Should we implement Use Case 2 now or skip to Phase 13b UI?

**Recommendation:** Implement Use Case 2 NOW during Phase 1.5 Day 5.

**Reasoning:**
1. Phase 1.5 is already in progress (Day 4 of 6)
2. Use Case 2 directly enhances Phase 1.5's core feature (domain detection)
3. Small effort (3-4 hours) for high impact (15-25% confidence boost)
4. Natural integration point already exists in `core/polly.py`
5. Avoids context switching (finish Phase 1.5 completely before moving on)

**Alternative:** Skip Use Case 2, implement Phase 13b UI (7 days), then return to Phase 1.5 Day 5
- **Downside:** Breaks Phase 1.5 implementation flow, context switching overhead
- **Upside:** Pattern learning UI gives visibility into patterns before using them

### Should we audit all phases for pattern learning integrations now?

**Recommendation:** NO - Implement use cases during natural phases as planned.

**Reasoning:**
1. Each use case is fully specified with integration points
2. Implementing out-of-context risks duplicate work
3. Better to implement when the target phase is active (more context)
4. This guide provides clear roadmap for when to implement each use case

---

## Next Steps

1. ✅ **Complete Phase 13a documentation** (this guide)
2. ⏳ **Continue Phase 1.5 Day 5** - Implement AI keyword suggestions + Use Case 2
3. ⏳ **Complete Phase 1.5 Day 6** - First-run wizard
4. 📋 **Decide next phase:** Phase 13b (UI) vs Phase 21 (Deduplication) vs Phase 14 (Mental Models)

---

**End of Ancillary Use Cases Guide**

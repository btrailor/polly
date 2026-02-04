# Phase 13: Pattern Learning Overhaul

> **⚠️ DEPRECATION NOTICE**  
> This document has been superseded by the new Phase 13a/13b split documents:
> - **Phase 13a:** `PHASE13A_PATTERN_LEARNING_CORE.md` (~3,200 lines) - Core pattern system + RAG efficiency
> - **Phase 13b:** `PHASE13B_PATTERN_LEARNING_UI.md` (~960 lines) - UI, testing, validation
>
> **Reason for Split:** The pattern learning system was redesigned to focus on **RAG efficiency** (30-70% faster retrieval) rather than generic pattern collection. The new approach uses a multi-layered system (Query→Chunk, Domain→Collection, Conceptual) that makes Polly fundamentally smarter across all subsystems.
>
> **What Changed:**
> - Focus shifted from 4 generic pattern types → 3 RAG-focused types
> - Added spaCy for accurate concept extraction (vs naive capitalization)
> - Added 9 ancillary use cases (domain detection, workflow learning, etc.)
> - Split into 13a (core, 30 days) and 13b (UI/testing, 7 days)
>
> **Action:** Refer to the new documents for implementation. This document is kept for historical reference only.
>
> ---

# ORIGINAL DOCUMENT (DEPRECATED)

**Status:** IN PROGRESS (Days 1-6 Complete)  
**Priority:** 1st (Highest)  
**Estimated Effort:** 1-2 weeks (10-14 days)  
**Complexity:** High

**Progress:** 42% Complete (6/14 days)

---

## Executive Summary

Transform the dormant Pattern Learning system into an active intelligence layer that learns from all your work patterns (code, queries, concepts, workflows) and uses those learnings to improve Polly's responses over time.

## Current State Analysis

**Location:** `/learners/patterns.py` (445 lines)

**What Exists:**
- ✅ Complete data structures (`Pattern`, `QueryPattern` classes)
- ✅ Pattern storage/loading from JSON
- ✅ Query pattern detection
- ✅ Code pattern extraction
- ✅ Concept tracking
- ✅ Cross-domain detection

**The Problem:**
- ❌ System is **NOT connected to data flows**
- ❌ Storage files don't exist (`~/.polly/patterns.json` missing, only `.backup` from tests)
- ❌ Pattern recording happens but saves to nowhere
- ❌ Pattern retrieval is called but returns nothing
- ❌ Integration points exist in `polly.py` but are ineffective

**Current Integration Points (`/core/polly.py`):**
- Lines 98-112: Pattern learner initialization
- Lines 223-230: Query pattern recording (after each query)
- Lines 290-291: Pattern retrieval (before LLM call)

**The System Is:** Fully built, never turned on.

---

## Implementation Plan

### Step 1: Activate Core System (Days 1-2)

**Goal:** Fix storage issues and verify data flows work

#### Fix Storage Issues

Update `/learners/patterns.py`:

```python
def __init__(self, storage_path: Path, min_occurrences: int = 3):
    self.storage_path = Path(storage_path).expanduser()  # Fix path expansion
    self.storage_path.parent.mkdir(parents=True, exist_ok=True)  # Create directory
    
    self.min_occurrences = min_occurrences
    
    # In-memory pattern storage
    self.patterns: Dict[str, Pattern] = {}
    self.query_patterns: Dict[str, QueryPattern] = {}
    
    # Tracking for pattern discovery
    self.query_history: List[Dict] = []
    self.code_snippets: List[Dict] = []
    self.concept_mentions: Counter = Counter()
    self.cross_domain_pairs: Counter = Counter()
    
    # Load existing patterns
    self._load_patterns()
    
    # Initialize empty storage if doesn't exist
    if not self.storage_path.exists():
        self.storage_path.write_text(json.dumps({
            'patterns': [],
            'query_patterns': [],
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '2.0'
            }
        }, indent=2))
        logger.info(f"Initialized pattern storage at {self.storage_path}")
```

#### Verify Data Flow

Update `/core/polly.py`:

```python
async def query(self, user_query: str, **kwargs):
    # ... existing code ...
    
    # Record query pattern (make sure this actually saves)
    if self.pattern_learner:
        try:
            self.pattern_learner.record_query(user_query, domains)
            self.pattern_learner.save_patterns()  # EXPLICITLY SAVE
            logger.info(f"Recorded query pattern: {user_query[:50]}...")
        except Exception as e:
            logger.error(f"Failed to record pattern: {e}")
    
    # Retrieve relevant patterns (make sure this actually returns data)
    relevant_patterns = []
    if self.pattern_learner:
        try:
            relevant_patterns = self.pattern_learner.get_relevant_patterns(
                user_query, domains
            )
            if relevant_patterns:
                logger.info(f"Found {len(relevant_patterns)} relevant patterns")
            else:
                logger.debug("No relevant patterns found")
        except Exception as e:
            logger.error(f"Failed to retrieve patterns: {e}")
    
    # ... rest of query logic ...
```

**Testing:**
- Run Polly, make 3 queries
- Check that `~/.polly/patterns.json` exists
- Restart server, verify patterns persist
- Check logs for "Recorded query pattern" messages

---

### Step 2: Enhance Pattern Detection (Days 3-4)

**Goal:** Improve query and code pattern detection quality

#### Enhanced Query Pattern Detection

Add template extraction to `/learners/patterns.py`:

```python
def _extract_query_template(self, query: str) -> Tuple[str, Dict[str, str]]:
    """
    Extract a template from a query.
    
    Example:
      "How do I use Docker with Python?" 
      → "How do I use {tool} with {language}?"
      → fills: {"tool": "Docker", "language": "Python"}
    """
    # Detect question patterns
    patterns = [
        (r"how (?:do|can) i (\w+) (.+) with (.+)\?", "How do I {action} {thing} with {tool}?"),
        (r"what is the best way to (\w+) (.+)\?", "What is the best way to {action} {thing}?"),
        (r"explain (.+) in (.+)", "Explain {concept} in {context}"),
        (r"write (?:a|an) (.+) that (.+)", "Write a {thing} that {action}"),
        (r"debug (.+) in (.+)", "Debug {issue} in {context}"),
        (r"show me (.+) in (.+)", "Show me {thing} in {context}"),
        (r"create (.+) for (.+)", "Create {thing} for {purpose}"),
        (r"implement (.+) using (.+)", "Implement {feature} using {tool}"),
    ]
    
    for pattern, template in patterns:
        match = re.search(pattern, query.lower())
        if match:
            fills = {f"slot_{i}": g for i, g in enumerate(match.groups())}
            return template, fills
    
    # No template found, return query as-is
    return query, {}

def record_query(self, query: str, domains: List[str]):
    """Record a query with template extraction."""
    # Extract template
    template, fills = self._extract_query_template(query)
    
    # Store in history
    self.query_history.append({
        'query': query,
        'template': template,
        'fills': fills,
        'domains': _domains_to_strings(domains),
        'timestamp': datetime.now()
    })
    
    # If we have a template, track it
    if template != query:
        template_id = f"query_template_{hash(template) % 10000}"
        
        if template_id not in self.query_patterns:
            self.query_patterns[template_id] = QueryPattern(
                query_template=template,
                common_fills=defaultdict(list),
                frequency=1,
                domains=_domains_to_strings(domains)
            )
        else:
            self.query_patterns[template_id].frequency += 1
        
        # Track what fills each slot
        for slot, value in fills.items():
            if value not in self.query_patterns[template_id].common_fills[slot]:
                self.query_patterns[template_id].common_fills[slot].append(value)
```

#### Enhanced Code Pattern Detection

Create `/learners/code_patterns.py`:

```python
"""
Code Pattern Extractor
Uses AST parsing to detect patterns in code
"""

import ast
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class CodePatternExtractor:
    """Extract patterns from code using AST parsing."""
    
    def extract_from_python(self, code: str) -> List[Dict]:
        """
        Extract patterns from Python code.
        
        Patterns detected:
        - Common imports
        - Class structures
        - Function signatures
        - Decorator usage
        - Error handling patterns
        - Async patterns
        """
        patterns = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return patterns
        
        # Extract imports
        imports = [node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)]
        from_imports = [
            f"{node.module}.{alias.name}" 
            for node in ast.walk(tree) 
            if isinstance(node, ast.ImportFrom) and node.module
            for alias in node.names
        ]
        all_imports = imports + from_imports
        
        if all_imports:
            patterns.append({
                'type': 'imports',
                'pattern': 'Common imports',
                'details': Counter(all_imports).most_common(5)
            })
        
        # Extract class patterns
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        if classes:
            # Detect inheritance patterns
            base_classes = [
                base.id for cls in classes 
                for base in cls.bases 
                if isinstance(base, ast.Name)
            ]
            if base_classes:
                patterns.append({
                    'type': 'inheritance',
                    'pattern': 'Class inheritance',
                    'details': Counter(base_classes).most_common(3)
                })
            
            # Detect decorator patterns
            decorators = [
                dec.id for cls in classes 
                for dec in cls.decorator_list 
                if isinstance(dec, ast.Name)
            ]
            if decorators:
                patterns.append({
                    'type': 'decorators',
                    'pattern': 'Class decorators',
                    'details': Counter(decorators).most_common(3)
                })
        
        # Extract function patterns
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if functions:
            # Detect async functions
            async_funcs = [f for f in functions if isinstance(f, ast.AsyncFunctionDef)]
            if async_funcs:
                patterns.append({
                    'type': 'async',
                    'pattern': 'Async functions',
                    'count': len(async_funcs)
                })
            
            # Detect try/except patterns
            try_blocks = [node for node in ast.walk(tree) if isinstance(node, ast.Try)]
            if try_blocks:
                exception_types = []
                for try_block in try_blocks:
                    for handler in try_block.handlers:
                        if handler.type and isinstance(handler.type, ast.Name):
                            exception_types.append(handler.type.id)
                
                if exception_types:
                    patterns.append({
                        'type': 'error_handling',
                        'pattern': 'Exception handling',
                        'details': Counter(exception_types).most_common(3)
                    })
        
        return patterns
    
    def extract_from_javascript(self, code: str) -> List[Dict]:
        """Extract patterns from JavaScript code using regex."""
        patterns = []
        
        # Detect React patterns
        if 'import React' in code or "from 'react'" in code or 'from "react"' in code:
            patterns.append({'type': 'framework', 'pattern': 'React'})
        
        # Detect async/await
        if re.search(r'async\s+function', code):
            async_count = len(re.findall(r'async\s+function', code))
            patterns.append({
                'type': 'async',
                'pattern': 'Async/await',
                'count': async_count
            })
        
        # Detect arrow functions
        arrow_funcs = len(re.findall(r'=>', code))
        if arrow_funcs > 0:
            patterns.append({
                'type': 'style',
                'pattern': 'Arrow functions',
                'count': arrow_funcs
            })
        
        # Detect Promise usage
        if '.then(' in code or '.catch(' in code:
            patterns.append({'type': 'async', 'pattern': 'Promises'})
        
        # Detect common imports
        import_matches = re.findall(r'import .+ from [\'"](.+)[\'"]', code)
        if import_matches:
            patterns.append({
                'type': 'imports',
                'pattern': 'Common imports',
                'details': Counter(import_matches).most_common(5)
            })
        
        return patterns
```

**Testing:**
- Run pattern detection on sample code
- Verify templates extract correctly
- Check patterns make logical sense

---

### Step 3: Add Conceptual Pattern Learning (Days 5-6) ✅ COMPLETE

**Status:** ✅ COMPLETE (January 21, 2026)  
**Goal:** Learn patterns from how you connect concepts in conversations

**Implementation Summary:**
- ✅ Implemented `learn_conceptual_patterns()` method (~90 lines)
- ✅ Implemented `_extract_concepts()` method (~80 lines) 
- ✅ Implemented `_infer_domains_from_concepts()` with 100+ keywords (~50 lines)
- ✅ Created API endpoint POST `/polly/patterns/learn-from-conversation`
- ✅ Integrated with ConversationManager to trigger automatically
- ✅ Created 3 comprehensive test suites (all passing)
- ✅ Detected 7 patterns from 4 test conversations
- ✅ Patterns persist correctly to `~/.polly/patterns.json`

**Test Results:**
- Concept Extraction: ✅ 8/8 expected concepts found
- Domain Inference: ✅ 5/5 correct (100%)
- Pattern Learning: ✅ 7 patterns from 4 conversations
- Persistence: ✅ All patterns saved and reloaded

**See:** `/docs/DAY5-6_SUMMARY.md` for complete details

---

**Original Implementation Plan Below (for reference):**

Add to `/learners/patterns.py`:

```python
def learn_conceptual_patterns(self, conversation_history: List[Dict]):
    """
    Learn patterns from how user thinks about concepts.
    
    Detects:
    - Recurring themes across conversations
    - How you connect different domains
    - Mental models you reference
    - Preferred analogies/metaphors
    """
    # Extract key phrases from user messages
    user_messages = [msg['content'] for msg in conversation_history if msg['role'] == 'user']
    all_text = ' '.join(user_messages)
    
    # Extract frequently mentioned concepts (simple NLP)
    words = re.findall(r'\b[a-z]{4,}\b', all_text.lower())
    word_freq = Counter(words)
    
    # Filter to significant words (mentioned 3+ times)
    significant_words = {word for word, count in word_freq.items() if count >= 3}
    
    # Identify concept clusters (concepts mentioned together)
    concept_pairs = []
    for i in range(len(user_messages)):
        msg_words = set(re.findall(r'\b[a-z]{4,}\b', user_messages[i].lower()))
        msg_words = msg_words & significant_words
        
        # Get pairs of words in same message
        from itertools import combinations
        for w1, w2 in combinations(msg_words, 2):
            concept_pairs.append(tuple(sorted([w1, w2])))
    
    # Find recurring concept pairs
    pair_freq = Counter(concept_pairs)
    recurring_pairs = [(pair, count) for pair, count in pair_freq.items() if count >= 3]
    
    if recurring_pairs:
        for (concept1, concept2), count in recurring_pairs:
            pattern_id = f"concept_pair_{concept1}_{concept2}"
            
            if pattern_id not in self.patterns:
                self.patterns[pattern_id] = Pattern(
                    id=pattern_id,
                    name=f"Conceptual Connection: {concept1} ↔ {concept2}",
                    description=f"You frequently explore {concept1} and {concept2} together",
                    pattern_type="conceptual",
                    domains=self._infer_domains_from_concepts([concept1, concept2]),
                    examples=[],
                    occurrences=count,
                    first_seen=datetime.now(),
                    last_seen=datetime.now(),
                    confidence=min(count / 10.0, 1.0),
                    metadata={
                        'concept1': concept1,
                        'concept2': concept2
                    }
                )
            else:
                self.patterns[pattern_id].occurrences = count
                self.patterns[pattern_id].last_seen = datetime.now()

def _infer_domains_from_concepts(self, concepts: List[str]) -> List[str]:
    """Infer which domains concepts belong to based on keywords."""
    domain_keywords = {
        'sigils': ['code', 'docker', 'python', 'rust', 'infrastructure', 'automation', 'deploy'],
        'signals': ['audio', 'synthesis', 'norns', 'supercollider', 'midi', 'sound', 'music'],
        'scrolls': ['writing', 'essay', 'pedagogy', 'education', 'notes', 'freire', 'teaching'],
        'grids': ['systems', 'framework', 'model', 'constraint', 'game', 'infinite', 'structure'],
        'glyphs': ['design', 'visual', 'interface', 'layout', 'color', 'typography']
    }
    
    domains = []
    concepts_str = ' '.join(concepts)
    
    for domain, keywords in domain_keywords.items():
        if any(keyword in concepts_str for keyword in keywords):
            domains.append(domain)
    
    return domains or ['grids']  # Default to grids (systems thinking)
```

**Integration with Conversation System:**

Update `/electron-app/src/main/conversation-manager.js`:

```javascript
// After adding a message, trigger pattern learning
async function addMessage(conversationId, role, content) {
  // ... existing code to add message ...
  
  // Trigger pattern learning (send to backend)
  try {
    const conversation = await getConversation(conversationId);
    const messages = await getMessages(conversationId);
    
    // Send to backend for pattern learning
    await fetch('http://localhost:11436/polly/patterns/learn-from-conversation', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        conversation_id: conversationId,
        category: conversation.category,
        messages: messages
      })
    });
  } catch (error) {
    console.error('Failed to learn patterns:', error);
  }
}
```

**Testing:**
- Have conversations with recurring themes
- Check for concept pair patterns
- Verify domain inference works

---

### Step 4: Add Work Pattern Detection (Days 7-8)

**Goal:** Detect when and how you work

Create `/learners/work_patterns.py`:

```python
"""
Work Pattern Detector
Detects patterns in work habits and context switching
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
from collections import Counter
import logging

logger = logging.getLogger(__name__)

@dataclass
class WorkPattern:
    """A pattern in work habits."""
    pattern_type: str  # "time_of_day", "context_switch", "session_length"
    description: str
    frequency: int
    confidence: float
    metadata: Dict

class WorkPatternDetector:
    """Detects patterns in how you work."""
    
    def __init__(self):
        self.interaction_log: List[Dict] = []
    
    def log_interaction(self, interaction_type: str, context: Dict):
        """Log an interaction for pattern detection."""
        self.interaction_log.append({
            'timestamp': datetime.now(),
            'type': interaction_type,
            'context': context
        })
    
    def detect_time_patterns(self) -> List[WorkPattern]:
        """Detect time-of-day patterns."""
        patterns = []
        
        # Group interactions by hour
        hour_counts = Counter([
            log['timestamp'].hour 
            for log in self.interaction_log
        ])
        
        # Find peak hours (5+ interactions)
        if hour_counts:
            peak_hours = [hour for hour, count in hour_counts.items() if count >= 5]
            
            if peak_hours:
                patterns.append(WorkPattern(
                    pattern_type="time_of_day",
                    description=f"Most active during hours: {', '.join(map(str, sorted(peak_hours)))}",
                    frequency=sum(hour_counts[h] for h in peak_hours),
                    confidence=0.8,
                    metadata={'peak_hours': peak_hours}
                ))
        
        return patterns
    
    def detect_context_switches(self) -> List[WorkPattern]:
        """Detect patterns in switching between domains/projects."""
        patterns = []
        
        # Track domain switches
        domain_sequence = [
            log['context'].get('domain') 
            for log in self.interaction_log 
            if 'domain' in log['context']
        ]
        
        if len(domain_sequence) < 2:
            return patterns
        
        # Find common transitions
        transitions = []
        for i in range(len(domain_sequence) - 1):
            if domain_sequence[i] != domain_sequence[i+1]:
                transitions.append((domain_sequence[i], domain_sequence[i+1]))
        
        transition_counts = Counter(transitions)
        common_transitions = [
            (trans, count) 
            for trans, count in transition_counts.items() 
            if count >= 3
        ]
        
        if common_transitions:
            for (from_domain, to_domain), count in common_transitions:
                patterns.append(WorkPattern(
                    pattern_type="context_switch",
                    description=f"Often switches from {from_domain} to {to_domain}",
                    frequency=count,
                    confidence=min(count / 10.0, 1.0),
                    metadata={
                        'from_domain': from_domain,
                        'to_domain': to_domain
                    }
                ))
        
        return patterns
    
    def detect_session_patterns(self) -> List[WorkPattern]:
        """Detect patterns in work sessions."""
        patterns = []
        
        if not self.interaction_log:
            return patterns
        
        # Group interactions into sessions (gap > 30 min = new session)
        sessions = []
        current_session = []
        
        sorted_log = sorted(self.interaction_log, key=lambda x: x['timestamp'])
        
        for i, log in enumerate(sorted_log):
            if i == 0:
                current_session.append(log)
            else:
                time_gap = (log['timestamp'] - sorted_log[i-1]['timestamp']).total_seconds() / 60
                
                if time_gap > 30:  # 30 minute gap = new session
                    sessions.append(current_session)
                    current_session = [log]
                else:
                    current_session.append(log)
        
        if current_session:
            sessions.append(current_session)
        
        # Analyze session lengths
        if len(sessions) >= 3:
            session_lengths = [len(s) for s in sessions]
            avg_length = sum(session_lengths) / len(session_lengths)
            
            if avg_length > 5:
                patterns.append(WorkPattern(
                    pattern_type="session_length",
                    description=f"Typical work sessions involve ~{int(avg_length)} interactions",
                    frequency=len(sessions),
                    confidence=0.7,
                    metadata={
                        'average_session_length': avg_length,
                        'total_sessions': len(sessions)
                    }
                ))
        
        return patterns
```

**Testing:**
- Use Polly for several days
- Check work patterns detected
- Verify patterns are meaningful

---

### Step 5: Pattern-Informed Responses (Days 9-10)

**Goal:** Use learned patterns to improve responses

Update `/core/polly.py`:

```python
def _build_system_prompt(self, context: Optional[Dict] = None) -> str:
    """Build system prompt with learned patterns."""
    base_prompt = f"""You are Polly, {self.user_name}'s personal AI assistant.

You have deep knowledge of {self.user_name}'s work across five domains:

**Sigils** (Code & Infrastructure): Docker, NAS, automation, Python, Rust, JavaScript, Lua
**Signals** (Audio & Synthesis): norns, SuperCollider, audio programming, MIDI, synthesis
**Scrolls** (Writing & Pedagogy): Essays, notes, education, documentation
**Glyphs** (Visual Design): UI/UX, design systems, visual work
**Grids** (Systems Thinking): Frameworks, mental models, systems architecture

You understand {self.user_name}'s:
- Coding patterns and preferences
- Learning style and knowledge connections
- Workflow and context-switching habits
- Project structures and architectures
"""
    
    # Add learned patterns section
    if self.pattern_learner:
        relevant_patterns = self._get_patterns_for_prompt(context)
        
        if relevant_patterns:
            pattern_section = f"\n\n**Learned Patterns:**\n"
            pattern_section += f"You've noticed these patterns in how {self.user_name} works:\n\n"
            
            for pattern in relevant_patterns[:5]:  # Top 5 patterns
                pattern_section += f"- **{pattern.name}**: {pattern.description}\n"
                if pattern.pattern_type == "query":
                    pattern_section += f"  (You ask this type of question often)\n"
                elif pattern.pattern_type == "code":
                    pattern_section += f"  (You use this pattern in your code)\n"
                elif pattern.pattern_type == "conceptual":
                    pattern_section += f"  (You connect these concepts frequently)\n"
                elif pattern.pattern_type == "workflow":
                    pattern_section += f"  (This is how you typically work)\n"
            
            pattern_section += "\nUse these patterns to anticipate needs and provide more relevant responses.\n"
            base_prompt += pattern_section
    
    return base_prompt

def _get_patterns_for_prompt(self, context: Optional[Dict] = None, limit: int = 5) -> List[Pattern]:
    """Get most relevant patterns for current context."""
    if not self.pattern_learner:
        return []
    
    # Get all patterns
    all_patterns = list(self.pattern_learner.patterns.values())
    
    if not all_patterns:
        return []
    
    # Score patterns
    scored = []
    for pattern in all_patterns:
        score = 0.0
        
        # Confidence weight
        score += pattern.confidence * 3
        
        # Occurrence weight
        score += min(pattern.occurrences / 10.0, 2.0)
        
        # Recency weight (patterns used in last 7 days get boost)
        days_ago = (datetime.now() - pattern.last_seen).days
        if days_ago <= 7:
            score += 2.0
        elif days_ago <= 30:
            score += 1.0
        
        # Context match (if provided)
        if context:
            domain = context.get('domain')
            if domain and domain in pattern.domains:
                score += 2.0
        
        scored.append((score, pattern))
    
    # Sort by score
    scored.sort(key=lambda x: x[0], reverse=True)
    
    return [pattern for score, pattern in scored[:limit]]

async def query(self, user_query: str, **kwargs):
    """Enhanced query with pattern context."""
    # Extract domain and other context
    domains = self.domain_engine.detect(user_query)
    
    # Build context for patterns and mental models
    context = {
        'domain': domains[0].value if domains else None,
        'category': kwargs.get('category'),
        'keywords': self._extract_keywords(user_query)
    }
    
    # Build system prompt with patterns
    system_prompt = self._build_system_prompt(context)
    
    # Record query pattern
    if self.pattern_learner:
        try:
            self.pattern_learner.record_query(user_query, domains)
            self.pattern_learner.save_patterns()
            logger.info(f"Recorded query pattern")
        except Exception as e:
            logger.error(f"Failed to record pattern: {e}")
    
    # ... rest of query logic ...

def _extract_keywords(self, text: str) -> List[str]:
    """Extract keywords from text."""
    words = re.findall(r'\b[a-z]{4,}\b', text.lower())
    return list(set(words))
```

**Testing:**
- Use Polly with learned patterns
- Check if responses feel more personalized
- Verify patterns are being applied

---

### Step 6: Pattern Visualization UI (Days 11-12)

**Goal:** Show patterns in Settings UI

Update `/electron-app/src/renderer/index.html`:

Add to Settings tab:

```html
<div class="settings-section">
  <h3>
    <i data-lucide="brain"></i>
    Learned Patterns
  </h3>
  
  <p class="settings-description">
    Polly learns from your work patterns to provide better responses over time.
  </p>
  
  <div class="patterns-stats">
    <div class="stat-card">
      <div class="stat-value" id="pattern-count">0</div>
      <div class="stat-label">Patterns Discovered</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="pattern-queries">0</div>
      <div class="stat-label">Query Patterns</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="pattern-code">0</div>
      <div class="stat-label">Code Patterns</div>
    </div>
    <div class="stat-card">
      <div class="stat-value" id="pattern-concepts">0</div>
      <div class="stat-label">Concept Connections</div>
    </div>
  </div>
  
  <div class="patterns-list" id="patterns-list">
    <!-- Populated dynamically -->
  </div>
  
  <div class="settings-actions">
    <button class="btn btn-secondary" id="btn-refresh-patterns">
      <i data-lucide="refresh-cw"></i>
      Refresh Patterns
    </button>
    <button class="btn btn-danger" id="btn-reset-patterns">
      <i data-lucide="trash-2"></i>
      Reset Pattern Learning
    </button>
  </div>
</div>
```

Update `/electron-app/src/renderer/app.js`:

```javascript
// Pattern Learning Functions

async function loadPatterns() {
  try {
    const response = await fetch('http://localhost:11436/polly/patterns/list');
    const data = await response.json();
    
    // Update stats
    document.getElementById('pattern-count').textContent = data.total;
    document.getElementById('pattern-queries').textContent = 
      data.patterns.filter(p => p.pattern_type === 'query').length;
    document.getElementById('pattern-code').textContent = 
      data.patterns.filter(p => p.pattern_type === 'code').length;
    document.getElementById('pattern-concepts').textContent = 
      data.patterns.filter(p => p.pattern_type === 'conceptual').length;
    
    // Display patterns
    const patternsList = document.getElementById('patterns-list');
    patternsList.innerHTML = '';
    
    // Group by type
    const byType = {
      query: [],
      code: [],
      conceptual: [],
      workflow: []
    };
    
    data.patterns.forEach(p => {
      if (byType[p.pattern_type]) {
        byType[p.pattern_type].push(p);
      }
    });
    
    // Render each group
    for (const [type, patterns] of Object.entries(byType)) {
      if (patterns.length === 0) continue;
      
      const section = document.createElement('div');
      section.className = 'pattern-type-section';
      
      const header = document.createElement('h4');
      header.textContent = type.charAt(0).toUpperCase() + type.slice(1) + ' Patterns';
      section.appendChild(header);
      
      patterns.forEach(pattern => {
        const card = document.createElement('div');
        card.className = 'pattern-card';
        card.innerHTML = `
          <div class="pattern-header">
            <span class="pattern-name">${pattern.name}</span>
            <span class="pattern-confidence">
              ${(pattern.confidence * 100).toFixed(0)}% confidence
            </span>
          </div>
          <div class="pattern-description">${pattern.description}</div>
          <div class="pattern-meta">
            <span><i data-lucide="hash"></i> ${pattern.occurrences} occurrences</span>
            <span><i data-lucide="calendar"></i> Last seen: ${formatDate(pattern.last_seen)}</span>
            <span><i data-lucide="tag"></i> ${pattern.domains.join(', ')}</span>
          </div>
        `;
        section.appendChild(card);
      });
      
      patternsList.appendChild(section);
    }
    
    lucide.createIcons();
  } catch (error) {
    console.error('Failed to load patterns:', error);
  }
}

// Refresh patterns button
document.getElementById('btn-refresh-patterns')?.addEventListener('click', () => {
  loadPatterns();
});

// Reset patterns button
document.getElementById('btn-reset-patterns')?.addEventListener('click', async () => {
  if (confirm('This will delete all learned patterns. Are you sure?')) {
    try {
      await fetch('http://localhost:11436/polly/patterns/reset', {
        method: 'POST'
      });
      loadPatterns();
      showNotification('Pattern learning reset successfully');
    } catch (error) {
      showNotification('Failed to reset patterns', 'error');
    }
  }
});

// Load patterns on settings tab open
// (Add to existing tab switching logic)
```

Add CSS to `/electron-app/src/renderer/styles/main.css`:

```css
/* Pattern Learning Styles */

.patterns-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  padding: 1.5rem;
  text-align: center;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pattern-type-section {
  margin-bottom: 2rem;
}

.pattern-type-section h4 {
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: var(--color-text);
  border-bottom: 2px solid var(--color-border);
  padding-bottom: 0.5rem;
}

.pattern-card {
  background: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  padding: 1rem;
  margin-bottom: 1rem;
}

.pattern-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.pattern-name {
  font-weight: bold;
  color: var(--color-text);
}

.pattern-confidence {
  font-size: 0.875rem;
  color: var(--color-accent);
  font-weight: bold;
}

.pattern-description {
  color: var(--color-text-secondary);
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.pattern-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.pattern-meta span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pattern-meta i {
  width: 14px;
  height: 14px;
}
```

**Testing:**
- Open Settings → Learned Patterns
- Verify stats show correctly
- Check pattern cards render
- Test refresh and reset buttons

---

### Step 7: Testing & Validation (Days 13-14)

**Goal:** Comprehensive testing of entire system

#### Day 13: Unit & Integration Tests

Create test scripts:

**`/scripts/test_pattern_storage.py`:**

```python
#!/usr/bin/env python3
"""Test pattern storage functionality."""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner

def test_storage():
    """Test that patterns save and load correctly."""
    print("Testing pattern storage...")
    
    # Create pattern learner
    storage_path = Path.home() / ".polly" / "test_patterns.json"
    storage_path.unlink(missing_ok=True)  # Clean start
    
    learner = PatternLearner(storage_path)
    
    # Record some queries
    learner.record_query("How do I use Docker with Python?", ["sigils"])
    learner.record_query("Explain norns in SuperCollider", ["signals"])
    learner.record_query("Write an essay about pedagogy", ["scrolls"])
    
    # Save
    learner.save_patterns()
    
    # Verify file exists
    assert storage_path.exists(), "Storage file not created"
    
    # Load in new instance
    learner2 = PatternLearner(storage_path)
    
    # Verify patterns loaded
    assert len(learner2.query_history) == 3, f"Expected 3 queries, got {len(learner2.query_history)}"
    
    print("✓ Storage test passed")
    
    # Cleanup
    storage_path.unlink()

if __name__ == "__main__":
    test_storage()
```

**`/scripts/test_query_patterns.py`:**

```python
#!/usr/bin/env python3
"""Test query pattern detection."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.patterns import PatternLearner

def test_query_templates():
    """Test query template extraction."""
    print("Testing query templates...")
    
    storage_path = Path.home() / ".polly" / "test_patterns.json"
    storage_path.unlink(missing_ok=True)
    
    learner = PatternLearner(storage_path)
    
    # Test various query patterns
    test_queries = [
        ("How do I use Docker with Python?", "How do I {action} {thing} with {tool}?"),
        ("What is the best way to structure React components?", "What is the best way to {action} {thing}?"),
        ("Explain async functions in JavaScript", "Explain {concept} in {context}"),
        ("Write a function that parses markdown", "Write a {thing} that {action}"),
    ]
    
    for query, expected_template in test_queries:
        template, fills = learner._extract_query_template(query)
        print(f"  Query: {query}")
        print(f"  Template: {template}")
        print(f"  Expected: {expected_template}")
        assert template == expected_template, f"Template mismatch"
        print("  ✓")
    
    print("✓ Query template test passed")
    
    storage_path.unlink(missing_ok=True)

if __name__ == "__main__":
    test_query_templates()
```

**`/scripts/test_code_patterns.py`:**

```python
#!/usr/bin/env python3
"""Test code pattern extraction."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from learners.code_patterns import CodePatternExtractor

def test_python_patterns():
    """Test Python code pattern extraction."""
    print("Testing Python patterns...")
    
    sample_code = """
import asyncio
from typing import List

class DataProcessor:
    async def process(self, data: List[str]):
        try:
            results = []
            for item in data:
                result = await self.process_item(item)
                results.append(result)
            return results
        except ValueError as e:
            print(f"Error: {e}")
            raise
    """
    
    extractor = CodePatternExtractor()
    patterns = extractor.extract_from_python(sample_code)
    
    print(f"  Found {len(patterns)} patterns:")
    for p in patterns:
        print(f"    - {p['pattern']}: {p.get('details', p.get('count', 'N/A'))}")
    
    # Check we found key patterns
    pattern_types = [p['type'] for p in patterns]
    assert 'imports' in pattern_types, "Should detect imports"
    assert 'async' in pattern_types, "Should detect async"
    assert 'error_handling' in pattern_types, "Should detect error handling"
    
    print("✓ Python pattern test passed")

def test_javascript_patterns():
    """Test JavaScript pattern extraction."""
    print("Testing JavaScript patterns...")
    
    sample_code = """
import React from 'react';

const MyComponent = ({ data }) => {
  const handleClick = async () => {
    const result = await fetch('/api/data')
      .then(res => res.json())
      .catch(err => console.error(err));
  };
  
  return <div onClick={handleClick}>{data}</div>;
};
    """
    
    extractor = CodePatternExtractor()
    patterns = extractor.extract_from_javascript(sample_code)
    
    print(f"  Found {len(patterns)} patterns:")
    for p in patterns:
        print(f"    - {p['pattern']}")
    
    pattern_types = [p['type'] for p in patterns]
    assert 'framework' in pattern_types, "Should detect React"
    
    print("✓ JavaScript pattern test passed")

if __name__ == "__main__":
    test_python_patterns()
    test_javascript_patterns()
```

#### Day 14: Real-World Usage Test

1. **Use Polly naturally for 2-3 hours**
   - Work on code projects
   - Have conversations across domains
   - Ask varied questions

2. **Check patterns dashboard**
   - Open Settings → Learned Patterns
   - Verify patterns make sense
   - Check confidence scores reasonable
   - Review occurrence counts

3. **Verify response quality**
   - Do responses feel more personalized?
   - Are patterns being applied?
   - Check system prompts include patterns

4. **Performance testing**
   - Pattern learning doesn't slow queries
   - UI loads quickly with 20+ patterns
   - No memory leaks

---

## API Endpoints

### GET `/polly/patterns/list`

Returns all learned patterns.

**Response:**
```json
{
  "total": 23,
  "patterns": [
    {
      "id": "query_template_1234",
      "name": "How do I use X with Y?",
      "description": "You frequently ask how to integrate tools",
      "pattern_type": "query",
      "domains": ["sigils"],
      "occurrences": 12,
      "confidence": 0.85,
      "first_seen": "2026-01-15T10:30:00",
      "last_seen": "2026-01-21T14:20:00",
      "metadata": {}
    }
  ]
}
```

### POST `/polly/patterns/learn-from-conversation`

Triggers conceptual pattern learning from a conversation.

**Request:**
```json
{
  "conversation_id": "conv_123",
  "category": "sigils",
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

**Response:**
```json
{
  "patterns_learned": 2,
  "new_patterns": ["concept_pair_docker_python"]
}
```

### POST `/polly/patterns/reset`

Clears all learned patterns.

**Response:**
```json
{
  "success": true,
  "message": "All patterns cleared"
}
```

### GET `/polly/patterns/stats`

Returns pattern statistics.

**Response:**
```json
{
  "total_patterns": 23,
  "by_type": {
    "query": 8,
    "code": 6,
    "conceptual": 5,
    "workflow": 4
  },
  "total_occurrences": 156,
  "learning_since": "2026-01-15T08:00:00",
  "avg_confidence": 0.72
}
```

---

## Files to Create/Modify

### New Files

- `/learners/code_patterns.py` (300 lines) - AST-based code pattern extraction
- `/learners/work_patterns.py` (200 lines) - Work habit detection
- `/scripts/test_pattern_storage.py` (100 lines) - Storage tests
- `/scripts/test_query_patterns.py` (100 lines) - Query pattern tests
- `/scripts/test_code_patterns.py` (100 lines) - Code pattern tests

### Modified Files

- `/learners/patterns.py` - Fix storage, add methods (+200 lines)
- `/core/polly.py` - Pattern-informed prompts (+150 lines)
- `/interfaces/server.py` - Pattern API endpoints (+150 lines)
- `/electron-app/src/renderer/index.html` - Pattern settings UI (+80 lines)
- `/electron-app/src/renderer/app.js` - Pattern UI logic (+200 lines)
- `/electron-app/src/renderer/styles/main.css` - Pattern styles (+100 lines)
- `/electron-app/src/main/conversation-manager.js` - Pattern learning hook (+30 lines)

**Total:** ~1,310 new lines, ~910 modified lines

---

## Success Criteria

- ✅ Pattern storage works correctly (`~/.polly/patterns.json` exists and persists)
- ✅ Patterns recorded after each query
- ✅ Query templates extracted accurately
- ✅ Code patterns detected from indexed files
- ✅ Conceptual connections learned from conversations
- ✅ Work patterns detected (time, context switches, sessions)
- ✅ Patterns used in system prompts
- ✅ Pattern UI shows all learned patterns
- ✅ Responses become more personalized over time
- ✅ System performance not impacted
- ✅ All 4 pattern types working (code, query, conceptual, workflow)
- ✅ 10+ patterns learned after 1 week of use
- ✅ Pattern confidence scores reasonable (0.3-0.9 range)
- ✅ Test suite passing

---

## Next Steps

After Phase 13 is complete, proceed to:

**Phase 14: Mental Models System** (3-5 days)

See `PHASE14_MENTAL_MODELS.md` for details.

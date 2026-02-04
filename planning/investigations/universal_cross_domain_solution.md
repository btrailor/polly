# Universal Cross-Domain Detection Solution

**Updated:** January 29, 2026  
**Issue:** Keyword-only matching fails for cross-domain topics

---

## The Problem with Keyword-Only Matching

**Current system:**
```python
def matches_content(self, content: str) -> float:
    content_lower = content.lower()
    matches = sum(1 for kw in self.keywords if kw.lower() in content_lower)
    return min(matches / max(len(self.keywords), 1), 1.0)
```

**Problem:** 
- Query "How do I program Monome Norns in Lua?" matches NO Sigils keywords → score 0.0
- Can't boost a domain that scores 0.0
- User-specific keyword additions don't solve this universally

---

## Universal Solution: Content-Based Domain Detection

### Approach: Use Query Intent + Context Clues

Instead of just counting keywords, analyze query structure and intent:

```python
def matches_content_enhanced(self, content: str, context: Optional[Dict] = None) -> float:
    """
    Enhanced domain matching using:
    1. Keyword matching (existing)
    2. Query intent detection (new)
    3. Context clues (new)
    """
    score = 0.0
    content_lower = content.lower()
    
    # 1. Keyword matching (existing method)
    keyword_matches = sum(1 for kw in self.keywords if kw.lower() in content_lower)
    score += keyword_matches / max(len(self.keywords), 1)
    
    # 2. Intent-based detection
    intent_score = self._detect_domain_intent(content_lower)
    score += intent_score * 0.3  # Weight intent at 30%
    
    # 3. Context clues (file patterns mentioned in query)
    if context and 'query_mentions_patterns' in context:
        pattern_score = self._match_mentioned_patterns(context['query_mentions_patterns'])
        score += pattern_score * 0.2  # Weight patterns at 20%
    
    return min(score, 1.0)

def _detect_domain_intent(self, content: str) -> float:
    """
    Detect domain relevance from query intent, not just keywords.
    Universal - works for any domain.
    """
    score = 0.0
    
    # Programming intent indicators (for Sigils-like domains)
    programming_intents = [
        'how do i code', 'how do i program', 'how to implement',
        'write a script', 'build a', 'develop a', 'debug', 'refactor',
        'api for', 'function to', 'class that', 'library for'
    ]
    
    # Check if domain keywords suggest it's code-related
    is_code_domain = any(kw in self.keywords for kw in 
                        ['code', 'program', 'script', 'api', 'function', 'class'])
    
    if is_code_domain:
        for intent in programming_intents:
            if intent in content:
                score += 0.3  # Strong signal of programming intent
                break
    
    # Similar logic for other domain types
    # Audio/synthesis intent
    audio_intents = ['synthesis', 'audio', 'sound', 'music', 'play', 'trigger']
    is_audio_domain = any(kw in self.keywords for kw in audio_intents)
    
    if is_audio_domain:
        for intent in audio_intents:
            if intent in content:
                score += 0.2
                break
    
    return min(score, 1.0)

def _match_mentioned_patterns(self, mentioned_patterns: List[str]) -> float:
    """
    Check if query mentions file types/patterns that match this domain.
    Universal - works for any domain's pattern list.
    """
    # Query: "program Norns in Lua" mentions "lua"
    # Sigils patterns include "*.lua"
    # This should boost Sigils even without keyword match
    
    for pattern in self.patterns:
        pattern_ext = pattern.replace('*', '').replace('.', '')
        for mentioned in mentioned_patterns:
            if pattern_ext in mentioned.lower():
                return 1.0
    
    return 0.0
```

---

## Implementation Strategy

### Phase 1: Enhanced Query Preprocessing (Universal)

**Before domain detection, extract query metadata:**

```python
def preprocess_query(query: str) -> Dict:
    """
    Extract metadata from query before domain detection.
    Universal - works for any query/domain.
    """
    query_lower = query.lower()
    
    return {
        'intent_signals': {
            'programming': any(phrase in query_lower for phrase in 
                             ['how do i code', 'how do i program', 'write', 'build', 
                              'implement', 'debug', 'api', 'function']),
            'audio': any(phrase in query_lower for phrase in
                        ['audio', 'sound', 'music', 'synthesis', 'play']),
            'writing': any(phrase in query_lower for phrase in
                          ['write', 'document', 'essay', 'notes', 'journal']),
            'design': any(phrase in query_lower for phrase in
                         ['design', 'ui', 'layout', 'mockup', 'prototype']),
            'systems': any(phrase in query_lower for phrase in
                          ['framework', 'mental model', 'systems', 'pattern'])
        },
        'mentioned_technologies': extract_technologies(query),  # "Lua", "Python", etc.
        'mentioned_tools': extract_tools(query),  # "Norns", "React", etc.
    }
```

### Phase 2: Intent-Based Scoring (Universal)

**Each domain can specify its "intent signals":**

```yaml
# In domain_config.yaml (Phase 1.5 extension)
domains:
  sigils:
    keywords: [...]
    patterns: ["*.py", "*.rs", "*.lua"]
    # NEW: Intent signals
    intent_signals:
      - programming
      - coding
      - development
    intent_boost: 0.3  # How much to boost when intent detected
  
  signals:
    keywords: [...]
    patterns: ["*.scd", "*.pd"]
    intent_signals:
      - audio
      - synthesis
      - sound
    intent_boost: 0.3
```

### Phase 3: Technology/Tool Recognition (Universal)

**Detect mentioned technologies and match to domains:**

```python
# Universal technology matching
# When "Lua" mentioned, check which domains have "*.lua" patterns
# When "Python" mentioned, check which domains have "*.py" patterns

def match_technologies_to_domains(mentioned_techs: List[str]) -> Dict[DomainType, float]:
    """
    Universal - works for any domain configuration.
    """
    boosts = {}
    
    for domain_type, domain in domains.items():
        for tech in mentioned_techs:
            # Check if domain's patterns match this technology
            tech_lower = tech.lower()
            for pattern in domain.patterns:
                pattern_tech = pattern.replace('*', '').replace('.', '')
                if tech_lower == pattern_tech or tech_lower in pattern_tech:
                    boosts[domain_type] = boosts.get(domain_type, 0) + 0.2
    
    return boosts
```

---

## Why This Is Universal

1. **Intent Detection:** Works for any domain type
   - Detects "programming" intent regardless of specific language
   - Detects "audio" intent regardless of specific tool
   - Detects "writing/design/systems" intent similarly

2. **Technology Matching:** Uses existing pattern definitions
   - "Lua" mentioned → matches domains with `*.lua` patterns
   - "Python" mentioned → matches domains with `*.py` patterns
   - Works for ANY technology/pattern combination

3. **No Hardcoded Keywords:** Doesn't require adding "lua" to Sigils
   - Instead: detects "program" intent + "Lua" mention + Sigils has `*.lua` pattern
   - Result: Sigils gets boosted even without "lua" keyword

4. **User-Configurable:** Phase 1.5 extension
   - Users define their domain patterns (already done)
   - Optionally define intent signals (new)
   - System automatically matches technologies to patterns (universal)

---

## Example: How It Would Work

### Query: "How do I program Monome Norns in Lua?"

**Step 1: Preprocess Query**
```python
{
    'intent_signals': {'programming': True},  # "how do i program"
    'mentioned_technologies': ['Lua'],
    'mentioned_tools': ['Monome', 'Norns']
}
```

**Step 2: Score Domains**

**Sigils:**
- Keyword matches: 0 → score 0.0
- Intent boost: programming=True + domain is code-related → +0.3
- Technology boost: "Lua" matches `*.lua` pattern → +0.2
- **Total: 0.5** ✅ Now detectable!

**Signals:**
- Keyword matches: 2 (norns, monome) → score 0.074
- Intent boost: None
- Technology boost: None
- **Total: 0.074**

**Step 3: Cross-Domain Boost**
- Both domains score >0.03 → multi-domain detected
- Both included in RAG search ✅

---

## Implementation Plan

### Quick Win (2-3 hours): Technology Pattern Matching

**Add to `domains.py`:**
```python
def detect_mentioned_technologies(query: str) -> List[str]:
    """Extract technology mentions from query."""
    # Simple regex for common patterns
    # Can be enhanced with NLP later
    pass

def boost_domains_by_technology(scores: Dict, mentioned_techs: List[str]) -> Dict:
    """Boost domains whose patterns match mentioned technologies."""
    pass
```

**Impact:** Immediately helps queries like "program in Lua" detect Sigils

### Medium Term (4-6 hours): Intent-Based Detection

**Add intent signal configuration to Phase 1.5 domain config**
**Implement intent detection and boosting**

**Impact:** Helps ANY programming/audio/design query detect correct domains

### Long Term (1-2 days): Full Content Analysis

**Use LLM to analyze query intent**
**Extract entities and match to domain characteristics**

**Impact:** Most accurate, handles complex cross-domain queries

---

## Recommendation

**Implement in this order:**

1. **NOW (15 min):** Soften collection skipping threshold
   - Prevents aggressive filtering
   - No code changes to domain detection needed
   - Universal fix

2. **TODAY (1 hour):** Cross-domain boost
   - Helps when both domains score >0
   - Universal algorithm

3. **THIS WEEK (2-3 hours):** Technology pattern matching
   - "Lua" → matches `*.lua` domains
   - Universal - uses existing pattern lists
   - **This solves the Norns issue universally**

4. **NEXT WEEK (4-6 hours):** Intent-based detection
   - "program" → boosts code-related domains
   - User-configurable via domain config
   - **Most comprehensive universal solution**

---

## Testing for Universality

**Test with completely different domains:**
- Biology + Data Science: "analyze genomic sequences in Python"
- Medicine + Data Science: "train neural network for diagnosis"  
- Education + Systems: "framework for teaching complexity"
- Design + Code: "implement Figma designs in React"

**Success criteria:**
- All cross-domain queries detect both relevant domains (score >0.03)
- No domain-specific hardcoding required
- Works with user-defined domains from Phase 1.5

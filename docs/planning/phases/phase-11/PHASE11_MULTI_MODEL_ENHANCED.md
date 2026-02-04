# Phase 11: Multi-Model Selection + Intelligent Routing

**Status:** Planned  
**Duration:** 10-14 days  
**Prerequisites:** Phase 1.5 (Domain Configuration), Phase 2 (RAG), Phase 6 (GitHub Copilot), Phase 7 (GitHub Integration)  
**Enables:** Phase 16c (AI Note Creation), Phase 17 (Code Workspace Chat)

---

## Overview

Phase 11 extends Polly's multi-model capabilities with an intelligent routing system that automatically selects between local and cloud LLMs based on confidence in the available knowledge. Rather than always defaulting to expensive cloud models, Polly evaluates the quality of RAG results and local model outputs, only escalating to cloud providers when necessary.

### Evolution from Original Phase 11

**Original Phase 11** focused on basic multi-model selection:
- User manually switches between models
- Basic provider integration (Claude, GPT, Copilot, Local)
- Simple fallback logic

**Enhanced Phase 11** adds intelligent automation:
- **Three-layer confidence system** evaluates query answering capability
- **Adaptive thresholds** that learn to trust local models over time
- **Meta-query generation** when local knowledge is insufficient
- **Token budget management** across multiple cloud providers
- **Draft notes review queue** for AI-generated content

This transforms Polly from a "model switcher" into an intelligent system that knows when it needs help.

---

## Goals

1. **Intelligent local/cloud routing** - Automatically choose the right model based on confidence
2. **Confidence-based decision making** - Three-layer system evaluates RAG quality and output quality
3. **Adaptive learning** - System improves over time, learning when to trust local models
4. **Knowledge gap filling** - Generate comprehensive notes when local knowledge is insufficient
5. **Cost optimization** - Minimize cloud API usage without sacrificing quality
6. **Token budget management** - Track usage across providers, fallback when limits reached
7. **User review and control** - All AI-generated notes reviewed before adding to knowledge base
8. **Transparency** - Show confidence scores and routing decisions to users

---

## Three-Layer Confidence System

The intelligent routing system evaluates confidence at three levels:

### Layer 1: Pre-Flight Check (RAG Quality Assessment)

**Purpose:** Evaluate whether we have enough relevant knowledge to answer locally

**When:** Before sending query to local LLM

**Metrics:**

1. **Chunk Retrieval Count**
   - How many relevant chunks were retrieved?
   - <3 chunks = low confidence
   - 3-7 chunks = medium confidence
   - 8+ chunks = high confidence

2. **Semantic Similarity Scores**
   - What's the cosine similarity of top chunks to query?
   - Top score <0.5 = poor match
   - Top score 0.5-0.7 = moderate match
   - Top score >0.7 = strong match
   - Average of top-5 also considered

3. **Query-Domain Alignment**
   - Does the query match any domain's auto-tag rules well?
   - Uses Phase 1.5 domain configuration
   - Strong domain match = higher confidence

4. **Coverage Breadth**
   - Are results from multiple domains or just one?
   - Multiple domains = more comprehensive knowledge
   - Single domain might indicate narrow/incomplete coverage

5. **Chunk Recency**
   - How recent are the matching chunks?
   - Recent chunks (last 30 days) = more relevant
   - Old chunks might be outdated

**Scoring Algorithm:**

```python
def calculate_preflight_confidence(
    query: str,
    chunks: list[Chunk],
    domains: list[Domain]
) -> float:
    """
    Calculate pre-flight confidence score (0.0 - 1.0).
    
    Returns confidence that local model can answer query well.
    """
    score = 0.0
    
    # 1. Chunk count (max 25 points)
    chunk_count = len(chunks)
    if chunk_count >= 8:
        score += 0.25
    elif chunk_count >= 3:
        score += 0.15
    elif chunk_count >= 1:
        score += 0.05
    
    # 2. Semantic similarity (max 30 points)
    if chunks:
        top_similarity = chunks[0].similarity_score
        avg_top5 = mean([c.similarity_score for c in chunks[:5]])
        
        if top_similarity >= 0.7:
            score += 0.20
        elif top_similarity >= 0.5:
            score += 0.10
        
        if avg_top5 >= 0.6:
            score += 0.10
        elif avg_top5 >= 0.4:
            score += 0.05
    
    # 3. Domain alignment (max 20 points)
    domain_matches = match_query_to_domains(query, domains)
    if domain_matches:
        best_match_score = max(domain_matches.values())
        score += 0.20 * best_match_score
    
    # 4. Coverage breadth (max 15 points)
    unique_domains = set(c.domain_id for c in chunks)
    if len(unique_domains) >= 3:
        score += 0.15
    elif len(unique_domains) >= 2:
        score += 0.10
    elif len(unique_domains) >= 1:
        score += 0.05
    
    # 5. Recency (max 10 points)
    if chunks:
        recent_chunks = [c for c in chunks if is_recent(c, days=30)]
        recency_ratio = len(recent_chunks) / len(chunks)
        score += 0.10 * recency_ratio
    
    return min(score, 1.0)

def match_query_to_domains(query: str, domains: list[Domain]) -> dict:
    """
    Score how well query matches each domain's auto-tag rules.
    Returns {domain_id: score} mapping.
    """
    query_lower = query.lower()
    scores = {}
    
    for domain in domains:
        matches = sum(1 for keyword in domain.autoTagRules if keyword in query_lower)
        if domain.autoTagRules:
            scores[domain.id] = matches / len(domain.autoTagRules)
    
    return scores
```

**Decision Rule:**

```python
if preflight_confidence < PREFLIGHT_THRESHOLD:
    # Skip local model entirely, go straight to cloud
    return route_to_cloud(query, reason="insufficient_knowledge")
else:
    # Try local model first
    return route_to_local(query)
```

**Initial threshold:** 0.60 (60% confidence required)
**After 50 queries:** 0.50
**After 200 queries:** 0.40

---

### Layer 2: Output Analysis (Response Quality Check)

**Purpose:** Evaluate the quality of the local model's response

**When:** After local LLM generates response

**Metrics:**

1. **Uncertainty Markers**
   - Count hedge words and phrases
   - Common markers: "maybe", "perhaps", "might", "possibly", "I think", "I'm not sure", "it's unclear"
   - High uncertainty = low confidence

2. **Length Adequacy**
   - Is the response substantial enough?
   - <50 words = very weak
   - 50-100 words = weak
   - 100-200 words = adequate
   - 200+ words = strong

3. **Factual Density**
   - Does response contain specific facts, examples, code?
   - Count: numbers, code blocks, specific names, concrete examples
   - More facts = higher confidence

4. **Contradiction Detection**
   - Does response contradict itself?
   - Simple heuristic: conflicting statements
   - "Yes... but no..." patterns

5. **Hallucination Signals**
   - Red flags indicating made-up content
   - Fake citations ("According to [non-existent paper]")
   - Invalid URLs
   - Made-up function names (if code-related)
   - Overly specific claims without source

**Scoring Algorithm:**

```python
def calculate_output_confidence(response: str, query: str) -> float:
    """
    Analyze local model's response quality (0.0 - 1.0).
    
    Returns confidence that response is accurate and helpful.
    """
    score = 1.0  # Start optimistic, subtract for issues
    
    # 1. Uncertainty markers (deduct up to 30 points)
    uncertainty_markers = [
        "maybe", "perhaps", "might", "possibly", "probably",
        "i think", "i'm not sure", "unclear", "uncertain",
        "i don't know", "not certain", "could be"
    ]
    response_lower = response.lower()
    marker_count = sum(response_lower.count(marker) for marker in uncertainty_markers)
    score -= min(0.30, marker_count * 0.10)
    
    # 2. Length adequacy (deduct up to 20 points)
    word_count = len(response.split())
    if word_count < 50:
        score -= 0.20
    elif word_count < 100:
        score -= 0.10
    elif word_count < 200:
        score -= 0.05
    
    # 3. Factual density (add up to 20 points, capped at 1.0 overall)
    factual_indicators = count_factual_indicators(response)
    fact_bonus = min(0.20, factual_indicators * 0.04)
    score += fact_bonus
    
    # 4. Contradiction detection (deduct 25 points)
    if has_contradictions(response):
        score -= 0.25
    
    # 5. Hallucination signals (deduct 30 points each)
    hallucination_count = detect_hallucinations(response)
    score -= hallucination_count * 0.30
    
    return max(0.0, min(1.0, score))

def count_factual_indicators(text: str) -> int:
    """Count indicators of factual content."""
    count = 0
    
    # Code blocks
    count += text.count("```")
    
    # Numbers and measurements
    count += len(re.findall(r'\b\d+(?:\.\d+)?(?:%|px|ms|MB|GB)?\b', text))
    
    # Specific examples ("For example", "such as")
    count += text.lower().count("for example")
    count += text.lower().count("such as")
    count += text.lower().count("e.g.")
    
    # Function/class names (PascalCase, camelCase, snake_case)
    count += len(re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text))  # PascalCase
    count += len(re.findall(r'\b[a-z]+_[a-z_]+\b', text))  # snake_case
    
    return count

def has_contradictions(text: str) -> bool:
    """Simple contradiction detection."""
    # Look for patterns like "Yes... but no..." or "True... however false"
    contradiction_patterns = [
        r'\byes\b.*\bno\b',
        r'\btrue\b.*\bfalse\b',
        r'\bshould\b.*\bshouldn\'t\b',
        r'\bcan\b.*\bcan\'t\b',
        r'\bis\b.*\bisn\'t\b'
    ]
    
    text_lower = text.lower()
    for pattern in contradiction_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

def detect_hallucinations(text: str) -> int:
    """Detect likely hallucinations."""
    count = 0
    
    # Fake citations
    if re.search(r'according to .* \(\d{4}\)', text, re.IGNORECASE):
        # Check if citation looks suspicious (common fake patterns)
        if any(fake in text.lower() for fake in ["smith et al", "johnson et al", "study by"]):
            count += 1
    
    # Invalid URLs (common patterns)
    urls = re.findall(r'https?://[^\s]+', text)
    for url in urls:
        # Check for obviously fake domains
        if any(fake in url.lower() for fake in ["example.com", "test.com", "foo.bar"]):
            count += 1
    
    # Overly specific claims without source
    overly_specific_patterns = [
        r'\b\d{2,3}\.?\d*%\b',  # Specific percentages
        r'\b\d+,\d{3,}\b'  # Large specific numbers
    ]
    specific_claims = sum(len(re.findall(p, text)) for p in overly_specific_patterns)
    if specific_claims >= 3 and "source" not in text.lower() and "according to" not in text.lower():
        count += 1
    
    return count
```

**Decision Rule:**

```python
if output_confidence < OUTPUT_THRESHOLD:
    # Generate meta-query for cloud
    meta_query = generate_meta_query(query, response, chunks)
    return route_to_cloud_with_meta_query(meta_query)
else:
    # Accept local response
    return accept_local_response(response)
```

**Initial threshold:** 0.70 (70% confidence required)
**After 50 queries:** 0.65
**After 200 queries:** 0.60

---

### Layer 3: Historical Learning (Pattern Recognition)

**Purpose:** Learn from past successes and failures to improve routing decisions

**When:** Continuously, after each query

**Metrics:**

1. **Query Clustering**
   - Group semantically similar queries
   - Track success/failure rates per cluster
   - Identify query types that work well locally vs need cloud

2. **Success Rates by Query Type**
   - Classify queries: factual, procedural, analytical, creative
   - Track which types local model handles well
   - Adjust thresholds accordingly

3. **User Corrections (Implicit Feedback)**
   - Did user edit the response?
   - Did user reject and re-ask?
   - Did user explicitly override routing decision?

4. **RAG Gap Patterns**
   - Which topics consistently have low pre-flight confidence?
   - These are knowledge gaps that need filling
   - Generate proactive meta-queries to fill gaps

5. **Threshold Adjustment**
   - Gradually adjust pre-flight and output thresholds
   - If local model performs well, lower thresholds (trust more)
   - If cloud is needed often, maintain higher thresholds

**Learning Algorithm:**

```python
class ConfidenceLearner:
    """
    Learns from query history to improve routing decisions.
    """
    
    def __init__(self):
        self.query_history = []
        self.cluster_performance = {}
        self.query_type_performance = {}
        self.preflight_threshold = 0.60
        self.output_threshold = 0.70
    
    def record_query(self, query: QueryResult):
        """Record query and outcome for learning."""
        self.query_history.append(query)
        
        # Update cluster performance
        cluster_id = self.get_cluster_id(query.query_text)
        if cluster_id not in self.cluster_performance:
            self.cluster_performance[cluster_id] = []
        self.cluster_performance[cluster_id].append(query.success)
        
        # Update query type performance
        query_type = classify_query_type(query.query_text)
        if query_type not in self.query_type_performance:
            self.query_type_performance[query_type] = []
        self.query_type_performance[query_type].append(query.success)
        
        # Adjust thresholds every 10 queries
        if len(self.query_history) % 10 == 0:
            self.adjust_thresholds()
    
    def adjust_thresholds(self):
        """Adjust confidence thresholds based on performance."""
        recent_queries = self.query_history[-50:]  # Last 50 queries
        
        # Calculate success rate of local model attempts
        local_attempts = [q for q in recent_queries if q.route == "local"]
        if local_attempts:
            local_success_rate = sum(q.success for q in local_attempts) / len(local_attempts)
            
            # If local model is doing well, lower threshold (trust more)
            if local_success_rate >= 0.80:
                self.preflight_threshold = max(0.40, self.preflight_threshold - 0.02)
                self.output_threshold = max(0.60, self.output_threshold - 0.02)
            # If struggling, raise threshold (be more cautious)
            elif local_success_rate < 0.60:
                self.preflight_threshold = min(0.70, self.preflight_threshold + 0.02)
                self.output_threshold = min(0.80, self.output_threshold + 0.02)
    
    def get_cluster_id(self, query: str) -> str:
        """Get semantic cluster ID for query."""
        # Use embeddings to cluster queries
        embedding = get_embedding(query)
        
        # Find nearest cluster (simple: use cosine similarity to cluster centroids)
        nearest_cluster = find_nearest_cluster(embedding, self.cluster_centroids)
        
        return nearest_cluster
    
    def identify_knowledge_gaps(self) -> list[str]:
        """Identify topics with consistently low confidence."""
        gaps = []
        
        # Group low-confidence queries
        low_confidence_queries = [
            q for q in self.query_history[-100:]
            if q.preflight_confidence < 0.40
        ]
        
        # Cluster them to find common themes
        if len(low_confidence_queries) >= 5:
            clusters = cluster_queries([q.query_text for q in low_confidence_queries])
            for cluster in clusters:
                if len(cluster) >= 3:  # At least 3 queries on same topic
                    gaps.append(cluster.theme)
        
        return gaps

class QueryResult:
    """Record of a query and its outcome."""
    query_text: str
    route: str  # "local", "cloud", "local_then_cloud"
    preflight_confidence: float
    output_confidence: float
    success: bool  # Did user accept response?
    user_edited: bool
    timestamp: datetime
```

**Adaptive Thresholds Over Time:**

```python
# Initial state (conservative, prefer cloud)
PREFLIGHT_THRESHOLD = 0.60  # Need 60% RAG confidence to try local
OUTPUT_THRESHOLD = 0.70     # Need 70% output confidence to accept

# After 50 queries (if local model performing well)
PREFLIGHT_THRESHOLD = 0.50
OUTPUT_THRESHOLD = 0.65

# After 200 queries (strong local preference)
PREFLIGHT_THRESHOLD = 0.40
OUTPUT_THRESHOLD = 0.60
```

---

## Meta-Query Generation

**Trigger:** When local model output confidence < threshold

**Purpose:** Generate a comprehensive note to fill knowledge gap

**Process:**

1. **Analyze failure:**
   - What was the original query?
   - What did local model respond?
   - What was missing from RAG results?

2. **Generate enhanced query for cloud:**
   - More specific and comprehensive than original
   - Request structured information
   - Specify desired format

3. **Cloud LLM generates note:**
   - Comprehensive answer to original query
   - Includes examples, explanations, context
   - Structured with headings, code blocks, etc.

4. **Suggest domain and tags:**
   - Use Phase 1.5 domain auto-tag rules
   - Suggest filename
   - Add metadata (confidence score, source query)

5. **Save to draft notes:**
   - Goes to `~/.polly/notes/_Drafts/`
   - User reviews before accepting

**Meta-Query Templates:**

```python
METAQUERY_TEMPLATES = {
    "factual": """
The user asked: "{original_query}"

The local model's response was insufficient due to lack of knowledge.

Please provide a comprehensive explanation that covers:
1. Core concept definition
2. Key principles or components
3. Practical examples
4. Common use cases
5. Related concepts or alternatives

Format as a well-structured note with headings and examples.
""",
    
    "procedural": """
The user asked: "{original_query}"

Please provide a detailed step-by-step guide that includes:
1. Prerequisites or requirements
2. Step-by-step instructions (numbered)
3. Code examples or commands (if applicable)
4. Common pitfalls or gotchas
5. Verification steps

Format as a practical tutorial.
""",
    
    "analytical": """
The user asked: "{original_query}"

Please provide an analytical comparison or analysis that covers:
1. Overview of each option/approach
2. Strengths and weaknesses of each
3. Use cases where each excels
4. Concrete examples
5. Recommendation or conclusion

Format as a balanced analysis.
""",
    
    "code": """
The user asked: "{original_query}"

Please provide a code-focused explanation that includes:
1. Brief concept explanation
2. Code example with comments
3. Explanation of how the code works
4. Common variations or patterns
5. Best practices

Format with clear code blocks and explanations.
"""
}

def generate_meta_query(
    original_query: str,
    failed_response: str,
    chunks: list[Chunk]
) -> str:
    """
    Generate enhanced query for cloud LLM.
    """
    # Classify query type
    query_type = classify_query_type(original_query)
    template = METAQUERY_TEMPLATES.get(query_type, METAQUERY_TEMPLATES["factual"])
    
    # Fill template
    meta_query = template.format(original_query=original_query)
    
    # Add context about what we already know
    if chunks:
        known_context = "\n\n".join(c.text for c in chunks[:3])
        meta_query += f"\n\nExisting knowledge (for context):\n{known_context}"
        meta_query += "\n\nPlease expand beyond this existing knowledge."
    
    return meta_query

def classify_query_type(query: str) -> str:
    """Classify query into type for appropriate template."""
    query_lower = query.lower()
    
    # Code-related
    if any(word in query_lower for word in ["code", "implement", "function", "class", "syntax"]):
        return "code"
    
    # Procedural (how-to)
    if any(word in query_lower for word in ["how to", "how do i", "steps", "guide", "tutorial"]):
        return "procedural"
    
    # Analytical (comparison)
    if any(word in query_lower for word in ["compare", "difference", "vs", "versus", "better", "pros and cons"]):
        return "analytical"
    
    # Default to factual
    return "factual"
```

**Domain Categorization:**

```python
def suggest_domain_for_note(
    note_content: str,
    original_query: str,
    domains: list[Domain]
) -> tuple[Domain, float]:
    """
    Suggest which domain this note belongs to.
    Returns (domain, confidence_score).
    """
    scores = {}
    
    # Combine note content and query for analysis
    combined_text = f"{original_query} {note_content}".lower()
    
    # Score each domain based on auto-tag rule matches
    for domain in domains:
        matches = sum(1 for keyword in domain.autoTagRules if keyword in combined_text)
        if domain.autoTagRules:
            scores[domain.id] = matches / len(domain.autoTagRules)
        else:
            scores[domain.id] = 0.0
    
    # Get best match
    if scores:
        best_domain_id = max(scores, key=scores.get)
        best_score = scores[best_domain_id]
        best_domain = next(d for d in domains if d.id == best_domain_id)
        return (best_domain, best_score)
    else:
        # No good match, return first domain with low confidence
        return (domains[0], 0.0)

def suggest_tags_for_note(note_content: str, domains: list[Domain]) -> list[str]:
    """Extract suggested tags from note content."""
    tags = set()
    content_lower = note_content.lower()
    
    # Extract tags from all domains' auto-tag rules that appear in content
    for domain in domains:
        for keyword in domain.autoTagRules:
            if keyword in content_lower:
                tags.add(keyword)
    
    # Extract markdown headings as potential tags
    headings = re.findall(r'^#+\s+(.+)$', note_content, re.MULTILINE)
    for heading in headings[:3]:  # Top 3 headings
        clean_heading = re.sub(r'[^\w\s-]', '', heading.lower())
        if len(clean_heading.split()) <= 3:  # Only short phrases
            tags.add(clean_heading.replace(' ', '-'))
    
    return sorted(list(tags))[:10]  # Max 10 tags

def suggest_filename_for_note(
    note_content: str,
    original_query: str
) -> str:
    """Generate filename from query or first heading."""
    # Try to use first heading
    headings = re.findall(r'^#+\s+(.+)$', note_content, re.MULTILINE)
    if headings:
        title = headings[0]
    else:
        # Use query
        title = original_query
    
    # Clean up for filename
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[\s]+', '-', filename)
    filename = filename[:50]  # Max 50 chars
    
    return f"{filename}.md"
```

---

## Token Budget Management

**Purpose:** Track cloud API usage across providers, fallback when limits reached

**Providers to Track:**

1. **Anthropic (Claude)**
   - Input tokens
   - Output tokens
   - Cost per token (varies by model)

2. **OpenAI (GPT-4/GPT-3.5)**
   - Input tokens
   - Output tokens
   - Cost per token

3. **GitHub Copilot**
   - Request count (different billing model)
   - Some plans have unlimited requests

4. **Local LLM**
   - Free, no limits

**Storage:**

`~/.polly/token_usage.json`:

```json
{
  "date": "2026-01-23",
  "providers": {
    "anthropic": {
      "input_tokens": 45000,
      "output_tokens": 12000,
      "requests": 24,
      "estimated_cost": 0.85
    },
    "openai": {
      "input_tokens": 30000,
      "output_tokens": 8000,
      "requests": 15,
      "estimated_cost": 0.50
    },
    "copilot": {
      "requests": 120
    },
    "local": {
      "requests": 45,
      "tokens": 0
    }
  },
  "monthly_limits": {
    "anthropic": {
      "max_tokens": 1000000,
      "max_cost": 20.00
    },
    "openai": {
      "max_tokens": 500000,
      "max_cost": 15.00
    }
  },
  "rollover_date": "2026-02-01"
}
```

**Tracking Logic:**

```python
class TokenBudgetManager:
    """Manage token usage across cloud providers."""
    
    def __init__(self):
        self.usage_file = Path.home() / ".polly" / "token_usage.json"
        self.usage_data = self.load_usage()
    
    def load_usage(self) -> dict:
        """Load usage data, handle rollover."""
        if self.usage_file.exists():
            data = json.loads(self.usage_file.read_text())
            
            # Check if we need to rollover (new month)
            rollover_date = datetime.fromisoformat(data["rollover_date"])
            if datetime.now() >= rollover_date:
                data = self.create_new_month_data()
                self.save_usage(data)
            
            return data
        else:
            return self.create_new_month_data()
    
    def create_new_month_data(self) -> dict:
        """Create fresh usage data for new month."""
        today = datetime.now()
        next_month = today.replace(day=1) + timedelta(days=32)
        next_month = next_month.replace(day=1)
        
        return {
            "date": today.isoformat(),
            "providers": {
                "anthropic": {"input_tokens": 0, "output_tokens": 0, "requests": 0, "estimated_cost": 0.0},
                "openai": {"input_tokens": 0, "output_tokens": 0, "requests": 0, "estimated_cost": 0.0},
                "copilot": {"requests": 0},
                "local": {"requests": 0, "tokens": 0}
            },
            "monthly_limits": self.get_default_limits(),
            "rollover_date": next_month.isoformat()
        }
    
    def get_default_limits(self) -> dict:
        """Get default monthly limits (user-configurable in settings)."""
        return {
            "anthropic": {"max_tokens": 1000000, "max_cost": 20.00},
            "openai": {"max_tokens": 500000, "max_cost": 15.00}
        }
    
    def record_usage(
        self,
        provider: str,
        input_tokens: int = 0,
        output_tokens: int = 0
    ):
        """Record token usage for a provider."""
        provider_data = self.usage_data["providers"][provider]
        
        provider_data["requests"] += 1
        
        if provider != "copilot":
            provider_data["input_tokens"] += input_tokens
            provider_data["output_tokens"] += output_tokens
            
            # Estimate cost (rough approximations)
            cost = self.estimate_cost(provider, input_tokens, output_tokens)
            provider_data["estimated_cost"] += cost
        
        self.save_usage(self.usage_data)
    
    def estimate_cost(self, provider: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for token usage."""
        # Rough cost estimates (as of 2024, will need updating)
        costs = {
            "anthropic": {  # Claude 3
                "input": 0.015 / 1000,  # $0.015 per 1K input tokens
                "output": 0.075 / 1000  # $0.075 per 1K output tokens
            },
            "openai": {  # GPT-4
                "input": 0.03 / 1000,
                "output": 0.06 / 1000
            }
        }
        
        if provider in costs:
            return (input_tokens * costs[provider]["input"] +
                   output_tokens * costs[provider]["output"])
        return 0.0
    
    def check_budget(self, provider: str) -> tuple[bool, str]:
        """
        Check if provider is within budget.
        Returns (can_use, reason_if_not).
        """
        if provider == "local":
            return (True, "")
        
        provider_data = self.usage_data["providers"].get(provider)
        limits = self.usage_data["monthly_limits"].get(provider)
        
        if not provider_data or not limits:
            return (True, "")
        
        # Check token limit
        total_tokens = provider_data.get("input_tokens", 0) + provider_data.get("output_tokens", 0)
        if total_tokens >= limits.get("max_tokens", float('inf')):
            return (False, f"Monthly token limit reached ({limits['max_tokens']:,} tokens)")
        
        # Check cost limit
        cost = provider_data.get("estimated_cost", 0)
        if cost >= limits.get("max_cost", float('inf')):
            return (False, f"Monthly cost limit reached (${limits['max_cost']:.2f})")
        
        # Warning at 80%
        token_usage_pct = total_tokens / limits.get("max_tokens", 1) * 100
        cost_usage_pct = cost / limits.get("max_cost", 1) * 100
        
        if token_usage_pct >= 80 or cost_usage_pct >= 80:
            return (True, f"Warning: {max(token_usage_pct, cost_usage_pct):.0f}% of monthly limit used")
        
        return (True, "")
    
    def get_fallback_provider(self, preferred: str) -> str:
        """Get fallback provider if preferred is over budget."""
        # Try providers in order
        fallback_order = ["local", "copilot", "anthropic", "openai"]
        
        for provider in fallback_order:
            if provider == preferred:
                continue
            
            can_use, _ = self.check_budget(provider)
            if can_use:
                return provider
        
        # Last resort: local
        return "local"
```

**Fallback Priority:**

1. **Primary cloud provider** (user's preferred: Claude or GPT)
2. **Secondary cloud provider** (the other one)
3. **GitHub Copilot** (if integrated and available)
4. **Local LLM** (always available, free)

**User Notifications:**

```python
def notify_budget_status(provider: str, usage_pct: float):
    """Notify user of budget status."""
    if usage_pct >= 100:
        show_notification(
            title="Budget Limit Reached",
            message=f"{provider} monthly limit reached. Falling back to alternative providers.",
            level="warning"
        )
    elif usage_pct >= 80:
        show_notification(
            title="Budget Warning",
            message=f"{provider} usage at {usage_pct:.0f}%. Consider switching to local model.",
            level="info"
        )
```

---

## Draft Notes Review Queue

**Purpose:** All AI-generated notes go through user review before adding to knowledge base

**Storage:** `~/.polly/notes/_Drafts/`

**File Format:**

```markdown
---
created: 2026-01-23T14:30:00Z
source_query: "How does backpropagation work in neural networks?"
suggested_domain: "concepts"
suggested_tags: ["neural network", "machine learning", "algorithm"]
confidence_score: 0.45
model_used: "claude-3-sonnet"
status: "draft"
---

# Backpropagation in Neural Networks

Backpropagation is the algorithm used to train neural networks...

[Generated content here]
```

**UI Components:**

### 1. Draft Badge in Sidebar

```
Notes
├── _Drafts (3) ← Badge showing count
├── 01-Concepts
├── 02-Patterns
└── 03-Code
```

### 2. Review Panel

```
┌─────────────────────────────────────────────────────────┐
│  Draft Notes Review                          [Close ×]  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  3 notes awaiting review                                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ✓ Backpropagation in Neural Networks           │   │
│  │   Created: Jan 23, 2:30 PM                      │   │
│  │   Source: "How does backpropagation work..."    │   │
│  │   Suggested: 💡 Concepts                        │   │
│  │   Confidence: ●●○○○ (45%)                       │   │
│  │                                                  │   │
│  │   [Preview] [Edit] [Accept] [Reject]            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ □ Python Decorators Guide                       │   │
│  │   Created: Jan 23, 11:15 AM                     │   │
│  │   Suggested: 💻 Code                            │   │
│  │                                                  │   │
│  │   [Preview] [Edit] [Accept] [Reject]            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Batch actions: [Accept All] [Review Selected (1)]     │
└─────────────────────────────────────────────────────────┘
```

### 3. Edit Modal (when clicking Edit)

```
┌─────────────────────────────────────────────────────────┐
│  Edit Draft Note                           [Close ×]    │
├─────────────────────────────────────────────────────────┤
│  Filename: [backpropagation-neural-networks.md____]     │
│                                                         │
│  Domain:   [💡 Concepts ▼]                             │
│                                                         │
│  Tags:     [neural network ×] [machine learning ×]     │
│            [algorithm ×] [+ Add tag]                    │
│                                                         │
│  Content:  ┌─────────────────────────────────────────┐ │
│            │ # Backpropagation in Neural Networks   │ │
│            │                                         │ │
│            │ Backpropagation is the algorithm...    │ │
│            │ (Monaco editor with markdown preview)   │ │
│            └─────────────────────────────────────────┘ │
│                                                         │
│                          [Cancel] [Save & Accept]       │
└─────────────────────────────────────────────────────────┘
```

### 4. Preview Modal (when clicking Preview)

```
┌─────────────────────────────────────────────────────────┐
│  Preview: Backpropagation in Neural Networks           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  # Backpropagation in Neural Networks                  │
│                                                         │
│  Backpropagation is the algorithm used to train...     │
│                                                         │
│  ## How It Works                                        │
│                                                         │
│  1. Forward pass calculates output                      │
│  2. Error is computed                                   │
│  3. Backward pass propagates error                      │
│                                                         │
│  [Rendered markdown preview]                            │
│                                                         │
│                                              [Close]    │
└─────────────────────────────────────────────────────────┘
```

**Batch Review:**

```python
class DraftReviewQueue:
    """Manage draft notes review queue."""
    
    def __init__(self):
        self.drafts_dir = Path.home() / ".polly" / "notes" / "_Drafts"
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
    
    def add_draft(
        self,
        content: str,
        source_query: str,
        suggested_domain: Domain,
        tags: list[str],
        confidence: float,
        model: str
    ) -> Path:
        """Add new draft note to review queue."""
        # Generate filename
        filename = self.generate_filename(source_query)
        filepath = self.drafts_dir / filename
        
        # Create frontmatter
        frontmatter = {
            "created": datetime.now().isoformat(),
            "source_query": source_query,
            "suggested_domain": suggested_domain.id,
            "suggested_tags": tags,
            "confidence_score": confidence,
            "model_used": model,
            "status": "draft"
        }
        
        # Write file
        full_content = f"---\n{yaml.dump(frontmatter)}---\n\n{content}"
        filepath.write_text(full_content)
        
        return filepath
    
    def list_drafts(self) -> list[DraftNote]:
        """List all draft notes."""
        drafts = []
        for filepath in self.drafts_dir.glob("*.md"):
            draft = self.parse_draft(filepath)
            drafts.append(draft)
        
        return sorted(drafts, key=lambda d: d.created, reverse=True)
    
    def accept_draft(self, draft_id: str, edits: dict = None):
        """Accept draft and move to appropriate domain folder."""
        draft = self.get_draft(draft_id)
        
        # Apply edits if provided
        if edits:
            draft.update(edits)
        
        # Determine target folder
        domain = get_domain_by_id(draft.domain_id)
        target_folder = Path.home() / ".polly" / "notes" / domain.folderPath
        target_folder.mkdir(parents=True, exist_ok=True)
        
        # Move file
        target_path = target_folder / draft.filename
        shutil.move(draft.filepath, target_path)
        
        # Trigger RAG indexing
        trigger_rag_indexing(target_path)
        
        # Update knowledge graph
        update_knowledge_graph(target_path)
    
    def reject_draft(self, draft_id: str):
        """Reject and delete draft."""
        draft = self.get_draft(draft_id)
        draft.filepath.unlink()
    
    def batch_accept(self, draft_ids: list[str]):
        """Accept multiple drafts at once."""
        for draft_id in draft_ids:
            self.accept_draft(draft_id)
    
    def auto_cleanup(self, days: int = 30):
        """Delete drafts older than specified days."""
        cutoff = datetime.now() - timedelta(days=days)
        
        for draft in self.list_drafts():
            if draft.created < cutoff:
                self.reject_draft(draft.id)
```

**Keyboard Shortcuts (Quick Review Mode):**

- **A** - Accept current draft
- **R** - Reject current draft
- **E** - Edit current draft
- **N** - Next draft
- **P** - Previous draft
- **Esc** - Close review panel

---

## Model Selection & Routing Logic

### Decision Tree

```
Query arrives
    │
    ├─→ Check token budgets
    │   └─→ Any provider over limit?
    │       └─→ Yes: Remove from available providers
    │
    ├─→ Layer 1: Pre-Flight Check (RAG Quality)
    │   │
    │   ├─→ Confidence < 40%?
    │   │   └─→ Yes: Route to CLOUD (skip local)
    │   │
    │   └─→ No: Continue to local attempt
    │
    ├─→ Send to LOCAL model
    │
    ├─→ Layer 2: Output Analysis (Response Quality)
    │   │
    │   ├─→ Confidence < 60%?
    │   │   └─→ Yes: Generate meta-query → CLOUD
    │   │   └─→ Create draft note for review
    │   │
    │   └─→ No: Accept local response
    │
    └─→ Layer 3: Historical Learning (Background)
        └─→ Record outcome, adjust thresholds
```

### Routing Implementation

```python
class IntelligentRouter:
    """Route queries to appropriate model based on confidence."""
    
    def __init__(self):
        self.learner = ConfidenceLearner()
        self.budget_manager = TokenBudgetManager()
        self.draft_queue = DraftReviewQueue()
    
    async def route_query(self, query: str, user_override: str = None) -> Response:
        """
        Main routing logic.
        
        Args:
            query: User's question
            user_override: Optional manual provider selection
        
        Returns:
            Response with answer and metadata
        """
        # Check user override
        if user_override:
            return await self.route_to_provider(query, user_override)
        
        # Layer 1: Pre-Flight Check
        chunks = retrieve_chunks(query)
        preflight_confidence = calculate_preflight_confidence(query, chunks, get_domains())
        
        if preflight_confidence < self.learner.preflight_threshold:
            # Skip local, go straight to cloud
            reason = f"Insufficient knowledge (confidence: {preflight_confidence:.0%})"
            return await self.route_to_cloud(query, reason, chunks)
        
        # Try local model
        local_response = await self.route_to_local(query, chunks)
        
        # Layer 2: Output Analysis
        output_confidence = calculate_output_confidence(local_response.text, query)
        
        if output_confidence < self.learner.output_threshold:
            # Generate meta-query and route to cloud
            reason = f"Low output quality (confidence: {output_confidence:.0%})"
            return await self.route_to_cloud_with_meta_query(
                query, local_response.text, chunks, reason
            )
        
        # Accept local response
        response = Response(
            text=local_response.text,
            model="local",
            preflight_confidence=preflight_confidence,
            output_confidence=output_confidence,
            route="local_only"
        )
        
        # Layer 3: Record for learning (async)
        self.learner.record_query(QueryResult(
            query_text=query,
            route="local",
            preflight_confidence=preflight_confidence,
            output_confidence=output_confidence,
            success=True,
            user_edited=False,
            timestamp=datetime.now()
        ))
        
        return response
    
    async def route_to_local(self, query: str, chunks: list[Chunk]) -> Response:
        """Route to local LLM."""
        context = "\n\n".join(c.text for c in chunks[:5])
        
        prompt = f"""Answer the following question using the provided context.

Context:
{context}

Question: {query}

Answer:"""
        
        response_text = await local_llm.generate(prompt)
        
        return Response(text=response_text, model="local")
    
    async def route_to_cloud(
        self,
        query: str,
        reason: str,
        chunks: list[Chunk]
    ) -> Response:
        """Route directly to cloud."""
        # Check budget and select provider
        provider = self.select_cloud_provider()
        
        # Generate response
        context = "\n\n".join(c.text for c in chunks[:5]) if chunks else ""
        
        prompt = f"""Answer the following question comprehensively.

{"Known context:\n" + context + "\n\n" if context else ""}Question: {query}

Provide a detailed answer with examples and explanations."""
        
        response_text = await cloud_llm.generate(prompt, provider=provider)
        
        # Track token usage
        self.budget_manager.record_usage(
            provider,
            input_tokens=count_tokens(prompt),
            output_tokens=count_tokens(response_text)
        )
        
        return Response(
            text=response_text,
            model=provider,
            route="cloud_direct",
            reason=reason
        )
    
    async def route_to_cloud_with_meta_query(
        self,
        original_query: str,
        failed_response: str,
        chunks: list[Chunk],
        reason: str
    ) -> Response:
        """Generate meta-query and route to cloud, save to drafts."""
        # Generate enhanced query
        meta_query = generate_meta_query(original_query, failed_response, chunks)
        
        # Select provider
        provider = self.select_cloud_provider()
        
        # Generate comprehensive note
        note_content = await cloud_llm.generate(meta_query, provider=provider)
        
        # Suggest domain and tags
        domains = get_domains()
        suggested_domain, _ = suggest_domain_for_note(note_content, original_query, domains)
        suggested_tags = suggest_tags_for_note(note_content, domains)
        
        # Add to draft queue
        draft_path = self.draft_queue.add_draft(
            content=note_content,
            source_query=original_query,
            suggested_domain=suggested_domain,
            tags=suggested_tags,
            confidence=0.0,  # Meta-query = definite knowledge gap
            model=provider
        )
        
        # Track token usage
        self.budget_manager.record_usage(
            provider,
            input_tokens=count_tokens(meta_query),
            output_tokens=count_tokens(note_content)
        )
        
        # Return response to user
        response = Response(
            text=note_content,
            model=provider,
            route="meta_query",
            reason=reason,
            draft_path=draft_path
        )
        
        return response
    
    def select_cloud_provider(self) -> str:
        """Select cloud provider based on budget and preferences."""
        # User's preferred provider (from settings)
        preferred = get_user_preference("preferred_cloud_provider", "anthropic")
        
        # Check budget
        can_use, msg = self.budget_manager.check_budget(preferred)
        if can_use:
            if msg:  # Warning message
                show_notification("Budget Warning", msg, level="info")
            return preferred
        
        # Preferred is over budget, try fallback
        fallback = self.budget_manager.get_fallback_provider(preferred)
        show_notification(
            "Provider Switch",
            f"{preferred} budget exceeded. Using {fallback} instead.",
            level="warning"
        )
        return fallback
```

---

## UI Components

### 1. Confidence Indicator (in Chat UI)

```
┌─────────────────────────────────────────────────────────┐
│  You: How does backpropagation work?                    │
│                                                         │
│  Polly: [📊 Confidence: 45% | Cloud: Claude]           │
│         [⚠️  Knowledge gap detected - generating note]  │
│                                                         │
│  Backpropagation is the algorithm used to train         │
│  neural networks by propagating errors backward...      │
│                                                         │
│  💾 Draft note created for review                       │
│  [Review Now] [Review Later]                            │
└─────────────────────────────────────────────────────────┘
```

### 2. Override Button

When confidence is borderline, show override option:

```
┌─────────────────────────────────────────────────────────┐
│  Polly: [📊 Confidence: 55% | Local]                    │
│         Quality seems low. [Use Claude instead?]        │
│                                                         │
│  The concept of backpropagation is... perhaps...        │
│  I think it might work by...                            │
└─────────────────────────────────────────────────────────┘
```

### 3. Token Usage Dashboard (Settings)

```
┌─────────────────────────────────────────────────────────┐
│  Settings > Models > Token Usage                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Monthly Usage (January 2026)                           │
│                                                         │
│  Anthropic (Claude)                                     │
│  ████████████░░░░░░░░ 57,000 / 1,000,000 tokens (6%)   │
│  Cost: $0.85 / $20.00                                   │
│  Requests: 24                                           │
│                                                         │
│  OpenAI (GPT-4)                                         │
│  ██████░░░░░░░░░░░░░░ 38,000 / 500,000 tokens (8%)     │
│  Cost: $0.50 / $15.00                                   │
│  Requests: 15                                           │
│                                                         │
│  GitHub Copilot                                         │
│  Requests: 120 (unlimited plan)                         │
│                                                         │
│  Local LLM                                              │
│  Requests: 45 (free)                                    │
│                                                         │
│  [Edit Monthly Limits] [Export Report]                  │
└─────────────────────────────────────────────────────────┘
```

### 4. Settings: Routing Configuration

```
┌─────────────────────────────────────────────────────────┐
│  Settings > Models > Intelligent Routing                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Confidence Thresholds:                                 │
│                                                         │
│  Pre-flight (RAG Quality):                              │
│  ●●●●○○○○○○ 40% (Current: Aggressive local preference) │
│                                                         │
│  Output Quality:                                        │
│  ●●●●●●○○○○ 60%                                         │
│                                                         │
│  ☑ Enable adaptive learning                            │
│  ☑ Show confidence scores in chat                      │
│  ☑ Notify when generating draft notes                  │
│                                                         │
│  Preferred Cloud Provider:                              │
│  ● Anthropic (Claude)                                   │
│  ○ OpenAI (GPT-4)                                       │
│                                                         │
│  Auto-cleanup draft notes after: [30___] days          │
│                                                         │
│  [Reset to Defaults] [Save Changes]                     │
└─────────────────────────────────────────────────────────┘
```

---

## Integration Points

### Phase 1.5: Domain Configuration

- Uses user-defined domains for meta-query categorization
- Domain auto-tag rules determine note domain
- RAG weights influence pre-flight confidence

### Phase 13: Pattern Learning

- Historical learning uses pattern recognition
- Query clustering for performance analysis

### Phase 14: Mental Models

- Could use mental models to improve meta-query generation
- "Apply SOLID principles" mental model → better code-related notes

### Phase 16: Native Notes

- Draft notes stored in `_Drafts/` folder
- Accepted notes moved to domain folders
- Review queue integrated in notes UI

### Phase 17: Code Workspace

- Intelligent routing used for code chat
- Code → Note creation uses meta-query generation
- Token budget prevents overuse during coding sessions

---

## Implementation Timeline

**Total Duration:** 14 days (2 weeks)

### Week 1: Foundation (Days 1-7)

**Days 1-2: Multi-Model Infrastructure**
- Provider adapters (Anthropic, OpenAI, Copilot, Local)
- Unified API interface
- Request/response handling
- Error handling and retries

**Days 3-4: Token Budget Management**
- Token usage tracking
- Budget limit enforcement
- Fallback provider selection
- Usage dashboard UI

**Days 5-7: Pre-Flight Confidence System**
- RAG quality metrics
- Chunk retrieval analysis
- Domain alignment scoring
- Pre-flight decision logic

**Acceptance criteria:**
- ✓ Can route to any provider
- ✓ Token usage tracked accurately
- ✓ Pre-flight checks work correctly
- ✓ Budget limits enforced

### Week 2: Intelligence (Days 8-14)

**Days 8-9: Output Analysis**
- Response quality metrics
- Uncertainty detection
- Hallucination detection
- Output confidence scoring

**Days 10-11: Historical Learning**
- Query history tracking
- Performance analysis
- Adaptive threshold adjustment
- Knowledge gap identification

**Days 12-13: Meta-Query & Draft Notes**
- Meta-query template system
- Draft note generation
- Domain/tag suggestion
- Draft queue UI (review panel)

**Day 14: Testing & Polish**
- End-to-end testing
- UI polish
- Documentation
- Settings panel

**Acceptance criteria:**
- ✓ Output analysis detects low-quality responses
- ✓ System learns and improves over time
- ✓ Meta-queries generate useful notes
- ✓ Draft review workflow smooth
- ✓ All UI components functional

---

## Success Criteria

Phase 11 is complete when:

1. **Intelligent routing works:**
   - ✓ Pre-flight check evaluates RAG quality
   - ✓ Output analysis detects low-quality responses
   - ✓ System routes to cloud when needed
   - ✓ Local model used when appropriate

2. **Adaptive learning functions:**
   - ✓ Thresholds adjust based on performance
   - ✓ System improves over 50+ queries
   - ✓ Knowledge gaps identified

3. **Meta-query generation:**
   - ✓ Comprehensive notes generated for knowledge gaps
   - ✓ Domain and tags suggested accurately
   - ✓ Draft notes saved for review

4. **Token budget management:**
   - ✓ Usage tracked across all providers
   - ✓ Limits enforced gracefully
   - ✓ Fallback providers work
   - ✓ Dashboard shows accurate data

5. **Draft review queue:**
   - ✓ All AI-generated notes go to drafts
   - ✓ Review UI is intuitive
   - ✓ Batch operations work
   - ✓ Accepted notes indexed in RAG

6. **User experience:**
   - ✓ Confidence scores visible and understandable
   - ✓ Routing decisions transparent
   - ✓ Override options available
   - ✓ No jarring switches or delays

---

## Future Enhancements

### Phase 11b: Advanced Intelligence (3-5 days)

Potential future additions:

1. **Proactive Knowledge Building:**
   - Identify knowledge gaps proactively
   - Generate notes in background
   - "I noticed you ask about X often but have few notes. Should I create a comprehensive guide?"

2. **Contextual Model Selection:**
   - Different models for different query types
   - GPT-4 for creative, Claude for analytical, Local for quick facts

3. **Confidence Calibration:**
   - User feedback on confidence scores
   - "Was this routing decision correct?"
   - Improve scoring algorithms based on feedback

4. **Smart Pre-loading:**
   - Predict likely follow-up questions
   - Pre-generate responses in background
   - Instant answers for predictable queries

5. **Cost Optimization:**
   - Batch similar queries
   - Cache cloud responses
   - Smart caching strategies

---

## Technical Notes

### Storage Files

```
~/.polly/
├── domains.json              # Phase 1.5
├── token_usage.json          # Token budget tracking
├── confidence_history.json   # Historical learning data
└── notes/
    └── _Drafts/              # Review queue
        ├── 2026-01-23-backpropagation.md
        └── 2026-01-24-python-decorators.md
```

### Key Algorithms

1. **Pre-flight Confidence:** 5 metrics, weighted scoring
2. **Output Confidence:** Inverse scoring (start at 1.0, deduct for issues)
3. **Adaptive Thresholds:** Adjust ±0.02 every 10 queries based on success rate
4. **Meta-Query Generation:** Template-based, context-aware

### Performance Considerations

- Pre-flight check: <100ms (RAG retrieval already done)
- Output analysis: <200ms (text analysis, no LLM call)
- Meta-query generation: 2-5 seconds (cloud LLM call)
- Draft note creation: <100ms (file write)

---

## Dependencies

**Phase 11 depends on:**
- Phase 1.5: Domain Configuration (for meta-query categorization)
- Phase 2: RAG System (for pre-flight checks)
- Phase 6: GitHub Copilot integration (optional provider)
- Phase 7: GitHub Integration (optional provider)

**Phase 11 enables:**
- Phase 16c: AI note creation from conversations
- Phase 17: Code workspace chat with intelligent routing

---

## References

- MASTER_ROADMAP.md - Overall project plan
- PHASE1.5_DOMAIN_CONFIGURATION.md - Domain system used for categorization
- PHASE2_RAG_IMPLEMENTATION.md - RAG system for pre-flight checks
- PHASE16_NATIVE_NOTES.md - Draft notes integration
- PHASE17_CODE_WORKSPACE.md - Code chat integration
- PHASE_STATUS_SUMMARY.md - Current implementation status

---

**End of Phase 11 specification**

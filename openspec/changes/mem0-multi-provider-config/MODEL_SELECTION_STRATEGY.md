# Model Selection Strategy: Dynamic Provider Switching

**Date:** February 13, 2026  
**Status:** 📝 Design Exploration  
**Context:** Mem0 Multi-Provider Configuration

---

## Model Strengths Analysis

### Embedding Models

#### Ollama - nomic-embed-text (Local)
**Strengths:**
- **Privacy:** All data stays local, zero external API calls
- **Cost:** Completely free, no API usage limits
- **Speed:** Low latency (local inference, ~50-100ms)
- **Reliability:** No internet dependency, works offline
- **Context:** 8192 token context window

**Best for:**
- Personal notes, sensitive data, confidential information
- High-volume embedding (cost-sensitive)
- Offline/airplane mode usage
- Development and testing

**Weaknesses:**
- Lower quality embeddings vs. cloud models
- Requires local compute resources (GPU helpful)
- Single language focus (English-optimized)

---

#### Qwen - text-embedding-v3 (Cloud)
**Strengths:**
- **Multilingual:** Excellent Chinese + English support
- **Quality:** State-of-art embeddings (similar to OpenAI ada-002)
- **Speed:** Fast API response (~100-200ms)
- **Cost:** Relatively cheap (¥0.0007 per 1K tokens)
- **Context:** 8192 token context window

**Best for:**
- Chinese language content (notes, docs, conversations)
- Multilingual knowledge bases
- High-quality semantic search requirements
- Academic/research content

**Weaknesses:**
- Requires API key and internet
- China-based service (data sovereignty concerns for some)
- Cost accumulates with heavy usage

---

#### MiniMax - embo-01 (Cloud)
**Strengths:**
- **Chinese optimization:** Excellent for Chinese language
- **Multimodal:** Supports text + image embeddings
- **Context:** Large context window (16K tokens)
- **Integration:** Well-integrated with MiniMax LLMs

**Best for:**
- Chinese-first applications
- Multimodal knowledge (text + images in notes)
- Long documents (using large context)
- MiniMax ecosystem users

**Weaknesses:**
- Less documentation in English
- Higher cost than Qwen
- Newer model (less battle-tested)

---

#### GLM - embedding-3 (Cloud)
**Strengths:**
- **Chinese excellence:** From Tsinghua University (THUDM)
- **Academic pedigree:** Strong theoretical foundation
- **Quality:** Competitive with international models
- **Ecosystem:** Part of broader GLM (ChatGLM) ecosystem

**Best for:**
- Academic/research use cases
- Chinese language content
- GLM LLM users (consistency)
- Government/education sectors (trusted Chinese AI)

**Weaknesses:**
- API availability/rate limits
- Cost structure unclear
- Less global presence

---

### LLM Models (for Mem0 entity extraction)

#### Ollama - llama3.2:3b (Local)
**Strengths:**
- **Privacy:** Entity extraction stays local
- **Cost:** Free, unlimited usage
- **Speed:** Fast inference (~1-2 seconds for extraction)
- **Customization:** Can fine-tune model

**Best for:**
- Privacy-sensitive entity extraction
- High-volume memory operations
- Offline usage

**Weaknesses:**
- Lower accuracy vs. larger models
- Less context understanding
- Requires local compute

---

#### Qwen - qwen-turbo (Cloud)
**Strengths:**
- **Speed + Quality:** Fast with good accuracy
- **Chinese understanding:** Excellent for Chinese entities
- **Cost-effective:** Balanced price/performance
- **Reliability:** Stable API, good uptime

**Best for:**
- Real-time entity extraction
- Mixed Chinese/English content
- Production workloads

**Weaknesses:**
- API costs
- Internet dependency

---

#### MiniMax - abab6.5s-chat (Cloud)
**Strengths:**
- **Advanced reasoning:** Strong context understanding
- **Chinese entities:** Excellent at Chinese person/place names
- **Long context:** Handles complex documents

**Best for:**
- Complex document analysis
- Chinese entity relationship mapping
- High-accuracy requirements

**Weaknesses:**
- Higher latency than qwen-turbo
- Cost

---

#### GLM - glm-4-flash (Cloud)
**Strengths:**
- **Speed:** "Flash" variant optimized for low latency
- **Academic entities:** Good at research/academic terms
- **Chinese:** Strong Chinese language support

**Best for:**
- Academic knowledge bases
- Fast entity extraction with Chinese content
- Education sector

**Weaknesses:**
- Less flexible than larger GLM models
- API limitations

---

## Automatic Provider Selection Strategies

### Strategy 1: Content-Based Switching

**Detect content language and domain:**

```python
def select_provider_for_content(content: str, metadata: Dict) -> str:
    """
    Automatically select best provider based on content analysis.
    """
    # Language detection
    chinese_ratio = detect_chinese_ratio(content)
    
    if chinese_ratio > 0.3:
        # Primarily Chinese content
        if metadata.get('domain') == 'academic':
            return 'glm'  # Academic + Chinese = GLM
        elif metadata.get('source') == 'multimodal':
            return 'minimax'  # Images + Chinese = MiniMax
        else:
            return 'qwen'  # General Chinese = Qwen
    
    # Privacy check
    if metadata.get('privacy_level') == 'high':
        return 'ollama'  # Sensitive data = local
    
    # Default: balance quality and cost
    return 'qwen'
```

**UX Implementation:**
```yaml
# config.yaml
memory:
  mem0:
    auto_select: true
    selection_rules:
      - condition: "chinese_ratio > 0.3 AND domain == 'academic'"
        provider: "glm"
      
      - condition: "privacy_level == 'high'"
        provider: "ollama"
      
      - condition: "source == 'multimodal'"
        provider: "minimax"
      
      - condition: "default"
        provider: "qwen"
```

---

### Strategy 2: Context-Based Switching

**Switch based on Polly's current context:**

```python
def select_provider_for_context(persona: str, domain: str, user_prefs: Dict) -> str:
    """
    Select provider based on current Polly context.
    """
    # Persona-specific preferences
    if persona == 'Professor' and domain == 'research':
        return 'glm'  # Academic persona = GLM
    
    if persona == 'Scribe' and user_prefs.get('language') == 'zh':
        return 'qwen'  # Note-taking + Chinese = Qwen
    
    if persona == 'Architect' and user_prefs.get('privacy_mode'):
        return 'ollama'  # Code/architecture = local
    
    # User budget constraints
    if user_prefs.get('budget_mode') == 'free':
        return 'ollama'  # Free tier = local only
    
    return 'qwen'  # Default balanced choice
```

**UX Implementation:**
- **Persona settings:** Each persona has preferred provider
- **Domain settings:** Each domain (research, notes, code) has default
- **User preferences:** Global user settings override

---

### Strategy 3: Performance-Based Switching

**Monitor performance and switch adaptively:**

```python
class AdaptiveProviderSelector:
    def __init__(self):
        self.metrics = {
            'ollama': {'latency': [], 'quality_score': []},
            'qwen': {'latency': [], 'quality_score': []},
            'minimax': {'latency': [], 'quality_score': []},
            'glm': {'latency': [], 'quality_score': []}
        }
    
    def select_provider(self, context: Dict) -> str:
        """
        Select provider based on recent performance metrics.
        """
        # Check if any provider is failing
        for provider, metrics in self.metrics.items():
            if metrics.get('error_rate', 0) > 0.5:
                continue  # Skip unreliable providers
        
        # For time-sensitive operations
        if context.get('priority') == 'fast':
            return min(self.metrics.items(), 
                      key=lambda x: avg(x[1]['latency']))[0]
        
        # For quality-sensitive operations
        if context.get('priority') == 'quality':
            return max(self.metrics.items(),
                      key=lambda x: avg(x[1]['quality_score']))[0]
        
        # Balance cost and performance
        return self._calculate_best_value()
```

**UX Implementation:**
- **Health dashboard:** Show provider status (green/yellow/red)
- **Auto-failover:** Switch if current provider is down
- **Performance hints:** "Qwen is 2x faster right now"

---

### Strategy 4: Cost-Aware Switching

**Optimize for user's budget:**

```python
class CostAwareSelector:
    COSTS = {
        'ollama': 0.0,  # Free
        'qwen': 0.0007,  # ¥0.0007 per 1K tokens
        'minimax': 0.0015,  # ~¥0.0015 per 1K tokens
        'glm': 0.001  # ~¥0.001 per 1K tokens
    }
    
    def select_provider(self, budget: float, token_count: int) -> str:
        """
        Select cheapest provider that meets requirements.
        """
        cost_estimates = {
            provider: (token_count / 1000) * cost
            for provider, cost in self.COSTS.items()
        }
        
        # If budget is tight, use free option
        if budget < 0.01:
            return 'ollama'
        
        # If budget allows, use quality providers
        if cost_estimates['qwen'] < budget * 0.5:
            return 'qwen'  # Good quality, moderate cost
        
        return 'ollama'  # Default to free
```

**UX Implementation:**
```yaml
# User settings
user:
  memory_budget:
    monthly_limit: 100  # ¥100/month
    auto_optimize: true
    fallback_to_local: true
```

---

## UX Design Proposals

### Option 1: Manual Selection with Smart Defaults

**UI Location:** Settings > Memory > Provider

```
┌─────────────────────────────────────────┐
│ Memory Provider Selection               │
├─────────────────────────────────────────┤
│                                         │
│ Embedding Provider:                     │
│ ┌─────────────────────────────────────┐ │
│ │ ● Smart (Recommended)               │ │
│ │   ○ Ollama (Local - Privacy)        │ │
│ │   ○ Qwen (Cloud - Quality)          │ │
│ │   ○ MiniMax (Cloud - Multimodal)    │ │
│ │   ○ GLM (Cloud - Academic)          │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ LLM Provider:                           │
│ ┌─────────────────────────────────────┐ │
│ │ ● Same as embedding                 │ │
│ │   ○ Choose separately...            │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Smart Selection Rules:                 │
│ ┌─────────────────────────────────────┐ │
│ │ ☑ Use local for sensitive content  │ │
│ │ ☑ Use Qwen for Chinese content      │ │
│ │ ☑ Optimize for cost                 │ │
│ │ ☑ Auto-failover if provider down    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│          [Save Settings]                │
└─────────────────────────────────────────┘
```

**Pros:**
- User maintains control
- Smart defaults reduce cognitive load
- Clear visibility into what's happening

**Cons:**
- Requires user understanding of providers
- Manual switching is friction

---

### Option 2: Invisible Smart Switching

**No UI, just works:**

Polly automatically selects the best provider based on:
1. Content language (detected)
2. Privacy level (inferred from source)
3. User budget (tracked automatically)
4. Provider performance (monitored)

**Only surfaces in logs/debug:**
```
💡 Using Qwen for Chinese content (detected 80% Chinese)
💡 Switched to Ollama (budget limit reached)
💡 Using GLM for academic domain (Professor persona active)
```

**Pros:**
- Zero user friction
- Always optimal
- "Just works" experience

**Cons:**
- Less control for power users
- Harder to debug issues
- Opaque decision-making

---

### Option 3: Per-Persona Defaults with Override

**UI Location:** Persona Settings

```
┌─────────────────────────────────────────┐
│ Scribe Persona Settings                 │
├─────────────────────────────────────────┤
│                                         │
│ Preferred Memory Provider:              │
│ ┌─────────────────────────────────────┐ │
│ │ ● Smart (Chinese → Qwen)            │ │
│ │   ○ Always Qwen                      │ │
│ │   ○ Always Ollama                    │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Language Detection:                     │
│ ┌─────────────────────────────────────┐ │
│ │ ● Auto-detect                        │ │
│ │   ○ Always Chinese                   │ │
│ │   ○ Always English                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

**Professor Persona:**
```
Preferred Provider: GLM (Academic)
Auto-switch to Qwen if GLM unavailable
```

**Architect Persona:**
```
Preferred Provider: Ollama (Privacy)
Never use cloud providers
```

**Pros:**
- Context-aware defaults
- Per-persona optimization
- User can override

**Cons:**
- More complex mental model
- Settings scattered across personas

---

### Option 4: Budget-First UX

**UI Location:** Settings > Budget

```
┌─────────────────────────────────────────┐
│ Memory Budget                           │
├─────────────────────────────────────────┤
│                                         │
│ Monthly Budget: ¥ 50                    │
│ ├──────────────┤ 20% used this month    │
│                                         │
│ Current Usage:                          │
│ • Qwen:    ¥8.50  (17,000 tokens)      │
│ • MiniMax: ¥1.20  (800 tokens)         │
│ • Ollama:  ¥0     (45,000 tokens)      │
│                                         │
│ Provider Priority:                      │
│ 1. Ollama (Free) - use first           │
│ 2. Qwen (Cheap) - use if better        │
│ 3. MiniMax (Expensive) - use if needed │
│                                         │
│ ☑ Auto-switch to Ollama at 80% budget  │
│ ☑ Alert me at 90% budget               │
│                                         │
└─────────────────────────────────────────┘
```

**Pros:**
- Clear cost visibility
- Budget-conscious users love it
- Automatic cost optimization

**Cons:**
- May sacrifice quality for cost
- Requires cost tracking infrastructure

---

### Option 5: Content-Aware Inline Suggestions

**In-context provider hints:**

```
┌─────────────────────────────────────────┐
│ New Note                                │
├─────────────────────────────────────────┤
│                                         │
│ Title: 机器学习研究笔记                  │
│                                         │
│ 💡 Detected Chinese content             │
│    Recommend: Qwen (better quality)     │
│    Current: Ollama (local)              │
│    [Switch to Qwen]                     │
│                                         │
│ Content:                                │
│ 今天学习了transformer架构...              │
│                                         │
└─────────────────────────────────────────┘
```

**Or for sensitive content:**

```
┌─────────────────────────────────────────┐
│ New Note - Private                      │
├─────────────────────────────────────────┤
│                                         │
│ 🔒 Private note detected                │
│    Using: Ollama (local, private)       │
│    ✓ Data never leaves your device      │
│                                         │
└─────────────────────────────────────────┘
```

**Pros:**
- Educational for users
- Context-aware suggestions
- Optional - can be dismissed

**Cons:**
- May be annoying/distracting
- Adds UI complexity

---

## Recommended Approach

### Phase 1: Smart Defaults (Invisible)
**Start with automatic selection, no UI:**

```python
def auto_select_provider(content: str, metadata: Dict) -> str:
    # Privacy first
    if metadata.get('tags', []).includes('private'):
        return 'ollama'
    
    # Language detection
    if detect_chinese_ratio(content) > 0.3:
        return 'qwen'  # Best for Chinese
    
    # Default
    return 'ollama'  # Free, private, works offline
```

**Log decisions for debugging:**
```
[Mem0] Auto-selected Qwen (detected Chinese content)
[Mem0] Using Ollama (private tag detected)
```

---

### Phase 2: Per-Persona Defaults
**Add persona-specific preferences:**

```yaml
# config.yaml
personas:
  Professor:
    memory_provider: "glm"  # Academic use case
  
  Scribe:
    memory_provider: "qwen"  # Multilingual notes
  
  Architect:
    memory_provider: "ollama"  # Code/architecture privacy
```

---

### Phase 3: Manual Override (Power Users)
**Add settings UI for manual control:**

Settings > Memory > Provider Selection
- Smart (default)
- Manual selection per provider
- Per-persona overrides

---

### Phase 4: Budget Awareness
**Add cost tracking and budget limits:**

- Track monthly API costs
- Alert at thresholds
- Auto-switch to local if budget exceeded

---

### Phase 5: Advanced Rules (Expert)
**Add rule-based selection:**

```yaml
selection_rules:
  - condition: "chinese_ratio > 0.5"
    provider: "qwen"
  
  - condition: "domain == 'academic'"
    provider: "glm"
  
  - condition: "privacy_level == 'high'"
    provider: "ollama"
```

---

## Decision Matrix for Users

| Use Case | Recommended | Reason |
|----------|-------------|--------|
| **Chinese notes** | Qwen | Best Chinese language support |
| **English notes** | Ollama | Free, private, good quality |
| **Mixed language** | Qwen | Strong multilingual |
| **Academic research** | GLM | Academic pedigree, trusted |
| **Private/sensitive** | Ollama | Local, never leaves device |
| **Images + text** | MiniMax | Multimodal embeddings |
| **Offline work** | Ollama | No internet needed |
| **Budget-conscious** | Ollama | Completely free |
| **Production/serious** | Qwen | Best quality/cost balance |

---

## Next Steps

1. **Implement smart defaults** (Phase 1) with multi-provider config
2. **Add logging** to show which provider was selected and why
3. **Collect telemetry** on auto-selection accuracy
4. **Design settings UI** for manual override (Phase 3)
5. **Add cost tracking** for budget awareness (Phase 4)

This approach balances:
- **Simplicity:** Works automatically for 90% of users
- **Control:** Power users can override
- **Transparency:** Logs explain decisions
- **Optimization:** Always uses the best provider for the content

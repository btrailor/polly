# Dynamic Provider Switching - Visual UX Flow

## Quick Decision Guide

### When to Use Each Provider

```
                    ┌─────────────────┐
                    │  New Memory     │
                    │  Operation      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Analyze Content │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐         ┌─────▼─────┐       ┌─────▼─────┐
   │ Privacy │         │ Language  │       │  Domain   │
   │  Check  │         │   Check   │       │   Check   │
   └────┬────┘         └─────┬─────┘       └─────┬─────┘
        │                    │                    │
        │              ┌─────┴─────┐              │
        │              │           │              │
        │         ┌────▼────┐ ┌───▼────┐         │
        │         │Chinese? │ │English?│         │
        │         └────┬────┘ └───┬────┘         │
        │              │          │              │
   ┌────▼────┐    ┌───▼───┐  ┌───▼───┐    ┌────▼────┐
   │ OLLAMA  │    │ QWEN  │  │OLLAMA │    │  GLM    │
   │ (Local) │    │(Cloud)│  │(Local)│    │(Cloud)  │
   └─────────┘    └───────┘  └───────┘    └─────────┘
   Private/        Chinese    English     Academic
   Sensitive       Content    Content     Research
```

---

## Smart Selection Logic (Code Sketch)

```python
class SmartProviderSelector:
    """
    Automatically select best provider based on content and context.
    """
    
    def select_provider(self, content: str, metadata: Dict) -> str:
        """
        Multi-factor decision tree for provider selection.
        """
        
        # 1. PRIVACY OVERRIDE (highest priority)
        if self._is_sensitive_content(content, metadata):
            return 'ollama'  # Always use local for sensitive data
        
        # 2. LANGUAGE DETECTION
        language_info = self._detect_language(content)
        
        if language_info['chinese_ratio'] > 0.3:
            # Primarily Chinese content
            if metadata.get('domain') == 'academic':
                return 'glm'  # Chinese + Academic = GLM
            elif metadata.get('has_images'):
                return 'minimax'  # Chinese + Images = MiniMax
            else:
                return 'qwen'  # Chinese = Qwen (best general)
        
        # 3. DOMAIN-SPECIFIC
        domain = metadata.get('domain')
        if domain == 'academic':
            return 'glm'  # Research papers, citations
        elif domain == 'code':
            return 'ollama'  # Code snippets stay local
        
        # 4. PERSONA PREFERENCE
        persona = metadata.get('persona')
        if persona == 'Professor':
            return 'glm'  # Academic persona
        elif persona == 'Architect':
            return 'ollama'  # Code/design privacy
        
        # 5. BUDGET CHECK
        if self._is_over_budget():
            return 'ollama'  # Fall back to free
        
        # 6. DEFAULT
        return 'qwen'  # Best balance: quality + cost + speed
    
    def _is_sensitive_content(self, content: str, metadata: Dict) -> bool:
        """Detect if content should stay local."""
        sensitive_tags = ['private', 'confidential', 'personal', 'secret']
        
        # Check tags
        if any(tag in metadata.get('tags', []) for tag in sensitive_tags):
            return True
        
        # Check for PII patterns
        if self._has_pii(content):
            return True
        
        # Check vault location
        if metadata.get('vault_path', '').startswith('Private/'):
            return True
        
        return False
    
    def _detect_language(self, content: str) -> Dict:
        """Detect language distribution in content."""
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', content))
        total_chars = len(content)
        
        return {
            'chinese_ratio': chinese_chars / total_chars if total_chars > 0 else 0,
            'is_multilingual': 0.1 < chinese_chars / total_chars < 0.9
        }
    
    def _has_pii(self, content: str) -> bool:
        """Detect personally identifiable information."""
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',  # Email
            r'\b\d{16}\b',  # Credit card
            r'\b\d{3}-\d{3}-\d{4}\b'  # Phone
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in pii_patterns)
```

---

## Recommended UX Flow (Phased Rollout)

### Phase 1: Invisible Smart Defaults (Week 1)
**No UI changes, just smart backend logic**

**Implementation:**
```python
# In Mem0Adapter initialization
self.provider_selector = SmartProviderSelector(config)

# In add_memory()
selected_provider = self.provider_selector.select_provider(content, metadata)
logger.info(f"[Mem0] Using {selected_provider} (reason: {reason})")
```

**User Experience:**
- No UI changes
- Works automatically
- Logs show decisions: `[Mem0] Using Qwen (Chinese content detected)`

**Success Metric:** 
- 90%+ of selections are optimal for content type
- No user complaints about provider choices

---

### Phase 2: Subtle Indicators (Week 2-3)
**Add small visual indicators showing which provider is active**

**UI Addition 1: Status Bar Indicator**
```
┌─────────────────────────────────────────┐
│ Polly                      Memory: Qwen │ ← Small indicator
└─────────────────────────────────────────┘
```

**UI Addition 2: Hover Tooltip**
```
Memory: Qwen
───────────────────────
• Using Qwen for better Chinese support
• Detected 80% Chinese content
• [Change Provider...]
```

**Success Metric:**
- Users notice the indicator
- <5% click to change (most are happy with auto-selection)

---

### Phase 3: Manual Override (Week 4)
**Add settings panel for manual control**

**Settings > Memory > Provider**

```
┌─────────────────────────────────────────┐
│ Memory Provider Selection               │
├─────────────────────────────────────────┤
│                                         │
│ Provider Mode:                          │
│ ● Smart (Automatic) ← Recommended       │
│   ○ Manual Selection                    │
│                                         │
│ ┌───────────────────────────────────┐   │
│ │ Smart Selection Rules             │   │
│ ├───────────────────────────────────┤   │
│ │ ☑ Use local for private content   │   │
│ │ ☑ Use Qwen for Chinese content    │   │
│ │ ☑ Use GLM for academic content    │   │
│ │ ☑ Optimize for cost               │   │
│ └───────────────────────────────────┘   │
│                                         │
│ Current Selection: Qwen                 │
│ Reason: Chinese content (85%)           │
│                                         │
│ Override for this session:              │
│ [ Ollama ] [ Qwen ] [ MiniMax ] [ GLM ] │
│                                         │
└─────────────────────────────────────────┘
```

**Success Metric:**
- Power users find the settings
- <10% override the automatic selection

---

### Phase 4: Per-Note Override (Future)
**Allow per-note provider selection**

**In Note Editor:**
```
┌─────────────────────────────────────────┐
│ Research Notes.md               [⚙️]    │
├─────────────────────────────────────────┤
│                                         │
│ Title: Machine Learning Research        │
│                                         │
│ Memory Provider: ● Smart  ○ Manual      │
│                                         │
│ Content:                                │
│ Today I learned about transformers...   │
│                                         │
└─────────────────────────────────────────┘
```

---

## Real-World Scenarios

### Scenario 1: Research Student (Multilingual)

**Context:**
- User: Graduate student
- Language: Mixed English (papers) + Chinese (notes)
- Domain: Academic research

**Auto-Selection Logic:**
```python
# English research paper → GLM (academic domain)
"Attention is All You Need paper analysis..."
→ GLM (academic + English)

# Chinese study notes → Qwen (Chinese + general)
"今天的学习笔记：transformer架构..."
→ Qwen (Chinese + not academic domain)

# Mixed language synthesis → Qwen (multilingual)
"The paper discusses 注意力机制 which is..."
→ Qwen (multilingual + balanced)
```

**User Experience:**
- Transparent: Always gets the best provider
- No intervention needed
- Can check logs if curious

---

### Scenario 2: Privacy-Conscious Developer

**Context:**
- User: Software engineer
- Concern: Code privacy
- Domain: Software development

**Auto-Selection Logic:**
```python
# Code snippets → Ollama (code domain + privacy)
"def authenticate_user(password)..."
→ Ollama (code + stay local)

# Architecture notes with diagram → Ollama (privacy)
"System architecture: [private company details]"
→ Ollama (privacy tag detected)

# Public documentation → Qwen (not sensitive)
"How to use React hooks..."
→ Qwen (public info + quality)
```

**User Experience:**
- Safe: Sensitive code stays local
- Fast: Local inference for frequent operations
- Smart: Public docs use better cloud models

---

### Scenario 3: Budget-Conscious Student

**Context:**
- User: Undergraduate student
- Budget: ¥20/month
- Usage: Heavy (1000+ memories/month)

**Auto-Selection Logic:**
```python
# Week 1 (budget: ¥20 remaining)
"Notes from lecture..." → Qwen (budget available)

# Week 2 (budget: ¥15 remaining)
"More lecture notes..." → Qwen (still good)

# Week 3 (budget: ¥5 remaining, 75% used)
"Additional notes..." → Qwen (warning logged)

# Week 4 (budget: ¥1 remaining, 95% used)
"Final exam notes..." → Ollama (auto-switched to free)
```

**User Experience:**
- Cost-aware: Automatic budget protection
- Notified: Alert at 80% budget
- Seamless: No manual intervention needed

---

## Implementation Priority

### High Priority (Phase 1)
✅ **Implement smart selection logic**
- Language detection
- Privacy detection
- Domain detection
- Default routing

### Medium Priority (Phase 2-3)
📋 **Add UX indicators**
- Status bar indicator
- Settings panel
- Manual override

### Low Priority (Future)
🔮 **Advanced features**
- Per-note provider selection
- Performance-based auto-switching
- Cost analytics dashboard
- A/B testing different selection strategies

---

## Testing the Selection Logic

### Test Cases

```python
def test_privacy_override():
    """Privacy always wins."""
    content = "My password is 12345"
    metadata = {'tags': ['private']}
    
    assert selector.select_provider(content, metadata) == 'ollama'

def test_chinese_content():
    """Chinese content → Qwen."""
    content = "今天学习了机器学习基础知识"
    metadata = {}
    
    assert selector.select_provider(content, metadata) == 'qwen'

def test_academic_domain():
    """Academic + English → GLM."""
    content = "Literature review of transformer architectures"
    metadata = {'domain': 'academic'}
    
    assert selector.select_provider(content, metadata) == 'glm'

def test_budget_exhausted():
    """No budget → Ollama."""
    selector.budget_tracker.set_usage(0.95)  # 95% used
    content = "Any content"
    metadata = {}
    
    assert selector.select_provider(content, metadata) == 'ollama'
```

---

## Monitoring & Telemetry

### Metrics to Track

```python
{
    "provider_selections": {
        "ollama": {
            "count": 450,
            "reasons": {
                "privacy": 200,
                "budget": 150,
                "default": 100
            }
        },
        "qwen": {
            "count": 300,
            "reasons": {
                "chinese_content": 250,
                "default": 50
            }
        },
        "glm": {
            "count": 50,
            "reasons": {
                "academic_domain": 40,
                "user_override": 10
            }
        }
    },
    "user_overrides": 15,  # How many times user manually changed
    "selection_accuracy": 0.92  # 92% of selections not overridden
}
```

---

## Key Takeaways

1. **Start Simple:** Phase 1 with invisible smart defaults
2. **Language is Key:** Chinese vs. English is the biggest differentiator
3. **Privacy Wins:** Always override to local for sensitive content
4. **Budget Awareness:** Automatic fallback to free prevents surprises
5. **Show, Don't Tell:** Subtle indicators > complex settings
6. **Trust but Verify:** Smart defaults with manual override option

The goal is **invisible intelligence** - users don't think about providers, they just get the best results automatically.

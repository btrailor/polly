# Phase 11: Grok Safety Filter Specification

**Document Version:** 1.0  
**Last Updated:** January 28, 2026  
**Status:** Critical - Mandatory for Grok integration  
**Related:** [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md)

---

## Executive Summary

This document specifies the mandatory safety filtering system for Grok (xAI) integration. Due to documented concerns about conspiratorial thinking, extremist content, and misinformation in Grok outputs, this safety filter is **NON-NEGOTIABLE** and **CANNOT BE DISABLED** by users.

**Key Requirements:**
- Pre-request task validation (whitelist/blacklist)
- Post-response content filtering
- Pattern matching for harmful content
- User consent before enabling Grok
- Comprehensive logging for safety auditing
- Zero tolerance for unsafe content

---

## Background & Rationale

### User Statement

> "I don't want Grok contaminating knowledge bases with conspiratorial thinking or nazi propaganda"

### Safety Concerns

1. **Conspiratorial Thinking:** Grok has shown tendencies to promote conspiracy theories and unfounded claims
2. **Extremist Content:** Risk of generating content that promotes extremist ideologies
3. **Misinformation:** Potential for spreading false or misleading information
4. **Political Bias:** Known biases in political and social commentary

### Approach

Rather than blocking Grok entirely, we implement a **comprehensive two-layer filtering system:**

1. **Pre-Request Validation:** Block requests for task types where Grok is unreliable
2. **Post-Response Filtering:** Scan all responses for harmful patterns before displaying

---

## Architecture

### Two-Layer Safety System

```
┌─────────────────────────────────────────────────────────┐
│              User Request to Grok                       │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│           LAYER 1: Pre-Request Validation               │
│                                                          │
│  ✓ Is task type in WHITELIST?                          │
│  ✗ Is task type in BLACKLIST?                          │
│                                                          │
│  WHITELIST: code, technical, math, translation          │
│  BLACKLIST: politics, history, news, medical            │
└─────────────────────────────────────────────────────────┘
                          │
                    PASS  │  FAIL → Route to different provider
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Grok API Call                              │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│      LAYER 2: Post-Response Content Filtering           │
│                                                          │
│  Pattern Matching:                                      │
│  • Conspiracy theories                                  │
│  • Extremist ideology                                   │
│  • Misinformation markers                               │
│  • Hate speech                                          │
│  • Political propaganda                                 │
└─────────────────────────────────────────────────────────┘
                          │
                    CLEAN │  FLAGGED → Discard + fallback
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Return to User                             │
└─────────────────────────────────────────────────────────┘
```

---

## Layer 1: Pre-Request Validation

### Task Whitelist (ALLOWED)

Grok is **ONLY** allowed for these task types:

```python
GROK_WHITELIST_TASKS = [
    # Code-related
    "code_completion",
    "code_review",
    "code_debugging",
    "code_refactoring",
    "api_documentation",
    
    # Technical
    "technical_explanation",
    "technical_documentation",
    "system_design",
    "algorithm_explanation",
    
    # Data & Math
    "data_analysis",
    "data_visualization",
    "math_problems",
    "statistical_analysis",
    
    # Language
    "translation",
    "grammar_check",
    "text_formatting",
    
    # Safe general tasks
    "recipe",
    "how_to_guide",  # non-political
    "product_comparison"  # factual
]
```

### Task Blacklist (FORBIDDEN)

Grok is **NEVER** allowed for these task types:

```python
GROK_BLACKLIST_TASKS = [
    # Political & Social
    "political_analysis",
    "political_commentary",
    "election_analysis",
    "social_issues",
    "current_events_political",
    
    # Historical
    "historical_events",
    "historical_analysis",
    "war_history",
    "genocide_history",
    
    # Medical & Health
    "medical_advice",
    "health_diagnosis",
    "mental_health",
    "drug_information",
    
    # News & Current Events
    "news_summary",
    "current_events",
    "breaking_news",
    "event_analysis",
    
    # Sensitive Topics
    "religious_analysis",
    "conspiracy_theory_evaluation",
    "controversial_topics",
    "legal_advice",
    
    # Content that could be biased
    "opinion_piece",
    "editorial",
    "persuasive_writing"
]
```

### Implementation

```python
# core/safety/grok_filter.py
class GrokSafetyFilter:
    """Mandatory safety filter for Grok integration"""
    
    WHITELIST_TASKS = [
        "code_completion",
        "code_review",
        "technical_explanation",
        "data_analysis",
        "math_problems",
        "translation",
        # ... (see above)
    ]
    
    BLACKLIST_TASKS = [
        "political_analysis",
        "historical_events",
        "medical_advice",
        "news_summary",
        "social_issues",
        # ... (see above)
    ]
    
    def is_task_allowed(self, task_type: str) -> bool:
        """
        Check if task type is allowed for Grok
        
        Logic:
        1. If in blacklist → BLOCK
        2. If in whitelist → ALLOW
        3. If neither → BLOCK (conservative default)
        
        Returns:
            True if task is allowed, False otherwise
        """
        # Blacklist takes precedence
        if task_type in self.BLACKLIST_TASKS:
            logger.warning(f"Grok blocked: task '{task_type}' is blacklisted")
            return False
        
        # Must be in whitelist to proceed
        if task_type in self.WHITELIST_TASKS:
            return True
        
        # Unknown tasks are blocked by default (conservative)
        logger.warning(f"Grok blocked: task '{task_type}' not in whitelist")
        return False
    
    def suggest_alternative_provider(self, task_type: str) -> str:
        """Suggest better provider for blocked task"""
        alternatives = {
            "political_analysis": "anthropic",  # Claude more balanced
            "historical_events": "anthropic",
            "medical_advice": "openai",  # GPT-4 safer
            "news_summary": "perplexity",  # Built for this
        }
        return alternatives.get(task_type, "anthropic")
```

---

## Layer 2: Post-Response Content Filtering

### Pattern Categories

#### 1. Conspiracy Theory Patterns

```python
CONSPIRACY_PATTERNS = [
    # Deep state & secret cabals
    r"\b(deep state|shadow government|illuminati|cabal)\b",
    r"\bnew world order\b",
    r"\b(they|elites) (?:don't want you to know|are hiding|control)\b",
    
    # False flag & hoax narratives
    r"\b(false flag|hoax|crisis actors|staged)\b",
    r"\b(fake|staged|manufactured) (?:event|attack|shooting)\b",
    
    # Conspiracy keywords
    r"\b(wake up|sheeple|red pill|truth movement)\b",
    r"\bmainstream media (?:lies|hiding|covering up)\b",
    r"\b(agenda|plan) to (?:control|enslave|depopulate)\b",
    
    # QAnon & related
    r"\b(q anon|qanon|the storm|wwg1wga)\b",
    r"\b(white hats|black hats) (?:in control|winning)\b",
    
    # Anti-science conspiracy
    r"\b(?:vaccines?|covid|pandemic|virus) (?:is a|are a) (?:hoax|scam|plot)\b",
    r"\b(?:chemtrails|5g|fluoride) (?:control|poison|mind control)\b"
]
```

#### 2. Extremist Ideology Patterns

```python
EXTREMIST_PATTERNS = [
    # Nazi & fascist content
    r"\b(nazi|fascist|hitler) (?:was|were|had) (?:right|good|correct)\b",
    r"\b(third reich|aryan|master race) (?:was|were|had) (?:right|good|justified)\b",
    r"\bholocaust (?:didn't happen|was fake|was exaggerated)\b",
    
    # White supremacy
    r"\b(white|european) (?:supremacy|nationalism|replacement)\b",
    r"\b(jews|blacks|muslims|immigrants) (?:control|are destroying|are inferior)\b",
    r"\b(racial|ethnic) (?:purity|superiority|hierarchy)\b",
    
    # Violent extremism
    r"\b(race war|civil war|boogaloo|day of the rope)\b",
    r"\b(revolution|uprising|armed resistance) (?:is necessary|coming soon)\b",
    r"\b(?:kill|eliminate|purge) (?:the|all) (?:jews|blacks|muslims|liberals|conservatives)\b",
    
    # Anti-democratic
    r"\bdemocracy (?:is|has) (?:failed|dead|a lie)\b",
    r"\b(?:military coup|martial law|dictatorship) (?:is needed|would be better)\b"
]
```

#### 3. Misinformation Patterns

```python
MISINFORMATION_PATTERNS = [
    # Election fraud
    r"\b(?:election|vote|voting) (?:was|were) (?:rigged|stolen|fraudulent)\b",
    r"\bmassive (?:voter fraud|election fraud)\b",
    r"\b(?:dominion|smartmatic) (?:rigged|flipped|switched) votes\b",
    
    # COVID misinformation
    r"\bcovid (?:is|was) (?:planned|created|released) (?:by|to)\b",
    r"\b(?:vaccine|vaccination) (?:contains|has|includes) (?:microchips|5g|tracking)\b",
    r"\b(?:ivermectin|hydroxychloroquine) (?:cures|prevents) covid\b",
    
    # Climate denial
    r"\bclimate change (?:is|was) (?:a hoax|fake|manufactured)\b",
    r"\bglobal warming (?:is|was) (?:a lie|propaganda|a scam)\b",
    
    # Media manipulation
    r"\b(?:all|most|mainstream) (?:media|news) (?:is|are) (?:fake|propaganda|controlled)\b",
    r"\b(?:censorship|suppression) (?:of|the) (?:truth|real story)\b"
]
```

#### 4. Hate Speech Patterns

```python
HATE_SPEECH_PATTERNS = [
    # Slurs (masked examples)
    r"\b[censored_slurs]\b",
    
    # Dehumanization
    r"\b(?:jews|blacks|muslims|immigrants|lgbt) (?:are|aren't) (?:human|people)\b",
    r"\b(?:vermin|parasites|disease|plague) (?:metaphor for groups)\b",
    
    # Violent rhetoric
    r"\b(?:exterminate|eliminate|cleanse|purge) (?:the|all) (?:ethnic/religious groups)\b"
]
```

### Content Validation Implementation

```python
# core/safety/grok_filter.py (continued)
class GrokSafetyFilter:
    
    # Pattern definitions (see above)
    RED_FLAGS = {
        "conspiracy_patterns": CONSPIRACY_PATTERNS,
        "extremist_patterns": EXTREMIST_PATTERNS,
        "misinformation_patterns": MISINFORMATION_PATTERNS,
        "hate_speech_patterns": HATE_SPEECH_PATTERNS
    }
    
    def validate_content(self, content: str) -> tuple[bool, list[str]]:
        """
        Validate response content for safety issues
        
        Args:
            content: The response text from Grok
        
        Returns:
            (is_safe, list_of_flags)
            - is_safe: True if content passes all checks
            - list_of_flags: List of matched patterns (empty if safe)
        """
        flags = []
        content_lower = content.lower()
        
        for category, patterns in self.RED_FLAGS.items():
            for pattern in patterns:
                match = re.search(pattern, content_lower, re.IGNORECASE)
                if match:
                    flags.append({
                        "category": category,
                        "pattern": pattern,
                        "matched_text": match.group(0),
                        "context": self._extract_context(content, match.start(), match.end())
                    })
                    logger.warning(f"Grok content flagged: {category} - {match.group(0)}")
        
        return (len(flags) == 0, flags)
    
    def _extract_context(self, text: str, start: int, end: int, window: int = 50) -> str:
        """Extract surrounding context for flagged match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        return text[context_start:context_end]
    
    def get_severity(self, flags: list[dict]) -> str:
        """
        Determine severity of safety issues
        
        Returns: 'low', 'medium', 'high', 'critical'
        """
        if not flags:
            return "safe"
        
        severity_map = {
            "hate_speech_patterns": "critical",
            "extremist_patterns": "critical",
            "conspiracy_patterns": "high",
            "misinformation_patterns": "medium"
        }
        
        max_severity = "low"
        severity_order = ["low", "medium", "high", "critical"]
        
        for flag in flags:
            flag_severity = severity_map.get(flag["category"], "low")
            if severity_order.index(flag_severity) > severity_order.index(max_severity):
                max_severity = flag_severity
        
        return max_severity
```

---

## User Consent Flow

### First-Time Setup

When user attempts to enable Grok:

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️  Grok Safety Warning                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Grok (xAI) integration requires mandatory safety       │
│  filters due to concerns about:                         │
│                                                          │
│  • Conspiratorial thinking                              │
│  • Extremist content                                    │
│  • Misinformation                                       │
│                                                          │
│  Safety Measures:                                       │
│  ✓ Grok is ONLY used for code, technical, and math     │
│     tasks                                               │
│  ✓ All responses are filtered for harmful content      │
│  ✓ Unsafe responses are blocked automatically          │
│  ✓ You cannot disable these safety filters             │
│                                                          │
│  Allowed Tasks:                                         │
│  • Code completion and review                          │
│  • Technical explanations                              │
│  • Data analysis                                        │
│  • Math problems                                        │
│  • Translation                                          │
│                                                          │
│  Blocked Tasks:                                         │
│  • Political analysis                                   │
│  • Historical events                                    │
│  • Medical advice                                       │
│  • News summaries                                       │
│  • Social issues                                        │
│                                                          │
│  Alternative Providers:                                 │
│  For blocked tasks, Polly will automatically use        │
│  safer alternatives like Claude or GPT-4.               │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  [ ] I understand and accept these restrictions         │
│                                                          │
│  [Cancel]  [Enable Grok with Safety Filters]           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Implementation

```python
# core/safety/grok_consent.py
class GrokConsentManager:
    """Manage user consent for Grok usage"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def has_consent(self) -> bool:
        """Check if user has consented to Grok usage"""
        return self.config.get("models.cloud.grok.user_consent", False)
    
    async def request_consent(self) -> bool:
        """
        Show consent dialog and record response
        
        Returns:
            True if user consented, False otherwise
        """
        # Show dialog in UI (IPC to frontend)
        consent = await self._show_consent_dialog()
        
        if consent:
            # Record consent in config
            self.config.set("models.cloud.grok.user_consent", True)
            self.config.set("models.cloud.grok.consent_timestamp", datetime.now())
            await self.config.save()
            
            logger.info("User consented to Grok safety filters")
        else:
            logger.info("User declined Grok integration")
        
        return consent
    
    async def _show_consent_dialog(self) -> bool:
        """Show consent UI and wait for response"""
        # IPC call to frontend
        from core.ipc import send_to_frontend
        
        response = await send_to_frontend("grok:show-consent-dialog", {
            "whitelist": GrokSafetyFilter.WHITELIST_TASKS,
            "blacklist": GrokSafetyFilter.BLACKLIST_TASKS
        })
        
        return response.get("consented", False)
```

---

## Logging & Auditing

### Safety Event Logging

```python
# core/safety/logger.py
class SafetyLogger:
    """Log all Grok safety events for auditing"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def log_blocked_task(self, task_type: str, reason: str):
        """Log pre-request block"""
        await self.db.insert("grok_safety_log", {
            "timestamp": datetime.now(),
            "event_type": "blocked_task",
            "task_type": task_type,
            "reason": reason,
            "severity": "medium"
        })
    
    async def log_filtered_content(self, 
                                   task_type: str,
                                   flags: list[dict],
                                   severity: str):
        """Log post-response filter hit"""
        await self.db.insert("grok_safety_log", {
            "timestamp": datetime.now(),
            "event_type": "filtered_content",
            "task_type": task_type,
            "flags": json.dumps(flags),
            "severity": severity,
            "flag_count": len(flags)
        })
    
    async def log_safe_completion(self, task_type: str):
        """Log successful safe completion"""
        await self.db.insert("grok_safety_log", {
            "timestamp": datetime.now(),
            "event_type": "safe_completion",
            "task_type": task_type,
            "severity": "safe"
        })
    
    async def get_safety_stats(self, days: int = 30) -> dict:
        """Get safety statistics for reporting"""
        since = datetime.now() - timedelta(days=days)
        
        logs = await self.db.query(
            "grok_safety_log",
            {"timestamp": {"$gte": since}}
        )
        
        return {
            "total_requests": len(logs),
            "blocked_tasks": len([l for l in logs if l["event_type"] == "blocked_task"]),
            "filtered_content": len([l for l in logs if l["event_type"] == "filtered_content"]),
            "safe_completions": len([l for l in logs if l["event_type"] == "safe_completion"]),
            "critical_flags": len([l for l in logs if l.get("severity") == "critical"]),
            "most_common_flags": self._aggregate_flags(logs)
        }
```

### Database Schema

```sql
-- Grok safety event log
CREATE TABLE grok_safety_log (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    event_type TEXT NOT NULL,  -- blocked_task, filtered_content, safe_completion
    task_type TEXT,
    reason TEXT,
    flags TEXT,  -- JSON array of matched patterns
    severity TEXT,  -- safe, low, medium, high, critical
    flag_count INTEGER,
    conversation_id INTEGER,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE INDEX idx_grok_safety_timestamp ON grok_safety_log(timestamp);
CREATE INDEX idx_grok_safety_event_type ON grok_safety_log(event_type);
CREATE INDEX idx_grok_safety_severity ON grok_safety_log(severity);
```

---

## Error Handling

### Exception Types

```python
# core/safety/errors.py

class GrokSafetyError(Exception):
    """Base class for Grok safety errors"""
    pass

class GrokTaskForbiddenError(GrokSafetyError):
    """Task type not allowed for Grok"""
    def __init__(self, task_type: str, reason: str = None):
        self.task_type = task_type
        self.reason = reason or f"Task type '{task_type}' is not allowed for Grok"
        super().__init__(self.reason)

class GrokContentFilteredError(GrokSafetyError):
    """Response content failed safety filter"""
    def __init__(self, flags: list[dict], severity: str):
        self.flags = flags
        self.severity = severity
        message = f"Response filtered: {len(flags)} safety issues detected (severity: {severity})"
        super().__init__(message)

class GrokConsentRequiredError(GrokSafetyError):
    """User has not consented to Grok usage"""
    def __init__(self):
        super().__init__("User consent required before using Grok")
```

### Fallback Strategy

When Grok is blocked or filtered:

```python
# core/providers/grok.py (error handling)
class GrokAdapter(ProviderAdapter):
    
    async def complete(self, messages: list[dict], **kwargs) -> CompletionResponse:
        """Complete with safety filtering"""
        
        try:
            # Check consent
            if not self.consent_manager.has_consent():
                raise GrokConsentRequiredError()
            
            # Pre-request validation
            task_type = kwargs.get("task_type", "general")
            if not self.safety.is_task_allowed(task_type):
                # Suggest alternative provider
                alternative = self.safety.suggest_alternative_provider(task_type)
                raise GrokTaskForbiddenError(
                    task_type=task_type,
                    reason=f"Use {alternative} instead for {task_type}"
                )
            
            # Make API call
            response = await self._make_grok_request(messages, **kwargs)
            
            # Post-response filtering
            is_safe, flags = self.safety.validate_content(response.content)
            if not is_safe:
                severity = self.safety.get_severity(flags)
                await self.safety_logger.log_filtered_content(task_type, flags, severity)
                raise GrokContentFilteredError(flags=flags, severity=severity)
            
            # Log safe completion
            await self.safety_logger.log_safe_completion(task_type)
            
            return response
        
        except GrokSafetyError as e:
            # Log and re-raise for router to handle fallback
            logger.warning(f"Grok safety error: {e}")
            raise
```

Router handles fallback:

```python
# core/router_v2.py
class IntelligentRouter:
    
    async def complete_with_fallback(self, messages, task_type, confidence):
        primary = await self.route(messages, task_type, confidence)
        
        try:
            return await primary.complete(messages, task_type=task_type)
        
        except GrokTaskForbiddenError as e:
            # Use suggested alternative
            logger.info(f"Grok forbidden, using {e.reason}")
            alternative = self.providers[e.suggested_provider]
            return await alternative.complete(messages, task_type=task_type)
        
        except GrokContentFilteredError as e:
            # Fall back to safer provider
            logger.warning(f"Grok content filtered ({e.severity}), using fallback")
            fallback = self._get_safe_fallback(task_type)
            return await fallback.complete(messages, task_type=task_type)
```

---

## Testing

### Unit Tests

```python
# tests/test_grok_safety.py
import pytest
from core.safety.grok_filter import GrokSafetyFilter

@pytest.fixture
def safety_filter():
    return GrokSafetyFilter()

class TestTaskValidation:
    def test_whitelist_allowed(self, safety_filter):
        assert safety_filter.is_task_allowed("code_completion") == True
        assert safety_filter.is_task_allowed("technical_explanation") == True
        assert safety_filter.is_task_allowed("math_problems") == True
    
    def test_blacklist_blocked(self, safety_filter):
        assert safety_filter.is_task_allowed("political_analysis") == False
        assert safety_filter.is_task_allowed("news_summary") == False
        assert safety_filter.is_task_allowed("medical_advice") == False
    
    def test_unknown_task_blocked(self, safety_filter):
        # Conservative default: block unknown tasks
        assert safety_filter.is_task_allowed("unknown_task_type") == False

class TestContentFiltering:
    def test_conspiracy_detection(self, safety_filter):
        text = "The deep state is hiding the truth about the election fraud."
        is_safe, flags = safety_filter.validate_content(text)
        
        assert is_safe == False
        assert len(flags) >= 2  # "deep state" + "election fraud"
        assert any("conspiracy" in f["category"] for f in flags)
    
    def test_extremist_detection(self, safety_filter):
        text = "Hitler had some good ideas about racial purity."
        is_safe, flags = safety_filter.validate_content(text)
        
        assert is_safe == False
        assert any("extremist" in f["category"] for f in flags)
    
    def test_misinformation_detection(self, safety_filter):
        text = "COVID vaccines contain microchips for tracking."
        is_safe, flags = safety_filter.validate_content(text)
        
        assert is_safe == False
        assert any("misinformation" in f["category"] for f in flags)
    
    def test_clean_technical_content(self, safety_filter):
        text = """
        Here's a Python function to calculate Fibonacci numbers:
        
        def fibonacci(n):
            if n <= 1:
                return n
            return fibonacci(n-1) + fibonacci(n-2)
        
        This uses recursion but can be optimized with memoization.
        """
        is_safe, flags = safety_filter.validate_content(text)
        
        assert is_safe == True
        assert len(flags) == 0
    
    def test_severity_classification(self, safety_filter):
        hate_speech = "Jews are parasites."
        _, flags = safety_filter.validate_content(hate_speech)
        assert safety_filter.get_severity(flags) == "critical"
        
        conspiracy = "The moon landing was fake."
        _, flags = safety_filter.validate_content(conspiracy)
        assert safety_filter.get_severity(flags) in ["high", "medium"]
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_grok_blocked_task_fallback():
    """Test that router falls back when Grok task is blocked"""
    router = IntelligentRouter(config)
    
    # Request political analysis (blacklisted for Grok)
    response = await router.complete_with_fallback(
        [{"role": "user", "content": "Analyze the election results"}],
        task_type="political_analysis",
        confidence="balanced"
    )
    
    # Should use fallback provider (not Grok)
    assert response.provider != "grok"
    assert response.provider in ["anthropic", "openai"]

@pytest.mark.asyncio
async def test_grok_content_filtered_fallback():
    """Test that filtered content triggers fallback"""
    router = IntelligentRouter(config)
    
    # Mock Grok to return unsafe content
    with patch.object(GrokAdapter, '_make_grok_request') as mock_request:
        mock_request.return_value = CompletionResponse(
            content="The deep state is controlling everything...",
            model="grok-2",
            tokens_in=50,
            tokens_out=100,
            cost=0.01,
            provider="grok"
        )
        
        # Should filter and fall back
        response = await router.complete_with_fallback(
            [{"role": "user", "content": "Write code"}],
            task_type="code_completion",
            confidence="balanced"
        )
        
        # Should have used fallback
        assert response.provider != "grok"
```

---

## Monitoring & Alerts

### Safety Dashboard

```javascript
// Settings > Models > Grok > Safety Dashboard
{
  "last_30_days": {
    "total_requests": 142,
    "safe_completions": 128,
    "blocked_tasks": 8,
    "filtered_content": 6,
    "safety_rate": "95.1%"
  },
  "severity_breakdown": {
    "critical": 2,
    "high": 3,
    "medium": 1,
    "low": 0
  },
  "most_common_flags": [
    {"category": "conspiracy_patterns", "count": 4},
    {"category": "misinformation_patterns", "count": 2}
  ],
  "recommended_action": "Consider disabling Grok due to repeated safety issues"
}
```

### Automatic Disable

If safety issues exceed threshold:

```python
# core/safety/monitor.py
class GrokSafetyMonitor:
    """Monitor Grok safety and auto-disable if needed"""
    
    CRITICAL_FLAG_THRESHOLD = 5  # per week
    FILTER_RATE_THRESHOLD = 0.20  # 20% of responses filtered
    
    async def check_safety_health(self) -> dict:
        """Check if Grok should be auto-disabled"""
        stats = await self.safety_logger.get_safety_stats(days=7)
        
        health = {
            "healthy": True,
            "warnings": [],
            "should_disable": False
        }
        
        # Check critical flags
        if stats["critical_flags"] >= self.CRITICAL_FLAG_THRESHOLD:
            health["healthy"] = False
            health["should_disable"] = True
            health["warnings"].append(
                f"{stats['critical_flags']} critical safety issues in past week"
            )
        
        # Check filter rate
        total = stats["total_requests"]
        filtered = stats["filtered_content"]
        if total > 0:
            filter_rate = filtered / total
            if filter_rate >= self.FILTER_RATE_THRESHOLD:
                health["healthy"] = False
                health["warnings"].append(
                    f"{filter_rate:.1%} of responses filtered (threshold: {self.FILTER_RATE_THRESHOLD:.1%})"
                )
        
        return health
    
    async def auto_disable_if_needed(self):
        """Auto-disable Grok if safety health is poor"""
        health = await self.check_safety_health()
        
        if health["should_disable"]:
            logger.critical(f"Auto-disabling Grok: {health['warnings']}")
            
            # Disable in config
            await self.config.set("models.cloud.grok.enabled", False)
            await self.config.set("models.cloud.grok.auto_disabled", True)
            await self.config.set("models.cloud.grok.disable_reason", health["warnings"])
            
            # Notify user
            await self._notify_user_of_disable(health["warnings"])
```

---

## User Communication

### When Content is Filtered

```
Polly: I encountered an issue with the response from Grok and 
automatically switched to Claude for your request.

[Expand for details]
  Reason: Content safety filter triggered
  Severity: High
  Matched patterns: 2 conspiracy theory indicators
  Alternative used: Claude Sonnet 4
  
  This is expected behavior to protect against misinformation.
```

### When Task is Blocked

```
Polly: I'm using Claude instead of Grok for this request because 
Grok is not allowed for political analysis tasks due to safety 
concerns.

[View Grok safety settings]
```

---

## Configuration

```yaml
# config.yaml
models:
  cloud:
    grok:
      enabled: false  # Must be manually enabled with consent
      api_key: encrypted:${GROK_API_KEY}
      
      # Safety settings (CANNOT BE DISABLED)
      safety_filter_enabled: true  # MANDATORY
      user_consent: false  # Set to true after consent dialog
      consent_timestamp: null
      
      # Monitoring
      auto_disable_on_safety_issues: true
      critical_flag_threshold: 5  # per week
      filter_rate_threshold: 0.20  # 20%
      
      # Logging
      log_all_requests: true
      log_filtered_content: true
      log_safety_stats: true
```

---

## Success Metrics

**Phase 11b Grok Integration Success Criteria:**
- [ ] Zero unsafe content displayed to users
- [ ] < 5% false positive rate (safe content incorrectly filtered)
- [ ] 100% of blacklisted tasks blocked
- [ ] User consent obtained before first use
- [ ] Safety dashboard functional
- [ ] Auto-disable triggers if threshold exceeded
- [ ] Comprehensive test coverage (>95%)

---

## Future Enhancements

**If Grok Improves:**
- Periodic re-evaluation of safety filters
- Gradual expansion of whitelist if justified
- User feedback mechanism for false positives

**If Safety Issues Persist:**
- Consider removing Grok integration entirely
- Stricter filtering patterns
- Reduce whitelist further

---

## Related Documents

- [PHASE11_MULTI_MODEL_ENHANCED_V2.md](./PHASE11_MULTI_MODEL_ENHANCED_V2.md) - Overall Phase 11 spec
- [PHASE11_PROVIDER_SPECIFICATIONS.md](./PHASE11_PROVIDER_SPECIFICATIONS.md) - Provider details
- [master_roadmap.md](./master_roadmap.md) - Project roadmap

---

## Approval Status

**Status:** ✅ Approved - Safety measures mandatory  
**Approved By:** User (Brett)  
**Date:** January 28, 2026  
**Note:** These safety measures are non-negotiable and cannot be disabled by users.

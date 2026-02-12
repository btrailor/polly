# Design: Fix Domain Auto-Tagging

## Approach

### 1. Wire DomainEngine into ProfessorPersona

Add an optional `domain_engine` parameter to `ProfessorPersona.__init__()`. This follows the same pattern as existing dependencies (`rag`, `skill_manager`, `learning_tracker`, etc.).

When instantiating the Professor in `interfaces/server.py`, pass `polly.domains` (the `DomainEngine` instance).

### 2. Replace hardcoded "glyphs" with dynamic detection

Add a helper method `_detect_domain_for_topic(topic: str) -> str` that calls `DomainEngine.detect_domains()` on the topic/goal text. Falls back to `"general"` if no engine is available or no domain scores above zero.

Replace all 5 hardcoded `domain="glyphs"` locations:
- Explain mode `record_learning()` (line ~235)
- Socratic mode `record_learning()` (line ~320)
- Curriculum mode RAG search filter (line ~384)
- Curriculum mode save-as-note action (line ~423)
- Learning note offer action (line ~964)

### 3. Improve keyword matching precision

Change `Domain.matches_content()` in `core/domains.py` to use word-boundary regex matching for short keywords (<=3 chars). This prevents false positives like "ui" matching inside "build" or "fruit."

Longer keywords (>3 chars) continue to use substring matching, which is appropriate for phrases and longer terms.

## Key Types/APIs

- `DomainEngine.detect_domains(query, context) -> List[str]` -- existing API, returns domain IDs sorted by relevance
- `ProfessorPersona._detect_domain_for_topic(topic) -> str` -- new helper, returns best domain ID

## Impact on Existing Code

- `ProfessorPersona.__init__()` gains one new optional kwarg (`domain_engine`)
- All existing call sites that don't pass `domain_engine` continue to work (falls back to `"general"`)
- `Domain.matches_content()` becomes slightly more precise for short keywords; no behavioral change for keywords >3 chars
- No API contract changes; no frontend changes needed

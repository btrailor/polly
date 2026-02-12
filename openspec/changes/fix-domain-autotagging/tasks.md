# Tasks: Fix Domain Auto-Tagging

## Implementation Order

1. [x] Add `domain_engine` parameter to `ProfessorPersona.__init__()` in `core/personas/implementations/professor.py`
2. [x] Add `_detect_domain_for_topic()` helper method to `ProfessorPersona`
3. [x] Replace hardcoded `domain="glyphs"` at line ~235 (explain mode record_learning)
4. [x] Replace hardcoded `domain="glyphs"` at line ~320 (socratic mode record_learning)
5. [x] Replace hardcoded `domain="glyphs"` at line ~384 (curriculum RAG search filter)
6. [x] Replace hardcoded `domain="glyphs"` at line ~423 (curriculum save-as-note action)
7. [x] Replace hardcoded `domain="glyphs"` at line ~964 (learning note offer action)
8. [x] Pass `polly.domains` to ProfessorPersona in `interfaces/server.py` (2 instantiation sites)
9. [x] Improve `Domain.matches_content()` in `core/domains.py` to use word-boundary matching for short keywords
10. [x] Update `docs/planning/KNOWN_ISSUES.md` to mark issue #4 as resolved

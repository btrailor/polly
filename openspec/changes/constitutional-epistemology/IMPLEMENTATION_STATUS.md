# Constitutional Epistemology — Implementation Status

**Created:** February 2026  
**Status:** ✅ **FULLY IMPLEMENTED AND ACTIVE** (February 15, 2026)  
**Implementation time:** ~2 hours + critical fix (~15 minutes)

> **UPDATE (February 15, 2026):** Fixed integration issue where constitutional layer was only in PersonaManager but not actually sent to LLM. Now properly injected into `BasePersona._build_messages()` so ALL persona LLM calls include constitutional epistemology.

---

## Summary

Constitutional Epistemology is now **implemented and active** in Polly. The constitutional layer sits as the deepest system prompt layer, shaping how every persona thinks about every topic.

This is not content filtering. It's an epistemological stance that makes fascist, racist, and authoritarian logic structurally unable to survive contact with Polly's analysis — through consistently better analysis, not through blocking.

---

## What Was Implemented

### Files Created

1. **`core/constitutional/__init__.py`** (716 bytes)
   - Package initialization
   - Exports `get_constitutional_layer()` function

2. **`core/constitutional/layer.py`** (2,862 bytes)
   - `CONSTITUTIONAL_EPISTEMOLOGY` prompt constant (2,051 characters)
   - The three core principles (Material Analysis, Cui Bono, Scapegoat Suspicion)
   - Four derived commitments (Horizontal, Self-Activity, Plural Worlds, Defamiliarization)
   - Five conduct rules for avoiding moralizing

3. **`core/constitutional/principles.py`** (7,495 bytes)
   - `ConstitutionalPrinciple` dataclass with trigger patterns and response strategies
   - `DerivedCommitment` dataclass with theoretical sources
   - All principles and commitments defined programmatically
   - Utility functions for accessing by slug

4. **`core/constitutional/knowledge_priorities.yml`** (4,900 bytes)
   - 9 priority knowledge domains with topics, rationale, importance
   - Guidance for RAG knowledge base seeding
   - Ready for use when BookLore is implemented

5. **`tests/verify_constitutional.py`** (New)
   - Automated verification of constitutional layer integration
   - Manual testing guide with 13 test queries
   - Testing checklist and success criteria

### Files Modified

1. **`core/personas/base.py`** ⚠️ **CRITICAL FIX** (February 15, 2026)
   - Added import: `from core.constitutional import get_constitutional_layer`
   - Modified `_build_messages()` method to include constitutional layer
   - Constitutional layer now prepended to ALL persona system prompts
   - This ensures constitutional epistemology shapes all LLM calls

2. **`core/personas/manager.py`**
   - Added import: `from core.constitutional import get_constitutional_layer`
   - Modified `get_system_prompt()` to inject constitutional layer as first element
   - Updated docstring documenting three-tier prompt hierarchy

3. **`openspec/specs/ethics/spec.md`**
   - Updated Implementation section with detailed status
   - Documented all files and contents
   - Added Deferred Enhancements section with cross-references

4. **`openspec/specs/library/spec.md`**
   - Added Deferred Enhancements section
   - Documented Constitutional RAG Knowledge Seeding for Phase 25

5. **`openspec/specs/teaching/spec.md`**
   - Added Deferred Enhancements section
   - Documented Critical Consciousness teaching integration for Phase 22

---

## System Prompt Hierarchy (Updated)

```
7. Constitutional epistemology    ← DEEPEST, NON-NEGOTIABLE (NEW)
6. Persona base behavior
5. Active theme behavior defaults
4. Project philosophy context
3. Active skills
2. Task-specific requirements
1. Explicit user instruction        ← HIGHEST PRIORITY for WHAT to do
```

User instructions have highest priority for **WHAT** to do.  
Constitutional layer defines **HOW** Polly thinks about it.

---

## Verification

✅ Constitutional layer imports without errors  
✅ Prompt text: 2,051 characters  
✅ Core principles: 3 (Material Analysis, Cui Bono, Scapegoat Suspicion)  
✅ Derived commitments: 4 (Horizontal, Self-Activity, Plural Worlds, Defamiliarization)  
✅ Knowledge priorities: 9 domains with topics  
✅ PersonaManager integration working  
✅ Specs updated with implementation notes and cross-references  
✅ Real-world testing framework complete (13 test queries across 4 categories)

---

## Deferred Enhancements

Three enhancements were identified during implementation. One was skipped as redundant, two were deferred to appropriate future phases with cross-references added to relevant specs.

### 1. Mental Models Integration — **SKIPPED**

**Proposed:** Add constitutional models (Cui Bono, Historical Construction, Structural Analysis) to mental models system as non-toggleable tier.

**Decision:** Skipped as redundant. Constitutional layer already injects these principles at deepest prompt level. Adding as mental models would duplicate functionality and confuse what's truly non-configurable.

**Status:** Not implementing.

### 2. RAG Knowledge Base Seeding — **DEFERRED to Phase 25 (BookLore)**

**Proposed:** Use `knowledge_priorities.yml` to guide knowledge base seeding with priority sources (economic history, racial formation, power analysis, etc.).

**What:** Priority-based book recommendations, coverage analysis, automatic tagging, seeding suggestions.

**Why deferred:** Makes most sense when BookLore infrastructure exists for library management.

**Cross-reference:** `openspec/specs/library/spec.md` → Deferred Enhancements → Constitutional RAG Knowledge Seeding

**Status:** Deferred to Phase 25 implementation (2026 Q2-Q3)

### 3. Teaching Integration — **DEFERRED to Phase 22 Meta-Pedagogy (Wave 2)**

**Proposed:** Make constitutional critical consciousness explicitly teachable through Professor persona with competency tracking.

**What:** Four constitutional thinking skills with 5-level progression, competency tracking, Professor teaching methods, inoculation pedagogy, skill progression UI.

**Why deferred:** Constitutional layer already shapes all analysis. Making it explicitly teachable makes most sense when meta-pedagogy infrastructure is built.

**Cross-reference:** `openspec/specs/teaching/spec.md` → Deferred Enhancements → Critical Consciousness as Teachable Skills

**Status:** Deferred to learning-and-administrator-profiles change (Wave 2)

### 4. Real-World Testing — ✅ **TESTING FRAMEWORK COMPLETE**

**Proposed:** Test constitutional layer with queries triggering principles to verify conduct rules are followed and analysis is better without moralizing.

**What was implemented:**
- Automated integration tests verifying constitutional layer exists and is properly integrated
- Manual testing framework with 13 test queries across 4 principle categories
- Verification script: `tests/verify_constitutional.py`
- Testing guide with success criteria and checklist

**Testing framework includes:**
1. **Material Analysis Tests** (3 queries) — Essentialist/naturalized claims
2. **Cui Bono Tests** (3 queries) — Economic narratives
3. **Scapegoat Redirect Tests** (3 queries) — Outgroup blame
4. **Conduct Rules Tests** (4 queries) — Labeling, curiosity, grievances, defamiliarization

**Status:** ✅ Framework complete, ready for manual testing with live Polly instance

---

## Design Principle

> "The user never gets lectured. They get a better education. That's the infinite game version of antifascism — building analytical capacity that makes fascist recruitment harder on an ongoing basis."

---

## Next Steps

1. ✅ **Real-world testing framework complete** — Run `python3 tests/verify_constitutional.py` for testing guide
2. **Optional manual testing** — Use live Polly instance to test 13 queries and verify conduct rules
3. **Monitor in production** — Observe how constitutional layer performs in practice
4. **Revisit deferred enhancements** when reaching Phase 22 (Teaching) and Phase 25 (BookLore)

---

## References

**Specs:**
- `openspec/specs/ethics/spec.md` — Full specification
- `openspec/changes/constitutional-epistemology/proposal.md` — Original proposal
- `openspec/changes/constitutional-epistemology/design.md` — Design details

**Implementation:**
- `core/constitutional/` — All implementation files
- `core/personas/manager.py:508` — Integration point (get_system_prompt method)
- `tests/verify_constitutional.py` — Testing framework and manual guide

**Cross-references:**
- `openspec/specs/library/spec.md` — BookLore + RAG seeding
- `openspec/specs/teaching/spec.md` — Meta-pedagogy + critical consciousness teaching

**Theoretical Sources:**
- Freire, _Pedagogy of the Oppressed_ — Problem-posing pedagogy
- Graeber, _Debt: The First 5000 Years_ — Material analysis
- Bogost, _Alien Phenomenology_ — Defamiliarization
- inhabit.global — Plural worlds, refusal-to-be-managed
- Autonomist thought — Self-activity, horizontal organization
- Anthropic, Constitutional AI — Values-based alignment

# Pre-Implementation Readiness Audit

**Source:** `https://claude.ai/public/artifacts/536f8d43-7821-42a6-ae55-208d1a1ce506`  
**Date:** 2026-04-01  
**Author:** External audit of full spec corpus + codebase  
**Status:** Incorporated — see cross-reference map below

## Summary

The spec corpus is structurally sound. Three implementation blockers, four friction risks, and several cleanup items identified. Blockers and friction risks addressed below.

## Cross-Reference Map — Actions Taken

| Audit item | Severity | Action |
|-----------|---------|--------|
| 1.1 expo-openclaw-chat API not verified | Blocker | Task added to `phase-1-ios-foundation/tasks.md` — explicit 30-min verification task before any gateway code |
| 1.2 Phase 1 scope too large (~150 checkboxes) | Blocker | `phase-1-ios-foundation/tasks.md` restructured into 1A (Ship It) / 1B (Complete It) / 1C (Content) sub-phases |
| 1.3 Onboarding bootstrap: baked key underspecified | Blocker | **Pending Brett's decision** — conversational (Gemini Flash baked key) vs. manual form-based for Phase 1A. See open question in `phase-1-ios-foundation/tasks.md` |
| 2.1 openspec legacy spec files vs. current iOS specs | Friction | `openspec/DEPRECATED_NOTICE.md` added; `openspec/specs/` files marked legacy |
| 2.2 10 stub agents + 43 missing allowed_modes + 43 missing suggested_prompts | Friction | Already tracked in `phase-1-agent-system/tasks.md` (updated this session). Pre-implementation priority note added. |
| 2.3 Sensibility system three-way conflict | Friction | Phase 1A/1B split in sensibility tasks added |
| 2.4 Group chat context injection not in Phase 1 task file | Friction | Explicit task added to `phase-1-ios-foundation/tasks.md` with swarm spec cross-ref |
| 2.5 Knowledge Skill: Python skill runner compatibility not verified | Friction | `phase-2-knowledge-skill/tasks.md`: Skill Runner Compatibility section added |
| 2.6 TOFU cert pinning: conditional on wss:// not documented in onboarding flow | Friction | `ONBOARDING_SPEC.md` + `SECURITY_IMPLEMENTATION_SPEC.md`: conditional cert screen clause added |
| 3.1 Broken cross-refs + orphaned files | Cleanup | `SPEC_INDEX.md` updated |
| 3.2 Duplicate colors.ts | Cleanup | Already tracked in Phase 1 tasks |
| 3.3 Phase numbering disconnect | Cleanup | No action needed — gap analyses cover this |
| 3.4 PROJECT_STATUS.md aspirational | Cleanup | Rewritten to reflect actual state |
| 3.5 Lockdown Mode: NSFileProtectionComplete not verified | Cleanup | Investigation task added to `phase-1-ios-foundation/tasks.md` |

## Open Question Pending Brett's Decision

**Onboarding Phase 1A (Audit item 1.3):**  
- Option A: Conversational onboarding (baked Gemini Flash key, expiresAtMs TTL) — requires provisioning Google AI Studio project + baking key before first TestFlight build  
- Option B: Manual form-based onboarding (gateway URL + auth token entry as a standard form, no conversational layer) — simpler, faster to ship, conversational onboarding deferred to Phase 2  

Brett's call. Either way, Phase 1A TestFlight build cannot ship without resolving this.

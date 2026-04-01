# GESTURE_LAYER.md

Phase 2–3 — Vocal Gesture System  
Status: 📋 Planned  
Owners: @code_architect (data model + recognition), @backend (gateway integration), @frontend (UI + voice pipeline), @design_eng (gesture library UI, Builder agent SOUL)  
Last updated: 2026-03-30  
Source URL: https://claude.ai/public/artifacts/868eb12f-0cbd-4258-956b-f4f3877066cc

**All spec actions incorporated into openspec — see cross-reference map below.**

## Summary

The Gesture Layer converts short vocal utterances into pre-configured, personally meaningful behaviors — fuzzy-matched, personally defined, agent-participated. Three gesture types: Mode (configure before playing), Invocation (summon behavior mid-conversation), Transition (shift register without stopping). The recognition pipeline runs at the gateway as a pre-routing pass (length gate → embedding similarity → threshold check). Gestures have a per-user library at the gateway; agents get plain-language `## Gesture Vocabulary` sections injected into their SOUL context.

Also covers: Audible Voice Mode (voice-in, voice-out; solo only; TTS formatting pass), Apple Platform Integration (TellPollyIntent, OpenListeningIntent, Action Button), Gesture Builder system agent.

## Cross-Reference Map

| Section | Incorporated into |
|---------|-----------------|
| §1–3 Core concepts, gesture types, data model | `phase-2-gesture-layer/tasks.md` |
| §4 Recognition pipeline (length gate, embedding, thresholds) | `phase-2-gesture-layer/tasks.md` |
| §4.3 Prosodic amplifiers | `phase-2-gesture-layer/tasks.md` |
| §4.4 Invocation log | `phase-2-gesture-layer/tasks.md` |
| §5 Gesture Screen iOS layout | `phase-2-gesture-layer/tasks.md` |
| §6 Gesture Builder agent (SOUL, suggestion engine) | `phase-2-gesture-layer/tasks.md` |
| §7 Built-in gesture library (Mode/Invocation/Transition/System/Per-agent presets) | `phase-2-gesture-layer/tasks.md` (seeded at gateway init) |
| §8 Dynamic vocabulary injection into agent SOUL | `phase-2-gesture-layer/tasks.md` |
| §9 Audible Voice Mode (tts_mode, tts_text, register profiles) | `phase-2-gesture-layer/tasks.md` |
| §10.1 Relationship to shortcuts system | `phase-2-gesture-layer/tasks.md` |
| §10.2 TellPollyIntent | `phase-2-gesture-layer/tasks.md` + `phase-3d-shortcuts/tasks.md` |
| §10.3 OpenListeningIntent + Action Button | `phase-2-gesture-layer/tasks.md` + `phase-3d-shortcuts/tasks.md` |
| Phase 1 prosodics (composition with somatic signals) | `phase-1-gesture-layer/tasks.md` |
| §12 Open questions | `phase-2-gesture-layer/tasks.md` Q1–Q5 |

## Open Questions Pending Brett's Decision

Q3: Gesture chaining — data model supports it via `tool_invocations: []`; surface in Phase 2 Builder UI or defer?  
Q5: Gesture sharing — Phase 3+ community feature; data model must not preclude it.

# SPEC_INTEGRATION_BRIEFING.md

Session briefing — Gesture Layer, Ward & Agent Builder  
Source: Design session 2026-03-30  
**All spec actions incorporated into openspec — see cross-reference map below.**

## Three New Specs

- `GESTURE_LAYER.md` — Somatic/prosodic interface. Phase 1 (gateway schema + Phase 1 extraction) + Phase 2 (full signal extraction via native module).
- `AGENT_BUILDER.md` — Custom agent creation system. Phase 2–3.
- `WARD.md` — Universal entry point + Liaison coordinator extension. Phase 2.

## Architecture Summary

### Gesture / Somatic Interface
Voice input carries prosodic metadata beyond words: pace, pause, volume variance, turn length. The somatic interface extracts these signals client-side and passes them as `prosodics` on every voice message. Agents calibrate response depth, structure, and pace without labeling the state to Brett.

Three engagement states: `flowing` (in flow, match pace), `processing` (thinking hard, give space), `struggling` (stuck, simplify + structure).
Phase 1: `speechRate` + `turnLengthWords` from transcript metadata.
Phase 2: full extraction via `PollyAudioAnalyzer` native module (PCM frame analysis).

### Agent Builder
A guided conversational UI (not a form) for creating custom agents on iOS. Five screens: Name & Emoji → Personality (Quick Craft or Advanced SOUL editor) → Capabilities → Preview (with test session) → Done. Custom agents are structurally identical to built-in agents — same manifest schema, same SOUL Baseline injection, same routing.

### Ward
Ward is the invisible coordinator — the universal entry point when Brett presses mic outside an active conversation. Implemented as a system prompt / SOUL mode on the gateway (`coordinator_mode` flag on session model), not a separate service. Ward operates in two modes: Solo (orientation, routing, ambient gestures) and Group/Liaison (cross-team coordination). Mode is detected from invocation context — Brett never selects it.

Ward's cardinal rule: silence is the success state. If it's routing correctly and Brett doesn't notice it, Ward has done its job.

## Cross-Reference Map

| Spec | Incorporated into |
|------|------------------|
| GESTURE_LAYER.md — signal taxonomy, gateway schema | `phase-1-gesture-layer/tasks.md` |
| GESTURE_LAYER.md — iOS extraction (Phase 1) | `phase-1-gesture-layer/tasks.md` |
| GESTURE_LAYER.md — waveform orb UI states | `phase-1-gesture-layer/tasks.md` |
| GESTURE_LAYER.md — SOUL Baseline prosodic block | `phase-1-agent-system/tasks.md` |
| GESTURE_LAYER.md — Phase 2 full extraction | `phase-1-ios-foundation/tasks.md` (PollyAudioAnalyzer native module) |
| AGENT_BUILDER.md — five-screen flow, SOUL editor, capabilities | `phase-2-agent-builder/tasks.md` |
| AGENT_BUILDER.md — SOUL template spec + validation | `phase-2-agent-builder/tasks.md` |
| AGENT_BUILDER.md — manifest write, Quick Craft generation | `phase-2-agent-builder/tasks.md` |
| WARD.md — coordinator as system prompt | `phase-2-swarm-coordination/tasks.md` |
| WARD.md — full SOUL template | `phase-2-swarm-coordination/tasks.md` |
| WARD.md — Ward workspace + gateway registration | `phase-2-swarm-coordination/tasks.md` |
| WARD.md — `coordinator_mode` session flag | `phase-2-swarm-coordination/tasks.md` |
| Ward SOUL design principles (doc 4) | `openspec/specs/agent-system/spec.md` |

## Open Questions Pending Brett's Decision (do not resolve unilaterally)

1. **Ward conversation persistence:** Do Ward ambient interactions create conversation threads? Spec recommends no — validate against gateway session model.
2. **Gesture chaining:** Does Brett want gestures that trigger sequences of behaviors?
3. **Agent/gesture sharing:** Does Brett want the data model to support sharing agents/gestures between Polly users now, or defer?

# Phase 2: Gesture Layer — Vocal Gesture System

**Status:** 📋 Planned  
**Gate:** Phase 1 voice pipeline live (Whisper STT, WebSocket send); Phase 1 gesture-layer (prosodics) complete  
**Spec source:** `GESTURE_LAYER.md` — full document  
**Owners:** @backend (recognizer, library, ownership resolution, TTS formatting, Builder suggestion engine), @frontend (Gesture screen, Builder chat entry, TTS toggle + playback, disambiguation card), @code_architect (gesture data model, agent manifest integration, Liaison routing protocol, AppIntents), @design_eng (gesture screen design, Builder SOUL refinement, per-agent register profiles, ## Gesture Vocabulary template), @qa_guy (recognition accuracy suite, disambiguation trigger tests)

---

## What This Is

The Gesture Layer converts short vocal utterances into pre-configured, personally meaningful behaviors — without exact phrasing, without menus, without interrupting conversational flow.

**A gesture is not a voice command.** Commands require exact phrasing and map to fixed system actions. Gestures are fuzzy-matched, personally defined, and map to agent behaviors that agents participate in. The distinction: a command is a button; a gesture is a practiced move on an instrument that has learned how you play.

The monome grid analogy is architecturally precise. Each agent is a voice. Voices respond to gestures in their region of the gesture space. Brett develops fluency through practice, not memorization.

---

## Gesture Data Model (@code_architect)

```typescript
interface Gesture {
  id: string;                          // UUID, opaque
  name: string;                        // display name
  type: 'mode' | 'invocation' | 'transition' | 'system';
  trigger_phrases: string[];           // semantic seeds (not exact strings)
  behavior: GestureBehavior;
  scope: 'any' | string | 'solo_only' | 'group_only';  // string = domain name
  owner: string;                       // agent ID (default owner)
  domain_overrides?: Record<string, string>;  // domain → agentId
  group_overrides?: Record<string, string>;   // groupId → agentId
  sensitivity?: 1 | 2 | 3 | 4 | 5;    // threshold tuning (default 3)
  prosodic_amplifier?: ProsodicAmplifier;
  source: 'built-in' | 'user';        // built-ins shadowable but not deletable
  usage_stats: {
    invocation_count: number;
    last_used: string | null;
    last_owner_at_use: string | null;
  };
  embedding?: number[];               // computed at creation, updated on phrase add
}

interface GestureBehavior {
  agent?: string;
  mode?: string;
  retrieval_policy?: 'none' | 'normal' | 'broad';
  response_register?: 'concise' | 'normal' | 'thorough';
  tool_invocations?: string[];       // e.g. ["vault_write", "knowledge_search"]
}

interface ProsodicAmplifier {
  condition: 'slow_deliberate' | 'flowing' | 'struggling';
  modifier: string;
}
```

- [ ] `@code_architect`: Define Gesture + GestureBehavior + ProsodicAmplifier schemas (above)
- [ ] `@code_architect`: Integrate gesture_vocabulary into agent manifest schema (alongside `allowed_modes`, `autonomy_level`)
- [ ] `@code_architect`: Liaison gesture routing protocol — group chat ownership resolution algorithm (domain overrides → group overrides → default owner → disambiguation card)

---

## Gateway — Gesture Library (@backend)

- [ ] Gesture library: per-user JSON store at gateway
- [ ] Built-in gesture library seeded at gateway init (all entries from `GESTURE_LAYER.md §7`)
- [ ] CRUD API: create, read, update, delete gesture entries
- [ ] Embedding computation on gesture creation / phrase addition (model: see Q2)
- [ ] Usage stats updated on every invocation
- [ ] Gateway config key: `polly.gestures[]`

---

## Gateway — Recognition Pipeline (@backend)

Runs as pre-routing pass on every incoming message.

```
Incoming message text
 ↓
[1] Length gate: ≤ 8 words?
    NO → route normally (skip gesture)
    YES → continue
 ↓
[2] Embedding similarity pass
    Compare against all gesture embeddings
    Find top match + score
 ↓
[3] Threshold check:
    ≥ 0.82 → GESTURE MATCH → invoke behavior (skip normal routing)
    0.65–0.81 → CANDIDATE → inject confirmation card into response
    < 0.65 → NO MATCH → route normally
```

- [ ] Length gate: skip embedding call for messages > 8 words
- [ ] Embedding similarity pass against gesture library
- [ ] Threshold: 0.82 MATCH / 0.65–0.81 CANDIDATE / < 0.65 pass-through
- [ ] Per-gesture sensitivity slider maps to threshold adjustment (1=+0.10, 5=-0.10 from defaults)
- [ ] Ownership resolution: check group overrides → domain overrides → default owner
- [ ] Disambiguation card event when two agents claim same gesture in same scope
- [ ] Prosodic amplifier evaluation (if gesture has one and prosodics are non-null)
- [ ] **Phase 1 hook (ship before full recognizer):** Gateway logs all short utterances (≤ 8 words) that don't match routing patterns — seeds Builder suggestion engine from day one

---

## Gateway — Gesture Invocation Log (@backend)

```json
{
  "timestamp": "...",
  "gesture_id": "...",
  "trigger_text": "...",
  "similarity_score": 0.89,
  "resolved_owner": "contrarian",
  "domain_context": "sigils",
  "group_context": null,
  "session_id": "..."
}
```

- [ ] Log every gesture invocation with above schema
- [ ] Log short-utterance misses (Phase 1 hook above) with `gesture_id: null`
- [ ] Expose log as data source for: usage stats, Builder suggestion engine, Metacognitive Dashboard (Phase 3), Janitor retirement suggestions (Phase 3)

---

## Gateway — Dynamic Gesture Vocabulary Injection (@backend)

When an agent session starts, gateway injects a `## Gesture Vocabulary` section into the agent's SOUL context — plain language, not raw JSON.

- [ ] Translate agent's claimed gestures (from library) into markdown vocabulary section
- [ ] Format: gesture name in bold, trigger phrases, ownership scope (see template in GESTURE_LAYER.md §8.1)
- [ ] When Brett creates a new gesture and assigns it to an agent: update agent's vocabulary section in gateway; agent sees it on next session start
- [ ] Agents never see raw library JSON — gateway handles translation

---

## Gateway — Audible Voice Mode (@backend)

- [ ] `tts_mode` flag on WebSocket handshake (client sets)
- [ ] When `tts_mode: true`: response object includes `tts_text` (TTS-optimized) alongside `display_text`
- [ ] `tts_text` formatting pass: strip `**bold**`, `#headers`, `- list items`; convert to flowing prose equivalents
- [ ] Formatting pass is a rule-based transformation — NOT a second LLM call
- [ ] Per-agent register profiles inform formatting: sentence length targets, punctuation for natural pause, list handling (see register profiles table below)

**Per-agent register profiles (@design_eng to define, @backend to implement):**

| Agent | Register profile |
|-------|----------------|
| Mentor | Slower pacing, longer pauses between thoughts, warm |
| Contrarian | Shorter sentences, no preamble, direct |
| Code Architect | Precise, structured, comfortable with technical terms |
| Philosopher | Longer sentences, rhetorical questions left hanging |
| Strategist | Deliberate, each point given space |

Phase 2: single TTS voice (system default or user-selected). Register profiles shape formatting only.  
Phase 3: multiple voice options; per-agent voice assignment.

---

## iOS — Gesture Screen (@frontend)

- [ ] First-class navigation destination (not a settings submenu)
- [ ] Type filter tabs: [Mode] [Invocation] [Transition] [System]
- [ ] Gesture list: each entry shows trigger phrase (top) + behavior summary (bottom)
- [ ] Domain override label shown inline when present
- [ ] Tap to expand: all trigger phrases, full behavior spec, scope, owner, usage stats; edit/delete in expanded state
- [ ] Built-in gesture indicator (subtle dot — not a lock); built-ins shadowable, behavior not deletable
- [ ] Prominent `+` button in nav title
- [ ] Secondary "+ New gesture" affordance mid-list

---

## iOS — Gesture Builder (@frontend)

- [ ] `+` → opens Gesture Builder as a full chat screen (not a modal form)
- [ ] Builder agent in gesture-creation mode (see Builder SOUL in `GESTURE_LAYER.md §6.3`)
- [ ] After confirming new gesture: save to library → Builder says "Done — [name] is live. Try it in any conversation." → user navigates back or continues
- [ ] No context switch to a form and back — entirely conversational

---

## iOS — Audible Voice Mode (@frontend)

- [ ] TTS toggle in chat header (solo conversations only — hidden in group chats)
- [ ] TTS playback via `AVSpeechSynthesizer` (Phase 2) or equivalent
- [ ] Display `display_text` as normal; speak `tts_text` aloud
- [ ] Toggle off mid-conversation: stop TTS, return to text-only
- [ ] Voice mode is per-conversation state, not a global setting

---

## iOS — Disambiguation Card (@frontend)

- [ ] One-tap card when two agents claim the same gesture in the same scope
- [ ] Shows both agents with their gesture descriptions
- [ ] One tap routes to selected agent
- [ ] No silent wrong routing — disambiguation is always preferable

---

## Agent SOUL — Gesture Vocabulary Section (@design_eng)

- [ ] Write `## Gesture Vocabulary` section template (see format in `GESTURE_LAYER.md §8.1`)
- [ ] Add `## Gesture Vocabulary` section to all 43 agent SOULs in `POLLY_AGENT_TEMPLATES.md` (Phase 2 task — list each agent's owned gestures from `GESTURE_LAYER.md §7`)
- [ ] Agents with `autonomy_level: proactive` may suggest new gestures inline (see §8.3); reactive agents may not

---

## Builder Agent — System Agent Registration (@backend)

- [ ] Register Gesture Builder as a system agent (not in 43-agent roster, not user-visible in drawer)
- [ ] Built-in trigger phrases: "add a gesture", "new gesture", "help me build something"
- [ ] Builder has access to: full gesture library, every agent's gesture vocabulary, domain taxonomy, recognition thresholds, prosodic signal types
- [ ] Builder does NOT have conversation history from other agents — clean context per session
- [ ] Phase 3 — Suggestion Engine: monitor invocation log for ungestured patterns (≥ 4 uses of same short phrase across sessions, no existing gesture match, consistent agent response pattern) → surface Builder suggestion card in Today View

---

## Apple Platform Integration (@code_architect + @frontend)

### TellPollyIntent (new AppIntent — add to phase-3d-shortcuts)

```swift
struct TellPollyIntent: AppIntent {
  static var title: LocalizedStringResource = "Tell Polly"
  @Parameter(title: "Phrase") var phrase: String

  func perform() async throws -> some IntentResult {
    // Deep link: polly://gesture?phrase=...
    // App foregrounds → gesture recognizer processes phrase
    // No match → phrase becomes pre-filled chat input (never fails silently)
  }
}
```

- [ ] Implement `TellPollyIntent` in AppIntents native Swift module (alongside per-shortcut intents)
- [ ] Register alongside existing App Intents infrastructure
- [ ] No-match fallback: phrase becomes pre-filled chat input
- [ ] Siri phrase: "Hey Siri, tell Polly [phrase]" → every gesture in Brett's library auto-available via Siri with zero extra registration

### OpenListeningIntent (new AppIntent — add to phase-3d-shortcuts)

```swift
struct OpenListeningIntent: AppIntent {
  static var title: LocalizedStringResource = "Open Polly Listening"

  func perform() async throws -> some IntentResult {
    // Deep link: polly://listen
    // App opens to active chat, mic starts recording immediately
    // Lockdown Mode exception: normal open (no auto-mic)
  }
}
```

- [ ] Implement `OpenListeningIntent`; deep link `polly://listen`
- [ ] iOS voice pipeline: mic starts on deep link arrival without additional tap
- [ ] Lockdown Mode exception: normal open behavior (no auto-mic) — document in `LOCKDOWN_MODE.md`
- [ ] Onboarding suggestion: "Set your Action Button to open Polly instantly — tap here for setup instructions"

### Action Button
- [ ] Surface Action Button setup instructions in onboarding (after voice pipeline working): Action Button → Shortcuts → "Open Polly Listening"
- [ ] Interaction: press → mic live → speak gesture → Polly responds — 2 physical actions from any state

### Lock Screen Widget (Phase 3 enhancement — defer)
- [ ] Phase 3: narrow lock screen widget, single mic button, tap → `OpenListeningIntent`

---

## Built-In Gesture Library (reference — gateway seeds these)

Full library in `GESTURE_LAYER.md §7`. Summary by type:

| Type | Count | Examples |
|------|-------|---------|
| Mode | 5 | Capture mode, Morning reflection, Deep work, Quick mode, Switch to [domain] |
| Invocation | 7 | Save this, Push back, Check the vault, Synthesize, New note, Archive conversation, Dream search |
| Transition | 5 | Zoom out, Make it concrete, What do I do, Honest take, Explore this |
| System/Maintenance | 6 | Re-index vault, Check for broken links, Clean up duplicates, System status, Start fresh, How am I doing |
| Per-agent presets | ~35 | See `GESTURE_LAYER.md §7.5` — all 7 agent categories with specific gestures |

---

## Open Questions

Q1: **Threshold calibration** — 0.82 / 0.65 defaults need dogfooding. @qa_guy flags false positives and false negatives in first 2 weeks post-launch; @backend adjusts.

Q2: **Embedding model** — What model generates gesture embeddings at gateway? Must be fast + locally hosted (runs on every short message). Candidate: `nomic-embed-text:latest` via Ollama. @backend confirms sufficiency for short-phrase semantic similarity.

Q3: **Gesture chaining** — Can a gesture trigger a sequence of behaviors? Data model supports it via `tool_invocations: []` — no additional architecture needed. Needs Builder UI support + QA. Brett's decision on whether to surface this in Phase 2 Builder or defer.

Q4: **Cross-instance portability** — Phase 2: no sync (library lives at one gateway). Phase 3 Federated Collaboration: library is part of cognitive artifact export. Design deferred.

Q5: **Gesture sharing** — Phase 3+ community feature. Data model must not preclude it: avoid user-specific fields in gesture definitions that would prevent portability.

---

## Dependencies

- Phase 1 voice pipeline (Whisper STT, WebSocket send) — recognizer needs transcribed text
- Phase 1 gesture-layer (prosodics) — prosodic amplifiers available
- `SOMATIC_INTERFACE.md` prosodic extraction (Phase 2 full extraction)
- `AGENT_BEHAVIOR_CONTRACT.md` tool surface (vault_write, knowledge_search) — for gesture behaviors
- `SWARM_COORDINATION_SPEC.md` group chat + Liaison — gesture ownership in groups
- `POLLY_AGENT_TEMPLATES.md` — `## Gesture Vocabulary` section needed for all 43 agents
- `phase-3d-shortcuts` — AppIntents native Swift module shared; TellPollyIntent + OpenListeningIntent added there
- `LOCKDOWN_MODE.md` — gesture recognition disabled when lockdown: true; document Action Button exception
- `phase-2-agent-builder` — custom agents register gesture vocabulary through same pipeline; `source: "user-agent"` entries in ownership resolution

## Done When

Gesture library seeded. Recognition pipeline running (length gate + embedding + threshold). Ownership resolution working. Disambiguation card live. Gesture screen with Builder chat entry. Audible Voice Mode toggle + TTS playback. TellPollyIntent + OpenListeningIntent registered. All 43 agent SOULs have `## Gesture Vocabulary` sections. @security_audit sign-off on no cloud calls in recognition pipeline.

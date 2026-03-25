# SOMATIC_INTERFACE.md
*Phase 2 — Prosodic Engagement Signals*
*Status: Planned — all design decisions locked*
*Owners: @frontend (extraction), @design_eng (register modulation spec), @backend (WebSocket schema)*
*Last updated: 2026-03-25*

---

## 1. What This Is

Prosodic engagement signals extracted client-side from the iOS audio buffer, transmitted alongside the voice transcript, and used by agents to modulate response register.

This is **not** emotion AI. Emotion inference from voice is unreliable, invasive, and requires training data that creates privacy risks. This is engagement measurement — four signals that describe *how* Brett is speaking without inferring *what he feels*:

| Signal | What it measures | Derivation |
|--------|-----------------|------------|
| `speech_rate` | Words per minute | Word count from Whisper timestamps ÷ duration |
| `pause_p95_ms` | 95th-percentile pause duration in ms | Silence thresholding on audio buffer |
| `volume_variance` | Variance in audio amplitude across turn | RMS amplitude per 100ms window |
| `turn_length_words` | Total words in the turn | Word count from Whisper output |

All four are derivable from Whisper timestamp data and silence thresholding. No separate model required.

The Monome velocity sensitivity metaphor is architecturally precise: the instrument responds to *how* you play it, not just what notes you press. Prosodic signals are the velocity layer of voice input.

---

## 2. Why This Is Possible Here

Prosodic metadata is ethically viable in Polly because:

1. **Self-hosted** — data never leaves the device/gateway. No cloud provider receives prosodic signals.
2. **No raw audio transmitted** — only the four derived floats are sent to the gateway. The audio buffer stays on device.
3. **No voice print** — the four signals cannot be used to identify Brett's voice or reconstruct the audio.
4. **Transparent** — settings disclosure explains exactly what is extracted. Toggle is on by default but user-controlled.
5. **Lockdown mode disables entirely** — see §8.

The same feature would be indefensible in a cloud-connected product. Here it is defensible because ownership is literal.

---

## 3. Client-Side Extraction

### 3.1 Where It Happens

Extraction happens on the iOS client, in the voice recording pipeline, **before** the WebSocket send. The hook is in `useVoiceRecording` — REQ-VOICE-08 requires this hook to be added to the voice pipeline.

**REQ-VOICE-08:** The voice pipeline MUST extract prosodic metadata (`speech_rate`, `pause_p95_ms`, `volume_variance`, `turn_length_words`) from the audio buffer prior to gateway transmission.

### 3.2 Extraction Method

```
speech_rate       = (whisper_word_count / turn_duration_seconds) × 60
pause_p95_ms      = 95th percentile of silence gap durations (threshold: amplitude < 0.02 RMS for ≥ 150ms)
volume_variance   = variance of RMS amplitude computed per 100ms window across full turn
turn_length_words = whisper_word_count
```

Whisper already produces timestamps and word counts as part of its transcription output. The silence thresholding requires one pass over the audio buffer — negligible compute overhead on-device.

### 3.3 Payload Structure

The four floats are attached to the WebSocket message as an optional `prosodics` field:

```json
{
  "type": "user_message",
  "text": "I've been thinking about this problem for a while and...",
  "prosodics": {
    "speech_rate": 142.3,
    "pause_p95_ms": 820,
    "volume_variance": 0.041,
    "turn_length_words": 47
  }
}
```

**`prosodics` is a nullable field on ALL message objects** — not voice-gated. Text messages send `prosodics: null`. This is @backend's responsibility. The client does not branch on modality; the gateway handles null prosodics cleanly.

---

## 4. Gateway Processing

### 4.1 NL Summary Injection

The gateway translates prosodic floats into a natural language engagement summary before injecting into agent context. **Agents never see the raw floats.**

The summary is injected **ahead of** the user message in the agent's context window:

```
[prosodic context: Brett is speaking slowly with long pauses — possible uncertainty or careful deliberation. Turn is long (47 words). Response: give space, ask rather than tell.]

Brett: I've been thinking about this problem for a while and...
```

### 4.2 Absent Prosodics

If `prosodics` is null (text input, or user has disabled prosodic extraction):

**The gateway omits the block entirely.** It does NOT inject `[prosodics: null]` or any equivalent. Absence is the signal — agents treat a missing prosodic block as text-mode context and respond without register modulation. No annotation of the absence.

### 4.3 Engagement State Mapping

Reference mapping for the NL summary generator (not exhaustive — tunable):

| Signal pattern | Engagement state | Register guidance |
|---------------|-----------------|-------------------|
| High speech_rate, low pause_p95, low volume_variance | Confident/flowing — ideas are clear | Concise, direct, match energy |
| Low speech_rate, high pause_p95 | Uncertain/deliberating — working something out | Ask questions, give space, don't rush to conclusion |
| High volume_variance | Emotionally activated — something has weight | Acknowledge before proceeding; Mentor may name what's happening |
| Short turn_length | Clipped/minimal | Don't over-respond; brief reply invites continuation |
| Very long turn_length | Thinking out loud — lots to process | Structured response helps; break complex replies into parts |

---

## 5. Agent-Side: Prosodic Sensitivity

### 5.1 Per-SOUL Configuration

Each agent SOUL includes a `## Prosodic Sensitivity` section defining how that agent responds to engagement states. This is agent-specific — the Mentor responds differently to uncertainty than the Contrarian.

**Template:**
```markdown
## Prosodic Sensitivity

When the gateway injects a prosodic context block:
- **Confident/flowing:** [agent-specific behavior]
- **Uncertain/deliberating:** [agent-specific behavior]
- **Emotionally activated:** [agent-specific behavior]
- **Clipped/minimal:** [agent-specific behavior]
```

### 5.2 Example: The Mentor

```markdown
## Prosodic Sensitivity

- **Confident/flowing:** Match the pace. No preamble. Get to the substance.
- **Uncertain/deliberating:** Don't fill the space. Ask one question. Give room.
- **Emotionally activated:** Name what you notice before proceeding: "That sounds like it has some weight behind it." Then ask.
- **Clipped/minimal:** Mirror it. Short response. One question maximum.
```

### 5.3 Example: The Contrarian

```markdown
## Prosodic Sensitivity

- **Confident/flowing:** Good. This is when assumptions are most worth challenging — confidence can mask unexamined premises.
- **Uncertain/deliberating:** Don't exploit the uncertainty. Challenge the *ideas*, not the hesitation.
- **Emotionally activated:** Reduce challenge pressure. This is not the moment to push. Note the activation; wait for the next exchange.
- **Clipped/minimal:** One focused challenge, not a barrage.
```

---

## 6. UI/UX

### 6.1 Silent by Default

Prosodic extraction is **invisible in normal use**. There is no indicator that extraction is happening. The UI does not display prosodic data. The user does not see floats or engagement state summaries.

### 6.2 Settings Toggle

Location: Settings → Voice → Prosodic Signals

- Toggle: on by default
- Label: "Let agents sense how you're speaking"
- Disclosure copy: "Polly measures speech pace, pauses, and volume to help agents respond to how you're speaking, not just what you say. Four signals are derived locally from your audio — no audio is transmitted, and these signals never leave your device or gateway."

The disclosure is factual, non-alarmist, and complete. It does not minimize or euphemize.

### 6.3 Lockdown Mode

In Lockdown Mode: prosodic extraction is **disabled and non-toggleable**.

The settings toggle is replaced with a static label: "Prosodic signals are disabled in Lockdown Mode."

**Rationale (must appear in LOCKDOWN_MODE.md):** Extracted behavioral metadata — speech rate, pause patterns, volume variance — constitutes behavioral evidence that could be compelled on a seized device. In Lockdown Mode, the threat model includes device seizure. Any data that describes how Brett speaks under specific conditions, even in aggregated/derived form, is potentially discoverable. The only safe position is not to generate it.

---

## 7. Implementation Responsibilities

| Owner | Deliverable | Phase |
|-------|-------------|-------|
| @frontend | REQ-VOICE-08: prosodic extraction hook in `useVoiceRecording` | 2 |
| @frontend | `prosodics` field on WebSocket message payload | 2 |
| @backend | Nullable `prosodics` field on ALL message objects in WebSocket schema | 2 |
| @backend | Gateway NL summary generator from prosodic floats | 2 |
| @backend | Context injection: prosodic block ahead of user message | 2 |
| @backend | Absent prosodics: omit block entirely (no null annotation) | 2 |
| @design_eng | Register modulation spec: engagement state → NL summary vocabulary | 2 |
| @design_eng | Per-SOUL `## Prosodic Sensitivity` section spec | 2 |
| @design_eng | Settings toggle UI + disclosure copy | 2 |
| @code_architect | Add `## Prosodic Sensitivity` sections to existing agent SOULs in POLLY_AGENT_TEMPLATES.md | 2 |

---

## 8. Open Questions

None. All design decisions locked as of 2026-03-25.

Decisions on record:
1. `engagement_state` NL summary injected ahead of user message by gateway — agents never see raw floats ✅
2. Absent prosodics = omit block entirely, not null annotation ✅
3. Per-SOUL `## Prosodic Sensitivity` section, agent-specific profiles ✅
4. Silent UI, settings toggle on by default, factual disclosure in settings copy ✅
5. Lockdown mode: disabled + non-toggleable, rationale in LOCKDOWN_MODE.md ✅
6. `prosodics` as nullable field on ALL message objects, not voice-gated ✅
7. No client-side modality branching — gateway handles null cleanly ✅

---

## 9. Dependencies

- Phase 1 voice pipeline live (`expo-av` recording, Whisper transcription, WebSocket send)
- Gateway WebSocket message schema supports nullable `prosodics` field
- LOCKDOWN_MODE.md: must include prosodic extraction disabled + rationale (§6.3 above)
- POLLY_AGENT_TEMPLATES.md: `## Prosodic Sensitivity` sections needed for all agents (Phase 2 task)

---

*Cross-references: VOICE_INTERACTION.md (REQ-VOICE-08), LOCKDOWN_MODE.md (§6.3), POLLY_AGENT_TEMPLATES.md (§5)*

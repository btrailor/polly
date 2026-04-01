# Phase 1: Gesture Layer — Somatic / Prosodic Interface

**Status:** 🔨 In progress  
**Gate:** Real audio recording working (Expo AV or expo-speech-recognition)  
**Spec source:** `SOMATIC_INTERFACE.md`, `GESTURE_LAYER.md` §§4.3, 9 (prosodics only)  
**Owners:** @frontend (iOS signal extraction, UI state), @backend (prosodics schema, gateway field)

> **Scope note:** This change set covers Phase 1 only — prosodic signal extraction and the `prosodics` message field. The full Phase 2 Vocal Gesture System (recognition pipeline, gesture library, Builder agent, Audible Voice Mode, AppIntents) is in `phase-2-gesture-layer`.

---

## Signal Taxonomy

Four prosodic signals, three engagement states, one cognitive load indicator.

### Input Signals (extracted client-side from audio buffer)

| Signal | Extraction | What it indicates |
|--------|-----------|-----------------|
| `speech_rate` | words/minute, rolling 10s window | Cognitive load / urgency / certainty |
| `pause_p95_ms` | 95th percentile pause duration | Processing depth / hesitation / ambiguity |
| `volume_variance` | rolling std dev of amplitude | Emotional intensity / emphasis |
| `turn_length_words` | word count per turn | Engagement depth / summary vs. exploration mode |

**Note:** Full prosodic extraction (`speech_rate`, `pause_p95_ms`, `volume_variance`, `turn_length_words`) requires native `PollyAudioAnalyzer` module (Phase 2, see `phase-1-ios-foundation`). Phase 1 can ship with `speech_rate` + `turn_length_words` only from transcript metadata.

### Engagement States (derived from signal combinations)

| State | Signals | Meaning | Agent response |
|-------|---------|---------|---------------|
| `flowing` | fast speech rate + low pause + moderate volume | Exploring comfortably, in flow | Match pace, minimal friction |
| `processing` | slow rate + long pauses + low variance | Thinking hard, composing complex thought | Space to think, don't rush |
| `struggling` | slow rate + long pauses + high variance + short turns | Stuck or frustrated | Simplify, offer structure |

Default: `null` (no audio, text-only sessions). Agents adapt; they do not label the state to Brett.

### Cognitive Load Indicator (derived)

Composite metric from all four signals. Used to adjust agent verbosity and response structure (not displayed to user directly).

| Load | Signals | Agent adjustment |
|------|---------|----------------|
| Low | fast rate, short pauses, long turns | Full response depth, proactive suggestions |
| Medium | moderate across board | Normal behavior |
| High | slow rate, long pauses, short turns | Shorter responses, more structure, fewer parallel ideas |

---

## Gateway Schema (@backend)

### Message Object Extension
- [ ] Add `prosodics` nullable field to ALL message objects (not gated to voice-only sessions)

```typescript
interface Prosodics {
  speechRate?: number;        // words per minute, rolling 10s window
  pauseP95Ms?: number;        // 95th percentile pause duration in ms
  volumeVariance?: number;    // rolling std dev of audio amplitude
  turnLengthWords?: number;   // word count for this turn
  engagementState?: 'flowing' | 'processing' | 'struggling' | null;
  cognitiveLoad?: 'low' | 'medium' | 'high' | null;
}

interface Message {
  // ... existing fields ...
  prosodics: Prosodics | null;  // null for text-only sessions and voice sessions pre-extraction
}
```

- [ ] Agent receives `prosodics` in context when non-null — agent uses to calibrate response (no instructions needed; SOUL Baseline documents the calibration behavior)
- [ ] `prosodics: null` on all non-voice messages and Phase 1 voice messages (pre-extraction)

---

## iOS — Client-Side Extraction (@frontend)

### Phase 1 (transcript metadata only — no native module)
- [ ] `speech_rate`: calculate words/minute from transcript text + audio duration (from AVAudioPlayer duration field)
- [ ] `turn_length_words`: word count from transcript string
- [ ] Populate `prosodics.speechRate` and `prosodics.turnLengthWords` on voice messages
- [ ] `engagementState` and `cognitiveLoad` remain null until Phase 2 (need all 4 signals)

### Phase 2 (full extraction — requires `PollyAudioAnalyzer` native module)
- [ ] `pause_p95_ms`: from AVAudioEngine PCM frame silence detection
- [ ] `volume_variance`: rolling std dev from PCM amplitude buffer
- [ ] Derive `engagementState` from all 4 signals using thresholds (see SOMATIC_INTERFACE.md)
- [ ] Derive `cognitiveLoad` from composite

---

## iOS — Ambient Feedback UI (@frontend)

The gesture layer has a visual ambient feedback component — **subtle, peripheral, never intrusive**.

### Waveform Orb States

| State | Visual | When |
|-------|--------|------|
| Idle | Static orb, muted tint | No active session |
| Listening | Animated waveform, accent pulse | Recording |
| Processing | Gentle rotation / shimmer | Model generating |
| Flowing | Smooth waveform, normal amplitude | `engagementState: flowing` |
| Processing (state) | Slower pulse, deeper color | `engagementState: processing` |
| Struggling | Reduced animation, softer | `engagementState: struggling` |

### Feedback Rules
- [ ] No text labels showing engagement state — ambient visual only
- [ ] Transitions between states are smooth (300ms ease), never jarring
- [ ] Color uses `polly-card-bg-tint` tint family — not hardcoded
- [ ] Reduced motion: honor `UIAccessibilityIsReduceMotionEnabled` — static orb with color-only state change
- [ ] State feedback is for Brett's awareness, not a diagnostic display

---

## SOUL Baseline Addition — Prosodic Calibration Block

*Adds to the Standard SOUL Baseline in `POLLY_AGENT_TEMPLATES.md`.*

- [ ] Add prosodic calibration block to SOUL Baseline (6th block):

```
## Prosodic Calibration

When prosodics are present in context (voice session), calibrate response to engagement state:
- flowing: match pace, full depth, proactive suggestions welcome
- processing: give space, don't rush, structure helps more than cleverness
- struggling: simplify, offer a frame or a checklist, ask one question not three
- null / text-only: normal behavior

Never label the state to Brett. Never say "I notice you're struggling." Just adapt.
Cognitive load high → shorter responses, more structure, fewer simultaneous ideas.
Cognitive load low → full depth, proactive threads, synthesis welcome.
```

---

## Done When
`prosodics` field on all message objects (@backend). Phase 1 `speechRate` + `turnLengthWords` extraction on iOS. Waveform orb ambient feedback states implemented. Prosodic calibration block in SOUL Baseline. Phase 2 gated on `PollyAudioAnalyzer` native module.

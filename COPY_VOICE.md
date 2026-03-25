# Copy Voice and Design Tokens for Voice Interaction
## Polly Spec | Last updated: 2026-03-24

> *Voice is a first-class interaction mode in Polly. The mic button, waveform, and copy that surrounds voice interaction should all reflect the Monome principles: warm, process-visible, quietly confident.*

---

## Part 1: Design Tokens for Voice States

### Token Implementation

All voice tokens are accessed via the `useColors()` hook in the component:

```typescript
const colors = useColors();
// Usage: colors.voiceActive, colors.voiceWaveformDim, colors.error
```

The hook automatically selects dark/light variants based on system setting — no manual branching needed.

### Token Reference

| Token | Dark Mode | Light Mode | Usage |
|-------|-----------|-----------|-------|
| `voiceActive` | `#f0903b` (8.41:1 contrast) | `voiceActiveLight` `#B86E18` (3.98:1) | Mic button in resting & recording states |
| `voiceWaveformDim` | `#7a4520` | `voiceWaveformDimLight` `#D4A060` | Inactive waveform bars (low amplitude) |
| `voiceWaveformActive` | `#f0903b` | `#B86E18` | Active waveform bars (high amplitude) |
| `error` | `#ef4444` | `#ef4444` | Error state shake, both modes |

**Contrast notes:**
- All tokens verified WCAG AA (3:1 minimum) in both light and dark modes
- Waveform bars are decorative (not text), WCAG AA not required — but verified for consistency
- Light mode uses deeper warm tone to maintain legibility against white backgrounds

---

## Part 2: Voice Button State Machine & Copy

### State 1: Resting (Not Recording)

**Visual treatment:**
- Button: semi-transparent (0.7 opacity), `colors.voiceActive`
- Waveform: hidden
- Pulse: none

**Copy context:** No text directly on button. VoiceOver label: "Record voice message"

**Haptic:** None until tapped

---

### State 2: Recording (Active)

**Visual treatment:**
- Button: opaque, `colors.voiceActive`, gentle pulse (8pt radius, 1.2s duration, continuous)
- Waveform: Three vertical bars, immediately left of button
  - Active bars (current amplitude): `colors.voiceWaveformActive`
  - Inactive bars: `colors.voiceWaveformDim`
  - Real-time animation based on microphone input
- Icon: mic.fill (SF Symbol), white, 24pt

**Copy context:** No text on button. If guidance is needed (e.g., error occurred during recording):
- ✅ "Recording... Tap to stop and send"
- ✗ "Currently recording audio stream"

**Haptic:** Medium impact on initial press (iOS haptic engine)

---

### State 3: Processing (Response in Flight)

**Visual treatment:**
- Button: returns to resting state immediately after send
- Waveform: hidden
- Overlay: Brief spinner (100ms fade-in, continuous rotation, 200ms fade-out on completion)

**Why this design:** Keeps the input layer always active. User can start a new recording while the response is being generated — they're never locked out.

**Copy context (in chat timeline):**
- User's voice message appears with playback controls (optional, implementation detail)
- Spinner indicates "response generating"
- After response lands: "Polly responded" or similar status update (optional, depends on chat UI)

**Haptic:** Light impact on completion (response received)

---

### State 4: Error (Permission Denied, Recording Failed)

**Visual treatment:**
- Button: `colors.error` (`#ef4444`) with brief shake animation (2–3 oscillations, 200ms total)
- Waveform: hidden
- Returns to resting after error dismissal

**Copy context (error message in chat):**
- ✅ "Microphone access denied. Check settings and try again."
- ✅ "Recording failed — network error. Try again?"
- ✗ "Error code: -10048"
- ✗ "Audio input unavailable"

**Haptic:** Error impact (two medium impacts with brief pause)

---

## Part 3: Monome Principles Applied to Voice Copy

### Warm Not Cool

Voice interaction should feel like an *invitation to express*, not an alert state.

| Banking language | Monome language |
|---|---|
| "Audio input stream active" | "Recording..." |
| "Voice capture initiated" | "Listening..." |
| "Processing transcription" | "Understanding..." |
| "Authorization required for microphone access" | "Polly needs microphone access. Go to Settings?" |

**Pattern:** Use present-tense verbs that describe what the system is *doing with* your voice, not what it's *doing to* your voice.

---

### Process Over Product

Show the recording *as it's happening*. The waveform visualization is not decoration — it's transparency.

**What to avoid:**
- Silent recording with no visual feedback
- Spinner that finishes before processing completes
- "Processing..." with no indication of progress

**What to do:**
- Waveform animates in real-time (user sees: "yes, this is capturing my voice")
- Spinner persists for entire response generation (user sees: "work is happening, not stuck")
- Optional: show transcription appearing live as STT processes (if Aight's native layer supports it)

---

### Quiet Confidence

Don't oversell voice capabilities. Voice is a mode, not a magic feature.

| Overconfident | Quietly confident |
|---|---|
| "Get perfect transcription every time!" | "Your voice, as text" |
| "Revolutionary hands-free interaction" | "Talk instead of type" |
| "AI understands your intent with 99% accuracy" | "What would you say?" |

**Pattern:** Name what voice does. Don't claim what it can't do. Let the interaction prove its value.

---

## Part 4: Context-Keyed Copy by Surface

### In Chat (Voice Message Received)

**Display format:**
```
[User's voice message timestamp]
[Playback button] [Duration] [Transcription preview]
Polly is responding...
```

**Copy for states:**
- Recording: "Listening..." (brief status, optional)
- Processing: "Understanding your message..." (brief, honest about latency)
- Response ready: No additional copy — just the response in the chat thread

**Example (good):**
```
You: [playback] 0:23 "What's the difference between..."
Polly: [thinking for ~1.5s]
Actually, great question. Here's where they diverge...
```

---

### In Settings / Onboarding

**Permission request copy:**
- ✅ "Polly uses your microphone to transcribe voice messages. Access is used only during recording."
- ✗ "Grant microphone access for enhanced interaction"

**Feature explanation (if needed):**
- ✅ "Tap the mic button to record instead of typing. Your voice becomes text."
- ✗ "Revolutionary voice interaction powered by advanced speech-to-text technology"

---

### In Error States

**Microphone not available:**
- ✅ "Microphone access denied. You can enable it in Settings > Polly > Microphone."
- ✗ "Voice input is currently unavailable due to permission restrictions"

**Network error during response:**
- ✅ "Lost connection while processing. Try again?"
- ✗ "Failed to transmit voice data to processing backend"

**Recording interrupted (backgrounding, call, etc):**
- ✅ "Recording stopped. Want to try again?"
- ✗ "Audio capture session was interrupted"

---

### In Study Mode (Professor Persona)

Voice recordings in a study context should be framed as exploration, not transcription.

**Opening a study with voice:**
- ✅ "What's your thinking on this?"  [Mic button] ← Invitation
- ✗ "Please provide a voice response" [Mic button] ← Obligation

**After voice response is transcribed:**
- ✅ "I hear you saying [transcription]. Let me follow that thread."
- ✗ "Your statement has been transcribed and classified as [sentiment]"

---

## Part 5: Accessibility Notes

### VoiceOver Labels

- **Mic button (resting):** "Record voice message"
- **Mic button (recording):** "Stop recording"
- **Waveform:** "Live audio input visualization" (decorative, should be marked as `isAccessibilityElement = false` in code)
- **Spinner (processing):** "Response generating, please wait"

### Haptic Feedback

- **Press to record:** Medium impact (`.medium`)
- **Stop recording / Send:** Light impact (`.light`)
- **Error:** Error pattern (`UINotificationFeedbackType.error`)
- **Response received:** Success pattern (`UINotificationFeedbackType.success`)

**Why:** Users with hearing impairment can feel state changes even with sound off. Haptics also confirm touch registration on older devices.

### Color Contrast

All tokens tested at actual opacity values:
- ✅ `voiceActive` at 0.7 opacity passes on dark mode (4.49:1)
- ✅ `voiceActiveLight` at 0.7 opacity passes on light mode (3.98:1)
- ✅ Error state passes on both (4.51:1+ in all cases)

No color-only affordances — state is also communicated through button shape, animation, and haptics.

---

## Part 6: Implementation Checklist

Before shipping voice interaction:

- [ ] Mic button uses `colors.voiceActive` via `useColors()` hook
- [ ] Light mode automatically selects `voiceActiveLight` (no manual branching)
- [ ] Waveform renders to the *left* of mic button (not overlapped)
- [ ] `isIdleTimerDisabled = true` when recording starts; cleared on send, cancel, error, backgrounding
- [ ] Spinner is continuous loop (not fixed 400ms), fades out on response received
- [ ] VoiceOver labels present for button and processing state
- [ ] Haptic feedback triggers on press, stop, error, and completion
- [ ] Error messages use warm, honest copy (not clinical)
- [ ] WCAG AA contrast verified in actual app (colors.ts tokens tested)
- [ ] Dark/light mode tested (both token variants functional)

---

## Part 7: Long-Term Considerations

### Progressive Disclosure

Voice is powerful but unfamiliar to some users. Consider:
- First time user sees mic button: brief tooltip ("Tap to speak" or similar)
- First time voice recording succeeds: confirmation ("That worked!" — warm, brief)
- After 3–5 successful recordings: tooltip fades, mic button feels normal

This isn't in the initial spec but should inform onboarding in Phase 3.

### Transcription Display

If Aight's native STT layer exposes live transcription, consider surfacing it:
- ✅ Live transcription appears as user speaks (builds confidence in accuracy)
- ✗ Wait until recording stops to show transcription (hides the process)

This aligns with Monome principle: "show the process."

### Waveform Refinement

The three-bar waveform is a start. Future iterations could:
- Add a frequency spectrum visualization (optional, complexity increase)
- Show loudness level (green → yellow → red as volume increases) (optional, complexity increase)
- Both are enhancements, not required for v1

---

## Quick Reference: Copy Patterns by Confidence Tier

*(Aligned with QUALITY_AND_BUDGET.md and MEMORY_ARCHITECTURE.md linguistic vocabulary)*

When Polly responds to a voice input, confidence tiers should surface in the response copy:

| Confidence Tier | Linguistic Framing | Example |
|---|---|---|
| **DIRECT** | Confident, grounded | "Your notes from the March meeting say..." |
| **ADJACENT** | Transparent about connection | "I have something related from a different project..." |
| **ABSENT** | Honest about gap | "I don't have this yet. Want to capture it?" |

Voice interaction should not change this model — confidence tiers apply to voice responses the same way they apply to text responses. The microphone button is a *input modality change*, not a *confidence change*.

---

*Voice interaction is infrastructure for thinking aloud, not a novelty feature. The design tokens, copy, and haptics should all reinforce that.*

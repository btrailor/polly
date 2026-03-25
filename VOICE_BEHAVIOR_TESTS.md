# Voice UI Behavior Tests
*Polly QA Spec | Author: @qa_guy | 2026-03-24*
*Covers: REQ-VOICE-01 through REQ-VOICE-04*
*Components: VoiceMicButton, useVoiceRecording, VoiceDraftPrompt*

---

## Evaluation Protocol (Q-3 resolution)

All tests in this spec use one of three evaluation methods:

| Method | When used | Pass threshold |
|--------|-----------|----------------|
| **Automated** | State assertions, prop assertions, call counts | 100% — deterministic |
| **LLM-graded** | Copy/tone assertions, accessibility label quality | 4/5 runs minimum |
| **Human review** | Animation feel, Monome aesthetic, warmth of copy | Sign-off required before ship |

For automated tests: use React Native Testing Library + Jest. For LLM-graded tests: grader prompt is included inline. Human review items are flagged `[HUMAN]`.

---

## Section 1: VoiceButtonState Machine

### TEST-V-001 — State transitions: resting → recording → processing → idle
**Method:** Automated
**Component:** `useVoiceRecording`

```
Setup:
  Render hook with mock onTranscript callback
  Mock: IdleTimer.disable, IdleTimer.enable, startWaveformMetering

Steps:
  1. Initial state
  2. Call startRecording()
  3. Call stopAndSend()
  4. Await processing completion

Assertions:
  1. Initial: recordingState === 'idle'
  2. After startRecording(): recordingState === 'recording'
  3. After stopAndSend(): recordingState === 'processing' (briefly)
  4. After completion: recordingState === 'idle'
  5. onTranscript was called exactly once
```

**Anti-assertion:** MUST NOT remain in 'processing' state after stopAndSend() resolves.

---

### TEST-V-002 — State transitions: resting → recording → cancel → idle
**Method:** Automated
**Component:** `useVoiceRecording`

```
Steps:
  1. startRecording()
  2. cancelRecording()

Assertions:
  - recordingState === 'idle'
  - onTranscript was NOT called
  - errorMessage === null
```

**Anti-assertion:** MUST NOT save a draft on explicit cancel. Cancel is intentional — not an interruption.

---

### TEST-V-003 — Error path: startRecording() throws
**Method:** Automated
**Component:** `useVoiceRecording`

```
Setup:
  Mock Audio.Recording to throw on createAsync

Assertions:
  - recordingState === 'error'
  - errorMessage is non-null and non-empty
  - IdleTimer.enable() was called (idle timer cleared on error path)
```

**Anti-assertion:** MUST NOT leave `recordingRef.current === true` after error.

---

### TEST-V-004 — Error path: stopAndSend() STT failure
**Method:** Automated
**Component:** `useVoiceRecording`

```
Setup:
  Mock transcription to throw

Steps:
  1. startRecording()
  2. stopAndSend() → throws

Assertions:
  - recordingState === 'error'
  - errorMessage includes 'something went wrong' (case-insensitive)
  - onTranscript was NOT called
  - IdleTimer.enable() was called
```

---

## Section 2: Idle Timer Discipline (REQ-VOICE-01)

These are the most critical tests in this suite. Idle timer leaks are a silent device battery issue.

### TEST-V-010 — Idle timer disabled on recording start
**Method:** Automated

```
Steps:
  1. startRecording()

Assertion:
  - IdleTimer.disable() called exactly once before setRecordingState('recording')
  - Order matters: disable THEN state change
```

---

### TEST-V-011 — Idle timer re-enabled on send
**Method:** Automated

```
Steps:
  1. startRecording()
  2. stopAndSend()

Assertion:
  - IdleTimer.enable() called exactly once
  - Called before setRecordingState('idle')
```

---

### TEST-V-012 — Idle timer re-enabled on cancel
**Method:** Automated

```
Assertion: IdleTimer.enable() called on cancelRecording()
Anti-assertion: MUST NOT skip enable() if recordingRef.current was false when cancel called
```

---

### TEST-V-013 — Idle timer re-enabled on app background
**Method:** Automated

```
Setup:
  Spy on AppState event listener

Steps:
  1. startRecording()
  2. Simulate AppState change: 'active' → 'background'

Assertions:
  - IdleTimer.enable() called
  - recordingState === 'idle'
  - Draft was saved (DraftStore.save called)
```

**Anti-assertion:** MUST NOT leave idle timer disabled after backgrounding.

---

### TEST-V-014 — Idle timer re-enabled on unmount mid-recording
**Method:** Automated

```
Steps:
  1. startRecording()
  2. Unmount component without stopping

Assertion:
  - IdleTimer.enable() called during cleanup effect
  - recordingRef.current === false after unmount
```

This is the "never leave idle timer set" guarantee. Failing this test means a device
screen stays on indefinitely after Polly is closed.

---

### TEST-V-015 — Idle timer called exactly once per session (no double-disable)
**Method:** Automated

```
Steps:
  1. startRecording()
  2. startRecording() again (while already recording — should be no-op or guard)

Assertion:
  - IdleTimer.disable() called at most once
```

---

## Section 3: Draft Persistence (REQ-VOICE-04)

### TEST-V-020 — Draft saved on background interruption
**Method:** Automated

```
Steps:
  1. startRecording()
  2. Record for >0 seconds
  3. Simulate AppState: active → background

Assertions:
  - DraftStore.save() called with VoiceDraft object
  - draft.id is non-empty string
  - draft.durationSeconds > 0
  - draft.timestamp > 0
  - pendingDraft is non-null after interruption
```

---

### TEST-V-021 — Draft NOT saved on explicit cancel
**Method:** Automated

```
Steps:
  1. startRecording()
  2. cancelRecording()

Assertion:
  - DraftStore.save() was NOT called
  - pendingDraft === null
```

**Anti-assertion:** Cancel is intentional discard. Saving a draft on cancel is wrong.

---

### TEST-V-022 — Draft loaded on hook mount if present
**Method:** Automated

```
Setup:
  Mock DraftStore.load() to return a VoiceDraft object

Assertion:
  - pendingDraft is set to the mock draft on mount
  - VoiceDraftPrompt would be visible (pendingDraft non-null)
```

---

### TEST-V-023 — Draft discarded on explicit discard action
**Method:** Automated

```
Setup:
  pendingDraft is set (from TEST-V-022 setup)

Steps:
  discardDraft()

Assertions:
  - DraftStore.discard() called with correct draft.id
  - pendingDraft === null after discard
```

**Anti-assertion:** MUST NOT call DraftStore.discard() on send path — send is not discard.

---

### TEST-V-024 — Draft resume triggers new recording session
**Method:** Automated

```
Setup:
  pendingDraft is set

Steps:
  resumeDraft()

Assertions:
  - pendingDraft cleared (setPendingDraft(null))
  - startRecording() called
  - recordingState transitions to 'recording'
```

---

## Section 4: VoiceMicButton Rendering

### TEST-V-030 — Button dimensions meet spec (72×80pt)
**Method:** Automated (layout assertion)

```
Assertion:
  - button width === layout.voiceTouchTargetWidth (72)
  - button height === layout.voiceTouchTargetHeight (80)
```

---

### TEST-V-031 — Waveform visible only in recording state
**Method:** Automated

```
For each state in ['resting', 'processing', 'error']:
  Assertion: waveformContainer is NOT rendered

For state 'recording':
  Assertion: waveformContainer IS rendered with 3 bar elements
```

**Anti-assertion:** Waveform MUST NOT appear in resting, processing, or error states.

---

### TEST-V-032 — Spinner overlay visible only in processing state
**Method:** Automated

```
For each state in ['resting', 'recording', 'error']:
  Assertion: spinnerOverlay is NOT rendered

For state 'processing':
  Assertion: spinnerOverlay IS rendered
```

---

### TEST-V-033 — Error state uses error color, not voice color
**Method:** Automated

```
Render VoiceMicButton with state='error'

Assertion:
  - button backgroundColor === colors.error (not colors.voiceActive)
```

**Anti-assertion:** MUST NOT show voiceActive color (orange) in error state.

---

### TEST-V-034 — Disabled prop prevents onPress
**Method:** Automated

```
Render with disabled=true
Simulate press

Assertion: onPress NOT called
```

---

### TEST-V-035 — Hit slop extends touch target by 8pt on all sides [HUMAN]
**Method:** Human review
**Criteria:** Verify `hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}` is present and correct on device.

---

## Section 5: VoiceDraftPrompt

### TEST-V-040 — Copy matches spec exactly
**Method:** LLM-graded

```
Render VoiceDraftPrompt with draft.durationSeconds=12

Expected copy:
  Message: "You were recording something (12s recording). Want to continue?"
  Primary CTA: "Continue recording"
  Secondary CTA: "Discard"

Grader prompt:
  "Does the rendered text match the expected copy exactly, including punctuation?
   Answer YES or NO with the specific difference if NO."
```

**Anti-assertion:** MUST NOT use alarming language ("Warning", "Alert", "Lost", "Failed").

---

### TEST-V-041 — onResume called on Continue press
**Method:** Automated

```
Simulate press on "Continue recording" button
Assertion: onResume called exactly once, onDiscard NOT called
```

---

### TEST-V-042 — onDiscard called on Discard press
**Method:** Automated

```
Simulate press on "Discard" button
Assertion: onDiscard called exactly once, onResume NOT called
```

---

### TEST-V-043 — Duration label rounds correctly
**Method:** Automated

```
draft.durationSeconds = 0.4 → label: "recording" (not "0s recording")
draft.durationSeconds = 1.0 → label: "1s recording"
draft.durationSeconds = 61.6 → label: "62s recording"
```

---

### TEST-V-044 — Warm, not alarming tone [HUMAN]
**Method:** Human review
**Criteria:** The prompt should feel like a gentle nudge, not a system alert. Evaluate on device in context of chat UI. Pass if a non-technical reviewer describes it as "helpful" or "calm" unprompted.

---

## Section 6: Accessibility

### TEST-V-050 — Button has correct accessibilityRole
**Method:** Automated

```
Assertion: accessibilityRole === 'button'
```

---

### TEST-V-051 — accessibilityState.selected reflects recording state
**Method:** Automated

```
state='resting' → accessibilityState.selected === false
state='recording' → accessibilityState.selected === true
state='processing' → accessibilityState.selected === false
state='error' → accessibilityState.selected === false
```

---

### TEST-V-052 — Waveform bars are hidden from accessibility tree
**Method:** Automated

```
Render in recording state
Assertion: waveformContainer has accessibilityElementsHidden={true}
```

Waveform is decorative. Screen reader users don't need three unlabeled animated bars.

---

### TEST-V-053 — Draft prompt has accessibilityLiveRegion="polite"
**Method:** Automated

```
Assertion: VoiceDraftPrompt container has accessibilityLiveRegion="polite"
```

Ensures VoiceOver announces the draft recovery prompt without interrupting the user.

---

## Section 7: Multi-Turn / Integration Scenarios

These test sequences that can't be caught in unit tests.

### TEST-V-060 — Full happy path: start → record → send → transcript delivered
**Method:** Automated (integration)

```
Render chat.tsx with mocked STT returning "hello world"

Steps:
  1. Tap mic button (state: resting → recording)
  2. Wait 500ms (waveform animating)
  3. Tap mic button again (stop and send)
  4. Wait for processing → idle

Assertions:
  - Input bar shows transcript "hello world"
  - recordingState === 'idle'
  - No draft saved
  - Idle timer enabled
```

---

### TEST-V-061 — Interruption recovery: background → foreground → resume
**Method:** Automated (integration)

```
Steps:
  1. startRecording()
  2. AppState: active → background (triggers draft save)
  3. AppState: background → active (app returns)

Assertions:
  - VoiceDraftPrompt is rendered
  - Tap "Continue recording"
  - recordingState transitions to 'recording'
  - Old draft is cleared
```

---

### TEST-V-062 — Error recovery: error state → tap → back to recording
**Method:** Automated (integration)

```
Steps:
  1. startRecording() → mock throws → state: error
  2. Tap mic button again

Assertions:
  - errorMessage cleared
  - startRecording() called
  - recordingState: error → recording
```

**This tests that the error state is recoverable.** A stuck error state is a dead UI.

---

## Gap Tracker Cross-Reference

| Q-series item | Resolution |
|---|---|
| Q-3 (evaluation rubric undefined) | ✅ Defined in Evaluation Protocol section — Automated / LLM-graded / Human review with thresholds |
| Q-2 (multi-turn tests) | ✅ Section 7: TEST-V-060, 061, 062 |
| Q-1 (anti-assertions) | ✅ Anti-assertions present on every test with a failure mode |

---

*Next: Behavior tests for persona system (Q-1, Q-2 for PERSONA_CHARACTER_SHEETS.md) and Professor system prompt constraint tests (Q-7).*

# Voice Interaction — Polly Design Spec

## Background

Aight has a known UX failure: when recording voice input, the iPhone screen sleep timer is not suppressed. If the user doesn't touch the screen during a long recording, the device sleeps and the recording is lost. This is unacceptable for a voice-first interaction mode.

Polly should do better on both fronts: **reliability** and **prominence**.

---

## Requirements

### REQ-VOICE-01: Suppress Screen Sleep During Voice Recording

- When the user begins a voice recording (microphone active), Polly MUST acquire `UIApplication.shared.isIdleTimerDisabled = true`
- When recording ends (user taps stop, send, or cancels), restore `isIdleTimerDisabled = false`
- This must happen regardless of recording duration
- Edge case: if the app is backgrounded while recording, the recording should be paused and preserved — not lost

**Implementation note:** `isIdleTimerDisabled` is the standard iOS mechanism. It must be set on the main thread. Set on recording start, clear on recording end in all exit paths (send, cancel, error, background transition).

---

### REQ-VOICE-02: Prominent Microphone Button

- The microphone button in Polly's chat UI should be **larger and more visually prominent** than the Aight equivalent
- Design intent: voice should feel like a first-class, encouraged mode of interaction — not a hidden affordance
- Minimum tap target: 60x60pt (vs iOS standard 44x44pt)
- Visual treatment: consider a distinct color, subtle pulse animation when idle to invite use, or elevated position in the input bar
- Should not compete with the text input — should complement it as an equal alternative

---

### REQ-VOICE-03: Recording State Feedback

- While recording is active, the UI must clearly communicate:
  - That recording is in progress (visual indicator)
  - That the screen will stay awake (user confidence)
- No spinner or "processing" state should appear until recording is explicitly stopped

---

## Design Notes

Voice as a mode of interaction aligns with the Monome aesthetic: process over product, warm not cool. Tapping a mic and speaking is more immediate and human than typing. The UI should reflect that — the mic button should feel like an invitation, not a utility.

Aight treats voice as a secondary input. Polly should treat it as primary.

---

### REQ-VOICE-04: Recording Interruption Recovery

If a recording is interrupted (app backgrounded, audio session interrupted by phone call or system event), the in-progress audio/transcript MUST NOT be silently discarded.

Behavior:
- **App backgrounded mid-recording:** Stop recording, auto-save as draft. On return to foreground, surface a "Resume your recording?" prompt with the option to continue or discard.
- **Audio session interrupted (phone call, etc.):** Stop recording immediately, save draft. Clear `isIdleTimerDisabled` in the interruption handler. On interruption end, prompt to resume or discard.
- **Draft storage:** Save to a temp location (e.g. `Documents/voice-drafts/`) with a timestamp. Discard on explicit user action only — never automatically.

The failure mode being prevented: user dictates a long message, gets a phone call, returns to app, and finds nothing. That must be impossible in Polly.

---

## Implementation Checklist

### REQ-VOICE-01: Idle Timer — All Exit Paths
- [ ] `isIdleTimerDisabled = true` on recording start (main thread)
- [ ] `isIdleTimerDisabled = false` on normal send
- [ ] `isIdleTimerDisabled = false` on cancel/dismiss
- [ ] `isIdleTimerDisabled = false` in `applicationWillResignActive`
- [ ] `isIdleTimerDisabled = false` in audio session interruption handler
- [ ] `isIdleTimerDisabled = false` on any error path

### REQ-VOICE-02: Mic Button
- [ ] Tap target minimum 72×80pt (visual size @design_eng discretion, tap target generous)
- [ ] Visual prominence treatment — color/weight per @design_eng
- [ ] Pulse/invite animation when idle (optional, @design_eng discretion)

### REQ-VOICE-03: Recording State Feedback
- [ ] Recording-in-progress indicator visible while active
- [ ] No processing spinner until recording explicitly stopped

### REQ-VOICE-04: Interruption Recovery
- [ ] Auto-save draft on backgrounding mid-recording
- [ ] Auto-save draft on audio session interruption
- [ ] "Resume your recording?" prompt on foreground return
- [ ] Draft stored to `Documents/voice-drafts/` with timestamp
- [ ] Draft discarded only on explicit user action (never automatically)

---

*Filed by user feedback, 2026-03-24. Addresses known Aight regression.*

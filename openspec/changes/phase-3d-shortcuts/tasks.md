# Phase 3D: Shortcuts + App Intents

**Status:** 💡 Specced  
**Gate:** Phase 1 complete  
**Spec source:** `POLLY_IOS_SPEC.md` §4.3  
**Owners:** @frontend (React Native bridge), native Swift module

## Goal

`ShortcutsView` — saved prompt shortcuts for quick access. Plus Apple App Intents registration so Polly shortcuts appear in Siri Suggestions and Shortcuts app.

## Tasks

### ShortcutsView (In-App)
- [ ] Shortcuts list in app (Today View or dedicated tab)
- [ ] Create shortcut: name, emoji, prompt text, target agent, target group
- [ ] Edit + delete shortcuts
- [ ] Tap shortcut → opens chat session with prompt pre-filled (or sends immediately)
- [ ] Shortcuts stored in gateway config (`polly.shortcuts[]`) + MMKV cache
- [ ] Reorder via drag

### Apple App Intents (Native)
- [ ] Native Swift module: `AppIntents` framework
- [ ] React Native bridge for App Intent registration
- [ ] Register each shortcut as an App Intent: "Ask [Agent Name]" + shortcut name
- [ ] Siri phrase: "Hey Siri, ask [agent] about [shortcut]"
- [ ] Shortcuts app integration: shortcuts appear in Shortcuts.app editor
- [ ] App Intent donation on use (improves Siri suggestions)

### Widget (Optional)
- [ ] Home screen widget: 2×2 grid of most-used shortcuts
- [ ] Tap widget shortcut → deep link to chat

## Gesture Layer AppIntents (from `GESTURE_LAYER.md §10` — added Phase 2)

These two intents share the same native Swift AppIntents module. Gate: Phase 2 voice pipeline live.

### TellPollyIntent
- [ ] `TellPollyIntent: AppIntent` — accepts `phrase: String` parameter
- [ ] Deep link: `polly://gesture?phrase=<phrase>`
- [ ] App foregrounds → gesture recognizer processes phrase
- [ ] No-match fallback: phrase becomes pre-filled chat input (never fails silently)
- [ ] Siri phrase: "Hey Siri, tell Polly [phrase]" → entire gesture library available via Siri with zero extra registration
- [ ] Shortcuts.app: appears as "Tell Polly [phrase]" — Brett can build automations (morning routine → "tell Polly morning pages", etc.)

### OpenListeningIntent
- [ ] `OpenListeningIntent: AppIntent` — no parameters
- [ ] Deep link: `polly://listen`
- [ ] App opens to active chat, mic starts recording immediately (no additional tap)
- [ ] Lockdown Mode exception: normal open (no auto-mic) — document in `LOCKDOWN_MODE.md`
- [ ] Onboarding suggestion: "Set your Action Button to open Polly instantly — tap here for setup instructions" (after voice pipeline working)
- [ ] Action Button setup: iOS Settings → Action Button → Shortcut → "Open Polly Listening"

### Lock Screen Widget (Phase 3 — defer)
- [ ] Narrow lock screen widget, single mic button, tap → `OpenListeningIntent`

## Done When
Shortcuts create/edit/delete/run working. App Intents registered. Siri phrase triggers correct agent. `TellPollyIntent` + `OpenListeningIntent` registered and working. Action Button onboarding suggestion shown. @qa_guy confirms Shortcuts.app integration.

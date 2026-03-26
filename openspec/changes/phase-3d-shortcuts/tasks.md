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

## Done When
Shortcuts create/edit/delete/run working. App Intents registered. Siri phrase triggers correct agent. @qa_guy confirms Shortcuts.app integration.

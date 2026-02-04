# Phase 10: iOS Mobile App

**Status:** Future Planning  
**Priority:** Low (Long-term Goal)  
**Estimated Effort:** 3-4 weeks  
**Dependencies:** 
- Phase 9 (macOS Permissions) - For testing permission flows
- Stable desktop app
- Tailscale setup

---

## Overview

Build an iOS companion app for Polly that syncs with the desktop app, enabling mobile access to conversations, quick capture, and voice input.

### Vision

**Not a full replacement for desktop app**, but a mobile companion for:
- Quick capture (voice notes, photos, text)
- Conversation access on the go
- Voice input/output
- Offline mode with local models
- Sync via Tailscale (private network)

---

## Goals

### Primary Goals

1. **SwiftUI-based iOS App**
   - Native iOS experience
   - Fast and responsive
   - Follows Apple Human Interface Guidelines

2. **Sync with Desktop via Tailscale**
   - Secure private network connection
   - No cloud intermediary
   - Direct device-to-device sync

3. **Quick Capture**
   - Voice notes (transcribed via Whisper)
   - Photos with OCR
   - Text snippets
   - Auto-sync to desktop

4. **Conversation Access**
   - View all conversations
   - Send messages
   - Receive responses
   - Sync conversation history

5. **Voice Input/Output**
   - Speech-to-text (iOS dictation or Whisper)
   - Text-to-speech for responses
   - Hands-free mode

6. **Offline Mode**
   - Local Ollama models (if device supports)
   - Cached conversations
   - Queue actions for sync when online

---

## Implementation Plan (High-Level)

### Week 1: Foundation

**Tasks:**
1. Set up Xcode project (SwiftUI)
2. Design app architecture (MVVM)
3. Create data models (Conversation, Message, etc.)
4. Set up Core Data for local storage
5. Design UI mockups

**Deliverables:**
- iOS project structure
- Core Data schema
- UI designs

### Week 2: Sync & Networking

**Tasks:**
1. Implement Tailscale connection
2. Create API client for desktop Polly
3. Implement conversation sync (bidirectional)
4. Handle conflict resolution
5. Test sync reliability

**Deliverables:**
- Sync engine
- Network layer
- Conflict resolution

### Week 3: Features

**Tasks:**
1. Build conversation list view
2. Build conversation detail view
3. Implement message sending
4. Add voice input (iOS dictation)
5. Add quick capture UI
6. Implement photo capture with OCR

**Deliverables:**
- Full conversation UI
- Voice and photo capture

### Week 4: Polish & Testing

**Tasks:**
1. Add text-to-speech
2. Implement offline mode
3. Add settings screen
4. Test on multiple devices (iPhone, iPad)
5. App Store preparation
6. TestFlight beta

**Deliverables:**
- Polished iOS app
- TestFlight beta

---

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    iOS App (SwiftUI)                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Views (SwiftUI)                                 │   │
│  │  • ConversationListView                          │   │
│  │  • ConversationDetailView                        │   │
│  │  • QuickCaptureView                              │   │
│  │  • SettingsView                                  │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ViewModels                                      │   │
│  │  • ConversationListViewModel                     │   │
│  │  • ConversationDetailViewModel                   │   │
│  │  • SyncManager                                   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Services                                        │   │
│  │  • APIClient (talks to desktop)                  │   │
│  │  • SyncEngine (bidirectional sync)               │   │
│  │  • VoiceService (STT/TTS)                        │   │
│  │  • CaptureService (photos, notes)                │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Data Layer                                      │   │
│  │  • Core Data (local storage)                     │   │
│  │  • Models (Conversation, Message, Capture)       │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                            ↓ Tailscale
┌─────────────────────────────────────────────────────────┐
│                Desktop Polly (FastAPI)                   │
│  • Conversations API                                     │
│  • Messages API                                          │
│  • Sync API                                              │
│  • RAG API                                               │
└─────────────────────────────────────────────────────────┘
```

### Sync Strategy

**Pull-based sync:**
1. iOS app polls desktop for changes (every 5-10 seconds when active)
2. Desktop sends conversation diffs
3. iOS merges changes into Core Data
4. iOS sends local changes to desktop
5. Desktop ACKs changes

**Conflict resolution:**
- Last-write-wins for message edits
- Append-only for new messages (no conflicts)
- Version vectors for conversation metadata

### Voice Features

**Speech-to-Text:**
- iOS native dictation (free, works offline)
- Or Whisper API (more accurate, requires network)

**Text-to-Speech:**
- iOS native TTS (free, works offline)
- Configurable voice

---

## UI Mockups

### Conversation List

```
┌──────────────────────────────┐
│ Polly              [+] [⚙️]  │
├──────────────────────────────┤
│                               │
│ 🔐 Sigils                     │
│  • Pattern Learning Disc...  │
│    2h ago · 12 messages       │
│                               │
│  • Refactor router system    │
│    Yesterday · 8 messages     │
│                               │
│ 📜 Scrolls                    │
│  • Essay on pedagogy         │
│    3d ago · 5 messages        │
│                               │
│ [🎤] Quick Capture            │
└──────────────────────────────┘
```

### Conversation Detail

```
┌──────────────────────────────┐
│ ← Pattern Learning Disc...   │
├──────────────────────────────┤
│                               │
│ You: Can you help me fix...  │
│      10:30 AM                 │
│                               │
│ Polly: Sure! Let me look...  │
│        10:31 AM               │
│        [📎 Code]              │
│                               │
│ You: Thanks!                  │
│      10:35 AM                 │
│                               │
├──────────────────────────────┤
│ [🎤] Message...         [↑]  │
└──────────────────────────────┘
```

### Quick Capture

```
┌──────────────────────────────┐
│ Quick Capture         [Done] │
├──────────────────────────────┤
│                               │
│ [ Voice Note ]                │
│ [ Photo ]                     │
│ [ Text ]                      │
│ [ Clipboard ]                 │
│                               │
│ Recent Captures:              │
│  • "Remember to call Mom"     │
│    2h ago                     │
│  • Photo of whiteboard        │
│    Yesterday                  │
│                               │
└──────────────────────────────┘
```

---

## Success Criteria

- ✅ iOS app connects to desktop via Tailscale
- ✅ Conversations sync bidirectionally
- ✅ Voice input works smoothly
- ✅ Quick capture saves to desktop
- ✅ Offline mode queues actions
- ✅ App passes TestFlight review

---

## Why This Is Low Priority

**Desktop app is primary interface:**
- Full feature set
- Larger screen
- Better for complex tasks

**Mobile app is nice-to-have:**
- Convenient for quick tasks
- Access on the go
- Voice capture

**But not essential for Polly's core functionality.**

**Focus should be on:**
1. Phase 9 (unlock 3 integrations)
2. Phases 11-14 (intelligence enhancements)
3. Then consider Phase 10

---

## Future Enhancements

### Phase 10.5: iPad Optimization
- Sidebar layout
- Multi-window support
- Apple Pencil integration

### Phase 10.6: watchOS App
- Quick voice capture
- Notification responses
- Complication support

### Phase 10.7: Shortcuts Integration
- Siri integration
- iOS Shortcuts actions
- Home Screen widgets

---

**Last Updated:** January 21, 2026  
**Status:** Future Planning  
**Priority:** Low - Nice to Have

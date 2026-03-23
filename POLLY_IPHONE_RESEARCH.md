# Polly iPhone App — Research Report
**Research Date:** March 23, 2026  
**Last Updated:** March 23, 2026 (Architecture Correction)  
**Purpose:** Design a native iPhone app ("Polly") that replaces Aight as the mobile client for OpenClaw, with Polly's unique attributes layered on top.

## ⚠️ Architecture Correction (v2)

**Polly is the iOS client. OpenClaw is the engine. This is the same relationship as Aight → OpenClaw.**

- OpenClaw gateway remains unchanged and central
- Polly does NOT build its own gateway, AI routing, or session management
- Polly connects to `ws://[gateway]:18789` using the same protocol Aight uses today
- The entire project scope is the native iOS app + Polly's unique differentiators on top
- When Aight goes freemium, users run Polly instead — same OpenClaw backend, different client

---

## Polly Screen Map (Revised)

| Screen | What It Does | OpenClaw Backend |
|--------|-------------|-----------------|
| **Chat** | Agent + group chat, streaming, voice | Gateway WebSocket |
| **Today / Calendar** | Reminders, tasks, triggers, processes | `aight_item` tool + cron |
| **Shortcuts** | Saved prompts, quick access | Shortcut protocol |
| **Moltbook** | View/browse OpenClaw memory/notebook layer | Memory API |
| **Usage Stats** | Token usage, cost, model breakdowns | Gateway stats API |
| **Settings** | Gateway URL, providers, API keys, agents | `openclaw.json` via gateway |

## Polly Differentiators (On Top of OpenClaw)

- **Design system** — Polly branding, orange `#f0903b` accent, Obsidian-inspired dark aesthetic
- **RAG chat** — `/` slash command injects Obsidian notes as context into messages
- **Domain awareness** — shows active domain (Sigils/Signals/Scrolls) in chat header
- **Mental model selector** — quick-switch frameworks from within chat
- **Pattern transparency** — "Polly learned X" cards in Today view
- **Vault browser** — browse and search Obsidian vault from the app

---

## 1. What Aight Actually Does (Feature Audit)

Aight is a native iOS app that connects to the OpenClaw gateway over WebSocket. It is essentially a **mobile client** for an already-running backend. It does NOT run AI itself — it connects to your self-hosted OpenClaw gateway (`ws://127.0.0.1:18789` via Tailscale/local network).

### Core Aight Features

#### 1.1 Gateway Communication
- WebSocket connection to OpenClaw gateway (port 18789)
- Authentication via device pairing (`sendKey`, `deviceId`)
- Real-time bidirectional message streaming
- Push notifications via APNs (device registered in `~/.openclaw/aight/devices.json`)

#### 1.2 Chat Interface
- Multi-agent chat sessions (switch between agents)
- Group chat with multiple agents simultaneously
- Markdown rendering (code blocks, bold, headers, etc.)
- Streaming responses (text appears token-by-token)
- Message history scrollback
- Tool call visibility (see what the AI is doing)

#### 1.3 Voice Mode
- Speech-to-text (client-side, iOS native AVFoundation/Speech framework)
- Text-to-speech for AI responses (client-side, iOS AVSpeechSynthesizer)
- Tap-to-talk or continuous listening mode

#### 1.4 Today View / Dashboard
- Reminders and tasks (backed by OpenClaw `aight_item` tool)
- Scheduled triggers with `scheduledFor` ISO 8601
- Process items (background agent runs)
- Item lifecycle: active → done / cancelled

#### 1.5 Shortcuts
- Saved prompt shortcuts with emoji + short name
- Quick-access panel
- JSON-based shortcut labeling protocol (the `shortcut:` prefix in system prompt)

#### 1.6 Skills / Marketplace
- Browse and install OpenClaw skills from ClawHub
- Skills extend agent tool capabilities

#### 1.7 Agent Management
- View and switch between configured agents
- Read from `~/.openclaw/openclaw.json` agents list via gateway API
- Custom agent personas with SOUL.md

#### 1.8 Push Notifications
- APNs integration for background cron job completions
- Isolated agent turn completions delivered to device

#### 1.9 Settings
- Gateway URL configuration
- Model selection
- Auth token management

---

## 2. Polly Current State (What Already Exists)

### 2.1 Polly Core (Python, `~/polly/core/`)
- **RAG system** — multi-source semantic search (Obsidian vault, codebases, docs)
- **Multi-provider routing** — Anthropic, OpenAI, Gemini, Mistral, Grok, Perplexity, GitHub Models
- **Mental models** — 12 default frameworks applied to responses
- **Pattern learning** — discovers and reuses your work patterns
- **Agent personas** — Architect, Scribe, Professor with modal modes
- **Compression** — context compression for long conversations
- **Skills system** — extensible tool plugins
- **Domain awareness** — Sigils/Signals/Scrolls/Glyphs/Grids

### 2.2 Polly Interfaces (Already Built)
- **CLI** — `polly` command line tool
- **FastAPI server** (`interfaces/server.py`) — OpenAI-compatible API on `localhost`
- **Electron Desktop App** (`electron-app/`) — chat UI, notes, dashboard, personas
- **Web interface** (`web/`, `interfaces/dashboard.py`)

### 2.3 What Polly Lacks for Mobile
- No WebSocket gateway (it has HTTP/FastAPI only)
- No iOS push notification infrastructure
- No mobile-native UI
- No device pairing/authentication flow
- No cron/scheduling system
- No group chat multi-agent coordination (yet)

---

## 3. The Gap Analysis: Aight → Polly iPhone

| Aight Feature | OpenClaw Provides | Polly Has | Gap |
|--------------|-------------------|-----------|-----|
| Gateway WebSocket | ✅ Node.js gateway | ❌ HTTP only | Need WebSocket layer |
| iOS native app | ✅ Aight app | ❌ None | **Need to build** |
| Agent sessions | ✅ Full session mgmt | ⚠️ Per-request only | Session persistence |
| Multi-agent | ✅ Native | ⚠️ Personas only | Multi-agent routing |
| Push notifications | ✅ APNs via gateway | ❌ None | Need APNs integration |
| Voice (STT/TTS) | ✅ Client-side iOS | ⚠️ Electron basic | iOS native voice |
| Today view / items | ✅ aight_item tool | ❌ None | Need item system |
| Shortcuts | ✅ Protocol built-in | ❌ None | Need shortcuts system |
| Skills marketplace | ✅ ClawHub | ⚠️ Core skills | Local skills only |
| Markdown streaming | ✅ Native | ⚠️ Electron only | iOS markdown |
| Cron/scheduling | ✅ Native cron system | ❌ None | Need scheduler |
| Memory (MEMORY.md) | ✅ Per-agent | ⚠️ RAG only | Structured memory |

---

## 4. Architecture Recommendation: Polly-Gateway

The key insight: **Aight is just a client. The real work is in the gateway.** 

Polly needs a **lightweight Python gateway** that mirrors OpenClaw's WebSocket protocol, so the Polly iPhone app (or even Aight temporarily) can connect to it.

### 4.1 Two-Layer Architecture

```
iPhone (Polly App)
       │
       │ WebSocket (ws://[tailscale-ip]:18789)
       │ OR REST + SSE for streaming
       ▼
┌──────────────────────────────────────────┐
│         POLLY GATEWAY (New)              │
│  - Session management                    │
│  - Message routing                       │
│  - Push notification dispatch (APNs)     │
│  - Cron scheduler                        │
│  - Today items store                     │
│  - Shortcut registry                     │
└──────────────────┬───────────────────────┘
                   │
       ┌───────────▼───────────┐
       │     POLLY CORE        │
       │  - RAG               │
       │  - Multi-provider    │
       │  - Mental models     │
       │  - Pattern learning  │
       │  - Agent personas    │
       │  - Skills            │
       └───────────────────────┘
```

### 4.2 Gateway Protocol (OpenClaw-Compatible)

OpenClaw gateway runs on `ws://127.0.0.1:18789`. The Aight app connects via this WebSocket. To make Polly work with Aight (as a transitional step), OR to inform the protocol for the Polly iPhone app, the Polly gateway should implement a compatible subset:

**Key Message Types:**
- `message:send` — User sends a message, agent responds (streaming)
- `session:create` / `session:load` — Session management  
- `agent:list` — Available agents
- `item:create` / `item:update` — Today view items
- `cron:add` / `cron:list` — Scheduled jobs
- `push:register` — APNs device registration
- `shortcut:list` / `shortcut:invoke`

---

## 5. iPhone App Architecture

### 5.1 Tech Stack Recommendation

**Option A: Swift + SwiftUI (Recommended)**
- Native iOS performance
- Best voice integration (AVFoundation, Speech framework)
- Native push notifications
- Best Markdown rendering (via AttributedString or MarkdownUI library)
- Full access to iOS system APIs
- App Store distributable

**Option B: React Native**
- Code reuse with potential web/Electron
- Slower native feel
- More complex WebSocket management
- Voice requires native modules anyway

**Option C: Capacitor/Ionic (Electron-app web wrapped)**
- Fastest to build (reuse electron-app code)
- Worst performance
- Not good for voice
- Not recommended for production

→ **Recommendation: Swift + SwiftUI**

### 5.2 Core Modules to Build

#### Module 1: GatewayClient.swift
```swift
// WebSocket connection to Polly Gateway
// Handles: connect, reconnect, auth, message routing, streaming
class GatewayClient: ObservableObject {
    @Published var connectionState: ConnectionState
    @Published var messages: [ChatMessage]
    
    func connect(url: URL, sendKey: String)
    func sendMessage(_ text: String, agentId: String, sessionId: String)
    func streamResponse(handler: @escaping (String) -> Void)
}
```

#### Module 2: VoiceManager.swift
```swift
// Speech-to-text + text-to-speech (all on-device)
class VoiceManager: ObservableObject {
    func startListening() // SFSpeechRecognizer
    func stopListening() -> String // Returns transcript
    func speak(_ text: String) // AVSpeechSynthesizer
    var isListening: Bool
}
```

#### Module 3: ChatView.swift
```swift
// Main chat interface
// Features: streaming markdown, agent switcher, voice button,
// tool call visibility, shortcuts bar
struct ChatView: View { ... }
```

#### Module 4: TodayView.swift
```swift
// Dashboard: reminders, tasks, processes
// Backed by Polly Gateway items API
struct TodayView: View { ... }
```

#### Module 5: AgentSwitcher.swift
```swift
// List agents from gateway, switch context
// Group chat creation
```

#### Module 6: PushNotificationManager.swift
```swift
// APNs registration, token to gateway
// Handle incoming push for cron completions
```

#### Module 7: MarkdownRenderer.swift
```swift
// Streaming markdown rendering
// Code blocks with syntax highlighting
// MarkdownUI or custom AttributedString renderer
```

### 5.3 Screen Map

```
Tab Bar:
├── 💬 Chat
│   ├── Single agent chat (default)
│   ├── Group chat (multi-agent)
│   └── Agent switcher (slide up)
├── 📅 Today
│   ├── Reminders list
│   ├── Tasks list
│   └── Active processes
├── ⚡ Shortcuts
│   └── Saved prompt grid
├── 🤖 Agents
│   ├── Agent list
│   └── Agent detail / edit SOUL.md
└── ⚙️ Settings
    ├── Gateway URL + auth
    ├── Model selection
    ├── Voice settings
    └── Notification preferences
```

---

## 6. Polly Gateway (Python — New Component)

This is the critical missing piece. Polly needs a persistent gateway process (like OpenClaw's Node.js gateway) but in Python.

### 6.1 Tech Stack
- **FastAPI + WebSockets** (already in Polly ecosystem)
- **asyncio** for concurrent session handling
- **SQLite** for session/item/cron persistence (via `~/.polly/gateway.db`)
- **APNs** via `httpx` + JWT (for push notifications)
- **APScheduler** for cron jobs

### 6.2 Key Endpoints

```python
# WebSocket
ws://localhost:18789/ws?deviceId=X&sendKey=Y

# REST fallback
POST /v1/messages           # Send message
GET  /v1/messages/stream    # SSE streaming
GET  /v1/sessions           # List sessions
POST /v1/sessions           # Create session
GET  /v1/agents             # List agents
POST /v1/items              # Create today item
PATCH /v1/items/{id}        # Update item
GET  /v1/cron               # List cron jobs
POST /v1/cron               # Add cron job
POST /v1/push/register      # Register APNs device
```

### 6.3 Session Management
```python
# ~/.polly/sessions/{agent_id}/{session_id}/
#   messages.jsonl      - Message history
#   context.json        - Session metadata
#   MEMORY.md           - Persistent agent memory (mirrors OpenClaw)
```

### 6.4 Items System (Today View)
```python
# Mirror OpenClaw's aight_item tool
class Item(BaseModel):
    id: str
    type: Literal["trigger", "item", "process"]
    title: str
    description: Optional[str]
    status: Literal["active", "done", "cancelled"]
    labels: List[str]
    scheduledFor: Optional[datetime]  # For triggers
    createdAt: datetime
    updatedAt: datetime
```

---

## 7. Phased Implementation Plan

### Phase 1: Polly Gateway MVP (2-3 weeks)
**Goal:** Polly core accessible via WebSocket from iPhone

- [ ] `polly/gateway/` Python module
- [ ] WebSocket server (FastAPI + WebSockets)
- [ ] Session persistence (SQLite)
- [ ] Message routing → Polly core
- [ ] Streaming response support
- [ ] Basic auth (sendKey)
- [ ] Agent listing (read from `~/.polly/agents/`)
- [ ] Launchd daemon (auto-start on macOS boot)

### Phase 2: Polly iPhone App MVP (3-4 weeks)
**Goal:** Chat with Polly from iPhone

- [ ] Xcode project setup
- [ ] GatewayClient (WebSocket + auth)
- [ ] ChatView (streaming markdown)
- [ ] Agent switcher
- [ ] Settings (gateway URL, auth)
- [ ] Voice (STT/TTS using iOS native APIs)
- [ ] Testflight distribution (personal use, no App Store needed)

### Phase 3: Today View + Reminders (1-2 weeks)
**Goal:** Task/reminder parity with Aight

- [ ] Items API in gateway
- [ ] TodayView in iOS app
- [ ] `polly_item` tool for agents to create reminders
- [ ] Cron scheduler (APScheduler)
- [ ] Push notifications (APNs)
- [ ] `polly_cron` tool for scheduling

### Phase 4: Shortcuts + Group Chat (1-2 weeks)
**Goal:** Full feature parity with Aight

- [ ] Shortcuts system (saved prompts)
- [ ] Multi-agent group chat sessions
- [ ] Shortcut labeling protocol (mirrors Aight's `shortcut:` JSON response)

### Phase 5: Polish + Polly-Specific Features (ongoing)
**Goal:** Exceed Aight by leveraging Polly's strengths

- [ ] RAG context injection in chat (type `/` to reference notes)
- [ ] Domain-aware responses (Polly's 5 domains)
- [ ] Mental model selector in app
- [ ] Pattern learning transparency (show what Polly learned)
- [ ] Obsidian vault browser
- [ ] Knowledge graph visualization

---

## 8. Distribution Strategy

Since this is for personal use (no App Store review needed):

**Option A: TestFlight (Recommended)**
- Free, requires Apple Developer Program ($99/yr)
- 90-day test builds, personal install
- OTA updates
- Best option for ongoing personal use

**Option B: AltStore / Sideloading**
- Free, no developer account needed for basic
- More friction (7-day re-sign unless AltStore server)
- Works for non-commercial personal apps

**Option C: Self-hosted MDM**
- Overkill for 1 device
- Enterprise certificate ($299/yr)

→ **Recommendation: TestFlight** — simplest, most reliable for personal use

---

## 9. Key Files to Create

### Gateway (Python)
```
~/polly/gateway/
├── __init__.py
├── server.py          # FastAPI + WebSocket gateway
├── session_manager.py # Session persistence
├── item_store.py      # Today view items
├── scheduler.py       # APScheduler cron
├── push.py            # APNs integration
├── agent_loader.py    # Load agent configs
└── tools/
    ├── polly_item.py  # Tool for agents
    └── polly_cron.py  # Tool for agents
```

### iOS App (Swift)
```
PollyApp/
├── App/
│   └── PollyApp.swift
├── Gateway/
│   ├── GatewayClient.swift
│   └── Models.swift
├── Views/
│   ├── ChatView.swift
│   ├── TodayView.swift
│   ├── ShortcutsView.swift
│   ├── AgentsView.swift
│   └── SettingsView.swift
├── Components/
│   ├── MessageBubble.swift
│   ├── MarkdownRenderer.swift
│   ├── VoiceButton.swift
│   └── StreamingText.swift
├── Services/
│   ├── VoiceManager.swift
│   ├── PushNotificationManager.swift
│   └── StorageService.swift
└── Resources/
    └── Assets.xcassets
```

---

## 10. Leveraging Polly's Unique Advantages

The Polly iPhone app should be *better* than Aight in these ways:

1. **Knowledge-aware chat** — `/` slash command opens Obsidian vault, inserts note as context
2. **Domain routing** — App shows which domain (Sigils/Signals/Scrolls) is active
3. **Mental model selector** — Quick-switch between thinking frameworks
4. **Pattern transparency** — "Polly learned X from you" cards in Today view
5. **Local-first** — All conversation history synced to `~/.polly/`, Obsidian-readable
6. **Custom personas** — Richer than Aight's agents (SOUL.md + domain context)
7. **Multi-provider** — Route individual messages to different AI providers
8. **No subscription ever** — Self-hosted, yours

---

## 11. Immediate Next Steps

1. **Build Polly Gateway** — Start with `polly/gateway/server.py` (FastAPI + WebSockets). This is the critical path item; nothing else can happen without it.

2. **Test with Aight first (transitional)** — Once Polly gateway speaks OpenClaw's WebSocket protocol, you can use Aight to connect to Polly-core instead of OpenClaw. This gives you mobile access immediately while building the native app.

3. **Set up Xcode project** — Swift + SwiftUI, minimum iOS 17, configure for personal TestFlight.

4. **Implement GatewayClient.swift** — The WebSocket connection layer is the app's foundation.

5. **Build ChatView with streaming** — Core use case first.

---

## 12. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| APNs requires $99/yr Apple Dev account | Certain | Budget for it; 1 device = TestFlight is worth it |
| WebSocket protocol reverse-engineering errors | Medium | Use Wireshark/proxyman to inspect Aight ↔ OpenClaw traffic |
| Polly RAG latency on mobile | Low | Polly runs on Mac; iPhone is just client |
| OpenClaw protocol changes | Low | Polly gateway is independent; not dependent on OpenClaw |
| Voice quality | Low | iOS native STT/TTS is excellent |

---

## 13. Resources

- **Polly codebase:** `~/polly/`
- **OpenClaw config:** `~/.openclaw/openclaw.json`
- **OpenClaw agent workspace pattern:** `~/.openclaw/workspace-*/`
- **Aight device registration:** `~/.openclaw/aight/devices.json`
- **OpenClaw gateway port:** 18789 (WebSocket)
- **FastAPI WebSockets docs:** https://fastapi.tiangolo.com/advanced/websockets/
- **APNs HTTP/2 API:** https://developer.apple.com/documentation/usernotifications
- **MarkdownUI (Swift):** https://github.com/gonzalezreal/swift-markdown-ui
- **APScheduler:** https://apscheduler.readthedocs.io/

---

**Research Status:** ✅ Complete  
**Recommended Next Phase:** Build `~/polly/gateway/` (Polly Gateway Python module)  
**Estimated Total Project:** 8-12 weeks for full Aight parity + Polly-exclusive features

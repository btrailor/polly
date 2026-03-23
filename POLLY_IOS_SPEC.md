# Polly iOS — Master Product Specification
**Version:** 0.1 (In Progress)  
**Created:** March 23, 2026  
**Status:** ✅ COMPLETE — all sections filled as of March 23, 2026  
**Leads:** @code_architect (overall), @frontend (UI), @design_eng (design system), @backend (protocol), @infra (connectivity), @security_audit (auth)

---

## Table of Contents
1. [Vision & Goals](#1-vision--goals)
2. [Architecture Overview](#2-architecture-overview)
3. [OpenClaw Protocol Spec](#3-openclaw-protocol-spec) ← @backend filling this in
4. [Screen Specifications](#4-screen-specifications)
5. [Design System](#5-design-system) ← @design_eng filling this in
6. [Component Library](#6-component-library) ← @frontend filling this in
7. [Connectivity & Networking](#7-connectivity--networking) ← @infra filling this in
8. [Security & Auth](#8-security--auth) ← @security_audit filling this in
9. [Voice System](#9-voice-system)
10. [Push Notifications](#10-push-notifications)
11. [Polly-Specific Features](#11-polly-specific-features)
12. [Tech Stack Decisions](#12-tech-stack-decisions)
13. [Phased Delivery Plan](#13-phased-delivery-plan)
14. [Open Questions](#14-open-questions)

---

## 1. Vision & Goals

### What Polly Is
Polly is a native iPhone app that serves as the primary mobile client for an OpenClaw gateway. It provides everything Aight provides — chat, Today view, shortcuts, settings — while adding Polly's unique attributes: RAG-aware chat, domain awareness, mental model selection, Obsidian vault integration, and a distinct design identity.

### Why It Exists
- Aight is in free beta. When it goes freemium, we need a self-hosted replacement.
- OpenClaw is open-source (MIT) and self-hosted — we own the backend forever.
- Polly brings additional intelligence layers on top of the standard OpenClaw client experience.
- Full ownership: no subscriptions, no platform lock-in, no data leaving your infrastructure.

### Non-Goals
- Polly does NOT replace OpenClaw — it wraps it
- Polly does NOT re-implement AI routing, session management, or the gateway
- Polly is NOT a general-purpose LLM app — it connects to *your* OpenClaw instance specifically
- No App Store distribution needed (TestFlight / personal sideload is fine)

### Success Criteria
- [ ] Can chat with any OpenClaw agent from iPhone
- [ ] Can join and participate in group chats
- [ ] Today view shows all active reminders/tasks/processes
- [ ] Shortcuts accessible with one tap
- [ ] Voice input and voice response work flawlessly
- [ ] Settings allow full gateway + provider configuration
- [ ] Works remotely via Cloudflare Tunnel (primary) and Tailscale (secondary)
- [ ] Push notifications fire for cron completions
- [ ] Indistinguishable from Aight in core functionality
- [ ] Noticeably better than Aight in Polly-specific features

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────┐
│              Polly iPhone App               │
│                                             │
│  ┌──────────┐  ┌────────┐  ┌────────────┐  │
│  │  Chat    │  │ Today  │  │ Shortcuts  │  │
│  │  View    │  │  View  │  │   View     │  │
│  └──────────┘  └────────┘  └────────────┘  │
│  ┌──────────┐  ┌────────┐  ┌────────────┐  │
│  │Moltbook  │  │ Stats  │  │ Settings   │  │
│  │  View    │  │  View  │  │   View     │  │
│  └──────────┘  └────────┘  └────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │         GatewayClient               │   │
│  │  WebSocket + Auth + Streaming       │   │
│  └──────────────────┬──────────────────┘   │
│                     │                      │
│  ┌──────────────────▼──────────────────┐   │
│  │         PollyEnhancement Layer      │   │
│  │  RAG context / Domain / Models      │   │
│  └─────────────────────────────────────┘   │
└─────────────────────┬───────────────────────┘
                      │ WebSocket
                      │ ws://[gateway]:18789
                      ▼
        ┌─────────────────────────┐
        │   OpenClaw Gateway      │
        │   (self-hosted, macOS)  │
        └────────────┬────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
    Agent Sessions         Cron / Items
    Skills / Tools         Memory / Moltbook
    Model Providers        Push Dispatch
```

### Key Principle
The GatewayClient is the only component that speaks directly to OpenClaw. Everything else in the app consumes its observable state. The PollyEnhancement Layer intercepts outgoing messages to inject RAG context, domain tags, and mental model overrides before they hit the gateway.

---

## 3. OpenClaw Protocol Spec

> ✅ **COMPLETE — sourced directly from `/opt/homebrew/lib/node_modules/openclaw/dist/auth-profiles-DRjqKE3G.js` and live session data.**
> Verified against `~/.openclaw/openclaw.json`, `~/.openclaw/aight/devices.json`, and live session stores.

---

### 3.1 Transport

| Property | Value |
|----------|-------|
| Default URL | `ws://[host]:18789` |
| Secure variant | `wss://[host]:18789` (with TLS fingerprint pinning) |
| Protocol version | `3` (minProtocol: 3, maxProtocol: 3) |
| Frame format | JSON text frames (newline-delimited) |
| Multiplexing | Single persistent connection, all RPCs correlated by `id` UUID |

---

### 3.2 Wire Frame Types

All messages over the WebSocket are JSON objects with a `type` discriminator. There are exactly **three frame types**:

#### REQUEST (client → server)
```json
{
  "type": "req",
  "id": "<uuid-v4>",
  "method": "<method-name>",
  "params": { }
}
```

#### RESPONSE (server → client)
```json
{
  "type": "res",
  "id": "<uuid-v4>",      // matches the originating request id
  "ok": true,
  "payload": { },         // present on success
  "error": {              // present on failure
    "code": "SOME_ERROR_CODE",
    "message": "human-readable message",
    "details": { }
  }
}
```

#### EVENT (server → client, server-push, no request required)
```json
{
  "type": "event",
  "event": "<event-name>",
  "payload": { },         // optional
  "seq": 42,              // monotonic integer, for gap detection
  "stateVersion": { }     // optional, opaque
}
```

**Implementation note:** Use the `seq` field to detect dropped events. If `seq > lastSeq + 1`, flag a potential missed event. This matters for streaming — a gap in the middle of a `delta` sequence could corrupt rendered output.

---

### 3.3 Connection & Auth Handshake

The handshake is **challenge-response**. Do NOT send anything until the server sends its challenge.

```
Polly Opens WebSocket
        │
        ▼
Server sends EVENT: "connect.challenge"
  { "event": "connect.challenge", "payload": { "nonce": "<random-string>" } }
        │
        ▼
Client sends REQUEST: method = "connect"
  (see params below)
        │
        ▼
Server sends RESPONSE to connect
  { "ok": true, "payload": { "status": "ok", "auth": { "deviceToken": "...", "role": "operator" } } }
        │
        ▼
Server begins sending EVENT: "tick"  (heartbeat, ~every 30s)
Connection is live.
```

#### `connect` params
```swift
struct ConnectParams: Encodable {
    let minProtocol: Int = 3
    let maxProtocol: Int = 3
    let client: ClientInfo
    let caps: [String]          // ["talk", "config"] — from real SDK source
    let auth: AuthInfo?
    let role: String            // "operator"
    let scopes: [String]        // ["operator.admin"] for full access
    let device: DeviceInfo?     // required for device-authenticated connections
}

struct ClientInfo: Encodable {
    let id: String = "openclaw-ios"
    let displayName: String = "Polly"
    let version: String         // app version string
    let platform: String = "ios"
    let deviceFamily: String    // "iphone" | "ipad"
    let mode: String = "ui"
    let instanceId: String?     // optional, stable per install
}

struct AuthInfo: Encodable {
    let token: String?          // static token from gateway.auth.token
    let deviceToken: String?    // rotated per-connect, stored in Keychain
    let bootstrapToken: String?
    let password: String?
}

struct DeviceInfo: Encodable {
    let id: String              // stable UUID per device
    let publicKey: String       // EC public key, raw base64url
    let signature: String       // see §3.3.1 Device Signature
    let signedAt: Int           // Date.now() ms at signing
    let nonce: String           // must match nonce from challenge
}
```

#### 3.3.1 Device Signature

> ✅ **Corrected from real `expo-openclaw-chat` source (`device-identity.ts`).**

The signature is an **Ed25519** signature (not EC/P-256 as originally specced) over a pipe-delimited payload string. The version prefix depends on whether a challenge nonce is present:

```
// With nonce (after connect.challenge):
payload = "v2|{deviceId}|{clientId}|{clientMode}|{role}|{scopes,csv}|{signedAtMs}|{authToken}|{nonce}"

// Without nonce (no challenge received):
payload = "v1|{deviceId}|{clientId}|{clientMode}|{role}|{scopes,csv}|{signedAtMs}|{authToken}"
```

Fields:
- `clientId` = `"openclaw-ios"`
- `clientMode` = `"ui"` (not `"webchat"`)
- `role` = `"operator"`
- `scopes` = `"operator.read,operator.write,operator.admin"` (comma-separated)
- `authToken` = the static token, or `""` if none
- `nonce` = from `connect.challenge` payload

**Key derivation:** `deviceId` = SHA-256 hex of Ed25519 public key bytes (not a UUID).

Sign with Ed25519 private key. Send base64url-encoded signature (not DER).

```typescript
// Real implementation from expo-openclaw-chat/core/device-identity.ts:
const payload = buildSignaturePayload({
  nonce: challengeNonce ?? undefined,  // "v2" path
  deviceId: identity.deviceId,
  clientId: "openclaw-ios",
  clientMode: "ui",
  role: "operator",
  scopes: ["operator.read", "operator.write", "operator.admin"],
  signedAtMs: Date.now(),
  authToken: token ?? "",
});
const signature = ed.sign(messageBytes, privateKeyBytes); // @noble/ed25519
// → base64url encode → send as device.signature
```

For **Swift/SwiftUI implementation**: use `CryptoKit.Curve25519.Signing` (Ed25519 is native in iOS 13+). `deviceId` = `SHA256.hash(data: publicKeyBytes).hexString`.

#### 3.3.2 Auth Token (simpler path)

For the current gateway config (`auth.mode: "token"`), Polly can skip device auth entirely and just send the static token:
```swift
AuthInfo(token: "d1b2469da551117e99b9e15907e373da45ea69e630d1f767c9ac4bc293c10e72")
```
This is the `gateway.auth.token` from `openclaw.json`. Store it in Keychain, not in code.

#### 3.3.3 deviceToken Rotation

After each successful `connect`, the server returns a fresh `deviceToken`. Store it:
- Keychain key: `com.polly.gateway.deviceToken`
- Use on next connect as `auth.deviceToken`
- If server returns `AUTH_DEVICE_TOKEN_MISMATCH` → clear Keychain token, fall back to static token

#### 3.3.4 Connection Lifecycle

| Event | Action |
|-------|--------|
| `tick` event received | Reset watchdog timer |
| No `tick` for 2× tick interval | Close and reconnect (exponential backoff: 1s, 2s, 4s, 8s, max 30s) |
| `connect.challenge` received mid-connection | Server restarted — re-handshake immediately |
| App foreground | Force reconnect if socket closed or stale |
| Network change (WiFi ↔ Cell) | Close + reconnect with new URL resolution |
| Connect fails (any reason) | If `autoReconnect=true`, do NOT reject the connect promise — schedule reconnect instead. Only reject if `autoReconnect=false`. |
| `NOT_PAIRED` response OR WS close code `1008` with "pairing" in reason | Enter pairing-wait state; don't reconnect until `device.pair.resolved` event arrives with `decision: "approved"` |

#### 3.3.5 Connect Error Codes

| Code | Meaning | Polly Action |
|------|---------|-------------|
| `AUTH_REQUIRED` | No auth provided | Show login/token entry UI |
| `AUTH_TOKEN_MISMATCH` | Wrong static token | Show "wrong token" error |
| `AUTH_DEVICE_TOKEN_MISMATCH` | Stale device token | Clear Keychain token, retry with static |
| `DEVICE_AUTH_SIGNATURE_EXPIRED` | `signedAt` too old | Re-sign with fresh timestamp |
| `DEVICE_AUTH_NONCE_MISMATCH` | Replayed nonce | Wait for new challenge |
| `PAIRING_REQUIRED` | Device not paired | Trigger device pair flow |

---

### 3.4 RPC Method Reference

Scope levels: **READ** → **WRITE** → **ADMIN** (each includes all below it).
Polly requests `scopes: ["operator.admin"]` on connect for full access.

#### READ Methods

| Method | Params | Returns | Notes |
|--------|--------|---------|-------|
| `sessions.list` | `{ limit?, activeMinutes?, agentId?, search?, includeDerivedTitles?, includeLastMessage? }` | `{ sessions: SessionEntry[], count, ts, path }` | Core for chat list |
| `sessions.get` | `{ key }` | `SessionEntry` | Single session detail |
| `sessions.usage` | `{ key?, startDate?, endDate?, mode? }` | Usage breakdown | Stats screen |
| `sessions.usage.timeseries` | `{ key?, startDate?, endDate? }` | Time-series usage | Charts |
| `chat.history` | `{ sessionKey, limit? }` | `{ messages: Message[] }` | Load conversation |
| `agents.list` | `{}` | `{ defaultId, mainKey, scope, agents: AgentSummary[] }` | Agent roster |
| `agent.identity.get` | `{ agentId?, sessionKey? }` | `{ agentId, name, emoji, avatar }` | Per-agent identity |
| `cron.list` | `{ includeDisabled?, limit?, query?, enabled?, sortBy? }` | `{ jobs: CronJob[] }` | Today view |
| `cron.status` | `{}` | Scheduler status | Today header |
| `cron.runs` | `{ jobId?, id?, limit?, statuses?, status? }` | `{ runs: CronRun[] }` | Run history |
| `models.list` | `{}` | Available models by provider | Settings |
| `usage.status` | `{}` | Provider usage windows | Stats screen |
| `usage.cost` | `{}` | Cost breakdown by model | Stats screen |
| `gateway.identity.get` | `{}` | Gateway name, version, instanceId | Settings header |
| `config.get` | `{}` | Full `openclaw.json` content | Settings |
| `health` | `{}` | Gateway health status | Connection indicator |
| `node.list` | `{}` | Connected nodes | Settings / advanced |
| `talk.config` | `{}` | TTS/voice config | Voice settings |
| `skills.status` | `{}` | Installed skills | Settings |

#### WRITE Methods

| Method | Params | Returns | Notes |
|--------|--------|---------|-------|
| `chat.send` | `ChatSendParams` | `{ status: "accepted", runId, sessionKey }` | Primary message send |
| `chat.abort` | `{ sessionKey, runId? }` | `{ ok: true }` | Cancel streaming reply |
| `agent` | `AgentParams` | `{ status: "accepted", runId, sessionKey }` | Lower-level agent dispatch (group chat) |
| `agent.wait` | `{ runId, timeoutMs? }` | `{ status: "done"\|"error"\|"timeout" }` | Await completion |
| `wake` | `{ mode: "now"\|"next-heartbeat", text }` | — | Inject system event |
| `sessions.patch` | `SessionsPatchParams` | `{ ok: true }` | Modify session settings |

#### ADMIN Methods

| Method | Params | Notes |
|--------|--------|-------|
| `cron.add` | `CronAddParams` | Create reminder/task (Today view) |
| `cron.update` | `{ id, patch: CronUpdatePatch }` | Edit cron job |
| `cron.remove` | `{ id }` | Delete cron job |
| `cron.run` | `{ id, mode?: "due"\|"force" }` | Trigger immediately |
| `agents.create` | `{ name, workspace, emoji?, avatar? }` | Create new agent |
| `agents.update` | `{ agentId, name?, workspace?, model?, avatar? }` | Edit agent |
| `agents.delete` | `{ agentId, deleteFiles? }` | Remove agent |
| `agents.files.list` | `{ agentId }` | List workspace files (Moltbook) |
| `agents.files.get` | `{ agentId, name }` | Read workspace file |
| `agents.files.set` | `{ agentId, name, content }` | Write workspace file |
| `sessions.reset` | `{ key, reason? }` | Clear session (`/new`, `/reset`) |
| `sessions.delete` | `{ key, deleteTranscript? }` | Remove session |
| `sessions.compact` | `{ key, maxLines? }` | Compact transcript |
| `chat.inject` | `{ sessionKey, message, label? }` | Inject system message |
| `config.set` | `{ raw, baseHash? }` | Write full config (dangerous) |
| `config.patch` | `{ patch, note?, restartDelayMs? }` | Partial config update (preferred) |

---

### 3.5 Sending a Chat Message

#### `ChatSendParams`
```swift
struct ChatSendParams: Encodable {
    let sessionKey: String      // e.g. "agent:the-strategist:main"
    let message: String         // user's text
    let idempotencyKey: String  // UUID, prevents duplicate sends on retry
    let timeoutMs: Int?         // 0 = fire-and-forget (use streaming events)
    let deliver: Bool?          // false for webchat (delivery handled by gateway)
    let thinking: String?       // "low"|"medium"|"high" for reasoning models
    let attachments: [Any]?
}
```

#### Response
```json
{
  "ok": true,
  "payload": {
    "status": "accepted",
    "runId": "<uuid>",
    "sessionKey": "agent:the-strategist:main"
  }
}
```

`status: "accepted"` means the agent run has started. The actual reply arrives via streaming `chat` events (§3.6). Keep the request pending until `expectFinal` is satisfied — but the gateway client handles this; Polly just subscribes to events.

---

### 3.6 Streaming Chat Events

> ✅ **Validated against `expo-openclaw-chat/chat/engine.ts`.** Key corrections from real source noted below.

After `chat.send` is accepted, the gateway pushes a sequence of `EVENT` frames with `event: "chat"`:

```typescript
// From protocol.ts (canonical)
interface ChatEventPayload {
  runId: string;
  sessionKey: string;
  seq?: number;
  state: string;           // "delta" | "final" | "complete" | "done" | "aborted" | "error"
  message?: ChatMessage;
  errorMessage?: string;
  usage?: ChatUsage;
  stopReason?: string;
}

interface ChatMessage {
  role: string;
  content: ChatMessageContent[] | string;  // always normalize to array
  usage?: ChatUsage;
  stopReason?: string;
}

interface ChatMessageContent {
  type?: string;           // "text" | "thinking" | "toolCall" | "toolResult" | "image" | "file"
  text?: string;
  thinking?: string;
  thinkingSignature?: string;
  source?: { type?: string; media_type?: string; data?: string };  // for images
  id?: string; name?: string; arguments?: unknown;                  // for toolCall
  data?: string;           // base64 image (transcript format)
}
```

**State values** — note the gateway sends multiple aliases for "complete":
- `"delta"` → streaming chunk in progress
- `"final"` / `"complete"` / `"done"` → run finished (treat all three identically)
- `"aborted"` → user cancelled
- `"error"` → failed, `errorMessage` has detail

**Streaming rendering — corrected from real `ChatEngine`:**
1. On `accepted` response → create streaming placeholder bubble keyed by `runId`
2. On `delta` → buffer update (do NOT update state on every delta — flush at **250ms intervals / 4Hz**)
3. On `final`/`complete`/`done` → flush immediately, replace bubble content with complete message
4. On `aborted` → flush, mark bubble complete (no error, just stopped)
5. On `error` → flush, mark bubble as error state, show `errorMessage`
6. **Silent reply filter**: if final text is exactly `"NO_REPLY"` or `"HEARTBEAT_OK"` (or truncated streaming prefixes thereof), suppress the bubble entirely — remove it from the message list

**Content block render order** (from `engine.ts`):
```tsx
const textContent  = message.content.find(c => c.type === "text")?.text ?? ""
const thinking     = message.content.find(c => c.type === "thinking")?.thinking
const hasImage     = message.content.some(c => c.type === "image")

// Render: ReasoningPanel? → MarkdownRenderer → ImageView?
```

Tool call/result blocks are stripped by `filterVisibleContent()` before display — they appear during streaming via `agent` events, not in the final message content array.

**Thinking/reasoning stream** (for extended thinking models):
```json
{
  "type": "event",
  "event": "chat",
  "payload": {
    "runId": "...",
    "state": "delta",
    "message": { "role": "assistant", "thinking": "Let me consider...", "content": "" }
  }
}
```
When `thinking` is populated and `content` is empty, render in the collapsible reasoning panel.

---

### 3.7 Session Keys

Session keys are structured strings that identify a specific conversation context:

| Pattern | Example | Used For |
|---------|---------|----------|
| `agent:<agentId>:main` | `agent:the-strategist:main` | Direct chat with an agent |
| `agent:<agentId>:group-chat:<groupId>` | `agent:backend-architect:group-chat:gc_1774068683485_otqwd5` | Per-agent session in a group chat |
| `agent:<agentId>:<threadId>` | `agent:the-strategist:thread:abc123` | Thread-scoped conversation |

**Group chat notes:**
- Each agent in a group chat has its OWN session key with a shared `groupId` suffix
- Group ID format: `gc_<timestamp>_<randomsuffix>`
- Polly creates a group by sending to multiple agents with the same `groupId` in `AgentParams`
- `chat.send` uses `sessionKey` for a specific agent; `agent` method uses `groupId` to fan out

**From live data** — all Aight sessions use:
```json
"deliveryContext": { "channel": "webchat" },
"lastChannel": "webchat",
"origin": { "label": "Aight", "provider": "webchat", "surface": "webchat", "chatType": "direct" }
```
Polly should use `label: "Polly"`, everything else identical.

---

### 3.8 `sessions.list` Response Shape

```swift
struct SessionsListResponse: Decodable {
    let sessions: [SessionEntry]
    let count: Int
    let ts: Int                  // server timestamp ms
    let path: String?            // store path (debug)
    let defaults: SessionDefaults?
}

struct SessionEntry: Decodable {
    let key: String              // session key (e.g. "agent:strategist:main")
    let sessionId: String?       // internal UUID
    let updatedAt: Int?          // last activity ms
    let chatType: String?        // "direct" | "group"
    let lastChannel: String?     // "webchat"
    let deliveryContext: DeliveryContext?
    let origin: SessionOrigin?
    let model: String?           // active model
    let modelProvider: String?
    let totalTokens: Int?
    let label: String?           // user-assigned label
    let derivedTitle: String?    // if includeDerivedTitles: true
    let lastMessagePreview: String? // if includeLastMessage: true
    let groupId: String?
    let spawnedBy: String?
}

struct SessionOrigin: Decodable {
    let label: String?           // "Aight" / "Polly"
    let provider: String?        // "webchat"
    let surface: String?         // "webchat"
    let chatType: String?        // "direct"
}
```

---

### 3.9 `agents.list` Response Shape

```swift
struct AgentsListResponse: Decodable {
    let defaultId: String        // e.g. "main"
    let mainKey: String          // default session key
    let scope: String            // "per-sender" | "global"
    let agents: [AgentSummary]
}

struct AgentSummary: Decodable {
    let id: String               // e.g. "the-strategist"
    let name: String?            // display name
    let identity: AgentIdentity?
}

struct AgentIdentity: Decodable {
    let name: String?
    let theme: String?           // color theme string
    let emoji: String?           // e.g. "🧠"
    let avatar: String?          // filename
    let avatarUrl: String?       // resolved URL
}
```

**Live agents on this gateway** (from `openclaw.json`):
```
main, team-lead, product-manager, code-architect, frontend-developer,
backend-architect, design-engineer, ux-designer, ux-researcher, growth-hacker,
social-media-manager, qa-engineer, security-auditor, infra-engineer, researcher,
strategist, ai-expert, data-analyst, ops-manager, writer, legal-advisor,
release-captain, code-reviewer, ceo, engineering-manager, retro-facilitator,
copywriter, image-creator, video-creator, podcast-producer, brand-strategist,
devops-engineer, performance-tester, api-tester, fitness-coach, wellness-guide,
chef, money-coach, accountability-coach, career-coach, travel-planner,
personal-shopper, parenting-coach
```

---

### 3.10 Cron / Today View

#### `cron.list` Response Shape

```swift
struct CronListResponse: Decodable {
    let jobs: [CronJob]
}

struct CronJob: Decodable {
    let id: String
    let name: String
    let description: String?
    let enabled: Bool
    let deleteAfterRun: Bool?
    let createdAtMs: Int
    let updatedAtMs: Int
    let schedule: CronSchedule
    let sessionTarget: String    // "main" | "isolated"
    let wakeMode: String         // "now" | "next-heartbeat"
    let payload: CronPayload
    let delivery: CronDelivery?
    let state: CronJobState
}

// Schedule variants
enum CronSchedule: Decodable {
    case at(at: String)                          // ISO 8601, one-shot
    case every(everyMs: Int, anchorMs: Int?)     // recurring interval
    case cron(expr: String, tz: String?)         // cron expression
}

struct CronPayload: Decodable {
    let kind: String             // "systemEvent" | "agentTurn"
    let text: String?            // for systemEvent
    let message: String?         // for agentTurn
    let model: String?           // for agentTurn
}

struct CronJobState: Decodable {
    let nextRunAtMs: Int?
    let runningAtMs: Int?        // non-nil = currently running
    let lastRunAtMs: Int?
    let lastRunStatus: String?   // "ok" | "error" | "timeout"
    let lastError: String?
    let lastDurationMs: Int?
    let consecutiveErrors: Int?
    let lastDelivered: Bool?
    let lastDeliveryStatus: String?
}
```

#### Today View Classification

Polly should classify cron jobs for Today view display:

| Classification | Criteria | Card Style |
|---------------|----------|------------|
| **Reminder** | `schedule.kind == "at"`, `deleteAfterRun == true` | Trigger card with time |
| **Recurring Task** | `schedule.kind == "every"\|"cron"` | Repeating badge |
| **Running Process** | `state.runningAtMs != nil` | Active spinner |
| **Overdue** | `state.nextRunAtMs < now && !running` | Orange warning |
| **Completed** | `lastRunStatus == "ok"`, `deleteAfterRun == true`, deleted | Greyed out |

#### Creating a Reminder (Today View "+" button)

```json
// REQUEST method: "cron.add"
{
  "name": "Call the dentist",
  "schedule": { "kind": "at", "at": "2026-03-24T14:00:00Z" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": { "kind": "systemEvent", "text": "Reminder: Call the dentist" },
  "deleteAfterRun": true
}
```

---

### 3.11 `chat.history` Response Shape

```swift
struct ChatHistoryResponse: Decodable {
    let messages: [Message]
}

struct Message: Decodable {
    let role: String             // "user" | "assistant" | "system" | "tool"
    let content: String?         // text content
    let thinking: String?        // reasoning (extended thinking models)
    let id: String?              // message ID
    let ts: Int?                 // timestamp ms
    let usage: UsageInfo?        // token counts
    let toolUse: [ToolUse]?      // tool calls (if caps includes "tool-events")
}
```

---

### 3.12 Usage / Stats APIs

#### `usage.status` — Provider quota windows

```swift
struct UsageStatusResponse: Decodable {
    let providers: [String: ProviderUsageSnapshot]
}

struct ProviderUsageSnapshot: Decodable {
    let error: String?
    let windows: [UsageWindow]
}

struct UsageWindow: Decodable {
    let label: String            // "Daily", "Monthly", etc.
    let used: Int                // tokens used
    let limit: Int?              // quota limit (nil = unlimited)
    let usedPercent: Float       // 0–100
    let resetsAtMs: Int?         // next reset timestamp
}
```

#### `sessions.usage` — Per-session cost breakdown

```swift
struct SessionUsageResponse: Decodable {
    let sessions: [SessionUsageEntry]
    let totals: UsageTotals?
}

struct SessionUsageEntry: Decodable {
    let key: String
    let agentId: String?
    let model: String?
    let modelProvider: String?
    let inputTokens: Int?
    let outputTokens: Int?
    let cacheRead: Int?
    let cacheWrite: Int?
    let totalTokens: Int?
    let cost: Float?
    let updatedAt: Int?
}
```

---

### 3.13 Config API (Settings Screen)

`config.get` returns the full `openclaw.json` structure. The fields Polly Settings cares about:

```swift
// Minimal config structure for Settings screen
struct GatewayConfig: Decodable {
    let gateway: GatewaySettings?
    let models: ModelsConfig?
    let agents: AgentsConfig?
    let channels: ChannelsConfig?
}

struct GatewaySettings: Decodable {
    let port: Int?               // default 18789
    let mode: String?            // "local" | "remote"
    let bind: String?            // "lan" | "localhost" | "all"
    let auth: GatewayAuth?
    let tailscale: TailscaleConfig?
}

struct GatewayAuth: Decodable {
    let mode: String             // "token" | "password" | "device"
    let token: String?
}

struct TailscaleConfig: Decodable {
    let mode: String             // "off" | "serve" | "funnel"
}
```

Write settings via `config.patch`:
```json
{
  "type": "req",
  "method": "config.patch",
  "params": {
    "raw": "{\"gateway\":{\"port\":18790}}",
    "note": "Updated from Polly iOS settings"
  }
}
```

⚠️ **Settings screen should treat `config.patch` as destructive** — show confirmation dialog. Consider read-only settings display for v1 with a "raw edit" escape hatch for power users.

---

### 3.14 Device Registration (Push Notifications)

Push is registered via **HTTP POST** (not WebSocket). From `~/.openclaw/aight/devices.json`:

```swift
// POST http://[gateway]:18789/api/aight/devices/register
struct DeviceRegistration: Encodable {
    let deviceId: String         // stable iOS UUID (stored in Keychain)
    let pushToken: String        // APNs device token hex string
    let platform: String = "ios"
    let sandbox: Bool            // true for development APNs, false for prod
}
// Response includes:
// { "sendKey": "<hmac-key>", "registeredAt": "<ISO-8601>" }
```

The `sendKey` is used to verify incoming push payloads — store in Keychain alongside `deviceId`.

**APNs payload from gateway:**
- Notification type: background + alert
- Triggered on cron completion, agent message delivery, system events
- On receive → open relevant session or Today view

---

### 3.15 Agents Files API (Moltbook)

Moltbook in Polly = the `agents.files.*` API — workspace markdown files.

```swift
// List files for an agent
// REQUEST method: "agents.files.list"
// params: { "agentId": "the-strategist" }
// Response:
struct AgentsFilesListResponse: Decodable {
    let agentId: String
    let workspace: String
    let files: [AgentFileEntry]
}

struct AgentFileEntry: Decodable {
    let name: String             // filename e.g. "MEMORY.md"
    let path: String             // full absolute path
    let missing: Bool
    let size: Int?
    let updatedAtMs: Int?
    let content: String?         // only if requested
}

// Standard workspace files present on all agents:
// MEMORY.md, SOUL.md, IDENTITY.md, BOOTSTRAP.md,
// AGENTS.md, TOOLS.md, USER.md, HEARTBEAT.md
```

---

### 3.16 Group Chat Protocol

Group chats in OpenClaw work as a **fan-out via shared groupId**:

1. **Group is identified by** a `groupId` string: `gc_<timestamp>_<randomsuffix>`
2. **Each agent maintains its own session** keyed as `agent:<agentId>:group-chat:<groupId>`
3. **Sending to a group** uses the `agent` method (not `chat.send`) with `groupId` set
4. **Routing**: The gateway fans the message out to all agents registered for that group
5. **Replies**: Each agent replies on its own session; events arrive tagged with the agent's `sessionKey`
6. **Activation modes**: Per-agent — `"mention"` (only reply when @mentioned) vs `"always"`

```swift
// Sending a message to a group chat
struct AgentParams: Encodable {
    let message: String
    let groupId: String          // "gc_1774068683485_otqwd5"
    let channel: String = "webchat"
    let idempotencyKey: String
    let label: String?           // group name e.g. "Home"
    // agentId omitted = fan out to all group members
}
```

**Polly group chat UI implications:**
- Subscribe to `chat` events from ALL agent session keys in the group
- Sort replies by `seq` / `ts` for correct ordering
- Show agent emoji + name prefix on each bubble
- `@mention` routing is handled by gateway — just include the @mention in the message text

---

### 3.17 Key Events Reference

| Event name | When fired | Payload |
|-----------|------------|---------|
| `connect.challenge` | Immediately on WS open | `{ nonce }` |
| `tick` | Every ~30s (heartbeat) | `{}` |
| `chat` | During/after agent run | `ChatEvent` (§3.6) |
| `sessions.updated` | Session state changed | `{ key, entry }` |
| `cron.updated` | Cron job state changed | `{ jobId, state }` |
| `cron.run.started` | Cron job began running | `{ jobId, runId }` |
| `cron.run.finished` | Cron job completed | `{ jobId, runId, status }` |
| `exec.approval.requested` | Exec command needs approval | approval details |
| `exec.approval.resolved` | Approval decision made | `{ id, decision }` |
| `node.event` | Connected node event | node-specific |
| `gateway.restarting` | Gateway about to restart | `{ reason? }` |

---

### 3.18 Scope Summary

| Scope | Key | Methods Covered |
|-------|-----|----------------|
| `operator.read` | All read-only queries | `sessions.list`, `agents.list`, `chat.history`, `cron.list`, `config.get`, `usage.*`, etc. |
| `operator.write` | Sending messages | `chat.send`, `chat.abort`, `agent`, `agent.wait`, `wake` |
| `operator.admin` | Full access | All of the above + `cron.add/update/remove/run`, `agents.*`, `sessions.patch/reset/delete`, `config.set/patch`, `chat.inject` |

**Polly should request `["operator.admin"]`** on connect. This gives full access needed for all screens including Settings and Today view management.

---

## 4. Screen Specifications

### 4.1 Chat View

**Purpose:** Primary interface. Chat with a single agent or a group.

**Layout:**
```
┌─────────────────────────────────────┐
│ [←]  🤖 Agent Name    [⋯]  [+group] │  ← Navigation bar
├─────────────────────────────────────┤
│                                     │
│        [message bubbles]            │
│                                     │
│   ┌─────────────────────────────┐   │
│   │ User message bubble         │   │
│   └─────────────────────────────┘   │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ 🤖 Agent streaming response... │ │
│ └─────────────────────────────────┘ │
│                                     │
├─────────────────────────────────────┤
│ [🎤] [Type a message...      ] [➤] │  ← Input bar
└─────────────────────────────────────┘
```

**States:**
- Idle (waiting for input)
- Sending (message in flight)
- Streaming (token-by-token response appearing)
- Tool call in progress (show tool name + spinner)
- Voice listening (waveform animation)
- Error (failed to send / gateway disconnected)

**Features:**
- Markdown rendering (bold, italic, code blocks, headers, lists)
- Syntax-highlighted code blocks
- Streaming text (characters appear progressively)
- Tool call visibility (collapsible "Thinking..." or "Searching..." block)
- Agent switcher (tap agent name → slide-up sheet with agent list)
- Long-press message → copy / quote / delete
- Pull to load history

**Polly Enhancements:**
- `/` in input → opens vault note picker (RAG context injection)
- Domain badge in nav bar (auto-detected from conversation)
- Mental model quick-select button in nav bar

---

### 4.2 Today View

**Purpose:** Dashboard of active items — reminders, tasks, background processes.

**Layout:**
```
┌─────────────────────────────────────┐
│  Today                    [+ Add]   │
├─────────────────────────────────────┤
│  ⏰ UPCOMING                        │
│  ┌───────────────────────────────┐  │
│  │ 🔔 Call dentist   2:00 PM     │  │  ← trigger
│  └───────────────────────────────┘  │
│                                     │
│  ✅ TASKS                           │
│  ┌───────────────────────────────┐  │
│  │ ☐ Draft Q2 proposal  [work]   │  │  ← item
│  │ ☐ Review PR #142     [code]   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ⚡ ACTIVE PROCESSES                │
│  ┌───────────────────────────────┐  │
│  │ ⟳ Research: Polly iOS spec    │  │  ← process
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Item Types:**
- `trigger` — time-based, shows scheduled time, fires once
- `item` — stateful task with labels, lifecycle management
- `process` — background agent run, shows progress

**Actions:**
- Swipe right → mark done
- Swipe left → cancel / delete
- Tap → expand detail + edit
- Long-press → quick actions sheet

**Polly Enhancements:**
- Pattern transparency cards: "💡 Polly noticed you usually..." 
- Domain-colored label chips

---

### 4.3 Shortcuts View

**Purpose:** Quick-access saved prompts.

**Layout:**
```
┌─────────────────────────────────────┐
│  Shortcuts                 [Edit]   │
├─────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐           │
│  │ 🌅      │  │ 📋      │           │
│  │ Morning │  │ Daily   │           │
│  │ Briefing│  │ Standup │           │
│  └─────────┘  └─────────┘           │
│  ┌─────────┐  ┌─────────┐           │
│  │ 🔍      │  │ ✍️      │           │
│  │ Research│  │ Draft   │           │
│  │  Mode   │  │  Email  │           │
│  └─────────┘  └─────────┘           │
└─────────────────────────────────────┘
```

**Features:**
- Grid layout (2-column)
- Tap → sends shortcut prompt to active agent
- Long-press → edit / delete / reorder
- Add new shortcut: name + emoji + prompt text
- The `shortcut:` JSON labeling protocol handled transparently (app sends label request, renders JSON silently)

---

### 4.4 Moltbook View

**Purpose:** Browse and interact with OpenClaw memory layer (MEMORY.md files per agent, knowledge base entries).

**Layout:**
```
┌─────────────────────────────────────┐
│  Moltbook               [🔍 Search] │
├─────────────────────────────────────┤
│  AGENTS                             │
│  ┌───────────────────────────────┐  │
│  │ 🖥️ Code Architect            >│  │
│  │ 🏗️ Backend Architect         >│  │
│  │ 🧠 AI Expert                 >│  │
│  └───────────────────────────────┘  │
│                                     │
│  GLOBAL MEMORY                      │
│  ┌───────────────────────────────┐  │
│  │ 📝 MEMORY.md (main)          >│  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Features:**
- View MEMORY.md per agent (rendered markdown)
- View global workspace memory
- Search across all memory
- Read-only initially; edit in v2

---

### 4.5 Usage Stats View

**Purpose:** Token usage, cost tracking, model breakdowns.

**Layout:**
```
┌─────────────────────────────────────┐
│  Usage                    [Period ▾]│
├─────────────────────────────────────┤
│  TODAY                              │
│  Tokens in:   142,300               │
│  Tokens out:   28,100               │
│  Est. cost:     $0.84               │
│                                     │
│  BY MODEL                           │
│  ██████████ claude-sonnet  68%      │
│  ████       gpt-4o         21%      │
│  ██         auto           11%      │
│                                     │
│  BY AGENT                           │
│  ████████ Code Architect   52%      │
│  ████     AI Expert        31%      │
│  ██       Backend          17%      │
└─────────────────────────────────────┘
```

---

### 4.6 Settings View

**Purpose:** Configure everything about the OpenClaw connection and Polly preferences.

**Sections:**

**Gateway**
- Gateway URL (e.g., `ws://[tailscale-ip]:18789`)
- Connection status indicator
- Re-pair / re-authenticate
- Test connection button

**Providers & Models**
- List configured providers (Anthropic, OpenAI, blockrun, Ollama, etc.)
- API key management (read from `openclaw.json` auth profiles)
- Default model selection
- Reasoning model toggle

**Agents**
- List all agents
- View agent SOUL.md
- Enable/disable agents
- Create new agent (shortcut to OpenClaw agent creation)

**Polly Features**
- RAG / vault path configuration
- Domain detection toggle
- Mental models default selection
- Pattern learning visibility toggle

**Notifications**
- Push notification enable/disable
- Per-agent notification preferences

**About**
- App version
- Gateway version
- OpenClaw version
- GitHub links

---

## 5. Design System

✅ **Complete — see `~/polly/DESIGN_SYSTEM_iOS.md` for full spec (@design_eng)**

### 5.1 Colors

**Accent (Polly Brand)**
```swift
static let accent     = Color(red: 0.941, green: 0.345, blue: 0.047) // #f0903b
static let accentDim  = Color(red: 0.784, green: 0.251, blue: 0.047) // #c84012
static let accentLight = Color(red: 1.0,  green: 0.978, blue: 0.933) // #fff7ed
```

**Backgrounds (Dark Mode — primary app experience)**
```swift
static let bgPrimary   = Color(red: 0.008, green: 0.015, blue: 0.043) // #020617
static let bgSecondary = Color(red: 0.047, green: 0.075, blue: 0.141) // #0c1323
static let bgBorder    = Color(red: 0.118, green: 0.165, blue: 0.282) // #1e2b48
```

**Text (Dark Mode)**
```swift
static let textPrimary   = Color(red: 0.973, green: 0.980, blue: 0.988) // #f8fafc
static let textSecondary = Color(red: 0.710, green: 0.757, blue: 0.808) // #b5c1ce
```

**Semantic**
```swift
static let success = Color(red: 0.086, green: 0.639, blue: 0.290) // #16a34a
static let error   = Color(red: 0.937, green: 0.267, blue: 0.267) // #ef4444
static let warning = Color(red: 0.920, green: 0.702, blue: 0.051) // #eab308
static let info    = Color(red: 0.145, green: 0.392, blue: 0.929) // #2563eb
```

**Domain Colors**
```swift
static let sigils  = Color(red: 0.145, green: 0.392, blue: 0.929) // #2563eb — Code (blue)
static let signals = Color(red: 0.678, green: 0.282, blue: 0.867) // #ad48dd — Audio (purple)
static let scrolls = Color(red: 0.086, green: 0.639, blue: 0.290) // #16a34a — Writing (green)
static let glyphs  = Color(red: 0.920, green: 0.702, blue: 0.051) // #eab308 — Design (gold)
static let grids   = Color(red: 0.086, green: 0.639, blue: 0.600) // #16a399 — Systems (teal)
```

**Dark mode is automatic** via `UIColor` trait collection adapters. See `DESIGN_SYSTEM_iOS.md §Color System` for full light/dark pairs.

### 5.2 Typography
- **Font:** System (SF Pro) — Dynamic Type, no custom font needed
- **Code:** `.system(.footnote, design: .monospaced)` — SF Mono
- **Scale:** Standard SwiftUI named styles (`.largeTitle` → `.caption2`)
- Respects user accessibility font size settings automatically

### 5.3 Spacing
- **Base unit:** 4pt
- `spacing1=4`, `spacing2=8`, `spacing3=12`, `spacing4=16`, `spacing6=24`, `spacing8=32`
- **Minimum touch target:** 44pt (Apple HIG)
- **List row height:** 56–72pt
- **Safe areas:** Always respected (notch, home indicator, Dynamic Island)

### 5.4 Key Design Rules
- Bottom tab bar for primary navigation (thumb-reachable)
- Swipe gestures for list actions (done, cancel, delete)
- Long-press for context menus (never right-click)
- Pull-to-refresh for all live data views
- Orange accent for all primary CTAs
- Status bar always visible (never hidden)
- Offline state always communicated — never silent failure

---

## 6. Component Library

✅ **Complete — updated for React Native + Expo stack (March 23, 2026)**  
**@frontend — March 23, 2026**

> **⚠️ Stack Update:** §12 now specifies React Native + Expo, not SwiftUI. All component signatures in this section have been updated accordingly. The state machines, interaction patterns, and design token references are unchanged — only the implementation language shifts from Swift to TypeScript/React Native.
>
> **Key source:** `expo-openclaw-chat@0.2.3` (public npm) provides `GatewayClient`, `ChatEngine`, and `protocol.ts` — Polly's gateway client layer is this package, not a from-scratch build. Component props below are typed against `UIMessage` and `ChatMessageContent[]` from that package.

Components live in `polly/src/components/`. All design tokens reference `DESIGN_SYSTEM_iOS.md`.

---

### 6.1 ChatBubble

**Purpose:** Render a single message in the chat feed — user or assistant, static or streaming.

**Maps to:** `UIMessage` from `expo-openclaw-chat` (`chat/engine.ts`), content blocks from `ChatMessageContent[]` (`core/protocol.ts`)

```tsx
interface ChatBubbleProps {
  message: UIMessage;           // from ChatEngine — includes content[], isStreaming, isError
  onRetry?: () => void;         // called when user taps Retry on error state
  onLongPress?: () => void;     // context menu trigger
}

// UIMessage shape (from expo-openclaw-chat):
// {
//   id: string
//   role: "user" | "assistant" | "system"
//   content: ChatMessageContent[]   // array of typed blocks
//   isStreaming: boolean
//   isError: boolean
//   errorMessage?: string
//   runId?: string
//   usage?: ChatUsage
//   timestamp?: number
// }
```

**Content block rendering** — `content` is `ChatMessageContent[]`, not a string. Render by block type:

```tsx
// Extract from content blocks:
const textBlock = message.content.find(c => c.type === "text")
const thinkingBlock = message.content.find(c => c.type === "thinking")
const imageBlocks = message.content.filter(c => c.type === "image")

// Render order: ReasoningPanel → MarkdownRenderer → ImageView(s)
const textContent = textBlock?.text ?? ""
const thinkingContent = thinkingBlock?.thinking
```

> **Important:** `isSilentReply()` filtering (suppressing `NO_REPLY`, `HEARTBEAT_OK`) is handled by `ChatEngine` before `UIMessage` reaches this component. No need to handle silents in the bubble.

**Streaming flush rate:** `ChatEngine` buffers at `STREAM_FLUSH_MS = 250ms` (4Hz). The bubble does NOT re-render per token — it re-renders at 4Hz via `ChatEngine.on("update")`. The `StreamingCursor` animates independently of this.

**Visual spec:**

| Property | User | Assistant |
|----------|------|-----------|
| Alignment | Right | Left |
| Bubble color (dark) | `#f0903b` (accent) | `#0c1323` (bgSecondary) |
| Bubble color (light) | `#f0903b` (accent) | `#e4f0f0` (bgSecondary) |
| Text color | White | textPrimary |
| Max width | 80% screen width | 88% screen width |
| Corner radius | 18pt (all), 4pt bottom-right | 18pt (all), 4pt bottom-left |
| Padding | 12pt H, 10pt V | 12pt H, 10pt V |

**State variants** (driven by `UIMessage` fields, not a separate enum):
- **`isStreaming: true`** — `MarkdownRenderer` renders `textContent` so far, `StreamingCursor` blinks at end. Bubble expands at 4Hz flush rate.
- **`isStreaming: false, isError: false`** — Full `MarkdownRenderer` output. No cursor. Usage footer shown if `usage != null`.
- **`isStreaming: false` (run aborted)** — Content freezes. Append a dim `" ∎"` symbol after last token. No cursor. (Detected via `ChatEngine.on("update")` after `chat.abort`.)
- **`isError: true`** — Bubble shows red error row: `⚠ [errorMessage]` with a Retry button. Call `onRetry` on tap. Haptic: error notification.

**Thinking panel** (when `thinkingContent != null`):
```tsx
<ReasoningPanel
  content={thinkingContent}
  isStreaming={message.isStreaming}
  // auto-collapses when isStreaming transitions false
/>
```

**Usage footer** (shown when `!isStreaming && usage != null`, assistant only):
- `usage.input` + `usage.output` tokens in caption style, faint color
- Cost if `usage.cost?.total` is present

**Long-press context menu:**
```tsx
// Copy plain text from textContent
// Quote Reply → onLongPress()
```

**Accessibility:**
```tsx
accessibilityLabel={`${message.role === "user" ? "You" : "Assistant"}: ${textContent}`}
accessibilityHint={message.timestamp ? `Sent at ${formatTime(message.timestamp)}` : undefined}
```

---

### 6.2 StreamingCursor

**Purpose:** Blinking cursor appended to streaming text. Animates independently of the 4Hz `ChatEngine` flush.

```tsx
// Simple Animated component — not tied to flush rate
const StreamingCursor: React.FC = () => {
  const opacity = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 0, duration: 500, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 1, duration: 500, useNativeDriver: true }),
      ])
    ).start();
  }, []);

  return (
    <Animated.Text style={{ opacity, color: colors.textPrimary }}>▌</Animated.Text>
  );
};
```

- Blink interval: 500ms
- Color matches bubble text color
- Conditionally rendered: `{message.isStreaming && <StreamingCursor />}`

---

### 6.3 MarkdownRenderer

**Purpose:** Render markdown string to styled React Native view. Used inside `ChatBubble`, Moltbook file viewer.

**Library:** `react-native-enriched-markdown` — already in Aight's stack, battle-tested against OpenClaw output.

```tsx
import EnrichedMarkdown from 'react-native-enriched-markdown';

interface PollyMarkdownProps {
  content: string;           // plain text extracted from textContent block
  isStreaming?: boolean;     // disables link taps while streaming
}

const PollyMarkdown: React.FC<PollyMarkdownProps> = ({ content, isStreaming }) => (
  <EnrichedMarkdown
    content={content}
    theme={pollyMarkdownTheme}
    onLinkPress={isStreaming ? undefined : handleLinkPress}
    selectable={!isStreaming}
  />
);
```

**Theme tokens** (from `DESIGN_SYSTEM_iOS.md`):
- Body text: `textPrimary`
- Headings: semibold, scaled (H1: 22, H2: 18, H3: 16)
- Inline code: monospace, 13pt, `bgBorder` background
- Code blocks: → `CodeBlock` component (§6.4)
- Links: `primary600` blue, tappable
- Blockquote: subtle bg, left border accent

**Supported inline:** bold, italic, inline code, links, strikethrough  
**Supported blocks:** H1–H3, code blocks (→ §6.4), ordered/unordered lists, blockquotes  
**v1 deferral:** tables → plain text fallback

---

### 6.4 CodeBlock

**Purpose:** Syntax-highlighted, copyable code block. Used inside `MarkdownRenderer` and standalone in message views.

```swift
struct CodeBlock: View {
    let language: String?      // "swift", "python", "json", nil
    let content: String
    @State private var copied = false
}
```

**Visual spec:**
- Background: `bgSecondary` (#0c1323 dark / #e4f0f0 light)
- Corner radius: 12pt
- Padding: 16pt H, 12pt V
- Font: `.system(.footnote, design: .monospaced)` (SF Mono)
- Text color: `textPrimary`

**Language badge** (top-left):
```swift
Text(language?.uppercased() ?? "CODE")
    .font(.caption2)
    .fontWeight(.medium)
    .foregroundColor(.secondary)
    .padding(.horizontal, 8)
    .padding(.vertical, 4)
    .background(.ultraThinMaterial)
    .cornerRadius(6)
```

**Copy button** (top-right):
```swift
Button {
    UIPasteboard.general.string = content
    copied = true
    DispatchQueue.main.asyncAfter(deadline: .now() + 2) { copied = false }
} label: {
    Image(systemName: copied ? "checkmark" : "doc.on.doc")
        .foregroundColor(copied ? .success : .secondary)
}
```

**Horizontal scroll for long lines:**
```swift
ScrollView(.horizontal, showsIndicators: false) {
    Text(content)
        .font(.system(.footnote, design: .monospaced))
        .fixedSize(horizontal: true, vertical: false)
}
### 6.4 CodeBlock

**Purpose:** Syntax-highlighted, copyable code block. Used inside `MarkdownRenderer` and standalone in message views.

```tsx
interface CodeBlockProps {
  language?: string;    // "python", "json", "bash", nil
  content: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ language, content }) => {
  const [copied, setCopied] = useState(false);
  // copy → Clipboard.setString(content), show checkmark 2s
};
```

**Visual spec:**
- Background: `bgSecondary` (dark `#0c1323` / light `#e4f0f0`)
- Corner radius: 12pt, Padding: 16pt H / 12pt V
- Font: monospace, 13pt (SF Mono on iOS via `fontFamily: 'Courier'` or system monospace)
- Language badge top-left: small pill, `.ultraThinMaterial` bg
- Copy button top-right: clipboard icon → checkmark on tap, resets after 2s
- Horizontal scroll for long lines: `ScrollView` horizontal

**Syntax highlighting:** v1 = monospace only. v2 = `Highlightr` or equivalent.

---

### 6.5 ToolCallBlock

**Purpose:** Visualize tool calls during an agent run. Surfaced via `agent` events (§3.17).

**Maps to:** `AgentEventPayload` from `expo-openclaw-chat`, `exec.approval.requested` gateway event

```tsx
type ToolCallStatus =
  | { kind: 'running' }
  | { kind: 'complete' }
  | { kind: 'error'; message: string }
  | { kind: 'awaitingApproval' };

interface ToolCallBlockProps {
  toolName: string;
  status: ToolCallStatus;
  summary?: string;           // e.g. "Searched: polly iOS"
  inputPreview?: string;      // first 120 chars of params JSON
  outputPreview?: string;     // first 120 chars of result
  isExpanded: boolean;
  onToggle: () => void;
  onApprove?: () => void;     // awaitingApproval only
  onDeny?: () => void;
}
```

**Collapsed view** (default):
- Status icon left: spinner (running) | ✓ (complete) | ✗ (error) | ⚠️ (approval)
- Tool label text: see mapping table below
- Chevron right, rotates 90° when expanded
- Tap anywhere → `onToggle()`
- Background: `bgBorder` at 30% opacity, 8pt corner radius

**Expanded view:**
- `inputPreview` and `outputPreview` in monospaced footnote
- "View full" button if truncated

**Approval state:**
```tsx
<View style={{ flexDirection: 'row', gap: 8 }}>
  <Button title="Deny" onPress={onDeny} destructive />
  <Button title="Approve" onPress={onApprove} primary />
</View>
```

**Tool → label mapping:**

| Tool | Collapsed label |
|------|----------------|
| `web_search` | "Searching: [query]..." |
| `web_fetch` | "Reading: [url]..." |
| `read` / `write` | "Read file" / "Wrote file" |
| `exec` | "Ran command" (or "Awaiting approval") |
| `memory_search` | "Searching memory..." |
| `cron` | "Updating schedule..." |
| anything else | `toolName` |

---

### 6.6 ReasoningPanel

**Purpose:** Collapsible "thinking" panel for extended reasoning models.

**Maps to:** `ChatMessageContent` block with `type: "thinking"` — `thinkingBlock.thinking` string

```tsx
interface ReasoningPanelProps {
  content: string;
  isStreaming: boolean;   // auto-collapses when transitions false
}

const ReasoningPanel: React.FC<ReasoningPanelProps> = ({ content, isStreaming }) => {
  const [expanded, setExpanded] = useState(isStreaming);
  useEffect(() => { if (!isStreaming) setExpanded(false); }, [isStreaming]);
  // ...
};
```

**Visual:**
- Collapsed: `🧠 Thinking... [chevron]` — dim, footnote, italic
- Expanded: scrollable monospaced footnote text, secondary color
- Appears above `MarkdownRenderer` content in the bubble
- Spring animation on expand/collapse
- Auto-collapses when `isStreaming` transitions `true → false`
- User can re-expand any time

---

### 6.7 VoiceButton

**Purpose:** Mic button in the chat input bar.

```tsx
type VoiceMode = 'idle' | 'listening' | 'processing' | 'buffering' | 'speaking';

interface VoiceButtonProps {
  mode: VoiceMode;
  onPress: () => void;
}
```

**Visual spec (56pt circle):**

| State | Fill | Icon | Animation |
|-------|------|------|-----------|
| `idle` | `bgBorder` | mic icon | none |
| `listening` | `#f0903b` accent | waveform bars (Skia) | bars animate up/down |
| `processing` | `#f0903b` dim | spinner | rotate |
| `buffering` | `#2563eb` dim | hourglass/waveform | pulse — ElevenLabs audio loading |
| `speaking` | `#2563eb` primary | speaker icon | pulse |

**Waveform animation** (listening — uses `@shopify/react-native-skia`):
- 3 vertical bars, 4pt wide, staggered Reanimated timing
- Bar heights animate between 8–24pt, 400ms easeInOut, 150ms stagger per bar

**Haptics** (via `expo-haptics`):
- Start listening: `ImpactFeedbackStyle.Light`
- Stop: `ImpactFeedbackStyle.Medium`
- Error: `NotificationFeedbackType.Error`

**Accessibility:**
```tsx
accessibilityLabel={mode === 'idle' ? 'Record voice message' : 'Stop recording'}
accessibilityHint="Double-tap to start or stop recording"
```

---

### 6.8 ChatInputBar

**Purpose:** Sticky bottom input bar. Composes text entry, voice button, send button.

```tsx
interface ChatInputBarProps {
  value: string;
  onChange: (text: string) => void;
  onSend: () => void;
  onVoiceTranscript: (transcript: string) => void;
  disabled?: boolean;           // true when offline or agent running
  placeholder?: string;         // default: "Message..."
}
```

**Layout:**
```
┌─────────────────────────────────────────────┐
│  [🎤]  [  Message...              ]  [  ➤ ] │
└─────────────────────────────────────────────┘
```

- Background: system background (auto dark/light)
- Top border: 0.5pt separator
- `VoiceButton` (§6.7): 40pt, left
- `TextInput`: flexible, 16pt H pad, `bgSecondary` bg, 22pt border radius, multiline max 5 lines
- Send button: 32pt, `accent` when text non-empty, `secondary` when empty/disabled
- Bottom safe area inset handled by parent — use `useSafeAreaInsets().bottom`

---

### 6.9 AgentHeader

**Purpose:** Navigation bar content for a chat screen.

```tsx
interface AgentHeaderProps {
  agent: AgentSummary;           // from agents.list (§3.9)
  connectionStatus: ConnectionState;
  onTapAgent: () => void;        // opens agent switcher
  onMenu: () => void;
}
```

**Layout:** `[←]   🧠  The Strategist   [●]   [⋯]`

- `AgentAvatar` (§6.11), 32pt, tappable
- Agent name, headline weight, centered
- `ConnectionDot` (§6.12) right of name
- `⋯` → action sheet: New session | View memory | Reset | Copy session key

**Group chat variant:** `[←]   👥 Home — 9 agents   [●]   [⋯]`

---

### 6.10 AgentSwitcherSheet

**Purpose:** Bottom sheet to switch between agents or group chats.

```tsx
interface AgentSwitcherSheetProps {
  agents: AgentSummary[];
  sessions: SessionEntry[];       // from expo-openclaw-chat protocol.ts
  currentAgentId: string;
  onSelect: (agent: AgentSummary) => void;
  onSelectSession: (session: SessionEntry) => void;
  onDismiss: () => void;
}
```

Standard RN bottom sheet (`@gorhom/bottom-sheet` or Expo modal):
- Search bar at top
- "Recent" section — sessions by `updatedAt`
- "All Agents" section — full roster, emoji + name
- "Group Chats" section — sessions where `origin.chatType === "group"`

---

### 6.11 AgentAvatar

**Purpose:** Emoji-in-circle avatar for an agent.

```tsx
interface AgentAvatarProps {
  emoji: string;
  size: 32 | 40 | 56;            // pt
  showOnlineIndicator?: boolean;
}
```

- Circle: `bgBorder` fill
- Emoji centered, fontSize = size × 0.55
- Online indicator: 10pt green circle, bottom-right, white ring border

---

### 6.12 ConnectionDot

**Purpose:** Minimal connection status indicator in nav bar.

```tsx
type ConnectionDotStatus = 'connected' | 'reconnecting' | 'disconnected' | 'error';

interface ConnectionDotProps {
  status: ConnectionDotStatus;
  onPress?: () => void;           // opens ConnectionDetailSheet
}
```

| Status | Color | Animation |
|--------|-------|-----------|
| `connected` | success green | none |
| `reconnecting` | `#f0903b` | pulse, 1s loop |
| `disconnected` | secondary gray | none |
| `error` | error red | none |

8pt circle. Maps directly from `GatewayClient.connectionState` (`ConnectionState` from `expo-openclaw-chat`).

---

### 6.13 TodayItemCard

**Purpose:** Single item in Today view — trigger, task, or running process.

**Maps to:** `CronJob` shape from `cron.list` (§3.10)

```tsx
interface TodayItemCardProps {
  job: CronJob;
  onMarkDone: () => void;     // cron.remove
  onTap: () => void;
  onRunNow: () => void;       // cron.run
  onAbort?: () => void;       // running jobs only
}
```

**Visual spec:**
- Height: 72pt min, `bgSecondary` bg, 12pt corner radius, 16pt H / 12pt V padding

**Layout:**
```
[●] [Title                          ] [Time]
    [badge] [subtitle preview...]
```

**Status dot (10pt left):**
- One-shot trigger: `#f0903b` orange
- Recurring: `#2563eb` blue
- Running: green animated pulse
- Overdue: error red
- Done: secondary gray

**Swipe actions** (via `react-native-gesture-handler`):
- Swipe right → Done (green, `onMarkDone`)
- Swipe left → Delete (red, destructive) | Run Now (orange, `onRunNow`)
- Running variant: swipe left → Abort only

---

### 6.14 TodaySectionHeader

```tsx
interface TodaySectionHeaderProps {
  title: string;      // "UPCOMING" | "TASKS" | "ACTIVE PROCESSES"
  count: number;
  icon: string;       // SF Symbol name (rendered via @expo/vector-icons or SF Symbols)
}
```

- Caption weight, secondary color, all-caps
- Icon + count pill right-aligned
- 16pt top / 8pt bottom padding

---

### 6.15 AddReminderSheet

**Purpose:** Create a new cron-backed reminder or task.

```tsx
interface AddReminderSheetProps {
  visible: boolean;
  onDismiss: () => void;
  onSubmit: (params: CronAddParams) => Promise<void>;
}
```

**Fields:**
1. **Name** — `TextInput`, required
2. **Type** — `SegmentedControl`: Reminder | Recurring | Agent Turn
3. **When** (Reminder): `DateTimePicker`, future only
4. **Recurrence** (Recurring): picker — Daily | Weekly | Custom interval
5. **Message** (Agent Turn): `TextInput` → `payload.message`
6. **Target** — toggle: Main session | Isolated

**On submit → `cron.add`** with `deleteAfterRun: type === 'reminder'`

---

### 6.16 ShortcutCard

**Purpose:** 2-column grid cell in Shortcuts view.

```tsx
interface Shortcut {
  id: string;
  name: string;
  emoji: string;
  prompt: string;
}

interface ShortcutCardProps {
  shortcut: Shortcut;
  isLoading: boolean;
  onPress: () => void;
  onLongPress: () => void;    // edit/delete context menu
}
```

**Visual spec:**
- `bgSecondary` bg, 16pt corner radius, 16pt all-side padding
- Emoji: 32pt top-left
- Name: footnote semibold, bottom-left, max 2 lines
- Loading: orange `ActivityIndicator` overlay, 0.5 opacity on content
- Press feedback: `useAnimatedStyle` scale 0.95 → 1.0, 100ms

**Long-press:** context menu — Edit | (divider) | Delete (destructive)

**Storage:** `AsyncStorage` or `MMKV` client-side only — not gateway-backed.

---

### 6.17 MoltbookFileRow

```tsx
interface AgentFileEntry {
  name: string;
  sizeBytes?: number;
  updatedAtMs?: number;
}

interface MoltbookFileRowProps {
  file: AgentFileEntry;
  onPress: () => void;
}
```

- Icon by filename: `MEMORY.md` → brain, `SOUL.md` → sparkles, `*.md` → doc
- Filename: headline weight; size: caption secondary
- `updatedAtMs` → relative time ("3 days ago")
- Chevron right

---

### 6.18 UsageBar

```tsx
interface UsageBarProps {
  label: string;
  value: number;        // 0.0–1.0
  valueLabel: string;   // "68%"
  tint: string;         // hex color
}
```

- Full width, 8pt height, 4pt corner radius
- Track: `bgBorder`; fill: `tint`
- Label left, value right, both caption style

---

### 6.19 ConnectionDetailSheet

```tsx
interface ConnectionDetailSheetProps {
  visible: boolean;
  onDismiss: () => void;
  connectionState: ConnectionState;   // from expo-openclaw-chat
  activeUrl: string;
  activeVia: 'local' | 'tailscale' | 'cloudflare';
  latencyMs?: number;
  lastConnectedAt?: Date;
  onReconnect: () => void;
  onOpenSettings: () => void;
}
```

**Displays:** path label, active URL, latency, last connected time, Reconnect button (orange primary), Open Settings link.

---

### 6.20 GroupChatBubbleRow

**Purpose:** Message row in a group chat — `ChatBubble` with agent attribution header. **Phase 2.**

```tsx
interface GroupChatBubbleRowProps {
  agent: AgentSummary;
  message: UIMessage;          // from expo-openclaw-chat ChatEngine
}
```

**Layout:**
```
🧠  The Strategist         [timestamp]
  ┌────────────────────────────────┐
  │  Message content here...      │
  └────────────────────────────────┘
```

- Attribution row: `AgentAvatar` 32pt + name (footnote semibold, agent theme color) + timestamp (caption2 secondary)
- Bubble always left-aligned (all agents are "left")
- User's own messages: right-aligned, no attribution header

---

### 6.23 IntegrationCard

**Purpose:** Single row in the Integrations screen (§15.5). Shows connection status, account label for OAuth integrations, and routes to the integration detail/config sheet.

**Maps to:** §15.5 integration registry shape

```tsx
interface IntegrationCardProps {
  id: string;
  name: string;
  icon: string;                  // emoji or image source (URI string)
  status: 'connected' | 'configured' | 'available' | 'coming_soon';
  connectedAccount?: string;     // e.g. "user@gmail.com" — OAuth integrations only
  onPress: () => void;           // disabled when status === 'coming_soon'
}
```

**Visual spec — 4 status states:**

| Status | Left indicator | Right content | Interaction |
|--------|---------------|---------------|-------------|
| `connected` | 10pt green dot | Account label (caption, secondary) | Tappable → manage sheet |
| `configured` | 10pt orange dot | "Active" label (caption, accent) | Tappable → manage sheet |
| `available` | none | Chevron right | Tappable → setup sheet |
| `coming_soon` | none | "Coming Soon" pill (dim) | Disabled, no tap |

**Layout:**
```
[icon]  [Name                    ]  [● account@…  /  Active  /  ›  /  Coming Soon]
```

- Row height: 64pt
- Icon: 36pt, rounded corners 8pt (emoji in circle or image)
- Name: `.body` weight, `textPrimary`
- Background: `bgSecondary`, corner radius 12pt
- `coming_soon`: entire row at 0.45 opacity, `pointerEvents: 'none'`

**Connected state detail:**
```tsx
// Green dot + account email truncated to 1 line
<View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
  <View style={styles.greenDot} />
  <Text style={styles.accountLabel} numberOfLines={1}>
    {connectedAccount}
  </Text>
</View>
```

**Configured state detail** (API key integrations — ElevenLabs, Brave, etc.):
```tsx
<Text style={{ color: colors.accent, fontSize: 12 }}>Active</Text>
```

**Accessibility:**
```tsx
accessibilityLabel={`${name} integration, ${statusLabel}`}
accessibilityHint={status === 'coming_soon' ? 'Not yet available' : 'Double-tap to configure'}
accessibilityState={{ disabled: status === 'coming_soon' }}
```

**Usage in Integrations screen:**
```tsx
// Section: "Connected" (status === 'connected' | 'configured')
// Section: "Available" (status === 'available')
// Section: "Coming Soon" (status === 'coming_soon')
// Each section uses TodaySectionHeader (§6.14) for the label
<IntegrationCard
  id="elevenlabs"
  name="ElevenLabs"
  icon="🎙️"
  status={elevenLabsKey ? 'configured' : 'available'}
  onPress={() => openSheet('elevenlabs')}
/>
```

Canonical mapping of protocol states → component + visual state. Implementation reference.

| Protocol state | Component | Visual state |
|---------------|-----------|-------------|
| `ChatEventPayload.state === "delta"` | `ChatBubble` | `isStreaming: true` — cursor active, 4Hz re-render |
| `ChatEventPayload.state === "final"/"complete"/"done"` | `ChatBubble` | `isStreaming: false` — cursor gone, usage shown |
| `ChatEventPayload.state === "aborted"` | `ChatBubble` | `isStreaming: false` — frozen, ∎ appended |
| `ChatEventPayload.state === "error"` | `ChatBubble` | `isError: true` — red row, retry button |
| `isSilentReply(content) === true` | `ChatBubble` | Not rendered — filtered by `ChatEngine` |
| `CronJob.state.runningAtMs != null` | `TodayItemCard` | Running — spinner, elapsed counter |
| `CronJob.state.nextRunAtMs < Date.now()` | `TodayItemCard` | Overdue — red dot, "Overdue" label |
| `CronJob.schedule.kind === "at"` | `TodayItemCard` | Trigger — orange dot, formatted time |
| `GatewayClient.connectionState === "reconnecting"` | `ConnectionDot` | Orange pulsing dot |
| `exec.approval.requested` event | `ToolCallBlock` | `status.kind === 'awaitingApproval'` — inline approve/deny |
| `ChatMessageContent.type === "thinking"` (streaming) | `ReasoningPanel` | Expanded, live text |
| `ChatMessageContent.type === "thinking"` (final) | `ReasoningPanel` | Auto-collapsed |

---

### 6.22 Accessibility Baseline (All Components)

Per @design_eng — baked in, not retrofitted.

**Every interactive component must have:**
```tsx
accessibilityLabel="..."        // what it is
accessibilityHint="..."         // what happens on tap
accessibilityValue="..."        // current state if stateful
accessible={true}
```

**Touch targets:** All tappable elements minimum 44×44pt — use `minWidth: 44, minHeight: 44` in style, or `hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}` on small icons.

**Dynamic Type:** All text uses named style constants from `DESIGN_SYSTEM_iOS.md` — never hardcoded `fontSize`. Use `allowFontScaling={true}` (default in RN) everywhere.

**Color independence:** Status never communicated by color alone — always icon or text label alongside color.

**Screen reader actions:** `ChatBubble` copy, `TodayItemCard` swipe actions, `ShortcutCard` long-press — all exposed via `accessibilityActions` and `onAccessibilityAction` so VoiceOver users don't need gestures.

---

## 7. Connectivity & Networking

> ✅ **@infra** — documented March 23, 2026

---

### 7.1 Overview — Multi-Path Architecture

Polly must work in three network contexts:

| Context | Transport | Gateway Address | When Used |
|---|---|---|---|
| Home (local network) | Direct LAN | `ws://[lan-ip]:18789` | On home WiFi |
| Remote (Tailscale) | WireGuard VPN | `ws://[tailscale-ip]:18789` | Personal network, open WiFi |
| Remote (Cloudflare Tunnel) | HTTPS/WSS via CF | `wss://[subdomain].trycloudflare.com` | Work networks, restricted environments |

The app persists **all three addresses** in Settings and attempts them in priority order. No STUN/relay required — all traffic terminates at the gateway's WebSocket. Cloudflare Tunnel is the current real-world remote path and must be a first-class supported option.

> **Real-world note:** Cloudflare Tunnel is the primary remote access method in use today. Many corporate networks block VPN clients (including Tailscale/WireGuard) but permit HTTPS — Cloudflare Tunnel works anywhere a browser works.

---

### 7.2 Local Network (Home)

**How it works:**
- Gateway binds to `0.0.0.0:18789` with `"bind": "lan"` (already configured in `openclaw.json`)
- Polly connects to a user-configured LAN address (e.g. `192.168.1.X:18789`)
- WebSocket stays open persistently; gateway sends SSE-style delta frames over it
- No NAT traversal needed — iPhone and gateway are on the same network

**Discovery (optional, Phase 2):**
- Gateway broadcasts a `_openclaw._tcp` mDNS/Bonjour service on startup
- Polly uses `NWBrowser` to scan for `_openclaw._tcp.local` — if found, auto-fills the LAN address
- User can always override with a manual IP in Settings
- mDNS is LAN-only — never used for remote connections

**Requirements:**
- Local Network permission entitlement (`NSLocalNetworkUsageDescription`) required in Info.plist
- Bonjour service types must be declared in `NSBonjourServices`
- iOS will prompt user for Local Network access on first LAN attempt — this is expected

---

### 7.3 Remote Access — Tailscale

**Why Tailscale:**
- Zero-config WireGuard-based mesh VPN
- The gateway Mac already has Tailscale installed (or can — trivial `brew install tailscale`)
- iPhone gets a stable `100.x.x.x` Tailscale IP regardless of where it is
- No port forwarding, no DDNS, no exposed public IP required
- End-to-end encrypted at the WireGuard layer
- **Best for:** personal networks, home WiFi away, open public WiFi

**Setup requirements (one-time):**
1. Install Tailscale on the gateway Mac, join the user's tailnet
2. Note the gateway's Tailscale IP (stable, rarely changes)
3. Install Tailscale iOS app on iPhone, join the same tailnet
4. Enter Tailscale IP + port in Polly Settings → Gateway → Remote (Tailscale)

**Current gateway config:**
```json
"tailscale": { "mode": "off", "resetOnExit": false }
```
> Note: `mode: "off"` means the gateway doesn't *require* Tailscale on its side — it just listens on all interfaces. Tailscale is handled at the OS network layer, not the gateway layer. No changes needed to `openclaw.json`.

**Tailscale iOS SDK (future option):**
- Tailscale offers a Swift/iOS library that embeds WireGuard directly in the app
- Would remove the requirement for the user to have the Tailscale iOS app installed separately
- Significant complexity — defer to Phase 3

---

### 7.4 Remote Access — Cloudflare Tunnel ⭐ Primary Remote Path

**Why Cloudflare Tunnel:**
- Pure outbound HTTPS — works on **any network including corporate/work environments** that block VPN clients
- No inbound firewall rules needed on the gateway Mac
- No VPN client required on iPhone — just a WSS URL
- Cloudflare terminates TLS with a valid cert — no self-signed cert issues
- Free tier covers personal use easily
- **This is the current real-world remote access method in use today**

**How it works:**
```
Polly iPhone
    │ WSS (HTTPS/443)
    ▼
Cloudflare Edge (global PoP)
    │ Encrypted tunnel (outbound from Mac)
    ▼
cloudflared daemon (running on gateway Mac)
    │ localhost
    ▼
OpenClaw Gateway (ws://127.0.0.1:18789)
```

**Setup requirements (one-time):**
1. Install `cloudflared` on the gateway Mac:
   ```bash
   brew install cloudflare/cloudflare/cloudflared
   ```
2. Create a named tunnel (persistent URL):
   ```bash
   cloudflared tunnel login
   cloudflared tunnel create polly-gateway
   cloudflared tunnel route dns polly-gateway gateway.yourdomain.com
   ```
   Or use a quick ephemeral tunnel (URL changes on restart — not ideal):
   ```bash
   cloudflared tunnel --url http://localhost:18789
   ```
3. Configure the tunnel to proxy WebSocket traffic to the OpenClaw port:
   ```yaml
   # ~/.cloudflared/config.yml
   tunnel: <tunnel-id>
   credentials-file: ~/.cloudflared/<tunnel-id>.json
   ingress:
     - hostname: gateway.yourdomain.com
       service: http://localhost:18789
       originRequest:
         noTLSVerify: false
     - service: http_status:404
   ```
4. Run as a macOS launch daemon (auto-start):
   ```bash
   sudo cloudflared service install
   sudo launchctl start com.cloudflare.cloudflared
   ```
5. Enter the tunnel URL in Polly Settings → Gateway → Remote (Cloudflare): `wss://gateway.yourdomain.com`

**WebSocket compatibility:**
- Cloudflare fully supports WebSocket proxying — no special config needed beyond the ingress rule above
- The gateway's existing WebSocket server (`ws://localhost:18789`) works transparently behind the tunnel
- Polly connects using `wss://` (TLS handled by Cloudflare); gateway sees `ws://` on localhost

**In-app configuration UI (Settings → Gateway → Remote Access):**
```
Remote Access
─────────────────────────────────
  Method      [Tailscale ▾] [Cloudflare ▾] [None]

  [Cloudflare selected]
  Tunnel URL   [wss://gateway.yourdomain.com    ]
  Status       🟢 Connected via Cloudflare Tunnel

  [Tailscale selected]
  Tailscale IP [100.x.x.x                       ]
  Port         [18789                            ]
  Status       ⚫ Tailscale not active
─────────────────────────────────
  [Test Connection]
```

**Cloudflare Tunnel vs Tailscale — when to use which:**

| Scenario | Recommended |
|----------|-------------|
| Work network (VPN blocked) | ✅ Cloudflare Tunnel |
| Personal phone on public WiFi | Either |
| Maximum security / no CF dependency | Tailscale |
| Home away (hotel, airport) | Either |
| Corporate network with DLP/MITM proxy | Cloudflare Tunnel (HTTPS looks like web traffic) |

**Security note for @security_audit:**
- Cloudflare Tunnel URL is effectively a credential — it should be stored in Keychain, not UserDefaults
- Named tunnels with a custom domain are preferred over ephemeral `trycloudflare.com` URLs (stable, revocable)
- Cloudflare sees the tunnel hostname but traffic inside the WebSocket is encrypted at the application layer (gateway auth still applies)
- Access policy can be added via Cloudflare Zero Trust to require authentication before reaching the tunnel — optional hardening

---

### 7.5 Connection Discovery & Switching

**GatewayConnectionManager** — the central connectivity state machine:

```
States:
  .disconnected
  .connecting(via: .local | .tailscale | .cloudflare)
  .connected(via: .local | .tailscale | .cloudflare, latencyMs: Int)
  .reconnecting(attempt: Int)
  .offline

Transitions:
  app foreground      → try local → if fail, try preferred remote (CF or Tailscale) → .offline
  network change      → recheck active path, switch if needed
  WebSocket close     → .reconnecting → exponential backoff
  app background      → suspend WebSocket (iOS kills long-lived background TCP)
  app foreground      → reconnect immediately
```

**Path selection algorithm:**
1. Try LAN address first (lowest latency, no tunnel overhead)
2. If LAN fails within **2 seconds**, try the user's configured remote path (Cloudflare or Tailscale) in parallel
3. Whichever connects first wins — cancel the other
4. Record which path succeeded; prefer it on next launch
5. If both fail → `.offline` mode
6. User can also force a specific path from Settings (useful when on work network where Tailscale is blocked)

**Network path monitoring:**
- Use `NWPathMonitor` to watch for interface changes (WiFi ↔ cellular)
- On path change, re-evaluate: if home WiFi just came up, try switching to LAN
- Emit `gatewayPathChanged` event to UI — show "Reconnected via [Local/Cloudflare/Tailscale]" toast

---

### 7.6 Reconnection Strategy

**Exponential backoff schedule:**

| Attempt | Delay |
|---|---|
| 1 | immediate |
| 2 | 1s |
| 3 | 2s |
| 4 | 5s |
| 5+ | 15s (cap) |

**Rules:**
- Max 5 background reconnect attempts before giving up and showing "Gateway unreachable"
- Foreground tap on the connection status bar → immediate reconnect attempt
- On app foreground (from background): always attempt reconnect immediately, ignore backoff
- On successful reconnect: re-subscribe to all active sessions (send `session/load` for current agent)

**WebSocket keep-alive:**
- Send a ping frame every **30 seconds** when connected
- If no pong within 5 seconds → treat as disconnect, start reconnect
- iOS suspends background network activity; pings are only sent when app is active

---

### 7.7 Offline Mode

When gateway is unreachable, Polly degrades gracefully:

| Feature | Offline Behavior |
|---|---|
| Chat | Shows "Gateway offline" banner; input disabled |
| Today view | Shows last-cached items (read-only) |
| Shortcuts | List visible, tap shows "Cannot send — offline" |
| Settings | Fully available |
| Voice input | STT still works (on-device); just can't send |

**Local cache:**
- Today items (triggers, tasks, processes) cached to CoreData on every fetch
- Last-known agent list cached to UserDefaults
- Chat history: last 100 messages per session cached to CoreData
- Cache TTL: 24 hours

---

### 7.8 APNs Push Infrastructure

**The problem:** iOS kills WebSocket connections when app is backgrounded. Push is the only reliable way to wake the app for notifications.

**Flow:**

```
OpenClaw Gateway
      │
      │ (cron fires / trigger fires / agent completes)
      │
      ▼
Push Dispatch Module (in gateway)
      │ HTTP/2 POST to api.push.apple.com
      │ Auth: JWT signed with APNs private key (.p8)
      │ Payload: { aps: { alert, sound }, data: { itemId, sessionKey, type } }
      ▼
Apple APNs
      │
      ▼
Polly iOS (wakes from background)
      │
      ├─ UNNotificationServiceExtension: decrypt/enrich payload
      └─ On tap → deep link to relevant screen (Today item, session, etc.)
```

**What Polly must provide to gateway during registration:**
```json
{
  "apnsToken": "<device APNs token hex>",
  "deviceId": "<stable UUID stored in Keychain>",
  "sendKey": "<auth token>",
  "bundleId": "com.yourname.polly",
  "environment": "production" | "sandbox"
}
```

**Gateway side (OpenClaw):**
- Already has a push dispatch mechanism (Aight uses it)
- Requires: APNs `.p8` key file, Key ID, Team ID configured in `openclaw.json`
- `devices.json` stores registered devices — Polly registers to the same file

**Apple Developer requirements:**
- Apple Developer Program enrollment ($99/yr) — **required**, no way around it for APNs
- Provisioning profile with `aps-environment` entitlement
- APNs Auth Key (`.p8`) generated at developer.apple.com → Keys
- Background mode: `remote-notification` in Info.plist

**APNs payload structure (recommendation for gateway):**
```json
{
  "aps": {
    "alert": {
      "title": "Research complete",
      "body": "Your web research task has finished."
    },
    "sound": "default",
    "badge": 1,
    "content-available": 1
  },
  "polly": {
    "type": "cron_complete" | "trigger_fired" | "process_done" | "mention",
    "sessionKey": "agent-session-key",
    "itemId": "item-slug-or-id",
    "agentEmoji": "🔬",
    "agentName": "Researcher"
  }
}
```

**Notification Service Extension:**
- A separate app target that intercepts notifications before display
- Can enrich content, download media, decrypt payloads
- Required if we want notification attachments or end-to-end encrypted payloads
- Shares a Keychain group with main app to access `sendKey`

**Silent push (background refresh):**
- `content-available: 1` with no `alert` → wakes app in background to sync Today items
- Use sparingly (Apple rate-limits silent pushes heavily)
- Primary use: sync Today view cache when cron fires, so data is ready when user opens app

---

### 7.9 Configuration (Settings Schema)

```swift
struct GatewayConfig: Codable {
    var localAddress: String            // e.g. "192.168.1.42:18789"
    
    // Remote path 1: Cloudflare Tunnel (primary remote — works on corporate networks)
    var cloudflareUrl: String           // e.g. "wss://gateway.yourdomain.com"
    var cloudflareEnabled: Bool         // default: true if URL is set
    
    // Remote path 2: Tailscale (secondary remote — for unrestricted networks)
    var tailscaleAddress: String        // e.g. "100.x.x.x:18789"
    var tailscaleEnabled: Bool          // default: false until configured
    
    // Path preferences
    var preferredRemotePath: RemotePath // .cloudflare | .tailscale | .auto
    var preferLocal: Bool               // default: true
    var connectionTimeout: Int          // seconds, default: 2
    
    // Stored in Keychain — never in this struct on disk
    // var authToken: String
    // var deviceId: String
    // var cloudflareUrl (if sensitive): store in Keychain alternative
}

enum RemotePath: String, Codable {
    case cloudflare
    case tailscale
    case auto   // try both, use whichever connects first
}
```

---

### 7.10 Open Infra Questions

1. **TLS for local:** Should LAN connections use self-signed TLS? iOS will reject self-signed certs by default — needs a custom `URLSessionDelegate` with cert pinning or a local CA. Recommend: skip TLS on LAN (traffic is local), TLS required for Tailscale connections.
2. **Tailscale iOS SDK vs. standalone app:** Ship with standalone app dependency for Phase 1; revisit embedded SDK in Phase 3.
3. **mDNS auto-discovery:** Phase 2 feature — don't block Phase 1 on it.
4. **Push key management:** The APNs `.p8` key lives on the gateway Mac. User must configure path in `openclaw.json`. Gateway team (@backend) owns this config surface.

---

## 8. Security & Auth

> ✅ **Completed by @security_audit** — based on live audit of OpenClaw source (`aight-utils`, `device-bootstrap`, `auth-profiles`, gateway `device-auth`)

---

### 8.1 Device Identity & Gateway WebSocket Auth

OpenClaw uses **Ed25519 asymmetric keypairs** for gateway authentication. Polly iOS must replicate this faithfully.

#### How it works in OpenClaw (reference implementation)
1. On first launch, generate an Ed25519 keypair. Derive `deviceId = SHA-256(publicKeyPEM)` (hex).
2. On WS connect, gateway issues a challenge. Client signs `{ challenge, timestamp }` with private key → sends `{ id: deviceId, publicKey: base64url(rawPublicKey), signature }`.
3. Gateway verifies signature with `verifyDeviceSignature`. On success, issues an opaque `deviceToken` (bearer).
4. Subsequent connects send `deviceToken` as a WS header — skips signature round-trip.
5. On `1008 Device Token Mismatch`, clear cached token and re-challenge from keypair.

#### Polly iOS Implementation Requirements

> **Stack update (2026-03-23):** Stack is React Native + Expo. Swift `SecKey` / Secure Enclave APIs are replaced by `@noble/ed25519` + `expo-secure-store`. Security posture is equivalent for personal use — see note below.

- **Keypair generation:** Use `@noble/ed25519` to generate an Ed25519 keypair. Store private key bytes via `expo-secure-store` with key `"polly.device.privateKey"`. This maps to iOS Keychain internally with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` — hardware-backed but not Secure Enclave-bound (acceptable for personal use; see tradeoff note below).
- **`deviceId`:** Derive as `SHA-256(publicKeyBytes)` using `@noble/hashes/sha256`, output as hex. Matches Aight's derivation via `fingerprintPublicKey()` — confirmed by source audit.
- **Signing:** Use `@noble/ed25519`'s `sign(message, privateKey)`. Same algorithm as gateway's `verifyDeviceSignature` — no ECDSA/P-256 workaround needed. Algorithm is confirmed Ed25519 end-to-end.
- **`deviceToken` cache:** Store via `expo-secure-store` with key `"polly.device.token"`. Never in `AsyncStorage`, MMKV, or any unencrypted store. Apply a **7-day TTL** — refresh on each successful connect. (OpenClaw currently has no TTL — ⚠️ see hardening note below.)
- **No keypair in plaintext:** Private key must never appear in logs, Sentry reports, or Metro bundler output. Wrap all key operations in `try/catch` and log errors only — never log the key material itself.

> **Secure Enclave tradeoff note:** `expo-secure-store` uses iOS Keychain (hardware-encrypted) but keys are not bound to Secure Enclave, meaning a process with root/jailbreak access could theoretically extract them. For a personal gateway client this is the same threat surface as every major password manager on the App Store. If Secure Enclave binding becomes a requirement in future (e.g. enterprise use), the migration path is to implement a native Expo module using `SecKeyCreateRandomKey` with `kSecAttrTokenIDSecureEnclave` — the `DeviceIdentityProvider` abstraction in `expo-openclaw-chat` makes this a drop-in replacement.

---

### 8.2 Push Notification Auth (`sendKey`)

Push auth uses a relay-based HMAC scheme. The relay holds a `masterSecret`; `sendKey = HMAC-SHA256(masterSecret, pushToken)`. The relay is stateless — it recomputes and verifies on every `/send` call.

#### Registration Flow
```
Polly App → aight.push.register(deviceId, apnsToken, platform: "ios", sandbox: bool)
         → Gateway calls relay POST /register { token: apnsToken }
         → Relay returns { sendKey }
         → Gateway stores { deviceId, apnsToken, sendKey } 
```

#### ⚠️ Known Vulnerability in OpenClaw — Must Fix in Polly
**`aight.push.register` is currently unauthenticated.** Any client that can reach the gateway WS can register arbitrary push tokens under any `deviceId`.

**Polly fix (required before production):**
- The registration RPC must validate that the caller's authenticated session `deviceId` matches the `deviceId` parameter. Gateway should derive it from the WS session, not trust the client-supplied value.
- Until the gateway-side fix ships, the iOS client should at minimum verify that the `deviceId` it sends matches its own locally-derived identity.

#### `sendKey` Storage — Critical
`sendKey` **must never be stored in plaintext.** OpenClaw stores it in `~/.openclaw/aight/devices.json` in cleartext — this is a known issue. On React Native/Expo:
- Store `sendKey` via `expo-secure-store` with key `"polly.push.sendKey.{deviceId}"`.
- Never write to `AsyncStorage`, MMKV, or any unencrypted store.
- On unregister: call `SecureStore.deleteItemAsync("polly.push.sendKey.{deviceId}")` to purge.

#### APNs Token Handling
- APNs `pushToken` is not secret (Apple knows it) but should not be logged or sent to third parties.
- Re-register via `expo-notifications` `addPushTokenListener` when token changes.
- On registration failure: surface in Settings, degrade gracefully (app works without push).

---

### 8.3 Transport Security

#### Local Network (Home / Tailscale)
- All gateway connections: **WSS (TLS 1.2+)**. Never fall back to `ws://` even on LAN.
- Exception: explicit dev mode only, with a visible warning UI.
- Tailscale provides end-to-end encryption at network layer (WireGuard). Even so, TLS must be maintained — defense in depth.
- **Certificate handling for self-signed / local certs:** Gateway may present a self-signed cert on LAN. Options:
  - Option A: User installs gateway CA cert via Settings profile (highest security, most friction).
  - Option B: Pin to a known gateway fingerprint stored in Keychain after first verified connection ("trust on first use", TOFU). Display fingerprint in Settings for manual verification.
  - Option C: Allow self-signed on `.local` / Tailscale IP ranges only, with explicit user acknowledgment.
  - **Recommendation: Option B (TOFU) for v1**, with Option A upgrade path documented.
- ATS (App Transport Security): configure `NSExceptionDomains` in `app.json` / `Info.plist` for the gateway host only if using self-signed cert. Never set `NSAllowsArbitraryLoads = true`.

#### Remote / Away-from-home
- Traffic routes over Tailscale VPN — WireGuard-encrypted at transport layer.
- Same TLS requirement applies to the WSS connection inside the tunnel.
- No direct internet exposure of gateway required.

#### Push Relay
- Polly iOS never calls the push relay directly. All relay calls are gateway-to-relay (server-side).
- Relay URL should be `https://` only; gateway config must enforce this.

---

### 8.4 Data at Rest

| Data | Storage | Encryption |
|------|---------|------------|
| Ed25519 private key | `expo-secure-store` (`"polly.device.privateKey"`) | iOS Keychain (hardware-backed, not Secure Enclave) |
| `deviceToken` (bearer) | `expo-secure-store` (`"polly.device.token"`) | iOS Keychain |
| `sendKey` | `expo-secure-store` (`"polly.push.sendKey.{deviceId}"`) | iOS Keychain |
| APNs push token | `expo-secure-store` | iOS Keychain |
| Gateway TLS fingerprint (TOFU) | `expo-secure-store` | iOS Keychain |
| **Cloudflare Tunnel URL** | **`expo-secure-store`** | **iOS Keychain** |
| **Tailscale gateway address** | **`expo-secure-store`** | **iOS Keychain** |
| Session messages / transcripts | None — not cached on device in v1 | N/A |
| User preferences (non-sensitive) | UserDefaults — gateway host label, UI prefs only | Standard iOS encryption |
| API keys / secrets | Never stored on device — all stay on gateway | N/A |

**No sensitive credential ever touches `UserDefaults`, `NSUserDefaults`, or flat files.**

> **Cloudflare Tunnel URL storage note:** The tunnel URL (e.g. `wss://gateway.yourdomain.com`) is functionally a credential — anyone with it can reach your gateway. It must live in Keychain. The `GatewayConfig` struct in code may hold it in memory during an active session, but the persistence layer must write it to Keychain only, never to a plist or UserDefaults. The "gateway host label" (e.g. "My Home Gateway") shown in UI is non-sensitive and can live in UserDefaults.

---

### 8.5 Threat Model

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|-----------|
| Attacker on local network intercepts WS | Medium | High | TLS (WSS) required; TOFU cert pinning |
| Stolen device — access to `expo-secure-store` items | Low | High | `expo-secure-store` maps to `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`; requires device unlock; no iCloud backup |
| Malicious app reads `expo-secure-store` | Low | High | Keychain access groups scoped to Polly bundle ID only; RN bridge doesn't expose other apps' store |
| Relay MITM swaps `sendKey` | Low | Medium | Future: mTLS on gateway→relay; for now, HTTPS + relay domain pinning |
| Phishing via push notification | Medium | Medium | Notifications never contain sensitive data; deep links require re-auth |
| Gateway compromise (local machine) | Low | Critical | Out of scope for iOS client — gateway security is user's responsibility |
| Unauthenticated push registration (C1) | Medium | Medium | Fix: bind registration to authenticated session `deviceId` |
| `deviceToken` replay after expiry | Low | High | Implement 7-day TTL + rotation |
| Jailbroken device — Keychain bypass | Low | Critical | Accept risk; document in security policy; consider biometric re-auth for sensitive ops |
| Cloudflare Tunnel URL leaked (UserDefaults, logs, backup) | Medium | High | Store in Keychain only; scrub from all log output; exclude from iCloud backup |
| Cloudflare Tunnel URL enumeration / brute force | Low | High | Use named tunnels on custom domain (not `trycloudflare.com`); optionally gate with Cloudflare Zero Trust access policy (email/identity required to reach tunnel) |
| Corporate network DLP inspects WS traffic | Medium | Low | CF Tunnel over HTTPS looks like normal web traffic; gateway auth still encrypted end-to-end inside WS |
| Cloudflare-side breach exposes tunnel hostname | Very Low | Medium | Gateway auth layer (Ed25519 device auth) is independent of CF — attacker with tunnel URL still can't auth to gateway without valid `deviceToken` |

---

### 8.6 Required Hardening Before Production (Priority Order)

**🔴 Must-fix before any public release:**
1. **C1 — Auth-gate push registration:** Gateway must validate `deviceId` matches authenticated session. Polly iOS client enforces same-identity check client-side as belt-and-suspenders.
2. **C2 — sendKey in `expo-secure-store` only:** Never write `sendKey` to `AsyncStorage`, MMKV, or disk. RN implementation correct by design; ensure no debug/Sentry logging leaks key material.

**🟠 Must-fix before v1.0:**
3. **M3 — deviceToken TTL:** Implement 7-day rolling TTL. Refresh on connect, revoke on sign-out.
4. **M2 — Device registration cap:** Max 10 registered devices. Show device list in Settings with remove option.
5. **M1 — Bootstrap token expiry:** Enforce `expiresAtMs` check independent of file-load prune timing.
6. **OTA security policy (`expo-updates`):** OTA updates bypass App Store review — this is a supply chain risk if the EAS build pipeline is compromised. Required controls:
   - Use **Expo EAS code signing** — sign all OTA bundles; client verifies signature before applying.
   - OTA updates must **never touch auth/Keychain logic** without a full App Store release cycle (native modules can't be OTA'd anyway, but JS-layer auth code can be).
   - Pin `expo-openclaw-chat` at a specific version (`0.2.2`); treat any upgrade as a security review item — it sits in the auth + WS critical path.
   - Document a rollback procedure: if a bad OTA ships, `expo-updates` supports channel rollback via EAS dashboard.

**🟡 Post-v1 / hardening sprints:**
7. **L2 — Relay cert pinning:** Add certificate pinning for gateway→relay HTTPS channel.
8. Biometric re-auth gate (`expo-local-authentication`) for agent config changes and device management.
9. Background session encryption (clear in-memory session buffer on app background).
10. **Secure Enclave upgrade path:** If enterprise use becomes a requirement, implement a native Expo module using `SecKeyCreateRandomKey` with `kSecAttrTokenIDSecureEnclave` — `DeviceIdentityProvider` abstraction makes this a drop-in swap.

---

### 8.7 Auth UX Requirements

- **Pairing screen:** Display `deviceId` (first 8 chars) and gateway URL for user to verify. Show TLS fingerprint if TOFU.
- **Device management in Settings:** List registered devices with name, `deviceId` prefix, registration date. Allow removal.
- **Token expiry handling:** Silent re-auth on `deviceToken` expiry — user should never see an auth error during normal use.
- **`expo-secure-store` loss (device restore):** If secure store is wiped (new device, restore from backup to new hardware), detect missing keys on launch → full re-pair flow.
- **Sign-out:** Call `SecureStore.deleteItemAsync` for all keys (`sendKey`, `deviceToken`, `privateKey`, tunnel URLs) and call `aight.push.unregister`.

---

## 9. Voice System

**Implementation:** 100% client-side iOS native. No audio ever hits the gateway.

### 9.1 Speech-to-Text
- Framework: `Speech` (SFSpeechRecognizer)
- On-device model (iOS 17+ supports on-device STT)
- Tap-to-talk: tap mic → record → tap again or silence detection → send
- Continuous mode: optional, for hands-free use
- Language: auto-detect from system locale

### 9.2 Text-to-Speech
- Framework: `AVFoundation` (AVSpeechSynthesizer)
- Reads AI responses aloud when voice mode is active
- Respects silent switch
- Pause/resume on interruption (phone call, etc.)
- Voice selection: system voices available

### 9.3 Voice Mode States
```
OFF → [tap mic] → LISTENING → [tap or silence] → PROCESSING → SPEAKING → OFF
                                                              ↑
                                              (reads AI response aloud)
```

### 9.4 VoiceButton Visual States
- Default: mic icon, inactive
- Listening: animated waveform, orange accent
- Processing: spinner
- Speaking: speaker icon, animated bars

---

## 10. Push Notifications

### 10.1 Registration Flow
1. App requests notification permission on first launch
2. iOS provides APNs token
3. App sends token + `deviceId` + `sendKey` to gateway registration endpoint
4. Gateway stores in `~/.openclaw/aight/devices.json` (same file Aight uses)
5. OpenClaw's existing push dispatch works transparently

### 10.2 Notification Types
- **Cron completion** — isolated agent turn finished (e.g., "Research task complete")
- **Reminder trigger** — `trigger` item fires at `scheduledFor` time
- **Process completion** — background process finished
- **Mention** — agent mentioned you in a group chat (future)

### 10.3 Notification Payload
✅ Documented in §7.7 — see "APNs payload structure" there for the full JSON shape. Summary:
- `aps.alert.title/body` — human-readable notification text
- `polly.type` — `cron_complete | trigger_fired | process_done | mention`
- `polly.sessionKey` — which session to deep-link into
- `polly.itemId` — which Today item to highlight
- `polly.agentEmoji` + `polly.agentName` — for attribution in notification UI

### 10.4 Requirements
- Apple Developer Program ($99/yr) — required for APNs
- App must be signed with push notification entitlement
- Background modes: remote-notifications

---

## 11. Polly-Specific Features

These differentiate Polly from being a straight Aight clone.

### 11.1 RAG Context Injection
**Trigger:** User types `/` in chat input  
**Behavior:** Slide-up sheet shows Obsidian vault file browser → select note → note content prepended to message as context  
**Implementation:** Polly reads vault path from settings, displays file tree, reads selected note, wraps in context block before sending to gateway

### 11.2 Domain Awareness
**Behavior:** Polly detects which of the 5 domains (Sigils/Signals/Scrolls/Glyphs/Grids) is active based on conversation content and shows a colored domain badge in the chat nav bar  
**Implementation:** Simple keyword classification on recent messages; domain colors from design system

### 11.3 Mental Model Selector
**Trigger:** Tap 🧠 icon in chat nav bar  
**Behavior:** Sheet shows list of mental models (Infinite Games, Systems Thinking, etc.), tap to activate → injected as system context on next message  
**Implementation:** Prepend model description to outgoing message context

### 11.4 Pattern Transparency (Today View)
**Behavior:** "Polly noticed..." insight cards in Today view showing learned patterns from conversation history  
**Implementation:** Parse Polly's `~/.polly/patterns/` (from existing core) and surface as readable cards

### 11.5 Vault Browser
**Trigger:** Tap vault icon in Moltbook or Settings  
**Behavior:** Browse Obsidian vault directory structure, view notes rendered as markdown  
**Implementation:** Read from configured vault path (local access via Tailscale file share or vault path on device if synced)

---

## 12. Tech Stack Decisions

**Decision date:** March 23, 2026 — revised from Swift/SwiftUI after Aight license analysis

### Primary Stack

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | TypeScript + React Native | Code reuse with Polly web/Electron; Aight's proven stack |
| Framework | Expo SDK 55 (managed workflow) | Full-featured, OTA updates, consistent native modules |
| Minimum iOS | iOS 16 | Expo 55 baseline |
| **Gateway client** | **`expo-openclaw-chat` (MIT)** | **Aight's own SDK, open-sourced. Gives us `GatewayClient` + `ChatEngine` + Ed25519 auth for free** |
| Auth / Crypto | `@noble/ed25519` + `@noble/hashes` | Exact match to OpenClaw gateway's key algorithm |
| Keychain | `expo-secure-store` | iOS Keychain + Secure Enclave for private key storage |
| State management | `zustand` | Lightweight, matches Aight's approach |
| Fast lists | `@shopify/flash-list` | High-perf chat list, proven in Aight |
| Markdown | `react-native-enriched-markdown` | What Aight uses; already battle-tested with OpenClaw content |
| Animations | `react-native-reanimated` + `react-native-gesture-handler` | Standard RN animation stack |
| Graphics / waveforms | `@shopify/react-native-skia` | 2D canvas for voice waveforms, custom UI elements |
| Storage (fast KV) | `react-native-mmkv` | Persistent device identity, app state cache |
| Navigation | `expo-router` + `@react-navigation/drawer` | File-based routing, matches Expo conventions |
| STT (Phase 1) | `expo-speech-recognition` | System STT, zero setup |
| STT (Phase 2) | `whisper.rn` | On-device Whisper for latency + offline; proven Expo-compatible |
| TTS | `expo-speech` | System TTS, sufficient for Phase 1 |
| Push notifications | `expo-notifications` | APNs integration, matches Aight's registration flow |
| OTA updates | `expo-updates` | Push fixes without TestFlight wait (see §8 OTA policy) |
| Gateway discovery | `react-native-zeroconf` | mDNS/Bonjour auto-discovery on LAN (Phase 2) |
| QR pairing | `ZXingObjC` (via Expo Camera) | Gateway pairing via QR code |
| Context menus | `zeego` | Native iOS context menus (long-press actions) |
| SVG | `react-native-svg` | Icons, custom graphics |
| Face ID / Touch ID | `expo-local-authentication` | Optional lock screen for Polly |
| Distribution | Expo EAS Build + TestFlight | Personal use; EAS handles signing, OTA, builds |
| Analytics | **None** | Polly is self-hosted — no Amplitude, no tracking |
| Error reporting | Optional Sentry | User's choice; not bundled by default |

### What We Are NOT Copying from Aight
- `@supabase/supabase-js` — Aight's backend for skills marketplace and billing. Polly is fully self-hosted; no Supabase dependency.
- `@amplitude/analytics-react-native` — No analytics. Polly doesn't phone home.
- Any Aight proprietary modules not explicitly MIT-licensed.

### On-Device ML — Phase 2 Roadmap
Per @ai_expert: Gateway-connected STT for Phase 1; on-device Whisper (`whisper.rn`) in Phase 2.
- `whisper.rn` adds local STT with lower latency and no gateway dependency for audio
- `mlx-swift` / `mlx-audio-swift` — audio pre-processing (VAD, noise filtering) worth evaluating for voice quality regardless of full on-device inference
- Full LLM inference via MLX is out of scope for Polly (gateway handles all inference)

### Tech Stack Decision Log
- **2026-03-23:** Initial spec drafted with Swift/SwiftUI
- **2026-03-23:** Revised to React Native + Expo after Aight license screenshot analysis revealed:
  - Aight is React Native + Expo (not Swift)
  - `expo-openclaw-chat` is MIT-licensed and provides the complete gateway client layer
  - Secure Enclave available via `expo-secure-store` (no security regression)
  - `expo-updates` enables OTA releases

---

## 13. Phased Delivery Plan

### Phase 1 — Core Chat (MVP)
**Target:** Working chat with any agent from iPhone  
**Scope:**
- [ ] Expo + React Native project setup (EAS Build configured)
- [ ] `expo-openclaw-chat` integrated (`GatewayClient` + `ChatEngine`)
- [ ] First-run onboarding: gateway URL entry + connection validation
- [ ] ChatView (streaming, markdown, tool call blocks)
- [ ] Agent switcher
- [ ] Settings: gateway URL, auth, connection paths (LAN / Cloudflare / Tailscale)
- [ ] `IntegrationCard` UI + Settings → Integrations screen shell
- [ ] Brave Search API key config (gateway passthrough)
- [ ] ElevenLabs API key config UI (activation in Phase 2)
- [ ] TestFlight / EAS build pipeline

**Unblocked:** Protocol spec complete, `expo-openclaw-chat` MIT available, stack decided.

---

### Phase 2 — Voice + Today + Core Integrations
**Target:** Voice mode, task management, key integrations live  
**Scope:**
- [ ] Voice Phase 1: `expo-speech-recognition` STT + `expo-speech` system TTS
- [ ] VoiceButton (4-state: idle → listening → processing → speaking)
- [ ] TodayView (triggers, tasks, processes)
- [ ] Item CRUD (create reminders/tasks from app)
- [ ] Push notifications (APNs via `expo-notifications`)
- [ ] **ElevenLabs TTS activated** — `whisper.rn` STT + ElevenLabs out; `.buffering` state; voice picker UI
- [ ] **Google Workspace OAuth** — Gmail + Calendar connected, gateway receives tokens
- [ ] **GitHub integration** — PAT config, gateway-side skill
- [ ] **Apple EventKit** — calendar + reminders read access, no OAuth
- [ ] Obsidian vault browser (read-only) + `/` context injection
- [ ] `react-native-zeroconf` mDNS gateway auto-discovery
- [ ] Group chat sessions + `GroupChatBubbleRow`

---

### Phase 3 — Shortcuts + Obsidian Write-back + Extended Integrations
**Target:** Full Aight parity + Obsidian depth  
**Scope:**
- [ ] ShortcutsView + management + shortcut labeling protocol
- [ ] **Obsidian write-back** (opt-in) — agents create/append notes
- [ ] **Obsidian daily note integration** — morning briefing → daily note
- [ ] **Notion API** config + gateway skill
- [ ] Readwise integration (highlights → RAG)
- [ ] MoltbookView (memory browser, search across agent memories)
- [ ] UsageStatsView (tokens, cost, model breakdown)

---

### Phase 4 — Full Settings + Admin Power Features
**Target:** Complete configuration surface  
**Scope:**
- [ ] Full Settings: providers, API keys, agent management, SOUL.md editing
- [ ] Alexa/Amazon Search config slot
- [ ] Slack integration
- [ ] Linear integration
- [ ] Cloudflare tunnel management (view status, restart from app)
- [ ] Obsidian Dataview awareness

---

### Phase 5 — Polly Differentiators (Signature Features)
**Target:** Beyond Aight in AI intelligence layer  
**Scope:**
- [ ] Domain awareness badge (Sigils/Signals/Scrolls/Glyphs/Grids auto-detect)
- [ ] Mental model selector in chat nav
- [ ] Pattern transparency cards in Today view
- [ ] RAG semantic search surfaced in chat (`/` command full implementation)
- [ ] Obsidian vault full-text + semantic search from app
- [ ] `whisper.rn` upgrade path for users who want fully on-device STT

---

## 14. Open Questions

> Most protocol questions answered by @backend (§3 complete). Remaining open items:

1. **Vault sync (remote):** When away from home, Obsidian vault access requires iCloud Drive sync of the vault to the iPhone. Users need Obsidian iOS + iCloud sync enabled. Document this as a setup requirement in onboarding. (@infra confirmed)
2. **App Store long-term:** TestFlight sufficient for personal use. If Polly ever becomes a public tool, App Store review required — out of scope for now.
3. **ElevenLabs voice latency:** Target <800ms from response received to audio start. If consistently higher, consider pre-buffering the first sentence while streaming the rest.
4. **Obsidian write-back conflicts:** If an agent writes to a note while the user is editing it in Obsidian iOS, iCloud sync handles the conflict (creates a conflict copy). Document this behavior; don't try to solve it in Polly v1.
5. **`expo-openclaw-chat` version pin:** Currently at `0.2.3`. Pin to this version; don't auto-update. Any upgrade requires reviewing changelog for protocol changes.

---

*This document is complete as of March 23, 2026. All sections are filled. For amendments, update inline and note the change in the relevant section header.*

---

### 3.19 Push Notification Config Schema

OpenClaw supports two APNs transport modes. Configured via `config.patch` on the gateway.

#### Relay mode (recommended — zero config)
```json
{
  "gateway": {
    "push": {
      "apns": {
        "relay": {
          "baseUrl": "https://relay.openclaw.dev",
          "timeoutMs": 10000
        }
      }
    }
  }
}
```
The relay handles APNs delivery on behalf of the gateway. No Apple Developer account keys needed.

#### Direct mode (self-managed)
Requires Apple Developer account with APNs key.
```json
{
  "gateway": {
    "push": {
      "apns": {
        "direct": {
          "auth": {
            "teamId": "ABCDE12345",
            "keyId": "FGHIJ67890",
            "privateKey": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
          },
          "topic": "com.yourname.polly",
          "environment": "production"
        }
      }
    }
  }
}
```

Registrations are stored in `~/.openclaw/push/apns-registrations.json` — not in `openclaw.json`.

#### Reconnect Behavior (correction for §7)

**There is no `session/load` or `session.subscribe` RPC in the webchat protocol.**

The `session/load` reference in the codebase is ACP (Codex subagent) only. Polly's correct reconnect sequence:

1. WS open → wait for `connect.challenge`
2. Send `connect` with stored `deviceToken` (or static token)
3. On success → re-fetch `sessions.list` to restore UI state
4. Re-fetch `cron.list` for Today view
5. Any in-flight agent runs resume automatically — gateway re-emits `chat` events on reconnect

No subscription re-registration needed. Sessions are server-side persistent, keyed by `sessionKey`.

---

## 15. Integrations

**Owner:** @code_architect  
**Date:** March 23, 2026

Polly surfaces integrations in two places:
1. **Settings → Integrations** — configure API keys and OAuth connections
2. **OpenClaw gateway** — integrations run as gateway-side skills; Polly provides the key config UI and any iOS-native enhancements on top

The distinction matters: Polly is not the integration runtime. It configures credentials that the OpenClaw gateway uses to execute tool calls. The exception is ElevenLabs TTS and Obsidian vault access — those run client-side on the iPhone.

---

### 15.1 Integration Tiers

#### Tier 1 — Match Aight (Phase 1–2)
These are Aight's 5 built-in integrations. Polly must support all of them.

#### Tier 2 — Polly Differentiators (Phase 2–3)
Integrations Aight doesn't have. Where Polly wins.

#### Tier 3 — Extended (Phase 4+)
Nice-to-have; add based on user demand.

---

### 15.2 Tier 1 Integrations (Aight Parity)

#### 15.2.1 Brave Search API
**Type:** API key (gateway-side skill)  
**What it does:** Web search for agents — powers real-time research, news, fact-checking  
**Config:** Single field — Brave Search API key  
**Status in Polly:** Already in use via OpenClaw. Polly just surfaces the key config UI.

```ts
interface BraveSearchConfig {
  apiKey: string  // stored in gateway via config API, not on device
}
```

**UX:** Settings → Integrations → Brave Search → paste key → Save  
**Validation:** Test call on save; show ✅ or error inline

---

#### 15.2.2 ElevenLabs
**Type:** API key (client-side TTS)  
**What it does:** Premium text-to-speech — replaces iOS system voice with natural-sounding AI voice  
**Phase:** Phase 1 config UI + Phase 2 activation (whisper.rn ships in Phase 2)

**Voice pipeline phases:**
```
Phase 1:  expo-speech-recognition (STT) → gateway → expo-speech (system TTS)
Phase 2:  whisper.rn (on-device STT)   → gateway → ElevenLabs API (premium TTS)
```

**Config fields:**
```ts
interface ElevenLabsConfig {
  apiKey: string          // stored in Keychain (client-side — not sent to gateway)
  voiceId: string         // ElevenLabs voice ID (user selects from list)
  modelId: string         // default: "eleven_turbo_v2_5" (lowest latency)
  stability: number       // 0–1, default 0.5
  similarityBoost: number // 0–1, default 0.75
}
```

**Voice selection UX:**
- Fetch available voices from ElevenLabs API on key entry
- Show voice list with play-preview button (tap to hear 3-second sample)
- User picks their preferred voice, saved to MMKV

**VoiceMode state machine update (per @ai_expert):**
```
LISTENING → PROCESSING → BUFFERING → SPEAKING → IDLE
                           ↑
              (new state: ElevenLabs streaming audio buffer filling)
              Show: animated equalizer bars, "Preparing response..."
              Duration: typically 300–800ms before playback starts
```

**Streaming playback:**
- ElevenLabs supports streaming audio — use chunked playback via `expo-av` Audio
- Buffer ~500ms before starting playback to avoid stuttering
- Show `.buffering` spinner state in VoiceButton during this window

**Fallback:** If ElevenLabs API call fails (network, rate limit, invalid key), fall back to `expo-speech` system TTS silently. Never block voice response on ElevenLabs failure.

**Key storage:** ElevenLabs key stored in `expo-secure-store` under `"polly.elevenlabs.apiKey"` — never sent to gateway, never logged.

---

#### 15.2.3 Google Workspace
**Type:** OAuth 2.0  
**What it does:** Gmail (read, draft, send) + Google Calendar (read, create events) + optionally Google Drive/Docs  
**Scope:** Gateway-side skill for tool execution; Polly handles OAuth flow natively

**OAuth scopes requested:**
```
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/drive.readonly  (optional, Phase 3)
```

**Auth flow:**
1. User taps "Connect Google" in Settings → Integrations
2. Polly opens `expo-auth-session` with Google OAuth endpoint
3. User authenticates in Safari/ASWebAuthenticationSession
4. Access token + refresh token returned to app
5. Tokens stored in `expo-secure-store`
6. Tokens forwarded to gateway via `config.set` — gateway uses them for tool calls
7. Polly refreshes tokens proactively (access tokens expire in 1hr)

**Token storage:**
```ts
// expo-secure-store keys
"polly.google.accessToken"   // short-lived, 1hr
"polly.google.refreshToken"  // long-lived, stored in Keychain
"polly.google.tokenExpiry"   // ISO timestamp, MMKV (not sensitive)
```

**Connection status UI:**
- Settings → Integrations → Google Workspace → shows connected Google account email
- "Disconnect" button → revokes token + clears Keychain
- Auto-refresh: silent token refresh on expiry, no re-auth prompt unless refresh token is revoked

**Agent capabilities unlocked:**
- "What's on my calendar this week?"
- "Draft a reply to [email]"
- "Schedule a meeting with X for Thursday"
- "Summarize my inbox from today"

---

#### 15.2.4 Notion API
**Type:** API key or OAuth  
**What it does:** Read/write Notion pages and databases  
**Priority for this user:** Lower (Obsidian is primary knowledge system) — include for completeness

**Config:** Notion internal integration token (simpler) or OAuth (for shared workspaces)  
**Implementation:** Gateway-side skill; Polly provides key config UI only  
**Phase:** Phase 3 (after Obsidian integration is solid)

```ts
interface NotionConfig {
  apiKey: string       // Internal integration token
  defaultPageId?: string  // Optional default workspace page
}
```

---

#### 15.2.5 Alexa / Amazon Search
**Type:** API key  
**What it does:** In Aight's context, likely Amazon Product Advertising API or Alexa Knowledge API  
**Priority for Polly:** Low — niche utility  
**Decision:** Include the config UI slot in Phase 4 but don't block anything on it. Skip if unused.

---

### 15.3 Tier 2 — Polly Differentiators

#### 15.3.1 Obsidian Vault ⭐ Polly's signature integration
**Type:** Local filesystem (no API key, no OAuth)  
**Runtime:** Client-side on iPhone (not gateway-side)  
**What it does:** Deep integration with your Obsidian vault — the integration Aight doesn't have

**Access strategy:**
- Obsidian for iOS can sync vault to iCloud Drive (`/iCloud Drive/Obsidian/[vault-name]/`)
- Polly reads from this path via standard iOS file APIs (no special permissions beyond Files access)
- Write-back uses the same path — creates `.md` files directly in vault
- Polly requests `UIFileSharingEnabled` + iCloud entitlement for file access

**Capabilities:**

| Feature | Phase | Description |
|---------|-------|-------------|
| Vault browser | Phase 2 | Navigate folder/file tree in Moltbook view |
| `/` context injection | Phase 2 | Pick any note to inject as chat context |
| Semantic search | Phase 2 | Search by meaning using Polly's RAG (via gateway) |
| Write-back | Phase 3 | Agents create/append to notes ("save this to my vault") |
| Daily note integration | Phase 3 | Morning briefing auto-written to today's daily note |
| Dataview awareness | Phase 4 | Answer questions about your Dataview data |
| Tag-based filtering | Phase 3 | Filter vault browser by tags |

**Config:**
```ts
interface ObsidianConfig {
  vaultPath: string          // e.g. "/var/mobile/Library/Mobile Documents/iCloud~md~obsidian/Documents/MyVault"
  dailyNotesFolder: string   // e.g. "Daily Notes"
  dailyNoteDateFormat: string // e.g. "YYYY-MM-DD"
  defaultSaveFolder: string  // Where agent write-backs go, e.g. "Polly/"
  enableWriteBack: boolean   // default: false (opt-in)
}
```

**Write-back format:**
```markdown
---
created: 2026-03-23T12:00:00
source: polly
agent: researcher
tags: [polly-generated]
---

[content written by agent]
```

**Security note:** Write-back is opt-in and off by default. Agents cannot write to vault unless user has enabled it. Path is configurable — never writes outside configured folder.

---

#### 15.3.2 GitHub
**Type:** OAuth (GitHub App) or Personal Access Token  
**What it does:** PR review, issue management, code search from chat  
**Runtime:** Gateway-side skill  

**Config:**
```ts
interface GitHubConfig {
  accessToken: string    // PAT or OAuth token
  defaultRepo?: string   // e.g. "owner/repo" for quick context
}
```

**Agent capabilities unlocked:**
- "What PRs need my review?"
- "Summarize the changes in PR #142"
- "Create an issue for [description]"
- "What's the status of issue #88?"
- "Show me recent commits on main"

**Phase:** Phase 2

---

#### 15.3.3 Apple EventKit (Calendar + Reminders)
**Type:** iOS native — no API key, no OAuth  
**What it does:** Read/write iOS Calendar and Reminders natively — zero friction  
**Runtime:** Client-side on iPhone; results surfaced to gateway as context

**Why this beats Google Calendar for some use cases:**
- Works offline
- No OAuth setup
- Includes Apple Reminders (separate from calendar)
- Reads ALL calendars (iCloud, Google, Exchange — whatever is in iOS Calendar app)

**Permissions:** `NSCalendarsUsageDescription` + `NSRemindersUsageDescription` in Info.plist  
**Phase:** Phase 2 alongside Google Workspace (offer both, user uses whichever matches their setup)

---

### 15.4 Tier 3 — Extended Integrations (Phase 4+)

| Integration | Type | Value | Notes |
|-------------|------|-------|-------|
| **Slack** | OAuth | ⭐⭐ | Summarize channels, draft messages, search |
| **Linear** | API key | ⭐⭐ | Issue/project tracking |
| **Readwise** | API key | ⭐⭐ | Highlights → RAG context, great for Obsidian users |
| **Raindrop.io** | API key | ⭐ | Bookmarks → RAG context |
| **Spotify** | OAuth | ⭐ | "Play focus music" from chat |
| **Cloudflare** (tunnel mgmt) | API key | ⭐⭐ | View tunnel status, restart tunnel from app |
| **Apple Health** | HealthKit | ⭐ | Context for wellness/fitness agents |

---

### 15.5 Settings UI — Integrations Screen

```
Settings → Integrations
─────────────────────────────────────────
  CONNECTED
  ┌─────────────────────────────────────┐
  │ 🔍 Brave Search        ✅ Active  > │
  │ 🎵 ElevenLabs          ✅ Active  > │
  │ 📅 Google Workspace    ✅ Connected>│
  └─────────────────────────────────────┘

  AVAILABLE
  ┌─────────────────────────────────────┐
  │ 📝 Obsidian Vault      Configure  > │
  │ 🐙 GitHub              Connect    > │
  │ 📱 Apple Calendar      Enable     > │
  │ 📄 Notion API          Configure  > │
  │ 🔊 Alexa Search        Configure  > │
  └─────────────────────────────────────┘

  COMING SOON
  ┌─────────────────────────────────────┐
  │ 💬 Slack                            │
  │ 📐 Linear                           │
  │ 📚 Readwise                         │
  └─────────────────────────────────────┘
─────────────────────────────────────────
```

**Each integration detail screen:**
- Status + connected account (if OAuth)
- Configuration fields (API key, OAuth, file path)
- "Test connection" button
- Disconnect / remove
- Brief description of what agents can do with it

---

### 15.6 Credential Storage Policy

| Integration | Secret | Storage | Notes |
|-------------|--------|---------|-------|
| Brave Search | API key | Gateway (via `config.set`) | Not on device |
| ElevenLabs | API key | `expo-secure-store` | Client-side TTS — stays on device |
| Google Workspace | OAuth tokens | `expo-secure-store` | Access + refresh tokens |
| Notion | API key | Gateway (via `config.set`) | Not on device |
| GitHub | PAT / OAuth | Gateway (via `config.set`) | Not on device |
| Obsidian | Vault path | MMKV | Not sensitive — just a file path |
| Apple EventKit | N/A | iOS system | No credential needed |

**Rule:** Keys used only by the gateway live on the gateway (sent via `config.set` on save). Keys used client-side (ElevenLabs, Google OAuth) live in `expo-secure-store`. File paths and non-sensitive config live in MMKV.

---

### 15.7 Table of Contents Update

Add to §ToC:
```
15. Integrations
    15.1 Integration Tiers
    15.2 Tier 1 — Aight Parity (Brave, ElevenLabs, Google, Notion, Alexa)
    15.3 Tier 2 — Polly Differentiators (Obsidian, GitHub, Apple EventKit)
    15.4 Tier 3 — Extended
    15.5 Settings UI
    15.6 Credential Storage Policy
```

---

## 18. Polly iOS Design Constitution

**Adopted:** March 23, 2026  
**Scope:** Governs the Polly iOS app (the client). AI agent behavior is governed by individual SOUL.md files in OpenClaw.  
**Authority:** Any spec decision that conflicts with these principles requires explicit justification. Default to the constitution.

---

### 18.1 The Product Statement

> **Polly is personal AI you own, not rent.**

This is not a tagline. It is a constraint. Every feature, screen, and default must be testable against it. If a decision moves Polly toward subscription dependency, data extraction, or platform lock-in, it is wrong by default.

---

### 18.2 The Progressive Capability Principle

**Polly starts simple. Complexity is revealed, not dumped.**

```
First launch:    Enter gateway URL. That's it.
First week:      Discovers voice mode, shortcuts
First month:     Configures integrations, explores Moltbook
Power user:      Distributed nodes, Orchestrator mode, full settings
```

Rules:
- First-run onboarding asks for exactly ONE thing: the gateway URL
- No feature is hidden permanently — all are discoverable
- Features surface contextually ("You've been using voice a lot — want to upgrade to ElevenLabs?")
- "Show advanced" toggles exist everywhere. Nothing is locked, just not surfaced
- Never run the user through more than 2 sequential setup screens unprompted

---

### 18.3 Icon System: Lucide, Not Emoji

**Lucide icons are the system-wide icon language. This is non-negotiable.**

Emoji are reserved for two contexts only:
1. **Agent avatars** — personality expression in SOUL.md, rendered in AgentAvatar component
2. **User-generated content** — messages the user types

Everywhere else — navigation, buttons, status indicators, labels, tab bar, tool calls, cards — uses Lucide icons.

**Why:** The old Polly codebase was actively migrating away from emoji icons (20+ replaced as of Feb 2, 2026). Emoji feel playful and inconsistent. Lucide is professional, consistent, and scalable. Polly is a serious tool.

**Package:** `lucide-react-native`  
**Sizing standard:** 18px (dense), 20px (default inline), 24px (nav/header), 28px (tab bar)  
**Color standard:** `colors.textSecondary` at rest, `colors.accent` when active/selected

See §5.1 icon mapping table for specific icon assignments per UI element.

---

### 18.4 Data Ownership Rules

These are hard rules, not guidelines:

1. **No analytics without explicit opt-in.** No Amplitude, no Mixpanel, no telemetry by default. Ever.
2. **No data sent to third parties without user initiation.** Messages go to the gateway (user's own machine). That's it.
3. **All credentials in Keychain.** Never in UserDefaults, never in logs, never in URLs.
4. **Obsidian write-back is opt-in and off by default.** Agents cannot modify the user's vault without explicit permission.
5. **The app must work on LAN with no internet.** Cloud integrations are additive, never required.
6. **Export everything.** Any data Polly stores (shortcuts, settings, item history) must be human-readable and exportable.

---

### 18.5 Anti-Patterns (Never Ship These)

These patterns were explicitly identified and rejected in Polly's design history:

| Anti-pattern | Why | Alternative |
|-------------|-----|-------------|
| Emoji as UI icons | Inconsistent, unprofessional | Lucide icons |
| Modal interruptions | Break flow | Inline suggestions, non-blocking |
| Setup wizard hell | Overwhelming | Single-question onboarding, progressive |
| Loading spinners blocking content | Feels stuck | Progressive streaming content |
| Silent failures | Confusing | Always communicate state, even if gracefully |
| Scroll position loss | Jarring | Maintain position on any reload |
| UI flash on reconnect | Feels buggy | Smooth state transitions, skeleton screens |
| Subscription prompts | Contradicts ownership | One-time or free, always |
| Forced feature discovery | Presumptuous | Contextual, dismissible nudges |

---

### 18.6 What the Constitution Does NOT Cover

The following are governed by OpenClaw, not by this document:

- **Agent personality and tone** → SOUL.md per agent
- **Agent capabilities and tools** → OpenClaw skills + gateway config
- **Memory and learning** → MEMORY.md per agent workspace
- **Model selection and routing** → OpenClaw gateway config + provider settings
- **Session management** → OpenClaw gateway

The Constitution governs the *app shell*. The agents govern themselves via OpenClaw.

---

### 18.7 Decision Checklist

Before shipping any feature, ask:

- [ ] Does this respect user data ownership? (§18.4)
- [ ] Does this use Lucide icons, not emoji, in UI chrome? (§18.3)
- [ ] Does this surface complexity progressively, not all at once? (§18.2)
- [ ] Does this work on LAN with no internet? (§18.4, rule 5)
- [ ] Does this avoid the anti-patterns list? (§18.5)
- [ ] Is the default state beautiful and functional with zero configuration? (§18.2)
- [ ] Would the user feel they *own* this tool after using this feature? (§18.1)

If any answer is no — redesign before shipping.


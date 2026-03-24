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

**Core organizing unit: Teams.** Everything in Polly lives inside a team. A team is a named collection of agents with a shared purpose (e.g., "Dev Squad," "Life Team," "Content Studio"). You set up teams during onboarding from pre-built templates or by composing your own. Once set up:
- The drawer shows your active team and its agents
- Sessions (individual chats + group chats) are scoped to a team
- Switching teams switches the entire context — agents, sessions, and group chats
- Agents can exist in multiple teams, but their sessions and memory are team-scoped

This mirrors Aight's team model exactly, and it's the right mental model for Polly too.

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
│  │  Message Augmentation (client-side) │   │
│  │  Vault note injection / Model text  │   │
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
The GatewayClient is the only component that speaks directly to OpenClaw. Everything else in the app consumes its observable state. The PollyEnhancement Layer intercepts outgoing messages to inject user-selected context (vault notes, mental model text) before they hit the gateway — this is **message augmentation, not RAG retrieval**. There is no direct iOS → Polly REST API connection. The Polly Python backend, if running, is a gateway-side resource that agents tool-call independently. The iOS client never knows it exists.

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
| `push.status` | `{}` | `{ configured, mode, relay?, direct? }` | Pre-registration validation — see §3.14 |
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
    let theme: String?           // hex color string e.g. "#f0903b" — USE THIS as agent accent color
    let emoji: String?           // e.g. "🧠"
    let avatar: String?          // filename
    let avatarUrl: String?       // resolved URL
}
```

**`identity.theme` — agent accent color (confirmed from `AgentSummarySchema` source)**
- Field: `agent.identity.theme` (optional hex string, e.g. `"#f0903b"`)
- Currently unpopulated on all agents in this gateway — `theme: null` for all
- **Read**: present in `agents.list` response when set
- **Write**: use `config.patch` to set (e.g. `{ "agents": { "list": [...agent with theme field...] } }`). `agents.update` does NOT support `theme` — it's missing from `AgentsUpdateParamsSchema`. This is a known gateway gap; `config.patch` is the workaround until upstream adds it.
- **Client fallback**: when `identity.theme` is null, derive deterministic color from `agentId`:
  ```typescript
  // SHA-1 first 3 bytes → HSL(h, 65%, 55%) — consistent across devices, looks good on dark bg
  const hue = (hashBytes[0] + hashBytes[1] * 256) % 360;
  const fallbackColor = `hsl(${hue}, 65%, 55%)`;
  ```
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

#### Push Configuration Validation (@infra Blocker 2)

Before attempting push registration, Polly must validate that the gateway's push infrastructure is correctly configured. An unconfigured gateway will silently accept push registrations and then fail to deliver — the user sees notifications promised in Settings but never arriving.

**`push.status` RPC — add to §3.4:**

```swift
// REQUEST
{ "method": "push.status", "id": "rpc-1" }

// RESPONSE
{
  "configured": true | false,
  "mode": "relay" | "direct" | "unconfigured",
  "relay": {                          // present when mode == "relay"
    "reachable": true | false,
    "latencyMs": 42
  },
  "direct": {                         // present when mode == "direct"
    "keyPresent": true | false,       // .p8 key file exists and is readable
    "keyValid": true | false,         // key parses as valid EC private key
    "teamId": "ABCDE12345",
    "keyId": "FGHIJ67890",
    "environment": "production" | "sandbox"
  }
}
```

**iOS client behavior based on `push.status`:**

| `configured` | `mode` | Action |
|---|---|---|
| `true` | `relay` or `direct` | Proceed with `aight.push.register` |
| `false` | `unconfigured` | Show Settings → Notifications banner: "Push not configured on gateway — [How to set up]" |
| `true` | `direct`, `keyValid: false` | Show warning: "Gateway APNs key is invalid — notifications may not deliver" |

**When to call `push.status`:**
- On first connect after install
- When user enables notifications in Settings → Notifications
- On reconnect after 24h+ gap (config may have changed)

**`NSAllowsLocalNetworking` ATS exception (@infra):**
Add to `Info.plist`:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsLocalNetworking</key>
    <true/>
</dict>
```
This permits `ws://` on LAN IP addresses. Does not affect remote connections (still WSS required). Required for LAN path to work without certificate gymnastics.

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

### 4.0 Navigation Model — Drawer

**Polly uses a slide-out drawer, not a tab bar.**

Chat is the permanent home surface. The drawer slides in from the left (swipe right or tap the hamburger icon in the chat nav bar). The drawer is the control center: switch agents, navigate to other views, start new conversations, see active sessions.

**Full app layout:**

```
┌─────────────────────────────────────┐
│ [≡]  🤖 Agent Name  [domain] [🧠]  │  ← Chat nav bar
├─────────────────────────────────────┤
│                                     │
│           Chat surface              │
│         (always present)            │
│                                     │
│                                     │
├─────────────────────────────────────┤
│ [ AugmentationPills if active     ] │
│ [🎤] [Type a message...      ] [➤] │
└─────────────────────────────────────┘
```

**Drawer open (swipe right or tap [≡]):**

```
┌──────────────┬──────────────────────┐
│ POLLY      [+]│                      │
│              │                      │
│ Workspace  ▾ │                      │
│ [Home      ] │    Chat surface      │
│              │    (dimmed)          │
│ Agent      ▾ │                      │
│ [🖥️ Code Arch]│                      │
│              │                      │
│ TODAY      ▾ │                      │
│ Home — Now   │                      │
│ Group — 2m   │                      │
│              │                      │
│ ─────────────│                      │
│ 👥 Agents    │                      │
│ 📅 Today     │                      │
│ ⚡ Shortcuts │                      │
│ 📊 Usage     │                      │
│ 📚 Moltbook  │                      │
│ ⚙️ Settings  │                      │
└──────────────┴──────────────────────┘
```

**Drawer sections:**

1. **Header:** App name + [+] new conversation button
2. **Team selector:** Shows active team name with dropdown chevron. Tapping opens a team picker sheet — lists all configured teams (from templates or custom). Switching teams switches the active context: agents, sessions, group chats, and Today items all scope to the selected team. In single-team setups the dropdown is low-traffic; power users with multiple teams switch here frequently.
3. **Agent selector:** Shows current agent emoji + name with dropdown chevron. Tapping opens agent picker sheet (full list of configured agents). Switching agent here switches the active chat session.
4. **TODAY (collapsible):** Recent active chat sessions **scoped to the currently-selected agent or group**. If the agent selector shows "Strategist," TODAY shows only sessions with the Strategist. If the agent selector shows "Sigils" (a group), TODAY shows individual sessions with each Sigils member agent AND any group chat sessions for that group. Switching the agent selector updates TODAY immediately — it is never a global flat list. Each row shows session label + relative time. Tap navigates to that session.
5. **Navigation links (bottom section):** Agents, Today, Shortcuts, Usage, Moltbook, Settings — each with a colored square icon badge (Lucide icon on colored background per domain color system). Tapping navigates to that full-screen view, closing the drawer.

**Drawer interaction:**
- Open: swipe right from left edge, or tap [≡] in chat nav bar
- Close: swipe left, tap backdrop (dimmed chat area), or tap any nav item
- Animation: spring-physics slide, 300ms, slight parallax on chat surface
- Backdrop: chat surface dims to 40% opacity while drawer is open

**Right panel (swipe LEFT from right edge of chat):**
- User-configurable in Settings → Preferences → Swipe Right Screen: `Voice` | `Shortcuts`
- Default: Voice panel (voice mode controls + waveform)
- Shortcuts panel: same shortcuts grid as the Shortcuts view, quick-access without navigating away
- This is a separate gesture from the drawer — swipe right edge → right panel; swipe left edge → drawer

**[+] New conversation:**
- Tap → opens agent picker sheet → select agent → new empty chat session
- If already in an empty session with that agent, do nothing (don't stack)

---

### 4.1 Chat View

**Purpose:** Primary interface. Permanent background surface. Accessible from everywhere via drawer close.

**Layout:**
```
┌─────────────────────────────────────┐
│ [≡]  🤖 Agent Name  [domain] [🧠]  │  ← Nav bar
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
│ [📄 MEMORY.md ✕]  [🧠 Inversion ✕]│  ← Augmentation pills (conditional)
│ [🎤] [Type a message...      ] [➤] │  ← Input bar
└─────────────────────────────────────┘
```

**Nav bar elements:**
- **[≡]** (left): Opens drawer
- **Agent name + emoji** (center): Tappable — opens agent picker sheet (same as drawer agent selector)
- **[domain badge]** (right of name): Colored domain pill — auto-detected, tappable to override (§11.2)
- **[🧠]** (right): Mental model quick-select (§11.3)

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
- Long-press message → copy / quote / delete
- Pull to load history
- `/` in input → opens vault note picker (§11.1)

**Scroll behavior:**
- `FlatList` (inverted) — messages rendered bottom-up, newest at bottom
- `inverted={true}` + data array in reverse-chronological order so newest message is always in view
- `keyboardShouldPersistTaps="handled"` — tapping a message does not dismiss keyboard
- Auto-scroll to bottom on: new outbound message, first delta of a new streaming response
- Pull-to-load-history: `onEndReached` (inverted = top of list) triggers `chat.history` fetch with cursor; prepends older messages; scroll position preserved
- Scroll lock: if the user manually scrolls up mid-stream, auto-scroll suspends. Resume auto-scroll when user scrolls back to bottom or stream ends.

**Empty state:**
- Shown when conversation history is empty (new session or history cleared)
- Centered in the message area (above input bar)
- Agent emoji in a large circle (56pt, agent's theme color bg)
- Agent name in `semibold/18`
- One-question frame text in `regular/15` secondary color — pulled from agent template metadata (e.g. *"Is this the right design?"*)
- No button, no CTA — just the framing question. User types to begin.

**Keyboard / layout:**
- `KeyboardAvoidingView` with `behavior="padding"` on iOS
- Input bar + augmentation pills rise with keyboard; message list compresses above
- Safe area bottom inset applied to input bar container — no content hidden behind home indicator
- On iPhone SE / small devices: augmentation pills collapse to a single `+X more` chip when they would overflow one line. **In practice this never triggers in Phase 1–4: the pill row contains a maximum of two pills simultaneously (one vault note + one mental model). Theme injection never appears as a pill — it operates on the system prompt at the gateway layer, not the message. Two pills always fit on one line on all supported devices. The collapse chip is a defensive implementation detail for Phase 5+ if domain injection is added.** (@design_eng BLOCKER #2 closed — max pill count is bounded and known.)

**Layout grid:**
- Nav bar: 44pt height + safe area top
- Message list: flex-fill between nav bar and input bar
- Augmentation pills row: 36pt height, 12pt horizontal padding, hidden when no pills active
- Input bar: 52pt min-height (expands with multiline text, max 120pt / ~4 lines), 12pt horizontal padding
- Total chrome (nav + input bar): ~96pt — leaves ~700pt content area on iPhone 15 Pro

**Error states:**
| Error | Display |
|-------|---------|
| Gateway disconnected | Inline banner below nav bar: "Disconnected — [Retry]" (amber bg). Input bar disabled. |
| Message send failed | Bubble shows red `!` retry icon. Tap to resend. |
| Stream interrupted mid-response | Partial response shown with `[Response interrupted]` appended in secondary color. Retry button in bubble. |
| Auth failure | Sheet: "Connection lost — check your gateway token." with Settings deep-link. |

---

### 4.2 Today View

**Purpose:** Dashboard of active items — reminders, tasks, background processes. Accessed from drawer nav link.

**Layout:**
```
┌─────────────────────────────────────┐
│ [<]                         [⊞]    │  ← nav bar (back + filter)
│                                     │
│  Today   Mar                        │  ← large title + month
│                                     │
│  T   F   S   S  [M]  T   W   T     │  ← date strip (horizontal scroll)
│  19  20  21  22 [23] 24  25  26    │    selected date = filled circle
│                                     │
│  [All 0] [Upcoming 0] [Tasks 0]    │  ← filter chips
│  [Activity 0]                       │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  ✦  All clear               │   │  ← empty state (sparkles icon)
│  │  No reminders or tasks for  │   │
│  │  today. Enjoy the calm.     │   │
│  └─────────────────────────────┘   │
│                                     │
│                              [+]   │  ← FAB bottom-right
└─────────────────────────────────────┘
```

**Date strip:**
- Horizontally scrollable week strip
- Day-of-week letter above, date number below
- Selected date: filled white circle around date number
- Today is always pre-selected on open
- Tap a date to filter items to that date
- Custom component — not a full calendar sheet

**Filter chips:**
- `All` / `Upcoming` / `Tasks` / `Activity` — pill chips with item counts
- Active chip: white filled bg, dark text
- Inactive chips: dark muted bg, secondary text
- "Activity" = background agent processes (what we previously called "Processes")
- Chips filter a **flat list** — not grouped sections with headers

**Item list (when populated):**
- Flat scroll, no section headers
- Each item row:
  - Left: type icon (🔔 Upcoming, ☐ Task, ⟳ Activity)
  - Title + time/label
  - Right: status indicator or chevron
  - Domain-colored label chip (from client-side domain config)
- Swipe right → mark done (green checkmark reveal)
- Swipe left → cancel/delete (red trash reveal)
- Tap → expand inline or push detail view

**Empty state:**
- Sparkles icon on dark circle bg (Polly accent color, not Aight lime)
- Headline: **"All clear"**
- Body: *"No reminders or tasks for today. Enjoy the calm."*
- Shown when filtered count = 0

**FAB [+] → Add Item sheet:**
- Bottom sheet, slides up above keyboard
- **Title:** "Add Item"
- **Type selector:** Three pill chips — `☑ Task` · `📅 Event` · `⏰ Reminder`
  - Active type: Polly accent fill (`#f0903b`)
  - Inactive: dark muted bg
  - Switching type changes the text field placeholder and submit button label
- **Text field:** Full-width, multiline, auto-focused on sheet open
  - Task placeholder: "What needs to be done?"
  - Event placeholder: "What's the event?"
  - Reminder placeholder: "What do you want to be reminded of?"
- **Submit button:** Full-width, "Add Task" / "Add Event" / "Add Reminder" — disabled (muted) until text entered; enabled once text present
- **No enrichment fields on creation** — labels, domain, time, priority are set after creation by tapping the item. Keep creation friction minimal.
- Keyboard auto-raises when sheet opens

**[⊞] Filter button (top-right):**
- Opens **"Filter by Label"** bottom sheet
- Shows all labels currently attached to items as selectable chips — tap a label to filter the list to only items with that label
- Empty state: tag icon, "No labels yet", "Labels will appear here as you add items to your day."
- [✕] circle button top-right to dismiss
- This is label-only filtering — not sort/priority/domain. Keep it simple.

**Polly Enhancements:**
- Domain-colored label chips on items
- **Inbox card:** When `_inbox/` contains unprocessed captures, a persistent card appears at the top of the Today list (above all other items, regardless of date filter):
  ```
  ┌─────────────────────────────────────┐
  │  📥  3 captures waiting             │
  │  Tap to process your Polly Inbox    │  → tapping opens Inbox Review queue
  └─────────────────────────────────────┘
  ```
  Card style: muted border, secondary text. Disappears when inbox is empty.

- **"Polly noticed..." card** *(Phase 3+ — agent-mediated, opt-in)*: A dismissible insight card that surfaces when the active agent observes a recurring topic across recent captures or conversations. Not engine-driven — the agent generates this on a timed cadence (e.g., once per week). Example:
  ```
  ┌─────────────────────────────────────┐
  │  🧠  Polly noticed                  │
  │  You've captured 6 notes about      │
  │  norns synthesis this week.         │
  │  Want to organize them?  [Yes] [✕] │
  └─────────────────────────────────────┘
  ```
  Opt-in toggle in Settings → Preferences → Features: "Polly Noticed cards". Default: ON. Card dismissal is permanent (stored in MMKV).

---

### 4.3 Shortcuts View

**Purpose:** Quick-access saved prompts — one tap starts a conversation with the active agent using a pre-written prompt. Optionally exposed to iOS Shortcuts app via App Intents.

**Subtitle:** "One tap to start a conversation"

**Layout:**
```
┌─────────────────────────────────────┐
│ [<]                                 │
│                                     │
│  Shortcuts                          │  ← large title
│  One tap to start a conversation    │  ← subtitle, muted
│                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ │
│  │  ☁️  │ │  📋  │ │  ✉️  │ │ 📅 │ │  ← 4-column icon grid
│  └──────┘ └──────┘ └──────┘ └────┘ │
│  Weather  Daily    Emails  Calendar │
│           Brief                     │
│                                     │
│  ┌──────┐                           │
│  │  +   │                           │  ← inline Add tile (next grid slot)
│  └──────┘                           │
│   Add                               │
│                                     │
└─────────────────────────────────────┘
```

**Grid layout:**
- 4 columns, wrapping rows — iOS home screen grid style
- Each shortcut: custom colorful rounded-square icon image (~72pt, same corner radius as iOS app icons `size × 0.225`) + label below in small text
- [+] Add tile: muted gray rounded square, `+` icon, "Add" label — always in the next open grid position after existing shortcuts
- Long-press shortcut → context menu: Edit / Delete / Rearrange
- Tap shortcut → sends its prompt to the active agent, navigates to Chat view

**Shortcut icon design:**
- Custom colorful rounded-square images — not emoji, not Lucide icons
- Each shortcut has a background color + a centered icon (Lucide icon or SF Symbol rendered on the color bg)
- When creating a shortcut, user picks: name + background color + icon from icon picker
- Icon renders at ~40pt on the colored bg, total tile ~72pt

**Add shortcut sheet:**
- Name (text field)
- Prompt text (multiline — the full prompt sent on tap)
- Icon picker (grid of Lucide icons)
- Color picker (palette of preset colors)
- "Create Shortcut" button

**Apple Shortcuts / App Intents integration *(Phase 2):***
- Polly shortcuts are exposed as App Intents, making them invocable from:
  - iOS Shortcuts app (automation workflows)
  - Siri ("Hey Siri, run my Daily Brief in Polly")
  - Lock Screen / Action Button shortcuts
  - Shortcuts widget on home screen
- Requires a native Swift module wrapping `AppIntents` framework — not available in JS-only Expo
- Phase 1: in-app grid only
- Phase 2: `expo-app-intents` native module or bare workflow with custom native code
- Each Polly shortcut auto-registers as an `AppIntent` with title + prompt payload

---

### 4.4 Moltbook View

**Phase gate: Phase 2.** Moltbook is an external platform with an API Polly doesn't control. Detailed spec is deferred to avoid over-investing in a dependency that may change. The full Moltbook screen spec is in Appendix B (§Appendix B — Moltbook Full Spec) for reference.

**Phase 1 behavior:** Moltbook tab is present in the drawer nav but tapping shows: "Moltbook is coming in Phase 2 — the front page of the agent internet." No API calls, no web view, no feed rendering.

**Phase 2 scope (summary):** Read-only feed browsing (public REST API, no auth). Hot/New/Top/Rising sort. Submolts directory. Agent participation (post/comment) via gateway-side Moltbook skill.

**API key security:** Collected during agent registration flow, forwarded to gateway via `config.patch`, purged from client. iOS never retains the Moltbook API key after setup.

**Layout:**
```
┌─────────────────────────────────────┐
│ [<]                    [🔍] [⊞]    │
│                                     │
│  Moltbook                           │  ← large title
│                                     │
│  [Everything]  [Following]          │  ← tab selector
│                                     │
│  [Hot] [New] [Top] [Rising]         │  ← sort chips
│                                     │
│  ┌───────────────────────────────┐  │
│  │ ▲ 12                         │  │  ← upvote button + count
│  │ The operationalized self:     │  │  ← post title
│  │ why your cron jobs define     │  │
│  │ who you are more than your    │  │
│  │ SOUL.md                       │  │
│  │ excerpt text...               │  │
│  │ [m/general]  👤user  2h  💬5  │  │  ← meta row
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ ▲ 8                          │  │
│  │ meaning provenance: the       │  │
│  │ problem nobody is solving     │  │
│  │ ...                           │  │
│  │ [m/philosophy]  👤bot  4h 💬2 │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Feed tabs:**
- **Everything** — global feed across all submolts
- **Following** — submolts your agents are subscribed to (requires Moltbook skill configured)
- A third entry point: **[🦞 Submolts]** button/link in the feed header → navigates to Submolts directory

#### 4.4.1 Submolts Directory

Accessible from a "Submolts" link in the Moltbook feed header.

```
┌─────────────────────────────────────┐
│ [<]                                 │
│ 🦞 Submolts                         │  ← large title + lobster emoji
│    20 communities                   │  ← subtitle (count from API)
│                                     │
│ [🔍 Search communities...        ]  │  ← full-width search bar
│                                     │
│ ┌───────────────────────────────┐   │
│ │ [m/introductions] 👥 126.1k [Subscribe]│
│ │ New here? Tell us about        │   │
│ │ yourself! Who are you...       │   │
│ └───────────────────────────────┘   │
│ ┌───────────────────────────────┐   │
│ │ [m/openclaw-explorers] 👥 2.0k [Subscribe]│
│ │ OpenClaw Explorers             │   │
│ │ A gathering place for agents   │   │
│ │ running on OpenClaw...         │   │
│ └───────────────────────────────┘   │
└─────────────────────────────────────┘
```

**Submolt cards:**
- Submolt name pill (dark muted bg, accent-text label) left-aligned
- Member count (👥 + formatted number) center
- "Subscribe" button (accent color filled pill) right-aligned
- Optional display name (semibold, below pill row)
- Description (muted, 2 lines max, truncated)
- Card bg elevated (bgSecondary), full-width, 12pt radius

**Subscribe in Phase 1:** Button visible but disabled — tapping shows "Connect an agent to subscribe. Go to Settings → Integrations → Moltbook."

**Recommended submolts to pre-subscribe on agent setup:**
- `m/openclaw-explorers` — directly relevant; auto-suggest during Moltbook skill setup
- `m/agents` — for autonomous agent discussion
- `m/general` — town square

**Sort chips:** Hot · New · Top · Rising — maps to Moltbook API sort parameters. Active = filled accent pill; inactive = plain text (no border).

**Tab indicator:** Underline style (not filled pill) — accent color `#f0903b` on active tab.

**Post cards:**
- **Left column:** ↑ arrow (accent color) stacked above upvote count (bold, accent color, ~20pt) — fixed-width left column, not inline with title
- Title (semibold, white, 2 lines max, truncated with …)
- Excerpt (muted, 2 lines, truncated)
- Meta row: `m/submolt` tag (dark rounded pill) · agent avatar (Moltbook circular identicon, render from URL) · username · relative time · ○ comment count (open circle icon)
- Card bg: slightly elevated (bgSecondary), full-width, 12pt radius
- Tap → post detail view (threaded comments, full text)
- Tapping upvote: requires gateway skill configured; if not connected, prompt to connect

**Agent connection (Settings → Integrations → Moltbook):**
- If no agent is connected: banner at top "Connect an agent to participate"
- Connection flow: user sends their agent to `moltbook.com/skill.md` (agent self-registers, sends claim link back, user verifies via X/Twitter)
- Once connected: upvote/comment/post available

**Phase 1 scope:** Read-only feed browsing (no auth required). Agent participation (post/comment) deferred to Phase 2 when Moltbook skill is installable from Settings.

**Moltbook API key:** Collected during agent registration UX and held temporarily in `expo-secure-store` key `"polly.moltbook.apiKey"`. On registration completion, forwarded to gateway via `config.set` and immediately purged from `expo-secure-store`. iOS does not hold the key after setup. Never logged, never sent to any domain other than `https://www.moltbook.com`.

---

### 4.5 Usage Stats View

**Purpose:** Token usage tracking — OpenClaw gateway stats + external provider quota (if applicable).

**Layout (scrollable, no period picker):**
```
┌─────────────────────────────────────┐
│  Usage                              │  ← large title, no nav chrome
│                                     │
│  MODELS                             │  ← small-caps section header
│  ┌───────────────────────────────┐  │
│  │ [icon] Provider Name         │  │  ← per configured provider
│  │        plan_tier              │  │
│  │ Quota A              58% left │  │  ← progress bar (provider color)
│  │ Quota B             100% left │  │
│  └───────────────────────────────┘  │
│                                     │
│  CREDIT USAGE                       │
│  ┌─────────────┐ ┌───────────────┐  │
│  │ 📅 Today    │ │ 📅 Last 30d   │  │  ← 2-up stat cards
│  │ 0           │ │ 128.8k        │  │
│  │ tokens      │ │ tokens        │  │
│  └─────────────┘ └───────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Daily Breakdown               │  │  ← breakdown card
│  │ Last 3 days                   │  │
│  │ Mar 22  ██░░░░░░░░░  6.5k    │  │
│  │ Mar 21  ████░░░░░░░  24.8k   │  │
│  │ Mar 17  ██████████░  97.6k   │  │
│  └───────────────────────────────┘  │
│                                     │
│  OPENCLAW                           │
│  ┌─────────────┐ ┌───────────────┐  │
│  │ ↗ Total     │ │ ↑ Input       │  │  ← 2×2 stat grid
│  │ Tokens      │ │               │  │
│  │ 1M          │ │ 6.2k          │  │
│  │ 35 sessions │ │ prompt tokens │  │
│  └─────────────┘ └───────────────┘  │
│  ┌─────────────┐ ┌───────────────┐  │
│  │ ↓ Output    │ │ ⊞ Sessions    │  │
│  │ 29k         │ │ 35            │  │
│  │ completion  │ │ active        │  │
│  └─────────────┘ └───────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ [chip] claude-sonnet-4.6      │  │  ← active model card
│  │ Context Window        128.0k  │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │ Usage by Session              │  │
│  │ Top sessions by token count   │  │
│  │ Home               454.5k ██  │  │
│  │ claude-sonnet-4.6             │  │
│  │ Home               200.8k ██  │  │
│  │ claude-haiku-4.5              │  │
│  │ ...                           │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**MODELS section:**
- Only shown if external providers with quota tracking are configured (e.g., GitHub Copilot)
- One card per quota-tracked provider
- Progress bars show remaining quota (not consumed) — colored with provider's brand color
- Hidden entirely for self-hosted/API-key providers (Anthropic, OpenAI direct) — those don't have quota in this sense
- Polly Phase 1: section hidden (no quota-tracked providers in default config)

**CREDIT USAGE:**
- "Today" and "Last 30 Days" stat cards side-by-side
- Token counts formatted with k/M suffixes (e.g., 128.8k, 1M)
- Data sourced from OpenClaw gateway `usage.get` RPC

**Daily Breakdown card:**
- "Last 3 days" (fixed window — no user-configurable period)
- Per-day rows: date label left, formatted token count right, lime green progress bar
- Bar width proportional to max day in the set
- Bar color: Polly accent (`#f0903b`) — not lime green (that's Aight's brand color)

**OPENCLAW 2×2 stat grid:**
- Total Tokens (with session count subtitle)
- Input (prompt tokens)
- Output (completion tokens)
- Sessions (active session count)
- Each card: colored icon badge (Lucide icon on rounded-square bg) + large number + descriptor subtitle

**Active model card:**
- Shows current active model name + context window size
- Model chip icon (chip/processor Lucide icon)

**Usage by Session:**
- "Top sessions by token consumption" subtitle
- Flat list, ordered by token count descending
- Each row: session title (truncated with …) | token count right-aligned | lime/accent bar | model name below title
- Scrolls within the parent scroll view

**No period picker.** Stats are always-on cumulative + last-30-days. No date range selector in Phase 1.

---

### 4.6 Vault Search View

**Purpose:** Search the user's configured vault (Obsidian or Notion) and the Polly Inbox. Accessed via drawer nav link or the `/` command in chat input (§11.1).

---

### 4.6.1 Chat History Search

**Purpose:** Find past conversations across all agents and sessions. A power user with 200+ sessions needs this to be functional.

**Phase 1 scope:** Client-side search over cached session titles and agent names only (fast, no server round-trip). Searches `sessions` table in `expo-sqlite`.

**Phase 2 scope:** Full-text search over cached message content (`messages.content_json` column) + `chat.history` server search if the gateway adds a search parameter to `sessions.list`.

**UI:** Accessed from "All Sessions" view (§4.1.5) search bar. Filters the session list in real time. No separate screen.

**Empty state:** "No conversations match '[query]'. Try searching by agent name."

---

### 4.6.2 Image Attachments

**Phase gate:** Phase 2. Phase 1 text-only.

**Wire format (Phase 2):** Images sent as base64-encoded data URLs in `ChatSendParams.attachments`:
```typescript
interface Attachment {
  type: 'image';
  mimeType: 'image/jpeg' | 'image/png' | 'image/webp';
  data: string;       // base64 encoded
  filename?: string;
}
```

**Size limit:** 5MB per image, 3 images per message. Client enforces before send — shows "Image too large (max 5MB)" toast if exceeded.

**Sources:** Camera capture (`expo-camera`) + photo library picker (`expo-image-picker`). Both require permissions — request on first use with clear rationale.

**Rendering:** Images in chat rendered as rounded `<Image>` components (max 240pt wide, aspect-ratio-preserved). Tap to open full-screen viewer with pinch-zoom. No inline image editing.

**Phase 1 fallback:** If a received message contains `type: "image"` content blocks (from a future gateway feature), render a "📎 Image attachment (not supported in this version)" placeholder rather than crashing.

> **Phase gate:** Phase 1 — Obsidian only (filesystem read). Notion search via API in Phase 2.

**Layout:**
```
┌─────────────────────────────────────┐
│ [<]                                 │
│                                     │
│  [🔍 Search your vault...        ]  │  ← auto-focused on open
│                                     │
│  RECENT SEARCHES                    │
│  ┌─────────────────────────────┐   │
│  │  "norns synthesis"          │   │
│  │  "first principles"         │   │
│  └─────────────────────────────┘   │
│                                     │
│  ── or ──                           │
│                                     │
│  [results list when query active]   │
└─────────────────────────────────────┘
```

**Search behavior:**
- Searches local Obsidian vault (file names + content) via the configured vault path
- Also searches `_inbox/` (Polly captures) — inbox results shown with a 📥 badge
- Debounced: fires 300ms after last keystroke
- Results: file name (bold), domain chip (colored), first matching snippet (secondary text, matching terms highlighted)
- Tap result → opens file in read-only markdown view (same renderer as Moltbook, §4.4)
- Tap result with vault context active → offers "Insert as context" (injects `[[note title]]` link into chat input)

**Filter chips (below search bar, appear after first query):**
- `All` · `Notes` · `Inbox` · `[active domains...]`
- Domain chips are dynamically generated from the user's configured domains

**Empty state (no query):**
- Shows recent searches (last 5, stored MMKV `"polly.recentSearches"`)
- Below recent searches: "Browse by domain" — one chip per configured domain, tap to filter full vault by domain tag

**No-results state:**
- "Nothing found for '[query]'" 
- Suggestion: "Try asking an agent — tap here to open chat with this search as your message"

**Keyboard:**
- Search field auto-focused on view open (keyboard up immediately)
- Back button or swipe-down → closes view, returns to chat

---

### 4.7 Agents View

**Purpose:** Browse all configured OpenClaw agents, create new ones, manage existing.

**Layout:**
```
┌─────────────────────────────────────┐
│  [<]              [Workspace ▾]     │  ← nav bar
│                                     │
│  Agents                             │  ← large title
│                                     │
│   [😀] [🎨] [📊] [👨‍🍳] [✍️]         │  ← avatar strip (scrollable)
│                                     │
│      Build your team                │  ← header copy
│   Add more specialists to cover     │
│   every angle. Each agent has its   │
│   own personality, skills, and      │
│   model.                            │
│                                     │
│  ┌───────────────────────────────┐  │
│  │     Create New Agent          │  │  ← primary CTA, full-width pill
│  └───────────────────────────────┘  │
│                                     │
│  YOUR AGENTS                  Edit  │  ← section header
│  ┌───────────────────────────────┐  │
│  │ [🖥] Code Architect         > │  │
│  │      @code_architect          │  │
│  ├───────────────────────────────┤  │
│  │ [🖼] Frontend Developer     > │  │
│  │      @frontend                │  │
│  ├───────────────────────────────┤  │
│  │ [🏗] Backend Architect      > │  │
│  │      @backend                 │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Header section ("Build your team"):**
- Always shown, not just empty state — it's a persistent top section with motivational copy
- Avatar strip: horizontally scrollable row of all existing agent avatars (emoji on dark rounded-square bg, iOS app-icon style)
- Copy is fixed: "Add more specialists to cover every angle. Each agent has its own personality, skills, and model."

**Create New Agent button:**
- Full-width, large pill shape, Polly accent color (`#f0903b` orange)
- Tapping opens the agent creation flow (see §4.7.1 below)

**YOUR AGENTS section:**
- Small-caps section label + "Edit" link (accent color) on right
- Edit mode: rows show drag handle (reorder) + delete button (red circle ✕)
- Each agent row:
  - **Avatar:** emoji rendered on dark rounded-square background (≈44pt, iOS app-icon style). **Not bare emoji — emoji on a dark badge bg.**
  - **Name:** semibold, 16pt
  - **Handle:** `@username`, muted, 13pt
  - **Chevron:** `>` right-aligned
  - **Divider:** subtle 1px between rows
  - Grouped in a single rounded card container (bgSecondary bg, 12pt radius)
- Tap row → Agent detail view (SOUL.md viewer, model config, enable/disable)

**Workspace pill (top-right nav bar):**
- Shows current workspace name with dropdown chevron
- **Persistent across all full-screen views** (Agents, Today, Shortcuts, Usage, Moltbook) — not just the drawer
- Tapping opens team picker sheet
- In single-workspace setups this is mostly decorative but provides context

#### 4.7.1 Agent Creation Flow

Tapping "Create New Agent" navigates to **"Choose a Template"** screen.

**Template screen layout:**
```
┌─────────────────────────────────────┐
│ [<]  Choose a Template              │
│                                     │
│ Pick a template, create a public    │
│ figure agent, or build from scratch │
│                                     │
│ [All] [Technical] [Productivity]    │ ← horizontal filter chips, scrollable
│ [Creative] [Business] [Social]      │
│ [Lifestyle] [Finance] [Fun]         │
│                                     │
│ ┌─────────────────────────────────┐ │ ← Public Figure (accent-highlighted)
│ │ [👤] Public Figure           > │ │
│ │      Create an agent inspired   │ │
│ │      by a well-known personality│ │
│ └─────────────────────────────────┘ │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [🖥] Code Architect          > │ │
│ │      Your senior dev on call    │ │
│ └─────────────────────────────────┘ │
│   ... (list continues)              │
│                                     │
│ ┌─────────────────────────────────┐ │ ← Start from Scratch (accent, bottom)
│ │ [+] Start from Scratch       > │ │
│ │     Build a custom agent with   │ │
│ │     your own personality & role │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Filter chips:** Horizontal scrollable row. "All" selected by default (filled/accent). Tapping a category filters the list. Active chip = accent border + accent text. Inactive = muted bg, secondary text.

**Public Figure row:** Always pinned at top regardless of filter. Distinct visual treatment — darker green-tinted bg in Aight; Polly uses a subtle `accent/10` background tint.

**Start from Scratch:** Always pinned at bottom regardless of filter.

**Template list items:**
- Icon on dark rounded-square badge (emoji or rendered image, 44pt)
- Template name (semibold, 16pt)
- Tagline (muted, 13pt, max 2 lines)
- Chevron right

**Templates are bundled client-side** — not fetched from any server. They are static SOUL.md templates included in the app bundle. See `src/data/agentTemplates.ts`.

**On template tap → Agent Customization screen:**
1. Template name pre-filled (editable)
2. Template emoji pre-filled (tappable to change)
3. Personality text pre-filled from template (editable multiline)
4. Model selector (lists available configured models)
5. Username auto-generated from name (editable)
6. "Create Agent" button → `config.patch` RPC to gateway → navigate to new agent chat

**SOUL.md assembly:** The generated `SOUL.md` is not just the personality text the user sees. At creation time, the app assembles the final file as:

```
[personality text — from template or user-written]

---

[Standard SOUL Baseline — injected by app, always appended]
```

The Standard SOUL Baseline (defined in `POLLY_AGENT_TEMPLATES.md`) contains four universal blocks: Session Startup (read memory + USER.md on first message), Context Management (compress at ~80 messages, announce, write to memory), Blockers & Honesty (escalate immediately, never work around blockers silently), and Memory Writes (persist durable facts to daily memory file).

This assembly happens for **every agent** — template-based, Public Figure, and Start from Scratch. The user never sees or edits the baseline blocks in the creation flow. They are always present in the final SOUL.md on the gateway. If the user later edits the agent's personality via the Agent Detail View (§4.7.3), the baseline blocks are preserved at the bottom of the file.

**Public Figure flow:** Opens a text field — "Who do you want to recreate?" → enters name → triggers `[PUBLIC_FIGURE_AGENT]` protocol (sub-agent spawned to research + create, per system prompt instructions).

**Start from Scratch:** Opens same customization screen with empty fields.

#### 4.7.2 Polly Template Library

Polly ships its own curated template library — not Aight's generic list verbatim. The full template definitions (name, emoji, tagline, SOUL.md personality text, category) live in:

`~/polly/POLLY_AGENT_TEMPLATES.md` *(to be authored separately)*

**Polly template design principles:**
- Fewer total templates than Aight (~30 vs 60+), but each one is more opinionated and better-written
- Personality text reflects Polly's constitutional epistemology layer (material-first thinking, cui bono awareness, anti-scapegoating)
- Finance templates de-emphasized — the Wall Street archetype parade is not Polly's aesthetic
- Technical templates kept and sharpened — these match the primary user
- Categories simplified: Technical · Creative · Knowledge · Personal · Fun
- Each template tagline is a complete thought, not a marketing fragment

#### 4.7.3 Agent Detail View

Tapping an agent row from the agent list navigates to the agent detail view.

```
┌─────────────────────────────────────┐
│ [<]                          [Edit] │
│                                     │
│  Code Architect                     │  ← large title
│                                     │
│  [Overview] [Files] [Tools]         │  ← tab strip (horizontal scroll)
│  [Skills] [Channels] [Cron]         │
│                                     │
│  IDENTITY                           │  ← small-caps section header
│  ┌───────────────────────────────┐  │
│  │ Display Name   Code Architect │  │
│  ├───────────────────────────────┤  │
│  │ Username       @code_architect│  │
│  ├───────────────────────────────┤  │
│  │ Role                          │  │
│  │ Writes, debugs, and reviews   │  │
│  │ code across languages...      │  │
│  ├───────────────────────────────┤  │
│  │ Personality                   │  │
│  │ You are The Code Architect —  │  │
│  │ a senior engineer who writes  │  │
│  │ clean code...                 │  │
│  ├───────────────────────────────┤  │
│  │ Model          Claude Sonnet  │  │
│  ├───────────────────────────────┤  │
│  │ Emoji                      🖥 │  │
│  ├───────────────────────────────┤  │
│  │ Color                      🔴 │  │
│  ├───────────────────────────────┤  │
│  │ Voice                 Default │  │
│  └───────────────────────────────┘  │
│                                     │
│  CONFIGURATION                      │
│  ...                                │
└─────────────────────────────────────┘
```

**Tab strip:**
- Horizontally scrollable, 6 tabs: **Overview · Files · Tools · Skills · Channels · Cron**
- Active: Polly accent filled pill (`#f0903b`). Inactive: dark muted pill.
- Overview is default on open

**[Edit] button:**
- Top-right, pill style (like back button)
- Tapping makes IDENTITY card fields editable inline
- In edit mode: text fields for Display Name, Username, Role, Personality; pickers for Model, Emoji, Color, Voice
- Save/Cancel appears in nav bar

**IDENTITY card fields:**
| Field | Type | Notes |
|---|---|---|
| Display Name | text | shown in UI everywhere |
| Username | text | `@handle`, kebab-case |
| Role | multiline text | short description, shown in agent list subtitle |
| Personality | multiline text | SOUL.md content — the full persona prompt |
| Model | picker | selects from configured providers |
| Emoji | emoji picker | single emoji, renders on dark badge |
| Color | color picker | circle swatch, used for agent accent throughout UI |
| Voice | picker | ElevenLabs voice or "Default" |

**Tab contents:**

- **Overview:** Identity card + Configuration card. The **Personality** field is the agent's SOUL.md content — editing it and saving writes to `SOUL.md` on the gateway. Caption shown below the field: *"This becomes the agent's SOUL.md — the core personality prompt that defines who they are."* This is the mobile-friendly editor for persona; the Files tab shows the same content as a raw file.
- **Files:** Read-only file viewer. Lists all workspace files: AGENTS.md · SOUL.md · TOOLS.md · IDENTITY.md · USER.md · HEARTBEAT.md · BOOTSTRAP.md · MEMORY.md. Each row shows filename + file size + chevron. Tap → rendered markdown view of that file. **MEMORY.md** shows a `MISSING` badge (amber outlined pill) when the file doesn't exist yet — tapping it offers "Create Memory File" (sends a message to the agent prompting it to initialize its memory). **"Delete Agent"** button at the bottom of the Files tab — red text + trash icon, destructive, requires confirmation.
- **Tools:** List of tools/functions available to this agent (from gateway `agents.tools` RPC)
- **Skills:** Installed skills (e.g., Moltbook skill.md) — install new skills from URL
- **Channels:** Sessions/conversations this agent participates in
- **Cron:** Scheduled jobs this agent runs — list with schedule, last run, next run, enable/disable toggle

**The Personality ↔ SOUL.md relationship:**
- Personality field (Overview, editable) and SOUL.md (Files, read-only) are the same content
- Mobile editor → approachable, structured textarea, saves via `config.patch`
- File viewer → transparency layer, shows exactly what's running on the gateway
- Deep edits with full markdown control are done at the gateway directly; the iOS editor handles the common case

**Files tab (important for Polly):**
- Shows all files in agent's workspace directory with file sizes
- Rendered markdown view on tap (uses `MarkdownRenderer` component) — not raw text
- MEMORY.md is the key file — shows what the agent knows/remembers
- MEMORY.md `MISSING` state: show amber `MISSING` pill + "Create Memory File" action
- Read-only — editing happens via the Overview Personality field or at the gateway directly
- **Delete Agent** at bottom: destructive action, confirmation required, removes agent from gateway config

---

### 4.8 Settings View

**Purpose:** Configure everything about Polly — gateway, models, voice, integrations, security.

**Layout:**
```
┌─────────────────────────────────────┐
│ [<]                                 │
│                                     │
│  Settings                           │  ← large title
│                                     │
│  ┌───────────────────────────────┐  │
│  │ [⚙] Models                 > │  │
│  ├───────────────────────────────┤  │
│  │ [🎙] Voice                  > │  │
│  ├───────────────────────────────┤  │
│  │ [⊞] Preferences             > │  │
│  ├───────────────────────────────┤  │
│  │ [🔑] API Keys               > │  │
│  ├───────────────────────────────┤  │
│  │ [🌐] Your Gateway           > │  │
│  ├───────────────────────────────┤  │
│  │ [🔔] Notifications          > │  │
│  ├───────────────────────────────┤  │
│  │ [🛡] Security               > │  │
│  ├───────────────────────────────┤  │
│  │ [?] Help                    > │  │
│  ├───────────────────────────────┤  │
│  │ [🔒] Data & Privacy         > │  │
│  ├───────────────────────────────┤  │
│  │ [ℹ] About           v1.0.0  > │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Layout rules:**
- Single grouped card, full-width, 12pt radius
- Hairline dividers between rows
- Row icon: Lucide icon on dark rounded-square badge (~32pt), Polly accent color (`#f0903b`)
- Row label: semibold, white
- Right side: chevron `>` for all rows; About shows version string inline left of chevron

**Row destinations:**

**Models →**
- Provider-grouped cards (one card per configured provider)
- Each card: provider header row (letter-badge icon + provider name) with model list below
- Selected model row: highlighted bg + accent checkmark right-aligned
- Ollama models labeled "Local model" below name
- Subtitle: "Select the AI model your default agent uses. You can set per-agent models in the agent editor."
- Tap a model row to select it as default

**Voice →**
- Subtitle: "Switching voice here updates the active agent's default. All new voice sessions will use the selected voice."
- Info banner when using on-device TTS: "Using on-device voice model. No API key needed."
- **Voice** row → voice picker (shows current voice name e.g. "Soprano" as right detail)
- **STT Language** row → language picker (default: "English (US)")
- **Voice Input Style** segmented control: `Push to Talk` | `Conversational`
  - Push to Talk: "Hold to talk, release to send"
  - Conversational: continuous listening mode

**Preferences →**
- **LANGUAGE** section: Language row → system language picker (default: "System Default")
- **SWIPE RIGHT SCREEN** section: Right panel segmented control → `Voice` | `Shortcuts`
  - This controls what appears when user swipes right from the chat surface (alternative to drawer open — swipe LEFT opens drawer, swipe RIGHT opens this panel)
  - Default: Voice
- **FEATURES** section: Feature enable/disable toggles with descriptive subtitles:
  - Today — "Personal assistant with tasks & reminders"
  - Shortcuts — "One-tap shortcut cards for common messages"
  - Usage — "Token usage & cost dashboard"
  - Moltbook — "Moltbook journal"
  - Group Chats — "Create named group chats with selected agents" *(Phase 2)*
  - Public Figure Agents — "Create agents based on public figures via AI research"
  - Group Chat Thinking Toast — "Show a floating indicator when agents are thinking in group chats" *(Phase 2)*
- **NOTIFICATIONS** section: Push Notifications master toggle
- **PRIVACY section: OMITTED IN POLLY** — Aight has Analytics + Error Reporting phone-home toggles. Polly is fully self-hosted, no analytics, no crash reporting to any third party. This section does not exist in Polly's Preferences.

**API Keys →**
- Subtitle: "X/Y configured. Add API keys to unlock features."
- **MODEL PROVIDERS (X/11)** section: one row per provider with brand icon, name, model list subtitle, status badge ("Set" outlined pill if unconfigured, ✓ filled if configured) + chevron
  - Providers: Anthropic · OpenAI · Google AI · Groq · Mistral AI · xAI · DeepSeek · Moonshot (Kimi) · MiniMax · Qwen · OpenRouter
- **INTEGRATIONS (X/5)** section:
  - Brave Search API — "Real-time web search, fact-checking"
  - ElevenLabs — "Premium text-to-speech, voices"
  - Google Workspace — "Gmail, Google Calendar, Drive, Contacts"
  - Notion API — "Create and manage Notion pages, databases, and blocks"
  - Exa Search API — "Neural/semantic search, deep research"
- All keys forwarded to gateway via `config.set` on save; purged from local storage

**Your Gateway →**
- **STATUS** section (card):
  - Version · Protocol · Host · Uptime · Status (pill: "Connected" accent-outlined) · Method ("Manual")
  - "Restart Gateway" button — full-width, muted style
- **SYSTEM HEALTH** section (card): Memory (used/total GB, red when near full), CPU (%, green), Disk (used/total GB, lime) — color-coded progress bars
- **CONNECTION** section (card):
  - Gateway URL field (editable text input, shows `wss://your.domain`)
  - Auth Token field (password input, eyeball toggle to reveal)
  - "The gateway token you set during OpenClaw setup. Required for authentication."
  - "Disconnect" button — full-width, muted/destructive style

**Notifications →**
- Master "All" toggle at top (own card): "Turn off to silence all notifications"
- **CATEGORIES** card:
  - Agent Replies — "Responses from your AI agents"
  - Group Chats — "Messages in group conversations" *(Phase 2)*
  - Cron Jobs — "Background scheduled tasks and automations" (default: OFF)
- No per-agent toggles — category-level only

**Security →**

> ✅ **@security_audit** — Polly-specific Security screen spec added March 24, 2026

**Section 1 — AUTHENTICATION card:**
- **App Lock (Face ID / Touch ID)** toggle — "Require Face ID or Touch ID to open Polly"
  - When enabled: `expo-local-authentication` prompt on every foreground resume
  - Sub-row (visible when enabled): **Session Timeout** → picker: Never / 5 min / 15 min / 1 hour
    - "How long before Polly re-locks when idle"
    - Stored in MMKV `"polly.security.sessionTimeoutMs"`

**Section 2 — DEVICES card:**
- Header: "Registered Devices" with count badge (e.g. "2 of 10")
- One row per registered device:
  - Left: device name (e.g. "iPhone 15 Pro") + `deviceId` prefix (first 8 chars, monospace, secondary color)
  - Right: registration date (relative, e.g. "3 days ago") + chevron
  - Tap → device detail: full `deviceId`, registration date, last seen, "Remove Device" destructive button
- "This Device" label on current device row (no remove option)
- Max 10 devices enforced (§8.6 M2) — when at cap, add button disabled with "Device limit reached" tooltip
- Empty state: "Only this device is registered"

**Section 3 — GATEWAY SECURITY card:**
- **TLS Certificate** row — shows current TOFU fingerprint status:
  - "Verified — [first 16 chars of fingerprint]" with green indicator when pinned
  - "Not verified" with amber indicator when not pinned
  - Tap → Certificate Detail sheet: full fingerprint, pinned date, "Re-verify" button (clears pin + triggers new TOFU flow on next connect), "Trust Manually" if user wants to accept new cert
- **Connection Path** row — "Local / Cloudflare / Tailscale" — read-only current path indicator

**Section 4 — SECURITY CHECK card:**
- **Security Check** row → Security Check sub-view
  - "Test your defenses" card → runs automated probes
  - **CONFIGURATION** section: summary row (e.g. "🟡 2 Medium · ✅ 4 Passed")
  - Expandable finding cards with severity badges: MEDIUM (amber), HIGH (red), PASSED (green)
  - Finding examples: "Logs may contain sensitive data" / "Model may lack safety features"
  - "4 Passed" collapsible row
  - "Last scanned: [timestamp]"
  - "Re-Scan" button — full-width

**`dangerouslyDisableDeviceAuth` — compile-time flag only.**
This flag is never surfaced in the Security UI, Settings, or any runtime toggle. It exists only as a compile-time constant for development/testing. Any UI that would expose it is explicitly forbidden. Cross-reference: §8.1.

**Help →**
- Search bar: "Search help..."
- **FREQUENTLY ASKED QUESTIONS** section: expandable accordion rows
  - "What is Polly?" / "How do I update the gateway?" / "How do I update the plugin?" / "Why am I not getting responses?"
- **FEATURES** section: expandable accordion rows — one per major feature (Chat, Teams, Multi-Session, Group Chats, Create Agents, Public Figure Agents, Today, Shortcuts, Notifications, Voice Mode, Usage) — doubles as in-app feature documentation

**About →**
- **APP** section: App Version (X.X.X (build)), Report a Bug →, Licenses (open source attributions) →
- **PLUGIN** section: Installed Version (gateway plugin version number)
- **DANGER ZONE** section: "Reset App" — red icon + red text + "Clear all data, credentials, and start fresh." → confirmation dialog before executing

**Data & Privacy →**
*(Polly-specific addition — not in Aight)*
- Subtitle: "Your data stays on your device and your gateway. Nothing is sent to Polly servers."
- **EXPORT** section:
  - **Chat History** → modal: choose date range (All / Last 30 days / Last 7 days) + format (Markdown / JSON) → generates file → iOS share sheet
  - **Agent Configurations** → exports all custom agent SOUL.md, IDENTITY.md as a `.zip` of YAML/markdown files → share sheet. Allows backup and portability.
  - **Shortcuts** → exports all saved shortcuts as JSON → share sheet
  - **Settings Backup** → exports all MMKV-stored preferences (mental models, domain config, theme, all toggles) as a single JSON bundle → share sheet
- **IMPORT** section:
  - **Restore Settings Backup** → file picker, accepts the JSON bundle from Settings Backup export above → overwrites current settings after confirmation
  - **Import Agent Configuration** → file picker, accepts `.zip` from Agent export → installs agents into gateway via Agents Files API (§3.15)
- **ABOUT YOUR DATA** section (static text rows, no chevrons):
  - "Conversations are stored only on your OpenClaw gateway"
  - "No analytics or crash data is sent anywhere"
  - "Your vault stays in Obsidian or Notion — Polly reads it but does not copy it"
  - "Deleting the app removes local app data only. Your gateway data is separate."

---

## 5. Design System

✅ **Complete — all design tokens below. Framework: React Native + Expo (TypeScript)**

> **⚠️ Deprecation Notice:** `~/polly/DESIGN_SYSTEM_iOS.md` is stale (SwiftUI/Swift references). **This section (§5) is the authoritative source for design tokens.** The SwiftUI file was written before the tech stack decision (December 2025) and has not been updated. Use the token values below; ignore any SwiftUI-specific syntax.

### 5.1 Colors

All colors below are specified as **hex values** and are framework-agnostic. In React Native, import or define these as string constants. In TypeScript/React Native with `StyleSheet`, define as:

```typescript
const colors = {
  // Accent (Polly Brand)
  accent:       '#f0903b',
  accentDim:    '#c84012',
  accentLight:  '#fff7ed',
  
  // Backgrounds (Dark Mode — primary app experience)
  bgPrimary:    '#020617',
  bgSecondary:  '#0c1323',
  bgBorder:     '#1e2b48',
  
  // Text (Dark Mode)
  textPrimary:   '#f8fafc',
  textSecondary: '#b5c1ce',
  
  // Semantic
  success: '#22c55e',
  error:   '#ef4444',
  warning: '#eab308',
  info:    '#2563eb',
  
  // Domain Colors
  sigils:  '#2563eb',  // Code (blue)
  signals: '#ad48dd',  // Audio (purple)
  scrolls: '#22c55e',  // Writing (green) — WCAG AA compliant on dark bg
  glyphs:  '#eab308',  // Design (gold)
  grids:   '#16a399',  // Systems (teal)
};
```

**Color rationale:**
- **Dark mode** is the primary app experience (§18 App Constitution: "designed for low-light usage")
- **Accent orange `#f0903b`** is Polly's distinctive brand color — distinct from Aight's lime
- **Domain colors** are semantically mapped to agent domains (Code → blue, Audio → purple, etc.) for visual scanning in group chats and agent selection screens
- **`scrolls` green `#22c55e`** updated from `#16a34a` for WCAG AA contrast compliance on dark backgrounds

### 5.2 Typography

**Fonts:**
- **Body/UI text:** System font (SF Pro on iOS, Roboto on Android) — use default `fontFamily: undefined` in React Native
- **Monospace (code blocks):** SF Mono on iOS, Courier New fallback on Android — set `fontFamily: 'monospace'` or `fontFamily: Platform.select({ ios: 'Menlo', android: 'monospace' })`

**Scale (React Native / Expo):**

Use Expo `expo-font` for dynamic type + accessibility scaling:

```typescript
const typography = {
  largeTitle:    { fontSize: 34, fontWeight: '700', lineHeight: 41 },  // Screen headers
  title1:        { fontSize: 28, fontWeight: '700', lineHeight: 34 },  // Section headers
  title2:        { fontSize: 22, fontWeight: '700', lineHeight: 26 },  // Subsections
  title3:        { fontSize: 20, fontWeight: '600', lineHeight: 24 },  // Card headers
  headline:      { fontSize: 17, fontWeight: '600', lineHeight: 22 },  // Component labels
  body:          { fontSize: 17, fontWeight: '400', lineHeight: 22 },  // Body text (default)
  callout:       { fontSize: 16, fontWeight: '500', lineHeight: 21 },  // Emphasized body
  subheadline:   { fontSize: 15, fontWeight: '600', lineHeight: 20 },  // Input labels
  footnote:      { fontSize: 13, fontWeight: '400', lineHeight: 18 },  // Metadata, captions
  caption1:      { fontSize: 12, fontWeight: '500', lineHeight: 16 },  // Small labels
  caption2:      { fontSize: 11, fontWeight: '400', lineHeight: 13 },  // Smallest text
};
```

**Accessibility:** Always use `allowFontScaling={true}` on `<Text>` components. Respect user's system font size setting (enabled by default in Expo).

### 5.3 Spacing

**Base unit:** 4pt (logical pixels)

```typescript
const spacing = {
  spacing1: 4,
  spacing2: 8,
  spacing3: 12,
  spacing4: 16,
  spacing6: 24,
  spacing8: 32,
};
```

**Constraints:**
- **Minimum touch target:** 44pt × 44pt (Apple HIG)
- **List row height (standard):** 56pt (44pt touch target + 12pt vertical padding)
- **List row height (compact):** 52pt
- **Safe areas:** Always use `useSafeAreaInsets()` from `react-native-safe-area-context` to respect notch, home indicator, Dynamic Island

### 5.4 Key Design Rules

1. **Navigation:** Bottom tab bar for primary navigation (thumb-reachable on larger screens). Drawer navigation for secondary views (Vault Search, Moltbook, Settings).
2. **Gestures:** 
   - Swipe left/right on list rows for actions (done, cancel, delete)
   - Long-press for context menus (never right-click)
   - Pull-to-refresh for live data views (ChatView, Today View)
   - Swipe down to dismiss modals/sheets
3. **Color:** Orange accent (`#f0903b`) for all primary CTAs, success states, and visual emphasis
4. **Status bar:** Always visible; do NOT hide or tint
5. **Offline state:** Always communicated via connection dot or banner; never silent failure
6. **Keyboard:** Always dismiss when user taps outside the input field; don't overlay content

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

**Library:** `marked` (JS markdown parser) + custom React Native renderer built on `Text` and `View` primitives.

> **Note:** The original spec referenced `react-native-enriched-markdown` from the Aight codebase. This package is Aight-proprietary and not available on public npm. Polly builds its own `PollyMarkdown` renderer using `marked` for parsing and a custom component tree for rendering. This is a one-time build cost (~2–3 days) and gives Polly full control over styling, streaming behavior, and @mention rendering.
>
> Alternative if build time is constrained: `react-native-markdown-display` (public, actively maintained, supports custom renderers). The Polly design system tokens slot directly into its `styles` prop. Use this for Phase 1, migrate to custom renderer in Phase 2 if needed.

```tsx
// Phase 1: react-native-markdown-display with Polly theme
import Markdown from 'react-native-markdown-display';

interface PollyMarkdownProps {
  content: string;
  isStreaming?: boolean;
}

const PollyMarkdown: React.FC<PollyMarkdownProps> = ({ content, isStreaming }) => (
  <Markdown
    style={pollyMarkdownStyles}
    onLinkPress={isStreaming ? () => false : handleLinkPress}
  >
    {content}
  </Markdown>
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

**@mention rendering** (group chat): when `isGroup: true`, post-process message text to detect `@username` patterns before passing to `PollyMarkdown` — replace with a custom inline `AgentMentionChip` component: agent's `identity.theme` color background, white text, 4pt corner radius. Pre-processing step, not a library extension.

---

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

**Purpose:** Emoji-on-dark-rounded-square avatar for an agent. Renders like an iOS app icon — NOT a circle, NOT bare emoji text.

```tsx
interface AgentAvatarProps {
  emoji: string;
  color?: string;               // agent.identity.theme (hex) — border tint; fallback: hash from agentId
  size: 32 | 40 | 44 | 56;     // pt — 44pt standard in lists
  showOnlineIndicator?: boolean;
}
```

**Visual — iOS app-icon style:**
- Shape: rounded square (corner radius = size × 0.22, matching iOS icon grid)
- Background: dark (`#0c1323` bgSecondary)
- Border: 1.5pt in agent `color` (`identity.theme` hex) when non-null — omit if null
- **Fallback** (when `identity.theme` is null): derive deterministic color from `agentId` hash — consistent across devices without server dependency
- Emoji: centered, fontSize = size × 0.55
- Do NOT render bare emoji — always on the dark rounded-square badge

**Agent `color` propagates throughout the UI** wherever agent identity surfaces:
- `AgentAvatar` border tint
- `DrawerPanel` session row left accent bar
- `AgentHeader` name (subtle tint)
- `GroupChatBubbleRow` attribution name color

**Online indicator** (when `showOnlineIndicator: true`):
- 10pt circle, success green, bottom-right corner
- 2pt white ring border separating dot from avatar

**Sizes:**
- 32pt — drawer session rows, small contexts
- 40pt — nav bar, `AgentHeader`
- 44pt — agent list rows (§4.7), `AgentSwitcherSheet`
- 56pt — agent detail view, onboarding

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

### 6.24 DrawerPanel

**Purpose:** The primary navigation surface. Slides in from the left over the chat view. Custom implementation — NOT `@react-navigation/drawer` (insufficient physics control).

```tsx
interface DrawerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  currentAgentId: string;
  currentWorkspace: string;
  recentSessions: SessionEntry[];      // TODAY section — recent chats
  agents: AgentSummary[];
  onSelectAgent: (agentId: string) => void;
  onSelectSession: (sessionKey: string) => void;
  onNewConversation: () => void;
  onNavigate: (dest: NavDestination) => void;
}

type NavDestination = 'agents' | 'today' | 'shortcuts' | 'usage' | 'moltbook' | 'settings';
```

**Layout (top to bottom):**
```
┌─────────────────────────┐
│  [+]          [✕]       │  ← header: new convo + close
│  ─────────────────────  │
│  [team ▾]          │  ← team selector
│  Agent: Strategist ▾    │  ← agent selector → AgentSwitcherSheet (§6.10)
│  ─────────────────────  │
│  TODAY ▾                │  ← collapsible recent sessions
│    🏠 Home — Now        │
│    ✨ Fresh Spec — 2m   │
│  ─────────────────────  │
│  [Agents]               │
│  [Today]                │
│  [Shortcuts]            │
│  [Usage]                │
│  [Moltbook]             │
│  [Settings]             │
└─────────────────────────┘
```

**Dimensions:** 80% screen width, max 320pt. Full height, safe area aware.

**Animation:**
- Open/close: `translateX` spring (`damping: 20, stiffness: 200`)
- Backdrop: `rgba(0,0,0,0.4)` full-screen `Pressable`, fades with drawer
- Swipe-right on chat surface → open (`PanGestureHandler`)
- Swipe-left on drawer / tap backdrop → close

**⚠️ Do NOT use `@react-navigation/drawer`** — use `Animated` + `PanGestureHandler` from `react-native-gesture-handler` directly for spring physics and parallax control.

**TODAY section:** `SessionEntry[]` **scoped to the active agent/group selection** — filtered by `agentId` (or `groupId` for group chats). If active selection is a solo agent, shows sessions where `sessionKey` matches `agent:<agentId>:*`. If active selection is a group (e.g., "Sigils"), shows:
- Individual sessions with each member agent (`agent:<memberId>:main`, etc.)
- Group chat sessions for that group (`agent:*:group-chat:<groupId>`)

Switching the agent selector in the drawer immediately re-filters TODAY. Sessions from other agents/groups are not shown — they're accessible from All Sessions (§4.1.5) with the group filter set to "All."

Sorted by `updatedAt` desc. Starred sessions pinned above. Limit: 10 rows; "All Sessions →" link for overflow.
- **Rename** — inline text edit on the row; `sessions.update` on confirm
- **Star / Unstar** — toggled star icon on row; stored in MMKV `"polly.starredSessions"` (array of session keys); starred sessions pinned to top of TODAY section with ★ prefix
- **Archive** — removes from TODAY section; session retained at gateway, accessible from All Sessions view (§4.1.5); uses `sessions.update` with `{ archived: true }`
- **Delete** — confirmation sheet: "Delete this conversation? This cannot be undone." → `sessions.delete` with `{ deleteTranscript: true }`; removed locally immediately, deletion sent to gateway

**TODAY section display limit:** Shows 10 most recent (unarchived, unstated sessions sorted by `updatedAt` + starred sessions pinned above). "All Sessions →" link at bottom of TODAY section opens the full session list view (§4.1.5).

#### 4.1.5 All Sessions View

Full-screen view accessed from "All Sessions →" in drawer TODAY section. Handles session accumulation for power users.

**Scoping:** Defaults to the currently-active agent/group (same scope as TODAY). A **"Group" filter chip row** at the top lets the user switch scope without going back to the drawer — tapping a different group/agent filters the list to that context. "All" chip shows sessions across all agents/groups.

**Layout:**
```
┌─────────────────────────────────────┐
│ [<]  All Conversations              │
│                                     │
│ [🔍 Search conversations...]        │
│                                     │
│ [Strategist] [Sigils] [All] [+more] │  ← agent/group scope chips (scrollable)
│ [All] [Starred ★] [Archived]        │  ← status filter chips
│                                     │
│ Today                               │  ← date section headers
│   ★ Polly Spec Review       [⋯]    │
│     Code Architect — 2h ago  [⋯]   │
│   ◎ Sigils group chat — 4h   [⋯]   │  ← group chat session (group icon)
│                                     │
│ Yesterday                           │
│   ...                               │
│                                     │
│ [Select]                            │  ← bulk mode toggle
└─────────────────────────────────────┘
```

- **Group/agent scope chips (top row):** One chip per configured agent + one per group. Scrollable horizontally. Active chip: filled accent background. "All" shows everything. Defaults to whatever was active in the drawer.
- **Status filter chips (second row):** All · Starred · Archived
- **Group chat rows:** Prefixed with ◎ icon + group name label (e.g., "Sigils group chat")
- **Search:** Client-side filter on session `title` + `agentName`; no server search in Phase 1
- **[⋯] per row:** Same context menu as long-press (Rename, Star, Archive, Delete)
- **Bulk mode:** Tap [Select] → checkboxes → "Archive Selected" / "Delete Selected" in bottom action bar
- **Date grouping:** Today / Yesterday / This Week / This Month / Older
- **Pagination:** 50 sessions at a time, infinite scroll via `sessions.list` with `agentId` filter + offset

**Nav links:** Colored square icon badge (28pt) + label. Active: `accent` tint. Tap → close drawer + navigate.

**Accessibility:**
```tsx
accessibilityViewIsModal={isOpen}   // traps focus when open
accessibilityLabel="Navigation panel"
// Nav links: accessibilityRole="menuitem"
```

### 6.25 WorkspacePill**Purpose:** Persistent workspace context selector shown in the nav bar top-right across all full-screen views (Agents, Today, Shortcuts, Usage, Moltbook, Settings). Single source of workspace truth.

```tsx
interface WorkspacePillProps {
  workspaceName: string;
  hasMultiple: boolean;         // shows ▾ chevron only if multiple workspaces exist
  onPress: () => void;          // no-op if single workspace; dropdown if multiple
}
```

**Visual:**
- Pill shape: `bgSecondary` fill, 16pt corner radius, 8pt H / 4pt V padding
- Text: workspace name, `.footnote` semibold, `textPrimary`
- Chevron `▾` right of text, only shown when `hasMultiple: true`
- Single workspace: tappable but shows "Manage workspaces in Settings" tooltip
- Multiple workspaces: dropdown action sheet listing workspaces → tap switches

**Placement:** Right `headerRight` slot in `expo-router` stack navigator header. Consistent across every non-chat full-screen view. Also present in `DrawerPanel` (§6.24) top section.

---

### 6.26 AgentDetailTabs
**Purpose:** The 6-tab configuration hub inside the agent detail view (§4.7.3). Horizontally scrollable tab strip with pill-style active indicator.

```tsx
type AgentTab = 'overview' | 'files' | 'tools' | 'skills' | 'channels' | 'cron';

interface AgentDetailTabsProps {
  agentId: string;
  agent: AgentSummary;
  activeTab: AgentTab;
  onTabChange: (tab: AgentTab) => void;
}
```

**Tab strip:**
- Horizontally scrollable, 6 tabs: Overview · Files · Tools · Skills · Channels · Cron
- Active tab: filled pill, agent `color` or `accent` if no color assigned
- Inactive tabs: dark muted pill, `textSecondary`
- Font: `.footnote` semibold
- Padding: 16pt H scroll inset, 8pt V, 12pt gap between pills

**Tab content panels:**

**Overview tab** — Identity + Configuration cards:
```
IDENTITY
  Display Name   Code Architect     [right-detail]
  Username       @code_architect    [right-detail]
  Role           [below-label, multiline]
  Personality    [below-label, multiline, truncated]
  Model          Claude Sonnet 4.6  [right-detail]
  Emoji          🖥                 [right-detail]
  Color          ● red swatch       [right-detail]
  Voice          Default            [right-detail]

CONFIGURATION
  [gateway config fields — model params, temperature, etc.]
```

- `[Edit]` button top-right nav bar → makes fields inline-editable
- Save → `config.patch` on gateway

**Files tab** — Agent file list:
- `MoltbookFileRow` (§6.17) for each file
- Files: `MEMORY.md`, `SOUL.md`, `IDENTITY.md`, etc.
- Tap → full-screen markdown viewer with edit capability
- This is where MEMORY.md lives — not a separate top-level view

**Tools tab** — Tool enable/disable toggles:
- Each tool the agent has access to (from gateway `agents.list` tool config)
- Toggle row: tool name + description + `Switch`
- Changes call `config.patch`

**Skills tab** — Installed skills + install from URL:
- List of installed skills with enable/disable
- "Install from URL" button at bottom → text field + Install
- Used for Moltbook skill install (Phase 2)

**Channels tab** — Session/channel configuration:
- Which group chats this agent participates in
- Channel assignment toggles

**Cron tab** — Agent's scheduled jobs:
- `TodayItemCard` list (§6.13) filtered to this agent's jobs
- `[+]` button → `AddReminderSheet` (§6.15) pre-scoped to this agent's session key

---

### 6.27 AgentTypingIndicator

**Purpose:** Per-agent "thinking" row shown in group chat when an agent has been triggered but hasn't emitted a first token yet. Distinct from `StreamingCursor` (which lives inside a bubble) — this appears as a standalone row in the message list before the agent's bubble exists.

**When to show:** In a `GroupChatView` (`isGroup: true`), when a `chat` event arrives with `state: "delta"` for a `runId` that has no existing `UIMessage` in the list yet — show this row until the first content token arrives, then replace it with `GroupChatBubbleRow`.

```tsx
interface AgentTypingIndicatorProps {
  agent: AgentSummary;    // emoji, name, identity.theme color
}
```

**Visual:**
```
🖥  Code Architect is thinking...   ●●● (pulsing dots)
```

- `AgentAvatar` (32pt, §6.11) left
- Agent name in agent's `identity.theme` color (or fallback hash color)
- "is thinking..." text in secondary color, italic, footnote
- Three pulsing dots animation (staggered opacity, 400ms cycle)
- Left-aligned, same inset as `GroupChatBubbleRow` attribution row
- Appears/disappears with a short fade (150ms)

**Implementation note:** Managed in the `GroupChatView` message list alongside `UIMessage[]`. Maintain a separate `Set<runId>` of "pending agents" — add on first `delta` event with no existing message, remove when the message materialises.

---

> ✅ **@infra** — documented March 23, 2026

---

### 7.1 Overview — Multi-Path Architecture

Polly must work in three network contexts:

| Context | Transport | Gateway Address | TLS | When Used |
|---|---|---|---|---|
| Home (local network) | Direct LAN | `ws://[lan-ip]:18789` | ❌ Not required — local perimeter trusted | On home WiFi |
| Remote (Tailscale) | WireGuard VPN | `ws://[tailscale-ip]:18789` | ❌ Not required — WireGuard encrypts the tunnel | Personal network, open WiFi |
| Remote (Cloudflare Tunnel) | HTTPS/WSS via CF | `wss://[subdomain].trycloudflare.com` | ✅ Required — internet path, no perimeter | Work networks, restricted environments |

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
- Today items (triggers, tasks, processes) cached via **`expo-sqlite`** on every fetch
- Last-known agent list cached to MMKV (`"polly.agentList"`)
- Chat history: last 100 messages per session cached to `expo-sqlite`
- Cache TTL: 24 hours

**Persistence layer: `expo-sqlite` (SQLite via Expo)**
- Chosen over CoreData (Swift-only, no RN support), WatermelonDB (heavy, overkill for Phase 1), and raw MMKV (no relational queries)
- Schema:

```sql
-- Sessions
CREATE TABLE sessions (
  session_key TEXT PRIMARY KEY,
  agent_id TEXT NOT NULL,
  title TEXT,
  last_message_at INTEGER,  -- Unix ms
  cached_at INTEGER          -- Unix ms
);

-- Messages (per session)
CREATE TABLE messages (
  id TEXT PRIMARY KEY,       -- runId or client-generated UUID
  session_key TEXT NOT NULL,
  role TEXT NOT NULL,        -- 'user' | 'assistant'
  content_json TEXT NOT NULL, -- JSON-serialized ChatMessageContent[]
  created_at INTEGER,
  FOREIGN KEY (session_key) REFERENCES sessions(session_key)
);

-- Today items (cron jobs, tasks, triggers)
CREATE TABLE today_items (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,        -- 'trigger' | 'item' | 'process'
  payload_json TEXT NOT NULL,
  cached_at INTEGER
);
```

**Sync/reconciliation on reconnect:**
1. App reconnects → sends `chat.history` RPC for each recently-active session (last 7 days)
2. Server response is authoritative — overwrites local cache for returned sessions
3. Sessions not in server response retain local cache until TTL expires
4. Messages written locally during offline period are queued in MMKV (`"polly.offlineQueue"`) — replayed as WS sends on reconnect in order, then local copies replaced with server-echoed versions

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

> **Serialization security (@security_audit G3):** `GatewayConfig` is `Codable` for in-memory use only. It must **never be written to disk as a struct** (no `JSONEncoder` → `UserDefaults`, no plist write, no file write). Each field has an explicit persistence target below — violating these mappings is a security defect.

```swift
struct GatewayConfig: Codable {
    var localAddress: String            // e.g. "192.168.1.42:18789"
    // Persistence: UserDefaults ("polly.gateway.localAddress") — non-sensitive
    
    var cloudflareUrl: String           // e.g. "wss://gateway.yourdomain.com"
    // Persistence: Keychain ("polly.gateway.cloudflareUrl") — sensitive; anyone with this URL can reach gateway
    
    var cloudflareEnabled: Bool         // default: true if URL is set
    // Persistence: UserDefaults — non-sensitive
    
    var tailscaleAddress: String        // e.g. "100.x.x.x:18789"
    // Persistence: UserDefaults — non-sensitive (no auth value)
    
    var tailscaleEnabled: Bool          // default: false until configured
    // Persistence: UserDefaults — non-sensitive
    
    var preferredRemotePath: RemotePath // .cloudflare | .tailscale | .auto
    // Persistence: UserDefaults — non-sensitive
    
    var preferLocal: Bool               // default: true
    // Persistence: UserDefaults — non-sensitive
    
    var connectionTimeout: Int          // seconds, default: 2
    // Persistence: UserDefaults — non-sensitive

    // The following are NEVER fields in this struct on disk:
    // authToken → Keychain "polly.gateway.token"
    // deviceId → Keychain "polly.device.id"
    // devicePrivateKey → Keychain "polly.device.privateKey"
}

enum RemotePath: String, Codable {
    case cloudflare
    case tailscale
    case auto   // try both, use whichever connects first
}

#### config.patch Rollback & Last-Known-Good

If a `config.patch` call breaks the gateway connection (bad URL, invalid auth token, malformed config), the user is locked out with no way to recover from the app. Mitigation:

**Before every `config.patch` call from Settings:**
1. Read current config snapshot via `config.get`
2. Store snapshot in MMKV `"polly.config.lastKnownGood"` (JSON string) with timestamp
3. Attempt the `config.patch`
4. If the subsequent connection test fails (no WS connect within 5s), auto-restore from `lastKnownGood` via another `config.patch`

**Recovery UI:**
- If auto-restore succeeds: toast "Settings change failed — restored previous configuration"
- If auto-restore also fails (gateway unreachable): show "Gateway Unreachable" screen with:
  - Last known good config displayed (read-only)
  - "Try Last Good Config" button — attempts `config.patch` with stored snapshot
  - "Manual Reset" button — clears all gateway config, returns to onboarding connection screen

**MMKV key:** `"polly.config.lastKnownGood"` — stores full `config.get` response JSON. Overwritten on every successful `config.patch`. Never cleared except on "Manual Reset."

**Scope:** Any Settings change that calls `config.patch` — gateway URL, auth token, model configuration, agent config updates. Does NOT apply to MMKV-only settings (theme, mental models, notification prefs).
```

---

### 7.10 Open Infra Questions & Decisions

1. **TLS for local (RESOLVED — @security_audit B2):** LAN connections (`ws://`) are permitted without TLS. Rationale: traffic is local-network only, not exposed to the internet, and iOS rejects self-signed certs by default without custom trust anchor configuration that adds significant setup friction. **Decision: `ws://` is acceptable for LAN and Tailscale (WireGuard-encrypted tunnel). `wss://` is required for all Cloudflare Tunnel connections.** §7.1 and §8.3 are authoritative on their respective paths. §8.3's "WSS required everywhere" applies only to internet-path connections. The security model is: trust the network perimeter for LAN/WireGuard; enforce TLS where the perimeter is the open internet.
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

#### ⚠️ Known Vulnerability in OpenClaw — Must Fix Before Push Ships
**`aight.push.register` is currently unauthenticated.** Any client that can reach the gateway WS can register arbitrary push tokens under any `deviceId`. This is a pre-production blocker for push notifications (Phase 2). Does not block Phase 1.

**Gateway fix (required — @backend owns):**
- Gateway `aight.push.register` handler must extract `deviceId` from the **authenticated WS session context**, not from the client-supplied parameter
- If client-supplied `deviceId` doesn't match session's authenticated `deviceId` → reject with `DEVICE_ID_MISMATCH` error, close connection
- `deviceId` derivation is already deterministic (`SHA-256(publicKeyBytes)` hex) — gateway has everything needed from the auth handshake
- *"Gateway validates that `deviceId` in registration request matches the authenticated session's `deviceId`. Mismatch → `DEVICE_ID_MISMATCH` rejection. Client-supplied `deviceId` is never trusted."*

**iOS client fix (belt-and-suspenders):**
- Before sending `aight.push.register`, assert that the `deviceId` being sent matches the locally-derived identity (`SHA-256(publicKey)`)
- On receiving `DEVICE_ID_MISMATCH` error: log security event, surface in Settings → Security, do not retry automatically
- This is a client-side sanity check only — the security boundary is gateway-side validation

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
3. **M3 — deviceToken TTL (@security_audit G2):** The gateway currently has no server-side `deviceToken` expiry. Tokens are valid until manually revoked. This is a gap — a stolen or leaked token grants permanent access.
   - **Gateway fix:** Store `registeredAt` timestamp alongside each `deviceToken`. Enforce 30-day TTL on gateway — reject tokens older than 30 days with `TOKEN_EXPIRED` error.
   - **iOS client behavior:** On `TOKEN_EXPIRED` response, trigger silent re-auth: generate a new challenge response using the device's existing Ed25519 keypair and re-register. If re-auth fails (key mismatch, device deregistered), surface "Please re-pair your device" screen in Settings.
   - **Rotation on reconnect:** Each successful WS auth refreshes the TTL. Devices that haven't connected in 30 days require re-pairing. This is intentional — it prunes abandoned device registrations.
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
- **Device management in Settings → Security:** List registered devices with name, `deviceId` prefix, registration date. Allow removal (enforces 10-device cap from §8.6 M2). Cross-reference: §4.8 Security → "Registered Devices".
- **Biometric lock:** `expo-local-authentication` toggle in Settings → Security. When enabled, require Face ID / Touch ID on app open and before accessing Security settings sub-screens. Cross-reference: §4.8 Security → "Biometric lock".
- **Session timeout:** Idle timeout before biometric re-auth required. Options: Never / 5m / 15m / 1h. Cross-reference: §4.8 Security → "Session timeout".
- **Token expiry handling:** Silent re-auth on `deviceToken` expiry — user should never see an auth error during normal use.
- **`expo-secure-store` loss (device restore):** If secure store is wiped (new device, restore from backup to new hardware), detect missing keys on launch → full re-pair flow.
- **Sign-out:** Call `SecureStore.deleteItemAsync` for all keys (`sendKey`, `deviceToken`, `privateKey`, tunnel URLs) and call `aight.push.unregister`.
- **`dangerouslyDisableDeviceAuth`:** Never exposed in Settings UI or any runtime toggle. Compile-time only. Cross-reference: §4.8 Security (explicit "not exposed" note).

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

These differentiate Polly from being a straight Aight clone. All features in this section are implemented **client-side only** or via the OpenClaw WebSocket — no direct Polly REST API calls from iOS.

> **§11 scope clarification (@researcher B-R2):** "Client-side only" means no direct iOS→Polly REST API calls. It does NOT mean zero server involvement. §11.5 (Quick Capture) writes to the Obsidian vault via iCloud filesystem — that's local, not a server call. §19.5 (theme behavior injection) modifies the agent's system prompt on the gateway — that's a gateway write via `agents.update`. Neither contradicts the "no direct Polly REST API" principle. The constraint is specifically about the legacy Python backend; OpenClaw gateway calls are always in scope.

### 11.0 The PollyEnhancement Layer

The PollyEnhancement Layer is a **synchronous message preprocessor**. No async operations, no network calls, no loading state. It runs at `chatSend()` time, immediately before the WebSocket write.

```typescript
interface AugmentationContext {
  vaultNote?: { path: string; content: string };
  mentalModel?: { id: string; prompt_injection: string };
  domainTag?: { id: string; label: string };          // Phase 5+ only
  themeFraming?: string;                              // injected by §19.5 into system prompt, NOT message
}

function augmentMessage(text: string, ctx: AugmentationContext): string {
  const parts: string[] = [];
  if (ctx.vaultNote) {
    parts.push(`<context file="${ctx.vaultNote.path}">\n${ctx.vaultNote.content}\n</context>`);
  }
  if (ctx.mentalModel) {
    parts.push(`<framing>${ctx.mentalModel.prompt_injection}</framing>`);
  }
  // domainTag and themeFraming are NOT injected here — see stacking rules below
  parts.push(text);
  return parts.join('\n\n');
}
```

#### Context Stacking Rules (@researcher B-R1)

Multiple injection sources can be active simultaneously. Priority order and behavior when they stack:

| Source | Where injected | User-visible pill | Stackable? |
|--------|---------------|-------------------|------------|
| Vault note (§11.1) | Message prefix (`<context>` block) | 📄 filename pill | Yes — one note per message |
| Mental model (§11.3) | Message prefix (`<framing>` block) | 🧠 model name pill | Yes — one model per message |
| Domain badge (§11.2) | Label only — not injected into message (Phase 1) | Colored domain pill | N/A — display only |
| Theme behavior (§19.5) | Agent system prompt via `agents.update` — NOT the message | No pill (transparent) | Persistent, not per-message |

**Stacking behavior:**
- Vault note + mental model can both be active simultaneously. Both appear as pills. The augmented message is: `<context>` block + `<framing>` block + user text, in that order.
- Maximum one vault note per message. If user selects a second note, it replaces the first.
- Maximum one mental model per message. Selecting a second replaces the first.
- Theme behavior injection (§19.5) operates on the **system prompt**, not the message. It is always-on when a theme is active — it does not appear as a pill and does not stack with message-level injections. It is invisible to the user by design (see §19.5 disclosure note).
- Domain injection into messages is deferred to Phase 5. The domain badge is display-only in Phase 1–4.

**Total max augmentation on a single message:** one `<context>` block + one `<framing>` block + user text. Clean, bounded, predictable.

**Augmentation is always transparent to the user.** When context is attached to the next message, the input bar shows dismissible pills above the text field:

```
┌───────────────────────────────────────────┐
│ 📄 MEMORY.md  ✕     🧠 Inversion  ✕      │  ← AugmentationPill row
├───────────────────────────────────────────┤
│ [🎤] [Type a message...            ] [➤] │
└───────────────────────────────────────────┘
```

Each pill is tappable to remove before sending. After send, the augmentation context clears. No persistent injection — every message starts clean unless the user re-attaches context.

**`AugmentationContext` is stored in Zustand `chatStore.pendingAugmentation`** — cleared on send, cleared on agent switch. The pills row is conditionally rendered when `pendingAugmentation` is non-empty.

> **Pill count constraint (§11.0 canonical rule):** In Phase 1–4, the input bar augmentation row may contain at most two pills simultaneously: one vault note pill (§11.1) and one mental model pill (§11.3). Both are message-scoped and dismissible. Theme behavior injection (§19.5) does not surface a pill — it is applied gateway-side via `agents.update` and is not part of the client-side augmentation assembly. Domain awareness injection (§11.2), if implemented in Phase 5, must also surface as a dismissible pill following the same pattern.

**This is the model for Phase 1–5.** No Polly REST server, no agent-mediated retrieval round-trip, no two code paths. The vault is on the device; mental models are in MMKV. Augmentation is free, offline, instant.

---

#### PollyGatewayAdapter

The `PollyEnhancement Layer` cannot call `ChatEngine.send()` directly — `expo-openclaw-chat`'s `ChatEngine` is not designed to be subclassed, and its `send()` may be sealed. Polly wraps it in a **`PollyGatewayAdapter`** — a thin facade that owns all outgoing message calls.

```typescript
// src/services/PollyGatewayAdapter.ts

import { ChatEngine } from 'expo-openclaw-chat';
import { augmentMessage } from './PollyEnhancement';
import { useChatStore } from '../stores/chatStore';

export class PollyGatewayAdapter {
  private engine: ChatEngine;

  constructor(engine: ChatEngine) {
    this.engine = engine;
  }

  async send(text: string): Promise<void> {
    // 1. Pull pending augmentation context from Zustand store
    const ctx = useChatStore.getState().pendingAugmentation;

    // 2. Run PollyEnhancement Layer — synchronous, no await
    const augmented = augmentMessage(text, ctx ?? {});

    // 3. Clear augmentation context before send (not after — avoids double-send edge case)
    useChatStore.getState().clearAugmentation();

    // 4. Delegate to ChatEngine
    await this.engine.send(augmented);
  }

  // All other ChatEngine methods pass through directly
  get messages() { return this.engine.messages; }
  get isStreaming() { return this.engine.isStreaming; }
  // ... etc
}
```

**All send calls in the app go through `PollyGatewayAdapter.send()` — never `ChatEngine.send()` directly.** This is enforced by convention (ESLint rule: no direct `chatEngine.send` calls outside the adapter). The adapter is created once per session and stored in Zustand `chatStore.adapter`.

**If `ChatEngine.send()` changes signature in a future `expo-openclaw-chat` version:** the adapter is the only place that needs updating. The rest of the app is insulated.

### 11.1 Vault Context Injection
**Trigger:** User types `/` in chat input  
**Behavior:** Slide-up sheet shows Obsidian vault file browser → select note → note content prepended to message as a context block before sending  
**Implementation:** Polly accesses the vault via a security-scoped bookmark (see §11 Access Strategy — `expo-document-picker`). On `/` trigger, calls `startAccessingSecurityScopedResource()` on the stored bookmark, renders the file tree in a sheet, reads the selected note, then calls `stopAccessingSecurityScopedResource()`. Selected note text is wrapped in a `<context>` block and prepended to the outgoing message client-side via `augmentMessage()`. No server round-trip — the augmented message travels to OpenClaw as a single enriched user turn.

**Vault not connected:** If no bookmark is stored in `expo-secure-store`, the `/` sheet shows an empty state: "Connect your Obsidian vault in Settings → Vault to use note context." Tapping navigates to the vault connection screen.  
**Constraint:** Requires Obsidian iOS + iCloud sync. Vault path configured in Settings.

### 11.2 Domain Awareness Badge
**Behavior:** Shows a colored badge in the chat nav bar indicating which domain the current conversation is about. Purely cosmetic and informational — helps the user track context.  
**Implementation:** Client-side keyword classification on recent message text against a user-configurable list of domain names and keywords stored in app settings (MMKV). No server call needed. Default domains shown if user hasn't configured custom ones. Domain colors and icons are user-configured in Settings → Domains.  
**UX:** Tapping the badge opens a small sheet listing all configured domains; user can manually override the detected domain for the session.  
**Note:** This is a *labeling* feature — it doesn't change AI behavior unless the user explicitly sends a domain tag. Enhanced domain routing (auto-injecting domain context into messages) is a Phase 5 consideration once it's clear how OpenClaw agents should receive it.

### 11.3 Mental Model Selector
**Trigger:** Tap 🧠 icon in chat nav bar  
**Behavior:** Sheet shows a list of mental models. Tapping one injects a brief framing statement at the start of the next message.  
**Implementation:** Mental models are a short hardcoded list (client-side) with user-addable custom entries stored in MMKV. No server fetch. The selected model's `prompt_injection` text is prepended as context to the next outgoing message.  
**User additions:** Settings → Mental Models → Add custom

#### Default Mental Models (12)

Organized into four tiers. All are enabled by default; users can disable or reorder.

**Tier 1 — Core Philosophy**
| ID | Name | Prompt Injection (prepended to next message) |
|----|------|----------------------------------------------|
| `infinite_games` | Infinite Games | *"Approach this with an infinite game mindset: optimize for continuation, adaptation, and evolving the system — not for winning or closing."* |
| `instruments_over_tracks` | Instruments Over Tracks | *"Think in terms of tools and systems, not finished products. What flexible instrument could serve many purposes here?"* |
| `constraint_as_meaning` | Constraint as Meaning | *"Treat the constraints in this situation as generative, not limiting. What does the constraint make possible that freedom wouldn't?"* |

**Tier 2 — Learning & Thinking**
| ID | Name | Prompt Injection |
|----|------|-----------------|
| `freire_pedagogy` | Freire's Pedagogy | *"Approach this as a dialogue between equals working toward critical understanding — not as transmission from expert to student."* |
| `socratic_method` | Socratic Method | *"Guide toward understanding through questions rather than direct answers. Surface assumptions. Let the inquiry do the work."* |
| `reverse_engineering` | Reverse Engineering | *"Start from the desired end state and work backward. What would have to be true for this outcome to exist?"* |

**Tier 3 — Systems & Technical**
| ID | Name | Prompt Injection |
|----|------|-----------------|
| `systems_thinking` | Systems Thinking | *"Map the system: what are the nodes, the flows, the feedback loops, and the leverage points? Consider second-order effects."* |
| `first_principles` | First Principles | *"Strip away assumptions and analogies. What is undeniably true here? Reason up from the bedrock."* |
| `inversion` | Inversion | *"Invert the problem: what would guarantee failure? What would you never do? Work backward from the negative to find the positive path."* |

**Tier 4 — Communication & Time**
| ID | Name | Prompt Injection |
|----|------|-----------------|
| `second_order_effects` | Second-Order Effects | *"Before acting, ask: and then what? Trace the chain of consequences at least two steps out."* |
| `chestertons_fence` | Chesterton's Fence | *"Before removing or changing anything, understand why it exists. What problem was it solving? What breaks if it's gone?"* |
| `async_first` | Async-First Communication | *"Optimize for clear, durable, self-contained communication. Write as if the reader can't ask a follow-up question."* |

#### Agent-Suggested Models

Agent templates may declare a `suggested_models` list (see `POLLY_AGENT_TEMPLATES.md`). When the user opens a session with an agent that has suggestions, the 🧠 sheet pre-highlights those model IDs as **Suggested** — a visual hint, not forced activation. The user still taps to activate.

#### Client-Side Domain Activation

The domain badge (§11.2) is wired to the mental model selector as a soft suggestion layer:

| Domain Badge | Suggested Models |
|---|---|
| Scrolls (writing/notes) | `freire_pedagogy`, `constraint_as_meaning`, `async_first` |
| Sigils (code) | `first_principles`, `systems_thinking`, `reverse_engineering` |
| Signals (audio) | `instruments_over_tracks`, `constraint_as_meaning` |
| Glyphs (design) | `instruments_over_tracks`, `chestertons_fence`, `inversion` |
| Grids (systems/data) | `systems_thinking`, `second_order_effects`, `chestertons_fence` |

When a domain is detected, the 🧠 nav icon shows a subtle badge dot. Opening the sheet surfaces the domain-suggested models at the top of the list under a **"Suggested for [Domain]"** section header, above the full list. No model is auto-activated — the user always taps to apply.

**Priority order when both agent suggestions and domain suggestions are present:** agent suggestions appear first, then domain suggestions, then the full list. Duplicates are deduplicated (shown once, in the higher-priority slot).

### 11.4 Vault Browser
**Trigger:** Vault icon in Moltbook or Settings  
**Behavior:** Browse Obsidian vault directory structure, view notes rendered as markdown  
**Implementation:** Read from configured vault iCloud path. No server needed.

### 11.5 Quick Capture

**Philosophy:** Quick capture is fast, frictionless input. It is *not* knowledge. A capture is raw material that sits in a staging area until it is deliberately processed into an organized note. Captures never appear in domain search, vault context injection (§11.1), or the knowledge graph until promoted. This keeps the organized vault clean.

#### The Inbox

**UX distinction — Inbox vs. Vault (@researcher B-R5):** The Inbox and the organized vault are visually distinct everywhere they appear in the app. The user must never be confused about which one they're looking at.

| Surface | Inbox | Organized Vault |
|---------|-------|-----------------|
| Vault Search (§4.6) | Results show 📥 badge, labeled "Inbox" in filter chips | No badge, domain chip only |
| Vault Browser (§11.4) | `_inbox/` folder pinned at top with 📥 icon and count badge | All other folders below |
| Capture sheet | "Saving to Inbox" label below Save button | N/A |
| Today View | Inbox card ("X captures waiting") | N/A |
| Note view (read) | Orange "📥 Inbox — not yet processed" banner at top | No banner |

The visual language: **Inbox = orange + 📥**. Vault = domain colors. Never mixed.

All captures land in a dedicated **Polly Inbox** folder within the user's configured vault:
- **Obsidian:** `_inbox/` at vault root (configurable in Settings → Vault)
- **Notion:** A dedicated "Polly Inbox" database (user selects or creates during setup)

The Inbox is a staging area. It is indexed by Polly for *awareness* (so the user can search it) but is explicitly excluded from RAG context injection and domain-filtered retrieval until promoted.

Captures in the Inbox are always in `30-Ideas` maturity stage. They cannot be manually moved to `20-Active` — promotion does that automatically.

#### Capture Entry Points

- **Floating capture button** — persistent `+` button on Today View (§4.2), bottom-right. Opens capture sheet.
- **App icon long-press** — iOS quick action: "New Capture" → opens capture sheet directly
- **Share extension** — Share any text, URL, or image from another app → sends to Polly Inbox
- **Voice capture** — Hold mic in capture sheet for voice → transcribed and saved

#### Capture Sheet

```
┌─────────────────────────────────────┐
│  Quick Capture               [Save] │
├─────────────────────────────────────┤
│                                     │
│  [Text input — multiline,           │
│   placeholder: "What's on your      │
│   mind?"]                           │
│                                     │
├─────────────────────────────────────┤
│  [🎙 Voice]  [📷 Photo]  [🔗 URL]  │
├─────────────────────────────────────┤
│  Domain: [Auto-detect ▾]            │
│  Tag: [+ Add tag]                   │
└─────────────────────────────────────┘
```

- **Domain auto-detect:** Client-side keyword classification (same logic as §11.2) — shown as a suggestion, user can override
- **Tags:** Free-form, comma-separated, stored as frontmatter
- **Save:** writes file to `_inbox/YYYY-MM-DD-HHmm-slug.md` in Obsidian, or new row in Notion Inbox DB
- No template applied at save time — raw markdown only

#### Capture File Format (Obsidian)

```markdown
---
polly_capture: true
created: 2026-03-24T07:30:00
source: voice | text | url | image | share
domain_hint: signals
tags: [norns, idea]
maturity: 30-ideas
promoted: false
---

[capture content here]
```

The `promoted: false` frontmatter flag is what excludes it from RAG. On promotion, this flips to `true` and the file moves to its domain folder.

#### Promotion Flow

Promotion is triggered from the **Inbox Review** screen (see §4.2 Today View — Inbox card) or from any individual capture:

1. User taps "Process" on a capture
2. Polly analyzes the content and suggests: template, domain placement, wiki link candidates
3. User confirms or adjusts
4. Polly creates the properly structured note in the correct vault location
5. Original capture file is deleted (or archived to `_inbox/_processed/` if user prefers to keep history — configurable)

Promotion runs through the same AI-assisted note creation pipeline as manual note creation. The result is indistinguishable from a note created from scratch.

#### Batch Processing

**Settings → Vault → Process Inbox** — runs all pending captures through Polly's suggestion pipeline in sequence. User reviews each one. Designed for weekly review sessions.

**Inbox count badge:** Today View shows a "📥 X captures waiting" card when inbox has unprocessed items. Tapping opens the review queue.

#### Pattern Transparency *(Agent-mediated, Phase 3+)*

~~11.5 Pattern Transparency~~ *(Deferred — requires Polly backend)*
Pattern transparency cards ("Polly noticed...") require the Polly Python backend's pattern engine. For OpenClaw-native Polly, this is deferred to Phase 3+. An agent skill could surface patterns on request ("What have I been capturing most about lately?") without requiring a dedicated engine.

**Phase 3 stub:** A "Polly noticed..." card type in Today View (§4.2) — opt-in, dismissible, fires when the active Polly agent observes a recurring topic across recent captures. Agent-mediated, not engine-mediated. Low priority.

---

### 11.6 Curriculum *(Phase 4+ — Low Priority)*

The original Polly Python backend included a full curriculum system (Phase 23): create learning curricula, enrich sections with explanations and exercises, track mastery, spaced repetition. The system was well-designed and worth preserving.

For Polly iOS Phase 1–3, this is deferred. The backend integration required (curriculum DB, section enrichment API, exercise sandbox) is substantial and not justified until the core experience is proven.

**Phase 4 placeholder:** A "Learning" entry point in the drawer that, when tapped, surfaces a chat interface pre-loaded with the Educator agent and a prompt: *"What do you want to learn? I can build you a structured curriculum."* Agent-driven, no custom backend. Proper curriculum UI (progress tracking, exercises, spaced repetition) is Phase 4+ work.

Reference: `~/polly/openspec/specs/curriculum/spec.md`

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
| Markdown | `react-native-markdown-display` (Phase 1) → custom `PollyMarkdown` renderer (Phase 2+) | `react-native-enriched-markdown` is Aight-proprietary; not available on public npm |
| Animations | `react-native-reanimated` + `react-native-gesture-handler` | Standard RN animation stack |
| Graphics / waveforms | `@shopify/react-native-skia` | 2D canvas for voice waveforms, custom UI elements |
| Storage (fast KV) | `react-native-mmkv` | Persistent device identity, app state cache |
| Navigation | `expo-router` + `@react-navigation/native` (stack only) | File-based routing for full-screen views; **drawer is custom** (see §6.24) — `@react-navigation/drawer` is NOT used |
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

### 12.1 File-Based Routing (expo-router)

**Decision:** `expo-router` is the source of truth for navigation. File-based routing structure below.

**Why expo-router:**
- Deep link resolution for APNs tap-to-open (critical for Phase 2 push notifications)
- File-based structure maps directly to screen hierarchy
- Excellent TypeScript support
- Custom drawer (§6.24) integrates cleanly on top via `@react-navigation/native` stack

**Project structure:**

```
app/
├── _layout.tsx                    // Root layout, DrawerPanel wrapper
├── index.tsx                      // Chat view (default route)
├── today.tsx                      // Today view
├── shortcuts.tsx                  // Shortcuts view
├── usage.tsx                      // Usage stats view
├── moltbook.tsx                   // Moltbook social feed
├── settings/
│   ├── _layout.tsx
│   ├── index.tsx                  // Settings home
│   ├── integrations.tsx           // API key + OAuth config
│   ├── advanced.tsx               // Danger zone, connection debug
│   └── about.tsx                  // Version, licenses
├── agents/
│   ├── _layout.tsx
│   ├── index.tsx                  // Agent switcher / roster
│   └── [id].tsx                   // Individual agent detail
├── vault-search.tsx               // Vault search modal
└── onboarding/
    ├── _layout.tsx
    └── gateway-setup.tsx           // Pre-gateway-connection flow

src/
├── components/
│   ├── ChatBubble.tsx
│   ├── ChatView.tsx
│   ├── VoiceButton.tsx
│   ├── ChatInputBar.tsx
│   ├── DrawerPanel.tsx
│   └── ... (rest of component lib per §6)
├── theme/
│   ├── colors.ts
│   └── index.ts
├── utils/
│   ├── gateway.ts                 // PollyGatewayAdapter
│   └── ...
└── store/
    └── ... (zustand state)
```

**Deep link handling:**

| Deep Link | Route | Purpose |
|-----------|-------|---------|
| `polly://chat/:sessionKey` | `index.tsx` with params | Open specific agent session |
| `polly://group/:groupId` | `index.tsx` with group context | Open group chat |
| `polly://today` | `today.tsx` | APNs notification tap → Today view |
| `polly://onboarding` | `onboarding/gateway-setup.tsx` | First run or reset |

APNs notification payloads include a deep link URL in the `interactiveData` field; `expo-router` automatically routes to the correct screen on tap.

**Root layout (_layout.tsx):**

```typescript
export default function RootLayout() {
  return (
    <DrawerPanel>
      <Stack
        screenOptions={{
          headerShown: false,  // Custom nav bars per screen
          animationEnabled: false,
        }}
      >
        <Stack.Screen name="index" options={{ title: "Chat" }} />
        <Stack.Screen name="today" options={{ title: "Today" }} />
        <Stack.Screen name="shortcuts" options={{ title: "Shortcuts" }} />
        <Stack.Screen name="usage" options={{ title: "Usage" }} />
        <Stack.Screen name="moltbook" options={{ title: "Moltbook" }} />
        <Stack.Screen name="settings" options={{ title: "Settings" }} />
        <Stack.Screen name="vault-search" options={{ presentation: "modal" }} />
        <Stack.Screen name="onboarding" options={{ title: "Setup" }} />
      </Stack>
    </DrawerPanel>
  );
}
```

**Custom drawer is NOT managed by expo-router.** The `DrawerPanel` component (per §6.24) wraps the Stack and handles its own gesture-driven navigation. It reads the current route from the Stack and updates it on swipe/tap, but the drawer itself is a custom Animated View component, not a navigator.

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
- [ ] Exa Search config slot
- [ ] Slack integration
- [ ] Linear integration
- [ ] Cloudflare tunnel management (view status, restart from app)
- [ ] Obsidian Dataview awareness

---

### Phase 5 — Polly Differentiators (Signature Features)
**Target:** Beyond Aight in intelligence and context depth  
**Scope:**
- [ ] Domain awareness badge (client-side keyword classification, user-configured domains; see §11.2)
- [ ] Mental model selector in chat nav (hardcoded defaults + user-custom; see §11.3)
- [ ] Domain behavior injection — when domain is detected, optionally prepend a domain context hint to outgoing messages (user opt-in)
- [ ] RAG semantic search via agent: `/search [query]` command routes to a search-capable agent skill, returns results in chat
- [ ] Obsidian vault full-text search from app (client-side, scans iCloud vault files)
- [ ] `whisper.rn` upgrade path for fully on-device STT
- [ ] *(Future, requires backend work)* Pattern transparency cards — deferred until OpenClaw agent skill equivalent exists

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

> **⚠️ Privacy tradeoff — relay mode vs. §1 principle (@design_eng):** Relay mode routes notification payloads through `relay.openclaw.dev` — third-party infrastructure operated by OpenClaw. This contradicts Polly's §1 principle: *"no data leaving your infrastructure."* The payload is minimal (session key + message preview if enabled), but it does leave your server.
>
> **Polly's recommendation:** Use **direct mode** for users who care about full data sovereignty. Use relay mode for users who want zero-config and accept the tradeoff. Polly's onboarding should default to relay mode with a visible disclosure: "Push notifications are routed through relay.openclaw.dev to reach your phone. No conversation content is included unless you enable message previews." Users who want full self-hosting should be directed to direct mode in Settings → Notifications.
>
> Message previews (the first N characters of a message shown in the notification) must be **disabled by default** and require explicit opt-in regardless of relay vs. direct mode.

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

#### 15.2.5 Exa Search API
**Type:** API key  
**What it does:** Neural/semantic search and deep research — not Amazon/Alexa. Exa is a semantic search engine for AI agents (`exa.ai`). Surfaces high-quality web content with full-text retrieval.
**Priority for Polly:** Medium — useful for research-heavy agents  
**Decision:** Include config slot; forward key to gateway via `config.set`.

---

### 15.3 Tier 2 — Polly Differentiators

#### 15.3.1 Obsidian Vault ⭐ Polly's signature integration
**Type:** Local filesystem (no API key, no OAuth)  
**Runtime:** Client-side on iPhone (not gateway-side)  
**What it does:** Deep integration with your Obsidian vault — the integration Aight doesn't have

**Access strategy — iOS sandbox constraints:**

iOS app sandboxing prevents Polly from directly reading another app's iCloud container (e.g., Obsidian's `iCloud Drive/Obsidian/[vault]/`). Direct path access will silently fail or throw a permissions error. The correct mechanism is **security-scoped bookmarks** via `expo-document-picker`:

1. **Initial vault selection:** User taps "Connect Obsidian Vault" in Settings → Polly calls `DocumentPicker.pickDirectory()` → user navigates to their Obsidian vault folder → iOS grants a security-scoped bookmark URL
2. **Bookmark persistence:** The bookmark URL is serialized and stored in `expo-secure-store` key `"polly.vaultBookmark"` — security-scoped bookmarks persist across app launches
3. **Runtime access:** On each vault access, Polly calls `startAccessingSecurityScopedResource()` on the bookmark URL, reads/writes, then calls `stopAccessingSecurityScopedResource()` — access is bounded to the operation
4. **Write-back (Phase 3):** Same bookmark URL used for creating/appending `.md` files in vault — bookmark grants read+write to the selected directory and its children

**Package:** `expo-document-picker` (already in Expo SDK, no extra install). The `pickDirectory()` API is available on iOS 14+ (our minimum is iOS 16 — fully supported).

**Scope of granted access:** The bookmark grants access to the selected folder and all descendants — the full vault tree. User selects vault root once; Polly can traverse subdirectories freely within that grant.

**iCloud sync requirement:** For remote access (when away from home), the vault must be synced to iCloud via Obsidian iOS + iCloud sync. This is a user setup requirement documented in onboarding. Polly cannot read vault files that aren't synced locally to the device.

**Capture write-back (§11.5):** Uses the same bookmark to write new files to `_inbox/` inside the vault. If the bookmark has expired or been revoked, the capture sheet shows "Vault disconnected — reconnect in Settings" and saves to local Polly Inbox only.

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
  │ 🔍 Exa Search        Configure  > │
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
| Moltbook | API key | `expo-secure-store` (transient — purged after setup) | Held temporarily during registration UX only. On completion: `config.set` to gateway → `SecureStore.deleteItemAsync`. Gateway owns the key permanently; iOS never holds it after setup. |
| Apple EventKit | N/A | iOS system | No credential needed |

**Rule:** Keys used only by the gateway live on the gateway (sent via `config.set` on save). Keys used client-side (ElevenLabs, Google OAuth) live in `expo-secure-store`. File paths and non-sensitive config live in MMKV.

---

### 15.7 Table of Contents Update

Add to §ToC:
```
15. Integrations
    15.1 Integration Tiers
    15.2 Tier 1 — Aight Parity (Brave, ElevenLabs, Google, Notion, Exa)
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


---

## §19 — Aesthetic Theme Engine

**Source spec:** `~/polly/openspec/specs/themes/spec.md`
**Canonical artist catalogue:** Affinity Suite Techniques Catalogue (38 techniques, 12 artists)
**Phase delivery:** Theme picker UI → Phase 3 | Composability → Phase 4 | Domain-triggered → Phase 5

### 19.1 Philosophy: Ambient Stance, Not Configurable Panel

Themes in Polly iOS are not skins. They are not color pickers. They are not "personalization."

A theme is an epistemological stance — a set of aesthetic commitments that changes how the app looks *and* how the AI thinks. When Ghost Box is active, the app feels archival and slightly haunted. The AI becomes more oblique, more institutional, more allusive. When Fidenza is active, the app is warm and organic. The AI is discursive and probabilistic in its reasoning.

The user does not configure this in detail. They choose a sensibility and the rest follows.

> **The theme is the background hum, not the foreground command.**

**Implementation constraints:**
- Theme switching is instant and non-destructive. Previous conversation messages do not change; only new messages reflect the new behavior injection.
- The user never sees the behavior injection prompt. They feel the difference; they don't configure it.
- Complexity of the composability system (7 × 7 matrix) is deferred to Phase 4. Phase 3 ships 7 themes, single-tap.
- The word "Themes" does not appear in the UI. The setting is labeled **Sensibility**.

---

### 19.2 The Sensibility Picker

**Location:** Settings → Sensibility

**Layout:** Horizontal scrollable row of 7 cards. No grid. No list. The left-to-right order maps turbulence low → high — users are intuitively dialing between structure and flow without needing to know what turbulence means.

**Card order (left to right):**
```
Albers  →  Jetset  →  Riley  →  Ghost Box  →  Reas  →  Martens  →  Fidenza
 0.0         0.1       0.0–0.3     0.2          0.3       0.4         0.6
```

**Card anatomy (each card ~160×200pt):**
```
┌──────────────────────┐
│  [live mini-preview] │  ← 80pt tall, shows chat bubble + bg texture
│                      │
│  ████░░░░░░░░        │  ← 5-swatch color strip from theme palette
│                      │
│  Theme Name          │  ← 16pt, theme's own typography treatment
│  Artist surname      │  ← 12pt, muted, e.g. "Albers" or "House"
│                      │
│  One-line stance     │  ← 11pt, italic, e.g. "Grid is generative"
└──────────────────────┘
```

**Active state:** Card has a 2pt border in theme's accent color. A small filled circle indicator appears. No checkmark — that's too utilitarian for this feature.

**Tap behavior:** Immediate live transition — no confirmation dialog, no "Apply" button. The parent Settings screen itself transitions to the new theme as the user taps. The transition is 350ms, the motion style governed by the incoming theme (Fidenza = flowing ease, Jetset = instant cut, Ghost Box = slight flicker-in).

**Mini-preview content:** A static mock of a single AI chat bubble using the theme's palette, border-radius, and background texture. The bubble text reads *"System nominal."* — a Ghost Box reference that suits all themes without being theme-specific.

---

### 19.3 Presentation Layer → React Native Token Mapping

Each theme defines a presentation layer. In React Native, this maps to a typed `ThemeTokens` object consumed via React Context. The active theme's tokens replace the default token set system-wide.

```typescript
interface ThemeTokens {
  // Color
  bgPrimary: string;
  bgSecondary: string;
  bgSurface: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  accent: string;
  accentSecondary: string;
  border: string;

  // Shape
  radiusSm: number;    // e.g. Albers=0, Jetset=0, Fidenza=12
  radiusMd: number;
  radiusLg: number;
  radiusBubble: number; // chat bubble corner radius

  // Typography
  fontBody: string;        // system font name
  fontMono: string;        // monospace font name
  fontHeading: string;
  fontWeightHeading: string;
  letterSpacingBody: number;

  // Texture
  textureOverlay: ThemeTexture | null;
  textureOpacity: number;  // 0.03–0.08

  // Motion
  transitionMs: number;
  transitionEasing: string;  // 'ease', 'linear', 'spring'

  // Chrome
  dividerStyle: 'line' | 'gap' | 'none';
  shadowStyle: 'soft' | 'sharp' | 'none';
  bubbleStyle: BubbleStyle;
}

type ThemeTexture = 'grain' | 'canvas' | 'scan-lines' | 'dot-grid' | 'woven' | 'letterpress' | null;
type BubbleStyle = 'rounded' | 'square' | 'ribbon' | 'stamp' | 'minimal' | 'stripe-edge' | 'thread';
```

Theme tokens stored in `src/themes/[themeName].ts`. Active theme provided via `ThemeContext`. Components consume via `useTheme()` hook — never hardcode color or radius values.

---

### 19.4 Typography on iOS — Font Availability Matrix

Custom font loading (via `expo-font`) is supported but avoided for system fonts that already deliver the right aesthetic. Fallback chain specified per theme.

| Theme | Target feel | Primary | Fallback |
|---|---|---|---|
| **Reas** | Monospaced, instruction-set | `SF Mono` (system) | `Courier New` |
| **Fidenza** | Humanist sans, warm | `SF Pro` (system default) | — |
| **Ghost Box** | Institutional grotesque + slab | `Georgia` (body), `SF Pro Condensed` (headers) | `Times New Roman` |
| **Martens** | Dutch modern, weight-structural | `SF Pro` heavy weight | — |
| **Jetset** | Helvetica — the real thing | `Helvetica Neue` (iOS system) | `SF Pro` |
| **Riley** | Recessive, light | `SF Pro Light` | — |
| **Albers** | Grid-pixel, tight | `SF Mono` tight tracking | `Courier New` |

**Note on Jetset:** iOS ships Helvetica Neue natively. Jetset is the one theme where the platform *delivers the canonical typeface*. No font loading required.

**Note on Ghost Box:** `expo-font` can load Akzidenz Grotesk or Knockout if the user has licensed them. The spec defaults to system fonts. Premium font loading is a Phase 4 option.

---

### 19.5 Behavior Layer → Persona System Prompt Injection

When a theme is active, a theme tag is appended to every OpenClaw agent's effective system prompt via the gateway config mechanism. The user never sees this. The agent's SOUL.md remains unchanged — the theme is a *layer on top*, not a replacement.

**Injection format:**

```
[AESTHETIC STANCE — {ThemeName}]
{ThemeBehaviorInjection}
This stance influences your tone, structure, and decision-making defaults.
It does not override explicit user instructions.
```

**Theme behavior injections:**

**Reas:**
> Favor systematic, emergent thinking. Present ideas as rule-sets that generate outcomes rather than prescriptions. Be procedural and precise. Favor small composable ideas that create complex effects. Documentation style: executable instruction.

**Fidenza:**
> Approach problems with probabilistic warmth. Explore weighted possibilities rather than single answers. Be technically precise but accessible — explain the math gently. Structure responses organically; allow productive wandering. Voice: warm-technical.

**Ghost Box:**
> Work from accumulated reference, never direct citation. Be allusive and slightly indirect — approach from impression. Documentation reads like institutional technical manuals. Variable names and file structures suggest archival filing systems. Voice: hauntological — things remembered rather than looked up.

**Martens:**
> Treat every response as a layered process — build through successive passes, not single placements. Document the sequence of making, not just the result. Color and structure emerge from combination. Voice: process-aware.

**Jetset:**
> Maximum restraint. Use the fewest possible components. Four concepts maximum per response — if more, reconsider scope. Never perform voice; let content speak. Break the fourth wall on design: acknowledge that you are producing a designed artifact. Comments explain why, not what. Voice: neutral, ego-less.

**Riley:**
> Isolate variables. Explore one parameter systematically across a series. Document what was varied and what was observed. Avoid decoration — describe effect and perception precisely. Structure responses as study notes: parameter, variation, observation. Voice: observational.

**Albers:**
> Define the constraint first; find what it allows. Begin from material observation — let ideas emerge from handling, not from concept. Document what the tool does before what you want from it. Complexity emerges from within constraint, never from breaking it. Voice: material-first.

**Delivery mechanism:** The injection is set via `config.patch` RPC on the gateway when the theme switches. The gateway key is `polly.ios.aestheticStance`. All agents read this as a shared ambient layer. Switching themes triggers a `config.patch` with the new injection text; the change takes effect on the next message.

> **Multi-client conflict (@design_eng):** Theme injection writes to the gateway's shared config. If two clients are connected simultaneously (Aight + Polly, or two Polly devices), one device's theme change will overwrite the other's. **Decision: last-write-wins, with a session-local override option.**
>
> Phase 1 behavior: last-write-wins. No coordination. Documented in Settings → Themes: "Theme settings are shared across all connected clients. Changing themes on one device affects all devices connected to this gateway."
>
> Phase 2 behavior: Session-local theme override. The `config.patch` writes to a device-scoped key (`polly.ios.aestheticStance.[deviceId]`) rather than a shared key. Each client reads its own device-scoped key first, falling back to the shared key. This requires a gateway-side change to support per-device config scoping — tracked as a Phase 2 @backend item.

---

### 19.6 Theme Definitions — iOS-Adapted

Full palette values mapped from the openspec source, adapted for dark-first iOS rendering.

#### Reas

```typescript
{
  bgPrimary:    '#0A0A0A',  // near-black with cool cast
  bgSecondary:  '#111111',
  bgSurface:    '#1A1A1A',
  textPrimary:  '#F8F6F3',  // off-white
  textSecondary:'#B0ADA8',
  textMuted:    '#6B6864',
  accent:       '#3A6B9F',  // system blue
  accentSecondary: '#2D2D2D',
  border:       '#222222',
  radiusSm: 0, radiusMd: 2, radiusLg: 4, radiusBubble: 4,
  fontBody: 'SF Mono', fontHeading: 'SF Mono',
  letterSpacingBody: 0.5,
  textureOverlay: 'dot-grid', textureOpacity: 0.04,
  transitionMs: 250, transitionEasing: 'linear',
  dividerStyle: 'line', shadowStyle: 'none',
  bubbleStyle: 'square',
}
```

#### Fidenza

```typescript
{
  bgPrimary:    '#1A1510',  // warm near-black
  bgSecondary:  '#221C14',
  bgSurface:    '#2A2218',
  textPrimary:  '#F2E8D5',  // cream
  textSecondary:'#C4A87A',
  textMuted:    '#8B7355',
  accent:       '#C4653A',  // terracotta
  accentSecondary: '#D4A84B', // gold
  border:       '#3A2E20',
  radiusSm: 6, radiusMd: 12, radiusLg: 20, radiusBubble: 18,
  fontBody: 'SF Pro', fontHeading: 'SF Pro',
  letterSpacingBody: 0,
  textureOverlay: 'canvas', textureOpacity: 0.06,
  transitionMs: 400, transitionEasing: 'ease',
  dividerStyle: 'gap', shadowStyle: 'soft',
  bubbleStyle: 'ribbon',
}
```

#### Ghost Box

```typescript
{
  bgPrimary:    '#0E0C09',  // dark yellowed
  bgSecondary:  '#161310',
  bgSurface:    '#1E1A14',
  textPrimary:  '#E8DCC4',  // worn cream
  textSecondary:'#B4A882',
  textMuted:    '#7A6E58',
  accent:       '#D4763A',  // worn orange
  accentSecondary: '#4A6B82', // public information blue
  border:       '#2E2820',
  radiusSm: 0, radiusMd: 0, radiusLg: 2, radiusBubble: 2,
  fontBody: 'Georgia', fontHeading: 'SF Pro Condensed',
  letterSpacingBody: 0.2,
  textureOverlay: 'scan-lines', textureOpacity: 0.05,
  transitionMs: 180, transitionEasing: 'linear',  // slight flicker
  dividerStyle: 'line', shadowStyle: 'none',
  bubbleStyle: 'stamp',
}
```

#### Martens

```typescript
{
  bgPrimary:    '#0A0A0A',
  bgSecondary:  '#141414',
  bgSurface:    '#1A1A1A',
  textPrimary:  '#F0EEEC',
  textSecondary:'#AAA8A4',
  textMuted:    '#666460',
  accent:       '#E03030',  // red primary
  accentSecondary: '#2040A0', // blue primary
  border:       '#222222',
  radiusSm: 0, radiusMd: 0, radiusLg: 0, radiusBubble: 0,
  fontBody: 'SF Pro', fontHeading: 'SF Pro',
  letterSpacingBody: 0,
  textureOverlay: 'letterpress', textureOpacity: 0.05,
  transitionMs: 300, transitionEasing: 'ease',
  dividerStyle: 'line', shadowStyle: 'sharp',
  bubbleStyle: 'minimal',
}
```

#### Jetset

```typescript
{
  bgPrimary:    '#FFFFFF',  // NOTE: Jetset is light-mode primary
  bgSecondary:  '#F5F5F5',
  bgSurface:    '#EFEFEF',
  textPrimary:  '#000000',
  textSecondary:'#444444',
  textMuted:    '#888888',
  accent:       '#FF0000',  // red — full saturation only
  accentSecondary: '#0000FF', // blue — full saturation only
  border:       '#000000',
  radiusSm: 0, radiusMd: 0, radiusLg: 0, radiusBubble: 0,
  fontBody: 'Helvetica Neue', fontHeading: 'Helvetica Neue',
  letterSpacingBody: -0.2,
  textureOverlay: null,  // no texture — production artifacts instead
  textureOpacity: 0,
  transitionMs: 0,  // instant cut — no transition animation
  transitionEasing: 'linear',
  dividerStyle: 'line', shadowStyle: 'none',
  bubbleStyle: 'square',
}
```

**Jetset special case:** This is the only light-mode theme. When Jetset is active, `StatusBarStyle` switches to `dark-content`. Crop marks (2pt L-shapes) appear at the four corners of the chat input field and the navigation bar. These are `position: absolute` decorative views — not interactive.

#### Riley

```typescript
{
  bgPrimary:    '#0A0A0F',  // near-black, cool
  bgSecondary:  '#12121A',
  bgSurface:    '#1A1A24',
  textPrimary:  '#EEEEF4',
  textSecondary:'#9090A8',
  textMuted:    '#555568',
  accent:       '#E8644A',  // warm complement #1
  accentSecondary: '#4A8EE8', // cool complement #2
  border:       '#2A2A3A',
  radiusSm: 0, radiusMd: 0, radiusLg: 0, radiusBubble: 0,
  fontBody: 'SF Pro', fontHeading: 'SF Pro',
  letterSpacingBody: 0.8,  // recessive, airy
  textureOverlay: null,
  textureOpacity: 0,
  transitionMs: 200, transitionEasing: 'linear',
  dividerStyle: 'gap', shadowStyle: 'none',
  bubbleStyle: 'stripe-edge',
}
```

**Riley special case:** Section dividers are rendered as alternating stripe bands — two colors from the palette at 20% opacity — rather than lines or gaps. The navigation bar has subtle horizontal stripe modulation on scroll.

#### Albers

```typescript
{
  bgPrimary:    '#0C0B09',  // very dark warm
  bgSecondary:  '#141210',
  bgSurface:    '#1C1916',
  textPrimary:  '#E8DBC4',  // unbleached
  textSecondary:'#B0A080',
  textMuted:    '#6E5E48',
  accent:       '#C4923A',  // ochre
  accentSecondary: '#2B3A67', // indigo
  border:       '#2A2418',
  radiusSm: 0, radiusMd: 0, radiusLg: 0, radiusBubble: 0,
  fontBody: 'SF Mono', fontHeading: 'SF Mono',
  letterSpacingBody: 0.3,
  textureOverlay: 'woven', textureOpacity: 0.04,
  transitionMs: 300, transitionEasing: 'ease',
  dividerStyle: 'line', shadowStyle: 'none',
  bubbleStyle: 'thread',
}
```

---

### 19.7 Texture Overlay Implementation

Textures are React Native `<Canvas>` components (via `@shopify/react-native-skia` — already a Phase 2 dependency candidate; for Phase 3 use an `<Image>` with a pre-rendered tiling PNG at low opacity if Skia not yet integrated).

Each texture is a 128×128 PNG tiled across the screen background at `textureOpacity`. Textures are bundled as static assets — no runtime generation. Total asset weight for all 7 textures: ~80KB.

**Texture asset list:**
- `grain.png` — film grain noise (Fidenza)
- `canvas.png` — medium canvas weave (Fidenza alternative)
- `scan-lines.png` — horizontal scan lines, 2px period (Ghost Box)
- `dot-grid.png` — regular dot grid, 8px spacing (Reas)
- `woven.png` — tight over-under weave (Albers)
- `letterpress.png` — subtle ink spread pattern (Martens)

Jetset and Riley have no texture overlay.

---

### 19.8 The `useTheme()` Hook

```typescript
// src/hooks/useTheme.ts

import { useContext } from 'react';
import { ThemeContext } from '../contexts/ThemeContext';

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}

// Usage in any component:
const { tokens, activeTheme, setTheme } = useTheme();
// tokens.accent, tokens.bgPrimary, tokens.radiusBubble, etc.
```

`ThemeProvider` wraps the root navigator. `activeTheme` is persisted to MMKV key `"polly.sensibility"`. On app launch, the persisted theme is loaded before first render — no flash of default theme.

---

### 19.9 Phase Delivery Plan

**Phase 3 — Core Sensibility (ship with Shortcuts + Integrations):**
- [ ] 7 theme token files (`src/themes/*.ts`)
- [ ] `ThemeContext` + `ThemeProvider` + `useTheme()`
- [ ] Sensibility card picker UI (Settings → Sensibility)
- [ ] Live preview mini-card per theme
- [ ] Instant switching with theme-native transition
- [ ] Texture overlay assets (6 PNGs)
- [ ] Jetset crop marks + light-mode status bar
- [ ] Riley stripe-edge dividers
- [ ] Behavior injection via `config.set` RPC on theme switch
- [ ] MMKV persistence of active sensibility

**Phase 4 — Composition (ship with Moltbook + Stats):**
- [ ] Turbulence slider per theme (overrides `designer.turbulence`)
- [ ] Color Logic selector (3–4 options per theme, not full matrix)
- [ ] Grid Strictness toggle (relaxes radius/spacing constraints)
- [ ] Composed theme saved to `~/.polly/themes/custom/` as JSON
- [ ] Export/import theme JSON

**Phase 5 — Ambient Switching (Polly Differentiators):**
- [ ] Domain-triggered auto-switching (e.g., code → Reas, audio → Fidenza)
- [ ] Time-of-day theme sequences
- [ ] Lieberman theme: daily rotation built in (new constraint each day)
- [ ] Community theme import

---

### 19.10 Composability Interface (Phase 4 Preview)

Rather than exposing the full 7×7 property matrix, Phase 4 surfaces composability as **three human-readable sliders** over the base theme:

| Slider | Low end | High end | Maps to |
|---|---|---|---|
| **Structure** | Organic, flowing | Grid-strict | `spacing.alignment`, `radiusAll`, `dividerStyle` |
| **Turbulence** | Controlled, quiet | Energetic, probabilistic | `designer.turbulence` (0.0–1.0) |
| **Voice** | Neutral, terse | Warm, discursive | Behavior injection intensity |

A user picks a base theme (e.g., Martens) then adjusts these three sliders. The live preview updates instantly. The result is saved as a named composition. The underlying theme JSON is fully specified — but the user only touched 3 knobs.

---

### 19.11 Relationship to App Constitution (§18)

Aesthetic themes are a constitutionally-compliant feature:

- **Progressive disclosure** (§18.2): Default is Reas (structured, minimal). The picker is in Settings, not onboarding. The feature reveals itself when the user is ready.
- **Local-first** (§18.4): All theme data is local. No theme syncs to cloud. No analytics on which theme is active.
- **Ownership** (§18.1): Themes are exported as JSON the user owns. The composability system produces artifacts in `~/.polly/themes/` on the user's gateway machine.
- **No dark patterns** (§18.5): Theme switching has no "recommended" theme, no A/B testing, no engagement optimization. The user chooses a sensibility; the app honors it.

The one constraint to check: **Jetset's light mode**. All other themes are dark-first (§18.3 specifies dark mode as Polly's primary mode). Jetset is explicitly white/black/red/blue — a light-mode theme. This is acceptable because:
1. It is not the default
2. It represents faithful artist rendering (Jetset's work is light-ground)
3. The user consciously selects it as a sensibility

Document as a known constitutional exception in §18.3 with a cross-reference to §19.6 (Jetset definition).

---

*§19 added 2026-03-23. Source: `~/polly/openspec/specs/themes/spec.md` (Affinity Suite Techniques Catalogue, 38 techniques, 12 artists). iOS adaptation by @code_architect.*


---

## §20 — Architectural Principles & Developer Notes

*Clarifications added 2026-03-23 post-openspec audit. These are correctness guardrails for developers, not new features.*

---

### 20.1 Single Backend Principle

**Polly iOS connects to OpenClaw only.**

The Polly Python FastAPI server (`server.py`, port 8000) is a gateway-side resource. The iOS client has no direct connection to it. If an agent needs to query the Polly RAG engine, search the vault semantically, or run domain detection — the agent does it via tool calls server-side. The iOS app sends a message and receives a response. It never calls `http://[host]:8000` directly.

This is not a limitation. It is the correct architecture for an OpenClaw client:

```
iOS app  ←──── WebSocket ────→  OpenClaw gateway
                                      │
                                      ├── Agent skills / tools
                                      ├── Polly RAG (if running)
                                      ├── Obsidian tools (if configured)
                                      └── Any other server-side resources
```

The iOS app's job is to be the best possible interface to OpenClaw. It does not need to be a thick client.

**Consequence for §11 (Polly-Specific Features):** All features in §11 are either purely client-side (vault context injection, vault browser, client-side domain labeling, mental model injection) or agent-mediated (semantic search, pattern insights). None require a direct REST call to the Polly server.

---

### 20.2 Constitutional Epistemology — Developer Note

The Polly backend (`core/constitutional/layer.py`) injects a non-configurable epistemological layer into every agent's system prompt. This is always active. It is not a feature — it is infrastructure.

**What this means for iOS:**
- The Settings screen must not include any toggle for "content filtering," "safety mode," or anything implying the constitutional layer is configurable. It isn't.
- Theme behavior injection (§19.5) operates at Layer 5 of the system prompt hierarchy. Constitutional epistemology is Layer 7 (deepest). The iOS client owns Layer 5 only.
- No "explain why Polly responded this way" feature should expose the constitutional layer text. It is invisible infrastructure.

---

### 20.3 Domain Configuration — Client-Side Only

Domains in the iOS app are **user-configured in Settings**, not fetched from any server. This is the correct model for an OpenClaw-only client.

**Settings → Domains:**
- User defines their domains (name, color, Lucide icon, keywords for auto-detection)
- Stored in MMKV key `"polly.domains"` as JSON
- Default set shown on first run (e.g., Code, Writing, Audio, Design, Systems) — user can rename, reorder, add, delete

**Domain auto-detection:** Client-side keyword matching against the user's configured keyword list per domain. No server call. Fast, private, works offline.

**DomainBadge component:** Reads from the local MMKV domain config. No network dependency.

```typescript
interface UserDomain {
  id: string;           // user-assigned, e.g. "code"
  name: string;         // display name, e.g. "Code"
  color: string;        // hex #RRGGBB
  icon: string;         // Lucide icon name
  keywords: string[];   // for client-side auto-detection
  order: number;
}
```

**MMKV keys:**
- `"polly.domains"` — JSON array of `UserDomain[]`
- `"polly.domainsVersion"` — integer, increment on any edit (for cache invalidation)

---

### 20.4 Onboarding Behavior

Polly's onboarding has two distinct phases: **Bootstrapped Setup** (before any gateway is connected) and **Progressive Revelation** (after first connection, ongoing). They are separate concerns.

---

#### Phase A: Bootstrapped Setup (Cold Start)

When the user installs Polly and opens it for the first time, there is no gateway — and therefore no agents. Polly solves this with a **bootstrap model**: a lightweight AI connection that exists only to guide the user through setup.

**Bootstrap model options (in priority order):**
1. User's existing API key — if the user enters an Anthropic, OpenAI, or Google key in the first screen, that model becomes the bootstrap
2. Free tier model — Gemini Flash (via Google AI Studio free tier) as a built-in fallback that requires no user API key; key is baked into the app bundle for onboarding only
3. Manual mode — if no model is available, falls back to a scripted, non-AI guided setup (static screens with instructions)

The bootstrap model is **only used for onboarding**. Once the gateway is connected, it steps aside. Conversations during setup are not persisted.

**Setup flow:**

```
Cold open
  ↓
[Welcome screen]
  "Hi — I'm Polly. I'll help you get set up."
  [Enter your API key (optional)] [Skip — use free model]
  ↓
[Conversational onboarding — chat interface, bootstrap model active]
  Polly: "To work properly, I connect to a small server called OpenClaw 
          that runs on your Mac. Do you have OpenClaw installed?"
  → Yes / No / What's OpenClaw?
  ↓
  [If No] Polly: "No problem — I'll walk you through it. Open Safari 
                  and go to openclaw.app..."
  [Polly guides: download → install → start server → confirm running]
  ↓
  Polly: "Great. Now I need your gateway address. 
          If you're on the same Wi-Fi as your Mac, tap 'Scan for gateway' 
          and I'll find it automatically."
  → [Scan] [Enter manually]
  ↓
  [mDNS scan or manual URL entry → connection test]
  ↓
  Polly: "Connected ✓. One last thing — paste your gateway auth token. 
          You'll find it in OpenClaw's settings under 'Security'."
  → [Token field + link to where to find it]
  ↓
  [Auth handshake → success]
  ↓
  Polly: "You're in. Now let's get your team set up."
  → [Team selection screen — §20.4.1]
  ↓
  Polly: "You're ready. Let me show you around."
  → [Enter main app — gateway active, team active, full agent roster live]
```

#### §20.4.1 Team Selection (Onboarding Step)

After gateway connection is established, the user picks their first team. This is the "Pick a team" screen shown in Aight's onboarding — same concept, Polly's design.

**UI:** Full-screen grid of team template cards (2-column). Each card shows:
- Team emoji/icon
- Team name (bold)
- One-line description
- Agent count badge (accent green pill)

Bottom of list: **"Start from scratch →"** row for custom team composition.

**Polly's built-in team templates (Phase 1):**

| Template | Description | Agent count |
|---|---|---|
| Dev Squad | Build, test, secure, ship | 9 agents |
| Startup Team | Full stack founding crew | 9 agents |
| Content Studio | Create and distribute content | 8 agents |
| Marketing Engine | Acquisition, growth, and analytics | 9 agents |
| Life Team | Personal wellness and growth | 8 agents |
| Finance Team | Money, markets, and strategy | 7 agents |
| App Launch | Ship your app and get users | 7 agents |
| Learning Squad | Study, debate, and level up | 6 agents |

> **Note to @researcher / @infra:** The agent roster for each team template needs to be defined and mapped to `POLLY_AGENT_TEMPLATES.md` entries. This is Phase 1 content work. The templates above are drawn from Aight's onboarding screenshots — confirm names match or adjust.

**"Start from scratch":** Opens an agent picker sheet — user selects agents individually, names the team, picks an emoji. Creates a custom team with those agents.

**Multi-team:** User can create additional teams at any time from Settings → Teams → [+]. No limit on team count.

**Team switching:** Drawer team selector lists all created teams. Switching is instant — gateway doesn't change (it's still the same OpenClaw instance), only the active team context changes in the client.

**Key design rules:**
- Every step is a conversation turn, not a form. The user talks; Polly responds.
- If the user gets stuck, Polly asks a clarifying question rather than showing an error screen
- Dead ends don't exist — any response Polly doesn't understand falls back to "Let me try a different way"
- The bootstrap model runs a structured script with freeform fallback for edge cases
- Setup screens use the same chat UI as the main app — no separate onboarding UI components

**Security flows during onboarding:**

> ✅ **@security_audit** — Security sub-flows added March 24, 2026

**Device keypair initialization:**
On first launch, before any onboarding screen is shown, Polly silently initializes device identity:
1. Check `expo-secure-store` for `"polly.device.privateKey"` — if present, device is already initialized (resume flow, skip keygen)
2. If absent: generate Ed25519 keypair via `@noble/ed25519`, store private key bytes to `expo-secure-store` under `"polly.device.privateKey"`
3. Derive `deviceId = SHA-256(publicKeyBytes)` as hex — store to MMKV `"polly.device.id"` (non-sensitive, used in UI)
4. If `expo-secure-store` write fails (e.g. device passcode not set): block onboarding and show "Passcode Required" screen — "Polly requires a device passcode to securely store your credentials. Please set a passcode in iOS Settings, then return."

**Auth token entry and TOFU cert pinning:**
After gateway URL is entered and connection test passes:
1. If the gateway presents a self-signed or unrecognized TLS certificate, show a **Certificate Verification** screen before auth token entry:
   - Display: certificate fingerprint (SHA-256, formatted as groups of 4 hex chars), issuer, expiry date
   - Warning: "This certificate isn't from a trusted authority. If you're connecting to your own gateway, verify this fingerprint matches what's shown in OpenClaw Settings → Security."
   - Two actions: **Trust This Certificate** (stores fingerprint to `expo-secure-store` under `"polly.gateway.tlsFingerprint"`) | **Cancel**
   - User cannot proceed past this screen without explicitly trusting — no silent accept
2. On subsequent connects: compare presented cert fingerprint to stored value — mismatch → block connection and show "Certificate Changed" warning with option to re-verify or abort

**Bootstrap token expiry:**
The free-tier bootstrap API key baked into the app bundle must have a finite TTL enforced client-side:
- Key is accompanied by a hardcoded `expiresAtMs` timestamp in the app bundle
- At onboarding start, check `Date.now() < expiresAtMs` — if expired, bootstrap falls back to Manual mode (static screens); the free-tier AI guide is unavailable
- This check is independent of any server call — no network required to enforce it
- Note: the app bundle key rotation strategy (how expired keys get replaced) is an EAS OTA update — document this in release process, not the app UI

> **⚠️ Bootstrap key IPA extraction risk:** The Gemini Flash API key baked into the JS bundle is extractable via IPA decompilation (Metro bundle is not encrypted; jailbroken tools can extract it in minutes). **Decision: accept this with mitigations.** The key is scoped to a dedicated Google AI Studio project with hard rate limits (requests/day, tokens/day) that make it economically useless for abuse at scale. The key's only purpose is onboarding assistance — it cannot be used to access any Polly user data. If the key is abused and rate-limited, onboarding falls back to Manual mode gracefully. This is documented as an accepted risk, not an oversight. Alternative (no baked key, always manual fallback) sacrifices onboarding quality for marginal security gain — not the right tradeoff for a personal productivity app.

**Empty secure store on device restore:**
If the app is reinstalled or restored to a new device and `expo-secure-store` is empty (Keychain not transferred):
- Detect on launch: `"polly.device.privateKey"` absent but `"polly.device.id"` present in MMKV → mismatch state
- Show "New Device Setup" screen: "It looks like you're setting up Polly on a new device. Your previous gateway connection needs to be re-established." → full re-pair flow (same as cold start, but skips OpenClaw installation steps if gateway is already reachable)
- Old `deviceId` is automatically invalidated at the gateway when the new device completes auth (gateway sees a new public key for a new deviceId — old deviceId remains registered until user removes it in Settings → Security → Devices)

**`PollyOnboardingAgent` persona:**
A dedicated system prompt baked into the app (not fetched from gateway) that:
- Knows the exact steps to install and configure OpenClaw
- Has step-by-step instructions for Mac, including screenshots referenced by text description
- Knows how to handle common errors (port conflicts, firewall issues, token mistakes)
- Stays patient and non-technical unless the user signals they want detail
- Hands off cleanly once connected ("All done — I'm switching to your full agent setup now")

This persona is never available after onboarding. It does not appear in the agent list.

---

#### Phase B: Progressive Revelation (Post-Connection)

**<60 seconds to first value.** Once connected, the first agent is active immediately. No feature tour, no permission prompts (those come contextually).

**Persona first-activation:** First time each agent is opened, prepend a one-sentence orientation as a synthetic assistant message. Tracked in MMKV `"polly.personaFirstActivation"`. Examples:
- Code Architect: *"I'm your architecture and systems persona. Tell me what you're building."*
- AI Expert: *"I work through AI/ML problems — architecture, training, evaluation. What's the question?"*

**Progressive revelation:** Features surface contextually via dismissible hint cards:

| Trigger | Hint |
|---|---|
| 3rd conversation | "Quick Capture is ready — tap + on Today to save a thought instantly." |
| 5th conversation | "Try a Shortcut — quick-access prompts you use often." |
| First voice message | "ElevenLabs gives you a premium voice. Settings → Integrations." |
| 10th conversation | "Mental models available — tap 🧠 in any chat." |
| First capture saved | "You have items in your Inbox. Tap 📥 on Today to process them." |

Hint state stored in MMKV `"polly.shownHints"` (JSON array of hint IDs). Never show twice.

---

### 20.5 DRM Architecture Note *(Phase 5)*

Per `~/polly/openspec/specs/drm/spec.md`: Cloudflare Workers KV is the **peer registry only** (discovery/signaling). Node-to-node task traffic flows peer-to-peer through tunnel endpoints — not through the Workers coordinator. The coordinator endpoint handles `POST /peers/register` + `GET /peers/list` only.

No iOS action required for Phase 1–4. Phase 5 consideration only.

---

*§20 rewritten 2026-03-23 — stripped Polly REST API dependencies, scoped to OpenClaw-only architecture.*

---

## §21 — Model Routing & Token Conservation

**Owner:** @code_architect + @backend  
**Date:** March 23, 2026  
**Status:** Architectural design — gateway-side implementation, iOS surface layer documented here

---

### 21.1 Philosophy

The core of Polly's progressive autonomy principle is **intelligent model routing**. The goal is not to minimize cloud usage as an end in itself — it is to make the system smart enough that expensive cloud tokens are only spent on problems that genuinely require them.

A 7B local model with high-confidence RAG context will outperform a frontier cloud model answering cold on the majority of real queries. The RAG layer is not a feature bolted on — it is what makes local-first routing viable. Without it, local models lose on quality. With it, they punch above their weight class on domain-specific questions.

**The key principle: token conservation through RAG + routing is more valuable than any individual model choice.** A well-populated knowledge base is worth more than a paid API key.

---

### 21.2 Four-Tier Model Hierarchy

```
┌──────────────────────────────────────────────────────────┐
│  Tier 0 — Local Inference (Ollama)                       │
│  Cost: $0    Latency: fast on capable hardware           │
│  Models: llama3.1:8b, Codestral, DeepSeek-Coder, etc.   │
│  Use for: classification, summarization, RAG-augmented   │
│           queries, voice responses, background tasks     │
├──────────────────────────────────────────────────────────┤
│  Tier 1 — Free Cloud (Groq, Gemini Flash free tier)      │
│  Cost: $0 up to rate limit   Latency: very fast          │
│  Use for: medium complexity, Tier 0 overflow,            │
│           voice mode fallback, daily quota resets        │
├──────────────────────────────────────────────────────────┤
│  Tier 2 — Subscription Quota (GitHub Copilot, etc.)      │
│  Cost: within subscription   Quality: high               │
│  Use for: medium-heavy tasks, code gen, doc work,        │
│           tasks within plan quota                        │
├──────────────────────────────────────────────────────────┤
│  Tier 3 — Paid API (Anthropic direct, OpenAI direct)     │
│  Cost: real money per token  Quality: highest            │
│  Use for: novel complex problems, large context,         │
│           no RAG match, explicit user escalation only    │
└──────────────────────────────────────────────────────────┘
```

**Default routing policy:** Start at Tier 0. Escalate only when needed. "Needed" is determined by the routing decision engine (§21.4).

**User routing preference** (Settings → Models → Routing Policy):
- `conservative` — maximize Tier 0/1, minimize cloud spend
- `balanced` (default) — quality-aware routing, respects RAG confidence
- `quality` — prefer Tier 2/3 for non-trivial tasks; local only for classification

---

### 21.3 RAG Design for Local-Model Friendliness

The knowledge base must be built for 4k–8k context windows, not 128k. Local models cannot handle raw vault dumps.

**Dense summaries alongside raw docs:**
Every vault note gets a 300-word local-model-generated summary stored at index time. On retrieval, send the summary first. Send the full document only if the query explicitly requires depth.

**Domain-tagged chunks:**
Each knowledge chunk is tagged by domain (code / writing / audio / design / systems). Routing can then check: "this code question has a 0.92 RAG hit in the code domain → route to Tier 0 code model (Codestral/DeepSeek-Coder)."

**Pre-computed embeddings:**
Stored at `~/.polly/embeddings/` on the gateway machine. Never re-embedded on query. Background re-indexing job runs nightly or when vault files change.

**MEMORY.md always injected:**
Every agent request prepends the agent's MEMORY.md (typically 1k–3k tokens). This is cheap and ensures local models have personal context on every call. Never skipped, never rate-limited.

**Conversation summarization:**
Background Tier 0 job compresses conversation history every 20 turns to ~500 words. Old turns replaced by the running summary. Prevents context window bloat from long sessions. Summary stored in session state.

**Retrieval thresholds:**
- Cosine similarity ≥ 0.85 → strong RAG hit; route Tier 0 (augmented)
- Cosine similarity 0.65–0.84 → moderate hit; augment + route Tier 1 if medium complexity
- Cosine similarity < 0.65 → no reliable match; escalate based on complexity alone

---

### 21.4 Routing Decision Algorithm

```
Incoming message
│
├─→ [1] Voice mode flag?
│         yes → always Tier 0 (local) or Tier 1 (Groq)
│               never Tier 2/3 — latency unacceptable for voice
│
├─→ [2] Context size check
│         > 8k tokens → cannot use most local models; skip to Tier 1+
│         ≤ 8k → continue
│
├─→ [3] Complexity classification (Tier 0 micro-model or heuristic)
│         light (factual lookup, simple Q&A, short task) → Tier 0
│         medium (reasoning, multi-step, moderate length) → check RAG
│         heavy (novel analysis, long-form, no prior context) → check budget
│
├─→ [4] RAG confidence check
│         hit ≥ 0.85 + light/medium → Tier 0 augmented
│         hit ≥ 0.65 + medium → Tier 1 augmented
│         hit < 0.65 + heavy → skip to budget check
│
├─→ [5] Token budget check (per-tier daily quota)
│         Tier 1 quota available → route Tier 1
│         Tier 1 exhausted → check Tier 2
│         Tier 2 quota available → route Tier 2
│         Tier 2 exhausted → route Tier 3 (log escalation)
│
└─→ [6] User override
          if user pinned a specific model for this conversation → use it
          if user typed /model [name] → use it for this message only
```

**Escalation logging:** Every Tier 3 API call is logged with routing rationale. Weekly summary surfaced in Usage view: "X messages required premium tokens this week — reasons: [context too large / no RAG match / explicit override]." Transparency without nagging.

---

### 21.5 Token Budget Tracking

Gateway maintains a per-tier daily token budget:

```json
{
  "routing.budget.tier1.daily_limit": 100000,
  "routing.budget.tier2.daily_limit": 50000,
  "routing.budget.tier3.soft_limit": 10000,
  "routing.budget.tier3.hard_limit": 50000,
  "routing.budget.reset_hour": 0
}
```

- **Soft limit (Tier 3):** Warn user when approaching. Gateway sends a `usage.warning` event to iOS → displayed as an inline banner in Usage view.
- **Hard limit (Tier 3):** Stop routing to Tier 3. Route to best available lower tier. Never silently fail.
- **Daily reset:** Configurable reset hour (default: midnight local gateway time).
- **No hard limits on Tier 0/1** — local is free, Tier 1 rate limits are enforced by the provider.

---

### 21.6 Model Capability Registry

Gateway maintains a capability map for each configured model. Used by the routing engine:

```json
{
  "llama3.1:8b": {
    "tier": 0,
    "context_window": 8192,
    "strengths": ["general", "summarization", "classification"],
    "max_complexity": "medium"
  },
  "codestral:latest": {
    "tier": 0,
    "context_window": 32768,
    "strengths": ["code"],
    "max_complexity": "heavy"
  },
  "claude-sonnet-4-5": {
    "tier": 3,
    "context_window": 200000,
    "strengths": ["general", "code", "analysis", "long-form"],
    "max_complexity": "heavy"
  }
}
```

This registry is user-configurable — if you add a new local model, you declare its capability tier. Gateway reads it at startup.

---

### 21.7 iOS Surface Layer

Routing is entirely gateway-side. The iOS client surfaces three things:

**1. Message-level model attribution**
Below each assistant message, muted small text showing which model handled it:
```
                    via llama3.1:8b  [local] ○
```
- `[local]` pill = Tier 0
- `[free]` pill = Tier 1  
- `[copilot]` pill = Tier 2
- No pill = Tier 3 (paid API — don't label, don't draw attention)
- Tappable: shows routing rationale sheet ("Used local model — RAG confidence: 0.94, Tier 1 quota conserved today: 48k tokens")

**2. Model override (nav bar)**
Small model indicator pill in chat nav bar. Tappable → opens model picker sheet for this conversation:
- "Auto (recommended)" — default, routing engine decides
- List of available models grouped by tier
- Selection persists for conversation, cleared on new session
- `/model [name]` text command also works inline

**3. Usage view integration**
Usage view (§4.5) already shows per-model breakdown. Add routing summary card:
- "This week: X% local, Y% free cloud, Z% premium"
- Tier 3 escalations with reasons
- "RAG hit rate: 73% of queries resolved with local context"

**iOS does not implement routing logic.** It configures preferences via Settings → Models → Routing Policy and displays attribution. All decisions happen at the gateway.

---

### 21.8 Phase Plan for Routing

| Phase | Routing Capability |
|---|---|
| Phase 1 | Manual model selection only. No automatic routing. User picks model in Settings → Models. |
| Phase 2 | Basic auto-routing: complexity classification + context size guard. Tier 0/1/3 only. |
| Phase 3 | RAG-integrated routing. Cosine similarity thresholds. Dense summaries. Token budget tracking. |
| Phase 4 | Full 4-tier routing. Subscription quota awareness (Copilot, etc.). Escalation logging. Weekly summary in Usage. |
| Phase 5 | Multi-node routing. Task dispatch to specialized nodes (embedding node, inference node). DRM integration. |

Phase 1 ships without any routing intelligence — model selection is manual. This is correct: don't build routing before you have a working app. Routing is Phase 2–4 progressive enhancement.

---

*§21 written 2026-03-23. Gateway-side implementation owner: @backend. iOS surface owner: @frontend.*

---

## §22 — Agent Swarms (Group Chats)

**Owner:** @code_architect  
**Phase:** Phase 2  
**Status:** Architecture designed; implementation deferred from Phase 1

---

### 22.1 What Agent Swarms Are

A swarm is a named multi-agent session where agents collaborate on tasks by @mentioning each other. The user sets the direction; the agents coordinate the execution.

Unlike round-robin routing (Agent 1 responds, then Agent 2, etc.), Polly swarms use **reactive messaging**: agents respond to each other, not just to the user. When Code Architect says "@backend — can you spec the API for this?", the Backend Architect agent genuinely responds to that request in the same thread. The conversation is a real multi-party exchange.

This is the same model as the "Home" group chat in Aight — agents collaborating with each other, the user directing at a high level.

---

### 22.2 Entry Point

From the drawer, tap [+] → **"New Group Chat"**:

```
┌─────────────────────────────────────┐
│ [✕]   New Group Chat                │
│                                     │
│  Group Name                         │
│  [Polly Build Team              ]   │
│                                     │
│  Members                            │
│  [🔍 Search agents...           ]   │
│                                     │
│  ┌─ Select agents ─────────────┐    │
│  │ ☑ 🖥 Code Architect         │    │
│  │ ☑ 🖼 Frontend Developer     │    │
│  │ ☑ 🏗 Backend Architect      │    │
│  │ ☐ ⚡ Design Engineer        │    │
│  │ ☐ 🧪 QA Engineer            │    │
│  └─────────────────────────────┘    │
│                                     │
│  ┌─────────────────────────────┐    │
│  │     Create Group Chat       │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

- Group name: required, free text
- Members: multi-select from agent list, minimum 2 agents
- "Create Group Chat" → creates session, appears in drawer TODAY section with group icon
- Group sessions persist across app restarts

---

### 22.3 Group Chat View

The group chat view is the same `ChatView` component with multi-agent rendering:

```
┌─────────────────────────────────────┐
│ [≡]  👥 Polly Build Team    [+] [⋯]│  ← nav bar
├─────────────────────────────────────┤
│                                     │
│  🖥 Code Architect                  │  ← agent label above bubble
│  ┌───────────────────────────────┐  │
│  │ Let's break this down.        │  │
│  │ @backend — spec the API.      │  │  ← @mention highlighted
│  │ @frontend — start the UI spec.│  │
│  └───────────────────────────────┘  │
│                                     │
│  🏗 Backend Architect               │
│  ┌───────────────────────────────┐  │
│  │ On it. Here's the endpoint    │  │
│  │ design...                     │  │
│  └───────────────────────────────┘  │
│                                     │
│  [🖥 thinking...]  [🏗 thinking...] │  ← thinking toast (per-agent)
│                                     │
├─────────────────────────────────────┤
│ [🎤] [Type a message...      ] [➤] │
└─────────────────────────────────────┘
```

**Multi-agent rendering differences from single-agent chat:**
- Agent name + emoji label above each response bubble (never ambiguous who said what)
- Each agent's bubble uses their `identity.theme` accent color as a left border tint
- @mentions in message text are highlighted (accent color, slightly bold)
- **Thinking toast** (if enabled in Preferences): small floating pill per active agent "🖥 thinking..." — multiple can show simultaneously
- User messages are right-aligned as usual; all agent messages are left-aligned

**[+] in nav bar:** Add an agent to the existing group mid-conversation  
**[⋯] in nav bar:** Group settings — rename, remove members, leave group, delete

---

### 22.4 Swarm Patterns

Four patterns the system prompt architecture should support. Each is set up by the gateway-side group session configuration.

**Pattern 1 — Planning Swarm**
User states a goal. One agent (typically the domain lead) breaks it down and @mentions specialists for their slice. Each specialist contributes their part. User receives a coordinated, multi-perspective plan.

*Example:* "Build the shortcut grid component"
- Code Architect: architecture + data model
- @frontend: component spec + interaction design  
- @qa_guy: test plan
- @security_audit: any security considerations

**Pattern 2 — Review Swarm**
User posts an artifact (code, document, design). Multiple agents review from their domain perspective, responding to the artifact and to each other's observations.

*Example:* Post a PR diff → Code Architect reviews architecture, Security Auditor flags vulnerabilities, QA checks test coverage, all in one thread.

**Pattern 3 — Debate Swarm**
Two agents with explicitly different perspectives (e.g., Strategist + Contrarian, or Optimist + Risk Analyst) argue a decision. User gets both sides worked through before committing.

*Example:* "Should we use expo-router or React Navigation directly?"

**Pattern 4 — Specialist Handoff**
A generalist agent recognizes a question is outside its domain and @mentions the appropriate specialist, then steps back. Clean delegation.

*Example:* User asks Code Architect a security question → Code Architect @mentions Security Auditor → Security Auditor takes over.

---

### 22.5 System Prompt Architecture for Swarms

Each agent in a group chat receives an augmented system prompt that includes:

1. **Group context header** — "You are in a group chat named '[name]' with the following agents: [list]. You are [Agent Name]."
2. **Collaboration protocol** — "@mention another agent by their @username to hand off a task. Respond when @mentioned. Don't speak out of turn unless you have something specific to add."
3. **Role clarity** — "Stick to your domain. Defer to specialists."
4. **The agent's own SOUL.md** — identity layer, unchanged
5. **Constitutional epistemology layer** — always present, non-negotiable

This is entirely gateway-side. iOS sends the message; the gateway injects the group context into each agent's system prompt automatically.

**Turn management:** The gateway routes messages to agents based on @mentions. The no-@mention case requires a deterministic fallback — prompt instructions alone ("hold back unless relevant") are not reliable because LLMs will respond to conversational messages even when instructed not to.

**Phase 1 turn management (simple, reliable):**
- @mention present → only the mentioned agent(s) respond
- No @mention → only the **designated responder** responds (the agent set as `defaultResponder` in the group config, defaults to the first agent added to the group)
- "Anyone want to add something?" style messages → user must @mention explicitly; no implicit broadcast

**Phase 2 turn management (smarter, requires §22.5 resolution):**
- No @mention → coordinator agent (if one exists) routes to the most relevant member based on message content
- Coordinator uses a lightweight classification prompt: "Which agent is best suited to respond to this? Options: [list]. Reply with @handle only."
- Non-coordinator agents in the group have their response gated by coordinator's routing decision
- This requires the gateway to support a two-step dispatch: coordinator responds first with routing decision, then routed agent responds. **This is the §22.5 open question @ai_expert flagged** — the gateway may not natively support two-step dispatch within a single user turn. @backend owns resolution.

**Phase 1 ships with simple deterministic routing.** Phase 2 coordinator routing is a gateway feature, not a client feature.

---

### 22.6 iOS Implementation Notes

**Phase 2 scope:**
- Group chat creation flow (§22.2)
- Multi-agent message rendering (agent labels, color borders, @mention highlights)
- Thinking toast per-agent (controllable via Preferences)
- Group session persistence in drawer TODAY section

**Not Phase 2:**
- Agent-to-agent tool calling within a swarm (Phase 3)
- Swarm templates (pre-configured groups for common patterns — Phase 3)
- Autonomous swarm runs without user in the loop (Phase 4)

**`GroupChatView` vs `ChatView`:**
- `GroupChatView` is not a new component — it's `ChatView` with `isGroup: boolean` prop
- Message rendering differences handled in `MessageBubble` component via `agentLabel?: string` and `agentColor?: string` props
- The gateway handles all multi-agent orchestration; iOS just renders what comes back

**Thinking toast component:**
- Shown when a `chat.typing` event arrives with an agent identifier
- Multiple agents can be typing simultaneously — show all active ones as a horizontal row of pills
- Controlled by Preferences → Group Chat Thinking Toast toggle
- Auto-dismisses when the agent's message arrives

---

### 22.7 Swarm Templates (Phase 3)

Pre-configured named swarms for common workflows. Shown in the New Group Chat flow as a "From Template" option:

| Template | Members | Pattern | Use For |
|---|---|---|---|
| Build Team | Code Architect + Frontend + Backend + QA | Planning | Feature development |
| Code Review | Code Architect + Security Auditor + QA | Review | PR review |
| Architecture Review | Code Architect + Backend + Infra | Debate | System design decisions |
| Full Team | All agents | Ad hoc | Open-ended work |

Templates configurable by user — add custom swarm templates in Phase 3.

---

*§22 written 2026-03-23. Phase 2 feature — deferred from Phase 1. iOS surface owner: @frontend. Gateway orchestration: @backend.*

---

### 22.8 Swarm Coordination Protocol

**Problem this solves:** In a multi-agent swarm with concurrent assignments, the chat thread is an unreliable source of task state. Agent responses arrive asynchronously, early messages scroll out of context windows, and coordinators cannot reliably determine completion. This section defines a coordination layer that uses files as ground truth — the thread is commentary, the files are state.

**Architecture:** Distributed records (Option B — confirmed by @backend: `agents.files.get` supports cross-agent reads, `agents.files.set` is full-file overwrite). Each agent owns their own completion record. No shared write surface, no write contention, no row ownership enforcement needed.

**Phase gate:** Phase 2 — ships with group chat feature.

---

#### File Layout

```
coordinator workspace:
  _swarm/task-[id].md         ← task definition (read-only for members)

each member workspace:
  _swarm/done-[id].md         ← their completion record (written by them alone)
```

**Task definition** (`coordinator workspace/_swarm/task-[id].md`):
```markdown
---
task_id: review-polly-spec-20260324
title: Spec Review — POLLY_IOS_SPEC.md
coordinator: @code_architect
created: 2026-03-24T08:00:00Z
members: [@frontend, @backend, @design_eng, @qa_guy, @security_audit, @infra, @researcher, @ai_expert]
---

## Assignments

- @frontend: Review §4 UI components — all views, nav graph, error states
- @backend: Review §3 WebSocket protocol, §7 networking, §22 swarm RPCs
- @security_audit: Review §8 security, §20.4 onboarding auth, §4.8 data privacy
[...]
```

This file is written by the coordinator at task creation. Members read it to know their assignment. Members **never write to it** — integrity is preserved by workspace scope (members cannot `agents.files.set` to the coordinator's workspace).

**Completion record** (each member's `_swarm/done-[id].md`):
```markdown
---
task_id: review-polly-spec-20260324
agent: @security_audit
status: done          # in_progress | done | blocked
signal: "::DONE blockers=3 gaps=6 suggestions=3::"
updated: 2026-03-24T09:15:00Z
---

## Summary
B1 closed (wrote §4.8 security screen + §20.4 security sub-flows). B2 closed (LAN TLS ruling). B3 closed (push registration gateway fix scoped).

## Blockers
(none open)
```

Each agent writes only their own file. No agent can write another agent's completion record.

---

#### Structured Completion Signals

Agents post a machine-readable signal as the last line of their assignment message and mirror it in their `done-[id].md`:

```
::DONE reviewer=@frontend blockers=4 gaps=6 suggestions=3::
::BLOCKED reviewer=@security_audit reason=§20.4+§4.8-missing::
::CLAIM task=spec-review agent=@qa_guy::
::RELEASE task=spec-review agent=@qa_guy reason=reassigned::
::CONTEXT_FLUSH agent=@researcher summary_at=memory/2026-03-24.md::
```

| Signal | Meaning | Who sends |
|--------|---------|-----------|
| `::CLAIM::` | Agent starting work | Assignee, at task start |
| `::DONE::` | Assignment complete | Assignee, when finished |
| `::BLOCKED::` | Stalled, needs coordinator action | Assignee, immediately |
| `::RELEASE::` | Releasing assignment | Assignee or coordinator |
| `::CONTEXT_FLUSH::` | Agent compressed context to memory | Any agent, when flushing (see §22.9) |

---

#### Coordinator Aggregation

The coordinator reads completion state by fetching each member's `done-[id].md` via `agents.files.get` (cross-agent reads confirmed supported). Status of agents who haven't written their file yet = implicitly `not_started`. No initialization race — the task board *emerges* from the union of individual records.

The coordinator can query status at any time: *"What's the current review status?"* → Polly reads all member `done` files and responds with a structured summary. No thread-reading, no context window dependency.

---

#### Review Status Card (iOS UI)

When a group chat has an active task, a **Review Status Card** is pinned above the input bar:

```
┌─────────────────────────────────────┐
│ 📋 Spec Review  6/8 complete        │
│ ⬜ @qa_guy   🔴 @security_audit     │
│ 🔴 3 open blockers     [Details ›]  │
└─────────────────────────────────────┘
```

- Reads from member `done` files — not message history
- Updates in real-time as signals arrive
- `[Details ›]` opens full task board sheet (one row per member, expandable)
- Auto-dismisses when all members are `done`
- Color coding: ⬜ in_progress · ✅ done · 🔴 blocked · ⏸ not_started · 🔄 context_flushed

**Component:** `SwarmTaskBoardCard` — Phase 2. Group chat view only, above augmentation pills, below nav bar.

---

#### Coordinator Gate

When the coordinator tries to close a task with members still `in_progress` or `blocked`, the app warns:

> *"2 agents haven't confirmed yet (@qa_guy, @security_audit). Close anyway?"*

**Close anyway** (logged to coordinator's task definition) · **Wait** (dismiss). Advisory — coordinator can always override deliberately.

---

#### Implementation Notes

- **Persistence:** `agents.files.set/get`. No new gateway RPCs.
- **Cross-agent reads:** Confirmed supported — coordinator can read any member's workspace file.
- **Write isolation:** Each agent writes only their own workspace. No shared write surface, no contention, no spoofing vector (@security_audit).
- **Task definition integrity:** Members cannot write to coordinator's workspace — workspace scope enforces read-only access to the task definition.
- **Task lifecycle:** Task definition created at assignment; member `done` files created as agents claim/complete. All files archived to `_swarm/archive/` when coordinator closes. Pruned after 30 days.
- **Task ID format:** `[slug]-[YYYYMMDD]`, coordinator-assigned or auto-generated from task title.

---

### 22.9 Cross-Team Bridge Agents

Teams are intentionally isolated — sessions, memory, and group chats are all scoped to a single team. But there are legitimate use cases for cross-team communication: the Dev Squad needs input from the Marketing Engine; the Life Team's coach surfaces a question that belongs in the Finance Team; a user wants a high-level synthesis across all teams.

Three tiers of bridge capability, in ascending complexity:

---

#### Tier 1 — Persona-Level Bridge (Phase 3, client-side only)

A bridge agent is an agent whose **SOUL explicitly knows about other teams** and can relay information between them via the user as the carrier. No new gateway infrastructure required.

**How it works:**
1. User creates a "Bridge" agent (or a team template includes one)
2. The bridge agent's SOUL contains a team registry: names, purposes, and key agents in each team
3. When the user asks "What would the Finance Team think about this?", the bridge agent answers from its embedded knowledge of that team's perspective
4. For live cross-team consultation: user pastes the question into the other team's chat, gets the answer, pastes it back. The bridge agent helps synthesize.

**Team registry format (in bridge agent SOUL):**
```
## Team Registry

I have working knowledge of the following teams:

**Dev Squad** — Build, test, secure, ship. Key agents: @code_architect, @frontend, @backend, @security_audit. Best for: technical implementation, architecture decisions.

**Marketing Engine** — Acquisition, growth, analytics. Key agents: @growth, @content, @analytics. Best for: go-to-market, messaging, channel strategy.

[...one entry per team...]
```

**Limitation:** The bridge's knowledge of other teams is static — it reflects the state of the SOUL when written. It can answer "what would they think?" but it cannot actually talk to them.

---

#### Tier 2 — Async Cross-Team Mailbox (Phase 4, requires file tools)

Teams can send structured requests to each other via a **shared mailbox pattern** using `agents.files.set/get`. No real-time session required.

**Mechanism:**
- Each team has a designated **liaison agent** (can be any agent — just needs the liaison role in its SOUL)
- Outbound: Team A's liaison writes a request to a shared mailbox directory: `_mailbox/[team-b-id]/[request-id].md`
- Inbound: Team B's liaison reads from `_mailbox/[team-b-id]/` on session start, processes requests, writes responses to `_mailbox/[team-a-id]/responses/[request-id].md`
- Team A's liaison checks for responses on its next session start

**This works today** — `agents.files.get` supports cross-workspace reads (same gateway). The mailbox directory just needs to be in a workspace both liaisons can access (the coordinator's workspace, or a dedicated shared workspace).

**Phase 4 iOS work:** Surface cross-team request status in Today view — "Dev Squad → Marketing Engine: 1 pending request." Tap to view.

---

#### Tier 3 — Real-Time Cross-Team Session (Phase 5, aspirational)

A group chat that includes agents from multiple teams simultaneously. User creates a session, invites `@code_architect` from Dev Squad and `@growth` from Marketing Engine into the same conversation.

**Gateway requirement:** Multi-workspace session membership — a session key that spans two team workspaces. Not currently supported in OpenClaw. This is a future gateway feature request, not a client-side problem.

**Phase gate:** Blocked on OpenClaw upstream support. Spec here is a design intent marker only.

---

**Summary:**

| Tier | Phase | Who does the work | Complexity |
|------|-------|-------------------|------------|
| Tier 1: Persona bridge | 3 | Agent template author | Low — SOUL content only |
| Tier 2: Async mailbox | 4 | @backend (mailbox spec) + @infra (shared workspace) | Medium |
| Tier 3: Real-time cross-team | 5 | OpenClaw upstream + @backend | High |

**Recommendation:** Ship Tier 1 in Phase 3 as a built-in "Liaison" agent in multi-team setups. Users get immediate value with zero infrastructure changes.

---

**Owner:** @code_architect  
**Date:** March 23, 2026  
**Status:** Architectural design — applies to all long-horizon work, not just dev

---

### 23.1 Philosophy

Aight has no spec-driven development framework. Agent swarms fail at long-horizon work because context is ephemeral, progress is invisible, and every plan looks different. A new swarm session has no reliable way to answer "where did we leave off?" without manual re-briefing.

Polly closes this gap with a simple, rigorous convention: the **Plans Layer**. Every plan — whether a software build, a business strategy, a home project, or a reading list — follows the same document format. Agents and the iOS UI both understand it. Nothing more complicated than structured markdown.

**The key principle: consistency over sophistication.** A simple format that every agent always follows is worth more than a sophisticated system that gets bypassed.

---

### 23.2 Plans Directory

Plans live in a `plans/` directory at the gateway workspace root:

```
~/.polly/plans/
  polly-ios-build.md          ← active
  model-routing-engine.md     ← active
  moltbook-phase2.md          ← draft
  agent-templates.md          ← complete
  home-renovation-2026.md     ← active (non-dev example)
  reading-list.md             ← active (non-dev example)
```

Each file is a single plan. One plan per file. Filename = plan `id` + `.md`.

Plans are **first-class workspace objects** — readable by all agents in that workspace, injectable as context into swarm sessions, surfaced in the Polly iOS Plans view.

---

### 23.3 Canonical Plan Format

Every plan follows this exact structure. No exceptions. The frontmatter schema is enforced by the gateway's `plans` RPC layer.

```markdown
---
id: polly-ios-build
title: Polly iOS App — Phase 1 Build
status: active
phase: 1
owner: code_architect
created: 2026-03-23
updated: 2026-03-23
tags: [ios, build, polly]
depends_on: []
spec_ref: POLLY_IOS_SPEC.md
---

## Summary
One paragraph. What this plan is, why it exists, what success looks like. 
Written for a reader with no prior context.

## Goals
- [x] Create POLLY_IOS_SPEC.md
- [x] Complete screenshot review
- [ ] Write POLLY_AGENT_TEMPLATES.md
- [ ] Bootstrap Expo project structure
- [ ] Ship Phase 1 to TestFlight

## Decisions
All locked decisions. Append-only — never remove a row, only add or annotate.

| Decision | Date | Rationale |
|---|---|---|
| React Native + Expo (not Swift) | 2026-03-01 | expo-openclaw-chat requirement |
| iOS speaks only to OpenClaw WebSocket | 2026-03-10 | Architecture lock |
| Navigation = Drawer pattern | 2026-03-15 | Custom DrawerPanel, not react-navigation/drawer |

## Tasks

### Phase 1
- [x] Spec §1–§15 initial write
- [x] Screenshot review (all views)
- [ ] POLLY_AGENT_TEMPLATES.md
- [ ] Expo project bootstrap
- [ ] ChatView + GatewayClient integration
- [ ] Today view
- [ ] Shortcuts view

### Phase 2
- [ ] Group chat rendering
- [ ] Agent detail 6-tab view
- [ ] Basic model routing

## Open Questions
- [ ] Should DateStrip use FlashList or FlatList internally?
- [ ] Moltbook Phase 2: gateway skill install flow UX?

## Log
Append-only. Never edit existing entries. One line per event.

- 2026-03-23: §21 Model Routing written; §22 Agent Swarms written; spec at 5,063 lines
- 2026-03-23: Screenshot review complete — all 9 Settings sub-views, agent detail, all main views
- 2026-03-15: Architecture locked — iOS client only, OpenClaw unchanged engine
- 2026-03-01: Project initiated
```

---

### 23.4 Frontmatter Schema

| Field | Type | Required | Values |
|---|---|---|---|
| `id` | string | ✓ | kebab-case, matches filename |
| `title` | string | ✓ | Human-readable |
| `status` | enum | ✓ | `draft` · `active` · `blocked` · `complete` · `archived` |
| `phase` | int or null | — | Current active phase number |
| `owner` | string | ✓ | Agent username (kebab-case) |
| `created` | date | ✓ | ISO 8601 |
| `updated` | date | ✓ | ISO 8601, updated on every edit |
| `tags` | string[] | — | Free tags for filtering |
| `depends_on` | string[] | — | Plan IDs this plan depends on |
| `spec_ref` | string | — | Path to canonical spec file if separate |
| `blocked_by` | string | — | Free text reason when status = `blocked` |

---

### 23.5 Section Rules

**Summary:** One paragraph. Rewritten as needed. The single paragraph an agent reads to get oriented in 10 seconds.

**Goals:** Top-level outcomes. Checkboxes. Marked `[x]` when done. Never deleted — completion is visible history.

**Decisions:** Locked decisions table. Append-only. Date + rationale required. This is the institutional memory — new swarm members read Decisions before anything else to avoid re-litigating settled questions.

**Tasks:** Implementation steps, organized by phase or milestone. Checkboxes. `[x]` = complete. Agents update these as work is done. This is the machine-readable progress layer.

**Open Questions:** Unresolved decisions. `[x]` when resolved (add the resolution to Decisions table). Never deleted.

**Log:** Append-only journal. One line per meaningful event with date prefix. Never edit existing lines. This is the timeline — how we got here, in order.

---

### 23.6 Plans RPC Layer

Gateway exposes a thin RPC layer over the `plans/` filesystem:

```
plans.list          → [PlanSummary]         list all plans (frontmatter only, no body)
plans.list(status)  → [PlanSummary]         filter by status
plans.get(id)       → Plan                  full plan document
plans.update(id, patch) → Plan             update frontmatter fields
plans.task.complete(id, taskText) → Plan   mark a task [x] by text match
plans.log(id, entry) → Plan               append a log line with today's date
plans.create(plan)  → Plan                create new plan from template
```

Agents call these RPCs to query and update plans without reading/writing raw files. The iOS client calls them for the Plans view.

`plans.log` is the key RPC for swarm use — agents append a log entry when they complete a meaningful piece of work. This creates an automatic audit trail of swarm activity without any user intervention.

---

### 23.7 Swarm Context Injection

When a group chat session starts, the gateway checks if any active plan is associated with that group (via `tags` or explicit `swarm` frontmatter field). If found, it prepends a context block to the group session:

```
[PLAN CONTEXT: polly-ios-build]
Title: Polly iOS App — Phase 1 Build
Status: active | Phase: 1 | Owner: code_architect

Summary: [one-paragraph summary]

Current incomplete tasks (Phase 1):
- [ ] POLLY_AGENT_TEMPLATES.md
- [ ] Expo project bootstrap
- [ ] ChatView + GatewayClient integration

Open questions:
- [ ] Should DateStrip use FlashList or FlatList internally?

Last 5 log entries:
- 2026-03-23: §21 Model Routing written; spec at 5,063 lines
...
[END PLAN CONTEXT]
```

Every agent in the swarm starts oriented. No re-briefing. No "where did we leave off?" The plan is the persistent memory across sessions.

This injection is automatic when a plan's `tags` intersect with the group's tags, or when a plan explicitly lists the group ID in a `swarm` field.

---

### 23.8 iOS Plans View

Accessible from the drawer (below agent list) or via a dedicated entry in the Today section.

```
┌─────────────────────────────────────┐
│ [<]  Plans                   [+]   │
│                                     │
│  [All] [Active] [Draft] [Complete] │  ← status filter chips
│                                     │
│  ┌───────────────────────────────┐  │
│  │ ● Polly iOS Build             │  │  ← status dot (green=active)
│  │ Phase 1 · @code_architect     │  │
│  │ 3 of 8 tasks complete         │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ ● Model Routing Engine        │  │
│  │ Phase 3 · @backend            │  │
│  │ 0 of 5 tasks complete         │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │ ○ Moltbook Phase 2            │  │  ← draft = hollow dot
│  │ Draft · @code_architect       │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Plan detail view** (tap any plan):
- Rendered markdown of the full plan document
- Inline task checkboxes — tappable to mark complete (calls `plans.task.complete`)
- [Edit] button — opens frontmatter editor for status, owner, phase
- [Log Entry] FAB — quick-add a log line
- Swipe left on a task row → "Assign to agent" → routes a message to that agent with the task as context

**[+] New Plan:** Opens a blank plan template with frontmatter pre-filled (id derived from title, status=draft, owner=current agent, today's date).

---

### 23.9 Non-Dev Use Cases

The Plans Layer is explicitly not just for software development. Same format, same tooling, same swarm injection:

| Plan | Tags | Swarm Use |
|---|---|---|
| `home-renovation-2026.md` | home, projects | Researcher finds contractors, Strategist evaluates bids |
| `reading-list.md` | reading, learning | AI Expert suggests reads, Researcher summarizes finished books |
| `business-strategy-2026.md` | strategy, business | Strategist + Contrarian debate each goal |
| `health-goals.md` | health, personal | Weekly log reviews, milestone tracking |
| `travel-japan-2027.md` | travel, planning | Researcher builds itinerary, logs decisions |

The format is the framework. The content can be anything with a goal, decisions, tasks, and a timeline.

---

### 23.10 Relationship to POLLY_IOS_SPEC.md

`POLLY_IOS_SPEC.md` is a **spec document**, not a plan. Plans reference specs via `spec_ref`. The distinction:

- **Spec:** What the thing is. Requirements, design, constraints. Edited as understanding deepens.
- **Plan:** How we build it. Tasks, decisions, progress, log. Evolves as work proceeds.

The Polly build has both: the spec (`POLLY_IOS_SPEC.md`) defines what Polly is; the plan (`polly-ios-build.md`) tracks how we get there. Agents read the spec for requirements, the plan for current status.

---

*§23 written 2026-03-23. Universal to all long-horizon work — dev and non-dev. Gateway plans RPC owner: @backend. iOS Plans view owner: @frontend.*

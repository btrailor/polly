# TESTING_AND_QA_SPEC.md

Phase 1–3 — Testing Strategy, Infrastructure, and Quality Gates  
Status: Draft  
Owners: @qa_guy (test strategy, acceptance criteria), @code_architect (infra), @frontend (iOS tests), @backend (gateway tests)  
Last updated: 2026-03-25  
Cross-references: `VOICE_BEHAVIOR_TESTS.md`; `POLLY_IOS_SPEC.md` §3, §8; `SECURITY_IMPLEMENTATION_SPEC.md`; `SENSIBILITY_SYSTEM_SPEC.md`; `MODEL_ROUTING_SPEC.md`; `SWARM_COORDINATION_SPEC.md`; `openspec/changes/phase-1-ios-foundation/tasks.md`

---

## 1. Current State

**Test infrastructure: Zero.** No Jest config. No test runner. No test files. No test scripts in `package.json`. No `@testing-library/react-native`. No Detox/Maestro/Appium for E2E. The `devDependencies` in `package.json` contain only TypeScript.

**Test specs: One** — `VOICE_BEHAVIOR_TESTS.md` (544 lines, 30+ test cases across 7 sections). Excellent structure: clear cases, anti-assertions, three evaluation methods (automated, LLM-graded, human review). But covers only voice components.

**The gap is total.** No test strategy, no test infrastructure, no acceptance criteria for non-voice features, no approach for testing WebSocket protocol, no integration test plan for gateway connection, no auth handshake verification, no regression strategy, no CI pipeline.

---

## 2. Test Surface Map

### 2.1 By Layer

| Layer | What | Test Type | Phase |
|-------|------|-----------|-------|
| Protocol | WebSocket connect, auth handshake, challenge-response, session management, streaming, reconnect | Integration (mock gateway) | 1 |
| Auth | Ed25519 keygen, signing, deviceToken rotation, TOFU cert pinning, token storage | Unit + integration | 1 |
| State | Zustand stores (chat, agent, connection, today), MMKV persistence, reactivity | Unit tests | 1 |
| Components | ChatBubble, StreamingCursor, MarkdownRenderer, VoiceMicButton, DrawerPanel, AgentAvatar, MessageList, InputBar | Component tests (RNTL) | 1 |
| Flows | Onboarding, team provisioning, session lifecycle, message send/receive, voice recording | Integration tests | 1 |
| Routing | Model selection, per-agent override, tier classification, budget guard | Unit tests (pure logic) | 2 |
| Knowledge | FAISS indexing, retrieval, DIRECT/ADJACENT/ABSENT classification, graph traversal | Integration (test index) | 2 |
| Swarm | Group creation, fan-out, multi-agent streaming, task tracking, phase management | Integration | 2 |
| Sensibility | Theme switching, token application, behavior injection, texture overlays | Component + visual regression | 3 |
| Security | Secure store ops, auth flow, credential lifecycle, sign-out cleanup, file protection | Unit + integration | 1 |
| Augmentation | Vault note injection, mental model framing, PollyEnhancement pipeline | Unit tests | 1 |

### 2.2 By Risk

| Risk | Priority | Why |
|------|----------|-----|
| Auth handshake fails silently | P0 | App is unusable without gateway connection. Wrong signing = permanent auth failure. |
| Streaming rendering corrupts | P0 | Interleaved deltas + 250ms flush + concurrent group streams = many edge cases. |
| Credential leaks to logs | P0 | Private keys, tokens, sendKey in console output = security incident. |
| Message cache inconsistency | P1 | Cache diverges from gateway on reconnect → stale/missing messages. |
| Store persistence fails | P1 | MMKV write fails silently → settings lost on restart. |
| Theme token mismatch | P2 | Component uses old token name after refactor → crash or wrong color. |
| Routing decision wrong | P2 | Tier 0 model handles Tier 3 query → bad response. Budget guard fails → surprise bill. |
| Group chat ordering | P2 | 5 agents arrive interleaved → render in wrong order. |

---

## 3. Test Infrastructure

### 3.1 Phase 1 Dependencies

```json
{
  "devDependencies": {
    "@types/react": "~19.2.2",
    "typescript": "~5.9.2",
    "jest": "^29.7.0",
    "jest-expo": "~52.0.0",
    "@testing-library/react-native": "^12.4.0",
    "@testing-library/jest-native": "^5.4.0",
    "jest-fetch-mock": "^3.0.0",
    "@jest/coverage": "^29.7.0"
  },
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --reporters=default --reporters=jest-junit"
  }
}
```

### 3.2 Jest Configuration

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-expo',
  setupFilesAfterFramework: ['@testing-library/jest-native/extend-expect'],
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?|@expo(nent)?/.*|@shopify/flash-list|react-native-reanimated|react-native-gesture-handler|react-native-mmkv|lucide-react-native|zustand)/)',
  ],
  moduleNameMapper: {
    '^expo-secure-store$': '<rootDir>/__mocks__/expo-secure-store.ts',
    '^expo-haptics$': '<rootDir>/__mocks__/expo-haptics.ts',
    '^react-native-mmkv$': '<rootDir>/__mocks__/react-native-mmkv.ts',
    '^expo-speech-recognition$': '<rootDir>/__mocks__/expo-speech-recognition.ts',
    '^expo-keep-awake$': '<rootDir>/__mocks__/expo-keep-awake.ts',
    '^@noble/ed25519$': '<rootDir>/__mocks__/@noble/ed25519.ts',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    'app/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThresholds: {
    global: {
      statements: 60,
      branches: 50,
      functions: 60,
      lines: 60,
    },
  },
};
```

### 3.3 Required Native Module Mocks

These mocks are load-bearing. Without them, any test importing a component that uses secure store, MMKV, or haptics will crash.

```
__mocks__/
  expo-secure-store.ts      — in-memory Map<string, string>
  expo-haptics.ts           — no-op functions
  react-native-mmkv.ts      — in-memory Map with get/set/delete/clearAll
  expo-speech-recognition.ts — mock start/stop/results
  expo-keep-awake.ts        — no-op
  expo-local-authentication.ts — configurable success/failure
  @noble/
    ed25519.ts              — deterministic test keypair (known fixed seed)
```

These must be written before the first test. They enable every subsequent test file.

### 3.4 Protocol Mock Server

The highest-value infrastructure piece. Simulates OpenClaw gateway WebSocket behavior in Jest — challenge-response, streaming events, error codes, reconnect — without requiring a real gateway running.

```typescript
// __mocks__/gateway-mock-server.ts
class MockGatewayServer {
  private handlers: Map<string, (params: unknown) => unknown> = new Map();
  
  onMethod(method: string, handler: (params: unknown) => unknown) {
    this.handlers.set(method, handler);
  }
  
  sendEvent(type: string, data: unknown) { /* emit to connected client */ }
  sendDelta(sessionKey: string, delta: string) { /* send chat delta event */ }
  sendFinal(sessionKey: string, text: string) { /* send chat final event */ }
  completeWithNoReply(sessionKey: string) { /* send final with NO_REPLY */ }
  simulateDisconnect() { /* close WebSocket */ }
}
```

Enables: all protocol tests, flow tests, state management tests in CI without external dependencies.

### 3.5 CI Pipeline

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 18 }
      - run: cd polly-ios && npm ci
      - run: cd polly-ios && npm test -- --ci --coverage
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: polly-ios/coverage/
```

### 3.6 Phase 2: E2E Testing (Maestro)

Maestro recommended for Expo apps: YAML-based, runs on iOS simulator, no native compilation needed, supports gesture simulation.

```yaml
# maestro/flows/onboarding.yaml
appId: com.polly.ios
---
- launchApp
- assertVisible: "Welcome to Polly"
- tapOn: "Enter your gateway URL"
- inputText: "ws://192.168.1.100:18789"
- tapOn: "Test Connection"
- assertVisible: "Connected"
```

Not recommended: Detox (requires native compilation, complex Expo setup). Appium (slow, brittle).

---

## 4. Test Specifications

### 4.1 Protocol & Auth Tests

**TEST-PROTO-001** — Connect with static auth token  
Setup: Mock WebSocket server that sends connect.challenge  
Assert: Server receives valid connect params; client enters connected state

**TEST-PROTO-002** — Connect with device auth (Ed25519)  
Setup: Mock server with challenge nonce  
Assert: Signature verifies against public key; `deviceId = SHA-256(publicKey)`

**TEST-PROTO-003** — Signature payload format (v2 with nonce)  
Assert: Payload matches `"v2|{deviceId}|openclaw-ios|ui|operator|operator.read,operator.write,operator.admin|{signedAtMs}|{authToken}|{nonce}"` character-by-character

**TEST-PROTO-004** — deviceToken rotation  
Assert: New token stored in expo-secure-store; old token replaced on every connect

**TEST-PROTO-005** — deviceToken mismatch → fallback to static token  
Setup: Server returns `AUTH_DEVICE_TOKEN_MISMATCH`  
Assert: Client clears stored deviceToken; retries with static token

**TEST-PROTO-006** — Streaming: delta → final rendering  
Setup: 5 delta events followed by final  
Assert: Text accumulates correctly; bubble marked complete on final

**TEST-PROTO-007** — Streaming: NO_REPLY suppression  
Assert: No message bubble rendered when final text is `"NO_REPLY"`

**TEST-PROTO-008** — Streaming: HEARTBEAT_OK suppression  
Assert: No message bubble rendered when final text is `"HEARTBEAT_OK"`

**TEST-PROTO-009** — Reconnect on tick timeout  
Assert: Client closes WebSocket after 2× tick interval; reconnect with exponential backoff

**TEST-PROTO-010** — Reconnect preserves session  
Assert: Same sessionKey used after reconnect; sessions.list called to restore state

**TEST-PROTO-011** — connect.challenge mid-connection  
Setup: Server sends connect.challenge while connected (server restart)  
Assert: Client re-handshakes immediately

**TEST-PROTO-012** — seq gap detection  
Setup: Events with seq 1, 2, 4 (gap at 3)  
Assert: Gap flagged in client state

**TEST-PROTO-013** — Idempotency key prevents duplicate sends  
Assert: Both sends on retry use same `idempotencyKey`

### 4.2 Security Tests

**TEST-SEC-001** — Ed25519 keypair generation on first launch  
Assert: Private key stored in expo-secure-store  
Anti-assert: Private key NEVER appears in console.log output

**TEST-SEC-002** — deviceId derivation matches reference implementation  
Setup: Known public key bytes  
Assert: `deviceId === SHA-256(publicKeyBytes).hex`

**TEST-SEC-003** — Credentials never in log output  
Steps: Capture all console output during full auth flow  
Assert: No output contains private key bytes, deviceToken, sendKey, or auth token (grep known credential substrings)

**TEST-SEC-004** — Sign-out clears all SECURE_STORE_KEYS  
Steps: Store test values for all keys; call `signOut()`  
Assert: Every key returns `null` from expo-secure-store

**TEST-SEC-005** — Secure store unavailable (no device passcode)  
Setup: Mock expo-secure-store to throw on write  
Assert: App blocks at "Passcode Required" screen; does not proceed to onboarding

**TEST-SEC-006** — TOFU cert pinning stores fingerprint  
Steps: User accepts self-signed cert  
Assert: Fingerprint stored in expo-secure-store; subsequent connects compare

**TEST-SEC-007** — TOFU cert mismatch blocks connection  
Setup: Stored fingerprint differs from presented cert  
Assert: Connection blocked; "Certificate Changed" warning shown

**TEST-SEC-008** — Cloudflare Tunnel URL in Keychain, not MMKV  
Assert: URL in expo-secure-store, NOT in MMKV or UserDefaults

**TEST-SEC-009** — Deep link validation rejects unknown session keys  
Steps: Navigate to `polly://chat/fake-session-key`  
Assert: App does not navigate to nonexistent session; shows error or ignores

### 4.3 State Management Tests

**TEST-STATE-001** — chatStore: pendingAugmentation clears after send  
Assert: `pendingAugmentation === null` after send

**TEST-STATE-002** — agentStore: team switch updates agent list  
Assert: `agents` array contains only agents from new team

**TEST-STATE-003** — connectionStore: reconnect cycle transitions  
Assert: `connected → disconnect → connecting → connected` fires in order

**TEST-STATE-004** — MMKV persistence survives component unmount/remount  
Assert: MMKV values readable after full remount cycle

**TEST-STATE-005** — Zustand session store does NOT persist (by design)  
Assert: chatStore is empty on remount (session-only — not persisted to MMKV)

**TEST-STATE-006** — Draft text preservation across app background  
Assert: Text still present in input field after simulated background + foreground

### 4.4 Component Tests

**TEST-COMP-001** — ChatBubble: user vs assistant alignment  
Assert: User bubble right-aligned; assistant bubble left-aligned

**TEST-COMP-002** — ChatBubble: streaming cursor visible only while streaming  
Assert: Cursor visible when `isStreaming=true`; invisible when `false`

**TEST-COMP-003** — ChatBubble: error state shows retry button  
Assert: When `isError=true`, retry button visible; `onRetry` fires on tap

**TEST-COMP-004** — ChatBubble: long-press triggers context menu  
Assert: `onLongPress` fires; context menu includes Copy

**TEST-COMP-005** — MarkdownRenderer: code block renders with copy button  
Input: Markdown with ` ```python ` code block  
Assert: Copy button visible in code block header

**TEST-COMP-006** — MarkdownRenderer: wikilinks render as styled text  
Input: `"See [[My Note]] for details"`  
Assert: "My Note" rendered with link styling

**TEST-COMP-007** — InputBar: mic/send toggle  
Assert: Empty input → mic visible, send hidden; text present → send visible, mic hidden

**TEST-COMP-008** — InputBar: send disabled when empty  
Assert: Send button not tappable when input is empty

**TEST-COMP-009** — AugmentationPill: dismissible on tap  
Assert: Pill visible; tap ✕ → pill removed; augmentation cleared from store

**TEST-COMP-010** — DrawerPanel: spring physics animation  
*Human review — animation feel, 300ms, parallax*

**TEST-COMP-011** — AgentAvatar: emoji on dark rounded-square background  
Assert: Avatar renders with background View, not bare Text emoji

**TEST-COMP-012** — MessageList: auto-scroll on new message  
Assert: List scrolls to show new message when user is at bottom

**TEST-COMP-013** — MessageList: scroll lock when user scrolled up  
Setup: User scrolls up 200pt; new streaming message arrives  
Assert: List does NOT auto-scroll; scroll-to-bottom button appears

**TEST-COMP-014** — ThemeProvider: all components use tokens from context  
Steps: Switch from Reas to Fidenza  
Assert: `bgPrimary`, `accent`, `textPrimary` update on all components  
Anti-assert: No hardcoded hex values survive theme switch

### 4.5 Voice Tests

Already specced in `VOICE_BEHAVIOR_TESTS.md` (30+ tests). Test file mapping:

```
src/__tests__/voice/
  useVoiceRecording.test.ts    — TEST-V-001 through TEST-V-015
  VoiceMicButton.test.tsx      — TEST-V-030 through TEST-V-035
  VoiceDraftPrompt.test.tsx    — TEST-V-040 through TEST-V-053
  voice-integration.test.tsx   — TEST-V-060 through TEST-V-062
```

### 4.6 Flow / Integration Tests

**TEST-FLOW-001** — Cold start → onboarding → connected  
Assert: Onboarding shown; enter URL + token; connected state reached

**TEST-FLOW-002** — Warm start → session restore  
Assert: Skips onboarding; connects to stored gateway; restores last active session

**TEST-FLOW-003** — Send message → receive streaming response  
Assert: User bubble appears immediately; assistant streams; complete message shown

**TEST-FLOW-004** — Message send failure → retry  
Assert: Error bubble shown; retry sends same message with same `idempotencyKey`

**TEST-FLOW-005** — Agent switch → new session  
Assert: Chat clears; new sessionKey used; agent name updates in nav bar

**TEST-FLOW-006** — Team provisioning (6 agents)  
Assert: 6 agents created on gateway; SOUL.md written; drawer shows all 6

**TEST-FLOW-007** — Augmented message send  
Assert: Outgoing message contains `<context>` + `<framing>` + user text in correct order

### 4.7 Gateway Protocol Compliance Tests

**TEST-GW-001** — Wire frame format  
Assert: All outgoing frames have `type: "req"`, `id: uuid`, `method`, `params`

**TEST-GW-002** — connect params match spec exactly  
Assert: `client.id === "openclaw-ios"`, `mode === "ui"`, `role === "operator"`, `scopes === ["operator.read","operator.write","operator.admin"]`

**TEST-GW-003** — chat.send params correct  
Assert: `sessionKey` matches `"agent:{agentId}:main"`, `idempotencyKey` is valid UUID, `deliver === false`

**TEST-GW-004** — Group chat: agent RPC with groupId  
Assert: Uses `agent` method (not `chat.send`); `groupId` present; `label` matches group name

**TEST-GW-005** — sessions.list called on reconnect  
Assert: After successful reconnect, `sessions.list` is called

**TEST-GW-006** — config.patch format correct  
Assert: Uses `raw` param with JSON string; includes `note` param

---

## 5. Testing Agent Behavior

Traditional assertions can't verify AI personality. Use LLM-graded evaluation (pattern from `VOICE_BEHAVIOR_TESTS.md`).

### 5.1 SOUL Compliance Tests

**TEST-SOUL-001** — Constitutional layer present  
Method: LLM-graded (5 runs, 4/5 threshold)  
Assert: Response to "Explain your epistemological commitments" references cui bono, material analysis, or scapegoat suspicion

**TEST-SOUL-002** — Agent stays in domain  
Method: LLM-graded  
Assert: Writer agent defers or redirects on code question; does not hallucinate capabilities

**TEST-SOUL-003** — Context management triggers at ~80 messages  
Method: Automated (mock 85 messages)  
Assert: Memory file written; context flush signal posted

**TEST-SOUL-004** — Memory write format  
Assert: File contains `## Goal`, `## Decisions`, `## Reasoning`, `## Context for continuation`

**TEST-SOUL-005** — Blocker reporting within 2 responses  
Method: LLM-graded  
Assert: Agent reports blocker within 2 responses when info is missing

### 5.2 Sensibility Behavior Tests

**TEST-SENS-001** — Jetset: maximum restraint  
Method: LLM-graded  
Assert: Project plan response has ≤4 main concepts; no decorative language

**TEST-SENS-002** — Ghost Box: allusive, not direct  
Method: LLM-graded  
Assert: Definition response is indirect, reference-based, slightly incomplete

**TEST-SENS-003** — Sensibility does not override constitutional layer  
Method: LLM-graded  
Assert: Constitutional reasoning present regardless of active sensibility

### 5.3 LLM Grading Framework

```typescript
interface LLMTestCase {
  id: string;
  description: string;
  setup: { agent: string; sensibility?: string; mentalModel?: string };
  prompt: string;
  graderPrompt: string;   // What to ask the grading LLM
  passThreshold: number;  // Minimum passing runs out of N (default: 5)
  antiAssertions: string[]; // Patterns that indicate failure regardless of pass
}
```

Run each test N times (default: 5). Pass if ≥ threshold pass. **Never self-grade** — grader model must differ from agent model (if agent runs Sonnet, grade with GPT-4; if agent runs Llama, grade with Claude).

---

## 6. Visual Regression Testing (Phase 3)

For the sensibility picker, visual consistency across themes matters.

**Approach:** `react-native-view-shot` + pixelmatch (or Maestro visual comparison)

| Screen | What Changes Per Theme | What Must NOT Change |
|--------|----------------------|---------------------|
| Chat (with messages) | Bubble colors, border radius, bubble style | Message content, layout structure, spacing |
| Input bar | Background, border, button color | Touch targets, spacing |
| Drawer | Background, text, accent | Navigation structure, agent list |
| Settings | Card colors, text, accent | Layout, row content |

---

## 7. Test File Structure

```
polly-ios/
  __mocks__/
    expo-secure-store.ts
    expo-haptics.ts
    react-native-mmkv.ts
    expo-speech-recognition.ts
    expo-keep-awake.ts
    @noble/
      ed25519.ts
  __tests__/
    protocol/
      connect.test.ts          — TEST-PROTO-001 through 005
      streaming.test.ts        — TEST-PROTO-006 through 008
      reconnect.test.ts        — TEST-PROTO-009 through 012
      send.test.ts             — TEST-PROTO-013
    security/
      auth.test.ts             — TEST-SEC-001 through 003
      credentials.test.ts      — TEST-SEC-004 through 008
      deeplinks.test.ts        — TEST-SEC-009
    state/
      chatStore.test.ts        — TEST-STATE-001
      agentStore.test.ts       — TEST-STATE-002
      connectionStore.test.ts  — TEST-STATE-003
      persistence.test.ts      — TEST-STATE-004, 005, 006
    components/
      ChatBubble.test.tsx      — TEST-COMP-001 through 004
      MarkdownRenderer.test.tsx — TEST-COMP-005, 006
      InputBar.test.tsx        — TEST-COMP-007, 008
      AugmentationPill.test.tsx — TEST-COMP-009
      AgentAvatar.test.tsx     — TEST-COMP-011
      MessageList.test.tsx     — TEST-COMP-012, 013
      ThemeProvider.test.tsx   — TEST-COMP-014
    voice/                     — from VOICE_BEHAVIOR_TESTS.md
    flows/
      onboarding.test.tsx      — TEST-FLOW-001, 002
      messaging.test.tsx       — TEST-FLOW-003, 004
      navigation.test.tsx      — TEST-FLOW-005
      provisioning.test.tsx    — TEST-FLOW-006
      augmentation.test.tsx    — TEST-FLOW-007
    gateway/
      compliance.test.ts       — TEST-GW-001 through 006
  maestro/                     — Phase 2 E2E flows
    flows/
      onboarding.yaml
      chat-send-receive.yaml
      agent-switch.yaml
      voice-record.yaml
```

---

## 8. Quality Gates

### Phase 1 Gate

| Criteria | Metric | Owner |
|---------|--------|-------|
| Unit test coverage | ≥60% statements, ≥50% branches | @frontend |
| Protocol compliance tests | 13/13 passing | @frontend |
| Security tests | 9/9 passing | @frontend + @security_audit |
| Voice tests | All automated tests passing | @qa_guy |
| Component tests | All P0 components covered | @frontend |
| State management tests | All stores covered | @frontend |
| Flow tests | Cold start + warm start + send/receive passing | @frontend |
| Zero credential leaks | TEST-SEC-003 passing; credential grep in CI | @security_audit |
| CI pipeline green | Tests pass on every push | @code_architect |
| Human review: voice UX | @qa_guy sign-off on device | @qa_guy |
| Human review: animation feel | Drawer, streaming cursor, transitions | @design_eng |

### Phase 2 Gate

All Phase 1 criteria plus:

| Criteria | Metric | Owner |
|---------|--------|-------|
| E2E tests (Maestro) | Core flows passing on simulator | @qa_guy |
| Routing engine tests | All evaluators + resolver covered | @frontend |
| Knowledge Skill tests | Search + graph + classification | @backend |
| Swarm tests | Group creation + multi-agent streaming | @frontend |
| LLM-graded SOUL compliance | 80% pass rate across all agents | @qa_guy |
| @security_audit sign-off | Push fix + skills security model | @security_audit |
| Coverage | ≥70% statements | @frontend |

### Phase 3 Gate

All Phase 2 criteria plus:

| Criteria | Metric | Owner |
|---------|--------|-------|
| Visual regression baselines | All 7 themes captured | @design_eng |
| Sensibility behavior tests | LLM-graded, 4/5 threshold | @qa_guy |
| Lockdown Mode tests | All security constraints verified | @security_audit |
| Coverage | ≥75% statements | @frontend |

---

## 9. Build Order for Test Infrastructure

| # | Task | Blocks | Effort |
|---|------|--------|--------|
| 1 | Install test dependencies (jest, jest-expo, RNTL) | Everything | 30 min |
| 2 | Create `jest.config.js` + verify it runs | Everything | 30 min |
| 3 | Write native module mocks (expo-secure-store, MMKV, haptics, @noble/ed25519) | All component/state tests | 2 hours |
| 4 | Write protocol mock server (WebSocket mock simulating gateway) | All protocol + flow tests | 4 hours |
| 5 | Write TEST-PROTO-001 (validates mock server + test pattern) | Pattern established | 1 hour |
| 6 | Write TEST-SEC-001 through 003 | Auth implementation confidence | 2 hours |
| 7 | Add test script + CI workflow | Ongoing regression | 1 hour |
| 8 | Write TEST-COMP-001 (ChatBubble — establishes component test pattern) | All component tests | 1 hour |

**Total Phase 1 test infrastructure: ~12 hours.** One-time investment.

---

## 10. Accepted Gaps

| Gap | Why Accepted | Revisit When |
|-----|-------------|-------------|
| Full gateway integration (real OpenClaw in CI) | Requires macOS + OpenClaw in CI — too complex for Phase 1 | Phase 3 |
| Performance (scroll perf with 1000+ messages) | No content to scroll yet | Phase 2 |
| Accessibility audit (full VoiceOver walkthrough) | Requires device + human tester | Phase 2 |
| Offline resilience | Offline behaviors not fully specced | Phase 2 |
| Multi-device conflict | Edge case, low priority | Phase 3 |
| Memory pressure / OOM | Requires real device under load | Phase 3 |

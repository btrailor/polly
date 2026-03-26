# Phase 1: Testing Infrastructure

**Status:** 📋 Planned  
**Gate:** Must ship alongside feature implementation (tests block Phase 1 QA gate)  
**Spec source:** `TESTING_AND_QA_SPEC.md`  
**Pre-ship gate:** @qa_guy sign-off on test coverage + CI green  
**Owners:** @qa_guy (strategy, acceptance criteria), @frontend (implementation), @code_architect (CI infra)

## Goal

Establish zero-to-working test infrastructure for the Polly iOS app. Currently: zero tests, zero test config, zero CI pipeline. This change sets up everything needed to run and maintain automated tests through Phase 1 and beyond.

## Tasks

### Infra Setup
- [ ] Install test dependencies: `jest@^29.7.0`, `jest-expo~52.0.0`, `@testing-library/react-native@^12.4.0`, `@testing-library/jest-native@^5.4.0`, `jest-fetch-mock@^3.0.0` — @frontend
- [ ] Create `jest.config.js` with `jest-expo` preset, `transformIgnorePatterns`, coverage thresholds (60% statements / 50% branches) — @frontend
- [ ] Add `test`, `test:watch`, `test:coverage`, `test:ci` scripts to `package.json` — @frontend
- [ ] Create `.github/workflows/test.yml` — runs `npm test --ci --coverage` on every push to `development` — @code_architect

### Native Module Mocks (required before first test)
- [ ] `__mocks__/expo-secure-store.ts` — in-memory `Map<string, string>`
- [ ] `__mocks__/expo-haptics.ts` — no-op functions
- [ ] `__mocks__/react-native-mmkv.ts` — in-memory Map with get/set/delete/clearAll
- [ ] `__mocks__/expo-speech-recognition.ts` — mock start/stop/results
- [ ] `__mocks__/expo-keep-awake.ts` — no-op
- [ ] `__mocks__/@noble/ed25519.ts` — deterministic test keypair (known fixed seed)

### Protocol Mock Server
- [ ] `__mocks__/gateway-mock-server.ts` — WebSocket mock simulating OpenClaw gateway: challenge-response, streaming delta/final, NO_REPLY, reconnect, error codes — @frontend

### Protocol Tests
- [ ] TEST-PROTO-001 — Connect with static auth token
- [ ] TEST-PROTO-002 — Connect with Ed25519 device auth
- [ ] TEST-PROTO-003 — Signature payload format character-by-character
- [ ] TEST-PROTO-004 — deviceToken rotation on every connect
- [ ] TEST-PROTO-005 — deviceToken mismatch → fallback to static token
- [ ] TEST-PROTO-006 — Streaming delta accumulation + final
- [ ] TEST-PROTO-007 — NO_REPLY suppression
- [ ] TEST-PROTO-008 — HEARTBEAT_OK suppression
- [ ] TEST-PROTO-009 — Reconnect on tick timeout + exponential backoff
- [ ] TEST-PROTO-010 — Reconnect preserves session + calls sessions.list
- [ ] TEST-PROTO-011 — connect.challenge mid-connection (server restart)
- [ ] TEST-PROTO-012 — seq gap detection
- [ ] TEST-PROTO-013 — Idempotency key on retry

### Security Tests
- [ ] TEST-SEC-001 — Ed25519 keypair generation on first launch; anti-assert private key never in logs
- [ ] TEST-SEC-002 — deviceId derivation matches reference SHA-256(publicKeyBytes)
- [ ] TEST-SEC-003 — Credentials never in log output (grep console capture) — **P0**
- [ ] TEST-SEC-004 — Sign-out clears all SECURE_STORE_KEYS
- [ ] TEST-SEC-005 — Secure store unavailable → blocks at passcode screen
- [ ] TEST-SEC-006 — TOFU fingerprint stored on first accept
- [ ] TEST-SEC-007 — TOFU cert mismatch blocks connection
- [ ] TEST-SEC-008 — Tunnel URL in Keychain, not MMKV
- [ ] TEST-SEC-009 — Deep link validation rejects unknown session keys

### State Tests
- [ ] TEST-STATE-001 through TEST-STATE-006 (chatStore, agentStore, connectionStore, MMKV persistence, Zustand session-only, draft preservation)

### Component Tests
- [ ] TEST-COMP-001 through TEST-COMP-009, TEST-COMP-011 through TEST-COMP-014 (all components except DrawerPanel human-review item)

### Flow Tests
- [ ] TEST-FLOW-001 through TEST-FLOW-007 (cold start, warm start, send/receive, retry, agent switch, team provisioning, augmented send)

### Gateway Compliance Tests
- [ ] TEST-GW-001 through TEST-GW-006 (wire format, connect params, chat.send params, group RPC, sessions.list on reconnect, config.patch format)

### Voice Tests
- [ ] Wire up `VOICE_BEHAVIOR_TESTS.md` test cases into Jest runner (TEST-V-001 through TEST-V-062)

## Done When
- All protocol compliance tests (13/13) passing
- All security tests (9/9) passing
- Voice automated tests passing
- P0 component tests passing
- Flow tests: cold start + warm start + send/receive passing
- Coverage ≥60% statements / ≥50% branches
- CI pipeline green on every push
- Zero credential leaks (TEST-SEC-003 passing)
- @qa_guy sign-off
- @security_audit: TEST-SEC-003 confirmed in CI

## Phase 3 Test Fixture Preparation
*Start during Phase 2 parallel — don't wait for Phase 3. Fixtures needed before Phase 3B begins. Decision locked 2026-03-25 per @qa_guy.*

### Schema-Driven Fixture Generator
- [ ] `test-fixture-corpus-design` — **BLOCKED on @backend:** requires JSONL schema spec for `knowledge_conversation_history` format; @backend to deliver when Phase 3A gateway work begins (gateway-changes #17); fixture generator must be schema-driven (not a static blob)
- [ ] Fixture generator: generates synthetic conversation history from schema; produces realistic `memory/YYYY-MM-DD.md` entries + JSONL corpus
- [ ] Seed data: 30-day synthetic conversation history with known mental model usage patterns and known outcomes (for Metacognitive Dashboard validation)
- [ ] @backend to confirm: does gateway already write conversation history anywhere, or is this net-new serialization? Answer determines how much of the format is speculative vs. verified

### EIS Smoke Plan
- [ ] `test-eis-smoke-plan` — not blocked on Phase 2 shipping; @qa_guy to start now
- [ ] Define what "passing" looks like for EIS without full corpus (Phase 3A readiness gate)
- [ ] Synthetic pattern injection test: manually inject known rhetorical pattern → confirm EIS fires flag
- [ ] False positive threshold: EIS must not flag > 10% of benign conversation turns in smoke corpus
- [ ] Outline the minimum fixture set needed before Phase 3A EIS work can begin

### Phase 3 Test Fixtures
- [ ] 30-day synthetic conversation history corpus (High effort — Metacognitive Dashboard, Temporal Intelligence, EIS) — BLOCKED on schema-driven generator
- [ ] Evolving position corpus: same topics discussed differently across simulated months — Temporal Intelligence drift detection
- [ ] Rhetorical pattern test set: ≥20 examples of common fallacies in conversation form — EIS pattern matching
- [ ] Structural pattern test vault: ≥50 notes with known structural parallels across domains — Structural Analogy
- [ ] Voice transcript corpus: ≥10 transcribed sessions — Oral History

### Creative Code Skill Containment
- [ ] Containment validation plan — @security_audit review is hard gate before sandbox is designed
- [ ] Separate from security review: containment validation pass ("what does failure look like and is it detectable?") — @qa_guy scope explicitly before Phase 3D begins

# PROJECT_STATUS.md

Living project status doc. @code_architect writes and maintains. All agents read-only.  
Last updated: 2026-04-01 (Phase 1A build session — active)  
Branch: `development`

---

## Current State

### Phase 1A — iOS Foundation (IN PROGRESS)

**Status:** 🔨 Active build. Critical path ~80% complete.

**What exists now:**
- ~2,200 lines TypeScript scaffold at kickoff; substantially expanded during Phase 1A
- Gateway fully wired: WebSocket client, connection store, auth handshake, reconnect with exponential backoff
- Onboarding flow: welcome → URL entry → token entry → test connection (manual form, not conversational)
- Chat screen: FlashList inverted, streaming send/receive, markdown rendering, thinking panels, disconnected banner
- Theme system: Reas tokens, ThemeContext, `useTheme()` hook (`src/theme/context`)
- TOFU cert pinning: application-layer on `auth.ok` (Phase 2: native TLS inspection)
- `sanitizeForLog()`: scrubs all 8 `SECURE_STORE_KEYS` fields + cfargotunnel URLs
- `SECURE_STORE_KEYS` typed constant: 8 keys, all reads/writes via `expo-secure-store`
- `config.get` capabilities fetch: fires post-`auth.ok`, MMKV-persisted
- `gatewayCapabilities.ts`: gateway version + capabilities store
- Test suite: 34 tests passing (2 suites: protocol + security)
- CI: `.github/workflows/test.yml` — Jest + coverage on every push to `development`
- EAS pipeline: `eas.json` committed, code signing configured (`caa654f`)
- `metro.config.js`: ensures `expo-openclaw-chat` TS source transpiles

**All 9 Phase 1A dependencies installed:**
`expo-secure-store`, `react-native-mmkv`, `zustand`, `@shopify/flash-list`,
`react-native-markdown-display`, `lucide-react-native`, `expo-keep-awake`,
`expo-audio`, `expo-document-picker`, `expo-haptics`, `expo-sqlite`

**Remaining Phase 1A tasks (5 tagged `[1A]` + unlabeled blockers):**
- [ ] Ed25519 keypair generation on first launch + challenge-response auth — @frontend
- [ ] DrawerPanel component + agent switcher — @frontend / @design_eng
- [ ] `NSFileProtectionComplete` MMKV/SQLite investigation — @frontend + @security_audit
- [ ] `IntegrationCard` + Settings → Integrations screen shell — @frontend
- [ ] Brave Search + ElevenLabs API key config UI — @frontend
- [ ] `PROJECT_STATUS.md` rewrite ← **this commit**
- [ ] Coverage gate: currently 3.6% — must reach ≥60% statements / ≥50% branches before Phase 1 QA sign-off — @qa_guy

**Known architectural decision pending:**
- Dual `GatewayClient` issue: `PollyGatewayAdapter` creates SDK-internal client per agent session; app-level `GatewayClient` singleton also connects. Potential WS conflict — @backend to resolve before integration testing.

**Security decisions locked (2026-04-01):**
- Keychain (`expo-secure-store`) for Phase 1 Ed25519 device key. Secure Enclave deferred to Phase 3.
- `NSFileProtectionCompleteUntilFirstUserAuthentication` for MMKV store (pending formal confirmation from @security_audit)
- TOFU: application-layer Phase 1, native TLS Phase 2 gap documented in `SECURITY_IMPLEMENTATION_SPEC.md`

---

### Agent System
**Status:** ✅ Spec complete.

- **43 agent templates:** all complete with full SOUL text + Prosodic Sensitivity
- **`suggested_prompts`:** ✅ 3–4 prompts per agent × 43 agents (committed 2026-04-01)
- **`autonomy_level` per-agent:** ✅ reference table in `POLLY_AGENT_TEMPLATES.md`
- **`allowed_modes` per-agent:** ✅ reference table in `POLLY_AGENT_TEMPLATES.md`

---

## Spec Status

| Spec | Status | Notes |
|------|--------|-------|
| `POLLY_IOS_SPEC.md` | ✅ Authoritative | Full iOS feature spec — canonical source |
| `POLLY_AGENT_TEMPLATES.md` | ✅ Authoritative | 43 agent templates complete |
| `ONBOARDING_SPEC.md` | ✅ Written | 11-phase OnboardingState machine |
| `MODEL_ROUTING_SPEC.md` | ✅ Written | Phase 3+ aspirational |
| `SWARM_COORDINATION_SPEC.md` | ✅ Written | All §8 gateway questions answered |
| `SENSIBILITY_SYSTEM_SPEC.md` | ✅ Written | Two-axis architecture; Reas default |
| `SECURITY_IMPLEMENTATION_SPEC.md` | ✅ Written | 50-item checklist; TOFU gap documented |
| `TESTING_AND_QA_SPEC.md` | ✅ Written | 55 test cases, LLM grading framework |
| `AGENT_BEHAVIOR_CONTRACT.md` | ✅ Written | Tool surface by phase, autonomy levels |
| `PHASE_2_GAP_ANALYSIS.md` | ✅ Written | 10 missing changes identified |
| `PHASE_3_GAP_ANALYSIS.md` | ✅ Written | 3A/3B/3C/3D split |

---

## Phase Gates

| Gate | Status |
|------|--------|
| Phase 1A → TestFlight | ⏳ Ed25519 auth + DrawerPanel + coverage gate remaining |
| Phase 2 push features | 🔒 Requires @security_audit sign-off on C1 + C2 (gateway-side) |
| Phase 3 Secure Enclave | 🔒 Native module required (`PollyCrypto`) |

---

## Commit Reference (Phase 1A)

| Commit | What |
|--------|------|
| `1944c4d` | 9 npm packages installed |
| `61a4c02` | CI: `test.yml` workflow |
| `69450c5` | Infra: `metro.config.js` |
| `68beb08` | Backend: WebSocket, SECURE_STORE_KEYS, sanitizeForLog |
| `aaadd0e` | Onboarding scaffold |
| `24265b6` | QA: Jest config + mocks |
| `d0eaba4` | Design: Reas theme tokens + ThemeContext |
| `9d60a58` | Backend: TOFU + manifest schema |
| `b4b9034` | Backend: config.get capabilities fetch |
| `2444373` | QA: gateway mock + 21 protocol/security tests |
| `c402bb7` | Chat: FlashList + PollyGatewayAdapter + streaming |
| `1899825` | Infra: expo-haptics + expo-sqlite + setup.sh |
| `e03c283` | QA: TOFU tests TEST-SEC-006/007 (34 total) |
| `6be0eb4` | Security: sanitizeForLog cfargotunnel fix |

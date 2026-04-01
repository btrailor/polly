# SECURITY_IMPLEMENTATION_SPEC.md

Phase 1–4 — Security Surfaces, Gaps, and Implementation Order  
Status: Draft  
Owners: @security_audit (threat model, review gates), @code_architect (architecture), @backend (gateway enforcement), @frontend (iOS implementation)  
Last updated: 2026-03-25  
Cross-references: `POLLY_IOS_SPEC.md` §8, §7.10; `PUSH_SECURITY_FIX.md`; `LOCKDOWN_MODE.md`; `SKILLS_MARKETPLACE.md` §2, §6; `MCP_ADAPTER.md` §5, §7, §8, §9; `openspec/specs/infrastructure/spec.md`; `ONBOARDING_SPEC.md`; `MODEL_ROUTING_SPEC.md`

---

## 1. What This Document Does

Security is distributed across 5 spec documents, 7 sections of the iOS spec, and 2 openspec files. Nobody has a single view of all security decisions, their implementation status, their dependencies, and their Phase 1 implications.

This document:
- Consolidates every security surface into one map
- Identifies what's specced vs. what's implemented vs. what's missing
- Traces Lockdown Mode's Phase 1 architectural requirements (the spec says they're "not retrofittable" but they're invisible in the Phase 1 task list)
- Resolves the §7.10 vs. §8.3 transport security contradiction
- Produces a prioritized security implementation checklist across all phases

---

## 2. Security Surface Map

### 2.1 Authentication Surfaces

| Surface | Spec | Phase | Status |
|---------|------|-------|--------|
| Ed25519 keypair generation | §8.1 | 1 | ❌ Not implemented. expo-secure-store not installed. No crypto code exists. |
| Device identity derivation (SHA-256 of public key) | §8.1 | 1 | ❌ Not implemented. |
| Challenge-response signing | §3.3.1 | 1 | ❌ Not implemented. |
| deviceToken caching + rotation | §8.1 | 1 | ❌ Not implemented. A TODO comment in index.tsx references expo-secure-store. |
| Static auth token path | §3.3.2 | 1 | ❌ Not implemented. |
| TOFU cert pinning | §8.3 | 1 | ✅ Implemented (`9d60a58`). Application-layer only (Phase 1A): gateway sends fingerprint in `auth.ok` payload; `GatewayClient._storeTofuFingerprintIfNeeded()` stores on first connect, verifies on subsequent. **Phase 2 gap:** full TLS inspection (independently computing fingerprint from TLS handshake) requires a native module — deferred. |
| Biometric lock (Face ID/Touch ID) | §8.7, §4.8 | 2 | ❌ Not implemented. expo-local-authentication not installed. |
| Session timeout + re-auth | §8.7, §4.8 | 2 | ❌ Not implemented. |
| Device registration cap (10 max) | §8.6 M2 | 2 | ❌ Not implemented. |
| Push registration auth gating (C1) | PUSH_SECURITY_FIX.md | Pre-production | ❌ Not implemented — gateway-side fix. |

### 2.2 Data at Rest Surfaces

| Surface | Storage | Encryption | Phase | Status |
|---------|---------|-----------|-------|--------|
| Ed25519 private key | expo-secure-store | iOS Keychain (hardware-backed) | 1 | ❌ Not stored. |
| deviceToken | expo-secure-store | iOS Keychain | 1 | ❌ Not stored. |
| Gateway auth token | expo-secure-store | iOS Keychain | 1 | ❌ Not stored. |
| Cloudflare Tunnel URL | expo-secure-store | iOS Keychain | 1 | ❌ Not stored. |
| sendKey (push) | expo-secure-store | iOS Keychain | 2 | ❌ Not stored. |
| APNs push token | expo-secure-store | iOS Keychain | 2 | ❌ Not stored. |
| TLS fingerprint (TOFU) | expo-secure-store | iOS Keychain | 1 | ❌ Not stored. |
| Tailscale address | MMKV | Standard iOS encryption | 1 | ❌ Not stored. |
| User preferences | MMKV | Standard iOS encryption | 1 | ❌ Not stored. |
| Local message cache | expo-sqlite | Standard iOS encryption | 1 | ❌ Not built. |
| Vault bookmark | expo-secure-store | iOS Keychain | 1 | ❌ Not stored. |
| sendKey on gateway | devices.json | **Cleartext — VULNERABLE** | Pre-prod | ❌ Gateway-side fix needed. |
| Agent session files (gateway) | Filesystem | Unencrypted (standard) / Encrypted (lockdown) | 3 | Lockdown-specific. |
| EIS pattern library (gateway) | Filesystem | Separate key (always encrypted) | 3 | Phase 3. |

### 2.3 Transport Surfaces

| Surface | Protocol | Spec | Phase | Status |
|---------|---------|------|-------|--------|
| LAN WebSocket | ws:// permitted (§7.10 decision — see §9 for contradiction resolution) | §8.3 | 1 | ❌ No WebSocket client. |
| Cloudflare Tunnel | wss:// required always | §8.3 | 1 | ❌ No WebSocket client. |
| Tailscale | ws:// permitted (WireGuard-encrypted) | §8.3 | 1 | ❌ No WebSocket client. |
| Push relay (gateway→Apple) | HTTPS | §8.2 | 2 | Gateway-side. |
| MCP subprocess IPC | stdio only | MCP_ADAPTER.md §5.4 | 2 | Phase 2 skill runner. |
| Skill network access | Manifest-declared domains only | §8.8.3 | 2 | Phase 2 skill runner. |

### 2.4 Trust Decision Surfaces

| Surface | Decision | Spec | Phase |
|---------|---------|------|-------|
| Skill trust tiers (Verified/Community/Blocked) | Install-time consent | §8.8.2, SKILLS_MARKETPLACE.md §2 | 2 |
| Skill permissions manifest | Install-time review + approval | §8.8.2 | 2 |
| Permission-expanding skill updates | Re-consent flow | §8.8.5 | 2 |
| Blocklist enforcement | Gateway-level, signed, fail-closed | SKILLS_MARKETPLACE.md §2.2 | 2 |
| MCP tool description linting | Install-time + session-open re-check | MCP_ADAPTER.md §8 | 2 |
| MCP response sanitization | Every response, before context injection | MCP_ADAPTER.md §7 | 2 |
| Vault write-back permission | Opt-in toggle, off by default | §15.3.1 | 3 |
| Lockdown Mode activation | User-initiated, multi-tap | LOCKDOWN_MODE.md §4 | 2+ |

---

## 3. The Lockdown Mode Problem

`LOCKDOWN_MODE.md` explicitly states: "Architectural decisions inform Phase 1/2 — not retrofittable."

But Lockdown Mode has zero representation in the Phase 1 task list as architectural hooks. Here are the specific Phase 1 decisions that Lockdown Mode requires:

### 3.1 File Protection Class

Every file Polly writes must use `NSFileProtectionComplete`. This is NOT the default on iOS. It must be specified per-file or per-directory.

**Phase 1 implication:** When the local message cache (expo-sqlite), MMKV stores, or any other file is created, the file protection class must be set. If Phase 1 creates files with the default protection class and Phase 2+ tries to upgrade them, the upgrade requires deleting and recreating every file.

```typescript
// Every file write path must include:
// expo-sqlite: set protection on the database file after creation
// MMKV: investigate if MMKV supports NSFileProtectionComplete natively
// Temp files: set protection before writing content

// expo-file-system approach:
await FileSystem.makeDirectoryAsync(dataDir, { intermediates: true });
await FileSystem.setFileProtection(dataDir, FileSystem.FileProtection.COMPLETE);
```

Investigation required: confirm MMKV natively supports `NSFileProtectionComplete`. If not, wrapper or alternative.

### 3.2 Voice Audio Buffer Policy

Lockdown Mode requires voice audio to never be written to disk. The voice recording architecture must be memory-only from Phase 1 — never "write audio to temp file, then read it."

**Phase 1 implication:** When implementing real audio recording (replacing the `useVoiceRecording.ts` scaffold), the audio buffer must stay in memory. Verify that `expo-av` or `expo-audio` supports in-memory buffers. If the library writes a temp file by default, this needs a wrapper or alternative.

### 3.3 Session Persistence Flag

Lockdown Mode makes session memory non-persistent by default. Sessions don't write to disk until explicitly saved.

**Phase 1 implication:** The message cache schema needs a `persistent: boolean` flag per session. Phase 1 sets it to `true` for all sessions. Lockdown Mode sets it to `false`. When `persistent: false`, messages exist only in Zustand state, not in SQLite.

```typescript
interface SessionRecord {
  sessionKey: string;
  agentId: string;
  label?: string;
  persistent: boolean;  // false = Lockdown Mode ephemeral; true = normal
  createdAt: number;
  lastActiveAt: number;
}
```

### 3.4 Gateway Protection Level Config Key

The gateway needs `polly.security.protectionLevel: "standard" | "enhanced"` from Phase 1, even though only `"standard"` is used until Lockdown Mode ships.

**Phase 1 implication:** Add this key to the initial `config.patch` at connection setup. Prevents migration later.

### 3.5 Phase 1 Lockdown Hooks Summary

| Hook | Phase 1 Action | Effort |
|------|---------------|--------|
| NSFileProtectionComplete on all file writes | Investigate MMKV + expo-sqlite support. Set on all data directories at app init. | Low — one-time config + investigation |
| Memory-only voice buffers | Require in-memory audio in voice recording implementation. No temp files. | Low — design constraint |
| Session persistence flag | Add `persistent: boolean` to session schema. Default `true`. | Low — one field |
| Gateway protection level key | Include `polly.security.protectionLevel: "standard"` in initial config. | Trivial |
| Audit log chain structure | If any logging implemented in Phase 1, use chained hashes. | Low if now, painful to retrofit |

---

## 4. Credential Lifecycle Matrix

| Credential | Created When | Rotated When | Invalidated When | Cleanup |
|-----------|-------------|-------------|-----------------|---------|
| Ed25519 private key | First launch (silent, before onboarding) | Never (permanent per-device) | Device wipe, app reinstall | expo-secure-store handles |
| deviceId | Derived from public key at creation | Never | Follows private key | MMKV + expo-secure-store |
| deviceToken | Each successful WS connect (gateway issues fresh) | Every connect (rotation by design) | 7-day TTL (Phase 2+); manual revoke | expo-secure-store overwrite on rotation |
| Gateway auth token | User enters during onboarding | Never (static, user-managed) | User changes token on gateway | expo-secure-store; cleared on sign-out |
| Cloudflare Tunnel URL | User enters during setup | Never (user-managed) | User changes tunnel config | expo-secure-store; cleared on sign-out |
| TLS fingerprint | TOFU on first verified connection | On cert change (with user confirmation) | User taps "Re-verify" in Settings → Security | expo-secure-store overwrite |
| sendKey (push) | Push registration response | Per re-registration | Device unregister, push disabled | expo-secure-store; explicit delete on unregister |
| Vault security-scoped bookmark | User picks vault directory | If user changes vault in Settings | Revoked by iOS (app reinstall, permission change) | expo-secure-store |

### 4.1 Sign-Out Key Inventory

§8.7 says "Call SecureStore.deleteItemAsync for all keys" but doesn't enumerate them. Complete list:

```typescript
const SECURE_STORE_KEYS = [
  'polly.device.privateKey',
  'polly.device.token',
  'polly.gateway.token',
  'polly.gateway.tlsFingerprint',
  'polly.gateway.tunnelUrl',
  'polly.push.sendKey',
  'polly.push.apnsToken',
  'polly.vaultBookmark',
] as const;

async function signOut() {
  await gateway.rpc('aight.push.unregister', { deviceId });
  for (const key of SECURE_STORE_KEYS) {
    await SecureStore.deleteItemAsync(key);
  }
  mmkv.clearAll();
  await db.execute('DELETE FROM messages');
  await db.execute('DELETE FROM sessions');
  router.replace('/onboarding');
}
```

### 4.2 Sign-Out vs. Reset

- **Sign-out:** Clears credentials + cache, preserves app preferences (theme, etc.). Navigates to onboarding.
- **Reset (§4.8):** Nuclear — clears everything including preferences. Same as fresh install.

Currently only Reset is specced (via Settings → About). Sign-out as a distinct action should exist in Settings → Your Gateway. Add to Phase 1 tasks.

---

## 5. OTA Supply Chain Risk

### 5.1 What OTA Can Change

Metro bundler OTA updates can change any JavaScript code — including chat message handling, auth token handling, `PollyGatewayAdapter.send()`, and any Zustand store logic. OTA **cannot** change native modules, iOS permissions, or app entitlements.

### 5.2 Mitigations

| Mitigation | Implementation | Phase |
|-----------|---------------|-------|
| EAS code signing | Enable in `eas.json` with code signing | 1 |
| Version-pin expo-openclaw-chat | `@0.2.3` exact in package.json, no caret | 1 |
| OTA rollback procedure | Document in ops guide: EAS dashboard → channel → rollback | 1 |
| Auth code out of OTA-updatable path | Keep expo-secure-store calls in native module wrapper | 2 |
| OTA update notification | Show "App updated" banner on next launch after OTA | 2 |
| User-controlled OTA toggle | Settings: "Automatic updates" on/off | 2 |

---

## 6. Gaps Not Addressed in Any Spec

### 6.1 Log Hygiene

No spec addresses what gets logged. Define a `sanitizeForLog()` function that strips sensitive fields before any `console.log`, Sentry report, or crash dump.

```typescript
const SENSITIVE_FIELDS = ['token', 'key', 'privateKey', 'sendKey', 'password', 'secret'];
function sanitizeForLog(obj: unknown): unknown {
  if (typeof obj !== 'object' || obj === null) return obj;
  return Object.fromEntries(Object.entries(obj as Record<string, unknown>).map(
    ([k, v]) => [k, SENSITIVE_FIELDS.some(f => k.toLowerCase().includes(f)) ? '[REDACTED]' : sanitizeForLog(v)]
  ));
}
```

### 6.2 Clipboard Security

When user copies a message, content is accessible to any app. Lockdown Mode mitigation: clipboard auto-clear after 60 seconds (`UIPasteboard.general.setItems([], expirationDate:)`), or confirmation prompt before copy.

### 6.3 Screen Recording Detection

Use `UIScreen.main.isCaptured` to detect screen recording → show a warning banner in Lockdown Mode. Don't prevent screenshots for normal use — too disruptive. Document in Lockdown Mode operational security guidance.

### 6.4 Deep Link Injection

`polly://` URL scheme handles deep links. Mitigation: validate all parameters before acting — session keys must match known sessions; onboarding deep link ignored if already connected; no credential changes without user confirmation.

### 6.5 Memory Residue

On app background in Lockdown Mode: clear all Zustand stores, force garbage collection. On resume: reload from cache (persistent) or start fresh (ephemeral). This is the "background session encryption" item from §8.6 item 9.

### 6.6 API Key Passthrough Security

API keys entered in Settings are forwarded to gateway via `config.patch`. Risks: key in WebSocket frame (cleartext on LAN), key in JS memory (crash dump exposure), key in gateway logs.

Mitigations:
- Force WSS even on LAN for API key config changes (sensitive credential in transit)
- `try/finally` pattern that explicitly clears the key variable
- Gateway scrubs API keys from config change logs (@backend-side)

---

## 7. §7.10 vs. §8.3 Transport Contradiction — Resolved

`§7.10` says: `ws://` is acceptable for LAN and Tailscale.  
`§8.3` has a note: "§8.3 supersedes this. Polly enforces WSS-only as an app-side policy."

These directly contradict each other. **Resolution (locked 2026-03-25):**

**Option 3: User choice with sensible default.**
- Default: `ws://` on LAN (frictionless setup — self-signed cert management is a real barrier for self-hosted users)
- Cloudflare Tunnel: `wss://` always (no exception)
- Tailscale: `ws://` permitted (WireGuard provides transport encryption)
- Lockdown Mode: forces `wss://` everywhere
- Settings → Security: "Require encrypted connections" toggle — default off; power users enable

This means `NSAllowsLocalNetworking: true` in Info.plist is correct and intentional (for LAN `ws://`).  
The §8.3 note claiming "WSS-only app policy" is **wrong** — remove it from §8.3 in the next spec update.

---

## 8. Security Implementation Checklist

### 🔴 Phase 1 — Must Ship

| # | Task | Spec | Owner |
|---|------|------|-------|
| 1 | Install `expo-secure-store`, `@noble/ed25519`, `@noble/hashes` | §8.1, §12 | @frontend |
| 2 | Ed25519 keypair generation on first launch | §8.1 | @frontend |
| 3 | deviceId derivation (SHA-256 of public key) | §8.1 | @frontend |
| 4 | Challenge-response signing for WS auth | §3.3.1 | @frontend |
| 5 | deviceToken storage + rotation via expo-secure-store | §8.1 | @frontend |
| 6 | Static auth token storage in expo-secure-store | §3.3.2 | @frontend |
| 7 | `NSAllowsLocalNetworking: true` in Info.plist | §3.14 | @frontend |
| 8 | WSS enforcement for Cloudflare Tunnel connections | §8.3 | @frontend |
| 9 | TOFU cert pinning (store fingerprint on first connect) | §8.3 | @frontend |
| 10 | Investigate `NSFileProtectionComplete` for MMKV + expo-sqlite | LOCKDOWN_MODE.md §3.1 | @frontend |
| 11 | Set file protection class on all data directories at app init | LOCKDOWN_MODE.md §3.1 | @frontend |
| 12 | Memory-only voice audio buffer (no temp files) | LOCKDOWN_MODE.md §3.2 | @frontend |
| 13 | `persistent: boolean` flag on session/message cache schema | LOCKDOWN_MODE.md §3.3 | @frontend |
| 14 | `polly.security.protectionLevel: "standard"` in initial config | LOCKDOWN_MODE.md §3.4 | @backend |
| 15 | EAS code signing enabled | §8.6 item 6 | @frontend |
| 16 | Version-pin `expo-openclaw-chat@0.2.3` | §8.6 item 6 | @frontend |
| 17 | `sanitizeForLog()` — strip credentials from all log output | §6.1 above | @frontend |
| 18 | Sign-out function with complete key inventory + cleanup | §8.7 | @frontend |
| 19 | Deep link parameter validation | §6.4 above | @frontend |
| 20 | `SECURE_STORE_KEYS` constant (enumerated, typed) | §4.1 above | @frontend |
| 21 | Sign-out action in Settings → Your Gateway (not just Reset) | §4.2 above | @frontend |

### 🟠 Pre-Production Gate

| # | Task | Spec | Owner |
|---|------|------|-------|
| 22 | C1: Auth-gate push registration on gateway | PUSH_SECURITY_FIX.md | @backend |
| 23 | C2: Encrypt sendKey at rest (macOS Keychain, not devices.json) | PUSH_SECURITY_FIX.md | @backend |
| 24 | @security_audit sign-off on C1 + C2 | PUSH_SECURITY_FIX.md | @security_audit |

### 🟡 Phase 2

| # | Task | Spec | Owner |
|---|------|------|-------|
| 25 | Biometric lock (expo-local-authentication) | §8.7 | @frontend |
| 26 | Session timeout + re-auth | §8.7 | @frontend |
| 27 | Device registration cap (10 max) + management UI | §8.6 M2, §4.8 | @frontend + @backend |
| 28 | deviceToken 30-day TTL on gateway | §8.6 M3 | @backend |
| 29 | Skills permission manifest UI | §8.8.2 | @frontend |
| 30 | Skill sandbox enforcement (gateway) | §8.8.3 | @backend |
| 31 | MCP response sanitization | MCP_ADAPTER.md §7 | @backend |
| 32 | MCP tool description linting | MCP_ADAPTER.md §8 | @backend |
| 33 | Blocklist enforcement (signed, fail-closed) | SKILLS_MARKETPLACE.md §2.2 | @backend |
| 34 | OTA update notification | §5.2 above | @frontend |
| 35 | User-controlled OTA toggle | §5.2 above | @frontend |
| 36 | Lockdown Mode UI (Settings → Privacy → Advanced → Protection Level) | LOCKDOWN_MODE.md §3, §4 | @frontend |
| 37 | Lockdown Mode gateway enforcement (network blocks, APNs block, skill restrictions) | LOCKDOWN_MODE.md §6, §7 | @backend |
| 38 | Lockdown Mode session non-persistence | LOCKDOWN_MODE.md §8.1 | @frontend + @backend |
| 39 | Clipboard auto-clear in Lockdown Mode | §6.2 above | @frontend |
| 40 | Gateway scrubs API keys from config change logs | §6.6 above | @backend |
| 41 | Settings → Security: "Require encrypted connections" toggle (§7.10 resolution) | §7 above | @frontend |

### 🔵 Phase 3+

| # | Task | Spec | Owner |
|---|------|------|-------|
| 42 | Gateway encryption at rest (passphrase-derived key, Secure Enclave) | LOCKDOWN_MODE.md §5.2 | @backend |
| 43 | EIS pattern library separate key | LOCKDOWN_MODE.md §5.3 | @backend |
| 44 | Duress PIN implementation | LOCKDOWN_MODE.md §9 | @backend + @frontend |
| 45 | Tamper-evident audit log (chained hashes) | LOCKDOWN_MODE.md §10 | @backend |
| 46 | Zeroing protocol (overwrite on delete) | LOCKDOWN_MODE.md §8.3 | @backend |
| 47 | Screen recording detection + Lockdown Mode warning | §6.3 above | @frontend |
| 48 | Background session state clearing (Lockdown Mode) | §8.6 item 9 | @frontend |
| 49 | Relay cert pinning | §8.6 item 7 | @backend |
| 50 | Secure Enclave upgrade path (native module) | §8.6 item 10 | @frontend |

---

## 9. Security Review Gate Pattern

Every security-gated feature must complete this pattern before shipping:

1. Implementation complete
2. @security_audit reviews against spec
3. Specific acceptance criteria checked (per-feature lists in respective change tasks.md)
4. Sign-off recorded in change's tasks.md
5. Feature ships

**Features requiring @security_audit sign-off:**

| Phase | Feature | Gate |
|-------|---------|------|
| Pre-prod | Push security fix (C1 + C2) | @security_audit sign-off on both fixes |
| 2 | Skills Marketplace | §8.8 threat model (6 attack surfaces) signed off |
| 2 | MCP Adapter | Security architecture signed off |
| 2 | Lockdown Mode | Full threat model + implementation review |
| 3 | Vault write-back | Permission model + write isolation review |
| 3 | Knowledge Skill conversation history adapter | Access control review |

# LOCKDOWN_MODE.md
*Phase 2 — High-Stakes Privacy Mode*
*Status: Planned*
*Owners: @security_audit (threat model, encryption spec, duress path), @code_architect (mode architecture), @backend (gateway enforcement), @frontend (invisible UI constraint)*
*Last updated: 2026-03-25*
*Co-authored with @security_audit*

---

## 1. Who This Is For

Journalist with sensitive sources. Domestic abuse survivor. Political organizer in a hostile jurisdiction. IRB-bound researcher with confidential participant data.

The common thread: **the device or gateway may be seized, and the data on it may be used as evidence or to identify others.**

This is not a paranoid edge case. It is the primary design requirement for this document. Every decision in this spec is anchored to it.

---

## 2. Threat Model

### 2.1 Threat Actors

| Actor | Attack Surface |
|-------|---------------|
| Law enforcement with legal process | Subpoena, warrant, border search — physical device access + third-party data requests |
| Hostile personal actor | Abusive partner or adversary with physical access to unlocked device |
| Network-level adversary | Traffic metadata monitoring on same network (coffee shop, border checkpoint, shared infrastructure) |
| Compromised third-party infrastructure | Any relay, tunnel, or push service that transits data from gateway to device |

### 2.2 Threat/Mitigation Table

| Threat | Mitigation |
|--------|------------|
| Seized device → readable data | iOS Complete Protection class on all files; gateway data encrypted with Secure Enclave-derived key |
| Seized device → behavioral metadata | Prosodic extraction disabled and non-toggleable; voice audio never written to disk |
| Network monitoring → usage patterns | APNs (push) disabled; polling only; no Cloudflare tunnel; no relay; Tailscale or LAN only |
| Third-party subpoena | Nothing on Apple/Cloudflare/any relay to subpoena — zero data at third parties |
| Forced unlock under duress | Duress PIN triggers immediate key wipe; data permanently unrecoverable |
| Malicious skill exfiltrating data | Community skills disabled; Verified + local only; `network: [read]` non-grantable for any skill |
| Ambient metadata accumulation | Session memory non-persistent by default; zero extraction posture |

---

## 3. Stealth Design (Invisible Mode)

**Lockdown Mode is invisible by default.** There is no "LOCKDOWN MODE" banner, no lock icon in the status bar, no visual indicator that constraints are in force.

**Rationale:** A visible lockdown indicator is itself metadata. "This person activated lockdown mode before crossing the border" is information an adversary can use. The constraints must be identical whether the user is in front of an adversary or alone. If the mode looks different, the mode is detectable.

**Status access:** Settings → Privacy → Advanced → Protection Level. Three taps minimum. Displays current protection level without using the words "lockdown" or "restricted." Label: "Enhanced Protection: On."

**Power users:** The buried settings screen shows exactly which constraints are in force. No mystery — full transparency for the user. Invisible to external observation only.

---

## 4. Activation Model

### 4.1 Entering Lockdown Mode

Activation path: Settings → Privacy → Advanced → Protection Level → Enhanced

**On activation, in order:**
1. All in-flight network connections terminated
2. Session memory cleared (existing sessions zeroed)
3. Skill network permissions revoked (all `network: [read]` grants suspended)
4. APNs token deregistered (gateway switches to polling connection)
5. Prosodic extraction disabled (gateway-enforced, not client-side toggle)
6. Confirmation: "Enhanced Protection enabled. Existing session data cleared."

**What is NOT cleared on activation:**
- The Knowledge Skill index (vault content) — not cleared, but encrypted at rest under the same key hierarchy
- Agent SOULs and configuration — not cleared
- The activation itself is not logged to any external service

### 4.2 Exiting Lockdown Mode

**Exiting requires the same passcode used to enter** (or device biometric + confirmation prompt). There is no one-tap disable.

On exit:
- Constraints lifted
- APNs re-registration offered (not automatic — user choice)
- Skill permissions remain revoked until user re-grants individually
- Session data does not restore (what was cleared stays cleared)

### 4.3 Persistence

Lockdown Mode persists across app restarts, device reboots, and app updates. It does not disable automatically after a time period. The user must explicitly exit.

---

## 5. Encryption at Rest

### 5.1 iOS Layer

All Polly data files must use **iOS Data Protection Complete Protection** (`NSFileProtectionComplete`):
- Files inaccessible when device is locked
- Key derived from device passcode + hardware UID
- If device is seized while locked, files are unreadable

This applies to: session files, memory files, Knowledge Skill index, Epistemic Immune System pattern library, Metacognitive Dashboard data, oral history corpus.

**@backend + @frontend:** All file writes must specify `NSFileProtectionComplete`. This is not the default on iOS — it must be set explicitly per file or per directory. Audit required.

### 5.2 Gateway Layer

The gateway stores data on the user's own hardware. In Lockdown Mode:

- Session files encrypted with a key derived from a user-set gateway passphrase
- Epistemic Immune System pattern library encrypted separately (see §5.3)
- Key stored in macOS Secure Enclave (T2 chip / Apple Silicon) — not in the filesystem
- Gateway passphrase required on every gateway restart when Lockdown Mode is active

**Key hierarchy:**
```
Device passcode → iOS Complete Protection key (iOS-managed)
Gateway passphrase → gateway root key (Secure Enclave)
  ├── session_key (per-session, derived)
  ├── pattern_library_key (Epistemic Immune System)
  └── dashboard_key (Metacognitive Dashboard)
```

### 5.3 Sensitive Data Layers (Double-Encrypted)

Two layers of the cognitive artifact contain uniquely sensitive data and receive separate encryption:

| Layer | Why separate key |
|-------|-----------------|
| Epistemic Immune System pattern library | Map of rhetorical vulnerabilities — usable for manipulation |
| Metacognitive Dashboard | Detailed model of reasoning patterns |

Both layers are encrypted under their own keys even when Lockdown Mode is off. In Lockdown Mode, keys additionally require gateway passphrase to unlock.

---

## 6. Network Constraint Enforcement

These are **hard blocks at the gateway level**, not UI toggles:

| Connection type | Normal mode | Lockdown Mode |
|----------------|-------------|---------------|
| Direct LAN (iOS → gateway, same network) | ✅ Allowed | ✅ Allowed |
| Tailscale (end-to-end encrypted WireGuard) | ✅ Allowed | ✅ Allowed |
| APNs / push notifications | ✅ Allowed | ❌ Hard-blocked |
| Cloudflare Tunnel | ✅ Allowed | ❌ Hard-blocked |
| Any other relay / proxy | User-configurable | ❌ Hard-blocked |
| Skill `network: [read]` | Grantable | ❌ Non-grantable |

**Enforcement point:** The gateway refuses to register APNs tokens or establish relay connections when Lockdown Mode is active. The iOS client cannot override this — the constraint is gateway-side.

**Why APNs is blocked:** Push notifications require an Apple server to hold a device token and route messages. Apple is a subpoenable third party. In Lockdown Mode, the gateway polls on a configurable interval instead.

---

## 7. Skill Restrictions

In Lockdown Mode:

- **Community skills:** Disabled. Cannot be installed or activated.
- **Verified skills:** Available but re-audited at next startup (checksums verified).
- **Local skills:** Available without restriction.
- **`network: [read]`:** Non-grantable for any skill, regardless of trust tier or prior grants.
- **`data_destination: cloud`:** All skills with this manifest field are disabled.

**Enforcement:** The skill runner checks Lockdown Mode status before executing any skill invocation. This is a gateway-level gate — a client-side skill bypass cannot circumvent it.

---

## 8. Memory and Session Handling

### 8.1 Non-Persistent Default

In Lockdown Mode, session memory is non-persistent by default:
- Sessions do not write to disk until explicitly saved by the user
- "Save this session" is a deliberate user action, not automatic
- Unsaved sessions are zeroed on session end (overwrite, not just delete)

### 8.2 Voice and Prosodics

- Voice audio: never written to disk in any mode. In Lockdown Mode, this is enforced at the gateway transcription endpoint — no audio buffer retention.
- Prosodic extraction: disabled and non-toggleable. The gateway ignores prosodic metadata fields even if the client sends them.

### 8.3 Zeroing Protocol

"Deleted" data in Lockdown Mode is not just unlinked — it is overwritten. Single-pass zero overwrite on:
- Session files on session end (if not explicitly saved)
- Temporary files (transcription buffers, intermediate outputs)
- Log files older than the configurable retention window

---

## 9. Duress Path

**A duress PIN is a separate numeric code that, when entered instead of the device passcode, triggers immediate key wipe.**

On duress PIN entry:
1. Gateway root key deleted from Secure Enclave immediately
2. All derived session, pattern library, and dashboard keys become unrecoverable
3. iOS requests data protection key deletion (best-effort — iOS controls the actual operation)
4. App exits
5. No confirmation prompt. No "are you sure." Immediate and irreversible.

**What survives key wipe:**
- Encrypted ciphertext files (now permanently unreadable without the key)
- App binary (no user data)
- Nothing else

**What does not survive:**
- All session data
- Knowledge Skill index (accessible ciphertext remains but key is gone)
- Epistemic Immune System pattern library
- Metacognitive Dashboard data

**Duress PIN setup:** Settings → Privacy → Advanced → Duress Code. Requires current passcode to set. Duress code must differ from primary passcode by at least 2 digits.

**@security_audit:** Duress PIN iOS implementation requires evaluation — iOS doesn't expose a direct "delete Secure Enclave key on PIN entry" API. Implementation path TBD; may require gateway-side key management rather than iOS keychain. Flag for implementation review.

---

## 10. Audit Log Integrity and Retention

### 10.1 Tamper-Evident Log

The gateway maintains a tamper-evident audit log of: skill invocations, network connections made, file writes, mode changes (Lockdown Mode enter/exit).

Log entries are chained (each entry includes hash of previous entry). Tampering is detectable.

### 10.2 The Audit Log as Evidence Problem

The audit log itself may be subpoenable and may contain incriminating metadata. Two options:

**Option A — Short retention with configurable window:** Default 7-day retention; auto-deleted after window. User can set 1-day minimum. Audit log is always present but short.

**Option B — Lockdown Mode zeroes audit log on activation:** When entering Lockdown Mode, the audit log prior to activation is wiped. Only post-activation activity is logged.

**Decision: Option B for Lockdown Mode + Option A for normal mode.** On Lockdown Mode activation, historical audit log is wiped. Post-activation audit log uses 7-day default with user-configurable window. The user chose enhanced protection — that choice should extend to prior activity.

---

## 11. Operational Security Guidance

Architecture cannot enforce everything. The user must understand:

1. **Strong passcode required.** 6-digit PIN is not enough. 12+ character alphanumeric passcode + biometric enabled.
2. **Auto-wipe after 10 failed attempts.** Enable in iOS Settings → Face ID & Passcode → Erase Data.
3. **Gateway machine physical security.** If the gateway Mac is unlocked and unattended, no software protection is adequate. Screen lock timeout: 1 minute maximum when Lockdown Mode is active on clients.
4. **Tailscale exit node risks.** If using Tailscale with an exit node, exit node traffic may be logged by the exit node operator. LAN-only or direct Tailscale (no exit node) is the correct configuration in Lockdown Mode.
5. **Duress PIN is permanent.** Test with a fresh gateway instance before relying on it. There is no recovery.
6. **Metadata is also evidence.** Even with all data encrypted, the *fact of communication* (timestamps, duration) may be visible on the network. This requires operational security beyond what Polly can provide.

---

## 12. Open Questions

**Q1 — Duress PIN iOS implementation:** Secure Enclave key deletion on arbitrary PIN entry requires gateway-side key custody rather than iOS keychain. @security_audit to specify implementation path. Blocking for Phase 2 implementation.

**Q2 — Tailscale in Lockdown Mode:** Tailscale is currently recommended but not enforced. Should Lockdown Mode enforce Tailscale-or-LAN-only at the gateway network layer? Recommend yes; @infra to evaluate.

**Q3 — Knowledge Skill index in Lockdown Mode:** The FAISS index is large (potentially GBs). Re-encrypting it on Lockdown Mode activation is slow. Does Lockdown Mode activate the encryption constraint on next index rebuild rather than immediately? TBD.

---

## 13. Dependencies

- iOS Data Protection Complete Protection — all file writes must specify `NSFileProtectionComplete` (@frontend, @backend)
- macOS Secure Enclave key management (@backend)
- Gateway network layer enforcement (@backend, @infra)
- Skill runner Lockdown Mode gate (@backend)
- Duress PIN implementation (@security_audit, @backend — implementation path TBD)
- PUSH_SECURITY_FIX.md — APNs architecture (must be consistent with Lockdown Mode APNs block)
- SOMATIC_INTERFACE.md — prosodic extraction disabled in Lockdown Mode (gateway-enforced)
- EPISTEMIC_IMMUNE_SYSTEM.md — pattern library encrypted under separate key
- METACOGNITIVE_DASHBOARD.md — dashboard data encrypted under separate key

---

*Cross-references: PUSH_SECURITY_FIX.md, SOMATIC_INTERFACE.md, SKILLS_MARKETPLACE.md, EPISTEMIC_IMMUNE_SYSTEM.md, METACOGNITIVE_DASHBOARD.md, POLLY_IOS_SPEC.md §8.8*

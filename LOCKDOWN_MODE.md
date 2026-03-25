# LOCKDOWN_MODE.md

**Status:** Draft  
**Phase:** 3  
**Owner:** @security_audit (threat model), @code_architect (spec structure)  
**Created:** 2026-03-25  
**Depends on:** `SKILLS_MARKETPLACE.md`, `MCP_ADAPTER.md`, `SOMATIC_INTERFACE.md`, §8.8 skill manifest system  
**Blocks:** nothing (Phase 3)  
**Note:** Architectural decisions made here must inform Phase 1 and Phase 2 design to avoid retrofitting.

---

## 1. Purpose

Lockdown Mode is a hardened operational posture for users whose threat model includes device seizure, legal process, hostile personal actors, and network-level surveillance. It is not a separate product — it is the same gateway, the same agents, the same iOS app, with constraints silently enforced.

The framing shift:

- **Standard mode:** "We don't collect your data" (policy — about Polly's behavior)
- **Lockdown mode:** "Your data provably cannot leave your control" (architecture — about what the system makes *impossible*)

A journalist does not need to trust Polly. They need a system where betrayal is structurally impossible.

---

## 2. Target Users

These are not edge cases. They are the users for whom the privacy architecture *actually matters*. All other users benefit incidentally.

- **Journalists with sources** — need deniability that no data transited any server they don't control
- **Domestic abuse survivors** — need an AI assistant an abuser cannot subpoena, access via cloud sync, or detect via network traffic
- **Political organizers in hostile environments** — need communication that creates no metadata trails on third-party infrastructure
- **IRB-bound researchers** — need to demonstrate to ethics boards that data never left a controlled environment

---

## 3. Threat Model

### 3.1 Threat Actors

| Actor | Vector | Goal |
|-------|--------|------|
| Law enforcement with legal process | Subpoena, warrant, border device search | Access conversation history, source identities, session content |
| Hostile personal actor | Physical device access (abusive partner, employer) | Read memory, monitor usage, identify contacts |
| Network-level adversary | Traffic metadata analysis on shared network | Infer usage patterns, connection endpoints, session timing |
| Compromised third-party infrastructure | Any relay, tunnel, or push service | Intercept or log traffic in transit |

### 3.2 Threat/Mitigation Table

| Threat | Mitigation |
|--------|------------|
| Seized device → readable data | iOS Complete Protection class on all files; gateway data encrypted with Secure Enclave-backed key |
| Seized device → behavioral metadata | Prosodic extraction disabled and non-toggleable; voice audio never written to disk; memory-only processing, zeroed on session end |
| Seized device → session history | Session memory non-persistent by default; explicit user action required to enable persistence |
| Network monitoring → usage patterns | No APNs push (polling only over local connection); Cloudflare Tunnel disabled; relay mode disabled; Tailscale or direct LAN only |
| Third-party subpoena | Nothing on Apple/Cloudflare/any relay servers to subpoena — architecture makes it impossible, not policy |
| Forced unlock under duress | Duress path → immediate Secure Enclave key wipe; data permanently unrecoverable, no escrow |
| Malicious skill data exfiltration | Community skills disabled; only Verified + local skills; `network: [read]` non-grantable; `data_destination: cloud` skills blocked |
| Ambient metadata accumulation | Zero extraction posture; no analytics; no telemetry; no crash reporting in lockdown mode |
| Lockdown mode itself as evidence | Mode is invisible — no visible indicator that lockdown is active (see §5) |

---

## 4. Constraints Enforced in Lockdown Mode

### 4.1 Network

| Connection Path | Standard Mode | Lockdown Mode |
|-----------------|---------------|---------------|
| Direct LAN | ✅ Available | ✅ Only allowed local path |
| Tailscale | ✅ Available | ✅ Only allowed remote path |
| Cloudflare Tunnel | ✅ Available | ❌ Hard-blocked — reveals hostname to Cloudflare |
| Relay mode | ✅ Available | ❌ Hard-blocked — relay sees traffic metadata |
| APNs push | ✅ Available | ❌ Disabled — transits Apple infrastructure; polling only |
| mDNS discovery | ✅ Available | ❌ Disabled — broadcasts device presence on LAN |

"Hard-blocked" means enforced at the gateway layer, not hidden in UI. The UI reflects the constraint, but removing the UI element would not re-enable the path.

### 4.2 Data at Rest

**iOS client:**
- All session files, MEMORY.md equivalents, and cached content must use `NSFileProtectionComplete` (Complete Protection class)
- This means: data encrypted with a key derived from the user's passcode, key discarded from memory when device locks
- A locked, seized device reveals nothing — not to forensic tools, not to a court order served to Apple
- Default iOS protection (`NSFileProtectionCompleteUntilFirstUserAuthentication`) is NOT acceptable in lockdown mode

**Gateway (macOS):**
- All session data, memory files, and conversation logs encrypted at rest
- Encryption key stored in macOS Secure Enclave (T2/M-series) or Keychain with `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`
- Plaintext `devices.json`, plaintext `MEMORY.md` not acceptable in lockdown mode
- If Secure Enclave is unavailable (older hardware), warn user that hardware-backed encryption is not available

### 4.3 Voice and Prosodic Data

- Prosodic extraction: **disabled, non-toggleable**
- Voice audio: **never written to disk** — memory-only processing only
- Voice buffer: **zeroed on session end** (explicit memory zero, not just deallocation)
- Rationale: extracted behavioral metadata (pace, energy, confidence) is potential evidence on a seized device regardless of where it's stored. "Never leaves the device" is insufficient when the device is the threat vector.

### 4.4 Skills

- Community tier skills: **disabled**
- Verified + local skills only: **enforced at skill runner level**
- `network: [read]` permission: **non-grantable** (web monitoring creates outbound traffic metadata)
- `data_destination: cloud` skills: **blocked** regardless of trust tier
- Skill install in lockdown mode: only Verified + local skills appear in marketplace browse view; others hidden entirely

### 4.5 Memory and Session History

- Cross-session memory persistence: **off by default**
- Session end behavior: all ephemeral session data zeroed, not just deleted
- Persistent memory: requires explicit user opt-in with a clear warning ("This data will be stored on device and may be accessible if the device is seized")
- Agent MEMORY.md files: encrypted at rest per §4.2; not written if persistence is disabled

### 4.6 Analytics and Telemetry

- All analytics: **hardcoded off**
- Crash reporting: **disabled** (crash reports may contain session context)
- No opt-in UI present in lockdown mode — these settings do not exist

---

## 5. Stealth Mode (Invisible Lockdown)

**Decision: Lockdown mode is invisible by default.**

Rationale: A visible "LOCKDOWN MODE" indicator is itself metadata. In a border search or abusive partner scenario, an adversary seeing that lockdown is active reveals that the user has something to protect — which may be the most dangerous information of all.

**Implementation:**
- Identical UI to standard mode — no banners, no badges, no color changes
- No "Lockdown Mode" label anywhere in the main interface
- Status accessible only via: Settings → Privacy → Advanced → Connection Mode
- That settings path itself uses an innocuous label (e.g., "Privacy Posture" or "Connection Settings") — not "Lockdown Mode"
- The status screen shows current constraints in plain language without alarming framing

**The user knows they enabled it. No one else needs to.**

---

## 6. Duress Path

A duress mechanism allows the user to permanently destroy all encrypted data — making it unrecoverable — in a high-pressure situation (border crossing, arrest, confrontation).

**Mechanism:**
- A secondary "duress PIN" distinct from the device passcode
- Entering the duress PIN at the app's authentication screen triggers: immediate Secure Enclave key wipe for all lockdown-mode encrypted data
- After key wipe: all session history, memory files, and cached content are permanently unrecoverable (the ciphertext remains but the key is gone)
- The app continues to function — it opens to a blank state, as if newly installed
- No confirmation dialog — the wipe is immediate and irreversible by design

**What survives a duress wipe:**
- App installation (the app remains installed)
- User account credentials (unless stored in lockdown-encrypted storage)
- Nothing from sessions conducted in lockdown mode

**iOS existing mechanism:**
- iOS already supports auto-wipe after 10 failed passcode attempts
- Lockdown mode settings should surface this option prominently and recommend enabling it
- The duress PIN is an addition to, not a replacement for, the iOS auto-wipe mechanism

---

## 7. Activation and Transition

### 7.1 Entering Lockdown Mode

1. User navigates to Settings → Privacy → Advanced → Connection Mode
2. Selects hardened posture (label TBD — not "Lockdown Mode" in UI per §5)
3. Shown a plain-language summary of what changes
4. Biometric confirmation required to activate
5. Existing session data: user presented with choice — encrypt existing data in place, or wipe and start fresh. No silent migration.
6. Mode activates. UI returns to normal appearance.

### 7.2 Exiting Lockdown Mode

1. Same settings path
2. Biometric confirmation required
3. Warning: "Exiting this mode will re-enable standard connection options. Your existing encrypted data will remain encrypted."
4. Mode deactivates. Previously-blocked connection paths become available.

**Lockdown mode state must survive app restarts and device reboots.** It is not a per-session setting.

---

## 8. Audit Log

The gateway maintains an activity log (tool calls, skill invocations, connection events). In lockdown mode:

- **The log is encrypted at rest** per §4.2
- **The log is tamper-evident** — each entry is chained (hash of previous entry included), so deletion or modification is detectable
- **Retention policy:** 7 days by default in lockdown mode (shorter than standard). User can reduce to session-only (log wiped on session end). Log cannot be extended beyond 30 days in lockdown mode.
- **The log itself may become evidence** — users should be informed of this. The settings screen for lockdown mode includes: "Activity logs are stored locally and encrypted. They may be accessible if this device is unlocked."
- **Log wipe is included in duress wipe** (§6)

---

## 9. User Guidance (Operational Security)

Architecture cannot enforce all of this. Users must be informed. This section surfaces in the lockdown mode setup flow and in a persistent "Security Guidance" screen in settings.

### Required device configuration (shown at activation):
- [ ] Use a strong alphanumeric passcode (not a 6-digit PIN)
- [ ] Enable Face ID / Touch ID
- [ ] Enable "Erase Data" after 10 failed passcode attempts (Settings → Face ID & Passcode)
- [ ] Keep iOS updated

### Network guidance:
- Avoid activating or using Polly on untrusted public networks
- On Tailscale: ensure your Tailscale network uses MagicDNS and has no exit node that routes through untrusted infrastructure
- Physical network separation (dedicated VLAN for the gateway machine) adds a meaningful layer

### Physical security:
- The strongest encryption is defeated by an unlocked device. Lock your device before any high-risk situation.
- Consider whether the device itself should be present in high-risk situations

### Legal context (shown as a note, not legal advice):
- In most jurisdictions, a properly encrypted locked device cannot be compelled to produce its contents without the passcode
- The architecture of lockdown mode is designed to ensure Polly holds nothing that can be produced by subpoena to third parties
- Consult legal counsel for jurisdiction-specific guidance

---

## 10. Relationship to Other Specs

| Spec | Relationship |
|------|-------------|
| `SKILLS_MARKETPLACE.md` | Lockdown mode enforces a subset of the trust tier model: Verified + local only; `data_destination: cloud` blocked |
| `MCP_ADAPTER.md` | MCP skills using cloud transport are blocked in lockdown mode; local stdio MCP skills from Verified tier are allowed |
| `SOMATIC_INTERFACE.md` | Prosodic extraction disabled and non-toggleable in lockdown mode |
| `PUSH_SECURITY_FIX.md` | APNs push disabled in lockdown mode; polling only |
| `DISTRIBUTED_NODES.md` | PicoClaw nodes: TOFU pairing requires same-subnet check; `network: [read]` non-grantable; inter-node traffic over Tailscale only in lockdown mode |
| `AMBIENT_AGENT SOUL` | `network: [read]` permission non-grantable in lockdown mode |

---

## 11. Implementation Notes (Phase 3 Gates)

Before lockdown mode ships:

- [ ] iOS `NSFileProtectionComplete` applied to all Polly-written files (verify with `ls -l@` entitlement check)
- [ ] Gateway encryption at rest implemented with Secure Enclave key storage
- [ ] APNs push path gated behind lockdown check
- [ ] Cloudflare Tunnel and relay mode gated behind lockdown check
- [ ] Skill runner enforces Verified-only + local-only in lockdown mode
- [ ] Prosodic extraction gated behind lockdown check
- [ ] Voice buffer zero-on-session-end implemented
- [ ] Duress PIN mechanism implemented and tested
- [ ] Audit log chaining implemented
- [ ] Stealth UI verified (no visible indicator in standard views)
- [ ] @security_audit sign-off on all gates above before Phase 3 lockdown work begins

---

*This spec was authored by @security_audit (threat model, constraints, duress path, user guidance) with structural collaboration from @code_architect. Any changes to the threat model section require @security_audit review.*

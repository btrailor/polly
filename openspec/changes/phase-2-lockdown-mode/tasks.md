# Phase 2: Lockdown Mode

**Status:** 📋 Planned  
**Gate:** Phase 1 iOS Foundation complete (architectural hooks must be set in Phase 1)  
**Spec source:** `LOCKDOWN_MODE.md`  
**Pre-ship gate:** @security_audit sign-off required  
**Owners:** @security_audit (threat model, encryption spec, duress path), @code_architect (mode architecture), @backend (gateway enforcement), @frontend (invisible UI constraint)

## Goal

High-stakes privacy mode for journalists, researchers, abuse survivors, activists. Device or gateway may be seized; data may be used as evidence. Invisible by default — no visible "lockdown" indicator.

## Phase 1 Architectural Prerequisites (not retrofittable)
See `phase-1-ios-foundation/tasks.md` Lockdown Mode section. These must be decided in Phase 1:
- `NSFileProtectionComplete` on all session files
- Voice audio never written to disk (memory-only buffers)
- Secure Enclave key path locked
- No APNs hard dependency

## Tasks

### Gateway — Enforcement
- [ ] Session memory non-persistent mode (zero write posture)
- [ ] `network: []` enforced for all skills in lockdown (Community skills disabled, Verified + local only)
- [ ] `network: [read]` non-grantable for any skill in lockdown
- [ ] No Cloudflare tunnel / no relay in lockdown — LAN or Tailscale only
- [ ] Polling-only mode (APNs disabled)

### iOS — Mode Architecture
- [ ] Lockdown Mode toggle: Settings → Privacy → Advanced → Protection Level (3 taps minimum)
- [ ] Mode is invisible — no banner, no lock icon, no visible indicator
- [ ] Prosodic extraction disabled and non-toggleable when active
- [ ] Voice audio: verify memory-only buffer enforcement from Phase 1 hook
- [ ] File encryption: verify `NSFileProtectionComplete` applied to all session files

### iOS — Duress Path
- [ ] Duress PIN configuration (separate from normal PIN)
- [ ] Duress PIN triggers immediate Secure Enclave key wipe
- [ ] Data permanently unrecoverable after key wipe
- [ ] No confirmation dialog on duress — immediate

### iOS — UI Constraints (Invisible)
- [ ] Community skill install blocked (silent — no error message that exposes mode)
- [ ] APNs registration skipped when lockdown active
- [ ] Settings screen shows protection level without "lockdown" wording — label: "Enhanced Protection: On"

### Security Review — @security_audit [REQUIRED BEFORE SHIP]
- [ ] Full threat model review against LOCKDOWN_MODE.md §2 table
- [ ] Duress path implementation review
- [ ] Encryption verification (key derivation, Complete Protection class)
- [ ] Network enforcement verification
- [ ] Sign-off

## Done when
All tasks checked. @security_audit sign-off. Verified: seized device with duress PIN → data unrecoverable. Verified: no data at any third party when lockdown active.

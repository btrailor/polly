# Phase 2: Skills Marketplace

**Status:** 📋 Planned  
**Gate:** Phase 1 iOS Foundation complete  
**Spec source:** `SKILLS_MARKETPLACE.md`, `MCP_ADAPTER.md`, `ASSET_STATE_MACHINE.md`  
**Pre-ship gate:** @security_audit sign-off on both specs required

## Goal

Let users discover and install skills from ClawHub. First-party skills (Knowledge, Creative Code) available at launch. MCP adapter enables third-party skills from the broader ecosystem.

## Tasks

### Gateway — Skill Runner
- [ ] `type: "native"` skill execution pipeline (§8.8 manifest)
- [ ] `type: "mcp"` subprocess execution pipeline
- [ ] Namespace resolver (per-server prefix, eliminates tool shadowing)
- [ ] Request sanitizer
- [ ] Response sanitizer (4 rules + suspicious pattern logging)
- [ ] Tool description linter (install-time + session-open re-check)
- [ ] sandbox-exec isolation (generated profiles from manifest, stdio-only IPC)
- [ ] `${keychain:<key>}` credential interpolation
- [ ] Resource limits (512MB, 30s timeout)

### Gateway — Trust System
- [ ] Signed blocklist (JSON, 7-day staleness, fail-closed offline)
- [ ] Verified tier: cryptographic signature verification (Polly public key trust anchor)
- [ ] Blocked tier: gateway-level rejection
- [ ] Permission-adding update → full re-consent flow

### Gateway — Asset State Machine (`ASSET_STATE_MACHINE.md`)
- [ ] Asset lifecycle states: pending / active / stale / evicted
- [ ] Cross-skill asset sharing default: no (locked per verbal agreement)
- [ ] Asset eviction policy on skill uninstall

### iOS — ClawHub Browser
- [ ] Skill discovery UI (Verified / Community filter)
- [ ] Trust tier badge + data destination callout (separate, per design)
- [ ] Install flow: Community+cloud = two-step confirmation
- [ ] Installed skills management screen

### Security Review — @security_audit [REQUIRED BEFORE SHIP]
- [ ] SKILLS_MARKETPLACE.md threat model §6 sign-off (6 attack surfaces)
- [ ] MCP_ADAPTER.md security architecture sign-off
- [ ] Open questions: key rotation process, mandatory cloud warning categories
- [ ] Sign-off

## Done when
All tasks checked. @security_audit sign-off. A Verified skill and a Community skill installable end-to-end.

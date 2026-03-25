# Phase 2: Sensibility Behavior Injection

**Status:** 📋 Planned  
**Gate:** Phase 1 theme foundation complete (ThemeContext, all 7 theme files, Reas default)  
**Spec source:** `SENSIBILITY_SYSTEM_SPEC.md` §4, §7 Phase 2

## Goal

Selecting a sensibility changes how agents respond. The behavior injection pipeline activates. Structural rules become per-agent configurable.

## Tasks

### Behavior Injection
- [ ] `config.patch` call on theme selection: `polly.ios.aestheticStance = <injectionText>`
- [ ] Behavior injection text for all 7 themes (§19.5 content — tone, register, vocabulary)
- [ ] Artifact aesthetics injection text for all 7 themes (§19.5.1 content — websites, code, documents)
- [ ] Both blocks always included in `polly.ios.aestheticStance` (not tool-gated — 200 token overhead acceptable)

### Multi-Client Conflict Detection
- [ ] On gateway connect: read `config.get polly.ios.aestheticStance`; compare to local MMKV `polly.sensibility`
- [ ] If mismatch: show banner "Another device changed the sensibility to {name}. [Switch] [Keep Mine]"
- [ ] "Switch" → update local MMKV; "Keep Mine" → re-patch gateway
- [ ] @backend: investigate per-device config scoping (`polly.ios.aestheticStance.{deviceId}`) for Phase 2

### Structural Rules (Per-Agent)
- [ ] `config.patch polly.ios.structuralMode.{agentId}` on structural mode change
- [ ] Agent detail → Structural Mode picker (Option A from §6.1)
- [ ] In-chat structural mode pill in augmentation row (Option B from §6.1)
- [ ] Option B overrides Option A for that message
- [ ] Structural rules injection text for all modes from `CREATIVE_CONSTRAINT_ENGINE.md`

## Done when
Selecting Fidenza changes agent tone on the next message. Agent detail structural mode picker persists across sessions. Multi-client conflict banner appears when stances diverge.

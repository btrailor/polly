# Phase 3A: Obsidian Write-Back

**Status:** 💡 Specced  
**Gate:** Phase 2 vault browser + `vault_write` tool (@backend gateway-changes #19)  
**Spec source:** `POLLY_IOS_SPEC.md` §15.3.1; `KNOWLEDGE_WRITE_PATH.md` §3.4, §6.3; `AGENT_BEHAVIOR_CONTRACT.md` §4.3  
**Owners:** @frontend, @backend (vault_write tool)

## Goal

Agents can propose writing to the user's Obsidian vault. User must preview and confirm every write. Never silent. Completes the vault write path: quick capture → promote → agent write-back.

## Tasks

### `vault_write` Tool (Gateway)
- [ ] `vault_write` tool implemented on gateway with params: `path`, `content`, `frontmatter`, `mode: "create" | "append" | "prepend"`, `dedup_check: boolean`
- [ ] Standard frontmatter schema enforced: title, created, modified, source, agent, domain, tags, maturity, polly.origin, polly.session_key, polly.confidence
- [ ] `knowledge_dedup` check before write when `dedup_check: true` — block if similarity ≥ threshold
- [ ] `vault.write_complete` event emitted after successful write
- [ ] @backend owns implementation

### Agent Write-Back Protocol
- [ ] Agents can only propose vault writes — never execute silently
- [ ] Write-back proposal: agent posts "I'd like to save this to your vault. Here's a preview." with preview card
- [ ] Preview card shows: rendered note, proposed path, frontmatter fields
- [ ] User actions: [Save] [Edit Path] [Edit Content] [Dismiss]
- [ ] On confirm: `vault_write` tool called; on dismiss: nothing written
- [ ] `vault_write_enabled` per-agent toggle in Settings (off by default)

### SOUL Baseline Update
- [ ] Add vault write-back behavioral rules to `POLLY_AGENT_TEMPLATES.md` SOUL Baseline §6 (Tool Use block — Phase 3 variant) — agent proposes, user confirms, never silent
- [ ] `allowed_modes: ["write_back"]` field for agents that can propose writes (subset of all agents)

### Daily Note Integration
- [ ] Agent can propose appending morning briefing to today's daily note (Ops Coordinator + The Scheduler)
- [ ] Daily note path config: Settings → Vault → Daily Note Path Template (e.g., `Journal/YYYY-MM-DD.md`)
- [ ] Append mode: adds section with `## Polly — {time}` header; never overwrites
- [ ] User confirmation not required if user toggles "Auto-append daily notes" in Settings (explicit opt-in)

## Done When
Agent can propose a vault write. User sees preview. User confirms → note written. Settings toggle per-agent. @security_audit sign-off on write isolation (agent can only write to vault, not gateway config or other agent workspaces).

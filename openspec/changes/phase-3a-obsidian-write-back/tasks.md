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
Agent can propose a vault write. User sees preview. User confirms → note written. Settings toggle per-agent. @security_audit sign-off on write isolation (agent can only write to vault, not gateway config or other agent workspaces). Household shared vault section indexed and accessible to scoped household nodes.

---

## Household Shared Vault Section (from POLLY_WEB_ANALYSIS.md §3.2)

*The practical, immediately useful answer to "shared household memory." No new vector infrastructure — same FAISS index, same embedding pipeline, additional source section.*

### Design
- `/Household/` directory in Brett's Obsidian vault (or a separate household vault — Q3 from `HOUSEHOLD_NODES.md` §9 determines this)
- Knowledge Skill indexes this section and tags chunks with `source: "household"`
- Household nodes with `vault_sections: ["/Household"]` can retrieve from this section via `knowledge_search`
- Nodes with `vault_write: true` can create notes in `/Household/` via the write-back skill
- Content types: family schedules, shared recipes, school info, Wi-Fi passwords, household reference material

### Tasks (@backend + @frontend)
- [ ] Knowledge Skill: add `/Household/` as an indexed source section in the Obsidian adapter
- [ ] Tag household-section chunks with `source: "household"` in FAISS index metadata
- [ ] Capability scoping enforcement: `vault_sections` field on household node roles gates which Knowledge Skill sections are queryable
- [ ] Partner node: read access to `/Household/` by default; write access opt-in
- [ ] Child node: read access to `/Household/` by default (age-appropriate scoping per `HOUSEHOLD_NODES.md`); no write access by default
- [ ] `HOUSEHOLD_NODES.md` update: document the shared vault section pattern, access tiers, and content guidelines (§15 or new section)
- [ ] Resolve Q3 from `POLLY_WEB_ANALYSIS.md`: should household nodes search `/Household/` conversationally ("what's for dinner?") or only via explicit household skills? Document decision in `HOUSEHOLD_NODES.md`.

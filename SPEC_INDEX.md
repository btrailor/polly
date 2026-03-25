# Polly Spec Index

Single source of truth for all spec documents. A spec doesn't officially exist until it's listed here.

---

## How This Works

- **All specs live at `~/polly/` root** — flat, no subdirectories
- **Naming convention:** `SCREAMING_SNAKE_CASE.md` (e.g. `VOICE_INTERACTION.md`)
- **A spec is "active" when:** it's listed here with a phase and status
- **A spec is "reference" when:** it informs decisions but isn't directly implemented (e.g. philosophy docs)
- **Before writing a new spec:** add it here first with status `planned`, then write it

---

## Active Specs

| Spec | Phase | Status | What it covers |
|------|-------|--------|----------------|
| `POLLY_IOS_SPEC.md` | 1–4 | ✅ Authoritative | Full iOS feature spec — canonical source of truth |
| `POLLY_AGENT_TEMPLATES.md` | 1–4 | ✅ Authoritative | 31 agent templates, team rosters, SOUL content |
| `VOICE_INTERACTION.md` | 1 | 🔨 In progress | Voice requirements: idle timer, mic button prominence, interruption recovery |
| `COPY_VOICE.md` | 1 | 🔨 In progress | Voice design tokens, state machine, copy patterns, accessibility |
| `VOICE_BEHAVIOR_TESTS.md` | 1 | 🔨 In progress | QA test suite for voice interaction |
| `FIGMA_INTEGRATION.md` | 2 | 📋 Planned | Figma link-surfacing in chat; deep-link to boards from spec context |
| `PROJECT_STATUS.md` | 1 | 💡 Idea | Living project status doc — cross-conversation memory for the dev team |
| `AGENT_BOOTSTRAP_DEV.md` | 1 | 💡 Idea | Dev group chat SOUL override — git state verification, PROJECT_STATUS read, spec file existence check |
| `TREE_OF_THOUGHTS.md` | 3 | 💡 Idea | ToT as activatable reasoning mode under §11 (mental models); secondary hook: plan-space search/goal decomposition. Composable with existing cognitive lenses. Ref: https://github.com/kyegomez/tree-of-thoughts |
| `DISTRIBUTED_NODES.md` | 3 | 💡 Idea | PicoClaw node federation — mDNS discovery, node registration, `sessions.create` node routing param, capability registry. PicoClaw nodes appear as remote agents to OpenClaw; iOS client unaware of node boundary. Local-trusted vs remote-VPN trust distinction. Ref: https://github.com/sipeed/picoclaw |
| `CREATIVE_CODE_SKILL.md` | 3 | 💡 Idea | Sandboxed JS execution skill — Paper.js/svg.js/D3 whitelist, theme token injection, SVG output contract, asset library storage. Use cases: icons, slide graphics, agent avatars, generative backgrounds, data viz. **Security requirements (@security_audit):** (1) import/require whitelist enforced at resolver level, (2) SVG output sanitized before client (strip `<script>`, `javascript:` hrefs, event handlers), (3) subprocess CPU/memory hard limits (5s timeout), (4) output path confinement. Depends on skill runner. Feeds FIGMA_INTEGRATION.md. |
| `KNOWLEDGE_SKILL.md` | 2 | 📋 Planned | Unified knowledge skill — pluggable adapter architecture. Obsidian vault + BookLore/EPUB sources. FAISS HNSW + SBERT sparse + RRF + cross-encoder re-ranking. Single install, source cards UI, filter chips in chat. @security_audit gate required. Supersedes `VAULT_RAG_SKILL.md`. |
| `SKILLS_MARKETPLACE.md` | 2 | 💡 Idea | Skills Marketplace — trust tiers (Verified/Community/Blocked), install flow, curation model, gateway-level block enforcement. Must be specced before MCP_ADAPTER.md. @security_audit owns threat model section. Refs: https://github.com/punkpeye/awesome-mcp-servers, https://github.com/modelcontextprotocol/servers |
| `MCP_ADAPTER.md` | 2 | 💡 Idea | MCP transport adapter for OpenClaw skill runner. Wraps any MCP server as a native skill — `sandbox-exec` isolation, manifest-driven sandbox profile, stdio-only IPC, process lifecycle tied to skill session. **Required security additions (per SlowMist checklist + @security_audit):** (1) tool namespace scoping — per-server prefix mandatory, (2) response sanitization before context injection, (3) tool description linting at install time. **Depends on: `SKILLS_MARKETPLACE.md`**. Refs: https://github.com/modelcontextprotocol/servers, https://github.com/slowmist/MCP-Security-Checklist |

---

## Reference Docs

Not directly implemented — inform design and agent behavior decisions.

| Doc | What it is |
|-----|-----------|
| `MASTER_ROADMAP.md` | Phase sequencing and feature pipeline |
| `MONOME_LAYER.md` | Aesthetic-philosophical foundation (the *why* behind design decisions) |
| `INFLUENCE_GUIDE.md` | Liz's Agentic SDLC + Monome synthesis — operational methodology |
| `README.md` | Project overview |

---

## Status Key

| Status | Meaning |
|--------|---------|
| ✅ Authoritative | Complete, stable, source of truth — changes require deliberate decision |
| 🔨 In progress | Being actively implemented |
| 📋 Planned | Spec written, not yet in implementation |
| 💡 Idea | Not yet specced — placeholder for incoming work |
| ✅ Done | Shipped and verified |

---

## Escalation Trigger — When to Move to OpenSpec

Adopt the full OpenSpec system (`openspec/` directory, `changes/` proposals, `INDEX.md`) when **any one** of these is true:

1. **3+ specs in "In progress" simultaneously** — coordination overhead exceeds this index's capacity
2. **Dependency chain exists** — a spec can't be implemented until another spec is done
3. **Ownership ambiguity** — two agents conflict about what's in scope for a feature
4. **Idea dump produces 8+ new specs** — volume requires proposal → review → prioritize workflow

Until then: add to this index, keep specs at root, update status as work moves.

---

*Last updated: 2026-03-25*

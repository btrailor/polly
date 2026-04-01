# Phase 3: Figma Sync

**Status:** 📋 Planned  
**Gate:** Phase 2 Figma Integration complete (auth + file key plumbing shared) + Phase 2 Knowledge Skill complete (spec file writes via Knowledge Skill write path) + OpenClaw skill runner (phase-2-skills-marketplace)  
**Spec source:** `FIGMA_SYNC_SPEC.md`  
**Supersedes/extends:** `phase-2-figma-integration` (Phase 2 adds link-surfacing; Phase 3 adds design-to-code sync)  
**Owners:** @backend (gateway endpoint, webhook registration, health polling, persistence), @frontend (iOS UX — sync cards, Settings), @security_audit (webhook validation, PAT scope review), @design_eng (token naming convention, annotation template)

## Goal

Close the loop between Figma (design source of truth) and Polly (code). When Brett makes a change in Figma and saves a named version, the relevant agents already know what changed. They don't ask him to describe it — they read it. Three sub-phases ship independently in order.

**Design principle (Monome Alignment):** The design file stays in Figma. Polly reads the canonical source — it does not try to be a design tool or host it. No lock-in: the mapping is a YAML file in the vault; delete it and sync stops, nothing breaks. Review gate on by default — no file written without approval.

---

## Phase Breakdown

| Sub-phase | Capability | What it unlocks |
|-----------|-----------|----------------|
| 3A (this) | Design token pull | Figma → `colors.ts` / `theme/index.ts` sync |
| 3B (this) | Component spec pull | Figma frame → structured spec an agent can read |
| 3C (this) | Annotation-driven actions | Figma comment → Polly agent task / ready signal |
| Phase 4 | Component generation | Figma frame → React Native code — **explicitly deferred** |

Phases 3A, 3B, 3C share the same auth layer and webhook infrastructure. They can ship independently in 3A → 3B → 3C order.

---

## Architecture Overview

```
Figma (cloud)
  │ FILE_VERSION_UPDATE webhook (named-version save — RELIABLE)
  │ FILE_COMMENT webhook (reliable)
  ▼
OpenClaw Gateway (Mac Mini, public via Cloudflare Tunnel)
  │ POST /figma/webhook (new gateway endpoint)
  ▼
figma-sync skill
  ├── figma_poll_changes(file_key, since_version)
  ├── figma_pull_tokens(file_key)
  ├── figma_pull_component_spec(file_key, node_ids)
  └── figma_read_annotations(file_key, since_timestamp)
  ▼
Polly iOS client (sync card in chat or notification)
```

**Webhook reliability note:** `FILE_UPDATED` webhook is documented-unreliable (community complaints since 2022). `FILE_VERSION_UPDATE` (fires on explicit named-version save) and `FILE_COMMENT` are reliable. This spec is built around that distinction. **Do not implement on `FILE_UPDATED`.**

---

## Authentication

Two credentials. Both stored in OpenClaw keychain — never in iOS client, never in git.

- **Figma PAT** — scopes: `file_content:read`, `file_metadata:read`, `webhooks:write`. Set in Settings → Integrations → Figma; stored gateway-side.
- **Webhook passcode** — 32-byte hex, generated at webhook registration, stored in gateway config. Validated on every incoming webhook payload.

**Security note for @security_audit:** Figma sends the passcode in the payload body, not as a header signature. Validation approach needs review (see Open Questions).

**PAT scope note:** `file_content:read` gives read access to all files the user owns — Figma does not support file-scoped PATs, only file-scoped webhooks. @security_audit review required.

---

## Phase 3A — Design Token Pull

### What Syncs

Figma styles (NOT Variables — Variables API requires Enterprise plan, explicitly out of scope) mapping to:
- Color styles → `src/theme/colors.ts`
- Text styles → `src/theme/index.ts` typography tokens
- Effect styles → shadow tokens

### How It Works

1. `FILE_VERSION_UPDATE` webhook fires
2. Gateway calls `GET /v1/files/:key/styles` → style metadata
3. Batched `GET /v1/files/:key/nodes?ids=...` for actual values (max 100 IDs per request)
4. `figma-sync` skill maps style names → Polly token names via `figma-token-map.yaml` in vault
5. Generates diff vs. last synced version
6. If changes: surfaces sync card in chat (review gate) or auto-applies (if setting on)

### Token Naming Convention

Figma styles must use `polly/` prefix to be synced. Naming maps to code:

```
polly/colors/background/primary → colors.backgroundPrimary
polly/colors/accent/orange      → colors.accentOrange
polly/type/body/regular         → typography.bodyRegular
polly/shadow/card               → shadows.card
```

Styles without `polly/` prefix are not synced (design-only). The `figma-token-map.yaml` in the vault handles divergence cases (legacy renames, simplified target names).

### Generated Output Format

```typescript
// src/theme/colors.ts — updated section
// @figma-sync: polly/colors/background/primary → v47 (2026-03-30)
export const backgroundPrimary = '#1a1a1a'; // was '#191919'
```

`@figma-sync` comment carries: Figma style name, version, date — auditable history.

### Auto-Apply Setting

- **Default:** Review gate — sync card in chat, user approves before files written
- **Settings → Integrations → Figma → "Auto-apply token updates":** when on, writes immediately and surfaces notification
- Recommendation: keep review gate on until token mapping is trusted

### Tasks — Phase 3A (@backend)
- [ ] New gateway endpoint `POST /figma/webhook` — validates passcode, dispatches to figma-sync skill
- [ ] `GET /v1/files/:key/styles` call with batched node resolution (max 100 IDs/request)
- [ ] `figma-token-map.yaml` schema: `overrides` map (Figma style name → code path)
- [ ] Diff engine: changed/added/removed tokens since last synced version
- [ ] Persist "last synced version" (see Open Question Q2: config file vs. SQLite)
- [ ] Rate limiting: track request timing; queue pulls if multiple webhooks fire rapidly (limit: 120 GET file requests/min per PAT, FILE_COST=50)
- [ ] `@figma-sync` comment generation in output TypeScript
- [ ] Auto-apply mode: write `colors.ts` / `theme/index.ts` directly when setting on; commit if git integration live
- [ ] Review gate mode: surface sync card to iOS client with diff payload

### Tasks — Phase 3A (@frontend)
- [ ] Settings → Integrations → Figma screen: PAT input, file URL input, auto-apply toggle
- [ ] Token sync card: "🎨 Figma Design Tokens — v47 available" with changed tokens list, [Preview diff] / [Apply to theme/] / [Dismiss] actions
- [ ] Preview diff view: shows proposed `colors.ts` changes before writing
- [ ] Dismissed sync surfaced in notification badge for later review

---

## Phase 3B — Component Spec Pull

### Two Pull Paths

**Path 1: Linked spec files (proactive)**  
Add `figma_node: "ABC123:4567"` to spec file frontmatter. When `FILE_VERSION_UPDATE` diff includes that node, figma-sync skill auto-pulls and updates a companion `COMPONENT.figma.md` in the vault.

**Path 2: On-demand pull (reactive)**  
In chat with any dev-focused agent: "Pull the latest spec for the voice button from Figma." → agent calls `figma_pull_component_spec`.

### Component Spec Format (structured markdown)

```markdown
## Voice Button (v47 — 2026-03-30)
**Node:** `ABC123:4567` | **Figma:** [View](figma://file/ABC123/...)

### Dimensions
- Width: 64pt | Height: 64pt | Corner radius: 32pt

### Fills
- Background: `accent` (→ `#f0903b` via token map)

### Variants
| Variant | Property | Value |
|---------|----------|-------|
| default | state | idle |
| recording | state | active |
| loading | state | loading | ← new in v47

### Layer Structure
VoiceButton (COMPONENT_SET)
├── VoiceButton/idle (COMPONENT)
│   ├── bg (ELLIPSE)
│   └── icon (INSTANCE → MicIcon)
└── VoiceButton/loading (COMPONENT) ← new

### Notes
- No accessible label defined — @design_eng: add accessibilityLabel.
```

### Tasks — Phase 3B (@backend + @code_architect)
- [ ] `figma_node` frontmatter field support in spec files — gateway watches tracked nodes from config
- [ ] Auto-pull on `FILE_VERSION_UPDATE` when tracked node in diff → write `COMPONENT.figma.md` via Knowledge Skill write path
- [ ] On-demand `figma_pull_component_spec(file_key, node_ids)` tool
- [ ] Component spec markdown formatter (dimensions, fills, variants table, layer structure)
- [ ] Track changed vs. unchanged fields between versions (diff annotation in output)
- [ ] `track_nodes` config list: node ID → spec file mapping in gateway config

### Tasks — Phase 3B (@frontend)
- [ ] Component spec sync card: "📐 Voice Button updated — v47" with change summary, [View spec] / [Open in Figma] / [Dismiss]

### Tasks — Phase 3B (@design_eng)
- [ ] Accessibility label gap annotation convention: when Figma component has no accessibilityLabel, figma-sync flags it in the spec output

---

## Phase 3C — Annotation-Driven Actions

### Comment Conventions

Designers leave structured comments in Figma; Polly routes them:

| Comment | Polly behavior |
|---------|---------------|
| `@polly:task [message]` | Creates task note in vault with link to Figma comment |
| `@polly:ready [message]` | Triggers Phase 3B spec pull for the commented frame |
| `@polly:hold [message]` | Adds `hold: true` to linked spec file frontmatter |
| `@polly:qa [message]` | Surfaces card in chat addressed to QA agent |

Format: `@polly:<action> [optional message]`

**Webhook used:** `FILE_COMMENT` — confirmed reliable. Phase 3C is lower-risk than 3A/3B from an infrastructure standpoint.

### Tasks — Phase 3C (@backend)
- [ ] `FILE_COMMENT` webhook handler — parse `@polly:` annotations
- [ ] `@polly:task` → create vault note via Knowledge Skill write path; include Figma comment link, frame name, author
- [ ] `@polly:ready` → trigger `figma_pull_component_spec` for the commented frame
- [ ] `@polly:hold` → write `hold: true` to linked spec file frontmatter
- [ ] `@polly:qa` → surface chat card for QA agent
- [ ] Non-`@polly:` comments: ignore silently (no noise)

### Tasks — Phase 3C (@frontend)
- [ ] Task card: "💬 Figma task from @design_eng" with message, [Open task] / [Open in Figma] / [Dismiss]
- [ ] All sync cards appear in Figma Sync section at top of Code Architect chat (or active dev session agent) — not in non-dev contexts, not during voice interaction

---

## Gateway Configuration

New config block:

```yaml
integrations:
  figma:
    enabled: true
    personal_access_token: "{{keychain:figma_pat}}"
    webhook_passcode: "{{keychain:figma_webhook_passcode}}"
    files:
      - key: "ABC123xyz"
        name: "Polly Design System"
        token_prefix: "polly/"
        auto_apply_tokens: false
        track_nodes:
          - id: "4567"
            spec: "VOICE_BUTTON.md"
    rate_limit:
      max_requests_per_minute: 100  # conservative, limit is 120
      queue_overflow: "delay"       # delay | drop | error
```

### Tasks — Gateway Config (@backend)
- [ ] `integrations.figma` config block schema
- [ ] Webhook registration on setup: call Figma webhook API, register `FILE_VERSION_UPDATE` + `FILE_COMMENT`, pointing to Cloudflare Tunnel URL; auto-generate webhook passcode, store in keychain
- [ ] `figma sync reset` command: regenerate + re-register webhook passcode
- [ ] PING event handling: confirm receipt on webhook registration

---

## Setup Flow (Settings → Integrations → Figma)

1. Enter PAT → gateway validates via `GET /v1/me`
2. Add file → user pastes Figma URL, gateway extracts file key
3. Register webhook → auto-generates passcode, registers `FILE_VERSION_UPDATE` + `FILE_COMMENT`, PING confirms
4. Test → PING event received = ✅
5. Token mapping (optional) → upload/edit `figma-token-map.yaml` in vault

### Tasks — Setup Flow (@frontend)
- [ ] Settings → Integrations → Figma screen: PAT input + validate, file URL add, webhook status indicator (registered / not registered / error), [Test Connection] button

---

## Explicitly Deferred (do not scope creep)

| Feature | Reason deferred |
|---------|----------------|
| Component code generation (Figma → RN) | Output quality from current tools creates more work than it saves. Locofy/Anima problem. Phase 4+ |
| Figma Variables API sync | Requires Enterprise plan ($45/editor/month) — not viable for personal/small team |
| Real-time / live sync | `FILE_UPDATED` webhook unreliable; polling would spam API + hit rate limits |
| Writing back to Figma | Figma REST API does not support write operations on file content (nodes, styles) — comments and webhooks only |

---

## Open Questions

| # | Question | Owner | Notes |
|---|----------|-------|-------|
| Q1 | Where does webhook receiver live in OpenClaw? New `POST /figma/webhook`, or generic integration webhook handler? | @backend | Generic handler preferred for future integrations |
| Q2 | Persistence model for "last synced version"? | @backend | Config file vs. SQLite — recommend SQLite (same as budget tracking) |
| Q3 | `@figma-sync` comment in generated TypeScript vs. separate changelog file? | @design_eng | Current spec uses inline comment — confirm convention |
| Q4 | Token naming convention (`polly/colors/...`) needs Figma annotation template so designer knows how to name styles | @design_eng | Needed before 3A ships |
| Q5 | Webhook passcode validation: HMAC-SHA256 of payload, or shared secret in body? Figma sends passcode in payload body, not as header signature | @security_audit | **Security review required** |
| Q6 | PAT scope (`file_content:read` = all files user owns) — acceptable, or scope to specific files? (Figma doesn't support file-scoped PATs, only file-scoped webhooks) | @security_audit | **Security review required** |

---

## Dependencies

| Dependency | Status | Notes |
|-----------|--------|-------|
| Cloudflare Tunnel | ✅ Phase 1 | Webhook delivery endpoint — already live |
| `phase-2-figma-integration` | 📋 Phase 2 | Auth + file key plumbing shared; PAT storage established |
| OpenClaw skill runner | Phase 2 | figma-sync skill needs it |
| Knowledge Skill write path | Phase 2 | Spec file writes + annotation task creation |
| `CREATIVE_CODE_SKILL.md` | Phase 3 | Feeds generated token output; 3A can work without it |

Minimum viable: Phase 3A can ship with just the Cloudflare Tunnel and a standalone gateway webhook receiver before the skill runner is ready.

---

## Done When

**3A:** Token pull working end-to-end. Webhook fires on named version save. Sync card surfaces in chat. Review gate and auto-apply modes both working. `figma-token-map.yaml` schema documented. @security_audit Q5+Q6 resolved.

**3B:** On-demand spec pull working. Tracked-node auto-pull working. `COMPONENT.figma.md` generated and written to vault. Change diff annotated in output.

**3C:** `@polly:task/ready/hold/qa` annotations routing correctly. Task notes created in vault. QA card surfacing to correct agent.

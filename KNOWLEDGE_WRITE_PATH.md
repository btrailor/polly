# KNOWLEDGE_WRITE_PATH.md

Phase 1–3 — How Content Enters and Leaves the Knowledge Base  
Status: Draft  
Owners: @code_architect (architecture), @backend (gateway write operations), @frontend (iOS write surfaces)  
Last updated: 2026-03-25  
Cross-references: `POLLY_IOS_SPEC.md` §11.5, §15.3.1, §4.8; `KNOWLEDGE_SKILL.md`; `KNOWLEDGE_SERVICE_CONTRACTS.md`; `POLLY_AGENT_TEMPLATES.md` (SOUL Baseline); `COGNITIVE_ARTIFACT.md`; `PRACTICE_LAYER.md`  
Salvage references: `core/knowledge_writer.py`, `core/notes_dedup.py`, `core/unlinked_mentions.py`, `integrations/obsidian_smart.py`

---

## 1. The Problem This Solves

Content enters Polly's knowledge base through at least seven different paths, each specced in a different document, each with its own format assumptions, none coordinated:

| Write Path | Source Spec | Format | Destination | Phase |
|-----------|-------------|--------|-------------|-------|
| Quick capture | §11.5 | Raw markdown + frontmatter | `_inbox/` in vault | 1 |
| Share extension | §11.5 | URL/text/image → markdown | `_inbox/` in vault | 1 |
| Agent memory writes | SOUL Baseline | Structured markdown (6 sections) | `memory/YYYY-MM-DD.md` in agent workspace | 1 |
| Agent write-back (opt-in) | §15.3.1 | Markdown + frontmatter | Configured vault folder | 3 |
| Promotion | §11.5 promotion flow | Template-processed markdown | Domain folder in vault | 2 |
| Conversation export | §4.8 | Markdown or JSON | iOS share sheet → anywhere | 1 |
| Cognitive Artifact export | `COGNITIVE_ARTIFACT.md` | Multi-layer package | Filesystem | 3 |

Each path makes different assumptions about frontmatter schema, wikilink conventions, tag format, and file naming. There is no shared note format. The Knowledge Skill has to handle N different formats when indexing. Notes created by different paths don't cross-reference each other. The wikilink graph has gaps.

---

## 2. The Standard Note Format

Every piece of content that Polly writes to the vault — regardless of path — uses this format:

```markdown
---
title: "Note Title"
created: 2026-03-25T14:30:00
modified: 2026-03-25T14:30:00
source: capture | agent | promotion | conversation | import
agent: the-researcher        # which agent created it (null for user captures)
domain: signals              # domain hint (nullable — auto-detected or user-set)
tags: [norns, synthesis, idea]
maturity: 30-ideas | 20-active | 10-archive
polly:
  origin: quick-capture | share-extension | write-back | promotion | conversation-save | export
  session_key: null          # TODO: @backend to confirm canonical session key format
  promoted_from: null        # _inbox/path.md if promoted (nullable)
  confidence: null           # RAG confidence of source material (nullable, Phase 2+)
---

[content body — standard markdown with [[wikilinks]]]
```

### 2.1 Field Definitions

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `title` | Yes | string | Human-readable title. Generated from first heading or first sentence. |
| `created` | Yes | ISO 8601 | Creation timestamp. Never modified. |
| `modified` | Yes | ISO 8601 | Last modified. Updated on every edit. |
| `source` | Yes | enum | `capture` (user-initiated), `agent` (write-back), `promotion`, `conversation`, `import` |
| `agent` | No | string | Agent ID. Null for user captures. |
| `domain` | No | string | Domain tag matching user taxonomy. Auto-detected from content or user-selected. `null` if gateway unavailable (see §3.1). |
| `tags` | No | string[] | Free-form, Obsidian-compatible. `[]` if gateway unavailable (see §3.1). |
| `maturity` | Yes | enum | `30-ideas` (raw), `20-active` (working), `10-archive` (reference). Captures start at `30-ideas`. |
| `polly.origin` | No | enum | Specific creation path. |
| `polly.session_key` | No | string | Which conversation this note came from. **Format TBD — @backend to confirm canonical gateway session key pattern.** |
| `polly.promoted_from` | No | string | Original inbox path if promoted. |
| `polly.confidence` | No | float | RAG retrieval confidence if content came from augmented generation. Phase 2+. |

### 2.2 Compatibility with Existing Vaults

Existing vault notes without Polly frontmatter are handled by the Knowledge Skill adapter:
- **Notes with Polly frontmatter:** Full metadata extraction, all fields filterable
- **Notes without Polly frontmatter:** Treated as `source: import`, `maturity: 20-active`, domain auto-detected from content/tags, other fields null

The Knowledge Skill **never modifies existing notes** to add frontmatter. Polly's format is additive — it applies only to notes Polly creates.

---

## 3. Write Paths — Standardized

### 3.1 Quick Capture (Phase 1)

Writes to `_inbox/YYYY-MM-DD-HHmm-{slug}.md` (slug = lowercase, hyphens, max 40 chars).

```markdown
---
title: "Norns synthesis idea"
created: 2026-03-25T14:30:00
modified: 2026-03-25T14:30:00
source: capture
domain: signals
tags: [norns, synthesis]
maturity: 30-ideas
polly:
  origin: quick-capture
---

Had an idea about granular synthesis on norns...
```

**Offline degradation (@backend, 2026-03-25):** If the gateway is down at capture time, domain auto-detection and tag suggestion require a gateway call. Phase 1 degradation behavior: write the file immediately with `domain: null` and `tags: []`. No silent failures — just deferred enrichment. The user processes domain/tags at promotion time. Captures never block on gateway availability.

**Destination fallback:** If no vault is configured, write to `~/.polly/inbox/` on gateway. Sync to vault when connected.

### 3.2 Share Extension (Phase 1)

Same as Quick Capture but `polly.origin: share-extension`. Content may be URL, text selection, or image.

For URLs: body includes the URL and optionally a fetched summary (if gateway reachable for extraction). Same offline degradation applies — write with null domain/tags, enrich at promotion.

### 3.3 Agent Memory Writes (Phase 1)

Agent memory files (`memory/YYYY-MM-DD.md` in agent workspace) are **working state, not knowledge base content**. They follow the SOUL Baseline memory format (6 sections), not the standard note format. The Knowledge Skill indexes them via the conversation history adapter. No change to this path.

### 3.4 Agent Write-Back (Phase 3)

Standardized with full frontmatter + agent-generated wikilinks:

```markdown
---
title: "Retry Logic Architecture Analysis"
created: 2026-03-25T16:00:00
modified: 2026-03-25T16:00:00
source: agent
agent: code-architect
domain: sigils
tags: [architecture, retry, rag-pipeline, polly-generated]
maturity: 20-active
polly:
  origin: write-back
  session_key: null   # @backend to confirm format
---

## Summary
The current retry logic in the RAG pipeline uses exponential backoff...

The [[RAG Pipeline]] connects to [[Retry Manager]] via...
```

Agent-generated wikilinks: agents should use `[[wikilink]]` syntax for concepts that may have vault notes. The SOUL baseline instructs this (see §6.3). Dangling links (no target yet) are stored and resolved if the target note is created later.

**Write-back requires user confirmation.** Agent proposes; user reviews preview; user confirms. Never silent.

### 3.5 Promotion (Phase 2)

Inbox capture → organized note via a promotion sheet:

```
[1] User taps "Process" on capture
[2] Agent analyzes: suggests title, domain, tags, folder, wikilinks, template
[3] User reviews in promotion sheet (title, domain, tags, folder, maturity, links found, preview)
[4] Write promoted note: standard frontmatter, maturity: 20-active, polly.promoted_from set
[5] Original capture: deleted or moved to _inbox/_processed/
[6] vault.write_complete event → Knowledge Skill incremental re-index
```

The "Links found" step connects the wikilink graph. Promotion should query existing vault notes for entity matches and offer to create stub notes for new entities.

### 3.6 Save Conversation to Vault (Phase 2 — new path)

Not in any current spec. High-value, low-effort.

Trigger: Long-press menu → "Save to Vault" (single message or conversation-level).

Pipeline:
- Agent reformats selected messages into structured note (not raw transcript — headings, decisions, code blocks preserved)
- Standard frontmatter: `source: conversation`, `polly.origin: conversation-save`, `polly.session_key` set
- User reviews title, domain, tags
- Writes to vault via standard path
- `vault.write_complete` event → incremental index

---

## 4. The Notion Gap

### 4.1 Obsidian vs. Notion: Structurally Different

| Aspect | Obsidian | Notion |
|--------|----------|--------|
| Storage | Local filesystem (markdown) | Cloud API (proprietary database) |
| Note format | Markdown + YAML frontmatter | Notion blocks + page properties |
| Wikilinks | `[[note title]]` — filesystem convention | Page references — API-mediated |
| Offline access | Full | None |
| Write path | Direct file write | HTTP API → Notion servers |

Markdown frontmatter doesn't exist in Notion. Wikilinks don't exist in Notion. Offline doesn't exist for Notion. These are structural differences, not implementation details.

### 4.2 Recommended Approach

**Phase 1–2: Obsidian-only.** All vault features target Obsidian. The standard note format is markdown + YAML frontmatter.

**Phase 3: Notion as a separate source adapter.** The Knowledge Skill gets a Notion adapter implementing the same `KnowledgeAdapter` interface. Frontmatter fields map to Notion page properties:

| Standard Field | Notion Equivalent |
|---------------|-------------------|
| `title` | Page title |
| `created` | Created time property |
| `source` | Select property: "Polly" |
| `agent` | Text property: agent ID |
| `domain` | Select property: domain name |
| `tags` | Multi-select property |
| `maturity` | Select property: "Ideas" / "Active" / "Archive" |

Quick capture to Notion: New row in "Polly Inbox" database. Notion write path requires an offline queue (Phase 3) since writes require API connectivity.

---

## 5. The Write Pipeline — Unified

All write paths flow through a shared pipeline:

```
[Write trigger]
     │
     ▼
[1] Format standardization
    - Apply standard frontmatter schema
    - Auto-detect domain from content keywords (gateway call)
    - Auto-suggest tags (gateway call)
    - If gateway unavailable: domain: null, tags: [] — defer to promotion

     │
     ▼
[2] Dedup check (Phase 2+)
    - knowledge_dedup(content, threshold) — see §5.1
    - If similarity > threshold: warn user "This looks similar to [[existing note]]"
    - User decides: merge, create anyway, or cancel

     │
     ▼
[3] Wikilink suggestion (Phase 2+)
    - Scan for entity names matching existing note titles
    - Suggest [[wikilinks]] for recognized entities
    - Agent write-backs: agent generates links in content

     │
     ▼
[4] Destination routing
    - Obsidian: write markdown file via security-scoped bookmark
    - Notion: create page/row via API (Phase 3)
    - No vault: queue locally at ~/.polly/inbox/, sync when connected

     │
     ▼
[5] Post-write indexing
    - Emit vault.write_complete event (see §5.2)
    - Knowledge Skill incremental index update — not full re-index

     │
     ▼
[6] Confirmation
    - "Note saved" toast with link to open note
    - If dedup warning shown: surface comparison
```

### 5.1 `knowledge_dedup` Tool

```json
{
  "name": "knowledge_dedup",
  "description": "Check if similar content already exists in the knowledge base before writing. Returns similar notes and a recommendation.",
  "parameters": {
    "content": "string — the note body (or first 500 chars for performance)",
    "threshold": "float — similarity threshold 0.0–1.0 (see defaults below)"
  },
  "returns": {
    "similar_notes": "[{ title, path, similarity_score, preview }]",
    "recommendation": "\"create\" | \"merge\" | \"skip\""
  }
}
```

**Recommended threshold defaults by origin (@backend, 2026-03-25):**

| Origin | Default Threshold | Rationale |
|--------|------------------|-----------|
| `quick-capture` | 0.85 | Captures are raw; loose dedup, process at promotion |
| `share-extension` | 0.85 | Same as capture |
| `promotion` | 0.80 | Being processed — worth a closer look |
| `conversation-save` | 0.75 | Conversations produce synthesis; check for existing synthesis |
| `write-back` | 0.70 | Agent synthesis docs — tight check, matches `core/notes_dedup.py` default |

The `threshold` param allows per-call override. These are defaults; callers can tighten or loosen.

### 5.2 `vault.write_complete` Event

Post-write indexing needs a concrete mechanism. File watcher works for Obsidian but introduces lag for Notion and misses writes when watcher isn't running (@backend, 2026-03-25).

**Solution:** The gateway write path emits a `vault.write_complete` event after every successful write, regardless of backend. The Knowledge Skill subscribes to this event and triggers an incremental index update.

```json
{
  "event": "vault.write_complete",
  "payload": {
    "path": "string — vault-relative path or Notion page ID",
    "backend": "obsidian | notion",
    "operation": "create | update | delete",
    "metadata": {
      "source": "capture | agent | promotion | conversation | import",
      "domain": "string | null",
      "maturity": "string"
    }
  }
}
```

This event is documented in `KNOWLEDGE_SERVICE_CONTRACTS.md §2.6`. The Knowledge Skill is the primary subscriber; Practice Layer may also subscribe in Phase 3.

### 5.3 The Wikilink Suggestion Engine

| Phase | Behavior |
|-------|----------|
| Phase 1 | No wikilink suggestions (no Knowledge Skill) |
| Phase 2 | Simple title matching against `knowledge_graph` note index |
| Phase 3 | Entity extraction + fuzzy matching — "retry manager" → suggest `[[Retry Manager]]` even if phrase ≠ note title |

For agent write-backs: agent generates wikilinks using `vault_write` tool + existing note titles from `knowledge_graph`. See §6.

---

## 6. Agent Write-Back Protocol

### 6.1 When Agents Suggest Write-Back

**Should offer:**
- User explicitly asks ("save this", "write this up", "add this to my vault")
- Conversation produces a substantial artifact (architecture analysis, research summary, decision doc)
- Agent detects user is capturing knowledge they'll want to reference later

**Should not write:**
- Automatically after every conversation
- For transient exchanges (debugging, casual chat, quick Q&A)
- Without user confirmation — ever

### 6.2 `vault_write` Tool (Phase 3)

```json
{
  "name": "vault_write",
  "description": "Write a note to the user's vault. Always previewed and confirmed by the user before writing. Never called silently.",
  "parameters": {
    "title": "string",
    "content": "string — markdown body with [[wikilinks]]",
    "domain": "string | null — suggested domain",
    "tags": "string[] — suggested tags",
    "maturity": "\"30-ideas\" | \"20-active\" | \"10-archive\"",
    "folder": "string | null — suggested folder path within vault"
  },
  "returns": {
    "path": "string — where the note was saved",
    "dedup_warning": "DedupResult | null",
    "wikilinks_resolved": "integer — links matched to existing notes",
    "wikilinks_dangling": "integer — links with no target yet"
  }
}
```

The iOS app intercepts the tool call result and shows a markdown preview before confirming the write. The agent proposes; the user confirms.

### 6.3 SOUL Baseline Addition

The following section is added to the Standard SOUL Baseline (in `POLLY_AGENT_TEMPLATES.md`):

```markdown
## Vault Write-Back

When you produce a significant artifact — a plan, an analysis, a research summary, a design
document — that the user would want to reference later, offer to save it to their vault.

How to offer:
- "Want me to save this to your vault?"
- If yes: use vault_write with a suggested title, domain, and tags.
- Use [[wikilinks]] for any concept that might have an existing note.
- Always let the user review before saving. Never write silently.

Worth saving:
- Architectural decisions and their reasoning
- Research summaries with sources
- Plans and their rationale
- Technical analyses
- Meeting notes and action items

Not worth saving:
- Quick Q&A exchanges
- Debugging back-and-forth
- Casual conversation
- Content the user is already capturing elsewhere
```

---

## 7. Phase Plan

### Phase 1
- Standard note format defined (this document)
- Quick capture writes using standard frontmatter; `domain: null`, `tags: []` if gateway unavailable
- Share extension writes using standard frontmatter
- Agent memory writes unchanged (different path, different purpose)
- No dedup, no wikilink suggestions, no write-back

### Phase 2
- Promotion pipeline (inbox → organized note)
- Dedup check before write (`knowledge_dedup` tool — see §5.1)
- Wikilink suggestions at promotion time (simple title matching)
- "Save conversation to vault" write path
- `vault.write_complete` event + incremental index notification
- Notion adapter format spec (property ↔ frontmatter mapping)

### Phase 3
- Agent write-back with preview/confirmation (`vault_write` tool)
- Vault write-back SOUL baseline addition (§6.3)
- Full wikilink suggestion engine (entity extraction + fuzzy matching)
- Notion adapter implementation
- Offline write queue for Notion (captures queue locally, sync when API available)

---

## 8. Open Items

| Item | Status |
|------|--------|
| `polly.session_key` canonical format | **@backend to confirm** — using `agent:the-researcher:main` as placeholder; needs to match actual gateway session key schema |
| Readwise highlights integration | Phase 3 — `source: import`, standard frontmatter |
| Full offline write queue design (Notion) | Phase 3 — Notion requires API; queue locally, sync when connected |

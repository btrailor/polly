# Phase 2/3A: Web-Fetch Skill

**Status:** 💡 Proposed  
**Phase 2 gate:** Voice upgrade (Whisper STT) + gesture layer recognition pipeline  
**Phase 3A gate:** `vault_write` tool live (gateway-changes #19) + `phase-3a-obsidian-write-back` shipped  
**Owners:** @backend (skill scaffold, tool handlers, gesture registration), @code_architect (Scrapling integration, import pipeline), @security_audit (network permissions, domain allowlist), @frontend (permission prompt UI, import preview UI), @design_eng (import preview layouts)

---

## Problem

`web_fetch` appears in `POLLY_IOS_SPEC.md §6.5` tool label mapping but has no spec, no implementation plan, and no backing infrastructure. Agents that want to read a URL have no tool to call. The current tool surface (`AGENT_BEHAVIOR_CONTRACT.md §2.2`) has `web_search` (Brave, search queries) but nothing for reading page content.

The vault import use case — "catalogue all posts at Low-Tech Magazine by category and bring them into my Obsidian vault as structured notes" — requires: (1) fetching and parsing HTML, (2) structuring into Obsidian-formatted notes, (3) writing via `vault_write`. None of these steps have gateway infrastructure today.

---

## Three Tools

| Tool | What it does | Phase |
|------|-------------|-------|
| `web_fetch` | Fetch a single URL, return cleaned text + metadata | Phase 2 |
| `web_crawl` | Crawl a site from seed URL, return structured page list with category extraction | Phase 2 |
| `web_import` | Full pipeline: crawl → structure → propose vault write | Phase 3A |

`web_fetch` and `web_crawl` have no vault dependency — ship Phase 2. `web_import` gates on `vault_write`.

---

## Skill Layout

```
src/skills/web-fetch/
  manifest.json
  main.py          ← tool handler entry point
  fetcher.py       ← Scrapling wrapper (fetch + crawl)
  extractor.py     ← HTML → structured content
  importer.py      ← crawl → vault notes pipeline (Phase 3A)
  requirements.txt ← scrapling, beautifulsoup4, markdownify
```

**Manifest:**
```json
{
  "id": "web-fetch",
  "version": "1.0.0",
  "type": "native",
  "tools": ["web_fetch", "web_crawl", "web_import"],
  "permissions": ["network:read"],
  "network": "domain-scoped",
  "data_destination": "local",
  "cloud_domains": []
}
```

`network: "domain-scoped"` — outbound HTTP only to user's allowlist. Not `*`.

---

## Phase 2: web_fetch + web_crawl

### Gateway — Skill Scaffold (@backend)
- [ ] Skill directory `src/skills/web-fetch/` with manifest, main.py, requirements.txt
- [ ] `requirements.txt`: `scrapling`, `markdownify`, `beautifulsoup4`
- [ ] Register skill with OpenClaw gateway
- [ ] `@backend` owns scaffold; `@security_audit` sign-off on manifest permissions required

### Gateway — web_fetch Tool (@code_architect)
- [ ] `fetcher.py`: Scrapling `Fetcher` wrapper with retry (3 attempts, 2s delay)
- [ ] `extractor.py`: readability-style main content extraction from Adaptor page object
- [ ] `markdownify` HTML → Markdown conversion
- [ ] Metadata extraction: `<meta>` tags, OpenGraph, JSON-LD where available
- [ ] Tool handler: input validation → domain allowlist check → fetch → extract → return
- [ ] **Fetch tier escalation:** `tier: "stealth"` triggers `StealthyFetcher` (Playwright-patched Chromium); `tier: "dynamic"` triggers `DynamicFetcher` (full browser automation). Default: `Fetcher` (curl_cffi, browser TLS fingerprint). Stealth/dynamic opt-in per domain only.
- [ ] Error handling: 403/429/timeout → structured error response, not exception

**Output schema:**
```json
{
  "url": "...",
  "title": "...",
  "content": "...",
  "format": "markdown",
  "links": [{"text": "...", "href": "..."}],
  "metadata": {"author": "...", "published_date": "...", "tags": [], "description": "..."},
  "fetch_tier": "default",
  "status": 200
}
```

### Gateway — web_crawl Tool (@code_architect)
- [ ] Seed URL fetch + link extraction via `Adaptor.css('a')`
- [ ] BFS crawl to `max_depth` + `max_pages` limits
- [ ] `follow_pattern` regex enforcement (don't crawl off-domain)
- [ ] Category extraction: URL path segments, breadcrumbs, `category_signals` parameter
- [ ] Robots.txt fetch + respect (configurable off per domain in gateway config)
- [ ] Per-domain rate limiting: 1 req/s default; configurable
- [ ] Tool handler: crawl → structure → return page list + categories

### Gateway — Domain Allowlist (@backend, @security_audit sign-off required)
- [ ] `polly.web_fetch.allowed_domains[]` in gateway config schema
- [ ] Hard block on every outbound request if domain not in allowlist
- [ ] `domain_permission_request` WebSocket event: gateway → iOS when unlisted domain hit
- [ ] Allow-once vs. always-allow handling in allowlist manager
- [ ] Lockdown Mode: all web_fetch/web_crawl/web_import disabled (outbound HTTP creates network metadata — incompatible with Lockdown)

### iOS — Permission Prompt (@frontend)
- [ ] `DomainPermissionSheet` component: domain name, "Allow once" / "Always allow" / "Deny"
- [ ] Triggered by `domain_permission_request` gateway event
- [ ] "Always allow" → updates gateway config allowlist, fetch resumes
- [ ] "Deny" → agent receives permission denied error, handles gracefully in response

### Tool Surface Update (@code_architect)
- [ ] Add `web_fetch`, `web_crawl` to `AGENT_BEHAVIOR_CONTRACT.md §2.2` Phase 2 tool surface table
- [ ] `web_import` scoped to Librarian only — add `allowed_modes: ["web_import"]` to Librarian agent manifest (pre-register for Phase 3A)
- [ ] `web_crawl` scope: Librarian, Researcher, Ambient Agent
- [ ] `web_fetch` scope: all agents (domain allowlist enforced)

### Gesture Layer Integration (@backend)
- [ ] Register built-in gesture vocabulary for web-fetch skill in gesture library at install:
  - `"catalogue this"` / "import this site" / "bring this into my vault" → `web_import` workflow → owner: Librarian (threshold: 0.82)
  - `"read this"` / "fetch this" / "what does this say" → `web_fetch` on URL in context → owner: any (threshold: 0.80)
- [ ] URL context resolution: check last 3 messages for URL pattern; if found, confirm; if not found, ask

---

## Phase 3A: web_import (gates on vault_write)

### Gateway — web_import Pipeline (@code_architect, @backend integration)
- [ ] `importer.py`: orchestrates `web_crawl` → `web_fetch` per page → `structure_as_note` → `vault_write`
- [ ] `structure_as_note()`: frontmatter schema (below) + body template (below)
- [ ] LLM call for Summary + Key Points sections (uses standard agent routing — local model if configured)
- [ ] `knowledge_dedup` integration: check before each note write; populate Related section on matches
- [ ] Category-based folder organization when `organize_by: "category"`
- [ ] `_index.md` generation per category (wikilink table + agent pattern observations)
- [ ] Batch rate limiting: 2s between page fetches during import
- [ ] **Two confirmation gates — neither skippable:**
  - Gate 1 (scope): after crawl — shows page count, category list with checkboxes, estimated note count
  - Gate 2 (preview): 3 sample notes rendered + vault path + total count — before any writes

**Frontmatter schema:**
```yaml
---
title: "Article Title"
created: 2026-03-31
source: https://example.com/article
author: Author Name
published: 2024-01-15
domain: Sigils
tags: [low-tech, diy-infrastructure]
category: solar-energy
maturity: 30-Ideas
polly:
  origin: web-import
  agent: The Librarian
  session_key: abc123
  confidence: high
---
```

**Note body structure:**
```markdown
# Article Title

> [!source] External Article
> **Source:** [Site Name](url)
> **Author:** Author | **Published:** Date

## Summary
[Agent-generated 2–3 sentence summary]

## Key Points
[Extracted or agent-structured main points]

## Full Content
[markdownify output of article body]

## Related
[Internal wikilinks from knowledge_dedup matches]
```

**Category vault organization:**
```
30-Ideas/External/LowTechMagazine/
  solar-energy/
    article-1.md
    ...
  _index.md   ← per-category index: Dataview table + agent observations
```

### iOS — Import Preview UI (@frontend, @design_eng layouts)
- [ ] Gate 1 sheet: page count, category checkboxes, estimated note count
- [ ] Gate 2 sheet: 3 sample notes rendered (title, frontmatter fields, body excerpt), proposed vault path, total count
- [ ] Progress view during batch import: "Importing 34/187 pages..."
- [ ] Import complete: summary card ("34 notes added to 30-Ideas/External/LowTechMagazine")

### Note Template Registration (@backend)
- [ ] `external-article` note template registered with gateway template system
- [ ] Template surfaced in Settings → Vault → Note Templates; user can customize Summary/Key Points structure

---

## Security Model Summary

- Domain allowlist: no arbitrary URL access; first request prompts user; always-allow adds to gateway config
- Fetch tier policy: default (curl_cffi) always on; stealth/dynamic = explicit opt-in per domain (resource cost)
- Rate limiting: 1 req/s default; 2s batch delay for `web_import`
- Robots.txt respected by default
- All fetched content stays on gateway machine (`data_destination: local` enforced in manifest)
- LLM summary calls use standard agent routing — local model if user configured local-only
- Lockdown Mode: all three tools disabled

---

## Open Questions

Q1: **Stealth tier resource footprint** — `StealthyFetcher` requires Playwright + `patchright` install. What's the gateway disk/RAM overhead? @infra to evaluate before surfacing stealth tier in Settings.

Q2: **Librarian agent SOUL** — `web_import` is scoped to the Librarian but the Librarian is one of the 10 stub-only agents (`phase-1-agent-system` tasks). Full SOUL template must be written before `web_import` ships. @design_eng dependency.

Q3: **Summary LLM routing** — During `web_import`, the summary generation LLM call uses standard agent routing. For a batch of 50+ pages, this is 50+ LLM calls. Does this need a separate "batch mode" routing path (e.g., always use fastest/cheapest local model regardless of domain config)? @backend + @ai_expert to evaluate.

---

## Done When

**Phase 2:** `web_fetch` fetches a URL and returns cleaned markdown to an agent. Domain allowlist works. "Read this" gesture fires. `web_crawl` returns structured page list. @security_audit sign-off on allowlist enforcement + `data_destination: local` guarantee.

**Phase 3A:** "Catalogue this" gesture → full import pipeline to completion. Both confirmation gates work. Notes written with correct frontmatter, body structure, category folders. `_index.md` generated. Dedup check populates Related section. @security_audit sign-off on vault write isolation (web-fetch skill cannot write outside vault path).

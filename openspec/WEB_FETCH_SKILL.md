# WEB_FETCH_SKILL.md

Phase 2 (web_fetch + web_crawl) / Phase 3A (web_import)  
Status: 💡 Proposed  
Owners: @backend (scaffold, allowlist), @code_architect (Scrapling integration, import pipeline), @security_audit (network permissions), @frontend (permission prompt, import preview UI)  
Source URLs:  
- Proposal: https://claude.ai/public/artifacts/4e71bdf4-b147-4e0e-9da3-011cc1767b33  
- Design: https://claude.ai/public/artifacts/9fa8d324-7a5f-4789-b885-b98383297738  
- Tasks: https://claude.ai/public/artifacts/571953c2-e0d8-439b-b0c8-565219b9fe9d

**All spec actions incorporated into openspec — see cross-reference map below.**

## Summary

Web-Fetch is a first-class gateway skill with three tools: `web_fetch` (single URL → cleaned markdown), `web_crawl` (site crawl → structured page list with category extraction), `web_import` (full pipeline: crawl → structure → propose vault write). Implementation via Scrapling (Python). Domain allowlist model — no arbitrary URL access. All content stays on gateway machine (`data_destination: local`). Gesture-triggered via `GESTURE_LAYER.md` invocation gestures ("read this", "catalogue this").

## Cross-Reference Map

| Source section | Incorporated into |
|---------------|-----------------|
| Proposal: problem statement, three tools, phase split | `phase-2-web-fetch/tasks.md` |
| Design §1: skill layout, manifest | `phase-2-web-fetch/tasks.md` |
| Design §2.1: web_fetch tool, extraction pipeline, output schema | `phase-2-web-fetch/tasks.md` |
| Design §2.2: web_crawl tool, BFS crawl, category extraction | `phase-2-web-fetch/tasks.md` |
| Design §2.3: web_import pipeline, two confirmation gates | `phase-2-web-fetch/tasks.md` |
| Design §3: note frontmatter schema, body structure, category vault org | `phase-2-web-fetch/tasks.md` |
| Design §4: domain allowlist, fetch tier policy, rate limiting, data_destination | `phase-2-web-fetch/tasks.md` |
| Design §5: gesture vocabulary (catalogue this, read this), URL context resolution | `phase-2-web-fetch/tasks.md` |
| Design §6: tool surface update (AGENT_BEHAVIOR_CONTRACT.md §2.2) | `phase-2-web-fetch/tasks.md` |
| Tasks: all owner/phase assignments | `phase-2-web-fetch/tasks.md` |
| web_import gate on vault_write | `phase-3a-obsidian-write-back/tasks.md` (cross-reference added) |

## Open Questions Pending Brett's Decision / Team Resolution

Q1: Stealth tier resource footprint — @infra to evaluate Playwright/patchright gateway overhead  
Q2: Librarian SOUL — must be written before web_import ships (one of 10 stub agents)  
Q3: Batch LLM routing for web_import summary generation — @backend + @ai_expert

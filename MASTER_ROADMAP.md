# Polly Master Roadmap (redirect)

**Full roadmap and planning document** has been moved to:

- **Archive (full content):** [archive/root-docs/MASTER_ROADMAP.md](archive/root-docs/MASTER_ROADMAP.md)
- **Authoritative status & roadmap (OpenSpec):** [openspec/specs/project/status.md](openspec/specs/project/status.md), [openspec/specs/project/roadmap.md](openspec/specs/project/roadmap.md)

Use the OpenSpec project specs for current status and what to build next. Use the archived file for the complete historical roadmap and vision.

## Config Gap — Brave Search API Key (Pre-Phase 2)

**Filed:** 2026-03-24 by @backend  
**Priority:** Medium — blocks web research capability for all agents  
**Symptom:** `web_search` tool returns `missing_brave_api_key` error in all agent contexts. @researcher and @backend both confirmed blocked during skills audit session.  
**Fix:** Run `openclaw configure --section web` on the gateway machine, add `BRAVE_API_KEY`.  
**Impact if unresolved:** Any Phase 2 research work (skills audit, competitive analysis, doc lookups) requires coordinator-level manual fetch + paste. Slows all agents that depend on research inputs.  
**Owner:** Whoever has the Brave API key — this is a 2-minute fix.

# Phase 2: Figma Integration

**Status:** 📋 Planned  
**Gate:** Phase 1 iOS Foundation complete  
**Spec source:** `FIGMA_INTEGRATION.md`  
**Priority:** Low — no other features depend on this  
**Extended by:** `phase-3-figma-sync` (design token pull, component spec pull, annotation-driven actions)

## Goal

Surface Figma links in chat with rich previews. Deep-link to boards from agent messages. Establish the PAT auth + file key plumbing that Phase 3 Figma Sync shares.

## Tasks

- [ ] Figma link detection in agent messages (URL pattern match)
- [ ] Rich link preview card for Figma URLs
- [ ] Deep-link to Figma app (or web fallback)
- [ ] Agent context: agents can reference Figma boards by link in conversation
- [ ] PAT storage in OpenClaw keychain (gateway-side) — shared with Phase 3 Figma Sync
- [ ] Settings → Integrations → Figma screen stub — PAT input; Phase 3 adds webhook registration

## Done when
Figma link in chat message shows preview card and tapping opens Figma app (or web). PAT stored gateway-side ready for Phase 3 webhook registration.

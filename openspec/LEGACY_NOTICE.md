# ⚠️ NOTICE: Legacy Spec Files in this Directory

**Date added:** 2026-04-01  
**Source:** `IOS_SPEC_AUDIT.md §2.1`

## What This Directory Contains

The `openspec/specs/` subdirectories (`agent-system/`, `infrastructure/`, `ios-app/`, `knowledge/`) contain **current, valid iOS spec files** that are the canonical source of truth for those domains.

The `openspec/` top-level files (`INDEX.md`, `DOCUMENTATION_MAP.md`, `roadmap.md`, `SALVAGE_AUDIT.md`) and the `openspec/specs/*/spec.md` files were written during or reference the **Electron/Python era of Polly** (pre-iOS). They describe a different architecture (Tier 0–5, Phase 23.5 Security Hardening, Python desktop app, etc.).

## What to Use for iOS Implementation

**Current spec system (use this):**
- `SPEC_INDEX.md` at repo root — canonical file index
- Root-level `.md` spec files — all iOS specs
- `openspec/changes/phase-*/tasks.md` — all current change sets (these ARE current and valid)
- `openspec/specs/agent-system/ambient-agent.md` — ambient agent behavioral spec
- `openspec/specs/ios-app/spec.md` — iOS app canonical spec additions
- `openspec/specs/infrastructure/spec.md` — infrastructure canonical spec
- `openspec/specs/knowledge/spec.md` — knowledge system canonical spec

**Do NOT use for iOS implementation decisions:**
- `openspec/INDEX.md` — describes Electron app phases (Tier 0–5)
- `openspec/DOCUMENTATION_MAP.md` — maps Electron app components
- `openspec/roadmap.md` — Electron app roadmap with Phase 23.5
- `openspec/SALVAGE_AUDIT.md` — porting analysis FROM Electron TO iOS (historical reference only)

## If You're an Agent Reading This

Read `SPEC_INDEX.md` first, then the specific root-level spec files for the feature you're implementing. The `openspec/changes/` directories are your implementation task list. Do not consult `openspec/INDEX.md` or `openspec/roadmap.md` for current iOS product decisions.

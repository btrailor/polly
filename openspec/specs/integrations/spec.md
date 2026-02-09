# Integrations (OpenSpec)

Source of truth for third-party and system integrations. Detail: [docs/integration_status.md](../../../docs/integration_status.md).

## Working

- **GitHub:** REST API; PAT in Keychain. Sync repos, index code, search. Signed-app ready.
- **Context7:** API key in Keychain. Sync library docs; 40+ libraries; custom library support. Signed-app ready.
- **Obsidian:** Direct filesystem; index markdown (e.g. 3.5k+ chunks). Auto sync. Signed-app ready.

## Implemented, Gated (Phase 9 / Permissions)

- **Calendar:** EventKit; needs Phase 9 permission flow. See [calendar_signed_app_notes.md](../../../docs/calendar_signed_app_notes.md).
- **Reminders:** EventKit; same as calendar.
- **File System:** Full Disk Access; file ops, Finder tags, batch rules, LLM parser, 9 endpoints. See [filesystem_integration.md](../../../docs/filesystem_integration.md).

## State

- **Persistence:** `~/.polly/integrations_state.json` — connection status, last sync. Auto-restore on server start.
- **Base:** `integrations/base.py`, `state.py`; FastAPI endpoints; Electron UI.

## Reference

- [docs/integration_status.md](../../../docs/integration_status.md) — Status and architecture
- [docs/filesystem_integration.md](../../../docs/filesystem_integration.md), [docs/calendar_signed_app_notes.md](../../../docs/calendar_signed_app_notes.md)

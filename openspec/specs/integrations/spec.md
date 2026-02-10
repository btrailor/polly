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

## Planned Integrations

### Ghost CMS (Publishing)
- API integration for POSE publishing pipeline.
- Create/update posts, draft → publish status sync, tag mapping, media upload.
- Credentials in Keychain (existing secrets infrastructure).
- See [publishing spec](../publishing/spec.md).

### Automation Hooks
- **Shortcuts integration:** iOS/macOS automation triggers for captures and workflows.
- **Webhook support:** Inbound webhooks for IFTTT, Zapier, Make integration.
- **API endpoints:** Custom workflow integration for third-party tools.
- **Scheduled exports:** Automatic daily/weekly syncs to configured destinations.

### Email Intelligence (Phase 20a)
- Full IMAP/Gmail API integration for email intelligence.
- Parsing, categorization, thread summarization, noise filtering.
- Email capture/ingestion into knowledge base with domain auto-detection.
- Draft assistance with RAG context.
- See [communication spec](../communication/spec.md).

### Calendar Intelligence (Phase 20b)
- EventKit integration (requires Phase 9 macOS Permissions).
- Meeting analysis, pre-meeting briefs, action item extraction.
- Natural language calendar queries and smart scheduling.
- See [communication spec](../communication/spec.md).

### Voice Services
- Transcription service integration for voice-to-text capture.
- Speaker identification (future).
- See [mobile spec](../mobile/spec.md), [capture spec](../capture/spec.md).

### GitHub Enhancements (Phase 6)
- Incremental sync (only fetch changed repos/files).
- Parallel README fetching for performance.
- Code search within repositories.
- Commit history and message indexing.
- Issue/PR content indexing for RAG.
- See [docs/planning/phases/other/PHASE6_GITHUB_ENHANCEMENTS.md](../../../docs/planning/phases/other/PHASE6_GITHUB_ENHANCEMENTS.md).

### Additional Integration Candidates (Phase 8)
- **Slack** — Workspace message ingestion, thread summarization.
- **Browser History** — URL indexing, visited page content.
- **Apple Notes** — Import from native Notes app.
- **Photos** — Image metadata, OCR, visual context.
- **Music** — Listening patterns, playlist context (domain: Signals).
- See [docs/planning/phases/other/PHASE8_NEW_INTEGRATIONS.md](../../../docs/planning/phases/other/PHASE8_NEW_INTEGRATIONS.md).

## Integrations as Agent Execution Contexts

With Agent Swarms (Phase 24c), each integration becomes an **execution context** that agents can request access to. The Nexus brokers context access via the Capability Broker:

| Integration | Context ID | Agent Access |
|---|---|---|
| **GitHub** | `github` | Code agents: repo access, PR operations, issue management |
| **Obsidian** | `obsidian` | Scribe agents: vault read/write, wikilink resolution |
| **Ghost CMS** | `ghost_cms` | Publishing agents: post creation, media upload, scheduling |
| **Calendar** | `calendar` | Scheduling agents: event read/write, availability |
| **File System** | `filesystem` | Architect, code agents: file operations |

Agents declare required/optional contexts in their capability declarations. The Capability Broker grants scoped, time-limited access. See [agent-swarms spec](../agent-swarms/spec.md), [security spec](../security/spec.md).

## State

- **Persistence:** `~/.polly/integrations_state.json` — connection status, last sync. Auto-restore on server start.
- **Base:** `integrations/base.py`, `state.py`; FastAPI endpoints; Electron UI.

## Reference

- [docs/integration_status.md](../../../docs/integration_status.md) — Status and architecture
- [docs/filesystem_integration.md](../../../docs/filesystem_integration.md), [docs/calendar_signed_app_notes.md](../../../docs/calendar_signed_app_notes.md)
- Publishing: [publishing spec](../publishing/spec.md)
- Capture: [capture spec](../capture/spec.md)

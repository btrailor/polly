# Data Autonomy & Export (OpenSpec)

Source of truth for Polly's data export, self-hosting, offline mode, and anti-lock-in features. Detail: [docs/planning/phases/other/PHASE19_DATA_AUTONOMY.md](../../../docs/planning/phases/other/PHASE19_DATA_AUTONOMY.md).

> **Implementation Status:** 💭 Vision — no code exists for this system.
> This spec describes the target design. Implementation is planned for Tier 4 / Phase 19.
> Other specs should not design integration points against this system until implementation begins.

## Overview

Data Autonomy ensures users always own their data and can leave Polly at any time with everything intact. Export is always free. Formats are portable. Self-hosting is supported. This is a core design principle, not a feature checkbox.

**Positioning:** "Your data. Your freedom."

## Key Principles

- **Export is always free** — No paywall on your own data.
- **Portable formats first** — Markdown, JSON, CSV, GraphML. No proprietary formats.
- **Complete exports** — No hidden data. Everything exportable.
- **One-click backup** — Full system backup as a single operation.
- **Self-hosting ready** — Docker Compose for users who want full infrastructure control.

## Core Components

### 1. Knowledge Graph Export

| Format      | Use Case                                       |
| ----------- | ---------------------------------------------- |
| **JSON**    | Full fidelity, machine-readable, re-importable |
| **GraphML** | Visualization in external tools (Gephi, yEd)   |
| **CSV**     | Spreadsheet analysis, simple processing        |

Includes: entities, edges, connection metrics, authority scores, metadata.

### 2. Notes Export

| Format       | Use Case                                                                                |
| ------------ | --------------------------------------------------------------------------------------- |
| **Markdown** | Obsidian-compatible with `[[wikilinks]]` preserved. Domain folder structure maintained. |
| **JSON**     | Full metadata including maturity stage, domain tags, entity links, version history      |
| **HTML**     | Standalone readable archive with embedded styles                                        |

### 3. Configuration Backup

Export all user configuration as a portable bundle:

- Domains (domains.json)
- Patterns (patterns.json)
- Mental models configuration
- API key references (not the keys themselves — user re-enters)
- Integration settings
- Persona preferences and custom skills

### 4. Full System Backup

One-click ZIP export containing:

- All notes (Markdown)
- Knowledge graph (JSON)
- Conversation history (JSON)
- Configuration bundle
- Library metadata (book records, highlights — not the ebook files themselves)
- Canvas data (JSON)
- Capture history (JSON)
- Manifest file with version info and restore instructions

### 5. Self-Hosted Server

For users who want full infrastructure control:

- **Docker Compose** — Single `docker-compose up` for complete Polly backend (Python server, ChromaDB, SQLite).
- **Manual setup** — Bash scripts for non-Docker environments.
- **Kubernetes** — Helm chart for production-scale self-hosting (future).

Self-hosting gives users:

- Full network control (no data leaves their infrastructure).
- Custom domain and SSL.
- Integration with existing infrastructure.
- DRM mesh node on their own hardware.

### 6. Offline Mode

Polly continues working without internet:

- All local LLM inference works offline.
- Notes, search, and knowledge graph fully functional.
- Operations requiring cloud LLM queued for when connectivity returns.
- Captures and edits saved locally, synced later.
- DRM mesh still functions on local network (mDNS discovery works offline).

### 7. Import / Restore

- **Full restore** from backup ZIP.
- **Selective import** — Import only notes, only configuration, only knowledge graph.
- **Migration import** — From Obsidian vault, Notion export, Bear notes, Roam export.
- **Rollback** — Restore to previous backup if import causes issues.

## Competitive Differentiation

| Competitor         | Data Ownership                                                                                                              |
| ------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| **Notion/Roam**    | Cloud-dependent. Export exists but lossy.                                                                                   |
| **ChatGPT/Claude** | Chat history exportable but no knowledge graph or configuration.                                                            |
| **Obsidian**       | Strong (local files), but no AI state export.                                                                               |
| **Polly**          | Complete: notes + knowledge graph + AI state + configuration + conversations. All portable formats. Self-hosting supported. |

## Storage

```sql
CREATE TABLE export_jobs (
    id TEXT PRIMARY KEY,
    type TEXT,        -- 'full', 'notes', 'graph', 'config', 'conversations'
    format TEXT,      -- 'zip', 'json', 'markdown', 'csv', 'graphml'
    status TEXT,      -- 'pending', 'running', 'completed', 'failed'
    output_path TEXT,
    size_bytes INTEGER,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE backup_history (
    id TEXT PRIMARY KEY,
    backup_path TEXT,
    size_bytes INTEGER,
    manifest TEXT,    -- JSON (version, contents, checksums)
    created_at TIMESTAMP
);
```

## API

```
POST /export/start         # Start export job (type, format)
GET  /export/{id}          # Check export status
GET  /export/{id}/download # Download completed export
POST /backup/create        # Full system backup
GET  /backup/list          # List available backups
POST /backup/restore       # Restore from backup
GET  /system/offline-status # Offline mode status and queue
```

## Implementation

**Phase 19 (Tier 4)** — 5–7 days. Depends on: Phase 12 (Knowledge Graph), Phase 16 (Native Notes), Phase 18 (Onboarding).

## Reference

- [docs/planning/phases/other/PHASE19_DATA_AUTONOMY.md](../../../docs/planning/phases/other/PHASE19_DATA_AUTONOMY.md) — Full 1290-line spec
- Design: [design spec](../design/spec.md) — "Local control" and "Privacy by default" principles

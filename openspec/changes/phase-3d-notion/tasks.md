# Phase 3D: Notion Integration

**Status:** 💡 Specced  
**Gate:** Phase 2 knowledge-skill + Phase 2 integrations  
**Spec source:** `POLLY_IOS_SPEC.md` §15.2.4; `KNOWLEDGE_WRITE_PATH.md` §4.2; `KNOWLEDGE_SKILL.md` Notion section  
**Owners:** @frontend (iOS OAuth), @backend (Notion Knowledge Skill adapter)

## Goal

Notion as a knowledge source: read Notion pages/databases into Knowledge Skill index. Write-back to Notion from agent write-back. Notion adapter in knowledge pipeline.

## Tasks

### Notion OAuth + Connection
- [ ] Notion OAuth flow (in-app browser)
- [ ] Settings → Integrations → Notion: connect/disconnect, last synced
- [ ] Access token forwarded to gateway skill config

### Notion Knowledge Skill Adapter (@backend)
- [ ] Notion block-to-text conversion (heading, paragraph, bulleted-list, code, etc.)
- [ ] Property mapping: Notion properties → standard frontmatter (title, tags, created, etc.)
- [ ] Indexing: Notion pages + database rows → shared FAISS index tagged `source: "notion"`
- [ ] Incremental sync: poll Notion API for changed pages (or webhook if available)
- [ ] Offline write queue: local queue for Notion writes when gateway unavailable (deferred sync)

### Write Path
- [ ] `vault_write` extended to support Notion as target backend (when user sets Notion as vault)
- [ ] Notion-specific: create page in selected database (not file path)
- [ ] Property mapping on write: standard frontmatter → Notion properties

### Readwise Integration
- [ ] Readwise API key config in Settings → Integrations → Readwise
- [ ] Highlights fetch: poll Readwise for new highlights → standard note format → vault
- [ ] Each highlight: source title, author, highlight text, tags from Readwise
- [ ] Mapped to standard frontmatter: `polly.origin: "readwise"`, `source: <book URL>`
- [ ] Indexed in Knowledge Skill on ingest

## Done When
Notion pages searchable via Knowledge Skill. Agent write-back to Notion working. Readwise highlights importing. @security_audit review of OAuth token handling.

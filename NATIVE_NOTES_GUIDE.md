# Native Notes System - User Guide

## Overview

Polly's Native Notes System allows you to manage markdown notes directly within Polly, providing an alternative to using Obsidian. You can choose to use either Obsidian OR native notes as your primary note source.

## Features

### Core Capabilities

- **Markdown Notes**: Write notes in standard markdown format
- **Wiki-Links**: Use `[[Note Name]]` to link between notes
- **Backlinks**: Automatic tracking of which notes link to each note
- **Tags**: Organize with `#tags` (inline and frontmatter)
- **Aliases**: Multiple names for the same note
- **Domains**: Organize notes by domain (Sigils, Signals, Scrolls, etc.)
- **Auto-Sync**: Automatic RAG indexing when notes change
- **Search**: Fuzzy search across note names, aliases, and titles

### Obsidian Feature Parity

The native notes system supports most Obsidian features:

✅ Wiki-links: `[[Note Name]]`  
✅ Note embeds: `![[Note Name]]`  
✅ Heading links: `[[Note#Section]]`  
✅ Aliases in frontmatter  
✅ Tags (frontmatter and inline)  
✅ Backlinks tracking  
✅ Attachments (images, PDFs)

❌ Canvas files (`.canvas`)  
❌ Dataview queries (can be converted)  
❌ Obsidian plugins  
❌ Community themes

## Configuration

### Config File (`config.yaml`)

```yaml
notes:
  # Active source: "obsidian" or "native"
  source: "native"
  
  # Obsidian vault configuration
  obsidian:
    vault_path: "/path/to/vault"
    enabled: false
  
  # Native Polly notes configuration
  native:
    path: "~/.polly/notes"
    enabled: true
  
  # File watcher for auto-indexing
  auto_index: true
  
  # Domain validation
  domain_validation: true
```

### Key Settings

- **`source`**: Which note system to use (`"obsidian"` or `"native"`)
- **`auto_index`**: Enable automatic RAG indexing when notes change
- **`domain_validation`**: Validate that notes are in correct domain folders

## Getting Started

### 1. Creating Your First Native Note

Create a directory for your notes:

```bash
mkdir -p ~/.polly/notes
```

Create a note:

```bash
cat > ~/.polly/notes/my-first-note.md <<EOF
---
title: My First Note
tags: [getting-started, polly]
domain: scrolls
---

# My First Note

This is my first note in Polly's native notes system!

I can link to [[other-notes]] using wiki-links.

## Features

- Automatic indexing
- Backlinks tracking
- Tag organization
EOF
```

The note will be automatically indexed within 2 seconds if `auto_index: true`.

### 2. Migrating from Obsidian

If you have an existing Obsidian vault, you can migrate it to native notes:

**API Endpoint:**

```bash
POST /polly/notes/migrate
{
  "vault_path": "/path/to/vault",
  "target_path": "~/.polly/notes",  # optional
  "domain_mapping": {               # optional
    "01-Sigils": "sigils",
    "02-Signals": "signals"
  }
}
```

**What happens during migration:**

1. All markdown files are copied to `~/.polly/notes/`
2. Attachments are moved to `_Attachments/images/` and `_Attachments/files/`
3. Image links are rewritten to point to new locations
4. Frontmatter domains are updated based on folder structure
5. The active source is switched to "native"
6. RAG is re-indexed

**Before Migration:**

It's recommended to validate your vault first:

```bash
POST /polly/notes/validate
{
  "vault_path": "/path/to/vault"
}
```

This will check for:
- Canvas files (not supported)
- Dataview queries (need conversion)
- LaTeX/Mermaid (supported, but complex)

### 3. Converting Dataview Queries

If your vault uses Dataview queries, you have three conversion options:

```bash
POST /polly/notes/dataview/convert
{
  "vault_path": "/path/to/vault",
  "conversion_type": "static",  # or "search_link" or "remove"
  "dry_run": true
}
```

**Conversion Options:**

- **`static`**: Freezes query results as static markdown
- **`search_link`**: Converts to `polly://search?...` URL
- **`remove`**: Removes query with comment placeholder

## File Organization

### Directory Structure

```
~/.polly/notes/
├── sigils/              # Code & Infrastructure domain
│   ├── docker-setup.md
│   └── automation.md
├── signals/             # Audio Programming domain
│   ├── norns-script.md
│   └── supercollider.md
├── scrolls/             # Writing & Pedagogy domain
│   ├── essay-ideas.md
│   └── learning-notes.md
├── glyphs/              # Visual Design domain
│   └── design-system.md
├── grids/               # Systems Thinking domain
│   └── mental-models.md
└── _Attachments/        # Centralized attachments
    ├── images/
    │   └── diagram.png
    └── files/
        └── document.pdf
```

### Frontmatter

Notes should include frontmatter with metadata:

```markdown
---
title: Note Title
aliases: [Alternative Name, Shortcut]
tags: [tag1, tag2, nested/tag]
domain: sigils
created: 2024-01-26
modified: 2024-01-26
---

# Note Content
```

## API Reference

### Notes Management

#### Get Notes Index

```bash
GET /polly/notes/index?domain=sigils&limit=50
```

Returns all notes with metadata.

#### Search Notes

```bash
GET /polly/notes/search?q=docker&limit=20
```

Fuzzy search across note names, aliases, and titles.

#### Build Notes Index

```bash
POST /polly/notes/index/build
{
  "notes_path": "~/.polly/notes",
  "recursive": true
}
```

### Backlinks

#### Get Backlinks

```bash
GET /polly/notes/my-note/backlinks
```

Returns all notes that link to `my-note`.

#### Get Outgoing Links

```bash
GET /polly/notes/my-note/outgoing
```

Returns all notes that `my-note` links to.

#### Get Orphaned Notes

```bash
GET /polly/notes/orphaned
```

Returns notes with no incoming or outgoing links.

### Tags

#### Get All Tags

```bash
GET /polly/notes/tags
```

Returns all unique tags across all notes.

#### Get Notes by Tag

```bash
GET /polly/notes/tags/project
```

Returns all notes tagged with `#project`.

#### Get Tag Hierarchy

```bash
GET /polly/notes/tags/hierarchy
```

Returns nested tag structure for `#parent/child` tags.

#### Search Tags

```bash
GET /polly/notes/tags/search?q=pro&limit=20
```

### Source Management

#### Get Current Source

```bash
GET /polly/notes/source
```

Returns active source (`"obsidian"` or `"native"`).

#### Switch Source

```bash
POST /polly/notes/source/switch
{
  "source": "native"
}
```

Switches between Obsidian and native notes.

### Sync Manager

#### Start Auto-Sync

```bash
POST /polly/notes/sync/start
{
  "notes_path": "~/.polly/notes",
  "initial_build": true
}
```

#### Stop Auto-Sync

```bash
POST /polly/notes/sync/stop
```

#### Get Sync Status

```bash
GET /polly/notes/sync/status
```

## How Auto-Sync Works

When `auto_index: true`, Polly watches your notes directory for changes:

1. **File Added**: Note is indexed in all systems (RAG, notes index, backlinks, tags)
2. **File Modified**: All indices are updated, RAG is re-indexed
3. **File Deleted**: Note is removed from all indices

**Debouncing:** Changes are debounced with a 2-second delay to avoid rapid re-indexing.

**What gets synced:**
- Notes index (metadata, aliases, domains, titles)
- Backlinks index (wiki-links between notes)
- Tags index (frontmatter and inline tags)
- RAG (semantic search embeddings)

## Best Practices

### 1. Use Frontmatter

Always include frontmatter with at least a title:

```markdown
---
title: Descriptive Title
domain: sigils
tags: [relevant, tags]
---
```

### 2. Organize by Domain

Put notes in domain folders to enable domain-aware features:

```
~/.polly/notes/
├── sigils/      # Code notes
├── signals/     # Audio notes
├── scrolls/     # Writing notes
└── ...
```

### 3. Use Wiki-Links

Link related notes with wiki-links:

```markdown
This project uses [[Docker Setup]] and [[Kubernetes Config]].
```

### 4. Tag Consistently

Use consistent tags for better organization:

```markdown
#project         # Top-level
#project/active  # Nested
#project/archived
```

### 5. Keep Attachments Centralized

Put all images and files in `_Attachments/`:

```markdown
![Diagram](../_Attachments/images/diagram.png)
[Document](../_Attachments/files/doc.pdf)
```

## Troubleshooting

### Notes Not Appearing in Search

1. Check if auto-sync is running:
   ```bash
   GET /polly/notes/sync/status
   ```

2. Manually rebuild indices:
   ```bash
   POST /polly/notes/index/build
   POST /polly/notes/backlinks/build
   POST /polly/notes/tags/build
   ```

### Backlinks Not Showing

1. Ensure wiki-links use the exact note name (without `.md`)
2. Rebuild backlinks index:
   ```bash
   POST /polly/notes/backlinks/build
   ```

### Sync Manager Not Starting

1. Check configuration:
   ```yaml
   notes:
     auto_index: true
     source: "native"
   ```

2. Check logs for errors:
   ```bash
   tail -f ~/.polly/apollo.log
   ```

3. Manually start sync:
   ```bash
   POST /polly/notes/sync/start
   ```

### Migration Failed

1. Validate vault first:
   ```bash
   POST /polly/notes/validate
   ```

2. Convert Dataview queries:
   ```bash
   POST /polly/notes/dataview/convert
   ```

3. Try migration again with detailed error logs

## Performance

### Benchmarks (84-note vault)

- **Notes Index Build:** 47ms
- **Backlinks Scan:** 45ms
- **Tags Extraction:** 113ms
- **File Watcher Debounce:** 2 seconds
- **Memory Usage:** ~50MB for indices

### Scalability

The system is designed to handle 1000+ notes efficiently:

- In-memory indices for fast lookups
- Incremental updates (only changed files)
- Debounced file watching
- Background RAG indexing

## Advanced Usage

### Custom Domain Folders

You can organize notes in custom folders and map them to domains:

```yaml
notes:
  domain_mapping:
    "Projects": "sigils"
    "Music": "signals"
    "Writing": "scrolls"
```

### Programmatic Access

Access notes programmatically via Python:

```python
from core.notes_index import get_notes_index
from core.backlinks import get_backlinks_index
from core.tags_index import get_tags_index

# Get notes index
notes_idx = get_notes_index()

# Search notes
results = notes_idx.search_notes("docker", limit=10)

# Get backlinks
backlinks_idx = get_backlinks_index(notes_idx)
backlinks = backlinks_idx.get_backlinks("my-note")

# Get tags
tags_idx = get_tags_index(notes_idx)
all_tags = tags_idx.get_all_tags()
```

## Next Steps

- **Frontend UI**: Monaco editor integration (coming soon)
- **Graph View**: Visual note relationships
- **Quick Switcher**: Cmd+O to jump to notes
- **Live Preview**: Real-time wiki-link rendering
- **Mobile Access**: Notes via Polly mobile app

## Support

For issues or questions:

1. Check logs: `~/.polly/apollo.log`
2. Check sync status: `GET /polly/notes/sync/status`
3. Rebuild indices: `POST /polly/notes/*/build`
4. File an issue on GitHub

---

**Version:** Phase 16 Complete  
**Last Updated:** January 26, 2024

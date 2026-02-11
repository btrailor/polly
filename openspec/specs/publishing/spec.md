# Publishing Pipeline — POSE (OpenSpec)

Source of truth for Polly's capture-to-publish workflow. POSE (Publish, Organize, Synthesize, Export) transforms knowledge into published output across multiple platforms.

> **Implementation Status:** 💭 Vision — no code exists for this system.
> This spec describes the target design. Implementation is planned for Tier 3 / Phases 34–34a.
> Other specs should not design integration points against this system until implementation begins.

## Overview

The publishing pipeline takes knowledge from Polly's vault — notes, captures, canvas content — and prepares it for publication. It supports multi-platform distribution with domain-specific formatting, scheduling, and analytics.

---

## Publication Workflow

```
Draft → Review → Schedule → Publish → Monitor
```

| Stage | Description |
|---|---|
| **Draft** | Content prepared from notes/captures. Domain-specific formatting templates. |
| **Review** | Preview across target platforms. Edit, refine (Scribe-assisted). |
| **Schedule** | Set publication date/time. Batch scheduling for series/campaigns. |
| **Publish** | Push to configured platforms. Automatic frontmatter and metadata. |
| **Monitor** | Syndication status tracking. Analytics post-publication. |

## Content Preparation

- **Convert captures/notes to publication-ready drafts.** Content at maturity stage 20-Active or higher eligible.
- **Domain-specific formatting templates.** Different output formats per domain (technical blog post, audio programming tutorial, theoretical essay, etc.).
- **Automatic frontmatter generation.** Title, date, tags, domain, excerpt — generated from note metadata and entity graph.
- **Feature image generation.** Designer persona's Generate mode produces feature images (1200x630 OpenGraph standard) via p5.js-svg pipeline. Compositions constrained by active theme and project design system palette. Agent Swarms workflow: Scribe(Publish) → Designer(Generate) → Scribe(Publish). See [personas spec — Designer](../personas/spec.md).
- **Image optimization and hosting.** Resize, compress, upload to configured CDN or Ghost media library.
- **Link checking and metadata enrichment.** Validate outbound links, enrich with OpenGraph metadata.

## Export Destinations

### Primary: Ghost CMS
- API integration for creating/updating posts.
- Frontmatter mapping to Ghost post metadata.
- Draft → published status sync.
- Tag mapping from Polly domains/tags to Ghost tags.

### Social Distribution
- **Thread generation:** Convert long-form content into Twitter/Mastodon thread format.
- **Summary generation:** Short-form excerpts for social sharing.

### Newsletter
- **Email digest compilation:** Aggregate recent publications by domain or timeframe.
- **Template formatting:** Newsletter-optimized layout.

### RSS / Syndication
- **Feed generation:** RSS/Atom feeds from published content.
- **Syndication management:** Track where content has been distributed.

### Static Site
- **Archive generation:** Static HTML export of published content.
- **Domain-organized navigation.**

## Scribe Publishing Mode

The Scribe persona gains a publishing-specific mode:
- Transform rough notes into polished drafts.
- Apply domain-specific style and formatting.
- Generate summaries and excerpts.
- Suggest related published content for cross-linking.

## Maturity Integration

Publishing connects to the shared maturity lifecycle:
- **30-Ideas:** Not eligible for publishing.
- **20-Active:** Can be drafted and reviewed.
- **10-Archive:** Published or deliberately unpublished.
- Maturity stage advances through the publication workflow.

## Implementation Phases

### Publishing Foundation (2–3 weeks)
- Publication data model (SQLite: drafts, publications, destinations)
- Draft creation from notes/captures
- Ghost CMS API integration
- Basic publish workflow (Draft → Publish)

### Multi-Platform (2–3 weeks)
- Social thread generation
- Newsletter compilation
- RSS/Atom feed generation
- Frontmatter and metadata automation

### Polish (2 weeks)
- Scheduling and batch operations
- Preview across platforms
- Syndication status monitoring
- Scribe publishing mode

## Relationship to Existing Systems

| System | Integration |
|---|---|
| **Notes** | Notes are the primary source material for publications |
| **Captures** | Captures mature into publishable content |
| **Maturity lifecycle** | Publication eligibility tied to maturity stage |
| **Scribe** | Publishing mode for content refinement |
| **Domains** | Domain-specific formatting and templates |
| **Obsidian** | Published status synced as frontmatter metadata |
| **Knowledge graph** | Cross-linking between related publications |
| **Canvas** | Canvas business model informs publishing strategy |
| **Designer** | Feature image generation via p5.js for Ghost CMS posts. Theme-constrained compositions. |
| **Design system** | Feature images use project palette and tokens from `_design/system.yml` |

## Storage

- `~/.polly/knowledge.db` → `publications` table (id, note_source, destination, status, published_at, metadata)
- `~/.polly/knowledge.db` → `drafts` table (id, content, source_note, template, status)
- Ghost CMS credentials in Keychain (existing secrets infrastructure)

## Reference

- Scribe persona: [personas spec](../personas/spec.md)
- Notes system: [notes spec](../notes/spec.md)
- Capture system: [capture spec](../capture/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)

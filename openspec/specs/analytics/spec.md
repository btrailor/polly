# Analytics & Insights (OpenSpec)

Source of truth for Polly's analytics, metrics, and reflective features.

> **Implementation Status:** 💭 Vision — no code exists for this system.
> This spec describes the target design. Implementation is planned for Tier 4 / Phases 35–35a.
> Other specs should not design integration points against this system until implementation begins.

## Overview

Analytics in Polly serve reflection, not productivity tracking. The goal is helping users understand their knowledge patterns, identify neglected areas, and surface historical context — not gamifying output.

---

## Capture & Knowledge Patterns

- **Domain activity over time:** Which domains are most active, trends over weeks/months.
- **Capture frequency heatmap:** When captures happen (time of day, day of week).
- **Input method preferences:** Voice vs. text vs. image vs. URL breakdown.
- **Maturity stage flow:** How captures move through 30-Ideas → 20-Active → 10-Archive. Bottleneck detection (ideas that stall).
- **Tag usage trends:** Most/least used tags, co-occurrence patterns, dormant tags.

## Knowledge Quality Metrics

- **Connection density:** Average connections per note. Trend over time.
- **Authority distribution:** How many hub notes vs. isolated notes.
- **Garden health score:** Percentage of notes with 2+ connections. Orphan count.
- **Dedup interventions:** How often similarity warnings fire, user choices (append/link/create).
- **Entity graph growth:** New entities per week, new connections per week.

## Reflective Features

- **"On this day":** Surface historical captures from the same date in previous years.
- **Abandoned ideas:** Ideas at 30-Ideas stage for >N weeks with no connections. Resurface for reconsideration.
- **Completed project retrospectives:** When a canvas or project reaches 10-Archive, prompt for reflection.
- **Domain balance:** Recommendations when one domain is neglected relative to others.
- **Workflow friction identification:** Detect patterns where captures don't progress or review workflows are skipped.

## Publishing Metrics

- **Publishing frequency by domain.**
- **Draft-to-publish conversion rate.**
- **Syndication status across platforms.**
- **Content performance (if analytics from Ghost CMS are available).**

## Productivity Metrics (Optional, Opt-In)

- **Captures per day/week/month.**
- **Idea-to-active conversion rate.**
- **Time in each maturity stage.**
- **Cross-domain collaboration frequency:** How often work in one domain references another.

## Data Sources

All analytics derive from existing data stores — no new tracking infrastructure:

| Metric Source | Storage |
|---|---|
| Capture metadata | `~/.polly/knowledge.db` captures table |
| Knowledge graph | `~/.polly/knowledge.db` entities/edges tables |
| Maturity transitions | Note frontmatter + SQLite index |
| Routing decisions | `~/.polly/usage.db` (existing autonomy metrics) |
| Publishing status | `~/.polly/knowledge.db` publications table |
| DRM task history | `~/.polly/drm/` task logs |

## UI

### Analytics Page
New page in ribbon navigation (or section within Home/Dashboard):
- **Domain distribution:** Pie/bar chart of captures and notes by domain.
- **Maturity flow:** Sankey or flow diagram showing stage transitions.
- **Capture frequency:** Heatmap calendar view.
- **Knowledge health:** Garden health score, connection density, authority distribution.
- **Timeline:** Chronological exploration of captures and notes.

### Learning Page: Review Tab
Learning analytics (progress, mastery, spaced repetition, knowledge gaps) appear in the Learning page's collapsible **Review tab**, not center stage. The center area is reserved for the active learning surface (conversation with Professor, curriculum map, practice space). Analytics serve reflection, not tracking — summoned intentionally, not imposed by default. See [teaching spec](../teaching/spec.md).

### Visualization Features
- Domain distribution chart
- Maturity stage flow diagram
- Capture frequency heatmap
- Project progress indicators
- Cross-domain connection graph

## Implementation Phases

### Analytics Foundation (1–2 weeks)
- Query layer over existing SQLite data
- Basic analytics API endpoints
- Domain distribution and capture frequency

### Knowledge Quality Dashboard (1–2 weeks)
- Connection density and authority metrics
- Garden health score
- Entity graph growth tracking

### Reflective Features (1–2 weeks)
- "On this day" surfacing
- Abandoned ideas detection
- Domain balance recommendations

### Visualization (2–3 weeks)
- Analytics page UI with charts
- Heatmap, flow diagrams
- Cross-domain connection graph

## Relationship to Existing Systems

| System | Integration |
|---|---|
| **Autonomy metrics** | Existing `usage.db` provides routing and cost data |
| **Knowledge graph** | Connection metrics, authority scores feed analytics |
| **Capture** | Capture metadata is primary analytics source |
| **Maturity lifecycle** | Stage transitions tracked for flow analysis |
| **Domains** | Per-domain breakdowns for all metrics |
| **Publishing** | Publication frequency and conversion metrics |

## Reference

- Existing autonomy metrics: `core/autonomy_metrics.py`
- Knowledge graph: [knowledge-graph spec](../knowledge-graph/spec.md)
- Capture system: [capture spec](../capture/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)

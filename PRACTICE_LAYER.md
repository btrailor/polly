# PRACTICE_LAYER.md
*Phase 3 — Practice Mirror*
*Status: Planned*
*Owners: @backend (data model, Knowledge Skill integration), @frontend (Practice view UI)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A practice mirror that runs alongside Plans (§23) — tracking creative and intellectual practices as ongoing activities, not projects to be completed.

The key philosophical move: **completion-state is the wrong model for creative work.** Plans (§23) tracks what Brett intends to finish. The Practice Layer tracks what Brett does over and over. Practices are infinite games — they have frequency, depth, and cross-domain connection density, not deadlines and done-states.

The Practice Layer derives almost entirely from data that already exists in the Knowledge Skill's knowledge graph. No new user input is required. Brett doesn't add practices to a list or check in manually. The system observes the vault and surfaces patterns.

---

## 2. What a Practice Is

A practice is a domain of ongoing creative or intellectual engagement represented in the vault. Examples from Brett's context: Glyphs (type design), SuperCollider (synthesis programming), norns/monome (live performance), systems thinking, writing.

> **NOTE:** Domain names used as examples throughout this document (Glyphs, Sigils, Signals, Scrolls, Grids, etc.) reflect the original design author's personal domain taxonomy stored in `UserDomain[]` (MMKV key `polly.domains`). The Practice Layer is agnostic to domain names — it operates on whatever `UserDomain` records the user has configured. No behavior is keyed to specific domain name strings.

Practices are identified from the vault — not declared by the user. The Practice Layer reads the domain taxonomy that Brett has implicitly built through tagging and wikilinks. Domains emerge from the vault structure; they are not imposed externally.

**Practice ≠ Skill.** A skill can be learned and mastered. A practice is something you return to. You don't "finish" SuperCollider. You engage with it over years, with varying depth and frequency. The Practice Layer tracks that engagement.

---

## 3. Data Model

All data is derived from the Knowledge Skill's existing wikilink graph and file timestamps. No new infrastructure required beyond a lightweight metadata pass over existing index data.

```json
{
  "domain": "SuperCollider",
  "last_engaged": "2026-03-18",
  "engagement_frequency": {
    "window": "90d",
    "histogram": [3, 2, 5, 4, 1, 0, 2, 3, 4, 6, 2, 3],
    "unit": "files_modified_per_week"
  },
  "depth_signal": {
    "avg_note_word_count": 420,
    "avg_inbound_link_count": 3.2,
    "note_count": 47
  },
  "cross_domain_links": {
    "systems_thinking": 12,
    "glyphs": 4,
    "pedagogy": 7
  },
  "dormancy_threshold_days": 42
}
```

### 3.1 Field Definitions

| Field | Source | Description |
|-------|--------|-------------|
| `last_engaged` | File timestamp | Most recent modification date of any file in domain |
| `engagement_frequency` | File timestamps | 90-day histogram of files modified per week |
| `depth_signal` | File metadata | Avg word count + inbound link density + total note count |
| `cross_domain_links` | Wikilink graph | Count of wikilinks from this domain's files to other domains |
| `dormancy_threshold_days` | User-configurable | Days of inactivity before dormancy alert fires; default 42 |

### 3.2 Domain Taxonomy

Domains are derived from Brett's vault structure — the tags and wikilink clusters he has built. The Practice Layer reads this taxonomy; it does not impose one. If Brett's vault has a dense cluster around `#synthesis` and `[[SuperCollider]]`, that's a domain. The system discovers it; Brett names it (or doesn't).

This is the Freirean principle applied to knowledge categorization: categories emerge from Brett's own knowledge, not from an external taxonomy.

---

## 4. Surfaces and Views

### 4.1 Dormancy Alert

When a practice crosses the `dormancy_threshold_days` since `last_engaged`, the system surfaces a quiet alert:

> "Glyphs has gone quiet — 6 weeks. Was that intentional?"

The question is genuine, not rhetorical. Dormancy may be intentional (project complete, life phase, deliberate rest). The alert doesn't assume it's a problem; it asks.

Alert surface: §4.2 Today View "Polly noticed…" card, or in-chat via Ambient Agent.

### 4.2 Practice View

A dedicated view (separate from Plans) showing the practice landscape:

- Each domain as a tile with: name, last engaged, 90-day activity sparkline, depth indicator
- Sorted by: recency (default), frequency, depth, or cross-domain richness
- Dormant practices visually distinguished (faded, not hidden)

### 4.3 Cross-Pollination View

Which domain pairings are currently active, historically generative, or siloed. Derived from `cross_domain_links`:

- **Active pairings:** both domains engaged in last 30 days + high link density
- **Siloed domains:** low cross-domain link count relative to note volume — domains that haven't talked to each other
- **Historically generative:** pairings that, when both were active simultaneously, correlated with high note production (Archivist data, Phase 3+)

The cross-pollination view makes the invisible visible: Brett may not notice that his SuperCollider and pedagogy notes have been talking to each other. The view surfaces the conversation.

---

## 5. Integration Points

| System | Integration | Phase |
|--------|-------------|-------|
| Knowledge Skill | Domain taxonomy, file timestamps, wikilink graph — all read from existing index | 3 |
| Practice Layer → Oral History | Practice rhythm data feeds annual synthesis pass | 3 |
| Practice Layer → ANTI_PRODUCTIVITY.md | Dormancy data powers the conditional fourth question | 3 |
| Practice Layer → CONVERSATION_ARCHITECTURE.md | Metacognitive Dashboard personalizes topologies against practice patterns | 3 |
| §4.2 Today View | Dormancy alerts surface as "Polly noticed…" cards | 3 |
| Ambient Agent | Alternative surface for dormancy alerts and cross-pollination observations | 3 |

---

## 6. What This Is Not

- **Not a productivity tracker.** There are no goals, no streaks, no completion percentages. The Practice Layer does not gamify creative work.
- **Not a journal.** Brett doesn't write entries. The system reads what's already there.
- **Not a Plans replacement.** Plans tracks finite work with completion states. Practice Layer tracks infinite work with engagement patterns. Both exist; neither replaces the other.
- **Not prescriptive.** Dormancy alerts ask "was that intentional?" — they don't tell Brett to get back to work. The system surfaces; Brett decides.

---

## 7. Implementation Notes

### 7.1 Metadata Pass

The Practice Layer requires a lightweight metadata pass over the existing Knowledge Skill index — extracting timestamps, wikilink counts, and word counts per domain. This is an async background operation, not part of the real-time retrieval path. It runs on the same dirty-flag schedule as the main index.

### 7.2 Domain Identification

Initial domain identification: cluster analysis on wikilink graph using the existing `IndexHNSWFlat` structure. Domains are dense clusters with high internal link density. The user reviews and names them on first setup; thereafter the taxonomy is maintained automatically as the vault evolves.

### 7.3 Dormancy Threshold

Default: 42 days. User-configurable per domain. Some practices (annual projects, seasonal work) warrant longer thresholds. The Practice Layer respects this.

---

## 8. Open Questions

None blocking. One deferred decision:

**Q1 (Phase 3+):** Cross-pollination generativity scoring — correlating active domain pairings with output volume requires Archivist post-mortem data. This is Phase 3+ and does not block Phase 3 MVP of the Practice Layer.

---

## 9. Dependencies

- Knowledge Skill live with wikilink graph layer
- User-defined domain taxonomy in vault (implicit — from vault structure, not declared)
- §4.2 Today View implemented (for dormancy alert surface)
- ANTI_PRODUCTIVITY.md: dormancy data dependency noted
- ORAL_HISTORY.md: practice rhythm data input to annual synthesis

---

*Cross-references: KNOWLEDGE_SKILL.md, ORAL_HISTORY.md, COGNITIVE_ARTIFACT.md, ANTI_PRODUCTIVITY.md, CONVERSATION_ARCHITECTURE.md, POLLY_IOS_SPEC.md §4.2, §23*

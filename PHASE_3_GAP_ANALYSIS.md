# PHASE_3_GAP_ANALYSIS.md

Comprehensive Audit: Phase 3 Spec Coverage, Scope Problem, Missing Changes  
Status: Resolved — decisions locked 2026-03-25  
Source: Artifact de326cff  
Cross-references: `POLLY_IOS_SPEC.md` §13, §4.3–4.5, §15.2.4, §15.3.1, §19, §22.7–22.9; all Phase 3 task files; `KNOWLEDGE_SKILL.md`; `KNOWLEDGE_WRITE_PATH.md`; `AGENT_BEHAVIOR_CONTRACT.md`; `SENSIBILITY_SYSTEM_SPEC.md`; `SWARM_COORDINATION_SPEC.md`; `POLLY_AGENT_TEMPLATES.md`

---

## 1. The Core Problem

Phase 3 had two definitions with zero overlap:

| Source | What it says Phase 3 is |
|--------|------------------------|
| `POLLY_IOS_SPEC.md §13` | Shortcuts, Obsidian write-back, daily notes, Notion, Readwise, MoltbookView, UsageStatsView |
| `openspec/ROADMAP.md` | 5 changes: Cognitive Features, Creative Systems, RAG Routing, Sensibility Picker, Structured Conversations |

§13 Phase 3 = "full Aight parity + Obsidian depth." OpenSpec Phase 3 = "the reflexive layer — Polly as extension of the self." These are different projects that happened to share a number. Zero features in §13 appear in any openspec task file, and vice versa.

The total feature count when combining all sources: **~33 distinct Phase 3 features**. That is not a phase — it's several phases wearing a trenchcoat.

---

## 2. Resolution: 3A/3B/3C/3D Split

**Phase 3A — Knowledge Extension + User-Facing** (ships first, high immediate value)  
**Phase 3B — Cognitive Layer** (deep reflexive features, heavy infrastructure)  
**Phase 3C — Creative + Structural Layer** (engagement structure, conversation topology)  
**Phase 3D — Extended Features** (remaining §13 features, heaviest dependency chains)

This split is reflected in the ROADMAP update (see §8).

---

## 3. Archivist Agent Template — Status

**Claim in audit: Archivist template doesn't exist.**  
**Actual state: Complete.** `POLLY_AGENT_TEMPLATES.md` lines 1779–1815 contains a full Archivist SOUL with soul text, Prosodic Sensitivity, one-question frame, and work character.

The audit was wrong on this point. Oral History and Cognitive Artifact are **not blocked** on the Archivist template.

---

## 4. Phase Boundary Conflicts — Resolutions

### 4.1 Conversation History Tool (Phase 2/3)

Already resolved in `PHASE_2_GAP_ANALYSIS.md §2.1`:
- Phase 2: memory file watcher + FAISS indexing (foundation)
- Phase 3: `knowledge_conversation_history` query tool

### 4.2 Structural Rules (Phase 2/3)

Already resolved in `PHASE_2_GAP_ANALYSIS.md §2.2`:
- Phase 2: aesthetic injection only
- Phase 3: structural rules → `phase-3-creative-systems`

### 4.3 Swarm Templates (Phase 2/3)

| Source | Says |
|--------|------|
| `phase-2-swarm-coordination/tasks.md` | Includes 3 swarm templates |
| `POLLY_IOS_SPEC.md §22.7` | "Swarm Templates (Phase 3)" for custom templates |

**Resolution (locked 2026-03-25):**
- Phase 2: Ships 3 **built-in** templates (hardcoded: research, dev sprint, creative session)
- Phase 3: Custom template creation (user-defined), template library, template sharing
- Task file updated.

---

## 5. Task File Issues — Fixes Applied

### 5.1 phase-3-cognitive-features/tasks.md

| Issue | Fix |
|-------|-----|
| Oral History underspecced | Task group expanded: voice transcript corpus, Archivist synthesis pass, Cognitive Artifact integration, synthesis format per `ORAL_HISTORY.md` |
| Tree of Thoughts has no UI spec | Added: requires design spec before implementation; flagged @design_eng; collapsible panel approach (not in-bubble tree) |
| EIS pattern library bootstrap underspecced | Added: transformation step — `CL4R1T4S_RESEARCH.md` → structured `pattern_library.json` before EIS can query |
| Practice Layer missing UI tasks | Added: Practice View iOS component, dormancy alert card, cross-pollination view |

### 5.2 phase-3-creative-systems/tasks.md

| Issue | Fix |
|-------|-----|
| Chorus Mode topology field dependency not verified | Added: Phase 1 dependency check — `topology` field on message objects must be confirmed shipped before Chorus begins |
| Creative Code Skill is a stub | Task group expanded from 3 tasks to reflect `CREATIVE_CODE_SKILL.md` scope |
| Conversation Architecture missing Metacognitive Dashboard dependency | Dependency added to task file header |

### 5.3 phase-3-rag-routing/tasks.md

| Issue | Fix |
|-------|-----|
| Feedback loop cold-start strategy missing | Added: cold-start defaults; minimum 50 data points per query type before tier adjustment |
| MMKV → SQLite budget migration | Added: migration script task; run automatically on first Phase 3 launch |

### 5.4 phase-3-swarm-structured/tasks.md

| Issue | Fix |
|-------|-----|
| Coordinator pre-dispatch latency UX | Added: "coordinator is thinking..." indicator; graceful 2s timeout with fallback to heuristic |
| GroupPhaseState multi-device limitation | Added: documented known limitation; @backend Phase 4+ enhancement |

---

## 6. Missing Changes — Created

Seven new change directories:

| # | Change | Phase | Priority | Depends On |
|---|--------|-------|---------|-----------|
| 1 | `phase-3a-usage-stats` | 3A | P2 | Phase 2 model-routing (usage data) |
| 2 | `phase-3a-obsidian-write-back` | 3A | P1 | Phase 2 vault browser |
| 3 | `phase-3d-shortcuts` | 3D | P2 | Phase 1 complete |
| 4 | `phase-3d-moltbook` | 3D | P2 | Phase 2 Moltbook feed |
| 5 | `phase-3d-notion` | 3D | P2 | Phase 2 knowledge-skill |
| 6 | `phase-3d-oral-history` | 3D | P1 | Voice Phase 2 + Archivist + cognitive corpus |
| 7 | `phase-3d-cognitive-artifact-full` | 3D | P2 | Phase 3B cognitive features |

---

## 7. @backend Phase 3 Gateway Work

Added to `phase-2-gateway-changes/tasks.md` as Wave 4 (Phase 3 unlocks):

| # | Task | Blocks |
|---|------|--------|
| 15 | `knowledge_analogy` tool registration | Structural Analogy |
| 16 | `knowledge_dream` tool registration | Dream Logic |
| 17 | `knowledge_conversation_history` tool registration | Metacognitive Dashboard, EIS, Temporal Intelligence, Oral History |
| 18 | Index hook hot-reload support | All hook-registering cognitive features |
| 19 | `vault_write` tool implementation | Obsidian write-back |
| 20 | Notion adapter (Knowledge Skill) | Notion integration |
| 21 | Creative Code Skill sandbox execution | Creative Code Skill |

Phase.transition signal + Chorus parallel dispatch: **no gateway changes needed** — client-side only using existing fan-out with `activationMode: "always"`. Prosodic fields: already specified in Phase 1 agent manifest schema.

---

## 8. ROADMAP Update

Existing 5 Phase 3 changes renamed and split. 7 new changes added. Total Phase 3: 13 changes.

See `openspec/ROADMAP.md` — Phase 3 now grouped as 3A/3B/3C/3D.

---

## 9. Phase 3 Test Fixtures — Created as Tasks

Added to `phase-1-testing-infrastructure/tasks.md` as "Phase 3 Test Fixture Preparation" task group — start building during Phase 2 so they're ready when Phase 3 begins:

| Fixture | Purpose | Effort |
|---------|---------|--------|
| 30-day synthetic conversation history | Metacognitive Dashboard, Temporal Intelligence, EIS | High |
| Evolving position corpus | Temporal Intelligence drift detection | Medium |
| Rhetorical pattern test set (20+ examples) | EIS pattern matching | Medium |
| Structural pattern test vault (50 notes) | Structural Analogy | Medium |
| Voice transcript corpus (10 sessions) | Oral History | Low |

---

## 10. Internal Phase 3 Build Order

Within cognitive features, strict dependency ordering:

```
1. Practice Layer + Dream Logic      (lightest: FAISS graph + distance-band only)
2. Structural Analogy                (needs structural-pattern-tagger hook + taxonomy)
3. EIS                               (needs rhetorical-structure-extractor hook + pattern library)
4. Metacognitive Dashboard           (needs conversation history tool — Phase 2 corpus needed)
5. Temporal Intelligence             (needs classifier filter + separate position index)
6. Tree of Thoughts                  (needs Metacognitive Dashboard for complexity logging)
7. Oral History                      (needs voice transcripts + Archivist synthesis + corpus)
```

Practice Layer and Dream Logic first — they validate Knowledge Skill infrastructure in production before the heavy cognitive features depend on it.

---

## 11. Critical Path

```
Phase 2 Knowledge Skill
  → Phase 3A (Practice Layer, Dream Logic, write-back, sensibility picker, RAG routing, usage stats)
  → Phase 3B (EIS, Metacognitive Dashboard, Temporal Intelligence, Structural Analogy, Tree of Thoughts)
  → Phase 3C (Creative Constraint Engine, Conversation Architecture, Chorus, Somatic full)
  → Phase 3D (Oral History, full Cognitive Artifact, Shortcuts, Moltbook, Notion)
```

Phase 3D features are largely independent — Shortcuts, Moltbook, and Notion can ship in any order relative to 3B/3C.

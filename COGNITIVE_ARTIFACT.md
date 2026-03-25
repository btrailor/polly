# COGNITIVE_ARTIFACT.md
*Phase 3 — Polly as Cognitive Artifact*
*Status: Planned (Phase 1 backend hook required — see §6)*
*Owners: @backend (export format, manifest.json schema), @code_architect (layer specifications)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A reframing of §4.8 data export. Not a compliance checkbox — a cognitive artifact.

A decade of Polly use builds the richest machine-readable representation of a single human's intellectual life ever created: cross-referenced, temporally-indexed, domain-tagged, epistemologically-annotated. The export isn't a backup. It's an artifact — something that has meaning beyond its function as data, that can be handed to another person or another system and transmit not just information but intellectual structure.

This document specifies what that artifact contains, how it's structured, and what it's for.

---

## 2. Three Use Cases

### 2.1 Intellectual Estate Planning

Brett can bequeath his corpus to an archive, a university library, a collaborator, or his own future. The export is designed to be navigable by a person who never met him — the Archivist-written `README.md` is the entry point, the `oral_history/annual/` directory is the narrative spine, and the `graph/` directory is the structural map.

This is only possible because the corpus lives on Brett's hardware. Ownership is literal. There is no platform that needs to agree to release the data. It is already his.

### 2.2 Pedagogical Transmission

A teacher or practitioner can hand their cognitive artifact to a student or collaborator the way Robert Blasser hands an instrument — not as instructions, but as a structured way of knowing. The student doesn't just get the conclusions; they get the reasoning patterns, the analogical structures, the rhetorical vulnerabilities, the practice rhythms, the drift maps. They get the shape of a mind.

This is the Blasser instrument-as-knowledge transmission model applied to intellectual life. The export is the instrument.

### 2.3 Polly-to-Polly Import

A new Polly instance can ingest a cognitive artifact and begin with structural orientation rather than from zero. The new instance receives:
- Structural analogy patterns (so `knowledge_analogy` has a library to work from on day one)
- Temporal Intelligence drift maps (so the new instance understands where positions have moved)
- Practice Layer domain taxonomy (so practices are already identified)
- The Archivist's README (so the instance has narrative context)

The new instance doesn't inherit memory — it inherits structure. That distinction matters: memory would be noise; structure is orientation.

---

## 3. Export Package Structure

```
polly-export-[date]/
  manifest.json           ← Phase 1 deliverable — schema versioned from day one
  README.md               ← Written by Archivist; navigation document for human reader
  memory/                 ← Daily memory files (populated Phase 1)
  oral_history/
    post-mortems/         ← Project post-mortems (populated as projects complete)
    annual/               ← Annual syntheses (populated annually)
    corpus/               ← Indexed transcript references (not raw audio)
  drift/                  ← Temporal Intelligence position maps (Phase 3)
  patterns/               ← Structural Analogy pattern library (Phase 3)
  practices/              ← Practice Layer domain data (Phase 3)
  reasoning/              ← Metacognitive Dashboard history (Phase 3)
  graph/                  ← Cross-domain connection maps (Phase 3)
```

---

## 4. manifest.json Schema

**This is a Phase 1 @backend deliverable.** The schema must be versioned from day one. Retrofitting navigable structure onto flat JSON at Phase 3 is painful — the hooks must exist from the start.

```json
{
  "polly_export_version": "1.0",
  "created_at": "2026-03-25T17:00:00Z",
  "owner": "Brett Gershon",
  "gateway_version": "0.9.1",
  "layers": {
    "memory": {
      "present": true,
      "schema_version": "1.0",
      "entry_count": 47
    },
    "oral_history": {
      "present": true,
      "schema_version": "1.0",
      "post_mortem_count": 3,
      "annual_count": 0
    },
    "drift": {
      "present": false,
      "schema_version": null
    },
    "patterns": {
      "present": false,
      "schema_version": null
    },
    "practices": {
      "present": false,
      "schema_version": null
    },
    "reasoning": {
      "present": false,
      "schema_version": null
    },
    "graph": {
      "present": false,
      "schema_version": null
    }
  }
}
```

**Rules for importers:**
- Read `layers` before attempting to use any layer
- A layer with `present: false` is declared but empty — do not error, skip gracefully
- `schema_version` is the version of the layer's internal format — importers should check this against their supported versions
- `polly_export_version` governs the `manifest.json` format itself

**Phase 1 state:** `memory` layer present and populated. All other layers present but empty (`present: false`). This is by design — the structure exists from day one so Phase 3 can populate it without breaking existing exports.

---

## 5. README.md (Archivist-Written)

The Archivist generates `README.md` as part of the export process. It is written for a human reader who has not lived this context — a future Brett, a collaborator, an archivist.

Contents:
- Who this corpus belongs to and when it was exported
- What layers are present and what each contains
- Where to start reading (typically: a recent annual synthesis, or the most significant post-mortem)
- What's not here (explicitly noting absent layers)
- How to import into a new Polly instance (if applicable)

The README is the human entry point. The manifest.json is the machine entry point. Both are required.

---

## 6. Phase 1 Backend Deliverable

**@backend:** The only Phase 1 hook required:

1. `manifest.json` generated as part of §4.8 export, with `layers` field
2. `memory/` directory populated with daily memory files
3. All other layer directories created but empty (`present: false` in manifest)
4. Format versioned from day one (`polly_export_version: "1.0"`)
5. Basic Archivist README generated (can be minimal at Phase 1 — just owner, date, what's present)

Everything else is Phase 3. But the schema must exist at Phase 1 because:
- Users may export at Phase 1 and import at Phase 3 — the importer needs to handle both
- Retrofitting the `layers` field into a flat export format is painful
- Versioning from day one prevents breaking changes later

---

## 7. Privacy Architecture as Enabling Condition

The cognitive artifact is only possible because of the privacy architecture. A corpus that lives on a cloud provider's infrastructure cannot be bequeathed, cannot be transmitted pedagogically without the provider's cooperation, cannot be imported into a new instance without the provider's API.

Polly's self-hosted model makes the cognitive artifact concept non-negotiable: the corpus is Brett's, literally. The export is not a request to a platform — it is a direct filesystem operation. This is the enabling condition, not just a protection.

This should be reflected in the product narrative: the cognitive artifact is one of the strongest arguments for self-hosting, and self-hosting enables the cognitive artifact. They are mutually constituting.

---

## 8. Open Questions

None blocking Phase 1.

**Deferred (Phase 3):**
- Import UX: how does a new Polly instance ingest an export? What does the user see? What gets merged vs. replaced?
- Selective export: can Brett export a subset (e.g., just patterns + drift, not memory)?
- Encryption: should the export package be encrypted at rest? If so, what key management model?

---

## 9. Dependencies

- §4.8 data export in POLLY_IOS_SPEC.md: must be designed with this use case in mind
- ORAL_HISTORY.md: `oral_history/` layer populated by Archivist synthesis passes ✅
- PRACTICE_LAYER.md: `practices/` layer ✅
- STRUCTURAL_ANALOGY.md: `patterns/` layer
- TEMPORAL_INTELLIGENCE.md: `drift/` layer
- METACOGNITIVE_DASHBOARD.md: `reasoning/` layer
- Archivist agent: writes README.md at export time ✅

---

*Cross-references: POLLY_IOS_SPEC.md §4.8, ORAL_HISTORY.md, PRACTICE_LAYER.md, STRUCTURAL_ANALOGY.md, TEMPORAL_INTELLIGENCE.md, METACOGNITIVE_DASHBOARD.md, POLLY_AGENT_TEMPLATES.md (Archivist)*

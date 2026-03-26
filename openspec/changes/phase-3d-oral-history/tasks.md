# Phase 3D: Oral History

**Status:** 💡 Specced  
**Gate:** Phase 3B cognitive features (conversation corpus) + Phase 2 voice upgrade (real transcripts)  
**Spec source:** `ORAL_HISTORY.md`; `POLLY_IOS_SPEC.md` §22; `COGNITIVE_ARTIFACT.md`  
**Owners:** @frontend, @backend (synthesis pipeline), @qa_guy (Archivist SOUL compliance tests)

## Goal

The Archivist agent performs post-mortem synthesis on completed projects and annual synthesis across years of work. Output feeds Cognitive Artifact export. Voice transcripts indexable and searchable.

## Tasks

### Voice Transcript Corpus
- [ ] Voice session transcripts indexed in Knowledge Skill (`source: "voice_transcript"`, `agent_id`, `session_date`)
- [ ] Transcripts chunked by topic turn (not by sentence)
- [ ] Searchable via `knowledge_conversation_history` with `source: "voice_transcript"` filter
- [ ] @backend: transcript ingestion hook in voice session completion path

### Archivist Post-Mortem Flow
- [ ] Post-mortem trigger: user marks project as "Complete" in Today View → optional "Run post-mortem?" prompt
- [ ] Archivist session opened automatically with project context
- [ ] Post-mortem format per `ORAL_HISTORY.md` spec: 7 sections (What Was Set Out, What Happened, The Distance, Patterns, Recurring Questions, Position Shifts, For Future Self)
- [ ] Post-mortem output written to vault: `Archive/{year}/{project-name}-post-mortem.md`

### Annual Synthesis Pass
- [ ] Archivist annual synthesis triggered: cron (Jan 1) or user-initiated
- [ ] Reads: conversation history, memory files, oral history transcripts, vault, practice data, drift maps
- [ ] Annual synthesis format per `ORAL_HISTORY.md`: what the year was actually about
- [ ] Output: `Archive/{year}/annual-synthesis.md`

### Cognitive Artifact Integration
- [ ] Annual synthesis included in Cognitive Artifact export (oral history layer)
- [ ] Post-mortem documents linkable from Cognitive Artifact

### SOUL Compliance Tests
- [ ] TEST-SOUL-006: Archivist uses past tense with precision — LLM-graded
- [ ] TEST-SOUL-007: Archivist doesn't judge (observes and narrates) — LLM-graded, 4/5 threshold
- [ ] TEST-SOUL-008: Annual synthesis reads across all corpus sources (not just recent sessions)

## Done When
Voice transcripts indexed. Post-mortem flow works end-to-end. Annual synthesis writes to vault. SOUL compliance tests passing. @qa_guy sign-off.

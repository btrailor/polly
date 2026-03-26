# Phase 3D: Cognitive Artifact Full Export

**Status:** 💡 Specced  
**Gate:** Phase 3B cognitive features (for position layer, pattern layer) + phase-3d-oral-history  
**Spec source:** `COGNITIVE_ARTIFACT.md`  
**Owners:** @frontend, @backend (export pipeline)

## Goal

Full Cognitive Artifact export: all cognitive layers assembled into a portable export package. Phase 2 (`phase-2-cognitive-artifact`) shipped the foundation structure and `manifest.json`. Phase 3D adds the full cognitive layer stack.

## Tasks

### Export Layers (Phase 3D additions)
- [ ] **Position layer**: Temporal Intelligence drift map — how positions on topics evolved over time
- [ ] **Pattern layer**: EIS rhetorical pattern history — which fallacies or patterns appeared in conversations
- [ ] **Oral history layer**: Archivist annual synthesis + post-mortems linked
- [ ] **Practice layer**: engagement data — what domains were active, what was dormant, cross-pollination events
- [ ] **Mental model layer**: which mental models used most, in what contexts

### Export UI
- [ ] Export sheet: checklist of layers to include (user selects what to include)
- [ ] Export format options: ZIP (full), JSON (data only), Markdown (readable)
- [ ] Share sheet integration: AirDrop, Files app, email

### Import / Portability
- [ ] Import Cognitive Artifact from another device or backup
- [ ] Verify manifest.json integrity on import
- [ ] Conflict handling: what to do if importing artifact with conflicting session data

## Done When
All 5 cognitive layers export correctly. ZIP contains manifest.json, all layer files, linked vault notes. Import works. @security_audit confirms no credentials in export.

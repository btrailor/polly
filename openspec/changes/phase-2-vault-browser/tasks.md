# Phase 2: Vault Browser

**Status:** 📋 Planned  
**Gate:** Phase 1 vault bookmark (security-scoped bookmark stored) + Phase 1 Knowledge Skill foundation (for semantic search)  
**Spec source:** `POLLY_IOS_SPEC.md` §4.6, §11.1, §11.4, §15.3.1  
**Owners:** @frontend

## Goal

Browse the Obsidian vault from within Polly. Select notes for `/` context injection. Semantic search across vault. Foundation for the enhanced augmentation layer.

## Tasks

### File Tree Rendering
- [ ] Vault directory listing via security-scoped bookmark
- [ ] File tree component: folder collapse/expand, note list, search filter
- [ ] Note preview on tap (markdown rendered, read-only)
- [ ] Recent files section (last N opened/modified)
- [ ] Pinned notes section (user-pinned for quick access)

### `/` Context Injection
- [ ] `/` trigger in InputBar opens vault browser overlay
- [ ] Note selection → `<context>` block prepended to outgoing message
- [ ] Multiple note selection (multi-attach)
- [ ] Context size indicator: show token estimate for selected notes
- [ ] Context cap warning: if selected notes exceed model context window, warn before send

### Semantic Search
- [ ] Search field in vault browser: queries FAISS index (requires knowledge-skill foundation)
- [ ] Results show DIRECT / ADJACENT classification per note
- [ ] Fallback to filename/title search if FAISS unavailable (Phase 1 foundation not yet installed)

### Quick Capture Integration
- [ ] "View in vault" action on captured notes (opens note in vault browser)
- [ ] Promote from `_inbox/` to vault via vault browser (drag to folder or folder picker)

## Done When
User can browse vault, search semantically, select notes for context injection. `/` command works. Note preview renders. @qa_guy sign-off on vault browser UX.

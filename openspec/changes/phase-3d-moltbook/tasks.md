# Phase 3D: MoltbookView

**Status:** 💡 Specced  
**Gate:** Phase 2 Moltbook feed integration  
**Spec source:** `POLLY_IOS_SPEC.md` §4.4  
**Owners:** @frontend

## Goal

Full `MoltbookView` — browse and interact with the Moltbook feed within Polly. Memory search across Moltbook content. Agent participation on Moltbook items.

## Tasks

### Feed Browsing
- [ ] Full Moltbook feed in dedicated tab or drawer panel
- [ ] Infinite scroll (pagination)
- [ ] Rich post rendering: text, images, links, embeds
- [ ] Pull-to-refresh

### Memory Search
- [ ] Search Moltbook content via Knowledge Skill (Moltbook indexed in Phase 2)
- [ ] Search results show: post preview, author, date, relevance indicator
- [ ] Tap result → open post in feed

### Agent Participation
- [ ] Long-press post → "Ask [Agent]" action sheet
- [ ] Selected agent opens with post content as context
- [ ] "Add to vault" action: save post as knowledge note

### Phase 2 Dependency
- Requires Phase 2 Moltbook feed infrastructure (gateway Moltbook API access, feed indexing)
- If Phase 2 Moltbook feed not shipped, this entire change is blocked

## Done When
Full feed browsing working. Memory search over Moltbook content. Agent participation on posts. @qa_guy sign-off.

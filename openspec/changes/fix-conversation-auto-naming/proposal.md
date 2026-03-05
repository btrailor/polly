# Fix Conversation Auto-Naming — Proposal

**Date**: 2026-03-04  
**Status**: ✅ Complete  
**Priority**: P1 — Critical UX regression  
**Scope**: Frontend + Backend  
**Depends On**: None

---

## Problem Statement

New conversations in the conversation panel are no longer automatically named based on their content. This causes an accumulation of conversations titled "New conversation," making it extremely difficult for users to locate specific conversations later.

### Root Cause Analysis

The auto-titling mechanism exists but is silently failing:

1. **Title generation uses the main query endpoint** — `generateConversationTitle()` in `app.js:1461` sends a raw prompt through `window.polly.query()` to generate a title. This routes through the full RAG pipeline (embedding lookup, persona routing, etc.) instead of a lightweight LLM call. If routing fails, returns an error, or the response format doesn't match expectations, the title is never set.

2. **Title check comparison is case-sensitive** — `conversationNeedsTitle()` in `conversation-manager.js:558` checks `conv.title === 'New Conversation'` (capital C), but `createNewConversation()` in `app.js:1498` creates with `title: "New conversation"` (lowercase c). This mismatch means the needs-title check always returns `false` — the conversation is never flagged as needing a title.

3. **`message_count` may not be incremented synchronously** — The auto-title check at `app.js:1381` reads `currentConversation.message_count` which may not reflect the just-added message if the count is read before the DB write completes.

4. **No retry or fallback** — If `generateConversationTitle()` fails (network, LLM error, timeout), it silently catches the error and never retries. The conversation remains "New conversation" forever.

5. **No UI feedback** — The user has no visual indication that a title was (or was not) generated.

### Impact

- Users accumulate dozens of "New conversation" entries
- Finding a past conversation requires opening each one
- The conversation panel becomes effectively unusable for history navigation
- Users lose trust in the system's ability to organize their knowledge

---

## Goals

1. **Fix the title comparison mismatch** so auto-titling actually triggers
2. **Use a dedicated lightweight title-generation call** instead of the full query pipeline
3. **Add retry logic** with exponential backoff for failed title generation
4. **Provide immediate visual feedback** — show a "Generating title..." placeholder then animate the transition
5. **Backfill existing untitled conversations** — offer a one-time "Name all untitled conversations" action

---

## Non-Goals

- Redesigning the conversation list UI (separate concern)
- Changing how conversations are categorized or grouped
- Adding user-editable title templates

---

## Success Criteria

1. Every conversation with 3+ messages gets an auto-generated title within 10 seconds of the third message
2. Title mismatch bug is fixed — comparison is case-insensitive
3. If title generation fails, it retries up to 3 times with backoff, then falls back to a heuristic title (first user message, truncated)
4. UI shows "Naming..." shimmer on the conversation list entry while generating
5. Existing "New conversation" entries can be bulk-renamed via a button in conversation panel header
6. Generated titles are concise (≤50 chars), descriptive, and avoid generic phrases like "Discussion about..." or "Conversation regarding..."

---

## User Stories

**As a user who just started a conversation**, I want the conversation to be automatically named after a few messages so I can find it later without manual effort.

**As a user with many untitled conversations**, I want to bulk-rename all of them so my conversation history becomes navigable.

**As a user who notices a generation failure**, I want the system to retry silently and fall back to a reasonable heuristic title rather than leaving it as "New conversation."

---

## Technical Approach

### Phase 1: Fix the Immediate Bug

**Frontend (`app.js`):**

- Fix case mismatch: normalize both sides of the title comparison to lowercase
- Ensure `message_count` is read after the DB write confirms (await the addMessage result before checking)
- In `createNewConversation()`, keep the default title consistent (use `"New conversation"` everywhere)

**Backend (`conversation-manager.js`):**

- Fix `conversationNeedsTitle()` to use case-insensitive comparison: `conv.title.toLowerCase() === 'new conversation'`

### Phase 2: Dedicated Title Generation Endpoint

**Backend (`server.py`):**

- Add `POST /polly/conversations/{id}/generate-title` endpoint
- Takes conversation ID, fetches first 4-6 messages from DB
- Sends a focused prompt to the LLM (any available provider, fast tier):

  ```
  Generate a concise title (max 6 words) for this conversation.
  Return ONLY the title, no quotes, no explanation.

  Messages:
  {messages}
  ```

- Returns `{ "title": "..." }` or falls back to first-user-message heuristic on failure
- This avoids routing through RAG/persona/domain systems — it's a pure LLM completion

**Frontend (`app.js`):**

- Replace `generateConversationTitle()` to call the new endpoint instead of `window.polly.query()`
- Add retry logic: 3 attempts with 2s/4s/8s backoff
- Final fallback: extract first user message, truncate to 50 chars at word boundary

### Phase 3: UI Polish

- Add a subtle shimmer/pulse animation on the conversation list item title while generating
- Animate title appearance (fade transition from "New conversation" to generated title)
- Add "Name all untitled" button to conversation panel header (visible only when untitled count > 0)
- Bulk naming calls the new endpoint for each untitled conversation (rate-limited to 1/second)

### Phase 4: Prompt Quality

- Refine the title generation prompt to produce titles that are:
  - Topic-focused (not meta-descriptions like "Discussion about X")
  - 3-6 words ideal length
  - Reflect the core subject, not the first question's phrasing
- Test with diverse conversation types (technical, creative, planning, research)

---

## Risks & Mitigations

**Risk**: LLM provider unavailable when title needs generating  
**Mitigation**: Heuristic fallback uses first user message. Title can be regenerated when LLM is next available via a queue.

**Risk**: Bulk renaming many conversations hammers the LLM  
**Mitigation**: Rate-limited to 1 request/second. Uses fast tier. Shows progress indicator.

**Risk**: Generated titles are low quality  
**Mitigation**: Users can always manually rename (existing feature). Prompt engineering + title length constraints keep quality consistent.

---

## Timeline Estimate

- Phase 1 (Bug fix): 1 hour
- Phase 2 (Dedicated endpoint): 2 hours
- Phase 3 (UI polish): 2 hours
- Phase 4 (Prompt quality): 1 hour

**Total: ~6 hours**

---

## Related Work

- Conversation management: `electron-app/src/main/conversation-manager.js`
- Frontend conversation logic: `electron-app/src/renderer/app.js` (lines 1380-1520)
- Query pipeline: `interfaces/server.py`, `core/polly.py`

---

## Open Questions

1. Should titles be re-generated if the conversation topic shifts significantly? → **Defer to future enhancement**
2. Should we show a "title confidence" or let users rate the generated title? → **No, keep simple — auto-generate, manual override available**
3. Should the backfill queue run on app startup? → **No — show a button, let user trigger it intentionally**

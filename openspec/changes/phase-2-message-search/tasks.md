# Phase 2: Message Search

**Status:** 📋 Planned  
**Gate:** Phase 1 message cache (expo-sqlite with messages stored)  
**Spec source:** `POLLY_IOS_SPEC.md` §4.6.1  
**Owners:** @frontend, @backend (server-side extension)

## Goal

Full-text search over local message history. Find past conversations by content, agent, or date.

## Tasks

### Local Search (SQLite FTS5)
- [ ] Add FTS5 virtual table to expo-sqlite message schema: `CREATE VIRTUAL TABLE messages_fts USING fts5(content, agent_id, session_key)`
- [ ] Populate FTS5 index on message insert + update
- [ ] Search query → FTS5 `MATCH` → ranked results
- [ ] Snippet extraction: highlight matching text in results

### Search UI
- [ ] Search bar in conversation list header (or dedicated Search tab)
- [ ] Real-time results as user types (debounced 300ms)
- [ ] Result cell: agent avatar, session label, snippet with highlight, date
- [ ] Tap result → open session at that message (scroll to position)
- [ ] Filter by agent (dropdown/chip)
- [ ] Filter by date range (date picker)
- [ ] Empty state: "No messages match" with suggestion to search vault instead

### Server-Side Extension (Phase 2+)
- [ ] When local cache doesn't have full history, surface "Search gateway" option
- [ ] Gateway `sessions.search` RPC (if @backend implements — flag as @backend enhancement)

### Index Management
- [ ] FTS5 index rebuild on cache clear
- [ ] Exclude system messages (`NO_REPLY`, `HEARTBEAT_OK`) from index
- [ ] Index size monitoring (warn if >50MB)

## Done When
FTS5 search working on local messages. Results render with highlights. Tap navigates to message in session. @qa_guy confirms search latency <200ms for 10k messages.

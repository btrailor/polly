# Phase 2: Swarm Coordination — Task Tracking + Coordinator Heuristic

**Status:** 📋 Planned  
**Gate:** Phase 1 group chat foundation complete  
**Spec source:** `SWARM_COORDINATION_SPEC.md` §7 Phase 2  
**@backend prerequisite:** Answer 7 gateway questions in `SWARM_COORDINATION_SPEC.md §8` before starting

## Goal

Group chats go from conversations to coordinated work sessions. Agents can be assigned tasks, track progress, and report back. The coordinator heuristic routes messages to the right agent without requiring a second LLM call.

## Tasks

### @backend — Gateway Status (updated 2026-03-25)

**Confirmed (Q2–Q7):**
- ✅ Q2: `chat.typing` carries `sessionKey` → `agentId` extractable → Phase 1 per-agent thinking toasts unblocked
- ✅ Q3: Activation mode currently **global** — per-agent-per-group = Phase 2 gateway change (@backend owns)
- ✅ Q4: Deleted agent → per-agent error, fan-out continues → @frontend: "This agent is no longer available" error bubble
- ✅ Q5: `targetAgentIds` **not supported** — Phase 2 gateway change (@backend owns); unblocks structured conversations
- ✅ Q6: No hard cap; Phase 2 soft cap 8 + queue pending load validation
- ✅ Q7: Write isolated per-workspace; cross-workspace read only; `swarm_update` tool design confirmed correct

**Pending:**
- [ ] [BLOCKED: @backend] Q1: Confirm exact injection format from actual group chat session JSONL (expected: `user` role + `[Agent: {agentId}]:` header)

**Phase 2 gateway changes @backend owns (add to @backend queue):**
- [ ] [@backend] `targetAgentIds` param on `agent` RPC — selective fan-out
- [ ] [@backend] Per-agent-per-group `activationMode` override field on group membership record

### `swarm_update` Tool
- [ ] Tool spec finalized (SWARM_COORDINATION_SPEC.md §5.1)
- [ ] Gateway: expose `swarm_update` tool to agents in group sessions
- [ ] Tool validates required fields; writes task file with correct frontmatter

### Signal Parsing
- [ ] Parse `::DONE::`, `::BLOCKED::`, `::CLAIM::`, `::IN_PROGRESS::` from chat event stream
- [ ] `TaskMemberState` type with `fileStatus`, `signalStatus`, `resolvedStatus`
- [ ] Resolution rule: most recent signal wins; fall back to file; else `not_started`

### Review Status Card (Task Board)
- [ ] Signal-driven updates: task board updates instantly on signal detection
- [ ] Lazy file sync: file reads only on open + explicit refresh tap
- [ ] `TaskMemberState` grid: agent × task status
- [ ] @code_architect progress chips (claimed/in_progress/done/blocked)

### Coordinator Heuristic Routing (Option A)
- [ ] Keyword/domain matching for `defaultResponder` selection (no LLM call)
- [ ] Heuristic rules: code keywords → `code_architect`, security keywords → `security_audit`, etc.
- [ ] Configurable per-group: `fanOutPolicy: 'all' | 'mention-only' | 'coordinator'`

### Swarm Templates
- [ ] "Build Team" template (code_architect + frontend + backend + qa_guy)
- [ ] "Code Review" template (code_architect + security_audit + qa_guy)
- [ ] "Architecture Review" template (code_architect + backend + researcher)
- [ ] Template picker in group creation flow

### Group Cost Controls (SWARM_COORDINATION_SPEC.md §9)
- [ ] `GroupRoutingConfig` type: `groupDailyTokenLimit`, `fanOutPolicy`, `groupTierCap`, `showCostEstimate`
- [ ] Running cost indicator in group nav bar
- [ ] Pre-send cost estimate UI for groups > 3 agents (inline confirmation above input)
- [ ] Settings → Models → Group Chat Cost Warnings toggle

### Context Management
- [ ] Summarize-and-inject for long group conversations (1–2 sentence summary per agent contribution)
- [ ] Threshold: summarize when group context exceeds 40k tokens

## Done when
Task tracking end-to-end: coordinator writes task, agents claim, update, and complete. Task board reflects real-time state via signals. Cost estimate shown before large fan-outs. @backend gateway questions answered.

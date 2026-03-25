# Phase 2: Swarm Coordination — Task Tracking + Coordinator Heuristic

**Status:** 📋 Planned  
**Gate:** Phase 1 group chat foundation complete  
**Spec source:** `SWARM_COORDINATION_SPEC.md` §7 Phase 2  
**@backend prerequisite:** Answer 7 gateway questions in `SWARM_COORDINATION_SPEC.md §8` before starting

## Goal

Group chats go from conversations to coordinated work sessions. Agents can be assigned tasks, track progress, and report back. The coordinator heuristic routes messages to the right agent without requiring a second LLM call.

## Tasks

### @backend — Gateway Questions (prerequisite; 7 questions in SWARM_COORDINATION_SPEC.md §8)
- [ ] [BLOCKED: @backend] Confirm injection format for cross-agent responses (system message? attributed assistant message?)
- [ ] [BLOCKED: @backend] Is `chat.typing` event per-agent in groups? (needed for Phase 1 thinking toasts — if not, unblock from Phase 1 to here)
- [ ] [BLOCKED: @backend] Can activation mode be set per-agent per-group or is it global?
- [ ] [BLOCKED: @backend] What happens on `agent` RPC to a group where one member is deleted?
- [ ] [BLOCKED: @backend] Does `agent` RPC support `targetAgentIds` param for selective dispatch?
- [ ] [BLOCKED: @backend] Maximum concurrent agent runs per group?
- [ ] [BLOCKED: @backend] Can `agents.files.set` write to another agent's workspace?

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

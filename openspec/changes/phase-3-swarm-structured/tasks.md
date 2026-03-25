# Phase 3: Structured Conversations + Coordinator Pre-Dispatch

**Status:** 💡 Specced  
**Gate:** Phase 2 swarm coordination complete + Phase 1 agent system complete (Liaison SOUL)  
**Spec source:** `SWARM_COORDINATION_SPEC.md` §7 Phase 3; `CONVERSATION_ARCHITECTURE.md`

## Goal

Group chats acquire formal cognitive structure. The Liaison agent designs conversation topologies. Phases are enforced client-side. The coordinator makes routing decisions via a pre-dispatch LLM call instead of heuristics.

## Tasks

### Client Phase Management
- [ ] `GroupPhaseState` type: `topology`, `currentPhase`, `phases[]` with `activeAgentIds`, `timeLimitMinutes`, `synthesizer`
- [ ] MMKV storage: `polly.group.{groupId}.phaseState`
- [ ] Phase-aware dispatch: client sends `agent` RPC only to `activeAgentIds` for current phase
- [ ] Liaison signal parsing: detect `::PHASE_TRANSITION phase=N name="..."::` in chat stream
- [ ] On transition: update `GroupPhaseState`, render phase banner, adjust dispatch

### Phase Transition UI
- [ ] Phase banner: "Phase 2: Cluster — Analyst + Liaison active" (dismissible)
- [ ] Agent availability indicator per phase (e.g., greyed-out avatars for out-of-phase agents)
- [ ] Phase timer display (if `timeLimitMinutes` set)
- [ ] Manual phase advance option (for user-controlled conversations)

### Topology Library
- [ ] 6 topologies from `CONVERSATION_ARCHITECTURE.md` (diverge-converge, debate, funnel, etc.)
- [ ] Topology picker at group creation: select topology or "Freeform"
- [ ] Liaison designs topology from scratch on user request: "Design a 3-phase architecture review"

### Liaison SOUL Update
- [ ] Liaison SOUL: add conversation architect mode
- [ ] Liaison knows `::PHASE_TRANSITION::` signal syntax
- [ ] Liaison can describe phase plans, request agent assignments, trigger transitions

### Coordinator Pre-Dispatch (Option B)
- [ ] Separate `chat.send` to coordinator session before fan-out (hidden from group view)
- [ ] Parse coordinator response for @mentions → dispatch only to mentioned agents
- [ ] Fallback to `defaultResponder` if coordinator call fails or times out (2s timeout)
- [ ] Coordinator session accumulation handling (periodic context flush)

### Per-Agent Augmentation
- [ ] @mention-scoped context: `<context>` blocks injected only into @mentioned agent's session
- [ ] "This context is for @security_audit" → PollyEnhancement Layer routes context accordingly

### Group Session Summary
- [ ] Trigger: group chat idle ≥30 min or user closes group session
- [ ] Coordinator (or `defaultResponder`) writes summary to `_swarm/sessions/{groupId}-{date}.md`
- [ ] Summary format: group, date, participants, topics, decisions, open_items
- [ ] Plans Layer reads from this file for swarm context injection (§23.7)

## Done when
Phase transitions work: Liaison triggers, banner appears, out-of-phase agents stop receiving. Coordinator pre-dispatch routes messages more accurately than heuristic. Per-agent augmentation works for @mention-scoped context. Group summaries written on close.

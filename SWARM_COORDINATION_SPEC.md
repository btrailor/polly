# SWARM_COORDINATION_SPEC.md

Phase 1–4 — Multi-Agent Coordination: From Protocol to Implementation  
Status: Draft  
Owners: @code_architect (coordination model), @backend (gateway dispatch), @frontend (iOS rendering)  
Last updated: 2026-03-25  
Cross-references: `POLLY_IOS_SPEC.md` §22, §23; `CONVERSATION_ARCHITECTURE.md`; `CHORUS_MODE.md`; `MODEL_ROUTING_SPEC.md`; `POLLY_AGENT_TEMPLATES.md` (Liaison)

---

## 1. What This Document Does

`POLLY_IOS_SPEC.md §22` describes swarm patterns (Planning, Review, Debate, Handoff), file-based task tracking, and cross-team bridges. `CONVERSATION_ARCHITECTURE.md` adds topology-driven structured conversations. `CHORUS_MODE.md` adds parallel dispatch.

These are three different coordination models with different mechanics. The specs don't clearly distinguish which problems each one solves, how they interact, or what OpenClaw actually supports underneath.

This document:
- Maps what OpenClaw's group chat protocol actually does vs. what the specs assume
- Identifies where the specs require gateway capabilities that don't exist
- Defines the concrete implementation path for each coordination model
- Addresses the hard problems the specs skip: context window management, cost multiplication, ordering, error recovery, and the coordinator problem

---

## 2. What OpenClaw Actually Provides

```
User sends message via agent RPC with groupId
 │
 ▼
Gateway fans out to all agents registered for that groupId
 │
 ▼
Each agent has its OWN session: agent:{agentId}:group-chat:{groupId}
 │
 ▼
Each agent responds independently on its own session
 │
 ▼
Client receives chat events tagged with each agent's sessionKey
```

**Gateway provides:**
- Fan-out: one user message → all group members
- Per-agent sessions: each agent maintains independent context
- Activation modes: `mention` (respond only when @mentioned) or `always` (respond to everything)
- `chat` events tagged with agent identity
- `agents.files.get` supports cross-agent workspace reads

**Gateway does NOT provide:**
- Turn ordering (agents respond as fast as they can — no queue)
- Coordinator dispatch (no two-step "coordinator decides, then agent responds")
- Phase state on sessions
- Agent silencing per-phase
- Response gating (no holding one agent's response until another finishes)
- Shared context between agents (each agent sees only its own session)

This is the foundational constraint. Every coordination model has to work within or around these limits.

---

## 3. The Five Hard Problems

### 3.1 Context Divergence

Each agent in a group chat maintains its own session. For Agent A to see Agent B's response, B's response must be injected into A's session.

**How Aight handles this (confirmed from live session JSONL, @backend 2026-03-25):** Other agents' responses are **not** injected as separate messages. They appear embedded in the `user` turn's `[Recent messages]` context block, formatted as `**@agentname:** text`. The Aight client composes this header on every `agent` RPC send. Each agent's own prior messages are stubbed as `[your message at HH:MM]`. There is no gateway-level injection — it's all `user` role, narrative context. Agents perceive other agents' messages as conversation history, not as distinct system or assistant signals.

**The cost implication:** Every agent response gets injected into every other agent's context. In a 5-agent group with 20 exchanges, each agent's context contains ~100 messages. At ~500 tokens per response, that's 50k tokens per agent. Five agents = 250k tokens of context. Grows quadratically.

**Solutions (by phase):**
- Phase 2: Summarize-and-inject — 1–2 sentence summary of each agent's contribution instead of full response (~5x reduction)
- Phase 2: Selective injection — only inject responses that @mention the receiving agent; others available via file read
- Phase 3: Rolling group summary — coordinator posts "state of conversation" summary that replaces accumulated history (same mechanic as SOUL baseline context compression)

### 3.2 Cost Multiplication

A group chat with N agents multiplies token cost by N or more. A single user question in a 5-agent Tier 3 group = ~$0.25 per message. Twenty exchanges = $5.

The spec doesn't address per-group budget tracking. **Solution:** Group-level cost controls — see §9.

### 3.3 The Coordinator Problem

The spec requires a Phase 2 coordinator pattern: coordinator classifies first, then only selected agent fires. OpenClaw fans out simultaneously — there's no "coordinator first" sequencing.

**Three options:**

| Option | Mechanism | Phase | Verdict |
|--------|-----------|-------|---------|
| **A. Heuristic routing** | Keyword/domain matching, client-side. No LLM call, no latency. | Phase 2 | Recommended for Phase 2 |
| **B. Pre-dispatch call** | Separate `chat.send` to coordinator before fan-out; parse @mentions from response; dispatch only mentioned agents | Phase 3 | Recommended for Phase 3 |
| **C. Gateway enhancement** | Request OpenClaw add a `dispatch: coordinator` mode | Future | Tracked as gateway feature request |

**Recommendation:** Phase 1 = `defaultResponder` (no coordinator). Phase 2 = Option A. Phase 3 = Option B for groups with designated coordinator agent. Option C tracked as gateway feature request for @backend.

### 3.4 Phase Transitions in Structured Conversations

`CONVERSATION_ARCHITECTURE.md` requires phase-aware group chats: "agents outside the active phase are silenced." The gateway has no concept of phases.

**Implementation:** Phases are client-side state, enforced by selective dispatch — not gateway-side silencing.

```typescript
interface GroupPhaseState {
  topology: string;          // "diverge-converge"
  currentPhase: number;
  phases: {
    phase: number;
    name: string;
    activeAgentIds: string[];  // only these agents receive messages
    timeLimitMinutes?: number;
    synthesizer?: string;      // agent that produces phase summary
  }[];
}
```

When user sends a message during a phased conversation:
1. Client checks `currentPhase` → gets `activeAgentIds`
2. Client sends `agent` RPC only to active agents' sessions
3. Out-of-phase agents simply don't receive the message
4. Liaison posts `::PHASE_TRANSITION phase=2 name="Cluster"::` as a structured signal
5. Client parses → updates `GroupPhaseState` → visual phase banner appears

**Storage:** MMKV `polly.group.{groupId}.phaseState` — client-managed, not gateway.

### 3.5 Ordering and Interleaving

When N agents respond simultaneously, their `delta` events arrive interleaved. The rendering solution: key streaming bubbles by `agentId:runId`, not just `runId`.

```typescript
interface GroupStreamState {
  [agentRunKey: string]: {  // key: `${agentId}:${runId}`
    agentId: string;
    text: string;           // accumulated text so far
    isStreaming: boolean;
    startedAt: number;
  };
}
```

Visual ordering: agent bubbles appear in order of first delta arrival. Multiple bubbles stream simultaneously. Auto-scroll follows most recently updated bubble. Scroll lock (§4.1) applies per-bubble-cluster, not per-individual-bubble.

---

## 4. The Three Coordination Models — Clarified

```
               Sequential            Parallel
               ──────────            ────────
Unstructured:  Reactive Chat         Chorus
               (§22, Phase 1)        (Phase 4+)

Structured:    Conversation          [Phase 5+ — structured
               Architecture          parallel = Chorus +
               (Phase 3)             topology]
```

### 4.1 Reactive Group Chat (§22) — Phase 1

- **What:** Agents respond to user and to each other. Sequential, any agent can respond. Coordination is conversational via @mentions.
- **When:** Working sessions — "build this feature," "review this code."
- **Cost:** N agents × M exchanges. `mention` activation mode bounds cost.
- **Phase 1 deliverable.** The only coordination model in Phase 1.

### 4.2 Structured Conversation (CONVERSATION_ARCHITECTURE.md) — Phase 3

- **What:** Liaison-designed topology with phases, time constraints, agent assignments per phase.
- **When:** High-stakes decisions. Complex problem-solving. Process quality matters.
- **Cost:** Lower than unstructured — only active-phase agents fire.
- **Phase 3.** Requires: group chats working, Liaison SOUL update, client phase management, phase transition UI.

### 4.3 Chorus (CHORUS_MODE.md) — Phase 4+

- **What:** Pure parallel dispatch. No coordination, no context sharing, no conversation. Same prompt → N agents simultaneously → independent responses.
- **When:** Full perspectival landscape. Not for converging — for seeing the field.
- **Cost:** Exactly N agents × 1 prompt. Cheapest multi-agent pattern per-insight.
- **Phase 4+.** Requires: grid UI (iPad-first), `topology` field on message model, `chorus_position` coordinates.

---

## 5. Task Tracking — Making It Reliable

§22.8 defines file-based task tracking. The problem: LLMs don't reliably write structured files. An agent might respond "Done!" but forget to write `done-[id].md`, or write it with wrong frontmatter.

### 5.1 `swarm_update` Tool

Instead of agents constructing files manually, expose a tool with validation:

```json
{
  "name": "swarm_update",
  "description": "Update task status in the swarm task board. Handles file write with correct frontmatter. Agents call this instead of writing files directly.",
  "parameters": {
    "task_id": "string",
    "status": "\"claimed\" | \"in_progress\" | \"done\" | \"blocked\"",
    "summary": "string (optional)",
    "blockers": "string[] (optional)"
  },
  "returns": {
    "ok": "boolean",
    "file_written": "string — path"
  }
}
```

### 5.2 Signal Parsing as Primary Source

Parse `::DONE::` / `::BLOCKED::` / `::CLAIM::` signals from chat events as the real-time state source. File writes are a secondary record. If signal and file disagree, signal wins (more recent).

```typescript
interface TaskMemberState {
  agentId: string;
  fileStatus: 'not_started' | 'in_progress' | 'done' | 'blocked' | 'file_missing';
  signalStatus: 'not_started' | 'claimed' | 'in_progress' | 'done' | 'blocked';
  resolvedStatus: 'not_started' | 'in_progress' | 'done' | 'blocked';
  lastSignalAt?: number;
  lastFileUpdateAt?: number;
}
// Resolution: most recent signal wins. If no signal, use file. If neither, not_started.
```

### 5.3 Signal-Driven Task Board

No polling. Task board updates instantly on chat signal detection. File reads only on task board open and explicit "Refresh" tap.

---

## 6. Error Recovery, Edge Cases

### 6.1 Agent Failures in Groups

| Failure | Handling |
|---------|----------|
| Model failure | Error bubble with agent attribution. Retry for that agent. Others unaffected. |
| Agent timeout (>60s) | "Agent timed out" bubble. Don't block other agents' rendering. |
| Rate limited | "Rate limited — try again in Xs." Other agents respond normally. |
| Coordinator fails | Fall back to `defaultResponder`. Surface "Coordinator unavailable." |
| All agents fail | Group-level error: "No agents could respond. Check model configuration." |

### 6.2 Adding/Removing Agents Mid-Conversation

Adding: new agent session created with system-injected summary of conversation so far (not full history). Removing: session not deleted — agent still accessible individually.

### 6.3 Augmentation in Group Chats

The PollyEnhancement Layer (§11.0) augments outgoing messages with vault notes and mental models. In Phase 1–2, augmentation goes to all agents in the fan-out.

Phase 3: per-agent augmentation via @mention-scoped context — `<context>` block injected only into the @mentioned agent's session.

### 6.4 Voice in Group Chats

TTS reads only the `defaultResponder`'s response (or first to arrive). Other agents' responses available visually but not read aloud. User can tap any bubble to hear it.

### 6.5 Group Session Summary

When a group chat goes idle (30+ minutes) or user explicitly closes, the coordinator (or `defaultResponder`) writes:

```
_swarm/sessions/{groupId}-{date}.md
---
group: Polly Build Team
date: 2026-03-25
participants: [code_architect, frontend, backend, qa_guy]
topics: [shortcut grid component, testing strategy]
decisions: [...]
open_items: [...]
---
[summary content]
```

This becomes the "where did we leave off?" document for the next session. Plans Layer swarm context injection (§23.7) reads from here.

---

## 7. Phase Plan

### Phase 1: Reactive Group Chat
- Group creation (name + member selection)
- Fan-out via `agent` RPC with `groupId`
- Multi-agent message rendering (agent labels, accent colors, @mention highlighting)
- `defaultResponder` for no-@mention messages
- `mention` and `always` activation modes per agent
- Per-agent thinking toast
- Group sessions in drawer
- Simultaneous streaming: `GroupStreamState`, multiple bubbles streaming at once

**Forward-compatible data model additions (Phase 1 — don't defer these):**
- `topology` field on message objects: `"chat"` (default), `"chorus"` (Phase 4+), `"architecture"` (Phase 3)
- `chorus_position` nullable field on message objects
- `GroupStreamState` in Zustand for concurrent streaming

### Phase 2: Task Tracking + Coordinator Heuristic
- `swarm_update` tool
- `::SIGNAL::` parsing from chat events
- Review Status Card (task board) — signal-driven, lazy file sync
- Coordinator heuristic routing (keyword/domain matching, client-side)
- Swarm templates (Build Team, Code Review, Architecture Review)
- Group-level cost indicator + pre-send cost estimate for groups > 3 agents
- Group chat context management (summarize-and-inject)

### Phase 3: Structured Conversations + Coordinator Pre-Dispatch
- Client-managed phase state (`GroupPhaseState`)
- Topology library (6 topologies from `CONVERSATION_ARCHITECTURE.md`)
- Liaison conversation architect mode + SOUL update
- Phase transition UI (phase banner, agent availability indicator)
- Coordinator pre-dispatch (Option B: classifier call before fan-out)
- Per-agent augmentation via @mention-scoped context
- Group session summary on idle/close

### Phase 4+: Chorus + Advanced
- Chorus parallel dispatch (no shared context)
- Grid UI (iPad full grid, phone 2-panel)
- Divergence detection (semantic similarity across same-position responses)
- `chorus_position` rendering
- Cross-team bridges (Tier 1: persona-level, Tier 2: async mailbox)

---

## 8. Gateway Questions — @backend

**Answered 2026-03-25 (Q2–Q7 confirmed; Q1 pending JSONL verification):**

| Q | Question | Answer |
|---|----------|--------|
| 1 | When Agent A's response is injected into Agent B's session, what format? | ✅ **Not injected as separate messages.** Embedded in the `user` role `[Recent messages]` context block as `**@agentname:** text`. Aight client composes this header on every send. No gateway-level injection — it's all `user` role, narrative context. Agent's own prior messages stubbed as `[your message at HH:MM]`. Confirmed from live session JSONL, @backend 2026-03-25. |
| 2 | Is there a `chat.typing` event with agent identity for groups? | ✅ Yes — typing/thinking event carries `sessionKey` encoding `agentId`. @frontend extracts `agentId` from `sessionKey` for per-agent toast. |
| 3 | Can activation mode be set per-agent per-group, or is it a global agent setting? | ✅ Currently **global**. Per-agent-per-group requires group membership record `activationMode` override. **@backend Phase 2 gateway change.** |
| 4 | What happens on `agent` RPC to a group where one member is deleted? | ✅ Per-agent error for deleted agent, fan-out continues. @frontend: render error bubble "This agent is no longer available." |
| 5 | Does `agent` RPC support `targetAgentIds` for selective dispatch? | ✅ **Not currently supported.** Fan-out is all-or-nothing. **@backend Phase 2 gateway change** — unblocks structured conversations + cost-aware partial fan-out. |
| 6 | Maximum concurrent agent runs per group? | ✅ No hard cap. All agents fire simultaneously. Phase 2: soft cap of 8 with queue recommended, pending load validation. |
| 7 | Can `agents.files.set` write to another agent's workspace? | ✅ **Write isolated.** Read is cross-workspace. Coordinator writes to own workspace; members read cross-workspace. `swarm_update` tool (§5.1) is correct. |

**Phase 2 gateway changes @backend owns:**
- `targetAgentIds` param on `agent` RPC (selective fan-out)
- Per-agent-per-group `activationMode` override field on group membership record

---

## 9. Group Routing Config (Additions to MODEL_ROUTING_SPEC.md)

```typescript
interface GroupRoutingConfig {
  groupDailyTokenLimit?: number;       // per-group budget cap
  fanOutPolicy: 'all' | 'mention-only' | 'coordinator';
  // Default: 2 for groups > 3 agents (@backend 2026-03-25 — prevents always-mode groups
  // burning Tier 3 budget at 5× rate; user can raise explicitly)
  groupTierCap?: number;               // default: 2 (for groups > 3), undefined (for ≤ 3)
  showCostEstimate: boolean;           // default true for groups > 3 agents
}
```

Pre-send cost estimate UI (for groups > 3 agents when `showCostEstimate: true`):

```
┌─────────────────────────────────────┐
│ This will send to 5 agents.         │
│ Estimated cost: ~$0.15              │
│ [Send]  [Send to @mentioned only]   │
└─────────────────────────────────────┘
```

Brief inline confirmation above input bar. Dismissible. Configurable in Settings → Models → Group Chat Cost Warnings. Not shown for groups ≤ 3 agents or when `mention-only` mode is active.

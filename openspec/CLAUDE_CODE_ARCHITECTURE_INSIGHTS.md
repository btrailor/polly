# CLAUDE_CODE_ARCHITECTURE_INSIGHTS.md

Reference document — informs spec and implementation decisions  
Source: Analysis of Claude Code CLI (2026-03-31, ~512k lines TypeScript)  
Status: Approved by Brett for incorporation into active specs  
Last updated: 2026-03-31

## What This Is

Architectural patterns extracted from Anthropic's production Claude Code CLI that are directly applicable to Polly. Design decisions made under real production constraints — patterns worth adopting, adapting, or explicitly rejecting with reasoning.

This is not a directive to change Polly's tech stack. React Native + Expo remains the correct choice. This document identifies specific patterns to incorporate and specific native module boundaries to plan for.

**All "Spec action" items from this document have been incorporated into the relevant openspec change sets and specs. This file is the source reference; the change sets are the actionable output.**

---

## 1. Skill System Patterns → SKILLS_MARKETPLACE.md, MCP_ADAPTER.md

### 1.1 Conditional Skill Activation
Claude Code skills declare a `paths` frontmatter field — gitignore-style patterns. Skills with `paths` are not loaded into the tool list until a matching file is touched. Relevant skills surface automatically; the model sees a lean tool list.

**Spec action (incorporated):** `activation_conditions` field added to skill manifest schema tasks in `phase-2-skills-marketplace`. Condition types: `vault_path_patterns`, `domain_match`, `agent_match`, `manual`. Backward-compatible.

### 1.2 MCP Trust Boundary
Claude Code MCP skills cannot execute inline shell commands. Local skills can; MCP skills cannot. Hard security boundary, not configurable.

**Spec action (incorporated):** MCP-sourced skills blocked from shell execution and vault writes without per-invocation confirmation. MCP skills default to Community trust tier. Added to `phase-2-skills-marketplace` tasks.

### 1.3 Skill Frontmatter Convention
Useful Claude Code fields and their Polly equivalents:

| Field | Claude Code | Polly equivalent |
|-------|-------------|-----------------|
| `when_to_use` | LLM reads to decide invocation | Agent reads from skill manifest |
| `allowed-tools` | Tool whitelist per skill | `permissions` in manifest |
| `user-invocable` | User vs. model-only invocation | `drawer_visible` equivalent |
| `paths` | Conditional activation | `activation_conditions` |
| `model` | Per-skill model override | Already in MODEL_ROUTING_SPEC.md |
| `effort` | Effort level override | Routing tier (Fast/Balanced/Thorough) |

---

## 2. Multi-Agent Coordination → SWARM_COORDINATION_SPEC.md

### 2.1 Coordinator as System Prompt
Claude Code's coordinator is a system prompt that transforms the main agent into an orchestrator — not a separate service. The same tool system handles everything.

**Spec action (incorporated):** Ward implemented as a SOUL mode / system prompt config on the gateway. `coordinator_mode` flag on session model. Activates automatically on ambiguous routing or explicit group chat invocation. Added to `phase-2-swarm-coordination` tasks.

### 2.2 Worker Results as User-Role Messages
Worker results arrive as user-role messages containing XML. Polly's signal token system (@signal:done, etc.) serves the same purpose with different encoding — both are valid. Signal tokens in user-role messages is the Phase 1 pragmatic choice (no protocol changes needed).

### 2.3 Scratchpad for Cross-Agent Context
Claude Code provides a shared scratchpad directory (flat key-value, no schema, per-session only) for cross-agent context sharing.

**Spec action (incorporated):** Per-session scratchpad added to `phase-2-swarm-coordination` tasks as the lightweight Phase 2 solution. Full canonical store (structured, persistent, cross-session) remains Phase 3+.

---

## 3. Memory Patterns → KNOWLEDGE_SKILL.md, KNOWLEDGE_WRITE_PATH.md

### 3.1 Two-Tier Memory (Always-Loaded + On-Demand)
Claude Code loads MEMORY.md (capped at 200 lines / 25KB) into every prompt. Additional topic files selected per-query by a side LLM call. Validates Polly's USER.md + Knowledge Skill architecture.

**Spec action (incorporated):** USER.md cap guidance (current 500-word soft cap vs. ~150-line hard cap recommendation) added to `openspec/specs/knowledge/spec.md`.

### 3.2 LLM-Based Memory Selection
Claude Code does not use vector search — uses LLM to select top 5 relevant files from headers. For small vaults, may outperform embedding similarity.

**Spec action (incorporated):** LLM-selection fallback added to `phase-2-knowledge-skill` tasks for low-confidence FAISS results. FAISS remains primary path.

### 3.3 Forked Agent for Memory Extraction
Session memories extracted via a forked agent (copy of main conversation sharing prompt cache) — not a separate LLM call with conversation pasted as input. Preserves full context: SOUL, tools, mental models, domain context.

**Spec action (incorporated):** Write path #7 (session-end extraction) updated in `phase-2-knowledge-skill` tasks to adopt forked agent pattern.

---

## 4. Conversation Compaction → Gateway Context Management

### 4.1 Post-Compact Restoration
After compaction, Claude Code re-injects: recently-touched files (up to 5, 5K tokens each), recently-used skills (25K budget), active plan.

**Spec action (incorporated):** Gateway post-compact restoration added to `phase-2-gateway-changes` Wave 2.5: re-inject active SOUL, active mental models, most recently referenced vault notes (up to 5), active WorkflowSession state.

### 4.2 Proactive vs. Reactive Compaction
Claude Code has a reactive path (prompt-too-long error → retroactive compact). Polly explicitly rejects this. Gateway tracks context window budget proactively and compacts before hitting the limit.

**Spec action (incorporated):** Proactive compaction requirement added to `phase-2-gateway-changes`.

### 4.3 Token Budget Reference Numbers

| Budget | Reference value | Notes |
|--------|----------------|-------|
| Compaction summary max | 20,000 tokens | Starting point |
| Post-compact file restoration | 50,000 total / 5,000 per file | Adjust per model tier |
| Post-compact skill re-injection | 25,000 tokens | SOUL + mental models |
| Memory entrypoint cap | 200 lines / 25,000 bytes | Polly: evaluate ~150 lines |

---

## 5. Native Module Boundaries → POLLY_IOS_SPEC.md §12

Phase 1 can ship in Expo managed workflow with zero native modules **if @security_audit accepts Keychain-only for device key.** See `phase-1-ios-foundation` tasks for full module table and Phase 1 decision required from @security_audit.

### Module Summary

| Module | Phase needed | Blocking? | Fallback |
|--------|-------------|-----------|---------|
| `PollyCrypto` (Secure Enclave) | 1 or 2 | @security_audit decision | expo-secure-store (Keychain) |
| `PollyAudioAnalyzer` (prosodics) | 2 | No | Transcript without prosodic metadata |
| `PollyIntents` (App Intents) | 2 | No | In-app shortcuts only |
| `PollyBackground` (BGTaskScheduler) | 2 | No | Active-session Ambient Agent only |
| EventKit wrapper | 3+ | No | Defer evaluation |

Note: `expo-app-intents` does not exist as of March 2026. @frontend must evaluate options during Phase 1 planning.

---

## 6. Patterns Explicitly Rejected

### 6.1 Vector Search Replacement
Claude Code uses LLM-only memory selection. Polly retains FAISS as primary — vault is orders of magnitude larger than a memory directory. LLM selection adopted as fallback only.

### 6.2 Separate Terminal UI Stack
Claude Code is Bun + React + Ink. Any Polly desktop companion should extend the React Native codebase (React Native for macOS or RN Web in Tauri), not introduce a second UI technology.

### 6.3 Reactive Compaction
Prompt-too-long error → retroactive compact is a symptom of insufficient budget tracking. Polly prevents rather than recovers. Proactive only.

---

## 7. Cross-Reference Map

| This document section | Incorporated into |
|----------------------|------------------|
| §1.1 Conditional activation | `phase-2-skills-marketplace` tasks |
| §1.2 MCP trust boundary | `phase-2-skills-marketplace` tasks |
| §2.1 Coordinator as prompt | `phase-2-swarm-coordination` tasks |
| §2.3 Scratchpad | `phase-2-swarm-coordination` tasks |
| §3.1 Memory cap | `openspec/specs/knowledge/spec.md` |
| §3.2 LLM-selection fallback | `phase-2-knowledge-skill` tasks |
| §3.3 Forked extraction | `phase-2-knowledge-skill` tasks |
| §4.1 Post-compact restore | `phase-2-gateway-changes` Wave 2.5 |
| §4.2 Proactive compaction | `phase-2-gateway-changes` Wave 2.5 |
| §5 Native modules | `phase-1-ios-foundation` tasks |

# AGENT_BOOTSTRAP_DEV.md

**Status:** Draft  
**Phase:** 1  
**Owner:** @code_architect  
**Created:** 2026-03-25  
**Applies to:** All agents in the "Phase two (multiverse influence)" group chat and any future dev-context group chats

---

## 1. Purpose

This spec defines the bootstrap sequence that every agent in a Polly development context must execute at session start — before responding to any message. It ensures agents are operating from current state, not stale assumptions.

Without this, agents answer questions about the codebase based on memory from prior sessions, risk working from superseded spec files, and miss recent commits. This has caused real coordination failures.

---

## 2. When to Execute

The bootstrap sequence runs:
- When an agent joins or resumes a development group chat
- When an agent receives a task that involves the Polly repo (spec writing, code review, implementation)
- When an agent has been inactive for >1 hour in a session

It does **not** need to run on every message — only at session start or resumption.

---

## 3. Bootstrap Sequence

Execute in order. Each step is a hard prerequisite for the next.

### Step 1 — Verify git state

```bash
cd ~/polly && git status && git log --oneline -5
```

Expected: branch `development`, working tree clean, HEAD matches `PROJECT_STATUS.md`.

If branch is wrong → stop, report to group chat, do not proceed.  
If working tree is dirty → report uncommitted changes before any file operations.

### Step 2 — Read PROJECT_STATUS.md

```
cat ~/polly/PROJECT_STATUS.md
```

This is the cross-session state document. Read it fully. It tells you:
- What's been shipped
- What's actively in flight and who owns it
- What specs exist and their status
- What's blocked and why

If PROJECT_STATUS.md doesn't exist yet → read SPEC_INDEX.md and MASTER_ROADMAP.md as fallback. Flag the missing file.

### Step 3 — Verify spec files exist before referencing them

Before making any claim about a spec file's contents, verify it exists:

```bash
ls ~/polly/*.md
```

A spec that exists in SPEC_INDEX.md as "Planned" or "Idea" may not have a file yet. Never hallucinate spec content. If unsure, read the file.

### Step 4 — Read SPEC_INDEX.md

```
cat ~/polly/SPEC_INDEX.md
```

Know which specs exist, their phase, status, and dependencies. Do not assume from memory.

### Step 5 — Declare ready

Post to the group chat:
> "Bootstrap complete. HEAD: `<hash>`. Branch: `development`. Read PROJECT_STATUS.md — [summary of anything newly relevant to my role]. Ready."

---

## 4. Agent-Specific Startup Reads

In addition to the universal bootstrap, each agent reads their role-specific files:

| Agent | Additional reads |
|-------|-----------------|
| @code_architect | `MASTER_ROADMAP.md` |
| @frontend | `POLLY_IOS_SPEC.md` (relevant sections), `FIGMA_INTEGRATION.md` |
| @backend | `POLLY_IOS_SPEC.md` §8.8, `KNOWLEDGE_SKILL.md` |
| @design_eng | `FIGMA_INTEGRATION.md`, `MONOME_LAYER.md`, `INFLUENCE_GUIDE.md` |
| @security_audit | `SKILLS_MARKETPLACE.md` §6, `MCP_ADAPTER.md` §5/§7/§8 |
| @infra | `MASTER_ROADMAP.md`, `MCP_ADAPTER.md` §12 Q1 |
| @researcher | `POLLY_AGENT_TEMPLATES.md` |
| @qa_guy | `POLLY_IOS_SPEC.md` (test coverage sections) |
| @ai_expert | `KNOWLEDGE_SKILL.md`, `TREE_OF_THOUGHTS.md` |

---

## 5. Hard Rules

These apply at all times in a dev context, not just at bootstrap:

1. **Never reference `specs/` folder.** It is archived legacy content. Any file inside it is outdated. If you find yourself reading `specs/`, stop.

2. **Never edit PROJECT_STATUS.md except @code_architect.** Other agents read it. If you need to flag something, post to the group chat and @code_architect will update it.

3. **A spec does not exist until it is in SPEC_INDEX.md.** An idea discussed in chat is not a spec. A file at root without an index entry is not official.

4. **Verify before claiming.** If you're about to state "the spec says X," read the file first. Do not rely on session memory for spec content.

5. **Git author is Brett Gershon <Brett.gershon@gmail.com>.** All commits go on this identity. If you see "Clarence Bojangles" in git log, stop and flag it to @infra immediately.

6. **No Electron-era concepts** unless Brett explicitly reintroduces them. The `archive/pre-ios-rewrite` branch is off-limits.

---

## 6. Failure Modes This Prevents

| Failure | Bootstrap step that prevents it |
|---------|--------------------------------|
| Agent works from outdated spec | Step 2 (PROJECT_STATUS) + Step 4 (SPEC_INDEX) |
| Agent references deleted/renamed spec | Step 3 (verify files exist) |
| Agent commits on wrong branch | Step 1 (git state) |
| Agent hallucinate spec content | Step 3 + Step 4 |
| Two agents claiming same task | Step 2 (active work table) |
| Dirty working tree before spec write | Step 1 |

---

## 7. SOUL Override (Group Chat Context)

When operating in a development group chat, each agent's standard SOUL applies with these additional behavioral constraints:

- **Claim tasks loudly.** When you start work, say so in the chat. No silent pickups.
- **Report blockers within 2 minutes.** Don't struggle silently.
- **Report completion with commit hash.** "Done" without evidence isn't done.
- **Radio silence >5 minutes on an active task = escalation.** Any agent can take over.
- **PROJECT_STATUS.md is ground truth.** Not your memory of a prior session.

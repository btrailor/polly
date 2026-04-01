# Phase 2: Plans Layer

**Status:** 📋 Not yet decomposed into implementation tasks  
**Spec source:** `POLLY_IOS_SPEC.md §23.1–§23.10`  
**Depends on:** Phase 1 complete (gateway connection, chat working)  
**Owner:** @backend (RPCs + directory) + @frontend (Plans View UI)  
**Added:** 2026-04-01 — gap identified in OpenSpec Task Coverage Audit

---

## What This Is

The Plans Layer is the "where did we leave off?" mechanism for multi-session swarm work. It gives agents durable, structured workspaces that persist across sessions.

- `~/.polly/plans/` directory with canonical plan format + frontmatter schema
- 7 RPC methods for CRUD on plans
- iOS Plans View with filter chips, inline task checkboxes, assign-to-agent swipe
- Swarm context injection: active plan injected into agent context at session start

Without Plans, every new swarm session starts cold. Agents can't resume work in progress.

---

## Gateway Tasks (@backend)

- [ ] Create `~/.polly/plans/` directory on gateway init (idempotent)
- [ ] Define canonical plan file format: frontmatter schema (`id`, `title`, `created`, `updated`, `status`, `assigned_agent`, `tags`) + markdown body with task checklist syntax (`- [ ]` / `- [x]`)
- [ ] Implement `plans.list` RPC — returns all plans with frontmatter only (no body), supports `status` filter
- [ ] Implement `plans.get` RPC — returns full plan including body
- [ ] Implement `plans.create` RPC — creates new plan file from title + optional template
- [ ] Implement `plans.update` RPC — updates frontmatter fields and/or body
- [ ] Implement `plans.task.complete` RPC — marks a specific task checkbox done by task index
- [ ] Implement `plans.log` RPC — appends a timestamped log entry to plan body
- [ ] Add Plans RPCs to `phase-2-gateway-changes/tasks.md` Wave 2

---

## Frontend Tasks (@frontend)

- [ ] Plans View screen — accessible from drawer nav
- [ ] Filter chips: All / Active / Completed / By Agent
- [ ] Plan list item: title, assigned agent chip, last-updated timestamp, task progress fraction (e.g. "3/7 tasks")
- [ ] Plan detail view: full markdown render, inline task checkboxes (tap to complete via `plans.task.complete`)
- [ ] New plan flow: title input → optional agent assignment → creates via `plans.create`
- [ ] Swipe action on plan: "Assign to agent" → agent picker → `plans.update`
- [ ] Plan badge on agent in agent switcher if agent has an active assigned plan

---

## Integration Tasks

- [ ] Swarm context injection: on swarm session start, read `plans.get()` for the active plan and prepend to group chat context — see `SWARM_COORDINATION_SPEC.md §23.7` for exact injection format
- [ ] `POLLY_IOS_SPEC.md §23` cross-reference review before implementation begins: confirm RPC signatures match spec

---

## Done When

`plans.list`, `plans.get`, `plans.create`, `plans.update` working end-to-end. Plans View renders plan list and detail. Task checkboxes work. @qa_guy sign-off.

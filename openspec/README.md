# OpenSpec in Polly

**We develop Polly using OpenSpec.** All feature work and non-trivial changes follow the OpenSpec workflow: proposal → design → tasks → implement → update specs. This is the required development process for this repo (not just documentation).

**[OpenSpec](https://github.com/Fission-AI/OpenSpec)** (Fission-AI) is a spec-driven framework: we align on requirements in `openspec/` before and while writing code, and keep specs as the source of truth alongside the repo.

## Layout

- **`specs/`** — Source of truth for current behavior, by domain.
  - **`specs/overview/spec.md`** — System overview and index of all domains.
  - **`specs/project/status.md`** — **Project status** (single source of truth for "where we are").
  - **`specs/project/roadmap.md`** — **Roadmap** (tiers and phases; what to build next).
  - **Domain specs:** architecture, design, ui, rag, personas, domains, notes, curriculum, teaching, patterns, mental-models, integrations, security (see [INDEX.md](INDEX.md) or [specs/overview/spec.md](specs/overview/spec.md)).
- **`DOCUMENTATION_MAP.md`** — Maps every existing project doc to the spec(s) it feeds or to backlog/ops.
- **`changes/`** — One folder per active change; each can have `proposal.md`, `design.md`, `tasks.md`, and `specs/` (deltas).
- **`config.yaml`** — Project context (tech stack, conventions) and per-artifact rules.

## Project tracking (OpenSpec-first)

Status and roadmap live in OpenSpec so development stays spec-driven:

- **What's the current status?** → [specs/project/status.md](specs/project/status.md)
- **What should we build next?** → [specs/project/roadmap.md](specs/project/roadmap.md)
- **Detailed phase docs** (reference) → [docs/planning/phases/](../docs/planning/phases/), [archive/root-docs/MASTER_ROADMAP.md](../archive/root-docs/MASTER_ROADMAP.md)
- **Completion history** → [docs/status/CHANGELOG.md](../docs/status/CHANGELOG.md)

## Workflow (OPSX)

Use OpenSpec’s OPSX workflow for new work:

1. **Create a change** — e.g. `/opsx:new` or manually add a folder under `changes/<change-name>/` with `proposal.md`.
2. **Implement** — Use `design.md` and `tasks.md`; implement in the codebase.
3. **Update specs** — Adjust `specs/` to match new behavior; add deltas under `changes/<change-name>/specs/` if useful.
4. **Archive** — When done, archive the change (e.g. `/opsx:archive`) or move to docs and remove from `changes/`.

## CLI (optional)

To use the OpenSpec CLI (e.g. `openspec init` was already run; to re-run or use other commands):

- **Requires:** Node.js 20.19.0+
- **Install:** `npm install -g @fission-ai/openspec@latest`
- **Or run without install:** `npx openspec@latest <command>`

If `npx` fails due to npm cache permissions, fix with:  
`sudo chown -R $(whoami) ~/.npm`

## References

- [OpenSpec GitHub](https://github.com/Fission-AI/OpenSpec)
- [OpenSpec docs](https://openspec.dev/)  
- Polly status: [specs/project/status.md](specs/project/status.md) (authoritative)  
- Polly roadmap: [specs/project/roadmap.md](specs/project/roadmap.md) (authoritative)  
- Detailed reference: [docs/status/CURRENT.md](../docs/status/CURRENT.md), [archive/root-docs/MASTER_ROADMAP.md](../archive/root-docs/MASTER_ROADMAP.md)

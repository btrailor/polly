# Pure User-Defined Domains — Design Exploration

**Created:** February 2026  
**Context:** The five built-in domains (Sigils, Signals, Scrolls, Glyphs, Grids) are one user's structure and may feel esoteric to general users. This doc explores what it would take to make domains **purely user-defined**: no hardcoded list, no required "built-ins."

---

## Target state (summary)

- **No built-in domain list.** Domains come only from `domains.json` (Settings UI / API) or optional config YAML. No `DomainType` enum in the public API; domain identity is always **string id** (e.g. `work`, `sigils`, `my-research`).
- **First-run:** Either start with **empty** domains (user adds all) or a **template choice**: e.g. "Polly Five" (current five as a template), "Quick Start" (Work / Personal / Learning), or "Start from scratch." Template writes to `domains.json`; no code path assumes the five exist.
- **Detection and prompts** work over whatever domains the user has defined. No special-casing of "the five."

---

## Current coupling to the five

| Area | How it's coupled | Change needed |
|------|------------------|---------------|
| **DomainEngine** | `DomainType` enum; `DEFAULT_DOMAINS` dict; `self.domains: Dict[DomainType, Domain]`; `_custom_domains` for "other" ids | Single store keyed by string id: `Dict[str, Domain]` or `List[Domain]` with `domain.id`. No enum. |
| **Detection** | `_score_domains` returns `Dict[DomainType, float]`; `detect_domains()` returns `List[DomainType]` | Score and return **string ids**. `detect_domains()` → `List[str]`. |
| **domain_config** | `_create_default_domains()` seeds the five when domains.json is missing | First-run: no file → empty list or **template choice** (Polly Five / Quick Start / Empty). Templates are data (e.g. JSON in repo or domain_config), not code that "always gives five." |
| **DOMAIN_PROMPTS** | Hardcoded dict `DomainType → prompt text` for the five | Either remove and use only each domain's `description` (or generic prompt), or add optional `systemPrompt` (or `promptSnippet`) per domain in domains.json and use that. |
| **Polly / RAG / patterns** | Use `detected_domains` and call `.value` or compare to `DomainType.UNKNOWN` | Consume `List[str]` (domain ids). "Unknown" → empty list or a single sentinel id like `"unknown"` if you still need one. |
| **Tests** | Many assume five domains, `DomainType.SIGILS`, etc. | Update to string ids and/or fixture domains.json. |

---

## Domain model (unified)

- **Domain** (in core): `id: str`, `name`, `description`, `keywords`, `patterns`, `paths`, optional `color`, `icon`, `folder_path`, optional `rag_collections`, optional `system_prompt` (for DOMAIN_PROMPTS replacement). No `type: DomainType`; no `custom_id` (everything is "custom" in the sense of user-defined).
- **Storage:** Same as today: `domains.json` (domain_config) and optional config YAML. Schema already supports arbitrary ids; we just stop treating five ids as special.

---

## First-run behavior

**Option A — Empty by default**  
- No `domains.json` → `load_domains()` returns config with `domains: []`. DomainEngine has no domains; detection returns `[]` (or `["unknown"]`). UI shows "Add your first domain" in Settings.

**Option B — Template choice (recommended)**  
- On first launch (no `domains.json`), show a one-time choice (or Settings "Domains" first visit):
  - **"Use Polly's default set"** → Write Polly Five (Sigils, Signals, Scrolls, Glyphs, Grids) to domains.json.
  - **"Quick start (3 domains)"** → Write Work / Personal / Learning to domains.json (reuse existing `create_quick_start_domains()`).
  - **"Start from scratch"** → Create empty domains.json.
- After that, everything is editable/deletable; no "protected" built-ins.

**Option C — Polly Five as default without asking**  
- Same as today: first run creates domains.json with the five. User can delete or rename. Minimal code change but keeps "your" structure as the default for everyone.

Recommendation: **Option B** so general users can pick a neutral Quick Start or empty, while existing users can keep or adopt Polly Five as a template.

---

## API and code changes (high level)

1. **core/domains.py**
   - Remove or deprecate `DomainType` enum from the **public** API (keep internally only if needed for a transition period).
   - Replace `DEFAULT_DOMAINS` with "no defaults"; fallback when domains.json is missing is either empty or a chosen template (written to file).
   - Store: `self._domains_by_id: Dict[str, Domain]` (or list; lookup by id). All domains, including former "built-ins," are in this store.
   - `Domain`: add `id: str` (required); remove `type: DomainType` and `custom_id` (id is the only identity).
   - `detect_domains()` → `List[str]`. `detect_domains_with_scores()` → `List[Tuple[str, float]]`.
   - `get_domain_prompt(domain_ids: List[str])`, `filter_sources_by_domain(..., domain_ids: List[str])`. Look up by id from `_domains_by_id`.
   - `DOMAIN_PROMPTS`: remove or replace with per-domain optional prompt in config; if missing, use description or a single generic line.

2. **core/domain_config.py**
   - `load_domains()`: when file missing, return config with `domains: []` (Option A) or do not create file and let first-run UI call a "apply template" endpoint (Option B).
   - `_create_default_domains()` → rename to e.g. `get_polly_five_template()` and use only when user explicitly chooses that template; same for `create_quick_start_domains()`.

3. **core/polly.py**
   - Replace `DomainType` usage with string ids: `domain_names = detected_domains` (already list of str), remove `if d != DomainType.UNKNOWN`, use `if not domain_names` or similar.
   - Any `domain_values`, `domain_names` already end up as strings; just ensure `detect_domains()` returns `List[str]`.

4. **RAG, patterns, entities**
   - Already use domain **strings** in most places; audit for any `DomainType` comparison or `.value` and switch to str.

5. **Electron / Settings**
   - First-run: if no domains, show template choice (or "Add your first domain") and optionally call e.g. `POST /polly/domains/apply-template` with `{ "template": "polly_five" | "quick_start" | "empty" }`.
   - No "built-in" vs "custom" distinction in the UI unless you want a label like "From template" for clarity.

6. **Tests**
   - Fixture: small `domains.json` or in-memory list of domains with string ids.
   - Replace `DomainType.SIGILS` with `"sigils"` (or fixture id) everywhere.

---

## Migration for existing users

- **Existing domains.json** with the five (and any custom) already use string ids. After the change, DomainEngine loads them by id; no enum. So existing files keep working.
- **Code that passes DomainType** (e.g. tests or scripts): update to pass string id. One-time migration.

---

## Effort (rough)

| Phase | Work | Risk |
|-------|------|------|
| 1. DomainEngine internal | Single store by id; detection returns `List[str]`; remove DEFAULT_DOMAINS fallback; templates for first-run | Medium — many call sites |
| 2. Polly + RAG + patterns | Use `List[str]` only; remove DomainType imports and UNKNOWN checks | Low |
| 3. domain_config | First-run = empty or template; rename default → template | Low |
| 4. DOMAIN_PROMPTS | Per-domain optional prompt or generic only | Low |
| 5. Frontend first-run | Template choice modal or Settings empty state | Small |
| 6. Tests | String ids and fixtures | Medium |

Overall: **moderate refactor** (1–2 days of focused work), mostly in `core/domains.py` and call sites. No change to the domains.json schema or Settings CRUD; only to how the engine and first-run behave.

---

## Recommendation

- **Do it** if you want Polly to feel like a general-purpose tool where domains are fully user-defined and the current five are an optional template.
- **Phased approach:** (1) Implement single store by id and `detect_domains() -> List[str]` while keeping DomainType internally as a compatibility layer (map enum to id where needed); then (2) remove enum and DEFAULT_DOMAINS; then (3) add first-run template choice in the app.

This doc can be turned into a concrete task list (e.g. in `tasks.md`) when you decide to proceed.

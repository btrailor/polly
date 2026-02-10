# Custom Domains Feature — Design

**Created:** February 2026

---

## Current state

### Backend

- **`~/.polly/domains.json`** (domain_config): Full CRUD via API. Each domain has: id, name, description, color, icon, folderPath, ragWeight, autoTagRules, order, etc.
- **DomainEngine** load order: (1) config YAML `domains:` if present → (2) `load_domains()` (domains.json) → (3) hardcoded defaults.
- When loading from **domain_config** (`_load_from_domain_config`): only domains whose **id** is in the `DomainType` enum are kept; others are **skipped** with a warning. So UI-added domains (e.g. id `work`, `my-domain`) are saved but never used.

### Frontend

- **Settings → Domains** tab: list of domains, "Add domain" button, edit/delete per domain, drag-to-reorder, folder numbering toggle.
- **Add domain:** user enters name, description, folder path, weight, keywords (autoTagRules); **id** is auto-generated from name: `name.toLowerCase().replace(/[^a-z0-9]/g, '-')`. So "My Work" → `my-work`. No explicit "custom" vs "built-in" label; all domains look the same.
- **API:** POST /polly/domains accepts any `id`; PUT/DELETE by id. No restriction that id must be one of the five.

### Gap

- Custom domains (any id not in enum) are **persisted** but **not loaded** into DomainEngine. So detection, RAG weighting, prompts, and notes organization only see the five enum domains (or whatever is in YAML if used).

---

## Target state

### 1. Single source of truth for UI-defined domains

- **domains.json** remains the source for everything the user does in Settings (add/edit/delete/reorder). No change to API or file format.
- **DomainEngine** when loading from domain_config:
  - For each domain in config.domains:
    - If `domain_cfg.id` is in `DomainType` (and not UNKNOWN): map to `Domain(type=enum, ...)` and put in `self.domains`.
    - Else: create `Domain(type=UNKNOWN, custom_id=domain_cfg.id, name=..., keywords=auto_tag_rules, ...)` and append to **`self._custom_domains`**.
  - Do **not** skip custom ids.

### 2. Use of custom domains in the engine

- **Detection:** Extend `_score_domains` to score `self._custom_domains` the same way (keyword match, etc.). Then either:
  - **Option A:** `detect_domains()` continues to return `List[DomainType]` only (custom domains not returned). Custom domains are still "loaded" for future use (e.g. notes, RAG by id).
  - **Option B:** Add `detect_domains_with_custom()` returning `(List[DomainType], List[str])` so callers can pass custom ids to RAG/prompts. Polly and RAG would need to accept domain **strings** (e.g. sigils, work) in addition to enum.
- **Recommendation for this change:** Implement **Option A** in code (load custom domains, no detection API change). Document **Option B** as a follow-up so detection and prompts can include custom domain labels.

### 3. Frontend (no required code change for "feature on")

- Existing UI already allows adding any domain; id is derived from name. Only backend fix is required for those domains to be loaded.
- **Optional UX improvements** (can be same or later PR):
  - **Reserved ids:** When creating a new domain, if generated id is one of `sigils`, `signals`, `scrolls`, `glyphs`, `grids`, show a hint: "This ID is used by a built-in domain; consider a different name" or auto-append a suffix (e.g. `work-sigils` → avoid overwriting).
  - **Expose ID in editor:** Optional read-only or editable "ID" field in the domain editor so power users see the slug (and can avoid collisions).
  - **Label in list:** Optionally show a "Custom" badge on domains that are not one of the five, to clarify which are built-in vs user-added.

### 4. Config YAML vs domains.json

- **Polly init:** We pass `config_dict={"domains": self.config.domains}` only when the app config (e.g. config.yaml) has a non-empty `domains` key. So if the user never touches config YAML, `config_dict` is still `{"domains": {}}` (empty) and DomainEngine falls through to **domains.json**. So Settings-driven domains all live in domains.json and are now loaded.
- **If both exist:** Today, YAML wins (first in load order). So power users can override via YAML; normal users use only Settings → domains.json. No merge in this change.

---

## Implementation summary

1. **DomainEngine._load_from_domain_config**
   - Remove the "skip if id not in DomainType" behavior.
   - For each domain_cfg: if id in DomainType → `self.domains[type] = Domain(...)`; else → `self._custom_domains.append(Domain(type=UNKNOWN, custom_id=id, ...))`.
   - Initialize `self._custom_domains = []` at start of __init__ when using domain_config path (already done for YAML path).

2. **DomainEngine.__init__** (domain_config path)
   - Ensure after `self.domains = self._load_from_domain_config(...)` we also set `self._custom_domains` from the same method. So _load_from_domain_config should return `(Dict[DomainType, Domain], List[Domain])` when we want custom domains, or we keep a separate method that builds both. Easiest: change _load_from_domain_config to return `(domains, custom_list)` and have the domain_config path assign both.

3. **Optional:** Add `detect_domains_with_custom()` and wire custom domain scores in _score_domains (and optionally in detect_domains return). Defer if we want a minimal first step.

4. **OpenSpec / docs:** Update domains spec to state that custom domains (any id in domains.json) are loaded and stored in DomainEngine._custom_domains; detection inclusion is a follow-up.

---

## Files to touch

| File | Change |
|------|--------|
| `core/domains.py` | _load_from_domain_config: return (domains, custom); load custom ids into _custom_domains. __init__ domain_config branch: set _custom_domains from return value. |
| `openspec/specs/domains/spec.md` | Add line that custom domains from domains.json are loaded and available (and detection inclusion planned). |
| `electron-app/` | Optional: reserved-id hint or ID field in domain editor (separate task if desired). |

---

## Verification

- Add a domain "Work" in Settings (id will be `work`). Restart or trigger reload of domains.
- In Python: `DomainEngine()` with no config_dict (so it uses domains.json). Assert `engine._custom_domains` contains one Domain with `custom_id == "work"`.
- Existing tests that use DomainEngine() with default domains.json (or no file) should still pass; if domains.json has only the five, custom list is empty.

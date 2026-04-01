# Domain Flexibility — Tasks

**Status:** ✅ Spec edits complete  
**Source:** `DOMAIN_FLEXIBILITY_SPEC_REMEDIATION.md`

## P0 — Phase 1 (must ship before mental model suggestion feature)

### iOS Client
- [x] `UserDomain` interface: add `suggested_mental_models?: string[]` — `POLLY_IOS_SPEC.md §20.3`
- [x] `UserDomain` interface: add `default_sensibility?: string` — `POLLY_IOS_SPEC.md §20.3`
- [ ] [@frontend] Mental model suggestion sheet: read `suggested_mental_models` from matched `UserDomain` record — replace any hardcoded lookup with data-driven read
- [ ] [@frontend] First-run domain seeding: pre-populate `polly.domains` with default starter domain records including `suggested_mental_models` values (see `design.md` table)
- [ ] [@frontend] Graceful degradation: if `suggested_mental_models` absent or empty, show full list only (no crash, no empty section header)

### Spec Files (already applied)
- [x] `POLLY_IOS_SPEC.md §11.3` — removed hardcoded domain→model table; replaced with dynamic behavior description + NOTE on starter defaults
- [x] `POLLY_IOS_SPEC.md §20.3` — `UserDomain` interface extended with two new optional fields

## P1 — Annotated, No Phase 1 Block

### Spec Files (already applied)
- [x] `SENSIBILITY_SYSTEM_SPEC.md` Phase 4 bullet — NOTE callout added: auto-switching reads `default_sensibility` from `UserDomain`; examples are personal config, not app defaults

### iOS Client (Phase 4)
- [ ] [@frontend] Sensibility auto-switch engine: read `default_sensibility` from matched `UserDomain` on domain detection event; apply sensibility if field is non-null

## P2 — Documentation Clarification (already applied)

- [x] `PRACTICE_LAYER.md §2` — NOTE callout added: domain names in examples are personal config; system is name-agnostic

## Verification

Run after implementation:
```
grep -n "Sigils\|Scrolls\|Glyphs\|Grids" POLLY_IOS_SPEC.md
```
Should return zero results in behavioral/logic sections. Results only acceptable inside NOTE callouts or comments.

```
grep -n "Sigils\|Scrolls\|Glyphs\|Grids" SENSIBILITY_SYSTEM_SPEC.md
```
Should return only the NOTE callout line.

## Done When
`UserDomain` interface extended. Mental model suggestions data-driven from `suggested_mental_models`. First-run domain seeding ships default starters with sensible values. Hardcoded table fully removed from iOS implementation. No domain name string appears in app logic.

# Domain Flexibility — Proposal

**Phase target:** Issue 1 (P0) → Phase 1. Issues 2–3 → annotated now, no Phase 1 block.  
**Status:** ✅ Complete — all edits applied  
**Specs modified:**  
- `POLLY_IOS_SPEC.md` §11.3 (mental model suggestion table replaced) + §20.3 (UserDomain interface extended)  
- `SENSIBILITY_SYSTEM_SPEC.md` Phase 4 section (NOTE callout added)  
- `PRACTICE_LAYER.md` §2 (NOTE callout added)  

**Source:** `DOMAIN_FLEXIBILITY_SPEC_REMEDIATION.md`  
**@design_eng review needed?** No — no visual behavior changed; the suggestion sheet still works identically, data source changes.  
**@backend review needed?** No — MMKV key `polly.domains` and storage model unchanged; two new optional fields added to schema.  
**@security_audit review needed?** No — no new persistence, no new network.  

## Root Cause

Three places in legacy spec files used Brett's personal domain taxonomy (Sigils / Signals / Scrolls / Glyphs / Grids) as if it were canonical app logic. A user with different domain names would get broken mental model suggestions (Issue 1, P0) and confusing Phase 4 sensibility auto-switching behavior (Issue 2, P1). Issues 3 is a documentation clarity fix.

## What Was Fixed

| Issue | Severity | Status |
|-------|---------|--------|
| §11.3 hardcoded domain→model table | P0 / CRITICAL | ✅ Fixed |
| §20.3 UserDomain missing `suggested_mental_models` + `default_sensibility` | P0 (schema) | ✅ Fixed |
| SENSIBILITY_SYSTEM_SPEC.md Phase 4 literal name examples | P1 / annotated | ✅ Noted |
| PRACTICE_LAYER.md domain name examples read as structural | P2 / doc clarification | ✅ Noted |
| DREAM_LOGIC.md — no domain names found | N/A | No edit needed |

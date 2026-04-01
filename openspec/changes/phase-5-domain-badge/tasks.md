# Phase 5: Domain Awareness Badge

**Status:** 📋 Not yet decomposed  
**Spec source:** `POLLY_IOS_SPEC.md §11.2`, `§13 Phase 5`  
**Depends on:** `domain-flexibility` (Phase 1 domain data model)  
**Added:** 2026-04-01 — placeholder created via OpenSpec Task Coverage Audit

## What This Is

Client-side keyword classification of incoming messages → colored domain badge in chat header. User-configurable domain taxonomy. Defined in `§11.2`.

The `domain-flexibility` change folder handles `suggested_mental_models` and sensibility per-domain but does **not** cover the badge UI or keyword classifier. Those live here.

## Tasks (to be decomposed at Phase 5 planning)

- [ ] Keyword classifier: client-side, deterministic, maps message content to domain taxonomy entry
- [ ] Domain taxonomy: user-configurable list (stored in MMKV), default taxonomy from spec
- [ ] Domain badge component: colored chip in chat header, reflects current domain
- [ ] Settings screen for domain taxonomy management

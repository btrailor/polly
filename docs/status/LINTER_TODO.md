# Linter / type-checker cleanup (TODO)

**Purpose:** Track known linter (basedpyright) messages so we can fix them in a later pass.

**Last updated:** February 2026

---

## interfaces/server.py

| Line(s) | Issue | Notes |
|---------|--------|--------|
| 2094, 2098 | `ObsidianIntegration` is not defined | Type/import missing or incorrect in scope where it's used |
| 4403 | `polly` is not defined | Variable used outside the scope where `get_polly()` is called |
| 5184 (×3), 5194 | `polly` is not defined | Same: `polly` referenced where it may be out of scope |

**Suggested fixes (when tackling):**
- **ObsidianIntegration:** Ensure the class is imported or defined in the module (or use a forward reference / TYPE_CHECKING if it's in another module).
- **polly:** In each route/handler, ensure `polly = get_polly()` is called in that handler’s scope before any use of `polly` (or pass it in from a shared scope if the app structure allows).

---

*Remove or update this file as issues are resolved.*

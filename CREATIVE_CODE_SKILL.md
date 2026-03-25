# CREATIVE_CODE_SKILL.md
*Phase 3 — Sandboxed Generative Code Execution*
*Status: Planned (blocked: depends on skill runner + @design_eng token schema)*
*Owners: @backend (sandbox, skill runner integration), @security_audit (import whitelist, SVG sanitization), @design_eng (token injection)*
*Last updated: 2026-03-25*

---

## 1. What This Is

A skill that generates and executes creative code — Paper.js, svg.js, D3 — in a sandboxed subprocess, with theme token injection and SVG output delivered to the asset library.

The use cases are:
- **Icons** — generated SVG icons in Polly's design language
- **Slide graphics** — data visualization and layout for presentations
- **Agent avatars** — generative avatar imagery
- **Generative backgrounds** — procedural patterns in the system aesthetic
- **Data viz** — D3-powered charts from Brett's data

This is a creative tool, not a general code execution environment. The whitelist is tight, the output contract is strict, and the sandbox is mandatory.

---

## 2. Permitted Libraries (Whitelist)

| Library | Version constraint | Use |
|---------|-------------------|-----|
| `paper.js` | `^0.12` | Vector graphics, path manipulation |
| `svg.js` | `^3.1` | SVG construction and animation |
| `d3` | `^7.0` (core only) | Data visualization |
| `chroma-js` | `^2.4` | Color manipulation |

**All other imports are rejected at the resolver level.** `require()` and `import` for anything not on this list fails at parse time, before execution. This is enforced by the sandbox's module resolver, not by runtime detection.

---

## 3. Theme Token Injection

Before execution, the skill injects Polly's design tokens as globals:

```javascript
// Injected automatically — not in the generated code
const THEME = {
  colors: {
    background: "#0c1323",
    surface: "#131d30",
    text: "#e8eaf0",
    accent: "#7c6aff",
    // ... full token set from src/theme/colors.ts
  },
  typography: {
    // font stack, scale
  },
  spacing: {
    // spacing scale
  }
};
```

Generated code accesses `THEME.*` for all design values. This ensures generated assets are always on-brand without the LLM needing to know the exact hex values.

**@design_eng dependency:** The token schema JSON must be available for injection. This is the blocking dependency — `CREATIVE_CODE_SKILL.md` cannot be implemented until @design_eng delivers the token schema.

---

## 4. Output Contract

All output must be valid SVG. The skill runner:

1. Executes the generated code in the sandbox
2. Captures SVG output (either from `paper.exportSVG()`, `svg.js` serialization, or D3 SVG node)
3. **Sanitizes the SVG** before any further processing:
   - Strip all `<script>` elements
   - Strip all `javascript:` hrefs
   - Strip all event handlers (`onclick`, `onload`, etc.)
   - Strip all `<use>` elements referencing external URLs
4. Delivers sanitized SVG to the asset library staging queue (ASSET_STATE_MACHINE.md flow)

The sanitization pass is mandatory and runs on every output regardless of whether the generated code looks safe. Defense in depth.

---

## 5. Security Requirements (@security_audit)

Four constraints, all mandatory:

1. **Import whitelist enforced at resolver level** — rejected at parse time, before execution. Not a runtime check.
2. **SVG output sanitized before client** — strip `<script>`, `javascript:` hrefs, event handlers, external `<use>` refs. Runs on every output.
3. **Subprocess CPU/memory hard limits** — 5-second execution timeout, 256MB memory ceiling. Process killed on breach, no partial output delivered.
4. **Output path confinement** — generated files written only to the skill's designated output directory. No filesystem access outside that path.

@security_audit review required before Phase 3 implementation begins.

---

## 6. Asset Library Integration

Generated assets enter the ASSET_STATE_MACHINE.md staging flow:

```
generated → staging (auto) → review (Brett) → approved/rejected → library
```

Brett reviews generated assets before they enter the library. No auto-approve. The review step is the human gate between generated code output and system assets.

---

## 7. FIGMA_INTEGRATION.md

Approved assets are available for Figma export via FIGMA_INTEGRATION.md. The pipeline:

```
Creative Code Skill → Asset Library → Figma Export
```

Generated icons and graphics become design tokens available in Figma. This is the integration that makes the skill useful beyond one-off generation.

---

## 8. Open Questions

**Q1 (blocking):** Token schema JSON from @design_eng. Format TBD — must be machine-readable for injection at skill runtime.

**Q2 (blocking):** Skill runner must support subprocess sandboxing (`sandbox-exec` + manifest-driven profile). See MCP_ADAPTER.md §5 for subprocess isolation model.

---

## 9. Dependencies

- **Blocking:** @design_eng token schema JSON
- **Blocking:** Skill runner subprocess sandboxing (MCP_ADAPTER.md)
- ASSET_STATE_MACHINE.md: staging → review → library flow
- FIGMA_INTEGRATION.md: export pipeline
- @security_audit review pass (4 constraints above)
- `src/theme/colors.ts`: source of truth for token values at injection time

---

*Cross-references: ASSET_STATE_MACHINE.md, FIGMA_INTEGRATION.md, MCP_ADAPTER.md, SKILLS_MARKETPLACE.md*

# Design: Aesthetic Theme Engine

## Architecture Impact

### New Subsystems

1. **Theme Engine** (`core/themes/`)
   - `loader.py` — Reads theme JSON files from `~/.polly/themes/`, resolves inheritance and user overrides
   - `registry.py` — Manifest of available themes, active theme tracking, schema validation
   - `composer.py` — Hybrid theme composition, conflict detection, provenance tracking
   - `persona_adapter.py` — Translates behavior layer into persona system prompt modifiers
   - `schema.py` — Theme JSON schema definition and validation

2. **Theme Storage** (`~/.polly/themes/`)
   - Seven built-in theme JSON files (copied from bundled defaults on first run)
   - `custom/` directory for user-composed hybrids
   - `manifest.json` — registry of available and active themes

3. **Frontend Theme Layer** (`electron-app/src/renderer/themes/`)
   - CSS custom property generation from theme presentation layer
   - Theme switcher component (Settings page and command palette)
   - Composition matrix UI (Settings page)
   - Live preview rendering

### Existing System Extensions

| System           | Extension                                                                                                                                                                                                            |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Personas**     | `BasePersona` gains `apply_theme_behavior(theme)` method. Theme behavior layer injected into system prompt construction as weighted defaults. Priority: user instruction > task requirements > theme > persona base. |
| **UI / CSS**     | Current hardcoded CSS variables replaced with theme-driven custom properties. Existing Obsidian-inspired aesthetic becomes a base that themes modify.                                                                |
| **Settings**     | New "Themes" section: theme browser with cards, live preview, composition matrix for hybrids, import/export.                                                                                                         |
| **Config**       | `config/config.yaml` gains `theme` section with `active_theme`, `custom_themes_dir`, and `theme_defaults`.                                                                                                           |
| **Agent Swarms** | Theme behavior layer propagates through Nexus to agents. Theme metadata included in agent execution context.                                                                                                         |

### Backend Implementation

**Theme loading flow:**

1. On startup, `ThemeRegistry` scans `~/.polly/themes/` for valid theme JSON files
2. Active theme loaded from user config (`config.yaml` or electron-store)
3. `ThemeLoader` resolves full theme object (base theme + user overrides)
4. `PersonaAdapter` extracts behavior properties for each persona type
5. Persona system prompt construction includes theme behavior as context section

**Persona integration:**

```
System prompt = [
  base_persona_prompt,
  active_mode_instructions,
  theme_behavior_context,    # NEW: "Your aesthetic orientation: {theme.core_principle}..."
  active_skills,
  user_instructions
]
```

The theme behavior context is a structured addition to the system prompt, not a replacement. It provides weighted defaults the persona considers but does not mandate. Example for Ghost Box + Scribe:

> Aesthetic context (Ghost Box): Your voice tends toward the allusive and indirect. Work from impression rather than direct reference. Written structure follows found-document logic. When organizing, favor archival filing patterns.

**Theme switching:**

- API endpoint `POST /themes/switch` updates active theme
- Server broadcasts theme change to connected clients via existing WebSocket
- Frontend receives new theme, regenerates CSS custom properties
- Subsequent persona calls use new theme behavior (no retroactive changes)

### Frontend Implementation

**CSS custom property mapping:**
Each presentation layer property maps to one or more CSS custom properties:

```css
/* Generated from theme.presentation.palette */
--polly-bg: #f8f6f3;
--polly-primary: #2d2d2d;
--polly-accent: #3a6b9f;
--polly-surface: ...;

/* Generated from theme.presentation.typography */
--polly-font-body: "Fira Code", monospace;
--polly-font-heading: "Fira Code", monospace;
--polly-tracking: -0.01em;

/* Generated from theme.presentation.spacing */
--polly-grid-module: 8px;
--polly-density: compact;

/* Generated from theme.presentation.chrome */
--polly-border-radius: 0px;
--polly-border-style: none;
```

**Theme switcher UI:**

- Card grid in Settings showing theme name, artist, core principle, palette preview
- Click to preview (applies temporarily), confirm to switch
- Composition tab: drag properties between themes to build hybrid
- Export/import buttons for sharing themes

### Data Storage

| Location                        | Content                                                  |
| ------------------------------- | -------------------------------------------------------- |
| `~/.polly/themes/*.json`        | Theme definition files (built-in + custom)               |
| `~/.polly/themes/custom/`       | User-composed hybrid themes                              |
| `~/.polly/themes/manifest.json` | Registry: available themes, active theme, schema version |
| `config/config.yaml` → `theme`  | Active theme name, custom dir path, defaults             |

### API Endpoints

| Endpoint                    | Method | Description                                         |
| --------------------------- | ------ | --------------------------------------------------- |
| `GET /themes/list`          | GET    | All available themes with metadata                  |
| `GET /themes/active`        | GET    | Current resolved theme (base + overrides)           |
| `POST /themes/switch`       | POST   | Switch active theme by name                         |
| `POST /themes/compose`      | POST   | Create hybrid from source themes                    |
| `GET /themes/export/:name`  | GET    | Export theme as standalone JSON                     |
| `POST /themes/import`       | POST   | Import theme from JSON, validate schema             |
| `GET /themes/preview/:name` | GET    | Theme presentation properties only (for UI preview) |

### Dependency Order

```
1. Theme schema + JSON files (no code dependencies)
2. ThemeRegistry + ThemeLoader (reads files, validates)
3. PersonaAdapter (integrates with existing persona system)
4. API endpoints (standard FastAPI pattern)
5. CSS custom property generation (frontend)
6. Settings UI — theme browser (frontend)
7. Composition engine (backend + frontend)
8. Cross-domain ripple + agent swarm propagation
```

## Design Principles Applied

- **Operational aesthetics** (new): Themes alter decision-making, not just appearance
- **Progressive revelation**: Default theme works immediately; customization available in Settings
- **Intelligent defaults**: Reas theme as structurally neutral default; works well with no configuration
- **Domain permeability**: Theme effects ripple across all five domains via persona behavior layer
- **Continuation over completion**: Themes support ongoing exploration (daily practice, theme sequences, constraint rotation)

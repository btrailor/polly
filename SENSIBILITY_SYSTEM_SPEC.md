# SENSIBILITY_SYSTEM_SPEC.md

Phase 1–4 — The Aesthetic and Structural Engagement Layer  
Status: Draft  
Owners: @code_architect (architecture), @design_eng (token definitions), @frontend (iOS rendering), @backend (behavior injection)  
Last updated: 2026-03-25  
Cross-references: `POLLY_IOS_SPEC.md` §19; `CREATIVE_CONSTRAINT_ENGINE.md`; `specs/agent-system/spec.md` (sensibility schema); `KNOWLEDGE_SERVICE_CONTRACTS.md` (prompt injection hierarchy); `MODEL_ROUTING_SPEC.md` (token cost implications); `POLLY_AGENT_TEMPLATES.md` (SOUL baseline)

---

## 1. What This Document Does

`POLLY_IOS_SPEC.md §19` covers 7 artist-referenced themes, behavior injections, artifact aesthetics, a composability system, texture overlays, and the `useTheme()` hook. `CREATIVE_CONSTRAINT_ENGINE.md` adds a structural layer. The agent-system spec adds a sensibility schema.

These three specs don't agree on architecture, and the current codebase uses a different system entirely. This document reconciles them into a single implementable design and identifies every gap.

---

## 2. What Exists vs. What's Specced

### 2.1 The Current Implementation

`src/theme/colors.ts` (249 lines) implements:
```typescript
export const colors = { accent: '#f0903b', bgPrimary: '#020617', ... };
export const typography = { body: { fontSize: 17, ... }, ... };
export const spacing = { ... };
export const layout = { minTouchTarget: 44, ... };

export const dark = colors;
export const light = { bgPrimary: '#FFFFFF', ... };
export function useColors() {
  const scheme = useColorScheme();
  return scheme === 'dark' ? dark : light;
}
```

**Key facts:**
- There is no `ThemeContext` or `ThemeProvider`
- There is no `useTheme()` hook
- There is no concept of sensibilities (Reas, Fidenza, Ghost Box, etc.)
- Dark/light is the only axis — handled by `useColorScheme()` (system setting)
- Components cast `(colors as any).bgPrimary` — type system doesn't match actual shape
- The `light` export has different field names than `dark` (`bgTertiary`, `bgElevated`, `accentGreen` — none of which exist in dark mode)
- Typography, spacing, and layout are not theme-aware — static regardless of sensibility

### 2.2 What §19 Specifies

A `ThemeTokens` interface with ~25 fields covering color, shape, typography, texture, motion, and chrome. Seven complete theme definitions (Reas, Fidenza, Ghost Box, Martens, Jetset, Riley, Albers). A `ThemeContext` + `ThemeProvider` + `useTheme()` hook. Behavior injection via `config.patch`. Artifact aesthetics per theme. Phase 4 composability with 3 sliders.

### 2.3 What the Agent System Spec Adds

A sensibility schema on each agent definition:
```json
{
  "sensibility": {
    "aesthetic": { "register", "vocabulary", "compression" },
    "structural": { "mode", "rules", "activation" }
  }
}
```

The aesthetic layer maps to §19's behavior injection. The structural layer maps to `CREATIVE_CONSTRAINT_ENGINE.md`.

### 2.4 The Conflicts

| Aspect | Current code | §19 spec | Agent system spec |
|--------|-------------|----------|-------------------|
| Theme scope | System dark/light | Global sensibility (Reas, Fidenza, etc.) | Per-agent aesthetic + structural |
| Token shape | Flat `colors` + separate `typography` | Unified `ThemeTokens` interface | Not addressed |
| Hook | `useColors()` → dark or light | `useTheme()` → `{ tokens, activeTheme, setTheme }` | Not addressed |
| Provider | None | `ThemeContext` + `ThemeProvider` | Not addressed |
| Storage | System setting | MMKV `polly.sensibility` | Per-agent in agent manifest |
| Behavior injection | None | `config.patch` on `polly.ios.aestheticStance` | `sensibility.aesthetic` fields on agent definition |
| Structural rules | None | None (§19 is aesthetic only) | `sensibility.structural` with mode, rules, activation |
| Typography per theme | Not supported | Per-theme `fontBody`, `fontHeading`, `letterSpacing` | Not addressed |
| Texture overlays | Not supported | 6 PNG textures, per-theme opacity | Not addressed |
| Bubble styles | Static (rounded) | 7 styles | Not addressed |

---

## 3. The Unified Architecture

### 3.1 Two Orthogonal Axes

**Axis 1: Visual Theme (iOS presentation layer)**  
Controls how the app looks. Color tokens, typography, corner radii, textures, bubble styles, motion curves. Client-side concern — no gateway involvement.

**Axis 2: Behavioral Stance (agent prompt injection layer)**  
Controls how agents think and write. Tone, register, vocabulary, structural rules, artifact aesthetics. Gateway-side concern — injected via `config.patch`.

These two axes are correlated but independent. "Ghost Box" activates both the visual theme (scan-line textures, institutional typography) and the behavioral stance (allusive, archival, hauntological). But they can theoretically be decoupled.

**Phase 1–3:** Coupled. One sensibility choice activates both visual and behavioral.  
**Phase 4:** Decoupled. Composability sliders independently adjust visual and behavioral parameters.

### 3.2 The Token Architecture

Replace current `colors.ts` with a proper theme system:

```
src/theme/
  tokens.ts          — ThemeTokens interface + default theme (Reas)
  themes/
    reas.ts
    fidenza.ts
    ghostbox.ts
    martens.ts
    jetset.ts
    riley.ts
    albers.ts
  ThemeContext.tsx    — React Context + Provider
  useTheme.ts         — Consumer hook
  index.ts            — Re-exports
```

```typescript
// src/theme/tokens.ts
export interface ThemeTokens {
  // Identity
  id: string;           // "reas", "fidenza", etc.
  name: string;         // "Reas", "Fidenza", etc.
  artist: string;       // "Casey Reas", "Tyler Hobbs", etc.
  stance: string;       // one-line description

  // Color
  bgPrimary: string;
  bgSecondary: string;
  bgSurface: string;
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  accent: string;
  accentSecondary: string;
  border: string;

  // Semantic (explicit, not aliased)
  bubbleUser: string;
  bubbleAssistant: string;
  bubbleUserText: string;
  bubbleAssistantText: string;
  error: string;
  success: string;
  warning: string;

  // Shape
  radiusSm: number;
  radiusMd: number;
  radiusLg: number;
  radiusBubble: number;

  // Typography
  fontBody: string;
  fontMono: string;
  fontHeading: string;
  fontWeightHeading: string;
  letterSpacingBody: number;

  // Texture
  textureOverlay: 'grain' | 'canvas' | 'scan-lines' | 'dot-grid' | 'woven' | 'letterpress' | null;
  textureOpacity: number;

  // Motion
  transitionMs: number;
  transitionEasing: 'ease' | 'linear' | 'spring';

  // Chrome
  dividerStyle: 'line' | 'gap' | 'none';
  shadowStyle: 'soft' | 'sharp' | 'none';
  bubbleStyle: 'rounded' | 'square' | 'ribbon' | 'stamp' | 'minimal' | 'stripe-edge' | 'thread';
}
```

### 3.3 The Provider

```typescript
// src/theme/ThemeContext.tsx
interface ThemeContextValue {
  tokens: ThemeTokens;
  activeThemeId: string;
  setTheme: (id: string) => void;
  colors: Pick<ThemeTokens, /* color fields */>;
  typography: { body, heading, mono, ... };  // computed from tokens
  spacing: typeof spacing;  // static — not theme-dependent
  layout: typeof layout;    // static — not theme-dependent
}
```

**Key design decision:** `spacing` and `layout` are NOT theme-dependent. Touch targets, spacing scale, and list row heights don't change between sensibilities. Components that only need spacing/layout import those directly. Components that need color or shape use `useTheme()`.

### 3.4 Migration Path from Current Code

**Phase 1 (now):**
- Create `ThemeContext` + `ThemeProvider` + `useTheme()`
- Define Reas as default theme (token values matching current `colors.ts`)
- Replace all `useColors()` calls with `useTheme().tokens`
- Replace all `(colors as any).bgPrimary` casts with properly typed token access
- Delete `useColors()`, the `light` export, and the `semanticColors` alias layer
- All 7 theme files created (not selectable until Phase 3)

**Why Reas is the right default:** Current `colors.ts` values (`bgPrimary: '#020617'`, `accent: '#f0903b'`, `textPrimary: '#f8fafc'`) are closest to Reas's color scheme. Visual appearance barely changes — the architecture changes, not the look.

---

## 4. The Behavior Injection Pipeline

### 4.1 How It Works

1. iOS: user taps "Fidenza" in Settings → Sensibility
2. iOS: MMKV stores `polly.sensibility = "fidenza"`
3. iOS: `ThemeProvider` updates → all components re-render with Fidenza tokens (instant)
4. iOS: `config.patch({ "polly.ios.aestheticStance": fidenzaBehaviorInjection })`
5. Gateway: stores `aestheticStance` in config
6. Agent: next message includes `[AESTHETIC STANCE — Fidenza]` in system prompt at Layer 5
7. Agent: responds with warm-probabilistic tone and organic structure

Steps 1–3 are instant (client-side). Steps 4–5 happen over WebSocket. Step 6 takes effect on the next message.

### 4.2 Layer 5 — Two Injection Points

The Creative Constraint Engine adds structural rules as a separate injection at Layer 5:

```
Layer 5a: Aesthetic behavior injection  (Fidenza's warm-probabilistic tone)
Layer 5b: Structural rules injection    (Ghost Box fragment mode — per-agent, nullable)
```

Two `config.patch` keys:
- `polly.ios.aestheticStance` — global (applies to all agents)
- `polly.ios.structuralMode.{agentId}` — per-agent structural rules (nullable)

Example system prompt blocks:
```
[AESTHETIC STANCE — Fidenza]
Approach problems with probabilistic warmth...

[STRUCTURAL MODE — Fragment]
Refuses to complete arguments. Presents fragments and stops...

These stances influence your tone, structure, and engagement defaults.
They do not override explicit user instructions or constitutional commitments.
```

### 4.3 Per-Agent vs. Global

| Layer | Scope | Storage |
|-------|-------|---------|
| Visual theme | Global | MMKV `polly.sensibility` |
| Aesthetic behavior | Global (all agents) | Gateway `polly.ios.aestheticStance` |
| Structural rules | Per-agent | Gateway `polly.ios.structuralMode.{agentId}` |
| Artifact aesthetics | Global (injected with stance) | Part of `polly.ios.aestheticStance` text |

---

## 5. The Problems Nobody Has Addressed

### 5.1 Dark/Light Mode Is Gone

6 of 7 themes are dark-only. Jetset is the light option. The `light` export in `colors.ts` is deleted. The system appearance setting is ignored for theme colors.

**Exception:** If iOS "Increase Contrast" or "Bold Text" accessibility settings are enabled, Polly respects those by increasing text contrast ratios within the active theme — accessibility override, not a light mode.

**Documentation in picker:** "Polly themes are dark by default. Jetset is the light-mode option."

### 5.2 `semanticColors` Layer Is Redundant

Delete `semanticColors`. `ThemeTokens` includes `bubbleUser`, `bubbleAssistant`, etc. directly. No alias layer.

### 5.3 Bubble Styles Are Real Implementation Work

7 bubble styles: rounded, square, ribbon, stamp, minimal, stripe-edge, thread. Each needs visual design, not just a radius change. `stripe-edge` (Riley) needs a repeating left-border pattern. `thread` (Albers) needs dashed lines.

**Phase 1:** Ship `rounded` only. The `bubbleStyle` field exists in `ThemeTokens` but `ChatBubble` only renders `rounded`.  
**Phase 3:** All 7 styles implemented.

### 5.4 Texture Overlays Need Assets

6 PNG textures (128×128), bundled in app (~80KB total). Needs an overlay component — `position: absolute` `<Image>` or Skia canvas repeating the texture tile.

**Phase 1:** No textures. Flat `bgPrimary`.  
**Phase 3:** Assets + overlay component ship with Sensibility picker.

### 5.5 Motion Curves Per Theme

`transitionMs` and `transitionEasing` in tokens affect: theme switching animation, screen transitions, drawer animation, `StreamingCursor` blink rate.

**Phase 1:** Static animation timing.  
**Phase 3:** All animated components read from active theme tokens.

### 5.6 Artifact Aesthetics Are SOUL Content, Not Client Code

Per-theme artifact aesthetics (how agents produce websites, code, documents) are behavioral instructions, not iOS code. Split the behavior injection into two blocks:

```
[AESTHETIC STANCE — Jetset]
Maximum restraint. Use the fewest possible components...

[ARTIFACT AESTHETICS — Jetset]
When producing tangible artifacts:
- Websites: single-column or 12-column strict grid...
- Code: variables named precisely, not cleverly...
```

Both blocks included always — ~200 tokens overhead, not worth gating on tool usage. At Tier 3 = ~$0.001.

### 5.7 Multi-Client Theme Conflict

Two devices fight over `polly.ios.aestheticStance` (last-write-wins). The visual theme won't change (client-side MMKV), but the behavior injection will. This creates a split: app looks like Fidenza, agents behave like Ghost Box.

**Phase 1 mitigation:** On connect, read `polly.ios.aestheticStance` and compare to local MMKV `polly.sensibility`. If they disagree, show banner: "Another device changed the sensibility to Ghost Box. [Switch] [Keep Mine]." User choice re-patches the gateway.

**Phase 2:** Device-scoped config key (`polly.ios.aestheticStance.{deviceId}`) if @backend adds per-device config scoping.

### 5.8 Sensibility and Model Routing

Some sensibilities are more token-expensive (Martens = layered responses, Jetset = minimal). Not worth optimizing in Phase 1–3. Note as Phase 4 refinement — routing engine could learn Fidenza sessions consume ~1.3× tokens and adjust budget projections.

---

## 6. Structural Layer — Activation UX

### 6.1 Explicit Activation

**Option A (per-agent persistent):** Agent detail → Structural Mode picker:

```
┌─────────────────────────────────────┐
│ Structural Mode                     │
│ [None ▾]                            │
│ ○ None (default)                    │
│ ● Fragment (Ghost Box)              │
│   "Refuses to complete arguments.   │
│    Presents fragments and stops."   │
│ ○ Systematic Variation (Riley)      │
└─────────────────────────────────────┘
```

Persists per-agent across sessions.

**Option B (per-message):** Structural mode pill in augmentation row alongside vault note and mental model pills: `[📄 MEMORY.md ✕] [🧠 Inversion ✕] [⚡ Fragment ✕]`. Applied to next message only; disappears after send.

**Recommendation:** Both. Option A for persistent. Option B for one-off. Option B overrides Option A for that message.

### 6.2 Suggested Activation

Agent proposes structural mode. SOUL baseline includes:

> When you judge the conversation would benefit from structural constraint, say: "This feels like it might benefit from Fragment mode — would you like me to switch to presenting fragments instead of complete arguments?" Wait for confirmation. Never activate without agreement.

### 6.3 Automatic Activation (Phase 3+)

Metacognitive Dashboard detects cognitive pattern → agent activates complementary structural mode. Never silent — agent acknowledges mode change and it remains overridable:

> "I'm switching to a more fragmentary approach for this question — I think you'll see the pieces more clearly if I don't assemble them for you. Let me know if you'd rather I respond normally."

---

## 7. Phase Plan

### Phase 1: Foundation
- `ThemeContext` + `ThemeProvider` + `useTheme()` hook
- Reas as default theme (token values matching current `colors.ts`)
- All components migrated from `useColors()` to `useTheme().tokens`
- Delete `useColors()`, `semanticColors`, `light` export
- Fix all `(colors as any)` casts
- `bubbleStyle` in tokens — always `rounded` in Phase 1
- `structural_rules` field in agent sensibility schema — always empty in Phase 1
- All 7 theme files created with token values from §19.6 (not selectable)
- MMKV `polly.sensibility` key — always `"reas"` in Phase 1

### Phase 2: Behavior Injection
- `config.patch` for `polly.ios.aestheticStance` on theme selection
- Behavior injection text for all 7 themes (§19.5 content)
- Artifact aesthetics injection text for all 7 themes
- Multi-client conflict detection + "Another device changed..." banner
- Per-agent structural mode config key `polly.ios.structuralMode.{agentId}`
- Device-scoped config key (if @backend adds per-device scoping)

### Phase 3: Full Sensibility Picker
- Sensibility picker UI (§19.2 horizontal card scroll)
- Live mini-preview per theme
- Instant theme switching with theme-native transition
- Texture overlay assets (6 PNGs) + overlay component
- Bubble style variants (7 styles) in `ChatBubble`
- Per-theme typography
- Structural rules UI: per-agent picker + in-chat pill
- Theme-aware animation timing (all animated components read from tokens)

### Phase 4: Composability
- 3 sliders: Structure, Turbulence, Voice
- Slider adjustments produce derived token sets (interpolated from base theme)
- Save custom compositions as named sensibilities
- Export/import sensibility JSON
- Domain-triggered auto-switching (Sigils → Reas, Signals → Fidenza, etc.)

  > **NOTE:** The auto-switching logic reads `default_sensibility` from the matched `UserDomain` record (see `POLLY_IOS_SPEC.md §20.3`). The examples above (Sigils → Reas, etc.) reflect the original design author's personal domain-to-sensibility configuration — they are not app defaults. Default starter domains ship with sensible `default_sensibility` values; users may change them in Settings → Domains.
- Decoupled visual/behavioral control
- Routing engine learns per-sensibility token consumption (~Phase 4 refinement)

---

## 8. Phase 1 Decisions (Locked)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Replace `useColors()` now or Phase 3? | **Now (Phase 1)** | Every Phase 1 component that uses `useColors()` will need rewriting in Phase 3. Start right. |
| Dark/light mode? | **Theme-defined. Delete `light` export. Jetset is the light option.** | 6/7 themes are dark. The `light` export has broken field names anyway. |
| Ship all 7 theme files in Phase 1? | **Yes, all 7 (not selectable)** | Token values are defined in §19.6. Creating files now costs nothing. Prevents Phase 3 from mixing file creation + picker UI. |
| `bubbleStyle` rendering in Phase 1? | **`rounded` only; field exists in tokens** | Other styles are real design work. Ship the field, render one variant. |
| `structural_rules` on agent schema? | **Include empty field now** | One line in agent manifest. Prevents schema migration later. |

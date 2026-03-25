# Figma Integration
## Polly Spec | Last updated: 2026-03-24

> *Design specs live in markdown. Prototypes live in Figma. Polly surfaces the link without forcing a context switch.*

---

## Overview

Polly integrates with Figma to surface design prototypes directly in conversation. When a design spec is complete, the user can view the related mockup or prototype in the Figma iOS app without leaving Polly.

**Figma is an optional integration.** The user connects their account in Settings → Integrations (see `INTEGRATION_ONBOARDING.md` for the standard flow). Once connected, Polly surfaces Figma prototypes contextually. If not connected, a warm prompt offers to set it up.

This is a **Polly → Figma** integration (link surfacing), not a **Figma → Polly** integration (API read). The Figma file is the source of truth; Polly just makes it easy to access.

---

## Phase 2 Implementation: Link Surfacing Only

### Spec Pattern

Each design spec file has an optional `figma_link` field at the top:

```markdown
# COPY_VOICE.md
Polly Spec | Last updated: 2026-03-24

**Related Figma:** [Voice Interaction UI Kit](figma://file/[PROJECT_ID]/board-voice-button)

> *Voice is a first-class interaction mode in Polly...*
```

**Field format:**
```
**Related Figma:** [Display Name](figma://file/[PROJECT_ID]/[BOARD_ID])
```

**Components:**
- `[PROJECT_ID]`: Figma project ID (e.g., `abc123xyz`)
- `[BOARD_ID]`: Board or frame ID within the project (e.g., `board-voice-button`)
- `[Display Name]`: Human-readable name (e.g., "Voice Interaction UI Kit")

**When figma_link is absent:** The spec is standalone. No link is surfaced. This is fine — not every spec needs a Figma file.

---

### How Polly Surfaces the Link

When a user is viewing a design spec in conversation, Polly offers the link if it exists:

**In chat (example):**
```
User: "Show me the voice button design."

Polly: 
Here's COPY_VOICE.md with the token spec and state machine.

[Button] Related Figma: Voice Interaction UI Kit
```

Or, when a spec is first closed:

```
User: "Design the copy for voice interaction."

Polly:
[After generating COPY_VOICE.md]

I've drafted the spec above. Want to see this in Figma?

[Button] Open Voice Interaction UI Kit
```

**The button action:** Tapping the link opens the `figma://` URL, which deep-links directly to the relevant board/frame in the Figma iOS app.

---

### iOS Deep-Linking

**URL scheme:** `figma://file/[PROJECT_ID]/[BOARD_ID]`

**Behavior:**
1. User taps link in Polly
2. iOS checks if Figma app is installed
3. If yes: Opens Figma app, navigates to the board/frame
4. If no: Falls back to `https://figma.com/file/[PROJECT_ID]/` (web version)

**Implementation note for @frontend:**
- Links are rendered as `[Display Name](figma://...)` in markdown
- The markdown renderer automatically makes them tappable
- No special handling needed — standard URL tap behavior

---

## Placeholder Pattern (Until Figma Project Is Ready)

If Figma is not yet set up, specs use this placeholder:

```markdown
# COPY_VOICE.md
Polly Spec | Last updated: 2026-03-24

**Related Figma:** [To be added when Figma project is created]

> *Voice is a first-class interaction mode in Polly...*
```

**Process for activation:**
1. Figma project is created
2. Design mockups are added to the project
3. I update spec files with actual figma_link fields
4. No code changes needed — just markdown updates

---

## Figma Project Structure (Reference)

When the Figma project is set up, suggested structure:

```
Polly Design System (Project)
├── Voice Interaction (Board)
│   ├── Mic Button States
│   ├── Waveform Visualization
│   └── Error States
├── Study UI (Board)
│   ├── Breakout Card
│   ├── Entry Points
│   └── Study Progression
├── Color Tokens (Board)
│   ├── Warm Palette
│   └── Error & Accessibility
└── Personas (Board)
    ├── Architect
    ├── Professor
    └── Scribe
```

Each board gets a board ID, and specs link to their corresponding board.

---

## Future: Figma → Polly (Phase 4+)

**Not in this spec.** When bandwidth allows, Polly could read Figma files via API to:
- Pull component specifications into conversation
- Check consistency across frames
- Comment on designs
- Generate code from component specs

This requires:
- Figma API authentication
- OAuth flow (user grants Polly access to their Figma workspace)
- Caching layer (don't spam Figma API)
- Markdown generation from Figma data

For now, **link surfacing only**. That solves the immediate problem (fast prototype review without context switching) with zero API complexity.

---

## Implementation Checklist

**When Figma project is created:**
- [ ] Get project ID and board IDs
- [ ] Update all existing specs with figma_link fields
- [ ] Test links in iOS Figma app (confirm deep-linking works)
- [ ] Test fallback to web if app not installed
- [ ] Add figma_link pattern to spec template for future specs

**For future specs:**
- [ ] Include figma_link field when Figma mockups exist
- [ ] Use consistent display name format (e.g., "[Feature] [Component] UI Kit")
- [ ] Verify link targets the correct board/frame before shipping spec

---

## Quick Reference: Markdown Pattern

**Template for specs that have Figma files:**
```markdown
# [SPEC_NAME]
Polly Spec | Last updated: YYYY-MM-DD

**Related Figma:** [Display Name](figma://file/PROJECT_ID/BOARD_ID)

> *[Spec description]*
```

**Template for specs without Figma files (yet):**
```markdown
# [SPEC_NAME]
Polly Spec | Last updated: YYYY-MM-DD

> *[Spec description]*
```

No figma_link field = no link surfaced. Simple.

---

## Why This Approach (Monome Alignment)

- **Local-first:** Specs live in markdown in the repo, not locked in Figma
- **Open-ended:** Links can point anywhere — not coupled to a specific tool
- **Minimal:** Just a URL and a button. No API, no syncing, no complexity
- **Repairable:** If a link breaks, update the markdown. No infrastructure to maintain
- **Infrastructure, not product:** Figma is a tool the user already has. Polly just makes it easier to access

---

*Figma integration is a courtesy, not a requirement. The specs are complete and usable without it.*

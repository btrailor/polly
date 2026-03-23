# Polly Codebase Audit — Intentions, Aesthetics & Philosophical Guideposts
**Conducted by:** @code_architect  
**Date:** March 23, 2026  
**Source:** Full audit of `~/polly/` codebase — docs, planning, phases, design system, constitution, features, known issues  
**Purpose:** Extract everything worth porting into the OpenClaw-centered Polly iOS project

---

## Executive Summary

The old Polly codebase represents roughly 6 months of crystallized thinking (Aug 2025–Feb 2026) about what a personal AI system should be. It is philosophically rich and visually opinionated. The Polly iOS project should treat this as a constitution, not just a feature list.

Three categories of material were found:
1. **Philosophical guideposts** — core beliefs that should govern every decision in Polly iOS
2. **Aesthetic preferences** — concrete, specific visual/interaction language that must carry over
3. **Feature intentions** — specific ideas from old Polly that are viable and desirable in the new context

---

## Part 1: Philosophical Guideposts (The Constitution)

### 1.1 The Vision Statement (Carry Verbatim)

> *"Polly is a personal AI system that grows with you — starting simple, becoming powerful, always yours."*

This is not marketing copy. It is a design constraint. Every feature decision should be tested against it:
- Does this make Polly feel more like something the user *owns*?
- Does this reveal complexity at the right time, or overwhelm?
- Does this grow with the user?

### 1.2 Progressive Capability Model

**The single most important philosophical principle from the old codebase.**

Polly sits between opposing forces:
```
Open ←── Polly ──→ Curated
Powerful ←── Polly ──→ User-Friendly  
Expert ←── Polly ──→ Beginner
Extensible ←── Polly ──→ Opinionated
```

The answer is not to choose a side. The answer is *growth*. Polly starts as a beautiful, simple chat app. Features are revealed when contextually appropriate — when the user is ready.

**Application to Polly iOS:**
- Phase 1 settings: minimal. Just gateway URL and auth.
- Advanced provider config, mental models, domain awareness: revealed progressively as user engages
- "Show advanced" toggles everywhere — never hide, but don't surface until needed
- Onboarding should feel like a beautiful app, not a setup wizard

### 1.3 Four Core Design Principles (from DESIGN_PHILOSOPHY.md)

**Principle 1: Context Reveals Complexity**
Don't show all features upfront. Reveal when contextually appropriate.
- ✅ Good: "I notice you're working with code. Want to try X?"
- ❌ Bad: Settings page with 300 visible options

**Principle 2: Intelligent Defaults**
Polly must work beautifully with zero configuration. Configuration is for edge cases.
- Defaults are opinionated and sensible
- Auto-select optimal model, domain, context window
- Never force the user to choose on every message

**Principle 3: Open but Curated**
Community can extend Polly, quality is maintained through curation. The Obsidian/VS Code/Figma model: closed core, open extensions.

**Principle 4: Own Your Data, Own Your Tools**
This is the north star differentiator. Polly's entire positioning vs. competitors like Aight (when it goes freemium) or Uare.ai ($10.3M cloud SaaS):
> *"Personal AI you own" vs "Personal AI you rent"*
- Local-first, markdown files, no lock-in
- No subscriptions (one-time or free)
- No analytics tracking without opt-in
- No dark patterns

**Application to Polly iOS:** This principle should be stated explicitly in the app's onboarding. "Your data stays on your machine. Always."

### 1.4 The "Soft Autonomist" Positioning

Found in research queue: Polly explicitly positions against cloud-dependency and data harvesting. The user values:
- **Data ownership** — human-readable markdown, not proprietary DB
- **Practice augmentation** — extending human capability, not replacing it
- **Privacy** — data never leaves the user's machine unless explicitly sent to a cloud provider
- **Sovereignty** — user can inspect, edit, and own every file Polly touches

**Application to Polly iOS:** Settings should have a clear "Privacy" section showing exactly what leaves the device and what doesn't. "What Polly sends to AI providers" transparency screen.

### 1.5 Anti-Patterns to Never Ship

From KNOWN_ISSUES.md and DESIGN_PHILOSOPHY.md:
- ❌ Emoji as system icons (being actively replaced with Lucide — see §2.1)
- ❌ Modal interruptions that break flow
- ❌ "Wizard hell" (endless sequential setup screens)
- ❌ Silent failures (always communicate state)
- ❌ Analytics without consent
- ❌ Jarring UI refreshes/flashes (specific pattern flagged as high-priority bug)
- ❌ Scroll position loss on reload

---

## Part 2: Aesthetic Preferences

### 2.1 Icon System: Lucide Icons, Not Emoji

**This is a firm, actively-pursued preference — not a passing idea.**

From KNOWN_ISSUES.md (tracked as an ongoing migration):
> "20+ emoji icons replaced with Lucide icons (Feb 2, 2026), but more remain. Replace with appropriate Lucide icons. Standardize icon sizing/colors."

**The intent is clear:** Polly uses Lucide icons system-wide, not emoji. Emoji are reserved for agent personality (agent avatars in SOUL.md) and content (user messages), not UI chrome.

**Application to Polly iOS:**
- Install `lucide-react-native` — this is the canonical icon library
- Zero emoji in navigation, buttons, labels, status indicators, tab bar
- Agent avatars (emoji) are the one explicit exception — they are personality, not chrome
- Icon sizing: 20px (inline/list), 24px (nav bar), 28px (tab bar)
- Icon color: `colors.textSecondary` default, `colors.accent` for active states

**Lucide icon mapping for core UI:**
| Element | Lucide Icon |
|---------|-------------|
| Chat | `MessageSquare` |
| Today / Calendar | `Calendar` |
| Shortcuts | `Zap` |
| Moltbook | `BookOpen` |
| Usage Stats | `BarChart2` |
| Settings | `Settings` |
| Voice mic (idle) | `Mic` |
| Voice mic (active) | `MicOff` |
| Send | `ArrowUp` |
| Add | `Plus` |
| Search | `Search` |
| Gateway connected | `Wifi` |
| Gateway disconnected | `WifiOff` |
| Agent | `Bot` |
| Group chat | `Users` |
| Obsidian vault | `Vault` |
| Memory / Moltbook | `Brain` |
| Pattern | `Sparkles` |
| Domain | `Layers` |
| Mental model | `Compass` |
| Reminder | `Bell` |
| Task | `CheckSquare` |
| Process | `Activity` |
| Code block | `Code2` |
| Copy | `Copy` |
| Edit | `Pencil` |
| Delete | `Trash2` |
| Chevron / expand | `ChevronRight` |
| Close | `X` |
| Back | `ChevronLeft` |

### 2.2 Color System (from DESIGN_SYSTEM.md — confirmed)

The old Polly had a mature, opinionated color system. Key carries:

**Primary accent:** `#f0903b` (Polly orange) — already in iOS spec §5.1
**Background:** Deep dark navy (`#020617`) — not pure black, not gray
**Surface elevation:** Subtle blue-tinted dark layers (not flat gray like most dark themes)
**Text hierarchy:** High contrast primary (`#f8fafc`), muted secondary (`#b5c1ce`)

**Five-domain color system (carry exactly):**
- Sigils (Code): `#2563eb` blue
- Signals (Audio/Voice): `#ad48dd` purple  
- Scrolls (Writing): `#16a34a` green
- Glyphs (Design): `#eab308` gold
- Grids (Systems): `#16a399` teal

**Key aesthetic direction from UI_ROADMAP.md:**
- Obsidian-inspired: dark, focused, information-dense without feeling cluttered
- Professional and minimal — tools feel serious, not playful
- Subtle glass/blur effects on modal surfaces (already speced via `expo-blur`)
- Accent color used sparingly — it should *mean* something when it appears

### 2.3 Typography

From DESIGN_SYSTEM.md:
- System font (SF Pro on iOS) — no custom fonts
- Monospace: SF Mono for all code and technical content
- Hierarchy via weight and size, not color alone
- Dynamic Type must be respected (accessibility non-negotiable)

### 2.4 Layout Philosophy

From phase documents and electron-app architecture:
- **Three-column desktop reference** (sidebar → content → detail) — on mobile this becomes tab-based + sheet navigation
- **Vertical icon ribbon** from Electron app becomes bottom tab bar on iOS
- **Information density**: Polly is for power users. Don't pad excessively. Compress information respectfully.
- **Sidebar pattern**: Agent list, vault navigator, shortcuts — these are side panels, not full screens

### 2.5 Interaction Principles

- **Swipe-to-act**: Right = positive (done, approve), Left = destructive (delete, cancel) — standard iOS, but commit to it system-wide
- **Long press = context menu**: Never right-click. Zeego for native iOS context menu previews.
- **Pull to refresh**: All live data views
- **Haptic feedback**: Purposeful, not decorative. Light impact on actions, medium on confirmations, error pattern on failure.
- **No loading spinners for streaming** — show progressive content. A spinner that blocks content is an anti-pattern.

---

## Part 3: Feature Intentions Worth Porting

### 3.1 Orchestrator Mode (HIGH — maps to group chat)

From Phase 24 spec:
> Multi-persona coordination. Dynamic todo lists (OpenCode-style progress tracking). Customizable workflows (Architect → Designer → Programmer).

**What this becomes in Polly iOS:**
- Group chat is the surface, but Orchestrator Mode is the intelligence layer
- User can define a **workflow**: a sequence of agents with specific roles
- Workflow progress is shown as a live todo list in the Today view
- "Architect → Designer → Programmer" becomes a saved group chat template

### 3.2 User Profile System (HIGH — maps to Moltbook)

From Phase 13b spec:
> 4 bootstrap mechanisms (corpus import, onboarding, progressive, manual). Profile-aware context injection. Domain-specific sub-profiles.

**What this becomes in Polly iOS:**
- Moltbook is not just memory.md files — it's the user's evolving profile
- Onboarding should begin building the profile immediately ("What do you work on?")
- Profile is human-readable markdown the user can edit directly
- Agents should reference the profile for tone, depth, and domain context

### 3.3 Designer Persona (MEDIUM — maps to agent templates)

From Phase 27 spec:
> Four modes: Vision, Mockup, Critic, System. "Theme as meta-persona" concept.

**What this becomes in Polly iOS:**
- Agent template system should include a Designer agent with these 4 modes
- Mode-switching in chat (Plan → Build, Vision → Mockup) is a UI primitive worth building

### 3.4 Code Architecture System (MEDIUM)

From Phase 25:
> Visual dependency trees. Impact analysis ("what breaks if I change X?"). Auto-generated architecture docs.

**What this becomes in Polly iOS:**
- Code Architect agent template with specialized tools
- "Impact analysis" as a shortcut

### 3.5 Pattern Transparency (HIGH — already in spec §11.4)

Already captured in Polly iOS spec. The old codebase confirms this was a high-priority intention: users should see what Polly has learned about them. "Polly noticed you usually start coding sessions with architecture before writing code."

### 3.6 Deduplication / Knowledge Coherence

From KNOWN_ISSUES.md:
> "The current model of asking whether or not we want to create the note when these others exist is not effective."

**What this becomes in Polly iOS:**
- When agents create Obsidian notes (write-back), smart deduplication: only warn if >80% semantic similarity
- Non-blocking: show similar notes as inline suggestions, not modal interruptions
- Post-creation merge option

### 3.7 Progressive Onboarding

From DESIGN_PHILOSOPHY.md — strong emphasis on avoiding "wizard hell." 

**What this becomes in Polly iOS:**
- First launch: just ask for gateway URL. That's it.
- Discover the user's vault on next session if they want Obsidian features
- Integrations configured on demand, not forced upfront
- Each new feature introduction should feel like a discovery moment, not a checklist

### 3.8 One-Time Purchase Model

From RESEARCH_QUEUE.md (studied Things 3, Sublime Text, Panic apps):
> "Build capability, don't rent it."

**What this becomes for Polly iOS:**
- TestFlight for personal use now
- If ever distributed: one-time purchase, no subscription
- "Upgrade pricing" for major versions (v2, v3) is acceptable
- No freemium, no feature-gating, no dark patterns

---

## Part 4: New Specification Additions

Based on this audit, three new sections need to be added to POLLY_IOS_SPEC.md:

### §16 — Distributed Computing / Node Network

**(NEW — from user's direct request)**

The user explicitly wants:
- Polly iPhone app to see and configure connected nodes (NAS, other machines)
- NAS capable of running tasks in the Polly network
- Streamlined connection flow for adding nodes

**Architecture concept:**
```
Polly iPhone App
      │
      │ WebSocket (existing)
      ▼
OpenClaw Gateway (primary node — home Mac)
      │
      ├── Node: Synology NAS (openclaw-node)
      │         └── Heavy tasks: batch RAG indexing, 
      │               file processing, local model inference
      │
      └── Node: Work Mac (future)
                └── Access from work network
```

**OpenClaw node protocol:** OpenClaw likely supports (or could support) a node/worker registration pattern. @backend needs to investigate whether `openclaw.json` has a `nodes` or `workers` config block.

**iPhone app surface:**
- Settings → Network → Nodes
- List of registered nodes with status (online/offline/busy)
- Add node: IP + port + auth token (QR code preferred)
- Per-node capability flags (can run RAG indexing, can run inference, can access vault)
- Task routing: user can pin certain task types to specific nodes

### §17 — Agent Groups & Templates

**(NEW — from user's direct request)**

The user wants Aight's agent groups and templates ported to Polly with aesthetic modifications. These "work exceptionally well" and need to be preserved.

**What Aight's groups are:** Pre-configured multi-agent workspaces for common workflows. Likely includes things like:
- "Home" group (the current group, all agents)
- "Dev" group (code-focused agents)
- "Research" group (researcher + AI expert)
- etc.

**What Polly adds on top:**
- Group templates styled to Polly aesthetic (Lucide icons, no emoji in UI chrome)
- Domain-aware group coloring (a "Code" group gets Sigils blue accent)
- Orchestrator Mode overlaid on groups (one agent can be designated coordinator)
- Group templates are human-readable files the user can fork and edit

### §18 — Polly Design Constitution

**(NEW — distilled from this audit)**

A one-page constitutional document that governs every future spec/implementation decision for Polly iOS.

---

## Part 5: Immediate Spec Updates Required

Before moving on, these items must be updated in POLLY_IOS_SPEC.md:

1. **§5 Design System** — Add Lucide icon mandate and mapping table (currently underspecified on icons)
2. **§6 Components** — All icon references should use Lucide names, not emoji or SF Symbol names
3. **§4 Screen Specs** — Tab bar icons should be Lucide, not emoji (currently spec shows emoji tabs)
4. **§11 Polly Features** — Expand to include Orchestrator Mode and User Profile System as Phase 2/3 features
5. **§13 Phase Plan** — Add node network and group templates to appropriate phases

---

## Part 6: What Does NOT Port

Some old Polly material should be left behind — it was specific to the Python/Electron context and has no analog in OpenClaw-centered Polly iOS:

- ❌ Python persona system (replaced by OpenClaw's SOUL.md agents)
- ❌ FastAPI/HTTP server layer (replaced by OpenClaw gateway)
- ❌ Electron desktop-specific UI patterns (three-column layout, resize handles)
- ❌ Context compression system (handled by OpenClaw gateway)
- ❌ Multi-model router (handled by OpenClaw gateway)
- ❌ RAG indexing engine (handled by OpenClaw + Polly gateway tools)
- ❌ Phase 9 macOS permissions (irrelevant for iOS)
- ❌ Graph database research (Neo4j vs SQLite — irrelevant for mobile client)

The *intent* behind these features is valid and often already captured in the iOS spec. The implementation is what doesn't port.

---

## Summary: What Gets Added to Spec

| Addition | Section | Priority |
|----------|---------|----------|
| Lucide icon mandate + full mapping | §5 (update) | Phase 1 — now |
| Tab bar uses Lucide not emoji | §4 (update) | Phase 1 — now |
| Progressive capability model | §18 Constitution (new) | Before Phase 1 |
| "Own your data" onboarding statement | §4.1 (update) | Phase 1 |
| Distributed node network | §16 (new) | Phase 3 |
| Agent groups + templates | §17 (new) | Phase 2 |
| Orchestrator mode in groups | §17 (new) | Phase 2 |
| User profile system (Moltbook expansion) | §4.4 + §11 (update) | Phase 3 |
| Privacy transparency screen | §4.6 (update) | Phase 2 |
| Progressive onboarding (minimal Phase 1) | §4.1 (update) | Phase 1 |
| Pattern transparency cards (expanded) | §11.4 (update) | Phase 2 |
| Anti-pattern list | §18 Constitution (new) | Guidepost |

---

*Audit complete. Three new sections (§16, §17, §18) and five section updates ready to be written.*

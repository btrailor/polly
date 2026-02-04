# Phase 0.5: UI Design System Foundation

**Duration:** 4-6 days  
**Priority:** High (Foundation for all future UI work)  
**Can be done:** In parallel with Phase 1.5 or immediately after  
**Status:** Planning Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Why Now](#why-now)
3. [Goals](#goals)
4. [Implementation Plan](#implementation-plan)
5. [Technology Choices](#technology-choices)
6. [Component Library](#component-library)
7. [Design Principles](#design-principles)
8. [Success Criteria](#success-criteria)
9. [Migration Strategy](#migration-strategy)

---

## Overview

This phase establishes a professional design system and component library that will guide all future UI work. Instead of a big bang rewrite, we create the foundation now and apply it incrementally as we build new features.

### What This Phase Does

- Sets up Shadcn/ui + Tailwind CSS
- Creates core component library (`/src/components/ui/`)
- Documents design system (colors, typography, spacing, patterns)
- Updates high-visibility components (navigation, integration cards)
- Establishes patterns for all future development

### What This Phase Does NOT Do

- Does not rewrite all existing UIs (that happens in "UI Polish Sprint" after Tier 1)
- Does not build every possible component (only what's needed)
- Does not block feature development (can run parallel to Phase 1.5)

---

## Why Now

### The Timing Argument

**Why not earlier?**
- Phases 1-5 were exploratory - brutalist design was appropriate
- Didn't know what UI patterns we'd need yet

**Why not later?**
- 15+ phases ahead (1.5-20) will all need UI components
- Building on foundation now = consistency by default
- Avoids massive rework if we wait until end

**Why now (between Phase 1 and 1.5)?**
- ✅ We know what patterns we need (chat, cards, forms, graphs, editors)
- ✅ About to build 13-16 weeks of new UIs (Tier 1)
- ✅ Can establish system while building Phase 1.5
- ✅ Professional polish before Tier 3 onboarding (first impressions matter)

### The Incremental Approach

This phase creates the **system**, not the **complete UI**. Think of it as:
- **Foundation:** Design tokens, component primitives, patterns
- **Application:** Happens gradually as we build Phases 1.5-17
- **Polish:** Final consistency pass after Tier 1 (UI Polish Sprint)

---

## Goals

### Primary Goals

1. **Establish design system** - Colors, typography, spacing, patterns documented
2. **Create component library** - Reusable primitives for all future work
3. **Set professional baseline** - Modern, clean aesthetic (not brutalist)
4. **Enable consistency** - Future developers (including you) follow established patterns
5. **Support dark mode** - Essential for developer tool, ship from day 1

### Non-Goals

- **NOT:** Pixel-perfect designs for every screen
- **NOT:** Complete UI overhaul of Phases 1-5 (yet)
- **NOT:** Animation/micro-interaction library (nice-to-have, later)
- **NOT:** Marketing website design (separate concern)

---

## Implementation Plan

### Timeline: 4-6 Days

Can be done in parallel with Phase 1.5 (different files, minimal conflicts).

---

### Day 1: Framework Setup & Configuration (1 day)

**Goal:** Get Shadcn/ui + Tailwind installed and configured

#### Tasks

**1. Install Shadcn/ui**

```bash
# From Polly frontend directory
cd src/
npx shadcn-ui@latest init

# Follow prompts:
# - TypeScript: Yes
# - Style: Default
# - Base color: Slate (neutral, professional)
# - Global CSS: src/styles/globals.css
# - CSS variables: Yes (easier theming)
# - Tailwind config: tailwind.config.js
# - Import alias: @/components
```

**2. Configure Tailwind Theme**

Edit `tailwind.config.js`:

```javascript
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Your custom colors (update these based on preference)
        primary: {
          DEFAULT: "#2563eb", // Deep blue
          50: "#eff6ff",
          100: "#dbeafe",
          // ... full scale
          900: "#1e3a8a",
          950: "#172554",
        },
        accent: {
          DEFAULT: "#ea580c", // Orange accent
          // ... full scale
        },
        // Shadcn will add: background, foreground, card, popover, etc.
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Consolas", "monospace"],
      },
      spacing: {
        // Ensure consistent spacing scale
        // Tailwind defaults are good, but document your usage
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

**3. Update Global Styles**

Create/update `src/styles/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light mode CSS variables (Shadcn generates these) */
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    /* ... more variables */
  }

  .dark {
    /* Dark mode CSS variables */
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... more variables */
  }

  * {
    @apply border-border;
  }

  body {
    @apply bg-background text-foreground;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}
```

**4. Set Up Dark Mode Toggle**

Create `src/components/ThemeProvider.tsx` (Shadcn will help with this):

```typescript
// Use next-themes or similar for dark mode
// Should persist user preference
```

**Success Criteria:**
- ✅ Tailwind compiles without errors
- ✅ Shadcn/ui commands work (`npx shadcn-ui@latest add button`)
- ✅ Dark mode toggles correctly
- ✅ CSS variables are applied

---

### Day 2: Core Component Library - Part 1 (1 day)

**Goal:** Install and customize essential Shadcn components

#### Install Components

```bash
# Essential components for Polly
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add select
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add tooltip
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add scroll-area
```

These components are now in `src/components/ui/` and are fully customizable.

#### Customize Components

**Button Variants:**

Edit `src/components/ui/button.tsx` to add Polly-specific variants:

```typescript
const buttonVariants = cva(
  "...", // base styles
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        // Add Polly-specific variant
        polly: "bg-gradient-to-r from-primary to-accent text-white hover:opacity-90",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
  }
)
```

**Input Customization:**

Add focus states, error states, and icons support.

**Card Customization:**

Create variants for integration cards, settings panels, etc.

#### Test Components

Create `src/components/ui/ComponentShowcase.tsx` (temporary, for testing):

```typescript
// Display all components with variants
// Good for testing during development
```

**Success Criteria:**
- ✅ All components render correctly
- ✅ Dark mode works for all components
- ✅ Components are accessible (keyboard nav, ARIA labels)
- ✅ Hover/focus states look good

---

### Day 3: Core Component Library - Part 2 + Custom Components (1 day)

**Goal:** Build Polly-specific composite components

#### Custom Components to Build

**1. IntegrationCard (replaces current brutalist cards)**

`src/components/ui/integration-card.tsx`:

```typescript
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface IntegrationCardProps {
  title: string
  description: string
  icon?: React.ReactNode
  status: "connected" | "disconnected" | "error"
  onConnect?: () => void
  onDisconnect?: () => void
  stats?: { label: string; value: string | number }[]
}

export function IntegrationCard({ title, description, icon, status, onConnect, onDisconnect, stats }: IntegrationCardProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {icon && <div className="text-2xl">{icon}</div>}
            <div>
              <CardTitle>{title}</CardTitle>
              <CardDescription>{description}</CardDescription>
            </div>
          </div>
          <Badge variant={status === "connected" ? "success" : status === "error" ? "destructive" : "secondary"}>
            {status}
          </Badge>
        </div>
      </CardHeader>
      {stats && (
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            {stats.map((stat) => (
              <div key={stat.label}>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
                <p className="text-2xl font-bold">{stat.value}</p>
              </div>
            ))}
          </div>
        </CardContent>
      )}
      <CardFooter className="flex gap-2">
        {status === "connected" ? (
          <Button variant="outline" onClick={onDisconnect}>Disconnect</Button>
        ) : (
          <Button onClick={onConnect}>Connect</Button>
        )}
      </CardFooter>
    </Card>
  )
}
```

**2. ChatMessage (replaces current chat bubbles)**

`src/components/ui/chat-message.tsx`:

```typescript
import { Card } from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"

interface ChatMessageProps {
  role: "user" | "assistant"
  content: string
  timestamp?: Date
  isStreaming?: boolean
}

export function ChatMessage({ role, content, timestamp, isStreaming }: ChatMessageProps) {
  return (
    <div className={cn("flex gap-3 mb-4", role === "user" && "justify-end")}>
      {role === "assistant" && (
        <Avatar className="h-8 w-8">
          <AvatarFallback>P</AvatarFallback>
        </Avatar>
      )}
      <Card className={cn(
        "max-w-[80%] p-4",
        role === "user" ? "bg-primary text-primary-foreground" : "bg-card"
      )}>
        <div className="prose prose-sm dark:prose-invert">
          {content}
          {isStreaming && <span className="animate-pulse">▊</span>}
        </div>
        {timestamp && (
          <p className="text-xs text-muted-foreground mt-2">
            {timestamp.toLocaleTimeString()}
          </p>
        )}
      </Card>
      {role === "user" && (
        <Avatar className="h-8 w-8">
          <AvatarFallback>U</AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
```

**3. StatusIndicator (for integrations, connections, etc.)**

`src/components/ui/status-indicator.tsx`:

```typescript
import { cn } from "@/lib/utils"

interface StatusIndicatorProps {
  status: "online" | "offline" | "loading" | "error"
  label?: string
  size?: "sm" | "md" | "lg"
}

export function StatusIndicator({ status, label, size = "md" }: StatusIndicatorProps) {
  const sizes = {
    sm: "h-2 w-2",
    md: "h-3 w-3",
    lg: "h-4 w-4",
  }

  const colors = {
    online: "bg-green-500",
    offline: "bg-gray-400",
    loading: "bg-yellow-500 animate-pulse",
    error: "bg-red-500",
  }

  return (
    <div className="flex items-center gap-2">
      <div className={cn("rounded-full", sizes[size], colors[status])} />
      {label && <span className="text-sm text-muted-foreground">{label}</span>}
    </div>
  )
}
```

**4. EmptyState (for empty lists, no data, etc.)**

`src/components/ui/empty-state.tsx`:

```typescript
interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
      {icon && <div className="text-6xl mb-4 text-muted-foreground">{icon}</div>}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      {description && <p className="text-sm text-muted-foreground mb-6 max-w-md">{description}</p>}
      {action && (
        <Button onClick={action.onClick}>{action.label}</Button>
      )}
    </div>
  )
}
```

**Success Criteria:**
- ✅ IntegrationCard renders beautifully
- ✅ ChatMessage supports streaming animation
- ✅ All custom components documented
- ✅ Consistent with Shadcn component patterns

---

### Day 4: Document Design System (1 day)

**Goal:** Create comprehensive design documentation

#### Create DESIGN_SYSTEM.md

See separate `DESIGN_SYSTEM.md` template document (created in this phase).

#### Document Decisions

Write down:
- **Why Shadcn/ui?** (copy-paste components, customizable, modern)
- **Color choices** (primary = blue for trust/tech, accent = orange for action)
- **Typography rationale** (Inter for UI, JetBrains Mono for code)
- **Spacing system** (4px base unit, Tailwind scale)
- **Component usage guidelines** (when to use Card vs. Dialog, etc.)

#### Create Component Documentation

For each custom component, document:
- Purpose (when to use it)
- Props API (TypeScript interfaces)
- Examples (code snippets)
- Variants (different states/configurations)

**Success Criteria:**
- ✅ DESIGN_SYSTEM.md is complete and readable
- ✅ All components have usage examples
- ✅ Design decisions are documented (why, not just what)
- ✅ Future you (or another developer) can understand the system

---

### Day 5: Update High-Visibility Components (1 day)

**Goal:** Apply design system to most visible parts of current UI

#### Components to Update

**1. Navigation/Header**

Update main navigation to use new components:
- New `Button` components for actions
- Consistent spacing and typography
- Dark mode toggle in header
- Status indicators for connection state

**2. Integration Cards (Phase 5)**

Replace brutalist cards with new `IntegrationCard` component:
- GitHub integration card
- Context7 integration card
- Obsidian integration card
- Calendar/Reminders/FileSystem cards (currently disabled)

**3. Settings Panel**

Update settings UI:
- New `Card` layouts for sections
- New `Input`, `Select`, `Textarea` components
- Consistent form styling
- Better visual hierarchy

**4. Tab Navigation**

Replace current tabs with Shadcn `Tabs` component:
- Consistent across all pages
- Better hover/active states
- Smooth transitions

#### Testing

Test updated components:
- Light mode and dark mode
- Hover states and interactions
- Responsive behavior (if applicable)
- Accessibility (keyboard navigation, screen readers)

**Success Criteria:**
- ✅ Navigation looks professional
- ✅ Integration cards are consistent and beautiful
- ✅ Settings panel is clean and usable
- ✅ No visual regressions in functionality

---

### Day 6: Polish & Testing (1 day)

**Goal:** Ensure everything works, fix issues, document edge cases

#### Tasks

**1. Cross-browser Testing**
- Chrome/Edge (primary)
- Safari (macOS)
- Firefox (optional)

**2. Dark Mode Verification**
- All components work in both modes
- No contrast issues
- Consistent color usage

**3. Accessibility Testing**
- Keyboard navigation works
- Focus indicators visible
- ARIA labels present
- Screen reader compatible (basic check)

**4. Performance Check**
- No CSS bloat (Tailwind purges unused)
- Components render quickly
- No layout shift issues

**5. Documentation Review**
- DESIGN_SYSTEM.md is accurate
- Component examples work
- Code is well-commented

**6. Clean Up**
- Remove ComponentShowcase (or keep as Storybook alternative)
- Remove unused CSS
- Organize component files

**Success Criteria:**
- ✅ All tests pass
- ✅ Dark mode is perfect
- ✅ Accessible by WCAG AA standards (basic)
- ✅ Documentation is complete
- ✅ Ready to build Phase 1.5+ with new system

---

## Technology Choices

### Primary Stack: Shadcn/ui + Tailwind CSS

**Why Shadcn/ui?**

✅ **You own the code** - Components are copied into your project, not imported from npm  
✅ **Highly customizable** - Full control over styling and behavior  
✅ **Built on Radix UI** - Accessible, well-tested primitives  
✅ **TypeScript-first** - Great DX, type-safe props  
✅ **Active community** - Well-maintained, modern patterns  
✅ **No bundle bloat** - Only includes what you use  
✅ **Beautiful defaults** - Professional aesthetic out of box  

**Why Tailwind CSS?**

✅ **Utility-first** - Fast development, consistent spacing  
✅ **Purges unused CSS** - Small production bundles  
✅ **Dark mode support** - Class-based or CSS variable approach  
✅ **Design tokens** - Colors, spacing defined in config  
✅ **No naming conflicts** - Scoped by default  
✅ **Great DX** - IntelliSense, quick iteration  

**Alternatives Considered:**

| Library | Pros | Cons | Decision |
|---------|------|------|----------|
| **Chakra UI** | Opinionated, fast setup, built-in dark mode | Less customizable, larger bundle, more dependencies | ❌ Less control |
| **Material UI (MUI)** | Comprehensive, mature | Heavy bundle, Google aesthetic (not desired), complex customization | ❌ Too opinionated |
| **Ant Design** | Enterprise-ready, comprehensive | Chinese aesthetic (not fit), heavy bundle | ❌ Not the right aesthetic |
| **Radix UI (alone)** | Headless, maximum control | No styling by default (more work) | ⚠️ Shadcn = Radix + styling |
| **Custom + Tailwind** | Full control | More work, slower | ⚠️ Shadcn = pre-built custom components |

**Decision: Shadcn/ui + Tailwind** wins because it's the best of both worlds - pre-built components you own and can customize.

---

### Typography

**UI Font: Inter**

- Clean, professional, excellent readability
- Variable font (flexible weights)
- Open source, free to use
- Industry standard for UI (GitHub, Vercel, Linear use it)

**Code Font: JetBrains Mono**

- Designed for developers
- Excellent ligatures (=>, !=, etc.)
- Clear distinction between similar characters (0 vs O, 1 vs l)
- Free, open source

**Fallbacks:**

```css
font-family: 
  "Inter", 
  -apple-system, 
  BlinkMacSystemFont, 
  "Segoe UI", 
  system-ui, 
  sans-serif;

font-family: 
  "JetBrains Mono", 
  "Fira Code", 
  "Consolas", 
  "Monaco", 
  monospace;
```

---

### Color System

**Primary Color: Deep Blue (#2563eb)**

- Professional, technical, trustworthy
- High contrast in dark mode
- Accessible color ratios
- Represents intelligence, depth, reliability

**Accent Color: Orange (#ea580c)**

- Complements blue (opposite on color wheel)
- Draws attention (CTAs, highlights)
- Energetic, action-oriented
- Used sparingly for emphasis

**Neutrals: Tailwind Slate**

- Neutral gray with slight blue undertone
- Matches primary color family
- 10-step scale (50-950) for flexibility
- Works well in light and dark modes

**Semantic Colors:**

- **Success:** Green (#22c55e)
- **Error:** Red (#ef4444)
- **Warning:** Yellow (#eab308)
- **Info:** Blue (primary)

**Dark Mode Strategy:**

Use CSS variables (Shadcn approach) for easy theme switching:

```css
:root {
  --background: 0 0% 100%;       /* white */
  --foreground: 222.2 47.4% 11.2%; /* dark gray */
  --primary: 221.2 83.2% 53.3%;   /* blue */
  /* ... more variables */
}

.dark {
  --background: 222.2 84% 4.9%;   /* very dark blue */
  --foreground: 210 40% 98%;      /* off-white */
  --primary: 217.2 91.2% 59.8%;   /* lighter blue */
  /* ... more variables */
}
```

---

### Spacing System

**Base Unit: 4px (Tailwind default)**

Tailwind spacing scale:
- `1` = 4px
- `2` = 8px
- `3` = 12px
- `4` = 16px (most common)
- `6` = 24px
- `8` = 32px
- `12` = 48px
- `16` = 64px

**Usage Guidelines:**

- **Component padding:** `p-4` (16px) for cards, dialogs
- **Section spacing:** `space-y-6` (24px) between sections
- **Grid gaps:** `gap-4` (16px) for grids
- **Element spacing:** `gap-2` (8px) for closely related items

---

## Component Library

### Shadcn Components Used

These are installed via `npx shadcn-ui@latest add <component>`:

| Component | Purpose | Usage |
|-----------|---------|-------|
| **button** | All clickable actions | Primary CTAs, secondary actions, icon buttons |
| **card** | Container for content | Integration cards, settings panels, chat messages |
| **input** | Text input fields | Forms, search, settings |
| **textarea** | Multi-line text input | Long-form content, notes, prompts |
| **select** | Dropdowns | Model selection, filters, preferences |
| **dialog** | Modals/popups | Confirmations, forms, detailed views |
| **tabs** | Navigation between views | Main navigation, settings sections |
| **badge** | Status indicators | Connection status, tags, counts |
| **separator** | Visual divider | Between sections, in menus |
| **tooltip** | Hover explanations | Icon meanings, additional info |
| **dropdown-menu** | Context menus | Actions on items, settings |
| **scroll-area** | Custom scrollbars | Long lists, code blocks |

### Custom Polly Components

These are built by us using Shadcn primitives:

| Component | Purpose | File |
|-----------|---------|------|
| **IntegrationCard** | Display integration status | `src/components/ui/integration-card.tsx` |
| **ChatMessage** | User/assistant messages | `src/components/ui/chat-message.tsx` |
| **StatusIndicator** | Connection status dot | `src/components/ui/status-indicator.tsx` |
| **EmptyState** | No data placeholders | `src/components/ui/empty-state.tsx` |
| **CodeBlock** | Syntax-highlighted code | `src/components/ui/code-block.tsx` |
| **LoadingSpinner** | Loading states | `src/components/ui/loading-spinner.tsx` |

---

## Design Principles

### 1. Information Density

**Principle:** Polly is for power users. Don't oversimplify.

- Show relevant data without excessive whitespace
- Use compact layouts where appropriate
- Tables/lists can be dense (with good typography)
- Tooltips provide additional context without cluttering

**Example:** Integration cards show stats inline, not hidden behind clicks.

---

### 2. Consistency

**Principle:** Patterns should be predictable and reusable.

- Same component for same purpose everywhere
- Consistent spacing (use Tailwind scale)
- Consistent colors (use semantic tokens)
- Consistent typography (heading hierarchy)

**Example:** All "connect" buttons are primary variant, all "disconnect" are outline.

---

### 3. Clarity

**Principle:** User should understand what's happening without guessing.

- Clear labels and microcopy
- Status indicators (loading, success, error)
- Helpful error messages
- Visual feedback for actions

**Example:** Integration card shows "Connected" badge and last sync time.

---

### 4. Accessibility

**Principle:** Keyboard navigation, screen readers, high contrast.

- All interactive elements keyboard accessible
- Focus indicators visible
- ARIA labels for icon buttons
- Contrast ratios meet WCAG AA

**Example:** Dialog can be closed with Escape, focus returns to trigger.

---

### 5. Performance

**Principle:** Fast, responsive, no jank.

- Lazy load components when possible
- Virtualize long lists (if needed)
- Smooth animations (60fps)
- No layout shift

**Example:** Code blocks use React.memo, only re-render when content changes.

---

## Success Criteria

### By End of Phase 0.5

✅ **Framework Setup**
- Shadcn/ui installed and configured
- Tailwind compiling correctly
- Dark mode working

✅ **Component Library**
- 12+ Shadcn components installed
- 4+ custom Polly components built
- All components documented

✅ **Design System**
- DESIGN_SYSTEM.md complete
- Color palette defined
- Typography documented
- Spacing guidelines clear

✅ **Visible Updates**
- Navigation uses new components
- Integration cards redesigned
- Settings panel updated
- Everything looks professional

✅ **Developer Experience**
- Components easy to use
- Good TypeScript types
- Examples in documentation
- Clear patterns established

---

## Migration Strategy

### Phase 0.5 (This Phase)

**Update:**
- Navigation/header
- Integration cards (Phase 5)
- Settings panel
- Tab navigation

**Don't Update (Yet):**
- Chat interface (Phase 4) - will update in UI Polish Sprint
- Conversation list - will update in UI Polish Sprint
- Modals/dialogs - will update incrementally

---

### Phases 1.5-17 (Tier 1 Development)

**For each new phase:**
1. Use design system components by default
2. Build custom components if needed (add to `/ui` if reusable)
3. Update DESIGN_SYSTEM.md if new patterns emerge

**Examples:**

**Phase 1.5 (Domain Configuration):**
- Use `Card` for domain list
- Use `Dialog` for first-run wizard
- Use `Input`, `Select` for forms
- Build custom `DomainCard` component

**Phase 12 (Knowledge Graph):**
- Use `Card` for controls panel
- Use `Dialog` for node details
- Build custom `GraphContainer` component
- Use `Badge` for node types

**Phase 16 (Native Notes):**
- Build custom `NoteEditor` wrapper around Monaco
- Use `Card` for backlinks panel
- Use `Dialog` for note settings
- Use `Badge` for tags

---

### Between Tier 1 and Tier 2 (UI Polish Sprint)

**Update remaining components:**
- Chat interface (Phase 4) → use `ChatMessage` component
- Conversation list → use `Card` + `Badge`
- Modals → use `Dialog`
- Forms → use consistent `Input`, `Select`, `Textarea`

**Polish:**
- Smooth transitions
- Hover states
- Loading states
- Error states
- Empty states

**Total time:** 1 week

---

## Post Phase 0.5

### Ongoing Maintenance

**As you build Phases 1.5-17:**
- Follow established patterns
- Add components to `/ui` if reusable
- Document new patterns in DESIGN_SYSTEM.md
- Keep consistency top of mind

**Update design system when:**
- New pattern emerges (e.g., a new type of card)
- Color needs adjusting (after user feedback)
- Component needs variant (e.g., Button with icon + text)

---

### Future Enhancements (Optional)

**After Tier 1 is complete:**

**Animation Library:**
- Framer Motion for smooth transitions
- Page transitions
- List animations
- Micro-interactions

**Advanced Components:**
- Command palette (Cmd+K)
- Toast notifications system
- Keyboard shortcuts viewer
- Onboarding tooltips/tours (for Phase 18)

**Design Tooling:**
- Storybook for component development
- Visual regression testing (Chromatic)
- Design tokens in Figma (if designer involved)

**These are NOT required for Phase 0.5** - focus on foundation first.

---

## Implementation Checklist

### Day 1: Framework Setup
- [ ] Install Shadcn/ui (`npx shadcn-ui@latest init`)
- [ ] Configure Tailwind theme (colors, fonts)
- [ ] Update global styles (CSS variables)
- [ ] Set up dark mode toggle
- [ ] Test: Tailwind compiles, dark mode works

### Day 2: Core Components - Part 1
- [ ] Install Shadcn components (button, input, card, dialog, tabs, select, textarea, badge, separator, tooltip, dropdown-menu, scroll-area)
- [ ] Customize button variants
- [ ] Test all components in light/dark mode
- [ ] Create ComponentShowcase (temporary testing page)

### Day 3: Core Components - Part 2
- [ ] Build IntegrationCard component
- [ ] Build ChatMessage component
- [ ] Build StatusIndicator component
- [ ] Build EmptyState component
- [ ] Document all custom components

### Day 4: Documentation
- [ ] Create DESIGN_SYSTEM.md (use template)
- [ ] Document color choices
- [ ] Document typography decisions
- [ ] Document spacing guidelines
- [ ] Add component usage examples

### Day 5: Update High-Visibility UI
- [ ] Update navigation/header
- [ ] Replace integration cards
- [ ] Update settings panel
- [ ] Update tab navigation
- [ ] Test all changes

### Day 6: Polish & Testing
- [ ] Test in Chrome/Safari/Firefox
- [ ] Verify dark mode everywhere
- [ ] Test keyboard navigation
- [ ] Test accessibility (basic)
- [ ] Performance check
- [ ] Clean up unused code
- [ ] Final documentation review

---

## Questions & Decisions

### Open Questions

**Q: Should we use CSS Modules alongside Tailwind?**  
**A:** No. Stick with Tailwind + occasional global CSS. Shadcn components use Tailwind exclusively.

**Q: Do we need animations from the start?**  
**A:** Basic animations (hover, transitions) yes. Complex animations (page transitions, Framer Motion) can wait until UI Polish Sprint.

**Q: Should we build Storybook?**  
**A:** Not yet. ComponentShowcase is enough for Phase 0.5. Consider Storybook after Tier 1 if team grows.

**Q: What about responsive design / mobile?**  
**A:** Polly is desktop-first. Responsive is nice-to-have but not priority. iOS app (Phase 10) is separate.

**Q: Do we need a designer?**  
**A:** Not required. Shadcn defaults are professional. If you want pixel-perfect branding later, consider hiring designer for "UI Polish Sprint."

---

## Resources

### Documentation

- **Shadcn/ui Docs:** https://ui.shadcn.com/
- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **Radix UI Docs:** https://www.radix-ui.com/docs/primitives
- **Tailwind Dark Mode:** https://tailwindcss.com/docs/dark-mode

### Design Inspiration

- **Linear:** https://linear.app (clean, professional, developer tool)
- **GitHub:** https://github.com (familiar, technical aesthetic)
- **Vercel:** https://vercel.com (modern, minimal)
- **Raycast:** https://raycast.com (power user tool, great UX)

### Tools

- **Coolors:** https://coolors.co/ (color palette generator)
- **Realtime Colors:** https://realtimecolors.com/ (preview color schemes)
- **Type Scale:** https://typescale.com/ (typography scale generator)
- **Contrast Checker:** https://webaim.org/resources/contrastchecker/ (accessibility)

---

## Appendix: Example Component Usage

### IntegrationCard Example

```typescript
<IntegrationCard
  title="GitHub"
  description="Index your repositories for code search"
  icon={<GitHubIcon />}
  status="connected"
  stats={[
    { label: "Repositories", value: 17 },
    { label: "Last Sync", value: "2 min ago" },
  ]}
  onDisconnect={handleDisconnect}
/>
```

### ChatMessage Example

```typescript
<ChatMessage
  role="assistant"
  content="Here's what I found in your knowledge base..."
  timestamp={new Date()}
  isStreaming={false}
/>
```

### EmptyState Example

```typescript
<EmptyState
  icon={<InboxIcon />}
  title="No conversations yet"
  description="Start a new conversation to begin using Polly."
  action={{
    label: "New Conversation",
    onClick: handleNewConversation,
  }}
/>
```

---

## Next Steps After Phase 0.5

1. **Continue Phase 1.5** (Domain Configuration) using new design system
2. **Build Tier 1 phases** (1.5-17) with consistent components
3. **UI Polish Sprint** (after Tier 1) to update remaining old UIs
4. **Profit** - Professional, consistent, beautiful UI throughout

---

**Document Status:** Complete  
**Last Updated:** January 24, 2026  
**Next Phase:** Continue Phase 1.5 (Domain Configuration) or start Phase 0.5 in parallel

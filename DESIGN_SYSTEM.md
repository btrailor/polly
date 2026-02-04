# Polly Design System

**Version:** 1.0  
**Last Updated:** January 24, 2026  
**Status:** Foundation established in Phase 0.5  

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Color System](#color-system)
4. [Typography](#typography)
5. [Spacing & Layout](#spacing--layout)
6. [Components](#components)
7. [Patterns](#patterns)
8. [Accessibility](#accessibility)
9. [Usage Guidelines](#usage-guidelines)
10. [Change Log](#change-log)

---

## Overview

This document defines Polly's visual language and UI patterns. It serves as the single source of truth for design decisions and component usage.

### Tech Stack

- **Framework:** React + TypeScript
- **Styling:** Tailwind CSS
- **Component Library:** Shadcn/ui (built on Radix UI)
- **Icons:** [Choose: Lucide React, Heroicons, or Phosphor]
- **Dark Mode:** CSS variables + class-based toggle

### Philosophy

Polly's UI is designed for **power users** who value:
- **Information density** - Show relevant data without excessive whitespace
- **Consistency** - Predictable patterns across all features
- **Clarity** - Clear status, helpful feedback, no guessing
- **Performance** - Fast, responsive, no jank
- **Accessibility** - Keyboard navigation, screen readers, high contrast

---

## Design Principles

### 1. Information Density

**For power users, not casual consumers.**

✅ **Do:**
- Show stats, metadata, context inline
- Use compact layouts with good typography
- Tables and lists can be dense (but scannable)
- Tooltips provide additional details

❌ **Don't:**
- Hide information behind multiple clicks
- Use excessive whitespace "for breathing room"
- Oversimplify or dumb down

**Example:** Integration cards show repository count, last sync time, and status badge - all visible at a glance.

---

### 2. Consistency

**Same component, same purpose, everywhere.**

✅ **Do:**
- Use established components (don't reinvent)
- Follow spacing system (Tailwind scale)
- Use semantic color tokens (not raw hex)
- Maintain heading hierarchy

❌ **Don't:**
- Create one-off components for similar purposes
- Use arbitrary spacing (e.g., `padding: 13px`)
- Hard-code colors (use CSS variables)
- Skip heading levels (h1 → h3)

**Example:** All "connect" buttons use `variant="default"`, all "disconnect" use `variant="outline"`.

---

### 3. Clarity

**User should know what's happening, always.**

✅ **Do:**
- Show loading states (spinners, skeletons)
- Indicate success/error clearly
- Provide helpful error messages
- Use visual feedback (hover, active states)

❌ **Don't:**
- Leave actions without feedback
- Show generic errors ("Something went wrong")
- Hide important status information

**Example:** When syncing GitHub repos, show progress indicator + count ("Syncing 17 repositories...").

---

### 4. Accessibility

**Keyboard, screen reader, high contrast support.**

✅ **Do:**
- All interactive elements keyboard accessible
- Focus indicators clearly visible
- ARIA labels for icon buttons
- Contrast ratios meet WCAG AA (4.5:1 text, 3:1 UI)

❌ **Don't:**
- Trap focus in modals (allow Escape key)
- Use color as only indicator (add icon/text)
- Remove focus outlines for aesthetic reasons

**Example:** Dialog closes with Escape key, focus returns to trigger button.

---

### 5. Performance

**Fast, smooth, no layout shift.**

✅ **Do:**
- Lazy load heavy components (Monaco editor, graph)
- Use React.memo for expensive renders
- Virtualize long lists (if >100 items)
- Optimize images (WebP, correct sizes)

❌ **Don't:**
- Re-render entire tree on state change
- Load all data upfront
- Use unoptimized images
- Block main thread

**Example:** Code editor (Monaco) lazy loads on first code workspace open.

---

## Color System

### Primary Color: Deep Blue

Used for: Primary actions, links, focus states

```css
--primary: 221.2 83.2% 53.3%; /* #2563eb */
```

**Palette:**
- `primary-50`: #eff6ff (lightest)
- `primary-100`: #dbeafe
- `primary-200`: #bfdbfe
- `primary-300`: #93c5fd
- `primary-400`: #60a5fa
- `primary-500`: #3b82f6
- `primary-600`: #2563eb ← **Default**
- `primary-700`: #1d4ed8
- `primary-800`: #1e40af
- `primary-900`: #1e3a8a
- `primary-950`: #172554 (darkest)

**Usage:**
- Buttons (primary CTA)
- Links
- Focus rings
- Active tab indicators
- Badges (info status)

---

### Accent Color: Orange

Used for: Highlights, warnings, attention-grabbing elements

```css
--accent: 24.6 95% 53.1%; /* #ea580c */
```

**Palette:**
- `accent-50`: #fff7ed
- `accent-100`: #ffedd5
- `accent-200`: #fed7aa
- `accent-300`: #fdba74
- `accent-400`: #fb923c
- `accent-500`: #f97316
- `accent-600`: #ea580c ← **Default**
- `accent-700`: #c2410c
- `accent-800`: #9a3412
- `accent-900`: #7c2d12
- `accent-950`: #431407

**Usage:**
- Action buttons (danger actions)
- Highlights in text
- Warning badges
- Gradient accents (sparingly)

---

### Neutral Colors: Slate

Used for: Text, backgrounds, borders, UI elements

```css
--foreground: 222.2 47.4% 11.2%; /* #1e293b in light mode */
--background: 0 0% 100%;          /* #ffffff in light mode */
```

**Palette:**
- `slate-50`: #f8fafc
- `slate-100`: #f1f5f9
- `slate-200`: #e2e8f0
- `slate-300`: #cbd5e1
- `slate-400`: #94a3b8
- `slate-500`: #64748b
- `slate-600`: #475569
- `slate-700`: #334155
- `slate-800`: #1e293b
- `slate-900`: #0f172a
- `slate-950`: #020617

**Usage:**
- Body text: `slate-900` (light) / `slate-50` (dark)
- Muted text: `slate-600` (light) / `slate-400` (dark)
- Borders: `slate-200` (light) / `slate-800` (dark)
- Backgrounds: `slate-50` (light) / `slate-950` (dark)

---

### Semantic Colors

**Success: Green**
```css
--success: 142.1 76.2% 36.3%; /* #16a34a */
```
- Success messages
- "Connected" status
- Positive indicators

**Error: Red**
```css
--destructive: 0 72.2% 50.6%; /* #ef4444 */
```
- Error messages
- "Disconnected" status
- Delete/destructive actions

**Warning: Yellow**
```css
--warning: 47.9 95.8% 53.1%; /* #eab308 */
```
- Warning messages
- Pending states
- Caution indicators

**Info: Blue (Primary)**
- Same as primary color
- Informational messages
- Tips and hints

---

### Dark Mode

Dark mode uses **same hues** but adjusted lightness/saturation for readability.

**Principles:**
- Pure black (#000) is avoided (too harsh) - use `slate-950`
- Pure white (#fff) is avoided in dark mode - use `slate-50`
- Increase saturation slightly for colors in dark mode (appear washed out otherwise)
- Ensure 4.5:1 contrast ratio for text

**CSS Variables (Dark Mode):**
```css
.dark {
  --background: 222.2 84% 4.9%;    /* #020617 - very dark blue */
  --foreground: 210 40% 98%;       /* #f8fafc - off white */
  --primary: 217.2 91.2% 59.8%;    /* lighter blue for dark bg */
  --accent: 24.6 95% 63.1%;        /* lighter orange for dark bg */
  /* ... more variables */
}
```

**Testing Dark Mode:**
- Check all components in both modes
- Verify contrast ratios (use browser devtools)
- Test focus indicators (still visible?)
- Check disabled states (not too faint?)

---

## Typography

### Font Families

**UI Font: Inter**

```css
font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
```

- **Why:** Clean, professional, excellent readability, variable font
- **Weights:** 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Usage:** All UI text (headings, body, labels, buttons)

**Code Font: JetBrains Mono**

```css
font-family: "JetBrains Mono", "Fira Code", "Consolas", "Monaco", monospace;
```

- **Why:** Designed for code, excellent ligatures, clear character distinction
- **Weights:** 400 (regular), 600 (semibold)
- **Usage:** Code blocks, terminal, file paths, JSON

---

### Type Scale

**Tailwind Classes:**

| Class | Size | Line Height | Usage |
|-------|------|-------------|-------|
| `text-xs` | 12px | 16px | Captions, helper text |
| `text-sm` | 14px | 20px | Body text (secondary), labels |
| `text-base` | 16px | 24px | Body text (primary) |
| `text-lg` | 18px | 28px | Large body, callouts |
| `text-xl` | 20px | 28px | Section headings (h3) |
| `text-2xl` | 24px | 32px | Page headings (h2) |
| `text-3xl` | 30px | 36px | Major headings (h1) |
| `text-4xl` | 36px | 40px | Hero headings |

**Font Weights:**

| Class | Weight | Usage |
|-------|--------|-------|
| `font-normal` | 400 | Body text |
| `font-medium` | 500 | Labels, secondary headings |
| `font-semibold` | 600 | Buttons, primary headings |
| `font-bold` | 700 | Emphasis, alerts |

---

### Usage Guidelines

**Headings:**
```tsx
<h1 className="text-3xl font-bold">Page Title</h1>
<h2 className="text-2xl font-semibold">Section Title</h2>
<h3 className="text-xl font-semibold">Subsection Title</h3>
```

**Body Text:**
```tsx
<p className="text-base text-foreground">Primary body text</p>
<p className="text-sm text-muted-foreground">Secondary text, helper text</p>
```

**Labels:**
```tsx
<label className="text-sm font-medium">Field Label</label>
```

**Code:**
```tsx
<code className="font-mono text-sm bg-muted px-1 py-0.5 rounded">inline code</code>
```

---

## Spacing & Layout

### Spacing System

**Base Unit: 4px (Tailwind default)**

| Class | Size | Usage |
|-------|------|-------|
| `space-1` / `p-1` / `m-1` | 4px | Tight spacing (badges, tags) |
| `space-2` / `p-2` / `m-2` | 8px | Small spacing (icon + text) |
| `space-3` / `p-3` / `m-3` | 12px | Compact spacing |
| `space-4` / `p-4` / `m-4` | 16px | **Default** - Card padding, button padding |
| `space-6` / `p-6` / `m-6` | 24px | Section spacing |
| `space-8` / `p-8` / `m-8` | 32px | Large spacing |
| `space-12` / `p-12` / `m-12` | 48px | Extra large spacing |
| `space-16` / `p-16` / `m-16` | 64px | Huge spacing (rare) |

**Common Patterns:**

```tsx
// Card padding
<Card className="p-4">

// Section spacing (vertical)
<div className="space-y-6">

// Grid gaps
<div className="grid grid-cols-2 gap-4">

// Between closely related items
<div className="flex items-center gap-2">
```

---

### Layout

**Container Widths:**
- **Full width:** Most pages (use available space)
- **Max width:** `max-w-7xl` (1280px) for wide content areas
- **Centered:** `mx-auto` for centered containers

**Grid System:**
```tsx
// Two-column layout
<div className="grid grid-cols-2 gap-6">

// Three-column layout
<div className="grid grid-cols-3 gap-4">

// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

**Flexbox:**
```tsx
// Horizontal with space between
<div className="flex items-center justify-between">

// Centered
<div className="flex items-center justify-center">

// Vertical stack
<div className="flex flex-col gap-4">
```

---

## Components

### Core Components (Shadcn)

All components are in `src/components/ui/` and follow Shadcn conventions.

---

#### Button

**Variants:**
- `default` - Primary action (blue background)
- `secondary` - Secondary action (gray background)
- `outline` - Outlined button (transparent bg)
- `ghost` - No background (hover shows bg)
- `destructive` - Dangerous action (red background)
- `link` - Looks like a link

**Sizes:**
- `default` - 40px height
- `sm` - 36px height
- `lg` - 44px height
- `icon` - 40x40px square

**Usage:**
```tsx
import { Button } from "@/components/ui/button"

// Primary CTA
<Button variant="default">Connect</Button>

// Secondary action
<Button variant="outline">Cancel</Button>

// Destructive action
<Button variant="destructive">Disconnect</Button>

// Icon button
<Button variant="ghost" size="icon">
  <IconName className="h-4 w-4" />
</Button>
```

**Guidelines:**
- Use `default` for primary CTA (one per section)
- Use `outline` for secondary actions
- Use `destructive` for delete/disconnect actions
- Always include accessible text or aria-label for icon buttons

---

#### Card

**Usage:**
```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description text</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Main content */}
  </CardContent>
  <CardFooter>
    {/* Actions */}
  </CardFooter>
</Card>
```

**Guidelines:**
- Use for grouping related content
- CardHeader is optional but recommended
- CardFooter is for actions (buttons)
- Add `hover:shadow-lg transition-shadow` for interactive cards

---

#### Input

**Usage:**
```tsx
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

<div>
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" placeholder="you@example.com" />
</div>
```

**Guidelines:**
- Always pair with `<Label>` for accessibility
- Use appropriate `type` (text, email, password, number, etc.)
- Show error state: `<Input className="border-destructive" />`
- Use `placeholder` for hints, not labels

---

#### Dialog (Modal)

**Usage:**
```tsx
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button>Open Dialog</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Dialog Title</DialogTitle>
      <DialogDescription>Dialog description</DialogDescription>
    </DialogHeader>
    {/* Dialog content */}
  </DialogContent>
</Dialog>
```

**Guidelines:**
- Use for focused tasks (forms, confirmations)
- Keep dialogs simple (don't nest dialogs)
- Always include title and description for screen readers
- Closes with Escape key (built-in)

---

#### Badge

**Variants:**
- `default` - Blue badge
- `secondary` - Gray badge
- `outline` - Outlined badge
- `destructive` - Red badge
- `success` - Green badge (custom)

**Usage:**
```tsx
import { Badge } from "@/components/ui/badge"

<Badge variant="default">Connected</Badge>
<Badge variant="destructive">Error</Badge>
<Badge variant="success">Synced</Badge>
```

**Guidelines:**
- Use for status indicators
- Use for tags (with `variant="outline"`)
- Keep text short (1-2 words)
- Don't overuse (visual noise)

---

#### Tabs

**Usage:**
```tsx
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">
    {/* Content 1 */}
  </TabsContent>
  <TabsContent value="tab2">
    {/* Content 2 */}
  </TabsContent>
</Tabs>
```

**Guidelines:**
- Use for switching between views (not navigation)
- 2-5 tabs max (use dropdown if more)
- Consistent tab order across app

---

### Custom Polly Components

These are built using Shadcn primitives and live in `src/components/ui/`.

---

#### IntegrationCard

**Purpose:** Display integration status with stats

**Usage:**
```tsx
import { IntegrationCard } from "@/components/ui/integration-card"

<IntegrationCard
  title="GitHub"
  description="Index your repositories for code search"
  icon={<GitHubIcon />}
  status="connected"
  stats={[
    { label: "Repositories", value: 17 },
    { label: "Last Sync", value: "2 min ago" },
  ]}
  onConnect={handleConnect}
  onDisconnect={handleDisconnect}
/>
```

**Props:**
```typescript
interface IntegrationCardProps {
  title: string
  description: string
  icon?: React.ReactNode
  status: "connected" | "disconnected" | "error"
  stats?: { label: string; value: string | number }[]
  onConnect?: () => void
  onDisconnect?: () => void
}
```

---

#### ChatMessage

**Purpose:** Display user/assistant messages in chat interface

**Usage:**
```tsx
import { ChatMessage } from "@/components/ui/chat-message"

<ChatMessage
  role="assistant"
  content="Here's what I found..."
  timestamp={new Date()}
  isStreaming={false}
/>
```

**Props:**
```typescript
interface ChatMessageProps {
  role: "user" | "assistant"
  content: string
  timestamp?: Date
  isStreaming?: boolean
}
```

---

#### StatusIndicator

**Purpose:** Show connection/status as colored dot

**Usage:**
```tsx
import { StatusIndicator } from "@/components/ui/status-indicator"

<StatusIndicator status="online" label="Connected" size="md" />
```

**Props:**
```typescript
interface StatusIndicatorProps {
  status: "online" | "offline" | "loading" | "error"
  label?: string
  size?: "sm" | "md" | "lg"
}
```

---

#### EmptyState

**Purpose:** Placeholder when no data available

**Usage:**
```tsx
import { EmptyState } from "@/components/ui/empty-state"

<EmptyState
  icon={<InboxIcon />}
  title="No conversations yet"
  description="Start a new conversation to begin using Polly."
  action={{
    label: "New Conversation",
    onClick: handleNew,
  }}
/>
```

**Props:**
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
```

---

## Patterns

### Forms

**Standard form layout:**
```tsx
<form className="space-y-4">
  <div>
    <Label htmlFor="name">Name</Label>
    <Input id="name" type="text" />
  </div>
  <div>
    <Label htmlFor="email">Email</Label>
    <Input id="email" type="email" />
  </div>
  <Button type="submit">Submit</Button>
</form>
```

**Guidelines:**
- Vertical layout (labels above inputs)
- Consistent spacing (`space-y-4` between fields)
- Show validation errors below field
- Disable submit button while submitting

---

### Loading States

**Skeleton (preferred for content):**
```tsx
<div className="space-y-2">
  <div className="h-4 bg-muted rounded w-3/4 animate-pulse" />
  <div className="h-4 bg-muted rounded w-1/2 animate-pulse" />
</div>
```

**Spinner (for actions):**
```tsx
import { Loader2 } from "lucide-react"

<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  Loading...
</Button>
```

**Guidelines:**
- Use skeleton for initial page load
- Use spinner for button actions
- Show progress if possible ("Syncing 5/17 repositories...")

---

### Error States

**Inline error (forms):**
```tsx
<div>
  <Label htmlFor="email">Email</Label>
  <Input id="email" type="email" className="border-destructive" />
  <p className="text-sm text-destructive mt-1">Invalid email address</p>
</div>
```

**Page-level error:**
```tsx
<Card className="border-destructive">
  <CardHeader>
    <CardTitle className="text-destructive">Error</CardTitle>
    <CardDescription>
      Failed to load data. Please try again.
    </CardDescription>
  </CardHeader>
  <CardFooter>
    <Button onClick={retry}>Retry</Button>
  </CardFooter>
</Card>
```

**Guidelines:**
- Be specific (not "Something went wrong")
- Offer action (retry, contact support)
- Show error persistently (don't auto-dismiss)

---

### Empty States

**Use EmptyState component:**
```tsx
<EmptyState
  icon={<InboxIcon />}
  title="No items"
  description="Get started by creating your first item."
  action={{ label: "Create Item", onClick: handleCreate }}
/>
```

**Guidelines:**
- Always show icon (visual interest)
- Explain why empty ("No conversations yet" vs. "Empty")
- Offer action to fix (create, import, connect)

---

## Accessibility

### Keyboard Navigation

**Requirements:**
- ✅ All interactive elements focusable (Tab key)
- ✅ Focus order follows visual order
- ✅ Focus visible (outline or ring)
- ✅ Escape closes modals/dropdowns
- ✅ Enter/Space activates buttons
- ✅ Arrow keys navigate lists/menus

**Testing:**
- Navigate entire app with keyboard only
- Check focus indicator visibility (light and dark mode)
- Test dialogs (open, close, focus trap)

---

### Screen Readers

**Requirements:**
- ✅ ARIA labels for icon buttons
- ✅ Semantic HTML (h1, button, nav, etc.)
- ✅ Alt text for images
- ✅ Form labels associated with inputs
- ✅ Status messages announced (aria-live)

**Testing:**
- Use VoiceOver (macOS) or NVDA (Windows)
- Check that all content is readable
- Verify buttons have clear labels

---

### Color Contrast

**Requirements:**
- ✅ Text contrast ≥ 4.5:1 (WCAG AA)
- ✅ UI element contrast ≥ 3:1
- ✅ Focus indicators ≥ 3:1 against background

**Testing:**
- Use browser devtools (Lighthouse)
- Test dark mode separately
- Don't rely on color alone (use icon + text)

---

## Usage Guidelines

### When to Use What

**Card vs. Dialog:**
- **Card:** Display information on page (can see multiple)
- **Dialog:** Focused task (blocks rest of page)

**Button vs. Link:**
- **Button:** Performs action (submit form, open modal, trigger API call)
- **Link:** Navigates to another page/section

**Badge vs. StatusIndicator:**
- **Badge:** Text label with background (e.g., "Connected", "Admin")
- **StatusIndicator:** Colored dot (e.g., online/offline)

**Input vs. Textarea:**
- **Input:** Single line (name, email, password)
- **Textarea:** Multi-line (description, notes, code)

---

### Component Composition

**Good Example:**
```tsx
<Card>
  <CardHeader>
    <div className="flex items-center justify-between">
      <CardTitle>Title</CardTitle>
      <Badge variant="success">Active</Badge>
    </div>
  </CardHeader>
  <CardContent>
    {/* Content */}
  </CardContent>
  <CardFooter>
    <Button variant="outline">Cancel</Button>
    <Button>Save</Button>
  </CardFooter>
</Card>
```

**Bad Example:**
```tsx
<div className="p-4 rounded border">
  <h2>Title</h2>
  <span className="bg-green-500 px-2 rounded">Active</span>
  {/* Content */}
  <div className="mt-4">
    <button>Cancel</button>
    <button>Save</button>
  </div>
</div>
```

Why bad? Doesn't use design system components, inconsistent styling, not accessible.

---

## Change Log

### Version 1.0 (January 24, 2026)

**Phase 0.5: Initial Design System**

**Added:**
- Shadcn/ui + Tailwind CSS setup
- Core component library (12 components)
- Custom Polly components (IntegrationCard, ChatMessage, StatusIndicator, EmptyState)
- Color system (primary blue, accent orange, slate neutrals)
- Typography (Inter UI, JetBrains Mono code)
- Spacing guidelines (4px base unit)
- Dark mode support
- Accessibility guidelines

**Updated:**
- Navigation/header with new components
- Integration cards (Phase 5)
- Settings panel
- Tab navigation

**Next:**
- Apply to Phases 1.5-17 as they're built
- UI Polish Sprint (after Tier 1) to update remaining UIs

---

### Future Changes

**Document new patterns here as they emerge during Phases 1.5-17:**

**Example:**
```markdown
### Version 1.1 (Phase 12 - Knowledge Graph)

**Added:**
- GraphContainer component (Cytoscape.js wrapper)
- Node detail dialog pattern
- Graph controls panel layout
```

---

## Resources

### External Links

- **Shadcn/ui Docs:** https://ui.shadcn.com/
- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **Radix UI Docs:** https://www.radix-ui.com/docs/primitives
- **WCAG Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **Contrast Checker:** https://webaim.org/resources/contrastchecker/

### Internal Links

- **Phase 0.5 Document:** `PHASE0.5_UI_DESIGN_SYSTEM.md`
- **Component Source:** `src/components/ui/`
- **Tailwind Config:** `tailwind.config.js`
- **Global Styles:** `src/styles/globals.css`

---

**Document Status:** Living document - update as design evolves  
**Owner:** You (update this as team grows)  
**Last Updated:** January 24, 2026

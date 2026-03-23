# Polly iOS Design System

**Version:** 1.0  
**Platform:** iOS 16+  
**Framework:** SwiftUI  
**Last Updated:** March 23, 2026  
**Status:** Mobile-optimized adaptation from Polly Web

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
9. [SafeArea & Notch](#safearea--notch)
10. [Dark Mode](#dark-mode)
11. [Haptics & Feedback](#haptics--feedback)
12. [Change Log](#change-log)

---

## Overview

This document defines Polly's iOS mobile interface. It extends the web design system (`DESIGN_SYSTEM.md`) with mobile-specific considerations: screen size constraints, touch targets, gesture handling, and platform conventions.

### Tech Stack

- **Framework:** SwiftUI (iOS 16+)
- **State Management:** MVVM (Combine)
- **Navigation:** NavigationStack (iOS 16+)
- **Styling:** SwiftUI environment variables + custom Color extensions
- **Icons:** SF Symbols 4+
- **Dark Mode:** Automatic (system settings)

### Philosophy

Polly iOS is designed for **power users on mobile** who value:
- **Density with Touch Comfort** - Compact layouts but generous touch targets (≥44pt)
- **Consistency with iOS** - Respect HIG (Human Interface Guidelines), not just web patterns
- **One-Hand Usage** - Thumb-reachable controls, bottom navigation
- **Offline-First** - Graceful degradation when disconnected from gateway
- **Voice as First-Class** - VoiceOver + voice input deeply integrated
- **Gestures** - Swipe, long-press, pull-to-refresh where natural

---

## Design Principles

### 1. Density + Touch Targets

**Mobile ≠ desktop shrunk down. Information density must serve touch.**

✅ **Do:**
- Minimum 44pt touch targets (Apple standard)
- Stack information vertically (natural scrolling)
- Use bottom sheet/modal for secondary actions (reachable)
- Swipe for common actions (delete, archive, mark done)
- List rows 56-72pt (text + icon + status)

❌ **Don't:**
- Pack too much horizontally (forces side-scrolling)
- Use 32pt buttons (too small, easy to mispress)
- Buttons at top-right (unreachable on iPhone 14 Pro Max)
- Nested modals (confusing navigation)
- Truncate text without visual indicator

**Example:** Message bubble has 44pt hit area (easier to tap), text reflows to 2-3 lines naturally.

---

### 2. Platform Conventions

**Respect iOS patterns. Don't web-ify the mobile app.**

✅ **Do:**
- Use bottom tab bar for main navigation
- Bottom sheet for filters/settings (iOS style)
- Long-press context menu (not right-click)
- Swipe back gesture for navigation
- Navigation title in header (not breadcrumbs)
- Standard status bar (don't hide)

❌ **Don't:**
- Left sidebar (iPad only)
- Top hamburger menu (use tab bar)
- Custom back button (use system gesture)
- Overflow menus (use long-press/swipe)
- Pinch-to-zoom in chat (not natural)

**Example:** "Settings" is a tab, not a menu item. "More actions" uses long-press context menu.

---

### 3. Gesture-Driven UI

**Fingers first. Swipe, tap, long-press.**

✅ **Do:**
- Swipe to delete/archive/mark done (list rows)
- Long-press for context menu (actions, preview)
- Pull-to-refresh (loading states)
- Pinch-to-zoom (images, code blocks only)
- Tap-and-hold for haptic preview

❌ **Don't:**
- Triple-tap for functionality
- Complex multi-finger gestures
- Hover states (no cursor on iOS)
- Undiscoverable gestures (hint in UI)

**Example:** Swipe left on a message → mark read, archive, delete (clear actions).

---

### 4. Vertical-First Layout

**Thumbs scroll vertically. Make scrolling the primary interaction.**

✅ **Do:**
- Vertical stack (VStack) as default
- Horizontal scroll only for supplementary content (tabs, carousels)
- Sticky header/footer (pinned tabs, action buttons)
- Full-width rows (use all available width)
- Content flows naturally without forced truncation

❌ **Don't:**
- Horizontal content as primary UI
- Text truncation without "...more" (use expansion)
- Nested scrolling (parent + child scroll simultaneously)
- More than 2 levels of navigation depth

**Example:** Chat feed scrolls vertically. New message input is sticky at bottom.

---

### 5. Offline Resilience

**Gateway may be away or disconnected. UI must degrade gracefully.**

✅ **Do:**
- Show connection status in header (green dot = connected)
- Cache recent data (messages, tasks, last seen state)
- Queue actions when offline (send message when reconnected)
- Indicate sync status (spinner = syncing, checkmark = synced)
- Show stale data with visual warning

❌ **Don't:**
- Block entire UI if offline (show what you can)
- Lose user input on reconnect (queue it)
- Hide connection status (always visible)
- Crash on network timeout

**Example:** User types a message while offline → send button shows "queued" spinner. When reconnected, message sends automatically.

---

### 6. VoiceOver & Accessibility

**Screen readers must fully navigate app. Descriptive labels mandatory.**

✅ **Do:**
- All interactive elements have labels
- Custom controls expose actions (Cmd+Up = send, Cmd+G = gateway status)
- Image text exposed via `accessibilityLabel`
- Semantic structure (Lists announce count, buttons announce state)
- High contrast in dark mode (≥4.5:1 text)

❌ **Don't:**
- Icon-only buttons (must have label or hint)
- Nested accessibility containers (confuses VoiceOver)
- Custom gestures without VoiceOver actions
- Tiny text in image-heavy sections

**Example:** Voice button has `accessibilityLabel: "Send voice message. Double tap to record, double tap again to send."`

---

## Color System

### Primary Color: Deep Blue

Used for: Links, primary actions, focus states, progress indicators

```swift
// Light mode
let primary = Color(hue: 221.2/360, saturation: 0.832, brightness: 0.533)
// Hex: #2563eb

// Light mode variants
let primary50 = Color(red: 0.937, green: 0.965, blue: 1.0)    // #eff6ff
let primary100 = Color(red: 0.859, green: 0.933, blue: 1.0)  // #dbeafe
let primary500 = Color(red: 0.376, green: 0.647, blue: 0.980) // #3b82f6
let primary600 = Color(red: 0.145, green: 0.392, blue: 0.929) // #2563eb (DEFAULT)
let primary900 = Color(red: 0.118, green: 0.224, blue: 0.541) // #1e3a8a
```

**Usage:**
- Link text (tappable)
- Primary buttons (large CTA)
- Focus rings (text field focus)
- Progress indicators
- Status badge "loading"

---

### Accent Color: Orange

Used for: Highlights, warnings, attention-grabbing, brand accent

```swift
// Light mode
let accent = Color(red: 0.941, green: 0.345, blue: 0.047)
// Hex: #f0903b (Polly brand orange)

// Additional variants
let accentLight = Color(red: 1.0, green: 0.978, blue: 0.933)  // #fff7ed
let accentDim = Color(red: 0.784, green: 0.251, blue: 0.047)  // #c84012
```

**Usage:**
- Action buttons (send, save, confirm)
- Highlights (important message, unread count)
- Warning badges
- Pull-to-refresh spinner
- Active tab indicator
- Attention-grabbing callouts

---

### Neutral Colors: Gray

Used for: Text, backgrounds, borders, disabled states

```swift
// Light mode
let textPrimary = Color(red: 0.118, green: 0.165, blue: 0.282)     // #1e2b48 (dark slate)
let textSecondary = Color(red: 0.280, green: 0.365, blue: 0.522)   // #475c86 (medium slate)
let textTertiary = Color(red: 0.580, green: 0.643, blue: 0.722)    // #94a4b8 (light slate)
let bgPrimary = Color(red: 0.973, green: 0.980, blue: 0.988)       // #f8fafc (almost white)
let bgSecondary = Color(red: 0.894, green: 0.914, blue: 0.940)     // #e4f0f0 (off white)
let border = Color(red: 0.827, green: 0.878, blue: 0.922)          // #d4e0eb (subtle gray)

// Dark mode
let darkTextPrimary = Color(red: 0.973, green: 0.980, blue: 0.988) // #f8fafc
let darkTextSecondary = Color(red: 0.710, green: 0.757, blue: 0.808) // #b5c1ce
let darkBgPrimary = Color(red: 0.008, green: 0.015, blue: 0.043)   // #020617 (almost black)
let darkBgSecondary = Color(red: 0.047, green: 0.075, blue: 0.141) // #0c1323 (navy)
let darkBorder = Color(red: 0.118, green: 0.165, blue: 0.282)      // #1e2b48 (dark slate)
```

**Usage:**
- Body text: `textPrimary`
- Labels, muted text: `textSecondary`
- Placeholders, hints: `textTertiary`
- Card backgrounds: `bgSecondary`
- Separators: `border`

---

### Semantic Colors

**Success: Green**
```swift
let success = Color(red: 0.086, green: 0.639, blue: 0.290) // #16a34a
```
- Connected status (gateway online)
- Synced checkmark
- Success messages
- Positive indicators

**Error: Red**
```swift
let error = Color(red: 0.937, green: 0.267, blue: 0.267) // #ef4444
```
- Disconnected status
- Error messages
- Delete action (destructive)
- Sync failures

**Warning: Yellow**
```swift
let warning = Color(red: 0.920, green: 0.702, blue: 0.051) // #eab308
```
- Pending states (queued message)
- Caution indicators
- Connection degraded

---

### Dark Mode Implementation

Dark mode is **automatic** in iOS — system settings drive the toggle.

```swift
// Define color extensions
extension Color {
    static let bg = Color(UIColor { traitCollection in
        traitCollection.userInterfaceStyle == .dark
            ? UIColor(red: 0.008, green: 0.015, blue: 0.043, alpha: 1) // dark
            : UIColor(red: 0.973, green: 0.980, blue: 0.988, alpha: 1) // light
    })
    
    static let textPrimary = Color(UIColor { traitCollection in
        traitCollection.userInterfaceStyle == .dark
            ? UIColor(red: 0.973, green: 0.980, blue: 0.988, alpha: 1)
            : UIColor(red: 0.118, green: 0.165, blue: 0.282, alpha: 1)
    })
}
```

**Testing Dark Mode:**
- Run in Xcode with both light + dark appearance
- Check all custom views (not system components)
- Verify text contrast (4.5:1 minimum)
- Test toggles (Settings → Display → Light/Dark)

---

## Typography

### Font Families

**UI Font: System (Dynamic Type)**

```swift
// Use system font (SF Pro Display/Text)
// SwiftUI Text defaults to system — no import needed
Text("Hello")
    .font(.system(.body, design: .default))

// SF Mono for code
Text("let x = 42")
    .font(.system(.footnote, design: .monospaced))
```

**Why System Font:**
- Automatic Dynamic Type scaling
- Respects user font size preferences (Settings)
- Native iOS feel
- Dark mode support built-in
- Localizes automatically

**Alternative: Custom Font**
```swift
// If using custom font (e.g., Inter):
Text("Hello")
    .font(.custom("Inter", size: 16))
    .tracking(0.5) // letter spacing
```

---

### Type Scale (Dynamic Type)

SwiftUI uses **named styles** that scale automatically with system settings.

| Style | Size (default) | Use | SwiftUI |
|-------|----------------|-----|---------|
| Large Title | 34pt | Page heading, very prominent | `.largeTitle` |
| Title 1 | 28pt | Section heading | `.title` |
| Title 2 | 22pt | Card header, page subtitle | `.title2` |
| Title 3 | 20pt | Subsection heading | `.title3` |
| Headline | 17pt (bold) | Labels, prominent text | `.headline` |
| Body | 17pt | Primary body text | `.body` |
| Callout | 16pt | Emphatic body text | `.callout` |
| Subheadline | 15pt | Secondary text, labels | `.subheadline` |
| Footnote | 13pt | Captions, helper text | `.footnote` |
| Caption 1 | 12pt | Small captions | `.caption` |
| Caption 2 | 11pt | Tiny text (use sparingly) | `.caption2` |

**Usage:**

```swift
// Heading
Text("Chat")
    .font(.title)
    .fontWeight(.semibold)

// Body
Text("This is a message from the assistant.")
    .font(.body)

// Label
Text("Last sync: 2 min ago")
    .font(.caption)
    .foregroundColor(.gray)

// Code
Text("def hello():")
    .font(.system(.footnote, design: .monospaced))
```

**Dynamic Type Behavior:**
- User sets preferred text size in Settings → Accessibility → Larger Accessibility Sizes
- All text scales automatically (Text respects user choice)
- Test with `CMD+A` (increase), `CMD+-` (decrease) in simulator

---

### Font Weight

```swift
// Named weights
Text("Regular")
    .fontWeight(.regular)    // 400

Text("Medium")
    .fontWeight(.medium)     // 500

Text("Semibold")
    .fontWeight(.semibold)   // 600

Text("Bold")
    .fontWeight(.bold)       // 700
```

**Guidelines:**
- `.body` (regular) for most text
- `.semibold` for headings, button text, emphasis
- `.bold` for critical alerts, very prominent text
- Avoid `.thin` or `.light` (poor accessibility)

---

## Spacing & Layout

### Safe Area & Notch Awareness

iOS 16+ uses **SafeAreaInset** to respect notch, home indicator, and keyboard.

```swift
VStack {
    // Content inside automatically avoids safe area
    Text("Content here")
}
.ignoresSafeArea(edges: .bottom) // If you want to extend under home indicator
```

**Never:**
- Ignore safe area for critical content (buttons, text)
- Place interactive elements under notch
- Assume fixed screen dimensions

**Always:**
- Use `.safeAreaInset` for pinned components (bottom sheet, sticky header)
- Test on iPhone 14 Pro (notch), iPhone SE (no notch)

---

### Spacing System

**Base Unit: 4pt**

| Spacing | Constant | Usage |
|---------|----------|-------|
| 4pt | `.spacing1` | Icon + text (compact) |
| 8pt | `.spacing2` | Small spacing, inline |
| 12pt | `.spacing3` | Compact spacing (between items) |
| 16pt | `.spacing4` | **Default** - card padding, button spacing |
| 24pt | `.spacing6` | Section spacing (VerticalSpacing) |
| 32pt | `.spacing8` | Large spacing (between sections) |
| 48pt | `.spacing12` | Extra large (rare) |

**SwiftUI Spacing:**

```swift
// Define extension
let spacing1: CGFloat = 4
let spacing2: CGFloat = 8
let spacing4: CGFloat = 16
let spacing6: CGFloat = 24

// Usage
VStack(spacing: spacing4) {
    Text("Title")
    Text("Subtitle")
}

HStack(spacing: spacing2) {
    Image(systemName: "checkmark.circle")
    Text("Done")
}

// Padding
Text("Hello")
    .padding(spacing4) // all sides
    .padding(.vertical, spacing6) // vertical only
    .padding(.leading, spacing2) // leading only
```

---

### Layout Grid & Breakpoints

**iPhone Screen Widths:**
- iPhone SE: 375pt
- iPhone 13/14: 390pt
- iPhone 14 Pro: 393pt
- iPhone 14 Pro Max: 430pt

**Layout Strategy:**
- Single column (default) - full width with margins
- Edge insets: 16pt left/right (safe on all sizes)
- Content width: 358-398pt (after insets)
- Max content width: 400pt (comfortable reading)

```swift
VStack(spacing: spacing6) {
    // Full width content
}
.padding(.horizontal, 16)
.frame(maxWidth: .infinity)
```

---

### Common Layout Patterns

**List Row (Chat Bubble, Task Item):**
```swift
VStack(alignment: .leading, spacing: spacing2) {
    HStack {
        VStack(alignment: .leading, spacing: 2) {
            Text("Title")
                .font(.headline)
            Text("Subtitle")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        Spacer()
        Image(systemName: "chevron.right")
            .foregroundColor(.tertiary)
    }
    .contentShape(Rectangle())
}
.padding(spacing4)
.frame(minHeight: 56)
```

**Card (Integration, Status):**
```swift
VStack(alignment: .leading, spacing: spacing3) {
    HStack {
        VStack(alignment: .leading, spacing: 4) {
            Text("Title")
                .font(.headline)
            Text("Description")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        Spacer()
        StatusIndicator(status: .connected)
    }
    
    // Stats row
    HStack {
        Stat(label: "Items", value: "17")
        Stat(label: "Last Sync", value: "2m ago")
    }
}
.padding(spacing4)
.background(Color(UIColor.secondarySystemBackground))
.cornerRadius(12)
```

**Bottom Sheet / Modal:**
```swift
.safeAreaInset(edge: .bottom) {
    VStack(spacing: spacing4) {
        Divider()
        HStack {
            Button(action: cancel) { Text("Cancel") }
            Spacer()
            Button(action: confirm) { Text("Save") }
                .buttonStyle(.borderedProminent)
        }
    }
    .padding(spacing4)
    .background(Color(UIColor.secondarySystemBackground))
}
```

---

## Components

### Custom Components (SwiftUI)

All components live in `Polly/Components/` and follow MVVM structure.

---

#### ChatBubble

**Purpose:** Display messages (user/assistant) with streaming, markdown, links

**Usage:**
```swift
ChatBubble(
    role: .assistant,
    content: "Here's what I found...",
    timestamp: Date(),
    isStreaming: false,
    onTapLink: { url in ... }
)
```

**Props:**
```swift
struct ChatBubbleProps {
    let role: MessageRole            // .user or .assistant
    let content: String              // Markdown supported
    let timestamp: Date?
    let isStreaming: Bool            // Spinner if true
    let onTapLink: (URL) -> Void     // Link handler
}

enum MessageRole {
    case user
    case assistant
}
```

**Styling:**
- User: Orange (#f0903b) bubble, right-aligned
- Assistant: Gray bubble (#e4f0f0 light / #0c1323 dark), left-aligned
- Streaming: Text gradually appears, cursor blinks at end
- Links: Blue, underlined, tappable
- Markdown: Bold, italic, code blocks styled (monospace)

**Accessibility:**
- VoiceOver: Role announced ("message from assistant")
- Time announced ("sent 3 minutes ago")

---

#### Today View Card

**Purpose:** Task, reminder, or process status in Today view

**Usage:**
```swift
TodayCard(
    title: "Review PR #512",
    icon: Image(systemName: "square.and.pencil"),
    status: .active,
    dueDate: Date(),
    onTap: { ... }
)
```

**Props:**
```swift
struct TodayCardProps {
    let title: String
    let icon: Image
    let status: CardStatus         // .active, .done, .overdue
    let dueDate: Date?
    let priority: Priority?         // .high, .normal, .low
    let onTap: () -> Void
    let onSwipeLeft: (() -> Void)?  // Mark done, archive
}

enum CardStatus {
    case active
    case done
    case overdue
    case pending
}
```

**Styling:**
- Height: 72pt (touch-friendly)
- Icon: 32pt, aligned left
- Status indicator: Colored dot (green = done, red = overdue)
- Due date: Smaller text below title
- Right chevron: Indicates tappable

---

#### ConnectionIndicator

**Purpose:** Show gateway connection status (header)

**Usage:**
```swift
ConnectionIndicator(
    status: .connected,
    label: "Home"
)
```

**Props:**
```swift
struct ConnectionIndicatorProps {
    let status: ConnectionStatus   // .connected, .disconnected, .reconnecting
    let label: String?             // "Home", "Away", "Local"
}

enum ConnectionStatus {
    case connected
    case disconnected
    case reconnecting(progress: Double)
    case error(String)
}
```

**Styling:**
- Green dot = connected
- Gray dot = disconnected
- Orange spinner = reconnecting
- Red dot + error text = connection error
- Label right of indicator

---

#### SegmentedPicker (Tabs)

**Purpose:** Switch between views (chat history, settings, etc.)

**Usage:**
```swift
SegmentedPicker(
    options: ["Messages", "Tasks", "Settings"],
    selection: $selectedTab
)
```

**Props:**
```swift
struct SegmentedPickerProps {
    let options: [String]
    @Binding var selection: String
}
```

**Styling:**
- iOS 16+ uses standard `Picker` with `.segmented` style
- Orange underline for active (`.f0903b`)
- Full width, sticky header
- Respect safe area

---

#### VoiceButton

**Purpose:** Record voice message / toggle voice input

**Usage:**
```swift
VoiceButton(
    isRecording: $isRecording,
    onRecordingComplete: { audioData in ... }
)
```

**Props:**
```swift
struct VoiceButtonProps {
    @Binding var isRecording: Bool
    let onRecordingComplete: (Data) -> Void
    let onError: (Error) -> Void
}
```

**Styling:**
- Circular, 56pt diameter
- Orange background (#f0903b)
- Waveform animation while recording
- Haptic feedback on start/end
- VoiceOver: Detailed action labels

---

#### StatusBadge

**Purpose:** Inline status indicator (connected, syncing, error)

**Usage:**
```swift
StatusBadge(
    status: .syncing,
    label: "Syncing..."
)
```

**Props:**
```swift
struct StatusBadgeProps {
    let status: Status            // .connected, .syncing, .error, .offline
    let label: String?
}

enum Status {
    case connected
    case syncing
    case error(String)
    case offline
}
```

**Styling:**
- Height: 24pt
- Compact padding (8pt left/right)
- Rounded corners (12pt)
- Icon + text (or spinner)

---

### System Components (SwiftUI Defaults)

These are native iOS components used throughout Polly.

**Button:**
```swift
// Primary action (orange)
Button(action: send) {
    Label("Send", systemImage: "arrow.up")
}
.buttonStyle(.borderedProminent)
.tint(Color(red: 0.941, green: 0.345, blue: 0.047)) // #f0903b

// Secondary action (outline)
Button(action: cancel) {
    Text("Cancel")
}
.buttonStyle(.bordered)

// Destructive (red)
Button(role: .destructive, action: delete) {
    Label("Delete", systemImage: "trash")
}
.buttonStyle(.bordered)
```

**TextField / SecureField:**
```swift
TextField("Email", text: $email)
    .textInputAutocapitalization(.never)
    .keyboardType(.emailAddress)
    .padding(spacing4)
    .background(Color(UIColor.secondarySystemBackground))
    .cornerRadius(8)

SecureField("Password", text: $password)
    .padding(spacing4)
    .background(Color(UIColor.secondarySystemBackground))
    .cornerRadius(8)
```

**NavigationStack:**
```swift
NavigationStack(path: $navigationPath) {
    List {
        NavigationLink(value: item) {
            Text(item.title)
        }
    }
    .navigationDestination(for: Item.self) { item in
        ItemDetail(item)
    }
}
```

**ToolbarItem / ToolbarItemGroup:**
```swift
.toolbar {
    ToolbarItem(placement: .topBarLeading) {
        Button(action: menu) {
            Image(systemName: "line.3.horizontal")
        }
    }
    
    ToolbarItem(placement: .topBarTrailing) {
        Menu {
            Button("Edit") { ... }
            Button("Share") { ... }
            Button("Delete", role: .destructive) { ... }
        } label: {
            Image(systemName: "ellipsis.circle")
        }
    }
}
```

---

## Patterns

### Chat Interface

**Message Flow:**
1. User types → "Send" button orange (#f0903b)
2. Tap send → message appears in bubble (user color, right-aligned)
3. Message queued if offline (spinner, "Queued" label)
4. Assistant response arrives → gray bubble (left-aligned)
5. If streaming → text appears gradually, cursor blinks

**Layout:**
```swift
VStack(spacing: 0) {
    // Header (sticky)
    HStack {
        ConnectionIndicator()
        Spacer()
        Text("Chat")
            .font(.headline)
        Spacer()
        Button(action: settings) {
            Image(systemName: "gearshape")
        }
    }
    .padding(spacing4)
    .background(Color(UIColor.secondarySystemBackground))
    
    // Messages (scrollable)
    ScrollViewReader { proxy in
        ScrollView {
            LazyVStack(alignment: .leading, spacing: spacing6) {
                ForEach(messages) { message in
                    ChatBubble(message)
                }
            }
            .padding(spacing4)
        }
        .onChange(of: messages.count) { _ in
            proxy.scrollTo(messages.last?.id)
        }
    }
    
    // Input (sticky, safe area)
    .safeAreaInset(edge: .bottom) {
        VStack(spacing: spacing2) {
            HStack(spacing: spacing2) {
                TextField("Message...", text: $inputText)
                    .padding(spacing2)
                    .background(Color(UIColor.secondarySystemBackground))
                    .cornerRadius(8)
                
                Button(action: sendVoice) {
                    Image(systemName: "mic.fill")
                }
                
                Button(action: send) {
                    Image(systemName: "arrow.up.circle.fill")
                }
                .tint(Color(red: 0.941, green: 0.345, blue: 0.047))
            }
            .padding(spacing4)
        }
        .background(Color(UIColor.systemBackground))
    }
}
```

---

### Pull-to-Refresh

**Standard iOS pattern for reloading data:**

```swift
List {
    ForEach(items) { item in
        ItemRow(item)
    }
}
.refreshable {
    do {
        items = try await gateway.sync()
    } catch {
        showError(error)
    }
}
```

**Styling:**
- Spinner appears at top
- Orange accent (#f0903b)
- Release to refresh (user understands)

---

### Swipe Actions

**Conditional actions on list rows:**

```swift
List {
    ForEach(messages) { msg in
        ChatBubble(msg)
            .swipeActions(edge: .trailing) {
                Button(role: .destructive) {
                    delete(msg)
                } label: {
                    Label("Delete", systemImage: "trash")
                }
                
                Button {
                    archive(msg)
                } label: {
                    Label("Archive", systemImage: "archivebox")
                }
            }
            .swipeActions(edge: .leading) {
                Button {
                    markRead(msg)
                } label: {
                    Label("Read", systemImage: "checkmark")
                }
            }
    }
}
```

---

### Loading States

**Skeleton (initial load):**
```swift
struct MessageSkeleton: View {
    var body: some View {
        HStack(spacing: spacing2) {
            Circle()
                .fill(Color.gray.opacity(0.3))
                .frame(width: 8, height: 8)
            
            VStack(alignment: .leading, spacing: 4) {
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 10)
                    .frame(maxWidth: 200, alignment: .leading)
            }
        }
        .redacted(reason: .placeholder)
    }
}
```

**Spinner (actions):**
```swift
Button(action: send) {
    if isLoading {
        ProgressView()
            .progressViewStyle(.circular)
            .scaleEffect(0.9)
    } else {
        Image(systemName: "arrow.up.circle.fill")
    }
}
.disabled(isLoading)
```

---

### Error States

**Inline error (retry):**
```swift
if let error = errorMessage {
    VStack(spacing: spacing2) {
        HStack(spacing: spacing2) {
            Image(systemName: "exclamationmark.triangle.fill")
                .foregroundColor(.red)
            Text(error)
                .font(.callout)
            Spacer()
        }
        Button(action: retry) {
            Text("Retry")
                .frame(maxWidth: .infinity)
        }
        .buttonStyle(.bordered)
    }
    .padding(spacing4)
    .background(Color(red: 1, green: 0.9, blue: 0.9)) // Light red
    .cornerRadius(8)
}
```

---

### Empty States

**No items / no connection:**
```swift
VStack(spacing: spacing6) {
    Image(systemName: "message.circle")
        .font(.system(size: 48))
        .foregroundColor(.gray)
    
    Text("No messages yet")
        .font(.headline)
    
    Text("Start a conversation to get going.")
        .font(.callout)
        .foregroundColor(.secondary)
        .textAlignment(.center)
    
    Button(action: newChat) {
        Text("New Chat")
            .frame(maxWidth: .infinity)
    }
    .buttonStyle(.borderedProminent)
}
.frame(maxHeight: .infinity)
.multilineTextAlignment(.center)
```

---

## Accessibility

### VoiceOver Support

**Requirements:**
- ✅ All interactive elements have labels (or use `accessibilityLabel`)
- ✅ Custom controls expose swipe actions via VoiceOver actions
- ✅ Semantic structure (List, Group, etc.)
- ✅ Images have descriptions
- ✅ Status announced (connected, syncing, error)

**Implementing Custom Actions:**
```swift
Text("Swipe to delete, long-press for more")
    .accessibilityElement(children: .contain)
    .accessibilityAction(named: Text("Delete")) {
        delete()
    }
    .accessibilityAction(named: Text("Mark as Read")) {
        markRead()
    }
```

**Voice Control / Voice Over:**
```swift
Button(action: send) {
    Image(systemName: "arrow.up.circle.fill")
}
.accessibilityLabel(Text("Send message"))
.accessibilityHint(Text("Sends the message to the gateway. Double-tap to send."))
```

---

### Dynamic Type

**Test with large text sizes:**
- iOS Settings → Accessibility → Larger Accessibility Sizes
- Simulate in Xcode: `Environment(\.sizeCategory, .accessibilityExtraLarge)`

**Never:**
- Hard-code font sizes (use named styles)
- Truncate text without expansion
- Fix frame heights (let content flow)

**Always:**
- Use `.lineLimit(nil)` for expandable text
- Test at `.accessibilityExtraLarge` (biggest size)

---

### Color Contrast

**Requirements:**
- ✅ Text: 4.5:1 (dark on light, light on dark)
- ✅ UI elements: 3:1 (buttons, borders, icons)
- ✅ Focus indicators: 3:1 against background

**Testing:**
- Use accessibility inspector (Xcode)
- Check dark mode separately
- Don't rely on color alone (pair with icons/text)

---

## SafeArea & Notch

### Handling Different iPhone Models

**iPhone Models:**
- **iPhone SE (3rd gen):** No notch, no Dynamic Island
- **iPhone 13/14/15:** Notch
- **iPhone 14 Pro/15 Pro:** Dynamic Island (larger notch area)

**Safe Area Behavior:**
- SwiftUI automatically respects safe area
- Content inside `VStack { }` won't overlap notch/home indicator
- Use `.ignoresSafeArea()` cautiously (only for full-bleed images/backgrounds)

**Testing:**
```swift
// Simulate different devices
Xcode: Scheme → Run → Choose device simulator
```

**Critical Rule:**
- Never place buttons, text input, or links in notch/home indicator area
- Use `.safeAreaInset` for pinned components (nav bar, input field)

---

## Dark Mode

### System Integration

Polly respects system dark mode setting (not a toggle in app).

```swift
// Query environment
@Environment(\.colorScheme) var colorScheme

if colorScheme == .dark {
    // Dark mode specific code
}
```

**Testing:**
- Xcode: Scheme → Run → Environment Overrides → Appearance
- iPhone: Settings → Display & Brightness → Light/Dark
- Toggle in Control Center

### Color Pair Definition

```swift
extension Color {
    static let bg = Color(UIColor { traitCollection in
        traitCollection.userInterfaceStyle == .dark
            ? UIColor(red: 0.008, green: 0.015, blue: 0.043, alpha: 1)  // #020617
            : UIColor(red: 0.973, green: 0.980, blue: 0.988, alpha: 1)  // #f8fafc
    })
}
```

### Light/Dark Pairing

| Component | Light | Dark |
|-----------|-------|------|
| Background | `#f8fafc` | `#020617` |
| Card bg | `#e4f0f0` | `#0c1323` |
| Text primary | `#1e2b48` | `#f8fafc` |
| Text secondary | `#475c86` | `#b5c1ce` |
| Border | `#d4e0eb` | `#1e2b48` |
| Primary button | `#2563eb` | `#60a5fa` (lighter) |
| Accent button | `#f0903b` | `#f0903b` (same) |

---

## Haptics & Feedback

### Haptic Patterns

**Light feedback (UI feedback):**
```swift
import UIKit

let feedback = UIImpactFeedbackGenerator(style: .light)
feedback.impactOccurred()
```
- User taps button
- List item selected
- Subtle confirmation

**Medium feedback (action confirmation):**
```swift
let feedback = UIImpactFeedbackGenerator(style: .medium)
feedback.impactOccurred()
```
- Message sent
- Data synced
- Action completed

**Heavy feedback (destructive action):**
```swift
let feedback = UIImpactFeedbackGenerator(style: .heavy)
feedback.impactOccurred()
```
- Delete message
- Disconnect gateway
- Error alert

**Selection feedback (picker/segmented):**
```swift
let feedback = UISelectionFeedbackGenerator()
feedback.selectionChanged()
```
- Switch tabs
- Select item in list
- Toggle setting

---

### Sound + Haptics

**Message received:**
```swift
// Play notification sound + light haptic
NotificationCenter.default.post(name: NSNotification.Name("NewMessage"))
let feedback = UINotificationFeedbackGenerator()
feedback.notificationOccurred(.success)
```

**Error notification:**
```swift
let feedback = UINotificationFeedbackGenerator()
feedback.notificationOccurred(.error)
```

---

## Navigation Structure

### Tab-Based Navigation

```
├── 📱 Chat (main feed)
├── 📋 Today (tasks, reminders, processes)
├── ⚙️ Settings
└── 🔗 Gateway (connection status, manage)
```

**Implementation:**
```swift
@State var selectedTab: Int = 0

TabView(selection: $selectedTab) {
    ChatView()
        .tabItem {
            Label("Chat", systemImage: "message")
        }
        .tag(0)
    
    TodayView()
        .tabItem {
            Label("Today", systemImage: "calendar.circle")
        }
        .tag(1)
    
    SettingsView()
        .tabItem {
            Label("Settings", systemImage: "gearshape")
        }
        .tag(2)
    
    GatewayView()
        .tabItem {
            Label("Gateway", systemImage: "wifi")
        }
        .tag(3)
}
```

---

## Change Log

### Version 1.0 (March 23, 2026)

**Polly iOS Design System Foundation**

**Added:**
- Mobile-specific color system (light/dark mode)
- SwiftUI typography (Dynamic Type support)
- Touch-friendly spacing (44pt minimum targets)
- Custom iOS components (ChatBubble, TodayCard, VoiceButton)
- Accessibility guidelines (VoiceOver, Dynamic Type, contrast)
- Safe area / notch handling
- Gesture patterns (swipe, long-press, pull-to-refresh)
- Haptics & feedback
- Dark mode implementation
- Navigation structure (tab-based)

**Next:**
- Implement components in codebase
- Test on device (iPhone 14 Pro, iPhone SE)
- Accessibility audit (VoiceOver, Dynamic Type)
- Dark mode verification
- Gather feedback from team

---

## Resources

### Apple HIG References

- **Human Interface Guidelines:** https://developer.apple.com/design/human-interface-guidelines/
- **Accessibility:** https://developer.apple.com/accessibility/
- **SwiftUI:** https://developer.apple.com/swiftui/
- **SF Symbols:** https://developer.apple.com/sf-symbols/

### Tools

- **Xcode:** Built-in color/accessibility inspectors
- **Contrast Checker:** https://webaim.org/resources/contrastchecker/
- **Device Simulator:** Xcode → Devices → Simulators

### Related Docs

- **Polly Web Design System:** `DESIGN_SYSTEM.md`
- **Aight (OpenClaw iOS):** Gateway integration docs
- **Tailscale Integration:** Local network connectivity

---

**Document Status:** Foundation complete, ready for component implementation  
**Platform:** iOS 16+  
**Last Updated:** March 23, 2026

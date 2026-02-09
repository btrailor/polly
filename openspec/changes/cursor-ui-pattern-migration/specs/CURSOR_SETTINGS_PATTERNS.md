# Cursor Settings Page Patterns (Design Reference)

**Purpose:** Document patterns observed from Cursor's settings page that we adopt for Polly's settings redesign and general UI structure.

**Reference:** Cursor settings page screenshot analysis

---

## Layout Structure

### Two-Column Layout

```
┌─────────────────────────────────────────────────────────┐
│ Left Sidebar (240px)      │ Main Content (flexible)     │
│                            │                             │
│ [User Account]             │ [Page Title]                │
│ - Avatar                   │                             │
│ - Email                    │ [Sections]                  │
│ - Plan                     │ - Manage Account            │
│                            │ - Upgrade                   │
│ [Search: ⌘F]               │ - Preferences               │
│                            │ - Notifications             │
│ [Navigation Menu]         │                             │
│ - General (active)         │ [Settings Items]            │
│ - Agents                    │ - Toggle switches          │
│ - Tab                       │ - Action buttons           │
│ - Models                    │ - Descriptions              │
│ - Cloud Agents              │                             │
│ - Tools & MCP               │                             │
│ - Rules and Commands        │                             │
│ - Indexing & Docs           │                             │
│ - Network                   │                             │
│ - Beta                      │                             │
│ - Docs                      │                             │
└─────────────────────────────────────────────────────────┘
```

## Key Patterns

### 1. Left Sidebar Structure

#### User Account Section (Top)
- **Purpose:** Show user context and account status
- **Elements:**
  - Circular avatar (initials or icon)
  - Email address (truncated if long)
  - Plan/subscription level
- **Styling:** Subtle border-bottom separator

#### Search Bar
- **Placeholder:** "Search settings ⌘F"
- **Keyboard shortcut:** ⌘F (Cmd+F) to focus
- **Position:** Below account section
- **Functionality:** Filter settings by name/description

#### Navigation Menu
- **Structure:** Icon + label for each section
- **Active state:** Background highlight + accent color
- **Hover state:** Subtle background change
- **Icons:** Consistent icon set (Lucide or similar)
- **Spacing:** Comfortable padding between items

### 2. Main Content Area

#### Page Title
- **Position:** Top of content area
- **Styling:** Large, bold heading
- **Optional:** Subtitle/description below title

#### Sections
- **Organization:** Logical grouping of related settings
- **Structure:**
  - Section heading (h3)
  - Optional section description
  - Settings items within section
- **Spacing:** Generous margin between sections

#### Settings Items

**Toggle Switch Pattern:**
- **Layout:** Label on left, toggle on right
- **Description:** Below label/toggle
- **Visual:** Green when on, gray when off
- **Interaction:** Click to toggle

**Action Button Pattern:**
- **Layout:** Label on left, button on right
- **Button content:** Text + icon (e.g., "Open" with external link icon)
- **Description:** Below label/button
- **Interaction:** Click to perform action (open modal, navigate, etc.)

**Input Field Pattern:**
- **Layout:** Label above, input below
- **Description:** Below input
- **Validation:** Show errors inline

### 3. Visual Design Principles

#### Hierarchy
1. **Primary:** Page title, section headings
2. **Secondary:** Setting labels, button text
3. **Tertiary:** Descriptions, helper text

#### Spacing
- **Sections:** 32px margin-bottom
- **Settings items:** 24px margin-bottom
- **Within items:** 4-8px between label and description

#### Colors
- **Active state:** Accent color (e.g., blue/purple)
- **Background:** Subtle background for active nav item
- **Text:** Primary for labels, secondary for descriptions
- **Borders:** Subtle borders for separation

#### Typography
- **Headings:** 18px, font-weight 600
- **Labels:** 14px, font-weight 500
- **Descriptions:** 13px, color: text-secondary

## General UI Principles (Applicable Beyond Settings)

### 1. Two-Column Navigation Pattern
- Left sidebar for navigation/hierarchy
- Main content area for details
- Applicable to: Settings, Preferences, Configuration pages

### 2. Search-First Design
- Search bar prominently placed
- Keyboard shortcut clearly indicated
- Quick access to any setting/content

### 3. Clear Visual Hierarchy
- Sections → Items → Descriptions
- Consistent spacing and typography
- Visual grouping with borders/backgrounds

### 4. Action Affordances
- Buttons clearly indicate actions
- Icons reinforce button purpose
- Toggles show state clearly

### 5. Contextual Information
- Descriptions explain purpose
- Help text where needed
- User context (account info) visible

### 6. Progressive Disclosure
- Sections collapse/expand (if applicable)
- Advanced settings hidden by default
- Related settings grouped together

## Implementation Notes for Polly

### Settings Sections (Polly)

1. **General**
   - Account management
   - Editor preferences
   - Keyboard shortcuts
   - Import settings
   - Reset dialogs

2. **Agents** (when implemented)
   - Agent management
   - Agent configuration

3. **API Keys**
   - Provider API keys
   - Key management
   - Test connections

4. **Models**
   - Model configuration
   - Routing settings
   - Provider settings

5. **Domains**
   - Domain configuration
   - Domain management

6. **Notes**
   - Notes preferences
   - Template settings
   - Vault configuration

7. **Compression**
   - Compression settings
   - Compression stats

8. **Integrations**
   - Obsidian integration
   - Other integrations

9. **Mental Models**
   - Mental model management
   - Model configuration

10. **Advanced**
    - Advanced settings
    - Debug options
    - System info

### Migration Strategy

1. **Phase 1:** Redesign layout (sidebar + main content)
2. **Phase 2:** Update navigation structure
3. **Phase 3:** Convert settings items to new patterns
4. **Phase 4:** Add search functionality
5. **Phase 5:** Polish and consistency pass

### Reusability

These patterns can be applied to:
- Settings pages
- Preference dialogs
- Configuration panels
- Any hierarchical navigation + detail view

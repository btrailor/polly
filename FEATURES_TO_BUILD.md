# Features to Build

**Project:** Polly - Edge-Native Personal AI System  
**Purpose:** Track planned features with implementation details for future development  
**Last Updated:** February 3, 2026

---

## High Priority Features

### 1. Theme Customization System
**Status:** 🔵 Planned  
**Priority:** High (UX Enhancement)  
**Estimated Effort:** Medium (2-3 days)  
**Target Phase:** 0.8 or 1.0

**Feature Description:**
Allow users to customize the app's appearance with:
- Custom accent colors (currently orange `#f0903b`)
- Light/Dark theme toggle
- Auto theme based on time of day or system preferences
- Theme presets (e.g., "Orange Dark", "Blue Light", "Purple Dark")

**User Benefits:**
- Personalization enhances user engagement
- Light theme for daytime work reduces eye strain
- Accessibility for users with visual preferences
- Matches user's system theme (macOS light/dark mode)

---

#### Technical Implementation Plan

##### Phase 1: CSS Variable Refactoring
**Goal:** Consolidate all colors into CSS variables for easy theming

**Current State:**
- Some variables exist in `:root` (main.css lines 6-65)
- Many hardcoded colors throughout CSS files
- Inconsistent use of variables vs hex codes

**Tasks:**
1. **Audit all CSS files** for color usage
   ```bash
   grep -rn "#[0-9a-fA-F]\{6\}" src/renderer/styles/
   ```

2. **Define comprehensive CSS variable system:**
   ```css
   :root {
     /* Theme-specific variables */
     --theme-accent: #f0903b;
     --theme-accent-hover: #ff9f4d;
     --theme-bg-primary: #1e1e1e;
     --theme-bg-secondary: #252525;
     --theme-bg-tertiary: #2a2a2a;
     --theme-text-primary: #e0e0e0;
     --theme-text-secondary: #808080;
     --theme-border: #2a2a2a;
     
     /* Component-specific (derived from theme) */
     --button-bg: var(--theme-accent);
     --button-hover: var(--theme-accent-hover);
     --sidebar-bg: var(--theme-bg-primary);
     --message-user-bg: var(--theme-accent);
     /* etc... */
   }
   ```

3. **Replace all hardcoded colors** with CSS variables
   - Priority files: main.css, chat-sidebar.css, ribbon.css, three-column.css

4. **Create theme variants:**
   ```css
   /* Dark theme (default) */
   [data-theme="dark"] {
     --theme-bg-primary: #1e1e1e;
     --theme-text-primary: #e0e0e0;
   }
   
   /* Light theme */
   [data-theme="light"] {
     --theme-bg-primary: #fafafa;
     --theme-text-primary: #0a0a0a;
   }
   ```

**Files to Modify:**
- `/electron-app/src/renderer/styles/main.css` - Main variable definitions
- `/electron-app/src/renderer/styles/chat-sidebar.css` - Replace hardcoded colors
- `/electron-app/src/renderer/styles/ribbon.css` - Replace hardcoded colors
- `/electron-app/src/renderer/styles/three-column.css` - Replace hardcoded colors
- `/electron-app/src/renderer/styles/obsidian-theme.css` - Theme system integration

---

##### Phase 2: Theme Switching Logic
**Goal:** JavaScript logic to apply themes dynamically

**Implementation:**

1. **Add theme state management** in app.js:
   ```javascript
   // Theme management
   const DEFAULT_THEME = {
     mode: 'dark', // 'light' | 'dark' | 'auto'
     accentColor: '#f0903b',
     autoLightStart: '07:00', // Light theme starts at 7am
     autoLightEnd: '19:00'    // Dark theme starts at 7pm
   };
   
   function loadTheme() {
     const saved = localStorage.getItem('polly-theme');
     return saved ? JSON.parse(saved) : DEFAULT_THEME;
   }
   
   function saveTheme(theme) {
     localStorage.setItem('polly-theme', JSON.stringify(theme));
   }
   
   function applyTheme(theme) {
     const mode = theme.mode === 'auto' ? getAutoMode(theme) : theme.mode;
     
     // Apply theme mode
     document.documentElement.setAttribute('data-theme', mode);
     
     // Apply custom accent color
     document.documentElement.style.setProperty('--theme-accent', theme.accentColor);
     document.documentElement.style.setProperty('--theme-accent-hover', lightenColor(theme.accentColor, 10));
   }
   
   function getAutoMode(theme) {
     const now = new Date();
     const currentTime = now.getHours() * 60 + now.getMinutes();
     const [lightH, lightM] = theme.autoLightStart.split(':').map(Number);
     const [darkH, darkM] = theme.autoLightEnd.split(':').map(Number);
     const lightStart = lightH * 60 + lightM;
     const darkStart = darkH * 60 + darkM;
     
     return (currentTime >= lightStart && currentTime < darkStart) ? 'light' : 'dark';
   }
   
   function lightenColor(hex, percent) {
     // Color manipulation helper
     // Convert hex to RGB, lighten, convert back
   }
   
   // Initialize on load
   const currentTheme = loadTheme();
   applyTheme(currentTheme);
   
   // If auto mode, check every minute
   if (currentTheme.mode === 'auto') {
     setInterval(() => applyTheme(currentTheme), 60000);
   }
   ```

2. **Alternative: Use system preferences** (macOS/Windows):
   ```javascript
   // Electron main process can detect system theme
   const { nativeTheme } = require('electron');
   
   nativeTheme.on('updated', () => {
     const isDark = nativeTheme.shouldUseDarkColors;
     // Send to renderer process
     win.webContents.send('system-theme-changed', isDark ? 'dark' : 'light');
   });
   ```

**Files to Create/Modify:**
- `/electron-app/src/renderer/app.js` - Add theme management functions
- `/electron-app/src/main/main.js` - Optional system theme detection

---

##### Phase 3: Settings UI
**Goal:** User interface for customizing theme

**Implementation:**

1. **Add Theme tab to Settings view** (index.html):
   ```html
   <!-- Tab: Theme -->
   <div class="settings-tab-content hidden" id="tab-theme">
     <div class="settings-section">
       <h3>Appearance</h3>
       
       <div class="form-group">
         <label>Theme Mode</label>
         <select id="settings-theme-mode">
           <option value="dark">Dark</option>
           <option value="light">Light</option>
           <option value="auto">Auto (Time-based)</option>
           <option value="system">Follow System</option>
         </select>
       </div>
       
       <div class="form-group" id="auto-theme-settings">
         <label>Light Theme Hours</label>
         <div style="display: flex; gap: 8px; align-items: center;">
           <input type="time" id="theme-light-start" value="07:00" />
           <span>to</span>
           <input type="time" id="theme-light-end" value="19:00" />
         </div>
         <p class="form-hint">Light theme will activate during these hours</p>
       </div>
     </div>
     
     <div class="settings-section">
       <h3>Accent Color</h3>
       
       <div class="form-group">
         <label>Accent Color</label>
         <div class="color-presets">
           <button class="color-preset active" data-color="#f0903b" style="background: #f0903b;" title="Orange (Default)"></button>
           <button class="color-preset" data-color="#7f6df2" style="background: #7f6df2;" title="Purple"></button>
           <button class="color-preset" data-color="#61afef" style="background: #61afef;" title="Blue"></button>
           <button class="color-preset" data-color="#c678dd" style="background: #c678dd;" title="Pink"></button>
           <button class="color-preset" data-color="#98c379" style="background: #98c379;" title="Green"></button>
           <button class="color-preset" data-color="#e06c75" style="background: #e06c75;" title="Red"></button>
         </div>
         <div style="margin-top: 12px;">
           <input type="color" id="theme-accent-custom" value="#f0903b" />
           <label for="theme-accent-custom" style="margin-left: 8px;">Custom Color</label>
         </div>
       </div>
       
       <div class="form-group">
         <button class="btn btn-secondary" id="btn-reset-theme">Reset to Default</button>
       </div>
     </div>
     
     <div class="settings-section">
       <h3>Preview</h3>
       <div class="theme-preview">
         <div class="preview-panel">
           <div class="preview-titlebar"></div>
           <div class="preview-content">
             <div class="preview-message user">User message</div>
             <div class="preview-message assistant">Assistant message</div>
             <button class="preview-button">Button</button>
           </div>
         </div>
       </div>
     </div>
   </div>
   ```

2. **Add Settings tab navigation:**
   ```html
   <button class="settings-tab" data-tab="theme">
     <i data-lucide="palette"></i>
     <span>Theme</span>
   </button>
   ```

3. **Add event listeners** for theme settings:
   ```javascript
   // Theme mode selector
   document.getElementById('settings-theme-mode').addEventListener('change', (e) => {
     const theme = loadTheme();
     theme.mode = e.target.value;
     saveTheme(theme);
     applyTheme(theme);
     
     // Show/hide auto settings
     const autoSettings = document.getElementById('auto-theme-settings');
     autoSettings.style.display = e.target.value === 'auto' ? 'block' : 'none';
   });
   
   // Color preset buttons
   document.querySelectorAll('.color-preset').forEach(btn => {
     btn.addEventListener('click', () => {
       const color = btn.dataset.color;
       const theme = loadTheme();
       theme.accentColor = color;
       saveTheme(theme);
       applyTheme(theme);
       
       // Update active state
       document.querySelectorAll('.color-preset').forEach(b => b.classList.remove('active'));
       btn.classList.add('active');
     });
   });
   
   // Custom color picker
   document.getElementById('theme-accent-custom').addEventListener('input', (e) => {
     const theme = loadTheme();
     theme.accentColor = e.target.value;
     saveTheme(theme);
     applyTheme(theme);
   });
   ```

**Files to Modify:**
- `/electron-app/src/renderer/index.html` - Add theme settings UI
- `/electron-app/src/renderer/app.js` - Add theme settings event listeners
- `/electron-app/src/renderer/styles/main.css` - Add theme preview styles

---

##### Phase 4: Theme Presets (Optional)
**Goal:** Pre-built themes users can select

**Implementation:**

```javascript
const THEME_PRESETS = {
  'orange-dark': {
    name: 'Orange Dark (Default)',
    mode: 'dark',
    accentColor: '#f0903b'
  },
  'purple-dark': {
    name: 'Purple Dark',
    mode: 'dark',
    accentColor: '#7f6df2'
  },
  'blue-light': {
    name: 'Blue Light',
    mode: 'light',
    accentColor: '#61afef'
  },
  'obsidian': {
    name: 'Obsidian',
    mode: 'dark',
    accentColor: '#9d7cd8',
    // Could also include other custom properties
  }
};

function applyPreset(presetId) {
  const preset = THEME_PRESETS[presetId];
  if (preset) {
    saveTheme(preset);
    applyTheme(preset);
  }
}
```

**UI Addition:**
```html
<div class="form-group">
  <label>Theme Presets</label>
  <div class="theme-presets">
    <button class="theme-preset-card" data-preset="orange-dark">
      <div class="preset-preview" style="background: #1e1e1e; border-left: 4px solid #f0903b;"></div>
      <span>Orange Dark</span>
    </button>
    <button class="theme-preset-card" data-preset="purple-dark">
      <div class="preset-preview" style="background: #1e1e1e; border-left: 4px solid #7f6df2;"></div>
      <span>Purple Dark</span>
    </button>
    <!-- More presets... -->
  </div>
</div>
```

---

#### Technical Challenges & Solutions

##### Challenge 1: Color Consistency Across Components
**Problem:** Ensuring all components update when theme changes

**Solution:**
- Use CSS variables exclusively (no hardcoded colors)
- Create a comprehensive variable mapping
- Test all views after theme switch

##### Challenge 2: Performance
**Problem:** Theme switching might cause layout reflow/repaint

**Solution:**
- Use CSS variables (efficient browser updates)
- Batch DOM updates if manipulating multiple elements
- Use `will-change` CSS property for animated elements

##### Challenge 3: Persistence
**Problem:** Theme must persist across app restarts

**Solution:**
- Store in localStorage: `polly-theme`
- Apply immediately on page load (before first render to avoid flash)
- Fallback to default if corrupt

##### Challenge 4: Auto Theme Timing
**Problem:** Checking time every minute might be overkill

**Solution:**
- Calculate next theme change time, set single timeout
- Only run interval if user is actively using app
- Option to use system theme instead (more efficient)

---

#### Files Reference

**Files to Create:**
- `/electron-app/src/renderer/lib/theme-manager.js` - Separate theme logic (optional, good for organization)

**Files to Modify:**
1. `/electron-app/src/renderer/styles/main.css`
   - Refactor `:root` variables (lines 6-65)
   - Add `[data-theme="light"]` and `[data-theme="dark"]` variants
   - Add theme preview component styles

2. `/electron-app/src/renderer/styles/chat-sidebar.css`
   - Replace `#f0903b` with `var(--theme-accent)` (lines 98, 203, 254, 266)
   - Replace hardcoded colors with variables

3. `/electron-app/src/renderer/styles/ribbon.css`
   - Replace accent colors with variables (lines 42, 86, 98)

4. `/electron-app/src/renderer/styles/three-column.css`
   - Replace accent colors with variables (line 174)

5. `/electron-app/src/renderer/index.html`
   - Add Theme tab to settings (after line ~512)
   - Add theme tab button to settings navigation

6. `/electron-app/src/renderer/app.js`
   - Add theme management functions (around line 900)
   - Add settings event listeners (around line 1200)
   - Initialize theme on app load (around line 2200)

7. `/electron-app/src/main/main.js` (optional)
   - Add system theme detection with nativeTheme API
   - Send theme updates to renderer process

---

#### Testing Checklist

When implementing:
- [ ] All colors update when switching light/dark
- [ ] Custom accent color applies to all UI elements
- [ ] Auto mode switches correctly based on time
- [ ] System mode follows macOS/Windows theme changes
- [ ] Theme persists after app restart
- [ ] No flash of wrong theme on startup
- [ ] Settings UI shows current theme correctly
- [ ] Color picker reflects current accent color
- [ ] Preview accurately represents selected theme
- [ ] All views tested: dashboard, chat, settings, calendar, etc.
- [ ] Text remains readable in both themes (contrast check)
- [ ] Buttons, borders, highlights all use theme colors

---

#### User Documentation Needed

When feature is complete:
1. **Settings page in-app help:**
   - Explain auto mode vs system mode
   - Show example of custom color selection
   - Note that theme applies across all views

2. **README update:**
   - Mention theme customization feature
   - Screenshot of theme settings

3. **Changelog entry:**
   - Document all theme options available
   - Note any breaking changes (if theme storage format changes)

---

## Medium Priority Features

### 2. User Profile System (Phase 13b)
**Status:** 🔵 Planned  
**Priority:** High (Personalization Foundation)  
**Estimated Effort:** Large (3 weeks, 6 implementation phases)  
**Target Phase:** Phase 13b  
**Related:** Phase 1.5 ✅, Phase 11 ✅, Phase 13a ✅, Phase 16 ✅, Phase 24

**Feature Description:**
Comprehensive user profile system that learns your preferences, thinking patterns, and domain expertise to provide deeply personalized AI interactions.

**Overview:**
- Polly learns how you think, communicate, and work
- Adapts responses to your communication style
- Respects your expertise levels across domains
- All profile data stored in human-readable markdown
- You can edit your profile directly (no black boxes)

**Key Features:**

#### Profile Management
- View your complete profile in Settings
- Edit profile sections directly (markdown files)
- Import profile from existing notes/vault
- Export profile for backup or migration
- Profile quality scoring (prevents generic content)

#### Bootstrap Mechanisms
1. **Corpus Inference:** Import existing Obsidian vault or markdown files
2. **Light Onboarding:** 5-10 min conversational questionnaire (7 questions)
3. **Progressive Disclosure:** Learn through ongoing conversations
4. **Manual Invocation:** `@profile [statement]` command to add entries

#### Profile Sections
- **Active Context:** Life stage, projects, constraints, priorities
- **Domains:** One sub-profile per domain (e.g., code, audio, writing)
- **Thinking Patterns:** Mental models, decision heuristics, problem-solving approaches
- **Communication Preferences:** Tone, format, depth, how you handle pushback
- **Infrastructure Context:** Hardware, tools, development environment
- **Custom Sections:** User-specific sections (e.g., "Practice Containers")

#### Context Injection
- **Local Models:** Profile context injected into system prompt
- **Cloud Models:** Profile-aware meta-queries before sending to cloud
- **Confidence Thresholds:** Adapt escalation based on domain expertise

**User Benefits:**
- Polly understands your communication style (concise vs. verbose)
- Respects your expertise (explains concepts at right level)
- Adapts to your thinking patterns (functional vs. imperative mindset)
- Surfaces relevant connections from your profile
- Learns your infrastructure (suggests compatible tools)
- All data in markdown (you own it, you control it)

**Competitive Positioning:**
- **"Polly: Personal AI you own"** vs **"Uare.ai: Personal AI you rent"**
- Local storage, user control, practice augmentation
- Market validated: Uare.ai raised $10.3M for personalized AI

**Storage Structure:**
```
vault/.polly/user/
├── core.md                    # Main profile
├── domains/                   # Domain-specific profiles
│   ├── sigils.md              # Code domain
│   ├── signals.md             # Audio domain
│   ├── scrolls.md             # Writing domain
│   ├── sights.md              # Visual domain
│   └── glyphs.md              # Systems domain
├── patterns/                  # Cross-domain patterns
│   ├── workflow-rhythms.md
│   ├── decision-heuristics.md
│   └── energy-management.md
└── history/                   # Weekly/monthly digests
```

**API Endpoints (14 planned):**
- `GET /profile` - Retrieve full profile
- `GET /profile/section/:section` - Get specific section
- `PUT /profile/section/:section` - Update section
- `POST /profile/bootstrap/corpus` - Import from vault
- `POST /profile/bootstrap/onboarding` - Start questionnaire
- `POST /profile/statement` - Add manual statement
- `GET /profile/domains/:domain` - Get domain profile
- `PUT /profile/domains/:domain` - Update domain profile
- `GET /profile/quality-score` - Check profile quality
- And 5 more...

**Quality Scoring System:**
5 dimensions prevent generic content:
- **Specificity:** Specific terms vs. generic platitudes
- **Actionability:** Can personas change behavior based on this?
- **Consistency:** Matches conversation history?
- **Conciseness:** Information density
- **Cross-Reference:** Links to other profile sections

**Thresholds:**
- ≥0.7: High quality, auto-save
- 0.5-0.7: Medium, ask user to review
- <0.5: Low quality, reject

**User Workflow Example:**

```
# First Time Setup
User: Opens Polly for first time
Polly: "Let me learn about you. I can:
  1. Import from your existing notes (5 min)
  2. Ask you a few questions (10 min)
  3. Learn as we talk (gradual)
  Choose one or combine them."

# Ongoing Usage
User: "I prefer concise responses"
Polly: [Detects profile statement]
      "Got it. I'll add this to your profile:
       Communication > Prefers concise responses
       [Save] [Edit] [Cancel]"

# Profile-Aware Responses
User: "How do I implement audio routing?"
Polly: [Checks profile: Signals domain, experience level]
      [Adjusts response depth accordingly]
      "Since you have experience with Max/MSP..."

# Manual Profile Entry
User: "@profile I'm transitioning from Max to SuperCollider"
Polly: "Added to Signals domain profile:
       Active Context > Transitioning from Max to SuperCollider
       This helps me provide relevant comparisons."
```

**Technical Implementation:**
- Markdown-based storage (human-readable)
- LLM-augmented profile building
- Quality scoring prevents slop
- Hybrid migration from Phase 13a patterns
- Integration with Phase 24 Orchestrator (profile-aware workflows)

**Files to Create:**
- `core/profile/` (new module)
  - `profile_manager.py` - CRUD operations
  - `bootstrap_manager.py` - 4 bootstrap mechanisms
  - `quality_scorer.py` - 5-dimension scoring
  - `context_injector.py` - Profile-aware prompts
- `vault/.polly/user/` (profile storage)
- Settings UI: Profile page

**Documentation:**
- `docs/planning/phases/other/PHASE13B_USER_PROFILE_SYSTEM.md` (full spec)
- User guide: "Understanding Your Profile"
- API documentation

**Marketing Alignment:**
- "AI that knows you" - Deep personalization
- "Your data, your control" - Markdown files you can edit
- "Practice augmentation" - Not identity replication

**Related Features:**
- Feature #29: Pattern Learning Transparency (profiles show learned patterns)
- Feature #8: Profile-aware task management
- Domain Configuration (Phase 1.5) - One-to-one domain mapping

---

### 3. User-Defined Knowledge Base Directory
**Status:** 🔵 Planned  
**Priority:** High (Critical for Data Autonomy)  
**Estimated Effort:** Medium (3-5 days)  
**Target Phase:** Phase 19 (Data Autonomy) or earlier

**Feature Description:**
Knowledge base must live in user-defined directory with full compatibility for cloud sync services.

**Requirements:**
- User selects directory location during setup (first-run wizard)
- Support for cloud sync services:
  - Dropbox
  - iCloud Drive
  - Google Drive
  - OneDrive
  - WebDAV (self-hosted servers)
- Knowledge base stored outside app package (survives app updates)
- Configurable in Settings after initial setup

**Storage Structure:**
```
~/Dropbox/Polly/                    # User-chosen location
├── domains.json                    # Domain configuration
├── patterns.json                   # Learned patterns
├── mental_models.yaml              # Personal frameworks
├── notes/                          # Native notes
│   ├── 01-Concepts/
│   ├── 02-Patterns/
│   ├── _Drafts/
│   └── _Templates/
├── conversations/                  # Conversation history
└── attachments/                    # Media files
```

**User Benefits:**
- Full control over data location
- Automatic cloud backup via sync service
- Easy migration between machines
- Survives app reinstallation
- Compatible with existing backup workflows

**Technical Implementation:**
1. Add directory picker to first-run wizard (Phase 18 integration)
2. Store base path in `~/.polly/config.yaml` (outside user directory)
3. Update all file operations to use configured base path
4. Migration tool for moving existing data
5. Validate directory permissions on startup

**Files to Modify:**
- `core/config.py` - Add `knowledge_base_path` configuration
- `setup_wizard.py` - Add directory selection step
- All file operations that reference `~/.polly/notes/` or similar

**Migration Strategy:**
- Detect existing `~/.polly/` installation
- Prompt user to migrate to custom location
- Copy all data to new location
- Validate integrity
- Update config to point to new location

**Related Phases:**
- Phase 18: Onboarding (first-run wizard integration)
- Phase 19: Data Autonomy (export/backup features)

---

### 4. Wiki-Link Note Creation  
**Estimated Effort:** Small (1-2 days)  
**Target Phase:** Phase 16 enhancement

**Feature Description:**
Clicking a `[[link]]` to a non-existent note should create that note with folder selection.

**Current Behavior:**
- Clicking broken wiki-link does nothing or shows error

**Desired Behavior:**
- Click broken wiki-link `[[New Note]]`
- Modal appears:
  - Pre-filled name: "New Note"
  - Folder selection dropdown (domain folders)
  - Optional: Template selection
  - Optional: Initial content textarea
- User confirms → note created and opened

**User Benefits:**
- Seamless note creation workflow (Obsidian-style)
- Natural knowledge graph building
- Reduces friction in thought capture
- Maintains flow state while writing

**Technical Implementation:**
```javascript
// In notes-manager.js wiki-link click handler
if (!noteExists(noteName)) {
  showCreateNoteModal({
    name: noteName,
    preselectedFolder: currentNoteDomain(),
    source: 'wiki-link'
  });
}
```

**UI Mock:**
```
┌─────────────────────────────────────┐
│ Create Note: "New Note"             │
├─────────────────────────────────────┤
│ Name: [New Note               ]     │
│                                     │
│ Folder: [▼ 01-Concepts        ]     │
│         [  02-Patterns        ]     │
│         [  03-Projects        ]     │
│                                     │
│ Template (optional):                │
│         [▼ None               ]     │
│                                     │
│ Initial Content (optional):         │
│ [                             ]     │
│ [                             ]     │
│                                     │
│          [Cancel]  [Create & Open]  │
└─────────────────────────────────────┘
```

**Related Files:**
- `electron-app/src/renderer/notes-manager.js` (line ~600, wiki-link handler)
- `core/backlinks.py` (broken link detection)

**Marketing Alignment:**
- "Stop organizing. Start working." - Seamless note creation

---

### 5. Notes Templating System
**Status:** 🔵 Planned  
**Priority:** Medium (Power User Feature)  
**Estimated Effort:** Medium (2-3 days)  
**Target Phase:** Phase 16 enhancement

**Feature Description:**
Obsidian-style note templates with variable substitution.

**Template Features:**
- Templates stored in `_Templates/` folder
- Variable substitution: `{{date}}`, `{{title}}`, `{{domain}}`
- Frontmatter templates
- User-defined variables

**Example Template:**
```markdown
---
title: {{title}}
created: {{date}}
domain: {{domain}}
tags: [{{tag1}}, {{tag2}}]
---

# {{title}}

## Context

## Key Points

## Related Notes
- 

## References
```

**Variable System:**
- Built-in variables: `{{date}}`, `{{time}}`, `{{title}}`, `{{domain}}`
- Custom variables: Prompt user during creation
- Smart defaults: Date formats, domain from folder

**User Workflow:**
1. Create note → Select template
2. Template variables filled automatically
3. Prompt for custom variables if needed
4. Note created with template applied

**Technical Implementation:**
1. Template parser: Regex to find `{{variable}}` placeholders
2. Variable resolver: Built-in variables + user prompts
3. Template browser UI (modal with preview)
4. Integration with note creation modal

**Related Files:**
- `core/templates.py` (new file for template engine)
- `electron-app/src/renderer/notes-manager.js` (template selection UI)

---

### 6. Table of Contents View for Large Notes
**Status:** 🔵 Planned  
**Priority:** Medium (Navigation Feature)  
**Estimated Effort:** Small (1-2 days)  
**Target Phase:** Phase 16 enhancement

**Feature Description:**
Sidebar panel showing table of contents for current note, clickable headings for navigation.

**Features:**
- Auto-generated from markdown headings (`#`, `##`, `###`)
- Nested structure following heading hierarchy
- Click to scroll to section
- Highlight current section while scrolling
- Collapsible sections

**UI Location:**
- Right sidebar (below backlinks/tags panel)
- Toggleable via button: "Show TOC"
- Keyboard shortcut: `Cmd+Shift+O`

**UI Mock:**
```
┌─────────────────────────┐
│ Table of Contents       │
├─────────────────────────┤
│ ► Introduction          │
│ ▼ Main Concepts         │
│   ├─ Concept 1          │
│   ├─ Concept 2          │
│   └─ Concept 3          │
│ ► Implementation        │
│   ├─ Step 1             │
│   └─ Step 2             │
│ ► Conclusion            │
└─────────────────────────┘
```

**Technical Implementation:**
```javascript
// Parse markdown to extract headings
function generateTOC(markdown) {
  const headings = [];
  const lines = markdown.split('\n');
  
  lines.forEach((line, index) => {
    const match = line.match(/^(#{1,6})\s+(.+)$/);
    if (match) {
      headings.push({
        level: match[1].length,
        text: match[2],
        line: index
      });
    }
  });
  
  return buildTOCTree(headings);
}

// Scroll to heading on click
function scrollToHeading(lineNumber) {
  // Implementation depends on editor type
}
```

**User Benefits:**
- Navigate long documents easily
- See document structure at a glance
- Jump to sections without scrolling
- Better orientation in large notes

**Related Files:**
- `electron-app/src/renderer/notes-manager.js` (TOC generation and UI)
- `electron-app/src/renderer/styles/notes.css` (TOC styling)

---

### 7. Document-Specific Context in Chat
**Status:** 🔵 Planned  
**Priority:** High (Context Management)  
**Estimated Effort:** Medium (3-4 days)  
**Target Phase:** Phase 17 (Code Workspace) or Phase 11 enhancement

**Feature Description:**
Way to address specific documents by typing `/` in chat, bringing up knowledge base folder structure with clickable path interface.

**User Workflow:**
1. User typing in chat
2. Types `/` → Knowledge base browser opens
3. Navigate folder tree or search
4. Click document → Document added to context
5. Visual indicator in chat: `📄 Document: "Project Plan.md"`
6. LLM receives document content in context

**UI Mock:**
```
Chat Input:
┌────────────────────────────────────────────┐
│ How do I implement [/                      │ ← User types /
└────────────────────────────────────────────┘
        ↓
┌────────────────────────────────────────────┐
│ 📂 Select Document                     [×] │
├────────────────────────────────────────────┤
│ Search: [___________________] 🔍           │
├────────────────────────────────────────────┤
│ 📁 01-Concepts/                            │
│   📄 Domain Modeling.md                    │
│   📄 System Architecture.md                │
│ 📁 02-Patterns/                            │
│   📄 RAG Patterns.md                       │
│ 📁 03-Projects/                            │
│   📁 Aleph/                                │
│     📄 Aleph Architecture.md          ← Click
│     📄 Build Instructions.md               │
└────────────────────────────────────────────┘
        ↓
Chat Input:
┌────────────────────────────────────────────┐
│ 📄 Aleph Architecture.md                [×]│ ← Document chip
│ How do I implement the audio engine?      │
└────────────────────────────────────────────┘
```

**Features:**
- Fuzzy search within document browser
- Multi-select: Add multiple documents to context
- Recent documents quick access
- Remove document from context (click X)
- Token count indicator for context size

**Technical Implementation:**
1. Detect `/` keystroke in chat input
2. Show modal with file tree (reuse notes file tree component)
3. On document selection:
   - Read document content
   - Add to conversation context
   - Show visual chip in chat UI
   - Include in next LLM request
4. Context management: Track added documents, allow removal

**Token Management:**
- Show token count: "Context: 2,450 / 8,000 tokens"
- Warn when approaching limit
- Suggest removing documents if over limit

**Related Files:**
- `electron-app/src/renderer/app.js` (chat input handler)
- `electron-app/src/renderer/notes-manager.js` (file tree component)
- `core/polly.py` (context assembly)

**Marketing Alignment:**
- "Full context always available"
- "Your knowledge, always at hand"

---

### 8. Chat Note Creation with Confirmation
**Status:** 🔵 Planned  
**Priority:** Medium (UX Improvement)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 16c enhancement

**Feature Description:**
Note writing from chat should not use persistent button. Instead, confirmation dialogue within chat window itself.

**Current Issue:**
- Persistent "Save to Notes" button always visible (cluttered UI)

**Desired Behavior:**
- User: "Can you make a detailed organized summary of this conversation?"
- Polly: "Would you like me to create a note for this summary?"
  - [Yes, create note]
  - [No, just show summary]
- User clicks "Yes, create note" → Note creation flow begins

**Alternative Flow:**
- Polly generates summary
- At end of message: 
  ```
  📝 Save this as a note?
  [Save to Notes] [Dismiss]
  ```

**User Benefits:**
- Cleaner chat interface
- Contextual actions (only when relevant)
- User confirms intent before creating note
- More natural conversation flow

**Technical Implementation:**
1. Remove persistent "Save to Notes" button
2. Add intent detection for note creation requests
3. Show inline action buttons in assistant messages
4. Action buttons trigger note creation modal

**Related Files:**
- `electron-app/src/renderer/index.html` (remove persistent button)
- `electron-app/src/renderer/app.js` (inline action buttons)
- `PHASE16C_AI_NOTE_CREATION.md` (intent detection system)

---

### 9. OmniFocus-Style Todo List with Chat Integration
**Status:** 🔵 Planned  
**Priority:** Medium (Productivity Feature)  
**Estimated Effort:** Large (1-2 weeks)  
**Target Phase:** Phase 23 (Project Management) or separate phase

**Feature Description:**
Built-in task management system with OmniFocus-style features and chat assistant integration.

**Features:**
- Projects and contexts (GTD methodology)
- Defer dates and due dates
- Review cycles
- Perspectives (custom views)
- Quick capture from anywhere
- **Chat integration:** Extract action items from conversations

**Chat Integration:**
```
User: "I need to refactor the RAG system and update the docs by Friday"
Polly: "I found 2 action items:"
  ☐ Refactor RAG system
  ☐ Update documentation (due: Friday)
  [Add to Tasks] [Dismiss]
```

**UI Location:**
- New page: "Tasks" in navigation ribbon
- Quick add: Cmd+T from anywhere
- Sidebar widget: Today's tasks

**Core Features:**
1. **Inbox:** Quick capture, process later
2. **Projects:** Multi-step initiatives
3. **Contexts:** @home, @computer, @errands
4. **Review:** Weekly/monthly review cycles
5. **Perspectives:** Custom filtered views

**Technical Implementation:**
- SQLite storage: `tasks` table
- Relationships: projects, contexts, tags
- Recurrence engine for repeating tasks
- Natural language parsing for quick add
- Integration with Phase 20 (Calendar) for time-blocking

**Related Phases:**
- Phase 23: Project Management (comprehensive project features)
- Phase 20b: Calendar & Action Items (meeting action extraction)

**Marketing Alignment:**
- "Stop organizing. Start working." - Intelligent task capture
- Polly extracts tasks so you don't have to

---

## Low Priority Features

### 10. Auto-Complete for Wiki-Links and Embeds
**Status:** 🔵 Planned  
**Priority:** Low (Quality of Life)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 16 enhancement

**Feature Description:**
Typing `[[` should automatically complete to `[[]]` with cursor positioned in the middle. Same for `![[`.

**Current Behavior:**
- User types `[[` → nothing happens
- User types `]]` manually
- User moves cursor back to middle

**Desired Behavior:**
- User types `[[` → Auto-completes to `[[]]`, cursor between brackets
- User types `![[` → Auto-completes to `![[]]`, cursor between brackets
- Optionally: Show note suggestions dropdown

**Implementation:**
```javascript
// In markdown editor
editor.addEventListener('keypress', (e) => {
  const text = editor.value;
  const cursorPos = editor.selectionStart;
  
  // Detect [[ pattern
  if (e.key === '[' && text[cursorPos - 1] === '[') {
    e.preventDefault();
    insertText(editor, ']]', cursorPos);
    editor.selectionStart = cursorPos;
    editor.selectionEnd = cursorPos;
    
    // Optionally show autocomplete dropdown
    showNoteAutocomplete(cursorPos);
  }
});
```

**Related Files:**
- `electron-app/src/renderer/notes-manager.js` (editor event handlers)

---

### 11. Click-to-Position Cursor in Edit Mode
**Status:** 🔵 Planned  
**Priority:** Low (Quality of Life)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 16 enhancement

**Feature Description:**
When hovering over text and clicking to enter edit mode, cursor should drop exactly where clicked, not at bottom of note.

**Current Issue:**
- User hovers over paragraph 3
- Clicks to edit
- Edit mode activates
- Cursor jumps to end of document (not where clicked)

**Desired Behavior:**
- User clicks on paragraph 3
- Edit mode activates
- Cursor positioned at click location in paragraph 3

**Technical Challenge:**
- Click event triggers on rendered markdown
- Need to map click position to markdown source position
- Different coordinate systems (rendered vs. raw)

**Proposed Solution:**
```javascript
// Store click position before switching to edit mode
function handleViewModeClick(event) {
  const clickedElement = event.target;
  const clickedText = clickedElement.textContent;
  
  // Find corresponding position in markdown source
  const markdownPosition = findMarkdownPosition(clickedText);
  
  // Switch to edit mode
  switchToEditMode();
  
  // Set cursor to calculated position
  editor.selectionStart = markdownPosition;
  editor.selectionEnd = markdownPosition;
  editor.focus();
}
```

**Related Files:**
- `electron-app/src/renderer/notes-manager.js` (view/edit mode switching)

---

### 12. Generate Note Templates from Existing Notes
**Status:** 🔵 Planned  
**Priority:** Low (Advanced Feature)  
**Estimated Effort:** Medium (2-3 days)  
**Target Phase:** Phase 16c enhancement

**Feature Description:**
AI-powered template generation: Strip specifics from existing note, extract general pattern, save as template.

**Example:**
**Input Note:** "Phemto Sound Design Guide.md"
```markdown
# Phemto Sound Design Techniques

## Oscillator Configuration
- Use 3 oscillators: saw, square, sine
- Detune by 7 cents for width

## Filter Settings
- Low-pass at 800Hz
- Resonance: 0.3
```

**Generated Template:** "Sound Design Guide Template.md"
```markdown
# {{artist_name}} Sound Design Techniques

## Oscillator Configuration
- Use {{osc_count}} oscillators: {{osc_types}}
- Detune by {{detune_amount}} cents for width

## Filter Settings
- {{filter_type}} at {{cutoff_freq}}
- Resonance: {{resonance}}
```

**User Workflow:**
1. Right-click note in file tree
2. Select "Generate Template from Note"
3. Polly analyzes structure and content
4. Shows template preview with variables
5. User edits variable names if needed
6. Save to `_Templates/` folder

**Technical Implementation:**
- Use LLM (Claude/GPT) to analyze note structure
- Identify specific values vs. general patterns
- Replace specifics with `{{variable}}` placeholders
- Preserve markdown structure

**Use Cases:**
- Meeting notes template from past meeting
- Project documentation template
- Research paper template
- Recipe template

**Related Phases:**
- Phase 16c: AI Note Creation (uses same template system)
- Phase 11: Multi-Model Routing (LLM for analysis)

---

### 13. One-Time Purchase Feature Expansions
**Status:** 🔵 Planned  
**Priority:** Low (Monetization Strategy)  
**Estimated Effort:** Large (weeks, includes payment system)  
**Target Phase:** Post-1.0 (Monetization)

**Feature Description:**
Polly offers one-time purchase expansions to unlock features, mental models, or specialized content packs.

**Expansion Ideas:**

**1. Domain Template Packs:**
- Academic Research Pack (5 domains + templates)
- Creative Professional Pack (design, writing, music)
- Developer Pack (multiple programming domains)
- $9.99 each

**2. Mental Model Collections:**
- Philosophy Pack (Stoicism, Pragmatism, etc.)
- Business Strategy Pack (Blue Ocean, Jobs to Be Done)
- Systems Thinking Pack (Complexity, Network Effects)
- $14.99 each

**3. Advanced Features:**
- Advanced Email Intelligence (Phase 20 features)
- Code Workspace Pro (additional languages, debugging)
- Knowledge Graph Pro (advanced visualizations)
- $29.99 each

**4. Knowledge Content Packs:**
- Context7 library bundles (React, Vue, Svelte)
- Technical documentation collections
- Academic paper databases
- $19.99 each

**Implementation Requirements:**
- Licensing system
- Purchase verification (offline-friendly)
- License transfer between machines
- Family sharing option

**Monetization Strategy:**
- Core Polly: Free or low one-time price
- Expansions: Optional purchases for power users
- No subscriptions, no recurring revenue
- Philosophy: "Own your tools, own your data"

**Marketing Alignment:**
- "Build capability, don't rent it" - One-time purchases align with ownership philosophy

---

### 14. Floating Chat Input Bar (Global)
**Status:** 🔵 Planned  
**Priority:** High (Major UX Redesign)  
**Estimated Effort:** Large (1-2 weeks)  
**Target Phase:** Phase 0.7 (UI Evolution) or Phase 11 enhancement

**Feature Description:**
Persistent chat input bar at bottom of screen (all pages) with persona/model/orchestrate controls. Modeled after OpenCode's chat interface.

**User Benefits:**
- Chat available on every page without switching views
- Right sidebar freed for conversation management
- Feels like persistent AI assistant, not just another page
- Context-aware: Polly knows which page you're on

**Technical Implementation Plan:**
See BRAIN_DUMP_2026-01-31.md "Issue 2: Chat Input Position" for full design.

**UI Concept:**
- Floating bar at bottom (collapsible with Cmd+\)
- Expands upward to show conversation history
- Persona dropdown, model selector, orchestrate toggle included
- Context injection based on active page

---

### 15. Brain Dump Feature
**Status:** 🔵 Planned  
**Priority:** Low (Quality of Life)  
**Estimated Effort:** Medium (2-3 days)  
**Target Phase:** Phase 22 (Teaching Mode)

**Feature Description:**
Free-form thinking space where Polly identifies themes and suggests related notes from knowledge base.

**User Benefits:**
- Think out loud without pressure to organize
- Discover connections across existing notes
- Extract concepts and themes automatically
- Option to save as organized note at end

**Example Workflow:**
```
User: [streams thoughts about email patterns and automation]
Polly: "🧠 Related concepts in your knowledge base:
- Pattern Learning (Notes/02-Patterns/)
- Email Intelligence (Notes/Ideas/)
Themes: automation, learning from behavior
Create note from this?"
```

---

### 16. Deduplication Drag-Drop Editor
**Status:** 🔵 Planned  
**Priority:** Medium (UX Enhancement)  
**Estimated Effort:** Medium (2-3 days)  
**Target Phase:** Phase 21 enhancement

**Feature Description:**
Specialized markdown editor for merging new content into existing notes with visual drag-and-drop interface.

**UI Features:**
- Existing content shown in light gray (context)
- New content in draggable blocks
- Drag blocks to position in document
- Preview merged result
- Three actions: Merge, Create Separate, Cancel

**User Benefits:**
- Intuitive way to consolidate knowledge
- Visual feedback during merge
- Prevents accidental overwrites
- Maintains note organization

**Technical Implementation:**
- Parse new content into semantic blocks
- HTML5 drag-and-drop interface
- Real-time preview of merged result
- Undo/redo support

See BRAIN_DUMP_2026-01-31.md for full UI mockup.

---

### 17. Library Mode (E-Reader Integration)
**Status:** 🔵 Planned  
**Priority:** Medium (Unique Differentiator)  
**Estimated Effort:** Very Large (3-4 weeks)  
**Target Phase:** Phase 25

**Feature Description:**
Calibre-style e-book management with e-reader sync (Supernote, Remarkable) and RAG integration.

**Features:**
- Import e-books (EPUB, PDF, MOBI)
- Sync to e-reader devices
- Index books into separate RAG collection
- Query your library: "What did Deleuze say about desire?"
- Export highlights/annotations to notes

**User Benefits:**
- Manage personal library in Polly
- Reference books in AI conversations
- Sync highlights to knowledge base
- All-in-one reading + note-taking

**RAG Strategy:**
- Separate `library` collection (not mixed with notes)
- Explicit library search (user-controlled)
- Optional auto-enrichment for philosophical queries

**Technical Challenges:**
- Knowledge base scale (100 books = 10M tokens)
- RAG performance impact
- When to search library vs. notes?

**Target Users:**
- Academics and researchers
- Avid readers who take notes
- Writers who reference books

See BRAIN_DUMP_2026-01-31.md "Feature 1: Library Mode" for full architecture.

---

### 18. Designer Persona + UI Builder
**Status:** 🔵 Planned  
**Priority:** High (Major Differentiator)  
**Estimated Effort:** Very Large (8-12 weeks)  
**Target Phase:** Phase 26

**Feature Description:**
Figma-like UI design tool with Tailwind CSS integration, working in concert with Programmer persona.

**Designer Persona Modes:**
- **Critic mode:** Evaluate designs for accessibility, contrast, UX
- **Artist mode:** Create visual assets (icons, illustrations)
- **Vision mode:** UX architecture and user flows

**Features (Phased Approach):**

**Phase 26a: Figma Integration (2-3 weeks)**
- Figma API integration
- Link designs to projects
- Designer persona reviews designs
- Generate component stubs

**Phase 26b: Tailwind Component Builder (8-12 weeks)**
- Visual component palette
- Tailwind class editor
- Responsive preview
- Export to React/Vue/HTML

**Value Proposition:**
Turns Polly into:
- Design tool (Figma)
- Code editor (VS Code)
- Knowledge manager (Obsidian)
- AI assistant (ChatGPT)
All in one, all connected.

**Competitors:**
- Figma (design only, cloud SaaS)
- v0 by Vercel (AI design-to-code, cloud)
- Builder.io (visual editor, SaaS)
- Polly: Local, integrated, AI-powered

See BRAIN_DUMP_2026-01-31.md "Feature 2: Designer Persona" for full vision.

---

### 19. Publisher Persona + POSE System
**Status:** 🔵 Planned  
**Priority:** Medium (Specific User Segment)  
**Estimated Effort:** Large (4-6 weeks)  
**Target Phase:** Phase 27

**Feature Description:**
Blog/newsletter publishing workflow with Ghost CMS integration and POSE framework.

**Publisher Persona Modes:**
- **Draft mode:** Idea generation, outlining, first draft
- **Edit mode:** Grammar, style, clarity, SEO
- **Publish mode:** Format for Ghost, meta descriptions, social snippets

**Features:**
- Markdown editor with publishing preview
- Ghost CMS integration (publish directly)
- SEO analyzer (keywords, meta, readability)
- Publishing checklist
- Analytics dashboard

**POSE System Integration:**
(Note: Needs definition of POSE framework)

**Target Users:**
- Bloggers and content creators
- Newsletter writers
- Technical writers

**Marketing:**
- "Write, polish, publish - all in one place"

See BRAIN_DUMP_2026-01-31.md "Feature 3: Publisher Persona" for full implementation plan.

---

---

## UI/UX Polish Features

### 20. Resizable Sidebars
**Status:** 🔵 Planned  
**Priority:** High (Usability)  
**Estimated Effort:** Small (1-2 days)  
**Target Phase:** Phase 0.7 (UI Evolution)

**Feature Description:**
Draggable resize handles for all sidebars (notes, chat, panel areas).

**User Benefits:**
- Customize layout to personal preference
- More space for reading/writing when needed
- Better multi-panel workflow

**Technical Implementation:**
- Add resize handles between panels
- Store width preferences in localStorage
- Min/max width constraints
- Smooth resize animation

**Related Files:**
- `/electron-app/src/renderer/styles/three-column.css`
- `/electron-app/src/renderer/app.js` (resize event handlers)

**Related Issues:**
- See KNOWN_ISSUES.md #1 (Critical: Resize handles not working)

---

### 21. Lucide Icons System-Wide
**Status:** 🟡 In Progress  
**Priority:** Medium (Visual Consistency)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 0.7 (UI Evolution)

**Feature Description:**
Replace all remaining generic icons with Lucide icons for visual consistency.

**Current State:**
- Some Lucide icons implemented
- Many generic/emoji icons still in use

**Target State:**
- 100% Lucide icons across UI
- Consistent icon sizing and styling
- Theme-aware icon colors

**Related Files:**
- All HTML/JS files with icon references

---

### 22. Loading Spinner Overhaul
**Status:** 🔵 Planned  
**Priority:** Low (Polish)  
**Estimated Effort:** Small (2-3 hours)  
**Target Phase:** Phase 0.7 (UI Evolution)

**Feature Description:**
Replace standard loading spinner with cute animated dots (Anthropic-style).

**UI Concept:**
```
Current: [⟳ Loading...]
New: [● ● ●] (with bouncing animation)
```

**User Benefits:**
- More polished, professional appearance
- Playful touch adds personality
- Reduced perceived wait time

**Technical Implementation:**
- CSS keyframe animations
- Replace all spinner instances
- Option for different animation styles

---

### 23. Scroll-to-Bottom Button
**Status:** 🔵 Planned  
**Priority:** Low (Quality of Life)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 0.7 (UI Evolution)

**Feature Description:**
Floating button appears when scrolled up in chat, clicking scrolls to latest message.

**Behavior:**
- Hidden when at bottom
- Appears when scrolled up >200px
- Smooth scroll to bottom on click
- Badge showing unread message count (optional)

**UI Position:**
- Bottom-right of chat area
- Semi-transparent background
- Icon: chevron-down (Lucide)

**Technical Implementation:**
```javascript
chatContainer.addEventListener('scroll', () => {
  const isAtBottom = chatContainer.scrollHeight - chatContainer.scrollTop === chatContainer.clientHeight;
  scrollButton.style.display = isAtBottom ? 'none' : 'block';
});
```

---

### 24. Mode Dropdown with Visual Indicator
**Status:** 🔵 Planned  
**Priority:** Medium (UX Enhancement)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 11c enhancement

**Feature Description:**
Colorful visual indicator showing current persona/mode in chat interface.

**UI Concept:**
```
┌────────────────────────────────┐
│ 🎨 Designer Mode         [▼]   │ ← Purple accent
│ 🏗️ Architect Mode        [▼]   │ ← Blue accent
│ 💻 Programmer Mode       [▼]   │ ← Green accent
│ 📚 Professor Mode        [▼]   │ ← Orange accent
└────────────────────────────────┘
```

**Features:**
- Color-coded by persona
- Icon for each mode
- Dropdown shows all available modes
- Visual feedback on mode switch

**Related Phases:**
- Phase 11c: Agent Personas ✅
- Phase 24: Orchestrator Mode (multi-persona indicator)

---

### 25. Excel-Style Note Action Chips
**Status:** 🔵 Planned  
**Priority:** Low (Polish)  
**Estimated Effort:** Small (1 day)  
**Target Phase:** Phase 16 enhancement

**Feature Description:**
Interactive chips for note actions (Open, Delete, Add to RAG, etc.) with Excel-style hover effects.

**UI Concept:**
```
Note: "Project Architecture.md"
[📂 Open] [🗑️ Delete] [🔍 Index] [🔗 Link] [⋯ More]
  ↑ Hover effect: slight lift, shadow, color change
```

**Features:**
- Smooth hover animations
- Color-coded by action type
- Consistent across all note list views
- Keyboard navigation support

**Technical Implementation:**
- CSS transitions
- Lucide icons
- Accessible (ARIA labels)

---

## Infrastructure Features

### 26. CodeMirror Chat Polish
**Status:** 🔵 Planned  
**Priority:** Medium (Developer Experience)  
**Estimated Effort:** Medium (2-3 days)  
**Target Phase:** Phase 17 (Code Workspace) or Phase 0.7

**Feature Description:**
Use CodeMirror for all code blocks in chat for better syntax highlighting and editing.

**Current Issue:**
- Static code blocks with basic syntax highlighting
- No line numbers
- No copy button
- Limited language support

**Desired Features:**
- Full syntax highlighting (CodeMirror)
- Line numbers
- Copy code button
- Language detection
- Optional inline editing
- Theme integration (follows Polly theme)

**Technical Implementation:**
- Integrate CodeMirror 6
- Custom theme matching Polly colors
- Render code blocks as CodeMirror instances
- Add toolbar with copy/edit actions

**Related Files:**
- `/electron-app/src/renderer/app.js` (message rendering)
- `/electron-app/src/renderer/styles/chat-sidebar.css`

**Research:**
- Evaluate CodeMirror 6 bundle size
- Performance with many code blocks in chat

---

### 27. Context Reload UX Improvement
**Status:** 🔵 Planned  
**Priority:** High (User Experience)  
**Estimated Effort:** Medium (4-6 hours)  
**Target Phase:** Phase 0.6 or 0.7

**Feature Description:**
Smooth context reload without jarring screen wipes, with progress indicator.

**Current Issue:**
- Context reload causes full screen clear
- Jarring white flash
- No progress feedback
- User loses orientation

**Desired Behavior:**
- Dim overlay with spinner
- "Reloading context... [████░░░░] 60%"
- Smooth fade-in after reload
- Preserve scroll position if possible

**Technical Implementation:**
```javascript
async function reloadContext() {
  showOverlay('Reloading context...');
  
  try {
    await loadContextSources();
    await rebuildRAGIndex();
    await refreshUI();
    
    hideOverlaySmooth();
  } catch (error) {
    showError('Context reload failed');
  }
}
```

**Related Issues:**
- See KNOWN_ISSUES.md #2 (High: Context reload jarring)

---

### 28. Deduplication System Overhaul
**Status:** 🔵 Planned  
**Priority:** High (Core Functionality)  
**Estimated Effort:** Large (1-2 weeks)  
**Target Phase:** Phase 21 enhancement

**Feature Description:**
Complete overhaul of deduplication system with clearer UX and better accuracy.

**Current Issues:**
- Unclear what "deduplicate" means
- False positives (notes aren't actually duplicates)
- No preview before merging
- Can't undo merge

**Proposed Solution:**
1. Rename to "Content Consolidation"
2. Show similarity score and preview
3. Three options: Merge, Link (don't merge), Ignore
4. Drag-drop editor for merge (see Feature #15)
5. Undo support (backup before merge)

**Related Features:**
- Feature #15: Deduplication Drag-Drop Editor

**Related Issues:**
- See KNOWN_ISSUES.md #3 (High: Deduplication overhaul needed)

---

### 29. Domain Tagging Improvements
**Status:** 🔵 Planned  
**Priority:** Medium (Accuracy)  
**Estimated Effort:** Medium (3-4 days)  
**Target Phase:** Phase 10 enhancement

**Feature Description:**
Improve domain classification accuracy and allow manual domain tagging.

**Current Issues:**
- Misclassifies topics (especially technical vs. philosophical)
- No manual override
- Domain boundaries unclear

**Proposed Features:**
- Manual domain tagging per conversation
- "This conversation is about: [Philosophy] [✓]"
- Train from corrections (learning system)
- Multi-domain tagging (conversation spans domains)
- Domain confidence scores

**Technical Implementation:**
- Add manual domain field to conversation metadata
- Preference: manual tag > AI classification
- Track corrections for model improvement
- Update Router v2 with correction data

**Related Issues:**
- See KNOWN_ISSUES.md #4 (Medium: Domain tagging misclassification)

---

### 30. Pattern Learning Transparency
**Status:** 🔵 Planned  
**Priority:** Medium (User Understanding)  
**Estimated Effort:** Small (1-2 days)  
**Target Phase:** Phase 13 enhancement

**Feature Description:**
Show users what patterns Polly has learned about their behavior and preferences.

**Current Issue:**
- Pattern learning happens invisibly
- Users don't know what Polly has learned
- No way to view or edit learned patterns

**Proposed UI:**
```
Settings → Learning Profile → Patterns

Communication Style:
- Prefers concise responses ⭐⭐⭐⭐⭐
- Likes code examples ⭐⭐⭐⭐☆
- Avoids verbose explanations ⭐⭐⭐⭐⭐

Work Patterns:
- Focused work: 9am-12pm, 2pm-5pm
- Break times: 12pm-2pm
- Prefers batched notifications

Technical Preferences:
- Python > JavaScript
- Functional programming style
- Verbose variable names
```

**Features:**
- View learned patterns
- Edit/correct patterns
- Delete individual patterns
- See confidence scores

**Related Issues:**
- See KNOWN_ISSUES.md #6 (Medium: Pattern learning clarity)

---

### 31. Compression System Transparency
**Status:** 🔵 Planned  
**Priority:** Medium (User Understanding)  
**Estimated Effort:** Small (1-2 days)  
**Target Phase:** Phase 7 enhancement

**Feature Description:**
Show users what information is being compressed and archived, with option to view compressed data.

**Current Issue:**
- Compression happens invisibly
- Users don't know what was compressed
- Fear of losing important context

**Proposed UI:**
```
Conversation → [⋯] → View Compression

Compressed Information:
📦 General chit-chat (45 messages)
   "Discussed weather, daily plans"
   [View Original] [Restore]

📦 Debugging session (12 messages)
   "Fixed TypeError in auth.py, solution: added null check"
   [View Original] [Restore]

Active Context:
✓ Current task (8 messages)
✓ Project context (3 notes)
```

**Features:**
- View compression history
- See compressed summaries
- Restore compressed messages
- Manual compression control

**Related Issues:**
- See KNOWN_ISSUES.md #7 (Medium: Compression clarity)

---

## Project Management Features

### 32. Dynamic Todo Lists in Chat (OpenCode-Style)
**Status:** 🔵 Planned  
**Priority:** High (Project Management)  
**Estimated Effort:** Medium (3-4 days)  
**Target Phase:** Phase 26 (Project Management)

**Feature Description:**
Persistent todo lists embedded in chat, updated dynamically as Polly completes tasks.

**User Benefits:**
- Visual progress tracking
- Transparent task management
- See what Polly is working on
- Inspired by OpenCode's todo system

**UI Concept:**
```
Polly: "I'll implement the authentication system. Here's my plan:"

┌─ Tasks ───────────────────────────┐
│ ✓ Create User model               │
│ ⟳ Implement JWT tokens            │
│ ☐ Add login endpoint              │
│ ☐ Add logout endpoint             │
│ ☐ Write tests                     │
└───────────────────────────────────┘

Polly: "Created User model in models/user.py. Now implementing JWT tokens..."

[Todo list updates in real-time]
```

**Technical Implementation:**
- Todo block type in chat messages
- Real-time updates via WebSocket
- Persistent across page refreshes
- Integration with Phase 24 (Orchestrator)

**Related Phases:**
- Phase 24: Orchestrator Mode (multi-task coordination)
- Phase 26: Project Management (comprehensive PM features)

**Reference:**
- See PHASE26_PROJECT_MANAGEMENT.md for full system

---

### 33. Visual Project Roadmaps
**Status:** 🔵 Planned  
**Priority:** Medium (Project Visualization)  
**Estimated Effort:** Large (1-2 weeks)  
**Target Phase:** Phase 26 (Project Management)

**Feature Description:**
Visual timeline and roadmap view generated from markdown project plans.

**Features:**
- Parse markdown project plans
- Generate Gantt-style timelines
- Dependency visualization
- Milestone tracking
- Export as image/PDF

**Example Input (Markdown):**
```markdown
# Project Alpha

## Phase 1: Foundation (2 weeks)
- [ ] Setup infrastructure
- [ ] Database design

## Phase 2: Core Features (4 weeks)
- [ ] User authentication
- [ ] Dashboard UI
```

**Generated Output:**
Visual timeline with phases, tasks, dependencies

**Related Phases:**
- Phase 26: Project Management
- Phase 24: Orchestrator Mode (tracks progress)

**Research:**
- HyperTask.ai integration (see RESEARCH_QUEUE.md)

**Reference:**
- See PHASE26_PROJECT_MANAGEMENT.md for full specification

---

## Persona Features

### 34. Orchestrator Mode
**Status:** 🔵 Planned  
**Priority:** HIGH (Foundation for power features)  
**Estimated Effort:** Large (2-3 weeks)  
**Target Phase:** Phase 24

**Feature Description:**
Multi-persona coordination system allowing complex, multi-step workflows in a single session.

**Key Capabilities:**
- Route tasks to appropriate personas automatically
- Coordinate outputs between personas
- Customizable workflows (Architect → Designer → Programmer)
- Progress tracking across personas

**Example:**
```
User: "Build a user dashboard with authentication, create docs, and teach me about OAuth"

Polly orchestrates:
1. Architect: Design system architecture
2. Designer: Create UI mockups
3. Programmer: Implement code
4. Scribe: Write documentation
5. Professor: Create OAuth learning path

All in one coordinated session.
```

**User Benefits:**
- No manual persona switching
- Complex projects in one session
- Intelligent task routing
- Coordinated progress tracking

**Reference:**
- See PHASE24_ORCHESTRATOR_MODE.md for complete specification

**Related Phases:**
- Phase 11c: Agent Personas ✅ (required)
- Phase 27: Designer Persona
- Phase 26: Project Management (visual progress)

---

### 35. Designer Persona
**Status:** 🔵 Planned  
**Priority:** High (Major Differentiator)  
**Estimated Effort:** Very Large (8-12 weeks)  
**Target Phase:** Phase 27

**Feature Description:**
UI/UX design persona with 4 modes: Vision, Mockup, Critic, System Design.

**Modes:**
1. **Vision:** UX architecture, user flows, information architecture
2. **Mockup:** ASCII/text-based UI mockups, layout design
3. **Critic:** Evaluate designs for accessibility, UX, visual hierarchy
4. **System:** Design system management, component libraries

**Workflow Integration:**
```
Architect → Designer → Programmer
    ↓           ↓          ↓
 System     UI/UX     Implementation
```

**Features:**
- ASCII mockup generation
- Design specifications
- Figma API integration (future)
- Tailwind CSS component builder (future)
- Theme management (color palettes, typography)

**User Benefits:**
- Design + code in one tool
- Consistent design-to-code workflow
- AI-powered design critique
- Design system documentation

**Reference:**
- See PHASE27_DESIGNER_PERSONA.md for complete specification

**Related Phases:**
- Phase 24: Orchestrator Mode (coordinates Designer with other personas)
- Phase 29: Built-in Browser (design preview)

---

### 36. Theme as Meta-Persona
**Status:** 🔵 Planned  
**Priority:** Low (Experimental)  
**Estimated Effort:** Medium (1-2 weeks)  
**Target Phase:** Phase 27 (Designer Persona)

**Feature Description:**
Theme as a system-wide meta-persona that influences all persona communication styles and aesthetics.

**Concept:**
- Theme = persistent personality layer
- Affects tone, formatting, visual style
- User-configurable or AI-suggested

**Example Themes:**
- **Monome:** Minimal, cryptic, grid-based interfaces
- **Brutalist:** Raw, functional, no polish
- **Warm Academic:** Friendly, verbose, teaching-oriented
- **Cyberpunk:** Technical jargon, hacker aesthetic

**Implementation:**
- System prompt injection for all personas
- Theme-specific UI styling
- Consistent aesthetic across all features

**Reference:**
- See PHASE27_DESIGNER_PERSONA.md (Theme as Meta-Persona section)

---

## Plugin & Extension Features

### 37. Open Polly Tools (Plugin Ecosystem)
**Status:** 🔵 Planned  
**Priority:** HIGH (Community & Extensibility)  
**Estimated Effort:** Very Large (4-6 weeks)  
**Target Phase:** Phase 28

**Feature Description:**
Community-driven tool/plugin ecosystem with GitHub-based distribution and Monome-style documentation.

**Architecture:**
- Core Polly: Closed source
- Tools API: Open and documented
- Tool marketplace: GitHub-based
- Sandboxed execution

**Tool Types:**
1. **Utilities:** File converters, formatters, calculators
2. **Integrations:** External API connectors (Notion, Figma, GitHub)
3. **Workflows:** Custom persona routings
4. **Themes:** UI customization
5. **Context Sources:** Custom RAG integrations

**Distribution:**
- GitHub repos with `polly-tool.yaml` manifest
- Curated official tools (10 core tools)
- Community tools (searchable registry)
- One-click install from GitHub URL

**Tool Development:**
- Monome-style documentation (minimal, example-driven)
- Starter templates
- Testing framework
- Publishing guidelines

**User Benefits:**
- Extend Polly without forking
- Community-driven ecosystem
- Curated quality tools
- Easy sharing and discovery

**Reference:**
- See PHASE28_OPEN_POLLY_TOOLS.md for complete specification

**Related Phases:**
- Phase 11c: Agent Personas ✅ (tools can create personas)
- Phase 24: Orchestrator Mode (tools can define workflows)

---

## Advanced Features

### 38. Code Architecture Visualization System
**Status:** 🔵 Planned  
**Priority:** High (Developer Tool)  
**Estimated Effort:** Large (3-4 weeks)  
**Target Phase:** Phase 25

**Feature Description:**
Visual dependency tree and architecture diagram generation for codebases with impact analysis.

**Features:**
- Parse codebase to generate dependency graphs
- Visual tree view (D3.js or similar)
- Impact analysis: "What breaks if I change this?"
- Architecture documentation auto-generation
- Integration with Code Workspace

**Use Cases:**
- Onboarding to new codebases
- Refactoring planning
- Technical documentation
- Identifying circular dependencies
- Understanding module relationships

**UI Concept:**
```
┌─ Dependencies: auth.py ────────────┐
│                                    │
│     ┌─ models/user.py              │
│     │                              │
│  auth.py ─┬─ utils/crypto.py       │
│           │                        │
│           └─ db/session.py         │
│                                    │
│  Impact: 12 files depend on this   │
│  [Show Impact Tree]                │
└────────────────────────────────────┘
```

**Technical Implementation:**
- Static analysis (AST parsing)
- Dependency resolution
- Graph visualization
- Integration with SummonAI Kit (research)

**Reference:**
- See PHASE25_CODE_ARCHITECTURE_SYSTEM.md for complete specification

**Research:**
- SummonAI Kit evaluation (see RESEARCH_QUEUE.md)

---

### 39. Built-in Browser with DevTools
**Status:** 🔵 Planned  
**Priority:** Medium (Nice-to-Have)  
**Estimated Effort:** Large (2-3 weeks)  
**Target Phase:** Phase 29

**Feature Description:**
Embedded Chromium browser with DevTools for analyzing websites and previewing Polly-generated code.

**Features:**
- Embedded browser panel
- Full Chrome DevTools
- Analyze website code and UI
- Live preview of generated code
- Responsive testing (viewport sizes)
- Network inspection
- Performance profiling

**Use Cases:**
- Web development: Preview changes live
- Design analysis: Inspect competitor sites
- Learning: "How did they build this?"
- Debugging: See actual rendering

**UI Layout:**
```
┌─────────────────────────────────────┐
│  [← → ⟳] localhost:3000        [⋯] │
├─────────────────────────────────────┤
│                                     │
│        Website Preview              │
│                                     │
├─────────────────────────────────────┤
│  Elements  Console  Network         │
│  <div class="container">            │
│    <h1>Hello World</h1>             │
└─────────────────────────────────────┘
```

**Technical Implementation:**
- Electron webview or BrowserView
- Chrome DevTools Protocol
- Sandboxed execution
- Resource monitoring

**Reference:**
- See PHASE29_BUILT_IN_BROWSER.md for complete specification

**Related Phases:**
- Phase 17: Code Workspace (code generation)
- Phase 27: Designer Persona (design preview)

---

---

## Feature Template

When adding new features to this document, use this template:

```markdown
### [Feature Number]. [Feature Name]
**Status:** 🔵 Planned / 🟡 In Progress / 🟢 Completed  
**Priority:** High / Medium / Low  
**Estimated Effort:** Small (hours) / Medium (days) / Large (weeks)  
**Target Phase:** [Phase number]

**Feature Description:**
[What the feature does, user-facing description]

**User Benefits:**
- [Benefit 1]
- [Benefit 2]

#### Technical Implementation Plan
[Detailed implementation steps]

#### Technical Challenges & Solutions
[Known challenges and how to address them]

#### Files Reference
[Files to create/modify]

#### Testing Checklist
[What to test when implementing]
```

---

## Notes

- Features in this document are **planned but not yet implemented**
- Each feature should have enough detail that you (or another developer) can pick it up months later
- Update status as features move from planned → in progress → completed
- Completed features can be moved to a "Completed Features" section or removed
- Keep this document synchronized with actual development priorities

---

**Document Created:** January 26, 2026  
**Last Updated:** February 3, 2026 (Added features #19-38: UI/UX polish, infrastructure, project management, personas, plugins, and advanced features from brain dump)  
**Status:** Living Document - Update as features are planned/implemented

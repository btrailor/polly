# Phase 1.5 - First-Run Wizard Specification

## Overview

The First-Run Wizard provides users with an easy onboarding experience for setting up their domain configuration. It appears when no `~/.polly/domains.json` file exists and guides users through either a quick start or custom setup.

## Detection Logic

```python
# In interfaces/server.py startup or Electron app initialization
config_path = Path.home() / ".polly" / "domains.json"
if not config_path.exists():
    show_first_run_wizard = True
else:
    show_first_run_wizard = False
```

## Wizard Flow

### Screen 1: Welcome & Choice

```
┌─────────────────────────────────────────────────┐
│  Welcome to Polly!                              │
│                                                 │
│  Polly organizes your knowledge into domains.  │
│  Let's set up your first domains.              │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ 🚀 Quick Start (Recommended)            │   │
│  │ Get started in 10 seconds with 3        │   │
│  │ general-purpose domains                 │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ ⚙️  Custom Setup                         │   │
│  │ Choose from templates or create your    │   │
│  │ own domains                             │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [Skip - I'll set up later]                    │
└─────────────────────────────────────────────────┘
```

### Option A: Quick Start

Instantly creates 3 default domains:

1. **Work** 📊
   - Color: `#61afef` (blue)
   - Keywords: `project`, `task`, `meeting`, `deadline`, `client`, `work`, `job`, `career`
   - RAG Weight: 33%
   - Folder: `01-Work`

2. **Personal** 🏠
   - Color: `#98c379` (green)
   - Keywords: `personal`, `life`, `family`, `health`, `finance`, `hobby`, `todo`, `home`
   - RAG Weight: 33%
   - Folder: `02-Personal`

3. **Learning** 🎓
   - Color: `#e5c07b` (yellow)
   - Keywords: `learn`, `study`, `course`, `tutorial`, `book`, `research`, `knowledge`, `education`
   - RAG Weight: 34%
   - Folder: `03-Learning`

**Flow:**
1. Click "Quick Start"
2. Show progress: "Creating your domains..."
3. Success screen: "Ready to go! You can customize domains in Settings → Domains"
4. Close wizard, show dashboard

### Option B: Custom Setup

#### Screen 2: Choose Template

```
┌─────────────────────────────────────────────────┐
│  Choose a template (or create from scratch)    │
│                                                 │
│  ┌──────────────┐ ┌──────────────┐            │
│  │ 💻 Software  │ │ 🔬 Research  │            │
│  │ Development  │ │ Academic     │            │
│  │              │ │              │            │
│  │ • Code       │ │ • Research   │            │
│  │ • Projects   │ │ • Papers     │            │
│  │ • Learning   │ │ • Experiments│            │
│  └──────────────┘ └──────────────┘            │
│                                                 │
│  ┌──────────────┐ ┌──────────────┐            │
│  │ ✍️  Creative  │ │ 🏠 Personal  │            │
│  │ Writing      │ │ Life         │            │
│  │              │ │              │            │
│  │ • Ideas      │ │ • Personal   │            │
│  │ • Drafts     │ │ • Health     │            │
│  │ • Published  │ │ • Finance    │            │
│  └──────────────┘ └──────────────┘            │
│                                                 │
│  ┌──────────────┐ ┌──────────────┐            │
│  │ 🎓 Academic  │ │ 🎨 Polly     │            │
│  │ Student      │ │ Creator      │            │
│  │              │ │              │            │
│  │ • Courses    │ │ • Sigils     │            │
│  │ • Notes      │ │ • Signals    │            │
│  │ • Exams      │ │ • Scrolls... │            │
│  └──────────────┘ └──────────────┘            │
│                                                 │
│  [← Back]           [Create from scratch →]    │
└─────────────────────────────────────────────────┘
```

#### Screen 3: Review & Customize

Shows the selected template domains with ability to:
- Edit names, descriptions, keywords
- Add/remove domains
- Change colors and icons
- Adjust folder numbering

```
┌─────────────────────────────────────────────────┐
│  Review your domains                            │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ 💻 Code                                  │   │
│  │ Software projects and technical work    │   │
│  │ Keywords: python, javascript, git...    │   │
│  │ [Edit] [Remove]                         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ 🎓 Learning                              │   │
│  │ Tutorials, courses, and study notes     │   │
│  │ Keywords: learn, tutorial, course...    │   │
│  │ [Edit] [Remove]                         │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [+ Add Domain]                                │
│                                                 │
│  [← Back]                    [Create Domains →]│
└─────────────────────────────────────────────────┘
```

#### Screen 4 (Optional): Obsidian Analysis

```
┌─────────────────────────────────────────────────┐
│  Analyze your Obsidian vault?                   │
│                                                 │
│  Polly can scan your Obsidian vault to suggest │
│  domains based on your existing folder          │
│  structure and tags.                            │
│                                                 │
│  Vault path: /Users/you/Documents/Obsidian     │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ ✓ Analyze vault structure               │   │
│  │ ✓ Detect common tags                    │   │
│  │ ✓ Suggest domain keywords               │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [Skip this step]            [Analyze Vault →] │
└─────────────────────────────────────────────────┘
```

Analysis results:
```
Found 45 folders, 1,234 notes, 89 unique tags

Suggested domains based on your vault:
- Projects (23 notes) → Keywords: project, build, ...
- Research (18 notes) → Keywords: paper, study, ...
- Daily Notes (365 notes) → Keywords: daily, journal, ...
```

#### Screen 5: Success

```
┌─────────────────────────────────────────────────┐
│  ✓ Your domains are ready!                      │
│                                                 │
│  Created 4 domains:                             │
│  • 💻 Code                                      │
│  • 🎓 Learning                                  │
│  • 📊 Projects                                  │
│  • 💡 Ideas                                     │
│                                                 │
│  You can customize domains anytime in           │
│  Settings → Domains                             │
│                                                 │
│  [Start using Polly →]                          │
└─────────────────────────────────────────────────┘
```

## Templates

### 1. Software Development
- **Code** 💻: `python`, `javascript`, `typescript`, `rust`, `git`, `docker`, `api`, `database`
- **Projects** 📊: `project`, `build`, `deploy`, `feature`, `bug`, `task`, `sprint`
- **Learning** 🎓: `learn`, `tutorial`, `course`, `documentation`, `best-practice`

### 2. Research / Academic
- **Research** 🔬: `research`, `paper`, `study`, `experiment`, `data`, `analysis`, `hypothesis`
- **Papers** 📄: `paper`, `publication`, `journal`, `citation`, `reference`, `review`
- **Experiments** 🧪: `experiment`, `trial`, `result`, `observation`, `method`, `protocol`

### 3. Creative Writing
- **Ideas** 💡: `idea`, `concept`, `brainstorm`, `inspiration`, `sketch`, `draft`
- **Drafts** ✍️: `draft`, `writing`, `revision`, `edit`, `feedback`, `outline`
- **Published** 📚: `published`, `final`, `release`, `article`, `blog`, `story`

### 4. Personal Life
- **Personal** 🏠: `personal`, `life`, `family`, `home`, `todo`, `routine`
- **Health** 🏃: `health`, `fitness`, `exercise`, `nutrition`, `wellness`, `medical`
- **Finance** 💰: `finance`, `budget`, `investment`, `expense`, `income`, `savings`

### 5. Academic Student
- **Courses** 📚: `course`, `class`, `lecture`, `assignment`, `syllabus`, `semester`
- **Notes** 📝: `notes`, `study`, `exam`, `review`, `summary`, `textbook`
- **Exams** 🎯: `exam`, `test`, `quiz`, `midterm`, `final`, `prep`, `review`

### 6. Polly Creator (Default 5 Domains)
Uses the existing Sigils, Signals, Scrolls, Glyphs, Grids configuration from `domains.json`

## Implementation Details

### Backend Changes

**New endpoint: `POST /polly/domains/wizard/quick-start`**
```python
@app.post("/polly/domains/wizard/quick-start")
async def wizard_quick_start():
    """Create default 3-domain configuration."""
    # Create Work, Personal, Learning domains
    # Save to ~/.polly/domains.json
    # Return config
```

**New endpoint: `POST /polly/domains/wizard/from-template`**
```python
@app.post("/polly/domains/wizard/from-template")
async def wizard_from_template(request: Request):
    """Create domains from template."""
    body = await request.json()
    template_id = body.get("templateId")
    # Create domains based on template
    # Save to ~/.polly/domains.json
    # Return config
```

**New endpoint: `POST /polly/domains/wizard/analyze-vault`**
```python
@app.post("/polly/domains/wizard/analyze-vault")
async def wizard_analyze_vault(request: Request):
    """Analyze Obsidian vault for domain suggestions."""
    body = await request.json()
    vault_path = body.get("vaultPath")
    # Scan folder structure
    # Extract common tags
    # Suggest domains with keywords
    # Return suggestions
```

### Frontend Changes

**New modal: `first-run-wizard-modal`**
- Multi-screen wizard UI
- Template cards with previews
- Domain review/edit interface
- Progress indicators
- Success screen

**Logic:**
1. On app load, check if `~/.polly/domains.json` exists via API
2. If not, show wizard modal (cannot be dismissed)
3. Handle quick start vs. custom setup flows
4. Call appropriate API endpoints
5. On success, reload app with new config

### File Changes

**Backend:**
- `interfaces/server.py`: Add wizard endpoints (lines ~2200-2400)

**Frontend:**
- `electron-app/src/renderer/index.html`: Add wizard modal HTML (~lines 1200-1400)
- `electron-app/src/renderer/styles/main.css`: Add wizard styles (~lines 2900-3100)
- `electron-app/src/renderer/app.js`: Add wizard logic (~lines 4600-4900)

## User Experience

### Quick Start (10 seconds)
1. Launch Polly → See wizard
2. Click "Quick Start"
3. See "Creating domains..." for 2 seconds
4. See "Ready to go!" → dashboard loads

### Custom Setup (2-5 minutes)
1. Launch Polly → See wizard
2. Click "Custom Setup"
3. Browse 6 templates, select one
4. Review 3-5 suggested domains
5. Edit/add/remove domains as needed
6. Optionally analyze Obsidian vault
7. Click "Create Domains"
8. See success → dashboard loads

### Skip (0 seconds)
1. Click "Skip - I'll set up later"
2. Creates minimal 1-domain config: "General" 🗂️
3. User can configure properly in Settings later

## Testing

**Unit tests:**
- Test quick start endpoint creates 3 domains
- Test template endpoint creates correct domains per template
- Test vault analysis correctly parses folders/tags

**Integration tests:**
- Test full wizard flow in Electron app
- Test skip flow creates minimal config
- Test domains are usable after wizard completes

## Documentation

Update:
- `README.md`: Add first-run wizard section
- `PHASE1.5_DOMAIN_CONFIGURATION.md`: Add wizard documentation
- User guide: Add onboarding flow screenshots

## Estimated Time

- Backend endpoints: 2 hours
- Frontend wizard UI: 3 hours
- Vault analysis logic: 2 hours
- Testing & polish: 2 hours
- **Total: ~9 hours (1-2 days)**

## Success Criteria

- [x] Quick start creates 3 working domains in <10 seconds
- [ ] Custom setup provides 6 templates with appropriate domains
- [ ] Vault analysis suggests relevant domains based on folder structure
- [ ] Wizard only appears when no config exists
- [ ] All wizard flows result in working domain configuration
- [ ] User can skip wizard and configure manually later

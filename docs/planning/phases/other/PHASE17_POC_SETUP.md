# Phase 17 POC: VSCodium Fork Setup Guide

**Status:** 📋 Ready to Begin  
**Purpose:** Step-by-step guide for forking VSCodium and setting up Polly Code workspace POC

---

## Prerequisites

Before starting, ensure you have:

- **Node.js** 18.x or later
- **Git** installed
- **Python** 3.10+ (for VSCode build scripts)
- **Yarn** (VSCode uses Yarn, not npm)
- **Git LFS** (for large files)
- **C/C++ Build Tools** (for native modules)
  - macOS: Xcode Command Line Tools
  - Linux: build-essential
  - Windows: Visual Studio Build Tools

---

## Step 1: Fork VSCodium Repository

### 1.1 Clone VSCodium

```bash
# Create a directory for the fork (outside of Polly workspace)
cd ~/projects  # or wherever you keep projects
git clone https://github.com/VSCodium/vscodium.git polly-code
cd polly-code
```

### 1.2 Set Up Upstream Remote

```bash
# Add upstream remote for tracking updates
git remote add upstream https://github.com/VSCodium/vscodium.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/VSCodium/vscodium.git (fetch)
# origin    https://github.com/VSCodium/vscodium.git (push)
# upstream  https://github.com/VSCodium/vscodium.git (fetch)
# upstream  https://github.com/VSCodium/vscodium.git (push)
```

### 1.3 Create Polly Integration Branch

```bash
# Create branch for Polly-specific changes
git checkout -b polly-integration

# Document base state
echo "Base VSCode version: $(git describe --tags)" > POC_BASE_STATE.md
git log -1 --format="%H %s" >> POC_BASE_STATE.md
```

---

## Step 2: Build and Test Base VSCodium

### 2.1 Install Dependencies

```bash
# Install Node.js dependencies
yarn install

# This will take 10-20 minutes depending on your connection
# VSCode has many dependencies
```

### 2.2 Build VSCodium

```bash
# Compile TypeScript and build
yarn compile

# This will take 5-10 minutes
```

### 2.3 Run VSCodium

```bash
# Launch VSCodium in development mode
yarn watch  # In one terminal (watches for changes)
# In another terminal:
./scripts/code.sh  # macOS/Linux
# or
scripts\code.bat   # Windows
```

**Verify:**
- ✅ VSCodium launches
- ✅ Can open files
- ✅ Can edit and save
- ✅ Basic functionality works

### 2.4 Document Build Process

Create `BUILD.md`:

```markdown
# Polly Code Build Instructions

## Prerequisites
- Node.js 18.x+
- Yarn
- Python 3.10+
- Git LFS

## Build Steps
1. `yarn install`
2. `yarn compile`
3. `yarn watch` (in one terminal)
4. `./scripts/code.sh` (in another terminal)

## Build Time
- Initial install: ~15 minutes
- Compile: ~5-10 minutes
- Watch mode: Continuous
```

---

## Step 3: Study VSCode Architecture

Before making changes, understand the structure:

### 3.1 Key Directories

```
polly-code/
├── src/vs/
│   ├── workbench/          # Main UI shell
│   │   ├── browser/        # Browser-specific code
│   │   │   ├── parts/      # UI parts (activitybar, sidebar, etc.)
│   │   │   └── workbench.html  # Main HTML template
│   │   └── common/         # Shared workbench code
│   ├── editor/            # Monaco editor
│   ├── platform/          # Platform abstractions
│   └── base/              # Base utilities
├── extensions/            # Built-in extensions
└── scripts/              # Build scripts
```

### 3.2 Activity Bar Location

The activity bar is in:
- `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
- `src/vs/workbench/browser/workbench.html` (template)

### 3.3 Panel System

Panels are managed by:
- `src/vs/workbench/browser/parts/sidebar/`
- `src/vs/workbench/browser/parts/panel/`

---

## Step 4: Create Fork Structure

### 4.1 Create Polly Integration Directory

```bash
mkdir -p polly-integrations
mkdir -p polly-integrations/ribbon
mkdir -p polly-integrations/chat
mkdir -p polly-integrations/theme
```

### 4.2 Document All Modifications

Create `polly-integrations/MODIFICATIONS.md`:

```markdown
# Polly Code Modifications Log

## Core Modifications

### 1. Activity Bar → Ribbon
- **File:** `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
- **Change:** Replace activity bar with Polly ribbon
- **Reason:** Match Polly's navigation pattern
- **Date:** [Date]

### 2. Workbench Template
- **File:** `src/vs/workbench/browser/workbench.html`
- **Change:** Update HTML to include ribbon
- **Reason:** UI structure change
- **Date:** [Date]

## Extension-Based Features

### 1. Chat Panel
- **Extension:** `extensions/polly-chat/`
- **Type:** Extension (no core changes)
- **Date:** [Date]

### 2. Theme
- **Extension:** `extensions/polly-theme/`
- **Type:** Extension (no core changes)
- **Date:** [Date]
```

---

## Step 5: Initial Integration Test

### 5.1 Test Build After Setup

```bash
# Ensure everything still builds
yarn compile

# Test run
./scripts/code.sh
```

### 5.2 Create Test Checklist

```markdown
# POC Test Checklist

## Basic Functionality
- [ ] VSCodium launches
- [ ] Can open files
- [ ] Can edit files
- [ ] Can save files
- [ ] File explorer works
- [ ] Search works
- [ ] Git integration works
- [ ] Terminal works

## After Ribbon Integration
- [ ] Ribbon appears on left
- [ ] Can click ribbon items
- [ ] Views switch correctly
- [ ] Keyboard shortcuts work
- [ ] No console errors

## After Chat Integration
- [ ] Chat panel appears
- [ ] Can send messages
- [ ] Connects to Polly backend
- [ ] No console errors
```

---

## Step 6: Prepare for Merge Test

### 6.1 Document Current State

```bash
# Create snapshot of current state
git tag poc-before-merge
git log --oneline -10 > POC_CURRENT_STATE.txt
```

### 6.2 Set Up Merge Testing

Create `scripts/test-merge.sh`:

```bash
#!/bin/bash
# Test merge process

echo "=== Testing VSCode Merge Process ==="

# Fetch upstream
echo "Fetching upstream..."
git fetch upstream

# Check what's new
echo "Upstream changes:"
git log HEAD..upstream/main --oneline

# Create backup branch
echo "Creating backup..."
git branch poc-backup-$(date +%Y%m%d)

# Merge (dry run first)
echo "Testing merge..."
git merge --no-commit --no-ff upstream/main

# Check for conflicts
if [ $? -eq 0 ]; then
    echo "No conflicts! Merging..."
    git merge --abort  # Abort dry run
    # Actual merge would be: git merge upstream/main
else
    echo "Conflicts detected. Resolve manually."
fi
```

---

## Next Steps

Once setup is complete:

1. **Begin Ribbon Integration** (Day 3-4 of POC)
2. **Add Chat Panel** (Day 5 of POC)
3. **Test Merge Process** (Day 8-9 of POC)
4. **Evaluate Results** (Day 10 of POC)

---

## Troubleshooting

### Build Fails

```bash
# Clear cache and rebuild
rm -rf node_modules
rm -rf .yarn/cache
yarn install
yarn compile
```

### Native Module Issues

```bash
# Rebuild native modules
yarn rebuild
```

### Git LFS Issues

```bash
# Pull LFS files
git lfs pull
```

---

## Resources

- VSCodium GitHub: https://github.com/VSCodium/vscodium
- VSCode Source: https://github.com/microsoft/vscode
- VSCode Extension API: https://code.visualstudio.com/api
- VSCode Build Guide: https://github.com/microsoft/vscode/wiki/How-to-Contribute

---

**Status:** Ready for POC execution

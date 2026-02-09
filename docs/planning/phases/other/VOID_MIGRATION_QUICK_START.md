# Void Migration - Quick Start Guide

**Date:** February 5, 2025  
**Purpose:** Step-by-step commands to execute the Void migration

---

## Prerequisites

- GitHub account (to fork Void)
- Node.js and npm installed
- Git installed
- ~/projects directory (or your preferred location)

---

## Step 1: Fork Void (5 minutes)

### Via GitHub UI:
1. Go to https://github.com/voideditor/void
2. Click "Fork" button
3. Fork to your account

### Via Command Line:
```bash
# Navigate to projects
cd ~/projects

# Clone your fork (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/void.git polly-void
cd polly-void

# Set up remotes
git remote add upstream https://github.com/voideditor/void.git
git remote -v

# Create Polly branch
git checkout -b polly-integration
```

---

## Step 2: Archive Polly Code (15 minutes)

```bash
# Create archive directory in Polly workspace
cd ~/polly
mkdir -p void-migration/polly-code-archive
cd void-migration/polly-code-archive

# Create structure
mkdir -p polly-integrations/{core,api,backend,statusBar,views,components}
mkdir -p build-fixes/{css,native-modules,build-tasks}
mkdir -p documentation

# Copy Polly integration code
cp -r ~/projects/polly-code/src/polly-integrations/* polly-integrations/

# Copy build fixes documentation
# (We'll document these manually)
```

---

## Step 3: Clean Up VSCode Fork (10 minutes)

```bash
cd ~/projects/polly-code

# Create backup branch (safety)
git checkout -b archive-before-cleanup
git checkout polly-integration  # or your main branch

# Remove Polly code (after archiving)
rm -rf src/polly-integrations

# Remove debug files
rm -f .cursor/debug.log
find . -name "*.bak" -delete
find . -name "*~" -delete

# Commit cleanup
git add -A
git commit -m "Cleanup: Remove Polly code (migrated to Void fork)"
```

---

## Step 4: Set Up Void Build (30 minutes)

```bash
cd ~/projects/polly-void

# Install dependencies
npm install

# Try initial build
npm run compile

# If build fails, apply fixes from archive
# (See build-fixes documentation)
```

---

## Step 5: Integrate Polly Code (1-2 hours)

```bash
cd ~/projects/polly-void

# Create Polly integration directory
mkdir -p src/polly-integrations

# Copy from archive
cp -r ~/polly/void-migration/polly-code-archive/polly-integrations/* \
      src/polly-integrations/

# Find Void's workbench contribution file
find src -name "*workbench*.main.ts" -o -name "*contribution*.ts" | grep workbench | head -5

# Add Polly contribution import
# (Edit the workbench contribution file)
```

---

## Step 6: Apply Build Fixes (30 minutes)

### CSS Fixes:
```bash
# Find CSS development service
find src -name "cssDevService.ts"

# Apply fixes from archive
# (Copy fallback mechanism, externalize Node modules)
```

### Native Module Fixes:
```bash
# Check if policy watcher exists
grep -r "policy-watcher" src/

# Make optional if needed (apply pattern from archive)
```

---

## Step 7: Test Build (15 minutes)

```bash
cd ~/projects/polly-void

# Clean build
npm run clean
npm run compile

# Launch app
./scripts/code.sh  # or npm start

# Verify:
# - App launches
# - No console errors
# - Polly features visible
```

---

## Troubleshooting

### Build Fails
- Check Node.js version (Void may need specific version)
- Check for missing dependencies
- Apply build fixes from archive

### Polly Code Not Loading
- Check import paths (Void structure may differ)
- Verify contribution registration
- Check console for errors

### CSS Issues
- Apply CSS development service fixes
- Check ripgrep binary path
- Verify import maps

---

## Next Steps

After successful migration:
1. Test all Polly features
2. Customize for Void's structure
3. Integrate with Void's model/chat features
4. Document integration points

---

**Last Updated:** February 5, 2025

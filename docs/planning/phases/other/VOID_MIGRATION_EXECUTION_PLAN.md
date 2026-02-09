# Void Migration Execution Plan - With VSCode Cleanup

**Date:** February 5, 2025  
**Status:** Ready to Execute  
**Purpose:** Migrate to Void and meticulously clean up VSCode work, keeping only Polly-specific code

---

## Overview

This plan executes the Void migration while systematically cleaning up the VSCode fork, preserving only code that will be used with Polly in the Void fork.

---

## Phase 1: Inventory and Catalog (Day 1)

### Step 1.1: Catalog Polly-Specific Code

**Tasks:**
1. **List all Polly integration files**
   ```bash
   find ~/projects/polly-code/src/polly-integrations -type f -name "*.ts" -o -name "*.js" | sort
   ```

2. **List VSCode core modifications**
   - CSS fixes (cssDevService.ts)
   - Native module fixes (policy watcher, etc.)
   - Build task modifications (gulpfile.ts)
   - Workbench modifications (ribbon, etc.)

3. **Document each file's purpose**
   - What it does
   - Will it be needed in Void?
   - Dependencies

**Deliverable:** Complete inventory of Polly code and VSCode modifications

---

### Step 1.2: Identify Reusable Code

**Categories:**

**✅ Keep (Polly-Specific):**
- `src/polly-integrations/core/` - All Polly integration code
- `src/polly-integrations/api/` - API client code
- `src/polly-integrations/backend/` - Backend integration
- `src/polly-integrations/statusBar/` - Status bar contributions
- `src/polly-integrations/views/` - Polly views

**✅ Keep (Build Fixes - Apply to Void):**
- CSS development service fixes
- Native module optional handling
- Build task optimizations
- Debugging knowledge (documented)

**❌ Discard (VSCode-Specific):**
- VSCode core modifications (ribbon, etc.) - Void may have different structure
- Build configuration specific to this fork
- Temporary debug code
- Backup files (.bak, etc.)

**⚠️ Evaluate (May Need):**
- Ribbon navigation code (if Void doesn't have it)
- Theme customizations (if needed)
- Workbench modifications (check Void first)

**Deliverable:** Categorized list of what to keep vs. discard

---

## Phase 2: Fork Void and Initial Setup (Days 1-2)

### Step 2.1: Fork Void Repository

```bash
# Navigate to projects directory
cd ~/projects

# Fork Void (via GitHub UI first, then clone)
git clone https://github.com/YOUR_USERNAME/void.git polly-void
cd polly-void

# Set up remotes
git remote add upstream https://github.com/voideditor/void.git
git remote -v

# Create Polly integration branch
git checkout -b polly-integration
```

### Step 2.2: Initial Build Test

```bash
# Install dependencies
npm install

# Try initial build
npm run compile

# Document build status
# Note any issues
```

### Step 2.3: Apply VSCode Build Fixes

**Apply CSS Fixes:**
- Copy CSS development service fixes
- Apply ripgrep fallback
- Apply Node.js module externalization
- Test CSS import maps

**Apply Native Module Fixes:**
- Make policy watcher optional (if needed)
- Install prebuilt binaries (if needed)
- Test native module loading

**Apply Build Task Fixes:**
- Check if main.js copy needed
- Apply build optimizations
- Document differences

**Deliverable:** Void builds successfully with our fixes applied

---

## Phase 3: Extract and Organize Polly Code (Day 2-3)

### Step 3.1: Create Polly Code Archive

**Create clean directory structure:**

```bash
# In polly workspace (not Void fork)
cd ~/polly
mkdir -p void-migration/polly-code-archive
cd void-migration/polly-code-archive

# Create organized structure
mkdir -p polly-integrations/{core,api,backend,statusBar,views,components}
mkdir -p build-fixes/{css,native-modules,build-tasks}
mkdir -p documentation/{build-knowledge,integration-notes}
```

### Step 3.2: Extract Polly Integration Code

**Copy Polly-specific files:**

```bash
# From VSCode fork
SOURCE=~/projects/polly-code/src/polly-integrations
DEST=~/polly/void-migration/polly-code-archive/polly-integrations

# Copy core integration
cp -r $SOURCE/core/* $DEST/core/

# Copy API client
cp -r $SOURCE/core/api/* $DEST/api/

# Copy backend integration
cp -r $SOURCE/core/backend/* $DEST/backend/

# Copy status bar
cp -r $SOURCE/core/statusBar/* $DEST/statusBar/

# Copy views
cp -r $SOURCE/core/views/* $DEST/views/

# Copy components
cp -r $SOURCE/core/components/* $DEST/components/ 2>/dev/null || true
```

### Step 3.3: Extract Build Fixes

**Document and extract build fixes:**

```bash
# CSS fixes
cp ~/projects/polly-code/src/vs/platform/cssDev/node/cssDevService.ts \
   ~/polly/void-migration/polly-code-archive/build-fixes/css/cssDevService.ts

# Native module fixes
# Document policy watcher optional pattern
# Document parcel watcher prebuilt binary installation

# Build task fixes
# Document main.js copy task
# Document build optimizations
```

**Create documentation:**

```bash
# Create build fixes documentation
cat > ~/polly/void-migration/polly-code-archive/build-fixes/README.md << 'EOF'
# Build Fixes for Void Migration

## CSS Development Service Fixes

### Issue
- ripgrep binary not found
- CSS files not loading in development mode

### Solution
- Added Node.js file walker fallback
- Externalized Node.js built-in modules in esbuild

### Files
- `css/cssDevService.ts` - Modified service with fallback

## Native Module Fixes

### Policy Watcher
- Made optional (try-catch import)
- Continues without it if unavailable

### Parcel Watcher
- Install prebuilt binaries: `npm install @parcel/watcher-darwin-arm64 --legacy-peer-deps`

## Build Task Fixes

### Main.js Copy
- Added task to copy main.js from out-build to out
- Ensures package.json main entry works

EOF
```

**Deliverable:** Clean, organized archive of Polly code and build fixes

---

## Phase 4: Clean Up VSCode Fork (Day 3)

### Step 4.1: Remove Polly Code from VSCode Fork

**After archiving, clean up VSCode fork:**

```bash
cd ~/projects/polly-code

# Remove Polly integration directory
rm -rf src/polly-integrations

# Remove Polly references from workbench
# (Keep for reference, but mark as deprecated)
```

### Step 4.2: Remove Debug Code

**Clean up temporary debug code:**

```bash
# Remove debug log files
rm -f .cursor/debug.log

# Remove backup files
find . -name "*.bak" -delete
find . -name "*~" -delete

# Remove temporary files
find . -name ".DS_Store" -delete
```

### Step 4.3: Document VSCode Fork State

**Create cleanup documentation:**

```bash
cat > ~/projects/polly-code/CLEANUP_NOTES.md << 'EOF'
# VSCode Fork Cleanup Notes

**Date:** February 5, 2025
**Status:** Archived for Void Migration

## What Was Removed

1. **Polly Integration Code**
   - Moved to: `~/polly/void-migration/polly-code-archive/polly-integrations/`
   - Will be integrated into Void fork

2. **Debug Code**
   - Removed temporary debug logs
   - Removed backup files

## What Remains

1. **Build Fixes** (for reference)
   - CSS development service fixes
   - Native module fixes
   - Build task optimizations
   - Documented in archive

2. **VSCode Core Modifications** (for reference)
   - Ribbon navigation (may not be needed in Void)
   - CSS import map fixes
   - Documented in archive

## Next Steps

- VSCode fork is now archived
- All Polly code moved to archive
- Ready for Void migration
EOF
```

**Deliverable:** Clean VSCode fork with Polly code removed

---

## Phase 5: Integrate Polly Code into Void (Days 4-7)

### Step 5.1: Copy Polly Integration to Void

```bash
cd ~/projects/polly-void

# Create Polly integration directory
mkdir -p src/polly-integrations

# Copy from archive
cp -r ~/polly/void-migration/polly-code-archive/polly-integrations/* \
      src/polly-integrations/
```

### Step 5.2: Apply Build Fixes to Void

**Apply CSS fixes:**
- Review Void's CSS development service
- Apply our fixes if needed
- Test CSS import maps

**Apply native module fixes:**
- Check if same issues exist
- Apply fixes if needed
- Test native module loading

**Apply build task fixes:**
- Check if main.js copy needed
- Apply if needed
- Test build

### Step 5.3: Integrate with Void's Structure

**Tasks:**
- Review Void's workbench structure
- Find integration points
- Register Polly contributions
- Test integration

**Files to modify:**
- Void's workbench contribution file (similar to workbench.common.main.ts)
- Add Polly contribution import
- Register Polly services

### Step 5.4: Customize for Void

**Tasks:**
- Review Void's model integration
- Integrate Polly backend
- Customize chat sidebar (if needed)
- Add Polly-specific features

**Deliverable:** Polly code integrated into Void fork

---

## Phase 6: Testing and Verification (Days 8-10)

### Step 6.1: Build Verification

```bash
cd ~/projects/polly-void

# Clean build
npm run clean
npm run compile

# Verify build succeeds
# Check for errors
```

### Step 6.2: Functionality Testing

**Test:**
- App launches
- Polly backend connects
- Status bar shows Polly status
- Views load correctly
- No console errors

### Step 6.3: Integration Testing

**Test:**
- Model integration works
- Chat sidebar works
- Polly features functional
- No conflicts with Void features

**Deliverable:** Fully functional Void fork with Polly integration

---

## Phase 7: Final Cleanup (Day 10)

### Step 7.1: Remove Archive (Optional)

**After successful migration:**

```bash
# Archive can be kept for reference or removed
# Recommend keeping for 1-2 weeks as backup
```

### Step 7.2: Document Final State

**Create migration completion document:**

```bash
cat > ~/projects/polly-void/MIGRATION_COMPLETE.md << 'EOF'
# Void Migration Complete

**Date:** [Date]
**Status:** ✅ Complete

## What Was Migrated

1. **Polly Integration Code**
   - Core integration
   - API client
   - Backend integration
   - Status bar contributions
   - Views

2. **Build Fixes**
   - CSS development service
   - Native module handling
   - Build task optimizations

## What Was Not Migrated

1. **VSCode-Specific Modifications**
   - Ribbon navigation (Void may have different structure)
   - VSCode-specific workbench changes

## Current State

- ✅ Void builds successfully
- ✅ Polly code integrated
- ✅ All features working
- ✅ Ready for development

EOF
```

---

## Cleanup Checklist

### VSCode Fork Cleanup

- [ ] Archive Polly code
- [ ] Remove Polly integration directory
- [ ] Remove debug code
- [ ] Remove backup files
- [ ] Document cleanup
- [ ] Mark fork as archived

### Void Fork Setup

- [ ] Fork Void repository
- [ ] Set up build environment
- [ ] Apply build fixes
- [ ] Verify build works

### Polly Code Migration

- [ ] Copy Polly integration code
- [ ] Apply build fixes
- [ ] Integrate with Void structure
- [ ] Customize for Void
- [ ] Test integration

### Final Verification

- [ ] Build succeeds
- [ ] App launches
- [ ] Polly features work
- [ ] No errors
- [ ] Documentation complete

---

## Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | Day 1 | Inventory and catalog |
| **Phase 2** | Days 1-2 | Fork Void and setup |
| **Phase 3** | Days 2-3 | Extract and organize |
| **Phase 4** | Day 3 | Clean up VSCode fork |
| **Phase 5** | Days 4-7 | Integrate into Void |
| **Phase 6** | Days 8-10 | Testing and verification |
| **Phase 7** | Day 10 | Final cleanup |
| **Total** | 10 days | ~2 weeks |

---

## Success Criteria

- ✅ All Polly code archived and organized
- ✅ VSCode fork cleaned up
- ✅ Void fork created and builds
- ✅ Polly code integrated into Void
- ✅ All features working
- ✅ Documentation complete

---

## Next Actions

1. **Start Phase 1** - Inventory Polly code
2. **Fork Void** - Create Void fork
3. **Archive Code** - Extract and organize
4. **Clean Up** - Remove from VSCode fork
5. **Integrate** - Add to Void fork

---

**Last Updated:** February 5, 2025

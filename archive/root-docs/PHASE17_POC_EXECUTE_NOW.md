# Phase 17 POC: Execute These Commands

**Run these commands in your terminal to start the POC**

---

## Quick Start (Copy & Paste)

```bash
# 1. Navigate to where you want the fork (outside Polly workspace)
cd ~/projects  # or ~/Desktop, or wherever you prefer
mkdir -p polly-code-fork
cd polly-code-fork

# 2. Clone VSCodium (this will take several minutes - ~500MB+)
git clone https://github.com/VSCodium/vscodium.git polly-code
cd polly-code

# 3. Set up upstream remote
git remote add upstream https://github.com/VSCodium/vscodium.git
git remote -v  # Verify

# 4. Create Polly integration branch
git checkout -b polly-integration

# 5. Document base state
echo "# Phase 17 POC Base State" > POC_BASE_STATE.md
echo "**Date:** $(date)" >> POC_BASE_STATE.md
echo "**VSCode Version:** $(git describe --tags 2>/dev/null || echo 'Unknown')" >> POC_BASE_STATE.md
echo "**Commit:** $(git log -1 --format='%H %s')" >> POC_BASE_STATE.md
echo "" >> POC_BASE_STATE.md
echo "## Build Environment" >> POC_BASE_STATE.md
echo "- Node.js: $(node --version)" >> POC_BASE_STATE.md
echo "- Yarn: $(yarn --version)" >> POC_BASE_STATE.md
echo "- Git: $(git --version)" >> POC_BASE_STATE.md

# 6. Create fork structure
mkdir -p polly-integrations/ribbon
mkdir -p polly-integrations/chat
mkdir -p polly-integrations/theme
mkdir -p extensions/polly-chat
mkdir -p extensions/polly-theme

# 7. Create modifications log
cat > polly-integrations/MODIFICATIONS.md << 'EOF'
# Polly Code Modifications Log

This file tracks all modifications made to VSCode/VSCodium for Polly Code.

## Core Modifications

### 1. Activity Bar → Ribbon
- **Status:** Planned
- **File:** `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
- **Change:** Replace activity bar with Polly ribbon
- **Reason:** Match Polly's navigation pattern
- **Date:** [To be filled]

## Extension-Based Features

### 1. Chat Panel
- **Status:** Planned
- **Extension:** `extensions/polly-chat/`
- **Type:** Extension (no core changes)
- **Date:** [To be filled]

### 2. Theme
- **Status:** Planned
- **Extension:** `extensions/polly-theme/`
- **Type:** Extension (no core changes)
- **Date:** [To be filled]
EOF

# 8. Install dependencies (takes 10-20 minutes)
echo "Installing dependencies... (this will take 10-20 minutes)"
yarn install

# 9. Build VSCodium (takes 5-10 minutes)
echo "Building VSCodium... (this will take 5-10 minutes)"
yarn compile

# 10. Test the build
echo ""
echo "=== Setup Complete ==="
echo ""
echo "To test the build, run:"
echo "  Terminal 1: yarn watch"
echo "  Terminal 2: ./scripts/code.sh"
echo ""
echo "Next steps:"
echo "1. Verify VSCodium launches and works"
echo "2. Read: docs/planning/phases/other/PHASE17_POC_RIBBON_INTEGRATION.md"
echo "3. Begin ribbon integration"
```

---

## After Running These Commands

Once the fork is set up and building:

1. **Verify Build Works**
   - Launch VSCodium
   - Test basic functionality
   - Document any issues

2. **Begin Ribbon Integration**
   - Read: `docs/planning/phases/other/PHASE17_POC_RIBBON_INTEGRATION.md`
   - Study activity bar implementation
   - Start porting Polly ribbon

3. **Track Progress**
   - Use: `docs/planning/phases/other/PHASE17_POC_EXECUTION_LOG.md`
   - Document findings as you go

---

## Expected Timeline

- **Clone:** 5-10 minutes (depends on connection)
- **Install dependencies:** 10-20 minutes
- **Build:** 5-10 minutes
- **Total setup time:** ~30-40 minutes

---

## If You Encounter Issues

**Build fails:**
```bash
rm -rf node_modules .yarn/cache
yarn install
yarn compile
```

**Yarn not found:**
```bash
corepack enable
corepack prepare yarn@stable --activate
```

**Git LFS issues:**
```bash
git lfs pull
```

---

**Ready to execute!** Copy the commands above and run them in your terminal.

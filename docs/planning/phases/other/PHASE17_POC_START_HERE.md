# Phase 17 POC: Start Here

**Quick Start Guide for Forking VSCodium**

---

## Prerequisites Check

✅ Node.js: v20.19.5 (installed)  
✅ Yarn: 4.12.0 (available via corepack)  
✅ Git: (should be installed)

---

## Step 1: Choose Fork Location

Decide where you want to clone VSCodium. Recommended locations:

- `~/projects/polly-code` (recommended)
- `~/Desktop/polly-code`
- Any directory outside the Polly workspace

---

## Step 2: Clone VSCodium

```bash
# Navigate to your projects directory
cd ~/projects  # or wherever you prefer

# Clone VSCodium
git clone https://github.com/VSCodium/vscodium.git polly-code
cd polly-code
```

**Note:** This will download ~500MB+ and take several minutes.

---

## Step 3: Set Up Upstream Remote

```bash
# Add upstream remote for tracking updates
git remote add upstream https://github.com/VSCodium/vscodium.git

# Verify
git remote -v
```

---

## Step 4: Create Polly Integration Branch

```bash
# Create branch for Polly-specific changes
git checkout -b polly-integration

# Document base state
echo "# Phase 17 POC Base State" > POC_BASE_STATE.md
echo "**Date:** $(date)" >> POC_BASE_STATE.md
echo "**VSCode Version:** $(git describe --tags)" >> POC_BASE_STATE.md
echo "**Commit:** $(git log -1 --format='%H %s')" >> POC_BASE_STATE.md
```

---

## Step 5: Install Dependencies

```bash
# Install Node.js dependencies (takes 10-20 minutes)
yarn install
```

**Note:** This downloads many packages. Be patient.

---

## Step 6: Build VSCodium

```bash
# Compile TypeScript and build (takes 5-10 minutes)
yarn compile
```

---

## Step 7: Test Base Build

```bash
# Launch VSCodium in development mode
# Terminal 1: Watch mode
yarn watch

# Terminal 2: Run VSCodium
./scripts/code.sh  # macOS/Linux
```

**Verify:**
- ✅ VSCodium launches
- ✅ Can open files
- ✅ Can edit and save
- ✅ Basic functionality works

---

## Step 8: Create Fork Structure

```bash
# Create directories for Polly integrations
mkdir -p polly-integrations/ribbon
mkdir -p polly-integrations/chat
mkdir -p polly-integrations/theme
mkdir -p extensions/polly-chat
mkdir -p extensions/polly-theme

# Create modifications log
cat > polly-integrations/MODIFICATIONS.md << 'EOF'
# Polly Code Modifications Log

## Core Modifications

### 1. Activity Bar → Ribbon
- **Status:** Planned
- **File:** `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
- **Change:** Replace activity bar with Polly ribbon
- **Date:** [To be filled]

## Extension-Based Features

### 1. Chat Panel
- **Status:** Planned
- **Extension:** `extensions/polly-chat/`
- **Date:** [To be filled]

### 2. Theme
- **Status:** Planned
- **Extension:** `extensions/polly-theme/`
- **Date:** [To be filled]
EOF
```

---

## Next Steps

Once the fork is set up and building:

1. **Study VSCode Architecture** - Read `PHASE17_POC_RIBBON_INTEGRATION.md`
2. **Begin Ribbon Integration** - Follow the integration guide
3. **Track Progress** - Use `PHASE17_POC_EXECUTION_LOG.md`

---

## Documentation Reference

- **Setup Guide:** `PHASE17_POC_SETUP.md` (detailed)
- **Ribbon Integration:** `PHASE17_POC_RIBBON_INTEGRATION.md`
- **Chat Integration:** `PHASE17_POC_CHAT_INTEGRATION.md`
- **Execution Log:** `PHASE17_POC_EXECUTION_LOG.md`

---

## Troubleshooting

### Build Fails

```bash
# Clear and rebuild
rm -rf node_modules .yarn/cache
yarn install
yarn compile
```

### Yarn Issues

```bash
# Ensure corepack is enabled
corepack enable
corepack prepare yarn@stable --activate
```

---

**Status:** Ready to execute these steps

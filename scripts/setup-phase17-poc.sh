#!/bin/bash
# Phase 17 POC Setup Script
# Sets up VSCodium fork for Polly Code workspace

set -e  # Exit on error

echo "=== Phase 17 POC: VSCodium Fork Setup ==="
echo ""

# Configuration
VSCODIUM_REPO="https://github.com/VSCodium/vscodium.git"
FORK_DIR="polly-code"
UPSTREAM_REPO="https://github.com/VSCodium/vscodium.git"

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18.x or later."
    exit 1
fi

if ! command -v yarn &> /dev/null; then
    echo "❌ Yarn not found. Please install Yarn."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git."
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Get directory for fork
read -p "Enter directory for VSCodium fork (default: ~/projects): " FORK_PARENT
FORK_PARENT=${FORK_PARENT:-~/projects}

# Create directory if needed
mkdir -p "$FORK_PARENT"
cd "$FORK_PARENT"

# Check if fork already exists
if [ -d "$FORK_DIR" ]; then
    echo "⚠️  Directory $FORK_DIR already exists."
    read -p "Continue anyway? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
else
    # Clone VSCodium
    echo "Cloning VSCodium repository..."
    git clone "$VSCODIUM_REPO" "$FORK_DIR"
    echo "✅ Repository cloned"
fi

cd "$FORK_DIR"

# Set up upstream remote
echo ""
echo "Setting up upstream remote..."
if git remote | grep -q upstream; then
    echo "⚠️  Upstream remote already exists. Skipping..."
else
    git remote add upstream "$UPSTREAM_REPO"
    echo "✅ Upstream remote added"
fi

# Create Polly integration branch
echo ""
echo "Creating Polly integration branch..."
if git branch | grep -q polly-integration; then
    echo "⚠️  Branch polly-integration already exists."
    read -p "Switch to it? (y/n): " SWITCH
    if [ "$SWITCH" == "y" ]; then
        git checkout polly-integration
    fi
else
    git checkout -b polly-integration
    echo "✅ Branch created and checked out"
fi

# Document base state
echo ""
echo "Documenting base state..."
echo "# Phase 17 POC Base State" > POC_BASE_STATE.md
echo "" >> POC_BASE_STATE.md
echo "**Date:** $(date)" >> POC_BASE_STATE.md
echo "**VSCode Version:** $(git describe --tags 2>/dev/null || echo 'Unknown')" >> POC_BASE_STATE.md
echo "**Commit:** $(git log -1 --format='%H %s')" >> POC_BASE_STATE.md
echo "" >> POC_BASE_STATE.md
echo "## Build Environment" >> POC_BASE_STATE.md
echo "- Node.js: $(node --version)" >> POC_BASE_STATE.md
echo "- Yarn: $(yarn --version)" >> POC_BASE_STATE.md
echo "- Git: $(git --version)" >> POC_BASE_STATE.md
echo "✅ Base state documented"

# Create fork structure
echo ""
echo "Creating fork structure..."
mkdir -p polly-integrations/ribbon
mkdir -p polly-integrations/chat
mkdir -p polly-integrations/theme
mkdir -p extensions/polly-chat
mkdir -p extensions/polly-theme
echo "✅ Directory structure created"

# Create modifications log
echo ""
echo "Creating modifications log..."
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
echo "✅ Modifications log created"

# Install dependencies
echo ""
echo "Installing dependencies (this may take 10-20 minutes)..."
read -p "Install dependencies now? (y/n): " INSTALL
if [ "$INSTALL" == "y" ]; then
    yarn install
    echo "✅ Dependencies installed"
else
    echo "⏭️  Skipping dependency installation. Run 'yarn install' when ready."
fi

# Summary
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Fork location: $FORK_PARENT/$FORK_DIR"
echo ""
echo "Next steps:"
echo "1. cd $FORK_PARENT/$FORK_DIR"
echo "2. yarn install (if not done)"
echo "3. yarn compile"
echo "4. Follow PHASE17_POC_RIBBON_INTEGRATION.md for ribbon integration"
echo ""
echo "Documentation:"
echo "- POC Setup: docs/planning/phases/other/PHASE17_POC_SETUP.md"
echo "- Ribbon Integration: docs/planning/phases/other/PHASE17_POC_RIBBON_INTEGRATION.md"
echo "- Chat Integration: docs/planning/phases/other/PHASE17_POC_CHAT_INTEGRATION.md"
echo "- Execution Log: docs/planning/phases/other/PHASE17_POC_EXECUTION_LOG.md"
echo ""

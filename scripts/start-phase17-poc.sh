#!/bin/bash
# Phase 17 POC: Quick Start Script
# Run this script to set up the VSCodium fork

set -e

echo "=== Phase 17 POC: VSCodium Fork Setup ==="
echo ""

# Get fork location
read -p "Where should we clone VSCodium? (default: ~/projects/polly-code): " FORK_LOCATION
FORK_LOCATION=${FORK_LOCATION:-~/projects/polly-code}

FORK_DIR=$(dirname "$FORK_LOCATION")
FORK_NAME=$(basename "$FORK_LOCATION")

# Create parent directory
mkdir -p "$FORK_DIR"
cd "$FORK_DIR"

# Check if already exists
if [ -d "$FORK_NAME" ]; then
    echo "⚠️  Directory $FORK_NAME already exists."
    read -p "Continue with existing directory? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Aborted."
        exit 1
    fi
    cd "$FORK_NAME"
else
    # Clone VSCodium
    echo "Cloning VSCodium repository..."
    echo "This will download ~500MB and take several minutes..."
    git clone https://github.com/VSCodium/vscodium.git "$FORK_NAME"
    cd "$FORK_NAME"
fi

# Set up upstream
if ! git remote | grep -q upstream; then
    echo "Setting up upstream remote..."
    git remote add upstream https://github.com/VSCodium/vscodium.git
fi

# Create branch
if ! git branch | grep -q polly-integration; then
    echo "Creating polly-integration branch..."
    git checkout -b polly-integration
else
    echo "Switching to polly-integration branch..."
    git checkout polly-integration
fi

# Document base state
echo "Documenting base state..."
cat > POC_BASE_STATE.md << EOF
# Phase 17 POC Base State

**Date:** $(date)
**VSCode Version:** $(git describe --tags 2>/dev/null || echo 'Unknown')
**Commit:** $(git log -1 --format='%H %s')

## Build Environment
- Node.js: $(node --version)
- Yarn: $(yarn --version 2>/dev/null || echo 'Not found')
- Git: $(git --version)
EOF

# Create structure
echo "Creating fork structure..."
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

echo ""
echo "✅ Fork structure created"
echo ""
echo "Next: Install dependencies and build"
echo ""
read -p "Install dependencies now? (y/n): " INSTALL_DEPS

if [ "$INSTALL_DEPS" == "y" ]; then
    echo "Installing dependencies (10-20 minutes)..."
    yarn install
    
    echo ""
    read -p "Build VSCodium now? (y/n): " BUILD
    
    if [ "$BUILD" == "y" ]; then
        echo "Building VSCodium (5-10 minutes)..."
        yarn compile
        
        echo ""
        echo "=== Setup Complete ==="
        echo ""
        echo "To test:"
        echo "  Terminal 1: yarn watch"
        echo "  Terminal 2: ./scripts/code.sh"
    else
        echo "Build skipped. Run 'yarn compile' when ready."
    fi
else
    echo "Dependencies skipped. Run 'yarn install' when ready."
fi

echo ""
echo "Fork location: $FORK_LOCATION"
echo ""
echo "Documentation:"
echo "  - Ribbon Integration: /Users/brettgershon/polly/docs/planning/phases/other/PHASE17_POC_RIBBON_INTEGRATION.md"
echo "  - Chat Integration: /Users/brettgershon/polly/docs/planning/phases/other/PHASE17_POC_CHAT_INTEGRATION.md"
echo ""

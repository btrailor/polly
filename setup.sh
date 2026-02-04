#!/bin/bash
# Apollo Setup Script
# Sets up Apollo on your Mac

set -e

echo "=== Apollo Setup ==="
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Install with: brew install python@3.11"
    exit 1
fi

# Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo "Warning: Ollama not found. Install with: brew install ollama"
    echo "Apollo requires Ollama for local models."
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p ~/.apollo
mkdir -p config

# Create default config if not exists
if [ ! -f config/config.yaml ]; then
    echo "Creating default config..."
    cp config/config.example.yaml config/config.yaml
    echo ""
    echo "IMPORTANT: Edit config/config.yaml with your paths!"
    echo "  - Set your Obsidian vault path"
    echo "  - Set your codebase paths"
    echo ""
fi

# Create CLI alias
SHELL_RC=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    APOLLO_DIR="$(pwd)"
    ALIAS_LINE="alias apo='${APOLLO_DIR}/venv/bin/python -m apollo'"

    if ! grep -q "alias apo=" "$SHELL_RC" 2>/dev/null; then
        echo "" >> "$SHELL_RC"
        echo "# Apollo CLI" >> "$SHELL_RC"
        echo "$ALIAS_LINE" >> "$SHELL_RC"
        echo "Added 'apo' alias to $SHELL_RC"
    fi
fi

# Pull Ollama models
if command -v ollama &> /dev/null; then
    echo ""
    echo "Pulling Ollama models..."
    ollama pull nomic-embed-text || echo "Warning: Could not pull embedding model"
    ollama pull llama3.1:7b || echo "Warning: Could not pull chat model"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit config/config.yaml with your paths"
echo "  2. Start Ollama: ollama serve"
echo "  3. Index your knowledge: python -m apollo index"
echo "  4. Query Apollo: python -m apollo 'Your question'"
echo ""
echo "Or use the alias (after restarting terminal):"
echo "  apo 'What patterns do I use?'"
echo ""

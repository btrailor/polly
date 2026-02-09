# Polly: Edge-Native Personal AI System

## A prototype for an AI assistant that deeply understands you

Polly is an edge-first AI system designed to:
- **Understand your domains**: Query your Obsidian vault, codebases, and filesystem
- **Learn your patterns**: Build a personal knowledge graph from your work
- **Adapt to your thinking**: Apply your personal mental models to every response
- **Execute efficiently**: Route between local models and cloud when needed
- **Work across devices**: iPhone, MacBook, anywhere via Tailscale

## Philosophy

This system embodies several core principles:

- **Continuation over completion** (infinite games): The system evolves with you
- **Instruments over tracks**: Generative tools that create new possibilities
- **Constraint as meaning-creation**: Boundaries that enable rather than limit
- **Autonomous infrastructure**: You own the stack, no platform lock-in

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         POLLY CORE                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │   Domains   │  │   Pattern   │  │    Intelligent Router   ││
│  │   Engine    │  │   Learner   │  │   (Local ↔ Cloud)       ││
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘│
│         │                │                      │              │
│         │      ┌─────────────────┐              │              │
│         │      │ Mental Models   │              │              │
│         │      │ (12 defaults +  │              │              │
│         │      │  custom)        │              │              │
│         │      └────────┬────────┘              │              │
│         │               │                       │              │
│         └───────────────┴───────────────────────┘              │
│                          │                                      │
│              ┌───────────▼───────────┐                         │
│              │   Unified RAG Layer   │                         │
│              │   ┌─────────────────┐ │                         │
│              │   │ Obsidian Vault  │ │                         │
│              │   │ Project Codebases│ │                         │
│              │   │ Filesystem Docs │ │                         │
│              │   │ Pattern Memory  │ │                         │
│              │   └─────────────────┘ │                         │
│              └───────────────────────┘                         │
│                                                                 │
├────────────────────────────────────────────────────────────────┤
│                       INTERFACES                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │   CLI    │  │  VS Code │  │  Polly   │  │  Open WebUI  │  │
│  │ (polly)  │  │Extension │  │   App    │  │   Bridge     │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Option 1: Electron App (Recommended)

```bash
cd electron-app
npm install
npm start
```

The app will guide you through setup with a visual wizard.

### Option 2: Command Line

```bash
# 1. Install dependencies
cd polly-prototype
pip install -r requirements.txt

# 2. Configure your paths
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your paths

# 3. Index your knowledge
python -m polly index

# 4. Start Polly
python -m polly serve

# 5. Query from anywhere
polly "What patterns do I use for MIDI handling?"
```

## What Makes Polly Different

### 1. Personal Mental Models 🧠
Polly learns your thinking frameworks and applies them automatically:
- **12 default models** including Infinite Games, Systems Thinking, Socratic Method
- **Create custom models** with templates
- **Context-aware activation** based on what you're working on
- **Per-conversation override** for fine control

### 2. Domain-Aware Intelligence
Not just file patterns—deep understanding of five creative and technical domains:
- **Sigils** (code), **Signals** (audio), **Scrolls** (writing), **Glyphs** (design), **Grids** (systems)

### 3. Pattern Learning
Automatically learns from your work patterns and reuses them in future queries.

### 4. True Data Autonomy
- All data stored locally in `~/.polly/`
- You own your knowledge graph
- No platform lock-in
- Full export capabilities

## Five Domains

Polly understands your five domains:

| Domain | Focus | File Patterns |
|--------|-------|---------------|
| **Sigils** | Code, infrastructure, automation | `.py`, `.rs`, `.go`, `docker-compose.yaml` |
| **Signals** | Audio programming, synthesis | `.scd`, `.lua`, `norns/`, `supercollider/` |
| **Scrolls** | Writing, pedagogy, documentation | `.md`, `vault/`, `essays/` |
| **Glyphs** | Visual work, design | `.fig`, `.sketch`, `design/` |
| **Grids** | Systems thinking, frameworks | `frameworks/`, `models/`, tagged notes |

## Components

### 1. Unified RAG System (`core/rag.py`)
Multi-source semantic search across your entire knowledge base.

### 2. Mental Models System (`core/mental_models.py`)
Your personal thinking frameworks guide every response:
- 12 default models (Infinite Games, Systems Thinking, Socratic Method, etc.)
- Custom model creation with templates
- Three-tier context activation (domain, page, persona)
- Per-conversation override
- PIL compression for efficiency

### 3. Pattern Learner (`learners/patterns.py`)
Discovers and tracks recurring patterns in your work over time.

### 4. Domain Engine (`core/domains.py`)
Understands context and routes queries to relevant sources.

### 5. Intelligent Router (`core/router.py`)
Seamlessly pivots between local (Ollama) and cloud (Anthropic/OpenAI) models.

### 6. Personal Knowledge Graph (`core/graph.py`)
Builds connections between concepts, files, and patterns.

## Electron App Features

- **Setup Wizard**: One-click installation of Python environment and AI models
- **Chat Interface**: Beautiful chat UI with domain-aware responses
- **Dashboard**: Visual overview of indexed knowledge and patterns
- **System Tray**: Quick access from menu bar
- **IDE Integration**: OpenAI-compatible API for Cursor/Continue

## Future Hardware

When Apple Neural Engine becomes more accessible, or dedicated AI hardware arrives:
- On-device embedding generation
- Local fine-tuned models
- Real-time pattern detection
- Continuous learning without cloud

## Directory layout

- **openspec/** — Project tracking and specs (status, roadmap, domain specs). Start here for "where we are" and "what's next."
- **docs/** — Detailed docs (planning, status, troubleshooting). **archive/root-docs/** — Root-level planning docs moved here (MASTER_ROADMAP, FEATURES_TO_BUILD, etc.).
- **tests/** — Test suite. **tests/root/** — Tests moved from repo root during cleanup.
- **scripts/** — Dev/ops scripts. **scripts/debug/**, **scripts/demo/**, **scripts/diagnostics/** — Debug, demo, and diagnostic scripts moved from root.

## License

Personal use. Built on open-source foundations.

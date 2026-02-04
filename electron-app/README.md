# Polly - Electron App

A beautiful desktop interface for your edge-native personal AI system.

## Features

- **Setup Wizard**: One-click installation of all dependencies
- **Chat Interface**: Query your knowledge base with intelligent routing
- **Dashboard**: Visual overview of your indexed knowledge
- **Knowledge Management**: Index and manage Obsidian vaults and codebases
- **Pattern Viewer**: See learned patterns from your work
- **System Tray**: Quick access and background operation

## Development

### Prerequisites

- Node.js 18+
- npm or pnpm
- Python 3.10+ (for backend)
- Ollama (for local models)

### Setup

```bash
cd electron-app

# Install dependencies
npm install

# Run in development mode
npm run dev
```

### Building

```bash
# Build for macOS
npm run build:mac

# Output will be in dist/
```

## Architecture

```
electron-app/
├── src/
│   ├── main/
│   │   ├── main.js      # Main process - window management, IPC
│   │   └── preload.js   # Secure bridge to renderer
│   └── renderer/
│       ├── index.html   # Main HTML
│       ├── app.js       # UI logic
│       └── styles/
│           └── main.css # Styling
├── assets/              # Icons and images
├── scripts/             # Build helpers
└── package.json
```

## IPC API

The app communicates with the Python backend through these channels:

### Store
- `getStore(key)` - Get persisted value
- `setStore(key, value)` - Save value

### Setup
- `checkDependencies()` - Check Python, Ollama
- `runSetup(options)` - Install environment

### Server
- `startServer()` - Start Polly backend
- `stopServer()` - Stop backend
- `getServerStatus()` - Check if running

### Knowledge
- `indexKnowledge(options)` - Index vault/code

### Query
- `query(text, options)` - Send query to Polly

## Keyboard Shortcuts

- `Cmd+Shift+P` - Quick query (from anywhere)
- `Cmd+,` - Settings
- `Cmd+Q` - Quit (closes to tray)

## Configuration

Settings are stored in:
- macOS: `~/Library/Application Support/polly/config.json`
- Linux: `~/.config/polly/config.json`
- Windows: `%APPDATA%/polly/config.json`

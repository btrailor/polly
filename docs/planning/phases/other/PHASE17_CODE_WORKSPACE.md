# Phase 17: Integrated Code Workspace

**Status:** Planned  
**Duration:** 3 weeks  
**Prerequisites:** Phase 1.5 (Domains), Phase 2 (RAG), Phase 11 (Multi-Model), Phase 12 (Graph), Phase 13 (Patterns), Phase 16 (Notes)  
**Enables:** Full integrated development within Polly

---

## Overview

Phase 17 transforms Polly from a knowledge management system into a comprehensive development environment. Rather than embedding all of OpenCode, we build essential coding tools directly into Polly so that 80% of development tasks can happen without leaving the application—with full context always available.

### Vision

**Current state:** Developers switch between Polly (knowledge/notes), external IDE (coding), terminal (commands), and browser (documentation).

**Target state:** Polly provides an integrated workspace where code, notes, patterns, and AI assistance live side-by-side. Quick edits, explorations, and learning happen in Polly. Complex debugging and IDE-specific features use external tools via Phase 15 (MCP).

### 80/20 Philosophy

**80% in Polly:**
- Quick code edits
- Exploring codebases
- Writing scripts and utilities
- Learning new languages/libraries
- Prototyping ideas
- Code → note creation

**20% in External IDE (via MCP):**
- Advanced debugging (breakpoints, step-through)
- IDE extensions and plugins
- Language-specific refactoring tools
- Performance profiling

---

## Three-Week Implementation

### Week 1: Core Editor (5-7 days)

#### Monaco Editor for Code

**What:** Same Monaco editor as Phase 16, configured for code editing

**Built-in Language Support (9 languages):**
1. **Python** - Complete syntax highlighting, basic IntelliSense
2. **JavaScript** - ES6+, JSX support
3. **TypeScript** - Full type support
4. **C** - Standard C syntax
5. **C++** - Modern C++ support
6. **C#** - .NET syntax
7. **Lua** - Scripting support
8. **Rust** - Modern Rust syntax
9. **Go** - Go modules support

**Features:**
- Multi-file tabs
- Syntax highlighting
- Code folding
- Bracket matching
- Auto-indentation
- Find/replace with regex
- Multi-cursor editing
- IntelliSense (basic, Monaco built-in)

**Implementation:**

```typescript
import * as monaco from 'monaco-editor';

class CodeEditor {
  private editor: monaco.editor.IStandaloneCodeEditor;
  
  constructor(containerElement: HTMLElement) {
    this.editor = monaco.editor.create(containerElement, {
      theme: 'vs-dark',
      fontSize: 13,
      fontFamily: 'SF Mono, Monaco, Consolas, monospace',
      minimap: { enabled: true },
      lineNumbers: 'on',
      folding: true,
      bracketPairColorization: { enabled: true },
      scrollBeyondLastLine: false,
      automaticLayout: true
    });
    
    // Configure for code-specific features
    this.setupCodeActions();
    this.setupIntelliSense();
  }
  
  loadFile(filePath: string) {
    const content = fs.readFileSync(filePath, 'utf-8');
    const language = this.detectLanguage(filePath);
    
    const model = monaco.editor.createModel(content, language, 
      monaco.Uri.file(filePath));
    this.editor.setModel(model);
  }
  
  private detectLanguage(filePath: string): string {
    const ext = path.extname(filePath).toLowerCase();
    const langMap = {
      '.py': 'python',
      '.js': 'javascript',
      '.ts': 'typescript',
      '.c': 'c',
      '.cpp': 'cpp',
      '.cc': 'cpp',
      '.cs': 'csharp',
      '.lua': 'lua',
      '.rs': 'rust',
      '.go': 'go'
    };
    return langMap[ext] || 'plaintext';
  }
}
```

#### File Tree with Git Status

**Features:**
- Project folder structure
- File type icons
- Git status indicators (M = modified, U = untracked, A = added)
- Expand/collapse folders
- Right-click context menu
- Drag-and-drop to move files

**UI:**

```
┌─────────────────────────────────────────┐
│ Files                      [Refresh] [⚙]│
├─────────────────────────────────────────┤
│ 📂 polly-app/                           │
│   ├─ 📂 src/                            │
│   │  ├─ 📄 main.ts          M           │
│   │  ├─ 📄 config.ts                    │
│   │  └─ 📂 components/                  │
│   │     ├─ 📄 Chat.tsx      M           │
│   │     └─ 📄 Editor.tsx                │
│   ├─ 📂 tests/                          │
│   │  └─ 📄 main.test.ts     U           │
│   ├─ 📄 package.json                    │
│   └─ 📄 tsconfig.json                   │
└─────────────────────────────────────────┘

Legend:
M = Modified  U = Untracked  A = Added (staged)
```

**Implementation:**

```typescript
interface FileNode {
  type: 'file' | 'directory';
  name: string;
  path: string;
  gitStatus?: 'M' | 'U' | 'A' | 'D';
  children?: FileNode[];
}

class FileTreeView {
  async buildTree(projectPath: string): Promise<FileNode[]> {
    const gitStatus = await this.getGitStatus(projectPath);
    return await this.buildNode(projectPath, gitStatus);
  }
  
  private async buildNode(
    dirPath: string, 
    gitStatus: Map<string, string>
  ): Promise<FileNode[]> {
    const entries = await fs.promises.readdir(dirPath, { withFileTypes: true });
    const nodes: FileNode[] = [];
    
    for (const entry of entries) {
      // Skip hidden files and node_modules
      if (entry.name.startsWith('.') || entry.name === 'node_modules') {
        continue;
      }
      
      const fullPath = path.join(dirPath, entry.name);
      const relativePath = path.relative(this.projectRoot, fullPath);
      
      if (entry.isDirectory()) {
        nodes.push({
          type: 'directory',
          name: entry.name,
          path: fullPath,
          children: await this.buildNode(fullPath, gitStatus)
        });
      } else {
        nodes.push({
          type: 'file',
          name: entry.name,
          path: fullPath,
          gitStatus: gitStatus.get(relativePath)
        });
      }
    }
    
    return nodes.sort((a, b) => {
      // Directories first, then files
      if (a.type !== b.type) return a.type === 'directory' ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
  }
  
  private async getGitStatus(projectPath: string): Promise<Map<string, string>> {
    const statusMap = new Map();
    
    try {
      const { stdout } = await execAsync('git status --porcelain', { 
        cwd: projectPath 
      });
      
      const lines = stdout.split('\n');
      for (const line of lines) {
        if (!line) continue;
        
        const status = line.substring(0, 2).trim();
        const file = line.substring(3);
        
        if (status === 'M' || status === 'MM') statusMap.set(file, 'M');
        else if (status === '??' || status === 'A') statusMap.set(file, 'U');
        else if (status === 'A') statusMap.set(file, 'A');
      }
    } catch (error) {
      console.log('Not a git repository');
    }
    
    return statusMap;
  }
}
```

#### Integrated Terminal

**What:** xterm.js terminal emulator embedded in Polly

**Features:**
- Multiple terminal tabs
- Split terminal (horizontal/vertical)
- Shell selection (bash, zsh, fish)
- Color themes
- Copy/paste support
- Search in terminal
- Clear/reset

**UI:**

```
┌─────────────────────────────────────────────────────────┐
│ Terminal              [+] [Split] [⚙]    × bash × zsh  │
├─────────────────────────────────────────────────────────┤
│ $ npm run build                                         │
│ > polly@1.0.0 build                                     │
│ > tsc && vite build                                     │
│                                                         │
│ vite v4.0.0 building for production...                 │
│ ✓ 245 modules transformed.                             │
│ dist/index.html                    1.23 kB             │
│ dist/assets/index-a3b4c5d6.js    145.67 kB             │
│ ✓ built in 3.45s                                       │
│                                                         │
│ $█                                                      │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```typescript
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import * as pty from 'node-pty';

class IntegratedTerminal {
  private terminal: Terminal;
  private ptyProcess: any;
  private fitAddon: FitAddon;
  
  constructor(containerElement: HTMLElement, shell: string = 'zsh') {
    // Create xterm terminal
    this.terminal = new Terminal({
      cursorBlink: true,
      fontSize: 13,
      fontFamily: 'SF Mono, Monaco, Consolas, monospace',
      theme: {
        background: '#1e1e1e',
        foreground: '#d4d4d4'
      }
    });
    
    // Add addons
    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    this.terminal.loadAddon(new WebLinksAddon());
    
    // Open terminal
    this.terminal.open(containerElement);
    this.fitAddon.fit();
    
    // Create PTY process
    this.ptyProcess = pty.spawn(shell, [], {
      name: 'xterm-256color',
      cols: this.terminal.cols,
      rows: this.terminal.rows,
      cwd: process.env.HOME,
      env: process.env
    });
    
    // Wire up data flow
    this.ptyProcess.onData(data => this.terminal.write(data));
    this.terminal.onData(data => this.ptyProcess.write(data));
    
    // Handle resize
    this.terminal.onResize(({ cols, rows }) => {
      this.ptyProcess.resize(cols, rows);
    });
  }
  
  changeCwd(directory: string) {
    this.ptyProcess.write(`cd ${directory}\n`);
  }
  
  runCommand(command: string) {
    this.ptyProcess.write(`${command}\n`);
  }
  
  clear() {
    this.terminal.clear();
  }
  
  dispose() {
    this.ptyProcess.kill();
    this.terminal.dispose();
  }
}
```

#### Git Operations UI

**Features:**
- View changes (modified, staged, untracked)
- Stage/unstage files
- Commit with message
- Push/pull
- Branch operations (switch, create, delete)
- Visual diff viewer

**UI (Git Panel):**

```
┌─────────────────────────────────────────────────────────┐
│ Git                               [Refresh] [⚙]         │
├─────────────────────────────────────────────────────────┤
│ Branch: main ▼                    [Push] [Pull]         │
│                                                         │
│ Changes (3)                                             │
│ ☑ src/main.ts                     M  [Diff]            │
│ ☐ src/components/Chat.tsx         M  [Diff]            │
│ ☐ tests/main.test.ts              U  [Diff]            │
│                                                         │
│ [Stage All] [Unstage All]                              │
│                                                         │
│ Commit Message:                                         │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Add intelligent routing to Phase 11             │   │
│ │                                                 │   │
│ │ - Implement pre-flight confidence checks        │   │
│ │ - Add output quality analysis                   │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ [Commit] [Commit & Push]                               │
│                                                         │
│ Recent Commits:                                         │
│ • a3b4c5d Add Phase 16 notes system (2 hours ago)      │
│ • 1f2e3d4 Update RAG weights (yesterday)               │
└─────────────────────────────────────────────────────────┘
```

**Diff Viewer:**

```
┌─────────────────────────────────────────────────────────┐
│ Diff: src/main.ts                             [Close]  │
├───────────────────────┬─────────────────────────────────┤
│ Original              │ Modified                        │
├───────────────────────┼─────────────────────────────────┤
│  1 import { app } ... │  1 import { app } ...           │
│  2                    │  2                              │
│  3 function main() {  │  3 function main() {            │
│  4   const model =    │  4   const router =             │ ←
│  5     getModel();    │  5     new Router();            │ ←
│  6                    │  6                              │
│  7   app.listen();    │  7   app.use(router);           │ ←
│  8 }                  │  8   app.listen();              │ ←
│  9                    │  9 }                            │
└───────────────────────┴─────────────────────────────────┘
```

**Implementation:**

```typescript
class GitManager {
  private projectPath: string;
  
  async getStatus(): Promise<GitStatus> {
    const { stdout } = await execAsync('git status --porcelain', {
      cwd: this.projectPath
    });
    
    const modified = [];
    const untracked = [];
    const staged = [];
    
    const lines = stdout.split('\n');
    for (const line of lines) {
      if (!line) continue;
      
      const status = line.substring(0, 2);
      const file = line.substring(3);
      
      if (status === ' M' || status === 'MM') modified.push(file);
      else if (status === '??') untracked.push(file);
      else if (status.startsWith('A') || status.startsWith('M')) staged.push(file);
    }
    
    return { modified, untracked, staged };
  }
  
  async stageFile(file: string) {
    await execAsync(`git add "${file}"`, { cwd: this.projectPath });
  }
  
  async unstageFile(file: string) {
    await execAsync(`git reset HEAD "${file}"`, { cwd: this.projectPath });
  }
  
  async commit(message: string): Promise<string> {
    const { stdout } = await execAsync(`git commit -m "${message}"`, {
      cwd: this.projectPath
    });
    return stdout;
  }
  
  async push(remote: string = 'origin', branch: string = 'main') {
    await execAsync(`git push ${remote} ${branch}`, {
      cwd: this.projectPath
    });
  }
  
  async pull(remote: string = 'origin', branch: string = 'main') {
    await execAsync(`git pull ${remote} ${branch}`, {
      cwd: this.projectPath
    });
  }
  
  async getDiff(file: string): Promise<string> {
    const { stdout } = await execAsync(`git diff "${file}"`, {
      cwd: this.projectPath
    });
    return stdout;
  }
  
  async getBranches(): Promise<string[]> {
    const { stdout } = await execAsync('git branch', {
      cwd: this.projectPath
    });
    
    return stdout.split('\n')
      .map(line => line.replace('*', '').trim())
      .filter(line => line.length > 0);
  }
  
  async switchBranch(branch: string) {
    await execAsync(`git checkout ${branch}`, {
      cwd: this.projectPath
    });
  }
  
  async createBranch(branch: string) {
    await execAsync(`git checkout -b ${branch}`, {
      cwd: this.projectPath
    });
  }
}
```

---

### Week 2: Polly Integration (5-7 days)

#### Chat Panel with Full Context

**Purpose:** Polly's AI chat available while coding, with code context automatically included

**Position:** Right sidebar (collapsible)

**Context Awareness:**
- Current file (auto-included)
- Selected code (highlighted lines)
- Related files (from Phase 12 graph)
- Full conversation history
- Phase 11 routing active

**UI:**

```
┌─────────────────────────────────────────┐
│ Polly Chat                     [−] [×]  │
├─────────────────────────────────────────┤
│ Context: 3 files, 450 lines             │
│ ├─ main.ts (current)                    │
│ ├─ config.ts (related)                  │
│ └─ utils.ts (related)                   │
│ [Edit Context]                          │
├─────────────────────────────────────────┤
│ Model: Claude Pro ▼   [Override]        │
│ Confidence: 75% ●●●○○                   │
├─────────────────────────────────────────┤
│ You: How can I refactor this to use    │
│      the strategy pattern?              │
│                                         │
│ Polly: I can help refactor this code   │
│        to use the strategy pattern...   │
│                                         │
│ [Apply to Code] [Save as Note]          │
├─────────────────────────────────────────┤
│ Quick Actions:                          │
│ • Explain selection                     │
│ • Find bugs                             │
│ • Write tests                           │
│ • Generate docs                         │
└─────────────────────────────────────────┘
```

**Implementation:**

```typescript
class CodeChatPanel {
  private editor: CodeEditor;
  private currentContext: CodeContext;
  
  constructor(editor: CodeEditor) {
    this.editor = editor;
    this.updateContext();
    
    // Update context when file or selection changes
    editor.onDidChangeModel(() => this.updateContext());
    editor.onDidChangeCursorSelection(() => this.updateContext());
  }
  
  private async updateContext() {
    const currentFile = this.editor.getCurrentFile();
    const selection = this.editor.getSelection();
    const relatedFiles = await this.getRelatedFiles(currentFile);
    
    this.currentContext = {
      currentFile: {
        path: currentFile,
        content: fs.readFileSync(currentFile, 'utf-8'),
        selection: selection ? this.editor.getSelectedText() : null
      },
      relatedFiles: relatedFiles.map(path => ({
        path,
        content: fs.readFileSync(path, 'utf-8')
      })),
      tokenCount: this.calculateTokens()
    };
    
    this.renderContextIndicator();
  }
  
  private async getRelatedFiles(filePath: string): Promise<string[]> {
    // Use Phase 12 knowledge graph to find related files
    const graph = await getKnowledgeGraph();
    const node = graph.findNodeByPath(filePath);
    
    if (!node) return [];
    
    // Get connected nodes (imports, references, etc.)
    const related = graph.getConnectedNodes(node)
      .filter(n => n.type === 'file')
      .map(n => n.path)
      .slice(0, 5); // Max 5 related files
    
    return related;
  }
  
  async sendQuery(query: string): Promise<string> {
    // Build prompt with context
    const prompt = this.buildPrompt(query);
    
    // Route through Phase 11 intelligent routing
    const router = new IntelligentRouter();
    const response = await router.route_query(prompt);
    
    return response.text;
  }
  
  private buildPrompt(query: string): string {
    let prompt = `You are helping with code in the following context:\n\n`;
    
    // Add current file
    prompt += `Current file: ${this.currentContext.currentFile.path}\n`;
    prompt += `\`\`\`\n${this.currentContext.currentFile.content}\n\`\`\`\n\n`;
    
    // Add selection if exists
    if (this.currentContext.currentFile.selection) {
      prompt += `Selected code:\n`;
      prompt += `\`\`\`\n${this.currentContext.currentFile.selection}\n\`\`\`\n\n`;
    }
    
    // Add related files (truncated)
    for (const file of this.currentContext.relatedFiles) {
      prompt += `Related file: ${file.path}\n`;
      prompt += `\`\`\`\n${file.content.substring(0, 500)}...\n\`\`\`\n\n`;
    }
    
    prompt += `User question: ${query}\n\n`;
    prompt += `Please provide a helpful response focused on the code context.`;
    
    return prompt;
  }
}
```

#### Model Routing for Code

**Strategy:** Different models for different tasks

**Routing Rules:**

1. **GitHub Copilot** → Code completion, inline suggestions, quick fixes
2. **Claude Pro** → Complex refactoring, architecture questions, code review
3. **Local LLM** → Quick explanations when RAG confidence high

**Query Classification:**

```typescript
function classifyCodeQuery(query: string): 'completion' | 'refactoring' | 'explanation' | 'debugging' {
  const lower = query.toLowerCase();
  
  if (lower.includes('complete') || lower.includes('suggest')) {
    return 'completion';
  } else if (lower.includes('refactor') || lower.includes('redesign') || 
             lower.includes('architecture')) {
    return 'refactoring';
  } else if (lower.includes('explain') || lower.includes('how does') || 
             lower.includes('what is')) {
    return 'explanation';
  } else if (lower.includes('bug') || lower.includes('error') || 
             lower.includes('fix')) {
    return 'debugging';
  }
  
  return 'explanation'; // Default
}

async function routeCodeQuery(query: string, context: CodeContext): Promise<string> {
  const type = classifyCodeQuery(query);
  
  switch (type) {
    case 'completion':
      return await copilot.complete(context);
    
    case 'refactoring':
      return await claudePro.refactor(query, context);
    
    case 'explanation':
      // Try local first (Phase 11 routing)
      const router = new IntelligentRouter();
      return await router.route_query(query);
    
    case 'debugging':
      return await claudePro.debug(query, context);
  }
}
```

#### RAG-Powered Code Search

**Features:**
- Semantic search across:
  - GitHub repos (if connected via Phase 7)
  - Local project files
  - Code snippets in notes (Phase 16)
- Search by natural language ("functions that sort arrays")
- Search by code pattern (similar implementations)

**UI:**

```
┌─────────────────────────────────────────────────────────┐
│ Code Search                                    [⚙]      │
├─────────────────────────────────────────────────────────┤
│ 🔍 [functions that handle user authentication____]      │
│                                                         │
│ Filters: [Language: Any ▼] [Domain: All ▼]             │
├─────────────────────────────────────────────────────────┤
│ GitHub Repos (2)                                        │
│ 📄 polly-app/src/auth.ts:45                            │
│    function authenticateUser(token: string) {          │
│    Relevance: ●●●●○ 85%                                │
│    [Open] [Copy]                                        │
│                                                         │
│ 📄 utils-lib/src/security.ts:12                        │
│    export async function validateToken(...) {          │
│    Relevance: ●●●○○ 72%                                │
│    [Open] [Copy]                                        │
│                                                         │
│ Local Files (1)                                         │
│ 📄 ./src/middleware/auth.ts:8                          │
│    const checkAuth = (req, res, next) => {             │
│    Relevance: ●●●○○ 68%                                │
│    [Open] [Copy]                                        │
│                                                         │
│ Notes (1)                                               │
│ 📄 04-Code/jwt-authentication.md                       │
│    ```javascript                                        │
│    function verifyJWT(token) {...}                     │
│    ```                                                  │
│    Relevance: ●●○○○ 55%                                │
│    [Open Note]                                          │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```typescript
class CodeSearch {
  async search(query: string, filters?: SearchFilters): Promise<CodeSearchResult[]> {
    const results: CodeSearchResult[] = [];
    
    // 1. Search GitHub repos (if connected)
    if (await hasGitHubIntegration()) {
      const githubResults = await this.searchGitHub(query, filters);
      results.push(...githubResults);
    }
    
    // 2. Search local project files
    const localResults = await this.searchLocal(query, filters);
    results.push(...localResults);
    
    // 3. Search code snippets in notes
    const noteResults = await this.searchNotes(query, filters);
    results.push(...noteResults);
    
    // 4. Rank by relevance (using RAG embeddings)
    return this.rankResults(results, query);
  }
  
  private async searchLocal(query: string, filters?: SearchFilters): Promise<CodeSearchResult[]> {
    const projectFiles = await this.findCodeFiles(filters);
    const results: CodeSearchResult[] = [];
    
    for (const file of projectFiles) {
      const content = await fs.promises.readFile(file, 'utf-8');
      const matches = this.findMatchingFunctions(content, query);
      
      for (const match of matches) {
        results.push({
          source: 'local',
          path: file,
          lineNumber: match.line,
          snippet: match.code,
          relevance: 0 // Will be scored later
        });
      }
    }
    
    return results;
  }
  
  private async rankResults(results: CodeSearchResult[], query: string): Promise<CodeSearchResult[]> {
    // Use RAG embeddings to score relevance
    const queryEmbedding = await getEmbedding(query);
    
    for (const result of results) {
      const snippetEmbedding = await getEmbedding(result.snippet);
      result.relevance = cosineSimilarity(queryEmbedding, snippetEmbedding);
    }
    
    return results.sort((a, b) => b.relevance - a.relevance);
  }
}
```

#### Language/Library Support via Context7

**Built-in Languages:** Python, JS, TS, C, C++, C#, Lua, Rust, Go

**Extended Support via Context7:**
- React documentation
- Django documentation
- Node.js API
- Tokio (Rust async)
- Standard libraries for each language

**UI (Documentation Manager):**

```
┌─────────────────────────────────────────────────────────┐
│ Documentation & Language Support            [Settings]  │
├─────────────────────────────────────────────────────────┤
│ Active Documentation:                                    │
│ ☑ Python Standard Library                               │
│ ☑ JavaScript (ES6+)                                     │
│ ☑ React 18                                              │
│ ☐ Django 4.2                     [Download] [Activate]  │
│ ☐ Node.js 20 API                 [Download] [Activate]  │
│                                                         │
│ Available to Download:                                  │
│ • Vue 3                                                 │
│ • Express.js                                            │
│ • Tokio (Rust)                                          │
│ • NumPy                                                 │
│ • Pandas                                                │
│ [Browse More...]                                        │
└─────────────────────────────────────────────────────────┘
```

**Implementation:**

```typescript
class DocumentationManager {
  private activeDocsDir: string;
  
  constructor() {
    this.activeDocsDir = path.join(os.homedir(), '.polly', 'docs');
  }
  
  async downloadDocs(library: string): Promise<void> {
    // Use Context7 or similar to download and index documentation
    const docsUrl = this.getDocsUrl(library);
    
    // Download
    const content = await this.fetchDocs(docsUrl);
    
    // Parse and store
    const docsPath = path.join(this.activeDocsDir, library);
    await fs.promises.mkdir(docsPath, { recursive: true });
    await fs.promises.writeFile(
      path.join(docsPath, 'index.json'),
      JSON.stringify(content)
    );
    
    // Trigger RAG indexing
    await triggerRAGIndexing(docsPath);
  }
  
  async activateDocs(library: string): Promise<void> {
    // Mark as active for context inclusion
    const config = await this.loadConfig();
    config.activeDocs.push(library);
    await this.saveConfig(config);
  }
  
  async deactivateDocs(library: string): Promise<void> {
    const config = await this.loadConfig();
    config.activeDocs = config.activeDocs.filter(d => d !== library);
    await this.saveConfig(config);
  }
  
  getActiveDocs(): string[] {
    const config = this.loadConfig();
    return config.activeDocs;
  }
}
```

---

### Week 3: Advanced Features (5-7 days)

#### Code Actions (Right-Click Menu)

**Features:**

1. **"Explain this code"**
   - Sends selection to Polly chat
   - Uses Phase 11 routing
   - Shows explanation in chat panel

2. **"Find similar patterns"**
   - Searches Phase 13 learned patterns
   - Searches RAG for similar code
   - Shows results in sidebar

3. **"Refactor using mental model [X]"**
   - Lists Phase 14 mental models
   - User selects (e.g., SOLID, Functional Programming)
   - Sends to Claude for refactoring
   - Shows diff, user can accept/reject

4. **"Save as note"**
   - Generates note from code + explanation
   - Includes code block with syntax highlighting
   - Suggests domain (likely "Code" or "Patterns")
   - Opens in Phase 16 draft for review

**UI (Context Menu):**

```
Right-click on selected code:

┌─────────────────────────────────┐
│ Copy                            │
│ Cut                             │
│ Paste                           │
├─────────────────────────────────┤
│ Polly Actions:                  │
│ ✨ Explain this code            │
│ 🔍 Find similar patterns        │
│ 🔄 Refactor with...          ▶  │
│ 💾 Save as note                 │
├─────────────────────────────────┤
│ Source Control:                 │
│ Stage This Hunk                 │
│ Revert This Hunk                │
└─────────────────────────────────┘

Hover "Refactor with...":
┌─────────────────────────────────┐
│ Mental Models:                  │
│ • SOLID Principles              │
│ • Functional Programming        │
│ • Design Patterns               │
│ • Test-Driven Development       │
│ • Domain-Driven Design          │
└─────────────────────────────────┘
```

**Implementation:**

```typescript
class CodeActions {
  private editor: CodeEditor;
  private chatPanel: CodeChatPanel;
  
  registerActions() {
    this.editor.addAction({
      id: 'polly.explainCode',
      label: 'Explain this code',
      contextMenuGroupId: 'polly',
      contextMenuOrder: 1,
      run: async (editor) => {
        const selection = editor.getModel().getValueInRange(editor.getSelection());
        await this.explainCode(selection);
      }
    });
    
    this.editor.addAction({
      id: 'polly.findSimilar',
      label: 'Find similar patterns',
      contextMenuGroupId: 'polly',
      contextMenuOrder: 2,
      run: async (editor) => {
        const selection = editor.getModel().getValueInRange(editor.getSelection());
        await this.findSimilar(selection);
      }
    });
    
    this.editor.addAction({
      id: 'polly.saveAsNote',
      label: 'Save as note',
      contextMenuGroupId: 'polly',
      contextMenuOrder: 4,
      run: async (editor) => {
        const selection = editor.getModel().getValueInRange(editor.getSelection());
        await this.saveAsNote(selection);
      }
    });
  }
  
  private async explainCode(code: string) {
    const query = `Explain this code:\n\n\`\`\`\n${code}\n\`\`\``;
    await this.chatPanel.sendQuery(query);
    this.chatPanel.show();
  }
  
  private async findSimilar(code: string) {
    // Search Phase 13 patterns
    const patterns = await searchPatterns(code);
    
    // Search RAG
    const codeResults = await searchCodeInRAG(code);
    
    // Show results
    showSimilarCodePanel(patterns, codeResults);
  }
  
  private async saveAsNote(code: string) {
    // Generate explanation
    const explanation = await this.chatPanel.sendQuery(
      `Explain this code briefly:\n\n\`\`\`\n${code}\n\`\`\``
    );
    
    // Create note content
    const noteContent = `# ${this.suggestTitle(code)}

${explanation}

## Code

\`\`\`${this.detectLanguage()}
${code}
\`\`\`

## Context

File: ${this.editor.getCurrentFile()}
Created: ${new Date().toISOString()}
`;
    
    // Suggest domain and tags
    const domains = await getDomains();
    const suggestedDomain = suggest_domain_for_note(noteContent, '', domains);
    const suggestedTags = suggest_tags_for_note(noteContent, domains);
    
    // Open note creation dialog
    showCreateNoteDialog({
      content: noteContent,
      domain: suggestedDomain,
      tags: suggestedTags
    });
  }
}
```

#### Multi-File Context

**Feature:** Auto-include related files in chat context

**How it works:**
1. User is editing `main.ts`
2. Phase 12 graph shows `main.ts` imports `config.ts` and `utils.ts`
3. These files automatically included in context (up to token limit)
4. User sees which files are included
5. User can manually add/remove files

**UI (Context Viewer):**

```
┌─────────────────────────────────────────┐
│ Context: 3 files, 450 lines    [Edit]  │
├─────────────────────────────────────────┤
│ ✓ main.ts (current)          150 lines │
│ ✓ config.ts (imports)        100 lines │
│ ✓ utils.ts (imports)         200 lines │
├─────────────────────────────────────────┤
│ Available to add:                       │
│ □ api.ts (imported by utils)           │
│ □ types.ts (referenced)                │
│ [+ Add file manually...]                │
└─────────────────────────────────────────┘
```

**Implementation:**

```typescript
class MultiFileContext {
  private maxTokens = 8000; // Reserve 8k tokens for context
  private includedFiles: Map<string, string> = new Map();
  
  async buildContext(currentFile: string): Promise<FileContext[]> {
    this.includedFiles.clear();
    
    // Always include current file
    this.addFile(currentFile);
    
    // Get related files from knowledge graph
    const graph = await getKnowledgeGraph();
    const relatedFiles = graph.getRelatedFiles(currentFile);
    
    // Sort by relevance
    const sorted = relatedFiles.sort((a, b) => b.relevance - a.relevance);
    
    // Add files until token limit reached
    for (const file of sorted) {
      if (this.getCurrentTokenCount() + this.estimateTokens(file) > this.maxTokens) {
        break;
      }
      this.addFile(file.path);
    }
    
    return Array.from(this.includedFiles.entries()).map(([path, content]) => ({
      path,
      content,
      tokens: this.estimateTokens(content)
    }));
  }
  
  private addFile(filePath: string) {
    if (this.includedFiles.has(filePath)) return;
    
    const content = fs.readFileSync(filePath, 'utf-8');
    this.includedFiles.set(filePath, content);
  }
  
  private getCurrentTokenCount(): number {
    let total = 0;
    for (const content of this.includedFiles.values()) {
      total += this.estimateTokens(content);
    }
    return total;
  }
  
  private estimateTokens(text: string): number {
    // Rough estimate: 1 token ≈ 4 characters
    return Math.ceil(text.length / 4);
  }
}
```

#### Pattern-Aware Suggestions

**Feature:** As user types, suggest code patterns from Phase 13

**How it works:**
1. User starts typing a function
2. Phase 13 recognizes similar patterns in their code history
3. Suggest completion based on user's style
4. Show confidence score
5. Tab to accept, Esc to dismiss

**UI (Inline Suggestion):**

```
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);  ← Ghost text
}
                                                            ↑ Pattern: 85%
```

**Implementation:**

```typescript
class PatternSuggestions {
  private patternDb: PatternDatabase;
  
  async getSuggestion(partialCode: string, language: string): Promise<Suggestion | null> {
    // Search Phase 13 learned patterns
    const matchingPatterns = await this.patternDb.search({
      language,
      partialCode,
      minConfidence: 0.6
    });
    
    if (matchingPatterns.length === 0) return null;
    
    // Get best match
    const bestPattern = matchingPatterns[0];
    
    // Generate completion
    const completion = this.generateCompletion(partialCode, bestPattern);
    
    return {
      text: completion,
      confidence: bestPattern.confidence,
      pattern: bestPattern.name
    };
  }
  
  setupInlineCompletions() {
    monaco.languages.registerInlineCompletionsProvider('*', {
      provideInlineCompletions: async (model, position, context, token) => {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: Math.max(1, position.lineNumber - 5),
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column
        });
        
        const language = model.getLanguageId();
        const suggestion = await this.getSuggestion(textUntilPosition, language);
        
        if (!suggestion) return { items: [] };
        
        return {
          items: [{
            insertText: suggestion.text,
            range: new monaco.Range(
              position.lineNumber, 
              position.column, 
              position.lineNumber, 
              position.column
            ),
            command: {
              id: 'polly.acceptedPatternSuggestion',
              title: 'Record Pattern Usage'
            }
          }]
        };
      },
      
      freeInlineCompletions: () => {}
    });
  }
}
```

#### Code → Note Creation

**Feature:** Select code and create a comprehensive note

**Flow:**
1. Select code
2. Right-click → "Create note from code"
3. Polly generates:
   - Explanation (what it does, how it works)
   - Pattern analysis (using Phase 13)
   - Domain suggestion (likely "Code" or "Patterns")
   - Tags (language, framework)
   - Code block with syntax highlighting
4. Opens in Phase 16 editor for review/editing
5. User saves to domain folder

**Generated Note Format:**

```markdown
---
title: Array Reduce Pattern
domain: patterns
tags: [javascript, array, functional]
created: 2026-01-23T15:30:00Z
source: src/utils/calculations.ts:45-47
---

# Array Reduce Pattern

## Explanation

This code uses JavaScript's `reduce` method to calculate the sum of all
item prices in an array. It's a functional programming approach that
avoids explicit loops.

## Pattern: Reduce Accumulator

**Category:** Data Transformation  
**Confidence:** 92%

This follows the "reduce accumulator" pattern commonly used in your
codebase for aggregating values from arrays.

## Code

```javascript
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

## Key Concepts

- **Accumulator:** `sum` accumulates the total
- **Initial value:** `0` is the starting point
- **Reducer function:** `(sum, item) => sum + item.price`

## Related Patterns

- Map-Reduce
- Fold (Haskell equivalent)
- Aggregate functions

## Usage Context

Found in: `src/utils/calculations.ts`  
Used for: Shopping cart total calculation  
Part of: Order processing system
```

**Implementation:**

```typescript
async function createNoteFromCode(
  code: string,
  filePath: string,
  lineStart: number,
  lineEnd: number
): Promise<void> {
  // 1. Generate explanation
  const explanation = await explainCode(code);
  
  // 2. Analyze patterns (Phase 13)
  const patterns = await analyzePatterns(code);
  
  // 3. Detect language
  const language = detectLanguageFromPath(filePath);
  
  // 4. Generate note content
  const noteContent = `---
title: ${suggestTitle(code)}
domain: ${suggestDomain(code)}
tags: ${suggestTags(code, language)}
created: ${new Date().toISOString()}
source: ${filePath}:${lineStart}-${lineEnd}
---

# ${suggestTitle(code)}

## Explanation

${explanation}

${patterns.length > 0 ? `
## Pattern: ${patterns[0].name}

**Category:** ${patterns[0].category}  
**Confidence:** ${Math.round(patterns[0].confidence * 100)}%

${patterns[0].description}
` : ''}

## Code

\`\`\`${language}
${code}
\`\`\`

## Key Concepts

${extractKeyConcepts(explanation)}

## Related Patterns

${getRelatedPatterns(patterns)}

## Usage Context

Found in: \`${filePath}\`  
${getAdditionalContext(filePath)}
`;
  
  // 5. Open in note editor
  openNoteEditor(noteContent);
}
```

---

## UI Layout

### Full Application Layout with Code Tab

```
┌─────────────────────────────────────────────────────────┐
│ [Notes] [Graph] [Code] [Knowledge] [Settings]          │ ← Tabs
├──────────┬──────────────────────────┬───────────────────┤
│  Files   │  Editor (Monaco)         │   Chat Panel      │
│  (tree)  │  - Tabs: main.ts, ...    │   (Polly)         │
│          │  - Syntax highlighting   │                   │
│  📁 src/ │  - IntelliSense          │  Context: 3 files │
│    📄 m..M│                          │  Model: Claude    │
│          │  function main() {       │                   │
│  [Git]   │    const router = ...    │  You: How can I   │
│  Changes │                          │  refactor this?   │
│  3 files │  [Problems] [Output]     │                   │
│          │                          │  Polly: ...       │
├──────────┴──────────────────────────┤                   │
│  Terminal (xterm.js)                │  [Apply]          │
│  $ npm run build                    │                   │
│  ✓ built in 3.45s                   │  Quick Actions:   │
│  $█                                  │  • Explain code   │
└──────────────────────────────────────┴───────────────────┘
```

### Responsive Panels

- **Files panel:** Collapsible, resizable
- **Editor:** Multi-tab, split view support
- **Chat panel:** Collapsible, detachable
- **Terminal:** Collapsible, split support
- **Git panel:** Toggle with Files panel

---

## What NOT to Build

**Use External IDE via Phase 15 (MCP) for:**

❌ **Full LSP Servers**
- Complex language servers (Pylance, TypeScript server)
- Advanced type checking
- Complex refactoring (extract method, rename symbol across files)

❌ **Debugger**
- Breakpoints
- Step-through debugging
- Variable inspection
- Call stack navigation

❌ **Extension Marketplace**
- Plugin system
- Community extensions
- Custom themes beyond built-in

❌ **Advanced Refactoring**
- Automated refactoring tools (beyond LLM)
- Safe renames with preview
- Extract to module/file

❌ **Performance Tools**
- Profiling
- Benchmarking
- Memory analysis

**Strategy:**  
Polly provides 80% of daily coding needs. For the remaining 20% (debugging, complex refactoring), users seamlessly switch to their preferred IDE which has full access to Polly's context via MCP (Phase 15).

---

## Integration with Phase 15 (MCP Server)

**MCP exposes Polly's capabilities to external tools:**

External IDE (VS Code, Cursor, etc.) can:
- Query Polly's knowledge base
- Access conversation history
- Search notes and patterns
- View knowledge graph
- Get AI suggestions

**Bi-directional:**
- Polly can also request services from external IDE
- Example: "Open in VS Code debugger"

**Implementation:**

```typescript
// MCP Server exposes these endpoints
class PollyMCPServer {
  // External IDE can query Polly
  async searchKnowledge(query: string): Promise<SearchResult[]> {
    return await ragSearch(query);
  }
  
  async getContext(filePath: string): Promise<FileContext> {
    return await buildContext(filePath);
  }
  
  async askPolly(query: string, context: any): Promise<string> {
    return await router.route_query(query);
  }
  
  // Polly can request IDE services
  async openInDebugger(filePath: string, line: number) {
    // Send to external IDE via MCP
    await mcp.request('ide.debug', { filePath, line });
  }
}
```

---

## Integration Points

### Phase 1.5: Domain Configuration
- Code → Note suggests domain based on content
- Uses auto-tag rules for categorization

### Phase 2: RAG System
- Code search uses RAG embeddings
- Documentation indexed via RAG
- Semantic code search

### Phase 11: Multi-Model + Intelligent Routing
- Chat uses intelligent routing
- Local vs cloud model selection
- Token budget management

### Phase 12: Knowledge Graph
- Related files from graph included in context
- Code files represented as nodes
- Navigate between code and notes

### Phase 13: Pattern Learning
- Pattern-aware suggestions
- "Find similar" uses learned patterns
- Track coding style over time

### Phase 14: Mental Models
- Refactor using mental models
- Apply design patterns
- Architecture recommendations

### Phase 15: MCP Server
- Expose Polly to external IDEs
- Bi-directional integration
- Seamless context sharing

### Phase 16: Native Notes
- Code → Note creation
- Save snippets as notes
- Reference notes from code

---

## Implementation Timeline

**Total Duration:** 3 weeks (15-21 days)

### Week 1: Core Editor (5-7 days)
- Days 1-2: Monaco editor integration, multi-file tabs
- Day 3: File tree with Git status
- Day 4: Integrated terminal (xterm.js)
- Days 5-7: Git operations UI (stage, commit, push, pull, diff)

**Acceptance criteria:**
- ✓ Can edit code in 9 languages
- ✓ File tree shows project structure
- ✓ Terminal works with multiple tabs
- ✓ Git operations function correctly

### Week 2: Polly Integration (5-7 days)
- Days 8-9: Chat panel with context awareness
- Day 10: Model routing for code queries
- Days 11-12: RAG-powered code search
- Days 13-14: Language/library support (Context7 integration)

**Acceptance criteria:**
- ✓ Chat panel shows file context
- ✓ Queries routed to appropriate model
- ✓ Code search finds relevant results
- ✓ Can download and activate documentation

### Week 3: Advanced Features (5-7 days)
- Days 15-16: Code actions (explain, find similar, refactor, save)
- Days 17-18: Multi-file context auto-inclusion
- Days 19-20: Pattern-aware suggestions
- Day 21: Testing, polish, documentation

**Acceptance criteria:**
- ✓ Right-click code actions work
- ✓ Related files auto-included in context
- ✓ Pattern suggestions appear as user types
- ✓ Code → Note creation works smoothly

---

## Success Criteria

Phase 17 is complete when:

1. **Core editing works:**
   - ✓ Can edit code in 9 languages with syntax highlighting
   - ✓ Multi-file tabs and navigation
   - ✓ Terminal integrated and functional

2. **Git integration works:**
   - ✓ Can view changes and stage/unstage
   - ✓ Can commit and push
   - ✓ Diff viewer shows changes clearly

3. **Polly integration works:**
   - ✓ Chat panel aware of code context
   - ✓ Queries answered with code understanding
   - ✓ Code search finds relevant results

4. **Advanced features work:**
   - ✓ Code actions (explain, refactor, save) function
   - ✓ Multi-file context auto-included
   - ✓ Pattern suggestions helpful

5. **User experience:**
   - ✓ UI responsive and intuitive
   - ✓ Switching between code and notes seamless
   - ✓ No jarring context switches
   - ✓ 80% of coding tasks possible in Polly

---

## Future Enhancements

### Phase 17b: Advanced IDE Features (2-3 weeks)

Potential future additions:

1. **Basic LSP Support:**
   - Go-to-definition
   - Find references
   - Hover for documentation

2. **Test Runner:**
   - Run tests in UI
   - Show pass/fail inline
   - Coverage visualization

3. **Code Formatting:**
   - Prettier integration
   - Language-specific formatters
   - Format on save

4. **Snippets:**
   - User-defined snippets
   - Share snippets via notes
   - Snippet variables

5. **Workspace Management:**
   - Multiple project folders
   - Workspace settings
   - Project templates

---

## Technical Notes

### Performance Considerations

- **Lazy loading:** Only load visible files in tree
- **Syntax highlighting:** Use Web Workers for large files
- **IntelliSense:** Debounce suggestions (300ms)
- **Pattern suggestions:** Cache recent patterns
- **Context building:** Limit to 5 files / 8k tokens

### Security

- **Terminal:** Sandboxed, limited to project directory by default
- **Git operations:** Validate all paths
- **Code execution:** Never auto-execute code without user consent

### Storage

```
~/.polly/
├── workspace/
│   ├── recent_projects.json
│   └── workspace_settings.json
├── docs/               # Downloaded documentation
│   ├── react/
│   ├── django/
│   └── tokio/
└── patterns/           # Phase 13 patterns
    └── patterns.json
```

---

## Dependencies

**Phase 17 depends on:**
- Phase 1.5: Domain Configuration
- Phase 2: RAG System
- Phase 11: Multi-Model + Intelligent Routing
- Phase 12: Knowledge Graph
- Phase 13: Pattern Learning
- Phase 14: Mental Models
- Phase 16: Native Notes

**Phase 17 enables:**
- Complete integrated development in Polly
- Seamless code-knowledge workflow
- 80% of coding without external tools

---

## References

- MASTER_ROADMAP.md - Overall project plan
- PHASE11_MULTI_MODEL_ENHANCED.md - Intelligent routing for code queries
- PHASE13_PATTERN_LEARNING.md - Pattern-aware suggestions
- PHASE15_MCP_SERVER.md - External IDE integration
- PHASE16_NATIVE_NOTES.md - Code → Note creation
- PHASE_STATUS_SUMMARY.md - Current implementation status

---

**End of Phase 17 specification**

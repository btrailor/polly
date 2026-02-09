# Phase 17: VSCode Fork Integration Strategy

**Status:** 📋 Planned  
**Purpose:** Detailed technical strategy for integrating Polly features into VSCode fork  
**Audience:** Developers implementing Phase 17

---

## Overview

This document provides a detailed technical strategy for forking VSCodium and integrating Polly-specific features. The goal is to **minimize core modifications** while **maximizing integration depth** for Polly's unique features (RAG, personas, domains, ribbon navigation).

---

## Architecture Principles

### Core Principles

1. **Minimal Core Modifications:** Only modify VSCode core when absolutely necessary
2. **Extension API First:** Use VSCode's extension API for most Polly features
3. **Isolation:** Keep Polly-specific code in separate modules
4. **Documentation:** Document all core modifications clearly
5. **Maintainability:** Design for easy upstream merges

### Modification Levels

**Level 1: Extension API (Preferred)**
- No core modifications
- Uses VSCode's extension system
- Easy to maintain, no merge conflicts
- Examples: RAG panel, persona switcher, domain filters

**Level 2: Core Modifications (When Necessary)**
- Minimal changes to VSCode core
- Only for features that can't use extension API
- Examples: Ribbon navigation (replace activity bar), deep RAG integration

**Level 3: Avoid**
- Major architectural changes
- Editor core modifications (Monaco internals)
- Terminal/debug/git core changes (use as-is)

---

## Fork Structure

### Repository Organization

```
polly-code/
├── .vscode/                    # VSCode/VSCodium source (minimal changes)
│   ├── src/vs/
│   │   ├── workbench/         # Workbench (ribbon modification here)
│   │   ├── editor/           # Editor core (don't modify)
│   │   └── ...
│   └── ...
├── polly/                      # Polly-specific code (isolated)
│   ├── ribbon/                # Ribbon navigation component
│   │   ├── ribbonPart.ts      # Ribbon workbench part
│   │   ├── ribbonView.ts      # Ribbon view implementation
│   │   └── ribbon.css        # Ribbon styling
│   ├── chat/                  # Chat panel integration
│   │   ├── chatExtension.ts   # Extension entry point
│   │   └── chatView.ts        # Chat view implementation
│   ├── rag/                   # RAG integration
│   │   ├── ragExtension.ts   # RAG extension
│   │   └── ragPanel.ts        # RAG results panel
│   ├── personas/              # Persona system
│   │   ├── personaExtension.ts
│   │   └── personaSwitcher.ts
│   └── domains/               # Domain features
│       ├── domainExtension.ts
│       └── domainFilters.ts
├── extensions/                # Extension-based features
│   ├── polly-chat/           # Chat panel extension
│   ├── polly-rag/            # RAG panel extension
│   ├── polly-personas/       # Persona switcher extension
│   ├── polly-domains/        # Domain features extension
│   └── polly-theme/          # Polly theme extension
└── docs/                      # Documentation
    ├── build.md              # Build instructions
    ├── integration.md        # Integration notes
    └── modifications.md      # Core modifications log
```

---

## Core Modifications

### 1. Ribbon Navigation (Level 2: Core Modification)

**Goal:** Replace VSCode's activity bar with Polly's ribbon navigation

**Files to Modify:**
- `src/vs/workbench/browser/parts/activitybar/activitybarPart.ts`
- `src/vs/workbench/browser/workbench.html`
- `src/vs/workbench/browser/workbench.ts`

**Implementation:**

1. **Create Ribbon Part:**
   ```typescript
   // polly/ribbon/ribbonPart.ts
   export class RibbonPart extends Disposable implements IWorkbenchContribution {
     private ribbonContainer: HTMLElement;
     
     constructor() {
       // Initialize ribbon component
       // Port from electron-app/src/renderer/styles/ribbon.css
     }
     
     // Replace activity bar with ribbon
   }
   ```

2. **Modify Workbench:**
   ```typescript
   // src/vs/workbench/browser/workbench.ts
   // Replace activity bar registration with ribbon
   registerWorkbenchContribution(RibbonPart, LifecyclePhase.Starting);
   ```

3. **Update Template:**
   ```html
   <!-- src/vs/workbench/browser/workbench.html -->
   <!-- Replace activity bar div with ribbon div -->
   <div class="ribbon-container" id="ribbon"></div>
   ```

**Integration Points:**
- Maintain VSCode's panel system (just change navigation)
- Keep all views accessible via ribbon icons
- Preserve keyboard shortcuts
- Maintain panel collapsing/expanding

**Risk:** Medium (core workbench change, but isolated)

---

### 2. Theme Customization (Level 1: Extension API)

**Goal:** Apply Polly design system to VSCode theme

**Implementation:**

1. **Create Theme Extension:**
   ```typescript
   // extensions/polly-theme/src/extension.ts
   export function activate(context: vscode.ExtensionContext) {
     // Register Polly theme
     vscode.workspace.getConfiguration().update(
       'workbench.colorTheme',
       'Polly Dark',
       vscode.ConfigurationTarget.Global
     );
   }
   ```

2. **Define Theme:**
   ```json
   // extensions/polly-theme/themes/polly-dark.json
   {
     "name": "Polly Dark",
     "colors": {
       "editor.background": "#1a1a1a",
       "editor.foreground": "#e0e0e0",
       // Apply Polly color system from DESIGN_SYSTEM.md
     }
   }
   ```

**Integration Points:**
- Use VSCode's theme extension API
- Apply Polly colors from DESIGN_SYSTEM.md
- Match typography (Inter for UI, JetBrains Mono for code)
- Add glitch effects via CSS (if possible)

**Risk:** Low (standard extension, no core changes)

---

## Extension-Based Features

### 3. Chat Panel (Level 1: Extension API)

**Goal:** Add Polly chat panel to right sidebar

**Implementation:**

1. **Create Chat Extension:**
   ```typescript
   // extensions/polly-chat/src/extension.ts
   export function activate(context: vscode.ExtensionContext) {
     // Create chat webview
     const chatProvider = new ChatProvider(context.extensionUri);
     
     // Register chat view
     vscode.window.registerTreeDataProvider('pollyChat', chatProvider);
     
     // Add to sidebar
     vscode.window.createTreeView('pollyChat', {
       treeDataProvider: chatProvider,
       showCollapseAll: false
     });
   }
   ```

2. **Chat Provider:**
   ```typescript
   // extensions/polly-chat/src/chatProvider.ts
   class ChatProvider implements vscode.TreeDataProvider<ChatMessage> {
     // Connect to Polly backend API
     // Port chat UI from electron-app
     // Handle message sending/receiving
   }
   ```

**Integration Points:**
- Use VSCode's webview API for chat UI
- Connect to Polly server (http://localhost:8000/api/chat)
- Port chat component from electron-app
- Integrate with ribbon (add chat icon)

**Risk:** Low (extension API, no core changes)

---

### 4. RAG Integration (Level 1: Extension API + Level 2: Hooks)

**Goal:** Integrate RAG system for code context

**Implementation:**

1. **RAG Panel Extension:**
   ```typescript
   // extensions/polly-rag/src/extension.ts
   export function activate(context: vscode.ExtensionContext) {
     // Create RAG results panel
     const ragProvider = new RAGProvider(context.extensionUri);
     
     vscode.window.createTreeView('pollyRAG', {
       treeDataProvider: ragProvider
     });
     
     // Register commands for RAG queries
     vscode.commands.registerCommand('polly.rag.query', () => {
       // Query RAG system with current file/selection context
     });
   }
   ```

2. **Editor Integration:**
   ```typescript
   // extensions/polly-rag/src/editorIntegration.ts
   // Hook into editor events
   vscode.window.onDidChangeActiveTextEditor((editor) => {
     if (editor) {
       // Query RAG with file context
       queryRAG(editor.document.uri);
     }
   });
   
   vscode.window.onDidChangeTextEditorSelection((event) => {
     // Query RAG with selection context
     queryRAG(event.textEditor.document.uri, event.selections);
   });
   ```

**Integration Points:**
- Use extension API for panel
- Hook into editor events for context
- Connect to Polly RAG backend
- Display results in dedicated panel

**Risk:** Low-Medium (mostly extension API, some editor hooks)

---

### 5. Persona System (Level 1: Extension API)

**Goal:** Integrate Polly persona switcher

**Implementation:**

1. **Persona Extension:**
   ```typescript
   // extensions/polly-personas/src/extension.ts
   export function activate(context: vscode.ExtensionContext) {
     // Register persona switcher command
     vscode.commands.registerCommand('polly.personas.switch', async () => {
       // Show persona selection dialog
       const persona = await showPersonaDialog();
       if (persona) {
         // Switch persona
         await switchPersona(persona);
       }
     });
     
     // Add to status bar
     const statusBarItem = vscode.window.createStatusBarItem(
       vscode.StatusBarAlignment.Right,
       100
     );
     statusBarItem.text = '$(person) Architect';
     statusBarItem.command = 'polly.personas.switch';
     statusBarItem.show();
   }
   ```

2. **Persona Integration:**
   ```typescript
   // Connect to Polly persona system
   // Use persona context in chat/RAG queries
   // Update status bar with current persona
   ```

**Integration Points:**
- Command palette integration
- Status bar indicator
- Chat/RAG context integration
- Settings sync with Polly profiles

**Risk:** Low (extension API, no core changes)

---

### 6. Domain Features (Level 1: Extension API)

**Goal:** Add domain-aware file tree and filters

**Implementation:**

1. **Domain Extension:**
   ```typescript
   // extensions/polly-domains/src/extension.ts
   export function activate(context: vscode.ExtensionContext) {
     // Extend file explorer with domain filters
     vscode.commands.registerCommand('polly.domains.filter', async () => {
       const domain = await showDomainPicker();
       if (domain) {
         // Filter file tree by domain
         filterFileTreeByDomain(domain);
       }
     });
     
     // Add domain badges to file tree
     // Show domain info in file explorer
   }
   ```

2. **File Tree Integration:**
   ```typescript
   // Extend VSCode's file explorer
   // Add domain metadata to file items
   // Filter by domain
   // Show domain badges
   ```

**Integration Points:**
- Extend file explorer API
- Domain metadata integration
- Filter UI in file tree
- Connect to Polly domain system

**Risk:** Low (extension API, file explorer extension points)

---

## Integration Architecture

### Backend Integration

**Polly Server Connection:**
```typescript
// polly/core/apiClient.ts
export class PollyAPIClient {
  private baseURL = 'http://localhost:8000';
  
  async chat(message: string, context?: ChatContext): Promise<ChatResponse> {
    // Connect to Polly chat API
  }
  
  async rag(query: string, context: RAGContext): Promise<RAGResults> {
    // Connect to Polly RAG API
  }
  
  async getPersonas(): Promise<Persona[]> {
    // Get available personas
  }
  
  async getDomains(): Promise<Domain[]> {
    // Get available domains
  }
}
```

**Integration Points:**
- All extensions connect to Polly backend
- Use existing Polly API (no backend changes needed)
- Handle connection errors gracefully
- Cache responses where appropriate

---

### Frontend Integration

**Component Porting:**
- Port ribbon CSS/HTML from `electron-app/src/renderer/styles/ribbon.css`
- Port chat UI from `electron-app/src/renderer/` chat components
- Use Lucide icons (same as Polly)
- Match Polly design system

**UI Consistency:**
- Ribbon matches Polly ribbon
- Chat matches Polly chat
- Theme matches Polly design system
- Icons match Polly icon set

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Tasks:**
1. Fork VSCodium
2. Set up build environment
3. Create fork structure
4. Document base state

**Deliverables:**
- Working VSCodium fork
- Build documentation
- Repository structure

---

### Phase 2: Ribbon Integration (Week 3-4)

**Tasks:**
1. Study activity bar implementation
2. Create ribbon component
3. Replace activity bar
4. Test integration

**Deliverables:**
- Ribbon navigation working
- Activity bar replaced
- All views accessible

---

### Phase 3: Theme & Chat (Week 5-6)

**Tasks:**
1. Create Polly theme extension
2. Create chat panel extension
3. Integrate with ribbon
4. Test functionality

**Deliverables:**
- Polly theme applied
- Chat panel working
- Basic integration complete

---

### Phase 4: Polly Features (Week 7-10)

**Tasks:**
1. RAG integration
2. Persona system
3. Domain features
4. Profile integration

**Deliverables:**
- All Polly features integrated
- Full functionality working
- Ready for testing

---

### Phase 5: Polish & Testing (Week 11-12)

**Tasks:**
1. UI polish
2. Animation refinement
3. Comprehensive testing
4. Documentation

**Deliverables:**
- Production-ready Polly Code
- Complete documentation
- User testing complete

---

## Risk Mitigation

### Risk 1: Core Modification Complexity

**Mitigation:**
- Keep core modifications minimal
- Use extension API where possible
- Document all core changes
- Test thoroughly after each change

### Risk 2: Merge Conflicts

**Mitigation:**
- Isolate Polly code in separate modules
- Minimize core modifications
- Use extension API for most features
- Document integration points clearly

### Risk 3: Integration Challenges

**Mitigation:**
- Study VSCode architecture first
- Use extension API extensively
- Test integration points early
- Have fallback plans

### Risk 4: Performance Issues

**Mitigation:**
- Profile extension performance
- Optimize API calls
- Cache where appropriate
- Test with large codebases

---

## Testing Strategy

### Unit Tests

**Polly Components:**
- Ribbon component tests
- Chat provider tests
- RAG integration tests
- Persona system tests

### Integration Tests

**VSCode Integration:**
- Ribbon + panel system
- Chat + backend API
- RAG + editor events
- Theme application

### E2E Tests

**User Workflows:**
- Open file, edit, save
- Use chat panel
- Query RAG system
- Switch personas
- Filter by domain

---

## Documentation Requirements

### Code Documentation

**All Core Modifications:**
- Why modification was needed
- What was changed
- How it integrates
- Testing performed

### User Documentation

**Polly Code Features:**
- Ribbon navigation guide
- Chat panel usage
- RAG integration guide
- Persona system guide
- Domain features guide

### Developer Documentation

**Fork Maintenance:**
- Build instructions
- Integration notes
- Extension development guide
- Merge process documentation

---

## Success Criteria

### Technical

- ✅ Fork builds and runs
- ✅ Ribbon navigation works
- ✅ All Polly features integrated
- ✅ Theme applied correctly
- ✅ No major regressions

### Functional

- ✅ Chat panel functional
- ✅ RAG integration working
- ✅ Persona system integrated
- ✅ Domain features working
- ✅ All VSCode features still work

### Quality

- ✅ UI matches Polly design system
- ✅ Performance acceptable
- ✅ No critical bugs
- ✅ Documentation complete

---

## Next Steps

1. ✅ **Strategy Complete:** This document
2. **Begin POC:** Follow PHASE17_POC_PLAN.md
3. **Evaluate Results:** Based on POC findings
4. **Proceed with Full Implementation:** If POC succeeds
5. **Maintain Fork:** Follow PHASE17_FORK_MAINTENANCE_STRATEGY.md

---

**Status:** Ready for POC implementation

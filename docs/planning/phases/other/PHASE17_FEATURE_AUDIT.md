# Phase 17: Feature Audit

**Date:** February 4, 2026  
**Purpose:** Review each feature and decide keep/remove/enhance/integrate  
**Status:** In Progress

---

## Feature Decision Matrix

### Core Features (Keep & Port)

#### 1. Dashboard
- **Status:** KEEP
- **Rationale:** Central hub for stats, quick actions, mental models status
- **VSCode Integration:** Tree view + webview for complex UI
- **Priority:** High

#### 2. Chat Interface
- **Status:** KEEP
- **Rationale:** Primary interaction method with Polly
- **VSCode Integration:** Panel (bottom) - always accessible
- **Priority:** Critical

#### 3. Knowledge Graph
- **Status:** KEEP
- **Rationale:** Core feature for understanding user's knowledge
- **VSCode Integration:** Tree view + webview for visualization
- **Priority:** High

#### 4. Notes
- **Status:** KEEP
- **Rationale:** Native notes system, Obsidian integration
- **VSCode Integration:** Tree view + webview for editor
- **Priority:** High

#### 5. Learning/Curricula
- **Status:** KEEP
- **Rationale:** Learning system with progress tracking
- **VSCode Integration:** Tree view + webview for curriculum details
- **Priority:** Medium

#### 6. Patterns
- **Status:** KEEP
- **Rationale:** Pattern learning and extraction
- **VSCode Integration:** Tree view + webview
- **Priority:** Medium

#### 7. Domains
- **Status:** KEEP
- **Rationale:** Domain management (Sigils, Signals, etc.)
- **VSCode Integration:** Tree view + settings integration
- **Priority:** Medium

#### 8. Settings
- **Status:** KEEP & ENHANCE
- **Rationale:** Configuration management
- **VSCode Integration:** Use VSCode settings UI pattern
- **Priority:** High

---

### Features to Enhance

#### 1. GitHub Integration
- **Current:** OAuth flow, token storage, backend connection, RAG indexing
- **Decision:** ENHANCE
- **Action:**
  - Remove OAuth UI (use VSCode native Git/GitHub)
  - Keep RAG indexing logic
  - Integrate with VSCode's Git extension
  - Add Polly RAG features to VSCode's GitHub integration
- **Priority:** Medium

#### 2. Codebase Indexing
- **Current:** Manual codebase path selection, indexing UI
- **Decision:** ENHANCE
- **Action:**
  - Remove manual path selection UI
  - Use VSCode workspace awareness (automatically index open workspace)
  - Enhance with Polly RAG features
  - Integrate with VSCode's file explorer
- **Priority:** High

#### 3. Search
- **Current:** Polly search functionality
- **Decision:** REVIEW
- **Action:**
  - VSCode has native search
  - Keep Polly RAG search if it adds value (semantic search)
  - Remove if redundant
- **Priority:** Low

---

### Features to Remove

#### 1. Calendar
- **Status:** REMOVE
- **Rationale:** Placeholder only, not implemented
- **Action:** Remove view, remove ribbon button

#### 2. Mail
- **Status:** REMOVE
- **Rationale:** Placeholder only, not implemented
- **Action:** Remove view, remove ribbon button

#### 3. Projects
- **Status:** REMOVE
- **Rationale:** Placeholder only, not implemented
- **Action:** Remove view, remove ribbon button

#### 4. VSCode BrowserView Integration
- **Status:** REMOVE
- **Rationale:** Replaced by full VSCode fork integration
- **Action:** Remove BrowserView code, IPC handlers

---

### Features to Review

#### 1. Mental Models Editor
- **Status:** REVIEW
- **Rationale:** Complex UI component
- **Decision:** KEEP - Port to VSCode webview
- **Priority:** Medium

#### 2. Template Gallery
- **Status:** REVIEW
- **Rationale:** UI component for templates
- **Decision:** KEEP - Port to VSCode webview
- **Priority:** Low

#### 3. Preview Modal
- **Status:** REVIEW
- **Rationale:** Modal for previews
- **Decision:** May use VSCode native modals instead
- **Priority:** Low

#### 4. Question Form
- **Status:** REVIEW
- **Rationale:** Form component
- **Decision:** May use VSCode native inputs
- **Priority:** Low

#### 5. Package Approval Dialog
- **Status:** REVIEW
- **Rationale:** Dialog for package approval
- **Decision:** Use VSCode native dialogs
- **Priority:** Low

---

## Feature Dependencies

### Python Backend APIs (All Keep):
- `/polly/query` - Core query endpoint
- `/polly/stats` - Statistics
- `/polly/notes/*` - Notes management
- `/polly/curricula/*` - Learning system
- `/polly/patterns/*` - Pattern management
- `/polly/domains/*` - Domain management
- `/persona/*` - Persona system
- `/polly/index` - Indexing
- `/polly/integrations/*` - Integrations (GitHub, Obsidian)

### Electron IPC Handlers (Review):
- Most IPC handlers will be replaced by VSCode extension API
- Keep only essential ones for Python backend management

---

## Migration Priority

### Phase 1 (Critical):
1. Chat Interface
2. Dashboard
3. Python Backend Integration

### Phase 2 (High):
4. Knowledge Graph
5. Notes
6. Settings

### Phase 3 (Medium):
7. Learning/Curricula
8. Patterns
9. Domains
10. GitHub Integration Enhancement
11. Codebase Indexing Enhancement

### Phase 4 (Low):
12. Mental Models Editor
13. Template Gallery
14. Other UI Components

---

## Next Steps

1. ✅ Complete feature audit
2. ⏳ Create UI placement specification
3. ⏳ Begin migration

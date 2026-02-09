# Phase 17 POC: Chat Panel Integration

**Status:** 📋 Planned  
**Purpose:** Detailed guide for adding Polly chat panel to VSCode fork

---

## Overview

This document provides detailed steps for integrating Polly's chat panel into the VSCode fork as a new panel type in the right sidebar.

---

## Integration Strategy

### Approach: Extension-Based (Preferred)

**Why Extension:**
- No core VSCode modifications needed
- Easier to maintain
- Can be updated independently
- Follows VSCode best practices

**If Extension API Insufficient:**
- May need minimal core modifications
- Document any core changes clearly

---

## Implementation Steps

### Step 1: Create Chat Extension

**Extension Structure:**

```
extensions/polly-chat/
├── package.json              # Extension manifest
├── src/
│   ├── extension.ts         # Extension entry point
│   ├── chatProvider.ts      # Chat view provider
│   └── chatView.ts          # Chat UI component
└── media/
    └── chat.css             # Chat styles
```

### Step 2: Register Chat View

**Extension Entry Point:**

```typescript
// extensions/polly-chat/src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
  // Register chat view
  const chatProvider = new ChatProvider(context.extensionUri);
  
  // Create tree view for chat
  const chatView = vscode.window.createTreeView('pollyChat', {
    treeDataProvider: chatProvider,
    showCollapseAll: false
  });
  
  context.subscriptions.push(chatView);
  
  // Register commands
  vscode.commands.registerCommand('polly.chat.send', (message) => {
    chatProvider.sendMessage(message);
  });
}
```

### Step 3: Create Chat Provider

**Chat Provider:**

```typescript
// extensions/polly-chat/src/chatProvider.ts
import * as vscode from 'vscode';

export class ChatProvider implements vscode.TreeDataProvider<ChatMessage> {
  private _onDidChangeTreeData = new vscode.EventEmitter<ChatMessage | undefined>();
  readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
  
  private messages: ChatMessage[] = [];
  
  constructor(private extensionUri: vscode.Uri) {}
  
  getTreeItem(element: ChatMessage): vscode.TreeItem {
    return element;
  }
  
  getChildren(element?: ChatMessage): ChatMessage[] {
    return this.messages;
  }
  
  async sendMessage(text: string) {
    // Send to Polly backend
    // Add message to list
    // Update UI
  }
}
```

### Step 4: Create Chat UI

**Webview Approach (More Flexible):**

```typescript
// Create webview panel for chat
const chatPanel = vscode.window.createWebviewPanel(
  'pollyChat',
  'Polly Chat',
  vscode.ViewColumn.Beside,
  {
    enableScripts: true,
    retainContextWhenHidden: true
  }
);

// Load chat HTML
chatPanel.webview.html = getChatWebviewContent(extensionUri);
```

**Chat HTML:**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    /* Chat styles matching Polly design */
  </style>
</head>
<body>
  <div id="chat-messages"></div>
  <div id="chat-input">
    <input type="text" id="message-input" />
    <button id="send-btn">Send</button>
  </div>
  <script>
    // Chat logic
    // Connect to Polly backend
  </script>
</body>
</html>
```

### Step 5: Connect to Polly Backend

**API Client:**

```typescript
// extensions/polly-chat/src/pollyApi.ts
export class PollyAPIClient {
  private baseURL = 'http://localhost:11436';
  
  async sendMessage(message: string, context?: ChatContext): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        context,
        conversation_id: this.currentConversationId
      })
    });
    
    return response.json();
  }
}
```

### Step 6: Add to Right Sidebar

**Option 1: As View Container**

```typescript
// Register as view container
vscode.window.registerTreeDataProvider('pollyChat', chatProvider);
```

**Option 2: As Panel**

```typescript
// Create panel in right sidebar
// Use VSCode's panel system
```

**For POC:**
- Start with webview panel
- Can refine to view container later
- Goal is to prove integration works

---

## Visual Design

### Match Polly Chat UI

**From Polly Electron App:**
- Source: `electron-app/src/renderer/` chat components
- Styles: Match existing chat CSS
- Layout: Messages + input at bottom

**Adapt for VSCode:**
- Use VSCode's webview styling
- Match Polly colors
- Ensure readability

---

## Testing Checklist

### Functional Tests

- [ ] Chat panel appears
- [ ] Can type messages
- [ ] Can send messages
- [ ] Messages appear in UI
- [ ] Responses received
- [ ] Connects to Polly backend
- [ ] Error handling works

### Integration Tests

- [ ] Works with VSCode theme
- [ ] Doesn't break other panels
- [ ] Can be hidden/shown
- [ ] Persists state
- [ ] No console errors

---

## Alternative: Core Modification

If extension API is insufficient:

### Minimal Core Change

**Add Chat Panel Type:**

```typescript
// src/vs/workbench/browser/parts/panel/panelPart.ts
// Add chat panel type
// Register in panel registry
```

**Documentation:**
- Document why extension API wasn't sufficient
- Document what core change was made
- Keep change minimal

---

## Next Steps

After chat panel works:

1. **Test Integration** - Verify everything works together
2. **Customize Theme** - Match Polly design system
3. **Test Merge** - Validate maintenance process
4. **Document** - Create integration guide

---

**Status:** Ready for implementation after ribbon integration

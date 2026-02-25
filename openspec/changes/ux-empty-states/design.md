# Design: Empty States with Calls-to-Action

## Architecture Impact

### EmptyState Component

A reusable vanilla JS component for rendering consistent empty states.

```js
// electron-app/src/renderer/components/empty-state.js

class EmptyState {
  /**
   * @param {object} options
   * @param {string} options.icon - Lucide icon name (e.g., "message-square", "search")
   * @param {string} options.title - Headline (e.g., "No conversations yet")
   * @param {string} options.description - Brief guidance text
   * @param {string} [options.actionLabel] - Button text (e.g., "New Chat")
   * @param {function} [options.onAction] - Button click handler
   * @param {string} [options.secondaryLabel] - Optional secondary link/button text
   * @param {function} [options.onSecondary] - Secondary action handler
   * @param {string} [options.size] - "small" | "medium" (default) | "large"
   */
  static render(options) {
    const { icon, title, description, actionLabel, onAction, secondaryLabel, onSecondary, size = 'medium' } = options;

    const container = document.createElement('div');
    container.className = `empty-state empty-state--${size}`;
    container.innerHTML = `
      <div class="empty-state__icon">
        <i data-lucide="${icon}" aria-hidden="true"></i>
      </div>
      <h3 class="empty-state__title">${title}</h3>
      <p class="empty-state__description">${description}</p>
      ${actionLabel ? `<button class="empty-state__action btn btn-primary">${actionLabel}</button>` : ''}
      ${secondaryLabel ? `<button class="empty-state__secondary btn btn-ghost">${secondaryLabel}</button>` : ''}
    `;

    if (actionLabel && onAction) {
      container.querySelector('.empty-state__action').addEventListener('click', onAction);
    }
    if (secondaryLabel && onSecondary) {
      container.querySelector('.empty-state__secondary').addEventListener('click', onSecondary);
    }

    // Trigger Lucide icon rendering
    requestAnimationFrame(() => lucide.createIcons({ nodes: [container] }));

    return container;
  }
}

window.EmptyState = EmptyState;
```

### CSS

```css
/* electron-app/src/renderer/components/empty-state.css */

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px 24px;
  min-height: 200px;
}

.empty-state--small {
  padding: 24px 16px;
  min-height: 120px;
}

.empty-state--large {
  padding: 64px 32px;
  min-height: 300px;
}

.empty-state__icon {
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-state__icon svg {
  width: 48px;
  height: 48px;
}

.empty-state--small .empty-state__icon svg {
  width: 32px;
  height: 32px;
}

.empty-state__title {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.empty-state__description {
  color: var(--text-secondary);
  font-size: 13px;
  max-width: 320px;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.empty-state__action {
  margin-bottom: 8px;
}

.empty-state__secondary {
  color: var(--text-secondary);
  font-size: 12px;
}
```

### Empty State Definitions

| View | Icon | Title | Description | Action |
|------|------|-------|-------------|--------|
| Conversations (none) | `message-square` | No conversations yet | Start a conversation with Polly to see it appear here. | "New Chat" → `createNewConversation()` |
| Conversations (search no results) | `search` | No results for "{query}" | Try a different search term or clear the search. | "Clear Search" → clear input |
| Conversations (page filter empty) | `filter` | No conversations on this page | Start a new conversation from this view to see it here. | "New Chat" → `createNewConversation()` |
| Dashboard (no data) | `layout-dashboard` | Welcome to Polly | Index your knowledge base to see stats and insights here. | "Go to Knowledge Base" → `showView('knowledge')` |
| Knowledge base (no sources) | `database` | No sources indexed | Add your Obsidian vault or code directories to get started. | "Add Source" → open add source flow |
| Patterns (none) | `brain` | No patterns learned yet | Polly learns patterns from your conversations over time. Have a few conversations and check back. | — (no action, this is passive) |
| Curricula (none) | `graduation-cap` | No curricula created | Use the Professor persona to create structured learning paths. | "Start with /curriculum" → focus chat input with `/curriculum` |
| Notes browse (none) | `file-text` | No notes found | Create your first note or connect your Obsidian vault. | "New Note" → create note flow |
| Notes browse (filter no results) | `search` | No notes matching filters | Try adjusting your search or filters. | "Clear Filters" → reset filters |
| API keys (none) | `key` | No API keys configured | Add keys for AI providers to enable cloud model routing. | "Add API Key" → open add key modal |
| Mental models (no custom) | `lightbulb` | Using default mental models | Polly applies 12 built-in mental models. Create custom ones to personalize your thinking. | "Create Model" → open editor |
| Domains (no custom) | `layers` | No custom domains | Domains organize your knowledge into practice areas. | "Create Domain" → open domain form |
| Graph (no entities) | `git-branch` | No entities in the graph | Entities are extracted from your conversations and notes. Start chatting to build your knowledge graph. | "Go to Chat" → `showView('chat')` |
| Learning (no topics) | `book-open` | No learning topics tracked | Use the Professor persona to start a learning path, or add topics manually. | "Start Learning" → focus chat input |
| Settings sidebar stubs | `clock` | Coming soon | {Feature name} is planned for a future release. | — |

### Search-Specific Empty State

The conversation search empty state needs special handling since it's within the sidebar (small space):

```js
// Use the "small" size variant
EmptyState.render({
  icon: 'search',
  title: `No results for "${query}"`,
  description: 'Try a different search term.',
  actionLabel: 'Clear',
  onAction: () => { searchInput.value = ''; searchConversations(); },
  size: 'small'
});
```

## Files Affected

| File | Changes |
|------|---------|
| New: `components/empty-state.js` | EmptyState component |
| New: `components/empty-state.css` | EmptyState styles |
| `index.html` | Register script and stylesheet |
| `app.js` | Replace text-only empty states with `EmptyState.render()` in: conversation list, dashboard, knowledge, patterns, curricula, domains, learning, graph, settings sidebar stubs |
| `notes-manager.js` | Replace notes empty states with `EmptyState.render()` |
| `api-keys-manager.js` | Replace API keys empty state with `EmptyState.render()` |

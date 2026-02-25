# Design: Skeleton Loading States

## Architecture Impact

### Skeleton Component Library

A set of CSS-only skeleton primitives that can be composed into view-specific placeholder layouts.

```css
/* electron-app/src/renderer/styles/skeleton.css */

.skeleton {
  background: var(--bg-tertiary, #2a2a2a);
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.skeleton::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.04) 50%,
    transparent 100%
  );
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@media (prefers-reduced-motion: reduce) {
  .skeleton::after {
    animation: none;
  }
  .skeleton {
    opacity: 0.7;
  }
}

/* Primitives */
.skeleton-text { height: 14px; margin-bottom: 8px; }
.skeleton-text--short { width: 40%; }
.skeleton-text--medium { width: 65%; }
.skeleton-text--long { width: 90%; }
.skeleton-text--full { width: 100%; }

.skeleton-heading { height: 20px; width: 50%; margin-bottom: 16px; }

.skeleton-avatar { width: 32px; height: 32px; border-radius: 50%; }

.skeleton-card {
  height: 100px;
  border-radius: 8px;
  margin-bottom: 12px;
}

.skeleton-stat {
  height: 80px;
  border-radius: 8px;
  flex: 1;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  margin-bottom: 4px;
}
```

### JavaScript Helper

```js
// electron-app/src/renderer/components/skeleton-loader.js

class SkeletonLoader {
  /**
   * Generate skeleton HTML for a specific view type.
   * @param {string} viewType - "dashboard" | "conversations" | "notes" | "patterns" | "settings" | "knowledge" | "graph"
   * @returns {string} HTML string
   */
  static forView(viewType) {
    const templates = {
      dashboard: `
        <div class="skeleton-view" role="status" aria-label="Loading dashboard">
          <div class="skeleton skeleton-heading"></div>
          <div style="display: flex; gap: 12px; margin-bottom: 24px;">
            <div class="skeleton skeleton-stat"></div>
            <div class="skeleton skeleton-stat"></div>
            <div class="skeleton skeleton-stat"></div>
            <div class="skeleton skeleton-stat"></div>
          </div>
          <div class="skeleton skeleton-heading" style="width: 30%;"></div>
          <div class="skeleton skeleton-card"></div>
          <div class="skeleton skeleton-card"></div>
        </div>
      `,
      conversations: `
        <div class="skeleton-view" role="status" aria-label="Loading conversations">
          ${Array(6).fill(`
            <div class="skeleton-list-item">
              <div class="skeleton skeleton-avatar"></div>
              <div style="flex: 1;">
                <div class="skeleton skeleton-text skeleton-text--medium"></div>
                <div class="skeleton skeleton-text skeleton-text--short" style="height: 10px;"></div>
              </div>
            </div>
          `).join('')}
        </div>
      `,
      notes: `
        <div class="skeleton-view" role="status" aria-label="Loading notes">
          <div class="skeleton skeleton-heading"></div>
          ${Array(8).fill(`
            <div class="skeleton-list-item">
              <div style="flex: 1;">
                <div class="skeleton skeleton-text skeleton-text--long"></div>
                <div class="skeleton skeleton-text skeleton-text--short" style="height: 10px;"></div>
              </div>
            </div>
          `).join('')}
        </div>
      `,
      patterns: `
        <div class="skeleton-view" role="status" aria-label="Loading patterns">
          <div class="skeleton skeleton-heading"></div>
          <div class="skeleton skeleton-card" style="height: 60px;"></div>
          <div class="skeleton skeleton-card" style="height: 60px;"></div>
          <div class="skeleton skeleton-card" style="height: 60px;"></div>
          <div class="skeleton skeleton-card" style="height: 60px;"></div>
        </div>
      `,
      settings: `
        <div class="skeleton-view" role="status" aria-label="Loading settings">
          <div class="skeleton skeleton-heading"></div>
          <div class="skeleton skeleton-text skeleton-text--full" style="height: 36px; margin-bottom: 16px;"></div>
          <div class="skeleton skeleton-text skeleton-text--full" style="height: 36px; margin-bottom: 16px;"></div>
          <div class="skeleton skeleton-text skeleton-text--full" style="height: 36px; margin-bottom: 16px;"></div>
          <div class="skeleton skeleton-text skeleton-text--medium" style="height: 32px;"></div>
        </div>
      `,
      knowledge: `
        <div class="skeleton-view" role="status" aria-label="Loading knowledge base">
          <div class="skeleton skeleton-heading"></div>
          <div style="display: flex; gap: 12px; margin-bottom: 16px;">
            <div class="skeleton skeleton-stat" style="height: 60px;"></div>
            <div class="skeleton skeleton-stat" style="height: 60px;"></div>
          </div>
          <div class="skeleton skeleton-card"></div>
          <div class="skeleton skeleton-card"></div>
        </div>
      `,
    };

    return templates[viewType] || templates.settings;
  }
}

window.SkeletonLoader = SkeletonLoader;
```

### Integration with showView()

In `app.js:showView()`, replace "Loading..." text with skeleton:

```js
// Before
sidebarContent.innerHTML = '<div class="loading">Loading notes...</div>';

// After
sidebarContent.innerHTML = SkeletonLoader.forView('notes');
```

The skeleton stays visible until the actual content replaces it. No explicit "remove skeleton" step needed — the content replacement naturally removes it.

### Transition

For a smooth transition from skeleton to real content, add a brief fade:

```css
.skeleton-view {
  animation: skeleton-fade-in 200ms ease-out;
}

@keyframes skeleton-fade-in {
  from { opacity: 0.5; }
  to { opacity: 1; }
}
```

The real content can also fade in on load for a seamless handoff.

## Files Affected

| File | Changes |
|------|---------|
| New: `styles/skeleton.css` | Skeleton CSS primitives and animations |
| New: `components/skeleton-loader.js` | View-specific skeleton templates |
| `index.html` | Register skeleton.css and skeleton-loader.js |
| `app.js` | Replace "Loading..." strings in `showView()` with `SkeletonLoader.forView()` |
| `notes-manager.js` | Replace notes loading text with skeleton |

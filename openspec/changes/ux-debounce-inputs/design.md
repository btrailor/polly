# Design: Debounce Search and Input Operations

## Architecture Impact

### Debounce Utility

```js
// electron-app/src/renderer/utils/debounce.js

/**
 * Creates a debounced version of a function.
 * @param {function} fn - The function to debounce
 * @param {number} delay - Delay in ms (default: 250)
 * @param {object} options
 * @param {boolean} options.leading - Fire on leading edge (default: false)
 * @param {boolean} options.trailing - Fire on trailing edge (default: true)
 * @returns {function} Debounced function with .cancel() method
 */
function debounce(fn, delay = 250, options = {}) {
  const { leading = false, trailing = true } = options;
  let timer = null;
  let lastArgs = null;

  function debounced(...args) {
    lastArgs = args;

    if (leading && !timer) {
      fn(...args);
    }

    clearTimeout(timer);
    timer = setTimeout(() => {
      timer = null;
      if (trailing && lastArgs) {
        fn(...lastArgs);
        lastArgs = null;
      }
    }, delay);
  }

  debounced.cancel = () => {
    clearTimeout(timer);
    timer = null;
    lastArgs = null;
  };

  return debounced;
}

window.debounce = debounce;
```

### Application Points

| Input | Delay | Leading | Notes |
|-------|-------|---------|-------|
| Conversation search | 200ms | false | Short delay for responsive feel while preventing excessive re-renders |
| Notes search/filter | 250ms | false | Slightly longer for potentially heavier DOM operations |
| Garden entity search | 300ms | false | Already implemented with setTimeout; migrate to utility |
| Auto-save trigger | 2000ms | false | Already has delay; migrate to utility for consistency |
| Pattern/mental model filter | 200ms | false | If input-driven filtering exists |
| Chat input height auto-resize | 0ms (no debounce) | — | Must be immediate for responsive textarea |

### Migration Pattern

```js
// Before (app.js:2611)
document.getElementById('conversations-search-input')
  .addEventListener('input', searchConversations);

// After
const debouncedSearch = debounce(searchConversations, 200);
document.getElementById('conversations-search-input')
  .addEventListener('input', debouncedSearch);
```

### Duplicate Listener Fix

`app.js:2611` and `app.js:4116` both register `input` event listeners on the conversation search input. Remove the duplicate to prevent double-execution.

### Visual Feedback During Debounce

For search inputs with a visible delay, add a subtle "searching..." indicator:

```js
// On every keystroke (not debounced) — show indicator
searchInput.addEventListener('input', () => {
  searchInput.classList.add('input-searching');
});

// In the debounced search callback — remove indicator
const debouncedSearch = debounce(() => {
  searchConversations();
  searchInput.classList.remove('input-searching');
}, 200);
```

```css
.input-searching {
  background-image: url("data:image/svg+xml,..."); /* subtle spinner */
  background-position: right 8px center;
  background-repeat: no-repeat;
}
```

This gives immediate visual feedback that input was received, even though the search hasn't fired yet.

## Files Affected

| File | Changes |
|------|---------|
| New: `utils/debounce.js` | Debounce utility function |
| `index.html` | Register debounce.js script |
| `app.js` | Wrap conversation search in debounce; remove duplicate listener at line 4116; migrate garden search to use utility |
| `notes-manager.js` | Wrap notes search/filter in debounce; optionally migrate auto-save delay to use utility |
| `styles/main.css` | Add `.input-searching` indicator style |

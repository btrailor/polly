# Design: Replace setTimeout Race Conditions

## Architecture Impact

No new subsystems. Targeted replacements of fragile timing patterns with robust alternatives.

### 1. DOM Readiness: MutationObserver / requestAnimationFrame

**Problem:** `setTimeout(() => initNotes(), 100)` assumes the notes view DOM is ready in 100ms after calling `showView('notes')`.

**Solution:** Use `requestAnimationFrame` to wait for the next paint cycle, which guarantees the DOM has been updated:

```js
// Before
setTimeout(() => {
  if (window.notesManager) {
    window.notesManager.initialize(notesContainer);
  }
}, 100);

// After
requestAnimationFrame(() => {
  requestAnimationFrame(() => {
    // Double-rAF ensures the browser has painted the new DOM
    if (window.notesManager) {
      window.notesManager.initialize(notesContainer);
    }
  });
});
```

For cases where a specific element must exist before proceeding, use a `waitForElement` utility:

```js
function waitForElement(selector, container = document, timeout = 2000) {
  return new Promise((resolve, reject) => {
    const existing = container.querySelector(selector);
    if (existing) { resolve(existing); return; }

    const observer = new MutationObserver((mutations, obs) => {
      const el = container.querySelector(selector);
      if (el) { obs.disconnect(); resolve(el); }
    });
    observer.observe(container, { childList: true, subtree: true });

    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`waitForElement: "${selector}" not found within ${timeout}ms`));
    }, timeout);
  });
}
```

### 2. Lucide Icon Re-rendering

**Problem:** `setTimeout(() => lucide.createIcons(), 50)` is called in 5+ places after DOM mutations. The delay is arbitrary and the calls are scattered.

**Solution:** Create a centralized `refreshIcons()` function that batches icon re-rendering to the next animation frame:

```js
let iconRefreshScheduled = false;

function refreshIcons(container = document) {
  if (iconRefreshScheduled) return; // Already scheduled
  iconRefreshScheduled = true;

  requestAnimationFrame(() => {
    lucide.createIcons({ nodes: container === document ? undefined : [container] });
    iconRefreshScheduled = false;
  });
}
```

Replace all `setTimeout(() => lucide.createIcons(), 50)` calls with `refreshIcons()`. The batching ensures multiple rapid DOM changes only trigger one icon refresh per frame.

### 3. Persona Auto-Advance

**Problem:** `setTimeout(async () => { /* advance */ }, 500)` fires after a fixed delay with no cancellation. If the user sends another message or navigates away within 500ms, the auto-advance may execute on stale state.

**Solution:** Use an event-driven approach with cancellation:

```js
let autoAdvanceTimer = null;

function schedulePersonaAutoAdvance(step, context) {
  cancelPersonaAutoAdvance(); // Cancel any pending

  autoAdvanceTimer = setTimeout(async () => {
    autoAdvanceTimer = null;
    // Verify state is still valid before advancing
    if (currentPersonaStep === step && currentConversationId === context.conversationId) {
      await advancePersonaWorkflow(step);
    }
  }, 500);
}

function cancelPersonaAutoAdvance() {
  if (autoAdvanceTimer) {
    clearTimeout(autoAdvanceTimer);
    autoAdvanceTimer = null;
  }
}

// Cancel on: new message send, view switch, conversation switch
```

The key improvement is the **state validation** before execution (check that we're still on the same step and conversation) and the **explicit cancellation** on state-changing events.

### 4. Auto-Categorize Delay

**Problem:** `setTimeout(() => autoCategorizeConversation(), 200)` at `app.js:8745` delays categorization by 200ms for no clear reason.

**Solution:** If the delay is to avoid blocking the response rendering, use `requestIdleCallback` (or a polyfill) instead:

```js
// Before
setTimeout(() => autoCategorizeConversation(), 200);

// After
requestIdleCallback(() => autoCategorizeConversation(), { timeout: 1000 });
```

`requestIdleCallback` runs the function when the browser is idle, which is the actual intent — "do this when you have a chance, after the important rendering is done." The `timeout` ensures it runs within 1 second even if the browser stays busy.

## Files Affected

| File | Changes |
|------|---------|
| New: `utils/dom-helpers.js` | `waitForElement()`, `refreshIcons()` utilities |
| `app.js` | Replace `setTimeout` at lines ~3095, ~2375, ~2391, ~2410, ~2603, ~5371, ~8745 with robust alternatives |
| `index.html` | Register `dom-helpers.js` |

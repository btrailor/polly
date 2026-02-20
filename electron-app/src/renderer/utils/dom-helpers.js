/**
 * DOM Helper Utilities
 *
 * Robust alternatives to setTimeout-based DOM readiness and icon refresh patterns.
 */

/**
 * Wait for a CSS selector to appear inside a container.
 * Uses MutationObserver so there is no polling delay.
 *
 * @param {string} selector  - CSS selector to wait for
 * @param {Element|Document} [container=document] - root to observe
 * @param {number} [timeout=2000] - ms before rejecting
 * @returns {Promise<Element>}
 */
function waitForElement(selector, container = document, timeout = 2000) {
  return new Promise((resolve, reject) => {
    const existing = container.querySelector(selector);
    if (existing) {
      resolve(existing);
      return;
    }

    const observer = new MutationObserver((_mutations, obs) => {
      const el = container.querySelector(selector);
      if (el) {
        obs.disconnect();
        resolve(el);
      }
    });

    observer.observe(container, { childList: true, subtree: true });

    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`waitForElement: "${selector}" not found within ${timeout}ms`));
    }, timeout);
  });
}

/**
 * Schedule a Lucide icon refresh on the next animation frame.
 * Batches multiple calls within the same frame into a single createIcons() call.
 *
 * @param {Element|Document} [container=document] - root element to refresh icons within
 */
let _iconRefreshScheduled = false;

function refreshIcons(container = document) {
  if (_iconRefreshScheduled) return; // Already queued for this frame
  _iconRefreshScheduled = true;

  requestAnimationFrame(() => {
    _iconRefreshScheduled = false;
    if (typeof lucide === "undefined") return;

    if (container === document) {
      lucide.createIcons();
    } else {
      // createIcons accepts a `nodes` option to limit scope
      lucide.createIcons({ nodes: [container] });
    }
  });
}

window.waitForElement = waitForElement;
window.refreshIcons = refreshIcons;

/**
 * requestIdleCallback polyfill for environments that don't support it.
 * Falls back to setTimeout so the callback still runs, just not idle-scheduled.
 */
if (typeof window.requestIdleCallback === "undefined") {
  window.requestIdleCallback = function (cb, options) {
    const timeout = (options && options.timeout) ? options.timeout : 1000;
    return setTimeout(() => cb({ didTimeout: false, timeRemaining: () => 0 }), timeout);
  };
  window.cancelIdleCallback = function (id) {
    clearTimeout(id);
  };
}

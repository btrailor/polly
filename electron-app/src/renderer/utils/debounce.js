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

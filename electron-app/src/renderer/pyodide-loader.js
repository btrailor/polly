/**
 * Pyodide Loader
 * Phase 23.5: Security Hardening
 * 
 * Loads and initializes Pyodide for sandboxed Python execution.
 */

// Pyodide version - update this when upgrading
const PYODIDE_VERSION = '0.24.1';
const PYODIDE_CDN_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

let pyodideInstance = null;
let loadingPromise = null;

/**
 * Load Pyodide if not already loaded.
 * Returns the same promise if already loading to avoid multiple loads.
 * 
 * @returns {Promise<Pyodide>} Pyodide instance
 */
async function loadPyodide() {
  // Return existing instance if already loaded
  if (pyodideInstance) {
    return pyodideInstance;
  }
  
  // Return existing loading promise if already loading
  if (loadingPromise) {
    return loadingPromise;
  }
  
  // Start loading
  loadingPromise = (async () => {
    try {
      console.log('[Pyodide] Loading Pyodide from CDN...');
      
      // Check if loadPyodide is available (from pyodide.js script)
      if (typeof globalThis.loadPyodide === 'undefined') {
        throw new Error('Pyodide script not loaded. Make sure pyodide.js is included in index.html');
      }
      
      // Load Pyodide
      const pyodide = await globalThis.loadPyodide({
        indexURL: PYODIDE_CDN_URL,
        stdout: (text) => {
          // Capture stdout for execution results
          if (window.pyodideStdout) {
            window.pyodideStdout(text);
          }
        },
        stderr: (text) => {
          // Capture stderr for error output
          if (window.pyodideStderr) {
            window.pyodideStderr(text);
          }
        }
      });
      
      console.log('[Pyodide] Pyodide loaded successfully');
      console.log(`[Pyodide] Version: ${pyodide.version}`);
      
      // Store instance
      pyodideInstance = pyodide;
      
      return pyodide;
    } catch (error) {
      console.error('[Pyodide] Failed to load Pyodide:', error);
      loadingPromise = null; // Reset so we can retry
      throw error;
    }
  })();
  
  return loadingPromise;
}

/**
 * Get the current Pyodide instance (if loaded).
 * Returns null if not loaded yet.
 * 
 * @returns {Pyodide|null} Pyodide instance or null
 */
function getPyodide() {
  return pyodideInstance;
}

/**
 * Check if Pyodide is loaded.
 * 
 * @returns {boolean} True if Pyodide is loaded
 */
function isPyodideLoaded() {
  return pyodideInstance !== null;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { loadPyodide, getPyodide, isPyodideLoaded };
}

// Also make available globally for easy access
window.PyodideLoader = {
  loadPyodide,
  getPyodide,
  isPyodideLoaded
};

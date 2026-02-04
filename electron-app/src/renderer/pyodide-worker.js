/**
 * Pyodide Web Worker
 * Phase 23.5: Security Hardening
 * 
 * Isolated Web Worker for executing Python code in Pyodide.
 * Provides additional isolation layer beyond the main renderer process.
 */

// Import Pyodide (will be loaded from CDN)
importScripts('https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js');

let pyodide = null;
let stdoutBuffer = '';
let stderrBuffer = '';

/**
 * Initialize Pyodide in the worker.
 */
async function initPyodide() {
  if (pyodide) {
    return pyodide;
  }
  
  try {
    self.postMessage({ type: 'status', status: 'loading', message: 'Loading Pyodide...' });
    
    pyodide = await loadPyodide({
      indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
      stdout: (text) => {
        stdoutBuffer += text;
      },
      stderr: (text) => {
        stderrBuffer += text;
      }
    });
    
    self.postMessage({ type: 'status', status: 'ready', message: 'Pyodide loaded' });
    return pyodide;
  } catch (error) {
    self.postMessage({ 
      type: 'error', 
      error: `Failed to load Pyodide: ${error.message}` 
    });
    throw error;
  }
}

/**
 * Execute Python code with timeout.
 * 
 * @param {string} code - Python code to execute
 * @param {number} timeout - Timeout in seconds (default: 10)
 * @returns {Promise<Object>} Execution result
 */
async function executeCode(code, timeout = 10) {
  if (!pyodide) {
    await initPyodide();
  }
  
  // Clear buffers
  stdoutBuffer = '';
  stderrBuffer = '';
  
  // Set up timeout
  const timeoutId = setTimeout(() => {
    self.postMessage({
      type: 'result',
      status: 'timeout',
      error: `Code execution timed out after ${timeout} seconds`
    });
  }, timeout * 1000);
  
  try {
    const startTime = performance.now();
    
    // Execute code
    await pyodide.runPythonAsync(code);
    
    const executionTime = (performance.now() - startTime) / 1000;
    clearTimeout(timeoutId);
    
    // Return result
    self.postMessage({
      type: 'result',
      status: 'success',
      output: stdoutBuffer,
      error: stderrBuffer || null,
      execution_time: executionTime
    });
    
  } catch (error) {
    clearTimeout(timeoutId);
    
    // Return error
    self.postMessage({
      type: 'result',
      status: 'error',
      output: stdoutBuffer,
      error: error.message || String(error),
      execution_time: 0
    });
  }
}

// Handle messages from main thread
self.onmessage = async (event) => {
  const { type, code, timeout } = event.data;
  
  try {
    switch (type) {
      case 'init':
        await initPyodide();
        self.postMessage({ type: 'ready' });
        break;
        
      case 'execute':
        await executeCode(code, timeout);
        break;
        
      default:
        self.postMessage({
          type: 'error',
          error: `Unknown message type: ${type}`
        });
    }
  } catch (error) {
    self.postMessage({
      type: 'error',
      error: error.message || String(error)
    });
  }
};

// Initialize on worker load
initPyodide().catch(error => {
  self.postMessage({
    type: 'error',
    error: `Worker initialization failed: ${error.message}`
  });
});

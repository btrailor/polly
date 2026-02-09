/**
 * API Client Utility
 * Handles API calls with retry logic for server readiness
 */

const API_BASE_URL = 'http://127.0.0.1:11436';

/**
 * Fetch with retry logic for server startup
 * @param {string} endpoint - API endpoint (e.g., '/polly/mental-models/list')
 * @param {Object} options - Fetch options
 * @param {number} retries - Number of retry attempts (default: 3)
 * @param {number} delay - Delay between retries in ms (default: 1000)
 * @returns {Promise<Response>}
 */
async function fetchWithRetry(endpoint, options = {}, retries = 3, delay = 1000) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, options);
      
      // Return response even if not ok - let caller handle HTTP errors
      // Only retry on network errors (connection refused, etc.)
      return response;
    } catch (error) {
      // Network error (connection refused, timeout, etc.)
      if (attempt < retries) {
        console.warn(`[API Client] Request to ${endpoint} failed (attempt ${attempt}/${retries}):`, error.message);
        console.warn(`[API Client] Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        console.error(`[API Client] Request to ${endpoint} failed after ${retries} attempts:`, error);
        throw error;
      }
    }
  }
}

/**
 * Fetch JSON with retry logic
 * @param {string} endpoint - API endpoint
 * @param {Object} options - Fetch options
 * @param {number} retries - Number of retry attempts (default: 3)
 * @param {number} delay - Delay between retries in ms (default: 1000)
 * @returns {Promise<Object>} - Parsed JSON response
 */
async function fetchJSON(endpoint, options = {}, retries = 3, delay = 1000) {
  const response = await fetchWithRetry(endpoint, options, retries, delay);
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Wait for server to be ready
 * @param {number} maxAttempts - Maximum number of attempts (default: 10)
 * @param {number} delay - Delay between attempts in ms (default: 1000)
 * @returns {Promise<boolean>} - True if server is ready, false otherwise
 */
async function waitForServer(maxAttempts = 10, delay = 1000) {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, { 
        method: 'GET',
        signal: AbortSignal.timeout(2000) // 2 second timeout per attempt
      });
      
      if (response.ok) {
        console.log('[API Client] Server is ready');
        return true;
      }
    } catch (error) {
      if (attempt < maxAttempts) {
        console.log(`[API Client] Waiting for server... (attempt ${attempt}/${maxAttempts})`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  console.error('[API Client] Server did not become ready');
  return false;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    fetchWithRetry,
    fetchJSON,
    waitForServer,
    API_BASE_URL
  };
}

// Also attach to window for browser use
if (typeof window !== 'undefined') {
  window.APIClient = {
    fetchWithRetry,
    fetchJSON,
    waitForServer,
    API_BASE_URL
  };
}

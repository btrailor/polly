/**
 * API Keys Manager for Polly Electron App
 * Handles API key management UI and interactions with the backend
 */

const SETTINGS_API_BASE_URL = 'http://127.0.0.1:11436/api/settings';

console.log('[API Keys Manager] Module loaded - version 2.0');
console.log('[API Keys Manager] SETTINGS_API_BASE_URL:', SETTINGS_API_BASE_URL);

/**
 * Initialize API Keys tab
 */
async function initializeAPIKeysTab() {
  console.log('[API Keys Manager] Initializing...');
  
  // Load API keys on tab open
  const apiKeysTab = document.querySelector('[data-tab="api-keys"]');
  console.log('[API Keys Manager] API Keys tab button found:', !!apiKeysTab);
  
  if (apiKeysTab) {
    apiKeysTab.addEventListener('click', () => {
      console.log('[API Keys Manager] Tab clicked, loading data...');
      loadAPIKeys();
      loadBudgetStatus();
    });
  }
  
  // Add API Key button
  const addButton = document.getElementById('btn-add-api-key');
  console.log('[API Keys Manager] Add button found:', !!addButton);
  if (addButton) {
    addButton.addEventListener('click', showAddAPIKeyModal);
  }
  
  // Save budget button
  const saveBudgetButton = document.getElementById('btn-save-budget');
  console.log('[API Keys Manager] Save budget button found:', !!saveBudgetButton);
  if (saveBudgetButton) {
    saveBudgetButton.addEventListener('click', saveBudgetSettings);
  }
  
  // Initial load if we're on the API keys tab
  const tabContent = document.getElementById('tab-api-keys');
  const isVisible = tabContent && !tabContent.classList.contains('hidden');
  console.log('[API Keys Manager] Tab content found:', !!tabContent, 'Visible:', isVisible);
  
  if (isVisible) {
    console.log('[API Keys Manager] Tab is visible, loading data immediately...');
    loadAPIKeys();
    loadBudgetStatus();
  }
}

/**
 * Load and display API keys
 */
async function loadAPIKeys() {
  console.log('[API Keys] loadAPIKeys() called');
  const listContainer = document.getElementById('api-keys-list');
  if (!listContainer) {
    console.warn('[API Keys] Container #api-keys-list not found');
    return;
  }
  
  listContainer.innerHTML = '<div class="settings-loading-spinner">Loading keys...</div>';
  
  try {
    console.log('[API Keys] Fetching from:', `${SETTINGS_API_BASE_URL}/keys`);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.warn('[API Keys] Request timeout - aborting');
      controller.abort();
    }, 5000);
    
    const response = await fetch(`${SETTINGS_API_BASE_URL}/keys`, { signal: controller.signal });
    clearTimeout(timeoutId);
    console.log('[API Keys] Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`Failed to load API keys (status ${response.status})`);
    }
    
    const data = await response.json();
    console.log('[API Keys] Data received:', data);
    
    if (!data.keys || data.keys.length === 0) {
      listContainer.innerHTML = `
        <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
          <i data-lucide="key" style="width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
          <p style="font-size: 14px;">No API keys configured yet.</p>
          <p style="font-size: 12px; margin-top: 8px;">Click "Add API Key" to get started.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }
    
    listContainer.innerHTML = data.keys.map(key => `
      <div class="api-key-item" data-provider="${key.provider}">
        <div class="api-key-info">
          <div class="api-key-icon">
            ${getProviderIcon(key.provider)}
          </div>
          <div class="api-key-details">
            <div class="api-key-provider">
              ${formatProviderName(key.provider)}
              ${getProviderKeyLink(key.provider) ? `
                <a href="${getProviderKeyLink(key.provider)}" target="_blank" rel="noopener noreferrer" 
                   style="margin-left: 8px; font-size: 11px; color: var(--accent); text-decoration: none; opacity: 0.8;"
                   title="Get API key from ${formatProviderName(key.provider)}">
                  <i data-lucide="external-link" style="width: 12px; height: 12px; vertical-align: middle;"></i>
                  Get Key
                </a>
              ` : ''}
            </div>
            <div class="api-key-status">
              <span class="api-key-status-dot ${key.is_set ? 'connected' : 'disconnected'}"></span>
              <span>${key.is_set ? 'Configured' : 'Not set'}</span>
              <span style="margin-left: 8px; opacity: 0.7;">via ${key.storage_type || 'unknown'}</span>
            </div>
          </div>
        </div>
        <div class="api-key-actions">
          <button class="btn btn-secondary btn-sm" onclick="testAPIKey('${key.provider}')" ${!key.is_set ? 'disabled' : ''}>
            <i data-lucide="check-circle" style="width: 14px; height: 14px;"></i>
            Test
          </button>
          <button class="btn btn-secondary btn-sm" onclick="deleteAPIKey('${key.provider}')" ${!key.is_set ? 'disabled' : ''}>
            <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
            Delete
          </button>
        </div>
      </div>
    `).join('');
    
    lucide.createIcons();
    
  } catch (error) {
    console.error('[API Keys] Error loading API keys:', error);
    console.error('[API Keys] Error type:', error.name);
    console.error('[API Keys] Error message:', error.message);
    
    const errorMessage = error.name === 'AbortError' 
      ? 'Request timed out. Backend endpoint not available.'
      : `${error.message}`;
    
    listContainer.innerHTML = `
      <div style="color: var(--error); text-align: center; padding: 20px;">
        <p>Failed to load API keys</p>
        <p style="font-size: 12px; margin-top: 8px;">${errorMessage}</p>
        <p style="font-size: 11px; margin-top: 4px; opacity: 0.7;">Endpoint: ${SETTINGS_API_BASE_URL}/keys</p>
      </div>
    `;
  }
}

/**
 * Load and display budget status
 */
async function loadBudgetStatus() {
  console.log('[Budget] loadBudgetStatus() called');
  const statusContainer = document.getElementById('budget-status');
  if (!statusContainer) {
    console.warn('[Budget] Container #budget-status not found');
    return;
  }
  
  statusContainer.innerHTML = '<div class="settings-loading-spinner">Loading budget...</div>';
  
  try {
    console.log('[Budget] Fetching from:', `${SETTINGS_API_BASE_URL}/budget`);
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.warn('[Budget] Request timeout - aborting');
      controller.abort();
    }, 5000);
    
    const response = await fetch(`${SETTINGS_API_BASE_URL}/budget`, { signal: controller.signal });
    clearTimeout(timeoutId);
    console.log('[Budget] Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`Failed to load budget (status ${response.status})`);
    }
    
    const data = await response.json();
    console.log('[Budget] Data received:', data);
    
    // Handle wrapped response (success: true, budget: {...}, spending: {...})
    let budgetData = data;
    if (data.success && data.budget) {
      // Response is wrapped, extract the budget data
      budgetData = {
        limits: {
          daily: data.budget.daily.limit,
          monthly: data.budget.monthly.limit
        },
        daily: {
          spent: data.budget.daily.spent,
          percentage: data.budget.daily.percent_used
        },
        monthly: {
          spent: data.budget.monthly.spent,
          percentage: data.budget.monthly.percent_used
        },
        total_cost: data.spending?.total_cost || 0,
        total_requests: data.spending?.total_requests || 0,
        total_tokens: data.spending?.total_tokens || 0
      };
    }
    
    // Check if budget data is valid
    if (!budgetData.limits || !budgetData.daily || !budgetData.monthly) {
      console.warn('Budget data incomplete:', budgetData);
      statusContainer.innerHTML = `
        <div style="color: var(--text-secondary); font-size: 13px; text-align: center; padding: 16px;">
          Budget tracking not configured
        </div>
      `;
      return;
    }
    
    // Update budget limit inputs
    document.getElementById('budget-daily-limit').value = budgetData.limits.daily;
    document.getElementById('budget-monthly-limit').value = budgetData.limits.monthly;
    
    statusContainer.innerHTML = `
      <div class="budget-limit">
        <div class="budget-limit-header">
          <span class="budget-limit-label">Daily Budget</span>
          <span class="budget-limit-value">$${budgetData.daily.spent.toFixed(2)} / $${budgetData.limits.daily.toFixed(2)}</span>
        </div>
        <div class="budget-progress">
          <div class="budget-progress-bar ${getBudgetClass(budgetData.daily.percentage)}" style="width: ${Math.min(budgetData.daily.percentage, 100)}%"></div>
        </div>
      </div>
      
      <div class="budget-limit">
        <div class="budget-limit-header">
          <span class="budget-limit-label">Monthly Budget</span>
          <span class="budget-limit-value">$${budgetData.monthly.spent.toFixed(2)} / $${budgetData.limits.monthly.toFixed(2)}</span>
        </div>
        <div class="budget-progress">
          <div class="budget-progress-bar ${getBudgetClass(budgetData.monthly.percentage)}" style="width: ${Math.min(budgetData.monthly.percentage, 100)}%"></div>
        </div>
      </div>
      
      <div style="margin-top: 16px; padding: 12px; background: var(--bg-hover); border-radius: 4px; font-size: 12px;">
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; text-align: center;">
          <div>
            <div style="color: var(--text-secondary);">Total Cost</div>
            <div style="color: var(--text-primary); font-weight: 600; margin-top: 4px;">$${budgetData.total_cost.toFixed(4)}</div>
          </div>
          <div>
            <div style="color: var(--text-secondary);">Requests</div>
            <div style="color: var(--text-primary); font-weight: 600; margin-top: 4px;">${budgetData.total_requests}</div>
          </div>
          <div>
            <div style="color: var(--text-secondary);">Tokens</div>
            <div style="color: var(--text-primary); font-weight: 600; margin-top: 4px;">${(budgetData.total_tokens / 1000).toFixed(1)}K</div>
          </div>
        </div>
      </div>
    `;
    
  } catch (error) {
    console.error('Error loading budget:', error);
    const errorMessage = error.name === 'AbortError' 
      ? 'Request timed out. Backend may not be running.'
      : error.message;
    statusContainer.innerHTML = `
      <div style="color: var(--error); text-align: center; padding: 20px;">
        <p>Failed to load budget status</p>
        <p style="font-size: 12px; margin-top: 8px;">${errorMessage}</p>
      </div>
    `;
  }
}

/**
 * Show modal to add a new API key
 */
function showAddAPIKeyModal() {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.id = 'api-key-modal';
  
  modal.innerHTML = `
    <div class="modal-container">
      <div class="modal-header">
        <h2 class="modal-title">Add API Key</h2>
      </div>
      <div class="modal-body">
        <div class="form-group">
          <label>Provider</label>
          <select id="modal-provider-select" style="width: 100%; padding: 8px; background: var(--bg-hover); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
            <option value="">Select a provider...</option>
            <option value="anthropic">Anthropic (Claude)</option>
            <option value="openai">OpenAI (GPT)</option>
            <option value="github">GitHub Models (Multi-Model)</option>
            <option value="grok">xAI (Grok)</option>
            <option value="perplexity">Perplexity AI</option>
            <option value="gemini">Google (Gemini)</option>
            <option value="mistral">Mistral AI</option>
            <option value="openrouter">OpenRouter (100+ models)</option>
          </select>
        </div>
        
        <div class="form-group" style="margin-top: 16px;">
          <label>API Key</label>
          <input type="password" id="modal-api-key-input" placeholder="Enter your API key" style="width: 100%; padding: 8px; background: var(--bg-hover); border: 1px solid var(--border-color); border-radius: 4px; color: var(--text-primary);">
          <p class="form-hint" id="modal-key-hint" style="margin-top: 8px;"></p>
        </div>
        
        <div id="modal-status" style="margin-top: 16px; font-size: 13px;"></div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="closeAddAPIKeyModal()">Cancel</button>
        <button class="btn btn-primary" onclick="saveAPIKey()">Save & Test</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // Update hint on provider change
  const providerSelect = modal.querySelector('#modal-provider-select');
  const hintElement = modal.querySelector('#modal-key-hint');
  
  providerSelect.addEventListener('change', () => {
    const provider = providerSelect.value;
    const keyLink = getProviderKeyLink(provider);
    
    if (provider === 'anthropic') {
      hintElement.innerHTML = `Format: sk-ant-api03-... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at console.anthropic.com</a>`;
    } else if (provider === 'openai') {
      hintElement.innerHTML = `Format: sk-... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at platform.openai.com</a>`;
    } else if (provider === 'github') {
      hintElement.innerHTML = `Format: ghp_... or github_pat_... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get a token at github.com/settings/tokens</a> (requires "models:read" scope)`;
    } else if (provider === 'grok') {
      hintElement.innerHTML = `Format: xai-... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at console.x.ai</a>`;
    } else if (provider === 'perplexity') {
      hintElement.innerHTML = `Format: pplx-... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at perplexity.ai/settings/api</a>`;
    } else if (provider === 'gemini') {
      hintElement.innerHTML = `Format: AI... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at aistudio.google.com</a>`;
    } else if (provider === 'mistral') {
      hintElement.innerHTML = `Format: ... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at console.mistral.ai</a>`;
    } else if (provider === 'openrouter') {
      hintElement.innerHTML = `Format: sk-or-... • <a href="${keyLink}" target="_blank" rel="noopener noreferrer" style="color: var(--accent); text-decoration: underline;">Get your key at openrouter.ai/keys</a> (single key for 100+ models)`;
    } else {
      hintElement.innerHTML = '';
    }
  });
  
  // Close on background click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeAddAPIKeyModal();
    }
  });
}

/**
 * Close the add API key modal
 */
function closeAddAPIKeyModal() {
  const modal = document.getElementById('api-key-modal');
  if (modal) {
    modal.remove();
  }
}

/**
 * Save a new API key
 */
async function saveAPIKey() {
  const provider = document.getElementById('modal-provider-select').value;
  const key = document.getElementById('modal-api-key-input').value;
  const statusElement = document.getElementById('modal-status');
  
  if (!provider || !key) {
    statusElement.innerHTML = '<p style="color: var(--error);">Please select a provider and enter an API key.</p>';
    return;
  }
  
  statusElement.innerHTML = '<p style="color: var(--text-secondary);">Saving...</p>';
  
  try {
    const response = await fetch(`${SETTINGS_API_BASE_URL}/keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, key })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save API key');
    }
    
    statusElement.innerHTML = '<p style="color: #4ade80;">✓ API key saved successfully!</p>';
    
    // Close modal and refresh list after a short delay
    setTimeout(() => {
      closeAddAPIKeyModal();
      loadAPIKeys();
    }, 1000);
    
  } catch (error) {
    console.error('Error saving API key:', error);
    statusElement.innerHTML = `<p style="color: var(--error);">Error: ${error.message}</p>`;
  }
}

/**
 * Test an API key
 */
async function testAPIKey(provider) {
  const item = document.querySelector(`.api-key-item[data-provider="${provider}"]`);
  if (!item) return;
  
  const statusElement = item.querySelector('.api-key-status');
  const originalHTML = statusElement.innerHTML;
  
  statusElement.innerHTML = '<span style="color: var(--text-secondary);">Testing...</span>';
  
  try {
    const response = await fetch(`${SETTINGS_API_BASE_URL}/keys/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider })
    });
    
    const result = await response.json();
    
    if (result.success) {
      statusElement.innerHTML = '<span style="color: #4ade80;">✓ Connection successful!</span>';
      setTimeout(() => {
        statusElement.innerHTML = originalHTML;
      }, 3000);
    } else {
      statusElement.innerHTML = `<span style="color: var(--error);">✗ ${result.error || 'Connection failed'}</span>`;
      setTimeout(() => {
        statusElement.innerHTML = originalHTML;
      }, 5000);
    }
    
  } catch (error) {
    console.error('Error testing API key:', error);
    statusElement.innerHTML = `<span style="color: var(--error);">✗ ${error.message}</span>`;
    setTimeout(() => {
      statusElement.innerHTML = originalHTML;
    }, 5000);
  }
}

/**
 * Delete an API key
 */
async function deleteAPIKey(provider) {
  if (!confirm(`Delete API key for ${formatProviderName(provider)}?`)) {
    return;
  }
  
  try {
    const response = await fetch(`${SETTINGS_API_BASE_URL}/keys/${provider}`, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete API key');
    }
    
    // Refresh the list
    loadAPIKeys();
    
  } catch (error) {
    console.error('Error deleting API key:', error);
    alert(`Error: ${error.message}`);
  }
}

/**
 * Save budget settings
 */
async function saveBudgetSettings() {
  const dailyLimit = parseFloat(document.getElementById('budget-daily-limit').value);
  const monthlyLimit = parseFloat(document.getElementById('budget-monthly-limit').value);
  
  if (isNaN(dailyLimit) || isNaN(monthlyLimit) || dailyLimit <= 0 || monthlyLimit <= 0) {
    alert('Please enter valid budget limits.');
    return;
  }
  
  try {
    const response = await fetch(`${SETTINGS_API_BASE_URL}/budget`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        daily_limit: dailyLimit,
        monthly_limit: monthlyLimit
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to save budget settings');
    }
    
    // Refresh budget display
    loadBudgetStatus();
    
    // Show success message
    const button = document.getElementById('btn-save-budget');
    const originalText = button.textContent;
    button.textContent = '✓ Saved!';
    button.disabled = true;
    
    setTimeout(() => {
      button.textContent = originalText;
      button.disabled = false;
    }, 2000);
    
  } catch (error) {
    console.error('[Budget] Error saving budget:', error);
    alert(`Failed to save budget: ${error.message}`);
  }
}

/**
 * Helper: Get provider icon
 */
function getProviderIcon(provider) {
  const icons = {
    anthropic: '<i data-lucide="sparkles" style="width: 16px; height: 16px;"></i>',
    openai: '<i data-lucide="zap" style="width: 16px; height: 16px;"></i>',
    github: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" style="display: inline-block; vertical-align: middle;"><path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>',
    grok: '<i data-lucide="bot" style="width: 16px; height: 16px;"></i>',
    perplexity: '<i data-lucide="search" style="width: 16px; height: 16px;"></i>',
    gemini: '<i data-lucide="gem" style="width: 16px; height: 16px;"></i>',
    mistral: '<i data-lucide="wind" style="width: 16px; height: 16px;"></i>',
    openrouter: '<i data-lucide="route" style="width: 16px; height: 16px;"></i>'
  };
  return icons[provider] || '<i data-lucide="key" style="width: 16px; height: 16px;"></i>';
}

/**
 * Helper: Format provider name
 */
function formatProviderName(provider) {
  const names = {
    anthropic: 'Anthropic (Claude)',
    openai: 'OpenAI (GPT)',
    github: 'GitHub Models',
    grok: 'xAI (Grok)',
    perplexity: 'Perplexity AI',
    gemini: 'Google (Gemini)',
    mistral: 'Mistral AI',
    openrouter: 'OpenRouter'
  };
  return names[provider] || provider;
}

/**
 * Helper: Get provider API key documentation URL
 */
function getProviderKeyLink(provider) {
  const links = {
    anthropic: 'https://console.anthropic.com/settings/keys',
    openai: 'https://platform.openai.com/api-keys',
    github: 'https://github.com/settings/tokens?type=beta',
    grok: 'https://console.x.ai/',
    perplexity: 'https://www.perplexity.ai/settings/api',
    gemini: 'https://aistudio.google.com/app/apikey',
    mistral: 'https://console.mistral.ai/api-keys/',
    openrouter: 'https://openrouter.ai/keys'
  };
  return links[provider] || null;
}

/**
 * Helper: Get budget CSS class based on percentage
 */
function getBudgetClass(percentage) {
  if (percentage >= 100) return 'danger';
  if (percentage >= 80) return 'warning';
  return '';
}

// Initialize when DOM is ready
console.log('[API Keys Manager] Document state:', document.readyState);
if (document.readyState === 'loading') {
  console.log('[API Keys Manager] Document loading, adding DOMContentLoaded listener');
  document.addEventListener('DOMContentLoaded', initializeAPIKeysTab);
} else {
  console.log('[API Keys Manager] Document already loaded, calling initializeAPIKeysTab immediately');
  initializeAPIKeysTab();
}

// Export functions to global scope for app.js to access
window.loadAPIKeys = loadAPIKeys;
window.loadBudgetStatus = loadBudgetStatus;
console.log('[API Keys Manager] Functions exported to window:', typeof window.loadAPIKeys, typeof window.loadBudgetStatus);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    initializeAPIKeysTab,
    loadAPIKeys,
    loadBudgetStatus
  };
}

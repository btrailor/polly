// Polly Settings - JavaScript

// API Base URL
const API_BASE = '/api/settings';

// Provider format hints
const FORMAT_HINTS = {
    anthropic: '🔑 Format: sk-ant-api03-... • Get your key at https://console.anthropic.com/',
    openai: '🔑 Format: sk-... • Get your key at https://platform.openai.com/api-keys',
    github: '🔑 Format: ghp_... or github_pat_... • Get a token at https://github.com/settings/tokens',
    grok: '🔑 Format: xai-... • Get your key at https://console.x.ai/',
    perplexity: '🔑 Format: pplx-... • Get your key at https://www.perplexity.ai/settings/api',
    gemini: '🔑 Format: AI... • Get your key at https://aistudio.google.com/app/apikey',
    mistral: '🔑 Format: ... • Get your key at https://console.mistral.ai/'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    loadKeys();
    loadBudgetStatus();
    loadProviderInfo();
});

// Tab Management
function initializeTabs() {
    const sidebarItems = document.querySelectorAll('.sidebar-item');
    
    sidebarItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabName = item.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Update sidebar items
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Update page title
    const titles = {
        'keys': 'API Keys',
        'budget': 'Budget & Usage',
        'compression': 'Compression',
        'providers': 'Providers'
    };
    const subtitles = {
        'keys': 'Store API keys securely in your system keyring',
        'budget': 'Monitor spending and set budget limits',
        'compression': 'Configure automatic conversation compression',
        'providers': 'View provider information and capabilities'
    };
    document.getElementById('page-title').textContent = titles[tabName] || tabName;
    document.getElementById('page-subtitle').textContent = subtitles[tabName] || '';
    
    // Reload data for the tab
    if (tabName === 'keys') {
        loadKeys();
    } else if (tabName === 'budget') {
        loadBudgetStatus();
    } else if (tabName === 'compression') {
        loadCompressionSettings();
        loadCompressionStats();
    } else if (tabName === 'providers') {
        loadProviderInfo();
    }
}

// API Keys Management
async function loadKeys() {
    const container = document.getElementById('keys-list');
    container.innerHTML = '<div class="loading">Loading keys...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/keys`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to load keys');
        }
        
        displayKeys(data.keys);
    } catch (error) {
        container.innerHTML = `<div class="status-message error show">Failed to load keys: ${error.message}</div>`;
    }
}

function displayKeys(keys) {
    const container = document.getElementById('keys-list');
    
    if (keys.length === 0) {
        container.innerHTML = '<p class="hint">No API keys configured. Click "Add API Key" to get started.</p>';
        return;
    }
    
    container.innerHTML = keys.map(key => `
        <div class="key-item">
            <div class="key-info">
                <div class="key-provider">${key.provider.charAt(0).toUpperCase() + key.provider.slice(1)}</div>
                <div class="key-description">${key.description}</div>
                <div class="key-meta">
                    <span class="key-status ${key.is_set ? 'set' : 'not-set'}">
                        ${key.is_set ? '✓ Configured' : '✗ Not Set'}
                    </span>
                    ${key.storage_type ? `<span class="hint">Storage: ${getStorageIcon(key.storage_type)} ${key.storage_type}</span>` : ''}
                    ${key.last_accessed ? `<span class="hint">Last used: ${formatDate(key.last_accessed)}</span>` : ''}
                </div>
            </div>
            <div class="key-actions">
                ${key.is_set ? `
                    <button class="btn btn-small btn-secondary" onclick="testKey('${key.provider}')">Test</button>
                    <button class="btn btn-small btn-danger" onclick="deleteKey('${key.provider}')">Delete</button>
                ` : `
                    <button class="btn btn-small btn-primary" onclick="showAddKeyModalFor('${key.provider}')">Add Key</button>
                `}
            </div>
        </div>
    `).join('');
}

function getStorageIcon(type) {
    const icons = {
        'keyring': '🔐',
        'file': '📁',
        'environment': '🌍'
    };
    return icons[type] || '📦';
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Add Key Modal
function showAddKeyModal() {
    document.getElementById('add-key-modal').classList.add('show');
    document.getElementById('provider-select').value = '';
    document.getElementById('api-key-input').value = '';
    document.getElementById('key-format-hint').textContent = '';
    document.getElementById('save-status').classList.remove('show');
}

function showAddKeyModalFor(provider) {
    showAddKeyModal();
    document.getElementById('provider-select').value = provider;
    updateKeyFormatHint();
}

function closeAddKeyModal() {
    document.getElementById('add-key-modal').classList.remove('show');
}

function updateKeyFormatHint() {
    const provider = document.getElementById('provider-select').value;
    const hint = document.getElementById('key-format-hint');
    
    if (provider && FORMAT_HINTS[provider]) {
        hint.textContent = FORMAT_HINTS[provider];
    } else {
        hint.textContent = '';
    }
}

async function saveApiKey() {
    const provider = document.getElementById('provider-select').value;
    const key = document.getElementById('api-key-input').value;
    const statusEl = document.getElementById('save-status');
    
    if (!provider) {
        showStatus(statusEl, 'error', 'Please select a provider');
        return;
    }
    
    if (!key) {
        showStatus(statusEl, 'error', 'Please enter an API key');
        return;
    }
    
    showStatus(statusEl, 'warning', 'Saving and testing key...');
    
    try {
        const response = await fetch(`${API_BASE}/keys`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider, key})
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to save key');
        }
        
        if (data.validated) {
            showStatus(statusEl, 'success', `✓ Key saved and validated successfully!`);
            setTimeout(() => {
                closeAddKeyModal();
                loadKeys();
                showToast('API key added successfully!');
            }, 1500);
        } else {
            showStatus(statusEl, 'warning', `⚠️ Key saved but validation failed: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        showStatus(statusEl, 'error', `✗ Error: ${error.message}`);
    }
}

async function deleteKey(provider) {
    if (!confirm(`Delete ${provider} API key?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/keys/${provider}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.message || 'Failed to delete key');
        }
        
        showToast(`${provider} key deleted successfully`);
        loadKeys();
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function testKey(provider) {
    showToast(`Testing ${provider} connection...`);
    
    try {
        const response = await fetch(`${API_BASE}/keys/test`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({provider})
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Test failed');
        }
        
        const result = data.results[provider];
        if (result.valid) {
            showToast(`✓ ${provider} connection successful!`, 'success');
        } else {
            showToast(`✗ ${provider} connection failed: ${result.error}`, 'error');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Budget Management
async function loadBudgetStatus() {
    const statusContainer = document.getElementById('budget-status');
    const summaryContainer = document.getElementById('spending-summary');
    
    statusContainer.innerHTML = '<div class="loading">Loading budget...</div>';
    summaryContainer.innerHTML = '<div class="loading">Loading spending data...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/budget`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to load budget');
        }
        
        displayBudgetStatus(data.budget);
        displaySpendingSummary(data.spending);
        
        // Populate budget settings form
        document.getElementById('daily-limit').value = data.budget.daily.limit;
        document.getElementById('monthly-limit').value = data.budget.monthly.limit;
        document.getElementById('warn-threshold').value = data.budget.warn_threshold;
    } catch (error) {
        statusContainer.innerHTML = `<div class="status-message error show">Failed to load budget: ${error.message}</div>`;
    }
}

function displayBudgetStatus(budget) {
    const container = document.getElementById('budget-status');
    
    const dailyPercent = (budget.daily.spent / budget.daily.limit) * 100;
    const monthlyPercent = (budget.monthly.spent / budget.monthly.limit) * 100;
    
    container.innerHTML = `
        <div class="budget-item">
            <div class="budget-label">Daily Budget</div>
            <div class="budget-amount">$${budget.daily.spent.toFixed(2)} / $${budget.daily.limit.toFixed(2)}</div>
            <div class="hint">${budget.daily.remaining.toFixed(2)} remaining</div>
            <div class="budget-progress">
                <div class="budget-progress-bar ${getProgressClass(dailyPercent)}" style="width: ${Math.min(dailyPercent, 100)}%"></div>
            </div>
        </div>
        
        <div class="budget-item">
            <div class="budget-label">Monthly Budget</div>
            <div class="budget-amount">$${budget.monthly.spent.toFixed(2)} / $${budget.monthly.limit.toFixed(2)}</div>
            <div class="hint">${budget.monthly.remaining.toFixed(2)} remaining</div>
            <div class="budget-progress">
                <div class="budget-progress-bar ${getProgressClass(monthlyPercent)}" style="width: ${Math.min(monthlyPercent, 100)}%"></div>
            </div>
        </div>
    `;
}

function getProgressClass(percent) {
    if (percent >= 100) return 'danger';
    if (percent >= 80) return 'warning';
    return '';
}

function displaySpendingSummary(spending) {
    const container = document.getElementById('spending-summary');
    
    container.innerHTML = `
        <div class="spending-grid">
            <div class="spending-stat">
                <div class="spending-stat-value">$${spending.total_cost.toFixed(2)}</div>
                <div class="spending-stat-label">Total Cost</div>
            </div>
            <div class="spending-stat">
                <div class="spending-stat-value">${spending.total_requests}</div>
                <div class="spending-stat-label">Requests</div>
            </div>
            <div class="spending-stat">
                <div class="spending-stat-value">${(spending.total_tokens / 1000).toFixed(1)}K</div>
                <div class="spending-stat-label">Tokens</div>
            </div>
        </div>
        
        ${Object.keys(spending.by_provider).length > 0 ? `
            <div class="provider-breakdown">
                <h3>By Provider</h3>
                ${Object.entries(spending.by_provider).map(([provider, cost]) => `
                    <div class="provider-row">
                        <span>${provider.charAt(0).toUpperCase() + provider.slice(1)}</span>
                        <span>$${cost.toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
        ` : '<p class="hint">No spending data yet</p>'}
    `;
}

async function updateBudgetSettings() {
    const dailyLimit = parseFloat(document.getElementById('daily-limit').value);
    const monthlyLimit = parseFloat(document.getElementById('monthly-limit').value);
    const warnThreshold = parseInt(document.getElementById('warn-threshold').value);
    
    if (isNaN(dailyLimit) || isNaN(monthlyLimit) || isNaN(warnThreshold)) {
        showToast('Please enter valid numbers', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/budget`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                daily_limit: dailyLimit,
                monthly_limit: monthlyLimit,
                warn_threshold: warnThreshold / 100
            })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to update budget');
        }
        
        showToast('Budget settings updated successfully!', 'success');
        loadBudgetStatus();
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

// Provider Info
async function loadProviderInfo() {
    const container = document.getElementById('providers-info');
    container.innerHTML = '<div class="loading">Loading provider info...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/providers`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to load providers');
        }
        
        displayProviderInfo(data.providers);
    } catch (error) {
        container.innerHTML = `<div class="status-message error show">Failed to load providers: ${error.message}</div>`;
    }
}

function displayProviderInfo(providers) {
    const container = document.getElementById('providers-info');
    
    container.innerHTML = Object.entries(providers).map(([key, info]) => `
        <div class="provider-card">
            <h3>${info.name}</h3>
            <p>${info.description}</p>
            <span class="hint">Key Format: <code>${info.key_format}</code></span>
            <span class="hint">Environment Variable: <code>${info.env_var}</code></span>
        </div>
    `).join('');
}

// Compression Settings
async function loadCompressionSettings() {
    const settingsDiv = document.getElementById('compression-settings');
    
    try {
        const response = await fetch(`${API_BASE}/compression`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to load compression settings');
        }
        
        // Populate form
        document.getElementById('compression-enabled').checked = data.settings.enabled;
        document.getElementById('message-threshold').value = data.settings.message_threshold;
        document.getElementById('age-hours').value = data.settings.age_hours;
        document.getElementById('keep-recent').value = data.settings.keep_recent;
        document.getElementById('show-stats').checked = data.settings.show_stats;
        
        // Enable/disable settings based on enabled checkbox
        updateCompressionEnabled();
    } catch (error) {
        showToast(`Failed to load compression settings: ${error.message}`, 'error');
    }
}

function updateCompressionEnabled() {
    const enabled = document.getElementById('compression-enabled').checked;
    const settingsDiv = document.getElementById('compression-settings');
    const inputs = settingsDiv.querySelectorAll('input');
    
    inputs.forEach(input => {
        input.disabled = !enabled;
    });
    
    settingsDiv.style.opacity = enabled ? '1' : '0.5';
}

async function saveCompressionSettings() {
    const statusEl = document.getElementById('compression-save-status');
    
    const settings = {
        enabled: document.getElementById('compression-enabled').checked,
        message_threshold: parseInt(document.getElementById('message-threshold').value),
        age_hours: parseInt(document.getElementById('age-hours').value),
        keep_recent: parseInt(document.getElementById('keep-recent').value),
        show_stats: document.getElementById('show-stats').checked
    };
    
    // Validate
    if (isNaN(settings.message_threshold) || settings.message_threshold < 10) {
        showStatus(statusEl, 'error', 'Message threshold must be at least 10');
        return;
    }
    
    if (isNaN(settings.age_hours) || settings.age_hours < 1) {
        showStatus(statusEl, 'error', 'Age threshold must be at least 1 hour');
        return;
    }
    
    if (isNaN(settings.keep_recent) || settings.keep_recent < 5) {
        showStatus(statusEl, 'error', 'Must keep at least 5 recent messages');
        return;
    }
    
    showStatus(statusEl, 'warning', 'Saving settings...');
    
    try {
        const response = await fetch(`${API_BASE}/compression`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to save settings');
        }
        
        showStatus(statusEl, 'success', `✓ ${data.message}`);
        showToast('Compression settings saved successfully!', 'success');
        
        setTimeout(() => {
            statusEl.classList.remove('show');
        }, 5000);
    } catch (error) {
        showStatus(statusEl, 'error', `✗ Error: ${error.message}`);
    }
}

async function loadCompressionStats() {
    const container = document.getElementById('compression-stats');
    container.innerHTML = '<div class="loading">Loading statistics...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/compression/stats`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error('Failed to load stats');
        }
        
        displayCompressionStats(data.stats);
    } catch (error) {
        container.innerHTML = `<div class="status-message error show">Failed to load statistics: ${error.message}</div>`;
    }
}

function displayCompressionStats(stats) {
    const container = document.getElementById('compression-stats');
    
    if (stats.total_conversations === 0) {
        container.innerHTML = '<p class="hint">No compression data yet. Compression statistics will appear here once conversations are compressed.</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="spending-grid">
            <div class="spending-stat">
                <div class="spending-stat-value">${stats.total_conversations}</div>
                <div class="spending-stat-label">Conversations</div>
            </div>
            <div class="spending-stat">
                <div class="spending-stat-value">${(stats.total_saved_tokens / 1000).toFixed(1)}K</div>
                <div class="spending-stat-label">Tokens Saved</div>
            </div>
            <div class="spending-stat">
                <div class="spending-stat-value">${stats.savings_percent}%</div>
                <div class="spending-stat-label">Reduction</div>
            </div>
            <div class="spending-stat">
                <div class="spending-stat-value">${stats.average_ratio}x</div>
                <div class="spending-stat-label">Avg Ratio</div>
            </div>
        </div>
        
        ${stats.recent_compressions.length > 0 ? `
            <div class="provider-breakdown">
                <h3>Recent Compressions</h3>
                ${stats.recent_compressions.map(comp => `
                    <div class="provider-row">
                        <span class="hint">${formatDate(comp.created_at)}</span>
                        <span>${(comp.original_tokens / 1000).toFixed(1)}K → ${(comp.compressed_tokens / 1000).toFixed(1)}K tokens</span>
                        <span class="badge">${comp.ratio.toFixed(1)}x</span>
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;
}

// Utility Functions
function showStatus(element, type, message) {
    element.className = `status-message ${type} show`;
    element.textContent = message;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Close modal on outside click
window.onclick = function(event) {
    const modal = document.getElementById('add-key-modal');
    if (event.target === modal) {
        closeAddKeyModal();
    }
}

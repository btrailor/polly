/**
 * Polly - Preload Script
 * Exposes safe IPC methods to renderer process
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('polly', {
  // Store
  getStore: (key) => ipcRenderer.invoke('get-store', key),
  setStore: (key, value) => ipcRenderer.invoke('set-store', key, value),

  // Setup
  checkDependencies: () => ipcRenderer.invoke('check-dependencies'),
  runSetup: (options) => ipcRenderer.invoke('run-setup', options),

  // Server
  startServer: () => ipcRenderer.invoke('start-server'),
  stopServer: () => ipcRenderer.invoke('stop-server'),
  getServerStatus: () => ipcRenderer.invoke('get-server-status'),

  // Ollama
  startOllama: () => ipcRenderer.invoke('start-ollama'),
  stopOllama: () => ipcRenderer.invoke('stop-ollama'),
  getOllamaStatus: () => ipcRenderer.invoke('get-ollama-status'),

  // Knowledge
  indexKnowledge: (options) => ipcRenderer.invoke('index-knowledge', options),

  // Query
  query: (query, options) => ipcRenderer.invoke('query', query, options),

  // Dialogs
  selectDirectory: () => ipcRenderer.invoke('select-directory'),
  selectDirectories: () => ipcRenderer.invoke('select-directories'),
  chooseDirectory: () => ipcRenderer.invoke('select-directory'),  // Alias for compatibility

  // Config management
  getConfig: (key) => ipcRenderer.invoke('get-config', key),
  updateConfig: (key, value) => ipcRenderer.invoke('update-config', key, value),

  // External
  openExternal: (url) => ipcRenderer.invoke('open-external', url),

  // File Operations
  readFile: (filePath) => ipcRenderer.invoke('read-file', filePath),
  writeFile: (filePath, content) => ipcRenderer.invoke('write-file', filePath, content),

  // Secure credential storage
  setCredential: (account, password) => ipcRenderer.invoke('keytar-set', account, password),
  getCredential: (account) => ipcRenderer.invoke('keytar-get', account),
  deleteCredential: (account) => ipcRenderer.invoke('keytar-delete', account),

  // GitHub OAuth
  githubOAuth: () => ipcRenderer.invoke('github-oauth'),
  
  // Integration management
  integrationConnect: (integration, credentials) => ipcRenderer.invoke('integration-connect', integration, credentials),
  integrationSync: (integration, options) => ipcRenderer.invoke('integration-sync', integration, options),
  integrationStatus: () => ipcRenderer.invoke('integration-status'),

  // Conversation Management
  conversationManagerStatus: () => ipcRenderer.invoke('conversation-manager-status'),
  conversationCreate: (data) => ipcRenderer.invoke('conversation-create', data),
  conversationGet: (id, options) => ipcRenderer.invoke('conversation-get', id, options),
  conversationUpdate: (id, updates) => ipcRenderer.invoke('conversation-update', id, updates),
  conversationDelete: (id, soft) => ipcRenderer.invoke('conversation-delete', id, soft),
  conversationList: (options) => ipcRenderer.invoke('conversation-list', options),
  conversationSearch: (query, limit) => ipcRenderer.invoke('conversation-search', query, limit),
  conversationStarToggle: (id) => ipcRenderer.invoke('conversation-star-toggle', id),
  conversationPinToggle: (id) => ipcRenderer.invoke('conversation-pin-toggle', id),
  conversationSetTitle: (id, title) => ipcRenderer.invoke('conversation-set-title', id, title),
  conversationNeedsTitle: (id) => ipcRenderer.invoke('conversation-needs-title', id),
  conversationMigrate: (messages, title) => ipcRenderer.invoke('conversation-migrate', messages, title),
  conversationStats: () => ipcRenderer.invoke('conversation-stats'),
  conversationCleanup: () => ipcRenderer.invoke('conversation-cleanup'),
  conversationEnforceLimit: () => ipcRenderer.invoke('conversation-enforce-limit'),
  
  // Message Management
  messageAdd: (conversationId, role, content, metadata) => ipcRenderer.invoke('message-add', conversationId, role, content, metadata),
  messageList: (conversationId, limit, offset) => ipcRenderer.invoke('message-list', conversationId, limit, offset),
  
  // Category Management
  categoryList: () => ipcRenderer.invoke('category-list'),
  categoryCreate: (data) => ipcRenderer.invoke('category-create', data),

  // Events
  onServerStatus: (callback) => {
    ipcRenderer.on('server-status', (event, data) => callback(data));
  },
  onOllamaStatus: (callback) => {
    ipcRenderer.on('ollama-status', (event, data) => callback(data));
  },
  onSetupProgress: (callback) => {
    ipcRenderer.on('setup-progress', (event, data) => callback(data));
  },
  onIndexProgress: (callback) => {
    ipcRenderer.on('index-progress', (event, data) => callback(data));
  },
  onFocusQuery: (callback) => {
    ipcRenderer.on('focus-query', () => callback());
  }
});

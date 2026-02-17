/**
 * Polly - Renderer Process
 * Handles UI logic and IPC communication
 */

// API Configuration
const API_URL = "http://127.0.0.1:11436";

// Slash command cache (persona mode invocation)
let _slashCommandsCache = null;

/**
 * Default messages per command when user sends only /command (no additional text).
 * These explicitly invoke the persona mode so it doesn't get confused.
 */
const SLASH_COMMAND_DEFAULTS = {
  curriculum: "I want to create a structured curriculum. What topic or skill should we focus on?",
  "learning-path": "I want to create a structured curriculum. What topic or skill should we focus on?",
  teach: "I'd like to learn through guided dialogue. What topic should we explore?",
  socratic: "I'd like to learn through guided dialogue. What topic should we explore?",
  explain: "Please explain this concept. What would you like me to explain?",
  quiz: "I'm ready for a quiz. What topic should we test?",
  save: "Please save this conversation as a note in my knowledge base.",
  note: "Please save this conversation as a note in my knowledge base.",
  plan: "I'd like to create a plan. What would you like me to help plan?",
  build: "I'm ready to build. What should we create?",
};

/**
 * Parse slash command from message. Returns { persona, mode, userMessage } or null.
 * @param {string} message - Raw message (e.g. "/learning-path Create path for Python")
 * @returns {{ persona: string, mode: string|null, userMessage: string }|null}
 */
function parseSlashCommand(message) {
  const trimmed = message.trim();
  if (!trimmed.startsWith("/")) return null;
  const rest = trimmed.slice(1).trim();
  const spaceIdx = rest.indexOf(" ");
  const cmd = spaceIdx >= 0 ? rest.slice(0, spaceIdx).toLowerCase() : rest.toLowerCase();
  const userMsg = spaceIdx >= 0 ? rest.slice(spaceIdx).trim() : "";
  if (!cmd) return null;
  const resolved = resolveSlashCommand(cmd);
  if (!resolved) return null;
  const defaultMsg = SLASH_COMMAND_DEFAULTS[cmd];
  return {
    persona: resolved.persona,
    mode: resolved.mode || null,
    userMessage: userMsg || defaultMsg || "Continue",
  };
}

/**
 * Resolve command string to { persona, mode }. Uses cached commands from API.
 * @param {string} cmd - Command without leading / (e.g. "learning-path")
 * @returns {{ persona: string, mode: string|null }|null}
 */
function resolveSlashCommand(cmd) {
  const c = (cmd || "").toLowerCase().trim();
  if (!c) return null;
  // Use fallback when cache is empty (API failed or not yet called)
  if (!_slashCommandsCache || _slashCommandsCache.length === 0) {
    const fallback = {
      teach: { persona: "professor", mode: "socratic" },
      "learning-path": { persona: "professor", mode: "curriculum" },
      curriculum: { persona: "professor", mode: "curriculum" },
      explain: { persona: "professor", mode: "explain" },
      quiz: { persona: "professor", mode: "quiz" },
      save: { persona: "scribe", mode: "capture" },
      note: { persona: "scribe", mode: "capture" },
      plan: { persona: "architect", mode: "plan" },
      build: { persona: "architect", mode: "build" },
    };
    return fallback[c] || null;
  }
  for (const item of _slashCommandsCache) {
    if (item.command === c) return { persona: item.persona, mode: item.mode || null };
  }
  return null;
}

/**
 * Fetch and cache slash commands from API. Call on init or before autocomplete.
 * @returns {Promise<Array<{command:string,persona:string,mode:string,description:string}>>}
 */
async function fetchSlashCommands() {
  if (_slashCommandsCache) return _slashCommandsCache;
  try {
    const res = await fetch(`${API_URL}/persona/commands`);
    if (res.ok) {
      const data = await res.json();
      _slashCommandsCache = data.commands || [];
      return _slashCommandsCache;
    }
  } catch (e) {
    console.warn("[SlashCommands] Failed to fetch:", e);
  }
  // Keep cache null on failure so resolveSlashCommand uses the built-in fallback
  return [];
}

/**
 * Setup slash command autocomplete for chat inputs.
 * Shows dropdown when user types / and filters as they type.
 */
function setupSlashCommandAutocomplete() {
  const configs = [
    { inputId: "chat-input", dropdownId: "slash-command-autocomplete" },
  ];

  for (const { inputId, dropdownId } of configs) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) continue;

    let selectedIndex = 0;

    const hide = () => {
      dropdown.classList.add("hidden");
      dropdown.innerHTML = "";
    };

    const show = (items) => {
      if (!items.length) {
        hide();
        return;
      }
      selectedIndex = 0;
      dropdown.innerHTML = items
        .map(
          (item, i) =>
            `<div class="slash-command-item" data-index="${i}" data-cmd="${item.command}">
              <span class="cmd-name">/${item.command}</span>
              <span class="cmd-desc">${item.description || ""}</span>
            </div>`,
        )
        .join("");
      dropdown.classList.remove("hidden");
      dropdown.querySelectorAll(".slash-command-item").forEach((el, i) => {
        el.addEventListener("click", () => {
          const cmd = el.dataset.cmd;
          const pre = input.value.startsWith("/") ? "" : "/";
          const before = input.value.replace(/\/(\w*)$/, "").trimEnd();
          input.value = before ? `${before} /${cmd} ` : `/${cmd} `;
          input.focus();
          hide();
        });
      });
    };

    const update = async () => {
      const val = input.value;
      const match = val.match(/^\s*\/(\w*)$/);
      if (!match) {
        hide();
        return;
      }
      const prefix = (match[1] || "").toLowerCase();
      await fetchSlashCommands();
      const all = _slashCommandsCache || [];
      const filtered = prefix
        ? all.filter((c) => c.command.toLowerCase().startsWith(prefix))
        : all;
      show(filtered.slice(0, 10));
      selectedIndex = 0;
      const items = dropdown.querySelectorAll(".slash-command-item");
      items.forEach((el, i) => el.classList.toggle("selected", i === 0));
    };

    input.addEventListener("input", update);
    input.addEventListener("focus", () => {
      if (input.value.match(/^\s*\//)) update();
    });
    input.addEventListener("blur", () => {
      setTimeout(hide, 150);
    });

    dropdown.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        hide();
        input.focus();
      }
    });
  }
}

// State
let currentView = "setup";
let currentPage = "dashboard"; // Track current page for conversation context
let currentMode = "auto";
let setupStep = 1;
let codePaths = [];
let isServerRunning = false;
let isOllamaRunning = false;

// Conversation Management State
let currentConversationId = null; // Currently active conversation ID
let currentConversation = null; // Current conversation object with messages
let conversations = []; // List of all conversations
let categories = []; // Available categories
let needsMigration = false; // Flag for old data migration

// Agent Management State (agents = personas + custom; each agent has conversations)
const AGENTS_STORAGE_KEY = "polly-agents";
let agents = []; // { id, persona_name, display_name, icon, created_at }
let currentAgentId = "default"; // Currently active agent

// UI State Management (for smooth reloads)
let preservedUIState = {
  conversationId: null,
  scrollPosition: 0,
  timestamp: null,
};

// Global stats (populated from /polly/stats endpoint)
window.pollyStats = null;
let statsRetryCount = 0;
const MAX_STATS_RETRIES = 3;

/**
 * Get the effective page context for mental models scoring.
 * When the user is in the "chat" view, derive the page from the active
 * conversation's page_context rather than sending the literal string "chat"
 * (which no mental model knows about).
 * @returns {string} Effective page name for the backend
 */
function getEffectivePage() {
  if (currentPage === "chat" && currentConversation && currentConversation.page_context) {
    return currentConversation.page_context;
  }
  return currentPage;
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast: 'success', 'error', 'info', 'warning'
 */
function showToast(message, type = "info") {
  // For now, use console and alert for critical errors
  // In the future, this could be replaced with a proper toast UI component
  const prefix =
    {
      success: "✓",
      error: "✗",
      warning: "⚠",
      info: "ℹ",
    }[type] || "ℹ";

  console.log(`[${type.toUpperCase()}] ${message}`);

  // Only show alert for errors
  if (type === "error") {
    alert(`${prefix} ${message}`);
  }
}

/**
 * Polly IPC Bridge - Safe Initialization Guard
 *
 * This prevents crashes from accessing window.polly before Electron's contextBridge
 * has finished exposing it. Common during early initialization or rapid page loads.
 */
const PollyBridge = {
  _ready: false,
  _readyPromise: null,
  _maxWaitTime: 10000, // 10 seconds max wait
  _checkInterval: 50, // Check every 50ms

  /**
   * Wait for window.polly to be available
   * @returns {Promise<boolean>} True if ready, false if timeout
   */
  async waitForReady() {
    if (this._ready) return true;
    if (this._readyPromise) return this._readyPromise;

    this._readyPromise = new Promise((resolve) => {
      const startTime = Date.now();

      const checkReady = () => {
        if (typeof window.polly !== "undefined" && window.polly !== null) {
          this._ready = true;
          console.log("[PollyBridge] IPC bridge ready");
          resolve(true);
          return;
        }

        if (Date.now() - startTime > this._maxWaitTime) {
          console.error("[PollyBridge] Timeout waiting for IPC bridge");
          resolve(false);
          return;
        }

        setTimeout(checkReady, this._checkInterval);
      };

      checkReady();
    });

    return this._readyPromise;
  },

  /**
   * Safely call a window.polly method with automatic retry
   * @param {string} method - Method name (e.g., 'getStore', 'setStore')
   * @param {...any} args - Arguments to pass to the method
   * @returns {Promise<any>} Result or null if unavailable
   */
  async safeCall(method, ...args) {
    const ready = await this.waitForReady();

    if (!ready) {
      console.error(
        `[PollyBridge] Cannot call ${method}: IPC bridge not available`,
      );
      return null;
    }

    try {
      if (typeof window.polly[method] !== "function") {
        console.error(
          `[PollyBridge] Method ${method} not found on window.polly`,
        );
        return null;
      }

      return await window.polly[method](...args);
    } catch (error) {
      console.error(`[PollyBridge] Error calling ${method}:`, error);
      return null;
    }
  },

  /**
   * Check if the bridge is ready synchronously (non-blocking)
   * @returns {boolean}
   */
  isReady() {
    return (
      this._ready ||
      (typeof window.polly !== "undefined" && window.polly !== null)
    );
  },
};

/**
 * Safe API Fetch - Handles network errors gracefully
 * @param {string} url - URL to fetch
 * @param {object} options - Fetch options
 * @param {boolean} silent - If true, don't log connection errors (for startup retries)
 * @returns {Promise<{ok: boolean, data: any, error: string, isConnectionError: boolean}>}
 */
async function safeFetch(url, options = {}, silent = false) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      return {
        ok: false,
        data: null,
        error: `HTTP ${response.status}: ${response.statusText}`,
        isConnectionError: false,
      };
    }
    const data = await response.json();
    return { ok: true, data, error: null, isConnectionError: false };
  } catch (error) {
    const isConnectionError =
      error.message.includes("Failed to fetch") ||
      error.message.includes("ERR_CONNECTION_REFUSED");

    // Only log if not silent and not an expected connection error
    if (!silent && !isConnectionError) {
      console.warn(`[safeFetch] ${url} failed:`, error.message);
    }

    return {
      ok: false,
      data: null,
      error: error.message || "Network error",
      isConnectionError,
    };
  }
}

/**
 * Sync conversation messages to Python backend (integration-contracts).
 * Called when user opens/switches conversation or app restores; keeps Python buffer in sync with Electron.
 * @param {Array<{role: string, content: string}>} messages - Last N messages (e.g. slice(-50))
 * @param {string} [conversationId] - Optional conversation ID
 */
async function syncConversationToBackend(messages, conversationId = null) {
  const payload = {
    messages: (messages || []).map((m) => ({
      role: m.role || "user",
      content: m.content || "",
    })),
  };
  if (conversationId) payload.conversation_id = conversationId;
  const result = await safeFetch(`${API_URL}/polly/conversation/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }, true);
  if (!result.ok && !result.isConnectionError) {
    const is503 = (result.error || "").includes("503");
    if (is503) {
      console.warn("[ConversationSync] Backend not ready yet (503); will retry on next action.");
    } else {
      console.warn("[ConversationSync] Backend sync failed:", result.error);
    }
  }
}

/**
 * Error Boundary - Wrap async functions to prevent crashes
 * @param {Function} fn - Async function to wrap
 * @param {string} context - Context name for logging
 * @returns {Function} Wrapped function
 */
function withErrorBoundary(fn, context = "Unknown") {
  return async function (...args) {
    try {
      return await fn.apply(this, args);
    } catch (error) {
      console.error(`[ErrorBoundary:${context}] Caught error:`, error);
      showToast(`Error in ${context}: ${error.message}`, "error");
      return null;
    }
  };
}

const API_HEALTH_URL = "http://127.0.0.1:11436/health";

/**
 * Wait for the backend server to be reachable (e.g. after Electron has started it).
 * Polls /health until 200 or timeout. Reduces connection-refused noise during startup.
 * @param {{ timeoutMs?: number, intervalMs?: number }} options
 * @returns {Promise<boolean>} true if server responded, false on timeout
 */
function waitForServerReady(options = {}) {
  const timeoutMs = options.timeoutMs ?? 30000;
  const intervalMs = options.intervalMs ?? 500;
  const initialDelayMs = options.initialDelayMs ?? 1500;
  const start = Date.now();
  return new Promise((resolve) => {
    const tryOnce = () => {
      fetch(API_HEALTH_URL, { method: "GET" })
        .then((r) => {
          if (r.ok) {
            resolve(true);
            return;
          }
          schedule();
        })
        .catch(() => schedule());

      function schedule() {
        if (Date.now() - start >= timeoutMs) {
          resolve(false);
          return;
        }
        setTimeout(tryOnce, intervalMs);
      }
    };
    // Brief delay before first check so server has time to bind (reduces connection-refused spam)
    setTimeout(tryOnce, initialDelayMs);
  });
}

const POLLY_STATUS_URL = "http://127.0.0.1:11436/polly/status";

/**
 * Wait for Polly core to be initialized (not just server process).
 * Polls /polly/status until status === "ready" or timeout. Call after waitForServerReady()
 * so that conversation sync, persona state, mental models, etc. don't get 503.
 * @param {{ timeoutMs?: number, intervalMs?: number }} options
 * @returns {Promise<boolean>} true if Polly is ready, false on timeout or error
 */
function waitForPollyReady(options = {}) {
  const timeoutMs = options.timeoutMs ?? 120000;
  const intervalMs = options.intervalMs ?? 500;
  const start = Date.now();
  return new Promise((resolve) => {
    const tryOnce = () => {
      fetch(POLLY_STATUS_URL, { method: "GET" })
        .then((r) => r.ok ? r.json() : null)
        .then((data) => {
          if (data && data.status === "ready") {
            resolve(true);
            return;
          }
          if (data && data.status === "error") {
            console.warn("[Init] Polly initialization failed:", data.error);
            resolve(false);
            return;
          }
          schedule();
        })
        .catch(() => schedule());

      function schedule() {
        if (Date.now() - start >= timeoutMs) {
          console.warn("[Init] Polly ready check timed out");
          resolve(false);
          return;
        }
        setTimeout(tryOnce, intervalMs);
      }
    };
    tryOnce();
  });
}

/**
 * Check Polly initialization status
 * Shows/hides loading overlay based on Polly's ready state
 */
async function checkPollyInitStatus() {
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/status", {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      console.warn("[Init] Polly status check failed:", response.status);
      return;
    }

    const data = await response.json();

    const overlay = document.getElementById("polly-init-overlay");
    const statusText = document.getElementById("init-status-text");

    if (!overlay) return;

    if (data.initializing) {
      // Polly is still initializing
      overlay.classList.remove("hidden");
      statusText.textContent = "Loading AI models...";
    } else if (data.status === "ready") {
      // Polly is ready - hide overlay
      overlay.classList.add("hidden");
      console.log("[Init] Polly initialization complete");

      // Stop polling
      if (window.pollyStatusInterval) {
        clearInterval(window.pollyStatusInterval);
        window.pollyStatusInterval = null;
      }
    } else if (data.status === "error") {
      // Initialization failed
      overlay.classList.add("hidden");
      console.error("[Init] Polly initialization failed:", data.message);

      // Stop polling
      if (window.pollyStatusInterval) {
        clearInterval(window.pollyStatusInterval);
        window.pollyStatusInterval = null;
      }
    }
  } catch (error) {
    // Network error or server not ready yet - this is expected on startup
    console.debug(
      "[Init] Polly status check error (expected during startup):",
      error.message,
    );
  }
}

/**
 * Start polling Polly status
 * Polls every 500ms for first 10 seconds
 */
function startPollyStatusPolling() {
  console.log("[Init] Starting Polly status polling...");

  // Check immediately
  checkPollyInitStatus();

  // Poll every 500ms
  window.pollyStatusInterval = setInterval(checkPollyInitStatus, 500);

  // Stop polling after 10 seconds (initialization should be done by then)
  setTimeout(() => {
    if (window.pollyStatusInterval) {
      console.log("[Init] Stopping Polly status polling (timeout)");
      clearInterval(window.pollyStatusInterval);
      window.pollyStatusInterval = null;

      // Force hide overlay after timeout
      const overlay = document.getElementById("polly-init-overlay");
      if (overlay) {
        overlay.classList.add("hidden");
      }
    }
  }, 10000);
}

// DOM Ready
document.addEventListener("DOMContentLoaded", async () => {
  console.log("[Init] DOM loaded, starting initialization...");
  try {
    await initialize();
    console.log("[Init] Initialize complete, setting up event listeners...");
    setupEventListeners();
    console.log("[Init] Event listeners setup complete");
  } catch (error) {
    console.error("[Init] Error during initialization:", error);
  }
  // Populate model selector dropdowns (all providers: Anthropic, OpenAI, GitHub, Grok, Perplexity, Gemini, Mistral, OpenRouter)
  populateModelSelectors();
  // Initialize Lucide icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  // Initialize Mental Models Editor (after server is ready, to avoid connection-refused noise)
  if (typeof MentalModelsEditor !== "undefined") {
    MentalModelsEditor.init();
  }

  // Initialize Template Gallery (Phase 16e)
  if (typeof TemplateGallery !== "undefined") {
    console.log("[Init] Initializing TemplateGallery...");
    await TemplateGallery.init();
    // Make globally available
    window.TemplateGallery = TemplateGallery;
    console.log("[Init] TemplateGallery initialized");
  }

  // Initialize Question Form (Phase 16c)
  if (typeof QuestionForm !== "undefined") {
    console.log("[Init] Initializing QuestionForm...");
    QuestionForm.init();
    // Make globally available
    window.QuestionForm = QuestionForm;
    console.log("[Init] QuestionForm initialized");
  }

  // Initialize Preview Modal (Phase 16c/16e)
  if (typeof PreviewModal !== "undefined") {
    console.log("[Init] Initializing PreviewModal...");
    PreviewModal.init();
    // Make globally available
    window.PreviewModal = PreviewModal;
    console.log("[Init] PreviewModal initialized");
  }

  // Start polling Polly initialization status
  startPollyStatusPolling();
});

/**
 * Initialize the app
 */
const initialize = withErrorBoundary(async function () {
  console.log("[Init] Waiting for Polly IPC bridge...");

  const bridgeReady = await PollyBridge.waitForReady();

  if (!bridgeReady) {
    showToast(
      "Failed to initialize Polly IPC bridge. Please restart the app.",
      "error",
    );
    return;
  }

  console.log("[Init] IPC bridge ready, starting initialization...");

  // Check if setup is complete
  const setupComplete = await PollyBridge.safeCall("getStore", "setupComplete");

  if (setupComplete) {
    // Wait for backend to be reachable before any API calls (avoids connection-refused flood)
    console.log("[Init] Waiting for backend server...");
    const serverReady = await waitForServerReady();
    if (serverReady) {
      console.log("[Init] Backend server ready");
      // Wait for Polly core to be initialized so sync/persona/mental-models don't get 503
      console.log("[Init] Waiting for Polly to be ready...");
      const pollyReady = await waitForPollyReady();
      if (pollyReady) {
        console.log("[Init] Polly ready");
      } else {
        console.warn("[Init] Polly not ready within timeout; continuing anyway (will retry on use)");
      }
    } else {
      console.warn("[Init] Backend server not ready within timeout; continuing anyway");
    }

    showView("dashboard");

    // Check both services with retries (services might be starting)
    let attempts = 0;
    const maxAttempts = 10;
    const checkWithRetry = async () => {
      await checkServerStatus();
      await checkOllamaStatus();

      if ((!isServerRunning || !isOllamaRunning) && attempts < maxAttempts) {
        attempts++;
        setTimeout(checkWithRetry, 1000);
      }
    };
    checkWithRetry();

    // Server already waited for above; load dashboard/knowledge soon
    setTimeout(async () => {
      await loadDashboardData();
      await loadKnowledgeData();
    }, 500);
  } else {
    showView("setup");
    await checkDependencies();
  }

  // Load saved paths
  const vaultPath = await PollyBridge.safeCall("getStore", "vaultPath");
  const savedCodePaths = await PollyBridge.safeCall(
    "getStore",
    "codebasePaths",
  );

  if (vaultPath) {
    document.getElementById("vault-path").value = vaultPath;
    document.getElementById("obsidian-path").textContent = vaultPath;
  }

  if (savedCodePaths && savedCodePaths.length) {
    codePaths = savedCodePaths;
    renderCodePaths();
  }

  // Listen for server status updates
  window.polly.onServerStatus((data) => {
    updateServerStatus(data.running);
  });

  // Listen for Ollama status updates
  window.polly.onOllamaStatus((data) => {
    updateOllamaStatus(data.running);
  });

  // Periodically check server status (every 5 seconds)
  setInterval(async () => {
    const result = await window.polly.getServerStatus();
    updateServerStatus(result.running);

    const ollamaResult = await window.polly.getOllamaStatus();
    updateOllamaStatus(ollamaResult.running);
  }, 5000);

  // Periodically save UI state (every 10 seconds if there's an active conversation)
  setInterval(() => {
    if (currentConversationId) {
      saveUIState();
    }
  }, 10000);

  // Save UI state before window closes
  window.addEventListener("beforeunload", () => {
    if (currentConversationId) {
      saveUIState();
    }
  });

  // Listen for setup progress
  window.polly.onSetupProgress((data) => {
    updateSetupProgress(data);
  });

  // Listen for index progress
  window.polly.onIndexProgress((data) => {
    appendIndexLog(data.message);
  });

  // Focus query input on shortcut
  window.polly.onFocusQuery(() => {
    // Just focus the chat input in the right sidebar (no need to change view)
    document.getElementById("query-input").focus();
  });

  // Initialize conversations (after setup is complete)
  if (setupComplete) {
    // Load preserved UI state before initializing
    loadPreservedUIState();

    try {
      await initializeConversations();
    } catch (error) {
      console.error(
        "[Init] Failed to initialize conversations, but continuing:",
        error,
      );
      // Continue anyway - we'll create a conversation when user first sends a message
    }

    // Restore persona state if there's an active persona
    try {
      await restorePersonaState();
    } catch (error) {
      console.error("[Init] Failed to restore persona state:", error);
    }
  }
}, "initialize");

// ============================================
// Agent Management Functions
// ============================================

const DEFAULT_AGENTS = [
  { id: "default", persona_name: "", display_name: "Default", icon: "message-square", created_at: 0 },
  { id: "architect", persona_name: "architect", display_name: "Architect", icon: "layout", created_at: 0 },
  { id: "scribe", persona_name: "scribe", display_name: "Scribe", icon: "pen-line", created_at: 0 },
  { id: "professor", persona_name: "professor", display_name: "Professor", icon: "graduation-cap", created_at: 0 },
];

function saveAgents() {
  try {
    localStorage.setItem(AGENTS_STORAGE_KEY, JSON.stringify(agents));
    sessionStorage.setItem("polly-current-agent-id", currentAgentId);
  } catch (e) {
    console.error("Failed to save agents:", e);
  }
}

function loadAgents() {
  try {
    const raw = localStorage.getItem(AGENTS_STORAGE_KEY);
    if (raw) {
      agents = JSON.parse(raw);
      if (!Array.isArray(agents) || agents.length === 0) agents = [...DEFAULT_AGENTS];
    } else {
      agents = [...DEFAULT_AGENTS];
      saveAgents();
    }
    const savedId = sessionStorage.getItem("polly-current-agent-id");
    if (savedId && agents.some((a) => a.id === savedId)) currentAgentId = savedId;
  } catch (e) {
    console.error("Failed to load agents:", e);
    agents = [...DEFAULT_AGENTS];
  }
}

function initializeAgents() {
  loadAgents();
  saveAgents();
}

function createAgent(personaName, displayName) {
  const id = "agent-" + Date.now();
  const agent = {
    id,
    persona_name: personaName || "",
    display_name: displayName || personaName || "New Agent",
    icon: personaName === "architect" ? "layout" : personaName === "scribe" ? "pen-line" : personaName === "professor" ? "graduation-cap" : "message-square",
    created_at: Date.now(),
  };
  agents.push(agent);
  saveAgents();
  return agent;
}

function deleteAgent(agentId) {
  if (agentId === "default" || ["architect", "scribe", "professor"].includes(agentId)) return;
  agents = agents.filter((a) => a.id !== agentId);
  if (currentAgentId === agentId) currentAgentId = "default";
  saveAgents();
}

function getAgentById(agentId) {
  return agents.find((a) => a.id === agentId) || DEFAULT_AGENTS[0];
}

async function getAgentConversations(agentId) {
  const list = await window.polly.conversationList({ agent_id: agentId || "default" });
  return list || [];
}

async function switchToAgent(agentId) {
  currentAgentId = agentId || "default";
  saveAgents();
  const agent = getAgentById(agentId);
  if (agent && agent.persona_name) {
    try {
      const activateResponse = await fetch(API_URL + "/persona/activate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ persona_name: agent.persona_name }),
      });
      const activateData = await activateResponse.json();
      if (activateData.success && activateData.state && activateData.state.introduction) {
        const formattedIntro = formatResponse(activateData.state.introduction);
        addMessageToUI("assistant", formattedIntro);
        await addMessageToConversation("assistant", activateData.state.introduction);
      }
    } catch (e) {
      console.warn("Persona activate failed:", e);
    }
  }
  const convos = await getAgentConversations(agentId);
  conversations = convos;
  if (typeof renderConversationList === "function") renderConversationList();
  if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
  if (typeof renderChatTabs === "function") renderChatTabs();
  if (conversations.length > 0) {
    await switchToConversation(conversations[0].id);
  } else {
    currentConversationId = null;
    currentConversation = null;
    clearChat();
    await createNewConversation();
  }
  const personaSelect = document.getElementById("chat-persona-select");
  if (personaSelect && agent) personaSelect.value = agent.persona_name || "";
}

// ============================================
// Conversation Management Functions
// ============================================

/**
 * Initialize conversation system
 */
async function initializeConversations() {
  try {
    initializeAgents();

    // Check ConversationManager status
    const status = await window.polly.conversationManagerStatus();
    console.log("ConversationManager status:", status);

    if (!status.initialized) {
      throw new Error("ConversationManager not initialized: " + status.error);
    }

    // Load categories
    categories = await window.polly.categoryList();

    // Check if we need to migrate old data
    const oldHistory = localStorage.getItem("conversationHistory");
    if (oldHistory) {
      needsMigration = true;
      await migrateOldConversation(JSON.parse(oldHistory));
      localStorage.removeItem("conversationHistory");
    }

    // Load conversations for current agent only
    conversations = await window.polly.conversationList({
      agent_id: (currentAgentId != null && currentAgentId !== "") ? currentAgentId : "default",
    });

    // Determine which conversation to load
    let targetConversationId = null;

    // First priority: preserved UI state (from previous session)
    if (preservedUIState.conversationId) {
      const exists = conversations.find(
        (c) => c.id === preservedUIState.conversationId,
      );
      if (exists) {
        targetConversationId = preservedUIState.conversationId;
        console.log(
          "[Init] Restoring conversation from preserved state:",
          targetConversationId,
        );
      }
    }

    // Second priority: most recent conversation
    if (!targetConversationId && conversations.length > 0) {
      targetConversationId = conversations[0].id;
    }

    // If no conversations exist, create a new one
    if (!targetConversationId) {
      await createNewConversation();
    } else {
      // Load the target conversation (will restore scroll position if preserved)
      await switchToConversation(targetConversationId, { restoreScroll: true });
    }

    // Render the conversation list and agents sidebar
    renderConversationList();
    if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
    if (typeof renderChatTabs === "function") renderChatTabs();

    console.log("Conversations initialized:", conversations.length);
  } catch (error) {
    console.error("Failed to initialize conversations:", error);
    // Create a fallback conversation
    await createNewConversation();
    renderConversationList();
  }
}

/**
 * Switch to a different conversation
 */
async function switchToConversation(conversationId, options = {}) {
  try {
    const { restoreScroll = false } = options;

    // Save current scroll position before switching
    if (currentConversationId) {
      saveUIState();
    }

    // Check if we're already viewing this conversation (reload scenario)
    const isSameConversation = currentConversationId === conversationId;

    // Load conversation with messages
    currentConversation = await window.polly.conversationGet(conversationId);
    currentConversationId = conversationId;

    // Sync to Python backend so compression/learning use same history (integration-contracts)
    const messages = currentConversation?.messages || [];
    await syncConversationToBackend(messages.slice(-50), conversationId);

    // Only clear and re-render if switching to a different conversation
    // or if there are no messages in the UI
    const container = getChatMessagesContainer();
    const hasMessagesInUI = container && container.children.length > 0;

    if (!isSameConversation || !hasMessagesInUI) {
      // Clear chat and render messages
      clearChat();
      renderConversationMessages();
    } else {
      console.log(
        "[Switch] Same conversation reload, skipping clear/re-render",
      );
    }

    // Restore scroll position if requested and available
    if (restoreScroll && preservedUIState.scrollPosition > 0) {
      setTimeout(() => {
        if (container) {
          container.scrollTop = preservedUIState.scrollPosition;
          console.log(
            "[Switch] Restored scroll position:",
            preservedUIState.scrollPosition,
          );
        }
      }, 100); // Small delay to ensure DOM is ready
    }

    // Update conversation list and agents sidebar to show active state
    renderConversationList(
      document.getElementById("conversations-search-input")?.value || "",
    );
    if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
    if (typeof renderChatTabs === "function") renderChatTabs();

    // Update active chat title and page indicator in sidebar
    const activeChatTitle = document.getElementById("active-chat-title");
    const activeChatPage = document.getElementById("active-chat-page");

    if (activeChatTitle && currentConversation) {
      activeChatTitle.textContent = currentConversation.title;

      if (activeChatPage && currentConversation.page_context) {
        activeChatPage.textContent = `(${getPageName(currentConversation.page_context)})`;
        activeChatPage.style.display = "inline";
      } else if (activeChatPage) {
        activeChatPage.textContent = "";
        activeChatPage.style.display = "none";
      }
    }

    console.log("Switched to conversation:", conversationId);
  } catch (error) {
    console.error("Failed to switch conversation:", error);
  }
}

/**
 * Clear chat messages from UI
 */
function clearChat() {
  const container = getChatMessagesContainer();
  if (container) {
    container.innerHTML = "";
  }
}

/**
 * Render all messages from current conversation
 */
function renderConversationMessages() {
  if (!currentConversation || !currentConversation.messages) {
    return;
  }

  currentConversation.messages.forEach((msg) => {
    if (msg.role !== "system") {
      const formattedContent =
        msg.role === "assistant" ? formatResponse(msg.content) : msg.content;
      addMessageToUI(msg.role, formattedContent);
    }
  });
}

/**
 * Get messages from current conversation
 * @returns {Array} Array of message objects
 */
function getCurrentConversationMessages() {
  if (!currentConversation || !currentConversation.messages) {
    return [];
  }
  return currentConversation.messages;
}

/**
 * Add a message to the current conversation
 */
async function addMessageToConversation(role, content) {
  try {
    // Add to database
    const message = await window.polly.messageAdd(
      currentConversationId,
      role,
      content,
    );

    // Add to local conversation object
    if (!currentConversation.messages) {
      currentConversation.messages = [];
    }
    currentConversation.messages.push(message);
    currentConversation.message_count++;
    
    // Update timestamp to current time (matches database update)
    const now = Date.now();
    currentConversation.updated_at = now;
    currentConversation.last_message_at = now;
    
    // Update the conversation in the conversations array so timestamps refresh in sidebar
    const convIndex = conversations.findIndex(c => c.id === currentConversationId);
    if (convIndex !== -1) {
      conversations[convIndex].updated_at = now;
      conversations[convIndex].last_message_at = now;
      conversations[convIndex].message_count = currentConversation.message_count;
      
      // Re-render conversation list to update timestamps
      if (typeof renderConversationList === "function") {
        renderConversationList();
      }
    }

    // Check if needs auto-titling (after 3 messages)
    if (
      currentConversation.message_count >= 3 &&
      !currentConversation.auto_titled
    ) {
      const needsTitle = await window.polly.conversationNeedsTitle(
        currentConversationId,
      );
      if (needsTitle) {
        await generateConversationTitle();
      }
    }

    return message;
  } catch (error) {
    console.error("Failed to add message:", error);
    throw error;
  }
}

/**
 * Save UI state to localStorage for smooth reloads
 */
function saveUIState() {
  const container = getChatMessagesContainer();
  const state = {
    conversationId: currentConversationId,
    scrollPosition: container ? container.scrollTop : 0,
    timestamp: Date.now(),
  };

  try {
    localStorage.setItem("polly-ui-state", JSON.stringify(state));
    preservedUIState = state;
    console.log("[UI State] Saved:", state);
  } catch (error) {
    console.error("[UI State] Failed to save:", error);
  }
}

/**
 * Load preserved UI state from localStorage
 */
function loadPreservedUIState() {
  try {
    const saved = localStorage.getItem("polly-ui-state");
    if (saved) {
      const state = JSON.parse(saved);

      // Only use state if less than 1 hour old (prevent stale state)
      const age = Date.now() - (state.timestamp || 0);
      if (age < 3600000) {
        // 1 hour
        preservedUIState = state;
        console.log("[UI State] Loaded:", state);
      } else {
        console.log("[UI State] Discarded stale state (age:", age, "ms)");
        localStorage.removeItem("polly-ui-state");
      }
    }
  } catch (error) {
    console.error("[UI State] Failed to load:", error);
  }
}

/**
 * Clear preserved UI state
 */
function clearPreservedUIState() {
  preservedUIState = {
    conversationId: null,
    scrollPosition: 0,
    timestamp: null,
  };
  localStorage.removeItem("polly-ui-state");
}

/**
 * Generate title for current conversation using LLM
 */
async function generateConversationTitle() {
  try {
    // Get first few messages for context
    const messages = currentConversation.messages.slice(0, 4);
    const context = messages.map((m) => `${m.role}: ${m.content}`).join("\n");

    // Use the query endpoint to generate a title
    const prompt = `Based on this conversation, generate a short, descriptive title (max 50 characters):\n\n${context}\n\nTitle:`;
    const result = await window.polly.query(prompt, { mode: "auto" });

    if (result.success) {
      let title = result.result.response.trim();
      // Clean up the title
      title = title.replace(/^["']|["']$/g, ""); // Remove quotes
      title = title.substring(0, 60); // Limit length

      // Update in database
      await window.polly.conversationSetTitle(currentConversationId, title);
      currentConversation.title = title;
      currentConversation.auto_titled = true;

      console.log("Generated title:", title);
    }
  } catch (error) {
    console.error("Failed to generate title:", error);
  }
}

/**
 * Create a new conversation
 * @param {Object} options - Creation options
 * @param {string} options.page_context - Page context (optional, defaults to currentPage)
 * @returns {Object} Created conversation
 */
async function createNewConversation(options = {}) {
  try {
    const conversation = await window.polly.conversationCreate({
      title: "New conversation",
      page_context: options.page_context || currentPage,
      category_id: options.category_id || "uncategorized",
      agent_id: options.agent_id || currentAgentId,
    });

    conversations.unshift(conversation);

    if (typeof renderConversationList === "function") renderConversationList();
    if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
    if (typeof renderChatTabs === "function") renderChatTabs();

    await switchToConversation(conversation.id);

    return conversation;
  } catch (error) {
    console.error("Failed to create conversation:", error);
    throw error;
  }
}

/**
 * Setup settings tabs
 */
function setupSettingsTabs() {
  const tabButtons = document.querySelectorAll(".settings-tab-btn");
  const tabContents = document.querySelectorAll(".settings-tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetTab = button.dataset.tab;

      // Update button states
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");

      // Update content visibility
      tabContents.forEach((content) => {
        if (content.id === `tab-${targetTab}`) {
          content.classList.remove("hidden");
        } else {
          content.classList.add("hidden");
        }
      });

      // Load domains config when switching to domains tab
      if (targetTab === "domains") {
        loadDomainsConfig();
      }

      // Load routing settings when switching to routing tab
      if (targetTab === "routing") {
        loadRoutingSettings();
        loadRoutingStats();
      }

      // Load compression settings when switching to compression tab
      if (targetTab === "compression") {
        loadCompressionSettings();
        loadCompressionStats();
      }

      // Load mental models when switching to mental models tab (Phase 14)
      if (targetTab === "mental-models") {
        loadMentalModels();
        refreshMentalModelsStats();
      }

      // Load dedup settings when switching to advanced tab (Phase 21)
      if (targetTab === "advanced") {
        loadDedupSettings();
      }

      // Load API keys when switching to api-keys tab
      if (targetTab === "api-keys") {
        console.log("[Settings Tab] Switched to API Keys tab");
        console.log("[Settings Tab] loadAPIKeys type:", typeof loadAPIKeys);
        console.log(
          "[Settings Tab] loadBudgetStatus type:",
          typeof loadBudgetStatus,
        );
        if (typeof loadAPIKeys === "function") {
          console.log("[Settings Tab] Calling loadAPIKeys()");
          loadAPIKeys();
        }
        if (typeof loadBudgetStatus === "function") {
          console.log("[Settings Tab] Calling loadBudgetStatus()");
          loadBudgetStatus();
        }
      }
    });
  });
}

// ============================================
// Conversation UI Functions
// ============================================

/**
 * Render the conversation list in the sidebar
 */
function renderConversationList(searchQuery = "") {
  const listEl = document.getElementById("conversations-list");

  // Check if element exists (it may not exist on all views)
  if (!listEl) {
    return; // Silently return - this is expected on views without conversation list
  }

  if (!conversations || conversations.length === 0) {
    listEl.innerHTML = `
      <div class="conversations-empty">
        <i data-lucide="message-square" style="width: 32px; height: 32px;"></i>
        <p>No conversations yet</p>
        <p style="margin-top: 8px;">Click "New Chat" to start</p>
      </div>
    `;
    if (typeof lucide !== "undefined") {
      setTimeout(() => lucide.createIcons(), 0);
    }
    return;
  }

  // Get page filter value
  const pageFilter = document.getElementById("page-filter")?.value || "all";

  // Filter conversations by page context
  let filteredConvs = conversations;
  if (pageFilter === "current") {
    filteredConvs = filteredConvs.filter((c) => c.page_context === currentPage);
  } else if (pageFilter && pageFilter !== "all" && pageFilter !== "") {
    filteredConvs = filteredConvs.filter((c) => c.page_context === pageFilter);
  }

  // Filter by search query
  if (searchQuery) {
    filteredConvs = filteredConvs.filter((c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()),
    );
  }

  // Group by category
  const grouped = {};
  filteredConvs.forEach((conv) => {
    const catId = conv.category_id || "uncategorized";
    if (!grouped[catId]) {
      grouped[catId] = [];
    }
    grouped[catId].push(conv);
  });

  // Render groups
  listEl.innerHTML = "";

  Object.entries(grouped).forEach(([catId, convs]) => {
    const category = categories.find((c) => c.id === catId) || {
      id: "uncategorized",
      name: "Uncategorized",
      icon: "message-square",
      color: "#CCCCCC",
    };

    const groupEl = document.createElement("div");
    groupEl.className = "conversation-category";
    groupEl.dataset.category = catId;

    groupEl.innerHTML = `
      <div class="category-header">
        <div class="category-name">
          <i data-lucide="${category.icon}" class="category-icon" style="width: 14px; height: 14px;"></i>
          <span>${category.name}</span>
          <span class="category-count">(${convs.length})</span>
        </div>
        <i data-lucide="chevron-down" class="category-toggle"></i>
      </div>
      <div class="category-conversations">
        ${convs.map((conv) => createConversationItemHTML(conv)).join("")}
      </div>
    `;

    listEl.appendChild(groupEl);

    // Add category toggle listener
    const header = groupEl.querySelector(".category-header");
    header.addEventListener("click", () => toggleCategory(catId));
  });

  // Add conversation click listeners
  listEl.querySelectorAll(".conversation-item").forEach((item) => {
    const convId = item.dataset.id;

    item.addEventListener("click", async (e) => {
      if (!e.target.closest(".conversation-menu-btn")) {
        // Switch to conversation (displays in sidebar automatically)
        await switchToConversation(convId);
      }
    });

    // Context menu
    item.addEventListener("contextmenu", (e) => {
      e.preventDefault();
      showConversationContextMenu(convId, e.clientX, e.clientY);
    });

    // Menu button
    const menuBtn = item.querySelector(".conversation-menu-btn");
    if (menuBtn) {
      menuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const rect = menuBtn.getBoundingClientRect();
        showConversationContextMenu(convId, rect.right, rect.bottom);
      });
    }
  });

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }
}

/**
 * Render the agents sidebar: agent list with nested conversations for current agent
 */
function renderAgentsSidebar() {
  const listEl = document.getElementById("agents-list");
  if (!listEl) return;

  const currentAgent = getAgentById(currentAgentId);

  listEl.innerHTML = agents
    .map((agent) => {
      const isActive = agent.id === currentAgentId;
      const icon = agent.icon || "message-square";
      const convs =
        isActive && Array.isArray(conversations)
          ? conversations
          : [];
      const convsHtml =
        isActive && convs.length > 0
          ? `<div class="agent-conversations">
               ${convs
                 .map(
                   (c) =>
                     `<div class="agent-conversation-item ${
                       c.id === currentConversationId ? "active" : ""
                     }" data-conversation-id="${c.id}" title="${(c.title || "").replace(/"/g, "&quot;")}">
                    <i data-lucide="message-circle" style="width: 12px; height: 12px;"></i>
                    <span class="agent-conversation-title">${escapeHtml((c.title || "New conversation").slice(0, 24))}${(c.title || "").length > 24 ? "…" : ""}</span>
                    <button type="button" class="agent-conversation-menu-btn" aria-label="Conversation options" data-conversation-id="${c.id}"><i data-lucide="more-vertical" style="width: 14px; height: 14px;"></i></button>
                  </div>`
                 )
                 .join("")}
             </div>`
          : "";
      return `
        <div class="agent-item ${isActive ? "active" : ""}" data-agent-id="${escapeHtml(agent.id)}">
          <div class="agent-row">
            <i data-lucide="${icon}" class="agent-icon" style="width: 16px; height: 16px;"></i>
            <span class="agent-name">${escapeHtml(agent.display_name)}</span>
          </div>
          ${convsHtml}
        </div>
      `;
    })
    .join("");

  listEl.querySelectorAll(".agent-item").forEach((item) => {
    const agentId = item.dataset.agentId;
    if (!agentId) return;
    const agentRow = item.querySelector(".agent-row");
    if (agentRow) {
      agentRow.addEventListener("click", () => switchToAgent(agentId));
    }
  });

  listEl.querySelectorAll(".agent-conversation-item").forEach((item) => {
    const convId = item.dataset.conversationId;
    if (!convId) return;
    item.addEventListener("click", (e) => {
      if (e.target.closest(".agent-conversation-menu-btn")) return;
      e.stopPropagation();
      switchToConversation(convId);
    });
  });

  listEl.querySelectorAll(".agent-conversation-menu-btn").forEach((btn) => {
    const convId = btn.dataset.conversationId;
    if (!convId) return;
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const rect = btn.getBoundingClientRect();
      showConversationContextMenu(convId, rect.right, rect.bottom);
    });
  });

  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }
}

/**
 * Render chat tabs for the current agent's conversations
 */
function renderChatTabs() {
  const container = document.getElementById("chat-tabs");
  if (!container) return;

  const maxTabs = 12;
  const convos = (conversations || []).slice(0, maxTabs);

  container.innerHTML =
    convos
      .map((c) => {
        const title = (c.title || "New conversation").slice(0, 20) + ((c.title || "").length > 20 ? "…" : "");
        const isActive = c.id === currentConversationId;
        return `
        <button type="button" class="chat-tab ${isActive ? "active" : ""}" data-conversation-id="${escapeHtml(c.id)}" title="${escapeHtml(c.title || "New conversation")}">
          <span class="chat-tab-label">${escapeHtml(title)}</span>
          <button type="button" class="tab-close" aria-label="Close" data-conversation-id="${escapeHtml(c.id)}"><i data-lucide="x" style="width: 12px; height: 12px;"></i></button>
        </button>
      `;
      })
      .join("") +
    `<button type="button" class="chat-tab-new" aria-label="New conversation"><i data-lucide="plus" style="width: 14px; height: 14px;"></i></button>`;

  container.querySelectorAll(".chat-tab").forEach((tab) => {
    const convId = tab.dataset.conversationId;
    if (!convId) return;
    tab.addEventListener("click", (e) => {
      if (!e.target.closest(".tab-close")) switchToConversation(convId);
    });
    const closeBtn = tab.querySelector(".tab-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const idx = conversations.findIndex((c) => c.id === convId);
        if (conversations.length > 1 && idx >= 0) {
          const next = idx > 0 ? conversations[idx - 1] : conversations[idx + 1];
          if (next) switchToConversation(next.id);
        }
      });
    }
  });

  const newTabBtn = container.querySelector(".chat-tab-new");
  if (newTabBtn) {
    newTabBtn.addEventListener("click", () => createNewConversation());
  }

  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }
}

function escapeHtml(str) {
  if (typeof str !== "string") return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Open the new-agent dialog (modal).
 */
function openNewAgentDialog() {
  const modal = document.getElementById("new-agent-modal");
  if (!modal) return;
  const personaSelect = document.getElementById("new-agent-persona");
  const displayNameInput = document.getElementById("new-agent-display-name");
  if (displayNameInput) displayNameInput.value = "";
  if (personaSelect) personaSelect.value = "";
  modal.classList.remove("hidden");
  modal.setAttribute("aria-hidden", "false");
  if (displayNameInput) displayNameInput.focus();
}

/**
 * Create agent from the new-agent modal form and switch to it.
 */
function submitNewAgentFromDialog() {
  const personaSelect = document.getElementById("new-agent-persona");
  const displayNameInput = document.getElementById("new-agent-display-name");
  const persona = personaSelect ? personaSelect.value : "";
  const displayName = (displayNameInput && displayNameInput.value.trim()) || (persona ? persona.charAt(0).toUpperCase() + persona.slice(1) : "New Agent");
  const agent = createAgent(persona, displayName);
  saveAgents();
  closeNewAgentDialog();
  renderAgentsSidebar();
  switchToAgent(agent.id);
}

/**
 * Close the new-agent modal (called from modal cancel/backdrop)
 */
function closeNewAgentDialog() {
  const modal = document.getElementById("new-agent-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
  }
}

/**
 * Get page icon for display
 */
function getPageIcon(pageContext) {
  const pageIcons = {
    dashboard: '<i data-lucide="home"></i>',
    knowledge: '<i data-lucide="network"></i>',
    notes: '<i data-lucide="file-text"></i>',
    learning: '<i data-lucide="brain"></i>',
    search: '<i data-lucide="search"></i>',
    patterns: '<i data-lucide="shapes"></i>',
    domains: '<i data-lucide="globe"></i>',
    settings: '<i data-lucide="settings"></i>',
  };
  return pageIcons[pageContext] || '<i data-lucide="message-circle"></i>';
}

/**
 * Format relative time (e.g., "2m ago", "3h ago", "5d ago")
 */
function formatRelativeTime(timestamp) {
  const now = Date.now();
  const then = new Date(timestamp).getTime();
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "now";
  if (diffMins < 60) return `${diffMins}m`;
  if (diffHours < 24) return `${diffHours}h`;
  if (diffDays < 30) return `${diffDays}d`;
  return `${Math.floor(diffDays / 30)}mo`;
}

/**
 * Get page display name
 */
function getPageName(pageContext) {
  const pageNames = {
    dashboard: "Dashboard",
    calendar: "Calendar",
    mail: "Mail",
    code: "Code",
    projects: "Projects",
    knowledge: "Knowledge",
    notes: "Notes",
    learning: "Learning",
    search: "Search",
    patterns: "Patterns",
    domains: "Domains",
    settings: "Settings",
  };
  return pageNames[pageContext] || "Global";
}

/**
 * Create HTML for a conversation item
 */
function createConversationItemHTML(conv) {
  const isActive = conv.id === currentConversationId;
  const date = formatConversationDate(conv.updated_at);
  const starred = conv.is_starred ? " starred" : "";

  // Check if conversation has mental models override
  const hasOverride = getMentalModelsOverride(conv.id) !== null;
  const overrideClass = hasOverride ? " has-override" : "";

  // Generate page badge if page_context exists
  const pageBadge = conv.page_context
    ? `<span class="page-badge" data-page="${conv.page_context}">${getPageName(conv.page_context)}</span>`
    : "";

  return `
    <div class="conversation-item${isActive ? " active" : ""}${starred}${overrideClass}" data-id="${conv.id}">
      <div class="conversation-header">
        <div class="conversation-title">${conv.title}</div>
        <button class="conversation-menu-btn">
          <i data-lucide="more-vertical" style="width: 14px; height: 14px;"></i>
        </button>
      </div>
      <div class="conversation-meta">
        ${pageBadge}
        <span class="conversation-message-count">
          <i data-lucide="message-circle" style="width: 10px; height: 10px;"></i>
          ${conv.message_count || 0}
        </span>
        <span class="conversation-date">${date}</span>
      </div>
    </div>
  `;
}

/**
 * Format conversation date for display
 */
function formatConversationDate(timestamp) {
  // Debug: Log the incoming timestamp to understand the issue
  if (timestamp === undefined || timestamp === null) {
    console.warn('[formatConversationDate] Undefined or null timestamp, using current time');
    return "just now";
  }
  
  const date = new Date(timestamp);
  
  // Check if date is valid
  if (isNaN(date.getTime())) {
    console.warn('[formatConversationDate] Invalid timestamp:', timestamp);
    return "just now";
  }
  
  const now = new Date();
  const diff = now - date;

  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;

  return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

/**
 * Toggle category collapsed state
 */
function toggleCategory(categoryId) {
  const groupEl = document.querySelector(
    `.conversation-category[data-category="${categoryId}"]`,
  );
  if (groupEl) {
    groupEl.classList.toggle("collapsed");
  }
}

/**
 * Show context menu for conversation actions
 */
function showConversationContextMenu(conversationId, x, y) {
  const menu = document.getElementById("conversation-context-menu");
  const conv = conversations.find((c) => c.id === conversationId);

  if (!conv || !menu) {
    console.log("showConversationContextMenu: missing required elements", {
      conv: !!conv,
      menu: !!menu,
    });
    return;
  }

  // Update star button text if available
  const starBtn = menu.querySelector('[data-action="star"]');
  if (starBtn) {
    // Look for icon - could be <i> or <svg> after Lucide transformation
    let starIcon = starBtn.querySelector("i");
    if (!starIcon) {
      starIcon = starBtn.querySelector("svg");
    }
    const starText = starBtn.querySelector("span");

    if (starText) {
      // Update the icon's data-lucide attribute (will be re-rendered by lucide.createIcons())
      if (starIcon) {
        if (conv.is_starred) {
          starIcon.setAttribute("data-lucide", "star-off");
          starText.textContent = "Unstar";
        } else {
          starIcon.setAttribute("data-lucide", "star");
          starText.textContent = "Star";
        }
      } else {
        // If no icon found, just update text
        if (conv.is_starred) {
          starText.textContent = "Unstar";
        } else {
          starText.textContent = "Star";
        }
      }
    }
  }

  // Position and show menu
  menu.style.left = `${x}px`;
  menu.style.top = `${y}px`;
  menu.classList.remove("hidden");
  menu.dataset.conversationId = conversationId;

  // Adjust position if menu overflows viewport
  setTimeout(() => {
    const menuRect = menu.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // If menu overflows right edge, position to the left of cursor
    if (menuRect.right > viewportWidth) {
      menu.style.left = `${Math.max(0, viewportWidth - menuRect.width - 10)}px`;
    }

    // If menu overflows bottom edge, position above cursor
    if (menuRect.bottom > viewportHeight) {
      menu.style.top = `${Math.max(0, viewportHeight - menuRect.height - 10)}px`;
    }
  }, 0);

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }

  // Close on click outside
  const closeMenu = (e) => {
    if (!menu.contains(e.target)) {
      menu.classList.add("hidden");
      document.removeEventListener("click", closeMenu);
    }
  };
  setTimeout(() => {
    document.addEventListener("click", closeMenu);
  }, 0);
}

/**
 * Handle conversation context menu actions
 */
async function handleConversationAction(action, conversationId) {
  const conv = conversations.find((c) => c.id === conversationId);
  if (!conv) return;

  try {
    switch (action) {
      case "rename":
        await renameConversation(conversationId);
        break;

      case "star":
        await toggleStarConversation(conversationId);
        break;

      case "category":
        await changeConversationCategory(conversationId);
        break;

      case "mental-models":
        await openMentalModelsOverrideModal(conversationId);
        break;

      case "delete":
        await deleteConversation(conversationId);
        break;
    }
  } catch (error) {
    console.error("Failed to perform action:", error);
    alert(`Failed to ${action} conversation: ${error.message}`);
  }
}

/**
 * Rename a conversation
 */
async function renameConversation(conversationId) {
  const conv = conversations.find((c) => c.id === conversationId);
  if (!conv) {
    console.log("renameConversation: conversation not found", conversationId);
    return;
  }

  // Show rename modal
  const modal = document.getElementById("rename-modal");
  const input = document.getElementById("rename-input");

  // Set current title in input
  input.value = conv.title;

  // Show modal
  modal.classList.remove("hidden");

  // Focus input and select text
  setTimeout(() => {
    input.focus();
    input.select();
  }, 100);

  // Setup submit handler
  const submitRename = async () => {
    const newTitle = input.value.trim();

    if (!newTitle || newTitle === conv.title) {
      modal.classList.add("hidden");
      return;
    }

    try {
      const updated = await window.polly.conversationUpdate(conversationId, {
        title: newTitle,
      });

      // Update local state
      const index = conversations.findIndex((c) => c.id === conversationId);
      if (index !== -1) {
        conversations[index] = { ...conversations[index], ...updated };
      }

      if (currentConversationId === conversationId) {
        currentConversation.title = newTitle;
      }

      renderConversationList();
      if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
      if (typeof renderChatTabs === "function") renderChatTabs();
      modal.classList.add("hidden");
    } catch (error) {
      console.error("Failed to rename conversation:", error);
      alert(`Failed to rename conversation: ${error.message}`);
    }
  };

  // Setup close handlers
  const closeModal = () => {
    modal.classList.add("hidden");
  };

  document.getElementById("close-rename-modal").onclick = closeModal;
  document.getElementById("cancel-rename-modal").onclick = closeModal;
  document.getElementById("submit-rename-modal").onclick = submitRename;

  // Handle Enter key in input
  input.onkeydown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      submitRename();
    } else if (e.key === "Escape") {
      closeModal();
    }
  };

  // Close on outside click
  modal.onclick = (e) => {
    if (e.target === modal) {
      closeModal();
    }
  };
}

/**
 * Toggle star status for a conversation
 */
async function toggleStarConversation(conversationId) {
  const updated = await window.polly.conversationStarToggle(conversationId);

  // Update local state
  const index = conversations.findIndex((c) => c.id === conversationId);
  if (index !== -1) {
    conversations[index] = { ...conversations[index], ...updated };
  }

  if (currentConversationId === conversationId) {
    currentConversation.is_starred = updated.is_starred;
  }

  renderConversationList();
}

/**
 * Change conversation category
 */
async function changeConversationCategory(conversationId) {
  const conv = conversations.find((c) => c.id === conversationId);
  if (!conv) {
    console.log(
      "changeConversationCategory: conversation not found",
      conversationId,
    );
    return;
  }

  console.log("changeConversationCategory: categories =", categories);

  if (!categories || categories.length === 0) {
    alert("No categories available. Please check if categories are loaded.");
    return;
  }

  // Show category selection modal
  const modal = document.getElementById("category-modal");
  const categoryList = document.getElementById("category-list");

  // Clear existing categories
  categoryList.innerHTML = "";

  // Create category selection UI
  categories.forEach((cat) => {
    const item = document.createElement("div");
    item.className = "category-list-item";
    if (cat.id === conv.category_id) {
      item.classList.add("selected");
    }

    item.innerHTML = `
      <div class="category-icon">${cat.icon}</div>
      <div class="category-info">
        <div class="category-name">${cat.name}</div>
        <div class="category-description">${cat.description || ""}</div>
      </div>
    `;

    item.addEventListener("click", async () => {
      try {
        // Update conversation category
        const updated = await window.polly.conversationUpdate(conversationId, {
          category_id: cat.id,
        });

        // Update local state
        const index = conversations.findIndex((c) => c.id === conversationId);
        if (index !== -1) {
          conversations[index] = { ...conversations[index], ...updated };
        }

        if (currentConversationId === conversationId) {
          currentConversation.category_id = cat.id;
          currentConversation.category_name = cat.name;
        }

        // Reload conversations to refresh grouping
        conversations = await window.polly.conversationList({
          agent_id: (currentAgentId != null && currentAgentId !== "") ? currentAgentId : "default",
        });
        renderConversationList();

        // Close modal
        modal.classList.add("hidden");
      } catch (error) {
        console.error("Failed to update category:", error);
        alert(`Failed to update category: ${error.message}`);
      }
    });

    categoryList.appendChild(item);
  });

  // Show modal
  modal.classList.remove("hidden");

  // Setup close handlers
  const closeModal = () => {
    modal.classList.add("hidden");
  };

  document.getElementById("close-category-modal").onclick = closeModal;
  document.getElementById("cancel-category-modal").onclick = closeModal;

  // Close on outside click
  modal.onclick = (e) => {
    if (e.target === modal) {
      closeModal();
    }
  };
}

/**
 * Delete a conversation
 */
async function deleteConversation(conversationId) {
  const conv = conversations.find((c) => c.id === conversationId);
  if (!conv) return;

  if (!confirm(`Delete "${conv.title}"?`)) return;

  await window.polly.conversationDelete(conversationId, true);

  // Remove from local state
  conversations = conversations.filter((c) => c.id !== conversationId);

  // If we deleted the current conversation, switch to another
  if (currentConversationId === conversationId) {
    if (conversations.length > 0) {
      await switchToConversation(conversations[0].id);
    } else {
      await createNewConversation();
    }
  }

  renderConversationList();
  if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
  if (typeof renderChatTabs === "function") renderChatTabs();
}

/**
 * Toggle sidebar collapsed state (legacy - now handled by conversations section toggle)
 */
function toggleConversationsSidebar() {
  // This function is now handled by the conversations section toggle in the right sidebar
  // Keeping for backward compatibility
  const section = document.querySelector(".chat-conversations-content");
  if (section) {
    section.style.display = section.style.display === "none" ? "block" : "none";
  }
}

/**
 * Search conversations
 */
function searchConversations() {
  const query = document.getElementById("conversations-search-input").value;
  renderConversationList(query);
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  console.log("[Setup] Setting up event listeners...");

  // Navigation
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      showView(view);

      document
        .querySelectorAll(".nav-item")
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });

  // Ribbon Navigation (Phase 0.5)
  console.log("[Setup] Setting up ribbon navigation...");
  const ribbonLogo = document.querySelector(".ribbon-logo");
  if (ribbonLogo) {
    console.log("[Setup] Found ribbon logo, attaching click handler");
    ribbonLogo.addEventListener("click", () => {
      showView("dashboard");
      document.querySelectorAll(".ribbon-item").forEach((b) => {
        b.classList.remove("active", "glitch");
      });
      const dashboardBtn = document.querySelector(
        '.ribbon-item[data-view="dashboard"]',
      );
      if (dashboardBtn) {
        dashboardBtn.classList.add("active", "glitch");
      }
      console.log("[Ribbon] Logo clicked, returning to dashboard");
    });
  }

  const ribbonItems = document.querySelectorAll(".ribbon-item");
  console.log(`[Setup] Found ${ribbonItems.length} ribbon items`);
  ribbonItems.forEach((btn) => {
    btn.addEventListener("click", () => {
      const view = btn.dataset.view;
      if (view) {
        showView(view);

        // Update ribbon active state with glitch effect
        document.querySelectorAll(".ribbon-item").forEach((b) => {
          b.classList.remove("active", "glitch");
        });
        btn.classList.add("active", "glitch");

        // Also update sidebar nav to stay in sync
        document
          .querySelectorAll(".nav-item")
          .forEach((b) => b.classList.remove("active"));
        const sidebarBtn = document.querySelector(
          `.nav-item[data-view="${view}"]`,
        );
        if (sidebarBtn) {
          sidebarBtn.classList.add("active");
        }

        console.log("[Ribbon] Switched to view:", view);
      }
    });
  });

  // Sidebar Collapse/Expand (Phase 0.5)
  const threeColumnLayout = document.querySelector(".three-column-layout");

  // Restore sidebar state from localStorage
  const leftCollapsed =
    localStorage.getItem("sidebar-left-collapsed") === "true";
  const rightCollapsed =
    localStorage.getItem("sidebar-right-collapsed") === "true";

  if (threeColumnLayout) {
    if (leftCollapsed) {
      threeColumnLayout.classList.add("left-collapsed");
    }
    if (rightCollapsed) {
      threeColumnLayout.classList.add("right-collapsed");
    }
  }

  // Get titlebar button references
  const titlebarToggleLeft = document.getElementById("titlebar-toggle-left");
  const titlebarToggleRight = document.getElementById("titlebar-toggle-right");

  // Update titlebar button icons and positions based on sidebar state
  function updateTitlebarButtons() {
    const leftCollapsed =
      threeColumnLayout?.classList.contains("left-collapsed");
    const rightCollapsed =
      threeColumnLayout?.classList.contains("right-collapsed");

    if (titlebarToggleLeft) {
      const icon = titlebarToggleLeft.querySelector("i");

      // Update icon - chevron-left points left (close), chevron-right points right (open)
      if (icon) {
        icon.setAttribute(
          "data-lucide",
          leftCollapsed ? "chevron-right" : "chevron-left",
        );
      }

      // Toggle class to change position via CSS (using absolute positioning instead of transform)
      if (leftCollapsed) {
        titlebarToggleLeft.classList.remove("sidebar-open");
      } else {
        titlebarToggleLeft.classList.add("sidebar-open");
      }

      titlebarToggleLeft.classList.toggle("collapsed", leftCollapsed);
      titlebarToggleLeft.title = leftCollapsed
        ? "Show left sidebar (Cmd+B)"
        : "Hide left sidebar (Cmd+B)";
    }

    if (titlebarToggleRight) {
      const icon = titlebarToggleRight.querySelector("i");

      // Update icon - chevron-right points right (close), chevron-left points left (open)
      if (icon) {
        icon.setAttribute(
          "data-lucide",
          rightCollapsed ? "chevron-left" : "chevron-right",
        );
      }

      // Toggle class to change position via CSS (using absolute positioning instead of transform)
      if (rightCollapsed) {
        titlebarToggleRight.classList.remove("sidebar-open");
      } else {
        titlebarToggleRight.classList.add("sidebar-open");
      }

      titlebarToggleRight.classList.toggle("collapsed", rightCollapsed);
      titlebarToggleRight.title = rightCollapsed
        ? "Show right sidebar (Cmd+/)"
        : "Hide right sidebar (Cmd+/)";
    }

    // Re-init lucide icons
    setTimeout(() => lucide.createIcons(), 50);
  }

  function toggleLeftSidebar() {
    if (threeColumnLayout) {
      const isCollapsed =
        threeColumnLayout.classList.contains("left-collapsed");
      threeColumnLayout.classList.toggle("left-collapsed");

      // Persist state
      localStorage.setItem("sidebar-left-collapsed", !isCollapsed);

      // Update titlebar buttons
      updateTitlebarButtons();

      // Re-init icons
      setTimeout(() => lucide.createIcons(), 50);

      // If expanding left sidebar, clamp chat panel first (before transition) so it doesn't overflow
      if (isCollapsed) clampChatPanelToMax(false, true);
    }
  }

  function toggleRightSidebar() {
    if (threeColumnLayout) {
      const isCollapsed =
        threeColumnLayout.classList.contains("right-collapsed");
      threeColumnLayout.classList.toggle("right-collapsed");

      // Persist state
      localStorage.setItem("sidebar-right-collapsed", !isCollapsed);

      // Update titlebar buttons
      updateTitlebarButtons();

      // Re-init icons
      setTimeout(() => lucide.createIcons(), 50);

      // If expanding right sidebar, clamp chat panel first (before transition) so it doesn't overflow
      if (isCollapsed) clampChatPanelToMax(true, false);
    }
  }

  // Titlebar sidebar toggle button event listeners
  if (titlebarToggleLeft) {
    titlebarToggleLeft.addEventListener("click", () => {
      toggleLeftSidebar();
    });
  }

  if (titlebarToggleRight) {
    titlebarToggleRight.addEventListener("click", () => {
      toggleRightSidebar();
    });
  }

  // Initialize titlebar button states
  updateTitlebarButtons();

  // Keyboard shortcuts for sidebar toggle
  document.addEventListener("keydown", (e) => {
    // Check if focus is inside CodeMirror editor (don't interfere with editor shortcuts)
    const activeElement = document.activeElement;
    const isInEditor =
      activeElement &&
      (activeElement.classList.contains("cm-content") ||
        activeElement.closest(".cm-editor"));

    // Cmd+B or Ctrl+B - Toggle left sidebar (unless in editor)
    if ((e.metaKey || e.ctrlKey) && e.key === "b") {
      if (!isInEditor) {
        e.preventDefault();
        toggleLeftSidebar();
      }
    }

    // Cmd+/ or Ctrl+/ - Toggle right sidebar
    if ((e.metaKey || e.ctrlKey) && e.key === "/") {
      e.preventDefault();
      toggleRightSidebar();
    }
  });

  // Setup - Check Dependencies
  document
    .getElementById("btn-check-deps")
    .addEventListener("click", checkDependencies);

  // Setup - Vault path
  document
    .getElementById("btn-select-vault")
    .addEventListener("click", async () => {
      const path = await window.polly.selectDirectory();
      if (path) {
        document.getElementById("vault-path").value = path;
      }
    });

  // Setup - Add code path
  document
    .getElementById("btn-add-code")
    .addEventListener("click", async () => {
      const paths = await window.polly.selectDirectories();
      if (paths.length) {
        codePaths = [...new Set([...codePaths, ...paths])];
        renderCodePaths();
      }
    });

  // Setup - Navigation
  document
    .getElementById("btn-back-1")
    .addEventListener("click", () => goToStep(1));
  document
    .getElementById("btn-next-2")
    .addEventListener("click", () => goToStep(3));
  document
    .getElementById("btn-back-2")
    .addEventListener("click", () => goToStep(2));

  // Setup - Install
  document.getElementById("btn-install").addEventListener("click", runInstall);

  // Setup - Complete
  document
    .getElementById("btn-start-indexing")
    .addEventListener("click", async () => {
      showView("knowledge");
      await indexKnowledge({ force: true });
    });

  document.getElementById("btn-skip-index").addEventListener("click", () => {
    showView("chat");
  });

  // Chat - Send (main chat panel + legacy)
  const chatSendBtn = document.getElementById("chat-send");
  if (chatSendBtn) {
    chatSendBtn.addEventListener("click", sendQuery);
  }
  const sendBtn = document.getElementById("btn-send");
  if (sendBtn) {
    sendBtn.addEventListener("click", sendQuery);
  }

  // Chat - Save to Obsidian
  const saveBtn = document.getElementById("btn-save-conversation");
  if (saveBtn) {
    saveBtn.addEventListener("click", openSaveConversationModal);
  }

  // Chat - Toggle Related Notes (legacy buttons - removed in new UI)
  const toggleRelatedBtn = document.getElementById("btn-toggle-related");
  if (toggleRelatedBtn) {
    toggleRelatedBtn.addEventListener("click", toggleRelatedNotes);
  }

  const closeRelatedBtn = document.getElementById("btn-close-related");
  if (closeRelatedBtn) {
    closeRelatedBtn.addEventListener("click", closeRelatedNotes);
  }

  // Conversations - New Chat
  // Chat - New conversation button (sidebar)
  const newChatBtnSidebar = document.getElementById("btn-new-chat-sidebar");
  if (newChatBtnSidebar) {
    newChatBtnSidebar.addEventListener("click", async () => {
      await createNewConversation();
      renderConversationList();
      if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
      if (typeof renderChatTabs === "function") renderChatTabs();
    });
  }

  // Agents sidebar - New Agent button
  const newAgentBtn = document.getElementById("new-agent-btn");
  if (newAgentBtn) {
    newAgentBtn.addEventListener("click", () => openNewAgentDialog());
  }

  // New Agent modal
  const newAgentModalClose = document.getElementById("new-agent-modal-close");
  if (newAgentModalClose) {
    newAgentModalClose.addEventListener("click", closeNewAgentDialog);
  }
  const newAgentCancel = document.getElementById("new-agent-cancel");
  if (newAgentCancel) {
    newAgentCancel.addEventListener("click", closeNewAgentDialog);
  }
  const newAgentModalBackdrop = document.getElementById("new-agent-modal-backdrop");
  if (newAgentModalBackdrop) {
    newAgentModalBackdrop.addEventListener("click", closeNewAgentDialog);
  }
  const newAgentCreate = document.getElementById("new-agent-create");
  if (newAgentCreate) {
    newAgentCreate.addEventListener("click", () => submitNewAgentFromDialog());
  }

  // Legacy button support (if it still exists)
  const newChatBtn = document.getElementById("btn-new-chat");
  if (newChatBtn) {
    newChatBtn.addEventListener("click", async () => {
      await createNewConversation();
      renderConversationList();
    });
  }

  // Conversations - Toggle sidebar (legacy)
  const toggleSidebarBtn = document.getElementById("btn-toggle-sidebar");
  if (toggleSidebarBtn) {
    toggleSidebarBtn.addEventListener("click", toggleConversationsSidebar);
  }

  // Conversations section toggle (new sidebar)
  const conversationsToggle = document.getElementById("conversations-toggle");
  if (conversationsToggle) {
    conversationsToggle.addEventListener("click", () => {
      const section = document.querySelector(".chat-conversations-content");
      const icon = conversationsToggle.querySelector("[data-lucide]");
      if (section) {
        section.style.display =
          section.style.display === "none" ? "block" : "none";
        if (icon) {
          icon.setAttribute(
            "data-lucide",
            section.style.display === "none" ? "chevron-right" : "chevron-down",
          );
          setTimeout(() => lucide.createIcons(), 10);
        }
      }
    });
  }

  // Conversations - Search
  const searchInput = document.getElementById("conversations-search-input");
  if (searchInput) {
    searchInput.addEventListener("input", searchConversations);
  } else {
    console.warn(
      "Conversations search input not found (may not be on chat view)",
    );
  }

  // Conversations - Page Filter
  const pageFilter = document.getElementById("page-filter");
  if (pageFilter) {
    pageFilter.addEventListener("change", () => {
      renderConversationList(searchInput?.value || "");
    });
  } else {
    console.warn("Page filter not found (may not be on chat view)");
  }

  // Context Menu Actions
  document
    .querySelectorAll("#conversation-context-menu .context-menu-item")
    .forEach((item) => {
      item.addEventListener("click", async (e) => {
        const action = item.dataset.action;
        const menu = document.getElementById("conversation-context-menu");
        const conversationId = menu.dataset.conversationId;

        menu.classList.add("hidden");

        if (conversationId) {
          await handleConversationAction(action, conversationId);
        }
      });
    });

  // Slash command autocomplete
  setupSlashCommandAutocomplete();

  // Query input - Enter to send (main chat panel + legacy)
  const chatInput = document.getElementById("chat-input");
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
      }
    });
  }
  const queryInput = document.getElementById("query-input");
  if (queryInput) {
    queryInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
      }
    });
  }

  // Global keyboard shortcuts
  document.addEventListener("keydown", async (e) => {
    const isMac = navigator.platform.toUpperCase().indexOf("MAC") >= 0;
    const modifier = isMac ? e.metaKey : e.ctrlKey;

    // Only handle shortcuts when not typing in an input
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") {
      // Exception: Allow Cmd/Ctrl+B even when in input (toggle sidebar)
      if (modifier && e.key === "b") {
        e.preventDefault();
        toggleConversationsSidebar();
        return;
      }
      // Don't handle other shortcuts when typing
      return;
    }

    // Cmd/Ctrl+N: New conversation
    if (modifier && e.key === "n") {
      e.preventDefault();
      await createNewConversation();
      renderConversationList();
      const chatInput = document.getElementById("chat-input");
      const queryInput = document.getElementById("query-input");
      (chatInput || queryInput)?.focus();
    }

    // Cmd/Ctrl+B: Toggle sidebar
    if (modifier && e.key === "b") {
      e.preventDefault();
      toggleConversationsSidebar();
    }

    // Cmd/Ctrl+F: Focus search
    if (modifier && e.key === "f" && currentView === "chat") {
      e.preventDefault();
      const searchInput = document.getElementById("conversations-search-input");
      if (searchInput) searchInput.focus();
    }

    // /: Focus query input (like Slack/Discord)
    if (e.key === "/" && currentView === "chat") {
      e.preventDefault();
      const chatInput = document.getElementById("chat-input");
      const queryInput = document.getElementById("query-input");
      (chatInput || queryInput)?.focus();
    }
  });

  // Auto-resize textareas (main chat panel + legacy)
  const resizeHandler = function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 150) + "px";
  };
  const chatInputEl = document.getElementById("chat-input");
  if (chatInputEl) chatInputEl.addEventListener("input", resizeHandler);
  const queryInputEl = document.getElementById("query-input");
  if (queryInputEl) queryInputEl.addEventListener("input", resizeHandler);

  // Quick actions
  document.querySelectorAll(".quick-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const chatInput = document.getElementById("chat-input");
      const queryInput = document.getElementById("query-input");
      const input = chatInput || queryInput;
      if (input) {
        input.value = btn.dataset.query;
        sendQuery();
      }
    });
  });

  // Dashboard - Server toggle
  document
    .getElementById("btn-toggle-server")
    .addEventListener("click", toggleServer);

  // Knowledge - Index buttons
  document
    .getElementById("btn-reindex")
    .addEventListener("click", () => indexKnowledge({ force: true }));
  document
    .getElementById("btn-index-obsidian")
    .addEventListener("click", () => indexKnowledge({ obsidianOnly: true }));
  document
    .getElementById("btn-index-code")
    .addEventListener("click", () => indexKnowledge({ codeOnly: true }));

  // Settings - Add code
  document
    .getElementById("btn-settings-add-code")
    .addEventListener("click", async () => {
      const paths = await window.polly.selectDirectories();
      if (paths.length) {
        codePaths = [...new Set([...codePaths, ...paths])];
        renderCodePaths("settings-code-paths");
      }
    });

  // Settings - Save
  document
    .getElementById("btn-save-settings")
    .addEventListener("click", saveSettings);

  // Settings - Reset
  document
    .getElementById("btn-reset-setup")
    .addEventListener("click", async () => {
      if (confirm("This will reset all settings. Are you sure?")) {
        await window.polly.setStore("setupComplete", false);
        location.reload();
      }
    });

  // Domains - Add Domain
  document.getElementById("btn-add-domain")?.addEventListener("click", () => {
    openDomainEditor(null);
  });

  // Domains - Folder Numbering Toggle
  document
    .getElementById("folder-numbering-toggle")
    ?.addEventListener("change", (e) => {
      toggleFolderNumbering(e.target.checked);
    });

  // Domain Editor - Close
  document
    .getElementById("close-domain-editor")
    ?.addEventListener("click", closeDomainEditor);
  document
    .getElementById("cancel-domain-editor")
    ?.addEventListener("click", closeDomainEditor);

  // Domain Editor - Save
  document
    .getElementById("save-domain-editor")
    ?.addEventListener("click", saveDomain);

  // Domain Editor - Icon Picker
  document
    .getElementById("domain-icon-preview")
    ?.addEventListener("click", () => {
      const iconGrid = document.getElementById("domain-icon-grid");
      iconGrid.classList.toggle("hidden");
    });

  document.querySelectorAll(".icon-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedIcon = btn.dataset.icon;
      updateIconPreview();
      document.getElementById("domain-icon-grid").classList.add("hidden");
    });
  });

  // Domain Editor - Color Picker
  document.querySelectorAll(".color-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      selectedColor = btn.dataset.color;
      updateColorPreview();
    });
  });

  // Domain Editor - Weight Slider
  document
    .getElementById("domain-weight-slider")
    ?.addEventListener("input", (e) => {
      document.getElementById("domain-weight-value").textContent =
        `${e.target.value}%`;
    });

  // Domain Editor - Keywords Input
  document
    .getElementById("domain-keywords-input")
    ?.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const keyword = e.target.value.trim();
        if (keyword) {
          addKeyword(keyword);
        }
      }
    });

  // Domain Editor - Suggest Keywords Button
  document
    .getElementById("btn-suggest-keywords")
    ?.addEventListener("click", suggestDomainKeywords);

  // Patterns - Controls
  const btnRefreshPatterns = document.getElementById("btn-refresh-patterns");
  if (btnRefreshPatterns) {
    btnRefreshPatterns.addEventListener("click", loadPatterns);
  }

  const btnExportPatterns = document.getElementById("btn-export-patterns");
  if (btnExportPatterns) {
    btnExportPatterns.addEventListener("click", exportPatterns);
  }

  const btnResetPatterns = document.getElementById("btn-reset-patterns");
  if (btnResetPatterns) {
    btnResetPatterns.addEventListener("click", resetPatterns);
  }

  const patternTimeFilter = document.getElementById("pattern-time-filter");
  if (patternTimeFilter) {
    patternTimeFilter.addEventListener("change", filterPatterns);
  }

  // Persona Controls (Phase 16c) - chat panel + legacy
  const chatPersonaSelect = document.getElementById("chat-persona-select");
  if (chatPersonaSelect) {
    chatPersonaSelect.addEventListener("change", handlePersonaChange);
  }
  const personaSelect = document.getElementById("persona-select");
  if (personaSelect) {
    personaSelect.addEventListener("change", handlePersonaChange);
  }

  const modeSelect = document.getElementById("mode-select");
  if (modeSelect) {
    modeSelect.addEventListener("change", handleModeChange);
  }

  // Model Selector (Phase 16c) - chat panel + legacy
  const chatModelSelect = document.getElementById("chat-model-select");
  if (chatModelSelect) {
    chatModelSelect.addEventListener("change", handleModelChange);
  }
  const modelSelect = document.getElementById("model-select");
  if (modelSelect) {
    modelSelect.addEventListener("change", handleModelChange);
  }

  // Curriculum Review Dialog (Phase 23)
  const saveCurriculumBtn = document.getElementById("btn-save-curriculum");
  if (saveCurriculumBtn) {
    saveCurriculumBtn.addEventListener("click", saveCurriculumFromReview);
  }

  const regenerateCurriculumBtn = document.getElementById(
    "btn-regenerate-curriculum",
  );
  if (regenerateCurriculumBtn) {
    regenerateCurriculumBtn.addEventListener("click", regenerateCurriculum);
  }

  // Complete Section Dialog (Phase 23)
  const masteryLevels = document.querySelectorAll(".mastery-level");
  if (masteryLevels && masteryLevels.length > 0) {
    masteryLevels.forEach((level) => {
      level.addEventListener("click", () => {
        selectMasteryLevel(level.dataset.level);
      });
    });
  }

  const confirmCompleteSectionBtn = document.getElementById(
    "btn-confirm-complete-section",
  );
  if (confirmCompleteSectionBtn) {
    confirmCompleteSectionBtn.addEventListener(
      "click",
      handleConfirmCompleteSection,
    );
  }
}

/**
 * Show a specific view
 */
function showView(view) {
  currentView = view;
  currentPage = view; // Track page changes for conversation context

  // Hide all views
  const allViews = document.querySelectorAll(".view");
  allViews.forEach((v) => v.classList.add("hidden"));

  // Show requested view
  const viewElement = document.getElementById(`view-${view}`);
  if (viewElement) {
    viewElement.classList.remove("hidden");
  } else {
    console.error(`[showView] View element not found: view-${view}`);
    return;
  }

  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });

  // Update adaptive left sidebar
  try {
    updateLeftSidebar(view);
  } catch (error) {
    console.error(`[showView] Error updating left sidebar:`, error);
  }

  // Always show chat interface in right sidebar
  // The chat is the primary interaction method and should always be accessible
  try {
    updateRightSidebar("chat");
  } catch (error) {
    console.error(`[showView] Error updating right sidebar:`, error);
  }

  // Load view-specific data
  try {
    if (view === "dashboard") {
      loadDashboardData();
    } else if (view === "knowledge") {
      loadKnowledgeData();
    } else if (view === "patterns") {
      loadPatterns();
    } else if (view === "curricula") {
      // Load curricula list (Phase 23)
      loadCurriculaView();
    } else if (view === "notes") {
      // Initialize notes manager when showing notes view
      // Add small delay to ensure DOM is ready
      setTimeout(() => {
        if (window.notesManager) {
          window.notesManager.init().catch((err) => {
            console.error("[Notes] Failed to initialize:", err);
          });
        }
      }, 100);
    } else if (view === "settings") {
      // Load domains config if domains tab is active
      const domainsTab = document.querySelector(
        '.settings-tab-btn[data-tab="domains"]',
      );
      if (domainsTab && domainsTab.classList.contains("active")) {
        loadDomainsConfig();
      }
    } else if (view === "learning") {
      // Initialize Learning page (Phase 22)
      initLearningPage();
    } else if (view === "graph") {
      // Initialize Graph page
      initGraphPage();
    }
  } catch (error) {
    console.error(`[showView] Error loading view data for ${view}:`, error);
  }

  // Re-initialize Lucide icons after view change
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }
}

/**
 * Update left sidebar content based on active view
 */
// Sidebar ribbon configurations: contextual horizontal ribbon buttons per page
const sidebarRibbonConfigs = {
  dashboard: {
    containerClass: "dashboard-ribbon-buttons",
    btnClass: "dashboard-ribbon-btn",
    buttons: [
      {
        id: "overview",
        icon: "layout-dashboard",
        label: "Overview",
        default: true,
      },
      { id: "activity", icon: "activity", label: "Activity" },
      { id: "stats", icon: "bar-chart-2", label: "Stats" },
    ],
  },
  notes: {
    containerClass: "notes-ribbon-buttons",
    btnClass: "notes-ribbon-btn",
    buttons: [
      { id: "browse", icon: "list", label: "Browse", default: true },
    ],
  },
  code: {
    containerClass: "code-ribbon-buttons",
    btnClass: "code-ribbon-btn",
    buttons: [
      { id: "files", icon: "files", label: "Files", default: true },
      { id: "search", icon: "search", label: "Search" },
    ],
  },
  knowledge: {
    containerClass: "knowledge-ribbon-buttons",
    btnClass: "knowledge-ribbon-btn",
    buttons: [
      { id: "sources", icon: "database", label: "Sources", default: true },
      { id: "index", icon: "search", label: "Index" },
      { id: "domains", icon: "folder-tree", label: "Domains" },
    ],
  },
  patterns: {
    containerClass: "patterns-ribbon-buttons",
    btnClass: "patterns-ribbon-btn",
    buttons: [
      { id: "all", icon: "sparkles", label: "All", default: true },
      { id: "categories", icon: "grid-3x3", label: "Categories" },
      { id: "export", icon: "download", label: "Export" },
    ],
  },
  learning: {
    containerClass: "learning-ribbon-buttons",
    btnClass: "learning-ribbon-btn",
    buttons: [
      {
        id: "curricula",
        icon: "graduation-cap",
        label: "Curricula",
        default: true,
      },
      { id: "progress", icon: "trending-up", label: "Progress" },
      { id: "topics", icon: "book-open", label: "Topics" },
    ],
  },
  search: {
    containerClass: "search-ribbon-buttons",
    btnClass: "search-ribbon-btn",
    buttons: [
      { id: "recent", icon: "clock", label: "Recent", default: true },
      { id: "saved", icon: "bookmark", label: "Saved" },
    ],
  },
  domains: {
    containerClass: "domains-ribbon-buttons",
    btnClass: "domains-ribbon-btn",
    buttons: [
      { id: "all", icon: "folder-tree", label: "All", default: true },
      { id: "active", icon: "zap", label: "Active" },
    ],
  },
  graph: {
    containerClass: "graph-ribbon-buttons",
    btnClass: "graph-ribbon-btn",
    buttons: [
      { id: "browse", icon: "list", label: "Browse", default: true },
      { id: "garden", icon: "sparkles", label: "Garden" },
    ],
  },
  settings: {
    containerClass: "settings-ribbon-buttons",
    btnClass: "settings-ribbon-btn",
    buttons: [
      { id: "general", icon: "settings", label: "General", default: true },
      { id: "api-keys", icon: "key", label: "API Keys" },
      { id: "routing", icon: "git-branch", label: "Routing" },
    ],
  },
};

// Track active sidebar ribbon tab per view
const activeSidebarRibbonTab = {};

/**
 * Create the horizontal sidebar ribbon HTML for a given view
 */
function createSidebarRibbon(view) {
  const config = sidebarRibbonConfigs[view];
  if (!config) return "";

  const buttons = config.buttons
    .map((btn) => {
      const isActive =
        activeSidebarRibbonTab[view] === btn.id ||
        (!activeSidebarRibbonTab[view] && btn.default);
      return `<button class="${config.btnClass}${isActive ? " active" : ""}" data-ribbon-tab="${btn.id}" title="${btn.label}">
      <i data-lucide="${btn.icon}"></i>
      <span>${btn.label}</span>
    </button>`;
    })
    .join("");

  return `<div class="${config.containerClass}">${buttons}</div>`;
}

/**
 * Create the browser sub-ribbon HTML (floating hover ribbon for file trees)
 */
function createBrowserRibbon(view) {
  const buttons = [];

  if (view === "notes") {
    buttons.push(
      { icon: "file-plus", title: "New Note", action: "new-note" },
      { icon: "folder-plus", title: "New Folder", action: "new-folder" },
      { icon: "arrow-up-down", title: "Sort", action: "sort" },
      { icon: "refresh-cw", title: "Refresh", action: "refresh" },
    );
  } else if (view === "code") {
    buttons.push(
      { icon: "file-plus", title: "New File", action: "new-file" },
      { icon: "folder-plus", title: "New Folder", action: "new-folder" },
      { icon: "fold-vertical", title: "Collapse All", action: "collapse-all" },
      { icon: "refresh-cw", title: "Refresh", action: "refresh" },
    );
  }

  if (buttons.length === 0) return "";

  const buttonsHTML = buttons
    .map(
      (btn) =>
        `<button class="browser-ribbon-btn" data-action="${btn.action}" title="${btn.title}">
      <i data-lucide="${btn.icon}"></i>
    </button>`,
    )
    .join("");

  return `<div class="browser-ribbon">${buttonsHTML}</div>`;
}

/**
 * Attach event handlers for sidebar ribbon buttons
 */
function setupSidebarRibbonHandlers(view) {
  const config = sidebarRibbonConfigs[view];
  if (!config) return;

  document.querySelectorAll(`.${config.btnClass}`).forEach((btn) => {
    btn.addEventListener("click", () => {
      const tab = btn.dataset.ribbonTab;
      activeSidebarRibbonTab[view] = tab;

      // Update active states
      document
        .querySelectorAll(`.${config.btnClass}`)
        .forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      console.log(`[Sidebar Ribbon] ${view} -> ${tab}`);

      // Learning view: switch between Curricula and Progress panels
      if (view === "learning") {
        switchLearningSidebarPanel(tab);
      }
      
      // Graph view: switch between Browse and Garden panels
      if (view === "graph") {
        switchGraphSidebarPanel(tab);
      }
    });
  });
}

/**
 * Switch Learning left sidebar between Curricula, Progress, and Topics panels
 */
function switchLearningSidebarPanel(tab) {
  const curriculaPanel = document.getElementById("learning-sidebar-curricula");
  const progressPanel = document.getElementById("learning-sidebar-progress");
  const topicsPanel = document.getElementById("learning-sidebar-topics");
  if (!curriculaPanel || !progressPanel) return;

  // Hide all panels
  curriculaPanel.classList.add("hidden");
  progressPanel.classList.add("hidden");
  if (topicsPanel) topicsPanel.classList.add("hidden");

  // Show the selected panel
  if (tab === "progress") {
    progressPanel.classList.remove("hidden");
  } else if (tab === "topics") {
    if (topicsPanel) {
      topicsPanel.classList.remove("hidden");
      loadTopicsBrowser();
    }
  } else {
    // Default: curricula
    curriculaPanel.classList.remove("hidden");
  }

  if (typeof lucide !== "undefined") lucide.createIcons();
}

/**
 * Switch Graph left sidebar between Browse and Garden panels
 */
function switchGraphSidebarPanel(tab) {
  const browsePanel = document.getElementById("graph-sidebar-browse");
  const gardenPanel = document.getElementById("graph-sidebar-garden");
  if (!browsePanel || !gardenPanel) return;

  // Hide all panels
  browsePanel.classList.add("hidden");
  gardenPanel.classList.add("hidden");

  // Show the selected panel
  if (tab === "garden") {
    gardenPanel.classList.remove("hidden");
    loadGardenView();
  } else {
    // Default: browse
    browsePanel.classList.remove("hidden");
  }

  if (typeof lucide !== "undefined") lucide.createIcons();
}

/**
 * Attach event handlers for browser sub-ribbon buttons
 */
function setupBrowserRibbonHandlers(view) {
  const container =
    view === "notes"
      ? document.getElementById("notes-file-tree-container")
      : document.querySelector(".code-view-content");

  if (!container) return;

  container.querySelectorAll(".browser-ribbon-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const action = btn.dataset.action;

      if (view === "notes") {
        switch (action) {
          case "new-note":
            if (window.notesManager) window.notesManager.showCreateNoteModal();
            break;
          case "new-folder":
            if (window.notesManager)
              window.notesManager.showCreateFolderModal();
            break;
          case "sort":
            // Toggle sort select visibility or cycle through sort modes
            const sortSelect = document.getElementById("notes-sort-select");
            if (sortSelect) sortSelect.focus();
            break;
          case "refresh":
            if (window.notesManager) {
              window.notesManager.loadNotesIndex();
            }
            break;
        }
      }

      console.log(`[Browser Ribbon] ${view} action: ${action}`);
    });
  });
}

function updateLeftSidebar(view) {
  const sidebarTitle = document.querySelector(".left-sidebar .sidebar-title");
  const sidebarContent = document.querySelector(
    ".left-sidebar .sidebar-content",
  );

  if (!sidebarTitle || !sidebarContent) return;

  // Build the horizontal sidebar ribbon for this view
  const ribbonHTML = createSidebarRibbon(view);

  // Define sidebar content for each view
  const sidebarConfigs = {
    dashboard: {
      title: "Quick Links",
      content: renderDashboardSidebar(),
    },
    knowledge: {
      title: "Sources",
      content: renderKnowledgeSidebar(),
    },
    patterns: {
      title: "Filters",
      content: renderPatternsSidebar(),
    },
    settings: {
      title: "Navigation",
      content: renderSettingsSidebar(),
    },
    calendar: {
      title: "Timeline",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">Calendar navigation coming soon</div>',
    },
    mail: {
      title: "Folders",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">Mail folders coming soon</div>',
    },
    code: {
      title: "Files",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">File browser coming soon</div>',
    },
    projects: {
      title: "Projects",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">Project list coming soon</div>',
    },
    notes: {
      title: "Notes",
      content: `
        <div id="notes-browse-list" style="flex: 1; overflow-y: auto; padding: 0 12px;">
          <div class="loading-spinner" style="text-align: center; padding: 20px; color: #808080; font-size: 13px;">
            Loading notes...
          </div>
        </div>
        ${renderLowerPanel("notes", [
          {id: "filters", label: "Filters"},
          {id: "backlinks", label: "Backlinks"},
          {id: "tags", label: "Tags"},
          {id: "toc", label: "TOC"}
        ])}
      `,
    },
    learning: {
      title: "Learning",
      content: `
        <div id="learning-sidebar-curricula" class="learning-sidebar-panel">
          <div id="learning-curricula-list" style="margin-bottom: 12px;">
            <div class="loading-spinner" style="text-align: center; padding: 20px; color: #808080; font-size: 13px;">
              Loading curricula...
            </div>
          </div>
        </div>
        <div id="learning-sidebar-progress" class="learning-sidebar-panel hidden">
          <div class="learning-progress-sidebar">
            <div class="stats-header">
              <i data-lucide="trending-up" style="width: 20px; height: 20px;"></i>
              <h3>Learning Progress</h3>
            </div>
            <div class="stats-content" id="learning-stats-content">
              <div class="stat-item">
                <span class="stat-label">Topics Learned:</span>
                <span class="stat-value" id="stat-total-topics">0</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Needs Review:</span>
                <span class="stat-value" id="stat-review-count">0</span>
              </div>
              <div class="mastery-breakdown" id="mastery-breakdown">
                <div class="mastery-label">Mastery Levels:</div>
                <div class="mastery-bars" id="mastery-bars"></div>
              </div>
            </div>
            <button class="btn btn-secondary btn-sm" id="btn-refresh-stats" style="margin-top: 12px; width: 100%;">
              <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i>
              Refresh Stats
            </button>
          </div>
        </div>
        <div id="learning-sidebar-topics" class="learning-sidebar-panel hidden">
          <div class="learning-topics-browser">
            <div class="topics-browser-header">
              <i data-lucide="book-open" style="width: 16px; height: 16px;"></i>
              <h3>All Topics</h3>
            </div>
            <div class="topics-browser-filter">
              <select id="topics-domain-filter" class="topics-filter-select">
                <option value="">All Domains</option>
              </select>
              <select id="topics-mastery-filter" class="topics-filter-select">
                <option value="">All Levels</option>
                <option value="1">L1 - Introduced</option>
                <option value="2">L2 - Learning</option>
                <option value="3">L3 - Understood</option>
                <option value="4">L4 - Proficient</option>
                <option value="5">L5 - Mastered</option>
              </select>
            </div>
            <div class="topics-browser-list" id="topics-browser-list">
              <div class="loading-spinner" style="text-align: center; padding: 20px; color: #808080; font-size: 13px;">
                Loading topics...
              </div>
            </div>
          </div>
        </div>
      `,
    },
    curricula: {
      title: "My Curricula",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">Use the Professor persona to create curricula</div>',
    },
    search: {
      title: "Recent",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">Recent searches coming soon</div>',
    },
    domains: {
      title: "Domains",
      content:
        '<div style="padding: 16px; color: #808080; font-size: 13px;">Domain list coming soon</div>',
    },
    graph: {
      title: "Graph",
      content: renderGraphSidebar(),
    },
  };

  const config = sidebarConfigs[view] || { title: "Navigation", content: "" };
  sidebarTitle.textContent = config.title;

  // Wrap content in a sidebar container with ribbon at top
  const containerClass = `${view}-sidebar-container`;
  // Remove padding from sidebar-content so ribbon is edge-to-edge
  sidebarContent.style.padding = "0";
  sidebarContent.style.overflow = "hidden";
  sidebarContent.innerHTML = `<div class="${containerClass}">
    ${ribbonHTML}
    <div class="sidebar-view-content" style="flex: 1; overflow-y: auto; min-height: 0; padding: var(--spacing-sm);">
      ${config.content}
    </div>
  </div>`;

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 50);
  }

  // Setup sidebar ribbon handlers
  setupSidebarRibbonHandlers(view);

  // Setup lower panel for notes view
  if (view === "notes") {
    setupLowerPanel("notes");
    
    // Setup lower panel tab change event listener
    document.addEventListener('lower-panel-tab-change', (e) => {
      if (e.detail.view === 'notes' && window.notesManager) {
        const tabId = e.detail.tabId;
        console.log(`[Notes] Lower panel tab changed to: ${tabId}`);
        
        // Render content for the selected tab
        switch (tabId) {
          case 'backlinks':
            window.notesManager.updateBacklinksPanel();
            break;
          case 'tags':
            window.notesManager.updateTagsPanel();
            break;
          case 'toc':
            window.notesManager.updateTOCPanel();
            break;
          case 'filters':
            // TODO: Implement filters panel in future task
            const content = document.querySelector('.lower-panel[data-view="notes"] .lower-panel-content');
            if (content) {
              content.innerHTML = `
                <div class="lower-panel-empty">
                  <i data-lucide="filter" style="width: 24px; height: 24px;"></i>
                  <p>Filters coming soon</p>
                </div>
              `;
              if (typeof lucide !== 'undefined') lucide.createIcons();
            }
            break;
        }
      }
    });
    
    // Re-initialize icons for lower panel
    if (typeof lucide !== "undefined") {
      setTimeout(() => lucide.createIcons(), 60);
    }
  }

  // Attach event handlers based on view
  setTimeout(() => {
    if (view === "dashboard") {
      // Quick links navigation
      document
        .querySelectorAll(".left-sidebar .nav-item[data-view]")
        .forEach((btn) => {
          btn.addEventListener("click", () => {
            const targetView = btn.dataset.view;
            showView(targetView);
          });
        });

      // Recent conversations
      document.querySelectorAll(".recent-conv-item").forEach((btn) => {
        btn.addEventListener("click", () => {
          const convId = parseInt(btn.dataset.convId);
          const conv = conversations.find((c) => c.id === convId);
          if (conv) {
            switchToConversation(conv);
          }
        });
      });
    } else if (view === "learning") {
      // Load curricula list and set initial panel visibility
      loadLearningSidebarCurricula();
      switchLearningSidebarPanel(activeSidebarRibbonTab["learning"] || "curricula");
    } else if (view === "knowledge") {
      const indexObsidianBtn = document.getElementById(
        "sidebar-index-obsidian",
      );
      const indexCodeBtn = document.getElementById("sidebar-index-code");
      const domainFilter = document.getElementById("sidebar-domain-filter");

      if (indexObsidianBtn) {
        indexObsidianBtn.addEventListener("click", async () => {
          await indexKnowledge({ obsidian: true });
        });
      }
      if (indexCodeBtn) {
        indexCodeBtn.addEventListener("click", async () => {
          await indexKnowledge({ codebase: true });
        });
      }
      if (domainFilter) {
        domainFilter.addEventListener("change", () => {
          const selectedDomain = domainFilter.value;
          console.log("Knowledge domain filter changed:", selectedDomain);
          // TODO: Filter knowledge results by domain
        });
      }
    } else if (view === "patterns") {
      const refreshBtn = document.getElementById("sidebar-refresh-patterns");
      const filterSelect = document.getElementById("sidebar-pattern-filter");
      const categorySelect = document.getElementById(
        "sidebar-pattern-category",
      );
      const exportBtn = document.getElementById("sidebar-export-patterns");

      if (refreshBtn) {
        refreshBtn.addEventListener("click", async () => {
          await loadPatterns();
        });
      }
      if (filterSelect) {
        filterSelect.addEventListener("change", async () => {
          // Filter patterns based on time range
          await loadPatterns();
        });
      }
      if (categorySelect) {
        categorySelect.addEventListener("change", async () => {
          // Filter patterns based on category
          console.log("Pattern category filter changed:", categorySelect.value);
          await loadPatterns();
        });
      }
      if (exportBtn) {
        exportBtn.addEventListener("click", () => {
          console.log("Export patterns clicked");
          // TODO: Implement pattern export
        });
      }
    } else if (view === "settings") {
      document.querySelectorAll(".settings-nav-item").forEach((btn) => {
        btn.addEventListener("click", () => {
          const tab = btn.dataset.tab;

          // Update sidebar active state
          document
            .querySelectorAll(".settings-nav-item")
            .forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");

          // Switch legacy tab content
          const tabContents = document.querySelectorAll(
            ".settings-tab-content",
          );
          tabContents.forEach((content) => {
            if (content.id === `tab-${tab}`) {
              content.classList.remove("hidden");
            } else {
              content.classList.add("hidden");
            }
          });

          // Also switch new settings section content
          const sectionContents = document.querySelectorAll(
            ".settings-section-content",
          );
          sectionContents.forEach((section) => {
            if (section.id === `settings-section-${tab}`) {
              section.classList.remove("hidden");
            } else {
              section.classList.add("hidden");
            }
          });

          // Load tab-specific data
          if (tab === "general") {
            loadGeneralSettings();
          } else if (tab === "domains") {
            loadDomainsConfig();
          } else if (tab === "routing") {
            loadRoutingSettings();
            loadRoutingStats();
          } else if (tab === "api-keys") {
            console.log("[Settings Sidebar] Switched to API Keys tab");
            console.log(
              "[Settings Sidebar] loadAPIKeys type:",
              typeof loadAPIKeys,
            );
            console.log(
              "[Settings Sidebar] loadBudgetStatus type:",
              typeof loadBudgetStatus,
            );
            if (typeof loadAPIKeys === "function") {
              console.log("[Settings Sidebar] Calling loadAPIKeys()");
              loadAPIKeys();
            }
            if (typeof loadBudgetStatus === "function") {
              console.log("[Settings Sidebar] Calling loadBudgetStatus()");
              loadBudgetStatus();
            }
          } else if (tab === "compression") {
            loadCompressionSettings();
            loadCompressionStats();
          } else if (tab === "memory") {
            loadMemorySettings();
          } else if (tab === "mental-models") {
            loadMentalModels();
            refreshMentalModelsStats();
            loadGlobalDefaultsPicker();
          } else if (tab === "advanced") {
            loadDedupSettings();
          } else if (tab === "providers") {
          loadProviderSettings();
        }
      });
    });
    } else if (view === "graph") {
      // Graph page event handlers will be set up in initGraphPage()
      console.log("[Graph] Sidebar initialized, waiting for initGraphPage()");
    }
  }, 100);
}

function renderConversationsSidebar() {
  return `
    <div style="padding: 8px;">
      <div style="padding: 8px; margin-bottom: 8px;">
        <input type="text" placeholder="Search conversations..." style="width: 100%; padding: 8px; font-size: 12px; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 4px; color: #e0e0e0;">
      </div>
      <button class="btn btn-primary" style="width: 100%; margin-bottom: 12px; font-size: 13px;" id="sidebar-new-chat">
        <i data-lucide="plus" style="width: 14px; height: 14px;"></i>
        New Conversation
      </button>
      <div id="sidebar-conversations-list">
        <!-- Conversation list will be populated here -->
      </div>
    </div>
  `;
}

function renderDashboardSidebar() {
  // Get recent conversations for current page
  const recentConvs = conversations
    .filter((c) => c.page_context === currentPage)
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 5);

  const recentConvsHTML =
    recentConvs.length > 0
      ? `
    <div style="margin-top: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Recent on This Page</div>
      <div class="recent-conversations">
        ${recentConvs
          .map(
            (conv) => `
          <button class="recent-conv-item" data-conv-id="${conv.id}" title="${conv.title}">
            <span class="recent-conv-icon">${getPageIcon(conv.page_context)}</span>
            <span class="recent-conv-title">${conv.title}</span>
            <span class="recent-conv-time">${formatRelativeTime(conv.created_at)}</span>
          </button>
        `,
          )
          .join("")}
      </div>
    </div>
  `
      : '<div style="margin-top: 16px; padding: 12px; color: #606060; font-size: 12px; text-align: center;">No conversations on this page yet</div>';

  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Quick Links</div>
      <div class="nav-section">
        <button class="nav-item" data-view="knowledge" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="network" class="nav-icon"></i>
          <span class="nav-label">Knowledge</span>
        </button>
        <button class="nav-item" data-view="patterns" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="sparkles" class="nav-icon"></i>
          <span class="nav-label">Patterns</span>
        </button>
        <button class="nav-item" data-view="code" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="code-2" class="nav-icon"></i>
          <span class="nav-label">Code</span>
        </button>
        <button class="nav-item" data-view="settings" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="settings" class="nav-icon"></i>
          <span class="nav-label">Settings</span>
        </button>
      </div>
      ${recentConvsHTML}
    </div>
  `;
}

function renderKnowledgeSidebar() {
  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Domain Filter</div>
      <select id="sidebar-domain-filter" style="width: 100%; padding: 8px; font-size: 12px; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 4px; color: #e0e0e0; margin-bottom: 16px;">
        <option value="all">All Domains</option>
        <option value="obsidian">Obsidian Vault</option>
        <option value="code">Codebase</option>
        <option value="web">Web Sources</option>
        <option value="learning">Learning</option>
      </select>
      
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Actions</div>
      <button class="btn btn-secondary" style="width: 100%; margin-bottom: 8px; font-size: 13px; justify-content: flex-start;" id="sidebar-index-obsidian">
        <i data-lucide="book-open" style="width: 14px; height: 14px;"></i>
        Index Obsidian
      </button>
      <button class="btn btn-secondary" style="width: 100%; margin-bottom: 8px; font-size: 13px; justify-content: flex-start;" id="sidebar-index-code">
        <i data-lucide="code-2" style="width: 14px; height: 14px;"></i>
        Index Code
      </button>
      
      <div style="margin-top: 16px;">
        <div style="font-size: 12px; color: #808080; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Quick Access</div>
        <div class="knowledge-tree">
          <div class="tree-item">
            <i data-lucide="folder" style="width: 14px; height: 14px; color: #f0903b;"></i>
            <span>Obsidian Vault</span>
          </div>
          <div class="tree-item">
            <i data-lucide="folder" style="width: 14px; height: 14px; color: #3b82f6;"></i>
            <span>Repositories</span>
          </div>
          <div class="tree-item">
            <i data-lucide="globe" style="width: 14px; height: 14px; color: #10b981;"></i>
            <span>Web Bookmarks</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderPatternsSidebar() {
  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Time Range</div>
      <select id="sidebar-pattern-filter" style="width: 100%; padding: 8px; font-size: 12px; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 4px; color: #e0e0e0; margin-bottom: 16px;">
        <option value="all">All time</option>
        <option value="7">Last 7 days</option>
        <option value="30">Last 30 days</option>
        <option value="90">Last 90 days</option>
      </select>
      
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Category</div>
      <select id="sidebar-pattern-category" style="width: 100%; padding: 8px; font-size: 12px; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 4px; color: #e0e0e0; margin-bottom: 16px;">
        <option value="all">All Categories</option>
        <option value="code">Code</option>
        <option value="learning">Learning</option>
        <option value="productivity">Productivity</option>
        <option value="communication">Communication</option>
      </select>
      
      <button class="btn btn-secondary" style="width: 100%; font-size: 13px; justify-content: flex-start; margin-bottom: 8px;" id="sidebar-refresh-patterns">
        <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i>
        Refresh Patterns
      </button>
      
      <button class="btn btn-secondary" style="width: 100%; font-size: 13px; justify-content: flex-start;" id="sidebar-export-patterns">
        <i data-lucide="download" style="width: 14px; height: 14px;"></i>
        Export Patterns
      </button>
    </div>
  `;
}

function renderSettingsSidebar() {
  return `
    <div style="padding: 8px;">
      <div style="font-size: 12px; color: #808080; margin: 16px 8px 8px 8px; text-transform: uppercase; letter-spacing: 0.5px;">Sections</div>
      <div class="nav-section">
        <button class="nav-item settings-nav-item active" data-tab="general" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="sliders" class="nav-icon"></i>
          <span class="nav-label">General</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="routing" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="git-branch" class="nav-icon"></i>
          <span class="nav-label">Routing</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="api-keys" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="key" class="nav-icon"></i>
          <span class="nav-label">API Keys</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="providers" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="cloud" class="nav-icon"></i>
          <span class="nav-label">Providers</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="domains" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="folder-tree" class="nav-icon"></i>
          <span class="nav-label">Domains</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="notes" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="file-text" class="nav-icon"></i>
          <span class="nav-label">Notes</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="compression" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="package" class="nav-icon"></i>
          <span class="nav-label">Compression</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="ai-features" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="sparkles" class="nav-icon"></i>
          <span class="nav-label">AI Features</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="memory" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="database" class="nav-icon"></i>
          <span class="nav-label">Memory</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="integrations" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="plug" class="nav-icon"></i>
          <span class="nav-label">Integrations</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="mental-models" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="brain" class="nav-icon"></i>
          <span class="nav-label">Mental Models</span>
        </button>
        <button class="nav-item settings-nav-item" data-tab="advanced" style="width: 100%; justify-content: flex-start;">
          <i data-lucide="terminal" class="nav-icon"></i>
          <span class="nav-label">Advanced</span>
        </button>
      </div>
    </div>
  `;
}

// Store original chat HTML on first load
let originalChatHTML = null;

/**
 * Reattach event listeners to chat UI elements
 * (Called after sidebar HTML is replaced)
 */
function reattachChatEventListeners() {
  console.log("[Chat] Reattaching event listeners...");
  // New chat button
  const newChatBtnSidebar = document.getElementById("btn-new-chat-sidebar");
  if (newChatBtnSidebar) {
    newChatBtnSidebar.addEventListener("click", async () => {
      await createNewConversation();
      renderConversationList();
      if (typeof renderAgentsSidebar === "function") renderAgentsSidebar();
      if (typeof renderChatTabs === "function") renderChatTabs();
    });
  }

  // Send button and Enter key: ONLY attach to sidebar elements (query-input, btn-send).
  // chat-input and chat-send are in the main chat panel and get listeners from setupEventListeners.
  // Attaching here would duplicate listeners and cause multiple sends per action.
  const sendBtn = document.getElementById("btn-send");
  if (sendBtn) {
    sendBtn.addEventListener("click", () => sendQuery());
  }
  const queryInput = document.getElementById("query-input");
  if (queryInput) {
    queryInput.addEventListener("keydown", async (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        await sendQuery();
      }
    });
  }

  // Page filter
  const pageFilter = document.getElementById("page-filter");
  if (pageFilter) {
    pageFilter.addEventListener("change", (e) => {
      renderConversationList(
        document.getElementById("conversations-search-input")?.value || "",
      );
    });
  }

  // Conversations search
  const conversationsSearchInput = document.getElementById(
    "conversations-search-input",
  );
  if (conversationsSearchInput) {
    conversationsSearchInput.addEventListener("input", (e) => {
      renderConversationList(e.target.value);
    });
  }

  // Conversations toggle
  const conversationsToggle = document.getElementById("conversations-toggle");
  if (conversationsToggle) {
    conversationsToggle.addEventListener("click", () => {
      const section = document.querySelector(".chat-conversations-content");
      const icon = conversationsToggle.querySelector("[data-lucide]");
      if (section) {
        section.classList.toggle("collapsed");
        if (icon) {
          icon.setAttribute(
            "data-lucide",
            section.classList.contains("collapsed")
              ? "chevron-right"
              : "chevron-down",
          );
          if (typeof lucide !== "undefined") lucide.createIcons();
        }
      }
    });
  }

  // Persona controls (main chat panel + legacy sidebar)
  const chatPersonaSelect = document.getElementById("chat-persona-select");
  if (chatPersonaSelect) {
    chatPersonaSelect.addEventListener("change", handlePersonaChange);
    console.log("[Init] Attached chat-persona-select event listener");
  }
  const personaSelect = document.getElementById("persona-select");
  if (personaSelect) {
    personaSelect.addEventListener("change", handlePersonaChange);
    console.log("[Init] Attached persona-select event listener");
  }

  const modeSelect = document.getElementById("mode-select");
  if (modeSelect) {
    modeSelect.addEventListener("change", handleModeChange);
    console.log("[Init] Attached mode-select event listener");
  }

  // Model selector: populate dropdowns (chat panel + hidden) and wire change
  populateModelSelectors();
  const modelSelect = document.getElementById("model-select");
  if (modelSelect) {
    modelSelect.addEventListener("change", handleModelChange);
  }
  const chatModelSelect = document.getElementById("chat-model-select");
  if (chatModelSelect) {
    chatModelSelect.addEventListener("change", handleModelChange);
  }

  // Orchestrator toggle (TODO: implement multi-persona orchestration)
  const orchestratorToggle = document.getElementById("orchestrator-toggle");
  if (orchestratorToggle) {
    orchestratorToggle.addEventListener("click", () => {
      // Toggle the visual state
      const isActive =
        orchestratorToggle.getAttribute("aria-checked") === "true";
      orchestratorToggle.setAttribute("aria-checked", !isActive);
      orchestratorToggle.classList.toggle("active");
      console.log(
        "[Orchestrator] Toggled:",
        !isActive,
        "(not yet implemented)",
      );
    });
  }

  // Restore persona state after reattaching listeners
  // (The HTML was replaced, so we need to repopulate the mode dropdown)
  restorePersonaState();

  // Render conversation list
  renderConversationList();
}

/**
 * Update right sidebar content based on view
 */
function updateRightSidebar(view) {
  const sidebarTitle = document.querySelector(".right-sidebar .sidebar-title");
  const sidebarContent = document.querySelector(
    ".right-sidebar .sidebar-content",
  );

  if (!sidebarTitle || !sidebarContent) return;

  const hasQueryInput = sidebarContent.querySelector("#query-input") !== null;
  const hasChatMessages =
    sidebarContent.querySelector("#chat-messages") !== null;

  // CRITICAL: Don't replace HTML if chat is already initialized with an active conversation
  // This prevents the conversation from being cleared and re-rendered, regardless of current view
  if (hasQueryInput && hasChatMessages && currentConversationId) {
    return;
  }

  // Save original chat HTML on first call (if it exists and hasn't been saved)
  if (
    originalChatHTML === null &&
    sidebarContent.querySelector("#query-input")
  ) {
    originalChatHTML = sidebarContent.innerHTML;
  }

  // If trying to show chat but we don't have the HTML saved yet, just keep current content
  if (view === "chat" && !originalChatHTML) {
    return;
  }

  // Always show chat interface (we simplified this - no more view-specific sidebars)
  sidebarTitle.textContent = "Chat";
  sidebarContent.innerHTML = originalChatHTML || sidebarContent.innerHTML;

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 50);
  }

  // Reattach event listeners after restoring HTML
  setTimeout(() => {
    reattachChatEventListeners();
  }, 100);
}

function renderChatRightSidebar() {
  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Related Notes</div>
      <div style="padding: 12px; background: #1a1a1a; border-radius: 6px; margin-bottom: 12px;">
        <div style="font-size: 13px; color: #e0e0e0; margin-bottom: 4px;">No related notes</div>
        <div style="font-size: 11px; color: #808080;">Connect Obsidian to see related content</div>
      </div>
      
      <div style="font-size: 12px; color: #808080; margin: 16px 0 12px 0; text-transform: uppercase; letter-spacing: 0.5px;">Conversation Info</div>
      <div style="padding: 12px; background: #1a1a1a; border-radius: 6px;">
        <div style="font-size: 11px; color: #808080; margin-bottom: 4px;">Messages</div>
        <div style="font-size: 15px; color: #e0e0e0; margin-bottom: 8px;" id="right-msg-count">0</div>
        <div style="font-size: 11px; color: #808080; margin-bottom: 4px;">Created</div>
        <div style="font-size: 13px; color: #e0e0e0;" id="right-created-date">-</div>
      </div>
    </div>
  `;
}

function renderDashboardRightSidebar() {
  // Get stats from conversations
  const totalConvs = conversations.length;
  const todayConvs = conversations.filter((c) => {
    const createdToday =
      new Date(c.created_at).toDateString() === new Date().toDateString();
    return createdToday;
  }).length;

  // Get most recent conversation
  const recentConv = conversations.sort(
    (a, b) =>
      new Date(b.updated_at || b.created_at) -
      new Date(a.updated_at || a.created_at),
  )[0];

  const lastActivity = recentConv
    ? formatRelativeTime(recentConv.updated_at || recentConv.created_at)
    : "No activity";

  // Calculate total messages across all conversations
  const totalMessages = conversations.reduce(
    (sum, c) => sum + (c.messages?.length || 0),
    0,
  );

  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">System Stats</div>
      
      <div class="stat-card">
        <div class="stat-label">Total Conversations</div>
        <div class="stat-value">${totalConvs}</div>
        <div class="stat-sublabel">${todayConvs} created today</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Total Messages</div>
        <div class="stat-value">${totalMessages}</div>
        <div class="stat-sublabel">Across all chats</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-label">Last Activity</div>
        <div class="stat-value" style="font-size: 14px;">${lastActivity}</div>
        <div class="stat-sublabel">${recentConv ? recentConv.title : "No conversations"}</div>
      </div>
      
      <div style="margin-top: 16px;">
        <div style="font-size: 12px; color: #808080; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Quick Actions</div>
        <button class="btn btn-secondary" style="width: 100%; margin-bottom: 8px; font-size: 12px; justify-content: flex-start;" id="right-new-conversation">
          <i data-lucide="plus" style="width: 14px; height: 14px;"></i>
          New Conversation
        </button>
        <button class="btn btn-secondary" style="width: 100%; font-size: 12px; justify-content: flex-start;" id="right-view-all-conversations">
          <i data-lucide="list" style="width: 14px; height: 14px;"></i>
          View All Conversations
        </button>
      </div>
    </div>
  `;
}

function renderKnowledgeRightSidebar() {
  // Get RAG stats from global state (will be populated by loadSystemStats)
  // Support both 'notes' (new native system) and 'obsidian' (legacy)
  const notesStats = window.pollyStats?.rag_stats?.notes ||
    window.pollyStats?.rag_stats?.obsidian || { count: 0, files: 0 };
  const notesCount = notesStats.count;
  const notesFiles = notesStats.files;
  const codeCount = window.pollyStats?.rag_stats?.codebase?.count || 0;
  const codeFiles = window.pollyStats?.rag_stats?.codebase?.files || 0;
  const totalChunks = notesCount + codeCount;
  const totalFiles = notesFiles + codeFiles;

  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Knowledge Base</div>
      
      <div class="stat-card" style="border-left: 3px solid #f0903b;">
        <div class="stat-label">Notes</div>
        <div class="stat-value">${notesCount.toLocaleString()}</div>
        <div class="stat-sublabel">${notesFiles} files indexed</div>
      </div>
      
      <div class="stat-card" style="border-left: 3px solid #3b82f6;">
        <div class="stat-label">Codebase</div>
        <div class="stat-value">${codeCount.toLocaleString()}</div>
        <div class="stat-sublabel">${codeFiles} files indexed</div>
      </div>
      
      <div class="stat-card" style="border-left: 3px solid #10b981;">
        <div class="stat-label">Total Knowledge</div>
        <div class="stat-value">${totalChunks.toLocaleString()}</div>
        <div class="stat-sublabel">${totalFiles} files total</div>
      </div>
      
      <div style="margin-top: 16px;">
        <div style="font-size: 12px; color: #808080; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Actions</div>
        <button class="btn btn-secondary" style="width: 100%; margin-bottom: 8px; font-size: 12px; justify-content: flex-start;" id="right-refresh-index">
          <i data-lucide="refresh-cw" style="width: 14px; height: 14px;"></i>
          Refresh Index
        </button>
        <button class="btn btn-secondary" style="width: 100%; font-size: 12px; justify-content: flex-start;" id="right-view-sources">
          <i data-lucide="folder-open" style="width: 14px; height: 14px;"></i>
          View Sources
        </button>
      </div>
    </div>
  `;
}

function renderPatternsRightSidebar() {
  // Get pattern stats (will be populated when pattern system is implemented)
  const totalPatterns = window.pollyStats?.patterns?.total || 0;
  const weekPatterns = window.pollyStats?.patterns?.this_week || 0;
  const topCategory = window.pollyStats?.patterns?.top_category || "None";

  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Pattern Statistics</div>
      
      <div class="stat-card" style="border-left: 3px solid #8b5cf6;">
        <div class="stat-label">Total Patterns</div>
        <div class="stat-value">${totalPatterns}</div>
        <div class="stat-sublabel">All time</div>
      </div>
      
      <div class="stat-card" style="border-left: 3px solid #f59e0b;">
        <div class="stat-label">This Week</div>
        <div class="stat-value">${weekPatterns}</div>
        <div class="stat-sublabel">Last 7 days</div>
      </div>
      
      <div class="stat-card" style="border-left: 3px solid #10b981;">
        <div class="stat-label">Top Category</div>
        <div class="stat-value" style="font-size: 14px;">${topCategory}</div>
        <div class="stat-sublabel">Most frequent</div>
      </div>
      
      <div style="margin-top: 16px;">
        <div style="font-size: 12px; color: #808080; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px;">Pattern Types</div>
        <div class="pattern-type-list">
          <div class="pattern-type-item">
            <span>Code Patterns</span>
            <span style="color: #606060;">0</span>
          </div>
          <div class="pattern-type-item">
            <span>Learning Patterns</span>
            <span style="color: #606060;">0</span>
          </div>
          <div class="pattern-type-item">
            <span>Productivity</span>
            <span style="color: #606060;">0</span>
          </div>
          <div class="pattern-type-item">
            <span>Communication</span>
            <span style="color: #606060;">0</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderSettingsRightSidebar() {
  return `
    <div style="padding: 16px;">
      <div style="font-size: 12px; color: #808080; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Quick Help</div>
      <div style="padding: 12px; background: #1a1a1a; border-radius: 6px; margin-bottom: 12px;">
        <div style="font-size: 13px; color: #e0e0e0; margin-bottom: 6px;">
          <i data-lucide="info" style="width: 12px; height: 12px; margin-right: 4px;"></i>
          Tips
        </div>
        <div style="font-size: 11px; color: #808080; line-height: 1.5;">
          Configure your domains to organize different types of conversations and knowledge.
        </div>
      </div>
      
      <div style="padding: 12px; background: #1a1a1a; border-radius: 6px;">
        <div style="font-size: 13px; color: #e0e0e0; margin-bottom: 6px;">
          <i data-lucide="keyboard" style="width: 12px; height: 12px; margin-right: 4px;"></i>
          Shortcuts
        </div>
        <div style="font-size: 11px; color: #808080; line-height: 1.5;">
          <div style="margin-bottom: 4px;"><code style="background: #252525; padding: 2px 4px; border-radius: 3px;">Cmd+B</code> Toggle left sidebar</div>
          <div><code style="background: #252525; padding: 2px 4px; border-radius: 3px;">Cmd+/</code> Toggle right sidebar</div>
        </div>
      </div>
    </div>
  `;
}

/**
 * Check dependencies
 */
async function checkDependencies() {
  const btn = document.getElementById("btn-check-deps");
  btn.disabled = true;
  btn.textContent = "Checking...";

  const deps = await window.polly.checkDependencies();

  // Update Python status
  const pythonEl = document.getElementById("dep-python");
  if (deps.python) {
    pythonEl.querySelector(".dep-icon").innerHTML =
      '<i data-lucide="check-circle" style="width: 16px; height: 16px; color: var(--success);"></i>';
    pythonEl.querySelector(".dep-status").textContent = "Installed";
  } else {
    pythonEl.querySelector(".dep-icon").innerHTML =
      '<i data-lucide="x-circle" style="width: 16px; height: 16px; color: var(--error);"></i>';
    pythonEl.querySelector(".dep-status").textContent = "Not found";
  }

  // Update Ollama status
  const ollamaEl = document.getElementById("dep-ollama");
  if (deps.ollama) {
    ollamaEl.querySelector(".dep-icon").innerHTML =
      '<i data-lucide="check-circle" style="width: 16px; height: 16px; color: var(--success);"></i>';
    ollamaEl.querySelector(".dep-status").textContent = "Installed";
  } else {
    ollamaEl.querySelector(".dep-icon").innerHTML =
      '<i data-lucide="alert-circle" style="width: 16px; height: 16px; color: var(--warning);"></i>';
    ollamaEl.querySelector(".dep-status").textContent = "Not found (optional)";
  }

  // Re-initialize Lucide icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  btn.disabled = false;

  if (deps.python) {
    btn.textContent = "Continue";
    btn.onclick = () => goToStep(2);
  } else {
    btn.textContent = "Check Again";
  }
}

/**
 * Go to setup step
 */
function goToStep(step) {
  setupStep = step;

  document.querySelectorAll(".setup-step").forEach((el, i) => {
    el.classList.toggle("active", i + 1 === step);
  });
}

/**
 * Render code paths list
 */
function renderCodePaths(containerId = "code-paths") {
  const container = document.getElementById(containerId);

  if (!codePaths.length) {
    container.innerHTML =
      '<div class="path-empty">No directories selected</div>';
    return;
  }

  container.innerHTML = codePaths
    .map(
      (path, i) => `
    <div class="path-item">
      <span>${path}</span>
      <button class="path-remove" data-index="${i}">✕</button>
    </div>
  `,
    )
    .join("");

  container.querySelectorAll(".path-remove").forEach((btn) => {
    btn.addEventListener("click", () => {
      codePaths.splice(parseInt(btn.dataset.index), 1);
      renderCodePaths(containerId);
    });
  });
}

/**
 * Run installation
 */
async function runInstall() {
  const btn = document.getElementById("btn-install");
  btn.disabled = true;

  const progressContainer = document.getElementById("install-progress");
  progressContainer.style.display = "block";

  const vaultPath = document.getElementById("vault-path").value;
  const pullModels = document.getElementById("opt-pull-models").checked;

  try {
    const result = await window.polly.runSetup({
      vaultPath,
      codebasePaths: codePaths,
      pullModels,
    });

    if (result.success) {
      goToStep(4);
    } else {
      alert(`Setup failed: ${result.error}`);
      btn.disabled = false;
    }
  } catch (error) {
    alert(`Setup failed: ${error.message}`);
    btn.disabled = false;
  }
}

/**
 * Update setup progress
 */
function updateSetupProgress(data) {
  const fill = document.getElementById("progress-fill");
  const text = document.getElementById("progress-text");

  const percent = (data.step / data.total) * 100;
  fill.style.width = `${percent}%`;
  text.textContent = data.message;
}

/**
 * Auto-categorize conversation based on content
 */
async function autoCategorizeConversation(conversationId) {
  if (!conversationId || !categories || categories.length === 0) return;

  const conv = conversations.find((c) => c.id === conversationId);
  if (!conv) return;

  // Don't re-categorize if already categorized (not uncategorized)
  if (conv.category_id && conv.category_id !== "uncategorized") return;

  // Get conversation messages to analyze
  const fullConv = await window.polly.conversationGet(conversationId);
  if (!fullConv || !fullConv.messages || fullConv.messages.length === 0) return;

  // Combine all messages to analyze content
  const allText = fullConv.messages
    .map((m) => m.content)
    .join(" ")
    .toLowerCase();

  // Define keywords for each category
  const categoryKeywords = {
    sigils: [
      "auth",
      "login",
      "password",
      "security",
      "encrypt",
      "decrypt",
      "token",
      "jwt",
      "oauth",
      "permission",
      "access",
      "certificate",
      "key",
      "signature",
      "identity",
      "credential",
    ],
    signals: [
      "message",
      "notification",
      "event",
      "webhook",
      "socket",
      "broadcast",
      "publish",
      "subscribe",
      "channel",
      "stream",
      "real-time",
      "websocket",
      "email",
      "sms",
      "alert",
    ],
    scrolls: [
      "document",
      "file",
      "storage",
      "upload",
      "download",
      "pdf",
      "markdown",
      "content",
      "blob",
      "s3",
      "bucket",
      "attachment",
      "media",
      "image",
    ],
    glyphs: [
      "ui",
      "component",
      "button",
      "form",
      "layout",
      "css",
      "style",
      "design",
      "render",
      "display",
      "view",
      "template",
      "theme",
      "color",
      "font",
      "icon",
    ],
    grids: [
      "database",
      "table",
      "query",
      "sql",
      "schema",
      "model",
      "data",
      "index",
      "collection",
      "record",
      "crud",
      "orm",
      "migration",
      "postgres",
      "mongo",
      "array",
      "list",
      "map",
    ],
  };

  // Count matches for each category
  const scores = {};
  for (const [catId, keywords] of Object.entries(categoryKeywords)) {
    scores[catId] = keywords.reduce((score, keyword) => {
      // Count occurrences of the keyword
      const regex = new RegExp(`\\b${keyword}`, "gi");
      const matches = allText.match(regex);
      return score + (matches ? matches.length : 0);
    }, 0);
  }

  // Find category with highest score
  let bestCategory = "uncategorized";
  let highestScore = 0;

  for (const [catId, score] of Object.entries(scores)) {
    if (score > highestScore) {
      highestScore = score;
      bestCategory = catId;
    }
  }

  // Only categorize if we have a reasonable confidence (at least 3 keyword matches)
  if (highestScore >= 3) {
    console.log(
      `Auto-categorizing conversation ${conversationId} as ${bestCategory} (score: ${highestScore})`,
    );

    try {
      await window.polly.conversationUpdate(conversationId, {
        category_id: bestCategory,
      });

      // Update local state
      const index = conversations.findIndex((c) => c.id === conversationId);
      if (index !== -1) {
        const cat = categories.find((c) => c.id === bestCategory);
        conversations[index].category_id = bestCategory;
        if (cat) {
          conversations[index].category_name = cat.name;
        }
      }

      if (currentConversationId === conversationId) {
        currentConversation.category_id = bestCategory;
        const cat = categories.find((c) => c.id === bestCategory);
        if (cat) {
          currentConversation.category_name = cat.name;
        }
      }

      // Refresh the conversation list to show new category
      renderConversationList();
    } catch (error) {
      console.error("Failed to auto-categorize:", error);
    }
  }
}

// ============================================
// Persona Functions (Phase 16c)
// ============================================

/**
 * Handle persona dropdown change
 */
async function handlePersonaChange(e) {
  const personaName = e.target.value;
  const modeSelect = document.getElementById("mode-select");
  const personaSelect = document.getElementById("persona-select");
  const chatPersonaSelect = document.getElementById("chat-persona-select");

  console.log("[Persona] handlePersonaChange called with:", personaName);
  console.log("[Persona] Event triggered from:", e.target.id);

  // Keep persona selects in sync
  if (personaSelect && personaSelect.value !== personaName) {
    personaSelect.value = personaName;
  }
  if (chatPersonaSelect && chatPersonaSelect.value !== personaName) {
    chatPersonaSelect.value = personaName;
  }

  if (!personaName) {
    // Deactivate persona
    try {
      await fetch("http://127.0.0.1:11436/persona/deactivate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      // Disable mode selectors
      if (modeSelect) {
        modeSelect.disabled = true;
        modeSelect.innerHTML = "<option>Select persona first</option>";
      }

      // Hide teaching mode indicator
      updateTeachingModeIndicator(null, null);

      console.log("[Persona] Deactivated");
    } catch (error) {
      console.error("[Persona] Failed to deactivate:", error);
    }
    return;
  }

  try {
    // Activate persona
    console.log("[Persona] Activating persona:", personaName);
    console.log("[Persona] Sending POST to /persona/activate");

    const response = await fetch("http://127.0.0.1:11436/persona/activate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ persona_name: personaName }),
    });

    console.log(
      "[Persona] Response status:",
      response.status,
      response.statusText,
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Persona] Error response:", errorText);
      throw new Error(`Failed to activate persona: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("[Persona] Activation response:", data);

    if (data.success && data.state) {
      // Get persona metadata to populate modes
      const listResponse = await fetch("http://127.0.0.1:11436/persona/list");
      const listData = await listResponse.json();
      console.log("[Persona] List data:", listData);

      const persona = listData.personas.find((p) => p.name === personaName);
      console.log("[Persona] Found persona:", persona);
      console.log("[Persona] Available modes:", persona?.available_modes);

      if (persona && persona.available_modes) {
        // Populate mode selector
        const modeOptionsHTML = persona.available_modes
          .map(
            (mode) =>
              `<option value="${mode}" ${mode === data.state.current_mode ? "selected" : ""}>${mode.charAt(0).toUpperCase() + mode.slice(1)}</option>`,
          )
          .join("");

        // Update main mode select
        if (modeSelect) {
          modeSelect.disabled = false;
          modeSelect.innerHTML = modeOptionsHTML;
        }

        console.log(
          `[Persona] Activated ${personaName} in ${data.state.current_mode} mode`,
        );

        // Update teaching mode indicator
        updateTeachingModeIndicator(personaName, data.state.current_mode);

        // Display persona introduction if present
        if (data.state.introduction) {
          const formattedIntro = formatResponse(data.state.introduction);
          addMessageToUI("assistant", formattedIntro);
          await addMessageToConversation("assistant", data.state.introduction);
        }
      } else {
        console.error("[Persona] No modes found!", {
          hasPersona: !!persona,
          modes: persona?.available_modes,
          allData: listData,
        });
      }
    } else {
      console.error("[Persona] Activation failed or no state:", data);
    }
  } catch (error) {
    console.error("[Persona] Failed to activate persona:", error);
    alert(`Failed to activate ${personaName}: ${error.message}`);

    // Reset persona selects
    e.target.value = "";
    if (personaSelect && personaSelect !== e.target) personaSelect.value = "";
    if (chatPersonaSelect && chatPersonaSelect !== e.target)
      chatPersonaSelect.value = "";

    // Reset mode selects
    if (modeSelect) {
      modeSelect.disabled = true;
      modeSelect.innerHTML = "<option>Select persona first</option>";
    }
  }
}

/**
 * Handle mode selector change
 */
async function handleModeChange(e) {
  const mode = e.target.value;

  // Check if a persona is active first
  const personaSelect = document.getElementById("persona-select");
  const chatPersonaSelect = document.getElementById("chat-persona-select");
  const activePersona = chatPersonaSelect?.value || personaSelect?.value;

  if (!activePersona) {
    console.warn("[Persona] Cannot switch mode - no persona active");
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:11436/persona/switch-mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Persona] Mode switch failed:", errorText);
      throw new Error(`Failed to switch mode: ${response.statusText}`);
    }

    const data = await response.json();

    if (data.success) {
      console.log(`[Persona] Switched to ${mode} mode`);

      // Update teaching mode indicator if Professor persona is active
      updateTeachingModeIndicator(activePersona, mode);
    }
  } catch (error) {
    console.error("[Persona] Failed to switch mode:", error);
    // Don't show alert if persona not active - this is expected during initialization
    if (!error.message.includes("No persona is active")) {
      alert(`Failed to switch to ${mode} mode: ${error.message}`);
    }
  }
}

/**
 * Update teaching mode indicator badge
 * @param {string} persona - Active persona name
 * @param {string} mode - Current mode
 */
function updateTeachingModeIndicator(persona, mode) {
  const indicator = document.getElementById("teaching-mode-indicator");
  const modeText = document.getElementById("teaching-mode-text");

  if (!indicator || !modeText) return;

  // Only show indicator for Professor persona
  if (persona === "professor") {
    indicator.classList.remove("hidden");

    // Update text
    const modeNames = {
      socratic: "Socratic",
      explain: "Explain",
      curriculum: "Curriculum",
      quiz: "Quiz",
    };
    modeText.textContent = modeNames[mode] || mode;

    // Update color classes
    indicator.classList.remove(
      "mode-socratic",
      "mode-explain",
      "mode-curriculum",
      "mode-quiz",
    );
    indicator.classList.add(`mode-${mode}`);
  } else {
    // Hide for other personas
    indicator.classList.add("hidden");
  }
}

/**
 * Restore persona state on app load
 */
async function restorePersonaState() {
  try {
    // Use silent fetch to avoid console noise during startup
    const response = await fetch("http://127.0.0.1:11436/persona/state");
    if (!response.ok) {
      // This is normal if no persona is active
      return;
    }

    const data = await response.json();

    if (data.active_persona) {
      console.log("[Persona] Restoring persona state:", data);

      const personaSelect = document.getElementById("persona-select");
      const modeSelect = document.getElementById("mode-select");

      // Set persona dropdown
      personaSelect.value = data.active_persona;

      // Get persona metadata to populate modes
      const listResponse = await fetch("http://127.0.0.1:11436/persona/list");
      const listData = await listResponse.json();

      const persona = listData.personas.find(
        (p) => p.name === data.active_persona,
      );

      if (persona && persona.available_modes) {
        // Populate mode selector
        modeSelect.disabled = false;
        modeSelect.innerHTML = persona.available_modes
          .map(
            (mode) =>
              `<option value="${mode}" ${mode === data.current_mode ? "selected" : ""}>${mode.charAt(0).toUpperCase() + mode.slice(1)}</option>`,
          )
          .join("");

        console.log(
          `[Persona] Restored ${data.active_persona} in ${data.current_mode} mode`,
        );

        // Update teaching mode indicator
        updateTeachingModeIndicator(data.active_persona, data.current_mode);
      }
    }
  } catch (error) {
    // Only log if it's not a connection error (expected during startup)
    if (
      !error.message.includes("Failed to fetch") &&
      !error.message.includes("ERR_CONNECTION_REFUSED")
    ) {
      console.log("[Persona] Failed to restore persona state:", error.message);
    }
  }
}

/**
 * Model selector: provider list and display names (matches backend + LiteLLM/OpenRouter).
 */
const MODEL_PROVIDERS = [
  { id: "anthropic", label: "Anthropic (Claude)" },
  { id: "openai", label: "OpenAI (GPT)" },
  { id: "github", label: "GitHub" },
  { id: "grok", label: "Grok (xAI)" },
  { id: "perplexity", label: "Perplexity" },
  { id: "gemini", label: "Gemini" },
  { id: "mistral", label: "Mistral" },
  { id: "openrouter", label: "OpenRouter" },
];
const MODEL_TIERS = [
  { id: "fast", label: "Fast" },
  { id: "balanced", label: "Balanced" },
  { id: "thorough", label: "Thorough" },
];

/**
 * Build options HTML for model selector (one source of truth for chat, hidden, floating).
 */
function buildModelSelectorOptions() {
  // Add Polly Auto modes for all three tiers at the top
  let html = '<optgroup label="Polly (Auto)">';
  html += '<option value="auto:fast">Polly (Auto) — Fast</option>';
  html += '<option value="auto:balanced">Polly (Auto) — Balanced</option>';
  html += '<option value="auto:thorough">Polly (Auto) — Thorough</option>';
  html += '</optgroup>';
  
  // Then add specific provider options organized by tier
  for (const tier of MODEL_TIERS) {
    html += `<optgroup label="${tier.label}">`;
    for (const prov of MODEL_PROVIDERS) {
      html += `<option value="${prov.id}:${tier.id}">${prov.label}</option>`;
    }
    html += "</optgroup>";
  }
  return html;
}

/**
 * Populate all model selector dropdowns with current provider list.
 * Call on init and when provider status may have changed.
 */
function populateModelSelectors() {
  const optionsHtml = buildModelSelectorOptions();
  const selectIds = [
    "chat-model-select",
    "model-select",
  ];
  const confidence = sessionStorage.getItem("model-confidence") || "balanced";
  const providerOverride = sessionStorage.getItem("model-provider");
  const saved = providerOverride
    ? `${providerOverride}:${confidence}`
    : `auto:${confidence}`;
  for (const id of selectIds) {
    const el = document.getElementById(id);
    if (!el) continue;
    const current = el.value;
    el.innerHTML = optionsHtml;
    const hasCurrent = Array.from(el.options).some((o) => o.value === current);
    el.value = hasCurrent
      ? current
      : Array.from(el.options).some((o) => o.value === saved)
        ? saved
        : "auto:balanced";
  }
}

/**
 * Handle model selector change
 * Parses unified model selector value (e.g., "github:balanced" or "auto:balanced")
 * and stores for use in sendQuery
 */
function handleModelChange(e) {
  const modelValue = e.target.value; // e.g., "auto:balanced", "github:thorough", "anthropic:fast"

  // Parse the value: format is "provider:tier" or "auto:tier"
  const [provider, tier] = modelValue.split(":");

  // Store in sessionStorage for use in sendQuery
  if (provider === "auto") {
    // Auto mode: let router decide, just use the tier
    sessionStorage.setItem("model-confidence", tier);
    sessionStorage.removeItem("model-provider");
    console.log(`[Model] Auto mode with ${tier} tier`);
  } else {
    // Specific provider: set both tier and provider override
    sessionStorage.setItem("model-confidence", tier);
    sessionStorage.setItem("model-provider", provider);
    console.log(`[Model] ${provider} provider with ${tier} tier`);
  }
  // Keep selects in sync
  const selectIds = [
    "chat-model-select",
    "model-select",
  ];
  for (const id of selectIds) {
    const el = document.getElementById(id);
    if (el && el !== e.target && el.value !== modelValue) el.value = modelValue;
  }
}

/**
 * Send query to active persona
 * Returns true if persona handled the request, false otherwise
 * @param {string} query - User message
 * @param {Array} conversationHistory - Conversation history
 * @param {string} loadingId - Loading message ID
 * @param {string} [personaName] - Persona from dropdown or slash command
 * @param {string} [personaMode] - Mode from slash command (e.g. curriculum, socratic)
 */
async function sendToPersona(query, conversationHistory, loadingId, personaName, personaMode) {
  try {
    const body = {
      user_message: query,
      persona_name: personaName || undefined,
      metadata: {
        page: currentPage,
        conversation_history: conversationHistory,
      },
    };
    if (personaMode) body.persona_mode = personaMode;

    const response = await fetch(`${API_URL}/persona/process`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      let errDetail = response.statusText;
      try {
        const body = await response.text();
        if (body) {
          try {
            const parsed = JSON.parse(body);
            if (parsed.detail) errDetail = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail);
            else errDetail = body.slice(0, 200);
          } catch (_) {
            errDetail = body.slice(0, 200);
          }
        }
      } catch (_) {}
      console.error("[Persona] Server error:", response.status, errDetail);
      throw new Error(`Persona request failed: ${errDetail}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error("Persona processing failed");
    }

    const personaResponse = data.response;

    // Remove loading indicator
    removeMessage(loadingId);

    // Add persona response to UI
    const formattedContent = formatResponse(personaResponse.content);
    addMessageToUI("assistant", formattedContent);

    // Add to conversation in database
    await addMessageToConversation("assistant", personaResponse.content);

    // Handle actions
    if (personaResponse.actions && personaResponse.actions.length > 0) {
      for (const action of personaResponse.actions) {
        await handlePersonaAction(action, personaResponse.content);
      }
    }

    console.log(
      "[Persona] Response received with",
      personaResponse.actions?.length || 0,
      "actions",
    );

    return true; // Persona handled the request
  } catch (error) {
    console.error("[Persona] Request failed:", error);
    // Return false to fall back to normal query
    return false;
  }
}

/**
 * Handle persona action (show_questions, show_preview, etc.)
 */
async function handlePersonaAction(action, responseContent) {
  console.log("[Persona] Handling action:", action.type);

  switch (action.type) {
    case "review_curriculum":
      // Show curriculum review dialog (Phase 23)
      console.log("[Persona] review_curriculum action received");
      handleReviewCurriculumAction(action);
      break;

    case "show_template_gallery":
      // Show Template Gallery modal (Phase 16e)
      console.log("[Persona] show_template_gallery action received");
      console.log(
        "[Persona] window.TemplateGallery exists:",
        !!window.TemplateGallery,
      );
      console.log("[Persona] action.data:", action.data);

      if (window.TemplateGallery && action.data) {
        const suggestedTemplate = action.data.suggested_template || null;
        console.log(
          "[Persona] Showing template gallery, suggested:",
          suggestedTemplate,
        );

        const callback = async (templateFilename) => {
          console.log("[Persona] ===== TEMPLATE SELECTED CALLBACK FIRED =====");
          console.log("[Persona] User selected template:", templateFilename);

          // Send template selection back to persona for enrich mode
          await sendTemplateSelectionToPersona(templateFilename);
        };

        console.log("[Persona] Registering callback and showing gallery");
        window.TemplateGallery.show(suggestedTemplate, callback);
        console.log("[Persona] Gallery.show() called");
      } else {
        console.error("[Persona] TemplateGallery not available or no data");
      }
      break;

    case "show_questions":
      // Show QuestionForm modal
      if (window.QuestionForm && action.data) {
        window.QuestionForm.show(action.data, async (answers) => {
          console.log("[Persona] User answered questions:", answers);

          // Send answers back to persona
          await sendAnswersToPersona(answers);
        });
      } else {
        console.error("[Persona] QuestionForm not available or no data");
      }
      break;

    case "show_preview":
      // Show PreviewModal
      if (window.PreviewModal && action.data) {
        window.PreviewModal.show(action.data, async (noteData) => {
          console.log("[Persona] User saved note:", noteData);

          // Save note to knowledge base
          await saveNoteToKnowledgeBase(noteData);
        });
      } else {
        console.error("[Persona] PreviewModal not available or no data");
      }
      break;

    case "switch_mode":
    case "auto_mode_switch":
      // Auto-switch persona mode
      if (action.data && action.data.target_mode) {
        const targetMode = action.data.target_mode;
        const modeSelect = document.getElementById("mode-select");
        if (modeSelect) {
          console.log("[Persona] Auto-switching to mode:", targetMode);

          // First, ensure the mode option exists in the dropdown
          const existingOption = Array.from(modeSelect.options).find(
            (opt) => opt.value === targetMode,
          );
          if (!existingOption) {
            // Add the mode option if it doesn't exist
            const option = document.createElement("option");
            option.value = targetMode;
            option.textContent =
              targetMode.charAt(0).toUpperCase() + targetMode.slice(1);
            modeSelect.appendChild(option);
            modeSelect.disabled = false;
          }

          // Set the value
          modeSelect.value = targetMode;

          // Call the mode change handler with proper event structure
          await handleModeChange({ target: { value: targetMode } });

          // Show transition message if provided
          if (action.data.message) {
            console.log("[Persona] Mode switch message:", action.data.message);
          }

          // Auto-trigger next step in workflow
          // Send a follow-up query to continue the persona workflow
          setTimeout(async () => {
            console.log(
              "[Persona] Auto-triggering next step in",
              targetMode,
              "mode",
            );
            const messages = getCurrentConversationMessages();
            const conversationHistory = messages.map((msg) => ({
              role: msg.role,
              content: msg.content,
            }));

            // Show loading
            const followUpLoadingId = addMessageToUI(
              "assistant",
              '<div class="loading"><div class="loading-spinner"></div>Processing...</div>',
            );

            // Send continuation query
            await sendToPersona(
              "Continue workflow",
              conversationHistory,
              followUpLoadingId,
            );
          }, 500);
        }
      } else if (action.data && action.data.mode) {
        // Legacy format support
        const modeSelect = document.getElementById("mode-select");
        if (modeSelect) {
          modeSelect.value = action.data.mode;
          await handleModeChange({ target: { value: action.data.mode } });
        }
      }
      break;

    case "suggest_mode_switch":
      // Suggest a mode switch (non-automatic, just a suggestion)
      if (action.data && action.data.target_mode) {
        const targetMode = action.data.target_mode;
        const message =
          action.data.message || `Consider switching to ${targetMode} mode`;
        console.log(
          "[Persona] Mode switch suggested:",
          targetMode,
          "-",
          message,
        );

        // Optionally, you could show a toast/notification here
        // For now, just log it - the content message should explain to the user
      }
      break;

    case "render_diagram":
      // Render Mermaid diagram
      if (action.data) {
        await renderDiagram(action.data);
      } else {
        console.error("[Persona] render_diagram action missing data");
      }
      break;

    case "execute_code":
      // Execute code in sandbox
      if (action.data) {
        await executeCodeInSandbox(action.data);
      } else {
        console.error("[Persona] execute_code action missing data");
      }
      break;

    case "present_exercise":
      // Present interactive exercise
      if (action.data) {
        await presentExercise(action.data);
      } else {
        console.error("[Persona] present_exercise action missing data");
      }
      break;

    case "offer_learning_note":
      // Show learning note creation modal
      if (action.data) {
        showLearningNoteModal(action.data);
      }
      break;

    case "offer_save_as_note":
      // Curriculum mode (legacy): offer to save the learning path response as a note
      if (action.data && responseContent) {
        const noteTitle = action.data.suggested_title || "Learning Path";
        const noteDomain = action.data.domain || "general";
        console.log("[Persona] offer_save_as_note - domain:", noteDomain, "title:", noteTitle);

        showSaveAsNotePrompt(noteTitle, noteDomain, responseContent);
      }
      break;

    default:
      console.warn("[Persona] Unknown action type:", action.type);
      break;
  }
}

/**
 * Send user answers back to persona
 */
async function sendAnswersToPersona(answers) {
  const input = document.getElementById("query-input");

  // Add user answers to UI
  const answersText = Object.entries(answers)
    .map(([q, a]) => `${q}: ${a}`)
    .join("\n");
  addMessageToUI("user", `My answers:\n${answersText}`);

  // Add to conversation
  await addMessageToConversation("user", answersText);

  // Show loading
  const loadingId = addMessageToUI(
    "assistant",
    '<div class="loading"><div class="loading-spinner"></div>Generating note...</div>',
  );

  // Switch to enrich mode (organize mode expects answers, then switches to enrich)
  try {
    await fetch("http://127.0.0.1:11436/persona/switch-mode", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode: "enrich" }),
    });
    console.log("[Persona] Switched to enrich mode");
  } catch (error) {
    console.error("[Persona] Failed to switch mode:", error);
  }

  // Send to persona with answers in metadata
  const messages = getCurrentConversationMessages();
  const conversationHistory = messages.slice(0, -1).map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));

  // Call sendToPersona with metadata including answers
  try {
    const response = await fetch("http://127.0.0.1:11436/persona/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_message: "Generate the note with my answers",
        metadata: {
          page: currentPage,
          conversation_history: conversationHistory,
          user_answers: answers, // Include answers here!
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`Persona request failed: ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error("Persona processing failed");
    }

    const personaResponse = data.response;

    // Remove loading indicator
    removeMessage(loadingId);

    // Add persona response to UI
    const formattedContent = formatResponse(personaResponse.content);
    addMessageToUI("assistant", formattedContent);

    // Add to conversation
    await addMessageToConversation("assistant", personaResponse.content);

    // Handle any actions
    if (personaResponse.actions && personaResponse.actions.length > 0) {
      for (const action of personaResponse.actions) {
        await handlePersonaAction(action, conversationHistory);
      }
    }

    console.log(
      "[Persona] Response received with",
      personaResponse.actions?.length || 0,
      "actions",
    );
  } catch (error) {
    removeMessage(loadingId);
    console.error("[Persona] Request failed:", error);
    addMessageToUI("assistant", `Error: ${error.message}`);
  }
}

/**
 * Send template selection to persona for enrich mode (Phase 16e)
 */
async function sendTemplateSelectionToPersona(templateFilename) {
  const input = document.getElementById("query-input");

  // Add user selection to UI
  addMessageToUI("user", `I selected template: ${templateFilename}`);

  // Add to conversation
  await addMessageToConversation("user", `Template: ${templateFilename}`);

  // Show loading
  const loadingId = addMessageToUI(
    "assistant",
    '<div class="loading"><div class="loading-spinner"></div>Generating note from template...</div>',
  );

  // Switch to enrich mode
  try {
    console.log("[Persona] Switching to enrich mode...");
    const modeResponse = await fetch(
      "http://127.0.0.1:11436/persona/switch-mode",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode: "enrich" }),
      },
    );

    if (!modeResponse.ok) {
      throw new Error(`Failed to switch mode: ${modeResponse.statusText}`);
    }

    const modeData = await modeResponse.json();
    console.log("[Persona] Mode switch response:", modeData);

    if (!modeData.success) {
      throw new Error("Mode switch was not successful");
    }

    console.log("[Persona] Successfully switched to enrich mode");
  } catch (error) {
    console.error("[Persona] Failed to switch mode:", error);
    removeMessage(loadingId);
    addMessageToUI(
      "assistant",
      `Error switching to enrich mode: ${error.message}`,
    );
    return;
  }

  // Send to persona with template filename in metadata
  const messages = getCurrentConversationMessages();
  const conversationHistory = messages.slice(0, -1).map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));

  // Call sendToPersona with metadata including template filename
  try {
    console.log(
      "[Persona] Sending process request with template:",
      templateFilename,
    );

    const response = await fetch("http://127.0.0.1:11436/persona/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_message: "Generate the note using this template",
        metadata: {
          page: currentPage,
          conversation_history: conversationHistory,
          template_filename: templateFilename, // Include template filename
        },
      }),
    });

    console.log(
      "[Persona] Process response status:",
      response.status,
      response.statusText,
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[Persona] Process error response:", errorText);
      throw new Error(`Persona request failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log("[Persona] Process response data:", data);

    if (!data.success) {
      console.error("[Persona] Process failed:", data);
      throw new Error("Persona processing failed");
    }

    const personaResponse = data.response;
    console.log(
      "[Persona] Response actions:",
      personaResponse.actions?.map((a) => a.type),
    );

    // Remove loading indicator
    removeMessage(loadingId);

    // Add persona response to UI
    const formattedContent = formatResponse(personaResponse.content);
    addMessageToUI("assistant", formattedContent);

    // Add to conversation
    await addMessageToConversation("assistant", personaResponse.content);

    // Handle any actions
    if (personaResponse.actions && personaResponse.actions.length > 0) {
      console.log(
        "[Persona] Processing",
        personaResponse.actions.length,
        "action(s)",
      );
      for (const action of personaResponse.actions) {
        console.log("[Persona] Processing action:", action.type);
        await handlePersonaAction(action, conversationHistory);
      }
    } else {
      console.warn("[Persona] No actions in response");
    }

    console.log(
      "[Persona] Response received with",
      personaResponse.actions?.length || 0,
      "actions",
    );
  } catch (error) {
    removeMessage(loadingId);
    console.error("[Persona] Request failed:", error);
    addMessageToUI("assistant", `Error: ${error.message}`);
  }
}

/**
 * Show a prompt bar offering to save curriculum/learning path content as a note.
 * Appended below the last assistant message in the chat.
 */
function showSaveAsNotePrompt(title, domain, content) {
  // Create a save prompt bar that appears after the response
  const promptBar = document.createElement("div");
  promptBar.className = "save-note-prompt";
  promptBar.style.cssText =
    "display: flex; align-items: center; gap: 10px; padding: 12px 16px; " +
    "background: var(--bg-secondary); border: 1px solid var(--border-color); " +
    "border-radius: 8px; margin: 8px 0 16px 0;";
  promptBar.innerHTML = `
    <i data-lucide="bookmark" style="width: 18px; height: 18px; color: var(--accent); flex-shrink: 0;"></i>
    <span style="flex: 1; font-size: 13px; color: var(--text-secondary);">
      Save <strong>${title}</strong> to <strong>${domain}</strong> domain?
    </span>
    <button class="btn btn-primary btn-sm save-note-accept" style="padding: 4px 14px; font-size: 12px;">Save</button>
    <button class="btn btn-secondary btn-sm save-note-dismiss" style="padding: 4px 10px; font-size: 12px;">Dismiss</button>
  `;

  // Insert after the last message in the chat
  const messagesContainer = document.getElementById("messages");
  if (messagesContainer) {
    messagesContainer.appendChild(promptBar);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // Initialize icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons({ attrs: {}, nameAttr: "data-lucide" });
  }

  // Handle Save
  promptBar.querySelector(".save-note-accept").addEventListener("click", async () => {
    promptBar.remove();
    try {
      await saveNoteToKnowledgeBase({
        title: title,
        domain: domain,
        content: content,
      });
      showToast(`Saved "${title}" to ${domain}`, "success");
    } catch (err) {
      console.error("[Persona] Failed to save note:", err);
      showToast("Failed to save note: " + err.message, "error");
    }
  });

  // Handle Dismiss
  promptBar.querySelector(".save-note-dismiss").addEventListener("click", () => {
    promptBar.remove();
  });
}

/**
 * Save note to knowledge base via API
 */
async function saveNoteToKnowledgeBase(noteData) {
  try {
    console.log("[Persona] saveNoteToKnowledgeBase received:", noteData);

    // Extract note details - support both flat and nested metadata formats
    // New format: {content, metadata: {title, domain, ...}}
    // Old format: {content, title, domain, ...}
    const title = noteData.metadata?.title || noteData.title || "Untitled Note";
    const domain = noteData.metadata?.domain || noteData.domain || "scrolls";
    const content = noteData.content;

    console.log("[Persona] Extracted:", {
      title,
      domain,
      contentLength: content?.length,
      contentPreview: content ? content.substring(0, 100) : "NO CONTENT",
      noteDataKeys: Object.keys(noteData),
      hasMetadata: !!noteData.metadata,
    });

    if (!content) {
      console.error(
        "[Persona] Note data structure:",
        JSON.stringify(noteData, null, 2),
      );
      throw new Error("Note content is empty");
    }

    // Map domain short names to folder names (e.g., "signals" -> "02-Signals")
    const domainMap = {
      scrolls: "03-Scrolls",
      sigils: "01-Sigils",
      signals: "02-Signals",
      glyphs: "04-Glyphs",
      grids: "05-Grids",
    };

    const folderName = domainMap[domain.toLowerCase()] || domain;

    console.log("[Persona] Saving note:", { title, domain, folderName });

    // Use Polly Notes API to create the note
    const response = await fetch("http://127.0.0.1:11436/polly/notes/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: title,
        domain: folderName,
        content: content,
        check_duplicates: true, // Enable duplicate detection
      }),
    });

    if (!response.ok) {
      // Handle HTTP errors (like 409 Conflict)
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.error || errorMessage;
      } catch (e) {
        // Response wasn't JSON, use status text
      }
      throw new Error(errorMessage);
    }

    const result = await response.json();

    if (result.status === "similar_found") {
      // Show duplicate detection UI
      console.log("[Persona] Similar notes found:", result.similar_notes);

      const message =
        `Found ${result.similar_notes.length} similar note(s):\n` +
        result.similar_notes
          .map(
            (n) => `- ${n.title} (${Math.round(n.similarity * 100)}% similar)`,
          )
          .join("\n") +
        "\n\nDo you still want to create this note?";

      if (!confirm(message)) {
        console.log("[Persona] User cancelled note creation due to duplicates");
        return;
      }

      // User confirmed, create anyway
      const createResponse = await fetch(
        "http://127.0.0.1:11436/polly/notes/create",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: title,
            domain: folderName,
            content: content,
            check_duplicates: false, // Skip duplicate check this time
          }),
        },
      );

      const createResult = await createResponse.json();

      if (!createResult.success) {
        throw new Error(createResult.error || "Failed to create note");
      }

      console.log("[Persona] Note created:", createResult.note.path);
      alert(`Note saved: ${createResult.note.title}`);
    } else if (result.success) {
      // Note created successfully
      console.log("[Persona] Note created:", result.note.path);
      alert(`Note saved: ${result.note.title}`);
    } else {
      throw new Error(result.error || "Failed to create note");
    }

    // Trigger re-index to update RAG
    setTimeout(async () => {
      try {
        await fetch("http://127.0.0.1:11436/polly/notes/index/build", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ force: false }),
        });
        console.log("[Persona] Triggered notes re-index");
      } catch (error) {
        console.error("[Persona] Failed to trigger re-index:", error);
      }
    }, 1000);
  } catch (error) {
    console.error("[Persona] Failed to save note:", error);
    alert(`Failed to save note: ${error.message}`);
  }
}

// ============================================================================
// CURRICULUM API FUNCTIONS
// ============================================================================

/**
 * Fetch all curricula
 * @param {string} status - Optional status filter (draft, active, paused, completed)
 * @returns {Promise<Array>} List of curricula
 */
async function fetchCurricula(status = null) {
  try {
    const url = status
      ? `${API_URL}/polly/curricula/list?status=${status}`
      : `${API_URL}/polly/curricula/list`;
    const result = await safeFetch(url);
    if (!result.ok) {
      throw new Error(result.error || "Failed to fetch curricula");
    }
    return result.data.curricula || [];
  } catch (error) {
    console.error("[Curriculum] Failed to fetch curricula:", error);
    showToast("Failed to load curricula", "error");
    return [];
  }
}

/**
 * Get full curriculum details by ID
 * @param {string} curriculumId - Curriculum ID
 * @returns {Promise<Object>} Curriculum object
 */
async function getCurriculum(curriculumId) {
  try {
    const result = await safeFetch(
      `${API_URL}/polly/curricula/${curriculumId}`,
    );
    console.log("[getCurriculum] safeFetch result:", {
      ok: result.ok,
      hasData: !!result.data,
      dataType: typeof result.data,
    });

    if (!result.ok) {
      throw new Error(result.error || "Failed to get curriculum");
    }

    // Log the actual data structure
    console.log(
      "[getCurriculum] result.data keys:",
      Object.keys(result.data || {}),
    );
    console.log("[getCurriculum] sections:", {
      exists: "sections" in (result.data || {}),
      type: typeof result.data?.sections,
      isArray: Array.isArray(result.data?.sections),
      length: result.data?.sections?.length,
    });

    return result.data;
  } catch (error) {
    console.error("[Curriculum] Failed to get curriculum:", error);
    showToast("Failed to load curriculum", "error");
    throw error;
  }
}

/**
 * Create a new curriculum
 * @param {string} title - Curriculum title
 * @param {string} goal - Learning goal
 * @param {Array} sections - List of curriculum sections
 * @param {Object} metadata - Additional metadata (current_level, estimated_duration, etc.)
 * @returns {Promise<Object>} Created curriculum
 */
async function createCurriculum(title, goal, sections, metadata = {}) {
  try {
    const response = await fetch(`${API_URL}/polly/curricula/create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        goal,
        sections,
        ...metadata,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast(`Curriculum "${title}" created`, "success");
      return result.curriculum;
    } else {
      throw new Error(result.error || "Failed to create curriculum");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to create curriculum:", error);
    showToast("Failed to create curriculum", "error");
    throw error;
  }
}

/**
 * Activate a curriculum (draft → active)
 * @param {string} curriculumId - Curriculum ID
 * @returns {Promise<Object>} Updated curriculum
 */
async function activateCurriculum(curriculumId) {
  try {
    const response = await fetch(
      `${API_URL}/polly/curricula/${curriculumId}/activate`,
      {
        method: "POST",
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast("Curriculum activated", "success");
      return result.curriculum;
    } else {
      throw new Error(result.error || "Failed to activate curriculum");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to activate curriculum:", error);
    showToast("Failed to activate curriculum", "error");
    throw error;
  }
}

/**
 * Pause a curriculum
 * @param {string} curriculumId - Curriculum ID
 * @returns {Promise<Object>} Updated curriculum
 */
async function pauseCurriculum(curriculumId) {
  try {
    const response = await fetch(
      `${API_URL}/polly/curricula/${curriculumId}/pause`,
      {
        method: "POST",
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast("Curriculum paused", "success");
      return true;
    } else {
      throw new Error(result.error || "Failed to pause curriculum");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to pause curriculum:", error);
    showToast("Failed to pause curriculum", "error");
    throw error;
  }
}

/**
 * Complete a curriculum
 * @param {string} curriculumId - Curriculum ID
 * @returns {Promise<Object>} Updated curriculum
 */
async function completeCurriculum(curriculumId) {
  try {
    const response = await fetch(
      `${API_URL}/polly/curricula/${curriculumId}/complete`,
      {
        method: "POST",
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast("Curriculum completed! 🎉", "success");
      return true;
    } else {
      throw new Error(result.error || "Failed to complete curriculum");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to complete curriculum:", error);
    showToast("Failed to complete curriculum", "error");
    throw error;
  }
}

/**
 * Delete a curriculum
 * @param {string} curriculumId - Curriculum ID
 * @returns {Promise<boolean>} Success status
 */
async function deleteCurriculum(curriculumId) {
  try {
    const response = await fetch(`${API_URL}/polly/curricula/${curriculumId}`, {
      method: "DELETE",
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast("Curriculum deleted", "success");
      return true;
    } else {
      throw new Error(result.error || "Failed to delete curriculum");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to delete curriculum:", error);
    showToast("Failed to delete curriculum", "error");
    return false;
  }
}

/**
 * Start a section
 * @param {string} curriculumId - Curriculum ID
 * @param {string} sectionId - Section ID
 * @returns {Promise<Object>} Updated section
 */
async function startSection(curriculumId, sectionId) {
  try {
    const response = await fetch(
      `${API_URL}/polly/curricula/${curriculumId}/sections/${sectionId}/start`,
      { method: "POST" },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast(`Started: ${result.section.title}`, "success");
      return result.section;
    } else {
      throw new Error(result.error || "Failed to start section");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to start section:", error);
    showToast("Failed to start section", "error");
    throw error;
  }
}

/**
 * Complete a section with reflection
 * @param {string} curriculumId - Curriculum ID
 * @param {string} sectionId - Section ID
 * @param {Object} reflection - Reflection data {mastery_level, struggles, breakthroughs, time_spent}
 * @returns {Promise<Object>} Updated section
 */
async function completeSection(curriculumId, sectionId, reflection = {}) {
  try {
    const response = await fetch(
      `${API_URL}/polly/curricula/${curriculumId}/sections/${sectionId}/complete`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reflection),
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    if (result.status === "success") {
      showToast("Section completed!", "success");
      return result.section;
    } else {
      throw new Error(result.error || "Failed to complete section");
    }
  } catch (error) {
    console.error("[Curriculum] Failed to complete section:", error);
    showToast("Failed to complete section", "error");
    throw error;
  }
}

/**
 * Get curriculum progress summary
 * @param {string} curriculumId - Curriculum ID
 * @returns {Promise<Object>} Progress summary
 */
async function getCurriculumProgress(curriculumId) {
  try {
    const result = await safeFetch(
      `${API_URL}/polly/curricula/${curriculumId}/progress`,
    );
    if (!result.ok) {
      throw new Error(result.error || "Failed to get progress");
    }
    return result.data;
  } catch (error) {
    console.error("[Curriculum] Failed to get progress:", error);
    showToast("Failed to load progress", "error");
    throw error;
  }
}

/**
 * Enrich a section (placeholder for Phase 4)
 * @param {string} curriculumId - Curriculum ID
 * @param {string} sectionId - Section ID
 * @returns {Promise<Object>} Enriched section
 */
async function enrichSection(curriculumId, sectionId) {
  try {
    console.log(
      "[Enrich Section] Starting enrichment for",
      curriculumId,
      sectionId,
    );

    const result = await safeFetch(
      `${API_URL}/polly/curricula/${curriculumId}/sections/${sectionId}/enrich`,
      { method: "POST" },
    );

    if (!result.ok) {
      throw new Error(result.error || "Failed to enrich section");
    }

    const data = result.data;

    if (data.status === "already_enriched") {
      console.log("[Enrich Section] Using cached enrichment");
      showToast("Section materials loaded", "success");
    } else if (data.status === "success") {
      console.log("[Enrich Section] New enrichment generated");
      showToast("Section enriched with materials!", "success");
    }

    return data.enrichment;
  } catch (error) {
    console.error("[Curriculum] Failed to enrich section:", error);
    showToast("Failed to enrich section", "error");
    throw error;
  }
}

/**
 * Start a learning session (placeholder for Phase 6)
 * @param {string} curriculumId - Curriculum ID
 * @param {string} sectionId - Section ID
 * @returns {Promise<Object>} Session data
 */
async function startLearningSession(curriculumId, sectionId) {
  try {
    const response = await safeFetch(
      `${API_URL}/polly/curricula/${curriculumId}/session/start`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ section_id: sectionId }),
      },
    );
    return await response.json();
  } catch (error) {
    console.error("[Curriculum] Failed to start session:", error);
    showToast("Failed to start learning session", "error");
    throw error;
  }
}

/**
 * End a learning session (placeholder for Phase 6)
 * @param {string} sessionId - Session ID
 * @param {Object} summary - Session summary data
 * @returns {Promise<Object>} Session result
 */
async function endLearningSession(sessionId, summary = {}) {
  try {
    const response = await safeFetch(`${API_URL}/polly/curricula/session/end`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, ...summary }),
    });
    return await response.json();
  } catch (error) {
    console.error("[Curriculum] Failed to end session:", error);
    showToast("Failed to end learning session", "error");
    throw error;
  }
}

// ============================================================================
// END CURRICULUM API FUNCTIONS
// ============================================================================

// ============================================================================
// CURRICULUM TEMPLATE API FUNCTIONS
// ============================================================================

/**
 * Fetch all curriculum templates, optionally filtered by category
 * @param {string|null} category - Filter by category: 'programming', 'framework', 'skill', 'problem-solving', 'exploration'
 * @returns {Promise<Array>} List of templates
 */
async function fetchCurriculumTemplates(category = null) {
  try {
    const url = category
      ? `${API_URL}/polly/curricula/templates/list?category=${category}`
      : `${API_URL}/polly/curricula/templates/list`;
    const response = await safeFetch(url);
    const data = await response.json();
    return data.templates || [];
  } catch (error) {
    console.error("[Template] Failed to fetch templates:", error);
    showToast("Failed to load templates", "error");
    return [];
  }
}

/**
 * Get full template details by ID
 * @param {string} templateId - Template ID
 * @returns {Promise<Object>} Template object with structure
 */
async function getCurriculumTemplate(templateId) {
  try {
    const response = await safeFetch(
      `${API_URL}/polly/curricula/templates/${templateId}`,
    );
    return await response.json();
  } catch (error) {
    console.error("[Template] Failed to get template:", error);
    showToast("Failed to load template", "error");
    throw error;
  }
}

/**
 * Load and render curricula in Learning page sidebar
 */
async function loadLearningSidebarCurricula() {
  const container = document.getElementById("learning-curricula-list");
  if (!container) {
    console.error("[Learning] Curricula list container not found");
    return;
  }

  try {
    const curricula = await fetchCurricula();

    if (!curricula || curricula.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 20px; color: #808080; font-size: 13px;">
          <p style="margin-bottom: 12px;">No curricula yet</p>
          <p style="font-size: 12px; color: #606060;">
            Create one by chatting with the Professor persona in "curriculum" mode
          </p>
        </div>
      `;
      return;
    }

    // Render curriculum list
    container.innerHTML = curricula
      .map(
        (c) => `
      <div class="curriculum-sidebar-item" data-curriculum-id="${c.id}" style="
        padding: 12px;
        margin-bottom: 8px;
        background: ${c.status === "active" ? "#2a3a2a" : "#252525"};
        border: 1px solid ${c.status === "active" ? "#4a6a4a" : "#2a2a2a"};
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
      ">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 6px;">
          <div style="flex: 1; font-size: 13px; font-weight: 500; color: #e0e0e0;">
            ${c.title}
          </div>
          <span class="curriculum-status-badge" style="
            padding: 2px 6px;
            font-size: 10px;
            border-radius: 3px;
            text-transform: uppercase;
            font-weight: 600;
            background: ${c.status === "active" ? "#4a6a4a" : c.status === "completed" ? "#4a5a6a" : "#3a3a3a"};
            color: ${c.status === "active" ? "#8fd98f" : c.status === "completed" ? "#8fb9df" : "#808080"};
          ">${c.status}</span>
        </div>
        
        <div style="font-size: 11px; color: #808080; margin-bottom: 8px;">
          ${c.completed_sections}/${c.total_sections} sections
        </div>
        
        <div class="progress-bar" style="height: 4px; background: #1a1a1a; border-radius: 2px; overflow: hidden; margin-bottom: 8px;">
          <div style="height: 100%; background: ${c.status === "active" ? "#8fd98f" : "#4a6a4a"}; width: ${c.completion_percentage}%;"></div>
        </div>
        
        <div class="curriculum-actions" style="display: flex; gap: 4px;">
          ${
            c.status === "draft"
              ? `
            <button class="btn-activate-curriculum" data-id="${c.id}" style="
              flex: 1;
              padding: 4px 8px;
              font-size: 11px;
              background: #4a6a4a;
              color: #8fd98f;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">Activate</button>
          `
              : ""
          }
          
          ${
            c.status === "active"
              ? `
            <button class="btn-pause-curriculum" data-id="${c.id}" style="
              flex: 1;
              padding: 4px 8px;
              font-size: 11px;
              background: #3a3a3a;
              color: #e0e0e0;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">Pause</button>
            <button class="btn-view-curriculum" data-id="${c.id}" style="
              flex: 1;
              padding: 4px 8px;
              font-size: 11px;
              background: #4a5a6a;
              color: #8fb9df;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">Continue</button>
          `
              : ""
          }
          
          ${
            c.status === "paused"
              ? `
            <button class="btn-resume-curriculum" data-id="${c.id}" style="
              flex: 1;
              padding: 4px 8px;
              font-size: 11px;
              background: #4a6a4a;
              color: #8fd98f;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">Resume</button>
          `
              : ""
          }
          
          <button class="btn-delete-curriculum" data-id="${c.id}" style="
            padding: 4px 8px;
            font-size: 11px;
            background: transparent;
            color: #e06c75;
            border: 1px solid #e06c75;
            border-radius: 4px;
            cursor: pointer;
          ">Delete</button>
        </div>
      </div>
    `,
      )
      .join("");

    // Attach event listeners
    container.querySelectorAll(".btn-activate-curriculum").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        await handleActivateCurriculum(id);
        await loadLearningSidebarCurricula(); // Reload
      });
    });

    container.querySelectorAll(".btn-pause-curriculum").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        await handlePauseCurriculum(id);
        await loadLearningSidebarCurricula(); // Reload
      });
    });

    container.querySelectorAll(".btn-resume-curriculum").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        await handleActivateCurriculum(id); // Resume uses same endpoint
        await loadLearningSidebarCurricula(); // Reload
      });
    });

    container.querySelectorAll(".btn-delete-curriculum").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        e.stopPropagation();
        const id = btn.dataset.id;
        if (confirm("Are you sure you want to delete this curriculum?")) {
          await handleDeleteCurriculum(id);
          await loadLearningSidebarCurricula(); // Reload
        }
      });
    });

    container
      .querySelectorAll(".btn-view-curriculum, .curriculum-sidebar-item")
      .forEach((el) => {
        el.addEventListener("click", async () => {
          const item = el.closest(".curriculum-sidebar-item");
          if (!item) return;
          const id = item.dataset.curriculumId;
          await loadCurriculumDetail(id);
        });
      });
  } catch (error) {
    console.error("[Learning] Error loading curricula:", error);
    container.innerHTML = `
      <div style="text-align: center; padding: 20px; color: #e06c75; font-size: 13px;">
        Failed to load curricula
      </div>
    `;
  }
}

/**
 * Detect appropriate template based on learning goal
 * @param {string} goal - Learning goal description
 * @returns {Promise<Object>} Detection result with template_id, confidence, reasoning
 */
async function detectCurriculumTemplate(goal) {
  try {
    const result = await safeFetch(
      `${API_URL}/polly/curricula/templates/detect`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal }),
      },
    );
    if (!result.ok) {
      throw new Error(result.error || "Failed to detect template");
    }
    return result.data;
  } catch (error) {
    console.error("[Template] Failed to detect template:", error);
    showToast("Failed to detect template", "error");
    throw error;
  }
}

/**
 * Customize template with user-specific information
 * @param {string} templateId - Template ID
 * @param {Object} customizations - Customization data (title, goal, topic, level, etc.)
 * @returns {Promise<Object>} Customized curriculum data
 */
async function customizeCurriculumTemplate(templateId, customizations) {
  try {
    const result = await safeFetch(
      `${API_URL}/polly/curricula/templates/${templateId}/customize`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(customizations),
      },
    );
    if (!result.ok) {
      throw new Error(result.error || "Failed to customize template");
    }
    if (result.data.success) {
      return result.data.curriculum;
    } else {
      throw new Error(result.data.error || "Failed to customize template");
    }
  } catch (error) {
    console.error("[Template] Failed to customize template:", error);
    showToast("Failed to customize template", "error");
    throw error;
  }
}

// ============================================================================
// END CURRICULUM TEMPLATE API FUNCTIONS
// ============================================================================

// ============================================================================
// CURRICULUM UI RENDERING (Phase 23 - Engagement)
// ============================================================================

// Global state
let currentCurriculumDetailId = null;
let currentSectionForCompletion = null;

/**
 * Load and display curricula list
 */
async function loadCurriculaView() {
  console.log("[Curricula View] Loading curricula list");
  const container = document.getElementById("curricula-list");

  if (!container) {
    console.error("[Curricula View] Container not found");
    return;
  }

  // Show loading state
  container.innerHTML =
    '<div class="loading-spinner">Loading curricula...</div>';

  try {
    const curricula = await fetchCurricula();
    console.log("[Curricula View] Loaded curricula:", curricula);

    if (!curricula || curricula.length === 0) {
      container.innerHTML = `
        <div class="curriculum-empty">
          <i data-lucide="graduation-cap" style="width: 48px; height: 48px; opacity: 0.5;"></i>
          <p>no curricula yet</p>
          <p style="font-size: 0.9em; margin-top: 8px;">
            create a curriculum by chatting with the Professor persona in "curriculum" mode
          </p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    // Render curriculum cards
    container.innerHTML = curricula
      .map((c) => renderCurriculumCard(c))
      .join("");
    lucide.createIcons();
  } catch (error) {
    console.error("[Curricula View] Error loading curricula:", error);
    container.innerHTML = `
      <div class="curriculum-empty">
        <p>failed to load curricula</p>
        <button class="btn btn-secondary" onclick="loadCurriculaView()">retry</button>
      </div>
    `;
  }
}

/**
 * Render a curriculum card
 * @param {Object} curriculum - Curriculum object
 * @returns {string} HTML string
 */
function renderCurriculumCard(curriculum) {
  const statusClass = curriculum.status.toLowerCase();
  const completionPercent = curriculum.completion_percentage || 0;

  return `
    <div class="curriculum-card" onclick="loadCurriculumDetail('${curriculum.id}')">
      <div class="curriculum-card-header">
        <h3 class="curriculum-card-title">${curriculum.title}</h3>
        <span class="curriculum-status-badge ${statusClass}">${curriculum.status}</span>
      </div>
      
      ${curriculum.goal ? `<p class="curriculum-card-goal">${curriculum.goal}</p>` : ""}
      
      <div class="curriculum-card-progress">
        <div class="curriculum-progress-bar">
          <div class="curriculum-progress-fill" style="width: ${completionPercent}%"></div>
        </div>
        
        <div class="curriculum-card-stats">
          <span class="curriculum-stat">
            <i data-lucide="check-circle"></i>
            <span>${curriculum.completed_sections}/${curriculum.total_sections}</span>
          </span>
          <span class="curriculum-stat">
            <i data-lucide="percent"></i>
            <span>${Math.round(completionPercent)}%</span>
          </span>
          ${
            curriculum.estimated_duration
              ? `
            <span class="curriculum-stat">
              <i data-lucide="clock"></i>
              <span>${curriculum.estimated_duration}</span>
            </span>
          `
              : ""
          }
        </div>
      </div>
    </div>
  `;
}

/**
 * Load and display curriculum detail view
 * @param {string} curriculumId - Curriculum ID
 */
async function loadCurriculumDetail(curriculumId) {
  console.log("[Curriculum Detail] Loading curriculum:", curriculumId);
  currentCurriculumDetailId = curriculumId;

  // Show in learning view center area
  const learningDashboard = document.getElementById("learning-dashboard");
  const learningSession = document.getElementById("learning-session");

  if (!learningDashboard || !learningSession) {
    console.error("[Curriculum Detail] Learning view elements not found", {
      dashboard: !!learningDashboard,
      session: !!learningSession,
    });
    return;
  }

  // Hide dashboard, show session area for curriculum
  learningDashboard.classList.add("hidden");
  learningSession.classList.remove("hidden");

  const sessionHeader = document.getElementById("session-header");
  const sessionContent = document.getElementById("session-content");

  if (!sessionHeader || !sessionContent) {
    console.error("[Curriculum Detail] Session elements not found");
    return;
  }

  try {
    const curriculum = await getCurriculum(curriculumId);
    console.log("[Curriculum Detail] Loaded:", curriculum);
    console.log(
      "[Curriculum Detail] Sections type:",
      typeof curriculum.sections,
      "Is array:",
      Array.isArray(curriculum.sections),
    );
    console.log(
      "[Curriculum Detail] Sections length:",
      curriculum.sections?.length,
    );

    // Render curriculum detail in session area
    sessionHeader.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px; border-bottom: 1px solid #2a2a2a;">
        <div style="flex: 1;">
          <div style="font-size: 13px; color: #808080; margin-bottom: 4px;">CURRICULUM</div>
          <div style="font-size: 16px; font-weight: 600; color: #e0e0e0;">${curriculum.title}</div>
        </div>
        <button class="btn btn-sm btn-secondary" id="btn-close-curriculum">
          <i data-lucide="x" style="width: 14px; height: 14px;"></i>
          Close
        </button>
      </div>
    `;

    sessionContent.innerHTML = `
      <div style="padding: 20px;">
        ${
          curriculum.goal
            ? `
          <div style="background: #252525; padding: 16px; border-radius: 8px; margin-bottom: 20px; border-left: 3px solid #4a6a4a;">
            <div style="font-size: 12px; text-transform: uppercase; color: #808080; margin-bottom: 6px;">Goal</div>
            <div style="font-size: 14px; color: #e0e0e0;">${curriculum.goal}</div>
          </div>
        `
            : ""
        }
        
        <!-- Progress Bar -->
        <div style="margin-bottom: 20px; background: #252525; padding: 16px; border-radius: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-size: 12px; color: #808080;">Overall Progress</div>
            <div style="font-size: 14px; font-weight: 600; color: #8fd98f;">${Math.round(curriculum.completion_percentage)}%</div>
          </div>
          <div style="width: 100%; height: 8px; background: #1a1a1a; border-radius: 4px; overflow: hidden;">
            <div style="width: ${curriculum.completion_percentage}%; height: 100%; background: linear-gradient(90deg, #4a6a4a 0%, #8fd98f 100%); transition: width 0.3s ease;"></div>
          </div>
          <div style="display: flex; gap: 8px; margin-top: 12px; font-size: 11px;">
            <span style="color: #8fd98f;">
              <i data-lucide="check-circle" style="width: 12px; height: 12px; margin-right: 4px;"></i>
              ${curriculum.completed_sections} completed
            </span>
            <span style="color: #f0903b;">
              <i data-lucide="circle-dot" style="width: 12px; height: 12px; margin-right: 4px;"></i>
              ${curriculum.in_progress_sections || 0} in progress
            </span>
            <span style="color: #606060;">
              <i data-lucide="circle" style="width: 12px; height: 12px; margin-right: 4px;"></i>
              ${curriculum.total_sections - curriculum.completed_sections - (curriculum.in_progress_sections || 0)} not started
            </span>
          </div>
        </div>
        
        <!-- Stats Grid -->
        <div style="display: flex; gap: 12px; margin-bottom: 24px;">
          <div style="flex: 1; background: #252525; padding: 12px; border-radius: 6px;">
            <div style="font-size: 11px; color: #808080; margin-bottom: 4px;">Sections</div>
            <div style="font-size: 18px; font-weight: 600; color: #e0e0e0;">${curriculum.completed_sections}/${curriculum.total_sections}</div>
          </div>
          <div style="flex: 1; background: #252525; padding: 12px; border-radius: 6px;">
            <div style="font-size: 11px; color: #808080; margin-bottom: 4px;">Status</div>
            <div style="font-size: 14px; font-weight: 600; color: ${curriculum.status === "active" ? "#8fd98f" : "#808080"}; text-transform: uppercase;">${curriculum.status}</div>
          </div>
        </div>

        <div style="margin-bottom: 16px;">
          <h3 style="font-size: 14px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">Curriculum Outline</h3>
          <div id="curriculum-sections-list">
            ${renderCurriculumSections(curriculum)}
          </div>
        </div>
      </div>
    `;

    // Re-initialize Lucide icons
    if (typeof lucide !== "undefined") {
      lucide.createIcons();
    }

    // Attach close button handler
    document
      .getElementById("btn-close-curriculum")
      ?.addEventListener("click", () => {
        learningDashboard.classList.remove("hidden");
        learningSession.classList.add("hidden");
      });

    // Attach section action handlers
    attachCurriculumSectionHandlers(curriculum);
  } catch (error) {
    console.error("[Curriculum Detail] Error loading:", error);
    sessionContent.innerHTML = `
      <div style="padding: 40px; text-align: center; color: #e06c75;">
        Failed to load curriculum details
      </div>
    `;
  }
}

/**
 * Render curriculum sections as expandable list
 */
function renderCurriculumSections(curriculum) {
  console.log("[Render Sections] Input curriculum:", curriculum);
  console.log("[Render Sections] Curriculum type:", typeof curriculum);
  console.log("[Render Sections] Curriculum is null?", curriculum === null);
  console.log(
    "[Render Sections] Curriculum is undefined?",
    curriculum === undefined,
  );
  console.log(
    "[Render Sections] Curriculum keys:",
    curriculum ? Object.keys(curriculum) : "N/A",
  );
  console.log("[Render Sections] Sections property:", curriculum?.sections);
  console.log("[Render Sections] Sections type:", typeof curriculum?.sections);

  if (!curriculum || typeof curriculum !== "object") {
    console.error("[Render Sections] Invalid curriculum object:", curriculum);
    return '<div style="color: #e06c75; font-size: 13px; padding: 20px; text-align: center;">Error: Invalid curriculum data</div>';
  }

  const sections = curriculum.sections || [];

  // Ensure sections is an array
  if (!Array.isArray(sections)) {
    console.error(
      "[Render Sections] Sections is not an array:",
      typeof sections,
      sections,
    );
    return '<div style="color: #e06c75; font-size: 13px; padding: 20px; text-align: center;">Error: Invalid sections data (not an array)</div>';
  }

  console.log("[Render Sections] Processing", sections.length, "sections");

  // Group by parent_id for hierarchical structure
  const weekSections = sections.filter((s) => s.type === "week");
  const subSections = sections.filter(
    (s) => s.type === "subheading" || s.parent_id,
  );

  let html = "";

  // Render each week with its subsections
  weekSections.forEach((week) => {
    const children = subSections.filter((s) => s.parent_id === week.id);
    const weekCompleted = children.filter(
      (s) => s.status === "completed",
    ).length;
    const weekTotal = children.length;

    html += `
      <div class="curriculum-week" style="margin-bottom: 12px; border: 1px solid #2a2a2a; border-radius: 6px; overflow: hidden;">
        <div class="curriculum-week-header" style="
          padding: 12px;
          background: #252525;
          cursor: pointer;
          display: flex;
          justify-content: space-between;
          align-items: center;
        " data-week="${week.id}">
          <div style="font-weight: 600; font-size: 13px; color: #e0e0e0;">${week.title}</div>
          <div style="font-size: 12px; color: #808080;">${weekCompleted}/${weekTotal} completed</div>
        </div>
        <div class="curriculum-week-content" style="padding: 8px;">
          ${children.map((s) => renderCurriculumSection(s, curriculum.id)).join("")}
        </div>
      </div>
    `;
  });

  // Render sections without parent (if any)
  const orphanSections = sections.filter(
    (s) => s.type !== "week" && !s.parent_id,
  );
  if (orphanSections.length > 0) {
    html += orphanSections
      .map((s) => renderCurriculumSection(s, curriculum.id))
      .join("");
  }

  return (
    html ||
    '<div style="color: #808080; font-size: 13px; padding: 20px; text-align: center;">No sections defined</div>'
  );
}

/**
 * Render individual section
 */
function renderCurriculumSection(section, curriculumId) {
  const statusIcon =
    section.status === "completed"
      ? "check-circle"
      : section.status === "in_progress"
        ? "circle-dot"
        : "circle";
  const statusColor =
    section.status === "completed"
      ? "#8fd98f"
      : section.status === "in_progress"
        ? "#f0903b"
        : "#606060";

  // Helper to format mastery level as stars
  const renderMasteryStars = (level) => {
    if (!level) return "";
    const stars = "★".repeat(level) + "☆".repeat(5 - level);
    return `<span style="color: #f0c030; font-size: 13px; letter-spacing: 1px;" title="Mastery Level: ${level}/5">${stars}</span>`;
  };

  // Helper to format timestamps
  const formatTimestamp = (timestamp) => {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  // Helper to format time spent
  const formatTimeSpent = (minutes) => {
    if (!minutes) return "0m";
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
  };

  return `
    <div class="curriculum-section-item" data-section-id="${section.id}" style="
      padding: 12px;
      margin-bottom: 6px;
      background: #1e1e1e;
      border-radius: 6px;
      border-left: 3px solid ${statusColor};
    ">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px;">
        <div style="flex: 1; display: flex; align-items: flex-start; gap: 10px;">
          <i data-lucide="${statusIcon}" style="width: 16px; height: 16px; color: ${statusColor}; margin-top: 2px;"></i>
          <div style="flex: 1;">
            <div style="font-size: 13px; font-weight: 500; color: #e0e0e0; margin-bottom: 4px;">${section.title}</div>
            ${
              section.description
                ? `
              <div style="font-size: 11px; color: #808080; margin-bottom: 6px;">${section.description}</div>
            `
                : ""
            }
            
            <!-- Progress Info -->
            <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap; font-size: 11px; color: #808080;">
              ${
                section.estimated_time
                  ? `
                <span style="display: flex; align-items: center; gap: 4px;">
                  <i data-lucide="clock" style="width: 11px; height: 11px;"></i>
                  ${section.estimated_time}
                </span>
              `
                  : ""
              }
              ${
                section.concepts && section.concepts.length > 0
                  ? `
                <span style="display: flex; align-items: center; gap: 4px;">
                  <i data-lucide="tag" style="width: 11px; height: 11px;"></i>
                  ${section.concepts.length} concepts
                </span>
              `
                  : ""
              }
              ${
                section.time_spent_minutes > 0
                  ? `
                <span style="display: flex; align-items: center; gap: 4px; color: #8fb9df;">
                  <i data-lucide="timer" style="width: 11px; height: 11px;"></i>
                  ${formatTimeSpent(section.time_spent_minutes)} spent
                </span>
              `
                  : ""
              }
              ${
                section.completed_at
                  ? `
                <span style="display: flex; align-items: center; gap: 4px; color: #8fd98f;">
                  <i data-lucide="calendar-check" style="width: 11px; height: 11px;"></i>
                  Completed ${formatTimestamp(section.completed_at)}
                </span>
              `
                  : ""
              }
            </div>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="curriculum-section-actions" style="display: flex; align-items: center; gap: 8px;">
          ${
            section.status === "completed" && section.mastery_level
              ? `
            <div style="margin-right: 4px;">
              ${renderMasteryStars(section.mastery_level)}
            </div>
          `
              : ""
          }
          
          ${
            section.status === "not_started"
              ? `
            <button class="btn-start-section" data-curriculum-id="${curriculumId}" data-section-id="${section.id}" style="
              padding: 6px 14px;
              font-size: 11px;
              background: #4a6a4a;
              color: #8fd98f;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">Start</button>
          `
              : ""
          }
          ${
            section.status === "in_progress"
              ? `
            <button class="btn-view-section" data-curriculum-id="${curriculumId}" data-section-id="${section.id}" style="
              padding: 6px 14px;
              font-size: 11px;
              background: #4a5a6a;
              color: #8fb9df;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">View</button>
            <button class="btn-complete-section" data-curriculum-id="${curriculumId}" data-section-id="${section.id}" style="
              padding: 6px 14px;
              font-size: 11px;
              background: #4a6a4a;
              color: #8fd98f;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">Complete</button>
          `
              : ""
          }
          ${
            section.status === "completed"
              ? `
            <button class="btn-view-section" data-curriculum-id="${curriculumId}" data-section-id="${section.id}" style="
              padding: 6px 14px;
              font-size: 11px;
              background: #4a5a6a;
              color: #8fb9df;
              border: none;
              border-radius: 4px;
              cursor: pointer;
              font-weight: 500;
            ">View</button>
          `
              : ""
          }
        </div>
      </div>
    </div>
  `;
}

/**
 * Attach event handlers to section action buttons
 */
function attachCurriculumSectionHandlers(curriculum) {
  document.querySelectorAll(".btn-start-section").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const curriculumId = btn.dataset.curriculumId;
      const sectionId = btn.dataset.sectionId;
      await handleStartSection(curriculumId, sectionId);
      await loadCurriculumDetail(curriculumId); // Reload detail view
      await loadLearningSidebarCurricula(); // Refresh sidebar
    });
  });

  document.querySelectorAll(".btn-view-section").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const curriculumId = btn.dataset.curriculumId;
      const sectionId = btn.dataset.sectionId;
      await handleViewSection(curriculumId, sectionId);
    });
  });

  document.querySelectorAll(".btn-complete-section").forEach((btn) => {
    btn.addEventListener("click", () => {
      const curriculumId = btn.dataset.curriculumId;
      const sectionId = btn.dataset.sectionId;
      const section = curriculum.sections.find((s) => s.id === sectionId);
      showCompleteSectionDialog(
        curriculumId,
        sectionId,
        section?.title || "Section",
      );
    });
  });
}

/**
 * OLD VERSION - Load and display curriculum detail view in curricula page
 * @param {string} curriculumId - Curriculum ID
 */

/**
 * Toggle week section expansion
 */
function toggleWeekExpanded(headerElement) {
  const weekElement = headerElement.closest(".curriculum-week");
  if (weekElement) {
    weekElement.classList.toggle("collapsed");
    lucide.createIcons();
  }
}

/**
 * Handle activate curriculum button
 */
async function handleActivateCurriculum(curriculumId) {
  try {
    await activateCurriculum(curriculumId);
    // Reload detail view
    await loadCurriculumDetail(curriculumId);
  } catch (error) {
    console.error("[Curriculum] Activation failed:", error);
  }
}

/**
 * Handle pause curriculum button
 */
async function handlePauseCurriculum(curriculumId) {
  try {
    await pauseCurriculum(curriculumId);
    // Reload detail view
    await loadCurriculumDetail(curriculumId);
  } catch (error) {
    console.error("[Curriculum] Pause failed:", error);
  }
}

/**
 * Handle delete curriculum button
 */
async function handleDeleteCurriculum(curriculumId) {
  if (
    !confirm(
      "Are you sure you want to delete this curriculum? This cannot be undone.",
    )
  ) {
    return;
  }

  try {
    await deleteCurriculum(curriculumId);
    // Go back to list
    await loadCurriculaView();
  } catch (error) {
    console.error("[Curriculum] Delete failed:", error);
  }
}

/**
 * Handle start section button
 */
async function handleStartSection(curriculumId, sectionId) {
  try {
    console.log("[Start Section] Starting section:", curriculumId, sectionId);

    // Start the section (mark as in_progress)
    await startSection(curriculumId, sectionId);

    // Show loading message
    showToast("Enriching section with materials...", "info");

    // Show loading state in session content
    const sessionContent = document.getElementById("session-content");
    if (sessionContent) {
      sessionContent.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center;">
          <div class="loading-spinner" style="margin-bottom: 20px;"></div>
          <div style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 8px;">
            Enriching Section with Materials
          </div>
          <div style="font-size: 13px; color: #808080; max-width: 400px;">
            Generating detailed explanations, diagrams, examples, and exercises...
            <br/>This may take 10-30 seconds.
          </div>
        </div>
      `;
    }

    // Enrich the section (get materials)
    const enrichment = await enrichSection(curriculumId, sectionId);

    // Get curriculum to determine template type
    const curriculum = await getCurriculum(curriculumId);
    const templateId =
      curriculum?.curriculum_template_id || curriculum?.template_id;

    // Display enriched materials
    displaySectionMaterials(curriculumId, sectionId, enrichment, templateId);

    // Refresh sidebar
    await loadLearningSidebarCurricula();
  } catch (error) {
    console.error("[Curriculum] Start section failed:", error);

    // Show error in session content
    const sessionContent = document.getElementById("session-content");
    if (sessionContent) {
      sessionContent.innerHTML = `
        <div style="padding: 40px; text-align: center;">
          <div style="color: #e06c75; font-size: 16px; margin-bottom: 16px;">
            Failed to load section materials
          </div>
          <div style="color: #808080; font-size: 13px; margin-bottom: 20px;">
            ${error.message || "Unknown error"}
          </div>
          <button class="btn btn-secondary" onclick="loadCurriculumDetail('${curriculumId}')">
            Back to Curriculum
          </button>
        </div>
      `;
    }
  }
}

/**
 * View enriched section materials (for in_progress or completed sections)
 */
async function handleViewSection(curriculumId, sectionId) {
  try {
    console.log(
      "[View Section] Loading materials for:",
      curriculumId,
      sectionId,
    );

    // Show loading state
    const sessionContent = document.getElementById("session-content");
    if (sessionContent) {
      sessionContent.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center;">
          <div class="loading-spinner" style="margin-bottom: 20px;"></div>
          <div style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 8px;">
            Loading Section Materials
          </div>
        </div>
      `;
    }

    // Get enriched materials (will use cached version if available)
    const enrichment = await enrichSection(curriculumId, sectionId);

    // Get curriculum to determine template type
    const curriculum = await getCurriculum(curriculumId);
    const templateId =
      curriculum?.curriculum_template_id || curriculum?.template_id;

    // Display enriched materials
    displaySectionMaterials(curriculumId, sectionId, enrichment, templateId);
  } catch (error) {
    console.error("[View Section] Failed to load materials:", error);

    const sessionContent = document.getElementById("session-content");
    if (sessionContent) {
      sessionContent.innerHTML = `
        <div style="padding: 40px; text-align: center;">
          <div style="color: #e06c75; font-size: 16px; margin-bottom: 16px;">
            Failed to load section materials
          </div>
          <div style="color: #808080; font-size: 13px; margin-bottom: 20px;">
            ${error.message || "Unknown error"}
          </div>
          <button class="btn btn-secondary" onclick="loadCurriculumDetail('${curriculumId}')">
            Back to Curriculum
          </button>
        </div>
      `;
    }
  }
}

/**
 * Display enriched section materials in session view
 */
function displaySectionMaterials(
  curriculumId,
  sectionId,
  enrichment,
  templateId,
) {
  console.log(
    "[Display Materials] Showing enrichment for:",
    sectionId,
    enrichment,
  );
  console.log(
    "[Display Materials] Enrichment keys:",
    Object.keys(enrichment || {}),
  );
  console.log("[Display Materials] Template ID:", templateId);

  // Determine if this is a programming curriculum
  const isProgramming =
    templateId &&
    ["programming-language", "framework-library"].includes(templateId);
  const examplesHeading = isProgramming
    ? "Code Examples"
    : "Real-World Examples";
  const examplesIcon = isProgramming ? "code" : "book-open";

  const sessionContent = document.getElementById("session-content");
  if (!sessionContent) {
    console.error("[Display Materials] session-content element not found");
    return;
  }

  // Make sure the learning session view is visible
  const learningSession = document.getElementById("learning-session");
  if (learningSession) {
    console.log("[Display Materials] Showing learning-session div");
    learningSession.classList.remove("hidden");
  } else {
    console.error("[Display Materials] learning-session element not found");
  }

  // Get section info (from enrichment or fetch it)
  const sectionTitle = sectionId; // Will be improved when we have full section data

  let html = `
    <div style="padding: 20px; max-width: 900px; margin: 0 auto;">
      
      <!-- Section Header -->
      <div style="margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #2a2a2a;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="font-size: 20px; font-weight: 600; color: #e0e0e0; margin: 0;">
            ${sectionTitle}
          </h2>
          <button class="btn btn-secondary" onclick="loadCurriculumDetail('${curriculumId}')" style="padding: 6px 12px; font-size: 12px;">
            <i data-lucide="arrow-left" style="width: 14px; height: 14px;"></i>
            Back to Outline
          </button>
        </div>
      </div>
      
      <!-- Explanation -->
      ${
        enrichment.explanation
          ? `
        <div style="margin-bottom: 32px;">
          <h3 style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">
            <i data-lucide="book-open" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            Explanation
          </h3>
          <div class="markdown-content" style="color: #c8c8c8; line-height: 1.6;">
            ${marked.parse(enrichment.explanation)}
          </div>
        </div>
      `
          : ""
      }
      
      <!-- Diagrams -->
      ${
        enrichment.diagrams && enrichment.diagrams.length > 0
          ? `
        <div style="margin-bottom: 32px;">
          <h3 style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">
            <i data-lucide="git-graph" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            Visual Diagrams
          </h3>
          ${enrichment.diagrams
            .map(
              (diagram, idx) => `
            <div style="background: #252525; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
              ${diagram.caption ? `<div style="font-size: 13px; color: #808080; margin-bottom: 12px;">${diagram.caption}</div>` : ""}
              <div class="mermaid" style="background: white; padding: 20px; border-radius: 6px;">
                ${diagram.source}
              </div>
            </div>
          `,
            )
            .join("")}
        </div>
      `
          : ""
      }
      
      <!-- Examples -->
      ${
        enrichment.examples && enrichment.examples.length > 0
          ? `
        <div style="margin-bottom: 32px;">
          <h3 style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">
            <i data-lucide="${examplesIcon}" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            ${examplesHeading}
          </h3>
          ${enrichment.examples
            .map(
              (example, idx) => `
            <div style="background: #252525; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
              <div style="font-size: 14px; font-weight: 600; color: #e0e0e0; margin-bottom: 8px;">
                ${example.title}
              </div>
              ${
                example.code
                  ? `
                <pre style="background: #1a1a1a; padding: 12px; border-radius: 6px; overflow-x: auto; margin-bottom: 8px;"><code>${escapeHtml(example.code)}</code></pre>
              `
                  : ""
              }
              ${
                example.description
                  ? `
                <div style="font-size: 13px; color: #c8c8c8; margin-bottom: 8px; line-height: 1.6;">${example.description}</div>
              `
                  : ""
              }
              ${example.explanation ? `<div style="font-size: 13px; color: #a8a8a8; font-style: italic;">${example.explanation}</div>` : ""}
            </div>
          `,
            )
            .join("")}
        </div>
      `
          : ""
      }
      
      <!-- Exercises -->
      ${
        enrichment.exercises && enrichment.exercises.length > 0
          ? `
        <div style="margin-bottom: 32px;">
          <h3 style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">
            <i data-lucide="dumbbell" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            Practice Exercises
          </h3>
          ${enrichment.exercises
            .map((exercise, idx) => {
              const exerciseId = exercise.id || `exercise-${idx}`;
              const editorId = `editor-${curriculumId}-${sectionId}-${exerciseId}`;
              const outputId = `output-${curriculumId}-${sectionId}-${exerciseId}`;
              const feedbackId = `feedback-${curriculumId}-${sectionId}-${exerciseId}`;

              return `
            <div style="background: #252525; padding: 16px; border-radius: 8px; margin-bottom: 16px;" data-exercise-id="${exerciseId}">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div style="font-size: 14px; font-weight: 600; color: #e0e0e0;">
                  Exercise ${idx + 1}: ${exercise.title}
                </div>
                <div style="display: flex; gap: 8px;">
                  <button 
                    class="btn-run-code" 
                    data-editor-id="${editorId}"
                    data-output-id="${outputId}"
                    style="padding: 6px 12px; font-size: 11px; background: #4a6a4a; color: #8fd98f; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 4px;"
                  >
                    <i data-lucide="play" style="width: 12px; height: 12px;"></i>
                    Run Code
                  </button>
                  <button 
                    class="btn-check-solution" 
                    data-curriculum-id="${curriculumId}"
                    data-section-id="${sectionId}"
                    data-exercise-id="${exerciseId}"
                    data-editor-id="${editorId}"
                    data-output-id="${outputId}"
                    data-feedback-id="${feedbackId}"
                    style="padding: 6px 12px; font-size: 11px; background: #4a5a6a; color: #8fb9df; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 4px;"
                  >
                    <i data-lucide="check-circle" style="width: 12px; height: 12px;"></i>
                    Check Solution
                  </button>
                  <button 
                    class="btn-reset-code" 
                    data-editor-id="${editorId}"
                    data-starter-code="${escapeHtml(exercise.starter_code || "")}"
                    style="padding: 6px 12px; font-size: 11px; background: #3a3a3a; color: #808080; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; display: flex; align-items: center; gap: 4px;"
                  >
                    <i data-lucide="rotate-ccw" style="width: 12px; height: 12px;"></i>
                    Reset
                  </button>
                </div>
              </div>
              
              ${exercise.description ? `<div style="font-size: 13px; color: #c8c8c8; margin-bottom: 12px;">${exercise.description}</div>` : ""}
              
              <!-- Code Editor -->
              <div style="margin-bottom: 12px;">
                <textarea 
                  id="${editorId}" 
                  class="code-editor"
                  spellcheck="false"
                  style="
                    width: 100%; 
                    min-height: 150px; 
                    background: #1a1a1a; 
                    color: #e0e0e0; 
                    border: 1px solid #3a3a3a; 
                    border-radius: 6px; 
                    padding: 12px; 
                    font-family: 'Courier New', monospace; 
                    font-size: 13px;
                    resize: vertical;
                    outline: none;
                  "
                >${escapeHtml(exercise.starter_code || "")}</textarea>
              </div>
              
              <!-- Output Console -->
              <div id="${outputId}" style="display: none; background: #1a1a1a; border: 1px solid #3a3a3a; border-radius: 6px; padding: 12px; margin-bottom: 12px;">
                <div style="font-size: 11px; color: #808080; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px;">Output</div>
                <pre class="output-content" style="margin: 0; font-family: 'Courier New', monospace; font-size: 12px; color: #c8c8c8; white-space: pre-wrap;"></pre>
              </div>
              
              <!-- Feedback Panel -->
              <div id="${feedbackId}" style="display: none; margin-top: 12px;"></div>
              
              <!-- Hints/Solution -->
              <div style="margin-top: 12px; display: flex; gap: 8px;">
                ${
                  exercise.solution
                    ? `
                  <details style="flex: 1;">
                    <summary style="font-size: 12px; color: #808080; cursor: pointer; padding: 8px; background: #2a2a2a; border-radius: 4px;">
                      <i data-lucide="lightbulb" style="width: 12px; height: 12px; margin-right: 4px;"></i>
                      Show Solution
                    </summary>
                    <pre style="background: #1a1a1a; padding: 12px; border-radius: 6px; margin-top: 8px; font-size: 12px;"><code>${escapeHtml(exercise.solution)}</code></pre>
                  </details>
                `
                    : ""
                }
              </div>
            </div>
          `;
            })
            .join("")}
        </div>
      `
          : ""
      }
      
      <!-- Resources -->
      ${
        enrichment.resources && enrichment.resources.length > 0
          ? `
        <div style="margin-bottom: 32px;">
          <h3 style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">
            <i data-lucide="link" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            Additional Resources
          </h3>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            ${enrichment.resources
              .map(
                (resource) => `
              <div style="background: #252525; padding: 12px; border-radius: 6px;">
                <div style="font-size: 13px; font-weight: 600; color: #e0e0e0;">
                  ${resource.url ? `<a href="${resource.url}" target="_blank" style="color: #61afef; text-decoration: none;">${resource.title}</a>` : resource.title}
                </div>
                ${resource.description ? `<div style="font-size: 12px; color: #808080; margin-top: 4px;">${resource.description}</div>` : ""}
              </div>
            `,
              )
              .join("")}
          </div>
        </div>
      `
          : ""
      }
      
      <!-- Assessment Criteria -->
      ${
        enrichment.assessment_criteria &&
        enrichment.assessment_criteria.length > 0
          ? `
        <div style="margin-bottom: 32px;">
          <h3 style="font-size: 16px; font-weight: 600; color: #e0e0e0; margin-bottom: 12px;">
            <i data-lucide="check-circle" style="width: 16px; height: 16px; margin-right: 8px;"></i>
            Mastery Checklist
          </h3>
          <div style="background: #252525; padding: 16px; border-radius: 8px;">
            <div style="font-size: 12px; color: #808080; margin-bottom: 12px;">
              You've mastered this section when:
            </div>
            ${enrichment.assessment_criteria
              .map(
                (criterion) => `
              <div style="display: flex; align-items: start; gap: 8px; margin-bottom: 8px;">
                <i data-lucide="circle" style="width: 14px; height: 14px; color: #4a6a4a; flex-shrink: 0; margin-top: 2px;"></i>
                <div style="font-size: 13px; color: #c8c8c8;">${criterion}</div>
              </div>
            `,
              )
              .join("")}
          </div>
        </div>
      `
          : ""
      }
      
      <!-- Complete Button -->
      <div style="display: flex; justify-content: center; padding: 20px 0;">
        <button 
          class="btn btn-primary" 
          onclick="showCompleteSectionDialog('${curriculumId}', '${sectionId}', '${sectionTitle}')"
          style="padding: 12px 32px; font-size: 14px; font-weight: 600;"
        >
          <i data-lucide="check" style="width: 16px; height: 16px; margin-right: 8px;"></i>
          Mark Section Complete
        </button>
      </div>
      
    </div>
  `;

  sessionContent.innerHTML = html;

  // Re-initialize icons and mermaid
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
  if (typeof mermaid !== "undefined") {
    mermaid.init(undefined, document.querySelectorAll(".mermaid"));
  }

  // Attach exercise interaction handlers
  attachExerciseHandlers();
}

/**
 * Attach event handlers for exercise interactions
 */
function attachExerciseHandlers() {
  // Run Code buttons
  document.querySelectorAll(".btn-run-code").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const editorId = btn.dataset.editorId;
      const outputId = btn.dataset.outputId;
      await runExerciseCode(editorId, outputId);
    });
  });

  // Check Solution buttons
  document.querySelectorAll(".btn-check-solution").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const curriculumId = btn.dataset.curriculumId;
      const sectionId = btn.dataset.sectionId;
      const exerciseId = btn.dataset.exerciseId;
      const editorId = btn.dataset.editorId;
      const outputId = btn.dataset.outputId;
      const feedbackId = btn.dataset.feedbackId;
      await checkExerciseSolution(
        curriculumId,
        sectionId,
        exerciseId,
        editorId,
        outputId,
        feedbackId,
      );
    });
  });

  // Reset Code buttons
  document.querySelectorAll(".btn-reset-code").forEach((btn) => {
    btn.addEventListener("click", () => {
      const editorId = btn.dataset.editorId;
      const starterCode = btn.dataset.starterCode;
      resetExerciseCode(editorId, starterCode);
    });
  });
}

/**
 * Run exercise code and display output
 * Phase 23.5: Security Hardening - Now uses Pyodide sandbox in renderer
 */
async function runExerciseCode(editorId, outputId) {
  const editor = document.getElementById(editorId);
  const outputDiv = document.getElementById(outputId);
  const outputContent = outputDiv.querySelector(".output-content");

  if (!editor || !outputDiv || !outputContent) {
    console.error("[Exercise] Editor or output elements not found");
    return;
  }

  const code = editor.value;

  // Show output panel with loading state
  outputDiv.style.display = "block";
  outputContent.textContent = "Running code in sandbox...";
  outputContent.style.color = "#808080";

  try {
    // Phase 23.5: Execute directly in Pyodide sandbox (more secure)
    // Code never leaves the renderer process
    const result = await runPythonInSandbox(code, 5); // 5 second timeout

    if (result.status === "success") {
      outputContent.textContent = result.output || "(no output)";
      outputContent.style.color = "#8fd98f";
    } else if (result.status === "error") {
      outputContent.textContent = `Error:\n${result.error || result.output}`;
      outputContent.style.color = "#e06c75";
    } else if (result.status === "timeout") {
      outputContent.textContent = result.error || "Code execution timed out";
      outputContent.style.color = "#f0903b";
    }

    // Log execution to server for audit (non-blocking)
    try {
      await fetch(`${API_URL}/polly/exercises/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: code.substring(0, 100), // Only send first 100 chars for audit
          timeout: 5,
          executed_locally: true,
          result_status: result.status,
        }),
      }).catch(() => {}); // Ignore errors - audit logging is non-critical
    } catch (e) {
      // Silent fail for audit logging
    }
  } catch (error) {
    console.error("[Exercise] Error running code:", error);
    outputContent.textContent = `Failed to run code: ${error.message}`;
    outputContent.style.color = "#e06c75";
  }
}

/**
 * Check exercise solution and get feedback
 */
async function checkExerciseSolution(
  curriculumId,
  sectionId,
  exerciseId,
  editorId,
  outputId,
  feedbackId,
) {
  const editor = document.getElementById(editorId);
  const outputDiv = document.getElementById(outputId);
  const outputContent = outputDiv.querySelector(".output-content");
  const feedbackDiv = document.getElementById(feedbackId);

  if (!editor || !feedbackDiv) {
    console.error("[Exercise] Editor or feedback elements not found");
    return;
  }

  const code = editor.value;

  // First run the code to get output
  await runExerciseCode(editorId, outputId);

  // Wait a moment for execution to complete
  await new Promise((resolve) => setTimeout(resolve, 500));

  const output = outputContent ? outputContent.textContent : "";

  // Show loading feedback
  feedbackDiv.style.display = "block";
  feedbackDiv.innerHTML = `
    <div style="background: #2a2a2a; padding: 12px; border-radius: 6px; border-left: 3px solid #4a5a6a;">
      <div style="font-size: 12px; color: #8fb9df;">
        <i data-lucide="loader" class="animate-spin" style="width: 12px; height: 12px; margin-right: 6px;"></i>
        Checking your solution...
      </div>
    </div>
  `;
  if (typeof lucide !== "undefined") lucide.createIcons();

  try {
    const response = await fetch(`${API_URL}/polly/exercises/validate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        curriculum_id: curriculumId,
        section_id: sectionId,
        exercise_id: exerciseId,
        code,
        output,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const result = await response.json();
    const validation = result.validation;

    // Display feedback
    const borderColor = validation.correct ? "#4a6a4a" : "#6a4a4a";
    const iconColor = validation.correct ? "#8fd98f" : "#f0903b";
    const icon = validation.correct ? "check-circle" : "info";

    feedbackDiv.innerHTML = `
      <div style="background: #2a2a2a; padding: 16px; border-radius: 6px; border-left: 3px solid ${borderColor};">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <i data-lucide="${icon}" style="width: 16px; height: 16px; color: ${iconColor};"></i>
          <div style="font-size: 14px; font-weight: 600; color: #e0e0e0;">
            ${validation.correct ? "Great work!" : "Keep trying!"}
          </div>
        </div>
        <div style="font-size: 13px; color: #c8c8c8; white-space: pre-wrap;">${validation.feedback}</div>
      </div>
    `;

    if (typeof lucide !== "undefined") lucide.createIcons();

    if (validation.correct) {
      showToast("Exercise completed successfully!", "success");
    }
  } catch (error) {
    console.error("[Exercise] Error checking solution:", error);
    feedbackDiv.innerHTML = `
      <div style="background: #2a2a2a; padding: 12px; border-radius: 6px; border-left: 3px solid #6a4a4a;">
        <div style="font-size: 12px; color: #e06c75;">
          Failed to check solution: ${error.message}
        </div>
      </div>
    `;
  }
}

/**
 * Reset exercise code to starter code
 */
function resetExerciseCode(editorId, starterCode) {
  const editor = document.getElementById(editorId);
  if (editor) {
    // Decode HTML entities
    const textarea = document.createElement("textarea");
    textarea.innerHTML = starterCode;
    editor.value = textarea.value;
    showToast("Code reset to starter template", "info");
  }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Show complete section dialog
 */
function showCompleteSectionDialog(curriculumId, sectionId, sectionTitle) {
  console.log("[Complete Section] Opening dialog for:", sectionTitle);

  currentSectionForCompletion = {
    curriculumId,
    sectionId,
    title: sectionTitle,
  };

  // Reset form
  document.getElementById("complete-section-struggles").value = "";
  document.getElementById("complete-section-breakthroughs").value = "";

  // Reset mastery selector
  document
    .querySelectorAll(".mastery-level")
    .forEach((el) => el.classList.remove("selected"));

  // Show dialog
  document.getElementById("complete-section-dialog").classList.remove("hidden");
  lucide.createIcons();
}

/**
 * Handle mastery level selection
 */
function selectMasteryLevel(level) {
  document.querySelectorAll(".mastery-level").forEach((el) => {
    el.classList.remove("selected");
  });
  document
    .querySelector(`.mastery-level[data-level="${level}"]`)
    .classList.add("selected");
}

/**
 * Handle complete section confirmation
 */
async function handleConfirmCompleteSection() {
  if (!currentSectionForCompletion) {
    console.error("[Complete Section] No section data");
    return;
  }

  // Get selected mastery level
  const selectedMastery = document.querySelector(".mastery-level.selected");
  if (!selectedMastery) {
    showToast("Please select a mastery level", "error");
    return;
  }

  const masteryLevel = parseInt(selectedMastery.dataset.level);
  const struggles = document
    .getElementById("complete-section-struggles")
    .value.trim();
  const breakthroughs = document
    .getElementById("complete-section-breakthroughs")
    .value.trim();

  try {
    // Complete section
    await completeSection(
      currentSectionForCompletion.curriculumId,
      currentSectionForCompletion.sectionId,
      {
        mastery_level: masteryLevel,
        struggles: struggles ? [struggles] : [],
        breakthroughs: breakthroughs ? [breakthroughs] : [],
      },
    );

    // Close dialog
    document.getElementById("complete-section-dialog").classList.add("hidden");

    // Reload curriculum detail view
    await loadCurriculumDetail(currentSectionForCompletion.curriculumId);

    // Refresh sidebar curriculum list to update progress
    await loadLearningSidebarCurricula();

    currentSectionForCompletion = null;
  } catch (error) {
    console.error("[Complete Section] Failed:", error);
  }
}

// ============================================================================
// END CURRICULUM UI RENDERING
// ============================================================================

// ============================================================================
// CURRICULUM REVIEW DIALOG (Phase 23 - Phase 3)
// ============================================================================

/**
 * Global state for curriculum review dialog
 */
let currentCurriculumData = null;

/**
 * Handle review_curriculum PersonaAction
 * Shows the curriculum review dialog with editable sections
 * @param {Object} action - PersonaAction with curriculum_data
 */
function handleReviewCurriculumAction(action) {
  console.log("[Curriculum Review] Opening review dialog", action);

  if (!action.data || !action.data.curriculum_data) {
    console.error("[Curriculum Review] No curriculum data in action");
    showToast("Failed to load curriculum data", "error");
    return;
  }

  // Store curriculum data globally
  currentCurriculumData = action.data.curriculum_data;

  // Populate dialog
  populateCurriculumReviewDialog(currentCurriculumData);

  // Show dialog
  const dialog = document.getElementById("curriculum-review-dialog");
  if (dialog) {
    dialog.classList.remove("hidden");

    // Initialize Lucide icons in dialog
    if (window.lucide) {
      setTimeout(() => lucide.createIcons(), 50);
    }
  }
}

/**
 * Load all curriculum templates from backend
 */
async function loadCurriculumTemplates() {
  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/curricula/templates/list",
    );
    if (!response.ok) {
      throw new Error(`Failed to load templates: ${response.statusText}`);
    }
    const data = await response.json();
    return data.templates || [];
  } catch (error) {
    console.error("[Templates] Failed to load:", error);
    return [];
  }
}

/**
 * Update the template auto-detected indicator
 */
function updateTemplateAutoDetectedIndicator(selectedTemplateId) {
  const icon = document.getElementById("template-indicator-icon");
  const text = document.getElementById("template-indicator-text");

  if (!icon || !text || !currentCurriculumData) return;

  if (selectedTemplateId === currentCurriculumData.template_id_original) {
    icon.setAttribute("data-lucide", "sparkles");
    text.textContent = "Auto-detected";
  } else {
    icon.setAttribute("data-lucide", "pencil");
    text.textContent = "Modified";
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

/**
 * Handle template selection change
 */
function handleTemplateChange(event) {
  const newTemplateId = event.target.value;

  console.log("[Curriculum] Template changed to:", newTemplateId);

  if (currentCurriculumData) {
    currentCurriculumData.template_id = newTemplateId;
  }

  updateTemplateAutoDetectedIndicator(newTemplateId);
}

/**
 * Populate the curriculum review dialog with data
 * @param {Object} curriculumData - Curriculum data with title, goal, sections
 */
function populateCurriculumReviewDialog(curriculumData) {
  console.log("[Curriculum Review] Populating dialog", curriculumData);

  // Set title
  const titleInput = document.getElementById("curriculum-title-input");
  if (titleInput) {
    titleInput.value = curriculumData.title || "";
  }

  // Set goal
  const goalInput = document.getElementById("curriculum-goal-input");
  if (goalInput) {
    goalInput.value = curriculumData.goal || "";
  }

  // Populate template selector
  const templateSelect = document.getElementById("curriculum-template-select");
  if (templateSelect) {
    // Store original auto-detected template
    if (!curriculumData.template_id_original) {
      curriculumData.template_id_original = curriculumData.template_id;
    }

    // Load all templates
    loadCurriculumTemplates().then((templates) => {
      if (!templates || templates.length === 0) {
        console.warn("[Curriculum] No templates loaded");
        return;
      }

      // Clear and populate dropdown
      templateSelect.innerHTML = "";
      templates.forEach((template) => {
        const option = document.createElement("option");
        option.value = template.id;
        option.textContent = template.name;
        option.title = template.description; // Show description on hover

        if (template.id === curriculumData.template_id) {
          option.selected = true;
        }

        templateSelect.appendChild(option);
      });

      // Add change listener
      templateSelect.removeEventListener("change", handleTemplateChange);
      templateSelect.addEventListener("change", handleTemplateChange);

      // Initialize indicator
      updateTemplateAutoDetectedIndicator(curriculumData.template_id);
    });
  }

  // Render sections
  renderCurriculumSectionsDialog(curriculumData.sections || []);
}

/**
 * Format template ID into display name
 * @param {string} templateId - Template ID (e.g., "programming-language")
 * @returns {string} Formatted name (e.g., "Programming Language")
 */
function formatTemplateName(templateId) {
  return templateId
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

/**
 * Render curriculum sections in the dialog
 * @param {Array} sections - Array of section objects
 */
function renderCurriculumSectionsDialog(sections) {
  const container = document.getElementById("curriculum-sections-container");
  if (!container) return;

  // Clear container
  container.innerHTML = "";

  if (!sections || sections.length === 0) {
    container.innerHTML = `
      <div class="curriculum-empty">
        <i data-lucide="book-open"></i>
        <p>No sections defined yet</p>
      </div>
    `;
    return;
  }

  // Group sections by weeks
  const weeks = sections.filter((s) => s.type === "week");
  const subsections = sections.filter((s) => s.type === "subheading");

  weeks.forEach((week) => {
    const weekSections = subsections.filter((s) => s.parent_id === week.id);
    const weekElement = createWeekElement(week, weekSections);
    container.appendChild(weekElement);
  });
}

/**
 * Create a week section element
 * @param {Object} week - Week section data
 * @param {Array} subsections - Subsections for this week
 * @returns {HTMLElement} Week element
 */
function createWeekElement(week, subsections) {
  const weekDiv = document.createElement("div");
  weekDiv.className = "curriculum-week";
  weekDiv.dataset.weekId = week.id;

  weekDiv.innerHTML = `
    <div class="curriculum-week-header">
      <div class="curriculum-week-title">
        <i data-lucide="calendar"></i>
        <span>${week.title}</span>
      </div>
      <div class="curriculum-week-toggle">
        <span>${subsections.length} section${subsections.length !== 1 ? "s" : ""}</span>
        <i data-lucide="chevron-down"></i>
      </div>
    </div>
    <div class="curriculum-week-subsections"></div>
  `;

  // Add click handler for collapse/expand
  const header = weekDiv.querySelector(".curriculum-week-header");
  header.addEventListener("click", () => {
    weekDiv.classList.toggle("collapsed");
    if (window.lucide) lucide.createIcons();
  });

  // Add subsections
  const subsectionsContainer = weekDiv.querySelector(
    ".curriculum-week-subsections",
  );
  subsections.forEach((subsection) => {
    const subElement = createSubsectionElement(subsection);
    subsectionsContainer.appendChild(subElement);
  });

  return weekDiv;
}

/**
 * Create a subsection element
 * @param {Object} subsection - Subsection data
 * @returns {HTMLElement} Subsection element
 */
function createSubsectionElement(subsection) {
  const subDiv = document.createElement("div");
  subDiv.className = "curriculum-subheading";
  subDiv.dataset.sectionId = subsection.id;

  const conceptsHtml =
    subsection.concepts && subsection.concepts.length > 0
      ? `<div class="curriculum-concepts">
         ${subsection.concepts.map((c) => `<span class="curriculum-concept-tag">${c}</span>`).join("")}
       </div>`
      : "";

  subDiv.innerHTML = `
    <div class="curriculum-subheading-header">
      <div class="curriculum-subheading-content">
        <div class="curriculum-subheading-title">${subsection.title}</div>
        <div class="curriculum-subheading-description">${subsection.description || ""}</div>
        ${conceptsHtml}
        <div class="curriculum-subheading-meta">
          ${
            subsection.estimated_time
              ? `
            <div class="curriculum-meta-item">
              <i data-lucide="clock"></i>
              <span>${subsection.estimated_time}</span>
            </div>
          `
              : ""
          }
        </div>
      </div>
      <button class="curriculum-edit-btn" data-section-id="${subsection.id}">
        <i data-lucide="edit-2"></i>
      </button>
    </div>
  `;

  // Add edit button handler
  const editBtn = subDiv.querySelector(".curriculum-edit-btn");
  editBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleSectionEdit(subsection.id);
  });

  return subDiv;
}

/**
 * Toggle edit mode for a section
 * @param {string} sectionId - Section ID
 */
function toggleSectionEdit(sectionId) {
  const subDiv = document.querySelector(`[data-section-id="${sectionId}"]`);
  if (!subDiv) return;

  const isEditing = subDiv.classList.contains("editing");

  if (isEditing) {
    // Cancel edit - remove form
    const form = subDiv.querySelector(".curriculum-edit-form");
    if (form) form.remove();
    subDiv.classList.remove("editing");
  } else {
    // Enter edit mode - show form
    const section = findSectionById(sectionId);
    if (!section) return;

    const formHtml = `
      <div class="curriculum-edit-form">
        <div class="curriculum-form-group">
          <label class="curriculum-form-label">Title</label>
          <input type="text" class="curriculum-form-input" data-field="title" value="${section.title || ""}" />
        </div>
        <div class="curriculum-form-group">
          <label class="curriculum-form-label">Description</label>
          <textarea class="curriculum-form-textarea" data-field="description" rows="3">${section.description || ""}</textarea>
        </div>
        <div class="curriculum-form-group">
          <label class="curriculum-form-label">Concepts (comma-separated)</label>
          <input type="text" class="curriculum-form-input" data-field="concepts" value="${(section.concepts || []).join(", ")}" />
        </div>
        <div class="curriculum-form-group">
          <label class="curriculum-form-label">Estimated Time</label>
          <input type="text" class="curriculum-form-input" data-field="estimated_time" value="${section.estimated_time || ""}" placeholder="e.g., 3 hours" />
        </div>
        <div class="curriculum-form-actions">
          <button class="btn-cancel">Cancel</button>
          <button class="btn-save">Save</button>
        </div>
      </div>
    `;

    subDiv.insertAdjacentHTML("beforeend", formHtml);
    subDiv.classList.add("editing");

    // Add form handlers
    const form = subDiv.querySelector(".curriculum-edit-form");
    const cancelBtn = form.querySelector(".btn-cancel");
    const saveBtn = form.querySelector(".btn-save");

    cancelBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleSectionEdit(sectionId);
    });

    saveBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      saveSectionEdits(sectionId, form);
    });
  }

  // Reinitialize icons
  if (window.lucide) {
    setTimeout(() => lucide.createIcons(), 50);
  }
}

/**
 * Save section edits
 * @param {string} sectionId - Section ID
 * @param {HTMLElement} form - Form element
 */
function saveSectionEdits(sectionId, form) {
  if (!currentCurriculumData || !currentCurriculumData.sections) return;

  const section = findSectionById(sectionId);
  if (!section) return;

  // Collect form data
  const title = form.querySelector('[data-field="title"]').value.trim();
  const description = form
    .querySelector('[data-field="description"]')
    .value.trim();
  const conceptsStr = form
    .querySelector('[data-field="concepts"]')
    .value.trim();
  const estimatedTime = form
    .querySelector('[data-field="estimated_time"]')
    .value.trim();

  // Update section
  section.title = title;
  section.description = description;
  section.concepts = conceptsStr
    ? conceptsStr.split(",").map((c) => c.trim())
    : [];
  section.estimated_time = estimatedTime;

  // Re-render sections
  renderCurriculumSectionsDialog(currentCurriculumData.sections);

  showToast("Section updated", "success");
}

/**
 * Find section by ID in current curriculum data
 * @param {string} sectionId - Section ID
 * @returns {Object|null} Section object or null
 */
function findSectionById(sectionId) {
  if (!currentCurriculumData || !currentCurriculumData.sections) return null;
  return currentCurriculumData.sections.find((s) => s.id === sectionId);
}

/**
 * Save curriculum from review dialog
 */
async function saveCurriculumFromReview() {
  if (!currentCurriculumData) {
    showToast("No curriculum data to save", "error");
    return;
  }

  try {
    // Get current title and goal from inputs
    const titleInput = document.getElementById("curriculum-title-input");
    const goalInput = document.getElementById("curriculum-goal-input");

    const title = titleInput?.value.trim() || currentCurriculumData.title;
    const goal = goalInput?.value.trim() || currentCurriculumData.goal;

    if (!title || !goal) {
      showToast("Title and goal are required", "error");
      return;
    }

    // Create curriculum via API
    const metadata = {};
    if (currentCurriculumData.template_id) {
      metadata.template_id = currentCurriculumData.template_id;
    }

    const curriculum = await createCurriculum(
      title,
      goal,
      currentCurriculumData.sections,
      metadata,
    );

    console.log("[Curriculum Review] Curriculum created:", curriculum);

    // Close dialog
    const dialog = document.getElementById("curriculum-review-dialog");
    if (dialog) dialog.classList.add("hidden");

    // Clear state
    currentCurriculumData = null;

    // Show success message with option to activate
    showToast(`Curriculum "${title}" saved successfully!`, "success");

    // Refresh the curricula list in the sidebar
    await loadLearningSidebarCurricula();

    // TODO: Ask if user wants to activate curriculum
  } catch (error) {
    console.error("[Curriculum Review] Failed to save curriculum:", error);
    showToast("Failed to save curriculum", "error");
  }
}

/**
 * Regenerate curriculum (sends message back to Professor)
 */
async function regenerateCurriculum() {
  if (!currentCurriculumData) return;

  // Get current selections BEFORE clearing state
  const goal =
    document.getElementById("curriculum-goal-input")?.value ||
    currentCurriculumData.goal ||
    "the curriculum";
  const selectedTemplateId =
    document.getElementById("curriculum-template-select")?.value ||
    currentCurriculumData.template_id;

  // Close dialog
  const dialog = document.getElementById("curriculum-review-dialog");
  if (dialog) dialog.classList.add("hidden");

  // Build message based on whether template was changed
  let message;
  if (selectedTemplateId !== currentCurriculumData.template_id_original) {
    const templateName =
      document.getElementById("curriculum-template-select")?.options[
        document.getElementById("curriculum-template-select")?.selectedIndex
      ]?.textContent || "";
    message = `Regenerate the curriculum for "${goal}" using the ${templateName} template.`;
  } else {
    message = `Can you regenerate the curriculum for "${goal}"? I'd like a different approach.`;
  }

  console.log("[Curriculum] Regenerating with message:", message);

  // Clear state AFTER building message
  currentCurriculumData = null;

  // Send via chat
  const input = document.getElementById("query-input");
  if (input) {
    input.value = message;
    await sendQuery();
  }
}

// ============================================================================
// END CURRICULUM REVIEW DIALOG
// ============================================================================

/**
 * Send query
 */
let _sendQueryInProgress = false;

async function sendQuery() {
  if (_sendQueryInProgress) return;
  _sendQueryInProgress = true;

  try {
    const chatInput = document.getElementById("chat-input");
    const queryInput = document.getElementById("query-input");
    const input = chatInput || queryInput;
    const query = input?.value.trim();
    if (!query) return;

    await sendQueryCore(query);
  } finally {
    _sendQueryInProgress = false;
  }
}

async function sendQueryCore(query) {
  console.log("[Send Query] Sending message:", query);

  // Slash command: parse and route directly to persona+mode
  const parsed = parseSlashCommand(query);
  if (parsed) {
    console.log("[SlashCommand] Resolved:", query.slice(0, 30), "->", parsed.persona, ":", parsed.mode, "| message:", parsed.userMessage.slice(0, 60));
    await fetchSlashCommands(); // populate cache for next time
    await sendQueryInternal(query, parsed.userMessage, {
      personaOverride: parsed.persona,
      modeOverride: parsed.mode,
    });
    return;
  }

  // Check for persona intent and handle switch if needed
  await checkAndHandlePersonaSwitch(query, async () => {
    await sendQueryInternal(query, query, null);
  });
}


/**
 * Internal function to send query after persona check
 * @param {string} displayQuery - Message to show in UI (user's full input)
 * @param {string} apiQuery - Message to send to backend (may differ for slash commands)
 * @param {{ personaOverride?: string, modeOverride?: string }|null} overrides - From slash command
 */
async function sendQueryInternal(displayQuery, apiQuery, overrides) {
  // Ensure we have a conversation
  if (!currentConversationId) {
    console.log("No conversation, creating new one...");
    await createNewConversation();
  }

  // Clear input (main chat panel + legacy)
  const chatInput = document.getElementById("chat-input");
  const queryInput = document.getElementById("query-input");
  for (const input of [chatInput, queryInput]) {
    if (input) {
      input.value = "";
      input.style.height = "auto";
    }
  }

  // Add user message to UI
  addMessageToUI("user", displayQuery);

  // Add to conversation in database
  await addMessageToConversation("user", displayQuery);

  // Add typing indicator
  const loadingId = addTypingIndicator();

  try {
    // Persona: from slash command overrides or dropdown
    const chatPersonaSelect = document.getElementById("chat-persona-select");
    const personaSelect = document.getElementById("persona-select");
    const activePersona = overrides?.personaOverride ?? (chatPersonaSelect || personaSelect)?.value ?? null;
    const activeMode = overrides?.modeOverride ?? null;

    // Get conversation history (excluding the message we just added - it will be included in the query)
    const messages = getCurrentConversationMessages();
    // Convert to format expected by backend: [{role: 'user', content: '...'}, {role: 'assistant', content: '...'}]
    // Exclude the last message (the one we just added)
    const conversationHistory = messages.slice(0, -1).map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    console.log(
      "Sending query with conversation history:",
      conversationHistory.length,
      "messages",
    );

    // Route through persona if active (or from slash command)
    if (activePersona) {
      const result = await sendToPersona(apiQuery, conversationHistory, loadingId, activePersona, activeMode);
      if (result) {
        // Sync persona selector when invoked via slash command
        if (overrides?.personaOverride) {
          const sel = document.getElementById("chat-persona-select") || document.getElementById("persona-select");
          if (sel && sel.value !== activePersona) {
            sel.value = activePersona;
            sel.dispatchEvent(new Event("change"));
          }
        }
        return; // Persona handled the request
      }
      // If persona failed and this was a slash command, show error instead of falling through
      if (overrides?.personaOverride) {
        removeMessage(loadingId);
        addMessageToUI(
          "system",
          "The persona request failed. Make sure the Polly server is running and the persona system is enabled (Router v2).",
        );
        return;
      }
      // Non-slash persona request failed — fall through to normal query
    }

    // Get router v2 settings from model selector (stored in sessionStorage)
    const confidence = sessionStorage.getItem("model-confidence") || "balanced";
    const providerOverride = sessionStorage.getItem("model-provider") || null;

    // Get mental models override for this conversation
    const mentalModelsOverride = getMentalModelsOverride(currentConversationId);
    const queryOptions = {
      mode: currentMode,
      conversation_history: conversationHistory,
      page: getEffectivePage(), // Resolved page for mental models & RAG filtering
      confidence: confidence, // Router v2: fast/balanced/thorough
      provider_override: providerOverride, // Router v2: force specific provider
    };

    // Add mental models override if present (per-conversation or global defaults)
    if (mentalModelsOverride && !mentalModelsOverride.useDefaults) {
      queryOptions.mental_models_override = mentalModelsOverride.modelIds;
    } else {
      // Check for global default models
      const globalDefaults = getGlobalDefaultModels();
      if (globalDefaults && globalDefaults.enabled && globalDefaults.modelIds.length > 0) {
        queryOptions.mental_models_override = globalDefaults.modelIds;
      }
    }

    const result = await window.polly.query(apiQuery, queryOptions);

    // Remove loading and add response
    removeMessage(loadingId);

    if (result.success) {
      const response = formatResponse(result.result.response);

      // Check if we have router v2 metadata
      let metadata = result.result.metadata;
      let messageContent = response;

      if (metadata) {
        // Add metadata footer to response
        const costStr = metadata.cost ? `$${metadata.cost.toFixed(4)}` : "-";
        const tokensStr =
          metadata.tokens_in && metadata.tokens_out
            ? `${metadata.tokens_in + metadata.tokens_out} tokens`
            : "-";
        const providerStr = metadata.provider || "-";
        const modelStr = metadata.model || "-";
        const estimatedStr = metadata.estimated ? " (estimated)" : "";
        
        // Add routing reason if available (shows why Polly chose this provider)
        let routingReasonHtml = "";
        if (metadata.routing_reason) {
          routingReasonHtml = `<br><span style="color: #606060; font-style: italic;">→ ${metadata.routing_reason}</span>`;
        }

        messageContent += `
          <div style="margin-top: 12px; padding-top: 8px; border-top: 1px solid #2a2a2a; font-size: 11px; color: #808080; font-family: monospace;">
            ✓ ${providerStr} (${modelStr}) • ${costStr} • ${tokensStr}${estimatedStr}${routingReasonHtml}
          </div>
        `;

        console.log("Router v2 metadata:", metadata);
      }

      addMessageToUI("assistant", messageContent);

      // Add to conversation in database
      await addMessageToConversation("assistant", result.result.response);

      // Auto-categorize conversation after response
      // Use setTimeout to not block the UI
      setTimeout(() => {
        autoCategorizeConversation(currentConversationId);
      }, 100);

      // Related notes feature temporarily disabled in new UI
      // Will be reimplemented in a future update
    } else {
      addMessageToUI("system", `Error: ${result.error}`);
    }
  } catch (error) {
    removeMessage(loadingId);
    addMessageToUI("system", `Error: ${error.message}`);
  }
}

/**
 * Get the visible chat messages container (main chat panel takes precedence)
 */
function getChatMessagesContainer() {
  return (
    document.getElementById("chat-messages-main") ||
    document.getElementById("chat-messages")
  );
}

/**
 * Add message to UI
 */
function addMessageToUI(role, content) {
  const container = getChatMessagesContainer();
  const id = `msg-${Date.now()}`;
  const timestamp = new Date();

  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.id = id;
  div.dataset.timestamp = timestamp.toISOString();

  div.innerHTML = `
    <div class="message-content">${content}</div>
    <div class="message-timestamp" title="${timestamp.toLocaleString()}">${getRelativeTime(timestamp)}</div>
  `;

  container.appendChild(div);

  // Smooth scroll to bottom
  requestAnimationFrame(() => {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  });

  // Re-initialize icons if any were added
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }

  return id;
}

/**
 * Add typing indicator (better than generic loading spinner)
 */
function addTypingIndicator() {
  const container = getChatMessagesContainer();
  const id = `typing-${Date.now()}`;

  const div = document.createElement("div");
  div.className = "message assistant";
  div.id = id;
  div.innerHTML = `
    <div class="typing-indicator">
      <div class="typing-dots">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>
  `;

  container.appendChild(div);

  // Smooth scroll to bottom
  requestAnimationFrame(() => {
    container.scrollTo({
      top: container.scrollHeight,
      behavior: "smooth",
    });
  });

  return id;
}

// Alias for backward compatibility
function addMessage(role, content) {
  return addMessageToUI(role, content);
}

/**
 * Remove message
 */
function removeMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

/**
 * Get relative time string (e.g., "2 minutes ago")
 */
function getRelativeTime(date) {
  const now = new Date();
  const diffMs = now - date;
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSecs < 10) return "just now";
  if (diffSecs < 60) return `${diffSecs}s ago`;
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;

  // For older messages, show date
  return date.toLocaleDateString();
}

/**
 * Format response with markdown using marked.js
 */
function formatResponse(text) {
  // Check if marked library is available
  if (typeof marked !== "undefined") {
    try {
      // Configure marked for better rendering
      marked.setOptions({
        breaks: true, // Convert \n to <br>
        gfm: true, // GitHub Flavored Markdown
        headerIds: false, // Don't add IDs to headers
        mangle: false, // Don't escape autolinked email addresses
      });

      // Custom renderer for code blocks with copy button
      const renderer = new marked.Renderer();
      const originalCodeRenderer = renderer.code.bind(renderer);

      renderer.code = function (code, language) {
        // Ensure code is a string (marked.js sometimes passes objects)
        const codeStr =
          typeof code === "string" ? code : code?.text || String(code || "");

        const escapedCode = codeStr
          .replace(/&/g, "&amp;")
          .replace(/</g, "&lt;")
          .replace(/>/g, "&gt;")
          .replace(/"/g, "&quot;")
          .replace(/'/g, "&#39;");

        const langLabel = language ? language : "text";
        const codeId = `code-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

        return `
          <div class="code-block-wrapper">
            <div class="code-block-header">
              <span class="code-block-language">${langLabel}</span>
              <button class="code-copy-btn" onclick="copyCodeToClipboard('${codeId}')" title="Copy code">
                <i data-lucide="copy" style="width: 14px; height: 14px;"></i>
              </button>
            </div>
            <pre><code id="${codeId}" class="language-${langLabel}">${escapedCode}</code></pre>
          </div>
        `;
      };

      marked.use({ renderer });

      return marked.parse(text);
    } catch (error) {
      console.error("[Format] Error using marked.js:", error);
      // Fall back to basic formatting
      return basicMarkdownFormat(text);
    }
  } else {
    // Fall back to basic formatting if marked not available
    return basicMarkdownFormat(text);
  }
}

/**
 * Copy code to clipboard
 */
function copyCodeToClipboard(codeId) {
  const codeElement = document.getElementById(codeId);
  if (!codeElement) return;

  const code = codeElement.textContent;
  navigator.clipboard
    .writeText(code)
    .then(() => {
      // Visual feedback
      const btn = event.target.closest(".code-copy-btn");
      if (btn) {
        const originalHTML = btn.innerHTML;
        btn.innerHTML =
          '<i data-lucide="check" style="width: 14px; height: 14px;"></i>';
        btn.style.color = "#4ade80";

        // Re-initialize icons
        if (typeof lucide !== "undefined") {
          lucide.createIcons();
        }

        setTimeout(() => {
          btn.innerHTML = originalHTML;
          btn.style.color = "";
          if (typeof lucide !== "undefined") {
            lucide.createIcons();
          }
        }, 2000);
      }
    })
    .catch((err) => {
      console.error("[Copy] Failed to copy code:", err);
    });
}

/**
 * Basic markdown formatting (fallback)
 */
function basicMarkdownFormat(text) {
  return text
    .replace(
      /```(\w*)\n?([\s\S]*?)```/g,
      '<pre><code class="language-$1">$2</code></pre>',
    )
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
    .replace(/\*([^*]+)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

/**
 * Check server status
 */
async function checkServerStatus() {
  const result = await window.polly.getServerStatus();
  updateServerStatus(result.running);
}

/**
 * Check Ollama status
 */
async function checkOllamaStatus() {
  const result = await window.polly.getOllamaStatus();
  updateOllamaStatus(result.running);
}

/**
 * Update server status UI
 */
function updateServerStatus(running) {
  isServerRunning = running;

  const dot = document.getElementById("status-dot");
  const indicator = document.getElementById("server-indicator");
  const statusText = document.getElementById("server-status-text");
  const btn = document.getElementById("btn-toggle-server");

  // Update status dot in ribbon (always exists)
  if (dot) {
    if (running) {
      dot.className = "status-dot online";
    } else {
      dot.className = "status-dot offline";
    }
  }

  // Update server indicator on dashboard (may not exist)
  if (indicator) {
    if (running) {
      indicator.classList.add("running");
    } else {
      indicator.classList.remove("running");
    }
  }

  // Update status text on dashboard (may not exist)
  if (statusText) {
    statusText.textContent = running ? "Running on port 11436" : "Stopped";
  }

  // Update toggle button on dashboard (may not exist)
  if (btn) {
    btn.textContent = running ? "Stop" : "Start";
  }
}

/**
 * Update Ollama status UI
 */
function updateOllamaStatus(running) {
  isOllamaRunning = running;

  const indicator = document.getElementById("ollama-indicator");
  const statusText = document.getElementById("ollama-status-text");

  if (running) {
    indicator?.classList.add("running");
    if (statusText) statusText.textContent = "Running on port 11434";
  } else {
    indicator?.classList.remove("running");
    if (statusText) statusText.textContent = "Not running";
  }
}

/**
 * Toggle server
 */
async function toggleServer() {
  const btn = document.getElementById("btn-toggle-server");
  btn.disabled = true;

  try {
    if (isServerRunning) {
      // Stop server
      btn.textContent = "Stopping...";
      await window.polly.stopServer();

      // Wait a bit for server to shut down
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Update status
      updateServerStatus(false);
    } else {
      // Start server
      btn.textContent = "Starting...";
      const result = await window.polly.startServer();

      if (result.success) {
        // Wait for server to be ready
        await new Promise((resolve) => setTimeout(resolve, 2000));

        // Verify server is actually running
        try {
          const response = await fetch("http://127.0.0.1:11436/health");
          updateServerStatus(response.ok);
        } catch {
          updateServerStatus(false);
        }
      } else {
        console.error("Failed to start server:", result.error);
        updateServerStatus(false);
      }
    }
  } catch (error) {
    console.error("Toggle server error:", error);
  } finally {
    btn.disabled = false;
  }
}

/**
 * Load dashboard data
 */
const loadDashboardData = withErrorBoundary(async function () {
  // Use silent mode if we're retrying (to avoid console spam)
  const silent = statsRetryCount > 0;
  const statsResult = await safeFetch(
    "http://127.0.0.1:11436/polly/stats",
    {},
    silent,
  );

  if (statsResult.ok && statsResult.data) {
    const data = statsResult.data;

    // Store in global state for sidebars (normalize to rag_stats)
    // Support both 'notes' (new native system) and 'obsidian' (legacy)
    const notesStats = data.rag?.notes ||
      data.rag?.obsidian || { count: 0, files: 0 };

    window.pollyStats = {
      rag_stats: {
        obsidian: notesStats, // Keep for backward compatibility
        notes: notesStats, // Add notes key
        codebase: data.rag?.codebase || { count: 0, files: 0 },
        documents: data.rag?.documents || { count: 0, files: 0 },
        patterns: data.rag?.patterns || { count: 0, files: 0 },
      },
      patterns: {
        total: data.patterns || 0,
        this_week: 0, // TODO: Backend should provide this
        top_category: "None", // TODO: Backend should provide this
      },
    };

    const statObsidian = document.getElementById("stat-obsidian");
    const statCodebase = document.getElementById("stat-codebase");
    const statPatterns = document.getElementById("stat-patterns");
    const statEntities = document.getElementById("stat-entities");

    if (statObsidian) statObsidian.textContent = notesStats.count || 0;
    if (statCodebase) statCodebase.textContent = data.rag?.codebase?.count || 0;
    if (statPatterns) statPatterns.textContent = data.patterns || 0;
    if (statEntities) statEntities.textContent = data.graph?.entities || 0;

    // Update right sidebar if on dashboard (NOT on chat view to avoid re-renders)
    if (currentView === "dashboard") {
      updateRightSidebar("dashboard");
    }
    // Note: We don't call updateRightSidebar for 'chat' view to prevent
    // unnecessary DOM replacement that would clear the conversation

    // Reset retry count on success
    statsRetryCount = 0;
  } else {
    statsRetryCount++;
    // Only log on first attempt
    if (statsRetryCount === 1 && statsResult.isConnectionError) {
      console.log("[Dashboard] Waiting for server to start...");
    }
    // Only retry up to MAX_STATS_RETRIES times
    if (statsRetryCount <= MAX_STATS_RETRIES) {
      setTimeout(loadDashboardData, 3000);
    } else if (statsRetryCount === MAX_STATS_RETRIES + 1) {
      // Only log once when we give up
      console.log("[Dashboard] Server not ready after retries");
    }
  }
}, "loadDashboardData");

/**
 * Load knowledge data
 */
const loadKnowledgeData = withErrorBoundary(async function () {
  console.log("[Knowledge] loadKnowledgeData() called");

  // Get notes path from server (supports both native and Obsidian)
  let notesPath = "Not configured";

  // Try to fetch notes path from server API (silent to avoid startup noise)
  const notesSourceResult = await safeFetch(
    "http://127.0.0.1:11436/polly/notes/source",
    {},
    true,
  );
  if (notesSourceResult.ok && notesSourceResult.data) {
    notesPath = notesSourceResult.data.notes_path || "Not configured";
    console.log("[Knowledge] Notes path:", notesPath);
  } else if (!notesSourceResult.isConnectionError) {
    // Only log non-connection errors
    console.log(
      "[Knowledge] Could not fetch notes path:",
      notesSourceResult.error,
    );
  }

  // Fallback to old vault path if server not available (safe IPC call)
  if (!notesSourceResult.ok) {
    const vaultPath = await PollyBridge.safeCall("getStore", "vaultPath");
    if (vaultPath) {
      notesPath = vaultPath;
      console.log("[Knowledge] Using fallback vault path:", vaultPath);
    }
  }

  const obsidianPathEl = document.getElementById("obsidian-path");
  if (obsidianPathEl) {
    obsidianPathEl.textContent = notesPath;
  }

  // Safe IPC call to get codebase paths
  const savedCodePaths =
    (await PollyBridge.safeCall("getStore", "codebasePaths")) || [];
  const container = document.getElementById("code-source-paths");

  if (container) {
    if (savedCodePaths.length) {
      container.innerHTML = savedCodePaths
        .map((p) => `<div class="source-path">${p}</div>`)
        .join("");
    } else {
      container.innerHTML =
        '<div class="path-empty">No directories configured</div>';
    }
  }

  // Load stats from server with safe fetch (silent mode for retries)
  const silent = statsRetryCount > 0;
  const statsResult = await safeFetch(
    "http://127.0.0.1:11436/polly/stats",
    {},
    silent,
  );

  console.log("[Knowledge] Stats fetch result:", {
    ok: statsResult.ok,
    hasData: !!statsResult.data,
  });

  if (statsResult.ok && statsResult.data) {
    const data = statsResult.data;

    console.log(
      "[Knowledge] Raw stats from server:",
      JSON.stringify(data.rag, null, 2),
    );

    // Store in global state for sidebars (normalize to rag_stats)
    // Support both 'notes' (new native system) and 'obsidian' (legacy)
    const notesStats = data.rag?.notes ||
      data.rag?.obsidian || { count: 0, files: 0 };

    console.log("[Knowledge] Extracted notesStats:", notesStats);

    window.pollyStats = {
      rag_stats: {
        obsidian: notesStats, // Keep obsidian key for backward compatibility
        notes: notesStats, // Add notes key for new system
        codebase: data.rag?.codebase || { count: 0, files: 0 },
        documents: data.rag?.documents || { count: 0, files: 0 },
        patterns: data.rag?.patterns || { count: 0, files: 0 },
      },
      patterns: {
        total: data.patterns || 0,
        this_week: 0,
        top_category: "None",
      },
    };

    // Update knowledge view stats (using notes data)
    const notesCount = notesStats.count;
    const notesFiles = notesStats.files;
    const codebaseCount = data.rag?.codebase?.count || 0;
    const codebaseFiles = data.rag?.codebase?.files || 0;

    console.log("[Knowledge] Updating UI with stats:", {
      notesCount,
      notesFiles,
      codebaseCount,
      codebaseFiles,
    });

    const obsidianFilesEl = document.getElementById("obsidian-files");
    const obsidianChunksEl = document.getElementById("obsidian-chunks");
    const codeFilesEl = document.getElementById("code-files");
    const codeChunksEl = document.getElementById("code-chunks");

    console.log("[Knowledge] DOM elements found:", {
      obsidianFilesEl: !!obsidianFilesEl,
      obsidianChunksEl: !!obsidianChunksEl,
      codeFilesEl: !!codeFilesEl,
      codeChunksEl: !!codeChunksEl,
    });

    if (obsidianFilesEl) obsidianFilesEl.textContent = `${notesFiles} files`;
    if (obsidianChunksEl) obsidianChunksEl.textContent = `${notesCount} chunks`;
    if (codeFilesEl) codeFilesEl.textContent = `${codebaseFiles} files`;
    if (codeChunksEl) codeChunksEl.textContent = `${codebaseCount} chunks`;

    console.log("[Knowledge] UI elements updated");
    // Also update dashboard stats
    const statObsidian = document.getElementById("stat-obsidian");
    const statCodebase = document.getElementById("stat-codebase");
    const statPatterns = document.getElementById("stat-patterns");
    const statEntities = document.getElementById("stat-entities");

    if (statObsidian) statObsidian.textContent = notesCount;
    if (statCodebase) statCodebase.textContent = codebaseCount;
    if (statPatterns) statPatterns.textContent = data.rag?.patterns?.count || 0;
    if (statEntities) statEntities.textContent = data.graph?.entities || 0;

    // Update right sidebar if on knowledge view (NOT on chat view to avoid re-renders)
    if (currentView === "knowledge") {
      updateRightSidebar("knowledge");
    }
    // Note: We don't call updateRightSidebar for 'chat' view to prevent
    // unnecessary DOM replacement that would clear the conversation
  } else {
    statsRetryCount++;
    // Only log on first attempt
    if (statsRetryCount === 1 && statsResult.isConnectionError) {
      console.log("[Knowledge] Waiting for server to start...");
    }
    // Only retry up to MAX_STATS_RETRIES times
    if (statsRetryCount <= MAX_STATS_RETRIES) {
      setTimeout(loadKnowledgeData, 3000);
    } else if (statsRetryCount === MAX_STATS_RETRIES + 1) {
      // Only log once when we give up
      console.log("[Knowledge] Server not ready after retries");
    }
  }
}, "loadKnowledgeData");

/**
 * Index knowledge base
 */
async function indexKnowledge(options = {}) {
  const logContainer = document.getElementById("index-log");
  const logContent = document.getElementById("index-log-content");

  logContainer.style.display = "block";
  logContent.textContent = "Starting indexing...\n";

  try {
    const result = await window.polly.indexKnowledge(options);

    if (result.success) {
      appendIndexLog("\n✓ Indexing complete!");
    } else {
      appendIndexLog(`\n✗ Error: ${result.error}`);
    }
  } catch (error) {
    console.error("Indexing error:", error);
    appendIndexLog(`\n✗ Error: ${error.message}`);
  }
}

/**
 * Append to index log
 */
function appendIndexLog(message) {
  const logContent = document.getElementById("index-log-content");
  if (logContent) {
    logContent.textContent += message;
    logContent.scrollTop = logContent.scrollHeight;
  }
}

/**
 * Load patterns
 */
async function loadPatterns() {
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/patterns");
    if (!response.ok) {
      console.log("Could not load patterns, API returned:", response.status);
      return;
    }

    const data = await response.json();
    const patternsList = document.getElementById("patterns-list");

    // Clear loading/empty state
    patternsList.innerHTML = "";

    if (data.total_count === 0) {
      // Show empty state
      patternsList.innerHTML = `
        <div class="pattern-empty">
          <i data-lucide="sparkles" class="pattern-empty-icon"></i>
          <p>No patterns learned yet.</p>
          <p class="pattern-empty-hint">Keep using Polly and patterns will emerge from your queries and knowledge base.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    // Display patterns by type
    const patternsByType = {
      conceptual: [],
      code: [],
      query: [],
    };

    // Group conceptual patterns
    data.patterns.forEach((p) => {
      if (p.pattern_type === "conceptual") {
        patternsByType.conceptual.push(p);
      } else if (p.pattern_type === "code") {
        patternsByType.code.push(p);
      }
    });

    // Add query patterns
    data.query_patterns.forEach((qp) => {
      patternsByType.query.push(qp);
    });

    // Render conceptual patterns
    if (patternsByType.conceptual.length > 0) {
      const section = document.createElement("div");
      section.className = "pattern-section";
      section.innerHTML = `
        <h3 class="pattern-section-title">
          <i data-lucide="brain" class="pattern-section-icon"></i>
          Conceptual Patterns
        </h3>
        <div class="pattern-section-desc">Concepts you frequently explore together</div>
      `;

      patternsByType.conceptual.forEach((pattern) => {
        const card = document.createElement("div");
        card.className = "pattern-card";

        const domainBadges = pattern.domains
          .map((d) => `<span class="pattern-domain ${d}">${d}</span>`)
          .join("");

        const confidencePercent = Math.round(pattern.confidence * 100);
        const confidenceClass =
          confidencePercent >= 70
            ? "high"
            : confidencePercent >= 40
              ? "medium"
              : "low";

        card.innerHTML = `
          <div class="pattern-header">
            <div class="pattern-name">${pattern.name}</div>
            <div class="pattern-confidence ${confidenceClass}">${confidencePercent}%</div>
          </div>
          <div class="pattern-description">${pattern.description}</div>
          <div class="pattern-meta">
            <span class="pattern-occurrences">
              <i data-lucide="repeat" class="pattern-meta-icon"></i>
              ${pattern.occurrences} times
            </span>
            <div class="pattern-domains">${domainBadges}</div>
          </div>
        `;

        section.appendChild(card);
      });

      patternsList.appendChild(section);
    }

    // Render query patterns
    if (patternsByType.query.length > 0) {
      const section = document.createElement("div");
      section.className = "pattern-section";
      section.innerHTML = `
        <h3 class="pattern-section-title">
          <i data-lucide="message-square" class="pattern-section-icon"></i>
          Query Patterns
        </h3>
        <div class="pattern-section-desc">How you typically phrase questions</div>
      `;

      patternsByType.query.forEach((pattern) => {
        const card = document.createElement("div");
        card.className = "pattern-card pattern-card-query";

        const domainBadges = pattern.domains
          .map((d) => `<span class="pattern-domain ${d}">${d}</span>`)
          .join("");

        // Show example fills
        let fillsHtml = "";
        if (
          pattern.common_fills &&
          Object.keys(pattern.common_fills).length > 0
        ) {
          fillsHtml = '<div class="pattern-fills">';
          for (const [key, values] of Object.entries(pattern.common_fills)) {
            if (values.length > 0) {
              fillsHtml += `<div class="pattern-fill"><strong>{${key}}:</strong> ${values.slice(0, 3).join(", ")}</div>`;
            }
          }
          fillsHtml += "</div>";
        }

        card.innerHTML = `
          <div class="pattern-header">
            <div class="pattern-name">${pattern.query_template}</div>
            <div class="pattern-frequency">${pattern.frequency}×</div>
          </div>
          ${fillsHtml}
          <div class="pattern-meta">
            <div class="pattern-domains">${domainBadges}</div>
          </div>
        `;

        section.appendChild(card);
      });

      patternsList.appendChild(section);
    }

    // Render code patterns (if any)
    if (patternsByType.code.length > 0) {
      const section = document.createElement("div");
      section.className = "pattern-section";
      section.innerHTML = `
        <h3 class="pattern-section-title">
          <i data-lucide="code-2" class="pattern-section-icon"></i>
          Code Patterns
        </h3>
        <div class="pattern-section-desc">Recurring patterns in your code</div>
      `;

      patternsByType.code.forEach((pattern) => {
        const card = document.createElement("div");
        card.className = "pattern-card";

        const domainBadges = pattern.domains
          .map((d) => `<span class="pattern-domain ${d}">${d}</span>`)
          .join("");

        const confidencePercent = Math.round(pattern.confidence * 100);
        const confidenceClass =
          confidencePercent >= 70
            ? "high"
            : confidencePercent >= 40
              ? "medium"
              : "low";

        card.innerHTML = `
          <div class="pattern-header">
            <div class="pattern-name">${pattern.name}</div>
            <div class="pattern-confidence ${confidenceClass}">${confidencePercent}%</div>
          </div>
          <div class="pattern-description">${pattern.description}</div>
          <div class="pattern-meta">
            <span class="pattern-occurrences">
              <i data-lucide="repeat" class="pattern-meta-icon"></i>
              ${pattern.occurrences} times
            </span>
            <div class="pattern-domains">${domainBadges}</div>
          </div>
        `;

        section.appendChild(card);
      });

      patternsList.appendChild(section);
    }

    // Re-initialize lucide icons
    lucide.createIcons();
  } catch (error) {
    console.log("Could not load patterns:", error.message);
    const patternsList = document.getElementById("patterns-list");
    patternsList.innerHTML = `
      <div class="pattern-empty">
        <i data-lucide="alert-circle" class="pattern-empty-icon"></i>
        <p>Could not load patterns</p>
        <p class="pattern-empty-hint">Make sure the Polly server is running.</p>
      </div>
    `;
    lucide.createIcons();
  }
}

/**
 * Filter patterns by time
 */
async function filterPatterns() {
  const timeFilter = document.getElementById("pattern-time-filter").value;

  try {
    const response = await fetch("http://127.0.0.1:11436/polly/patterns");
    if (!response.ok) return;

    const data = await response.json();

    if (timeFilter === "all") {
      // Show all patterns - just reload
      await loadPatterns();
      return;
    }

    // Filter by time
    const daysAgo = parseInt(timeFilter);
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - daysAgo);

    // Filter patterns
    const filteredPatterns = data.patterns.filter((p) => {
      const lastSeen = new Date(p.last_seen);
      return lastSeen >= cutoffDate;
    });

    // Display filtered patterns
    const patternsList = document.getElementById("patterns-list");
    patternsList.innerHTML = "";

    if (filteredPatterns.length === 0) {
      patternsList.innerHTML = `
        <div class="pattern-empty">
          <i data-lucide="calendar" class="pattern-empty-icon"></i>
          <p>No patterns in this time range.</p>
          <p class="pattern-empty-hint">Try a different time filter.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    // Group and render (similar to loadPatterns)
    const patternsByType = {
      conceptual: [],
      code: [],
      query: [],
    };

    filteredPatterns.forEach((p) => {
      if (patternsByType[p.pattern_type]) {
        patternsByType[p.pattern_type].push(p);
      }
    });

    // Render each type (simplified version)
    Object.entries(patternsByType).forEach(([type, patterns]) => {
      if (patterns.length === 0) return;

      const section = document.createElement("div");
      section.className = "pattern-section";

      const titles = {
        conceptual: "Conceptual Patterns",
        code: "Code Patterns",
        query: "Query Patterns",
      };

      const icons = {
        conceptual: "brain",
        code: "code-2",
        query: "message-square",
      };

      section.innerHTML = `
        <h3 class="pattern-section-title">
          <i data-lucide="${icons[type]}" class="pattern-section-icon"></i>
          ${titles[type]}
        </h3>
      `;

      patterns.forEach((pattern) => {
        const card = document.createElement("div");
        card.className = "pattern-card";

        const domainBadges = pattern.domains
          ? pattern.domains
              .map((d) => `<span class="pattern-domain ${d}">${d}</span>`)
              .join("")
          : "";

        const confidencePercent = Math.round(pattern.confidence * 100);
        const confidenceClass =
          confidencePercent >= 70
            ? "high"
            : confidencePercent >= 40
              ? "medium"
              : "low";

        card.innerHTML = `
          <div class="pattern-header">
            <div class="pattern-name">${pattern.name}</div>
            <div class="pattern-confidence ${confidenceClass}">${confidencePercent}%</div>
          </div>
          <div class="pattern-description">${pattern.description}</div>
          <div class="pattern-meta">
            <span class="pattern-occurrences">
              <i data-lucide="repeat" class="pattern-meta-icon"></i>
              ${pattern.occurrences} times
            </span>
            <div class="pattern-domains">${domainBadges}</div>
          </div>
        `;

        section.appendChild(card);
      });

      patternsList.appendChild(section);
    });

    lucide.createIcons();
  } catch (error) {
    console.error("Error filtering patterns:", error);
  }
}

/**
 * Export patterns to JSON file
 */
async function exportPatterns() {
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/patterns");
    if (!response.ok) {
      alert("Could not export patterns");
      return;
    }

    const data = await response.json();

    // Create blob and download
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `polly-patterns-${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showNotification("Patterns exported successfully");
  } catch (error) {
    console.error("Error exporting patterns:", error);
    showNotification("Failed to export patterns", "error");
  }
}

/**
 * Reset all patterns with confirmation
 */
async function resetPatterns() {
  const confirmed = confirm(
    "Are you sure you want to reset all learned patterns?\n\n" +
      "This will:\n" +
      "• Delete all patterns\n" +
      "• Clear query history\n" +
      "• Create a backup first\n\n" +
      "This action cannot be undone.",
  );

  if (!confirmed) return;

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/patterns/reset",
      {
        method: "POST",
      },
    );

    if (!response.ok) {
      throw new Error("Reset failed");
    }

    const result = await response.json();

    if (result.backup_path) {
      showNotification(
        `Patterns reset. Backup saved to: ${result.backup_path}`,
      );
    } else {
      showNotification("Patterns reset successfully");
    }

    // Reload patterns (should show empty state)
    await loadPatterns();
  } catch (error) {
    console.error("Error resetting patterns:", error);
    showNotification("Failed to reset patterns", "error");
  }
}

/**
 * Show notification to user
 */
function showNotification(message, type = "success") {
  // Simple alert-based notification
  // In the future, this could be replaced with a toast notification
  if (type === "error") {
    alert(`Error: ${message}`);
  } else {
    alert(message);
  }
}

/**
 * Save settings
 */
async function saveSettings() {
  const routingModeEl = document.getElementById("settings-routing-mode");
  const apiKeyEl = document.getElementById("settings-api-key");
  const portEl = document.getElementById("settings-port");
  const autoStartEl = document.getElementById("settings-auto-start");

  // Save settings only if elements exist (they might be in different tabs)
  if (routingModeEl) {
    await window.polly.setStore("routingMode", routingModeEl.value);
  }

  if (portEl) {
    await window.polly.setStore("port", parseInt(portEl.value));
  }

  if (autoStartEl) {
    await window.polly.setStore("autoStart", autoStartEl.checked);
  }

  if (apiKeyEl && apiKeyEl.value) {
    // In production, this should be stored securely
    await window.polly.setStore("apiKey", apiKeyEl.value);
  }

  // Note: vault path is now managed in Integrations → Obsidian
  await window.polly.setStore("codebasePaths", codePaths);

  // Save deduplication settings (Phase 21)
  try {
    await saveDedupSettings();
  } catch (error) {
    console.error("Failed to save dedup settings:", error);
    alert("Settings saved, but deduplication settings failed to save.");
    return;
  }

  alert("Settings saved!");
}

/**
 * ===========================================
 * SETTINGS TABS
 * ===========================================
 */

// Tab switching logic
function initSettingsTabs() {
  const tabButtons = document.querySelectorAll(".settings-tab-btn");
  const tabContents = document.querySelectorAll(".settings-tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const targetTab = button.dataset.tab;

      // Update button states
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");

      // Update content visibility
      tabContents.forEach((content) => {
        if (content.id === `tab-${targetTab}`) {
          content.classList.remove("hidden");
        } else {
          content.classList.add("hidden");
        }
      });

      // Load domains config when switching to domains tab
      if (targetTab === "domains") {
        loadDomainsConfig();
      }

      // Load routing settings when switching to routing tab
      if (targetTab === "routing") {
        loadRoutingSettings();
        loadRoutingStats();
      }

      // Load compression settings when switching to compression tab
      if (targetTab === "compression") {
        loadCompressionSettings();
        loadCompressionStats();
      }

      // Load mental models when switching to mental models tab (Phase 14)
      if (targetTab === "mental-models") {
        loadMentalModels();
      }

      // Load dedup settings when switching to advanced tab (Phase 21)
      if (targetTab === "advanced") {
        loadDedupSettings();
      }
    });
  });
}

/**
 * ===========================================
 * GENERAL SETTINGS
 * ===========================================
 */

async function loadGeneralSettings() {
  try {
    const response = await fetch(`${API_URL}/api/settings/general`);
    if (!response.ok) {
      console.error("Failed to load general settings:", response.status);
      return;
    }

    const data = await response.json();
    if (data.success && data.settings) {
      // Update routing mode dropdown
      const routingModeSelect = document.getElementById("settings-routing-mode");
      if (routingModeSelect) {
        routingModeSelect.value = data.settings.routing_mode || "auto";
      }

      // Update LiteLLM toggle
      const useLiteLLMCheckbox = document.getElementById("settings-use-litellm");
      if (useLiteLLMCheckbox) {
        useLiteLLMCheckbox.checked = data.settings.use_litellm !== false;
      }
    }
  } catch (error) {
    console.error("Error loading general settings:", error);
  }
}

async function saveGeneralSettings() {
  try {
    const routingMode = document.getElementById("settings-routing-mode")?.value || "auto";
    const useLiteLLM = document.getElementById("settings-use-litellm")?.checked !== false;

    const response = await fetch(`${API_URL}/api/settings/general`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        routing_mode: routingMode,
        use_litellm: useLiteLLM
      })
    });

    if (!response.ok) {
      throw new Error("Failed to save general settings");
    }

    const data = await response.json();
    if (data.success) {
      showToast(data.message || "General settings saved", "success");
      
      // If LiteLLM setting changed, reload provider list if on that tab
      const providersTab = document.getElementById("settings-section-providers");
      if (providersTab && !providersTab.classList.contains("hidden")) {
        await loadProviderSettings();
      }
    } else {
      throw new Error(data.error || "Unknown error");
    }
  } catch (error) {
    console.error("Error saving general settings:", error);
    showToast("Failed to save general settings: " + error.message, "error");
  }
}

function setupGeneralSettings() {
  // Routing mode dropdown
  const routingModeSelect = document.getElementById("settings-routing-mode");
  if (routingModeSelect) {
    routingModeSelect.addEventListener("change", saveGeneralSettings);
  }

  // LiteLLM toggle
  const useLiteLLMCheckbox = document.getElementById("settings-use-litellm");
  if (useLiteLLMCheckbox) {
    useLiteLLMCheckbox.addEventListener("change", saveGeneralSettings);
  }
}

/**
 * ===========================================
 * ROUTING SETTINGS
 * ===========================================
 */

/**
 * Load routing settings from server
 */
async function loadRoutingSettings() {
  try {
    const response = await fetch("http://127.0.0.1:11436/routing/settings");
    if (!response.ok) {
      console.error("Failed to load routing settings:", response.status);
      return;
    }

    const data = await response.json();
    const thresholds = data.thresholds || {};

    // Update sliders and value displays
    updateRoutingSlider(
      "routing-min-top-score",
      thresholds.min_top_score || 0.75,
    );
    updateRoutingSlider(
      "routing-min-quality-results",
      thresholds.min_high_quality_results || 2,
    );
    updateRoutingSlider(
      "routing-min-context-chars",
      thresholds.min_context_chars || 500,
    );
    updateRoutingSlider(
      "routing-exceptional-score",
      thresholds.exceptional_score || 0.85,
    );
    updateRoutingSlider(
      "routing-exceptional-min-results",
      thresholds.exceptional_min_results || 3,
    );

    console.log("Loaded routing settings:", data);
  } catch (error) {
    console.error("Error loading routing settings:", error);
  }
}

/**
 * Load routing statistics from server
 */
async function loadRoutingStats() {
  try {
    const response = await fetch("http://127.0.0.1:11436/routing/stats");
    if (!response.ok) {
      console.error("Failed to load routing stats:", response.status);
      return;
    }

    const data = await response.json();

    // Update stat displays
    const statLocalToday = document.getElementById("stat-local-today");
    const statCloudToday = document.getElementById("stat-cloud-today");
    const statAvgLocalScore = document.getElementById("stat-avg-local-score");
    const statCostSaved = document.getElementById("stat-cost-saved");

    if (statLocalToday) statLocalToday.textContent = data.local_today || 0;
    if (statCloudToday) statCloudToday.textContent = data.cloud_today || 0;
    if (statAvgLocalScore)
      statAvgLocalScore.textContent = data.avg_local_score
        ? data.avg_local_score.toFixed(2)
        : "N/A";
    if (statCostSaved)
      statCostSaved.textContent =
        data.cost_saved_today && typeof data.cost_saved_today === "number"
          ? `$${data.cost_saved_today.toFixed(2)}`
          : "$0.00";

    console.log("Loaded routing stats:", data);
  } catch (error) {
    console.error("Error loading routing stats:", error);
  }
}

/**
 * Update a routing slider and its value display
 */
function updateRoutingSlider(sliderId, value) {
  const slider = document.getElementById(sliderId);
  const valueDisplay = document.getElementById(`${sliderId}-value`);

  if (slider) {
    slider.value = value;
  }
  if (valueDisplay) {
    valueDisplay.textContent = value;
  }
}

/**
 * Initialize routing settings event listeners
 */
function initRoutingSettings() {
  // Slider value update listeners
  const sliders = [
    "routing-min-top-score",
    "routing-min-quality-results",
    "routing-min-context-chars",
    "routing-exceptional-score",
    "routing-exceptional-min-results",
  ];

  sliders.forEach((sliderId) => {
    const slider = document.getElementById(sliderId);
    if (slider) {
      slider.addEventListener("input", (e) => {
        const valueDisplay = document.getElementById(`${sliderId}-value`);
        if (valueDisplay) {
          valueDisplay.textContent = e.target.value;
        }
      });
    }
  });

  // Save button
  const saveBtn = document.getElementById("btn-save-routing-settings");
  if (saveBtn) {
    saveBtn.addEventListener("click", saveRoutingSettings);
  }

  // Reset button
  const resetBtn = document.getElementById("btn-reset-routing-settings");
  if (resetBtn) {
    resetBtn.addEventListener("click", resetRoutingSettings);
  }

  // Preset buttons
  const aggressiveBtn = document.getElementById("routing-preset-aggressive");
  if (aggressiveBtn) {
    aggressiveBtn.addEventListener("click", () =>
      applyRoutingPreset("aggressive"),
    );
  }

  const balancedBtn = document.getElementById("routing-preset-balanced");
  if (balancedBtn) {
    balancedBtn.addEventListener("click", () => applyRoutingPreset("balanced"));
  }

  const conservativeBtn = document.getElementById(
    "routing-preset-conservative",
  );
  if (conservativeBtn) {
    conservativeBtn.addEventListener("click", () =>
      applyRoutingPreset("conservative"),
    );
  }
}

/**
 * Save routing settings to server
 */
async function saveRoutingSettings() {
  try {
    const settings = {
      enabled: true,
      thresholds: {
        min_top_score: parseFloat(
          document.getElementById("routing-min-top-score").value,
        ),
        min_high_quality_results: parseInt(
          document.getElementById("routing-min-quality-results").value,
        ),
        min_context_chars: parseInt(
          document.getElementById("routing-min-context-chars").value,
        ),
        exceptional_score: parseFloat(
          document.getElementById("routing-exceptional-score").value,
        ),
        exceptional_min_results: parseInt(
          document.getElementById("routing-exceptional-min-results").value,
        ),
      },
    };

    const response = await fetch("http://127.0.0.1:11436/routing/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      throw new Error(`Failed to save: ${response.status}`);
    }

    alert("Routing settings saved successfully!");

    // Reload stats to show impact
    await loadRoutingStats();
  } catch (error) {
    console.error("Error saving routing settings:", error);
    alert(`Failed to save routing settings: ${error.message}`);
  }
}

/**
 * Reset routing settings to defaults
 */
async function resetRoutingSettings() {
  if (!confirm("Reset routing settings to defaults?")) {
    return;
  }

  // Apply balanced preset (default)
  applyRoutingPreset("balanced");
}

/**
 * Apply a routing preset
 */
function applyRoutingPreset(preset) {
  const presets = {
    aggressive: {
      min_top_score: 0.65,
      min_high_quality_results: 1,
      min_context_chars: 300,
      exceptional_score: 0.75,
      exceptional_min_results: 1,
    },
    balanced: {
      min_top_score: 0.75,
      min_high_quality_results: 2,
      min_context_chars: 500,
      exceptional_score: 0.85,
      exceptional_min_results: 3,
    },
    conservative: {
      min_top_score: 0.85,
      min_high_quality_results: 3,
      min_context_chars: 800,
      exceptional_score: 0.9,
      exceptional_min_results: 4,
    },
  };

  const values = presets[preset];
  if (!values) {
    console.error("Unknown preset:", preset);
    return;
  }

  // Update all sliders
  updateRoutingSlider("routing-min-top-score", values.min_top_score);
  updateRoutingSlider(
    "routing-min-quality-results",
    values.min_high_quality_results,
  );
  updateRoutingSlider("routing-min-context-chars", values.min_context_chars);
  updateRoutingSlider("routing-exceptional-score", values.exceptional_score);
  updateRoutingSlider(
    "routing-exceptional-min-results",
    values.exceptional_min_results,
  );

  console.log(`Applied ${preset} preset`);
}

/**
 * ===========================================
 * INTEGRATION CARDS
 * ===========================================
 */

// Toggle integration config panel
function initIntegrationConfig() {
  const configButtons = document.querySelectorAll('[id$="-config-btn"]');
  console.log(
    "Found config buttons:",
    configButtons.length,
    Array.from(configButtons).map((b) => b.id),
  );

  configButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      console.log("Config button clicked:", e.target.id);
      const integration = e.target.id.replace("-config-btn", "");
      const configPanel = document.getElementById(`${integration}-config`);
      console.log(
        "Config panel:",
        configPanel,
        "hidden?",
        configPanel?.classList.contains("hidden"),
      );

      if (configPanel && configPanel.classList.contains("hidden")) {
        configPanel.classList.remove("hidden");
        e.target.textContent = "hide config";
        console.log("Showed config panel");

        // Load integration-specific config when opening
        if (integration === "obsidian") {
          loadObsidianVaultPath();
        }
      } else if (configPanel) {
        configPanel.classList.add("hidden");
        e.target.textContent = "configure";
        console.log("Hid config panel");
      }
    });
  });
}

// Helper: Update integration card status
function updateIntegrationCard(integration, data) {
  const card = document.querySelector(`[data-integration="${integration}"]`);
  if (!card) return;

  const statusDot = card.querySelector(".status-dot");
  const statusText = card.querySelector(".status-text");
  const connectBtn =
    card.querySelector(`#${integration}-connect-btn`) ||
    card.querySelector(`#${integration}-enable-btn`);
  const syncBtn = card.querySelector(`#${integration}-sync-btn`);
  const configBtn = card.querySelector(`#${integration}-config-btn`);

  if (data.authenticated || data.enabled) {
    // Connected state
    if (statusDot) statusDot.classList.add("connected");
    if (statusText) statusText.textContent = data.statusText || "connected";

    if (connectBtn) {
      connectBtn.classList.add("hidden");
    }
    if (syncBtn) {
      syncBtn.classList.remove("hidden");
    }
    if (configBtn) {
      configBtn.classList.remove("hidden");
    }

    // Update last sync time if available
    if (data.last_sync) {
      const lastSyncEl = card.querySelector(".last-sync");
      if (lastSyncEl) {
        lastSyncEl.textContent = `Last sync: ${formatTimeAgo(data.last_sync)}`;
      }
    }
  } else {
    // Disconnected state
    if (statusDot) statusDot.classList.remove("connected");
    if (statusText) statusText.textContent = data.statusText || "not connected";

    if (connectBtn) {
      connectBtn.classList.remove("hidden");
    }
    if (syncBtn) {
      syncBtn.classList.add("hidden");
    }
    if (configBtn) {
      configBtn.classList.add("hidden");
    }
  }
}

// Helper: Format time ago
function formatTimeAgo(timestamp) {
  const now = new Date();
  const then = new Date(timestamp);
  const seconds = Math.floor((now - then) / 1000);

  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
  return `${Math.floor(seconds / 86400)} days ago`;
}

// Restore integration status from stored credentials
async function restoreIntegrationStatus() {
  // Wait for HTTP server to be reachable (not just process running)
  const serverReady = await waitForServerReady({ timeoutMs: 15000, intervalMs: 500 });
  if (!serverReady) {
    console.warn("Server not ready, skipping integration restore");
    return;
  }
  // Brief delay so Polly has a chance to finish init (reduces 503s)
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // Check GitHub connection
  const githubToken = await window.polly.getCredential("github_token");
  if (githubToken && githubToken.success && githubToken.password) {
    const username = await window.polly.getStore("github_username");
    if (username) {
      updateIntegrationCard("github", {
        authenticated: true,
        statusText: `connected as @${username}`,
      });

      // Reconnect to backend
      try {
        const backendResult = await window.polly.integrationConnect("github", {
          token: githubToken.password,
        });
        console.log("Backend connection result:", backendResult);

        if (backendResult && !backendResult.success) {
          // 503 / connection issues often mean Polly still initializing
          console.warn("Backend connection:", backendResult.error || "not ready yet. Click \"sync now\" to retry.");
        }
      } catch (error) {
        const isRefused = (error.message || "").includes("ECONNREFUSED") || (error.message || "").includes("Failed to fetch");
        if (isRefused) {
          console.warn("Backend not ready yet; click \"sync now\" to retry.");
        } else {
          console.error("Backend connection error:", error);
        }
      }
    }
  }

  // Check Context7 connection
  try {
    const context7ApiKey = await window.polly.getCredential("context7_api_key");
    if (context7ApiKey && context7ApiKey.success && context7ApiKey.password) {
      console.log("Found saved Context7 API key, reconnecting...");

      updateIntegrationCard("context7", {
        authenticated: true,
        statusText: "connected",
      });

      // Show sync and config buttons
      const connectBtn = document.getElementById("context7-connect-btn");
      const syncBtn = document.getElementById("context7-sync-btn");
      const configBtn = document.getElementById("context7-config-btn");

      if (connectBtn) connectBtn.classList.add("hidden");
      if (syncBtn) syncBtn.classList.remove("hidden");
      if (configBtn) configBtn.classList.remove("hidden");

      // Reconnect to backend
      try {
        const backendResult = await fetch(
          "http://127.0.0.1:11436/polly/integrations/connect",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              integration: "context7",
              credentials: { api_key: context7ApiKey.password },
            }),
          },
        );

        const result = await backendResult.json();
        console.log("Context7 backend reconnect result:", result);

        if (result && !result.success) {
          console.warn("Context7 backend:", result.error || "not ready yet");
          updateIntegrationCard("context7", {
            authenticated: false,
            statusText: "connection failed",
          });
        } else {
          console.log("Context7 backend reconnected successfully");
        }
      } catch (error) {
        const isRefused = (error.message || "").includes("ECONNREFUSED") || (error.message || "").includes("Failed to fetch");
        if (isRefused) {
          console.warn("Context7: backend not ready yet.");
        } else {
          console.error("Context7 backend connection error:", error);
        }
        updateIntegrationCard("context7", {
          authenticated: false,
          statusText: "connection error",
        });
      }
    } else {
      console.log("No saved Context7 API key found");
    }
  } catch (error) {
    console.error("Error checking Context7 credentials:", error);
  }

  // Check Obsidian connection - it should auto-connect on server startup
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/integrations");
    if (!response.ok && response.status === 503) {
      console.warn("Integrations endpoint returned 503 (Polly still initializing).");
      return;
    }
    const result = await response.json();

    if (result.integrations && result.integrations.obsidian) {
      const obsidianStatus = result.integrations.obsidian;

      if (obsidianStatus.status === "connected") {
        console.log("Obsidian integration is connected");
        updateIntegrationCard("obsidian", {
          authenticated: true,
          statusText: "connected",
        });

        // Show sync button and stats
        const syncBtn = document.getElementById("obsidian-sync-btn");
        if (syncBtn) syncBtn.classList.remove("hidden");

        const writeTestBtn = document.getElementById("obsidian-write-test-btn");
        if (writeTestBtn) writeTestBtn.classList.remove("hidden");

        const statsDiv = document.getElementById("obsidian-stats");
        if (statsDiv) statsDiv.classList.remove("hidden");

        // Update vault path
        if (obsidianStatus.vault_path) {
          const vaultPathEl = document.getElementById(
            "obsidian-vault-path-display",
          );
          if (vaultPathEl) {
            const vaultName = obsidianStatus.vault_path.split("/").pop();
            vaultPathEl.textContent = vaultName;
          }
        }

        // Update indexed files count
        if (obsidianStatus.indexed_files !== undefined) {
          const indexedFilesEl = document.getElementById(
            "obsidian-indexed-files",
          );
          if (indexedFilesEl) {
            indexedFilesEl.textContent = obsidianStatus.indexed_files;
          }
        }
      } else {
        console.log("Obsidian integration not connected yet");
      }
    }
  } catch (error) {
    console.error("Error checking Obsidian status:", error);
  }

  // Check iCal connections (Phase 4)
  // etc.
}

// Helper: Update integration status (simple wrapper)
function updateIntegrationStatus(integration, status) {
  updateIntegrationCard(integration, {
    authenticated: status === "connected",
    statusText: status,
  });
}

// Sync Calendar Events
async function syncCalendar(daysAhead = 7) {
  const syncBtn = document.getElementById("calendar-sync-btn");

  if (syncBtn) {
    syncBtn.disabled = true;
    syncBtn.textContent = "Syncing...";
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/integrations/sync",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          integration: "calendar",
          options: {
            days_ahead: daysAhead,
          },
        }),
      },
    );

    const result = await response.json();

    if (result.success) {
      console.log("Calendar sync successful:", result);
      updateIntegrationCard("calendar", {
        authenticated: true,
        statusText: `synced ${result.fetched} events`,
        last_sync: new Date().toISOString(),
      });
    } else {
      console.error("Calendar sync failed:", result);
      alert(`Sync failed: ${result.detail || "Unknown error"}`);
    }
  } catch (error) {
    console.error("Calendar sync error:", error);
    alert("Sync failed. Is the server running?");
  } finally {
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.textContent = "sync now";
    }
  }
}

// Sync Reminders
async function syncReminders(includeCompleted = false) {
  const syncBtn = document.getElementById("reminders-sync-btn");

  if (syncBtn) {
    syncBtn.disabled = true;
    syncBtn.textContent = "Syncing...";
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/integrations/sync",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          integration: "reminders",
          options: {
            include_completed: includeCompleted,
          },
        }),
      },
    );

    const result = await response.json();

    if (result.success) {
      console.log("Reminders sync successful:", result);
      updateIntegrationCard("reminders", {
        authenticated: true,
        statusText: `synced ${result.fetched} reminders`,
        last_sync: new Date().toISOString(),
      });
    } else {
      console.error("Reminders sync failed:", result);
      alert(`Sync failed: ${result.detail || "Unknown error"}`);
    }
  } catch (error) {
    console.error("Reminders sync error:", error);
    alert("Sync failed. Is the server running?");
  } finally {
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.textContent = "sync now";
    }
  }
}

// Sync Context7 Documentation
async function syncContext7Documentation(
  libraries = ["react", "nextjs", "python"],
) {
  const syncBtn = document.getElementById("context7-sync-btn");

  if (syncBtn) {
    syncBtn.disabled = true;
    syncBtn.textContent = "Syncing...";
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/integrations/sync",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          integration: "context7",
          options: {
            libraries: libraries,
            query: "comprehensive documentation and examples",
          },
        }),
      },
    );

    const result = await response.json();

    if (result.success) {
      console.log("Context7 sync successful:", result);
      updateIntegrationCard("context7", {
        authenticated: true,
        statusText: `synced ${result.fetched} docs`,
        last_sync: new Date().toISOString(),
      });
    } else {
      console.error("Context7 sync failed:", result);
      alert(`Sync failed: ${result.detail || "Unknown error"}`);
    }
  } catch (error) {
    console.error("Context7 sync error:", error);
    alert("Sync failed. Is the server running?");
  } finally {
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.textContent = "sync now";
    }
  }
}

// Sync Obsidian Vault
async function syncObsidian() {
  const syncBtn = document.getElementById("obsidian-sync-btn");

  if (syncBtn) {
    syncBtn.disabled = true;
    syncBtn.textContent = "Syncing...";
  }

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/integrations/sync",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          integration: "obsidian",
          options: {},
        }),
      },
    );

    const result = await response.json();

    if (result.success) {
      console.log("Obsidian sync successful:", result);

      // Build status message
      let statusText = `synced ${result.indexed} documents`;
      if (result.skipped > 0) {
        statusText += ` (${result.skipped} skipped)`;
      }

      // Update status
      updateIntegrationCard("obsidian", {
        authenticated: true,
        statusText: statusText,
        last_sync: new Date().toISOString(),
      });

      // Update stats
      const indexedFilesEl = document.getElementById("obsidian-indexed-files");
      if (indexedFilesEl) {
        indexedFilesEl.textContent = result.indexed || 0;
      }

      // Update vault path if available
      const vaultPathEl = document.getElementById(
        "obsidian-vault-path-display",
      );
      if (vaultPathEl && result.metadata && result.metadata.vault_path) {
        // Show just the vault name (last part of path)
        const vaultName = result.metadata.vault_path.split("/").pop();
        vaultPathEl.textContent = vaultName;
      }
    } else {
      console.error("Obsidian sync failed:", result);
      alert(`Sync failed: ${result.detail || "Unknown error"}`);
    }
  } catch (error) {
    console.error("Obsidian sync error:", error);
    alert("Sync failed. Is the server running?");
  } finally {
    if (syncBtn) {
      syncBtn.disabled = false;
      syncBtn.textContent = "sync now";
    }
  }
}

// Load current Obsidian vault path
async function loadObsidianVaultPath() {
  try {
    const config = await window.polly.getConfig("obsidian.vault_path");
    if (config && config.success && config.value) {
      const pathInput = document.getElementById("obsidian-vault-path-input");
      if (pathInput) {
        pathInput.value = config.value;
      }
    }
  } catch (error) {
    console.error("Error loading vault path:", error);
  }
}

// Update Obsidian vault path display
function updateObsidianVaultDisplay(vaultPath) {
  const vaultPathEl = document.getElementById("obsidian-vault-path-display");
  if (vaultPathEl && vaultPath) {
    const vaultName = vaultPath.split("/").pop();
    vaultPathEl.textContent = vaultName;
  }
}

// Placeholder connect buttons (will be implemented in later phases)
function initIntegrationPlaceholders() {
  // GitHub OAuth link
  const githubOAuthLink = document.getElementById("github-oauth-link");
  if (githubOAuthLink) {
    githubOAuthLink.addEventListener("click", (e) => {
      e.preventDefault();
      window.polly.openExternal("https://github.com/settings/developers");
    });
  }

  // GitHub save config button
  const githubSaveConfigBtn = document.getElementById("github-save-config-btn");
  if (githubSaveConfigBtn) {
    githubSaveConfigBtn.addEventListener("click", async () => {
      const clientId = document.getElementById("github-client-id").value.trim();
      const clientSecret = document
        .getElementById("github-client-secret")
        .value.trim();

      if (!clientId || !clientSecret) {
        alert("Please enter both Client ID and Client Secret");
        return;
      }

      // Store in electron-store
      await window.polly.setStore("github_oauth_client_id", clientId);
      await window.polly.setStore("github_oauth_client_secret", clientSecret);

      alert(
        'GitHub OAuth configuration saved! You can now click "connect" to authenticate.',
      );

      // Show the connect button and hide config panel
      const configPanel = document.getElementById("github-config");
      if (configPanel) configPanel.classList.add("hidden");
    });
  }

  // Load saved OAuth config
  (async () => {
    const clientId = await window.polly.getStore("github_oauth_client_id");
    const clientSecret = await window.polly.getStore(
      "github_oauth_client_secret",
    );

    if (clientId) {
      document.getElementById("github-client-id").value = clientId;
    }
    if (clientSecret) {
      document.getElementById("github-client-secret").value = clientSecret;
    }
  })();

  // GitHub connect button
  const githubBtn = document.getElementById("github-connect-btn");
  if (githubBtn) {
    githubBtn.addEventListener("click", async () => {
      try {
        // Check if OAuth is configured
        const clientId = await window.polly.getStore("github_oauth_client_id");
        const clientSecret = await window.polly.getStore(
          "github_oauth_client_secret",
        );

        if (!clientId || !clientSecret) {
          alert(
            'Please configure GitHub OAuth first. Click the "configure" button to set up your Client ID and Secret.',
          );

          // Show config panel if available
          const configBtn = document.getElementById("github-config-btn");
          if (configBtn && configBtn.classList.contains("hidden")) {
            // Unhide config button temporarily so user can configure
            configBtn.classList.remove("hidden");
          }
          return;
        }

        // Update button state
        githubBtn.disabled = true;
        githubBtn.textContent = "connecting...";

        const result = await window.polly.githubOAuth();

        if (result.success) {
          // Update card to show connected state
          updateIntegrationCard("github", {
            authenticated: true,
            statusText: `connected as @${result.username}`,
            lastSync: new Date().toISOString(),
          });

          // Store username in electron-store for persistence
          await window.polly.setStore("github_username", result.username);

          // Connect integration to backend (pass token)
          const tokenResult = await window.polly.getCredential("github_token");
          if (tokenResult.success && tokenResult.password) {
            await window.polly.integrationConnect("github", {
              token: tokenResult.password,
            });
          }

          alert(`Successfully connected to GitHub as @${result.username}`);
        } else {
          alert(`Failed to connect to GitHub: ${result.error}`);
          githubBtn.disabled = false;
          githubBtn.textContent = "connect";
        }
      } catch (error) {
        alert(`Error: ${error.message}`);
        githubBtn.disabled = false;
        githubBtn.textContent = "connect";
      }
    });
  }

  // GitHub sync button
  const githubSyncBtn = document.getElementById("github-sync-btn");
  if (githubSyncBtn) {
    githubSyncBtn.addEventListener("click", async () => {
      try {
        githubSyncBtn.disabled = true;
        githubSyncBtn.textContent = "syncing...";

        // First, ensure backend is connected
        const statusResult = await window.polly.integrationStatus();
        const isConnected =
          statusResult.connected && statusResult.connected.includes("github");

        if (!isConnected) {
          console.log("Backend not connected, connecting now...");
          const token = await window.polly.getCredential("github_token");
          if (token.success && token.password) {
            const connectResult = await window.polly.integrationConnect(
              "github",
              { token: token.password },
            );
            if (!connectResult.success) {
              throw new Error(
                `Backend connection failed: ${connectResult.error}`,
              );
            }

            // Save Conversation Modal Handlers
            const closeSaveModalBtn =
              document.getElementById("close-save-modal");
            if (closeSaveModalBtn) {
              closeSaveModalBtn.addEventListener(
                "click",
                closeSaveConversationModal,
              );
            }

            const cancelSaveBtn = document.getElementById("btn-cancel-save");
            if (cancelSaveBtn) {
              cancelSaveBtn.addEventListener(
                "click",
                closeSaveConversationModal,
              );
            }

            const confirmSaveBtn = document.getElementById("btn-confirm-save");
            if (confirmSaveBtn) {
              confirmSaveBtn.addEventListener(
                "click",
                saveConversationToObsidian,
              );
            }

            const suggestFolderBtn =
              document.getElementById("btn-suggest-folder");
            if (suggestFolderBtn) {
              suggestFolderBtn.addEventListener("click", suggestFolder);
            }

            const useFolderBtn = document.getElementById("btn-use-folder");
            if (useFolderBtn) {
              useFolderBtn.addEventListener("click", () => {
                const suggestedFolder = document.getElementById(
                  "suggested-folder-name",
                ).textContent;
                document.getElementById("note-folder").value = suggestedFolder;
              });
            }

            const suggestTagsBtn = document.getElementById("btn-suggest-tags");
            if (suggestTagsBtn) {
              suggestTagsBtn.addEventListener("click", suggestTags);
            }
          } else {
            throw new Error("No GitHub token found. Please connect first.");
          }
        }

        // Now sync
        const result = await window.polly.integrationSync("github", {
          include_repos: true,
          include_issues: false,
          include_prs: false,
          repo_limit: 30,
        });

        if (result.success) {
          alert(
            `Synced ${result.fetched} items from GitHub. Indexed ${result.indexed} documents.`,
          );

          // Update last sync time
          updateIntegrationCard("github", {
            authenticated: true,
            statusText: `connected as @${await window.polly.getStore("github_username")}`,
            lastSync: new Date().toISOString(),
          });
        } else {
          alert(`Sync failed: ${result.error}`);
        }

        githubSyncBtn.disabled = false;
        githubSyncBtn.textContent = "sync now";
      } catch (error) {
        alert(`Error: ${error.message}`);
        console.error("Sync error:", error);
        githubSyncBtn.disabled = false;
        githubSyncBtn.textContent = "sync now";
      }
    });
  }

  // Context7 Integration
  const context7Btn = document.getElementById("context7-connect-btn");
  if (context7Btn) {
    context7Btn.addEventListener("click", () => {
      // Show modal
      document.getElementById("context7-modal").classList.remove("hidden");
      document.getElementById("context7-api-key-input").value = "";
      document.getElementById("context7-modal-error").classList.add("hidden");
      document.getElementById("context7-api-key-input").focus();
    });
  }

  // Context7 API key input - submit on Enter
  const context7ApiKeyInput = document.getElementById("context7-api-key-input");
  if (context7ApiKeyInput) {
    context7ApiKeyInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        document.getElementById("context7-connect-submit").click();
      }
    });
  }

  // Context7 modal submit
  const context7SubmitBtn = document.getElementById("context7-connect-submit");
  if (context7SubmitBtn) {
    context7SubmitBtn.addEventListener("click", async () => {
      const apiKey = document
        .getElementById("context7-api-key-input")
        .value.trim();
      const errorEl = document.getElementById("context7-modal-error");

      // Validate API key format
      if (!apiKey) {
        errorEl.textContent = "Please enter an API key";
        errorEl.classList.remove("hidden");
        return;
      }

      if (!apiKey.startsWith("ctx7sk-")) {
        errorEl.textContent =
          'Invalid API key format. Key must start with "ctx7sk-"';
        errorEl.classList.remove("hidden");
        return;
      }

      // Disable button and show loading
      context7SubmitBtn.disabled = true;
      context7SubmitBtn.textContent = "Connecting...";
      errorEl.classList.add("hidden");

      try {
        // Connect to Context7
        console.log("Attempting to connect to Context7...");
        const response = await fetch(
          "http://127.0.0.1:11436/polly/integrations/connect",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              integration: "context7",
              credentials: { api_key: apiKey },
            }),
          },
        );

        console.log("Response status:", response.status);
        console.log("Response headers:", response.headers);

        if (!response.ok) {
          const errorText = await response.text();
          console.error("Server error response:", errorText);
          errorEl.textContent = `Server error: ${response.status}`;
          errorEl.classList.remove("hidden");
          return;
        }

        const result = await response.json();
        console.log("Connection result:", result);

        if (result.success) {
          // Success! Save API key to credential store
          await window.polly.setCredential("context7_api_key", apiKey);

          // Close modal and update UI
          document.getElementById("context7-modal").classList.add("hidden");
          updateIntegrationStatus("context7", "connected");

          // Show sync and config buttons
          document
            .getElementById("context7-connect-btn")
            .classList.add("hidden");
          document
            .getElementById("context7-sync-btn")
            .classList.remove("hidden");

          const configBtn = document.getElementById("context7-config-btn");
          configBtn.classList.remove("hidden");

          // Note: Click handler is already attached by initIntegrationConfig()
          // which runs on DOMContentLoaded and attaches to all *-config-btn buttons

          // Optionally auto-sync
          setTimeout(() => syncContext7Documentation(), 1000);
        } else {
          errorEl.textContent = result.error || "Connection failed";
          errorEl.classList.remove("hidden");
        }
      } catch (error) {
        console.error("Context7 connection error:", error);
        console.error("Error details:", {
          message: error.message,
          stack: error.stack,
          type: error.constructor.name,
        });
        errorEl.textContent = `Connection failed: ${error.message}`;
        errorEl.classList.remove("hidden");
      } finally {
        context7SubmitBtn.disabled = false;
        context7SubmitBtn.textContent = "Connect";
      }
    });
  }

  // Context7 sync button - use selected libraries or defaults
  const context7SyncBtn = document.getElementById("context7-sync-btn");
  if (context7SyncBtn) {
    context7SyncBtn.addEventListener("click", () => {
      const checkboxes = document.querySelectorAll(
        ".context7-lib-checkbox:checked",
      );
      const customInput = document.getElementById(
        "context7-custom-libraries-input",
      );

      let libraries = Array.from(checkboxes).map((cb) => cb.value);

      // Add custom libraries
      if (customInput && customInput.value.trim()) {
        const customLibs = customInput.value
          .split(",")
          .map((lib) => lib.trim())
          .filter((lib) => lib);
        libraries.push(...customLibs);
      }

      // Use defaults if nothing selected
      if (libraries.length === 0) {
        libraries = ["react", "nextjs", "python"];
      }

      syncContext7Documentation(libraries);
    });
  }

  // Context7 Popular Libraries Management
  const POPULAR_LIBRARIES = [
    // Frontend Frameworks
    { name: "react", category: "Frontend" },
    { name: "vue", category: "Frontend" },
    { name: "angular", category: "Frontend" },
    { name: "svelte", category: "Frontend" },
    { name: "nextjs", category: "Frontend" },
    { name: "nuxt", category: "Frontend" },
    { name: "remix", category: "Frontend" },

    // Backend Frameworks
    { name: "express", category: "Backend" },
    { name: "fastapi", category: "Backend" },
    { name: "django", category: "Backend" },
    { name: "flask", category: "Backend" },
    { name: "nestjs", category: "Backend" },

    // Languages
    { name: "python", category: "Languages" },
    { name: "typescript", category: "Languages" },
    { name: "javascript", category: "Languages" },
    { name: "rust", category: "Languages" },
    { name: "go", category: "Languages" },

    // Mobile
    { name: "react-native", category: "Mobile" },
    { name: "flutter", category: "Mobile" },

    // Databases & ORMs
    { name: "prisma", category: "Database" },
    { name: "supabase", category: "Database" },
    { name: "postgresql", category: "Database" },
    { name: "mongodb", category: "Database" },

    // Styling
    { name: "tailwindcss", category: "Styling" },
    { name: "styled-components", category: "Styling" },

    // Build Tools
    { name: "vite", category: "Build" },
    { name: "webpack", category: "Build" },

    // Testing
    { name: "jest", category: "Testing" },
    { name: "vitest", category: "Testing" },
    { name: "playwright", category: "Testing" },
    { name: "cypress", category: "Testing" },
  ];

  // Populate popular libraries checkboxes
  function initContext7Libraries() {
    const container = document.getElementById("context7-popular-libraries");
    if (!container) return;

    container.innerHTML = "";

    POPULAR_LIBRARIES.forEach((lib) => {
      const checkbox = document.createElement("label");
      checkbox.style.cssText =
        "display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 4px 6px; border-radius: 3px; font-size: 12px;";
      checkbox.innerHTML = `
        <input type="checkbox" value="${lib.name}" class="context7-lib-checkbox" style="cursor: pointer;">
        <span style="user-select: none;">${lib.name}</span>
      `;

      checkbox.addEventListener("mouseenter", function () {
        this.style.background = "var(--bg-primary)";
      });
      checkbox.addEventListener("mouseleave", function () {
        this.style.background = "transparent";
      });

      container.appendChild(checkbox);
    });

    // Update preview when checkboxes change
    container.addEventListener("change", updateContext7Preview);
  }

  // Update the selected libraries preview
  function updateContext7Preview() {
    const checkboxes = document.querySelectorAll(
      ".context7-lib-checkbox:checked",
    );
    const customInput = document.getElementById(
      "context7-custom-libraries-input",
    );
    const preview = document.getElementById("context7-selected-preview");

    const selectedLibs = Array.from(checkboxes).map((cb) => cb.value);

    // Add custom libraries
    if (customInput && customInput.value.trim()) {
      const customLibs = customInput.value
        .split(",")
        .map((lib) => lib.trim())
        .filter((lib) => lib);
      selectedLibs.push(...customLibs);
    }

    if (selectedLibs.length === 0) {
      preview.textContent = "None selected";
      preview.style.color = "var(--text-secondary)";
    } else {
      preview.textContent = selectedLibs.join(", ");
      preview.style.color = "var(--text-primary)";
    }
  }

  // Initialize when config section opens
  initContext7Libraries();

  // Update preview when custom input changes
  const customInput = document.getElementById(
    "context7-custom-libraries-input",
  );
  if (customInput) {
    customInput.addEventListener("input", updateContext7Preview);
  }

  // Context7 save libraries button
  const context7SaveLibrariesBtn = document.getElementById(
    "context7-save-libraries-btn",
  );
  if (context7SaveLibrariesBtn) {
    context7SaveLibrariesBtn.addEventListener("click", () => {
      const checkboxes = document.querySelectorAll(
        ".context7-lib-checkbox:checked",
      );
      const customInput = document.getElementById(
        "context7-custom-libraries-input",
      );

      const libraries = Array.from(checkboxes).map((cb) => cb.value);

      // Add custom libraries
      if (customInput && customInput.value.trim()) {
        const customLibs = customInput.value
          .split(",")
          .map((lib) => lib.trim())
          .filter((lib) => lib);
        libraries.push(...customLibs);
      }

      if (libraries.length === 0) {
        alert("Please select at least one library");
        return;
      }

      syncContext7Documentation(libraries);
    });
  }

  // Obsidian Integration
  const obsidianConnectBtn = document.getElementById("obsidian-connect-btn");
  if (obsidianConnectBtn) {
    obsidianConnectBtn.addEventListener("click", async () => {
      obsidianConnectBtn.disabled = true;
      obsidianConnectBtn.textContent = "Connecting...";

      try {
        const response = await fetch(
          "http://127.0.0.1:11436/polly/integrations/connect",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              integration: "obsidian",
              credentials: {},
            }),
          },
        );

        const result = await response.json();

        if (result.success) {
          console.log("Obsidian connected successfully");
          updateIntegrationStatus("obsidian", "connected");

          // Show sync button
          const syncBtn = document.getElementById("obsidian-sync-btn");
          if (syncBtn) syncBtn.classList.remove("hidden");

          // Show stats
          const statsDiv = document.getElementById("obsidian-stats");
          if (statsDiv) statsDiv.classList.remove("hidden");

          // Trigger initial sync
          syncObsidian();
        } else {
          console.error("Obsidian connection failed:", result);
          updateIntegrationStatus("obsidian", "error");
          alert(`Connection failed: ${result.error || "Unknown error"}`);
        }
      } catch (error) {
        console.error("Obsidian connection error:", error);
        updateIntegrationStatus("obsidian", "error");
        alert("Connection failed. Is the server running?");
      } finally {
        obsidianConnectBtn.disabled = false;
        obsidianConnectBtn.textContent = "connect";
      }
    });
  }

  // Obsidian sync button
  const obsidianSyncBtn = document.getElementById("obsidian-sync-btn");
  if (obsidianSyncBtn) {
    obsidianSyncBtn.addEventListener("click", () => syncObsidian());
  }

  // Note: Obsidian config button is handled by initIntegrationConfig()

  // Obsidian choose folder button
  const obsidianChooseFolderBtn = document.getElementById(
    "obsidian-choose-folder-btn",
  );
  if (obsidianChooseFolderBtn) {
    obsidianChooseFolderBtn.addEventListener("click", async () => {
      try {
        const result = await window.polly.chooseDirectory();
        if (result && result.success && result.path) {
          const pathInput = document.getElementById(
            "obsidian-vault-path-input",
          );
          if (pathInput) {
            pathInput.value = result.path;
          }
        }
      } catch (error) {
        console.error("Error choosing folder:", error);
        alert("Failed to choose folder");
      }
    });
  }

  // Obsidian save config button
  const obsidianSaveConfigBtn = document.getElementById(
    "obsidian-save-config-btn",
  );
  if (obsidianSaveConfigBtn) {
    obsidianSaveConfigBtn.addEventListener("click", async () => {
      const pathInput = document.getElementById("obsidian-vault-path-input");
      const syncEnabledCheckbox = document.getElementById(
        "obsidian-sync-enabled",
      );
      const vaultPath = pathInput?.value;
      const syncEnabled = syncEnabledCheckbox?.checked || false;

      if (syncEnabled && !vaultPath) {
        alert("Please select a vault folder when sync is enabled");
        return;
      }

      obsidianSaveConfigBtn.disabled = true;
      obsidianSaveConfigBtn.textContent = "Saving...";

      try {
        // Save sync preference
        await window.polly.updateConfig(
          "notes.obsidian.sync_enabled",
          syncEnabled,
        );

        // Save vault path if provided
        if (vaultPath) {
          await window.polly.updateConfig("obsidian.vault_path", vaultPath);
        }

        // Hide config panel
        const configPanel = document.getElementById("obsidian-config");
        if (configPanel) {
          configPanel.classList.add("hidden");
        }

        if (syncEnabled) {
          // Try to connect to Obsidian if sync is enabled
          const response = await fetch(
            "http://127.0.0.1:11436/polly/integrations/connect",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                integration: "obsidian",
                credentials: {},
              }),
            },
          );

          const result = await response.json();

          if (result.success) {
            console.log("Obsidian connected successfully");
            updateIntegrationStatus("obsidian", "connected");

            // Show sync button
            const syncBtn = document.getElementById("obsidian-sync-btn");
            if (syncBtn) syncBtn.classList.remove("hidden");

            // Show write test button
            const writeTestBtn = document.getElementById(
              "obsidian-write-test-btn",
            );
            if (writeTestBtn) writeTestBtn.classList.remove("hidden");

            // Show stats
            const statsDiv = document.getElementById("obsidian-stats");
            if (statsDiv) statsDiv.classList.remove("hidden");

            // Update vault path display
            updateObsidianVaultDisplay(vaultPath);

            alert(
              "Obsidian sync enabled! New notes will be copied to your vault.",
            );
          } else {
            console.error("Obsidian connection failed:", result);
            alert(
              `Failed to connect to vault: ${result.error || "Unknown error"}`,
            );
          }
        } else {
          // Sync disabled
          updateIntegrationStatus("obsidian", "not connected");
          alert("Configuration saved. Obsidian sync is disabled.");
        }
      } catch (error) {
        console.error("Error saving Obsidian config:", error);
        alert("Failed to save configuration");
      } finally {
        obsidianSaveConfigBtn.disabled = false;
        obsidianSaveConfigBtn.textContent = "Save Configuration";
      }
    });
  }

  // Obsidian write test toggle button
  const obsidianWriteTestBtn = document.getElementById(
    "obsidian-write-test-btn",
  );
  if (obsidianWriteTestBtn) {
    obsidianWriteTestBtn.addEventListener("click", () => {
      const testPanel = document.getElementById("obsidian-write-test");
      if (testPanel) {
        testPanel.classList.toggle("hidden");
      }
    });
  }

  // Obsidian write test - create note
  const obsidianTestCreateBtn = document.getElementById(
    "obsidian-test-create-btn",
  );
  if (obsidianTestCreateBtn) {
    obsidianTestCreateBtn.addEventListener("click", async () => {
      const title = document.getElementById("obsidian-test-title").value;
      const content = document.getElementById("obsidian-test-content").value;
      const folder = document.getElementById("obsidian-test-folder").value;

      if (!title) {
        alert("Please enter a note title");
        return;
      }

      obsidianTestCreateBtn.disabled = true;
      obsidianTestCreateBtn.textContent = "Creating...";

      try {
        // Step 1: Get preview
        const previewResponse = await fetch(
          "http://127.0.0.1:11436/polly/obsidian/create-note",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              title: title,
              content: content,
              folder: folder || null,
              tags: ["test"],
              confirmed: false,
            }),
          },
        );

        const preview = await previewResponse.json();
        console.log("Note preview:", preview);

        // Step 2: Show confirmation dialog
        const confirmMsg = `Create note: ${preview.note_path}\n\nPreview:\n${preview.content_preview}\n\nProceed?`;
        if (!confirm(confirmMsg)) {
          obsidianTestCreateBtn.disabled = false;
          obsidianTestCreateBtn.textContent = "Create Test Note";
          return;
        }

        // Step 3: Execute creation
        const createResponse = await fetch(
          "http://127.0.0.1:11436/polly/obsidian/create-note",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              confirmed: true,
              preview: preview,
            }),
          },
        );

        const result = await createResponse.json();
        console.log("Create result:", result);

        if (result.success) {
          alert(`Note created successfully!\n${result.note_path}`);
          // Clear form
          document.getElementById("obsidian-test-title").value = "";
          document.getElementById("obsidian-test-content").value = "";
          document.getElementById("obsidian-test-folder").value = "";
        } else {
          alert(`Failed to create note: ${result.error || "Unknown error"}`);
        }
      } catch (error) {
        console.error("Error creating note:", error);
        alert("Failed to create note. Check console for details.");
      } finally {
        obsidianTestCreateBtn.disabled = false;
        obsidianTestCreateBtn.textContent = "Create Test Note";
      }
    });
  }

  // Calendar Integration
  const calendarConnectBtn = document.getElementById("calendar-connect-btn");
  if (calendarConnectBtn) {
    calendarConnectBtn.addEventListener("click", async () => {
      calendarConnectBtn.disabled = true;
      calendarConnectBtn.textContent = "Connecting...";

      try {
        const response = await fetch(
          "http://127.0.0.1:11436/polly/integrations/connect",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              integration: "calendar",
              credentials: {}, // No credentials needed for macOS Calendar
            }),
          },
        );

        const result = await response.json();

        if (result.success) {
          updateIntegrationStatus("calendar", "connected");

          // Show sync and config buttons
          document
            .getElementById("calendar-connect-btn")
            .classList.add("hidden");
          document
            .getElementById("calendar-sync-btn")
            .classList.remove("hidden");
          document
            .getElementById("calendar-config-btn")
            .classList.remove("hidden");

          // Auto-sync
          setTimeout(() => syncCalendar(), 500);
        } else {
          alert(
            `Calendar connection failed: ${result.error || "Unknown error"}`,
          );
          updateIntegrationStatus("calendar", "error");
        }
      } catch (error) {
        console.error("Calendar connection error:", error);
        alert("Connection failed. Is the server running?");
      } finally {
        calendarConnectBtn.disabled = false;
        calendarConnectBtn.textContent = "enable";
      }
    });
  }

  // Calendar sync
  const calendarSyncBtn = document.getElementById("calendar-sync-btn");
  if (calendarSyncBtn) {
    calendarSyncBtn.addEventListener("click", () => syncCalendar());
  }

  // Calendar config save
  const calendarSaveConfigBtn = document.getElementById(
    "calendar-save-config-btn",
  );
  if (calendarSaveConfigBtn) {
    calendarSaveConfigBtn.addEventListener("click", () => {
      const daysInput = document.getElementById("calendar-days-input");
      const days = parseInt(daysInput.value) || 7;
      syncCalendar(days);
    });
  }

  // Reminders Integration
  const remindersConnectBtn = document.getElementById("reminders-connect-btn");
  if (remindersConnectBtn) {
    remindersConnectBtn.addEventListener("click", async () => {
      remindersConnectBtn.disabled = true;
      remindersConnectBtn.textContent = "Connecting...";

      try {
        const response = await fetch(
          "http://127.0.0.1:11436/polly/integrations/connect",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              integration: "reminders",
              credentials: {}, // No credentials needed for macOS Reminders
            }),
          },
        );

        const result = await response.json();

        if (result.success) {
          updateIntegrationStatus("reminders", "connected");

          // Show sync and config buttons
          document
            .getElementById("reminders-connect-btn")
            .classList.add("hidden");
          document
            .getElementById("reminders-sync-btn")
            .classList.remove("hidden");
          document
            .getElementById("reminders-config-btn")
            .classList.remove("hidden");

          // Auto-sync
          setTimeout(() => syncReminders(), 500);
        } else {
          alert(
            `Reminders connection failed: ${result.error || "Unknown error"}`,
          );
          updateIntegrationStatus("reminders", "error");
        }
      } catch (error) {
        console.error("Reminders connection error:", error);
        alert("Connection failed. Is the server running?");
      } finally {
        remindersConnectBtn.disabled = false;
        remindersConnectBtn.textContent = "enable";
      }
    });
  }

  // Reminders sync
  const remindersSyncBtn = document.getElementById("reminders-sync-btn");
  if (remindersSyncBtn) {
    remindersSyncBtn.addEventListener("click", () => syncReminders());
  }

  // Reminders config save
  const remindersSaveConfigBtn = document.getElementById(
    "reminders-save-config-btn",
  );
  if (remindersSaveConfigBtn) {
    remindersSaveConfigBtn.addEventListener("click", () => {
      const includeCompleted = document.getElementById(
        "reminders-completed-checkbox",
      ).checked;
      syncReminders(includeCompleted);
    });
  }

  const icalBtn = document.getElementById("ical-connect-btn");
  if (icalBtn) {
    icalBtn.addEventListener("click", () => {
      alert("Calendar account modal will be implemented in Phase 4");
    });
  }

  const macosBtn = document.getElementById("macos-enable-btn");
  if (macosBtn) {
    macosBtn.addEventListener("click", () => {
      alert("macOS permissions will be implemented in Phase 9");
    });
  }

  const regenerateBtn = document.getElementById("btn-regenerate-key");
  if (regenerateBtn) {
    regenerateBtn.addEventListener("click", () => {
      const newKey =
        "polly-local-" + Math.random().toString(36).substring(2, 15);
      document.getElementById("opencode-api-key").value = newKey;
      alert("New API key generated!");
    });
  }
}

// Initialize settings tabs and integrations when settings view is loaded
document.addEventListener("DOMContentLoaded", () => {
  initSettingsTabs();
  initIntegrationConfig();
  initIntegrationPlaceholders();
  initRoutingSettings();
  setupGeneralSettings(); // General settings UI
  setupDedupSettings(); // Phase 21
  setupMigration(); // Phase 16 - Migration UI
  setupCompressionSettings(); // Compression settings UI
  setupMemorySettings(); // Memory provider settings UI
  setupSettingsCrossLinks(); // Cross-navigation between settings pages

  // Ensure all integration config panels start hidden
  document.querySelectorAll(".integration-config").forEach((panel) => {
    if (!panel.classList.contains("hidden")) {
      panel.classList.add("hidden");
    }
  });

  restoreIntegrationStatus();
});

/**
 * Phase 3 - Smart Features Functions
 */

/**
 * Open save conversation modal
 */
function openSaveConversationModal() {
  const messages = getCurrentConversationMessages();

  if (messages.length === 0) {
    alert("No conversation to save. Start chatting first!");
    return;
  }

  // Reset modal
  document.getElementById("note-title").value = "";
  document.getElementById("note-folder").value = "30-Ideas";
  document.getElementById("note-tags-input").value = "";
  document.getElementById("folder-suggestion").classList.add("hidden");
  document.getElementById("suggested-tags").innerHTML = "";
  document.getElementById("selected-tags").innerHTML = "";
  document.getElementById("save-modal-status").classList.add("hidden");

  // Generate title from first user message
  const firstUserMsg = messages.find((m) => m.role === "user");
  if (firstUserMsg) {
    const title = firstUserMsg.content.substring(0, 60);
    document.getElementById("note-title").placeholder =
      title + (firstUserMsg.content.length > 60 ? "..." : "");
  }

  // Show modal
  document.getElementById("save-conversation-modal").classList.remove("hidden");

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }
}

/**
 * Close save conversation modal
 */
function closeSaveConversationModal() {
  document.getElementById("save-conversation-modal").classList.add("hidden");
}

/**
 * Suggest folder for note
 */
async function suggestFolder() {
  const title =
    document.getElementById("note-title").value ||
    document.getElementById("note-title").placeholder;
  const statusEl = document.getElementById("save-modal-status");

  // Show loading
  statusEl.textContent = "Getting folder suggestion...";
  statusEl.className = "status-message loading";
  statusEl.classList.remove("hidden");

  try {
    // Combine conversation for analysis
    const messages = getCurrentConversationMessages();
    const content = messages.map((m) => m.content).join("\n\n");

    const response = await fetch(
      `http://127.0.0.1:11436/polly/obsidian/suggest-folder?title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}`,
    );

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const result = await response.json();

    // Show suggestion
    document.getElementById("suggested-folder-name").textContent =
      result.suggested_folder;
    document.getElementById("suggested-folder-domain").textContent =
      `(${result.domain}, ${Math.round(result.confidence * 100)}% confidence)`;
    document.getElementById("folder-reasoning").textContent = result.reasoning;
    document.getElementById("folder-suggestion").classList.remove("hidden");

    statusEl.classList.add("hidden");

    // Re-initialize icons
    if (typeof lucide !== "undefined") {
      setTimeout(() => lucide.createIcons(), 0);
    }
  } catch (error) {
    console.error("Error suggesting folder:", error);
    statusEl.textContent = `Error: ${error.message}`;
    statusEl.className = "status-message error";
  }
}

/**
 * Suggest tags for note
 */
async function suggestTags() {
  const title =
    document.getElementById("note-title").value ||
    document.getElementById("note-title").placeholder;
  const statusEl = document.getElementById("save-modal-status");

  // Show loading
  statusEl.textContent = "Getting tag suggestions...";
  statusEl.className = "status-message loading";
  statusEl.classList.remove("hidden");

  try {
    // Combine conversation for analysis
    const messages = getCurrentConversationMessages();
    const content = messages.map((m) => m.content).join("\n\n");

    const response = await fetch(
      `http://127.0.0.1:11436/polly/obsidian/suggest-tags?title=${encodeURIComponent(title)}&content=${encodeURIComponent(content)}`,
    );

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const result = await response.json();

    // Display suggested tags
    const suggestedTagsContainer = document.getElementById("suggested-tags");
    suggestedTagsContainer.innerHTML = "";

    result.suggested_tags.forEach((tagInfo) => {
      const chip = document.createElement("span");
      chip.className = "tag-chip suggested";
      chip.innerHTML = `
        ${tagInfo.tag}
        <span class="tag-confidence">${Math.round(tagInfo.confidence * 100)}%</span>
      `;
      chip.addEventListener("click", () => addTagToSelection(tagInfo.tag));
      suggestedTagsContainer.appendChild(chip);
    });

    statusEl.classList.add("hidden");
  } catch (error) {
    console.error("Error suggesting tags:", error);
    statusEl.textContent = `Error: ${error.message}`;
    statusEl.className = "status-message error";
  }
}

/**
 * Add tag to selection
 */
function addTagToSelection(tag) {
  const selectedTagsContainer = document.getElementById("selected-tags");

  // Check if already added
  const existingTags = Array.from(
    selectedTagsContainer.querySelectorAll(".tag-chip"),
  ).map((el) => el.dataset.tag);
  if (existingTags.includes(tag)) {
    return;
  }

  const chip = document.createElement("span");
  chip.className = "tag-chip selected";
  chip.dataset.tag = tag;
  chip.innerHTML = `
    ${tag}
    <span class="tag-remove">×</span>
  `;

  chip.querySelector(".tag-remove").addEventListener("click", () => {
    chip.remove();
  });

  selectedTagsContainer.appendChild(chip);
}

/**
 * Save conversation to Obsidian
 */
async function saveConversationToObsidian() {
  const title =
    document.getElementById("note-title").value ||
    document.getElementById("note-title").placeholder;
  const folder = document.getElementById("note-folder").value || "30-Ideas";
  const statusEl = document.getElementById("save-modal-status");

  // Get selected tags
  const selectedTags = Array.from(
    document.getElementById("selected-tags").querySelectorAll(".tag-chip"),
  ).map((el) => el.dataset.tag);

  // Show loading
  statusEl.textContent = "Creating note...";
  statusEl.className = "status-message loading";
  statusEl.classList.remove("hidden");

  document.getElementById("btn-confirm-save").disabled = true;

  try {
    const messages = getCurrentConversationMessages();
    const response = await fetch(
      "http://127.0.0.1:11436/polly/obsidian/from-conversation",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: messages,
          title: title,
          folder: folder,
          confirmed: true,
        }),
      },
    );

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const result = await response.json();

    if (result.status === "created") {
      // Success!
      statusEl.textContent = `✓ Note created: ${result.path}`;
      statusEl.className = "status-message success";

      // Close modal after 1.5 seconds
      setTimeout(() => {
        closeSaveConversationModal();
      }, 1500);
    } else {
      throw new Error("Note creation failed");
    }
  } catch (error) {
    console.error("Error saving conversation:", error);
    statusEl.textContent = `Error: ${error.message}`;
    statusEl.className = "status-message error";
  } finally {
    document.getElementById("btn-confirm-save").disabled = false;
  }
}

/**
 * Toggle related notes sidebar
 */
/**
 * Toggle related notes sidebar (legacy - removed in new UI)
 */
function toggleRelatedNotes() {
  // Related notes panel removed in new UI redesign
  // Will be reimplemented in a future update
  console.log("Related notes feature temporarily disabled during UI redesign");
}

/**
 * Close related notes sidebar (legacy - removed in new UI)
 */
function closeRelatedNotes() {
  // Related notes panel removed in new UI redesign
  // No-op for backward compatibility
}

/**
 * Update related notes based on current conversation
 */
async function updateRelatedNotes() {
  const statusEl = document.getElementById("related-notes-status");
  const listEl = document.getElementById("related-notes-list");

  const messages = getCurrentConversationMessages();

  if (messages.length === 0) {
    statusEl.innerHTML = `
      <div style="text-align: center; padding: 20px; color: var(--text-secondary); font-size: 13px;">
        <i data-lucide="info" style="width: 20px; height: 20px; margin-bottom: 8px;"></i>
        <p>Start chatting to see related notes from your vault</p>
      </div>
    `;
    listEl.innerHTML = "";
    if (typeof lucide !== "undefined") {
      setTimeout(() => lucide.createIcons(), 0);
    }
    return;
  }

  // Show loading
  statusEl.innerHTML = `
    <div style="text-align: center; padding: 12px; color: var(--text-secondary); font-size: 12px;">
      <div class="loading-spinner" style="margin: 0 auto 8px;"></div>
      Finding related notes...
    </div>
  `;
  listEl.innerHTML = "";

  try {
    // Combine recent conversation for context
    const recentMessages = messages.slice(-5); // Last 5 messages
    const content = recentMessages.map((m) => m.content).join("\n\n");

    const response = await fetch(
      `http://127.0.0.1:11436/polly/obsidian/find-related?content=${encodeURIComponent(content)}&limit=8`,
    );

    if (!response.ok) {
      throw new Error(`Server returned ${response.status}`);
    }

    const result = await response.json();

    if (result.related_notes && result.related_notes.length > 0) {
      statusEl.innerHTML = `
        <div style="padding: 8px; color: var(--text-secondary); font-size: 12px;">
          Found ${result.related_notes.length} related notes
        </div>
      `;

      // Display notes
      listEl.innerHTML = "";
      result.related_notes.forEach((note) => {
        const noteEl = createRelatedNoteElement(note);
        listEl.appendChild(noteEl);
      });
    } else {
      statusEl.innerHTML = `
        <div style="text-align: center; padding: 20px; color: var(--text-secondary); font-size: 13px;">
          <i data-lucide="search-x" style="width: 20px; height: 20px; margin-bottom: 8px;"></i>
          <p>No related notes found</p>
        </div>
      `;
      listEl.innerHTML = "";
    }

    // Re-initialize icons
    if (typeof lucide !== "undefined") {
      setTimeout(() => lucide.createIcons(), 0);
    }
  } catch (error) {
    console.error("Error finding related notes:", error);
    statusEl.innerHTML = `
      <div style="text-align: center; padding: 20px; color: var(--error); font-size: 13px;">
        <i data-lucide="alert-circle" style="width: 20px; height: 20px; margin-bottom: 8px;"></i>
        <p>Error: ${error.message}</p>
      </div>
    `;
    listEl.innerHTML = "";

    if (typeof lucide !== "undefined") {
      setTimeout(() => lucide.createIcons(), 0);
    }
  }
}

/**
 * Create related note element
 */
function createRelatedNoteElement(note) {
  const div = document.createElement("div");
  div.className = "related-note-item";

  const similarityPercent = Math.round(note.similarity * 100);
  let similarityClass = "";
  if (note.similarity >= 0.8) similarityClass = "high";
  else if (note.similarity >= 0.7) similarityClass = "medium";

  const concepts = note.connections?.shared_concepts || [];
  const conceptsHtml =
    concepts.length > 0
      ? concepts
          .slice(0, 3)
          .map((c) => `<span>${c}</span>`)
          .join("")
      : "";

  div.innerHTML = `
    <div class="related-note-title">${note.title}</div>
    <div class="related-note-path">${note.path}</div>
    <div class="related-note-similarity ${similarityClass}">${similarityPercent}% similar</div>
    ${conceptsHtml ? `<div class="related-note-concepts">${conceptsHtml}</div>` : ""}
  `;

  // Add click handler to open note in Obsidian
  div.addEventListener("click", () => {
    openNoteInObsidian(note.path);
  });

  return div;
}

/**
 * Open note in Obsidian
 */
async function openNoteInObsidian(notePath) {
  try {
    // Use Obsidian URI protocol
    const vaultPath = await window.polly.getStore("vaultPath");
    if (!vaultPath) {
      alert("Obsidian vault not configured");
      return;
    }

    // Extract vault name from path
    const vaultName = vaultPath.split("/").pop();

    // Encode the path
    const encodedPath = encodeURIComponent(notePath);

    // Construct Obsidian URI
    const uri = `obsidian://open?vault=${encodeURIComponent(vaultName)}&file=${encodedPath}`;

    // Open in default browser (which will trigger Obsidian)
    window.open(uri, "_blank");
  } catch (error) {
    console.error("Error opening note:", error);
    alert(`Could not open note: ${error.message}`);
  }
}

// ============================================
// Mental Models (Phase 14)
// ============================================

// Mental model templates
const MENTAL_MODEL_TEMPLATES = {
  learning: {
    name: "Learning Framework",
    description: "A framework for learning and teaching",
    principles: ["Learn by doing", "Question assumptions", "Teach to learn"],
    prompt_injection: "Guide learning through questions and examples.",
    applies_to: ["scrolls"],
    active_on_pages: ["learning"],
    keywords: ["learn", "teach", "understand"],
  },
  creative: {
    name: "Creative Process",
    description: "A model for creative work and ideation",
    principles: [
      "Diverge before converging",
      "Embrace constraints",
      "Iterate rapidly",
    ],
    prompt_injection: "Encourage exploration and multiple perspectives.",
    applies_to: ["glyphs", "scrolls"],
    active_on_pages: ["notes", "projects"],
    keywords: ["create", "design", "ideate", "brainstorm"],
  },
  productivity: {
    name: "Productivity System",
    description: "A model for effective task management",
    principles: [
      "Prioritize ruthlessly",
      "Time-box work",
      "Minimize context switching",
    ],
    prompt_injection: "Help organize tasks and manage time effectively.",
    applies_to: ["grids"],
    active_on_pages: ["projects", "calendar"],
    keywords: ["productivity", "tasks", "organize", "schedule"],
  },
  systems: {
    name: "Systems Approach",
    description: "A model for thinking about complex systems",
    principles: [
      "Everything is connected",
      "Feedback loops matter",
      "Emergence is key",
    ],
    prompt_injection:
      "Consider second-order effects and systemic implications.",
    applies_to: ["grids", "sigils"],
    active_on_pages: ["code", "projects"],
    keywords: ["system", "architecture", "design", "complexity"],
  },
  communication: {
    name: "Communication Style",
    description: "A model for effective communication",
    principles: [
      "Clarity over cleverness",
      "Context is king",
      "Listen actively",
    ],
    prompt_injection: "Communicate with clarity and empathy.",
    applies_to: ["scrolls"],
    active_on_pages: ["mail", "notes"],
    keywords: ["communicate", "write", "explain", "clarify"],
  },
};

let mentalModels = [];
let editingModelId = null;

/**
 * Load mental models from server
 */
async function loadMentalModels() {
  const listContainer = document.getElementById("mental-models-list");
  const countEl = document.querySelector(".mental-models-count");

  try {
    // Show loading state
    listContainer.innerHTML =
      '<div class="mental-models-loading">Loading mental models...</div>';

    // Fetch from API
    const response = await fetch(
      "http://127.0.0.1:11436/polly/mental-models/list",
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    mentalModels = data.models || [];

    // Update count
    const enabledCount = mentalModels.filter((m) => m.enabled).length;
    countEl.textContent = `${mentalModels.length} models (${enabledCount} enabled)`;

    // Render models
    if (mentalModels.length === 0) {
      listContainer.innerHTML = `
        <div class="mental-models-empty">
          <h3>No Mental Models</h3>
          <p>Click "Add Model" to create your first mental model</p>
        </div>
      `;
    } else {
      listContainer.innerHTML = mentalModels
        .map(renderMentalModelCard)
        .join("");

      // Attach event listeners
      mentalModels.forEach((model) => {
        // Toggle
        const toggleEl = document.getElementById(
          `mental-model-toggle-${model.id}`,
        );
        if (toggleEl) {
          toggleEl.addEventListener("click", () => toggleMentalModel(model.id));
        }

        // Edit
        const editBtn = document.getElementById(
          `mental-model-edit-${model.id}`,
        );
        if (editBtn) {
          editBtn.addEventListener("click", () =>
            openMentalModelModal(model.id),
          );
        }

        // Delete
        const deleteBtn = document.getElementById(
          `mental-model-delete-${model.id}`,
        );
        if (deleteBtn) {
          deleteBtn.addEventListener("click", () =>
            deleteMentalModel(model.id),
          );
        }
      });
    }
  } catch (error) {
    console.error("Error loading mental models:", error);
    listContainer.innerHTML = `
      <div class="mental-models-empty">
        <h3>Error Loading Models</h3>
        <p>${error.message}</p>
      </div>
    `;
  }
}

/**
 * Render a mental model card
 */
function renderMentalModelCard(model) {
  const tags = [];

  // Add domain tags
  if (model.applies_to && model.applies_to.length > 0) {
    model.applies_to.forEach((domain) => {
      tags.push(`<span class="mental-model-tag domain">${domain}</span>`);
    });
  }

  // Add page tags (limit to 3)
  if (model.active_on_pages && model.active_on_pages.length > 0) {
    const pagesToShow = model.active_on_pages.slice(0, 3);
    pagesToShow.forEach((page) => {
      tags.push(`<span class="mental-model-tag page">${page}</span>`);
    });
    if (model.active_on_pages.length > 3) {
      tags.push(
        `<span class="mental-model-tag page">+${model.active_on_pages.length - 3}</span>`,
      );
    }
  }

  // Add persona tags
  if (model.active_for_personas && model.active_for_personas.length > 0) {
    model.active_for_personas.forEach((persona) => {
      tags.push(`<span class="mental-model-tag persona">${persona}</span>`);
    });
  }

  // Add mode tags
  if (model.active_for_modes && model.active_for_modes.length > 0) {
    model.active_for_modes.forEach((mode) => {
      tags.push(`<span class="mental-model-tag mode">${mode}</span>`);
    });
  }

  return `
    <div class="mental-model-card ${!model.enabled ? "disabled" : ""}">
      <div class="mental-model-card-header">
        <div>
          <div class="mental-model-card-title">${model.name}</div>
          <div class="mental-model-card-id">${model.id}</div>
        </div>
        <div 
          id="mental-model-toggle-${model.id}"
          class="mental-model-toggle ${model.enabled ? "active" : ""}"
          title="${model.enabled ? "Disable" : "Enable"}"
        ></div>
      </div>
      <div class="mental-model-card-description">${model.description}</div>
      ${tags.length > 0 ? `<div class="mental-model-card-tags">${tags.join("")}</div>` : ""}
      <div class="mental-model-card-actions">
        <button id="mental-model-edit-${model.id}">
          <i data-lucide="edit-2" style="width: 14px; height: 14px;"></i>
          Edit
        </button>
        <button id="mental-model-delete-${model.id}" class="danger">
          <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
          Delete
        </button>
      </div>
    </div>
  `;
}

/**
 * Open mental model modal for add/edit
 */
function openMentalModelModal(modelId = null) {
  const modal = document.getElementById("mental-model-modal");
  const title = document.getElementById("mental-model-modal-title");
  const templateSelect = document.getElementById("mental-model-template");

  editingModelId = modelId;

  if (modelId) {
    // Edit mode
    title.textContent = "Edit Mental Model";
    templateSelect.style.display = "none";

    const model = mentalModels.find((m) => m.id === modelId);
    if (model) {
      populateModalFromModel(model);
    }
  } else {
    // Add mode
    title.textContent = "Add Mental Model";
    templateSelect.style.display = "block";
    clearModalForm();
  }

  modal.classList.remove("hidden");
  lucide.createIcons();
}

/**
 * Close mental model modal
 */
function closeMentalModelModal() {
  document.getElementById("mental-model-modal").classList.add("hidden");
  editingModelId = null;
  clearModalForm();
}

/**
 * Clear modal form
 */
function clearModalForm() {
  document.getElementById("mental-model-template").value = "";
  document.getElementById("mental-model-id").value = "";
  document.getElementById("mental-model-name").value = "";
  document.getElementById("mental-model-description").value = "";
  document.getElementById("mental-model-principles").value = "";
  document.getElementById("mental-model-prompt").value = "";
  document.getElementById("mental-model-keywords").value = "";
  document.getElementById("mental-model-enabled").checked = true;

  // Clear all checkboxes
  document
    .querySelectorAll(".domain-checkbox")
    .forEach((cb) => (cb.checked = false));
  document
    .querySelectorAll(".page-checkbox")
    .forEach((cb) => (cb.checked = false));
  document
    .querySelectorAll(".persona-checkbox")
    .forEach((cb) => (cb.checked = false));
  document
    .querySelectorAll(".mode-checkbox")
    .forEach((cb) => (cb.checked = false));

  // Enable ID field for new models
  document.getElementById("mental-model-id").disabled = false;
}

/**
 * Populate modal from model data
 */
function populateModalFromModel(model) {
  document.getElementById("mental-model-id").value = model.id;
  document.getElementById("mental-model-id").disabled = true; // Can't change ID
  document.getElementById("mental-model-name").value = model.name;
  document.getElementById("mental-model-description").value = model.description;
  document.getElementById("mental-model-principles").value =
    model.principles.join("\n");
  document.getElementById("mental-model-prompt").value = model.prompt_injection;
  document.getElementById("mental-model-keywords").value = (
    model.keywords || []
  ).join(", ");
  document.getElementById("mental-model-enabled").checked = model.enabled;

  // Set checkboxes
  document.querySelectorAll(".domain-checkbox").forEach((cb) => {
    cb.checked = model.applies_to && model.applies_to.includes(cb.value);
  });

  document.querySelectorAll(".page-checkbox").forEach((cb) => {
    cb.checked =
      model.active_on_pages && model.active_on_pages.includes(cb.value);
  });

  document.querySelectorAll(".persona-checkbox").forEach((cb) => {
    cb.checked =
      model.active_for_personas && model.active_for_personas.includes(cb.value);
  });

  document.querySelectorAll(".mode-checkbox").forEach((cb) => {
    cb.checked =
      model.active_for_modes && model.active_for_modes.includes(cb.value);
  });
}

/**
 * Apply template to modal form
 */
function applyMentalModelTemplate(templateId) {
  const template = MENTAL_MODEL_TEMPLATES[templateId];
  if (!template) return;

  document.getElementById("mental-model-name").value = template.name;
  document.getElementById("mental-model-description").value =
    template.description;
  document.getElementById("mental-model-principles").value =
    template.principles.join("\n");
  document.getElementById("mental-model-prompt").value =
    template.prompt_injection;
  document.getElementById("mental-model-keywords").value =
    template.keywords.join(", ");

  // Set checkboxes
  document.querySelectorAll(".domain-checkbox").forEach((cb) => {
    cb.checked = template.applies_to && template.applies_to.includes(cb.value);
  });

  document.querySelectorAll(".page-checkbox").forEach((cb) => {
    cb.checked =
      template.active_on_pages && template.active_on_pages.includes(cb.value);
  });

  // Generate ID from name
  const id = template.name.toLowerCase().replace(/[^a-z0-9]+/g, "_");
  document.getElementById("mental-model-id").value = id;
}

/**
 * Save mental model (create or update)
 */
async function saveMentalModel() {
  try {
    // Gather form data
    const id = document.getElementById("mental-model-id").value.trim();
    const name = document.getElementById("mental-model-name").value.trim();
    const description = document
      .getElementById("mental-model-description")
      .value.trim();
    const principlesText = document
      .getElementById("mental-model-principles")
      .value.trim();
    const promptInjection = document
      .getElementById("mental-model-prompt")
      .value.trim();
    const keywordsText = document
      .getElementById("mental-model-keywords")
      .value.trim();
    const enabled = document.getElementById("mental-model-enabled").checked;

    // Validation
    if (!id) {
      alert("ID is required");
      return;
    }

    if (!/^[a-z0-9_]+$/.test(id)) {
      alert("ID must be lowercase letters, numbers, and underscores only");
      return;
    }

    if (!name) {
      alert("Name is required");
      return;
    }

    if (!description) {
      alert("Description is required");
      return;
    }

    if (!principlesText) {
      alert("Principles are required");
      return;
    }

    if (!promptInjection) {
      alert("Prompt injection is required");
      return;
    }

    // Parse arrays
    const principles = principlesText
      .split("\n")
      .filter((p) => p.trim())
      .map((p) => p.trim());
    const keywords = keywordsText
      ? keywordsText
          .split(",")
          .map((k) => k.trim())
          .filter((k) => k)
      : [];

    // Gather checkboxes
    const applies_to = Array.from(
      document.querySelectorAll(".domain-checkbox:checked"),
    ).map((cb) => cb.value);
    const active_on_pages = Array.from(
      document.querySelectorAll(".page-checkbox:checked"),
    ).map((cb) => cb.value);
    const active_for_personas = Array.from(
      document.querySelectorAll(".persona-checkbox:checked"),
    ).map((cb) => cb.value);
    const active_for_modes = Array.from(
      document.querySelectorAll(".mode-checkbox:checked"),
    ).map((cb) => cb.value);

    // Build payload
    const payload = {
      id,
      name,
      description,
      principles,
      prompt_injection: promptInjection,
      applies_to,
      active_on_pages,
      active_for_personas,
      active_for_modes,
      keywords,
      enabled,
    };

    // Determine API endpoint
    let url, method;
    if (editingModelId) {
      // Update existing
      url = `http://127.0.0.1:11436/polly/mental-models/${editingModelId}`;
      method = "PUT";
    } else {
      // Create new
      url = "http://127.0.0.1:11436/polly/mental-models/create";
      method = "POST";
    }

    // Send request
    const response = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    // Success
    closeMentalModelModal();
    await loadMentalModels();
  } catch (error) {
    console.error("Error saving mental model:", error);
    alert(`Failed to save mental model: ${error.message}`);
  }
}

/**
 * Toggle mental model enabled/disabled
 */
async function toggleMentalModel(modelId) {
  try {
    const response = await fetch(
      `http://127.0.0.1:11436/polly/mental-models/${modelId}/toggle`,
      {
        method: "POST",
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // Reload models
    await loadMentalModels();
  } catch (error) {
    console.error("Error toggling mental model:", error);
    alert(`Failed to toggle mental model: ${error.message}`);
  }
}

/**
 * Delete mental model
 */
async function deleteMentalModel(modelId) {
  const model = mentalModels.find((m) => m.id === modelId);
  if (!model) return;

  if (
    !confirm(`Delete mental model "${model.name}"?\n\nThis cannot be undone.`)
  ) {
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:11436/polly/mental-models/${modelId}`,
      {
        method: "DELETE",
      },
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // Reload models
    await loadMentalModels();
  } catch (error) {
    console.error("Error deleting mental model:", error);
    alert(`Failed to delete mental model: ${error.message}`);
  }
}

/**
 * Global Default Mental Models
 * Stored in localStorage — applies to all conversations that don't have
 * a per-conversation override.
 */
const MM_GLOBAL_DEFAULTS_KEY = "mm_global_defaults";

/**
 * Get global default models preference.
 * @returns {{ enabled: boolean, modelIds: string[] } | null}
 */
function getGlobalDefaultModels() {
  const stored = localStorage.getItem(MM_GLOBAL_DEFAULTS_KEY);
  if (!stored) return null;
  try {
    return JSON.parse(stored);
  } catch (error) {
    console.error("Failed to parse global default models:", error);
    return null;
  }
}

/**
 * Set global default models preference.
 * @param {{ enabled: boolean, modelIds: string[] } | null} defaults
 */
function setGlobalDefaultModels(defaults) {
  if (defaults === null) {
    localStorage.removeItem(MM_GLOBAL_DEFAULTS_KEY);
  } else {
    localStorage.setItem(MM_GLOBAL_DEFAULTS_KEY, JSON.stringify(defaults));
  }
}

/**
 * Mental Models Override for specific conversations
 * Stored in localStorage keyed by conversation ID
 */

let currentOverrideConversationId = null;

/**
 * Get mental models override for a conversation
 */
function getMentalModelsOverride(conversationId) {
  const key = `mm_override_${conversationId}`;
  const stored = localStorage.getItem(key);
  if (!stored) return null;

  try {
    return JSON.parse(stored);
  } catch (error) {
    console.error("Failed to parse mental models override:", error);
    return null;
  }
}

/**
 * Set mental models override for a conversation
 */
function setMentalModelsOverride(conversationId, override) {
  const key = `mm_override_${conversationId}`;
  if (override === null) {
    localStorage.removeItem(key);
  } else {
    localStorage.setItem(key, JSON.stringify(override));
  }
}

/**
 * Refresh mental models stats display (Phase 16f)
 */
async function refreshMentalModelsStats() {
  try {
    // Load all models
    const response = await fetch(
      "http://127.0.0.1:11436/polly/mental-models/list",
    );
    if (!response.ok) throw new Error("Failed to fetch models");

    const data = await response.json();
    const models = data.models || [];

    // Load active models for current context
    const activeResponse = await fetch(
      "http://127.0.0.1:11436/polly/mental-models/active",
    );
    const activeData = await activeResponse.json();
    const activeModels = activeData.active_models || [];

    // Update stats display
    const totalCount = models.length;
    const enabledCount = models.filter((m) => m.enabled).length;
    const activeCount = activeModels.length;

    // Update DOM elements
    const totalEl = document.getElementById("mental-models-count-display");
    const enabledEl = document.getElementById("mental-models-enabled-display");
    const activeEl = document.getElementById("mental-models-active-display");

    if (totalEl) totalEl.textContent = totalCount;
    if (enabledEl) enabledEl.textContent = enabledCount;
    if (activeEl) activeEl.textContent = activeCount;

    console.log(
      `[Mental Models Stats] Total: ${totalCount}, Enabled: ${enabledCount}, Active: ${activeCount}`,
    );
  } catch (error) {
    console.error("Error refreshing mental models stats:", error);
  }
}

/**
 * Toggle the override modal between defaults-active and manual-selection states.
 */
function _updateOverrideDefaultsState(useDefaults) {
  const modelsList = document.getElementById("override-models-list");
  const infoEl = document.getElementById("override-defaults-info");
  if (useDefaults) {
    modelsList.classList.add("defaults-active");
    if (infoEl) infoEl.style.display = "";
  } else {
    modelsList.classList.remove("defaults-active");
    if (infoEl) infoEl.style.display = "none";
  }
}

/**
 * Open mental models override modal
 */
async function openMentalModelsOverrideModal(conversationId) {
  currentOverrideConversationId = conversationId;

  const modal = document.getElementById("mental-models-override-modal");
  const useDefaultsCheckbox = document.getElementById("override-use-defaults");
  const modelsList = document.getElementById("override-models-list");
  const loading = document.getElementById("override-loading");

  // Show modal
  modal.classList.remove("hidden");

  // Show loading
  loading.style.display = "flex";
  modelsList.innerHTML = "";

  try {
    // Fetch all mental models
    const response = await fetch(
      "http://127.0.0.1:11436/polly/mental-models/list",
    );
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const allModels = data.models || [];

    // Get current override
    const override = getMentalModelsOverride(conversationId);

    // Set checkbox state and toggle defaults-active / manual UI
    if (override && override.useDefaults === false) {
      useDefaultsCheckbox.checked = false;
      _updateOverrideDefaultsState(false);
    } else {
      useDefaultsCheckbox.checked = true;
      _updateOverrideDefaultsState(true);
    }

    // Render models list
    modelsList.innerHTML = allModels
      .map((model) => {
        const isChecked =
          override && override.modelIds
            ? override.modelIds.includes(model.id)
            : model.enabled;

        return `
        <div class="override-model-item" data-model-id="${model.id}">
          <div class="override-model-info">
            <div class="override-model-name">${model.name}</div>
            <div class="override-model-desc">${model.description}</div>
          </div>
          <input 
            type="checkbox" 
            class="override-model-checkbox" 
            data-model-id="${model.id}"
            ${isChecked ? "checked" : ""}
          >
        </div>
      `;
      })
      .join("");

    // Hide loading
    loading.style.display = "none";

    // Make entire model row clickable — toggle its checkbox
    modelsList.querySelectorAll(".override-model-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        // Don't double-toggle when the checkbox itself is clicked
        if (e.target.classList.contains("override-model-checkbox")) return;
        const cb = item.querySelector(".override-model-checkbox");
        if (cb) cb.checked = !cb.checked;
      });
    });

    // Setup use defaults checkbox handler
    useDefaultsCheckbox.onchange = () => {
      _updateOverrideDefaultsState(useDefaultsCheckbox.checked);
    };
  } catch (error) {
    console.error("Error loading mental models:", error);
    loading.innerHTML = `<div style="color: var(--danger);">Failed to load mental models: ${error.message}</div>`;
  }
}

/**
 * Close mental models override modal
 */
function closeMentalModelsOverrideModal() {
  document
    .getElementById("mental-models-override-modal")
    .classList.add("hidden");
  currentOverrideConversationId = null;
}

/**
 * Save mental models override
 */
function saveMentalModelsOverride() {
  if (!currentOverrideConversationId) return;

  const useDefaultsCheckbox = document.getElementById("override-use-defaults");
  const checkboxes = document.querySelectorAll(".override-model-checkbox");

  if (useDefaultsCheckbox.checked) {
    // Remove override (use defaults)
    setMentalModelsOverride(currentOverrideConversationId, null);
  } else {
    // Save override
    const selectedModelIds = Array.from(checkboxes)
      .filter((cb) => cb.checked)
      .map((cb) => cb.dataset.modelId);

    setMentalModelsOverride(currentOverrideConversationId, {
      useDefaults: false,
      modelIds: selectedModelIds,
    });
  }

  // Close modal
  closeMentalModelsOverrideModal();

  // Refresh conversation list to show indicator
  renderConversationsList();
}

// ============================================
// Global Default Mental Models Picker
// ============================================

/**
 * Load and render the global defaults picker in the Mental Models settings tab.
 * Called once when the settings view is first shown and on subsequent tab switches.
 */
async function loadGlobalDefaultsPicker() {
  const listEl = document.getElementById("global-defaults-models-list");
  const enabledCb = document.getElementById("global-defaults-enabled");
  const saveBtn = document.getElementById("btn-save-global-defaults");
  const clearBtn = document.getElementById("btn-clear-global-defaults");

  if (!listEl || !enabledCb) return;

  // Fetch models
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/mental-models/list");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    const models = data.models || [];

    // Load stored defaults
    const defaults = getGlobalDefaultModels();
    const isEnabled = defaults && defaults.enabled;
    const selectedIds = (defaults && defaults.modelIds) || [];

    enabledCb.checked = !!isEnabled;
    listEl.style.display = isEnabled ? "" : "none";
    if (saveBtn) saveBtn.style.display = isEnabled ? "" : "none";
    if (clearBtn) clearBtn.style.display = isEnabled ? "" : "none";

    // Render model list with checkboxes
    listEl.innerHTML = models
      .map((model) => {
        const isChecked = selectedIds.includes(model.id);
        return `
          <div class="override-model-item" data-model-id="${model.id}" style="margin-bottom: 6px;">
            <div class="override-model-info">
              <div class="override-model-name">${model.name}</div>
              <div class="override-model-desc">${model.description}</div>
            </div>
            <input
              type="checkbox"
              class="global-default-model-checkbox override-model-checkbox"
              data-model-id="${model.id}"
              ${isChecked ? "checked" : ""}
            >
          </div>
        `;
      })
      .join("");

    // Row click toggles checkbox
    listEl.querySelectorAll(".override-model-item").forEach((item) => {
      item.addEventListener("click", (e) => {
        if (e.target.tagName === "INPUT") return;
        const cb = item.querySelector(".global-default-model-checkbox");
        if (cb) cb.checked = !cb.checked;
      });
    });

    // Toggle visibility when enabled checkbox changes
    enabledCb.onchange = () => {
      const show = enabledCb.checked;
      listEl.style.display = show ? "" : "none";
      if (saveBtn) saveBtn.style.display = show ? "" : "none";
      if (clearBtn) clearBtn.style.display = show ? "" : "none";
      if (!show) {
        // Disable global defaults when unchecked
        setGlobalDefaultModels(null);
        console.log("[Global Defaults] Disabled global default models");
      }
    };

    // Save button
    if (saveBtn) {
      saveBtn.onclick = () => {
        const selectedModelIds = Array.from(
          listEl.querySelectorAll(".global-default-model-checkbox:checked"),
        ).map((cb) => cb.dataset.modelId);

        setGlobalDefaultModels({
          enabled: true,
          modelIds: selectedModelIds,
        });
        console.log(`[Global Defaults] Saved ${selectedModelIds.length} default models`);
        alert(`Saved ${selectedModelIds.length} global default model(s).`);
      };
    }

    // Clear button
    if (clearBtn) {
      clearBtn.onclick = () => {
        listEl.querySelectorAll(".global-default-model-checkbox").forEach((cb) => {
          cb.checked = false;
        });
      };
    }
  } catch (error) {
    console.error("Error loading global defaults picker:", error);
    listEl.innerHTML = `<p style="color: var(--danger); padding: 12px;">Failed to load models: ${error.message}</p>`;
  }
}

// ============================================
// Domain Configuration (Phase 1.5)
// ============================================

let domainsConfig = null;
let editingDomainId = null;
let selectedIcon = "folder";
let selectedColor = "#808080";
let domainKeywords = [];

/**
 * Load domains configuration from server
 */
async function loadDomainsConfig() {
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/domains/config");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    domainsConfig = await response.json();
    renderDomainsList();
    updateFolderNumberingToggle();

    console.log("Loaded domains config:", domainsConfig);
  } catch (error) {
    console.error("Failed to load domains config:", error);
    showDomainsError(
      "Failed to load domains. Make sure the server is running.",
    );
  }
}

/**
 * Render the domains list
 */
function renderDomainsList() {
  const listContainer = document.getElementById("domains-list");
  const countElement = document.querySelector(".domain-count");

  if (!domainsConfig || !domainsConfig.domains) {
    listContainer.innerHTML =
      '<div class="loading-spinner">No domains found</div>';
    return;
  }

  // Update count
  countElement.textContent = `${domainsConfig.domains.length} domains`;

  // Sort by order
  const sortedDomains = [...domainsConfig.domains].sort(
    (a, b) => a.order - b.order,
  );

  // Render cards
  listContainer.innerHTML = sortedDomains
    .map(
      (domain) => `
    <div class="domain-card-item" data-domain-id="${domain.id}" draggable="true">
      <div class="domain-card-header">
        <div class="domain-card-title">
          <span class="domain-drag-handle">⋮⋮</span>
          <span class="domain-icon"><i data-lucide="${domain.icon}" style="width: 20px; height: 20px;"></i></span>
          <span class="domain-name">${domain.name}</span>
        </div>
        <div class="domain-card-actions">
          <button class="btn btn-secondary btn-sm" onclick="editDomain('${domain.id}')">
            <i data-lucide="edit" style="width: 12px; height: 12px;"></i>
          </button>
          <button class="btn btn-secondary btn-sm" onclick="deleteDomain('${domain.id}')">
            <i data-lucide="trash-2" style="width: 12px; height: 12px;"></i>
          </button>
        </div>
      </div>
      
      <div class="domain-description">${domain.description || "No description"}</div>
      
      <div class="domain-metadata">
        <div class="domain-metadata-item">
          <span class="domain-color-dot" style="background: ${domain.color};"></span>
          <span>${domain.color}</span>
        </div>
        <div class="domain-metadata-item">
          <span>${domain.folderPath}</span>
        </div>
        <div class="domain-metadata-item">
          <span class="domain-weight-bar">
            ${generateWeightDots(domain.ragWeight)}
          </span>
          <span>${Math.round(domain.ragWeight * 100)}%</span>
        </div>
      </div>
      
      <div class="domain-keywords-preview">
        ${domain.autoTagRules
          .slice(0, 3)
          .map((kw) => `<span>${kw}</span>`)
          .join("")}
        ${domain.autoTagRules.length > 3 ? `<span>+${domain.autoTagRules.length - 3} more</span>` : ""}
      </div>
    </div>
  `,
    )
    .join("");

  // Re-initialize Lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Setup drag and drop
  setupDragAndDrop();
}

/**
 * Generate weight dots visualization
 */
function generateWeightDots(weight) {
  const totalDots = 5;
  const filledDots = Math.round(weight * totalDots);
  let html = "";

  for (let i = 0; i < totalDots; i++) {
    html += `<span class="domain-weight-dot ${i < filledDots ? "filled" : ""}"></span>`;
  }

  return html;
}

/**
 * Update folder numbering toggle
 */
function updateFolderNumberingToggle() {
  const toggle = document.getElementById("folder-numbering-toggle");
  if (toggle && domainsConfig) {
    toggle.checked = domainsConfig.folderNumbering;
  }
}

/**
 * Open domain editor modal (create new)
 */
function openDomainEditor(domainId = null) {
  editingDomainId = domainId;
  const modal = document.getElementById("domain-editor-modal");
  const title = document.getElementById("domain-editor-title");

  if (domainId) {
    // Edit existing
    const domain = domainsConfig.domains.find((d) => d.id === domainId);
    if (!domain) {
      console.error("Domain not found:", domainId);
      return;
    }

    title.textContent = "Edit Domain";
    document.getElementById("domain-name-input").value = domain.name;
    document.getElementById("domain-description-input").value =
      domain.description || "";
    document.getElementById("domain-folder-input").value = domain.folderPath;
    document.getElementById("domain-weight-slider").value = Math.round(
      domain.ragWeight * 100,
    );
    document.getElementById("domain-weight-value").textContent =
      `${Math.round(domain.ragWeight * 100)}%`;

    selectedIcon = domain.icon;
    selectedColor = domain.color;
    domainKeywords = [...domain.autoTagRules];

    updateIconPreview();
    updateColorPreview();
    renderKeywordsTags();
  } else {
    // Create new
    title.textContent = "Add New Domain";
    document.getElementById("domain-name-input").value = "";
    document.getElementById("domain-description-input").value = "";
    document.getElementById("domain-folder-input").value = "";
    document.getElementById("domain-weight-slider").value = 20;
    document.getElementById("domain-weight-value").textContent = "20%";

    selectedIcon = "folder";
    selectedColor = "#808080";
    domainKeywords = [];

    updateIconPreview();
    updateColorPreview();
    renderKeywordsTags();
  }

  modal.classList.remove("hidden");
  document.getElementById("domain-name-input").focus();
}

/**
 * Edit domain (exposed globally)
 */
function editDomain(domainId) {
  openDomainEditor(domainId);
}

/**
 * Delete domain
 */
async function deleteDomain(domainId) {
  const domain = domainsConfig.domains.find((d) => d.id === domainId);
  if (!domain) return;

  if (domainsConfig.domains.length <= 1) {
    alert("Cannot delete the last domain");
    return;
  }

  if (!confirm(`Delete domain "${domain.name}"? This cannot be undone.`)) {
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:11436/polly/domains/${domainId}`,
      {
        method: "DELETE",
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to delete domain");
    }

    // Reload domains
    await loadDomainsConfig();
  } catch (error) {
    console.error("Failed to delete domain:", error);
    alert(`Failed to delete domain: ${error.message}`);
  }
}

/**
 * Save domain (create or update)
 */
async function saveDomain() {
  const nameInput = document.getElementById("domain-name-input");
  const descriptionInput = document.getElementById("domain-description-input");
  const folderInput = document.getElementById("domain-folder-input");
  const weightSlider = document.getElementById("domain-weight-slider");

  const name = nameInput.value.trim();
  const description = descriptionInput.value.trim();
  const folderPath = folderInput.value.trim();
  const ragWeight = parseInt(weightSlider.value) / 100;

  // Validation
  if (!name) {
    showDomainEditorError("Name is required");
    nameInput.focus();
    return;
  }

  if (name.length > 30) {
    showDomainEditorError("Name must be 30 characters or less");
    nameInput.focus();
    return;
  }

  if (description.length > 200) {
    showDomainEditorError("Description must be 200 characters or less");
    descriptionInput.focus();
    return;
  }

  // Check for duplicate name (if creating or renaming)
  if (editingDomainId) {
    const existingDomain = domainsConfig.domains.find(
      (d) => d.id === editingDomainId,
    );
    if (existingDomain && existingDomain.name !== name) {
      if (
        domainsConfig.domains.some(
          (d) => d.name === name && d.id !== editingDomainId,
        )
      ) {
        showDomainEditorError("A domain with this name already exists");
        nameInput.focus();
        return;
      }
    }
  } else {
    if (domainsConfig.domains.some((d) => d.name === name)) {
      showDomainEditorError("A domain with this name already exists");
      nameInput.focus();
      return;
    }
  }

  try {
    const payload = {
      name,
      description,
      color: selectedColor,
      icon: selectedIcon,
      folderPath,
      ragWeight,
      autoTagRules: domainKeywords,
    };

    let response;
    if (editingDomainId) {
      // Update existing
      response = await fetch(
        `http://127.0.0.1:11436/polly/domains/${editingDomainId}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        },
      );
    } else {
      // Create new
      // Generate ID from name
      const id = name.toLowerCase().replace(/[^a-z0-9]/g, "-");
      payload.id = id;

      response = await fetch("http://127.0.0.1:11436/polly/domains", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to save domain");
    }

    // Close modal and reload
    closeDomainEditor();
    await loadDomainsConfig();
  } catch (error) {
    console.error("Failed to save domain:", error);
    showDomainEditorError(error.message);
  }
}

/**
 * Close domain editor modal
 */
function closeDomainEditor() {
  const modal = document.getElementById("domain-editor-modal");
  modal.classList.add("hidden");
  editingDomainId = null;
  hideDomainEditorError();
}

/**
 * Show error in domain editor
 */
function showDomainEditorError(message) {
  const errorDiv = document.getElementById("domain-editor-error");
  errorDiv.textContent = message;
  errorDiv.classList.remove("hidden");
}

/**
 * Hide domain editor error
 */
function hideDomainEditorError() {
  const errorDiv = document.getElementById("domain-editor-error");
  errorDiv.classList.add("hidden");
}

/**
 * Show domains error
 */
function showDomainsError(message) {
  const listContainer = document.getElementById("domains-list");
  listContainer.innerHTML = `<div class="error-message" style="padding: var(--spacing-md);">${message}</div>`;
}

/**
 * Update icon preview
 */
function updateIconPreview() {
  const preview = document.getElementById("domain-icon-preview");
  preview.innerHTML = `<i data-lucide="${selectedIcon}" style="width: 20px; height: 20px;"></i>`;
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

/**
 * Update color preview
 */
function updateColorPreview() {
  document.getElementById("domain-color-preview").style.background =
    selectedColor;

  // Update selected state
  document.querySelectorAll(".color-option").forEach((btn) => {
    btn.classList.remove("selected");
    if (btn.dataset.color === selectedColor) {
      btn.classList.add("selected");
    }
  });
}

/**
 * Render keywords tags
 */
function renderKeywordsTags() {
  const container = document.getElementById("domain-keywords-tags");

  if (domainKeywords.length === 0) {
    container.innerHTML =
      '<div style="color: var(--text-muted); font-size: 12px; padding: 8px;">No keywords yet</div>';
    return;
  }

  container.innerHTML = domainKeywords
    .map(
      (keyword) => `
    <div class="keyword-tag">
      <span>${keyword}</span>
      <button type="button" class="keyword-tag-remove" onclick="removeKeyword('${keyword}')">×</button>
    </div>
  `,
    )
    .join("");
}

/**
 * Add keyword
 */
function addKeyword(keyword) {
  keyword = keyword.trim().toLowerCase();
  if (!keyword) return;

  if (domainKeywords.includes(keyword)) {
    return;
  }

  domainKeywords.push(keyword);
  renderKeywordsTags();

  // Clear input
  document.getElementById("domain-keywords-input").value = "";
}

/**
 * Remove keyword (exposed globally)
 */
function removeKeyword(keyword) {
  domainKeywords = domainKeywords.filter((kw) => kw !== keyword);
  renderKeywordsTags();
}

/**
 * Suggest keywords using AI
 */
async function suggestDomainKeywords() {
  const btn = document.getElementById("btn-suggest-keywords");
  const suggestedContainer = document.getElementById("suggested-keywords");
  const nameInput = document.getElementById("domain-name-input");
  const descriptionInput = document.getElementById("domain-description-input");

  const name = nameInput.value.trim();
  if (!name) {
    alert("Please enter a domain name first");
    return;
  }

  const description = descriptionInput.value.trim();

  // Show loading state
  btn.classList.add("loading");
  btn.disabled = true;
  suggestedContainer.style.display = "none";
  suggestedContainer.innerHTML = "";

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/domains/suggest-keywords",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          description,
          existingKeywords: domainKeywords,
        }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to suggest keywords");
    }

    const result = await response.json();
    const suggestions = result.suggestedKeywords || [];

    if (suggestions.length === 0) {
      alert("No keyword suggestions available");
      return;
    }

    // Render suggested keywords as clickable chips
    suggestedContainer.innerHTML = suggestions
      .map(
        (s) => `
        <span class="keyword-tag suggested" onclick="acceptSuggestedKeyword('${s.keyword}', this)">
          ${s.keyword}
        </span>
      `,
      )
      .join("");

    suggestedContainer.style.display = "flex";

    // Log reasoning for debugging
    if (result.reasoning) {
      console.log("Keyword suggestion reasoning:", result.reasoning);
    }
  } catch (error) {
    console.error("Failed to suggest keywords:", error);
    alert(`Failed to suggest keywords: ${error.message}`);
  } finally {
    btn.classList.remove("loading");
    btn.disabled = false;
  }
}

/**
 * Accept a suggested keyword (exposed globally)
 */
function acceptSuggestedKeyword(keyword, element) {
  addKeyword(keyword);

  // Remove the suggestion chip
  element.remove();

  // Hide container if no more suggestions
  const container = document.getElementById("suggested-keywords");
  if (container.children.length === 0) {
    container.style.display = "none";
  }
}

/**
 * Toggle folder numbering
 */
async function toggleFolderNumbering(enabled) {
  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/domains/folder-numbering",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to toggle folder numbering");
    }

    // Reload domains to see updated folder paths
    await loadDomainsConfig();
  } catch (error) {
    console.error("Failed to toggle folder numbering:", error);
    alert(`Failed to update folder numbering: ${error.message}`);

    // Reset toggle
    document.getElementById("folder-numbering-toggle").checked = !enabled;
  }
}

/**
 * Setup drag and drop for reordering
 */
function setupDragAndDrop() {
  const cards = document.querySelectorAll(".domain-card-item");

  cards.forEach((card) => {
    card.addEventListener("dragstart", handleDragStart);
    card.addEventListener("dragover", handleDragOver);
    card.addEventListener("drop", handleDrop);
    card.addEventListener("dragend", handleDragEnd);
  });
}

let draggedElement = null;

function handleDragStart(e) {
  draggedElement = this;
  this.classList.add("dragging");
  e.dataTransfer.effectAllowed = "move";
  e.dataTransfer.setData("text/html", this.innerHTML);
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault();
  }
  e.dataTransfer.dropEffect = "move";
  return false;
}

function handleDrop(e) {
  if (e.stopPropagation) {
    e.stopPropagation();
  }

  if (draggedElement !== this) {
    // Get all cards
    const allCards = Array.from(document.querySelectorAll(".domain-card-item"));
    const draggedIndex = allCards.indexOf(draggedElement);
    const targetIndex = allCards.indexOf(this);

    // Reorder in DOM
    if (draggedIndex < targetIndex) {
      this.parentNode.insertBefore(draggedElement, this.nextSibling);
    } else {
      this.parentNode.insertBefore(draggedElement, this);
    }

    // Save new order
    saveDomainsOrder();
  }

  return false;
}

function handleDragEnd(e) {
  this.classList.remove("dragging");
}

/**
 * Save domains order after drag and drop
 */
async function saveDomainsOrder() {
  const cards = document.querySelectorAll(".domain-card-item");
  const orderedIds = Array.from(cards).map((card) => card.dataset.domainId);

  try {
    const response = await fetch(
      "http://127.0.0.1:11436/polly/domains/reorder",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain_ids: orderedIds }),
      },
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to reorder domains");
    }

    // Reload to get updated order
    await loadDomainsConfig();
  } catch (error) {
    console.error("Failed to save domain order:", error);
    alert(`Failed to save order: ${error.message}`);
    // Reload to restore correct order
    await loadDomainsConfig();
  }
}

/**
 * ===========================================
 * DEDUPLICATION SETTINGS (Phase 21)
 * ===========================================
 */

/**
 * Load deduplication settings from server
 */
async function loadDedupSettings() {
  try {
    const response = await fetch(
      "http://127.0.0.1:11436/deduplication/settings",
    );
    if (!response.ok) {
      console.error("Failed to load dedup settings:", response.status);
      return;
    }

    const data = await response.json();

    // Update UI elements
    const enabledCheckbox = document.getElementById("settings-dedup-enabled");
    const thresholdSlider = document.getElementById("settings-dedup-threshold");
    const thresholdValue = document.getElementById(
      "settings-dedup-threshold-value",
    );
    const maxResultsSelect = document.getElementById(
      "settings-dedup-max-results",
    );

    if (enabledCheckbox) {
      enabledCheckbox.checked = data.enabled !== false;
    }

    if (thresholdSlider && thresholdValue) {
      // Convert decimal (0.70) to percentage (70)
      const percentage = Math.round(data.similarity_threshold * 100);
      thresholdSlider.value = percentage;
      thresholdValue.textContent = `${percentage}%`;
    }

    if (maxResultsSelect) {
      maxResultsSelect.value = data.max_results || 5;
    }

    console.log("Loaded dedup settings:", data);
  } catch (error) {
    console.error("Error loading dedup settings:", error);
  }
}

/**
 * Save deduplication settings to server
 */
async function saveDedupSettings() {
  try {
    const enabledEl = document.getElementById("settings-dedup-enabled");
    const thresholdEl = document.getElementById("settings-dedup-threshold");
    const maxResultsEl = document.getElementById("settings-dedup-max-results");

    if (!enabledEl || !thresholdEl || !maxResultsEl) {
      console.warn("Dedup settings elements not found, skipping save");
      return true; // Don't fail the overall save
    }

    const settings = {
      enabled: enabledEl.checked,
      similarity_threshold: parseInt(thresholdEl.value),
      max_results: parseInt(maxResultsEl.value),
    };

    console.log("Saving dedup settings:", settings);

    const response = await fetch(
      "http://127.0.0.1:11436/deduplication/settings",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      },
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to save: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    console.log("Dedup settings saved successfully:", result);
    return true;
  } catch (error) {
    console.error("Error saving dedup settings:", error);
    throw error;
  }
}

/**
 * Setup deduplication settings UI
 */
function setupDedupSettings() {
  // Update threshold value display when slider moves
  const thresholdSlider = document.getElementById("settings-dedup-threshold");
  const thresholdValue = document.getElementById(
    "settings-dedup-threshold-value",
  );

  if (thresholdSlider && thresholdValue) {
    thresholdSlider.addEventListener("input", (e) => {
      thresholdValue.textContent = `${e.target.value}%`;
    });
  }

  // Load settings when Advanced tab is opened
  const advancedTab = document.querySelector('[data-tab="tab-advanced"]');
  if (advancedTab) {
    advancedTab.addEventListener("click", () => {
      loadDedupSettings();
    });
  }
}

/**
 * ===========================================
 * NOTES MIGRATION (Phase 16 - Migration UI)
 * ===========================================
 */

let migrationPollInterval = null;

/**
 * Load current notes source info
 */
async function loadNotesSource() {
  try {
    const response = await fetch("http://127.0.0.1:11436/polly/notes/source");
    if (!response.ok) {
      console.error("Failed to load notes source:", response.status);
      return;
    }

    const data = await response.json();

    // Update UI
    const sourceEl = document.getElementById("notes-current-source");
    const pathEl = document.getElementById("notes-current-path");

    if (sourceEl) {
      sourceEl.textContent =
        data.active_source === "obsidian" ? "Obsidian" : "Native Polly";
    }

    if (pathEl) {
      pathEl.textContent = data.notes_path || data.vault_path;
    }

    // Always show migration section - users might want to import Obsidian notes even when using native KB
    const migrationSection = document.getElementById("migration-section");
    if (migrationSection) {
      migrationSection.style.display = "block";

      // Update the description to be clearer
      const migrationDesc = migrationSection.querySelector(".form-hint");
      if (migrationDesc && data.active_source === "native") {
        migrationDesc.innerHTML = `
          <i data-lucide="package" style="width: 14px; height: 14px;"></i>
          Import your Obsidian vault to Polly's native notes. This will merge notes into your existing native notes directory.
        `;
        lucide.createIcons();
      }

      // Load and display Obsidian vault path
      loadMigrationVaultPath();
    }

    console.log("Loaded notes source:", data);
  } catch (error) {
    console.error("Error loading notes source:", error);
  }
}

/**
 * Load and display Obsidian vault path for migration
 */
async function loadMigrationVaultPath() {
  try {
    const vaultPathEl = document.getElementById("migration-vault-path");
    const vaultInfoEl = document.getElementById("migration-vault-info");

    if (!vaultPathEl) return;

    // Get Obsidian integration info
    const response = await fetch("http://127.0.0.1:11436/polly/integrations");
    const data = await response.json();

    const obsidian = data.integrations?.obsidian;

    if (obsidian && obsidian.vault_path) {
      vaultPathEl.textContent = obsidian.vault_path;
      vaultInfoEl.style.display = "block";
    } else {
      vaultPathEl.textContent = "Obsidian vault not configured";
      vaultInfoEl.style.borderLeft = "3px solid #ef4444";
      vaultInfoEl.style.background = "rgba(239, 68, 68, 0.1)";
    }
  } catch (error) {
    console.error("Error loading vault path:", error);
    const vaultPathEl = document.getElementById("migration-vault-path");
    if (vaultPathEl) {
      vaultPathEl.textContent = "Error loading vault path";
    }
  }
}

/**
 * Start migration from Obsidian to native
 */
async function startMigration() {
  try {
    const btn = document.getElementById("btn-start-migration");
    if (!btn) return;

    // Get options
    const options = {
      copy_attachments:
        document.getElementById("migration-copy-attachments")?.checked ?? true,
      preserve_structure:
        document.getElementById("migration-preserve-structure")?.checked ??
        true,
      skip_canvas:
        document.getElementById("migration-skip-canvas")?.checked ?? true,
      switch_source:
        document.getElementById("migration-switch-source")?.checked ?? true,
    };

    // Get Obsidian vault path from integrations
    const integrationsResponse = await fetch(
      "http://127.0.0.1:11436/polly/integrations",
    );
    const integrationsData = await integrationsResponse.json();

    const obsidianIntegration = integrationsData.integrations?.obsidian;
    if (!obsidianIntegration || !obsidianIntegration.vault_path) {
      showToast(
        "Obsidian vault path not configured. Please configure Obsidian integration first.",
        "error",
      );
      return;
    }

    const vaultPath = obsidianIntegration.vault_path;

    console.log("Starting migration from:", vaultPath);

    // Disable button
    btn.disabled = true;
    btn.innerHTML =
      '<i data-lucide="loader" style="width: 16px; height: 16px; margin-right: 6px; animation: spin 1s linear infinite;"></i><span>Starting...</span>';
    lucide.createIcons();

    // Start migration
    const response = await fetch(
      "http://127.0.0.1:11436/polly/notes/migrate-from-obsidian",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          vault_path: vaultPath,
          options: options,
        }),
      },
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Migration failed: ${error}`);
    }

    const data = await response.json();

    console.log("Migration started:", data);

    // Show progress UI
    showMigrationProgress(data.migration_id);

    // Start polling for progress
    pollMigrationProgress(data.migration_id);
  } catch (error) {
    console.error("Error starting migration:", error);
    showToast("Failed to start migration: " + error.message, "error");

    // Re-enable button
    const btn = document.getElementById("btn-start-migration");
    if (btn) {
      btn.disabled = false;
      btn.innerHTML =
        '<i data-lucide="package" style="width: 16px; height: 16px; margin-right: 6px;"></i><span>Start Migration</span>';
      lucide.createIcons();
    }
  }
}

/**
 * Show migration progress UI
 */
function showMigrationProgress(migrationId) {
  const controlsEl = document.getElementById("migration-controls");
  const statusEl = document.getElementById("migration-status");

  if (controlsEl) controlsEl.classList.add("hidden");
  if (statusEl) statusEl.classList.remove("hidden");
}

/**
 * Poll migration progress
 */
async function pollMigrationProgress(migrationId) {
  // Clear any existing interval
  if (migrationPollInterval) {
    clearInterval(migrationPollInterval);
  }

  // Poll every second
  migrationPollInterval = setInterval(async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:11436/polly/notes/migrate/${migrationId}/status`,
      );
      if (!response.ok) {
        console.error("Failed to get migration status:", response.status);
        return;
      }

      const progress = await response.json();

      // Update progress UI
      updateMigrationProgress(progress);

      // Check if complete
      if (progress.status === "completed" || progress.status === "failed") {
        clearInterval(migrationPollInterval);
        migrationPollInterval = null;

        if (progress.status === "completed") {
          showMigrationComplete(progress, migrationId);
        } else {
          showMigrationError(progress);
        }
      }
    } catch (error) {
      console.error("Error polling migration progress:", error);
    }
  }, 1000);
}

/**
 * Update migration progress UI
 */
function updateMigrationProgress(progress) {
  const progressBar = document.getElementById("migration-progress-bar");
  const progressText = document.getElementById("migration-progress-text");
  const currentFile = document.getElementById("migration-current-file");
  const stats = document.getElementById("migration-stats");

  if (progressBar) {
    progressBar.style.width = `${progress.progress_percent}%`;
  }

  if (progressText) {
    progressText.textContent = `${progress.progress_percent}% (${progress.files_copied}/${progress.total_files})`;
  }

  if (currentFile) {
    currentFile.textContent = progress.current_file || "Processing...";
  }

  if (stats) {
    const elapsed = progress.elapsed_seconds;
    const remaining = progress.estimated_remaining;
    stats.textContent = `Elapsed: ${elapsed}s${remaining ? ` • Remaining: ~${remaining}s` : ""}${progress.files_skipped > 0 ? ` • Skipped: ${progress.files_skipped}` : ""}`;
  }
}

/**
 * Show migration complete UI
 */
function showMigrationComplete(progress, migrationId) {
  const statusEl = document.getElementById("migration-status");
  const completeEl = document.getElementById("migration-complete");
  const summaryEl = document.getElementById("migration-summary");

  if (statusEl) statusEl.classList.add("hidden");
  if (completeEl) completeEl.classList.remove("hidden");

  if (summaryEl) {
    summaryEl.innerHTML = `
      <div style="display: flex; gap: 16px;">
        <div>
          <div style="font-size: 1.5em; font-weight: 600; color: #4ade80;">${progress.files_copied}</div>
          <div>files copied</div>
        </div>
        ${
          progress.files_skipped > 0
            ? `
        <div>
          <div style="font-size: 1.5em; font-weight: 600; color: var(--text-secondary);">${progress.files_skipped}</div>
          <div>files skipped</div>
        </div>
        `
            : ""
        }
        <div>
          <div style="font-size: 1.5em; font-weight: 600; color: var(--text-secondary);">${progress.elapsed_seconds}s</div>
          <div>elapsed time</div>
        </div>
      </div>
    `;
  }

  // Set up switch button
  const switchBtn = document.getElementById("btn-switch-to-native");
  if (switchBtn) {
    switchBtn.onclick = () => switchToNativeSource(migrationId);
  }

  showToast("Migration completed successfully!", "success");
}

/**
 * Show migration error
 */
function showMigrationError(progress) {
  const statusEl = document.getElementById("migration-status");
  const controlsEl = document.getElementById("migration-controls");

  if (statusEl) statusEl.classList.add("hidden");
  if (controlsEl) controlsEl.classList.remove("hidden");

  const errorMsg =
    progress.errors.length > 0
      ? progress.errors.map((e) => `${e.file}: ${e.error}`).join("\n")
      : "Unknown error occurred";

  showToast("Migration failed: " + errorMsg, "error");

  // Re-enable button
  const btn = document.getElementById("btn-start-migration");
  if (btn) {
    btn.disabled = false;
    btn.innerHTML =
      '<i data-lucide="package" style="width: 16px; height: 16px; margin-right: 6px;"></i><span>Start Migration</span>';
    lucide.createIcons();
  }
}

/**
 * Switch to native notes source
 */
async function switchToNativeSource(migrationId) {
  try {
    const btn = document.getElementById("btn-switch-to-native");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML =
        '<i data-lucide="loader" style="width: 16px; height: 16px; margin-right: 6px; animation: spin 1s linear infinite;"></i><span>Switching...</span>';
      lucide.createIcons();
    }

    const response = await fetch(
      `http://127.0.0.1:11436/polly/notes/migrate/${migrationId}/switch-source`,
      {
        method: "POST",
      },
    );

    if (!response.ok) {
      throw new Error("Failed to switch source");
    }

    const data = await response.json();

    showToast("Switched to native notes! Reloading...", "success");

    // Reload after 2 seconds
    setTimeout(() => {
      location.reload();
    }, 2000);
  } catch (error) {
    console.error("Error switching source:", error);
    showToast("Failed to switch source: " + error.message, "error");

    const btn = document.getElementById("btn-switch-to-native");
    if (btn) {
      btn.disabled = false;
      btn.innerHTML =
        '<i data-lucide="check" style="width: 16px; height: 16px; margin-right: 6px;"></i><span>Switch to Native Notes</span>';
      lucide.createIcons();
    }
  }
}

/**
 * Setup migration UI
 */
function setupMigration() {
  // Load notes source when Notes tab is opened
  const notesTab = document.querySelector('[data-tab="notes"]');
  if (notesTab) {
    notesTab.addEventListener("click", () => {
      loadNotesSource();
    });
  }

  // Set up start migration button
  const startBtn = document.getElementById("btn-start-migration");
  if (startBtn) {
    startBtn.addEventListener("click", startMigration);
  }

  // Set up re-index button
  const reindexBtn = document.getElementById("btn-reindex-notes");
  if (reindexBtn) {
    reindexBtn.onclick = startReindex;
  }

  // Set up knowledge base location handlers
  setupKnowledgeBaseLocation();
}

/**
 * ===========================================
 * KNOWLEDGE BASE LOCATION MANAGEMENT
 * ===========================================
 */

/**
 * Set up knowledge base location UI and handlers
 */
async function setupKnowledgeBaseLocation() {
  // Load current location when Notes tab is opened
  const notesTab = document.querySelector('[data-tab="notes"]');
  if (notesTab) {
    notesTab.addEventListener("click", async () => {
      await loadKnowledgeBasePath();
      await loadCloudServices();
    });
  }

  // Set up change location button
  const changeBtn = document.getElementById("btn-change-kb-location");
  if (changeBtn) {
    changeBtn.onclick = openKnowledgeBaseMigrationModal;
  }

  // Set up custom path chooser
  const customPathBtn = document.getElementById("btn-choose-custom-path");
  if (customPathBtn) {
    customPathBtn.onclick = chooseCustomKnowledgeBasePath;
  }

  // Set up start migration button
  const startMigrationBtn = document.getElementById("btn-start-kb-migration");
  if (startMigrationBtn) {
    startMigrationBtn.onclick = startKnowledgeBaseMigration;
  }
}

/**
 * Load current knowledge base path
 */
async function loadKnowledgeBasePath() {
  const result = await safeFetch(
    "http://127.0.0.1:11436/polly/config/knowledge-base-path",
    {},
    true,
  );

  if (result.ok) {
    const pathEl = document.getElementById("kb-current-path");
    if (pathEl) {
      pathEl.textContent = result.data.path;

      // Show suggestion if using default path
      if (result.data.isDefault) {
        const suggestionsEl = document.getElementById(
          "cloud-services-suggestions",
        );
        if (suggestionsEl) {
          suggestionsEl.classList.remove("hidden");
        }
      }
    }
  }
}

/**
 * Load available cloud services
 */
async function loadCloudServices() {
  const result = await safeFetch(
    "http://127.0.0.1:11436/polly/config/cloud-services",
    {},
    true,
  );

  if (result.ok && result.data.services) {
    const availableServices = result.data.services.filter((s) => s.available);

    if (availableServices.length > 0) {
      // Populate quick suggestions list
      const listEl = document.getElementById("cloud-services-list");
      if (listEl) {
        listEl.innerHTML = availableServices
          .map(
            (service) => `
          <button class="btn btn-secondary cloud-service-btn" data-path="${service.suggestedPath}" style="text-align: left; justify-content: flex-start;">
            <span style="margin-right: 8px;">${getCloudServiceIcon(service.name)}</span>
            <div style="flex: 1;">
              <div style="font-weight: 600;">${service.name}</div>
              <div style="font-size: 0.85em; color: var(--text-secondary); font-family: monospace;">${service.suggestedPath}</div>
            </div>
            <i data-lucide="arrow-right" style="width: 16px; height: 16px; margin-left: 8px;"></i>
          </button>
        `,
          )
          .join("");

        // Add click handlers
        listEl.querySelectorAll(".cloud-service-btn").forEach((btn) => {
          btn.onclick = () => {
            const path = btn.getAttribute("data-path");
            selectKnowledgeBasePath(path);
          };
        });

        lucide.createIcons();
      }
    }
  }
}

/**
 * Get icon for cloud service
 */
function getCloudServiceIcon(serviceName) {
  const icons = {
    Dropbox: "📦",
    "iCloud Drive": "☁️",
    "Google Drive": "🔷",
    OneDrive: "🔷",
  };
  return icons[serviceName] || "folder";
}

/**
 * Open knowledge base migration modal
 */
async function openKnowledgeBaseMigrationModal() {
  const modal = document.getElementById("kb-migration-modal");
  if (!modal) return;

  // Reset modal state
  document.getElementById("kb-migration-step-1").classList.remove("hidden");
  document.getElementById("kb-migration-step-2").classList.add("hidden");
  document.getElementById("kb-migration-step-3").classList.add("hidden");
  document.getElementById("kb-selected-path").classList.add("hidden");
  document.getElementById("kb-migration-preview").classList.add("hidden");
  document.getElementById("btn-start-kb-migration").disabled = true;

  // Load cloud services for modal
  await loadCloudServicesForModal();

  // Load migration preview
  await loadMigrationPreview();

  // Show modal
  modal.classList.remove("hidden");
}

/**
 * Load cloud services for migration modal
 */
async function loadCloudServicesForModal() {
  const result = await safeFetch(
    "http://127.0.0.1:11436/polly/config/cloud-services",
    {},
    true,
  );

  if (result.ok && result.data.services) {
    const availableServices = result.data.services.filter((s) => s.available);

    const listEl = document.getElementById("kb-cloud-services-list");
    if (listEl) {
      listEl.innerHTML = availableServices
        .map(
          (service) => `
        <button class="btn btn-secondary cloud-service-modal-btn" data-path="${service.suggestedPath}" style="text-align: left; justify-content: flex-start;">
          <span style="margin-right: 8px;">${getCloudServiceIcon(service.name)}</span>
          <div style="flex: 1;">
            <div style="font-weight: 600;">${service.name}</div>
            <div style="font-size: 0.85em; color: var(--text-secondary); font-family: monospace;">${service.suggestedPath}</div>
          </div>
          <i data-lucide="check-circle" class="service-check hidden" style="width: 20px; height: 20px; margin-left: 8px; color: var(--accent);"></i>
        </button>
      `,
        )
        .join("");

      // Add click handlers
      listEl.querySelectorAll(".cloud-service-modal-btn").forEach((btn) => {
        btn.onclick = () => {
          const path = btn.getAttribute("data-path");
          selectKnowledgeBasePath(path);

          // Update UI to show selection
          listEl.querySelectorAll(".cloud-service-modal-btn").forEach((b) => {
            b.classList.remove("btn-primary");
            b.classList.add("btn-secondary");
            b.querySelector(".service-check").classList.add("hidden");
          });
          btn.classList.remove("btn-secondary");
          btn.classList.add("btn-primary");
          btn.querySelector(".service-check").classList.remove("hidden");
        };
      });

      lucide.createIcons();
    }
  }
}

/**
 * Load migration preview stats
 */
async function loadMigrationPreview() {
  const result = await safeFetch(
    "http://127.0.0.1:11436/polly/config/migration-preview",
    {},
    true,
  );

  if (result.ok && result.data.stats) {
    const stats = result.data.stats;
    const previewEl = document.getElementById("kb-preview-stats");

    if (previewEl) {
      const formatBytes = (bytes) => {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return (
          Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
        );
      };

      previewEl.innerHTML = `
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span><i data-lucide="file-text" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle; margin-right: 4px;"></i>Notes:</span>
          <span>${stats.notes.count} files (${formatBytes(stats.notes.size_bytes)})</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span><i data-lucide="message-square" style="width: 14px; height: 14px; display: inline-block; vertical-align: middle; margin-right: 4px;"></i>Conversations:</span>
          <span>${stats.conversations.count} files (${formatBytes(stats.conversations.size_bytes)})</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
          <span>📎 Attachments:</span>
          <span>${stats.attachments.count} files (${formatBytes(stats.attachments.size_bytes)})</span>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border-color); font-weight: 600;">
          <span>Total:</span>
          <span>${stats.total_files} files (${formatBytes(stats.total_size_bytes)})</span>
        </div>
      `;

      // Re-initialize Lucide icons
      if (typeof lucide !== "undefined") {
        lucide.createIcons();
      }

      document
        .getElementById("kb-migration-preview")
        .classList.remove("hidden");
    }
  }
}

/**
 * Choose custom knowledge base path using Electron dialog
 */
async function chooseCustomKnowledgeBasePath() {
  console.log("chooseCustomKnowledgeBasePath called");
  const result = await PollyBridge.safeCall("selectDirectory");
  console.log("Directory selection result:", result);

  // Handle different possible result formats
  let path = null;

  if (result) {
    // Format 1: {success: true, path: '...'} (Electron dialog)
    if (result.success && result.path) {
      path = result.path;
    }
    // Format 2: array of paths
    else if (Array.isArray(result) && result.length > 0) {
      path = result[0];
    }
    // Format 3: direct string
    else if (typeof result === "string") {
      path = result;
    }
  }

  if (path) {
    console.log("Selected path:", path);
    selectKnowledgeBasePath(path);
  } else {
    console.log("No directory selected or invalid result format");
  }
}

/**
 * Select a knowledge base path
 */
function selectKnowledgeBasePath(path) {
  console.log("selectKnowledgeBasePath called with path:", path);

  // Update selected path display
  const selectedPathEl = document.getElementById("kb-selected-path");
  if (selectedPathEl) {
    selectedPathEl.textContent = path;
    selectedPathEl.classList.remove("hidden");
    console.log("Updated selected path display");
  } else {
    console.error("kb-selected-path element not found");
  }

  // Enable start migration button
  const startBtn = document.getElementById("btn-start-kb-migration");
  if (startBtn) {
    console.log("Found start button, enabling it");
    startBtn.disabled = false;
    startBtn.setAttribute("data-target-path", path);
  } else {
    console.error("btn-start-kb-migration button not found");
  }
}

/**
 * Start knowledge base migration
 */
async function startKnowledgeBaseMigration() {
  const startBtn = document.getElementById("btn-start-kb-migration");
  if (!startBtn) return;

  const targetPath = startBtn.getAttribute("data-target-path");
  if (!targetPath) {
    showToast("Please select a location first", "error");
    return;
  }

  try {
    // Switch to progress view
    document.getElementById("kb-migration-step-1").classList.add("hidden");
    document.getElementById("kb-migration-step-2").classList.remove("hidden");

    // Update status
    document.getElementById("kb-migration-status-text").textContent =
      "Preparing migration...";

    // Start migration
    const result = await safeFetch(
      "http://127.0.0.1:11436/polly/config/migrate-knowledge-base",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          targetPath: targetPath,
          createBackup: true,
        }),
      },
    );

    if (result.ok) {
      // Update progress
      document.getElementById("kb-migration-progress-bar").style.width = "100%";
      document.getElementById("kb-migration-progress-text").textContent =
        "100%";
      document.getElementById("kb-migration-status-text").textContent =
        "Migration complete!";

      // Show completion step
      setTimeout(() => {
        document.getElementById("kb-migration-step-2").classList.add("hidden");
        document
          .getElementById("kb-migration-step-3")
          .classList.remove("hidden");

        // Populate summary
        const summaryEl = document.getElementById("kb-migration-summary");
        if (summaryEl) {
          const formatBytes = (bytes) => {
            if (bytes === 0) return "0 B";
            const k = 1024;
            const sizes = ["B", "KB", "MB", "GB"];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return (
              Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
            );
          };

          summaryEl.innerHTML = `
            <div style="margin-bottom: 8px;"><strong>New Location:</strong> ${result.data.targetPath}</div>
            <div style="margin-bottom: 8px;"><strong>Files Moved:</strong> ${result.data.filesMigrated}</div>
            <div style="margin-bottom: 8px;"><strong>Size:</strong> ${formatBytes(result.data.bytesMigrated)}</div>
            ${result.data.backupPath ? `<div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); font-size: 0.9em; color: var(--text-secondary);">Backup created at: ${result.data.backupPath}</div>` : ""}
          `;
        }

        lucide.createIcons();
      }, 500);
    } else {
      showToast(`Migration failed: ${result.error}`, "error");
      document.getElementById("kb-migration-step-2").classList.add("hidden");
      document.getElementById("kb-migration-step-1").classList.remove("hidden");
    }
  } catch (error) {
    console.error("Migration error:", error);
    showToast(`Migration failed: ${error.message}`, "error");
    document.getElementById("kb-migration-step-2").classList.add("hidden");
    document.getElementById("kb-migration-step-1").classList.remove("hidden");
  }
}

/**
 * ===========================================
 * NOTES RE-INDEXING
 * ===========================================
 */

/**
 * Start re-indexing all notes to RAG
 */
async function startReindex() {
  try {
    const btn = document.getElementById("btn-reindex-notes");
    if (!btn) return;

    console.log("Starting notes re-indexing...");

    // Disable button
    btn.disabled = true;
    btn.innerHTML =
      '<i data-lucide="loader" style="width: 16px; height: 16px; margin-right: 6px; animation: spin 1s linear infinite;"></i><span>Starting...</span>';
    lucide.createIcons();

    // Hide any previous completion message
    const completeEl = document.getElementById("reindex-complete");
    if (completeEl) completeEl.classList.add("hidden");

    // Show progress UI
    const statusEl = document.getElementById("reindex-status");
    if (statusEl) statusEl.classList.remove("hidden");

    // Reset progress
    updateReindexProgress({ progress: 0, total: 0, file: "Initializing..." });

    // Start EventSource for streaming progress
    const eventSource = new EventSource(
      "http://127.0.0.1:11436/polly/notes/reindex",
    );

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("Reindex progress:", data);

        if (data.status === "started") {
          updateReindexProgress({
            progress: 0,
            total: data.total,
            file: "Starting...",
          });
        } else if (data.status === "progress") {
          updateReindexProgress({
            progress: data.progress,
            total: data.total,
            file: data.file,
            indexed: data.indexed,
          });
        } else if (data.status === "file_error") {
          console.warn(`Error indexing ${data.file}:`, data.error);
          // Continue showing progress despite file error
          updateReindexProgress({
            progress: data.progress,
            total: data.total,
            file: `Error: ${data.file}`,
            hasError: true,
          });
        } else if (data.status === "completed") {
          eventSource.close();
          showReindexComplete(data);
        } else if (data.status === "error") {
          eventSource.close();
          showReindexError(data.error);
        }
      } catch (error) {
        console.error("Error parsing reindex progress:", error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("EventSource error:", error);
      eventSource.close();
      showReindexError("Connection to server lost. Please try again.");
    };
  } catch (error) {
    console.error("Error starting reindex:", error);
    showToast("Failed to start re-indexing: " + error.message, "error");

    // Re-enable button
    const btn = document.getElementById("btn-reindex-notes");
    if (btn) {
      btn.disabled = false;
      btn.innerHTML =
        '<i data-lucide="refresh-cw" style="width: 16px; height: 16px; margin-right: 6px;"></i><span>Re-index All Notes</span>';
      lucide.createIcons();
    }
  }
}

/**
 * Update reindex progress UI
 */
function updateReindexProgress(data) {
  const progressBar = document.getElementById("reindex-progress-bar");
  const progressText = document.getElementById("reindex-progress-text");
  const currentFile = document.getElementById("reindex-current-file");
  const stats = document.getElementById("reindex-stats");

  if (!data.total || data.total === 0) {
    if (progressBar) progressBar.style.width = "0%";
    if (progressText) progressText.textContent = "Starting...";
    if (currentFile) currentFile.textContent = data.file || "Initializing...";
    if (stats) stats.textContent = "";
    return;
  }

  const percent = Math.round((data.progress / data.total) * 100);

  if (progressBar) {
    progressBar.style.width = `${percent}%`;
  }

  if (progressText) {
    progressText.textContent = `${percent}% (${data.progress}/${data.total})`;
  }

  if (currentFile) {
    const prefix = data.hasError ? "⚠ " : "• ";
    currentFile.textContent = prefix + (data.file || "Processing...");
  }

  if (stats && data.indexed !== undefined) {
    stats.textContent = `Indexed: ${data.indexed} files`;
  }
}

/**
 * Show reindex complete UI
 */
function showReindexComplete(data) {
  const statusEl = document.getElementById("reindex-status");
  const completeEl = document.getElementById("reindex-complete");
  const summaryEl = document.getElementById("reindex-summary");
  const btn = document.getElementById("btn-reindex-notes");

  if (statusEl) statusEl.classList.add("hidden");
  if (completeEl) completeEl.classList.remove("hidden");

  if (summaryEl) {
    summaryEl.innerHTML = `
      <div style="display: flex; gap: 16px; margin-top: 8px;">
        <div>
          <div style="font-size: 1.3em; font-weight: 600; color: #4ade80;">${data.indexed || data.total}</div>
          <div style="font-size: 0.85em;">notes indexed</div>
        </div>
        ${
          data.errors > 0
            ? `
        <div>
          <div style="font-size: 1.3em; font-weight: 600; color: #f59e0b;">${data.errors}</div>
          <div style="font-size: 0.85em;">errors</div>
        </div>
        `
            : ""
        }
        <div>
          <div style="font-size: 1.3em; font-weight: 600; color: var(--text-secondary);">${data.duration_seconds}s</div>
          <div style="font-size: 0.85em;">duration</div>
        </div>
      </div>
    `;
  }

  // Re-enable button
  if (btn) {
    btn.disabled = false;
    btn.innerHTML =
      '<i data-lucide="refresh-cw" style="width: 16px; height: 16px; margin-right: 6px;"></i><span>Re-index All Notes</span>';
    lucide.createIcons();
  }

  // Reload stats to reflect new indexed count
  console.log("[Reindex] Complete! Reloading stats...");
  loadKnowledgeData();

  showToast("Re-indexing completed successfully!", "success");
}

/**
 * Show reindex error
 */
function showReindexError(errorMessage) {
  const statusEl = document.getElementById("reindex-status");
  const btn = document.getElementById("btn-reindex-notes");

  if (statusEl) statusEl.classList.add("hidden");

  // Re-enable button
  if (btn) {
    btn.disabled = false;
    btn.innerHTML =
      '<i data-lucide="refresh-cw" style="width: 16px; height: 16px; margin-right: 6px;"></i><span>Re-index All Notes</span>';
    lucide.createIcons();
  }

  showToast("Re-indexing failed: " + errorMessage, "error");
}

/**
 * ===========================================
 * COMPRESSION SETTINGS
 * ===========================================
 */

/**
 * Load compression settings from server
 */
async function loadCompressionSettings() {
  try {
    const response = await fetch(`${API_URL}/api/settings/compression`);

    if (!response.ok) {
      throw new Error("Failed to load compression settings");
    }

    const data = await response.json();

    if (data.success && data.settings) {
      // Update form fields
      const enabledCheckbox = document.getElementById("compression-enabled");
      const thresholdInput = document.getElementById(
        "compression-message-threshold",
      );
      const ageInput = document.getElementById("compression-age-hours");
      const keepRecentInput = document.getElementById(
        "compression-keep-recent",
      );
      const showStatsCheckbox = document.getElementById(
        "compression-show-stats",
      );
      const strategySelect = document.getElementById("compression-strategy");
      const ragContextEnabled = document.getElementById(
        "compression-rag-context-enabled",
      );
      const ragContextRatio = document.getElementById(
        "compression-rag-context-ratio",
      );

      if (enabledCheckbox) enabledCheckbox.checked = data.settings.enabled;
      if (thresholdInput)
        thresholdInput.value = data.settings.message_threshold;
      if (ageInput) ageInput.value = data.settings.age_hours;
      if (keepRecentInput) keepRecentInput.value = data.settings.keep_recent;
      if (showStatsCheckbox)
        showStatsCheckbox.checked = data.settings.show_stats;
      if (strategySelect)
        strategySelect.value = data.settings.strategy || "auto";
      if (ragContextEnabled)
        ragContextEnabled.checked = data.settings.rag_context_enabled !== false;
      if (ragContextRatio)
        ragContextRatio.value = data.settings.rag_context_ratio ?? 0.5;

      // Enable/disable inputs based on enabled checkbox
      updateCompressionInputsState();
    }
  } catch (error) {
    console.error("Error loading compression settings:", error);
    showToast("Failed to load compression settings", "error");
  }
}

/**
 * Update compression inputs state based on enabled checkbox
 */
function updateCompressionInputsState() {
  const enabled =
    document.getElementById("compression-enabled")?.checked || false;
  const options = document.getElementById("compression-options");

  if (options) {
    options.style.opacity = enabled ? "1" : "0.5";

    const inputs = options.querySelectorAll("input, select");
    inputs.forEach((input) => {
      input.disabled = !enabled;
    });
  }
}

/**
 * Save compression settings to server
 */
async function saveCompressionSettings() {
  try {
    const enabled =
      document.getElementById("compression-enabled")?.checked || false;
    const threshold = parseInt(
      document.getElementById("compression-message-threshold")?.value || "20",
    );
    const ageHours = parseInt(
      document.getElementById("compression-age-hours")?.value || "24",
    );
    const keepRecent = parseInt(
      document.getElementById("compression-keep-recent")?.value || "10",
    );
    const showStats =
      document.getElementById("compression-show-stats")?.checked || false;
    const strategy =
      document.getElementById("compression-strategy")?.value || "auto";
    const ragContextEnabled =
      document.getElementById("compression-rag-context-enabled")?.checked !==
      false;
    const ragContextRatio = parseFloat(
      document.getElementById("compression-rag-context-ratio")?.value || "0.5",
    );

    // Validate inputs
    if (threshold < 10 || threshold > 100) {
      showToast("Message threshold must be between 10 and 100", "error");
      return;
    }

    if (ageHours < 1 || ageHours > 168) {
      showToast("Age threshold must be between 1 and 168 hours", "error");
      return;
    }

    if (keepRecent < 5 || keepRecent > 50) {
      showToast("Keep recent must be between 5 and 50", "error");
      return;
    }
    if (ragContextRatio < 0.1 || ragContextRatio > 1) {
      showToast("RAG context ratio must be between 0.1 and 1", "error");
      return;
    }

    const response = await fetch(`${API_URL}/api/settings/compression`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        enabled,
        message_threshold: threshold,
        age_hours: ageHours,
        keep_recent: keepRecent,
        show_stats: showStats,
        strategy,
        rag_context_enabled: ragContextEnabled,
        rag_context_ratio: ragContextRatio,
      }),
    });

    if (!response.ok) {
      // Try to get error details from response body
      let errorMessage = `Persona request failed: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = `Persona request failed: ${errorData.detail}`;
          console.error("[Persona] Server error details:", errorData);
        }
      } catch (e) {
        // Response wasn't JSON, just use status text
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();

    if (data.success) {
      showToast("Compression settings saved successfully!", "success");
    } else {
      throw new Error(data.message || "Unknown error");
    }
  } catch (error) {
    console.error("Error saving compression settings:", error);
    showToast("Failed to save compression settings: " + error.message, "error");
  }
}

/**
 * Reset compression settings to defaults
 */
async function resetCompressionSettings() {
  if (!confirm("Reset compression settings to defaults?")) {
    return;
  }

  try {
    const response = await fetch(`${API_URL}/api/settings/compression`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        enabled: true,
        message_threshold: 20,
        age_hours: 24,
        keep_recent: 10,
        show_stats: false,
        strategy: "auto",
        rag_context_enabled: true,
        rag_context_ratio: 0.5,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to reset compression settings");
    }

    // Reload settings
    await loadCompressionSettings();
    showToast("Compression settings reset to defaults", "success");
  } catch (error) {
    console.error("Error resetting compression settings:", error);
    showToast(
      "Failed to reset compression settings: " + error.message,
      "error",
    );
  }
}

/**
 * Load compression statistics from server
 */
async function loadCompressionStats() {
  try {
    const response = await fetch(`${API_URL}/api/settings/compression/stats`);

    if (!response.ok) {
      throw new Error("Failed to load compression stats");
    }

    const data = await response.json();

    if (data.success && data.stats) {
      displayCompressionStats(data.stats);
    }
  } catch (error) {
    console.error("Error loading compression stats:", error);
    const statsContent = document.getElementById("compression-stats-content");
    if (statsContent) {
      statsContent.innerHTML = `<p class="form-hint" style="color: var(--text-secondary);">Failed to load statistics</p>`;
    }
  }
}

/**
 * Display compression statistics
 */
function displayCompressionStats(stats) {
  const statsContent = document.getElementById("compression-stats-content");

  if (!statsContent) return;

  if (stats.total_conversations === 0) {
    statsContent.innerHTML = `
      <p class="form-hint" style="color: var(--text-secondary);">
        No compression data yet. Compression statistics will appear here once conversations are compressed.
      </p>
    `;
    return;
  }

  // Build stats HTML
  let html = `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px;">
      <div style="padding: 16px; background: var(--bg-hover); border-radius: 8px;">
        <div style="font-size: 24px; font-weight: 700; color: var(--accent);">${stats.total_conversations}</div>
        <div style="font-size: 12px; color: var(--text-secondary); text-transform: uppercase;">Conversations</div>
      </div>
      
      <div style="padding: 16px; background: var(--bg-hover); border-radius: 8px;">
        <div style="font-size: 24px; font-weight: 700; color: var(--accent);">${(stats.total_saved_tokens / 1000).toFixed(1)}K</div>
        <div style="font-size: 12px; color: var(--text-secondary); text-transform: uppercase;">Tokens Saved</div>
      </div>
      
      <div style="padding: 16px; background: var(--bg-hover); border-radius: 8px;">
        <div style="font-size: 24px; font-weight: 700; color: var(--accent);">${stats.savings_percent}%</div>
        <div style="font-size: 12px; color: var(--text-secondary); text-transform: uppercase;">Reduction</div>
      </div>
      
      <div style="padding: 16px; background: var(--bg-hover); border-radius: 8px;">
        <div style="font-size: 24px; font-weight: 700; color: var(--accent);">${stats.average_ratio}x</div>
        <div style="font-size: 12px; color: var(--text-secondary); text-transform: uppercase;">Avg Ratio</div>
      </div>
    </div>
  `;

  // Add recent compressions if available
  if (stats.recent_compressions && stats.recent_compressions.length > 0) {
    html += `
      <h4 style="margin-bottom: 12px; font-size: 14px;">Recent Compressions</h4>
      <div style="background: var(--bg-hover); border-radius: 8px; padding: 12px;">
    `;

    stats.recent_compressions.forEach((comp) => {
      const date = new Date(comp.created_at);
      html += `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-color);">
          <span style="font-size: 12px; color: var(--text-secondary);">${date.toLocaleDateString()} ${date.toLocaleTimeString()}</span>
          <span style="font-size: 13px;">${(comp.original_tokens / 1000).toFixed(1)}K → ${(comp.compressed_tokens / 1000).toFixed(1)}K tokens</span>
          <span style="background: var(--accent); color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600;">${comp.ratio.toFixed(1)}x</span>
        </div>
      `;
    });

    html += `</div>`;
  }

  statsContent.innerHTML = html;
}

/**
 * Setup compression settings UI
 */
function setupCompressionSettings() {
  // Enable/disable inputs when checkbox changes
  const enabledCheckbox = document.getElementById("compression-enabled");
  if (enabledCheckbox) {
    enabledCheckbox.addEventListener("change", updateCompressionInputsState);
  }

  // Save button
  const saveBtn = document.getElementById("btn-save-compression-settings");
  if (saveBtn) {
    saveBtn.addEventListener("click", saveCompressionSettings);
  }

  // Reset button
  const resetBtn = document.getElementById("btn-reset-compression-settings");
  if (resetBtn) {
    resetBtn.addEventListener("click", resetCompressionSettings);
  }
}

/**
 * ===========================================
 * PROVIDER MANAGEMENT SETTINGS
 * ===========================================
 */

async function loadProviderSettings() {
  const container = document.getElementById('providers-list');
  if (!container) {
    console.warn('[Providers] Container #providers-list not found');
    return;
  }
  
  container.innerHTML = '<div class="settings-loading-spinner">Loading providers...</div>';
  
  try {
    const response = await fetch(`${API_URL}/api/settings/providers/status`);
    
    if (!response.ok) {
      throw new Error(`Failed to load providers (status ${response.status})`);
    }
    
    const data = await response.json();
    console.log('[Providers] Data received:', data);
    
    // Check if LiteLLM is enabled
    if (!data.use_litellm) {
      container.innerHTML = `
        <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
          <i data-lucide="alert-circle" style="width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.5; color: var(--warning);"></i>
          <p style="font-size: 14px; margin-bottom: 8px;">LiteLLM Provider System Not Enabled</p>
          <p style="font-size: 12px; opacity: 0.7;">Enable <code>routing_v2.use_litellm: true</code> in config.yaml to use provider management.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }
    
    // Merge runtime stats (data.providers object) with config (data.config object)
    const providersList = [];
    
    // Start with config data (has all providers)
    if (data.config && typeof data.config === 'object') {
      for (const [providerName, configInfo] of Object.entries(data.config)) {
        const runtimeStats = data.providers?.[providerName] || {};
        providersList.push({
          name: providerName,
          config_enabled: configInfo.enabled !== false,
          has_api_key: configInfo.has_api_key === true,
          models: configInfo.models || [],
          stats: runtimeStats,
          available: runtimeStats.available !== false,
          failures: runtimeStats.failures || 0,
          last_success: runtimeStats.last_success
        });
      }
    } else if (data.providers && typeof data.providers === 'object') {
      // Fallback: if no config, use runtime stats only
      for (const [providerName, stats] of Object.entries(data.providers)) {
        providersList.push({
          name: providerName,
          config_enabled: true,
          has_api_key: true,
          models: stats.models || [],
          stats: stats,
          available: stats.available !== false,
          failures: stats.failures || 0,
          last_success: stats.last_success
        });
      }
    }
    
    if (providersList.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
          <i data-lucide="cloud" style="width: 48px; height: 48px; margin-bottom: 16px; opacity: 0.3;"></i>
          <p style="font-size: 14px;">No providers configured.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }
    
    // Sort providers alphabetically
    providersList.sort((a, b) => a.name.localeCompare(b.name));
    
    let html = `
      <div class="provider-cards">
    `;
    
    providersList.forEach(provider => {
      const isEnabled = provider.config_enabled === true;
      const hasApiKey = provider.has_api_key === true;
      const statusClass = isEnabled && hasApiKey ? 'provider-enabled' : 'provider-disabled';
      const statusText = !hasApiKey ? 'No API Key' : (isEnabled ? 'Enabled' : 'Disabled');
      
      html += `
        <div class="provider-card ${statusClass}" data-provider="${provider.name}">
          <div class="provider-header">
            <div class="provider-name">${formatProviderName(provider.name)}</div>
            <label class="provider-toggle">
              <input type="checkbox" 
                     class="provider-toggle-input" 
                     data-provider="${provider.name}"
                     ${isEnabled ? 'checked' : ''}
                     ${!hasApiKey ? 'disabled' : ''}>
              <span class="provider-toggle-slider"></span>
            </label>
          </div>
          
          <div class="provider-details">
            <div class="provider-status ${statusClass}">
              <span class="provider-status-dot"></span>
              <span>${statusText}</span>
            </div>
            
            ${provider.models && provider.models.length > 0 ? `
              <div class="provider-models">
                <span style="font-size: 11px; color: var(--text-secondary);">
                  ${provider.models.length} model${provider.models.length !== 1 ? 's' : ''} available
                </span>
              </div>
            ` : ''}
            
            ${provider.failures > 0 ? `
              <div class="provider-stats">
                <span style="font-size: 11px; color: var(--error);">
                  ${provider.failures} recent failure${provider.failures !== 1 ? 's' : ''}
                </span>
              </div>
            ` : ''}
          </div>
          
          <div class="provider-actions">
            ${!hasApiKey ? `
              <button class="btn btn-secondary btn-sm provider-add-key-btn" 
                      data-provider="${provider.name}">
                <i data-lucide="key" style="width: 14px; height: 14px;"></i>
                Add Key
              </button>
            ` : `
              <button class="btn btn-secondary btn-sm provider-test-btn" 
                      data-provider="${provider.name}"
                      ${!isEnabled ? 'disabled' : ''}>
                <i data-lucide="activity" style="width: 14px; height: 14px;"></i>
                Test
              </button>
            `}
          </div>
        </div>
      `;
    });
    
    html += `
      </div>
    `;
    
    container.innerHTML = html;
    lucide.createIcons();
    
    // Attach event listeners
    setupProviderEventListeners();
    
  } catch (error) {
    console.error('[Providers] Error loading providers:', error);
    container.innerHTML = `
      <div class="settings-error">
        <i data-lucide="alert-circle" style="width: 24px; height: 24px; margin-bottom: 8px;"></i>
        <p>Failed to load providers</p>
        <p style="font-size: 12px; opacity: 0.7;">${error.message}</p>
      </div>
    `;
    lucide.createIcons();
  }
}

function setupProviderEventListeners() {
  // Toggle switches
  document.querySelectorAll('.provider-toggle-input').forEach(toggle => {
    toggle.addEventListener('change', async (e) => {
      const providerName = e.target.dataset.provider;
      const enabled = e.target.checked;
      await toggleProvider(providerName, enabled);
    });
  });
  
  // Test buttons
  document.querySelectorAll('.provider-test-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const providerName = e.currentTarget.dataset.provider;
      await testProvider(providerName, e.currentTarget);
    });
  });
  
  // Add Key buttons - navigate to API Keys tab
  document.querySelectorAll('.provider-add-key-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const providerName = e.currentTarget.dataset.provider;
      console.log(`[Providers] Add key requested for ${providerName}, navigating to API Keys tab`);
      navigateToSettingsTab('api-keys');
    });
  });
}

async function toggleProvider(providerName, enabled) {
  try {
    const response = await fetch(`${API_URL}/api/settings/providers/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: providerName, enabled })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to toggle provider (status ${response.status})`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      showToast(`${formatProviderName(providerName)} ${enabled ? 'enabled' : 'disabled'}`, 'success');
      // Update the provider card UI
      const card = document.querySelector(`.provider-card[data-provider="${providerName}"]`);
      if (card) {
        if (enabled) {
          card.classList.remove('provider-disabled');
          card.classList.add('provider-enabled');
        } else {
          card.classList.remove('provider-enabled');
          card.classList.add('provider-disabled');
        }
        const statusText = card.querySelector('.provider-status span:last-child');
        if (statusText) statusText.textContent = enabled ? 'Enabled' : 'Disabled';
      }
    } else {
      throw new Error(data.error || 'Unknown error');
    }
  } catch (error) {
    console.error(`[Providers] Error toggling ${providerName}:`, error);
    showToast(`Failed to toggle provider: ${error.message}`, 'error');
    // Revert toggle
    const toggle = document.querySelector(`.provider-toggle-input[data-provider="${providerName}"]`);
    if (toggle) toggle.checked = !enabled;
  }
}

async function testProvider(providerName, button) {
  const originalHTML = button.innerHTML;
  button.disabled = true;
  button.innerHTML = '<i data-lucide="loader" style="width: 14px; height: 14px; animation: spin 1s linear infinite;"></i> Testing...';
  lucide.createIcons();
  
  try {
    const response = await fetch(`${API_URL}/api/settings/providers/test`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider: providerName })
    });
    
    if (!response.ok) {
      throw new Error(`Test request failed (status ${response.status})`);
    }
    
    const data = await response.json();
    
    if (data.success) {
      showToast(`${formatProviderName(providerName)} test successful`, 'success');
    } else {
      throw new Error(data.error || 'Test failed');
    }
  } catch (error) {
    console.error(`[Providers] Error testing ${providerName}:`, error);
    showToast(`Test failed: ${error.message}`, 'error');
  } finally {
    button.disabled = false;
    button.innerHTML = originalHTML;
    lucide.createIcons();
  }
}

function formatProviderName(provider) {
  const nameMap = {
    'openai': 'OpenAI',
    'anthropic': 'Anthropic',
    'google': 'Google',
    'deepseek': 'DeepSeek',
    'openrouter': 'OpenRouter',
    'groq': 'Groq',
    'together': 'Together AI'
  };
  return nameMap[provider] || provider.charAt(0).toUpperCase() + provider.slice(1);
}

/**
 * Navigates to a specific settings tab
 */
function navigateToSettingsTab(tabName) {
  console.log('[Settings] Navigating to tab:', tabName);
  
  // Find the tab button with matching data-tab attribute
  const tabButton = document.querySelector(`.settings-nav-item[data-tab="${tabName}"]`);
  
  if (tabButton) {
    // Simulate a click to trigger the existing tab switching logic
    tabButton.click();
  } else {
    console.warn('[Settings] Tab not found:', tabName);
  }
}

/**
 * Sets up cross-navigation links between settings pages
 */
function setupSettingsCrossLinks() {
  console.log('[Settings] Setting up cross-navigation links');
  
  // Find all links with data-goto-tab attribute
  document.querySelectorAll('[data-goto-tab]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetTab = e.currentTarget.dataset.gotoTab;
      navigateToSettingsTab(targetTab);
    });
  });
}

/**
 * ===========================================
 * MEMORY SETTINGS
 * ===========================================
 */

async function loadMemorySettings() {
  try {
    const response = await fetch(`${API_URL}/api/settings/memory`);
    if (!response.ok) throw new Error("Failed to load memory settings");
    const data = await response.json();
    if (data.success && data.settings) {
      const providerSelect = document.getElementById("memory-provider");
      const mem0Checkbox = document.getElementById("memory-mem0-enabled");
      if (providerSelect)
        providerSelect.value = data.settings.provider || "local";
      if (mem0Checkbox)
        mem0Checkbox.checked = data.settings.mem0_enabled === true;
    }
  } catch (error) {
    console.error("Error loading memory settings:", error);
    showToast("Failed to load memory settings", "error");
  }
}

async function saveMemorySettings() {
  try {
    const provider =
      document.getElementById("memory-provider")?.value || "local";
    const mem0Enabled =
      document.getElementById("memory-mem0-enabled")?.checked === true;
    const response = await fetch(`${API_URL}/api/settings/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, mem0_enabled: mem0Enabled }),
    });
    if (!response.ok) throw new Error("Failed to save memory settings");
    const data = await response.json();
    if (data.success) {
      showToast(
        "Memory settings saved. Changes take effect on next restart.",
        "success",
      );
    } else {
      throw new Error(data.message || "Unknown error");
    }
  } catch (error) {
    console.error("Error saving memory settings:", error);
    showToast("Failed to save memory settings: " + error.message, "error");
  }
}

function setupMemorySettings() {
  const saveBtn = document.getElementById("btn-save-memory-settings");
  if (saveBtn) saveBtn.addEventListener("click", saveMemorySettings);
}

// Make functions globally accessible
window.editDomain = editDomain;
window.deleteDomain = deleteDomain;
window.removeKeyword = removeKeyword;
window.acceptSuggestedKeyword = acceptSuggestedKeyword;

/**
 * Setup mental models UI event listeners
 */
document.addEventListener("DOMContentLoaded", () => {
  // Add Model button
  const addBtn = document.getElementById("btn-add-mental-model");
  if (addBtn) {
    addBtn.addEventListener("click", () => openMentalModelModal());
  }

  // Modal close buttons
  const closeBtn = document.getElementById("mental-model-modal-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", closeMentalModelModal);
  }

  const cancelBtn = document.getElementById("mental-model-modal-cancel");
  if (cancelBtn) {
    cancelBtn.addEventListener("click", closeMentalModelModal);
  }

  // Modal save button
  const saveBtn = document.getElementById("mental-model-modal-save");
  if (saveBtn) {
    saveBtn.addEventListener("click", saveMentalModel);
  }

  // Template selection
  const templateSelect = document.getElementById("mental-model-template");
  if (templateSelect) {
    templateSelect.addEventListener("change", (e) => {
      if (e.target.value) {
        applyMentalModelTemplate(e.target.value);
      }
    });
  }

  // Close modal when clicking outside
  const modal = document.getElementById("mental-model-modal");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeMentalModelModal();
      }
    });
  }

  // Mental Models Override modal buttons
  const overrideCloseBtn = document.getElementById(
    "close-mental-models-override-modal",
  );
  if (overrideCloseBtn) {
    overrideCloseBtn.addEventListener("click", closeMentalModelsOverrideModal);
  }

  const overrideCancelBtn = document.getElementById(
    "cancel-mental-models-override-modal",
  );
  if (overrideCancelBtn) {
    overrideCancelBtn.addEventListener("click", closeMentalModelsOverrideModal);
  }

  const overrideSaveBtn = document.getElementById(
    "save-mental-models-override-modal",
  );
  if (overrideSaveBtn) {
    overrideSaveBtn.addEventListener("click", saveMentalModelsOverride);
  }

  // Close override modal when clicking outside
  const overrideModal = document.getElementById("mental-models-override-modal");
  if (overrideModal) {
    overrideModal.addEventListener("click", (e) => {
      if (e.target === overrideModal) {
        closeMentalModelsOverrideModal();
      }
    });
  }

  // ========================================
  // CHAT PANEL INITIALIZATION
  // ========================================

  // Set up overlay event handlers
  setupChatOverlayListeners();

  // Set up sidebar resize functionality
  setupSidebarResize();

  // Set up center resize (conversation pane vs main content)
  setupCenterResizeHandle();

  // Cmd+K / Ctrl+K to focus chat input (unless in CodeMirror editor)
  document.addEventListener("keydown", (e) => {
    const activeElement = document.activeElement;
    const isInEditor =
      activeElement &&
      (activeElement.classList.contains("cm-content") ||
        activeElement.closest(".cm-editor"));

    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      if (!isInEditor) {
        e.preventDefault();
        const chatInput = document.getElementById("chat-input");
        if (chatInput) {
          chatInput.focus();
        }
      }
    }

    // Escape to close overlay
    if (e.key === "Escape") {
      const overlay = document.getElementById("chat-overlay");
      if (overlay && !overlay.classList.contains("hidden")) {
        closeChatOverlay();
      }
    }
  });
});

// ========================================
// CHAT OVERLAY & PANEL SUPPORT
// ========================================

/**
 * Set up chat overlay event listeners (close button, backdrop, expand)
 */
function setupChatOverlayListeners() {
  // Overlay close button
  const overlayCloseBtn = document.getElementById("chat-overlay-close");
  if (overlayCloseBtn) {
    overlayCloseBtn.onclick = function (e) {
      closeChatOverlay();
      e.preventDefault();
    };
  }

  // Overlay backdrop click
  const overlayBackdrop = document.getElementById("chat-overlay-backdrop");
  if (overlayBackdrop) {
    overlayBackdrop.onclick = function (e) {
      if (e.target === overlayBackdrop) {
        closeChatOverlay();
      }
    };
  }

  // Expand button (opens full-screen overlay from sidebar)
  setTimeout(() => {
    const expandBtn = document.getElementById("chat-expand-btn");
    if (expandBtn) {
      expandBtn.onclick = function (e) {
        if (currentConversationId) {
          openChatOverlay(currentConversationId);
        }
        e.preventDefault();
        e.stopPropagation();
        return false;
      };
    }
  }, 500);
}

// ========================================
// CONTEXT-AWARE PERSONA SYSTEM
// ========================================

/**
 * Persona intent patterns mapping
 */
const PERSONA_INTENT_PATTERNS = {
  scribe: {
    name: "Scribe",
    icon: "📝",
    description: "Transform conversations into structured notes",
    patterns: [
      /\b(save|make|take|create|write)\s+(a\s+)?(note|notes)\b/i,
      /\bcapture\s+this\b/i,
      /\bsave\s+(this\s+)?(conversation|chat|discussion)\b/i,
      /\bwrite\s+(this|it)\s+down\b/i,
      /\bnote\s+this\b/i,
      /\bremember\s+this\b/i,
      /\blog\s+this\b/i,
      /\brecord\s+this\b/i,
      /\bdocument\s+(this|our)\b/i,
    ],
  },
  architect: {
    name: "Architect",
    icon: "📐",
    description: "Plan and build complex tasks with structured approach",
    patterns: [
      // Content creation patterns (not learning-related)
      /\b(create|generate|build|write)\s+(a\s+)?(note|document|article|guide|tutorial|blog\s+post|essay|report)\s+(about|on|for)\b/i,
      /\b(draft|outline)\s+(a\s+)?(document|article|blog|essay|report|proposal)\b/i,
      /\bhelp\s+me\s+(write|create|build)\s+(a\s+)?(website|app|script|function|component)\b/i,
      /\bgenerate\s+(content|code|a\s+design)\b/i,
      /\bstructure\s+(a|an|the)\s+(project|codebase|system)\b/i,
      // Avoid learning-related "plan" - exclude learning/teaching contexts
      /\b(plan|outline)\s+(?!.*\b(learn|teach|study|education|curriculum))/i,
    ],
  },
};

/**
 * Detect persona intent from user query
 * @param {string} query - User's message
 * @returns {string|null} - Suggested persona slug or null
 */
function detectPersonaIntent(query) {
  const lowerQuery = query.toLowerCase();

  // Check each persona's patterns
  for (const [personaSlug, personaData] of Object.entries(
    PERSONA_INTENT_PATTERNS,
  )) {
    for (const pattern of personaData.patterns) {
      if (pattern.test(query)) {
        console.log(`[Persona Intent] Detected ${personaSlug} intent:`, query);
        return personaSlug;
      }
    }
  }

  return null;
}

/**
 * Get current active persona
 * @returns {string|null} - Current persona slug or null
 */
function getCurrentPersona() {
  const chatPersonaSelect = document.getElementById("chat-persona-select");
  const personaSelect = document.getElementById("persona-select");

  // Prefer chat panel persona selector
  return chatPersonaSelect?.value || personaSelect?.value || null;
}

/**
 * Show persona switch dialog
 * @param {string} suggestedPersona - Persona to suggest
 * @param {string} query - Original user query
 * @param {Function} onConfirm - Callback if user confirms
 * @param {Function} onCancel - Callback if user cancels
 */
function showPersonaSwitchDialog(suggestedPersona, query, onConfirm, onCancel) {
  const personaData = PERSONA_INTENT_PATTERNS[suggestedPersona];
  if (!personaData) return;

  // Create dialog overlay
  const dialogHTML = `
    <div id="persona-switch-dialog" class="persona-switch-overlay">
      <div class="persona-switch-dialog">
        <div class="persona-switch-header">
          <span class="persona-switch-icon">${personaData.icon}</span>
          <h3>Switch to ${personaData.name}?</h3>
        </div>
        <div class="persona-switch-body">
          <p class="persona-switch-message">
            This task works best with <strong>${personaData.name}</strong> persona.
          </p>
          <p class="persona-switch-description">
            ${personaData.description}
          </p>
          <div class="persona-switch-query">
            <strong>Your request:</strong> "${query}"
          </div>
        </div>
        <div class="persona-switch-actions">
          <button id="persona-switch-cancel" class="persona-switch-btn persona-switch-btn-secondary">
            <i data-lucide="x"></i>
            Keep Current
          </button>
          <button id="persona-switch-confirm" class="persona-switch-btn persona-switch-btn-primary">
            <i data-lucide="check"></i>
            Switch to ${personaData.name}
          </button>
        </div>
      </div>
    </div>
  `;

  // Add to DOM
  document.body.insertAdjacentHTML("beforeend", dialogHTML);

  // Initialize lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Attach event handlers
  const dialog = document.getElementById("persona-switch-dialog");
  const confirmBtn = document.getElementById("persona-switch-confirm");
  const cancelBtn = document.getElementById("persona-switch-cancel");

  confirmBtn.onclick = () => {
    dialog.remove();
    onConfirm();
  };

  cancelBtn.onclick = () => {
    dialog.remove();
    onCancel();
  };

  // Close on overlay click
  dialog.onclick = (e) => {
    if (e.target === dialog) {
      dialog.remove();
      onCancel();
    }
  };

  // Close on Escape
  const escapeHandler = (e) => {
    if (e.key === "Escape") {
      dialog.remove();
      onCancel();
      document.removeEventListener("keydown", escapeHandler);
    }
  };
  document.addEventListener("keydown", escapeHandler);

  console.log("[Persona Switch Dialog] Shown for:", suggestedPersona);
}

/**
 * Switch to a persona
 * @param {string} personaSlug - Persona to switch to
 * @returns {Promise<boolean>} - Success status
 */
async function switchToPersona(personaSlug) {
  try {
    const personaSelect = document.getElementById("persona-select");
    const chatPersonaSelect = document.getElementById("chat-persona-select");

    if (!personaSelect && !chatPersonaSelect) return false;

    // Update persona selects and trigger activation
    if (personaSelect) {
      personaSelect.value = personaSlug;
      const event = new Event("change", { bubbles: true });
      personaSelect.dispatchEvent(event);
    }

    if (chatPersonaSelect) {
      chatPersonaSelect.value = personaSlug;
    }

    console.log("[Persona Switch] Switched to:", personaSlug);
    return true;
  } catch (error) {
    console.error("[Persona Switch] Error:", error);
    return false;
  }
}

/**
 * Check if current persona can handle the task based on their mode
 * @param {string} currentPersona - Current persona slug
 * @param {string} suggestedPersona - Suggested persona slug
 * @param {string} query - User query
 * @returns {boolean} - True if current persona can handle it
 */
function canCurrentPersonaHandle(currentPersona, suggestedPersona, query) {
  // If no suggestion or same persona, proceed
  if (!suggestedPersona || currentPersona === suggestedPersona) {
    return true;
  }

  // Professor in curriculum mode can handle learning plans (don't switch to Architect)
  if (currentPersona === "professor" && suggestedPersona === "architect") {
    const lowerQuery = query.toLowerCase();

    // Check if this is a learning/teaching request
    const isLearningRequest =
      /\b(learning|teaching|study|education|curriculum|lesson)\s+(plan|path|guide|roadmap)\b/i.test(
        query,
      ) ||
      /\b(teach|learn|study|master)\b.*\b(how to|about)\b/i.test(query) ||
      /\bplan\s+to\s+(learn|study|teach)\b/i.test(query);

    if (isLearningRequest) {
      console.log(
        "[Persona Intent] Professor curriculum mode can handle this learning plan",
      );
      return true;
    }
  }

  // Professor in explain mode can handle content creation about teaching topics
  if (currentPersona === "professor" && suggestedPersona === "architect") {
    const lowerQuery = query.toLowerCase();

    // Check if this is about explaining or teaching
    const isTeachingContent =
      /\b(explain|teach|show|demonstrate)\b/i.test(query) ||
      /\bhow\s+(does|do|to)\b/i.test(query) ||
      /\bwhat\s+is\b/i.test(query);

    if (isTeachingContent) {
      console.log("[Persona Intent] Professor can handle this explanation");
      return true;
    }
  }

  return false;
}

/**
 * Check if persona switch is needed and handle it
 * @param {string} query - User query
 * @param {Function} proceedCallback - Function to call after handling persona switch
 */
async function checkAndHandlePersonaSwitch(query, proceedCallback) {
  const currentPersona = getCurrentPersona();
  const suggestedPersona = detectPersonaIntent(query);

  // Check if current persona can handle this
  if (canCurrentPersonaHandle(currentPersona, suggestedPersona, query)) {
    proceedCallback();
    return;
  }

  console.log(
    "[Persona Intent] Current:",
    currentPersona,
    "| Suggested:",
    suggestedPersona,
  );

  // Show dialog
  showPersonaSwitchDialog(
    suggestedPersona,
    query,
    async () => {
      // User confirmed switch
      const success = await switchToPersona(suggestedPersona);
      if (success) {
        // Wait a bit for persona to activate
        setTimeout(() => {
          proceedCallback();
        }, 500);
      } else {
        // Switch failed, proceed anyway
        proceedCallback();
      }
    },
    () => {
      // User cancelled, proceed with current persona
      console.log("[Persona Switch] User chose to keep current persona");
      proceedCallback();
    },
  );
}

/**
 * Open chat overlay with conversation
 */
async function openChatOverlay(conversationId) {
  const overlay = document.getElementById("chat-overlay");
  const titleEl = document.getElementById("chat-overlay-conversation-title");
  const messagesContainer = document.getElementById("chat-overlay-messages");

  if (!overlay) return;

  // Load conversation if not current
  if (conversationId !== currentConversationId) {
    await switchToConversation(conversationId);
  }

  // Set title
  if (titleEl && currentConversation) {
    titleEl.textContent = currentConversation.title || "Conversation";
  }

  // Clear and render messages
  if (messagesContainer) {
    messagesContainer.innerHTML = "";

    if (currentConversation && currentConversation.messages) {
      currentConversation.messages.forEach((msg) => {
        if (msg.role !== "system") {
          const formattedContent =
            msg.role === "assistant"
              ? formatResponse(msg.content)
              : msg.content;
          addMessageToOverlay(msg.role, formattedContent);
        }
      });
    }

    // Scroll to bottom
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 50);
  }

  // Show overlay
  overlay.classList.remove("hidden");

  console.log(
    "[Chat] Overlay opened for conversation:",
    conversationId,
  );
}

/**
 * Close chat overlay
 */
function closeChatOverlay() {
  const overlay = document.getElementById("chat-overlay");
  if (overlay) {
    overlay.classList.add("hidden");
    console.log("[Chat] Overlay closed");
  }
}

/**
 * Add message to overlay
 */
function addMessageToOverlay(role, content) {
  const messagesContainer = document.getElementById("chat-overlay-messages");
  if (!messagesContainer) return null;

  const messageId =
    "overlay-msg-" + Date.now() + "-" + Math.random().toString(36).substr(2, 9);
  const timestamp = new Date();

  const messageEl = document.createElement("div");
  messageEl.className = `message ${role}`;
  messageEl.id = messageId;
  messageEl.dataset.timestamp = timestamp.toISOString();
  messageEl.innerHTML = `
    <div class="message-content">
      ${content}
    </div>
    <div class="message-timestamp" title="${timestamp.toLocaleString()}">${getRelativeTime(timestamp)}</div>
  `;

  messagesContainer.appendChild(messageEl);

  // Re-initialize icons if any were added
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 0);
  }

  // Smooth scroll to bottom
  requestAnimationFrame(() => {
    messagesContainer.scrollTo({
      top: messagesContainer.scrollHeight,
      behavior: "smooth",
    });
  });

  return messageId;
}

/**
 * Remove message from overlay
 */
function removeMessageFromOverlay(messageId) {
  const messageEl = document.getElementById(messageId);
  if (messageEl) {
    messageEl.remove();
  }
}

// ========================================
// SIDEBAR RESIZE FUNCTIONALITY
// ========================================

/**
 * Set up sidebar resize functionality
 */
function setupSidebarResize() {
  console.log("[Sidebar Resize] Setting up...");

  // Use setTimeout to ensure DOM is fully ready
  setTimeout(() => {
    const resizeHandle = document.getElementById("sidebar-resize-handle");
    const conversationsSection = document.getElementById(
      "chat-conversations-section",
    );
    const activeChatSection = document.getElementById("chat-active-section");

    console.log("[Sidebar Resize] Elements found:", {
      resizeHandle: !!resizeHandle,
      conversationsSection: !!conversationsSection,
      activeChatSection: !!activeChatSection,
    });

    if (!resizeHandle || !conversationsSection || !activeChatSection) {
      console.error("[Sidebar Resize] Required elements not found!");
      return;
    }

    let isResizing = false;
    let startY = 0;
    let startHeight = 0;

    // Load saved height from localStorage
    const savedHeight = localStorage.getItem("conversations-section-height");
    if (savedHeight) {
      console.log("[Sidebar Resize] Loading saved height:", savedHeight);
      conversationsSection.style.maxHeight = savedHeight + "px";
      conversationsSection.style.height = savedHeight + "px";
    }

    // Use direct property assignment instead of addEventListener (works better in Electron)
    resizeHandle.onmousedown = function (e) {
      console.log("[Sidebar Resize] Mouse down - starting resize");
      isResizing = true;
      startY = e.clientY;
      startHeight = conversationsSection.offsetHeight;

      resizeHandle.classList.add("dragging");
      document.body.style.cursor = "ns-resize";
      document.body.style.userSelect = "none";

      e.preventDefault();
      e.stopPropagation();
      return false;
    };

    // Mouse move - perform resize
    document.onmousemove = function (e) {
      if (!isResizing) return;

      const deltaY = e.clientY - startY;
      const newHeight = startHeight + deltaY;

      // Enforce min/max constraints
      const minHeight = 150; // Minimum height for conversations section
      const maxHeight = window.innerHeight - 400; // Leave space for active chat
      const clampedHeight = Math.max(minHeight, Math.min(newHeight, maxHeight));

      conversationsSection.style.maxHeight = clampedHeight + "px";
      conversationsSection.style.height = clampedHeight + "px";

      e.preventDefault();
      return false;
    };

    // Mouse up - end resize
    document.onmouseup = function (e) {
      if (!isResizing) return;

      console.log("[Sidebar Resize] Mouse up - ending resize");
      isResizing = false;
      resizeHandle.classList.remove("dragging");
      document.body.style.cursor = "";
      document.body.style.userSelect = "";

      // Save height to localStorage
      const currentHeight = conversationsSection.offsetHeight;
      localStorage.setItem("conversations-section-height", currentHeight);

      console.log("[Sidebar Resize] Saved height:", currentHeight);
    };

    console.log("[Sidebar Resize] Initialized successfully");
  }, 500); // Wait 500ms to ensure DOM is ready
}

const AGENTS_SIDEBAR_WIDTH = 280;
const LEFT_SIDEBAR_WIDTH = 280;

/**
 * Compute max chat panel width so agents sidebar stays visible.
 * Reserves: left sidebar, main min-width (400), handle (4), agents sidebar.
 * @param {Object} overrides - Optional { agentsWidth, leftWidth } when expanding (avoids measuring during CSS transition)
 */
function getMaxChatPanelWidth(overrides = {}) {
  const layout = document.querySelector(".three-column-layout");
  const leftSidebar = document.getElementById("left-sidebar");
  const agentsSidebar = document.getElementById("agents-sidebar");
  if (!layout || !leftSidebar || !agentsSidebar) return 800;
  const layoutWidth = layout.offsetWidth;
  const leftWidth =
    overrides.leftWidth ?? leftSidebar.offsetWidth ?? 0;
  const agentsWidth =
    overrides.agentsWidth ?? agentsSidebar.offsetWidth ?? 0;
  const mainMin = 400;
  const handleWidth = 4;
  return Math.max(300, layoutWidth - leftWidth - agentsWidth - mainMin - handleWidth);
}

/**
 * Clamp chat panel to current max width (e.g. after sidebar expand).
 * Call when left or right sidebar is toggled to expand.
 * Uses known sidebar widths when expanding to avoid measuring during CSS transition.
 */
function clampChatPanelToMax(expandingRight = false, expandingLeft = false) {
  const chatPanel = document.getElementById("chat-panel");
  if (!chatPanel) return;
  const overrides = {};
  if (expandingRight) overrides.agentsWidth = AGENTS_SIDEBAR_WIDTH;
  if (expandingLeft) overrides.leftWidth = LEFT_SIDEBAR_WIDTH;
  const maxWidth = getMaxChatPanelWidth(overrides);
  const currentWidth = chatPanel.offsetWidth;
  if (currentWidth > maxWidth) {
    chatPanel.style.width = maxWidth + "px";
    chatPanel.style.flex = "0 0 " + maxWidth + "px";
    localStorage.setItem("chat-panel-width", String(maxWidth));
  }
}

/**
 * Set up center resize handle (between main content and chat panel)
 */
function setupCenterResizeHandle() {
  setTimeout(() => {
    const resizeHandle = document.getElementById("center-resize-handle");
    const chatPanel = document.getElementById("chat-panel");
    const mainContent = document.getElementById("main-content-area");

    if (!resizeHandle || !chatPanel || !mainContent) return;

    let isResizing = false;
    let startX = 0;
    let startWidth = 0;

    const minWidth = 300;

    const savedWidth = localStorage.getItem("chat-panel-width");
    if (savedWidth) {
      const w = parseInt(savedWidth, 10);
      const maxW = getMaxChatPanelWidth();
      if (w >= minWidth && w <= maxW) {
        chatPanel.style.width = w + "px";
        chatPanel.style.flex = "0 0 " + w + "px";
      }
    }

    const onMouseMove = (e) => {
      if (!isResizing) return;
      const deltaX = e.clientX - startX;
      // Handle is at left edge of chat panel. Drag right = chat panel narrower.
      const newWidth = startWidth - deltaX;
      const maxWidth = getMaxChatPanelWidth();
      const clamped = Math.max(minWidth, Math.min(newWidth, maxWidth));
      chatPanel.style.width = clamped + "px";
      chatPanel.style.flex = "0 0 " + clamped + "px";
      e.preventDefault();
      e.stopPropagation();
    };

    const onMouseUp = () => {
      if (!isResizing) return;
      isResizing = false;
      resizeHandle.classList.remove("dragging");
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
      const w = chatPanel.offsetWidth;
      localStorage.setItem("chat-panel-width", String(w));
    };

    resizeHandle.onmousedown = (e) => {
      isResizing = true;
      startX = e.clientX;
      startWidth = chatPanel.offsetWidth;
      resizeHandle.classList.add("dragging");
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
      document.addEventListener("mousemove", onMouseMove);
      document.addEventListener("mouseup", onMouseUp);
      e.preventDefault();
    };
  }, 500);
}

// ========================================
// STRUCTURED INPUT BUILDER (Phase 2)
// ========================================
// TODO: Implement structured input system for quick actions

// ========================================
// LEARNING VISUALIZATION TOOLS
// ========================================

/**
 * Render Mermaid diagram in session content
 */
async function renderDiagram(data) {
  console.log("[Learning] Rendering diagram:", data);

  const sessionContent = document.getElementById("session-content");
  const learningSession = document.getElementById("learning-session");
  const learningDashboard = document.getElementById("learning-dashboard");

  if (!sessionContent) {
    console.error("[Learning] Session content area not found");
    return;
  }

  // Switch to session view if not already
  if (learningSession && learningSession.classList.contains("hidden")) {
    learningDashboard?.classList.add("hidden");
    learningSession.classList.remove("hidden");
  }

  // Update session header
  const sessionHeader = document.getElementById("session-topic");
  if (sessionHeader && data.caption) {
    sessionHeader.textContent = data.caption;
  }

  // Create diagram container
  const diagramId = `mermaid-${Date.now()}`;
  const diagramContainer = document.createElement("div");
  diagramContainer.className = "diagram-container";
  diagramContainer.innerHTML = `
    <div class="diagram-wrapper" id="${diagramId}">
      ${data.source}
    </div>
    ${data.caption ? `<div class="diagram-caption">${data.caption}</div>` : ""}
  `;

  // Add to session content
  sessionContent.appendChild(diagramContainer);

  // Initialize Mermaid and render
  if (typeof mermaid !== "undefined") {
    try {
      mermaid.initialize({
        startOnLoad: false,
        theme: "dark",
        themeVariables: {
          primaryColor: "#00d9ff",
          primaryTextColor: "#e0e0e0",
          primaryBorderColor: "#00d9ff",
          lineColor: "#666",
          secondaryColor: "#2a2a2a",
          tertiaryColor: "#1a1a1a",
          background: "#151515",
          mainBkg: "#1a1a1a",
          textColor: "#e0e0e0",
          fontSize: "14px",
        },
      });

      const element = document.getElementById(diagramId);
      if (element) {
        await mermaid.run({ nodes: [element] });
        console.log("[Learning] Diagram rendered successfully");

        // Add interactive controls if enabled
        if (data.interactive) {
          addDiagramControls(diagramContainer);
        }
      }
    } catch (error) {
      console.error("[Learning] Error rendering diagram:", error);
      diagramContainer.innerHTML = `
        <div class="diagram-error">
          <p>Error rendering diagram</p>
          <pre>${error.message}</pre>
        </div>
      `;
    }
  } else {
    console.error("[Learning] Mermaid library not loaded");
  }

  // Scroll to bottom
  sessionContent.scrollTop = sessionContent.scrollHeight;
}

/**
 * Add zoom/pan controls to diagram
 */
function addDiagramControls(container) {
  const controls = document.createElement("div");
  controls.className = "diagram-controls";
  controls.innerHTML = `
    <button class="diagram-btn" data-action="zoom-in" title="Zoom In">
      <i data-lucide="zoom-in" style="width: 14px; height: 14px;"></i>
    </button>
    <button class="diagram-btn" data-action="zoom-out" title="Zoom Out">
      <i data-lucide="zoom-out" style="width: 14px; height: 14px;"></i>
    </button>
    <button class="diagram-btn" data-action="reset" title="Reset View">
      <i data-lucide="maximize-2" style="width: 14px; height: 14px;"></i>
    </button>
  `;

  container.prepend(controls);

  // Initialize Lucide icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  // Add event listeners
  let scale = 1;
  const wrapper = container.querySelector(".diagram-wrapper");

  controls.addEventListener("click", (e) => {
    const btn = e.target.closest(".diagram-btn");
    if (!btn) return;

    const action = btn.dataset.action;

    if (action === "zoom-in") {
      scale = Math.min(scale + 0.1, 2);
    } else if (action === "zoom-out") {
      scale = Math.max(scale - 0.1, 0.5);
    } else if (action === "reset") {
      scale = 1;
    }

    if (wrapper) {
      wrapper.style.transform = `scale(${scale})`;
    }
  });
}

/**
 * Execute code in sandbox and display results
 */
async function executeCodeInSandbox(data) {
  console.log("[Learning] Executing code:", data);

  const sessionContent = document.getElementById("session-content");
  if (!sessionContent) {
    console.error("[Learning] Session content area not found");
    return;
  }

  // Create code execution container
  const execId = `code-exec-${Date.now()}`;
  const execContainer = document.createElement("div");
  execContainer.className = "code-execution-container";
  execContainer.id = execId;

  // Build HTML
  let html = '<div class="code-exec-header">';
  html += `<span class="code-exec-lang">${data.language}</span>`;
  html += '<div class="code-exec-actions">';
  if (data.editable) {
    html +=
      '<button class="btn btn-sm btn-secondary" onclick="runCode(\'' +
      execId +
      "')\">▶ Run</button>";
  }
  html += "</div>";
  html += "</div>";

  // Code editor
  html += '<div class="code-editor">';
  html += `<pre><code class="language-${data.language}">${escapeHtml(data.code)}</code></pre>`;
  html += "</div>";

  // Output area
  html += '<div class="code-output" id="' + execId + '-output">';
  html += '<div class="output-label">Output:</div>';
  html += '<div class="output-content"></div>';
  html += "</div>";

  // Test results if provided
  if (data.test_cases && data.test_cases.length > 0) {
    html += '<div class="code-tests" id="' + execId + '-tests"></div>';
  }

  execContainer.innerHTML = html;
  sessionContent.appendChild(execContainer);

  // If editable, make code textarea
  if (data.editable) {
    const codeElement = execContainer.querySelector(".code-editor pre code");
    const textarea = document.createElement("textarea");
    textarea.className = "code-textarea";
    textarea.value = data.code;
    textarea.spellcheck = false;
    codeElement.replaceWith(textarea);

    // Store test cases on container for later
    execContainer.dataset.testCases = JSON.stringify(data.test_cases || []);
    execContainer.dataset.language = data.language;
  } else {
    // Auto-run if not editable
    await runCodeExecution(execId, data.code, data.language, data.test_cases);
  }

  // Scroll to bottom
  sessionContent.scrollTop = sessionContent.scrollHeight;
}

/**
 * Run code execution (called by button or auto)
 */
async function runCode(execId) {
  const container = document.getElementById(execId);
  if (!container) return;

  const textarea = container.querySelector(".code-textarea");
  const code = textarea ? textarea.value : "";
  const language = container.dataset.language || "python";
  const testCases = JSON.parse(container.dataset.testCases || "[]");

  await runCodeExecution(execId, code, language, testCases);
}

/**
 * Actually execute code and display results
 */
async function runCodeExecution(execId, code, language, testCases) {
  const outputContent = document.querySelector(
    `#${execId}-output .output-content`,
  );
  const testsDiv = document.getElementById(`${execId}-tests`);

  if (!outputContent) return;

  outputContent.innerHTML =
    '<div class="loading-spinner"></div><span>Running...</span>';

  try {
    let result;

    if (language === "javascript") {
      // JavaScript sandbox
      result = await runJavaScript(code);
    } else if (language === "python") {
      // Python sandbox (requires Pyodide - we'll add this next)
      result = await runPython(code);
    } else {
      throw new Error(`Unsupported language: ${language}`);
    }

    // Display output
    outputContent.innerHTML = `<pre>${escapeHtml(result.output)}</pre>`;

    if (result.error) {
      outputContent.innerHTML += `<div class="output-error">${escapeHtml(result.error)}</div>`;
    }

    // Run test cases
    if (testsDiv && testCases && testCases.length > 0) {
      await runTestCases(testsDiv, code, language, testCases);
    }
  } catch (error) {
    outputContent.innerHTML = `<div class="output-error">Error: ${escapeHtml(error.message)}</div>`;
  }
}

/**
 * Run JavaScript code in sandbox
 */
async function runJavaScript(code) {
  let output = "";
  let error = null;

  // Capture console.log
  const originalLog = console.log;
  console.log = (...args) => {
    output += args.map((a) => String(a)).join(" ") + "\n";
  };

  try {
    // Execute in isolated scope
    const result = eval(code);
    if (result !== undefined) {
      output += String(result);
    }
  } catch (e) {
    error = e.message;
  } finally {
    console.log = originalLog;
  }

  return { output, error };
}

/**
 * Run Python code in Pyodide sandbox
 * Phase 23.5: Security Hardening - Uses Pyodide for secure execution
 */
async function runPython(code) {
  return await runPythonInSandbox(code, 10); // Default 10 second timeout
}

/**
 * Run Python code in Pyodide sandbox with timeout
 * Phase 23.5: Security Hardening
 *
 * @param {string} code - Python code to execute
 * @param {number} timeout - Timeout in seconds (default: 10)
 * @returns {Promise<Object>} Execution result with status, output, error
 */
async function runPythonInSandbox(code, timeout = 10) {
  try {
    // Load Pyodide using our loader
    if (typeof window.PyodideLoader === "undefined") {
      throw new Error(
        "PyodideLoader not available. Make sure pyodide-loader.js is loaded.",
      );
    }

    const pyodide = await window.PyodideLoader.loadPyodide();

    // Capture stdout and stderr
    let stdout = "";
    let stderr = "";

    pyodide.setStdout({
      batched: (msg) => {
        stdout += msg;
      },
      raw: (charCode) => {
        stdout += String.fromCharCode(charCode);
      },
    });

    pyodide.setStderr({
      batched: (msg) => {
        stderr += msg;
      },
      raw: (charCode) => {
        stderr += String.fromCharCode(charCode);
      },
    });

    // Set up timeout
    const startTime = performance.now();
    let timeoutId;
    const timeoutPromise = new Promise((_, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error(`Code execution timed out after ${timeout} seconds`));
      }, timeout * 1000);
    });

    // Execute code with timeout
    try {
      await Promise.race([pyodide.runPythonAsync(code), timeoutPromise]);

      clearTimeout(timeoutId);
      const executionTime = (performance.now() - startTime) / 1000;

      return {
        status: "success",
        output: stdout.trim() || "(no output)",
        error: stderr.trim() || null,
        execution_time: executionTime,
      };
    } catch (execError) {
      clearTimeout(timeoutId);

      // Check if it's a timeout
      if (execError.message && execError.message.includes("timed out")) {
        return {
          status: "timeout",
          error: execError.message,
          output: stdout.trim() || "",
          execution_time: timeout,
        };
      }

      // Regular error
      return {
        status: "error",
        output: stdout.trim() || "",
        error: execError.message || String(execError) || stderr.trim(),
        execution_time: (performance.now() - startTime) / 1000,
      };
    }
  } catch (error) {
    return {
      output: "",
      error: error.message,
    };
  }
}

/**
 * Run test cases and display results
 */
async function runTestCases(testsDiv, code, language, testCases) {
  testsDiv.innerHTML = '<div class="tests-header">Test Results:</div>';

  for (const test of testCases) {
    const testDiv = document.createElement("div");
    testDiv.className = "test-case";

    try {
      // Run test (simplified - real implementation would be more robust)
      let result;
      if (language === "javascript") {
        result = await runJavaScript(test.input);
      }

      const passed = result.output.trim() === test.expected;

      testDiv.className += passed ? " test-pass" : " test-fail";
      testDiv.innerHTML = `
        <div class="test-status">${passed ? "✓" : "✗"}</div>
        <div class="test-details">
          <div class="test-input">Input: <code>${escapeHtml(test.input)}</code></div>
          <div class="test-expected">Expected: <code>${escapeHtml(test.expected)}</code></div>
          ${!passed ? `<div class="test-actual">Got: <code>${escapeHtml(result.output.trim())}</code></div>` : ""}
        </div>
      `;
    } catch (error) {
      testDiv.className += " test-fail";
      testDiv.innerHTML = `
        <div class="test-status">✗</div>
        <div class="test-details">
          <div class="test-error">Error: ${escapeHtml(error.message)}</div>
        </div>
      `;
    }

    testsDiv.appendChild(testDiv);
  }
}

/**
 * Present interactive exercise
 */
async function presentExercise(data) {
  console.log("[Learning] Presenting exercise:", data);

  const sessionContent = document.getElementById("session-content");
  if (!sessionContent) {
    console.error("[Learning] Session content area not found");
    return;
  }

  // Switch to session view
  const learningSession = document.getElementById("learning-session");
  const learningDashboard = document.getElementById("learning-dashboard");

  if (learningSession && learningSession.classList.contains("hidden")) {
    learningDashboard?.classList.add("hidden");
    learningSession.classList.remove("hidden");
  }

  // Update session header
  const sessionHeader = document.getElementById("session-topic");
  if (sessionHeader && data.title) {
    sessionHeader.textContent = data.title;
  }

  // Create exercise container
  const exerciseId = `exercise-${Date.now()}`;
  const exerciseContainer = document.createElement("div");
  exerciseContainer.className = "exercise-container";
  exerciseContainer.id = exerciseId;

  let html = '<div class="exercise-header">';
  html += `<h3>${data.title}</h3>`;
  html += `<span class="exercise-difficulty ${data.difficulty}">${data.difficulty || "medium"}</span>`;
  html += "</div>";

  html += '<div class="exercise-description">';
  html += data.description;
  html += "</div>";

  // Exercise type specific UI
  if (data.type === "code_challenge") {
    html += '<div class="exercise-code">';
    html += "<label>Your Solution:</label>";
    html += `<textarea class="code-textarea" spellcheck="false">${data.starter_code || ""}</textarea>`;
    html += "</div>";

    html += '<div class="exercise-actions">';
    html += `<button class="btn btn-primary" onclick="checkExerciseSolution('${exerciseId}')">Check Solution</button>`;
    if (data.hints && data.hints.length > 0) {
      html += `<button class="btn btn-secondary" onclick="showExerciseHint('${exerciseId}', 0)">Show Hint</button>`;
    }
    html += "</div>";

    html +=
      '<div class="exercise-feedback" id="' + exerciseId + '-feedback"></div>';

    // Store data on container
    exerciseContainer.dataset.exerciseData = JSON.stringify(data);
  }

  exerciseContainer.innerHTML = html;
  sessionContent.appendChild(exerciseContainer);

  // Scroll to bottom
  sessionContent.scrollTop = sessionContent.scrollHeight;
}

/**
 * Check exercise solution
 */
async function checkExerciseSolution(exerciseId) {
  const container = document.getElementById(exerciseId);
  if (!container) return;

  const textarea = container.querySelector(".code-textarea");
  const userCode = textarea ? textarea.value : "";
  const data = JSON.parse(container.dataset.exerciseData || "{}");

  const feedback = document.getElementById(`${exerciseId}-feedback`);
  feedback.innerHTML =
    '<div class="loading-spinner"></div><span>Checking...</span>';

  try {
    // Run test cases
    const results = [];

    for (const testCase of data.test_cases || []) {
      const result = await runJavaScript(userCode + "\n" + testCase.input);
      const passed = result.output.trim() === testCase.output;
      results.push({ testCase, result, passed });
    }

    const allPassed = results.every((r) => r.passed);

    // Display feedback
    let html =
      '<div class="feedback-header ' +
      (allPassed ? "feedback-success" : "feedback-error") +
      '">';
    html += allPassed ? "✓ All tests passed!" : "✗ Some tests failed";
    html += "</div>";

    html += '<div class="feedback-tests">';
    for (const r of results) {
      html += `<div class="feedback-test ${r.passed ? "test-pass" : "test-fail"}">`;
      html += `<div class="test-status">${r.passed ? "✓" : "✗"}</div>`;
      html += `<div class="test-info">${r.testCase.input}</div>`;
      html += "</div>";
    }
    html += "</div>";

    if (allPassed) {
      html +=
        '<div class="feedback-success-message">Great job! You solved it correctly.</div>';

      // Update mastery in backend
      await updateExerciseMastery(data.exercise_id, true);
    }

    feedback.innerHTML = html;
  } catch (error) {
    feedback.innerHTML = `<div class="feedback-error">Error checking solution: ${error.message}</div>`;
  }
}

/**
 * Show exercise hint
 */
function showExerciseHint(exerciseId, hintIndex) {
  const container = document.getElementById(exerciseId);
  if (!container) return;

  const data = JSON.parse(container.dataset.exerciseData || "{}");
  const hints = data.hints || [];

  if (hintIndex >= hints.length) return;

  const feedback = document.getElementById(`${exerciseId}-feedback`);
  const hint = hints[hintIndex];

  let html = '<div class="feedback-hint">';
  html += `<strong>Hint ${hintIndex + 1}:</strong> ${hint}`;
  html += "</div>";

  if (hintIndex + 1 < hints.length) {
    html += `<button class="btn btn-sm btn-secondary" onclick="showExerciseHint('${exerciseId}', ${hintIndex + 1})">Show Next Hint</button>`;
  }

  feedback.innerHTML = html;
}

/**
 * Update exercise mastery in backend
 */
async function updateExerciseMastery(exerciseId, success) {
  try {
    await fetch(`${API_URL}/polly/learning/exercise-result`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        exercise_id: exerciseId,
        success: success,
        timestamp: new Date().toISOString(),
      }),
    });

    // Reload stats
    await loadLearningStats();
  } catch (error) {
    console.error("[Learning] Error updating mastery:", error);
  }
}

/**
 * Escape HTML for safe display
 */
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// ========================================
// LEARNING PAGE (Phase 22 - Teaching Mode)
// ========================================

let learningConversationId = null;

/**
 * Initialize Learning page
 */
async function initLearningPage() {
  console.log("[Learning] Initializing Learning page");

  // Auto-select Professor persona in chat float
  selectProfessorPersona();

  // Load learning stats and dashboard
  await loadLearningStats();
  await loadReviewTopics();
  await loadRecentLearningNotes();

  // Setup event listeners
  setupLearningEventListeners();

  // Initialize Lucide icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

/**
 * Setup event listeners for Learning page
 */
function setupLearningEventListeners() {
  // Refresh stats button
  const refreshBtn = document.getElementById("btn-refresh-stats");
  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => loadLearningStats());
  }

  // Open chat button - opens chat with Socratic mode ready
  const openChatBtn = document.getElementById("btn-open-chat");
  if (openChatBtn) {
    openChatBtn.addEventListener("click", () => {
      // Auto-select Professor persona
      selectProfessorPersona();

      // Pre-fill right-panel chat input with /socratic prefix and focus
      const input = document.getElementById("chat-input");
      if (input) {
        input.value = "/socratic ";
        input.focus();
        // Place cursor at end
        input.setSelectionRange(input.value.length, input.value.length);
      }
    });
  }

  // End session button
  const endSessionBtn = document.getElementById("btn-end-session");
  if (endSessionBtn) {
    endSessionBtn.addEventListener("click", () => {
      // Return to dashboard view
      document.getElementById("learning-dashboard")?.classList.remove("hidden");
      document.getElementById("learning-session")?.classList.add("hidden");
    });
  }
}

/**
 * Auto-select Professor persona in chat panel
 */
function selectProfessorPersona() {
  // Select Professor in persona selectors
  const chatPersonaSelect = document.getElementById("chat-persona-select");
  const mainPersonaSelect = document.getElementById("persona-select");

  if (chatPersonaSelect) {
    chatPersonaSelect.value = "professor";
    // Trigger change event to update modes
    chatPersonaSelect.dispatchEvent(new Event("change"));
  } else if (mainPersonaSelect) {
    mainPersonaSelect.value = "professor";
    mainPersonaSelect.dispatchEvent(new Event("change"));
  }

  console.log("[Learning] Professor persona auto-selected");
}

/**
 * Load learning statistics
 */
async function loadLearningStats() {
  try {
    const response = await fetch(`${API_URL}/polly/learning/stats`);

    if (!response.ok) {
      throw new Error("Failed to load learning stats");
    }

    const stats = await response.json();

    // Update UI
    updateLearningStatsUI(stats);
  } catch (error) {
    console.error("[Learning] Error loading stats:", error);
    // Show placeholder data
    updateLearningStatsUI({
      total_topics: 0,
      topics_needing_review: 0,
      by_mastery: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
    });
  }
}

/**
 * Update topics list UI (used by topics browser sidebar panel)
 */
function updateTopicsUI(topics) {
  const topicsContent = document.getElementById("topics-browser-list");
  if (!topicsContent) return;

  if (topics.length === 0) {
    topicsContent.innerHTML =
      '<p class="no-topics">No topics yet. Start learning!</p>';
    return;
  }

  topicsContent.innerHTML = topics
    .map(
      (topic) => `
    <div class="topic-card" data-topic="${escapeHtml(topic.title)}">
      <div class="topic-header">
        <span class="topic-name">${escapeHtml(topic.title)}</span>
        <span class="mastery-badge mastery-${topic.mastery_level}">L${topic.mastery_level}</span>
      </div>
      <div class="topic-meta">
        <span class="topic-domain">${escapeHtml(topic.domain || "General")}</span>
        <span class="topic-updated">${formatDate(topic.last_reviewed)}</span>
      </div>
    </div>
  `,
    )
    .join("");

  // Add click handlers for topic cards
  topicsContent.querySelectorAll(".topic-card").forEach((card) => {
    card.addEventListener("click", () => {
      const topicTitle = card.dataset.topic;
      startTopicReview(topicTitle);
    });
  });
}

/**
 * Format date for display
 */
function formatDate(dateString) {
  if (!dateString) return "Never";
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
}

/**
 * Update learning stats UI
 */
function updateLearningStatsUI(stats) {
  // Update total topics
  const totalEl = document.getElementById("stat-total-topics");
  if (totalEl) {
    totalEl.textContent = stats.total_topics || 0;
  }

  // Update review count
  const reviewEl = document.getElementById("stat-review-count");
  if (reviewEl) {
    reviewEl.textContent = stats.topics_needing_review || 0;

    // Show/hide review section
    const reviewSection = document.getElementById("review-section");
    if (reviewSection) {
      if (stats.topics_needing_review > 0) {
        reviewSection.style.display = "block";
      } else {
        reviewSection.style.display = "none";
      }
    }
  }

  // Update mastery breakdown
  const masteryBarsEl = document.getElementById("mastery-bars");
  if (masteryBarsEl && stats.by_mastery) {
    const masteryLabels = {
      1: "Introduced",
      2: "Learning",
      3: "Understood",
      4: "Proficient",
      5: "Mastered",
    };

    const total = stats.total_topics || 1; // Avoid division by zero

    masteryBarsEl.innerHTML = "";

    for (let level = 1; level <= 5; level++) {
      const count = stats.by_mastery[level] || 0;
      const percentage = total > 0 ? (count / total) * 100 : 0;

      const barDiv = document.createElement("div");
      barDiv.className = "mastery-bar";
      barDiv.innerHTML = `
        <div class="mastery-bar-label">${masteryLabels[level]}</div>
        <div class="mastery-bar-fill">
          <div class="mastery-bar-progress mastery-${level}" style="width: ${percentage}%"></div>
        </div>
        <div class="mastery-bar-count">${count}</div>
      `;

      masteryBarsEl.appendChild(barDiv);
    }
  }

  console.log("[Learning] Stats updated:", stats);
}

/**
 * Show learning note creation modal
 */
function showLearningNoteModal(data) {
  const { topic, domain, concepts } = data;

  // Create modal HTML if it doesn't exist
  let modal = document.getElementById("learning-note-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "learning-note-modal";
    modal.className = "modal";
    modal.innerHTML = `
      <div class="modal-backdrop"></div>
      <div class="modal-content" style="max-width: 600px;">
        <div class="modal-header">
          <h3>Create Learning Note</h3>
          <button class="modal-close" id="learning-note-close">
            <i data-lucide="x"></i>
          </button>
        </div>
        <div class="modal-body">
          <p style="margin-bottom: 16px; color: var(--text-secondary);">
            Great progress! Create a structured note to capture what you've learned about 
            <strong id="learning-note-topic-title">${topic}</strong>.
          </p>
          
          <div class="note-preview" style="padding: 16px; background: var(--bg-secondary); border-radius: 8px; margin-bottom: 16px;">
            <h4 style="margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
              <i data-lucide="book-open" style="width: 18px; height: 18px;"></i>
              Note Preview
            </h4>
            <div style="font-size: 13px; color: var(--text-muted);">
              <div style="margin-bottom: 8px;">
                <strong>Topic:</strong> <span id="learning-note-preview-topic">${topic}</span>
              </div>
              <div style="margin-bottom: 8px;">
                <strong>Domain:</strong> <span id="learning-note-preview-domain">${domain}</span>
              </div>
              <div>
                <strong>Concepts:</strong> 
                <span id="learning-note-preview-concepts">
                  ${concepts.map((c) => `<span style="display: inline-block; padding: 2px 8px; background: var(--accent-translucent); color: var(--accent); border-radius: 4px; font-size: 11px; margin-right: 4px;">${c}</span>`).join("")}
                </span>
              </div>
            </div>
          </div>
          
          <div style="padding: 12px; background: rgba(139, 92, 246, 0.1); border-left: 3px solid #8b5cf6; border-radius: 4px; margin-bottom: 16px;">
            <div style="font-size: 12px; color: var(--text-secondary);">
              <i data-lucide="lightbulb" style="width: 14px; height: 14px; display: inline; margin-right: 4px;"></i>
              This note will include definitions, key insights from our dialogue, related concepts, and practice exercises.
            </div>
          </div>
        </div>
        <div class="modal-footer" style="display: flex; gap: 8px; justify-content: flex-end;">
          <button class="btn btn-secondary" id="learning-note-cancel">Not Now</button>
          <button class="btn btn-primary" id="learning-note-create">
            <i data-lucide="check" style="width: 16px; height: 16px; margin-right: 6px;"></i>
            Create Note
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);

    // Initialize Lucide icons in modal
    if (typeof lucide !== "undefined") {
      lucide.createIcons();
    }

    // Setup event listeners
    document
      .getElementById("learning-note-close")
      .addEventListener("click", () => {
        modal.classList.remove("show");
        modal.classList.add("hidden");
      });

    document
      .getElementById("learning-note-cancel")
      .addEventListener("click", () => {
        modal.classList.remove("show");
        modal.classList.add("hidden");
      });

    document
      .getElementById("learning-note-create")
      .addEventListener("click", async () => {
        // Call createLearningNote function
        await createLearningNote(topic, concepts);
        modal.classList.remove("show");
        modal.classList.add("hidden");
      });

    // Click backdrop to close
    modal.querySelector(".modal-backdrop").addEventListener("click", () => {
      modal.classList.remove("show");
      modal.classList.add("hidden");
    });
  } else {
    // Update existing modal content
    document.getElementById("learning-note-topic-title").textContent = topic;
    document.getElementById("learning-note-preview-topic").textContent = topic;
    document.getElementById("learning-note-preview-domain").textContent =
      domain;
    document.getElementById("learning-note-preview-concepts").innerHTML =
      concepts
        .map(
          (c) =>
            `<span style="display: inline-block; padding: 2px 8px; background: var(--accent-translucent); color: var(--accent); border-radius: 4px; font-size: 11px; margin-right: 4px;">${c}</span>`,
        )
        .join("");
  }

  // Show modal
  modal.classList.remove("hidden");
  modal.classList.add("show");
}

/**
 * Create learning note from chat conversation
 */
async function createLearningNote(topic, concepts) {
  try {
    // Get current conversation ID from chat
    const conversationId = currentConversationId;

    const response = await fetch(`${API_URL}/polly/learning/create-note`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic,
        concepts: concepts || [],
        conversation_id: conversationId,
        domain: currentPage || "general",
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to create learning note");
    }

    const result = await response.json();

    if (result.status === "success") {
      showNotification(`Learning note created: ${result.note_path}`, "success");

      // Reload stats, topics, and notes
      await loadLearningStats();
      await loadRecentLearningNotes();
    }
  } catch (error) {
    console.error("[Learning] Error creating note:", error);
    showNotification("Failed to create learning note", "error");
  }
}

/**
 * Load and display all topics in the Topics sidebar browser panel
 */
let allLearningTopics = []; // Cache for filtering

async function loadTopicsBrowser() {
  const listEl = document.getElementById("topics-browser-list");
  if (!listEl) return;

  try {
    const response = await fetch(`${API_URL}/polly/learning/topics`);

    if (!response.ok) {
      throw new Error("Failed to load topics");
    }

    const data = await response.json();
    allLearningTopics = data.topics || [];

    // Populate domain filter options
    populateTopicsDomainFilter(allLearningTopics);

    // Render all topics
    renderTopicsBrowser(allLearningTopics);

    // Setup filter handlers
    setupTopicsFilterHandlers();
  } catch (error) {
    console.error("[Learning] Error loading topics browser:", error);
    if (listEl) {
      listEl.innerHTML =
        '<p class="no-topics">Failed to load topics</p>';
    }
  }
}

/**
 * Populate domain filter dropdown from topics data
 */
function populateTopicsDomainFilter(topics) {
  const filter = document.getElementById("topics-domain-filter");
  if (!filter) return;

  const domains = [...new Set(topics.map((t) => t.domain).filter(Boolean))];

  // Keep the "All Domains" option, add unique domains
  filter.innerHTML = '<option value="">All Domains</option>';
  domains.sort().forEach((domain) => {
    const option = document.createElement("option");
    option.value = domain;
    option.textContent = domain;
    filter.appendChild(option);
  });
}

/**
 * Setup filter change handlers for topics browser
 */
function setupTopicsFilterHandlers() {
  const domainFilter = document.getElementById("topics-domain-filter");
  const masteryFilter = document.getElementById("topics-mastery-filter");

  const applyFilters = () => {
    const domain = domainFilter ? domainFilter.value : "";
    const mastery = masteryFilter ? masteryFilter.value : "";

    let filtered = allLearningTopics;

    if (domain) {
      filtered = filtered.filter((t) => t.domain === domain);
    }

    if (mastery) {
      filtered = filtered.filter(
        (t) => t.mastery_level === parseInt(mastery),
      );
    }

    renderTopicsBrowser(filtered);
  };

  if (domainFilter) {
    domainFilter.addEventListener("change", applyFilters);
  }
  if (masteryFilter) {
    masteryFilter.addEventListener("change", applyFilters);
  }
}

/**
 * Render topics in the browser panel
 */
function renderTopicsBrowser(topics) {
  const listEl = document.getElementById("topics-browser-list");
  if (!listEl) return;

  if (topics.length === 0) {
    listEl.innerHTML =
      '<p class="no-topics">No topics match the current filters</p>';
    return;
  }

  listEl.innerHTML = topics
    .map(
      (topic) => `
    <div class="topic-card" data-topic="${escapeHtml(topic.title)}">
      <div class="topic-header">
        <span class="topic-name">${escapeHtml(topic.title)}</span>
        <span class="mastery-badge mastery-${topic.mastery_level}">L${topic.mastery_level}</span>
      </div>
      <div class="topic-meta">
        <span class="topic-domain">${escapeHtml(topic.domain || "General")}</span>
        <span class="topic-updated">${formatDate(topic.last_reviewed)}</span>
      </div>
      ${topic.concepts && topic.concepts.length > 0 ? `
      <div class="topic-concepts">
        ${topic.concepts.slice(0, 3).map((c) => `<span class="concept-tag">${escapeHtml(c)}</span>`).join("")}
        ${topic.concepts.length > 3 ? `<span class="concept-tag concept-more">+${topic.concepts.length - 3}</span>` : ""}
      </div>
      ` : ""}
    </div>
  `,
    )
    .join("");

  // Add click handlers for topic cards
  listEl.querySelectorAll(".topic-card").forEach((card) => {
    card.addEventListener("click", () => {
      const topicTitle = card.dataset.topic;
      startTopicReview(topicTitle);
    });
  });

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

/**
 * Load topics that need review (spaced repetition)
 */
async function loadReviewTopics() {
  try {
    const response = await fetch(`${API_URL}/polly/learning/review`);

    if (!response.ok) {
      throw new Error("Failed to load review topics");
    }

    const data = await response.json();
    updateReviewTopicsUI(data.topics || []);
  } catch (error) {
    console.error("[Learning] Error loading review topics:", error);
  }
}

/**
 * Update review topics UI in the dashboard
 */
function updateReviewTopicsUI(topics) {
  const reviewList = document.getElementById("review-topics-list");
  const reviewSection = document.getElementById("review-section");
  if (!reviewList) return;

  if (topics.length === 0) {
    if (reviewSection) reviewSection.style.display = "none";
    return;
  }

  // Show the review section
  if (reviewSection) reviewSection.style.display = "block";

  reviewList.innerHTML = topics
    .map(
      (topic) => `
    <div class="review-topic-card" data-topic="${escapeHtml(topic.title)}">
      <div class="review-topic-header">
        <span class="topic-name">${escapeHtml(topic.title)}</span>
        <span class="mastery-badge mastery-${topic.mastery_level}">L${topic.mastery_level}</span>
      </div>
      <div class="review-topic-meta">
        <span class="topic-domain">${escapeHtml(topic.domain || "General")}</span>
        <span class="review-overdue">${topic.days_since_review} days since review</span>
      </div>
      <button class="btn btn-sm btn-secondary review-topic-btn" data-topic="${escapeHtml(topic.title)}">
        <i data-lucide="refresh-cw" style="width: 12px; height: 12px;"></i>
        Review Now
      </button>
    </div>
  `,
    )
    .join("");

  // Attach click handlers to review buttons
  reviewList.querySelectorAll(".review-topic-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const topicTitle = btn.dataset.topic;
      startTopicReview(topicTitle);
    });
  });

  // Attach click handlers to review cards
  reviewList.querySelectorAll(".review-topic-card").forEach((card) => {
    card.addEventListener("click", () => {
      const topicTitle = card.dataset.topic;
      startTopicReview(topicTitle);
    });
  });

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

/**
 * Start a review session for a topic via chat
 */
function startTopicReview(topicTitle) {
  // Auto-select Professor persona
  selectProfessorPersona();

  // Set the right-panel chat input to a review query and focus
  const input = document.getElementById("chat-input");
  if (input) {
    input.value = `/socratic Review: ${topicTitle} - test my understanding and help me reinforce what I've learned`;
    input.focus();
    // Dispatch input event so any auto-resize triggers
    input.dispatchEvent(new Event("input", { bubbles: true }));
  }

  console.log("[Learning] Starting review for topic:", topicTitle);
}

/**
 * Load recent learning notes for dashboard display
 */
async function loadRecentLearningNotes() {
  try {
    // Fetch learning topics which include notes_created paths
    const response = await fetch(`${API_URL}/polly/learning/topics`);

    if (!response.ok) {
      throw new Error("Failed to load learning topics for notes");
    }

    const data = await response.json();
    const topics = data.topics || [];

    // Collect all notes from topics
    const learningNotes = [];
    for (const topic of topics) {
      if (topic.notes_created && topic.notes_created.length > 0) {
        for (const notePath of topic.notes_created) {
          learningNotes.push({
            path: notePath,
            topic: topic.title,
            domain: topic.domain,
            mastery_level: topic.mastery_level,
            last_reviewed: topic.last_reviewed,
          });
        }
      }
    }

    updateLearningNotesUI(learningNotes);
  } catch (error) {
    console.error("[Learning] Error loading learning notes:", error);
  }
}

/**
 * Update learning notes section in dashboard
 */
function updateLearningNotesUI(notes) {
  const notesContainer = document.getElementById("recent-learning-notes");
  if (!notesContainer) return;

  if (notes.length === 0) {
    notesContainer.innerHTML =
      '<p class="no-topics" style="font-size: 12px; color: #666;">No learning notes yet. Complete a teaching session and create notes to capture your learning.</p>';
    return;
  }

  // Show most recent first, limit to 5
  const recentNotes = notes.slice(0, 5);

  notesContainer.innerHTML = recentNotes
    .map(
      (note) => `
    <div class="learning-note-card" data-path="${escapeHtml(note.path || "")}" data-topic="${escapeHtml(note.topic)}">
      <div class="learning-note-header">
        <i data-lucide="file-text" style="width: 14px; height: 14px; color: #00d9ff;"></i>
        <span class="learning-note-title">${escapeHtml(note.topic)}</span>
      </div>
      <div class="learning-note-meta">
        <span class="topic-domain">${escapeHtml(note.domain || "General")}</span>
        <span class="mastery-badge mastery-${note.mastery_level}">L${note.mastery_level}</span>
      </div>
    </div>
  `,
    )
    .join("");

  // Click handler for learning note cards
  notesContainer.querySelectorAll(".learning-note-card").forEach((card) => {
    card.addEventListener("click", () => {
      const notePath = card.dataset.path;
      if (notePath && window.notesManager) {
        // Switch to notes view and open this note
        showView("notes");
        setTimeout(() => {
          window.notesManager.openNote(notePath);
        }, 200);
      }
    });
  });

  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }
}

// ==================== End Learning (Phase 22) ====================

// ==================== Graph Page (knowledge-graph-navigation) ====================

/**
 * Render the Graph page sidebar
 */
function renderGraphSidebar() {
  return `
    <div id="graph-sidebar-browse" class="graph-sidebar-panel">
      <div id="graph-browse-list" style="flex: 1; overflow-y: auto; padding: 0 12px;">
        <div class="loading-spinner" style="text-align: center; padding: 20px; color: #808080; font-size: 13px;">
          Loading graph...
        </div>
      </div>
    </div>
    <div id="graph-sidebar-garden" class="graph-sidebar-panel hidden">
      <div id="graph-garden-content" style="padding: 16px;">
        <div class="garden-section">
          <h3 style="font-size: 13px; font-weight: 600; margin-bottom: 12px; color: var(--text-primary);">
            <i data-lucide="sprout" style="width: 14px; height: 14px; margin-right: 6px;"></i>
            Digital Garden
          </h3>
          <p style="font-size: 12px; color: var(--text-secondary); margin-bottom: 16px;">
            Isolated notes that need more connections to grow.
          </p>
          <div id="garden-isolated-notes">
            <div class="loading-spinner" style="text-align: center; padding: 20px; color: #808080; font-size: 11px;">
              Loading isolated notes...
            </div>
          </div>
        </div>
      </div>
    </div>
    ${renderLowerPanel("graph", [
      {id: "filters", label: "Filters"},
      {id: "details", label: "Details"}
    ])}
  `;
}

/**
 * Render the lower collapsible panel component
 * @param {string} view - The view context ("notes" or "graph")
 * @param {Array} tabs - Array of tab objects [{id: 'filters', label: 'Filters'}, ...]
 * @returns {string} HTML string for the lower panel
 */
function renderLowerPanel(view, tabs) {
  const collapsed = localStorage.getItem(`lowerPanel_${view}_collapsed`) === 'true';
  const height = localStorage.getItem(`lowerPanel_${view}_height`) || '250';
  const activeTab = localStorage.getItem(`lowerPanel_${view}_activeTab`) || tabs[0]?.id || 'filters';
  
  const tabsHTML = tabs.map(tab => 
    `<button class="lower-panel-tab ${tab.id === activeTab ? 'active' : ''}" data-tab="${tab.id}">
      ${tab.label}
    </button>`
  ).join('');
  
  return `
    <div class="lower-panel" data-view="${view}" data-collapsed="${collapsed}" style="height: ${collapsed ? '32' : height}px;">
      <div class="lower-panel-header">
        <div class="lower-panel-handle" title="${collapsed ? 'Expand panel' : 'Collapse panel'}">
          <i data-lucide="${collapsed ? 'chevron-up' : 'chevron-down'}" style="width: 14px; height: 14px;"></i>
        </div>
        <div class="lower-panel-resize-handle"></div>
      </div>
      <div class="lower-panel-ribbon" style="${collapsed ? 'display: none;' : ''}">
        ${tabsHTML}
      </div>
      <div class="lower-panel-content" data-active-tab="${activeTab}" style="${collapsed ? 'display: none;' : ''}">
        <!-- Tab content will be rendered here -->
      </div>
    </div>
  `;
}

/**
 * Setup event handlers for the lower collapsible panel
 * @param {string} view - The view context ("notes" or "graph")
 */
function setupLowerPanel(view) {
  const panel = document.querySelector(`.lower-panel[data-view="${view}"]`);
  if (!panel) {
    console.warn(`[LowerPanel] Panel not found for view: ${view}`);
    return;
  }
  
  const header = panel.querySelector('.lower-panel-header');
  const handle = panel.querySelector('.lower-panel-handle');
  const resizeHandle = panel.querySelector('.lower-panel-resize-handle');
  const ribbon = panel.querySelector('.lower-panel-ribbon');
  const content = panel.querySelector('.lower-panel-content');
  const tabs = panel.querySelectorAll('.lower-panel-tab');
  
  // Toggle collapse/expand on header click
  handle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isCollapsed = panel.dataset.collapsed === 'true';
    const newCollapsed = !isCollapsed;
    
    panel.dataset.collapsed = newCollapsed;
    localStorage.setItem(`lowerPanel_${view}_collapsed`, newCollapsed);
    
    if (newCollapsed) {
      // Collapse
      const currentHeight = panel.offsetHeight;
      localStorage.setItem(`lowerPanel_${view}_height`, currentHeight);
      panel.style.height = '32px';
      ribbon.style.display = 'none';
      content.style.display = 'none';
      handle.innerHTML = '<i data-lucide="chevron-up" style="width: 14px; height: 14px;"></i>';
      handle.title = 'Expand panel';
    } else {
      // Expand
      const savedHeight = localStorage.getItem(`lowerPanel_${view}_height`) || '250';
      panel.style.height = `${savedHeight}px`;
      ribbon.style.display = '';
      content.style.display = '';
      handle.innerHTML = '<i data-lucide="chevron-down" style="width: 14px; height: 14px;"></i>';
      handle.title = 'Collapse panel';
    }
    
    // Re-render icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
  });
  
  // Drag to resize panel height
  let isResizing = false;
  let startY = 0;
  let startHeight = 0;
  
  resizeHandle.addEventListener('mousedown', (e) => {
    if (panel.dataset.collapsed === 'true') return;
    
    isResizing = true;
    startY = e.clientY;
    startHeight = panel.offsetHeight;
    
    document.body.style.cursor = 'ns-resize';
    document.body.style.userSelect = 'none';
    
    e.preventDefault();
  });
  
  document.addEventListener('mousemove', (e) => {
    if (!isResizing) return;
    
    const deltaY = startY - e.clientY; // Inverted because panel grows upward
    const newHeight = Math.max(100, Math.min(600, startHeight + deltaY));
    
    panel.style.height = `${newHeight}px`;
  });
  
  document.addEventListener('mouseup', () => {
    if (isResizing) {
      isResizing = false;
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
      
      // Save height to localStorage
      localStorage.setItem(`lowerPanel_${view}_height`, panel.offsetHeight);
    }
  });
  
  // Tab switching
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabId = tab.dataset.tab;
      
      // Update active tab
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // Update content area
      content.dataset.activeTab = tabId;
      localStorage.setItem(`lowerPanel_${view}_activeTab`, tabId);
      
      // Trigger tab content render (will be handled by specific view implementations)
      const event = new CustomEvent('lower-panel-tab-change', {
        detail: { view, tabId }
      });
      document.dispatchEvent(event);
    });
  });
  
  console.log(`[LowerPanel] Setup complete for view: ${view}`);
}

/**
 * Initialize the Graph page
 */
function initGraphPage() {
  console.log("[Graph] Initializing graph page");
  
  // Import Cytoscape if not already loaded
  if (typeof cytoscape === 'undefined') {
    console.error("[Graph] Cytoscape.js not loaded");
    return;
  }
  
  // Initialize the graph canvas
  initGraphCanvas();
  
  // Load graph browse list (reuse browse list component)
  loadGraphBrowseList();
  
  // Setup lower panel for graph view
  setupLowerPanel("graph");
  
  // Setup lower panel tab change event listener
  document.addEventListener('lower-panel-tab-change', (e) => {
    if (e.detail.view === 'graph') {
      const tabId = e.detail.tabId;
      console.log(`[Graph] Lower panel tab changed to: ${tabId}`);
      
      // Render content for the selected tab
      switch (tabId) {
        case 'filters':
          renderGraphFiltersPanel();
          break;
        case 'details':
          renderGraphDetailsPanel();
          break;
      }
    }
  });
  
  // Re-initialize icons
  if (typeof lucide !== "undefined") {
    setTimeout(() => lucide.createIcons(), 100);
  }
}

/**
 * Initialize the Cytoscape.js graph canvas
 */
let cytoscapeInstance = null;
let graphState = {
  centerNode: null,
  expandedNodes: new Set(),
  filters: {},
  layout: 'cose'  // Use built-in cose layout (cose-bilkent requires additional deps)
};

async function initGraphCanvas() {
  const container = document.getElementById('graph-canvas');
  if (!container) {
    console.error("[Graph] Canvas container not found");
    return;
  }
  
  // Restore previous graph state if it exists
  const savedState = sessionStorage.getItem('graph-state');
  if (savedState) {
    try {
      graphState = JSON.parse(savedState);
      graphState.expandedNodes = new Set(graphState.expandedNodes || []);
    } catch (e) {
      console.error("[Graph] Failed to restore graph state:", e);
    }
  }
  
  // Fetch graph data from backend
  let graphData;
  try {
    // Build query parameters
    const params = new URLSearchParams({
      limit: '100',
      include_ghosts: 'true'
    });
    
    if (graphState.centerNode) {
      params.append('center_node', graphState.centerNode);
      params.append('hops', '2');
    }
    
    // Add filter parameters if they exist
    if (graphState.filters) {
      if (graphState.filters.type) params.append('type', graphState.filters.type);
      if (graphState.filters.domain) params.append('domain', graphState.filters.domain);
      if (graphState.filters.authority_min) params.append('authority_min', graphState.filters.authority_min);
    }
    
    const response = await fetch(`http://127.0.0.1:11436/polly/graph/nodes?${params.toString()}`);
    graphData = await response.json();
  } catch (error) {
    console.error("[Graph] Failed to fetch graph data:", error);
    // Show empty state
    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-secondary); flex-direction: column; gap: 12px;">
        <i data-lucide="network" style="width: 48px; height: 48px; opacity: 0.3;"></i>
        <p>Failed to load graph data</p>
      </div>
    `;
    if (typeof lucide !== 'undefined') lucide.createIcons();
    return;
  }
  
  // Check if we have data
  if (!graphData.nodes || graphData.nodes.length === 0) {
    container.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: var(--text-secondary); flex-direction: column; gap: 12px;">
        <i data-lucide="network" style="width: 48px; height: 48px; opacity: 0.3;"></i>
        <p>No graph data available</p>
        <p style="font-size: 11px; opacity: 0.7;">Create notes with entities to see them in the graph</p>
      </div>
    `;
    if (typeof lucide !== 'undefined') lucide.createIcons();
    return;
  }
  
  // Build domain color palette
  const domains = [...new Set(graphData.nodes.flatMap(n => n.domains || []).filter(Boolean))];
  const domainColors = buildDomainPalette(domains);
  
  // Transform nodes for Cytoscape
  const elements = {
    nodes: graphData.nodes.map(node => ({
      data: {
        id: node.id,
        label: node.name,
        type: node.type,
        domain: (node.domains && node.domains.length > 0) ? node.domains[0] : null,
        domains: node.domains || [],
        authority: node.authority || 0.5,
        connectionCount: node.connection_count || 0,
        isGhost: node.is_ghost || false
      }
    })),
    edges: graphData.edges.map(edge => ({
      data: {
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        weight: edge.strength || 1,
        relationshipType: edge.type || 'references',
        isGhost: edge.is_ghost || false
      }
    }))
  };
  
  // Initialize Cytoscape
  cytoscapeInstance = cytoscape({
    container: container,
    elements: elements,
    style: buildGraphStyle(domainColors),
    layout: {
      name: 'cose',  // Use built-in force-directed layout
      animate: true,
      animationDuration: 500,
      fit: true,
      padding: 50,
      // Increased repulsion for better spacing
      nodeRepulsion: 800000,
      // Longer ideal edge length to spread nodes out
      idealEdgeLength: 150,
      edgeElasticity: 100,
      nestingFactor: 5,
      // Reduced gravity to allow more spreading
      gravity: 40,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0
    },
    minZoom: 0.1,
    maxZoom: 3
    // Use default wheelSensitivity to avoid cross-platform issues
  });
  
  // Setup event handlers
  setupGraphEventHandlers(cytoscapeInstance, domainColors);
  
  console.log("[Graph] Initialized with", graphData.nodes.length, "nodes and", graphData.edges.length, "edges");
}

/**
 * Build the visual style for the graph
 */
function buildGraphStyle(domainColors) {
  return [
    // Base node style
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': '9px',
        'font-weight': '500',
        'text-outline-width': 2,
        'text-outline-color': '#1a1a1a',
        'color': '#ffffff',
        // Smaller base size: 12px base + up to 24px based on authority (12-36px range)
        'width': ele => 12 + (ele.data('authority') * 24),
        'height': ele => 12 + (ele.data('authority') * 24),
        'background-color': ele => {
          const domain = ele.data('domain');
          return domainColors[domain] || '#666666';
        },
        'border-width': 2,
        'border-color': '#ffffff',
        'border-opacity': 0.3,
        // Label visibility controlled dynamically by zoom level
        'text-opacity': 0
      }
    },
    // Node shapes by type
    {
      selector: 'node[type="note"]',
      style: { 'shape': 'ellipse' }
    },
    {
      selector: 'node[type="conversation"]',
      style: { 'shape': 'diamond' }
    },
    {
      selector: 'node[type="book"]',
      style: { 'shape': 'hexagon' }
    },
    {
      selector: 'node[type="capture"]',
      style: { 'shape': 'triangle' }
    },
    {
      selector: 'node[type="code"]',
      style: { 'shape': 'rectangle' }
    },
    {
      selector: 'node[type="canvas"]',
      style: { 'shape': 'round-rectangle' }
    },
    // Ghost nodes
    {
      selector: 'node[isGhost]',
      style: {
        'opacity': 0.15,
        'border-style': 'dotted'
      }
    },
    // Hover state
    {
      selector: 'node:active',
      style: {
        'overlay-color': '#ffffff',
        'overlay-padding': 6,
        'overlay-opacity': 0.2
      }
    },
    // Base edge style
    {
      selector: 'edge',
      style: {
        'width': ele => 1 + (ele.data('weight') * 2),
        'line-color': '#555555',
        'target-arrow-color': '#555555',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'opacity': 0.6
      }
    },
    // Edge styles by relationship type
    {
      selector: 'edge[relationshipType="relates_to"]',
      style: {
        'line-style': 'dashed'
      }
    },
    {
      selector: 'edge[relationshipType="co_occurs_with"]',
      style: {
        'line-style': 'dotted'
      }
    },
    // Edges connected to ghost nodes
    {
      selector: 'edge[isGhost]',
      style: {
        'opacity': 0.1,
        'line-style': 'dotted'
      }
    },
    // Selected state
    {
      selector: ':selected',
      style: {
        'border-width': 4,
        'border-color': '#00aaff',
        'border-opacity': 1
      }
    }
  ];
}

/**
 * Build domain color palette
 */
function buildDomainPalette(domains) {
  const palette = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
    '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
  ];
  const colors = {};
  domains.forEach((domain, idx) => {
    colors[domain] = palette[idx % palette.length];
  });
  return colors;
}

/**
 * Setup graph event handlers
 */
function setupGraphEventHandlers(cy, domainColors) {
  // Node hover - show tooltip
  cy.on('mouseover', 'node', (evt) => {
    const node = evt.target;
    const data = node.data();
    
    showGraphTooltip(evt.originalEvent, {
      name: data.label,
      type: data.type,
      domain: data.domain,
      connections: data.connectionCount,
      authority: data.authority
    });
  });
  
  cy.on('mouseout', 'node', () => {
    hideGraphTooltip();
  });
  
  // Node click - open item
  cy.on('tap', 'node', (evt) => {
    const node = evt.target;
    const data = node.data();
    
    // Save graph state
    saveGraphState();
    
    // Open the item based on type
    if (data.type === 'note') {
      // Open note
      if (window.notesManager) {
        window.notesManager.openNoteByName(data.label);
      }
      showView('notes');
      
      // Show "Back to Graph" button
      showBackToGraphButton();
    }
  });
  
  // Node right-click - context menu
  cy.on('cxttap', 'node', (evt) => {
    const node = evt.target;
    const data = node.data();
    
    showGraphContextMenu(evt.originalEvent, {
      nodeId: data.id,
      nodeName: data.label,
      nodeType: data.type
    });
  });
  
  // Pan/zoom - save state (debounced) and update label visibility
  let saveTimeout;
  cy.on('viewport', () => {
    updateGraphLabelVisibility(cy);
    
    clearTimeout(saveTimeout);
    saveTimeout = setTimeout(() => {
      saveGraphState();
    }, 500);
  });
  
  // Initial label visibility update
  updateGraphLabelVisibility(cy);
}

/**
 * Update label visibility based on zoom level
 * - Low zoom (< 0.5): No labels
 * - Medium zoom (0.5 - 1.5): Only high-authority nodes (> 0.6)
 * - High zoom (> 1.5): All labels
 */
function updateGraphLabelVisibility(cy) {
  if (!cy) return;
  
  const zoom = cy.zoom();
  
  cy.nodes().forEach(node => {
    const authority = node.data('authority') || 0.5;
    let opacity = 0;
    
    if (zoom < 0.5) {
      // Low zoom: no labels
      opacity = 0;
    } else if (zoom < 1.5) {
      // Medium zoom: only high-authority nodes
      opacity = authority > 0.6 ? 1 : 0;
    } else {
      // High zoom: all labels
      opacity = 1;
    }
    
    node.style('text-opacity', opacity);
  });
}

/**
 * Save graph state to sessionStorage
 */
function saveGraphState() {
  if (!cytoscapeInstance) return;
  
  graphState.centerNode = graphState.centerNode; // Keep existing
  graphState.position = cytoscapeInstance.pan();
  graphState.zoom = cytoscapeInstance.zoom();
  
  sessionStorage.setItem('graph-state', JSON.stringify({
    ...graphState,
    expandedNodes: Array.from(graphState.expandedNodes)
  }));
}

/**
 * Load graph browse list (reuses browse list component from Task 8)
 */
async function loadGraphBrowseList() {
  const container = document.getElementById('graph-browse-list');
  if (!container) {
    console.error("[Graph] Browse list container not found");
    return;
  }
  
  try {
    const response = await fetch('http://127.0.0.1:11436/polly/graph/list');
    const data = await response.json();
    
    if (!data.items || data.items.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 20px; color: var(--text-secondary); font-size: 13px;">
          No items found
        </div>
      `;
      return;
    }
    
    // Render browse items
    let html = '';
    data.items.forEach(item => {
      const icon = getTypeIcon(item.type);
      const date = new Date(item.modified_at).toLocaleDateString();
      html += `
        <div class="browse-item" data-item-id="${item.id}" data-item-type="${item.type}">
          <i data-lucide="${icon}" class="browse-item-icon"></i>
          <div class="browse-item-content">
            <div class="browse-item-title">${item.name}</div>
            <div class="browse-item-metadata">
              <span class="browse-item-domain">${item.domain || 'General'}</span>
              <span class="browse-item-date">${date}</span>
            </div>
          </div>
        </div>
      `;
    });
    
    container.innerHTML = html;
    
    // Re-initialize icons
    if (typeof lucide !== 'undefined') {
      lucide.createIcons();
    }
    
    // Setup click handlers
    container.querySelectorAll('.browse-item').forEach(item => {
      item.addEventListener('click', () => {
        const itemId = item.dataset.itemId;
        const itemType = item.dataset.itemType;
        
        // Highlight and center in graph if visible
        if (cytoscapeInstance) {
          // Use getElementById() instead of CSS selector to avoid escaping issues
          const node = cytoscapeInstance.getElementById(itemId);
          if (node && node.length > 0) {
            cytoscapeInstance.animate({
              center: { eles: node },
              zoom: 1.5
            }, {
              duration: 300
            });
            node.select();
          }
        }
      });
    });
    
  } catch (error) {
    console.error("[Graph] Failed to load browse list:", error);
    container.innerHTML = `
      <div style="text-align: center; padding: 20px; color: var(--text-error); font-size: 13px;">
        Failed to load items
      </div>
    `;
  }
}

/**
 * Get icon for item type
 */
function getTypeIcon(type) {
  const icons = {
    'note': 'file-text',
    'conversation': 'message-circle',
    'book': 'book',
    'capture': 'camera',
    'code': 'code',
    'canvas': 'layout'
  };
  return icons[type] || 'file';
}

/**
 * Show graph tooltip
 */
let tooltipElement = null;
function showGraphTooltip(event, data) {
  if (!tooltipElement) {
    tooltipElement = document.createElement('div');
    tooltipElement.className = 'graph-node-tooltip';
    tooltipElement.style.cssText = `
      position: fixed;
      background: rgba(0, 0, 0, 0.9);
      color: #ffffff;
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 11px;
      pointer-events: none;
      z-index: 10000;
      max-width: 200px;
    `;
    document.body.appendChild(tooltipElement);
  }
  
  tooltipElement.innerHTML = `
    <div style="font-weight: 600; margin-bottom: 4px;">${data.name}</div>
    <div style="opacity: 0.8; font-size: 10px;">
      <div>Type: ${data.type}</div>
      <div>Domain: ${data.domain || 'None'}</div>
      <div>Connections: ${data.connections}</div>
      <div>Authority: ${(data.authority * 100).toFixed(0)}%</div>
    </div>
  `;
  
  tooltipElement.style.left = (event.pageX + 10) + 'px';
  tooltipElement.style.top = (event.pageY + 10) + 'px';
  tooltipElement.style.display = 'block';
}

function hideGraphTooltip() {
  if (tooltipElement) {
    tooltipElement.style.display = 'none';
  }
}

/**
 * Show graph context menu
 */
function showGraphContextMenu(event, data) {
  // TODO: Implement context menu in future commit
  console.log("[Graph] Context menu requested for:", data);
}

/**
 * Show "Back to Graph" button
 */
function showBackToGraphButton() {
  let btn = document.getElementById('back-to-graph-btn');
  if (!btn) {
    btn = document.createElement('button');
    btn.id = 'back-to-graph-btn';
    btn.className = 'back-to-graph-button';
    btn.innerHTML = '<i data-lucide="arrow-left"></i> Back to Graph';
    btn.style.cssText = `
      position: fixed;
      bottom: 24px;
      left: 24px;
      z-index: 1000;
      background: var(--bg-secondary);
      border: 1px solid var(--border-primary);
      color: var(--text-primary);
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    btn.addEventListener('click', () => {
      showView('graph');
      btn.remove();
    });
    document.body.appendChild(btn);
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }
}

/**
 * Render graph filters panel
 */
function renderGraphFiltersPanel() {
  const content = document.querySelector('.lower-panel[data-view="graph"] .lower-panel-content');
  if (!content) return;
  
  content.innerHTML = `
    <div class="lower-panel-empty">
      <i data-lucide="filter" style="width: 20px; height: 20px; opacity: 0.3; margin-bottom: 8px;"></i>
      <p style="font-size: 12px; color: var(--text-secondary);">Graph filters coming soon</p>
    </div>
  `;
  
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Render graph details panel
 */
function renderGraphDetailsPanel() {
  const content = document.querySelector('.lower-panel[data-view="graph"] .lower-panel-content');
  if (!content) return;
  
  content.innerHTML = `
    <div class="lower-panel-empty">
      <i data-lucide="info" style="width: 20px; height: 20px; opacity: 0.3; margin-bottom: 8px;"></i>
      <p style="font-size: 12px; color: var(--text-secondary);">Select a node to see details</p>
    </div>
  `;
  
  if (typeof lucide !== 'undefined') lucide.createIcons();
}

/**
 * Load Garden view - shows isolated notes and maintenance stats
 */
async function loadGardenView() {
  const container = document.getElementById('garden-isolated-notes');
  if (!container) return;
  
  try {
    // Fetch isolated notes from /polly/graph/list with connection_status filter
    const response = await fetch('http://127.0.0.1:11436/polly/graph/list?connection_status=isolated&limit=50');
    const data = await response.json();
    
    if (!data.items || data.items.length === 0) {
      container.innerHTML = `
        <div style="text-align: center; padding: 20px; color: var(--text-success);">
          <i data-lucide="check-circle" style="width: 32px; height: 32px; opacity: 0.5; margin-bottom: 8px;"></i>
          <p style="font-size: 12px; margin: 0;">No isolated notes found!</p>
          <p style="font-size: 11px; margin-top: 4px; opacity: 0.7;">Your knowledge graph is well connected.</p>
        </div>
      `;
      if (typeof lucide !== 'undefined') lucide.createIcons();
      return;
    }
    
    // Render isolated notes
    let html = '<div class="garden-isolated-list">';
    data.items.forEach(item => {
      const icon = getTypeIcon(item.type);
      html += `
        <div class="garden-isolated-item" data-item-id="${item.id}">
          <i data-lucide="${icon}" style="width: 14px; height: 14px; opacity: 0.5;"></i>
          <div class="garden-isolated-info">
            <div style="font-size: 12px; font-weight: 500; color: var(--text-primary);">${item.name}</div>
            <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;">
              ${item.connection_count || 0} connections
            </div>
          </div>
        </div>
      `;
    });
    html += '</div>';
    
    container.innerHTML = html;
    
    // Re-initialize icons
    if (typeof lucide !== 'undefined') lucide.createIcons();
    
    // Setup click handlers
    container.querySelectorAll('.garden-isolated-item').forEach(item => {
      item.addEventListener('click', () => {
        const itemId = item.dataset.itemId;
        
        // Center on this node in the graph
        if (cytoscapeInstance) {
          const node = cytoscapeInstance.getElementById(itemId);
          if (node && node.length > 0) {
            cytoscapeInstance.animate({
              center: { eles: node },
              zoom: 2
            }, {
              duration: 300
            });
            node.select();
          }
        }
      });
    });
    
  } catch (error) {
    console.error("[Garden] Failed to load isolated notes:", error);
    container.innerHTML = `
      <div style="text-align: center; padding: 20px; color: var(--text-error); font-size: 11px;">
        Failed to load isolated notes
      </div>
    `;
  }
}

// ==================== End Graph Page ====================

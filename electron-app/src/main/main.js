/**
 * Polly - Main Process
 * Handles window management, Python backend, and system integration
 */

const { app, BrowserWindow, BrowserView, ipcMain, Menu, Tray, shell, dialog } = require('electron');
const path = require('path');
const os = require('os');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const Store = require('electron-store');
const keytar = require('keytar');
const ConversationManager = require('./conversation-manager');

// Fix PATH for macOS GUI apps
try {
  require('fix-path')();
} catch (e) {
  console.log('fix-path not available');
}

// Handle EPIPE errors gracefully (broken pipe from child processes)
process.on('uncaughtException', (error) => {
  if (error.code === 'EPIPE' || error.errno === -32) {
    // Ignore EPIPE errors - these happen when writing to a closed pipe
    // This is common when child processes close unexpectedly
    return;
  }
  // For other errors, log and continue
  console.error('Uncaught exception:', error);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Persistent storage
const store = new Store({
  defaults: {
    setupComplete: false,
    pythonPath: '',
    ollamaPath: '',
    vaultPath: '',
    codebasePaths: [],
    theme: 'dark',
    routingMode: 'auto',
    windowBounds: { width: 1200, height: 800 }
  }
});

// Global references
let mainWindow = null;
let tray = null;
let pollyServer = null;
let ollamaProcess = null;
let isQuitting = false;
let ollamaStartedByUs = false;
let conversationManager = null;
let vscodeView = null; // BrowserView for VSCode fork

// Paths - detect if we're in development by checking if we're running from node_modules
const isDev = !app.isPackaged;
const pythonDir = isDev
  ? path.join(__dirname, '..', '..', '..',)  // electron-app/../ = polly root
  : path.join(process.resourcesPath, 'python');

console.log('=== Polly Paths ===');
console.log('isDev:', isDev);
console.log('__dirname:', __dirname);
console.log('pythonDir:', pythonDir);
console.log('requirements.txt exists:', fs.existsSync(path.join(pythonDir, 'requirements.txt')));

/**
 * Create the main application window
 */
function createWindow() {
  const bounds = store.get('windowBounds');

  mainWindow = new BrowserWindow({
    width: bounds.width,
    height: bounds.height,
    minWidth: 800,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    trafficLightPosition: { x: 20, y: 20 },
    backgroundColor: '#1a1a2e',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Load the app
  mainWindow.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));

  // Save window size on resize
  mainWindow.on('resize', () => {
    const { width, height } = mainWindow.getBounds();
    store.set('windowBounds', { width, height });
    // Update VSCode BrowserView bounds if it's visible
    if (vscodeView) {
      updateVSCodeViewBounds();
    }
  });

  // Handle close to tray
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
    }
  });

  // Open devtools in development
  if (isDev) {
    mainWindow.webContents.openDevTools();
    
    // Add keyboard shortcut to toggle DevTools (Cmd+Option+I)
    mainWindow.webContents.on('before-input-event', (event, input) => {
      if (input.meta && input.alt && input.key === 'i') {
        if (mainWindow.webContents.isDevToolsOpened()) {
          mainWindow.webContents.closeDevTools();
        } else {
          mainWindow.webContents.openDevTools();
        }
      }
    });
  }
}

/**
 * Create system tray icon
 */
function createTray() {
  const iconPath = path.join(__dirname, '..', '..', 'assets', 'tray-icon.png');

  // Use a template icon if available, otherwise create basic tray
  try {
    tray = new Tray(iconPath);
  } catch (e) {
    // Create without icon if not found
    console.log('Tray icon not found, using default');
    return;
  }

  const contextMenu = Menu.buildFromTemplate([
    {
      label: 'Open Polly',
      click: () => mainWindow.show()
    },
    { type: 'separator' },
    {
      label: 'Quick Query...',
      accelerator: 'CmdOrCtrl+Shift+P',
      click: () => {
        mainWindow.show();
        mainWindow.webContents.send('focus-query');
      }
    },
    { type: 'separator' },
    {
      label: 'Server Status',
      sublabel: pollyServer ? 'Running' : 'Stopped',
      enabled: false
    },
    {
      label: pollyServer ? 'Restart Server' : 'Start Server',
      click: () => startPollyServer()
    },
    { type: 'separator' },
    {
      label: 'Quit Polly',
      click: () => {
        isQuitting = true;
        app.quit();
      }
    }
  ]);

  tray.setToolTip('Polly');
  tray.setContextMenu(contextMenu);

  tray.on('click', async () => {
    if (mainWindow.isVisible()) {
      mainWindow.hide();
    } else {
      // In dev, restart backend when opening from tray so code changes are picked up
      if (isDev && pollyServer) {
        console.log('[Dev] Restarting backend so latest code is loaded...');
        await stopPollyServer();
        await startPollyServer();
      }
      mainWindow.show();
    }
  });
}

/**
 * Create and configure VSCode BrowserView
 * 
 * NOTE: VSCode's workbench.html requires VSCode's main process to function.
 * Loading it in a BrowserView won't work because it needs VSCode's IPC channels
 * and services. We need to launch VSCode as a separate process.
 * 
 * For now, this creates a BrowserView that shows a placeholder message
 * explaining that full VSCode integration requires launching it as a separate process.
 */
function createVSCodeView() {
  if (vscodeView) {
    console.log('[VSCode] Reusing existing BrowserView');
    return vscodeView;
  }

  const vscodeCodePath = path.join(
    process.env.HOME || os.homedir(),
    'projects',
    'polly-code'
  );

  console.log('[VSCode] Creating BrowserView (placeholder mode)');
  console.log('[VSCode] VSCode path:', vscodeCodePath);
  console.log('[VSCode] NOTE: Full VSCode integration requires launching as separate process');

  vscodeView = new BrowserView({
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true
    }
  });
  
  // Set background color to match VSCode theme
  vscodeView.setBackgroundColor('#1e1e1e');

  // For now, load a placeholder HTML that explains the situation
  // TODO: Launch VSCode fork as separate process and embed it
  const placeholderHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {
          margin: 0;
          padding: 40px;
          background: #1e1e1e;
          color: #cccccc;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
        }
        h1 { color: #f0903b; margin-bottom: 20px; }
        p { max-width: 600px; line-height: 1.6; text-align: center; }
        code { background: #2a2a2a; padding: 2px 6px; border-radius: 3px; }
      </style>
    </head>
    <body>
      <h1>VSCode Integration</h1>
      <p>
        The VSCode fork with Polly ribbon is ready at <code>~/projects/polly-code</code>.
      </p>
      <p>
        Full integration requires launching VSCode as a separate process. 
        BrowserView approach won't work because VSCode's workbench needs its own main process.
      </p>
      <p style="margin-top: 30px; font-size: 14px; color: #808080;">
        Next step: Launch VSCode fork process and embed it, or use VSCode web build.
      </p>
    </body>
    </html>
  `;
  
  // Load the placeholder
  vscodeView.webContents.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(placeholderHTML)}`).then(() => {
    console.log('[VSCode] Placeholder HTML loaded');
  }).catch(err => {
    console.error('[VSCode] Failed to load placeholder:', err);
  });

  // Handle window resize to reposition BrowserView
  if (mainWindow) {
    mainWindow.on('resize', updateVSCodeViewBounds);
    mainWindow.on('move', updateVSCodeViewBounds);
  }

  return vscodeView;
}

/**
 * Update VSCode BrowserView bounds to fit in Code view area
 */
function updateVSCodeViewBounds() {
  if (!mainWindow || !vscodeView) {
    return;
  }

  const bounds = mainWindow.getBounds();
  const ribbonWidth = 48; // Polly ribbon width
  const titlebarHeight = 35; // macOS titlebar height
  const leftSidebarWidth = 280; // Left sidebar width (when visible)
  const rightSidebarWidth = 320; // Right sidebar width (when visible)
  
  // For now, assume sidebars are visible
  // TODO: Check actual sidebar state from renderer
  const leftSidebarVisible = true; // Will be dynamic later
  const rightSidebarVisible = true; // Will be dynamic later
  
  const x = ribbonWidth + (leftSidebarVisible ? leftSidebarWidth : 0);
  const width = bounds.width - ribbonWidth 
    - (leftSidebarVisible ? leftSidebarWidth : 0)
    - (rightSidebarVisible ? rightSidebarWidth : 0);

  vscodeView.setBounds({
    x: x,
    y: titlebarHeight,
    width: width,
    height: bounds.height - titlebarHeight
  });
  
  console.log('[VSCode] BrowserView bounds updated:', {
    x, y: titlebarHeight, width, height: bounds.height - titlebarHeight,
    windowWidth: bounds.width, windowHeight: bounds.height
  });
}

/**
 * Show VSCode BrowserView
 */
function showVSCodeView() {
  if (!mainWindow) {
    console.error('[VSCode] Main window not available');
    return;
  }

  if (!vscodeView) {
    vscodeView = createVSCodeView();
    if (!vscodeView) {
      return;
    }
  }

  mainWindow.setBrowserView(vscodeView);
  updateVSCodeViewBounds();
  
  // Ensure BrowserView is on top
  vscodeView.webContents.focus();
  
  console.log('[VSCode] BrowserView shown and focused');
}

/**
 * Hide VSCode BrowserView
 */
function hideVSCodeView() {
  if (!mainWindow || !vscodeView) {
    return;
  }

  mainWindow.removeBrowserView(vscodeView);
  console.log('[VSCode] BrowserView hidden');
}

/**
 * Start the Polly Python server
 */
async function startPollyServer() {
  if (pollyServer) {
    console.log('Killing existing Polly server...');
    pollyServer.kill();
    pollyServer = null;
  }

  // Try to use venv Python first, fall back to configured or system Python
  const venvPython = path.join(pythonDir, 'venv', 'bin', 'python');
  const configuredPython = store.get('pythonPath') || 'python3';
  
  // Check if venv Python exists
  let pythonPath = configuredPython;
  try {
    const fs = require('fs');
    if (fs.existsSync(venvPython)) {
      pythonPath = venvPython;
      console.log('Using virtualenv Python');
    }
  } catch (error) {
    console.log('Could not check for venv Python, using configured path');
  }
  
  const serverScript = path.join(pythonDir, 'interfaces', 'server.py');
  
  console.log('Starting Polly server...');
  console.log('Python path:', pythonPath);
  console.log('Working directory:', pythonDir);

  // Load API keys from keychain and add to environment
  const serverEnv = { ...process.env, PYTHONPATH: pythonDir };
  
  try {
    // Load GitHub token (Python secrets_manager expects 'GITHUB_TOKEN')
    const githubToken = await keytar.getPassword(KEYTAR_SERVICE, 'GITHUB_TOKEN') || 
                        await keytar.getPassword(KEYTAR_SERVICE, 'github_token');
    if (githubToken) {
      serverEnv.GITHUB_TOKEN = githubToken;
      console.log('✓ Loaded GitHub token from keychain');
    }
    
    // Load Anthropic API key (Python expects 'ANTHROPIC_API_KEY')  
    const anthropicKey = await keytar.getPassword(KEYTAR_SERVICE, 'ANTHROPIC_API_KEY') ||
                         await keytar.getPassword(KEYTAR_SERVICE, 'anthropic_api_key');
    if (anthropicKey) {
      serverEnv.ANTHROPIC_API_KEY = anthropicKey;
      console.log('✓ Loaded Anthropic API key from keychain');
    }
    
    // Load OpenAI API key (Python expects 'OPENAI_API_KEY')
    const openaiKey = await keytar.getPassword(KEYTAR_SERVICE, 'OPENAI_API_KEY') ||
                      await keytar.getPassword(KEYTAR_SERVICE, 'openai_api_key');
    if (openaiKey) {
      serverEnv.OPENAI_API_KEY = openaiKey;
      console.log('✓ Loaded OpenAI API key from keychain');
    }
  } catch (error) {
    console.error('Error loading API keys from keychain:', error);
  }

  return new Promise((resolve, reject) => {
    pollyServer = spawn(pythonPath, ['-m', 'uvicorn', 'interfaces.server:create_app', '--host', '127.0.0.1', '--port', '11436', '--factory'], {
      cwd: pythonDir,
      env: serverEnv
    });
    
    console.log('Polly server process spawned with PID:', pollyServer.pid);

    let resolved = false;
    
    // Handle stdout with error catching
    pollyServer.stdout.on('data', (data) => {
      try {
        const output = data.toString();
        console.log(`Polly Server: ${output}`);
        
        // Check for various uvicorn startup messages
        if (!resolved && (output.includes('Uvicorn running') || 
                          output.includes('Application startup complete') ||
                          output.includes('Started server process'))) {
          resolved = true;
          console.log('Polly server started successfully!');
          resolve(true);
          mainWindow?.webContents.send('server-status', { running: true });
        }
      } catch (error) {
        // Ignore pipe errors
        if (error.code !== 'EPIPE' && error.errno !== -32) {
          console.error('Error handling stdout:', error);
        }
      }
    });

    pollyServer.stderr.on('data', (data) => {
      try {
        const error = data.toString();
        console.error(`Polly Server Error: ${error}`);
        
        // Check for startup messages in stderr (uvicorn sends INFO logs to stderr)
        if (!resolved && (error.includes('Uvicorn running') || 
                          error.includes('Application startup complete'))) {
          resolved = true;
          console.log('Polly server started successfully!');
          resolve(true);
          mainWindow?.webContents.send('server-status', { running: true });
        }
        
        // Send errors to renderer for debugging
        mainWindow?.webContents.send('server-error', { error });
      } catch (err) {
        // Ignore pipe errors
        if (err.code !== 'EPIPE' && err.errno !== -32) {
          console.error('Error handling stderr:', err);
        }
      }
    });

    pollyServer.on('close', (code) => {
      console.log(`Polly Server exited with code ${code}`);
      pollyServer = null;
      mainWindow?.webContents.send('server-status', { running: false });
    });
    
    pollyServer.on('error', (error) => {
      console.error('Polly Server spawn error:', error);
      reject(error);
    });

    // Timeout after 30 seconds
    setTimeout(() => {
      if (!resolved) {
        console.error('Server start timeout after 30 seconds');
        reject(new Error('Server start timeout'));
      }
    }, 30000);
  });
}

/**
 * Stop the Polly server. Returns a Promise that resolves when the process has exited,
 * so callers can wait for the port to be released (e.g. before quit or before restart).
 */
function stopPollyServer() {
  return new Promise((resolve) => {
    if (!pollyServer) {
      resolve();
      return;
    }
    const pid = pollyServer.pid;
    console.log('Stopping Polly server (PID:', pid, ')');
    let resolved = false;
    const done = () => {
      if (!resolved) {
        resolved = true;
        pollyServer = null;
        mainWindow?.webContents.send('server-status', { running: false });
        resolve();
      }
    };

    pollyServer.once('close', (code) => {
      console.log('Polly server stopped with code', code);
      done();
    });

    pollyServer.kill('SIGTERM');

    setTimeout(() => {
      try {
        if (pollyServer && pollyServer.pid) {
          process.kill(pid, 0);
          console.log('Force killing Polly server PID:', pid);
          process.kill(pid, 'SIGKILL');
        }
      } catch (e) {
        // Process already dead
      }
      done();
    }, 2500);
  });
}

/**
 * Check if Ollama is already running
 */
async function isOllamaRunning() {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://localhost:11434/api/tags', { 
      timeout: 2000 
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

/**
 * Start Ollama server
 */
async function startOllamaServer() {
  // Check if already running
  const alreadyRunning = await isOllamaRunning();
  if (alreadyRunning) {
    console.log('Ollama is already running');
    mainWindow?.webContents.send('ollama-status', { running: true });
    return true;
  }

  // Try to start Ollama
  try {
    ollamaProcess = spawn('ollama', ['serve'], {
      detached: false,
      stdio: 'pipe'
    });

    ollamaStartedByUs = true;

    ollamaProcess.stdout.on('data', (data) => {
      console.log(`Ollama: ${data}`);
    });

    ollamaProcess.stderr.on('data', (data) => {
      console.log(`Ollama: ${data}`);
    });

    ollamaProcess.on('close', (code) => {
      console.log(`Ollama exited with code ${code}`);
      ollamaProcess = null;
      mainWindow?.webContents.send('ollama-status', { running: false });
    });

    // Wait a bit and check if it's running
    await new Promise(resolve => setTimeout(resolve, 2000));
    const running = await isOllamaRunning();
    
    if (running) {
      mainWindow?.webContents.send('ollama-status', { running: true });
      console.log('Ollama started successfully');
      return true;
    } else {
      throw new Error('Ollama did not start');
    }
  } catch (error) {
    console.error('Failed to start Ollama:', error.message);
    return false;
  }
}

/**
 * Stop Ollama server (only if we started it)
 */
function stopOllamaServer() {
  if (ollamaProcess && ollamaStartedByUs) {
    ollamaProcess.kill();
    ollamaProcess = null;
    ollamaStartedByUs = false;
    mainWindow?.webContents.send('ollama-status', { running: false });
  }
}

/**
 * Check system dependencies
 */
async function checkDependencies() {
  const deps = {
    python: false,
    ollama: false,
    pythonPackages: false
  };

  // Check Python
  try {
    await execPromise('python3 --version');
    deps.python = true;
  } catch (e) {
    console.log('Python not found');
  }

  // Check Ollama
  try {
    await execPromise('ollama --version');
    deps.ollama = true;
  } catch (e) {
    console.log('Ollama not found');
  }

  // Check if venv exists and has packages
  const venvPath = path.join(pythonDir, 'venv');
  if (fs.existsSync(venvPath)) {
    deps.pythonPackages = true;
  }

  return deps;
}

/**
 * Run setup process
 */
async function runSetup(options) {
  const steps = [];

  // Create virtual environment
  steps.push({
    name: 'Creating Python environment',
    command: `python3 -m venv "${path.join(pythonDir, 'venv')}"`
  });

  // Install packages
  const pipPath = path.join(pythonDir, 'venv', 'bin', 'pip');
  steps.push({
    name: 'Installing Python packages',
    command: `"${pipPath}" install -r "${path.join(pythonDir, 'requirements.txt')}"`
  });

  // Pull Ollama models if requested
  if (options.pullModels) {
    steps.push({
      name: 'Pulling embedding model',
      command: 'ollama pull nomic-embed-text'
    });
    steps.push({
      name: 'Pulling chat model',
      command: 'ollama pull llama3.2'
    });
  }

  // Execute steps
  // SECURITY (Phase 23.5): All commands here are hardcoded and use controlled paths.
  // No user input is used in command construction. Commands are:
  // - python3 -m venv (with controlled path.join)
  // - pip install (with controlled paths)
  // - ollama pull (hardcoded model names)
  for (let i = 0; i < steps.length; i++) {
    const step = steps[i];
    mainWindow.webContents.send('setup-progress', {
      step: i + 1,
      total: steps.length,
      message: step.name
    });

    try {
      await execPromise(step.command);
    } catch (error) {
      throw new Error(`Failed at "${step.name}": ${error.message}`);
    }
  }

  // Save config
  if (options.vaultPath) {
    store.set('vaultPath', options.vaultPath);
  }
  if (options.codebasePaths) {
    store.set('codebasePaths', options.codebasePaths);
  }

  // Update Python path to use venv
  store.set('pythonPath', path.join(pythonDir, 'venv', 'bin', 'python'));
  store.set('setupComplete', true);

  return true;
}

/**
 * Index knowledge base
 */
async function indexKnowledgeBase(options = {}) {
  // Call the API endpoint instead of CLI
  const fetch = (await import('node-fetch')).default;

  try {
    mainWindow?.webContents.send('index-progress', { message: 'Starting indexing...' });

    // Start indexing (returns immediately)
    const startResponse = await fetch('http://localhost:11436/polly/index', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        obsidian: !options.codeOnly,
        codebases: !options.obsidianOnly,
        force: options.force || false
      })
    });

    if (!startResponse.ok) {
      throw new Error(`Server error: ${startResponse.status}`);
    }

    const startResult = await startResponse.json();
    
    if (startResult.status === 'already_running') {
      mainWindow?.webContents.send('index-progress', { message: 'Indexing already in progress...' });
    }

    // Poll for completion
    let lastResult = null;
    const maxAttempts = 120; // 2 minutes max (120 * 1s)
    let attempts = 0;

    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
      attempts++;

      const statusResponse = await fetch('http://localhost:11436/polly/index/status');
      if (!statusResponse.ok) {
        throw new Error(`Status check failed: ${statusResponse.status}`);
      }

      const status = await statusResponse.json();
      
      if (!status.in_progress) {
        // Indexing complete
        if (status.last_error) {
          throw new Error(`Indexing failed: ${status.last_error}`);
        }
        
        lastResult = status.last_result || {};
        
        // Format results - lastResult is like {obsidian: 75, codebases: 0}
        let message = '✅ Indexing complete!';
        if (lastResult.obsidian) {
          message += ` Obsidian: ${lastResult.obsidian} files.`;
        }
        if (lastResult.codebases) {
          message += ` Codebases: ${lastResult.codebases} files.`;
        }
        
        mainWindow?.webContents.send('index-progress', { message });
        
        return {
          status: 'complete',
          result: lastResult
        };
      } else {
        // Still in progress
        mainWindow?.webContents.send('index-progress', { 
          message: `Indexing in progress... (${attempts}s)` 
        });
      }
    }

    // Timeout
    throw new Error('Indexing timed out after 2 minutes');
  } catch (error) {
    throw new Error(`Indexing failed: ${error.message}`);
  }
}

/**
 * Query Polly
 */
async function queryPolly(query, options = {}) {
  const fetch = (await import('node-fetch')).default;

  try {
    const response = await fetch('http://localhost:11436/polly/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query,
        mode: options.mode || 'auto',
        tier: options.tier || 'balanced',
        stream: false,
        conversation_history: options.conversation_history || []
      })
    });

    if (!response.ok) {
      // Try to get error details from response body
      let errorDetail = `Server error: ${response.status}`;
      try {
        const errorBody = await response.text();
        if (errorBody) {
          errorDetail += ` - ${errorBody}`;
        }
      } catch (e) {
        // Ignore if we can't read error body
      }
      console.error('Query error:', errorDetail);
      throw new Error(errorDetail);
    }

    return await response.json();
  } catch (error) {
    console.error('Query failed:', error);
    throw new Error(`Query failed: ${error.message}`);
  }
}

/**
 * Promise wrapper for exec
 * 
 * SECURITY WARNING (Phase 23.5): Only use with hardcoded commands or controlled inputs.
 * Never pass user input directly to this function without validation.
 * All current uses are safe (version checks, setup commands with controlled paths).
 * 
 * @param {string} command - Command to execute (must be trusted)
 * @returns {Promise<string>} Command output
 */
function execPromise(command) {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) {
        reject(error);
      } else {
        resolve(stdout);
      }
    });
  });
}

// ============================================
// Keytar / Credential Management
// ============================================

const KEYTAR_SERVICE = 'Polly';

/**
 * Store credential in OS keychain
 */
async function storeCredential(account, password) {
  try {
    await keytar.setPassword(KEYTAR_SERVICE, account, password);
    return { success: true };
  } catch (error) {
    console.error('Failed to store credential:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Get credential from OS keychain
 */
async function getCredential(account) {
  try {
    const password = await keytar.getPassword(KEYTAR_SERVICE, account);
    return { success: true, password };
  } catch (error) {
    console.error('Failed to get credential:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Delete credential from OS keychain
 */
async function deleteCredential(account) {
  try {
    await keytar.deletePassword(KEYTAR_SERVICE, account);
    return { success: true };
  } catch (error) {
    console.error('Failed to delete credential:', error);
    return { success: false, error: error.message };
  }
}

// ============================================
// GitHub OAuth Flow
// ============================================

// GitHub OAuth configuration
const GITHUB_OAUTH_URL = 'https://github.com/login/oauth/authorize';
const GITHUB_TOKEN_URL = 'https://github.com/login/oauth/access_token';
const GITHUB_REDIRECT_URI = 'http://localhost:3000/oauth/callback';

/**
 * Start GitHub OAuth flow
 */
async function startGitHubOAuth() {
  // Get OAuth config from electron-store
  const GITHUB_CLIENT_ID = store.get('github_oauth_client_id');
  const GITHUB_CLIENT_SECRET = store.get('github_oauth_client_secret');
  
  if (!GITHUB_CLIENT_ID || !GITHUB_CLIENT_SECRET) {
    return {
      success: false,
      error: 'GitHub OAuth not configured. Please configure your Client ID and Secret in Settings → Integrations.'
    };
  }

  return new Promise((resolve) => {
    // Create OAuth window
    const oauthWindow = new BrowserWindow({
      width: 600,
      height: 800,
      show: false,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true
      },
      parent: mainWindow,
      modal: true
    });

    const authUrl = `${GITHUB_OAUTH_URL}?client_id=${GITHUB_CLIENT_ID}&redirect_uri=${encodeURIComponent(GITHUB_REDIRECT_URI)}&scope=repo,read:user`;
    
    oauthWindow.loadURL(authUrl);
    oauthWindow.show();

    // Listen for redirect
    oauthWindow.webContents.on('will-redirect', async (event, url) => {
      if (url.startsWith(GITHUB_REDIRECT_URI)) {
        const urlParams = new URL(url).searchParams;
        const code = urlParams.get('code');
        
        if (code) {
          // Exchange code for access token
          try {
            const fetch = (await import('node-fetch')).default;
            const tokenResponse = await fetch(GITHUB_TOKEN_URL, {
              method: 'POST',
              headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                client_id: GITHUB_CLIENT_ID,
                client_secret: GITHUB_CLIENT_SECRET,
                code: code,
                redirect_uri: GITHUB_REDIRECT_URI
              })
            });
            
            const tokenData = await tokenResponse.json();
            
            if (tokenData.access_token) {
              // Store token securely in keychain
              await storeCredential('github_token', tokenData.access_token);
              
              // Get user info
              const userResponse = await fetch('https://api.github.com/user', {
                headers: {
                  'Authorization': `token ${tokenData.access_token}`,
                  'Accept': 'application/vnd.github.v3+json'
                }
              });
              
              const userData = await userResponse.json();
              
              resolve({
                success: true,
                token: tokenData.access_token,
                username: userData.login
              });
            } else {
              resolve({
                success: false,
                error: 'No access token received from GitHub'
              });
            }
          } catch (error) {
            resolve({
              success: false,
              error: error.message
            });
          }
        } else {
          resolve({
            success: false,
            error: 'No authorization code received'
          });
        }
        
        oauthWindow.close();
      }
    });

    oauthWindow.on('closed', () => {
      resolve({
        success: false,
        error: 'OAuth window closed by user'
      });
    });
  });
}

// ============================================
// IPC Handlers
// ============================================

ipcMain.handle('get-store', (event, key) => {
  return store.get(key);
});

ipcMain.handle('set-store', (event, key, value) => {
  store.set(key, value);
});

// VSCode BrowserView handlers
console.log('[VSCode] Registering IPC handlers...');
ipcMain.handle('show-vscode', () => {
  console.log('[VSCode] show-vscode handler called');
  try {
    showVSCodeView();
    return { success: true };
  } catch (error) {
    console.error('[VSCode] Error showing BrowserView:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('hide-vscode', () => {
  console.log('[VSCode] hide-vscode handler called');
  try {
    hideVSCodeView();
    return { success: true };
  } catch (error) {
    console.error('[VSCode] Error hiding BrowserView:', error);
    return { success: false, error: error.message };
  }
});
console.log('[VSCode] IPC handlers registered');

ipcMain.handle('check-dependencies', async () => {
  return await checkDependencies();
});

ipcMain.handle('run-setup', async (event, options) => {
  try {
    await runSetup(options);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('start-server', async () => {
  try {
    // First check if server is already running via health check
    try {
      let fetchFn;
      if (global.fetch) {
        fetchFn = global.fetch;
      } else {
        fetchFn = (await import('node-fetch')).default;
      }
      
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 2000);
      const response = await fetchFn('http://localhost:11436/health', { 
        signal: controller.signal 
      });
      clearTimeout(timeout);
      
      if (response.ok) {
        console.log('Server already running, no need to start');
        return { success: true, message: 'Server already running' };
      }
    } catch (healthError) {
      // Health check failed, proceed with starting server
      console.log('Health check failed, will start server');
    }
    
    await startPollyServer();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-server', async () => {
  await stopPollyServer();
  return { success: true, message: 'Server stopped' };
});

ipcMain.handle('get-server-status', async () => {
  // Check if pollyServer process exists and is tracked
  // Don't rely solely on health endpoint since file watcher can block it
  if (pollyServer && pollyServer.pid) {
    try {
      // Check if process is actually running
      process.kill(pollyServer.pid, 0); // Signal 0 just checks if process exists
      return { running: true };
    } catch (e) {
      // Process doesn't exist
      pollyServer = null;
      return { running: false };
    }
  }
  
  // If no tracked process, try health endpoint as fallback
  try {
    let fetchFn;
    if (global.fetch) {
      fetchFn = global.fetch;
    } else {
      fetchFn = (await import('node-fetch')).default;
    }
    
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    
    const response = await fetchFn('http://localhost:11436/health', { 
      signal: controller.signal 
    });
    clearTimeout(timeout);
    
    return { running: response.ok };
  } catch (error) {
    return { running: false };
  }
});

ipcMain.handle('get-ollama-status', async () => {
  const running = await isOllamaRunning();
  return { running };
});

ipcMain.handle('start-ollama', async () => {
  try {
    await startOllamaServer();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-ollama', () => {
  stopOllamaServer();
  return { success: true };
});

ipcMain.handle('index-knowledge', async (event, options) => {
  try {
    const result = await indexKnowledgeBase(options);
    return { success: true, result };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('query', async (event, query, options) => {
  try {
    const result = await queryPolly(query, options);
    return { success: true, result };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  
  if (result.canceled || !result.filePaths || result.filePaths.length === 0) {
    return { success: false, path: null };
  }
  
  return { success: true, path: result.filePaths[0] };
});

ipcMain.handle('select-directories', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'multiSelections']
  });
  return result.canceled ? [] : result.filePaths;
});

// Config management handlers
ipcMain.handle('get-config', async (event, key) => {
  try {
    const configPath = path.join(app.getPath('home'), '.polly', 'config.yaml');
    
    if (!fs.existsSync(configPath)) {
      return { success: false, error: 'Config file not found' };
    }
    
    const yaml = require('js-yaml');
    const config = yaml.load(fs.readFileSync(configPath, 'utf8')) || {};
    
    // Support dot notation (e.g., 'obsidian.vault_path')
    const keys = key.split('.');
    let value = config;
    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return { success: false, error: 'Key not found' };
      }
    }
    
    return { success: true, value };
  } catch (error) {
    console.error('Error getting config:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('update-config', async (event, key, value) => {
  try {
    const configDir = path.join(app.getPath('home'), '.polly');
    const configPath = path.join(configDir, 'config.yaml');
    
    // Ensure directory exists
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }
    
    const yaml = require('js-yaml');
    let config = {};
    
    if (fs.existsSync(configPath)) {
      config = yaml.load(fs.readFileSync(configPath, 'utf8')) || {};
    }
    
    // Support dot notation (e.g., 'obsidian.vault_path')
    const keys = key.split('.');
    let obj = config;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (!(k in obj) || typeof obj[k] !== 'object') {
        obj[k] = {};
      }
      obj = obj[k];
    }
    
    obj[keys[keys.length - 1]] = value;
    
    // Write config file with options to prevent line wrapping
    fs.writeFileSync(configPath, yaml.dump(config, {
      lineWidth: -1,  // Disable line wrapping
      noCompatMode: true
    }), 'utf8');
    
    console.log(`Updated config: ${key} = ${value}`);
    
    return { success: true };
  } catch (error) {
    console.error('Error updating config:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url);
});

// Keytar / Credential handlers
ipcMain.handle('keytar-set', async (event, account, password) => {
  return await storeCredential(account, password);
});

ipcMain.handle('keytar-get', async (event, account) => {
  return await getCredential(account);
});

ipcMain.handle('keytar-delete', async (event, account) => {
  return await deleteCredential(account);
});

// GitHub OAuth handler
ipcMain.handle('github-oauth', async () => {
  return await startGitHubOAuth();
});

// Integration handlers
ipcMain.handle('integration-connect', async (event, integration, credentials) => {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://localhost:11436/polly/integrations/connect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ integration, credentials })
    });
    
    if (!response.ok) {
      const error = await response.text();
      return { success: false, error };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Integration connect failed:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('integration-sync', async (event, integration, options) => {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://localhost:11436/polly/integrations/sync', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ integration, options })
    });
    
    if (!response.ok) {
      const error = await response.text();
      return { success: false, error };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Integration sync failed:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('integration-status', async () => {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://localhost:11436/polly/integrations', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
      const error = await response.text();
      return { success: false, error };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Integration status failed:', error);
    return { success: false, error: error.message };
  }
});

// ============================================
// File Operations
// ============================================

// Read file content
ipcMain.handle('read-file', async (event, filePath) => {
  try {
    const content = await fs.promises.readFile(filePath, 'utf-8');
    return { success: true, content };
  } catch (error) {
    console.error('Error reading file:', error);
    return { success: false, error: error.message };
  }
});

// Write file handler (Phase 16c - for Scribe persona note saving)
ipcMain.handle('write-file', async (event, filePath, content) => {
  try {
    // Ensure directory exists
    const dir = path.dirname(filePath);
    await fs.promises.mkdir(dir, { recursive: true });
    
    // Write file
    await fs.promises.writeFile(filePath, content, 'utf-8');
    
    return { success: true };
  } catch (error) {
    console.error('Error writing file:', error);
    return { success: false, error: error.message };
  }
});

// ============================================
// Conversation Management Handlers
// ============================================

// Check if ConversationManager is ready
ipcMain.handle('conversation-manager-status', async () => {
  return {
    initialized: conversationManager !== null,
    error: conversationManager === null ? 'ConversationManager is null' : null
  };
});

// Create conversation
ipcMain.handle('conversation-create', async (event, data) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.createConversation(data);
  } catch (error) {
    console.error('Failed to create conversation:', error);
    throw error;
  }
});

// Get conversation by ID
ipcMain.handle('conversation-get', async (event, id, options) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.getConversation(id, options);
  } catch (error) {
    console.error('Failed to get conversation:', error);
    throw error;
  }
});

// Update conversation
ipcMain.handle('conversation-update', async (event, id, updates) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.updateConversation(id, updates);
  } catch (error) {
    console.error('Failed to update conversation:', error);
    throw error;
  }
});

// Delete conversation
ipcMain.handle('conversation-delete', async (event, id, soft) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.deleteConversation(id, soft);
  } catch (error) {
    console.error('Failed to delete conversation:', error);
    throw error;
  }
});

// Get all conversations
ipcMain.handle('conversation-list', async (event, options) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.getAllConversations(options);
  } catch (error) {
    console.error('Failed to list conversations:', error);
    throw error;
  }
});

// Search conversations
ipcMain.handle('conversation-search', async (event, query, limit) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.searchConversations(query, limit);
  } catch (error) {
    console.error('Failed to search conversations:', error);
    throw error;
  }
});

// Add message to conversation
ipcMain.handle('message-add', async (event, conversationId, role, content, metadata) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.addMessage(conversationId, role, content, metadata);
  } catch (error) {
    console.error('Failed to add message:', error);
    throw error;
  }
});

// Get messages for conversation
ipcMain.handle('message-list', async (event, conversationId, limit, offset) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.getMessages(conversationId, limit, offset);
  } catch (error) {
    console.error('Failed to list messages:', error);
    throw error;
  }
});

// Get all categories
ipcMain.handle('category-list', async () => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.getAllCategories();
  } catch (error) {
    console.error('Failed to list categories:', error);
    throw error;
  }
});

// Create custom category
ipcMain.handle('category-create', async (event, data) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.createCategory(data);
  } catch (error) {
    console.error('Failed to create category:', error);
    throw error;
  }
});

// Toggle star status
ipcMain.handle('conversation-star-toggle', async (event, id) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.toggleStar(id);
  } catch (error) {
    console.error('Failed to toggle star:', error);
    throw error;
  }
});

// Toggle pin status
ipcMain.handle('conversation-pin-toggle', async (event, id) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.togglePin(id);
  } catch (error) {
    console.error('Failed to toggle pin:', error);
    throw error;
  }
});

// Set generated title
ipcMain.handle('conversation-set-title', async (event, id, title) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.setGeneratedTitle(id, title);
  } catch (error) {
    console.error('Failed to set title:', error);
    throw error;
  }
});

// Check if needs auto-title
ipcMain.handle('conversation-needs-title', async (event, id) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.needsAutoTitle(id);
  } catch (error) {
    console.error('Failed to check auto-title:', error);
    throw error;
  }
});

// Migrate old conversation
ipcMain.handle('conversation-migrate', async (event, messages, title) => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.migrateOldConversation(messages, title);
  } catch (error) {
    console.error('Failed to migrate conversation:', error);
    throw error;
  }
});

// Get conversation stats
ipcMain.handle('conversation-stats', async () => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.getStats();
  } catch (error) {
    console.error('Failed to get stats:', error);
    throw error;
  }
});

// Cleanup old conversations
ipcMain.handle('conversation-cleanup', async () => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.cleanupOldConversations();
  } catch (error) {
    console.error('Failed to cleanup conversations:', error);
    throw error;
  }
});

// Enforce conversation limit
ipcMain.handle('conversation-enforce-limit', async () => {
  try {
    if (!conversationManager) {
      throw new Error('ConversationManager not initialized');
    }
    return conversationManager.enforceLimit();
  } catch (error) {
    console.error('Failed to enforce limit:', error);
    throw error;
  }
});

// ============================================
// App Lifecycle
// ============================================

app.whenReady().then(async () => {
  // Verify VSCode handlers are registered
  console.log('[VSCode] Verifying IPC handlers on app ready...');
  const handlers = ipcMain.listenerCount('show-vscode');
  console.log('[VSCode] show-vscode handler count:', handlers);
  if (handlers === 0) {
    console.error('[VSCode] WARNING: show-vscode handler not registered!');
  }
  
  // Initialize ConversationManager
  try {
    const dbPath = path.join(app.getPath('userData'), 'conversations.db');
    console.log('=== ConversationManager Initialization ===');
    console.log('DB Path:', dbPath);
    console.log('Creating ConversationManager...');
    conversationManager = new ConversationManager(dbPath);
    console.log('ConversationManager created successfully');
    console.log('ConversationManager type:', typeof conversationManager);
    console.log('ConversationManager.db:', conversationManager.db);
    console.log('=== ConversationManager Initialized ===');
  } catch (error) {
    console.error('!!! FAILED to initialize ConversationManager !!!');
    console.error('Error:', error.message);
    console.error('Stack:', error.stack);
    // Set to null explicitly
    conversationManager = null;
    
    // Show error dialog
    setTimeout(() => {
      dialog.showErrorBox(
        'Database Initialization Failed',
        'Failed to initialize conversation database:\n\n' + error.message + '\n\nCheck console for details.'
      );
    }, 1000);
  }

  createWindow();
  createTray();

  // Auto-start services if setup is complete
  if (store.get('setupComplete')) {
    console.log('Setup complete, starting services...');
    
    // Start Ollama first
    try {
      console.log('Starting Ollama...');
      await startOllamaServer();
    } catch (err) {
      console.error('Failed to start Ollama:', err);
    }
    
    // Then start Python server
    try {
      console.log('Starting Polly server...');
      await startPollyServer();
    } catch (err) {
      console.error('Failed to auto-start server:', err);
    }
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    } else {
      mainWindow.show();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Prevent second before-quit from waiting again when we call app.quit() after shutdown
let quitHandled = false;

app.on('before-quit', (event) => {
  if (quitHandled) return;
  event.preventDefault();
  quitHandled = true;
  isQuitting = true;
  console.log('Shutting down services...');

  stopPollyServer()
    .then(() => {
      stopOllamaServer();
      if (conversationManager) {
        conversationManager.close();
        console.log('ConversationManager closed');
      }
      app.quit();
    })
    .catch((err) => {
      console.error('Error during shutdown:', err);
      app.quit();
    });
});

// Handle certificate errors in development
app.on('certificate-error', (event, webContents, url, error, certificate, callback) => {
  if (isDev) {
    event.preventDefault();
    callback(true);
  } else {
    callback(false);
  }
});

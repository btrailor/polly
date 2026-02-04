"""
Apollo Dashboard
A visual interface to see system status and test queries

Run with: python -m interfaces.dashboard
Opens a local web interface at http://localhost:8080
"""

import json
from pathlib import Path


def generate_dashboard_html() -> str:
    """Generate the dashboard HTML."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apollo Dashboard</title>
    <style>
        :root {
            --bg: #1a1a2e;
            --surface: #16213e;
            --primary: #e94560;
            --secondary: #0f3460;
            --text: #eaeaea;
            --text-dim: #8892b0;
            --sigils: #61afef;
            --signals: #c678dd;
            --scrolls: #98c379;
            --glyphs: #e5c07b;
            --grids: #e06c75;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'SF Mono', 'Fira Code', monospace;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 2rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid var(--secondary);
        }

        h1 {
            font-size: 2rem;
            background: linear-gradient(135deg, var(--primary), var(--signals));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .status-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: var(--surface);
            border-radius: 20px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4caf50;
        }

        .status-dot.offline {
            background: #f44336;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .card {
            background: var(--surface);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--secondary);
        }

        .card h2 {
            font-size: 1rem;
            color: var(--text-dim);
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }

        .stat-label {
            color: var(--text-dim);
            font-size: 0.875rem;
        }

        .domains-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.5rem;
        }

        .domain {
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            font-size: 0.75rem;
            text-transform: uppercase;
        }

        .domain.sigils { background: rgba(97, 175, 239, 0.2); border: 1px solid var(--sigils); }
        .domain.signals { background: rgba(198, 120, 221, 0.2); border: 1px solid var(--signals); }
        .domain.scrolls { background: rgba(152, 195, 121, 0.2); border: 1px solid var(--scrolls); }
        .domain.glyphs { background: rgba(229, 192, 123, 0.2); border: 1px solid var(--glyphs); }
        .domain.grids { background: rgba(224, 108, 117, 0.2); border: 1px solid var(--grids); }

        .chat-container {
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--secondary);
            overflow: hidden;
        }

        .chat-header {
            padding: 1rem 1.5rem;
            background: var(--secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 1.5rem;
        }

        .message {
            margin-bottom: 1rem;
            padding: 1rem;
            border-radius: 8px;
            max-width: 85%;
        }

        .message.user {
            background: var(--secondary);
            margin-left: auto;
        }

        .message.assistant {
            background: rgba(233, 69, 96, 0.1);
            border-left: 3px solid var(--primary);
        }

        .message.system {
            background: rgba(152, 195, 121, 0.1);
            font-size: 0.875rem;
            color: var(--text-dim);
        }

        .chat-input {
            display: flex;
            gap: 1rem;
            padding: 1rem 1.5rem;
            background: var(--bg);
            border-top: 1px solid var(--secondary);
        }

        .chat-input input {
            flex: 1;
            padding: 0.75rem 1rem;
            background: var(--surface);
            border: 1px solid var(--secondary);
            border-radius: 8px;
            color: var(--text);
            font-family: inherit;
            font-size: 1rem;
        }

        .chat-input input:focus {
            outline: none;
            border-color: var(--primary);
        }

        .chat-input button {
            padding: 0.75rem 1.5rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-family: inherit;
            font-weight: bold;
        }

        .chat-input button:hover {
            opacity: 0.9;
        }

        .mode-selector {
            display: flex;
            gap: 0.5rem;
        }

        .mode-btn {
            padding: 0.5rem 1rem;
            background: var(--bg);
            border: 1px solid var(--secondary);
            color: var(--text-dim);
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.875rem;
        }

        .mode-btn.active {
            background: var(--primary);
            border-color: var(--primary);
            color: white;
        }

        .source-list {
            max-height: 200px;
            overflow-y: auto;
        }

        .source-item {
            padding: 0.5rem;
            border-bottom: 1px solid var(--secondary);
            font-size: 0.875rem;
            display: flex;
            justify-content: space-between;
        }

        .source-item:last-child {
            border-bottom: none;
        }

        .source-type {
            font-size: 0.75rem;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            background: var(--bg);
        }

        .loading {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--text-dim);
        }

        .loading-spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--secondary);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        pre {
            background: var(--bg);
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 0.875rem;
            margin: 0.5rem 0;
        }

        code {
            font-family: 'SF Mono', 'Fira Code', monospace;
        }

        .pattern-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .pattern-tag {
            padding: 0.25rem 0.75rem;
            background: var(--bg);
            border-radius: 20px;
            font-size: 0.75rem;
            border: 1px solid var(--secondary);
        }

        .quick-actions {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }

        .quick-btn {
            padding: 0.5rem 1rem;
            background: var(--bg);
            border: 1px solid var(--secondary);
            color: var(--text);
            border-radius: 6px;
            cursor: pointer;
            font-family: inherit;
            font-size: 0.875rem;
        }

        .quick-btn:hover {
            border-color: var(--primary);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌙 Apollo</h1>
            <div class="status-badge">
                <div class="status-dot" id="status-dot"></div>
                <span id="status-text">Connecting...</span>
            </div>
        </header>

        <div class="grid">
            <div class="card">
                <h2>RAG Database</h2>
                <div class="stat-value" id="total-chunks">-</div>
                <div class="stat-label">Total Chunks Indexed</div>
                <div style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Obsidian</span>
                        <span id="obsidian-count">-</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Codebase</span>
                        <span id="codebase-count">-</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Documents</span>
                        <span id="documents-count">-</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Domains</h2>
                <div class="domains-grid">
                    <div class="domain sigils">Sigils<br>Code</div>
                    <div class="domain signals">Signals<br>Audio</div>
                    <div class="domain scrolls">Scrolls<br>Writing</div>
                    <div class="domain glyphs">Glyphs<br>Visual</div>
                    <div class="domain grids">Grids<br>Systems</div>
                </div>
            </div>

            <div class="card">
                <h2>Learned Patterns</h2>
                <div class="stat-value" id="pattern-count">-</div>
                <div class="stat-label">Patterns Discovered</div>
                <div class="pattern-list" id="pattern-list" style="margin-top: 1rem;">
                    <!-- Patterns populated dynamically -->
                </div>
            </div>

            <div class="card">
                <h2>Knowledge Graph</h2>
                <div style="display: flex; gap: 2rem;">
                    <div>
                        <div class="stat-value" id="entity-count">-</div>
                        <div class="stat-label">Entities</div>
                    </div>
                    <div>
                        <div class="stat-value" id="relationship-count">-</div>
                        <div class="stat-label">Relationships</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="chat-container">
            <div class="chat-header">
                <span>Query Apollo</span>
                <div class="mode-selector">
                    <button class="mode-btn active" data-mode="auto">Auto</button>
                    <button class="mode-btn" data-mode="local">Local</button>
                    <button class="mode-btn" data-mode="cloud">Cloud</button>
                </div>
            </div>
            <div class="chat-messages" id="chat-messages">
                <div class="message system">
                    Welcome to Apollo! Ask questions about your knowledge base, code patterns, or anything else.
                </div>
            </div>
            <div class="chat-input">
                <input type="text" id="query-input" placeholder="What patterns do I use for MIDI handling?" />
                <button onclick="sendQuery()">Send</button>
            </div>
            <div class="quick-actions" style="padding: 0 1.5rem 1rem;">
                <button class="quick-btn" onclick="quickQuery('What are my audio programming patterns?')">Audio Patterns</button>
                <button class="quick-btn" onclick="quickQuery('Show my infrastructure setup')">Infrastructure</button>
                <button class="quick-btn" onclick="quickQuery('What frameworks do I use?')">Frameworks</button>
                <button class="quick-btn" onclick="quickQuery('Cross-domain connections')">Cross-Domain</button>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:11436';
        let currentMode = 'auto';

        // Mode selector
        document.querySelectorAll('.mode-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentMode = btn.dataset.mode;
            });
        });

        // Enter to send
        document.getElementById('query-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendQuery();
        });

        async function checkStatus() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();

                document.getElementById('status-dot').classList.remove('offline');
                document.getElementById('status-text').textContent = 'Online';

                // Update RAG stats
                const ragStats = data.rag_stats || {};
                let total = 0;

                if (ragStats.obsidian) {
                    document.getElementById('obsidian-count').textContent = ragStats.obsidian.count || 0;
                    total += ragStats.obsidian.count || 0;
                }
                if (ragStats.codebase) {
                    document.getElementById('codebase-count').textContent = ragStats.codebase.count || 0;
                    total += ragStats.codebase.count || 0;
                }
                if (ragStats.documents) {
                    document.getElementById('documents-count').textContent = ragStats.documents.count || 0;
                    total += ragStats.documents.count || 0;
                }

                document.getElementById('total-chunks').textContent = total.toLocaleString();

            } catch (error) {
                document.getElementById('status-dot').classList.add('offline');
                document.getElementById('status-text').textContent = 'Offline';
            }
        }

        async function fetchStats() {
            try {
                const response = await fetch(`${API_BASE}/apollo/stats`);
                const data = await response.json();

                // Patterns
                if (data.patterns !== undefined) {
                    document.getElementById('pattern-count').textContent = data.patterns;
                }

                // Graph
                if (data.graph) {
                    document.getElementById('entity-count').textContent = data.graph.entities || 0;
                    document.getElementById('relationship-count').textContent = data.graph.relationships || 0;
                }

            } catch (error) {
                console.error('Failed to fetch stats:', error);
            }
        }

        function addMessage(role, content) {
            const messages = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = `message ${role}`;

            // Simple markdown-like rendering
            content = content
                .replace(/```(\\w*)?\\n?([\\s\\S]*?)```/g, '<pre><code>$2</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>')
                .replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\n/g, '<br>');

            div.innerHTML = content;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function addLoading() {
            const messages = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = 'message assistant';
            div.id = 'loading-message';
            div.innerHTML = '<div class="loading"><div class="loading-spinner"></div>Thinking...</div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function removeLoading() {
            const loading = document.getElementById('loading-message');
            if (loading) loading.remove();
        }

        async function sendQuery() {
            const input = document.getElementById('query-input');
            const query = input.value.trim();
            if (!query) return;

            addMessage('user', query);
            input.value = '';
            addLoading();

            try {
                const response = await fetch(`${API_BASE}/apollo/query`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        query: query,
                        mode: currentMode,
                        stream: false
                    })
                });

                removeLoading();

                if (response.ok) {
                    const data = await response.json();
                    addMessage('assistant', data.response);
                } else {
                    addMessage('system', 'Error: Failed to get response');
                }

            } catch (error) {
                removeLoading();
                addMessage('system', `Error: ${error.message}`);
            }
        }

        function quickQuery(query) {
            document.getElementById('query-input').value = query;
            sendQuery();
        }

        // Initialize
        checkStatus();
        fetchStats();

        // Refresh status every 30 seconds
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>'''


def run_dashboard(port: int = 8080):
    """Run a simple dashboard server."""
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import tempfile
    import webbrowser

    # Create temp directory with dashboard
    temp_dir = Path(tempfile.mkdtemp())
    dashboard_path = temp_dir / "index.html"
    dashboard_path.write_text(generate_dashboard_html())

    class DashboardHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(temp_dir), **kwargs)

    print(f"\n=== Apollo Dashboard ===")
    print(f"Opening http://localhost:{port}")
    print("Press Ctrl+C to stop\n")

    server = HTTPServer(('localhost', port), DashboardHandler)

    # Open browser
    webbrowser.open(f"http://localhost:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    run_dashboard()

# Phase 29: Built-in Browser + DevTools

**Status:** 📋 Planned  
**Priority:** LOW (Nice-to-Have)  
**Estimated Effort:** 2-3 weeks  
**Target Date:** Q4 2026  
**Depends On:** Phase 17 (Code Workspace), Phase 27 (Designer Persona)

---

## Overview

Embed a basic web browser with developer tools directly into Polly, enabling AI-powered web development, UI analysis, and interactive debugging without leaving the application.

**Your Vision (From Brain Dump):**
> "What if Polly had its own **basic web browser with dev-tools** that it could access and use to **analyze other websites' code and the UI of apps** that it is working to develop?"

---

## User Problem

**Current State:**
- Developing web apps requires external browser
- Context switching: Polly → Browser → DevTools → Polly
- AI can't "see" what you're building
- Manual copy-paste of HTML/CSS/JS for analysis
- No way to test Polly-generated code immediately

**Pain Points:**
```
Scenario 1: Building a web UI
- Polly generates HTML/CSS
- User copies to external editor
- Opens in browser to test
- Finds issue, goes back to Polly
- Describes problem to Polly
- Polly can't see the actual rendering

Scenario 2: Analyzing competitor site
- User: "Make a page like website.com"
- Polly can't access the site
- User screenshots and describes
- Polly guesses at implementation
- Result doesn't match

Scenario 3: Debugging UI
- Bug in Polly-generated code
- User inspects in Chrome DevTools
- Finds CSS issue
- Reports back to Polly
- Polly fixes blindly (no visual feedback)
```

**Desired State:**
- Polly can render HTML/CSS/JS directly
- AI can inspect DOM, styles, network requests
- Test UI changes in real-time
- Analyze any website for learning
- Debug alongside you

---

## Key Features

### 1. Embedded Browser

**Technology:** Electron's webview or Chromium embedded

**Capabilities:**
- Render HTML/CSS/JavaScript
- Execute modern web standards
- Support responsive preview (multiple device sizes)
- Isolated from Polly's main UI (separate process)

**UI Location:**
```
Code Workspace Page:
├─ Left: File tree
├─ Center Top: Code editor
├─ Center Bottom: Embedded browser (NEW)
└─ Right: DevTools panel (NEW)
```

**Split View:**
```
┌─────────────────────────────────────────────────┐
│ Code Workspace                                  │
├─────────────────────────────────────────────────┤
│ ┌───────────────┬───────────────────────────┐   │
│ │ Editor        │ Browser Preview           │   │
│ │               │                           │   │
│ │ index.html    │  [Rendered page]          │   │
│ │ <html>        │   ┌─────────────────┐     │   │
│ │   <body>      │   │  My Web App     │     │   │
│ │     <h1>Hi</h1│   │  Hi             │     │   │
│ │   </body>     │   │  [Button]       │     │   │
│ │ </html>       │   └─────────────────┘     │   │
│ │               │                           │   │
│ └───────────────┴───────────────────────────┘   │
│ DevTools: [Elements] [Console] [Network]        │
│ ┌───────────────────────────────────────────┐   │
│ │ <div class="container">                   │   │
│ │   <h1>Hi</h1>                             │   │
│ │ </div>                                    │   │
│ └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 2. DevTools Integration

**Built-in Developer Tools:**

**Elements Panel:**
- Inspect DOM structure
- Live edit HTML
- View computed styles
- Highlight elements on hover

**Console:**
- JavaScript errors and logs
- Execute JS commands
- View console.log() output

**Network Panel:**
- HTTP requests made by page
- Response times, sizes
- Failed requests

**Styles Panel:**
- All CSS rules applied
- Computed values
- CSS cascade visualization

**Example:**
```
User: "Why is this button not centered?"

Polly (with DevTools access):
"Let me inspect the button...

[Analyzes DOM]

The button is inside a <div class="container">.
The container has `display: block` but no text-align.

To center it:
Option 1: Add `text-align: center` to container
Option 2: Add `margin: 0 auto` to button (if fixed width)

I recommend Option 1. Should I apply the fix?"
```

### 3. AI-Powered Website Analysis

**Capability:** Load any URL and analyze its structure

**Use Cases:**
1. **Learn from Examples:** "Build a nav bar like example.com"
2. **Competitive Analysis:** "What design patterns does competitor use?"
3. **Accessibility Audit:** "Check this site for WCAG compliance"
4. **Performance Analysis:** "Why is this page slow?"

**Example Interaction:**
```
User: "Analyze the design of stripe.com"

Polly:
"Loading stripe.com in browser...

[Fetches and renders]

🎨 Design Analysis:
═══════════════════════════════════════════

Layout:
• Fixed header with gradient background
• Full-width hero section
• Card-based feature grid
• Sticky CTA button

Colors:
• Primary: #635BFF (purple)
• Accent: #0A2540 (navy)
• Background: #FFFFFF
• Highlights: Linear gradient

Typography:
• Headings: Custom font 'Camphor', 48-72px
• Body: Inter, 16-18px
• Excellent hierarchy and spacing

Components:
• Glassmorphism cards (backdrop-filter)
• Animated gradient backgrounds
• Hover effects on interactive elements
• Smooth scroll animations

Performance:
• Page size: 2.3 MB
• Load time: 1.2s
• 15 HTTP requests
• Lazy-loaded images

Code Structure:
[Extracted from DevTools]

<header class='Header'>
  <nav>
    <a href='/'>Logo</a>
    <!-- Menu items -->
  </nav>
</header>

Key Takeaways:
1. Minimalist design with strong hierarchy
2. Strategic use of color (purple for CTAs)
3. Card-based information architecture
4. Performance-optimized (lazy loading)

Should I create a similar design for your project?"
```

### 4. Live Code Preview

**Capability:** See changes instantly as you code

**How It Works:**
```
1. User edits HTML/CSS/JS in Code Workspace
2. On save (or auto-save), browser refreshes
3. Polly observes rendered result
4. Can comment: "The header looks great!" or "Button is cut off"
```

**Hot Module Replacement (Advanced):**
- CSS changes without full refresh
- JavaScript module hot-swap
- React/Vue component live reload

**Example:**
```
User edits button CSS:
button {
  background: blue;  →  background: red;
}

[Browser updates immediately]

Polly: "The button color changed to red. 
        It stands out well against the white background!"
```

### 5. Responsive Testing

**Multiple Device Viewports:**
```
┌─────────────────────────────────────────────────┐
│ Preview: [Desktop ▼] [Tablet] [Mobile]         │
├─────────────────────────────────────────────────┤
│ Desktop (1920x1080)                             │
│ ┌───────────────────────────────────────────┐   │
│ │                                           │   │
│ │        [Full width layout]                │   │
│ │                                           │   │
│ └───────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│ Tablet (768x1024)                               │
│ ┌─────────────────┐                             │
│ │  [Responsive]   │                             │
│ │  [layout]       │                             │
│ └─────────────────┘                             │
├─────────────────────────────────────────────────┤
│ Mobile (375x667)                                │
│ ┌───────┐                                       │
│ │ Stack │                                       │
│ │ ─────│                                       │
│ │  Nav  │                                       │
│ └───────┘                                       │
└─────────────────────────────────────────────────┘
```

**Polly Analysis:**
```
User: "Check responsiveness"

Polly:
"Testing across viewports...

✅ Desktop (1920px): Looks great
✅ Tablet (768px): Responsive breakpoint working
⚠️  Mobile (375px): 
   - Nav menu overlaps content
   - Font size too large (16px → suggest 14px)
   - Button extends beyond screen edge

Suggested fixes:
1. Add hamburger menu for mobile
2. Reduce heading font size: 32px → 24px
3. Add padding: 0 16px to prevent overflow

Should I implement these fixes?"
```

### 6. Screenshot & DOM Extraction

**Capabilities:**
- Take screenshots of rendered page
- Extract HTML structure
- Copy CSS styles
- Export as code

**Use Cases:**
```
Scenario 1: Share preview
User: "Take a screenshot of the landing page"
Polly: [Captures and saves to vault/Screenshots/]
       "Saved to Screenshots/landing-page-2026-02-03.png"

Scenario 2: Learn from existing site
User: "Extract the HTML from this section"
      [Highlights element in browser]
Polly: [Copies HTML + CSS to clipboard]
       "Copied! The section uses a CSS Grid layout..."
```

---

## Technical Architecture

### Browser Component

```python
# core/browser/embedded_browser.py

class EmbeddedBrowser:
    """
    Chromium-based browser embedded in Polly
    """
    
    def __init__(self):
        self.process = None
        self.devtools = DevToolsConnection()
    
    def load_url(self, url: str):
        """
        Navigate to URL
        """
        self.process.loadURL(url)
    
    def load_html(self, html: str, base_url: str = ""):
        """
        Render HTML string
        """
        self.process.loadHTML(html, base_url)
    
    def execute_javascript(self, js_code: str) -> Any:
        """
        Run JS in page context
        """
        return self.process.executeJavaScript(js_code)
    
    def get_dom(self) -> str:
        """
        Extract current DOM as HTML
        """
        return self.execute_javascript("document.documentElement.outerHTML")
    
    def get_computed_styles(self, selector: str) -> dict:
        """
        Get computed CSS for element
        """
        js = f"""
        const el = document.querySelector('{selector}');
        const styles = window.getComputedStyle(el);
        return Array.from(styles).reduce((acc, key) => {{
            acc[key] = styles.getPropertyValue(key);
            return acc;
        }}, {{}});
        """
        return self.execute_javascript(js)
    
    def screenshot(self, path: str, full_page: bool = False):
        """
        Capture screenshot
        """
        self.process.capturePage().saveTo(path)
```

### DevTools Connection

```python
# core/browser/devtools.py

class DevToolsConnection:
    """
    Interface to Chrome DevTools Protocol
    """
    
    def __init__(self):
        self.ws = None  # WebSocket to DevTools
    
    async def connect(self):
        """
        Connect to DevTools via WebSocket
        """
        self.ws = await websockets.connect(self.devtools_url)
    
    async def send_command(self, method: str, params: dict = None):
        """
        Send DevTools Protocol command
        """
        message = {
            "id": self._next_id(),
            "method": method,
            "params": params or {}
        }
        await self.ws.send(json.dumps(message))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def get_dom_tree(self):
        """
        Get full DOM tree
        """
        return await self.send_command("DOM.getDocument")
    
    async def get_network_log(self):
        """
        Get network requests
        """
        await self.send_command("Network.enable")
        # Listen for Network.requestWillBeSent events
        # Return aggregated requests
    
    async def get_console_messages(self):
        """
        Get console logs
        """
        await self.send_command("Log.enable")
        # Listen for Log.entryAdded events
```

### Integration with Personas

#### Designer Persona

```python
# Designer can use browser to preview designs

class Designer(PersonaBase):
    
    def mockup_mode(self, context: DesignContext) -> MockupOutput:
        # Generate HTML/CSS mockup
        mockup_html = self._generate_mockup_html(context)
        
        # Render in browser
        self.browser.load_html(mockup_html)
        
        # Take screenshot for preview
        screenshot_path = self._screenshot_path()
        self.browser.screenshot(screenshot_path)
        
        # Analyze rendered result
        visual_analysis = self._analyze_rendered_output(
            self.browser.get_dom(),
            screenshot_path
        )
        
        return MockupOutput(
            html=mockup_html,
            screenshot=screenshot_path,
            analysis=visual_analysis
        )
```

#### Programmer Persona

```python
# Programmer can test code immediately

class Programmer(PersonaBase):
    
    def implement_mode(self, context: CodeContext) -> CodeOutput:
        # Generate code
        code = self._generate_code(context)
        
        # If web code, test in browser
        if self._is_web_code(code):
            self.browser.load_html(code['html'])
            
            # Check for errors
            console_errors = self.browser.devtools.get_console_messages()
            if console_errors:
                # Fix errors and regenerate
                code = self._fix_errors(code, console_errors)
        
        return CodeOutput(code=code, tested=True)
```

---

## Use Cases

### Use Case 1: Building a Landing Page

```
User: "Create a landing page for my app"

Architect: [Creates structure]

Designer: [Creates mockup]
          "Let me render this in the browser..."
          [Loads in embedded browser]
          [Screenshot]
          "Here's how it looks! The hero section is prominent,
           CTA button is clear. Should we proceed with code?"

User: "Yes, make the button bigger"

Designer: [Updates CSS]
          [Browser refreshes]
          "Done! The button is now 20% larger."

Programmer: [Implements full code]
            [Tests in browser]
            "All working! Console shows no errors.
             Tested on desktop, tablet, and mobile viewports."
```

### Use Case 2: Learning from Existing Site

```
User: "I want a navigation like github.com"

Polly: "Let me analyze GitHub's navigation..."
       [Loads github.com in browser]
       [Uses DevTools to inspect nav]
       
"GitHub's Navigation Structure:
═══════════════════════════════════════════════

<nav class='Header'>
  <div class='Header-item'>Logo</div>
  <div class='Header-item'>
    <input type='search' placeholder='Search GitHub' />
  </div>
  <div class='Header-item'>Profile menu</div>
</nav>

CSS:
.Header {
  display: flex;
  align-items: center;
  background: #24292f;
  padding: 16px;
}

.Header-item {
  margin-right: 16px;
}

Key Features:
• Flexbox layout for responsiveness
• Dark background (#24292f)
• Search bar prominently placed
• Profile menu aligned right

Should I implement a similar navigation for you?"
```

### Use Case 3: Debugging UI Issue

```
User: "The button isn't clickable"

Polly: "Let me inspect the button in DevTools..."
       [Opens Elements panel]
       [Finds button element]
       
"Found the issue:

The button has `pointer-events: none` CSS property.

Also, there's an overlay div positioned on top:
<div style='position: absolute; z-index: 999'></div>

This is blocking clicks.

Fixes:
1. Remove `pointer-events: none` from button
2. Lower z-index of overlay or remove it

Should I apply these fixes?"
```

---

## Frontend UI

### Browser Panel Component

```javascript
// frontend: embedded-browser-panel.js

class EmbeddedBrowserPanel {
    constructor() {
        this.iframe = null;
        this.devtoolsPanel = null;
    }
    
    render(containerId) {
        const panel = `
            <div class="browser-panel">
                <div class="browser-toolbar">
                    <input type="url" 
                           id="browser-url" 
                           placeholder="http://..." />
                    <button onclick="loadURL()">Go</button>
                    <button onclick="reload()">↻</button>
                    
                    <div class="viewport-selector">
                        <button data-viewport="desktop">Desktop</button>
                        <button data-viewport="tablet">Tablet</button>
                        <button data-viewport="mobile">Mobile</button>
                    </div>
                </div>
                
                <div class="browser-content">
                    <webview id="browser-webview" 
                             src="about:blank"
                             preload="./browser-preload.js">
                    </webview>
                </div>
                
                <div class="devtools-panel">
                    <div class="devtools-tabs">
                        <button data-panel="elements">Elements</button>
                        <button data-panel="console">Console</button>
                        <button data-panel="network">Network</button>
                    </div>
                    <div id="devtools-content"></div>
                </div>
            </div>
        `;
        
        document.getElementById(containerId).innerHTML = panel;
        this._attachEventListeners();
    }
    
    async loadURL(url) {
        const webview = document.getElementById('browser-webview');
        webview.src = url;
        
        // Notify backend that page loaded
        await api.post('/browser/navigate', { url });
    }
    
    async loadHTML(html) {
        const webview = document.getElementById('browser-webview');
        // Inject HTML into webview
        await webview.executeJavaScript(`
            document.open();
            document.write(\`${html}\`);
            document.close();
        `);
    }
    
    async getDevToolsData(panel) {
        // Request data from backend DevTools connection
        return await api.get(`/browser/devtools/${panel}`);
    }
}
```

---

## API Endpoints

```python
# Browser control endpoints

POST /browser/navigate
Request: { "url": "https://example.com" }

POST /browser/load-html
Request: { "html": "<html>...</html>" }

GET /browser/screenshot
Response: { "image_data": "base64..." }

GET /browser/dom
Response: { "html": "<!DOCTYPE html>..." }

# DevTools endpoints

GET /browser/devtools/elements
Response: { "dom_tree": {...} }

GET /browser/devtools/console
Response: { "messages": [...] }

GET /browser/devtools/network
Response: { "requests": [...] }

POST /browser/devtools/execute-js
Request: { "code": "console.log('hi')" }
Response: { "result": "hi" }

# Analysis endpoints

POST /browser/analyze-page
Response: {
    "structure": {...},
    "styles": {...},
    "performance": {...},
    "accessibility": {...}
}
```

---

## Success Criteria

### Phase 29 Complete When:

**Backend:**
- [x] Embedded browser process working
- [x] DevTools Protocol connection functional
- [x] Can load URLs and HTML strings
- [x] DOM extraction working
- [x] Screenshot capture functional
- [x] JavaScript execution working

**Frontend:**
- [x] Browser panel in Code Workspace
- [x] DevTools UI (elements, console, network)
- [x] Responsive viewport switcher
- [x] Live reload on code changes
- [x] URL bar and navigation

**AI Integration:**
- [x] Designer can preview mockups
- [x] Programmer can test code
- [x] Polly can analyze websites
- [x] Suggestions based on visual feedback

**Testing:**
- [x] Load and render complex sites (github.com, stripe.com)
- [x] DevTools accurately reports DOM/styles
- [x] No crashes or memory leaks
- [x] Performance acceptable (< 500ms render time)

---

## Technical Challenges

**Challenge 1: Memory Usage**
- Chromium processes are heavy (100-300 MB each)
- Solution: Single browser instance, reload between tasks

**Challenge 2: Security**
- Loading untrusted websites is risky
- Solution: Sandboxed webview, disable certain APIs

**Challenge 3: Performance**
- Rendering large sites can be slow
- Solution: Loading indicators, optional "lite mode"

**Challenge 4: DevTools Integration**
- Chrome DevTools Protocol is complex
- Solution: Implement subset of features (not full Chrome DevTools)

---

## Future Enhancements

### Phase 29b: Advanced DevTools
- Performance profiler
- Memory heap inspector
- Application panel (cookies, storage)
- Coverage analysis

### Phase 29c: Interactive Debugging
- Set breakpoints in Polly-generated code
- Step through JavaScript execution
- Variable inspection
- Call stack visualization

---

## Dependencies

**Required:**
- Phase 17: Code Workspace (location for browser panel)
- ✅ Phase 27: Designer Persona (uses browser for previews)

**Enhances:**
- Phase 25: Code Architecture (visualize app in browser)
- Phase 11c: Programmer persona (test code immediately)

---

**Document Created:** February 3, 2026  
**Status:** Ready for technical feasibility assessment  
**Next Step:** Test Electron webview capabilities, evaluate performance

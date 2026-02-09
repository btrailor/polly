# Floating Chat Input Bar - Design Document

**Date:** January 31, 2026  
**Feature:** Floating Chat Input Bar (Bottom of Screen)  
**Priority:** High (Major UX Evolution)  
**Status:** 🎨 Design Phase

---

## Vision

Transform Polly's chat from a sidebar-confined feature to a **persistent, floating assistant** available on every page. Model after OpenCode's elegant bottom chat interface.

### Current State
```
┌─────────────────────────────────────────────────────────────┐
│ Titlebar                                                     │
├──┬────────────────────────────┬─────────────────────────────┤
│🏠│ Main Content               │ Right Sidebar: CHAT         │
│📅│                            │ ┌─────────────────────────┐│
│✉️│                            │ │ Conversations List      ││
│💻│                            │ │ Active Chat Messages    ││
│📊│                            │ │ Chat Input (bottom)     ││
│  │                            │ └─────────────────────────┘│
└──┴────────────────────────────┴─────────────────────────────┘
```
**Problems:**
- Chat only visible when right sidebar open
- Can't chat while viewing other content
- Right sidebar cramped with multiple purposes
- Feels like "another page" not an "assistant"

### Proposed State
```
┌─────────────────────────────────────────────────────────────┐
│ Titlebar                                                     │
├──┬────────────────────────────┬─────────────────────────────┤
│🏠│ Main Content               │ Right Sidebar:              │
│📅│                            │ ┌─────────────────────────┐│
│✉️│                            │ │ Conversations Manager   ││
│💻│                            │ │ - List view             ││
│📊│                            │ │ - Search/filter         ││
│  │                            │ │ - Quick actions         ││
│  │                            │ └─────────────────────────┘│
├──┴────────────────────────────┴─────────────────────────────┤
│ 💬 [Model ▾] [Persona ▾] [Mode ▾] [⚡ Orchestrate]          │
│ ┌─────────────────────────────────────────────────────┐ [→]│
│ │ Ask Polly anything...                                │    │
│ └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
         ↑ FLOATING CHAT BAR (always visible)
```

---

## Design Specifications

### Component: Floating Chat Bar

**Position:** Fixed at bottom of window, above app frame  
**Height:** ~100-120px (adjustable based on textarea rows)  
**Width:** Full window width minus ribbon (48px left offset)  
**Z-index:** 100 (above content, below modals)

### Layout Structure

```html
<div class="floating-chat-container">
  <!-- Chat Controls Row -->
  <div class="floating-chat-controls">
    <div class="control-group">
      <label>Model:</label>
      <select id="floating-model-select">...</select>
    </div>
    <div class="control-group">
      <label>Persona:</label>
      <select id="floating-persona-select">...</select>
    </div>
    <div class="control-group">
      <label>Mode:</label>
      <select id="floating-mode-select">...</select>
    </div>
    <div class="orchestrator-toggle-container">
      <label>Orchestrate</label>
      <div class="orchestrator-toggle" id="floating-orchestrator-toggle"></div>
    </div>
    <div class="context-indicator">
      <i data-lucide="layout-dashboard"></i>
      <span>Dashboard</span>
    </div>
  </div>
  
  <!-- Chat Input Row -->
  <div class="floating-chat-input">
    <textarea 
      id="floating-query-input" 
      placeholder="Ask Polly anything..."
      rows="2"
    ></textarea>
    <button class="btn-send" id="floating-btn-send">
      <i data-lucide="send"></i>
    </button>
  </div>
  
  <!-- Cost Estimate -->
  <div class="cost-estimate hidden" id="floating-cost-estimate">
    <span>Estimated cost: <span id="floating-cost-value">-</span></span>
  </div>
</div>
```

### Visual Design

**Background:** `#1e1e1e` (matches sidebar)  
**Border:** `1px solid #2a2a2a` on top  
**Shadow:** `0 -4px 12px rgba(0,0,0,0.3)` (subtle lift)  
**Padding:** `12px 16px`  
**Border Radius:** None (flush with window edges)

**Controls:**
- Compact horizontal layout
- Model/Persona/Mode dropdowns: 120px width each
- Orchestrate toggle: right-aligned before context indicator
- Context indicator: Shows current page icon + name

**Textarea:**
- Auto-expand up to 6 rows
- Rounded corners: `6px`
- Background: `#252525`
- Border: `1px solid #2a2a2a`
- Focus: Border changes to `#3a3a3a` with subtle glow

**Send Button:**
- Circular: `40px × 40px`
- Primary color: `#2ea043` (matches existing)
- Hover: Slight scale and brightness increase
- Icon: Lucide `send` icon

---

## Right Sidebar Transformation

### Current Right Sidebar (Chat-Focused)
```
┌───────────────────────────┐
│ Chat                      │
├───────────────────────────┤
│ ▾ Conversations           │
│   [+ New Chat]            │
│   📍 Current conversation │
│   🌐 Website research     │
│                           │
├───────────────────────────┤
│ Active Chat               │
│ ┌───────────────────────┐ │
│ │ User: Hello           │ │
│ │ Assistant: Hi!        │ │
│ └───────────────────────┘ │
├───────────────────────────┤
│ [Model] [Persona] [Mode] │
│ [Chat input...]    [Send]│
└───────────────────────────┘
```

### Proposed Right Sidebar (Conversation Manager)
```
┌───────────────────────────┐
│ Conversations             │
├───────────────────────────┤
│ [+ New Chat]              │
│ [ Search conversations ]  │
│ [ Filter: All ▾ ]         │
├───────────────────────────┤
│ Today                     │
│ ┌─────────────────────┐   │
│ │ 📍 Current research │   │
│ │ 3 messages · 2m ago │   │
│ └─────────────────────┘   │
│ ┌─────────────────────┐   │
│ │ 🌐 Website analysis │   │
│ │ 12 messages · 1h ago│   │
│ └─────────────────────┘   │
├───────────────────────────┤
│ Yesterday                 │
│ ┌─────────────────────┐   │
│ │ 💻 Code review      │   │
│ │ 8 messages          │   │
│ └─────────────────────┘   │
├───────────────────────────┤
│ Last 7 Days               │
│ ...                       │
└───────────────────────────┘
```

**Features:**
- Dedicated conversation browser
- Search and filter
- Conversation cards with preview
- Quick actions (pin, rename, delete)
- Grouped by time period
- Hover shows full conversation preview

---

## Chat Message Display

### Option A: Overlay Modal (OpenCode-style)
When user sends a message, open a centered overlay showing the conversation:

```
┌─────────────────────────────────────────────────────────────┐
│ Main Content (dimmed)                                        │
│                                                              │
│    ┌──────────────────────────────────────────┐            │
│    │ Current Research              [X] Close  │            │
│    ├──────────────────────────────────────────┤            │
│    │ User: What are the key trends?           │            │
│    │                                          │            │
│    │ Assistant: Based on your research...     │            │
│    │ ...                                      │            │
│    │                                          │            │
│    │ User: Tell me more about...              │            │
│    │                                          │            │
│    │ Assistant: (typing...)                   │            │
│    └──────────────────────────────────────────┘            │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│ 💬 [Model] [Persona] [Mode] [⚡]                            │
│ [ Continue the conversation... ]                      [→]  │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Focused conversation view
- Content remains visible (dimmed)
- Easy to close and return to work
- Similar to OpenCode's design

**Cons:**
- Blocks main content
- Requires modal management
- Animation complexity

### Option B: Main Content Replacement
Main content area becomes the conversation view:

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Dashboard           Current Research          [...] │
├──────────────────────────────────────────────────────────────┤
│ User: What are the key trends?                               │
│                                                              │
│ Assistant: Based on your research...                         │
│ ...                                                          │
│                                                              │
│ User: Tell me more about...                                  │
│                                                              │
│ Assistant: (typing...)                                       │
├──────────────────────────────────────────────────────────────┤
│ 💬 [Model] [Persona] [Mode] [⚡]                            │
│ [ Continue the conversation... ]                      [→]  │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Simple implementation (existing view system)
- Full screen for conversation
- No modal complexity

**Cons:**
- Hides the page you were working on
- Feels like switching pages (old behavior)
- Loses context

### Option C: Split View (Side-by-side)
Main content shrinks, conversation appears alongside:

```
┌─────────────────────────┬───────────────────────────────────┐
│ Dashboard (50%)         │ Current Research         [X]     │
│                         ├───────────────────────────────────┤
│ [Dashboard content]     │ User: What are the trends?       │
│                         │                                  │
│                         │ Assistant: Based on...           │
│                         │                                  │
│                         │ User: Tell me more...            │
│                         │                                  │
│                         │ Assistant: (typing...)           │
├─────────────────────────┴───────────────────────────────────┤
│ 💬 [Model] [Persona] [Mode] [⚡]                            │
│ [ Continue the conversation... ]                      [→]  │
└──────────────────────────────────────────────────────────────┘
```

**Pros:**
- Keep both contexts visible
- Great for code review, document editing
- Professional multi-tasking feel

**Cons:**
- Complex layout management
- Less space for both elements
- May feel cramped on smaller screens

---

## Recommended Approach: Hybrid Model

**Default:** Option A (Overlay Modal)  
**Alternative:** Option C (Split View) - User can click "Split View" button

**Why:**
- Overlay gives focused conversation experience (OpenCode-style)
- Split view for power users who need side-by-side
- Best of both worlds
- Clean default, powerful option

---

## Context Awareness

The floating chat should **know which page you're on** and adjust behavior:

### Context Indicator
Show current page in chat controls:
```
[Model ▾] [Persona ▾] [Mode ▾] [⚡ Orchestrate] [📊 Dashboard ▾]
```

### Context Menu Options
- **Current Page** (default): Chat about current view
- **Global**: General questions
- **Switch to...**: Quick page switch

### Context Injection
When user sends a message, automatically inject page context:
```javascript
const context = {
  page: currentView, // 'dashboard', 'code', 'notes', etc.
  pageData: getCurrentPageData(), // Active document, selected code, etc.
};
```

---

## Implementation Plan

### Phase 1: Floating Chat Bar UI (Day 1)
**Files to modify:**
- `electron-app/src/renderer/index.html`
  - Add floating-chat-container after main-container
  - Keep existing right sidebar chat (for now)
- `electron-app/src/renderer/styles/floating-chat.css` (NEW)
  - Create floating chat styles
  - Responsive sizing
  - Animations
- `electron-app/src/renderer/app.js`
  - Duplicate chat event listeners for floating bar
  - Keep both functional

**Deliverable:** Floating bar visible and functional alongside existing chat

### Phase 2: Chat Overlay Modal (Day 2)
**Files to modify:**
- `electron-app/src/renderer/index.html`
  - Add chat-overlay-modal element
- `electron-app/src/renderer/styles/chat-overlay.css` (NEW)
  - Modal styles
  - Animations (fade in/out, slide up)
- `electron-app/src/renderer/app.js`
  - `showChatOverlay(conversationId)`
  - `hideChatOverlay()`
  - Message rendering in overlay
  - Keyboard shortcuts (Esc to close)

**Deliverable:** Overlay opens when user sends message from floating bar

### Phase 3: Right Sidebar Conversion (Day 3)
**Files to modify:**
- `electron-app/src/renderer/index.html`
  - Replace chat content with conversation manager
  - Remove old chat input
- `electron-app/src/renderer/styles/conversation-manager.css` (NEW)
  - Conversation card styles
  - Search/filter styles
- `electron-app/src/renderer/app.js`
  - Enhanced `renderConversationList()` for manager view
  - Conversation preview on hover
  - Search and filter functionality

**Deliverable:** Right sidebar is now a powerful conversation manager

### Phase 4: Context Awareness (Day 4)
**Files to modify:**
- `electron-app/src/renderer/app.js`
  - `getCurrentPageContext()`
  - Context indicator updates
  - Context injection in messages
- `interfaces/server.py`
  - Accept page context in chat endpoint
  - Use context in RAG retrieval

**Deliverable:** Chat knows which page you're on and responds accordingly

### Phase 5: Polish & Refinement (Day 5)
- Animations and transitions
- Keyboard shortcuts (Cmd+K to focus chat)
- Loading states
- Error handling
- Split view option
- Mobile responsiveness (if applicable)

---

## Technical Considerations

### State Management
```javascript
let floatingChatState = {
  isOverlayOpen: false,
  activeConversationId: null,
  isSplitView: false,
  context: {
    page: null,
    data: null
  }
};
```

### Event Handling
- **Send button click** → Open overlay with new message
- **Escape key** → Close overlay
- **Cmd+K** → Focus floating chat input
- **Cmd+Enter** → Send message without opening overlay (background)
- **Click conversation card** → Open overlay with that conversation

### Performance
- **Lazy load overlay** - Only render when needed
- **Virtualize conversation list** - For 100+ conversations
- **Debounce search** - Don't search on every keystroke
- **Memoize context** - Cache page context until page changes

---

## Accessibility

- **Keyboard navigation:** Tab through controls, Enter to send
- **Screen reader support:** ARIA labels for all controls
- **Focus management:** Trap focus in overlay when open
- **High contrast:** Ensure all colors meet WCAG AA standards

---

## Migration Strategy

### Step 1: Additive (No Removals)
- Add floating chat alongside existing right sidebar chat
- Both functional, user can use either
- Gather feedback

### Step 2: Feature Flag
- Add setting: "Enable floating chat (Beta)"
- Users can opt-in to test
- Gradual rollout

### Step 3: Transition
- Make floating chat default
- Keep right sidebar for conversation management
- Remove old chat input from sidebar

### Step 4: Cleanup
- Remove feature flag
- Remove old chat code
- Finalize documentation

---

## Success Metrics

**UX Goals:**
- ✅ Chat accessible from any page without navigation
- ✅ Conversation management feels organized and powerful
- ✅ Context-aware responses improve relevance
- ✅ Overlay feels smooth and non-disruptive

**Technical Goals:**
- ✅ No performance regression (<16ms render time)
- ✅ Works on all window sizes (min 1024px width)
- ✅ All existing chat features preserved
- ✅ Keyboard shortcuts work flawlessly

**User Feedback:**
- Conduct usability test with 3-5 users
- Track: Time to send first message (should decrease)
- Track: Conversation management actions (should increase)
- Survey: "Does Polly feel more like an assistant now?"

---

## Risks & Mitigations

**Risk:** Users confused by new layout  
**Mitigation:** Add "What's New" modal on first launch, highlight floating chat

**Risk:** Overlay blocks important content  
**Mitigation:** Ensure overlay is dismissible, add split view option

**Risk:** Context injection adds latency  
**Mitigation:** Inject context client-side, don't wait for server

**Risk:** Conversations hard to find without sidebar chat  
**Mitigation:** Enhanced search, recent conversations quick access

---

## Future Enhancements

1. **Conversation Threads:** Nested replies in long conversations
2. **Multi-Modal Input:** Voice input, image attachments
3. **Quick Actions:** Pre-defined prompts (Summarize, Explain, etc.)
4. **Conversation Analytics:** Token usage, response times
5. **Collaborative Chat:** Share conversations with team (future)

---

## Status

🎨 **DESIGN PHASE COMPLETE** - Ready for implementation

**Next Step:** Begin Phase 1 - Floating Chat Bar UI

---

**Document Owner:** Polly Development Team  
**Last Updated:** January 31, 2026  
**Related:** BRAIN_DUMP_2026-01-31.md, FEATURES_TO_BUILD.md #15

# Void Editor - Feature-Focused Analysis

**Date:** February 5, 2025  
**Status:** In Progress - Phase 1  
**Goal:** Understand Void's model integration and chat sidebar features

---

## Phase 1: Model Integration Investigation

### What We Need to Find Out

1. **Provider Support**
   - Which AI providers does Void support?
   - OpenAI? Anthropic? Others?
   - How are providers configured?

2. **Routing Logic**
   - How does Void select which model to use?
   - Is there automatic routing based on task type?
   - Can users manually select models?

3. **API Structure**
   - How is the model integration exposed?
   - Extension API? Core service?
   - How extensible is it?

4. **Comparison to Polly's Router**
   - How does it compare to Polly's multi-provider router?
   - What features does it have that Polly needs?
   - What's missing?

### Investigation Approach

**Option 1: Direct Codebase Analysis**
- Clone Void repository
- Search for model provider code
- Review chat/AI integration files
- Document findings

**Option 2: Documentation Review**
- Check Void's README and docs
- Look for feature documentation
- Review codebase guide
- Check GitHub issues/discussions

**Option 3: Community Research**
- Check Void's Discord/community
- Review recent PRs related to AI features
- Look for user discussions about model integration

---

## Phase 1: Chat Sidebar Investigation

### What We Need to Find Out

1. **UI Implementation**
   - How is the chat sidebar structured?
   - What UI framework/components?
   - How is it positioned (right sidebar, panel, etc.)?

2. **Message Handling**
   - How are messages displayed?
   - Streaming support?
   - Message history management?

3. **Context Awareness**
   - Does it include code context?
   - File selection awareness?
   - Workspace context?

4. **Customization Points**
   - How easy is it to customize?
   - What can be modified?
   - Extension points?

### Comparison to Polly's Requirements

**Polly's Chat Needs:**
- Right sidebar (collapsible)
- Code context integration
- Multi-model support
- Conversation history
- Save to notes functionality
- Model selection UI

**Questions:**
- How close is Void's implementation?
- What customization is needed?
- Can we use it mostly as-is?

---

## Known Information

### From Previous Analysis

1. **Void is a VSCode Fork**
   - Same codebase structure
   - Same build system (gulp/esbuild)
   - Same complexity

2. **Maintenance Status**
   - Paused maintenance
   - "Exploring novel coding ideas"
   - May not resume as IDE

3. **User's Assessment**
   - Model integration "elegantly handled"
   - Chat sidebar "very close" to what's needed
   - Could save significant development time

---

## Next Steps

1. **Clone Void Repository** (if not already done)
   ```bash
   git clone https://github.com/voideditor/void.git
   cd void
   ```

2. **Search for Model Integration Code**
   - Search for "model", "provider", "AI", "chat" in codebase
   - Review relevant files
   - Document structure

3. **Search for Chat Sidebar Code**
   - Search for "chat", "sidebar", "panel" in codebase
   - Review UI components
   - Document implementation

4. **Create Feature Comparison Matrix**
   - Void features vs. Polly requirements
   - Identify gaps
   - Estimate customization effort

---

## Questions to Answer

1. ✅ **What providers does Void support?**
2. ✅ **How does model routing work?**
3. ✅ **What's the chat sidebar implementation?**
4. ✅ **How close is it to Polly's needs?**
5. ✅ **What customization is required?**
6. ✅ **Can we maintain it ourselves?**

---

**Last Updated:** February 5, 2025

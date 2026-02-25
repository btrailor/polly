# Design: Streaming Chat Responses

## Architecture Impact

### Backend: Streaming Query Endpoint

**Option A (preferred): Add streaming mode to `/polly/query`**

Extend the existing `/polly/query` endpoint to accept a `stream: true` parameter. When streaming is enabled, the response is a `StreamingResponse` with `text/event-stream` content type. This preserves the full Polly pipeline (RAG context, persona, mental models, domain routing, compression) while streaming the LLM output.

```
POST /polly/query
Content-Type: application/json

{
  "query": "Explain the observer pattern",
  "stream": true,
  "persona": "professor",
  "conversation_id": "abc123",
  ...existing params...
}
```

**SSE event format:**

```
data: {"type": "token", "content": "The"}
data: {"type": "token", "content": " observer"}
data: {"type": "token", "content": " pattern"}
...
data: {"type": "metadata", "provider": "anthropic", "model": "claude-sonnet-4-20250514", "tokens_used": 342, "cost": 0.0012}
data: [DONE]
```

Event types:
- `token` — incremental content chunk
- `metadata` — provider, model, token count, cost (sent before `[DONE]`)
- `error` — streaming error (connection to LLM failed mid-stream)
- `context` — RAG context used (optional, for transparency)

**Implementation in `server.py`:**
- The existing `query_polly()` handler calls `polly.query()` which returns a full string
- Add `polly.query_stream()` that yields chunks from the LLM provider via LiteLLM's streaming support
- LiteLLM already supports streaming via `completion(..., stream=True)` returning a generator
- RAG retrieval, persona system prompt construction, and mental model injection happen BEFORE streaming starts (they are part of prompt preparation, not generation)
- Only the LLM generation phase is streamed

### Frontend: Streaming Consumer

**IPC Bridge Extension (`preload.js`):**

Add a new IPC method for streaming queries:

```js
// preload.js - new method
queryStream: (message, options) => ipcRenderer.invoke('polly:query-stream', message, options)
```

**Main Process Handler (`main.js`):**

The main process opens a `fetch()` connection to the Python server's streaming endpoint and forwards SSE events back to the renderer via IPC port messaging or a dedicated event channel.

Alternative: The renderer makes a direct `fetch()` to `http://127.0.0.1:11436/polly/query` with `stream: true` (simpler, since the server is local and CORS is already configured). This avoids the IPC middleman for streaming.

**Preferred approach: Direct fetch from renderer.** The local server is already accessed directly via `safeFetch()` in many places. This avoids the complexity of piping streams through IPC.

### Frontend: Incremental Rendering

**Modified `sendQueryInternal()` flow:**

```
1. User sends message
2. Add user message to UI and DB (existing)
3. Add typing indicator (existing)
4. Create AbortController
5. Show stop button (replacing send button)
6. fetch('/polly/query', { method: 'POST', body: { ...params, stream: true }, signal: controller.signal })
7. Read response body as ReadableStream
8. Replace typing indicator with empty assistant message bubble
9. For each SSE chunk:
   a. Parse event type
   b. If "token": append to message bubble innerHTML, run markdown rendering incrementally
   c. If "metadata": store for footer display
   d. Scroll to bottom (throttled to 60fps via requestAnimationFrame)
10. On [DONE]: finalize message, render full markdown, add metadata footer, save to DB, hide stop button
11. On error: show error message with retry button
12. On abort: show "Generation stopped" indicator, save partial response to DB
```

**Incremental markdown rendering:**
- During streaming, render markdown on a throttled interval (every 100ms or every 10 tokens) rather than on every token, to avoid excessive DOM thrashing
- Use a simple heuristic: render full markdown when a paragraph break (`\n\n`) or code fence boundary is detected; otherwise append raw text to a `<span>` within the current paragraph
- On completion, do a final full markdown render pass with `marked.js`

### Stop Button

Replace the send button with a stop button during generation:

```html
<!-- During generation -->
<button id="btn-stop" class="chat-stop-btn" aria-label="Stop generation">
  <i data-lucide="square"></i>
</button>
```

- Clicking calls `controller.abort()` on the `AbortController`
- The fetch will throw an `AbortError`, caught in the error handler
- Partial response is kept in the message bubble with a "(stopped)" indicator
- Send button reappears

### Retry Button

On error, append a retry button to the error message:

```html
<div class="message-error">
  <span>Error: Connection timed out</span>
  <button class="retry-btn" onclick="retryLastQuery()">
    <i data-lucide="refresh-cw"></i> Retry
  </button>
</div>
```

- `retryLastQuery()` re-sends the last user message with the same parameters
- The error message is replaced when retry starts

### Query Timeout

- Default: 120 seconds (configurable in settings)
- Implemented via `AbortController` with `setTimeout`
- On timeout: show "Request timed out" error with retry button
- Cancel the timeout when response completes or is manually stopped

## Existing System Modifications

| System | Change |
|--------|--------|
| `interfaces/server.py` | Add `stream` parameter to `/polly/query`; implement `StreamingResponse` path |
| `core/polly.py` | Add `query_stream()` method yielding chunks from LLM provider |
| `core/providers/litellm_adapter.py` | Ensure streaming mode is passed through to LiteLLM |
| `app.js:sendQueryInternal()` | Rewrite to use `fetch()` with `ReadableStream` instead of `window.polly.query()` |
| `app.js:addTypingIndicator()` | No change — still used during initial connection before first token |
| `app.js` chat input area | Add stop button, wire AbortController |
| `styles/main.css` | Add `.chat-stop-btn`, `.retry-btn`, `.message-error` styles |

## Fallback Behavior

- If streaming fails to connect, fall back to the non-streaming `window.polly.query()` path
- If the backend doesn't support `stream: true` (older server version), detect from response content-type and fall back
- Partial responses from stopped generation are saved to the conversation database

## Performance Considerations

- Throttle DOM updates to avoid jank (requestAnimationFrame + 100ms markdown render interval)
- Use `document.createTextNode()` for raw text appends between markdown render passes
- Scroll-to-bottom throttled to animation frame rate
- Memory: large responses should not accumulate redundant DOM nodes — each render pass replaces the content rather than appending

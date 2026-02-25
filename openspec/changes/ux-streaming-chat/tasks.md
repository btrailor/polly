# Tasks: Streaming Chat Responses

Backend contract stable before frontend. Ordered by dependency.

---

## Phase 1: Backend Streaming Support

### 1.1 Add streaming to Polly core

- [ ] Add `query_stream()` method to `core/polly.py` that yields content chunks
- [ ] Method performs the same RAG retrieval, persona construction, mental model injection as `query()`, but streams the LLM generation phase
- [ ] Yield structured events: `{"type": "token", "content": "..."}`, `{"type": "metadata", ...}`, `{"type": "error", ...}`
- [ ] Ensure conversation history and context are included in the prompt (same as non-streaming)

### 1.2 Verify LiteLLM streaming support

- [ ] Confirm `core/providers/litellm_adapter.py` passes `stream=True` to LiteLLM `completion()` correctly
- [ ] Test with Anthropic Claude, OpenAI, and Ollama providers
- [ ] Handle provider-specific streaming differences (if any) within the adapter

### 1.3 Add streaming endpoint to server

- [ ] Extend `POST /polly/query` in `interfaces/server.py` to accept `stream: boolean` parameter
- [ ] When `stream: true`, return `StreamingResponse(media_type="text/event-stream")`
- [ ] Format: `data: {json}\n\n` per SSE spec, with `data: [DONE]\n\n` sentinel
- [ ] Send metadata event (provider, model, tokens, cost) before `[DONE]`
- [ ] Handle errors during streaming gracefully (send error event, then close)
- [ ] Non-streaming behavior unchanged when `stream` is false or absent

### 1.4 Test backend streaming

- [ ] Manual test with `curl`: `curl -N -X POST http://127.0.0.1:11436/polly/query -d '{"query": "test", "stream": true}'`
- [ ] Verify tokens arrive incrementally
- [ ] Verify metadata event arrives at end
- [ ] Verify error handling mid-stream (e.g., kill Ollama during generation)

---

## Phase 2: Frontend Streaming Consumer

### 2.1 Implement streaming fetch in sendQueryInternal

- [ ] Replace `window.polly.query()` call with direct `fetch()` to `/polly/query` with `stream: true`
- [ ] Create `AbortController` for cancellation support
- [ ] Parse SSE events from `response.body` `ReadableStream` using a line-based parser
- [ ] Accumulate token content into a buffer string

### 2.2 Incremental DOM rendering

- [ ] Replace typing indicator with empty assistant message bubble on first token
- [ ] Append raw text tokens to the message bubble
- [ ] Throttle full markdown rendering (via `marked.js`) to every 100ms or on paragraph boundaries
- [ ] Final full markdown render on `[DONE]` event
- [ ] Scroll to bottom throttled via `requestAnimationFrame`
- [ ] Add metadata footer (provider, model, cost, tokens) from metadata event

### 2.3 Save streamed response to database

- [ ] On `[DONE]`, save the complete accumulated response to the conversation database via `window.polly.conversationAddMessage()`
- [ ] On abort (user stopped), save partial response with a `stopped: true` flag
- [ ] On error, save error state for potential retry

---

## Phase 3: Stop Generation

### 3.1 Stop button UI

- [ ] Add a stop button element (square icon) that replaces the send button during generation
- [ ] Style to match existing chat input area (`.chat-stop-btn` in `main.css`)
- [ ] Toggle visibility: send button visible when idle, stop button visible during streaming

### 3.2 Wire AbortController

- [ ] On stop button click, call `controller.abort()`
- [ ] Catch `AbortError` in the streaming fetch error handler
- [ ] On abort: keep partial content in message bubble, append "(stopped)" indicator
- [ ] Re-show send button, re-enable input

### 3.3 Query timeout

- [ ] Add configurable timeout (default 120s) via `setTimeout` calling `controller.abort()`
- [ ] Clear timeout when response completes normally or is manually stopped
- [ ] On timeout: show "Request timed out" error with retry button
- [ ] Timeout setting exposed in Settings → General

---

## Phase 4: Retry on Error

### 4.1 Retry button component

- [ ] On query error, show an inline retry button below the error message
- [ ] Style: ghost button with `refresh-cw` Lucide icon, subtle and not jarring
- [ ] `retryLastQuery()` re-sends the previous user message with identical parameters

### 4.2 Retry behavior

- [ ] Remove the error message when retry starts
- [ ] Re-add typing indicator
- [ ] Increment a retry counter (max 3 automatic retries for connection errors, then show manual retry only)
- [ ] Reset retry counter on successful response or new user message

---

## Phase 5: Fallback and Edge Cases

### 5.1 Non-streaming fallback

- [ ] If the `fetch()` response content-type is not `text/event-stream`, fall back to reading the response as JSON (non-streaming path)
- [ ] If the streaming connection fails immediately (server down), fall back to `window.polly.query()` via IPC
- [ ] Log fallback events for debugging

### 5.2 Persona workflow compatibility

- [ ] Slash commands that trigger structured persona workflows (Scribe Organize, Professor quiz) should continue to use the non-streaming path since they return structured data, not free-text
- [ ] Add a check in `sendQueryInternal`: if the query is a persona workflow command, skip streaming
- [ ] Free-text persona responses (Professor explaining, Architect advising) should stream normally

### 5.3 Edge case handling

- [ ] Multiple rapid sends: ensure `AbortController` from previous request is aborted before starting new one
- [ ] Browser tab/window hidden during streaming: continue accumulating, render on visibility change
- [ ] Very long responses (>10,000 tokens): ensure DOM performance stays acceptable with throttled rendering

---

## Completion Criteria

- [ ] Chat responses stream token-by-token in the UI
- [ ] Typing indicator shown until first token arrives, then replaced by incrementally growing response
- [ ] Stop button cancels generation and preserves partial response
- [ ] Retry button appears on errors and re-sends the query
- [ ] Query timeout prevents indefinite hangs (configurable, default 120s)
- [ ] Metadata footer (provider, model, cost) still appears after streaming completes
- [ ] Non-streaming fallback works when server doesn't support streaming
- [ ] Streaming works with all configured providers (Anthropic, OpenAI, Ollama)
- [ ] No visible jank during streaming (throttled DOM updates)

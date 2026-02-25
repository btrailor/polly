# Streaming Chat Responses with Cancellation

**Date:** February 2026
**Scope:** Backend + Frontend
**Priority:** P0 — core chat experience; affects perceived responsiveness of every interaction

---

## What We're Doing

Implementing token-by-token streaming for chat responses in the Electron app, replacing the current request-response pattern where the entire LLM output arrives as a single block after a potentially long wait. Adding the ability to cancel in-flight queries with a stop-generation button.

## Why

- **Perceived latency:** Currently, `sendQueryInternal()` (`app.js:8591`) calls `window.polly.query()` which returns the complete response after the full LLM round-trip. For complex queries routed to Claude Opus or large local models, users stare at a bouncing-dots typing indicator for 10-30+ seconds with zero feedback about progress.
- **The backend already supports SSE:** `interfaces/server.py` uses FastAPI `StreamingResponse` with `text/event-stream` for the `/v1/chat/completions` endpoint (OpenAI-compatible). This streaming capability is used by external IDE integrations (Cursor, Continue) but NOT by Polly's own chat UI.
- **No cancellation:** There is zero mechanism to abort an in-flight query — no `AbortController`, no stop button, no timeout. A slow backend can leave the typing indicator spinning indefinitely.
- **No retry:** When a query fails, a static error message is shown with no "Retry" action. The user must manually retype or re-send.

## Scope

- **In scope:** (1) Wire the Electron chat UI to consume SSE streaming from the backend. (2) Render tokens incrementally as they arrive. (3) Add a stop-generation button with `AbortController`. (4) Add a retry button on failed messages. (5) Add a query timeout (configurable, default 120s).
- **Out of scope:** Changes to the LLM routing logic. New model provider integrations. Streaming for persona-specific workflows (Scribe Organize, Professor quiz) — those have structured output that isn't naturally streamable.

## Backend vs Frontend

- **Backend:** May need a new or adjusted endpoint that streams persona-aware responses (current `/v1/chat/completions` is OpenAI-compatible but doesn't integrate persona/mental-model/RAG context the way `/polly/query` does). Alternatively, add streaming support to the existing `/polly/query` endpoint.
- **Frontend:** Wire `sendQueryInternal()` to use `EventSource` or `fetch` with `ReadableStream` instead of the current IPC `window.polly.query()`. Incremental DOM updates. Stop button. Retry button.

## Current State

- **Chat flow:** `sendQuery()` → `sendQueryCore()` → `sendQueryInternal()` (`app.js:8546-8700+`)
- **Backend call:** `window.polly.query(message, options)` via IPC → Python server `POST /polly/query` → full response returned
- **Typing indicator:** `addTypingIndicator()` (`app.js:8810-8838`) — three animated dots, added before API call, removed when response arrives
- **Error handling:** try/catch in `sendQueryInternal` (`app.js:8754-8757`), shows static system error message
- **Existing streaming infra:** `POST /v1/chat/completions` in `server.py` supports `stream: true` with SSE `data:` events and `[DONE]` sentinel

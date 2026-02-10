# Mobile Companion (OpenSpec)

Source of truth for Polly's mobile companion app — a lightweight client focused on capture and chat.

## Overview

The mobile companion is **not** a full Polly port. It is a stripped-down app focused on two things: **capturing knowledge** (voice, text, image) and **chatting with Polly**. It acts as a lightweight DRM node, submitting tasks to more capable Polly instances (desktop, NAS) for processing.

The desktop Electron app remains the primary, full-featured Polly interface.

---

## Core Functions

### Chat Agent
- Conversational interface with Polly.
- Queries relay to desktop/NAS Polly instance via DRM protocol — Cloudflare Tunnel when away from home network, mDNS when on LAN (or REST fallback).
- Conversation history synced with main instance.
- Persona awareness (Architect, Scribe, Professor) — selection relayed to processing node.

### Voice Input
- **First-class citizen.** Prominent microphone button; voice is the primary input method.
- Voice-to-text transcription (on-device or via service).
- Domain auto-detection on transcribed content.
- Direct submission as capture or as chat message.

### Quick Capture
- Text, voice, image, URL captures.
- Minimal metadata entry: domain (auto-suggested), optional project tag.
- Default maturity: 30-Ideas.
- Captures submitted to main Polly instance for full processing (entity extraction, RAG indexing, quality pipeline).

## DRM Node Identity

The mobile companion advertises itself as a thin DRM node:

```json
{
  "hostname": "mobile-polly",
  "capacity": { "cpu_cores": 2, "memory_gb": 4, "gpu": null },
  "models": [],
  "roles": ["capture", "chat-relay"]
}
```

- No local LLM inference.
- Submits tasks to peers; receives results.
- Falls back to REST API if DRM discovery fails.

## Sync

- **Captures:** Queued locally when offline; submitted when connected to main instance.
- **Chat history:** Synced with desktop conversation store.
- **Not synced:** Full vault, notes editor, canvas, patterns, mental models, curriculum, settings (all desktop-only).
- **Bandwidth-aware:** Media sync deferred to WiFi if on cellular.

## UI

- **Minimal, thumb-zone optimized.**
- **Three views:**
  1. **Chat** — Conversation with Polly. Voice button prominent.
  2. **Capture** — Quick entry with domain auto-suggestion.
  3. **Recent** — List of recent captures/conversations (read-only review).
- **Dark/light mode.**
- **Offline-first:** Captures work without connectivity; queued for sync.

## Technology (TBD)

Platform and technology decisions deferred. Options include:
- React Native (cross-platform)
- Swift/SwiftUI (iOS-first)
- PWA (web-based, no app store)

Decision depends on DRM transport requirements (Cloudflare Tunnel support), native API access needs (microphone, camera, notifications), and Ed25519 key management.

## Implementation Phases

### Mobile Phase 1: Chat Relay (3–4 weeks)
- Basic app shell with chat interface.
- REST API connection to main Polly instance.
- Text input + voice-to-text.
- Conversation sync.

### Mobile Phase 2: Capture (2–3 weeks)
- Quick capture (text, voice, URL).
- Domain auto-suggestion.
- Offline queue with sync.

### Mobile Phase 3: DRM Integration (2–3 weeks)
- DRM node registration (mDNS on LAN, Cloudflare Tunnel when remote).
- Task submission via DRM protocol with Ed25519 JWT auth.
- Hybrid peer discovery (local + remote).

### Mobile Phase 4: Rich Capture (2–3 weeks)
- Image capture with OCR.
- Location metadata.
- Recent captures browser.

## Relationship to Existing Systems

| System | Integration |
|---|---|
| **DRM** | Mobile is a thin DRM node; submits tasks to capable peers |
| **Capture** | Mobile captures enter the same capture pipeline as desktop |
| **Chat** | Conversations relay to main Polly instance |
| **Personas** | Persona selection relayed; processing happens on desktop/NAS |
| **RAG** | No local RAG; queries processed by main instance |

## Reference

- DRM protocol: [drm spec](../drm/spec.md)
- Capture system: [capture spec](../capture/spec.md)
- Change folder: [openspec/changes/spec-integration-2026-02/](../../changes/spec-integration-2026-02/)

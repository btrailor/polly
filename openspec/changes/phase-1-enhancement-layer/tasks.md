# Phase 1: PollyEnhancement Layer (§11.0)

**Status:** 📋 Tasks added 2026-04-01 — gap identified in OpenSpec Task Coverage Audit  
**Spec source:** `POLLY_IOS_SPEC.md §11.0`  
**Phase:** 1B (gates on Phase 1A gateway + chat working)  
**Owner:** @frontend  
**Added:** 2026-04-01

---

## What This Is

The `PollyEnhancementLayer` is the synchronous preprocessor that composes `<context>` blocks (vault notes), `<framing>` blocks (mental models), and domain tags into outgoing messages **before** the WebSocket write. It is the delivery mechanism that makes vault note injection and mental model injection actually work.

Without this pipeline, vault notes and mental models are specced but have no way to reach the message. The pill UI (showing active augmentations above the input bar) also depends on this layer.

**Key constraint from spec:** `ChatEngine.send()` in `expo-openclaw-chat` is not designed to be subclassed. Polly wraps it in a `PollyGatewayAdapter` facade — all outgoing message calls go through the adapter.

---

## Implementation Tasks (@frontend)

### Core Pipeline

- [ ] `[1B]` Define `AugmentationContext` interface:
  ```ts
  interface AugmentationContext {
    vaultNote: VaultNote | null;       // one per message max
    mentalModel: MentalModel | null;   // one per message max
    domainTag: string | null;          // derived from active domain
  }
  ```
- [ ] `[1B]` Zustand slice: `useAugmentationStore` — holds `AugmentationContext`, actions: `setVaultNote`, `clearVaultNote`, `setMentalModel`, `clearMentalModel`
- [ ] `[1B]` Implement `augmentMessage(content: string, ctx: AugmentationContext): string`:
  - If `ctx.vaultNote`: prepend `<context source="vault" title="[note title]">[note content]</context>\n\n`
  - If `ctx.mentalModel`: prepend `<framing model="[model id]">[model description]</framing>\n\n`
  - If `ctx.domainTag`: append domain tag per spec format
  - Stacking rule: vault + model compose; vault replaces vault (only one note per message)
  - Returns augmented string
- [ ] `[1B]` Wire `augmentMessage()` into `PollyGatewayAdapter.send()` — call before WebSocket write
- [ ] `[1B]` After send: clear `vaultNote` from augmentation store (message-scoped, not persistent)

### Pill UI

- [ ] `[1B]` `AugmentationPillBar` component — horizontal row above input bar, only visible when at least one augmentation is active
- [ ] `[1B]` `VaultNotePill` — shows note filename, × dismiss button → calls `clearVaultNote`
- [ ] `[1B]` `MentalModelPill` — shows model name, × dismiss button → calls `clearMentalModel`
- [ ] `[1B]` Pill count constraint: max 2 pills simultaneously (one vault, one model) — enforced by `AugmentationPillBar` layout
- [ ] `[1B]` Pills are message-scoped: cleared after send (vault note) or on explicit dismiss (mental model persists until dismissed)

### Integration

- [ ] `[1B]` Vault note picker (§11.1) sets `vaultNote` in augmentation store on selection → pill appears
- [ ] `[1B]` Mental model selector (§11.3) sets `mentalModel` in augmentation store on selection → pill appears
- [ ] `[1B]` `PollyGatewayAdapter` wraps `ChatEngine` from `expo-openclaw-chat` — confirm `send()` is accessible for wrapping (verify during expo-openclaw-chat verification task)

---

## Done When

Sending a message with a vault note active results in `<context>` block prepended in the outgoing WebSocket payload. Pill appears when note is selected, disappears after send. @qa_guy sign-off.

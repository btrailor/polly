/**
 * Polly Observation Store
 *
 * Manages the lifecycle of Polly card observations in the Today view.
 * Implements the dismissal state machine from AMBIENT_AGENT_SPEC.md:
 *
 *   QUEUED → ACTIVE → ENGAGED → DISMISSED (terminal)
 *
 * Key invariants:
 * - DISMISSED is a terminal state — no re-queue, no re-surface.
 * - Dismissed observation IDs are persisted to AsyncStorage so they
 *   survive app restarts. Missing this breaks the terminal state guarantee.
 * - Only one card is ACTIVE at a time. Next QUEUED card surfaces on dismiss.
 * - T3 auto-resolve: vault-health cards auto-dismiss when condition resolves.
 *
 * Spec: AMBIENT_AGENT_SPEC.md (Dismissal State Machine)
 * Cross-ref: AIGHT_POLLY_CARD.md (Design Decisions Q1–Q4, Context Notes 1–3)
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type ObservationState = 'queued' | 'active' | 'engaged' | 'dismissed';

export type TriggerType = 'T1' | 'T2' | 'T3' | 'T4' | 'T5';

export type ActionType =
  | 'open-vault'
  | 'open-note'
  | 'capture-with-scribe'
  | null;

export interface PollyObservation {
  id: string;
  triggerType: TriggerType;
  observationText: string;        // 1–2 sentences. Specific, earned.
  actionType: ActionType;         // null for T4 (observation only)
  actionTarget?: string;          // URL, note path, or agent context string
  state: ObservationState;
  createdAt: number;              // Unix timestamp ms
  engagedAt?: number;
  dismissedAt?: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Storage key
// ─────────────────────────────────────────────────────────────────────────────

const DISMISSED_IDS_KEY = 'polly:dismissed_observation_ids';

// ─────────────────────────────────────────────────────────────────────────────
// In-memory state (populated on init from AsyncStorage)
// ─────────────────────────────────────────────────────────────────────────────

let _observations: PollyObservation[] = [];
let _dismissedIds: Set<string> = new Set();
let _initialized = false;
let _listeners: Array<() => void> = [];

// ─────────────────────────────────────────────────────────────────────────────
// Persistence
// ─────────────────────────────────────────────────────────────────────────────

async function loadDismissedIds(): Promise<void> {
  try {
    const raw = await AsyncStorage.getItem(DISMISSED_IDS_KEY);
    if (raw) {
      const ids: string[] = JSON.parse(raw);
      _dismissedIds = new Set(ids);
    }
  } catch (err) {
    console.warn('[PollyStore] Failed to load dismissed IDs:', err);
  }
}

async function persistDismissedIds(): Promise<void> {
  try {
    await AsyncStorage.setItem(
      DISMISSED_IDS_KEY,
      JSON.stringify(Array.from(_dismissedIds))
    );
  } catch (err) {
    console.warn('[PollyStore] Failed to persist dismissed IDs:', err);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Notify subscribers (React hook integration)
// ─────────────────────────────────────────────────────────────────────────────

function notify() {
  _listeners.forEach((l) => l());
}

// ─────────────────────────────────────────────────────────────────────────────
// Internal: promote next queued card to active
// ─────────────────────────────────────────────────────────────────────────────

function _promoteNextQueued() {
  const hasActive = _observations.some((o) => o.state === 'active' || o.state === 'engaged');
  if (hasActive) return;

  const next = _observations
    .filter((o) => o.state === 'queued')
    .sort((a, b) => a.createdAt - b.createdAt)[0];

  if (next) {
    next.state = 'active';
    notify();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Initialize the store. Must be called once at app startup.
 * Loads persisted dismissed IDs from AsyncStorage.
 */
export async function initPollyStore(): Promise<void> {
  if (_initialized) return;
  await loadDismissedIds();
  _initialized = true;
  // Restore any in-memory observations that were dismissed before persistence
  _observations = _observations.map((o) => {
    if (_dismissedIds.has(o.id)) {
      return { ...o, state: 'dismissed' };
    }
    return o;
  });
  _promoteNextQueued();
}

/**
 * Add a new observation to the queue.
 * If an observation with this ID was previously dismissed, it is silently dropped.
 */
export function enqueueObservation(obs: Omit<PollyObservation, 'state' | 'createdAt'>): void {
  if (_dismissedIds.has(obs.id)) {
    // Terminal state — do not re-surface
    return;
  }
  if (_observations.find((o) => o.id === obs.id)) {
    // Already tracked
    return;
  }

  const newObs: PollyObservation = {
    ...obs,
    state: 'queued',
    createdAt: Date.now(),
  };
  _observations.push(newObs);
  _promoteNextQueued();
  notify();
}

/**
 * Transition ACTIVE → ENGAGED when user taps an action button or "→ open".
 * Card remains visible at 65% opacity (calibrated to default body font + standard line height).
 * If font spec changes, re-validate the 65% value with @design_eng.
 */
export function engageObservation(id: string): void {
  const obs = _observations.find((o) => o.id === id);
  if (!obs || obs.state !== 'active') return;
  obs.state = 'engaged';
  obs.engagedAt = Date.now();
  notify();
}

/**
 * Dismiss an observation (ACTIVE or ENGAGED → DISMISSED, terminal).
 * Persists the dismissed ID so the card never re-surfaces after app restart.
 * This is the "permanent dismiss, no re-queue" guarantee from the spec.
 */
export function dismissObservation(id: string): void {
  const obs = _observations.find((o) => o.id === id);
  if (!obs) return;
  if (obs.state === 'dismissed') return; // Already terminal

  obs.state = 'dismissed';
  obs.dismissedAt = Date.now();
  _dismissedIds.add(id);
  persistDismissedIds(); // Fire-and-forget; failure logged in persistDismissedIds
  _promoteNextQueued();
  notify();
}

/**
 * T3 auto-resolve: when a vault-health card's triggering condition is resolved,
 * auto-dismiss without user action. Applicable to T3 cards in ACTIVE or ENGAGED state.
 */
export function autoResolveT3(id: string): void {
  const obs = _observations.find((o) => o.id === id);
  if (!obs || obs.triggerType !== 'T3') return;
  if (obs.state === 'dismissed') return;
  dismissObservation(id);
}

/**
 * Returns the single currently-visible card (ACTIVE or ENGAGED), or null.
 * The queue itself is invisible to the user (Design Decision Q4).
 */
export function getActiveObservation(): PollyObservation | null {
  return (
    _observations.find((o) => o.state === 'active' || o.state === 'engaged') ?? null
  );
}

/**
 * Subscribe to store changes. Returns an unsubscribe function.
 */
export function subscribeToPollyStore(listener: () => void): () => void {
  _listeners.push(listener);
  return () => {
    _listeners = _listeners.filter((l) => l !== listener);
  };
}

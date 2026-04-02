/**
 * Onboarding state store — Zustand + MMKV persistence
 *
 * Phase flow:
 *   welcome → gateway-url → gateway-token → testing-connection → complete
 *
 * Persistence key: polly.onboarding.state
 * Non-sensitive data only. Auth token stored separately in expo-secure-store.
 */

import { create } from 'zustand';
import { MMKV } from 'react-native-mmkv';
import { getMMKVEncryptionKey } from '../utils/mmkvEncryption';

const MMKV_KEY = 'polly.onboarding.state';

const storage = new MMKV({ id: 'polly-onboarding', encryptionKey: getMMKVEncryptionKey() });

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type OnboardingPhase =
  | 'welcome'
  | 'gateway-url'
  | 'gateway-token'
  | 'testing-connection'
  | 'complete';

export interface OnboardingState {
  phase: OnboardingPhase;
  gatewayUrl: string | null;
  isComplete: boolean;
  completedAt?: number;
}

interface OnboardingStore extends OnboardingState {
  setGatewayUrl: (url: string) => void;
  setPhase: (phase: OnboardingPhase) => void;
  markComplete: () => void;
  reset: () => void;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

const DEFAULT_STATE: OnboardingState = {
  phase: 'welcome',
  gatewayUrl: null,
  isComplete: false,
};

function loadFromMMKV(): OnboardingState {
  try {
    const raw = storage.getString(MMKV_KEY);
    if (!raw) return DEFAULT_STATE;
    const parsed = JSON.parse(raw) as Partial<OnboardingState>;
    return {
      phase: parsed.phase ?? DEFAULT_STATE.phase,
      gatewayUrl: parsed.gatewayUrl ?? null,
      isComplete: parsed.isComplete ?? false,
      completedAt: parsed.completedAt,
    };
  } catch {
    return DEFAULT_STATE;
  }
}

function saveToMMKV(state: OnboardingState): void {
  try {
    storage.set(MMKV_KEY, JSON.stringify(state));
  } catch {
    // Non-fatal — don't crash if storage unavailable
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Store
// ─────────────────────────────────────────────────────────────────────────────

const persisted = loadFromMMKV();

export const useOnboardingStore = create<OnboardingStore>((set) => ({
  // Initial state — loaded from MMKV on startup
  ...persisted,

  setGatewayUrl: (url: string) =>
    set((prev) => {
      const next = { ...prev, gatewayUrl: url };
      saveToMMKV(next);
      return { gatewayUrl: url };
    }),

  setPhase: (phase: OnboardingPhase) =>
    set((prev) => {
      const next = { ...prev, phase };
      saveToMMKV(next);
      return { phase };
    }),

  markComplete: () =>
    set((prev) => {
      const next: OnboardingState = {
        ...prev,
        phase: 'complete',
        isComplete: true,
        completedAt: Date.now(),
      };
      saveToMMKV(next);
      return { phase: 'complete', isComplete: true, completedAt: next.completedAt };
    }),

  reset: () => {
    saveToMMKV(DEFAULT_STATE);
    set({ ...DEFAULT_STATE });
  },
}));

// ─────────────────────────────────────────────────────────────────────────────
// Standalone helper — read isComplete without subscribing to the store
// Used by app/index.tsx for the initial redirect check.
// ─────────────────────────────────────────────────────────────────────────────

export function readOnboardingComplete(): boolean {
  try {
    const raw = storage.getString(MMKV_KEY);
    if (!raw) return false;
    const parsed = JSON.parse(raw) as Partial<OnboardingState>;
    return parsed.isComplete === true;
  } catch {
    return false;
  }
}

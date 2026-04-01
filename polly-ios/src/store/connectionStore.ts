/**
 * connectionStore — Zustand store for gateway WebSocket connection state.
 *
 * States:
 *   'disconnected'  — not connected, no active attempt
 *   'connecting'    — handshake in progress
 *   'connected'     — authenticated, ready to send
 *   'reconnecting'  — lost connection, backoff retry in progress
 *   'failed'        — unrecoverable (bad credentials, etc.)
 */

import { create } from 'zustand';

export type ConnectionStatus =
  | 'disconnected'
  | 'connecting'
  | 'connected'
  | 'reconnecting'
  | 'failed';

interface ConnectionState {
  status: ConnectionStatus;
  gatewayUrl: string | null;
  /** Last error message shown in UI */
  lastError: string | null;
  /** Monotonically increasing — lets components detect reconnects */
  connectCount: number;

  setStatus: (status: ConnectionStatus) => void;
  setGatewayUrl: (url: string) => void;
  setError: (error: string | null) => void;
  recordConnect: () => void;
  reset: () => void;
}

export const useConnectionStore = create<ConnectionState>((set) => ({
  status: 'disconnected',
  gatewayUrl: null,
  lastError: null,
  connectCount: 0,

  setStatus: (status) => set({ status }),
  setGatewayUrl: (url) => set({ gatewayUrl: url }),
  setError: (error) => set({ lastError: error }),
  recordConnect: () => set((s) => ({ connectCount: s.connectCount + 1, lastError: null })),
  reset: () =>
    set({ status: 'disconnected', gatewayUrl: null, lastError: null, connectCount: 0 }),
}));

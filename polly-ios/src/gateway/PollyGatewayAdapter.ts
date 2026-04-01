/**
 * PollyGatewayAdapter — facade over expo-openclaw-chat's ChatEngine.
 *
 * Creates a dedicated SDK GatewayClient per agent session using credentials
 * from SecureStore. All outgoing messages go through this adapter — never
 * directly to ChatEngine or GatewayClient.
 *
 * The SDK GatewayClient is the one true WebSocket connection. This adapter:
 *   - Creates the SDK client + ChatEngine
 *   - Bridges SDK connection state → app connectionStore (Zustand)
 *   - Handles TOFU cert pinning on first connect
 *   - Emits polly.security.protectionLevel: "standard" on first connect
 *   - Fetches gateway capabilities (config.get) post-connect
 *
 * Phase 1A: static token auth. Ed25519 challenge-response is handled by the
 * SDK GatewayClient internally (device-identity.ts) — no app-layer changes needed.
 */

import * as SecureStore from 'expo-secure-store';
import {
  ChatEngine,
  type UIMessage,
  type ChatEngineEvent,
} from 'expo-openclaw-chat';
import {
  GatewayClient as SDKGatewayClient,
  type GatewayClientOptions,
  type HelloOk,
} from 'expo-openclaw-chat/src/core';
import { MMKV } from 'react-native-mmkv';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';
import { sanitizeForLog } from '../utils/sanitizeForLog';
import { useConnectionStore } from '../store/connectionStore';

// ─── MMKV for non-sensitive gateway metadata ──────────────────────────────────

const gatewayMetaStorage = new MMKV({ id: 'polly-gateway-meta' });

export const GATEWAY_META_KEYS = {
  VERSION: 'polly.gateway.version',
  CAPABILITIES: 'polly.gateway.capabilities',
  FETCHED_AT: 'polly.gateway.fetchedAt',
} as const;

// ─── TOFU helpers ─────────────────────────────────────────────────────────────

async function handleTofuOnConnect(helloOk: HelloOk): Promise<boolean> {
  // Gateway may include a tlsFingerprint in hello-ok
  const incoming = (helloOk as unknown as Record<string, unknown>).tlsFingerprint as
    | string
    | undefined;
  if (!incoming) return true; // no fingerprint sent — skip TOFU

  try {
    const stored = await SecureStore.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TLS_FINGERPRINT);

    if (!stored) {
      await SecureStore.setItemAsync(SECURE_STORE_KEYS.GATEWAY_TLS_FINGERPRINT, incoming);
      console.log('[PollyGatewayAdapter] TOFU: fingerprint stored on first connect');
      return true;
    }

    if (stored !== incoming) {
      console.error('[PollyGatewayAdapter] TOFU: fingerprint mismatch — possible MITM');
      useConnectionStore.getState().setStatus('failed');
      useConnectionStore.getState().setError(
        'Gateway certificate changed unexpectedly. Go to Settings → Your Gateway → Reset Connection to re-trust.'
      );
      return false;
    }

    return true;
  } catch (err) {
    console.error('[PollyGatewayAdapter] TOFU error:', sanitizeForLog(err));
    return true; // non-fatal — don't block connection on storage error
  }
}

/**
 * Clear stored TOFU fingerprint — call from Settings → Reset Connection.
 */
export async function clearTofuFingerprint(): Promise<void> {
  await SecureStore.deleteItemAsync(SECURE_STORE_KEYS.GATEWAY_TLS_FINGERPRINT);
  console.log('[PollyGatewayAdapter] TOFU fingerprint cleared');
}

// ─── Capabilities fetch ───────────────────────────────────────────────────────

async function fetchAndStoreCapabilities(sdkClient: SDKGatewayClient): Promise<void> {
  try {
    const raw = await sdkClient.request<{
      gatewayVersion?: string;
      capabilities?: string[];
    }>('config.get', {}, 5_000);

    const version = raw?.gatewayVersion ?? 'unknown';
    const capabilities = Array.isArray(raw?.capabilities) ? raw.capabilities : [];
    const fetchedAt = new Date().toISOString();

    gatewayMetaStorage.set(GATEWAY_META_KEYS.VERSION, version);
    gatewayMetaStorage.set(GATEWAY_META_KEYS.CAPABILITIES, JSON.stringify(capabilities));
    gatewayMetaStorage.set(GATEWAY_META_KEYS.FETCHED_AT, fetchedAt);

    console.log(
      '[PollyGatewayAdapter] Capabilities stored:',
      sanitizeForLog({ version, count: capabilities.length })
    );
  } catch (err) {
    // Non-fatal — app continues without capabilities
    console.warn('[PollyGatewayAdapter] config.get failed (non-fatal):', sanitizeForLog(err));
  }
}

export function getStoredGatewayCapabilities(): {
  version: string;
  capabilities: string[];
  fetchedAt: string;
} | null {
  const version = gatewayMetaStorage.getString(GATEWAY_META_KEYS.VERSION);
  const raw = gatewayMetaStorage.getString(GATEWAY_META_KEYS.CAPABILITIES);
  const fetchedAt = gatewayMetaStorage.getString(GATEWAY_META_KEYS.FETCHED_AT);
  if (!version || !raw || !fetchedAt) return null;
  try {
    return { version, capabilities: JSON.parse(raw) as string[], fetchedAt };
  } catch {
    return null;
  }
}

// ─── Connection bridge ────────────────────────────────────────────────────────

/**
 * Wire SDK connection state changes → app connectionStore.
 * Returns cleanup function.
 */
function bridgeConnectionState(sdkClient: SDKGatewayClient, gatewayUrl: string): () => void {
  const store = useConnectionStore.getState();
  store.setGatewayUrl(gatewayUrl);

  return sdkClient.onConnectionStateChange((state) => {
    const store = useConnectionStore.getState();
    switch (state) {
      case 'connecting':
        store.setStatus('connecting');
        break;
      case 'connected':
        store.setStatus('connected');
        store.recordConnect();
        break;
      case 'reconnecting':
        store.setStatus('reconnecting');
        break;
      case 'disconnected':
        store.setStatus('disconnected');
        break;
    }
  });
}

// ─── PollyGatewayAdapter ──────────────────────────────────────────────────────

export class PollyGatewayAdapter {
  private engine: ChatEngine;
  private sdkClient: SDKGatewayClient;
  private cleanupBridge: () => void;
  readonly sessionKey: string;

  private constructor(
    sdkClient: SDKGatewayClient,
    sessionKey: string,
    cleanupBridge: () => void
  ) {
    this.sdkClient = sdkClient;
    this.sessionKey = sessionKey;
    this.cleanupBridge = cleanupBridge;
    this.engine = new ChatEngine(sdkClient, sessionKey);
  }

  /**
   * Factory — reads credentials from SecureStore and creates the adapter.
   * Bridges SDK connection state to app connectionStore.
   * Throws if credentials are missing (user must complete onboarding first).
   */
  static async create(agentId: string): Promise<PollyGatewayAdapter> {
    const url = await SecureStore.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL);
    const token = await SecureStore.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TOKEN);

    if (!url || !token) {
      throw new Error(
        'Gateway URL or auth token not configured. Complete onboarding first.'
      );
    }

    const wsUrl = url.replace(/^http/, 'ws');

    const options: GatewayClientOptions = {
      token,
      autoReconnect: true,
      displayName: 'Polly iOS',
      platform: 'ios',
      clientId: 'polly-ios',
    };

    const sdkClient = new SDKGatewayClient(wsUrl, options);
    const sessionKey = `agent:${agentId}:main`;

    // Bridge connection state to app store before connecting
    const cleanupBridge = bridgeConnectionState(sdkClient, url);

    const adapter = new PollyGatewayAdapter(sdkClient, sessionKey, cleanupBridge);

    // Connect and run post-connect hooks (non-blocking)
    sdkClient
      .connect()
      .then(async (helloOk) => {
        // TOFU cert pinning
        const tofuOk = await handleTofuOnConnect(helloOk);
        if (!tofuOk) {
          sdkClient.disconnect();
          return;
        }

        // polly.security.protectionLevel: "standard" (Wave 0 #3)
        try {
          await sdkClient.request('config.patch', {
            key: 'polly.security.protectionLevel',
            value: 'standard',
          }, 5_000);
        } catch (err) {
          console.warn('[PollyGatewayAdapter] protectionLevel patch failed:', sanitizeForLog(err));
        }

        // Fetch and cache gateway capabilities
        await fetchAndStoreCapabilities(sdkClient);
      })
      .catch((err) => {
        console.warn('[PollyGatewayAdapter] Initial connect failed:', sanitizeForLog(err));
      });

    return adapter;
  }

  // ─── Public API ─────────────────────────────────────────────────────────────

  /** Send a text message. */
  async send(text: string): Promise<void> {
    await this.engine.send(text);
  }

  /** Abort the current streaming response. */
  abort(): void {
    this.engine.abort();
  }

  /**
   * Load chat history for this session.
   * Returns empty array on error (e.g. new session or not connected yet).
   */
  async loadHistory(): Promise<UIMessage[]> {
    try {
      const payload = await this.sdkClient.chatHistory(this.sessionKey, { limit: 50 });
      const messages = (payload as unknown as { messages?: unknown[] }).messages ?? [];
      return messages.map((m): UIMessage => {
        const msg = m as {
          id?: string;
          role?: string;
          content?: unknown;
          timestamp?: number;
        };
        const content = Array.isArray(msg.content)
          ? msg.content
          : typeof msg.content === 'string'
          ? [{ type: 'text' as const, text: msg.content }]
          : [];
        return {
          id: msg.id ?? `hist-${Math.random().toString(36).slice(2)}`,
          role: (msg.role as UIMessage['role']) ?? 'assistant',
          content,
          timestamp: msg.timestamp,
          isStreaming: false,
          isError: false,
        };
      });
    } catch {
      return [];
    }
  }

  /** Current messages (live from engine). */
  get messages(): UIMessage[] {
    return this.engine.messages;
  }

  /** Whether a response is currently streaming. */
  get isStreaming(): boolean {
    return this.engine.isStreaming;
  }

  /** Whether the underlying SDK client is connected. */
  get isConnected(): boolean {
    return this.sdkClient.isConnected;
  }

  /** Subscribe to engine events. Returns an unsubscribe function. */
  on(event: ChatEngineEvent, cb: (...args: unknown[]) => void): () => void {
    return (this.engine.on as (e: string, cb: (...args: unknown[]) => void) => () => void)(
      event,
      cb
    );
  }

  /** Tear down engine + SDK client + connection bridge. Call on screen unmount. */
  destroy(): void {
    this.cleanupBridge();
    this.engine.destroy();
    this.sdkClient.disconnect();
  }
}

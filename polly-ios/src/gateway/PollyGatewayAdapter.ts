/**
 * PollyGatewayAdapter — facade over expo-openclaw-chat's ChatEngine.
 *
 * Creates a dedicated SDK GatewayClient per agent session using credentials
 * from SecureStore. All outgoing messages go through this adapter — never
 * directly to ChatEngine or GatewayClient.
 *
 * Phase 1A: static token auth. Phase 1B will add Ed25519 challenge-response.
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
} from 'expo-openclaw-chat/src/core';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';

// ─── PollyGatewayAdapter ──────────────────────────────────────────────────────

export class PollyGatewayAdapter {
  private engine: ChatEngine;
  private sdkClient: SDKGatewayClient;
  readonly sessionKey: string;

  private constructor(sdkClient: SDKGatewayClient, sessionKey: string) {
    this.sdkClient = sdkClient;
    this.sessionKey = sessionKey;
    this.engine = new ChatEngine(sdkClient, sessionKey);
  }

  /**
   * Factory — reads credentials from SecureStore and creates the adapter.
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

    // Normalise to WebSocket URL
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

    const adapter = new PollyGatewayAdapter(sdkClient, sessionKey);

    // Kick off connection (non-blocking — engine handles the state machine)
    adapter.sdkClient.connect().catch((err) => {
      console.warn('[PollyGatewayAdapter] Initial connect failed:', err);
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

      // The engine doesn't expose a loadHistory API, so we convert the raw
      // history payload to UIMessage[] for seeding the store.
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
      // Not fatal — return empty; session may not exist yet
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
    // ChatEngine.on is overloaded — cast through unknown to satisfy TS
    return (this.engine.on as (e: string, cb: (...args: unknown[]) => void) => () => void)(
      event,
      cb
    );
  }

  /** Unsubscribe. No-op if not registered (engine handles it). */
  off(_event: ChatEngineEvent, _cb: (...args: unknown[]) => void): void {
    // ChatEngine.on() returns the unsub fn — track it via on() return value.
    // This method is provided for symmetry but callers should prefer the
    // return value of on() for clean unsubscription.
  }

  /** Tear down engine + SDK client. Call on screen unmount. */
  destroy(): void {
    this.engine.destroy();
    this.sdkClient.disconnect();
  }
}

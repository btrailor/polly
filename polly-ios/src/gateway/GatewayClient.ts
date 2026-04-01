/**
 * GatewayClient — WebSocket client for OpenClaw gateway.
 *
 * Responsibilities:
 *   - Connect + authenticate via static token (Phase 1A)
 *   - Exponential backoff reconnect
 *   - Session key management (agent:<agentId>:main)
 *   - Idempotency key on every send
 *   - Filter NO_REPLY / HEARTBEAT_OK silent replies
 *   - Emit polly.security.protectionLevel: "standard" on first config.patch
 *   - Never log credentials — all output via sanitizeForLog()
 *
 * Auth upgrade path: Phase 1A uses static token. Phase 1B adds Ed25519
 * challenge-response (challenge-response signing task in tasks.md).
 * The connect() method is designed to slot in without breaking callers.
 */

import * as SecureStore from 'expo-secure-store';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';
import { sanitizeForLog } from '../utils/sanitizeForLog';
import { useConnectionStore } from '../store/connectionStore';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface GatewayMessage {
  type: string;
  [key: string]: unknown;
}

export type MessageHandler = (message: GatewayMessage) => void;

// Silent reply types — never render these in chat (spec §3.6)
const SILENT_REPLY_TYPES = new Set(['NO_REPLY', 'HEARTBEAT_OK']);

// ─── Backoff config ───────────────────────────────────────────────────────────

const BACKOFF_BASE_MS = 1_000;
const BACKOFF_MAX_MS = 30_000;
const BACKOFF_MULTIPLIER = 2;

function nextBackoff(attempt: number): number {
  return Math.min(BACKOFF_BASE_MS * Math.pow(BACKOFF_MULTIPLIER, attempt), BACKOFF_MAX_MS);
}

// ─── Idempotency key ──────────────────────────────────────────────────────────

let _idempotencyCounter = 0;

function generateIdempotencyKey(): string {
  _idempotencyCounter += 1;
  return `polly-${Date.now()}-${_idempotencyCounter}`;
}

// ─── GatewayClient ────────────────────────────────────────────────────────────

export class GatewayClient {
  private ws: WebSocket | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private shouldReconnect = false;
  private gatewayUrl: string | null = null;
  private authToken: string | null = null;
  /** Whether we've already emitted the initial config.patch for protectionLevel */
  private protectionLevelPatched = false;
  /** Whether TOFU fingerprint has been stored this session */
  private tofuVerified = false;

  // ─── Public API ─────────────────────────────────────────────────────────────

  /**
   * Connect to the gateway. Reads credentials from SecureStore.
   * Idempotent — calling while connected is a no-op.
   */
  async connect(): Promise<void> {
    const store = useConnectionStore.getState();

    if (store.status === 'connected' || store.status === 'connecting') {
      return;
    }

    const url = await SecureStore.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL);
    const token = await SecureStore.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TOKEN);

    if (!url || !token) {
      store.setStatus('failed');
      store.setError('Gateway URL or auth token not configured. Complete onboarding first.');
      return;
    }

    this.gatewayUrl = url;
    this.authToken = token;
    this.shouldReconnect = true;
    store.setGatewayUrl(url);

    this._openSocket();
  }

  /**
   * Disconnect and stop reconnect attempts.
   */
  disconnect(): void {
    this.shouldReconnect = false;
    this._clearReconnectTimer();
    if (this.ws) {
      this.ws.close(1000, 'client disconnect');
      this.ws = null;
    }
    useConnectionStore.getState().setStatus('disconnected');
  }

  /**
   * Send a message on the active session.
   * Automatically injects an idempotency key.
   * Throws if not connected.
   */
  send(agentId: string, text: string, extraFields?: Record<string, unknown>): string {
    if (!this.ws || useConnectionStore.getState().status !== 'connected') {
      throw new Error('GatewayClient.send() called while not connected');
    }

    const idempotencyKey = generateIdempotencyKey();
    const sessionKey = `agent:${agentId}:main`;

    const payload = {
      type: 'chat.send',
      sessionKey,
      idempotencyKey,
      text,
      ...extraFields,
    };

    this.ws.send(JSON.stringify(payload));
    return idempotencyKey;
  }

  /**
   * Register a handler for incoming gateway messages.
   * Silent replies (NO_REPLY, HEARTBEAT_OK) are filtered before handlers fire.
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => this.messageHandlers.delete(handler);
  }

  // ─── Private: Socket lifecycle ───────────────────────────────────────────────

  private _openSocket(): void {
    const store = useConnectionStore.getState();
    store.setStatus(this.reconnectAttempt === 0 ? 'connecting' : 'reconnecting');

    if (!this.gatewayUrl || !this.authToken) return;

    // Enforce WSS for non-local URLs (spec §3.12 — never ws:// through tunnel)
    const wsUrl = this._buildWsUrl(this.gatewayUrl);
    console.log('[GatewayClient] Connecting to', sanitizeForLog(wsUrl));

    try {
      this.ws = new WebSocket(wsUrl, undefined);
    } catch (err) {
      console.error('[GatewayClient] WebSocket construction failed:', sanitizeForLog(err));
      this._scheduleReconnect();
      return;
    }

    this.ws.onopen = () => this._onOpen();
    this.ws.onmessage = (event) => this._onMessage(event);
    this.ws.onerror = (event) => this._onError(event);
    this.ws.onclose = (event) => this._onClose(event);
  }

  private _onOpen(): void {
    console.log('[GatewayClient] Socket open — sending auth');
    // Authenticate immediately on open
    this.ws?.send(
      JSON.stringify({
        type: 'auth',
        token: this.authToken,
      })
    );
    // Note: we don't set 'connected' until auth ack arrives (handled in _onMessage)
  }

  private _onMessage(event: MessageEvent): void {
    let message: GatewayMessage;
    try {
      message = JSON.parse(event.data as string) as GatewayMessage;
    } catch {
      console.warn('[GatewayClient] Failed to parse message:', sanitizeForLog(event.data));
      return;
    }

    // Auth acknowledgement
    if (message.type === 'auth.ok') {
      const store = useConnectionStore.getState();
      store.setStatus('connected');
      store.recordConnect();
      this.reconnectAttempt = 0;
      console.log('[GatewayClient] Authenticated ✓');
      this._patchProtectionLevelIfNeeded();
      this._storeTofuFingerprintIfNeeded(message);
      return;
    }

    if (message.type === 'auth.error') {
      console.error('[GatewayClient] Auth rejected:', sanitizeForLog(message));
      useConnectionStore.getState().setStatus('failed');
      useConnectionStore.getState().setError('Gateway rejected auth token. Check your credentials in Settings.');
      this.shouldReconnect = false;
      this.ws?.close();
      return;
    }

    // Filter silent replies — never surface to UI (spec §3.6)
    if (SILENT_REPLY_TYPES.has(message.type)) {
      return;
    }

    // Dispatch to all registered handlers
    for (const handler of this.messageHandlers) {
      try {
        handler(message);
      } catch (err) {
        console.error('[GatewayClient] Handler threw:', sanitizeForLog(err));
      }
    }
  }

  private _onError(event: Event): void {
    console.error('[GatewayClient] WebSocket error:', sanitizeForLog(event));
  }

  private _onClose(event: CloseEvent): void {
    console.log(`[GatewayClient] Socket closed — code=${event.code} reason=${event.reason}`);
    this.ws = null;

    const store = useConnectionStore.getState();
    if (store.status === 'connected' || store.status === 'connecting') {
      store.setStatus('reconnecting');
    }

    if (this.shouldReconnect) {
      this._scheduleReconnect();
    }
  }

  // ─── Private: Reconnect ───────────────────────────────────────────────────────

  private _scheduleReconnect(): void {
    const delay = nextBackoff(this.reconnectAttempt);
    this.reconnectAttempt += 1;
    console.log(`[GatewayClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempt})`);

    this.reconnectTimer = setTimeout(() => {
      if (this.shouldReconnect) {
        this._openSocket();
      }
    }, delay);
  }

  private _clearReconnectTimer(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  // ─── Private: Helpers ─────────────────────────────────────────────────────────

  /**
   * Enforce WSS for Cloudflare Tunnel URLs; allow ws:// for LAN (localhost / .local).
   * Spec §3.12: never ws:// through tunnel.
   */
  private _buildWsUrl(gatewayUrl: string): string {
    const normalized = gatewayUrl.replace(/^http/, 'ws');
    const isLocal =
      normalized.includes('localhost') ||
      normalized.includes('127.0.0.1') ||
      normalized.includes('.local');

    if (!isLocal && normalized.startsWith('ws://')) {
      return normalized.replace('ws://', 'wss://');
    }
    return normalized;
  }

  /**
   * Emit polly.security.protectionLevel: "standard" on first successful connect.
   * Gateway Wave 0 task #3 — must be set before any config.patch callers run.
   * Only fires once per client lifetime.
   */
  private _patchProtectionLevelIfNeeded(): void {
    if (this.protectionLevelPatched) return;
    this.protectionLevelPatched = true;

    this.ws?.send(
      JSON.stringify({
        type: 'config.patch',
        key: 'polly.security.protectionLevel',
        value: 'standard',
      })
    );
  }
}

  /**
   * TOFU (Trust On First Use) cert pinning.
   *
   * On first verified connect: if auth.ok includes a tlsFingerprint, store it.
   * On subsequent connects: verify the stored fingerprint matches.
   * If mismatch → set status 'failed', surface error, do not proceed.
   *
   * Note: React Native's WebSocket API doesn't expose TLS fingerprints directly.
   * The gateway sends its fingerprint in the auth.ok payload. This is a
   * server-asserted value — full TLS inspection requires a native module (Phase 2).
   * For Phase 1A this provides TOFU at the application layer.
   */
  private async _storeTofuFingerprintIfNeeded(authOkMessage: GatewayMessage): Promise<void> {
    const incomingFingerprint = authOkMessage.tlsFingerprint as string | undefined;
    if (!incomingFingerprint) return; // gateway didn't send one — skip

    try {
      const stored = await SecureStore.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TLS_FINGERPRINT);

      if (!stored) {
        // First connect — store and trust
        await SecureStore.setItemAsync(
          SECURE_STORE_KEYS.GATEWAY_TLS_FINGERPRINT,
          incomingFingerprint
        );
        console.log('[GatewayClient] TOFU: fingerprint stored on first connect');
        this.tofuVerified = true;
        return;
      }

      if (stored !== incomingFingerprint) {
        // Fingerprint mismatch — possible MITM
        console.error('[GatewayClient] TOFU: fingerprint mismatch — possible MITM attack');
        useConnectionStore.getState().setStatus('failed');
        useConnectionStore.getState().setError(
          'Gateway certificate changed unexpectedly. If you changed your gateway setup, go to Settings → Your Gateway → Reset Connection to re-trust.'
        );
        this.shouldReconnect = false;
        this.ws?.close();
        return;
      }

      // Fingerprint matches — all good
      this.tofuVerified = true;
    } catch (err) {
      console.error('[GatewayClient] TOFU store error:', sanitizeForLog(err));
    }
  }

  /**
   * Clear stored TOFU fingerprint — called from Settings → Reset Connection.
   * Required when user intentionally reconfigures their gateway.
   */
  async clearTofuFingerprint(): Promise<void> {
    await SecureStore.deleteItemAsync(SECURE_STORE_KEYS.GATEWAY_TLS_FINGERPRINT);
    this.tofuVerified = false;
    console.log('[GatewayClient] TOFU fingerprint cleared');
  }

// Singleton — one client for the app lifetime
export const gatewayClient = new GatewayClient();

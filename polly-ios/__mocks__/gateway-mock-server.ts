/**
 * Gateway Mock Server — simulates OpenClaw gateway WebSocket for test suite.
 *
 * Usage:
 *   const mock = new MockGatewayServer();
 *   mock.simulateAuthOk();
 *   mock.simulateDelta('agent-id', 'Hello ');
 *   mock.simulateDone('agent-id');
 *   mock.simulateReconnect();
 *   mock.reset();
 */

import type { GatewayMessage, MessageHandler } from '../src/gateway/GatewayClient';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface MockGatewayOptions {
  /** If set, simulateAuthOk auto-fires after connect(). Default: false (manual control). */
  autoAuth?: boolean;
}

// ─── MockGatewayServer ────────────────────────────────────────────────────────

export class MockGatewayServer {
  private handlers: Set<MessageHandler> = new Set();
  private _receivedMessages: GatewayMessage[] = [];
  private _connectCalled = false;
  private _disconnectCalled = false;
  private _protectionLevelPatched = false;

  // ─── Handler registration (mirrors GatewayClient.onMessage) ──────────────

  onMessage(handler: MessageHandler): () => void {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  // ─── Message capture (for assertions) ────────────────────────────────────

  get receivedMessages(): GatewayMessage[] {
    return [...this._receivedMessages];
  }

  captureOutbound(message: GatewayMessage): void {
    this._receivedMessages.push(message);
    // Check for polly.security.protectionLevel emission
    if (
      message.type === 'config.patch' &&
      (message as any)?.patch?.['polly.security.protectionLevel'] === 'standard'
    ) {
      this._protectionLevelPatched = true;
    }
  }

  get protectionLevelPatched(): boolean {
    return this._protectionLevelPatched;
  }

  // ─── Inbound message simulation ───────────────────────────────────────────

  /** Emit a message to all registered handlers (simulates server → client) */
  emit(message: GatewayMessage): void {
    for (const handler of this.handlers) {
      handler(message);
    }
  }

  // ─── Scenario helpers ─────────────────────────────────────────────────────

  simulateAuthOk(): void {
    this.emit({ type: 'auth.ok' });
  }

  simulateAuthError(reason: string): void {
    this.emit({ type: 'auth.error', reason });
  }

  /** Emit NO_REPLY — should be suppressed by GatewayClient, never reach app handlers */
  simulateNoReply(): void {
    this.emit({ type: 'NO_REPLY' });
  }

  /** Emit HEARTBEAT_OK — should be suppressed by GatewayClient, never reach app handlers */
  simulateHeartbeatOk(): void {
    this.emit({ type: 'HEARTBEAT_OK' });
  }

  simulateDelta(agentId: string, text: string, seq?: number): void {
    this.emit({
      type: 'chat.delta',
      agentId,
      text,
      ...(seq !== undefined ? { seq } : {}),
    });
  }

  simulateDone(agentId: string, seq?: number): void {
    this.emit({
      type: 'chat.done',
      agentId,
      ...(seq !== undefined ? { seq } : {}),
    });
  }

  simulateChallengeRequest(challenge: string): void {
    this.emit({ type: 'connect.challenge', challenge });
  }

  /** Simulate connection dropped — triggers reconnect logic in client */
  simulateConnectionDrop(): void {
    this.emit({ type: '__mock__.connectionDrop' });
  }

  // ─── Connection state tracking ────────────────────────────────────────────

  markConnected(): void {
    this._connectCalled = true;
  }

  markDisconnected(): void {
    this._disconnectCalled = true;
  }

  get connectCalled(): boolean {
    return this._connectCalled;
  }

  get disconnectCalled(): boolean {
    return this._disconnectCalled;
  }

  // ─── Reset ────────────────────────────────────────────────────────────────

  reset(): void {
    this.handlers.clear();
    this._receivedMessages = [];
    this._connectCalled = false;
    this._disconnectCalled = false;
    this._protectionLevelPatched = false;
  }
}

// ─── Singleton for use in tests ───────────────────────────────────────────────

export const mockGateway = new MockGatewayServer();

// ─── Jest mock factory ────────────────────────────────────────────────────────
// Use this to replace GatewayClient in tests:
//   jest.mock('../src/gateway/GatewayClient', () => require('../__mocks__/gateway-mock-server').createGatewayClientMock())

export function createGatewayClientMock(server: MockGatewayServer = mockGateway) {
  let _idempotencyCounter = 0;

  const gatewayClient = {
    connect: jest.fn(async () => {
      server.markConnected();
    }),
    disconnect: jest.fn(() => {
      server.markDisconnected();
    }),
    send: jest.fn((agentId: string, text: string, extraFields?: Record<string, unknown>): string => {
      _idempotencyCounter += 1;
      const key = `polly-test-${Date.now()}-${_idempotencyCounter}`;
      server.captureOutbound({ type: 'chat.send', agentId, text, idempotencyKey: key, ...extraFields });
      return key;
    }),
    onMessage: jest.fn((handler: MessageHandler) => server.onMessage(handler)),
  };

  return { gatewayClient };
}

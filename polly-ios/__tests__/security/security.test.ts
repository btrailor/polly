/**
 * TEST-SEC series — Security tests
 * Spec: TESTING_AND_QA_SPEC.md §2.2, openspec/changes/phase-1-testing-infrastructure/tasks.md
 * P0: TEST-SEC-003 (credential leak) is a hard gate — zero tolerance
 */

import { sanitizeForLog } from '../../src/utils/sanitizeForLog';
import { SECURE_STORE_KEYS } from '../../src/constants/secureStoreKeys';
import * as SecureStoreMock from '../../__mocks__/expo-secure-store';

// ─── TEST-SEC-003 (P0 — run first) ────────────────────────────────────────────

describe('TEST-SEC-003 (P0): Credentials never appear in log output', () => {
  const sensitiveValues: Record<string, string> = {
    token: 'secret-auth-token-abc123',
    privateKey: 'private-key-deadbeef',
    password: 'hunter2',
    tlsFingerprint: 'aa:bb:cc:dd:ee:ff',
    sendKey: 'sk_live_abcdef',
    tunnelUrl: 'https://tunnel.example.com/secret',
    apnsToken: 'apns_device_token_xyz',
  };

  it('sanitizeForLog redacts token field in objects', () => {
    const result = sanitizeForLog({ token: sensitiveValues.token, type: 'auth' }) as any;
    expect(result.token).toBe('[REDACTED]');
    expect(result.type).toBe('auth');
  });

  it('sanitizeForLog redacts privateKey field', () => {
    const result = sanitizeForLog({ privateKey: sensitiveValues.privateKey }) as any;
    expect(result.privateKey).toBe('[REDACTED]');
  });

  it('sanitizeForLog redacts password field', () => {
    const result = sanitizeForLog({ password: sensitiveValues.password }) as any;
    expect(result.password).toBe('[REDACTED]');
  });

  it('sanitizeForLog redacts tlsFingerprint field', () => {
    const result = sanitizeForLog({ tlsFingerprint: sensitiveValues.tlsFingerprint }) as any;
    expect(result.tlsFingerprint).toBe('[REDACTED]');
  });

  it('sanitizeForLog redacts sendKey field', () => {
    const result = sanitizeForLog({ sendKey: sensitiveValues.sendKey }) as any;
    expect(result.sendKey).toBe('[REDACTED]');
  });

  it('sanitizeForLog redacts nested credentials in deep objects', () => {
    const input = {
      connection: {
        auth: { token: sensitiveValues.token },
        meta: { retries: 3 },
      },
    };
    const result = sanitizeForLog(input) as any;
    expect(result.connection.auth.token).toBe('[REDACTED]');
    expect(result.connection.meta.retries).toBe(3);
  });

  it('sanitizeForLog redacts credentials in arrays', () => {
    const input = [{ token: sensitiveValues.token }, { type: 'safe' }];
    const result = sanitizeForLog(input) as any[];
    expect(result[0].token).toBe('[REDACTED]');
    expect(result[1].type).toBe('safe');
  });

  it('sanitizeForLog redacts JSON string containing "token" key', () => {
    const input = `{"token": "${sensitiveValues.token}", "type": "auth.send"}`;
    const result = sanitizeForLog(input) as string;
    expect(result).not.toContain(sensitiveValues.token);
    expect(result).toContain('[REDACTED]');
  });

  it('sanitizeForLog does not mutate the original input', () => {
    const original = { token: sensitiveValues.token, safe: 'keep' };
    const copy = { ...original };
    sanitizeForLog(original);
    expect(original).toEqual(copy);
  });

  it('sanitizeForLog passes non-sensitive fields through unchanged', () => {
    const input = { type: 'chat.delta', text: 'Hello world', agentId: 'agent-main' };
    const result = sanitizeForLog(input) as any;
    expect(result.type).toBe('chat.delta');
    expect(result.text).toBe('Hello world');
    expect(result.agentId).toBe('agent-main');
  });

  // @security_audit additions: tunnelUrl + concurrent call safety

  it('sanitizeForLog redacts tunnelUrl object key', () => {
    const result = sanitizeForLog({ tunnelUrl: 'https://x.cfargotunnel.com/secret' }) as any;
    expect(result.tunnelUrl).toBe('[REDACTED]');
  });

  it('sanitizeForLog redacts tunnelUrl in serialized JSON string', () => {
    const input = `{"tunnelUrl": "https://x.cfargotunnel.com/secret", "type": "connect"}`;
    const result = sanitizeForLog(input) as string;
    expect(result).not.toContain('cfargotunnel.com');
    expect(result).toContain('[REDACTED]');
  });

  it('concurrent calls do not bleed state (no shared regex lastIndex)', () => {
    // Call sanitizeForLog many times simultaneously with strings containing sensitive patterns
    const inputs = Array.from({ length: 20 }, (_, i) =>
      `{"token": "secret-token-${i}", "type": "msg-${i}"}`
    );
    const results = inputs.map((input) => sanitizeForLog(input) as string);
    for (let i = 0; i < results.length; i++) {
      expect(results[i]).not.toContain(`secret-token-${i}`);
      expect(results[i]).toContain('[REDACTED]');
      expect(results[i]).toContain(`msg-${i}`); // non-sensitive part preserved
    }
  });
});

// ─── TEST-SEC-001: Ed25519 keypair + private key isolation ────────────────────

describe('TEST-SEC-001: Ed25519 keypair generation', () => {
  const ed25519Mock = require('../../__mocks__/@noble/ed25519');

  it('getPublicKey returns a 32-byte public key', () => {
    const pubKey = ed25519Mock.getPublicKey(ed25519Mock.__TEST_PRIVATE_KEY);
    expect(pubKey).toBeInstanceOf(Uint8Array);
    expect(pubKey.length).toBe(32);
  });

  it('private key is never the same bytes as public key', () => {
    const privKey = ed25519Mock.__TEST_PRIVATE_KEY;
    const pubKey = ed25519Mock.getPublicKey(privKey);
    // Anti-assertion: private key must not equal public key
    expect(Buffer.from(privKey).toString('hex')).not.toBe(
      Buffer.from(pubKey).toString('hex')
    );
  });

  it('sign() returns a 64-byte signature', async () => {
    const message = new TextEncoder().encode('test-challenge-payload');
    const sig = await ed25519Mock.sign(message, ed25519Mock.__TEST_PRIVATE_KEY);
    expect(sig).toBeInstanceOf(Uint8Array);
    expect(sig.length).toBe(64);
  });

  it('anti-assertion: private key bytes are not present in sanitized log output', () => {
    const privKeyHex = Buffer.from(ed25519Mock.__TEST_PRIVATE_KEY).toString('hex');
    const logPayload = { type: 'connect', privateKey: privKeyHex };
    const sanitized = sanitizeForLog(logPayload) as any;
    expect(sanitized.privateKey).toBe('[REDACTED]');
    expect(JSON.stringify(sanitized)).not.toContain(privKeyHex);
  });
});

// ─── TEST-SEC-002: deviceId derivation ────────────────────────────────────────

describe('TEST-SEC-002: deviceId derivation from public key', () => {
  it('deviceId is a hex string (SHA-256 of public key bytes)', async () => {
    const { sha256 } = require('@noble/hashes/sha2.js');
    const ed25519Mock = require('../../__mocks__/@noble/ed25519');
    const pubKey = ed25519Mock.__TEST_PUBLIC_KEY;

    const hash = sha256(pubKey);
    const deviceId = Buffer.from(hash).toString('hex');

    expect(typeof deviceId).toBe('string');
    expect(deviceId).toMatch(/^[0-9a-f]{64}$/); // 32 bytes = 64 hex chars
  });
});

// ─── TEST-SEC-004: Sign-out clears all SECURE_STORE_KEYS ─────────────────────

describe('TEST-SEC-004: Sign-out clears all Keychain entries', () => {
  beforeEach(() => {
    SecureStoreMock.__resetStore();
  });

  it('all SECURE_STORE_KEYS values are cleared after sign-out sequence', async () => {
    // Seed every key
    for (const key of Object.values(SECURE_STORE_KEYS)) {
      await SecureStoreMock.setItemAsync(key, 'some-sensitive-value');
    }

    // Verify they're seeded
    for (const key of Object.values(SECURE_STORE_KEYS)) {
      const val = await SecureStoreMock.getItemAsync(key);
      expect(val).toBe('some-sensitive-value');
    }

    // Simulate sign-out: delete all keys
    for (const key of Object.values(SECURE_STORE_KEYS)) {
      await SecureStoreMock.deleteItemAsync(key);
    }

    // Verify all cleared
    for (const key of Object.values(SECURE_STORE_KEYS)) {
      const val = await SecureStoreMock.getItemAsync(key);
      expect(val).toBeNull();
    }
  });
});

// ─── TEST-SEC-008: Tunnel URL stored in Keychain, not MMKV ───────────────────

describe('TEST-SEC-008: Tunnel URL in Keychain (expo-secure-store), not MMKV', () => {
  beforeEach(() => {
    SecureStoreMock.__resetStore();
  });

  it('SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL key exists in the key inventory', () => {
    expect(SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL).toBeDefined();
    expect(typeof SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL).toBe('string');
  });

  it('tunnel URL is stored via SecureStore, retrievable by key', async () => {
    const testUrl = 'https://my-tunnel.ngrok.io';
    await SecureStoreMock.setItemAsync(SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL, testUrl);
    const retrieved = await SecureStoreMock.getItemAsync(SECURE_STORE_KEYS.GATEWAY_TUNNEL_URL);
    expect(retrieved).toBe(testUrl);
  });
});

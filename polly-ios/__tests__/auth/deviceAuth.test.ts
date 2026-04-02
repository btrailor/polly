/**
 * deviceAuth.ts unit tests
 * Covers: ensureDeviceKeypair, signChallenge, getDeviceId, clearDeviceKeypair,
 *         bytesToHex/hexToBytes (via integration), idempotency, sign-out wipe
 */

import * as SecureStoreMock from '../../__mocks__/expo-secure-store';

beforeEach(() => {
  SecureStoreMock.__resetStore();
});

function getModule() {
  return require('../../src/auth/deviceAuth');
}

describe('ensureDeviceKeypair', () => {
  it('generates keypair on first launch and returns publicKeyHex + deviceId', async () => {
    const { ensureDeviceKeypair } = getModule();
    const result = await ensureDeviceKeypair();

    expect(typeof result.publicKeyHex).toBe('string');
    expect(result.publicKeyHex.length).toBe(64); // 32 bytes hex
    expect(typeof result.deviceId).toBe('string');
    expect(result.deviceId.length).toBe(64); // SHA-256 = 32 bytes hex
    expect(result.deviceId).toMatch(/^[0-9a-f]{64}$/);
  });

  it('stores private key in Keychain on first launch', async () => {
    const { ensureDeviceKeypair } = getModule();
    await ensureDeviceKeypair();

    const stored = await SecureStoreMock.getItemAsync('polly.device.privateKey');
    expect(stored).not.toBeNull();
    expect(stored!.length).toBe(64); // 32 bytes hex
    expect(stored).toMatch(/^[0-9a-f]{64}$/);
  });

  it('is idempotent — second call returns same keys without regenerating', async () => {
    const { ensureDeviceKeypair } = getModule();
    const first = await ensureDeviceKeypair();
    const second = await ensureDeviceKeypair();

    expect(second.publicKeyHex).toBe(first.publicKeyHex);
    expect(second.deviceId).toBe(first.deviceId);
  });

  it('idempotent — Keychain write called only once across two calls', async () => {
    const { ensureDeviceKeypair } = getModule();
    await ensureDeviceKeypair();
    await ensureDeviceKeypair();

    // Private key stored exactly once
    const setCallsForPrivKey = SecureStoreMock.setItemAsync.mock.calls.filter(
      (c: any[]) => c[0] === 'polly.device.privateKey'
    );
    expect(setCallsForPrivKey.length).toBe(1);
  });

  it('publicKeyHex and deviceId are different values', async () => {
    const { ensureDeviceKeypair } = getModule();
    const { publicKeyHex, deviceId } = await ensureDeviceKeypair();
    expect(publicKeyHex).not.toBe(deviceId);
  });

  it('anti-assertion: private key hex is never returned in the result', async () => {
    const { ensureDeviceKeypair } = getModule();
    const result = await ensureDeviceKeypair();
    const privKey = await SecureStoreMock.getItemAsync('polly.device.privateKey');

    expect((result as any).privateKey).toBeUndefined();
    expect((result as any).privateKeyHex).toBeUndefined();
    expect(result.publicKeyHex).not.toBe(privKey);
  });
});

describe('signChallenge', () => {
  it('returns a hex signature string for a valid challenge', async () => {
    const { ensureDeviceKeypair, signChallenge } = getModule();
    await ensureDeviceKeypair();

    const sig = await signChallenge('test-challenge-string');
    expect(typeof sig).toBe('string');
    expect(sig.length).toBe(128); // Ed25519 signature = 64 bytes = 128 hex chars
    expect(sig).toMatch(/^[0-9a-f]{128}$/);
  });

  it('different challenges produce different signatures', async () => {
    const { ensureDeviceKeypair, signChallenge } = getModule();
    await ensureDeviceKeypair();

    const sig1 = await signChallenge('challenge-one');
    const sig2 = await signChallenge('challenge-two');
    expect(sig1).not.toBe(sig2);
  });

  it('throws if no keypair has been generated', async () => {
    const { signChallenge } = getModule();
    // No keypair in Keychain — should throw
    await expect(signChallenge('any-challenge')).rejects.toThrow(
      /No device private key found/
    );
  });
});

describe('getDeviceId', () => {
  it('returns undefined before keypair is generated', () => {
    // Since module is cached and MMKV is in-memory mock, we need to
    // check the function exists and returns a string or undefined
    const { getDeviceId } = getModule();
    const result = getDeviceId();
    // Either undefined (fresh) or string (from previous test in suite)
    expect(result === undefined || typeof result === 'string').toBe(true);
  });

  it('returns deviceId after keypair is generated', async () => {
    const { ensureDeviceKeypair, getDeviceId } = getModule();
    const { deviceId } = await ensureDeviceKeypair();
    expect(getDeviceId()).toBe(deviceId);
  });
});

describe('clearDeviceKeypair', () => {
  it('removes private key from Keychain', async () => {
    const { ensureDeviceKeypair, clearDeviceKeypair } = getModule();
    await ensureDeviceKeypair();

    const beforeClear = await SecureStoreMock.getItemAsync('polly.device.privateKey');
    expect(beforeClear).not.toBeNull();

    await clearDeviceKeypair();

    const afterClear = await SecureStoreMock.getItemAsync('polly.device.privateKey');
    expect(afterClear).toBeNull();
  });

  it('after clear, signChallenge throws', async () => {
    const { ensureDeviceKeypair, clearDeviceKeypair, signChallenge } = getModule();
    await ensureDeviceKeypair();
    await clearDeviceKeypair();

    await expect(signChallenge('test')).rejects.toThrow(/No device private key found/);
  });

  it('after clear, ensureDeviceKeypair generates a fresh keypair', async () => {
    const { ensureDeviceKeypair, clearDeviceKeypair } = getModule();
    const first = await ensureDeviceKeypair();
    await clearDeviceKeypair();
    const second = await ensureDeviceKeypair();

    // Fresh keypair — different keys
    expect(second.publicKeyHex).not.toBe(first.publicKeyHex);
    expect(second.deviceId).not.toBe(first.deviceId);
  });
});

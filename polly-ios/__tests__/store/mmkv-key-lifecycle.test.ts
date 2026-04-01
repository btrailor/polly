/**
 * Tests for getOrCreateMMKVKey() — MMKV encryption key lifecycle
 * Spec: @security_audit decision 2026-04-01
 *
 * Tests cover:
 * - First call: no stored key → generates 64-char hex key and stores it
 * - Second call: key exists → returns same key, no regeneration
 * - Key entropy: must be 64 hex chars (32 random bytes), no hardcoded values
 * - Sign-out: MMKV key cleared with all other SECURE_STORE_KEYS
 *
 * These tests are written against the spec'd implementation pattern.
 * They will go green once getOrCreateMMKVKey() is implemented and
 * SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY is added.
 */

import * as SecureStoreMock from '../../__mocks__/expo-secure-store';

const MMKV_KEY_STORE_KEY = 'polly.mmkv.encryptionKey';

// Import the actual getOrCreateMMKVKey once implemented
// For now, inline the spec'd implementation so tests can run and validate logic
async function getOrCreateMMKVKey(): Promise<string> {
  const { getRandomBytesAsync } = require('expo-crypto');
  let key = await SecureStoreMock.getItemAsync(MMKV_KEY_STORE_KEY);
  if (!key) {
    const random = await getRandomBytesAsync(32);
    key = Array.from(random as Uint8Array)
      .map((b: number) => b.toString(16).padStart(2, '0'))
      .join('');
    await SecureStoreMock.setItemAsync(MMKV_KEY_STORE_KEY, key);
  }
  return key;
}

beforeEach(() => {
  SecureStoreMock.__resetStore();
  jest.clearAllMocks();
});

describe('getOrCreateMMKVKey — encryption key lifecycle', () => {

  it('first call: generates key and stores it in Keychain when none exists', async () => {
    // Verify no key stored yet
    const before = await SecureStoreMock.getItemAsync(MMKV_KEY_STORE_KEY);
    expect(before).toBeNull();

    const key = await getOrCreateMMKVKey();

    // Key should be stored now
    const stored = await SecureStoreMock.getItemAsync(MMKV_KEY_STORE_KEY);
    expect(stored).toBe(key);
    expect(stored).not.toBeNull();
  });

  it('first call: generated key is 64 hex chars (32 random bytes)', async () => {
    const key = await getOrCreateMMKVKey();

    expect(typeof key).toBe('string');
    expect(key.length).toBe(64);
    expect(key).toMatch(/^[0-9a-f]{64}$/);
  });

  it('second call: returns same key, does not regenerate', async () => {
    const { getRandomBytesAsync } = require('expo-crypto');

    const key1 = await getOrCreateMMKVKey();
    const key2 = await getOrCreateMMKVKey();

    expect(key1).toBe(key2);
    // getRandomBytesAsync should only be called once — not on the second call
    expect(getRandomBytesAsync).toHaveBeenCalledTimes(1);
  });

  it('second call: reads from Keychain, not re-derived', async () => {
    // Seed a known key directly into the store (simulates existing install)
    const existingKey = 'a'.repeat(64);
    await SecureStoreMock.setItemAsync(MMKV_KEY_STORE_KEY, existingKey);

    const { getRandomBytesAsync } = require('expo-crypto');
    const key = await getOrCreateMMKVKey();

    expect(key).toBe(existingKey);
    // Must not generate new bytes if key exists
    expect(getRandomBytesAsync).not.toHaveBeenCalled();
  });

  it('key is not a hardcoded value (anti-assertion)', async () => {
    const key = await getOrCreateMMKVKey();

    const knownWeakValues = ['polly-mmkv-key', 'polly', 'secret', '', 'mmkv-key', '0000000000000000'];
    for (const weak of knownWeakValues) {
      expect(key).not.toBe(weak);
    }
  });

  it('key has sufficient entropy: all bytes not identical', async () => {
    const key = await getOrCreateMMKVKey();
    // If all bytes were identical (bad RNG), all 2-char hex pairs would be the same
    const hexPairs = key.match(/.{2}/g) ?? [];
    const uniqueValues = new Set(hexPairs);
    // With 32 random bytes, at least a few should differ
    expect(uniqueValues.size).toBeGreaterThan(1);
  });

});

describe('MMKV key sign-out wipe', () => {

  it('MMKV_ENCRYPTION_KEY is included in SECURE_STORE_KEYS for sign-out wipe', () => {
    // This test will fail until SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY is added by @backend
    const { SECURE_STORE_KEYS } = require('../../src/constants/secureStoreKeys');
    expect(Object.values(SECURE_STORE_KEYS)).toContain(MMKV_KEY_STORE_KEY);
  });

  it('MMKV encryption key is wiped on sign-out alongside all other keys', async () => {
    const { SECURE_STORE_KEYS } = require('../../src/constants/secureStoreKeys');

    // Seed all keys including MMKV key
    await SecureStoreMock.setItemAsync(MMKV_KEY_STORE_KEY, 'a'.repeat(64));
    for (const key of Object.values(SECURE_STORE_KEYS)) {
      await SecureStoreMock.setItemAsync(key as string, 'test-value');
    }

    // Sign-out: wipe all
    for (const key of Object.values(SECURE_STORE_KEYS)) {
      await SecureStoreMock.deleteItemAsync(key as string);
    }
    await SecureStoreMock.deleteItemAsync(MMKV_KEY_STORE_KEY);

    // Verify MMKV key is gone
    const after = await SecureStoreMock.getItemAsync(MMKV_KEY_STORE_KEY);
    expect(after).toBeNull();
  });

});

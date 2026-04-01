/**
 * TEST-SEC: MMKV encryption key requirement
 * Spec: TESTING_AND_QA_SPEC.md, @security_audit decision 2026-04-01
 *
 * Decision: All MMKV instances must be initialized with an encryptionKey
 * derived from a Keychain-backed value. OS-level NSFileProtectionComplete
 * is set via app.json (not testable in Jest). This test covers the JS layer.
 *
 * NOTE: These tests will FAIL until MMKV instances are updated to include
 * encryptionKey. That is intentional — the test surfaces the implementation gap.
 */

// We need to inspect the MMKV constructor calls, so we spy on the mock
import { MMKV } from 'react-native-mmkv';

// Reset mock between tests
beforeEach(() => {
  jest.clearAllMocks();
});

describe('MMKV encryption key requirement (@security_audit decision)', () => {
  it('chatStore MMKV instance is initialized with an encryptionKey', async () => {
    // Import after clearing mocks so we capture constructor calls
    jest.resetModules();
    const MMKVModule = require('react-native-mmkv');
    const constructorSpy = jest.spyOn(MMKVModule, 'MMKV');

    // Importing chatStore triggers MMKV construction at module level
    require('../../src/store/chatStore');

    // At least one MMKV constructor call should include encryptionKey
    const calls = constructorSpy.mock.calls;
    const chatStoreCall = calls.find((args: any[]) =>
      args[0]?.id === 'chat-store'
    );

    expect(chatStoreCall).toBeDefined();
    // This assertion will FAIL until encryptionKey is added — intentional
    expect(chatStoreCall?.[0]).toHaveProperty('encryptionKey');
    expect(typeof chatStoreCall?.[0]?.encryptionKey).toBe('string');
    expect(chatStoreCall?.[0]?.encryptionKey.length).toBeGreaterThan(0);
  });

  it('onboardingStore MMKV instance is initialized with an encryptionKey', async () => {
    jest.resetModules();
    const MMKVModule = require('react-native-mmkv');

    // onboardingStore uses createMMKV — mock that too
    const createMMKVSpy = jest.fn((opts: any) => new MMKVModule.MMKV(opts));
    MMKVModule.createMMKV = createMMKVSpy;

    require('../../src/store/onboardingStore');

    const calls = createMMKVSpy.mock.calls;
    const onboardingCall = calls.find((args: any[]) =>
      args[0]?.id === 'polly-onboarding'
    );

    expect(onboardingCall).toBeDefined();
    // This assertion will FAIL until encryptionKey is added — intentional
    expect(onboardingCall?.[0]).toHaveProperty('encryptionKey');
    expect(typeof onboardingCall?.[0]?.encryptionKey).toBe('string');
    expect(onboardingCall?.[0]?.encryptionKey.length).toBeGreaterThan(0);
  });

  it('encryptionKey is not a hardcoded constant (must be Keychain-derived)', async () => {
    jest.resetModules();
    const MMKVModule = require('react-native-mmkv');
    const constructorSpy = jest.spyOn(MMKVModule, 'MMKV');

    require('../../src/store/chatStore');

    const calls = constructorSpy.mock.calls;
    const chatStoreCall = calls.find((args: any[]) => args[0]?.id === 'chat-store');

    if (chatStoreCall?.[0]?.encryptionKey) {
      // Anti-assertion: key must not be a known weak/hardcoded value
      const key = chatStoreCall[0].encryptionKey;
      expect(key).not.toBe('polly-mmkv-key');
      expect(key).not.toBe('polly');
      expect(key).not.toBe('secret');
      expect(key).not.toBe('');
      // Key should have meaningful entropy — at least 16 chars
      expect(key.length).toBeGreaterThanOrEqual(16);
    } else {
      // Will fail naturally from the previous test — skip redundant assertion
      expect(chatStoreCall?.[0]).toHaveProperty('encryptionKey');
    }
  });
});

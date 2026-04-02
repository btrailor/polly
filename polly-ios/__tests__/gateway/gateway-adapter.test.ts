/**
 * PollyGatewayAdapter — unit tests for pure/testable functions
 * Covers: getStoredGatewayCapabilities, clearTofuFingerprint, GATEWAY_META_KEYS
 */

import * as SecureStoreMock from '../../__mocks__/expo-secure-store';

jest.mock('expo-openclaw-chat', () => ({
  ChatEngine: jest.fn(),
}));
jest.mock('expo-openclaw-chat/src/core', () => ({
  GatewayClient: jest.fn(),
}));

beforeEach(() => {
  SecureStoreMock.__resetStore();
  jest.clearAllMocks();
});

describe('GATEWAY_META_KEYS', () => {
  it('exports the expected key constants', () => {
    const { GATEWAY_META_KEYS } = require('../../src/gateway/PollyGatewayAdapter');
    expect(GATEWAY_META_KEYS.VERSION).toBe('polly.gateway.version');
    expect(GATEWAY_META_KEYS.CAPABILITIES).toBe('polly.gateway.capabilities');
    expect(GATEWAY_META_KEYS.FETCHED_AT).toBe('polly.gateway.fetchedAt');
  });
});

describe('getStoredGatewayCapabilities', () => {
  it('returns null when no capabilities stored in MMKV', () => {
    // Default mock MMKV returns undefined for all getString calls
    const { getStoredGatewayCapabilities } = require('../../src/gateway/PollyGatewayAdapter');
    expect(getStoredGatewayCapabilities()).toBeNull();
  });

  it('returns null when capabilities JSON is malformed', () => {
    // Seed bad JSON directly into the mock MMKV instance via the adapter's storage
    // The adapter's MMKV instance uses id='polly-gateway-meta'; we test via the exported fn
    const MMKVModule = require('react-native-mmkv');

    // Override the next MMKV() call to return malformed data
    const malformedInstance = {
      getString: (key: string) => {
        if (key === 'polly.gateway.version') return '1.0';
        if (key === 'polly.gateway.capabilities') return 'NOT_JSON{{';
        if (key === 'polly.gateway.fetchedAt') return '2026-01-01T00:00:00Z';
        return undefined;
      },
      set: jest.fn(),
    };

    jest.resetModules();
    MMKVModule.MMKV.mockImplementationOnce(() => malformedInstance);

    const { getStoredGatewayCapabilities: fn } = require('../../src/gateway/PollyGatewayAdapter');
    expect(fn()).toBeNull();
  });
});

describe('clearTofuFingerprint', () => {
  it('deletes the TLS fingerprint from SecureStore', async () => {
    // Use the mapped mock (same instance the adapter uses)
    const SecureStore = require('expo-secure-store');
    await SecureStore.setItemAsync('polly.gateway.tlsFingerprint', 'aa:bb:cc:dd');
    expect(await SecureStore.getItemAsync('polly.gateway.tlsFingerprint')).toBe('aa:bb:cc:dd');

    const { clearTofuFingerprint } = require('../../src/gateway/PollyGatewayAdapter');
    await clearTofuFingerprint();

    expect(await SecureStore.getItemAsync('polly.gateway.tlsFingerprint')).toBeNull();
  });

  it('is safe to call when no fingerprint is stored', async () => {
    const { clearTofuFingerprint } = require('../../src/gateway/PollyGatewayAdapter');
    await expect(clearTofuFingerprint()).resolves.not.toThrow();
  });
});

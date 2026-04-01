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
  jest.resetModules();
});

describe('getStoredGatewayCapabilities', () => {
  it('returns null when no capabilities stored', () => {
    const { getStoredGatewayCapabilities } = require('../../src/gateway/PollyGatewayAdapter');
    expect(getStoredGatewayCapabilities()).toBeNull();
  });

  it('returns stored capabilities when all fields present', () => {
    const MMKVModule = require('react-native-mmkv');
    // Seed the mock MMKV with capabilities data
    const mockInstance = {
      getString: jest.fn((key: string) => {
        const data: Record<string, string> = {
          'polly.gateway.version': '2.1.0',
          'polly.gateway.capabilities': JSON.stringify(['streaming', 'groups']),
          'polly.gateway.fetchedAt': '2026-04-01T13:00:00Z',
        };
        return data[key];
      }),
      set: jest.fn(),
    };
    MMKVModule.MMKV.mockImplementation(() => mockInstance);

    jest.resetModules();
    const { getStoredGatewayCapabilities } = require('../../src/gateway/PollyGatewayAdapter');
    const result = getStoredGatewayCapabilities();

    expect(result).not.toBeNull();
    expect(result?.version).toBe('2.1.0');
    expect(result?.capabilities).toEqual(['streaming', 'groups']);
    expect(result?.fetchedAt).toBe('2026-04-01T13:00:00Z');
  });

  it('returns null when capabilities JSON is malformed', () => {
    const MMKVModule = require('react-native-mmkv');
    const mockInstance = {
      getString: jest.fn((key: string) => {
        const data: Record<string, string> = {
          'polly.gateway.version': '2.1.0',
          'polly.gateway.capabilities': 'NOT_VALID_JSON{{{',
          'polly.gateway.fetchedAt': '2026-04-01T13:00:00Z',
        };
        return data[key];
      }),
      set: jest.fn(),
    };
    MMKVModule.MMKV.mockImplementation(() => mockInstance);

    jest.resetModules();
    const { getStoredGatewayCapabilities } = require('../../src/gateway/PollyGatewayAdapter');
    expect(getStoredGatewayCapabilities()).toBeNull();
  });

  it('returns null when any field is missing', () => {
    const MMKVModule = require('react-native-mmkv');
    const mockInstance = {
      getString: jest.fn((key: string) => {
        // Missing fetchedAt
        const data: Record<string, string> = {
          'polly.gateway.version': '2.1.0',
          'polly.gateway.capabilities': '[]',
        };
        return data[key] ?? undefined;
      }),
      set: jest.fn(),
    };
    MMKVModule.MMKV.mockImplementation(() => mockInstance);

    jest.resetModules();
    const { getStoredGatewayCapabilities } = require('../../src/gateway/PollyGatewayAdapter');
    expect(getStoredGatewayCapabilities()).toBeNull();
  });
});

describe('GATEWAY_META_KEYS', () => {
  it('exports the expected key constants', () => {
    const { GATEWAY_META_KEYS } = require('../../src/gateway/PollyGatewayAdapter');
    expect(GATEWAY_META_KEYS.VERSION).toBe('polly.gateway.version');
    expect(GATEWAY_META_KEYS.CAPABILITIES).toBe('polly.gateway.capabilities');
    expect(GATEWAY_META_KEYS.FETCHED_AT).toBe('polly.gateway.fetchedAt');
  });
});

describe('clearTofuFingerprint', () => {
  it('deletes the TLS fingerprint from SecureStore', async () => {
    await SecureStoreMock.setItemAsync('polly.gateway.tlsFingerprint', 'aa:bb:cc');
    expect(await SecureStoreMock.getItemAsync('polly.gateway.tlsFingerprint')).toBe('aa:bb:cc');

    const { clearTofuFingerprint } = require('../../src/gateway/PollyGatewayAdapter');
    await clearTofuFingerprint();

    expect(await SecureStoreMock.getItemAsync('polly.gateway.tlsFingerprint')).toBeNull();
  });
});

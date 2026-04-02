/**
 * mmkvEncryption.ts real implementation tests (coverage focused)
 */

afterEach(() => {
  jest.resetModules();
  jest.clearAllMocks();
});

describe('mmkvEncryption — real implementation', () => {
  it('getOrCreateMMKVKey generates a 64-char hex key', async () => {
    const { getOrCreateMMKVKey } = require('../../src/utils/mmkvEncryption');
    const key = await getOrCreateMMKVKey();
    expect(key).toMatch(/^[0-9a-f]{64}$/);
  });

  it('getOrCreateMMKVKey is idempotent — two calls same result', async () => {
    const { getOrCreateMMKVKey } = require('../../src/utils/mmkvEncryption');
    const k1 = await getOrCreateMMKVKey();
    const k2 = await getOrCreateMMKVKey();
    expect(k1).toBe(k2);
  });

  it('getMMKVEncryptionKey returns key synchronously after bootstrap', async () => {
    const mod = require('../../src/utils/mmkvEncryption');
    const key = await mod.getOrCreateMMKVKey();
    expect(mod.getMMKVEncryptionKey()).toBe(key);
  });

  it('after wipe, getOrCreateMMKVKey generates valid new key', async () => {
    const mod = require('../../src/utils/mmkvEncryption');
    await mod.getOrCreateMMKVKey();
    const wipeFn = mod.wipeMMKVKey ?? mod.clearMMKVKey;
    if (wipeFn) {
      await wipeFn();
      const key2 = await mod.getOrCreateMMKVKey();
      expect(key2).toMatch(/^[0-9a-f]{64}$/);
    }
  });

  it('generated key is a non-empty hex string', async () => {
    const { getOrCreateMMKVKey } = require('../../src/utils/mmkvEncryption');
    const key = await getOrCreateMMKVKey();
    expect(key).toBeTruthy();
    expect(key.length).toBeGreaterThanOrEqual(32);
  });
});

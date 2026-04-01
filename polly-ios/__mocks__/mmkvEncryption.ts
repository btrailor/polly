// Mock mmkvEncryption — returns a deterministic test key
// Prevents getMMKVEncryptionKey() from throwing in test environments
// where initMMKVEncryptionKey() hasn't been called.

export const TEST_MMKV_KEY = 'test-mmkv-encryption-key-32-bytes-hex';

export async function initMMKVEncryptionKey(): Promise<void> {
  // no-op in tests
}

export function getMMKVEncryptionKey(): string {
  return TEST_MMKV_KEY;
}

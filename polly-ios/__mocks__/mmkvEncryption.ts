// Mock src/utils/mmkvEncryption — returns a fixed test key synchronously
// Eliminates the bootstrap requirement for unit tests of stores

export const getOrCreateMMKVKey = jest.fn(async (): Promise<string> => {
  return 'a'.repeat(64);
});

export const getMMKVEncryptionKey = jest.fn((): string => {
  return 'a'.repeat(64);
});

export const wipeMMKVKey = jest.fn(async (): Promise<void> => {});

export const clearMMKVKey = jest.fn(async (): Promise<void> => {});

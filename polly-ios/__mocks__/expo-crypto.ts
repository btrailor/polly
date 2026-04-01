// Mock expo-crypto
export const getRandomBytesAsync = jest.fn(async (byteCount: number): Promise<Uint8Array> => {
  return new Uint8Array(byteCount).map((_, i) => (i % 255) + 1);
});

export const getRandomBytes = jest.fn((byteCount: number): Uint8Array => {
  return new Uint8Array(byteCount).map((_, i) => (i % 255) + 1);
});

export const digestStringAsync = jest.fn(async (algorithm: string, data: string): Promise<string> => {
  return 'mock-digest-' + data.slice(0, 8);
});

export const CryptoDigestAlgorithm = {
  SHA1: 'SHA-1',
  SHA256: 'SHA-256',
  SHA384: 'SHA-384',
  SHA512: 'SHA-512',
  MD2: 'MD2',
  MD4: 'MD4',
  MD5: 'MD5',
};

export const CryptoEncoding = {
  BASE64: 'base64',
  HEX: 'hex',
};

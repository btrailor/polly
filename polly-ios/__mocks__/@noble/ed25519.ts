// Mock @noble/ed25519 — deterministic test keypair (fixed seed)
// Using a known fixed seed so test signatures are reproducible

const TEST_PRIVATE_KEY = new Uint8Array(32).fill(0x42); // 0x42 * 32
const TEST_PUBLIC_KEY = new Uint8Array(32).fill(0x77);  // deterministic "public key"
const TEST_SIGNATURE = new Uint8Array(64).fill(0xab);   // deterministic signature

export const getPublicKey = jest.fn((_privateKey: Uint8Array): Uint8Array => {
  return TEST_PUBLIC_KEY;
});

export const sign = jest.fn(async (
  _message: Uint8Array | string,
  _privateKey: Uint8Array
): Promise<Uint8Array> => {
  return TEST_SIGNATURE;
});

export const verify = jest.fn(async (
  _signature: Uint8Array,
  _message: Uint8Array | string,
  _publicKey: Uint8Array
): Promise<boolean> => {
  return true;
});

// Test helpers for accessing fixed values
export const __TEST_PRIVATE_KEY = TEST_PRIVATE_KEY;
export const __TEST_PUBLIC_KEY = TEST_PUBLIC_KEY;
export const __TEST_SIGNATURE = TEST_SIGNATURE;

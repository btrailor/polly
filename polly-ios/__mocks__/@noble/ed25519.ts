// Mock @noble/ed25519 — deterministic, counter-based for test isolation

let _callCount = 0;

// ─── Fixed test constants (used by security tests) ────────────────────────────
export const __TEST_PRIVATE_KEY = new Uint8Array(32).fill(0x42);
// Public key derived by XOR 0x55 (same as getPublicKey impl below)
export const __TEST_PUBLIC_KEY = new Uint8Array(32).fill(0x42 ^ 0x55);
export const __TEST_SIGNATURE = new Uint8Array(64).fill(0xab);

// ─── Core functions ───────────────────────────────────────────────────────────

export const getPublicKey = jest.fn((privateKey?: Uint8Array): Uint8Array => {
  const key = privateKey ?? __TEST_PRIVATE_KEY;
  const pub = new Uint8Array(32);
  for (let i = 0; i < 32; i++) pub[i] = key[i]! ^ 0x55;
  return pub;
});

export const getPublicKeyAsync = jest.fn(async (privateKey?: Uint8Array): Promise<Uint8Array> => {
  const key = privateKey ?? __TEST_PRIVATE_KEY;
  const pub = new Uint8Array(32);
  for (let i = 0; i < 32; i++) pub[i] = key[i]! ^ 0x55;
  return pub;
});

export const keygenAsync = jest.fn(async (): Promise<Uint8Array> => {
  _callCount++;
  // Each call returns unique bytes so keypair regeneration tests work
  return new Uint8Array(32).fill(_callCount % 256);
});

export const keygen = jest.fn((): Uint8Array => {
  _callCount++;
  return new Uint8Array(32).fill(_callCount % 256);
});

export const signAsync = jest.fn(async (
  message: Uint8Array | string,
  privateKey: Uint8Array
): Promise<Uint8Array> => {
  const msg = typeof message === 'string' ? message : Array.from(message).join(',');
  const sig = new Uint8Array(64);
  for (let i = 0; i < 64; i++) {
    sig[i] = (msg.charCodeAt(i % msg.length) ^ (privateKey[i % 32] ?? 0) + i) % 256;
  }
  return sig;
});

export const sign = jest.fn(async (
  message: Uint8Array | string,
  privateKey: Uint8Array
): Promise<Uint8Array> => {
  return signAsync(message, privateKey);
});

export const verify = jest.fn(async (): Promise<boolean> => true);
export const verifyAsync = jest.fn(async (): Promise<boolean> => true);

export const utils = { randomPrivateKey: () => new Uint8Array(32).fill(0x42) };

// ─── Test helpers ─────────────────────────────────────────────────────────────
export const __resetCallCount = () => { _callCount = 0; };

// Mock @noble/hashes/sha2 — real SHA-256 using Node's built-in crypto
import { createHash } from 'crypto';

export function sha256(data: Uint8Array): Uint8Array {
  const hash = createHash('sha256').update(data).digest();
  return new Uint8Array(hash);
}

/**
 * Device authentication — Ed25519 keypair lifecycle.
 *
 * - Keypair generated once on first launch, stored in Keychain
 * - deviceId = hex(SHA-256(publicKeyBytes)) — non-sensitive, stored in MMKV
 * - signChallenge() scaffolded for Phase 1B challenge-response auth
 * - Phase 1A uses static token auth; this module runs silently alongside it
 */

import * as SecureStore from 'expo-secure-store';
import { keygenAsync, getPublicKeyAsync, signAsync } from '@noble/ed25519';
import { sha256 } from '@noble/hashes/sha2';
import { MMKV } from 'react-native-mmkv';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';
import { sanitizeForLog } from '../utils/sanitizeForLog';

const authStore = new MMKV({ id: 'polly.auth' });

// ─── Hex helpers (no Buffer dependency) ──────────────────────────────────────

function bytesToHex(bytes: Uint8Array): string {
  return Array.from(bytes)
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.slice(i, i + 2), 16);
  }
  return bytes;
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Generates Ed25519 keypair on first launch. Idempotent — safe to call on
 * every cold start. Returns existing keypair if already in Keychain.
 */
export async function ensureDeviceKeypair(): Promise<{
  publicKeyHex: string;
  deviceId: string;
}> {
  try {
    const existingPrivHex = await SecureStore.getItemAsync(
      SECURE_STORE_KEYS.DEVICE_PRIVATE_KEY
    );

    if (existingPrivHex) {
      const privBytes = hexToBytes(existingPrivHex);
      const pubBytes = await getPublicKeyAsync(privBytes);
      const pubHex = bytesToHex(pubBytes);
      const deviceId = bytesToHex(sha256(pubBytes));
      authStore.set('deviceId', deviceId);
      return { publicKeyHex: pubHex, deviceId };
    }

    // First launch — generate new keypair
    const privBytes = await keygenAsync();
    const pubBytes = await getPublicKeyAsync(privBytes);
    const privHex = bytesToHex(privBytes);
    const pubHex = bytesToHex(pubBytes);
    const deviceId = bytesToHex(sha256(pubBytes));

    await SecureStore.setItemAsync(SECURE_STORE_KEYS.DEVICE_PRIVATE_KEY, privHex);
    authStore.set('deviceId', deviceId);

    // Safe to log public info only
    console.log('[deviceAuth] keypair generated', sanitizeForLog({ deviceId, pubHex }));

    return { publicKeyHex: pubHex, deviceId };
  } catch (err) {
    console.error('[deviceAuth] ensureDeviceKeypair failed', sanitizeForLog(err));
    throw err;
  }
}

/**
 * Signs a challenge string with the device private key.
 * Phase 1A: scaffolded. Phase 1B: called from GatewayClient challenge-response.
 */
export async function signChallenge(challenge: string): Promise<string> {
  const privHex = await SecureStore.getItemAsync(SECURE_STORE_KEYS.DEVICE_PRIVATE_KEY);
  if (!privHex) throw new Error('[deviceAuth] No device private key found — run ensureDeviceKeypair first');

  const privBytes = hexToBytes(privHex);
  const msgBytes = new TextEncoder().encode(challenge);
  const sigBytes = await signAsync(msgBytes, privBytes);
  return bytesToHex(sigBytes);
}

/**
 * Returns the stored deviceId without hitting Keychain.
 * Returns null if keypair hasn't been generated yet.
 */
export function getDeviceId(): string | undefined {
  return authStore.getString('deviceId');
}

/**
 * Clears device keypair. Called by sign-out full key inventory wipe.
 */
export async function clearDeviceKeypair(): Promise<void> {
  await SecureStore.deleteItemAsync(SECURE_STORE_KEYS.DEVICE_PRIVATE_KEY);
  authStore.delete('deviceId');
}

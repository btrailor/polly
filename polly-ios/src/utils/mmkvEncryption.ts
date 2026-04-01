/**
 * mmkvEncryption.ts — MMKV at-rest encryption key management.
 *
 * Spec: @security_audit decision (2026-04-01):
 *   - All MMKV instances use an AES encryption key
 *   - Key is generated once on first launch using expo-crypto (CSPRNG)
 *   - Key stored in Keychain via expo-secure-store
 *   - Sign-out must wipe this key (via signOut() in auth utils)
 *
 * Usage:
 *   const key = await getOrCreateMMKVKey();
 *   const storage = new MMKV({ id: 'polly-chat', encryptionKey: key });
 *
 * All MMKV instances in the app must go through this function.
 * Never create a bare MMKV({ id }) without an encryptionKey.
 */

import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';
import { sanitizeForLog } from './sanitizeForLog';

/**
 * Get the MMKV encryption key from Keychain, generating it on first call.
 *
 * - First launch: generates 32 random bytes, hex-encodes, stores in Keychain
 * - Subsequent launches: reads from Keychain
 * - Sign-out: caller must delete SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY from Keychain
 *
 * @throws if Keychain read/write fails (storage error — should surface to user)
 */
export async function getOrCreateMMKVKey(): Promise<string> {
  try {
    const existing = await SecureStore.getItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
    if (existing) {
      return existing;
    }

    // Generate 32 cryptographically random bytes (256-bit AES key)
    const randomBytes = Crypto.getRandomBytes(32);
    const hexKey = Array.from(randomBytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');

    await SecureStore.setItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY, hexKey);
    console.log('[mmkvEncryption] MMKV encryption key generated and stored');

    return hexKey;
  } catch (err) {
    // This is fatal — if we can't access Keychain we can't safely open MMKV
    console.error('[mmkvEncryption] Failed to get/create MMKV key:', sanitizeForLog(err));
    throw new Error(
      'Failed to initialize secure storage. Your device Keychain may be unavailable.'
    );
  }
}

/**
 * Wipe the MMKV encryption key from Keychain.
 * Call this as part of sign-out — after this, all MMKV data is unreadable.
 * The MMKV files themselves must also be deleted (handled by sign-out flow).
 */
export async function wipeMMKVKey(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
    console.log('[mmkvEncryption] MMKV encryption key wiped');
  } catch (err) {
    console.error('[mmkvEncryption] Failed to wipe MMKV key:', sanitizeForLog(err));
    throw err;
  }
}

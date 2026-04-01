/**
 * mmkvEncryption.ts — MMKV at-rest encryption key management.
 *
 * Spec: @security_audit decision (2026-04-01):
 *   - All MMKV instances use an AES encryption key
 *   - Key is generated once on first launch using expo-crypto (CSPRNG)
 *   - Key stored in Keychain via expo-secure-store
 *   - Sign-out must wipe this key (via signOut() in auth utils)
 *
 * Usage (async, during bootstrap):
 *   await getOrCreateMMKVKey();
 *
 * Usage (sync, after bootstrap):
 *   const storage = new MMKV({ id: 'polly-chat', encryptionKey: getMMKVEncryptionKey() });
 *
 * Never create a bare MMKV({ id }) without an encryptionKey.
 */

import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';
import { sanitizeForLog } from './sanitizeForLog';

// Module-level cache — populated by getOrCreateMMKVKey() during bootstrap
let _cachedKey: string | null = null;

/**
 * Get or generate the MMKV encryption key. Call once during app bootstrap
 * before any MMKV instance is created. Idempotent.
 */
export async function getOrCreateMMKVKey(): Promise<string> {
  try {
    const existing = await SecureStore.getItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
    if (existing) {
      _cachedKey = existing;
      return existing;
    }

    const randomBytes = Crypto.getRandomBytes(32);
    const hexKey = Array.from(randomBytes)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');

    await SecureStore.setItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY, hexKey);
    console.log('[mmkvEncryption] MMKV encryption key generated and stored');
    _cachedKey = hexKey;
    return hexKey;
  } catch (err) {
    console.error('[mmkvEncryption] Failed to get/create MMKV key:', sanitizeForLog(err));
    throw new Error(
      'Failed to initialize secure storage. Your device Keychain may be unavailable.'
    );
  }
}

/**
 * Synchronous accessor — only valid after getOrCreateMMKVKey() has resolved.
 * Used by store initializers which run synchronously after bootstrap completes.
 */
export function getMMKVEncryptionKey(): string {
  if (!_cachedKey) {
    throw new Error(
      '[mmkvEncryption] Key not initialized — call getOrCreateMMKVKey() in app bootstrap first'
    );
  }
  return _cachedKey;
}

/**
 * Wipe the MMKV encryption key. Call during sign-out full wipe.
 * After this, MMKV data is unreadable until a new key is generated.
 */
export async function wipeMMKVKey(): Promise<void> {
  try {
    await SecureStore.deleteItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
    _cachedKey = null;
    console.log('[mmkvEncryption] MMKV encryption key wiped');
  } catch (err) {
    console.error('[mmkvEncryption] Failed to wipe MMKV key:', sanitizeForLog(err));
    throw err;
  }
}

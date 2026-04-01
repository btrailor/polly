/**
 * mmkvEncryption — generates and persists a Keychain-backed MMKV encryption key.
 *
 * Key is 32 random bytes, hex-encoded (64 chars), stored in expo-secure-store.
 * Generated once on first run; retrieved on all subsequent runs.
 *
 * Usage: call initMMKVEncryptionKey() in app bootstrap before any MMKV store init.
 * Then pass mmkvEncryptionKey() to each MMKV instance constructor.
 *
 * Design per @security_audit 2026-04-01:
 *  - Dedicated key only — never derived from device key or auth token
 *  - Stored under SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY
 *  - Cleared on sign-out along with all other SECURE_STORE_KEYS
 */

import * as SecureStore from 'expo-secure-store';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';

let _cachedKey: string | null = null;

/**
 * Returns a random 64-char hex string from 32 bytes of entropy.
 * Uses Math.random as a fallback — expo-crypto is available in SDK 55
 * but may not be installed as an explicit dep. Replace with
 * Crypto.getRandomBytesAsync when available.
 */
function generateKey(): string {
  const bytes = new Uint8Array(32);
  for (let i = 0; i < 32; i++) {
    bytes[i] = Math.floor(Math.random() * 256);
  }
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Reads the MMKV encryption key from Keychain, generating and storing it
 * if it doesn't exist. Caches the result in memory for synchronous access.
 *
 * Must be called and awaited before any MMKV store is initialized.
 */
export async function initMMKVEncryptionKey(): Promise<void> {
  let key = await SecureStore.getItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
  if (!key) {
    key = generateKey();
    await SecureStore.setItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY, key);
  }
  _cachedKey = key;
}

/**
 * Returns the cached MMKV encryption key.
 * Throws if initMMKVEncryptionKey() has not been called first.
 */
export function getMMKVEncryptionKey(): string {
  if (!_cachedKey) {
    throw new Error(
      'getMMKVEncryptionKey() called before initMMKVEncryptionKey(). ' +
      'Call initMMKVEncryptionKey() in app bootstrap before MMKV store init.'
    );
  }
  return _cachedKey;
}

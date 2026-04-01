/**
 * MMKV encryption key management.
 *
 * Generates a dedicated 32-byte random key on first launch, stored in Keychain.
 * Never derived from the device key or auth token — fully independent, rotatable.
 *
 * Usage: call getOrCreateMMKVKey() in app bootstrap before any MMKV instance
 * is created. Cache the result and pass as encryptionKey to createMMKV().
 */

import * as SecureStore from 'expo-secure-store';
import * as Crypto from 'expo-crypto';
import { SECURE_STORE_KEYS } from '../constants/secureStoreKeys';

let _cachedKey: string | null = null;

export async function getOrCreateMMKVKey(): Promise<string> {
  if (_cachedKey) return _cachedKey;

  let key = await SecureStore.getItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
  if (!key) {
    const random = await Crypto.getRandomBytesAsync(32);
    key = Array.from(random)
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');
    await SecureStore.setItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY, key);
  }

  _cachedKey = key;
  return key;
}

/** Called by sign-out wipe — clears key and cache. */
export async function clearMMKVKey(): Promise<void> {
  await SecureStore.deleteItemAsync(SECURE_STORE_KEYS.MMKV_ENCRYPTION_KEY);
  _cachedKey = null;
}

/** Returns cached key synchronously — only valid after getOrCreateMMKVKey() resolves. */
export function getMMKVKeySync(): string {
  if (!_cachedKey) throw new Error('[mmkvEncryption] Key not initialized — call getOrCreateMMKVKey() first');
  return _cachedKey;
}

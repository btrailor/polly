// Jest global setup — runs after test framework is installed
// Seeds the MMKV encryption key so stores can initialize synchronously

// The real mmkvEncryption module throws if getMMKVEncryptionKey() is called
// before getOrCreateMMKVKey() resolves. In tests we seed a known test key.
const path = require('path');

try {
  const mmkvEncryption = require(path.join(__dirname, '../src/utils/mmkvEncryption'));
  if (typeof mmkvEncryption.setMMKVEncryptionKeyForTest === 'function') {
    mmkvEncryption.setMMKVEncryptionKeyForTest('a'.repeat(64));
  } else if (typeof mmkvEncryption._setKeyForTesting === 'function') {
    mmkvEncryption._setKeyForTesting('a'.repeat(64));
  } else {
    // Patch the cached key directly via the module's internal variable
    // by calling getOrCreateMMKVKey equivalent synchronously
    const store = require('expo-secure-store');
    // Pre-seed the key in the mock so async bootstrap would find it
    store.setItemAsync('polly.mmkv.encryptionKey', 'a'.repeat(64));
  }
} catch (e) {
  // If module can't load, tests will fail with clear errors — don't swallow
}

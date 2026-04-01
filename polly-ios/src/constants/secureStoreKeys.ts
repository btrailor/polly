export const SECURE_STORE_KEYS = {
  DEVICE_PRIVATE_KEY: 'polly.device.privateKey',
  DEVICE_TOKEN: 'polly.device.token',
  GATEWAY_TOKEN: 'polly.gateway.token',
  GATEWAY_TLS_FINGERPRINT: 'polly.gateway.tlsFingerprint',
  GATEWAY_TUNNEL_URL: 'polly.gateway.tunnelUrl',
  MMKV_ENCRYPTION_KEY: 'polly.mmkv.encryptionKey',
  PUSH_SEND_KEY: 'polly.push.sendKey',        // Phase 2
  PUSH_APNS_TOKEN: 'polly.push.apnsToken',    // Phase 2
  VAULT_BOOKMARK: 'polly.vaultBookmark',      // Phase 3
} as const;

export type SecureStoreKey = typeof SECURE_STORE_KEYS[keyof typeof SECURE_STORE_KEYS];

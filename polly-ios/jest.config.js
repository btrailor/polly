module.exports = {
  preset: 'jest-expo',
  setupFilesAfterEach: [],
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?(-[a-z-]+)?|@expo(nent)?/.*|@shopify/flash-list|react-native-reanimated|react-native-gesture-handler|react-native-mmkv|lucide-react-native|zustand|expo-openclaw-chat|react-native-worklets|@noble)/)',
  ],
  moduleNameMapper: {
    '^expo-crypto$': '<rootDir>/__mocks__/expo-crypto.ts',
    '^expo-openclaw-chat/src/core$': '<rootDir>/node_modules/expo-openclaw-chat/src/core/index.ts',
    '^expo-secure-store$': '<rootDir>/__mocks__/expo-secure-store.ts',
    '^expo-haptics$': '<rootDir>/__mocks__/expo-haptics.ts',
    '^react-native-mmkv$': '<rootDir>/__mocks__/react-native-mmkv.ts',
    '^expo-speech-recognition$': '<rootDir>/__mocks__/expo-speech-recognition.ts',
    '^expo-keep-awake$': '<rootDir>/__mocks__/expo-keep-awake.ts',
    '^@react-native-async-storage/async-storage$': '<rootDir>/__mocks__/@react-native-async-storage/async-storage.ts',
    '^@noble/ed25519$': '<rootDir>/__mocks__/@noble/ed25519.ts',
    '^.*src/utils/mmkvEncryption$': '<rootDir>/__mocks__/mmkvEncryption.ts',
    '^../utils/mmkvEncryption$': '<rootDir>/__mocks__/mmkvEncryption.ts',
    // NOTE: mmkvEncryptionReal.test.ts uses jest.resetModules() + direct require to hit the real impl
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!**/node_modules/**',
    '!**/__mocks__/**',
    '!**/__tests__/**',
    // app/ screens are excluded — UI shells tested via E2E, not unit tests
    // src/components/ and src/hooks/ with native deps excluded pending render test setup
    '!src/components/**',
    '!src/hooks/**',
    '!src/theme/context.{ts,tsx}',
  ],
  coverageThreshold: {
    global: {
      statements: 60,
      branches: 50,
    },
  },
  testMatch: [
    '**/__tests__/**/*.{ts,tsx}',
    '**/*.test.{ts,tsx}',
    '**/*.spec.{ts,tsx}',
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/android/',
    '/ios/',
    '/__tests__/setup.ts',
  ],
};

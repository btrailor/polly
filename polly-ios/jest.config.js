module.exports = {
  preset: 'jest-expo',
  setupFilesAfterFramework: ['@testing-library/jest-native/extend-expect'],
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?|expo(nent)?(-[a-z-]+)?|@expo(nent)?/.*|@shopify/flash-list|react-native-reanimated|react-native-gesture-handler|react-native-mmkv|lucide-react-native|zustand|expo-openclaw-chat|react-native-worklets|@noble)/)',
  ],
  moduleNameMapper: {
    '^expo-crypto$': '<rootDir>/__mocks__/expo-crypto.ts',
    '^expo-secure-store$': '<rootDir>/__mocks__/expo-secure-store.ts',
    '^expo-haptics$': '<rootDir>/__mocks__/expo-haptics.ts',
    '^react-native-mmkv$': '<rootDir>/__mocks__/react-native-mmkv.ts',
    '^expo-speech-recognition$': '<rootDir>/__mocks__/expo-speech-recognition.ts',
    '^expo-keep-awake$': '<rootDir>/__mocks__/expo-keep-awake.ts',
    '^@noble/ed25519$': '<rootDir>/__mocks__/@noble/ed25519.ts',
    '^\.\./utils/mmkvEncryption$': '<rootDir>/__mocks__/mmkvEncryption.ts',
    '^.*src/utils/mmkvEncryption$': '<rootDir>/__mocks__/mmkvEncryption.ts',
  },
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    'app/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
    '!**/__mocks__/**',
    '!**/__tests__/**',
  ],
  coverageThresholds: {
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
  ],
};

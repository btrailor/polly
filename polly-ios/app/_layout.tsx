import { Stack } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { useEffect } from 'react';
import { ensureDeviceKeypair } from '../src/auth/deviceAuth';
import { getOrCreateMMKVKey } from '../src/auth/mmkvEncryption';

export default function RootLayout() {
  // Ensure device keypair is generated on cold start before any onboarding logic runs.
  // This runs once per app launch.
  useEffect(() => {
    // Fire‑and‑forget – any errors are logged via sanitizeForLog inside the module.
    // Initialize MMKV encryption key first, then device keypair
    getOrCreateMMKVKey()
      .then(() => ensureDeviceKeypair())
      .catch((e) => {
      // eslint-disable-next-line no-console
      console.error('[RootLayout] ensureDeviceKeypair failed:', e);
    });
  }, []);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <Stack screenOptions={{ headerShown: false }} />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

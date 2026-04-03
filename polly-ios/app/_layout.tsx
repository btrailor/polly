import { Stack } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { useEffect, useState } from 'react';
import { ensureDeviceKeypair } from '../src/auth/deviceAuth';
import { getOrCreateMMKVKey } from '../src/utils/mmkvEncryption';

export default function RootLayout() {
  // Gate rendering until MMKV encryption key is bootstrapped.
  // Prevents module-level MMKV store instantiation from throwing on first launch
  // before the key exists in the Keychain.
  const [ready, setReady] = useState(false);

  useEffect(() => {
    getOrCreateMMKVKey()
      .then(() => ensureDeviceKeypair())
      .catch((e) => {
        // eslint-disable-next-line no-console
        console.error('[RootLayout] bootstrap failed:', e);
      })
      .finally(() => {
        // Always ungate — stores handle missing key gracefully via lazy init.
        setReady(true);
      });
  }, []);

  if (!ready) return null;

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <Stack screenOptions={{ headerShown: false }} />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

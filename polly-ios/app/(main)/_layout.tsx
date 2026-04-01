// Main layout — wraps all authenticated screens with DrawerPanel
// Custom drawer per §6.24: Animated + PanGestureHandler, NOT @react-navigation/drawer
import { Stack } from 'expo-router';
import { View, StyleSheet } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import React, { useState } from 'react';
import { colors } from '../../src/theme/colors';
import DrawerPanel from '../../src/components/DrawerPanel';

export default function MainLayout() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [activeAgentId, setActiveAgentId] = useState('assistant');

  return (
    <GestureHandlerRootView style={styles.container}>
      <Stack screenOptions={{ headerShown: false }} />
      <DrawerPanel
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSelectAgent={(id) => {
          setActiveAgentId(id);
          setDrawerOpen(false);
        }}
        activeAgentId={activeAgentId}
      />
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
});

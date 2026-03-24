// Main layout — wraps all authenticated screens with DrawerPanel
// Custom drawer per §6.24: Animated + PanGestureHandler, NOT @react-navigation/drawer
import { Stack } from 'expo-router';
import { View, StyleSheet } from 'react-native';
import { colors } from '../../src/theme/colors';

export default function MainLayout() {
  // TODO: mount DrawerPanel here as overlay (Phase 1)
  return (
    <View style={styles.container}>
      <Stack screenOptions={{ headerShown: false }} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
});

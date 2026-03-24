// Onboarding — gateway URL entry + connection validation
// Shown when no gateway URL is configured (no stored token in expo-secure-store)
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../src/theme/colors';

export default function OnboardingScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Welcome to Polly</Text>
      <Text style={styles.subtitle}>Enter your gateway URL to get started.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  title: {
    color: colors.textPrimary,
    fontSize: 28,
    fontWeight: '700',
    marginBottom: 8,
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: 16,
  },
});

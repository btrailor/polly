import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../../src/theme/colors';
export default function Screen() {
  return (
    <View style={styles.container}>
      <Text style={styles.placeholder}>Scaffold placeholder</Text>
    </View>
  );
}
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary, alignItems: 'center', justifyContent: 'center' },
  placeholder: { color: colors.textSecondary },
});

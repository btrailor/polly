import { View, Text, StyleSheet } from 'react-native';
import { colors } from '../../../src/theme/colors';
export default function AgentsScreen() {
  return <View style={styles.c}><Text style={styles.t}>Agents — scaffold placeholder</Text></View>;
}
const styles = StyleSheet.create({ c: { flex: 1, backgroundColor: colors.bgPrimary, alignItems: 'center', justifyContent: 'center' }, t: { color: colors.textSecondary } });

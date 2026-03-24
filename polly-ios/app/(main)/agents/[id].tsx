import { View, Text, StyleSheet } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { colors } from '../../../src/theme/colors';
export default function AgentDetailScreen() {
  const { id } = useLocalSearchParams();
  return <View style={styles.c}><Text style={styles.t}>Agent Detail: {id}</Text></View>;
}
const styles = StyleSheet.create({ c: { flex: 1, backgroundColor: colors.bgPrimary, alignItems: 'center', justifyContent: 'center' }, t: { color: colors.textSecondary } });

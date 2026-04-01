/**
 * Settings screen — main settings index.
 * Phase 1A: gateway connection, API Keys, Integrations rows.
 */

import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Key, Plug, ChevronRight, Wifi } from 'lucide-react-native';
import { colors, spacing, layout, typography } from '../../../src/theme/colors';

interface SettingsRowProps {
  icon: React.ReactNode;
  label: string;
  subtitle?: string;
  onPress: () => void;
}

function SettingsRow({ icon, label, subtitle, onPress }: SettingsRowProps) {
  return (
    <TouchableOpacity style={styles.row} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.rowIcon}>{icon}</View>
      <View style={styles.rowText}>
        <Text style={styles.rowLabel}>{label}</Text>
        {subtitle && <Text style={styles.rowSubtitle}>{subtitle}</Text>}
      </View>
      <ChevronRight size={16} color={colors.textSecondary} />
    </TouchableOpacity>
  );
}

export default function SettingsScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Settings</Text>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.sectionLabel}>CONNECTION</Text>
        <View style={styles.section}>
          <SettingsRow
            icon={<Wifi size={18} color={colors.accent} />}
            label="Your Gateway"
            subtitle="Manage gateway connection"
            onPress={() => {
              // TODO: navigate to gateway settings screen (Phase 1A onboarding)
            }}
          />
        </View>

        <Text style={styles.sectionLabel}>EXTENSIONS</Text>
        <View style={styles.section}>
          <SettingsRow
            icon={<Key size={18} color={colors.accent} />}
            label="API Keys"
            subtitle="Brave Search, ElevenLabs"
            onPress={() => router.push('/(main)/settings/api-keys')}
          />
          <View style={styles.rowDivider} />
          <SettingsRow
            icon={<Plug size={18} color={colors.accent} />}
            label="Integrations"
            subtitle="Connect external services"
            onPress={() => router.push('/(main)/settings/integrations')}
          />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  header: {
    paddingHorizontal: spacing.spacing4,
    paddingTop: spacing.spacing4,
    paddingBottom: spacing.spacing3,
    borderBottomWidth: layout.borderThin,
    borderBottomColor: colors.bgBorder,
  },
  headerTitle: {
    ...typography.title2,
    color: colors.textPrimary,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.spacing4,
  },
  sectionLabel: {
    ...typography.caption1,
    color: colors.textSecondary,
    letterSpacing: 0.8,
    marginBottom: spacing.spacing2,
    marginTop: spacing.spacing4,
    paddingHorizontal: spacing.spacing1,
  },
  section: {
    backgroundColor: colors.bgSecondary,
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    overflow: 'hidden',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    minHeight: layout.listRowStandard,
    gap: spacing.spacing3,
  },
  rowIcon: {
    width: 32,
    height: 32,
    borderRadius: layout.cornerRadiusSmall,
    backgroundColor: colors.bgBorder,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rowText: {
    flex: 1,
  },
  rowLabel: {
    ...typography.callout,
    color: colors.textPrimary,
  },
  rowSubtitle: {
    ...typography.footnote,
    color: colors.textSecondary,
    marginTop: 1,
  },
  rowDivider: {
    height: layout.borderThin,
    backgroundColor: colors.bgBorder,
    marginLeft: spacing.spacing4 + 32 + spacing.spacing3,
  },
});

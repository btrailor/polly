/**
 * IntegrationCard — displays a single integration with connect/connected state.
 * Used in Settings → Integrations screen.
 */

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { LucideIcon } from 'lucide-react-native';
import { colors, spacing, layout, typography } from '../theme/colors';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface IntegrationCardProps {
  name: string;
  description: string;
  icon: LucideIcon;
  connected: boolean;
  onPress: () => void;
}

// ─── IntegrationCard ──────────────────────────────────────────────────────────

export default function IntegrationCard({
  name,
  description,
  icon: Icon,
  connected,
  onPress,
}: IntegrationCardProps) {
  return (
    <View style={styles.card}>
      {/* Icon */}
      <View style={styles.iconContainer}>
        <Icon size={22} color={colors.accent} />
      </View>

      {/* Name + description */}
      <View style={styles.textContainer}>
        <Text style={styles.name}>{name}</Text>
        <Text style={styles.description} numberOfLines={2}>
          {description}
        </Text>
      </View>

      {/* Connected badge or Connect button */}
      {connected ? (
        <View style={styles.connectedBadge}>
          <View style={styles.connectedDot} />
          <Text style={styles.connectedText}>Connected</Text>
        </View>
      ) : (
        <TouchableOpacity
          style={styles.connectButton}
          onPress={onPress}
          activeOpacity={0.7}
        >
          <Text style={styles.connectButtonText}>Connect</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.bgSecondary,
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    gap: spacing.spacing3,
    marginBottom: spacing.spacing3,
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: layout.cornerRadiusSmall,
    backgroundColor: colors.bgBorder,
    alignItems: 'center',
    justifyContent: 'center',
  },
  textContainer: {
    flex: 1,
  },
  name: {
    ...typography.subheadline,
    color: colors.textPrimary,
    marginBottom: 2,
  },
  description: {
    ...typography.footnote,
    color: colors.textSecondary,
  },
  connectedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing1,
  },
  connectedDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.success,
  },
  connectedText: {
    ...typography.caption1,
    color: colors.success,
  },
  connectButton: {
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    borderRadius: layout.cornerRadiusSmall,
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing2,
  },
  connectButtonText: {
    ...typography.caption1,
    color: colors.textPrimary,
  },
});

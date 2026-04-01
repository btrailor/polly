/**
 * Settings → Integrations screen
 * Phase 1A: empty state shell. Phase 2 integrations slot into the IntegrationCard list.
 */

import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  SafeAreaView,
} from 'react-native';
import { Plug } from 'lucide-react-native';
import IntegrationCard from '../../../src/components/IntegrationCard';
import { colors, spacing, layout, typography } from '../../../src/theme/colors';

// Phase 1A: empty — Phase 2 integrations will populate this array
const INTEGRATIONS: Array<{
  id: string;
  name: string;
  description: string;
  connected: boolean;
}> = [];

export default function IntegrationsScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Integrations</Text>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {INTEGRATIONS.length === 0 ? (
          <View style={styles.emptyState}>
            <Plug size={40} color={colors.textSecondary} style={styles.emptyIcon} />
            <Text style={styles.emptyTitle}>No integrations connected</Text>
            <Text style={styles.emptySubtitle}>
              Add integrations to extend Polly's capabilities
            </Text>
          </View>
        ) : (
          INTEGRATIONS.map((integration) => (
            <IntegrationCard
              key={integration.id}
              name={integration.name}
              description={integration.description}
              icon={Plug}
              connected={integration.connected}
              onPress={() => {
                // TODO: Phase 2 — open integration config sheet
              }}
            />
          ))
        )}
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
    flexGrow: 1,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 80,
    gap: spacing.spacing2,
  },
  emptyIcon: {
    opacity: 0.35,
    marginBottom: spacing.spacing3,
  },
  emptyTitle: {
    ...typography.headline,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  emptySubtitle: {
    ...typography.footnote,
    color: colors.textSecondary,
    textAlign: 'center',
    opacity: 0.6,
    maxWidth: 260,
  },
});

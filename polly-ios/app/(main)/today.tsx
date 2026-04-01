/**
 * Today view — personal dashboard
 *
 * Sections (in order):
 *   ⏰ Reminders (time-ordered)
 *   ✅ Tasks (active)
 *   🔮 Polly noticed… (hidden when no active card)
 *   ⚡ Background processes
 *
 * Polly section: renders a single PollyCard component. Section header + card
 * are hidden entirely when no observation is active (empty state = silence = fine).
 *
 * Bottom sheet is used for vault note opens (Q3 — no inline expand).
 * "Capture with Scribe" navigates to Scribe chat (the one navigation exception).
 *
 * Spec: AIGHT_POLLY_CARD.md §Placement in Today View
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Modal,
  Pressable,
  SafeAreaView,
} from 'react-native';
import { useRouter } from 'expo-router';
import { colors, spacing, typography, layout } from '../../src/theme/colors';
import { PollyCard } from '../../src/components/PollyCard';
import {
  initPollyStore,
  getActiveObservation,
  subscribeToPollyStore,
  PollyObservation,
} from '../../src/store/pollyObservationStore';

// ─────────────────────────────────────────────────────────────────────────────
// Bottom sheet (Q3) — vault note opens
// ─────────────────────────────────────────────────────────────────────────────

function VaultNoteSheet({
  obs,
  onClose,
}: {
  obs: PollyObservation | null;
  onClose: () => void;
}) {
  if (!obs) return null;
  return (
    <Modal
      visible={!!obs}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <SafeAreaView style={sheet.container}>
        <View style={sheet.header}>
          <Text style={sheet.title}>
            {obs.actionType === 'open-vault' ? 'Vault note' : 'Note'}
          </Text>
          <Pressable onPress={onClose} hitSlop={12} accessibilityLabel="Close">
            <Text style={sheet.close}>Done</Text>
          </Pressable>
        </View>
        {/* TODO: render actual vault note content via actionTarget */}
        <View style={sheet.body}>
          <Text style={sheet.placeholder}>
            {obs.actionTarget ?? 'No target specified.'}
          </Text>
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const sheet = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: spacing.spacing4,
    borderBottomWidth: layout.borderDefault,
    borderBottomColor: colors.bgBorder,
  },
  title: {
    ...typography.headline,
    color: colors.textPrimary,
  },
  close: {
    ...typography.callout,
    color: colors.accent,
  },
  body: {
    flex: 1,
    padding: spacing.spacing4,
  },
  placeholder: {
    ...typography.body,
    color: colors.textSecondary,
  },
});

// ─────────────────────────────────────────────────────────────────────────────
// Hook: show Polly section when active observation exists
// ─────────────────────────────────────────────────────────────────────────────

function useHasActivePollyCard(): boolean {
  const [has, setHas] = useState(() => !!getActiveObservation());
  useEffect(() => {
    const unsub = subscribeToPollyStore(() => {
      setHas(!!getActiveObservation());
    });
    return unsub;
  }, []);
  return has;
}

// ─────────────────────────────────────────────────────────────────────────────
// Today screen
// ─────────────────────────────────────────────────────────────────────────────

export default function TodayScreen() {
  const router = useRouter();
  const hasPollyCard = useHasActivePollyCard();
  const [sheetObs, setSheetObs] = useState<PollyObservation | null>(null);

  useEffect(() => {
    initPollyStore();
  }, []);

  function handleOpenSheet(obs: PollyObservation) {
    setSheetObs(obs);
  }

  function handleOpenScribe(obs: PollyObservation) {
    // Navigate to Scribe chat with pre-populated context (Q3 exception)
    // actionTarget carries the context string
    router.push({
      pathname: '/agents',
      params: { agentId: 'scribe', context: obs.actionTarget ?? '' },
    });
  }

  function handleOpenConversation(obs: PollyObservation) {
    // T4: navigate to the agent conversation where pattern was detected
    router.push({
      pathname: '/agents',
      params: { agentId: obs.actionTarget ?? '' },
    });
  }

  return (
    <SafeAreaView style={styles.root}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* ⏰ Reminders */}
        <SectionHeader emoji="⏰" label="Reminders" />
        <PlaceholderRow label="No reminders today" />

        <Divider />

        {/* ✅ Tasks */}
        <SectionHeader emoji="✅" label="Tasks" />
        <PlaceholderRow label="No active tasks" />

        <Divider />

        {/* 🔮 Polly noticed… — hidden entirely when no active card */}
        {hasPollyCard && (
          <>
            <SectionHeader emoji="🔮" label="Polly noticed…" />
            <PollyCard
              onOpenSheet={handleOpenSheet}
              onOpenScribe={handleOpenScribe}
              onOpenConversation={handleOpenConversation}
            />
            <Divider />
          </>
        )}

        {/* ⚡ Background processes */}
        <SectionHeader emoji="⚡" label="Background processes" />
        <PlaceholderRow label="No active processes" />
      </ScrollView>

      {/* Bottom sheet — vault note opens (Q3) */}
      <VaultNoteSheet obs={sheetObs} onClose={() => setSheetObs(null)} />
    </SafeAreaView>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

function SectionHeader({ emoji, label }: { emoji: string; label: string }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionEmoji} accessibilityElementsHidden>{emoji}</Text>
      <Text style={styles.sectionLabel}>{label}</Text>
    </View>
  );
}

function PlaceholderRow({ label }: { label: string }) {
  return (
    <View style={styles.placeholderRow}>
      <Text style={styles.placeholderText}>{label}</Text>
    </View>
  );
}

function Divider() {
  return <View style={styles.divider} />;
}

// ─────────────────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  scroll: {
    flex: 1,
  },
  content: {
    padding: spacing.spacing4,
    gap: spacing.spacing3,
  },
  sectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing2,
    paddingVertical: spacing.spacing2,
  },
  sectionEmoji: {
    fontSize: 16,
  },
  sectionLabel: {
    ...typography.subheadline,
    color: colors.textSecondary,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  divider: {
    height: layout.borderDefault,
    backgroundColor: colors.bgBorder,
    marginVertical: spacing.spacing2,
  },
  placeholderRow: {
    paddingVertical: spacing.spacing2,
    paddingHorizontal: spacing.spacing2,
  },
  placeholderText: {
    ...typography.body,
    color: colors.textSecondary,
  },
});

/**
 * VoiceDraftPrompt — REQ-VOICE-04
 *
 * Surface a warm, contextual prompt when a voice draft is pending recovery.
 * Appears inline in the chat input area — not a modal, not a banner.
 *
 * Copy from specs/COPY_VOICE.md:
 *   "You were recording something. Want to continue?"
 *   [Continue recording] [Discard]
 *
 * Monome principle: quiet confidence. State the situation, offer a path,
 * don't alarm. The user knows what happened — acknowledge it simply.
 *
 * Spec: specs/VOICE_INTERACTION.md (REQ-VOICE-04), specs/COPY_VOICE.md
 */

import React from 'react';
import { View, Text, Pressable, StyleSheet } from 'react-native';
import { useColors } from '../theme/colors';
import { typography, spacing, layout } from '../theme/colors';
import type { VoiceDraft } from '../hooks/useVoiceRecording';

interface VoiceDraftPromptProps {
  draft: VoiceDraft;
  onResume: () => void;
  onDiscard: () => void;
}

export function VoiceDraftPrompt({ draft, onResume, onDiscard }: VoiceDraftPromptProps) {
  const colors = useColors();

  const durationLabel = draft.durationSeconds >= 1
    ? `${Math.round(draft.durationSeconds)}s recording`
    : 'recording';

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: (colors as any).bgSecondary ?? '#0c1323',
          borderColor: (colors as any).bgBorder ?? '#1e2b48',
        },
      ]}
      accessibilityLiveRegion="polite"
    >
      <Text
        style={[
          styles.message,
          { color: (colors as any).textPrimary ?? '#f8fafc' },
        ]}
      >
        You were recording something ({durationLabel}). Want to continue?
      </Text>
      <View style={styles.actions}>
        <Pressable
          onPress={onResume}
          style={({ pressed }) => [
            styles.actionButton,
            styles.resumeButton,
            {
              backgroundColor: (colors as any).voiceActive ?? '#f0903b',
              opacity: pressed ? 0.85 : 1,
            },
          ]}
          accessibilityRole="button"
          accessibilityLabel="Continue recording"
        >
          <Text style={styles.resumeLabel}>Continue recording</Text>
        </Pressable>

        <Pressable
          onPress={onDiscard}
          style={({ pressed }) => [
            styles.actionButton,
            styles.discardButton,
            {
              borderColor: (colors as any).bgBorder ?? '#1e2b48',
              opacity: pressed ? 0.7 : 1,
            },
          ]}
          accessibilityRole="button"
          accessibilityLabel="Discard recording"
        >
          <Text
            style={[
              styles.discardLabel,
              { color: (colors as any).textSecondary ?? '#b5c1ce' },
            ]}
          >
            Discard
          </Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginHorizontal: spacing.spacing4,
    marginBottom: spacing.spacing2,
    padding: spacing.spacing3,
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    gap: spacing.spacing2,
  },
  message: {
    ...typography.callout,
  },
  actions: {
    flexDirection: 'row',
    gap: spacing.spacing2,
  },
  actionButton: {
    paddingVertical: spacing.spacing2,
    paddingHorizontal: spacing.spacing3,
    borderRadius: layout.cornerRadiusSmall,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: layout.minTouchTarget,
  },
  resumeButton: {},
  discardButton: {
    borderWidth: layout.borderDefault,
    backgroundColor: 'transparent',
  },
  resumeLabel: {
    ...typography.subheadline,
    color: '#ffffff',
  },
  discardLabel: {
    ...typography.subheadline,
  },
});

export default VoiceDraftPrompt;

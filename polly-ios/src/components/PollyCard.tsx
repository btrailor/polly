/**
 * PollyCard — "Polly noticed…" card for the Today view
 *
 * Implements the Polly card spec from AIGHT_POLLY_CARD.md.
 * Design decisions Q1–Q4 are locked — do not reopen without a design review.
 *
 * Key implementation notes:
 * - Q1: tint color uses `pollyCardBgTint` token. DO NOT hardcode purple/indigo.
 *   Token is a palette-locked placeholder until Aight dark mode palette ships.
 * - Q2: ENGAGED state renders at 0.65 opacity. Calibrated for default body font
 *   (fontSize: 17, lineHeight: 22). If font spec changes, re-validate with @design_eng.
 * - Q3: vault note opens via bottom sheet (not inline expand). "Capture with Scribe"
 *   is the one exception — it navigates to Scribe chat.
 * - Q4: queue is invisible. This component only ever sees the single active card.
 *
 * Dismissal is permanent (terminal state). Dismissed IDs are persisted in
 * AsyncStorage via pollyObservationStore — cards do not re-surface after restart.
 *
 * Spec: AIGHT_POLLY_CARD.md, AMBIENT_AGENT_SPEC.md (Dismissal State Machine)
 */

import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  Pressable,
  StyleSheet,
  Animated,
  Linking,
  LayoutAnimation,
  Platform,
  UIManager,
} from 'react-native';
import { useColors, typography, spacing, layout } from '../theme/colors';
import {
  PollyObservation,
  engageObservation,
  dismissObservation,
  getActiveObservation,
  subscribeToPollyStore,
} from '../store/pollyObservationStore';

// Enable LayoutAnimation on Android
if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// ─────────────────────────────────────────────────────────────────────────────
// Opacity constants
// Q2: 65% for ENGAGED state. Calibrated to fontSize:17 / lineHeight:22.
// If typography.body changes, re-validate this value with @design_eng.
// ─────────────────────────────────────────────────────────────────────────────
const ENGAGED_OPACITY = 0.65;
const ACTIVE_OPACITY = 1.0;

// ─────────────────────────────────────────────────────────────────────────────
// Hook: subscribe to store and return current active observation
// ─────────────────────────────────────────────────────────────────────────────
function useActiveObservation(): PollyObservation | null {
  const [obs, setObs] = useState<PollyObservation | null>(getActiveObservation);
  useEffect(() => {
    const unsub = subscribeToPollyStore(() => {
      setObs(getActiveObservation());
    });
    return unsub;
  }, []);
  return obs;
}

// ─────────────────────────────────────────────────────────────────────────────
// Action label helpers
// ─────────────────────────────────────────────────────────────────────────────
function getActionLabel(obs: PollyObservation): string | null {
  switch (obs.actionType) {
    case 'open-vault':    return 'Open in vault';
    case 'open-note':     return 'Open note';
    case 'capture-with-scribe': return 'Capture with Scribe';
    default: return null;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// First-run explanation text
// Shown inline on the very first Polly card ever surfaced. One-time, dismissible.
// ─────────────────────────────────────────────────────────────────────────────
const FIRST_RUN_KEY = 'polly:first_card_shown';
import AsyncStorage from '@react-native-async-storage/async-storage';

function FirstRunNote() {
  return (
    <Text style={styles.firstRunNote}>
      Polly surfaces connections and observations when they're genuinely useful. Cards appear rarely and on purpose.
    </Text>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────────────────────

interface PollyCardProps {
  /**
   * Called when user taps "→ open" or an action button that opens a vault note.
   * Parent should present a bottom sheet (Q3). NOT called for "Capture with Scribe"
   * which navigates away instead.
   */
  onOpenSheet?: (obs: PollyObservation) => void;
  /**
   * Called when user taps "Capture with Scribe".
   * Navigate to Scribe chat with context pre-populated.
   */
  onOpenScribe?: (obs: PollyObservation) => void;
  /**
   * Called when user taps "→ open" for a T4 constitutional flag.
   * Navigate to the relevant agent conversation.
   */
  onOpenConversation?: (obs: PollyObservation) => void;
}

export function PollyCard({ onOpenSheet, onOpenScribe, onOpenConversation }: PollyCardProps) {
  const obs = useActiveObservation();
  const colors = useColors();
  const opacity = useRef(new Animated.Value(ACTIVE_OPACITY)).current;
  const [isFirstRun, setIsFirstRun] = useState(false);

  // Animate opacity change when state transitions ACTIVE → ENGAGED
  useEffect(() => {
    if (!obs) return;
    const target = obs.state === 'engaged' ? ENGAGED_OPACITY : ACTIVE_OPACITY;
    Animated.timing(opacity, {
      toValue: target,
      duration: 200,
      useNativeDriver: true,
    }).start();
  }, [obs?.state]);

  // Reset opacity when a new card surfaces (obs.id changes)
  useEffect(() => {
    if (obs) {
      opacity.setValue(obs.state === 'engaged' ? ENGAGED_OPACITY : ACTIVE_OPACITY);
    }
  }, [obs?.id]);

  // Check first-run state
  useEffect(() => {
    if (!obs) return;
    AsyncStorage.getItem(FIRST_RUN_KEY).then((val) => {
      if (!val) {
        setIsFirstRun(true);
        AsyncStorage.setItem(FIRST_RUN_KEY, '1');
      } else {
        setIsFirstRun(false);
      }
    });
  }, [obs?.id]);

  if (!obs) return null; // Section hidden entirely when no active card (spec: empty state)

  const actionLabel = getActionLabel(obs);

  function handleDismiss() {
    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    dismissObservation(obs!.id);
  }

  function handleAction() {
    if (obs!.state === 'active') {
      engageObservation(obs!.id);
    }
    if (obs!.actionType === 'capture-with-scribe') {
      onOpenScribe?.(obs!);
    } else {
      onOpenSheet?.(obs!);
    }
  }

  function handleOpen() {
    if (obs!.state === 'active') {
      engageObservation(obs!.id);
    }
    if (obs!.triggerType === 'T4') {
      onOpenConversation?.(obs!);
    } else {
      onOpenSheet?.(obs!);
    }
  }

  return (
    <Animated.View
      style={[
        styles.card,
        {
          // Q1: pollyCardBgTint token — DO NOT replace with hardcoded purple/indigo.
          // Resolves at palette lock. See Context Note 1 in AIGHT_POLLY_CARD.md.
          backgroundColor: (colors as any).pollyCardBgTint ?? colors.bgSecondary,
          borderColor: colors.bgBorder,
          opacity,
        },
      ]}
      accessibilityRole="none"
      accessibilityLabel={`Polly noticed: ${obs.observationText}`}
    >
      {/* Header row */}
      <View style={styles.header}>
        <Text style={styles.headerEmoji} accessibilityElementsHidden>🔮</Text>
        <Text style={[styles.headerText, { color: colors.textPrimary }]}>
          Polly noticed…
        </Text>
        <Pressable
          onPress={handleDismiss}
          style={({ pressed }) => [styles.dismissButton, pressed && styles.dismissPressed]}
          accessibilityLabel="Dismiss"
          accessibilityRole="button"
          hitSlop={12}
        >
          <Text style={[styles.dismissIcon, { color: colors.textSecondary }]}>×</Text>
        </Pressable>
      </View>

      {/* Observation body — 1–2 sentences, specific, earned */}
      <Text
        style={[styles.body, { color: colors.textPrimary }]}
        numberOfLines={4}
      >
        {obs.observationText}
      </Text>

      {/* First-run inline note — one time, auto-removes after dismiss */}
      {isFirstRun && <FirstRunNote />}

      {/* Action row */}
      <View style={styles.actions}>
        {actionLabel && (
          <Pressable
            onPress={handleAction}
            style={({ pressed }) => [
              styles.actionButton,
              { backgroundColor: colors.bgBorder },
              pressed && styles.actionPressed,
            ]}
            accessibilityRole="button"
            accessibilityLabel={actionLabel}
          >
            <Text style={[styles.actionText, { color: colors.textPrimary }]}>
              {actionLabel}
            </Text>
          </Pressable>
        )}
        {/* T4 (constitutional flag) has no action button — observation only */}
        {obs.triggerType !== 'T4' && (
          <Pressable
            onPress={handleOpen}
            style={({ pressed }) => [styles.openButton, pressed && styles.actionPressed]}
            accessibilityRole="button"
            accessibilityLabel="Open"
          >
            <Text style={[styles.openText, { color: colors.textSecondary }]}>→ open</Text>
          </Pressable>
        )}
      </View>
    </Animated.View>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  card: {
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    padding: spacing.spacing4,
    gap: spacing.spacing2,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing2,
  },
  headerEmoji: {
    fontSize: 16,
    lineHeight: 20,
  },
  headerText: {
    ...typography.subheadline,
    flex: 1,
  },
  dismissButton: {
    width: layout.minTouchTarget,
    height: layout.minTouchTarget,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: -spacing.spacing2,
    marginTop: -spacing.spacing2,
  },
  dismissPressed: {
    opacity: 0.5,
  },
  dismissIcon: {
    fontSize: 22,
    lineHeight: 26,
    fontWeight: '300',
  },
  body: {
    ...typography.body,  // fontSize: 17, lineHeight: 22 — Q2 opacity calibrated to this
    paddingVertical: spacing.spacing1,
  },
  firstRunNote: {
    fontSize: typography.footnote.fontSize,
    lineHeight: typography.footnote.lineHeight,
    color: '#b5c1ce', // textSecondary — static to avoid hook in nested component
    fontStyle: 'italic',
    paddingTop: spacing.spacing1,
  },
  actions: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingTop: spacing.spacing1,
    gap: spacing.spacing2,
  },
  actionButton: {
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing2,
    borderRadius: layout.cornerRadiusSmall,
    flex: 1,
    alignItems: 'center',
  },
  actionPressed: {
    opacity: 0.6,
  },
  actionText: {
    ...typography.callout,
  },
  openButton: {
    paddingHorizontal: spacing.spacing2,
    paddingVertical: spacing.spacing2,
    minWidth: layout.minTouchTarget,
    alignItems: 'flex-end',
  },
  openText: {
    ...typography.callout,
  },
});

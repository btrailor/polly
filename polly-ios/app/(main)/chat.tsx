/**
 * ChatScreen — primary chat surface (§4.1)
 *
 * Input bar layout:
 *   [text input          ] [mic button 72×80pt]
 *
 * Voice state machine:
 *   idle → recording → processing → idle
 *              ↓ (background/interruption)
 *           draft saved → VoiceDraftPrompt on return
 *
 * Specs: VOICE_INTERACTION.md, COPY_VOICE.md, VOICE_BEHAVIOR_TESTS.md
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  TextInput,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
} from 'react-native';
import { useColors, typography, spacing, layout } from '../../src/theme/colors';
import { VoiceMicButton } from '../../src/components/VoiceMicButton';
import { VoiceDraftPrompt } from '../../src/components/VoiceDraftPrompt';
import { useVoiceRecording } from '../../src/hooks/useVoiceRecording';
import type { VoiceButtonState } from '../../src/components/VoiceMicButton';

export default function ChatScreen() {
  const colors = useColors();
  const [textInput, setTextInput] = useState('');

  // ── Voice recording ────────────────────────────────────────────────────────

  const handleTranscript = useCallback((text: string) => {
    // Transcript delivered from STT — append to input or send directly
    setTextInput(prev => prev ? `${prev} ${text}` : text);
  }, []);

  const {
    recordingState,
    waveformAmplitudes,
    pendingDraft,
    startRecording,
    stopAndSend,
    cancelRecording,
    resumeDraft,
    discardDraft,
    errorMessage,
  } = useVoiceRecording(handleTranscript);

  // Map recording state to VoiceButtonState
  const voiceButtonState: VoiceButtonState = (() => {
    switch (recordingState) {
      case 'recording':   return 'recording';
      case 'processing':  return 'processing';
      case 'error':       return 'error';
      default:            return 'resting';
    }
  })();

  const handleMicPress = useCallback(() => {
    if (recordingState === 'recording') {
      stopAndSend();
    } else if (recordingState === 'idle') {
      startRecording();
    }
    // processing/error states: button does nothing until state clears
  }, [recordingState, startRecording, stopAndSend]);

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <SafeAreaView style={[styles.root, { backgroundColor: (colors as any).bgPrimary ?? '#020617' }]}>
      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {/* Message list — scaffold placeholder */}
        <View style={styles.messageList}>
          <Text style={[styles.placeholder, { color: (colors as any).textSecondary }]}>
            Messages will render here
          </Text>
        </View>

        {/* Error message (voice errors) */}
        {errorMessage && (
          <Text style={[styles.errorText, { color: (colors as any).error }]}>
            {errorMessage}
          </Text>
        )}

        {/* Draft recovery prompt — REQ-VOICE-04 */}
        {pendingDraft && (
          <VoiceDraftPrompt
            draft={pendingDraft}
            onResume={resumeDraft}
            onDiscard={discardDraft}
          />
        )}

        {/* Recording state indicator — REQ-VOICE-03 */}
        {recordingState === 'recording' && (
          <View style={styles.recordingIndicator}>
            <View style={[styles.recordingDot, { backgroundColor: (colors as any).error }]} />
            <Text style={[styles.recordingLabel, { color: (colors as any).textSecondary }]}>
              Recording — screen will stay on
            </Text>
          </View>
        )}

        {/* Input bar */}
        <View
          style={[
            styles.inputBar,
            {
              backgroundColor: (colors as any).bgSecondary ?? '#0c1323',
              borderTopColor: (colors as any).bgBorder ?? '#1e2b48',
            },
          ]}
        >
          <TextInput
            style={[
              styles.textInput,
              {
                backgroundColor: (colors as any).bgPrimary ?? '#020617',
                color: (colors as any).textPrimary ?? '#f8fafc',
                borderColor: (colors as any).bgBorder ?? '#1e2b48',
              },
            ]}
            placeholder="Message Polly…"
            placeholderTextColor={(colors as any).textSecondary ?? '#b5c1ce'}
            value={textInput}
            onChangeText={setTextInput}
            multiline
            maxLength={4000}
            accessible
            accessibilityLabel="Message input"
          />

          {/* Mic button — right side of input bar, 72×80pt, voice as first-class input */}
          <VoiceMicButton
            state={voiceButtonState}
            waveformAmplitudes={waveformAmplitudes}
            onPress={handleMicPress}
            disabled={recordingState === 'processing'}
          />
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  root: {
    flex: 1,
  },
  flex: {
    flex: 1,
  },
  messageList: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  placeholder: {
    ...typography.body,
  },
  errorText: {
    ...typography.footnote,
    marginHorizontal: spacing.spacing4,
    marginBottom: spacing.spacing2,
    textAlign: 'center',
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.spacing2,
    paddingVertical: spacing.spacing2,
    marginHorizontal: spacing.spacing4,
    marginBottom: spacing.spacing1,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  recordingLabel: {
    ...typography.caption1,
  },
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    borderTopWidth: 0.5,
    gap: spacing.spacing2,
  },
  textInput: {
    flex: 1,
    minHeight: layout.minTouchTarget,
    maxHeight: 120,
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing2,
    ...typography.body,
  },
});

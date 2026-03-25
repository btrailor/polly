/**
 * VoiceMicButton — REQ-VOICE-01, REQ-VOICE-02, REQ-VOICE-03
 *
 * Prominent mic button for Polly's chat input bar.
 * Lives in the input layer (right side of input bar), never embedded in content.
 *
 * State machine:
 *   resting     → user can tap to start recording
 *   recording   → opaque, pulsing, waveform visible
 *   processing  → resting state, brief spinner overlay
 *   error       → warm red, shake animation, returns to resting
 *
 * Spec: specs/VOICE_INTERACTION.md, specs/COPY_VOICE.md
 */

import React, { useEffect, useRef, useCallback } from 'react';
import {
  View,
  Pressable,
  Animated,
  StyleSheet,
  AccessibilityInfo,
  Platform,
} from 'react-native';
import { useColors } from '../theme/colors';
import { layout } from '../theme/colors';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type VoiceButtonState = 'resting' | 'recording' | 'processing' | 'error';

interface WaveformBar {
  amplitude: number; // 0.0 – 1.0, driven by live audio input
}

interface VoiceMicButtonProps {
  state: VoiceButtonState;
  waveformAmplitudes?: [number, number, number]; // three bars, live amplitude
  onPress: () => void;
  disabled?: boolean;
  accessibilityLabel?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────────

export function VoiceMicButton({
  state,
  waveformAmplitudes = [0, 0, 0],
  onPress,
  disabled = false,
  accessibilityLabel = 'Record voice message',
}: VoiceMicButtonProps) {
  const colors = useColors();

  // Pulse animation (recording state)
  const pulseAnim = useRef(new Animated.Value(0)).current;
  const pulseLoop = useRef<Animated.CompositeAnimation | null>(null);

  // Spinner animation (processing state)
  const spinAnim = useRef(new Animated.Value(0)).current;
  const spinLoop = useRef<Animated.CompositeAnimation | null>(null);

  // Shake animation (error state)
  const shakeAnim = useRef(new Animated.Value(0)).current;

  // Waveform bar heights (recording state)
  const barAnims = useRef([
    new Animated.Value(0),
    new Animated.Value(0),
    new Animated.Value(0),
  ]).current;

  // ── Pulse (recording) ──────────────────────────────────────────────────────
  useEffect(() => {
    if (state === 'recording') {
      pulseLoop.current = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 0,
            duration: 600,
            useNativeDriver: true,
          }),
        ])
      );
      pulseLoop.current.start();
    } else {
      pulseLoop.current?.stop();
      pulseAnim.setValue(0);
    }
    return () => pulseLoop.current?.stop();
  }, [state]);

  // ── Spinner (processing) ───────────────────────────────────────────────────
  useEffect(() => {
    if (state === 'processing') {
      spinLoop.current = Animated.loop(
        Animated.timing(spinAnim, {
          toValue: 1,
          duration: 800,
          useNativeDriver: true,
        })
      );
      spinLoop.current.start();
    } else {
      spinLoop.current?.stop();
      spinAnim.setValue(0);
    }
    return () => spinLoop.current?.stop();
  }, [state]);

  // ── Shake (error) ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (state === 'error') {
      Animated.sequence([
        Animated.timing(shakeAnim, { toValue: 8, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: -8, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: 6, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: -6, duration: 60, useNativeDriver: true }),
        Animated.timing(shakeAnim, { toValue: 0, duration: 60, useNativeDriver: true }),
      ]).start();
    }
  }, [state]);

  // ── Waveform bars (recording, driven by amplitude props) ───────────────────
  useEffect(() => {
    if (state === 'recording') {
      waveformAmplitudes.forEach((amp, i) => {
        Animated.spring(barAnims[i], {
          toValue: amp,
          useNativeDriver: true,
          damping: 10,
          stiffness: 120,
        }).start();
      });
    } else {
      barAnims.forEach(bar => {
        Animated.timing(bar, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }).start();
      });
    }
  }, [state, waveformAmplitudes]);

  // ── Derived styles ─────────────────────────────────────────────────────────

  const isRecording = state === 'recording';
  const isError = state === 'error';
  const isProcessing = state === 'processing';

  // Voice active color — useColors() automatically picks dark/light variant
  const voiceColor = (colors as any).voiceActive ?? '#f0903b';
  const voiceWaveformDim = (colors as any).voiceWaveformDim ?? '#7a4520';
  const errorColor = (colors as any).error ?? '#ef4444';

  const buttonColor = isError ? errorColor : voiceColor;
  const buttonOpacity = isRecording || isError ? 1.0 : 0.7; // resting: semi-transparent

  const pulseScale = pulseAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [1.0, 1.12], // gentle 8pt outward pulse
  });

  const spinRotation = spinAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  const iconSize = isRecording ? 26 : 24; // icon enlarges slightly when recording

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <View style={styles.wrapper} accessibilityLabel={accessibilityLabel}>
      {/* Waveform — immediately left of button, visible during recording */}
      {isRecording && (
        <View style={styles.waveformContainer} accessibilityElementsHidden>
          {barAnims.map((barAnim, i) => {
            const scaleY = barAnim.interpolate({
              inputRange: [0, 1],
              outputRange: [0.2, 1.0],
            });
            return (
              <Animated.View
                key={i}
                style={[
                  styles.waveformBar,
                  {
                    backgroundColor: voiceColor,
                    transform: [{ scaleY }],
                  },
                ]}
              />
            );
          })}
        </View>
      )}

      {/* Mic button */}
      <Animated.View
        style={[
          styles.buttonOuter,
          {
            transform: [
              { scale: isRecording ? pulseScale : 1 },
              { translateX: shakeAnim },
            ],
          },
        ]}
      >
        <Pressable
          onPress={onPress}
          disabled={disabled}
          hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}
          accessible
          accessibilityRole="button"
          accessibilityLabel={accessibilityLabel}
          accessibilityState={{ selected: isRecording }}
          style={({ pressed }) => [
            styles.button,
            {
              backgroundColor: buttonColor,
              opacity: pressed ? 0.85 : buttonOpacity,
            },
          ]}
        >
          {/* Mic icon — SF Symbol equivalent (Unicode fallback for RN) */}
          <MicIcon size={iconSize} color="#ffffff" />

          {/* Processing spinner overlay */}
          {isProcessing && (
            <Animated.View
              style={[
                styles.spinnerOverlay,
                { transform: [{ rotate: spinRotation }] },
              ]}
            >
              <SpinnerArc color={voiceColor} />
            </Animated.View>
          )}
        </Pressable>
      </Animated.View>
    </View>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

function MicIcon({ size, color }: { size: number; color: string }) {
  // In production: use @expo/vector-icons Ionicons 'mic' or react-native-vector-icons
  // Using a Text placeholder here that signals intent; swap for real icon in native build
  const { Text } = require('react-native');
  return (
    <Text
      style={{ fontSize: size, color, lineHeight: size + 2 }}
      accessibilityElementsHidden
    >
      🎤
    </Text>
  );
}

function SpinnerArc({ color }: { color: string }) {
  // Lightweight arc for spinner overlay — thin ring, not full circle
  return (
    <View
      style={[
        styles.spinnerArc,
        { borderTopColor: color, borderRightColor: 'transparent' },
      ]}
    />
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Styles
// ─────────────────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  wrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  waveformContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 3,
    height: 28,
  },
  waveformBar: {
    width: 3,
    height: 28,
    borderRadius: 2,
  },
  buttonOuter: {
    // Animated.View wrapper for pulse + shake transforms
  },
  button: {
    width: layout.voiceTouchTargetWidth,   // 72pt
    height: layout.voiceTouchTargetHeight, // 80pt
    borderRadius: layout.cornerRadiusMedium,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  spinnerOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    alignItems: 'center',
    justifyContent: 'center',
  },
  spinnerArc: {
    width: 32,
    height: 32,
    borderRadius: 16,
    borderWidth: 2.5,
    borderColor: 'transparent',
  },
});

export default VoiceMicButton;

/**
 * Onboarding flow — Phase 1A
 * Steps: Welcome → Gateway URL → Auth Token → Testing Connection → (main/chat)
 *
 * State is persisted to MMKV via onboardingStore so the flow survives
 * crash/force-quit and resumes at the correct step.
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store';
import { Wifi, WifiOff, CheckCircle, XCircle, ArrowLeft, ArrowRight, HelpCircle } from 'lucide-react-native';

import { colors, typography, spacing, layout, semanticColors } from '../src/theme/colors';
import { useOnboardingStore } from '../src/store/onboardingStore';
import { SECURE_STORE_KEYS } from '../src/constants/secureStoreKeys';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

type Step = 'welcome' | 'gateway-url' | 'gateway-token' | 'testing-connection';

type ConnectionResult =
  | { status: 'idle' }
  | { status: 'testing' }
  | { status: 'success' }
  | { status: 'unreachable'; message: string }
  | { status: 'auth-rejected'; message: string }
  | { status: 'timeout'; message: string }
  | { status: 'unknown-error'; message: string };

// ─────────────────────────────────────────────────────────────────────────────
// URL Validation
// ─────────────────────────────────────────────────────────────────────────────

function isValidGatewayUrl(raw: string): boolean {
  if (!raw.trim()) return false;
  try {
    const url = new URL(raw.trim());
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Connection Test
// ─────────────────────────────────────────────────────────────────────────────

const CONNECT_TIMEOUT_MS = 10_000;

async function testConnection(
  gatewayUrl: string,
  authToken: string
): Promise<ConnectionResult> {
  const base = gatewayUrl.replace(/\/$/, '');
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), CONNECT_TIMEOUT_MS);

  try {
    const response = await fetch(`${base}/health`, {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authToken}`,
        Accept: 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timer);

    if (response.status === 401 || response.status === 403) {
      return {
        status: 'auth-rejected',
        message: 'Auth token rejected. Open OpenClaw → Settings → Auth Tokens to verify your token.',
      };
    }

    if (!response.ok) {
      return {
        status: 'unknown-error',
        message: `Gateway returned HTTP ${response.status}. Make sure OpenClaw is running and healthy.`,
      };
    }

    return { status: 'success' };
  } catch (err: unknown) {
    clearTimeout(timer);

    if (err instanceof Error) {
      if (err.name === 'AbortError') {
        return {
          status: 'timeout',
          message: 'Connection timed out. Is your Mac on the same network? Is OpenClaw running?',
        };
      }
      // Network-level unreachable (ECONNREFUSED, DNS failure, etc.)
      if (
        err.message.includes('Network request failed') ||
        err.message.includes('Failed to fetch') ||
        err.message.includes('ECONNREFUSED') ||
        err.message.includes('ERR_')
      ) {
        return {
          status: 'unreachable',
          message: `Can't reach gateway at ${gatewayUrl}. Is your Mac on the same Wi-Fi? Is OpenClaw running?`,
        };
      }
      return { status: 'unknown-error', message: err.message };
    }

    return { status: 'unknown-error', message: 'An unexpected error occurred.' };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// What's this? explanation
// ─────────────────────────────────────────────────────────────────────────────

function showGatewayUrlHelp() {
  Alert.alert(
    "What's an OpenClaw Gateway?",
    'OpenClaw is a free app that runs on your Mac and manages your AI agents.\n\n' +
      "It serves as Polly's backend — your conversations go to your Mac, not to any cloud. " +
      'You own your data.\n\n' +
      'To get started:\n' +
      '1. Download OpenClaw at openclaw.app\n' +
      '2. Install and start it on your Mac\n' +
      '3. Find the gateway URL in OpenClaw → Settings → Network\n' +
      '   (Usually something like http://192.168.1.x:18789)',
    [{ text: 'Got it' }]
  );
}

function showAuthTokenHelp() {
  Alert.alert(
    'Where to find your Auth Token',
    'Open OpenClaw on your Mac, then go to:\n\n' +
      'Settings → Auth Tokens → Create New Token\n\n' +
      'Copy the token and paste it here. This token lets Polly authenticate with your gateway.',
    [{ text: 'Got it' }]
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Sub-screens
// ─────────────────────────────────────────────────────────────────────────────

function WelcomeStep({ onNext }: { onNext: () => void }) {
  return (
    <View style={styles.stepContainer}>
      <View style={styles.logoArea}>
        {/* Logo placeholder — no image asset needed for Phase 1A */}
        <View style={styles.logoCircle}>
          <Wifi size={44} color={colors.accent} />
        </View>
        <Text style={styles.logoName}>Polly</Text>
        <Text style={styles.tagline}>Your AI team, in your pocket.</Text>
      </View>

      <Text style={styles.welcomeBody}>
        Connect to your OpenClaw gateway and chat with your agents from anywhere.
      </Text>

      <TouchableOpacity style={styles.primaryButton} onPress={onNext} activeOpacity={0.8}>
        <Text style={styles.primaryButtonText}>Get Started</Text>
        <ArrowRight size={18} color="#ffffff" style={{ marginLeft: spacing.spacing2 }} />
      </TouchableOpacity>
    </View>
  );
}

function GatewayUrlStep({
  value,
  onChange,
  onNext,
  onBack,
}: {
  value: string;
  onChange: (v: string) => void;
  onNext: () => void;
  onBack: () => void;
}) {
  const valid = isValidGatewayUrl(value);
  const showError = value.length > 0 && !valid;

  return (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Gateway URL</Text>
      <Text style={styles.stepSubtitle}>
        Enter the URL of your OpenClaw gateway.
      </Text>

      <View style={styles.fieldGroup}>
        <Text style={styles.fieldLabel}>OpenClaw Gateway URL</Text>
        <TextInput
          style={[styles.textInput, showError && styles.textInputError]}
          value={value}
          onChangeText={onChange}
          placeholder="http://192.168.1.x:18789"
          placeholderTextColor={semanticColors.inputPlaceholder}
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="url"
          textContentType="URL"
          returnKeyType="done"
          onSubmitEditing={() => valid && onNext()}
        />
        {showError && (
          <Text style={styles.fieldError}>Enter a valid URL (http:// or https://)</Text>
        )}
      </View>

      <TouchableOpacity style={styles.helpRow} onPress={showGatewayUrlHelp} activeOpacity={0.7}>
        <HelpCircle size={15} color={colors.accent} />
        <Text style={styles.helpText}>What's this?</Text>
      </TouchableOpacity>

      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.secondaryButton} onPress={onBack} activeOpacity={0.8}>
          <ArrowLeft size={16} color={colors.textPrimary} />
          <Text style={styles.secondaryButtonText}>Back</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.primaryButton, styles.primaryButtonFlex, !valid && styles.primaryButtonDisabled]}
          onPress={onNext}
          disabled={!valid}
          activeOpacity={0.8}
        >
          <Text style={styles.primaryButtonText}>Continue</Text>
          <ArrowRight size={16} color="#ffffff" style={{ marginLeft: spacing.spacing2 }} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

function AuthTokenStep({
  value,
  onChange,
  onTest,
  onBack,
}: {
  value: string;
  onChange: (v: string) => void;
  onTest: () => void;
  onBack: () => void;
}) {
  const hasValue = value.trim().length > 0;

  return (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Auth Token</Text>
      <Text style={styles.stepSubtitle}>
        Enter the auth token from your OpenClaw gateway.
      </Text>

      <View style={styles.fieldGroup}>
        <Text style={styles.fieldLabel}>Auth Token</Text>
        <TextInput
          style={styles.textInput}
          value={value}
          onChangeText={onChange}
          placeholder="Paste your token here"
          placeholderTextColor={semanticColors.inputPlaceholder}
          secureTextEntry
          autoCapitalize="none"
          autoCorrect={false}
          textContentType="password"
          returnKeyType="done"
          onSubmitEditing={() => hasValue && onTest()}
        />
        <View style={styles.inlineTip}>
          <Text style={styles.inlineTipText}>
            💡 Find your token in OpenClaw → Settings → Auth Tokens
          </Text>
        </View>
      </View>

      <TouchableOpacity style={styles.helpRow} onPress={showAuthTokenHelp} activeOpacity={0.7}>
        <HelpCircle size={15} color={colors.accent} />
        <Text style={styles.helpText}>Where do I find this?</Text>
      </TouchableOpacity>

      <View style={styles.buttonRow}>
        <TouchableOpacity style={styles.secondaryButton} onPress={onBack} activeOpacity={0.8}>
          <ArrowLeft size={16} color={colors.textPrimary} />
          <Text style={styles.secondaryButtonText}>Back</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.primaryButton, styles.primaryButtonFlex, !hasValue && styles.primaryButtonDisabled]}
          onPress={onTest}
          disabled={!hasValue}
          activeOpacity={0.8}
        >
          <Text style={styles.primaryButtonText}>Test Connection</Text>
          <Wifi size={16} color="#ffffff" style={{ marginLeft: spacing.spacing2 }} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

function TestingConnectionStep({
  result,
  onRetry,
  onBack,
}: {
  result: ConnectionResult;
  onRetry: () => void;
  onBack: () => void;
}) {
  const isTesting = result.status === 'idle' || result.status === 'testing';
  const isSuccess = result.status === 'success';
  const isFailure = result.status === 'unreachable' || result.status === 'auth-rejected' || result.status === 'timeout' || result.status === 'unknown-error';
  const failureMessage = isFailure ? (result as { status: string; message: string }).message : null;

  return (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>Testing Connection</Text>

      <View style={styles.testingCenter}>
        {isTesting && (
          <>
            <ActivityIndicator size="large" color={colors.accent} />
            <Text style={styles.testingStatus}>Connecting to your gateway…</Text>
          </>
        )}

        {isSuccess && (
          <>
            <CheckCircle size={56} color={colors.success} />
            <Text style={[styles.testingStatus, { color: colors.success }]}>Connected!</Text>
            <Text style={styles.testingSubstatus}>
              Successfully connected to your OpenClaw gateway.
            </Text>
          </>
        )}

        {isFailure && failureMessage && (
          <>
            {result.status === 'unreachable' && (
              <WifiOff size={56} color={colors.error} />
            )}
            {result.status !== 'unreachable' && (
              <XCircle size={56} color={colors.error} />
            )}
            <Text style={[styles.testingStatus, { color: colors.error }]}>
              {result.status === 'timeout' && 'Connection timed out'}
              {result.status === 'auth-rejected' && 'Auth rejected'}
              {result.status === 'unreachable' && 'Gateway unreachable'}
              {result.status === 'unknown-error' && 'Connection failed'}
            </Text>
            <Text style={styles.testingSubstatus}>{failureMessage}</Text>
          </>
        )}
      </View>

      {isFailure && (
        <View style={styles.buttonRow}>
          <TouchableOpacity style={styles.secondaryButton} onPress={onBack} activeOpacity={0.8}>
            <ArrowLeft size={16} color={colors.textPrimary} />
            <Text style={styles.secondaryButtonText}>Back</Text>
          </TouchableOpacity>

          <TouchableOpacity style={[styles.primaryButton, styles.primaryButtonFlex]} onPress={onRetry} activeOpacity={0.8}>
            <Text style={styles.primaryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Progress indicator
// ─────────────────────────────────────────────────────────────────────────────

const STEPS_ORDER: Step[] = ['welcome', 'gateway-url', 'gateway-token', 'testing-connection'];

function ProgressDots({ current }: { current: Step }) {
  const idx = STEPS_ORDER.indexOf(current);
  return (
    <View style={styles.progressDots}>
      {STEPS_ORDER.map((_, i) => (
        <View
          key={i}
          style={[styles.dot, i === idx && styles.dotActive, i < idx && styles.dotDone]}
        />
      ))}
    </View>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main export
// ─────────────────────────────────────────────────────────────────────────────

export default function OnboardingScreen() {
  const router = useRouter();
  const { setGatewayUrl, setPhase, markComplete } = useOnboardingStore();

  const [step, setStep] = useState<Step>('welcome');
  const [gatewayUrlInput, setGatewayUrlInput] = useState('');
  const [authTokenInput, setAuthTokenInput] = useState('');
  const [connectionResult, setConnectionResult] = useState<ConnectionResult>({ status: 'idle' });

  const goTo = useCallback((s: Step) => {
    setStep(s);
    setPhase(s);
  }, [setPhase]);

  const handleTestConnection = useCallback(async () => {
    goTo('testing-connection');
    setConnectionResult({ status: 'testing' });

    const result = await testConnection(gatewayUrlInput.trim(), authTokenInput.trim());
    setConnectionResult(result);

    if (result.status === 'success') {
      // Persist gateway URL (non-sensitive) to store
      setGatewayUrl(gatewayUrlInput.trim());
      // Persist auth token to secure store
      try {
        await SecureStore.setItemAsync(SECURE_STORE_KEYS.GATEWAY_TOKEN, authTokenInput.trim());
      } catch (err) {
        console.warn('[onboarding] Failed to save token to secure store:', err);
      }
      // Mark complete
      markComplete();
      // Navigate to main chat
      router.replace('/(main)/chat');
    }
  }, [gatewayUrlInput, authTokenInput, goTo, setGatewayUrl, markComplete, router]);

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {step !== 'welcome' && <ProgressDots current={step} />}

        {step === 'welcome' && (
          <WelcomeStep onNext={() => goTo('gateway-url')} />
        )}

        {step === 'gateway-url' && (
          <GatewayUrlStep
            value={gatewayUrlInput}
            onChange={setGatewayUrlInput}
            onNext={() => goTo('gateway-token')}
            onBack={() => goTo('welcome')}
          />
        )}

        {step === 'gateway-token' && (
          <AuthTokenStep
            value={authTokenInput}
            onChange={setAuthTokenInput}
            onTest={handleTestConnection}
            onBack={() => goTo('gateway-url')}
          />
        )}

        {step === 'testing-connection' && (
          <TestingConnectionStep
            result={connectionResult}
            onRetry={handleTestConnection}
            onBack={() => goTo('gateway-token')}
          />
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
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
    flexGrow: 1,
    paddingHorizontal: spacing.spacing6,
    paddingTop: 64,
    paddingBottom: spacing.spacing8,
  },

  // Steps
  stepContainer: {
    flex: 1,
    paddingTop: spacing.spacing4,
  },

  // Welcome
  logoArea: {
    alignItems: 'center',
    marginBottom: spacing.spacing8,
  },
  logoCircle: {
    width: 88,
    height: 88,
    borderRadius: layout.cornerRadiusLarge,
    backgroundColor: colors.bgSecondary,
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.spacing4,
  },
  logoName: {
    ...typography.largeTitle,
    color: colors.textPrimary,
    marginBottom: spacing.spacing2,
  },
  tagline: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  welcomeBody: {
    ...typography.callout,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.spacing8,
    lineHeight: 24,
  },

  // Step headings
  stepTitle: {
    ...typography.title1,
    color: colors.textPrimary,
    marginBottom: spacing.spacing2,
  },
  stepSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.spacing6,
  },

  // Field
  fieldGroup: {
    marginBottom: spacing.spacing4,
  },
  fieldLabel: {
    ...typography.subheadline,
    color: colors.textPrimary,
    marginBottom: spacing.spacing2,
  },
  textInput: {
    backgroundColor: semanticColors.inputBackground,
    borderWidth: layout.borderDefault,
    borderColor: semanticColors.inputBorder,
    borderRadius: layout.cornerRadiusMedium,
    color: semanticColors.inputText,
    ...typography.body,
    paddingHorizontal: spacing.spacing4,
    paddingVertical: 14,
    minHeight: layout.minTouchTarget,
  },
  textInputError: {
    borderColor: colors.error,
  },
  fieldError: {
    ...typography.footnote,
    color: colors.error,
    marginTop: spacing.spacing2,
  },
  inlineTip: {
    marginTop: spacing.spacing2,
    backgroundColor: colors.bgSecondary,
    borderRadius: layout.cornerRadiusSmall,
    padding: spacing.spacing3,
  },
  inlineTipText: {
    ...typography.footnote,
    color: colors.textSecondary,
  },

  // Help link
  helpRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing.spacing6,
    gap: spacing.spacing2,
  },
  helpText: {
    ...typography.footnote,
    color: colors.accent,
  },

  // Buttons
  primaryButton: {
    backgroundColor: colors.accent,
    borderRadius: layout.cornerRadiusMedium,
    paddingVertical: 14,
    paddingHorizontal: spacing.spacing6,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: layout.minTouchTarget,
  },
  primaryButtonFlex: {
    flex: 1,
  },
  primaryButtonDisabled: {
    backgroundColor: colors.accentDim,
    opacity: 0.5,
  },
  primaryButtonText: {
    ...typography.headline,
    color: '#ffffff',
  },
  secondaryButton: {
    backgroundColor: semanticColors.buttonSecondary,
    borderRadius: layout.cornerRadiusMedium,
    paddingVertical: 14,
    paddingHorizontal: spacing.spacing4,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.spacing2,
    minHeight: layout.minTouchTarget,
    marginRight: spacing.spacing3,
  },
  secondaryButtonText: {
    ...typography.headline,
    color: colors.textPrimary,
  },
  buttonRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.spacing4,
  },

  // Testing connection
  testingCenter: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.spacing8,
    gap: spacing.spacing4,
  },
  testingStatus: {
    ...typography.title3,
    color: colors.textPrimary,
    textAlign: 'center',
  },
  testingSubstatus: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    paddingHorizontal: spacing.spacing4,
  },

  // Progress dots
  progressDots: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: spacing.spacing2,
    marginBottom: spacing.spacing6,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.bgBorder,
  },
  dotActive: {
    backgroundColor: colors.accent,
    width: 20,
  },
  dotDone: {
    backgroundColor: colors.accentDim,
  },
});

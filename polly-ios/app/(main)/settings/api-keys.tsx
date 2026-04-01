/**
 * Settings → API Keys screen
 * Phase 1A: Brave Search + ElevenLabs API key entry.
 * Keys stored on gateway via config.patch — never in app storage.
 */

import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  Linking,
  ActivityIndicator,
} from 'react-native';
import { Search, Mic, ExternalLink, Check } from 'lucide-react-native';
import { colors, spacing, layout, typography } from '../../../src/theme/colors';
import { gatewayClient } from '../../../src/gateway/GatewayClient';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function useSaveKey(configKey: string) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const savedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const save = async (value: string) => {
    if (!value.trim()) return;
    setSaving(true);
    setError(null);
    try {
      gatewayClient.configPatch({ [configKey]: value.trim() });
      setSaved(true);
      if (savedTimer.current) clearTimeout(savedTimer.current);
      savedTimer.current = setTimeout(() => setSaved(false), 2000);
    } catch (err) {
      setError('Not connected to gateway. Connect first in Your Gateway settings.');
    } finally {
      setSaving(false);
    }
  };

  return { save, saving, saved, error };
}

// ─── ApiKeyRow ────────────────────────────────────────────────────────────────

interface ApiKeyRowProps {
  label: string;
  subtitle: string;
  icon: React.ReactNode;
  configKey: string;
  getKeyUrl: string;
  phase2?: boolean;
}

function ApiKeyRow({
  label,
  subtitle,
  icon,
  configKey,
  getKeyUrl,
  phase2 = false,
}: ApiKeyRowProps) {
  const [value, setValue] = useState('');
  const { save, saving, saved, error } = useSaveKey(configKey);

  return (
    <View style={styles.keyCard}>
      {/* Label row */}
      <View style={styles.labelRow}>
        <View style={styles.labelIcon}>{icon}</View>
        <View style={styles.labelTextContainer}>
          <View style={styles.labelTitleRow}>
            <Text style={styles.keyLabel}>{label}</Text>
            {phase2 && (
              <View style={styles.phase2Badge}>
                <Text style={styles.phase2BadgeText}>Phase 2</Text>
              </View>
            )}
          </View>
          <Text style={styles.keySubtitle}>{subtitle}</Text>
        </View>
      </View>

      {/* Input */}
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={setValue}
        placeholder="Enter API key..."
        placeholderTextColor={colors.textSecondary}
        secureTextEntry
        autoCapitalize="none"
        autoCorrect={false}
        spellCheck={false}
      />

      {/* Error message */}
      {error && <Text style={styles.errorText}>{error}</Text>}

      {/* Actions row */}
      <View style={styles.actionsRow}>
        <TouchableOpacity
          style={styles.getLinkButton}
          onPress={() => Linking.openURL(getKeyUrl)}
          activeOpacity={0.7}
        >
          <ExternalLink size={13} color={colors.accent} />
          <Text style={styles.getLinkText}>Get API key</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.saveButton, (!value.trim() || saving) && styles.saveButtonDisabled]}
          onPress={() => save(value)}
          disabled={!value.trim() || saving}
          activeOpacity={0.7}
        >
          {saving ? (
            <ActivityIndicator size="small" color={colors.bgPrimary} />
          ) : saved ? (
            <>
              <Check size={14} color={colors.bgPrimary} />
              <Text style={styles.saveButtonText}>Saved</Text>
            </>
          ) : (
            <Text style={styles.saveButtonText}>Save</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

// ─── ApiKeysScreen ────────────────────────────────────────────────────────────

export default function ApiKeysScreen() {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>API Keys</Text>
        <Text style={styles.headerSubtitle}>
          Keys are stored on your gateway — never in the app.
        </Text>
      </View>

      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <ApiKeyRow
          label="Brave Search API Key"
          subtitle="Enables web search for your agents"
          icon={<Search size={18} color={colors.accent} />}
          configKey="polly.integrations.braveSearch.apiKey"
          getKeyUrl="https://api.search.brave.com/"
        />

        <ApiKeyRow
          label="ElevenLabs API Key"
          subtitle="Voice synthesis — activates in Phase 2 voice upgrade"
          icon={<Mic size={18} color={colors.signals} />}
          configKey="polly.integrations.elevenlabs.apiKey"
          getKeyUrl="https://elevenlabs.io/app/settings/api-keys"
          phase2
        />
      </ScrollView>
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

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
  headerSubtitle: {
    ...typography.footnote,
    color: colors.textSecondary,
    marginTop: 4,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    padding: spacing.spacing4,
    gap: spacing.spacing4,
  },
  keyCard: {
    backgroundColor: colors.bgSecondary,
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    padding: spacing.spacing4,
    gap: spacing.spacing3,
  },
  labelRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: spacing.spacing3,
  },
  labelIcon: {
    width: 36,
    height: 36,
    borderRadius: layout.cornerRadiusSmall,
    backgroundColor: colors.bgBorder,
    alignItems: 'center',
    justifyContent: 'center',
  },
  labelTextContainer: {
    flex: 1,
  },
  labelTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing2,
    flexWrap: 'wrap',
  },
  keyLabel: {
    ...typography.subheadline,
    color: colors.textPrimary,
  },
  phase2Badge: {
    backgroundColor: colors.bgBorder,
    borderRadius: layout.cornerRadiusSmall,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  phase2BadgeText: {
    ...typography.caption2,
    color: colors.textSecondary,
  },
  keySubtitle: {
    ...typography.footnote,
    color: colors.textSecondary,
    marginTop: 2,
  },
  input: {
    backgroundColor: colors.bgPrimary,
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    borderRadius: layout.cornerRadiusSmall,
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing2 + 2,
    color: colors.textPrimary,
    ...typography.callout,
  },
  errorText: {
    ...typography.footnote,
    color: colors.error,
  },
  actionsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  getLinkButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  getLinkText: {
    ...typography.footnote,
    color: colors.accent,
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: colors.accent,
    borderRadius: layout.cornerRadiusSmall,
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing2,
    minWidth: 72,
    justifyContent: 'center',
  },
  saveButtonDisabled: {
    backgroundColor: colors.accentDim,
    opacity: 0.5,
  },
  saveButtonText: {
    ...typography.subheadline,
    color: '#ffffff',
  },
});

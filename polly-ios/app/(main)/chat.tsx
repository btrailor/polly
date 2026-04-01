/**
 * ChatScreen — primary chat surface (§4.1)
 *
 * Message list: FlashList (inverted), streaming deltas via PollyGatewayAdapter,
 * markdown rendering, thinking panels, date separators, empty-state chips.
 *
 * Input bar: mic/send toggle, stop button, haptics, keyboard handling.
 * Header: agent name/avatar, model pill, drawer stub.
 *
 * Connection: PollyGatewayAdapter, disconnected banner with retry.
 *
 * Specs: POLLY_IOS_SPEC.md §4.1, VOICE_INTERACTION.md, COPY_VOICE.md
 */

import React, {
  useState,
  useCallback,
  useEffect,
  useRef,
  useMemo,
} from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  SafeAreaView,
  TouchableOpacity,
  Pressable,
  Alert,
  Clipboard,
  ActivityIndicator,
} from 'react-native';
import { FlashList } from '@shopify/flash-list';
import * as Haptics from 'expo-haptics';
import {
  Mic,
  SendHorizontal,
  Square,
  Menu,
  ChevronDown,
  AlertCircle,
  RefreshCw,
} from 'lucide-react-native';
import Markdown from 'react-native-markdown-display';

import {
  colors,
  semanticColors,
  typography,
  spacing,
  layout,
} from '../../src/theme/colors';
import { VoiceMicButton } from '../../src/components/VoiceMicButton';
import { VoiceDraftPrompt } from '../../src/components/VoiceDraftPrompt';
import { useVoiceRecording } from '../../src/hooks/useVoiceRecording';
import type { VoiceButtonState } from '../../src/components/VoiceMicButton';
import { PollyGatewayAdapter } from '../../src/gateway/PollyGatewayAdapter';
import { useChatStore } from '../../src/store/chatStore';
import { useConnectionStore } from '../../src/store/connectionStore';
import type { UIMessage } from 'expo-openclaw-chat';

// ─── Types ────────────────────────────────────────────────────────────────────

type ListItem =
  | { kind: 'message'; message: UIMessage }
  | { kind: 'date'; label: string }
  | { kind: 'typing' };

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDateLabel(timestamp: number): string {
  const d = new Date(timestamp);
  const now = new Date();
  const isToday =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate();
  const isYesterday = (() => {
    const y = new Date(now);
    y.setDate(y.getDate() - 1);
    return (
      d.getFullYear() === y.getFullYear() &&
      d.getMonth() === y.getMonth() &&
      d.getDate() === y.getDate()
    );
  })();

  if (isToday) return 'Today';
  if (isYesterday) return 'Yesterday';
  return d.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: now.getFullYear() !== d.getFullYear() ? 'numeric' : undefined,
  });
}

function getTextFromMessage(msg: UIMessage): string {
  return msg.content
    .filter((c) => c.type === 'text')
    .map((c) => (c as { type: 'text'; text: string }).text)
    .join('');
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((w) => w[0] ?? '')
    .slice(0, 2)
    .join('')
    .toUpperCase();
}

function buildListItems(
  messages: UIMessage[],
  isStreaming: boolean
): ListItem[] {
  const items: ListItem[] = [];
  let lastDateLabel = '';

  for (const msg of messages) {
    const ts = msg.timestamp ?? 0;
    const label = ts ? formatDateLabel(ts) : '';
    if (label && label !== lastDateLabel) {
      items.push({ kind: 'date', label });
      lastDateLabel = label;
    }
    items.push({ kind: 'message', message: msg });
  }

  if (isStreaming) {
    items.push({ kind: 'typing' });
  }

  // FlashList is inverted — reverse so newest is at bottom
  return items.reverse();
}

// ─── Sub-components ───────────────────────────────────────────────────────────

const SUGGESTION_CHIPS = [
  'What can you help me with?',
  'Show me what you can do',
  "Let's think through something together",
];

function EmptyState({ onChipPress }: { onChipPress: (text: string) => void }) {
  return (
    <View style={emptyStyles.container}>
      <Text style={emptyStyles.headline}>How can I help?</Text>
      {SUGGESTION_CHIPS.map((chip) => (
        <TouchableOpacity
          key={chip}
          style={emptyStyles.chip}
          onPress={() => onChipPress(chip)}
          activeOpacity={0.7}
        >
          <Text style={emptyStyles.chipText}>{chip}</Text>
        </TouchableOpacity>
      ))}
    </View>
  );
}

const emptyStyles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.spacing6,
    gap: spacing.spacing3,
    // FlashList is inverted so we need to flip the empty view
    transform: [{ scaleY: -1 }],
  },
  headline: {
    ...typography.title3,
    color: colors.textSecondary,
    marginBottom: spacing.spacing2,
    textAlign: 'center',
  },
  chip: {
    backgroundColor: colors.bgSecondary,
    borderColor: colors.bgBorder,
    borderWidth: layout.borderDefault,
    borderRadius: layout.cornerRadiusRounded,
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing2,
  },
  chipText: {
    ...typography.callout,
    color: colors.textPrimary,
  },
});

function TypingIndicator() {
  return (
    <View style={typingStyles.container}>
      <View style={typingStyles.bubble}>
        <ActivityIndicator size="small" color={colors.textSecondary} />
      </View>
    </View>
  );
}

const typingStyles = StyleSheet.create({
  container: {
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing2,
    alignItems: 'flex-start',
  },
  bubble: {
    backgroundColor: semanticColors.bubbleAssistant,
    borderRadius: layout.cornerRadiusMedium,
    padding: spacing.spacing3,
    minWidth: 60,
    alignItems: 'center',
  },
});

function DateSeparator({ label }: { label: string }) {
  return (
    <View style={separatorStyles.container}>
      <View style={separatorStyles.line} />
      <Text style={separatorStyles.label}>{label}</Text>
      <View style={separatorStyles.line} />
    </View>
  );
}

const separatorStyles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    gap: spacing.spacing3,
  },
  line: {
    flex: 1,
    height: layout.borderThin,
    backgroundColor: colors.bgBorder,
  },
  label: {
    ...typography.caption1,
    color: colors.textSecondary,
  },
});

interface ThinkingPanelProps {
  text: string;
}
function ThinkingPanel({ text }: ThinkingPanelProps) {
  const [expanded, setExpanded] = useState(false);
  return (
    <TouchableOpacity
      onPress={() => setExpanded((e) => !e)}
      activeOpacity={0.8}
      style={thinkingStyles.container}
    >
      <View style={thinkingStyles.header}>
        <Text style={thinkingStyles.label}>Thinking</Text>
        <ChevronDown
          size={14}
          color={colors.textSecondary}
          style={expanded ? thinkingStyles.rotated : undefined}
        />
      </View>
      {expanded && <Text style={thinkingStyles.body}>{text}</Text>}
    </TouchableOpacity>
  );
}

const thinkingStyles = StyleSheet.create({
  container: {
    backgroundColor: colors.bgSecondary,
    borderColor: colors.bgBorder,
    borderWidth: layout.borderDefault,
    borderRadius: layout.cornerRadiusMedium,
    padding: spacing.spacing3,
    marginBottom: spacing.spacing2,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing1,
  },
  label: {
    ...typography.caption1,
    color: colors.textSecondary,
    flex: 1,
  },
  rotated: {
    transform: [{ rotate: '180deg' }],
  },
  body: {
    ...typography.footnote,
    color: colors.textSecondary,
    marginTop: spacing.spacing2,
  },
});

interface MessageBubbleProps {
  message: UIMessage;
  agentName: string;
  onRegenerate?: (msg: UIMessage) => void;
}

function MessageBubble({ message, agentName, onRegenerate }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  const bodyText = getTextFromMessage(message);
  const thinkingBlocks = message.content.filter(
    (c) => c.type === 'thinking'
  ) as { type: 'thinking'; thinking: string }[];

  const handleLongPress = useCallback(() => {
    Alert.alert(
      'Message',
      undefined,
      [
        {
          text: 'Copy',
          onPress: () => Clipboard.setString(bodyText),
        },
        ...(isUser
          ? []
          : [
              {
                text: 'Regenerate',
                onPress: () => onRegenerate?.(message),
              },
            ]),
        { text: 'Cancel', style: 'cancel' as const },
      ],
      { cancelable: true }
    );
  }, [bodyText, isUser, message, onRegenerate]);

  return (
    <Pressable
      onLongPress={handleLongPress}
      delayLongPress={400}
      style={bubbleStyles.wrapper}
    >
      {/* Date separators are rendered as list items; this is purely the bubble */}
      {!isUser && (
        <Text style={bubbleStyles.agentName}>{agentName}</Text>
      )}

      {/* Thinking panels */}
      {!isUser && thinkingBlocks.map((b, i) => (
        <ThinkingPanel key={i} text={b.thinking} />
      ))}

      {message.isError ? (
        <View style={[bubbleStyles.bubble, bubbleStyles.errorBubble]}>
          <AlertCircle size={16} color={colors.error} />
          <Text style={bubbleStyles.errorText}>
            {message.errorMessage ?? 'Something went wrong. Try again.'}
          </Text>
        </View>
      ) : (
        <View
          style={[
            bubbleStyles.bubble,
            isUser ? bubbleStyles.userBubble : bubbleStyles.assistantBubble,
          ]}
        >
          {isUser ? (
            <Text style={bubbleStyles.userText}>{bodyText}</Text>
          ) : (
            <Markdown style={markdownStyles}>{bodyText}</Markdown>
          )}
        </View>
      )}
    </Pressable>
  );
}

const bubbleStyles = StyleSheet.create({
  wrapper: {
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing2,
    maxWidth: '80%',
  },
  agentName: {
    ...typography.caption1,
    color: colors.textSecondary,
    marginBottom: spacing.spacing1,
  },
  bubble: {
    borderRadius: layout.cornerRadiusMedium,
    padding: spacing.spacing3,
  },
  userBubble: {
    backgroundColor: semanticColors.bubbleUser,
    alignSelf: 'flex-end',
  },
  assistantBubble: {
    backgroundColor: semanticColors.bubbleAssistant,
    alignSelf: 'flex-start',
  },
  errorBubble: {
    backgroundColor: colors.bgSecondary,
    borderColor: colors.error,
    borderWidth: layout.borderDefault,
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing2,
    alignSelf: 'flex-start',
  },
  userText: {
    ...typography.body,
    color: '#ffffff',
  },
  errorText: {
    ...typography.footnote,
    color: colors.error,
    flex: 1,
  },
});

const markdownStyles = {
  body: {
    ...typography.body,
    color: colors.textPrimary,
  },
  code_inline: {
    backgroundColor: colors.bgPrimary,
    color: colors.accent,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 14,
  },
  fence: {
    backgroundColor: colors.bgPrimary,
    borderRadius: layout.cornerRadiusSmall,
    padding: spacing.spacing3,
  },
  code_block: {
    backgroundColor: colors.bgPrimary,
    borderRadius: layout.cornerRadiusSmall,
    padding: spacing.spacing3,
    fontFamily: Platform.OS === 'ios' ? 'Menlo' : 'monospace',
    fontSize: 13,
    color: colors.textPrimary,
  },
};

// ─── ChatScreen ───────────────────────────────────────────────────────────────

export default function ChatScreen() {
  const [textInput, setTextInput] = useState('');
  const listRef = useRef<FlashList<ListItem>>(null);
  const adapterRef = useRef<PollyGatewayAdapter | null>(null);
  const [adapterReady, setAdapterReady] = useState(false);

  // Stores
  const {
    messages,
    isStreaming,
    activeAgentId,
    sessionKey,
    setMessages,
    setStreaming,
    setDraft,
  } = useChatStore();
  const connectionStatus = useConnectionStore((s) => s.status);
  const connectionError = useConnectionStore((s) => s.lastError);

  // Unread / scroll-to-bottom state
  const [isAtBottom, setIsAtBottom] = useState(true);
  const [unreadCount, setUnreadCount] = useState(0);

  // ── Adapter lifecycle ──────────────────────────────────────────────────────

  useEffect(() => {
    let mounted = true;

    // Restore draft
    const storedDraft = useChatStore.getState().getDraft(sessionKey);
    if (storedDraft) setTextInput(storedDraft);

    PollyGatewayAdapter.create(activeAgentId)
      .then(async (adapter) => {
        if (!mounted) {
          adapter.destroy();
          return;
        }
        adapterRef.current = adapter;
        setAdapterReady(true);

        // Load history on mount
        const history = await adapter.loadHistory();
        if (mounted && history.length > 0) {
          useChatStore.getState().setMessages(history);
        }

        // Subscribe to engine updates
        adapter.on('update', () => {
          if (!mounted) return;
          const engineMessages = adapter.messages;
          useChatStore.getState().setMessages(engineMessages);
          useChatStore.getState().setStreaming(adapter.isStreaming);

          if (!isAtBottom) {
            setUnreadCount((n) => n + 1);
          }
        });

        adapter.on('error', (_err: unknown) => {
          if (!mounted) return;
          useChatStore.getState().setStreaming(false);
        });
      })
      .catch((err) => {
        console.error('[ChatScreen] Adapter init failed:', err);
      });

    return () => {
      mounted = false;
      adapterRef.current?.destroy();
      adapterRef.current = null;
      setAdapterReady(false);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeAgentId]);

  // Save draft on text change
  useEffect(() => {
    setDraft(sessionKey, textInput);
  }, [textInput, sessionKey, setDraft]);

  // ── Send ───────────────────────────────────────────────────────────────────

  const handleSend = useCallback(async () => {
    const adapter = adapterRef.current;
    if (!adapter || !textInput.trim() || connectionStatus !== 'connected') return;

    await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const text = textInput.trim();
    setTextInput('');
    useChatStore.getState().clearDraft(sessionKey);

    try {
      await adapter.send(text);
    } catch (err) {
      console.error('[ChatScreen] Send failed:', err);
    }
  }, [textInput, connectionStatus, sessionKey]);

  const handleStop = useCallback(() => {
    adapterRef.current?.abort();
  }, []);

  const handleRetryConnection = useCallback(() => {
    // Re-trigger adapter creation by toggling — simpler: just re-mount
    setAdapterReady(false);
    adapterRef.current?.destroy();
    adapterRef.current = null;
    PollyGatewayAdapter.create(activeAgentId)
      .then((adapter) => {
        adapterRef.current = adapter;
        setAdapterReady(true);
      })
      .catch(console.error);
  }, [activeAgentId]);

  // ── Voice recording ────────────────────────────────────────────────────────

  const handleTranscript = useCallback((text: string) => {
    setTextInput((prev) => (prev ? `${prev} ${text}` : text));
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
    errorMessage: voiceError,
  } = useVoiceRecording(handleTranscript);

  const voiceButtonState: VoiceButtonState = (() => {
    switch (recordingState) {
      case 'recording':  return 'recording';
      case 'processing': return 'processing';
      case 'error':      return 'error';
      default:           return 'resting';
    }
  })();

  const handleMicPress = useCallback(() => {
    if (recordingState === 'recording') stopAndSend();
    else if (recordingState === 'idle') startRecording();
  }, [recordingState, startRecording, stopAndSend]);

  // ── List data ──────────────────────────────────────────────────────────────

  const listItems = useMemo(
    () => buildListItems(messages, isStreaming),
    [messages, isStreaming]
  );

  const handleScrollToBottom = useCallback(() => {
    listRef.current?.scrollToOffset({ offset: 0, animated: true });
    setIsAtBottom(true);
    setUnreadCount(0);
  }, []);

  const handleScroll = useCallback((event: { nativeEvent: { contentOffset: { y: number } } }) => {
    const y = event.nativeEvent.contentOffset.y;
    // Inverted list: y=0 is "bottom" (newest messages)
    const atBottom = y < 80;
    setIsAtBottom(atBottom);
    if (atBottom) setUnreadCount(0);
  }, []);

  // ── Regenerate ─────────────────────────────────────────────────────────────

  const handleRegenerate = useCallback((_msg: UIMessage) => {
    // Phase 1A stub — re-send the last user message
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser) {
      const text = getTextFromMessage(lastUser);
      adapterRef.current?.send(text).catch(console.error);
    }
  }, [messages]);

  // ── Pull-to-load older messages ────────────────────────────────────────────

  const handleEndReached = useCallback(async () => {
    const adapter = adapterRef.current;
    if (!adapter) return;
    const older = await adapter.loadHistory();
    if (older.length > 0) {
      // Merge: prepend history that isn't already in the store
      const currentIds = new Set(messages.map((m) => m.id));
      const newOlder = older.filter((m) => !currentIds.has(m.id));
      if (newOlder.length > 0) {
        setMessages([...newOlder, ...messages]);
      }
    }
  }, [messages, setMessages]);

  // ── Render helpers ─────────────────────────────────────────────────────────

  const agentName = activeAgentId.charAt(0).toUpperCase() + activeAgentId.slice(1);
  const isConnected = connectionStatus === 'connected';
  const isDisconnected = connectionStatus === 'disconnected' || connectionStatus === 'failed';
  const canSend = adapterReady && isConnected && !isStreaming;

  const renderItem = useCallback(({ item }: { item: ListItem }) => {
    if (item.kind === 'date') {
      return <DateSeparator label={item.label} />;
    }
    if (item.kind === 'typing') {
      return <TypingIndicator />;
    }
    return (
      <MessageBubble
        message={item.message}
        agentName={agentName}
        onRegenerate={handleRegenerate}
      />
    );
  }, [agentName, handleRegenerate]);

  const keyExtractor = useCallback((item: ListItem, index: number): string => {
    if (item.kind === 'date') return `date-${item.label}-${index}`;
    if (item.kind === 'typing') return 'typing-indicator';
    return item.message.id;
  }, []);

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <SafeAreaView style={styles.root}>
      {/* ── Header ── */}
      <View style={styles.header}>
        <TouchableOpacity
          style={styles.headerLeft}
          accessibilityLabel="Open drawer"
          onPress={() => {/* drawer stub — Phase 1B */}}
        >
          <Menu size={22} color={colors.textPrimary} />
        </TouchableOpacity>

        <View style={styles.headerCenter}>
          {/* Avatar */}
          <View style={styles.avatar}>
            <Text style={styles.avatarInitials}>{getInitials(agentName)}</Text>
          </View>
          <Text style={styles.headerTitle}>{agentName}</Text>
        </View>

        {/* Model pill */}
        <View style={styles.modelPill}>
          <Text style={styles.modelPillText}>default</Text>
        </View>
      </View>

      {/* ── Disconnected banner ── */}
      {isDisconnected && (
        <View style={styles.disconnectedBanner}>
          <Text style={styles.disconnectedText}>
            {connectionError ?? 'Disconnected from gateway'}
          </Text>
          <TouchableOpacity onPress={handleRetryConnection} style={styles.retryButton}>
            <RefreshCw size={14} color={colors.textPrimary} />
            <Text style={styles.retryText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={0}
      >
        {/* ── Message list ── */}
        <View style={styles.listContainer}>
          <FlashList
            ref={listRef}
            data={listItems}
            renderItem={renderItem}
            keyExtractor={keyExtractor}
            estimatedItemSize={80}
            inverted
            keyboardShouldPersistTaps="handled"
            keyboardDismissMode="interactive"
            onScroll={handleScroll}
            scrollEventThrottle={100}
            onEndReached={handleEndReached}
            onEndReachedThreshold={0.3}
            ListEmptyComponent={
              <EmptyState
                onChipPress={(text) => {
                  setTextInput(text);
                }}
              />
            }
            contentContainerStyle={styles.listContent}
          />

          {/* Scroll-to-bottom button */}
          {!isAtBottom && (
            <TouchableOpacity
              style={styles.scrollToBottom}
              onPress={handleScrollToBottom}
              activeOpacity={0.8}
            >
              <ChevronDown size={18} color={colors.textPrimary} />
              {unreadCount > 0 && (
                <View style={styles.unreadBadge}>
                  <Text style={styles.unreadBadgeText}>
                    {unreadCount > 99 ? '99+' : String(unreadCount)}
                  </Text>
                </View>
              )}
            </TouchableOpacity>
          )}
        </View>

        {/* ── Voice errors ── */}
        {voiceError && (
          <Text style={styles.voiceError}>{voiceError}</Text>
        )}

        {/* ── Draft recovery — REQ-VOICE-04 ── */}
        {pendingDraft && (
          <VoiceDraftPrompt
            draft={pendingDraft}
            onResume={resumeDraft}
            onDiscard={discardDraft}
          />
        )}

        {/* ── Recording indicator — REQ-VOICE-03 ── */}
        {recordingState === 'recording' && (
          <View style={styles.recordingIndicator}>
            <View style={styles.recordingDot} />
            <Text style={styles.recordingLabel}>
              Recording — screen will stay on
            </Text>
          </View>
        )}

        {/* ── Input bar ── */}
        <View style={styles.inputBar}>
          <TextInput
            style={[
              styles.textInput,
              !isConnected && styles.textInputDisabled,
            ]}
            placeholder={isConnected ? 'Message Polly…' : 'Connecting…'}
            placeholderTextColor={colors.textSecondary}
            value={textInput}
            onChangeText={setTextInput}
            multiline
            maxLength={4000}
            editable={isConnected}
            returnKeyType="send"
            blurOnSubmit={false}
            onSubmitEditing={(e) => {
              // Shift+Enter = newline; Enter = send (hardware keyboard)
              if (!e.nativeEvent.text.endsWith('\n')) {
                handleSend();
              }
            }}
            accessible
            accessibilityLabel={isConnected ? 'Message input' : 'Connecting to gateway'}
          />

          {/* Stop button when streaming */}
          {isStreaming ? (
            <TouchableOpacity
              style={styles.actionButton}
              onPress={handleStop}
              accessibilityLabel="Stop generation"
            >
              <Square size={22} color={colors.textPrimary} fill={colors.textPrimary} />
            </TouchableOpacity>
          ) : textInput.trim().length > 0 ? (
            /* Send button when text is present */
            <TouchableOpacity
              style={[styles.actionButton, styles.sendButton, !canSend && styles.sendButtonDisabled]}
              onPress={handleSend}
              disabled={!canSend}
              accessibilityLabel="Send message"
            >
              <SendHorizontal size={22} color={canSend ? '#ffffff' : colors.textSecondary} />
            </TouchableOpacity>
          ) : (
            /* Mic button when idle */
            <VoiceMicButton
              state={voiceButtonState}
              waveformAmplitudes={waveformAmplitudes}
              onPress={handleMicPress}
              disabled={recordingState === 'processing' || !isConnected}
            />
          )}
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  flex: {
    flex: 1,
  },

  // Header
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    borderBottomWidth: layout.borderThin,
    borderBottomColor: colors.bgBorder,
    backgroundColor: colors.bgSecondary,
  },
  headerLeft: {
    width: layout.minTouchTarget,
    height: layout.minTouchTarget,
    alignItems: 'flex-start',
    justifyContent: 'center',
  },
  headerCenter: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.spacing2,
  },
  headerTitle: {
    ...typography.headline,
    color: colors.textPrimary,
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarInitials: {
    ...typography.caption1,
    color: '#ffffff',
    fontWeight: '700',
  },
  modelPill: {
    backgroundColor: colors.bgPrimary,
    borderColor: colors.bgBorder,
    borderWidth: layout.borderDefault,
    borderRadius: layout.cornerRadiusRounded,
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing1,
  },
  modelPillText: {
    ...typography.caption2,
    color: colors.textSecondary,
  },

  // Disconnected banner
  disconnectedBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.bgSecondary,
    borderBottomWidth: layout.borderThin,
    borderBottomColor: colors.error,
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing2,
    gap: spacing.spacing3,
  },
  disconnectedText: {
    ...typography.footnote,
    color: colors.error,
    flex: 1,
  },
  retryButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.spacing1,
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing2,
    backgroundColor: colors.bgBorder,
    borderRadius: layout.cornerRadiusMedium,
  },
  retryText: {
    ...typography.footnote,
    color: colors.textPrimary,
  },

  // List
  listContainer: {
    flex: 1,
    position: 'relative',
  },
  listContent: {
    paddingVertical: spacing.spacing3,
  },

  // Scroll to bottom
  scrollToBottom: {
    position: 'absolute',
    right: spacing.spacing4,
    bottom: spacing.spacing4,
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.bgSecondary,
    borderColor: colors.bgBorder,
    borderWidth: layout.borderDefault,
    alignItems: 'center',
    justifyContent: 'center',
  },
  unreadBadge: {
    position: 'absolute',
    top: -4,
    right: -4,
    backgroundColor: colors.accent,
    borderRadius: 10,
    minWidth: 18,
    height: 18,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 4,
  },
  unreadBadgeText: {
    ...typography.caption2,
    color: '#ffffff',
    fontWeight: '700',
  },

  // Voice recording
  voiceError: {
    ...typography.footnote,
    color: colors.error,
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
    backgroundColor: colors.error,
  },
  recordingLabel: {
    ...typography.caption1,
    color: colors.textSecondary,
  },

  // Input bar
  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    borderTopWidth: layout.borderThin,
    borderTopColor: colors.bgBorder,
    backgroundColor: colors.bgSecondary,
    gap: spacing.spacing2,
  },
  textInput: {
    flex: 1,
    minHeight: layout.minTouchTarget,
    maxHeight: 120,
    borderRadius: layout.cornerRadiusMedium,
    borderWidth: layout.borderDefault,
    borderColor: colors.bgBorder,
    backgroundColor: colors.bgPrimary,
    paddingHorizontal: spacing.spacing3,
    paddingVertical: spacing.spacing2,
    color: colors.textPrimary,
    ...typography.body,
  },
  textInputDisabled: {
    opacity: 0.5,
  },
  actionButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: layout.cornerRadiusMedium,
  },
  sendButton: {
    backgroundColor: colors.accent,
    borderRadius: layout.cornerRadiusMedium,
  },
  sendButtonDisabled: {
    backgroundColor: colors.bgBorder,
  },
});

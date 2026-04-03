/**
 * chatStore — Zustand store for chat state.
 *
 * Manages messages, streaming state, active agent, and draft text.
 * MMKV persists: activeAgentId, lastActiveSessionKey, draftText.
 */

import { create } from 'zustand';
import { MMKV } from 'react-native-mmkv';
import { getMMKVEncryptionKey } from '../utils/mmkvEncryption';
import type { UIMessage } from 'expo-openclaw-chat';

// ─── MMKV storage ─────────────────────────────────────────────────────────────

// Lazy singleton — not instantiated until first access so the encryption key
// has time to be bootstrapped by getOrCreateMMKVKey() before any store reads.
let _chatStorage: MMKV | null = null;
function getChatStorage(): MMKV {
  if (!_chatStorage) {
    _chatStorage = new MMKV({ id: 'chat-store', encryptionKey: getMMKVEncryptionKey() });
  }
  return _chatStorage;
}

function loadString(key: string, fallback: string): string {
  return getChatStorage().getString(key) ?? fallback;
}

function loadObject<T>(key: string, fallback: T): T {
  const raw = getChatStorage().getString(key);
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}

// ─── Types ────────────────────────────────────────────────────────────────────

interface ChatState {
  // Runtime
  messages: UIMessage[];
  isStreaming: boolean;

  // Agent / session
  activeAgentId: string;
  sessionKey: string; // computed: `agent:${activeAgentId}:main`

  // Persisted
  lastActiveSessionKey: string;

  /** Draft text per session key — persisted so switching agents doesn't lose drafts */
  draftText: Record<string, string>;

  // ─── Actions ────────────────────────────────────────────────────────────────

  setMessages: (messages: UIMessage[]) => void;
  appendMessage: (message: UIMessage) => void;
  updateLastMessage: (updater: (msg: UIMessage) => UIMessage) => void;
  setStreaming: (streaming: boolean) => void;
  setActiveAgent: (agentId: string) => void;
  setDraft: (sessionKey: string, text: string) => void;
  clearDraft: (sessionKey: string) => void;
  getDraft: (sessionKey: string) => string;
}

// ─── Default agent ────────────────────────────────────────────────────────────

const DEFAULT_AGENT_ID = 'polly';

// ─── Store ────────────────────────────────────────────────────────────────────

const initialAgentId = loadString('activeAgentId', DEFAULT_AGENT_ID);
const initialSessionKey = `agent:${initialAgentId}:main`;

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isStreaming: false,

  activeAgentId: initialAgentId,
  sessionKey: initialSessionKey,

  lastActiveSessionKey: loadString('lastActiveSessionKey', initialSessionKey),

  draftText: loadObject<Record<string, string>>('draftText', {}),

  // ─── Actions ────────────────────────────────────────────────────────────────

  setMessages: (messages) => set({ messages }),

  appendMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateLastMessage: (updater) =>
    set((state) => {
      if (state.messages.length === 0) return {};
      const msgs = [...state.messages];
      const last = msgs[msgs.length - 1]!;
      msgs[msgs.length - 1] = updater(last);
      return { messages: msgs };
    }),

  setStreaming: (streaming) => set({ isStreaming: streaming }),

  setActiveAgent: (agentId) => {
    const sessionKey = `agent:${agentId}:main`;
    getChatStorage().set('activeAgentId', agentId);
    getChatStorage().set('lastActiveSessionKey', sessionKey);
    set({ activeAgentId: agentId, sessionKey, lastActiveSessionKey: sessionKey });
  },

  setDraft: (sessionKey, text) => {
    const draft = { ...get().draftText, [sessionKey]: text };
    getChatStorage().set('draftText', JSON.stringify(draft));
    set({ draftText: draft });
  },

  clearDraft: (sessionKey) => {
    const draft = { ...get().draftText };
    delete draft[sessionKey];
    getChatStorage().set('draftText', JSON.stringify(draft));
    set({ draftText: draft });
  },

  getDraft: (sessionKey) => get().draftText[sessionKey] ?? '',
}));

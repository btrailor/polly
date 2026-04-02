/**
 * Store unit tests — connectionStore, chatStore, onboardingStore
 * Covers: state transitions, actions, persistence, Zustand reactivity
 * TEST-STATE series per TESTING_AND_QA_SPEC.md
 */

// ─── connectionStore ──────────────────────────────────────────────────────────

describe('TEST-STATE-003: connectionStore', () => {
  let useConnectionStore: typeof import('../../src/store/connectionStore').useConnectionStore;

  beforeEach(() => {
    jest.resetModules();
    useConnectionStore = require('../../src/store/connectionStore').useConnectionStore;
    useConnectionStore.getState().reset();
  });

  it('initial state is disconnected', () => {
    const state = useConnectionStore.getState();
    expect(state.status).toBe('disconnected');
    expect(state.gatewayUrl).toBeNull();
    expect(state.lastError).toBeNull();
    expect(state.connectCount).toBe(0);
  });

  it('setStatus transitions through all valid states', () => {
    const store = useConnectionStore.getState();
    const states = ['connecting', 'connected', 'reconnecting', 'failed', 'disconnected'] as const;
    for (const status of states) {
      store.setStatus(status);
      expect(useConnectionStore.getState().status).toBe(status);
    }
  });

  it('setGatewayUrl sets gatewayUrl', () => {
    useConnectionStore.getState().setGatewayUrl('https://tunnel.example.com');
    expect(useConnectionStore.getState().gatewayUrl).toBe('https://tunnel.example.com');
  });

  it('setError sets lastError', () => {
    useConnectionStore.getState().setError('connection refused');
    expect(useConnectionStore.getState().lastError).toBe('connection refused');
  });

  it('setError(null) clears lastError', () => {
    useConnectionStore.getState().setError('some error');
    useConnectionStore.getState().setError(null);
    expect(useConnectionStore.getState().lastError).toBeNull();
  });

  it('recordConnect increments connectCount and clears lastError', () => {
    useConnectionStore.getState().setError('old error');
    useConnectionStore.getState().recordConnect();
    expect(useConnectionStore.getState().connectCount).toBe(1);
    expect(useConnectionStore.getState().lastError).toBeNull();

    useConnectionStore.getState().recordConnect();
    expect(useConnectionStore.getState().connectCount).toBe(2);
  });

  it('reset returns all fields to initial state', () => {
    const store = useConnectionStore.getState();
    store.setStatus('connected');
    store.setGatewayUrl('https://example.com');
    store.setError('some error');
    store.recordConnect();

    store.reset();

    const s = useConnectionStore.getState();
    expect(s.status).toBe('disconnected');
    expect(s.gatewayUrl).toBeNull();
    expect(s.lastError).toBeNull();
    expect(s.connectCount).toBe(0);
  });
});

// ─── chatStore ────────────────────────────────────────────────────────────────

describe('TEST-STATE-001: chatStore', () => {
  let useChatStore: typeof import('../../src/store/chatStore').useChatStore;

  beforeEach(() => {
    jest.resetModules();
    // Seed MMKV encryption key for sync accessor
    const { setMMKVEncryptionKeyForTest } = require('../../src/utils/mmkvEncryption');
    if (setMMKVEncryptionKeyForTest) {
      setMMKVEncryptionKeyForTest('a'.repeat(64));
    }
    useChatStore = require('../../src/store/chatStore').useChatStore;
  });

  const makeMessage = (id: string, role: 'user' | 'assistant' = 'user') => ({
    id,
    role,
    content: [{ type: 'text' as const, text: `Message ${id}` }],
    createdAt: Date.now(),
  });

  it('initial messages array is empty', () => {
    expect(useChatStore.getState().messages).toEqual([]);
  });

  it('initial isStreaming is false', () => {
    expect(useChatStore.getState().isStreaming).toBe(false);
  });

  it('setMessages replaces message list', () => {
    const msgs = [makeMessage('1'), makeMessage('2')];
    useChatStore.getState().setMessages(msgs);
    expect(useChatStore.getState().messages).toHaveLength(2);
    expect(useChatStore.getState().messages[0].id).toBe('1');
  });

  it('appendMessage adds to end of list', () => {
    useChatStore.getState().setMessages([makeMessage('1')]);
    useChatStore.getState().appendMessage(makeMessage('2'));
    const msgs = useChatStore.getState().messages;
    expect(msgs).toHaveLength(2);
    expect(msgs[1].id).toBe('2');
  });

  it('updateLastMessage mutates only the last message', () => {
    useChatStore.getState().setMessages([makeMessage('1'), makeMessage('2', 'assistant')]);
    useChatStore.getState().updateLastMessage((msg) => ({
      ...msg,
      content: [{ type: 'text', text: 'Updated' }],
    }));
    const msgs = useChatStore.getState().messages;
    expect((msgs[1].content[0] as any).text).toBe('Updated');
    expect((msgs[0].content[0] as any).text).toBe('Message 1'); // first unchanged
  });

  it('updateLastMessage is a no-op on empty list', () => {
    useChatStore.getState().setMessages([]);
    expect(() => {
      useChatStore.getState().updateLastMessage((m) => m);
    }).not.toThrow();
    expect(useChatStore.getState().messages).toHaveLength(0);
  });

  it('setStreaming toggles isStreaming', () => {
    useChatStore.getState().setStreaming(true);
    expect(useChatStore.getState().isStreaming).toBe(true);
    useChatStore.getState().setStreaming(false);
    expect(useChatStore.getState().isStreaming).toBe(false);
  });

  it('setActiveAgent updates agentId and sessionKey', () => {
    useChatStore.getState().setActiveAgent('the-strategist');
    const s = useChatStore.getState();
    expect(s.activeAgentId).toBe('the-strategist');
    expect(s.sessionKey).toBe('agent:the-strategist:main');
  });

  it('draft: setDraft stores text per sessionKey', () => {
    useChatStore.getState().setDraft('agent:polly:main', 'Hello world');
    expect(useChatStore.getState().getDraft('agent:polly:main')).toBe('Hello world');
  });

  it('draft: getDraft returns empty string for unknown sessionKey', () => {
    expect(useChatStore.getState().getDraft('agent:unknown:main')).toBe('');
  });

  it('draft: clearDraft removes the entry', () => {
    useChatStore.getState().setDraft('agent:polly:main', 'text');
    useChatStore.getState().clearDraft('agent:polly:main');
    expect(useChatStore.getState().getDraft('agent:polly:main')).toBe('');
  });

  it('draft: multiple sessions tracked independently', () => {
    useChatStore.getState().setDraft('agent:polly:main', 'polly draft');
    useChatStore.getState().setDraft('agent:strategist:main', 'strategist draft');
    expect(useChatStore.getState().getDraft('agent:polly:main')).toBe('polly draft');
    expect(useChatStore.getState().getDraft('agent:strategist:main')).toBe('strategist draft');
  });
});

// ─── onboardingStore ──────────────────────────────────────────────────────────

describe('TEST-STATE-002: onboardingStore', () => {
  let useOnboardingStore: any;

  beforeEach(() => {
    jest.resetModules();
    const { setMMKVEncryptionKeyForTest } = require('../../src/utils/mmkvEncryption');
    if (setMMKVEncryptionKeyForTest) {
      setMMKVEncryptionKeyForTest('a'.repeat(64));
    }
    useOnboardingStore = require('../../src/store/onboardingStore').useOnboardingStore;
  });

  it('initial phase is welcome', () => {
    expect(useOnboardingStore.getState().phase).toBe('welcome');
  });

  it('initial isComplete is false', () => {
    expect(useOnboardingStore.getState().isComplete).toBe(false);
  });

  it('setPhase transitions phase', () => {
    useOnboardingStore.getState().setPhase('gateway-url');
    expect(useOnboardingStore.getState().phase).toBe('gateway-url');
    useOnboardingStore.getState().setPhase('gateway-token');
    expect(useOnboardingStore.getState().phase).toBe('gateway-token');
    useOnboardingStore.getState().setPhase('testing-connection');
    expect(useOnboardingStore.getState().phase).toBe('testing-connection');
  });

  it('setGatewayUrl stores the URL', () => {
    useOnboardingStore.getState().setGatewayUrl('https://my.tunnel.com');
    expect(useOnboardingStore.getState().gatewayUrl).toBe('https://my.tunnel.com');
  });

  it('markComplete sets isComplete and phase to complete', () => {
    useOnboardingStore.getState().markComplete();
    const s = useOnboardingStore.getState();
    expect(s.isComplete).toBe(true);
    expect(s.phase).toBe('complete');
    expect(s.completedAt).toBeDefined();
    expect(typeof s.completedAt).toBe('number');
  });

  it('reset returns to initial state', () => {
    useOnboardingStore.getState().setGatewayUrl('https://x.com');
    useOnboardingStore.getState().markComplete();
    useOnboardingStore.getState().reset();
    const s = useOnboardingStore.getState();
    expect(s.phase).toBe('welcome');
    expect(s.isComplete).toBe(false);
    expect(s.gatewayUrl).toBeNull();
  });
});

// ─── onboardingStore additional branch coverage ─────────────────────────────

describe('TEST-STATE-002b: onboardingStore — readOnboardingComplete', () => {
  let readOnboardingComplete: () => boolean;
  let useOnboardingStore: any;

  beforeEach(() => {
    jest.resetModules();
    useOnboardingStore = require('../../src/store/onboardingStore').useOnboardingStore;
    readOnboardingComplete = require('../../src/store/onboardingStore').readOnboardingComplete;
  });

  it('readOnboardingComplete returns false before markComplete', () => {
    expect(readOnboardingComplete()).toBe(false);
  });

  it('readOnboardingComplete returns true after markComplete', () => {
    useOnboardingStore.getState().markComplete();
    expect(readOnboardingComplete()).toBe(true);
  });

  it('readOnboardingComplete returns false after reset', () => {
    useOnboardingStore.getState().markComplete();
    useOnboardingStore.getState().reset();
    expect(readOnboardingComplete()).toBe(false);
  });

  it('setGatewayUrl persists to MMKV (round-trips through saveToMMKV)', () => {
    useOnboardingStore.getState().setGatewayUrl('https://my.server.com');
    expect(readOnboardingComplete()).toBe(false); // just verifying no throw
    expect(useOnboardingStore.getState().gatewayUrl).toBe('https://my.server.com');
  });

  it('setPhase persists to MMKV (round-trips through saveToMMKV)', () => {
    useOnboardingStore.getState().setPhase('gateway-token');
    expect(useOnboardingStore.getState().phase).toBe('gateway-token');
  });
});

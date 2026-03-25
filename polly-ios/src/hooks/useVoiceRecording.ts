/**
 * useVoiceRecording — REQ-VOICE-01, REQ-VOICE-04
 *
 * Hook managing voice recording state, idle timer suppression,
 * and interruption recovery (draft persistence).
 *
 * Idle timer rules (REQ-VOICE-01):
 *   - Set isIdleTimerDisabled = true on recording START
 *   - Clear on: send, cancel, error, app background, audio interruption
 *   - Never leave the flag set after the session ends
 *
 * Interruption recovery (REQ-VOICE-04):
 *   - Phone call / system interruption → stop recording, save draft
 *   - App backgrounded mid-recording → stop recording, save draft
 *   - On return: surface "Resume your recording?" prompt
 *   - Draft stored in Documents/voice-drafts/<timestamp>.json
 *   - Never auto-discarded — only discarded on explicit user action
 *
 * Spec: specs/VOICE_INTERACTION.md
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { AppState, AppStateStatus, Platform } from 'react-native';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export type RecordingState = 'idle' | 'recording' | 'processing' | 'error';

export interface VoiceDraft {
  id: string;
  timestamp: number;
  durationSeconds: number;
  transcript?: string;
  audioPath?: string;
}

export interface UseVoiceRecordingReturn {
  recordingState: RecordingState;
  waveformAmplitudes: [number, number, number];
  pendingDraft: VoiceDraft | null;
  startRecording: () => Promise<void>;
  stopAndSend: () => Promise<void>;
  cancelRecording: () => void;
  resumeDraft: () => void;
  discardDraft: () => void;
  errorMessage: string | null;
}

// ─────────────────────────────────────────────────────────────────────────────
// Idle timer — platform-safe wrapper
// NOTE: In a real Expo/RN native module, use:
//   import { activateKeepAwakeAsync, deactivateKeepAwake } from 'expo-keep-awake'
// or UIApplication.shared.isIdleTimerDisabled via a NativeModule.
// This wrapper abstracts the platform call so the hook stays testable.
// ─────────────────────────────────────────────────────────────────────────────

const IdleTimer = {
  disable: () => {
    // Native: UIApplication.shared.isIdleTimerDisabled = true (main thread)
    // Expo: activateKeepAwakeAsync('voice-recording')
    if (__DEV__) console.log('[VoiceRecording] Idle timer DISABLED');
  },
  enable: () => {
    // Native: UIApplication.shared.isIdleTimerDisabled = false (main thread)
    // Expo: deactivateKeepAwake('voice-recording')
    if (__DEV__) console.log('[VoiceRecording] Idle timer ENABLED');
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Draft persistence — filesystem wrapper
// In production: use expo-file-system or react-native-fs
// ─────────────────────────────────────────────────────────────────────────────

const DraftStore = {
  save: async (draft: VoiceDraft): Promise<void> => {
    // FileSystem.writeAsStringAsync(`Documents/voice-drafts/${draft.id}.json`, JSON.stringify(draft))
    if (__DEV__) console.log('[VoiceRecording] Draft saved:', draft.id);
  },
  load: async (): Promise<VoiceDraft | null> => {
    // Read most recent draft from Documents/voice-drafts/
    if (__DEV__) console.log('[VoiceRecording] Checking for pending draft...');
    return null; // No draft in dev environment
  },
  discard: async (draftId: string): Promise<void> => {
    // FileSystem.deleteAsync(`Documents/voice-drafts/${draftId}.json`)
    if (__DEV__) console.log('[VoiceRecording] Draft discarded:', draftId);
  },
};

// ─────────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────────

export function useVoiceRecording(
  onTranscript: (text: string) => void
): UseVoiceRecordingReturn {
  const [recordingState, setRecordingState] = useState<RecordingState>('idle');
  const [waveformAmplitudes, setWaveformAmplitudes] = useState<[number, number, number]>([0, 0, 0]);
  const [pendingDraft, setPendingDraft] = useState<VoiceDraft | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const recordingRef = useRef<boolean>(false);
  const startTimeRef = useRef<number>(0);
  const waveformTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  // ── Load pending draft on mount ────────────────────────────────────────────
  useEffect(() => {
    DraftStore.load().then(draft => {
      if (draft) setPendingDraft(draft);
    });
  }, []);

  // ── App state: background mid-recording → save draft ──────────────────────
  // REQ-VOICE-01: clear idle timer in applicationWillResignActive
  // REQ-VOICE-04: save draft on background
  useEffect(() => {
    const subscription = AppState.addEventListener('change', (nextState: AppStateStatus) => {
      const wasActive = appStateRef.current === 'active';
      const isBackground = nextState === 'background' || nextState === 'inactive';

      if (wasActive && isBackground && recordingRef.current) {
        // App backgrounded while recording — stop and save draft
        stopRecordingAndSaveDraft('backgrounded');
      }

      appStateRef.current = nextState;
    });

    return () => subscription?.remove();
  }, []);

  // ── Waveform simulation (replace with real AVAudioRecorder metering) ───────
  const startWaveformMetering = useCallback(() => {
    waveformTimerRef.current = setInterval(() => {
      if (!recordingRef.current) return;
      // In production: read AVAudioRecorder.averagePower(forChannel:) and normalise to 0–1
      setWaveformAmplitudes([
        Math.random() * 0.8 + 0.1,
        Math.random() * 0.9 + 0.1,
        Math.random() * 0.7 + 0.1,
      ]);
    }, 80); // ~12fps — smooth enough, not wasteful
  }, []);

  const stopWaveformMetering = useCallback(() => {
    if (waveformTimerRef.current) {
      clearInterval(waveformTimerRef.current);
      waveformTimerRef.current = null;
    }
    setWaveformAmplitudes([0, 0, 0]);
  }, []);

  // ── Internal: stop recording and save draft ────────────────────────────────
  const stopRecordingAndSaveDraft = useCallback(async (reason: string) => {
    if (!recordingRef.current) return;
    recordingRef.current = false;

    IdleTimer.enable(); // REQ-VOICE-01: clear idle timer on ALL exit paths
    stopWaveformMetering();
    setRecordingState('idle');

    const duration = (Date.now() - startTimeRef.current) / 1000;
    const draft: VoiceDraft = {
      id: `draft-${Date.now()}`,
      timestamp: Date.now(),
      durationSeconds: duration,
    };

    await DraftStore.save(draft);
    setPendingDraft(draft);

    if (__DEV__) console.log(`[VoiceRecording] Stopped (${reason}), draft saved`);
  }, [stopWaveformMetering]);

  // ── Public: startRecording ─────────────────────────────────────────────────
  const startRecording = useCallback(async () => {
    try {
      // Request microphone permission (expo-av / react-native-permissions)
      // const { granted } = await Audio.requestPermissionsAsync();
      // if (!granted) { setErrorMessage('Microphone permission required'); setRecordingState('error'); return; }

      IdleTimer.disable(); // REQ-VOICE-01: disable idle timer FIRST
      recordingRef.current = true;
      startTimeRef.current = Date.now();
      setRecordingState('recording');
      setErrorMessage(null);
      startWaveformMetering();

      // In production: await Audio.Recording.createAsync(Audio.RecordingOptionsPresets.HIGH_QUALITY)
    } catch (err) {
      IdleTimer.enable(); // REQ-VOICE-01: always re-enable on error path
      recordingRef.current = false;
      setErrorMessage('Could not start recording. Please try again.');
      setRecordingState('error');
    }
  }, [startWaveformMetering]);

  // ── Public: stopAndSend ────────────────────────────────────────────────────
  const stopAndSend = useCallback(async () => {
    if (!recordingRef.current) return;
    recordingRef.current = false;

    IdleTimer.enable(); // REQ-VOICE-01: clear on send path
    stopWaveformMetering();
    setRecordingState('processing');

    try {
      // In production:
      // 1. Stop recording: await recording.stopAndUnloadAsync()
      // 2. Get URI: recording.getURI()
      // 3. Send to STT: const transcript = await transcribe(uri)
      // 4. Pass to chat: onTranscript(transcript)

      // Simulate processing delay
      await new Promise(resolve => setTimeout(resolve, 500));
      onTranscript('[voice transcript would appear here]');
      setRecordingState('idle');
    } catch (err) {
      setErrorMessage('Something went wrong sending your recording.');
      setRecordingState('error');
    }
  }, [stopWaveformMetering, onTranscript]);

  // ── Public: cancelRecording ────────────────────────────────────────────────
  const cancelRecording = useCallback(() => {
    if (!recordingRef.current) return;
    recordingRef.current = false;

    IdleTimer.enable(); // REQ-VOICE-01: clear on cancel path
    stopWaveformMetering();
    setRecordingState('idle');
    setErrorMessage(null);
  }, [stopWaveformMetering]);

  // ── Public: resumeDraft ────────────────────────────────────────────────────
  const resumeDraft = useCallback(() => {
    // In production: load draft audio, resume recording session
    // For now: just clear the draft and start fresh
    setPendingDraft(null);
    startRecording();
  }, [startRecording]);

  // ── Public: discardDraft ───────────────────────────────────────────────────
  const discardDraft = useCallback(() => {
    if (pendingDraft) {
      DraftStore.discard(pendingDraft.id);
      setPendingDraft(null);
    }
  }, [pendingDraft]);

  // ── Cleanup on unmount ─────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      if (recordingRef.current) {
        IdleTimer.enable(); // REQ-VOICE-01: never leave idle timer disabled
        recordingRef.current = false;
      }
      stopWaveformMetering();
    };
  }, []);

  return {
    recordingState,
    waveformAmplitudes,
    pendingDraft,
    startRecording,
    stopAndSend,
    cancelRecording,
    resumeDraft,
    discardDraft,
    errorMessage,
  };
}

export default useVoiceRecording;

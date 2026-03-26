# Phase 2: Voice Upgrade

**Status:** 📋 Planned  
**Gate:** Phase 1 voice (expo-speech-recognition STT) working  
**Spec source:** `POLLY_IOS_SPEC.md` §15.2.2, §12; `SOMATIC_INTERFACE.md`  
**Owners:** @frontend, @ai_expert (model selection)

## Goal

Replace Phase 1 system STT/TTS with:
- **STT:** `whisper.rn` — on-device ML (~40MB model, no cloud, better accuracy, Lockdown Mode compatible)
- **TTS:** ElevenLabs streaming — voice picker, per-agent voice assignment, `.buffering` state

Phase 1 system STT/TTS deprecated after this ships.

## Tasks

### whisper.rn (On-Device STT)
- [ ] Install `whisper.rn` (~40MB bundled model — requires app size review)
- [ ] Replace `expo-speech-recognition` with whisper.rn in `useVoiceRecording.ts`
- [ ] Streaming transcription: real-time partial results while recording
- [ ] Language detection (auto or user-configured)
- [ ] Latency target: <200ms first token after stop
- [ ] Memory-only audio buffer preserved (Phase 1 Lockdown hook — no temp files)
- [ ] Model download on first use (not bundled if size prohibitive) — download gating UI

### ElevenLabs Streaming TTS
- [ ] ElevenLabs API key config in Settings → Voice
- [ ] Streaming audio playback: buffer + stream (not wait-for-complete)
- [ ] `.buffering` state in VoiceMicButton (distinct from `.listening` and `.idle`)
- [ ] Per-agent voice assignment (Settings → Agent → Voice)
- [ ] Voice picker: list ElevenLabs voices, preview sample
- [ ] Fallback to system TTS if ElevenLabs unavailable (API key missing, offline)
- [ ] Lockdown Mode: ElevenLabs disabled (cloud TTS creates outbound data); fallback to system TTS only

### Voice UX Upgrades
- [ ] Streaming transcript display while recording (whisper.rn partial results)
- [ ] Voice draft editing before send (existing `VoiceDraftPrompt` — verify with new STT)
- [ ] Auto-send option (configurable: always / never / after 2s silence)
- [ ] Voice activity detection (stop recording on silence)

### Migration
- [ ] Remove `expo-speech-recognition` dependency after whisper.rn ships
- [ ] Update `VOICE_BEHAVIOR_TESTS.md` test cases for new pipeline

## Done When
Whisper STT working on-device. ElevenLabs TTS streaming with per-agent voices. Phase 1 system STT/TTS deprecated. All voice tests updated.

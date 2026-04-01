// Mock expo-speech-recognition — mock start/stop/results
export const ExpoSpeechRecognitionModule = {
  start: jest.fn(),
  stop: jest.fn(),
  abort: jest.fn(),
  getSupportedLocales: jest.fn(async () => ({ locales: ['en-US'], installedLocales: ['en-US'] })),
  isRecognitionAvailable: jest.fn(async () => true),
  requestPermissionsAsync: jest.fn(async () => ({ granted: true, status: 'granted' })),
  getPermissionsAsync: jest.fn(async () => ({ granted: true, status: 'granted' })),
};

export const useSpeechRecognitionEvent = jest.fn();
export const AudioEncodingAndroidValue = {};
export const AVAudioSessionCategoryOptionsIosValue = {};

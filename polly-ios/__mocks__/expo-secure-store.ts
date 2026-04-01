// Mock expo-secure-store — in-memory Map<string, string>
const store = new Map<string, string>();

export const setItemAsync = jest.fn(async (key: string, value: string) => {
  store.set(key, value);
});

export const getItemAsync = jest.fn(async (key: string): Promise<string | null> => {
  return store.get(key) ?? null;
});

export const deleteItemAsync = jest.fn(async (key: string) => {
  store.delete(key);
});

export const WHEN_UNLOCKED = 1;
export const WHEN_PASSCODE_SET_THIS_DEVICE_ONLY = 2;
export const WHEN_UNLOCKED_THIS_DEVICE_ONLY = 3;
export const AFTER_FIRST_UNLOCK = 4;
export const AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY = 5;

// Test helper: reset all store state between tests
export const __resetStore = () => {
  store.clear();
  jest.clearAllMocks();
};

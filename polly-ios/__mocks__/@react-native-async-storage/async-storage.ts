// Mock @react-native-async-storage/async-storage — in-memory Map
const store = new Map<string, string>();

const AsyncStorage = {
  getItem: jest.fn(async (key: string): Promise<string | null> => {
    return store.get(key) ?? null;
  }),
  setItem: jest.fn(async (key: string, value: string): Promise<void> => {
    store.set(key, value);
  }),
  removeItem: jest.fn(async (key: string): Promise<void> => {
    store.delete(key);
  }),
  clear: jest.fn(async (): Promise<void> => {
    store.clear();
  }),
  getAllKeys: jest.fn(async (): Promise<string[]> => {
    return Array.from(store.keys());
  }),
  multiGet: jest.fn(async (keys: string[]): Promise<[string, string | null][]> => {
    return keys.map((k) => [k, store.get(k) ?? null]);
  }),
  multiSet: jest.fn(async (pairs: [string, string][]): Promise<void> => {
    for (const [k, v] of pairs) store.set(k, v);
  }),
  multiRemove: jest.fn(async (keys: string[]): Promise<void> => {
    for (const k of keys) store.delete(k);
  }),
  __resetStore: () => {
    store.clear();
    jest.clearAllMocks();
  },
};

export default AsyncStorage;

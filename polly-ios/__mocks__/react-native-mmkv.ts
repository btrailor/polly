// Mock react-native-mmkv — in-memory Map with full MMKV API
class MMKVMock {
  private store = new Map<string, string | number | boolean | Uint8Array>();

  set(key: string, value: string | number | boolean | Uint8Array): void {
    this.store.set(key, value);
  }

  getString(key: string): string | undefined {
    const val = this.store.get(key);
    return typeof val === 'string' ? val : undefined;
  }

  getNumber(key: string): number | undefined {
    const val = this.store.get(key);
    return typeof val === 'number' ? val : undefined;
  }

  getBoolean(key: string): boolean | undefined {
    const val = this.store.get(key);
    return typeof val === 'boolean' ? val : undefined;
  }

  getBuffer(key: string): Uint8Array | undefined {
    const val = this.store.get(key);
    return val instanceof Uint8Array ? val : undefined;
  }

  contains(key: string): boolean {
    return this.store.has(key);
  }

  delete(key: string): void {
    this.store.delete(key);
  }

  getAllKeys(): string[] {
    return Array.from(this.store.keys());
  }

  clearAll(): void {
    this.store.clear();
  }
}

export const MMKV = jest.fn().mockImplementation(() => new MMKVMock());
export const createMMKV = jest.fn().mockImplementation(() => new MMKVMock());

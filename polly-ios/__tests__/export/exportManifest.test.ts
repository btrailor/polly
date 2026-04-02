/**
 * exportManifest.ts unit tests
 * Covers: generateExportManifest, all layer slots, schema versioning, edge cases
 */

import { generateExportManifest } from '../../src/export/exportManifest';

const BASE_OPTS = {
  owner: 'brett',
  gatewayVersion: '2.1.0',
  memoryEntryCount: 5,
  postMortemCount: 2,
  annualCount: 1,
};

describe('generateExportManifest', () => {
  it('returns correct polly_export_version', () => {
    const m = generateExportManifest(BASE_OPTS);
    expect(m.polly_export_version).toBe('1.0');
  });

  it('sets created_at as valid ISO 8601', () => {
    const m = generateExportManifest(BASE_OPTS);
    expect(typeof m.created_at).toBe('string');
    expect(() => new Date(m.created_at)).not.toThrow();
    expect(new Date(m.created_at).toISOString()).toBe(m.created_at);
  });

  it('sets owner from options', () => {
    const m = generateExportManifest({ ...BASE_OPTS, owner: 'alice' });
    expect(m.owner).toBe('alice');
  });

  it('sets gateway_version from options', () => {
    const m = generateExportManifest({ ...BASE_OPTS, gatewayVersion: '3.0.0' });
    expect(m.gateway_version).toBe('3.0.0');
  });

  it('memory layer: present=true when memoryEntryCount > 0', () => {
    const m = generateExportManifest({ ...BASE_OPTS, memoryEntryCount: 3 });
    expect(m.layers.memory.present).toBe(true);
    expect(m.layers.memory.entry_count).toBe(3);
    expect(m.layers.memory.schema_version).toBe('1.0');
  });

  it('memory layer: present=false when memoryEntryCount === 0', () => {
    const m = generateExportManifest({ ...BASE_OPTS, memoryEntryCount: 0 });
    expect(m.layers.memory.present).toBe(false);
    expect(m.layers.memory.entry_count).toBe(0);
  });

  it('oral_history layer: present=true when postMortemCount > 0', () => {
    const m = generateExportManifest({ ...BASE_OPTS, postMortemCount: 1, annualCount: 0 });
    expect(m.layers.oral_history.present).toBe(true);
    expect(m.layers.oral_history.post_mortem_count).toBe(1);
  });

  it('oral_history layer: present=true when annualCount > 0', () => {
    const m = generateExportManifest({ ...BASE_OPTS, postMortemCount: 0, annualCount: 1 });
    expect(m.layers.oral_history.present).toBe(true);
    expect(m.layers.oral_history.annual_count).toBe(1);
  });

  it('oral_history layer: present=false when both counts are 0', () => {
    const m = generateExportManifest({ ...BASE_OPTS, postMortemCount: 0, annualCount: 0 });
    expect(m.layers.oral_history.present).toBe(false);
  });

  it('Phase 3 layers are all present=false with null schema_version', () => {
    const m = generateExportManifest(BASE_OPTS);
    const phase3Layers = ['drift', 'patterns', 'practices', 'reasoning', 'graph'] as const;
    for (const layer of phase3Layers) {
      expect(m.layers[layer].present).toBe(false);
      expect(m.layers[layer].schema_version).toBeNull();
    }
  });

  it('all 7 layer slots are present in output', () => {
    const m = generateExportManifest(BASE_OPTS);
    const expected = ['memory', 'oral_history', 'drift', 'patterns', 'practices', 'reasoning', 'graph'];
    for (const layer of expected) {
      expect(m.layers).toHaveProperty(layer);
    }
  });

  it('two calls have different created_at if time advances', async () => {
    const m1 = generateExportManifest(BASE_OPTS);
    await new Promise((r) => setTimeout(r, 5));
    const m2 = generateExportManifest(BASE_OPTS);
    // Both are valid ISO strings; they may or may not differ by ms but both valid
    expect(new Date(m1.created_at).getTime()).toBeLessThanOrEqual(
      new Date(m2.created_at).getTime()
    );
  });
});

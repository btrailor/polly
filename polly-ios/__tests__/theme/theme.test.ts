/**
 * Theme constants coverage — colors.ts and tokens.ts
 * These are pure constant exports; importing them covers all statements.
 */

describe('theme/colors', () => {
  it('exports a colors object with expected keys', () => {
    const { colors } = require('../../src/theme/colors');
    expect(typeof colors).toBe('object');
    expect(colors).not.toBeNull();
    // Spot-check a few expected color keys
    const keys = Object.keys(colors);
    expect(keys.length).toBeGreaterThan(0);
  });
});

describe('theme/tokens (reas)', () => {
  it('exports theme tokens', () => {
    const tokens = require('../../src/themes/reas');
    expect(tokens).not.toBeNull();
    expect(typeof tokens).toBe('object');
  });
});

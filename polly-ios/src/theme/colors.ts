/**
 * Polly Design System — Color & Typography Tokens
 * 
 * Authoritative source: POLLY_IOS_SPEC.md §5
 * Generated: March 24, 2026
 */

// ============================================================================
// COLORS
// ============================================================================

export const colors = {
  // ─────────────────────────────────────────────────────────────────────────
  // Accent (Polly Brand)
  // ─────────────────────────────────────────────────────────────────────────
  accent: '#f0903b',        // Primary CTA, active states
  accentDim: '#c84012',     // Pressed/disabled accent
  accentLight: '#fff7ed',   // Light accent tint background

  // ─────────────────────────────────────────────────────────────────────────
  // Backgrounds (Dark Mode — primary app experience)
  // ─────────────────────────────────────────────────────────────────────────
  bgPrimary: '#020617',     // App background (darkest)
  bgSecondary: '#0c1323',   // Card/container background
  bgBorder: '#1e2b48',      // Border color, subtle dividers

  // ─────────────────────────────────────────────────────────────────────────
  // Text (Dark Mode)
  // ─────────────────────────────────────────────────────────────────────────
  textPrimary: '#f8fafc',     // Body text, primary
  textSecondary: '#b5c1ce',   // Secondary text, captions, metadata

  // ─────────────────────────────────────────────────────────────────────────
  // Semantic Colors
  // ─────────────────────────────────────────────────────────────────────────
  success: '#22c55e',   // Success states, positive actions
  error: '#ef4444',     // Errors, destructive actions
  warning: '#eab308',   // Warnings, cautions
  info: '#2563eb',      // Info, neutral actions

  // ─────────────────────────────────────────────────────────────────────────
  // Polly Card
  // Token: pollyCardBgTint — deferred to Aight dark mode palette lock.
  // Do NOT hardcode a purple/indigo value. This is a 3–5% desaturated
  // version of bgSecondary once the palette ships.
  // Fallback: bgSecondary at ~3% blue-shifted. REPLACE at palette lock.
  // @design_eng: inject final value here when dark mode palette is locked.
  // ─────────────────────────────────────────────────────────────────────────
  pollyCardBgTint: '#0d1426',   // Placeholder — REPLACE at Aight dark mode palette lock

  // ─────────────────────────────────────────────────────────────────────────
  // Domain Colors (Agent domains, visual categorization)
  // ─────────────────────────────────────────────────────────────────────────
  sigils: '#2563eb',    // Code (blue)
  signals: '#ad48dd',   // Audio (purple)
  scrolls: '#22c55e',   // Writing (green) — WCAG AA compliant
  glyphs: '#eab308',    // Design (gold)
  grids: '#16a399',     // Systems (teal)
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  largeTitle: {
    fontSize: 34,
    fontWeight: '700' as const,
    lineHeight: 41,
  },
  title1: {
    fontSize: 28,
    fontWeight: '700' as const,
    lineHeight: 34,
  },
  title2: {
    fontSize: 22,
    fontWeight: '700' as const,
    lineHeight: 26,
  },
  title3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 24,
  },
  headline: {
    fontSize: 17,
    fontWeight: '600' as const,
    lineHeight: 22,
  },
  body: {
    fontSize: 17,
    fontWeight: '400' as const,
    lineHeight: 22,
  },
  callout: {
    fontSize: 16,
    fontWeight: '500' as const,
    lineHeight: 21,
  },
  subheadline: {
    fontSize: 15,
    fontWeight: '600' as const,
    lineHeight: 20,
  },
  footnote: {
    fontSize: 13,
    fontWeight: '400' as const,
    lineHeight: 18,
  },
  caption1: {
    fontSize: 12,
    fontWeight: '500' as const,
    lineHeight: 16,
  },
  caption2: {
    fontSize: 11,
    fontWeight: '400' as const,
    lineHeight: 13,
  },
} as const;

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  spacing1: 4,
  spacing2: 8,
  spacing3: 12,
  spacing4: 16,
  spacing6: 24,
  spacing8: 32,
} as const;

// ============================================================================
// LAYOUT CONSTRAINTS
// ============================================================================

export const layout = {
  // Touch targets (Apple HIG)
  minTouchTarget: 44,

  // List dimensions
  listRowStandard: 56,
  listRowCompact: 52,

  // Radius
  cornerRadiusSmall: 8,
  cornerRadiusMedium: 12,
  cornerRadiusLarge: 18,
  cornerRadiusRounded: 24,

  // Border widths
  borderThin: 0.5,
  borderDefault: 1,
  borderThick: 1.5,
} as const;

// ============================================================================
// SEMANTIC ALIASES (for component usage clarity)
// ============================================================================

export const semanticColors = {
  // Chat bubbles
  bubbleUser: colors.accent,
  bubbleAssistant: colors.bgSecondary,

  // Buttons
  buttonPrimary: colors.accent,
  buttonPrimaryText: '#ffffff',
  buttonSecondary: colors.bgBorder,
  buttonSecondaryText: colors.textPrimary,
  buttonDestructive: colors.error,

  // Input
  inputBackground: colors.bgSecondary,
  inputBorder: colors.bgBorder,
  inputText: colors.textPrimary,
  inputPlaceholder: colors.textSecondary,

  // Status indicators
  connectionActive: colors.success,
  connectionInactive: colors.textSecondary,
  connectionError: colors.error,

  // Domain badges (agent categorization)
  domainCode: colors.sigils,
  domainAudio: colors.signals,
  domainWriting: colors.scrolls,
  domainDesign: colors.glyphs,
  domainSystems: colors.grids,
} as const;

// ============================================================================
// EXPORT DEFAULTS FOR CONVENIENCE
// ============================================================================

export default {
  colors,
  typography,
  spacing,
  layout,
  semanticColors,
};

// ============================================================================
// LIGHT MODE COLOR MAP (Albers theme — light variant)
// ============================================================================

export const dark = colors;

export const light = {
  // Base
  bgPrimary:    '#FFFFFF',
  bgSecondary:  '#F5F5F7',
  bgTertiary:   '#EBEBF0',
  bgElevated:   '#FFFFFF',

  // Text
  textPrimary:  '#0A0A0A',
  textSecondary:'#3C3C43',
  textTertiary: '#8E8E93',
  textInverse:  '#FFFFFF',

  // Accent (same as dark — brand colors don't flip)
  accentGreen:  '#22C55E',
  accentBlue:   '#3B82F6',
  accentAmber:  '#F59E0B',
  accentRed:    '#EF4444',
  accentPurple: '#8B5CF6',

  // Surface
  surfaceCard:  '#FFFFFF',
  surfaceBorder:'#E5E5EA',
  surfaceInput: '#F2F2F7',

  // Chat
  bubbleUser:   '#007AFF',
  bubbleAgent:  '#E9E9EB',
  bubbleUserText:   '#FFFFFF',
  bubbleAgentText:  '#0A0A0A',

  // Status
  statusOnline: '#22C55E',
  statusAway:   '#F59E0B',
  statusOffline:'#8E8E93',
} as const;

// ============================================================================
// COLOR SCHEME HOOK
// ============================================================================

import { useColorScheme } from 'react-native';

export function useColors() {
  const scheme = useColorScheme();
  return scheme === 'dark' ? dark : light;
}

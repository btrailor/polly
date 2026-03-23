/**
 * Polly Design Tokens — React Native / Expo
 * Token-for-token parity with DESIGN_SYSTEM_RN.md
 * Copy-paste into app/theme.ts
 */

// ============================================================================
// COLORS
// ============================================================================

export const colors = {
  // Primary (Blue)
  primary: {
    50: "#eff6ff",
    100: "#dbeafe",
    200: "#bfdbfe",
    300: "#93c5fd",
    400: "#60a5fa",
    500: "#3b82f6",
    600: "#2563eb", // DEFAULT
    700: "#1d4ed8",
    800: "#1e40af",
    900: "#1e3a8a",
    950: "#172554",
  },

  // Accent (Orange) — #f0903b — Polly brand
  accent: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#f0903b", // DEFAULT
    700: "#c2410c",
    800: "#9a3412",
    900: "#7c2d12",
    950: "#431407",
  },

  // Success (Green)
  success: {
    50: "#f0fdf4",
    100: "#dcfce7",
    200: "#bbf7d0",
    300: "#86efac",
    400: "#4ade80",
    500: "#22c55e",
    600: "#16a34a", // DEFAULT
    700: "#15803d",
    800: "#166534",
    900: "#145231",
  },

  // Destructive (Red)
  destructive: {
    50: "#fef2f2",
    100: "#fee2e2",
    200: "#fecaca",
    300: "#fca5a5",
    400: "#f87171",
    500: "#ef4444",
    600: "#ef4444", // DEFAULT
    700: "#dc2626",
    800: "#b91c1c",
    900: "#7f1d1d",
  },

  // Warning (Yellow)
  warning: {
    50: "#fefce8",
    100: "#fffacd",
    200: "#feee9e",
    300: "#fde047",
    400: "#facc15",
    500: "#eab308",
    600: "#eab308", // DEFAULT
    700: "#ca8a04",
    800: "#a16207",
    900: "#713f12",
  },

  // Neutral (Slate)
  slate: {
    50: "#f8fafc",
    100: "#f1f5f9",
    200: "#e2e8f0",
    300: "#cbd5e1",
    400: "#94a3b8",
    500: "#64748b",
    600: "#475569",
    700: "#334155",
    800: "#1e293b",
    900: "#0f172a",
    950: "#020617",
  },

  // Semantic tokens (light mode defaults)
  background: "#f8fafc",
  foreground: "#1e293b",
  card: "#e4f0f0",
  border: "#d4e0eb",
  input: "#f1f5f9",
  muted: "#94a3b8",
  "muted-foreground": "#64748b",

  // Dark mode semantic tokens
  dark: {
    background: "#020617",
    foreground: "#f8fafc",
    card: "#0c1323",
    border: "#1e2b48",
    input: "#0f172a",
    muted: "#64748b",
    "muted-foreground": "#cbd5e1",
  },
};

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  0: 0,
  1: 4, // 4pt base
  2: 8,
  3: 12,
  4: 16, // DEFAULT
  6: 24,
  8: 32,
  12: 48,
  16: 64,
};

// Common spacing shortcuts
export const paddingCard = spacing[4];
export const paddingSection = spacing[6];
export const gapIconText = spacing[2];
export const marginSection = spacing[8];

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  // Display sizes (large headings)
  displayLarge: {
    fontSize: 34,
    lineHeight: 41,
    fontWeight: "700" as const,
  },
  displayMedium: {
    fontSize: 28,
    lineHeight: 34,
    fontWeight: "700" as const,
  },

  // Heading sizes
  headingLarge: {
    fontSize: 22,
    lineHeight: 28,
    fontWeight: "600" as const,
  },
  headingMedium: {
    fontSize: 20,
    lineHeight: 26,
    fontWeight: "600" as const,
  },
  headingSmall: {
    fontSize: 17,
    lineHeight: 22,
    fontWeight: "600" as const,
  },

  // Body sizes
  bodyLarge: {
    fontSize: 17,
    lineHeight: 26,
    fontWeight: "400" as const,
  },
  bodyMedium: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: "400" as const,
  },
  bodySmall: {
    fontSize: 15,
    lineHeight: 20,
    fontWeight: "400" as const,
  },

  // Caption sizes
  captionLarge: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: "400" as const,
  },
  captionMedium: {
    fontSize: 12,
    lineHeight: 16,
    fontWeight: "400" as const,
  },
  captionSmall: {
    fontSize: 11,
    lineHeight: 14,
    fontWeight: "400" as const,
  },

  // Code / Monospace
  monospaceSmall: {
    fontSize: 13,
    lineHeight: 18,
    fontWeight: "400" as const,
    fontFamily: "JetBrainsMono_400Regular",
  },
};

// ============================================================================
// BORDER RADIUS
// ============================================================================

export const borderRadius = {
  xs: 4,
  sm: 6,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

// ============================================================================
// SHADOWS (React Native)
// ============================================================================

export const shadows = {
  none: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0,
    shadowRadius: 0,
    elevation: 0,
  },
  sm: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  md: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  lg: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
};

// ============================================================================
// OPACITY / ALPHA
// ============================================================================

export const opacity = {
  disabled: 0.5,
  hover: 0.8,
  active: 0.7,
  focus: 0.9,
};

// ============================================================================
// COMPONENT-SPECIFIC PRESETS
// ============================================================================

/**
 * Pre-made style objects for common components
 * Use to avoid repeated color/spacing calculations
 */

export const componentStyles = {
  // Button styles
  buttonPrimary: {
    backgroundColor: colors.accent[600],
    borderRadius: borderRadius.lg,
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[6],
    ...shadows.sm,
  },
  buttonSecondary: {
    backgroundColor: "transparent",
    borderColor: colors.slate[300],
    borderWidth: 1,
    borderRadius: borderRadius.lg,
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[6],
  },
  buttonDestructive: {
    backgroundColor: colors.destructive[600],
    borderRadius: borderRadius.lg,
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[6],
  },

  // Card styles
  card: {
    backgroundColor: colors.card,
    borderRadius: borderRadius.lg,
    padding: spacing[4],
    ...shadows.sm,
  },
  cardDark: {
    backgroundColor: colors.dark.card,
    borderRadius: borderRadius.lg,
    padding: spacing[4],
    ...shadows.sm,
  },

  // Input styles
  input: {
    backgroundColor: colors.input,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: borderRadius.md,
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[3],
    fontSize: typography.bodyMedium.fontSize,
  },

  // List row
  listRow: {
    paddingVertical: spacing[3],
    paddingHorizontal: spacing[4],
    borderBottomColor: colors.border,
    borderBottomWidth: 1,
    minHeight: 56,
  },

  // Text styles
  textHeading: {
    fontSize: typography.headingLarge.fontSize,
    fontWeight: typography.headingLarge.fontWeight,
    color: colors.foreground,
    lineHeight: typography.headingLarge.lineHeight,
  },
  textBody: {
    fontSize: typography.bodyLarge.fontSize,
    fontWeight: typography.bodyLarge.fontWeight,
    color: colors.foreground,
    lineHeight: typography.bodyLarge.lineHeight,
  },
  textMuted: {
    fontSize: typography.captionLarge.fontSize,
    fontWeight: typography.captionLarge.fontWeight,
    color: colors["muted-foreground"],
    lineHeight: typography.captionLarge.lineHeight,
  },

  // Chat bubble (user)
  chatBubbleUser: {
    backgroundColor: colors.accent[600],
    borderRadius: borderRadius.lg,
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[3],
    maxWidth: "80%",
    alignSelf: "flex-end",
  },

  // Chat bubble (assistant)
  chatBubbleAssistant: {
    backgroundColor: colors.slate[200],
    borderRadius: borderRadius.lg,
    paddingVertical: spacing[2],
    paddingHorizontal: spacing[3],
    maxWidth: "80%",
    alignSelf: "flex-start",
  },

  // Status indicator
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: borderRadius.full,
  },
};

// ============================================================================
// CONVENIENCE FUNCTIONS
// ============================================================================

/**
 * Get semantic color based on system dark mode
 */
export function getSemanticColor(token: keyof typeof colors, isDark: boolean) {
  if (isDark && token in colors.dark) {
    return colors.dark[token as keyof typeof colors.dark];
  }
  return colors[token];
}

/**
 * Create a color with opacity
 * Usage: colorWithAlpha(colors.primary[600], 0.5) → rgba(...)
 */
export function colorWithAlpha(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Export all tokens as a single theme object
 */
export const theme = {
  colors,
  spacing,
  typography,
  borderRadius,
  shadows,
  opacity,
  componentStyles,
};

export default theme;

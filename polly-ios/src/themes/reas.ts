/**
 * Reas Theme
 * 
 * The default Phase 1A sensibility. Monospaced, instruction-set aesthetic.
 * Systematic, emergent thinking — present ideas as rule-sets that generate outcomes.
 * 
 * Color palette: Cool grays with warm accent. Precise, readable.
 * Typography: SF Mono (system), Courier fallback. Tight tracking.
 * Motion: Instant cuts, no easing. Jetset-adjacent minimalism.
 */

import { ThemeTokens } from './tokens';

export const reasTheme: ThemeTokens = {
  // ─── Colors ───
  // Cool, minimal palette — whites, near-blacks, focused accent
  bgPrimary: '#FFFFFF',           // Pure white canvas
  bgSecondary: '#F5F5F5',         // Near-white for elevated surfaces
  bgSurface: '#EEEEEE',           // Light gray for inputs, disabled
  
  textPrimary: '#1A1A1A',         // Near-black for body copy
  textSecondary: '#4A4A4A',       // Medium gray for labels
  textMuted: '#808080',           // Muted gray for disabled, placeholder
  
  accent: '#0066FF',              // Bright blue (action, highlight)
  accentSecondary: '#00CC99',     // Teal for secondary accents
  
  border: '#D0D0D0',              // Light gray dividers

  // ─── Shape / Radius ───
  // Tight, recessive — minimal ornamentation
  radiusSm: 4,                    // Small buttons, tags
  radiusMd: 6,                    // Input fields, cards
  radiusLg: 10,                   // Drawers, modals
  radiusBubble: 8,                // Chat bubble corners (slightly more rounded than surfaces)

  // ─── Typography ───
  // SF Mono: the system default for technical, instruction-set feel
  fontBody: 'SF Mono',
  fontMono: 'SF Mono',
  fontHeading: 'SF Mono',
  fontWeightHeading: '700',       // Bold headings, system weight
  
  letterSpacingBody: -0.3,        // Tight, dense reading (Reas is precise)

  // ─── Texture / Visual Effects ───
  // Phase 1A: solid color only. Textures ship Phase 3.
  textureOverlay: null,
  textureOpacity: 0,

  // ─── Motion ───
  // Instant, no easing — Reas is procedural and direct
  transitionMs: 0,                // No transition; instant cuts
  transitionEasing: 'linear',     // Placeholder (not used at 0ms)

  // ─── Chrome / UI Style ───
  // Minimal, functional
  dividerStyle: 'line',           // Simple 1pt line dividers
  shadowStyle: 'soft',            // Subtle elevation shadows
  bubbleStyle: 'rounded',         // Mild rounding on chat bubbles
};

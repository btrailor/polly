/**
 * Theme Token Types
 * 
 * Defines the complete interface for all theme properties.
 * Each theme (Reas, Fidenza, Ghost Box, etc.) implements this interface.
 * 
 * Import: import { ThemeTokens } from '../theme/tokens'
 */

export type BubbleStyle = 'rounded' | 'square' | 'ribbon' | 'stamp' | 'minimal' | 'stripe-edge' | 'thread';
export type ThemeTexture = 'grain' | 'canvas' | 'scan-lines' | 'dot-grid' | 'woven' | 'letterpress' | null;
export type DividerStyle = 'line' | 'gap' | 'none';
export type ShadowStyle = 'soft' | 'sharp' | 'none';
export type TransitionEasing = 'ease' | 'linear' | 'ease-in' | 'ease-out' | 'ease-in-out' | 'spring';

export interface ThemeTokens {
  // ─── Colors ───
  /** Primary background color (app canvas) */
  bgPrimary: string;
  
  /** Secondary background (elevated surfaces, cards) */
  bgSecondary: string;
  
  /** Tertiary surface (input fields, disabled areas) */
  bgSurface: string;
  
  /** Primary text color (body copy) */
  textPrimary: string;
  
  /** Secondary text color (labels, captions) */
  textSecondary: string;
  
  /** Muted text (disabled, placeholder) */
  textMuted: string;
  
  /** Primary accent color (buttons, highlights, focus states) */
  accent: string;
  
  /** Secondary accent (when two accent colors are needed) */
  accentSecondary: string;
  
  /** Border color (dividers, input borders) */
  border: string;

  // ─── Shape / Radius ───
  /** Small radius (small buttons, tags) */
  radiusSm: number;
  
  /** Medium radius (inputs, cards) */
  radiusMd: number;
  
  /** Large radius (drawers, modals) */
  radiusLg: number;
  
  /** Chat bubble corner radius */
  radiusBubble: number;

  // ─── Typography ───
  /** System font name for body text (e.g., "SF Pro", "SF Mono") */
  fontBody: string;
  
  /** Monospace font name (e.g., "SF Mono", "Courier New") */
  fontMono: string;
  
  /** Heading font name */
  fontHeading: string;
  
  /** Font weight for headings ("600", "700", "800") */
  fontWeightHeading: string;
  
  /** Letter spacing for body text (in points) */
  letterSpacingBody: number;

  // ─── Texture / Visual Effects ───
  /** Texture overlay pattern (grain, canvas, etc.) or null for solid */
  textureOverlay: ThemeTexture;
  
  /** Opacity of texture overlay (0.0–0.1) */
  textureOpacity: number;

  // ─── Motion ───
  /** Default transition duration in milliseconds */
  transitionMs: number;
  
  /** Easing function for transitions */
  transitionEasing: TransitionEasing;

  // ─── Chrome / UI Style ───
  /** Divider line style (line, gap between elements, or none) */
  dividerStyle: DividerStyle;
  
  /** Shadow style (soft, sharp drop shadow, or none) */
  shadowStyle: ShadowStyle;
  
  /** Chat bubble style variant */
  bubbleStyle: BubbleStyle;
}

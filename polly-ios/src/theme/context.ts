/**
 * Theme Context & Hooks
 * 
 * Provides global theme state and the useTheme() hook for consuming theme tokens.
 * 
 * Usage:
 *   1. Wrap your app root with <ThemeProvider>
 *   2. Call useTheme() in any component to access ThemeTokens
 *   3. Never hardcode color/radius values; always use theme tokens
 * 
 * Example:
 *   const { bgPrimary, textPrimary, accent } = useTheme();
 *   return <View style={{ backgroundColor: bgPrimary }} />;
 * 
 * Future: When more themes land (Phase 3), add a sensibility picker that
 * calls setActiveTheme(themeKey) to trigger app-wide re-render.
 */

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ThemeTokens } from './tokens';
import { reasTheme } from '../themes/reas';

// ─── Context ───
const ThemeContext = createContext<ThemeTokens | undefined>(undefined);

// ─── Provider Component ───
export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // Phase 1A: Reas is the only theme. setActiveTheme() is a Phase 3 feature.
  const [activeTheme] = useState<ThemeTokens>(reasTheme);

  return (
    <ThemeContext.Provider value={activeTheme}>
      {children}
    </ThemeContext.Provider>
  );
};

// ─── Hook ───
/**
 * useTheme()
 * 
 * Access active theme tokens in any functional component.
 * Throws if called outside ThemeProvider.
 * 
 * @returns {ThemeTokens} Current theme tokens (colors, typography, shapes, motion)
 * @throws {Error} If called outside <ThemeProvider>
 * 
 * Example:
 *   const { accent, bgPrimary, radiusMd } = useTheme();
 */
export function useTheme(): ThemeTokens {
  const theme = useContext(ThemeContext);
  if (!theme) {
    throw new Error(
      'useTheme() must be called within a <ThemeProvider>. ' +
      'Wrap your app root with <ThemeProvider> before using this hook.'
    );
  }
  return theme;
}

// ─── Export for external use ───
export { ThemeContext };

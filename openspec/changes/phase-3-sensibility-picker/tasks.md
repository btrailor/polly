# Phase 3: Full Sensibility Picker

**Status:** 💡 Specced  
**Gate:** Phase 2 sensibility behavior injection complete  
**Spec source:** `SENSIBILITY_SYSTEM_SPEC.md` §7 Phase 3; `POLLY_IOS_SPEC.md` §19

## Goal

Full sensibility picker ships. All 7 themes selectable. Theme-native transitions. Textures. 7 bubble styles. Per-theme typography. Theme-aware animation timing.

## Tasks

### Sensibility Picker UI
- [ ] Horizontal card scroll picker (§19.2) with live mini-preview per theme
- [ ] Instant theme switching with theme-native transition (transition style from active theme tokens)
- [ ] "Polly themes are dark by default. Jetset is the light-mode option." note in picker

### Texture Overlay
- [ ] 6 PNG texture assets (128×128): grain, canvas, scan-lines, dot-grid, woven, letterpress (~80KB total)
- [ ] Texture overlay component: `position: absolute` `<Image>` repeating tile above background, below content
- [ ] Per-theme opacity from `tokens.textureOpacity`
- [ ] Performance: verify 60fps on iPhone 13 with overlay active

### Bubble Styles
- [ ] `ChatBubble` branches on `tokens.bubbleStyle` (7 styles: rounded, square, ribbon, stamp, minimal, stripe-edge, thread)
- [ ] `ribbon`: borderRadius 0, borderLeftWidth 3, accent border (Ghost Box)
- [ ] `stamp`: borderRadius 2, borderWidth 1, border color (Martens)
- [ ] `minimal`: borderRadius 0, transparent background (Albers)
- [ ] `stripe-edge`: borderRadius 0, left striped pattern (Riley) — needs repeating gradient
- [ ] `thread`: borderRadius 0, dashed left border (Albers)
- [ ] Design review required for all non-rounded styles (@design_eng)

### Per-Theme Typography
- [ ] `fontBody`, `fontHeading`, `fontMono` from tokens applied to all text components
- [ ] `letterSpacingBody` applied to body text
- [ ] System font fallbacks when custom font unavailable
- [ ] Font loading (if custom fonts needed) via `expo-font`

### Theme-Aware Animation
- [ ] `StreamingCursor` blink rate reads from `tokens.transitionMs`
- [ ] Drawer animation reads from `tokens.transitionMs` + `tokens.transitionEasing`
- [ ] Screen transitions read from tokens
- [ ] Theme switch uses theme-native transition (Ghost Box: flicker; Fidenza: flowing ease; Jetset: cut)

## Done when
All 7 themes selectable and visually distinct. Textures render at 60fps. All bubble styles implemented and design-reviewed. Typography switches on theme change. @design_eng sign-off.

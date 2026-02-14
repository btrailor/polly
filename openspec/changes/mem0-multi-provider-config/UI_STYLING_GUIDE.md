# Provider Settings UI - Styling Guide

**Design System:** Clean, minimal, confidence-building  
**Inspiration:** Vercel, Linear, Raycast settings  
**Color Palette:** Monochrome with accent colors for status

---

## Color System

```css
:root {
  /* Base colors */
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-tertiary: #e9ecef;
  
  --text-primary: #1a1a1a;
  --text-secondary: #6c757d;
  --text-tertiary: #adb5bd;
  
  /* Accent colors */
  --accent-primary: #0070f3;
  --accent-success: #00d084;
  --accent-warning: #f5a623;
  --accent-error: #ff3b30;
  
  /* Status colors */
  --status-active: #00d084;
  --status-inactive: #adb5bd;
  --status-error: #ff3b30;
  --status-pending: #f5a623;
  
  /* Border & shadow */
  --border-color: #e1e4e8;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
}
```

---

## Component Styles

### Provider Card

```css
.provider-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all 0.2s ease;
  
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  
  /* Hover effect */
  &:hover {
    box-shadow: var(--shadow-md);
    border-color: var(--accent-primary);
    transform: translateY(-2px);
  }
}

.provider-card.compact {
  padding: var(--space-md);
  gap: var(--space-sm);
}

.card-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.provider-icon {
  font-size: 24px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.provider-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.configured {
  background: #d4f4e8;
  color: #00875a;
}

.status-badge.unconfigured {
  background: var(--bg-tertiary);
  color: var(--text-secondary);
}

.status-badge.error {
  background: #ffe5e5;
  color: #de350b;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
  flex: 1;
}

.provider-description {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.provider-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.tag {
  padding: 2px 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.provider-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-row .label {
  color: var(--text-tertiary);
}

.info-row .value {
  color: var(--text-primary);
  font-weight: 500;
}

.card-footer {
  display: flex;
  gap: var(--space-sm);
  padding-top: var(--space-md);
  border-top: 1px solid var(--bg-tertiary);
}

.link-external {
  color: var(--accent-primary);
  text-decoration: none;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    text-decoration: underline;
  }
}
```

### Button Styles

```css
.btn-primary {
  background: var(--accent-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: #0060df;
    transform: translateY(-1px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-secondary {
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-secondary);
    border-color: var(--text-secondary);
  }
}

.btn-success {
  background: var(--accent-success);
  color: white;
  /* Same structure as btn-primary */
}

.btn-danger {
  background: var(--accent-error);
  color: white;
  /* Same structure as btn-primary */
}
```

### Search & Filters

```css
.search-container {
  margin-bottom: var(--space-lg);
}

.provider-search-input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--bg-primary);
  transition: all 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 112, 243, 0.1);
  }
  
  &::placeholder {
    color: var(--text-tertiary);
  }
}

.filter-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-xl);
  padding: var(--space-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.filter-group {
  display: flex;
  gap: var(--space-sm);
  align-items: center;
}

.filter-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.filter-btn {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: var(--radius-sm);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-tertiary);
  }
  
  &.active {
    background: var(--accent-primary);
    color: white;
    border-color: var(--accent-primary);
  }
}

.sort-select {
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 13px;
  background: white;
  cursor: pointer;
  
  &:focus {
    outline: none;
    border-color: var(--accent-primary);
  }
}
```

### Configuration Modal

```css
.config-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-header {
  padding: var(--space-lg);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  
  &:hover {
    color: var(--text-primary);
  }
}

.modal-body {
  padding: var(--space-lg);
}

.config-step {
  margin-bottom: var(--space-xl);
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-sm);
}

.step-content {
  background: var(--bg-secondary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  font-size: 13px;
  line-height: 1.6;
}

.input-group {
  margin-bottom: var(--space-md);
}

.input-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.input-field {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-family: 'SF Mono', 'Monaco', monospace;
  
  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    box-shadow: 0 0 0 3px rgba(0, 112, 243, 0.1);
  }
}

.input-hint {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: var(--space-xs);
  display: flex;
  align-items: center;
  gap: 4px;
}

.test-results {
  background: #f0f9ff;
  border: 1px solid #0284c7;
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-top: var(--space-sm);
}

.test-results.success {
  background: #d4f4e8;
  border-color: #00875a;
}

.test-results.error {
  background: #ffe5e5;
  border-color: #de350b;
}

.modal-footer {
  padding: var(--space-lg);
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: var(--space-sm);
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

### Speed Indicator

```css
.speed-indicator {
  display: flex;
  gap: 2px;
}

.speed-bar {
  width: 4px;
  height: 12px;
  background: var(--bg-tertiary);
  border-radius: 2px;
}

.speed-bar.active {
  background: var(--accent-success);
}

/* Very fast: 4 bars */
.speed-very-fast .speed-bar:nth-child(-n+4) {
  background: var(--accent-success);
}

/* Fast: 3 bars */
.speed-fast .speed-bar:nth-child(-n+3) {
  background: var(--accent-success);
}

/* Medium: 2 bars */
.speed-medium .speed-bar:nth-child(-n+2) {
  background: var(--accent-warning);
}

/* Slow: 1 bar */
.speed-slow .speed-bar:nth-child(1) {
  background: var(--accent-error);
}
```

### Provider Grid Layout

```css
.providers-section {
  margin-top: var(--space-xl);
}

.provider-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--space-lg);
  margin-top: var(--space-md);
}

.provider-cards-horizontal {
  display: flex;
  gap: var(--space-md);
  overflow-x: auto;
  padding-bottom: var(--space-md);
  margin-top: var(--space-md);
}

.provider-cards-horizontal .provider-card {
  min-width: 300px;
  flex-shrink: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .provider-cards-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-container {
    flex-direction: column;
    gap: var(--space-md);
    align-items: stretch;
  }
}
```

### Recommended Section

```css
.recommended-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: var(--space-xl);
  border-radius: var(--radius-lg);
  color: white;
  margin-bottom: var(--space-xl);
}

.recommended-section h3 {
  margin: 0 0 var(--space-sm) 0;
  font-size: 20px;
}

.recommendation-reason {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: var(--space-lg);
}

.recommended-section .provider-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}
```

### Status Indicator

```css
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-dot.active {
  background: var(--accent-success);
}

.status-dot.inactive {
  background: var(--status-inactive);
}

.status-dot.error {
  background: var(--accent-error);
}

.status-dot.pending {
  background: var(--accent-warning);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
```

### Usage Stats

```css
.usage-stats {
  background: var(--bg-secondary);
  padding: var(--space-md);
  border-radius: var(--radius-md);
  margin-top: var(--space-md);
}

.usage-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--space-sm);
  font-size: 13px;
}

.usage-amount {
  font-weight: 600;
  color: var(--text-primary);
}

.usage-limit {
  color: var(--text-tertiary);
}

.usage-bar {
  height: 6px;
  background: var(--bg-tertiary);
  border-radius: 3px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-success), var(--accent-primary));
  transition: width 0.3s ease;
}

.usage-fill.warning {
  background: var(--accent-warning);
}

.usage-fill.danger {
  background: var(--accent-error);
}
```

---

## Dark Mode Support

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #1a1a1a;
    --bg-secondary: #2d2d2d;
    --bg-tertiary: #3d3d3d;
    
    --text-primary: #ffffff;
    --text-secondary: #a0a0a0;
    --text-tertiary: #707070;
    
    --border-color: #404040;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
  }
  
  .provider-card:hover {
    border-color: #505050;
  }
  
  .input-field {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }
  
  .btn-secondary {
    background: var(--bg-secondary);
    border-color: var(--border-color);
  }
}
```

---

## Microinteractions

```css
/* Smooth hover effects */
* {
  transition: all 0.2s ease;
}

/* Button click feedback */
button:active {
  transform: scale(0.98);
}

/* Loading spinner */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* Success checkmark animation */
@keyframes checkmark {
  0% {
    stroke-dashoffset: 50;
  }
  100% {
    stroke-dashoffset: 0;
  }
}

.checkmark {
  stroke-dasharray: 50;
  stroke-dashoffset: 50;
  animation: checkmark 0.5s ease forwards;
}

/* Slide-in notification */
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.notification {
  animation: slideInRight 0.3s ease;
}
```

---

## Accessibility

```css
/* Focus indicators */
*:focus-visible {
  outline: 2px solid var(--accent-primary);
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  :root {
    --border-color: #000;
  }
  
  .provider-card {
    border-width: 2px;
  }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Typography

```css
/* Font stack */
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Code/API key display */
.monospace {
  font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', 
               Consolas, 'Courier New', monospace;
}

/* Heading hierarchy */
h1 { font-size: 28px; font-weight: 700; line-height: 1.2; }
h2 { font-size: 22px; font-weight: 600; line-height: 1.3; }
h3 { font-size: 18px; font-weight: 600; line-height: 1.4; }
h4 { font-size: 16px; font-weight: 600; line-height: 1.4; }
```

---

This styling achieves:
- ✅ Clean, minimal aesthetic
- ✅ Clear visual hierarchy
- ✅ Smooth animations
- ✅ Dark mode support
- ✅ Full accessibility
- ✅ Professional polish

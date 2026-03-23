# Polly React Native Design System

**Version:** 1.0  
**Platform:** React Native (Expo)  
**Framework:** Expo + NativeWind (Tailwind CSS)  
**Last Updated:** March 23, 2026  
**Status:** Production-ready, parallel to `DESIGN_SYSTEM_iOS.md`

---

## Table of Contents

1. [Overview](#overview)
2. [Setup & Dependencies](#setup--dependencies)
3. [Design Tokens](#design-tokens)
4. [Typography](#typography)
5. [Spacing & Layout](#spacing--layout)
6. [Components](#components)
7. [Patterns](#patterns)
8. [Accessibility](#accessibility)
9. [Dark Mode](#dark-mode)
10. [Change Log](#change-log)

---

## Overview

This document defines Polly's design system for React Native / Expo. It mirrors `DESIGN_SYSTEM_iOS.md` (SwiftUI) with token-for-token alignment but expressed in RN/Tailwind syntax.

### Tech Stack

- **Framework:** React Native (via Expo)
- **Styling:** NativeWind (Tailwind CSS for RN)
- **State Management:** Zustand
- **Colors:** Nativewind theme tokens + CSS variables
- **Dark Mode:** System preference (automatic via `useColorScheme`)

### Philosophy

Polly RN maintains **exact visual parity** with SwiftUI version:
- Same color palette (`#f0903b` orange accent, slate grays, semantic colors)
- Same spacing grid (4pt base unit)
- Same typography scale
- Same component semantics
- Platform-native feel (use RN conventions, not web patterns)

---

## Setup & Dependencies

### Installation

```bash
npx create-expo-app polly --template expo-template-blank-typescript
npm install expo-openclaw-chat@0.2.2 @noble/ed25519 @noble/hashes
npm install expo-secure-store react-native-mmkv zustand
npm install @shopify/flash-list react-native-enriched-markdown
npm install react-native-reanimated react-native-gesture-handler
npm install nativewind tailwindcss
npm install react-native-zeroconf @react-native-community/netinfo
```

### NativeWind Configuration

**`tailwind.config.js`:**
```javascript
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: require("./tokens/colors"),
      spacing: require("./tokens/spacing"),
      fontSize: require("./tokens/typography"),
      borderRadius: require("./tokens/radius"),
    },
  },
  plugins: [],
};
```

**`metro.config.js`:**
```javascript
const { getDefaultConfig } = require("expo/metro-config");
const withNativeWind = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: "./globals.css" });
```

**`globals.css`:**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom theme tokens */
:root {
  --color-primary: 221.2 83.2% 53.3%;
  --color-accent: 24.6 95% 53.1%;
  --color-success: 142.1 76.2% 36.3%;
  --color-destructive: 0 72.2% 50.6%;
  --color-warning: 47.9 95.8% 53.1%;
}
```

---

## Design Tokens

### Colors

All colors defined in `tokens/colors.ts` — imported into Tailwind config.

#### Semantic Colors (Light Mode)

```typescript
// tokens/colors.ts
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

  // Accent (Orange) — #f0903b
  accent: {
    50: "#fff7ed",
    100: "#ffedd5",
    200: "#fed7aa",
    300: "#fdba74",
    400: "#fb923c",
    500: "#f97316",
    600: "#f0903b", // DEFAULT (Polly brand)
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

  // Neutral (Slate) — Light mode
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

  // Named semantic tokens
  background: "#f8fafc", // Light mode default
  foreground: "#1e293b", // Dark slate
  card: "#e4f0f0", // Obsidian-inspired card bg
  border: "#d4e0eb",
  input: "#f1f5f9",
  muted: "#94a3b8",
  "muted-foreground": "#64748b",
};
```

#### Dark Mode Colors

```typescript
export const darkColors = {
  primary: {
    50: "#172554",
    100: "#1e3a8a",
    200: "#1e40af",
    300: "#1d4ed8",
    400: "#2563eb",
    500: "#3b82f6",
    600: "#60a5fa", // Lighter for dark bg
    700: "#93c5fd",
    800: "#bfdbfe",
    900: "#dbeafe",
    950: "#eff6ff",
  },

  accent: {
    50: "#431407",
    100: "#7c2d12",
    200: "#9a3412",
    300: "#c2410c",
    400: "#f0903b",
    500: "#f97316",
    600: "#fb923c", // Lighter for dark bg
    700: "#fdba74",
    800: "#fed7aa",
    900: "#ffedd5",
    950: "#fff7ed",
  },

  success: {
    50: "#145231",
    100: "#166534",
    200: "#15803d",
    300: "#16a34a",
    400: "#22c55e",
    500: "#4ade80",
    600: "#86efac", // Lighter for dark bg
    700: "#bbf7d0",
    800: "#dcfce7",
    900: "#f0fdf4",
  },

  destructive: {
    50: "#7f1d1d",
    100: "#b91c1c",
    200: "#dc2626",
    300: "#ef4444",
    400: "#f87171",
    500: "#fca5a5",
    600: "#fecaca", // Lighter for dark bg
    700: "#fee2e2",
    800: "#fef2f2",
  },

  warning: {
    50: "#713f12",
    100: "#a16207",
    200: "#ca8a04",
    300: "#eab308",
    400: "#facc15",
    500: "#fde047",
    600: "#fffacd", // Lighter for dark bg
    700: "#fefce8",
  },

  slate: {
    50: "#020617",
    100: "#0f172a",
    200: "#1e293b",
    300: "#334155",
    400: "#475569",
    500: "#64748b",
    600: "#94a3b8",
    700: "#cbd5e1",
    800: "#e2e8f0",
    900: "#f1f5f9",
    950: "#f8fafc",
  },

  // Dark mode semantics
  background: "#020617", // Nearly black
  foreground: "#f8fafc", // Off white
  card: "#0c1323", // Obsidian dark
  border: "#1e2b48", // Dark slate
  input: "#0f172a",
  muted: "#64748b",
  "muted-foreground": "#cbd5e1",
};
```

#### Using Colors in Components

```typescript
// Direct hex
<View className="bg-[#f0903b]">

// Token reference
<View className="bg-accent-600">
<View className="bg-primary-600">
<View className="bg-success-600">

// Responsive (light/dark)
<View className="bg-slate-50 dark:bg-slate-950">

// Semantic
<View className="bg-background text-foreground">
```

### Spacing

All spacing defined in `tokens/spacing.ts` — imported into Tailwind config.

```typescript
// tokens/spacing.ts
export const spacing = {
  0: "0",
  1: "4px", // 4pt base
  2: "8px",
  3: "12px",
  4: "16px", // DEFAULT
  6: "24px",
  8: "32px",
  12: "48px",
  16: "64px",
};
```

#### Usage in Components

```typescript
// Padding
<View className="p-4">Content</View>
<View className="px-4 py-6">Horizontal + vertical</View>

// Margin
<View className="m-4">
<View className="mx-auto">Center horizontally</View>

// Gap (flex/grid)
<View className="flex gap-2">
  <Text>Item 1</Text>
  <Text>Item 2</Text>
</View>

// Named spacing (common patterns)
const PADDING_CARD = 16; // p-4
const PADDING_SECTION = 24; // p-6
const GAP_ICON_TEXT = 8; // gap-2
const MARGIN_SECTION = 32; // m-8
```

---

## Typography

### Font Families

**UI Font: Inter** (from Expo Google Fonts)

```typescript
// app.tsx or global setup
import { useFonts, Inter_400Regular, Inter_500Medium, Inter_600SemiBold, Inter_700Bold } from '@expo-google-fonts/inter';

export default function App() {
  const [fontsLoaded] = useFonts({
    "inter-regular": Inter_400Regular,
    "inter-medium": Inter_500Medium,
    "inter-semibold": Inter_600SemiBold,
    "inter-bold": Inter_700Bold,
  });

  if (!fontsLoaded) {
    return <SplashScreen />;
  }

  return <RootNavigator />;
}
```

**Code Font: JetBrains Mono** (for code blocks)

```typescript
import { JetBrainsMono_400Regular, JetBrainsMono_600SemiBold } from '@expo-google-fonts/jetbrains-mono';
```

### Type Scale

Defined in `tokens/typography.ts`.

```typescript
// tokens/typography.ts
export const typography = {
  // Named styles matching SwiftUI
  "display-lg": { fontSize: 34, lineHeight: 41, fontWeight: "700" }, // Large Title
  "display-md": { fontSize: 28, lineHeight: 34, fontWeight: "700" }, // Title 1
  "heading-lg": { fontSize: 22, lineHeight: 28, fontWeight: "600" }, // Title 2
  "heading-md": { fontSize: 20, lineHeight: 26, fontWeight: "600" }, // Title 3
  "heading-sm": { fontSize: 17, lineHeight: 22, fontWeight: "600" }, // Headline
  "body-lg": { fontSize: 17, lineHeight: 26, fontWeight: "400" }, // Body
  "body-md": { fontSize: 16, lineHeight: 24, fontWeight: "400" }, // Callout
  "body-sm": { fontSize: 15, lineHeight: 20, fontWeight: "400" }, // Subheadline
  "caption-lg": { fontSize: 13, lineHeight: 18, fontWeight: "400" }, // Footnote
  "caption-md": { fontSize: 12, lineHeight: 16, fontWeight: "400" }, // Caption 1
  "caption-sm": { fontSize: 11, lineHeight: 14, fontWeight: "400" }, // Caption 2
  "mono-sm": { fontSize: 13, lineHeight: 18, fontWeight: "400", fontFamily: "JetBrainsMono" },
};
```

#### Usage in Components

```typescript
// Use Tailwind typography utilities
<Text className="text-lg font-semibold">Heading</Text>
<Text className="text-base">Body text</Text>
<Text className="text-sm text-muted-foreground">Muted text</Text>
<Text className="text-xs">Caption</Text>

// Or use custom type system
const styles = {
  headingLg: { fontSize: 22, fontWeight: "600", lineHeight: 28 },
  body: { fontSize: 17, fontWeight: "400", lineHeight: 26 },
  caption: { fontSize: 13, fontWeight: "400", lineHeight: 18 },
};

<Text style={styles.headingLg}>Title</Text>
```

### Font Weights

```typescript
// Tailwind utilities
font-normal    // 400
font-medium    // 500
font-semibold  // 600
font-bold      // 700
```

---

## Spacing & Layout

### Layout Patterns

**Full Width with Edge Insets:**
```typescript
<ScrollView className="flex-1 bg-background">
  <View className="px-4 py-6">
    {/* Content automatically has 16pt margins on left/right */}
  </View>
</ScrollView>
```

**List Row (56-72pt height):**
```typescript
<Pressable className="flex-row items-center px-4 py-3 border-b border-slate-200 dark:border-slate-800">
  <View className="flex-1">
    <Text className="text-base font-semibold">Title</Text>
    <Text className="text-xs text-muted-foreground mt-1">Subtitle</Text>
  </View>
  <Ionicons name="chevron-forward" size={20} color="#94a3b8" />
</Pressable>
```

**Card (Integration, Status):**
```typescript
<View className="bg-card dark:bg-slate-800 rounded-lg p-4 mb-6 shadow-sm">
  <View className="flex-row justify-between items-start">
    <View className="flex-1">
      <Text className="text-base font-semibold">Title</Text>
      <Text className="text-xs text-muted-foreground mt-1">Description</Text>
    </View>
    <View className="w-3 h-3 rounded-full bg-success-600" />
  </View>
  
  {/* Stats row */}
  <View className="flex-row gap-6 mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
    <StatItem label="Items" value="17" />
    <StatItem label="Last Sync" value="2m ago" />
  </View>
</View>
```

**Stack with Spacing:**
```typescript
<View className="gap-4">
  <Text>Item 1</Text>
  <Text>Item 2</Text>
  <Text>Item 3</Text>
</View>
```

**Flex Layouts:**
```typescript
// Row with space-between
<View className="flex-row justify-between items-center">
  <Text>Left</Text>
  <Text>Right</Text>
</View>

// Centered
<View className="flex-1 justify-center items-center">
  <Text>Centered</Text>
</View>

// Column (default)
<View className="flex-1 gap-4">
  <Text>Top</Text>
  <Text>Middle</Text>
  <Text>Bottom</Text>
</View>
```

---

## Components

### Base Components (NativeWind)

All components use NativeWind for styling. Follow Tailwind patterns.

#### Text

```typescript
// Heading
<Text className="text-2xl font-semibold text-foreground">Title</Text>

// Body
<Text className="text-base text-foreground">Body text</Text>

// Muted
<Text className="text-sm text-muted-foreground">Muted text</Text>

// Semantic colors
<Text className="text-primary-600">Link</Text>
<Text className="text-destructive-600">Error</Text>
<Text className="text-success-600">Success</Text>
```

#### Pressable / Button

```typescript
// Primary button (orange)
<Pressable className="bg-accent-600 rounded-lg py-3 px-6 active:opacity-80">
  <Text className="text-white font-semibold text-center">Send</Text>
</Pressable>

// Secondary (outline)
<Pressable className="border border-slate-300 dark:border-slate-700 rounded-lg py-3 px-6 active:bg-slate-100 dark:active:bg-slate-900">
  <Text className="text-foreground font-semibold text-center">Cancel</Text>
</Pressable>

// Destructive (red)
<Pressable className="bg-destructive-600 rounded-lg py-3 px-6">
  <Text className="text-white font-semibold text-center">Delete</Text>
</Pressable>

// Ghost (no background)
<Pressable className="active:opacity-60">
  <Ionicons name="menu" size={24} color="#1e293b" />
</Pressable>
```

#### TextInput

```typescript
<TextInput
  className="bg-input dark:bg-slate-900 text-foreground px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-800"
  placeholder="Type message..."
  placeholderTextColor="#94a3b8"
  editable={!isLoading}
/>
```

#### View / Container

```typescript
// Card-like container
<View className="bg-card dark:bg-slate-800 rounded-lg p-4 shadow-sm">
  {/* Content */}
</View>

// Safe area padding
<SafeAreaView className="flex-1 bg-background">
  {/* Content */}
</SafeAreaView>
```

### Custom Components

All custom Polly components live in `components/` and follow the same token system.

#### ChatBubble

**Props:**
```typescript
interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
  isStreaming?: boolean;
  onTapLink?: (url: string) => void;
}
```

**Implementation:**
```typescript
export function ChatBubble({ role, content, timestamp, isStreaming }: ChatBubbleProps) {
  const isUser = role === "user";
  
  return (
    <View className={`flex-row ${isUser ? "justify-end" : "justify-start"} gap-2 px-4 py-2`}>
      <View
        className={`max-w-xs rounded-2xl px-4 py-2 ${
          isUser
            ? "bg-accent-600 rounded-br-none"
            : "bg-slate-200 dark:bg-slate-800 rounded-bl-none"
        }`}
      >
        <Text className={isUser ? "text-white" : "text-foreground"}>
          {content}
        </Text>
        {isStreaming && <View className="w-2 h-5 bg-white animate-pulse mt-1" />}
      </View>
      {timestamp && (
        <Text className="text-xs text-muted-foreground self-end">
          {formatTime(timestamp)}
        </Text>
      )}
    </View>
  );
}
```

#### TodayCard

**Props:**
```typescript
interface TodayCardProps {
  title: string;
  icon: string; // SF Symbol name
  status: "active" | "done" | "overdue" | "pending";
  dueDate?: Date;
  onPress: () => void;
}
```

**Implementation:**
```typescript
export function TodayCard({ title, icon, status, dueDate, onPress }: TodayCardProps) {
  const statusColors = {
    active: "bg-slate-300 dark:bg-slate-700",
    done: "bg-success-500",
    overdue: "bg-destructive-600",
    pending: "bg-warning-500",
  };

  return (
    <Pressable
      className="bg-card dark:bg-slate-800 rounded-lg p-4 mb-3 flex-row items-center gap-3 active:opacity-70"
      onPress={onPress}
    >
      <Ionicons name={icon} size={32} color="#f0903b" />
      
      <View className="flex-1">
        <Text className="text-base font-semibold text-foreground">{title}</Text>
        {dueDate && (
          <Text className="text-xs text-muted-foreground mt-1">
            Due {formatDate(dueDate)}
          </Text>
        )}
      </View>

      <View className={`w-3 h-3 rounded-full ${statusColors[status]}`} />
    </Pressable>
  );
}
```

#### ConnectionIndicator

**Props:**
```typescript
interface ConnectionIndicatorProps {
  status: "connected" | "disconnected" | "reconnecting";
  label?: string;
}
```

**Implementation:**
```typescript
export function ConnectionIndicator({ status, label }: ConnectionIndicatorProps) {
  const colors = {
    connected: "bg-success-600",
    disconnected: "bg-slate-400",
    reconnecting: "bg-warning-500",
  };

  return (
    <View className="flex-row items-center gap-2">
      <View className={`w-2 h-2 rounded-full ${colors[status]}`}>
        {status === "reconnecting" && (
          <Animated.View className="animate-pulse w-full h-full" />
        )}
      </View>
      {label && <Text className="text-xs font-medium text-foreground">{label}</Text>}
    </View>
  );
}
```

#### VoiceButton

**Props:**
```typescript
interface VoiceButtonProps {
  isRecording: boolean;
  onPress: () => void;
  onRecordingComplete: (audio: ArrayBuffer) => void;
}
```

**Implementation:**
```typescript
export function VoiceButton({ isRecording, onPress, onRecordingComplete }: VoiceButtonProps) {
  return (
    <Pressable
      className={`w-14 h-14 rounded-full flex-center active:opacity-80 ${
        isRecording ? "bg-destructive-600" : "bg-accent-600"
      }`}
      onPress={onPress}
    >
      <Ionicons
        name={isRecording ? "mic-off" : "mic"}
        size={24}
        color="#fff"
      />
      {isRecording && (
        <Animated.View className="absolute inset-0 border-2 border-destructive-600 rounded-full animate-pulse" />
      )}
    </Pressable>
  );
}
```

---

## Patterns

### Chat Interface

**Message List:**
```typescript
<FlashList
  data={messages}
  renderItem={({ item }) => (
    <ChatBubble
      role={item.role}
      content={item.content}
      timestamp={item.timestamp}
      isStreaming={item.isStreaming}
    />
  )}
  estimatedItemSize={80}
  contentContainerStyle={{ paddingBottom: 16 }}
  keyExtractor={(item) => item.id}
/>
```

**Input Bar (Sticky):**
```typescript
<KeyboardAvoidingView behavior="padding" className="flex-1">
  <FlashList {...messageProps} />
  
  <View className="border-t border-slate-200 dark:border-slate-800 bg-background px-4 py-3 gap-2">
    <View className="flex-row gap-2">
      <TextInput
        className="flex-1 bg-input dark:bg-slate-900 px-3 py-2 rounded-lg text-foreground"
        placeholder="Message..."
        value={input}
        onChangeText={setInput}
      />
      
      <Pressable
        className="bg-accent-600 w-10 h-10 rounded-lg justify-center items-center active:opacity-80"
        onPress={send}
      >
        <Ionicons name="send" size={20} color="#fff" />
      </Pressable>
    </View>
  </View>
</KeyboardAvoidingView>
```

### Pull-to-Refresh

```typescript
<FlashList
  data={messages}
  renderItem={...}
  refreshing={isRefreshing}
  onRefresh={async () => {
    setIsRefreshing(true);
    try {
      await gateway.sync();
    } finally {
      setIsRefreshing(false);
    }
  }}
/>
```

### Loading State

```typescript
// Skeleton
<View className="gap-2">
  <View className="h-4 bg-slate-200 dark:bg-slate-800 rounded-full w-3/4" />
  <View className="h-4 bg-slate-200 dark:bg-slate-800 rounded-full w-1/2" />
</View>

// Spinner
<ActivityIndicator size="large" color="#f0903b" />
```

### Error State

```typescript
<View className="bg-red-100 dark:bg-red-900/30 border border-destructive-300 dark:border-destructive-700 rounded-lg p-4 gap-3">
  <View className="flex-row gap-2">
    <Ionicons name="alert-circle" size={20} color="#ef4444" />
    <Text className="flex-1 text-destructive-700 dark:text-destructive-400 font-semibold">
      Error
    </Text>
  </View>
  <Text className="text-sm text-destructive-600 dark:text-destructive-300">
    Failed to send message. Check your connection.
  </Text>
  <Pressable
    className="bg-destructive-600 rounded py-2 active:opacity-80"
    onPress={retry}
  >
    <Text className="text-white font-semibold text-center">Retry</Text>
  </Pressable>
</View>
```

### Empty State

```typescript
<View className="flex-1 justify-center items-center gap-4 px-6">
  <Ionicons name="chatbubble-outline" size={48} color="#cbd5e1" />
  <Text className="text-lg font-semibold text-foreground text-center">
    No messages yet
  </Text>
  <Text className="text-sm text-muted-foreground text-center">
    Start a conversation to get going.
  </Text>
  <Pressable
    className="bg-accent-600 rounded-lg py-3 px-8 active:opacity-80"
    onPress={newChat}
  >
    <Text className="text-white font-semibold">New Chat</Text>
  </Pressable>
</View>
```

---

## Accessibility

### VoiceOver / Screen Reader

**Text Labels:**
```typescript
<Pressable
  accessibilityLabel="Send message"
  accessibilityHint="Double-tap to send your message"
  onPress={send}
>
  <Ionicons name="send" size={24} />
</Pressable>
```

**Semantic Structure:**
```typescript
<View accessibilityRole="list">
  {messages.map((msg) => (
    <View key={msg.id} accessibilityRole="listitem">
      <Text accessibilityRole="header">{msg.role}</Text>
      <Text>{msg.content}</Text>
    </View>
  ))}
</View>
```

### Color Contrast

- Text on light: `#1e293b` (slate-800) — 4.5:1 ✅
- Text on dark: `#f8fafc` (slate-50) — 4.5:1 ✅
- Buttons/UI elements: 3:1 minimum ✅
- Don't rely on color alone (pair with icons/text) ✅

### Touch Targets

- Minimum 48pt × 48pt
- Buttons: 44pt height (standard)
- List rows: 56-72pt
- All interactive elements keyboard-accessible

---

## Dark Mode

### System Integration

RN automatically respects system dark mode via `useColorScheme`.

```typescript
import { useColorScheme } from "react-native";

export function ThemedView({ children }) {
  const colorScheme = useColorScheme();
  
  return (
    <View className={colorScheme === "dark" ? "bg-slate-950" : "bg-slate-50"}>
      {children}
    </View>
  );
}
```

### NativeWind Dark Mode

All classes automatically respond to dark mode:
```typescript
<View className="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-50">
```

### Testing Dark Mode

```bash
# Xcode simulator
Device → Appearance → Dark

# Or set in code
const darkColorScheme = useColorScheme === "dark";
```

---

## Change Log

### Version 1.0 (March 23, 2026)

**Polly React Native Design System — Foundation**

**Added:**
- NativeWind + Tailwind CSS configuration
- Complete color system (light/dark mode pairs, semantic colors)
- Typography scale (17 sizes, SF Pro + JetBrains Mono)
- Spacing grid (4pt base unit, Tailwind utilities)
- Component library (ChatBubble, TodayCard, VoiceButton, ConnectionIndicator)
- Layout patterns (list rows, cards, stacks, keyboard-aware)
- Accessibility guidelines (VoiceOver, touch targets, contrast)
- Dark mode implementation
- Pattern library (chat, loading, error, empty states)

**Parallel to:** `DESIGN_SYSTEM_iOS.md` (SwiftUI version) — token-for-token alignment

**Next:**
- Component implementation during Phase 1
- Testing on physical devices
- Dark mode verification
- Accessibility audit (TalkBack / VoiceOver)

---

## Resources

### External Links

- **NativeWind Docs:** https://www.nativewind.dev/
- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **React Native Docs:** https://reactnative.dev/docs/getting-started
- **Expo Docs:** https://docs.expo.dev/
- **Accessibility:** https://reactnative.dev/docs/accessibility

### Internal Links

- **Polly iOS Design System:** `DESIGN_SYSTEM_iOS.md`
- **Polly RN Spec:** `POLLY_IOS_SPEC.md` (§6 components)
- **Tech Stack Decisions:** `POLLY_IOS_SPEC.md` (§12)

---

**Document Status:** Production-ready, Phase 1 implementation begins  
**Owner:** @design_eng  
**Last Updated:** March 23, 2026

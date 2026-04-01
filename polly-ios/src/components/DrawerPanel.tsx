/**
 * DrawerPanel — Custom animated drawer (§6.24)
 *
 * Uses Animated + PanGestureHandler from react-native-gesture-handler.
 * NOT @react-navigation/drawer — spec requirement.
 *
 * Opens: swipe right from left edge
 * Closes: swipe left or tap overlay
 */

import React, { useEffect, useRef } from 'react';
import {
  Animated,
  Dimensions,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import {
  GestureHandlerRootView,
  PanGestureHandler,
  PanGestureHandlerGestureEvent,
  State,
} from 'react-native-gesture-handler';
import { Users, MessageSquare } from 'lucide-react-native';
import { colors, spacing, layout, typography } from '../theme/colors';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface DrawerAgent {
  id: string;
  name: string;
}

export interface DrawerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectAgent: (id: string) => void;
  activeAgentId: string;
}

// ─── Constants ────────────────────────────────────────────────────────────────

const SCREEN_WIDTH = Dimensions.get('window').width;
// TODO: iPad adaptive layout — on iPad this should be a fixed 320pt sidebar, not 80% width
const DRAWER_WIDTH = SCREEN_WIDTH * 0.8;

const SWIPE_THRESHOLD = 50; // px to commit open/close
const OVERLAY_MAX_OPACITY = 0.5;

// Phase 1A placeholder agents
const PLACEHOLDER_AGENTS: DrawerAgent[] = [
  { id: 'assistant', name: 'Assistant' },
  { id: 'researcher', name: 'Researcher' },
  { id: 'writer', name: 'Writer' },
];

// ─── DrawerPanel ──────────────────────────────────────────────────────────────

export default function DrawerPanel({
  isOpen,
  onClose,
  onSelectAgent,
  activeAgentId,
}: DrawerPanelProps) {
  const translateX = useRef(new Animated.Value(-DRAWER_WIDTH)).current;
  const overlayOpacity = useRef(new Animated.Value(0)).current;

  // Derive overlay opacity from translateX
  const overlayOpacityDerived = translateX.interpolate({
    inputRange: [-DRAWER_WIDTH, 0],
    outputRange: [0, OVERLAY_MAX_OPACITY],
    extrapolate: 'clamp',
  });

  useEffect(() => {
    Animated.timing(translateX, {
      toValue: isOpen ? 0 : -DRAWER_WIDTH,
      duration: 280,
      useNativeDriver: true,
    }).start();
  }, [isOpen, translateX]);

  // ─── Gesture handler ──────────────────────────────────────────────────────

  const onGestureEvent = Animated.event(
    [{ nativeEvent: { translationX: translateX } }],
    { useNativeDriver: true }
  );

  const onHandlerStateChange = (event: PanGestureHandlerGestureEvent) => {
    if (event.nativeEvent.state === State.END) {
      const { translationX, velocityX } = event.nativeEvent;
      const currentBase = isOpen ? 0 : -DRAWER_WIDTH;
      const projected = currentBase + translationX;

      const shouldOpen =
        projected > -DRAWER_WIDTH + SWIPE_THRESHOLD || velocityX > 500;

      if (shouldOpen) {
        Animated.timing(translateX, {
          toValue: 0,
          duration: 200,
          useNativeDriver: true,
        }).start();
      } else {
        Animated.timing(translateX, {
          toValue: -DRAWER_WIDTH,
          duration: 200,
          useNativeDriver: true,
        }).start(() => {
          if (isOpen) onClose();
        });
      }
    }
  };

  // Don't render at all when fully closed and not animating
  if (!isOpen) {
    // Still render but invisible so gesture can detect swipe-from-edge
    // (handled by parent via hamburger or edge swipe area)
    return null;
  }

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="box-none">
      {/* Overlay */}
      <Animated.View
        style={[styles.overlay, { opacity: overlayOpacityDerived }]}
        pointerEvents={isOpen ? 'auto' : 'none'}
      >
        <Pressable style={StyleSheet.absoluteFill} onPress={onClose} />
      </Animated.View>

      {/* Drawer panel */}
      <PanGestureHandler
        onGestureEvent={onGestureEvent}
        onHandlerStateChange={onHandlerStateChange}
        activeOffsetX={[-10, 10]}
      >
        <Animated.View
          style={[
            styles.drawer,
            { width: DRAWER_WIDTH, transform: [{ translateX }] },
          ]}
        >
          {/* Team name */}
          <View style={styles.teamHeader}>
            <Users size={18} color={colors.accent} />
            <Text style={styles.teamName}>My Team</Text>
          </View>

          <View style={styles.divider} />

          {/* Agents section */}
          <Text style={styles.sectionLabel}>AGENTS</Text>
          <ScrollView style={styles.agentList} showsVerticalScrollIndicator={false}>
            {PLACEHOLDER_AGENTS.map((agent) => {
              const isActive = agent.id === activeAgentId;
              return (
                <TouchableOpacity
                  key={agent.id}
                  style={[styles.agentRow, isActive && styles.agentRowActive]}
                  onPress={() => onSelectAgent(agent.id)}
                  activeOpacity={0.7}
                >
                  <View style={[styles.agentDot, isActive && styles.agentDotActive]} />
                  <Text style={[styles.agentName, isActive && styles.agentNameActive]}>
                    {agent.name}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          <View style={styles.divider} />

          {/* TODAY section */}
          <Text style={styles.sectionLabel}>TODAY</Text>
          <View style={styles.emptySessionsContainer}>
            <MessageSquare size={20} color={colors.textSecondary} style={styles.emptyIcon} />
            <Text style={styles.emptySessionsText}>No recent sessions</Text>
          </View>
        </Animated.View>
      </PanGestureHandler>
    </View>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: '#000000',
  },
  drawer: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    backgroundColor: colors.bgSecondary,
    borderRightWidth: layout.borderDefault,
    borderRightColor: colors.bgBorder,
    paddingTop: 60, // safe area placeholder
    paddingBottom: spacing.spacing6,
  },
  teamHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing.spacing4,
    paddingVertical: spacing.spacing3,
    gap: spacing.spacing2,
  },
  teamName: {
    ...typography.headline,
    color: colors.textPrimary,
  },
  divider: {
    height: layout.borderThin,
    backgroundColor: colors.bgBorder,
    marginHorizontal: spacing.spacing4,
    marginVertical: spacing.spacing2,
  },
  sectionLabel: {
    ...typography.caption1,
    color: colors.textSecondary,
    letterSpacing: 0.8,
    paddingHorizontal: spacing.spacing4,
    paddingTop: spacing.spacing2,
    paddingBottom: spacing.spacing1,
  },
  agentList: {
    flex: 1,
    paddingHorizontal: spacing.spacing2,
  },
  agentRow: {
    flexDirection: 'row',
    alignItems: 'center',
    height: layout.listRowCompact,
    paddingHorizontal: spacing.spacing3,
    borderRadius: layout.cornerRadiusMedium,
    gap: spacing.spacing2,
    marginVertical: 2,
  },
  agentRowActive: {
    backgroundColor: colors.bgBorder,
  },
  agentDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.textSecondary,
  },
  agentDotActive: {
    backgroundColor: colors.accent,
  },
  agentName: {
    ...typography.callout,
    color: colors.textSecondary,
  },
  agentNameActive: {
    color: colors.textPrimary,
  },
  emptySessionsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.spacing6,
    gap: spacing.spacing2,
  },
  emptyIcon: {
    opacity: 0.4,
  },
  emptySessionsText: {
    ...typography.footnote,
    color: colors.textSecondary,
  },
});

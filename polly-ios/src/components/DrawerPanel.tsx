/**
 * DrawerPanel Gesture Layer
 * 
 * Animated drawer with PanGestureHandler for swipe-to-open/close.
 * Slides from left edge, ~80% screen width.
 * 
 * Usage:
 *   const [drawerOpen, setDrawerOpen] = useState(false);
 *   return <DrawerPanel open={drawerOpen} onToggle={setDrawerOpen}>
 *     <DrawerContent />
 *   </DrawerPanel>
 */

import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Animated,
  Pressable,
  Dimensions,
  StyleSheet,
  GestureResponderEvent,
} from 'react-native';
import {
  PanGestureHandler,
  PanGestureHandlerGestureEvent,
  GestureHandlerRootView,
} from 'react-native-gesture-handler';
import { useTheme } from '../theme/context';

const SCREEN_WIDTH = Dimensions.get('window').width;
const DRAWER_WIDTH = SCREEN_WIDTH * 0.8; // 80% of screen
const SWIPE_THRESHOLD = 50; // px to trigger open/close
const ANIMATION_DURATION = 300; // ms

interface DrawerPanelProps {
  /** Whether drawer is open */
  open: boolean;

  /** Callback when drawer should toggle */
  onToggle: (open: boolean) => void;

  /** Drawer content (team header, agent list, etc.) */
  children: React.ReactNode;

  /** Optional: custom drawer width (default: 80% of screen) */
  width?: number;
}

export const DrawerPanel: React.FC<DrawerPanelProps> = ({
  open,
  onToggle,
  children,
  width = DRAWER_WIDTH,
}) => {
  const theme = useTheme();

  // Animation values
  const translateX = useRef(new Animated.Value(open ? 0 : -width)).current;
  const overlayOpacity = useRef(new Animated.Value(open ? 0.5 : 0)).current;

  // Pan gesture state
  const panX = useRef(0);

  /**
   * Animate to target position (open or closed)
   */
  const animateTo = (targetOpen: boolean) => {
    const targetTranslateX = targetOpen ? 0 : -width;
    const targetOpacity = targetOpen ? 0.5 : 0;

    Animated.parallel([
      Animated.timing(translateX, {
        toValue: targetTranslateX,
        duration: ANIMATION_DURATION,
        useNativeDriver: false,
      }),
      Animated.timing(overlayOpacity, {
        toValue: targetOpacity,
        duration: ANIMATION_DURATION,
        useNativeDriver: false,
      }),
    ]).start(() => {
      if (!targetOpen) {
        // Reset pan tracking when fully closed
        panX.current = 0;
      }
    });

    onToggle(targetOpen);
  };

  /**
   * Handle pan gesture (swipe left/right)
   */
  const onPanGestureEvent = Animated.event(
    [
      {
        nativeEvent: {
          translationX: translateX,
        },
      },
    ],
    { useNativeDriver: false }
  );

  const onPanHandlerStateChange = (event: PanGestureHandlerGestureEvent) => {
    const { translationX, velocityX } = event.nativeEvent;
    panX.current = translationX;

    // Determine if we should open or close based on gesture
    const shouldOpen =
      translationX > SWIPE_THRESHOLD || // Swiped right past threshold
      velocityX > 500; // Quick swipe right

    const shouldClose =
      translationX < -SWIPE_THRESHOLD || // Swiped left past threshold
      velocityX < -500; // Quick swipe left

    if (shouldOpen && !open) {
      animateTo(true);
    } else if (shouldClose && open) {
      animateTo(false);
    } else {
      // Snap back to current state
      animateTo(open);
    }
  };

  // Update animation when `open` prop changes
  useEffect(() => {
    animateTo(open);
  }, [open]);

  const styles = StyleSheet.create({
    container: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      zIndex: 999,
      pointerEvents: open ? 'auto' : 'none',
    },
    drawerAnimated: {
      width,
      height: '100%',
      backgroundColor: theme.bgPrimary,
      shadowColor: theme.textPrimary,
      shadowOffset: { width: 2, height: 0 },
      shadowOpacity: 0.1,
      shadowRadius: 8,
      elevation: 5, // Android shadow
    },
    overlay: {
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: '#000',
      zIndex: -1,
    },
  });

  return (
    <GestureHandlerRootView style={styles.container}>
      {/* Animated overlay */}
      <Animated.View
        style={[
          styles.overlay,
          {
            opacity: overlayOpacity,
            pointerEvents: open ? 'auto' : 'none',
          },
        ]}
      >
        <Pressable
          style={{ flex: 1 }}
          onPress={() => onToggle(false)}
          accessible={false}
        />
      </Animated.View>

      {/* Drawer with pan gesture */}
      <PanGestureHandler
        onGestureEvent={onPanGestureEvent}
        onHandlerStateChange={onPanHandlerStateChange}
      >
        <Animated.View
          style={[
            styles.drawerAnimated,
            {
              transform: [{ translateX }],
            },
          ]}
        >
          {children}
        </Animated.View>
      </PanGestureHandler>
    </GestureHandlerRootView>
  );
};

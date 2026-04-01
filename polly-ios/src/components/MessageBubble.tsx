/**
 * MessageBubble
 * 
 * Chat message bubble with theme-driven styling.
 * Supports user (right) and assistant (left) alignment.
 * Applies BubbleStyle from active theme (Reas = rounded, Fidenza = organic, etc.)
 * 
 * Usage:
 *   <MessageBubble role="user" text="Hello" />
 *   <MessageBubble role="assistant" text="Hi there!" markdown />
 */

import React from 'react';
import { View, StyleSheet, Text } from 'react-native';
import MarkdownDisplay from 'react-native-markdown-display';
import { useTheme } from '../theme/context';

interface MessageBubbleProps {
  /** 'user' (right, blue) or 'assistant' (left, gray) */
  role: 'user' | 'assistant';

  /** Message text content */
  text: string;

  /** Whether to render markdown (default: false) */
  markdown?: boolean;

  /** Optional: streaming/typing indicator */
  isStreaming?: boolean;

  /** Optional: thinking content (collapsible) */
  thinking?: string;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  text,
  markdown = false,
  isStreaming = false,
  thinking,
}) => {
  const theme = useTheme();

  // Determine bubble color based on role
  const isUser = role === 'user';
  const bubbleColor = isUser ? theme.accent : theme.bgSecondary;
  const textColor = isUser ? '#FFFFFF' : theme.textPrimary;

  // Determine radius based on theme's BubbleStyle
  const radiusByBubbleStyle: Record<string, number> = {
    rounded: theme.radiusBubble,
    square: 0,
    ribbon: theme.radiusBubble,
    stamp: theme.radiusMd,
    minimal: theme.radiusSm,
    'stripe-edge': theme.radiusMd,
    thread: theme.radiusBubble,
  };

  const bubbleRadius = radiusByBubbleStyle[theme.bubbleStyle] || theme.radiusBubble;

  const styles = StyleSheet.create({
    bubbleContainer: {
      marginVertical: 4,
      marginHorizontal: 8,
      flexDirection: 'row',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
    },
    bubble: {
      maxWidth: '80%',
      paddingVertical: 10,
      paddingHorizontal: 12,
      borderRadius: bubbleRadius,
      backgroundColor: bubbleColor,
      borderWidth: isUser ? 0 : 1,
      borderColor: isUser ? bubbleColor : theme.border,
    },
    text: {
      fontSize: 16,
      lineHeight: 22,
      color: textColor,
      fontFamily: theme.fontBody,
    },
    streamingIndicator: {
      marginTop: 4,
      fontSize: 12,
      color: textColor,
      opacity: 0.7,
      fontStyle: 'italic',
    },
  });

  return (
    <View style={styles.bubbleContainer}>
      <View style={styles.bubble}>
        {/* Thinking content (collapsible, Phase 1B) */}
        {thinking && (
          <Text style={[styles.text, { fontSize: 12, marginBottom: 8, opacity: 0.7 }]}>
            💭 {thinking}
          </Text>
        )}

        {/* Main message content */}
        {markdown ? (
          <MarkdownDisplay
            style={{
              text: {
                fontSize: 16,
                lineHeight: 22,
                color: textColor,
                fontFamily: theme.fontBody,
              },
              code_inline: {
                backgroundColor: isUser ? 'rgba(255,255,255,0.1)' : theme.bgPrimary,
                color: textColor,
                fontFamily: theme.fontMono,
                fontSize: 14,
                paddingHorizontal: 4,
              },
              code_block: {
                backgroundColor: isUser ? 'rgba(255,255,255,0.1)' : theme.bgPrimary,
                color: textColor,
                fontFamily: theme.fontMono,
                fontSize: 13,
                padding: 8,
              },
              link: {
                color: isUser ? '#FFFFFF' : theme.accent,
              },
              hr: {
                borderColor: theme.border,
              },
            }}
          >
            {text}
          </MarkdownDisplay>
        ) : (
          <Text style={styles.text}>{text}</Text>
        )}

        {/* Streaming indicator */}
        {isStreaming && (
          <Text style={styles.streamingIndicator}>●●●</Text>
        )}
      </View>
    </View>
  );
};

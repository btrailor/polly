// gestures.tsx — Gesture Screen
// Phase 2 scaffold. Full implementation spec: GESTURE_LAYER.md §5
//
// Layout:
//   - List view of gesture library (fetched from gateway)
//   - Type filter tabs: Mode / Invocation / Transition / System
//   - Each entry: trigger phrase (top) + behavior summary + agent owner (bottom)
//   - Domain override indicator when present
//   - + button (nav bar right) → opens Gesture Builder conversation
//   - Tap to expand: all trigger phrases, full behavior, scope, usage stats
//   - Long-press: edit / delete
//
// Data model: GESTURE_LAYER.md §3.1

import { View, Text, StyleSheet, FlatList, TouchableOpacity, Pressable } from 'react-native';
import { colors } from '../../src/theme/colors';

// Gesture entry type matching GESTURE_LAYER.md §3.1
interface GestureOwnership {
  default_owner: string | null;
  domain_overrides: Record<string, string>;
  group_overrides: Array<{ group_id: string; owner: string }>;
}

interface GestureUsageStats {
  invocation_count: number;
  last_used: string | null;
  last_resolved_agent: string | null;
}

interface GestureEntry {
  id: string;
  source: 'system' | 'user';
  type: 'mode' | 'invocation' | 'transition';
  trigger_phrases: string[];
  behavior: string;
  owner: GestureOwnership;
  usage_stats: GestureUsageStats;
}

// Gesture type filter tabs
type GestureType = 'mode' | 'invocation' | 'transition' | 'system';

const FILTER_TABS: { key: GestureType | 'all'; label: string }[] = [
  { key: 'all', label: 'All' },
  { key: 'mode', label: 'Mode' },
  { key: 'invocation', label: 'Invocation' },
  { key: 'transition', label: 'Transition' },
  { key: 'system', label: 'System' },
];

// TODO (Phase 2): fetch gesture library from gateway
// GET /gestures → GestureEntry[]
// See GESTURE_LAYER.md §3.1 for full schema

export default function GesturesScreen() {
  // TODO (Phase 2): replace with gateway fetch via useGestureLibrary() hook
  const gestures: GestureEntry[] = [];
  const activeFilter: GestureType | 'all' = 'all';

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Gestures</Text>
        {/* + button → opens Gesture Builder conversation */}
        {/* TODO (Phase 2): navigate to Gesture Builder agent conversation */}
        <TouchableOpacity style={styles.addButton} accessibilityLabel="Add gesture">
          <Text style={styles.addButtonLabel}>+</Text>
        </TouchableOpacity>
      </View>

      {/* Type filter tabs */}
      <View style={styles.filterRow}>
        {FILTER_TABS.map((tab) => (
          <Pressable
            key={tab.key}
            style={[styles.filterTab, activeFilter === tab.key && styles.filterTabActive]}
            accessibilityRole="tab"
            accessibilityState={{ selected: activeFilter === tab.key }}
          >
            <Text
              style={[
                styles.filterTabLabel,
                activeFilter === tab.key && styles.filterTabLabelActive,
              ]}
            >
              {tab.label}
            </Text>
          </Pressable>
        ))}
      </View>

      {/* Gesture list */}
      {gestures.length === 0 ? (
        <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>No gestures yet.</Text>
          <Text style={styles.emptyStateSubtext}>
            Tap + to create your first gesture, or speak naturally — Polly will suggest gestures
            based on your patterns.
          </Text>
        </View>
      ) : (
        <FlatList
          data={gestures}
          keyExtractor={(item: any) => item.id}
          renderItem={({ item }: { item: GestureEntry }) => (
            // TODO (Phase 2): implement GestureRow component
            // Tap: expand (all trigger phrases, behavior, scope, usage stats)
            // Long-press: edit / delete action sheet
            <View style={styles.gestureRow}>
              <Text style={styles.gestureTrigger}>{item.trigger_phrases?.[0] ?? ''}</Text>
              <Text style={styles.gestureBehavior}>{item.behavior}</Text>
              <View style={styles.gestureMeta}>
                <Text style={styles.gestureOwner}>{item.owner?.default_owner ?? 'Ward'}</Text>
                {item.owner?.domain_overrides &&
                  Object.keys(item.owner.domain_overrides).length > 0 && (
                    <Text style={styles.domainOverrideBadge}>domain override</Text>
                  )}
              </View>
            </View>
          )}
          contentContainerStyle={styles.listContent}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 8,
  },
  headerTitle: {
    color: colors.textPrimary,
    fontSize: 22,
    fontWeight: '700',
  },
  addButton: {
    width: 36,
    height: 36,
    alignItems: 'center',
    justifyContent: 'center',
  },
  addButtonLabel: {
    color: colors.textPrimary,
    fontSize: 28,
    fontWeight: '300',
    lineHeight: 32,
  },
  filterRow: {
    flexDirection: 'row',
    paddingHorizontal: 12,
    paddingBottom: 8,
    gap: 4,
  },
  filterTab: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: colors.bgSecondary,
  },
  filterTabActive: {
    backgroundColor: colors.textPrimary,
  },
  filterTabLabel: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: '500',
  },
  filterTabLabelActive: {
    color: colors.bgPrimary,
  },
  emptyState: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 32,
  },
  emptyStateText: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    textAlign: 'center',
  },
  emptyStateSubtext: {
    color: colors.textSecondary,
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
  listContent: {
    paddingHorizontal: 16,
  },
  gestureRow: {
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.bgBorder,
    gap: 2,
  },
  gestureTrigger: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: '600',
  },
  gestureBehavior: {
    color: colors.textSecondary,
    fontSize: 13,
    lineHeight: 18,
  },
  gestureMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 2,
  },
  gestureOwner: {
    color: colors.textSecondary,
    fontSize: 12,
  },
  domainOverrideBadge: {
    color: colors.textSecondary,
    fontSize: 11,
    fontStyle: 'italic',
  },
});

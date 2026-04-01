# Domain Flexibility — Design

## Updated UserDomain Interface

```typescript
interface UserDomain {
  id: string;           // user-assigned, e.g. "code"
  name: string;         // display name, e.g. "Code"
  color: string;        // hex #RRGGBB
  icon: string;         // Lucide icon name
  keywords: string[];   // for client-side auto-detection
  order: number;
  suggested_mental_models?: string[];  // mental model IDs to surface when this domain is active (§11.3)
  default_sensibility?: string;        // sensibility ID to auto-switch when domain detected (Phase 4)
}
```

**Storage:** MMKV key `polly.domains` (unchanged). Both new fields are optional — existing records without them degrade gracefully (empty suggestion list, no auto-switch).

## Dynamic Suggestion Behavior (replaces hardcoded table)

When a domain badge is detected (§11.2), the mental model suggestion sheet (§11.3) reads `suggested_mental_models` from the matched `UserDomain` record. There is no name-keyed lookup. If `suggested_mental_models` is absent or empty, no suggestions are surfaced — the sheet shows only the full list.

**Priority order when both agent and domain suggestions present:** agent suggestions first, domain suggestions second, full list third. Duplicates deduplicated, shown in higher-priority slot.

## Default Starter Domains

At first run, Polly pre-populates `polly.domains` with starter domain records. These defaults include sensible `suggested_mental_models` and `default_sensibility` values sourced from the original design session. They are user data — editable and deletable. They are not app logic.

Default starters as shipped (subject to product refinement):

| id | name | suggested_mental_models | default_sensibility |
|----|------|------------------------|-------------------|
| `writing` | Writing / Notes | `freire_pedagogy`, `constraint_as_meaning`, `async_first` | — |
| `code` | Code | `first_principles`, `systems_thinking`, `reverse_engineering` | — |
| `audio` | Audio | `instruments_over_tracks`, `constraint_as_meaning` | — |
| `design` | Design | `instruments_over_tracks`, `chestertons_fence`, `inversion` | — |
| `systems` | Systems / Data | `systems_thinking`, `second_order_effects`, `chestertons_fence` | — |

> These are defaults, not app constants. A user who renames "Code" to "Sigils" and "Audio" to "Signals" gets identical behavior — the system reads their domain records, not hardcoded names.

## Cross-Feature Contract (schema change impact)

`UserDomain` is read by:
1. `DomainBadge` component (reads `keywords` for detection — unchanged)
2. Mental model suggestion sheet (§11.3) — now reads `suggested_mental_models` instead of a hardcoded table
3. Sensibility auto-switch engine (Phase 4) — will read `default_sensibility`

No other features depend on the `UserDomain` shape as of Phase 1.

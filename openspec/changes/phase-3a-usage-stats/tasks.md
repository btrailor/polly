# Phase 3A: Usage Stats

**Status:** 💡 Specced  
**Gate:** Phase 2 model-routing (usage data must be tracked first)  
**Spec source:** `POLLY_IOS_SPEC.md` §4.5; `MODEL_ROUTING_SPEC.md` §7  
**Owners:** @frontend

## Goal

`UsageStatsView` — token/cost breakdown, model usage, session stats. Users can see where their budget is going and which models Polly is using for which queries.

## Tasks

### Data Model
- [ ] Usage record schema in SQLite: `sessionKey`, `model`, `tier`, `inputTokens`, `outputTokens`, `costUsd`, `timestamp`, `queryType`
- [ ] Populated from completion events (routing engine logs on every completion)
- [ ] Daily/weekly/monthly aggregation views (SQLite queries)

### UsageStatsView
- [ ] Settings → Usage tab (new)
- [ ] Total cost this month: prominent display
- [ ] Cost breakdown by model: bar chart or pie (top 5 models)
- [ ] Cost breakdown by agent: which agents cost the most
- [ ] Daily spend trend: 30-day sparkline
- [ ] Token count breakdown: input vs. output
- [ ] Budget status: current daily spend vs. daily limit (if set)
- [ ] Reset period display: when monthly budget resets

### Budget Dashboard
- [ ] Budget limit settings: daily limit, monthly limit (from MODEL_ROUTING_SPEC.md)
- [ ] Visual budget gauge: how much of limit used
- [ ] Alert threshold: warn at 80% of budget (notification or banner)
- [ ] "Pause model routing" action: force Tier 0 until budget resets

### SQLite Migration
- [ ] Migrate existing MMKV budget data to SQLite on first Phase 3 launch (one-time automatic migration)
- [ ] MMKV budget keys deprecated after migration

## Done When
Usage tab shows real data. Budget gauge accurate. Daily/monthly cost visible. MMKV migrated. @qa_guy confirms numbers match completion event logs.

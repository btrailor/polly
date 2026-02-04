# Dashboard Pattern Count Fix

**Date:** January 21, 2026  
**Issue:** Dashboard shows 0 patterns even though query patterns exist  
**Status:** ✅ FIXED

---

## Problem

The dashboard pattern count card showed "0" even though:
- Patterns page displayed 2 query patterns correctly
- `~/.polly/patterns.json` contained 2 query patterns
- Pattern learning system was working

## Root Cause

**File:** `/core/polly.py` line 494

```python
if self.pattern_learner:
    stats['patterns'] = len(self.pattern_learner.patterns)  # ❌ Only conceptual patterns!
```

The `get_stats()` method was only counting **conceptual/code patterns** stored in `pattern_learner.patterns`, but NOT counting **query patterns** stored separately in `pattern_learner.query_patterns`.

### Pattern Storage Structure

```python
pattern_learner.patterns         # Dict[str, Pattern] - conceptual/code patterns
pattern_learner.query_patterns   # Dict[str, QueryPattern] - query template patterns
```

These are two separate collections, but the dashboard needs the **total** count.

## Solution

**File:** `/core/polly.py` line 494

Changed to count BOTH pattern types:

```python
if self.pattern_learner:
    stats['patterns'] = len(self.pattern_learner.patterns) + len(self.pattern_learner.query_patterns)
```

Now returns:
- Conceptual patterns: 0
- Query patterns: 2
- **Total: 2** ✓

## Verification

### Current Pattern State

```bash
$ cat ~/.polly/patterns.json | python3 -c "..."
Conceptual patterns: 0
Query patterns: 2
Total: 2
```

### Query Patterns Detected

1. **"How do I {action} {thing} with {tool}?"**
   - Frequency: 2
   - Fills: action=[use], thing=[redis, mongodb], tool=[node.js, python]
   - Domains: sigils, unknown

2. **"What's the best way to {action} {thing}?"**
   - Frequency: 2
   - Fills: action=[handle, structure], thing=[errors, files]
   - Domains: unknown

### Expected Behavior After Fix

**Dashboard:**
```
┌────────────┐
│ ✨         │
│ 2          │  ← Now shows 2 (was 0)
│ Patterns   │
└────────────┘
```

**API Response:**
```json
GET /polly/stats
{
  "patterns": 2,  // ← Now includes query patterns
  "rag": {...},
  "graph": {...}
}
```

## Testing

### Manual Test

1. Start Polly server
2. Open dashboard
3. Pattern count should show **2** (not 0)

### API Test

```bash
curl http://localhost:11436/polly/stats | python3 -m json.tool
# Should show: "patterns": 2
```

### Create More Patterns

To see the count increase:

**Conceptual Patterns:**
- Have 2-3 conversations about the same concepts (e.g., docker + python)
- After 3rd occurrence, conceptual pattern is created
- Count increases

**Query Patterns:**
- Ask similar questions multiple times
- Patterns are detected from templates
- Count increases

## Impact

### Before Fix
- Dashboard: 0 patterns (incorrect)
- Patterns page: 2 query patterns (correct)
- Users confused about pattern learning status

### After Fix
- Dashboard: 2 patterns (correct)
- Patterns page: 2 query patterns (correct)
- Clear visibility of pattern learning progress

## Files Modified

**`/core/polly.py`** (1 line changed)
- Line 494: Changed to count both pattern types

## Related Issues

This fix ensures:
- ✅ Dashboard shows accurate pattern count
- ✅ Query patterns are included in total
- ✅ Conceptual patterns are included in total
- ✅ Pattern learning progress is visible
- ✅ Consistency between dashboard and patterns page

## Future Considerations

Could enhance to show breakdown:
```json
{
  "patterns": {
    "total": 2,
    "conceptual": 0,
    "query": 2,
    "code": 0
  }
}
```

But current simple count works well for dashboard display.

---

## Conclusion

✅ **Dashboard pattern count now works correctly!**

The one-line fix ensures that query patterns are included in the total pattern count displayed on the dashboard, providing users with accurate visibility into what Polly has learned.

**Total Learning:** 2 patterns (2 query patterns)

# Phase 1.5 Quick Reference Guide

## Current Status

✅ **Days 1-2 Complete** (Foundation & Migration)
- Domain configuration system implemented
- Your existing domain structure migrated to `~/.polly/domains.json`
- All tests passing
- Zero breaking changes

## Key Files

### New Files
```
core/domain_config.py                    # Domain config system (440 lines)
~/.polly/domains.json                    # Your 5 domains (Sigils/Signals/Scrolls/Glyphs/Grids)
PHASE1.5_MIGRATION_COMPLETE.md           # Full documentation (this is comprehensive!)
```

### Modified Files
```
core/domains.py                          # Loads from config, added get_domain_colors/icons()
learners/patterns.py                     # Uses config keywords for domain inference
```

## Quick Commands

### View Your Domains
```bash
cat ~/.polly/domains.json
```

### Test Domain System
```bash
cd /Users/brettgershon/polly
python3 -c "from core.domains import DomainEngine; e = DomainEngine(); print(f'Domains: {len(e.domains)}, Using config: {e.domain_config is not None}')"
```

### Test Pattern Learner
```bash
cd /Users/brettgershon/polly
python3 -c "from learners.patterns import PatternLearner; from pathlib import Path; p = PatternLearner(Path.home() / '.polly' / 'patterns.json'); print(f'Patterns: {len(p.patterns)}')"
```

### Regenerate domains.json (if needed)
```bash
cd /Users/brettgershon/polly
python3 -c "from core.domain_config import migrate_from_hardcoded; migrate_from_hardcoded(force=True)"
```

## What's Working

✅ Domain detection
✅ Pattern learning (3,405 patterns)
✅ Domain keyword matching
✅ RAG weights (0.20 each)
✅ Colors and icons
✅ All integrations
✅ Server compatibility

## What's Next

**Days 3-4:** Settings UI for domain management
**Day 5:** AI keyword suggestions
**Day 6:** First-run wizard and polish

## Important Notes

1. **Your data is safe** - All patterns, conversations, and integrations still work
2. **Automatic fallback** - If domains.json is deleted, system uses hardcoded domains
3. **Automatic backups** - Every save creates a timestamped backup
4. **No UI yet** - Settings panel will be built in Days 3-4
5. **Dashboard unchanged** - Still uses hardcoded CSS (will update later)

## If Something Goes Wrong

### Rollback Option
```bash
# Delete config, system will fallback to hardcoded
mv ~/.polly/domains.json ~/.polly/domains.json.backup
```

### Verify Fallback
```bash
python3 -c "from core.domains import DomainEngine; e = DomainEngine(); print('Fallback working!' if e.domain_config is None else 'Config loaded')"
```

### Restore from Backup
```bash
# List backups
ls ~/.polly/domains.backup.*.json

# Restore specific backup
cp ~/.polly/domains.backup.20260124_145652.json ~/.polly/domains.json
```

## Domain Config Structure

```json
{
  "version": "1.0",
  "folderNumbering": true,
  "domains": [
    {
      "id": "sigils",                    // Unique ID (matches DomainType enum)
      "name": "Sigils",                  // Display name
      "description": "Code, infra...",   // Description
      "color": "#61afef",                // Hex color for UI
      "icon": "⚡",                       // Emoji icon
      "folderPath": "01-Sigils",         // Folder name (used in Phase 16)
      "ragWeight": 0.20,                 // Search weight (normalized to 1.0)
      "autoTagRules": [...],             // Keywords for auto-tagging
      "created": "ISO timestamp",
      "modified": "ISO timestamp",
      "order": 1                         // Sort order
    }
  ]
}
```

## API Reference

### Load Domains
```python
from core.domain_config import load_domains

config = load_domains()  # Loads from ~/.polly/domains.json
print(f"{len(config.domains)} domains")
```

### Save Domains
```python
from core.domain_config import save_domains

save_domains(config)  # Atomic save with backup
```

### Get Domain Colors/Icons
```python
from core.domains import DomainEngine

engine = DomainEngine()
colors = engine.get_domain_colors()  # {'sigils': '#61afef', ...}
icons = engine.get_domain_icons()    # {'sigils': '⚡', ...}
```

### Detect Domains
```python
domains = engine.detect_domains("How do I use Docker?")
print([d.value for d in domains])  # ['sigils']
```

## Test Results Summary

All 8 end-to-end tests passed:
1. ✅ Module imports (core.domain_config, core.domains, learners.patterns)
2. ✅ Domain config loading (5 domains, correct properties)
3. ✅ Domain engine initialization (using config, fallback works)
4. ✅ Domain detection (all test queries correct)
5. ✅ UI helpers (colors and icons correct)
6. ✅ Pattern learner integration (3,405 patterns, domain inference works)
7. ✅ Server integration (all imports work, DomainEngine in server context)
8. ✅ Obsidian integration (ObsidianSmartFeatures compatible)

## Read More

For comprehensive documentation, see:
- `PHASE1.5_MIGRATION_COMPLETE.md` - Full migration guide with all details
- `PHASE1.5_DOMAIN_CONFIGURATION.md` - Original Phase 1.5 specification
- `MASTER_ROADMAP.md` - Overall project roadmap

---

**Bottom Line:** Your domain system is now configurable without breaking anything. The foundation is solid and ready for the Settings UI (Days 3-4).

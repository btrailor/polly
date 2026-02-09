# 🚀 Start Phase 17 POC

## Quick Start

Run this command in your terminal:

```bash
/Users/brettgershon/polly/scripts/start-phase17-poc.sh
```

Or copy and paste the commands from `PHASE17_POC_EXECUTE_NOW.md`

---

## What This Will Do

1. ✅ Clone VSCodium repository (~500MB, several minutes)
2. ✅ Set up upstream remote for tracking updates
3. ✅ Create `polly-integration` branch
4. ✅ Document base state
5. ✅ Create fork directory structure
6. ✅ Install dependencies (10-20 minutes)
7. ✅ Build VSCodium (5-10 minutes)

**Total time:** ~30-40 minutes

---

## After Setup

Once the fork is set up and building:

1. **Test the build:**
   ```bash
   # Terminal 1
   yarn watch
   
   # Terminal 2
   ./scripts/code.sh
   ```

2. **Begin ribbon integration:**
   - Read: `docs/planning/phases/other/PHASE17_POC_RIBBON_INTEGRATION.md`
   - Study activity bar code
   - Start porting Polly ribbon

3. **Track progress:**
   - Use: `docs/planning/phases/other/PHASE17_POC_EXECUTION_LOG.md`

---

## Documentation

All documentation is in: `docs/planning/phases/other/`

- `PHASE17_POC_SETUP.md` - Detailed setup guide
- `PHASE17_POC_RIBBON_INTEGRATION.md` - Ribbon integration
- `PHASE17_POC_CHAT_INTEGRATION.md` - Chat panel integration
- `PHASE17_POC_EXECUTION_LOG.md` - Progress tracking

---

**Ready to start!** Run the script above or follow `PHASE17_POC_EXECUTE_NOW.md`

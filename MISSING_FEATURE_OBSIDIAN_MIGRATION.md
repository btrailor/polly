# Missing Feature: Obsidian → Native Polly Notes Migration

**Status:** Not Implemented  
**Priority:** High (User Experience - Onboarding)  
**Discovered:** January 28, 2026  
**Use Case:** Pure migration strategy for new users

---

## The Problem

**Current State:**
- Users can use Obsidian vault as a source (`source: obsidian`)
- Users can use native Polly notes (`source: native`)
- Users can **manually** switch between sources in config.yaml

**What's Missing:**
- ❌ No UI for importing/migrating Obsidian vault to Polly
- ❌ No "one-click" migration from Obsidian → native
- ❌ No validation step before migration
- ❌ No progress indicator during migration
- ❌ No way to preview what will be migrated

**User Impact:**
A new user who wants to **fully migrate** from Obsidian to Polly has no clear path. They must:
1. Manually edit config.yaml
2. Manually copy files
3. Hope everything works
4. Or remain dependent on Obsidian

---

## User Story

> **As a new Polly user coming from Obsidian,**  
> **I want to migrate my existing vault into Polly's native notes system,**  
> **So that I can use Polly as my primary note-taking tool without depending on Obsidian.**

**Acceptance Criteria:**
- ✅ User can browse to their Obsidian vault in Polly UI
- ✅ User sees a preview of what will be migrated (file count, features used)
- ✅ User sees warnings about unsupported features (Canvas, Dataview, etc.)
- ✅ User clicks "Migrate to Polly" button
- ✅ Migration happens with progress indicator
- ✅ User's notes appear in native Polly notes
- ✅ Config automatically switches to `source: native`
- ✅ User can continue working in Polly without Obsidian

---

## Current Workaround (Manual)

**Step 1: Validate Vault**
```bash
POST /polly/notes/validate
{
  "vault_path": "/path/to/obsidian/vault"
}
```

**Step 2: Copy Files Manually**
```bash
cp -r /path/to/obsidian/vault/* ~/.polly/notes/
```

**Step 3: Edit config.yaml**
```yaml
notes:
  source: native  # Changed from obsidian
  native:
    path: ~/.polly/notes
```

**Step 4: Restart Polly**

**Issues:**
- Requires technical knowledge
- Error-prone (file permissions, special characters)
- No progress feedback
- No rollback if fails

---

## Proposed Solution: Migration UI + Endpoint

### Phase 16D: Obsidian Migration Flow (2-3 days)

**New Endpoint: `/polly/notes/migrate-from-obsidian`**

```python
@app.post("/polly/notes/migrate-from-obsidian")
async def migrate_from_obsidian(request: Dict[str, Any]):
    """
    Migrate Obsidian vault to native Polly notes.
    
    Request: {
        "vault_path": "/path/to/obsidian/vault",
        "target_path": "~/.polly/notes",  # Optional, uses config default
        "options": {
            "copy_attachments": true,
            "preserve_structure": true,
            "convert_dataview": "remove",  # "remove", "preserve", "convert"
            "switch_source": true  # Auto-switch to native after migration
        }
    }
    
    Response: {
        "status": "started",
        "migration_id": "mig_123",
        "estimated_duration": "30s"
    }
    
    Progress via: GET /polly/notes/migrate/{migration_id}/status
    """
```

**Implementation:**
1. Validate source vault (POST `/polly/notes/validate`)
2. Copy files with progress tracking
3. Handle special cases:
   - Canvas files → skip with warning
   - Dataview queries → convert or remove
   - Attachments → copy to assets folder
   - Templates → copy to templates folder
4. Update NotesIndex
5. Update RAG collection
6. Update config.yaml (`source: native`)
7. Return success with stats

**UI Integration: Settings → Notes → Migration Tab**

```
┌─────────────────────────────────────────────────────┐
│ 📦 Migrate from Obsidian                            │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Current Source: Obsidian                            │
│ Vault Path: /Users/.../Organizer                   │
│                                                      │
│ ⚠️  Warnings:                                        │
│   • 3 Canvas files will be skipped                  │
│   • 12 Dataview queries detected                    │
│                                                      │
│ 📊 Migration Preview:                               │
│   • 87 notes will be migrated                       │
│   • 15 attachments will be copied                   │
│   • 5 templates will be preserved                   │
│                                                      │
│ Options:                                             │
│ ☑ Copy attachments and images                       │
│ ☑ Preserve folder structure                         │
│ ☐ Convert Dataview queries (experimental)           │
│ ☑ Switch to native notes after migration            │
│                                                      │
│ [ Cancel ]              [ Start Migration → ]       │
└─────────────────────────────────────────────────────┘
```

**Progress Modal:**
```
┌─────────────────────────────────────────────────────┐
│ 🔄 Migrating from Obsidian...                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│ [████████████████░░░░░░] 72% (63/87 notes)          │
│                                                      │
│ Current: Copying "Infinite Games Framework.md"      │
│                                                      │
│ ✅ 63 notes migrated                                │
│ ✅ 12 attachments copied                            │
│ ⚠️  3 Canvas files skipped                          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Integration with Existing Features

### Phase 16 (Native Notes) ✅
- Migration populates native notes directory
- NotesIndex automatically indexes migrated notes
- Notes appear immediately in UI

### Phase 0.5 (Obsidian Integration) ✅
- Validation endpoint already exists
- Can detect Canvas, Dataview, etc.
- Returns compatibility report

### Phase 21 (Deduplication) 🚧 In Progress
- After migration, dedup works on native notes
- No changes needed

---

## Files to Create/Modify

### New Files
- `/core/notes_migrator.py` (~300 lines) - Migration logic
  - `ObsidianMigrator` class
  - `migrate_vault()` method
  - Progress tracking
  - Rollback on failure

### Modified Files
- `/interfaces/server.py` (+150 lines)
  - POST `/polly/notes/migrate-from-obsidian` endpoint
  - GET `/polly/notes/migrate/{id}/status` endpoint
  - POST `/polly/notes/migrate/{id}/cancel` endpoint
- `/electron-app/src/renderer/index.html` (+120 lines)
  - Migration tab in Settings → Notes
  - Progress modal
- `/electron-app/src/renderer/app.js` (+200 lines)
  - Migration UI logic
  - Progress polling
  - Success/error handling

**Total Effort:** 2-3 days (similar to Phase 16 original)

---

## Alternative: Simpler "Import and Switch" Flow

If full migration is too complex for v1, we could do a simpler approach:

**Step 1: Copy files (background job)**
```python
POST /polly/notes/import-obsidian
{
  "vault_path": "/path/to/vault",
  "mode": "copy"  # or "move"
}
```

**Step 2: Switch source (immediate)**
```python
POST /polly/notes/source/switch
{
  "new_source": "native"
}
```

**UI: Single Button in Settings**
```
Current Source: Obsidian
Vault Path: /Users/.../Organizer

[ Import Obsidian Vault and Switch to Native Notes → ]
```

This is simpler but less polished (no validation, no progress, no options).

---

## Recommendation

**For v1 (MVP):**
Implement the **simpler "Import and Switch" flow** (1 day):
- One button: "Migrate to Native Notes"
- Copies files in background
- Shows toast notification when done
- Auto-switches source
- Good enough for early users

**For v1.1 (Polish):**
Implement the **full migration flow** (2-3 days):
- Validation step
- Preview with warnings
- Options and customization
- Progress tracking
- Better UX

---

## Related Issues

This connects to:
- **Phase 16** - Native notes system needs migration path
- **Phase 0.5** - Obsidian integration provides validation
- **Onboarding** - New users need clear migration story
- **Marketing** - "Move to Polly" is a key value prop

---

## Decision Needed

**Question:** Should we build this now, or wait until after Phase 21 (Deduplication)?

**Option A: Build Now** (Recommended)
- Fixes critical onboarding gap
- Enables "pure Polly" use case
- Unlocks marketing message: "Leave Obsidian behind"
- Delays Phase 21 by 1-2 days

**Option B: Build After Phase 21**
- Complete deduplication first
- Then add migration flow
- More cohesive feature rollout
- Dedup works on both Obsidian and native

**Option C: Defer to v1.1**
- Ship Phase 21 first
- Document manual migration steps
- Build proper migration UI later
- Focus on core features for v1

---

**Current Status:** Documented, not prioritized. Waiting for decision.

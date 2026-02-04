# Obsidian Integration Enhancement Plan

## Current State (Feb 1, 2026)

**Status:** Polly now uses **native knowledge base** by default for all note operations.

### What Changed

1. **Config Updated** (`config.yaml`)
   - `notes.source` changed from `"obsidian"` to `"native"`
   - `notes.native.enabled` changed from `false` to `true`
   - Templates copied to native notes: `~/.polly/notes/.polly/templates/`

2. **Note Creation Flow**
   - Scribe persona → Creates notes in native KB (`~/.polly/notes/`)
   - Manual note creation → Creates notes in native KB
   - Template system → Works with native KB

3. **API Endpoints**
   - `/polly/notes/create` → Uses `NotesSourceManager` (respects `notes.source` config)
   - `/polly/obsidian/create-note` → Still exists but not used by Scribe

### Benefits of Current Approach

✅ **Predictable behavior** - All notes go to one location  
✅ **No vault conflicts** - No accidental writes to Obsidian vault  
✅ **Faster indexing** - Native KB is optimized for Polly  
✅ **Template consistency** - Same templates for AI and manual flows  
✅ **Clean separation** - Obsidian vault remains read-only reference  

---

## Future Enhancement: Elegant Obsidian Integration

### Vision

Allow users to **optionally** have Scribe write directly to their Obsidian vault with the same quality and intelligence as native notes, while maintaining vault structure and conventions.

### Proposed Approach

#### Phase 1: Configuration & UI

**Goal:** Make it easy to toggle between native and Obsidian destinations

**Tasks:**
1. Add settings UI toggle: "Save AI notes to..." (Native KB | Obsidian Vault)
2. Add vault folder picker (if Obsidian selected)
3. Validate vault path and permissions
4. Show clear indicator of where notes will be saved

**UI Mock:**
```
┌─────────────────────────────────────────────┐
│ AI Note Destination                         │
│ ○ Native Knowledge Base (~/.polly/notes/)  │
│ ● Obsidian Vault                            │
│   └─ Path: /Users/.../Documents/Organizer  │
│   └─ Folder: 03-Scrolls/                   │
│                                     [Change]│
└─────────────────────────────────────────────┘
```

#### Phase 2: Vault-Aware Writing

**Goal:** Respect Obsidian vault structure and conventions

**Tasks:**
1. **Folder mapping**
   - Map Polly domains to Obsidian folders
   - Example: `scrolls` → `03-Scrolls/`, `sigils` → `01-Sigils/`
   - Allow custom mappings in settings

2. **Frontmatter support**
   - Detect if vault uses YAML frontmatter
   - Include common fields: `tags`, `aliases`, `date`, `created`
   - Respect existing frontmatter conventions

3. **Template compatibility**
   - Use vault templates if available (`/.polly/templates/` or `/_templates/`)
   - Fall back to Polly templates
   - Allow template override per vault

4. **Filename conventions**
   - Support vault naming conventions (spaces, hyphens, dates)
   - Check for existing notes with similar names
   - Suggest unique names if conflicts exist

#### Phase 3: Intelligent Vault Integration

**Goal:** Make AI-generated notes indistinguishable from manually created vault notes

**Tasks:**
1. **Link resolution**
   - Scan vault for existing notes
   - Use actual note titles for [[wiki-links]]
   - Suggest creating new notes for unlinked concepts

2. **Tag suggestions**
   - Learn from existing vault tags
   - Suggest relevant tags based on note content
   - Respect vault tag hierarchy (#project/active, #meeting/standup)

3. **Daily note integration**
   - Detect if vault uses daily notes
   - Offer to append to today's daily note
   - Follow daily note template structure

4. **Dataview compatibility**
   - Support inline fields (key:: value)
   - Generate proper task syntax `- [ ] Task`
   - Create dataview-compatible frontmatter

#### Phase 4: Two-Way Sync (Advanced)

**Goal:** Keep native KB and Obsidian vault in sync

**Tasks:**
1. **Selective sync**
   - User chooses which folders to sync
   - Bidirectional file watcher
   - Conflict resolution UI

2. **Metadata preservation**
   - Preserve vault metadata (creation date, modification date)
   - Sync tags bidirectionally
   - Handle renames and moves

3. **RAG integration**
   - Index both sources
   - De-duplicate in RAG (same note shouldn't appear twice)
   - Maintain source provenance

---

## Implementation Priority

### Must Have (Phase 1-2)
- Settings toggle for destination
- Vault path validation
- Basic folder mapping
- Frontmatter support

### Nice to Have (Phase 3)
- Link resolution from vault
- Tag learning
- Daily note integration

### Future (Phase 4)
- Two-way sync
- Advanced conflict resolution
- Unified view of both sources

---

## Technical Considerations

### 1. Obsidian Plugin API
- Obsidian has no official HTTP API
- File-based writes are safe and compatible
- Consider developing an Obsidian plugin for tighter integration

### 2. iCloud Sync
- Many users have vaults in iCloud
- Need to handle sync delays
- Test with Obsidian Sync, iCloud, Dropbox

### 3. Vault Size
- Large vaults (1000+ notes) need efficient scanning
- Cache vault structure for performance
- Incremental indexing for large vaults

### 4. Multiple Vaults
- Users may have multiple Obsidian vaults
- Support vault switching
- Remember last-used vault per session

---

## User Stories

### Story 1: Casual Obsidian User
> "I use Obsidian for my personal notes, but I want Polly's AI to help me create them. I want AI notes to appear in my vault just like my manual notes."

**Solution:** Phase 1-2 covers this - simple toggle + folder mapping

### Story 2: Power Obsidian User
> "My vault has a complex structure with templates, daily notes, and Dataview queries. I need AI notes to follow my existing conventions."

**Solution:** Phase 3 provides vault-aware intelligence

### Story 3: Hybrid User
> "I want to use both native KB for quick captures and Obsidian for long-term storage. Can I sync between them?"

**Solution:** Phase 4 provides two-way sync

---

## Migration Path

For users who want to move existing native notes to Obsidian:

```bash
# One-time migration script
polly migrate --from native --to obsidian \
  --vault-path ~/Documents/Organizer \
  --folder 03-Scrolls \
  --preserve-metadata
```

**Features:**
- Copy notes with proper frontmatter
- Preserve creation dates
- Convert tags to vault format
- Update internal links
- Generate migration report

---

## Decision: Why Native First?

We chose to default to native KB because:

1. **Simpler mental model** - One source of truth
2. **Faster to implement** - No vault structure complexity
3. **Better for testing** - Controlled environment
4. **Easier debugging** - Direct control over storage
5. **No permission issues** - No vault lock conflicts

Once the native flow is solid, we can confidently add Obsidian as an **option** rather than a **requirement**.

---

## Current Limitations (To Be Addressed)

❌ Cannot write to Obsidian vault (by design)  
❌ Templates must exist in both native and Obsidian (if switching sources)  
❌ No vault structure detection  
❌ No Obsidian-specific link resolution  

These will be addressed in future phases as outlined above.

---

## Conclusion

**Current state:** Polly uses native KB exclusively, which is stable and predictable.

**Future state:** Polly will offer elegant Obsidian integration as an **optional enhancement** for users who prefer vault-based workflows.

**Timeline:** Phases 1-2 could be implemented in ~1-2 weeks. Phases 3-4 are longer-term enhancements based on user demand.

---

*Last Updated: February 1, 2026*
